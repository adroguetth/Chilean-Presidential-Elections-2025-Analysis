#!/usr/bin/env python3

"""
Chilean Presidential Elections 2025 - Web Scraper for SERVEL Second Round Results
================================================================================
Automated scraper for extracting electoral results by commune from SERVEL (Chile).

Features:
- Extracts votes for Jara vs Kast from second round election
- Normalizes commune and region names to title format
- Generates CSV with standardized columns for SQL/Python/DAX analysis
- Automatic backup before overwriting latest results
- Firefox automation with Selenium

Output Directory Structure:
elections_archive/
├── backup/                              # Automatic backups before overwrite
├── latest_results.csv                   # Most recent results (overwritten each run)
├── results_*.csv                        # Timestamped historical files
├── *_METADATA.txt                       # Metadata for each results file
└── scraper_second_round.log             # Execution log

Columns Output:
commune,region,jara_votes,jara_pct,kast_votes,kast_pct,blank_votes,blank_pct,casted_votes,casted_pct,null_votes,null_pct

Requirements:
- Python 3.7+
- selenium
- pandas
- firefox-browser
- geckodriver

Author: Alfonso Droguett
License: MIT
Date: November 2025
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
LOG_FILE = ARCHIVE_DIR / "scraper_second_round.log"

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
class ScraperSegundaVueltaServel:
    """
    Scraper for Chilean Second Round Electoral Results from SERVEL.
    Extracts commune-level data for Jara vs Kast presidential election.
    """

    def __init__(self, headless=False, max_comunas=None):
        """
        Initialize the second round scraper.

        Args:
            headless: Run browser in headless mode
            max_comunas: Limit communes to process (None for all)
        """
        self.headless = headless
        self.max_comunas = max_comunas
        self.driver = None
        self.datos_completos = {}
        self.comunas_procesadas = 0
        self.comunas_con_error = 0

        self.MAPEO_CANDIDATOS = {
            "JEANNETTE JARA ROMAN": "jara",
            "JOSE ANTONIO KAST RIST": "kast"
        }

        self.TIEMPO_ESPERA_CARGA = 15
        self.TIEMPO_ESPERA_SELECCION = 5
        self.TIEMPO_ESPERA_DATOS = 6

    def normalizar_nombre_comuna(self, nombre_comuna):
        """Normalize commune name to title format (e.g., 'ARICA' -> 'Arica')"""
        excepciones = ['II', 'III', 'IV', 'VI', 'VII', 'X', 'XIV', 'XV', 'XVI', 'XVIII', 'XIX']

        nombre_minusculas = nombre_comuna.lower()
        palabras = nombre_minusculas.split()
        palabras_capitalizadas = []

        for palabra in palabras:
            if palabra.upper() in excepciones:
                palabras_capitalizadas.append(palabra.upper())
            else:
                if palabra.startswith('ñ'):
                    palabras_capitalizadas.append('Ñ' + palabra[1:].capitalize())
                else:
                    palabras_capitalizadas.append(palabra.capitalize())

        nombre_normalizado = ' '.join(palabras_capitalizadas)

        correcciones = {
            'De': 'de', 'Del': 'del', 'La': 'la', 'Las': 'las',
            'Los': 'los', 'Y': 'y', 'E': 'e', 'En': 'en', 'Con': 'con'
        }

        for incorrecto, correcto in correcciones.items():
            nombre_normalizado = re.sub(r'\b' + incorrecto + r'\b', correcto, nombre_normalizado)

        nombres_especificos = {
            'Arica': 'Arica', 'Iquique': 'Iquique', 'Antofagasta': 'Antofagasta',
            'Copiapó': 'Copiapó', 'La Serena': 'La Serena', 'Coquimbo': 'Coquimbo',
            'Valparaíso': 'Valparaíso', 'Viña del Mar': 'Viña del Mar',
            'Santiago': 'Santiago', 'Rancagua': 'Rancagua', 'Talca': 'Talca',
            'Chillán': 'Chillán', 'Concepción': 'Concepción', 'Temuco': 'Temuco',
            'Valdivia': 'Valdivia', 'Puerto Montt': 'Puerto Montt',
            'Coyhaique': 'Coyhaique', 'Punta Arenas': 'Punta Arenas',
            'Ñuñoa': 'Ñuñoa', 'Providencia': 'Providencia', 'Las Condes': 'Las Condes',
            'Maipú': 'Maipú', 'San Bernardo': 'San Bernardo', 'Puente Alto': 'Puente Alto'
        }

        if nombre_normalizado in nombres_especificos:
            return nombres_especificos[nombre_normalizado]

        return nombre_normalizado

    def normalizar_nombre_region(self, nombre_region):
        """Normalize region name by removing prefixes like 'De', 'Del'"""
        mapeo_especial = {
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

        if nombre_region.upper() in mapeo_especial:
            return mapeo_especial[nombre_region.upper()]

        nombre_normalizado = re.sub(
            r'^(DE|DEL|DE LA|DE LOS)\s+',
            '',
            nombre_region,
            flags=re.IGNORECASE
        )

        palabras = nombre_normalizado.split()
        if palabras:
            palabras[0] = palabras[0].capitalize()
            for i in range(1, len(palabras)):
                if palabras[i].upper() in ['Y', 'O', 'DE', 'DEL']:
                    palabras[i] = palabras[i].lower()
                else:
                    palabras[i] = palabras[i].capitalize()

        return ' '.join(palabras)

    def simplificar_nombre_candidato(self, nombre_completo):
        """Simplify candidate name for column naming (e.g., 'Jara', 'Kast')"""
        nombre_upper = nombre_completo.upper().strip()

        for nombre_largo, nombre_corto in self.MAPEO_CANDIDATOS.items():
            if nombre_upper == nombre_largo:
                return nombre_corto

        for nombre_largo, nombre_corto in self.MAPEO_CANDIDATOS.items():
            if nombre_largo in nombre_upper:
                return nombre_corto

        palabras = nombre_completo.split()
        if palabras:
            apellido = palabras[-1].lower()
            apellido = re.sub(r'[^a-zA-Z0-9_]', '_', apellido)
            return apellido

        return "candidato_desconocido"

    def inicializar_navegador(self):
        """Initialize Firefox browser with optimized options"""
        try:
            options = Options()
            if self.headless:
                options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Firefox(options=options)
            self.driver.set_page_load_timeout(60)
            logging.info("✅ Firefox browser initialized successfully")

        except Exception as e:
            logging.error(f"❌ Error initializing browser: {e}")
            raise

    def _navegar_a_servel(self):
        """Navigate to SERVEL second round voting site"""
        url = 'https://segundavotacion.servel.cl/'
        logging.info(f"🌐 Navigating to: {url}")

        self.driver.get(url)
        time.sleep(self.TIEMPO_ESPERA_CARGA)

        if "segundavotacion" not in self.driver.current_url.lower():
            raise Exception("Failed to load SERVEL second round voting page")

    def _activar_filtro_division_electoral(self):
        """Activate 'División Electoral Chile' filter"""
        try:
            boton_division = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'División Electoral Chile')]"))
            )
            boton_division.click()
            time.sleep(self.TIEMPO_ESPERA_SELECCION)
            logging.info("✅ 'División Electoral Chile' filter activated")

        except Exception as e:
            logging.error(f"❌ Could not activate filter: {e}")
            raise

    def _obtener_regiones(self):
        """Get list of all available regions"""
        try:
            select_region = self.driver.find_element(By.XPATH,
                                                     "//select[preceding-sibling::*[contains(text(), 'Región')]]")
            selector_region = Select(select_region)

            opciones_region = selector_region.options
            regiones = [opcion.text for opcion in opciones_region if opcion.text and opcion.text != "Seleccionar"]

            logging.info(f"🗺️ Found {len(regiones)} regions")
            return regiones

        except Exception as e:
            logging.error(f"❌ Error getting regions: {e}")
            return []

    def _obtener_comunas_region(self, region_nombre):
        """Get communes available for a specific region"""
        try:
            select_region = self.driver.find_element(By.XPATH,
                                                     "//select[preceding-sibling::*[contains(text(), 'Región')]]")
            selector_region = Select(select_region)
            selector_region.select_by_visible_text(region_nombre)
            time.sleep(self.TIEMPO_ESPERA_SELECCION)

            select_comuna = self.driver.find_element(By.XPATH,
                                                     "//select[preceding-sibling::*[contains(text(), 'Comuna')]]")
            selector_comuna = Select(select_comuna)

            opciones_comuna = selector_comuna.options
            comunas = [opcion.text for opcion in opciones_comuna if opcion.text and opcion.text != "Seleccionar"]

            return comunas

        except Exception as e:
            logging.error(f"❌ Error getting communes for {region_nombre}: {e}")
            return []

    def _extraer_datos_comuna(self, comuna_nombre, region_normalizada):
        """Extract electoral data for a specific commune"""
        try:
            select_comuna = self.driver.find_element(By.XPATH,
                                                     "//select[preceding-sibling::*[contains(text(), 'Comuna')]]")
            selector_comuna = Select(select_comuna)
            selector_comuna.select_by_visible_text(comuna_nombre)

            time.sleep(self.TIEMPO_ESPERA_DATOS)

            return self._procesar_tabla_resultados()

        except Exception as e:
            logging.error(f"❌ Error extracting data from {comuna_nombre}: {e}")
            return None, None

    def _procesar_tabla_resultados(self):
        """Process results table and extract candidate and totals data"""
        try:
            tabla = self._encontrar_tabla_resultados()
            if not tabla:
                return None, None

            filas = tabla.find_elements(By.TAG_NAME, "tr")
            datos_candidatos = {}
            datos_totales = {}

            for fila in filas:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 3:
                    self._procesar_fila(celdas, datos_candidatos, datos_totales)

            return datos_candidatos, datos_totales

        except Exception as e:
            logging.error(f"❌ Error processing table: {e}")
            return None, None

    def _encontrar_tabla_resultados(self):
        """Find and return the main results table"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            tablas = self.driver.find_elements(By.TAG_NAME, "table")
            for tabla in tablas:
                if tabla.is_displayed():
                    texto = tabla.text.upper()
                    if any(palabra in texto for palabra in
                           ['CANDIDATO', 'VOTOS', 'PORCENTAJE', 'PARTIDO', 'BLANCO', 'NULO', 'EMITIDO']):
                        return tabla

            return None

        except TimeoutException:
            logging.warning("⏰ Timeout waiting for results table")
            return None

    def _procesar_fila(self, celdas, datos_candidatos, datos_totales):
        """Process individual row from results table"""
        try:
            nombre = celdas[0].text.strip()
            votos_texto = celdas[1].text.strip().replace('.', '')
            porcentaje_texto = celdas[2].text.strip().replace('%', '').replace(',', '.')

            votos = int(votos_texto) if votos_texto.isdigit() else 0
            try:
                porcentaje = float(porcentaje_texto) if porcentaje_texto else 0.0
            except ValueError:
                porcentaje = 0.0

            nombre_upper = nombre.upper()

            if "BLANCO" in nombre_upper:
                datos_totales['blank'] = {'votos': votos, 'porcentaje': porcentaje}
            elif "NULO" in nombre_upper:
                datos_totales['null'] = {'votos': votos, 'porcentaje': porcentaje}
            elif "EMITIDO" in nombre_upper or "TOTAL" in nombre_upper:
                datos_totales['casted'] = {'votos': votos, 'porcentaje': porcentaje}
            elif nombre and not any(
                    palabra in nombre_upper for palabra in ['TOTAL', 'VOTACIÓN', 'CANDIDATO', 'PARTIDO']):
                nombre_simplificado = self.simplificar_nombre_candidato(nombre)
                datos_candidatos[nombre_simplificado] = {
                    'votos': votos,
                    'porcentaje': porcentaje
                }

        except (ValueError, IndexError):
            pass

    def _procesar_region(self, region_nombre):
        """Process all communes in a region"""
        region_normalizada = self.normalizar_nombre_region(region_nombre)

        logging.info(f"\n{'=' * 60}")
        logging.info(f"🏛️ PROCESSING REGION: {region_nombre} -> {region_normalizada}")
        logging.info(f"{'=' * 60}")

        comunas = self._obtener_comunas_region(region_nombre)
        if not comunas:
            logging.warning(f"⚠️ No communes found for {region_nombre}")
            return

        logging.info(f"📍 Found {len(comunas)} communes in {region_normalizada}")

        if self.max_comunas and len(comunas) > self.max_comunas:
            comunas = comunas[:self.max_comunas]
            logging.info(f"🔢 Limited to {self.max_comunas} communes for testing")

        for comuna_nombre in comunas:
            if self.max_comunas and self.comunas_procesadas >= self.max_comunas:
                logging.info("🔚 Commune limit reached")
                break

            self._procesar_comuna_individual(comuna_nombre, region_normalizada)

    def _procesar_comuna_individual(self, comuna_nombre, region_normalizada):
        """Process an individual commune"""
        try:
            comuna_normalizada = self.normalizar_nombre_comuna(comuna_nombre)
            logging.info(f"📊 Processing: {comuna_normalizada} - {region_normalizada}")

            datos_candidatos, datos_totales = self._extraer_datos_comuna(
                comuna_nombre,
                region_normalizada
            )

            if datos_candidatos:
                clave = (comuna_normalizada, region_normalizada)
                self.datos_completos[clave] = {
                    'candidatos': datos_candidatos,
                    'totales': datos_totales
                }
                self.comunas_procesadas += 1

                logging.info(
                    f"✅ {comuna_normalizada}: {len(datos_candidatos)} candidates - Total: {self.comunas_procesadas}")

                if self.comunas_procesadas % 10 == 0:
                    self._guardar_progreso_parcial()
            else:
                self.comunas_con_error += 1
                logging.warning(f"⚠️ Could not extract data for {comuna_normalizada}")

        except Exception as e:
            self.comunas_con_error += 1
            logging.error(f"❌ Error processing {comuna_nombre}: {e}")

    def _crear_dataframe_final(self):
        """
        Create final DataFrame with standardized columns in English:
        commune, region, jara_votes, jara_pct, kast_votes, kast_pct,
        blank_votes, blank_pct, casted_votes, casted_pct, null_votes, null_pct
        """
        logging.info("📈 Creating complete data matrix...")

        columns = [
            'commune', 'region',
            'jara_votes', 'jara_pct',
            'kast_votes', 'kast_pct',
            'blank_votes', 'blank_pct',
            'casted_votes', 'casted_pct',
            'null_votes', 'null_pct'
        ]

        rows = []
        for (commune, region), data in self.datos_completos.items():
            candidates = data.get('candidatos', {})
            totals = data.get('totales', {})

            row = [
                commune,
                region,
                candidates.get('jara', {}).get('votos', 0),
                candidates.get('jara', {}).get('porcentaje', 0.0),
                candidates.get('kast', {}).get('votos', 0),
                candidates.get('kast', {}).get('porcentaje', 0.0),
                totals.get('blank', {}).get('votos', 0),
                totals.get('blank', {}).get('porcentaje', 0.0),
                totals.get('casted', {}).get('votos', 0),
                totals.get('casted', {}).get('porcentaje', 0.0),
                totals.get('null', {}).get('votos', 0),
                totals.get('null', {}).get('porcentaje', 0.0),
            ]
            rows.append(row)

        df = pd.DataFrame(rows, columns=columns)
        df = df.sort_values(['region', 'commune']).reset_index(drop=True)

        return df

    def _guardar_progreso_parcial(self):
        """Save partial progress every N communes (English filenames)"""
        try:
            if not self.datos_completos:
                return

            df_parcial = self._crear_dataframe_final()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = ARCHIVE_DIR / f"partial_progress_second_round_{self.comunas_procesadas}_communes_{timestamp}.csv"

            df_parcial.to_csv(filename, index=False, encoding='utf-8')
            logging.info(f"💾 Partial progress saved: {filename}")

        except Exception as e:
            logging.error(f"❌ Error saving partial progress: {e}")

    def _guardar_resultados_finales(self, df):
        """Save final results to latest_results.csv with backup and timestamped copy"""
        try:
            create_backup_before_update()

            df.to_csv(LATEST_CSV, index=False, encoding='utf-8')
            logging.info(f"💾 Final results saved to: {LATEST_CSV}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_csv = ARCHIVE_DIR / f"results_second_round_{self.comunas_procesadas}_communes_{timestamp}.csv"
            df.to_csv(timestamped_csv, index=False, encoding='utf-8')
            logging.info(f"💾 Timestamped backup saved: {timestamped_csv}")

            self._crear_archivo_metadatos(df, timestamped_csv)
            self._mostrar_resumen_final(df)

        except Exception as e:
            logging.error(f"❌ Error saving final results: {e}")

    def _crear_archivo_metadatos(self, df, nombre_archivo_csv):
        """Create metadata file with dataset information (English)"""
        try:
            nombre_metadatos = str(nombre_archivo_csv).replace('.csv', '_METADATA.txt')

            with open(nombre_metadatos, 'w', encoding='utf-8') as f:
                f.write("METADATA - CHILEAN SECOND ROUND ELECTION MATRIX 2025\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Data file: {nombre_archivo_csv}\n")
                f.write(f"Latest file: {LATEST_CSV}\n")
                f.write(f"Generation date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total communes: {len(df)}\n")
                f.write(f"Total regions: {df['region'].nunique()}\n\n")

                f.write("SECOND ROUND CANDIDATES:\n")
                f.write("-" * 30 + "\n")
                f.write("Jeannette Jara Roman (jara)\n")
                f.write("José Antonio Kast Rist (kast)\n\n")

                f.write("COLUMN STRUCTURE:\n")
                f.write("-" * 30 + "\n")
                f.write("commune: Commune name (text)\n")
                f.write("region: Region name (text)\n")
                f.write("jara_votes: Votes for Jeannette Jara (integer)\n")
                f.write("jara_pct: Percentage for Jeannette Jara (float)\n")
                f.write("kast_votes: Votes for José Antonio Kast (integer)\n")
                f.write("kast_pct: Percentage for José Antonio Kast (float)\n")
                f.write("blank_votes: Blank votes (integer)\n")
                f.write("blank_pct: Blank votes percentage (float)\n")
                f.write("casted_votes: Total casted votes (integer)\n")
                f.write("casted_pct: Total casted votes percentage (float)\n")
                f.write("null_votes: Null votes (integer)\n")
                f.write("null_pct: Null votes percentage (float)\n\n")

                f.write("ANALYSIS USAGE:\n")
                f.write("-" * 30 + "\n")
                f.write("SQL: SELECT commune, jara_votes, kast_votes FROM table WHERE region = 'Metropolitana';\n")
                f.write("Python: df['jara_pct'].corr(df['kast_pct'])\n")
                f.write("DAX: CALCULATE(SUM([jara_votes]), [region] = 'Metropolitana')\n\n")

                f.write("WINNER CALCULATION PER COMMUNE:\n")
                f.write("-" * 30 + "\n")
                f.write("SQL: SELECT commune, CASE WHEN jara_votes > kast_votes THEN 'Jara' ELSE 'Kast' END as winner\n")
                f.write("     FROM table\n")

            logging.info(f"📄 Metadata saved: {nombre_metadatos}")

        except Exception as e:
            logging.error(f"❌ Error creating metadata: {e}")

    def _mostrar_resumen_final(self, df):
        """Display final extraction summary"""
        logging.info(f"\n{'=' * 80}")
        logging.info("🎊 SECOND ROUND EXTRACTION COMPLETED")
        logging.info(f"{'=' * 80}")
        logging.info(f"✅ Successfully processed communes: {self.comunas_procesadas}")
        logging.info(f"❌ Communes with errors: {self.comunas_con_error}")
        logging.info(f"📊 Total communes in dataset: {len(df)}")
        logging.info(f"🗺️ Regions processed: {df['region'].nunique()}")
        logging.info(f"📑 Total columns: {len(df.columns)}")
        logging.info(f"💾 Output file: {LATEST_CSV}")

        logging.info(f"\n📈 Distribution by region:")
        distribucion = df['region'].value_counts().sort_index()
        for region, count in distribucion.items():
            logging.info(f"  {region}: {count} communes")

    def ejecutar_extraccion(self):
        """Main extraction orchestrator"""
        tiempo_inicio = time.time()

        try:
            logging.info("🚀 Starting second round election data extraction...")
            self.inicializar_navegador()

            self._navegar_a_servel()
            self._activar_filtro_division_electoral()

            regiones = self._obtener_regiones()
            if not regiones:
                raise Exception("Could not obtain regions")

            for region in regiones:
                if self.max_comunas and self.comunas_procesadas >= self.max_comunas:
                    break
                self._procesar_region(region)

            df_final = self._crear_dataframe_final()
            self._guardar_resultados_finales(df_final)

            tiempo_total = time.time() - tiempo_inicio
            logging.info(f"⏱️ Total execution time: {tiempo_total / 60:.2f} minutes")

            return df_final

        except Exception as e:
            logging.error(f"💥 Critical extraction error: {e}")
            raise

        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🔚 Browser closed")


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """Main execution function with CLI argument handling"""
    parser = argparse.ArgumentParser(description='Web Scraper for Chilean Second Round Election 2025')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--comunas', type=int, help='Limit number of communes to process')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("\n" + "=" * 80)
    print("🌐 WEB SCRAPER - CHILEAN SECOND ROUND ELECTION 2025")
    print("=" * 80)
    print("📊 Automatic extraction from SERVEL")
    print("🎯 Candidates: JARA vs KAST")
    print("💾 Output: CSV ready for SQL/Python/DAX")
    print(f"📁 Output directory: {ARCHIVE_DIR}")
    print(f"💾 Latest results: {LATEST_CSV}")
    print("=" * 80)

    if args.comunas:
        print(f"🔢 Test mode: {args.comunas} communes only")
    if args.headless:
        print("👻 Running in headless mode")

    print("=" * 80)

    try:
        scraper = ScraperSegundaVueltaServel(
            headless=args.headless,
            max_comunas=args.comunas
        )

        df_resultados = scraper.ejecutar_extraccion()

        print("\n🎉 EXTRACTION COMPLETED SUCCESSFULLY")
        print(f"📁 Files generated in {ARCHIVE_DIR}:")
        print(f"   • {LATEST_CSV} (latest results)")
        print(f"   • results_second_round_*_communes_*.csv (timestamped historical)")
        print(f"   • *_METADATA.txt (metadata)")
        print(f"   • {LOG_FILE} (execution log)")
        print(f"   • backup/*.csv (automatic backups)")

        cleanup_old_backups(days=7)

        return 0

    except KeyboardInterrupt:
        print("\n⏹️ Execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
