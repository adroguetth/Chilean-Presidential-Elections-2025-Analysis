# 🗳️ Electoral Analysis — Chile 2025 · Presidential First Round

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-f37626?style=flat-square&logo=jupyter&logoColor=white) 

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=flat-square&logo=geopandas&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-4c72b0?style=flat-square&logo=python&logoColor=white)

**Análisis de datos:** procesamiento cuantitativo, análisis espacial y visualización

**Análisis político:** comentario experto independiente, contextualización e interpretación

------

## 📥 Acceso Rápido

| Idioma         | Notebook                           | Formato                                                      |
| :------------- | :--------------------------------- | :----------------------------------------------------------- |
| **🇬🇧 Inglés**  | `electoral_analysis_2025_EN.ipynb` | [Ver en GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_notebooks/electoral_analysis_2025_EN.ipynb) |
| **🇪🇸 Español** | `electoral_analysis_2025_ES.ipynb` | [Ver en GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_notebooks/electoral_analysis_2025_ES.ipynb) |

------

## 📋 Descripción General

Este notebook presenta un análisis territorial, demográfico y político completo de la primera vuelta de las elecciones presidenciales chilenas realizadas en noviembre de 2025. Cubre resultados nacionales, mapeo de ganadores a nivel comunal, desgloses regionales, gradientes de voto urbano-rural, bastiones electorales, proyecciones de segunda vuelta y un estudio comparativo del realineamiento entre las primeras vueltas de 2021 y 2025.

El análisis fue elaborado bajo **voto obligatorio** — reinstaurado en Chile en 2022 y vigente desde las elecciones municipales de octubre de 2024 — lo que generó un **aumento del 89,1%** en el total de votos emitidos (7,08 millones en 2021 → 13,39 millones en 2025) y constituye el principal lente metodológico para todas las comparaciones entre ciclos.

------

### 📊 Secciones del Análisis

| Sección                                  | Contenido                                                    | Visualizaciones          |
| :--------------------------------------- | :----------------------------------------------------------- | :----------------------- |
| **1. Configuración**                     | Dependencias, imports, configuración                         | Ninguna                  |
| **2. Carga de Datos**                    | CSVs, población, dimensión regional, GeoJSON **2.4 normalize_commune_name()** Clave canónica de comuna para uniones entre datasets | Ninguna                  |
| **3. Participación General**             | Análisis de votos válidos/nulos/blancos; comparación con 2021 | Tabla                    |
| **4. Resultados Nacionales**             | Resultados por candidato; lectura estratégica por bloques    | Tabla, gráfico de barras |
| **5. Bastiones Electorales**             | Top-10 comunas por candidato; perfiles geográficos           | Tabla                    |
| **6. Mapeo Territorial**                 | Comunas ganadas por candidato; paradoja territorio-demografía | Tabla, gráfico de barras |
| **7. Resultados por Región**             | Trifurcación de las tres Chiles; regiones bisagra            | Tabla, mapas             |
| **8. Capitales Regionales**              | Divergencia de voto entre capital y hinterland               | Tabla                    |
| **9. Comportamiento de Centros Urbanos** | Gradiente urbano-rural de cinco niveles (>200k → <10k habitantes) | Tabla, gráfico de barras |
| **10. Ganadores por Comuna**             | Coropleta nacional + facetas de áreas metropolitanas         | Mapas                    |
| **11. Comunas Recuperables**             | Márgenes < 1.000 votos; costo de movilización por macrozona  | Tabla, gráfico de barras |
| **12. Proyecciones de Segunda Vuelta**   | Cuatro escenarios de transferencia de voto (Jara vs. Kast)   | Tabla                    |
| **13. Voto Antisistema**                 | Parisi vs. el duopolio; análisis de dominancia a nivel comunal | Tabla                    |
| **14. Comparativo 2021–2025**            | Matriz de realineamiento; crecimiento de Parisi; transiciones territoriales **Mapas de Transición** Mapas de cambio de ganador nacional + áreas metropolitanas | Tabla, Mapas             |
| **Resumen Ejecutivo**                    | Síntesis de hallazgos y conclusión                           | Ninguna                  |

------

## 📝 Hallazgos Clave

| Hallazgo                                      | Detalle                                                      |
| :-------------------------------------------- | :----------------------------------------------------------- |
| **Ningún candidato superó el 27%**            | El bloque de derecha combinado (Kast + Kaiser + Matthei) superó el **50%** por primera vez en condiciones competitivas. |
| **Jara lideró por concentración demográfica** | Controló el **76,9% de la población** en comunas de más de 200.000 habitantes, ganando solo 105 de 346 comunas. |
| **Kast dominó territorialmente**              | 169 comunas, con dominio creciendo monótonamente a medida que disminuye el tamaño comunal. Punto de inflexión: ~50.000 habitantes. |
| **Monopolio norteño de Parisi**               | Resultado territorialmente más intenso del mapa: **retención territorial del 95,7%** desde 2021, crecimiento en 15 de 16 regiones. |
| **El 45% de las comunas cambió de ganador**   | Entre 2021 y 2025. El centro-izquierda (Provoste) retuvo el **0%** de sus comunas de 2021; el 70% migró a Parisi. |
| **Proyección de segunda vuelta**              | En los cuatro escenarios de transferencia, **Kast proyecta una victoria**, desde +113k votos (escenario óptimo Jara) hasta +2,4M (escenario óptimo Kast). |

------

## 📁 Estructura del Repositorio

```text
Chilean-Presidential-Elections-2025-Analysis/
├── first_round
│   └── 2_notebooks/
│       ├── README.md
│       ├── requirements.txt
│       ├── electoral_analysis_2025_EN.ipynb      # Versión en inglés
│       └── electoral_analysis_2025_ES.ipynb      # Versión en español
└── raw/                                       (datos cargados automáticamente)
    ├── chile_2025_first_round.csv
    ├── chile_2021_first_round.csv
    ├── communes_population_2024.csv
    └── region_dimension.csv
```



------

## 📦 Fuentes de Datos

| Archivo                        | Descripción                                                  | Unidad |
| :----------------------------- | :----------------------------------------------------------- | :----- |
| `chile_2025_first_round.csv`   | Participación de voto por candidato a nivel comunal, primera vuelta 2025 | Comuna |
| `chile_2021_first_round.csv`   | Participación de voto por candidato a nivel comunal, primera vuelta 2021 | Comuna |
| `communes_population_2024.csv` | Estimaciones de población por comuna (proyección censal 2024) | Comuna |
| `region_dimension.csv`         | Metadatos de región: macrozona, orden de visualización, códigos de región | Región |
| GeoJSON de comunas de Chile    | Geometrías poligonales para todas las 346 comunas            | Comuna |

Los datos geográficos se cargan desde el repositorio público [`caracena/chile-geojson`](https://github.com/caracena/chile-geojson), con descarga automática por región si no se dispone de un archivo único.

**Fuente primaria:** Servicio Electoral de Chile (SERVEL), resultados oficiales de primera vuelta 2021 y 2025.

Todos los archivos de datos se cargan directamente desde el directorio `raw/` del repositorio a través de HTTPS. No se requiere descarga local de datos para ejecutar el notebook.

------

## 🚀 Configuración Local

### Prerrequisitos

- Python 3.7 o superior (3.12 recomendado)

### **Instalación Paso a Paso**

1. **Clonar el Repositorio**
```bash
git clone https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis.git
cd Chilean-Presidential-Elections-2025-Analysis/first_round/2_notebooks
```



2. **Crear Entorno Virtual (recomendado)**
```bash
python -m venv venv

# Activar entorno
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```



3. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```



O mediante conda (recomendado para geopandas en Windows):

```bash
conda install -c conda-forge geopandas pandas numpy matplotlib jupyterlab
```




4. **Ejecutar el Notebook**

```bash
# Versión en inglés
jupyter lab electoral_analysis_2025_EN.ipynb

# Versión en español
jupyter lab electoral_analysis_2025_ES.ipynb
```



El notebook obtiene todos los datos de forma remota en la primera ejecución. Se requiere conexión a internet. Las ejecuciones posteriores funcionan sin conexión si se mantiene la sesión del kernel.

------

## 🧠 Notas Técnicas

### Normalización de Nombres de Comunas (`normalize_commune_name`)

Las uniones entre datasets (CSVs de SERVEL y GeoJSON) dependen de una clave canónica de comuna generada por `normalize_commune_name()` (§ 2.4). El proceso:

1. Minúsculas + eliminar espacios al inicio/final
2. Descomposición NFD → eliminar marcas diacríticas (remueve tildes y diéresis, incluyendo `ü` → `u`)
3. Eliminar caracteres no alfanuméricos (guiones, paréntesis, puntuación)
4. Colapsar espacios múltiples
5. Aplicar tabla de correcciones curadas sobre la forma ASCII limpia

Las correcciones manejan divergencias de codificación conocidas entre datasets:

| Forma original                | Canónica         |
| :---------------------------- | :--------------- |
| `Marchigüe` / `Marchigue`     | `marchihue`      |
| `Llay-Llay`                   | `llaillay`       |
| `Trehuaco`                    | `treguaco`       |
| `Cabo de Hornos(ex-Navarino)` | `cabo de hornos` |

### Realineamiento Electoral (`df_change`)

El dataset de transición 2021→2025 se construye uniendo ambos CSVs electorales por `(commune_norm, region)` después de la normalización (§ 14.4). Una unión simple sobre nombres crudos de comuna pierde filas donde la codificación difiere entre los dos archivos fuente; la clave normalizada evita esa pérdida de datos.

### Renderizado de Mapas

Los mapas coropléticos utilizan un diseño 3×3 `GridSpec` organizado por macrozona:

| Grid  | Macrozona                  |
| :---- | :------------------------- |
| (0,0) | Norte Grande               |
| (0,1) | Norte Chico                |
| (0,2) | Centro (Valparaíso y RM)   |
| (1,0) | Centro (O'Higgins y Maule) |
| (1,1) | Centro Sur                 |
| (1,2) | Sur                        |
| (2,1) | Patagonia                  |

Isla de Pascua y Juan Fernández están excluidas de todos los mapas (su geometría atípica distorsiona los bounding boxes regionales). Las facetas de áreas metropolitanas utilizan claves de comuna normalizadas para el filtrado GeoJSON, evitando problemas de codificación con las cadenas `NOM_COM` originales.

------

## 👥 Candidatos

| Candidato              | Bloc                      | Color     |
| :--------------------- | :------------------------ | :-------- |
| Jeannette Jara         | Izquierda                 | `#E54944` |
| José Antonio Kast      | Derecha                   | `#35466D` |
| Franco Parisi          | Antisistema               | `#4B70B5` |
| Johannes Kaiser        | Libertario                | `#F3832C` |
| Evelyn Matthei         | Derecha Tradicional       | `#226FD4` |
| Harold Mayne-Nicholls  | Independiente             | `#BED8DF` |
| Marco Enríquez-Ominami | Izquierda (independiente) | `#DD2883` |
| Eduardo Artés          | Extrema Izquierda         | `#CA1C1F` |

------

## 📄 Licencia y Atribución

- **Licencia**: MIT
- **Autor**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Portafolio web:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Correo electrónico:** adroguett.consultor@gmail.com
- **Fuentes de Datos**:
  - SERVEL (dominio público, autoridad electoral oficial)
- **Tecnologías**:
  - Jupyter Notebooks
  - Matplotlib
  - Pandas, NumPy (procesamiento de datos)

------

## ⭐ Agradecimientos

¡Si este proyecto te es útil, considera darle una estrella en GitHub!
