"""
Data table components with styling.
"""

import pandas as pd
import streamlit as st


def render_first_round_table(df_results: pd.DataFrame, t: dict):
    """
    Render a styled table for first round results.

    Parameters
    ----------
    df_results : pd.DataFrame
        DataFrame with candidate_name, party, votes, pct, status, color.
    t : dict
        Translation dictionary.
    """
    # Prepare display data
    display_df = df_results.copy()

    # Format votes with thousands separator
    display_df["votes_formatted"] = display_df["votes"].apply(lambda x: f"{x:,}".replace(",", "."))

    # Format percentage
    display_df["pct_formatted"] = display_df["pct"].apply(lambda x: f"{x:.2f}%")

    # Translate status
    status_map = {
        "passes_to_runoff": t["passes_to_runoff"],
        "does_not_pass": t["does_not_pass"],
    }
    display_df["status_formatted"] = display_df["status"].map(status_map)

    # Select columns for display
    display_cols = ["candidate_name", "party", "votes_formatted", "pct_formatted", "status_formatted"]

    # Rename columns
    column_names = {
        "candidate_name": t["candidate"],
        "party": t["party"],
        "votes_formatted": t["votes"],
        "pct_formatted": t["pct"],
        "status_formatted": t["status"],
    }

    final_df = display_df[display_cols].rename(columns=column_names)

    # Apply styling
    def color_status(val):
        """Color the status cell."""
        if val == t["passes_to_runoff"]:
            return "background-color: #DDF4E4; color: #1E753D; font-weight: bold;"
        return "background-color: #F5F5F5; color: #A0A0A0;"

    def color_candidate(val):
        """Color the candidate name based on their color."""
        # We need to use the original color mapping
        color_map = df_results.set_index("candidate_name")["color"].to_dict()
        color = color_map.get(val, "#333333")
        return f"color: {color}; font-weight: bold;"

    styled = final_df.style.applymap(
        color_status,
        subset=[t["status"]],
    )

    # Apply candidate color to first column
    for idx, row in df_results.iterrows():
        styled = styled.apply(
            lambda x, idx=idx, row=row: [f"color: {row['color']}; font-weight: bold;" if i == 0 else "" for i in range(len(x))],
            axis=1,
            subset=pd.IndexSlice[idx, :],
        )

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            t["candidate"]: st.column_config.TextColumn(t["candidate"], width="medium"),
            t["party"]: st.column_config.TextColumn(t["party"], width="large"),
            t["votes"]: st.column_config.TextColumn(t["votes"], width="small"),
            t["pct"]: st.column_config.TextColumn(t["pct"], width="small"),
            t["status"]: st.column_config.TextColumn(t["status"], width="medium"),
        },
    )

    # Add legal note
    st.caption("⚖️ " + t.get("legal_note", "De acuerdo con la ley N° 18.700, en el caso que ningún candidato obtenga la mayoría absoluta de los votos válidamente emitidos (50% + 1), se realizará una segunda vuelta entre las dos candidaturas más votadas."))
