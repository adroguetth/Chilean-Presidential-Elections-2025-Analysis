"""
Core calculations for vote metrics and results.
"""

import pandas as pd

from config.constants import CANDIDATES_2025, CANDIDATES_2025_SR


def compute_vote_metrics(df_raw: pd.DataFrame, padron: int = None) -> dict:
    """
    Calculate national vote metrics from a fact table.
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


def compute_round_comparison(df_current_raw: pd.DataFrame, df_previous_raw: pd.DataFrame) -> dict:
    """
    Compare vote percentages between two rounds (in percentage points).
    """
    current = compute_vote_metrics(df_current_raw)
    previous = compute_vote_metrics(df_previous_raw)

    return {
        "valid_pct_diff": current["valid_pct"] - previous["valid_pct"],
        "null_pct_diff": current["null_pct"] - previous["null_pct"],
        "blank_pct_diff": current["blank_pct"] - previous["blank_pct"],
    }


def compute_second_round_results(df_raw: pd.DataFrame) -> dict:
    """
    Calculate second round results.
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


def format_thousands(n: int) -> str:
    """Format integer with thousands separator (Chilean style: dots)."""
    return f"{n:,}".replace(",", ".")
