"""
Plotly chart components.
"""

import plotly.graph_objects as go
import streamlit as st

from utils.calculations import format_thousands


def render_second_round_chart(results: dict, t: dict):
    """
    Render the second round result as an HTML/CSS rounded bar (no Plotly).
    """
    jara_name = "Jeannette Jara"
    kast_name = "José Antonio Kast"

    jara_votes = results["jara_votes"]
    kast_votes = results["kast_votes"]
    jara_pct = results["jara_pct"]
    kast_pct = results["kast_pct"]

    winner = results["winner"]
    winner_color = "#1F3A5F" if winner == kast_name else "#E84A4A"

    diff_sign = "+" if results["diff_votes"] > 0 else ""
    diff_votes_formatted = format_thousands(abs(results["diff_votes"]))
    diff_pct = abs(results["diff_pct"])

    st.markdown(
        f"""<div style="text-align:center;margin-bottom:0.6rem;">
<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#888780;">{t['winner']}</div>
<div style="font-size:20px;font-weight:700;color:{winner_color};">{winner}</div>
</div>
<div style="display:flex;width:100%;height:44px;border-radius:10px;overflow:hidden;">
<div style="width:{kast_pct}%;background:#1F3A5F;display:flex;align-items:center;justify-content:center;">
<span style="color:white;font-size:15px;font-weight:700;">{kast_pct:.2f}%</span>
</div>
<div style="width:{jara_pct}%;background:#E84A4A;display:flex;align-items:center;justify-content:center;">
<span style="color:white;font-size:15px;font-weight:700;">{jara_pct:.2f}%</span>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""<div style="font-size:12px;color:#888780;">{jara_name}</div>
<div style="font-size:14px;font-weight:600;color:#1a1a18;">{format_thousands(jara_votes)} {t['votes']}</div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div style="font-size:12px;color:#888780;text-align:center;">{t['difference']}</div>
<div style="font-size:14px;font-weight:600;color:#1a1a18;text-align:center;">{diff_sign}{diff_votes_formatted} {t['votes']} ({diff_sign}{diff_pct:.2f} pp)</div>""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""<div style="font-size:12px;color:#888780;text-align:right;">{kast_name}</div>
<div style="font-size:14px;font-weight:600;color:#1a1a18;text-align:right;">{format_thousands(kast_votes)} {t['votes']}</div>""",
            unsafe_allow_html=True,
        )


def render_donut_chart(data: dict, t: dict):
    """
    Render a donut chart showing communes won by each candidate.
    """
    if not data:
        st.info("No hay datos de comunas ganadas para mostrar.")
        return

    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    color_map = {
        "Kast": "#1F3A5F",
        "Jara": "#E84A4A",
        "Parisi": "#3166B5",
        "Kaiser": "#F28A3D",
        "Matthei": "#2E73C1",
        "Mayne-Nicholls": "#D5DFE4",
        "Enríquez-Ominami": "#D43986",
        "Artés": "#CC2222",
    }
    colors = [color_map.get(name, "#888888") for name in labels]

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
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
