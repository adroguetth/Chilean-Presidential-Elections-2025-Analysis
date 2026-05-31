# 🗃️ SQL Queries — Chilean Presidential Election 2025 (First Round)
**¿Buscas la versión en español?** → [README.es.md](README.es.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?style=flat-square&logo=microsoft-sql-server&logoColor=white)

## 📋 Overview

This folder contains **9 analytical SQL queries** for the first round of the Chilean presidential election 2025. Designed for **SQL Server 2012+**, they replicate and validate the key findings from the main [analysis notebook](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/tree/main/first_round/2_2.notebooks).

All queries reference the table `first_round_2025`, created from the official CSV using the conversion script [`create_elections_database.py`](https://sql_server_scripts/create_elections_database.py).

You can obtain the database in two ways:

- **Download the pre‑generated script:** [`create_database.sql`](https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/first_round/2_1.sql_queries/sql_server_scripts/create_database.sql)
- **Generate it yourself** using the Python script (see below).

------

## 🎯 Analysis Objectives

| Objective                   | Description                                                  |
| :-------------------------- | :----------------------------------------------------------- |
| **National Distribution**   | Analyze vote distribution by candidate at national level     |
| **Electoral Strongholds**   | Identify communes with highest support per candidate         |
| **Competitiveness**         | Detect communes with narrow margins between candidates       |
| **Regional Patterns**       | Examine trends by region and regional capitals               |
| **Anti‑Establishment Vote** | Investigate protest voting against the political duopoly     |
| **Runoff Strategy**         | Identify strategic opportunities for the second round campaign |

------

## 📁 Query Index

| #     | Query                        | Description                                                 |
| :---- | :--------------------------- | :---------------------------------------------------------- |
| **1** | `01_overall_turnout.sql`     | Voter turnout: valid, blank, null votes                     |
| **2** | `02_national_results.sql`    | Vote shares for all 8 candidates                            |
| **3** | `03_runoff_candidates.sql`   | Identifies Jara and Kast as runoff finalists                |
| **4** | `04_top_10_communes.sql`     | Highest vote shares per candidate                           |
| **5** | `05_territorial_mapping.sql` | Communes won per candidate                                  |
| **6** | `06_results_by_region.sql`   | Regional averages and winners (north–south order)           |
| **7** | `07_regional_capitals.sql`   | Results in Chile's 16 regional capitals (north–south order) |
| **8** | `08_flippable_communes.sql`  | Communes with margin < 1,000 votes (runoff battlegrounds)   |
| **9** | `09_anti_establishment.sql`  | Parisi vs. Jara+Kast duopoly                                |

------

## 🗃️ Data Model

| Element        | Description                         |
| :------------- | :---------------------------------- |
| **Source**     | SERVEL (Electoral Service of Chile) |
| **Extraction** | Python with Selenium                |
| **Coverage**   | 346 communes nationwide             |

### Table Structure (`first_round_2025`)

```text
first_round_2025
├── commune (NVARCHAR)
├── region (NVARCHAR)
├── casted_votes (INT)
├── blank_votes (INT)
├── null_votes (INT)
├── jara_votes, jara_pct (INT, DECIMAL)
├── kast_votes, kast_pct (INT, DECIMAL)
├── parisi_votes, parisi_pct (INT, DECIMAL)
├── kaiser_votes, kaiser_pct (INT, DECIMAL)
├── matthei_votes, matthei_pct (INT, DECIMAL)
├── mayne_nicholls_votes, mayne_nicholls_pct (INT, DECIMAL)
├── enriquez_ominami_votes, enriquez_ominami_pct (INT, DECIMAL)
├── artes_votes, artes_pct (INT, DECIMAL)
└── [remaining percentage columns]
```



------

## 📊 Key Findings by Query

Based on the actual data (`first_round_2025`, 346 communes, 24 columns):

| Query                      | Key Finding                                                  |
| :------------------------- | :----------------------------------------------------------- |
| **1 – Turnout**            | 13.39M votes cast, 2.69% null, 1.06% blank. Valid votes: 96.25% |
| **2 – National**           | Jara 26.74%, Kast 23.95%, Parisi 19.80%, Kaiser 13.94%, Matthei 12.44%, others <2% |
| **3 – Runoff**             | Jara (1st) and Kast (2nd) advance to second round            |
| **4 – Top 10**             | Parisi dominates northern communes (Ollagüe 58.2%, Maria Elena 45.9%). Jara strongest in RM (Pedro Aguirre Cerda 41.9%). Kast strongest in rural areas (Lumaco 46.2%) |
| **5 – Territorial**        | Kast wins 169 communes (48.8%), Jara 105 (30.3%), Parisi 64 (18.5%), Kaiser 4, Matthei 2 |
| **6 – Regional**           | Parisi wins 5 northern regions, Jara wins RM/Valparaíso/Aysén/Magallanes, Kast wins centre‑south (Ñuble to Los Lagos) |
| **7 – Capitals**           | Jara wins 10 capitals (Santiago, Valparaíso, Concepción…), Kast wins 4 (Chillán, Temuco, Puerto Montt, Coyhaique), Parisi wins 2 (Arica, Antofagasta) |
| **8 – Flippable**          | 31 communes with margin <1,000 votes; Jara would need 19,853 votes to flip them, Kast 15,224 |
| **9 – Anti‑establishment** | Parisi outperforms Jara+Kast in 11 northern communes (Ollagüe +29.97%, Maria Elena +8.44%, Calama +1.01%) |

------

## 🚀 Quick Start

### 1. Create the database and table

**Option A – Download pre‑generated script:**

```bash
curl -O https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/first_round/2_1.sql_queries/sql_server_scripts/create_database.sql
```

Then execute it in SSMS or `sqlcmd`.



**Option B – Generate the script yourself:**

Navigate to `sql_server_scripts/` and run:

```bash
cd sql_server_scripts/

# Normal execution (tries direct SQL Server connection)
python create_elections_database.py

# Only generate the SQL script (do not execute)
python create_elections_database.py --no-execute

# Change batch size (default 500)
python create_elections_database.py --batch-size 1000

# Change table name
python create_elections_database.py --table "first_round_results"
```



### 2. Run a query

```sql
USE EleccionesChile2025;
GO

-- Example: Runoff candidates
SELECT candidato, porcentaje
FROM (
    -- Copy query from 03_runoff_candidates.sql
) AS resultados;
```



------

## 🧠 Design Notes

| Feature                | Description                                                  |
| :--------------------- | :----------------------------------------------------------- |
| **Geographic order**   | Queries 6 and 7 use a `CASE` statement to order regions **north to south** (Arica → Magallanes) |
| **Precision**          | All percentages are formatted as `DECIMAL(5,2)` (e.g., `35.00`, `27.68`) |
| **Reusable structure** | CTEs are used to break down complex logic (e.g., `WITH resultados_region`, `ganadores_region`) |
| **Runoff analysis**    | Query 8 identifies flippable communes with margin < 1,000 votes for strategic campaign planning |

------

## 🛠️ Tech Stack

| Technology              | Purpose                             |
| :---------------------- | :---------------------------------- |
| **Database**            | SQL Server (T-SQL)                  |
| **Analytical Approach** | Common Table Expressions (CTEs)     |
| **Metrics**             | Spatial and percentage aggregations |
| **Language**            | T-SQL (SQL Server 2012+)            |

------

## 📂 File Structure

```text
2_1.sql_queries/
├── README.md
├── 01_overall_turnout.sql
├── 02_national_results.sql
├── 03_runoff_candidates.sql
├── 04_top_10_communes.sql
├── 05_territorial_mapping.sql
├── 06_results_by_region.sql
├── 07_regional_capitals.sql
├── 08_flippable_communes.sql
├── 09_anti_establishment.sql
└── sql_server_scripts/
    ├── create_elections_database.py
    └── create_database.sql
```


------

## 📄 License and Attribution

- **License**: MIT
- **Author**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Web portfolio:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Email:** adroguett.consultor@gmail.com
- **Data Source**: SERVEL (public domain, official electoral authority)
- **Technologies**: SQL Server (T-SQL)
- **Analytical Approach**: Common Table Expressions (CTEs)

------

## ⭐ Acknowledgements

If this project is useful to you, please consider giving it a star on GitHub!
