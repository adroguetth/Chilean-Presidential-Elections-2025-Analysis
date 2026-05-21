#!/usr/bin/env python3

"""
Web Scraper for Chilean Election Results - First Round 2025
===========================================================
Automated scraper for extracting first-round electoral results by commune
from the official SERVEL website, structured into a matrix ready for SQL,
Python, and DAX analysis.

Features:
- Extracts votes for 8 presidential candidates (Parisi, Jara, Enríquez-Ominami,
  Kaiser, Kast, Artes, Matthei, Mayne-Nicholls)
- Iterates over all regions and communes in Chile
- Normalizes commune and region names to title format
- Saves checkpoints every 10 communes to prevent data loss
- Automatic backup before overwriting latest results
- Exports CSV (primary), Excel (secondary), and metadata file

Output Directory Structure:
elections_archive/
├── backup/                         # Automatic backups before overwrite
├── latest_results.csv              # Most recent results (overwritten each run)
├── election_matrix_*_communes_*.csv # Timestamped historical files
├── *_METADATA.txt                  # Metadata for each results file
└── scraper_elections.log           # Execution log

Requirements:
- Python 3.7+
- selenium
- pandas
- openpyxl

Author: Alfonso Droguett
License: MIT
Date: November 2025
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd
import logging
import re
import argparse
import sys
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================
ARCHIVE_DIR = Path("elections_archive")
BACKUP_DIR = ARCHIVE_DIR / "backup"
LATEST_CSV = ARCHIVE_DIR / "latest_results.csv"
LOG_FILE = ARCHIVE_DIR / "scraper_elections.log"

for dir_path in [ARCHIVE_DIR, BACKUP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


# ============================================================================
# BACKUP UTILITIES
# ============================================================================
def create_backup_before_update():
    """Create backup of existing latest_results.csv before overwriting."""
    if not LATEST_CSV.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = BACKUP_DIR / f"backup_latest_results_{timestamp}.csv"

    try:
        shutil.copy2(LATEST_CSV, backup_filename)
        logging.info(f"   ✅ Backup created: {backup_filename.name}")
    except Exception as e:
        logging.warning(f"   ⚠️  Error creating backup: {e}")


def cleanup_old_backups(days: int = 7):
    """Remove backup files older than specified days."""
    logging.info(f"   🧹 Cleaning backups older than {days} days...")

    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0

    for backup in BACKUP_DIR.glob("backup_*.csv"):
        if backup.stat().st_mtime < cutoff_date.timestamp():
            try:
                backup.unlink()
                deleted_count += 1
            except Exception as e:
                logging.warning(f"   ⚠️  Error deleting {backup.name}: {e}")

    if deleted_count > 0:
        logging.info(f"   ✅ Deleted {deleted_count} old backup(s)")


# ============================================================================
# MAIN SCRAPER CLASS
# ============================================================================
class ServelElectionScraper:
    """
    Main scraper class for Chilean electoral results from SERVEL.
    Extracts first-round results for 8 presidential candidates.
    """

    def __init__(self, headless: bool = False, max_comunas: int | None = None):
        """
        Initialise the scraper.

        Parameters
        ----------
        headless : bool
            Run Firefox in headless mode (no visible window).
        max_comunas : int or None
            Cap the total number of comunas to process.
        """
        self.headless = headless
        self.max_comunas = max_comunas
        self.driver = None
        self.complete_data: dict = {}
        self.processed_comunas: int = 0
        self.failed_comunas: int = 0

        # Candidate mapping (8 candidates for first round)
        self.CANDIDATE_MAP: dict[str, str] = {
            "FRANCO PARISI FERNANDEZ": "parisi",
            "JEANNETTE JARA ROMAN": "jara",
            "MARCO ANTONIO ENRIQUEZ-OMINAMI": "enriquez_ominami",
            "JOHANNES KAISER BARENTS-VON HOHENHAGEN": "kaiser",
            "JOSE ANTONIO KAST RIST": "kast",
            "EDUARDO ANTONIO ARTES BRICHETTI": "artes",
            "EVELYN MATTHEI FORNET": "matthei",
            "HAROLD MAYNE-NICHOLLS SECUL": "mayne_nicholls"
        }

        # Wait times (seconds)
        self.WAIT_PAGE_LOAD: int = 15
        self.WAIT_DROPDOWN_SELECT: int = 5
        self.WAIT_TABLE_RENDER: int = 6

    # =========================================================================
    # Name normalisation helpers
    # =========================================================================

    def normalise_comuna_name(self, raw_name: str) -> str:
        """Convert raw comuna name to Title Case."""
        ROMAN_NUMERALS = {'II', 'III', 'IV', 'VI', 'VII', 'X', 'XIV', 'XV', 'XVI', 'XVIII', 'XIX'}

        words = raw_name.lower().split()
        capitalised = []

        for word in words:
            if word.upper() in ROMAN_NUMERALS:
                capitalised.append(word.upper())
            elif word.startswith('ñ'):
                capitalised.append('Ñ' + word[1:])
            else:
                capitalised.append(word.capitalize())

        normalised = ' '.join(capitalised)

        LOWERCASE_WORDS = {
            'De': 'de', 'Del': 'del', 'La': 'la', 'Las': 'las',
            'Los': 'los', 'Y': 'y', 'E': 'e', 'En': 'en', 'Con': 'con'
        }
        for wrong, right in LOWERCASE_WORDS.items():
            normalised = re.sub(r'\b' + wrong + r'\b', right, normalised)

        KNOWN_NAMES = {
            'Arica': 'Arica', 'Iquique': 'Iquique', 'Antofagasta': 'Antofagasta',
            'Copiapó': 'Copiapó', 'La Serena': 'La Serena', 'Coquimbo': 'Coquimbo',
            'Valparaíso': 'Valparaíso', 'Viña del Mar': 'Viña del Mar',
            'Santiago': 'Santiago', 'Rancagua': 'Rancagua', 'Talca': 'Talca',
            'Chillán': 'Chillán', 'Concepción': 'Concepción', 'Temuco': 'Temuco',
            'Valdivia': 'Valdivia', 'Puerto Montt': 'Puerto Montt',
            'Coyhaique': 'Coyhaique', 'Punta Arenas': 'Punta Arenas',
            'Ñuñoa': 'Ñuñoa', 'Providencia': 'Providencia',
            'Las Condes': 'Las Condes', 'Maipú': 'Maipú',
            'San Bernardo': 'San Bernardo', 'Puente Alto': 'Puente Alto'
        }
        return KNOWN_NAMES.get(normalised, normalised)

    def normalise_region_name(self, raw_name: str) -> str:
        """Convert raw region name to short, readable label."""
        REGION_MAP = {
            "METROPOLITANA DE SANTIAGO": "Metropolitana",
            "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS": "Libertador",
            "DEL MAULE": "Maule",
            "DEL BIOBIO": "Biobío",
            "DE ARICA Y PARINACOTA": "Arica y Parinacota",
            "DE TARAPACA": "Tarapacá",
            "DE ANTOFAGASTA": "Antofagasta",
            "DE ATACAMA": "Atacama",
            "DE COQUIMBO": "Coquimbo",
            "DE VALPARAISO": "Valparaíso",
            "DE ÑUBLE": "Ñuble",
            "DE LA ARAUCANIA": "La Araucanía",
            "DE LOS RIOS": "Los Ríos",
            "DE LOS LAGOS": "Los Lagos",
            "DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO": "Aysén",
            "DE MAGALLANES Y DE LA ANTARTICA CHILENA": "Magallanes"
        }

        upper = raw_name.upper()
        if upper in REGION_MAP:
            return REGION_MAP[upper]

        stripped = re.sub(
            r'^(DE|DEL|DE LA|DE LOS)\s+',
            '',
            raw_name,
            flags=re.IGNORECASE
        )

        words = stripped.split()
        if not words:
            return stripped

        words[0] = words[0].capitalize()
        for i in range(1, len(words)):
            if words[i].upper() in {'Y', 'O', 'DE', 'DEL'}:
                words[i] = words[i].lower()
            else:
                words[i] = words[i].capitalize()

        return ' '.join(words)

    def simplify_candidate_name(self, full_name: str) -> str:
        """Map candidate full name to short column prefix."""
        upper = full_name.upper().strip()

        for long_name, short_name in self.CANDIDATE_MAP.items():
            if upper == long_name:
                return short_name

        for long_name, short_name in self.CANDIDATE_MAP.items():
            if long_name in upper:
                return short_name

        words = full_name.split()
        if words:
            surname = words[-1].lower()
            return re.sub(r'[^a-zA-Z0-9_]', '_', surname)

        return "unknown_candidate"

    # =========================================================================
    # Browser setup and navigation
    # =========================================================================

    def initialise_browser(self):
        """Initialise Firefox with options tuned for scraping SERVEL."""
        try:
            options = Options()
            if self.headless:
                options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Firefox(options=options)
            self.driver.set_page_load_timeout(60)
            logging.info("✅ Firefox initialised successfully")

        except Exception as e:
            logging.error(f"❌ Failed to initialise Firefox: {e}")
            raise

    def _navigate_to_servel(self):
        """Open the SERVEL election results page."""
        url = 'https://elecciones.servel.cl/'
        logging.info(f"🌐 Navigating to: {url}")

        self.driver.get(url)
        time.sleep(self.WAIT_PAGE_LOAD)

        if "servel" not in self.driver.current_url.lower():
            raise Exception("Could not load the SERVEL page")

    def _activate_electoral_division_filter(self):
        """Click the 'División Electoral Chile' button."""
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'División Electoral Chile')]")
                )
            )
            button.click()
            time.sleep(self.WAIT_DROPDOWN_SELECT)
            logging.info("✅ 'División Electoral Chile' filter activated")

        except Exception as e:
            logging.error(f"❌ Could not activate filter: {e}")
            raise

    # =========================================================================
    # Region and comuna discovery
    # =========================================================================

    def _get_regions(self) -> list[str]:
        """Read all region names from the Región dropdown."""
        try:
            select_el = self.driver.find_element(
                By.XPATH, "//select[preceding-sibling::*[contains(text(), 'Región')]]"
            )
            selector = Select(select_el)
            regions = [
                opt.text for opt in selector.options
                if opt.text and opt.text != "Seleccionar"
            ]
            logging.info(f"🗺️ Found {len(regions)} regions")
            return regions

        except Exception as e:
            logging.error(f"❌ Failed to retrieve regions: {e}")
            return []

    def _get_comunas_for_region(self, region_name: str) -> list[str]:
        """Select a region and return its list of comunas."""
        try:
            region_select_el = self.driver.find_element(
                By.XPATH, "//select[preceding-sibling::*[contains(text(), 'Región')]]"
            )
            Select(region_select_el).select_by_visible_text(region_name)
            time.sleep(self.WAIT_DROPDOWN_SELECT)

            comuna_select_el = self.driver.find_element(
                By.XPATH, "//select[preceding-sibling::*[contains(text(), 'Comuna')]]"
            )
            comunas = [
                opt.text for opt in Select(comuna_select_el).options
                if opt.text and opt.text != "Seleccionar"
            ]
            return comunas

        except Exception as e:
            logging.error(f"❌ Failed to retrieve comunas for {region_name}: {e}")
            return []

    # =========================================================================
    # Data extraction — table parsing
    # =========================================================================

    def _extract_comuna_data(
        self, comuna_name: str, normalised_region: str
    ) -> tuple[dict | None, dict | None]:
        """Select a comuna and extract its results table."""
        try:
            comuna_select_el = self.driver.find_element(
                By.XPATH, "//select[preceding-sibling::*[contains(text(), 'Comuna')]]"
            )
            Select(comuna_select_el).select_by_visible_text(comuna_name)
            time.sleep(self.WAIT_TABLE_RENDER)

            return self._parse_results_table()

        except Exception as e:
            logging.error(f"❌ Failed to extract data for {comuna_name}: {e}")
            return None, None

    def _parse_results_table(self) -> tuple[dict | None, dict | None]:
        """Locate and parse the results table."""
        try:
            table = self._find_results_table()
            if not table:
                return None, None

            candidate_data: dict = {}
            totals_data: dict = {}

            for row in table.find_elements(By.TAG_NAME, "tr"):
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    self._parse_row(cells, candidate_data, totals_data)

            return candidate_data, totals_data

        except Exception as e:
            logging.error(f"❌ Error parsing results table: {e}")
            return None, None

    def _find_results_table(self):
        """Find table containing electoral keywords."""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            ELECTORAL_KEYWORDS = {
                'CANDIDATO', 'VOTOS', 'PORCENTAJE', 'PARTIDO',
                'BLANCO', 'NULO', 'EMITIDO'
            }
            for table in self.driver.find_elements(By.TAG_NAME, "table"):
                if table.is_displayed():
                    text_upper = table.text.upper()
                    if any(kw in text_upper for kw in ELECTORAL_KEYWORDS):
                        return table
            return None

        except TimeoutException:
            logging.warning("⏰ Timed out waiting for results table")
            return None

    def _parse_row(
        self,
        cells: list,
        candidate_data: dict,
        totals_data: dict
    ) -> None:
        """Parse a single table row."""
        try:
            name = cells[0].text.strip()
            votes_raw = cells[1].text.strip().replace('.', '')
            pct_raw = cells[2].text.strip().replace('%', '').replace(',', '.')

            votes = int(votes_raw) if votes_raw.isdigit() else 0
            try:
                percentage = float(pct_raw) if pct_raw else 0.0
            except ValueError:
                percentage = 0.0

            name_upper = name.upper()

            # English column names for totals
            if "BLANCO" in name_upper:
                totals_data['blank'] = {'votos': votes, 'porcentaje': percentage}
            elif "NULO" in name_upper:
                totals_data['null'] = {'votos': votes, 'porcentaje': percentage}
            elif "EMITIDO" in name_upper or "TOTAL" in name_upper:
                totals_data['casted'] = {'votos': votes, 'porcentaje': percentage}
            elif name and not any(
                kw in name_upper for kw in {'TOTAL', 'VOTACIÓN', 'CANDIDATO', 'PARTIDO'}
            ):
                short_name = self.simplify_candidate_name(name)
                candidate_data[short_name] = {'votos': votes, 'porcentaje': percentage}

        except (ValueError, IndexError):
            pass

    # =========================================================================
    # Region and comuna processing orchestration
    # =========================================================================

    def _process_region(self, region_name: str) -> None:
        """Iterate over all comunas in a region."""
        normalised_region = self.normalise_region_name(region_name)

        logging.info(f"\n{'=' * 60}")
        logging.info(f"🏛️ PROCESSING REGION: {region_name} → {normalised_region}")
        logging.info(f"{'=' * 60}")

        comunas = self._get_comunas_for_region(region_name)
        if not comunas:
            logging.warning(f"⚠️ No comunas found for {region_name}")
            return

        logging.info(f"📍 Found {len(comunas)} comunas in {normalised_region}")

        if self.max_comunas and len(comunas) > self.max_comunas:
            comunas = comunas[:self.max_comunas]
            logging.info(f"🔢 Capped to {self.max_comunas} comunas for testing")

        for comuna_name in comunas:
            if self.max_comunas and self.processed_comunas >= self.max_comunas:
                logging.info("🔚 Global max_comunas limit reached — stopping")
                break
            self._process_single_comuna(comuna_name, normalised_region)

    def _process_single_comuna(
        self, comuna_name: str, normalised_region: str
    ) -> None:
        """Extract and store results for one comuna."""
        try:
            normalised_comuna = self.normalise_comuna_name(comuna_name)
            logging.info(f"📊 Processing: {normalised_comuna} — {normalised_region}")

            candidate_data, totals_data = self._extract_comuna_data(
                comuna_name,
                normalised_region
            )

            if candidate_data:
                key = (normalised_comuna, normalised_region)
                self.complete_data[key] = {
                    'candidatos': candidate_data,
                    'totales': totals_data
                }
                self.processed_comunas += 1
                logging.info(
                    f"✅ {normalised_comuna}: {len(candidate_data)} candidates "
                    f"— Total processed: {self.processed_comunas}"
                )

                if self.processed_comunas % 10 == 0:
                    self._save_partial_progress()
            else:
                self.failed_comunas += 1
                logging.warning(f"⚠️ No data extracted for {normalised_comuna}")

        except Exception as e:
            self.failed_comunas += 1
            logging.error(f"❌ Error processing {comuna_name}: {e}")

    # =========================================================================
    # Output generation
    # =========================================================================

    def _build_final_dataframe(self) -> pd.DataFrame:
        """Assemble all scraped data into a wide-format DataFrame."""
        logging.info("📈 Assembling final data matrix…")

        all_candidates: set[str] = set()
        all_totals: set[str] = set()

        for (_, _), data in self.complete_data.items():
            all_candidates.update(data.get('candidatos', {}).keys())
            all_totals.update(data.get('totales', {}).keys())

        all_candidates_sorted = sorted(all_candidates)
        all_totals_sorted = sorted(all_totals)

        logging.info(f"👥 Unique candidates: {len(all_candidates_sorted)}")
        logging.info(f"📋 Unique totals: {len(all_totals_sorted)}")

        # English column names
        columns = ['commune', 'region']
        for candidate in all_candidates_sorted:
            columns += [f'{candidate}_votes', f'{candidate}_pct']
        for total in all_totals_sorted:
            columns += [f'{total}_votes', f'{total}_pct']

        rows = []
        for (comuna, region), data in self.complete_data.items():
            row = [comuna, region]

            for candidate in all_candidates_sorted:
                entry = data.get('candidatos', {}).get(candidate)
                row += [entry['votos'], entry['porcentaje']] if entry else [0, 0.0]

            for total in all_totals_sorted:
                entry = data.get('totales', {}).get(total)
                row += [entry['votos'], entry['porcentaje']] if entry else [0, 0.0]

            rows.append(row)

        df = pd.DataFrame(rows, columns=columns)
        df = df.sort_values(['region', 'commune']).reset_index(drop=True)
        return df

    def _save_partial_progress(self) -> None:
        """Save checkpoint every 10 communes."""
        try:
            if not self.complete_data:
                return

            df_partial = self._build_final_dataframe()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = ARCHIVE_DIR / f"checkpoint_{self.processed_comunas}_communes_{timestamp}.csv"

            df_partial.to_csv(filename, index=False, encoding='utf-8')
            logging.info(f"💾 Checkpoint saved: {filename}")

        except Exception as e:
            logging.error(f"❌ Failed to save checkpoint: {e}")

    def _save_final_results(self, df: pd.DataFrame) -> None:
        """Save final results to CSV, Excel, and metadata."""
        try:
            create_backup_before_update()

            df.to_csv(LATEST_CSV, index=False, encoding='utf-8')
            logging.info(f"💾 Final results saved to: {LATEST_CSV}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_csv = ARCHIVE_DIR / f"election_matrix_{self.processed_comunas}_communes_{timestamp}.csv"
            df.to_csv(timestamped_csv, index=False, encoding='utf-8')
            logging.info(f"💾 Timestamped CSV saved: {timestamped_csv}")

            try:
                excel_name = ARCHIVE_DIR / f"election_matrix_{self.processed_comunas}_communes_{timestamp}.xlsx"
                df.to_excel(excel_name, index=False)
                logging.info(f"💾 Excel saved: {excel_name}")
            except Exception as e:
                logging.warning(f"⚠️ Could not save Excel file: {e}")

            self._write_metadata_file(df, timestamped_csv)
            self._log_final_summary(df)

        except Exception as e:
            logging.error(f"❌ Error saving final results: {e}")

    def _write_metadata_file(self, df: pd.DataFrame, csv_filename: Path) -> None:
        """Write metadata file with dataset documentation."""
        try:
            meta_filename = str(csv_filename).replace('.csv', '_METADATA.txt')

            with open(meta_filename, 'w', encoding='utf-8') as f:
                f.write("METADATA — CHILE FIRST ROUND ELECTION MATRIX 2025\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Data file:        {csv_filename}\n")
                f.write(f"Latest file:      {LATEST_CSV}\n")
                f.write(f"Generated:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total communes:   {len(df)}\n")
                f.write(f"Total regions:    {df['region'].nunique()}\n\n")

                f.write("COLUMN SCHEMA\n")
                f.write("-" * 30 + "\n")
                f.write("commune : Commune name — Title Case (string)\n")
                f.write("region  : Region name — short form   (string)\n")

                candidate_vote_cols = [
                    c for c in df.columns
                    if c.endswith('_votes')
                    and not any(t in c for t in ['blank', 'null', 'casted'])
                ]
                for col in candidate_vote_cols:
                    cand = col.replace('_votes', '')
                    f.write(f"{cand}_votes : Absolute vote count (int)\n")
                    f.write(f"{cand}_pct   : Vote share 0–100   (float)\n")

                total_vote_cols = [
                    c for c in df.columns
                    if c.endswith('_votes')
                    and any(t in c for t in ['blank', 'null', 'casted'])
                ]
                for col in total_vote_cols:
                    total = col.replace('_votes', '')
                    f.write(f"{total}_votes : Absolute count (int)\n")
                    f.write(f"{total}_pct   : Percentage 0–100 (float)\n")

                f.write("\nCANDIDATE DICTIONARY\n")
                f.write("-" * 30 + "\n")
                for long_name, short_name in self.CANDIDATE_MAP.items():
                    f.write(f"{long_name} → {short_name}\n")

                f.write("\nQUICK-START QUERIES\n")
                f.write("-" * 30 + "\n")
                f.write("SQL    : SELECT commune, parisi_votes FROM table WHERE region = 'Metropolitana';\n")
                f.write("Python : df['parisi_pct'].corr(df['kast_pct'])\n")
                f.write("DAX    : CALCULATE(SUM([parisi_votes]), [region] = 'Metropolitana')\n")

            logging.info(f"📄 Metadata saved: {meta_filename}")

        except Exception as e:
            logging.error(f"❌ Failed to write metadata file: {e}")

    def _log_final_summary(self, df: pd.DataFrame) -> None:
        """Log extraction summary."""
        candidate_vote_cols = [
            c for c in df.columns
            if c.endswith('_votes')
            and not any(t in c for t in ['blank', 'null', 'casted'])
        ]
        total_vote_cols = [
            c for c in df.columns
            if c.endswith('_votes')
            and any(t in c for t in ['blank', 'null', 'casted'])
        ]

        logging.info(f"\n{'=' * 80}")
        logging.info("🎊 EXTRACTION COMPLETE — FIRST ROUND")
        logging.info(f"{'=' * 80}")
        logging.info(f"✅ Communes processed successfully : {self.processed_comunas}")
        logging.info(f"❌ Communes with errors           : {self.failed_comunas}")
        logging.info(f"📊 Communes in final dataset      : {len(df)}")
        logging.info(f"🗺️ Regions in final dataset      : {df['region'].nunique()}")
        logging.info(f"👥 Candidates in dataset         : {len(candidate_vote_cols)}")
        logging.info(f"📋 Aggregate total metrics       : {len(total_vote_cols)}")
        logging.info(f"📑 Total columns                 : {len(df.columns)}")
        logging.info(f"💾 Output file                   : {LATEST_CSV}")

        logging.info(f"\n📈 Communes per region:")
        for region, count in df['region'].value_counts().sort_index().items():
            logging.info(f"   {region}: {count} communes")

    # =========================================================================
    # Main entry point
    # =========================================================================

    def run_extraction(self) -> pd.DataFrame:
        """Execute the full extraction pipeline."""
        start_time = time.time()

        try:
            logging.info("🚀 Starting first round electoral data extraction…")
            self.initialise_browser()

            self._navigate_to_servel()
            self._activate_electoral_division_filter()

            regions = self._get_regions()
            if not regions:
                raise Exception("Could not retrieve any regions from SERVEL")

            for region in regions:
                if self.max_comunas and self.processed_comunas >= self.max_comunas:
                    break
                self._process_region(region)

            final_df = self._build_final_dataframe()
            self._save_final_results(final_df)

            elapsed_minutes = (time.time() - start_time) / 60
            logging.info(f"⏱️ Total run time: {elapsed_minutes:.2f} minutes")

            return final_df

        except Exception as e:
            logging.error(f"💥 Critical error during extraction: {e}")
            raise

        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🔚 Browser closed")


# =============================================================================
# CLI entry point
# =============================================================================

def main() -> int:
    """Parse command-line arguments and run the scraper."""
    parser = argparse.ArgumentParser(
        description='Web scraper for Chilean electoral results (SERVEL)'
    )
    parser.add_argument(
        '--headless', action='store_true',
        help='Run Firefox in headless mode (no visible window)'
    )
    parser.add_argument(
        '--comunas', type=int,
        help='Maximum number of communes to process (omit for all)'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Enable DEBUG-level logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("\n" + "=" * 80)
    print("🌐 WEB SCRAPER — CHILEAN FIRST ROUND ELECTION RESULTS (SERVEL)")
    print("=" * 80)
    print("📊 Automated extraction · structured output for SQL / Python / DAX")
    print("🎯 Candidates: PARISI · JARA · ENRÍQUEZ-OMINAMI · KAISER · KAST · ARTES · MATTHEI · MAYNE-NICHOLLS")
    print(f"📁 Output directory: {ARCHIVE_DIR}")
    print(f"💾 Latest results: {LATEST_CSV}")
    print("=" * 80)

    if args.comunas:
        print(f"🔢 Test mode: processing up to {args.comunas} communes")
    if args.headless:
        print("👻 Running in headless mode")
    print("=" * 80)

    try:
        scraper = ServelElectionScraper(
            headless=args.headless,
            max_comunas=args.comunas
        )
        df_results = scraper.run_extraction()

        print("\n🎉 EXTRACTION COMPLETED SUCCESSFULLY")
        print(f"📁 Files generated in {ARCHIVE_DIR}:")
        print(f"   • {LATEST_CSV} (latest results)")
        print(f"   • election_matrix_*_communes_*.csv (timestamped historical)")
        print(f"   • election_matrix_*_communes_*.xlsx (Excel format)")
        print(f"   • *_METADATA.txt (metadata)")
        print(f"   • {LOG_FILE} (execution log)")
        print(f"   • backup/*.csv (automatic backups)")

        print("\n🏙️ Sample of normalised commune names:")
        for comuna in df_results['commune'].head(5).tolist():
            print(f"   • {comuna}")

        cleanup_old_backups(days=7)

        return 0

    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
