"""
Second Round page — Parent view with sub-navigation.
"""

import streamlit as st

from components.layout import render_sub_navigation


def render(t: dict):
    """
    Render the Second Round page.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language.
    """
    st.title(t["second_round"])

    # Sub-navigation tabs
    tabs = [
        ("summary", t["summary"]),
        ("zones", t["zones"]),
        ("communal", t["communal"]),
        ("null_blank", t["null_blank"]),
        ("transfers", t["transfers"]),
        ("historical", t["historical"]),
    ]

    # Initialize or get current tab
    if "second_round_tab" not in st.session_state:
        st.session_state.second_round_tab = "summary"

    selected_tab = render_sub_navigation(t, st.session_state.second_round_tab, tabs)
    st.session_state.second_round_tab = selected_tab

    # Render selected view
    if selected_tab == "summary":
        from views.second_round.summary import render as render_summary
        render_summary(t)
    elif selected_tab == "zones":
        from views.second_round.zones import render as render_zones
        render_zones(t)
    elif selected_tab == "communal":
        from views.second_round.communal import render as render_communal
        render_communal(t)
    elif selected_tab == "null_blank":
        from views.second_round.null_blank import render as render_null_blank
        render_null_blank(t)
    elif selected_tab == "transfers":
        from views.second_round.transfers import render as render_transfers
        render_transfers(t)
    elif selected_tab == "historical":
        from views.second_round.historical import render as render_historical
        render_historical(t)
