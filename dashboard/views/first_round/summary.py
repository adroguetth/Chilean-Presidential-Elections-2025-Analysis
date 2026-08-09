"""
First Round — Summary view (dynamic with filters).

Shows:
1. 6 KPI cards (3+3 layout)
2. Candidate table (8 candidates with status)
3. Donut: communes won by candidate
4. Top 5 communes for Jara, Kast, Parisi (bastiones electorales)
5. Macrozone results: Jara%/Kast%/Parisi%/%Nulo/Ganador/Distribución
"""

import streamlit as st
import pandas as pd

from utils.data_loader import load_fact_first_round_2025
from utils.calculations import (
    compute_vote_metrics,
    compute_first_round_results,
)
from config.constants import (
    PADRON_ELECTORAL_2025,
    CANDIDATES_2025,
    MACROZONE_ORDER,
)
from components.tables import (
    render_first_round_table,
    render_bastion_table,
    render_macrozone_table,
)
from components.charts import render_donut_chart
from components.metrics import render_metric_cards_6


# ============================================================================
# CONSTANTS — Electoral strongholds
# ============================================================================
MIN_VOTOS_EMITIDOS = 300


# ============================================================================
# FUNCTION — Top 5 bastions (exactly as in script 05)
# ============================================================================
def top_bastiones(df: pd.DataFrame, votes_col: str, pct_col: str, n: int = 5) -> pd.DataFrame:
    """
    Returns the n communes where a candidate gets their highest % of valid votes,
    among communes that exceed the voting threshold.
    """
    cols = ["commune_name", "region_name", "macrozone", votes_col, pct_col]
    out = (
        df[cols]
        .rename(columns={votes_col: "votos", pct_col: "porcentaje"})
        .sort_values("porcentaje", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    out.index = out.index + 1
    return out


def render(t: dict):
    """
    Render the First Round Summary page.
    """
    try:
        df_fr_2025_raw = load_fact_first_round_2025()

        # ====================================================================
        # 1. KPIs (6 cards, 3+3 layout)
        # ====================================================================
        fr_metrics = compute_vote_metrics(df_fr_2025_raw, padron=PADRON_ELECTORAL_2025)
        fr_results = compute_first_round_results(df_fr_2025_raw)
        num_candidates = len(fr_results)

        render_metric_cards_6(fr_metrics, t, num_candidates)

        # ====================================================================
        # 2. Candidate table (title outside)
        # ====================================================================
        st.markdown(
            f"<h3 style='font-size:16px;font-weight:600;color:#1a1a18;margin-top:0.5rem;margin-bottom:0.25rem;'>{t.get('candidate_results_title', 'Resultados por candidato')}</h3>",
            unsafe_allow_html=True,
        )
        render_first_round_table(fr_results, t)

        # ====================================================================
        # 3. Donut — Communes won by candidate
        # ====================================================================
        st.markdown(
            "<h3 style='font-size:16px;font-weight:600;color:#1a1a18;margin-top:1rem;margin-bottom:0.25rem;'>Comunas ganadas por candidato</h3>",
            unsafe_allow_html=True,
        )

        candidate_columns = {
            "Jara": "jara_pct",
            "Kast": "kast_pct",
            "Parisi": "parisi_pct",
            "Kaiser": "kaiser_pct",
            "Matthei": "matthei_pct",
            "Mayne-Nicholls": "mayne_nicholls_pct",
            "Enríquez-Ominami": "enriquez_ominami_pct",
            "Artés": "artes_pct",
        }

        df_communes = df_fr_2025_raw.copy()
        for col in candidate_columns.values():
            df_communes[col] = pd.to_numeric(df_communes[col], errors='coerce')

        pct_cols = list(candidate_columns.values())
        df_communes['winner'] = df_communes[pct_cols].idxmax(axis=1)
        col_to_name = {v: k for k, v in candidate_columns.items()}
        df_communes['winner_name'] = df_communes['winner'].map(col_to_name)

        communes_won = df_communes['winner_name'].value_counts().to_dict()
        communes_won = {k: v for k, v in communes_won.items() if v > 0}

        render_donut_chart(communes_won, t)

        # ====================================================================
        # 4. Bastions — Top 5 communes (Jara, Kast, Parisi)
        # ====================================================================
        st.markdown(
            "<h3 style='font-size:16px;font-weight:600;color:#1a1a18;margin-top:1rem;margin-bottom:0.25rem;'>Top 5 comunas por candidato (Bastiones electorales)</h3>",
            unsafe_allow_html=True,
        )

        df_base = df_fr_2025_raw[df_fr_2025_raw["casted_votes"] >= MIN_VOTOS_EMITIDOS].copy()

        CANDIDATOS_FOCO = {
            "Jeannette Jara": {
                "votes_col": "jara_votes",
                "pct_col": "jara_pct",
                "color": "#E84A4A",
            },
            "José Antonio Kast": {
                "votes_col": "kast_votes",
                "pct_col": "kast_pct",
                "color": "#1F3A5F",
            },
            "Franco Parisi": {
                "votes_col": "parisi_votes",
                "pct_col": "parisi_pct",
                "color": "#3166B5",
            },
        }

        bastiones = {}
        for nombre, meta in CANDIDATOS_FOCO.items():
            bastiones[nombre] = top_bastiones(
                df_base,
                meta["votes_col"],
                meta["pct_col"],
                n=5
            )

        cols = st.columns(3)
        for idx, (nombre, tabla) in enumerate(bastiones.items()):
            with cols[idx]:
                color = CANDIDATOS_FOCO[nombre]["color"]
                st.markdown(
                    f"<div style='font-weight:600;color:{color};font-size:14px;margin-bottom:0.3rem;'>🏅 {nombre}</div>",
                    unsafe_allow_html=True,
                )
                render_bastion_table(tabla, nombre, color)

        # ====================================================================
        # 5. Macrozone — Jara% / Kast% / Parisi% / %Nulo / Ganador / Distribución
        # ====================================================================
        st.markdown(
            "<h3 style='font-size:16px;font-weight:600;color:#1a1a18;margin-top:1rem;margin-bottom:0.25rem;'>Resultados por macrozona</h3>",
            unsafe_allow_html=True,
        )

        color_by_short = {meta["short_name"]: meta["color"] for meta in CANDIDATES_2025.values()}
        vote_cols_all = {meta["short_name"]: meta["column"] for meta in CANDIDATES_2025.values()}
        cols_votos = list(vote_cols_all.values())
        col_to_short = {v: k for k, v in vote_cols_all.items()}

        sum_cols = cols_votos + ["casted_votes", "null_votes"]
        df_macro = df_fr_2025_raw.groupby("macrozone")[sum_cols].sum().reset_index()

        df_macro["total_valid"] = df_macro[cols_votos].sum(axis=1)
        df_macro["ganador_col"] = df_macro[cols_votos].idxmax(axis=1)
        df_macro["ganador"] = df_macro["ganador_col"].map(col_to_short)
        df_macro["jara_pct"] = df_macro["jara_votes"] / df_macro["total_valid"] * 100
        df_macro["kast_pct"] = df_macro["kast_votes"] / df_macro["total_valid"] * 100
        df_macro["parisi_pct"] = df_macro["parisi_votes"] / df_macro["total_valid"] * 100
        df_macro["nulo_pct"] = df_macro["null_votes"] / df_macro["casted_votes"] * 100
        df_macro["order"] = df_macro["macrozone"].map(MACROZONE_ORDER)
        df_macro = df_macro.sort_values("order")

        render_macrozone_table(df_macro, color_by_short)

        # ====================================================================
        # FOOTER
        # ====================================================================
        st.divider()
        st.markdown(
            f"<div style='text-align:center;font-size:12px;color:#888780;padding:0.5rem 0;'>{t['data_source']} · {t['data_source_note']}</div>",
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"{t['error']}: {e}")
        st.exception(e)
