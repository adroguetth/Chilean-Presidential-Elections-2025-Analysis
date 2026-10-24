"""
Second Round — Jeannette Jara Analysis
============================================================================
Candidate-specific analysis for Jara in the 2025 runoff.

Featured cards at the top (4 cards):
    1. Jara's votes in the runoff.
    2. Jara's % over valid votes in the runoff.
    3. Communes won by Jara in the runoff.
    4. Communes where Jara flipped the 2025 first round winner.

Sections (all collapsible):
    1. Territorial strongholds: communes where Jara got > 50% in the runoff.
    2. Flips: communes won by another candidate in the first round but won
       by Jara in the runoff.
    3. Stronghold expansion: top 20 communes where Jara grew the most in
       absolute votes between the first and second round.
    4. Geography of the vote: Jara's profile by macrozone (first round vs
       runoff).
    5. Urban-rural gradient: Jara's % by commune size (runoff).
    6. Urban-rural intensity: Jara's % by commune size × macrozone (runoff).
    7. Close losses: communes where Jara lost by ≤ 2 pp.
    8. Loss distribution by zone: how close losses are distributed across
       macrozones.
    9. Losses by zone and margin: heatmap of close losses by macrozone and
       margin bucket.
   10. Santiago elite: Jara's performance in Vitacura, Las Condes, and
       Lo Barnechea.
   11. Protest vote: how changes in null/blank votes correlate with changes
       in Jara's %.

Transformation helpers (clean_html, format_number, format_signed) are
imported from utils.html_helpers.
View and section titles live in components.titles.
Colors live in config.constants.

Notes
-----
- `TREND_GRAY` is imported from config.constants. The old name
  `GRIS_TENDENCIA` is still available as an alias but is not used here.
- `POPULATION_BRACKETS_JARA`, the `label_map` in `_plot_top_bar`, and the
  `bucket_*` variables in `_render_protest_vote` contain user-facing
  strings hardcoded in Spanish. They should be migrated to
  translations.py in a future cleanup pass. See the TECHNICAL DEBT block
  at the bottom of the file.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import (
    load_fact_first_round_2025,
    load_fact_second_round_2025,
    load_dim_commune,
)
from utils.html_helpers import (
    clean_html as _clean_html,
    format_number as _fmt_number,
    format_signed as _fmt_signed,
)
from config.constants import (
    COLOR_NEUTRAL_INDICATOR,
    TREND_GRAY,
    NEUTRAL_COLOR,
    MARGIN_SCALE_COLORS,
    HEATMAP_SCALE_PCT,
    HEATMAP_SCALE_COUNT,
    CANDIDATE_COLOR_VARIANTS,
    _get_candidate_color,
)
from components.titles import (
    render_view_title,
    render_section_title,
    render_section_subtitle,
)


# ============================================================================
# CONSTANTS
# ============================================================================
JARA_NAME = "Jeannette Jara"
JARA_COLOR = _get_candidate_color(JARA_NAME)
KAST_NAME = "José Antonio Kast"
KAST_COLOR = _get_candidate_color(KAST_NAME)

# Per-candidate color variants (single source: constants.py).
JARA_VARIANTS = CANDIDATE_COLOR_VARIANTS[JARA_NAME]
KAST_VARIANTS = CANDIDATE_COLOR_VARIANTS[KAST_NAME]

# Competitiveness pill colors (Kast blues).
COMP_ULTRA_TIGHT = KAST_VARIANTS["claro"]     # #3D76AC
COMP_COMPETITIVE = KAST_VARIANTS["oficial"]   # #243C5F

ZONE_ORDER = ["Norte Grande", "Norte Chico", "Centro", "Centro Sur", "Sur", "Patagonia"]
MACROZONE_ORDER = ZONE_ORDER
RANGE_ORDER = ["0-1%", "1-2%", "2-3%", "3-4%", "4-5%"]

WINNER_FR_DISPLAY = {
    "jara": "Jeannette Jara",
    "kast": "José Antonio Kast",
    "parisi": "Franco Parisi",
    "kaiser": "Johannes Kaiser",
    "matthei": "Evelyn Matthei",
    "mayne_nicholls": "Harold Mayne-Nicholls",
    "enriquez_ominami": "Marco Enríquez-Ominami",
    "artes": "Eduardo Artés",
}

# NOTE: labels and subtitles are user-facing strings hardcoded in Spanish.
# They should live in translations.py. See TECHNICAL DEBT at the bottom.
POPULATION_BRACKETS_JARA = [
    {"label": "Rural",                    "sub": "menos de 10.000 hab.",   "min": 0,       "max": 9_999},
    {"label": "Rural-urbano",             "sub": "10.000 – 49.999 hab.",   "min": 10_000,  "max": 49_999},
    {"label": "Centros urbanos pequeños", "sub": "50.000 – 99.999 hab.",   "min": 50_000,  "max": 99_999},
    {"label": "Centros urbanos medios",   "sub": "100.000 – 199.999 hab.", "min": 100_000, "max": 199_999},
    {"label": "Grandes centros urbanos",  "sub": "más de 200.000 hab.",     "min": 200_001, "max": None},
]


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

_FOOTER_CSS = """
<style>
    .page-footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; width: 100%; }
    .page-footer p { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; color: #9a9a9a; text-align: center; margin: 0; line-height: 1.4; }
</style>
"""

_STRONGHOLDS_BAR_CSS = """
<style>
    .jara-bast-bar-wrap { font-family: "Liberation Sans", Arial, sans-serif; margin-top: 8px; margin-bottom: 24px; }
    .jara-bast-bar { display: flex; height: 44px; width: 100%; border-radius: 6px; overflow: hidden; }
    .jara-bast-bar-seg { display: flex; align-items: center; justify-content: center; color: #ffffff; font-weight: 700; font-size: 13pt; line-height: 1; }
    .jara-bast-bar-labels { display: flex; justify-content: space-between; margin-top: 8px; font-size: 9.5pt; color: #6b7280; }
</style>
"""

_MACROZONE_PROFILE_CSS = """
<style>
    .mzp-wrap { font-family: "Liberation Sans", Arial, sans-serif; max-width: 960px; }
    .mzp-block { margin-bottom: 22px; }
    .mzp-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
    .mzp-title { font-size: 11pt; font-weight: 700; color: #111827; }
    .mzp-meta { font-size: 9pt; color: #6b7280; }
    .mzp-rows { display: flex; flex-direction: column; gap: 0; }
    .mzp-row { display: flex; align-items: center; gap: 10px; height: 32px; }
    .mzp-label { width: 72px; font-size: 9pt; color: #6b7280; text-align: right; flex-shrink: 0; }
    .mzp-bar-wrap { flex: 1; position: relative; }
    .mzp-bar { height: 100%; border-radius: 0; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; box-sizing: border-box; }
    .mzp-bar-1v { background: {ROJO_1V}; border-top-left-radius: 4px; }
    .mzp-bar-2v { background: {ROJO_2V}; border-bottom-left-radius: 4px; }
    .mzp-pct { color: #ffffff; font-size: 9.5pt; font-weight: 700; }
    .mzp-delta { width: 110px; font-size: 9.5pt; font-weight: 600; text-align: left; flex-shrink: 0; }
</style>
"""

_LOSS_DISTRIBUTION_CSS = """
<style>
    .tramos-wrap { font-family: "Liberation Sans", Arial, sans-serif; max-width: 940px; }
    .tramo-wrap { margin-bottom: 22px; }
    .tramo-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
    .tramo-label { font-size: 11pt; font-weight: 700; color: #111827; }
    .tramo-meta { font-size: 9pt; color: #6b7280; }
    .tramo-bar-wrap { position: relative; }
    .tramo-bar { display: flex; height: 34px; border-radius: 6px; overflow: hidden; width: 100%; box-sizing: border-box; isolation: isolate; }
    .tramo-seg { display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 10.5pt; flex-shrink: 0; box-sizing: border-box; overflow: hidden; }
    .tramo-seg-first { border-top-left-radius: 6px; border-bottom-left-radius: 6px; }
    .tramo-seg-last { border-top-right-radius: 6px; border-bottom-right-radius: 6px; }
    .tramo-midline { position: absolute; top: -6px; bottom: -6px; left: 50%; width: 0; border-left: 1px dashed #9ca3af; pointer-events: none; z-index: 2; }
    .tramos-leyenda { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 12px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 9pt; color: #333; }
    .legend-item { display: flex; align-items: center; gap: 8px; }
    .legend-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; flex-shrink: 0; }
</style>
"""


# ============================================================================
# LOCAL HELPERS — VISUAL FORMATTING
# ============================================================================
def _candidate_cell(name: str, escape: bool = True) -> str:
    """Color box + full name. Copied from panorama.py."""
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
    """6px gap below each table."""
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)


def _table_css(class_name: str) -> str:
    """Table CSS, identical to panorama.py."""
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


def _prepare_narrow_losses(df_sr: pd.DataFrame) -> pd.DataFrame:
    """Filter communes where Jara lost by ≤ 5 pp, with a margin bucket."""
    df = df_sr.copy()
    df["__valid"] = df["jara_votes"] + df["kast_votes"]
    df["__jara_pct"] = (df["jara_votes"] / df["__valid"].replace(0, 1) * 100)
    df["__kast_pct"] = (df["kast_votes"] / df["__valid"].replace(0, 1) * 100)
    df["__margin"] = df["__jara_pct"] - df["__kast_pct"]

    narrow = df[(df["__margin"] < 0) & (df["__margin"] >= -5)].copy()
    narrow["__margin_abs"] = narrow["__margin"].abs()

    def _get_margin_range(m: float) -> str:
        if m < 1:
            return "0-1%"
        elif m < 2:
            return "1-2%"
        elif m < 3:
            return "2-3%"
        elif m < 4:
            return "3-4%"
        else:
            return "4-5%"

    narrow["__margin_range"] = narrow["__margin_abs"].apply(_get_margin_range)
    return narrow


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
        "jara_fmt": "Votos Jara",
        "kast_fmt": "Votos Kast",
        "pop_fmt": "Población",
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
# SECTION NO. 1 — TERRITORIAL STRONGHOLDS
# ============================================================================
def _render_strongholds_bar(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the stacked bar: % of Jara's votes that came from strongholds
    vs the rest.
    """
    df = df_sr.copy()
    df["__valid"] = df["jara_votes"] + df["kast_votes"]
    df["__jara_pct"] = (df["jara_votes"] / df["__valid"].replace(0, 1) * 100)

    stronghold_mask = df["__jara_pct"] > 50
    stronghold_votes = int(df.loc[stronghold_mask, "jara_votes"].sum())
    total_votes = int(df["jara_votes"].sum())

    if total_votes == 0:
        return

    n_strongholds = int(stronghold_mask.sum())
    pct_strongholds = stronghold_votes / total_votes * 100
    pct_rest = 100 - pct_strongholds

    html = _STRONGHOLDS_BAR_CSS + f"""
    <div class="jara-bast-bar-wrap">
        <div class="jara-bast-bar">
            <div class="jara-bast-bar-seg" style="width:{pct_strongholds}%; background:{JARA_COLOR};">{pct_strongholds:.1f}%</div>
            <div class="jara-bast-bar-seg" style="width:{pct_rest}%; background:{COLOR_NEUTRAL_INDICATOR}; color:#333;">{pct_rest:.1f}%</div>
        </div>
        <div class="jara-bast-bar-labels">
            <span>{t['sr_jara_bar_bastiones_izq'].format(n=n_strongholds)}</span>
            <span>{t['sr_jara_bar_bastiones_der']}</span>
        </div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


def _render_strongholds(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the strongholds section: subtitle + stacked bar + table.

    Parameters
    ----------
    df_sr : pd.DataFrame
        Second round 2025 fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    df = df_sr.copy()
    df["__valid"] = df["jara_votes"] + df["kast_votes"]
    df["__jara_pct"] = (df["jara_votes"] / df["__valid"].replace(0, 1) * 100)

    sub = df[df["__jara_pct"] > 50].copy().sort_values("__jara_pct", ascending=False)
    total = len(sub)

    render_section_subtitle(t["sr_jara_sub_bastiones"].format(n=total))

    if sub.empty:
        st.info(t["sr_jara_no_data"])
        return

    _render_strongholds_bar(df_sr, t)

    rows_html = ""
    for _, r in sub.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        pct = f"{r['__jara_pct']:.2f}%"
        votes = _fmt_number(r["jara_votes"])
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{pct}</td>'
            f'<td style="text-align:right; color:{JARA_COLOR};">{votes}</td>'
            f"</tr>"
        )

    html = _table_css("jara-bast-table") + f"""
    <div class="jara-bast-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_jara_th_comuna']}</th>
                    <th>{t['sr_jara_th_region']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_pct_jara']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_votos_jara']}</th>
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
# SECTION NO. 2 — FLIPS
# ============================================================================
def _render_flips_jara(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the flips table: communes won by another candidate in the first
    round but won by Jara in the runoff.
    """
    fr = df_fr.copy()
    fr_cols = ["jara_pct", "kast_pct", "parisi_pct", "kaiser_pct",
               "matthei_pct", "mayne_nicholls_pct", "enriquez_ominami_pct", "artes_pct"]
    fr_cols = [c for c in fr_cols if c in fr.columns]
    fr["__winner_fr"] = fr[fr_cols].idxmax(axis=1).str.replace("_pct", "", regex=False)

    sr = df_sr.copy()
    sr["__winner_sr"] = sr.apply(
        lambda r: "jara" if r["jara_votes"] > r["kast_votes"] else "kast", axis=1
    )

    merged = fr[["commune_id", "commune_name", "region_name", "jara_pct", "__winner_fr"]].rename(
        columns={"jara_pct": "jara_pct_1v"}
    ).merge(
        sr[["commune_id", "jara_pct", "__winner_sr"]].rename(
            columns={"jara_pct": "jara_pct_2v"}
        ),
        on="commune_id",
        how="inner",
    )

    merged["__swing"] = (merged["jara_pct_2v"] - merged["jara_pct_1v"]).round(2)

    flipped = merged[
        (merged["__winner_fr"] != "jara") &
        (merged["__winner_sr"] == "jara")
    ].copy().sort_values("__swing", ascending=False).reset_index(drop=True)

    total = len(flipped)

    render_section_subtitle(t["sr_jara_sub_flips"].format(n=total))

    if flipped.empty:
        st.info(t["sr_jara_no_data"])
        return

    rows_html = ""
    for _, r in flipped.iterrows():
        winner_fr_name = WINNER_FR_DISPLAY.get(r["__winner_fr"], r["__winner_fr"])
        winner_cell = _candidate_cell(winner_fr_name)

        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        jara_1v = f"{r['jara_pct_1v']:.2f}%"
        jara_2v = f"{r['jara_pct_2v']:.2f}%"
        swing = f"+{r['__swing']:.2f} pp"

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f"<td>{winner_cell}</td>"
            f'<td style="text-align:right; color:#666;">{jara_1v}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{jara_2v}</td>'
            f'<td style="text-align:right; color:{JARA_COLOR};">{swing}</td>'
            f"</tr>"
        )

    html = _table_css("jara-flip-table") + f"""
    <div class="jara-flip-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_jara_th_comuna']}</th>
                    <th>{t['sr_jara_th_region']}</th>
                    <th>{t['sr_jara_th_ganador_1v']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_pct_jara_1v']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_pct_jara_2v']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_swing']}</th>
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
# SECTION NO. 3 — STRONGHOLD EXPANSION
# ============================================================================
def _render_strongholds_expansion(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the top-20 communes where Jara grew the most in absolute votes
    between the first and second round.
    """
    df = df_fr[["commune_id", "commune_name", "region_name", "jara_votes"]].copy()
    df = df.rename(columns={"jara_votes": "jara_votes_1v"})
    df = df.merge(
        df_sr[["commune_id", "jara_votes"]].rename(columns={"jara_votes": "jara_votes_2v"}),
        on="commune_id",
        how="inner",
    )

    df["__change"] = df["jara_votes_2v"] - df["jara_votes_1v"]
    df["__pct_change"] = (df["__change"] / df["jara_votes_1v"].replace(0, 1) * 100)

    top = df.nlargest(20, "__change").reset_index(drop=True)

    render_section_subtitle(t["sr_jara_sub_expansion"])

    rows_html = ""
    for _, r in top.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        v1 = _fmt_number(r["jara_votes_1v"])
        v2 = _fmt_number(r["jara_votes_2v"])
        change = f"+{_fmt_number(r['__change'])}"
        pct_change = f"+{r['__pct_change']:.1f}%"
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{v1}</td>'
            f'<td style="text-align:right; color:#666;">{v2}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{change}</td>'
            f'<td style="text-align:right; color:{JARA_COLOR};">{pct_change}</td>'
            f"</tr>"
        )

    html = _table_css("jara-exp-table") + f"""
    <div class="jara-exp-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_jara_th_comuna']}</th>
                    <th>{t['sr_jara_th_region']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_votos_1v']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_votos_2v']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_delta_votos']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_delta_pct']}</th>
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
# SECTION NO. 4 — MACROZONE PROFILE
# ============================================================================
def _render_macrozone_profile(df_fr: pd.DataFrame, df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """
    Render the macrozone profile: for each macrozone, two horizontal bars
    (first round and runoff) showing Jara's % over casted votes, plus the
    delta in pp.
    """
    fr = df_fr[["commune_id", "jara_votes", "casted_votes"]].rename(columns={
        "jara_votes": "jara_1v", "casted_votes": "casted_1v",
    })
    sr = df_sr[["commune_id", "jara_votes", "casted_votes"]].rename(columns={
        "jara_votes": "jara_2v", "casted_votes": "casted_2v",
    })

    df = fr.merge(sr, on="commune_id", how="inner")
    df = df.merge(
        dim[["commune_id", "macrozone", "macrozone_order"]],
        on="commune_id",
        how="left",
    )
    df = df.dropna(subset=["macrozone"]).copy()

    agg = df.groupby(["macrozone", "macrozone_order"], as_index=False).agg(
        communes=("commune_id", "count"),
        jara_1v=("jara_1v", "sum"),
        casted_1v=("casted_1v", "sum"),
        jara_2v=("jara_2v", "sum"),
        casted_2v=("casted_2v", "sum"),
    )
    agg["jara_pct_1v"] = agg["jara_1v"] / agg["casted_1v"].replace(0, 1) * 100
    agg["jara_pct_2v"] = agg["jara_2v"] / agg["casted_2v"].replace(0, 1) * 100
    agg["delta_pp"] = agg["jara_pct_2v"] - agg["jara_pct_1v"]

    agg = agg.sort_values("macrozone_order").reset_index(drop=True)

    if agg.empty:
        st.info(t["sr_jara_no_data_macrozone"])
        return

    max_pct = max(agg["jara_pct_1v"].max(), agg["jara_pct_2v"].max())
    scale_max = min(100, max(60, max_pct * 1.05))

    RED_1V = JARA_VARIANTS["intenso"]
    RED_2V = JARA_VARIANTS["oficial"]

    blocks_html = ""
    for _, r in agg.iterrows():
        macrozone = str(r["macrozone"])
        n_communes = int(r["communes"])
        p1 = float(r["jara_pct_1v"])
        p2 = float(r["jara_pct_2v"])
        delta = float(r["delta_pp"])

        w1 = p1 / scale_max * 100
        w2 = p2 / scale_max * 100

        delta_color = RED_2V if delta >= 0 else TREND_GRAY
        delta_sign = "+" if delta >= 0 else ""

        blocks_html += f"""
        <div class="mzp-block">
            <div class="mzp-header">
                <div class="mzp-title">{macrozone}</div>
                <div class="mzp-meta">{t['sr_jara_meta_comunas'].format(n=n_communes)}</div>
            </div>
            <div class="mzp-rows">
                <div class="mzp-row">
                    <div class="mzp-label">{t['sr_jara_label_1v']}</div>
                    <div class="mzp-bar-wrap">
                        <div class="mzp-bar mzp-bar-1v" style="width:{w1}%;">
                            <span class="mzp-pct">{p1:.1f}%</span>
                        </div>
                    </div>
                    <div class="mzp-delta"></div>
                </div>
                <div class="mzp-row">
                    <div class="mzp-label">{t['sr_jara_label_2v']}</div>
                    <div class="mzp-bar-wrap">
                        <div class="mzp-bar mzp-bar-2v" style="width:{w2}%;">
                            <span class="mzp-pct">{p2:.1f}%</span>
                        </div>
                    </div>
                    <div class="mzp-delta">
                        <span style="color:{delta_color};">Δ {delta_sign}{delta:.1f} pp</span>
                    </div>
                </div>
            </div>
        </div>
        """

    html = _MACROZONE_PROFILE_CSS.replace("{ROJO_1V}", RED_1V).replace("{ROJO_2V}", RED_2V) + f"""
    <div class="mzp-wrap">
        {blocks_html}
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 5 — JARA BY COMMUNE SIZE
# ============================================================================
def _render_jara_by_commune_size(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """
    Render the horizontal bar chart: Jara's % by commune size (runoff).
    The % is Jara / (Jara + Kast).
    """
    df = df_sr[["commune_id", "jara_votes", "kast_votes"]].copy()
    df = df.merge(dim[["commune_id", "population"]], on="commune_id", how="left")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df = df.dropna(subset=["population"]).copy()

    df["__valid"] = df["jara_votes"] + df["kast_votes"]

    def _classify(pop: float):
        for tr in POPULATION_BRACKETS_JARA:
            if tr["min"] is not None and pop < tr["min"]:
                continue
            if tr["max"] is not None and pop > tr["max"]:
                continue
            return tr["label"]
        return None

    df["__bracket"] = df["population"].apply(_classify)

    agg = df.groupby("__bracket", as_index=False).agg(
        communes=("commune_id", "count"),
        population=("population", "sum"),
        jara_votes=("jara_votes", "sum"),
        valid_votes=("__valid", "sum"),
    )
    agg["jara_pct"] = (agg["jara_votes"] / agg["valid_votes"].replace(0, 1) * 100).round(2)

    if agg.empty:
        st.info(t["sr_jara_no_data_population"])
        return

    sub_map = {tr["label"]: tr["sub"] for tr in POPULATION_BRACKETS_JARA}
    agg["zona"] = agg["__bracket"].apply(lambda x: f"{x} · {sub_map.get(x, '')}")

    agg["jara_fmt"] = agg["jara_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    agg["valid_fmt"] = agg["valid_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    agg["pop_fmt"] = agg["population"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    agg["winner"] = "Jara"

    render_section_subtitle(t["sr_jara_sub_size"])

    _plot_top_bar(
        plot_df=agg,
        t=t,
        value_col="jara_pct",
        label_col="zona",
        title="",
        xaxis_title=t["sr_jara_colorbar_pct_jara"] + " " + t["sr_jara_kpi_pct_validos"],
        value_fmt=lambda v: f"{v:.1f}%",
        extra_hover_cols=["jara_fmt", "valid_fmt", "pop_fmt"],
        height_per_bar=44,
        height_min=320,
        bar_color=JARA_COLOR,
        rounded=True,
        transparent_bg=True,
        font_boost=1.0,
    )


# ============================================================================
# SECTION NO. 6 — JARA SIZE × MACROZONE
# ============================================================================
def _compute_jara_size_x_macrozone(df_sr: pd.DataFrame, dim: pd.DataFrame):
    """
    Cross runoff votes with dim_commune (population, macrozone) and build
    a Commune-size × Macrozone matrix with Jara's % weighted by casted votes.
    """
    df = df_sr[["commune_id", "jara_votes", "casted_votes"]].copy()
    df = df.merge(
        dim[["commune_id", "population", "macrozone", "macrozone_order"]],
        on="commune_id",
        how="left",
    )
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df = df.dropna(subset=["population", "macrozone"]).copy()

    df["__valid"] = df["casted_votes"]

    def _classify(pop: float):
        for tr in POPULATION_BRACKETS_JARA:
            if tr["min"] is not None and pop < tr["min"]:
                continue
            if tr["max"] is not None and pop > tr["max"]:
                continue
            return tr["label"]
        return None

    df["__bracket"] = df["population"].apply(_classify)
    df = df.dropna(subset=["__bracket"])

    size_order = [tr["label"] for tr in POPULATION_BRACKETS_JARA]

    agg = df.groupby(["__bracket", "macrozone"], as_index=False).agg(
        jara_votes=("jara_votes", "sum"),
        valid_votes=("__valid", "sum"),
        communes=("commune_id", "count"),
    )
    agg["jara_pct"] = agg["jara_votes"] / agg["valid_votes"].replace(0, 1) * 100

    pivot = agg.pivot(index="__bracket", columns="macrozone", values="jara_pct")
    pivot = pivot.reindex(index=size_order, columns=MACROZONE_ORDER)

    pivot_n = agg.pivot(index="__bracket", columns="macrozone", values="communes")
    pivot_n = pivot_n.reindex(index=size_order, columns=MACROZONE_ORDER)

    return pivot, pivot_n


def _render_jara_size_x_macrozone(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """
    Render the heatmap: Commune size × Macrozone with Jara's % weighted by
    casted votes. White text on cells with Jara % >= 50.
    """
    pivot, pivot_n = _compute_jara_size_x_macrozone(df_sr, dim)

    if pivot.empty or pivot.isna().all().all():
        st.info(t["sr_jara_no_data_size_macro"])
        return

    sub_map = {tt["label"]: tt["sub"] for tt in POPULATION_BRACKETS_JARA}

    def _fmt_row_label(lbl: str) -> str:
        sub = sub_map.get(lbl, "")
        return f"{lbl}\n{sub}" if sub else lbl

    plot_df = pivot.copy()
    plot_n = pivot_n.copy()
    plot_df.index = [_fmt_row_label(i) for i in plot_df.index]
    plot_n.index = [_fmt_row_label(i) for i in plot_n.index]

    render_section_subtitle(t["sr_jara_sub_size_macro"])

    customdata = []
    for i, size in enumerate(plot_df.index):
        row = []
        for j, zone in enumerate(plot_df.columns):
            val = plot_df.iloc[i, j]
            n = plot_n.iloc[i, j]
            n_txt = "—" if pd.isna(n) else int(n)
            val_txt = "—" if pd.isna(val) else f"{val:.2f}%"
            row.append([str(size).replace("\n", " · "), str(zone), val_txt, n_txt])
        customdata.append(row)

    colorscale = HEATMAP_SCALE_PCT

    empty_text = [["" for _ in plot_df.columns] for _ in plot_df.index]

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=plot_df.values,
        x=plot_df.columns.tolist(),
        y=plot_df.index.tolist(),
        colorscale=colorscale,
        zmin=30,
        zmax=70,
        showscale=True,
        text=empty_text,
        customdata=customdata,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[1]}<br>"
            "% Jara: %{customdata[2]}<br>"
            "Comunas: %{customdata[3]}"
            "<extra></extra>"
        ),
        xgap=2,
        ygap=2,
        colorbar=dict(
            title=dict(text=t["sr_jara_colorbar_pct_jara"], font=dict(size=10)),
            tickfont=dict(size=9),
            thickness=12,
            len=0.75,
        ),
    ))

    xs_w, ys_w, texts_w = [], [], []
    xs_d, ys_d, texts_d = [], [], []
    for i, size in enumerate(plot_df.index):
        for j, zone in enumerate(plot_df.columns):
            val = plot_df.iloc[i, j]
            if pd.isna(val):
                continue
            label = f"{val:.1f}%"
            if val >= 50:
                xs_w.append(zone)
                ys_w.append(size)
                texts_w.append(label)
            else:
                xs_d.append(zone)
                ys_d.append(size)
                texts_d.append(label)

    if xs_w:
        fig.add_trace(go.Scatter(
            x=xs_w, y=ys_w,
            mode="text",
            text=texts_w,
            textfont=dict(size=12, family="Liberation Sans, Arial", color="white"),
            textposition="middle center",
            hoverinfo="skip",
            showlegend=False,
        ))

    if xs_d:
        fig.add_trace(go.Scatter(
            x=xs_d, y=ys_d,
            mode="text",
            text=texts_d,
            textfont=dict(size=12, family="Liberation Sans, Arial", color="#333333"),
            textposition="middle center",
            hoverinfo="skip",
            showlegend=False,
        ))

    fig.update_layout(
        height=460,
        margin=dict(l=240, r=80, t=20, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Liberation Sans, Arial, sans-serif", size=11),
        xaxis=dict(
            title=dict(text=t["sr_jara_axis_macrozone"], font=dict(size=12, color="#333")),
            tickfont=dict(size=10, color="#333"),
            side="bottom",
        ),
        yaxis=dict(
            title=dict(text=t["sr_jara_axis_size"], font=dict(size=12, color="#333")),
            tickfont=dict(size=10, color="#333"),
            autorange="reversed",
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    render_section_subtitle(t["sr_jara_sub_size_macro_footer"])


# ============================================================================
# SECTION NO. 7 — CLOSE LOSSES
# ============================================================================
def _render_close_losses(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the close losses table: communes where Kast won by ≤ 2 pp.
    """
    df = df_sr.copy()
    df["__valid"] = df["jara_votes"] + df["kast_votes"]
    df["__jara_pct"] = (df["jara_votes"] / df["__valid"].replace(0, 1) * 100)
    df["__kast_pct"] = (df["kast_votes"] / df["__valid"].replace(0, 1) * 100)

    comp_ultra = t["sr_jara_comp_ultra"]
    comp_competitive = t["sr_jara_comp_competitive"]

    sub = df[df["__kast_pct"] > df["__jara_pct"]].copy()
    sub["__margin_pp"] = (sub["__kast_pct"] - sub["__jara_pct"]).round(2)
    sub = sub[sub["__margin_pp"] <= 2].copy()
    sub["__comp"] = sub["__margin_pp"].apply(
        lambda x: comp_ultra if x <= 1 else comp_competitive
    )
    sub = sub.sort_values("__margin_pp", ascending=True).reset_index(drop=True)
    total = len(sub)

    render_section_subtitle(t["sr_jara_sub_derrotas_comp"].format(n=total))

    if sub.empty:
        st.info(t["sr_jara_no_data"])
        return

    rows_html = ""
    for _, r in sub.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        jara_pct = f"{r['__jara_pct']:.2f}%"
        kast_pct = f"{r['__kast_pct']:.2f}%"
        margin = f"+{r['__margin_pp']:.2f} pp"
        comp = str(r["__comp"])

        if comp == comp_ultra:
            comp_color = COMP_ULTRA_TIGHT
        else:
            comp_color = COMP_COMPETITIVE

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{jara_pct}</td>'
            f'<td style="text-align:right; color:#666;">{kast_pct}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{margin}</td>'
            f'<td style="color:{comp_color}; font-size:9.5pt;">{comp}</td>'
            f"</tr>"
        )

    html = _table_css("jara-daj-table") + f"""
    <div class="jara-daj-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_jara_th_comuna']}</th>
                    <th>{t['sr_jara_th_region']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_pct_jara']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_pct_kast']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_margen_kast']}</th>
                    <th>{t['sr_jara_th_competitividad']}</th>
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
# SECTION NO. 8 — LOSS DISTRIBUTION BY ZONE
# ============================================================================
def _render_loss_distribution_by_zone(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the loss distribution by zone: for each macrozone, a horizontal
    stacked bar showing how close losses are distributed across margin
    buckets.
    """
    narrow = _prepare_narrow_losses(df_sr)

    pivot = pd.crosstab(narrow["__margin_range"], narrow["macrozone"])
    pivot = pivot.reindex(index=RANGE_ORDER, columns=ZONE_ORDER, fill_value=0)

    pivot = pivot.loc[:, (pivot.sum(axis=0) > 0)]
    zones_present = [z for z in ZONE_ORDER if z in pivot.columns]
    pivot = pivot[zones_present]

    if pivot.empty:
        st.info(t["sr_jara_no_data"])
        return

    pct_df = pivot.div(pivot.sum(axis=0), axis=1) * 100
    pct_df = pct_df.round(1).fillna(0)

    render_section_subtitle(t["sr_jara_sub_dist_zona"])

    blocks_html = ""
    for zone in zones_present:
        n_communes_zone = int(pivot[zone].sum())
        if n_communes_zone == 0:
            continue

        segments = []
        for rng in RANGE_ORDER:
            if rng in pct_df.index:
                pct = float(pct_df.loc[rng, zone])
                if pct > 0:
                    segments.append({
                        "label": rng,
                        "pct": pct,
                        "color": MARGIN_SCALE_COLORS[rng],
                    })

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
                f'<div class="{classes}" style="width:{s["pct"]}%; background:{s["color"]};" '
                f'title="{s["label"]}: {s["pct"]:.2f}%">{label}</div>'
            )

        blocks_html += f"""
        <div class="tramo-wrap">
            <div class="tramo-header">
                <div class="tramo-label">{zone}</div>
                <div class="tramo-meta">{t['sr_jara_meta_comunas'].format(n=n_communes_zone)}</div>
            </div>
            <div class="tramo-bar-wrap">
                <div class="tramo-midline"></div>
                <div class="tramo-bar">{bar}</div>
            </div>
        </div>
        """

    legend_items = ""
    for rng in RANGE_ORDER:
        color = MARGIN_SCALE_COLORS[rng]
        legend_items += (
            f'<div class="legend-item">'
            f'<span class="legend-dot" style="background:{color};"></span>'
            f'{rng}'
            f'</div>'
        )

    html = _LOSS_DISTRIBUTION_CSS + f"""
    <div class="tramos-wrap">
        {blocks_html}
        <div class="tramos-leyenda">
            {legend_items}
        </div>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)

    zones_without_losses = [z for z in ZONE_ORDER if z not in zones_present]

    if zones_without_losses:
        if len(zones_without_losses) == 1:
            zones_txt = zones_without_losses[0]
        elif len(zones_without_losses) == 2:
            zones_txt = f"{zones_without_losses[0]} y {zones_without_losses[1]}"
        else:
            zones_txt = ", ".join(zones_without_losses[:-1]) + f" y {zones_without_losses[-1]}"

        msg = t["sr_jara_msg_sin_derrotas"].format(zonas=zones_txt)

        st.markdown(
            _clean_html(f"""
            <div style="
                font-family: 'Liberation Sans', Arial, sans-serif;
                font-size: 10pt;
                color: #6B7280;
                line-height: 1.5;
                max-width: 940px;
            ">
                {msg}
            </div>
            """),
            unsafe_allow_html=True,
        )


# ============================================================================
# SECTION NO. 9 — LOSSES BY ZONE AND MARGIN
# ============================================================================
def _render_losses_by_zone(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the losses-by-zone heatmap: rows are margin buckets, columns are
    macrozones, cells are the number of communes in each bucket.
    """
    narrow = _prepare_narrow_losses(df_sr)

    pivot = pd.crosstab(narrow["__margin_range"], narrow["macrozone"])
    pivot = pivot.reindex(index=RANGE_ORDER, columns=ZONE_ORDER, fill_value=0)
    pivot.loc["TOTAL"] = pivot.sum(axis=0)
    pivot["TOTAL"] = pivot.sum(axis=1)

    render_section_subtitle(t["sr_jara_sub_derrotas_zona_margen"])

    plot_df = pivot.drop(index="TOTAL", errors="ignore").drop(columns="TOTAL", errors="ignore")
    plot_df = plot_df.reindex(index=RANGE_ORDER, columns=ZONE_ORDER, fill_value=0)

    colorscale = HEATMAP_SCALE_COUNT

    fig = go.Figure(data=go.Heatmap(
        z=plot_df.values,
        x=plot_df.columns.tolist(),
        y=plot_df.index.tolist(),
        colorscale=colorscale,
        showscale=True,
        text=plot_df.values,
        texttemplate="%{text}",
        textfont={"size": 13, "family": "Liberation Sans, Arial"},
        hovertemplate="<b>%{x}</b><br>Margen: %{y}<br>Comunas: %{z}<extra></extra>",
        xgap=2,
        ygap=2,
        colorbar=dict(
            title=dict(text=t["sr_jara_colorbar_comunas"], font=dict(size=10)),
            tickfont=dict(size=9),
            thickness=12,
            len=0.7,
        ),
    ))

    fig.update_layout(
        height=380,
        margin=dict(l=80, r=80, t=20, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Liberation Sans, Arial, sans-serif", size=11),
        xaxis=dict(
            title=dict(text=t["sr_jara_axis_macrozone"], font=dict(size=12, color="#333")),
            tickfont=dict(size=10, color="#333"),
            side="bottom",
        ),
        yaxis=dict(
            title=dict(text=t["sr_jara_axis_margen_derrota"], font=dict(size=12, color="#333")),
            tickfont=dict(size=10, color="#333"),
            autorange="reversed",
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ============================================================================
# SECTION NO. 10 — SANTIAGO ELITE
# ============================================================================
def _render_santiago_elite(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the Santiago elite analysis: Jara's performance in Vitacura,
    Las Condes, and Lo Barnechea, comparing first round and runoff.
    """
    elite_norm = ["vitacura", "las condes", "lo barnechea"]

    DISPLAY_NAMES = {
        "las condes": "Las Condes",
        "vitacura": "Vitacura",
        "lo barnechea": "Lo Barnechea",
    }

    df_fr_sub = df_fr[
        df_fr["commune_name"].astype(str).str.strip().str.lower().isin(elite_norm)
    ][["commune_id", "commune_name", "jara_votes", "jara_pct"]].rename(
        columns={"jara_votes": "jara_votes_1v", "jara_pct": "jara_pct_1v"}
    )

    df_sr_sub = df_sr[
        df_sr["commune_name"].astype(str).str.strip().str.lower().isin(elite_norm)
    ][["commune_id", "jara_votes", "jara_pct"]].rename(
        columns={"jara_votes": "jara_votes_2v", "jara_pct": "jara_pct_2v"}
    )

    df = df_fr_sub.merge(df_sr_sub, on="commune_id", how="inner")
    df["__vote_change"] = df["jara_votes_2v"] - df["jara_votes_1v"]
    df["__pct_change"] = df["jara_pct_2v"] - df["jara_pct_1v"]

    df["__display_name"] = (
        df["commune_name"].astype(str).str.strip().str.lower().map(DISPLAY_NAMES)
    )
    df = df.sort_values("__display_name").reset_index(drop=True)

    render_section_subtitle(t["sr_jara_sub_elite"])

    rows_html = ""
    for _, r in df.iterrows():
        vc = int(r["__vote_change"])
        pc = float(r["__pct_change"])
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{r["__display_name"]}</td>'
            f'<td style="text-align:right; color:#666;">{_fmt_number(r["jara_votes_1v"])}</td>'
            f'<td style="text-align:right; color:#666;">{_fmt_number(r["jara_votes_2v"])}</td>'
            f'<td style="text-align:right; color:#666;">{_fmt_signed(vc, 0)}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{_fmt_signed(pc, 2)} pp</td>'
            f"</tr>"
        )

    html = _table_css("jara-eli-table") + f"""
    <div class="jara-eli-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_jara_th_comuna']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_votos_1v']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_votos_2v']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_delta_votos']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_delta_jara_pp']}</th>
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
# SECTION NO. 11 — PROTEST VOTE
# ============================================================================
def _render_protest_vote(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the protest vote analysis: how changes in null/blank votes
    between the first round and the runoff correlate with changes in Jara's %.
    """
    fr = df_fr[["commune_id", "commune_name", "region_name",
                "null_votes", "blank_votes", "jara_pct"]].rename(columns={
        "null_votes": "null_1v", "blank_votes": "blank_1v", "jara_pct": "jara_pct_1v"
    })

    sr = df_sr[["commune_id", "null_votes", "blank_votes", "jara_pct"]].rename(columns={
        "null_votes": "null_2v", "blank_votes": "blank_2v", "jara_pct": "jara_pct_2v"
    })

    df = fr.merge(sr, on="commune_id", how="inner")

    df["__protest_change"] = (
        (df["null_2v"] - df["null_1v"]) +
        (df["blank_2v"] - df["blank_1v"])
    )
    df["__jara_pct_change"] = (df["jara_pct_2v"] - df["jara_pct_1v"]).round(2)

    # NOTE: bucket labels are user-facing and hardcoded in Spanish.
    # They should live in translations.py. See TECHNICAL DEBT.
    bucket_decreases = t["sr_jara_bucket_disminuye"]
    bucket_0_500 = t["sr_jara_bucket_0_500"]
    bucket_500_1000 = t["sr_jara_bucket_500_1000"]
    bucket_1000_2000 = t["sr_jara_bucket_1000_2000"]
    bucket_2000_mas = t["sr_jara_bucket_2000_mas"]

    def _bucket(change: float) -> str:
        if change < 0:
            return bucket_decreases
        if change < 500:
            return bucket_0_500
        if change < 1000:
            return bucket_500_1000
        if change < 2000:
            return bucket_1000_2000
        return bucket_2000_mas

    df["__bucket"] = df["__protest_change"].apply(_bucket)

    BUCKET_ORDER = [bucket_decreases, bucket_0_500, bucket_500_1000, bucket_1000_2000, bucket_2000_mas]

    summary = df.groupby("__bucket").agg(
        communes=("commune_id", "count"),
        avg_jara_change=("__jara_pct_change", "mean"),
    ).round(2).reindex(BUCKET_ORDER).fillna(0)

    render_section_subtitle(t["sr_jara_sub_protesta"])

    rows_b = ""
    for b in BUCKET_ORDER:
        if b in summary.index:
            r = summary.loc[b]
            rows_b += (
                f"<tr>"
                f'<td style="font-weight:400; color:#333;">{b}</td>'
                f'<td style="text-align:right; color:#666;">{int(r["communes"])}</td>'
                f'<td style="text-align:right; font-weight:700; color:#111827;">{r["avg_jara_change"]:+.2f} pp</td>'
                f"</tr>"
            )

    html_b = _table_css("jara-prot-b-table") + f"""
    <div class="jara-prot-b-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_jara_th_delta_voto_protesta']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_comunas']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_delta_jara_prom']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_b}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_b), unsafe_allow_html=True)
    _table_gap()

    render_section_title(t["sr_jara_section_top_protesta"])

    top10 = df.nlargest(10, "__protest_change")

    rows_t = ""
    for _, r in top10.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        p_change = f"+{_fmt_number(r['__protest_change'])}"
        j_change = f"{_fmt_signed(r['__jara_pct_change'], 2)} pp"
        rows_t += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{p_change}</td>'
            f'<td style="text-align:right; color:{JARA_COLOR};">{j_change}</td>'
            f"</tr>"
        )

    html_t = _table_css("jara-prot-t-table") + f"""
    <div class="jara-prot-t-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_jara_th_comuna']}</th>
                    <th>{t['sr_jara_th_region']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_delta_protesta']}</th>
                    <th style="text-align:right;">{t['sr_jara_th_delta_jara_pp']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_t}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_t), unsafe_allow_html=True)
    _table_gap()


# ============================================================================
# SECTION NO. 0 — KPI CARDS
# ============================================================================
def _render_kpi_cards(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the 4 featured cards at the top of the view.
    """
    jara_votes_2v = int(df_sr["jara_votes"].sum())
    kast_votes_2v = int(df_sr["kast_votes"].sum())
    total_valid_2v = jara_votes_2v + kast_votes_2v
    jara_pct_2v = (jara_votes_2v / total_valid_2v * 100) if total_valid_2v else 0

    df_sr_copy = df_sr.copy()
    df_sr_copy["__winner"] = df_sr_copy.apply(
        lambda r: "Jara" if r["jara_votes"] > r["kast_votes"] else "Kast", axis=1
    )
    communes_won = int((df_sr_copy["__winner"] == "Jara").sum())

    fr_winner = df_fr.copy()
    fr_cols = ["jara_pct", "kast_pct", "parisi_pct", "kaiser_pct",
               "matthei_pct", "mayne_nicholls_pct", "enriquez_ominami_pct", "artes_pct"]
    fr_cols = [c for c in fr_cols if c in fr_winner.columns]
    fr_winner["__winner_fr"] = fr_winner[fr_cols].idxmax(axis=1).str.replace("_pct", "", regex=False)

    merged = fr_winner[["commune_id", "__winner_fr"]].merge(
        df_sr_copy[["commune_id", "__winner"]],
        on="commune_id",
        how="inner",
    )
    flips = int(((merged["__winner_fr"] != "jara") & (merged["__winner"] == "Jara")).sum())

    cards = [
        (t["sr_jara_kpi_votos_2v"], _fmt_number(jara_votes_2v), t["sr_jara_kpi_votos_2v_sub"]),
        (t["sr_jara_kpi_pct_validos"], f"{jara_pct_2v:.2f}%", t["sr_jara_kpi_pct_validos_sub"]),
        (t["sr_jara_kpi_comunas_ganadas"], str(communes_won), t["sr_jara_kpi_comunas_ganadas_sub"]),
        (t["sr_jara_kpi_flips"], str(flips), t["sr_jara_kpi_flips_sub"]),
    ]

    cards_html = ""
    for label, value, sub in cards:
        cards_html += f"""
        <div class="nb-card">
            <div class="nb-card-label">{label}</div>
            <div class="nb-card-value">{value}</div>
            <div class="nb-card-sub">{sub}</div>
        </div>
        """

    html = _NB_CARD_CSS + f'<div class="nb-cards">{cards_html}</div>'
    st.markdown(_clean_html(html), unsafe_allow_html=True)


# ============================================================================
# FOOTER
# ============================================================================
def _render_footer(t: dict) -> None:
    st.markdown(
        _clean_html(_FOOTER_CSS + f"""
        <div class="page-footer">
            <p>{t['data_source']} · {t['data_source_note']}</p>
        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION BUILDERS
# ============================================================================
def _build_kpis_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the KPI cards section."""
    _render_kpi_cards(df_fr, df_sr, t)


def _build_strongholds_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the strongholds section."""
    _render_strongholds(df_sr, t)


def _build_flips_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the flips section."""
    _render_flips_jara(df_fr, df_sr, t)


def _build_strongholds_expansion_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the strongholds expansion section."""
    _render_strongholds_expansion(df_fr, df_sr, t)


def _build_macrozone_profile_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """Build the macrozone profile section."""
    _render_macrozone_profile(df_fr, df_sr, dim, t)


def _build_jara_by_commune_size_section(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """Build the Jara-by-commune-size section."""
    _render_jara_by_commune_size(df_sr, dim, t)


def _build_jara_size_x_macrozone_section(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """Build the Jara-size × macrozone section."""
    _render_jara_size_x_macrozone(df_sr, dim, t)


def _build_close_losses_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the close losses section."""
    _render_close_losses(df_sr, t)


def _build_loss_distribution_by_zone_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the loss distribution by zone section."""
    _render_loss_distribution_by_zone(df_sr, t)


def _build_losses_by_zone_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the losses by zone and margin section."""
    _render_losses_by_zone(df_sr, t)


def _build_santiago_elite_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the Santiago elite section."""
    _render_santiago_elite(df_fr, df_sr, t)


def _build_protest_vote_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the protest vote section."""
    _render_protest_vote(df_fr, df_sr, t)


# ============================================================================
# RENDER (orchestrator)
# ============================================================================
def render(t: dict) -> None:
    """
    Render the Jeannette Jara page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    render_view_title(JARA_NAME)

    try:
        df_fr = load_fact_first_round_2025()
        df_sr = load_fact_second_round_2025()
        dim = load_dim_commune()

        _build_kpis_section(df_fr, df_sr, t)

        with st.expander(t["sr_jara_exp_bastiones"], expanded=False):
            _build_strongholds_section(df_sr, t)

        with st.expander(t["sr_jara_exp_flips"], expanded=False):
            _build_flips_section(df_fr, df_sr, t)

        with st.expander(t["sr_jara_exp_expansion"], expanded=False):
            _build_strongholds_expansion_section(df_fr, df_sr, t)

        with st.expander(t["sr_jara_exp_perfil_macro"], expanded=False):
            _build_macrozone_profile_section(df_fr, df_sr, dim, t)

        with st.expander(t["sr_jara_exp_gradiente_size"], expanded=False):
            _build_jara_by_commune_size_section(df_sr, dim, t)

        with st.expander(t["sr_jara_exp_gradiente_intensidad"], expanded=False):
            _build_jara_size_x_macrozone_section(df_sr, dim, t)

        with st.expander(t["sr_jara_exp_derrotas_comp"], expanded=False):
            _build_close_losses_section(df_sr, t)

        with st.expander(t["sr_jara_exp_derrotas_dist"], expanded=False):
            _build_loss_distribution_by_zone_section(df_sr, t)

        with st.expander(t["sr_jara_exp_derrotas_zona_margen"], expanded=False):
            _build_losses_by_zone_section(df_sr, t)

        with st.expander(t["sr_jara_exp_elite"], expanded=False):
            _build_santiago_elite_section(df_fr, df_sr, t)

        with st.expander(t["sr_jara_exp_protesta"], expanded=False):
            _build_protest_vote_section(df_fr, df_sr, t)

        _render_footer(t)

    except Exception as e:
        st.error(f"{t.get('error', 'Error')}: {e}")
        st.exception(e)


# ============================================================================
# TECHNICAL DEBT
# ============================================================================
# Three groups of user-facing strings are still hardcoded in Spanish. They
# should be moved to translations.py (LANG["ES"] / LANG["EN"]) in a future
# cleanup pass. Until then, they are kept as-is to avoid breaking the
# bilingual setup and to keep this refactor focused on identifier translation.
#
# 1. POPULATION_BRACKETS_JARA labels and subtitles:
#      "Rural" / "menos de 10.000 hab."
#      "Rural-urbano" / "10.000 – 49.999 hab."
#      "Centros urbanos pequeños" / "50.000 – 99.999 hab."
#      "Centros urbanos medios" / "100.000 – 199.999 hab."
#      "Grandes centros urbanos" / "más de 200.000 hab."
#
#    These appear in the commune-size charts (sections 5 and 6). The labels
#    describe the population brackets used to classify communes by size.
#
# 2. `label_map` inside `_plot_top_bar`:
#      "Región" = region, "Votos totales" = total casted votes,
#      "Votos válidos" = valid votes, "Votos nulos" = null votes,
#      "Votos blancos" = blank votes, "% nulos" = null %,
#      "% blancos" = blank %, "Comuna" = commune,
#      "Votos Jara" = Jara votes, "Votos Kast" = Kast votes,
#      "Población" = population.
#
#    These are used only in the Plotly hover tooltip, not in the static
#    HTML. They could be moved to translations.py and resolved per call,
#    but that would require passing `t` to `label_map` at the call site.
#
# 3. Bucket labels inside `_render_protest_vote`:
#      "Disminuye" = protest vote decreases,
#      "0-500" = protest vote grows by 0-500 votes,
#      "500-1000" = grows by 500-1,000 votes,
#      "1000-2000" = grows by 1,000-2,000 votes,
#      "2000+" = grows by more than 2,000 votes.
#
#    These describe how the null + blank votes changed between the first
#    round and the runoff. They appear in the bucket summary table of the
#    protest vote section.
#
# When these are moved, add the corresponding keys to translations.py with
# the prefix `sr_jara_` and update the call sites. No other code depends on
# them.
