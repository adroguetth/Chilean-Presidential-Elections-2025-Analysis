"""
Constants used across the dashboard.
"""

CANDIDATES_2025 = {
    "Jeannette Jara": {
        "column": "jara_votes",
        "party": "Unidad por Chile",
        "color": "#E84A4A",
        "short_name": "Jara",
    },
    "José Antonio Kast": {
        "column": "kast_votes",
        "party": "Partido Republicano",
        "color": "#1F3A5F",
        "short_name": "Kast",
    },
    "Franco Parisi": {
        "column": "parisi_votes",
        "party": "Partido de la Gente",
        "color": "#3166B5",
        "short_name": "Parisi",
    },
    "Johannes Kaiser": {
        "column": "kaiser_votes",
        "party": "Partido Nacional Libertario",
        "color": "#F28A3D",
        "short_name": "Kaiser",
    },
    "Evelyn Matthei": {
        "column": "matthei_votes",
        "party": "Chile Vamos",
        "color": "#2E73C1",
        "short_name": "Matthei",
    },
    "Harold Mayne-Nicholls": {
        "column": "mayne_nicholls_votes",
        "party": "Independiente Centro",
        "color": "#D5DFE4",
        "short_name": "Mayne-Nicholls",
    },
    "Marco Enríquez-Ominami": {
        "column": "enriquez_ominami_votes",
        "party": "Independiente de Izquierda",
        "color": "#D43986",
        "short_name": "Enríquez-Ominami",
    },
    "Eduardo Artés": {
        "column": "artes_votes",
        "party": "Independiente Extrema Izquierda",
        "color": "#CC2222",
        "short_name": "Artés",
    },
}

CANDIDATES_2025_SR = {
    "Jeannette Jara": {
        "column": "jara_votes",
        "party": "Unidad por Chile",
        "color": "#E84A4A",
        "short_name": "Jara",
    },
    "José Antonio Kast": {
        "column": "kast_votes",
        "party": "Partido Republicano",
        "color": "#1F3A5F",
        "short_name": "Kast",
    },
}

MACROZONE_MAP = {
    15: "Norte Grande",
    1: "Norte Grande",
    2: "Norte Grande",
    3: "Norte Chico",
    4: "Norte Chico",
    5: "Centro",
    13: "Centro",
    6: "Centro",
    7: "Centro",
    16: "Centro Sur",
    8: "Centro Sur",
    9: "Centro Sur",
    14: "Sur",
    10: "Sur",
    11: "Patagonia",
    12: "Patagonia",
}

MACROZONE_ORDER = {
    "Norte Grande": 1,
    "Norte Chico": 2,
    "Centro": 3,
    "Centro Sur": 4,
    "Sur": 5,
    "Patagonia": 6,
}

PROTEST_COLORS = {
    "very_high": "#8B0000",
    "high": "#CC3333",
    "medium": "#E68A2E",
    "low": "#F4C542",
    "very_low": "#A8D5A2",
    "no_data": "#D3D3D3",
}

PADRON_ELECTORAL_2025 = 15_779_102

DB_URL = (
    "https://raw.githubusercontent.com/adroguetth/"
    "Chilean-Presidential-Elections-2025-Analysis/main/"
    "raw/database/chile_elections.db"
)

DB_LOCAL_PATH = "chile_elections.db"

DEFAULT_FILTERS = {
    "macrozone": None,
    "region": None,
    "commune": None,
}
