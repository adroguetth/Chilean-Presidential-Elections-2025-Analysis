# Análisis SQL — Elección Presidencial Chile 2025 (Primera Vuelta)

## Descripción General

Esta carpeta contiene la capa analítica SQL completa del proyecto. Todas las consultas se ejecutan sobre una única tabla (`resultados_elecciones`) cargada con los datos extraídos por el Web Scraper, y están estructuradas mediante CTEs para garantizar legibilidad, modularidad y auditabilidad.

El análisis cubre el universo completo de **346 comunas** en las 16 regiones de Chile, utilizando datos oficiales del SERVEL para la Primera Vuelta Presidencial 2025.

---

## Estructura de Carpeta

```
SQL Analysis/
├── README.md                          ← documentación en ingles
├── README.es.md                       ← este archivo
├── queries/
│   ├── 01_participation_stats.sql     ← métricas de participación nacional
│   ├── 02_national_results.sql        ← porcentaje de votos por candidato
│   ├── 03_runoff_candidates.sql       ← identificación top-2 (Ley 18.700)
│   ├── 04_results_by_region.sql       ← desglose regional
│   ├── 05_top_communes.sql            ← comunas más fuertes por candidato
│   ├── 06_competitive_communes.sql    ← comunas reñidas (margen <5%)
│   ├── 07_regional_capitals.sql       ← resultados en capitales regionales
│   ├── 08_urban_rural_gap.sql         ← paradoja territorio vs. población
│   └── 09_parisi_kingmaker.sql        ← voto antisistema y escenarios de transferencia
└── docs/
    └── Technical Analysis.md          ← documentación técnica completa
```

---

## Modelo de Datos

**Base de datos:** SQL Server  
**Fuente:** SERVEL (extraído mediante Python/Selenium — ver `../Web Scraper/`)  
**Tabla:** `resultados_elecciones`

```sql
resultados_elecciones (
    comuna                    VARCHAR,   -- nombre normalizado de la comuna
    region                    VARCHAR,   -- nombre corto de la región
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

> **Nota:** Las columnas `_votos` contienen conteos absolutos; las columnas `_pct` contienen el porcentaje de cada candidato como float (0–100) pre-calculado por el scraper. Los porcentajes en las consultas siempre se re-derivan sobre `total_votos_validos` para garantizar consistencia analítica.

---

## Índice de Consultas

Ejecutar las consultas en orden — cada una construye conceptualmente sobre la anterior.

### `01_participation_stats.sql` — Métricas de Participación Nacional
Agrega las métricas fundamentales de participación a nivel nacional mediante una CTE de dos capas: totales brutos en la CTE 1, formato indicador-valor pivotado en la CTE 2. Establece el universo electoral para todos los análisis posteriores.

| Métrica | Valor |
|---|---|
| Total comunas | 346 |
| Total votos emitidos | 13.388.455 |
| Votos válidos | 12.885.928 (96,25%) |
| Votos en blanco | 141.956 (1,06%) |
| Votos nulos | 360.571 (2,69%) |

**Técnica clave:** `CAST(métrica AS FLOAT) / total_emitidos * 100` — evita la división entera.

---

### `02_national_results.sql` — Porcentaje de Votos por Candidato
Transpone la tabla ancha a formato largo de filas por candidato mediante `UNION ALL`, calcula el porcentaje de cada candidato sobre votos válidos y aplica una clasificación categórica de apoyo (`Alto / Medio / Bajo`).

| Candidato | Porcentaje | Categoría |
|---|---|---|
| Jeannette Jara | 26,75% | Alto |
| José Antonio Kast | 23,96% | Alto |
| Franco Parisi | 19,80% | Medio |
| Johannes Kaiser | 13,94% | Medio |
| Evelyn Matthei | 12,44% | Medio |
| Harold Mayne-Nicholls | 1,26% | Bajo |
| Marco Enríquez-Ominami | 1,20% | Bajo |
| Eduardo Artes | 0,66% | Bajo |

**Técnica clave:** `CASE WHEN pct >= 20` para clasificación de apoyo; umbrales en 20% y 10%.

---

### `03_runoff_candidates.sql` — Identificación para Segunda Vuelta (Ley 18.700)
Cascada de tres CTEs: agregación nacional → porcentajes individuales → ranking con `ROW_NUMBER()`. Filtra `WHERE posicion <= 2` para identificar los dos candidatos que avanzan a segunda vuelta, y aplica umbrales de competitividad legal (>50% = mayoría absoluta, >20% = competitivo).

| Candidato | % | Posición | Contexto |
|---|---|---|---|
| Jeannette Jara | 26,75% | 1er Lugar | Umbral competitivo |
| José Antonio Kast | 23,96% | 2do Lugar | Umbral competitivo |

**Técnica clave:** `ROW_NUMBER() OVER (ORDER BY porcentaje DESC)` para ranking sin empates.

---

### `04_results_by_region.sql` — Desglose Regional
Agrega conteos absolutos y relativos por región para cada candidato, permitiendo la segmentación geográfica del mapa electoral. Identifica al candidato dominante por región.

**Hallazgos clave:**
- Norte (4 regiones): Dominio de Parisi — voto antisistema / minero
- Centro-Sur (7 regiones): Hegemonía de Kast — voto rural / conservador
- Centro / Patagonia (5 regiones): Fortaleza de Jara — voto urbano / izquierda

**Técnica clave:** `GROUP BY region` con función ventana para asignar ganador regional.

---

### `05_top_communes.sql` — Comunas Más Fuertes por Candidato
Rankea las comunas por porcentaje de voto para cada candidato y retorna el top N por candidato. Útil para identificar fortalezas geográficas y territorio base.

**Técnica clave:** `ROW_NUMBER() OVER (PARTITION BY candidato ORDER BY pct DESC)`.

---

### `06_competitive_communes.sql` — Comunas Reñidas
Identifica las comunas donde el margen entre Jara y Kast es inferior a un umbral configurable (por defecto: <5 puntos porcentuales). Estas son las comunas bisagra que determinan el resultado nacional.

| Umbral | Comunas |
|---|---|
| < 1.000 votos | 134 comunas |
| < 5% de margen | ~180 comunas |

**Técnica clave:** Filtro `ABS(jara_pct - kast_pct) < 5` con diferencia absoluta de votos.

---

### `07_regional_capitals.sql` — Resultados en Capitales Regionales
Filtra las 16 capitales regionales y analiza el desempeño de cada candidato en centros urbanos, revelando la brecha estructural urbano-rural.

**Hallazgos clave:**
- Jara gana 10/16 capitales (62,5%) pero solo 5/16 regiones (31,3%)
- Kast gana 4/16 capitales (25,0%) pero 7/16 regiones (43,8%)
- Paradoja estructural: conteo de territorio vs. peso poblacional

**Técnica clave:** `WHERE comuna IN (...)` con lista curada de capitales regionales.

---

### `08_urban_rural_gap.sql` — Paradoja Territorio vs. Población
Cuantifica el sesgo estructural entre conteo de comunas (territorio) y volumen de votos (población). Calcula métricas de eficiencia: votos por comuna ganada, cobertura territorial vs. peso electoral.

**Hallazgos clave:**
- Kast: 169 comunas (48,8%) → 23,96% de los votos
- Jara: 105 comunas (30,3%) → 26,75% de los votos
- Kast requiere ~334 votos/comuna en promedio vs. ~420 de Jara

**Técnica clave:** `COUNT(*)` particionado por candidato ganador vs. `SUM(votos)` particionado por el mismo criterio.

---

### `09_parisi_kingmaker.sql` — Voto Antisistema y Escenarios de Transferencia
Analiza la concentración geográfica de Parisi en comunas del norte, modela tres escenarios de transferencia de votos para la segunda vuelta (con complemento de simulación en Python), e identifica sus comunas más vulnerables (margen <5% sobre el duopolio Jara-Kast).

**Escenarios de transferencia modelados:**

| Escenario | % a Jara | % a Kast | Resultado neto |
|---|---|---|---|
| Óptimo para Jara | 60% | 30% | Jara +2.500 votos netos |
| División neutral | 40% | 50% | Kast +800 votos netos |
| Óptimo para Kast | 30% | 60% | Kast +2.000 votos netos |

**Técnicas clave:** Filtrado CTE en regiones del norte, correlación tamaño vs. margen, función Python `simular_transferencia_parisi()` para modelado de escenarios.

---

## Enfoque Analítico

Todas las consultas comparten una filosofía de diseño consistente:

**Arquitectura CTE-first** — sin subconsultas anidadas en `FROM` o `WHERE`. Cada paso de transformación está nombrado e isolado, haciendo los planes de ejecución legibles y los resultados auditables.

**Votos válidos como denominador** — todos los porcentajes por candidato se calculan sobre `SUM(emitidos_votos) - SUM(nulo_votos) - SUM(blanco_votos)`, consistente con la ley electoral chilena (Ley 18.700, Art. 109).

**`CAST(AS FLOAT)` antes de dividir** — previene el truncamiento por división entera en SQL Server.

**`ROUND(..., 2)` en todos los porcentajes** — 2 decimales en todas las consultas para consistencia.

---

## Hallazgos Principales

```
1. Fragmentación Política Avanzada
   Ningún candidato supera el 27%: Jara 26,75%, Kast 23,96%, Parisi 19,80%
   Tres derechas competidoras: Kast (populista), Kaiser (libertaria), Matthei (tradicional)
   49,29% del voto disponible para la segunda vuelta

2. Disociación Estructural Territorio–Población
   Kast domina el territorio (48,8% de comunas) pero obtiene menos votos (23,96%)
   Jara domina los centros poblacionales (30,3% de comunas) con más votos (26,75%)

3. Segmentación Norte–Centro–Sur Definida
   Norte (4 regiones): "Reino de Parisi" — voto antisistema / minero
   Centro + Patagonia (5 regiones): "Fortaleza de Jara" — izquierda urbana / institucional
   Centro-Sur (7 regiones): "Hegemonía de Kast" — derecha rural / tradicional

4. Brecha Urbano-Rural Extrema
   Jara gana 10/16 capitales regionales (62,5%) pero solo 5/16 regiones (31,3%)
   Kast gana 4/16 capitales (25,0%) pero 7/16 regiones (43,8%)

5. Ventaja Estructural Cuantificable para Kast en Segunda Vuelta
   Kast necesita 91,8% menos votos para recuperar territorio que Jara
   Eficiencia electoral: Kast requiere ~334 votos/comuna vs. ~420 de Jara

6. Parisi como Rey Maker Decisivo
   Monopolio norteño: 4 regiones con 27–35% de apoyo
   Dilema estratégico: Alianza con Jara (más natural) vs. Kast (más potente)
   Vulnerabilidad demográfica: Fuerza concentrada en ~3% del padrón nacional

7. Crisis Terminal de la Derecha Tradicional
   Matthei reducida a 4 comunas (1,2% del territorio, 12,44% de los votos)
   Kast absorbe comunas emblemáticas de la derecha (Lo Barnechea, etc.)

8. Sesgo Rural Estructural del Sistema Electoral
   Paradoja: Kast gana más comunas (169 vs. 105) pero menos votos (23,96% vs. 26,75%)
   1 comuna rural (1.000 hab.) = 1 comuna urbana (500.000 hab.) en peso político

9. Competitividad Extrema en Múltiples Niveles
   Diferencia nacional: 2,79% (~360.000 votos)
   134 comunas recuperables: margen menor a 1.000 votos entre Jara y Kast
   5 regiones bisagra con diferencia <3% determinan el resultado nacional

10. Alta Legitimidad Procesal, Déficit de Representación
    96,25% de votos válidos: Proceso considerado legítimo por la gran mayoría
    Nulo > Blanco (2,69% vs. 1,06%): El descontento es confrontacional, no pasivo
    Ningún candidato supera el 27%: Legitimidad del ganador inherentemente limitada
```

---

## Stack Tecnológico

| Componente | Detalle |
|---|---|
| Base de datos | SQL Server |
| Estilo de consultas | Basado en CTEs, modular |
| Técnicas utilizadas | Agregaciones, Funciones Ventana (`ROW_NUMBER`, `RANK`), pivoteo con `UNION ALL`, clasificación con `CASE WHEN` |
| Lenguaje complementario | Python (simulaciones de escenarios en `09_parisi_kingmaker.sql`) |
| Capa de extracción | Python + Selenium (ver `../Web Scraper/`) |

---

## Autor

**Alfonso Droguett** — Analista de Datos

- 🔗 [LinkedIn](https://www.linkedin.com/in/adroguetth/)
- 🌐 [Portafolio](https://www.adroguett-portfolio.cl/)
- 📧 [adroguett.consultor@gmail.com](mailto:adroguett.consultor@gmail.com)
- 🐙 [GitHub](https://github.com/adroguetth/)

---

*Última actualización: Enero 2026 (v2.0)*
