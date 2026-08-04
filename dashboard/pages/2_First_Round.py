"""
First Round page — Parent view with sub-navigation.
"""

import streamlit as st

from components.layout import render_sub_navigation


def render(t: dict):
    """
    Render the First Round page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language.
    """
    st.title(t["first_round"])

    # Sub-navigation tabs
    tabs = [
        ("summary", t["summary"]),
        ("zones", t["zones"]),
        ("communal", t["communal"]),
        ("null_blank", t["null_blank"]),
        ("transfers", t["transfers"]),
    ]

    # Initialize or get current tab
    if "first_round_tab" not in st.session_state:
        st.session_state.first_round_tab = "summary"

    selected_tab = render_sub_navigation(t, st.session_state.first_round_tab, tabs)
    st.session_state.first_round_tab = selected_tab

    # Render selected view
    if selected_tab == "summary":
        from views.first_round.summary import render as render_summary
        render_summary(t)
    elif selected_tab == "zones":
        from views.first_round.zones import render as render_zones
        render_zones(t)
    elif selected_tab == "communal":
        from views.first_round.communal import render as render_communal
        render_communal(t)
    elif selected_tab == "null_blank":
        from views.first_round.null_blank import render as render_null_blank
        render_null_blank(t)
    elif selected_tab == "transfers":
        from views.first_round.transfers import render as render_transfers
        render_transfers(t)
