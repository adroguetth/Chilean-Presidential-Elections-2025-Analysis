"""
First Round — Historical (2021 vs 2025)
============================================================================
Comparison of the first presidential round between 2021 and 2025.

Featured cards at the top (4 cards):
    1. Growth in casted votes (voluntary → compulsory voting)
    2. Effective number of candidates 2025 (fragmentation)
    3. Communes that changed winner (territorial realignment)
    4. Parisi: absolute growth (protagonist of the change)

Sections (all collapsible):
    1. National participation 2021 vs 2025
    2. Political block evolution 2021 vs 2025
    3. Electoral realignment: winner transitions 2021 → 2025
    4. Winner changes grouped by transition
    5. Communes that changed winner: decisive vs close
    6. Political system fragmentation 2021 vs 2025
    7. Franco Parisi: evolution and territory 2021 → 2025
    8. Franco Parisi: communes and absorption 2021 → 2025

Transformation helpers (clean_html, format_number, hex_to_rgba) are imported
from utils.html_helpers.
View and section titles live in components.titles.
Colors live in config.constants.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import pandas as pd
import streamlit as st

from utils.data_loader import (
    load_fact_first_round_2021,
    load_fact_first_round_2025,
)
from utils.html_helpers import (
    clean_html as _clean_html,
    format_number as _fmt_number,
    hex_to_rgba as _hex_to_rgba,
)
from config.constants import (
    CANDIDATE_COLORS,
    CANDIDATE_COLORS_2021,
    COLOR_NEGATIVE,
    COLOR_NEUTRAL_INDICATOR,
    COLOR_POSITIVE,
    NEUTRAL_COLOR,
    POLITICAL_BLOCKS,
    _get_candidate_color,
)
from components.titles import (
    render_view_title,
    render_view_subtitle,
    render_section_title,
)


# ============================================================================
# LOCAL HELPERS (only visual formatting)
# ============================================================================
def _format_pct(v: float) -> str:
    return f"{v:.2f}%"


def _table_gap():
    """6px gap between the bottom of a table and the next element.
    Rendered in a separate st.markdown call so Streamlit doesn't collapse it."""
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)


def _color_2021(name_ref: str) -> str:
    """2021 candidate color from CANDIDATE_COLORS_2021 with fallback."""
    if name_ref in CANDIDATE_COLORS_2021:
        return CANDIDATE_COLORS_2021[name_ref]
    return _get_candidate_color(name_ref)


def _color_2025(name_ref: str) -> str:
    """2025 candidate color from CANDIDATE_COLORS with fallback."""
    if name_ref in CANDIDATE_COLORS:
        return CANDIDATE_COLORS[name_ref]
    return _get_candidate_color(name_ref)


def _render_page_footer(t: dict) -> None:
    st.markdown(_clean_html(f"""
    <style>
        .page-footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; width: 100%; }}
        .page-footer p {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 8pt; color: #9a9a9a; text-align: center; margin: 0; line-height: 1.4; }}
    </style>
    <div class="page-footer"><p>{t['data_source']} · {t['data_source_note']}</p></div>
    """), unsafe_allow_html=True)


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
        .{class_name} tr:last-child td {{
            border-bottom: none;
        }}
        .{class_name} tr:hover td {{
            background: #fafaf8;
        }}
        .{class_name} .hr-color-box {{
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
# SHARED HELPERS — WINNER BY COMMUNE
# ============================================================================
CANDIDATES_2021 = ["boric_pct", "kast_pct", "parisi_pct", "sichel_pct", "provoste_pct"]
CANDIDATES_2025_COLS = ["jara_pct", "kast_pct", "parisi_pct", "kaiser_pct", "matthei_pct"]

# Internal lookup: internal key (no translation) -> canonical name (to resolve color per year).
REF_2021_BY_KEY = {
    "boric":    "Gabriel Boric",
    "kast":     "José Antonio Kast",
    "parisi":   "Franco Parisi",
    "sichel":   "Sebastián Sichel",
    "provoste": "Yasna Provoste",
}
REF_2025_BY_KEY = {
    "jara":    "Jeannette Jara",
    "kast":    "José Antonio Kast",
    "parisi":  "Franco Parisi",
    "kaiser":  "Johannes Kaiser",
    "matthei": "Evelyn Matthei",
}


def _labels_2021(t: dict) -> dict:
    return {
        "boric":    t["fr_hist_label_2021_boric"],
        "kast":     t["fr_hist_label_2021_kast"],
        "parisi":   t["fr_hist_label_2021_parisi"],
        "sichel":   t["fr_hist_label_2021_sichel"],
        "provoste": t["fr_hist_label_2021_provoste"],
    }


def _labels_2025(t: dict) -> dict:
    return {
        "jara":    t["fr_hist_label_2025_jara"],
        "kast":    t["fr_hist_label_2025_kast"],
        "parisi":  t["fr_hist_label_2025_parisi"],
        "kaiser":  t["fr_hist_label_2025_kaiser"],
        "matthei": t["fr_hist_label_2025_matthei"],
    }


def _add_winner_columns(df: pd.DataFrame, year: str, t: dict) -> pd.DataFrame:
    """Add winner_{year}, winner_pct_{year}, and winner_key_{year} columns."""
    out = df.copy()
    if year == "2021":
        cols = CANDIDATES_2021
        labels = _labels_2021(t)
    else:
        cols = CANDIDATES_2025_COLS
        labels = _labels_2025(t)

    for c in cols:
        if c in out.columns:
            out[c] = out[c].fillna(0)

    # Internal key (no translation): "boric", "jara", etc.
    out[f"winner_key_{year}"] = (
        out[cols].idxmax(axis=1)
        .str.replace("_pct", "", regex=False)
    )
    # Translated label: "Boric (Left)", "Jara (Left)", etc.
    out[f"winner_{year}"] = out[f"winner_key_{year}"].map(labels)
    out[f"winner_pct_{year}"] = out[cols].max(axis=1)
    return out


def _color_for_key_2021(key: str) -> str:
    """Given a 2021 internal key, return the candidate's color."""
    ref = REF_2021_BY_KEY.get(key, "")
    return _color_2021(ref) if ref else NEUTRAL_COLOR


def _color_for_key_2025(key: str) -> str:
    """Given a 2025 internal key, return the candidate's color."""
    ref = REF_2025_BY_KEY.get(key, "")
    return _color_2025(ref) if ref else NEUTRAL_COLOR


# ============================================================================
# SECTION NO. 0 — FEATURED CARDS
# ============================================================================
def _render_featured_cards(df_2021, df_2025, t: dict) -> None:
    total_cast_2021 = int(df_2021["casted_votes"].sum())
    total_cast_2025 = int(df_2025["casted_votes"].sum())
    cast_growth = ((total_cast_2025 - total_cast_2021) / total_cast_2021 * 100) if total_cast_2021 else 0

    candidates_2025 = [
        ("Jeannette Jara", "jara_votes"),
        ("José Antonio Kast", "kast_votes"),
        ("Franco Parisi", "parisi_votes"),
        ("Johannes Kaiser", "kaiser_votes"),
        ("Evelyn Matthei", "matthei_votes"),
        ("Harold Mayne-Nicholls", "mayne_nicholls_votes"),
        ("Marco Enríquez-Ominami", "enriquez_ominami_votes"),
        ("Eduardo Artés", "artes_votes"),
    ]
    total_valid_2025 = total_cast_2025 - int(df_2025["blank_votes"].sum()) - int(df_2025["null_votes"].sum())
    suma_sq = 0.0
    for _, col in candidates_2025:
        if col in df_2025.columns and total_valid_2025 > 0:
            pct = int(df_2025[col].sum()) / total_valid_2025
            suma_sq += pct ** 2
    efectivo_2025 = (1 / suma_sq) if suma_sq > 0 else 0

    df_21 = _add_winner_columns(df_2021, "2021", t)
    df_25 = _add_winner_columns(df_2025, "2025", t)
    merge = df_21[["commune_id", "winner_key_2021"]].merge(
        df_25[["commune_id", "winner_key_2025"]],
        on="commune_id",
        how="inner",
    )
    communes_changed = int((merge["winner_key_2021"] != merge["winner_key_2025"]).sum())
    total_communes = len(merge)
    pct_changed = (communes_changed / total_communes * 100) if total_communes else 0

    parisi_2021 = int(df_2021["parisi_votes"].sum())
    parisi_2025 = int(df_2025["parisi_votes"].sum())
    parisi_growth_pct = ((parisi_2025 - parisi_2021) / parisi_2021 * 100) if parisi_2021 else 0
    parisi_color = _color_2025("Franco Parisi")

    cards_html = f"""
    <style>
        .nb-cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
        .nb-card {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 160px; }}
        .nb-card-label {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 10pt; color: #6b7280; font-weight: 500; letter-spacing: 0.2px; }}
        .nb-card-value {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; }}
        .nb-card-sub {{ font-family: "Liberation Sans", Arial, sans-serif; font-size: 9pt; font-weight: 400; color: #6b7280; margin-top: 8px; }}
    </style>
    <div class="nb-cards">
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_hist_kpi_cast_growth']}</div>
            <div class="nb-card-value">+{cast_growth:.1f}%</div>
            <div class="nb-card-sub"><b>{t['fr_hist_kpi_voto_obligatorio']}</b></div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_hist_kpi_efectivo_2025']}</div>
            <div class="nb-card-value">{efectivo_2025:.2f}</div>
            <div class="nb-card-sub">{t['fr_hist_kpi_fragmentacion_sub']}</div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_hist_kpi_comunas_cambiaron']}</div>
            <div class="nb-card-value">{communes_changed}</div>
            <div class="nb-card-sub"><b>{t['fr_hist_kpi_pct_comparado'].format(pct=f"{pct_changed:.1f}")}</b></div>
        </div>
        <div class="nb-card">
            <div class="nb-card-label">{t['fr_hist_kpi_parisi_growth']}</div>
            <div class="nb-card-value">+{parisi_growth_pct:.0f}%</div>
            <div class="nb-card-sub">vs 2021 · <span style="color:{parisi_color};">{t['fr_hist_kpi_parisi_sub']}</span></div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)


# ============================================================================
# SECTION NO. 1 — PARTICIPATION 2021 VS 2025
# ============================================================================
def _render_participation(df_2021, df_2025, t: dict) -> None:
    total_cast_2021 = int(df_2021["casted_votes"].sum())
    total_blank_2021 = int(df_2021["blank_votes"].sum())
    total_null_2021 = int(df_2021["null_votes"].sum())
    total_valid_2021 = total_cast_2021 - total_blank_2021 - total_null_2021

    total_cast_2025 = int(df_2025["casted_votes"].sum())
    total_blank_2025 = int(df_2025["blank_votes"].sum())
    total_null_2025 = int(df_2025["null_votes"].sum())
    total_valid_2025 = total_cast_2025 - total_blank_2025 - total_null_2025

    cast_growth = ((total_cast_2025 - total_cast_2021) / total_cast_2021 * 100) if total_cast_2021 else 0

    filas = [
        (t["casted_votes"], total_cast_2021, total_cast_2025, COLOR_POSITIVE),
        (t["valid_votes"],  total_valid_2021, total_valid_2025, COLOR_POSITIVE),
        (t["null_votes"],   total_null_2021, total_null_2025, COLOR_NEGATIVE),
        (t["blank_votes"],  total_blank_2021, total_blank_2025, COLOR_NEGATIVE),
    ]

    rows_html = ""
    for label, v21, v25, delta_color in filas:
        delta = v25 - v21
        delta_pct = (delta / v21 * 100) if v21 else 0
        delta_sign = "+" if delta >= 0 else ""
        rows_html += (
            f"<tr>"
            f"<td style=\"color:#333;\">{label}</td>"
            f"<td style=\"text-align:right; color:#666;\">{_fmt_number(v21)}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{_fmt_number(v25)}</td>"
            f"<td style=\"text-align:right; color:{delta_color};\">{delta_sign}{_fmt_number(delta)}</td>"
            f"<td style=\"text-align:right; color:{delta_color};\">{delta_sign}{delta_pct:.2f}%</td>"
            f"</tr>"
        )

    pct_filas = [
        ("% válidos sobre emitidos", total_valid_2021 / total_cast_2021 * 100, total_valid_2025 / total_cast_2025 * 100, True),
        ("% nulos sobre emitidos",   total_null_2021  / total_cast_2021 * 100, total_null_2025  / total_cast_2025 * 100, False),
        ("% blancos sobre emitidos", total_blank_2021 / total_cast_2021 * 100, total_blank_2025 / total_cast_2025 * 100, False),
    ]

    rows_pct_html = ""
    for label, p21, p25, bold_delta in pct_filas:
        delta_pp = p25 - p21
        delta_sign = "+" if delta_pp >= 0 else ""
        delta_weight = "700" if bold_delta else "400"
        rows_pct_html += (
            f"<tr>"
            f"<td style=\"color:#333;\">{label}</td>"
            f"<td style=\"text-align:right; color:#666;\">{p21:.2f}%</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{p25:.2f}%</td>"
            f"<td style=\"text-align:right; color:{COLOR_NEGATIVE}; font-weight:{delta_weight};\">{delta_sign}{delta_pp:.2f} pp</td>"
            f"<td></td>"
            f"</tr>"
        )

    html = _table_css("hr-tabla-participacion") + f"""
    <div class="hr-tabla-participacion">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_hist_th_metric']}</th>
                    <th style="text-align:right;">2021</th>
                    <th style="text-align:right;">2025</th>
                    <th style="text-align:right;">{t['fr_hist_th_delta']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_delta_pct']}</th>
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

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px;\">"
        f"{t['fr_hist_note_participacion'].format(pct=f'{cast_growth:.1f}')}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 2 — POLITICAL BLOCKS 2021 VS 2025
# ============================================================================
def _render_blocks(df_2021, df_2025, t: dict) -> None:
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

    def _s(df, col):
        return int(df[col].sum()) if col in df.columns else 0

    bloques = [
        {
            "bloque": t["fr_hist_bloque_izq"],
            "cand_2021": "Boric + Provoste",
            "cand_2025": "Jara",
            "votes_2021": _s(df_2021, "boric_votes") + _s(df_2021, "provoste_votes"),
            "votes_2025": _s(df_2025, "jara_votes"),
            "color_ref_2025": "Jeannette Jara",
        },
        {
            "bloque": t["fr_hist_bloque_der_cons"],
            "cand_2021": "Kast",
            "cand_2025": "Kast",
            "votes_2021": _s(df_2021, "kast_votes"),
            "votes_2025": _s(df_2025, "kast_votes"),
            "color_ref_2025": "José Antonio Kast",
        },
        {
            "bloque": t["fr_hist_bloque_der_trad"],
            "cand_2021": "Sichel",
            "cand_2025": "Matthei",
            "votes_2021": _s(df_2021, "sichel_votes"),
            "votes_2025": _s(df_2025, "matthei_votes"),
            "color_ref_2025": "Evelyn Matthei",
        },
        {
            "bloque": t["fr_hist_bloque_antisistema"],
            "cand_2021": "Parisi",
            "cand_2025": "Parisi",
            "votes_2021": _s(df_2021, "parisi_votes"),
            "votes_2025": _s(df_2025, "parisi_votes"),
            "color_ref_2025": "Franco Parisi",
        },
        {
            "bloque": t["fr_hist_bloque_libertario"],
            "cand_2021": t["fr_hist_bloque_no_existia"],
            "cand_2025": "Kaiser",
            "votes_2021": 0,
            "votes_2025": _s(df_2025, "kaiser_votes"),
            "color_ref_2025": "Johannes Kaiser",
        },
        {
            "bloque": t["fr_hist_bloque_izq_alt"],
            "cand_2021": "MEO",
            "cand_2025": "MEO",
            "votes_2021": _s(df_2021, "enriquez_ominami_votes"),
            "votes_2025": _s(df_2025, "enriquez_ominami_votes"),
            "color_ref_2025": "Marco Enríquez-Ominami",
        },
        {
            "bloque": t["fr_hist_bloque_izq_rad"],
            "cand_2021": "Artés",
            "cand_2025": "Artés",
            "votes_2021": _s(df_2021, "artes_votes"),
            "votes_2025": _s(df_2025, "artes_votes"),
            "color_ref_2025": "Eduardo Artés",
        },
        {
            "bloque": t["fr_hist_bloque_indep"],
            "cand_2021": t["fr_hist_bloque_no_existia"],
            "cand_2025": "Mayne-Nicholls",
            "votes_2021": 0,
            "votes_2025": _s(df_2025, "mayne_nicholls_votes"),
            "color_ref_2025": "Harold Mayne-Nicholls",
        },
    ]

    rows_html = ""
    for b in bloques:
        p21 = (b["votes_2021"] / total_valid_2021 * 100) if total_valid_2021 else 0
        p25 = (b["votes_2025"] / total_valid_2025 * 100) if total_valid_2025 else 0
        delta_pp = p25 - p21
        delta_sign = "+" if delta_pp >= 0 else ""
        delta_color = COLOR_POSITIVE if delta_pp >= 0 else COLOR_NEGATIVE
        color = _color_2025(b["color_ref_2025"])

        rows_html += (
            f"<tr>"
            f"<td style=\"font-weight:600;\">"
            f"<span class=\"hr-color-box\" style=\"background:{color};\"></span>{b['bloque']}"
            f"</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{b['cand_2021']}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{b['cand_2025']}</td>"
            f"<td style=\"text-align:right; color:#666;\">{_fmt_number(b['votes_2021'])}</td>"
            f"<td style=\"text-align:right; color:#666;\">{p21:.2f}%</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{_fmt_number(b['votes_2025'])}</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{p25:.2f}%</td>"
            f"<td style=\"text-align:right; color:{delta_color};\">{delta_sign}{delta_pp:.2f} pp</td>"
            f"</tr>"
        )

    html = _table_css("hr-tabla-bloques") + f"""
    <div class="hr-tabla-bloques">
        <table>
            <thead>
                <tr>
                    <th rowspan="2">{t['fr_hist_th_bloque']}</th>
                    <th rowspan="2">{t['fr_hist_th_cand_2021']}</th>
                    <th rowspan="2">{t['fr_hist_th_cand_2025']}</th>
                    <th colspan="2" style="text-align:center;">2021</th>
                    <th colspan="2" style="text-align:center;">2025</th>
                    <th rowspan="2" style="text-align:right;">{t['fr_hist_th_delta_pp']}</th>
                </tr>
                <tr>
                    <th style="text-align:right;">{t['fr_hist_th_votos']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_votos']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct']}</th>
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

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px;\">"
        f"{t['fr_hist_note_bloques']}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    izq_2021 = (
        _s(df_2021, "boric_votes")
        + _s(df_2021, "provoste_votes")
        + _s(df_2021, "enriquez_ominami_votes")
        + _s(df_2021, "artes_votes")
    )
    cen_2021 = _s(df_2021, "parisi_votes")
    der_2021 = _s(df_2021, "kast_votes") + _s(df_2021, "sichel_votes")

    pct_izq_2021 = izq_2021 / total_valid_2021 * 100 if total_valid_2021 else 0
    pct_cen_2021 = cen_2021 / total_valid_2021 * 100 if total_valid_2021 else 0
    pct_der_2021 = der_2021 / total_valid_2021 * 100 if total_valid_2021 else 0

    izq_2025 = (
        _s(df_2025, "jara_votes")
        + _s(df_2025, "enriquez_ominami_votes")
        + _s(df_2025, "artes_votes")
    )
    cen_2025 = _s(df_2025, "parisi_votes") + _s(df_2025, "mayne_nicholls_votes")
    der_2025 = (
        _s(df_2025, "kast_votes")
        + _s(df_2025, "kaiser_votes")
        + _s(df_2025, "matthei_votes")
    )

    pct_izq_2025 = izq_2025 / total_valid_2025 * 100 if total_valid_2025 else 0
    pct_cen_2025 = cen_2025 / total_valid_2025 * 100 if total_valid_2025 else 0
    pct_der_2025 = der_2025 / total_valid_2025 * 100 if total_valid_2025 else 0

    COLOR_IZQ = POLITICAL_BLOCKS["Izquierda"]
    COLOR_CEN = POLITICAL_BLOCKS["Antisistema"]
    COLOR_DER = POLITICAL_BLOCKS["Derecha"]

    html_barras = f"""
    <style>
        .bloques-barras-wrap {{ font-family: "Liberation Sans", Arial, sans-serif; max-width: 940px; }}
        .bloques-año {{ margin-bottom: 36px; }}
        .bloques-año-titulo {{ font-size: 12pt; font-weight: 700; color: #111827; margin-bottom: 10px; }}
        .bloques-labels {{ display: flex; margin-bottom: 6px; font-size: 8pt; color: #6b7280; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; }}
        .bloques-labels > div {{ white-space: nowrap; }}
        .bloques-bar-wrap {{ position: relative; margin-bottom: 14px; }}
        .bloques-bar {{ display: flex; height: 48px; border-radius: 6px; overflow: hidden; }}
        .bloques-bar > div {{ display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 13pt; }}
        .bloques-midline {{ position: absolute; top: -8px; bottom: -8px; left: 50%; width: 0; border-left: 1px dashed #6b7280; pointer-events: none; }}
        .bloques-details {{ display: flex; margin-bottom: 8px; }}
        .bloques-detail {{ padding: 0 6px; }}
        .bloques-cands {{ font-size: 10pt; color: #333; margin-bottom: 4px; }}
        .bloques-votes {{ font-size: 12pt; font-weight: 700; color: #111827; }}
        .bloques-legend {{ display: flex; flex-direction: column; gap: 8px; font-size: 9pt; color: #333; margin-top: 24px; }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; }}
        .legend-dot {{ width: 13px; height: 13px; border-radius: 3px; display: inline-block; flex-shrink: 0; }}
    </style>
    <div class="bloques-barras-wrap">
        <div class="bloques-año">
            <div class="bloques-año-titulo">2021</div>
            <div class="bloques-labels">
                <div style="width: {pct_izq_2021}%; text-align: left;">{t['fr_hist_bloque_izq']}</div>
                <div style="width: {pct_cen_2021}%; text-align: center;">{t['fr_hist_bloque_antisistema']}</div>
                <div style="width: {pct_der_2021}%; text-align: right;">{t['fr_hist_bloque_der_cons']}</div>
            </div>
            <div class="bloques-bar-wrap">
                <div class="bloques-midline"></div>
                <div class="bloques-bar">
                    <div style="width: {pct_izq_2021}%; background: {COLOR_IZQ};">{pct_izq_2021:.2f}%</div>
                    <div style="width: {pct_cen_2021}%; background: {COLOR_CEN};">{pct_cen_2021:.2f}%</div>
                    <div style="width: {pct_der_2021}%; background: {COLOR_DER};">{pct_der_2021:.2f}%</div>
                </div>
            </div>
            <div class="bloques-details">
                <div class="bloques-detail" style="width: {pct_izq_2021}%; text-align: left;">
                    <div class="bloques-cands">Boric + Provoste + ME-O + Artés</div>
                    <div class="bloques-votes">{_fmt_number(izq_2021)} {t['votes']}</div>
                </div>
                <div class="bloques-detail" style="width: {pct_cen_2021}%; text-align: center;">
                    <div class="bloques-cands">Parisi</div>
                    <div class="bloques-votes">{_fmt_number(cen_2021)} {t['votes']}</div>
                </div>
                <div class="bloques-detail" style="width: {pct_der_2021}%; text-align: right;">
                    <div class="bloques-cands">Kast + Sichel</div>
                    <div class="bloques-votes">{_fmt_number(der_2021)} {t['votes']}</div>
                </div>
            </div>
        </div>

        <div class="bloques-año">
            <div class="bloques-año-titulo">2025</div>
            <div class="bloques-labels">
                <div style="width: {pct_izq_2025}%; text-align: left;">{t['fr_hist_bloque_izq']}</div>
                <div style="width: {pct_cen_2025}%; text-align: center;">{t['fr_hist_bloque_antisistema']}</div>
                <div style="width: {pct_der_2025}%; text-align: right;">{t['fr_hist_bloque_der_cons']}</div>
            </div>
            <div class="bloques-bar-wrap">
                <div class="bloques-midline"></div>
                <div class="bloques-bar">
                    <div style="width: {pct_izq_2025}%; background: {COLOR_IZQ};">{pct_izq_2025:.2f}%</div>
                    <div style="width: {pct_cen_2025}%; background: {COLOR_CEN};">{pct_cen_2025:.2f}%</div>
                    <div style="width: {pct_der_2025}%; background: {COLOR_DER};">{pct_der_2025:.2f}%</div>
                </div>
            </div>
            <div class="bloques-details">
                <div class="bloques-detail" style="width: {pct_izq_2025}%; text-align: left;">
                    <div class="bloques-cands">Jara + ME-O + Artés</div>
                    <div class="bloques-votes">{_fmt_number(izq_2025)} {t['votes']}</div>
                </div>
                <div class="bloques-detail" style="width: {pct_cen_2025}%; text-align: center;">
                    <div class="bloques-cands">Parisi + Mayne-Nicholls</div>
                    <div class="bloques-votes">{_fmt_number(cen_2025)} {t['votes']}</div>
                </div>
                <div class="bloques-detail" style="width: {pct_der_2025}%; text-align: right;">
                    <div class="bloques-cands">Kast + Kaiser + Matthei</div>
                    <div class="bloques-votes">{_fmt_number(der_2025)} {t['votes']}</div>
                </div>
            </div>
        </div>

        <div class="bloques-legend">
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_IZQ};"></span>{t['fr_hist_bloque_izq']}</div>
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_CEN};"></span>{t['fr_hist_bloque_antisistema']}</div>
            <div class="legend-item"><span class="legend-dot" style="background: {COLOR_DER};"></span>{t['fr_hist_bloque_der_cons']}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(html_barras), unsafe_allow_html=True)

    delta_izq = pct_izq_2025 - pct_izq_2021
    delta_cen = pct_cen_2025 - pct_cen_2021
    delta_der = pct_der_2025 - pct_der_2021

    def _signo(v):
        return "+" if v >= 0 else ""

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 18px; line-height: 1.8;\">"
        f"<b>{t['fr_hist_card_cambio_pp']}:</b> "
        f"{t['fr_hist_bloque_izq']} <span style=\"color:#6B7280; font-weight:700;\">{_signo(delta_izq)}{delta_izq:.2f} pp</span> · "
        f"{t['fr_hist_bloque_antisistema']} <span style=\"color:#6B7280; font-weight:700;\">{_signo(delta_cen)}{delta_cen:.2f} pp</span> · "
        f"{t['fr_hist_bloque_der_cons']} <span style=\"color:#6B7280; font-weight:700;\">{_signo(delta_der)}{delta_der:.2f} pp</span>."
        f"<br>{t['fr_hist_note_parisi_region']}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 3 — ELECTORAL REALIGNMENT
# ============================================================================
def _render_realignment(df_2021, df_2025, t: dict) -> None:
    df_21 = _add_winner_columns(df_2021, "2021", t)
    df_25 = _add_winner_columns(df_2025, "2025", t)

    realignment = df_21[["commune_id", "winner_2021", "winner_key_2021"]].merge(
        df_25[["commune_id", "winner_2025", "winner_key_2025"]],
        on="commune_id",
        how="inner",
    )

    realignment["change_type"] = (
        realignment["winner_key_2021"] == realignment["winner_key_2025"]
    ).map({True: t["fr_hist_card_se_mantiene"], False: t["fr_hist_card_cambia"]})

    resumen = realignment["change_type"].value_counts().to_dict()
    mantienen = int(resumen.get(t["fr_hist_card_se_mantiene"], 0))
    cambian = int(resumen.get(t["fr_hist_card_cambia"], 0))
    total_communes = len(realignment)

    pct_mantienen = (mantienen / total_communes * 100) if total_communes else 0
    pct_cambian = (cambian / total_communes * 100) if total_communes else 0

    cards_html = f"""
    <style>
        .hr-cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
        .hr-card {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }}
        .hr-card-label {{ font-size: 10pt; color: #6b7280; font-weight: 500; }}
        .hr-card-value {{ font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; }}
        .hr-card-sub {{ font-size: 9pt; color: #6b7280; margin-top: 8px; font-weight: 400; }}
    </style>
    <div class="hr-cards">
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_comunas_comp']}</div>
            <div class="hr-card-value">{total_communes}</div>
            <div class="hr-card-sub">{t['fr_hist_card_comunas_comp_sub']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_se_mantiene']}</div>
            <div class="hr-card-value">{mantienen}</div>
            <div class="hr-card-sub">{t['fr_hist_card_pct_total'].format(pct=f"{pct_mantienen:.1f}")}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_cambia']}</div>
            <div class="hr-card-value">{cambian}</div>
            <div class="hr-card-sub">{t['fr_hist_card_pct_total'].format(pct=f"{pct_cambian:.1f}")}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    labels_21 = _labels_2021(t)
    labels_25 = _labels_2025(t)
    all_2021 = [labels_21[k] for k in ["boric", "kast", "parisi", "sichel", "provoste"]]
    all_2025 = [labels_25[k] for k in ["jara", "kast", "parisi", "kaiser", "matthei"]]

    matriz = pd.crosstab(
        realignment["winner_2021"],
        realignment["winner_2025"],
    ).reindex(index=all_2021, columns=all_2025, fill_value=0)

    color_2025 = {lbl: _color_for_key_2025(k) for k, lbl in labels_25.items()}

    header_2025_html = ""
    for c in all_2025:
        header_2025_html += f"<th style=\"text-align:center; font-weight:700 !important;\">{c}</th>"

    body_html = ""
    for r_label in all_2021:
        cells = ""
        for c_label in all_2025:
            val = int(matriz.loc[r_label, c_label]) if r_label in matriz.index and c_label in matriz.columns else 0
            if val == 0:
                cells += f"<td style=\"text-align:center; color:{COLOR_NEUTRAL_INDICATOR}; font-weight:400;\">·</td>"
            else:
                bg = _hex_to_rgba(color_2025[c_label], 0.18)
                cells += (
                    f"<td style=\"text-align:center; font-weight:400; color:#111827; "
                    f"background:{bg} !important;\">{val}</td>"
                )
        body_html += (
            f"<tr>"
            f"<td style=\"font-weight:700; color:#333;\">{r_label}</td>"
            f"{cells}"
            f"</tr>"
        )

    html_matriz = _table_css("hr-tabla-realineamiento-matriz") + f"""
    <div class="hr-tabla-realineamiento-matriz">
        <table>
            <thead>
                <tr>
                    <th style="font-weight:700 !important;">2021 \\ 2025</th>
                    {header_2025_html}
                </tr>
            </thead>
            <tbody>
                {body_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_matriz), unsafe_allow_html=True)
    _table_gap()

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px;\">"
        f"{t['fr_hist_note_realineamiento']}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 4 — WINNER CHANGES GROUPED BY TRANSITION
# ============================================================================
def _render_grouped_changes(df_2021, df_2025, t: dict) -> None:
    df_21 = _add_winner_columns(df_2021, "2021", t)
    df_25 = _add_winner_columns(df_2025, "2025", t)

    merge = df_21[["commune_id", "winner_2021", "winner_key_2021", "winner_pct_2021"]].merge(
        df_25[["commune_id", "winner_2025", "winner_key_2025", "winner_pct_2025"]],
        on="commune_id",
        how="inner",
    )

    changed = merge[merge["winner_key_2021"] != merge["winner_key_2025"]].copy()

    if changed.empty:
        st.info(t["fr_hist_info_sin_cambios"])
        return

    grouped = (
        changed.groupby(["winner_key_2021", "winner_key_2025"])
        .agg(
            comunas=("commune_id", "count"),
            pct_2025_min=("winner_pct_2025", "min"),
            pct_2025_max=("winner_pct_2025", "max"),
            pct_2025_prom=("winner_pct_2025", "mean"),
        )
        .reset_index()
        .sort_values("comunas", ascending=False)
        .reset_index(drop=True)
    )

    total_changes = int(grouped["comunas"].sum())
    labels_21 = _labels_2021(t)
    labels_25 = _labels_2025(t)

    rows_html = ""
    for i, r in grouped.iterrows():
        rank = i + 1
        color_21 = _color_for_key_2021(r["winner_key_2021"])
        color_25 = _color_for_key_2025(r["winner_key_2025"])
        label_21 = labels_21.get(r["winner_key_2021"], r["winner_key_2021"])
        label_25 = labels_25.get(r["winner_key_2025"], r["winner_key_2025"])

        rows_html += (
            f"<tr>"
            f"<td style=\"color:#9a9a9a; text-align:center;\">{rank}</td>"
            f"<td style=\"font-weight:400; color:#333;\">"
            f"<span class=\"hr-color-box\" style=\"background:{color_21};\"></span>{label_21}"
            f"</td>"
            f"<td style=\"color:#9a9a9a; text-align:center;\">→</td>"
            f"<td style=\"font-weight:400; color:#333;\">"
            f"<span class=\"hr-color-box\" style=\"background:{color_25};\"></span>{label_25}"
            f"</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{int(r['comunas'])}</td>"
            f"<td style=\"text-align:right; color:#666;\">{r['pct_2025_min']:.2f}%</td>"
            f"<td style=\"text-align:right; color:#666;\">{r['pct_2025_prom']:.2f}%</td>"
            f"<td style=\"text-align:right; color:#666;\">{r['pct_2025_max']:.2f}%</td>"
            f"</tr>"
        )

    html = _table_css("hr-tabla-transiciones") + f"""
    <div class="hr-tabla-transiciones">
        <table>
            <thead>
                <tr>
                    <th style="text-align:center;">#</th>
                    <th>{t['fr_hist_th_ganador_2021']}</th>
                    <th style="text-align:center;">→</th>
                    <th>{t['fr_hist_th_ganador_2025']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_comunas']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_min_2025']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_prom_2025']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_max_2025']}</th>
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

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px;\">"
        f"{t['fr_hist_note_transiciones'].format(total=total_changes)}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 5 — DECISIVE VS CLOSE
# ============================================================================
def _render_decisive_vs_close(df_2021, df_2025, t: dict) -> None:
    df_21 = _add_winner_columns(df_2021, "2021", t)
    df_25 = _add_winner_columns(df_2025, "2025", t)

    merge = df_21[[
        "commune_id", "commune_name", "region_name",
        "winner_2021", "winner_key_2021", "winner_pct_2021",
    ]].merge(
        df_25[["commune_id", "winner_2025", "winner_key_2025", "winner_pct_2025"]],
        on="commune_id",
        how="inner",
    )

    changed = merge[merge["winner_key_2021"] != merge["winner_key_2025"]].copy()

    if changed.empty:
        st.info(t["fr_hist_info_sin_cambios"])
        return

    total_changes = len(changed)

    DECISIVE_THRESHOLD = 40.0
    CLOSE_THRESHOLD = 30.0

    decisive = int((changed["winner_pct_2025"] >= DECISIVE_THRESHOLD).sum())
    close = int((changed["winner_pct_2025"] < CLOSE_THRESHOLD).sum())

    pct_decisive = (decisive / total_changes * 100) if total_changes else 0
    pct_close = (close / total_changes * 100) if total_changes else 0

    cards_html = f"""
    <style>
        .hr-cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
        .hr-card {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }}
        .hr-card-label {{ font-size: 10pt; color: #6b7280; font-weight: 500; }}
        .hr-card-value {{ font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; }}
        .hr-card-sub {{ font-size: 9pt; color: #6b7280; margin-top: 8px; font-weight: 400; }}
    </style>
    <div class="hr-cards">
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_comunas_comp']}</div>
            <div class="hr-card-value">{total_changes}</div>
            <div class="hr-card-sub">{t['fr_hist_card_comunas_comp_sub']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_contundentes']}</div>
            <div class="hr-card-value">{decisive}</div>
            <div class="hr-card-sub">{pct_decisive:.1f}% · {t['fr_hist_card_contundentes_sub']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_reñidas']}</div>
            <div class="hr-card-value">{close}</div>
            <div class="hr-card-sub">{pct_close:.1f}% · {t['fr_hist_card_reñidas_sub']}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    labels_21 = _labels_2021(t)
    labels_25 = _labels_2025(t)

    def _tabla_cambios(df_sub, titulo):
        render_section_title(titulo)
        rows_html = ""
        for i, r in df_sub.iterrows():
            rank = i + 1
            comuna = str(r.get("commune_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            region = str(r.get("region_name", "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            color_21 = _color_for_key_2021(r["winner_key_2021"])
            color_25 = _color_for_key_2025(r["winner_key_2025"])
            label_21 = labels_21.get(r["winner_key_2021"], r["winner_key_2021"])
            label_25 = labels_25.get(r["winner_key_2025"], r["winner_key_2025"])

            rows_html += (
                f"<tr>"
                f"<td style=\"color:#9a9a9a; text-align:center;\">{rank}</td>"
                f"<td style=\"font-weight:400; color:#333;\">{comuna}</td>"
                f"<td style=\"color:#6b7280; font-size:9.5pt;\">{region}</td>"
                f"<td style=\"color:#333;\">"
                f"<span class=\"hr-color-box\" style=\"background:{color_21};\"></span>{label_21}"
                f"</td>"
                f"<td style=\"color:#333;\">"
                f"<span class=\"hr-color-box\" style=\"background:{color_25};\"></span>{label_25}"
                f"</td>"
                f"<td style=\"text-align:right; color:#666;\">{r['winner_pct_2021']:.2f}%</td>"
                f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{r['winner_pct_2025']:.2f}%</td>"
                f"</tr>"
            )

        html = _table_css("hr-tabla-top-cambios") + f"""
        <div class="hr-tabla-top-cambios">
            <table>
                <thead>
                    <tr>
                        <th style="text-align:center;">#</th>
                        <th>{t['fr_hist_th_comuna']}</th>
                        <th>{t['fr_hist_th_region_short']}</th>
                        <th>{t['fr_hist_th_ganador_2021']}</th>
                        <th>{t['fr_hist_th_ganador_2025']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_pct_gan_2021']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_pct_gan_2025']}</th>
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
    _tabla_cambios(top_decisive, t["fr_hist_section_top_contundentes"])

    top_close = changed.nsmallest(10, "winner_pct_2025").reset_index(drop=True)
    _tabla_cambios(top_close, t["fr_hist_section_top_reñidas"])

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px; line-height: 1.6;\">"
        f"{t['fr_hist_note_contundentes']} {t['fr_hist_note_reñidas']}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 6 — FRAGMENTATION
# ============================================================================
def _render_fragmentation(df_2021, df_2025, t: dict) -> None:
    candidates_2021 = [
        ("Gabriel Boric", "boric_votes"),
        ("José Antonio Kast", "kast_votes"),
        ("Franco Parisi", "parisi_votes"),
        ("Yasna Provoste", "provoste_votes"),
        ("Sebastián Sichel", "sichel_votes"),
        ("Marco Enríquez-Ominami", "enriquez_ominami_votes"),
        ("Eduardo Artés", "artes_votes"),
    ]
    candidates_2025 = [
        ("Jeannette Jara", "jara_votes"),
        ("José Antonio Kast", "kast_votes"),
        ("Franco Parisi", "parisi_votes"),
        ("Johannes Kaiser", "kaiser_votes"),
        ("Evelyn Matthei", "matthei_votes"),
        ("Harold Mayne-Nicholls", "mayne_nicholls_votes"),
        ("Marco Enríquez-Ominami", "enriquez_ominami_votes"),
        ("Eduardo Artés", "artes_votes"),
    ]

    def _build_rows(df, candidates):
        total_valid = (
            int(df["casted_votes"].sum())
            - int(df["blank_votes"].sum())
            - int(df["null_votes"].sum())
        )
        rows = []
        for nombre, col in candidates:
            if col not in df.columns or total_valid == 0:
                continue
            votes = int(df[col].sum())
            pct = votes / total_valid * 100
            rows.append({
                "nombre": nombre,
                "votes": votes,
                "pct": pct,
                "pct_sq": (pct / 100) ** 2,
                "color_ref": nombre,
            })
        rows.sort(key=lambda r: r["pct"], reverse=True)
        sum_sq = sum(r["pct_sq"] for r in rows)
        effective = (1 / sum_sq) if sum_sq > 0 else 0
        for r in rows:
            r["aporte_pct"] = (r["pct_sq"] / sum_sq * 100) if sum_sq > 0 else 0
        return rows, effective

    rows_2021, effective_2021 = _build_rows(df_2021, candidates_2021)
    rows_2025, effective_2025 = _build_rows(df_2025, candidates_2025)

    delta_effective = effective_2025 - effective_2021
    signo = "+" if delta_effective >= 0 else ""
    sub_label = t["fr_hist_card_mas_fragmentado"] if delta_effective >= 0 else t["fr_hist_card_menos_fragmentado"]
    sub_color = COLOR_NEGATIVE if delta_effective >= 0 else COLOR_POSITIVE

    cards_html = f"""
    <style>
        .hr-cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
        .hr-card {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }}
        .hr-card-label {{ font-size: 10pt; color: #6b7280; font-weight: 500; }}
        .hr-card-value {{ font-size: 20pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.1; }}
        .hr-card-sub {{ font-size: 9pt; color: #6b7280; margin-top: 8px; font-weight: 400; }}
    </style>
    <div class="hr-cards">
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_efectivo_2021']}</div>
            <div class="hr-card-value">{effective_2021:.2f}</div>
            <div class="hr-card-sub">{t['fr_hist_card_sobre_validos']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_kpi_efectivo_2025']}</div>
            <div class="hr-card-value">{effective_2025:.2f}</div>
            <div class="hr-card-sub">{t['fr_hist_card_sobre_validos']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_cambio']}</div>
            <div class="hr-card-value">{signo}{delta_effective:.2f}</div>
            <div class="hr-card-sub"><span style="color:{sub_color}; font-weight:700;">{sub_label}</span></div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    def _build_frag_table(rows, section_key):
        render_section_title(section_key)
        rows_html = ""
        for r in rows:
            color = _color_2025(r["color_ref"]) if "2025" in section_key else _color_2021(r["color_ref"])
            rows_html += (
                f"<tr>"
                f"<td style=\"font-weight:400; color:#333;\">"
                f"<span class=\"hr-color-box\" style=\"background:{color};\"></span>{r['nombre']}"
                f"</td>"
                f"<td style=\"text-align:right; color:#666;\">{_fmt_number(r['votes'])}</td>"
                f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{r['pct']:.2f}%</td>"
                f"<td style=\"text-align:right; color:#666;\">{(r['pct']/100)**2:.4f}</td>"
                f"<td style=\"text-align:right; color:#666;\">{r['aporte_pct']:.1f}%</td>"
                f"</tr>"
            )
        html = _table_css("hr-tabla-frag") + f"""
        <div class="hr-tabla-frag">
            <table>
                <thead>
                    <tr>
                        <th>{t['fr_hist_th_candidato']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_votos']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_pct']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_p2']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_aporte']}</th>
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

    _build_frag_table(rows_2021, t["fr_hist_section_desglose_2021"])
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    _build_frag_table(rows_2025, t["fr_hist_section_desglose_2025"])

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px; line-height: 1.6;\">"
        f"{t['fr_hist_note_fragmentacion']}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 7 — PARISI: EVOLUTION AND TERRITORY
# ============================================================================
def _render_parisi_evolution_territory(df_2021, df_2025, t: dict) -> None:
    parisi_votes_2021 = int(df_2021["parisi_votes"].sum())
    parisi_votes_2025 = int(df_2025["parisi_votes"].sum())

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

    parisi_pct_2021 = (parisi_votes_2021 / total_valid_2021 * 100) if total_valid_2021 else 0
    parisi_pct_2025 = (parisi_votes_2025 / total_valid_2025 * 100) if total_valid_2025 else 0

    absolute_growth = parisi_votes_2025 - parisi_votes_2021
    growth_rate = (absolute_growth / parisi_votes_2021 * 100) if parisi_votes_2021 else 0
    change_pp = parisi_pct_2025 - parisi_pct_2021

    cards_html = f"""
    <style>
        .hr-cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
        .hr-card {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 14px 16px 12px 16px; flex: 1; min-width: 160px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-family: "Liberation Sans", Arial, sans-serif; }}
        .hr-card-label {{ font-size: 10pt; color: #6b7280; font-weight: 500; }}
        .hr-card-value {{ font-size: 15pt; font-weight: 700; color: #111827; margin-top: 6px; line-height: 1.2; }}
        .hr-card-sub {{ font-size: 9pt; color: #6b7280; margin-top: 8px; font-weight: 400; }}
    </style>
    <div class="hr-cards">
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_votos_2021']}</div>
            <div class="hr-card-value">{_fmt_number(parisi_votes_2021)}</div>
            <div class="hr-card-sub">{parisi_pct_2021:.2f}% {t['fr_hist_card_sobre_validos']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_votos_2025']}</div>
            <div class="hr-card-value">{_fmt_number(parisi_votes_2025)}</div>
            <div class="hr-card-sub">{parisi_pct_2025:.2f}% {t['fr_hist_card_sobre_validos']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_crecimiento_abs']}</div>
            <div class="hr-card-value">+{_fmt_number(absolute_growth)}</div>
            <div class="hr-card-sub">{t['fr_hist_card_votos_mas']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_tasa_crecimiento']}</div>
            <div class="hr-card-value">+{growth_rate:.1f}%</div>
            <div class="hr-card-sub">{t['fr_hist_card_vs_2021']}</div>
        </div>
        <div class="hr-card">
            <div class="hr-card-label">{t['fr_hist_card_cambio_pp']}</div>
            <div class="hr-card-value">+{change_pp:.2f} pp</div>
            <div class="hr-card-sub">{t['fr_hist_card_sobre_validos']}</div>
        </div>
    </div>
    """
    st.markdown(_clean_html(cards_html), unsafe_allow_html=True)
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    df_21 = df_2021.copy()
    df_25 = df_2025.copy()
    df_21["valid_votes"] = df_21["casted_votes"] - df_21["blank_votes"] - df_21["null_votes"]
    df_25["valid_votes"] = df_25["casted_votes"] - df_25["blank_votes"] - df_25["null_votes"]

    macro_21 = df_21.groupby(["macrozone", "macrozone_order"], as_index=False).agg(
        valid_2021=("valid_votes", "sum"),
        parisi_2021=("parisi_votes", "sum"),
    )
    macro_25 = df_25.groupby(["macrozone", "macrozone_order"], as_index=False).agg(
        valid_2025=("valid_votes", "sum"),
        parisi_2025=("parisi_votes", "sum"),
    )

    macro = macro_21.merge(macro_25, on=["macrozone", "macrozone_order"], how="outer")
    macro["parisi_pct_2021"] = macro["parisi_2021"] / macro["valid_2021"] * 100
    macro["parisi_pct_2025"] = macro["parisi_2025"] / macro["valid_2025"] * 100
    macro["change_pp"] = macro["parisi_pct_2025"] - macro["parisi_pct_2021"]
    macro = macro.sort_values("macrozone_order").reset_index(drop=True)

    render_section_title(t["fr_hist_section_parisi_macrozone"])

    rows_html = ""
    for _, r in macro.iterrows():
        change = r["change_pp"]
        signo = "+" if change >= 0 else ""
        color = COLOR_POSITIVE if change >= 0 else COLOR_NEGATIVE
        rows_html += (
            f"<tr>"
            f"<td style=\"font-weight:600; color:#333;\">{r['macrozone']}</td>"
            f"<td style=\"text-align:right; color:#666;\">{r['parisi_pct_2021']:.2f}%</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{r['parisi_pct_2025']:.2f}%</td>"
            f"<td style=\"text-align:right; color:{color};\">{signo}{change:.2f} pp</td>"
            f"<td style=\"text-align:right; color:#666; font-size:9.5pt;\">{_fmt_number(r['valid_2021'])}</td>"
            f"<td style=\"text-align:right; color:#666; font-size:9.5pt;\">{_fmt_number(r['valid_2025'])}</td>"
            f"</tr>"
        )

    html_macro = _table_css("hr-tabla-parisi-macro") + f"""
    <div class="hr-tabla-parisi-macro">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_hist_th_macrozone']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_2021']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_2025']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_delta_pp']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_validos_2021']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_validos_2025']}</th>
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

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    region_21 = df_21.groupby("region_name", as_index=False).agg(
        valid_2021=("valid_votes", "sum"),
        parisi_2021=("parisi_votes", "sum"),
    )
    region_25 = df_25.groupby("region_name", as_index=False).agg(
        valid_2025=("valid_votes", "sum"),
        parisi_2025=("parisi_votes", "sum"),
    )

    region = region_21.merge(region_25, on="region_name", how="outer")
    region["parisi_pct_2021"] = region["parisi_2021"] / region["valid_2021"] * 100
    region["parisi_pct_2025"] = region["parisi_2025"] / region["valid_2025"] * 100
    region["change_pp"] = region["parisi_pct_2025"] - region["parisi_pct_2021"]
    region["pct_growth"] = (
        (region["parisi_pct_2025"] - region["parisi_pct_2021"]) / region["parisi_pct_2021"] * 100
    )

    region_order_map = (
        df_25[["region_name", "region_order", "macrozone"]]
        .dropna()
        .drop_duplicates()
        .set_index("region_name")
        .to_dict(orient="index")
    )
    region["region_order"] = region["region_name"].map(
        lambda r: region_order_map.get(r, {}).get("region_order", 9999)
    )
    region["macrozone"] = region["region_name"].map(
        lambda r: region_order_map.get(r, {}).get("macrozone", "")
    )
    region = region.sort_values("region_order").reset_index(drop=True)

    render_section_title(t["fr_hist_section_parisi_region"])

    rows_html = ""
    for _, r in region.iterrows():
        change = r["change_pp"]
        signo = "+" if change >= 0 else ""
        color = COLOR_POSITIVE if change >= 0 else COLOR_NEGATIVE
        rows_html += (
            f"<tr>"
            f"<td style=\"font-weight:600; color:#333;\">{r['region_name']}</td>"
            f"<td style=\"color:#6b7280; font-size:9.5pt;\">{r['macrozone']}</td>"
            f"<td style=\"text-align:right; color:#666;\">{r['parisi_pct_2021']:.2f}%</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{r['parisi_pct_2025']:.2f}%</td>"
            f"<td style=\"text-align:right; color:{color};\">{signo}{change:.2f} pp</td>"
            f"<td style=\"text-align:right; color:#666;\">{signo}{r['pct_growth']:.1f}%</td>"
            f"</tr>"
        )

    html_region = _table_css("hr-tabla-parisi-region") + f"""
    <div class="hr-tabla-parisi-region">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_hist_th_region']}</th>
                    <th>{t['fr_hist_th_macrozone']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_2021']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_2025']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_delta_pp']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_delta_pct']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_region), unsafe_allow_html=True)
    _table_gap()

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px;\">"
        f"{t['fr_hist_note_parisi_region']}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION NO. 8 — PARISI: COMMUNES AND ABSORPTION
# ============================================================================
def _render_parisi_communes_absorption(df_2021, df_2025, t: dict) -> None:
    df_21 = _add_winner_columns(df_2021, "2021", t)
    df_25 = _add_winner_columns(df_2025, "2025", t)

    merge = df_21[[
        "commune_id", "commune_name", "region_name",
        "parisi_pct", "winner_2021", "winner_key_2021"
    ]].rename(columns={"parisi_pct": "parisi_pct_2021"}).merge(
        df_25[[
            "commune_id", "parisi_pct", "winner_2025", "winner_key_2025"
        ]].rename(columns={"parisi_pct": "parisi_pct_2025"}),
        on="commune_id",
        how="inner",
    )
    merge["parisi_change_pp"] = merge["parisi_pct_2025"] - merge["parisi_pct_2021"]

    labels_21 = _labels_2021(t)
    labels_25 = _labels_2025(t)

    def _tabla_top(df_sub, section_key):
        render_section_title(section_key)
        rows_html = ""
        for i, r in df_sub.iterrows():
            rank = i + 1
            color_21 = _color_for_key_2021(r["winner_key_2021"])
            color_25 = _color_for_key_2025(r["winner_key_2025"])
            label_21 = labels_21.get(r["winner_key_2021"], r["winner_key_2021"])
            label_25 = labels_25.get(r["winner_key_2025"], r["winner_key_2025"])
            change = r["parisi_change_pp"]
            signo = "+" if change >= 0 else ""
            color_cambio = COLOR_POSITIVE if change >= 0 else COLOR_NEGATIVE
            rows_html += (
                f"<tr>"
                f"<td style=\"color:#9a9a9a; text-align:center;\">{rank}</td>"
                f"<td style=\"font-weight:400; color:#333;\">{r['commune_name']}</td>"
                f"<td style=\"color:#6b7280; font-size:9.5pt;\">{r['region_name']}</td>"
                f"<td style=\"text-align:right; color:#666;\">{r['parisi_pct_2021']:.2f}%</td>"
                f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{r['parisi_pct_2025']:.2f}%</td>"
                f"<td style=\"text-align:right; color:{color_cambio};\">{signo}{change:.2f} pp</td>"
                f"<td style=\"color:#333;\"><span class=\"hr-color-box\" style=\"background:{color_21};\"></span>{label_21}</td>"
                f"<td style=\"color:#333;\"><span class=\"hr-color-box\" style=\"background:{color_25};\"></span>{label_25}</td>"
                f"</tr>"
            )

        html = _table_css("hr-tabla-parisi-top") + f"""
        <div class="hr-tabla-parisi-top">
            <table>
                <thead>
                    <tr>
                        <th style="text-align:center;">#</th>
                        <th>{t['fr_hist_th_comuna']}</th>
                        <th>{t['fr_hist_th_region_short']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_pct_2021']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_pct_2025']}</th>
                        <th style="text-align:right;">{t['fr_hist_th_delta_pp']}</th>
                        <th>{t['fr_hist_th_ganador_2021']}</th>
                        <th>{t['fr_hist_th_ganador_2025']}</th>
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

    top_inc = merge.nlargest(10, "parisi_change_pp").reset_index(drop=True)
    _tabla_top(top_inc, t["fr_hist_section_parisi_top_inc"])

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    top_dec = merge.nsmallest(10, "parisi_change_pp").reset_index(drop=True)
    _tabla_top(top_dec, t["fr_hist_section_parisi_top_dec"])

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px; line-height: 1.6;\">"
        f"{t['fr_hist_note_parisi_absorcion']}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    parisi_2025 = merge[merge["winner_key_2025"] == "parisi"].copy()
    captured = parisi_2025[parisi_2025["winner_key_2021"] != "parisi"].copy()

    if captured.empty:
        st.info(t["fr_hist_info_parisi_sin_absorcion"])
        return

    captured_agg = (
        captured.groupby("winner_key_2021")
        .size()
        .reset_index(name="comunas")
        .sort_values("comunas", ascending=False)
        .reset_index(drop=True)
    )
    total_captured = int(captured_agg["comunas"].sum())

    render_section_title(t["fr_hist_section_parisi_absorbente"])

    rows_abs_html = ""
    for _, r in captured_agg.iterrows():
        color = _color_for_key_2021(r["winner_key_2021"])
        label = labels_21.get(r["winner_key_2021"], r["winner_key_2021"])
        pct = (r["comunas"] / total_captured * 100) if total_captured else 0
        rows_abs_html += (
            f"<tr>"
            f"<td style=\"font-weight:400; color:#333;\">"
            f"<span class=\"hr-color-box\" style=\"background:{color};\"></span>{label}"
            f"</td>"
            f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{int(r['comunas'])}</td>"
            f"<td style=\"text-align:right; color:#666;\">{pct:.1f}%</td>"
            f"</tr>"
        )

    rows_abs_html += (
        f"<tr style=\"border-top:1px solid #e0e0e0;\">"
        f"<td style=\"font-weight:700; color:#111827;\">{t['fr_hist_th_comunas_capturadas']}</td>"
        f"<td style=\"text-align:right; font-weight:700; color:#111827;\">{total_captured}</td>"
        f"<td style=\"text-align:right; color:#666;\">100.0%</td>"
        f"</tr>"
    )

    html_abs = _table_css("hr-tabla-parisi-absorbente") + f"""
    <div class="hr-tabla-parisi-absorbente" style="max-width:620px;">
        <table>
            <thead>
                <tr>
                    <th>{t['fr_hist_th_ganador_2021']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_comunas_capturadas']}</th>
                    <th style="text-align:right;">{t['fr_hist_th_pct_del_total']}</th>
                </tr>
            </thead>
            <tbody>
                {rows_abs_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(_clean_html(html_abs), unsafe_allow_html=True)
    _table_gap()

    st.markdown(
        f"<div style=\"font-family: 'Liberation Sans', Arial, sans-serif; font-size: 10pt; color: #6b7280; margin-top: 10px;\">"
        f"{t['fr_hist_note_parisi_absorbente'].format(total=len(parisi_2025), capturadas=total_captured)}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# MAIN RENDER
# ============================================================================
def render(t: dict) -> None:
    render_view_title(t["fr_hist_view_title"])
    render_view_subtitle(t["fr_hist_view_subtitle"])

    try:
        with st.spinner(t["loading"]):
            df_2021 = load_fact_first_round_2021()
            df_2025 = load_fact_first_round_2025()

        _render_featured_cards(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_participacion"], expanded=False):
            _render_participation(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_bloques"], expanded=False):
            _render_blocks(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_realineamiento"], expanded=False):
            _render_realignment(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_cambios_agrupados"], expanded=False):
            _render_grouped_changes(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_contundentes"], expanded=False):
            _render_decisive_vs_close(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_fragmentacion"], expanded=False):
            _render_fragmentation(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_parisi_evolucion"], expanded=False):
            _render_parisi_evolution_territory(df_2021, df_2025, t)

        with st.expander(t["fr_hist_exp_parisi_absorcion"], expanded=False):
            _render_parisi_communes_absorption(df_2021, df_2025, t)

        _render_page_footer(t)

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
