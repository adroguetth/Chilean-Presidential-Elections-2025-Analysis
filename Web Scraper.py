"""
Web Scraper para Resultados Electorales Chilenos
Autor: Alfonso Droguett
Fecha: Noviembre 2025
Descripción: Extracción automática de resultados electorales por comuna desde SERVEL
Repositorio (Web-Scraper): https://github.com/adroguetth/Elecciones_Chile_PrimeraVuelta_2025/tree/Web-Scraper
Repositorio (Proyecto completo): https://github.com/adroguetth/Elecciones_Chile_PrimeraVuelta_2025
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

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_elecciones.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


class ScraperEleccionesServel:
    """
    Clase principal para el scraping de resultados electorales del SERVEL

    Esta clase automatiza la extracción de datos electorales por comuna
    desde el sitio web oficial del SERVEL y los estructura en un formato
    óptimo para análisis de datos.
    """

    def __init__(self, headless=False, max_comunas=None):
        """
        Inicializa el scraper

        Args:
            headless (bool): Ejecutar navegador en modo headless
            max_comunas (int): Límite de comunas a procesar (None para todas)
        """
        self.headless = headless
        self.max_comunas = max_comunas
        self.driver = None
        self.datos_completos = {}
        self.comunas_procesadas = 0
        self.comunas_con_error = 0

        # Mapeo de candidatos a nombres simplificados para columnas
        self.MAPEO_CANDIDATOS = {
            "FRANCO PARISI FERNANDEZ": "parisi",
            "JEANNETTE JARA ROMAN": "jara",
            "MARCO ANTONIO ENRIQUEZ-OMINAMI": "enriquez_ominami",
            "JOHANNES KAISER BARENTS-VON HOHENHAGEN": "kaiser",
            "JOSE ANTONIO KAST RIST": "kast",
            "EDUARDO ANTONIO ARTES BRICHETTI": "artes",
            "EVELYN MATTHEI FORNET": "matthei",
            "HAROLD MAYNE-NICHOLLS SECUL": "mayne_nicholls"
        }

        # Configuración de tiempos de espera
        self.TIEMPO_ESPERA_CARGA = 15
        self.TIEMPO_ESPERA_SELECCION = 5
        self.TIEMPO_ESPERA_DATOS = 6

    def normalizar_nombre_comuna(self, nombre_comuna):
        """
        Normaliza el nombre de la comuna a formato de título

        Args:
            nombre_comuna (str): Nombre de la comuna en mayúsculas

        Returns:
            str: Nombre de la comuna en formato título
        """
        # Lista de excepciones para palabras que deben mantenerse en mayúsculas
        excepciones = ['II', 'III', 'IV', 'VI', 'VII', 'X', 'XIV', 'XV', 'XVI', 'XVIII', 'XIX']

        # Convertir a minúsculas primero
        nombre_minusculas = nombre_comuna.lower()

        # Capitalizar cada palabra, pero manejar excepciones
        palabras = nombre_minusculas.split()
        palabras_capitalizadas = []

        for palabra in palabras:
            # Manejar casos especiales como "Ñ" y palabras con excepciones
            if palabra.upper() in excepciones:
                palabras_capitalizadas.append(palabra.upper())
            else:
                # Capitalizar palabra, manejando correctamente la "ñ"
                if palabra.startswith('ñ'):
                    palabras_capitalizadas.append('Ñ' + palabra[1:].capitalize())
                else:
                    palabras_capitalizadas.append(palabra.capitalize())

        nombre_normalizado = ' '.join(palabras_capitalizadas)

        # Correcciones específicas para nombres de comunas
        correcciones = {
            'De': 'de',
            'Del': 'del',
            'La': 'la',
            'Las': 'las',
            'Los': 'los',
            'Y': 'y',
            'E': 'e',
            'En': 'en',
            'Con': 'con'
        }

        # Aplicar correcciones de preposiciones y conjunciones
        for incorrecto, correcto in correcciones.items():
            nombre_normalizado = re.sub(r'\b' + incorrecto + r'\b', correcto, nombre_normalizado)

        # Correcciones específicas para nombres conocidos
        nombres_especificos = {
            'Arica': 'Arica',
            'Iquique': 'Iquique',
            'Antofagasta': 'Antofagasta',
            'Copiapó': 'Copiapó',
            'La Serena': 'La Serena',
            'Coquimbo': 'Coquimbo',
            'Valparaíso': 'Valparaíso',
            'Viña del Mar': 'Viña del Mar',
            'Santiago': 'Santiago',
            'Rancagua': 'Rancagua',
            'Talca': 'Talca',
            'Chillán': 'Chillán',
            'Concepción': 'Concepción',
            'Temuco': 'Temuco',
            'Valdivia': 'Valdivia',
            'Puerto Montt': 'Puerto Montt',
            'Coyhaique': 'Coyhaique',
            'Punta Arenas': 'Punta Arenas',
            'Ñuñoa': 'Ñuñoa',
            'Providencia': 'Providencia',
            'Las Condes': 'Las Condes',
            'Maipú': 'Maipú',
            'San Bernardo': 'San Bernardo',
            'Puente Alto': 'Puente Alto'
        }

        # Si el nombre está en el diccionario de específicos, usar esa versión
        if nombre_normalizado in nombres_especificos:
            return nombres_especificos[nombre_normalizado]

        return nombre_normalizado

    def normalizar_nombre_region(self, nombre_region):
        """
        Normaliza nombres de regiones removiendo prefijos como 'De', 'Del'

        Args:
            nombre_region (str): Nombre original de la región

        Returns:
            str: Nombre normalizado de la región
        """
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

        # Verificar si el nombre está en el mapeo especial
        if nombre_region.upper() in mapeo_especial:
            return mapeo_especial[nombre_region.upper()]

        # Normalización genérica: eliminar prefijos
        nombre_normalizado = re.sub(
            r'^(DE|DEL|DE LA|DE LOS)\s+',
            '',
            nombre_region,
            flags=re.IGNORECASE
        )

        # Capitalizar correctamente
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
        """
        Simplifica el nombre del candidato para uso en nombres de columnas

        Args:
            nombre_completo (str): Nombre completo del candidato

        Returns:
            str: Nombre simplificado para la columna
        """
        nombre_upper = nombre_completo.upper().strip()

        # Buscar coincidencia exacta en el diccionario
        for nombre_largo, nombre_corto in self.MAPEO_CANDIDATOS.items():
            if nombre_upper == nombre_largo:
                return nombre_corto

        # Buscar coincidencia parcial
        for nombre_largo, nombre_corto in self.MAPEO_CANDIDATOS.items():
            if nombre_largo in nombre_upper:
                return nombre_corto

        # Si no hay coincidencia, usar el primer apellido
        palabras = nombre_completo.split()
        if palabras:
            apellido = palabras[-1].lower()
            # Reemplazar caracteres especiales para compatibilidad con SQL
            apellido = re.sub(r'[^a-zA-Z0-9_]', '_', apellido)
            return apellido

        return "candidato_desconocido"

    def inicializar_navegador(self):
        """Configura e inicializa el navegador Firefox con opciones optimizadas"""
        try:
            options = Options()
            if self.headless:
                options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Firefox(options=options)
            self.driver.set_page_load_timeout(60)
            logging.info("✅ Navegador Firefox inicializado correctamente")

        except Exception as e:
            logging.error(f"❌ Error al inicializar el navegador: {e}")
            raise

    def _navegar_a_servel(self):
        """Navega al sitio de SERVEL y espera a que cargue"""
        url = 'https://elecciones.servel.cl/'
        logging.info(f"🌐 Navegando a: {url}")

        self.driver.get(url)
        time.sleep(self.TIEMPO_ESPERA_CARGA)

        # Verificar que la página cargó correctamente
        if "servel" not in self.driver.current_url.lower():
            raise Exception("No se pudo cargar la página de SERVEL")

    def _activar_filtro_division_electoral(self):
        """Activa el filtro de 'División Electoral Chile'"""
        try:
            boton_division = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'División Electoral Chile')]"))
            )
            boton_division.click()
            time.sleep(self.TIEMPO_ESPERA_SELECCION)
            logging.info("✅ Filtro 'División Electoral Chile' activado")

        except Exception as e:
            logging.error(f"❌ No se pudo activar el filtro: {e}")
            raise

    def _obtener_regiones(self):
        """Obtiene la lista de todas las regiones disponibles"""
        try:
            select_region = self.driver.find_element(By.XPATH,
                                                     "//select[preceding-sibling::*[contains(text(), 'Región')]]")
            selector_region = Select(select_region)

            opciones_region = selector_region.options
            regiones = [opcion.text for opcion in opciones_region if opcion.text and opcion.text != "Seleccionar"]

            logging.info(f"🗺️ Se encontraron {len(regiones)} regiones")
            return regiones

        except Exception as e:
            logging.error(f"❌ Error al obtener regiones: {e}")
            return []

    def _obtener_comunas_region(self, region_nombre):
        """
        Obtiene las comunas disponibles para una región específica

        Args:
            region_nombre (str): Nombre de la región

        Returns:
            list: Lista de nombres de comunas
        """
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
            logging.error(f"❌ Error al obtener comunas para {region_nombre}: {e}")
            return []

    def _extraer_datos_comuna(self, comuna_nombre, region_normalizada):
        """
        Extrae los datos electorales para una comuna específica

        Args:
            comuna_nombre (str): Nombre de la comuna
            region_normalizada (str): Nombre normalizado de la región

        Returns:
            tuple: (datos_candidatos, datos_totales) o (None, None) en caso de error
        """
        try:
            # Seleccionar la comuna
            select_comuna = self.driver.find_element(By.XPATH,
                                                     "//select[preceding-sibling::*[contains(text(), 'Comuna')]]")
            selector_comuna = Select(select_comuna)
            selector_comuna.select_by_visible_text(comuna_nombre)

            # Esperar a que carguen los datos
            time.sleep(self.TIEMPO_ESPERA_DATOS)

            return self._procesar_tabla_resultados()

        except Exception as e:
            logging.error(f"❌ Error al extraer datos de {comuna_nombre}: {e}")
            return None, None

    def _procesar_tabla_resultados(self):
        """
        Procesa la tabla de resultados y extrae datos de candidatos y totales

        Returns:
            tuple: (dict_candidatos, dict_totales)
        """
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
            logging.error(f"❌ Error al procesar tabla: {e}")
            return None, None

    def _encontrar_tabla_resultados(self):
        """Encuentra y retorna la tabla de resultados principales"""
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
            logging.warning("⏰ Timeout esperando tabla de resultados")
            return None

    def _procesar_fila(self, celdas, datos_candidatos, datos_totales):
        """
        Procesa una fila individual de la tabla de resultados

        Args:
            celdas: Lista de celdas de la fila
            datos_candidatos: Diccionario para almacenar datos de candidatos
            datos_totales: Diccionario para almacenar datos de totales
        """
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

            # Identificar tipo de dato
            if "BLANCO" in nombre_upper:
                datos_totales['blanco'] = {'votos': votos, 'porcentaje': porcentaje}
            elif "NULO" in nombre_upper:
                datos_totales['nulo'] = {'votos': votos, 'porcentaje': porcentaje}
            elif "EMITIDO" in nombre_upper or "TOTAL" in nombre_upper:
                datos_totales['emitidos'] = {'votos': votos, 'porcentaje': porcentaje}
            elif nombre and not any(
                    palabra in nombre_upper for palabra in ['TOTAL', 'VOTACIÓN', 'CANDIDATO', 'PARTIDO']):
                # Es un candidato normal
                nombre_simplificado = self.simplificar_nombre_candidato(nombre)
                datos_candidatos[nombre_simplificado] = {
                    'votos': votos,
                    'porcentaje': porcentaje
                }

        except (ValueError, IndexError) as e:
            # Error silencioso para filas individuales
            pass

    def _procesar_region(self, region_nombre):
        """
        Procesa todas las comunas de una región

        Args:
            region_nombre (str): Nombre de la región a procesar
        """
        region_normalizada = self.normalizar_nombre_region(region_nombre)

        logging.info(f"\n{'=' * 60}")
        logging.info(f"🏛️ PROCESANDO REGIÓN: {region_nombre} -> {region_normalizada}")
        logging.info(f"{'=' * 60}")

        comunas = self._obtener_comunas_region(region_nombre)
        if not comunas:
            logging.warning(f"⚠️ No se encontraron comunas para {region_nombre}")
            return

        logging.info(f"📍 Se encontraron {len(comunas)} comunas en {region_normalizada}")

        # Limitar comunas si se especificó un máximo
        if self.max_comunas and len(comunas) > self.max_comunas:
            comunas = comunas[:self.max_comunas]
            logging.info(f"🔢 Limité a {self.max_comunas} comunas para prueba")

        for comuna_nombre in comunas:
            if self.max_comunas and self.comunas_procesadas >= self.max_comunas:
                logging.info("🔚 Límite de comunas alcanzado")
                break

            self._procesar_comuna_individual(comuna_nombre, region_normalizada)

    def _procesar_comuna_individual(self, comuna_nombre, region_normalizada):
        """
        Procesa una comuna individual

        Args:
            comuna_nombre (str): Nombre de la comuna
            region_normalizada (str): Nombre normalizado de la región
        """
        try:
            # Normalizar el nombre de la comuna
            comuna_normalizada = self.normalizar_nombre_comuna(comuna_nombre)
            logging.info(f"📊 Procesando: {comuna_normalizada} - {region_normalizada}")

            datos_candidatos, datos_totales = self._extraer_datos_comuna(
                comuna_nombre,  # Usar nombre original para selección
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
                    f"✅ {comuna_normalizada}: {len(datos_candidatos)} candidatos - Total: {self.comunas_procesadas}")

                # Guardar progreso cada 10 comunas
                if self.comunas_procesadas % 10 == 0:
                    self._guardar_progreso_parcial()
            else:
                self.comunas_con_error += 1
                logging.warning(f"⚠️ No se pudieron extraer datos para {comuna_normalizada}")

        except Exception as e:
            self.comunas_con_error += 1
            logging.error(f"❌ Error procesando {comuna_nombre}: {e}")

    def _crear_dataframe_final(self):
        """
        Crea el DataFrame final con todos los datos estructurados

        Returns:
            pandas.DataFrame: DataFrame con todos los datos electorales
        """
        logging.info("📈 Creando matriz completa de datos...")

        # Recopilar todos los candidatos y totales únicos
        todos_candidatos = set()
        todos_totales = set()

        for (comuna, region), datos in self.datos_completos.items():
            if 'candidatos' in datos:
                todos_candidatos.update(datos['candidatos'].keys())
            if 'totales' in datos:
                todos_totales.update(datos['totales'].keys())

        todos_candidatos = sorted(list(todos_candidatos))
        todos_totales = sorted(list(todos_totales))

        logging.info(f"👥 Candidatos únicos: {len(todos_candidatos)}")
        logging.info(f"📋 Totales únicos: {len(todos_totales)}")

        # Crear estructura de columnas
        columnas = ['comuna', 'region']

        # Columnas para candidatos
        for candidato in todos_candidatos:
            columnas.extend([f'{candidato}_votos', f'{candidato}_pct'])

        # Columnas para totales (al final)
        for total in todos_totales:
            columnas.extend([f'{total}_votos', f'{total}_pct'])

        # Llenar datos
        filas = []
        for (comuna, region), datos in self.datos_completos.items():
            fila = [comuna, region]

            # Datos de candidatos
            for candidato in todos_candidatos:
                if 'candidatos' in datos and candidato in datos['candidatos']:
                    fila.extend([
                        datos['candidatos'][candidato]['votos'],
                        datos['candidatos'][candidato]['porcentaje']
                    ])
                else:
                    fila.extend([0, 0.0])

            # Datos de totales
            for total in todos_totales:
                if 'totales' in datos and total in datos['totales']:
                    fila.extend([
                        datos['totales'][total]['votos'],
                        datos['totales'][total]['porcentaje']
                    ])
                else:
                    fila.extend([0, 0.0])

            filas.append(fila)

        # Crear DataFrame
        df = pd.DataFrame(filas, columns=columnas)
        df = df.sort_values(['region', 'comuna']).reset_index(drop=True)

        return df

    def _guardar_progreso_parcial(self):
        """Guarda el progreso actual cada cierto número de comunas"""
        try:
            if not self.datos_completos:
                return

            df_parcial = self._crear_dataframe_final()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"progreso_parcial_{self.comunas_procesadas}_comunas_{timestamp}.csv"

            df_parcial.to_csv(nombre_archivo, index=False, encoding='utf-8')
            logging.info(f"💾 Progreso guardado: {nombre_archivo}")

        except Exception as e:
            logging.error(f"❌ Error guardando progreso parcial: {e}")

    def _guardar_resultados_finales(self, df):
        """
        Guarda los resultados finales en múltiples formatos

        Args:
            df (pandas.DataFrame): DataFrame con los datos finales
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_nombre = f"matriz_elecciones_{self.comunas_procesadas}_comunas_{timestamp}"

            # Guardar CSV
            nombre_csv = f"{base_nombre}.csv"
            df.to_csv(nombre_csv, index=False, encoding='utf-8')
            logging.info(f"💾 CSV guardado: {nombre_csv}")

            # Guardar Excel
            try:
                nombre_excel = f"{base_nombre}.xlsx"
                df.to_excel(nombre_excel, index=False)
                logging.info(f"💾 Excel guardado: {nombre_excel}")
            except Exception as e:
                logging.warning(f"⚠️ No se pudo guardar Excel: {e}")

            # Crear metadatos
            self._crear_archivo_metadatos(df, nombre_csv)

            # Mostrar resumen
            self._mostrar_resumen_final(df)

        except Exception as e:
            logging.error(f"❌ Error guardando resultados finales: {e}")

    def _crear_archivo_metadatos(self, df, nombre_archivo_csv):
        """
        Crea un archivo de metadatos con información del dataset

        Args:
            df (pandas.DataFrame): DataFrame con los datos
            nombre_archivo_csv (str): Nombre del archivo CSV principal
        """
        try:
            nombre_metadatos = nombre_archivo_csv.replace('.csv', '_METADATOS.txt')

            with open(nombre_metadatos, 'w', encoding='utf-8') as f:
                f.write("METADATOS - MATRIZ ELECTORAL CHILE\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Archivo de datos: {nombre_archivo_csv}\n")
                f.write(f"Fecha generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total comunas: {len(df)}\n")
                f.write(f"Total regiones: {df['region'].nunique()}\n\n")

                f.write("ESTRUCTURA DE COLUMNAS:\n")
                f.write("-" * 30 + "\n")
                f.write("comuna: Nombre de la comuna (texto)\n")
                f.write("region: Nombre de la región (texto)\n")

                # Columnas de candidatos
                columnas_candidatos = [col for col in df.columns
                                       if col.endswith('_votos')
                                       and not any(total in col for total in ['blanco', 'nulo', 'emitidos'])]

                for col in columnas_candidatos:
                    candidato = col.replace('_votos', '')
                    f.write(f"{candidato}_votos: Número de votos (entero)\n")
                    f.write(f"{candidato}_pct: Porcentaje de votos (decimal)\n")

                # Columnas de totales
                columnas_totales = [col for col in df.columns
                                    if col.endswith('_votos')
                                    and any(total in col for total in ['blanco', 'nulo', 'emitidos'])]

                for col in columnas_totales:
                    total = col.replace('_votos', '')
                    f.write(f"{total}_votos: Número de votos (entero)\n")
                    f.write(f"{total}_pct: Porcentaje de votos (decimal)\n")

                f.write("\nDICCIONARIO DE CANDIDATOS:\n")
                f.write("-" * 30 + "\n")
                for nombre_largo, nombre_corto in self.MAPEO_CANDIDATOS.items():
                    f.write(f"{nombre_largo} -> {nombre_corto}\n")

                f.write("\nUSO PARA ANÁLISIS:\n")
                f.write("-" * 30 + "\n")
                f.write("SQL: SELECT comuna, parisi_votos FROM tabla WHERE region = 'Metropolitana';\n")
                f.write("Python: df['parisi_pct'].corr(df['kast_pct'])\n")
                f.write("DAX: CALCULATE(SUM([parisi_votos]), [region] = 'Metropolitana')\n")

            logging.info(f"📄 Metadatos guardados: {nombre_metadatos}")

        except Exception as e:
            logging.error(f"❌ Error creando metadatos: {e}")

    def _mostrar_resumen_final(self, df):
        """Muestra un resumen final del proceso de extracción"""
        logging.info(f"\n{'=' * 80}")
        logging.info("🎊 EXTRACCIÓN COMPLETADA")
        logging.info(f"{'=' * 80}")
        logging.info(f"✅ Comunas procesadas exitosamente: {self.comunas_procesadas}")
        logging.info(f"❌ Comunas con error: {self.comunas_con_error}")
        logging.info(f"📊 Total de comunas en el dataset: {len(df)}")
        logging.info(f"🗺️ Regiones procesadas: {df['region'].nunique()}")

        # Contar candidatos y totales
        columnas_candidatos = [col for col in df.columns
                               if col.endswith('_votos')
                               and not any(total in col for total in ['blanco', 'nulo', 'emitidos'])]
        columnas_totales = [col for col in df.columns
                            if col.endswith('_votos')
                            and any(total in col for total in ['blanco', 'nulo', 'emitidos'])]

        logging.info(f"👥 Candidatos en el dataset: {len(columnas_candidatos)}")
        logging.info(f"📋 Métricas de totales: {len(columnas_totales)}")
        logging.info(f"📑 Columnas totales: {len(df.columns)}")

        # Mostrar distribución por región
        logging.info(f"\n📈 Distribución por región:")
        distribucion = df['region'].value_counts().sort_index()
        for region, count in distribucion.items():
            logging.info(f"  {region}: {count} comunas")

    def ejecutar_extraccion(self):
        """
        Método principal que ejecuta todo el proceso de extracción

        Returns:
            pandas.DataFrame: DataFrame con todos los datos extraídos
        """
        tiempo_inicio = time.time()

        try:
            logging.info("🚀 Iniciando extracción de datos electorales...")
            self.inicializar_navegador()

            # Flujo principal de extracción
            self._navegar_a_servel()
            self._activar_filtro_division_electoral()

            regiones = self._obtener_regiones()
            if not regiones:
                raise Exception("No se pudieron obtener las regiones")

            for region in regiones:
                if self.max_comunas and self.comunas_procesadas >= self.max_comunas:
                    break
                self._procesar_region(region)

            # Crear y guardar resultados
            df_final = self._crear_dataframe_final()
            self._guardar_resultados_finales(df_final)

            tiempo_total = time.time() - tiempo_inicio
            logging.info(f"⏱️ Tiempo total de ejecución: {tiempo_total / 60:.2f} minutos")

            return df_final

        except Exception as e:
            logging.error(f"💥 Error crítico en la extracción: {e}")
            raise

        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🔚 Navegador cerrado")


def main():
    """Función principal con manejo de argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Web Scraper para Resultados Electorales Chilenos')
    parser.add_argument('--headless', action='store_true', help='Ejecutar en modo headless')
    parser.add_argument('--comunas', type=int, help='Límite de comunas a procesar')
    parser.add_argument('--verbose', action='store_true', help='Logging más detallado')

    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Mostrar información inicial
    print("\n" + "=" * 80)
    print("🌐 WEB SCRAPER - RESULTADOS ELECTORALES CHILENOS")
    print("=" * 80)
    print("📊 Extracción automática desde SERVEL")
    print("💾 Datos estructurados para SQL/Python/DAX")
    print("🏙️ Nombres de comunas en formato título (Ej: 'Arica' en lugar de 'ARICA')")
    print("=" * 80)

    if args.comunas:
        print(f"🔢 Modo prueba: {args.comunas} comunas")
    if args.headless:
        print("👻 Ejecutando en modo headless")

    print("=" * 80)

    try:
        # Crear y ejecutar scraper
        scraper = ScraperEleccionesServel(
            headless=args.headless,
            max_comunas=args.comunas
        )

        df_resultados = scraper.ejecutar_extraccion()

        print("\n🎉 EXTRACCIÓN COMPLETADA EXITOSAMENTE")
        print(f"📁 Archivos generados:")
        print(f"   • CSV con {len(df_resultados)} comunas")
        print(f"   • Excel con los mismos datos")
        print(f"   • Archivo de metadatos")
        print(f"   • Log de ejecución (scraper_elecciones.log)")

        # Mostrar ejemplos de nombres normalizados
        print(f"\n🏙️ Ejemplos de nombres de comunas normalizados:")
        comunas_ejemplo = df_resultados['comuna'].head(5).tolist()
        for comuna in comunas_ejemplo:
            print(f"   • {comuna}")

        return 0

    except KeyboardInterrupt:
        print("\n⏹️ Ejecución interrumpida por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)