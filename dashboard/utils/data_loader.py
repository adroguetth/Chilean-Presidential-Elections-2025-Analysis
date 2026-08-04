"""
Data loading from SQLite database with caching.
"""

import os
import sqlite3
import urllib.request
from typing import Optional

import pandas as pd
import streamlit as st

from config.constants import DB_URL, DB_LOCAL_PATH


@st.cache_data(ttl=3600)
def load_database() -> sqlite3.Connection:
    """
    Download SQLite database from GitHub and return a read-only connection.

    The database is cached locally. If the file already exists, it is reused.
    The connection is read-only to prevent accidental modifications.

    Returns
    -------
    sqlite3.Connection
        Read-only connection to the SQLite database.
    """
    if not os.path.exists(DB_LOCAL_PATH):
        print(f"Downloading database from {DB_URL}...")
        urllib.request.urlretrieve(DB_URL, DB_LOCAL_PATH)
        print(f"Download complete: {DB_LOCAL_PATH}")

    conn = sqlite3.connect(f"file:{DB_LOCAL_PATH}?mode=ro", uri=True)
    return conn


@st.cache_data(ttl=3600)
def load_dim_commune() -> pd.DataFrame:
    """
    Load the commune dimension table.

    Returns
    -------
    pd.DataFrame
        dim_commune table with commune_id, commune_name, region_name, etc.
    """
    conn = load_database()
    df = pd.read_sql("SELECT * FROM dim_commune;", conn)
    conn.close()
    return df


@st.cache_data(ttl=3600)
def load_fact_first_round_2025() -> pd.DataFrame:
    """
    Load first round 2025 fact table and join with dim_commune.

    Returns
    -------
    pd.DataFrame
        Fact table with geographic attributes (region, macrozone, commune_name).
    """
    conn = load_database()
    df = pd.read_sql("SELECT * FROM fact_first_round_2025;", conn)
    dim = load_dim_commune()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    conn.close()
    return df


@st.cache_data(ttl=3600)
def load_fact_second_round_2025() -> pd.DataFrame:
    """
    Load second round 2025 fact table and join with dim_commune.

    Returns
    -------
    pd.DataFrame
        Fact table with geographic attributes (region, macrozone, commune_name).
    """
    conn = load_database()
    df = pd.read_sql("SELECT * FROM fact_second_round_2025;", conn)
    dim = load_dim_commune()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    conn.close()
    return df


@st.cache_data(ttl=3600)
def load_fact_first_round_2021() -> pd.DataFrame:
    """
    Load first round 2021 fact table and join with dim_commune.
    """
    conn = load_database()
    df = pd.read_sql("SELECT * FROM fact_first_round_2021;", conn)
    dim = load_dim_commune()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    conn.close()
    return df


@st.cache_data(ttl=3600)
def load_fact_second_round_2021() -> pd.DataFrame:
    """
    Load second round 2021 fact table and join with dim_commune.
    """
    conn = load_database()
    df = pd.read_sql("SELECT * FROM fact_second_round_2021;", conn)
    dim = load_dim_commune()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    conn.close()
    return df
