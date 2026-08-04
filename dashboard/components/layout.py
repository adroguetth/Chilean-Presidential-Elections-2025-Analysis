"""
Layout helpers and reusable UI components.
"""

import streamlit as st

from config.translations import LANG


def render_header(t: dict):
    """
    Render the dashboard header with language selector.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language.
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title(t["app_title"])
        st.caption(t["app_subtitle"])

    with col2:
        current_lang = st.session_state.language
        options = ["ES", "EN"]
        idx = options.index(current_lang)

        selected = st.selectbox(
            t["language"],
            options=options,
            index=idx,
            key="language_selector",
        )

        if selected != current_lang:
            st.session_state.language = selected
            st.rerun()

    st.divider()


def render_sub_navigation(t: dict, current_tab: str, tabs: list):
    """
    Render sub-navigation tabs for First/Second Round pages.

    Parameters
    ----------
    t : dict
        Translation dictionary.
    current_tab : str
        Currently active tab key.
    tabs : list
        List of tab keys and labels, e.g., [("summary", "Summary"), ("zones", "Zones")]

    Returns
    -------
    str
        The key of the selected tab.
    """
    cols = st.columns(len(tabs))

    for col, (tab_key, tab_label) in zip(cols, tabs):
        with col:
            is_active = current_tab == tab_key
            if st.button(
                tab_label,
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                return tab_key

    return current_tab
