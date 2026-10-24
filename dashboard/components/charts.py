"""
Plotly Chart Components
============================================================================
Reusable Plotly charts used across the dashboard: the second-round result
bar, the donut of communes won per candidate, and the region × candidate
heatmap.

All visible strings come from the translation dict `t`. No user-facing text
is hardcoded here. Candidate names, short names, and DataFrame column names
are data, not UI, and are kept as-is.

Features
--------
- Second-round result bar (HTML/CSS, no Plotly).
- Donut chart of communes won per candidate.
- Region × candidate heatmap with per-candidate color overlays.

Dependencies
------------
- Internal: utils.calculations (format_thousands), config.constants
  (NEUTRAL_COLOR, _get_candidate_color).
- External: math, pandas, plotly.graph_objects, streamlit.
- Downstream: pages/summary.py, views/first_round/summary.py.

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.calculations import format_thousands
from config.constants import (
    NEUTRAL_COLOR,
    _get_candidate_color,
)


# ============================================================================
# SECOND ROUND RESULT BAR
# ============================================================================
def render_second_round_chart(results: dict, t: dict) -> None:
    """
    Render the second-round result as an HTML/CSS rounded bar (no Plotly).

    The bar shows two segments (Jara and Kast) with their respective
    percentages. Above the bar: the winner label and name, colored with the
    candidate's color. Below the bar: three columns with Jara's votes,
    the difference, and Kast's votes.

    Parameters
    ----------
    results : dict
        Output of compute_second_round_results(). Must contain jara_votes,
        kast_votes, jara_pct, kast_pct, diff_votes, diff_pct, winner.
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    jara_name = "Jeannette Jara"
    kast_name = "José Antonio Kast"

    jara_votes = results["jara_votes"]
    kast_votes = results["kast_votes"]
    jara_pct = results["jara_pct"]
    kast_pct = results["kast_pct"]

    winner = results["winner"]
    winner_color = (
        _get_candidate_color(kast_name) if winner == kast_name
        else _get_candidate_color(jara_name)
    )
    kast_color = _get_candidate_color(kast_name)
    jara_color = _get_candidate_color(jara_name)

    diff_sign = "+" if results["diff_votes"] > 0 else ""
    diff_votes_formatted = format_thousands(abs(results["diff_votes"]))
    diff_pct = abs(results["diff_pct"])

    st.markdown(
        f"""<div style="text-align:center;margin-bottom:0.6rem;">
<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:{NEUTRAL_COLOR};">{t['winner']}</div>
<div style="font-size:20px;font-weight:700;color:{winner_color};">{winner}</div>
</div>
<div style="display:flex;width:100%;height:44px;border-radius:10px;overflow:hidden;">
<div style="width:{kast_pct}%;background:{kast_color};display:flex;align-items:center;justify-content:center;">
<span style="color:white;font-size:15px;font-weight:700;">{kast_pct:.2f}%</span>
</div>
<div style="width:{jara_pct}%;background:{jara_color};display:flex;align-items:center;justify-content:center;">
<span style="color:white;font-size:15px;font-weight:700;">{jara_pct:.2f}%</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""<div style="font-size:12px;color:{NEUTRAL_COLOR};">{jara_name}</div>
<div style="font-size:14px;font-weight:600;color:#1a1a18;">{format_thousands(jara_votes)} {t['votes']}</div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div style="font-size:12px;color:{NEUTRAL_COLOR};text-align:center;">{t['difference']}</div>
<div style="font-size:14px;font-weight:600;color:#1a1a18;text-align:center;">{diff_sign}{diff_votes_formatted} {t['votes']} ({diff_sign}{diff_pct:.2f} pp)</div>""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""<div style="font-size:12px;color:{NEUTRAL_COLOR};text-align:right;">{kast_name}</div>
<div style="font-size:14px;font-weight:600;color:#1a1a18;text-align:right;">{format_thousands(kast_votes)} {t['votes']}</div>""",
            unsafe_allow_html=True,
        )


# ============================================================================
# DONUT CHART
# ============================================================================
def render_donut_chart(data: dict, t: dict) -> None:
    """
    Render a donut chart showing communes won by each candidate.

    Parameters
    ----------
    data : dict
        Mapping of short candidate name -> number of communes won.
        Example: {"Jara": 120, "Kast": 150, "Parisi": 40}.
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    if not data:
        st.info(t["charts_donut_no_data"])
        return

    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    short_to_full = {
        "Jara": "Jeannette Jara",
        "Kast": "José Antonio Kast",
        "Parisi": "Franco Parisi",
        "Kaiser": "Johannes Kaiser",
        "Matthei": "Evelyn Matthei",
        "Mayne-Nicholls": "Harold Mayne-Nicholls",
        "Enríquez-Ominami": "Marco Enríquez-Ominami",
        "Artés": "Eduardo Artés",
    }
    colors = [
        _get_candidate_color(short_to_full.get(name, name))
        for name in labels
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        textposition='inside',
        insidetextorientation='horizontal',
        hoverinfo='label+value+percent',
        showlegend=False,
    )])

    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ============================================================================
# REGION × CANDIDATE HEATMAP
# ============================================================================
def render_region_candidate_heatmap(df: pd.DataFrame, t: dict) -> None:
    """
    Horizontal heatmap: candidates (rows) × regions (columns).

    Each cell of the regional winner is colored with that candidate's color
    and an intensity proportional to their % over valid votes in the region.
    Other candidates' cells stay in light gray.

    Below each column: the regional winner's name, rotated and colored.

    Technical note: Plotly's Heatmap does not allow per-cell colorscales.
    To color each winner cell with a different candidate color, the chart
    stacks 5 traces (one per candidate), each with NaN in cells that do not
    belong to that candidate. The first trace provides the gray base, the
    remaining ones paint the winning cells.

    Parameters
    ----------
    df : pd.DataFrame
        Fact table with one row per commune, including vote columns
        (jara_votes, kast_votes, etc.), casted_votes, null_votes,
        blank_votes, and region_name (optionally region_order).
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    if df is None or df.empty:
        st.info(t["charts_heatmap_no_data"])
        return

    # Candidates considered, with short names and colors
    CANDIDATES = [
        ("jara_votes", "jara_pct", "Jara",     _get_candidate_color("Jeannette Jara")),
        ("kast_votes", "kast_pct", "Kast",     _get_candidate_color("José Antonio Kast")),
        ("parisi_votes", "parisi_pct", "Parisi", _get_candidate_color("Franco Parisi")),
        ("kaiser_votes", "kaiser_pct", "Kaiser", _get_candidate_color("Johannes Kaiser")),
        ("matthei_votes", "matthei_pct", "Matthei", _get_candidate_color("Evelyn Matthei")),
    ]
    CANDIDATES = [
        (v, p, s, c) for v, p, s, c in CANDIDATES
        if v in df.columns and p in df.columns
    ]
    if not CANDIDATES:
        st.info(t["charts_heatmap_no_cols"])
        return

    df_work = df.copy()

    # Valid votes per commune
    if "valid_votes" not in df_work.columns:
        df_work["valid_votes"] = (
            df_work["casted_votes"] - df_work["null_votes"] - df_work["blank_votes"]
        )

    # Aggregation by region
    agg_dict = {"valid_votes": ("valid_votes", "sum")}
    for vcol, _, _, _ in CANDIDATES:
        df_work[vcol] = pd.to_numeric(df_work[vcol], errors="coerce").fillna(0)
        agg_dict[vcol] = (vcol, "sum")

    region_agg = df_work.groupby("region_name", as_index=False).agg(**agg_dict)

    # % over valid votes in the region
    for vcol, pcol, _, _ in CANDIDATES:
        region_agg[pcol] = (
            region_agg[vcol] / region_agg["valid_votes"].replace(0, 1) * 100
        ).round(2)

    # North-to-south order
    if "region_order" in df_work.columns:
        orden_map = (
            df_work[["region_name", "region_order"]]
            .dropna()
            .drop_duplicates()
            .set_index("region_name")["region_order"]
            .to_dict()
        )
        region_agg["_order"] = region_agg["region_name"].map(orden_map).fillna(9999)
        region_agg = region_agg.sort_values("_order").drop(columns="_order")
    else:
        region_agg = region_agg.sort_values("region_name")

    region_agg = region_agg.reset_index(drop=True)

    # Short names and regions
    short_names = [s for _, _, s, _ in CANDIDATES]
    regions = region_agg["region_name"].tolist()

    # Matrix of % per region × candidate
    region_pct = {}
    for _, row in region_agg.iterrows():
        r = row["region_name"]
        region_pct[r] = {}
        for _, pcol, short, _ in CANDIDATES:
            region_pct[r][short] = float(row.get(pcol, 0) or 0)

    # Regional winner by total votes (not by %)
    winner_by_region = {}
    for _, row in region_agg.iterrows():
        r = row["region_name"]
        votos_por_cand = {
            short: float(row.get(vcol, 0) or 0)
            for vcol, _, short, _ in CANDIDATES
        }
        winner_by_region[r] = max(votos_por_cand.items(), key=lambda x: x[1])[0]

    short_to_color = {s: c for _, _, s, c in CANDIDATES}

    # ------------------------------------------------------------------
    # FIGURE
    # ------------------------------------------------------------------
    fig = go.Figure()

    # Base trace: all % in very light gray
    base_z = []
    for short in short_names:
        base_z.append([region_pct[r][short] for r in regions])

    fig.add_trace(go.Heatmap(
        z=base_z,
        x=regions,
        y=short_names,
        colorscale=[[0.0, "#FCFCFA"], [1.0, "#E8E8E0"]],
        zmin=0, zmax=40,
        showscale=False,
        xgap=3, ygap=3,
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.2f}%<extra></extra>",
    ))

    # Overlays: 5 traces, one per candidate, only painting the winning cell
    for _, _, short, color in CANDIDATES:
        overlay_z = []
        for s in short_names:
            row_values = []
            for r in regions:
                if s == short and winner_by_region[r] == short:
                    row_values.append(region_pct[r][short])
                else:
                    row_values.append(math.nan)
            overlay_z.append(row_values)

        fig.add_trace(go.Heatmap(
            z=overlay_z,
            x=regions,
            y=short_names,
            colorscale=[[0.0, color + "40"], [1.0, color]],
            zmin=0, zmax=40,
            showscale=False,
            xgap=3, ygap=3,
            hoverinfo="skip",
        ))

    # Regional winner names below each column, rotated 90°
    for r in regions:
        winner = winner_by_region[r]
        color = short_to_color[winner]
        fig.add_annotation(
            x=r,
            xref="x",
            y=-0.02,
            yref="paper",
            text=f"<b>{winner}</b>",
            showarrow=False,
            font=dict(
                color=color,
                size=9,
                family="Liberation Sans, Arial, sans-serif",
            ),
            textangle=-90,
            xanchor="center",
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        )

    fig.update_layout(
        height=440,
        margin=dict(l=80, r=20, t=80, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Liberation Sans, Arial, sans-serif"),
        xaxis=dict(
            side="top",
            tickfont=dict(
                size=9,
                color="#333",
                family="Liberation Sans, Arial, sans-serif",
            ),
            tickangle=-40,
            showgrid=False,
        ),
        yaxis=dict(
            tickfont=dict(
                size=11,
                color="#333",
                family="Liberation Sans, Arial, sans-serif",
            ),
            autorange="reversed",
            showgrid=False,
        ),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
