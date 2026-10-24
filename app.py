"""
Main Entry Point
============================================================================
Orchestrator for the Chilean Presidential Elections 2025 dashboard. Handles
session state initialization, page configuration, CSS injection, header
rendering, main navigation, and page dispatch.

This module is the only entry point of the Streamlit app. It does NOT
contain any rendering logic beyond the main navigation buttons: all views
live under pages/, components/, and views/, and are dispatched dynamically
based on the current session_state.page.

Features
--------
- Session state initialization (language, page, filters).
- Streamlit page configuration (title, icon, layout).
- Custom CSS injection.
- Header rendering (language selector, app title, subtitle).
- Main navigation (Summary / First Round / Second Round).
- Dynamic page dispatch with ImportError handling.

Dependencies
------------
- Internal: config.translations (LANG), components.layout (render_header),
  components.theme (inject_custom_css).
- External: streamlit, sys, os.
- Downstream: none (this is the entry point).

Requirements
------------
- None.

Notes
-----
- The `sys.path.insert` at the top is required so that `python app.py` works
  from any directory. `streamlit run app.py` also works without it, but the
  insert is kept for consistency with direct execution.
- Session state keys (`language`, `page`, `filters`, `macrozone`, `region`,
  `commune`) and page values (`"Summary"`, `"First Round"`, `"Second Round"`)
  are internal identifiers and are NOT translated.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.translations import LANG
from components.layout import render_header
from components.theme import inject_custom_css


# ============================================================================
# SESSION STATE
# ============================================================================
def init_session_state() -> None:
    """
    Initialize the session state with default values.

    Sets:
        - language: current language code ("ES" by default).
        - page: current page ("Summary" by default).
        - filters: dict with initial empty filters.

    Returns
    -------
    None
    """
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


# ============================================================================
# MAIN NAVIGATION
# ============================================================================
def render_main_navigation(t: dict) -> None:
    """
    Render the main navigation buttons (Summary / First Round / Second Round).

    Each button sets st.session_state.page and triggers a rerun. The active
    button is rendered as primary; the others as secondary.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
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


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    """
    Entry point of the app. Initializes the session state, configures the
    page, injects CSS, renders the header and navigation, and dispatches to
    the current page.

    Page dispatch is done via dynamic imports so that a missing or broken
    page does not crash the whole app: only the error message is shown.

    Returns
    -------
    None
    """
    init_session_state()
    lang = st.session_state.language
    t = LANG[lang]

    st.set_page_config(
        page_title=t["page_title"],
        page_icon="🗳️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_custom_css()

    render_header(t)
    render_main_navigation(t)

    try:
        if st.session_state.page == "Summary":
            from pages.summary import render as render_summary
            render_summary(t)

        elif st.session_state.page == "First Round":
            from pages.first_Round import render as render_first_round
            render_first_round(t)

        elif st.session_state.page == "Second Round":
            from pages.second_Round import render as render_second_round
            render_second_round(t)

        else:
            st.warning(t["no_data"])

    except ImportError as e:
        st.error(f"{t['error_importing_page']}: {e}")
        st.exception(e)


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
