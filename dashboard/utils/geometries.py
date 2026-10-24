"""
Commune Geometry Loading
============================================================================
Load and prepare Chilean commune geometries for the territorial explorer.

The geojson is downloaded from caracena/chile-geojson (17 regional files),
cached locally under assets/, repaired (invalid geometries are fixed with
make_valid), and merged with dim_commune by (region_code, normalized commune
name), with a fuzzy fallback for leftovers.

This module does NOT load votes. The caller must join votes by commune_id
when needed.

Features
--------
- Automatic download and local caching of commune geometries.
- Robust repair of invalid geometries.
- Name normalization to bridge geojson and INE naming.
- Fuzzy matching for names that do not match exactly.
- Final GeoDataFrame with geometry + territorial dimensions.

Dependencies
------------
- Internal: utils.data_loader (load_dim_commune).
- External: difflib, os, re, unicodedata, geopandas, pandas, streamlit,
  shapely.
- Downstream: views/first_round/territorial_explorer.py,
  views/second_round/territorial.py.

Requirements
------------
- Internet access on first run (to download the geojson).
- Write access to assets/.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import difflib
import os
import re
import unicodedata

import geopandas as gpd
import pandas as pd
import streamlit as st
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

from utils.data_loader import load_dim_commune


# ============================================================================
# CONSTANTS
# ============================================================================
# Island communes excluded from the map (they distort the continental frame).
# "Antártica" is continental (Magallanes) and is NOT excluded.
EXCLUDE_COMMUNES = ["ISLA DE PASCUA", "JUAN FERNANDEZ", "JUAN FERNÁNDEZ"]

# Name variants between caracena/chile-geojson and the official INE names
# used in the database. Anything not covered here falls back to fuzzy matching.
KNOWN_ALIASES = {
    "COIHAIQUE": "COYHAIQUE",
    "CABO DE HORNOS EX NAVARINO": "CABO DE HORNOS",
    "MARCHIGUE": "MARCHIHUE",
    "LLAY LLAY": "LLAILLAY",
    "LLAY-LLAY": "LLAILLAY",
    "ALTO BIO BIO": "ALTO BIOBIO",
    "ALTO BIO-BIO": "ALTO BIOBIO",
    "TIL-TIL": "TIL TIL",
}


# ============================================================================
# NAME NORMALIZATION
# ============================================================================
def normalize_commune_name(value) -> str:
    """
    Normalize a commune name to a comparable technical key.

    Applies: uppercase, accent stripping (NFKD), removal of parenthetical
    suffixes, hyphen/space collapsing, and a final lookup in KNOWN_ALIASES.

    Parameters
    ----------
    value : Any
        Commune name (any variant). NaN is treated as empty string.

    Returns
    -------
    str
        Normalized commune name (uppercase, no accents, single spaces).
    """
    if pd.isna(value):
        return ""

    value = str(value).strip().upper()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.replace("’", "'").replace("`", "'")
    value = re.sub(r"\(.*?\)", " ", value)   # remove parenthetical suffixes
    value = value.replace("-", " ")
    value = re.sub(r"[^A-Z0-9' ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return KNOWN_ALIASES.get(value, value)


# ============================================================================
# FUZZY MATCHING
# ============================================================================
def _fuzzy_match_leftovers(unmatched_geo, unmatched_dim, cutoff=0.82):
    """
    For communes that did not match by exact name after normalization, find
    the best match within the same region using text similarity.

    Parameters
    ----------
    unmatched_geo : pd.DataFrame
        Geojson communes without an exact match.
    unmatched_dim : pd.DataFrame
        dim_commune communes without an exact match.
    cutoff : float, optional
        Minimum similarity score to accept a match (default 0.82).

    Returns
    -------
    dict
        Mapping of (region_code, geo_name) -> dim_name.

    Notes
    -----
    Matches are restricted to the same region to avoid homonymous communes
    in other zones.
    """
    matches = {}
    for region_code, geo_group in unmatched_geo.groupby("region_code"):
        dim_group = unmatched_dim[unmatched_dim["region_code"] == region_code]
        if dim_group.empty:
            continue
        dim_names = dim_group["commune_name_norm"].tolist()
        for geo_name in geo_group["commune_name_norm"].unique():
            best = difflib.get_close_matches(geo_name, dim_names, n=1, cutoff=cutoff)
            if best:
                matches[(region_code, geo_name)] = best[0]
    return matches


# ============================================================================
# GEOMETRY REPAIR
# ============================================================================
def _clean_geometry(geom):
    """
    Repair an invalid geometry and keep only the polygonal part.

    make_valid() may return a GeometryCollection when the original geometry
    was heavily damaged. PyDeck cannot render mixed collections, so only the
    polygonal parts are extracted.

    Parameters
    ----------
    geom : shapely geometry or None
        Raw geometry (possibly invalid).

    Returns
    -------
    Polygon, MultiPolygon, or None
        Repaired geometry, or None if it could not be salvaged.
    """
    if geom is None or geom.is_empty:
        return None

    if not geom.is_valid:
        geom = make_valid(geom)

    if geom.geom_type == "GeometryCollection":
        polys = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        if not polys:
            return None
        geom = unary_union(polys)

    if geom.geom_type not in ("Polygon", "MultiPolygon"):
        return None

    if not geom.is_valid:
        geom = geom.buffer(0)

    if geom is None or geom.is_empty:
        return None

    return geom


# ============================================================================
# GEOJSON LOADING
# ============================================================================
@st.cache_data
# Cached: the geojson does not change during a session.
def load_commune_geometries() -> gpd.GeoDataFrame:
    """
    Load commune geometries from caracena/chile-geojson and repair invalid
    geometries. Caches the consolidated result in assets/comunas_caracena.geojson.

    Returns
    -------
    gpd.GeoDataFrame
        Commune geometries, already repaired.

    Notes
    -----
    If the local cache exists and has rows, it is used. Otherwise, the 17
    regional files are downloaded and saved locally.
    """
    local_path = "assets/comunas_caracena.geojson"

    gdf = None
    if os.path.exists(local_path):
        try:
            candidate = gpd.read_file(local_path)
            if len(candidate) > 0:
                gdf = candidate
        except Exception:
            gdf = None

    if gdf is None:
        os.makedirs("assets", exist_ok=True)
        gdfs = []
        for i in range(1, 17):
            url = f"https://raw.githubusercontent.com/caracena/chile-geojson/master/{i}.geojson"
            try:
                gdf_region = gpd.read_file(url)
                if "Comuna" in gdf_region.columns:
                    gdf_region["NOM_COM"] = gdf_region["Comuna"]
                if "cod_comuna" in gdf_region.columns:
                    gdf_region["COD_COM"] = gdf_region["cod_comuna"]
                if "codregion" in gdf_region.columns:
                    gdf_region["REGION_NUM"] = gdf_region["codregion"]
                else:
                    gdf_region["REGION_NUM"] = i
                gdfs.append(gdf_region)
            except Exception:
                pass

        if not gdfs:
            return gpd.GeoDataFrame()

        gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs="EPSG:4326")
        try:
            gdf.to_file(local_path, driver="GeoJSON")
        except Exception:
            pass

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    # Robust repair: applied to ALL communes uniformly.
    gdf["geometry"] = gdf["geometry"].apply(_clean_geometry)
    gdf = gdf[gdf["geometry"].notna()].copy()

    return gdf


# ============================================================================
# FINAL PREPARATION
# ============================================================================
@st.cache_data
# Cached: the merge result does not change during a session.
def prepare_commune_geometries() -> gpd.GeoDataFrame:
    """
    Return a GeoDataFrame with commune geometry + territorial dimensions
    (region, macrozone, province, circumscription, district).

    Merges geometry (from caracena) with dim_commune by
    (region_code, commune_name_norm), with fuzzy fallback within each region.

    Does not include votes. The caller must join by commune_id when needed.

    Returns
    -------
    gpd.GeoDataFrame
        Geometry + territorial dimensions, sorted by (region, commune).
    """
    communes = load_commune_geometries()
    if communes.empty:
        return gpd.GeoDataFrame()

    communes = communes[
        ~communes["NOM_COM"].str.upper().str.contains("|".join(EXCLUDE_COMMUNES), na=False)
    ].copy()

    dim = load_dim_commune().copy()

    communes["commune_name_norm"] = communes["NOM_COM"].map(normalize_commune_name)
    dim["commune_name_norm"] = dim["commune_name"].map(normalize_commune_name)
    dim["region_code"] = (
        dim["region_code"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    )

    if "REGION_NUM" in communes.columns:
        communes["region_code"] = (
            communes["REGION_NUM"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
        )
    elif "codregion" in communes.columns:
        communes["region_code"] = (
            communes["codregion"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
        )
    else:
        raise RuntimeError("The GeoJSON does not contain a regional code.")

    # Forced fix for Ñuble (region_code "16"): buffer(0) + simplify, in
    # addition to the general repair. make_valid()/unary_union() alone were
    # not producing a valid polygon for this region. Note: the root cause
    # was likely the accented "Ñuble" not matching "NUBLE" during the merge,
    # but this geometric fix is kept as a safety net.
    nuble_mask = communes["region_code"] == "16"
    if nuble_mask.any():
        communes.loc[nuble_mask, "geometry"] = communes.loc[nuble_mask, "geometry"].apply(
            lambda geom: geom.buffer(0).simplify(0.001) if geom is not None else geom
        )

    # ---- Fuzzy fallback for names that did not match exactly ----
    matched_keys = set(
        communes[["region_code", "commune_name_norm"]]
        .merge(dim[["region_code", "commune_name_norm"]], on=["region_code", "commune_name_norm"])
        .apply(tuple, axis=1)
    )
    unmatched_geo = communes[
        ~communes.apply(lambda r: (r["region_code"], r["commune_name_norm"]) in matched_keys, axis=1)
    ]
    if not unmatched_geo.empty:
        unmatched_dim = dim[
            ~dim.apply(lambda r: (r["region_code"], r["commune_name_norm"]) in matched_keys, axis=1)
        ]
        fuzzy = _fuzzy_match_leftovers(unmatched_geo, unmatched_dim)
        if fuzzy:
            def _apply_fuzzy(row):
                key = (row["region_code"], row["commune_name_norm"])
                return fuzzy.get(key, row["commune_name_norm"])
            communes["commune_name_norm"] = communes.apply(_apply_fuzzy, axis=1)

    dim_cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order",
        "circunscripcion_senatorial", "distrito_electoral", "province",
    ]
    dim_cols = [c for c in dim_cols if c in dim.columns]

    gdf = communes.merge(
        dim[dim_cols + ["commune_name_norm"]],
        on=["region_code", "commune_name_norm"],
        how="left",
        suffixes=("_geo", ""),
    )

    # If dim did not bring commune_name, fall back to NOM_COM from the geojson.
    if "commune_name" not in gdf.columns and "NOM_COM" in gdf.columns:
        gdf["commune_name"] = gdf["NOM_COM"]

    # Consistent order by region and commune.
    sort_cols = [c for c in ["region_order", "commune_name"] if c in gdf.columns]
    if sort_cols:
        gdf = gdf.sort_values(sort_cols).reset_index(drop=True)

    return gdf
