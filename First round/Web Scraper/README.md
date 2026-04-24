# Chilean Presidential Election Results — Web Scraper 🇨🇱

**¿Buscas la versión en español?** → [README.es.md](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/blob/main/First%20round/Web%20Scraper/README.ES.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![Web Scraping](https://img.shields.io/badge/Web-Scraping-orange?style=flat-square) ![ETL](https://img.shields.io/badge/ETL-9ecae1?style=flat-square)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Selenium](https://img.shields.io/badge/Selenium-43b02a?style=flat-square&logo=selenium&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)

## Overview

An automated web scraper that extracts commune-level results from Chile's **2025 Presidential Election First Round**, sourced directly from the official [SERVEL](https://elecciones.servel.cl/) website. The tool builds a clean, analysis-ready dataset structured for SQL, Python, and DAX workflows.

> **Part of the broader project:** [Chilean-Presidential-Elections-2025-Analysis](https://github.com/adroguetth/Elecciones_Presidenciales_Chile_2025)  
> **Branch:** `PrimeraVuelta_2025`

---

## Features

| Feature | Description |
|---|---|
| 📊 **Full coverage** | Iterates all 346 Chilean communes automatically |
| 🧹 **Clean names** | Normalises commune/region labels to Title Case with proper Spanish accentuation |
| 💾 **Checkpoint saves** | Auto-saves progress every 10 communes to prevent data loss on long runs |
| 📁 **Multi-format output** | Exports CSV, Excel, and a metadata sidecar file |
| 🔤 **SQL-safe columns** | Column naming convention compatible with SQL, Python, and DAX |
| 🛡️ **Fault tolerance** | Continues automatically after per-commune errors; failed communes are logged |
| 🕐 **Configurable timeouts** | Tune wait times to match your network conditions |

---

## Dataset Preview

### Output Schema

```
comuna, region, parisi_votos, parisi_pct, kast_votos, kast_pct, ..., blanco_votos, blanco_pct
Arica, Arica y Parinacota, 15000, 45.50, 12000, 36.36, ..., 500, 1.50
Santiago, Metropolitana, 80000, 42.30, 75000, 39.68, ..., 1200, 0.63
```

### Column Reference

| Column | Type | Description |
|---|---|---|
| `comuna` | `str` | Normalised commune name (e.g. `Viña del Mar`, not `VIÑA DEL MAR`) |
| `region` | `str` | Short region label (e.g. `Metropolitana`, not `METROPOLITANA DE SANTIAGO`) |
| `{candidate}_votos` | `int` | Absolute vote count per candidate |
| `{candidate}_pct` | `float` | Vote share as a percentage (0–100) |
| `blanco_votos` | `int` | Blank ballots |
| `blanco_pct` | `float` | Blank ballot percentage |
| `nulo_votos` | `int` | Null/spoiled ballots |
| `nulo_pct` | `float` | Null ballot percentage |
| `emitidos_votos` | `int` | Total ballots cast |
| `emitidos_pct` | `float` | Voter turnout percentage |

### Candidate Identifiers

The scraper maps each candidate's full SERVEL name to a short, SQL-safe column prefix:

```python
"FRANCO PARISI FERNANDEZ"                       → parisi
"JEANNETTE JARA ROMAN"                          → jara
"MARCO ANTONIO ENRIQUEZ-OMINAMI"                → enriquez_ominami
"JOHANNES KAISER BARENTS-VON HOHENHAGEN"        → kaiser
"JOSE ANTONIO KAST RIST"                        → kast
"EDUARDO ANTONIO ARTES BRICHETTI"               → artes
"EVELYN MATTHEI FORNET"                         → matthei
"HAROLD MAYNE-NICHOLLS SECUL"                   → mayne_nicholls
```

---

## Installation

### Prerequisites

GeckoDriver (Firefox WebDriver) must be installed and available on your `PATH`:

```bash
# Ubuntu / Debian
sudo apt-get install firefox firefox-geckodriver

# macOS
brew install firefox geckodriver

# Windows
# Download GeckoDriver from https://github.com/mozilla/geckodriver/releases
# and add it to your PATH
```

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/adroguetth/Elecciones_Presidenciales_Chile_2025.git
cd Elecciones_Presidenciales_Chile_2025

# Switch to the First Round branch
git checkout PrimeraVuelta_2025

# Navigate to the scraper directory
cd "Chilean-Presidential-Elections-2025-Analysis/First round/Web Scraper"

# Install Python dependencies
pip install -r requirements.txt
```

### `requirements.txt`

```
selenium>=4.15.0
pandas>=2.0.0
openpyxl>=3.0.0
```

---

## Usage

### Basic Run (interactive — opens a visible Firefox window)

```bash
python "Web Scraper.py"
```

### Headless Mode (recommended for servers and CI)

```bash
python "Web Scraper.py" --headless
```

### Quick Test (first N communes only)

```bash
# Process only 50 communes — useful for development and smoke-testing
python "Web Scraper.py" --comunas 50 --headless
```

### Verbose / Debug Logging

```bash
python "Web Scraper.py" --verbose --headless
```

### CLI Arguments Summary

| Argument | Description |
|---|---|
| `--headless` | Run Firefox without a visible window |
| `--comunas N` | Limit extraction to the first `N` communes |
| `--verbose` | Set logging to `DEBUG` level for detailed output |

---

## Output Files

After a successful run, the scraper writes the following files to the working directory:

| File | Format | Description |
|---|---|---|
| `election_matrix_{N}_comunas_{timestamp}.csv` | CSV | Primary output — UTF-8, analysis-ready |
| `election_matrix_{N}_comunas_{timestamp}.xlsx` | Excel | Same data in `.xlsx` for non-technical stakeholders |
| `election_matrix_{N}_comunas_{timestamp}_METADATA.txt` | Text | Schema documentation, candidate dictionary, quick-start query examples |
| `checkpoint_{N}_comunas_{timestamp}.csv` | CSV | Intermediate saves every 10 communes (auto-generated during the run) |
| `scraper_elecciones.log` | Log | Full run log with timestamps and error details |

---

## Performance Benchmarks

| Metric | Value |
|---|---|
| ⏱️ Estimated runtime | 35–60 minutes (full 346 communes) |
| 🧠 RAM usage | ~500 MB |
| 💾 Disk usage | 50–100 MB |
| 🏙️ Throughput | ~300–400 communes/hour |
| 💾 Checkpoint frequency | Every 10 communes |

---

## Architecture & Extraction Pipeline

The scraper is implemented as a single class, `ServelElectionScraper`, following a clean pipeline:

```
initialise_browser()
    └── _navigate_to_servel()
        └── _activate_electoral_division_filter()
            └── _get_regions()
                └── for each region:
                    _get_comunas_for_region()
                        └── for each commune:
                            _extract_comuna_data()
                                └── _parse_results_table()
                                    └── _parse_row()  ← candidate vs. total row classification
                            _save_partial_progress()  ← every 10 communes
_build_final_dataframe()
_save_final_results()  ← CSV + Excel + metadata
```

### Name Normalisation Logic

**Communes** go through a three-pass normalisation:
1. Lowercase → Title Case, with special handling for `ñ` and Roman numerals.
2. Spanish prepositions (`de`, `del`, `la`, `los`, `y`, etc.) are lowercased.
3. A curated dictionary guarantees correct accentuation for well-known city names (e.g. `Copiapó`, `Valparaíso`, `Ñuñoa`).

**Regions** are mapped from SERVEL's verbose administrative labels to short canonical names via an explicit lookup dictionary, with a regex-based fallback for any unlisted variants.

---

## Customisation

### Adjust Selenium Wait Times

Increase these if you see frequent `TimeoutException` errors on slow connections:

```python
self.WAIT_PAGE_LOAD = 20       # Seconds to wait for initial page load
self.WAIT_DROPDOWN_SELECT = 5  # Seconds after selecting a region/commune
self.WAIT_TABLE_RENDER = 6     # Seconds for the results table to appear
```

### Add New Candidates

Extend the candidate mapping dictionary inside `__init__`:

```python
self.CANDIDATE_MAP = {
    "NEW CANDIDATE FULL NAME": "new_candidate",
    # ... existing entries
}
```

### Limit Extraction to Specific Regions

```python
regions = self._get_regions()
regions_to_process = [r for r in regions if "METROPOLITANA" in r.upper()]
```

---

## Troubleshooting

### GeckoDriver not found

```bash
# Ubuntu / Debian
sudo apt-get install firefox-geckodriver

# Verify the installation
which geckodriver
geckodriver --version
```

### Frequent timeout errors

Increase wait times in the scraper's `__init__` (see [Customisation](#customisation)).

### Page elements not found

- Confirm that [https://elecciones.servel.cl/](https://elecciones.servel.cl/) is reachable from your machine.
- Run with `--verbose` to identify which step is failing.
- SERVEL occasionally updates its page structure; check whether dropdown XPaths or button labels have changed.

### Monitor logs in real time

```bash
tail -f scraper_elecciones.log

# Filter for errors only
grep "ERROR" scraper_elecciones.log
```

---

## Quick-Start Queries

Once extraction completes, the dataset is immediately usable:

```sql
-- SQL: Kast results in the Metropolitana region
SELECT comuna, kast_votos, kast_pct
FROM election_matrix
WHERE region = 'Metropolitana'
ORDER BY kast_pct DESC;
```

```python
# Python: correlation between two candidates across all communes
import pandas as pd
df = pd.read_csv("election_matrix_346_comunas_*.csv")
print(df['kast_pct'].corr(df['matthei_pct']))
```

```dax
// DAX: total Jara votes in a region
CALCULATE(SUM([jara_votos]), [region] = "Metropolitana")
```

---

## Use Cases

**Researchers & political scientists** — voting pattern analysis, turnout studies, geographic clustering.

**Data analysts & journalists** — BI dashboards, geographic segmentation, trend reporting.

**Developers** — electoral data APIs, predictive models, web applications.

---

## Contributing

Contributions are welcome. To get started:

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/your-feature-name`
3. **Commit** your changes: `git commit -m "Add: description of change"`
4. **Push** to your fork: `git push origin feature/your-feature-name`
5. **Open a Pull Request** against the `PrimeraVuelta_2025` branch

### Code Style Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints on all function signatures
- Include NumPy-style docstrings on public methods
- Maintain backwards compatibility
- Write tests for new functionality

---

## Legal & Ethical Notice

Data extracted using this tool is sourced from a public government website. Usage must comply with:

- SERVEL's terms of use
- Chilean data protection law (Ley 19.628)
- Responsible and ethical use of electoral information

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](https://github.com/adroguetth/Elecciones_Presidenciales_Chile_2025/blob/PrimeraVuelta_2025/LICENSE) file for full details.

---

## Author

**Alfonso Droguett**

- 🔗 [LinkedIn](https://www.linkedin.com/in/adroguetth/)
- 🌐 [Portfolio](https://www.adroguett-portfolio.cl/)
- 📧 [adroguett.consultor@gmail.com](mailto:adroguett.consultor@gmail.com)

---

_Last updated: April 2026_
