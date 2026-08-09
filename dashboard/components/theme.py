"""
Custom CSS for the dashboard.
"""

import streamlit as st

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


def inject_custom_css():
    """Inject the custom CSS into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
