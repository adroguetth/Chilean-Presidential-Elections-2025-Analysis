"""
Summary page — Static overview with no filters.
"""

import streamlit as st


def render(t: dict):
    """
    Render the Summary page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language.
    """
    st.title(t["summary_title"])

    st.info("📊 Summary page coming soon...")

    # TODO: Implement Summary page using:
    # - utils.data_loader.load_fact_first_round_2025()
    # - utils.data_loader.load_fact_second_round_2025()
    # - utils.calculations.compute_vote_metrics()
    # - utils.calculations.compute_first_round_results()
    # - components.charts.render_second_round_chart()
    # - components.tables.render_first_round_table()
