"""
Custom CSS Theme
============================================================================
Global CSS injected into the Streamlit app.

This module contains a single CSS string (CUSTOM_CSS) and a function to
inject it into the app (inject_custom_css). The CSS defines the global
background, typography, button styles, metric cards, and a few Streamlit
overrides (hide the default menu and footer).

The CSS itself is not processed by Python. It is passed verbatim to
st.markdown with unsafe_allow_html=True.

Features
--------
- Global background and font family.
- Transparent containers for columns.
- Custom navigation button styles.
- Custom dividers.
- Custom metric cards.
- Hide Streamlit's default menu and footer.

Dependencies
------------
- Internal: none.
- External: streamlit.
- Downstream: app.py (calls inject_custom_css on startup).

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st


# ============================================================================
# CUSTOM CSS
# ============================================================================
CUSTOM_CSS = """
<style>
/* ---------- Global background ---------- */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background-color: #F7F7F2 !important;
}
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.block-container {
    max-width: 1100px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    background-color: #F7F7F2 !important;
}

/* ---------- Remove automatic containers around columns ---------- */
div[data-testid="stHorizontalBlock"],
div[data-testid="stColumn"],
div[data-testid="stElementContainer"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ---------- Navigation buttons ---------- */
div[data-testid="stButton"] > button {
    background-color: #ffffff;
    border: 1px solid #E0DED8;
    border-radius: 7px;
    padding: 0.25rem 0.65rem;
    min-height: 0;
    font-size: 12px;
    font-weight: 500;
    color: #888780;
    box-shadow: none;
    line-height: 1.4;
    transition: 0.15s;
}
div[data-testid="stButton"] > button p {
    font-size: 12px;
}
div[data-testid="stButton"] > button:hover {
    background-color: #f0efec;
    border-color: #c0bdb5;
    color: #1a1a18;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background-color: #1a1a18;
    border-color: #1a1a18;
    color: #ffffff;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background-color: #2a2a26;
}

/* ---------- Dividers ---------- */
hr {
    border: none !important;
    border-top: 1px solid #E0DED8 !important;
    margin: 0.75rem 0 !important;
    opacity: 1 !important;
}

/* ---------- Metric cards ---------- */
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #E0DED8;
    border-radius: 10px;
    padding: 0.7rem 1rem;
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: .04em;
    color: #888780 !important;
}
[data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: #1a1a18 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 11px !important;
}

/* ---------- Plotly charts ---------- */
div[data-testid="stPlotlyChart"] {
    background: transparent;
    border-radius: 8px;
    overflow: hidden;
}

/* ---------- Hide default Streamlit elements ---------- */
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {
    display: none;
}
</style>
"""


# ============================================================================
# INJECTION
# ============================================================================
def inject_custom_css():
    """Inject the custom CSS into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
