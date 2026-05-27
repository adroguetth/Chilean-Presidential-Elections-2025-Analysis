#!/usr/bin/env python3
"""
Generador de Mapas Electorales - Segunda Vuelta Presidencial Chile 2025.

Módulo principal para generar mapas electorales detallados de Chile,
mostrando resultados por comuna de la segunda vuelta presidencial 2025
(Jara vs Kast). Incluye mapas regionales, áreas metropolitanas,
reportes estadísticos y visualizaciones nacionales.

Características principales:
- Generación de mapas por región con nombres de comunas
- Mapas de áreas metropolitanas (Gran Santiago, Valparaíso, Concepción)
- Reportes nacionales y regionales con estadísticas
- Visualización de diferencia de votos con escala de colores personalizada
- Procesamiento de datos electorales desde archivos CSV
- Integración con datos geográficos de múltiples fuentes

Autor: Alfonso Droguett
Fecha: 2025
"""

# ============================================================================
# IMPORTS Y CONFIGURACIÓN
# ============================================================================

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import sys
import warnings
import logging
from pathlib import Path
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime
import argparse
import requests
from io import BytesIO
from matplotlib.patches import Rectangle
from PIL import Image
import urllib.request
import tempfile
import shutil

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
warnings.filterwarnings('ignore')

# ============================================================================
# CONSTANTES Y CONFIGURACIONES
# ============================================================================

# Mapeo de números de región a nombres
REGIONES_ANTIGUAS_NUM = {
    1: "Tarapacá",
    2: "Antofagasta",
    3: "Atacama",
    4: "Coquimbo",
    5: "Valparaíso",
    6: "O'Higgins",
    7: "Maule",
    8: "Biobío",
    9: "Araucanía",
    10: "Los Lagos",
    11: "Aysén",
    12: "Magallanes",
    13: "Metropolitana",
    14: "Los Ríos",
    15: "Arica y Parinacota",
    16: "Ñuble"
}

# Nombres completos de regiones para títulos
REGIONES_NOMBRES_TITULOS = {
    1: "Región de Tarapacá",
    2: "Región de Antofagasta",
    3: "Región de Atacama",
    4: "Región de Coquimbo",
    5: "Región de Valparaíso",
    6: "Región del Libertador General Bernardo O'Higgins",
    7: "Región del Maule",
    8: "Región del Biobío",
    9: "Región de la Araucanía",
    10: "Región de Los Lagos",
    11: "Región de Aysén del General Carlos Ibáñez del Campo",
    12: "Región de Magallanes y de la Antártica Chilena",
    13: "Región Metropolitana de Santiago",
    14: "Región de Los Ríos",
    15: "Región de Arica y Parinacota",
    16: "Región de Ñuble"
}

# Tamaños de fuente para etiquetas de comunas por región
TAMANOS_FUENTE_REGION = {
    1: 9,
    2: 9,
    3: 9,
    4: 9,
    5: 9,
    6: 9,
    7: 9,
    8: 8,
    9: 9,
    10: 9,
    11: 9,
    12: 9,
    13: 9,
    14: 9,
    15: 9,
    16: 9
}

# Tamaños de fuente para áreas metropolitanas
TAMANOS_FUENTE_AREAS_METROPOLITANAS = {
    'gran_valparaiso': 9,
    'gran_concepcion': 9,
    'gran_santiago': 14,
    'islas': 9,
    'region_metropolitana_etiquetas': 9,
    'region_metropolitana_numeros': 9
}

# Mapeo de nombres de región en CSV a números de región
NOMBRES_CSV_A_NUM = {
    "Metropolitana": 13,
    "Libertador": 6,
    "Maule": 7,
    "Biobío": 8,
    "Arica y Parinacota": 15,
    "Tarapacá": 1,
    "Antofagasta": 2,
    "Atacama": 3,
    "Coquimbo": 4,
    "Valparaíso": 5,
    "Ñuble": 16,
    "La Araucanía": 9,
    "Los Ríos": 14,
    "Los Lagos": 10,
    "Aysén": 11,
    "Magallanes": 12,
    "O'Higgins": 6,
    "Valparaiso": 5,
    "Bio Bío": 8,
    "Bio Bio": 8,
    "Araucania": 9,
    "Araucanía": 9,
    "Aysen": 11,
    "Nuble": 16,
    "Los Rios": 14
}

# Paleta de colores para la diferencia entre candidatos
COLORES_BALOTAJE = [
    '#0F2D5C',
    '#1A3D7C',
    '#2A58A6',
    '#3D76D1',
    '#5E91E8',
    '#8BB2F0',
    '#9CA3AF',
    '#F8A0A0',
    '#F28787',
    '#E86969',
    '#DA4A4A',
    '#C92A2A',
    '#B91C1C',
]

# Mapa de colores continuo para la escala
cmap_continuo = LinearSegmentedColormap.from_list('jara_kast_divergente', COLORES_BALOTAJE, N=256)


def asignar_color_diferencia(diferencia):
    """
    Asigna color hexadecimal según la diferencia porcentual entre candidatos.

    Args:
        diferencia (float): Diferencia porcentual (Jara% - Kast%).

    Returns:
        str: Código hexadecimal del color asignado.
    """
    if pd.isna(diferencia):
        return "#D3D3D3"

    if diferencia == 0:
        return "#9CA3AF"

    if diferencia > 0:
        if diferencia >= 50:
            return "#B91C1C"
        elif diferencia >= 40:
            return "#C92A2A"
        elif diferencia >= 30:
            return "#DA4A4A"
        elif diferencia >= 20:
            return "#E86969"
        elif diferencia >= 10:
            return "#F28787"
        else:
            return "#F8A0A0"
    else:
        diferencia_abs = abs(diferencia)
        if diferencia_abs >= 50:
            return "#0F2D5C"
        elif diferencia_abs >= 40:
            return "#1A3D7C"
        elif diferencia_abs >= 30:
            return "#2A58A6"
        elif diferencia_abs >= 20:
            return "#3D76D1"
        elif diferencia_abs >= 10:
            return "#5E91E8"
        else:
            return "#8BB2F0"


# ============================================================================
# DEFINICIONES DE ÁREAS METROPOLITANAS Y COMUNAS ESPECIALES
# ============================================================================

# Comunas que forman parte del Gran Santiago
CONURBACION_SANTIAGO = [
    "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central",
    "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja",
    "Providencia", "Las Condes", "La Reina", "Lo Espejo",
    "Lo Prado", "Macul", "Maipú", "Ñuñoa", "Padre Hurtado",
    "Pedro Aguirre Cerda", "Peñalolén", "Vitacura", "Pudahuel", "Puente Alto",
    "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo",
    "San Joaquín", "San Miguel", "San Ramón", "Santiago", "Lo Barnechea"
]

# Comunas que forman parte del Gran Valparaíso
GRAN_VALPARAISO = [
    "Valparaíso", "Viña del Mar", "Concón", "Quilpué", "Villa Alemana"
]

# Comunas que forman parte del Gran Concepción
GRAN_CONCEPCION = [
    "Concepción", "Coronel", "Chiguayante", "Hualpén", "Hualqui", "Lota",
    "Penco", "San Pedro de la Paz", "Talcahuano", "Tomé"
]

# Mapeo de comunas del Gran Santiago a números (para etiquetas pequeñas)
MAQUEO_COMUNAS_NUMEROS = {
    "Conchalí": "1",
    "Recoleta": "2",
    "Independencia": "3",
    "Cerro Navia": "4",
    "Quinta Normal": "5",
    "Providencia": "6",
    "Lo Prado": "7",
    "Estación Central": "8",
    "Pedro Aguirre Cerda": "9",
    "San Miguel": "10",
    "San Joaquín": "11",
    "Macul": "12",
    "Cerrillos": "13",
    "Lo Espejo": "14",
    "La Cisterna": "15",
    "San Ramón": "16",
    "La Granja": "17"
}

# Mapeo de comunas de Región Metropolitana a números
COMUNAS_NUMEROS_RM = {
    "Quilicura": "1",
    "Huechuraba": "2",
    "Las Condes": "3",
    "Pudahuel": "4",
    "Maipú": "5",
    "Padre Hurtado": "6",
    "San Bernardo": "7",
    "Peñaflor": "8",
    "Calera de Tango": "9",
    "El Monte": "10",
    "Talagante": "11",
    "Isla de Maipo": "12"
}

# Comunas de RM que solo llevan etiqueta (sin número)
COMUNAS_ETIQUETAS_RM = [
    "Tiltil",
    "Colina",
    "Lo Barnechea",
    "Lampa",
    "Curacaví",
    "María Pinto",
    "Melipilla",
    "San Pedro",
    "Alhué",
    "Paine",
    "Buin",
    "Pirque",
    "San José de Maipo"
]

# Mapeo de comunas de Región de Valparaíso a números
COMUNAS_NUMEROS_REGION_5 = {
    "Concón": "1",
    "Viña del Mar": "2",
    "Villa Alemana": "3",
    "Limache": "4",
    "La Cruz": "5",
    "Calera": "6",
    "San Felipe": "7",
    "Panquehue": "8",
    "Santa María": "9",
    "Rinconada": "10",
    "El Quisco": "11",
    "El Tabo": "12"
}

# Mapeo de comunas de Región de O'Higgins a números
COMUNAS_NUMEROS_REGION_6 = {
    "Codegua": "1",
    "Graneros": "2",
    "Doñihue": "3",
    "Olivar": "4",
    "Coinco": "5",
    "Quinta de Tilcoco": "6",
    "Peumo": "7",
    "Pichidegua": "8"
}

# Mapeo de comunas de Región del Maule a números
COMUNAS_NUMEROS_REGION_7 = {
    "Licantén": "1",
    "Rauco": "2",
    "San Rafael": "3",
    "Río Claro": "4",
    "Villa Alegre": "5",
    "Yerbas Buenas": "6"
}

# Mapeo de comunas de Región del Biobío a números
COMUNAS_NUMEROS_REGION_8 = {
    "Concepción": "1",
    "Talcahuano": "2",
    "Hualpén": "3",
    "Penco": "4",
    "San Pedro de la Paz": "5",
    "Chiguayante": "6",
    "Coronel": "7",
    "Lota": "8",
    "San Rosendo": "9",
    "Negrete": "10",
    "Quilaco": "11",
    "Contulmo": "12"
}

# Mapeo de comunas de Región de la Araucanía a números
COMUNAS_NUMEROS_REGION_9 = {
    "Renaico": "1",
    "Ercilla": "2",
    "Perquenco": "3",
    "Lautaro": "4",
    "Cholchol": "5",
    "Nueva Imperial": "6",
    "Padre Las Casas": "7",
    "Saavedra": "8",
    "Teodoro Schmidt": "9",
    "Pitrufquén": "10"
}

# Mapeo de comunas de Región de Los Lagos a números
COMUNAS_NUMEROS_REGION_10 = {
    "San Juan de la Costa": "1",
    "Río Negro": "2",
    "Frutillar": "3",
    "Llanquihue": "4",
    "Calbuco": "5",
    "Quemchi": "6",
    "Dalcahue": "7",
    "Castro": "8",
    "Curaco de Vélez": "9",
    "Puqueldón": "10",
    "Quinchao": "11",
    "Queilén": "12"
}

# Mapeo de comunas de Región de Magallanes a números
COMUNAS_NUMEROS_REGION_12 = {
    "Torres del Paine": "1",
    "Laguna Blanca": "2",
    "San Gregorio": "3"
}

# Mapeo de comunas de Región de Ñuble a números
COMUNAS_NUMEROS_REGION_16 = {
    "Ñiquén": "1",
    "Cobquecura": "2",
    "Quirihue": "3",
    "Treguaco": "4",
    "Coelemu": "5"
}


# ============================================================================
# FUNCIONES DE UTILIDAD Y PREPROCESAMIENTO
# ============================================================================

def normalizar_nombre(nombre):
    """
    Normaliza nombres de comunas para comparación.

    Elimina acentos, caracteres especiales, prefijos comunes y estandariza
    variaciones ortográficas.

    Args:
        nombre (str): Nombre de comuna a normalizar.

    Returns:
        str: Nombre normalizado en minúsculas y sin caracteres especiales.
    """
    if pd.isna(nombre):
        return ""

    nombre_str = str(nombre).lower()

    # Correcciones específicas para nombres problemáticos
    nombre_str = nombre_str.replace("llay-llay", "llaillay")
    nombre_str = nombre_str.replace("cabo de hornos(ex-navarino)", "cabo de hornos")
    nombre_str = nombre_str.replace("trehuaco", "treguaco")

    # Tabla de reemplazos para normalización
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u',
        'puerto ': '', 'las ': '', 'los ': '',
        'el ': '', 'la ': '', 'del ': '',
        ' de ': ' ', ' y ': ' ', "'": '', '"': '',
        '-': ' ', '.': '', ' ': ' '
    }

    for orig, reemp in reemplazos.items():
        nombre_str = nombre_str.replace(orig, reemp)

    return nombre_str.strip()


def cargar_gran_santiago_geojson():
    """
    Carga GeoJSON especializado para el Gran Santiago desde GitHub.

    Returns:
        GeoDataFrame or None: Datos geográficos del Gran Santiago o None si falla.
    """
    print("\n🗺️ CARGANDO GEOJSON ESPECÍFICO DE GRAN SANTIAGO...")

    url = "https://raw.githubusercontent.com/robsalasco/precenso_2016_geojson_chile/master/Extras/GRAN_SANTIAGO.geojson"

    try:
        response = requests.get(url)
        response.raise_for_status()

        gdf_gran_santiago = gpd.read_file(BytesIO(response.content))

        print(f" ✓ GeoJSON de Gran Santiago cargado: {len(gdf_gran_santiago)} elementos")

        # Buscar columna que contiene nombres de comunas
        posibles_columnas_comuna = ['NOM_COM', 'Comuna', 'nombre', 'NOMBRE', 'comuna', 'NOMCOM']
        columna_comuna = None

        for col in posibles_columnas_comuna:
            if col in gdf_gran_santiago.columns:
                columna_comuna = col
                break

        if columna_comuna:
            gdf_gran_santiago['NOM_COM'] = gdf_gran_santiago[columna_comuna]
        else:
            gdf_gran_santiago['NOM_COM'] = [f"Gran Santiago {i}" for i in range(len(gdf_gran_santiago))]

        gdf_gran_santiago['REGION_NUM'] = 13
        gdf_gran_santiago['REGION'] = 13

        gdf_gran_santiago['NOM_COM_NORM'] = gdf_gran_santiago['NOM_COM'].apply(normalizar_nombre)

        print(f" ✓ Gran Santiago preparado con {len(gdf_gran_santiago)} elementos")
        return gdf_gran_santiago

    except Exception as e:
        print(f" ✗ Error cargando GeoJSON de Gran Santiago: {e}")
        print("  Se usará la versión estándar de comunas para la conurbación")
        return None


def cargar_datos_geograficos():
    """
    Carga datos geográficos de comunas chilenas desde múltiples fuentes.

    Intenta cargar archivos locales primero, luego descarga desde GitHub.
    Si todo falla, genera datos básicos de emergencia.

    Returns:
        GeoDataFrame: Datos geográficos de comunas chilenas.

    Raises:
        ValueError: Si los datos geográficos son inválidos.
    """
    print("\n🗺️ CARGANDO DATOS GEOGRÁFICOS...")

    # Lista de archivos locales comunes
    archivos_locales = [
        'comunas_chile.geojson',
        'comunas.geojson',
        'chile_comunas.geojson',
        'chile.geojson',
        'comunas_chile.shp',
        'comunas.json'
    ]

    # Intentar cargar archivos locales
    for archivo in archivos_locales:
        if os.path.exists(archivo):
            try:
                print(f" Cargando archivo local: {archivo}")
                gdf = gpd.read_file(archivo)
                if len(gdf) > 0:
                    print(f" ✓ Datos cargados: {len(gdf)} comunas")
                    if 'geometry' not in gdf.columns or gdf.geometry.is_empty.all():
                        raise ValueError("Datos geográficos inválidos: sin geometrías válidas.")
                    return gdf
            except Exception as e:
                print(f" ✗ Error cargando {archivo}: {e}")

    # Si no hay locales, descargar por región desde GitHub
    print(" No se encontraron archivos locales. Intentando descargar por región desde caracena/chile-geojson...")
    gdfs = []
    for i in range(1, 17):
        url = f"https://raw.githubusercontent.com/caracena/chile-geojson/master/{i}.geojson"
        try:
            gdf_region = gpd.read_file(url)
            print(f" ✓ Cargado región {i}: {len(gdf_region)} comunas")
            if 'Comuna' in gdf_region.columns:
                gdf_region['NOM_COM'] = gdf_region['Comuna']
            if 'cod_comuna' in gdf_region.columns:
                gdf_region['COD_COM'] = gdf_region['cod_comuna']
            if 'codregion' in gdf_region.columns:
                gdf_region['REGION_NUM'] = gdf_region['codregion']
            else:
                gdf_region['REGION_NUM'] = i
            gdfs.append(gdf_region)
        except Exception as e:
            print(f" ✗ Error descargando región {i} desde {url}: {e}")

    # Concatenar regiones descargadas
    if gdfs:
        gdf = pd.concat(gdfs, ignore_index=True)
        gdf = gpd.GeoDataFrame(gdf, crs='EPSG:4326')
        total_comunas = len(gdf)
        print(f" ✓ Datos descargados y concatenados: {total_comunas} comunas totales")
        gdf.to_file('comunas_chile.geojson', driver='GeoJSON')
        print(" ✓ Archivo guardado localmente como 'comunas_chile.geojson'")
        if 'geometry' not in gdf.columns or gdf.geometry.is_empty.all():
            raise ValueError("Datos geográficos inválidos: sin geometrías válidas.")
        return gdf

    # Si todas las descargas fallaron, crear datos básicos
    print(" ⚠ Todas las descargas fallaron. Usando datos básicos (formas cuadradas)")
    return crear_datos_basicos()


def crear_datos_basicos():
    """
    Crea datos geográficos básicos de emergencia cuando no hay datos reales.

    Genera polígonos rectangulares simulados para cada región y comuna.

    Returns:
        GeoDataFrame: Datos geográficos simulados.
    """
    print(" Creando datos básicos de emergencia...")

    from shapely.geometry import Polygon

    # Límites aproximados por región
    region_bounds = {
        1: {"minx": -70.5, "miny": -20.5, "maxx": -68.5, "maxy": -17.5},
        2: {"minx": -71.5, "miny": -25.5, "maxx": -67.5, "maxy": -21.5},
        3: {"minx": -72.5, "miny": -29.5, "maxx": -69.5, "maxy": -25.5},
        4: {"minx": -72.5, "miny": -32.5, "maxx": -69.5, "maxy": -29.5},
        5: {"minx": -73.5, "miny": -34.5, "maxx": -70.5, "maxy": -31.5},
        6: {"minx": -72.5, "miny": -35.5, "maxx": -69.5, "maxy": -33.5},
        7: {"minx": -73.5, "miny": -37.5, "maxx": -70.5, "maxy": -34.5},
        8: {"minx": -74.5, "miny": -39.5, "maxx": -71.5, "maxy": -36.5},
        9: {"minx": -74.5, "miny": -41.5, "maxx": -71.5, "maxy": -38.5},
        10: {"minx": -75.5, "miny": -44.5, "maxx": -71.5, "maxy": -40.5},
        11: {"minx": -76.5, "miny": -48.5, "maxx": -71.5, "maxy": -43.5},
        12: {"minx": -76.5, "miny": -56.5, "maxx": -68.5, "maxy": -51.5},
        13: {"minx": -71.5, "miny": -34.5, "maxx": -69.5, "maxy": -32.5},
        14: {"minx": -74.5, "miny": -41.5, "maxx": -71.5, "maxy": -39.5},
        15: {"minx": -70.5, "miny": -19.5, "maxx": -68.5, "maxy": -17.5},
        16: {"minx": -73.5, "miny": -37.5, "maxx": -71.5, "maxy": -35.5},
    }

    # Nombres de comunas por región
    nombres_comunas = {
        1: ["Iquique", "Alto Hospicio", "Pozo Almonte", "Camiña", "Colchane", "Huara", "Pica"],
        2: ["Antofagasta", "Calama", "Tocopilla", "María Elena", "Mejillones", "Sierra Gorda", "Taltal"],
        3: ["Copiapó", "Caldera", "Chañaral", "Diego de Almagro", "Huasco", "Vallenar", "Freirina"],
        4: ["La Serena", "Coquimbo", "Ovalle", "Illapel", "Vicuña", "Andacollo", "Salamanca"],
        5: ["Valparaíso", "Viña del Mar", "Quilpué", "Villa Alemana", "San Antonio", "Los Andes", "Quillota",
            "Juan Fernández", "Isla de Pascua", "Concón", "Limache", "La Cruz", "Calera", "San Felipe",
            "Panquehue", "Santa María", "Rinconada", "El Quisco", "El Tabo", "Cartagena", "Casablanca",
            "Catemu", "Hijuelas", "La Ligua", "Llay-Llay", "Nogales", "Olmué", "Petorca", "Puchuncaví",
            "Putaendo", "Quillota", "Quintero", "San Antonio", "San Esteban", "Santo Domingo", "Zapallar"],
        6: ["Rancagua", "Machalí", "Graneros", "San Fernando", "Rengo", "Santa Cruz", "Pichilemu",
            "Codegua", "Doñihue", "Olivar", "Coinco", "Quinta de Tilcoco", "Chimbarongo"],
        7: ["Talca", "Curicó", "Linares", "Constitución", "Cauquenes", "Parral", "San Javier",
            "Licantén", "Rauco", "San Rafael", "Río Claro", "Villa Alegre", "Yerbas Buenas", "Curepto"],
        8: ["Concepción", "Talcahuano", "Coronel", "Chiguayante", "Los Ángeles", "Lebu", "Arauco",
            "Hualpén", "Hualqui", "Lota", "Penco", "San Pedro de la Paz", "Tomé", "San Rosendo", "Negrete"],
        9: ["Temuco", "Padre Las Casas", "Villarrica", "Angol", "Victoria", "Pucón", "Lautaro", "Renaico", "Ercilla",
            "Perquenco", "Cholchol", "Nueva Imperial", "Saavedra", "Teodoro Schmidt", "Pitrufquén"],
        10: ["Puerto Montt", "Osorno", "Castro", "Ancud", "Puerto Varas", "Frutillar", "Calbuco",
             "San Juan de la Costa", "Quemchi", "Dalcahue", "Curaco de Vélez", "Puqueldón", "Quinchao", "Queilén"],
        11: ["Coyhaique", "Aysén", "Chile Chico", "Cochrane", "Puerto Aysén", "Puerto Cisnes"],
        12: ["Punta Arenas", "Puerto Natales", "Porvenir", "Cabo de Hornos", "Torres del Paine", "Laguna Blanca",
             "San Gregorio"],
        13: ["Santiago", "Puente Alto", "Maipú", "Las Condes", "Ñuñoa", "La Florida", "San Bernardo"],
        14: ["Valdivia", "La Unión", "Río Bueno", "Panguipulli", "Paillaco", "Los Lagos"],
        15: ["Arica", "Putre", "General Lagos", "Camarones"],
        16: ["Chillán", "Chillán Viejo", "San Carlos", "Bulnes", "Yungay", "Pemuco", "Ñiquén", "Cobquecura", "Quirihue",
             "Treguaco", "Coelemu"]
    }

    regiones_data = []
    for region_num in range(1, 17):
        bounds = region_bounds.get(region_num)
        if not bounds:
            continue

        nombres = nombres_comunas.get(region_num, [f"Comuna {region_num}"])
        num_comunas = len(nombres)
        width = (bounds["maxx"] - bounds["minx"]) / num_comunas if num_comunas > 0 else 1

        # Crear rectángulo para cada comuna
        for i, nombre in enumerate(nombres):
            minx = bounds["minx"] + i * width
            maxx = minx + width
            miny = bounds["miny"]
            maxy = bounds["maxy"]

            polygon = Polygon([
                [minx, miny],
                [maxx, miny],
                [maxx, maxy],
                [minx, maxy],
                [minx, miny]
            ])

            regiones_data.append({
                'COD_COM': f'{region_num:02d}{i + 1:03d}',
                'NOM_COM': nombre,
                'REGION': region_num,
                'geometry': polygon
            })

    gdf = gpd.GeoDataFrame(regiones_data, crs='EPSG:4326')
    gdf['REGION_NUM'] = gdf['REGION']

    print(f" ✓ Datos básicos creados: {len(gdf)} comunas simuladas")
    return gdf


def procesar_csv(csv_path):
    """
    Procesa archivo CSV con datos electorales.

    Args:
        csv_path (str): Ruta al archivo CSV.

    Returns:
        DataFrame: Datos electorales procesados.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si faltan columnas requeridas.
    """
    print(f"\n📊 PROCESANDO DATOS ELECTORALES...")
    print(f" Cargando CSV: {csv_path}")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")

    # Intentar diferentes codificaciones
    codificaciones = ['utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8']

    for encoding in codificaciones:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f" ✓ CSV cargado con encoding: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    else:
        df = pd.read_csv(csv_path)
        print(" ✓ CSV cargado (encoding automático)")

    print(f" Filas: {len(df)}")
    print(f" Columnas: {list(df.columns)}")

    # Normalizar nombres de columnas
    df.columns = [str(col).strip().lower() for col in df.columns]

    # Mapeo de nombres de columnas alternativos a estandarizados
    mapeo_columnas = {
        'comuna': ['comuna', 'nombre comuna', 'comuna_nombre', 'nombre_comuna'],
        'region': ['region', 'región', 'nombre_region', 'region_nombre'],
        'jara_votos': ['jara_votos', 'jara votos', 'votos jara'],
        'jara_pct': ['jara_pct', 'jara %', 'jara%', 'jara pct'],
        'kast_votos': ['kast_votos', 'kast votos', 'votos kast'],
        'kast_pct': ['kast_pct', 'kast %', 'kast%', 'kast pct'],
        'blanco_votos': ['blanco_votos', 'blanco votos', 'votos blanco', 'blancos'],
        'nulo_votos': ['nulo_votos', 'nulo votos', 'votos nulo', 'nulos'],
        'emitidos_votos': ['emitidos_votos', 'emitidos votos', 'votos emitidos', 'total votos', 'votos_total']
    }

    for col_estandar, alternativas in mapeo_columnas.items():
        for alt in alternativas:
            if alt in df.columns:
                df = df.rename(columns={alt: col_estandar})
                print(f" ✓ Renombrada '{alt}' -> '{col_estandar}'")
                break

    # Verificar columnas requeridas
    columnas_requeridas = ['comuna', 'jara_pct', 'kast_pct']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Columna requerida no encontrada: '{col}'")

    # Limpiar datos de texto
    df['comuna'] = df['comuna'].astype(str).str.strip()

    if 'region' in df.columns:
        df['region'] = df['region'].astype(str).str.strip()

    # Convertir columnas numéricas
    columnas_numericas = ['jara_pct', 'kast_pct', 'jara_votos', 'kast_votos',
                          'blanco_votos', 'nulo_votos', 'emitidos_votos']

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calcular votos si solo hay porcentajes
    if 'jara_votos' not in df.columns and 'jara_pct' in df.columns and 'emitidos_votos' in df.columns:
        print(" Calculando votos de Jara a partir de porcentajes...")
        df['jara_votos'] = (df['jara_pct'] / 100) * df['emitidos_votos']

    if 'kast_votos' not in df.columns and 'kast_pct' in df.columns and 'emitidos_votos' in df.columns:
        print(" Calculando votos de Kast a partir de porcentajes...")
        df['kast_votos'] = (df['kast_pct'] / 100) * df['emitidos_votos']

    # Calcular diferencia porcentual
    df['diferencia_pct'] = df['jara_pct'] - df['kast_pct']

    # Calcular votos válidos si hay datos suficientes
    if all(col in df.columns for col in ['emitidos_votos', 'blanco_votos', 'nulo_votos']):
        print(" Calculando votos válidos...")
        df['validos_votos'] = df['emitidos_votos'] - df['blanco_votos'] - df['nulo_votos']

    # Validar porcentajes (deben estar entre 0 y 100)
    invalid_rows = df[(df['jara_pct'] < 0) | (df['jara_pct'] > 100) | (df['kast_pct'] < 0) | (df['kast_pct'] > 100)]
    if not invalid_rows.empty:
        print(f" ⚠ Filas con porcentajes inválidos (>100 o <0): {len(invalid_rows)}")
        df.loc[invalid_rows.index, ['jara_pct', 'kast_pct']] = np.nan

    # Función auxiliar para mapear nombres de región a números
    def mapear_region(nombre):
        """Mapea nombre textual de región a número."""
        if pd.isna(nombre):
            return None

        nombre_str = str(nombre).strip()

        # Búsqueda exacta
        for region_csv, num in NOMBRES_CSV_A_NUM.items():
            if nombre_str.lower() == region_csv.lower():
                return num

        # Búsqueda parcial
        for region_csv, num in NOMBRES_CSV_A_NUM.items():
            if region_csv.lower() in nombre_str.lower():
                return num

        print(f" ⚠ No se pudo mapear región: '{nombre_str}'")
        return None

    # Mapear regiones del CSV
    if 'region' in df.columns:
        print("\n Mapeando regiones del CSV a números:")
        regiones_unicas = df['region'].unique()
        for region in regiones_unicas:
            region_num = mapear_region(region)
            print(f" '{region}' -> {region_num}")

        df['REGION_NUM'] = df['region'].apply(mapear_region)
    else:
        df['REGION_NUM'] = None

    # Normalizar nombres de comunas para matching
    df['NOM_COM_NORM'] = df['comuna'].apply(normalizar_nombre)

    # Estadísticas del CSV
    comunas_con_datos = df['diferencia_pct'].notna().sum()
    dif_promedio = df['diferencia_pct'].mean() if comunas_con_datos > 0 else 0

    print(f"\n 📈 ESTADÍSTICAS DEL CSV:")
    print(f" Total comunas: {len(df)}")
    print(f" Comunas con datos: {comunas_con_datos}")
    print(f" Diferencia promedio: {dif_promedio:.2f}%")
    print(f" Jara gana en: {(df['diferencia_pct'] > 0).sum()} comunas")
    print(f" Kast gana en: {(df['diferencia_pct'] < 0).sum()} comunas")

    print(f" Columnas disponibles: {list(df.columns)}")

    return df


def unir_datos(comunas, df_electoral):
    """
    Une datos geográficos con datos electorales.

    Args:
        comunas (GeoDataFrame): Datos geográficos de comunas.
        df_electoral (DataFrame): Datos electorales procesados.

    Returns:
        GeoDataFrame: Datos combinados con geometrías y resultados electorales.
    """
    print("\n🔄 UNIENDO DATOS GEOGRÁFICOS Y ELECTORALES...")

    # Asegurar columna REGION_NUM en datos geográficos
    if 'REGION_NUM' not in comunas.columns and 'REGION' in comunas.columns:
        comunas['REGION_NUM'] = comunas['REGION']

    # Normalizar nombres de comunas en ambos datasets
    comunas['NOM_COM_NORM'] = comunas['NOM_COM'].apply(normalizar_nombre)

    # Mostrar ejemplos de normalización para debugging
    print(" 🔍 Ejemplos de normalización (geográficas vs electorales):")
    min_samples = min(5, len(comunas), len(df_electoral))
    for i in range(min_samples):
        print(f" Geo: '{comunas.iloc[i]['NOM_COM']}' -> '{comunas.iloc[i]['NOM_COM_NORM']}'")
        print(f" CSV: '{df_electoral.iloc[i]['comuna']}' -> '{df_electoral.iloc[i]['NOM_COM_NORM']}'")

    # Realizar merge por nombre normalizado y región
    print(" Realizando merge...")
    mapa_data = comunas.merge(
        df_electoral,
        left_on=['NOM_COM_NORM', 'REGION_NUM'],
        right_on=['NOM_COM_NORM', 'REGION_NUM'],
        how='left'
    )

    # Si no hay REGION_NUM, intentar merge solo por nombre
    if 'REGION_NUM' not in mapa_data.columns:
        mapa_data = comunas.merge(
            df_electoral,
            left_on='NOM_COM_NORM',
            right_on='NOM_COM_NORM',
            how='left'
        )

    # Gestionar columnas de región duplicadas
    if 'REGION_NUM_x' in mapa_data.columns:
        mapa_data['REGION_NUM'] = mapa_data['REGION_NUM_x']
    elif 'REGION_NUM_y' in mapa_data.columns:
        mapa_data['REGION_NUM'] = mapa_data['REGION_NUM_y']
    elif 'REGION_NUM' not in mapa_data.columns and 'REGION' in mapa_data.columns:
        mapa_data['REGION_NUM'] = mapa_data['REGION']

    # Si aún no hay REGION_NUM, intentar extraer de código de comuna
    if 'REGION_NUM' not in mapa_data.columns and 'COD_COM' in mapa_data.columns:
        def extraer_region_de_codigo(codigo):
            try:
                cod_str = str(codigo)
                if len(cod_str) >= 2:
                    return int(cod_str[:2])
            except:
                return None

        mapa_data['REGION_NUM'] = mapa_data['COD_COM'].apply(extraer_region_de_codigo)

    # Si todo falla, asignar Región Metropolitana como predeterminada
    if 'REGION_NUM' not in mapa_data.columns or mapa_data['REGION_NUM'].isna().all():
        mapa_data['REGION_NUM'] = 13

    # Asegurar tipo numérico
    mapa_data['REGION_NUM'] = pd.to_numeric(mapa_data['REGION_NUM'], errors='coerce').fillna(13).astype(int)

    # Identificar comunas sin datos
    sin_datos = mapa_data[mapa_data['diferencia_pct'].isna()]['NOM_COM'].tolist()
    if sin_datos:
        print(
            f" ⚠ Comunas sin datos electorales (posibles mismatches): {len(sin_datos)} - Ejemplos: {sin_datos[:5]}...")

    # Estadísticas de la unión
    comunas_con_datos = mapa_data['diferencia_pct'].notna().sum() if 'diferencia_pct' in mapa_data.columns else 0
    total_comunas = len(mapa_data)

    print(f"\n ✅ UNIÓN COMPLETADA:")
    print(f" Total comunas geográficas: {len(comunas)}")
    print(f" Total comunas electorales: {len(df_electoral)}")
    print(f" Comunas con datos después del merge: {comunas_con_datos} ({comunas_con_datos / total_comunas * 100:.1f}%)")

    # Estadísticas de resultados si hay datos
    if comunas_con_datos > 0 and 'diferencia_pct' in mapa_data.columns:
        jara_gana = (mapa_data['diferencia_pct'] > 0).sum()
        kast_gana = (mapa_data['diferencia_pct'] < 0).sum()
        empates = (mapa_data['diferencia_pct'] == 0).sum()

        print(f" Jara gana en: {jara_gana} comunas")
        print(f" Kast gana en: {kast_gana} comunas")
        print(f" Empates: {empates} comunas")

    return mapa_data


# ============================================================================
# FUNCIONES PARA AGREGAR ETIQUETAS A MAPAS
# ============================================================================

def agregar_nombres_comunas(ax, region_data, fontsize=7, exclude_comunas=None):
    """
    Agrega nombres de comunas a un mapa.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la región.
        fontsize (int): Tamaño de fuente para etiquetas.
        exclude_comunas (list): Lista de nombres de comunas a excluir.
    """
    print(f"  Agregando nombres de comunas (tamaño fuente: {fontsize})...")

    if exclude_comunas is None:
        exclude_comunas = []

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])
                if comuna_nombre in exclude_comunas:
                    continue

                point = row['geometry'].representative_point()

                nombre_comuna = comuna_nombre

                # Acortar nombres largos
                max_length = 20 if fontsize <= 7 else 25

                if len(nombre_comuna) > max_length:
                    if "de la" in nombre_comuna:
                        nombre_comuna = nombre_comuna.replace("de la ", "")
                    elif "del " in nombre_comuna:
                        nombre_comuna = nombre_comuna.replace("del ", "")
                    elif "de " in nombre_comuna:
                        nombre_comuna = nombre_comuna.replace("de ", "")
                    elif "General " in nombre_comuna:
                        nombre_comuna = nombre_comuna.replace("General ", "Gral. ")

                # Determinar color de texto basado en color de fondo
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255

                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b

                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                bbox_alpha = 0.6 if fontsize <= 7 else 0.7

                # Agregar texto con fondo semitransparente
                ax.text(point.x, point.y, nombre_comuna,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight='normal',
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=bbox_alpha))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Nombres de comunas agregados: {nombres_agregados}")


def agregar_etiquetas_region_metropolitana(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región Metropolitana.

    Usa números para comunas pequeñas y nombres para otras.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región Metropolitana.
    """
    print(f"  Agregando etiquetas especiales para Región Metropolitana...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta (número o texto)
                if comuna_nombre in COMUNAS_NUMEROS_RM:
                    etiqueta = COMUNAS_NUMEROS_RM[comuna_nombre]
                    fontsize = TAMANOS_FUENTE_AREAS_METROPOLITANAS['region_metropolitana_numeros']
                    fontweight = 'normal'
                elif comuna_nombre in COMUNAS_ETIQUETAS_RM:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = TAMANOS_FUENTE_AREAS_METROPOLITANAS['region_metropolitana_etiquetas']
                    fontweight = 'normal'
                else:
                    continue

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Ajustes de posición para comunas específicas
                offset_x = 0
                offset_y = 0

                if comuna_nombre == "Lo Barnechea":
                    offset_y = 0.01
                elif comuna_nombre == "Colina":
                    offset_x = 0.005
                elif comuna_nombre == "Lampa":
                    offset_y = -0.005
                elif comuna_nombre == "Curacaví":
                    offset_x = -0.008
                elif comuna_nombre == "María Pinto":
                    offset_y = 0.008
                elif comuna_nombre == "Melipilla":
                    offset_x = 0.01
                elif comuna_nombre == "San José de Maipo":
                    offset_x = -0.01

                # Agregar etiqueta
                ax.text(point.x + offset_x, point.y + offset_y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región Metropolitana agregadas: {nombres_agregados}")


def agregar_etiquetas_gran_santiago(ax, region_data, usar_numeros=True):
    """
    Agrega etiquetas especiales para el Gran Santiago.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos del Gran Santiago.
        usar_numeros (bool): Si True, usa números en lugar de nombres.
    """
    print(f"  Agregando etiquetas especiales para Gran Santiago...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar etiqueta (número o texto)
                if usar_numeros and comuna_nombre in MAQUEO_COMUNAS_NUMEROS:
                    etiqueta = MAQUEO_COMUNAS_NUMEROS[comuna_nombre]
                    fontsize = 15
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 15

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight='normal',
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales agregadas: {nombres_agregados}")


def agregar_etiquetas_region_5_valparaiso(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región de Valparaíso.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región de Valparaíso.
    """
    print(f"  Agregando etiquetas especiales para Región 5 (Valparaíso)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_5:
                    etiqueta = COMUNAS_NUMEROS_REGION_5[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 5 (Valparaíso) agregadas: {nombres_agregados}")


def agregar_etiquetas_region_6_ohiggins(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región de O'Higgins.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región de O'Higgins.
    """
    print(f"  Agregando etiquetas especiales para Región 6 (O'Higgins)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_6:
                    etiqueta = COMUNAS_NUMEROS_REGION_6[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 6 (O'Higgins) agregadas: {nombres_agregados}")


def agregar_etiquetas_region_7_maule(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región del Maule.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región del Maule.
    """
    print(f"  Agregando etiquetas especiales para Región 7 (Maule)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_7:
                    etiqueta = COMUNAS_NUMEROS_REGION_7[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 7 (Maule) agregadas: {nombres_agregados}")


def agregar_etiquetas_region_8_biobio(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región del Biobío.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región del Biobío.
    """
    print(f"  Agregando etiquetas especiales para Región 8 (Biobío)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_8:
                    etiqueta = COMUNAS_NUMEROS_REGION_8[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 8 (Biobío) agregadas: {nombres_agregados}")


def agregar_etiquetas_region_9_araucania(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región de la Araucanía.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región de la Araucanía.
    """
    print(f"  Agregando etiquetas especiales para Región 9 (Araucanía)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_9:
                    etiqueta = COMUNAS_NUMEROS_REGION_9[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 9 (Araucanía) agregadas: {nombres_agregados}")


def agregar_etiquetas_region_10_loslagos(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región de Los Lagos.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región de Los Lagos.
    """
    print(f"  Agregando etiquetas especiales para Región 10 (Los Lagos)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_10:
                    etiqueta = COMUNAS_NUMEROS_REGION_10[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 10 (Los Lagos) agregadas: {nombres_agregados}")


def agregar_etiquetas_region_12_magallanes(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región de Magallanes.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región de Magallanes.
    """
    print(f"  Agregando etiquetas especiales para Región 12 (Magallanes)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_12:
                    etiqueta = COMUNAS_NUMEROS_REGION_12[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 12 (Magallanes) agregadas: {nombres_agregados}")


def agregar_etiquetas_region_16_nuble(ax, region_data):
    """
    Agrega etiquetas especiales para comunas de la Región de Ñuble.

    Args:
        ax (matplotlib.axes.Axes): Ejes donde dibujar.
        region_data (GeoDataFrame): Datos de la Región de Ñuble.
    """
    print(f"  Agregando etiquetas especiales para Región 16 (Ñuble)...")

    nombres_agregados = 0
    for idx, row in region_data.iterrows():
        try:
            if 'NOM_COM' in row and row['NOM_COM'] and 'geometry' in row and row['geometry']:
                comuna_nombre = str(row['NOM_COM'])

                point = row['geometry'].representative_point()

                # Determinar tipo de etiqueta
                if comuna_nombre in COMUNAS_NUMEROS_REGION_16:
                    etiqueta = COMUNAS_NUMEROS_REGION_16[comuna_nombre]
                    fontsize = 9
                    fontweight = 'normal'
                else:
                    etiqueta = comuna_nombre
                    if len(etiqueta) > 15:
                        etiqueta = etiqueta[:12] + '...'
                    fontsize = 9
                    fontweight = 'normal'

                # Determinar color de texto
                if 'color' in row:
                    color_hex = row['color']
                    if color_hex.startswith('#'):
                        r = int(color_hex[1:3], 16) / 255
                        g = int(color_hex[3:5], 16) / 255
                        b = int(color_hex[5:7], 16) / 255
                        luminosidad = 0.299 * r + 0.587 * g + 0.114 * b
                        text_color = 'white' if luminosidad < 0.5 else 'black'
                    else:
                        text_color = 'black'
                else:
                    text_color = 'black'

                # Agregar etiqueta
                ax.text(point.x, point.y, etiqueta,
                        fontsize=fontsize,
                        ha='center', va='center',
                        color=text_color,
                        fontweight=fontweight,
                        bbox=dict(boxstyle="round,pad=0.3",
                                  facecolor='white' if text_color == 'black' else 'black',
                                  edgecolor='none',
                                  alpha=0.7))
                nombres_agregados += 1
        except Exception as e:
            continue

    print(f"  ✓ Etiquetas especiales para Región 16 (Ñuble) agregadas: {nombres_agregados}")


def calcular_promedio_regional_correcto(region_data):
    """
    Calcula el promedio regional corregido usando votos válidos.

    Args:
        region_data (GeoDataFrame): Datos de la región.

    Returns:
        tuple: Porcentaje de Jara y Kast en la región.
    """
    columnas_necesarias = ['jara_votos', 'kast_votos', 'emitidos_votos', 'blanco_votos', 'nulo_votos']

    if all(col in region_data.columns for col in columnas_necesarias):
        print("  Calculando promedio regional usando votos válidos...")

        total_jara = region_data['jara_votos'].sum()
        total_kast = region_data['kast_votos'].sum()
        total_emitidos = region_data['emitidos_votos'].sum()
        total_blanco = region_data['blanco_votos'].sum()
        total_nulo = region_data['nulo_votos'].sum()

        total_validos = total_emitidos - total_blanco - total_nulo

        if total_validos > 0:
            jara_promedio_regional = (total_jara / total_validos) * 100
            kast_promedio_regional = (total_kast / total_validos) * 100

            print(f"  Total votos válidos regional: {total_validos:.0f}")
            print(f"  Jara regional: {total_jara:.0f} votos ({jara_promedio_regional:.1f}%)")
            print(f"  Kast regional: {total_kast:.0f} votos ({kast_promedio_regional:.1f}%)")
            print(f"  Diferencia regional calculada: {jara_promedio_regional - kast_promedio_regional:.1f}%")

            return jara_promedio_regional, kast_promedio_regional

    print("  Usando promedio simple de porcentajes (datos de votos incompletos)")
    if 'jara_pct' in region_data.columns and 'kast_pct' in region_data.columns:
        jara_promedio = region_data['jara_pct'].mean()
        kast_promedio = region_data['kast_pct'].mean()
        return jara_promedio, kast_promedio

    return 0, 0


# ============================================================================
# FUNCIONES PARA CREAR MAPAS REGIONALES
# ============================================================================

def crear_mapa_regional_completo(region_num, mapa_data, output_dir):
    """
    Crea un mapa regional completo con estadísticas.

    Args:
        region_num (int): Número de región (1-16).
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    region_nombre = REGIONES_NOMBRES_TITULOS.get(region_num, f"Región {region_num}")
    print(f" 🗺️ Generando mapa para {region_nombre}")

    if 'REGION_NUM' not in mapa_data.columns:
        print(f" ❌ ERROR: No hay columna REGION_NUM en los datos")
        return None

    # Filtrar datos de la región
    region_data = mapa_data[mapa_data['REGION_NUM'] == region_num].copy()

    if region_data.empty:
        print(f" ⚠ No hay datos para {region_nombre}")
        return None

    # Excluir islas de la Región de Valparaíso
    islas_note = ""
    if region_num == 5:
        islands = ['Juan Fernández', 'Isla de Pascua', 'Rapa Nui', 'Easter Island']
        region_data = region_data[~region_data['NOM_COM'].str.contains('|'.join(islands), case=False, na=False)]
        islas_note = " (Islas excluidas, ver mapa separado)"

    # Verificar datos electorales
    comunas_con_datos = 0
    if 'diferencia_pct' in region_data.columns:
        comunas_con_datos = region_data['diferencia_pct'].notna().sum()

    if comunas_con_datos == 0:
        print(f" ⚠ No hay datos electorales para {region_nombre}")

    # Configurar tamaño de figura según región
    if region_num in [5, 6, 7, 8, 9, 10, 12, 13, 16]:
        fig = plt.figure(figsize=(18, 16))
        gs = GridSpec(4, 2, figure=fig, height_ratios=[0.05, 0.75, 0.15, 0.05],
                      width_ratios=[0.65, 0.35], hspace=0.12, wspace=0.08)
    else:
        fig = plt.figure(figsize=(18, 14))
        gs = GridSpec(3, 2, figure=fig, height_ratios=[0.05, 0.90, 0.05],
                      width_ratios=[0.65, 0.35], hspace=0.08, wspace=0.08)

    # Título
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    titulo_texto = f'{region_nombre}{islas_note}'
    ax_titulo.text(0.5, 0.5, titulo_texto, ha='center', va='center',
                   fontsize=22, fontweight='bold', transform=ax_titulo.transAxes)

    # Mapa
    ax_mapa = fig.add_subplot(gs[1, 0])

    # Asignar colores según diferencia
    if 'diferencia_pct' in region_data.columns:
        region_data['color'] = region_data['diferencia_pct'].apply(asignar_color_diferencia)
    else:
        region_data['color'] = '#D3D3D3'

    # Dibujar mapa
    try:
        region_data.plot(ax=ax_mapa, color=region_data['color'], edgecolor='black', linewidth=0.5)
    except Exception as e:
        print(f" ⚠ Error dibujando mapa: {e}")
        # Dibujar comunas individualmente si falla el plot colectivo
        for idx, row in region_data.iterrows():
            if hasattr(row, 'geometry') and row.geometry is not None:
                try:
                    gpd.GeoSeries([row.geometry]).plot(ax=ax_mapa, color=row['color'],
                                                       edgecolor='black', linewidth=0.5)
                except:
                    continue

    # Agregar etiquetas según región
    fontsize_regional = TAMANOS_FUENTE_REGION.get(region_num, 7)

    if region_num == 13:
        agregar_etiquetas_region_metropolitana(ax_mapa, region_data)
    elif region_num == 5:
        agregar_etiquetas_region_5_valparaiso(ax_mapa, region_data)
    elif region_num == 6:
        agregar_etiquetas_region_6_ohiggins(ax_mapa, region_data)
    elif region_num == 7:
        agregar_etiquetas_region_7_maule(ax_mapa, region_data)
    elif region_num == 8:
        agregar_etiquetas_region_8_biobio(ax_mapa, region_data)
    elif region_num == 9:
        agregar_etiquetas_region_9_araucania(ax_mapa, region_data)
    elif region_num == 10:
        agregar_etiquetas_region_10_loslagos(ax_mapa, region_data)
    elif region_num == 12:
        agregar_etiquetas_region_12_magallanes(ax_mapa, region_data)
    elif region_num == 16:
        agregar_etiquetas_region_16_nuble(ax_mapa, region_data)
    else:
        agregar_nombres_comunas(ax_mapa, region_data, fontsize=fontsize_regional)

    ax_mapa.set_axis_off()
    ax_mapa.set_aspect('equal')

    # Panel de estadísticas
    ax_stats_container = fig.add_subplot(gs[1, 1])
    ax_stats_container.set_axis_off()

    stats_gs = GridSpecFromSubplotSpec(4, 1, subplot_spec=gs[1, 1],
                                       height_ratios=[0.50, 0.25, 0.15, 0.10], hspace=0.15)

    # Calcular estadísticas
    jara_promedio = kast_promedio = 0
    jara_gana = kast_gana = empates = 0
    dif_promedio = 0

    if comunas_con_datos > 0:
        jara_promedio, kast_promedio = calcular_promedio_regional_correcto(region_data)
        dif_promedio = jara_promedio - kast_promedio

        jara_gana = (region_data['diferencia_pct'] > 0).sum()
        kast_gana = (region_data['diferencia_pct'] < 0).sum()
        empates = (region_data['diferencia_pct'] == 0).sum()

    # Gráfico de barras
    ax_barras = fig.add_subplot(stats_gs[0])

    if comunas_con_datos > 0:
        candidatos = ['JARA', 'KAST']
        porcentajes = [jara_promedio, kast_promedio]
        colores_barras = ['#E54540', '#2D426C']

        bars = ax_barras.bar(candidatos, porcentajes, color=colores_barras,
                             edgecolor='black', width=0.6)

        fontsize_ylabel = 11
        fontsize_title = 13
        fontsize_bars = 11
        fontsize_ticks = 10

        ax_barras.set_ylabel('Porcentaje (%)', fontsize=fontsize_ylabel, fontweight='bold')
        ax_barras.set_title('PROMEDIO REGIONAL', fontsize=fontsize_title, fontweight='bold', pad=10)

        max_porcentaje = max(porcentajes) if len(porcentajes) > 0 else 100
        ax_barras.set_ylim(0, max_porcentaje * 1.25)

        ax_barras.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        for bar in bars:
            height = bar.get_height()
            ax_barras.text(bar.get_x() + bar.get_width() / 2.,
                           height + (max_porcentaje * 0.02),
                           f'{height:.1f}%',
                           ha='center', va='bottom',
                           fontsize=fontsize_bars, fontweight='bold')
    else:
        ax_barras.text(0.5, 0.5, 'SIN DATOS',
                       ha='center', va='center',
                       transform=ax_barras.transAxes,
                       fontsize=14, fontweight='bold',
                       color='gray')
        ax_barras.set_title('PROMEDIO REGIONAL', fontsize=13, fontweight='bold', pad=10)

    ax_barras.grid(axis='y', alpha=0.3)
    ax_barras.tick_params(axis='both', labelsize=10)

    # Estadísticas de comunas
    ax_comunas = fig.add_subplot(stats_gs[1])
    ax_comunas.set_axis_off()

    if comunas_con_datos > 0:
        total_comunas = len(region_data)
        sin_datos = total_comunas - comunas_con_datos

        fontsize_stats = 10

        stats_text = (f"COMUNAS CON DATOS: {comunas_con_datos}/{total_comunas}\n\n"
                      f"JARA gana en: {jara_gana} comunas\n"
                      f"KAST gana en: {kast_gana} comunas\n"
                      f"Empates: {empates} comunas")

        if sin_datos > 0:
            stats_text += f"\nSin datos: {sin_datos} comunas"

        ax_comunas.text(0.05, 0.9, stats_text,
                        ha='left', va='top',
                        fontsize=fontsize_stats,
                        transform=ax_comunas.transAxes,
                        linespacing=1.5)
    else:
        ax_comunas.text(0.5, 0.5, 'NO HAY DATOS ELECTORALES\nPARA ESTA REGIÓN',
                        ha='center', va='center',
                        fontsize=11, fontweight='bold',
                        transform=ax_comunas.transAxes,
                        color='gray')

    # Diferencia promedio
    ax_diferencia = fig.add_subplot(stats_gs[2])
    ax_diferencia.set_axis_off()

    if comunas_con_datos > 0:
        color_dif = '#E54540' if dif_promedio > 0 else '#2D426C' if dif_promedio < 0 else 'gray'

        fontsize_dif = 12
        fontsize_info = 9

        dif_text = (f"DIFERENCIA PROMEDIO REGIONAL\n"
                    f"{dif_promedio:+.1f}%")

        ax_diferencia.text(0.5, 0.7, dif_text,
                           ha='center', va='center',
                           fontsize=fontsize_dif, fontweight='bold',
                           color=color_dif,
                           transform=ax_diferencia.transAxes)

        info_text = f"Jara {jara_promedio:.1f}% - Kast {kast_promedio:.1f}%"
        ax_diferencia.text(0.5, 0.3, info_text,
                           ha='center', va='center',
                           fontsize=fontsize_info,
                           color='gray',
                           transform=ax_diferencia.transAxes)
    else:
        ax_diferencia.text(0.5, 0.7, 'DIFERENCIA PROMEDIO\nN/A',
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color='gray',
                           transform=ax_diferencia.transAxes)

    # Escala de colores
    ax_escala = fig.add_subplot(stats_gs[3])

    norm = plt.Normalize(-100, 100)
    sm = ScalarMappable(cmap=cmap_continuo, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=ax_escala, orientation='horizontal', fraction=0.9)
    cbar.set_label('Diferencia (Jara% - Kast%)', fontsize=8, fontweight='bold', labelpad=3)

    ticks = [-100, -50, -10, 0, 10, 50, 100]
    tick_labels = ['-100', '-50', '-10', '0', '10', '50', '+100']

    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)
    cbar.ax.tick_params(labelsize=6)

    # Simbología para regiones con números
    if region_num in [5, 6, 7, 8, 9, 10, 12, 13, 16]:
        ax_simbologia = fig.add_subplot(gs[2, :])
        ax_simbologia.set_axis_off()

        ax_simbologia.text(0.5, 0.85, 'Simbología - Comunas con número',
                           ha='center', va='top',
                           fontsize=14, fontweight='bold',
                           transform=ax_simbologia.transAxes)

        # Seleccionar diccionario de comunas según región
        if region_num == 5:
            comunas_dict = COMUNAS_NUMEROS_REGION_5
        elif region_num == 6:
            comunas_dict = COMUNAS_NUMEROS_REGION_6
        elif region_num == 7:
            comunas_dict = COMUNAS_NUMEROS_REGION_7
        elif region_num == 8:
            comunas_dict = COMUNAS_NUMEROS_REGION_8
        elif region_num == 9:
            comunas_dict = COMUNAS_NUMEROS_REGION_9
        elif region_num == 10:
            comunas_dict = COMUNAS_NUMEROS_REGION_10
        elif region_num == 12:
            comunas_dict = COMUNAS_NUMEROS_REGION_12
        elif region_num == 13:
            comunas_dict = COMUNAS_NUMEROS_RM
        elif region_num == 16:
            comunas_dict = COMUNAS_NUMEROS_REGION_16
        else:
            comunas_dict = {}

        # Mostrar simbología en dos columnas
        items = list(comunas_dict.items())
        if items:
            mitad = len(items) // 2 + len(items) % 2

            for i, (comuna, numero) in enumerate(items[:mitad]):
                y_pos = 0.70 - i * 0.08
                ax_simbologia.text(0.25, y_pos, f'{numero}. {comuna}',
                                   ha='left', va='center',
                                   fontsize=11,
                                   transform=ax_simbologia.transAxes)

            for i, (comuna, numero) in enumerate(items[mitad:]):
                y_pos = 0.70 - i * 0.08
                ax_simbologia.text(0.65, y_pos, f'{numero}. {comuna}',
                                   ha='left', va='center',
                                   fontsize=11,
                                   transform=ax_simbologia.transAxes)

        ax_simbologia.text(0.5, 0.20,
                           'Nota: Las comunas con números son demasiado pequeñas para mostrar su nombre completo.',
                           ha='center', va='center',
                           fontsize=9, style='italic', color='gray',
                           transform=ax_simbologia.transAxes)

    # Pie de página
    if region_num in [5, 6, 7, 8, 9, 10, 12, 13, 16]:
        ax_fondo = fig.add_subplot(gs[3, :])
    else:
        ax_fondo = fig.add_subplot(gs[2, :])

    ax_fondo.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | {region_nombre} | Generado: {fecha}"
    ax_fondo.text(0.5, 0.5, info_text,
                  ha='center', va='center',
                  fontsize=8, color='gray',
                  transform=ax_fondo.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])

    # Guardar archivo
    region_num_str = str(region_num).zfill(2)
    region_nombre_safe = REGIONES_ANTIGUAS_NUM.get(region_num, f"Region_{region_num}").replace(' ', '_').replace('á',
                                                                                                                 'a').replace(
        'é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n').replace('Ñ', 'N').replace("'",
                                                                                                                    '').replace(
        '"', '').replace("'", '').replace('O\'', 'O_')

    output_path = os.path.join(output_dir, f"REGION_{region_num_str}_{region_nombre_safe}_COMPLETO.png")

    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Mapa guardado: {output_path}")
    return output_path


# ============================================================================
# FUNCIONES PARA MAPAS DE ISLAS
# ============================================================================

def crear_mapa_isla_pascua(mapa_data, output_dir):
    """
    Crea mapa separado para Isla de Pascua (Rapa Nui).

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 🗺️ Generando mapa separado para Isla de Pascua (Rapa Nui) - SOLO ISLA PRINCIPAL")

    islands_data = mapa_data[
        mapa_data['NOM_COM'].str.contains('Isla de Pascua|Rapa Nui', case=False, na=False)].copy()

    if islands_data.empty:
        print(f" ⚠ No hay datos para Isla de Pascua")
        return None

    # Límites geográficos para Isla de Pascua
    rapa_nui_bounds = {
        'minx': -109.5,
        'miny': -27.2,
        'maxx': -109.2,
        'maxy': -27.0
    }

    # Verificar datos electorales
    comunas_con_datos = 0
    if 'diferencia_pct' in islands_data.columns:
        comunas_con_datos = islands_data['diferencia_pct'].notna().sum()

    if comunas_con_datos == 0:
        print(f" ⚠ No hay datos electorales para Isla de Pascua")

    # Configurar figura
    fig = plt.figure(figsize=(14, 10))

    gs = GridSpec(3, 2, figure=fig, height_ratios=[0.05, 0.90, 0.05],
                  width_ratios=[0.70, 0.30], hspace=0.08, wspace=0.08)

    # Título
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'Isla de Pascua (Rapa Nui) - Comuna de Isla de Pascua',
                   ha='center', va='center', fontsize=18, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Mapa
    ax_mapa = fig.add_subplot(gs[1, 0])

    if 'diferencia_pct' in islands_data.columns:
        islands_data['color'] = islands_data['diferencia_pct'].apply(asignar_color_diferencia)
    else:
        islands_data['color'] = '#D3D3D3'

    # Dibujar mapa con límites específicos
    try:
        islands_data.plot(ax=ax_mapa, color=islands_data['color'], edgecolor='black', linewidth=0.5)

        ax_mapa.set_xlim(rapa_nui_bounds['minx'], rapa_nui_bounds['maxx'])
        ax_mapa.set_ylim(rapa_nui_bounds['miny'], rapa_nui_bounds['maxy'])

    except Exception as e:
        print(f" ⚠ Error dibujando mapa de Isla de Pascua: {e}")
        for idx, row in islands_data.iterrows():
            if hasattr(row, 'geometry') and row.geometry is not None:
                try:
                    gpd.GeoSeries([row.geometry]).plot(ax=ax_mapa, color=row['color'],
                                                       edgecolor='black', linewidth=0.5)
                except:
                    continue

    # Agregar nombres
    agregar_nombres_comunas(ax_mapa, islands_data, fontsize=12)

    ax_mapa.set_axis_off()
    ax_mapa.set_aspect('equal')

    # Panel de estadísticas
    ax_stats_container = fig.add_subplot(gs[1, 1])
    ax_stats_container.set_axis_off()

    stats_gs = GridSpecFromSubplotSpec(4, 1, subplot_spec=gs[1, 1],
                                       height_ratios=[0.5, 0.25, 0.15, 0.10], hspace=0.15)

    # Calcular estadísticas
    jara_promedio = kast_promedio = 0
    jara_gana = kast_gana = empates = 0
    dif_promedio = 0

    if comunas_con_datos > 0:
        jara_promedio, kast_promedio = calcular_promedio_regional_correcto(islands_data)
        dif_promedio = jara_promedio - kast_promedio

        jara_gana = (islands_data['diferencia_pct'] > 0).sum()
        kast_gana = (islands_data['diferencia_pct'] < 0).sum()
        empates = (islands_data['diferencia_pct'] == 0).sum()

    # Gráfico de barras
    ax_barras = fig.add_subplot(stats_gs[0])

    if comunas_con_datos > 0:
        candidatos = ['JARA', 'KAST']
        porcentajes = [jara_promedio, kast_promedio]
        colores_barras = ['#E54540', '#2D426C']

        bars = ax_barras.bar(candidatos, porcentajes, color=colores_barras,
                             edgecolor='black', width=0.6)

        ax_barras.set_ylabel('Porcentaje (%)', fontsize=11, fontweight='bold')
        ax_barras.set_title('RESULTADO ISLA DE PASCUA', fontsize=13, fontweight='bold', pad=10)

        max_porcentaje = max(porcentajes) if len(porcentajes) > 0 else 100
        ax_barras.set_ylim(0, max_porcentaje * 1.25)

        ax_barras.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        for bar in bars:
            height = bar.get_height()
            ax_barras.text(bar.get_x() + bar.get_width() / 2.,
                           height + (max_porcentaje * 0.02),
                           f'{height:.1f}%',
                           ha='center', va='bottom',
                           fontsize=11, fontweight='bold')
    else:
        ax_barras.text(0.5, 0.5, 'SIN DATOS',
                       ha='center', va='center',
                       transform=ax_barras.transAxes,
                       fontsize=14, fontweight='bold',
                       color='gray')
        ax_barras.set_title('RESULTADO ISLA DE PASCUA', fontsize=13, fontweight='bold', pad=10)

    ax_barras.grid(axis='y', alpha=0.3)
    ax_barras.tick_params(axis='both', labelsize=10)

    # Estadísticas de comunas
    ax_comunas = fig.add_subplot(stats_gs[1])
    ax_comunas.set_axis_off()

    if comunas_con_datos > 0:
        total_comunas = len(islands_data)
        sin_datos = total_comunas - comunas_con_datos

        stats_text = (f"COMUNAS CON DATOS: {comunas_con_datos}/{total_comunas}\n\n"
                      f"JARA gana en: {jara_gana} comunas\n"
                      f"KAST gana en: {kast_gana} comunas\n"
                      f"Empates: {empates} comunas")

        if sin_datos > 0:
            stats_text += f"\nSin datos: {sin_datos} comunas"

        ax_comunas.text(0.05, 0.9, stats_text,
                        ha='left', va='top',
                        fontsize=10,
                        transform=ax_comunas.transAxes,
                        linespacing=1.5)
    else:
        ax_comunas.text(0.5, 0.5, 'NO HAY DATOS ELECTORALES\nPARA ISLA DE PASCUA',
                        ha='center', va='center',
                        fontsize=11, fontweight='bold',
                        transform=ax_comunas.transAxes,
                        color='gray')

    # Diferencia
    ax_diferencia = fig.add_subplot(stats_gs[2])
    ax_diferencia.set_axis_off()

    if comunas_con_datos > 0:
        color_dif = '#E54540' if dif_promedio > 0 else '#2D426C' if dif_promedio < 0 else 'gray'

        dif_text = (f"DIFERENCIA\n"
                    f"{dif_promedio:+.1f}%")

        ax_diferencia.text(0.5, 0.7, dif_text,
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color=color_dif,
                           transform=ax_diferencia.transAxes)

        info_text = f"Jara {jara_promedio:.1f}% - Kast {kast_promedio:.1f}%"
        ax_diferencia.text(0.5, 0.3, info_text,
                           ha='center', va='center',
                           fontsize=9,
                           color='gray',
                           transform=ax_diferencia.transAxes)
    else:
        ax_diferencia.text(0.5, 0.7, 'DIFERENCIA\nN/A',
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color='gray',
                           transform=ax_diferencia.transAxes)

    # Escala de colores
    ax_escala = fig.add_subplot(stats_gs[3])

    norm = plt.Normalize(-100, 100)
    sm = ScalarMappable(cmap=cmap_continuo, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=ax_escala, orientation='horizontal', fraction=0.9)
    cbar.set_label('Diferencia (Jara% - Kast%)', fontsize=8, fontweight='bold', labelpad=3)

    ticks = [-100, -50, -10, 0, 10, 50, 100]
    tick_labels = ['-100', '-50', '-10', '0', '10', '50', '+100']

    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)
    cbar.ax.tick_params(labelsize=6)

    # Pie de página
    ax_fondo = fig.add_subplot(gs[2, :])
    ax_fondo.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Isla de Pascua | Generado: {fecha}"
    ax_fondo.text(0.5, 0.5, info_text,
                  ha='center', va='center',
                  fontsize=8, color='gray',
                  transform=ax_fondo.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    output_path = os.path.join(output_dir, "ISLA_DE_PASCUA_RAPA_NUI.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Mapa de Isla de Pascua guardado: {output_path}")
    return output_path


def crear_mapa_juan_fernandez(mapa_data, output_dir):
    """
    Crea mapa separado para Archipiélago Juan Fernández.

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 🗺️ Generando mapa separado para Archipiélago Juan Fernández")

    islands_data = mapa_data[
        mapa_data['NOM_COM'].str.contains('Juan Fernández', case=False, na=False)].copy()

    if islands_data.empty:
        print(f" ⚠ No hay datos para Archipiélago Juan Fernández")
        return None

    # Límites geográficos para Juan Fernández
    juan_fernandez_bounds = {
        'minx': -79.0,
        'miny': -33.8,
        'maxx': -78.7,
        'maxy': -33.6
    }

    # Verificar datos electorales
    comunas_con_datos = 0
    if 'diferencia_pct' in islands_data.columns:
        comunas_con_datos = islands_data['diferencia_pct'].notna().sum()

    if comunas_con_datos == 0:
        print(f" ⚠ No hay datos electorales para Archipiélago Juan Fernández")

    # Configurar figura
    fig = plt.figure(figsize=(14, 10))

    gs = GridSpec(3, 2, figure=fig, height_ratios=[0.05, 0.90, 0.05],
                  width_ratios=[0.70, 0.30], hspace=0.08, wspace=0.08)

    # Título
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'Comuna de Juan Fernández - Islas Robinson Crusoe y Santa Clara',
                   ha='center', va='center', fontsize=18, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Mapa
    ax_mapa = fig.add_subplot(gs[1, 0])

    if 'diferencia_pct' in islands_data.columns:
        islands_data['color'] = islands_data['diferencia_pct'].apply(asignar_color_diferencia)
    else:
        islands_data['color'] = '#D3D3D3'

    # Dibujar mapa con límites específicos
    try:
        islands_data.plot(ax=ax_mapa, color=islands_data['color'], edgecolor='black', linewidth=0.5)

        ax_mapa.set_xlim(juan_fernandez_bounds['minx'], juan_fernandez_bounds['maxx'])
        ax_mapa.set_ylim(juan_fernandez_bounds['miny'], juan_fernandez_bounds['maxy'])

    except Exception as e:
        print(f" ⚠ Error dibujando mapa de Juan Fernández: {e}")
        for idx, row in islands_data.iterrows():
            if hasattr(row, 'geometry') and row.geometry is not None:
                try:
                    gpd.GeoSeries([row.geometry]).plot(ax=ax_mapa, color=row['color'],
                                                       edgecolor='black', linewidth=0.5)
                except:
                    continue

    # Agregar nombres
    agregar_nombres_comunas(ax_mapa, islands_data, fontsize=12)

    ax_mapa.set_axis_off()
    ax_mapa.set_aspect('equal')

    # Panel de estadísticas
    ax_stats_container = fig.add_subplot(gs[1, 1])
    ax_stats_container.set_axis_off()

    stats_gs = GridSpecFromSubplotSpec(4, 1, subplot_spec=gs[1, 1],
                                       height_ratios=[0.5, 0.25, 0.15, 0.10], hspace=0.15)

    # Calcular estadísticas
    jara_promedio = kast_promedio = 0
    jara_gana = kast_gana = empates = 0
    dif_promedio = 0

    if comunas_con_datos > 0:
        jara_promedio, kast_promedio = calcular_promedio_regional_correcto(islands_data)
        dif_promedio = jara_promedio - kast_promedio

        jara_gana = (islands_data['diferencia_pct'] > 0).sum()
        kast_gana = (islands_data['diferencia_pct'] < 0).sum()
        empates = (islands_data['diferencia_pct'] == 0).sum()

    # Gráfico de barras
    ax_barras = fig.add_subplot(stats_gs[0])

    if comunas_con_datos > 0:
        candidatos = ['JARA', 'KAST']
        porcentajes = [jara_promedio, kast_promedio]
        colores_barras = ['#E54540', '#2D426C']

        bars = ax_barras.bar(candidatos, porcentajes, color=colores_barras,
                             edgecolor='black', width=0.6)

        ax_barras.set_ylabel('Porcentaje (%)', fontsize=11, fontweight='bold')
        ax_barras.set_title('RESULTADO JUAN FERNÁNDEZ', fontsize=13, fontweight='bold', pad=10)

        max_porcentaje = max(porcentajes) if len(porcentajes) > 0 else 100
        ax_barras.set_ylim(0, max_porcentaje * 1.25)

        ax_barras.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        for bar in bars:
            height = bar.get_height()
            ax_barras.text(bar.get_x() + bar.get_width() / 2.,
                           height + (max_porcentaje * 0.02),
                           f'{height:.1f}%',
                           ha='center', va='bottom',
                           fontsize=11, fontweight='bold')
    else:
        ax_barras.text(0.5, 0.5, 'SIN DATOS',
                       ha='center', va='center',
                       transform=ax_barras.transAxes,
                       fontsize=14, fontweight='bold',
                       color='gray')
        ax_barras.set_title('RESULTADO JUAN FERNÁNDEZ', fontsize=13, fontweight='bold', pad=10)

    ax_barras.grid(axis='y', alpha=0.3)
    ax_barras.tick_params(axis='both', labelsize=10)

    # Estadísticas de comunas
    ax_comunas = fig.add_subplot(stats_gs[1])
    ax_comunas.set_axis_off()

    if comunas_con_datos > 0:
        total_comunas = len(islands_data)
        sin_datos = total_comunas - comunas_con_datos

        stats_text = (f"COMUNAS CON DATOS: {comunas_con_datos}/{total_comunas}\n\n"
                      f"JARA gana en: {jara_gana} comunas\n"
                      f"KAST gana en: {kast_gana} comunas\n"
                      f"Empates: {empates} comunas")

        if sin_datos > 0:
            stats_text += f"\nSin datos: {sin_datos} comunas"

        ax_comunas.text(0.05, 0.9, stats_text,
                        ha='left', va='top',
                        fontsize=10,
                        transform=ax_comunas.transAxes,
                        linespacing=1.5)
    else:
        ax_comunas.text(0.5, 0.5, 'NO HAY DATOS ELECTORALES\nPARA JUAN FERNÁNDEZ',
                        ha='center', va='center',
                        fontsize=11, fontweight='bold',
                        transform=ax_comunas.transAxes,
                        color='gray')

    # Diferencia
    ax_diferencia = fig.add_subplot(stats_gs[2])
    ax_diferencia.set_axis_off()

    if comunas_con_datos > 0:
        color_dif = '#E54540' if dif_promedio > 0 else '#2D426C' if dif_promedio < 0 else 'gray'

        dif_text = (f"DIFERENCIA\n"
                    f"{dif_promedio:+.1f}%")

        ax_diferencia.text(0.5, 0.7, dif_text,
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color=color_dif,
                           transform=ax_diferencia.transAxes)

        info_text = f"Jara {jara_promedio:.1f}% - Kast {kast_promedio:.1f}%"
        ax_diferencia.text(0.5, 0.3, info_text,
                           ha='center', va='center',
                           fontsize=9,
                           color='gray',
                           transform=ax_diferencia.transAxes)
    else:
        ax_diferencia.text(0.5, 0.7, 'DIFERENCIA\nN/A',
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color='gray',
                           transform=ax_diferencia.transAxes)

    # Escala de colores
    ax_escala = fig.add_subplot(stats_gs[3])

    norm = plt.Normalize(-100, 100)
    sm = ScalarMappable(cmap=cmap_continuo, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=ax_escala, orientation='horizontal', fraction=0.9)
    cbar.set_label('Diferencia (Jara% - Kast%)', fontsize=8, fontweight='bold', labelpad=3)

    ticks = [-100, -50, -10, 0, 10, 50, 100]
    tick_labels = ['-100', '-50', '-10', '0', '10', '50', '+100']

    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)
    cbar.ax.tick_params(labelsize=6)

    # Pie de página
    ax_fondo = fig.add_subplot(gs[2, :])
    ax_fondo.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Juan Fernández | Generado: {fecha}"
    ax_fondo.text(0.5, 0.5, info_text,
                  ha='center', va='center',
                  fontsize=8, color='gray',
                  transform=ax_fondo.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    output_path = os.path.join(output_dir, "ARCHIPIELAGO_JUAN_FERNANDEZ.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Mapa de Juan Fernández guardado: {output_path}")
    return output_path


# ============================================================================
# FUNCIONES PARA MAPAS DE ÁREAS METROPOLITANAS
# ============================================================================

def crear_mapa_gran_valparaiso(mapa_data, output_dir):
    """
    Crea mapa del Gran Valparaíso (área metropolitana).

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 🗺️ Generando mapa separado para Gran Valparaíso")

    # Normalizar nombres de comunas del Gran Valparaíso
    gran_valparaiso_norm = [normalizar_nombre(comuna) for comuna in GRAN_VALPARAISO]

    # Filtrar datos del Gran Valparaíso
    gran_valparaiso_data = mapa_data[
        (mapa_data['REGION_NUM'] == 5) &
        (mapa_data['NOM_COM_NORM'].isin(gran_valparaiso_norm))
        ].copy()

    if gran_valparaiso_data.empty:
        print(f" ⚠ No hay datos para Gran Valparaíso")
        return None

    # Verificar datos electorales
    comunas_con_datos = 0
    if 'diferencia_pct' in gran_valparaiso_data.columns:
        comunas_con_datos = gran_valparaiso_data['diferencia_pct'].notna().sum()

    if comunas_con_datos == 0:
        print(f" ⚠ No hay datos electorales para Gran Valparaíso")

    # Configurar figura
    fig = plt.figure(figsize=(18, 14))

    gs = GridSpec(3, 2, figure=fig, height_ratios=[0.05, 0.90, 0.05],
                  width_ratios=[0.65, 0.35], hspace=0.08, wspace=0.08)

    # Título
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'Gran Valparaíso - Área Metropolitana',
                   ha='center', va='center', fontsize=22, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Mapa
    ax_mapa = fig.add_subplot(gs[1, 0])

    # Calcular estadísticas
    jara_promedio = kast_promedio = 0
    jara_gana = kast_gana = empates = 0
    dif_promedio = 0

    if comunas_con_datos > 0:
        gran_valparaiso_data['color'] = gran_valparaiso_data['diferencia_pct'].apply(asignar_color_diferencia)
        jara_promedio, kast_promedio = calcular_promedio_regional_correcto(gran_valparaiso_data)
        dif_promedio = jara_promedio - kast_promedio

        jara_gana = (gran_valparaiso_data['diferencia_pct'] > 0).sum()
        kast_gana = (gran_valparaiso_data['diferencia_pct'] < 0).sum()
        empates = (gran_valparaiso_data['diferencia_pct'] == 0).sum()
    else:
        gran_valparaiso_data['color'] = '#D3D3D3'

    # Dibujar mapa
    try:
        if 'geometry' in gran_valparaiso_data.columns and not gran_valparaiso_data.geometry.isna().all():
            gran_valparaiso_data.plot(ax=ax_mapa, color=gran_valparaiso_data['color'],
                                      edgecolor='black', linewidth=0.8)

            agregar_nombres_comunas(ax_mapa, gran_valparaiso_data,
                                    fontsize=TAMANOS_FUENTE_AREAS_METROPOLITANAS['gran_valparaiso'])
        else:
            ax_mapa.text(0.5, 0.5, 'No hay geometrías disponibles',
                         ha='center', va='center',
                         transform=ax_mapa.transAxes,
                         fontsize=14, fontweight='bold',
                         color='gray')
    except Exception as e:
        print(f" ⚠ Error dibujando mapa de Gran Valparaíso: {e}")
        ax_mapa.text(0.5, 0.5, f'Error: {str(e)}',
                     ha='center', va='center',
                     transform=ax_mapa.transAxes,
                     fontsize=12, color='red')

    ax_mapa.set_axis_off()
    ax_mapa.set_aspect('equal')

    # Panel de estadísticas
    ax_stats_container = fig.add_subplot(gs[1, 1])
    ax_stats_container.set_axis_off()

    stats_gs = GridSpecFromSubplotSpec(4, 1, subplot_spec=gs[1, 1],
                                       height_ratios=[0.5, 0.25, 0.15, 0.10], hspace=0.15)

    # Gráfico de barras
    ax_barras = fig.add_subplot(stats_gs[0])

    if comunas_con_datos > 0:
        candidatos = ['JARA', 'KAST']
        porcentajes = [jara_promedio, kast_promedio]
        colores_barras = ['#E54540', '#2D426C']

        bars = ax_barras.bar(candidatos, porcentajes, color=colores_barras,
                             edgecolor='black', width=0.6)

        ax_barras.set_ylabel('Porcentaje (%)', fontsize=11, fontweight='bold')
        ax_barras.set_title('PROMEDIO GRAN VALPARAÍSO', fontsize=13, fontweight='bold', pad=10)

        max_porcentaje = max(porcentajes) if len(porcentajes) > 0 else 100
        ax_barras.set_ylim(0, max_porcentaje * 1.25)

        ax_barras.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        for bar in bars:
            height = bar.get_height()
            ax_barras.text(bar.get_x() + bar.get_width() / 2.,
                           height + (max_porcentaje * 0.02),
                           f'{height:.1f}%',
                           ha='center', va='bottom',
                           fontsize=11, fontweight='bold')
    else:
        ax_barras.text(0.5, 0.5, 'SIN DATOS',
                       ha='center', va='center',
                       transform=ax_barras.transAxes,
                       fontsize=14, fontweight='bold',
                       color='gray')
        ax_barras.set_title('PROMEDIO GRAN VALPARAÍSO', fontsize=13, fontweight='bold', pad=10)

    ax_barras.grid(axis='y', alpha=0.3)
    ax_barras.tick_params(axis='both', labelsize=10)

    # Estadísticas de comunas
    ax_comunas = fig.add_subplot(stats_gs[1])
    ax_comunas.set_axis_off()

    if comunas_con_datos > 0:
        total_comunas = len(gran_valparaiso_data)
        sin_datos = total_comunas - comunas_con_datos

        comunas_lista = ", ".join(gran_valparaiso_data['NOM_COM'].tolist()[:5])
        if len(gran_valparaiso_data) > 5:
            comunas_lista += "..."

        stats_text = (f"COMUNAS INCLUIDAS ({len(gran_valparaiso_data)}):\n{comunas_lista}\n\n"
                      f"COMUNAS CON DATOS: {comunas_con_datos}/{total_comunas}\n"
                      f"JARA gana en: {jara_gana} comunas\n"
                      f"KAST gana en: {kast_gana} comunas\n"
                      f"Empates: {empates} comunas")

        if sin_datos > 0:
            stats_text += f"\nSin datos: {sin_datos} comunas"

        ax_comunas.text(0.05, 0.9, stats_text,
                        ha='left', va='top',
                        fontsize=10,
                        transform=ax_comunas.transAxes,
                        linespacing=1.5)
    else:
        ax_comunas.text(0.5, 0.5, 'NO HAY DATOS ELECTORALES\nPARA GRAN VALPARAÍSO',
                        ha='center', va='center',
                        fontsize=11, fontweight='bold',
                        transform=ax_comunas.transAxes,
                        color='gray')

    # Diferencia
    ax_diferencia = fig.add_subplot(stats_gs[2])
    ax_diferencia.set_axis_off()

    if comunas_con_datos > 0:
        color_dif = '#E54540' if dif_promedio > 0 else '#2D426C' if dif_promedio < 0 else 'gray'

        dif_text = (f"DIFERENCIA PROMEDIO\nGRAN VALPARAÍSO\n"
                    f"{dif_promedio:+.1f}%")

        ax_diferencia.text(0.5, 0.7, dif_text,
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color=color_dif,
                           transform=ax_diferencia.transAxes)

        info_text = f"Jara {jara_promedio:.1f}% - Kast {kast_promedio:.1f}%"
        ax_diferencia.text(0.5, 0.3, info_text,
                           ha='center', va='center',
                           fontsize=9,
                           color='gray',
                           transform=ax_diferencia.transAxes)
    else:
        ax_diferencia.text(0.5, 0.7, 'DIFERENCIA PROMEDIO\nGRAN VALPARAÍSO\nN/A',
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color='gray',
                           transform=ax_diferencia.transAxes)

    # Escala de colores
    ax_escala = fig.add_subplot(stats_gs[3])

    norm = plt.Normalize(-100, 100)
    sm = ScalarMappable(cmap=cmap_continuo, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=ax_escala, orientation='horizontal', fraction=0.9)
    cbar.set_label('Diferencia (Jara% - Kast%)', fontsize=8, fontweight='bold', labelpad=3)

    ticks = [-100, -50, -10, 0, 10, 50, 100]
    tick_labels = ['-100', '-50', '-10', '0', '10', '50', '+100']

    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)
    cbar.ax.tick_params(labelsize=6)

    # Pie de página
    ax_fondo = fig.add_subplot(gs[2, :])
    ax_fondo.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Gran Valparaíso | Generado: {fecha}"
    ax_fondo.text(0.5, 0.5, info_text,
                  ha='center', va='center',
                  fontsize=8, color='gray',
                  transform=ax_fondo.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    output_path = os.path.join(output_dir, "GRAN_VALPARAISO_METROPOLITANO.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Mapa de Gran Valparaíso guardado: {output_path}")
    return output_path


def crear_mapa_gran_concepcion(mapa_data, output_dir):
    """
    Crea mapa del Gran Concepción (área metropolitana).

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 🗺️ Generando mapa separado para Gran Concepción")

    # Normalizar nombres de comunas del Gran Concepción
    gran_concepcion_norm = [normalizar_nombre(comuna) for comuna in GRAN_CONCEPCION]

    # Filtrar datos del Gran Concepción
    gran_concepcion_data = mapa_data[
        (mapa_data['REGION_NUM'] == 8) &
        (mapa_data['NOM_COM_NORM'].isin(gran_concepcion_norm))
        ].copy()

    if gran_concepcion_data.empty:
        print(f" ⚠ No hay datos para Gran Concepción")
        return None

    # Verificar datos electorales
    comunas_con_datos = 0
    if 'diferencia_pct' in gran_concepcion_data.columns:
        comunas_con_datos = gran_concepcion_data['diferencia_pct'].notna().sum()

    if comunas_con_datos == 0:
        print(f" ⚠ No hay datos electorales para Gran Concepción")

    # Configurar figura
    fig = plt.figure(figsize=(18, 14))

    gs = GridSpec(3, 2, figure=fig, height_ratios=[0.05, 0.90, 0.05],
                  width_ratios=[0.65, 0.35], hspace=0.08, wspace=0.08)

    # Título
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'Gran Concepción - Área Metropolitana',
                   ha='center', va='center', fontsize=22, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Mapa
    ax_mapa = fig.add_subplot(gs[1, 0])

    # Calcular estadísticas
    jara_promedio = kast_promedio = 0
    jara_gana = kast_gana = empates = 0
    dif_promedio = 0

    if comunas_con_datos > 0:
        gran_concepcion_data['color'] = gran_concepcion_data['diferencia_pct'].apply(asignar_color_diferencia)
        jara_promedio, kast_promedio = calcular_promedio_regional_correcto(gran_concepcion_data)
        dif_promedio = jara_promedio - kast_promedio

        jara_gana = (gran_concepcion_data['diferencia_pct'] > 0).sum()
        kast_gana = (gran_concepcion_data['diferencia_pct'] < 0).sum()
        empates = (gran_concepcion_data['diferencia_pct'] == 0).sum()
    else:
        gran_concepcion_data['color'] = '#D3D3D3'

    # Dibujar mapa
    try:
        if 'geometry' in gran_concepcion_data.columns and not gran_concepcion_data.geometry.isna().all():
            gran_concepcion_data.plot(ax=ax_mapa, color=gran_concepcion_data['color'],
                                      edgecolor='black', linewidth=0.8)

            agregar_nombres_comunas(ax_mapa, gran_concepcion_data,
                                    fontsize=TAMANOS_FUENTE_AREAS_METROPOLITANAS['gran_concepcion'])
        else:
            ax_mapa.text(0.5, 0.5, 'No hay geometrías disponibles',
                         ha='center', va='center',
                         transform=ax_mapa.transAxes,
                         fontsize=14, fontweight='bold',
                         color='gray')
    except Exception as e:
        print(f" ⚠ Error dibujando mapa de Gran Concepción: {e}")
        ax_mapa.text(0.5, 0.5, f'Error: {str(e)}',
                     ha='center', va='center',
                     transform=ax_mapa.transAxes,
                     fontsize=12, color='red')

    ax_mapa.set_axis_off()
    ax_mapa.set_aspect('equal')

    # Panel de estadísticas
    ax_stats_container = fig.add_subplot(gs[1, 1])
    ax_stats_container.set_axis_off()

    stats_gs = GridSpecFromSubplotSpec(4, 1, subplot_spec=gs[1, 1],
                                       height_ratios=[0.5, 0.25, 0.15, 0.10], hspace=0.15)

    # Gráfico de barras
    ax_barras = fig.add_subplot(stats_gs[0])

    if comunas_con_datos > 0:
        candidatos = ['JARA', 'KAST']
        porcentajes = [jara_promedio, kast_promedio]
        colores_barras = ['#E54540', '#2D426C']

        bars = ax_barras.bar(candidatos, porcentajes, color=colores_barras,
                             edgecolor='black', width=0.6)

        ax_barras.set_ylabel('Porcentaje (%)', fontsize=11, fontweight='bold')
        ax_barras.set_title('PROMEDIO GRAN CONCEPCIÓN', fontsize=13, fontweight='bold', pad=10)

        max_porcentaje = max(porcentajes) if len(porcentajes) > 0 else 100
        ax_barras.set_ylim(0, max_porcentaje * 1.25)

        ax_barras.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        for bar in bars:
            height = bar.get_height()
            ax_barras.text(bar.get_x() + bar.get_width() / 2.,
                           height + (max_porcentaje * 0.02),
                           f'{height:.1f}%',
                           ha='center', va='bottom',
                           fontsize=11, fontweight='bold')
    else:
        ax_barras.text(0.5, 0.5, 'SIN DATOS',
                       ha='center', va='center',
                       transform=ax_barras.transAxes,
                       fontsize=14, fontweight='bold',
                       color='gray')
        ax_barras.set_title('PROMEDIO GRAN CONCEPCIÓN', fontsize=13, fontweight='bold', pad=10)

    ax_barras.grid(axis='y', alpha=0.3)
    ax_barras.tick_params(axis='both', labelsize=10)

    # Estadísticas de comunas
    ax_comunas = fig.add_subplot(stats_gs[1])
    ax_comunas.set_axis_off()

    if comunas_con_datos > 0:
        total_comunas = len(gran_concepcion_data)
        sin_datos = total_comunas - comunas_con_datos

        comunas_lista = ", ".join(gran_concepcion_data['NOM_COM'].tolist()[:8])
        if len(gran_concepcion_data) > 8:
            comunas_lista += "..."

        stats_text = (f"COMUNAS INCLUIDAS ({len(gran_concepcion_data)}):\n{comunas_lista}\n\n"
                      f"COMUNAS CON DATOS: {comunas_con_datos}/{total_comunas}\n"
                      f"JARA gana en: {jara_gana} comunas\n"
                      f"KAST gana en: {kast_gana} comunas\n"
                      f"Empates: {empates} comunas")

        if sin_datos > 0:
            stats_text += f"\nSin datos: {sin_datos} comunas"

        ax_comunas.text(0.05, 0.9, stats_text,
                        ha='left', va='top',
                        fontsize=10,
                        transform=ax_comunas.transAxes,
                        linespacing=1.5)
    else:
        ax_comunas.text(0.5, 0.5, 'NO HAY DATOS ELECTORALES\nPARA GRAN CONCEPCIÓN',
                        ha='center', va='center',
                        fontsize=11, fontweight='bold',
                        transform=ax_comunas.transAxes,
                        color='gray')

    # Diferencia
    ax_diferencia = fig.add_subplot(stats_gs[2])
    ax_diferencia.set_axis_off()

    if comunas_con_datos > 0:
        color_dif = '#E54540' if dif_promedio > 0 else '#2D426C' if dif_promedio < 0 else 'gray'

        dif_text = (f"DIFERENCIA PROMEDIO\nGRAN CONCEPCIÓN\n"
                    f"{dif_promedio:+.1f}%")

        ax_diferencia.text(0.5, 0.7, dif_text,
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color=color_dif,
                           transform=ax_diferencia.transAxes)

        info_text = f"Jara {jara_promedio:.1f}% - Kast {kast_promedio:.1f}%"
        ax_diferencia.text(0.5, 0.3, info_text,
                           ha='center', va='center',
                           fontsize=9,
                           color='gray',
                           transform=ax_diferencia.transAxes)
    else:
        ax_diferencia.text(0.5, 0.7, 'DIFERENCIA PROMEDIO\nGRAN CONCEPCIÓN\nN/A',
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color='gray',
                           transform=ax_diferencia.transAxes)

    # Escala de colores
    ax_escala = fig.add_subplot(stats_gs[3])

    norm = plt.Normalize(-100, 100)
    sm = ScalarMappable(cmap=cmap_continuo, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=ax_escala, orientation='horizontal', fraction=0.9)
    cbar.set_label('Diferencia (Jara% - Kast%)', fontsize=8, fontweight='bold', labelpad=3)

    ticks = [-100, -50, -10, 0, 10, 50, 100]
    tick_labels = ['-100', '-50', '-10', '0', '10', '50', '+100']

    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)
    cbar.ax.tick_params(labelsize=6)

    # Pie de página
    ax_fondo = fig.add_subplot(gs[2, :])
    ax_fondo.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Gran Concepción | Generado: {fecha}"
    ax_fondo.text(0.5, 0.5, info_text,
                  ha='center', va='center',
                  fontsize=8, color='gray',
                  transform=ax_fondo.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    output_path = os.path.join(output_dir, "GRAN_CONCEPCION_METROPOLITANO.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Mapa de Gran Concepción guardado: {output_path}")
    return output_path


def crear_mapa_conurbacion_santiago(mapa_data, output_dir):
    """
    Crea mapa del Gran Santiago (Santiago Metropolitano).

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 🗺️ Generando mapa separado para Gran Santiago (Santiago Metropolitano)")

    # Cargar GeoJSON especializado para Gran Santiago
    gran_santiago_gdf = cargar_gran_santiago_geojson()

    # Filtrar datos de la conurbación de Santiago
    conurbacion_norm = [normalizar_nombre(comuna) for comuna in CONURBACION_SANTIAGO]
    conurb_data = mapa_data[
        (mapa_data['REGION_NUM'] == 13) &
        (mapa_data['NOM_COM_NORM'].isin(conurbacion_norm))
        ].copy()

    if conurb_data.empty:
        print(f" ⚠ No hay datos para el Gran Santiago")
        return None

    # Verificar datos electorales
    comunas_con_datos = 0
    if 'diferencia_pct' in conurb_data.columns:
        comunas_con_datos = conurb_data['diferencia_pct'].notna().sum()

    if comunas_con_datos == 0:
        print(f" ⚠ No hay datos electorales para el Gran Santiago")
        return None

    # Calcular estadísticas
    jara_promedio = kast_promedio = 0
    dif_promedio = 0

    if comunas_con_datos > 0:
        jara_promedio, kast_promedio = calcular_promedio_regional_correcto(conurb_data)
        dif_promedio = jara_promedio - kast_promedio

    # Configurar figura grande
    fig = plt.figure(figsize=(36, 32))

    gs = GridSpec(5, 1, figure=fig, height_ratios=[0.04, 0.06, 0.70, 0.15, 0.05], hspace=0.03)

    # Título
    ax_titulo = fig.add_subplot(gs[0])
    ax_titulo.set_axis_off()

    if gran_santiago_gdf is not None:
        titulo = 'Gran Santiago - Área Metropolitana'
    else:
        titulo = 'Conurbación de Santiago'

    ax_titulo.text(0.5, 0.5, titulo,
                   ha='center', va='center', fontsize=32, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Estadísticas principales
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.set_axis_off()

    if comunas_con_datos > 0:
        color_jara = '#E54540'
        color_kast = '#2D426C'
        color_dif = color_jara if dif_promedio > 0 else color_kast if dif_promedio < 0 else 'gray'

        texto_completo = f"JARA: {jara_promedio:.1f}%   |   KAST: {kast_promedio:.1f}%   |   Diferencia: {dif_promedio:+.1f}%"

        ax_stats.text(0.5, 0.7, texto_completo,
                      ha='center', va='center',
                      fontsize=28, fontweight='bold',
                      transform=ax_stats.transAxes)

        info_text = f"Promedio basado en {comunas_con_datos} comunas con datos"
        ax_stats.text(0.5, 0.3, info_text,
                      ha='center', va='center',
                      fontsize=18, color='gray',
                      transform=ax_stats.transAxes)
    else:
        ax_stats.text(0.5, 0.5, 'SIN DATOS DISPONIBLES',
                      ha='center', va='center',
                      fontsize=24, fontweight='bold', color='gray',
                      transform=ax_stats.transAxes)

    # Mapa principal
    ax_mapa = fig.add_subplot(gs[2])

    if comunas_con_datos > 0:
        conurb_data['color'] = conurb_data['diferencia_pct'].apply(asignar_color_diferencia)
    else:
        conurb_data['color'] = '#D3D3D3'

    # Dibujar mapa
    try:
        if 'geometry' in conurb_data.columns and not conurb_data.geometry.isna().all():
            conurb_data.plot(ax=ax_mapa, color=conurb_data['color'], edgecolor='black', linewidth=1.2)

            agregar_etiquetas_gran_santiago(ax_mapa, conurb_data, usar_numeros=True)

        else:
            ax_mapa.text(0.5, 0.5, 'No hay geometrías disponibles',
                         ha='center', va='center',
                         transform=ax_mapa.transAxes,
                         fontsize=20, fontweight='bold',
                         color='gray')
    except Exception as e:
        print(f" ⚠ Error dibujando mapa del Gran Santiago: {e}")
        ax_mapa.text(0.5, 0.5, f'Error: {str(e)}',
                     ha='center', va='center',
                     transform=ax_mapa.transAxes,
                     fontsize=16, color='red')

    ax_mapa.set_axis_off()
    ax_mapa.set_aspect('equal')

    # Simbología
    ax_simbologia = fig.add_subplot(gs[3])
    ax_simbologia.set_axis_off()

    ax_simbologia.text(0.5, 0.97, 'Simbología - Comunas',
                       ha='center', va='top',
                       fontsize=30, fontweight='bold',
                       transform=ax_simbologia.transAxes)

    items = list(MAQUEO_COMUNAS_NUMEROS.items())
    mitad = len(items) // 2 + len(items) % 2

    espaciado_vertical = 0.09

    # Primera columna de simbología
    for i, (comuna, numero) in enumerate(items[:mitad]):
        y_pos = 0.88 - i * espaciado_vertical
        ax_simbologia.text(0.25, y_pos, f'{numero}. {comuna}',
                           ha='left', va='center',
                           fontsize=22,
                           transform=ax_simbologia.transAxes)

    # Segunda columna de simbología
    for i, (comuna, numero) in enumerate(items[mitad:]):
        y_pos = 0.88 - i * espaciado_vertical
        ax_simbologia.text(0.65, y_pos, f'{numero}. {comuna}',
                           ha='left', va='center',
                           fontsize=22,
                           transform=ax_simbologia.transAxes)

    # Escala de colores
    ax_escala = fig.add_subplot(gs[4])

    norm = plt.Normalize(-100, 100)
    sm = ScalarMappable(cmap=cmap_continuo, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=ax_escala, orientation='horizontal', fraction=0.9)
    cbar.set_label('Diferencia (Jara% - Kast%)', fontsize=22, fontweight='bold', labelpad=12)

    ticks = [-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100]
    tick_labels = ['-100 (Kast absoluto)', '-80', '-60', '-40', '-20', '0', '20', '40', '60', '80',
                   '+100 (Jara absoluto)']

    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)
    cbar.ax.tick_params(labelsize=16)

    plt.tight_layout(rect=[0.01, 0.01, 0.99, 0.99])

    # Guardar archivo
    if gran_santiago_gdf is not None:
        output_path = os.path.join(output_dir, "GRAN_SANTIAGO_METROPOLITANO.png")
    else:
        output_path = os.path.join(output_dir, "CONURBACION_SANTIAGO_.png")

    plt.savefig(output_path, dpi=400, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

    print(f" ✓ Mapa de Gran Santiago guardado: {output_path}")
    return output_path


# ============================================================================
# FUNCIONES PARA MAPAS NACIONALES Y REPORTES
# ============================================================================

def crear_mapa_chile_tres_partes(mapa_data, output_dir):
    """
    Crea mapa de Chile dividido en tres zonas (Norte, Centro, Sur).

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 🗺️ Generando mapa de Chile en tres partes (Norte, Centro, Sur) - SIN ETIQUETAS DE COMUNAS")

    # Filtrar datos con resultados electorales
    datos_chile = mapa_data[mapa_data['diferencia_pct'].notna()].copy()

    if datos_chile.empty:
        print(f" ⚠ No hay datos suficientes para el mapa de Chile en tres partes")
        return None

    # Excluir islas
    datos_chile = datos_chile[~datos_chile['NOM_COM'].str.contains('Isla de Pascua|Rapa Nui|Juan Fernández',
                                                                   case=False, na=False)]

    # Dividir en zonas
    norte_data = datos_chile[datos_chile['REGION_NUM'].isin([15, 1, 2, 3, 4])].copy()
    centro_data = datos_chile[datos_chile['REGION_NUM'].isin([5, 6, 7, 8, 13, 16])].copy()
    sur_data = datos_chile[datos_chile['REGION_NUM'].isin([9, 10, 11, 12, 14])].copy()

    def calcular_estadisticas_zona(zona_data, nombre_zona):
        """Calcula estadísticas para una zona geográfica."""
        if zona_data.empty:
            return {
                'nombre': nombre_zona,
                'jara_pct': 0,
                'kast_pct': 0,
                'dif_pct': 0,
                'jara_gana': 0,
                'kast_gana': 0,
                'empates': 0,
                'total_comunas': 0
            }

        jara_pct, kast_pct = calcular_promedio_regional_correcto(zona_data)
        dif_pct = jara_pct - kast_pct

        jara_gana = (zona_data['diferencia_pct'] > 0).sum()
        kast_gana = (zona_data['diferencia_pct'] < 0).sum()
        empates = (zona_data['diferencia_pct'] == 0).sum()

        return {
            'nombre': nombre_zona,
            'jara_pct': jara_pct,
            'kast_pct': kast_pct,
            'dif_pct': dif_pct,
            'jara_gana': jara_gana,
            'kast_gana': kast_gana,
            'empates': empates,
            'total_comunas': len(zona_data)
        }

    # Calcular estadísticas por zona
    estadisticas_norte = calcular_estadisticas_zona(norte_data, 'Norte')
    estadisticas_centro = calcular_estadisticas_zona(centro_data, 'Centro')
    estadisticas_sur = calcular_estadisticas_zona(sur_data, 'Sur')

    # Configurar figura
    fig = plt.figure(figsize=(30, 20))

    gs = GridSpec(3, 4, figure=fig,
                  height_ratios=[0.10, 0.70, 0.20],
                  width_ratios=[0.30, 0.30, 0.30, 0.10],
                  hspace=0.08, wspace=0.10)

    # Título principal
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'Análisis Segunda Vuelta, 2025 - Resultados Nacionales',
                   ha='center', va='center', fontsize=32, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Mapa Zona Norte
    ax_norte = fig.add_subplot(gs[1, 0])

    if not norte_data.empty:
        norte_data['color'] = norte_data['diferencia_pct'].apply(asignar_color_diferencia)
        norte_data.plot(ax=ax_norte, color=norte_data['color'], edgecolor='black', linewidth=0.5)

        ax_norte.set_title('ZONA NORTE\n(Arica y Parinacota a Coquimbo)',
                           fontsize=16, fontweight='bold', pad=10)
    else:
        ax_norte.text(0.5, 0.5, 'SIN DATOS\nPARA ZONA NORTE',
                      ha='center', va='center',
                      fontsize=14, fontweight='bold',
                      color='gray')
        ax_norte.set_title('ZONA NORTE', fontsize=16, fontweight='bold', pad=10)

    ax_norte.set_axis_off()
    ax_norte.set_aspect('equal')

    # Mapa Zona Centro
    ax_centro = fig.add_subplot(gs[1, 1])

    if not centro_data.empty:
        centro_data['color'] = centro_data['diferencia_pct'].apply(asignar_color_diferencia)
        centro_data.plot(ax=ax_centro, color=centro_data['color'], edgecolor='black', linewidth=0.5)

        ax_centro.set_title('ZONA CENTRO\n(Valparaíso a Biobío + RM)',
                            fontsize=16, fontweight='bold', pad=10)
    else:
        ax_centro.text(0.5, 0.5, 'SIN DATOS\nPARA ZONA CENTRO',
                       ha='center', va='center',
                       fontsize=14, fontweight='bold',
                       color='gray')
        ax_centro.set_title('ZONA CENTRO', fontsize=16, fontweight='bold', pad=10)

    ax_centro.set_axis_off()
    ax_centro.set_aspect('equal')

    # Mapa Zona Sur
    ax_sur = fig.add_subplot(gs[1, 2])

    if not sur_data.empty:
        sur_data['color'] = sur_data['diferencia_pct'].apply(asignar_color_diferencia)
        sur_data.plot(ax=ax_sur, color=sur_data['color'], edgecolor='black', linewidth=0.5)

        ax_sur.set_title('ZONA SUR\n(Araucanía a Magallanes)',
                         fontsize=16, fontweight='bold', pad=10)
    else:
        ax_sur.text(0.5, 0.5, 'SIN DATOS\nPARA ZONA SUR',
                    ha='center', va='center',
                    fontsize=14, fontweight='bold',
                    color='gray')
        ax_sur.set_title('ZONA SUR', fontsize=16, fontweight='bold', pad=10)

    ax_sur.set_axis_off()
    ax_sur.set_aspect('equal')

    # Leyenda de colores
    ax_leyenda = fig.add_subplot(gs[1, 3])
    ax_leyenda.set_axis_off()

    ax_leyenda.text(0.5, 0.95, 'Simbología',
                    ha='center', va='top',
                    fontsize=18, fontweight='bold',
                    transform=ax_leyenda.transAxes)

    # Elementos de la leyenda
    leyenda_elementos = [
        mpatches.Patch(color='#B91C1C', label='Jara +50% o más'),
        mpatches.Patch(color='#C92A2A', label='Jara +40% a +50%'),
        mpatches.Patch(color='#DA4A4A', label='Jara +30% a +40%'),
        mpatches.Patch(color='#E86969', label='Jara +20% a +30%'),
        mpatches.Patch(color='#F28787', label='Jara +10% a +20%'),
        mpatches.Patch(color='#F8A0A0', label='Jara +1% a +10%'),
        mpatches.Patch(color='#9CA3AF', label='Empate técnico'),
        mpatches.Patch(color='#8BB2F0', label='Kast +1% a +10%'),
        mpatches.Patch(color='#5E91E8', label='Kast +10% a +20%'),
        mpatches.Patch(color='#3D76D1', label='Kast +20% a +30%'),
        mpatches.Patch(color='#2A58A6', label='Kast +30% a +40%'),
        mpatches.Patch(color='#1A3D7C', label='Kast +40% a +50%'),
        mpatches.Patch(color='#0F2D5C', label='Kast +50% o más'),
        mpatches.Patch(color='#D3D3D3', label='Sin datos'),
    ]

    ax_leyenda.legend(handles=leyenda_elementos,
                      loc='center',
                      fontsize=9,
                      title='Diferencia (Jara% - Kast%)',
                      title_fontsize=11,
                      framealpha=0.9)

    # Gráfico de barras comparativo
    ax_estadisticas = fig.add_subplot(gs[2, :3])
    ax_estadisticas.set_axis_off()

    zonas = ['Norte', 'Centro', 'Sur']
    jara_porcentajes = [estadisticas_norte['jara_pct'], estadisticas_centro['jara_pct'], estadisticas_sur['jara_pct']]
    kast_porcentajes = [estadisticas_norte['kast_pct'], estadisticas_centro['kast_pct'], estadisticas_sur['kast_pct']]

    x = np.arange(len(zonas))
    width = 0.35

    # Barras para Jara
    bars_jara = ax_estadisticas.bar(x - width / 2, jara_porcentajes, width,
                                    label='Jara', color='#E54540', edgecolor='black')
    # Barras para Kast
    bars_kast = ax_estadisticas.bar(x + width / 2, kast_porcentajes, width,
                                    label='Kast', color='#2D426C', edgecolor='black')

    ax_estadisticas.set_xlabel('Zona', fontsize=14, fontweight='bold')
    ax_estadisticas.set_ylabel('Porcentaje (%)', fontsize=14, fontweight='bold')
    ax_estadisticas.set_title('COMPARATIVA POR ZONAS - RESULTADOS PROMEDIO',
                              fontsize=16, fontweight='bold', pad=15)
    ax_estadisticas.set_xticks(x)
    ax_estadisticas.set_xticklabels(zonas, fontsize=12)
    ax_estadisticas.legend(fontsize=12)

    # Agregar valores en barras
    for bars in [bars_jara, bars_kast]:
        for bar in bars:
            height = bar.get_height()
            ax_estadisticas.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                                 f'{height:.1f}%',
                                 ha='center', va='bottom',
                                 fontsize=11, fontweight='bold')

    ax_estadisticas.grid(axis='y', alpha=0.3)
    ax_estadisticas.set_ylim(0, max(max(jara_porcentajes), max(kast_porcentajes)) * 1.2)

    # Información adicional
    ax_info = fig.add_subplot(gs[2, 3])
    ax_info.set_axis_off()

    info_text = (
        f"ESTADÍSTICAS POR ZONA\n\n"
        f"NORTE:\n"
        f"• Comunas: {estadisticas_norte['total_comunas']}\n"
        f"• Jara gana: {estadisticas_norte['jara_gana']}\n"
        f"• Kast gana: {estadisticas_norte['kast_gana']}\n"
        f"• Empates: {estadisticas_norte['empates']}\n\n"
        f"CENTRO:\n"
        f"• Comunas: {estadisticas_centro['total_comunas']}\n"
        f"• Jara gana: {estadisticas_centro['jara_gana']}\n"
        f"• Kast gana: {estadisticas_centro['kast_gana']}\n"
        f"• Empates: {estadisticas_centro['empates']}\n\n"
        f"SUR:\n"
        f"• Comunas: {estadisticas_sur['total_comunas']}\n"
        f"• Jara gana: {estadisticas_sur['jara_gana']}\n"
        f"• Kast gana: {estadisticas_sur['kast_gana']}\n"
        f"• Empates: {estadisticas_sur['empates']}"
    )

    ax_info.text(0.05, 0.95, info_text,
                 ha='left', va='top',
                 fontsize=10,
                 transform=ax_info.transAxes,
                 linespacing=1.4)

    # Pie de página
    ax_pie = fig.add_axes([0.1, 0.02, 0.8, 0.03])
    ax_pie.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Chile mapa completo | Generado: {fecha} | Nota: Islas (Pascua y Juan Fernández) no incluidas"
    ax_pie.text(0.5, 0.5, info_text,
                ha='center', va='center',
                fontsize=10, color='gray',
                transform=ax_pie.transAxes)

    plt.tight_layout(rect=[0.02, 0.05, 0.98, 0.98])
    output_path = os.path.join(output_dir, "CHILE_MAP_COMPLETO.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Mapa de Chile completo: {output_path}")
    return output_path


def crear_reporte_nacional_completo(mapa_data, output_dir):
    """
    Crea reporte nacional completo con estadísticas detalladas.

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el reporte.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 📊 Generando reporte nacional completo")

    # Filtrar datos con resultados
    datos_nacionales = mapa_data[mapa_data['diferencia_pct'].notna()].copy()

    if datos_nacionales.empty:
        print(f" ⚠ No hay datos suficientes para el reporte nacional")
        return None

    # Calcular totales nacionales
    votos_emitidos = datos_nacionales['emitidos_votos'].sum()
    votos_blanco = datos_nacionales['blanco_votos'].sum()
    votos_nulo = datos_nacionales['nulo_votos'].sum()
    votos_validos = votos_emitidos - votos_blanco - votos_nulo

    jara_votos_total = datos_nacionales['jara_votos'].sum()
    kast_votos_total = datos_nacionales['kast_votos'].sum()

    # Calcular porcentajes nacionales
    if votos_validos > 0:
        jara_nacional_pct = (jara_votos_total / votos_validos) * 100
        kast_nacional_pct = (kast_votos_total / votos_validos) * 100
    else:
        jara_nacional_pct = datos_nacionales['jara_pct'].mean()
        kast_nacional_pct = datos_nacionales['kast_pct'].mean()

    dif_nacional_pct = jara_nacional_pct - kast_nacional_pct

    # Estadísticas por comuna
    total_comunas = len(datos_nacionales)
    jara_gana = (datos_nacionales['diferencia_pct'] > 0).sum()
    kast_gana = (datos_nacionales['diferencia_pct'] < 0).sum()
    empates = (datos_nacionales['diferencia_pct'] == 0).sum()

    # Top 5 comunas por candidato
    comunas_jara_top = datos_nacionales.sort_values('jara_pct', ascending=False).head(5)
    comunas_kast_top = datos_nacionales.sort_values('kast_pct', ascending=False).head(5)

    # Configurar figura
    fig = plt.figure(figsize=(28, 20))

    gs = GridSpec(4, 3, figure=fig,
                  height_ratios=[0.08, 0.42, 0.42, 0.08],
                  width_ratios=[0.33, 0.34, 0.33],
                  hspace=0.12, wspace=0.10)

    # Título principal
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'REPORTE NACIONAL COMPLETO',
                   ha='center', va='center', fontsize=32, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Panel Kast
    ax_kast = fig.add_subplot(gs[1, 0])
    ax_kast.set_axis_off()

    rect_kast = Rectangle((0, 0), 1, 1, transform=ax_kast.transAxes,
                          facecolor='#2D426C', alpha=0.1, edgecolor='#2D426C', linewidth=2)
    ax_kast.add_patch(rect_kast)

    ax_kast.text(0.5, 0.95, 'José Antonio Kast',
                 ha='center', va='top', fontsize=18, fontweight='bold',
                 transform=ax_kast.transAxes,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='black', alpha=0.9))

    ax_kast.text(0.5, 0.7, f'RESULTADO NACIONAL\n{kast_nacional_pct:.1f}%',
                 ha='center', va='center', fontsize=28, fontweight='bold',
                 color='#2D426C', transform=ax_kast.transAxes)

    votos_kast_text = f'{kast_votos_total:,.0f} votos'.replace(',', '.')
    ax_kast.text(0.5, 0.5, votos_kast_text,
                 ha='center', va='center', fontsize=18,
                 transform=ax_kast.transAxes)

    info_kast = f"Gana en {kast_gana} comunas"
    ax_kast.text(0.5, 0.35, info_kast,
                 ha='center', va='center', fontsize=16,
                 transform=ax_kast.transAxes)

    # Panel Jara
    ax_jara = fig.add_subplot(gs[1, 2])
    ax_jara.set_axis_off()

    rect_jara = Rectangle((0, 0), 1, 1, transform=ax_jara.transAxes,
                          facecolor='#E54540', alpha=0.1, edgecolor='#E54540', linewidth=2)
    ax_jara.add_patch(rect_jara)

    ax_jara.text(0.5, 0.95, 'Jeannette Jara',
                 ha='center', va='top', fontsize=18, fontweight='bold',
                 transform=ax_jara.transAxes,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='black', alpha=0.9))

    ax_jara.text(0.5, 0.7, f'RESULTADO NACIONAL\n{jara_nacional_pct:.1f}%',
                 ha='center', va='center', fontsize=28, fontweight='bold',
                 color='#E54540', transform=ax_jara.transAxes)

    votos_jara_text = f'{jara_votos_total:,.0f} votos'.replace(',', '.')
    ax_jara.text(0.5, 0.5, votos_jara_text,
                 ha='center', va='center', fontsize=18,
                 transform=ax_jara.transAxes)

    info_jara = f"Gana en {jara_gana} comunas"
    ax_jara.text(0.5, 0.35, info_jara,
                 ha='center', va='center', fontsize=16,
                 transform=ax_jara.transAxes)

    # Panel central (diferencia)
    ax_centro = fig.add_subplot(gs[1, 1])
    ax_centro.set_axis_off()

    dif_color = '#E54540' if dif_nacional_pct > 0 else '#2D426C' if dif_nacional_pct < 0 else 'gray'

    dif_text = f'DIFERENCIA NACIONAL\n{dif_nacional_pct:+.1f}%'

    ax_centro.text(0.5, 0.8, dif_text,
                   ha='center', va='center', fontsize=36, fontweight='bold',
                   color=dif_color, transform=ax_centro.transAxes)

    comunas_text = f"{total_comunas} comunas con datos"

    ax_centro.text(0.5, 0.6, comunas_text,
                   ha='center', va='center', fontsize=18,
                   transform=ax_centro.transAxes)

    empates_text = f"Empates: {empates} comunas"

    ax_centro.text(0.5, 0.5, empates_text,
                   ha='center', va='center', fontsize=16,
                   color='gray', transform=ax_centro.transAxes)

    # Top 5 comunas Kast
    ax_top_kast = fig.add_subplot(gs[2, 0])

    if not comunas_kast_top.empty:
        comunas_nombres = comunas_kast_top['NOM_COM'].tolist()
        porcentajes = comunas_kast_top['kast_pct'].tolist()

        # Acortar nombres largos
        comunas_nombres_short = []
        for nombre in comunas_nombres:
            if len(nombre) > 15:
                nombre = nombre[:12] + '...'
            comunas_nombres_short.append(nombre)

        bars = ax_top_kast.barh(range(len(comunas_nombres_short)), porcentajes,
                                color='#2D426C', edgecolor='black', height=0.6)

        ax_top_kast.set_yticks(range(len(comunas_nombres_short)))
        ax_top_kast.set_yticklabels(comunas_nombres_short, fontsize=12)
        ax_top_kast.set_xlabel('Porcentaje de Kast (%)', fontsize=14, fontweight='bold')
        ax_top_kast.set_title('TOP 5 COMUNAS - KAST GANA', fontsize=16, fontweight='bold', pad=10)

        # Agregar valores en barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax_top_kast.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                             f'{width:.1f}%',
                             ha='left', va='center',
                             fontsize=12, fontweight='bold')

        ax_top_kast.set_xlim(0, max(porcentajes) * 1.3 if max(porcentajes) > 0 else 100)
        ax_top_kast.grid(axis='x', alpha=0.3)
    else:
        ax_top_kast.text(0.5, 0.5, 'No hay comunas donde Kast gane',
                         ha='center', va='center',
                         transform=ax_top_kast.transAxes,
                         fontsize=14, fontweight='bold',
                         color='gray')
        ax_top_kast.set_title('TOP 5 COMUNAS - KAST GANA', fontsize=16, fontweight='bold', pad=10)
        ax_top_kast.set_axis_off()

    # Top 5 comunas Jara
    ax_top_jara = fig.add_subplot(gs[2, 2])

    if not comunas_jara_top.empty:
        comunas_nombres = comunas_jara_top['NOM_COM'].tolist()
        porcentajes = comunas_jara_top['jara_pct'].tolist()

        # Acortar nombres largos
        comunas_nombres_short = []
        for nombre in comunas_nombres:
            if len(nombre) > 15:
                nombre = nombre[:12] + '...'
            comunas_nombres_short.append(nombre)

        bars = ax_top_jara.barh(range(len(comunas_nombres_short)), porcentajes,
                                color='#E54540', edgecolor='black', height=0.6)

        ax_top_jara.set_yticks(range(len(comunas_nombres_short)))
        ax_top_jara.set_yticklabels(comunas_nombres_short, fontsize=12)
        ax_top_jara.set_xlabel('Porcentaje de Jara (%)', fontsize=14, fontweight='bold')
        ax_top_jara.set_title('TOP 5 COMUNAS - JARA GANA', fontsize=16, fontweight='bold', pad=10)

        # Agregar valores en barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax_top_jara.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                             f'{width:.1f}%',
                             ha='left', va='center',
                             fontsize=12, fontweight='bold')

        ax_top_jara.set_xlim(0, max(porcentajes) * 1.3 if max(porcentajes) > 0 else 100)
        ax_top_jara.grid(axis='x', alpha=0.3)
    else:
        ax_top_jara.text(0.5, 0.5, 'No hay comunas donde Jara gane',
                         ha='center', va='center',
                         transform=ax_top_jara.transAxes,
                         fontsize=14, fontweight='bold',
                         color='gray')
        ax_top_jara.set_title('TOP 5 COMUNAS - JARA GANA', fontsize=16, fontweight='bold', pad=10)
        ax_top_jara.set_axis_off()

    # Estadísticas de votos
    ax_estadisticas = fig.add_subplot(gs[2, 1])
    ax_estadisticas.set_axis_off()

    # Calcular porcentajes de votos
    votos_nulo_pct = (votos_nulo / votos_emitidos) * 100 if votos_emitidos > 0 else 0
    votos_blanco_pct = (votos_blanco / votos_emitidos) * 100 if votos_emitidos > 0 else 0
    votos_validos_pct = (votos_validos / votos_emitidos) * 100 if votos_emitidos > 0 else 0

    # Formatear números con separador de miles
    votos_emitidos_str = f'{votos_emitidos:,.0f}'.replace(',', '.')
    votos_validos_str = f'{votos_validos:,.0f}'.replace(',', '.')
    votos_nulo_str = f'{votos_nulo:,.0f}'.replace(',', '.')
    votos_blanco_str = f'{votos_blanco:,.0f}'.replace(',', '.')

    estadisticas_text = (
        f"ESTADÍSTICAS NACIONALES DE VOTOS\n\n"
        f"Votos emitidos: {votos_emitidos_str}\n"
        f"Votos válidos: {votos_validos_str} ({votos_validos_pct:.1f}%)\n"
        f"Votos nulos: {votos_nulo_str} ({votos_nulo_pct:.1f}%)\n"
        f"Votos en blanco: {votos_blanco_str} ({votos_blanco_pct:.1f}%)"
    )

    ax_estadisticas.text(0.5, 0.7, estadisticas_text,
                         ha='center', va='center', fontsize=16,
                         transform=ax_estadisticas.transAxes, linespacing=1.6)

    # Pie de página
    ax_fondo = fig.add_subplot(gs[3, :])
    ax_fondo.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Reporte Nacional | Generado: {fecha}"
    ax_fondo.text(0.5, 0.5, info_text,
                  ha='center', va='center',
                  fontsize=12, color='gray',
                  transform=ax_fondo.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    output_path = os.path.join(output_dir, "REPORTE_NACIONAL_COMPLETO.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Reporte nacional completo guardado: {output_path}")
    return output_path


def crear_tabla_capitales_regionales(mapa_data, output_dir):
    """
    Crea tabla de resultados en capitales regionales.

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar la tabla.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 📋 Generando tabla de capitales regionales")

    # Definir capitales regionales
    capitales_regionales = [
        {"region_num": 15, "region_nombre": "Arica y Parinacota", "capital": "Arica"},
        {"region_num": 1, "region_nombre": "Tarapacá", "capital": "Iquique"},
        {"region_num": 2, "region_nombre": "Antofagasta", "capital": "Antofagasta"},
        {"region_num": 3, "region_nombre": "Atacama", "capital": "Copiapó"},
        {"region_num": 4, "region_nombre": "Coquimbo", "capital": "La Serena"},
        {"region_num": 5, "region_nombre": "Valparaíso", "capital": "Valparaíso"},
        {"region_num": 13, "region_nombre": "Metropolitana", "capital": "Santiago"},
        {"region_num": 6, "region_nombre": "O'Higgins", "capital": "Rancagua"},
        {"region_num": 7, "region_nombre": "Maule", "capital": "Talca"},
        {"region_num": 16, "region_nombre": "Ñuble", "capital": "Chillán"},
        {"region_num": 8, "region_nombre": "Biobío", "capital": "Concepción"},
        {"region_num": 9, "region_nombre": "Araucanía", "capital": "Temuco"},
        {"region_num": 14, "region_nombre": "Los Ríos", "capital": "Valdivia"},
        {"region_num": 10, "region_nombre": "Los Lagos", "capital": "Puerto Montt"},
        {"region_num": 11, "region_nombre": "Aysén", "capital": "Coyhaique"},
        {"region_num": 12, "region_nombre": "Magallanes", "capital": "Punta Arenas"}
    ]

    datos_capitales = []
    for capital_info in capitales_regionales:
        region_num = capital_info["region_num"]
        capital_nombre = capital_info["capital"]

        # Buscar datos de la capital
        capital_data = mapa_data[
            (mapa_data['REGION_NUM'] == region_num) &
            (mapa_data['NOM_COM'].str.contains(capital_nombre, case=False, na=False))
            ].copy()

        if not capital_data.empty:
            capital_row = capital_data.iloc[0]

            jara_pct = capital_row['jara_pct'] if 'jara_pct' in capital_row and not pd.isna(
                capital_row['jara_pct']) else 0
            kast_pct = capital_row['kast_pct'] if 'kast_pct' in capital_row and not pd.isna(
                capital_row['kast_pct']) else 0

            # Determinar ganador
            if jara_pct > kast_pct:
                ganador = "JARA"
                color_ganador = "#E54540"
            elif kast_pct > jara_pct:
                ganador = "KAST"
                color_ganador = "#2D426C"
            else:
                ganador = "EMPATE"
                color_ganador = "gray"

            diferencia = jara_pct - kast_pct

            datos_capitales.append({
                "Región": capital_info["region_nombre"],
                "Capital": capital_nombre,
                "Jara (%)": jara_pct,
                "Kast (%)": kast_pct,
                "Diferencia": diferencia,
                "Ganador": ganador,
                "Color": color_ganador
            })
        else:
            print(f" ⚠ No se encontraron datos para {capital_nombre} (Región {region_num})")

    if not datos_capitales:
        print(f" ⚠ No hay datos para capitales regionales")
        return None

    # Crear DataFrame
    df_capitales = pd.DataFrame(datos_capitales)

    # Configurar figura
    fig = plt.figure(figsize=(22, 14))

    gs = GridSpec(3, 1, figure=fig, height_ratios=[0.10, 0.80, 0.10], hspace=0.05)

    # Título
    ax_titulo = fig.add_subplot(gs[0])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'RESULTADOS EN CAPITALES REGIONALES DE CHILE',
                   ha='center', va='center', fontsize=28, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Tabla
    ax_tabla = fig.add_subplot(gs[1])
    ax_tabla.set_axis_off()

    # Preparar datos para tabla
    tabla_data = []
    for i, row in df_capitales.iterrows():
        tabla_data.append([
            row['Región'],
            row['Capital'],
            f"{row['Jara (%)']:.1f}%",
            f"{row['Kast (%)']:.1f}%",
            f"{row['Diferencia']:+.1f}%",
            row['Ganador']
        ])

    column_labels = ['Región', 'Capital', 'Jara (%)', 'Kast (%)', 'Diferencia', 'Ganador']

    colores_filas = ['#f5f5f5', 'white']

    # Crear tabla
    tabla = ax_tabla.table(cellText=tabla_data,
                           colLabels=column_labels,
                           cellLoc='center',
                           loc='center',
                           colColours=['#e0e0e0'] * 6,
                           cellColours=None)

    tabla.auto_set_font_size(False)
    tabla.set_fontsize(11)
    tabla.scale(1.2, 2.2)

    # Formatear encabezados
    for j in range(len(column_labels)):
        cell = tabla[(0, j)]
        cell.set_text_props(fontweight='bold', fontsize=12)
        cell.set_facecolor('#2D426C')
        cell.set_text_props(color='white')

    # Formatear celdas de datos
    for i in range(len(tabla_data) + 1):
        for j in range(len(column_labels)):
            cell = tabla[(i, j)]

            if i > 0:
                cell.set_facecolor(colores_filas[i % 2])

            # Resaltar ganador
            if j == 5 and i > 0:
                ganador = tabla_data[i - 1][5]
                if ganador == "JARA":
                    cell.set_facecolor('#FFE5E5')
                    cell.set_text_props(color='#E54540', fontweight='bold')
                elif ganador == "KAST":
                    cell.set_facecolor('#E5EDFF')
                    cell.set_text_props(color='#2D426C', fontweight='bold')
                else:
                    cell.set_facecolor('#F0F0F0')
                    cell.set_text_props(color='gray', fontweight='bold')

    # Resumen
    ax_resumen = fig.add_subplot(gs[2])
    ax_resumen.set_axis_off()

    total_capitales = len(df_capitales)
    jara_gana = (df_capitales['Ganador'] == 'JARA').sum()
    kast_gana = (df_capitales['Ganador'] == 'KAST').sum()
    empates = (df_capitales['Ganador'] == 'EMPATE').sum()

    jara_promedio = df_capitales['Jara (%)'].mean()
    kast_promedio = df_capitales['Kast (%)'].mean()
    diferencia_promedio = jara_promedio - kast_promedio

    resumen_text = (
        f"RESUMEN: JARA gana en {jara_gana} capitales regionales, KAST gana en {kast_gana} capitales regionales"
    )

    if empates > 0:
        resumen_text += f", {empates} empates"

    resumen_text += f". Promedio: Jara {jara_promedio:.1f}% - Kast {kast_promedio:.1f}% (Diferencia: {diferencia_promedio:+.1f}%)"

    ax_resumen.text(0.5, 0.7, resumen_text,
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    transform=ax_resumen.transAxes)

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    nota_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Capitales Regionales | Generado: {fecha}"
    ax_resumen.text(0.5, 0.3, nota_text,
                    ha='center', va='center', fontsize=10, color='gray',
                    transform=ax_resumen.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    output_path = os.path.join(output_dir, "TABLA_CAPITALES_REGIONALES.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Tabla de capitales regionales guardada: {output_path}")

    # Guardar también como CSV
    csv_path = os.path.join(output_dir, "TABLA_CAPITALES_REGIONALES.csv")
    df_capitales.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f" ✓ Datos de capitales regionales guardados como CSV: {csv_path}")

    return output_path


def crear_reporte_gran_santiago_completo(mapa_data, output_dir):
    """
    Crea reporte completo para el Gran Santiago.

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el reporte.

    Returns:
        str or None: Ruta del archivo guardado o None si falla.
    """
    print(f" 📊 Generando reporte completo para Gran Santiago")

    # Filtrar datos del Gran Santiago
    conurbacion_norm = [normalizar_nombre(comuna) for comuna in CONURBACION_SANTIAGO]
    gran_santiago_data = mapa_data[
        (mapa_data['REGION_NUM'] == 13) &
        (mapa_data['NOM_COM_NORM'].isin(conurbacion_norm)) &
        (mapa_data['diferencia_pct'].notna())
        ].copy()

    if gran_santiago_data.empty:
        print(f" ⚠ No hay datos suficientes para el reporte de Gran Santiago")
        return None

    # Calcular estadísticas
    jara_promedio, kast_promedio = calcular_promedio_regional_correcto(gran_santiago_data)
    dif_promedio = jara_promedio - kast_promedio

    # Separar comunas por ganador
    comunas_jara = gran_santiago_data[gran_santiago_data['diferencia_pct'] > 0].copy()
    comunas_kast = gran_santiago_data[gran_santiago_data['diferencia_pct'] < 0].copy()

    # Top 5 comunas por candidato
    comunas_jara_top = comunas_jara.sort_values('jara_pct', ascending=False).head(5)
    comunas_kast_top = comunas_kast.sort_values('kast_pct', ascending=False).head(5)

    # URLs de fotos de candidatos
    jara_foto_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/2/2d/Live_Especial_Mujeres_Comit%C3%A9_Pol%C3%ADtico%2C_Ministra_Jannette_Jara_%28cropped%29.jpg",
        "https://www.latercera.com/resizer/v2/W4LV4DZTLVG2JLA4FSNXGSZ53U.jpg?auth=ac72355711cd6ba404761233d4e8c5db88b09d7e1383330b23f44f6fe4c4da02&smart=true&width=800&height=533&quality=70",
        "https://media.biobiochile.cl/wp-content/uploads/2022/03/Jannette-Jara-1-1200x800.jpg"
    ]

    kast_foto_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Jos%C3%A9_Antonio_Kast_en_2025_%28cropped%29.jpg/960px-Jos%C3%A9_Antonio_Kast_en_2025_%28cropped%29.jpg",
        "https://www.latercera.com/resizer/v2/CHVAFJVR7FCPJNPW2WSY7O3GEE.jpg?auth=4283b658dda7f5ed3f2e4e014eefc4fa4cf096e36131ed2620338bd73bf0b73a&smart=true&width=800&height=533&quality=70",
        "https://media.biobiochile.cl/wp-content/uploads/2021/11/kast-1-1200x800.jpg"
    ]

    def descargar_imagen(urls, nombre_candidato):
        """Descarga imagen de candidato desde URLs alternativas."""
        for url in urls:
            try:
                print(f"  Intentando descargar imagen de {nombre_candidato} desde: {url[:60]}...")

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9',
                    'Referer': 'https://www.google.com/'
                }

                response = requests.get(url, headers=headers, timeout=10, stream=True)

                if response.status_code == 200:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    with open(temp_file.name, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    img = Image.open(temp_file.name)

                    os.unlink(temp_file.name)

                    print(f"  ✓ Imagen de {nombre_candidato} descargada correctamente")
                    return img

            except Exception as e:
                print(f"  ⚠ Error con URL {url[:60]}: {e}")
                continue

        print(f"  ✗ No se pudo descargar imagen de {nombre_candidato}, usando placeholder")
        return None

    # Descargar imágenes
    print(" 📷 Descargando imágenes de candidatos...")
    jara_img = descargar_imagen(jara_foto_urls, "Jeannette Jara")
    kast_img = descargar_imagen(kast_foto_urls, "José Antonio Kast")

    # Configurar figura
    fig = plt.figure(figsize=(28, 20))

    gs = GridSpec(4, 3, figure=fig,
                  height_ratios=[0.08, 0.42, 0.42, 0.08],
                  width_ratios=[0.33, 0.34, 0.33],
                  hspace=0.12, wspace=0.10)

    # Título principal
    ax_titulo = fig.add_subplot(gs[0, :])
    ax_titulo.set_axis_off()
    ax_titulo.text(0.5, 0.5, 'REPORTE GRAN SANTIAGO',
                   ha='center', va='center', fontsize=32, fontweight='bold',
                   transform=ax_titulo.transAxes)

    # Panel Kast
    ax_kast = fig.add_subplot(gs[1, 0])
    ax_kast.set_axis_off()

    rect_kast = Rectangle((0, 0), 1, 1, transform=ax_kast.transAxes,
                          facecolor='#2D426C', alpha=0.1, edgecolor='#2D426C', linewidth=2)
    ax_kast.add_patch(rect_kast)

    ax_kast.text(0.5, 0.95, 'José Antonio Kast (Retador - Derecha)',
                 ha='center', va='top', fontsize=18, fontweight='bold',
                 transform=ax_kast.transAxes,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='black', alpha=0.9))

    # Mostrar imagen de Kast si está disponible
    if kast_img is not None:
        try:
            kast_img_resized = kast_img.resize((250, 300), Image.Resampling.LANCZOS)
            ax_kast.imshow(kast_img_resized, aspect='auto', extent=[0.2, 0.8, 0.4, 0.8])
        except:
            ax_kast.text(0.5, 0.6, 'José Antonio Kast\n\nRetador - Derecha',
                         ha='center', va='center', fontsize=16,
                         transform=ax_kast.transAxes)
    else:
        ax_kast.text(0.5, 0.6, 'José Antonio Kast\n\nRetador - Derecha',
                     ha='center', va='center', fontsize=16,
                     transform=ax_kast.transAxes)

    ax_kast.text(0.5, 0.1, f'Resultado: {kast_promedio:.1f}%',
                 ha='center', va='center', fontsize=28, fontweight='bold',
                 color='#2D426C', transform=ax_kast.transAxes,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='black', alpha=0.9))

    # Panel Jara
    ax_jara = fig.add_subplot(gs[1, 2])
    ax_jara.set_axis_off()

    rect_jara = Rectangle((0, 0), 1, 1, transform=ax_jara.transAxes,
                          facecolor='#E54540', alpha=0.1, edgecolor='#E54540', linewidth=2)
    ax_jara.add_patch(rect_jara)

    ax_jara.text(0.5, 0.95, 'Jeannette Jara (Oficialista - Izquierda)',
                 ha='center', va='top', fontsize=18, fontweight='bold',
                 transform=ax_jara.transAxes,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='black', alpha=0.9))

    # Mostrar imagen de Jara si está disponible
    if jara_img is not None:
        try:
            jara_img_resized = jara_img.resize((250, 300), Image.Resampling.LANCZOS)
            ax_jara.imshow(jara_img_resized, aspect='auto', extent=[0.2, 0.8, 0.4, 0.8])
        except:
            ax_jara.text(0.5, 0.6, 'Jeannette Jara\n\nOficialista - Izquierda',
                         ha='center', va='center', fontsize=16,
                         transform=ax_jara.transAxes)
    else:
        ax_jara.text(0.5, 0.6, 'Jeannette Jara\n\nOficialista - Izquierda',
                     ha='center', va='center', fontsize=16,
                     transform=ax_jara.transAxes)

    ax_jara.text(0.5, 0.1, f'Resultado: {jara_promedio:.1f}%',
                 ha='center', va='center', fontsize=28, fontweight='bold',
                 color='#E54540', transform=ax_jara.transAxes,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='black', alpha=0.9))

    # Panel central (estadísticas)
    ax_centro = fig.add_subplot(gs[1, 1])
    ax_centro.set_axis_off()

    total_comunas = len(gran_santiago_data)
    jara_gana = len(comunas_jara)
    kast_gana = len(comunas_kast)
    empates = len(gran_santiago_data[gran_santiago_data['diferencia_pct'] == 0])

    dif_color = '#E54540' if dif_promedio > 0 else '#2D426C' if dif_promedio < 0 else 'gray'

    dif_text = f'DIFERENCIA\n{dif_promedio:+.1f}%'

    ax_centro.text(0.5, 0.7, dif_text,
                   ha='center', va='center', fontsize=36, fontweight='bold',
                   color=dif_color, transform=ax_centro.transAxes)

    info_text = f"{total_comunas} comunas analizadas"

    ax_centro.text(0.5, 0.4, info_text,
                   ha='center', va='center', fontsize=18,
                   transform=ax_centro.transAxes)

    # Top 5 comunas Kast
    ax_top_kast = fig.add_subplot(gs[2, 0])

    if not comunas_kast_top.empty:
        comunas_nombres = comunas_kast_top['NOM_COM'].tolist()
        porcentajes = comunas_kast_top['kast_pct'].tolist()

        # Acortar nombres largos
        comunas_nombres_short = []
        for nombre in comunas_nombres:
            if len(nombre) > 15:
                nombre = nombre[:12] + '...'
            comunas_nombres_short.append(nombre)

        bars = ax_top_kast.barh(range(len(comunas_nombres_short)), porcentajes,
                                color='#2D426C', edgecolor='black', height=0.6)

        ax_top_kast.set_yticks(range(len(comunas_nombres_short)))
        ax_top_kast.set_yticklabels(comunas_nombres_short, fontsize=12)
        ax_top_kast.set_xlabel('Porcentaje de Kast (%)', fontsize=14, fontweight='bold')
        ax_top_kast.set_title('TOP 5 COMUNAS - KAST GANA', fontsize=16, fontweight='bold', pad=10)

        # Agregar valores en barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax_top_kast.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                             f'{width:.1f}%',
                             ha='left', va='center',
                             fontsize=12, fontweight='bold')

        ax_top_kast.set_xlim(0, max(porcentajes) * 1.3 if max(porcentajes) > 0 else 100)
        ax_top_kast.grid(axis='x', alpha=0.3)
    else:
        ax_top_kast.text(0.5, 0.5, 'No hay comunas donde Kast gane',
                         ha='center', va='center',
                         transform=ax_top_kast.transAxes,
                         fontsize=14, fontweight='bold',
                         color='gray')
        ax_top_kast.set_title('TOP 5 COMUNAS - KAST GANA', fontsize=16, fontweight='bold', pad=10)
        ax_top_kast.set_axis_off()

    # Top 5 comunas Jara
    ax_top_jara = fig.add_subplot(gs[2, 2])

    if not comunas_jara_top.empty:
        comunas_nombres = comunas_jara_top['NOM_COM'].tolist()
        porcentajes = comunas_jara_top['jara_pct'].tolist()

        # Acortar nombres largos
        comunas_nombres_short = []
        for nombre in comunas_nombres:
            if len(nombre) > 15:
                nombre = nombre[:12] + '...'
            comunas_nombres_short.append(nombre)

        bars = ax_top_jara.barh(range(len(comunas_nombres_short)), porcentajes,
                                color='#E54540', edgecolor='black', height=0.6)

        ax_top_jara.set_yticks(range(len(comunas_nombres_short)))
        ax_top_jara.set_yticklabels(comunas_nombres_short, fontsize=12)
        ax_top_jara.set_xlabel('Porcentaje de Jara (%)', fontsize=14, fontweight='bold')
        ax_top_jara.set_title('TOP 5 COMUNAS - JARA GANA', fontsize=16, fontweight='bold', pad=10)

        # Agregar valores en barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax_top_jara.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                             f'{width:.1f}%',
                             ha='left', va='center',
                             fontsize=12, fontweight='bold')

        ax_top_jara.set_xlim(0, max(porcentajes) * 1.3 if max(porcentajes) > 0 else 100)
        ax_top_jara.grid(axis='x', alpha=0.3)
    else:
        ax_top_jara.text(0.5, 0.5, 'No hay comunas donde Jara gane',
                         ha='center', va='center',
                         transform=ax_top_jara.transAxes,
                         fontsize=14, fontweight='bold',
                         color='gray')
        ax_top_jara.set_title('TOP 5 COMUNAS - JARA GANA', fontsize=16, fontweight='bold', pad=10)
        ax_top_jara.set_axis_off()

    # Estadísticas generales
    ax_info = fig.add_subplot(gs[2, 1])
    ax_info.set_axis_off()

    info_text = (
        f"ESTADÍSTICAS GRAN SANTIAGO\n\n"
        f"JARA gana en: {jara_gana} comunas\n"
        f"KAST gana en: {kast_gana} comunas\n"
        f"Empates: {empates} comunas\n\n"
        f"Total comunas: {total_comunas}"
    )

    ax_info.text(0.5, 0.7, info_text,
                 ha='center', va='center', fontsize=16,
                 transform=ax_info.transAxes, linespacing=1.6)

    # Pie de página
    ax_fondo = fig.add_subplot(gs[3, :])
    ax_fondo.set_axis_off()

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    info_text = f"Análisis Segunda Vuelta Presidencial Chile 2025 - Jara vs Kast | Reporte Gran Santiago | Generado: {fecha}"
    ax_fondo.text(0.5, 0.5, info_text,
                  ha='center', va='center',
                  fontsize=12, color='gray',
                  transform=ax_fondo.transAxes)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    output_path = os.path.join(output_dir, "REPORTE_GRAN_SANTIAGO_COMPLETO.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)

    print(f" ✓ Reporte completo de Gran Santiago guardado: {output_path}")
    return output_path


# ============================================================================
# FUNCIONES DE REPORTE FINAL Y MAPA NACIONAL
# ============================================================================

def generar_reporte_final(mapa_data, output_dir):
    """
    Genera reporte final en texto con estadísticas generales.

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el reporte.
    """
    reporte_path = os.path.join(output_dir, "REPORTE_FINAL.txt")

    print(f"\n📋 Generando reporte final...")

    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("REPORTE FINAL - ANÁLISIS SEGUNDA VUELTA PRESIDENCIAL CHILE 2025 - JARA vs KAST\n")
        f.write("=" * 100 + "\n\n")

        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        f.write(f"Fecha de generación: {fecha_actual}\n")
        f.write(f"Total de comunas procesadas: {len(mapa_data)}\n\n")

        if 'REGION_NUM' not in mapa_data.columns:
            f.write("ADVERTENCIA: No se encontró información de región en los datos\n\n")
            return

        # Estadísticas generales
        total_comunas = len(mapa_data)
        comunas_con_datos = 0
        if 'diferencia_pct' in mapa_data.columns:
            comunas_con_datos = mapa_data['diferencia_pct'].notna().sum()

        f.write("1. ESTADÍSTICAS GENERALES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total comunas: {total_comunas}\n")

        if 'diferencia_pct' in mapa_data.columns:
            f.write(
                f"Comunas con datos electorales: {comunas_con_datos} ({comunas_con_datos / total_comunas * 100:.1f}%)\n")

            if comunas_con_datos > 0:
                dif_promedio = mapa_data['diferencia_pct'].mean()
                jara_gana = (mapa_data['diferencia_pct'] > 0).sum()
                kast_gana = (mapa_data['diferencia_pct'] < 0).sum()
                empates = (mapa_data['diferencia_pct'] == 0).sum()

                f.write(f"Diferencia promedio nacional: {dif_promedio:+.2f}%\n")
                f.write(f"Jara gana en: {jara_gana} comunas ({jara_gana / comunas_con_datos * 100:.1f}%)\n")
                f.write(f"Kast gana en: {kast_gana} comunas ({kast_gana / comunas_con_datos * 100:.1f}%)\n")
                f.write(f"Empates: {empates} comunas ({empates / comunas_con_datos * 100:.1f}%)\n\n")

        f.write("\n" + "=" * 100 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("=" * 100 + "\n")

    print(f"✓ Reporte final guardado: {reporte_path}")


def generar_mapa_nacional(mapa_data, output_dir):
    """
    Genera mapa nacional simple con leyenda de colores.

    Args:
        mapa_data (GeoDataFrame): Datos combinados de toda Chile.
        output_dir (str): Directorio para guardar el mapa.
    """
    if mapa_data.empty:
        print(" ⚠ No hay datos para generar mapa nacional")
        return

    print(f"\n🌍 Generando mapa nacional...")

    fig, ax = plt.subplots(1, 1, figsize=(20, 12))

    # Asignar colores
    if 'diferencia_pct' in mapa_data.columns:
        mapa_data['color'] = mapa_data['diferencia_pct'].apply(asignar_color_diferencia)
    else:
        mapa_data['color'] = '#D3D3D3'

    # Dibujar mapa
    try:
        mapa_data.plot(ax=ax, color=mapa_data['color'], edgecolor='black', linewidth=0.3)
    except:
        # Fallback: dibujar comunas individualmente
        for idx, row in mapa_data.iterrows():
            if hasattr(row, 'geometry') and row.geometry is not None:
                try:
                    gpd.GeoSeries([row.geometry]).plot(ax=ax, color=row['color'], edgecolor='black', linewidth=0.3)
                except:
                    continue

    ax.set_title('ANÁLISIS SEGUNDA VELTA PRESIDENCIAL CHILE 2025 - DIFERENCIA JARA vs KAST', fontsize=24,
                 fontweight='bold', pad=20)
    ax.set_axis_off()

    # Leyenda de colores
    leyenda_elementos = [
        mpatches.Patch(color='#B91C1C', label='Jara +50% o más'),
        mpatches.Patch(color='#C92A2A', label='Jara +40% a +50%'),
        mpatches.Patch(color='#DA4A4A', label='Jara +30% a +40%'),
        mpatches.Patch(color='#E86969', label='Jara +20% a +30%'),
        mpatches.Patch(color='#F28787', label='Jara +10% a +20%'),
        mpatches.Patch(color='#F8A0A0', label='Jara +1% a +10%'),
        mpatches.Patch(color='#9CA3AF', label='Empate técnico'),
        mpatches.Patch(color='#8BB2F0', label='Kast +1% a +10%'),
        mpatches.Patch(color='#5E91E8', label='Kast +10% a +20%'),
        mpatches.Patch(color='#3D76D1', label='Kast +20% a +30%'),
        mpatches.Patch(color='#2A58A6', label='Kast +30% a +40%'),
        mpatches.Patch(color='#1A3D7C', label='Kast +40% a +50%'),
        mpatches.Patch(color='#0F2D5C', label='Kast +50% o más'),
        mpatches.Patch(color='#D3D3D3', label='Sin datos'),
    ]

    ax.legend(handles=leyenda_elementos,
              loc='upper left',
              bbox_to_anchor=(0.01, 0.99),
              fontsize=9,
              title='Leyenda (Nueva Escala COLORES_BALOTAJE)',
              title_fontsize=11,
              framealpha=0.9,
              ncol=2)

    output_path = os.path.join(output_dir, "MAPA_NACIONAL_COMPLETO.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"✓ Mapa nacional generado: {output_path}")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main(csv_path, output_dir, regions=None):
    """
    Función principal del generador de mapas electorales.

    Args:
        csv_path (str): Ruta al archivo CSV con datos electorales.
        output_dir (str): Directorio de salida para los mapas.
        regions (list or None): Lista de regiones a procesar, o None para todas.
    """
    print("\n" + "=" * 80)
    print("ANÁLISIS SEGUNDA VUELTA PRESIDENCIAL CHILE 2025 - JARA vs KAST")
    print("Incluye mapas de áreas metropolitanas: Gran Santiago, Gran Valparaíso, Gran Concepción")
    print("Con nombres de comunas en mapas regionales y tamaños ajustados por región")
    print("MODIFICACIONES REALIZADAS:")
    print("1. Eliminadas las funciones que generaban mapas simples de islas (ya no son necesarios)")
    print("2. En el mapa de Chile en tres partes, eliminadas las etiquetas de comunas (solo para este gráfico)")
    print("3. Todas las demás etiquetas de comunas se mantienen intactas")
    print("4. CORREGIDO: Error en función crear_reporte_nacional_completo")
    print("5. MODIFICADO: Nueva escala de colores")
    print("6. AGREGADO: Tabla de resultados en capitales regionales")
    print("=" * 80)

    print(f"\n📍 Ruta del CSV: {csv_path}")
    print(f"📁 Directorio de salida: {output_dir}")

    if not os.path.exists(csv_path):
        print(f"❌ Archivo no encontrado")
        return

    os.makedirs(output_dir, exist_ok=True)

    try:
        # Cargar y procesar datos
        comunas = cargar_datos_geograficos()
        df_electoral = procesar_csv(csv_path)
        mapa_data = unir_datos(comunas, df_electoral)

        # Guardar datos combinados
        datos_path = os.path.join(output_dir, 'datos_combinados.csv')
        columnas_a_guardar = []
        for col in ['COD_COM', 'NOM_COM', 'REGION_NUM', 'geometry',
                    'comuna', 'region', 'jara_votos', 'kast_votos', 'jara_pct', 'kast_pct',
                    'blanco_votos', 'nulo_votos', 'emitidos_votos', 'diferencia_pct']:
            if col in mapa_data.columns:
                columnas_a_guardar.append(col)

        if columnas_a_guardar:
            if 'geometry' in mapa_data.columns:
                mapa_data[columnas_a_guardar].to_file(datos_path.replace('.csv', '.geojson'), driver='GeoJSON')
                print(f"\n💾 Datos combinados guardados (GeoJSON): {datos_path.replace('.csv', '.geojson')}")

            columnas_sin_geo = [c for c in columnas_a_guardar if c != 'geometry']
            if columnas_sin_geo:
                mapa_data[columnas_sin_geo].to_csv(datos_path, index=False, encoding='utf-8-sig')
                print(f"💾 Datos combinados guardados (CSV): {datos_path}")

        print("\n" + "=" * 60)
        print("🎨 GENERANDO MAPAS REGIONALES")
        print("=" * 60)

        # Generar mapas regionales
        if regions is None:
            regions = range(1, 17)

        mapas_generados = []
        for region_num in regions:
            try:
                mapa_path = crear_mapa_regional_completo(region_num, mapa_data, output_dir)
                if mapa_path:
                    mapas_generados.append(mapa_path)
            except Exception as e:
                print(f" ✗ Error generando mapa Región {region_num}: {e}")

        print("\n" + "=" * 60)
        print("🏝️ GENERANDO MAPAS DE ISLAS SEPARADAS")
        print("=" * 60)

        # Mapas de islas
        crear_mapa_isla_pascua(mapa_data, output_dir)
        crear_mapa_juan_fernandez(mapa_data, output_dir)

        print("\n" + "=" * 60)
        print("🗺️ GENERANDO NUEVO MAPA DE CHILE EN TRES PARTES")
        print("=" * 60)

        # Mapa de Chile en tres partes
        crear_mapa_chile_tres_partes(mapa_data, output_dir)

        print("\n" + "=" * 60)
        print("🏙️ GENERANDO MAPAS DE ÁREAS METROPOLITANAS")
        print("=" * 60)

        # Mapas de áreas metropolitanas
        if 5 in regions or regions is None:
            crear_mapa_gran_valparaiso(mapa_data, output_dir)

        if 8 in regions or regions is None:
            crear_mapa_gran_concepcion(mapa_data, output_dir)

        if 13 in regions or regions is None:
            crear_mapa_conurbacion_santiago(mapa_data, output_dir)
            crear_reporte_gran_santiago_completo(mapa_data, output_dir)

        print("\n" + "=" * 60)
        print("📊 GENERANDO REPORTE NACIONAL COMPLETO")
        print("=" * 60)

        crear_reporte_nacional_completo(mapa_data, output_dir)

        print("\n" + "=" * 60)
        print("📋 GENERANDO TABLA DE CAPITALES REGIONALES")
        print("=" * 60)

        crear_tabla_capitales_regionales(mapa_data, output_dir)

        # Reporte final
        generar_reporte_final(mapa_data, output_dir)

        print(f"\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO!")
        print("=" * 80)
        print(f"\n📁 Resultados en: {output_dir}")
        print(f"🗺️ Mapas regionales generados: {len(mapas_generados)} regiones")
        print(f"🏝️ Mapas de islas generados: 2 (Isla de Pascua y Juan Fernández - SOLO ISLAS PRINCIPALES)")
        print(f"🗺️ Nuevo mapa de Chile: 1 (Chile en tres partes: Norte, Centro, Sur) - SIN ETIQUETAS DE COMUNAS")
        print(f"🏙️ Mapas de áreas metropolitanas generados: 3 (Gran Santiago, Gran Valparaíso, Gran Concepción)")
        print(f"📊 Reportes especiales: 2 (Reporte Gran Santiago Completo y Reporte Nacional Completo)")
        print(f"📋 Tabla de capitales regionales: 1 (16 capitales regionales con resultados)")
        print(f"📈 Comunas procesadas: {len(mapa_data)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Generador de mapas electorales")
    parser.add_argument('--csv', type=str,
                        default="/home/alfonso/PyCharmMiscProject/[OK ]Elecciones presidencial 2025/Segunda vuelta/mapas/matriz_elecciones_346_comunas.csv",
                        help="Ruta al archivo CSV")
    parser.add_argument('--output', type=str, default="mapas_regionales_completos",
                        help="Directorio de salida")
    parser.add_argument('--regions', type=str, default=None,
                        help="Regiones a procesar (ej: 1,13 o all)")

    args = parser.parse_args()

    # Procesar argumentos de regiones
    if args.regions and args.regions.lower() != 'all':
        regions = [int(r) for r in args.regions.split(',')]
    else:
        regions = None

    # Ejecutar función principal
    main(args.csv, args.output, regions)
