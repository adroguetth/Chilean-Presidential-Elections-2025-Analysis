"""
First Round — Panorama
============================================================================
Visual analysis view for the First Round 2025. Contains 12 collapsible
sections covering national participation, null/blank vote analysis, national
results, ideological blocks, top communes per candidate, communes won,
regional winners, capital cities, vote by commune size, recoverable communes
for the runoff, the anti-system vote (Parisi), and the libertarian right
(Kaiser).

Sections:
     1. National participation (cards)
     2. Null vote analysis
     3. Blank vote analysis
     4. National results + ideological blocks
     5. Top communes per candidate
     6. Communes won (table + waffle + macrozone)
     7. Regional winners
     8. Vote in regional capitals
     9. Vote by commune size (stacked bars)
    10. Second round: recoverable communes (Jara / Kast scatter)
    11. Anti-system vote analysis: Franco Parisi
    12. Kaiser: the new libertarian right

Notes:
    All HTML is passed through _clean_html() before st.markdown() to prevent
    Markdown from interpreting indented f-strings (4+ spaces) as code blocks.

    Candidate cells in tables follow the reference HTML: color box + plain
    text name (no pill). Applies to every table in this view.

    Transformation helpers (clean_html, format_number, normalize_commune) are
    imported from utils.html_helpers.
    Titles use components.titles.
    Electoral data colors and block colors use config.constants.

Technical debt:
    Two groups of user-facing strings are still hardcoded in Spanish and
    should be migrated to translations.py in a future cleanup pass:
      - TRAMOS_POPULATION labels and subtitles.
      - Plotly hover labels in _plot_top_bar (label_map).
    See the TECHNICAL DEBT block at the bottom of the file for details.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_fact_first_round_2025, load_dim_commune
from utils.calculations import compute_first_round_results
from utils.html_helpers import (
    clean_html as _clean_html,
    format_number as _fmt_number,
    normalize_commune as _norm_commune,
)
from config.constants import (
    COLOR_VALIDOS,
    COLOR_NULOS,
    COLOR_BLANCOS,
    COLOR_POSITIVE,
    COLOR_NEUTRAL_INDICATOR,
    NEUTRAL_COLOR,
    POLITICAL_BLOCKS,
    _get_candidate_color,
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
VOTE_COLS_TO_NAMES = {
    "jara_votes": "Jeannette Jara",
    "kast_votes": "José Antonio Kast",
    "parisi_votes": "Franco Parisi",
    "kaiser_votes": "Johannes Kaiser",
    "matthei_votes": "Evelyn Matthei",
    "mayne_nicholls_votes": "Harold Mayne-Nicholls",
    "enriquez_ominami_votes": "Marco Enríquez-Ominami",
    "artes_votes": "Eduardo Artés",
}

MIN_CASTED_VOTES = 300
RECOVERABLE_THRESHOLD = 1000

REGIONAL_CAPITALS = [
    "Arica", "Iquique", "Antofagasta", "Copiapó", "La Serena",
    "Valparaíso", "Santiago", "Rancagua", "Talca", "Chillán",
    "Concepción", "Temuco", "Valdivia", "Puerto Montt", "Coyhaique",
    "Punta Arenas",
]

TOP_CANDIDATES = [
    {"name": "Jeannette Jara",    "pct_col": "jara_pct",    "votes_col": "jara_votes"},
    {"name": "José Antonio Kast", "pct_col": "kast_pct",    "votes_col": "kast_votes"},
    {"name": "Franco Parisi",     "pct_col": "parisi_pct",  "votes_col": "parisi_votes"},
    {"name": "Johannes Kaiser",   "pct_col": "kaiser_pct",  "votes_col": "kaiser_votes"},
    {"name": "Evelyn Matthei",    "pct_col": "matthei_pct", "votes_col": "matthei_votes"},
]

# NOTE: labels and subtitles are user-facing strings hardcoded in Spanish.
# They should live in translations.py. See TECHNICAL DEBT at the bottom.
POPULATION_BRACKETS = [
    {"label": "Grandes centros urbanos", "sub": "más de 200.000 hab.",     "min": 200_001, "max": None},
    {"label": "Centros urbanos medios",  "sub": "100.000 – 199.999 hab.",  "min": 100_000, "max": 199_999},
    {"label": "Centros urbanos pequeños","sub": "50.000 – 99.999 hab.",    "min": 50_000,  "max": 99_999},
    {"label": "Rural-urbano",            "sub": "10.000 – 49.999 hab.",    "min": 10_000,  "max": 49_999},
    {"label": "Rural",                   "sub": "menos de 10.000 hab.",    "min": 0,       "max": 9_999},
]

INTENSITY_ORDER = ["> 40%", "35% – 40%", "30% – 35%", "20% – 30%", "< 20%"]


# ============================================================================
# LOCAL HELPERS — VISUAL FORMATTING
# ============================================================================
def _compute_winner(df: pd.DataFrame) -> pd.Series:
    cols = [c for c in VOTE_COLS_TO_NAMES if c in df.columns]
    if not cols:
        return pd.Series(["No data"] * len(df), index=df.index)
    return df[cols].idxmax(axis=1).map(VOTE_COLS_TO_NAMES)


def _format_pct(v: float) -> str:
    return f"{v:.2f}%"


def _short_winner(winner_full: str) -> str:
    mapping = {
        "Jeannette Jara": "Jara",
        "José Antonio Kast": "Kast",
        "Franco Parisi": "Parisi",
        "Johannes Kaiser": "Kaiser",
        "Evelyn Matthei": "Matthei",
        "Harold Mayne-Nicholls": "Mayne-N.",
        "Marco Enríquez-Ominami": "ME-O",
        "Eduardo Artés": "Artés",
        "No data": "—",
    }
    return mapping.get(winner_full, winner_full.split()[-1] if winner_full else "—")


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
    """6px gap below each table. Called in a separate st.markdown so Streamlit
    does not collapse the div."""
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)


def _render_page_footer(t: dict) -> None:
    st.markdown(_clean_html(f"""
    <style>
        .page-footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; width: 100%; }}
        .page-footer p {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; color: #9a9a9a; text-align: center; margin: 0; line-height: 1.4; }}
    </style>
    <div class="page-footer"><p>{t['data_source']} · {t['data_source_note']}</p></div>
    """), unsafe_allow_html=True)


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
    </style>
    """


# ============================================================================
# SHARED CARD CSS
# ============================================================================
# Extracted because .nb-card is used in three sections (participation,
# Parisi intensity, and one more). The .hr-card variant is used in the
# Kaiser section. Keeping them as constants avoids divergence.
_NB_CARD_CSS = """
<style>
    .nb-cards { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
    .nb-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 160px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .nb-card-label { font-family: "Liberation Sans", Arial, sans-serif; font-size: 10pt; color: #6b7280; font-weight: 500; }
    .nb-card-value { font-family: "Liberation Sans", Arial, sans-serif; font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; display: flex; align-items: center; gap: 8px; }
    .nb-card-sub { font-family: "Liberation Sans", Arial, sans-serif; font-size: 9pt; color: #6b7280; margin-top: 8px; }
</style>
"""

_KAISER_CARD_CSS = """
<style>
    .kaiser-cards { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
    .kaiser-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 180px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }
    .kaiser-card-label { font-size: 10pt; color: #6b7280; font-weight: 500; }
    .kaiser-card-value { font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; }
    .kaiser-card-sub { font-size: 9pt; color: #6b7280; margin-top: 8px; font-weight: 400; }
</style>
"""

_BLOCKS_CSS = """
<style>
    .blocks-wrap { font-family: "Liberation Sans", Arial, sans-serif; max-width: 900px; }
    .blocks-labels { display: flex; margin-bottom: 6px; font-size: 8pt; color: #6b7280; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; }
    .blocks-labels > div { white-space: nowrap; }
    .blocks-bar-wrap { position: relative; margin-bottom: 14px; }
    .blocks-bar { display: flex; height: 48px; border-radius: 6px; overflow: hidden; }
    .blocks-bar > div { display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 13pt; }
    .blocks-midline { position: absolute; top: -8px; bottom: -8px; left: 50%; width: 0; border-left: 1px dashed #6b7280; pointer-events: none; }
    .blocks-midlabel { position: absolute; top: -22px; left: 50%; transform: translateX(-50%); font-size: 7.5pt; color: #6b7280; letter-spacing: 0.06em; font-weight: 500; }
    .blocks-details { display: flex; margin-bottom: 30px; }
    .blocks-detail { padding: 0 6px; }
    .blocks-cands { font-size: 10pt; color: #333; margin-bottom: 4px; }
    .blocks-votes { font-size: 12pt; font-weight: 700; color: #111827; }
    .blocks-legend { display: flex; flex-direction: column; gap: 8px; font-size: 9pt; color: #333; }
    .legend-item { display: flex; align-items: center; gap: 8px; }
    .legend-dot { width: 13px; height: 13px; border-radius: 3px; display: inline-block; flex-shrink: 0; }
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
    .tramos-legend { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 12px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 10pt; color: #333; }
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
        "zona": "Región",
        "casted_votes": "Votos totales",
        "casted_fmt": "Votos totales",
        "valid_votes": "Votos válidos",
        "valid_fmt": "Votos válidos",
        "null_votes": "Votos nulos",
        "null_fmt": "Votos nulos",
        "blank_votes": "Votos blancos",
        "blank_fmt": "Votos blancos",
        "null_pct": "% nulos",
        "null_pct_fmt": "% nulos",
        "blank_pct": "% blancos",
        "blank_pct_fmt": "% blancos",
        "region_name": "Región",
        "commune_name": "Comuna",
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
    if has_title:
        fig.update_layout(
            title=dict(text=title, font=dict(size=12 + font_boost, color="#111827", family="Liberation Sans, Arial, sans-serif"), x=0, xanchor="left"),
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
            margin=dict(l=120, r=110, t=50, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)" if transparent_bg else "rgba(255,255,255,1)",
            height=max(height_min, height_per_bar * len(df) + 120),
            font=dict(family="Liberation Sans, Arial, sans-serif"),
        )
    else:
        fig.update_layout(
            title_text="",
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
            margin=dict(l=120, r=110, t=10, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)" if transparent_bg else "rgba(255,255,255,1)",
            height=max(height_min, height_per_bar * len(df) + 80),
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
    agg = agg.rename(columns={"region_name": "zona"})
    return agg


def _blank_stats_by_region(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("region_name", as_index=False).agg(
        null_votes=("null_votes", "sum"),
        blank_votes=("blank_votes", "sum"),
        casted_votes=("casted_votes", "sum"),
    )
    agg["valid_votes"] = agg["casted_votes"] - agg["null_votes"] - agg["blank_votes"]
    agg["blank_pct"] = (agg["blank_votes"] / agg["casted_votes"] * 100).round(2)
    agg = agg.rename(columns={"region_name": "zona"})
    return agg


def _commune_null_stats(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["commune_name", "region_name", "null_votes", "blank_votes", "casted_votes"]].copy()
    out["valid_votes"] = out["casted_votes"] - out["null_votes"] - out["blank_votes"]
    out["null_pct"] = (out["null_votes"] / out["casted_votes"] * 100).round(2)
    out["winner"] = _compute_winner(df)
    out = out.rename(columns={"commune_name": "zona"})
    return out


def _commune_blank_stats(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["commune_name", "region_name", "null_votes", "blank_votes", "casted_votes"]].copy()
    out["valid_votes"] = out["casted_votes"] - out["null_votes"] - out["blank_votes"]
    out["blank_pct"] = (out["blank_votes"] / out["casted_votes"] * 100).round(2)
    out["winner"] = _compute_winner(df)
    out = out.rename(columns={"commune_name": "zona"})
    return out

# ============================================================================
# IDEOLOGICAL BLOCKS — SHARED DEFINITION
# ============================================================================
def _ideological_blocks(t: dict) -> list:
    """
    Return the three ideological blocks with their translated labels and
    the vote columns that compose each one.

    Parameters
    ----------
    t : dict
        Translation dictionary.

    Returns
    -------
    list of dict
        Each dict has: block (label), columns (vote columns),
        candidates (short description), characteristic (translated text).
    """
    return [
        {
            "block": t["fr_pano_bloques_izq"],
            "columns": ["jara_votes", "enriquez_ominami_votes", "artes_votes"],
            "candidates": "Jara + MEO + Artés",
            "characteristic": t["fr_pano_bloque_izq_caract"],
        },
        {
            "block": t["fr_pano_bloques_der"],
            "columns": ["kast_votes", "kaiser_votes", "matthei_votes"],
            "candidates": "Kast + Kaiser + Matthei",
            "characteristic": t["fr_pano_bloque_der_caract"],
        },
        {
            "block": t["fr_pano_bloques_antisistema"],
            "columns": ["parisi_votes", "mayne_nicholls_votes"],
            "candidates": "Parisi + Mayne-Nicholls",
            "characteristic": t["fr_pano_bloque_cen_caract"],
        },
    ]

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
            <div class="nb-card-label">{t['fr_pano_kpi_total_emitidos']}</div>
            <div class="nb-card-value">{_fmt_number(total_cast)}</div>
            <div class="nb-card-sub"><b>{t['fr_pano_kpi_nulos_blancos'].format(pct=f"{combined_pct:.2f}")}</b></div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_pano_kpi_validos']}</div>
            <div class="nb-card-value">{_fmt_number(total_valid)}</div>
            <div class="nb-card-sub">{t['fr_pano_kpi_pct_total'].format(pct=f"{pct_valid:.1f}")}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_pano_kpi_nulos']}</div>
            <div class="nb-card-value">{_fmt_number(total_null)}</div>
            <div class="nb-card-sub" style="color:{COLOR_NULOS};">{pct_null:.2f}%</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_pano_kpi_blancos']}</div>
            <div class="nb-card-value">{_fmt_number(total_blank)}</div>
            <div class="nb-card-sub" style="color:{COLOR_BLANCOS};">{pct_blank:.2f}%</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 2 — NULL VOTES
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


def _render_null_section(df: pd.DataFrame, t: dict):
    render_section_title(t["fr_pano_section_reg_nulos_abs"])
    _render_top_null_regions(df, t, top_n=16)

    st.divider()

    communes = _commune_null_stats(df)
    communes = communes[communes["casted_votes"] >= MIN_CASTED_VOTES].copy()

    render_section_title(t["fr_pano_section_com_nulos_abs"])
    _render_communes_table(communes, value_col="null_votes", pct_col="null_pct", mode="abs", t=t)

    render_section_title(t["fr_pano_section_com_nulos_rel"])
    _render_communes_table(communes, value_col="null_votes", pct_col="null_pct", mode="rel", t=t)


# ============================================================================
# SECTION NO. 3 — BLANK VOTES
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


def _render_blank_section(df: pd.DataFrame, t: dict):
    render_section_title(t["fr_pano_section_reg_blancos_abs"])
    _render_top_blank_regions(df, t, top_n=16)

    st.divider()

    communes = _commune_blank_stats(df)
    communes = communes[communes["casted_votes"] >= MIN_CASTED_VOTES].copy()

    render_section_title(t["fr_pano_section_com_blancos_abs"])
    _render_communes_table(communes, value_col="blank_votes", pct_col="blank_pct", mode="abs", t=t)

    render_section_title(t["fr_pano_section_com_blancos_rel"])
    _render_communes_table(communes, value_col="blank_votes", pct_col="blank_pct", mode="rel", t=t)


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
# SECTION NO. 4 — NATIONAL RESULTS + IDEOLOGICAL BLOCKS
# ============================================================================
def _render_national_results(df: pd.DataFrame, t: dict):
    fr = compute_first_round_results(df)

    rows_html = ""
    for _, row in fr.iterrows():
        party = str(row["party"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        votes = _fmt_number(row["votes"])
        pct = f"{row['pct']:.2f}%"

        candidate_cell = _candidate_cell(row["candidate_name"])

        passes = row["status"] == "passes_to_runoff"
        status_text = t["passes_to_runoff"] if passes else t["does_not_pass"]
        if passes:
            status_style = "background:#E8F5E9; color:#2E7D32; border:1px solid #C8E6C9;"
        else:
            status_style = "background:#F0EFEC; color:#888780; border:1px solid #E0DED8;"

        rows_html += (
            f"<tr>"
            f"<td>{candidate_cell}</td>"
            f"<td style=\"color:#6b7280; font-size:10pt;\">{party}</td>"
            f"<td style=\"text-align:right; color:#666;\">{votes}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{pct}</td>"
            f"<td style=\"text-align:center;\"><span class=\"pa-status-pill\" style=\"{status_style}\">{status_text}</span></td>"
            f"</tr>"
        )

    html = _table_css("pa-tabla-resultados") + f"""
    <style>
        .pa-status-pill {{ display: inline-block; padding: 2px 9px; border-radius: 6px; font-size: 8pt; font-weight: 600; white-space: nowrap; }}
    </style>
    <div class="pa-tabla-resultados" style="max-width:720px;">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_pano_th_candidato']}</th>
                    <th>{t['fr_pano_th_partido']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_votos']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th style="text-align:center;">{t['fr_pano_th_estado']}</th>
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


def _render_ideological_blocks(df: pd.DataFrame, t: dict):
    total_valid = (
        int(df["casted_votes"].sum())
        - int(df["null_votes"].sum())
        - int(df["blank_votes"].sum())
    )

    blocks = _ideological_blocks(t)

    blocks_data = []
    for block in blocks:
        cols = [c for c in block["columns"] if c in df.columns]
        votes = int(df[cols].sum().sum())
        pct = (votes / total_valid * 100) if total_valid else 0
        blocks_data.append({**block, "votes": votes, "pct": pct})

    left = next(b for b in blocks_data if b["block"] == t["fr_pano_bloques_izq"])
    right = next(b for b in blocks_data if b["block"] == t["fr_pano_bloques_der"])
    center = next(b for b in blocks_data if b["block"] == t["fr_pano_bloques_antisistema"])

    COLOR_LEFT = POLITICAL_BLOCKS["Izquierda"]
    COLOR_CENTER = POLITICAL_BLOCKS["Antisistema"]
    COLOR_RIGHT = POLITICAL_BLOCKS["Derecha"]

    html = _BLOCKS_CSS + f"""
    <div class="blocks-wrap">
        <div class="blocks-labels">
            <div style="width: {left['pct']}%; text-align: left;">{t['fr_pano_bloques_izq']}</div>
            <div style="width: {center['pct']}%; text-align: center;">{t['fr_pano_bloques_antisistema']}</div>
            <div style="width: {right['pct']}%; text-align: right;">{t['fr_pano_bloques_der']}</div>
        </div>

        <div class="blocks-bar-wrap">
            <div class="blocks-midlabel">50%</div>
            <div class="blocks-midline"></div>
            <div class="blocks-bar">
                <div style="width: {left['pct']}%; background: {COLOR_LEFT};">{left['pct']:.2f}%</div>
                <div style="width: {center['pct']}%; background: {COLOR_CENTER};">{center['pct']:.2f}%</div>
                <div style="width: {right['pct']}%; background: {COLOR_RIGHT};">{right['pct']:.2f}%</div>
            </div>
        </div>

        <div class="blocks-details">
            <div class="blocks-detail" style="width: {left['pct']}%; text-align: left;">
                <div class="blocks-cands">Jara + Artés + ME-O</div>
                <div class="blocks-votes">{t['fr_pano_bloques_votos'].format(n=_fmt_number(left['votes']))}</div>
            </div>
            <div class="blocks-detail" style="width: {center['pct']}%; text-align: center;">
                <div class="blocks-cands">Parisi + Mayne-Nicholls</div>
                <div class="blocks-votes">{t['fr_pano_bloques_votos'].format(n=_fmt_number(center['votes']))}</div>
            </div>
            <div class="blocks-detail" style="width: {right['pct']}%; text-align: right;">
                <div class="blocks-cands">Kast + Kaiser + Matthei</div>
                <div class="blocks-votes">{t['fr_pano_bloques_votos'].format(n=_fmt_number(right['votes']))}</div>
            </div>
        </div>

        <div class="blocks-legend">
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_LEFT};"></span>{t['fr_pano_bloques_izq_legend']}</div>
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_CENTER};"></span>{t['fr_pano_bloques_antisistema_legend']}</div>
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_RIGHT};"></span>{t['fr_pano_bloques_der_legend']}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 5 — TOP COMMUNES PER CANDIDATE
# ============================================================================
def _render_top_communes_candidate(
    df: pd.DataFrame,
    pct_col: str,
    votes_col: str,
    name: str,
    t: dict,
    top_n: int = 15,
):
    if pct_col not in df.columns or votes_col not in df.columns:
        st.info(t["fr_pano_no_cols_cand"].format(name=name))
        return

    df_work = df.copy()
    df_work["_winner"] = _compute_winner(df_work)
    df_filtered = df_work[df_work["casted_votes"] >= MIN_CASTED_VOTES].copy()
    sub = df_filtered.nlargest(top_n, pct_col).copy().reset_index(drop=True)

    rows_html = ""
    for i, row in sub.iterrows():
        rank = i + 1
        commune = str(row.get("commune_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(row.get("region_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        votes = _fmt_number(row[votes_col])
        pct = f"{row[pct_col]:.2f}%"

        if row["_winner"] == name:
            result_pill = (
                f'<span class="pa-res-pill" '
                f'style="background:{COLOR_POSITIVE}1A; color:{COLOR_POSITIVE}; '
                f'border:1px solid {COLOR_POSITIVE}40;">'
                f'{t["fr_pano_th_ganador"]}</span>'
            )
        else:
            result_pill = (
                f'<span class="pa-res-pill" '
                f'style="background:{COLOR_NEUTRAL_INDICATOR}; '
                f'color:#6b7280; border:1px solid #E0DED8;">—</span>'
            )

        rows_html += (
            f"<tr>"
            f"<td style=\"color:#9a9a9a; text-align:center;\">{rank}</td>"
            f"<td style=\"font-weight:400; color:#333333;\">{commune}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{region}</td>"
            f"<td style=\"text-align:right; color:#666;\">{votes}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{pct}</td>"
            f"<td style=\"text-align:center;\">{result_pill}</td>"
            f"</tr>"
        )

    html = _table_css("pa-tabla-candidato") + f"""
    <style>
        .pa-res-pill {{ display: inline-block; padding: 2px 9px; border-radius: 6px; font-size: 8pt; font-weight: 600; white-space: nowrap; min-width: 36px; text-align: center; }}
    </style>
    <div class="pa-tabla-candidato" style="max-width:720px;">
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>{t['fr_pano_th_comuna']}</th>
                    <th>{t['fr_pano_th_region']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_votos']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th style="text-align:center;">{t['fr_pano_th_ganador']}</th>
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


def _render_top_candidates_section(df: pd.DataFrame, t: dict, top_n: int = 15):
    render_section_subtitle(t["fr_pano_sub_top_comunas"])

    for cand in TOP_CANDIDATES:
        color = _get_candidate_color(cand["name"])
        # Title with dynamic candidate color — must stay inline.
        st.markdown(
            f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 12pt; font-weight: 700; color: {color}; margin-top: 16px; margin-bottom: 10px;\">{cand['name']}</div>",
            unsafe_allow_html=True,
        )
        _render_top_communes_candidate(df, cand["pct_col"], cand["votes_col"], cand["name"], t, top_n=top_n)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 6 — COMMUNES WON
# ============================================================================
def _render_communes_won(df: pd.DataFrame, t: dict):
    vote_cols = [c for c in VOTE_COLS_TO_NAMES if c in df.columns]
    if not vote_cols:
        st.info(t["fr_pano_no_votes_cols"])
        return

    df_work = df.copy()
    df_work["_winner"] = df_work[vote_cols].idxmax(axis=1).map(VOTE_COLS_TO_NAMES)

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
        f"<th style=\"text-align:center;\">{str(m).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</th>"
        for m in pivot.columns
    )
    header_cols += f"<th style=\"text-align:center;\">{t['fr_pano_th_total']}</th>"

    rows_html = ""
    for cand, row in pivot.iterrows():
        candidate_cell = _candidate_cell(cand)
        total = int(row.sum())

        cells = ""
        for m in pivot.columns:
            val = int(row[m])
            if val == 0:
                cells += f"<td style=\"text-align:center; color:{COLOR_NEUTRAL_INDICATOR};\">·</td>"
            else:
                cells += f"<td style=\"text-align:center; color:#333;\">{val}</td>"

        cells += f"<td style=\"text-align:center; font-weight:700; color:#111827; border-left:1px solid #e0e0e0 !important;\">{total}</td>"

        rows_html += (
            f"<tr>"
            f"<td>{candidate_cell}</td>"
            f"{cells}"
            f"</tr>"
        )

    totals = pivot.sum(axis=0)
    total_general = int(totals.sum())
    total_cells = "".join(
        f"<td style=\"text-align:center; font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important;\">{int(totals[m])}</td>"
        for m in pivot.columns
    )
    total_cells += f"<td style=\"text-align:center; font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important; border-left:1px solid #e0e0e0 !important;\">{total_general}</td>"

    rows_html += (
        f"<tr>"
        f"<td style=\"font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important;\">{t['fr_pano_th_total']}</td>"
        f"{total_cells}"
        f"</tr>"
    )

    html = _table_css("pa-tabla-macro") + f"""
    <div class="pa-tabla-macro">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_pano_th_candidato']}</th>
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
# SECTION NO. 7 — REGIONAL WINNERS
# ============================================================================
def _render_regional_winners(df: pd.DataFrame, t: dict):
    cand_keys = [
        ("jara_votes", "Jeannette Jara"),
        ("kast_votes", "José Antonio Kast"),
        ("parisi_votes", "Franco Parisi"),
        ("kaiser_votes", "Johannes Kaiser"),
        ("matthei_votes", "Evelyn Matthei"),
    ]
    vote_cols = [c for c, _ in cand_keys if c in df.columns]
    if not vote_cols or "region_name" not in df.columns:
        st.info(t["fr_pano_no_data_regionales"])
        return

    key_to_name = {c: n for c, n in cand_keys}

    agg_cols = {c: "sum" for c in vote_cols}
    agg_cols["casted_votes"] = "sum"
    agg_cols["blank_votes"] = "sum"
    agg_cols["null_votes"] = "sum"

    region_metrics = df.groupby("region_name", as_index=False).agg(agg_cols).copy()
    region_metrics["valid_votes"] = (
        region_metrics["casted_votes"]
        - region_metrics["blank_votes"]
        - region_metrics["null_votes"]
    ).replace(0, 1)

    for c in vote_cols:
        region_metrics[f"{c}_pct"] = (
            region_metrics[c] / region_metrics["valid_votes"] * 100
        )

    if "region_order" in df.columns:
        order_map = (
            df[["region_name", "region_order"]]
            .dropna()
            .drop_duplicates()
            .set_index("region_name")["region_order"]
            .to_dict()
        )
        region_metrics["_order"] = region_metrics["region_name"].map(order_map).fillna(9999)
        region_metrics = region_metrics.sort_values("_order").drop(columns="_order")
    else:
        region_metrics = region_metrics.sort_values("region_name")

    region_metrics = region_metrics.reset_index(drop=True)

    rows_html = ""
    for _, row in region_metrics.iterrows():
        region = str(row["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        ranking = sorted(
            [(key_to_name[c], row[f"{c}_pct"]) for c in vote_cols],
            key=lambda x: x[1],
            reverse=True,
        )
        winner_name, winner_pct = ranking[0]
        runner_name, runner_pct = ranking[1]
        margin = winner_pct - runner_pct

        w_color = _get_candidate_color(winner_name)
        bar_width = min(100, margin * 3)

        winner_cell = _candidate_cell(winner_name)
        runner_cell = _candidate_cell(runner_name)

        rows_html += (
            f"<tr>"
            f"<td style=\"color:#333;\">{region}</td>"
            f"<td>{winner_cell}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{winner_pct:.2f}%</td>"
            f"<td>{runner_cell}</td>"
            f"<td style=\"text-align:right; color:#666;\">{runner_pct:.2f}%</td>"
            f"<td style=\"text-align:right; color:{w_color};\">{margin:.2f} pp</td>"
            f"<td style=\"width:140px;\"><div style=\"background:#f0f0f0; border-radius:3px; height:8px; width:100%;\"><div style=\"background:{w_color}; height:8px; width:{bar_width}%; border-radius:3px;\"></div></div></td>"
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
# SECTION NO. 8 — VOTE IN REGIONAL CAPITALS
# ============================================================================
def _render_regional_capitals(df: pd.DataFrame, t: dict):
    cand_keys = [
        ("jara_pct", "Jeannette Jara"),
        ("kast_pct", "José Antonio Kast"),
        ("parisi_pct", "Franco Parisi"),
        ("kaiser_pct", "Johannes Kaiser"),
        ("matthei_pct", "Evelyn Matthei"),
    ]
    pct_cols = [c for c, _ in cand_keys if c in df.columns]
    if not pct_cols or "commune_name" not in df.columns or "region_name" not in df.columns:
        st.info(t["fr_pano_no_data_capitales"])
        return

    cap_norm_map = {_norm_commune(c): c for c in REGIONAL_CAPITALS}
    df_work = df.copy()
    df_work["_commune_norm"] = df_work["commune_name"].apply(_norm_commune)
    capitals_df = df_work[df_work["_commune_norm"].isin(cap_norm_map.keys())].copy()
    capitals_df["_capital_display"] = capitals_df["_commune_norm"].map(cap_norm_map)

    if capitals_df.empty:
        st.info(t["fr_pano_no_capitales_found"])
        return

    if "region_order" in capitals_df.columns:
        capitals_df = capitals_df.sort_values(["region_order", "_capital_display"])
    else:
        capitals_df = capitals_df.sort_values("_capital_display")

    capitals_df = capitals_df.reset_index(drop=True)

    key_to_name = {c: n for c, n in cand_keys}

    rows_html = ""
    for _, row in capitals_df.iterrows():
        capital = str(row["_capital_display"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(row.get("region_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        ranking = sorted(
            [(key_to_name[c], float(row[c])) for c in pct_cols],
            key=lambda x: x[1],
            reverse=True,
        )
        winner_name, winner_pct = ranking[0]
        runner_name, runner_pct = ranking[1]
        margin = winner_pct - runner_pct

        w_color = _get_candidate_color(winner_name)
        bar_width = min(100, margin * 3)

        winner_cell = _candidate_cell(winner_name)
        runner_cell = _candidate_cell(runner_name)

        rows_html += (
            f"<tr>"
            f"<td style=\"font-weight:400; color:#333333;\">{capital}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{region}</td>"
            f"<td>{winner_cell}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{winner_pct:.2f}%</td>"
            f"<td>{runner_cell}</td>"
            f"<td style=\"text-align:right; color:#666;\">{runner_pct:.2f}%</td>"
            f"<td style=\"text-align:right; color:{w_color};\">{margin:.2f} pp</td>"
            f"<td style=\"width:120px;\"><div style=\"background:#f0f0f0; border-radius:3px; height:8px; width:100%;\"><div style=\"background:{w_color}; height:8px; width:{bar_width}%; border-radius:3px;\"></div></div></td>"
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
# SECTION NO. 9 — VOTE BY COMMUNE SIZE
# ============================================================================
def _render_vote_by_commune_size(df: pd.DataFrame, t: dict):
    if "population" not in df.columns:
        st.info(t["fr_pano_no_population"])
        return

    cand_keys = [
        ("jara_votes", "Jeannette Jara"),
        ("kast_votes", "José Antonio Kast"),
        ("parisi_votes", "Franco Parisi"),
        ("kaiser_votes", "Johannes Kaiser"),
        ("matthei_votes", "Evelyn Matthei"),
    ]
    vote_cols = [c for c, _ in cand_keys if c in df.columns]
    if not vote_cols:
        st.info(t["fr_pano_no_votes_cols"])
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

        valid = (
            int(sub["casted_votes"].sum())
            - int(sub["null_votes"].sum())
            - int(sub["blank_votes"].sum())
        )
        if valid <= 0:
            continue

        segments = []
        for col, name in cand_keys:
            if col not in sub.columns:
                continue
            votes = int(sub[col].sum())
            pct = votes / valid * 100
            segments.append({
                "name": name,
                "pct": pct,
                "color": _get_candidate_color(name),
            })

        n_communes = len(sub)
        pct_pop = sub["population"].sum() / total_pop_national * 100

        visible_segments = [s for s in segments if s["pct"] >= 0.3]

        bar = ""
        for idx, s in enumerate(visible_segments):
            is_first = idx == 0
            is_last = idx == len(visible_segments) - 1
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
                <div class="tramo-meta">{t['fr_pano_tramo_meta'].format(n=n_communes, pct=f"{pct_pop:.1f}")}</div>
            </div>
            <div class="tramo-bar-wrap">
                <div class="tramo-midline"></div>
                <div class="tramo-bar">{bar}</div>
            </div>
        </div>
        """

    legend_items = ""
    for _, name in cand_keys:
        color = _get_candidate_color(name)
        legend_items += (
            f"<div class=\"legend-item\">"
            f"<span class=\"legend-dot\" style=\"background:{color};\"></span>"
            f"{name}"
            f"</div>"
        )

    html = _TRAMOS_CSS + f"""
    <div class="tramos-wrap">
        {blocks_html}
        <div class="tramos-legend">
            {legend_items}
        </div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 10 — SECOND ROUND: RECOVERABLE COMMUNES
# ============================================================================
def _render_recoverable_communes(df: pd.DataFrame, t: dict):
    required = ["casted_votes", "jara_votes", "kast_votes",
                "jara_pct", "kast_pct", "commune_name", "region_name"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.info(t["fr_pano_missing_cols"].format(cols=missing))
        return

    df_work = df.copy()
    df_work["valid_votes"] = (
        df_work["casted_votes"] - df_work["null_votes"] - df_work["blank_votes"]
    )
    df_work["jara_abs"] = df_work["jara_votes"].astype(float)
    df_work["kast_abs"] = df_work["kast_votes"].astype(float)
    df_work["diff"] = (df_work["jara_abs"] - df_work["kast_abs"]).abs()

    close = df_work[df_work["diff"] < RECOVERABLE_THRESHOLD].copy()
    if close.empty:
        st.info(t["fr_pano_no_margin_1000"])
        return

    close["winner"] = close.apply(
        lambda r: "Jeannette Jara" if r["jara_abs"] > r["kast_abs"] else "José Antonio Kast",
        axis=1,
    )
    close["loser"] = close["winner"].apply(
        lambda w: "José Antonio Kast" if w == "Jeannette Jara" else "Jeannette Jara"
    )
    close["votes_needed"] = close["diff"].round(0).astype(int)

    if "region_order" in close.columns:
        close = close.sort_values(["region_order", "commune_name"])
    else:
        close = close.sort_values("commune_name")

    close = close.reset_index(drop=True)

    filter_choice = st.radio(
        t["fr_pano_radio_label"],
        [t["fr_pano_radio_ambos"], t["fr_pano_radio_jara"], t["fr_pano_radio_kast"]],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="filtro_recuperables",
    )

    if filter_choice == t["fr_pano_radio_jara"]:
        candidates_to_show = ["Jeannette Jara"]
    elif filter_choice == t["fr_pano_radio_kast"]:
        candidates_to_show = ["José Antonio Kast"]
    else:
        candidates_to_show = ["Jeannette Jara", "José Antonio Kast"]

    fig = go.Figure()

    for cand in candidates_to_show:
        sub = close[close["loser"] == cand]
        if sub.empty:
            continue
        color = _get_candidate_color(cand)
        customdata = sub[["commune_name", "region_name", "votes_needed", "casted_votes", "loser"]].values

        fig.add_trace(go.Scatter(
            x=sub["votes_needed"],
            y=sub["casted_votes"],
            mode="markers",
            name=cand,
            marker=dict(
                color=color,
                size=12,
                line=dict(color="white", width=1.5),
                opacity=0.85,
            ),
            customdata=customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                f"{t['fr_pano_scatter_lost'].format(cand='')}%{{customdata[4]}}<br>"
                f"{t['fr_pano_scatter_margin'].format(n='')}%{{customdata[2]}}<br>"
                f"{t['fr_pano_scatter_casted'].format(n='')}%{{customdata[3]:,}}"
                "<extra></extra>"
            ),
        ))

    fig.add_vline(
        x=RECOVERABLE_THRESHOLD / 2,
        line=dict(color=COLOR_NEUTRAL_INDICATOR, width=1, dash="dash"),
    )

    fig.update_layout(
        xaxis=dict(
            title=dict(
                text=t["fr_pano_scatter_xaxis"],
                font=dict(size=11, color="#6b7280", family="Liberation Sans, Arial, sans-serif"),
            ),
            showgrid=True,
            gridcolor="#f0f0f0",
            tickfont=dict(size=10, color="#6b7280", family="Liberation Sans, Arial, sans-serif"),
            range=[0, RECOVERABLE_THRESHOLD * 1.05],
        ),
        yaxis=dict(
            title=dict(
                text=t["fr_pano_scatter_yaxis"],
                font=dict(size=11, color="#6b7280", family="Liberation Sans, Arial, sans-serif"),
            ),
            showgrid=True,
            gridcolor="#f0f0f0",
            tickfont=dict(size=10, color="#6b7280", family="Liberation Sans, Arial, sans-serif"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=10, color="#333", family="Liberation Sans, Arial, sans-serif"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        margin=dict(l=60, r=30, t=40, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        height=520,
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#e0e0e0",
            font=dict(size=11, family="Liberation Sans, Arial, sans-serif"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    def _difficulty(total):
        if total < 5000:
            return t["fr_pano_diff_menor"]
        if total < 20000:
            return t["fr_pano_diff_moderado"]
        return t["fr_pano_diff_significativo"]

    col1, col2 = st.columns(2)
    for col, cand in zip([col1, col2], ["Jeannette Jara", "José Antonio Kast"]):
        sub = close[close["loser"] == cand]
        with col:
            color = _get_candidate_color(cand)
            n = len(sub)
            total_votes = int(sub["votes_needed"].sum())
            avg = int(sub["votes_needed"].mean()) if n else 0
            st.markdown(
                _clean_html(f"""
                <div style="border:1px solid #e0e0e0; border-radius:10px; padding:14px 16px; background:white; box-shadow:0 2px 4px rgba(0,0,0,0.05); font-family:'Liberation Sans',Arial,sans-serif;">
                    <div style="font-size:10pt; color:{color}; font-weight:700; margin-bottom:8px;">{t['fr_pano_scatter_lost'].format(cand=cand)}</div>
                    <div style="font-size:9pt; color:#6b7280;">{t['fr_pano_card_recuperables']}</div>
                    <div style="font-size:15pt; font-weight:700; color:#111827;">{n}</div>
                    <div style="font-size:9pt; color:#6b7280; margin-top:8px;">{t['fr_pano_card_total_revertir']}</div>
                    <div style="font-size:15pt; font-weight:700; color:#111827;">{_fmt_number(total_votes)}</div>
                    <div style="font-size:9pt; color:#6b7280; margin-top:8px;">{t['fr_pano_card_prom_comuna']}</div>
                    <div style="font-size:13pt; font-weight:600; color:#333;">{_fmt_number(avg)} {t['votes']}</div>
                    <div style="font-size:9pt; color:#6b7280; margin-top:8px;">{_difficulty(total_votes)}</div>
                </div>
                """),
                unsafe_allow_html=True,
            )


# ============================================================================
# SECTION NO. 11 — ANTI-SYSTEM VOTE: FRANCO PARISI
# ============================================================================
def _classify_parisi_intensity(pct: float) -> str:
    if pct > 40:
        return "> 40%"
    if pct >= 35:
        return "35% – 40%"
    if pct >= 30:
        return "30% – 35%"
    if pct >= 20:
        return "20% – 30%"
    return "< 20%"


def _render_parisi_top_bottom_table(
    sub_df: pd.DataFrame,
    t: dict,
    show_macrozone: bool = False,
):
    rows_html = ""
    for i, row in sub_df.iterrows():
        rank = i + 1
        commune = str(row.get("commune_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(row.get("region_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        macro = str(row.get("macrozone", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if show_macrozone else ""
        p_parisi = f"{float(row['parisi_pct']):.2f}%"
        p_jara = f"{float(row['jara_pct']):.2f}%"
        p_kast = f"{float(row['kast_pct']):.2f}%"
        winner_full = str(row.get("_winner", "No data"))

        candidate_cell = _candidate_cell(winner_full)
        macrozone_cell = f"<td style=\"color:#6b7280; font-size:9.5pt;\">{macro}</td>" if show_macrozone else ""

        rows_html += (
            f"<tr>"
            f"<td style=\"color:#9a9a9a; text-align:center;\">{rank}</td>"
            f"<td style=\"font-weight:400; color:#333333;\">{commune}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{region}</td>"
            f"{macrozone_cell}"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{p_parisi}</td>"
            f"<td style=\"text-align:right; color:#666;\">{p_jara}</td>"
            f"<td style=\"text-align:right; color:#666;\">{p_kast}</td>"
            f"<td>{candidate_cell}</td>"
            f"</tr>"
        )

    macrozone_header = f"<th>{t['fr_pano_th_macrozone']}</th>" if show_macrozone else ""

    html = _table_css("pa-tabla-parisi-tb") + f"""
    <div class="pa-tabla-parisi-tb">
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>{t['fr_pano_th_comuna']}</th>
                    <th>{t['fr_pano_th_region']}</th>
                    {macrozone_header}
                    <th style="text-align:right;">{t['fr_pano_th_pct_parisi']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_pct_jara']}</th>
                    <th style="text-align:right;">{t['fr_pano_th_pct_kast']}</th>
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


def _render_anti_system(df: pd.DataFrame, t: dict):
    if "parisi_pct" not in df.columns:
        st.info(t["fr_pano_no_parisi_pct"])
        return

    df_work = df.copy()
    df_work["parisi_pct"] = pd.to_numeric(df_work["parisi_pct"], errors="coerce").fillna(0)
    df_work["_intensity"] = df_work["parisi_pct"].apply(_classify_parisi_intensity)
    df_work["_winner"] = _compute_winner(df_work)

    range_counts = df_work["_intensity"].value_counts().reindex(INTENSITY_ORDER).fillna(0).astype(int)

    cards_html = ""
    for range_label in INTENSITY_ORDER:
        n = int(range_counts[range_label])
        category_label = t["fr_pano_parisi_cat_singular"] if n == 1 else t["fr_pano_parisi_cat_plural"]
        cards_html += (
            f"<div class=\"nb-card\">"
            f"<div class=\"nb-card-label\">{range_label}</div>"
            f"<div class=\"nb-card-value\">{n}</div>"
            f"<div class=\"nb-card-sub\">{category_label}</div>"
            f"</div>"
        )

    cards_block = _NB_CARD_CSS + f"""
    <div class="nb-cards">{cards_html}</div>
    """
    st.markdown(_clean_html(cards_block), unsafe_allow_html=True)

    if "macrozone" in df_work.columns and "macrozone_order" in df_work.columns:
        render_section_title(t["fr_pano_section_dist_macro"])

        macro_order = (
            df_work[["macrozone", "macrozone_order"]]
            .dropna()
            .drop_duplicates()
            .sort_values("macrozone_order")["macrozone"]
            .tolist()
        )

        pivot = pd.crosstab(df_work["macrozone"], df_work["_intensity"])
        pivot = pivot.reindex(index=macro_order, columns=INTENSITY_ORDER, fill_value=0).astype(int)

        header_cols = "".join(
            f"<th style=\"text-align:center;\">{r}</th>" for r in INTENSITY_ORDER
        )
        header_cols += f"<th style=\"text-align:center;\">{t['fr_pano_th_total']}</th>"

        rows_html = ""
        for macro in pivot.index:
            macro_esc = str(macro).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            cells = ""
            row_total = 0
            for r in INTENSITY_ORDER:
                val = int(pivot.loc[macro, r])
                row_total += val
                if val == 0:
                    cells += f"<td style=\"text-align:center; color:{COLOR_NEUTRAL_INDICATOR};\">·</td>"
                else:
                    cells += f"<td style=\"text-align:center; color:#333;\">{val}</td>"
            cells += f"<td style=\"text-align:center; font-weight:700; color:#111827; border-left:1px solid #e0e0e0 !important;\">{row_total}</td>"
            rows_html += (
                f"<tr>"
                f"<td style=\"font-weight:600; color:#111827;\">{macro_esc}</td>"
                f"{cells}"
                f"</tr>"
            )

        totals = pivot.sum(axis=0)
        total_general = int(totals.sum())
        total_cells = "".join(
            f"<td style=\"text-align:center; font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important;\">{int(totals[r])}</td>"
            for r in INTENSITY_ORDER
        )
        total_cells += f"<td style=\"text-align:center; font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important; border-left:1px solid #e0e0e0 !important;\">{total_general}</td>"
        rows_html += (
            f"<tr>"
            f"<td style=\"font-weight:700; color:#111827; border-top:1px solid #e0e0e0 !important;\">{t['fr_pano_th_total']}</td>"
            f"{total_cells}"
            f"</tr>"
        )

        html_macro = _table_css("pa-tabla-parisi-macro") + f"""
        <div class="pa-tabla-parisi-macro">
            <table>
                <thead>
                    <tr>
                        <th>{t['fr_pano_th_macrozone']}</th>
                        {header_cols}
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(_clean_html(html_macro), unsafe_allow_html=True)
        _table_gap()

    columns_to_show = ["commune_name", "region_name"]
    if "macrozone" in df_work.columns:
        columns_to_show.append("macrozone")
    columns_to_show += ["parisi_pct", "jara_pct", "kast_pct", "_winner"]

    top10 = df_work.nlargest(10, "parisi_pct")[columns_to_show].reset_index(drop=True)
    bottom10 = df_work.nsmallest(10, "parisi_pct")[columns_to_show].reset_index(drop=True)

    render_section_title(t["fr_pano_section_parisi_top"])
    _render_parisi_top_bottom_table(top10, t, show_macrozone=("macrozone" in df_work.columns))

    render_section_title(t["fr_pano_section_parisi_bottom"])
    _render_parisi_top_bottom_table(bottom10, t, show_macrozone=("macrozone" in df_work.columns))


# ============================================================================
# SECTION NO. 12 — KAISER: THE NEW LIBERTARIAN RIGHT
# ============================================================================
def _render_kaiser(df: pd.DataFrame, t: dict):
    if "kaiser_votes" not in df.columns:
        st.info(t["fr_pano_no_kaiser_cols"])
        return

    total_valid = (
        int(df["casted_votes"].sum())
        - int(df["null_votes"].sum())
        - int(df["blank_votes"].sum())
    )
    kaiser_votes = int(df["kaiser_votes"].sum())
    kaiser_pct = (kaiser_votes / total_valid * 100) if total_valid else 0

    df_work = df.copy()
    df_work["_winner"] = _compute_winner(df_work)
    kaiser_won = int((df_work["_winner"] == "Johannes Kaiser").sum())

    # ---- Cards ----
    cards_html = _KAISER_CARD_CSS + f"""
    <div class="kaiser-cards">
        <div class="kaiser-card">
            <div class="kaiser-card-label">{t['fr_pano_kaiser_card_votos']}</div>
            <div class="kaiser-card-value">{_fmt_number(kaiser_votes)}</div>
            <div class="kaiser-card-sub">{t['fr_pano_kaiser_val_pct_validos'].format(pct=f"{kaiser_pct:.2f}")}</div>
        </div>
        <div class="kaiser-card">
            <div class="kaiser-card-label">{t['fr_pano_kaiser_card_comunas']}</div>
            <div class="kaiser-card-value">{kaiser_won}</div>
            <div class="kaiser-card-sub">{t['fr_pano_kaiser_val_de_comunas']}</div>
        </div>
        <div class="kaiser-card">
            <div class="kaiser-card-label">{t['fr_pano_kaiser_card_posicion']}</div>
            <div class="kaiser-card-value">{t['fr_pano_kaiser_val_posicion']}</div>
            <div class="kaiser-card-sub">{t['fr_pano_kaiser_val_de_candidatos']}</div>
        </div>
        <div class="kaiser-card">
            <div class="kaiser-card-label">{t['fr_pano_kaiser_card_bloque']}</div>
            <div class="kaiser-card-value" style="font-size:13pt;">{t['fr_pano_kaiser_val_bloque']}</div>
            <div class="kaiser-card-sub">{t['fr_pano_kaiser_val_bloque_sub']}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ---- Distribution by macrozone ----
    if "macrozone" in df_work.columns and "macrozone_order" in df_work.columns:
        render_section_title(t["fr_pano_section_kaiser_macro"])

        df_work["valid_votes"] = (
            df_work["casted_votes"] - df_work["null_votes"] - df_work["blank_votes"]
        )

        macro = df_work.groupby(["macrozone", "macrozone_order"], as_index=False).agg(
            valid=("valid_votes", "sum"),
            kaiser=("kaiser_votes", "sum"),
            kast=("kast_votes", "sum"),
            matthei=("matthei_votes", "sum"),
        )
        macro["kaiser_pct"] = macro["kaiser"] / macro["valid"] * 100
        macro["kast_pct"] = macro["kast"] / macro["valid"] * 100
        macro["matthei_pct"] = macro["matthei"] / macro["valid"] * 100
        macro = macro.sort_values("macrozone_order").reset_index(drop=True)

        rows_html = ""
        for _, r in macro.iterrows():
            rows_html += (
                f"<tr>"
                f"<td style=\"font-weight:600; color:#333;\">{r['macrozone']}</td>"
                f"<td style=\"text-align:right; color:#666;\">{_fmt_number(r['kaiser'])}</td>"
                f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{r['kaiser_pct']:.2f}%</td>"
                f"<td style=\"text-align:right; color:#666;\">{r['kast_pct']:.2f}%</td>"
                f"<td style=\"text-align:right; color:#666;\">{r['matthei_pct']:.2f}%</td>"
                f"</tr>"
            )

        html_macro = _table_css("pa-tabla-kaiser-macro") + f"""
        <div class="pa-tabla-kaiser-macro">
            <table>
                <thead>
                    <tr>
                        <th>{t['fr_pano_th_macrozone']}</th>
                        <th style="text-align:right;">{t['fr_pano_kaiser_th_votos']}</th>
                        <th style="text-align:right;">{t['fr_pano_kaiser_th_pct']}</th>
                        <th style="text-align:right;">{t['fr_pano_kaiser_th_kast']}</th>
                        <th style="text-align:right;">{t['fr_pano_kaiser_th_matthei']}</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(_clean_html(html_macro), unsafe_allow_html=True)
        _table_gap()

        render_section_subtitle(t["fr_pano_sub_kaiser_comp"])

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ---- Top 10 communes where Kaiser was strongest ----
    df_work["kaiser_pct"] = pd.to_numeric(df_work.get("kaiser_pct", 0), errors="coerce").fillna(0)
    top10 = df_work.nlargest(10, "kaiser_pct").copy().reset_index(drop=True)

    render_section_title(t["fr_pano_section_kaiser_top"])

    rows_top_html = ""
    for i, r in top10.iterrows():
        rank = i + 1
        commune = str(r.get("commune_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        kaiser_pct = f"{float(r.get('kaiser_pct', 0)):.2f}%"
        kast_pct = f"{float(r.get('kast_pct', 0)):.2f}%"
        matthei_pct = f"{float(r.get('matthei_pct', 0)):.2f}%"
        winner_full = str(r.get("_winner", "No data"))
        candidate_cell = _candidate_cell(winner_full)

        rows_top_html += (
            f"<tr>"
            f"<td style=\"color:#9a9a9a; text-align:center;\">{rank}</td>"
            f"<td style=\"font-weight:400; color:#333333;\">{commune}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{region}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{kaiser_pct}</td>"
            f"<td style=\"text-align:right; color:#666;\">{kast_pct}</td>"
            f"<td style=\"text-align:right; color:#666;\">{matthei_pct}</td>"
            f"<td>{candidate_cell}</td>"
            f"</tr>"
        )

    html_top = _table_css("pa-tabla-kaiser-top") + f"""
    <div class="pa-tabla-kaiser-top">
        <table>
            <thead>
                <tr>
                    <th style="text-align:center;">#</th>
                    <th>{t['fr_pano_th_comuna']}</th>
                    <th>{t['fr_pano_th_region']}</th>
                    <th style="text-align:right;">{t['fr_pano_kaiser_th_pct']}</th>
                    <th style="text-align:right;">{t['fr_pano_kaiser_th_kast']}</th>
                    <th style="text-align:right;">{t['fr_pano_kaiser_th_matthei']}</th>
                    <th>{t['fr_pano_th_ganador']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_top_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_top), unsafe_allow_html=True)
    _table_gap()

    render_section_subtitle(t["fr_pano_sub_kaiser"])


# ============================================================================
# MAIN RENDER
# ============================================================================
def render(t: dict):
    render_view_title(t["fr_pano_view_title"])
    render_view_subtitle(t["fr_pano_view_subtitle"])

    try:
        with st.spinner(t["loading"]):
            df = load_fact_first_round_2025()
            dim = load_dim_commune()
            if "population" in dim.columns and "population" not in df.columns:
                df = df.merge(
                    dim[["commune_id", "population"]],
                    on="commune_id",
                    how="left",
                )

        render_section_title(t["fr_pano_section_participacion"])
        _render_national_participation(df, t)

        st.divider()

        with st.expander(t["fr_pano_exp_nulos"], expanded=False):
            _render_null_section(df, t)

        with st.expander(t["fr_pano_exp_blancos"], expanded=False):
            _render_blank_section(df, t)

        with st.expander(t["fr_pano_exp_resultados"], expanded=False):
            _render_national_results(df, t)

            render_section_title(t["fr_pano_section_bloques"])
            _render_ideological_blocks(df, t)

        with st.expander(t["fr_pano_exp_top_comunas"], expanded=False):
            _render_top_candidates_section(df, t, top_n=15)

        with st.expander(t["fr_pano_exp_comunas_ganadas"], expanded=False):
            render_section_subtitle(t["fr_pano_sub_comunas_ganadas"])
            _render_communes_won(df, t)

            st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
            render_section_title(t["fr_pano_section_comunas_macro"])
            _render_winners_by_macrozone(df, t)

        with st.expander(t["fr_pano_exp_ganadores_regionales"], expanded=False):
            render_section_subtitle(t["fr_pano_sub_ganadores_regionales"])
            _render_regional_winners(df, t)

        with st.expander(t["fr_pano_exp_capitales"], expanded=False):
            render_section_subtitle(t["fr_pano_sub_capitales"])
            _render_regional_capitals(df, t)

        with st.expander(t["fr_pano_exp_tamano_comuna"], expanded=False):
            render_section_subtitle(t["fr_pano_sub_tamano_comuna"])
            _render_vote_by_commune_size(df, t)

        with st.expander(t["fr_pano_exp_recuperables"], expanded=False):
            render_section_subtitle(t["fr_pano_sub_recuperables"])
            _render_recoverable_communes(df, t)

        with st.expander(t["fr_pano_exp_antisistema"], expanded=False):
            render_section_subtitle(t["fr_pano_sub_antisistema"])
            _render_anti_system(df, t)

        with st.expander(t["fr_pano_exp_kaiser"], expanded=False):
            render_section_subtitle(t["fr_pano_sub_kaiser"])
            _render_kaiser(df, t)

        _render_page_footer(t)

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)


# ============================================================================
# TECHNICAL DEBT
# ============================================================================
# This file contains two groups of user-facing strings still hardcoded in
# Spanish. They should be moved to translations.py (LANG["ES"] / LANG["EN"])
# in a future cleanup pass. Until then, they are kept as-is to avoid breaking
# the bilingual setup and to keep this refactor focused on identifier
# translation.
#
# 1. POPULATION_BRACKETS labels and subtitles:
#      "Grandes centros urbanos", "más de 200.000 hab.",
#      "Centros urbanos medios",  "100.000 – 199.999 hab.",
#      "Centros urbanos pequeños", "50.000 – 99.999 hab.",
#      "Rural-urbano",            "10.000 – 49.999 hab.",
#      "Rural",                   "menos de 10.000 hab."
#
# 2. Plotly hover labels in _plot_top_bar (label_map):
#      "Región", "Votos totales", "Votos válidos", "Votos nulos",
#      "Votos blancos", "% nulos", "% blancos", "Comuna".
#
# When these are moved, add the corresponding keys to translations.py with
# the prefix fr_pano_ and update the two call sites. No other code depends
# on them.
