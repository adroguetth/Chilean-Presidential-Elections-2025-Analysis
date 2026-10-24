"""
Summary Page — Executive Summary (Second Round + First Round)
============================================================================
Renders the executive summary page with two sections:

1. Second Round 2025
   - 4 KPI cards (.nb-card, deltas with COLOR_DELTA)
   - Winner block (label + name in party color + stacked bar + margin)

2. First Round 2025
   - 4 KPI cards (.nb-card)
   - 8-candidate table (inline, with status pills)

3. Footer

The candidate table is inline in this file; it does not use
components/tables.py. Colors come from config.constants. Transformation
helpers (clean_html, escape_html, format_number, format_signed) are imported
from utils.html_helpers. Titles use components.titles.

This file does NOT touch components/, utils/, config/, or other views.

Features
--------
- Second-round KPIs with deltas vs first round.
- Winner block with stacked bar, 50% midline, and margin.
- First-round KPIs.
- First-round candidate table with status pills and runoff note.
- Shared footer.

Dependencies
------------
- Internal: utils.data_loader, utils.calculations, utils.html_helpers,
  config.constants, components.titles.
- External: streamlit.
- Downstream: app.py (render_summary).

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st

from utils.data_loader import (
    load_fact_first_round_2025,
    load_fact_second_round_2025,
)
from utils.calculations import (
    compute_vote_metrics,
    compute_first_round_results,
    compute_second_round_results,
    compute_round_comparison,
)
from utils.html_helpers import (
    clean_html as _clean_html,
    escape_html as _escape_html,
    format_number as _fmt_number,
    format_signed as _signed_pp,
)
from config.constants import (
    PADRON_ELECTORAL_2025,
    COLOR_DELTA,
    COLOR_POSITIVE,
    COLOR_NEUTRAL_INDICATOR,
    _get_candidate_color,
    _hex_to_rgba_string,
)
from components.titles import (
    render_page_title,
    render_view_title,
    render_view_subtitle,
    render_section_title,
)


# ============================================================================
# KPI CARDS — CSS
# ============================================================================
_KPI_CSS = """
<style>
    .nb-cards {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 16px;
    }
    .nb-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 14px 16px 12px 16px;
        flex: 1;
        min-width: 160px;
        box-sizing: border-box;
    }
    .nb-card-label {
        font-family: "Liberation Sans", Arial, sans-serif;
        font-size: 10pt;
        color: #6b7280;
        font-weight: 500;
        letter-spacing: 0.2px;
    }
    .nb-card-value {
        font-family: "Liberation Sans", Arial, sans-serif;
        font-size: 15pt;
        font-weight: 700;
        color: #111827;
        margin-top: 6px;
        line-height: 1.2;
    }
    .nb-card-sub {
        font-family: "Liberation Sans", Arial, sans-serif;
        font-size: 9pt;
        font-weight: 400;
        color: #6b7280;
        margin-top: 8px;
    }
</style>
"""


# ============================================================================
# KPI CARDS — HELPERS
# ============================================================================
def _kpi_card_html(
    label: str,
    value: str,
    sub: str,
    delta: str = None,
    delta_color: str = None,
) -> str:
    """
    Render a single .nb-card with optional delta line.

    Parameters
    ----------
    label : str
        KPI label (already translated).
    value : str
        KPI value (already formatted).
    sub : str
        Subtitle line (already formatted, may contain a placeholder).
    delta : str, optional
        Delta line (e.g. "+1.23 pp").
    delta_color : str, optional
        CSS color for the delta line.

    Returns
    -------
    str
        HTML string for one card.
    """
    if delta:
        color_style = f' style="color:{delta_color};"' if delta_color else ""
        delta_line = f'<div class="nb-card-sub"{color_style}>{delta}</div>'
    else:
        delta_line = ""
    return f"""
    <div class="nb-card">
        <div class="nb-card-label">{label}</div>
        <div class="nb-card-value">{value}</div>
        <div class="nb-card-sub">{sub}</div>
        {delta_line}
    </div>
    """


def _kpi_row_html(cards: list) -> str:
    """
    Render the .nb-cards container with N cards.

    Parameters
    ----------
    cards : list of str
        List of card HTML strings (each one from _kpi_card_html).

    Returns
    -------
    str
        HTML string for the full row.
    """
    inner = "".join(cards)
    return _KPI_CSS + f'<div class="nb-cards">{inner}</div>'


# ============================================================================
# WINNER BLOCK — CSS
# ============================================================================
_WINNER_CSS = """
<style>
    .rs-winner-wrap {
        margin-top: 12px;
        margin-bottom: 28px;
        font-family: "Liberation Sans", Arial, sans-serif;
    }
    .rs-winner-label {
        font-size: 10pt;
        font-weight: 500;
        color: #6b7280;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .rs-winner-name {
        font-size: 16pt;
        font-weight: 700;
        margin-bottom: 14px;
    }
    .rs-bar-wrap {
        position: relative;
        margin-bottom: 14px;
    }
    .rs-bar {
        display: flex;
        height: 44px;
        width: 100%;
    }
    .rs-bar-seg {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 700;
        font-size: 13pt;
        line-height: 1;
    }
    .rs-bar-seg:first-child {
        border-top-left-radius: 6px;
        border-bottom-left-radius: 6px;
    }
    .rs-bar-seg:last-child {
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }
    .rs-bar-midline {
        position: absolute;
        top: -6px;
        bottom: -6px;
        left: 50%;
        width: 0;
        border-left: 1px dashed #9ca3af;
        pointer-events: none;
        z-index: 2;
    }
    .rs-bar-midlabel {
        position: absolute;
        top: -22px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 7.5pt;
        color: #6b7280;
        letter-spacing: 0.06em;
        font-weight: 500;
    }
    .rs-bar-details {
        display: flex;
        margin-bottom: 8px;
    }
    .rs-bar-detail {
        padding: 0 6px;
    }
    .rs-bar-detail .rs-name {
        font-size: 10pt;
        color: #333;
        margin-bottom: 4px;
    }
    .rs-bar-detail .rs-votes {
        font-size: 12pt;
        font-weight: 700;
        color: #111827;
    }
    .rs-margin {
        font-size: 10pt;
        color: #111827;
        font-weight: 600;
        border-top: 1px solid #e5e7eb;
        padding-top: 10px;
    }
    .rs-margin span { color: #6b7280; font-weight: 400; }
</style>
"""


# ============================================================================
# WINNER BLOCK — BUILDER
# ============================================================================
def _winner_block_html(
    winner_name: str,
    loser_name: str,
    winner_votes: int,
    loser_votes: int,
    winner_pct: float,
    loser_pct: float,
    margin_votes: int,
    margin_pp: float,
    t: dict,
) -> str:
    """
    Build the winner block for the second round.

    Replicates the style of the ideological block bars:
      - No top labels.
      - No container card.
      - Single stacked bar, 44px tall, rounded outer corners.
      - Dashed line at 50%.
      - Names below in 10pt black.
      - Votes below in 12pt bold black.
      - Winner's name colored with their party color.

    Parameters
    ----------
    winner_name : str
        Full name of the winner.
    loser_name : str
        Full name of the loser.
    winner_votes : int
        Winner's vote count.
    loser_votes : int
        Loser's vote count.
    winner_pct : float
        Winner's percentage over valid votes.
    loser_pct : float
        Loser's percentage over valid votes.
    margin_votes : int
        Absolute vote difference.
    margin_pp : float
        Absolute percentage-point difference.
    t : dict
        Translation dictionary.

    Returns
    -------
    str
        HTML string for the winner block.
    """
    jara_votes = loser_votes if loser_name == "Jeannette Jara" else winner_votes
    kast_votes = winner_votes if winner_name == "José Antonio Kast" else loser_votes
    jara_pct = loser_pct if loser_name == "Jeannette Jara" else winner_pct
    kast_pct = winner_pct if winner_name == "José Antonio Kast" else loser_pct

    jara_name = "Jeannette Jara"
    kast_name = "José Antonio Kast"
    jara_color = _get_candidate_color(jara_name)
    kast_color = _get_candidate_color(kast_name)
    winner_color = _get_candidate_color(winner_name)

    # The winner name color is resolved dynamically, so it goes inline.
    winner_name_style = f'style="color:{winner_color};"'

    return f"""
    {_WINNER_CSS}
    <div class="rs-winner-wrap">
        <div class="rs-winner-label">{t['summary_winner_label']}</div>
        <div class="rs-winner-name" {winner_name_style}>{winner_name}</div>

        <div class="rs-bar-wrap">
            <div class="rs-bar-midlabel">{t['summary_bar_midlabel']}</div>
            <div class="rs-bar-midline"></div>
            <div class="rs-bar">
                <div class="rs-bar-seg" style="width:{jara_pct}%; background:{jara_color};">{jara_pct:.2f}%</div>
                <div class="rs-bar-seg" style="width:{kast_pct}%; background:{kast_color};">{kast_pct:.2f}%</div>
            </div>
        </div>

        <div class="rs-bar-details">
            <div class="rs-bar-detail" style="width:{jara_pct}%; text-align: left;">
                <div class="rs-name">{jara_name}</div>
                <div class="rs-votes">{t['summary_votes_unit'].format(n=_fmt_number(jara_votes))}</div>
            </div>
            <div class="rs-bar-detail" style="width:{kast_pct}%; text-align: right;">
                <div class="rs-name">{kast_name}</div>
                <div class="rs-votes">{t['summary_votes_unit'].format(n=_fmt_number(kast_votes))}</div>
            </div>
        </div>

        <div class="rs-margin">
            {t['summary_margin_label']}: <span style="color:#111827; font-weight:700;">{t['summary_margin_votes'].format(n=_fmt_number(margin_votes))}</span>
            <span>({_signed_pp(margin_pp)} pp)</span>
        </div>
    </div>
    """


# ============================================================================
# CANDIDATE TABLE (FIRST ROUND) — CSS
# ============================================================================
_CANDIDATE_TABLE_CSS = """
<style>
    .sr-candidate-table {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-family: "Liberation Sans", Arial, sans-serif;
        margin-bottom: 8px;
    }
    .sr-candidate-table table {
        width: 100%;
        border-collapse: collapse;
        font-family: "Liberation Sans", Arial, sans-serif;
        margin: 0;
    }
    .sr-candidate-table th,
    .sr-candidate-table td {
        border-left: none !important;
        border-right: none !important;
        border-top: none;
    }
    .sr-candidate-table th {
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
    }
    .sr-candidate-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #f0f0f0;
        font-size: 10.5pt;
        color: #333;
        font-weight: 400;
        line-height: 1.3;
    }
    .sr-candidate-table tr:last-child td {
        border-bottom: none;
    }
    .sr-color-box {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 3px;
        margin-right: 8px;
        vertical-align: middle;
    }
    .sr-pill {
        font-size: 8pt;
        padding: 2px 10px;
        border-radius: 4px;
        font-weight: 500;
        white-space: nowrap;
        display: inline-block;
    }
</style>
"""


# ============================================================================
# CANDIDATE TABLE (FIRST ROUND) — RENDER
# ============================================================================
def _render_candidate_table_fr(fr_results, t: dict) -> None:
    """
    Render the first round candidate table.

    Format: color-box + name | party | votes | % | status pill.
    No dependency on components/tables.py.

    Parameters
    ----------
    fr_results : pd.DataFrame
        Output of compute_first_round_results().
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    if fr_results is None or fr_results.empty:
        st.warning(t.get("no_data", "No data available"))
        return

    pill_bg_advance = _hex_to_rgba_string(COLOR_POSITIVE, 0.12)

    rows_html = ""
    for _, row in fr_results.iterrows():
        passes = row["status"] == "passes_to_runoff"
        status_label = t["passes_to_runoff"] if passes else t["does_not_pass"]

        if passes:
            pill_style = f"background:{pill_bg_advance}; color:{COLOR_POSITIVE};"
        else:
            pill_style = f"background:{COLOR_NEUTRAL_INDICATOR}; color:#6b7280;"

        candidate = _escape_html(row["candidate_name"])
        party = _escape_html(row["party"])
        votes = _fmt_number(row["votes"])
        pct = f"{row['pct']:.2f}%"
        color = _get_candidate_color(row["candidate_name"])

        rows_html += f"""
        <tr>
            <td><span class="sr-color-box" style="background:{color};"></span>{candidate}</td>
            <td style="color:#666;">{party}</td>
            <td style="text-align:right;">{votes}</td>
            <td style="text-align:right;">{pct}</td>
            <td><span class="sr-pill" style="{pill_style}">{status_label}</span></td>
        </tr>
        """

    html = _CANDIDATE_TABLE_CSS + f"""
    <div class="sr-candidate-table">
        <table>
            <thead>
                <tr>
                    <th>{t['candidate']}</th>
                    <th>{t['party']}</th>
                    <th style="text-align:right;">{t['votes']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
                    <th>{t['status']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

    st.markdown(_clean_html(html), unsafe_allow_html=True)

    # Legal note below the table
    st.markdown(
        f"<div style='font-size:11px;color:#888780;padding:6px 4px 0 4px;line-height:1.5;"
        f"font-family:Liberation Sans,Arial,sans-serif;'>{t['runoff_note']}</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# FOOTER — CSS
# ============================================================================
_FOOTER_CSS = """
<style>
    .rs-footer {
        margin-top: 48px;
        padding-top: 16px;
        border-top: 1px solid #e5e7eb;
        width: 100%;
    }
    .rs-footer p {
        font-family: "Liberation Sans", Arial, sans-serif;
        font-size: 8pt;
        color: #9a9a9a;
        text-align: center;
        margin: 0;
        line-height: 1.4;
    }
</style>
"""


# ============================================================================
# FOOTER — BUILDER
# ============================================================================
def _footer_html(t: dict) -> str:
    """
    Build the shared footer.

    Parameters
    ----------
    t : dict
        Translation dictionary.

    Returns
    -------
    str
        HTML string for the footer.
    """
    return _FOOTER_CSS + f"""
    <div class="rs-footer">
        <p>{t['data_source']} · {t['data_source_note']}</p>
    </div>
    """


# ============================================================================
# SECTIONS
# ============================================================================
def _build_sr_section(df_fr_2025_raw, df_sr_2025_raw, t: dict) -> None:
    """
    Render the Second Round section (KPIs + winner block).

    Parameters
    ----------
    df_fr_2025_raw : pd.DataFrame
        First round fact table (for the round comparison deltas).
    df_sr_2025_raw : pd.DataFrame
        Second round fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    render_view_title(t["summary_sr_view_title"])
    render_view_subtitle(t["summary_sr_view_subtitle"])

    sr_metrics = compute_vote_metrics(df_sr_2025_raw, padron=PADRON_ELECTORAL_2025)
    comparison = compute_round_comparison(df_sr_2025_raw, df_fr_2025_raw)

    sr_cards = [
        _kpi_card_html(
            label=t["summary_kpi_casted"],
            value=_fmt_number(sr_metrics["casted_votes"]),
            sub=t["summary_kpi_pct_padron"].format(pct=f"{sr_metrics['casted_pct_padron']:.2f}"),
        ),
        _kpi_card_html(
            label=t["summary_kpi_valid"],
            value=_fmt_number(sr_metrics["valid_votes"]),
            sub=t["summary_kpi_pct_total"].format(pct=f"{sr_metrics['valid_pct']:.2f}"),
            delta=t["summary_kpi_diff_vs_fr"].format(pp=_signed_pp(comparison['valid_pct_diff'])),
            delta_color=COLOR_DELTA,
        ),
        _kpi_card_html(
            label=t["summary_kpi_null"],
            value=_fmt_number(sr_metrics["null_votes"]),
            sub=t["summary_kpi_pct_total"].format(pct=f"{sr_metrics['null_pct']:.2f}"),
            delta=t["summary_kpi_diff_vs_fr"].format(pp=_signed_pp(comparison['null_pct_diff'])),
            delta_color=COLOR_DELTA,
        ),
        _kpi_card_html(
            label=t["summary_kpi_blank"],
            value=_fmt_number(sr_metrics["blank_votes"]),
            sub=t["summary_kpi_pct_total"].format(pct=f"{sr_metrics['blank_pct']:.2f}"),
            delta=t["summary_kpi_diff_vs_fr"].format(pp=_signed_pp(comparison['blank_pct_diff'])),
            delta_color=COLOR_DELTA,
        ),
    ]
    st.markdown(_clean_html(_kpi_row_html(sr_cards)), unsafe_allow_html=True)

    sr_results = compute_second_round_results(df_sr_2025_raw)
    winner = sr_results["winner"]
    loser = "José Antonio Kast" if winner == "Jeannette Jara" else "Jeannette Jara"

    st.markdown(
        _clean_html(_winner_block_html(
            winner_name=winner,
            loser_name=loser,
            winner_votes=(sr_results["kast_votes"] if winner == "José Antonio Kast"
                          else sr_results["jara_votes"]),
            loser_votes=(sr_results["jara_votes"] if winner == "José Antonio Kast"
                         else sr_results["kast_votes"]),
            winner_pct=(sr_results["kast_pct"] if winner == "José Antonio Kast"
                        else sr_results["jara_pct"]),
            loser_pct=(sr_results["jara_pct"] if winner == "José Antonio Kast"
                       else sr_results["kast_pct"]),
            margin_votes=abs(sr_results["diff_votes"]),
            margin_pp=abs(sr_results["diff_pct"]),
            t=t,
        )),
        unsafe_allow_html=True,
    )


def _build_fr_section(df_fr_2025_raw, t: dict) -> None:
    """
    Render the First Round section (KPIs + candidate table).

    Parameters
    ----------
    df_fr_2025_raw : pd.DataFrame
        First round fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    render_view_title(t["summary_fr_view_title"])
    render_view_subtitle(t["summary_fr_view_subtitle"])

    fr_metrics = compute_vote_metrics(df_fr_2025_raw, padron=PADRON_ELECTORAL_2025)

    fr_cards = [
        _kpi_card_html(
            label=t["summary_kpi_casted"],
            value=_fmt_number(fr_metrics["casted_votes"]),
            sub=t["summary_kpi_pct_padron"].format(pct=f"{fr_metrics['casted_pct_padron']:.2f}"),
        ),
        _kpi_card_html(
            label=t["summary_kpi_valid"],
            value=_fmt_number(fr_metrics["valid_votes"]),
            sub=t["summary_kpi_pct_total"].format(pct=f"{fr_metrics['valid_pct']:.2f}"),
        ),
        _kpi_card_html(
            label=t["summary_kpi_null"],
            value=_fmt_number(fr_metrics["null_votes"]),
            sub=t["summary_kpi_pct_total"].format(pct=f"{fr_metrics['null_pct']:.2f}"),
        ),
        _kpi_card_html(
            label=t["summary_kpi_blank"],
            value=_fmt_number(fr_metrics["blank_votes"]),
            sub=t["summary_kpi_pct_total"].format(pct=f"{fr_metrics['blank_pct']:.2f}"),
        ),
    ]
    st.markdown(_clean_html(_kpi_row_html(fr_cards)), unsafe_allow_html=True)

    render_section_title(t["candidate_results_title"])
    fr_results = compute_first_round_results(df_fr_2025_raw)
    _render_candidate_table_fr(fr_results, t)


# ============================================================================
# RENDER (orchestrator)
# ============================================================================
def render(t: dict) -> None:
    """
    Render the Summary page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    render_page_title(t["summary_title"])

    try:
        df_fr_2025_raw = load_fact_first_round_2025()
        df_sr_2025_raw = load_fact_second_round_2025()

        _build_sr_section(df_fr_2025_raw, df_sr_2025_raw, t)
        _build_fr_section(df_fr_2025_raw, t)

        st.markdown(_clean_html(_footer_html(t)), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"{t.get('error', 'Error')}: {e}")
