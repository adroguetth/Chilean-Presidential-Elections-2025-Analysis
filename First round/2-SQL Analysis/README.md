# SQL Analysis — 2025 Chilean Presidential Election (First Round)

**¿Buscas la versión en español?** → [README.es.md](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/First%20round/2-SQL%20Analysis/README.ES.md)

## Overview

This folder contains the full SQL-based analytical layer of the project. All queries run against a single table (`resultados_elecciones`) loaded from the data extracted by the Web Scraper, and are structured using CTEs for readability, modularity, and auditability.

The analysis covers the complete universe of **346 communes** across all 16 Chilean regions, using official SERVEL data for the 2025 First Round Presidential Election.

---

## Folder Structure

```
SQL Analysis/
├── README.md                          ← this file
├── queries/
│   ├── 01_participation_stats.sql     ← national turnout metrics
│   ├── 02_national_results.sql        ← vote share by candidate
│   ├── 03_runoff_candidates.sql       ← top-2 identification (Ley 18.700)
│   ├── 04_results_by_region.sql       ← regional breakdown
│   ├── 05_top_communes.sql            ← strongest communes per candidate
│   ├── 06_competitive_communes.sql    ← tight races (<5% margin)
│   ├── 07_regional_capitals.sql       ← capital city results
│   ├── 08_urban_rural_gap.sql         ← territory vs. population paradox
│   └── 09_parisi_kingmaker.sql        ← antisystem vote & transfer scenarios
└── docs/
    └── Technical Analysis.md          ← full technical documentation
```

---

## Data Model

**Database:** SQL Server  
**Source:** SERVEL (extracted via Python/Selenium — see `../Web Scraper/`)  
**Table:** `resultados_elecciones`

```sql
resultados_elecciones (
    comuna                    VARCHAR,   -- normalised commune name
    region                    VARCHAR,   -- short region label
    artes_votos               INT,
    artes_pct                 DECIMAL,
    enriquez_ominami_votos    INT,
    enriquez_ominami_pct      DECIMAL,
    jara_votos                INT,
    jara_pct                  DECIMAL,
    kaiser_votos              INT,
    kaiser_pct                DECIMAL,
    kast_votos                INT,
    kast_pct                  DECIMAL,
    matthei_votos             INT,
    matthei_pct               DECIMAL,
    mayne_nicholls_votos      INT,
    mayne_nicholls_pct        DECIMAL,
    parisi_votos              INT,
    parisi_pct                DECIMAL,
    blanco_votos              INT,
    blanco_pct                DECIMAL,
    nulo_votos                INT,
    nulo_pct                  DECIMAL,
    emitidos_votos            INT,
    emitidos_pct              DECIMAL
)
```

> **Note:** `_votos` columns hold absolute counts; `_pct` columns hold each candidate's share as a float (0–100) pre-calculated by the scraper. Percentages in the queries are always re-derived over `total_votos_validos` to ensure analytical consistency.

---

## Query Index

Run queries in order — each builds conceptually on the previous one.

### `01_participation_stats.sql` — National Turnout Metrics
Aggregates fundamental participation metrics at the national level using a two-layer CTE: raw totals in CTE 1, pivoted indicator-value format in CTE 2. Establishes the electoral universe for all downstream analyses.

| Metric | Value |
|---|---|
| Total communes | 346 |
| Total ballots cast | 13,388,455 |
| Valid votes | 12,885,928 (96.25%) |
| Blank ballots | 141,956 (1.06%) |
| Null/spoiled ballots | 360,571 (2.69%) |

**Key technique:** `CAST(metric AS FLOAT) / total_emitidos * 100` — avoids integer division.

---

### `02_national_results.sql` — Vote Share by Candidate
Transposes the wide table into a long candidate-row format via `UNION ALL`, calculates each candidate's share over valid votes, and applies a categorical support classification (`High / Medium / Low`).

| Candidate | Vote Share | Category |
|---|---|---|
| Jeannette Jara | 26.75% | High |
| José Antonio Kast | 23.96% | High |
| Franco Parisi | 19.80% | Medium |
| Johannes Kaiser | 13.94% | Medium |
| Evelyn Matthei | 12.44% | Medium |
| Harold Mayne-Nicholls | 1.26% | Low |
| Marco Enríquez-Ominami | 1.20% | Low |
| Eduardo Artes | 0.66% | Low |

**Key technique:** `CASE WHEN pct >= 20` for support classification; thresholds at 20% and 10%.

---

### `03_runoff_candidates.sql` — Runoff Identification (Ley 18.700)
Three-CTE cascade: national aggregation → individual percentages → `ROW_NUMBER()` ranking. Filters `WHERE posicion <= 2` to identify the two candidates advancing to the runoff, and applies legal competitiveness thresholds (>50% = absolute majority, >20% = competitive).

| Candidate | % | Position | Context |
|---|---|---|---|
| Jeannette Jara | 26.75% | 1st | Competitive threshold |
| José Antonio Kast | 23.96% | 2nd | Competitive threshold |

**Key technique:** `ROW_NUMBER() OVER (ORDER BY porcentaje DESC)` for tie-safe ranking.

---

### `04_results_by_region.sql` — Regional Breakdown
Aggregates absolute and relative vote counts by region for each candidate, enabling geographic segmentation of the electoral map. Identifies dominant candidate per region.

**Key findings:**
- North (4 regions): Parisi dominance — antisystem / mining vote
- Centre-South (7 regions): Kast hegemony — rural / conservative vote  
- Centre / Patagonia (5 regions): Jara's stronghold — urban / left vote

**Key technique:** `GROUP BY region` with window function to assign regional winner.

---

### `05_top_communes.sql` — Strongest Communes per Candidate
Ranks communes by vote share for each candidate and returns the top N per candidate. Useful for identifying geographic strongholds and base territory.

**Key technique:** `ROW_NUMBER() OVER (PARTITION BY candidato ORDER BY pct DESC)`.

---

### `06_competitive_communes.sql` — Tight Races
Identifies communes where the margin between Jara and Kast is below a configurable threshold (default: <5 percentage points). These are the swing communes that determine the national result.

| Threshold | Communes |
|---|---|
| < 1,000 votes | 134 communes |
| < 5% margin | ~180 communes |

**Key technique:** `ABS(jara_pct - kast_pct) < 5` filter with absolute vote difference.

---

### `07_regional_capitals.sql` — Capital City Results
Filters for the 16 regional capital cities and analyses candidate performance in urban centres, revealing the urban-rural structural gap.

**Key findings:**
- Jara wins 10/16 capitals (62.5%) but only 5/16 regions (31.3%)
- Kast wins 4/16 capitals (25.0%) but 7/16 regions (43.8%)
- Structural paradox: territory count vs. population weight

**Key technique:** `WHERE comuna IN (...)` with curated list of regional capitals.

---

### `08_urban_rural_gap.sql` — Territory vs. Population Paradox
Quantifies the structural bias between commune count (territory) and vote volume (population). Calculates efficiency metrics: votes per commune won, territorial coverage vs. electoral weight.

**Key findings:**
- Kast: 169 communes (48.8%) → 23.96% of votes
- Jara: 105 communes (30.3%) → 26.75% of votes
- Kast requires ~334 votes/commune on average vs. ~420 for Jara

**Key technique:** `COUNT(*)` partitioned by winning candidate vs. `SUM(votos)` partitioned by same.

---

### `09_parisi_kingmaker.sql` — Antisystem Vote & Transfer Scenarios
Analyses Parisi's geographic concentration in northern communes, models three vote-transfer scenarios for the runoff (with Python simulation complement), and identifies his most vulnerable communes (<5% margin over the Jara-Kast duopoly).

**Transfer scenarios modelled:**

| Scenario | Jara % | Kast % | Net result |
|---|---|---|---|
| Optimal for Jara | 60% | 30% | Jara +2,500 net votes |
| Neutral split | 40% | 50% | Kast +800 net votes |
| Optimal for Kast | 30% | 60% | Kast +2,000 net votes |

**Key techniques:** CTE filtering on northern regions, `CORR()` equivalent for size vs. margin, Python `simular_transferencia_parisi()` for scenario modelling.

---

## Analytical Approach

All queries share a consistent design philosophy:

**CTE-first architecture** — no nested subqueries in `FROM` or `WHERE`. Each transformation step is named and isolated, making execution plans readable and results auditable.

**Valid votes as the denominator** — all candidate percentages are calculated over `SUM(emitidos_votos) - SUM(nulo_votos) - SUM(blanco_votos)`, consistent with Chilean electoral law (Ley 18.700, Art. 109).

**`CAST(AS FLOAT)` before division** — prevents integer truncation in SQL Server.

**`ROUND(..., 2)` on all percentages** — 2 decimal places throughout for consistency.

---

## Key Findings

```
1. Advanced Political Fragmentation
   No candidate exceeds 27%: Jara 26.75%, Kast 23.96%, Parisi 19.80%
   Three competing right-wing options: Kast (populist), Kaiser (libertarian), Matthei (traditional)
   49.29% of the total vote is up for grabs in the runoff

2. Structural Territory–Population Dissociation
   Kast dominates territory (48.8% of communes) but has fewer votes (23.96%)
   Jara dominates population centres (30.3% of communes) with more votes (26.75%)

3. Clear North–Centre–South Segmentation
   North (4 regions): "Parisi's Kingdom" — antisystem / mining vote
   Centre + Patagonia (5 regions): "Jara's stronghold" — urban / institutional left
   Centre-South (7 regions): "Kast's hegemony" — rural / traditional right

4. Extreme Urban–Rural Gap
   Jara wins 10/16 regional capitals (62.5%) but only 5/16 regions (31.3%)
   Kast wins 4/16 capitals (25.0%) but 7/16 regions (43.8%)

5. Quantifiable Structural Advantage for Kast in the Runoff
   Kast needs 91.8% fewer votes to recover territory than Jara
   Electoral efficiency: Kast requires ~334 votes/commune vs. ~420 for Jara

6. Parisi as Decisive Kingmaker
   Northern monopoly: 4 regions with 27–35% support
   Strategic dilemma: Alliance with Jara (more natural) vs. Kast (more potent)
   Demographic vulnerability: Strength concentrated in ~3% of the national electorate

7. Terminal Crisis of Traditional Right
   Matthei reduced to 4 communes (1.2% of territory, 12.44% of votes)
   Kast absorbs emblematic right-wing communes (Lo Barnechea, etc.)

8. Rural Structural Bias in the Electoral System
   Paradox: Kast wins more communes (169 vs. 105) but fewer votes (23.96% vs. 26.75%)
   1 rural commune (1,000 voters) = 1 urban commune (500,000 voters) in political weight

9. Extreme Competitiveness at Multiple Levels
   National gap: 2.79% (~360,000 votes)
   134 communes recoverable: <1,000-vote gap between Jara and Kast
   5 pivot regions with <3% difference determine the national outcome

10. High Procedural Legitimacy, Representation Deficit
    96.25% valid votes: Process considered legitimate by the vast majority
    Null > Blank (2.69% vs. 1.06%): Discontent is confrontational, not passive
    No candidate exceeds 27%: Winner's legitimacy is inherently limited
```

---

## Technical Stack

| Component | Detail |
|---|---|
| Database | SQL Server |
| Query style | CTE-based, modular |
| Techniques used | Aggregations, Window Functions (`ROW_NUMBER`, `RANK`), `UNION ALL` pivoting, `CASE WHEN` classification |
| Companion language | Python (scenario simulations in `09_parisi_kingmaker.sql`) |
| Extraction layer | Python + Selenium (see `../Web Scraper/`) |

---

## Author

**Alfonso Droguett** — Data Analyst

- 🔗 [LinkedIn](https://www.linkedin.com/in/adroguetth/)
- 🌐 [Portfolio](https://www.adroguett-portfolio.cl/)
- 📧 [adroguett.consultor@gmail.com](mailto:adroguett.consultor@gmail.com)
- 🐙 [GitHub](https://github.com/adroguetth/)

---

*Last updated: January 2026 (v2.0)*
