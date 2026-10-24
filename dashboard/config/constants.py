"""
Global Constants
============================================================================
Single source of truth for candidates, colors, macrozones, and other
dashboard-wide constants.

This module contains only data (dicts, lists, strings) and a small set of
helper functions for color resolution. No Streamlit, no UI, no translations
for data values (candidate names, party names, macrozone names are proper
nouns and are kept as-is).

Features
--------
- Candidate metadata: 2025 (first and second round), 2021.
- Macrozone mapping and ordering.
- Electoral roll size (padrón electoral).
- Database URL and local path.
- Color palettes for candidates, political groups, and blocks.
- Color variants per candidate (light/dark shades).
- Indicator, trend, margin, and heatmap scales.
- Helper functions: _get_candidate_color, _hex_to_rgba, _hex_to_rgba_string.

Dependencies
------------
- Internal: none.
- External: unicodedata, pandas.
- Downstream: all views, pages, and components.

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import unicodedata

import pandas as pd


# ============================================================================
# CANDIDATES 2025 (FIRST ROUND)
# ============================================================================
CANDIDATES_2025 = {
    "Jeannette Jara": {
        "column": "jara_votes",
        "party": "Unidad por Chile",
        "color": "#E34843",
        "short_name": "Jara",
    },
    "José Antonio Kast": {
        "column": "kast_votes",
        "party": "Partido Republicano",
        "color": "#243C5F",
        "short_name": "Kast",
    },
    "Franco Parisi": {
        "column": "parisi_votes",
        "party": "Partido de la Gente",
        "color": "#3466B3",
        "short_name": "Parisi",
    },
    "Johannes Kaiser": {
        "column": "kaiser_votes",
        "party": "Partido Nacional Libertario",
        "color": "#F1893F",
        "short_name": "Kaiser",
    },
    "Evelyn Matthei": {
        "column": "matthei_votes",
        "party": "Chile Vamos",
        "color": "#3272BF",
        "short_name": "Matthei",
    },
    "Harold Mayne-Nicholls": {
        "column": "mayne_nicholls_votes",
        "party": "Independiente",
        "color": "#C0D9E0",
        "short_name": "Mayne-Nicholls",
    },
    "Marco Enríquez-Ominami": {
        "column": "enriquez_ominami_votes",
        "party": "Izquierda Alternativa",
        "color": "#DF2884",
        "short_name": "Enríquez-Ominami",
    },
    "Eduardo Artés": {
        "column": "artes_votes",
        "party": "Izquierda Radical",
        "color": "#CA1518",
        "short_name": "Artés",
    },
}


# ============================================================================
# CANDIDATES 2025 (SECOND ROUND)
# ============================================================================
CANDIDATES_2025_SR = {
    "Jeannette Jara": {
        "column": "jara_votes",
        "party": "Unidad por Chile",
        "color": "#E34843",
        "short_name": "Jara",
    },
    "José Antonio Kast": {
        "column": "kast_votes",
        "party": "Partido Republicano",
        "color": "#243C5F",
        "short_name": "Kast",
    },
}


# ============================================================================
# MACROZONES
# ============================================================================
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


# ============================================================================
# ELECTORAL ROLL
# ============================================================================
# PADRON_ELECTORAL_2025 = "padrón electoral" (electoral roll) for 2025.
PADRON_ELECTORAL_2025 = 15_779_102


# ============================================================================
# DATABASE
# ============================================================================
DB_URL = (
    "https://raw.githubusercontent.com/adroguetth/"
    "Chilean-Presidential-Elections-2025-Analysis/main/"
    "raw/database/chile_elections.db"
)

DB_LOCAL_PATH = "chile_elections.db"


# ============================================================================
# DEFAULT FILTERS
# ============================================================================
DEFAULT_FILTERS = {
    "macrozone": None,
    "region": None,
    "commune": None,
}


# ============================================================================
# CANDIDATE COLORS — single source of truth
# ============================================================================
# Derived from CANDIDATES_2025. Exposed here as a flat dict so the territorial
# explorer and new views can use them without duplication. Includes name
# variants (with/without accents, full names) so _get_candidate_color()
# resolves any form coming from the data.

CANDIDATE_COLORS = {
    # Jara
    "Jeannette Jara": "#E34843",
    "Jeannette Jara Román": "#E34843",
    "Jara": "#E34843",
    # Kast
    "José Antonio Kast": "#243C5F",
    "Jose Antonio Kast": "#243C5F",
    "José Antonio Kast Rist": "#243C5F",
    "Kast": "#243C5F",
    # Parisi
    "Franco Parisi": "#3466B3",
    "Franco Aldo Parisi Fernández": "#3466B3",
    "Parisi": "#3466B3",
    # Kaiser
    "Johannes Kaiser": "#F1893F",
    "Johannes Kaiser Barents-von Hohenhagen": "#F1893F",
    "Kaiser": "#F1893F",
    # Matthei
    "Evelyn Matthei": "#3272BF",
    "Evelyn Rose Matthei Fornet": "#3272BF",
    "Matthei": "#3272BF",
    # Mayne-Nicholls
    "Harold Mayne-Nicholls": "#C0D9E0",
    "Harold Alfred Mayne-Nicholls Secor": "#C0D9E0",
    "Mayne-Nicholls": "#C0D9E0",
    # Enríquez-Ominami
    "Marco Enríquez-Ominami": "#DF2884",
    "Marco Enríquez-Ominami Gumucio": "#DF2884",
    "Enríquez-Ominami": "#DF2884",
    # Artés
    "Eduardo Artés": "#CA1518",
    "Eduardo Antonio Artés Brichetti": "#CA1518",
    "Artés": "#CA1518",
}


# ============================================================================
# CANDIDATE COLORS 2021
# ============================================================================
# Colors for the 2021 first round candidates. Some overlap with 2025 when the
# candidate or block repeats (Kast, Parisi, MEO, Artés).

CANDIDATE_COLORS_2021 = {
    # Boric
    "Gabriel Boric": "#E34843",
    "Boric": "#E34843",
    # Kast
    "José Antonio Kast": "#243C5F",
    "Kast": "#243C5F",
    # Parisi
    "Franco Parisi": "#3466B3",
    "Parisi": "#3466B3",
    # Provoste
    "Yasna Provoste": "#80097E",
    "Provoste": "#80097E",
    # Sichel
    "Sebastián Sichel": "#3272BF",
    "Sichel": "#3272BF",
    # Enríquez-Ominami
    "Marco Enríquez-Ominami": "#DF2884",
    "Enríquez-Ominami": "#DF2884",
    # Artés
    "Eduardo Artés": "#CA1518",
    "Artés": "#CA1518",
}


# ============================================================================
# POLITICAL GROUPS — 8 ideological groups
# ============================================================================
# Colors for ideological blocks (not individual candidates). A block can group
# more than one candidate. For individual candidate colors, always use
# _get_candidate_color().

POLITICAL_GROUPS = {
    "Izquierda / Centro-Izquierda": "#E34843",
    "Derecha Conservadora": "#243C5F",
    "Derecha Tradicional": "#3272BF",
    "Nueva Derecha / Libertario": "#F1893F",
    "Tercera Vía / Antisistema": "#3466B3",
    "Izquierda Alternativa": "#DF2884",
    "Izquierda Radical": "#CA1518",
    "Independiente": "#C0D9E0",
}


# ============================================================================
# POLITICAL BLOCKS — 3 aggregated blocks
# ============================================================================
# Reduced version of POLITICAL_GROUPS: 3 aggregated blocks (left, right,
# anti-system) used in the "Strategic Analysis by Ideological Blocks" chart.

POLITICAL_BLOCKS = {
    "Izquierda": "#E34843",
    "Derecha": "#243C5F",
    "Antisistema": "#9AA0A6",
}


# ============================================================================
# CANDIDATE COLOR VARIANTS — per-candidate shades
# ============================================================================
# Color variants per candidate. Only Jara and Kast have variants defined so
# far. The rest will be added when needed.

CANDIDATE_COLOR_VARIANTS = {
    "Jeannette Jara": {
        "oficial": "#E34843",
        "claro": "#D94B4B",
        "muy_claro": "#FCC3C3",
        "intenso": "#B72222",
    },
    "José Antonio Kast": {
        "oficial": "#243C5F",
        "claro": "#3D76AC",
        "muy_claro": "#5E90BF",
        "intenso": "#121E30",
    },
}


# ============================================================================
# INDICATOR COLORS
# ============================================================================
# Colors for UI indicators: positive, negative, neutral variations and deltas.

COLOR_POSITIVE = "#2E7D32"
COLOR_NEGATIVE = "#C0392B"
COLOR_NEUTRAL_INDICATOR = "#D0D4DA"
COLOR_DELTA = "#A03A3A"


# ============================================================================
# ELECTORAL DATA COLORS
# ============================================================================
# Colors for vote types: valid, null, blank.

COLOR_VALIDOS = "#EBE4D6"
COLOR_NULOS = "#595959"
COLOR_BLANCOS = "#B4814C"


# ============================================================================
# TREND COLORS
# ============================================================================
# Colors for pills and markers that indicate trend (up/down/flat).

TREND_COLOR_UP = "#E84A4A"
TREND_COLOR_DOWN = "#2E7D32"
TREND_COLOR_FLAT = "#6b7280"


# ============================================================================
# SCATTER / GROUPING COLORS
# ============================================================================
# Gray for secondary points in scatter plots.
TREND_GRAY = "#9CA3AF"

# Palette for K-means clusters (commune segmentation).
CLUSTER_COLORS = ["#5C6BC0", "#7CB342", "#F57C00", "#8E24AA"]


# ============================================================================
# INTENSITY SCALES (reds and grays)
# ============================================================================
# Reusable scales for charts that encode intensity: defeat margins, percentage
# heatmaps, count heatmaps.

# Intensity scale for defeat margins (from closest to most comfortable).
MARGIN_SCALE_COLORS = {
    "0-1%": "#B91C1C",
    "1-2%": "#DA4A4A",
    "2-3%": "#F28787",
    "3-4%": "#F8A0A0",
    "4-5%": "#FCC5C5",
}

# Scale for heatmaps of vote % over casted votes — red variant (Jara).
HEATMAP_SCALE_PCT = [
    [0.00, "#FCE7E7"],
    [0.15, "#FCC5C5"],
    [0.35, "#F28787"],
    [0.55, "#DA4A4A"],
    [0.80, "#B91C1C"],
    [1.00, "#7F1010"],
]

# Scale for heatmaps of vote % — blue variant (Kast).
HEATMAP_SCALE_PCT_KAST = [
    [0.00, "#E8F0F8"],
    [0.15, "#C5D5E8"],
    [0.30, "#8BB2D4"],
    [0.45, "#5E91C0"],
    [0.60, "#3D76AC"],
    [0.75, "#2A5890"],
    [0.90, "#1A3D74"],
    [1.00, "#0F2D5C"],
]

# Scale for heatmaps of commune count (0 to max).
HEATMAP_SCALE_COUNT = [
    [0.0, "#FFFFFF"],
    [0.25, "#FCC5C5"],
    [0.5, "#F8A0A0"],
    [0.75, "#DA4A4A"],
    [1.0, "#B91C1C"],
]


# ============================================================================
# NEUTRAL COLOR
# ============================================================================
# Neutral color for unrecognized names (medium gray).
NEUTRAL_COLOR = "#6B7280"


# ============================================================================
# ID TO NAME MAP
# ============================================================================
# Numeric ID to canonical name. Some datasets ship "1".."8".
_ID_TO_NAME = {
    "1": "Jeannette Jara",
    "2": "José Antonio Kast",
    "3": "Franco Parisi",
    "4": "Johannes Kaiser",
    "5": "Evelyn Matthei",
    "6": "Harold Mayne-Nicholls",
    "7": "Marco Enríquez-Ominami",
    "8": "Eduardo Artés",
}


# ============================================================================
# HELPERS
# ============================================================================
def _normalize(s: str) -> str:
    """
    Normalize a name: strip accents, lowercase, collapse spaces.

    Parameters
    ----------
    s : str
        Name to normalize.

    Returns
    -------
    str
        Normalized name (ASCII, lowercase).
    """
    return (
        unicodedata.normalize("NFD", str(s))
        .encode("ascii", "ignore")
        .decode()
        .lower()
        .strip()
    )


def _get_candidate_color(name) -> str:
    """
    Return the candidate color hex from any name variant.

    Accepts full name, surname, numeric ID as string, or None.

    Parameters
    ----------
    name : Any
        Candidate name or ID.

    Returns
    -------
    str
        Hex color string. Returns NEUTRAL_COLOR if the name is not recognized.
    """
    if name is None:
        return NEUTRAL_COLOR
    try:
        if pd.isna(name):
            return NEUTRAL_COLOR
    except Exception:
        pass

    n = str(name).strip()
    if not n or n.lower() == "nan":
        return NEUTRAL_COLOR

    if n in CANDIDATE_COLORS:
        return CANDIDATE_COLORS[n]

    n_norm = _normalize(n)
    if n_norm in _ID_TO_NAME:
        return CANDIDATE_COLORS.get(_ID_TO_NAME[n_norm], NEUTRAL_COLOR)

    for k, v in CANDIDATE_COLORS.items():
        k_norm = _normalize(k)
        if k_norm == n_norm:
            return v
        if k_norm in n_norm or n_norm in k_norm:
            return v
        k_tokens = set(k_norm.split())
        n_tokens = set(n_norm.split())
        common = k_tokens & n_tokens
        if any(len(t) > 3 for t in common):
            return v

    try:
        first = n_norm.split()[0]
        for k, v in CANDIDATE_COLORS.items():
            if first in _normalize(k):
                return v
    except Exception:
        pass

    return NEUTRAL_COLOR


def _hex_to_rgba(hex_color, alpha: int = 180) -> list:
    """
    Convert a hex '#RRGGBB' to [r, g, b, alpha] for PyDeck.

    Parameters
    ----------
    hex_color : str
        Hex color string.
    alpha : int, optional
        Alpha channel (default 180).

    Returns
    -------
    list
        [r, g, b, alpha]. Returns neutral gray if the input is invalid.
    """
    h = str(hex_color).lstrip("#")
    try:
        return [int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha]
    except Exception:
        return [107, 114, 128, alpha]


def _hex_to_rgba_string(hex_color, alpha: float = 0.12) -> str:
    """
    Convert a hex '#RRGGBB' to 'rgba(r,g,b,a)' for CSS.

    Parameters
    ----------
    hex_color : str
        Hex color string.
    alpha : float, optional
        Alpha channel (default 0.12).

    Returns
    -------
    str
        RGBA string. Returns neutral gray if the input is invalid.
    """
    h = str(hex_color).lstrip("#")
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except Exception:
        return f"rgba(107,114,128,{alpha})"


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================
# These aliases keep the old names working while the rest of the codebase is
# migrated to the new names. They will be removed in a future cleanup pass,
# once all imports have been updated.

GRIS_TENDENCIA = TREND_GRAY
