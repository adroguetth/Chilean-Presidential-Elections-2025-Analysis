-- =====================================================
-- 8. FLIPPABLE COMMUNES ANALYSIS (MARGIN < 1,000 VOTES)
-- =====================================================
-- Objective: Identify communes where the Jara–Kast margin is under 1,000 votes
-- Method: Convert percentage shares to absolute votes + competitive margin analysis
-- Strategic context: These communes represent pivotal battlegrounds where small
--                   campaign-level shifts could flip the outcome in a runoff
-- Critical threshold: 1,000 votes (adjustable based on electoral context)

WITH votos_comuna AS (
    -- CTE 1: PER-COMMUNE DATA PREPARATION
    -- Purpose: Compute valid votes per commune and prepare base dataset for analysis
    -- Note: Only valid votes are considered (blank and null ballots excluded)
    SELECT
        comuna,          -- Base territorial unit
        region,          -- Regional geographic context
        -- CALCULATION: Valid votes per commune
        -- Formula: Ballots cast - Null votes - Blank votes
        (emitidos_votos - nulo_votos - blanco_votos) AS votos_validos,
        jara_pct,        -- Jeannette Jara's vote share (range: 0–100)
        kast_pct         -- José Antonio Kast's vote share (range: 0–100)
    FROM resultados_elecciones
),
votos_absolutos AS (
    -- CTE 2: PERCENTAGE-TO-ABSOLUTE VOTE CONVERSION AND MARGIN CALCULATION
    -- Purpose: Transform percentage shares into absolute vote counts and compute margins
    -- Method: Percentage × Valid votes / 100
    SELECT
        comuna,
        region,
        -- CONVERSION: Percentages to absolute vote counts
        -- Jara: (percentage / 100) × valid votes
        ROUND((jara_pct / 100.0) * votos_validos, 0) AS votos_jara,
        -- Kast: (percentage / 100) × valid votes
        ROUND((kast_pct / 100.0) * votos_validos, 0) AS votos_kast,
        -- CALCULATION: Absolute vote margin between the two candidates
        -- Formula: |Jara votes - Kast votes|
        -- Purpose: Quantify how competitive the commune is
        ABS(
            ROUND((jara_pct / 100.0) * votos_validos, 0) -
            ROUND((kast_pct / 100.0) * votos_validos, 0)
        ) AS diferencia_votos
    FROM votos_comuna
    -- FILTER: Only communes where both candidates received votes (> 0%)
    -- Excludes communes where either candidate did not compete or scored 0
    WHERE jara_pct > 0 AND kast_pct > 0
),
analisis_jara AS (
    -- CTE 3: FLIPPABLE COMMUNE ANALYSIS FOR JEANNETTE JARA
    -- Purpose: Identify communes where Jara lost by fewer than 1,000 votes
    -- Context: Communes won by Kast with a narrow margin
    SELECT
        'Jeannette Jara' AS candidato_analizado,
        -- METRIC 1: Number of flippable communes
        COUNT(*) AS comunas_recuperables,
        -- METRIC 2: Total votes needed to reverse all losses
        -- If Jara captures these votes, she flips every listed commune
        SUM(diferencia_votos) AS votos_necesarios_totales,
        -- METRIC 3: Average votes needed per commune
        ROUND(AVG(diferencia_votos), 0) AS promedio_votos_necesarios
    FROM votos_absolutos
    WHERE
        -- CONDITION: Jara lost this commune
        votos_kast > votos_jara
        -- CONDITION: Margin is below the critical 1,000-vote threshold
        AND diferencia_votos < 1000
),
analisis_kast AS (
    -- CTE 4: FLIPPABLE COMMUNE ANALYSIS FOR JOSÉ ANTONIO KAST
    -- Purpose: Identify communes where Kast lost by fewer than 1,000 votes
    -- Context: Communes won by Jara with a narrow margin
    SELECT
        'José Antonio Kast' AS candidato_analizado,
        COUNT(*) AS comunas_recuperables,
        SUM(diferencia_votos) AS votos_necesarios_totales,
        ROUND(AVG(diferencia_votos), 0) AS promedio_votos_necesarios
    FROM votos_absolutos
    WHERE
        -- CONDITION: Kast lost this commune
        votos_jara > votos_kast
        -- CONDITION: Margin is below the critical 1,000-vote threshold
        AND diferencia_votos < 1000
)
-- FINAL QUERY: COMPARATIVE FLIPPABILITY REPORT
-- Purpose: Present strategic overview of recoverability for both runoff candidates
SELECT
    candidato_analizado,
    comunas_recuperables,
    -- INTERPRETATION: Total votes the candidate would need to mobilize or convert
    votos_necesarios_totales,
    -- INTERPRETATION: Average mobilization effort required per commune
    promedio_votos_necesarios,
    -- STRATEGIC ANALYSIS: Difficulty tier classification
    CASE
        WHEN votos_necesarios_totales < 5000 THEN 'Desafío menor'
        WHEN votos_necesarios_totales < 20000 THEN 'Desafío moderado'
        ELSE 'Desafío significativo'
    END AS nivel_dificultad
FROM (
    SELECT * FROM analisis_jara
    UNION ALL
    SELECT * FROM analisis_kast
) resultados
-- ORDER: Alphabetical by candidate name (Jara first, then Kast)
ORDER BY candidato_analizado;
