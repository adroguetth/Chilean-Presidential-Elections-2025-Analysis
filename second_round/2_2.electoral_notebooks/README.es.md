# 🗳️ Análisis Electoral — Chile 2025 · Segunda Vuelta Presidencial

**Looking for the English version?** → [README.md](README.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-f37626?style=flat-square&logo=jupyter&logoColor=white) 

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=flat-square&logo=geopandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-4c72b0?style=flat-square&logo=python&logoColor=white) ![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=flat-square&logo=python&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white) ![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=flat-square&logo=scipy&logoColor=white)

**Análisis de datos:** procesamiento cuantitativo, análisis espacial, correlaciones estadísticas y clustering de machine learning<br/>
**Análisis político:** comentario experto independiente, contextualización e interpretación

---

## 📥 Acceso Rápido

| Idioma         | Notebook                                        | Formato                                                      |
| :------------- | :---------------------------------------------- | :----------------------------------------------------------- |
| **🇬🇧 English** | `electoral_analysis_2025_second_round_EN.ipynb` | [Ver en GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/second_round/2_notebooks/electoral_analysis_2025_second_round_EN.ipynb) |
| **🇪🇸 Español** | `electoral_analysis_2025_second_round_ES.ipynb` | [Ver en GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/second_round/2_notebooks/electoral_analysis_2025_second_round_ES.ipynb) |

---

## 📋 Descripción General

Este notebook presenta un análisis territorial, demográfico, estadístico y político de la **segunda vuelta presidencial chilena del 14 de diciembre de 2025**, en la que José Antonio Kast (Partido Republicano) derrotó a Jeannette Jara (coalición de gobierno) por un margen de 16,48 puntos porcentuales, el más amplio en la historia de los balotajes chilenos desde el retorno a la democracia.

El análisis cubre la anatomía completa del resultado: totales nacionales de votos, mapeo territorial comunal y regional, el explosivo aumento del voto nulo y blanco, el gradiente urbano-rural del voto a Kast, el destino del electorado de Franco Parisi (mediante correlaciones estadísticas y clustering k-means), mapas de transición comunal entre primera y segunda vuelta y entre los balotajes de 2021 y 2025, y conclusiones estratégicas para cada uno de los actores políticos principales.

La elección se realizó bajo **voto obligatorio** — reinstaurado en 2022 y en vigencia desde octubre de 2024 —, lo que incrementó la participación total en **+60,4%** respecto al balotaje de 2021 (8,3M → 13,4M votos emitidos) y constituye el principal lente institucional que condiciona todas las comparaciones entre ciclos.

**Nota metodológica.** Salvo indicación contraria, todos los datos se calculan a partir de la base comunal de 346 comunas continentales e insulares (datos públicos de SERVEL), que arroja **Kast 58,24% / Jara 41,76%**. El resultado oficial nacional de Servel —que incorpora los votos emitidos en el exterior— fue **Kast 58,16% / Jara 41,84%**. La divergencia se documenta y discute en la Sección 6.

---

## 📊 Secciones del Análisis

| Sección               | Titulo                                           | Contenido                                                    | Visualizaciones                            |
| --------------------- | :----------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------- |
| **1.**                | **Configuración**                                | Dependencias, imports, configuración                         | —                                          |
| **2.**                | **Carga de Datos**                               | CSVs, población, dimensión regional, GeoJSON · `normalize_commune_name()` para joins entre datasets | —                                          |
| **3.**                | **Participación vs Primera Vuelta**              | Comparación de votos válidos, nulos y blancos; anomalía de un balotaje con caída de votos válidos | Tabla                                      |
| **4.1.** & **4.2**    | **Voto Nulo — Nacional (Región, Macrozona)**     | Explosión del voto nulo por región y macrozona (+116,9%, máximo histórico) | Tablas                                     |
| **4.3.**              | **Voto Nulo — Nivel Comunal**                    | Top-20 comunas por aumento absoluto y relativo; distribución por ganador de primera vuelta | Tablas, Gráficos de barras, box plots      |
| **5.1.** & **5.2.**   | **Voto Blanco — Nacional (Región, Macrozona)**   | Variación del voto blanco por región y macrozona; contraste con el patrón del nulo | Tablas                                     |
| **5.3.**              | **Voto Blanco — Nivel Comunal**                  | Top-20 comunas por aumento absoluto y relativo; bastiones de Matthei como epicentro | Tabla, Gráficos de barras, box plots       |
| **6.**                | **Declaración del Ganador**                      | Resultado nacional, margen, nota metodológica sobre voto exterior | Tabla, Gráfico de barra.                   |
| **7.1.**              | **Mapeo Territorial — Comunas**                  | 310 vs 36 comunas ganadas; cobertura porcentual y poblacional | Tabla                                      |
| **7.2.**              | **Mapeo Territorial — Regiones**                 | Las 16 regiones para Kast; ordenamiento norte a sur          | Tabla                                      |
| **7.3.**              | **Mapa de Márgenes por Macrozona**               | Coropleta (Jara%−Kast%) a nivel comunal; grilla 3×3 por macrozona | Mapas                                      |
| **7.4.**              | **Áreas Metropolitanas (Margen)**                | Mapas de margen para Gran Santiago, Valparaíso y Concepción, entre otras | Mapas                                      |
| **8.1.**              | **Bastiones de Jara**                            | 36 comunas con mayoría absoluta; perfil geográfico y socioeconómico | Tabla                                      |
| **8.2.1**             | **Jara: Comunas Competitivas (<2 pp)**           | 6 comunas decididas por menos de 2 pp; mapa de recuperación para la coalición de Jara | Tabla                                      |
| **8.2.2** & **8.2.3** | **Jara: Comunas Perdidas por <5 pp**             | 20 comunas adicionales competitivas; capitales regionales del norte | Tabla, Heatmap, Gráfico de barras apiladas |
| **8.3.**              | **Comunas Volteadas por Jara (Norte)**           | 6 comunas de Parisi capturadas por Jara; voto de clase en la minería | Tabla, Gráfico de barras                   |
| **8.4.**              | **Retención del Voto de Jara**                   | Retención completa de comunas de primera vuelta; solidez vs. problema de techo | Análisis                                   |
| **8.5.**              | **Crecimiento del Voto de Jara**                 | Comunas donde Jara creció en votos absolutos; Gran Santiago como motor | Tabla                                      |
| **8.6.**              | **Jara: Penetración en Comunas de Élite**        | Crecimiento porcentual de Jara en Las Condes, Providencia, Vitacura | Tabla                                      |
| **8.7.**              | **Jara: Impacto del Voto de Protesta**           | Correlación aumento voto nulo vs desempeño de Jara; matiz a la narrativa dominante | Tablas                                     |
| **9.1.**              | **Bastiones de Kast**                            | Top-10 por % y por votos absolutos; diversidad territorial de la coalición | Tabla                                      |
| **9.2.**              | **Kast: Intensidad de Victorias**                | Resumen por categoría: Aplastante / Bastión Fuerte / Ventaja Sólida / Mayoría Simple | Tabla                                      |
| **9.3.**              | **Kast: Bastiones por Región (>60%)**            | Desglose regional de comunas con Kast >60%; La Araucanía y Los Lagos como corazón | Tabla                                      |
| **9.4.**              | **Crecimiento de Kast por Región**               | Crecimiento absoluto y en pp por región norte a sur; explosión en el norte | Tabla                                      |
| **9.5.**              | **Pérdidas de Votos de Kast**                    | Comunas donde Kast perdió votos absolutos entre vueltas (caso marginal) | Tabla                                      |
| **9.6.**              | **Impacto del Voto de Protesta en Kast**         | Correlación aumento protesta vs crecimiento de Kast; efecto amortiguador casi simétrico | Tabla                                      |
| **9.7.**              | **Crecimiento Superior/Inferior de Kast**        | Ranking doble: top-20 y bottom-20 por crecimiento absoluto y relativo | Tablas, scatter                            |
| **9.8.**              | **Kast: Gradiente Urbano-Rural**                 | Kast % por tamaño de comuna y macrozona; tabla cruzada y heatmap | Tablas, Gráfico de barras, heatmap         |
| **10.1.**             | **Transiciones 1ª→2ª Vuelta**                    | Matriz de transición, tasas de retención, desglose regional  | Tabla                                      |
| **10.2.**             | **Mapa de Transición Nacional**                  | Coropleta de cambios de ganador 1ª→2ª vuelta; grilla 3×3 por macrozona | Mapa                                       |
| **10.3.**             | **Mapas de Transición Metropolitanos**           | Transiciones 1ª→2ª vuelta en Gran Santiago, Valparaíso, Concepción | Mapas                                      |
| **11.1.**             | **Parisi vs Caída de Participación**             | Correlación Pearson/Spearman y scatter; top-10 comunas por caída de participación | Scatter, tabla                             |
| **11.2.**             | **Parisi vs Voto Nulo/Blanco**                   | Parisi % (1ª vuelta) vs tasas de nulo y blanco (2ª vuelta); r = 0,681 para nulo | Scatter, box plot, tabla                   |
| **11.3.**             | **Parisi vs Margen Kast-Jara**                   | Intensidad Parisi vs margen final; box plot por tramo Parisi | Scatter, box plot, tabla                   |
| **11.4.**             | **Clustering de Comunas Parisi**                 | K-means (método del codo + ACP); segmentación en 4 clústeres del comportamiento en 2ª vuelta | Grafico de lineas, Scatter, Radial         |
| **12.1.**             | **Participación 2021 vs 2025**                   | Voto voluntario vs obligatorio; impacto en votos válidos, nulos y blancos | Tabla                                      |
| **12.2.**             | **Evolución de Bloques 2021 vs 2025**            | Evolución de votos absolutos y porcentuales de bloques izquierda y derecha | Tabla                                      |
| **12.3.**             | **Realineamiento 2021→2025**                     | 194 comunas cambiaron de signo; matriz de transición; tasas de retención | Tablas                                     |
| **12.4.1.**           | **Mapa de Transición Nacional 2021→2025**        | Coropleta de cambios de ganador 2021→2025; grilla 3×3 por macrozona | Mapa                                       |
| **12.4.2.**           | **Mapas de Transición Metropolitanos 2021→2025** | Transiciones 2021→2025 en Gran Santiago, Valparaíso, Concepción | Mapas                                      |
| **12.**               | **Resumen Ejecutivo**                            | Hallazgos sintetizados y conclusiones estratégicas           | —                                          |

---

## 📝 Resumen de Hallazgos Principales

### 1. Victoria Contundente de Kast con Mandato Amplio
- **58,24%** de los votos válidos vs **41,76%** de Jara (base comunal, 346 comunas)
- Resultado oficial Servel: **58,16%** vs **41,84%** (incorporando voto exterior)
- Margen de **16,48 puntos porcentuales** y **más de 2 millones de votos** (2.046.992)
- Ganó en **las 16 regiones** y en **310 de 346 comunas** (89,6%)
- Margen sin precedente en la historia de los balotajes presidenciales chilenos desde el retorno a la democracia en 1990

### 2. Hegemonía Territorial Sin Precedentes
- Kast ganó el **89,6% de las comunas**; Jara solo **36 comunas (10,4%)**
- **~71%** de las comunas de Kast se ganaron con **más del 60%** del voto válido (220 de 310)
- Gradiente urbano-rural: el porcentaje de Kast aumenta sistemáticamente a medida que disminuye el tamaño de la comuna
- **Tres mundos políticos** articulados: Norte antisistema, élite santiaguina y Chile rural-conservador del sur

### 3. Explosión del Voto de Protesta (Nulo/Blanco)
- Voto nulo: **+421.458 votos (+116,9%)** entre primera y segunda vuelta
- Alcanzó el **5,85%** de los votos emitidos (nivel más alto en una elección presidencial chilena desde el retorno a la democracia)
- Correlación de Pearson entre voto Parisi (1ª vuelta) y voto nulo (2ª vuelta): **r = 0,681** — la más sólida de las tres correlaciones analizadas
- Voto nulo concentrado en bastiones de Parisi del **Norte Grande** (Antofagasta alcanzó 9,04%, Atacama 8,05%)

### 4. Voto Obligatorio y el Nuevo Electorado
- La participación aumentó **+60,4%** (8,3M → 13,4M votos emitidos)
- Kast casi **duplicó** su votación (3,6M → 7,2M, +97%)
- La izquierda creció solo **+587.000 votos** (4,6M → 5,2M, +13%)
- La izquierda perdió **~14 puntos porcentuales** de cuota de voto válido (55,87% → 41,84%)
- La asimetría confirma que los votantes recién incorporados se distribuyeron de forma significativamente más favorable a la derecha

### 5. Realineamiento Electoral 2021–2025
- El **56,1%** de las comunas cambió de ganador entre 2021 y 2025 (194 de 346)
- **158 comunas** pasaron de Boric a Kast — el 81,4% de la base territorial de la izquierda en 2021 se perdió
- Kast retuvo el **100%** de sus comunas de 2021 (152 comunas, +158 nuevas)
- La izquierda retuvo solo el **18,6%** de sus comunas de 2021 (36 de 194)
- Un realineamiento de esta magnitud —que afectó a más de la mitad de todas las comunas— no tiene precedente en balotajes presidenciales chilenos anteriores

### 6. Destino del Voto Parisi
- El **90,6%** de las comunas donde Parisi ganó la primera vuelta (58 de 64) fueron ganadas por Kast en la segunda
- Jara volteó solo **6 comunas de Parisi**, todas en el cinturón minero del norte con fuerte presencia sindical
- La transferencia fue **incompleta**: una fracción significativa optó por el voto nulo en lugar de validar su voto
- Segmentación mediante **clustering k-means** (4 clústeres): transferencia casi completa a Kast en el centro-sur conservador; protesta activa (voto nulo) en el Norte Grande; fragmentación en ciudades intermedias; transferencia parcial a Jara en comunas mineras con alta organización laboral

### 7. Geografía de la Victoria
- **Corazón electoral de Kast**: sur y centro-sur de Chile (La Araucanía, Los Lagos, Maule, Biobío, Ñuble — todas las comunas ganadas, márgenes frecuentemente superiores a 20 pp)
- **Bastiones de Jara**: Región Metropolitana (21 de sus 36 comunas, 58% del total) y enclaves mineros del norte
- **Norte**: mayor crecimiento de Kast en puntos porcentuales (Arica y Parinacota +36,47 pp; Tarapacá +35,21 pp)
- **Sur**: consolidación con máxima estabilidad (La Araucanía: 0% de comunas cambiaron de signo entre 2021 y 2025)

### 8. Resistencia al Voto de Protesta
- Kast creció entre **+38 y +34 pp** incluso en comunas con el mayor aumento de voto de protesta
- Diferencia de solo **~4 pp** entre los grupos de comunas con menor y mayor protesta
- Jara **no perdió votos absolutos en ninguna comuna** entre primera y segunda vuelta
- Pero **no logró expandirse** más allá de sus bastiones tradicionales: cero comunas volteadas desde Kast u otros candidatos de derecha

---

### Implicancia Estratégica Global

La elección de 2025 no fue un simple recambio presidencial, sino un **realineamiento electoral de magnitud histórica**. Kast construyó una **coalición territorial diversa** que articula el Norte antisistema, la élite santiaguina y el Chile rural-conservador del sur. La izquierda quedó **confinada a un archipiélago de bastiones urbanos** sin capacidad de expandirse hacia el Chile profundo. El **voto obligatorio** incorporó a millones de nuevos votantes que la derecha capturó con mucha mayor eficiencia. El elevado **voto de protesta** revela un descontento antisistema estructural que no fue completamente absorbido por ninguna de las dos opciones finales — y cuya gestión será uno de los desafíos definitorios del gobierno entrante.

---

## 📁 Estructura del Repositorio

```text
Chilean-Presidential-Elections-2025-Analysis/
├── first_round/                          (Análisis primera vuelta)
├── dashboard/                            (Streamlit dashboard)
│
├── second_round/
│   ├── 1_web_scraper/                    (Selenium - obtención de CSVs)
│   ├── 2_1.sql_analysis                  (SQL Server - análisis de datos)
│   └── 2_2.notebooks/
│       ├── README.md                     ← Readme en inglés
│       ├── README.es.md                  ← Readme en español
│       ├── requirements.txt
│       ├── electoral_analysis_2025_second_round_EN.ipynb
│       ├── electoral_analysis_2025_second_round_ES.ipynb
│       └── additional_scripts/           (Scripts de apoyo)
│
└── raw/                                  (Datos cargados por HTTPS)
    ├── chile_2025_second_round.csv
    ├── chile_2025_first_round.csv
    ├── chile_2021_second_round.csv
    ├── communes_population_2024.csv
    └── region_dimension.csv
```

---

## 📦 Fuentes de Datos

| Archivo                        | Descripción                                                  | Unidad |
| :----------------------------- | :----------------------------------------------------------- | :----- |
| `chile_2025_second_round.csv`  | Porcentajes de votos por candidato y comuna, 2ª vuelta 2025  | Comuna |
| `chile_2025_first_round.csv`   | Porcentajes de votos por candidato y comuna, 1ª vuelta 2025 (análisis Parisi) | Comuna |
| `chile_2021_second_round.csv`  | Porcentajes de votos por candidato y comuna, 2ª vuelta 2021 (análisis comparativo) | Comuna |
| `communes_population_2024.csv` | Estimaciones de población por comuna (proyección censo 2024) | Comuna |
| `region_dimension.csv`         | Metadatos de región: macrozona, orden de visualización, códigos de región | Región |
| GeoJSON comunas Chile          | Geometrías poligonales para las 346 comunas                  | Comuna |

Los datos geográficos se cargan desde el repositorio público [`caracena/chile-geojson`](https://github.com/caracena/chile-geojson).

**Fuente primaria:** Servicio Electoral de Chile (SERVEL), resultados oficiales de la segunda vuelta 2021 y 2025.

Todos los archivos de datos se cargan directamente desde el directorio `raw/` del repositorio por HTTPS. No se requiere descarga local.

---

## 🚀 Configuración Local

### Requisitos Previos

- Python 3.7 o superior (se recomienda 3.12)

### Instalación Paso a Paso

1. **Clonar el repositorio**

```bash
git clone https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis.git
cd Chilean-Presidential-Elections-2025-Analysis/second_round/2_notebooks
```

2. **Crear entorno virtual (recomendado)**

```bash
python -m venv venv

# Activar
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

O mediante conda (recomendado para geopandas en Windows):

```bash
conda install -c conda-forge geopandas pandas numpy matplotlib scikit-learn scipy seaborn jupyterlab
```

4. **Ejecutar el notebook**

```bash
# Versión en inglés
jupyter lab electoral_analysis_2025_second_round_EN.ipynb

# Versión en español
jupyter lab electoral_analysis_2025_second_round_ES.ipynb
```

El notebook carga todos los datos remotamente en la primera ejecución. Se requiere conexión a internet. Las ejecuciones posteriores funcionan sin conexión si se mantiene la sesión del kernel.

---

## 🧠 Notas Técnicas

### Normalización de Nombres de Comunas (`normalize_commune_name`)

Los joins entre los CSV de SERVEL y el GeoJSON dependen de una clave canónica generada por `normalize_commune_name()` (§ 2). El pipeline:

1. Minúsculas + eliminar espacios extremos
2. Descomposición NFD → eliminar marcas de combinación (elimina todos los diacríticos y diéresis, incluyendo `ü → u`)
3. Eliminar caracteres no alfanuméricos (guiones, paréntesis, puntuación)
4. Colapsar espacios internos a uno solo
5. Aplicar una tabla de corrección sobre la forma ASCII limpia

| Forma original                | Canónica         |
| :---------------------------- | :--------------- |
| `Marchigüe` / `Marchigue`     | `marchihue`      |
| `Llay-Llay`                   | `llaillay`       |
| `Trehuaco`                    | `treguaco`       |
| `Cabo de Hornos(ex-Navarino)` | `cabo de hornos` |

Los diacríticos se eliminan **antes** de la consulta de correcciones, por lo que todas las claves de la tabla usan ASCII plano — no se necesitan variantes acentuadas y la tabla es fácilmente extensible.

### Escala de Colores del Mapa de Márgenes

El margen con signo (Jara% − Kast%) se mapea a una paleta divergente mediante `assign_margin_color()`, que usa una tabla centralizada `MARGIN_BANDS`. Tanto la función de renderizado como la leyenda derivan sus colores de la misma fuente, garantizando consistencia.

| Banda    | Jara (tonos rojos) | Kast (tonos azules) |
| :------- | :----------------- | :------------------ |
| ≥ 50 pp  | `#7F1D1D`          | `#0C1E40`           |
| 40–50 pp | `#9B1C1C`          | `#0F2D5C`           |
| 30–40 pp | `#B91C1C`          | `#1A3D7C`           |
| 20–30 pp | `#DA4A4A`          | `#2A58A6`           |
| 10–20 pp | `#F28787`          | `#5E91E8`           |
| 0–10 pp  | `#F8A0A0`          | `#8BB2F0`           |

### Clustering de Comunas Parisi (k-means)

Se aplica clustering k-means a las comunas donde Parisi ganó la primera vuelta (64 comunas), utilizando variables electorales de la segunda vuelta (Kast %, Jara %, nulo %, blanco %, cambio en participación). El *k* óptimo se selecciona mediante el método del codo; se usa ACP (2 componentes) para visualización. Emergen cuatro clústeres con perfiles de comportamiento diferenciados:

| Clúster | Perfil                                | Geografía                                  |
| :------ | :------------------------------------ | :----------------------------------------- |
| 1       | Transferencia casi completa a Kast    | Centro-sur conservador                     |
| 2       | Protesta activa (voto nulo dominante) | Norte Grande                               |
| 3       | Fragmentación (alta competencia)      | Ciudades intermedias del norte             |
| 4       | Transferencia parcial a Jara          | Comunas mineras con alta densidad sindical |

### Renderizado de Mapas

Los mapas coropléticos usan una grilla `GridSpec` 3×3 organizada por macrozona:

| Grilla | Macrozona                  |
| :----- | :------------------------- |
| (0,0)  | Norte Grande               |
| (0,1)  | Norte Chico                |
| (0,2)  | Centro (Valparaíso y RM)   |
| (1,0)  | Centro (O'Higgins y Maule) |
| (1,1)  | Centro Sur                 |
| (1,2)  | Sur                        |
| (2,1)  | Patagonia                  |

Isla de Pascua y Juan Fernández se excluyen de todos los mapas (su geometría distorsiona los bounding boxes por macrozona). Las facetas de áreas metropolitanas filtran por claves normalizadas (`NOM_COM_NORM`) para evitar inconsistencias de codificación.

### Dataset de Transición Electoral

El dataset de transición 2021→2025 une ambos CSV de segunda vuelta en `(commune_norm, region)` tras la normalización. Un join de texto plano sobre nombres crudos descarta silenciosamente filas donde la codificación diverge entre archivos fuente; la clave normalizada previene esa pérdida de datos.

---

## 👥 Candidatos (Segunda Vuelta)

| Candidato         | Bloque               | Color     |
| :---------------- | :------------------- | :-------- |
| Jeannette Jara    | Izquierda            | `#E54944` |
| José Antonio Kast | Derecha Conservadora | `#35466D` |

---

## 📄 Licencia y Atribución

- **Licencia**: MIT
- **Autor**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Portafolio web:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Email:** adroguett.consultor@gmail.com
- **Fuentes de datos:** SERVEL (dominio público, autoridad electoral oficial)
- **Tecnologías:** Jupyter Notebooks · Pandas · NumPy · Matplotlib · GeoPandas · Seaborn · scikit-learn · SciPy

---

## ⭐ Agradecimientos

Si este proyecto te ha sido útil, ¡considera darle una estrella en GitHub!
