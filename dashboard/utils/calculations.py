"""
Core calculations for vote metrics and results.
"""

import pandas as pd

from config.constants import CANDIDATES_2025, CANDIDATES_2025_SR


def compute_vote_metrics(df_raw: pd.DataFrame) -> dict:
    """
    Calculate national vote metrics from a fact table.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Fact table with casted_votes, null_votes, blank_votes.

    Returns
    -------
    dict
        casted_votes, valid_votes, null_votes, blank_votes,
        casted_pct, valid_pct, null_pct, blank_pct
    """
    casted_votes = int(df_raw["casted_votes"].sum())
    null_votes = int(df_raw["null_votes"].sum())
    blank_votes = int(df_raw["blank_votes"].sum())
    valid_votes = casted_votes - null_votes - blank_votes

    return {
        "casted_votes": casted_votes,
        "valid_votes": valid_votes,
        "null_votes": null_votes,
        "blank_votes": blank_votes,
        "casted_pct": 100.0,
        "valid_pct": (valid_votes / casted_votes * 100) if casted_votes else 0.0,
        "null_pct": (null_votes / casted_votes * 100) if casted_votes else 0.0,
        "blank_pct": (blank_votes / casted_votes * 100) if casted_votes else 0.0,
    }


def compute_second_round_results(df_raw: pd.DataFrame) -> dict:
    """
    Calculate second round results: votes, percentages, and difference.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Fact table with jara_votes and kast_votes.

    Returns
    -------
    dict
        jara_votes, kast_votes, jara_pct, kast_pct, diff_votes, diff_pct, winner
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


def compute_first_round_results(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate first round results by candidate.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Fact table with candidate vote columns.

    Returns
    -------
    pd.DataFrame
        Columns: candidate_name, party, votes, pct, status, color
    """
    # Calculate total valid votes
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

    # Sort by votes descending
    results_ranked = sorted(results, key=lambda x: x["votes"], reverse=True)

    # Add status: top 2 pass to runoff
    for i, row in enumerate(results_ranked):
        row["status"] = "passes_to_runoff" if i < 2 else "does_not_pass"

    return pd.DataFrame(results_ranked)


def format_thousands(n: int) -> str:
    """Format integer with thousands separator (Chilean style: dots)."""
    return f"{n:,}".replace(",", ".")
