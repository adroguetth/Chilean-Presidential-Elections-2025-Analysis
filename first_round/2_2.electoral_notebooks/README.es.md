# 🗳️ Análisis Electoral — Chile 2025 · Primera Vuelta Presidencial
**Looking for the English version?** → [README.md](README.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-f37626?style=flat-square&logo=jupyter&logoColor=white) 

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=flat-square&logo=geopandas&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-4c72b0?style=flat-square&logo=python&logoColor=white)

**Analítica de datos:** procesamiento cuantitativo, análisis espacial y visualización <br/>
**Análisis político:** comentario experto independiente, contextualización e interpretación

------

## 📥 Acceso Rápido

| Idioma          | Notebook                                        | Enlace                                                       |
| :-------------- | :----------------------------------------------- | :------------------------------------------------------------ |
| **🇬🇧 English** | `electoral_analysis_2025_first_round_EN.ipynb` | https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_2.electoral_notebooks/electoral_analysis_2025_first_round_EN.ipynb |
| **🇪🇸 Español** | `electoral_analysis_2025_first_round_ES.ipynb` | https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_2.electoral_notebooks/electoral_analysis_2025_first_round_ES.ipynb |

------

## 📋 Descripción General

La primera vuelta presidencial de noviembre de 2025 produjo uno de los resultados más fragmentados de la historia democrática del país — ningún candidato superó el 27% de los votos válidos — y dejó configurado un balotaje entre Jeannette Jara (26,75%) y José Antonio Kast (23,96%), mientras el ascenso antisistema de Franco Parisi (19,71%) redibujaba el mapa electoral en el camino.

Este repositorio contiene un análisis territorial, demográfico y político exhaustivo de esa primera vuelta, construido íntegramente sobre datos oficiales de Servel a nivel comunal. Más allá de los resultados nacionales, el análisis mapea **quién ganó dónde, y por qué**: mapeo de ganadores por comuna, desgloses regionales, el gradiente de voto urbano-rural, los bastiones electorales de cada candidato, las comunas decididas por márgenes mínimos, proyecciones de escenarios de segunda vuelta, y un estudio comparativo del realineamiento entre las primeras vueltas de 2021 y 2025.

El análisis se produjo bajo **voto obligatorio** —reinstaurado en Chile en 2022 y vigente desde las elecciones municipales de octubre de 2024—, lo que generó un **incremento del 89,1%** en el total de votos emitidos (7,08 millones en 2021 → 13,39 millones en 2025) y constituye la lente metodológica central para todas las comparaciones entre ambos ciclos.

El notebook combina dos capas a lo largo de todo el análisis: **analítica de datos** (procesamiento cuantitativo, análisis espacial y visualización) y **análisis político** (comentario experto independiente y contextualización), y está disponible íntegramente tanto en inglés como en español.

---

### 📊 Estructura del Análisis

| # | Sección | Qué cubre |
| :- | :------- | :--------- |
| 1–2 | Setup y Carga de Datos | Entorno, ingesta de datos, normalización de nombres de comuna |
| 3 | Estadísticas Generales de Participación | Participación, tasas de voto válido/nulo/blanco bajo voto obligatorio |
| 4 | El Voto Nulo | Geografía regional y comunal de la protesta activa |
| 5 | El Voto en Blanco | Geografía regional y comunal de la protesta pasiva |
| 6 | Resultados Nacionales por Candidato | Grupos de competitividad y bloques ideológicos |
| 7 | Bastiones Electorales | Top 15 comunas y perfil socioeconómico, por candidato |
| 8 | Mapeo Territorial y Distribución del Voto | Comunas ganadas, macrozonas, resultados regionales, brechas regionales |
| 9 | Capitales Regionales | El voto urbano-administrativo frente al resto de la región |
| 10 | Comportamiento Electoral en Centros Urbanos | El gradiente urbano-rural en cinco segmentos poblacionales |
| 11 | Comunas Recuperables | Comunas perdidas por menos de 1.000 votos; costo de movilización por macrozona |
| 12 | Proyección Segunda Vuelta | Cuatro escenarios de transferencia de voto, Jara vs. Kast |
| 13 | Franco Parisi: El Fenómeno del Voto Antisistema | Dónde —y por qué— se concentró el voto antisistema |
| 14 | Análisis Comparativo: Evolución 2021-2025 | Tendencias de participación, evolución de bloques, ascenso de Parisi, mapa de realineamiento |
| — | Recomendaciones Estratégicas y Resumen | Lectura estratégica por candidato y resumen ejecutivo |

Cada capítulo sigue la misma estructura: una introducción que plantea la pregunta, un análisis basado en datos, y una síntesis de cierre (`Conclusión X.X`) que responde al planteamiento inicial del capítulo.

------

## 📝 Hallazgos Clave

**Un país sin mayorías.** Ningún candidato superó el 27% de los votos válidos. La derecha sumada (Kast + Kaiser + Matthei) superó el 50% por primera vez en la era del voto voluntario/obligatorio — un umbral que ya se insinuaba en 2021 (Kast + Sichel ≈ 40,8%) pero que solo se consolidó en 2025.

| Candidato | Votos | % | 2021→2025 |
| :--------- | -----: | ---: | :--------- |
| Jeannette Jara | 3.446.854 | 26,75% | +32% |
| José Antonio Kast | 3.086.963 | 23,96% | +58% |
| Franco Parisi | 2.550.770 | 19,71% | **+184%** |
| Johannes Kaiser | 1.796.034 | 13,94% | *(nuevo)* |
| Evelyn Matthei | 1.603.104 | 12,44% | +79% |
| Marco Enríquez-Ominami | 154.321 | 1,2% | **−71%** |

**Una paradoja territorial.** Kast ganó más comunas (169, 48,8%) pero quedó segundo en votos; Jara ganó menos comunas (105, 30,3%) pero lideró el conteo nacional — la señal más clara de que Chile se dividió en **tres países electorales**: un Norte antisistema (Parisi), un Centro urbano-progresista (Jara) y un Centro-Sur rural-conservador (Kast).

**El gradiente urbano-rural.** La preferencia de voto correlaciona casi mecánicamente con el tamaño de la comuna, con un punto de inflexión en torno a los **50.000 habitantes**: por encima, domina Jara (76,9% de la población en ciudades de más de 200 mil habitantes); por debajo, domina Kast (~60% en comunas de menos de 10 mil).

**Las capitales votan distinto a sus propias regiones.** Jara ganó 10 de 16 capitales regionales pero solo 5 de 16 regiones; Kast ganó 4 capitales pero 7 regiones. Iquique, dividida casi en tercios iguales, fue la ciudad más competitiva del país.

**El fenómeno Parisi.** Los votos de Franco Parisi crecieron un 184% (899.067 → 2.550.770) y sus comunas ganadas pasaron de 6 a 64, con una tasa de retención del 95,7% — la base electoral más leal del país. En 11 comunas superó a Jara *y* a Kast **combinados**; ahí, el antisistema no fue la tercera fuerza: fue la primera, por un promedio de 8,9 puntos.

**El realineamiento fue marcadamente desigual.** El 45% de las comunas comparables cambió de ganador entre 2021 y 2025 — pero esa volatilidad se concentró en regiones densas y urbanas (Valparaíso 87,1%, Metropolitana 81,6%), mientras Antofagasta y La Araucanía no registraron ningún cambio. Dos tercios o más de la expansión territorial de Parisi provinieron de antiguos votantes de Kast, no de la izquierda.

**Las proyecciones de segunda vuelta muestran una inclinación estructural, no un veredicto.** Cuatro escenarios de transferencia (ver Cap. 12) sitúan a Kast por delante en todos los casos, pero el margen oscila entre 2,4 millones de votos (mejor caso para Kast) y apenas 112.774 (mejor caso para Jara), dependiendo enteramente de cómo se reparta finalmente el electorado de Franco Parisi — el verdadero "gran elector" del balotaje. Se trata de escenarios modelados sobre supuestos de transferencia, no de resultados observados.

*Un desglose completo, sección por sección, con todas las tablas de respaldo, está disponible en [`Key_Findings.md`](Key_Findings.md).*

------

## 📁 Estructura del Repositorio

```text
Chilean-Presidential-Elections-2025-Analysis/
├── first_round
│ 	└── 2_2.electoral_notebooks/
│		├── README.md
│		├── requirements.txt
│		├── electoral_analysis_2025_first_round_EN.ipynb      # Versión en inglés
│		└── electoral_analysis_2025_first_round_ES.ipynb      # Versión en español
└── raw/                                       (datos cargados automáticamente)
    ├── chile_2025_first_round.csv
    ├── chile_2021_first_round.csv
    ├── communes_population_2024.csv
    └── region_dimension.csv
```



------

## 📦 Fuentes de Datos

| Archivo                        | Descripción                                                | Unidad  |
| :------------------------------ | :------------------------------------------------------------ | :------- |
| `chile_2025_first_round.csv`   | Votación por candidato y comuna, primera vuelta 2025       | Comuna |
| `chile_2021_first_round.csv`   | Votación por candidato y comuna, primera vuelta 2021       | Comuna |
| `communes_population_2024.csv` | Estimaciones de población por comuna (proyección censo 2024) | Comuna |
| `region_dimension.csv`         | Metadatos regionales: macrozona, orden de despliegue, códigos de región | Región  |
| GeoJSON de comunas de Chile     | Geometrías poligonales de las 346 comunas                  | Comuna |

Los datos geográficos se cargan desde el repositorio público [`caracena/chile-geojson`](https://github.com/caracena/chile-geojson), con respaldo automático por región si no está disponible una fuente de archivo único.

**Fuente primaria:** Servicio Electoral de Chile (Servel), resultados oficiales de primera vuelta 2021 y 2025.

Todos los archivos de datos se cargan directamente desde el directorio `raw/` del repositorio vía HTTPS. No se requiere descarga local de datos para ejecutar el notebook.



------

## 🚀 Instalación Local

### Requisitos Previos

- Python 3.7 o superior (se recomienda 3.12)



### **Instalación Paso a Paso**

1. **Clonar el Repositorio**
   
```bash
git clone https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis.git
cd Chilean-Presidential-Elections-2025-Analysis/first_round/2_2.electoral_notebooks
```
2. **Crear un Entorno Virtual (recomendado)**

```bash
python -m venv venv

# Activar el entorno
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. **Instalar Dependencias**

```bash
pip install -r requirements.txt
```

O vía conda (recomendado para geopandas en Windows):

```bash
conda install -c conda-forge geopandas pandas numpy matplotlib jupyterlab
```



4. **Ejecutar el Notebook**

```bash
# Versión en inglés
jupyter lab electoral_analysis_2025_first_round_EN.ipynb

# Versión en español
jupyter lab electoral_analysis_2025_first_round_ES.ipynb
```

El notebook obtiene todos los datos de forma remota en la primera ejecución. Se requiere conexión a internet. Las ejecuciones posteriores funcionan sin conexión si se mantiene la sesión del kernel.



------

## 🧠 Notas Técnicas

### Normalización de Nombres de Comuna (`normalize_commune_name`)

Las uniones entre los CSV de Servel y el GeoJSON dependen de una clave comunal canónica generada por `normalize_commune_name()` (§ 2.4). El proceso:

1. Minúsculas + eliminación de espacios
2. Descomposición NFD → eliminación de marcas diacríticas (elimina todas las tildes y diéresis, incluyendo `ü` → `u`)
3. Eliminación de caracteres no alfanuméricos (guiones, paréntesis, puntuación)
4. Colapso de espacios en blanco
5. Aplicación de una tabla de correcciones curada sobre la forma ASCII limpia

Las correcciones abordan divergencias de codificación conocidas entre los conjuntos de datos:

| Forma original                | Forma canónica   |
| :------------------------------ | :----------------- |
| `Marchigüe` / `Marchigue`     | `marchihue`      |
| `Llay-Llay`                   | `llaillay`       |
| `Trehuaco`                    | `treguaco`       |
| `Cabo de Hornos(ex-Navarino)` | `cabo de hornos` |

### Realineamiento Electoral (`df_change`)

El conjunto de datos de transición 2021→2025 se construye uniendo ambos CSV electorales por `(comuna_norm, región)` tras la normalización (§ 14.4). Una unión de cadenas simple sobre los nombres de comuna sin normalizar descarta silenciosamente filas allí donde la codificación diverge entre ambos archivos fuente; la clave normalizada evita esa pérdida de datos.

### Renderizado de Mapas

Los mapas coropléticos usan una cuadrícula `GridSpec` de 3×3 organizada por macrozona:

| Cuadrícula | Macrozona                  |
| :---------- | :---------------------------- |
| (0,0)       | Norte Grande                |
| (0,1)       | Norte Chico                 |
| (0,2)       | Centro (Valparaíso y RM)    |
| (1,0)       | Centro (O'Higgins y Maule)  |
| (1,1)       | Centro Sur                  |
| (1,2)       | Sur                          |
| (2,1)       | Patagonia                   |

Isla de Pascua y Juan Fernández se excluyen de todos los mapas (su geometría atípica distorsiona los cuadros delimitadores regionales). Las vistas de áreas metropolitanas usan claves comunales normalizadas para el filtrado del GeoJSON, evitando discordancias de codificación con las cadenas `NOM_COM` sin normalizar.

------

## 👥 Candidatos

| Candidato              | Bloque              | Color     |
| :----------------------- | :-------------------- | :--------- |
| Jeannette Jara         | Izquierda           | `#E54944` |
| José Antonio Kast      | Derecha             | `#35466D` |
| Franco Parisi          | Antisistema         | `#4B70B5` |
| Johannes Kaiser        | Libertario          | `#F3832C` |
| Evelyn Matthei         | Derecha Tradicional | `#226FD4` |
| Harold Mayne-Nicholls  | Independiente       | `#BED8DF` |
| Marco Enríquez-Ominami | Izquierda (independiente) | `#DD2883` |
| Eduardo Artés          | Extrema Izquierda   | `#CA1C1F` |



------

## 📄 Licencia y Atribución

- **Licencia**: MIT
- **Autor**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Portafolio web:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Correo:** adroguett.consultor@gmail.com
- **Fuentes de Datos**:
  - Servel (dominio público, autoridad electoral oficial)
- **Tecnologías**:
  - Jupyter Notebooks
  - Matplotlib
  - Pandas, NumPy (procesamiento de datos)
