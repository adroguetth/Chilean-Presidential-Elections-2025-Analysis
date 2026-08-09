"""
Table components for the dashboard.
Uses st.components.v1.html() for reliable rendering.
"""

import streamlit as st
import pandas as pd


def _table_css(container_id: str) -> str:
    """Return CSS for a table with the given container ID."""
    return f"""
    <style>
        #{container_id} {{
            border-radius: 10px;
            border: 1px solid #E0DED8;
            overflow: hidden;
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        #{container_id} table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        #{container_id} th {{
            text-align: left;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: .05em;
            color: #888780;
            padding: 8px 12px;
            border-bottom: 1px solid #E0DED8;
            font-weight: 500;
            background: #fafafa;
        }}
        #{container_id} td {{
            padding: 8px 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        #{container_id} tr:last-child td {{
            border-bottom: none;
        }}
        #{container_id} tr:hover td {{
            background: #F7F6F3;
        }}
        .cand-dot {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 3px;
            margin-right: 6px;
            vertical-align: middle;
        }}
        .pill {{
            font-size: 10px;
            padding: 2px 10px;
            border-radius: 4px;
            font-weight: 500;
            white-space: nowrap;
        }}
        .pill-advance {{
            background: #E8F5E9;
            color: #2E7D32;
        }}
        .pill-normal {{
            background: #F0EFEC;
            color: #888780;
        }}
        .bar-container {{
            display: flex;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
        }}
        .macro-pill {{
            font-size: 11px;
            padding: 2px 10px;
            border-radius: 12px;
            font-weight: 600;
            display: inline-block;
        }}
        .table-footer {{
            font-size: 12px;
            color: #888780;
            padding: 0.5rem 1.25rem 0.25rem 1.25rem;
            border-top: 1px solid #E0DED8;
            margin-top: 0.5rem;
        }}
    </style>
    """


def render_first_round_table(df: pd.DataFrame, t: dict):
    """Render candidate table with dots and pills (no internal title)."""
    if df is None or df.empty:
        st.warning(f"⚠️ {t.get('no_data', 'No data available')}")
        return

    rows = ""
    for _, row in df.iterrows():
        pill_class = "pill-advance" if row["status"] == "passes_to_runoff" else "pill-normal"
        status_label = t["passes_to_runoff"] if row["status"] == "passes_to_runoff" else t["does_not_pass"]
        rows += f"""
        <tr>
            <td><span class="cand-dot" style="background:{row['color']};"></span>{row['candidate_name']}</td>
            <td style="color:#888780;">{row['party']}</td>
            <td>{row['votes']:,}</td>
            <td>{row['pct']:.2f}%</td>
            <td><span class="pill {pill_class}">{status_label}</span></td>
        </tr>"""

    html = f"""
    {_table_css("candidate-table")}
    <div id="candidate-table">
        <table>
            <thead>
                <tr>
                    <th>{t['candidate']}</th>
                    <th>{t['party']}</th>
                    <th>{t['votes']}</th>
                    <th>{t['pct']}</th>
                    <th>{t['status']}</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <div class="table-footer">⚖️ {t['runoff_note']}</div>
    </div>
    """
    st.components.v1.html(html, height=500, scrolling=False)


def render_bastion_table(df: pd.DataFrame, candidate_name: str, color: str):
    """Render bastion table (Top 5 communes, no internal title)."""
    if df is None or df.empty:
        st.write("No hay datos")
        return

    # Format numbers
    df_f = df.copy()
    df_f["votos"] = df_f["votos"].apply(lambda x: f"{x:,}".replace(",", "."))
    df_f["porcentaje"] = df_f["porcentaje"].apply(lambda x: f"{x:.2f}%")

    rows = ""
    for i, row in df_f.iterrows():
        rows += f"""
        <tr>
            <td style="text-align:center;color:#888780;font-weight:500;">{i}</td>
            <td style="font-weight:600;font-size:13px;">{row['commune_name']}</td>
            <td style="color:#888780;font-size:12px;">{row['region_name']}</td>
            <td style="color:{color};font-weight:600;text-align:right;">{row['porcentaje']}</td>
        </tr>"""

    html = f"""
    {_table_css("bastion-table")}
    <div id="bastion-table">
        <table>
            <thead>
                <tr>
                    <th style="text-align:center;">#</th>
                    <th>Comuna</th>
                    <th>Región</th>
                    <th style="text-align:right;">%</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """
    st.components.v1.html(html, height=350, scrolling=False)


def render_macrozone_table(df: pd.DataFrame, color_by_short: dict):
    """
    Render macrozone table (no internal title).
    df must have columns: macrozone, jara_pct, kast_pct, parisi_pct, nulo_pct,
    ganador, jara_votes, kast_votes, parisi_votes
    """
    if df is None or df.empty:
        st.warning("No hay datos para macrozona")
        return

    rows = ""
    for _, row in df.iterrows():
        three_sum = row["jara_votes"] + row["kast_votes"] + row["parisi_votes"]
        w_jara = (row["jara_votes"] / three_sum * 100) if three_sum else 0.0
        w_kast = (row["kast_votes"] / three_sum * 100) if three_sum else 0.0
        w_parisi = (row["parisi_votes"] / three_sum * 100) if three_sum else 0.0

        ganador = row["ganador"]
        ganador_color = color_by_short.get(ganador, "#888780")
        r = int(ganador_color[1:3], 16)
        g = int(ganador_color[3:5], 16)
        b = int(ganador_color[5:7], 16)
        pill_bg = f"rgba({r},{g},{b},0.12)"

        rows += f"""
        <tr>
            <td style="font-weight:600;">{row['macrozone']}</td>
            <td style="color:{color_by_short.get('Jara', '#E84A4A')};">{row['jara_pct']:.1f}%</td>
            <td style="color:{color_by_short.get('Kast', '#1F3A5F')};">{row['kast_pct']:.1f}%</td>
            <td style="color:{color_by_short.get('Parisi', '#3166B5')};">{row['parisi_pct']:.1f}%</td>
            <td style="color:#E68A2E;">{row['nulo_pct']:.2f}%</td>
            <td><span class="macro-pill" style="background:{pill_bg};color:{ganador_color};">{ganador}</span></td>
            <td>
                <div class="bar-container">
                    <div style="width:{w_jara}%;background:{color_by_short.get('Jara', '#E84A4A')};"></div>
                    <div style="width:{w_kast}%;background:{color_by_short.get('Kast', '#1F3A5F')};"></div>
                    <div style="width:{w_parisi}%;background:{color_by_short.get('Parisi', '#3166B5')};"></div>
                </div>
            </td>
        </tr>"""

    html = f"""
    {_table_css("macro-table")}
    <div id="macro-table">
        <table>
            <thead>
                <tr>
                    <th>Macrozona</th>
                    <th>Jara %</th>
                    <th>Kast %</th>
                    <th>Parisi %</th>
                    <th>% Nulo</th>
                    <th>Ganador</th>
                    <th>Distribución</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """
    st.components.v1.html(html, height=400, scrolling=False)
