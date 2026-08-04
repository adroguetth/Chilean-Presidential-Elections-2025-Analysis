"""
ES/EN translations for the dashboard UI.

All UI text is centralized here. Use `t = LANG[st.session_state.language]`
to access the current language dictionary.
"""

LANG = {
    "ES": {
        # Header
        "app_title": "Elecciones Presidenciales 2025 · Chile",
        "app_subtitle": "República de Chile · Resultados nacionales",
        "language": "Idioma",

        # Main navigation
        "summary": "Resumen",
        "first_round": "Primera Vuelta",
        "second_round": "Segunda Vuelta",

        # Sub-navigation (First / Second Round)
        "zones": "Zonas",
        "communal": "Comunal",
        "null_blank": "Nulos / Blancos",
        "transfers": "Transferencias",
        "historical": "Histórico",

        # Segment / Metrics tabs
        "segment": "Segmentación",
        "metrics": "Métricas",

        # Filters
        "macrozone": "Macrozona",
        "region": "Región",
        "commune": "Comuna",
        "all": "Todos",

        # Summary page
        "summary_title": "Resumen Ejecutivo",
        "second_round_title": "Segunda Vuelta",
        "first_round_title": "Primera Vuelta",
        "casted_votes": "Votos emitidos",
        "valid_votes": "Votos válidos",
        "null_votes": "Votos nulos",
        "blank_votes": "Votos en blanco",
        "winner": "Presidente electo",
        "difference": "Diferencia",
        "votes": "votos",
        "passes_to_runoff": "Pasa a 2ª vuelta",
        "does_not_pass": "No pasa",
        "candidate": "Candidato",
        "party": "Partido / Coalición",
        "pct": "%",
        "status": "Estado",

        # Footer
        "data_source": "Datos extraídos de Servicio Electoral de Chile (Servel)",
        "data_source_note": "Escrutinio definitivo · Actualizado: 18 de diciembre 2025",

        # General
        "loading": "Cargando datos...",
        "error": "Error al cargar los datos",
        "no_data": "No hay datos disponibles",
    },
    "EN": {
        # Header
        "app_title": "Presidential Elections 2025 · Chile",
        "app_subtitle": "Republic of Chile · National results",
        "language": "Language",

        # Main navigation
        "summary": "Summary",
        "first_round": "First Round",
        "second_round": "Second Round",

        # Sub-navigation (First / Second Round)
        "zones": "Zones",
        "communal": "Communal",
        "null_blank": "Null / Blank",
        "transfers": "Transfers",
        "historical": "Historical",

        # Segment / Metrics tabs
        "segment": "Segment",
        "metrics": "Metrics",

        # Filters
        "macrozone": "Macrozone",
        "region": "Region",
        "commune": "Commune",
        "all": "All",

        # Summary page
        "summary_title": "Executive Summary",
        "second_round_title": "Second Round",
        "first_round_title": "First Round",
        "casted_votes": "Casted votes",
        "valid_votes": "Valid votes",
        "null_votes": "Null votes",
        "blank_votes": "Blank votes",
        "winner": "President-elect",
        "difference": "Difference",
        "votes": "votes",
        "passes_to_runoff": "Passes to runoff",
        "does_not_pass": "Does not pass",
        "candidate": "Candidate",
        "party": "Party / Coalition",
        "pct": "%",
        "status": "Status",

        # Footer
        "data_source": "Data from Servicio Electoral de Chile (Servel)",
        "data_source_note": "Final scrutiny · Updated: December 18, 2025",

        # General
        "loading": "Loading data...",
        "error": "Error loading data",
        "no_data": "No data available",
    },
}
