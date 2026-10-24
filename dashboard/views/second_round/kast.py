"""
Second Round — José Antonio Kast Analysis
============================================================================
Candidate-specific analysis for Kast in the 2025 runoff.

Featured cards at the top (4 cards):
    1. Kast's votes in the runoff.
    2. Kast's % over valid votes in the runoff.
    3. Communes won by Kast in the runoff.
    4. Communes where Kast got more than 75% (strongholds).

Sections (all collapsible):
    1. Territorial strongholds: communes where Kast got > 75%, plus the
       victory intensity breakdown.
    2. Regional strongholds: regions where Kast's average is > 60%.
    3. Geography of the vote: Kast's profile by macrozone (first round vs
       runoff).
    4. Reversed duels: communes won by Jara in the first round but won by
       Kast in the runoff.
    5. Close margins: communes where Kast won by ≤ 5 pp.
    6. Protest vote and Kast: how changes in null/blank votes correlate
       with changes in Kast's %.
    7. Growth and loyalty: top/bottom communes by Kast's absolute and
       relative growth (switchable views).
    8. Urban-rural gradient: Kast's % by commune size (runoff).
    9. Urban-rural intensity: Kast's % by commune size × macrozone (runoff).

Transformation helpers (clean_html, format_number) are imported from
utils.html_helpers.
View and section titles live in components.titles.
Colors live in config.constants.

Notes
-----
- `TREND_GRAY` is imported from config.constants. The old name
  `GRIS_TENDENCIA` is still available as an alias but is not used here.
- `POPULATION_BRACKETS_KAST`, the `label_map` in `_plot_top_bar`, and the
  `"Crecimiento Dual"` / `"Lealtad de Base"` strings passed to
  `_render_growth_scatter` contain user-facing strings hardcoded in
  Spanish. They should be migrated to translations.py in a future cleanup
  pass. See the TECHNICAL DEBT block at the bottom of the file.

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
)
from config.constants import (
    CANDIDATE_COLOR_VARIANTS,
    COLOR_NEUTRAL_INDICATOR,
    TREND_GRAY,
    HEATMAP_SCALE_PCT_KAST,
    NEUTRAL_COLOR,
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
KAST_NAME = "José Antonio Kast"
KAST_COLOR = _get_candidate_color(KAST_NAME)
JARA_NAME = "Jeannette Jara"
JARA_COLOR = _get_candidate_color(JARA_NAME)

# Per-candidate color variants (single source: constants.py).
KAST_VARIANTS = CANDIDATE_COLOR_VARIANTS[KAST_NAME]

STRONGHOLD_THRESHOLD = 75.0
REGIONAL_THRESHOLD = 60.0
MACROZONE_ORDER = ["Norte Grande", "Norte Chico", "Centro", "Centro Sur", "Sur", "Patagonia"]

# Scatter colors (Growth & Loyalty block).
COLOR_SCATTER_BASE = NEUTRAL_COLOR
COLOR_SCATTER_PRIMARY = KAST_VARIANTS["oficial"]
COLOR_SCATTER_SECONDARY = KAST_VARIANTS["claro"]

# Number of communes used in the top/bottom growth tables.
N_GROWTH = 20

# NOTE: labels and subtitles are user-facing strings hardcoded in Spanish.
# They should live in translations.py. See TECHNICAL DEBT at the bottom.
POPULATION_BRACKETS_KAST = [
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
    .kast-bast-bar-wrap { font-family: "Liberation Sans", Arial, sans-serif; margin-top: 8px; margin-bottom: 24px; }
    .kast-bast-bar { display: flex; height: 44px; width: 100%; border-radius: 6px; overflow: hidden; }
    .kast-bast-bar-seg { display: flex; align-items: center; justify-content: center; color: #ffffff; font-weight: 700; font-size: 13pt; line-height: 1; }
    .kast-bast-bar-labels { display: flex; justify-content: space-between; margin-top: 8px; font-size: 9.5pt; color: #6b7280; }
</style>
"""

_FLIP_BAR_CSS = """
<style>
    .kast-flip-bar-wrap { font-family: "Liberation Sans", Arial, sans-serif; margin-top: 8px; margin-bottom: 24px; }
    .kast-flip-bar { display: flex; height: 44px; width: 100%; border-radius: 6px; overflow: hidden; }
    .kast-flip-bar-seg { display: flex; align-items: center; justify-content: center; color: #ffffff; font-weight: 700; font-size: 13pt; line-height: 1; }
    .kast-flip-bar-labels { display: flex; justify-content: space-between; margin-top: 8px; font-size: 9.5pt; color: #6b7280; }
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
    .mzp-bar-1v { background: {BLUE_1V}; border-top-left-radius: 4px; }
    .mzp-bar-2v { background: {BLUE_2V}; border-bottom-left-radius: 4px; }
    .mzp-pct { color: #ffffff; font-size: 9.5pt; font-weight: 700; }
    .mzp-delta { width: 110px; font-size: 9.5pt; font-weight: 600; text-align: left; flex-shrink: 0; }
</style>
"""


# ============================================================================
# LOCAL HELPERS — VISUAL FORMATTING
# ============================================================================
def _table_gap():
    """6px gap below each table."""
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)


def _table_css(class_name: str) -> str:
    """Table CSS, identical to jara.py and panorama.py."""
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


def _classify_victory(pct: float, t: dict) -> str:
    if pct > 80:
        return t["sr_kast_victoria_arrasa"]
    elif pct > 70:
        return t["sr_kast_victoria_bastion"]
    elif pct > 60:
        return t["sr_kast_victoria_solido"]
    return t["sr_kast_victoria_otro"]


def _classify_victory_extended(pct: float, t: dict) -> str:
    if pct > 80:
        return t["sr_kast_victoria_ext_arrasa"]
    elif pct > 70:
        return t["sr_kast_victoria_ext_bastion"]
    elif pct > 60:
        return t["sr_kast_victoria_ext_solido"]
    else:
        return t["sr_kast_victoria_ext_mayoria"]


def _get_protest_category(x: float, t: dict) -> str:
    if x < 0:
        return t["sr_kast_protest_disminuye"]
    elif x < 500:
        return t["sr_kast_protest_bajo"]
    elif x < 1000:
        return t["sr_kast_protest_medio"]
    elif x < 2000:
        return t["sr_kast_protest_alto"]
    else:
        return t["sr_kast_protest_muy_alto"]


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
# SECTION NO. 0 — KPI CARDS
# ============================================================================
def _render_kpi_cards(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the 4 featured cards at the top of the view.
    """
    kast_votes_2v = int(df_sr["kast_votes"].sum())
    jara_votes_2v = int(df_sr["jara_votes"].sum())
    total_valid_2v = kast_votes_2v + jara_votes_2v
    kast_pct_2v = (kast_votes_2v / total_valid_2v * 100) if total_valid_2v else 0

    df_sr_copy = df_sr.copy()
    df_sr_copy["__winner"] = df_sr_copy.apply(
        lambda r: "Kast" if r["kast_votes"] > r["jara_votes"] else "Jara", axis=1
    )
    communes_won = int((df_sr_copy["__winner"] == "Kast").sum())

    df_sr_copy["__kast_pct"] = (
        df_sr_copy["kast_votes"] /
        (df_sr_copy["kast_votes"] + df_sr_copy["jara_votes"]).replace(0, 1) * 100
    )
    n_strongholds = int((df_sr_copy["__kast_pct"] > STRONGHOLD_THRESHOLD).sum())

    cards = [
        (t["sr_kast_kpi_votos_2v"], _fmt_number(kast_votes_2v), t["sr_kast_kpi_votos_2v_sub"]),
        (t["sr_kast_kpi_pct_validos"], f"{kast_pct_2v:.2f}%", t["sr_kast_kpi_pct_validos_sub"]),
        (t["sr_kast_kpi_comunas_ganadas"], str(communes_won), t["sr_kast_kpi_comunas_ganadas_sub"]),
        (t["sr_kast_kpi_bastiones"].format(u=int(STRONGHOLD_THRESHOLD)), str(n_strongholds), t["sr_kast_kpi_bastiones_sub"]),
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
# SECTION NO. 1 — STRONGHOLDS (>75%) + VICTORY INTENSITY
# ============================================================================
def _render_strongholds_top10(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the strongholds section: communes where Kast got more than 75%
    in the runoff, plus the victory intensity breakdown.
    """
    df = df_sr.copy()
    df["__valid"] = df["kast_votes"] + df["jara_votes"]
    df["__kast_pct"] = (df["kast_votes"] / df["__valid"].replace(0, 1) * 100)
    df["__jara_pct"] = (df["jara_votes"] / df["__valid"].replace(0, 1) * 100)

    sub = df[df["__kast_pct"] > STRONGHOLD_THRESHOLD].copy()
    sub["__margin_pp"] = (sub["__kast_pct"] - sub["__jara_pct"]).round(2)
    sub["__victory_type"] = sub["__kast_pct"].apply(lambda x: _classify_victory(x, t))
    sub = sub.sort_values("__kast_pct", ascending=False).reset_index(drop=True)

    n_total = len(sub)
    stronghold_votes = int(sub["kast_votes"].sum())
    kast_votes_total = int(df["kast_votes"].sum())
    pct_del_total = (stronghold_votes / kast_votes_total * 100) if kast_votes_total else 0

    render_section_subtitle(
        t["sr_kast_sub_bastiones"].format(
            u=int(STRONGHOLD_THRESHOLD),
            n=n_total,
            p=f"{pct_del_total:.1f}",
        )
    )

    if sub.empty:
        st.info(t["sr_kast_no_data"])
        return

    pct_strongholds = pct_del_total
    pct_rest = 100 - pct_strongholds

    bar_html = _STRONGHOLDS_BAR_CSS + f"""
    <div class="kast-bast-bar-wrap">
        <div class="kast-bast-bar">
            <div class="kast-bast-bar-seg" style="width:{pct_strongholds}%; background:{KAST_COLOR};">{pct_strongholds:.1f}%</div>
            <div class="kast-bast-bar-seg" style="width:{pct_rest}%; background:{COLOR_NEUTRAL_INDICATOR}; color:#333;">{pct_rest:.1f}%</div>
        </div>
        <div class="kast-bast-bar-labels">
            <span>{t['sr_kast_bar_bastiones_izq'].format(n=_fmt_number(stronghold_votes), m=n_total, u=int(STRONGHOLD_THRESHOLD))}</span>
            <span>{t['sr_kast_bar_bastiones_der']}</span>
        </div>
    </div>
    """
    st.markdown(_clean_html(bar_html), unsafe_allow_html=True)

    rows_html = ""
    for _, r in sub.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        kast_pct = f"{r['__kast_pct']:.2f}%"
        margin = f"+{r['__margin_pp']:.2f} pp"
        victory_type = str(r["__victory_type"])

        if victory_type == t["sr_kast_victoria_arrasa"]:
            tipo_color = KAST_VARIANTS["intenso"]
        elif victory_type == t["sr_kast_victoria_bastion"]:
            tipo_color = KAST_VARIANTS["claro"]
        else:
            tipo_color = NEUTRAL_COLOR

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{kast_pct}</td>'
            f'<td style="text-align:right; color:#666;">{margin}</td>'
            f'<td style="color:{tipo_color}; font-size:9.5pt;">{victory_type}</td>'
            f"</tr>"
        )

    html = _table_css("kast-bast-table") + f"""
    <div class="kast-bast-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_kast_th_comuna']}</th>
                    <th>{t['sr_kast_th_region']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_margen']}</th>
                    <th>{t['sr_kast_th_tipo_victoria']}</th>
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

    render_section_title(t["sr_kast_section_intensidad"])
    render_section_subtitle(t["sr_kast_sub_intensidad"])

    wins = df[df["__kast_pct"] > 50].copy()
    wins["__victory_cat"] = wins["__kast_pct"].apply(lambda x: _classify_victory_extended(x, t))
    total_wins = len(wins)

    CATEGORY_ORDER = [
        t["sr_kast_victoria_ext_arrasa"],
        t["sr_kast_victoria_ext_bastion"],
        t["sr_kast_victoria_ext_solido"],
        t["sr_kast_victoria_ext_mayoria"],
    ]

    rows_intensity = ""
    for cat in CATEGORY_ORDER:
        cat_df = wins[wins["__victory_cat"] == cat]
        n = len(cat_df)
        pct_wins = (n / total_wins * 100) if total_wins > 0 else 0

        if n > 0:
            avg_pct = cat_df["__kast_pct"].mean()
            min_pct = cat_df["__kast_pct"].min()
            max_pct = cat_df["__kast_pct"].max()
        else:
            avg_pct = 0
            min_pct = 0
            max_pct = 0

        rows_intensity += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{cat}</td>'
            f'<td style="text-align:right; color:#666;">{n}</td>'
            f'<td style="text-align:right; color:#666;">{pct_wins:.2f}%</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{avg_pct:.2f}%</td>'
            f'<td style="text-align:right; color:#666;">{min_pct:.2f}%</td>'
            f'<td style="text-align:right; color:#666;">{max_pct:.2f}%</td>'
            f"</tr>"
        )

    html_intensity = _table_css("kast-intensidad-table") + f"""
    <div class="kast-intensidad-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_kast_th_categoria']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_comunas']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_victorias']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast_prom']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast_min']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast_max']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_intensity}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_intensity), unsafe_allow_html=True)
    _table_gap()


# ============================================================================
# SECTION NO. 2 — REGIONAL STRONGHOLDS (>60%)
# ============================================================================
def _render_regional_strongholds(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the regional strongholds section: regions where Kast's average
    % over communes with > 60% is aggregated.
    """
    df = df_sr.copy()
    df["__valid"] = df["kast_votes"] + df["jara_votes"]
    df["__kast_pct"] = (df["kast_votes"] / df["__valid"].replace(0, 1) * 100)
    df["__jara_pct"] = (df["jara_votes"] / df["__valid"].replace(0, 1) * 100)

    sub = df[df["__kast_pct"] > REGIONAL_THRESHOLD].copy()
    sub["__margin_pp"] = (sub["__kast_pct"] - sub["__jara_pct"]).round(2)

    total_strongholds = len(sub)
    if total_strongholds == 0:
        st.info(t["sr_kast_no_data"])
        return

    region_order_map = (
        df[["region_name", "region_order"]]
        .dropna().drop_duplicates()
        .set_index("region_name")["region_order"].to_dict()
    )

    region_summary = sub.groupby("region_name").agg(
        n_communes=("commune_id", "count"),
        avg_kast_pct=("__kast_pct", "mean"),
        avg_margin_pp=("__margin_pp", "mean"),
        max_kast_pct=("__kast_pct", "max"),
    ).reset_index()

    region_summary["pct_of_total"] = (
        region_summary["n_communes"] / total_strongholds * 100
    ).round(2)

    region_summary["_order"] = region_summary["region_name"].map(region_order_map).fillna(9999)
    region_summary = region_summary.sort_values("_order").drop(columns="_order").reset_index(drop=True)

    render_section_subtitle(
        t["sr_kast_sub_regionales"].format(
            u=int(REGIONAL_THRESHOLD),
            n=total_strongholds,
            r=len(region_summary),
        )
    )

    rows_html = ""
    for _, r in region_summary.iterrows():
        region = str(r["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        n = int(r["n_communes"])
        pct_of_total = f"{r['pct_of_total']:.2f}%"
        avg_pct = f"{r['avg_kast_pct']:.2f}%"
        avg_margin = f"+{r['avg_margin_pp']:.2f} pp"
        max_pct = f"{r['max_kast_pct']:.2f}%"

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{n}</td>'
            f'<td style="text-align:right; color:#666;">{pct_of_total}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{avg_pct}</td>'
            f'<td style="text-align:right; color:#666;">{avg_margin}</td>'
            f'<td style="text-align:right; color:#666;">{max_pct}</td>'
            f"</tr>"
        )

    html = _table_css("kast-reg-table") + f"""
    <div class="kast-reg-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_kast_th_region']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_comunas_gt'].format(u=int(REGIONAL_THRESHOLD))}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_del_total']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast_prom']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_margen_prom']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast_max']}</th>
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
# SECTION NO. 3 — MACROZONE PROFILE
# ============================================================================
def _render_macrozone_profile(df_fr: pd.DataFrame, df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """
    Render the macrozone profile: for each macrozone, two horizontal bars
    (first round and runoff) showing Kast's % over casted votes, plus the
    delta in pp.
    """
    fr = df_fr[["commune_id", "kast_votes", "casted_votes"]].rename(columns={
        "kast_votes": "kast_1v", "casted_votes": "casted_1v",
    })
    sr = df_sr[["commune_id", "kast_votes", "casted_votes"]].rename(columns={
        "kast_votes": "kast_2v", "casted_votes": "casted_2v",
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
        kast_1v=("kast_1v", "sum"),
        casted_1v=("casted_1v", "sum"),
        kast_2v=("kast_2v", "sum"),
        casted_2v=("casted_2v", "sum"),
    )
    agg["kast_pct_1v"] = agg["kast_1v"] / agg["casted_1v"].replace(0, 1) * 100
    agg["kast_pct_2v"] = agg["kast_2v"] / agg["casted_2v"].replace(0, 1) * 100
    agg["delta_pp"] = agg["kast_pct_2v"] - agg["kast_pct_1v"]

    agg = agg.sort_values("macrozone_order").reset_index(drop=True)

    if agg.empty:
        st.info(t["sr_kast_no_data_macrozone"])
        return

    max_pct = max(agg["kast_pct_1v"].max(), agg["kast_pct_2v"].max())
    scale_max = min(100, max(60, max_pct * 1.05))

    BLUE_1V = KAST_VARIANTS["oficial"]
    BLUE_2V = KAST_VARIANTS["claro"]

    blocks_html = ""
    for _, r in agg.iterrows():
        macrozone = str(r["macrozone"])
        n_communes = int(r["communes"])
        p1 = float(r["kast_pct_1v"])
        p2 = float(r["kast_pct_2v"])
        delta = float(r["delta_pp"])

        w1 = p1 / scale_max * 100
        w2 = p2 / scale_max * 100

        delta_color = BLUE_2V if delta >= 0 else TREND_GRAY
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

    html = _MACROZONE_PROFILE_CSS.replace("{BLUE_1V}", BLUE_1V).replace("{BLUE_2V}", BLUE_2V) + f"""
    <div class="mzp-wrap">
        {blocks_html}
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 4 — REVERSED DUELS (JARA 1st → KAST 2nd)
# ============================================================================
def _render_reversed_duels(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the reversed duels section: communes won by Jara in the first
    round but won by Kast in the runoff. Includes a stacked bar (% of Kast's
    runoff votes that came from these communes) and a top-20 table by swing.
    """
    fr_cols = ["jara_pct", "kast_pct", "parisi_pct", "kaiser_pct",
               "matthei_pct", "mayne_nicholls_pct",
               "enriquez_ominami_pct", "artes_pct"]
    fr_cols = [c for c in fr_cols if c in df_fr.columns]

    fr = df_fr[["commune_id", "commune_name", "region_name"] + fr_cols].copy()
    fr["__winner_fr"] = fr[fr_cols].idxmax(axis=1).str.replace("_pct", "", regex=False)

    fr = fr.rename(columns={
        "jara_pct": "jara_pct_1v",
        "kast_pct": "kast_pct_1v",
    })[["commune_id", "commune_name", "region_name",
        "jara_pct_1v", "kast_pct_1v", "__winner_fr"]]

    sr = df_sr[["commune_id", "kast_votes", "jara_votes", "kast_pct"]].copy()
    sr["__winner_sr"] = sr.apply(
        lambda r: "kast" if r["kast_votes"] > r["jara_votes"] else "jara", axis=1
    )
    sr = sr.rename(columns={"kast_pct": "kast_pct_2v", "kast_votes": "kast_votes_2v"})
    sr = sr[["commune_id", "kast_votes_2v", "kast_pct_2v", "__winner_sr"]]

    df = fr.merge(sr, on="commune_id", how="inner")

    flips = df[
        (df["__winner_fr"] == "jara") & (df["__winner_sr"] == "kast")
    ].copy()

    total = len(flips)

    render_section_subtitle(t["sr_kast_sub_duelos"].format(n=total))

    if flips.empty:
        st.info(t["sr_kast_no_data"])
        return

    flips["__swing_pp"] = (flips["kast_pct_2v"] - flips["kast_pct_1v"]).round(2)

    kast_votes_total = int(df_sr["kast_votes"].sum())
    kast_votes_flips = int(flips["kast_votes_2v"].sum())
    pct_del_total = (kast_votes_flips / kast_votes_total * 100) if kast_votes_total else 0
    pct_rest = 100 - pct_del_total

    bar_html = _FLIP_BAR_CSS + f"""
    <div class="kast-flip-bar-wrap">
        <div class="kast-flip-bar">
            <div class="kast-flip-bar-seg" style="width:{pct_del_total}%; background:{KAST_COLOR};">{pct_del_total:.1f}%</div>
            <div class="kast-flip-bar-seg" style="width:{pct_rest}%; background:{COLOR_NEUTRAL_INDICATOR}; color:#333;">{pct_rest:.1f}%</div>
        </div>
        <div class="kast-flip-bar-labels">
            <span>{t['sr_kast_bar_flips_izq'].format(n=_fmt_number(kast_votes_flips), m=total)}</span>
            <span>{t['sr_kast_bar_bastiones_der']}</span>
        </div>
    </div>
    """
    st.markdown(_clean_html(bar_html), unsafe_allow_html=True)

    top20 = flips.sort_values("__swing_pp", ascending=False).head(20).reset_index(drop=True)

    render_section_title(t["sr_kast_section_swing"])

    rows_html = ""
    for _, r in top20.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        jara_1v = f"{r['jara_pct_1v']:.2f}%"
        kast_1v = f"{r['kast_pct_1v']:.2f}%"
        kast_2v = f"{r['kast_pct_2v']:.2f}%"
        swing = f"+{r['__swing_pp']:.2f} pp"

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{jara_1v}</td>'
            f'<td style="text-align:right; color:#666;">{kast_1v}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{kast_2v}</td>'
            f'<td style="text-align:right; color:{KAST_COLOR};">{swing}</td>'
            f"</tr>"
        )

    html = _table_css("kast-flip-table") + f"""
    <div class="kast-flip-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_kast_th_comuna']}</th>
                    <th>{t['sr_kast_th_region']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_jara_1v']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast_1v']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast_2v']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_swing_kast']}</th>
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
# SECTION NO. 5 — CLOSE MARGINS (< 5 pp)
# ============================================================================
def _render_close_margins(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the close margins section: communes where Kast won by ≤ 5 pp,
    sorted by margin ascending (the most fragile first).
    """
    df = df_sr[["commune_id", "commune_name", "region_name",
                "kast_votes", "jara_votes"]].copy()
    df["__valid"] = df["kast_votes"] + df["jara_votes"]
    df = df[df["__valid"] > 0].copy()

    df["__kast_pct"] = df["kast_votes"] / df["__valid"] * 100
    df["__jara_pct"] = df["jara_votes"] / df["__valid"] * 100
    df["__margin_pp"] = (df["__kast_pct"] - df["__jara_pct"]).round(2)

    sub = df[
        (df["__margin_pp"] > 0) & (df["__margin_pp"] <= 5)
    ].copy().sort_values("__margin_pp", ascending=True).reset_index(drop=True)

    total = len(sub)

    render_section_subtitle(t["sr_kast_sub_margenes"].format(n=total))

    if sub.empty:
        st.info(t["sr_kast_no_data"])
        return

    rows_html = ""
    for _, r in sub.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        kast_pct = f"{r['__kast_pct']:.2f}%"
        jara_pct = f"{r['__jara_pct']:.2f}%"
        margin = f"+{r['__margin_pp']:.2f} pp"

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{kast_pct}</td>'
            f'<td style="text-align:right; color:#666;">{jara_pct}</td>'
            f'<td style="text-align:right; color:{KAST_COLOR};">{margin}</td>'
            f"</tr>"
        )

    html = _table_css("kast-margenes-table") + f"""
    <div class="kast-margenes-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_kast_th_comuna']}</th>
                    <th>{t['sr_kast_th_region']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_kast']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_pct_jara']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_margen_kast']}</th>
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
# SECTION NO. 6 — PROTEST VOTE AND KAST
# ============================================================================
def _render_kast_protest_vote(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the protest vote analysis: how changes in null/blank votes
    correlate with changes in Kast's %.
    """
    fr = df_fr[["commune_id", "commune_name", "region_name",
                "null_votes", "blank_votes", "casted_votes", "kast_pct"]].rename(columns={
        "null_votes": "null_1v", "blank_votes": "blank_1v",
        "casted_votes": "casted_1v", "kast_pct": "kast_pct_1v",
    })

    sr = df_sr[["commune_id", "null_votes", "blank_votes", "kast_pct"]].rename(columns={
        "null_votes": "null_2v", "blank_votes": "blank_2v", "kast_pct": "kast_pct_2v",
    })

    df = fr.merge(sr, on="commune_id", how="inner")

    df["__null_increase"] = df["null_2v"] - df["null_1v"]
    df["__blank_increase"] = df["blank_2v"] - df["blank_1v"]
    df["__total_protest_increase"] = df["__null_increase"] + df["__blank_increase"]
    df["__kast_growth_pp"] = (df["kast_pct_2v"] - df["kast_pct_1v"]).round(2)

    df["__null_increase_pct"] = (
        100 * df["__null_increase"] / df["casted_1v"].replace(0, 1)
    ).round(2)
    df["__blank_increase_pct"] = (
        100 * df["__blank_increase"] / df["casted_1v"].replace(0, 1)
    ).round(2)

    df["__protest_category"] = df["__total_protest_increase"].apply(
        lambda x: _get_protest_category(x, t)
    )

    CATEGORY_ORDER = [
        t["sr_kast_protest_disminuye"],
        t["sr_kast_protest_bajo"],
        t["sr_kast_protest_medio"],
        t["sr_kast_protest_alto"],
        t["sr_kast_protest_muy_alto"],
    ]

    summary = df.groupby("__protest_category").agg(
        communes=("commune_id", "count"),
        avg_kast_growth_pp=("__kast_growth_pp", "mean"),
        avg_null_increase_pct=("__null_increase_pct", "mean"),
        avg_blank_increase_pct=("__blank_increase_pct", "mean"),
    ).round(2).reindex(CATEGORY_ORDER)

    render_section_subtitle(t["sr_kast_sub_protesta"])

    rows_html = ""
    for cat in CATEGORY_ORDER:
        if cat in summary.index:
            r = summary.loc[cat]
            n = int(r["communes"])
            avg_growth = f"{r['avg_kast_growth_pp']:+.2f} pp"
            avg_null = f"{r['avg_null_increase_pct']:+.2f}%"
            avg_blank = f"{r['avg_blank_increase_pct']:+.2f}%"

            rows_html += (
                f"<tr>"
                f'<td style="font-weight:400; color:#333;">{cat}</td>'
                f'<td style="text-align:right; color:#666;">{n}</td>'
                f'<td style="text-align:right; font-weight:700; color:#111827;">{avg_growth}</td>'
                f'<td style="text-align:right; color:#666;">{avg_null}</td>'
                f'<td style="text-align:right; color:#666;">{avg_blank}</td>'
                f"</tr>"
            )

    html = _table_css("kast-protest-table") + f"""
    <div class="kast-protest-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_kast_th_delta_voto_protesta']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_comunas']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_delta_kast_pp']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_delta_nulos']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_delta_blancos']}</th>
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
# SECTION NO. 7 — GROWTH AND LOYALTY
# ============================================================================
def _compute_kast_growth_commune(df_fr: pd.DataFrame, df_sr: pd.DataFrame) -> pd.DataFrame:
    """Merge first and second round, compute Kast's absolute and relative growth."""
    fr = df_fr[["commune_id", "commune_name", "region_name", "kast_votes"]].rename(
        columns={"kast_votes": "kast_votes_1v"}
    )
    sr = df_sr[["commune_id", "kast_votes"]].rename(columns={"kast_votes": "kast_votes_2v"})

    df = fr.merge(sr, on="commune_id", how="inner")
    df["__abs_growth"] = df["kast_votes_2v"] - df["kast_votes_1v"]
    df["__rel_growth_pct"] = (
        100 * df["__abs_growth"] / df["kast_votes_1v"].replace(0, 1)
    ).round(1)
    return df


def _render_top10_growth_table(df_top: pd.DataFrame, title: str, t: dict) -> None:
    """Reusable table for top/bottom N growth."""
    rows_html = ""
    for _, r in df_top.iterrows():
        commune = str(r.get("commune_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r.get("region_name", "—")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        v1 = _fmt_number(r["kast_votes_1v"])
        v2 = _fmt_number(r["kast_votes_2v"])
        abs_growth = r["__abs_growth"]
        rel_growth = r["__rel_growth_pct"]

        abs_sign = "+" if abs_growth >= 0 else ""
        rel_sign = "+" if rel_growth >= 0 else ""

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{commune}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{v1}</td>'
            f'<td style="text-align:right; color:#666;">{v2}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{abs_sign}{_fmt_number(abs_growth)}</td>'
            f'<td style="text-align:right; color:{KAST_COLOR};">{rel_sign}{rel_growth:.1f}%</td>'
            f"</tr>"
        )

    slug = title.lower().replace(" ", "-")
    html = _table_css(f"kast-growth-{slug}") + f"""
    <div class="kast-growth-{slug}">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_kast_th_comuna']}</th>
                    <th>{t['sr_kast_th_region']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_votos_kast_1v']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_votos_kast_2v']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_delta_abs']}</th>
                    <th style="text-align:right;">{t['sr_kast_th_delta_rel']}</th>
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


def _render_growth_scatter(
    df_all: pd.DataFrame,
    df_primary: pd.DataFrame,
    df_secondary: pd.DataFrame,
    primary_label: str,
    secondary_label: str,
    title: str,
    t: dict,
) -> None:
    """
    Scatter Plotly: all communes (gray) + top/bottom N absolute (dark blue)
    + top/bottom N relative (light blue). Labels only for the primary group.
    """
    n_all = len(df_all)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_all["__rel_growth_pct"],
        y=df_all["__abs_growth"],
        mode="markers",
        name=t["sr_kast_scatter_all"].format(n=n_all),
        marker=dict(
            color=COLOR_SCATTER_BASE,
            size=8,
            opacity=0.65,
            line=dict(width=0),
        ),
        text=df_all["commune_name"],
        hovertemplate="<b>%{text}</b><br>Crec. relativo: %{x:.1f}%<br>Crec. absoluto: %{y:,}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_secondary["__rel_growth_pct"],
        y=df_secondary["__abs_growth"],
        mode="markers",
        name=secondary_label,
        marker=dict(
            color=COLOR_SCATTER_SECONDARY,
            size=11,
            opacity=0.9,
            line=dict(color="white", width=1),
        ),
        text=df_secondary["commune_name"],
        hovertemplate="<b>%{text}</b><br>Crec. relativo: %{x:.1f}%<br>Crec. absoluto: %{y:,}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_primary["__rel_growth_pct"],
        y=df_primary["__abs_growth"],
        mode="markers+text",
        name=primary_label,
        marker=dict(
            color=COLOR_SCATTER_PRIMARY,
            size=13,
            opacity=1.0,
            line=dict(color="white", width=1.5),
        ),
        text=df_primary["commune_name"],
        textposition="top center",
        textfont=dict(size=9, color="#333", family="Liberation Sans, Arial"),
        hovertemplate="<b>%{text}</b><br>Crec. relativo: %{x:.1f}%<br>Crec. absoluto: %{y:,}<extra></extra>",
    ))

    fig.add_hline(y=0, line=dict(color=TREND_GRAY, width=1, dash="dash"), opacity=0.7)

    x_all = df_all["__rel_growth_pct"].dropna()
    y_all = df_all["__abs_growth"].dropna()

    x_lo = float(x_all.quantile(0.01))
    x_hi = float(x_all.quantile(0.99))
    y_lo = float(y_all.quantile(0.01))
    y_hi = float(y_all.quantile(0.99))

    if len(df_primary):
        x_hi = max(x_hi, float(df_primary["__rel_growth_pct"].max()))
        x_lo = min(x_lo, float(df_primary["__rel_growth_pct"].min()))
        y_hi = max(y_hi, float(df_primary["__abs_growth"].max()))
        y_lo = min(y_lo, float(df_primary["__abs_growth"].min()))
    if len(df_secondary):
        x_hi = max(x_hi, float(df_secondary["__rel_growth_pct"].max()))
        x_lo = min(x_lo, float(df_secondary["__rel_growth_pct"].min()))
        y_hi = max(y_hi, float(df_secondary["__abs_growth"].max()))
        y_lo = min(y_lo, float(df_secondary["__abs_growth"].min()))

    x_pad = (x_hi - x_lo) * 0.05 if x_hi > x_lo else 1
    y_pad = (y_hi - y_lo) * 0.05 if y_hi > y_lo else 1

    fig.update_layout(
        height=560,
        margin=dict(l=80, r=40, t=30, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,1)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        xaxis=dict(
            title=dict(text=t["sr_kast_scatter_xaxis"], font=dict(size=12, color="#333")),
            showgrid=True,
            gridcolor="#f0f0f0",
            tickfont=dict(size=10, color="#333"),
            zeroline=True,
            zerolinecolor=TREND_GRAY,
            zerolinewidth=1,
            range=[x_lo - x_pad, x_hi + x_pad],
        ),
        yaxis=dict(
            title=dict(text=t["sr_kast_scatter_yaxis"], font=dict(size=12, color="#333")),
            showgrid=True,
            gridcolor="#f0f0f0",
            tickfont=dict(size=10, color="#333"),
            range=[y_lo - y_pad, y_hi + y_pad],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=10, color="#333"),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#e0e0e0",
            font=dict(size=11, family="Liberation Sans, Arial"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_growth_and_loyalty(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the growth and loyalty block with 2 switchable views:
    Growth (top N) and Loyalty (bottom N).
    """
    df_all = _compute_kast_growth_commune(df_fr, df_sr)

    option_dual = t["sr_kast_radio_dual"]
    option_loyalty = t["sr_kast_radio_lealtad"]

    view = st.radio(
        t["sr_kast_radio_label"],
        [option_dual, option_loyalty],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
        key="kast_crecimiento_dual_vista",
    )

    if view == option_dual:
        render_section_title(t["sr_kast_section_growth_top_abs"].format(n=N_GROWTH))
        top_abs = df_all.nlargest(N_GROWTH, "__abs_growth").reset_index(drop=True)
        _render_top10_growth_table(top_abs, t["sr_kast_scatter_label_top_abs"].format(n=N_GROWTH), t)

        render_section_title(t["sr_kast_section_growth_top_rel"].format(n=N_GROWTH))
        top_rel = df_all.nlargest(N_GROWTH, "__rel_growth_pct").reset_index(drop=True)
        _render_top10_growth_table(top_rel, t["sr_kast_scatter_label_top_rel"].format(n=N_GROWTH), t)

        render_section_title(t["sr_kast_section_growth_scatter"])
        _render_growth_scatter(
            df_all=df_all,
            df_primary=top_abs,
            df_secondary=top_rel,
            primary_label=t["sr_kast_scatter_label_top_abs"].format(n=N_GROWTH),
            secondary_label=t["sr_kast_scatter_label_top_rel"].format(n=N_GROWTH),
            title="Crecimiento Dual",
            t=t,
        )

    else:  # Loyalty
        render_section_title(t["sr_kast_section_growth_bot_abs"].format(n=N_GROWTH))
        bot_abs = df_all.nsmallest(N_GROWTH, "__abs_growth").reset_index(drop=True)
        _render_top10_growth_table(bot_abs, t["sr_kast_scatter_label_bot_abs"].format(n=N_GROWTH), t)

        render_section_title(t["sr_kast_section_growth_bot_rel"].format(n=N_GROWTH))
        bot_rel = df_all.nsmallest(N_GROWTH, "__rel_growth_pct").reset_index(drop=True)
        _render_top10_growth_table(bot_rel, t["sr_kast_scatter_label_bot_rel"].format(n=N_GROWTH), t)

        render_section_title(t["sr_kast_section_growth_scatter"])
        _render_growth_scatter(
            df_all=df_all,
            df_primary=bot_abs,
            df_secondary=bot_rel,
            primary_label=t["sr_kast_scatter_label_bot_abs"].format(n=N_GROWTH),
            secondary_label=t["sr_kast_scatter_label_bot_rel"].format(n=N_GROWTH),
            title="Lealtad de Base",
            t=t,
        )


# ============================================================================
# SECTION NO. 8 — KAST BY COMMUNE SIZE
# ============================================================================
def _render_kast_by_commune_size(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """
    Render the horizontal bar chart: Kast's % by commune size (runoff).
    The % is Kast / (Kast + Jara). Communes are classified into 5 population
    brackets.
    """
    df = df_sr[["commune_id", "kast_votes", "jara_votes"]].copy()
    df = df.merge(dim[["commune_id", "population"]], on="commune_id", how="left")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df = df.dropna(subset=["population"]).copy()

    df["__valid"] = df["kast_votes"] + df["jara_votes"]

    def _classify(pop: float):
        for tr in POPULATION_BRACKETS_KAST:
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
        kast_votes=("kast_votes", "sum"),
        valid_votes=("__valid", "sum"),
    )
    agg["kast_pct"] = (agg["kast_votes"] / agg["valid_votes"].replace(0, 1) * 100).round(2)

    if agg.empty:
        st.info(t["sr_kast_no_data_population"])
        return

    sub_map = {tr["label"]: tr["sub"] for tr in POPULATION_BRACKETS_KAST}
    agg["zona"] = agg["__bracket"].apply(lambda x: f"{x} · {sub_map.get(x, '')}")

    agg["kast_fmt"] = agg["kast_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    agg["valid_fmt"] = agg["valid_votes"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    agg["pop_fmt"] = agg["population"].apply(lambda x: f"{int(x):,}".replace(",", "."))
    agg["winner"] = "Kast"

    render_section_subtitle(t["sr_kast_sub_size"])

    _plot_top_bar(
        plot_df=agg,
        t=t,
        value_col="kast_pct",
        label_col="zona",
        title="",
        xaxis_title=t["sr_kast_colorbar_pct_kast"] + " " + t["sr_kast_kpi_pct_validos_sub"],
        value_fmt=lambda v: f"{v:.1f}%",
        extra_hover_cols=["kast_fmt", "valid_fmt", "pop_fmt"],
        height_per_bar=44,
        height_min=320,
        bar_color=KAST_COLOR,
        rounded=True,
        transparent_bg=True,
        font_boost=1.0,
    )


# ============================================================================
# SECTION NO. 9 — KAST SIZE × MACROZONE
# ============================================================================
def _compute_kast_size_x_macrozone(df_sr: pd.DataFrame, dim: pd.DataFrame):
    """
    Cross runoff votes with dim_commune (population, macrozone) and build
    a Commune-size × Macrozone matrix with Kast's % weighted by casted votes.
    """
    df = df_sr[["commune_id", "kast_votes", "casted_votes"]].copy()
    df = df.merge(
        dim[["commune_id", "population", "macrozone", "macrozone_order"]],
        on="commune_id",
        how="left",
    )
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df = df.dropna(subset=["population", "macrozone"]).copy()

    df["__valid"] = df["casted_votes"]

    def _classify(pop: float):
        for tr in POPULATION_BRACKETS_KAST:
            if tr["min"] is not None and pop < tr["min"]:
                continue
            if tr["max"] is not None and pop > tr["max"]:
                continue
            return tr["label"]
        return None

    df["__bracket"] = df["population"].apply(_classify)
    df = df.dropna(subset=["__bracket"])

    size_order = [tr["label"] for tr in POPULATION_BRACKETS_KAST]

    agg = df.groupby(["__bracket", "macrozone"], as_index=False).agg(
        kast_votes=("kast_votes", "sum"),
        valid_votes=("__valid", "sum"),
        communes=("commune_id", "count"),
    )
    agg["kast_pct"] = agg["kast_votes"] / agg["valid_votes"].replace(0, 1) * 100

    pivot = agg.pivot(index="__bracket", columns="macrozone", values="kast_pct")
    pivot = pivot.reindex(index=size_order, columns=MACROZONE_ORDER)

    pivot_n = agg.pivot(index="__bracket", columns="macrozone", values="communes")
    pivot_n = pivot_n.reindex(index=size_order, columns=MACROZONE_ORDER)

    return pivot, pivot_n


def _render_kast_size_x_macrozone(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """
    Render the heatmap: Commune size × Macrozone with Kast's % weighted by
    casted votes. White text on cells with Kast % ≥ 55.
    """
    pivot, pivot_n = _compute_kast_size_x_macrozone(df_sr, dim)

    if pivot.empty or pivot.isna().all().all():
        st.info(t["sr_kast_no_data_size_macro"])
        return

    sub_map = {tt["label"]: tt["sub"] for tt in POPULATION_BRACKETS_KAST}

    def _fmt_row_label(lbl: str) -> str:
        sub = sub_map.get(lbl, "")
        return f"{lbl}\n{sub}" if sub else lbl

    plot_df = pivot.copy()
    plot_n = pivot_n.copy()
    plot_df.index = [_fmt_row_label(i) for i in plot_df.index]
    plot_n.index = [_fmt_row_label(i) for i in plot_n.index]

    render_section_subtitle(t["sr_kast_sub_size_macro"])

    empty_text = [["" for _ in plot_df.columns] for _ in plot_df.index]

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

    colorscale = HEATMAP_SCALE_PCT_KAST

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=plot_df.values,
        x=plot_df.columns.tolist(),
        y=plot_df.index.tolist(),
        colorscale=colorscale,
        zmin=40,
        zmax=75,
        showscale=True,
        text=empty_text,
        customdata=customdata,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[1]}<br>"
            "% Kast: %{customdata[2]}<br>"
            "Comunas: %{customdata[3]}"
            "<extra></extra>"
        ),
        xgap=2,
        ygap=2,
        colorbar=dict(
            title=dict(text=t["sr_kast_colorbar_pct_kast"], font=dict(size=10)),
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
            if val >= 55:
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
            title=dict(text=t["sr_kast_axis_macrozone"], font=dict(size=12, color="#333")),
            tickfont=dict(size=10, color="#333"),
            side="bottom",
        ),
        yaxis=dict(
            title=dict(text=t["sr_kast_axis_size"], font=dict(size=12, color="#333")),
            tickfont=dict(size=10, color="#333"),
            autorange="reversed",
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    render_section_subtitle(t["sr_kast_sub_size_macro_footer"])


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
def _build_kpis_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the KPI cards section."""
    _render_kpi_cards(df_sr, t)


def _build_strongholds_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the strongholds section."""
    _render_strongholds_top10(df_sr, t)


def _build_regional_strongholds_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the regional strongholds section."""
    _render_regional_strongholds(df_sr, t)


def _build_macrozone_profile_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """Build the macrozone profile section."""
    _render_macrozone_profile(df_fr, df_sr, dim, t)


def _build_reversed_duels_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the reversed duels section."""
    _render_reversed_duels(df_fr, df_sr, t)


def _build_close_margins_section(df_sr: pd.DataFrame, t: dict) -> None:
    """Build the close margins section."""
    _render_close_margins(df_sr, t)


def _build_kast_protest_vote_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the protest vote section."""
    _render_kast_protest_vote(df_fr, df_sr, t)


def _build_growth_and_loyalty_section(df_fr: pd.DataFrame, df_sr: pd.DataFrame, t: dict) -> None:
    """Build the growth and loyalty section."""
    _render_growth_and_loyalty(df_fr, df_sr, t)


def _build_kast_by_commune_size_section(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """Build the Kast-by-commune-size section."""
    _render_kast_by_commune_size(df_sr, dim, t)


def _build_kast_size_x_macrozone_section(df_sr: pd.DataFrame, dim: pd.DataFrame, t: dict) -> None:
    """Build the Kast-size × macrozone section."""
    _render_kast_size_x_macrozone(df_sr, dim, t)


# ============================================================================
# RENDER (orchestrator)
# ============================================================================
def render(t: dict) -> None:
    """
    Render the José Antonio Kast page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    render_view_title(KAST_NAME)

    try:
        df_fr = load_fact_first_round_2025()
        df_sr = load_fact_second_round_2025()
        dim = load_dim_commune()

        _build_kpis_section(df_sr, t)

        with st.expander(t["sr_kast_exp_bastiones"], expanded=False):
            _build_strongholds_section(df_sr, t)

        with st.expander(t["sr_kast_exp_regionales"], expanded=False):
            _build_regional_strongholds_section(df_sr, t)

        with st.expander(t["sr_kast_exp_perfil_macro"], expanded=False):
            _build_macrozone_profile_section(df_fr, df_sr, dim, t)

        with st.expander(t["sr_kast_exp_duelos"], expanded=False):
            _build_reversed_duels_section(df_fr, df_sr, t)

        with st.expander(t["sr_kast_exp_margenes"], expanded=False):
            _build_close_margins_section(df_sr, t)

        with st.expander(t["sr_kast_exp_protesta"], expanded=False):
            _build_kast_protest_vote_section(df_fr, df_sr, t)

        with st.expander(t["sr_kast_exp_crecimiento_dual"], expanded=False):
            _build_growth_and_loyalty_section(df_fr, df_sr, t)

        with st.expander(t["sr_kast_exp_gradiente_size"], expanded=False):
            _build_kast_by_commune_size_section(df_sr, dim, t)

        with st.expander(t["sr_kast_exp_gradiente_intensidad"], expanded=False):
            _build_kast_size_x_macrozone_section(df_sr, dim, t)

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
# 1. POPULATION_BRACKETS_KAST labels and subtitles:
#      "Rural" / "menos de 10.000 hab."
#      "Rural-urbano" / "10.000 – 49.999 hab."
#      "Centros urbanos pequeños" / "50.000 – 99.999 hab."
#      "Centros urbanos medios" / "100.000 – 199.999 hab."
#      "Grandes centros urbanos" / "más de 200.000 hab."
#
#    These appear in the commune-size charts (sections 8 and 9). The labels
#    describe the population brackets used to classify communes by size.
#
# 2. `label_map` inside `_plot_top_bar`:
#      "Región" = region, "Votos totales" = total casted votes,
#      "Votos válidos" = valid votes, "Votos nulos" = null votes,
#      "Votos blancos" = blank votes, "% nulos" = null %,
#      "% blancos" = blank %, "Comuna" = commune,
#      "Votos Kast" = Kast votes, "Población" = population.
#
#    These are used only in the Plotly hover tooltip, not in the static
#    HTML. They could be moved to translations.py and resolved per call,
#    but that would require passing `t` to `label_map` at the call site.
#
# 3. The `title` parameter passed to `_render_growth_scatter`:
#      "Crecimiento Dual" = Dual Growth (top N view)
#      "Lealtad de Base" = Base Loyalty (bottom N view)
#
#    These are passed as a parameter to `_render_growth_scatter` but are
#    not actually used inside the function (the scatter has no title). They
#    are kept as-is for documentation purposes. If they are ever used, they
#    should be moved to translations.py.
#
# When these are moved, add the corresponding keys to translations.py with
# the prefix `sr_kast_` and update the call sites. No other code depends on
# them.
