"""
Summary page — Static overview with no filters.
"""

import streamlit as st

from utils.data_loader import (
    load_fact_first_round_2025,
    load_fact_second_round_2025,
)
from utils.calculations import (
    compute_vote_metrics,
    compute_second_round_results,
    compute_first_round_results,
    compute_round_comparison,
)
from config.constants import PADRON_ELECTORAL_2025
from components.metrics import render_metric_cards
from components.charts import render_second_round_chart
from components.tables import render_first_round_table


def render(t: dict):
    """
    Render the Summary page.
    """
    st.markdown(
        f"""<h1 style='font-size:28px;font-weight:700;color:#1a1a18;margin-bottom:0.2rem;'>{t['summary_title']}</h1>
        <h2 style='font-size:22px;font-weight:600;color:#1a1a18;margin-top:0;margin-bottom:0.5rem;'>{t['second_round_title']}</h2>""",
        unsafe_allow_html=True,
    )

    try:
        df_fr_2025_raw = load_fact_first_round_2025()
        df_sr_2025_raw = load_fact_second_round_2025()

        sr_metrics = compute_vote_metrics(df_sr_2025_raw, padron=PADRON_ELECTORAL_2025)
        comparison = compute_round_comparison(df_sr_2025_raw, df_fr_2025_raw)

        def _signed(value: float) -> str:
            return f"+{value:.2f}" if value >= 0 else f"{value:.2f}"

        sr_deltas = {
            "casted": (f"{sr_metrics['casted_pct_padron']:.2f}% del padrón electoral", "down"),
            "valid": (f"{_signed(comparison['valid_pct_diff'])} pp vs 1ª vuelta", "normal"),
            "null": (f"{_signed(comparison['null_pct_diff'])} pp vs 1ª vuelta", "inverse"),
            "blank": (f"{_signed(comparison['blank_pct_diff'])} pp vs 1ª vuelta", "inverse"),
        }
        render_metric_cards(sr_metrics, t, deltas=sr_deltas)

        sr_results = compute_second_round_results(df_sr_2025_raw)
        render_second_round_chart(sr_results, t)

        st.divider()

        # FIRST ROUND
        st.markdown(
            f"<h2 style='font-size:22px;font-weight:600;color:#1a1a18;margin-top:0.5rem;margin-bottom:0.5rem;'>{t['first_round_title']}</h2>",
            unsafe_allow_html=True,
        )

        fr_metrics = compute_vote_metrics(df_fr_2025_raw, padron=PADRON_ELECTORAL_2025)
        fr_deltas = {
            "casted": (f"{fr_metrics['casted_pct_padron']:.2f}% del padrón electoral", "neutral"),
            "valid": (f"{fr_metrics['valid_pct']:.2f}% del total", "neutral"),
        }
        render_metric_cards(fr_metrics, t, deltas=fr_deltas)

        fr_results = compute_first_round_results(df_fr_2025_raw)
        render_first_round_table(fr_results, t)

        # FOOTER
        st.divider()
        st.markdown(
            f"<div style='text-align:center;font-size:12px;color:#888780;padding:0.5rem 0;'>{t['data_source']} · {t['data_source_note']}</div>",
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
