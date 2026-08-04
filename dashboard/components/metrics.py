"""
Reusable metric card components.
"""

import streamlit as st


def render_metric_cards(metrics: dict, t: dict, key_prefix: str = ""):
    """
    Render four metric cards in a row.

    Parameters
    ----------
    metrics : dict
        Dictionary with casted_votes, valid_votes, null_votes, blank_votes,
        casted_pct, valid_pct, null_pct, blank_pct.
    t : dict
        Translation dictionary.
    key_prefix : str
        Prefix for Streamlit component keys (for uniqueness).
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=t["casted_votes"],
            value=f"{metrics['casted_votes']:,}",
            delta=f"{metrics['casted_pct']:.2f}%",
            key=f"{key_prefix}_casted",
        )

    with col2:
        st.metric(
            label=t["valid_votes"],
            value=f"{metrics['valid_votes']:,}",
            delta=f"{metrics['valid_pct']:.2f}% del total",
            key=f"{key_prefix}_valid",
        )

    with col3:
        st.metric(
            label=t["null_votes"],
            value=f"{metrics['null_votes']:,}",
            delta=f"{metrics['null_pct']:.2f}% del total",
            key=f"{key_prefix}_null",
            delta_color="inverse",
        )

    with col4:
        st.metric(
            label=t["blank_votes"],
            value=f"{metrics['blank_votes']:,}",
            delta=f"{metrics['blank_pct']:.2f}% del total",
            key=f"{key_prefix}_blank",
            delta_color="inverse",
        )
