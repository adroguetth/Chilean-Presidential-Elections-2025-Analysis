"""
Geographic data loader — Regiones de Chile.
"""

import os
import geopandas as gpd
import pandas as pd
import streamlit as st


@st.cache_data
def load_region_geometries() -> gpd.GeoDataFrame:
    """
    Carga geometrías de regiones de Chile desde el repositorio caracena.
    """
    # Intentar cargar desde archivo local
    local_path = "assets/regiones_chile.geojson"
    if os.path.exists(local_path):
        gdf = gpd.read_file(local_path)
        if len(gdf) > 0:
            return gdf

    # Descargar desde GitHub y guardar
    print("Descargando geometrías de regiones desde GitHub...")
    url = "https://raw.githubusercontent.com/caracena/chile-geojson/master/regiones.geojson"
    gdf = gpd.read_file(url)
    gdf.to_file(local_path, driver="GeoJSON")
    print(f"Archivo guardado: {local_path}")
    return gdf


@st.cache_data
def prepare_region_map_data(df_votes: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Une los resultados electorales con las geometrías de regiones.

    Parameters
    ----------
    df_votes : pd.DataFrame
        Datos electorales con columna 'region_name' (nombre de región).

    Returns
    -------
    gpd.GeoDataFrame
        Geometrías de regiones con columnas electorales añadidas.
    """
    # Cargar geometrías de regiones
    gdf_regions = load_region_geometries()

    # Normalizar nombres para el merge
    # El GeoJSON de regiones tiene columna 'nombre'
    gdf_regions['region_name'] = gdf_regions['nombre'].str.upper().str.strip()

    # Normalizar nombres en df_votes
    df_votes['region_name_norm'] = df_votes['region_name'].str.upper().str.strip()

    # Agrupar votos por región
    vote_cols = [col for col in df_votes.columns if col.endswith('_votes')]
    df_region_agg = df_votes.groupby('region_name_norm')[vote_cols].sum().reset_index()

    # Merge con geometrías
    gdf_merged = gdf_regions.merge(
        df_region_agg,
        on='region_name_norm',
        how='left'
    )

    # Calcular total de votos válidos y ganador
    if vote_cols:
        gdf_merged['total_valid'] = gdf_merged[vote_cols].sum(axis=1)
        gdf_merged['ganador_col'] = gdf_merged[vote_cols].idxmax(axis=1)
        # Mapear nombre de columna a nombre de candidato
        col_to_name = {col: col.replace('_votes', '').replace('_', ' ').title() for col in vote_cols}
        gdf_merged['ganador'] = gdf_merged['ganador_col'].map(col_to_name)

    return gdf_merged


def render_region_map(
    gdf: gpd.GeoDataFrame,
    selected_region: str = None,
    figsize: tuple = (10, 12),
    title: str = "Resultados por región - Primera Vuelta 2025"
):
    """
    Renderiza un mapa de Chile coloreado por región ganadora.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame con geometrías y columna 'ganador'.
    selected_region : str, optional
        Región a resaltar (zoom).
    figsize : tuple
        Tamaño de la figura.
    title : str
        Título del mapa.
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    # Definir colores por candidato (usar los mismos que en constants)
    color_map = {
        "Jara": "#E84A4A",
        "Kast": "#1F3A5F",
        "Parisi": "#3166B5",
        "Kaiser": "#F28A3D",
        "Matthei": "#2E73C1",
        "Mayne Nicholls": "#D5DFE4",
        "Enriquez Ominami": "#D43986",
        "Artes": "#CC2222",
    }
    # Añadir colores para nombres largos
    color_map["Jeannette Jara"] = "#E84A4A"
    color_map["José Antonio Kast"] = "#1F3A5F"
    color_map["Franco Parisi"] = "#3166B5"
    color_map["Johannes Kaiser"] = "#F28A3D"
    color_map["Evelyn Matthei"] = "#2E73C1"

    # Asignar colores
    gdf['color'] = gdf['ganador'].map(color_map).fillna('#D3D3D3')

    fig, ax = plt.subplots(figsize=figsize)
    gdf.plot(ax=ax, color=gdf['color'], edgecolor='white', linewidth=0.8)

    # Si hay región seleccionada, resaltarla
    if selected_region:
        gdf_selected = gdf[gdf['region_name'] == selected_region]
        if not gdf_selected.empty:
            gdf_selected.plot(ax=ax, color='none', edgecolor='#FFD700', linewidth=3, zorder=10)

    ax.set_axis_off()
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    # Leyenda
    legend_elements = []
    for name, color in color_map.items():
        if name in gdf['ganador'].unique():
            legend_elements.append(Patch(facecolor=color, edgecolor='none', label=name))

    if legend_elements:
        ax.legend(
            handles=legend_elements,
            loc='lower left',
            fontsize=9,
            frameon=False,
            bbox_to_anchor=(0, 0.01)
        )

    plt.tight_layout()
    return fig
