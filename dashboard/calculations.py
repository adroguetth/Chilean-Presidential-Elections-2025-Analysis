"""
Core Vote Calculations
============================================================================
Pure calculation functions for vote metrics, round comparisons, and
per-candidate results. No Streamlit, no UI, no translations.

All functions operate on raw DataFrames loaded from the database and return
plain dicts or DataFrames. This makes them testable in isolation and reusable
from any view.

Features
--------
- National vote metrics (casted, valid, null, blank).
- Round-to-round comparison in percentage points.
- Second-round results (Jara vs Kast).
- First-round results per candidate (ranked by votes).
- Integer formatting with Chilean thousands separator.

Dependencies
------------
- Internal: config.constants (CANDIDATES_2025).
- External: pandas.
- Downstream: pages/*, views/*, components/charts.

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import pandas as pd

from config.constants import CANDIDATES_2025


# ============================================================================
# NATIONAL VOTE METRICS
# ============================================================================
def compute_vote_metrics(df_raw: pd.DataFrame, padron: int = None) -> dict:
    """
    Calculate national vote metrics from a fact table.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Fact table with columns: casted_votes, null_votes, blank_votes.
    padron : int, optional
        Electoral roll size (Chilean: "padrón electoral", equivalent to
        electoral_roll). If provided, adds the casted_pct_padron metric.

    Returns
    -------
    dict
        Metrics: casted_votes, valid_votes, null_votes, blank_votes,
        casted_pct, valid_pct, null_pct, blank_pct. If `padron` is provided,
        also includes casted_pct_padron.
    """
    casted_votes = int(df_raw["casted_votes"].sum())
    null_votes = int(df_raw["null_votes"].sum())
    blank_votes = int(df_raw["blank_votes"].sum())
    valid_votes = casted_votes - null_votes - blank_votes

    metrics = {
        "casted_votes": casted_votes,
        "valid_votes": valid_votes,
        "null_votes": null_votes,
        "blank_votes": blank_votes,
        "casted_pct": 100.0,
        "valid_pct": (valid_votes / casted_votes * 100) if casted_votes else 0.0,
        "null_pct": (null_votes / casted_votes * 100) if casted_votes else 0.0,
        "blank_pct": (blank_votes / casted_votes * 100) if casted_votes else 0.0,
    }

    if padron:
        metrics["casted_pct_padron"] = (casted_votes / padron * 100) if padron else 0.0

    return metrics


# ============================================================================
# ROUND COMPARISON
# ============================================================================
def compute_round_comparison(df_current_raw: pd.DataFrame, df_previous_raw: pd.DataFrame) -> dict:
    """
    Compare vote percentages between two rounds (in percentage points).

    Parameters
    ----------
    df_current_raw : pd.DataFrame
        Current round fact table.
    df_previous_raw : pd.DataFrame
        Previous round fact table.

    Returns
    -------
    dict
        Differences in percentage points: valid_pct_diff, null_pct_diff,
        blank_pct_diff.
    """
    current = compute_vote_metrics(df_current_raw)
    previous = compute_vote_metrics(df_previous_raw)

    return {
        "valid_pct_diff": current["valid_pct"] - previous["valid_pct"],
        "null_pct_diff": current["null_pct"] - previous["null_pct"],
        "blank_pct_diff": current["blank_pct"] - previous["blank_pct"],
    }


# ============================================================================
# SECOND ROUND RESULTS
# ============================================================================
def compute_second_round_results(df_raw: pd.DataFrame) -> dict:
    """
    Calculate second round results (Jara vs Kast).

    Parameters
    ----------
    df_raw : pd.DataFrame
        Fact table with columns: jara_votes, kast_votes.

    Returns
    -------
    dict
        jara_votes, kast_votes, jara_pct, kast_pct, diff_votes, diff_pct,
        winner (candidate name).
    """
    jara_votes = int(df_raw["jara_votes"].sum())
    kast_votes = int(df_raw["kast_votes"].sum())
    total_valid = jara_votes + kast_votes

    jara_pct = (jara_votes / total_valid * 100) if total_valid else 0.0
    kast_pct = (kast_votes / total_valid * 100) if total_valid else 0.0

    diff_votes = kast_votes - jara_votes
    diff_pct = kast_pct - jara_pct

    winner = "José Antonio Kast" if kast_votes > jara_votes else "Jeannette Jara"

    return {
        "jara_votes": jara_votes,
        "kast_votes": kast_votes,
        "jara_pct": jara_pct,
        "kast_pct": kast_pct,
        "diff_votes": diff_votes,
        "diff_pct": diff_pct,
        "winner": winner,
    }


# ============================================================================
# FIRST ROUND RESULTS PER CANDIDATE
# ============================================================================
def compute_first_round_results(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate first round results by candidate, ranked by votes.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Fact table with one column per candidate (see CANDIDATES_2025).

    Returns
    -------
    pd.DataFrame
        Columns: candidate_name, party, votes, pct, color, short_name,
        status ("passes_to_runoff" / "does_not_pass"). Rows ranked by votes.
    """
    casted_votes = int(df_raw["casted_votes"].sum())
    null_votes = int(df_raw["null_votes"].sum())
    blank_votes = int(df_raw["blank_votes"].sum())
    valid_votes = casted_votes - null_votes - blank_votes

    results = []
    for name, meta in CANDIDATES_2025.items():
        votes = int(df_raw[meta["column"]].sum())
        pct = (votes / valid_votes * 100) if valid_votes else 0.0
        results.append({
            "candidate_name": name,
            "party": meta["party"],
            "votes": votes,
            "pct": pct,
            "color": meta["color"],
            "short_name": meta["short_name"],
        })

    results_ranked = sorted(results, key=lambda x: x["votes"], reverse=True)

    for i, row in enumerate(results_ranked):
        row["status"] = "passes_to_runoff" if i < 2 else "does_not_pass"

    return pd.DataFrame(results_ranked)


# ============================================================================
# FORMATTING
# ============================================================================
def format_thousands(n: int) -> str:
    """
    Format an integer with Chilean thousands separator (dots).

    Parameters
    ----------
    n : int
        Number to format.

    Returns
    -------
    str
        Formatted number, e.g. 1234567 -> '1.234.567'.

    Notes
    -----
    Duplicate of `format_number` in utils/html_helpers.py. Kept for backward
    compatibility with components/charts.py. Will be removed in a future
    cleanup pass once all imports are unified.
    """
    return f"{n:,}".replace(",", ".")
