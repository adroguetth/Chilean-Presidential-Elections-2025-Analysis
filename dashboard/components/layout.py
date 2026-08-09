"""
Layout helpers and reusable UI components.
"""

import streamlit as st


def render_header(t: dict):
    """
    Render the dashboard header with language selector.
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


def render_sub_navigation(t: dict, current_tab: str, tabs: list):
    """
    Render sub-navigation tabs with unique keys for each button.
    """
    cols = st.columns(len(tabs))

    for idx, (tab_key, tab_label) in enumerate(tabs):
        with cols[idx]:
            is_active = current_tab == tab_key
            # 🔧 Agregar key única basada en el índice
            if st.button(
                tab_label,
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"sub_nav_{tab_key}_{idx}",  # ← CLAVE ÚNICA
            ):
                return tab_key

    return current_tab
