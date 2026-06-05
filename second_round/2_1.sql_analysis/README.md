# 🗳️ SQL Queries — Chilean Presidential Election 2025 (Second Round)

**¿Buscas la versión en español?** → [README.es.md](README.es.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?style=flat-square&logo=microsoft-sql-server&logoColor=white)

## 📋 Overview

This repository contains the complete SQL‑based analytical layer for the **2025 Chilean presidential runoff**. It extends the first‑round analysis by:

- Comparing participation, null/blank votes, and candidate growth between rounds.
- Measuring territorial dominance (communes & regions).
- Modelling the decisive transfer of **Parisi’s 2.55 million voters**.
- Simulating 17 scenarios of Parisi→Jara transfer rates (20% to 80%).
- Identifying ultra‑competitive communes, vote‑loss zones, and protest vote patterns.

All queries are written in **T‑SQL** (SQL Server 2012+), use **Common Table Expressions (CTEs)** and aggregate functions, and are fully documented.

---

## 🎯 Key Analytical Findings

### 1. Participation anomaly – valid votes dropped sharply

| Indicator       | First Round | Second Round   | Change                 |
| --------------- | ----------- | -------------- | ---------------------- |
| Votes cast      | 13,388,455  | 13,362,076     | –26,379                |
| **Valid votes** | 12,885,928  | **12,415,044** | **–470,884**           |
| Null votes      | 360,571     | 782,029        | **+421,458** (+116.9%) |
| Blank votes     | 141,956     | 165,003        | +23,047                |

> **Interpretation:** Despite compulsory voting, valid votes fell by almost half a million. The surge in null votes (+421k) is the main driver, not abstention.

### 2. Null vote increase was universal – strongest in mining regions

All 16 regions recorded a higher null vote share. The steepest rises occurred in the north:

| Region      | Null % 1st round | Null % 2nd round | Δ pp         |
| ----------- | ---------------- | ---------------- | ------------ |
| Antofagasta | 3.08%            | 9.04%            | **+5.96 pp** |
| Atacama     | 2.80%            | 8.05%            | **+5.25 pp** |
| Tarapacá    | 2.42%            | 7.00%            | +4.58 pp     |
| Coquimbo    | 3.10%            | 7.30%            | +4.20 pp     |

> **Interpretation:** The null vote was the preferred protest mechanism against the Jara‑Kast duopoly. Mining regions, where Parisi had excelled in the first round, led the protest.

### 3. Kast’s territorial sweep – 310 communes, all 16 regions

| Candidate | Communes won | % of communes | Regions won |
| --------- | ------------ | ------------- | ----------- |
| **Kast**  | **310**      | **89.6%**     | **16/16**   |
| Jara      | 36           | 10.4%         | 0/16        |

- Jara’s 36 communes are concentrated in only **5 regions**: Metropolitana (21), Valparaíso (5), Atacama (4), Coquimbo (3), Antofagasta (3).
- She achieved **absolute majority (>50%)** in exactly those 36 communes – nowhere else.

### 4. Kast’s strongholds are deep, not just wide

| Win intensity          | Communes | % of Kast wins | Average Kast % |
| ---------------------- | -------- | -------------- | -------------- |
| Landslide (>80%)       | 6        | 1.9%           | 86.62%         |
| Stronghold (70‑80%)    | 77       | 24.8%          | 73.54%         |
| Solid (60‑70%)         | 137      | 44.2%          | 65.11%         |
| Bare majority (50‑60%) | 90       | 29.0%          | 55.64%         |

**63.6% of all communes gave Kast >60%** – a sign of deep territorial support, not a fragmented victory.

### 5. The decisive Parisi transfer – 42% to Jara, 37.7% to Kast, 20.3% protest

Through commune‑level correlation (query 12) and scenario simulation (11a, 11b), the most probable distribution of Parisi’s 2,550,770 first‑round voters is:

| Destination               | % of Parisi voters | Estimated votes |
| ------------------------- | ------------------ | --------------- |
| Jeannette Jara            | 42.0%              | 1,071,323       |
| José Antonio Kast         | 37.7%              | 961,640         |
| Null / Blank / Abstention | 20.3%              | 517,806         |

> **Interpretation:** Jara captured the largest single share, but Kast’s share (37.7%) was critical. One in five Parisi voters chose active protest (null/blank) or abstention.

### 6. Scenario analysis – Jara needed >65% of Parisi to win

Using fixed transfers for all other eliminated candidates (Kaiser, Matthei, Artes, MEO, Mayne‑Nicholls), we swept Parisi→Jara from 20% to 80%:

| Parisi → Jara      | Jara % (sim) | Kast % (sim) | Winner (sim) | Match reality     |
| ------------------ | ------------ | ------------ | ------------ | ----------------- |
| 20%                | 37.14%       | 62.86%       | Kast         | No                |
| **42% (best fit)** | **41.69%**   | **58.31%**   | **Kast**     | **✅**             |
| 43% (closest)      | 41.89%       | 58.11%       | Kast         | ✅ (error <0.1 pp) |
| 60%                | 45.41%       | 54.59%       | Kast         | No                |
| 65%                | 46.44%       | 53.56%       | Kast         | No                |
| 80%                | 49.54%       | 50.46%       | Kast         | No                |

**Conclusion:** Even at 80% transfer, Jara would not have won. To reach a majority, she would have needed **>65% of Parisi voters** – a level that never materialised and was structurally impossible given Parisi’s anti‑establishment profile.

### 7. Kast grew in every region – strongest growth in Parisi strongholds

| Region             | Kast growth (pp) | Kast 1st round | Kast 2nd round |
| ------------------ | ---------------- | -------------- | -------------- |
| Arica y Parinacota | **+36.47**       | 20.97%         | 57.44%         |
| Tarapacá           | **+35.21**       | 21.82%         | 57.03%         |
| Antofagasta        | +33.56           | 17.27%         | 50.83%         |
| Atacama            | +31.25           | 18.04%         | 49.29%         |

Kast more than doubled his vote share in the four northern regions – the same areas where Parisi had dominated in the first round.

### 8. Protest votes did not hurt Kast

We categorised communes by the absolute increase in null+blank votes. Kast’s growth remained stable across all protest levels:

| Protest increase   | Communes | Avg Kast growth (pp) |
| ------------------ | -------- | -------------------- |
| Decrease           | 6        | +38.26               |
| Low (0–500)        | 170      | +36.73               |
| Medium (500–1,000) | 63       | +36.92               |
| High (1,000–2,000) | 44       | +34.05               |
| Very high (>2,000) | 63       | +34.49               |

**Range of average growth:** only 4 percentage points. Kast’s performance was almost independent of protest intensity.

### 9. Only one commune where Kast lost absolute votes

Out of 346 communes, Kast lost absolute votes in **just 1 commune** (Antártica, with negligible population). This confirms that his support was not only broad but also extremely stable between rounds.

---

## 🗃️  Data Model

Two tables are used, both keyed by `commune` (NVARCHAR) and `region` (NVARCHAR).

### `first_round_2025` (346 rows, 24 columns)

```text
first_round_2025
├── commune, region
├── casted_votes, blank_votes, null_votes
├── jara_votes, jara_pct
├── kast_votes, kast_pct
├── parisi_votes, parisi_pct
├── kaiser_votes, kaiser_pct
├── matthei_votes, matthei_pct
├── mayne_nicholls_votes, mayne_nicholls_pct
├── enriquez_ominami_votes, enriquez_ominami_pct
└── artes_votes, artes_pct
```

### `second_round_2025` (346 rows, 12 columns)

```text
second_round_2025
├── commune, region
├── casted_votes
├── blank_votes, blank_pct
├── null_votes, null_pct
├── jara_votes, jara_pct
└── kast_votes, kast_pct
```

All percentage columns are `DECIMAL(5,2)`. The composite key `(commune, region)` guarantees uniqueness and correct joins even when commune names repeat across regions.

---

## 🗃️ Complete Query Index

| #    | File                                                  | Objective                                        |
| ---- | ----------------------------------------------------- | ------------------------------------------------ |
| 01   | `01_comparative_voter_turnout_first_second_round.sql` | Cross‑round turnout, valid, null, blank          |
| 02   | `02_regions_null_vote_increase.sql`                   | Null vote increase by region                     |
| 03   | `03_regions_blank_vote_comparison.sql`                | Blank vote change by region                      |
| 04   | `04_second_round_winner.sql`                          | Final result & margin                            |
| 05   | `05_second_round_territorial_mapping.sql`             | Communes won per candidate                       |
| 06   | `06_second_round_regional_mapping.sql`                | Regional winners                                 |
| 07   | `07_jara_absolute_majority_communes.sql`              | Communes where Jara >50%                         |
| 08   | `08_competitive_communes_kast_margin_under_2pp.sql`   | Margins <2 percentage points                     |
| 09   | `09_communes_flipped_to_jara.sql`                     | Parisi→Jara flips                                |
| 10a  | `10a_kast_top_strongholds.sql`                        | Top 10 Kast communes                             |
| 10b  | `10b_kast_strongholds_summary.sql`                    | Kast wins by intensity                           |
| 10c  | `10c_kast_strongholds_by_region.sql`                  | Regional breakdown of Kast >60%                  |
| 11a  | `11a_parisi_vote_destination.sql`                     | Parisi transfer simulation (fixed 42% to Jara)   |
| 11b  | `11b_parisi_transfer_scenarios.sql`                   | 17‑scenario sweep (20%–80% to Jara)              |
| 12   | `12_parisi_to_kast_correlation.sql`                   | Parisi intensity vs Kast 2nd round %             |
| 13   | `13_kast_growth_by_region.sql`                        | Kast growth (absolute & pp) by region            |
| 14   | `14_kast_communes_with_vote_loss.sql`                 | Communes where Kast lost votes                   |
| 15   | `15_null_blank_impact_on_kast.sql`                    | Protest vote impact on Kast growth               |
| 16   | `16_top_parisi_communes_second_round.sql`             | Second‑round behaviour in top‑20 Parisi communes |
| 17   | `17_parisi_null_vote_correlation.sql`                 | Parisi intensity vs null vote rate in round 2    |

---

## 🚀 Setup & Usage

### Prerequisites

- SQL Server 2012 or higher (any edition)
- (Optional) Python 3.10+ with `pandas`, `pyodbc` for the ETL script.

### Option A – Python ETL (recommended – creates both tables)

```bash
cd second_round/2_1.sql_analysis/sql_server_scripts
python create_elections_database.py
```



Optional flags:

```bash
--no-execute        # Generate SQL script only, do not execute
--batch-size 1000   # Insert batch size (default: 500)
```



### Option B – Pre‑generated SQL scripts

Execute in order in SSMS / Azure Data Studio / `sqlcmd`:

```sql
USE master;
GO
CREATE DATABASE EleccionesChile2025;
GO
USE EleccionesChile2025;
GO
-- 1. Run: create_database_first_round_2025.sql
-- 2. Run: create_database_second_round_2025.sql
```



Raw file links:

- [`create_database_first_round_2025.sql`](https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/second_round/2_1.sql_analysis/sql_server_scripts/create_database_first_round_2025.sql)
- [`create_database_second_round_2025.sql`](https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/second_round/2_1.sql_analysis/sql_server_scripts/create_database_second_round_2025.sql)

### Run any analytical query

```sql
USE EleccionesChile2025;
GO
-- Copy and paste the content of any .sql file
```



------

## Project Structure

```text
second_round/
└── 2_1.sql_analysis/
    ├── README.md      (this file)
    ├── README.es.md   (Spanish translation of the readme)
    ├── 01_*.sql
    ├── ...
    ├── 10a_*.sql, 10b_*.sql, 10c_*.sql
    ├── 11a_parisi_vote_destination.sql
    ├── 11b_parisi_transfer_scenarios.sql
    ├── 12_*.sql ... 17_*.sql
    └── sql_server_scripts/
        ├── create_elections_database.py
        ├── create_database_first_round_2025.sql
        └── create_database_second_round_2025.sql
```



------

## Design & Performance Notes

| Practice                                        | Why                                                          |
| :---------------------------------------------- | :----------------------------------------------------------- |
| **CTEs (`WITH ...`)**                           | Break down complex logic (totals → ratios → categories) without nested subqueries. Dramatically improves readability and maintenance. |
| **`DECIMAL(5,2)` for percentages**              | Avoids floating‑point drift. Matches the source SERVEL format. |
| **`NULLIF(denominator,0)`**                     | Prevents division‑by‑zero for very small communes (e.g., Antártica, Ollagüe). |
| **Composite join key**                          | Joins on `commune` + `region` to avoid false matches when two regions share a commune name (e.g., “San José” appears in multiple regions). |
| **North‑to‑south regional ordering**            | `CASE` statement in `ORDER BY` assigns numeric order from Arica to Magallanes, not alphabetical – essential for geographical coherence. |
| **Simulation parameterisation**                 | The 17 scenarios in query 11b are defined as a CTE of rows, `CROSS JOIN`ed to fixed calculations. Adding a new scenario requires one extra row. |
| **Protest categorisation by absolute increase** | Using absolute increases (0–500, 500–1000, etc.) rather than percentage points is more stable across communes with very different population sizes. |

All queries are set‑based and run in <1 second on a standard SQL Server instance (346 rows).

------


## 📄 License and Attribution

- **License**: MIT
- **Author**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Web portfolio:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Email:** adroguett.consultor@gmail.com
- **Data Source**: SERVEL (public domain, official electoral authority)
- **Technologies**: SQL Server, T-SQL, Python (data extraction)
- **Analytical Approach**: Common Table Expressions (CTEs)

------

## ⭐ Acknowledgements

If this project is useful to you, please consider giving it a star on GitHub!
