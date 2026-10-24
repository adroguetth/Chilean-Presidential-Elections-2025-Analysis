"""
Layout Helpers and Reusable UI Components
============================================================================
Reusable UI pieces used across the dashboard: the main header (with language
selector) and the sub-navigation bar (tabs inside a page).

Both functions receive the translation dict `t` and use it for every visible
string. No user-facing text is hardcoded here.

Features
--------
- App header with title, subtitle, and language selector (ES/EN).
- Sub-navigation bar built with st.columns + st.button.
- Single-click tab switching: no double-click bug, no flicker.

Dependencies
------------
- Internal: none.
- External: streamlit.
- Downstream: app.py (render_header), pages/first_Round.py and
  pages/second_Round.py (render_sub_navigation).

Requirements
------------
- st.session_state must already contain "language" before render_header is
  called (initialized in app.py's init_session_state).

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st


# ============================================================================
# HEADER
# ============================================================================
def render_header(t: dict) -> None:
    """
    Render the dashboard header with the language selector.

    The header is split into two columns:
    - Left (3/4 width): country, app title, app subtitle.
    - Right (1/4 width): language selector (ES / EN).

    If the user changes the language, the new value is stored in
    st.session_state.language and st.rerun() is called so the whole app
    re-renders with the new translations.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"""
            <div style="font-size:13px;color:#888780;margin-bottom:2px;padding-top:2px;">{t['country']}</div>
            <div style="font-size:32px;font-weight:700;color:#1a1a18;line-height:1.2;margin-bottom:2px;">
                🗳️ {t['app_title']}
            </div>
            <div style="font-size:13px;color:#888780;margin-top:-2px;padding-bottom:2px;">{t['app_subtitle']}</div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        current_lang = st.session_state.language
        options = ["ES", "EN"]
        idx = options.index(current_lang)

        selected = st.selectbox(
            t["language"],
            options=options,
            index=idx,
            key="language_selector",
            label_visibility="collapsed",
        )

        if selected != current_lang:
            st.session_state.language = selected
            st.rerun()

    st.divider()


# ============================================================================
# SUB-NAVIGATION
# ============================================================================
def render_sub_navigation(t: dict, state_key: str, tabs: list) -> str:
    """
    Render the sub-navigation buttons and return the active tab.

    This function solves a classic Streamlit state bug: when the active tab is
    set *after* the button is rendered, the button and the content below it
    fall out of sync for one frame. The user sees a flicker and, sometimes,
    the content does not update on the first click (the famous "double-click"
    bug). The fix is to store the tab in st.session_state *inside* an
    on_click callback, which Streamlit executes BEFORE the rerun. That way,
    the button and the content are always computed from the same state in
    the same frame.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).
    state_key : str
        Key in st.session_state where the active tab is stored
        (e.g. "first_round_tab", "second_round_tab").
    tabs : list of tuple
        List of (tab_key, tab_label). tab_key is a stable identifier
        (never translated). tab_label is the visible text (already resolved
        by the caller, typically t["summary"], t["panorama"], etc.).

    Returns
    -------
    str
        The active tab_key after rendering.
    """
    if not tabs:
        return ""

    valid_keys = [k for k, _ in tabs]

    # Initialize state if it does not exist yet.
    if state_key not in st.session_state:
        st.session_state[state_key] = valid_keys[0]

    # Sanity check: if the stored tab no longer exists (old sessions that
    # still have "zones", "communal", etc.), fall back to the first tab.
    if st.session_state[state_key] not in valid_keys:
        st.session_state[state_key] = valid_keys[0]

    def _set_tab(tab_key: str) -> None:
        st.session_state[state_key] = tab_key

    cols = st.columns(len(tabs))
    current = st.session_state[state_key]

    for idx, (tab_key, tab_label) in enumerate(tabs):
        with cols[idx]:
            is_active = current == tab_key
            st.button(
                tab_label,
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"sub_nav_{state_key}_{tab_key}_{idx}",
                on_click=_set_tab,
                args=(tab_key,),
            )

    return st.session_state[state_key]
