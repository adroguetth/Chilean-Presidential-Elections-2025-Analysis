"""
First Round — Summary View
============================================================================
Summary view for the First Round 2025. Renders six KPI cards, the
candidate table, a donut + heatmap of communes won per candidate, the
top-5 strongholds for three focus candidates, and the macrozone table.

The layout is intentionally static (no filters, no tabs). It is the first
view a user sees when opening the First Round page.

Features
--------
- Six KPI cards (3 + 3 layout, nb-card format).
- Candidate table with color dot and status pill.
- Donut chart of communes won per candidate.
- Region × candidate heatmap.
- Top-5 strongholds per focus candidate (Jara, Kast, Parisi).
- Macrozone table with winner pill and distribution bar.
- Shared footer.

Dependencies
------------
- Internal: utils.data_loader, utils.calculations, utils.html_helpers,
  config.constants, components.charts, components.titles.
- External: streamlit, pandas.
- Downstream: pages/first_Round.py.

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st
import pandas as pd

from utils.data_loader import load_fact_first_round_2025
from utils.calculations import (
    compute_vote_metrics,
    compute_first_round_results,
)
from utils.html_helpers import (
    clean_html as _clean_html,
)
from config.constants import (
    PADRON_ELECTORAL_2025,
    CANDIDATES_2025,
    MACROZONE_ORDER,
    COLOR_DELTA,
    COLOR_NULOS,
    COLOR_POSITIVE,
    COLOR_NEUTRAL_INDICATOR,
    NEUTRAL_COLOR,
    _get_candidate_color,
    _hex_to_rgba_string,
)
from components.charts import (
    render_donut_chart,
    render_region_candidate_heatmap,
)
from components.titles import render_section_title


# ============================================================================
# CONSTANTS
# ============================================================================
# Minimum number of casted votes for a commune to be included in the
# strongholds ranking. Communes with fewer votes are too small to be
# meaningful in a percentage comparison.
MIN_CASTED_VOTES = 300


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
        font-family: "Liberation Sans", Arial, sans-serif;
    }
    .nb-card-value {
        font-size: 15pt;
        font-weight: 700;
        color: #111827;
        margin-top: 6px;
        line-height: 1.2;
        font-family: "Liberation Sans", Arial, sans-serif;
    }
    .nb-card-sub {
        font-size: 9pt;
        font-weight: 400;
        color: #6b7280;
        margin-top: 8px;
        font-family: "Liberation Sans", Arial, sans-serif;
    }
</style>
"""


# ============================================================================
# CANDIDATE TABLE — CSS
# ============================================================================
_CANDIDATE_TABLE_CSS = """
<style>
    .sr-candidate-table {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        max-width: 900px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-family: "Liberation Sans", Arial, sans-serif;
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
# BASTION TABLE — CSS
# ============================================================================
_BASTION_TABLE_CSS = """
<style>
    .sr-bastion-table {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-family: "Liberation Sans", Arial, sans-serif;
    }
    .sr-bastion-table table {
        width: 100%;
        border-collapse: collapse;
        font-family: "Liberation Sans", Arial, sans-serif;
        margin: 0;
    }
    .sr-bastion-table th,
    .sr-bastion-table td {
        border-left: none !important;
        border-right: none !important;
        border-top: none;
    }
    .sr-bastion-table th {
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
    .sr-bastion-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #f0f0f0;
        font-size: 10.5pt;
        color: #333;
        font-weight: 400;
        line-height: 1.3;
    }
    .sr-bastion-table tr:last-child td {
        border-bottom: none;
    }
</style>
"""


# ============================================================================
# MACROZONE TABLE — CSS
# ============================================================================
_MACROZONE_TABLE_CSS = """
<style>
    .sr-macro-table {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        font-family: "Liberation Sans", Arial, sans-serif;
    }
    .sr-macro-table table {
        width: 100%;
        border-collapse: collapse;
        font-family: "Liberation Sans", Arial, sans-serif;
        margin: 0;
    }
    .sr-macro-table th,
    .sr-macro-table td {
        border-left: none !important;
        border-right: none !important;
        border-top: none;
    }
    .sr-macro-table th {
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
    .sr-macro-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #f0f0f0;
        font-size: 10.5pt;
        color: #333;
        font-weight: 400;
        line-height: 1.3;
    }
    .sr-macro-table tr:last-child td {
        border-bottom: none;
    }
    .sr-macro-pill {
        font-size: 8pt;
        padding: 2px 10px;
        border-radius: 999px;
        font-weight: 600;
        display: inline-block;
        white-space: nowrap;
    }
    .sr-bar-container {
        display: flex;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        background: #f0f0f0;
    }
</style>
"""


# ============================================================================
# HELPERS
# ============================================================================
def _render_html(html: str) -> None:
    """Render clean HTML via st.markdown."""
    st.markdown(_clean_html(html), unsafe_allow_html=True)


# ============================================================================
# KPI CARDS
# ============================================================================
def _render_kpi_cards(fr_metrics: dict, fr_results, t: dict) -> None:
    """
    Render the six KPI cards in nb-card format (2 rows of 3).

    Parameters
    ----------
    fr_metrics : dict
        Output of compute_vote_metrics().
    fr_results : pd.DataFrame
        Output of compute_first_round_results().
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    padron = PADRON_ELECTORAL_2025
    casted = fr_metrics["casted_votes"]
    valid = fr_metrics["valid_votes"]
    null = fr_metrics["null_votes"]
    blank = fr_metrics["blank_votes"]

    pct_cast = (casted / padron * 100) if padron else 0
    pct_valid = (valid / casted * 100) if casted else 0
    pct_null = (null / casted * 100) if casted else 0
    pct_blank = (blank / casted * 100) if casted else 0

    n_candidates = len(fr_results) if fr_results is not None else 0
    n_over_10 = 0
    if fr_results is not None and not fr_results.empty and "pct" in fr_results.columns:
        n_over_10 = int((fr_results["pct"] > 10).sum())

    def _fmt(n: int) -> str:
        return f"{int(n):,}".replace(",", ".")

    # Each tuple: (label, value, sub, sub_style)
    cards = [
        (
            t["fr_summary_kpi_inscritos"],
            _fmt(padron),
            t["fr_summary_kpi_obligatorio"],
            "font-weight: 700; color: #6b7280;",
        ),
        (
            t["fr_summary_kpi_casted"],
            _fmt(casted),
            t["fr_summary_kpi_pct_padron"].format(pct=f"{pct_cast:.2f}"),
            "",
        ),
        (
            t["fr_summary_kpi_valid"],
            _fmt(valid),
            t["fr_summary_kpi_pct_total"].format(pct=f"{pct_valid:.2f}"),
            "",
        ),
        (
            t["fr_summary_kpi_null"],
            _fmt(null),
            t["fr_summary_kpi_pct_total"].format(pct=f"{pct_null:.2f}"),
            f"color: {COLOR_DELTA};",
        ),
        (
            t["fr_summary_kpi_blank"],
            _fmt(blank),
            t["fr_summary_kpi_pct_total"].format(pct=f"{pct_blank:.2f}"),
            f"color: {COLOR_DELTA};",
        ),
        (
            t["fr_summary_kpi_candidates"],
            str(n_candidates),
            t["fr_summary_kpi_over_10"].format(n=n_over_10),
            "font-weight: 700; color: #6b7280;",
        ),
    ]

    cards_html = ""
    for label, value, sub, sub_style in cards:
        style_attr = f' style="{sub_style}"' if sub_style else ""
        cards_html += f"""
        <div class="nb-card">
            <div class="nb-card-label">{label}</div>
            <div class="nb-card-value">{value}</div>
            <div class="nb-card-sub"{style_attr}>{sub}</div>
        </div>
        """

    html = _KPI_CSS + f'<div class="nb-cards">{cards_html}</div>'
    _render_html(html)


# ============================================================================
# CANDIDATE TABLE
# ============================================================================
def _render_candidate_table(fr_results, t: dict) -> None:
    """
    Render the candidate table with color dot and status pill.

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

        rows_html += f"""
        <tr>
            <td><span class="sr-color-box" style="background:{row['color']};"></span>{row['candidate_name']}</td>
            <td style="color:#666;">{row['party']}</td>
            <td>{row['votes']:,}</td>
            <td>{row['pct']:.2f}%</td>
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
                    <th>{t['votes']}</th>
                    <th>{t['pct']}</th>
                    <th>{t['status']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    _render_html(html)

    st.markdown(
        f"<div style='font-size:12px;color:#888780;padding:6px 14px 0 14px;line-height:1.5;"
        f"font-family:Liberation Sans,Arial,sans-serif;'>{t['runoff_note']}</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# BASTION TABLE
# ============================================================================
def _render_bastion_table(df, color: str, t: dict) -> None:
    """
    Render the top-5 commune table for one candidate.

    Parameters
    ----------
    df : pd.DataFrame
        Output of top_strongholds().
    color : str
        Candidate color (hex) for the percentage column.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    if df is None or df.empty:
        st.write(t["fr_summary_no_data_bastions"])
        return

    rows_html = ""
    for i, row in df.iterrows():
        pct_fmt = f"{row['porcentaje']:.2f}%"
        rows_html += f"""
        <tr>
            <td style="text-align:center; color:#9a9a9a; font-size:9.5pt;">{i}</td>
            <td style="font-weight:400; color:#333;">{row['commune_name']}</td>
            <td style="color:#6b7280; font-size:9.5pt;">{row['region_name']}</td>
            <td style="text-align:right; font-weight:700; color:{color};">{pct_fmt}</td>
        </tr>
        """

    html = _BASTION_TABLE_CSS + f"""
    <div class="sr-bastion-table">
        <table>
            <thead>
                <tr>
                    <th style="text-align:center;">{t['fr_summary_table_hash']}</th>
                    <th>{t['fr_summary_table_commune']}</th>
                    <th>{t['fr_summary_table_region']}</th>
                    <th style="text-align:right;">{t['pct']}</th>
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
def _render_macrozone_table(df_macro, color_by_short: dict, t: dict) -> None:
    """
    Render the macrozone table with winner pill and distribution bar.

    Parameters
    ----------
    df_macro : pd.DataFrame
        Aggregated macrozone data (see _build_macrozone_section).
    color_by_short : dict
        Mapping of candidate short name -> color.
    t : dict
        Translation dictionary.

    Returns
    -------
    None
    """
    if df_macro is None or df_macro.empty:
        st.warning(t["fr_summary_no_data_macrozone"])
        return

    rows_html = ""
    for _, row in df_macro.iterrows():
        three_sum = row["jara_votes"] + row["kast_votes"] + row["parisi_votes"]
        w_jara = (row["jara_votes"] / three_sum * 100) if three_sum else 0.0
        w_kast = (row["kast_votes"] / three_sum * 100) if three_sum else 0.0
        w_parisi = (row["parisi_votes"] / three_sum * 100) if three_sum else 0.0

        ganador = row["ganador"]
        ganador_color = color_by_short.get(ganador, NEUTRAL_COLOR)
        r = int(ganador_color[1:3], 16)
        g = int(ganador_color[3:5], 16)
        b = int(ganador_color[5:7], 16)
        pill_bg = f"rgba({r},{g},{b},0.12)"

        color_jara = color_by_short.get("Jara", _get_candidate_color("Jeannette Jara"))
        color_kast = color_by_short.get("Kast", _get_candidate_color("José Antonio Kast"))
        color_parisi = color_by_short.get("Parisi", _get_candidate_color("Franco Parisi"))

        rows_html += f"""
        <tr>
            <td style="font-weight:400; color:#333;">{row['macrozone']}</td>
            <td style="color:{color_jara};">{row['jara_pct']:.1f}%</td>
            <td style="color:{color_kast};">{row['kast_pct']:.1f}%</td>
            <td style="color:{color_parisi};">{row['parisi_pct']:.1f}%</td>
            <td style="color:{COLOR_NULOS};">{row['nulo_pct']:.2f}%</td>
            <td><span class="sr-macro-pill" style="background:{pill_bg}; color:{ganador_color};">{ganador}</span></td>
            <td>
                <div class="sr-bar-container">
                    <div style="width:{w_jara}%; background:{color_jara};"></div>
                    <div style="width:{w_kast}%; background:{color_kast};"></div>
                    <div style="width:{w_parisi}%; background:{color_parisi};"></div>
                </div>
            </td>
        </tr>
        """

    html = _MACROZONE_TABLE_CSS + f"""
    <div class="sr-macro-table">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_summary_table_macrozone']}</th>
                    <th>{t['fr_summary_table_jara_pct']}</th>
                    <th>{t['fr_summary_table_kast_pct']}</th>
                    <th>{t['fr_summary_table_parisi_pct']}</th>
                    <th>{t['fr_summary_table_null_pct']}</th>
                    <th>{t['fr_summary_table_winner']}</th>
                    <th>{t['fr_summary_table_distribution']}</th>
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
# STRONGHOLDS
# ============================================================================
def top_strongholds(
    df: pd.DataFrame,
    votes_col: str,
    pct_col: str,
    n: int = 5,
) -> pd.DataFrame:
    """
    Return the n communes where a candidate gets their highest % of valid
    votes, among communes that exceed the voting threshold.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered fact table (already above MIN_CASTED_VOTES).
    votes_col : str
        Vote column for the candidate.
    pct_col : str
        Percentage column for the candidate.
    n : int, optional
        Number of communes to return (default 5).

    Returns
    -------
    pd.DataFrame
        Columns: commune_name, region_name, macrozone, votos, porcentaje.
        Index is 1-based.
    """
    cols = ["commune_name", "region_name", "macrozone", votes_col, pct_col]
    out = (
        df[cols]
        .rename(columns={votes_col: "votos", pct_col: "porcentaje"})
        .sort_values("porcentaje", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    out.index = out.index + 1
    return out


# ============================================================================
# SECTION BUILDERS
# ============================================================================
def _build_kpis_section(df_fr_2025_raw, t: dict) -> None:
    """Build the KPI cards section."""
    fr_metrics = compute_vote_metrics(df_fr_2025_raw, padron=PADRON_ELECTORAL_2025)
    fr_results = compute_first_round_results(df_fr_2025_raw)
    _render_kpi_cards(fr_metrics, fr_results, t)


def _build_candidate_table_section(df_fr_2025_raw, t: dict) -> None:
    """Build the candidate table section."""
    render_section_title(t.get("candidate_results_title", "Resultados por candidato"))
    fr_results = compute_first_round_results(df_fr_2025_raw)
    _render_candidate_table(fr_results, t)


def _build_donut_heatmap_section(df_fr_2025_raw, t: dict) -> None:
    """Build the donut + heatmap section."""
    render_section_title(t["fr_summary_section_communes_won"])

    candidate_columns = {
        "Jara": "jara_pct",
        "Kast": "kast_pct",
        "Parisi": "parisi_pct",
        "Kaiser": "kaiser_pct",
        "Matthei": "matthei_pct",
        "Mayne-Nicholls": "mayne_nicholls_pct",
        "Enríquez-Ominami": "enriquez_ominami_pct",
        "Artés": "artes_pct",
    }

    df_communes = df_fr_2025_raw.copy()
    for col in candidate_columns.values():
        df_communes[col] = pd.to_numeric(df_communes[col], errors='coerce')

    pct_cols = list(candidate_columns.values())
    df_communes['winner'] = df_communes[pct_cols].idxmax(axis=1)
    col_to_name = {v: k for k, v in candidate_columns.items()}
    df_communes['winner_name'] = df_communes['winner'].map(col_to_name)

    communes_won = df_communes['winner_name'].value_counts().to_dict()
    communes_won = {k: v for k, v in communes_won.items() if v > 0}

    col_donut, col_heatmap = st.columns([0.8, 1.2], gap="large")

    with col_donut:
        st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)
        render_donut_chart(communes_won, t)
        st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

    with col_heatmap:
        render_region_candidate_heatmap(df_fr_2025_raw, t)


def _build_strongholds_section(df_fr_2025_raw, t: dict) -> None:
    """Build the top-5 strongholds section (Jara, Kast, Parisi)."""
    render_section_title(t["fr_summary_section_bastions"])

    df_base = df_fr_2025_raw[df_fr_2025_raw["casted_votes"] >= MIN_CASTED_VOTES].copy()

    focus_candidates = {
        "Jeannette Jara": {
            "votes_col": "jara_votes",
            "pct_col": "jara_pct",
            "color": _get_candidate_color("Jeannette Jara"),
        },
        "José Antonio Kast": {
            "votes_col": "kast_votes",
            "pct_col": "kast_pct",
            "color": _get_candidate_color("José Antonio Kast"),
        },
        "Franco Parisi": {
            "votes_col": "parisi_votes",
            "pct_col": "parisi_pct",
            "color": _get_candidate_color("Franco Parisi"),
        },
    }

    strongholds = {}
    for name, meta in focus_candidates.items():
        strongholds[name] = top_strongholds(
            df_base,
            meta["votes_col"],
            meta["pct_col"],
            n=5,
        )

    cols = st.columns(3)
    for idx, (name, table) in enumerate(strongholds.items()):
        with cols[idx]:
            color = focus_candidates[name]["color"]
            st.markdown(
                f"<div style='font-weight:600;color:{color};font-size:14px;margin-bottom:0.3rem;'>{name}</div>",
                unsafe_allow_html=True,
            )
            _render_bastion_table(table, color, t)


def _build_macrozone_section(df_fr_2025_raw, t: dict) -> None:
    """Build the macrozone table section."""
    render_section_title(t["fr_summary_section_macrozone"])

    color_by_short = {meta["short_name"]: meta["color"] for meta in CANDIDATES_2025.values()}
    vote_cols_all = {meta["short_name"]: meta["column"] for meta in CANDIDATES_2025.values()}
    cols_votos = list(vote_cols_all.values())
    col_to_short = {v: k for k, v in vote_cols_all.items()}

    sum_cols = cols_votos + ["casted_votes", "null_votes"]
    df_macro = df_fr_2025_raw.groupby("macrozone")[sum_cols].sum().reset_index()

    df_macro["total_valid"] = df_macro[cols_votos].sum(axis=1)
    df_macro["ganador_col"] = df_macro[cols_votos].idxmax(axis=1)
    df_macro["ganador"] = df_macro["ganador_col"].map(col_to_short)
    df_macro["jara_pct"] = df_macro["jara_votes"] / df_macro["total_valid"] * 100
    df_macro["kast_pct"] = df_macro["kast_votes"] / df_macro["total_valid"] * 100
    df_macro["parisi_pct"] = df_macro["parisi_votes"] / df_macro["total_valid"] * 100
    df_macro["nulo_pct"] = df_macro["null_votes"] / df_macro["casted_votes"] * 100
    df_macro["order"] = df_macro["macrozone"].map(MACROZONE_ORDER)
    df_macro = df_macro.sort_values("order")

    _render_macrozone_table(df_macro, color_by_short, t)


# ============================================================================
# FOOTER
# ============================================================================
_FOOTER_CSS = """
<style>
    .sr-footer {
        margin-top: 48px;
        padding-top: 16px;
        border-top: 1px solid #e5e7eb;
        width: 100%;
    }
    .sr-footer p {
        font-family: "Liberation Sans", Arial, sans-serif;
        font-size: 8pt;
        color: #9a9a9a;
        text-align: center;
        margin: 0;
        line-height: 1.4;
    }
</style>
"""


def _render_footer(t: dict) -> None:
    """Render the shared footer."""
    html = _FOOTER_CSS + f"""
    <div class="sr-footer">
        <p>{t['data_source']} · {t['data_source_note']}</p>
    </div>
    """
    _render_html(html)


# ============================================================================
# RENDER (orchestrator)
# ============================================================================
def render(t: dict) -> None:
    """
    Render the First Round Summary page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    try:
        df_fr_2025_raw = load_fact_first_round_2025()

        _build_kpis_section(df_fr_2025_raw, t)
        _build_candidate_table_section(df_fr_2025_raw, t)
        _build_donut_heatmap_section(df_fr_2025_raw, t)
        _build_strongholds_section(df_fr_2025_raw, t)
        _build_macrozone_section(df_fr_2025_raw, t)
        _render_footer(t)

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
