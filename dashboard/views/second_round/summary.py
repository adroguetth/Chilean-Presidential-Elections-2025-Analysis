"""
Second Round — Summary View
============================================================================
Summary view for the Second Round 2025. Renders six KPI cards, the winner
block (stacked bar + margin), a first-round vs second-round comparison
table, two top-10 commune tables by margin (Kast and Jara), and the
macrozone table with winner pill and distribution bar.

The layout is static (no filters, no tabs). It is the first view a user
sees when opening the Second Round page.

Features
--------
- Six KPI cards (3 + 3 layout, nb-card format) with deltas vs first round.
- Winner block: label + winner name in party color + stacked bar + margin.
- First round vs second round comparison table (Jara, Kast).
- Top-10 communes per winner by margin (Kast, Jara).
- Macrozone table with winner pill and distribution bar.
- Shared footer.

Dependencies
------------
- Internal: utils.data_loader, utils.calculations, utils.html_helpers,
  config.constants, components.titles.
- External: streamlit, pandas.
- Downstream: pages/second_Round.py.

Requirements
------------
- None.

Notes
-----
- `padron` refers to the Chilean electoral roll ("padrón electoral"),
  equivalent to `electoral_roll`. Kept in Spanish to preserve domain
  recognizability, consistent with `utils/calculations.py` and
  `views/first_round/summary.py`.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_fact_first_round_2025,
    load_fact_second_round_2025,
)
from utils.calculations import (
    compute_vote_metrics,
    compute_second_round_results,
)
from utils.html_helpers import (
    clean_html as _clean_html,
    escape_html as _escape_html,
    format_number as _fmt_number,
    format_signed as _signed_pp,
)
from config.constants import (
    PADRON_ELECTORAL_2025,
    MACROZONE_ORDER,
    COLOR_DELTA,
    COLOR_NULOS,
    _get_candidate_color,
    _hex_to_rgba_string,
)
from components.titles import render_section_title


# ============================================================================
# CONSTANTS
# ============================================================================
JARA_NAME = "Jeannette Jara"
KAST_NAME = "José Antonio Kast"
KAST_COLOR = _get_candidate_color(KAST_NAME)
JARA_COLOR = _get_candidate_color(JARA_NAME)


# ============================================================================
# KPI CARDS — CSS
# ============================================================================
_KPI_CSS = """
<style>
    .nb-cards {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 16px;
    }
    .nb-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 14px 16px 12px 16px;
        flex: 1 1 calc(33.333% - 8px);
        min-width: 160px;
        box-sizing: border-box;
        font-family: "Liberation Sans", Arial, sans-serif;
    }
    .nb-card-label {
        font-size: 10pt;
        color: #6b7280;
        font-weight: 500;
        letter-spacing: 0.2px;
    }
    .nb-card-value {
        font-size: 15pt;
        font-weight: 700;
        color: #111827;
        margin-top: 6px;
        line-height: 1.2;
    }
    .nb-card-sub {
        font-size: 9pt;
        font-weight: 400;
        color: #6b7280;
        margin-top: 8px;
    }
</style>
"""


# ============================================================================
# WINNER BLOCK — CSS
# ============================================================================
_WINNER_CSS = """
<style>
    .sr2-winner-wrap {
        margin-top: 12px;
        margin-bottom: 28px;
        font-family: "Liberation Sans", Arial, sans-serif;
    }
    .sr2-winner-label {
        font-size: 10pt;
        font-weight: 500;
        color: #6b7280;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .sr2-winner-name {
        font-size: 16pt;
        font-weight: 700;
        margin-bottom: 14px;
    }
    .sr2-bar-wrap {
        position: relative;
        margin-bottom: 14px;
    }
    .sr2-bar {
        display: flex;
        height: 44px;
        width: 100%;
    }
    .sr2-bar-seg {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 700;
        font-size: 13pt;
        line-height: 1;
    }
    .sr2-bar-seg:first-child {
        border-top-left-radius: 6px;
        border-bottom-left-radius: 6px;
    }
    .sr2-bar-seg:last-child {
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }
    .sr2-bar-midline {
        position: absolute;
        top: -6px;
        bottom: -6px;
        left: 50%;
        width: 0;
        border-left: 1px dashed #9ca3af;
        pointer-events: none;
        z-index: 2;
    }
    .sr2-bar-midlabel {
        position: absolute;
        top: -22px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 7.5pt;
        color: #6b7280;
        letter-spacing: 0.06em;
        font-weight: 500;
    }
    .sr2-bar-details {
        display: flex;
        margin-bottom: 8px;
    }
    .sr2-bar-detail {
        padding: 0 6px;
    }
    .sr2-bar-detail .sr2-name {
        font-size: 10pt;
        color: #333;
        margin-bottom: 4px;
    }
    .sr2-bar-detail .sr2-votes {
        font-size: 12pt;
        font-weight: 700;
        color: #111827;
    }
    .sr2-margin {
        font-size: 10pt;
        color: #111827;
        font-weight: 600;
        border-top: 1px solid #e5e7eb;
        padding-top: 10px;
    }
    .sr2-margin span { color: #6b7280; font-weight: 400; }
</style>
"""


# ============================================================================
# GENERIC TABLE — CSS
# ============================================================================
# Shared by the comparison table, the top-10 tables, and the macrozone
# table. Each caller passes its own container class name to avoid collisions.
def _table_css(container_class: str) -> str:
    return f"""
    <style>
        .{container_class} {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-family: "Liberation Sans", Arial, sans-serif;
            margin-bottom: 8px;
        }}
        .{container_class} table {{
            width: 100%;
            border-collapse: collapse;
            font-family: "Liberation Sans", Arial, sans-serif;
            margin: 0;
        }}
        .{container_class} th,
        .{container_class} td {{
            border-left: none !important;
            border-right: none !important;
            border-top: none;
        }}
        .{container_class} th {{
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
        .{container_class} td {{
            padding: 8px 12px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 10.5pt;
            color: #333;
            font-weight: 400;
            line-height: 1.3;
        }}
        .{container_class} tr:last-child td {{
            border-bottom: none;
        }}
        .{container_class} .sr2-color-box {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
            vertical-align: middle;
        }}
    </style>
    """


# ============================================================================
# MACROZONE TABLE — ADDITIONAL CSS
# ============================================================================
# Extra styles specific to the macrozone table, appended after _table_css().
_MACROZONE_EXTRA_CSS = """
<style>
    .sr2-macro-pill {
        font-size: 8pt;
        padding: 2px 10px;
        border-radius: 999px;
        font-weight: 600;
        display: inline-block;
        white-space: nowrap;
    }
    .sr2-bar-container {
        display: flex;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        background: #f0f0f0;
    }
</style>
"""


# ============================================================================
# FOOTER — CSS
# ============================================================================
_FOOTER_CSS = """
<style>
    .sr2-footer {
        margin-top: 48px;
        padding-top: 16px;
        border-top: 1px solid #e5e7eb;
        width: 100%;
    }
    .sr2-footer p {
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
# HELPERS
# ============================================================================
def _render_html(html: str) -> None:
    """Render clean HTML via st.markdown."""
    st.markdown(_clean_html(html), unsafe_allow_html=True)


def _top_communes_by_margin(df: pd.DataFrame, winner: str, n: int = 10) -> pd.DataFrame:
    """
    Return the top N communes where the given candidate won by the largest
    margin (in percentage points).

    Uses the columns already present in the second round fact table
    (`commune_name`, `region_name`, `jara_votes`, `kast_votes`).

    Parameters
    ----------
    df : pd.DataFrame
        Second round fact table.
    winner : str
        Full candidate name (`JARA_NAME` or `KAST_NAME`).
    n : int, optional
        Number of communes to return (default 10).

    Returns
    -------
    pd.DataFrame
        Filtered and sorted by margin (descending), with internal columns
        prefixed by `__` (winner, winner_pct, margin_pp).
    """
    out = df.copy()
    out["__winner"] = out.apply(
        lambda r: KAST_NAME if r["kast_votes"] > r["jara_votes"] else JARA_NAME,
        axis=1,
    )

    out["__valid"] = out["jara_votes"] + out["kast_votes"]
    out["__jara_pct"] = out["jara_votes"] / out["__valid"].replace(0, 1) * 100
    out["__kast_pct"] = out["kast_votes"] / out["__valid"].replace(0, 1) * 100
    out["__margin_pp"] = (out["__kast_pct"] - out["__jara_pct"]).abs()
    out["__winner_pct"] = out.apply(
        lambda r: r["__kast_pct"] if r["__winner"] == KAST_NAME else r["__jara_pct"],
        axis=1,
    )

    subset = out[out["__winner"] == winner].copy()

    if "commune_name" not in subset.columns:
        subset["commune_name"] = "—"
    if "region_name" not in subset.columns:
        subset["region_name"] = "—"

    subset = subset.sort_values(
        ["__margin_pp", "__winner_pct"], ascending=False
    ).head(n)
    return subset.reset_index(drop=True)


# ============================================================================
# KPI CARDS
# ============================================================================
def _render_kpi_cards(sr_metrics: dict, fr_metrics: dict, sr_results: dict, t: dict) -> None:
    """
    Render the six KPI cards in nb-card format (2 rows of 3), with deltas
    vs first round where applicable.

    Parameters
    ----------
    sr_metrics : dict
        Output of compute_vote_metrics() for the second round fact table.
    fr_metrics : dict
        Output of compute_vote_metrics() for the first round fact table.
    sr_results : dict
        Output of compute_second_round_results().
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    padron = PADRON_ELECTORAL_2025
    casted = sr_metrics["casted_votes"]
    valid = sr_metrics["valid_votes"]
    null = sr_metrics["null_votes"]
    blank = sr_metrics["blank_votes"]

    pct_cast = (casted / padron * 100) if padron else 0
    pct_valid = (valid / casted * 100) if casted else 0
    pct_null = (null / casted * 100) if casted else 0
    pct_blank = (blank / casted * 100) if casted else 0

    cast_delta = sr_metrics["casted_pct_padron"] - fr_metrics["casted_pct_padron"]
    valid_delta = sr_metrics["valid_pct"] - fr_metrics["valid_pct"]
    null_delta = sr_metrics["null_pct"] - fr_metrics["null_pct"]
    blank_delta = sr_metrics["blank_pct"] - fr_metrics["blank_pct"]

    margin_votes = abs(sr_results["diff_votes"])
    margin_pp = abs(sr_results["diff_pct"])

    def _fmt(n: int) -> str:
        return f"{int(n):,}".replace(",", ".")

    # Each tuple: (label, value, sub, sub_style, delta, delta_style)
    cards = [
        (
            t["sr_summary_kpi_inscritos"],
            _fmt(padron),
            t["sr_summary_kpi_voto_obligatorio"],
            "font-weight: 600;",
            None,
            None,
        ),
        (
            t["sr_summary_kpi_cast"],
            _fmt(casted),
            t["sr_summary_kpi_pct_padron"].format(pct=f"{pct_cast:.2f}"),
            "",
            t["sr_summary_kpi_delta_vs_fr"].format(pp=_signed_pp(cast_delta)),
            f"color: {COLOR_DELTA};",
        ),
        (
            t["sr_summary_kpi_valid"],
            _fmt(valid),
            t["sr_summary_kpi_pct_total"].format(pct=f"{pct_valid:.2f}"),
            "",
            t["sr_summary_kpi_delta_vs_fr"].format(pp=_signed_pp(valid_delta)),
            f"color: {COLOR_DELTA};",
        ),
        (
            t["sr_summary_kpi_null"],
            _fmt(null),
            t["sr_summary_kpi_pct_total"].format(pct=f"{pct_null:.2f}"),
            "",
            t["sr_summary_kpi_delta_vs_fr"].format(pp=_signed_pp(null_delta)),
            f"color: {COLOR_DELTA};",
        ),
        (
            t["sr_summary_kpi_blank"],
            _fmt(blank),
            t["sr_summary_kpi_pct_total"].format(pct=f"{pct_blank:.2f}"),
            "",
            t["sr_summary_kpi_delta_vs_fr"].format(pp=_signed_pp(blank_delta)),
            f"color: {COLOR_DELTA};",
        ),
        (
            t["sr_summary_kpi_margin"],
            t["sr_summary_kpi_margin_value"].format(n=_fmt(margin_votes)),
            t["sr_summary_kpi_margin_sub"],
            "",
            t["sr_summary_kpi_margin_delta"].format(pp=_signed_pp(margin_pp)),
            f"font-weight: 600; color: {KAST_COLOR};",
        ),
    ]

    cards_html = ""
    for label, value, sub, sub_style, delta, delta_style in cards:
        sub_attr = f' style="{sub_style}"' if sub_style else ""
        delta_line = ""
        if delta:
            delta_line = f'<div class="nb-card-sub" style="{delta_style}">{delta}</div>'
        cards_html += f"""
        <div class="nb-card">
            <div class="nb-card-label">{label}</div>
            <div class="nb-card-value">{value}</div>
            <div class="nb-card-sub"{sub_attr}>{sub}</div>
            {delta_line}
        </div>
        """

    html = _KPI_CSS + f'<div class="nb-cards">{cards_html}</div>'
    _render_html(html)


# ============================================================================
# WINNER BLOCK
# ============================================================================
def _render_winner_block(sr_results: dict, t: dict) -> None:
    """
    Render the winner block: label, winner name in party color, stacked
    bar (Jara / Kast), and margin line.

    Parameters
    ----------
    sr_results : dict
        Output of compute_second_round_results().
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    winner = sr_results["winner"]

    jara_votes = sr_results["jara_votes"]
    kast_votes = sr_results["kast_votes"]
    jara_pct = sr_results["jara_pct"]
    kast_pct = sr_results["kast_pct"]
    margin_votes = abs(sr_results["diff_votes"])
    margin_pp = abs(sr_results["diff_pct"])

    jara_color = _get_candidate_color(JARA_NAME)
    kast_color = _get_candidate_color(KAST_NAME)
    winner_color = _get_candidate_color(winner)

    # Winner name color is dynamic, so it goes inline.
    winner_name_style = f'style="color:{winner_color};"'

    html = _WINNER_CSS + f"""
    <div class="sr2-winner-wrap">
        <div class="sr2-winner-label">{t['sr_summary_winner_label']}</div>
        <div class="sr2-winner-name" {winner_name_style}>{winner}</div>
        <div class="sr2-bar-wrap">
            <div class="sr2-bar-midlabel">{t['sr_summary_bar_midlabel']}</div>
            <div class="sr2-bar-midline"></div>
            <div class="sr2-bar">
                <div class="sr2-bar-seg" style="width:{jara_pct}%; background:{jara_color};">{jara_pct:.2f}%</div>
                <div class="sr2-bar-seg" style="width:{kast_pct}%; background:{kast_color};">{kast_pct:.2f}%</div>
            </div>
        </div>
        <div class="sr2-bar-details">
            <div class="sr2-bar-detail" style="width:{jara_pct}%; text-align: left;">
                <div class="sr2-name">{JARA_NAME}</div>
                <div class="sr2-votes">{t['sr_summary_votes_unit'].format(n=_fmt_number(jara_votes))}</div>
            </div>
            <div class="sr2-bar-detail" style="width:{kast_pct}%; text-align: right;">
                <div class="sr2-name">{KAST_NAME}</div>
                <div class="sr2-votes">{t['sr_summary_votes_unit'].format(n=_fmt_number(kast_votes))}</div>
            </div>
        </div>
        <div class="sr2-margin">
            {t['sr_summary_margin_label']}: <span style="color:#111827; font-weight:700;">{t['sr_summary_margin_votes'].format(n=_fmt_number(margin_votes))}</span>
            <span>({_signed_pp(margin_pp)} pp)</span>
        </div>
    </div>
    """
    _render_html(html)


# ============================================================================
# COMPARISON TABLE (FR vs SR)
# ============================================================================
def _render_comparison_table(fr_df: pd.DataFrame, sr_df: pd.DataFrame, t: dict) -> None:
    """
    Render the FR vs SR comparison table: Jara and Kast, % FR, % SR, Δ pp.

    Parameters
    ----------
    fr_df : pd.DataFrame
        First round fact table.
    sr_df : pd.DataFrame
        Second round fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    fr_total_valid = (
        int(fr_df["casted_votes"].sum())
        - int(fr_df["null_votes"].sum())
        - int(fr_df["blank_votes"].sum())
    )
    sr_total_valid = (
        int(sr_df["casted_votes"].sum())
        - int(sr_df["null_votes"].sum())
        - int(sr_df["blank_votes"].sum())
    )

    rows_html = ""
    for name, col in [(JARA_NAME, "jara"), (KAST_NAME, "kast")]:
        fr_votes = int(fr_df[f"{col}_votes"].sum())
        sr_votes = int(sr_df[f"{col}_votes"].sum())
        fr_pct = fr_votes / fr_total_valid * 100 if fr_total_valid else 0
        sr_pct = sr_votes / sr_total_valid * 100 if sr_total_valid else 0
        delta_pp = sr_pct - fr_pct
        color = _get_candidate_color(name)
        delta_sign = "+" if delta_pp >= 0 else ""

        rows_html += f"""
        <tr>
            <td><span class="sr2-color-box" style="background:{color};"></span>{_escape_html(name)}</td>
            <td style="text-align:right; color:#666;">{fr_pct:.2f}%</td>
            <td style="text-align:right; font-weight:700;">{sr_pct:.2f}%</td>
            <td style="text-align:right; color:{color};">{delta_sign}{delta_pp:.2f} pp</td>
        </tr>
        """

    css = _table_css("sr2-comparison-table")
    html = css + f"""
    <div class="sr2-comparison-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_summary_th_candidato']}</th>
                    <th style="text-align:right;">{t['sr_summary_th_1v']}</th>
                    <th style="text-align:right;">{t['sr_summary_th_2v']}</th>
                    <th style="text-align:right;">{t['sr_summary_th_delta_pp']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    _render_html(html)


# ============================================================================
# TOP 10 COMMUNES BY MARGIN
# ============================================================================
def _render_top_communes(sr_df: pd.DataFrame, t: dict) -> None:
    """
    Render two columns: top 10 communes won by Kast and top 10 won by Jara,
    each sorted by margin in percentage points.

    Parameters
    ----------
    sr_df : pd.DataFrame
        Second round fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    col_left, col_right = st.columns(2, gap="medium")

    for col, winner in [(col_left, KAST_NAME), (col_right, JARA_NAME)]:
        with col:
            color = _get_candidate_color(winner)
            st.markdown(
                f"<div style='font-family:Liberation Sans,Arial,sans-serif;"
                f"font-size:11pt;font-weight:700;color:{color};"
                f"margin-top:8px;margin-bottom:8px;'>"
                f"{t['sr_summary_top10_label'].format(winner=winner)}</div>",
                unsafe_allow_html=True,
            )

            top = _top_communes_by_margin(sr_df, winner, n=10)
            if top.empty:
                st.info(t["sr_summary_no_data"])
                continue

            margin_color = _get_candidate_color(winner)

            rows_html = ""
            for i, row in top.iterrows():
                rank = i + 1
                commune = _escape_html(row.get("commune_name", "—"))
                region = _escape_html(row.get("region_name", "—"))
                pct = f"{row['__winner_pct']:.2f}%"
                margin = f"+{row['__margin_pp']:.2f} pp"

                rows_html += f"""
                <tr>
                    <td style="text-align:center; color:#9a9a9a; font-size:9.5pt;">{rank}</td>
                    <td style="font-weight:400; color:#333;">{commune}</td>
                    <td style="color:#6b7280; font-size:9.5pt;">{region}</td>
                    <td style="text-align:right; font-weight:700;">{pct}</td>
                    <td style="text-align:right; color:{margin_color};">{margin}</td>
                </tr>
                """

            container_class = "sr2-top-kast" if winner == KAST_NAME else "sr2-top-jara"
            css = _table_css(container_class)

            html = css + f"""
            <div class="{container_class}">
                <table>
                    <thead>
                        <tr>
                            <th style="text-align:center;">{t['sr_summary_th_hash']}</th>
                            <th>{t['sr_summary_th_comuna']}</th>
                            <th>{t['sr_summary_th_region']}</th>
                            <th style="text-align:right;">{t['sr_summary_th_pct_gan']}</th>
                            <th style="text-align:right;">{t['sr_summary_th_margen']}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """
            _render_html(html)


# ============================================================================
# MACROZONE TABLE
# ============================================================================
def _render_macrozone_table(df_sr: pd.DataFrame, t: dict) -> None:
    """
    Render the macrozone table for the second round.

    Columns: Macrozone | Jara % | Kast % | Null % | Winner | Distribution.
    All data comes from the second round fact table. The winner is the
    candidate with more votes in the macrozone.

    Parameters
    ----------
    df_sr : pd.DataFrame
        Second round fact table.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    df = df_sr[["macrozone", "jara_votes", "kast_votes",
                "null_votes", "casted_votes"]].copy()
    df = df.dropna(subset=["macrozone"]).copy()

    agg = df.groupby("macrozone", as_index=False).agg(
        jara_votes=("jara_votes", "sum"),
        kast_votes=("kast_votes", "sum"),
        null_votes=("null_votes", "sum"),
        casted_votes=("casted_votes", "sum"),
    )

    agg["__valid"] = agg["jara_votes"] + agg["kast_votes"]
    agg["jara_pct"] = (agg["jara_votes"] / agg["__valid"].replace(0, 1) * 100).round(2)
    agg["kast_pct"] = (agg["kast_votes"] / agg["__valid"].replace(0, 1) * 100).round(2)
    agg["null_pct"] = (agg["null_votes"] / agg["casted_votes"].replace(0, 1) * 100).round(2)
    agg["winner"] = agg.apply(
        lambda r: "Kast" if r["kast_votes"] > r["jara_votes"] else "Jara", axis=1
    )

    # North-to-south order.
    agg["_order"] = agg["macrozone"].map(
        {m: i for i, m in enumerate(MACROZONE_ORDER)}
    ).fillna(9999)
    agg = agg.sort_values("_order").drop(columns="_order").reset_index(drop=True)

    if agg.empty:
        st.info(t["sr_summary_no_data_macrozone"])
        return

    JARA_C = JARA_COLOR
    KAST_C = KAST_COLOR
    NULO_C = COLOR_NULOS

    rows_html = ""
    for _, r in agg.iterrows():
        macrozone = _escape_html(r["macrozone"])
        jara_pct = float(r["jara_pct"])
        kast_pct = float(r["kast_pct"])
        null_pct = float(r["null_pct"])
        winner = str(r["winner"])

        winner_color = KAST_C if winner == "Kast" else JARA_C
        pill_bg = _hex_to_rgba_string(winner_color, 0.12)

        w_jara = jara_pct
        w_kast = kast_pct

        rows_html += f"""
        <tr>
            <td style="font-weight:400; color:#333;">{macrozone}</td>
            <td style="color:{JARA_C};">{jara_pct:.2f}%</td>
            <td style="color:{KAST_C};">{kast_pct:.2f}%</td>
            <td style="color:{NULO_C};">{null_pct:.2f}%</td>
            <td><span class="sr2-macro-pill" style="background:{pill_bg}; color:{winner_color};">{winner}</span></td>
            <td>
                <div class="sr2-bar-container">
                    <div style="width:{w_jara}%; background:{JARA_C};"></div>
                    <div style="width:{w_kast}%; background:{KAST_C};"></div>
                </div>
            </td>
        </tr>
        """

    css = _table_css("sr2-macrozone-table") + _MACROZONE_EXTRA_CSS

    html = css + f"""
    <div class="sr2-macrozone-table">
        <table>
            <thead>
                <tr>
                    <th>{t['sr_summary_th_macrozone']}</th>
                    <th style="text-align:left;">{t['sr_summary_th_jara_pct']}</th>
                    <th style="text-align:left;">{t['sr_summary_th_kast_pct']}</th>
                    <th style="text-align:left;">{t['sr_summary_th_null_pct']}</th>
                    <th style="text-align:left;">{t['sr_summary_th_ganador']}</th>
                    <th style="text-align:left;">{t['sr_summary_th_distribucion']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    _render_html(html)


# ============================================================================
# FOOTER
# ============================================================================
def _render_footer(t: dict) -> None:
    """Render the shared footer."""
    html = _FOOTER_CSS + f"""
    <div class="sr2-footer">
        <p>{t['data_source']} · {t['data_source_note']}</p>
    </div>
    """
    _render_html(html)


# ============================================================================
# SECTION BUILDERS
# ============================================================================
def _build_kpis_section(df_fr, df_sr, t: dict) -> None:
    """Build the KPI cards section (6 cards, 3+3 layout)."""
    sr_metrics = compute_vote_metrics(df_sr, padron=PADRON_ELECTORAL_2025)
    fr_metrics = compute_vote_metrics(df_fr, padron=PADRON_ELECTORAL_2025)
    sr_results = compute_second_round_results(df_sr)
    _render_kpi_cards(sr_metrics, fr_metrics, sr_results, t)


def _build_winner_section(df_sr, t: dict) -> None:
    """Build the winner block section."""
    sr_results = compute_second_round_results(df_sr)
    _render_winner_block(sr_results, t)


def _build_comparison_section(df_fr, df_sr, t: dict) -> None:
    """Build the FR vs SR comparison table section."""
    render_section_title(t["sr_summary_section_comparativa"])
    _render_comparison_table(df_fr, df_sr, t)


def _build_top_communes_section(df_sr, t: dict) -> None:
    """Build the top-10 communes by margin section."""
    render_section_title(t["sr_summary_section_top_comunas"])
    _render_top_communes(df_sr, t)


def _build_macrozone_section(df_sr, t: dict) -> None:
    """Build the macrozone table section."""
    render_section_title(t["sr_summary_section_macrozone"])
    _render_macrozone_table(df_sr, t)


# ============================================================================
# RENDER (orchestrator)
# ============================================================================
def render(t: dict) -> None:
    """
    Render the Second Round Summary page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    try:
        df_fr = load_fact_first_round_2025()
        df_sr = load_fact_second_round_2025()

        _build_kpis_section(df_fr, df_sr, t)
        _build_winner_section(df_sr, t)
        _build_comparison_section(df_fr, df_sr, t)
        _build_top_communes_section(df_sr, t)
        _build_macrozone_section(df_sr, t)
        _render_footer(t)

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
