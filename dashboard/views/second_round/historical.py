"""
Second Round — Historical (2021 vs 2025)
============================================================================
Comparison of the second presidential round between 2021 (Boric vs Kast)
and 2025 (Kast vs Jara).

Featured cards at the top (4 cards):
    1. Growth in casted votes (voluntary → compulsory voting)
    2. Margin 2025 (Kast vs Jara) on valid votes
    3. Communes that changed winner (territorial realignment)
    4. Kast: absolute growth (protagonist of the change)

Sections (all collapsible):
    1. National participation 2021 vs 2025
    2. National result: Boric vs Kast (2021) and Kast vs Jara (2025)
    3. Political block evolution 2021 → 2025
    4. Electoral realignment: transition matrix 2021 → 2025
    5. Kast: evolution by commune 2021 → 2025
    6. The left: Boric 2021 → Jara 2025
    7. Communes that changed winner: decisive vs close

Transformation helpers (clean_html, format_number, hex_to_rgba) are imported
from utils.html_helpers.
View and section titles live in components.titles.
Colors live in config.constants.

Notes
-----
- `TREND_GRAY` is imported from config.constants. The old name
  `GRIS_TENDENCIA` is still available as an alias but should not be used
  in new code; this file uses the new name directly.
- `_render_featured_cards` recomputes the communes-changed count that is
  also computed in `_render_realignment`. This duplication is pre-existing
  and intentionally not resolved in this refactor to avoid changing the
  rendering behavior.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import (
    load_fact_second_round_2021,
    load_fact_second_round_2025,
)
from utils.html_helpers import (
    clean_html as _clean_html,
    format_number as _fmt_number,
    hex_to_rgba as _hex_to_rgba,
)
from config.constants import (
    COLOR_NEGATIVE,
    COLOR_NEUTRAL_INDICATOR,
    COLOR_POSITIVE,
    NEUTRAL_COLOR,
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
KAST_COLOR = _get_candidate_color("José Antonio Kast")
JARA_COLOR = _get_candidate_color("Jeannette Jara")


# ============================================================================
# LOCAL HELPERS (only visual formatting)
# ============================================================================
def _table_gap():
    """6px gap between the bottom of a table and the next element.
    Rendered in a separate st.markdown call so Streamlit doesn't collapse it."""
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)


def _render_comment(text: str, bold: bool = False) -> None:
    weight = "700" if bold else "400"
    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; "
        f"font-size: 10pt; color: #6b7280; margin-top: 4px; margin-bottom: 20px; "
        f"line-height: 1.5; max-width: 900px; font-weight: {weight};\">{text}</div>",
        unsafe_allow_html=True,
    )


def _render_nb_cards_row(cards: list) -> None:
    """Render a row of nb-cards. Each card is (label, value, sub, accent)."""
    inner = ""
    for label, value, sub, accent in cards:
        inner += f"""
        <div class="nb-card">
            <div class="nb-card-label">{label}</div>
            <div class="nb-card-value">{value}</div>
            <div class="nb-card-sub">{sub}</div>
        </div>
        """
    html = _NB_CARD_CSS + f'<div class="nb-cards">{inner}</div>'
    st.markdown(_clean_html(html), unsafe_allow_html=True)


def _render_page_footer(t: dict) -> None:
    st.markdown(_clean_html(_FOOTER_CSS + f"""
    <div class="page-footer"><p>{t['data_source']} · {t['data_source_note']}</p></div>
    """), unsafe_allow_html=True)


def _table_css(clase: str) -> str:
    return f"""
    <style>
        .{clase} {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-family: "Liberation Sans", Arial, sans-serif;
        }}
        .{clase} table {{
            width: 100%;
            border-collapse: collapse;
            border-spacing: 0;
            font-family: "Liberation Sans", Arial, sans-serif;
            margin: 0;
        }}
        .{clase} th,
        .{clase} td {{
            border-left: none !important;
            border-right: none !important;
            border-top: none;
            margin: 0;
        }}
        .{clase} th {{
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
        .{clase} td {{
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
        .{clase} tr:first-child td {{
            padding-top: 8px;
        }}
        .{clase} tr:last-child td {{
            border-bottom: none;
            padding-bottom: 8px;
        }}
        .{clase} tr:hover td {{
            background: #fafaf8;
        }}
        .hi-color-box {{
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
        .hi-pill {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 6px;
            font-size: 8pt;
            font-weight: 600;
            white-space: nowrap;
            text-align: center;
            min-width: 70px;
        }}
    </style>
    """


def _plotly_title(text: str) -> dict:
    return dict(
        text=text,
        font=dict(size=16, color="#111827", family="Liberation Sans, Arial, sans-serif"),
        x=0, xanchor="left",
    )


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

_BLOCKS_CSS = """
<style>
    .blocks-barras-wrap { font-family: "Liberation Sans", Arial, sans-serif; max-width: 940px; }
    .blocks-year { margin-bottom: 36px; }
    .blocks-year-title { font-size: 12pt; font-weight: 700; color: #111827; margin-bottom: 10px; }
    .blocks-labels { display: flex; margin-bottom: 6px; font-size: 8pt; color: #6b7280; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; }
    .blocks-labels > div { white-space: nowrap; }
    .blocks-bar-wrap { position: relative; margin-bottom: 14px; }
    .blocks-bar { display: flex; height: 48px; border-radius: 6px; overflow: hidden; }
    .blocks-bar > div { display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 13pt; }
    .blocks-midline { position: absolute; top: -8px; bottom: -8px; left: 50%; width: 0; border-left: 1px dashed #6b7280; pointer-events: none; }
    .blocks-details { display: flex; margin-bottom: 8px; }
    .blocks-detail { padding: 0 6px; }
    .blocks-cands { font-size: 10pt; color: #333; margin-bottom: 4px; }
    .blocks-votes { font-size: 12pt; font-weight: 700; color: #111827; }
    .blocks-legend { display: flex; flex-direction: column; gap: 8px; font-size: 9pt; color: #333; margin-top: 24px; }
    .legend-item { display: flex; align-items: center; gap: 8px; }
    .legend-dot { width: 13px; height: 13px; border-radius: 3px; display: inline-block; flex-shrink: 0; }
</style>
"""


# ============================================================================
# WINNER HELPERS
# ============================================================================
def _winner_labels(t: dict) -> dict:
    """Return winner key -> translated label."""
    return {
        "boric": t["sr_hist_winner_boric"],
        "jara":  t["sr_hist_winner_jara"],
        "kast":  t["sr_hist_winner_kast"],
    }


def _add_winner_sr2021(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["winner_2021"] = "kast"
    out.loc[out["boric_votes"] > out["kast_votes"], "winner_2021"] = "boric"
    out["winner_pct_2021"] = out[["boric_pct", "kast_pct"]].max(axis=1)
    return out


def _add_winner_sr2025(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["winner_2025"] = "kast"
    out.loc[out["jara_votes"] > out["kast_votes"], "winner_2025"] = "jara"
    out["winner_pct_2025"] = out[["jara_pct", "kast_pct"]].max(axis=1)
    return out


def _candidate_color(winner_key: str) -> str:
    """Color for a winner key ('boric' / 'jara' / 'kast')."""
    if winner_key in ("boric", "jara"):
        return JARA_COLOR
    return KAST_COLOR


def _compute_transitions(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> pd.DataFrame:
    """
    Merge SR 2021 and SR 2025 winners per commune, with translated labels.

    Parameters
    ----------
    df_2021 : pd.DataFrame
        Second round 2021 fact table.
    df_2025 : pd.DataFrame
        Second round 2025 fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    pd.DataFrame
        One row per commune, with columns: commune_id, commune_name,
        region_name, winner_2021, winner_2025, winner_2021_label,
        winner_2025_label, change_type.
    """
    df_21 = _add_winner_sr2021(df_2021)
    df_25 = _add_winner_sr2025(df_2025)

    labels = _winner_labels(t)

    merged = df_21[["commune_id", "commune_name", "region_name", "winner_2021"]].merge(
        df_25[["commune_id", "winner_2025"]],
        on="commune_id",
        how="inner",
    )
    merged["winner_2021_label"] = merged["winner_2021"].map(labels)
    merged["winner_2025_label"] = merged["winner_2025"].map(labels)
    merged["change_type"] = (
        (merged["winner_2021"] == merged["winner_2025"])
        .map({True: t["sr_hist_change_same"], False: t["sr_hist_change_changed"]})
    )
    return merged


# ============================================================================
# SECTION NO. 0 — FEATURED CARDS
# ============================================================================
def _render_featured_cards(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the 4 featured cards at the top of the view.

    Parameters
    ----------
    df_2021 : pd.DataFrame
        Second round 2021 fact table.
    df_2025 : pd.DataFrame
        Second round 2025 fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    total_cast_2021 = int(df_2021["casted_votes"].sum())
    total_cast_2025 = int(df_2025["casted_votes"].sum())
    cast_growth = (
        (total_cast_2025 - total_cast_2021) / total_cast_2021 * 100
        if total_cast_2021 else 0
    )

    valid_2025 = (
        total_cast_2025
        - int(df_2025["blank_votes"].sum())
        - int(df_2025["null_votes"].sum())
    )
    kast_2025 = int(df_2025["kast_votes"].sum())
    jara_2025 = int(df_2025["jara_votes"].sum())
    margin_2025_pp = (
        (kast_2025 - jara_2025) / valid_2025 * 100 if valid_2025 else 0
    )

    df_21 = _add_winner_sr2021(df_2021)
    df_25 = _add_winner_sr2025(df_2025)
    merge = df_21[["commune_id", "winner_2021"]].merge(
        df_25[["commune_id", "winner_2025"]],
        on="commune_id",
        how="inner",
    )
    communes_changed = int((merge["winner_2021"] != merge["winner_2025"]).sum())
    total_communes = len(merge)
    pct_changed = (communes_changed / total_communes * 100) if total_communes else 0

    kast_2021 = int(df_2021["kast_votes"].sum())
    kast_growth_pct = (
        (kast_2025 - kast_2021) / kast_2021 * 100 if kast_2021 else 0
    )

    cards = [
        (
            t["sr_hist_kpi_cast_growth"],
            f"+{cast_growth:.1f}%",
            t["sr_hist_kpi_sr_growth_sub"],
            COLOR_POSITIVE,
        ),
        (
            t["sr_hist_kpi_margin_2025"],
            f"+{margin_2025_pp:.2f} pp",
            t["sr_hist_kpi_on_valid"],
            KAST_COLOR,
        ),
        (
            t["sr_hist_kpi_comunas_cambiaron"],
            str(communes_changed),
            t["sr_hist_kpi_pct_total"].format(pct=f"{pct_changed:.1f}"),
            None,
        ),
        (
            t["sr_hist_kpi_kast_growth"],
            f"+{kast_growth_pct:.0f}%",
            t["sr_hist_kpi_kast_unique"],
            KAST_COLOR,
        ),
    ]
    _render_nb_cards_row(cards)


# ============================================================================
# SECTION NO. 1 — PARTICIPATION 2021 VS 2025
# ============================================================================
def _render_participation(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the participation table comparing SR 2021 and SR 2025.
    """
    total_cast_2021 = int(df_2021["casted_votes"].sum())
    total_blank_2021 = int(df_2021["blank_votes"].sum())
    total_null_2021 = int(df_2021["null_votes"].sum())
    total_valid_2021 = total_cast_2021 - total_blank_2021 - total_null_2021

    total_cast_2025 = int(df_2025["casted_votes"].sum())
    total_blank_2025 = int(df_2025["blank_votes"].sum())
    total_null_2025 = int(df_2025["null_votes"].sum())
    total_valid_2025 = total_cast_2025 - total_blank_2025 - total_null_2025

    rows = [
        (t["casted_votes"], total_cast_2021, total_cast_2025, COLOR_POSITIVE),
        (t["valid_votes"],  total_valid_2021, total_valid_2025, COLOR_POSITIVE),
        (t["null_votes"],   total_null_2021, total_null_2025, COLOR_NEGATIVE),
        (t["blank_votes"],  total_blank_2021, total_blank_2025, COLOR_NEGATIVE),
    ]

    rows_html = ""
    for label, v21, v25, color in rows:
        delta = v25 - v21
        delta_pct = (delta / v21 * 100) if v21 else 0
        delta_sign = "+" if delta >= 0 else ""

        rows_html += (
            f"<tr>"
            f'<td style="color:#333;">{label}</td>'
            f'<td style="text-align:right; color:#666;">{_fmt_number(v21)}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{_fmt_number(v25)}</td>'
            f'<td style="text-align:right; color:{color};">{delta_sign}{_fmt_number(delta)}</td>'
            f'<td style="text-align:right; color:{color};">{delta_sign}{delta_pct:.2f}%</td>'
            f"</tr>"
        )

    pct_rows = [
        (t["sr_hist_row_pct_valid"], total_valid_2021 / total_cast_2021 * 100, total_valid_2025 / total_cast_2025 * 100),
        (t["sr_hist_row_pct_null"],  total_null_2021  / total_cast_2021 * 100, total_null_2025  / total_cast_2025 * 100),
        (t["sr_hist_row_pct_blank"], total_blank_2021 / total_cast_2021 * 100, total_blank_2025 / total_cast_2025 * 100),
    ]

    rows_pct_html = ""
    for label, p21, p25 in pct_rows:
        delta_pp = p25 - p21
        delta_sign = "+" if delta_pp >= 0 else ""
        rows_pct_html += (
            f"<tr>"
            f'<td style="color:#333;">{label}</td>'
            f'<td style="text-align:right; color:#666;">{p21:.2f}%</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{p25:.2f}%</td>'
            f'<td style="text-align:right; color:{COLOR_NEGATIVE};">{delta_sign}{delta_pp:.2f} pp</td>'
            f"<td></td>"
            f"</tr>"
        )

    html = _table_css("hi-tabla-participacion") + f"""
    <div class="hi-tabla-participacion">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_hist_th_metric']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_sr_2021']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_sr_2025']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_delta_abs']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_delta_pct']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
                {rows_pct_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

    _render_comment(t["sr_hist_note_participacion"])


# ============================================================================
# SECTION NO. 2 — NATIONAL RESULT SR 2021 vs SR 2025
# ============================================================================
def _render_national_result(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the national result table: Boric vs Kast (2021) and
    Kast vs Jara (2025).
    """
    v2021 = (
        int(df_2021["casted_votes"].sum())
        - int(df_2021["blank_votes"].sum())
        - int(df_2021["null_votes"].sum())
    )
    boric_v = int(df_2021["boric_votes"].sum())
    kast21_v = int(df_2021["kast_votes"].sum())
    boric_pct = boric_v / v2021 * 100 if v2021 else 0
    kast21_pct = kast21_v / v2021 * 100 if v2021 else 0
    winner_2021 = "Boric" if boric_v > kast21_v else "Kast"
    margin_2021_pp = abs(boric_pct - kast21_pct)
    margin_2021_v = abs(boric_v - kast21_v)

    v2025 = (
        int(df_2025["casted_votes"].sum())
        - int(df_2025["blank_votes"].sum())
        - int(df_2025["null_votes"].sum())
    )
    jara_v = int(df_2025["jara_votes"].sum())
    kast25_v = int(df_2025["kast_votes"].sum())
    jara_pct = jara_v / v2025 * 100 if v2025 else 0
    kast25_pct = kast25_v / v2025 * 100 if v2025 else 0
    winner_2025 = "Kast" if kast25_v > jara_v else "Jara"
    margin_2025_pp = abs(jara_pct - kast25_pct)
    margin_2025_v = abs(jara_v - kast25_v)

    def _pct_style(is_winner: bool, winner_color: str) -> str:
        if is_winner:
            return f"text-align:right; color:{winner_color};"
        return "text-align:right; color:#666;"

    boric_wins_2021 = winner_2021 == "Boric"
    kast_wins_2021 = not boric_wins_2021
    kast_wins_2025 = winner_2025 == "Kast"
    jara_wins_2025 = not kast_wins_2025

    cell_boric = f'<span class="hi-color-box" style="background:{JARA_COLOR};"></span>Boric'
    cell_jara = f'<span class="hi-color-box" style="background:{JARA_COLOR};"></span>Jeannette Jara'
    cell_kast_21 = f'<span class="hi-color-box" style="background:{KAST_COLOR};"></span>José Antonio Kast'
    cell_kast_25 = f'<span class="hi-color-box" style="background:{KAST_COLOR};"></span>José Antonio Kast'

    def _pill(winner: str) -> str:
        color = JARA_COLOR if winner in ("Boric", "Jara") else KAST_COLOR
        bg = _hex_to_rgba(color, 0.12)
        return f'<span class="hi-pill" style="background:{bg}; color:{color};">{t["sr_hist_pill_elected"].format(winner=winner)}</span>'

    html = _table_css("hi-tabla-resultado-nacional") + f"""
    <div class="hi-tabla-resultado-nacional" style="max-width:960px;">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_hist_th_eleccion']}</th>
                    <th>{t['sr_hist_th_cand_izq']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_votos']}</th>
                    <th>{t['sr_hist_th_cand_der']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_votos']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_margin']}</th>
                    <th>{t['sr_hist_th_ganador']}</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color:#333;">SR 2021</td>
                    <td>{cell_boric}</td>
                    <td style="{_pct_style(boric_wins_2021, JARA_COLOR)}">{boric_pct:.2f}%</td>
                    <td style="text-align:right; color:#666;">{_fmt_number(boric_v)}</td>
                    <td>{cell_kast_21}</td>
                    <td style="{_pct_style(kast_wins_2021, KAST_COLOR)}">{kast21_pct:.2f}%</td>
                    <td style="text-align:right; color:#666;">{_fmt_number(kast21_v)}</td>
                    <td style="text-align:right; font-weight:700; color:#111827;">{margin_2021_pp:.2f} pp</td>
                    <td>{_pill(winner_2021)}</td>
                </tr>
                <tr>
                    <td style="color:#333;">SR 2025</td>
                    <td>{cell_jara}</td>
                    <td style="{_pct_style(jara_wins_2025, JARA_COLOR)}">{jara_pct:.2f}%</td>
                    <td style="text-align:right; color:#666;">{_fmt_number(jara_v)}</td>
                    <td>{cell_kast_25}</td>
                    <td style="{_pct_style(kast_wins_2025, KAST_COLOR)}">{kast25_pct:.2f}%</td>
                    <td style="text-align:right; color:#666;">{_fmt_number(kast25_v)}</td>
                    <td style="text-align:right; font-weight:700; color:#111827;">{margin_2025_pp:.2f} pp</td>
                    <td>{_pill(winner_2025)}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html), unsafe_allow_html=True)
    _table_gap()

    _render_comment(
        t["sr_hist_note_resultado"].format(
            m21=f"{margin_2021_pp:.2f}",
            v21=_fmt_number(margin_2021_v),
            m25=f"{margin_2025_pp:.2f}",
            v25=_fmt_number(margin_2025_v),
        )
    )


# ============================================================================
# SECTION NO. 3 — POLITICAL BLOCKS 2021 VS 2025
# ============================================================================
def _render_blocks(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the political block evolution: a table with the two blocks
    present in the second round (left and right) and two stacked bars
    (2021 and 2025).
    """
    total_valid_2021 = (
        int(df_2021["casted_votes"].sum())
        - int(df_2021["blank_votes"].sum())
        - int(df_2021["null_votes"].sum())
    )
    total_valid_2025 = (
        int(df_2025["casted_votes"].sum())
        - int(df_2025["blank_votes"].sum())
        - int(df_2025["null_votes"].sum())
    )

    boric_2021 = int(df_2021["boric_votes"].sum())
    kast_2021 = int(df_2021["kast_votes"].sum())
    jara_2025 = int(df_2025["jara_votes"].sum())
    kast_2025 = int(df_2025["kast_votes"].sum())

    blocks = [
        {
            "block": t["fr_hist_bloque_izq"],
            "cand_2021": "Boric",
            "cand_2025": "Jara",
            "votes_2021": boric_2021,
            "votes_2025": jara_2025,
            "color": JARA_COLOR,
            "delta_pct_color": COLOR_NEGATIVE,
        },
        {
            "block": t["fr_hist_bloque_der_cons"],
            "cand_2021": "Kast",
            "cand_2025": "Kast",
            "votes_2021": kast_2021,
            "votes_2025": kast_2025,
            "color": KAST_COLOR,
            "delta_pct_color": COLOR_POSITIVE,
        },
    ]

    rows_html = ""
    for b in blocks:
        p21 = (b["votes_2021"] / total_valid_2021 * 100) if total_valid_2021 else 0
        p25 = (b["votes_2025"] / total_valid_2025 * 100) if total_valid_2025 else 0
        rel = (
            (b["votes_2025"] - b["votes_2021"]) / b["votes_2021"] * 100
            if b["votes_2021"] else 0
        )
        rel_sign = "+" if rel >= 0 else ""

        rows_html += (
            f"<tr>"
            f'<td style="font-weight:600;">'
            f'<span class="hi-color-box" style="background:{b["color"]};"></span>{b["block"]}'
            f'</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{b["cand_2021"]}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{b["cand_2025"]}</td>'
            f'<td style="text-align:right; color:#666;">{_fmt_number(b["votes_2021"])}</td>'
            f'<td style="text-align:right; color:#666;">{p21:.2f}%</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{_fmt_number(b["votes_2025"])}</td>'
            f'<td style="text-align:right; font-weight:700; color:#111827;">{p25:.2f}%</td>'
            f'<td style="text-align:right; color:{b["delta_pct_color"]};">{rel_sign}{rel:.1f}%</td>'
            f"</tr>"
        )

    html = _table_css("hi-tabla-bloques") + f"""
    <div class="hi-tabla-bloques">
        <table>
            <thead>
                <tr>
                    <th rowspan="2">{t['sr_hist_th_bloque']}</th>
                    <th rowspan="2">{t['sr_hist_th_cand_2021']}</th>
                    <th rowspan="2">{t['sr_hist_th_cand_2025']}</th>
                    <th colspan="2" style="text-align:center;">{t['sr_hist_th_sr_2021']}</th>
                    <th colspan="2" style="text-align:center;">{t['sr_hist_th_sr_2025']}</th>
                    <th rowspan="2" style="text-align:right;">{t['sr_hist_th_delta_pp']}</th>
                </tr>
                <tr>
                    <th style="text-align:right;">{t['sr_hist_th_votos']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_votos']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct']}</th>
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

    _render_comment(t["sr_hist_note_bloques"])

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    COLOR_LEFT = JARA_COLOR
    COLOR_RIGHT = KAST_COLOR

    pct_left_2021 = (boric_2021 / total_valid_2021 * 100) if total_valid_2021 else 0
    pct_right_2021 = (kast_2021 / total_valid_2021 * 100) if total_valid_2021 else 0
    pct_left_2025 = (jara_2025 / total_valid_2025 * 100) if total_valid_2025 else 0
    pct_right_2025 = (kast_2025 / total_valid_2025 * 100) if total_valid_2025 else 0

    html_bars = _BLOCKS_CSS + f"""
    <div class="blocks-barras-wrap">
        <div class="blocks-year">
            <div class="blocks-year-title">2021</div>
            <div class="blocks-labels">
                <div style="width: {pct_left_2021}%; text-align: left;">{t['fr_hist_bloque_izq']}</div>
                <div style="width: {pct_right_2021}%; text-align: right;">{t['fr_hist_bloque_der_cons']}</div>
            </div>
            <div class="blocks-bar-wrap">
                <div class="blocks-midline"></div>
                <div class="blocks-bar">
                    <div style="width: {pct_left_2021}%; background: {COLOR_LEFT};">{pct_left_2021:.2f}%</div>
                    <div style="width: {pct_right_2021}%; background: {COLOR_RIGHT};">{pct_right_2021:.2f}%</div>
                </div>
            </div>
            <div class="blocks-details">
                <div class="blocks-detail" style="width: {pct_left_2021}%; text-align: left;">
                    <div class="blocks-cands">Boric</div>
                    <div class="blocks-votes">{_fmt_number(boric_2021)} {t['votes']}</div>
                </div>
                <div class="blocks-detail" style="width: {pct_right_2021}%; text-align: right;">
                    <div class="blocks-cands">Kast</div>
                    <div class="blocks-votes">{_fmt_number(kast_2021)} {t['votes']}</div>
                </div>
            </div>
        </div>

        <div class="blocks-year">
            <div class="blocks-year-title">2025</div>
            <div class="blocks-labels">
                <div style="width: {pct_left_2025}%; text-align: left;">{t['fr_hist_bloque_izq']}</div>
                <div style="width: {pct_right_2025}%; text-align: right;">{t['fr_hist_bloque_der_cons']}</div>
            </div>
            <div class="blocks-bar-wrap">
                <div class="blocks-midline"></div>
                <div class="blocks-bar">
                    <div style="width: {pct_left_2025}%; background: {COLOR_LEFT};">{pct_left_2025:.2f}%</div>
                    <div style="width: {pct_right_2025}%; background: {COLOR_RIGHT};">{pct_right_2025:.2f}%</div>
                </div>
            </div>
            <div class="blocks-details">
                <div class="blocks-detail" style="width: {pct_left_2025}%; text-align: left;">
                    <div class="blocks-cands">Jara</div>
                    <div class="blocks-votes">{_fmt_number(jara_2025)} {t['votes']}</div>
                </div>
                <div class="blocks-detail" style="width: {pct_right_2025}%; text-align: right;">
                    <div class="blocks-cands">Kast</div>
                    <div class="blocks-votes">{_fmt_number(kast_2025)} {t['votes']}</div>
                </div>
            </div>
        </div>

        <div class="blocks-legend">
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_LEFT};"></span>{t['fr_hist_bloque_izq']}</div>
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_RIGHT};"></span>{t['fr_hist_bloque_der_cons']}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(html_bars), unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 4 — ELECTORAL REALIGNMENT (HEATMAP + TOTALS)
# ============================================================================
def _render_realignment(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the electoral realignment matrix (heatmap) and the totals line.
    """
    df_change = _compute_transitions(df_2021, df_2025, t)
    total = len(df_change)

    if total == 0:
        st.info(t["sr_hist_no_data_transiciones"])
        return

    labels = _winner_labels(t)
    same_key = t["sr_hist_change_same"]
    changed_key = t["sr_hist_change_changed"]

    n_same = int((df_change["change_type"] == same_key).sum())
    n_changed = int((df_change["change_type"] == changed_key).sum())
    pct_same = n_same / total * 100 if total else 0
    pct_changed = n_changed / total * 100 if total else 0

    cards = [
        (t["sr_hist_card_total_comunas"], str(total), t["sr_hist_card_universo"], None),
        (t["sr_hist_card_mantuvo"], str(n_same), t["sr_hist_kpi_pct_total"].format(pct=f"{pct_same:.1f}"), None),
        (t["sr_hist_card_cambio"], str(n_changed), t["sr_hist_kpi_pct_total"].format(pct=f"{pct_changed:.1f}"), None),
    ]
    _render_nb_cards_row(cards)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    render_section_subtitle(t["sr_hist_sub_transicion_matrix"])

    rows_order = [labels["boric"], labels["kast"]]
    cols_order = [labels["jara"], labels["kast"]]

    matrix = pd.crosstab(df_change["winner_2021_label"], df_change["winner_2025_label"])
    matrix = matrix.reindex(index=rows_order, columns=cols_order, fill_value=0).astype(int)

    max_val = int(matrix.values.max()) if matrix.size else 1
    if max_val == 0:
        max_val = 1

    col_color_hex = {
        labels["jara"]: JARA_COLOR,
        labels["kast"]: KAST_COLOR,
    }

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=[[1, 1], [1, 1]],
        x=cols_order,
        y=rows_order,
        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
        showscale=False,
        hoverinfo="skip",
        xgap=4,
        ygap=4,
    ))

    for i, row_label in enumerate(rows_order):
        for j, col_label in enumerate(cols_order):
            val = int(matrix.loc[row_label, col_label])
            hexc = col_color_hex.get(col_label, NEUTRAL_COLOR).lstrip("#")
            r = int(hexc[0:2], 16)
            g = int(hexc[2:4], 16)
            b = int(hexc[4:6], 16)
            if val == 0:
                fillcolor = COLOR_NEUTRAL_INDICATOR
                text_color = NEUTRAL_COLOR
            else:
                alpha = 0.15 + 0.65 * (val / max_val)
                fillcolor = f"rgba({r},{g},{b},{alpha:.2f})"
                text_color = "white" if alpha >= 0.55 else "#111827"

            fig.add_shape(
                type="rect",
                x0=j - 0.5, x1=j + 0.5,
                y0=i - 0.5, y1=i + 0.5,
                fillcolor=fillcolor,
                line=dict(color="#ffffff", width=2),
                layer="below",
            )
            fig.add_annotation(
                x=col_label, y=row_label,
                text=str(val),
                showarrow=False,
                font=dict(
                    size=24,
                    color=text_color,
                    family="Liberation Sans, Arial, sans-serif",
                ),
            )

    total_boric = int(matrix.loc[labels["boric"]].sum())
    total_kast21 = int(matrix.loc[labels["kast"]].sum())
    total_jara = int(matrix[labels["jara"]].sum())
    total_kast25 = int(matrix[labels["kast"]].sum())

    fig.update_layout(
        height=320,
        margin=dict(l=140, r=40, t=60, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        title=_plotly_title(t["sr_hist_plot_matrix_title"]),
        xaxis=dict(
            side="top",
            showgrid=False,
            tickfont=dict(size=11, color="#333", family="Liberation Sans, Arial, sans-serif"),
        ),
        yaxis=dict(
            showgrid=False,
            autorange="reversed",
            tickfont=dict(size=11, color="#333", family="Liberation Sans, Arial, sans-serif"),
        ),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; "
        f"font-size: 10pt; color: #6b7280; margin-top: 4px; margin-bottom: 20px;\">"
        f"{t['sr_hist_card_total_comunas']}: <b>{total}</b> · "
        f"{labels['boric']} 2021: <b>{total_boric}</b> · "
        f"{labels['kast']} 2021: <b>{total_kast21}</b> · "
        f"{labels['jara']} 2025: <b>{total_jara}</b> · "
        f"{labels['kast']} 2025: <b>{total_kast25}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 5 — KAST: EVOLUTION BY COMMUNE 2021 → 2025
# ============================================================================
def _render_kast_evolution(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the top-up and top-down commune tables for Kast's evolution.
    """
    fr = df_2021[["commune_id", "commune_name", "region_name", "kast_pct", "kast_votes"]].rename(
        columns={"kast_pct": "kast_pct_2021", "kast_votes": "kast_votes_2021"}
    )
    sr = df_2025[["commune_id", "kast_pct", "kast_votes"]].rename(
        columns={"kast_pct": "kast_pct_2025", "kast_votes": "kast_votes_2025"}
    )
    merged = fr.merge(sr, on="commune_id", how="inner")
    merged["delta_pp"] = merged["kast_pct_2025"] - merged["kast_pct_2021"]
    merged["delta_votes"] = merged["kast_votes_2025"] - merged["kast_votes_2021"]

    render_section_title(t["sr_hist_section_kast_top_up"])

    top_up = merged.nlargest(10, "delta_pp").reset_index(drop=True)
    rows_up = ""
    for _, r in top_up.iterrows():
        comuna = str(r["commune_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows_up += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{comuna}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{r["kast_pct_2021"]:.2f}%</td>'
            f'<td style="text-align:right; color:{KAST_COLOR};">{r["kast_pct_2025"]:.2f}%</td>'
            f'<td style="text-align:right; color:{COLOR_POSITIVE};">+{r["delta_pp"]:.2f} pp</td>'
            f"</tr>"
        )

    html_up = _table_css("hi-tabla-kast-up") + f"""
    <div class="hi-tabla-kast-up">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_hist_th_comuna']}</th>
                    <th>{t['sr_hist_th_region']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct_kast_2021']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct_kast_2025']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_delta_pp']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_up}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_up), unsafe_allow_html=True)
    _table_gap()

    render_section_title(t["sr_hist_section_kast_top_down"])

    top_down = merged.nsmallest(10, "delta_pp").reset_index(drop=True)
    rows_down = ""
    for _, r in top_down.iterrows():
        comuna = str(r["commune_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        region = str(r["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows_down += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{comuna}</td>'
            f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{r["kast_pct_2021"]:.2f}%</td>'
            f'<td style="text-align:right; color:{KAST_COLOR};">{r["kast_pct_2025"]:.2f}%</td>'
            f'<td style="text-align:right; color:{COLOR_NEGATIVE};">{r["delta_pp"]:.2f} pp</td>'
            f"</tr>"
        )

    html_down = _table_css("hi-tabla-kast-down") + f"""
    <div class="hi-tabla-kast-down">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_hist_th_comuna']}</th>
                    <th>{t['sr_hist_th_region']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct_kast_2021']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct_kast_2025']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_delta_pp']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_down}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_down), unsafe_allow_html=True)
    _table_gap()

    _render_comment(t["sr_hist_note_kast"])


# ============================================================================
# SECTION NO. 6 — THE LEFT: BORIC 2021 → JARA 2025
# ============================================================================
def _render_left_block(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the left block analysis: 4 KPI cards and a by-region table.
    """
    valid_2021 = (
        int(df_2021["casted_votes"].sum())
        - int(df_2021["blank_votes"].sum())
        - int(df_2021["null_votes"].sum())
    )
    valid_2025 = (
        int(df_2025["casted_votes"].sum())
        - int(df_2025["blank_votes"].sum())
        - int(df_2025["null_votes"].sum())
    )

    boric_v = int(df_2021["boric_votes"].sum())
    jara_v = int(df_2025["jara_votes"].sum())
    boric_pct = boric_v / valid_2021 * 100 if valid_2021 else 0
    jara_pct = jara_v / valid_2025 * 100 if valid_2025 else 0

    delta_pp = jara_pct - boric_pct
    delta_v = jara_v - boric_v
    delta_sign = "+" if delta_pp >= 0 else ""

    cards = [
        (t["sr_hist_card_boric_2021"], f"{boric_pct:.2f}%", f"{_fmt_number(boric_v)} {t['votes']}", JARA_COLOR),
        (t["sr_hist_card_jara_2025"], f"{jara_pct:.2f}%", f"{_fmt_number(jara_v)} {t['votes']}", JARA_COLOR),
        (
            t["sr_hist_card_delta_pp"],
            f"{delta_sign}{delta_pp:.2f} pp",
            t["sr_hist_card_izq_sub"],
            COLOR_NEGATIVE,
        ),
        (
            t["sr_hist_card_delta_votos"],
            f"{'+' if delta_v >= 0 else ''}{_fmt_number(delta_v)}",
            t["sr_hist_card_votos"],
            COLOR_NEGATIVE,
        ),
    ]
    _render_nb_cards_row(cards)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    render_section_title(t["sr_hist_section_por_region"])

    reg_21 = df_2021.groupby("region_name", as_index=False).agg(
        valid_2021=("casted_votes", "sum"),
        null_2021=("null_votes", "sum"),
        blank_2021=("blank_votes", "sum"),
        boric_votes=("boric_votes", "sum"),
    )
    reg_21["valid_2021"] = reg_21["valid_2021"] - reg_21["null_2021"] - reg_21["blank_2021"]

    reg_25 = df_2025.groupby("region_name", as_index=False).agg(
        valid_2025=("casted_votes", "sum"),
        null_2025=("null_votes", "sum"),
        blank_2025=("blank_votes", "sum"),
        jara_votes=("jara_votes", "sum"),
    )
    reg_25["valid_2025"] = reg_25["valid_2025"] - reg_25["null_2025"] - reg_25["blank_2025"]

    region_metrics = reg_21.merge(
        reg_25[["region_name", "valid_2025", "jara_votes"]],
        on="region_name",
        how="inner",
    )
    region_metrics["boric_pct"] = region_metrics["boric_votes"] / region_metrics["valid_2021"].replace(0, 1) * 100
    region_metrics["jara_pct"] = region_metrics["jara_votes"] / region_metrics["valid_2025"].replace(0, 1) * 100
    region_metrics["delta_pp"] = region_metrics["jara_pct"] - region_metrics["boric_pct"]

    if "region_order" in df_2025.columns:
        order_map = (
            df_2025[["region_name", "region_order"]]
            .dropna().drop_duplicates()
            .set_index("region_name")["region_order"].to_dict()
        )
        region_metrics["_order"] = region_metrics["region_name"].map(order_map).fillna(9999)
        region_metrics = region_metrics.sort_values("_order").drop(columns="_order")
    else:
        region_metrics = region_metrics.sort_values("region_name")

    region_metrics = region_metrics.reset_index(drop=True)

    rows_html = ""
    for _, r in region_metrics.iterrows():
        region = str(r["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        delta = float(r["delta_pp"])
        delta_sign = "+" if delta >= 0 else ""
        delta_color = COLOR_POSITIVE if delta >= 0 else COLOR_NEGATIVE
        rows_html += (
            f"<tr>"
            f'<td style="font-weight:400; color:#333;">{region}</td>'
            f'<td style="text-align:right; color:#666;">{r["boric_pct"]:.2f}%</td>'
            f'<td style="text-align:right; color:{JARA_COLOR};">{r["jara_pct"]:.2f}%</td>'
            f'<td style="text-align:right; color:{delta_color};">{delta_sign}{delta:.2f} pp</td>'
            f"</tr>"
        )

    html = _table_css("hi-tabla-izquierda-region") + f"""
    <div class="hi-tabla-izquierda-region">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_hist_th_region']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct_boric_2021']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_pct_jara_2025']}</th>
                    <th style="text-align:right;">{t['sr_hist_th_delta_pp']}</th>
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
# SECTION NO. 7 — DECISIVE VS CLOSE
# ============================================================================
def _render_decisive_vs_close(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """
    Render the top-10 decisive and top-10 close communes where the winner
    changed between SR 2021 and SR 2025.
    """
    df_change = _compute_transitions(df_2021, df_2025, t)

    df_21 = _add_winner_sr2021(df_2021)[["commune_id", "winner_pct_2021"]]
    df_25 = _add_winner_sr2025(df_2025)[["commune_id", "winner_pct_2025"]]

    df_change = df_change.merge(df_21, on="commune_id", how="left")
    df_change = df_change.merge(df_25, on="commune_id", how="left")

    changed = df_change[df_change["change_type"] == t["sr_hist_change_changed"]].copy()

    if changed.empty:
        st.info(t["sr_hist_no_data_cambios"])
        return

    total_changes = len(changed)

    DECISIVE_THRESHOLD = 40.0
    CLOSE_THRESHOLD = 30.0

    decisive = int((changed["winner_pct_2025"] >= DECISIVE_THRESHOLD).sum())
    close = int((changed["winner_pct_2025"] < CLOSE_THRESHOLD).sum())

    pct_decisive = (decisive / total_changes * 100) if total_changes else 0
    pct_close = (close / total_changes * 100) if total_changes else 0

    cards = [
        (t["sr_hist_card_total_comunas"], str(total_changes), t["sr_hist_card_universo"], None),
        (
            t["sr_hist_card_contundentes"],
            str(decisive),
            f"{pct_decisive:.1f}% · {t['sr_hist_card_contundentes_sub']}",
            KAST_COLOR,
        ),
        (
            t["sr_hist_card_reñidas"],
            str(close),
            f"{pct_close:.1f}% · {t['sr_hist_card_reñidas_sub']}",
            JARA_COLOR,
        ),
    ]
    _render_nb_cards_row(cards)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    def _tabla_top(df_sub, title_key: str) -> None:
        render_section_title(title_key)
        rows_html = ""
        for _, r in df_sub.iterrows():
            comuna = str(r["commune_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            region = str(r["region_name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            color_21 = _candidate_color(r["winner_2021"])
            color_25 = _candidate_color(r["winner_2025"])
            rows_html += (
                f"<tr>"
                f'<td style="font-weight:400; color:#333;">{comuna}</td>'
                f'<td style="color:#6b7280; font-size:9.5pt;">{region}</td>'
                f'<td><span class="hi-color-box" style="background:{color_21};"></span>{r["winner_2021_label"]}</td>'
                f'<td><span class="hi-color-box" style="background:{color_25};"></span>{r["winner_2025_label"]}</td>'
                f'<td style="text-align:right; color:#666;">{r["winner_pct_2021"]:.2f}%</td>'
                f'<td style="text-align:right; color:{color_25};">{r["winner_pct_2025"]:.2f}%</td>'
                f"</tr>"
            )
        html = _table_css("hi-tabla-top-cambios") + f"""
        <div class="hi-tabla-top-cambios">
            <table>
                <thead>
                    <tr>
                        <th>{t['sr_hist_th_comuna']}</th>
                        <th>{t['sr_hist_th_region']}</th>
                        <th>{t['sr_hist_th_ganador_sr_2021']}</th>
                        <th>{t['sr_hist_th_ganador_sr_2025']}</th>
                        <th style="text-align:right;">{t['sr_hist_th_pct_gan_2021']}</th>
                        <th style="text-align:right;">{t['sr_hist_th_pct_gan_2025']}</th>
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

    top_decisive = changed.nlargest(10, "winner_pct_2025").reset_index(drop=True)
    _tabla_top(top_decisive, t["sr_hist_section_top_contundentes"])

    top_close = changed.nsmallest(10, "winner_pct_2025").reset_index(drop=True)
    _tabla_top(top_close, t["sr_hist_section_top_reñidas"])

    _render_comment(t["sr_hist_note_cambios"])


# ============================================================================
# SECTION BUILDERS
# ============================================================================
def _build_featured_cards_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the featured cards section."""
    _render_featured_cards(df_2021, df_2025, t)


def _build_participation_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the participation section."""
    _render_participation(df_2021, df_2025, t)


def _build_national_result_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the national result section."""
    _render_national_result(df_2021, df_2025, t)


def _build_blocks_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the political blocks section."""
    _render_blocks(df_2021, df_2025, t)


def _build_realignment_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the electoral realignment section."""
    _render_realignment(df_2021, df_2025, t)


def _build_kast_evolution_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the Kast evolution section."""
    _render_kast_evolution(df_2021, df_2025, t)


def _build_left_block_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the left block section."""
    _render_left_block(df_2021, df_2025, t)


def _build_decisive_vs_close_section(df_2021: pd.DataFrame, df_2025: pd.DataFrame, t: dict) -> None:
    """Build the decisive vs close section."""
    _render_decisive_vs_close(df_2021, df_2025, t)


# ============================================================================
# RENDER (orchestrator)
# ============================================================================
def render(t: dict) -> None:
    """
    Render the Second Round Historical page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    render_view_title(t["sr_hist_view_title"])
    render_view_subtitle(t["sr_hist_view_subtitle"])

    try:
        with st.spinner(t["loading"]):
            df_2021 = load_fact_second_round_2021()
            df_2025 = load_fact_second_round_2025()

        _build_featured_cards_section(df_2021, df_2025, t)

        with st.expander(t["sr_hist_exp_participacion"], expanded=False):
            _build_participation_section(df_2021, df_2025, t)

        with st.expander(t["sr_hist_exp_resultado_nacional"], expanded=False):
            _build_national_result_section(df_2021, df_2025, t)

        with st.expander(t["sr_hist_exp_bloques"], expanded=False):
            _build_blocks_section(df_2021, df_2025, t)

        with st.expander(t["sr_hist_exp_realineamiento"], expanded=False):
            _build_realignment_section(df_2021, df_2025, t)

        with st.expander(t["sr_hist_exp_kast_evolucion"], expanded=False):
            _build_kast_evolution_section(df_2021, df_2025, t)

        with st.expander(t["sr_hist_exp_izquierda"], expanded=False):
            _build_left_block_section(df_2021, df_2025, t)

        with st.expander(t["sr_hist_exp_contundentes"], expanded=False):
            _build_decisive_vs_close_section(df_2021, df_2025, t)

        _render_page_footer(t)

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
