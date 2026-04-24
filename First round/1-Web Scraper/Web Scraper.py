#!/usr/bin/env python3

"""
Web Scraper for Chilean Election Results
=================================================
Automatic extraction of election results by commune from the official
SERVEL website, structured into a matrix ready for SQL, Python and DAX.

Features:
- Iterates over all regions and communes available in SERVEL's dropdowns
- Normalizes commune and region names (e.g. 'ARICA' -> 'Arica', 'DEL MAULE' -> 'Maule')
- Saves checkpoints every 10 communes to avoid data loss
- Exports CSV, Excel and metadata file with candidate dictionary

Requirements:
- Python 3.7+
- selenium
- pandas
- openpyxl

Workflow:
1. Initialize Firefox browser
2. Navigate to SERVEL and activate Electoral Division filter
3. Get list of regions
4. For each region, iterate over its communes and extract the results table
5. Save final results to CSV, Excel and metadata

Author: Alfonso Droguett
Date: November 2025
Repository: https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/tree/main/First%20round/1-Web%20Scraper
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
from datetime import datetime

# ---------------------------------------------------------------------------
# Logging configuration
# Writes to both a log file (UTF-8) and stdout so progress is visible in the
# terminal during long extraction runs.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_elecciones.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


class ServelElectionScraper:
    """
    Main scraper class for Chilean electoral results from SERVEL.

    Automates Firefox to navigate the official SERVEL election results page,
    iterates over every region and comuna available in the dropdown menus,
    and builds a wide-format DataFrame where each row is one comuna and each
    column group contains votes and percentage for one candidate (or for the
    votos emitidos / votos nulos / votos blancos totals).

    Usage
    -----
    >>> scraper = ServelElectionScraper(headless=True, max_comunas=10)
    >>> df = scraper.run_extraction()
    """

    def __init__(self, headless: bool = False, max_comunas: int | None = None):
        """
        Initialise the scraper.

        Parameters
        ----------
        headless : bool
            Run Firefox in headless mode (no visible window).
            Useful for server environments or CI pipelines.
        max_comunas : int or None
            Cap the total number of comunas to process.
            Pass ``None`` (default) to process all comunas in Chile.
            Useful for quick smoke-tests during development.
        """
        self.headless = headless
        self.max_comunas = max_comunas
        self.driver = None
        self.complete_data: dict = {}   # Keyed by (comuna_name, region_name)
        self.processed_comunas: int = 0
        self.failed_comunas: int = 0

        # ---------------------------------------------------------------------------
        # Candidate name mapping
        # Maps the full name as it appears on SERVEL to a short, SQL-safe identifier
        # used as a column prefix in the output dataset.
        # ---------------------------------------------------------------------------
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

        # ---------------------------------------------------------------------------
        # Selenium wait times (seconds)
        # Tuned for SERVEL's typical response times. Increase if you observe
        # frequent TimeoutExceptions on a slow connection.
        # ---------------------------------------------------------------------------
        self.WAIT_PAGE_LOAD: int = 15       # Initial page load
        self.WAIT_DROPDOWN_SELECT: int = 5  # After selecting a region/comuna
        self.WAIT_TABLE_RENDER: int = 6     # After selecting a comuna, for the table to appear

    # =========================================================================
    # Name normalisation helpers
    # =========================================================================

    def normalise_comuna_name(self, raw_name: str) -> str:
        """
        Convert a raw comuna name from SERVEL (all-caps) to Title Case,
        respecting Spanish prepositions and Roman numerals.

        The function applies three passes:
        1. Lowercase everything, then capitalise each word.
        2. Lower-case Spanish prepositions/conjunctions (de, del, la, …).
        3. Look up the result in a curated dictionary of well-known ciudad names
           to guarantee correct accentuation (e.g. ``Valparaíso``, ``Ñuñoa``).

        Parameters
        ----------
        raw_name : str
            Comuna name as returned by SERVEL (e.g. ``"VIÑA DEL MAR"``).

        Returns
        -------
        str
            Normalised name (e.g. ``"Viña del Mar"``).
        """
        # Roman numerals that must stay uppercase (appear in some district names)
        ROMAN_NUMERALS = {'II', 'III', 'IV', 'VI', 'VII', 'X', 'XIV', 'XV', 'XVI', 'XVIII', 'XIX'}

        words = raw_name.lower().split()
        capitalised = []

        for word in words:
            if word.upper() in ROMAN_NUMERALS:
                capitalised.append(word.upper())
            elif word.startswith('ñ'):
                # Python's str.capitalize() does not handle 'ñ' → 'Ñ' correctly
                capitalised.append('Ñ' + word[1:])
            else:
                capitalised.append(word.capitalize())

        normalised = ' '.join(capitalised)

        # Lower-case Spanish prepositions and conjunctions that appear mid-name
        LOWERCASE_WORDS = {
            'De': 'de', 'Del': 'del', 'La': 'la', 'Las': 'las',
            'Los': 'los', 'Y': 'y', 'E': 'e', 'En': 'en', 'Con': 'con'
        }
        for wrong, right in LOWERCASE_WORDS.items():
            normalised = re.sub(r'\b' + wrong + r'\b', right, normalised)

        # Curated overrides for names that require specific accentuation
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
        """
        Convert a raw region name from SERVEL to a short, readable label.

        SERVEL stores region names with administrative prefixes such as
        ``"DE LOS LAGOS"`` or ``"METROPOLITANA DE SANTIAGO"``. This method
        strips those prefixes and returns the canonical short form used
        throughout the dataset (e.g. ``"Los Lagos"``, ``"Metropolitana"``).

        Parameters
        ----------
        raw_name : str
            Region name as returned by SERVEL.

        Returns
        -------
        str
            Normalised region name.
        """
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

        # Generic fallback: strip leading preposition (De / Del / De La / De Los)
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
        """
        Map a candidate's full name to its short, SQL-safe column prefix.

        The lookup order is:
        1. Exact match in ``CANDIDATE_MAP``.
        2. Partial match (full_name contains a key from the map).
        3. Fallback: use the last word (surname), strip non-alphanumeric chars.

        Parameters
        ----------
        full_name : str
            Candidate name as it appears in the SERVEL results table.

        Returns
        -------
        str
            Short identifier used as a column prefix (e.g. ``"kast"``).
        """
        upper = full_name.upper().strip()

        # Exact match
        for long_name, short_name in self.CANDIDATE_MAP.items():
            if upper == long_name:
                return short_name

        # Partial match (handles minor spelling variations on the website)
        for long_name, short_name in self.CANDIDATE_MAP.items():
            if long_name in upper:
                return short_name

        # Fallback: derive from surname, sanitise for SQL compatibility
        words = full_name.split()
        if words:
            surname = words[-1].lower()
            return re.sub(r'[^a-zA-Z0-9_]', '_', surname)

        return "unknown_candidate"

    # =========================================================================
    # Browser setup and navigation
    # =========================================================================

    def initialise_browser(self):
        """
        Initialise Firefox with options tuned for scraping SERVEL.

        Window size is set to 1920×1080 to ensure all page elements are
        rendered and visible to Selenium (some dropdowns only appear at
        wider viewports).
        """
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
        """
        Open the SERVEL election results page and wait for it to fully load.

        Raises
        ------
        Exception
            If the page URL does not contain 'servel' after loading, indicating
            a redirect or network failure.
        """
        url = 'https://elecciones.servel.cl/'
        logging.info(f"🌐 Navigating to: {url}")

        self.driver.get(url)
        time.sleep(self.WAIT_PAGE_LOAD)

        if "servel" not in self.driver.current_url.lower():
            raise Exception("Could not load the SERVEL page — unexpected URL after navigation")

    def _activate_electoral_division_filter(self):
        """
        Click the 'División Electoral Chile' button on the SERVEL results page.

        This button switches the view to the region/comuna breakdown, which is
        required before the region and comuna dropdowns become available.

        Raises
        ------
        Exception
            If the button is not found or cannot be clicked within 10 seconds.
        """
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
            logging.error(f"❌ Could not activate electoral division filter: {e}")
            raise

    # =========================================================================
    # Region and comuna discovery
    # =========================================================================

    def _get_regions(self) -> list[str]:
        """
        Read all region names from the Región dropdown on the SERVEL page.

        Returns
        -------
        list[str]
            List of region name strings, excluding the placeholder option
            ``"Seleccionar"``.
        """
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
        """
        Select a region in the dropdown and return its list of comunas.

        Parameters
        ----------
        region_name : str
            Region name exactly as it appears in the SERVEL dropdown.

        Returns
        -------
        list[str]
            List of comuna name strings for the selected region.
        """
        try:
            # Select the region first so the comuna dropdown is populated
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
        """
        Select a comuna in the dropdown and extract its results table.

        Parameters
        ----------
        comuna_name : str
            Raw comuna name as it appears in the SERVEL dropdown (used for
            selection; normalisation happens in the calling method).
        normalised_region : str
            Already-normalised region name (used only for logging).

        Returns
        -------
        tuple[dict | None, dict | None]
            ``(candidate_data, totals_data)`` where each dict maps a short
            name to ``{'votos': int, 'porcentaje': float}``.
            Returns ``(None, None)`` on error.
        """
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
        """
        Locate the results table on the current page and parse every row.

        The method scans all ``<table>`` elements for one that contains
        election-related keywords (CANDIDATO, VOTOS, BLANCO, NULO, EMITIDO)
        and delegates each row to ``_parse_row``.

        Returns
        -------
        tuple[dict, dict]
            ``(candidate_data, totals_data)``
        """
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
        """
        Wait for a ``<table>`` element containing electoral keywords to appear.

        Scans all visible tables and returns the first one whose text contains
        at least one of: CANDIDATO, VOTOS, PORCENTAJE, PARTIDO, BLANCO, NULO,
        EMITIDO.

        Returns
        -------
        WebElement or None
        """
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
        """
        Parse a single table row and update the appropriate data dictionary.

        The SERVEL results table uses three columns: name | votos | porcentaje.
        Row classification logic:
        - Row contains "BLANCO"   → votos blancos total
        - Row contains "NULO"     → votos nulos total
        - Row contains "EMITIDO" or "TOTAL" → votos emitidos total
        - Otherwise (and not a header/footer row) → individual candidate

        Thousand-separator dots are removed before parsing vote counts.
        Percentage commas are replaced with dots before float conversion.

        Parameters
        ----------
        cells : list[WebElement]
            The ``<td>`` elements of the current row (minimum 3 required).
        candidate_data : dict
            Accumulator for candidate-level results (modified in-place).
        totals_data : dict
            Accumulator for aggregate totals (modified in-place).
        """
        try:
            name = cells[0].text.strip()
            votes_raw = cells[1].text.strip().replace('.', '')   # Remove thousands separator
            pct_raw = cells[2].text.strip().replace('%', '').replace(',', '.')

            votes = int(votes_raw) if votes_raw.isdigit() else 0
            try:
                percentage = float(pct_raw) if pct_raw else 0.0
            except ValueError:
                percentage = 0.0

            name_upper = name.upper()

            if "BLANCO" in name_upper:
                totals_data['blanco'] = {'votos': votes, 'porcentaje': percentage}
            elif "NULO" in name_upper:
                totals_data['nulo'] = {'votos': votes, 'porcentaje': percentage}
            elif "EMITIDO" in name_upper or "TOTAL" in name_upper:
                totals_data['emitidos'] = {'votos': votes, 'porcentaje': percentage}
            elif name and not any(
                kw in name_upper for kw in {'TOTAL', 'VOTACIÓN', 'CANDIDATO', 'PARTIDO'}
            ):
                # Regular candidate row
                short_name = self.simplify_candidate_name(name)
                candidate_data[short_name] = {'votos': votes, 'porcentaje': percentage}

        except (ValueError, IndexError):
            # Silently skip malformed rows (headers, blank separators, etc.)
            pass

    # =========================================================================
    # Region and comuna processing orchestration
    # =========================================================================

    def _process_region(self, region_name: str) -> None:
        """
        Iterate over all comunas in a region and extract their results.

        Applies ``max_comunas`` cap if set. Logs progress at the region level.

        Parameters
        ----------
        region_name : str
            Raw region name from the SERVEL dropdown.
        """
        normalised_region = self.normalise_region_name(region_name)

        logging.info(f"\n{'=' * 60}")
        logging.info(f"🏛️ PROCESSING REGION: {region_name} → {normalised_region}")
        logging.info(f"{'=' * 60}")

        comunas = self._get_comunas_for_region(region_name)
        if not comunas:
            logging.warning(f"⚠️ No comunas found for {region_name}")
            return

        logging.info(f"📍 Found {len(comunas)} comunas in {normalised_region}")

        # Honour the max_comunas cap at region level to avoid over-fetching
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
        """
        Extract and store results for one comuna.

        On success the data is stored in ``self.complete_data`` under the key
        ``(normalised_comuna, normalised_region)``. A partial save is triggered
        every 10 successfully processed comunas to guard against data loss on
        long runs.

        Parameters
        ----------
        comuna_name : str
            Raw comuna name from the dropdown (used for Selenium selection).
        normalised_region : str
            Already-normalised region name.
        """
        try:
            normalised_comuna = self.normalise_comuna_name(comuna_name)
            logging.info(f"📊 Processing: {normalised_comuna} — {normalised_region}")

            candidate_data, totals_data = self._extract_comuna_data(
                comuna_name,       # Raw name used for dropdown selection
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

                # Periodic checkpoint every 10 comunas
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
        """
        Assemble all scraped data into a single wide-format DataFrame.

        Each row represents one comuna. Columns are:
        ``comuna``, ``region``,
        then ``{candidate}_votos`` / ``{candidate}_pct`` for every candidate
        found across all comunas, followed by the same pattern for
        votos emitidos / votos nulos / votos blancos.

        Missing values (a candidate not present in a particular comuna) are
        filled with ``0`` / ``0.0`` to keep the schema consistent.

        Returns
        -------
        pd.DataFrame
            Sorted by region then comuna.
        """
        logging.info("📈 Assembling final data matrix…")

        # Collect the full set of candidate and total keys across all comunas
        all_candidates: set[str] = set()
        all_totals: set[str] = set()

        for (_, _), data in self.complete_data.items():
            all_candidates.update(data.get('candidatos', {}).keys())
            all_totals.update(data.get('totales', {}).keys())

        all_candidates_sorted = sorted(all_candidates)
        all_totals_sorted = sorted(all_totals)

        logging.info(f"👥 Unique candidates: {len(all_candidates_sorted)}")
        logging.info(f"📋 Unique totals: {len(all_totals_sorted)}")

        # Build column list: identifiers → candidate columns → totals columns
        columns = ['comuna', 'region']
        for candidate in all_candidates_sorted:
            columns += [f'{candidate}_votos', f'{candidate}_pct']
        for total in all_totals_sorted:
            columns += [f'{total}_votos', f'{total}_pct']

        # Build row list
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
        df = df.sort_values(['region', 'comuna']).reset_index(drop=True)
        return df

    def _save_partial_progress(self) -> None:
        """
        Persist the current state to a timestamped CSV checkpoint file.

        Called automatically every 10 comunas during the main extraction loop.
        Allows recovery of partial results if the process is interrupted.
        """
        try:
            if not self.complete_data:
                return

            df_partial = self._build_final_dataframe()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"checkpoint_{self.processed_comunas}_comunas_{timestamp}.csv"

            df_partial.to_csv(filename, index=False, encoding='utf-8')
            logging.info(f"💾 Checkpoint saved: {filename}")

        except Exception as e:
            logging.error(f"❌ Failed to save checkpoint: {e}")

    def _save_final_results(self, df: pd.DataFrame) -> None:
        """
        Write the final DataFrame to CSV, Excel, and a metadata text file.

        Output files are named with the count of processed comunas and a
        timestamp to avoid accidental overwrites between runs.

        Parameters
        ----------
        df : pd.DataFrame
            The complete electoral results matrix.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"election_matrix_{self.processed_comunas}_comunas_{timestamp}"

            # CSV (primary output — lightweight, UTF-8)
            csv_name = f"{base_name}.csv"
            df.to_csv(csv_name, index=False, encoding='utf-8')
            logging.info(f"💾 CSV saved: {csv_name}")

            # Excel (secondary output — for non-technical stakeholders)
            try:
                excel_name = f"{base_name}.xlsx"
                df.to_excel(excel_name, index=False)
                logging.info(f"💾 Excel saved: {excel_name}")
            except Exception as e:
                logging.warning(f"⚠️ Could not save Excel file: {e}")

            # Metadata sidecar file
            self._write_metadata_file(df, csv_name)

            # Final summary to log
            self._log_final_summary(df)

        except Exception as e:
            logging.error(f"❌ Error saving final results: {e}")

    def _write_metadata_file(self, df: pd.DataFrame, csv_filename: str) -> None:
        """
        Write a human-readable metadata file alongside the main CSV.

        The file documents the dataset schema, candidate dictionary,
        and quick-start query examples for SQL, Python, and DAX.

        Parameters
        ----------
        df : pd.DataFrame
            The final DataFrame (used to derive column names and counts).
        csv_filename : str
            Name of the primary CSV file (used to derive the metadata filename).
        """
        try:
            meta_filename = csv_filename.replace('.csv', '_METADATA.txt')

            with open(meta_filename, 'w', encoding='utf-8') as f:
                f.write("METADATA — CHILE ELECTORAL MATRIX\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Data file:        {csv_filename}\n")
                f.write(f"Generated:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total comunas:    {len(df)}\n")
                f.write(f"Total regions:    {df['region'].nunique()}\n\n")

                f.write("COLUMN SCHEMA\n")
                f.write("-" * 30 + "\n")
                f.write("comuna  : Comuna name — Title Case (string)\n")
                f.write("region  : Region name — short form   (string)\n")

                candidate_vote_cols = [
                    c for c in df.columns
                    if c.endswith('_votos')
                    and not any(t in c for t in ['blanco', 'nulo', 'emitidos'])
                ]
                for col in candidate_vote_cols:
                    cand = col.replace('_votos', '')
                    f.write(f"{cand}_votos : Absolute vote count (int)\n")
                    f.write(f"{cand}_pct   : Vote share 0–100   (float)\n")

                total_vote_cols = [
                    c for c in df.columns
                    if c.endswith('_votos')
                    and any(t in c for t in ['blanco', 'nulo', 'emitidos'])
                ]
                for col in total_vote_cols:
                    total = col.replace('_votos', '')
                    f.write(f"{total}_votos : Absolute count (int)\n")
                    f.write(f"{total}_pct   : Percentage 0–100 (float)\n")

                f.write("\nCANDIDATE DICTIONARY\n")
                f.write("-" * 30 + "\n")
                for long_name, short_name in self.CANDIDATE_MAP.items():
                    f.write(f"{long_name} → {short_name}\n")

                f.write("\nQUICK-START QUERIES\n")
                f.write("-" * 30 + "\n")
                f.write("SQL    : SELECT comuna, parisi_votos FROM tabla WHERE region = 'Metropolitana';\n")
                f.write("Python : df['parisi_pct'].corr(df['kast_pct'])\n")
                f.write("DAX    : CALCULATE(SUM([parisi_votos]), [region] = 'Metropolitana')\n")

            logging.info(f"📄 Metadata saved: {meta_filename}")

        except Exception as e:
            logging.error(f"❌ Failed to write metadata file: {e}")

    def _log_final_summary(self, df: pd.DataFrame) -> None:
        """Log a concise extraction summary once all data has been saved."""
        candidate_vote_cols = [
            c for c in df.columns
            if c.endswith('_votos')
            and not any(t in c for t in ['blanco', 'nulo', 'emitidos'])
        ]
        total_vote_cols = [
            c for c in df.columns
            if c.endswith('_votos')
            and any(t in c for t in ['blanco', 'nulo', 'emitidos'])
        ]

        logging.info(f"\n{'=' * 80}")
        logging.info("🎊 EXTRACTION COMPLETE")
        logging.info(f"{'=' * 80}")
        logging.info(f"✅ Comunas processed successfully : {self.processed_comunas}")
        logging.info(f"❌ Comunas with errors           : {self.failed_comunas}")
        logging.info(f"📊 Comunas in final dataset      : {len(df)}")
        logging.info(f"🗺️ Regions in final dataset      : {df['region'].nunique()}")
        logging.info(f"👥 Candidates in dataset         : {len(candidate_vote_cols)}")
        logging.info(f"📋 Aggregate total metrics       : {len(total_vote_cols)}")
        logging.info(f"📑 Total columns                 : {len(df.columns)}")

        logging.info(f"\n📈 Comunas per region:")
        for region, count in df['region'].value_counts().sort_index().items():
            logging.info(f"   {region}: {count} comunas")

    # =========================================================================
    # Main entry point
    # =========================================================================

    def run_extraction(self) -> pd.DataFrame:
        """
        Execute the full extraction pipeline from start to finish.

        Steps
        -----
        1. Initialise Firefox.
        2. Navigate to SERVEL and activate the electoral division filter.
        3. Enumerate all regions.
        4. For each region, enumerate and process all comunas.
        5. Build the final DataFrame and save outputs (CSV, Excel, metadata).
        6. Close the browser.

        Returns
        -------
        pd.DataFrame
            The complete electoral results matrix.

        Raises
        ------
        Exception
            Re-raises any unrecoverable error after logging it.
        """
        start_time = time.time()

        try:
            logging.info("🚀 Starting electoral data extraction…")
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
    """
    Parse command-line arguments and run the scraper.

    Arguments
    ---------
    --headless
        Run Firefox without a visible window.
    --comunas N
        Limit extraction to the first N comunas (useful for quick tests).
    --verbose
        Set logging level to DEBUG for detailed output.

    Returns
    -------
    int
        Exit code: 0 on success, 1 on error or user interruption.
    """
    parser = argparse.ArgumentParser(
        description='Web scraper for Chilean electoral results (SERVEL)'
    )
    parser.add_argument(
        '--headless', action='store_true',
        help='Run Firefox in headless mode (no visible window)'
    )
    parser.add_argument(
        '--comunas', type=int,
        help='Maximum number of comunas to process (omit for all)'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Enable DEBUG-level logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("\n" + "=" * 80)
    print("🌐 WEB SCRAPER — CHILEAN ELECTORAL RESULTS (SERVEL)")
    print("=" * 80)
    print("📊 Automated extraction · structured output for SQL / Python / DAX")
    print("🏙️ Comuna names normalised to Title Case (e.g. 'Arica' not 'ARICA')")
    print("=" * 80)

    if args.comunas:
        print(f"🔢 Test mode: processing up to {args.comunas} comunas")
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
        print("📁 Files generated:")
        print(f"   • CSV  — {len(df_results)} comunas")
        print("   • Excel — same data, .xlsx format")
        print("   • Metadata sidecar — schema + candidate dictionary")
        print("   • Log file — scraper_elecciones.log")

        print("\n🏙️ Sample of normalised comuna names:")
        for comuna in df_results['comuna'].head(5).tolist():
            print(f"   • {comuna}")

        return 0

    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
