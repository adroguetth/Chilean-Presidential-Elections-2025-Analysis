"""
HTML Helper Utilities
============================================================================
Pure transformation helpers for the dashboard views.

This module contains ONLY functions that transform data (strings, numbers,
colors) into a format ready to be inserted into HTML. It does NOT contain
functions that define visual styles: all CSS, sizes, colors, and spacing
live in each view, respecting the format that each one defines.

Rule: if a function has a <style> block inside, it does not belong here.

Features
--------
- HTML cleaning and escaping.
- Number, percentage, and percentage-point formatting (Chilean locale).
- Hex color to RGBA conversion.
- Commune name normalization for comparisons.

Dependencies
------------
- Internal: none.
- External: unicodedata (standard library).
- Downstream: all views and components that render HTML.

Requirements
------------
- None.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import unicodedata


# ============================================================================
# CLEANING AND ESCAPING
# ============================================================================
def clean_html(html: str) -> str:
    """
    Remove leading whitespace from each line so Markdown does not treat
    the content as a code block.

    Parameters
    ----------
    html : str
        Raw HTML string, possibly indented.

    Returns
    -------
    str
        HTML string with each line stripped of leading/trailing whitespace.
    """
    return "\n".join(line.strip() for line in html.strip().split("\n"))


def escape_html(s) -> str:
    """
    Escape dangerous characters to insert plain text inside HTML.

    Parameters
    ----------
    s : Any
        Value to escape. Converted to string internally.

    Returns
    -------
    str
        Escaped string safe for HTML insertion.
    """
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ============================================================================
# NUMBER FORMATTING
# ============================================================================
def format_number(v) -> str:
    """
    Format a number with Chilean thousands separator (dot).

    Parameters
    ----------
    v : Any
        Value to format. Converted to float and rounded internally.

    Returns
    -------
    str
        Formatted number, e.g. 1234567 -> '1.234.567'.
        Returns '0' if the value cannot be converted.
    """
    try:
        return f"{int(round(float(v))):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def format_percentage(v: float, decimals: int = 2) -> str:
    """
    Format a number as a percentage string.

    Parameters
    ----------
    v : float
        Value to format (already in percentage scale, e.g. 12.34 for 12.34%).
    decimals : int, optional
        Number of decimal places (default 2).

    Returns
    -------
    str
        Formatted percentage, e.g. 12.34 -> '12.34%'.
    """
    return f"{v:.{decimals}f}%"


def format_signed(v: float, decimals: int = 2) -> str:
    """
    Format a number with an explicit sign.

    Parameters
    ----------
    v : float
        Value to format.
    decimals : int, optional
        Number of decimal places (default 2).

    Returns
    -------
    str
        Formatted number with sign, e.g. 3.16 -> '+3.16', -1.23 -> '-1.23'.
    """
    return f"+{v:.{decimals}f}" if v >= 0 else f"{v:.{decimals}f}"


def format_pp(v: float, decimals: int = 2) -> str:
    """
    Format a number as percentage points with an explicit sign.

    Parameters
    ----------
    v : float
        Value to format.
    decimals : int, optional
        Number of decimal places (default 2).

    Returns
    -------
    str
        Formatted percentage points, e.g. 3.16 -> '+3.16 pp'.
    """
    return f"{format_signed(v, decimals)} pp"


# ============================================================================
# COLORS
# ============================================================================
def hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    """
    Convert a hex color to an RGBA string.

    Parameters
    ----------
    hex_color : str
        Hex color string, with or without leading '#'.
    alpha : float, optional
        Alpha channel (default 0.12).

    Returns
    -------
    str
        RGBA string, e.g. '#E34843' -> 'rgba(227,72,67,0.12)'.
        Falls back to neutral gray if the input is invalid.
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
# COMMUNE NAME NORMALIZATION
# ============================================================================
def normalize_commune(s) -> str:
    """
    Normalize a commune name for comparisons.

    Removes accents, collapses whitespace, and converts to uppercase.

    Parameters
    ----------
    s : Any
        Commune name to normalize. Converted to string internally.

    Returns
    -------
    str
        Normalized commune name, e.g. 'Ñuñoa' -> 'NUNOA'.
    """
    n = unicodedata.normalize("NFKD", str(s))
    n = "".join(c for c in n if not unicodedata.combining(c))
    return " ".join(n.strip().upper().split())


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================
# These aliases keep the old names working while the rest of the codebase
# is migrated to the new function names. They will be removed in a future
# cleanup pass, once all imports have been updated.

fmt_number = format_number
fmt_pct = format_percentage
fmt_signed = format_signed
fmt_pp = format_pp
norm_commune = normalize_commune
