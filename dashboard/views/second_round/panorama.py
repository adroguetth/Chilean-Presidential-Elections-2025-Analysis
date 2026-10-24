"""
Second Round — Panorama
============================================================================
Visual analysis view for the Second Round 2025. Contains 12 collapsible
sections covering national participation, participation comparison (1V vs
2V), null/blank vote analysis (with selector for 2V vs comparison), national
results, communes won, regional winners, regional capitals, vote by commune
size, electoral realignment, Parisi's fate (with selector for participation
/ protest / margin), and Parisi's commune segmentation (KMeans + PCA).

Sections:
 1. National participation (cards)
 2. Participation and valid vote: 1V vs 2V
 3. Null vote analysis (with selector: 2V / comparison)
 4. Blank vote analysis (with selector: 2V / comparison)
 5. National results (2V)
 6. Communes won (table + waffle)
 7. Regional winners
 8. Vote in regional capitals
 9. Vote by commune size (stacked bars)
 10. Electoral realignment: winner transitions 1V → 2V
 11. Parisi: the fate of the anti-system vote (with selector)
 12. Parisi: segmentation of his communes

Notes:
 All HTML is passed through _clean_html() before st.markdown() to prevent
 Markdown from interpreting indented f-strings (4+ spaces) as code blocks.
 Transformation helpers (clean_html, format_number, hex_to_rgba,
 normalize_commune) are imported from utils.html_helpers.
 Titles use components.titles.

Technical debt:
 Three groups of user-facing strings are still hardcoded in Spanish and
 should be migrated to translations.py in a future cleanup pass:
 - POPULATION_BRACKETS labels and subtitles.
 - Plotly hover labels in _plot_top_bar (label_map).
 - Parisi bracket labels in _classify_parisi_brackets_4 and _5.
 See the TECHNICAL DEBT block at the bottom of the file for details.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats as scipy_stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from utils.data_loader import (
    load_fact_first_round_2025,
    load_fact_second_round_2025,
    load_dim_commune,
)
from utils.html_helpers import (
    clean_html as _clean_html,
    format_number as _fmt_number,
    hex_to_rgba as _hex_to_rgba,
    normalize_commune as _norm_commune,
)
from config.constants import (
    COLOR_VALIDOS,
    COLOR_NULOS,
    COLOR_BLANCOS,
    COLOR_NEGATIVE,
    COLOR_NEUTRAL_INDICATOR,
    NEUTRAL_COLOR,
    TREND_COLOR_UP,
    TREND_COLOR_DOWN,
    TREND_COLOR_FLAT,
    TREND_GRAY,
    CLUSTER_COLORS,
    _get_candidate_color,
    _hex_to_rgba_string,
)
from components.titles import (
    render_view_title,
    render_view_subtitle,
    render_section_title,
    render_section_subtitle,
)

# ============================================================================
# CONSTANTS
# ============================================================================
VOTE_COLS_FR = [
    "jara_votes", "kast_votes", "parisi_votes", "kaiser_votes",
    "matthei_votes", "mayne_nicholls_votes",
    "enriquez_ominami_votes", "artes_votes",
]
VOTE_COLS_TO_NAMES_FR = {
    "jara_votes": "Jeannette Jara",
    "kast_votes": "José Antonio Kast",
    "parisi_votes": "Franco Parisi",
    "kaiser_votes": "Johannes Kaiser",
    "matthei_votes": "Evelyn Matthei",
    "mayne_nicholls_votes": "Harold Mayne-Nicholls",
    "enriquez_ominami_votes": "Marco Enríquez-Ominami",
    "artes_votes": "Eduardo Artés",
}
VOTE_COLS_TO_NAMES = {
    "jara_votes": "Jeannette Jara",
    "kast_votes": "José Antonio Kast",
}
# Labels with ideology (for the transition matrix).
WINNER_LABELS_1V_IDEOLOGY = {
    "jara": "Jara (izquierda)",  # "Jara (left)"
    "kast": "Kast (derecha)",  # "Kast (right)"
    "parisi": "Parisi (antisistema)",  # "Parisi (anti-system)"
    "kaiser": "Kaiser (libertario)",  # "Kaiser (libertarian)"
    "matthei": "Matthei (derecha tradicional)",  # "Matthei (traditional right)"
    "mayne_nicholls": "Mayne-Nicholls (centro)",  # "Mayne-Nicholls (center)"
    "enriquez_ominami": "Enríquez-Ominami (izquierda)",  # "Enríquez-Ominami (left)"
    "artes": "Artés (izquierda radical)",  # "Artés (radical left)"
}
WINNER_LABELS_2V_IDEOLOGY = {
    "jara": "Jara (izquierda)",  # "Jara (left)"
    "kast": "Kast (derecha)",  # "Kast (right)"
}
MIN_CASTED_VOTES = 300
# Candidate colors (single source: constants).
KAST_COLOR = _get_candidate_color("José Antonio Kast")
JARA_COLOR = _get_candidate_color("Jeannette Jara")
REGIONAL_CAPITALS = [
    "Arica", "Iquique", "Antofagasta", "Copiapó", "La Serena",
    "Valparaíso", "Santiago", "Rancagua", "Talca", "Chillán",
    "Concepción", "Temuco", "Valdivia", "Puerto Montt", "Coyhaique",
    "Punta Arenas",
]
# NOTE: labels and subtitles are user-facing strings hardcoded in Spanish.
# They should live in translations.py. See TECHNICAL DEBT at the bottom.
POPULATION_BRACKETS = [
    {"label": "Grandes centros urbanos", "sub": "más de 200.000 hab.", "min": 200_001, "max": None},  # "Large urban centers", "more than 200,000 inhabitants"
    {"label": "Centros urbanos medios", "sub": "100.000 – 199.999 hab.", "min": 100_000, "max": 199_999},  # "Medium urban centers", "100,000 – 199,999 inhabitants"
    {"label": "Centros urbanos pequeños", "sub": "50.000 – 99.999 hab.", "min": 50_000, "max": 99_999},  # "Small urban centers", "50,000 – 99,999 inhabitants"
    {"label": "Rural-urbano", "sub": "10.000 – 49.999 hab.", "min": 10_000, "max": 49_999},  # "Rural-urban", "10,000 – 49,999 inhabitants"
    {"label": "Rural", "sub": "menos de 10.000 hab.", "min": 0, "max": 9_999},  # "Rural", "fewer than 10,000 inhabitants"
]
SR_CANDIDATES = [
    {"name": "Jeannette Jara", "votes_col": "jara_votes"},
    {"name": "José Antonio Kast", "votes_col": "kast_votes"},
]

# ============================================================================
# LOCAL HELPERS — VISUAL FORMATTING
# ============================================================================
def _compute_winner_sr(df: pd.DataFrame) -> pd.Series:
    if "jara_votes" in df.columns and "kast_votes" in df.columns:
        return df.apply(
            lambda r: "Jeannette Jara" if r["jara_votes"] > r["kast_votes"] else "José Antonio Kast",
            axis=1,
        )
    return pd.Series(["No data"] * len(df), index=df.index)

def _compute_winner_fr(df: pd.DataFrame) -> pd.Series:
    cols = [c for c in VOTE_COLS_FR if c in df.columns]
    if not cols:
        return pd.Series(["No data"] * len(df), index=df.index)
    return df[cols].idxmax(axis=1).map(VOTE_COLS_TO_NAMES_FR)

def _candidate_cell(name: str, escape: bool = True) -> str:
    if name is None:
        name = ""
    display = str(name).strip()
    if escape:
        display = (
            display.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
    color = _get_candidate_color(name)
    return (
        f'<span class="pa-color-box" style="background:{color};"></span>'
        f'{display}'
    )

def _table_gap():
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

def _trend_pill(trend: str, t: dict) -> str:
    if trend == "sube":
        color = TREND_COLOR_UP
        bg = _hex_to_rgba_string(TREND_COLOR_UP, 0.12)
        label = t["sr_pano_trend_up"]
    elif trend == "baja":
        color = TREND_COLOR_DOWN
        bg = _hex_to_rgba_string(TREND_COLOR_DOWN, 0.12)
        label = t["sr_pano_trend_down"]
    else:
        color = TREND_COLOR_FLAT
        bg = _hex_to_rgba_string(TREND_COLOR_FLAT, 0.12)
        label = t["sr_pano_trend_flat"]
    return (
        f'<span class="pa-trend-pill" '
        f'style="background:{bg}; color:{color};">{label}</span>'
    )

def _render_page_footer(t: dict) -> None:
    st.markdown(_clean_html(_FOOTER_CSS + f"""
    <div class="page-footer"><p>{t['data_source']} · {t['data_source_note']}</p></div>
    """), unsafe_allow_html=True)

def _render_nb_card(label: str, value: str, sub: str, accent_color: str = None):
    accent_style = f' style="color:{accent_color};"' if accent_color else ""
    html = _NB_SINGLE_CARD_CSS + f"""
    <div class="nb-single-card">
        <div class="nb-single-card-label">{label}</div>
        <div class="nb-single-card-value"{accent_style}>{value}</div>
        <div class="nb-single-card-sub">{sub}</div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)

def _render_nb_cards_row(cards: list):
    inner = ""
    for label, value, sub, accent in cards:
        accent_style = f' style="color:{accent};"' if accent else ""
        inner += f"""
        <div class="nb-card">
            <div class="nb-card-label">{label}</div>
            <div class="nb-card-value"{accent_style}>{value}</div>
            <div class="nb-card-sub">{sub}</div>
        </div>
        """
    html = _NB_CARD_CSS + f'<div class="nb-cards">{inner}</div>'
    st.markdown(_clean_html(html), unsafe_allow_html=True)

# ============================================================================
# SHARED CSS
# ============================================================================
_NB_CARD_CSS = """
<style>
    .nb-cards { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
    .nb-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 160px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }
    .nb-card-label { font-size: 10pt; color: #6b7280; font-weight: 500; letter-spacing: 0.2px; }
    .nb-card-value { font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; }
    .nb-card-sub { font-size: 9pt; font-weight: 400; color: #6b7280; margin-top: 8px; }
</style>
"""

_NB_SINGLE_CARD_CSS = """
<style>
    .nb-single-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 16px; font-family: "Liberation Sans", Arial, sans-serif; }
    .nb-single-card-label { font-size: 10pt; color: #6b7280; font-weight: 500; letter-spacing: 0.2px; }
    .nb-single-card-value { font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; }
    .nb-single-card-sub { font-size: 9pt; color: #6b7280; margin-top: 8px; line-height: 1.5; }
</style>
"""

_FOOTER_CSS = """
<style>
    .page-footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; width: 100%; }
    .page-footer p { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; color: #9a9a9a; text-align: center; margin: 0; line-height: 1.4; }
</style>
"""

_WAFFLE_CSS = """
<style>
    .waffle-wrap { max-width: 940px; font-family: "Liberation Sans", Arial, sans-serif; }
    .waffle-title { font-size: 9pt; color: #6b7280; margin-bottom: 10px; }
    .waffle-grid { display: grid; grid-template-columns: repeat(32, 1fr); gap: 3px; }
    .waffle-cell { aspect-ratio: 1; border-radius: 2px; cursor: default; transition: transform 0.08s ease, outline 0.08s ease; }
    .waffle-cell:hover { transform: scale(1.3); outline: 1px solid rgba(0,0,0,0.45); position: relative; z-index: 2; }
</style>
"""

_TRAMOS_CSS = """
<style>
    .tramos-wrap { font-family: "Liberation Sans", Arial, sans-serif; max-width: 940px; }
    .tramo-wrap { margin-bottom: 22px; }
    .tramo-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
    .tramo-label { font-size: 11pt; font-weight: 700; color: #111827; }
    .tramo-label span { font-weight: 400; color: #6b7280; font-size: 9pt; }
    .tramo-meta { font-size: 9pt; color: #6b7280; }
    .tramo-bar-wrap { position: relative; }
    .tramo-bar { display: flex; height: 34px; border-radius: 6px; overflow: hidden; width: 100%; box-sizing: border-box; isolation: isolate; }
    .tramo-seg { display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 10.5pt; flex-shrink: 0; box-sizing: border-box; overflow: hidden; }
    .tramo-seg-first { border-top-left-radius: 6px; border-bottom-left-radius: 6px; }
    .tramo-seg-last { border-top-right-radius: 6px; border-bottom-right-radius: 6px; }
    .tramo-midline { position: absolute; top: -6px; bottom: -6px; left: 50%; width: 0; border-left: 1px dashed #9ca3af; pointer-events: none; z-index: 2; }
    .tramos-leyendas { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 12px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 9pt; color: #333; }
    .legend-item { display: flex; align-items: center; gap: 8px; font-size: 10.5pt; color: #333; }
    .legend-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; flex-shrink: 0; }
</style>
"""

# ============================================================================
# BASE TABLE STYLE (prefix pa-)
# ============================================================================
def _table_css(class_name: str) -> str:
    return f"""
    <style>
    .{class_name} {{
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-family: "Liberation Sans", Arial, sans-serif;
    }}
    .{class_name} table {{
        width: 100%;
        border-collapse: collapse;
        border-spacing: 0;
        font-family: "Liberation Sans", Arial, sans-serif;
        margin: 0;
    }}
    .{class_name} th,
    .{class_name} td {{
        border-left: none !important;
        border-right: none !important;
        border-top: none;
        margin: 0;
    }}
    .{class_name} th {{
        background-color: #f9f9f9;
        text-align: left;
        padding: 6px 12px;
        font-size: 7.5pt;
        color: #666;
        text-transform: uppercase;
        border-bottom: 1px solid #e0e0e0;
        font-weight: 400;
        letter-spacing: 0.04em;
        line-height: 1.1;
    }}
    .{class_name} td {{
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
    .{class_name} tr:first-child td {{
        padding-top: 8px;
    }}
    .{class_name} tr:last-child td {{
        border-bottom: none;
        padding-bottom: 8px;
    }}
    .{class_name} tr:hover td {{
        background: #fafaf8;
    }}
    .pa-color-box {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 3px;
        margin-right: 8px;
        vertical-align: middle;
        position: relative;
        top: -1px;
        flex-shrink: 0;
    }}
    .pa-trend-pill {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 8pt;
        font-weight: 600;
        white-space: nowrap;
        text-align: center;
        min-width: 44px;
    }}
    .pa-status-pill {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 8pt;
        font-weight: 600;
        white-space: nowrap;
        text-align: center;
        min-width: 90px;
    }}
    </style>
    """

# ============================================================================
# BAR CHART HELPER
# ============================================================================
def _plot_top_bar(
    plot_df: pd.DataFrame,
    t: dict,
    value_col: str,
    label_col: str,
    title: str,
    xaxis_title: str,
    value_fmt,
    extra_hover_cols: list = None,
    height_per_bar: int = 30,
    height_min: int = 400,
    bar_color: str = None,
    rounded: bool = False,
    transparent_bg: bool = False,
    font_boost: float = 0,
):
    if plot_df is None or plot_df.empty:
        st.info(t["fr_pano_plot_no_data"])
        return
    df = plot_df.sort_values(value_col, ascending=True).copy()
    if bar_color:
        colors = [bar_color] * len(df)
    elif "winner" in df.columns:
        colors = [_get_candidate_color(w) for w in df["winner"]]
    else:
        colors = [NEUTRAL_COLOR] * len(df)
    texts = [value_fmt(v) for v in df[value_col]]
    hover_cols = [label_col] + (extra_hover_cols or [])
    customdata = df[hover_cols].values
    # NOTE: hover labels are user-facing and hardcoded in Spanish.
    # They should live in translations.py. See TECHNICAL DEBT.
    label_map = {
        "zona": "Región",  # "Region"
        "casted_votes": "Votos totales",  # "Total casted votes"
        "casted_fmt": "Votos totales",  # "Total casted votes"
        "valid_votes": "Votos válidos",  # "Valid votes"
        "valid_fmt": "Votos válidos",  # "Valid votes"
        "null_votes": "Votos nulos",  # "Null votes"
        "null_fmt": "Votos nulos",  # "Null votes"
        "blank_votes": "Votos blancos",  # "Blank votes"
        "blank_fmt": "Votos blancos",  # "Blank votes"
        "null_pct": "% nulos",  # "Null %"
        "null_pct_fmt": "% nulos",  # "Null %"
        "blank_pct": "% blancos",  # "Blank %"
        "blank_pct_fmt": "% blancos",  # "Blank %"
        "region_name": "Región",  # "Region"
        "commune_name": "Comuna",  # "Commune"
    }
    hovertemplate_lines = [f"<b>%{{customdata[0]}}</b>"]
    for i, col in enumerate(extra_hover_cols or [], start=1):
        friendly = label_map.get(col, col)
        if "pct" in col:
            hovertemplate_lines.append(f"{friendly}: %{{customdata[{i}]}}%")
        else:
            hovertemplate_lines.append(f"{friendly}: %{{customdata[{i}]}}")
    hovertemplate = "<br>".join(hovertemplate_lines) + "<extra></extra>"
    marker_kwargs = dict(color=colors, line=dict(color="rgba(0,0,0,0.12)", width=0.5))
    if rounded:
        marker_kwargs["cornerradius"] = 4
        marker_kwargs["line"]["width"] = 0
    fig = go.Figure(
        go.Bar(
            x=df[value_col],
            y=df[label_col],
            orientation="h",
            marker=marker_kwargs,
            text=texts,
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=10 + font_boost, color="#333333", family="Liberation Sans, Arial, sans-serif"),
            hovertemplate=hovertemplate,
            customdata=customdata,
        )
    )
    has_title = bool(title and str(title).strip())
    title_cfg = dict(
        text=title if has_title else "",
        font=dict(size=16 + font_boost, color="#111827", family="Liberation Sans, Arial, sans-serif"),
        x=0, xanchor="left",
    )
    fig.update_layout(
        title=title_cfg,
        xaxis=dict(
            title=dict(text=xaxis_title, font=dict(size=10 + font_boost, color="#6b7280", family="Liberation Sans, Arial, sans-serif")),
            showgrid=True, gridcolor="#e5e7eb",
            tickfont=dict(size=9 + font_boost, color="#6b7280", family="Liberation Sans, Arial, sans-serif"),
            rangemode="tozero"
        ),
        yaxis=dict(
            title="", showgrid=False, automargin=True,
            tickfont=dict(size=10.5 + font_boost, color="#333333", family="Liberation Sans, Arial, sans-serif")
        ),
        showlegend=False,
        margin=dict(l=120, r=110, t=50 if has_title else 10, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)" if transparent_bg else "rgba(255,255,255,1)",
        height=max(height_min, height_per_bar * len(df) + (120 if has_title else 80)),
        font=dict(family="Liberation Sans, Arial, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ============================================================================
# AGGREGATIONS
# ============================================================================
def _null_stats_by_region(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("region_name", as_index=False).agg(
        null_votes=("null_votes", "sum"),
        blank_votes=("blank_votes", "sum"),
        casted_votes=("casted_votes", "sum"),
    )
    agg["valid_votes"] = agg["casted_votes"] - agg["null_votes"] - agg["blank_votes"]
    agg["null_pct"] = (agg["null_votes"] / agg["casted_votes"] * 100).round(2)
    agg = agg.rename(columns={"region_name": "zona"})  # "zona" is an internal alias for "region_name"
    return agg

def _blank_stats_by_region(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("region_name", as_index=False).agg(
        null_votes=("null_votes", "sum"),
        blank_votes=("blank_votes", "sum"),
        casted_votes=("casted_votes", "sum"),
    )
    agg["valid_votes"] = agg["casted_votes"] - agg["null_votes"] - agg["blank_votes"]
    agg["blank_pct"] = (agg["blank_votes"] / agg["casted_votes"] * 100).round(2)
    agg = agg.rename(columns={"region_name": "zona"})  # "zona" is an internal alias for "region_name"
    return agg

def _commune_null_stats(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["commune_name", "region_name", "null_votes", "blank_votes", "casted_votes"]].copy()
    out["valid_votes"] = out["casted_votes"] - out["null_votes"] - out["blank_votes"]
    out["null_pct"] = (out["null_votes"] / out["casted_votes"] * 100).round(2)
    out["winner"] = _compute_winner_sr(df)
    out = out.rename(columns={"commune_name": "zona"})  # "zona" is an internal alias for "commune_name"
    return out

def _commune_blank_stats(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["commune_name", "region_name", "null_votes", "blank_votes", "casted_votes"]].copy()
    out["valid_votes"] = out["casted_votes"] - out["null_votes"] - out["blank_votes"]
    out["blank_pct"] = (out["blank_votes"] / out["casted_votes"] * 100).round(2)
    out["winner"] = _compute_winner_sr(df)
    out = out.rename(columns={"commune_name": "zona"})  # "zona" is an internal alias for "commune_name"
    return out

# ============================================================================
# SECTION NO. 1 — NATIONAL PARTICIPATION
# ============================================================================
def _render_national_participation(df: pd.DataFrame, t: dict):
    total_cast = int(df["casted_votes"].sum())
    total_null = int(df["null_votes"].sum())
    total_blank = int(df["blank_votes"].sum())
    total_valid = total_cast - total_null - total_blank
    pct_null = total_null / total_cast * 100 if total_cast else 0
    pct_blank = total_blank / total_cast * 100 if total_cast else 0
    pct_valid = total_valid / total_cast * 100 if total_cast else 0
    combined_pct = pct_null + pct_blank

    cards_html = _NB_CARD_CSS + f"""
    <div class="nb-cards">
        <div class="nb-card">
            <div class="nb-card-label">{t['sr_pano_kpi_total_emitidos']}</div>
            <div class="nb-card-value">{_fmt_number(total_cast)}</div>
            <div class="nb-card-sub"><b>{t['fr_pano_kpi_nulos_blancos'].format(pct=f"{combined_pct:.2f}")}</b></div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['sr_pano_kpi_validos']}</div>
            <div class="nb-card-value">{_fmt_number(total_valid)}</div>
            <div class="nb-card-sub">{t['fr_pano_kpi_pct_total'].format(pct=f"{pct_valid:.1f}")}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['sr_pano_kpi_nulos']}</div>
            <div class="nb-card-value">{_fmt_number(total_null)}</div>
            <div class="nb-card-sub" style="color:{COLOR_NULOS};">{pct_null:.2f}%</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['sr_pano_kpi_blancos']}</div>
            <div class="nb-card-value">{_fmt_number(total_blank)}</div>
            <div class="nb-card-sub" style="color:{COLOR_BLANCOS};">{pct_blank:.2f}%</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)

# ============================================================================
# SECTION NO. 2 — PARTICIPATION AND VALID VOTE: 1V vs 2V
# ============================================================================
def _trend_label(v1, v2):
    if v2 > v1:
        return "sube"  # "up"
    if v2 < v1:
        return "baja"  # "down"
    return "igual"  # "flat"

def _render_participation_comparison(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict):
    def _stats(df):
        casted = int(df["casted_votes"].sum())
        blank = int(df["blank_votes"].sum())
        null = int(df["null_votes"].sum())
        valid = casted - blank - null
        return {"casted": casted, "valid": valid, "blank": blank, "null": null}
    fr = _stats(df_fr)
    sr = _stats(df_sr)
    def _pct(n, base):
        return (n / base * 100) if base else 0
    rows = [
        (t["casted_votes"], fr["casted"], sr["casted"], fr["casted"], sr["casted"]),
        (t["valid_votes"], fr["valid"], sr["valid"], fr["casted"], sr["casted"]),
        (t["blank_votes"], fr["blank"], sr["blank"], fr["casted"], sr["casted"]),
        (t["null_votes"], fr["null"], sr["null"], fr["casted"], sr["casted"]),
    ]
    rows_html = ""
    for label, v1, v2, b1, b2 in rows:
        diff_abs = v2 - v1
        diff_pct = (diff_abs / v1 * 100) if v1 else 0
        sign_abs = "+" if diff_abs > 0 else ""
        sign_pct = "+" if diff_pct > 0 else ""
        if label == t["casted_votes"]:
            rel_1 = ""
            rel_2 = ""
        else:
            rel_1 = f" ({_pct(v1, b1):.2f}%)"
            rel_2 = f" ({_pct(v2, b2):.2f}%)"
        trend = _trend_label(v1, v2)
        trend_pill = _trend_pill(trend, t)
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{label}</td>'
            f'<td style="text-align:right; color:#333;">{_fmt_number(v1)}<span style="color:#9a9a9a; font-size:9pt;">{rel_1}</span></td>'
            f'<td style="text-align:right; color:#333; font-weight:700;">{_fmt_number(v2)}<span style="color:#9a9a9a; font-size:9pt; font-weight:400;">{rel_2}</span></td>'
            f'<td style="text-align:right; color:#333;">{sign_abs}{_fmt_number(abs(diff_abs))}</td>'
            f'<td style="text-align:right; color:#333;">{sign_pct}{diff_pct:.2f}%</td>'
            f'<td>{trend_pill}</td>'
            f"</tr>"
        )
    # NOTE: Table headers are user-facing and hardcoded in Spanish.
    # They should live in translations.py. See TECHNICAL DEBT.
    html = _table_css("pa-tabla-participacion") + f"""
    <div class="pa-tabla-participacion" style="max-width:900px;">
        <table>
            <thead>
                <tr>
                    <th>Indicador</th>  <!-- "Indicator" -->
                    <th style="text-align:right;">1ª Vuelta</th>  <!-- "1st Round" -->
                    <th style="text-align:right;">2ª Vuelta</th>  <!-- "2nd Round" -->
                    <th style="text-align:right;">Δ Absoluto</th>  <!-- "Δ Absolute" -->
                    <th style="text-align:right;">Δ %</th>
                    <th>Tendencia</th>  <!-- "Trend" -->
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

# ============================================================================
# SECTION NO. 3 — NULL VOTE ANALYSIS (with selector)
# ============================================================================
def _render_top_null_regions(df: pd.DataFrame, t: dict, top_n: int = 16):
    regions = _null_stats_by_region(df)
    regions = regions.nlargest(top_n, "null_votes").copy()
    regions["winner"] = "No data"
    regions["casted_fmt"] = regions["casted_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    regions["valid_fmt"] = regions["valid_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    regions["null_fmt"] = regions["null_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    _plot_top_bar(
        plot_df=regions,
        t=t,
        value_col="null_votes",
        label_col="zona",
        title="",
        xaxis_title=t["fr_pano_plot_x_nulos"],
        value_fmt=_fmt_number,
        extra_hover_cols=["casted_fmt", "valid_fmt", "null_fmt", "null_pct"],
        height_per_bar=32,
        bar_color=COLOR_NULOS,
        rounded=True,
        transparent_bg=True,
        font_boost=1.5,
    )


def _render_special_votes_by_region(df_fr, df_sr, vote_type: str, t: dict):
    col = f"{vote_type}_votes"
    label = t["sr_pano_th_nulos"] if vote_type == "null" else t["sr_pano_th_blancos"]

    fr = df_fr.groupby("region_name", as_index=False).agg(
        v1=(col, "sum"),
        casted_1=("casted_votes", "sum"),
    )
    sr = df_sr.groupby("region_name", as_index=False).agg(
        v2=(col, "sum"),
        casted_2=("casted_votes", "sum"),
    )
    merged = fr.merge(sr, on="region_name", how="inner")
    merged["v1"] = merged["v1"].astype(int)
    merged["v2"] = merged["v2"].astype(int)
    merged["diff"] = merged["v2"] - merged["v1"]
    merged["pct_1"] = (merged["v1"] / merged["casted_1"].replace(0, 1) * 100).round(2)
    merged["pct_2"] = (merged["v2"] / merged["casted_2"].replace(0, 1) * 100).round(2)
    merged["pp_change"] = (merged["pct_2"] - merged["pct_1"]).round(2)
    merged["trend"] = merged.apply(lambda r: _trend_label(r["v1"], r["v2"]), axis=1)
    merged = merged.sort_values("diff", ascending=False).reset_index(drop=True)

    rows_html = ""
    for _, r in merged.iterrows():
        region = str(r["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        v1 = _fmt_number(r["v1"])
        v2 = _fmt_number(r["v2"])
        diff = int(r["diff"])
        sign_diff = "+" if diff > 0 else ""
        diff_txt = f"{sign_diff}{_fmt_number(abs(diff))}"
        pct_1 = f"{r['pct_1']:.2f}%"
        pct_2 = f"{r['pct_2']:.2f}%"
        pp = float(r["pp_change"])
        sign_pp = "+" if pp > 0 else ""
        pp_txt = f"{sign_pp}{pp:.2f} pp"
        trend_html = _trend_pill(r["trend"], t)

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{v1}</td>'
            f'<td style="text-align:right; color:#666;">{v2}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{diff_txt}</td>'
            f'<td style="text-align:right; color:#666;">{pct_1}</td>'
            f'<td style="text-align:right; color:#666;">{pct_2}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{pp_txt}</td>'
            f'<td>{trend_html}</td>'
            f"</tr>"
        )

    html = _table_css(f"pa-tabla-{vote_type}-region-comp") + f"""
    <div class="pa-tabla-{vote_type}-region-comp">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_region']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_votos_1v'].format(label=label)}</th>
                    <th style="text-align:right;">{t['sr_pano_th_votos_2v'].format(label=label)}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_votos']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_1v']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_2v']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_pp']}</th>
                    <th>{t['sr_pano_th_tendencia']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()


def _render_special_votes_top_communes(df_fr, df_sr, vote_type: str, top_n: int = 10, t: dict = None):
    col = f"{vote_type}_votes"
    label = t["sr_pano_th_nulos"] if vote_type == "null" else t["sr_pano_th_blancos"]

    df_fr_work = df_fr.copy()
    df_fr_work["__winner_fr"] = _compute_winner_fr(df_fr_work)
    fr = df_fr_work[[
        "commune_id", "commune_name", "region_name",
        col, "casted_votes", "__winner_fr",
    ]].rename(columns={col: "v1", "casted_votes": "casted_1"})
    sr = df_sr[["commune_id", col, "casted_votes"]].rename(columns={col: "v2", "casted_votes": "casted_2"})
    merged = fr.merge(sr, on="commune_id", how="inner")
    merged["v1"] = merged["v1"].astype(int)
    merged["v2"] = merged["v2"].astype(int)
    merged["diff"] = merged["v2"] - merged["v1"]
    merged["pct_1"] = (merged["v1"] / merged["casted_1"].replace(0, 1) * 100).round(2)
    merged["pct_2"] = (merged["v2"] / merged["casted_2"].replace(0, 1) * 100).round(2)
    merged["pp_change"] = (merged["pct_2"] - merged["pct_1"]).round(2)
    top = merged.nlargest(top_n, "diff").reset_index(drop=True)

    rows_html = ""
    for _, r in top.iterrows():
        commune = str(r["commune_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        v1 = _fmt_number(r["v1"])
        v2 = _fmt_number(r["v2"])
        diff = int(r["diff"])
        sign = "+" if diff > 0 else ""
        diff_txt = f"{sign}{_fmt_number(abs(diff))}"
        pct_1 = f"{r['pct_1']:.2f}%"
        pct_2 = f"{r['pct_2']:.2f}%"
        pp = float(r["pp_change"])
        sign_pp = "+" if pp > 0 else ""
        pp_txt = f"{sign_pp}{pp:.2f} pp"
        winner_cell = _candidate_cell(str(r["__winner_fr"]))

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{v1}</td>'
            f'<td style="text-align:right; color:#666;">{v2}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{diff_txt}</td>'
            f'<td style="text-align:right; color:#666;">{pct_1}</td>'
            f'<td style="text-align:right; color:#666;">{pct_2}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{pp_txt}</td>'
            f"<td>{winner_cell}</td>"
            f"</tr>"
        )

    html = _table_css(f"pa-tabla-{vote_type}-top-comunas") + f"""
    <div class="pa-tabla-{vote_type}-top-comunas">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_comuna']}</th>
                    <th>{t['sr_pano_th_region']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_votos_1v'].format(label=label)}</th>
                    <th style="text-align:right;">{t['sr_pano_th_votos_2v'].format(label=label)}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_votos']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_1v']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_2v']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_pp']}</th>
                    <th>{t['sr_pano_th_ganador_1v']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()


def _render_null_section(df: pd.DataFrame, df_fr: pd.DataFrame, t: dict):
    view = st.radio(
        t["sr_pano_radio_label"],
        [t["sr_pano_radio_nulos_v2"], t["sr_pano_radio_nulos_comp"]],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="panorama_sr_nulos_view",
    )
    if view == t["sr_pano_radio_nulos_v2"]:
        render_section_title(t["fr_pano_section_reg_nulos_abs"])
        _render_top_null_regions(df, t, top_n=16)
        st.divider()
        communes = _commune_null_stats(df)
        communes = communes[communes["casted_votes"] >= MIN_CASTED_VOTES].copy()
        render_section_title(t["fr_pano_section_com_nulos_abs"])
        _render_communes_table(communes, value_col="null_votes", pct_col="null_pct", mode="abs", t=t)
        render_section_title(t["fr_pano_section_com_nulos_rel"])
        _render_communes_table(communes, value_col="null_votes", pct_col="null_pct", mode="rel", t=t)
    else:
        render_section_title(t["sr_pano_section_nulos_comp"])
        _render_special_votes_by_region(df_fr, df, vote_type="null", t=t)
        render_section_title(t["sr_pano_section_nulos_top"])
        _render_special_votes_top_communes(df_fr, df, vote_type="null", top_n=10, t=t)

# ============================================================================
# SECTION NO. 4 — BLANK VOTE ANALYSIS (with selector)
# ============================================================================
def _render_top_blank_regions(df: pd.DataFrame, t: dict, top_n: int = 16):
    regions = _blank_stats_by_region(df)
    regions = regions.nlargest(top_n, "blank_votes").copy()
    regions["winner"] = "No data"
    regions["casted_fmt"] = regions["casted_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    regions["valid_fmt"] = regions["valid_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    regions["blank_fmt"] = regions["blank_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    _plot_top_bar(
        plot_df=regions,
        t=t,
        value_col="blank_votes",
        label_col="zona",
        title="",
        xaxis_title=t["fr_pano_plot_x_blancos"],
        value_fmt=_fmt_number,
        extra_hover_cols=["casted_fmt", "valid_fmt", "blank_fmt", "blank_pct"],
        height_per_bar=32,
        bar_color=COLOR_BLANCOS,
        rounded=True,
        transparent_bg=True,
        font_boost=1.5,
    )


def _render_blank_section(df: pd.DataFrame, df_fr: pd.DataFrame, t: dict):
    view = st.radio(
        t["sr_pano_radio_label"],
        [t["sr_pano_radio_blancos_v2"], t["sr_pano_radio_blancos_comp"]],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="panorama_sr_blancos_view",
    )
    if view == t["sr_pano_radio_blancos_v2"]:
        render_section_title(t["fr_pano_section_reg_blancos_abs"])
        _render_top_blank_regions(df, t, top_n=16)
        st.divider()
        communes = _commune_blank_stats(df)
        communes = communes[communes["casted_votes"] >= MIN_CASTED_VOTES].copy()
        render_section_title(t["fr_pano_section_com_blancos_abs"])
        _render_communes_table(communes, value_col="blank_votes", pct_col="blank_pct", mode="abs", t=t)
        render_section_title(t["fr_pano_section_com_blancos_rel"])
        _render_communes_table(communes, value_col="blank_votes", pct_col="blank_pct", mode="rel", t=t)
    else:
        render_section_title(t["sr_pano_section_blancos_comp"])
        _render_special_votes_by_region(df_fr, df, vote_type="blank", t=t)
        render_section_title(t["sr_pano_section_blancos_top"])
        _render_special_votes_top_communes(df_fr, df, vote_type="blank", top_n=10, t=t)

# ============================================================================
# GENERIC COMMUNES TABLE
# ============================================================================
def _render_communes_table(
    communes_df: pd.DataFrame,
    value_col: str,
    pct_col: str,
    mode: str,
    t: dict,
    top_n: int = 10,
):
    if mode == "abs":
        sub_df = communes_df.nlargest(top_n, value_col).copy().reset_index(drop=True)
    else:
        sub_df = communes_df.nlargest(top_n, pct_col).copy().reset_index(drop=True)
    rows_html = ""
    for i, row in sub_df.iterrows():
        rank = i + 1
        commune = str(row["zona"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(row.get("region_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        value_abs = _fmt_number(row[value_col])
        value_pct = f"{row[pct_col]:.2f}%"
        winner_full = row.get("winner", "No data")
        if mode == "abs":
            abs_style = "font-weight:700; color:#111827;"
            pct_style = "color:#666;"
        else:
            abs_style = "color:#666;"
            pct_style = "font-weight:700; color:#111827;"
        candidate_cell = _candidate_cell(winner_full)
        rows_html += (
            f"<tr>"
            f"<td style=\"color:#9a9a9a; text-align:center;\">{rank}</td>"
            f"<td style=\"font-weight:400; color:#333333;\">{commune}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{region}</td>"
            f"<td style=\"text-align:right; {abs_style}\">{value_abs}</td>"
            f"<td style=\"text-align:right; {pct_style}\">{value_pct}</td>"
            f"<td>{candidate_cell}</td>"
            f"</tr>"
        )
    html = _table_css("pa-tabla-comunas") + f"""
    <div class="pa-tabla-comunas" style="max-width:720px;">
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>{t['fr_pano_th_comuna']}</th>
                    <th>{t['fr_pano_th_region']}</th>
                    <th style="text-align:right;">{value_col.split("_")[0].upper()}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th>{t['fr_pano_th_ganador']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

# ============================================================================
# SECTION NO. 5 — NATIONAL RESULTS
# ============================================================================
def _render_national_results(df: pd.DataFrame, t: dict):
    total_cast = int(df["casted_votes"].sum())
    total_blank = int(df["blank_votes"].sum())
    total_null = int(df["null_votes"].sum())
    total_valid = total_cast - total_blank - total_null
    jara_total = int(df["jara_votes"].sum())
    kast_total = int(df["kast_votes"].sum())
    jara_pct = (jara_total / total_valid * 100) if total_valid else 0
    kast_pct = (kast_total / total_valid * 100) if total_valid else 0
    margin_pct = abs(jara_pct - kast_pct)
    margin_votes = abs(jara_total - kast_total)

    pill_electo = (
        f'<span class="pa-status-pill" '
        f'style="background:{_hex_to_rgba_string(KAST_COLOR, 0.12)}; color:{KAST_COLOR};">{t["sr_pano_result_electo"]}</span>'
    )
    pill_segundo = (
        f'<span class="pa-status-pill" '
        f'style="background:{COLOR_NEUTRAL_INDICATOR}; color:#6b7280;">{t["sr_pano_result_segundo"]}</span>'
    )

    rows_html = (
        f"<tr>"
        f'<td>{_candidate_cell("José Antonio Kast")}</td>'
        f'<td style="text-align:right; font-weight:700; color:{KAST_COLOR};">{kast_pct:.2f}%</td>'
        f'<td style="text-align:right; color:#666;">{_fmt_number(kast_total)}</td>'
        f'<td>{pill_electo}</td>'
        f"</tr>"
        f"<tr>"
        f'<td>{_candidate_cell("Jeannette Jara")}</td>'
        f'<td style="text-align:right; color:#666;">{jara_pct:.2f}%</td>'
        f'<td style="text-align:right; color:#666;">{_fmt_number(jara_total)}</td>'
        f'<td>{pill_segundo}</td>'
        f"</tr>"
        f"<tr>"
        f'<td style="font-weight:400; color:#333; border-top:1px solid #e0e0e0 !important;">{t["sr_pano_result_margen"]}</td>'
        f'<td style="text-align:right; font-weight:700; color:{KAST_COLOR}; border-top:1px solid #e0e0e0 !important;">{margin_pct:.2f}%</td>'
        f'<td style="text-align:right; font-weight:700; color:{KAST_COLOR}; border-top:1px solid #e0e0e0 !important;">{_fmt_number(margin_votes)}</td>'
        f'<td style="border-top:1px solid #e0e0e0 !important;"></td>'
        f"</tr>"
    )
    html = _table_css("pa-tabla-resultados-nacionales") + f"""
    <div class="pa-tabla-resultados-nacionales" style="max-width:820px;">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_pano_th_candidato']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_validos']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_votos']}</th>
                    <th>{t['sr_pano_th_estado']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

# ============================================================================
# SECTION NO. 6 — COMMUNES WON
# ============================================================================
def _render_communes_won(df: pd.DataFrame, t: dict):
    df_work = df.copy()
    df_work["_winner"] = _compute_winner_sr(df_work)
    counts = df_work["_winner"].value_counts().reset_index()
    counts.columns = ["candidate", "communes"]
    total = int(counts["communes"].sum())
    counts["pct"] = (counts["communes"] / total * 100).round(2) if total else 0
    counts = counts.sort_values("communes", ascending=False).reset_index(drop=True)
    rows_html = ""
    for _, row in counts.iterrows():
        candidate_cell = _candidate_cell(row["candidate"])
        communes = int(row["communes"])
        pct = f"{row['pct']:.2f}%"
        rows_html += (
            f"<tr>"
            f"<td>{candidate_cell}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{communes}</td>"
            f"<td style=\"text-align:right; color:#666;\">{pct}</td>"
            f"</tr>"
        )
    html = _table_css("pa-tabla-ganadas") + f"""
    <div class="pa-tabla-ganadas" style="max-width:720px;">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_pano_th_candidato']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_comunas']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_pct_del_total']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    order_cand = {c: i for i, c in enumerate(counts["candidate"].tolist())}
    df_work["_order_cand"] = df_work["_winner"].map(order_cand)
    sort_cols = ["_order_cand"]
    if "region_order" in df_work.columns:
        sort_cols.append("region_order")
    if "commune_name" in df_work.columns:
        sort_cols.append("commune_name")
    df_sorted = df_work.sort_values(sort_cols).reset_index(drop=True)
    cells_html = ""
    for _, row in df_sorted.iterrows():
        cand = str(row["_winner"])
        commune = str(row.get("commune_name", "")).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(row.get("region_name", "")).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        color = _get_candidate_color(cand)
        tip = f"{cand} · {commune} ({region})"
        cells_html += f'<div class="waffle-cell" style="background:{color};" title="{tip}"></div>'
    html_waffle = _WAFFLE_CSS + f"""
    <div class="waffle-wrap">
        <div class="waffle-title">{t['fr_pano_waffle_title'].format(n=total)}</div>
        <div class="waffle-grid">
            {cells_html}
        </div>
    </div>
    """
    st.markdown(_clean_html(html_waffle), unsafe_allow_html=True)

# ============================================================================
# SECTION NO. 6 (part 2) - WINNERS BY MACROZONE
# ============================================================================
def _render_winners_by_macrozone(df: pd.DataFrame, t: dict):
    if "macrozone" not in df.columns or "macrozone_order" not in df.columns:
        st.info(t["fr_pano_no_data_macrozone"])
        return
    pct_cols = ["jara_pct", "kast_pct", "parisi_pct", "kaiser_pct", "matthei_pct"]
    pct_cols = [c for c in pct_cols if c in df.columns]
    if not pct_cols:
        st.info(t["fr_pano_no_cand_cols"])
        return
    name_map = {
        "jara_pct": "Jeannette Jara",
        "kast_pct": "José Antonio Kast",
        "parisi_pct": "Franco Parisi",
        "kaiser_pct": "Johannes Kaiser",
        "matthei_pct": "Evelyn Matthei",
    }
    df_work = df.copy()
    df_work["_winner"] = df_work[pct_cols].idxmax(axis=1).map(name_map)
    pivot = pd.crosstab(df_work["_winner"], df_work["macrozone"])
    macro_order = (
        df_work[["macrozone", "macrozone_order"]]
        .dropna()
        .drop_duplicates()
        .sort_values("macrozone_order")["macrozone"]
        .tolist()
    )
    macro_order = [m for m in macro_order if m in pivot.columns]
    others = [c for c in pivot.columns if c not in macro_order]
    macro_order = macro_order + others
    pivot["_total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("_total", ascending=False).drop(columns="_total")
    pivot = pivot[macro_order]
    header_cols = "".join(
        f"<th style='text-align:center;'>{str(m).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</th>"
        for m in pivot.columns
    )
    header_cols += f"<th style='text-align:center;'>{t['fr_pano_th_total']}</th>"
    rows_html = ""
    for cand, row in pivot.iterrows():
        candidate_cell = _candidate_cell(cand)
        total = int(row.sum())
        cells = ""
        for m in pivot.columns:
            val = int(row[m])
            if val == 0:
                cells += f"<td style='text-align:center; color: {COLOR_NEUTRAL_INDICATOR};'>·</td>"
            else:
                cells += f"<td style='text-align:center; color:#333;'>{val}</td>"
        cells += f"<td style='text-align:center; font-weight:700; color:#111827; border-left:1px solid #e0e0e0 !important;'>{total}</td>"
        rows_html += (
            f"<tr>"
            f"<td>{candidate_cell}</td>"
            f"{cells}"
            f"</tr>"
        )
    totals = pivot.sum(axis=0)
    total_general = int(totals.sum())
    total_cells = "".join(
        f"<td style='text-align:center; font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important;'>{int(totals[m])}</td>"
        for m in pivot.columns
    )
    total_cells += f"<td style='text-align:center; font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important; border-left:1px solid #e0e0e0 !important;'>{total_general}</td>"
    rows_html += (
        f"<tr>"
        f"<td style='font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important;'>{t['fr_pano_th_total']}</td>"
        f"{total_cells}"
        f"</tr>"
    )
    html = _table_css("pa-tabla-macro") + f"""
    <div class="pa-tabla-macro">
        <table>
            <thead>
                <tr>
                    <th>{t["fr_pano_th_candidato"]}</th>
                    {header_cols}
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

# ============================================================================
# SECTION NO. 7 - REGIONAL WINNERS
# ============================================================================
def _render_regional_winners(df: pd.DataFrame, t: dict):
    if "region_name" not in df.columns:
        st.info(t["sr_pano_no_data_region"])
        return
    agg_cols = {"jara_votes": "sum", "kast_votes": "sum"}
    agg_cols = {k: v for k, v in agg_cols.items() if k in df.columns}
    if len(agg_cols) < 2:
        st.info(t["sr_pano_no_data_regionales"])
        return
    region_metrics = df.groupby("region_name", as_index=False).agg(agg_cols).copy()
    region_metrics["_valid"] = region_metrics["jara_votes"] + region_metrics["kast_votes"]
    region_metrics["jara_pct"] = (region_metrics["jara_votes"] / region_metrics["_valid"].replace(0, 1) * 100).round(2)
    region_metrics["kast_pct"] = (region_metrics["kast_votes"] / region_metrics["_valid"].replace(0, 1) * 100).round(2)
    if "region_order" in df.columns:
        order_map = (
            df[["region_name", "region_order"]]
            .dropna().drop_duplicates()
            .set_index("region_name")["region_order"].to_dict()
        )
        region_metrics["_order"] = region_metrics["region_name"].map(order_map).fillna(9999)
        region_metrics = region_metrics.sort_values("_order").drop(columns="_order")
    else:
        region_metrics = region_metrics.sort_values("region_name")
    region_metrics = region_metrics.reset_index(drop=True)
    rows_html = ""
    for _, row in region_metrics.iterrows():
        region = str(row["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        jara_pct = float(row["jara_pct"])
        kast_pct = float(row["kast_pct"])
        if kast_pct > jara_pct:
            winner = "José Antonio Kast"
            winner_pct = kast_pct
            loser_pct = jara_pct
        else:
            winner = "Jeannette Jara"
            winner_pct = jara_pct
            loser_pct = kast_pct
        margin = winner_pct - loser_pct
        w_color = _get_candidate_color(winner)
        bar_width = min(100, margin * 3)
        margin_color = KAST_COLOR if winner == "José Antonio Kast" else JARA_COLOR

        rows_html += (
            f"<tr>"
            f"<td style=\"color:#333;\">{region}</td>"
            f"<td>{_candidate_cell(winner)}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{winner_pct:.2f}%</td>"
            f"<td>{_candidate_cell('Jeannette Jara' if winner == 'José Antonio Kast' else 'José Antonio Kast')}</td>"
            f"<td style=\"text-align:right; color:#666;\">{loser_pct:.2f}%</td>"
            f"<td style=\"text-align:right; color:{margin_color};\">{margin:.2f} pp</td>"
            f"<td style=\"width:140px;\"><div style=\"background:#f0f0f0; border-radius:3px; height:8px; width:100%;\"><div style=\"background:{w_color}; height:8px; width: {bar_width}%; border-radius:3px;\"></div></div></td>"
            f"</tr>"
        )
    html = _table_css("pa-tabla-regional") + f"""
    <div class="pa-tabla-regional">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_pano_th_region']}</th>
                    <th>{t['fr_pano_th_ganador']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th>{t['fr_pano_th_segundo']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_brecha']}</th>
                    <th>{t['fr_pano_th_intensidad']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

# ============================================================================
# SECTION NO. 8 - VOTE IN REGIONAL CAPITALS
# ============================================================================
def _render_regional_capitals(df: pd.DataFrame, t: dict):
    if "commune_name" not in df.columns or "region_name" not in df.columns:
        st.info(t["sr_pano_no_data_capitales"])
        return
    cap_norm_map = {_norm_commune(c): c for c in REGIONAL_CAPITALS}
    df_work = df.copy()
    df_work["_commune_norm"] = df_work["commune_name"].apply(_norm_commune)
    capitals_df = df_work[df_work["_commune_norm"].isin(cap_norm_map.keys())].copy()
    capitals_df["_capital_display"] = capitals_df["_commune_norm"].map(cap_norm_map)
    if capitals_df.empty:
        st.info(t["sr_pano_no_capitales_found"])
        return
    if "region_order" in capitals_df.columns:
        capitals_df = capitals_df.sort_values(["region_order", "_capital_display"])
    else:
        capitals_df = capitals_df.sort_values("_capital_display")
    capitals_df = capitals_df.reset_index(drop=True)
    rows_html = ""
    for _, row in capitals_df.iterrows():
        capital = str(row["_capital_display"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(row.get("region_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        jara_pct = float(row["jara_pct"]) if "jara_pct" in row and pd.notna(row["jara_pct"]) else 0
        kast_pct = float(row["kast_pct"]) if "kast_pct" in row and pd.notna(row["kast_pct"]) else 0
        if jara_pct == 0 and kast_pct == 0:
            valid = float(row.get("jara_votes", 0) + row.get("kast_votes", 0))
            if valid > 0:
                jara_pct = float(row["jara_votes"]) / valid * 100
                kast_pct = float(row["kast_votes"]) / valid * 100
        if kast_pct > jara_pct:
            winner = "José Antonio Kast"
            winner_pct = kast_pct
            loser_pct = jara_pct
        else:
            winner = "Jeannette Jara"
            winner_pct = jara_pct
            loser_pct = kast_pct
        margin = winner_pct - loser_pct
        w_color = _get_candidate_color(winner)
        bar_width = min(100, margin * 3)
        margin_color = KAST_COLOR if winner == "José Antonio Kast" else JARA_COLOR

        rows_html += (
            f"<tr>"
            f"<td style=\"font-weight:400; color:#333333;\">{capital}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{region}</td>"
            f"<td>{_candidate_cell(winner)}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{winner_pct:.2f}%</td>"
            f"<td>{_candidate_cell('Jeannette Jara' if winner == 'José Antonio Kast' else 'José Antonio Kast')}</td>"
            f"<td style=\"text-align:right; color:#666;\">{loser_pct:.2f}%</td>"
            f"<td style=\"text-align:right; color:{margin_color};\">{margin:.2f} pp</td>"
            f"<td style=\"width:120px;\"><div style=\"background:#f0f0f0; border-radius:3px; height:8px; width:100%;\"><div style=\"background:{w_color}; height:8px; width: {bar_width}%; border-radius:3px;\"></div></div></td>"
            f"</tr>"
        )
    html = _table_css("pa-tabla-capitales") + f"""
    <div class="pa-tabla-capitales">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_pano_th_capital']}</th>
                    <th>{t['fr_pano_th_region']}</th>
                    <th>{t['fr_pano_th_ganador']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th>{t['fr_pano_th_segundo']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_brecha']}</th>
                    <th>{t['fr_pano_th_intensidad']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

# ============================================================================
# SECTION NO. 9 - VOTE BY COMMUNE SIZE
# ============================================================================
def _render_vote_by_commune_size(df: pd.DataFrame, t: dict):
    if "population" not in df.columns:
        st.info(t["fr_pano_no_population"])
        return
    df_work = df.copy()
    df_work["population"] = pd.to_numeric(df_work["population"], errors="coerce")
    df_work = df_work.dropna(subset=["population"])
    total_pop_national = df_work["population"].sum()
    blocks_html = ""
    for bracket in POPULATION_BRACKETS:
        mask = pd.Series(True, index=df_work.index)
        if bracket["min"] is not None:
            mask &= df_work["population"] >= bracket["min"]
        if bracket["max"] is not None:
            mask &= df_work["population"] <= bracket["max"]
        sub = df_work[mask].copy()
        if sub.empty:
            continue
        jara_v = int(sub["jara_votes"].sum())
        kast_v = int(sub["kast_votes"].sum())
        validos = jara_v + kast_v
        if validos <= 0:
            continue
        p_jara = jara_v / validos * 100
        p_kast = kast_v / validos * 100
        segments = [
            {"name": "Jeannette Jara", "pct": p_jara, "color": _get_candidate_color("Jeannette Jara")},
            {"name": "José Antonio Kast", "pct": p_kast, "color": _get_candidate_color("José Antonio Kast")},
        ]
        n_communes = len(sub)
        pct_pop = sub["population"].sum() / total_pop_national * 100 if total_pop_national else 0
        bar = ""
        for idx, s in enumerate(segments):
            is_first = idx == 0
            is_last = idx == len(segments) - 1
            classes = "tramo-seg"
            if is_first:
                classes += " tramo-seg-first"
            if is_last:
                classes += " tramo-seg-last"
            label = f"{s['pct']:.1f}%" if s["pct"] >= 5 else ""
            bar += (
                f"<div class=\"{classes}\" style=\"width:{s['pct']}%; background:{s['color']};\" "
                f"title=\"{s['name']}: {s['pct']:.2f}%\">{label}</div>"
            )
        blocks_html += f"""
        <div class="tramo-wrap">
            <div class="tramo-header">
                <div class="tramo-label">{bracket['label']} <span>{bracket['sub']}</span></div>
                <div class="tramo-meta">{t['sr_pano_th_comunas']} · {pct_pop:.1f}%</div>
            </div>
            <div class="tramo-bar-wrap">
                <div class="tramo-midline"></div>
                <div class="tramo-bar">{bar}</div>
            </div>
        </div>
        """
    legend_items = ""
    for cand in SR_CANDIDATES:
        color = _get_candidate_color(cand["name"])
        legend_items += (
            f"<div class=\"legend-item\">"
            f"<span class=\"legend-dot\" style=\"background:{color};\"></span>"
            f"{cand['name']}"
            f"</div>"
        )
    html = _TRAMOS_CSS + f"""
    <div class="tramos-wrap">
        {blocks_html}
        <div class="tramos-leyendas">
            {legend_items}
        </div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)

# ============================================================================
# SECTION NO. 10 — ELECTORAL REALIGNMENT
# ============================================================================
def _compute_transitions(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> pd.DataFrame:
    fr = df_fr.copy()
    fr_cols = [c for c in VOTE_COLS_FR if c in fr.columns]
    fr["__winner_key_1v"] = fr[fr_cols].idxmax(axis=1).str.replace("_votes", "", regex=False)
    fr["winner_1v"] = fr["__winner_key_1v"].map(WINNER_LABELS_1V_IDEOLOGY).fillna(t["sr_pano_winner_sin_dato"])
    sr = df_sr.copy()
    sr["__winner_key_2v"] = sr.apply(
        lambda r: "kast" if r["kast_votes"] > r["jara_votes"] else "jara", axis=1
    )
    sr["winner_2v"] = sr["__winner_key_2v"].map(WINNER_LABELS_2V_IDEOLOGY).fillna(t["sr_pano_winner_sin_dato"])
    merged = fr[["commune_id", "commune_name", "region_name", "winner_1v"]].merge(
        sr[["commune_id", "winner_2v"]],
        on="commune_id",
        how="inner",
    )
    merged["change_type"] = merged.apply(
        lambda r: t["sr_hist_change_same"] if r["winner_1v"] == r["winner_2v"] else t["sr_hist_change_changed"], axis=1
    )
    return merged

def _render_electoral_realignment(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict):
    df_change = _compute_transitions(df_fr, df_sr, t)
    total = len(df_change)
    if total == 0:
        st.info(t["sr_pano_no_transiciones"])
        return
    same_key = t["sr_hist_change_same"]
    changed_key = t["sr_hist_change_changed"]
    n_same = int((df_change["change_type"] == same_key).sum())
    n_changed = int((df_change["change_type"] == changed_key).sum())
    pct_same = n_same / total * 100 if total else 0
    pct_changed = n_changed / total * 100 if total else 0
    cards_html = _NB_CARD_CSS + f"""
    <div class="nb-cards">
        <div class="nb-card">
            <div class="nb-card-label">{t['sr_pano_card_total_comunas']}</div>
            <div class="nb-card-value">{total}</div>
            <div class="nb-card-sub">{t['sr_pano_card_universo']}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['sr_pano_card_mantuvo']}</div>
            <div class="nb-card-value">{n_same}</div>
            <div class="nb-card-sub">{t['sr_hist_kpi_pct_total'].format(pct=f"{pct_same:.1f}")}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['sr_pano_card_cambio']}</div>
            <div class="nb-card-value">{n_changed}</div>
            <div class="nb-card-sub">{t['sr_hist_kpi_pct_total'].format(pct=f"{pct_changed:.1f}")}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)
    render_section_title(t["sr_pano_section_matriz"])
    render_section_subtitle(t["sr_pano_sub_matriz"])
    rows_order = df_change["winner_1v"].value_counts().index.tolist()
    cols_order = ["Jara (izquierda)", "Kast (derecha)"]
    matrix = pd.crosstab(df_change["winner_1v"], df_change["winner_2v"])
    matrix = matrix.reindex(index=rows_order, columns=cols_order, fill_value=0).astype(int)
    col_colors = {
        "Jara (izquierda)": _get_candidate_color("Jeannette Jara"),
        "Kast (derecha)": _get_candidate_color("José Antonio Kast"),
    }
    max_val = int(matrix.values.max()) if matrix.size else 1
    if max_val == 0:
        max_val = 1
    header_html = f"<th>{t['sr_pano_th_matriz_label']}</th>"
    for col in cols_order:
        header_html += f"<th style='text-align:center;'>{col}</th>"
    header_html += f"<th style='text-align:center;'>{t['sr_pano_th_total']}</th>"
    rows_html = ""
    for row_label in matrix.index:
        row_total = int(matrix.loc[row_label].sum())
        rows_html += f'<tr><td style="font-weight:600; color:#111827;">{row_label}</td>'
        for col in matrix.columns:
            val = int(matrix.loc[row_label, col])
            if val == 0:
                rows_html += f'<td style="text-align:center; color: {COLOR_NEUTRAL_INDICATOR};">·</td>'
            else:
                hexc = col_colors.get(col, NEUTRAL_COLOR).lstrip("#")
                r = int(hexc[0:2], 16)
                g = int(hexc[2:4], 16)
                b = int(hexc[4:6], 16)
                alpha = 0.15 + 0.55 * (val / max_val)
                bg = f"rgba({r},{g},{b},{alpha:.2f})"
                text_color = "white" if alpha >= 0.5 else "#111827"
                rows_html += (
                    f'<td style="text-align:center; background:{bg}; '
                    f'color:{text_color};">{val}</td>'
                )
        rows_html += f'<td style="text-align:center; font-weight:700; color:#111827;">{row_total}</td></tr>'
    col_totals = matrix.sum(axis=0)
    grand_total = int(col_totals.sum())
    total_row = f'<tr><td style="font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important;">{t["sr_pano_th_total"]}</td>'
    for col in matrix.columns:
        total_row += (
            f'<td style="text-align:center; font-weight:700; color:#111827; '
            f'border-top:1px solid #e0e0e0 !important;">{int(col_totals[col])}</td>'
        )
    total_row += (
        f'<td style="text-align:center; font-weight:700; color:#111827; '
        f'border-top:1px solid #e0e0e0 !important;">{grand_total}</td></tr>'
    )
    html_matrix = _table_css("pa-tabla-transiciones") + f"""
    <div class="pa-tabla-transiciones" style="max-width:760px;">
        <table>
            <thead>
                <tr>{header_html}</tr>
            </thead>
            <tbody>
                {rows_html}
                {total_row}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_matrix), unsafe_allow_html=True)
    _table_gap()
    render_section_title(t["sr_pano_section_retencion"])
    render_section_subtitle(t["sr_pano_sub_retencion"])
    total_by = df_change.groupby("winner_1v").size().reset_index(name="total")
    retained = (
        df_change[df_change["change_type"] == same_key]
        .groupby("winner_1v")
        .size()
        .reset_index(name="retained")
    )
    retention = total_by.merge(retained, on="winner_1v", how="left").fillna(0)
    retention["retained"] = retention["retained"].astype(int)
    retention["rate"] = (retention["retained"] / retention["total"] * 100).round(1)
    retention = retention.sort_values("rate", ascending=False).reset_index(drop=True)
    rows_ret = ""
    for _, r in retention.iterrows():
        winner_label = str(r["winner_1v"])
        label = winner_label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        total_c = int(r["total"])
        participa_2v = winner_label in ("Jara (izquierda)", "Kast (derecha)")
        if participa_2v:
            retained_txt = str(int(r["retained"]))
            rate = float(r["rate"])
            if rate >= 70:
                rate_color = KAST_COLOR
            elif rate >= 40:
                rate_color = "#6b7280"
            else:
                rate_color = JARA_COLOR
            rate_txt = f"{rate:.1f}%"
            rate_style = f"font-weight:700; color:{rate_color};"
        else:
            retained_txt = "—"
            rate_txt = "—"
            rate_style = "color:#9CA3AF;"
        rows_ret += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{label}</td>'
            f'<td style="text-align:right; color:#666;">{total_c}</td>'
            f'<td style="text-align:right; color:#666;">{retained_txt}</td>'
            f'<td style="text-align:right; {rate_style}">{rate_txt}</td>'
            f"</tr>"
        )
    html_ret = _table_css("pa-tabla-retencion") + f"""
    <div class="pa-tabla-retencion" style="max-width:620px;">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_ganador_1v_lower']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_comunas_1v']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_retenidas']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_retencion']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_ret}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_ret), unsafe_allow_html=True)
    _table_gap()

# ============================================================================
# SECTION NO. 11 — PARISI: THE FATE OF THE ANTI-SYSTEM VOTE
# ============================================================================
def _prepare_parisi_df(df_fr: pd.DataFrame, df_sr: pd.DataFrame) -> pd.DataFrame:
    fr = df_fr[[
        "commune_id", "commune_name", "region_name", "parisi_pct", "casted_votes",
    ]].rename(columns={"parisi_pct": "parisi_pct_1v", "casted_votes": "casted_1v"})
    sr = df_sr[[
        "commune_id", "kast_pct", "jara_pct", "null_pct", "blank_pct", "casted_votes",
    ]].rename(columns={"casted_votes": "casted_2v"})
    merged = fr.merge(sr, on="commune_id", how="inner")
    merged["turnout_change"] = merged["casted_2v"] - merged["casted_1v"]
    merged["turnout_change_pct"] = (
        100 * merged["turnout_change"] / merged["casted_1v"].replace(0, 1)
    ).round(2)
    merged["margin_pp"] = (merged["kast_pct"] - merged["jara_pct"]).round(2)
    return merged

def _classify_parisi_brackets_4(pct: float) -> str:
    # NOTE: bracket labels are user-facing and hardcoded in Spanish.
    # They should live in translations.py. See TECHNICAL DEBT.
    if pct < 10:
        return "Bajo (<10%)"  # "Low (<10%)"
    elif pct < 20:
        return "Medio (10-20%)"  # "Medium (10-20%)"
    elif pct < 30:
        return "Alto (20-30%)"  # "High (20-30%)"
    else:
        return "Muy alto (>30%)"  # "Very high (>30%)"

def _classify_parisi_brackets_5(pct: float) -> str:
    # NOTE: bracket labels are user-facing and hardcoded in Spanish.
    # They should live in translations.py. See TECHNICAL DEBT.
    if pct < 5:
        return "<5%"
    elif pct < 10:
        return "5-10%"
    elif pct < 15:
        return "10-15%"
    elif pct < 20:
        return "15-20%"
    else:
        return ">20%"

def _comment_for_r(r: float, p: float, tema: str, t: dict) -> str:
    """Return a dynamic interpretive comment based on r and p, translated."""
    p_txt = f"p = {p:.4f}" if p < 0.05 else "no significativo"  # "not significant"
    if tema == "participacion":
        if r <= -0.3:
            key = "sr_pano_comment_part_neg"
        elif r < 0:
            key = "sr_pano_comment_part_lev_neg"
        elif r < 0.3:
            key = "sr_pano_comment_part_flat"
        else:
            key = "sr_pano_comment_part_pos"
        return t[key].format(r=f"{r:.2f}", p_txt=p_txt)
    elif tema == "nulo":
        if r >= 0.3:
            key = "sr_pano_comment_null_pos"
        elif r > 0:
            key = "sr_pano_comment_null_lev_pos"
        elif r > -0.3:
            key = "sr_pano_comment_null_flat"
        else:
            key = "sr_pano_comment_null_neg"
        return t[key].format(r=f"{r:.2f}", p_txt=p_txt)
    elif tema == "blanco":
        if abs(r) < 0.15:
            key = "sr_pano_comment_blank_flat"
        elif r > 0:
            key = "sr_pano_comment_blank_pos"
        else:
            key = "sr_pano_comment_blank_neg"
        return t[key].format(r=f"{r:.2f}", p_txt=p_txt)
    elif tema == "margen":
        if r >= 0.3:
            key = "sr_pano_comment_margen_pos"
        elif r > 0:
            key = "sr_pano_comment_margen_lev_pos"
        elif r > -0.3:
            key = "sr_pano_comment_margen_flat"
        else:
            key = "sr_pano_comment_margen_neg"
        return t[key].format(r=f"{r:.2f}", p_txt=p_txt)
    return ""

def _plotly_title(text: str) -> dict:
    """Unified Plotly title format (16px, #111827, left)."""
    return dict(
        text=text,
        font=dict(size=16, color="#111827", family="Liberation Sans, Arial, sans-serif"),
        x=0, xanchor="left",
    )

def _legend_standard() -> dict:
    """Unified Plotly legend format (bottom, 10px)."""
    return dict(
        orientation="h",
        yanchor="top",
        y=-0.15,
        xanchor="left",
        x=0,
        font=dict(size=10, color="#333", family="Liberation Sans, Arial, sans-serif"),
        bgcolor="rgba(0,0,0,0)",
    )

def _render_parisi_participation(df_parisi: pd.DataFrame, t: dict):
    df = df_parisi.copy()
    df["__bracket"] = df["parisi_pct_1v"].apply(_classify_parisi_brackets_4)
    order = ["Bajo (<10%)", "Medio (10-20%)", "Alto (20-30%)", "Muy alto (>30%)"]
    r, p = scipy_stats.pearsonr(df["parisi_pct_1v"], df["turnout_change"])
    sub = _comment_for_r(r, p, "participacion", t)
    _render_nb_card(
        label=t["sr_pano_card_corr_part"],
        value=f"Pearson r = {r:.2f}",
        sub=sub,
    )
    summary = df.groupby("__bracket").agg(
        communes=("commune_id", "count"),
        avg_parisi=("parisi_pct_1v", "mean"),
        avg_change=("turnout_change", "mean"),
        avg_change_pct=("turnout_change_pct", "mean"),
        with_fall=("turnout_change", lambda x: (x < 0).sum()),
    ).round(2)
    summary["pct_fall"] = (summary["with_fall"] / summary["communes"] * 100).round(2)
    summary = summary.reindex(order).dropna(how="all")
    rows_html = ""
    for bracket, r_ in summary.iterrows():
        bracket_esc = str(bracket).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        change = float(r_["avg_change"])
        change_sign = "+" if change >= 0 else ""
        change_txt = f"{change_sign}{_fmt_number(abs(change))}"
        change_pct = float(r_["avg_change_pct"])
        change_pct_sign = "+" if change_pct >= 0 else ""
        change_pct_txt = f"{change_pct_sign}{change_pct:.2f}%"
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{bracket_esc}</td>'
            f'<td style="text-align:right; color:#666;">{int(r_["communes"])}</td>'
            f'<td style="text-align:right; color:#666;">{r_["avg_parisi"]:.2f}%</td>'
            f'<td style="text-align:right; color:#333;">{change_txt}</td>'
            f'<td style="text-align:right; color:#333;">{change_pct_txt}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{r_["pct_fall"]:.2f}%</td>'
            f"</tr>"
        )
    html = _table_css("pa-tabla-parisi-part") + f"""
    <div class="pa-tabla-parisi-part" style="max-width:820px;">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_tramo_parisi']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_comunas']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_parisi_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_part_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_pct_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_con_caida']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["parisi_pct_1v"],
        y=df["turnout_change"],
        mode="markers",
        marker=dict(color=TREND_GRAY, size=8, opacity=0.6,
                    line=dict(color="white", width=0.5)),
        text=df["commune_name"],
        hovertemplate="<b>%{text}</b><br>Parisi 1V: %{x:.2f}%<br>Δ participación: %{y:,}<extra></extra>",
        showlegend=False,
    ))
    if len(df) > 2:
        z = np.polyfit(df["parisi_pct_1v"], df["turnout_change"], 1)
        p_line = np.poly1d(z)
        x_line = np.linspace(df["parisi_pct_1v"].min(), df["parisi_pct_1v"].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_line, y=p_line(x_line),
            mode="lines",
            line=dict(color="#333333", width=1.5, dash="dash"),
            name=t["sr_pano_plot_tendencia"],
            hoverinfo="skip",
            showlegend=False,
        ))
    fig.add_hline(y=0, line=dict(color=TREND_GRAY, width=1, dash="dot"))
    fig.update_layout(
        height=440,
        margin=dict(l=60, r=40, t=50, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        title=_plotly_title(t["sr_pano_plot_part_title"]),
        xaxis=dict(title=t["sr_pano_plot_part_x"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333"), zeroline=False),
        yaxis=dict(title=t["sr_pano_plot_part_y"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333")),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    render_section_subtitle(_comment_for_r(r, p, "participacion", t))
    render_section_title(t["sr_pano_section_top_caida"])
    top10 = df.nsmallest(10, "turnout_change")[
        ["commune_name", "region_name", "parisi_pct_1v", "turnout_change", "turnout_change_pct"]
    ].reset_index(drop=True)
    rows_top = ""
    for _, r_ in top10.iterrows():
        commune = str(r_["commune_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r_["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        change = int(r_["turnout_change"])
        change_txt = _fmt_number(change)
        change_pct = float(r_["turnout_change_pct"])
        change_pct_txt = f"{change_pct:+.2f}%"
        parisi_pct = f"{r_['parisi_pct_1v']:.2f}%"
        rows_top += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{parisi_pct}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{change_txt}</td>'
            f'<td style="text-align:right; color:#666;">{change_pct_txt}</td>'
            f"</tr>"
        )
    html_top = _table_css("pa-tabla-parisi-part-top") + f"""
    <div class="pa-tabla-parisi-part-top" style="max-width:820px;">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_comuna']}</th>
                    <th>{t['sr_pano_th_region']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_parisi_1v']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_part_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_delta_pct_prom']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_top}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_top), unsafe_allow_html=True)
    _table_gap()

def _render_parisi_protest(df_parisi: pd.DataFrame, t: dict):
    df = df_parisi.copy()
    df["__bracket"] = df["parisi_pct_1v"].apply(_classify_parisi_brackets_5)
    order = ["<5%", "5-10%", "10-15%", "15-20%", ">20%"]
    r_null, p_null = scipy_stats.pearsonr(df["parisi_pct_1v"], df["null_pct"])
    r_blank, p_blank = scipy_stats.pearsonr(df["parisi_pct_1v"], df["blank_pct"])
    def _p_str(p):
        return f"p = {p:.4f}" if p < 0.05 else t["sr_pano_p_not_significant"]
    cards = [
        (
            t["sr_pano_card_corr_null"],
            f"r = {r_null:.2f}",
            _p_str(p_null),
            COLOR_NULOS,
        ),
        (
            t["sr_pano_card_corr_blank"],
            f"r = {r_blank:.2f}",
            _p_str(p_blank),
            COLOR_BLANCOS,
        ),
    ]
    _render_nb_cards_row(cards)
    summary = df.groupby("__bracket").agg(
        communes=("commune_id", "count"),
        avg_parisi=("parisi_pct_1v", "mean"),
        avg_null=("null_pct", "mean"),
        avg_blank=("blank_pct", "mean"),
    ).round(2)
    summary = summary.reindex(order).dropna(how="all")
    rows_html = ""
    for bracket, r_ in summary.iterrows():
        bracket_esc = str(bracket).replace("<", "&lt;").replace(">", "&gt;")
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{bracket_esc}</td>'
            f'<td style="text-align:right; color:#666;">{int(r_["communes"])}</td>'
            f'<td style="text-align:right; color:#666;">{r_["avg_parisi"]:.2f}%</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{r_["avg_null"]:.2f}%</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{r_["avg_blank"]:.2f}%</td>'
            f"</tr>"
        )
    html = _table_css("pa-tabla-parisi-protesta") + f"""
    <div class="pa-tabla-parisi-protesta" style="max-width:820px;">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_tramo_parisi']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_comunas']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_parisi_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_nulo_2v_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_blanco_2v_prom']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()
    # Scatter 1: Nulls
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df["parisi_pct_1v"], y=df["null_pct"],
        mode="markers",
        marker=dict(color=COLOR_NULOS, size=8, opacity=0.6,
                    line=dict(color="white", width=0.5)),
        text=df["commune_name"],
        hovertemplate="<b>%{text}</b><br>Parisi 1V: %{x:.2f}%<br>Nulo 2V: %{y:.2f}%<extra></extra>",
        showlegend=False,
    ))
    if len(df) > 2:
        z = np.polyfit(df["parisi_pct_1v"], df["null_pct"], 1)
        p_line = np.poly1d(z)
        x_line = np.linspace(df["parisi_pct_1v"].min(), df["parisi_pct_1v"].max(), 100)
        fig1.add_trace(go.Scatter(
            x=x_line, y=p_line(x_line), mode="lines",
            line=dict(color="#333333", width=1.5, dash="dash"),
            hoverinfo="skip", showlegend=False,
        ))
    fig1.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=50, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        title=_plotly_title(t["sr_pano_plot_null_title"]),
        xaxis=dict(title=t["sr_pano_plot_part_x"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333")),
        yaxis=dict(title=t["sr_pano_plot_null_y"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333")),
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
    render_section_subtitle(_comment_for_r(r_null, p_null, "nulo", t))
    # Scatter 2: Blanks
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["parisi_pct_1v"], y=df["blank_pct"],
        mode="markers",
        marker=dict(color=COLOR_BLANCOS, size=8, opacity=0.6,
                    line=dict(color="white", width=0.5)),
        text=df["commune_name"],
        hovertemplate="<b>%{text}</b><br>Parisi 1V: %{x:.2f}%<br>Blanco 2V: %{y:.2f}%<extra></extra>",
        showlegend=False,
    ))
    if len(df) > 2:
        z = np.polyfit(df["parisi_pct_1v"], df["blank_pct"], 1)
        p_line = np.poly1d(z)
        x_line = np.linspace(df["parisi_pct_1v"].min(), df["parisi_pct_1v"].max(), 100)
        fig2.add_trace(go.Scatter(
            x=x_line, y=p_line(x_line), mode="lines",
            line=dict(color="#333333", width=1.5, dash="dash"),
            hoverinfo="skip", showlegend=False,
        ))
    fig2.update_layout(
        height=400,
        margin=dict(l=60, r=40, t=50, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        title=_plotly_title(t["sr_pano_plot_blank_title"]),
        xaxis=dict(title=t["sr_pano_plot_part_x"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333")),
        yaxis=dict(title=t["sr_pano_plot_blank_y"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333")),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    render_section_subtitle(_comment_for_r(r_blank, p_blank, "blanco", t))

def _render_parisi_margin(df_parisi: pd.DataFrame, t: dict):
    df = df_parisi.copy()
    df["__bracket"] = df["parisi_pct_1v"].apply(_classify_parisi_brackets_5)
    order = ["<5%", "5-10%", "10-15%", "15-20%", ">20%"]
    r_margin, p_margin = scipy_stats.pearsonr(df["parisi_pct_1v"], df["margin_pp"])
    _render_nb_card(
        label=t["sr_pano_card_corr_margen"],
        value=f"Pearson r = {r_margin:.2f}",
        sub=_comment_for_r(r_margin, p_margin, "margen", t),
        accent_color=KAST_COLOR if r_margin > 0 else None,
    )
    summary = df.groupby("__bracket").agg(
        communes=("commune_id", "count"),
        avg_kast=("kast_pct", "mean"),
        avg_jara=("jara_pct", "mean"),
        avg_margin=("margin_pp", "mean"),
        kast_wins=("margin_pp", lambda x: (x > 0).sum()),
    ).round(2)
    summary["pct_kast"] = (summary["kast_wins"] / summary["communes"] * 100).round(2)
    summary = summary.reindex(order).dropna(how="all")
    rows_html = ""
    for bracket, r_ in summary.iterrows():
        bracket_esc = str(bracket).replace("<", "&lt;").replace(">", "&gt;")
        margin = float(r_["avg_margin"])
        margin_sign = "+" if margin >= 0 else ""
        margin_txt = f"{margin_sign}{margin:.2f} pp"
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{bracket_esc}</td>'
            f'<td style="text-align:right; color:#666;">{int(r_["communes"])}</td>'
            f'<td style="text-align:right; font-weight:700; color:{KAST_COLOR};">{r_["avg_kast"]:.2f}%</td>'
            f'<td style="text-align:right; color:#666;">{r_["avg_jara"]:.2f}%</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{margin_txt}</td>'
            f'<td style="text-align:right; color:#666;">{r_["pct_kast"]:.2f}%</td>'
            f"</tr>"
        )
    html = _table_css("pa-tabla-parisi-margin") + f"""
    <div class="pa-tabla-parisi-margin" style="max-width:820px;">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_tramo_parisi']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_comunas']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_kast_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_jara_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_margen_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_comunas_kast']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()
    colors_pts = [
        _get_candidate_color("José Antonio Kast") if m > 0
        else _get_candidate_color("Jeannette Jara")
        for m in df["margin_pp"]
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["parisi_pct_1v"], y=df["margin_pp"],
        mode="markers",
        marker=dict(color=colors_pts, size=8, opacity=0.7,
                    line=dict(color="white", width=0.5)),
        text=df["commune_name"],
        hovertemplate="<b>%{text}</b><br>Parisi 1V: %{x:.2f}%<br>Margen Kast-Jara: %{y:.2f} pp<extra></extra>",
        showlegend=False,
    ))
    if len(df) > 2:
        z = np.polyfit(df["parisi_pct_1v"], df["margin_pp"], 1)
        p_line = np.poly1d(z)
        x_line = np.linspace(df["parisi_pct_1v"].min(), df["parisi_pct_1v"].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_line, y=p_line(x_line), mode="lines",
            line=dict(color="#333333", width=1.5, dash="dash"),
            hoverinfo="skip", showlegend=False,
        ))
    fig.add_hline(y=0, line=dict(color=TREND_GRAY, width=1, dash="dot"))
    fig.update_layout(
        height=440,
        margin=dict(l=60, r=40, t=50, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        title=_plotly_title(t["sr_pano_plot_margen_title"]),
        xaxis=dict(title=t["sr_pano_plot_part_x"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333")),
        yaxis=dict(title=t["sr_pano_plot_margen_y"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333")),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    render_section_subtitle(_comment_for_r(r_margin, p_margin, "margen", t))
    valid_brackets = summary.dropna(subset=["avg_margin"])
    if not valid_brackets.empty:
        fig2 = go.Figure()
        bar_colors = [
            _get_candidate_color("José Antonio Kast") if m > 0
            else _get_candidate_color("Jeannette Jara")
            for m in valid_brackets["avg_margin"]
        ]
        fig2.add_trace(go.Bar(
            x=valid_brackets["avg_margin"],
            y=valid_brackets.index.tolist(),
            orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{m:+.2f} pp" for m in valid_brackets["avg_margin"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Margen prom.: %{x:.2f} pp<extra></extra>",
        ))
        fig2.add_vline(x=0, line=dict(color=TREND_GRAY, width=1))
        fig2.update_layout(
            height=340,
            margin=dict(l=120, r=80, t=50, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Liberation Sans, Arial, sans-serif"),
            title=_plotly_title(t["sr_pano_plot_margen_bar_title"]),
            xaxis=dict(title=t["sr_pano_plot_margen_y"], showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333"), zeroline=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=10, color="#333")),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    if ">20%" in valid_brackets.index:
        high_margin = float(valid_brackets.loc[">20%", "avg_margin"])
        winner_txt = "Kast" if high_margin > 0 else "Jara"
        comment_bar = t["sr_pano_parisi_margen_comment_alto"].format(
            margen=f"{high_margin:+.2f}",
            ganador=winner_txt,
        )
    else:
        comment_bar = t["sr_pano_parisi_margen_comment"]
    render_section_subtitle(comment_bar)
    render_section_title(t["sr_pano_section_high_both"])
    high_both = df[(df["parisi_pct_1v"] > 20) & (df["margin_pp"] > 10)].copy()
    if high_both.empty:
        st.info(t["sr_pano_no_high_both"])
    else:
        high_both = high_both.sort_values("margin_pp", ascending=False).reset_index(drop=True)
        rows_hb = ""
        for _, r_ in high_both.iterrows():
            commune = str(r_["commune_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            region = str(r_["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            rows_hb += (
                f"<tr>"
                f'<td style="font-weight:400; color:#333;">{commune}</td>'
                f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
                f'<td style="text-align:right; color:#666;">{r_["parisi_pct_1v"]:.2f}%</td>'
                f'<td style="text-align:right; color:{KAST_COLOR};">{r_["kast_pct"]:.2f}%</td>'
                f'<td style="text-align:right; color:#666;">{r_["jara_pct"]:.2f}%</td>'
                f'<td style="text-align:right; font-weight:700; color:#111827;">{r_["margin_pp"]:+.2f} pp</td>'
                f"</tr>"
            )
        html_hb = _table_css("pa-tabla-parisi-margin-extra") + f"""
        <div class="pa-tabla-scroll" style="max-width:820px; max-height:600px; overflow-y:auto;">
            <div class="pa-tabla-parisi-margin-extra">
                <table>
                    <thead>
                        <tr>
                            <th>{t['sr_pano_th_comuna']}</th>
                            <th>{t['sr_pano_th_region']}</th>
                            <th style="text-align:right;">{t['sr_pano_th_pct_parisi_1v']}</th>
                            <th style="text-align:right;">{t['sr_pano_th_pct_kast_2v']}</th>
                            <th style="text-align:right;">{t['sr_pano_th_pct_jara_2v']}</th>
                            <th style="text-align:right;">{t['sr_pano_th_margen']}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_hb}
                    </tbody>
                </table>
            </div>
        </div>
        """
        st.markdown(_clean_html(html_hb), unsafe_allow_html=True)
        _table_gap()

def _render_parisi_anti_system(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict):
    df_parisi = _prepare_parisi_df(df_fr, df_sr)
    if df_parisi.empty:
        st.info(t["sr_pano_no_parisi"])
        return
    view = st.radio(
        t["sr_pano_radio_label"],
        [t["sr_pano_radio_parisi_part"], t["sr_pano_radio_parisi_nb"], t["sr_pano_radio_parisi_margen"]],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="panorama_sr_parisi_view",
    )
    if view == t["sr_pano_radio_parisi_part"]:
        _render_parisi_participation(df_parisi, t)
    elif view == t["sr_pano_radio_parisi_nb"]:
        _render_parisi_protest(df_parisi, t)
    else:
        _render_parisi_margin(df_parisi, t)

# ============================================================================
# SECTION NO. 12 — PARISI: COMMUNE SEGMENTATION
# ============================================================================
def _render_parisi_segmentation(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict):
    fr_work = df_fr.copy()
    fr_cols = [c for c in VOTE_COLS_FR if c in fr_work.columns]
    fr_work["__winner_key_1v"] = fr_work[fr_cols].idxmax(axis=1).str.replace("_votes", "", regex=False)
    parisi_communes = fr_work[fr_work["__winner_key_1v"] == "parisi"][
        ["commune_id", "commune_name", "region_name"]
    ].copy()
    if parisi_communes.empty:
        st.info(t["sr_pano_no_parisi_wins"])
        return
    sr_metrics = df_sr[[
        "commune_id", "jara_pct", "kast_pct", "null_pct", "blank_pct",
    ]].copy()
    sr_metrics["protest_pct"] = sr_metrics["null_pct"] + sr_metrics["blank_pct"]
    sr_metrics["kast_margin"] = sr_metrics["kast_pct"] - sr_metrics["jara_pct"]
    sr_metrics["null_blank_ratio"] = sr_metrics["null_pct"] / (sr_metrics["blank_pct"] + 0.01)
    merged = parisi_communes.merge(sr_metrics, on="commune_id", how="inner")
    if len(merged) < 4:
        st.info(t["sr_pano_no_clustering"])
        return
    features = ["kast_pct", "jara_pct", "null_pct", "blank_pct",
                "protest_pct", "kast_margin", "null_blank_ratio"]
    X = merged[features].fillna(0).copy()
    X_scaled = StandardScaler().fit_transform(X)
    k_optimal = 4
    if len(merged) < k_optimal:
        k_optimal = max(2, len(merged) - 1)
    kmeans = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
    merged["cluster"] = kmeans.fit_predict(X_scaled)
    cluster_labels = {}
    for cid in range(k_optimal):
        cluster_data = merged[merged["cluster"] == cid]
        avg_kast = cluster_data["kast_pct"].mean()
        avg_null = cluster_data["null_pct"].mean()
        if avg_kast > 60 and avg_null < 5:
            key = "sr_pano_cluster_feudos_kast"
        elif avg_kast > 50:
            key = "sr_pano_cluster_proclives_kast"
        elif avg_kast < 40:
            key = "sr_pano_cluster_proclives_jara"
        else:
            key = "sr_pano_cluster_mixto"
        label = t[key].format(cid=cid)
        base = label
        n = 1
        while label in cluster_labels.values():
            n += 1
            label = f"{base} #{n}"
        cluster_labels[cid] = label
    merged["cluster_label"] = merged["cluster"].map(cluster_labels)
    _render_nb_card(
        label=t["sr_pano_card_segment_label"],
        value=t["sr_pano_card_segment_value"].format(n=len(merged)),
        sub=t["sr_pano_card_segment_sub"].format(k=k_optimal),
    )
    render_section_title(t["sr_pano_section_clusters"])
    summary = merged.groupby(["cluster", "cluster_label"]).agg(
        communes=("commune_id", "count"),
        avg_kast=("kast_pct", "mean"),
        avg_jara=("jara_pct", "mean"),
        avg_null=("null_pct", "mean"),
        avg_blank=("blank_pct", "mean"),
        avg_margin=("kast_margin", "mean"),
    ).round(2).reset_index().sort_values("cluster")
    rows_html = ""
    for _, r_ in summary.iterrows():
        margin = float(r_["avg_margin"])
        margin_sign = "+" if margin >= 0 else ""
        margin_txt = f"{margin_sign}{margin:.2f} pp"
        label = str(r_["cluster_label"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cid = int(r_["cluster"])
        color = CLUSTER_COLORS[cid % len(CLUSTER_COLORS)]
        rows_html += (
            f"<tr>"
            f'<td><span class="pa-color-box" style="background:{color};"></span>{label}</td>'
            f'<td style="text-align:right; color:#666;">{int(r_["communes"])}</td>'
            f'<td style="text-align:right; font-weight:700; color:{KAST_COLOR};">{r_["avg_kast"]:.2f}%</td>'
            f'<td style="text-align:right; color:#666;">{r_["avg_jara"]:.2f}%</td>'
            f'<td style="text-align:right; color:#666;">{r_["avg_null"]:.2f}%</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{margin_txt}</td>'
            f"</tr>"
        )
    html = _table_css("pa-tabla-parisi-segment") + f"""
    <div class="pa-tabla-parisi-segment" style="max-width:900px;">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_pano_th_cluster']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_comunas']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_kast_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_jara_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_pct_nulo_prom']}</th>
                    <th style="text-align:right;">{t['sr_pano_th_margen_prom']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    render_section_title(t["sr_pano_section_pca"])
    fig_pca = go.Figure()
    for cid in range(k_optimal):
        mask = merged["cluster"] == cid
        label = cluster_labels[cid]
        color = CLUSTER_COLORS[cid % len(CLUSTER_COLORS)]
        fig_pca.add_trace(go.Scatter(
            x=X_pca[mask, 0], y=X_pca[mask, 1],
            mode="markers",
            name=label,
            marker=dict(color=color, size=10, opacity=0.75,
                        line=dict(color="white", width=1)),
            text=merged.loc[mask, "commune_name"],
            hovertemplate="<b>%{text}</b><extra></extra>",
        ))
    fig_pca.update_layout(
        height=520,
        margin=dict(l=60, r=40, t=30, b=100),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        xaxis=dict(
            title=t["sr_pano_plot_pca_x"].format(pct=f"{pca.explained_variance_ratio_[0]*100:.1f}"),
            showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333"),
            zeroline=True, zerolinecolor="#e5e7eb",
        ),
        yaxis=dict(
            title=t["sr_pano_plot_pca_y"].format(pct=f"{pca.explained_variance_ratio_[1]*100:.1f}"),
            showgrid=True, gridcolor="#f0f0f0", tickfont=dict(size=10, color="#333"),
            zeroline=True, zerolinecolor="#e5e7eb",
        ),
        showlegend=True,
        legend=_legend_standard(),
    )
    st.plotly_chart(fig_pca, use_container_width=True, config={"displayModeBar": False})
    render_section_title(t["sr_pano_section_perfil_clusters"])
    metrics = ["avg_kast", "avg_jara", "avg_null", "avg_blank", "avg_margin"]
    metric_labels = [
        t["sr_pano_radar_pct_kast"],
        t["sr_pano_radar_pct_jara"],
        t["sr_pano_radar_pct_null"],
        t["sr_pano_radar_pct_blank"],
        t["sr_pano_radar_margin"],
    ]
    df_radar = summary[["cluster_label", "cluster"] + metrics].copy()
    for col in metrics:
        col_min = df_radar[col].min()
        col_max = df_radar[col].max()
        rng = col_max - col_min
        if rng == 0:
            df_radar[col] = 0.5
        else:
            df_radar[col] = (df_radar[col] - col_min) / rng
    angles = [n / float(len(metrics)) * 2 * np.pi for n in range(len(metrics))]
    angles += angles[:1]
    fig_radar = go.Figure()
    for _, row in df_radar.iterrows():
        values = [row[c] for c in metrics]
        values += values[:1]
        cid = int(row["cluster"])
        color = CLUSTER_COLORS[cid % len(CLUSTER_COLORS)]
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=metric_labels + [metric_labels[0]],
            mode="lines+markers",
            name=row["cluster_label"],
            line=dict(color=color, width=2),
            fill="toself",
            fillcolor=color,
            opacity=0.4,
            hovertemplate="<b>%{theta}</b>: %{r:.2f}<extra></extra>",
        ))
    fig_radar.update_layout(
        height=520,
        margin=dict(l=60, r=40, t=60, b=100),
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(255,255,255,1)",
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, gridcolor="#e5e7eb"),
            angularaxis=dict(gridcolor="#e5e7eb", tickfont=dict(size=10, color="#333")),
        ),
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        showlegend=True,
        legend=_legend_standard(),
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

# ============================================================================
# SECTION BUILDERS
# ============================================================================
def _build_participation_section(df: pd.DataFrame, t: dict) -> None:
    """Build the national participation section."""
    render_section_title(t["sr_pano_section_participacion"])
    _render_national_participation(df, t)

def _build_participation_comparison_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the participation comparison section."""
    # This title is user-facing and hardcoded in Spanish.
    # It should live in translations.py. See TECHNICAL DEBT.
    render_section_title("Participación y Voto Válido: 1ª vs 2ª vuelta")  # "Participation and Valid Vote: 1st vs 2nd round"
    _render_participation_comparison(df_fr, df_sr, t)

def _build_null_section(df: pd.DataFrame, df_fr: pd.DataFrame, t: dict) -> None:
    """Build the null vote section."""
    _render_null_section(df, df_fr, t)

def _build_blank_section(df: pd.DataFrame, df_fr: pd.DataFrame, t: dict) -> None:
    """Build the blank vote section."""
    _render_blank_section(df, df_fr, t)

def _build_national_results_section(df: pd.DataFrame, t: dict) -> None:
    """Build the national results section."""
    render_section_subtitle(t["sr_pano_sub_resultados"])
    _render_national_results(df, t)

def _build_communes_won_section(df: pd.DataFrame, t: dict) -> None:
    """Build the communes won section."""
    render_section_subtitle(t["sr_pano_sub_comunas_ganadas"])
    _render_communes_won(df, t)

def _build_winners_by_macrozone_section(df: pd.DataFrame, t: dict) -> None:
    """Build the winners by macrozone section."""
    render_section_title(t["fr_pano_section_comunas_macro"])
    _render_winners_by_macrozone(df, t)

def _build_regional_winners_section(df: pd.DataFrame, t: dict) -> None:
    """Build the regional winners section."""
    render_section_subtitle(t["sr_pano_sub_regionales"])
    _render_regional_winners(df, t)

def _build_regional_capitals_section(df: pd.DataFrame, t: dict) -> None:
    """Build the regional capitals section."""
    render_section_subtitle(t["sr_pano_sub_capitales"])
    _render_regional_capitals(df, t)

def _build_vote_by_commune_size_section(df: pd.DataFrame, t: dict) -> None:
    """Build the vote by commune size section."""
    render_section_subtitle(t["sr_pano_sub_tamano_comuna"])
    _render_vote_by_commune_size(df, t)

def _build_electoral_realignment_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the electoral realignment section."""
    render_section_subtitle(t["sr_pano_sub_realineamiento"])
    _render_electoral_realignment(df_fr, df_sr, t)

def _build_parisi_anti_system_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the Parisi anti-system section."""
    render_section_subtitle(t["sr_pano_sub_parisi"])
    _render_parisi_anti_system(df_fr, df_sr, t)

def _build_parisi_segmentation_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the Parisi segmentation section."""
    render_section_subtitle(t["sr_pano_sub_segmentacion"])
    _render_parisi_segmentation(df_fr, df_sr, t)

# ============================================================================
# RENDER (orchestrator)
# ============================================================================
def render(t: dict):
    """
    Render the Second Round Panorama page.
    """
    render_view_title(t["sr_pano_view_title"])
    render_view_subtitle(t["sr_pano_view_subtitle"])
    try:
        with st.spinner(t["loading"]):
            df = load_fact_second_round_2025()
            df_fr = load_fact_first_round_2025()
            dim = load_dim_commune()
            if "population" in dim.columns and "population" not in df.columns:
                df = df.merge(
                    dim[["commune_id", "population"]],
                    on="commune_id",
                    how="left",
                )

        _build_participation_section(df, t)
        st.divider()

        with st.expander(t["sr_pano_exp_part_comp"], expanded=False):
            _build_participation_comparison_section(df_fr, df, t)

        with st.expander(t["sr_pano_exp_nulos"], expanded=False):
            _build_null_section(df, df_fr, t)
        with st.expander(t["sr_pano_exp_blancos"], expanded=False):
            _build_blank_section(df, df_fr, t)
        with st.expander(t["sr_pano_exp_resultados"], expanded=False):
            _build_national_results_section(df, t)
        with st.expander(t["sr_pano_exp_comunas_ganadas"], expanded=False):
            _build_communes_won_section(df, t)
            st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
            _build_winners_by_macrozone_section(df, t)
        with st.expander(t["sr_pano_exp_regionales"], expanded=False):
            _build_regional_winners_section(df, t)
        with st.expander(t["sr_pano_exp_capitales"], expanded=False):
            _build_regional_capitals_section(df, t)
        with st.expander(t["sr_pano_exp_tamano_comuna"], expanded=False):
            _build_vote_by_commune_size_section(df, t)
        with st.expander(t["sr_pano_exp_realineamiento"], expanded=False):
            _build_electoral_realignment_section(df_fr, df, t)
        with st.expander(t["sr_pano_exp_parisi_destino"], expanded=False):
            _build_parisi_anti_system_section(df_fr, df, t)
        with st.expander(t["sr_pano_exp_parisi_segmentacion"], expanded=False):
            _build_parisi_segmentation_section(df_fr, df, t)
        _render_page_footer(t)
    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)

# ============================================================================
# TECHNICAL DEBT
# ============================================================================
# Three groups of user-facing strings are still hardcoded in Spanish. They
# should be moved to translations.py (LANG["ES"] / LANG["EN"]) in a future
# cleanup pass. Until then, they are kept as-is to avoid breaking the
# bilingual setup and to keep this refactor focused on identifier translation.
#
# 1. POPULATION_BRACKETS labels and subtitles:
# "Grandes centros urbanos" = Large urban centers
# "Centros urbanos medios" = Medium urban centers
# "Centros urbanos pequeños" = Small urban centers
# "Rural-urbano" = Rural-urban
# "Rural" = Rural
# Subtitles describe the population range:
# "más de 200.000 hab." = more than 200,000 inhabitants
# "100.000 – 199.999 hab." = 100,000 – 199,999 inhabitants
# "50.000 – 99.999 hab." = 50,000 – 99,999 inhabitants
# "10.000 – 49.999 hab." = 10,000 – 49,999 inhabitants
# "menos de 10.000 hab." = fewer than 10,000 inhabitants
#
# 2. Plotly hover labels in _plot_top_bar (label_map):
# "Región" = Region
# "Votos totales" = Total casted votes
# "Votos válidos" = Valid votes
# "Votos nulos" = Null votes
# "Votos blancos" = Blank votes
# "% nulos" = Null %
# "% blancos" = Blank %
# "Comuna" = Commune
#
# 3. Parisi bracket labels in _classify_parisi_brackets_4 and _5:
# "Bajo (<10%)" = Low (<10%)
# "Medio (10-20%)" = Medium (10-20%)
# "Alto (20-30%)" = High (20-30%)
# "Muy alto (>30%)" = Very high (>30%)
# "<5%", "5-10%", "10-15%", "15-20%", ">20%" = same ranges, no translation needed
#
# When these are moved, add the corresponding keys to translations.py with
# the prefix sr_pano_ and update the call sites. No other code depends on
# them.
