"""
Data loading from SQLite database with caching.
"""

import os
import sqlite3
import urllib.request

import pandas as pd
import streamlit as st

from config.constants import DB_URL, DB_LOCAL_PATH


def get_db_connection() -> sqlite3.Connection:
    """
    Get a read-only connection to the SQLite database.
    Downloads the database if it doesn't exist locally.
    """
    if not os.path.exists(DB_LOCAL_PATH):
        print(f"Downloading database from {DB_URL}...")
        urllib.request.urlretrieve(DB_URL, DB_LOCAL_PATH)
        print(f"Download complete: {DB_LOCAL_PATH}")

    conn = sqlite3.connect(f"file:{DB_LOCAL_PATH}?mode=ro", uri=True)
    return conn


@st.cache_data
def load_dim_commune() -> pd.DataFrame:
    """
    Load the commune dimension table.
    """
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM dim_commune;", conn)
    conn.close()
    return df


@st.cache_data
def load_fact_first_round_2025() -> pd.DataFrame:
    """
    Load first round 2025 fact table and join with dim_commune.
    """
    dim = load_dim_commune()
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM fact_first_round_2025;", conn)
    conn.close()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    return df


@st.cache_data
def load_fact_second_round_2025() -> pd.DataFrame:
    """
    Load second round 2025 fact table and join with dim_commune.
    """
    dim = load_dim_commune()
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM fact_second_round_2025;", conn)
    conn.close()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    return df


@st.cache_data
def load_fact_first_round_2021() -> pd.DataFrame:
    """
    Load first round 2021 fact table and join with dim_commune.
    """
    dim = load_dim_commune()
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM fact_first_round_2021;", conn)
    conn.close()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    return df


@st.cache_data
def load_fact_second_round_2021() -> pd.DataFrame:
    """
    Load second round 2021 fact table and join with dim_commune.
    """
    dim = load_dim_commune()
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM fact_second_round_2021;", conn)
    conn.close()

    cols = [
        "commune_id", "commune_name", "region_code", "region_name",
        "region_order", "macrozone", "macrozone_order", "province",
    ]
    df = df.merge(dim[cols], on="commune_id", how="left")
    return df
