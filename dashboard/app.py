"""
Main entry point for the Chilean Presidential Elections 2025 Dashboard.

Handles:
- Language selection (ES / EN)
- Main navigation (Summary, First Round, Second Round)
- Page routing
"""

import streamlit as st

from config.translations import LANG
from components.layout import render_header


def init_session_state():
    """Initialize session state variables."""
    if "language" not in st.session_state:
        st.session_state.language = "ES"
    if "page" not in st.session_state:
        st.session_state.page = "Summary"
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "macrozone": None,
            "region": None,
            "commune": None,
        }


def render_main_navigation(t: dict):
    """
    Render the main navigation buttons.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            t["summary"],
            use_container_width=True,
            type="primary" if st.session_state.page == "Summary" else "secondary",
        ):
            st.session_state.page = "Summary"
            st.rerun()

    with col2:
        if st.button(
            t["first_round"],
            use_container_width=True,
            type="primary" if st.session_state.page == "First Round" else "secondary",
        ):
            st.session_state.page = "First Round"
            st.rerun()

    with col3:
        if st.button(
            t["second_round"],
            use_container_width=True,
            type="primary" if st.session_state.page == "Second Round" else "secondary",
        ):
            st.session_state.page = "Second Round"
            st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Chile Elections 2025",
        page_icon="🗳️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_session_state()

    # Get current language
    lang = st.session_state.language
    t = LANG[lang]

    # Render header with language selector
    render_header(t)

    # Render main navigation
    render_main_navigation(t)

    # Page routing
    if st.session_state.page == "Summary":
        from pages import 1_Summary as summary_page
        summary_page.render(t)

    elif st.session_state.page == "First Round":
        from pages import 2_First_Round as first_round_page
        first_round_page.render(t)

    elif st.session_state.page == "Second Round":
        from pages import 3_Second_Round as second_round_page
        second_round_page.render(t)

    else:
        st.warning(t["no_data"])


if __name__ == "__main__":
    main()
