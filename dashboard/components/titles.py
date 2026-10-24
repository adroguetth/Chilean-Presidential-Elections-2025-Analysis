"""
Title Rendering Helpers
============================================================================
Unified title formats for the dashboard.

This module centralizes every title level used across the app: app title,
page title, view title, view subtitle, section title, and section subtitle.
Each function injects a styled HTML block via st.markdown with a fixed
hierarchy (size, weight, color) so views never re-implement title styles.

The actual text is passed as an argument by the caller. This module does not
hardcode any visible string and does not use translations (t) directly.

Features
--------
- Six title levels with fixed visual hierarchy.
- HTML is passed through _clean_html to avoid Markdown code blocks.
- Consistent font family across all levels.

Dependencies
------------
- Internal: utils.html_helpers (clean_html).
- External: streamlit.
- Downstream: all views and pages.

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st

from utils.html_helpers import clean_html as _clean_html


# ============================================================================
# CONSTANTS
# ============================================================================
FONT_FAMILY = "'Liberation Sans', Arial, sans-serif"


# ============================================================================
# APP TITLE
# ============================================================================
def render_app_title(text: str) -> None:
    """
    Render the app title.

    32px, #1a1a18, weight 700. Used once at the top of the app.

    Parameters
    ----------
    text : str
        Title text (already resolved by the caller, typically t["app_title"]).

    Returns
    -------
    None
    """
    st.markdown(
        _clean_html(f"""
        <div style="font-family: {FONT_FAMILY};
                    font-size: 32px;
                    font-weight: 700;
                    color: #1a1a18;
                    line-height: 1.2;
                    margin-bottom: 2px;">
            {text}
        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================================
# PAGE TITLE
# ============================================================================
def render_page_title(text: str) -> None:
    """
    Render a parent page title (First Round, Second Round, Executive Summary).

    28px, #1a1a18, weight 700. Used in pages/*.py.

    Parameters
    ----------
    text : str
        Title text (already resolved by the caller).

    Returns
    -------
    None
    """
    st.markdown(
        _clean_html(f"""
        <div style="font-family: {FONT_FAMILY};
                    font-size: 28px;
                    font-weight: 700;
                    color: #1a1a18;
                    line-height: 1.2;
                    margin-top: 0;
                    margin-bottom: 1.2rem;">
            {text}
        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================================
# VIEW TITLE
# ============================================================================
def render_view_title(text: str) -> None:
    """
    Render a view title.

    16.5pt, #111827, weight 700. Used in views/**/*.py.

    Parameters
    ----------
    text : str
        Title text (already resolved by the caller).

    Returns
    -------
    None
    """
    st.markdown(
        _clean_html(f"""
        <div style="font-family: {FONT_FAMILY};
                    font-size: 16.5pt;
                    font-weight: 700;
                    color: #111827;
                    margin-top: 16px;
                    margin-bottom: 8px;">
            {text}
        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================================
# VIEW SUBTITLE
# ============================================================================
def render_view_subtitle(text: str) -> None:
    """
    Render a view subtitle.

    9.5pt, #6b7280. Used right below a view title.

    Parameters
    ----------
    text : str
        Subtitle text (already resolved by the caller).

    Returns
    -------
    None
    """
    st.markdown(
        _clean_html(f"""
        <div style="font-family: {FONT_FAMILY};
                    font-size: 9.5pt;
                    color: #6b7280;
                    margin-bottom: 16px;">
            {text}
        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION TITLE
# ============================================================================
def render_section_title(text: str) -> None:
    """
    Render a section title.

    12pt, #111827, weight 700. Used for internal section headers.

    Parameters
    ----------
    text : str
        Title text (already resolved by the caller).

    Returns
    -------
    None
    """
    st.markdown(
        _clean_html(f"""
        <div style="font-family: {FONT_FAMILY};
                    font-size: 12pt;
                    font-weight: 700;
                    color: #111827;
                    margin-top: 12px;
                    margin-bottom: 6px;">
            {text}
        </div>
        """),
        unsafe_allow_html=True,
    )


# ============================================================================
# SECTION SUBTITLE
# ============================================================================
def render_section_subtitle(text: str) -> None:
    """
    Render a section subtitle.

    10pt, #6b7280. Used right below a section title.

    Parameters
    ----------
    text : str
        Subtitle text (already resolved by the caller).

    Returns
    -------
    None
    """
    st.markdown(
        _clean_html(f"""
        <div style="font-family: {FONT_FAMILY};
                    font-size: 10pt;
                    color: #6b7280;
                    margin-bottom: 16px;">
            {text}
        </div>
        """),
        unsafe_allow_html=True,
    )
