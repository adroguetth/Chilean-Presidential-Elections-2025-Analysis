"""
Second Round Page — Parent View with Sub-Navigation
============================================================================
Orchestrator for the Second Round page. Renders the page title and a tab bar
with six tabs (Summary, Territorial Explorer, Panorama, Candidate Jara,
Candidate Kast, Historical). The active tab determines which view module is
imported and rendered.

The tab bar is delegated to components.layout.render_sub_navigation, which
handles state initialization, legacy session cleanup, and single-click tab
switching via on_click callbacks.

Each tab's view is imported dynamically with _render_safe. This allows the
page to keep working even if a view module is missing or broken: the user
sees a translated fallback message instead of a full page crash.

Features
--------
- Page title from translations.
- Six tabs (Summary, Territorial Explorer, Panorama, Jara, Kast, Historical).
- Dynamic import with graceful fallback per tab.

Dependencies
------------
- Internal: components.layout (render_sub_navigation),
  components.titles (render_page_title).
- External: streamlit.
- Downstream: app.py (render_second_round).

Requirements
------------
- All view modules must expose a `render(t)` function.

Author: Alfonso Droguett
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
Email: adroguett.consultor@gmail.com
"""

import streamlit as st

from components.layout import render_sub_navigation
from components.titles import render_page_title


# ============================================================================
# RENDER
# ============================================================================
def render(t: dict) -> None:
    """
    Render the Second Round page.

    Builds the tab list, delegates the tab bar to
    components.layout.render_sub_navigation, and dispatches to the active
    view via _render_safe.

    Parameters
    ----------
    t : dict
        Translation dictionary for the current language (LANG[lang]).

    Returns
    -------
    None
    """
    render_page_title(t["second_round"])

    tabs = [
        ("summary", t["summary"]),
        ("territorial_explorer", t["territorial_explorer"]),
        ("panorama", t["sr_orch_tab_panorama"]),
        ("jara", t["sr_orch_tab_jara"]),
        ("kast", t["sr_orch_tab_kast"]),
        ("historical", t["historical"]),
    ]

    selected_tab = render_sub_navigation(t, "second_round_tab", tabs)

    if selected_tab == "summary":
        _render_safe(
            "views.second_round.summary",
            t,
            fallback=t["sr_orch_fallback_summary"],
        )

    elif selected_tab == "territorial_explorer":
        _render_safe(
            "views.second_round.territorial",
            t,
            fallback=t["sr_orch_fallback_territorial"],
        )

    elif selected_tab == "panorama":
        _render_safe(
            "views.second_round.panorama",
            t,
            fallback=t["sr_orch_fallback_panorama"],
        )

    elif selected_tab == "jara":
        _render_safe(
            "views.second_round.jara",
            t,
            fallback=t["sr_orch_fallback_jara"],
        )

    elif selected_tab == "kast":
        _render_safe(
            "views.second_round.kast",
            t,
            fallback=t["sr_orch_fallback_kast"],
        )

    elif selected_tab == "historical":
        _render_safe(
            "views.second_round.historical",
            t,
            fallback=t["sr_orch_fallback_historical"],
        )


# ============================================================================
# SAFE RENDER
# ============================================================================
def _render_safe(module_path: str, t: dict, fallback: str = "") -> None:
    """
    Import and execute the render function of the given module.

    If the module does not exist (ImportError), a translated fallback
    message is shown instead of crashing the whole page. If the module
    raises any other exception, it is caught and shown via st.error.

    Uses __import__(module_path, fromlist=["render"]) to import a module
    by dotted path at runtime. This is needed because the module path is
    stored in a string (e.g. "views.second_round.summary") and resolved
    lazily. A regular `import` statement would require the path at parse
    time, which defeats the purpose of the fallback.

    Parameters
    ----------
    module_path : str
        Dotted module path (e.g. "views.second_round.summary").
    t : dict
        Translation dictionary for the current language (LANG[lang]).
    fallback : str, optional
        Message shown if the module is missing. If empty, the generic
        fr_orch_fallback_modulo message is used with the ImportError.

    Returns
    -------
    None
    """
    try:
        module = __import__(module_path, fromlist=["render"])
        render_fn = getattr(module, "render")
        render_fn(t)
    except ImportError as e:
        st.info(fallback or t["fr_orch_fallback_modulo"].format(err=e))
    except Exception as e:
        st.error(f"{t.get('error', 'Error')}: {e}")
        st.exception(e)
