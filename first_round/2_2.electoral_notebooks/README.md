# 🗳️ Electoral Analysis — Chile 2025 · Presidential First Round
**¿Buscas la versión en español?** → [README.es.md](README.es.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-f37626?style=flat-square&logo=jupyter&logoColor=white) 

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=flat-square&logo=geopandas&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-4c72b0?style=flat-square&logo=python&logoColor=white)

**Data analytics:** quantitative processing, spatial analysis and visualisation <br/>
**Political analysis:** independent expert commentary, contextualisation and interpretation

------

## 📥 Quick Access

| Language       | Notebook                                        | Format                                                       |
| :------------- | :----------------------------------------------- | :----------------------------------------------------------- |
| **🇬🇧 English** | `electoral_analysis_2025_first_round_EN.ipynb` | https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_2.electoral_notebooks/electoral_analysis_2025_first_round_EN.ipynb |
| **🇪🇸 Español** | `electoral_analysis_2025_first_round_ES.ipynb` | https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/first_round/2_2.electoral_notebooks/electoral_analysis_2025_first_round_ES.ipynb |

------

## 📋 Overview

Chile's November 2025 presidential first round produced one of the most fragmented results in the country's democratic history — no candidate cleared 27% of the valid vote — and set up a runoff between Jeannette Jara (26.75%) and José Antonio Kast (23.96%), with Franco Parisi's anti-establishment surge (19.71%) reshaping the electoral map along the way.

This repository contains a comprehensive territorial, demographic, and political analysis of that first round, built entirely from official Servel data at the commune level. Beyond national results, it maps **who won where, and why**: commune-level winner mapping, regional breakdowns, the urban–rural voting gradient, each candidate's electoral strongholds, communes decided by razor-thin margins, runoff-scenario projections, and a comparative study of the realignment between the 2021 and 2025 first rounds.

The analysis was produced under **compulsory voting** — reinstated in Chile in 2022 and in effect since the October 2024 municipal elections — which generated an **89.1% increase** in total votes cast (7.08 million in 2021 → 13.39 million in 2025) and constitutes the primary methodological lens for all cross-cycle comparisons in this study.

The notebook combines two layers throughout: **data analytics** (quantitative processing, spatial analysis, and visualisation) and **political analysis** (independent expert commentary and contextualisation), and is available in full in both English and Spanish.

---

### 📊 Analysis Sections

| # | Section | What it covers |
| :- | :------- | :--------------- |
| 1–2 | Setup & Data Loading | Environment, data ingestion, commune-name normalisation |
| 3 | General Turnout Statistics | Participation, valid/null/blank vote rates under compulsory voting |
| 4 | The Null Vote | Regional and commune-level geography of active protest |
| 5 | The Blank Vote | Regional and commune-level geography of passive protest |
| 6 | National Results by Candidate | Competitiveness groups and ideological blocs |
| 7 | Electoral Strongholds | Top 15 communes and socioeconomic profile, per candidate |
| 8 | Territorial Mapping and Vote Distribution | Communes won, macrozones, regional results, regional gaps |
| 9 | Regional Capitals | The urban-administrative vote vs. the rest of the region |
| 10 | Electoral Behaviour in Urban Centres | The urban–rural gradient across five population segments |
| 11 | Recoverable Communes | Communes lost by fewer than 1,000 votes; mobilisation cost by macrozone |
| 12 | Runoff Projection | Four vote-transfer scenarios, Jara vs. Kast |
| 13 | Franco Parisi: The Anti-Establishment Vote | Where — and why — the anti-system vote concentrated |
| 14 | Comparative Analysis: Evolution 2021–2025 | Turnout trends, bloc evolution, Parisi's rise, the realignment map |
| — | Strategic Recommendations & Summary | Candidate-by-candidate strategic reading and executive summary |

Each chapter follows the same structure: an introduction framing the question, a data-driven analysis, and a closing synthesis (`Conclusion X.X`) tying the finding back to the chapter's opening question.

------

## 📝 Key Findings

**A country without majorities.** No candidate exceeded 27% of the valid vote. The combined right (Kast + Kaiser + Matthei) crossed 50% for the first time in the voluntary/compulsory-voting era — a threshold already hinted at in 2021 (Kast + Sichel ≈ 40.8%) but only consolidated in 2025.

| Candidate | Votes | % | 2021→2025 |
| :--------- | -----: | ---: | :--------- |
| Jeannette Jara | 3,446,854 | 26.75% | +32% |
| José Antonio Kast | 3,086,963 | 23.96% | +58% |
| Franco Parisi | 2,550,770 | 19.71% | **+184%** |
| Johannes Kaiser | 1,796,034 | 13.94% | *(new)* |
| Evelyn Matthei | 1,603,104 | 12.44% | +79% |
| Marco Enríquez-Ominami | 154,321 | 1.2% | **−71%** |

**A territorial paradox.** Kast won more communes (169, 48.8%) but came second in votes; Jara won fewer communes (105, 30.3%) but led the national count — the clearest signal that Chile split into **three electoral countries**: an anti-establishment North (Parisi), an urban-progressive Centre (Jara), and a rural-conservative Centre-South (Kast).

**The urban–rural gradient.** Vote share correlates almost mechanically with commune size, with an inflection point around **50,000 residents**: above it, Jara dominates (76.9% of the population in cities over 200k); below it, Kast takes over (~60% in communes under 10k).

**Capitals vote differently than their own regions.** Jara won 10 of 16 regional capitals but only 5 of 16 regions; Kast won 4 capitals but 7 regions. Iquique, split almost evenly three ways, was the country's most competitive city.

**The Parisi phenomenon.** Votes for Franco Parisi grew 184% (899,067 → 2,550,770) and his communes won went from 6 to 64, with a 95.7% retention rate — the most loyal electoral base in the country. In 11 communes he outpolled Jara *and* Kast **combined**; there, anti-establishment politics wasn't the third force, it was the first, by an average of 8.9 points.

**Realignment was sharply uneven.** 45% of comparable communes changed winners between 2021 and 2025 — but that volatility concentrated in dense, urban regions (Valparaíso 87.1%, Metropolitana 81.6%) while Antofagasta and La Araucanía recorded zero change. Two-thirds or more of Parisi's territorial expansion came from former Kast voters, not from the left.

**Runoff projections carry a structural tilt, not a verdict.** Four transfer scenarios (see Ch. 12) place Kast ahead in every case, but the margin swings from 2.4 million votes (best case for Kast) to just 112,774 (best case for Jara) depending entirely on how Franco Parisi's electorate — the real "kingmaker" of the runoff — ultimately divides. These are modelled scenarios built on transfer assumptions, not observed results.

*A full, section-by-section breakdown with all supporting tables lives in [`Key_Findings.md`](Key_Findings.md).*

------

## 📁 Repository Structure

```text
Chilean-Presidential-Elections-2025-Analysis/
├── first_round
│ 	└── 2_2.electoral_notebooks/
│		├── README.md
│		├── requirements.txt
│		├── electoral_analysis_2025_first_round_EN.ipynb      # English version
│		└── electoral_analysis_2025_first_round_ES.ipynb      # Spanish version
└── raw/                                       (data loaded automatically)
    ├── chile_2025_first_round.csv
    ├── chile_2021_first_round.csv
    ├── communes_population_2024.csv
    └── region_dimension.csv
```



------

## 📦 Data Sources

| File                           | Description                                              | Unit    |
| :----------------------------- | :--------------------------------------------------------- | :------- |
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
cd Chilean-Presidential-Elections-2025-Analysis/first_round/2_2.electoral_notebooks
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
jupyter lab electoral_analysis_2025_first_round_EN.ipynb

# Spanish version
jupyter lab electoral_analysis_2025_first_round_ES.ipynb
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
| :---------------------------- | :----------------- |
| `Marchigüe` / `Marchigue`     | `marchihue`      |
| `Llay-Llay`                   | `llaillay`       |
| `Trehuaco`                    | `treguaco`       |
| `Cabo de Hornos(ex-Navarino)` | `cabo de hornos` |

### Electoral Realignment (`df_change`)

The 2021→2025 transition dataset is constructed by joining both electoral CSVs on `(commune_norm, region)` after normalisation (§ 14.4). A plain string join on raw commune names silently drops rows wherever encoding diverges between the two source files; the normalised key prevents that data loss.

### Map Rendering

Choropleth maps use a 3×3 `GridSpec` layout organised by macrozone:

| Grid  | Macrozone                  |
| :---- | :---------------------------- |
| (0,0) | Norte Grande               |
| (0,1) | Norte Chico                |
| (0,2) | Centro (Valparaíso y RM)   |
| (1,0) | Centro (O'Higgins y Maule) |
| (1,1) | Centro Sur                 |
| (1,2) | Sur                         |
| (2,1) | Patagonia                  |

Isla de Pascua and Juan Fernández are excluded from all maps (outlier geometry distorts regional bounding boxes). Metropolitan area facets use normalised commune keys for GeoJSON filtering to avoid encoding mismatches with raw `NOM_COM` strings.

------

## 👥 Candidates

| Candidate              | Bloc               | Colour    |
| :----------------------- | :-------------------- | :--------- |
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
