"""
Data Loading
============================================================================
Load data from a local SQLite database with Streamlit caching.

The database is downloaded on first run if it does not exist locally. All
public loaders are cached to avoid re-reading the database on every Streamlit
rerun, which is expensive and unnecessary since the underlying data does not
change during a session.

Features
--------
- Read-only SQLite connection.
- Automatic download of the database on first run.
- Cached loaders for the commune dimension and all fact tables.
- Automatic merge of fact tables with the commune dimension.

Dependencies
------------
- Internal: config.constants (DB_URL, DB_LOCAL_PATH).
- External: os, sqlite3, urllib.request, pandas, streamlit.
- Downstream: all views, pages, and components that need vote data.

Requirements
------------
- Internet access on first run (to download the database).
- Write access to the directory containing DB_LOCAL_PATH.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import os
import sqlite3
import urllib.request

import pandas as pd
import streamlit as st

from config.constants import DB_URL, DB_LOCAL_PATH


# ============================================================================
# DATABASE CONNECTION
# ============================================================================
def get_db_connection() -> sqlite3.Connection:
    """
    Get a read-only connection to the SQLite database.

    Downloads the database from DB_URL if it does not exist locally. The
    connection is opened in read-only mode to prevent accidental writes.

    Returns
    -------
    sqlite3.Connection
        Read-only connection to the SQLite database.
    """
    if not os.path.exists(DB_LOCAL_PATH):
        print(f"Downloading database from {DB_URL}...")
        urllib.request.urlretrieve(DB_URL, DB_LOCAL_PATH)
        print(f"Download complete: {DB_LOCAL_PATH}")

    # Read-only mode: prevents accidental writes from the dashboard
    conn = sqlite3.connect(f"file:{DB_LOCAL_PATH}?mode=ro", uri=True)
    return conn


# ============================================================================
# DIMENSION COLUMNS
# ============================================================================
# Columns of dim_commune that are merged into every fact table.
# These are data identifiers (column names from the database), not translatable.
_DIM_COLS = [
    "commune_id", "commune_name", "region_code", "region_name",
    "region_order", "macrozone", "macrozone_order", "province",
]


# ============================================================================
# DIMENSION TABLE
# ============================================================================
@st.cache_data
# Cached: the dim_commune table does not change during a session.
def load_dim_commune() -> pd.DataFrame:
    """
    Load the commune dimension table.

    Returns
    -------
    pd.DataFrame
        Full dim_commune table.
    """
    conn = get_db_connection()
    try:
        df = pd.read_sql("SELECT * FROM dim_commune;", conn)
    finally:
        conn.close()
    return df


# ============================================================================
# FACT TABLES
# ============================================================================
def _load_fact_table(table_name: str) -> pd.DataFrame:
    """
    Load a fact table and merge it with the commune dimension.

    Parameters
    ----------
    table_name : str
        Name of the fact table in the SQLite database.

    Returns
    -------
    pd.DataFrame
        Fact table merged with dim_commune columns on commune_id.

    Notes
    -----
    This function is not cached directly. Each public loader below wraps it
    with @st.cache_data, so the cache is keyed by the specific table.
    """
    dim = load_dim_commune()
    conn = get_db_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name};", conn)
    finally:
        conn.close()
    return df.merge(dim[_DIM_COLS], on="commune_id", how="left")


@st.cache_data
# Cached: the fact table does not change during a session.
def load_fact_first_round_2025() -> pd.DataFrame:
    """
    Load the 2025 first round fact table and join with dim_commune.

    Returns
    -------
    pd.DataFrame
        Fact table merged with commune dimension columns.
    """
    return _load_fact_table("fact_first_round_2025")


@st.cache_data
# Cached: the fact table does not change during a session.
def load_fact_second_round_2025() -> pd.DataFrame:
    """
    Load the 2025 second round fact table and join with dim_commune.

    Returns
    -------
    pd.DataFrame
        Fact table merged with commune dimension columns.
    """
    return _load_fact_table("fact_second_round_2025")


@st.cache_data
# Cached: the fact table does not change during a session.
def load_fact_first_round_2021() -> pd.DataFrame:
    """
    Load the 2021 first round fact table and join with dim_commune.

    Returns
    -------
    pd.DataFrame
        Fact table merged with commune dimension columns.
    """
    return _load_fact_table("fact_first_round_2021")


@st.cache_data
# Cached: the fact table does not change during a session.
def load_fact_second_round_2021() -> pd.DataFrame:
    """
    Load the 2021 second round fact table and join with dim_commune.

    Returns
    -------
    pd.DataFrame
        Fact table merged with commune dimension columns.
    """
    return _load_fact_table("fact_second_round_2021")
