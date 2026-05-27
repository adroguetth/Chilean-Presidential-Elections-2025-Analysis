# 🗳️ Electoral Analysis — Chile 2025 · Presidential First Round

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-f37626?style=flat-square&logo=jupyter&logoColor=white) 

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=flat-square&logo=geopandas&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-4c72b0?style=flat-square&logo=python&logoColor=white)

**Data analytics:** quantitative processing, spatial analysis and visualisation
**Political analysis:** independent expert commentary, contextualisation and interpretation

------

## 📥 Quick Access

| Language       | Notebook                           | Format                                                       |
| :------------- | :--------------------------------- | :----------------------------------------------------------- |
| **🇬🇧 English** | `electoral_analysis_2025_EN.ipynb` | [View on GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_notebooks/electoral_analysis_2025_EN.ipynb) |
| **🇪🇸 Español** | `electoral_analysis_2025_ES.ipynb` | [View on GitHub](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_notebooks/electoral_analysis_2025_ES.ipynb) |

------

## 📋 Overview

This notebook presents a comprehensive territorial, demographic and political analysis of the Chilean presidential first round held in November 2025. It covers national results, commune-level winner mapping, regional breakdowns, urban–rural voting gradients, electoral strongholds, runoff projections and a comparative study of the realignment between the 2021 and 2025 first rounds.

The analysis was produced under **compulsory voting** — reinstated in Chile in 2022 and in effect since the October 2024 municipal elections — which generated an **89.1% increase** in total votes cast (7.08 million in 2021 → 13.39 million in 2025) and constitutes the primary methodological lens for all cross-cycle comparisons.

---

### 📊 Analysis Sections

| Section                         | Content                                                      | Visualizations   |
| ------------------------------- | ------------------------------------------------------------ | ---------------- |
| **1. Setup**                    | Dependencies, imports, configuration                         | None             |
| **2. Data Loading**             | CSVs, population, region dimension, GeoJSON <br/>**2.4 aormalize_commune_name()** Canonical commune key for cross-dataset joins | None             |
| **3. General Participation**    | Valid/null/blank vote analysis; comparison with 2021         | Table            |
| **4. National Results**         | Results by candidate; bloc-level strategic reading           | Table, bar chart |
| **5. Electoral Strongholds**    | Top-10 communes per candidate; geographic profiles           | Table            |
| **6. Territorial Mapping**      | Communes won per candidate; territory–demographics paradox   | Table, bar chart |
| **7. Results by Region**        | Three-Chile trifurcation; swing regions                      | Table, maps      |
| **8. Regional Capitals**        | Capital vs. hinterland voting divergence                     | Table            |
| **9. Urban Centre Behaviour**   | Five-tier urban–rural gradient (>200k → <10k inhabitants)    | Table, bar chart |
| **10. Winners by Commune**      | National choropleth + metropolitan area facets               | Maps             |
| **11. Recoverable Communes**    | Margins < 1,000 votes; mobilisation cost by macrozone        | Table, bar chart |
| **12. Runoff Projections **     | Four vote-transfer scenarios (Jara vs. Kast)                 | Table            |
| **13. Anti-Establishment Vote** | Parisi vs. the duopoly; commune-level dominance analysis     | Table            |
| **14.  Comparative 2021–2025**  | Realignment matrix; Parisi growth; territorial transitions <br/>**Transition Maps** Canonical commune key for cross-dataset joins | Table, Maps      |
| **Executive Summary**           | Summary of findings and conclusion                           | None             |


------

## 📝 Key Findings

| Finding                                        | Detail                                                       |
| :--------------------------------------------- | :----------------------------------------------------------- |
| **No candidate exceeded 27%**                  | The right bloc combined (Kast + Kaiser + Matthei) exceeded **50%** for the first time under competitive conditions. |
| **Jara led through demographic concentration** | She controlled **76.9% of the population** in communes larger than 200,000 inhabitants while winning only 105 of 346 communes. |
| **Kast dominated territorially**               | 169 communes, with dominance growing monotonically as commune size decreases. Inflection point: ~50,000 inhabitants. |
| **Parisi's northern monopoly**                 | Most structurally intense result on the map: **95.7% territorial retention** from 2021, growth in 15 of 16 regions. |
| **45% of communes changed winner**             | Between 2021 and 2025. The centre-left (Provoste) retained **0%** of its 2021 communes; 70% migrated to Parisi. |
| **Runoff projection**                          | Under all four transfer scenarios, **Kast projects a victory**, ranging from +113k votes (optimal Jara) to +2.4M (optimal Kast). |

------

## 📁 Repository Structure

```text
Chilean-Presidential-Elections-2025-Analysis/
├── first_round
│ 	└── 2_notebooks/
│		├── README.md
│		├── requirements.txt
│		├── electoral_analysis_2025_EN.ipynb      # English version
│		└── electoral_analysis_2025_ES.ipynb      # Spanish version
└── raw/                                       (data loaded automatically)
    ├── chile_2025_first_round.csv
    ├── chile_2021_first_round.csv
    ├── communes_population_2024.csv
    └── region_dimension.csv
```



------

## 📦 Data Sources

| File                           | Description                                              | Unit    |
| :----------------------------- | :------------------------------------------------------- | :------ |
| `chile_2025_first_round.csv`   | Candidate vote shares by commune, 2025 first round       | Commune |
| `chile_2021_first_round.csv`   | Candidate vote shares by commune, 2021 first round       | Commune |
| `communes_population_2024.csv` | Population estimates by commune (2024 census projection) | Commune |
| `region_dimension.csv`         | Region metadata: macrozone, display order, region codes  | Region  |
| Chilean commune GeoJSON        | Polygon geometries for all 346 communes                  | Commune |

Geographic data is loaded from the public [`caracena/chile-geojson`](https://github.com/caracena/chile-geojson) repository, with automatic per-region fallback if a single-file source is unavailable.

**Primary source:** Servicio Electoral de Chile (SERVEL), official first-round results 2021 and 2025.

All data files are loaded directly from the repository's `raw/` directory over HTTPS. No local data download is required to run the notebook.



------

## 🚀 Local Setup

### Prerequisites

- Python 3.7 or higher (3.12 recommended)



### **Step-by-Step Installation**

1. **Clone the Repository**
   
```bash
git clone https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis.git
cd Chilean-Presidential-Elections-2025-Analysis/first_round/2_notebooks
```
2. **Create Virtual Environment (recommended)**

```bash
python -m venv venv

# Activate environment
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

Or  via conda (recommended for geopandas on Windows):

```bash
conda install -c conda-forge geopandas pandas numpy matplotlib jupyterlab
```



4. **Running the Notebook**

```bash
# English version
jupyter lab electoral_analysis_2025_EN.ipynb

# Spanish version
jupyter lab electoral_analysis_2025_ES.ipynb
```

The notebook fetches all data remotely on first run. An internet connection is required. Subsequent runs work offline if the kernel session is maintained.



------

## 🧠 Technical Notes

### Commune Name Normalisation (`normalize_commune_name`)

Cross-dataset joins between the SERVEL CSVs and the GeoJSON rely on a canonical commune key generated by `normalize_commune_name()` (§ 2.4). The pipeline:

1. Lowercase + strip whitespace
2. NFD decomposition → strip combining marks (removes all diacritics and diaereses, including `ü` → `u`)
3. Remove non-alphanumeric characters (hyphens, parentheses, punctuation)
4. Collapse whitespace
5. Apply a curated correction table on the clean ASCII form

Corrections handle known encoding divergences between datasets:

| Raw form                      | Canonical        |
| :---------------------------- | :--------------- |
| `Marchigüe` / `Marchigue`     | `marchihue`      |
| `Llay-Llay`                   | `llaillay`       |
| `Trehuaco`                    | `treguaco`       |
| `Cabo de Hornos(ex-Navarino)` | `cabo de hornos` |

### Electoral Realignment (`df_change`)

The 2021→2025 transition dataset is constructed by joining both electoral CSVs on `(commune_norm, region)` after normalisation (§ 14.4). A plain string join on raw commune names silently drops rows wherever encoding diverges between the two source files; the normalised key prevents that data loss.

### Map Rendering

Choropleth maps use a 3×3 `GridSpec` layout organised by macrozone:

| Grid  | Macrozone                  |
| :---- | :------------------------- |
| (0,0) | Norte Grande               |
| (0,1) | Norte Chico                |
| (0,2) | Centro (Valparaíso y RM)   |
| (1,0) | Centro (O'Higgins y Maule) |
| (1,1) | Centro Sur                 |
| (1,2) | Sur                        |
| (2,1) | Patagonia                  |

Isla de Pascua and Juan Fernández are excluded from all maps (outlier geometry distorts regional bounding boxes). Metropolitan area facets use normalised commune keys for GeoJSON filtering to avoid encoding mismatches with raw `NOM_COM` strings.

------

## 👥 Candidates

| Candidate              | Bloc               | Colour    |
| :--------------------- | :----------------- | :-------- |
| Jeannette Jara         | Left               | `#E54944` |
| José Antonio Kast      | Right              | `#35466D` |
| Franco Parisi          | Anti-system        | `#4B70B5` |
| Johannes Kaiser        | Libertarian        | `#F3832C` |
| Evelyn Matthei         | Traditional Right  | `#226FD4` |
| Harold Mayne-Nicholls  | Independent        | `#BED8DF` |
| Marco Enríquez-Ominami | Left (independent) | `#DD2883` |
| Eduardo Artés          | Far Left           | `#CA1C1F` |



------

## 📄 License and Attribution

- **License**: MIT
- **Author**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Web portfolio:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Email:** adroguett.consultor@gmail.com
- **Data Sources**:
  - SERVEL (public domain, official electoral authority)
- **Technologies**:
  - Jupyter Notebooks
  - Matplotlib
  - Pandas, NumPy (data processing)

------

## ⭐ Acknowledgements

If this project is useful to you, please consider giving it a star on GitHub!