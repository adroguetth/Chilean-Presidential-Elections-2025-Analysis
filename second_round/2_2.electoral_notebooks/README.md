# 🗳️ Electoral Analysis — Chile 2025 · Presidential Runoff

**¿Buscas la versión en español?** → [README.es.md](README.es.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-f37626?style=flat-square&logo=jupyter&logoColor=white) 

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=flat-square&logo=geopandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-4c72b0?style=flat-square&logo=python&logoColor=white) ![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=flat-square&logo=python&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white) ![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=flat-square&logo=scipy&logoColor=white)

**Data analysis:** quantitative processing, spatial analysis, statistical correlations and machine learning clustering<br/>
**Political analysis:** independent expert commentary, contextualization and interpretation

---

## 📥 Quick Access

| Language       | Notebook                                        | Format                                                       |
| :------------- | :---------------------------------------------- | :----------------------------------------------------------- |
| **🇬🇧 English** | `electoral_analysis_2025_second_round_EN.ipynb` | [View on GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/second_round/2_notebooks/electoral_analysis_2025_second_round_EN.ipynb) |
| **🇪🇸 Español** | `electoral_analysis_2025_second_round_ES.ipynb` | [View on GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/second_round/2_notebooks/electoral_analysis_2025_second_round_ES.ipynb) |

---

## 📋 Overview

This notebook presents a territorial, demographic, statistical and political analysis of the **Chilean presidential runoff of December 14, 2025**, in which José Antonio Kast (Republican Party) defeated Jeannette Jara (government coalition) by a margin of 16.48 percentage points, the largest in the history of Chilean runoffs since the return to democracy.

The analysis covers the complete anatomy of the result: national vote totals, communal and regional territorial mapping, the explosive increase in null and blank votes, the urban-rural gradient of Kast's vote, the destination of Franco Parisi's electorate (through statistical correlations and k-means clustering), communal transition maps between the first and second rounds and between the 2021 and 2025 runoffs, and strategic conclusions for each of the main political actors.

The election was held under **compulsory voting** — reinstated in 2022 and in effect since October 2024 — which increased total turnout by **+60.4%** compared to the 2021 runoff (8.3M → 13.4M votes cast) and constitutes the main institutional lens that conditions all comparisons between cycles.

**Methodological note.** Unless otherwise indicated, all data are calculated from the communal base of 346 continental and insular communes (public SERVEL data), which yields **Kast 58.24% / Jara 41.76%**. Servel's official national result — which incorporates votes cast abroad — was **Kast 58.16% / Jara 41.84%**. The divergence is documented and discussed in Section 6.

---

## 📊 Analysis Sections

| Section               | Title                                         | Content                                                      | Visualizations                    |
| --------------------- | :-------------------------------------------- | :----------------------------------------------------------- | :-------------------------------- |
| **1.**                | **Setup**                                     | Dependencies, imports, configuration                         | —                                 |
| **2.**                | **Data Loading**                              | CSVs, population, regional dimension, GeoJSON · `normalize_commune_name()` for joins between datasets | —                                 |
| **3.**                | **Turnout vs First Round**                    | Comparison of valid, null and blank votes; anomaly of a runoff with falling valid votes | Table                             |
| **4.1.** & **4.2**    | **Null Vote — National (Region, Macrozone)**  | Explosion of null vote by region and macrozone (+116.9%, historical high) | Tables                            |
| **4.3.**              | **Null Vote — Commune Level**                 | Top-20 communes by absolute and relative increase; distribution by first-round winner | Tables, Bar charts, box plots     |
| **5.1.** & **5.2.**   | **Blank Vote — National (Region, Macrozone)** | Variation of blank vote by region and macrozone; contrast with null vote pattern | Tables                            |
| **5.3.**              | **Blank Vote — Commune Level**                | Top-20 communes by absolute and relative increase; Matthei strongholds as epicenter | Table, Bar charts, box plots      |
| **6.**                | **Winner Declaration**                        | National result, margin, methodological note on overseas vote | Table, Bar chart                  |
| **7.1.**              | **Territorial Mapping — Communes**            | 310 vs 36 communes won; percentage and population coverage   | Table                             |
| **7.2.**              | **Territorial Mapping — Regions**             | All 16 regions for Kast; north-to-south ordering             | Table                             |
| **7.3.**              | **Margin Map by Macrozone**                   | Choropleth (Jara%−Kast%) at commune level; 3×3 grid by macrozone | Maps                              |
| **7.4.**              | **Metropolitan Areas (Margin)**               | Margin maps for Greater Santiago, Valparaíso and Concepción, among others | Maps                              |
| **8.1.**              | **Jara Strongholds**                          | 36 communes with absolute majority; geographic and socioeconomic profile | Table                             |
| **8.2.1**             | **Jara: Competitive Communes (<2 pp)**        | 6 communes decided by less than 2 pp; recovery map for Jara's coalition | Table                             |
| **8.2.2** & **8.2.3** | **Jara: Communes Lost by <5 pp**              | 20 additional competitive communes; northern regional capitals | Table, Heatmap, Stacked bar chart |
| **8.3.**              | **Communes Flipped by Jara (North)**          | 6 Parisi communes captured by Jara; class voting in mining   | Table, Bar chart                  |
| **8.4.**              | **Jara's Vote Retention**                     | Full retention of first-round communes; solidity vs. ceiling problem | Analysis                          |
| **8.5.**              | **Jara's Vote Growth**                        | Communes where Jara grew in absolute votes; Greater Santiago as engine | Table                             |
| **8.6.**              | **Jara: Penetration in Elite Communes**       | Jara's percentage growth in Las Condes, Providencia, Vitacura | Table                             |
| **8.7.**              | **Jara: Impact of Protest Vote**              | Correlation between null vote increase and Jara's performance; nuance to the dominant narrative | Tables                            |
| **9.1.**              | **Kast Strongholds**                          | Top-10 by % and by absolute votes; territorial diversity of the coalition | Table                             |
| **9.2.**              | **Kast: Victory Intensity**                   | Summary by category: Landslide / Stronghold / Solid Advantage / Simple Majority | Table                             |
| **9.3.**              | **Kast: Regional Strongholds (>60%)**         | Regional breakdown of communes with Kast >60%; La Araucanía and Los Lagos as heartland | Table                             |
| **9.4.**              | **Kast's Growth by Region**                   | Absolute and pp growth by region north to south; explosion in the north | Table                             |
| **9.5.**              | **Kast's Vote Losses**                        | Communes where Kast lost absolute votes between rounds (marginal case) | Table                             |
| **9.6.**              | **Impact of Protest Vote on Kast**            | Correlation between protest increase and Kast's growth; almost symmetric buffering effect | Table                             |
| **9.7.**              | **Kast's Top/Bottom Growth**                  | Double ranking: top-20 and bottom-20 by absolute and relative growth | Tables, scatter                   |
| **9.8.**              | **Kast: Urban-Rural Gradient**                | Kast % by commune size and macrozone; cross-tabulation and heatmap | Tables, Bar chart, heatmap        |
| **10.1.**             | **Transitions 1st→2nd Round**                 | Transition matrix, retention rates, regional breakdown       | Table                             |
| **10.2.**             | **National Transition Map**                   | Choropleth of winner changes 1st→2nd round; 3×3 grid by macrozone | Map                               |
| **10.3.**             | **Metropolitan Transition Maps**              | Transitions 1st→2nd round in Greater Santiago, Valparaíso, Concepción | Maps                              |
| **11.1.**             | **Parisi vs Turnout Drop**                    | Pearson/Spearman correlation and scatter; top-10 communes by turnout drop | Scatter, table                    |
| **11.2.**             | **Parisi vs Null/Blank Vote**                 | Parisi % (1st round) vs null and blank rates (2nd round); r = 0.681 for null | Scatter, box plot, table          |
| **11.3.**             | **Parisi vs Kast-Jara Margin**                | Parisi intensity vs final margin; box plot by Parisi bracket | Scatter, box plot, table          |
| **11.4.**             | **Parisi Commune Clustering**                 | K-means (elbow method + PCA); 4-cluster segmentation of 2nd round behavior | Line chart, Scatter, Radial       |
| **12.1.**             | **Turnout 2021 vs 2025**                      | Voluntary vs compulsory voting; impact on valid, null and blank votes | Table                             |
| **12.2.**             | **Block Evolution 2021 vs 2025**              | Evolution of absolute and percentage votes of left and right blocs | Table                             |
| **12.3.**             | **Realignment 2021→2025**                     | 194 communes changed sign; transition matrix; retention rates | Tables                            |
| **12.4.1.**           | **National Transition Map 2021→2025**         | Choropleth of winner changes 2021→2025; 3×3 grid by macrozone | Map                               |
| **12.4.2.**           | **Metropolitan Transition Maps 2021→2025**    | Transitions 2021→2025 in Greater Santiago, Valparaíso, Concepción | Maps                              |
| **12.**               | **Executive Summary**                         | Synthesized findings and strategic conclusions               | —                                 |

---

## 📝 Summary of Main Findings

### 1. Kast's Decisive Victory with Broad Mandate
- **58.24%** of valid votes vs **41.76%** for Jara (communal base, 346 communes)
- Official Servel result: **58.16%** vs **41.84%** (incorporating overseas vote)
- Margin of **16.48 percentage points** and **over 2 million votes** (2,046,992)
- Won in **all 16 regions** and in **310 of 346 communes** (89.6%)
- Unprecedented margin in the history of Chilean presidential runoffs since the return to democracy in 1990

### 2. Unprecedented Territorial Hegemony
- Kast won **89.6% of communes**; Jara only **36 communes (10.4%)**
- **~71%** of Kast's communes were won with **over 60%** of the valid vote (220 of 310)
- Urban-rural gradient: Kast's percentage systematically increases as commune size decreases
- **Three political worlds** articulated: anti-system North, Santiago elite, and rural-conservative southern Chile

### 3. Explosion of Protest Vote (Null/Blank)
- Null vote: **+421,458 votes (+116.9%)** between first and second rounds
- Reached **5.85%** of votes cast (highest level in a Chilean presidential election since the return to democracy)
- Pearson correlation between Parisi vote (1st round) and null vote (2nd round): **r = 0.681** — the strongest of the three correlations analyzed
- Null vote concentrated in Parisi strongholds of the **Norte Grande** (Antofagasta reached 9.04%, Atacama 8.05%)

### 4. Compulsory Voting and the New Electorate
- Turnout increased **+60.4%** (8.3M → 13.4M votes cast)
- Kast nearly **doubled** his vote (3.6M → 7.2M, +97%)
- The left grew by only **+587,000 votes** (4.6M → 5.2M, +13%)
- The left lost **~14 percentage points** of valid vote share (55.87% → 41.84%)
- The asymmetry confirms that newly incorporated voters distributed significantly more favorably to the right

### 5. Electoral Realignment 2021–2025
- **56.1%** of communes changed winner between 2021 and 2025 (194 of 346)
- **158 communes** switched from Boric to Kast — 81.4% of the left's 2021 territorial base was lost
- Kast retained **100%** of his 2021 communes (152 communes, +158 new)
- The left retained only **18.6%** of its 2021 communes (36 of 194)
- A realignment of this magnitude — affecting more than half of all communes — is unprecedented in previous Chilean presidential runoffs

### 6. Destination of the Parisi Vote
- **90.6%** of communes where Parisi won the first round (58 of 64) were won by Kast in the second
- Jara flipped only **6 Parisi communes**, all in the northern mining belt with strong union presence
- The transfer was **incomplete**: a significant fraction opted for null voting rather than validating their vote
- Segmentation via **k-means clustering** (4 clusters): near-complete transfer to Kast in the conservative south-center; active protest (null vote) in the Norte Grande; fragmentation in intermediate cities; partial transfer to Jara in mining communes with high union organization

### 7. Geography of Victory
- **Kast's electoral heartland**: southern and south-central Chile (La Araucanía, Los Lagos, Maule, Biobío, Ñuble — all communes won, margins frequently above 20 pp)
- **Jara's strongholds**: Metropolitan Region (21 of her 36 communes, 58% of total) and northern mining enclaves
- **North**: Kast's largest growth in percentage points (Arica y Parinacota +36.47 pp; Tarapacá +35.21 pp)
- **South**: consolidation with maximum stability (La Araucanía: 0% of communes changed sign between 2021 and 2025)

### 8. Resistance to Protest Vote
- Kast grew between **+38 and +34 pp** even in communes with the largest protest vote increase
- Difference of only **~4 pp** between communes with lowest and highest protest
- Jara **did not lose absolute votes in any commune** between first and second rounds
- But **failed to expand** beyond her traditional strongholds: zero communes flipped from Kast or other right-wing candidates

---

### Strategic Global Implication

The 2025 election was not a simple presidential succession, but an **electoral realignment of historic magnitude**. Kast built a **diverse territorial coalition** articulating the anti-system North, the Santiago elite, and rural-conservative southern Chile. The left was **confined to an archipelago of urban strongholds** with no capacity to expand into deep Chile. **Compulsory voting** brought in millions of new voters that the right captured much more efficiently. The high **protest vote** reveals a structural anti-system discontent that was not fully absorbed by either of the two final options — and whose management will be one of the defining challenges of the incoming government.

---

## 📁 Repository Structure

```text
Chilean-Presidential-Elections-2025-Analysis/
├── first_round/                          (First round analysis)
├── dashboard/                            (Streamlit dashboard)
│
├── second_round/
│   ├── 1_web_scraper/                    (Selenium - CSV acquisition)
│   ├── 2_1.sql_analysis                  (SQL Server - data analysis)
│   └── 2_2.notebooks/
│       ├── README.md                     ← Readme in English
│       ├── README.es.md                  ← Readme in Spanish
│       ├── requirements.txt
│       ├── electoral_analysis_2025_second_round_EN.ipynb
│       ├── electoral_analysis_2025_second_round_ES.ipynb
│       └── additional_scripts/           (Support scripts)
│
└── raw/                                  (Data loaded via HTTPS)
    ├── chile_2025_second_round.csv
    ├── chile_2025_first_round.csv
    ├── chile_2021_second_round.csv
    ├── communes_population_2024.csv
    └── region_dimension.csv
```

------

## 📦 Data Sources

| File                           | Description                                                  | Unit    |
| ------------------------------ | ------------------------------------------------------------ | ------- |
| `chile_2025_second_round.csv`  | Candidate vote shares by commune, 2025 runoff                | Commune |
| `chile_2025_first_round.csv`   | Candidate vote shares by commune, 2025 first round (Parisi analysis) | Commune |
| `chile_2021_second_round.csv`  | Candidate vote shares by commune, 2021 runoff (comparative analysis) | Commune |
| `communes_population_2024.csv` | Population estimates by commune (2024 census projection)     | Commune |
| `region_dimension.csv`         | Region metadata: macrozone, display order, region codes      | Region  |
| Chilean commune GeoJSON        | Polygon geometries for all 346 communes                      | Commune |

Geographic data is loaded from the public [`caracena/chile-geojson`](https://github.com/caracena/chile-geojson) repository.

**Primary source:** Servicio Electoral de Chile (SERVEL), official runoff results 2021 and 2025.

All data files are loaded directly from the repository's `raw/` directory over HTTPS. No local data download is required.

------

## 🚀 Local Setup

### Prerequisites

- Python 3.7 or higher (3.12 recommended)

### Step-by-Step Installation

1. **Clone the repository**

```bash
git clone https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis.git
cd Chilean-Presidential-Elections-2025-Analysis/second_round/2_notebooks
```

1. **Create a virtual environment (recommended)**

```bash
python -m venv venv

# Activate
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

Or via conda (recommended for geopandas on Windows):

```bash
conda install -c conda-forge geopandas pandas numpy matplotlib scikit-learn scipy seaborn jupyterlab
```

1. **Run the notebook**

```bash
# English version
jupyter lab electoral_analysis_2025_second_round_EN.ipynb

# Spanish version
jupyter lab electoral_analysis_2025_second_round_ES.ipynb
```

The notebook fetches all data remotely on first run. An internet connection is required. Subsequent runs work offline if the kernel session is maintained.

------

## 🧠 Technical Notes

### Commune Name Normalisation (`normalize_commune_name`)

Cross-dataset joins between the SERVEL CSVs and the GeoJSON rely on a canonical commune key generated by `normalize_commune_name()` (§ 2). The pipeline:

1. Lowercase + strip surrounding whitespace
2. NFD decomposition → strip combining marks (removes all diacritics and diaereses, including `ü → u`)
3. Remove non-alphanumeric characters (hyphens, parentheses, punctuation)
4. Collapse internal whitespace to a single space
5. Apply a curated correction table on the clean ASCII form

| Raw form                      | Canonical        |
| ----------------------------- | ---------------- |
| `Marchigüe` / `Marchigue`     | `marchihue`      |
| `Llay-Llay`                   | `llaillay`       |
| `Trehuaco`                    | `treguaco`       |
| `Cabo de Hornos(ex-Navarino)` | `cabo de hornos` |

Diacritics are stripped **before** the correction lookup, so all correction keys use plain ASCII — no accented variants are required and the table is straightforwardly extensible.

### Margin Map Colour Scale

The signed margin (Jara% − Kast%) is mapped to a diverging palette via `assign_margin_color()`, which uses a centralised `MARGIN_BANDS` lookup table. Both the rendering function and the legend derive their colours from the same source, guaranteeing consistency.

| Band     | Jara (red tones) | Kast (blue tones) |
| -------- | ---------------- | ----------------- |
| ≥ 50 pp  | `#7F1D1D`        | `#0C1E40`         |
| 40–50 pp | `#9B1C1C`        | `#0F2D5C`         |
| 30–40 pp | `#B91C1C`        | `#1A3D7C`         |
| 20–30 pp | `#DA4A4A`        | `#2A58A6`         |
| 10–20 pp | `#F28787`        | `#5E91E8`         |
| 0–10 pp  | `#F8A0A0`        | `#8BB2F0`         |

### Parisi Clustering (k-means)

K-means clustering is applied to communes where Parisi won the first round (64 communes), using second-round electoral features (Kast %, Jara %, null %, blank %, turnout change). The optimal *k* is selected via the elbow method; PCA (2 components) is used for visualisation. Four clusters emerge with distinct behavioural profiles:

| Cluster | Profile                             | Geography                                     |
| ------- | ----------------------------------- | --------------------------------------------- |
| 1       | Near-complete transfer to Kast      | Conservative centre-south                     |
| 2       | Active protest (null vote dominant) | Norte Grande                                  |
| 3       | Fragmentation (high competition)    | Intermediate northern cities                  |
| 4       | Partial transfer to Jara            | Mining communes with high trade-union density |

### Map Rendering

Choropleth maps use a 3×3 `GridSpec` layout organised by macrozone:

| Grid  | Macrozone                  |
| ----- | -------------------------- |
| (0,0) | Norte Grande               |
| (0,1) | Norte Chico                |
| (0,2) | Centro (Valparaíso y RM)   |
| (1,0) | Centro (O'Higgins y Maule) |
| (1,1) | Centro Sur                 |
| (1,2) | Sur                        |
| (2,1) | Patagonia                  |

Isla de Pascua and Juan Fernández are excluded from all maps (outlier geometry distorts macrozone bounding boxes). Metropolitan area facets filter on normalised commune keys (`NOM_COM_NORM`) to avoid encoding mismatches.

### Electoral Transition Dataset

The 2021→2025 transition dataset joins both second-round CSVs on `(commune_norm, region)` after normalisation. A plain string join on raw commune names silently drops rows wherever encoding diverges between source files; the normalised key prevents that data loss.

------

## 👥 Candidates (Second Round)

| Candidate         | Bloc               | Colour    |
| ----------------- | ------------------ | --------- |
| Jeannette Jara    | Left               | `#E54944` |
| José Antonio Kast | Conservative Right | `#35466D` |

------

## 📄 License and Attribution

- **License**: MIT
- **Author**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Web portfolio:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Email:** adroguett.consultor@gmail.com
- **Data sources:** SERVEL (public domain, official electoral authority)
- **Technologies:** Jupyter Notebooks · Pandas · NumPy · Matplotlib · GeoPandas · Seaborn · scikit-learn · SciPy

------

## ⭐ Acknowledgements

If this project is useful to you, please consider giving it a star on GitHub!
