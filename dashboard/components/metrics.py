"""
Reusable metric card components.
"""

import streamlit as st

NEUTRAL_COLOR = "#86867F"
RED_COLOR = "#E84A4A"


def _custom_metric_card(label: str, value: str, delta_text: str, color: str, arrow: str):
    """
    Custom metric card for cases where st.metric doesn't provide enough control.
    """
    arrow_html = f"{arrow} " if arrow else ""
    st.markdown(
        f"""<div style="background:#ffffff;border:1px solid #E0DED8;border-radius:10px;padding:0.7rem 1rem;">
<div style="font-size:10px;text-transform:uppercase;letter-spacing:.04em;color:#888780;">{label}</div>
<div style="font-size:20px;font-weight:600;color:#1a1a18;">{value}</div>
<div style="font-size:11px;color:{color};margin-top:4px;">{arrow_html}{delta_text}</div>
</div>""",
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: dict, t: dict, deltas: dict = None):
    """
    Render four metric cards in a row.
    """
    deltas = deltas or {}

    casted = deltas.get("casted", (f"{metrics['casted_pct']:.2f}%", "normal"))
    valid = deltas.get("valid", (f"{metrics['valid_pct']:.2f}% del total", "normal"))
    null_ = deltas.get("null", (f"{metrics['null_pct']:.2f}% del total", "inverse"))
    blank = deltas.get("blank", (f"{metrics['blank_pct']:.2f}% del total", "inverse"))

    cards = [
        (t["casted_votes"], metrics["casted_votes"], casted),
        (t["valid_votes"], metrics["valid_votes"], valid),
        (t["null_votes"], metrics["null_votes"], null_),
        (t["blank_votes"], metrics["blank_votes"], blank),
    ]

    cols = st.columns(4)

    for col, (label, value, entry) in zip(cols, cards):
        text, mode = entry
        with col:
            if mode in ("normal", "inverse"):
                st.metric(
                    label=label,
                    value=f"{value:,}",
                    delta=text,
                    delta_color=mode,
                )
            else:
                arrow = {"neutral": "", "down": "▼", "up": "▲"}.get(mode, "")
                color = NEUTRAL_COLOR if mode == "neutral" else RED_COLOR
                _custom_metric_card(label, f"{value:,}", text, color, arrow)


def render_metric_cards_6(metrics: dict, t: dict, num_candidates: int = None):
    """
    Render six metric cards in two rows of three columns.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Inscritos",
            value=f"{metrics.get('padron', 15_779_102):,}",
            delta="Voto obligatorio",
            delta_color="off",
        )

    with col2:
        st.metric(
            label=t["casted_votes"],
            value=f"{metrics['casted_votes']:,}",
            delta=f"{metrics.get('casted_pct_padron', metrics['casted_pct']):.2f}% del padrón",
            delta_color="normal",
        )

    with col3:
        st.metric(
            label=t["valid_votes"],
            value=f"{metrics['valid_votes']:,}",
            delta=f"{metrics['valid_pct']:.2f}% del total",
            delta_color="normal",
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            label=t["null_votes"],
            value=f"{metrics['null_votes']:,}",
            delta=f"{metrics['null_pct']:.2f}% del total",
            delta_color="inverse",
        )

    with col5:
        st.metric(
            label=t["blank_votes"],
            value=f"{metrics['blank_votes']:,}",
            delta=f"{metrics['blank_pct']:.2f}% del total",
            delta_color="inverse",
        )

    with col6:
        st.metric(
            label="Candidatos",
            value=num_candidates if num_candidates else 8,
            delta="3 con >10%",
            delta_color="off",
        )
