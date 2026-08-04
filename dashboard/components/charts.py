"""
Plotly chart components.
"""

import plotly.graph_objects as go
import streamlit as st

from config.constants import CANDIDATES_2025_SR
from utils.calculations import format_thousands


def render_second_round_chart(results: dict, t: dict):
    """
    Render a stacked horizontal bar chart for second round results.

    Parameters
    ----------
    results : dict
        Dictionary with jara_votes, kast_votes, jara_pct, kast_pct,
        diff_votes, diff_pct, winner.
    t : dict
        Translation dictionary.
    """
    # Data
    candidates = [
        {"name": "José Antonio Kast", "votes": results["kast_votes"], "pct": results["kast_pct"], "color": "#1F3A5F"},
        {"name": "Jeannette Jara", "votes": results["jara_votes"], "pct": results["jara_pct"], "color": "#E84A4A"},
    ]

    # Sort: Kast first (left), Jara second (right)
    candidates_sorted = sorted(candidates, key=lambda x: x["votes"], reverse=True)
    left = candidates_sorted[0]
    right = candidates_sorted[1]

    # Create figure
    fig = go.Figure()

    # Left bar (Kast)
    fig.add_trace(go.Bar(
        x=[left["pct"]],
        y=[""],
        orientation="h",
        name=left["name"],
        marker_color=left["color"],
        text=[f"{left['pct']:.2f}%"],
        textposition="inside",
        textfont=dict(color="white", size=14, weight="bold"),
        hovertemplate=f"{left['name']}<br>{left['pct']:.2f}%<br>{left['votes']:,} {t['votes']}<extra></extra>",
    ))

    # Right bar (Jara)
    fig.add_trace(go.Bar(
        x=[right["pct"]],
        y=[""],
        orientation="h",
        name=right["name"],
        marker_color=right["color"],
        text=[f"{right['pct']:.2f}%"],
        textposition="inside",
        textfont=dict(color="white", size=14, weight="bold"),
        hovertemplate=f"{right['name']}<br>{right['pct']:.2f}%<br>{right['votes']:,} {t['votes']}<extra></extra>",
    ))

    # Layout
    fig.update_layout(
        barmode="stack",
        title={
            "text": f"<b>{t['winner']}</b><br>{results['winner']}",
            "x": 0.5,
            "xanchor": "center",
            "font": dict(size=16),
        },
        xaxis=dict(
            title="%",
            range=[0, 100],
            tickformat=".0f",
            showgrid=True,
            gridcolor="#E0E0E0",
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
        ),
        height=150,
        margin=dict(l=50, r=50, t=80, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
        ),
        showlegend=True,
        plot_bgcolor="white",
        hovermode="y",
    )

    # Add annotation for difference
    diff_text = (
        f"{'+' if results['diff_votes'] > 0 else ''}{results['diff_votes']:,} {t['votes']} · "
        f"{'+' if results['diff_pct'] > 0 else ''}{results['diff_pct']:.2f} pp"
    )
    fig.add_annotation(
        text=f"<b>{t['difference']}:</b> {diff_text}",
        x=50,
        y=-0.5,
        xref="x",
        yref="y",
        showarrow=False,
        font=dict(size=13, color="#333333"),
    )

    # Add vote counts under the bars
    fig.add_annotation(
        text=f"{format_thousands(left['votes'])}",
        x=5,
        y=-0.8,
        xref="x",
        yref="y",
        showarrow=False,
        font=dict(size=11, color="gray"),
    )
    fig.add_annotation(
        text=f"{format_thousands(right['votes'])}",
        x=95,
        y=-0.8,
        xref="x",
        yref="y",
        showarrow=False,
        font=dict(size=11, color="gray"),
    )

    st.plotly_chart(fig, use_container_width=True)
