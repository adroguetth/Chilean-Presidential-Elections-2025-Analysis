"""
First Round — Zones view (mapa interactivo de comunas con Plotly, corregido - todas las comunas).
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import os
import re
import unicodedata
from shapely.validation import make_valid

from utils.data_loader import load_fact_first_round_2025, load_dim_commune
from utils.calculations import compute_first_round_results


# ============================================================================
# CONSTANTES
# ============================================================================

CANDIDATE_KEYS = [
    'artes', 'enriquez_ominami', 'jara', 'kaiser',
    'kast', 'matthei', 'mayne_nicholls', 'parisi'
]
CANDIDATE_DISPLAY = {
    'artes': 'Artés',
    'enriquez_ominami': 'Enríquez-Ominami',
    'jara': 'Jara',
    'kaiser': 'Kaiser',
    'kast': 'Kast',
    'matthei': 'Matthei',
    'mayne_nicholls': 'Mayne-Nicholls',
    'parisi': 'Parisi',
}
CANDIDATE_COLORS = {
    'Artés': '#CC2222',
    'Enríquez-Ominami': '#D43986',
    'Jara': '#E94B4C',
    'Kaiser': '#F28A3D',
    'Kast': '#243C60',
    'Matthei': '#2E73C1',
    'Mayne-Nicholls': '#8A9BA8',
    'Parisi': '#3366B4',
    'No data': '#D3D3D3',
}

# Palabras clave para excluir islas
EXCLUDE_ISLANDS = ['PASCUA', 'JUAN FERNÁNDEZ', 'ANTÁRTICA']


# ============================================================================
# CARGA Y REPARACIÓN DE GEOMETRÍAS
# ============================================================================

@st.cache_data
def load_commune_geometries():
    """Carga geometrías de comunas desde caracena y repara geometrías inválidas."""
    local_path = "assets/comunas_caracena.geojson"
    if os.path.exists(local_path):
        try:
            gdf = gpd.read_file(local_path)
            if len(gdf) > 0:
                if gdf.crs is None:
                    gdf = gdf.set_crs("EPSG:4326")
                # Reparar geometrías inválidas
                gdf['geometry'] = gdf['geometry'].apply(
                    lambda g: make_valid(g) if g is not None and not g.is_valid else g
                )
                return gdf
        except Exception:
            pass

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
            # Reparar geometrías
            gdf_region['geometry'] = gdf_region['geometry'].apply(
                lambda g: make_valid(g) if g is not None and not g.is_valid else g
            )
            gdfs.append(gdf_region)
        except Exception:
            pass

    if gdfs:
        gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs="EPSG:4326")
        try:
            gdf.to_file(local_path, driver="GeoJSON")
        except Exception:
            pass
        return gdf
    return gpd.GeoDataFrame()


# ============================================================================
# PREPARACIÓN DE DATOS
# ============================================================================

def normalize_commune_name(value):
    """Normaliza nombres solo para la llave técnica de unión mapa <-> BD."""
    if pd.isna(value):
        return ""

    value = str(value).strip().upper()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.replace("’", "'").replace("`", "'")
    value = value.replace("-", " ")
    value = re.sub(r"[()]", " ", value)
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    aliases = {
        "CABO DE HORNOS EX NAVARINO": "CABO DE HORNOS",
    }
    return aliases.get(value, value)


@st.cache_data
def prepare_commune_data(df_votes: pd.DataFrame):
    """
    Fuente de verdad:
      dim_commune -> región, region_order y comuna
      fact_first_round_2025 -> votos

    La geometría solo aporta la forma. La unión se hace por
    region_code + nombre de comuna normalizado.
    """
    communes = load_commune_geometries()
    if communes.empty:
        return gpd.GeoDataFrame()

    # 🟢 Excluir islas (Pascua, Juan Fernández, Antártica)
    communes = communes[
        ~communes['NOM_COM'].str.upper().str.contains('|'.join(EXCLUDE_ISLANDS), na=False)
    ].copy()

    dim = load_dim_commune().copy()
    votes = df_votes.copy()

    communes["commune_name_norm"] = communes["NOM_COM"].map(
        normalize_commune_name
    )

    dim["commune_name_norm"] = dim["commune_name"].map(
        normalize_commune_name
    )
    dim["region_code"] = (
        dim["region_code"].astype(str).str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    if "REGION_NUM" in communes.columns:
        communes["region_code"] = (
            communes["REGION_NUM"].astype(str).str.strip()
            .str.replace(r"\.0$", "", regex=True)
        )
    elif "codregion" in communes.columns:
        communes["region_code"] = (
            communes["codregion"].astype(str).str.strip()
            .str.replace(r"\.0$", "", regex=True)
        )
    else:
        raise RuntimeError("El GeoJSON no contiene código regional.")

    # La tabla de resultados del proyecto normalmente ya viene enriquecida
    # con dim_commune. Si trae commune_id, esa es la relación primaria.
    if "commune_id" in votes.columns:
        votes = votes.drop(
            columns=["commune_name_norm", "region_code"],
            errors="ignore"
        )
        votes = votes.merge(
            dim[[
                "commune_id", "region_code", "region_name",
                "region_order", "commune_name", "commune_name_norm"
            ]],
            on="commune_id",
            how="left",
            suffixes=("", "_dim")
        )
    else:
        # Compatibilidad con el loader existente.
        votes = votes.merge(
            dim[[
                "commune_id", "region_code", "region_name",
                "region_order", "commune_name_norm"
            ]],
            left_on="commune_name",
            right_on="commune_name_norm",
            how="left"
        )

    # Nunca usamos solo el nombre: región + comuna evita colisiones.
    gdf = communes.merge(
        votes,
        on=["region_code", "commune_name_norm"],
        how="left",
        suffixes=("_geo", "")
    )

    vote_cols = [
        f"{c}_votes" for c in CANDIDATE_KEYS
        if f"{c}_votes" in gdf.columns
    ]
    if not vote_cols:
        raise RuntimeError(
            "No se encontraron columnas de votos 2025 en los datos cargados."
        )

    gdf[vote_cols] = (
        gdf[vote_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    )

    gdf["total_valid"] = gdf[vote_cols].sum(axis=1)
    gdf["winner_key"] = (
        gdf[vote_cols].idxmax(axis=1)
        .str.replace("_votes", "", regex=False)
    )
    gdf.loc[gdf["total_valid"] <= 0, "winner_key"] = None
    gdf["winner_display"] = gdf["winner_key"].map(CANDIDATE_DISPLAY)

    pct_cols = {
        c: f"{c}_pct" for c in CANDIDATE_KEYS
        if f"{c}_pct" in gdf.columns
    }

    def pct(row):
        key = row["winner_key"]
        if not key:
            return 0.0
        col = pct_cols.get(key)
        if col and pd.notna(row[col]):
            return float(row[col])
        total = row["total_valid"]
        return float(row[f"{key}_votes"]) / total * 100 if total else 0.0

    gdf["winner_pct"] = gdf.apply(pct, axis=1)
    gdf["color"] = (
        gdf["winner_display"].map(CANDIDATE_COLORS)
        .fillna(CANDIDATE_COLORS["No data"])
    )

    # Orden oficial de la BD, no alfabético.
    gdf = gdf.sort_values(
        ["region_order", "commune_name"]
    ).reset_index(drop=True)

    return gdf


# ============================================================================
# RENDERIZADO DEL MAPA
# ============================================================================

def render_interactive_map(gdf: gpd.GeoDataFrame, selected_region: str = None):
    """Muestra el mapa de Chile completo o de una región específica."""
    if gdf.empty:
        return None

    if selected_region and selected_region != "Todos":
        g = gdf[gdf["region_name"] == selected_region].copy()
        title = selected_region
    else:
        g = gdf.copy()
        title = "Chile"

    g = g[g["geometry"].notna() & ~g["geometry"].is_empty].copy()

    if g.empty:
        return None

    # Reparar geometrías una vez más
    g["geometry"] = g["geometry"].apply(
        lambda geom: make_valid(geom) if geom is not None and not geom.is_valid else geom
    )
    g = g[g["geometry"].notna() & ~g["geometry"].is_empty].copy()
    g = g.reset_index(drop=True)
    g["map_id"] = g["commune_id"].astype(str)

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": str(row["map_id"]),
                "properties": {},
                "geometry": row.geometry.__geo_interface__,
            }
            for _, row in g.iterrows()
        ],
    }

    fig = px.choropleth(
        g,
        geojson=geojson,
        locations="map_id",
        featureidkey="id",
        color="winner_display",
        hover_name="NOM_COM",
        hover_data={"winner_pct": ":.1f", "total_valid": ":,"},
        color_discrete_map=CANDIDATE_COLORS,
        category_orders={
            "winner_display": [
                "Jara", "Kast", "Parisi", "Kaiser", "Matthei",
                "Mayne-Nicholls", "Enríquez-Ominami", "Artés", "No data"
            ]
        },
        title=title,
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
    )

    fig.update_traces(
        marker_line_color="white",
        marker_line_width=0.8,
    )

    fig.update_layout(
        height=450,
        margin={"r": 0, "t": 35, "l": 0, "b": 0},
        legend_title_text="Ganador",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font_size=9,
        ),
    )

    return fig


# ============================================================================
# TABLA SIMPLIFICADA
# ============================================================================

def render_simplified_table(df: pd.DataFrame, t: dict):
    """
    Renderiza una tabla simplificada usando st.components.v1.html.
    """
    if df is None or df.empty:
        st.warning(f"⚠️ {t.get('no_data', 'No data available')}")
        return

    display_df = df[['candidate_name', 'votes', 'pct', 'color']].copy()
    display_df['votes'] = display_df['votes'].apply(lambda x: f"{x:,}")
    display_df['pct'] = display_df['pct'].apply(lambda x: f"{x:.2f}%")

    rows_html = ""
    for _, row in display_df.iterrows():
        rows_html += f"""
        <tr>
            <td>
                <span style="display:inline-block;width:10px;height:10px;border-radius:3px;background:{row['color']};margin-right:8px;vertical-align:middle;"></span>
                {row['candidate_name']}
            </td>
            <td style="text-align:right;font-weight:500;">{row['votes']}</td>
            <td style="text-align:right;font-weight:600;">{row['pct']}</td>
        </tr>
        """

    html = f"""
    <style>
        .simplified-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 14px;
        }}
        .simplified-table th {{
            text-align: left;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: .05em;
            color: #888780;
            padding: 8px 8px;
            border-bottom: 2px solid #E0DED8;
            font-weight: 600;
        }}
        .simplified-table td {{
            padding: 8px 8px;
            border-bottom: 1px solid #f0f0f0;
            vertical-align: middle;
        }}
        .simplified-table tr:last-child td {{
            border-bottom: none;
        }}
        .simplified-table tr:hover td {{
            background: #F7F6F3;
        }}
    </style>
    <table class="simplified-table">
        <thead>
            <tr>
                <th>{t.get('candidate', 'Candidato')}</th>
                <th style="text-align:right;">{t.get('votes', 'Votos')}</th>
                <th style="text-align:right;">{t.get('pct', '%')}</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """

    st.components.v1.html(html, height=350, scrolling=False)


# ============================================================================
# VISTA PRINCIPAL
# ============================================================================

def render(t: dict):
    st.markdown(
        f"<h2 style='font-size:22px;font-weight:600;color:#1a1a18;margin-top:0;margin-bottom:0.3rem;'>{t.get('zones', 'Zonas')}</h2>",
        unsafe_allow_html=True,
    )

    try:
        with st.spinner("Cargando datos..."):
            df_fr_2025_raw = load_fact_first_round_2025()
            gdf_communes = prepare_commune_data(df_fr_2025_raw)

        if gdf_communes.empty:
            st.error("No se pudieron cargar los datos geográficos.")
            return

        # ====================================================================
        # SELECTOR DE REGIÓN (con "Todos" al inicio)
        # ====================================================================
        region_list = (
            gdf_communes[["region_name", "region_order"]]
            .drop_duplicates()
            .sort_values("region_order")["region_name"]
            .dropna()
            .tolist()
        )
        region_list.insert(0, "Todos")  # 🟢 Opción nacional

        selected_region = st.selectbox(
            "Selecciona una región",
            options=region_list,
            index=0,  # 🟢 Por defecto "Todos"
            key="zones_region_selector",
        )

        # ====================================================================
        # LAYOUT: MAPA + TABLA
        # ====================================================================
        col_left, col_right = st.columns([1, 1])

        with col_left:
            if selected_region == "Todos":
                df_filtered = df_fr_2025_raw.copy()
            else:
                df_filtered = df_fr_2025_raw[
                    df_fr_2025_raw["region_name"] == selected_region
                ].copy()

            if df_filtered.empty:
                st.warning(f"No se encontraron resultados para {selected_region}.")
                return

            fr_results = compute_first_round_results(df_filtered)
            render_simplified_table(fr_results, t)

        with col_right:
            fig = render_interactive_map(
                gdf_communes,
                selected_region=selected_region if selected_region != "Todos" else None,
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        # ====================================================================
        # FOOTER
        # ====================================================================
        st.divider()
        st.markdown(
            f"<div style='text-align:center;font-size:12px;color:#888780;padding:0.3rem 0;'>{t['data_source']} · {t['data_source_note']}</div>",
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
