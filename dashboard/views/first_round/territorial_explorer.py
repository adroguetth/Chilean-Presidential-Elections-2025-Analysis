"""
First Round — Territorial Explorer
============================================================================
Territorial navigator for the 2025 first round. Six levels (Macrozona →
Región → Circunscripción → Distrito → Provincia → Comuna) with a movable
anchor, PyDeck + OpenStreetMap map, results table, donut chart, null/blank
vote analysis, and cascading breakdown tables.

This file is a refactored version of views/first_round/communal.py, with no
dependency on zones.py. Candidate colors and helpers come from
config.constants. Titles come from components.titles.

Features
--------
- Six-level territorial navigation with movable anchor.
- PyDeck + OpenStreetMap map with per-zone winner coloring.
- Results table + donut chart (top >10%, rest grouped as "Otros").
- Null/blank vote analysis with a 100-square waffle chart.
- Cascading breakdown tables (parent → child).

Dependencies
------------
- Internal: utils.data_loader (load_fact_first_round_2025,
  load_dim_commune), utils.geometries (prepare_commune_geometries),
  utils.html_helpers (fmt_number), utils.calculations
  (compute_first_round_results), config.constants (CANDIDATE_COLORS,
  COLOR_VALIDOS, COLOR_NULOS, COLOR_BLANCOS, NEUTRAL_COLOR,
  _get_candidate_color, _hex_to_rgba), components.titles.
- External: streamlit, pandas, unicodedata, shapely, pydeck, plotly.

Requirements
------------
- None.

Notes
-----
This file contains the most critical state machine in the dashboard: the
territorial navigation (LEVELS, COLS, KEYS, _on_change, _infer_ancestors,
_effective_state, _sibling_universe, _prepare, _reset, _clean, _fold,
_num_key, _unique, _filter).

Per an explicit project decision, the identifiers of that core are kept in
Spanish. Translating them (e.g. renaming "Todas" to "All", or COLS to
COLUMNS) is considered a time bomb: any change in those identifiers has a
high risk of introducing subtle navigation bugs (double-click issues, lost
context, sibling universe mismatches). The rest of the file (rendering
functions, table helpers, docstrings, comments) is translated to English.

See the README or CONTRIBUTING.md for the full rationale.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st
import pandas as pd
import unicodedata

from shapely import union_all

from utils.data_loader import load_fact_first_round_2025, load_dim_commune
from utils.geometries import prepare_commune_geometries
from utils.html_helpers import (
    fmt_number as _fmt_number,
)
from config.constants import (
    CANDIDATE_COLORS,
    COLOR_VALIDOS,
    COLOR_NULOS,
    COLOR_BLANCOS,
    NEUTRAL_COLOR,
    _get_candidate_color,
    _hex_to_rgba,
)
from components.titles import (
    render_view_title,
    render_section_title,
)


# ============================================================================
# HELPERS — HTML CLEANING
# ============================================================================
def _clean_html(html: str) -> str:
    """Strip leading/trailing whitespace from each line so Markdown does not
    interpret the HTML as a code block."""
    return "\n".join(line.strip() for line in html.strip().split("\n"))


# ============================================================================
# RESULTS TABLE
# ============================================================================
def _render_resultados_table(fr_df, t):
    if fr_df is None or fr_df.empty:
        st.info(t["fr_te_no_results"])
        return

    rows_html = ""
    for _, r in fr_df.iterrows():
        cand = str(r.get('candidate_name', t["fr_te_na"])).strip()
        votos = int(r.get('votes', 0))
        pct = float(r.get('pct', 0))
        color = _get_candidate_color(cand)
        rows_html += (
            f"<tr>"
            f"<td><span class=\"te-color-box\" style=\"background-color:{color};\"></span>{cand}</td>"
            f"<td>{votos:,}</td>"
            f"<td>{pct:.2f}%</td>"
            f"</tr>"
        )

    html = f"""
    <style>
        .te-tabla-contenedor {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            max-width: 700px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-family: "Liberation Sans", Arial, sans-serif;
        }}
        .te-tabla-contenedor table {{
            width: 100%;
            border-collapse: collapse;
            border-spacing: 0;
            font-family: "Liberation Sans", Arial, sans-serif;
            margin: 0;
        }}
        .te-tabla-contenedor thead,
        .te-tabla-contenedor thead tr {{
            background: transparent;
            margin: 0;
            padding: 0;
        }}
        .te-tabla-contenedor th,
        .te-tabla-contenedor td {{
            border-left: none !important;
            border-right: none !important;
            border-top: none;
            margin: 0;
        }}
        .te-tabla-contenedor th {{
            background-color: #f9f9f9 !important;
            text-align: left !important;
            padding: 6px 12px !important;
            font-size: 7.5pt !important;
            color: #666 !important;
            border-bottom: 1px solid #e0e0e0 !important;
            font-weight: 400 !important;
            letter-spacing: 0.04em !important;
            line-height: 1.1 !important;
            font-family: "Liberation Sans", Arial, sans-serif !important;
            font-style: normal !important;
            vertical-align: middle !important;
            text-transform: uppercase !important;
        }}
        .te-tabla-contenedor td {{
            padding: 8px 12px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 10.5pt;
            color: #333;
            font-weight: 400;
            line-height: 1.3;
            font-family: "Liberation Sans", Arial, sans-serif;
            font-style: normal;
            vertical-align: middle;
        }}
        .te-tabla-contenedor tr:last-child td {{
            border-bottom: none;
        }}
        .te-color-box {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
            vertical-align: middle;
            position: relative;
            top: -1px;
            font-style: normal;
        }}
    </style>
    <div class="te-tabla-contenedor" style="margin-top:2px;">
        <table>
            <thead>
                <tr>
                    <th>{t['candidate']}</th>
                    <th>{t['fr_pano_th_votos']}</th>
                    <th>{t['pct']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


def _render_donut_chart(fr_df, t):
    """Donut chart: only candidates with pct > 10% are shown individually;
    the rest are grouped as "Otros" in dark gray."""
    if fr_df is None or fr_df.empty:
        return
    try:
        import plotly.graph_objects as go
        df = fr_df.copy()
        if "pct" not in df.columns:
            return
        df = df.sort_values("pct", ascending=False)

        def short_name(name):
            if str(name).strip().lower() == "otros":
                return t["fr_te_donut_otros"]
            n = str(name).strip()
            parts = n.split()
            if len(parts) == 1:
                return parts[0]
            # Map common first names to the short surname used in the donut.
            mapping = {
                "Jeannette": "Jara",
                "José": "Kast",
                "Jose": "Kast",
                "Franco": "Parisi",
                "Johannes": "Kaiser",
                "Evelyn": "Matthei",
                "Harold": "Mayne-Nicholls",
                "Marco": "Enríquez-Ominami",
                "Eduardo": "Artés"
            }
            first = parts[0]
            if first in mapping:
                return mapping[first]
            return parts[-1] if len(parts[-1]) > 2 else parts[0]

        df_big = df[df["pct"] > 10].copy()
        df_small = df[df["pct"] <= 10].copy()

        chart_rows = []
        for _, r in df_big.iterrows():
            chart_rows.append({
                "candidate_name": r.get("candidate_name", t["fr_te_na"]),
                "pct": float(r.get("pct", 0)),
                "votes": int(r.get("votes", 0)) if "votes" in r else 0
            })

        if not df_small.empty:
            otros_pct = float(df_small["pct"].sum())
            otros_votes = int(df_small["votes"].sum()) if "votes" in df_small.columns else 0
            if otros_pct > 0:
                chart_rows.append({
                    "candidate_name": t["fr_te_donut_otros"],
                    "pct": otros_pct,
                    "votes": otros_votes
                })

        if not chart_rows:
            return

        import pandas as pd
        chart_df = pd.DataFrame(chart_rows)

        labels = [short_name(c) for c in chart_df["candidate_name"].astype(str)]
        values = chart_df["pct"].astype(float).tolist()
        cand_names = chart_df["candidate_name"].astype(str).tolist()
        colors = []
        for c in cand_names:
            if str(c).lower() == "otros" or str(c) == t["fr_te_donut_otros"]:
                colors.append(NEUTRAL_COLOR)
            else:
                colors.append(_get_candidate_color(c))

        text_labels = [f"{lab}<br>{pct:.1f}%" for lab, pct in zip(labels, values)]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            text=text_labels,
            textinfo='text',
            textposition='inside',
            textfont=dict(size=11, family="Liberation Sans, Arial", color='white'),
            insidetextorientation='horizontal',
            sort=False,
            direction='clockwise',
            hoverinfo='label+percent',
            hovertemplate='%{label}: %{value:.1f}%<extra></extra>'
        )])
        fig.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=280,
            width=280,
        )
        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})
    except Exception as e:
        try:
            st.caption(t["fr_te_donut_unavailable"].format(err=e))
        except Exception:
            pass


# ============================================================================
# MAP
# ============================================================================
def _build_map_gdf_progresivo(gdf_all, df_raw, alvl, aval, t):
    if alvl == "Nacional":
        group_col = "macrozone"
        base = gdf_all.copy()
        map_label = t["fr_te_mapa_macrozone"]
    elif alvl == "Macrozona":
        group_col = "region_name"
        base = gdf_all[gdf_all["macrozone"] == aval].copy() if aval else gdf_all.copy()
        map_label = t["fr_te_mapa_region_de"].format(zona=aval)
    elif alvl == "Región":
        group_col = "province"
        base = gdf_all[gdf_all["region_name"] == aval].copy() if aval else gdf_all.copy()
        map_label = t["fr_te_mapa_provincia_de"].format(zona=aval)
    elif alvl == "Provincia":
        group_col = "commune_name"
        base = gdf_all[gdf_all["province"] == aval].copy() if aval else gdf_all.copy()
        map_label = t["fr_te_mapa_comuna_de"].format(zona=aval)
    elif alvl == "Circunscripción":
        group_col = "commune_name"
        base = gdf_all[gdf_all["circunscripcion_senatorial"].astype(str) == str(aval)].copy() if aval else gdf_all.copy()
        map_label = t["fr_te_mapa_comuna_circ"].format(zona=aval)
    elif alvl == "Distrito":
        group_col = "commune_name"
        base = gdf_all[gdf_all["distrito_electoral"].astype(str) == str(aval)].copy() if aval else gdf_all.copy()
        map_label = t["fr_te_mapa_comuna_dist"].format(zona=aval)
    elif alvl == "Comuna":
        group_col = "commune_name"
        base = gdf_all[gdf_all["commune_name"] == aval].copy() if aval else gdf_all.copy()
        map_label = t["fr_te_mapa_comuna_single"].format(zona=aval)
    else:
        group_col = "commune_name"
        base = gdf_all.copy()
        map_label = t["fr_te_mapa_comunas"]

    if base.empty:
        return base, map_label, group_col
    if group_col not in base.columns:
        group_col = "commune_name"

    ids = base["commune_id"].dropna().unique().tolist()
    if not ids:
        return base, map_label, group_col

    try:
        from utils.calculations import compute_first_round_results
    except Exception:
        compute_first_round_results = None

    winners = []
    unique_groups = base[group_col].dropna().unique().tolist()

    for gval in unique_groups:
        sub_base = base[base[group_col] == gval]
        sub_ids = sub_base["commune_id"].dropna().unique().tolist()
        if not sub_ids:
            continue
        df_f_group = df_raw[df_raw["commune_id"].isin(sub_ids)].copy()
        if df_f_group.empty:
            continue

        try:
            region_name = sub_base["region_name"].iloc[0] if "region_name" in sub_base.columns else ""
            province_name = sub_base["province"].iloc[0] if "province" in sub_base.columns else ""
        except Exception:
            region_name = ""
            province_name = ""

        winner_display = t["fr_te_na"]
        winner_pct = 0.0
        winner_votes = 0
        total_valid = 0
        null_votes = 0

        if compute_first_round_results is not None:
            try:
                fr_group = compute_first_round_results(df_f_group)
                if fr_group is not None and not fr_group.empty:
                    winner_row = fr_group.iloc[0]
                    cand_name = None
                    for col in ["candidate_name", "candidate", "candidate_display", "name"]:
                        if col in fr_group.columns:
                            cand_name = winner_row.get(col)
                            if pd.notna(cand_name):
                                break
                    if cand_name is None:
                        cand_name = str(winner_row.iloc[0]) if len(winner_row) > 0 else t["fr_te_na"]
                    winner_display = str(cand_name)
                    total_valid = int(fr_group["votes"].sum()) if "votes" in fr_group.columns else 0
                    winner_votes = int(winner_row.get("votes", 0)) if hasattr(winner_row, 'get') else 0
                    winner_pct = float(winner_row.get("pct", 0)) if hasattr(winner_row, 'get') else 0
                    if winner_pct == 0 and total_valid > 0:
                        winner_pct = float(winner_votes / total_valid * 100) if total_valid else 0
            except Exception:
                pass

        # Fallback: if compute_first_round_results did not yield a winner,
        # aggregate votes by candidate column directly.
        if winner_display == t["fr_te_na"] or total_valid == 0:
            cand_col = None
            for c in df_f_group.columns:
                if "cand" in c.lower() and "id" not in c.lower():
                    cand_col = c
                    break
            if cand_col is None:
                for c in ["candidate_name", "candidate", "candidate_id"]:
                    if c in df_f_group.columns:
                        cand_col = c
                        break
            votes_col = "votes" if "votes" in df_f_group.columns else None
            if cand_col and votes_col:
                try:
                    agg = df_f_group.groupby(cand_col, as_index=False)[votes_col].sum()
                    if not agg.empty:
                        wr = agg.loc[agg[votes_col].idxmax()]
                        winner_display = str(wr[cand_col])
                        winner_votes = int(wr[votes_col])
                        total_valid = int(agg[votes_col].sum())
                        winner_pct = float(winner_votes / total_valid * 100) if total_valid else 0
                except Exception:
                    pass

        # Null/blank votes: try explicit null/blank columns first, then
        # fall back to candidate rows whose name contains "nulo" / "blanco".
        null_votes = 0
        blank_votes = 0
        try:
            null_cols = [c for c in df_raw.columns if isinstance(c, str) and any(k in c.lower() for k in ["nulo", "null", "nul"]) and "blanco" not in c.lower() and "blank" not in c.lower()]
            blank_cols = [c for c in df_raw.columns if isinstance(c, str) and any(k in c.lower() for k in ["blanco", "blank"])]

            if null_cols or blank_cols:
                cols_to_check = null_cols + blank_cols
                df_base = df_raw[df_raw["commune_id"].isin(sub_ids)][["commune_id"] + cols_to_check].drop_duplicates(subset=["commune_id"])
                for nc in null_cols:
                    try:
                        null_votes += int(pd.to_numeric(df_base[nc], errors='coerce').fillna(0).sum())
                    except:
                        pass
                for bc in blank_cols:
                    try:
                        blank_votes += int(pd.to_numeric(df_base[bc], errors='coerce').fillna(0).sum())
                    except:
                        pass

            if null_votes == 0 and blank_votes == 0:
                for c in df_f_group.columns:
                    if "cand" in c.lower():
                        try:
                            mask_nulo = df_f_group[c].astype(str).str.lower().str.contains("nulo|null", na=False)
                            mask_blanco = df_f_group[c].astype(str).str.lower().str.contains("blanco|blank", na=False)
                            if mask_nulo.any() and "votes" in df_f_group.columns:
                                null_votes = int(df_f_group.loc[mask_nulo, "votes"].sum())
                            if mask_blanco.any() and "votes" in df_f_group.columns:
                                blank_votes = int(df_f_group.loc[mask_blanco, "votes"].sum())
                            if mask_nulo.any() or mask_blanco.any():
                                break
                        except:
                            pass
        except Exception:
            null_votes = 0
            blank_votes = 0

        null_fmt = f"{int(null_votes):,}" if null_votes != 0 else t["fr_te_na"]
        blank_fmt = f"{int(blank_votes):,}" if blank_votes != 0 else t["fr_te_na"]

        winners.append({
            group_col: gval,
            "winner_display": winner_display,
            "winner_pct": round(winner_pct, 2),
            "winner_pct_fmt": f"{winner_pct:.2f}%",
            "winner_votes": int(winner_votes),
            "winner_votes_fmt": f"{int(winner_votes):,}",
            "total_votes": int(total_valid + null_votes + blank_votes) if (null_votes or blank_votes) else int(total_valid),
            "valid_votes": int(total_valid),
            "valid_votes_fmt": f"{int(total_valid):,}",
            "null_votes": int(null_votes),
            "null_votes_fmt": null_fmt,
            "blank_votes": int(blank_votes),
            "blank_votes_fmt": blank_fmt,
            "region_name_tooltip": str(region_name),
            "province_tooltip": str(province_name),
            "winner_color": _get_candidate_color(winner_display),
        })

    winners_df = pd.DataFrame(winners)

    cols_to_drop = ["winner_display", "winner_pct", "total_votes", "__hex", "__fill", "__line", "winner", "ganador", "valid_votes", "null_votes", "blank_votes", "winner_votes", "winner_color", "region_name_tooltip", "province_tooltip", "winner_pct_fmt", "winner_votes_fmt", "valid_votes_fmt", "null_votes_fmt", "blank_votes_fmt"]
    base_clean = base.drop(columns=[c for c in cols_to_drop if c in base.columns], errors="ignore")

    if group_col == "commune_name":
        map_gdf = base_clean.merge(winners_df, on=group_col, how="left")
    else:
        try:
            dissolved = base_clean.dissolve(by=group_col, as_index=False)
        except Exception:
            try:
                dissolved = base_clean.groupby(group_col, as_index=False).agg({"geometry": lambda x: union_all(x.values) if hasattr(x, 'values') else x.iloc[0]})
            except Exception:
                dissolved = base_clean.drop_duplicates(subset=[group_col]).copy()
            keep_cols = [c for c in ["macrozone", "region_name", "province", "circunscripcion_senatorial", "distrito_electoral"] if c in base.columns]
            if keep_cols:
                try:
                    meta = base[[group_col] + keep_cols].drop_duplicates(subset=[group_col])
                    dissolved = dissolved.drop(columns=[c for c in keep_cols if c in dissolved.columns], errors="ignore").merge(meta, on=group_col, how="left")
                except Exception:
                    pass
        map_gdf = dissolved.merge(winners_df, on=group_col, how="left")
        map_gdf["commune_name"] = map_gdf[group_col].astype(str)
        if "province" not in map_gdf.columns:
            map_gdf["province"] = map_gdf[group_col].astype(str)
        if "region_name" not in map_gdf.columns and "region_name_tooltip" in map_gdf.columns:
            map_gdf["region_name"] = map_gdf["region_name_tooltip"]

    return map_gdf, map_label, group_col


def _render_mapa(map_gdf, group_col, alvl, aval, t):
    if map_gdf is None or map_gdf.empty:
        return
    try:
        import pydeck as pdk
        gdf = map_gdf.copy()
        try:
            if hasattr(gdf, 'crs') and gdf.crs and gdf.crs.to_string() != "EPSG:4326":
                gdf = gdf.to_crs(epsg=4326)
        except:
            pass

        if "winner_display" in gdf.columns:
            gdf["__hex"] = gdf["winner_display"].apply(_get_candidate_color)
        else:
            gdf["__hex"] = NEUTRAL_COLOR
        gdf["__fill"] = gdf["__hex"].apply(lambda h: _hex_to_rgba(h, 165))
        gdf["__line"] = gdf["__hex"].apply(lambda h: _hex_to_rgba(h, 255))

        gdf["nombre"] = gdf["commune_name"].astype(str) if "commune_name" in gdf.columns else gdf[group_col].astype(str) if group_col in gdf.columns else t["fr_te_na"]
        gdf["ganador"] = gdf["winner_display"].astype(str) if "winner_display" in gdf.columns else t["fr_te_na"]
        gdf["porcentaje"] = gdf["winner_pct_fmt"].astype(str) if "winner_pct_fmt" in gdf.columns else (gdf["winner_pct"].astype(str) + "%" if "winner_pct" in gdf.columns else "")
        gdf["validos"] = gdf["valid_votes_fmt"].astype(str) if "valid_votes_fmt" in gdf.columns else gdf["valid_votes"].astype(str) if "valid_votes" in gdf.columns else "0"
        gdf["nulos"] = gdf["null_votes_fmt"].astype(str) if "null_votes_fmt" in gdf.columns else gdf["null_votes"].astype(str) if "null_votes" in gdf.columns else t["fr_te_na"]
        gdf["blancos"] = gdf["blank_votes_fmt"].astype(str) if "blank_votes_fmt" in gdf.columns else gdf["blank_votes"].astype(str) if "blank_votes" in gdf.columns else t["fr_te_na"]
        gdf["region"] = gdf["region_name_tooltip"].astype(str) if "region_name_tooltip" in gdf.columns else gdf["region_name"].astype(str) if "region_name" in gdf.columns else ""
        gdf["colorGanador"] = gdf["winner_color"].astype(str) if "winner_color" in gdf.columns else gdf["winner_display"].apply(_get_candidate_color) if "winner_display" in gdf.columns else NEUTRAL_COLOR

        try:
            centroid = union_all(gdf.geometry.values).centroid
            lat, lon = float(centroid.y), float(centroid.x)
        except:
            lat, lon = -33.4, -70.6

        n = len(gdf)
        # Zoom level per territorial level. Tuned so the map shows the right
        # amount of detail without manual intervention.
        if alvl == "Comuna":
            zoom = 10
        elif alvl == "Provincia":
            zoom = 8.5
        elif alvl == "Distrito":
            zoom = 8
        elif alvl == "Circunscripción":
            zoom = 7.5
        elif alvl == "Región":
            zoom = 7
        elif alvl == "Macrozona":
            zoom = 5.5
        else:
            zoom = 4.2

        view = pdk.ViewState(latitude=lat, longitude=lon, zoom=zoom, pitch=0)
        osm_style = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"

        # Simplify geometries to speed up rendering. Tolerance depends on
        # the territorial level: more detail at the commune level, less at
        # the national level.
        try:
            if alvl == "Comuna":
                tol = 0.0005
            elif alvl in ("Provincia", "Distrito"):
                tol = 0.001
            elif alvl in ("Región", "Circunscripción"):
                tol = 0.003
            else:
                tol = 0.008
            gdf_simpl = gdf.copy()
            gdf_simpl["geometry"] = gdf_simpl.geometry.simplify(tol, preserve_topology=True)
        except:
            gdf_simpl = gdf.copy()

        layer_zona = pdk.Layer(
            "GeoJsonLayer",
            data=gdf_simpl,
            get_fill_color="__fill",
            get_line_color="__line",
            line_width_min_pixels=1.5 if alvl != "Comuna" else 2.5,
            get_line_width=2,
            pickable=True,
            auto_highlight=True,
            highlight_color=[255,255,0,120],
            opacity=0.78,
            stroked=True,
            filled=True,
        )

        # Tooltip HTML varies by group_col: macrozone/region/province do not
        # need the region line, but communes do.
        if group_col == "macrozone":
            html_tip = f"""
            <div style='font-family: Liberation Sans, Arial, sans-serif; line-height: 1.4; min-width: 180px;'>
                <div style='font-weight: 700; font-size: 13px; margin-bottom: 4px; color: #111827;'>{{nombre}}</div>
                <div style='font-size: 11px;'>{t['fr_te_tooltip_ganador']}<span style='color: {{colorGanador}}; font-weight: 700;'>{{ganador}} ({{porcentaje}})</span></div>
                <div style='font-size: 11px; color: #374151;'>{t['fr_te_tooltip_validos']}{{validos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_nulos']}{{nulos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_blancos']}{{blancos}}</div>
            </div>
            """
        elif group_col == "region_name":
            html_tip = f"""
            <div style='font-family: Liberation Sans, Arial, sans-serif; line-height: 1.4; min-width: 180px;'>
                <div style='font-weight: 700; font-size: 13px; margin-bottom: 4px; color: #111827;'>{{nombre}}</div>
                <div style='font-size: 11px;'>{t['fr_te_tooltip_ganador']}<span style='color: {{colorGanador}}; font-weight: 700;'>{{ganador}} ({{porcentaje}})</span></div>
                <div style='font-size: 11px; color: #374151;'>{t['fr_te_tooltip_validos']}{{validos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_nulos']}{{nulos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_blancos']}{{blancos}}</div>
            </div>
            """
        elif group_col == "province":
            html_tip = f"""
            <div style='font-family: Liberation Sans, Arial, sans-serif; line-height: 1.4; min-width: 180px;'>
                <div style='font-weight: 700; font-size: 13px; margin-bottom: 4px; color: #111827;'>{{nombre}}</div>
                <div style='font-size: 11px; color: #6b7280; margin-bottom: 2px;'>{t['fr_te_tooltip_region']}{{region}}</div>
                <div style='font-size: 11px;'>{t['fr_te_tooltip_ganador']}<span style='color: {{colorGanador}}; font-weight: 700;'>{{ganador}} ({{porcentaje}})</span></div>
                <div style='font-size: 11px; color: #374151;'>{t['fr_te_tooltip_validos']}{{validos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_nulos']}{{nulos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_blancos']}{{blancos}}</div>
            </div>
            """
        else:
            html_tip = f"""
            <div style='font-family: Liberation Sans, Arial, sans-serif; line-height: 1.45; min-width: 190px;'>
                <div style='font-weight: 700; font-size: 13px; margin-bottom: 5px; color: #111827;'>{{nombre}}</div>
                <div style='font-size: 11px; color: #4b5563; margin-bottom: 2px;'>{t['fr_te_tooltip_region']}{{region}}</div>
                <div style='font-size: 11px; margin-bottom: 2px;'>{t['fr_te_tooltip_ganador']}<span style='color: {{colorGanador}}; font-weight: 700;'>{{ganador}} ({{porcentaje}})</span></div>
                <div style='font-size: 11px; color: #374151;'>{t['fr_te_tooltip_validos']}{{validos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_nulos']}{{nulos}}</div>
                <div style='font-size: 11px; color: #6b7280;'>{t['fr_te_tooltip_blancos']}{{blancos}}</div>
            </div>
            """

        tooltip = {
            "html": html_tip,
            "style": {"backgroundColor": "#ffffff", "color": "#111827", "font-family": "Liberation Sans, Arial, sans-serif", "font-size": "11px", "border-radius": "8px", "padding": "10px 12px", "border": "1px solid #e5e7eb", "boxShadow": "0 4px 12px rgba(0,0,0,0.12)"}
        }

        deck = pdk.Deck(layers=[layer_zona], initial_view_state=view, tooltip=tooltip, map_style=osm_style)
        st.pydeck_chart(deck, use_container_width=True)

        # Legend: only show if the map has 50 or fewer zones, to avoid
        # clutter on the national view.
        if n <= 50:
            st.markdown("""<style>.legend{display:flex;flex-wrap:wrap;gap:12px;margin-top:10px;font-family:"Liberation Sans",Arial,sans-serif;font-size:9pt;}.legend-item{display:flex;align-items:center;gap:5px;}.legend-dot{width:12px;height:12px;border-radius:3px;display:inline-block;border:1px solid rgba(0,0,0,0.1);}</style>""", unsafe_allow_html=True)
            presentes = gdf["ganador"].dropna().unique() if "ganador" in gdf.columns else []
            if len(presentes) > 0:
                legend_html = '<div class="legend">'
                for cand in presentes:
                    col = _get_candidate_color(cand)
                    legend_html += f'<div class="legend-item"><span class="legend-dot" style="background:{col}"></span>{cand}</div>'
                legend_html += '</div>'
                st.markdown(legend_html, unsafe_allow_html=True)
    except Exception as e:
        st.warning(t["fr_te_map_unavailable"].format(err=e))
        st.exception(e)


# ============================================================================
# CASCADING TABLES
# ============================================================================
def _build_child_summary(analysis_gdf, df_raw, child_col, compute_fn):
    """
    Build a per-child summary: winner, % and valid votes.
    """
    import pandas as pd
    if child_col not in analysis_gdf.columns:
        return pd.DataFrame()

    ordered_vals = []

    # Macrozone: order by macrozone_order.
    if child_col == "macrozone" and "macrozone_order" in analysis_gdf.columns:
        orden_prep = (
            analysis_gdf[["macrozone", "macrozone_order"]]
            .dropna()
            .drop_duplicates()
            .sort_values("macrozone_order")
        )
        ordered_vals = orden_prep["macrozone"].tolist()
        extras = sorted(
            [v for v in analysis_gdf[child_col].dropna().unique().tolist() if v not in ordered_vals],
            key=lambda x: str(x).lower(),
        )
        ordered_vals = ordered_vals + extras

    # Region: order by region_order.
    elif child_col == "region_name" and "region_order" in analysis_gdf.columns:
        orden_prep = (
            analysis_gdf[["region_name", "region_order"]]
            .dropna()
            .drop_duplicates()
            .sort_values("region_order")
        )
        ordered_vals = orden_prep["region_name"].tolist()
        extras = sorted(
            [v for v in analysis_gdf[child_col].dropna().unique().tolist() if v not in ordered_vals],
            key=lambda x: str(x).lower(),
        )
        ordered_vals = ordered_vals + extras

    else:
        ordered_vals = sorted(
            analysis_gdf[child_col].dropna().unique().tolist(),
            key=lambda x: str(x).lower(),
        )

    rows = []
    for child_val in ordered_vals:
        sub_ids = analysis_gdf[analysis_gdf[child_col] == child_val]["commune_id"].dropna().unique().tolist()
        if not sub_ids:
            continue
        df_sub = df_raw[df_raw["commune_id"].isin(sub_ids)]
        if df_sub.empty:
            continue
        try:
            fr_sub = compute_fn(df_sub)
            if fr_sub is None or fr_sub.empty:
                continue
            winner_idx = fr_sub["pct"].idxmax() if "pct" in fr_sub.columns else fr_sub["votes"].idxmax()
            winner_row = fr_sub.loc[winner_idx]
            rows.append({
                "Zona": str(child_val),
                "Ganador": str(winner_row.get("candidate_name", "N/A")),
                "% Ganador": f"{float(winner_row.get('pct',0)):.1f}%",
                "Votos válidos": int(fr_sub["votes"].sum()) if "votes" in fr_sub.columns else 0,
                "Comunas": len(sub_ids),
                "color": _get_candidate_color(str(winner_row.get("candidate_name","")))
            })
        except Exception as e:
            rows.append({"Zona": str(child_val), "Ganador": f"Error {e}", "% Ganador": "-", "Votos válidos": 0, "Comunas": len(sub_ids), "color": NEUTRAL_COLOR})
    return pd.DataFrame(rows)


def _render_child_table(title, child_df, t, include_comunas=True):
    """
    Render a breakdown table by zone.

    If include_comunas=False, the "Comunas" column is not shown (each row
    is already a commune, so the column would always be 1).
    """
    if child_df is None or child_df.empty:
        return
    if title:
        render_section_title(f"{title} ({len(child_df)})")

    import uuid
    import streamlit.components.v1 as components

    rows_html = ""
    for _, r in child_df.iterrows():
        zona = str(r.get("Zona","")).strip()
        ganador = str(r.get("Ganador","")).strip()
        pct_raw = str(r.get("% Ganador","")).strip()
        votos = int(r.get("Votos válidos",0) or 0)
        comunas = int(r.get("Comunas",0) or 0)
        color = str(r.get("color",NEUTRAL_COLOR)).strip()

        try:
            pct_val = float(pct_raw.replace("%","").replace(",",".").strip())
        except:
            pct_val = 0.0

        zona_esc = zona.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        ganador_esc = ganador.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

        # "Comunas" column only when include_comunas=True.
        comunas_td = f'<td data-value="{comunas}">{comunas}</td>' if include_comunas else ""

        rows_html += f"""
        <tr>
            <td data-value="{zona.lower()}">{zona_esc}</td>
            <td data-value="{ganador.lower()}"><span class="dot" style="background:{color}"></span>{ganador_esc}</td>
            <td data-value="{pct_val:.4f}">{pct_raw}</td>
            <td data-value="{votos}">{votos:,}</td>
            {comunas_td}
        </tr>
        """

    table_id = f"child-{uuid.uuid4().hex[:6]}"

    # "Comunas" header only when include_comunas=True.
    comunas_th = f'<th data-col="4" data-type="number" onclick="sortChildTable(\'{table_id}\',4,\'number\',this)">{t["fr_te_th_comunas"]} <span class="sort-arrow">↕</span></th>' if include_comunas else ""

    html_table = f"""
    <style>
        .child-tabla-contenedor-sort {{ border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; max-width: 750px; width: 100%; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }}
        .child-tabla-contenedor-sort table {{ width: 100%; border-collapse: collapse; }}
        .child-tabla-contenedor-sort th {{ background-color: #f9f9f9; text-align: left; padding: 8px 12px; font-size: 7.5pt; color: #666; text-transform: uppercase; border-bottom: 1px solid #e0e0e0; font-weight: 600; letter-spacing: 0.04em; line-height: 1.1; cursor: pointer; user-select: none; position: relative; }}
        .child-tabla-contenedor-sort th:hover {{ background-color: #f0f0f0; color: #111827; }}
        .child-tabla-contenedor-sort td {{ padding: 8px 12px; border-bottom: 1px solid #f0f0f0; font-size: 10.5pt; color: #333; font-weight: 400; line-height: 1.3; }}
        .child-tabla-contenedor-sort tr:last-child td {{ border-bottom: none; }}
        .child-tabla-contenedor-sort .sort-arrow {{ margin-left: 6px; font-size: 9pt; color: #9ca3af; }}
        .child-tabla-contenedor-sort th.active {{ color: #111827; }}
        .child-tabla-contenedor-sort th.active .sort-arrow {{ color: #111827; }}
        .child-tabla-contenedor-sort .dot {{ width:10px; height:10px; border-radius:3px; display:inline-block; margin-right:6px; vertical-align:middle; }}
        .child-tabla-contenedor-sort tr:hover td {{ background-color: #fafafa; }}
    </style>
    <div class="child-tabla-contenedor-sort">
        <table id="{table_id}">
            <thead>
                <tr>
                    <th data-col="0" data-type="text" onclick="sortChildTable('{table_id}',0,'text',this)">{t['fr_te_th_zona']} <span class="sort-arrow">↕</span></th>
                    <th data-col="1" data-type="text" onclick="sortChildTable('{table_id}',1,'text',this)">{t['fr_te_th_ganador']} <span class="sort-arrow">↕</span></th>
                    <th data-col="2" data-type="number" onclick="sortChildTable('{table_id}',2,'number',this)">{t['pct']} <span class="sort-arrow">↕</span></th>
                    <th data-col="3" data-type="number" onclick="sortChildTable('{table_id}',3,'number',this)">{t['valid_votes']} <span class="sort-arrow">↕</span></th>
                    {comunas_th}
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    <script>
    function sortChildTable(tableId, colIndex, type, headerEl) {{
        const table = document.getElementById(tableId);
        if(!table) return;
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.rows);
        const headers = table.tHead.rows[0].cells;

        let dir = headerEl.getAttribute('data-dir');
        dir = (!dir || dir === 'desc') ? 'asc' : 'desc';

        for(let i=0; i<headers.length; i++){{
            const th = headers[i];
            if(th !== headerEl){{
                th.removeAttribute('data-dir');
                const arr = th.querySelector('.sort-arrow');
                if(arr) arr.textContent = '↕';
                th.classList.remove('active');
            }}
        }}
        headerEl.setAttribute('data-dir', dir);
        headerEl.classList.add('active');
        const arrow = headerEl.querySelector('.sort-arrow');
        if(arrow) arrow.textContent = dir === 'asc' ? '↑' : '↓';

        rows.sort((a,b) => {{
            let aVal = a.cells[colIndex].getAttribute('data-value') || a.cells[colIndex].textContent.trim();
            let bVal = b.cells[colIndex].getAttribute('data-value') || b.cells[colIndex].textContent.trim();
            if(type === 'number'){{
                aVal = parseFloat(aVal) || 0;
                bVal = parseFloat(bVal) || 0;
                return dir === 'asc' ? aVal - bVal : bVal - aVal;
            }} else {{
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
                if(aVal < bVal) return dir === 'asc' ? -1 : 1;
                if(aVal > bVal) return dir === 'asc' ? 1 : -1;
                return 0;
            }}
        }});

        rows.forEach(row => tbody.appendChild(row));
    }}
    </script>
    """

    # Scroll only if the table exceeds 700px.
    real_height = 62 + len(child_df) * 36
    h = min(700, max(120, real_height))
    needs_scroll = real_height > 700
    components.html(html_table, height=h, scrolling=needs_scroll)


def _render_cascading_tables(alvl, aval, analysis_gdf, df_raw, compute_fn, t):
    """Cascading breakdown tables: parent → child."""
    import pandas as pd

    # At the commune level there is no further breakdown.
    if alvl == "Comuna":
        return

    st.divider()

    # Title "Desglose" with prefix for Circunscripción/Distrito.
    if aval is None:
        zona_txt = alvl
    elif alvl == "Circunscripción":
        zona_txt = f"Circunscripción {aval}"
    elif alvl == "Distrito":
        zona_txt = f"Distrito {aval}"
    else:
        zona_txt = aval

    render_view_title(t["fr_te_view_desglose"].format(zona=zona_txt))

    if alvl == "Nacional":
        render_section_title(t["fr_te_tabla_macrozonas"])
        child_macro = _build_child_summary(analysis_gdf, df_raw, "macrozone", compute_fn)
        _render_child_table("", child_macro, t, include_comunas=True)
        render_section_title(t["fr_te_tabla_regiones_2"])
        child_reg = _build_child_summary(analysis_gdf, df_raw, "region_name", compute_fn)
        _render_child_table("", child_reg, t, include_comunas=True)

    elif alvl == "Macrozona":
        render_section_title(t["fr_te_tabla_regiones_1"])
        child_reg = _build_child_summary(analysis_gdf, df_raw, "region_name", compute_fn)
        _render_child_table("", child_reg, t, include_comunas=True)

    elif alvl == "Región":
        render_section_title(t["fr_te_tabla_provincias"])
        child_prov = _build_child_summary(analysis_gdf, df_raw, "province", compute_fn)
        _render_child_table("", child_prov, t, include_comunas=True)
        render_section_title(t["fr_te_tabla_comunas_2"])
        child_com = _build_child_summary(analysis_gdf, df_raw, "commune_name", compute_fn)
        _render_child_table("", child_com, t, include_comunas=False)

    elif alvl == "Circunscripción":
        render_section_title(t["fr_te_tabla_provincias"])
        child_prov = _build_child_summary(analysis_gdf, df_raw, "province", compute_fn)
        _render_child_table("", child_prov, t, include_comunas=True)
        render_section_title(t["fr_te_tabla_comunas_2"])
        child_com = _build_child_summary(analysis_gdf, df_raw, "commune_name", compute_fn)
        _render_child_table("", child_com, t, include_comunas=False)

    elif alvl == "Distrito":
        render_section_title(t["fr_te_tabla_provincias"])
        child_prov = _build_child_summary(analysis_gdf, df_raw, "province", compute_fn)
        _render_child_table("", child_prov, t, include_comunas=True)
        render_section_title(t["fr_te_tabla_comunas_2"])
        child_com = _build_child_summary(analysis_gdf, df_raw, "commune_name", compute_fn)
        _render_child_table("", child_com, t, include_comunas=False)

    elif alvl == "Provincia":
        render_section_title(t["fr_te_tabla_comunas_1"])
        child_com = _build_child_summary(analysis_gdf, df_raw, "commune_name", compute_fn)
        _render_child_table("", child_com, t, include_comunas=False)


# ============================================================================
# NULL/BLANK VOTES
# ============================================================================
def _extract_null_blank_for_ids(sub_ids, df_raw, df_f):
    """Extract null and blank votes for a set of commune_id, kept separate."""
    import pandas as pd
    null_votes = 0
    blank_votes = 0
    try:
        null_cols = [c for c in df_raw.columns if isinstance(c, str) and any(k in c.lower() for k in ["nulo", "null"]) and "blanco" not in c.lower() and "blank" not in c.lower()]
        blank_cols = [c for c in df_raw.columns if isinstance(c, str) and any(k in c.lower() for k in ["blanco", "blank"])]
        if null_cols or blank_cols:
            cols_to_check = null_cols + blank_cols
            base_cols = ["commune_id"] + cols_to_check
            base_cols = [c for c in base_cols if c in df_raw.columns]
            df_base = df_raw[df_raw["commune_id"].isin(sub_ids)][base_cols].drop_duplicates(subset=["commune_id"])
            for nc in null_cols:
                if nc in df_base.columns:
                    try:
                        null_votes += int(pd.to_numeric(df_base[nc], errors='coerce').fillna(0).sum())
                    except:
                        pass
            for bc in blank_cols:
                if bc in df_base.columns:
                    try:
                        blank_votes += int(pd.to_numeric(df_base[bc], errors='coerce').fillna(0).sum())
                    except:
                        pass
        if null_votes == 0 and blank_votes == 0 and not df_f.empty:
            for c in df_f.columns:
                if "cand" in c.lower():
                    try:
                        mask_nulo = df_f[c].astype(str).str.lower().str.contains("nulo|null", na=False)
                        mask_blanco = df_f[c].astype(str).str.lower().str.contains("blanco|blank", na=False)
                        if mask_nulo.any() and "votes" in df_f.columns:
                            null_votes = int(df_f.loc[mask_nulo, "votes"].sum())
                        if mask_blanco.any() and "votes" in df_f.columns:
                            blank_votes = int(df_f.loc[mask_blanco, "votes"].sum())
                        if mask_nulo.any() or mask_blanco.any():
                            break
                    except:
                        pass
    except Exception:
        pass
    return int(null_votes), int(blank_votes)


def _render_null_blank_analysis(alvl, aval, analysis_gdf, df_raw, df_f, fr_df, compute_fn, t):
    """Dynamic null/blank votes analysis panel."""
    import pandas as pd
    import streamlit.components.v1 as components
    import uuid
    if analysis_gdf.empty or df_f.empty:
        return

    sub_ids = analysis_gdf["commune_id"].dropna().unique().tolist()
    if not sub_ids:
        return

    null_votes, blank_votes = _extract_null_blank_for_ids(sub_ids, df_raw, df_f)

    try:
        valid_votes = int(fr_df["votes"].sum()) if fr_df is not None and not fr_df.empty and "votes" in fr_df.columns else int(df_f["votes"].sum()) if "votes" in df_f.columns else 0
    except:
        valid_votes = 0

    total_emitidos = valid_votes + null_votes + blank_votes
    if total_emitidos == 0:
        return

    null_pct = (null_votes / total_emitidos * 100) if total_emitidos else 0
    blank_pct = (blank_votes / total_emitidos * 100) if total_emitidos else 0
    valid_pct = (valid_votes / total_emitidos * 100) if total_emitidos else 0
    combined_pct = null_pct + blank_pct

    if alvl == "Nacional":
        titulo_ranking = t["fr_te_rank_nacional"]
        child_col = "region_name"
    elif alvl == "Macrozona":
        titulo_ranking = t["fr_te_rank_macrozona"]
        child_col = "region_name"
    elif alvl == "Región":
        titulo_ranking = t["fr_te_rank_region"]
        child_col = "province"
    elif alvl == "Circunscripción":
        titulo_ranking = t["fr_te_rank_region"]
        child_col = "province"
    elif alvl == "Distrito":
        titulo_ranking = t["fr_te_rank_region"]
        child_col = "province"
    elif alvl == "Provincia":
        titulo_ranking = t["fr_te_rank_provincia"]
        child_col = "commune_name"
    elif alvl == "Comuna":
        titulo_ranking = None
        child_col = None
    else:
        titulo_ranking = t["fr_te_rank_otro"].format(zona=aval or alvl)
        child_col = None

    render_section_title(t["fr_te_section_nulos_blancos"])

    cards_html = f"""
    <style>
        .nb-cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
        .nb-card {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 160px; }}
        .nb-card-label {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 10pt; color: #6b7280; font-weight: 500; letter-spacing: 0.2px; }}
        .nb-card-value {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; display: flex; align-items: center; gap: 8px; }}
        .nb-card-sub {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 9pt; color: #6b7280; margin-top: 8px; font-weight: 400; }}
        .nb-dot {{ width: 13px; height: 13px; border-radius: 3px; display: inline-block; flex-shrink: 0; }}
    </style>
    <div class="nb-cards">
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_te_card_emitidos']}</div>
            <div class="nb-card-value">{_fmt_number(total_emitidos)}</div>
            <div class="nb-card-sub">{t['fr_te_card_nb_pct'].format(pct=f"{combined_pct:.2f}")}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['valid_votes']}</div>
            <div class="nb-card-value"><span class="nb-dot" style="background-color: {COLOR_VALIDOS}; border: 1px solid #d6cbb8;"></span>{_fmt_number(valid_votes)}</div>
            <div class="nb-card-sub">{t['fr_te_card_pct_total'].format(pct=f"{valid_pct:.1f}")}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['null_votes']}</div>
            <div class="nb-card-value"><span class="nb-dot" style="background-color: {COLOR_NULOS};"></span>{_fmt_number(null_votes) if null_votes else t['fr_te_na']}</div>
            <div class="nb-card-sub">{f"{null_pct:.2f}%" if null_votes else t['fr_te_na']}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['blank_votes']}</div>
            <div class="nb-card-value"><span class="nb-dot" style="background-color: {COLOR_BLANCOS};"></span>{_fmt_number(blank_votes) if blank_votes else t['fr_te_na']}</div>
            <div class="nb-card-sub">{f"{blank_pct:.2f}%" if blank_votes else t['fr_te_na']}</div>
        </div>
    </div>
    """
    st.markdown(cards_html, unsafe_allow_html=True)

    if alvl == "Comuna" or child_col is None:
        return

    col_rank, col_graf = st.columns([0.65, 0.35], gap="medium")

    with col_rank:
        try:
            if child_col not in analysis_gdf.columns:
                st.caption(t["fr_te_no_data"])
                return

            # Region order map: used to sort the ranking north → south.
            region_order_map = {}
            if child_col == "region_name" and "region_order" in analysis_gdf.columns:
                tmp = analysis_gdf[["region_name", "region_order"]].dropna().drop_duplicates()
                for _, r in tmp.iterrows():
                    try:
                        region_order_map[str(r["region_name"])] = int(r["region_order"])
                    except:
                        pass

            # Manual north-to-south order, used as a fallback when the
            # region_order column is not available.
            norte_sur_manual = [
                "Arica y Parinacota", "Arica Y Parinacota",
                "Tarapacá", "Tarapaca",
                "Antofagasta",
                "Atacama",
                "Coquimbo",
                "Valparaíso", "Valparaiso",
                "Metropolitana de Santiago", "Metropolitana", "Región Metropolitana",
                "Libertador General Bernardo O'Higgins", "Libertador", "O'Higgins", "OHiggins",
                "Maule",
                "Ñuble", "Nuble",
                "Biobío", "Biobio",
                "La Araucanía", "La Araucania", "Araucanía", "Araucania",
                "Los Ríos", "Los Rios",
                "Los Lagos",
                "Aysén del General Carlos Ibáñez del Campo", "Aysén", "Aysen",
                "Magallanes y de la Antártica Chilena", "Magallanes"
            ]
            norte_sur_idx = {name.lower(): i for i, name in enumerate(norte_sur_manual)}

            rows = []
            unique_vals = analysis_gdf[child_col].dropna().unique().tolist()
            for child_val in unique_vals:
                c_ids = analysis_gdf[analysis_gdf[child_col] == child_val]["commune_id"].dropna().unique().tolist()
                c_df_f = df_raw[df_raw["commune_id"].isin(c_ids)]
                c_null, c_blank = _extract_null_blank_for_ids(c_ids, df_raw, c_df_f)
                try:
                    c_fr = compute_fn(c_df_f)
                    c_valid = int(c_fr["votes"].sum()) if c_fr is not None and not c_fr.empty and "votes" in c_fr.columns else 0
                except:
                    c_valid = 0
                c_total = c_valid + c_null + c_blank
                c_pct = ((c_null + c_blank) / c_total * 100) if c_total else 0
                if c_total > 0:
                    if child_val in region_order_map:
                        orden = region_order_map[child_val]
                    else:
                        key = str(child_val).lower().strip()
                        orden = None
                        for k, v in norte_sur_idx.items():
                            if k in key or key in k:
                                orden = v
                                break
                        if orden is None:
                            orden = 9999
                    rows.append({
                        "Zona": str(child_val),
                        "Nulos": c_null,
                        "Blancos": c_blank,
                        "N+B": c_null + c_blank,
                        "% N+B": c_pct,
                        "Total": c_total,
                        "_orden": orden
                    })

            if not rows:
                st.caption(t["fr_te_no_data"])
                return

            rank_df = pd.DataFrame(rows)
            if child_col == "region_name":
                rank_df = rank_df.sort_values("_orden", ascending=True)
            else:
                rank_df = rank_df.sort_values("Zona", ascending=True)

            render_section_title(titulo_ranking)

            table_id = f"nb-table-{uuid.uuid4().hex[:8]}"
            max_pct = rank_df["% N+B"].max() if not rank_df.empty else 1

            tbody_rows = ""
            for _, r in rank_df.iterrows():
                zona = r["Zona"]
                nulos_val = int(r["Nulos"]) if r["Nulos"] else 0
                blancos_val = int(r["Blancos"]) if r["Blancos"] else 0
                nb_val = int(r["N+B"]) if r["N+B"] else 0
                pct = r["% N+B"]
                nulos_fmt = f"{nulos_val:,}" if nulos_val else t["fr_te_na"]
                blancos_fmt = f"{blancos_val:,}" if blancos_val else t["fr_te_na"]
                nb_fmt = f"{nb_val:,}" if nb_val else t["fr_te_na"]
                pct_fmt = f"{pct:.2f}%"

                bar_w = int(pct / max_pct * 80) if max_pct else 0
                if nb_val > 0:
                    nulos_ratio = nulos_val / nb_val if nb_val else 0
                    nulos_w = int(bar_w * nulos_ratio)
                    blancos_w = bar_w - nulos_w
                    bar_html = f"<span class='bar-dist' style='width:{bar_w}px'><span class='seg-nulos' style='width:{nulos_w}px'></span><span class='seg-blancos' style='width:{blancos_w}px'></span></span>"
                else:
                    bar_html = f"<span class='bar-single' style='width:{bar_w}px'></span>"

                zona_esc = str(zona).replace('"', '&quot;').replace("'", "&#39;")

                tbody_rows += f"""
                <tr>
                    <td data-value="{zona_esc.lower()}">{zona}</td>
                    <td data-value="{nulos_val}">{nulos_fmt}</td>
                    <td data-value="{blancos_val}">{blancos_fmt}</td>
                    <td data-value="{nb_val}">{nb_fmt}</td>
                    <td data-value="{pct:.4f}">{pct_fmt} {bar_html}</td>
                </tr>
                """

            header_zona = t["fr_te_th_comuna"] if child_col=="commune_name" else t["fr_te_th_zona"]

            html_table = f"""
            <style>
                .tabla-contenedor-sort {{ border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; max-width: 750px; width: 100%; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }}
                .tabla-contenedor-sort table {{ width: 100%; border-collapse: collapse; table-layout: auto; }}
                .tabla-contenedor-sort th {{ background-color: #f9f9f9; text-align: left; padding: 8px 12px; font-size: 7.5pt; color: #666; text-transform: uppercase; border-bottom: 1px solid #e0e0e0; font-weight: 600; letter-spacing: 0.04em; line-height: 1.1; cursor: pointer; user-select: none; position: relative; }}
                .tabla-contenedor-sort th:hover {{ background-color: #f0f0f0; color: #111827; }}
                .tabla-contenedor-sort td {{ padding: 8px 12px; border-bottom: 1px solid #f0f0f0; font-size: 10.5pt; color: #333; font-weight: 400; line-height: 1.3; }}
                .tabla-contenedor-sort tr:last-child td {{ border-bottom: none; }}
                .tabla-contenedor-sort .sort-arrow {{ margin-left: 6px; font-size: 9pt; color: #9ca3af; }}
                .tabla-contenedor-sort th.active {{ color: #111827; }}
                .tabla-contenedor-sort th.active .sort-arrow {{ color: #111827; }}
                .tabla-contenedor-sort .bar-dist {{ display:inline-flex; height:10px; border-radius:5px; overflow:hidden; vertical-align:middle; margin-left:8px; background:#e5e7eb; }}
                .tabla-contenedor-sort .seg-nulos {{ background:{COLOR_NULOS}; height:100%; }}
                .tabla-contenedor-sort .seg-blancos {{ background:{COLOR_BLANCOS}; height:100%; }}
                .tabla-contenedor-sort .bar-single {{ height:10px; background:{COLOR_NULOS}; border-radius:5px; display:inline-block; vertical-align:middle; margin-left:8px; }}
            </style>
            <div class="tabla-contenedor-sort">
                <table id="{table_id}">
                    <thead>
                        <tr>
                            <th data-col="0" data-type="text" onclick="sortNbTable('{table_id}', 0, 'text', this)">{header_zona} <span class="sort-arrow">↕</span></th>
                            <th data-col="1" data-type="number" onclick="sortNbTable('{table_id}', 1, 'number', this)">{t['fr_te_th_nulos']} <span class="sort-arrow">↕</span></th>
                            <th data-col="2" data-type="number" onclick="sortNbTable('{table_id}', 2, 'number', this)">{t['fr_te_th_blancos']} <span class="sort-arrow">↕</span></th>
                            <th data-col="3" data-type="number" onclick="sortNbTable('{table_id}', 3, 'number', this)">{t['fr_te_th_nb']} <span class="sort-arrow">↕</span></th>
                            <th data-col="4" data-type="number" onclick="sortNbTable('{table_id}', 4, 'number', this)">{t['fr_te_th_pct_nb']} <span class="sort-arrow">↕</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        {tbody_rows}
                    </tbody>
                </table>
            </div>
            <script>
            function sortNbTable(tableId, colIndex, type, headerEl) {{
                const table = document.getElementById(tableId);
                const tbody = table.tBodies[0];
                const rows = Array.from(tbody.rows);

                let dir = headerEl.getAttribute('data-dir');
                if (!dir || dir === 'desc') {{
                    dir = 'asc';
                }} else {{
                    dir = 'desc';
                }}

                const allHeaders = table.querySelectorAll('th');
                allHeaders.forEach(th => {{
                    if (th !== headerEl) {{
                        th.removeAttribute('data-dir');
                        const arrow = th.querySelector('.sort-arrow');
                        if (arrow) arrow.textContent = '↕';
                        th.classList.remove('active');
                    }}
                }});
                headerEl.setAttribute('data-dir', dir);
                headerEl.classList.add('active');
                const arrow = headerEl.querySelector('.sort-arrow');
                if (arrow) arrow.textContent = dir === 'asc' ? '↑' : '↓';

                rows.sort((a, b) => {{
                    let aVal = a.cells[colIndex].getAttribute('data-value');
                    let bVal = b.cells[colIndex].getAttribute('data-value');

                    if (type === 'number') {{
                        aVal = parseFloat(aVal) || 0;
                        bVal = parseFloat(bVal) || 0;
                        return dir === 'asc' ? aVal - bVal : bVal - aVal;
                    }} else {{
                        aVal = (aVal || '').toLowerCase();
                        bVal = (bVal || '').toLowerCase();
                        if (aVal < bVal) return dir === 'asc' ? -1 : 1;
                        if (aVal > bVal) return dir === 'asc' ? 1 : -1;
                        return 0;
                    }}
                }});

                rows.forEach(row => tbody.appendChild(row));
            }}
            </script>
            """

            # Scroll only if the table exceeds 700px.
            real_height = 62 + len(rank_df) * 36
            h = min(700, max(120, real_height))
            needs_scroll = real_height > 700
            components.html(html_table, height=h, scrolling=needs_scroll)

        except Exception as e:
            st.caption(t["fr_te_rank_unavailable"].format(err=e))
            st.exception(e)

    with col_graf:
        st.markdown("<div style='height:78px;'></div>", unsafe_allow_html=True)
        try:
            total = valid_votes + null_votes + blank_votes
            if total > 0:
                v_pct = valid_votes / total * 100 if total else 0
                n_pct = null_votes / total * 100 if total else 0
                b_pct = blank_votes / total * 100 if total else 0
                v_sq = int(round(v_pct))
                n_sq = int(round(n_pct))
                b_sq = int(round(b_pct))
                if null_votes > 0 and n_sq == 0:
                    n_sq = 1
                if blank_votes > 0 and b_sq == 0:
                    b_sq = 1
                v_sq = 100 - n_sq - b_sq
                if v_sq < 0:
                    v_sq = 0
                squares = []
                squares += [(COLOR_VALIDOS, t["fr_te_waffle_validos"].format(n=f"{valid_votes:,}", pct=f"{v_pct:.1f}"))] * v_sq
                squares += [(COLOR_NULOS, t["fr_te_waffle_nulos"].format(n=f"{null_votes:,}", pct=f"{n_pct:.1f}"))] * n_sq
                squares += [(COLOR_BLANCOS, t["fr_te_waffle_blancos"].format(n=f"{blank_votes:,}", pct=f"{b_pct:.1f}"))] * b_sq
                if len(squares) < 100:
                    squares += [(COLOR_VALIDOS, t["fr_te_waffle_validos"].format(n=f"{valid_votes:,}", pct=f"{v_pct:.1f}"))] * (100 - len(squares))
                squares = squares[:100]
                waffle_html = f'''
                <style>
                    .waffle-wrap {{ max-width: 280px; font-family: "Liberation Sans", Arial, sans-serif; }}
                    .waffle-grid {{ display: grid; grid-template-columns: repeat(10, 1fr); gap: 4px; margin-bottom: 14px; }}
                    .waffle-sq {{
                        width: 100%;
                        aspect-ratio: 1;
                        border-radius: 3px;
                        position: relative;
                        cursor: default;
                        transition: filter 0.12s ease, outline 0.12s ease;
                    }}
                    .waffle-sq:hover {{
                        filter: brightness(0.92);
                        outline: 1px solid rgba(0,0,0,0.25);
                        outline-offset: 0px;
                    }}
                    .waffle-sq::after {{
                        content: attr(data-tip);
                        position: absolute;
                        bottom: 125%;
                        left: 50%;
                        transform: translateX(-50%);
                        background: #1f2937;
                        color: #fff;
                        padding: 5px 8px;
                        border-radius: 5px;
                        font-size: 8.5pt;
                        white-space: nowrap;
                        opacity: 0;
                        pointer-events: none;
                        transition: opacity 0.12s ease;
                        z-index: 30;
                        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
                    }}
                    .waffle-sq:hover::after {{ opacity: 1; }}
                    .waffle-legend {{ display: none; }}
                </style>
                <div class="waffle-wrap">
                    <div class="waffle-grid">
                '''
                for col, tip in squares:
                    safe_tip = tip.replace('"', '&quot;')
                    waffle_html += f'<div class="waffle-sq" style="background-color: {col};" data-tip="{safe_tip}" title="{safe_tip}"></div>'
                waffle_html += '</div></div>'
                st.markdown(waffle_html, unsafe_allow_html=True)
            else:
                st.caption(t["fr_te_no_waffle"])
        except Exception as e:
            st.caption(t["fr_te_waffle_unavailable"].format(err=e))


def _render_page_footer(t):
    st.markdown(f"""
    <style>
        .page-footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; width: 100%; }}
        .page-footer p {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; color: #9a9a9a; text-align: center; margin: 0; line-height: 1.4; }}
    </style>
    <div class="page-footer"><p>{t['data_source']} · {t['data_source_note']}</p></div>
    """, unsafe_allow_html=True)


# ============================================================================
# TERRITORIAL NAVIGATION — CORE (DO NOT TOUCH)
# ============================================================================
# WARNING: The identifiers below are part of the most critical state machine
# in the dashboard. Per an explicit project decision, they are kept in
# Spanish. Renaming them (e.g. "Todas" → "All", COLS → COLUMNS) is a
# time bomb: any change in these identifiers has a high risk of introducing
# subtle navigation bugs (double-click issues, lost context, sibling
# universe mismatches). Do not translate, do not rename, do not refactor.

def _clean(v):
    if pd.isna(v):
        return ""
    return unicodedata.normalize("NFC", str(v).strip())


def _fold(v):
    if pd.isna(v):
        return ""
    return unicodedata.normalize("NFC", str(v).strip()).casefold()


def _num_key(v):
    t = _clean(v)
    try:
        return (0, int(float(t)))
    except:
        return (1, t.casefold())


def _unique(df, col, order_col=None, numeric=False):
    if col not in df.columns or df.empty:
        return []
    cols = [col] + ([order_col] if order_col and order_col in df.columns else [])
    w = df[cols].copy()
    w[col] = w[col].map(_clean)
    w = w[w[col] != ""]
    if w.empty:
        return []
    if order_col and order_col in w.columns:
        w[order_col] = pd.to_numeric(w[order_col], errors='coerce')
        w = w.sort_values(order_col, na_position='last')
        w = w.drop_duplicates(subset=[col])
    else:
        if numeric:
            w["_n"] = w[col].map(lambda x: _num_key(x))
            w = w.sort_values("_n")
        else:
            w = w.sort_values(col, key=lambda s: s.str.casefold())
        w = w.drop_duplicates(subset=[col])
    return w[col].tolist()


def _filter(df, col, val):
    if val in (None, "Todas", ""):
        return df
    return df[df[col].map(_fold) == _fold(val)].copy()


LEVELS = ["Macrozona","Región","Circunscripción","Distrito","Provincia","Comuna"]
COLS = {"Macrozona": "macrozone","Región": "region_name","Circunscripción": "circunscripcion_senatorial","Distrito": "distrito_electoral","Provincia": "province","Comuna": "commune_name",}
KEYS = {"Macrozona": "communal_macrozone_v2","Región": "communal_region_v2","Circunscripción": "communal_circ_v2","Distrito": "communal_distrito_v2","Provincia": "communal_provincia_v2","Comuna": "communal_comuna_v2",}
ANCHOR_KEY = "communal_anchor_v2"
PREV_ANCHOR_KEY = "communal_prev_anchor_v2"
EXPLICIT_MACROZONA_KEY = "communal_macrozona_explicit_v2"


def _prepare(gdf_communes):
    gdf = gdf_communes.copy()
    needed = ["commune_id","region_code","region_name","region_order","macrozone","macrozone_order","circunscripcion_senatorial","distrito_electoral","province","commune_name"]
    missing = [c for c in needed if c not in gdf.columns]
    if missing:
        from utils.data_loader import load_dim_commune
        dim = load_dim_commune().copy()
        avail = [c for c in needed if c in dim.columns and c not in gdf.columns]
        if avail:
            gdf = gdf.merge(dim[["commune_id"]+avail], on="commune_id", how="left")
    return gdf


def _reset():
    for k in KEYS.values():
        st.session_state[k] = "Todas"
    st.session_state[ANCHOR_KEY] = "Nacional"
    st.session_state[PREV_ANCHOR_KEY] = "Nacional"
    st.session_state[EXPLICIT_MACROZONA_KEY] = False


def _infer_ancestors(gdf, level, value):
    rows = _filter(gdf, COLS[level], value)
    if rows.empty:
        return {}
    row = rows.iloc[0]
    res = {}
    for anc_lvl in LEVELS[:LEVELS.index(level)]:
        col = COLS[anc_lvl]
        if col in row:
            v = _clean(row[col])
            if v:
                res[anc_lvl] = v
    return res


def _on_change(gdf, level):
    def _cb():
        new_val = _clean(st.session_state.get(KEYS[level], "Todas")) or "Todas"
        old_anchor = st.session_state.get(ANCHOR_KEY, "Nacional")
        if new_val == "Todas":
            st.session_state[KEYS[level]] = "Todas"
            st.session_state[ANCHOR_KEY] = "Nacional"
            st.session_state[PREV_ANCHOR_KEY] = old_anchor
            if level == "Macrozona":
                st.session_state[EXPLICIT_MACROZONA_KEY] = False
            for lvl in LEVELS[LEVELS.index(level)+1:]:
                st.session_state[KEYS[lvl]] = "Todas"
            return
        ancestors = _infer_ancestors(gdf, level, new_val)
        for anc_lvl, anc_val in ancestors.items():
            st.session_state[KEYS[anc_lvl]] = anc_val
        st.session_state[KEYS[level]] = new_val
        st.session_state[PREV_ANCHOR_KEY] = old_anchor
        st.session_state[ANCHOR_KEY] = level
        if level == "Macrozona":
            st.session_state[EXPLICIT_MACROZONA_KEY] = True
        for lvl in LEVELS[LEVELS.index(level)+1:]:
            st.session_state[KEYS[lvl]] = "Todas"
    return _cb


def _effective_state(gdf):
    raw = {lvl: _clean(st.session_state.get(KEYS[lvl], "Todas")) or "Todas" for lvl in LEVELS}
    anchor = st.session_state.get(ANCHOR_KEY, "Nacional")
    prev_anchor = st.session_state.get(PREV_ANCHOR_KEY, "Nacional")
    if anchor == "Nacional":
        return raw, anchor, prev_anchor
    if anchor not in LEVELS:
        return raw, "Nacional", prev_anchor
    if raw[anchor] == "Todas":
        return raw, "Nacional", prev_anchor
    idx = LEVELS.index(anchor)
    for anc in LEVELS[:idx]:
        if raw[anc] == "Todas":
            inf = _infer_ancestors(gdf, anchor, raw[anchor])
            for k,v in inf.items():
                raw[k] = v
            break
    return raw, anchor, prev_anchor


def _sibling_universe(gdf, state, anchor, prev_anchor):
    if anchor == "Nacional":
        return gdf
    anchor_idx = LEVELS.index(anchor)
    if prev_anchor == "Nacional" and anchor in ["Región","Circunscripción","Distrito","Provincia"]:
        return gdf
    for parent_idx in range(anchor_idx-1, -1, -1):
        parent_lvl = LEVELS[parent_idx]
        parent_val = state[parent_lvl]
        if parent_val == "Todas":
            continue
        parent_univ = _filter(gdf, COLS[parent_lvl], parent_val)
        if parent_univ.empty:
            continue
        is_numeric = anchor in ["Circunscripción","Distrito"]
        uniq = _unique(parent_univ, COLS[anchor], numeric=is_numeric, order_col="region_order" if anchor=="Región" else ("macrozone_order" if anchor=="Macrozona" else None))
        if len(uniq) > 1:
            return parent_univ
    if prev_anchor != "Nacional" and prev_anchor in LEVELS:
        prev_val = state.get(prev_anchor, "Todas")
        if prev_val != "Todas":
            pu = _filter(gdf, COLS[prev_anchor], prev_val)
            if not pu.empty:
                return pu
    return gdf


# ============================================================================
# MAIN RENDER
# ============================================================================
def render_territorial_explorer(t, df_raw, gdf_communes):
    gdf = _prepare(gdf_communes)
    if gdf.empty:
        st.warning(t["fr_te_no_data"])
        return
    state, anchor, prev_anchor = _effective_state(gdf)
    if anchor == "Nacional":
        anchor_universe = gdf
        anchor_idx = -1
    else:
        anchor_idx = LEVELS.index(anchor)
        anchor_universe = _filter(gdf, COLS[anchor], state[anchor])
    sib_universe = _sibling_universe(gdf, state, anchor, prev_anchor)
    options = {}
    for idx, lvl in enumerate(LEVELS):
        if anchor == "Nacional":
            if lvl == "Macrozona":
                options[lvl] = _unique(gdf, COLS[lvl], "macrozone_order")
            elif lvl == "Región":
                options[lvl] = _unique(gdf, COLS[lvl], "region_order")
            elif lvl in ("Circunscripción","Distrito"):
                options[lvl] = _unique(gdf, COLS[lvl], numeric=True)
            else:
                options[lvl] = _unique(gdf, COLS[lvl])
        elif idx < anchor_idx:
            options[lvl] = [state[lvl]] if state[lvl] != "Todas" else []
        elif idx == anchor_idx:
            if lvl == "Macrozona":
                options[lvl] = _unique(gdf, COLS[lvl], "macrozone_order")
            elif lvl == "Región":
                options[lvl] = _unique(sib_universe, COLS[lvl], "region_order")
            elif lvl in ("Circunscripción","Distrito"):
                options[lvl] = _unique(sib_universe, COLS[lvl], numeric=True)
            else:
                options[lvl] = _unique(sib_universe, COLS[lvl])
        else:
            # The options of the child levels depend on the current anchor
            # and on the values already selected. This block is one of the
            # most complex parts of the state machine: any change here can
            # introduce subtle navigation bugs.
            if lvl == "Provincia" and state.get("Distrito", "Todas") != "Todas":
                base = _filter(gdf, COLS["Distrito"], state["Distrito"])
            elif lvl == "Provincia" and state.get("Región", "Todas") != "Todas":
                base = _filter(gdf, COLS["Región"], state["Región"])
            elif lvl == "Distrito" and state.get("Circunscripción", "Todas") != "Todas":
                base = _filter(gdf, COLS["Circunscripción"], state["Circunscripción"])
            elif lvl == "Distrito" and state.get("Distrito", "Todas") != "Todas" and anchor == "Nacional":
                row = _filter(gdf, COLS["Distrito"], state["Distrito"])
                if not row.empty:
                    circ = _clean(row.iloc[0].get(COLS["Circunscripción"], ""))
                    base = _filter(gdf, COLS["Circunscripción"], circ) if circ else anchor_universe
                else:
                    base = anchor_universe
            elif lvl == "Comuna" and state.get("Provincia", "Todas") != "Todas":
                base = _filter(gdf, COLS["Provincia"], state["Provincia"])
            elif lvl == "Comuna" and state.get("Provincia", "Todas") == "Todas" and state.get("Región", "Todas") != "Todas":
                base = _filter(gdf, COLS["Región"], state["Región"])
            elif state.get("Macrozona", "Todas") != "Todas" and state.get("Región", "Todas") == "Todas":
                if lvl == "Distrito" and state.get("Circunscripción", "Todas") != "Todas":
                    base = _filter(gdf, COLS["Circunscripción"], state["Circunscripción"])
                elif lvl == "Distrito":
                    base = _filter(gdf, COLS["Macrozona"], state["Macrozona"])
                elif lvl == "Circunscripción":
                    base = _filter(gdf, COLS["Macrozona"], state["Macrozona"])
                else:
                    base = _filter(gdf, COLS["Macrozona"], state["Macrozona"])
            else:
                base = anchor_universe
            if lvl in ("Circunscripción","Distrito"):
                options[lvl] = _unique(base, COLS[lvl], numeric=True)
            elif lvl == "Región":
                options[lvl] = _unique(base, COLS[lvl], "region_order")
            elif lvl == "Macrozona":
                options[lvl] = _unique(base, COLS[lvl], "macrozone_order")
            else:
                options[lvl] = _unique(base, COLS[lvl])
        cur = state[lvl]
        if _fold(cur) not in ("", "todas") and not any(_fold(o) == _fold(cur) for o in options[lvl]):
            options[lvl] = [cur] + options[lvl]

    trail = []
    for lvl in LEVELS:
        if state[lvl] != "Todas":
            if lvl == "Circunscripción":
                trail.append(t["fr_te_breadcrumb_circunscripcion"].format(n=state[lvl]))
            elif lvl == "Distrito":
                trail.append(t["fr_te_breadcrumb_distrito"].format(n=state[lvl]))
            else:
                trail.append(state[lvl])
    trail_txt = " > ".join(trail) if trail else t["fr_te_breadcrumb_nacional"]
    st.markdown(f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 9pt; color: #6b7280; margin-bottom: 8px;\">{t['fr_te_breadcrumb'].format(trail=trail_txt, anchor=anchor)}</div>", unsafe_allow_html=True)

    if st.button(t["fr_te_reset_btn"], key="reset_v2"):
        _reset()
        st.rerun()
    st.divider()
    col_nav, col_map = st.columns([0.3, 0.7], gap="large")
    with col_nav:
        render_view_title(t["fr_te_view_title"])

        # The internal value "Todas" must stay fixed to not break the state
        # machine. format_func translates "Todas" to "All" (or the current
        # language) only on screen.
        fmt_all = lambda x: t["fr_te_level_all"] if x == "Todas" else x

        st.selectbox(
            t["fr_te_level_macrozona"],
            ["Todas"] + options["Macrozona"],
            format_func=fmt_all,
            key=KEYS["Macrozona"],
            on_change=_on_change(gdf, "Macrozona")
        )
        st.selectbox(
            t["fr_te_level_region"],
            ["Todas"] + options["Región"],
            format_func=fmt_all,
            key=KEYS["Región"],
            on_change=_on_change(gdf, "Región")
        )
        st.selectbox(
            t["fr_te_level_circunscripcion"],
            ["Todas"] + options["Circunscripción"],
            format_func=fmt_all,
            key=KEYS["Circunscripción"],
            on_change=_on_change(gdf, "Circunscripción")
        )
        st.selectbox(
            t["fr_te_level_distrito"],
            ["Todas"] + options["Distrito"],
            format_func=fmt_all,
            key=KEYS["Distrito"],
            on_change=_on_change(gdf, "Distrito")
        )
        st.selectbox(
            t["fr_te_level_provincia"],
            ["Todas"] + options["Provincia"],
            format_func=fmt_all,
            key=KEYS["Provincia"],
            on_change=_on_change(gdf, "Provincia")
        )
        st.selectbox(
            t["fr_te_level_comuna"],
            ["Todas"] + options["Comuna"],
            format_func=fmt_all,
            key=KEYS["Comuna"],
            on_change=_on_change(gdf, "Comuna")
        )

    state = {lvl: _clean(st.session_state.get(KEYS[lvl], "Todas")) or "Todas" for lvl in LEVELS}
    anchor = st.session_state.get(ANCHOR_KEY, "Nacional")
    if state["Comuna"] != "Todas":
        alvl, aval = "Comuna", state["Comuna"]
    elif state["Provincia"] != "Todas":
        alvl, aval = "Provincia", state["Provincia"]
    elif state["Distrito"] != "Todas":
        alvl, aval = "Distrito", state["Distrito"]
    elif state["Circunscripción"] != "Todas":
        alvl, aval = "Circunscripción", state["Circunscripción"]
    elif state["Región"] != "Todas":
        alvl, aval = "Región", state["Región"]
    elif state["Macrozona"] != "Todas":
        alvl, aval = "Macrozona", state["Macrozona"]
    else:
        alvl, aval = "Nacional", None
    analysis_gdf = gdf if alvl=="Nacional" else _filter(gdf, COLS[alvl], aval)
    map_gdf, map_label, group_col = _build_map_gdf_progresivo(gdf, df_raw, alvl, aval, t)
    with col_map:
        render_view_title(t["fr_te_view_mapa"].format(label=map_label, n=len(map_gdf)))
        if map_gdf.empty:
            st.warning(t["fr_te_no_zones"].format(alvl=alvl, aval=aval))
        else:
            _render_mapa(map_gdf, group_col, alvl, aval, t)
    st.divider()
    if analysis_gdf.empty:
        return
    ids = set(analysis_gdf["commune_id"].dropna().tolist())
    df_f = df_raw[df_raw["commune_id"].isin(ids)].copy()
    if df_f.empty:
        st.warning(t["fr_te_no_votes"])
        return
    from utils.calculations import compute_first_round_results
    fr = compute_first_round_results(df_f)

    if aval is None:
        resultados_txt = alvl
    elif alvl == "Circunscripción":
        resultados_txt = t["fr_te_breadcrumb_circunscripcion"].format(n=aval)
    elif alvl == "Distrito":
        resultados_txt = t["fr_te_breadcrumb_distrito"].format(n=aval)
    else:
        resultados_txt = aval

    render_view_title(t["fr_te_view_resultados"].format(zona=resultados_txt))
    render_section_title(t["fr_te_section_validos"])
    col_tabla, col_donut = st.columns([0.58, 0.42], gap="medium")
    with col_tabla:
        _render_resultados_table(fr, t)
    with col_donut:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        _render_donut_chart(fr, t)

    _render_null_blank_analysis(alvl, aval, analysis_gdf, df_raw, df_f, fr, compute_first_round_results, t)

    _render_cascading_tables(alvl, aval, analysis_gdf, df_raw, compute_first_round_results, t)

    _render_page_footer(t)


def render(t):
    try:
        with st.spinner(t["loading"]):
            df_raw = load_fact_first_round_2025()
            gdf_communes = prepare_commune_geometries()
        render_territorial_explorer(t, df_raw, gdf_communes)
    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
