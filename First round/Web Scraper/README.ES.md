# Resultados Electorales Presidenciales Chile — Web Scraper 🇨🇱

![Licencia](https://img.shields.io/badge/License-MIT-yellow)
![Web Scraping](https://img.shields.io/badge/Web-Scraping-orange)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=fff)](#)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=fff)](#)

## Descripción General

Scraper web automatizado que extrae resultados a nivel de comuna de la **Primera Vuelta Presidencial Chile 2025**, obtenidos directamente desde el sitio oficial del [SERVEL](https://elecciones.servel.cl/). La herramienta construye un dataset limpio y listo para análisis, estructurado para flujos de trabajo en SQL, Python y DAX.

> **Proyecto principal:** [Chilean-Presidential-Elections-2025-Analysis](https://github.com/adroguetth/Elecciones_Presidenciales_Chile_2025)  
> **Rama:** `PrimeraVuelta_2025`

---

## Características

| Característica | Descripción |
|---|---|
| 📊 **Cobertura completa** | Itera automáticamente las 346 comunas de Chile |
| 🧹 **Nombres normalizados** | Etiquetas de comunas y regiones en formato título con acentuación correcta en español |
| 💾 **Guardado automático** | Guarda el progreso cada 10 comunas para evitar pérdida de datos en ejecuciones largas |
| 📁 **Múltiples formatos** | Exporta a CSV, Excel y un archivo sidecar de metadatos |
| 🔤 **Columnas compatibles con SQL** | Convención de nombres compatible con SQL, Python y DAX |
| 🛡️ **Tolerancia a errores** | Continúa automáticamente tras errores por comuna; los fallos quedan registrados en el log |
| 🕐 **Tiempos configurables** | Ajusta los tiempos de espera según las condiciones de tu red |

---

## Vista Previa del Dataset

### Esquema de Salida

```
comuna, region, parisi_votos, parisi_pct, kast_votos, kast_pct, ..., blanco_votos, blanco_pct
Arica, Arica y Parinacota, 15000, 45.50, 12000, 36.36, ..., 500, 1.50
Santiago, Metropolitana, 80000, 42.30, 75000, 39.68, ..., 1200, 0.63
```

### Referencia de Columnas

| Columna | Tipo | Descripción |
|---|---|---|
| `comuna` | `str` | Nombre normalizado de la comuna (ej. `Viña del Mar`, no `VIÑA DEL MAR`) |
| `region` | `str` | Nombre corto de la región (ej. `Metropolitana`, no `METROPOLITANA DE SANTIAGO`) |
| `{candidato}_votos` | `int` | Conteo absoluto de votos por candidato |
| `{candidato}_pct` | `float` | Porcentaje de votos (rango 0–100) |
| `blanco_votos` | `int` | Votos en blanco |
| `blanco_pct` | `float` | Porcentaje de votos en blanco |
| `nulo_votos` | `int` | Votos nulos |
| `nulo_pct` | `float` | Porcentaje de votos nulos |
| `emitidos_votos` | `int` | Total de votos emitidos |
| `emitidos_pct` | `float` | Porcentaje de participación electoral |

### Identificadores de Candidatos

El scraper mapea el nombre completo de cada candidato en SERVEL a un prefijo de columna corto y compatible con SQL:

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

## Instalación

### Prerrequisitos

GeckoDriver (WebDriver de Firefox) debe estar instalado y disponible en tu `PATH`:

```bash
# Ubuntu / Debian
sudo apt-get install firefox firefox-geckodriver

# macOS
brew install firefox geckodriver

# Windows
# Descarga GeckoDriver desde https://github.com/mozilla/geckodriver/releases
# y agrégalo a tu PATH
```

### Clonar y Configurar

```bash
# Clonar el repositorio
git clone https://github.com/adroguetth/Elecciones_Presidenciales_Chile_2025.git
cd Elecciones_Presidenciales_Chile_2025

# Cambiar a la rama de Primera Vuelta
git checkout PrimeraVuelta_2025

# Navegar al directorio del scraper
cd "Chilean-Presidential-Elections-2025-Analysis/First round/Web Scraper"

# Instalar dependencias Python
pip install -r requirements.txt
```

### `requirements.txt`

```
selenium>=4.15.0
pandas>=2.0.0
openpyxl>=3.0.0
```

---

## Uso

### Ejecución Básica (modo interactivo — abre una ventana Firefox visible)

```bash
python "Web Scraper.py"
```

### Modo Headless (recomendado para servidores y CI)

```bash
python "Web Scraper.py" --headless
```

### Prueba Rápida (primeras N comunas)

```bash
# Procesar solo 50 comunas — útil para desarrollo y pruebas rápidas
python "Web Scraper.py" --comunas 50 --headless
```

### Logging Detallado / Modo Debug

```bash
python "Web Scraper.py" --verbose --headless
```

### Resumen de Argumentos CLI

| Argumento | Descripción |
|---|---|
| `--headless` | Ejecutar Firefox sin ventana visible |
| `--comunas N` | Limitar la extracción a las primeras `N` comunas |
| `--verbose` | Activar nivel de logging `DEBUG` para salida detallada |

---

## Archivos de Salida

Tras una ejecución exitosa, el scraper genera los siguientes archivos en el directorio de trabajo:

| Archivo | Formato | Descripción |
|---|---|---|
| `election_matrix_{N}_comunas_{timestamp}.csv` | CSV | Salida principal — UTF-8, lista para análisis |
| `election_matrix_{N}_comunas_{timestamp}.xlsx` | Excel | Mismos datos en `.xlsx` para usuarios no técnicos |
| `election_matrix_{N}_comunas_{timestamp}_METADATA.txt` | Texto | Documentación del esquema, diccionario de candidatos y ejemplos de consultas |
| `checkpoint_{N}_comunas_{timestamp}.csv` | CSV | Guardados intermedios cada 10 comunas (generados automáticamente durante la ejecución) |
| `scraper_elecciones.log` | Log | Log completo de la ejecución con timestamps y detalles de errores |

---

## Benchmarks de Rendimiento

| Métrica | Valor |
|---|---|
| ⏱️ Tiempo estimado | 35–60 minutos (346 comunas completas) |
| 🧠 Uso de RAM | ~500 MB |
| 💾 Uso de disco | 50–100 MB |
| 🏙️ Throughput | ~300–400 comunas/hora |
| 💾 Frecuencia de checkpoint | Cada 10 comunas |

---

## Arquitectura y Pipeline de Extracción

El scraper está implementado como una única clase, `ServelElectionScraper`, siguiendo un pipeline limpio y secuencial:

```
initialise_browser()
    └── _navigate_to_servel()
        └── _activate_electoral_division_filter()
            └── _get_regions()
                └── por cada región:
                    _get_comunas_for_region()
                        └── por cada comuna:
                            _extract_comuna_data()
                                └── _parse_results_table()
                                    └── _parse_row()  ← clasifica fila como candidato o total
                            _save_partial_progress()  ← cada 10 comunas
_build_final_dataframe()
_save_final_results()  ← CSV + Excel + metadatos
```

### Lógica de Normalización de Nombres

**Comunas** pasan por una normalización en tres etapas:
1. Minúsculas → Título, con manejo especial para `ñ` y números romanos.
2. Las preposiciones españolas (`de`, `del`, `la`, `los`, `y`, etc.) se convierten a minúsculas.
3. Un diccionario curado garantiza la acentuación correcta de nombres conocidos (ej. `Copiapó`, `Valparaíso`, `Ñuñoa`).

**Regiones** se mapean desde las etiquetas administrativas verbosas de SERVEL a nombres canónicos cortos mediante un diccionario explícito, con un fallback basado en regex para variantes no listadas.

---

## Personalización

### Ajustar Tiempos de Espera de Selenium

Aumenta estos valores si ves errores frecuentes de `TimeoutException` en conexiones lentas:

```python
self.WAIT_PAGE_LOAD = 20       # Segundos de espera para la carga inicial de la página
self.WAIT_DROPDOWN_SELECT = 5  # Segundos tras seleccionar una región/comuna
self.WAIT_TABLE_RENDER = 6     # Segundos para que aparezca la tabla de resultados
```

### Agregar Nuevos Candidatos

Extiende el diccionario de mapeo de candidatos dentro de `__init__`:

```python
self.CANDIDATE_MAP = {
    "NOMBRE COMPLETO NUEVO CANDIDATO": "nuevo_candidato",
    # ... entradas existentes
}
```

### Limitar la Extracción a Regiones Específicas

```python
regions = self._get_regions()
regions_to_process = [r for r in regions if "METROPOLITANA" in r.upper()]
```

---

## Solución de Problemas

### GeckoDriver no encontrado

```bash
# Ubuntu / Debian
sudo apt-get install firefox-geckodriver

# Verificar la instalación
which geckodriver
geckodriver --version
```

### Errores de timeout frecuentes

Aumenta los tiempos de espera en el `__init__` del scraper (ver [Personalización](#personalización)).

### Elementos de página no encontrados

- Verifica que [https://elecciones.servel.cl/](https://elecciones.servel.cl/) sea accesible desde tu máquina.
- Ejecuta con `--verbose` para identificar en qué paso está fallando.
- SERVEL actualiza su estructura de página ocasionalmente; revisa si los XPaths o los textos de los botones han cambiado.

### Monitorear logs en tiempo real

```bash
tail -f scraper_elecciones.log

# Filtrar solo errores
grep "ERROR" scraper_elecciones.log
```

---

## Ejemplos de Consultas

Una vez finalizada la extracción, el dataset está listo para usar de inmediato:

```sql
-- SQL: resultados de Kast en la región Metropolitana
SELECT comuna, kast_votos, kast_pct
FROM election_matrix
WHERE region = 'Metropolitana'
ORDER BY kast_pct DESC;
```

```python
# Python: correlación entre dos candidatos en todas las comunas
import pandas as pd
df = pd.read_csv("election_matrix_346_comunas_*.csv")
print(df['kast_pct'].corr(df['matthei_pct']))
```

```dax
// DAX: total de votos de Jara en una región
CALCULATE(SUM([jara_votos]), [region] = "Metropolitana")
```

---

## Casos de Uso

**Investigadores y cientistas políticos** — análisis de patrones de voto, estudios de participación, clustering geográfico.

**Analistas de datos y periodistas** — dashboards de BI, segmentación geográfica, reportes de tendencias.

**Desarrolladores** — APIs de datos electorales, modelos predictivos, aplicaciones web.

---

## Contribuciones

Las contribuciones son bienvenidas. Para comenzar:

1. **Haz un fork** del repositorio
2. **Crea una rama** para tu funcionalidad: `git checkout -b feature/nombre-de-tu-feature`
3. **Haz commit** de tus cambios: `git commit -m "Add: descripción del cambio"`
4. **Sube** tu fork: `git push origin feature/nombre-de-tu-feature`
5. **Abre un Pull Request** contra la rama `PrimeraVuelta_2025`

### Guía de Estilo de Código

- Seguir [PEP 8](https://peps.python.org/pep-0008/)
- Usar type hints en todas las firmas de funciones
- Incluir docstrings estilo NumPy en métodos públicos
- Mantener compatibilidad con versiones anteriores
- Escribir tests para nuevas funcionalidades

---

## Aviso Legal y Ético

Los datos extraídos con esta herramienta provienen de un sitio web gubernamental público. Su uso debe cumplir con:

- Los términos de uso del SERVEL
- La Ley chilena de protección de datos (Ley 19.628)
- Un uso responsable y ético de la información electoral

---

## Licencia

Este proyecto está bajo la **Licencia MIT** — consulta el archivo [LICENSE](https://github.com/adroguetth/Elecciones_Presidenciales_Chile_2025/blob/PrimeraVuelta_2025/LICENSE) para más detalles.

---

## Autor

**Alfonso Droguett** — Analista de Datos

- 🔗 [LinkedIn](https://www.linkedin.com/in/adroguetth/)
- 🌐 [Portafolio](https://www.adroguett-portfolio.cl/)
- 📧 [adroguett.consultor@gmail.com](mailto:adroguett.consultor@gmail.com)

---

_Última actualización: Noviembre 2025_
