# 🗳️ Consultas SQL — Elección Presidencial Chile 2025 (Segunda Vuelta)

**¿Buscas la versión en inglés?** → [README.md](README.md)

![MIT License](https://img.shields.io/badge/license-MIT-9ecae1?style=flat-square&logo=open-source-initiative&logoColor=white) ![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?style=flat-square&logo=microsoft-sql-server&logoColor=white)

## 📋 Descripción General

Este repositorio contiene la capa analítica completa basada en SQL para la **segunda vuelta de las elecciones presidenciales chilenas 2025**. Extiende el análisis de primera vuelta mediante:

- Comparación de participación, votos nulos/blancos y crecimiento de candidatos entre rondas.
- Medición del dominio territorial (comunas y regiones).
- Modelado de la transferencia decisiva de los **2,55 millones de votantes de Parisi**.
- Simulación de 17 escenarios de tasas de transferencia Parisi→Jara (20% a 80%).
- Identificación de comunas ultracompetitivas, zonas de pérdida de votos y patrones de voto protesta.

Todas las consultas están escritas en **T-SQL** (SQL Server 2012+), utilizan **Expresiones de Tabla Comunes (CTEs)** y funciones de agregación, y están completamente documentadas.

---

## 🎯 Hallazgos Analíticos Clave

### 1. Anomalía en la participación – caída pronunciada de votos válidos

| Indicador         | Primera Vuelta | Segunda Vuelta | Cambio                 |
| ----------------- | -------------- | -------------- | ---------------------- |
| Votos emitidos    | 13.388.455     | 13.362.076     | –26.379                |
| **Votos válidos** | 12.885.928     | **12.415.044** | **–470.884**           |
| Votos nulos       | 360.571        | 782.029        | **+421.458** (+116,9%) |
| Votos en blanco   | 141.956        | 165.003        | +23.047                |

> **Interpretación:** A pesar del voto obligatorio, los votos válidos cayeron casi medio millón. El aumento de votos nulos (+421k) es el principal factor, no la abstención.

### 2. El aumento del voto nulo fue universal – más fuerte en regiones mineras

Las 16 regiones registraron un mayor porcentaje de voto nulo. Los aumentos más pronunciados ocurrieron en el norte:

| Región      | % Nulos 1V | % Nulos 2V | Δ pp         |
| ----------- | ---------- | ---------- | ------------ |
| Antofagasta | 3,08%      | 9,04%      | **+5,96 pp** |
| Atacama     | 2,80%      | 8,05%      | **+5,25 pp** |
| Tarapacá    | 2,42%      | 7,00%      | +4,58 pp     |
| Coquimbo    | 3,10%      | 7,30%      | +4,20 pp     |

> **Interpretación:** El voto nulo fue el mecanismo de protesta preferido contra el duopolio Jara‑Kast. Las regiones mineras, donde Parisi había destacado en primera vuelta, lideraron la protesta.

### 3. Barrido territorial de Kast – 310 comunas, las 16 regiones

| Candidato | Comunas ganadas | % de comunas | Regiones ganadas |
| --------- | --------------- | ------------ | ---------------- |
| **Kast**  | **310**         | **89,6%**    | **16/16**        |
| Jara      | 36              | 10,4%        | 0/16             |

- Las 36 comunas de Jara se concentran en solo **5 regiones**: Metropolitana (21), Valparaíso (5), Atacama (4), Coquimbo (3), Antofagasta (3).
- Alcanzó **mayoría absoluta (>50%)** exactamente en esas 36 comunas – en ningún otro lugar.

### 4. Los bastiones de Kast son profundos, no solo amplios

| Intensidad de victoria    | Comunas | % de victorias de Kast | % promedio de Kast |
| ------------------------- | ------- | ---------------------- | ------------------ |
| Arrolladora (>80%)        | 6       | 1,9%                   | 86,62%             |
| Bastión (70‑80%)          | 77      | 24,8%                  | 73,54%             |
| Sólida (60‑70%)           | 137     | 44,2%                  | 65,11%             |
| Mayoría estrecha (50‑60%) | 90      | 29,0%                  | 55,64%             |

**El 63,6% de todas las comunas dio a Kast >60%** – una señal de apoyo territorial profundo, no una victoria fragmentada.

### 5. La transferencia decisiva de Parisi – 42% a Jara, 37,7% a Kast, 20,3% protesta

Mediante correlación a nivel comunal (consulta 12) y simulación de escenarios (11a, 11b), la distribución más probable de los 2.550.770 votantes de Parisi en primera vuelta es:

| Destino                    | % de votantes de Parisi | Votos estimados |
| -------------------------- | ----------------------- | --------------- |
| Jeannette Jara             | 42,0%                   | 1.071.323       |
| José Antonio Kast          | 37,7%                   | 961.640         |
| Nulo / Blanco / Abstención | 20,3%                   | 517.806         |

> **Interpretación:** Jara capturó la mayor porción individual, pero la porción de Kast (37,7%) fue crítica. Uno de cada cinco votantes de Parisi eligió la protesta activa (nulo/blanco) o la abstención.

### 6. Análisis de escenarios – Jara necesitaba >65% de Parisi para ganar

Utilizando transferencias fijas para todos los demás candidatos eliminados (Kaiser, Matthei, Artes, MEO, Mayne‑Nicholls), realizamos un barrido de Parisi→Jara desde 20% hasta 80%:

| Parisi → Jara          | % Jara (sim) | % Kast (sim) | Ganador (sim) | Coincide con realidad |
| ---------------------- | ------------ | ------------ | ------------- | --------------------- |
| 20%                    | 37,14%       | 62,86%       | Kast          | No                    |
| **42% (mejor ajuste)** | **41,69%**   | **58,31%**   | **Kast**      | **✅**                 |
| 43% (más cercano)      | 41,89%       | 58,11%       | Kast          | ✅ (error <0,1 pp)     |
| 60%                    | 45,41%       | 54,59%       | Kast          | No                    |
| 65%                    | 46,44%       | 53,56%       | Kast          | No                    |
| 80%                    | 49,54%       | 50,46%       | Kast          | No                    |

**Conclusión:** Incluso con un 80% de transferencia, Jara no habría ganado. Para alcanzar la mayoría, habría necesitado **>65% de los votantes de Parisi** – un nivel que nunca se materializó y era estructuralmente imposible dado el perfil antisistema de Parisi.

### 7. Kast creció en todas las regiones – crecimiento más fuerte en bastiones de Parisi

| Región             | Crecimiento Kast (pp) | % Kast 1V | % Kast 2V |
| ------------------ | --------------------- | --------- | --------- |
| Arica y Parinacota | **+36,47**            | 20,97%    | 57,44%    |
| Tarapacá           | **+35,21**            | 21,82%    | 57,03%    |
| Antofagasta        | +33,56                | 17,27%    | 50,83%    |
| Atacama            | +31,25                | 18,04%    | 49,29%    |

Kast más que duplicó su porcentaje de votos en las cuatro regiones del norte – las mismas áreas donde Parisi había dominado en primera vuelta.

### 8. Los votos de protesta no perjudicaron a Kast

Categorizamos las comunas por el aumento absoluto de votos nulos+blancos. El crecimiento de Kast se mantuvo estable en todos los niveles de protesta:

| Aumento de protesta | Comunas | Crecimiento promedio Kast (pp) |
| ------------------- | ------- | ------------------------------ |
| Disminución         | 6       | +38,26                         |
| Bajo (0–500)        | 170     | +36,73                         |
| Medio (500–1.000)   | 63      | +36,92                         |
| Alto (1.000–2.000)  | 44      | +34,05                         |
| Muy alto (>2.000)   | 63      | +34,49                         |

**Rango de crecimiento promedio:** solo 4 puntos porcentuales. El desempeño de Kast fue casi independiente de la intensidad de la protesta.

### 9. Solo una comuna donde Kast perdió votos absolutos

De 346 comunas, Kast perdió votos absolutos en **solo 1 comuna** (Antártica, con población insignificante). Esto confirma que su apoyo no solo fue amplio sino también extremadamente estable entre rondas.

---

## 🗃️ Modelo de Datos

Se utilizan dos tablas, ambas con clave compuesta por `commune` (NVARCHAR) y `region` (NVARCHAR).

### `first_round_2025` (346 filas, 24 columnas)

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

### `second_round_2025` (346 filas, 12 columnas)

```text
second_round_2025
├── commune, region
├── casted_votes
├── blank_votes, blank_pct
├── null_votes, null_pct
├── jara_votes, jara_pct
└── kast_votes, kast_pct
```



Todas las columnas de porcentaje son `DECIMAL(5,2)`. La clave compuesta `(commune, region)` garantiza la unicidad y las uniones correctas incluso cuando los nombres de comunas se repiten entre regiones.

------

## 📊 Índice Completo de Consultas

| #    | Archivo                                               | Objetivo                                                  |
| :--- | :---------------------------------------------------- | :-------------------------------------------------------- |
| 01   | `01_comparative_voter_turnout_first_second_round.sql` | Participación, votos válidos, nulos, blancos entre rondas |
| 02   | `02_regions_null_vote_increase.sql`                   | Aumento de votos nulos por región                         |
| 03   | `03_regions_blank_vote_comparison.sql`                | Cambio de votos en blanco por región                      |
| 04   | `04_second_round_winner.sql`                          | Resultado final y margen                                  |
| 05   | `05_second_round_territorial_mapping.sql`             | Comunas ganadas por candidato                             |
| 06   | `06_second_round_regional_mapping.sql`                | Regiones ganadas por candidato                            |
| 07   | `07_jara_absolute_majority_communes.sql`              | Comunas donde Jara >50%                                   |
| 08   | `08_competitive_communes_kast_margin_under_2pp.sql`   | Margen <2 puntos porcentuales                             |
| 09   | `09_communes_flipped_to_jara.sql`                     | Transferencias Parisi→Jara                                |
| 10a  | `10a_kast_top_strongholds.sql`                        | Top 10 comunas de Kast                                    |
| 10b  | `10b_kast_strongholds_summary.sql`                    | Victorias de Kast por intensidad                          |
| 10c  | `10c_kast_strongholds_by_region.sql`                  | Desglose regional de Kast >60%                            |
| 11a  | `11a_parisi_vote_destination.sql`                     | Simulación de transferencia Parisi (42% fijo a Jara)      |
| 11b  | `11b_parisi_transfer_scenarios.sql`                   | Barrido de 17 escenarios (20%–80% a Jara)                 |
| 12   | `12_parisi_to_kast_correlation.sql`                   | Intensidad Parisi vs % Kast 2V                            |
| 13   | `13_kast_growth_by_region.sql`                        | Crecimiento de Kast (absoluto y pp) por región            |
| 14   | `14_kast_communes_with_vote_loss.sql`                 | Comunas donde Kast perdió votos                           |
| 15   | `15_null_blank_impact_on_kast.sql`                    | Impacto del voto protesta en el crecimiento de Kast       |
| 16   | `16_top_parisi_communes_second_round.sql`             | Comportamiento en las 20 comunas con más Parisi           |
| 17   | `17_parisi_null_vote_correlation.sql`                 | Intensidad Parisi vs tasa de voto nulo en segunda vuelta  |

------

## 🚀 Configuración y Uso

### Requisitos previos

- SQL Server 2012 o superior (cualquier edición)
- (Opcional) Python 3.10+ con `pandas`, `pyodbc` para el script ETL.

### Opción A – ETL con Python (recomendada – crea ambas tablas)

```bash
cd second_round/2_1.sql_analysis/sql_server_scripts
python create_elections_database.py
```



Flags opcionales:

```bash
--no-execute        # Genera solo el script SQL, no lo ejecuta
--batch-size 1000   # Tamaño del lote de inserción (predeterminado: 500)
```



### Opción B – Scripts SQL pregenerados

Ejecutar en orden en SSMS / Azure Data Studio / `sqlcmd`:

```sql
USE master;
GO
CREATE DATABASE EleccionesChile2025;
GO
USE EleccionesChile2025;
GO
-- 1. Ejecutar: create_database_first_round_2025.sql
-- 2. Ejecutar: create_database_second_round_2025.sql
```

Enlaces a los archivos raw:

- [`create_database_first_round_2025.sql`](https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/second_round/2_1.sql_analysis/sql_server_scripts/create_database_first_round_2025.sql)
- [`create_database_second_round_2025.sql`](https://raw.githubusercontent.com/adroguetth/Chilean-Presidential-Elections-2025-Analysis/refs/heads/main/second_round/2_1.sql_analysis/sql_server_scripts/create_database_second_round_2025.sql)

### Ejecutar cualquier consulta analítica

```sql
USE EleccionesChile2025;
GO
-- Copiar y pegar el contenido de cualquier archivo .sql
```



------

## 📂 Estructura del Proyecto

```text
second_round/
└── 2_1.sql_analysis/
    ├── README.md      (traducción al ingles del readme)
    ├── README.es.md   (este archivo)
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

## 🧠 Notas de Diseño y Rendimiento

| Práctica                                            | Por qué                                                      |
| :-------------------------------------------------- | :----------------------------------------------------------- |
| **CTEs (`WITH ...`)**                               | Descomponen la lógica compleja (totales → ratios → categorías) sin subconsultas anidadas. Mejora drásticamente la legibilidad y el mantenimiento. |
| **`DECIMAL(5,2)` para porcentajes**                 | Evita la desviación del punto flotante. Coincide con el formato fuente de SERVEL. |
| **`NULLIF(denominador,0)`**                         | Previene la división por cero en comunas muy pequeñas (ej. Antártica, Ollagüe). |
| **Clave de unión compuesta**                        | Une por `commune` + `region` para evitar coincidencias falsas cuando dos regiones comparten un nombre de comuna (ej. "San José" aparece en múltiples regiones). |
| **Ordenamiento regional norte‑sur**                 | La sentencia `CASE` en `ORDER BY` asigna orden numérico desde Arica hasta Magallanes, no alfabético – esencial para la coherencia geográfica. |
| **Parametrización de la simulación**                | Los 17 escenarios en la consulta 11b se definen como un CTE de filas, con `CROSS JOIN` a cálculos fijos. Agregar un nuevo escenario requiere una fila adicional. |
| **Categorización de protesta por aumento absoluto** | Usar aumentos absolutos (0–500, 500–1.000, etc.) en lugar de puntos porcentuales es más estable entre comunas con tamaños de población muy diferentes. |

Todas las consultas están basadas en conjuntos y se ejecutan en <1 segundo en una instancia estándar de SQL Server (346 filas).

------

## 📄 Licencia y Atribución

- **Licencia**: MIT
- **Autor**: Alfonso Droguett
  - 🔗 **LinkedIn:** [Alfonso Droguett](https://www.linkedin.com/in/adroguetth/)
  - 🌐 **Portafolio web:** [adroguett-portfolio.cl](https://www.adroguett-portfolio.cl/)
  - 📧 **Correo:** adroguett.consultor@gmail.com
- **Fuente de datos**: SERVEL (dominio público, autoridad electoral oficial)
- **Tecnologías**: SQL Server, T-SQL, Python (extracción de datos)
- **Enfoque analítico**: Expresiones de Tabla Comunes (CTEs)

------

## ⭐ Agradecimientos

Si este proyecto te es útil, ¡considera darle una estrella en GitHub!
