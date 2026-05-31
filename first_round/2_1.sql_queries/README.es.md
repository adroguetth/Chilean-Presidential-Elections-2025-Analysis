# 🗃️ SQL Queries — Chilean Presidential Election 2025 (First Round)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?style=flat-square&logo=microsoft-sql-server&logoColor=white)

## 📋 Descripción General

Esta carpeta contiene **9 consultas SQL analíticas** para la primera vuelta de la elección presidencial chilena 2025. Diseñadas para **SQL Server 2012+**, replican y validan los hallazgos clave del [notebook de análisis principal](https://github.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/tree/main/first_round/2_2.notebooks).

Todas las consultas referencian la tabla `first_round_2025`, creada a partir del CSV oficial usando el script de conversión [`create_elections_database.py`](https://sql_server_scripts/create_elections_database.py).

Puedes obtener la base de datos de dos maneras:

- **Descargar el script pre‑generado:** [`create_database.sql`](https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/first_round/2_1.sql_queries/sql_server_scripts/create_database.sql)
- **Generarlo tú mismo** usando el script Python (ver más abajo).

------

## 🎯 Objetivos del Análisis

| Objetivo                         | Descripción                                                  |
| :------------------------------- | :----------------------------------------------------------- |
| **Distribución Nacional**        | Analizar la distribución de votos por candidato a nivel nacional |
| **Bastiones Electorales**        | Identificar comunas con mayor apoyo por candidato            |
| **Competitividad**               | Detectar comunas con diferencias estrechas entre candidatos  |
| **Patrones Regionales**          | Examinar tendencias por región y capitales regionales        |
| **Fenómeno Antisistema**         | Investigar el voto de protesta contra el duopolio político   |
| **Estrategia de Segunda Vuelta** | Identificar oportunidades estratégicas para la campaña       |

------

## 📁 Índice de Consultas

| #     | Consulta                     | Descripción                                                 |
| :---- | :--------------------------- | :---------------------------------------------------------- |
| **1** | `01_overall_turnout.sql`     | Participación electoral: votos válidos, blancos, nulos      |
| **2** | `02_national_results.sql`    | Porcentajes de voto para los 8 candidatos                   |
| **3** | `03_runoff_candidates.sql`   | Identifica a Jara y Kast como finalistas de segunda vuelta  |
| **4** | `04_top_10_communes.sql`     | Mayor porcentaje de voto por candidato                      |
| **5** | `05_territorial_mapping.sql` | Comunas ganadas por candidato                               |
| **6** | `06_results_by_region.sql`   | Promedios regionales y ganadores (orden norte–sur)          |
| **7** | `07_regional_capitals.sql`   | Resultados en las 16 capitales regionales (orden norte–sur) |
| **8** | `08_flippable_communes.sql`  | Comunas con margen < 1.000 votos (territorios disputables)  |
| **9** | `09_anti_establishment.sql`  | Parisi vs. duopolio Jara+Kast                               |

------

## 🗃️ Modelo de Datos

| Elemento       | Descripción                          |
| :------------- | :----------------------------------- |
| **Fuente**     | SERVEL (Servicio Electoral de Chile) |
| **Extracción** | Python con Selenium                  |
| **Cobertura**  | 346 comunas a nivel nacional         |

### Estructura de la Tabla (`first_round_2025`)

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
└── [columnas de porcentaje restantes]
```



------

## 📊 Hallazgos Clave por Consulta

Basado en los datos reales (`first_round_2025`, 346 comunas, 24 columnas):

| Consulta               | Hallazgo Clave                                               |
| :--------------------- | :----------------------------------------------------------- |
| **1 – Participación**  | 13,39M votos emitidos, 2,69% nulos, 1,06% blancos. Votos válidos: 96,25% |
| **2 – Nacional**       | Jara 26,74%, Kast 23,95%, Parisi 19,80%, Kaiser 13,94%, Matthei 12,44%, otros <2% |
| **3 – Segunda Vuelta** | Jara (1°) y Kast (2°) avanzan a segunda vuelta               |
| **4 – Top 10**         | Parisi domina el norte (Ollagüe 58,2%, María Elena 45,9%). Jara más fuerte en RM (Pedro Aguirre Cerda 41,9%). Kast más fuerte en zonas rurales (Lumaco 46,2%) |
| **5 – Territorial**    | Kast gana 169 comunas (48,8%), Jara 105 (30,3%), Parisi 64 (18,5%), Kaiser 4, Matthei 2 |
| **6 – Regional**       | Parisi gana 5 regiones del norte, Jara gana RM/Valparaíso/Aysén/Magallanes, Kast gana centro‑sur (Ñuble a Los Lagos) |
| **7 – Capitales**      | Jara gana 10 capitales (Santiago, Valparaíso, Concepción…), Kast gana 4 (Chillán, Temuco, Puerto Montt, Coyhaique), Parisi gana 2 (Arica, Antofagasta) |
| **8 – Recuperables**   | 31 comunas con margen <1.000 votos; Jara necesitaría 19.853 votos para voltearlas, Kast 15.224 |
| **9 – Antisistema**    | Parisi supera a Jara+Kast en 11 comunas del norte (Ollagüe +29,97%, María Elena +8,44%, Calama +1,01%) |

------

## 🚀 Guía Rápida

### 1. Crear la base de datos y la tabla

**Opción A – Descargar script pre‑generado:**

```bash
curl -O https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/first_round/2_1.sql_queries/sql_server_scripts/create_database.sql
```

Luego ejecútalo en SSMS o `sqlcmd`.



**Opción B – Generar el script tú mismo:**

Navega a `sql_server_scripts/` y ejecuta:

```bash
cd sql_server_scripts/

# Ejecución normal (intenta conexión directa a SQL Server)
python create_elections_database.py

# Solo generar el script SQL (no ejecutar)
python create_elections_database.py --no-execute

# Cambiar el tamaño del lote (por defecto 500)
python create_elections_database.py --batch-size 1000

# Cambiar el nombre de la tabla
python create_elections_database.py --table "first_round_results"
```



### 2. Ejecutar una consulta

```sql
USE EleccionesChile2025;
GO

-- Ejemplo: Candidatos de segunda vuelta
SELECT candidato, porcentaje
FROM (
    -- Copiar consulta desde 03_runoff_candidates.sql
) AS resultados;
```



------

## 🧠 Notas de Diseño

| Característica                 | Descripción                                                  |
| :----------------------------- | :----------------------------------------------------------- |
| **Orden geográfico**           | Las consultas 6 y 7 usan `CASE` para ordenar regiones de **norte a sur** (Arica → Magallanes) |
| **Precisión**                  | Todos los porcentajes están formateados como `DECIMAL(5,2)` (ej: `35,00`, `27,68`) |
| **Estructura reutilizable**    | Se usan CTEs para descomponer la lógica compleja (ej: `WITH resultados_region`, `ganadores_region`) |
| **Análisis de segunda vuelta** | La consulta 8 identifica comunas recuperables con margen < 1.000 votos |

------

## 🛠️ Stack Tecnológico

| Tecnología            | Propósito                              |
| :-------------------- | :------------------------------------- |
| **Base de Datos**     | SQL Server (T-SQL)                     |
| **Enfoque Analítico** | Common Table Expressions (CTEs)        |
| **Métricas**          | Agregaciones espaciales y porcentuales |
| **Lenguaje**          | T-SQL (SQL Server 2012+)               |

------

## 📂 Estructura de Archivos

```text
2_1.sql_queries/
├── README.md
├── README.es.md
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

## 📄 Licencia y Atribución

- **Licencia**: MIT
- **Autor**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Portafolio web:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Correo:** adroguett.consultor@gmail.com
- **Fuente de datos**: SERVEL (dominio público, autoridad electoral oficial)
- **Tecnologías**: SQL Server (T-SQL)
- **Enfoque analítico**: Common Table Expressions (CTEs)

------

## ⭐ Agradecimientos

¡Si este proyecto te es útil, considera darle una estrella en GitHub!
