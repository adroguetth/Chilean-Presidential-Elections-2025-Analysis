-- =====================================================
-- 1. OVERALL VOTER TURNOUT STATISTICS
-- =====================================================
-- Objective: Compute core voter participation metrics
-- Context: Foundational dataset for all subsequent analyses

WITH participacion_nacional AS (
-- CTE 1: National-level aggregation of electoral results
-- Purpose: Consolidate baseline turnout metrics across the entire territory
-- Note: This CTE is the dependency for all downstream percentage calculations
SELECT
    -- METRIC 1: GEOGRAPHIC COVERAGE OF THE ANALYSIS
    -- Represents 100% of the national electoral territory
    -- Unit: number of communes
    COUNT(*) AS total_comunas,

    -- METRIC 2: ABSOLUTE VOTER PARTICIPATION
    -- Total ballots cast (denominator for all percentage calculations)
    -- Unit: number of votes
    SUM(emitidos_votos) AS total_votos_emitidos,

    -- METRIC 3: PASSIVE PROTEST VOTE
    -- Blank ballots: dissent not directed at any candidate
    -- Unit: number of votes
    SUM(blanco_votos) AS total_votos_blancos,

    -- METRIC 4: ACTIVE PROTEST VOTE
    -- Null/spoiled ballots: explicit rejection of the electoral system
    -- Unit: number of votes
    SUM(nulo_votos) AS total_votos_nulos,

    -- METRIC 5: VALID VOTES (DERIVED)
    -- Difference between total cast and (blank + null)
    -- Represents ballots effectively assigned to a candidate
    -- Unit: number of votes
    SUM(emitidos_votos) - (SUM(blanco_votos) + SUM(nulo_votos)) AS total_votos_validos
FROM resultados_elecciones  -- Source table: electoral results per commune
),
Estadisticas AS (
-- CTE 2: Pivot aggregated metrics into indicator-value format
-- Purpose: Transform wide aggregate row into a normalized two-column reporting structure
-- Output schema: (indicator VARCHAR, valor FLOAT)
SELECT 'Total comunas' AS indicador, total_comunas AS valor FROM participacion_nacional
UNION ALL
SELECT 'Total votos emitidos', total_votos_emitidos FROM participacion_nacional
UNION ALL
SELECT 'Total votos blancos', total_votos_blancos FROM participacion_nacional
UNION ALL
-- DERIVED METRIC 1: Blank vote share over total ballots cast
-- Interpretation: Proportion of voters who exercised passive protest
SELECT 'Porcentaje votos blancos',
       ROUND(CAST(total_votos_blancos AS FLOAT) / total_votos_emitidos * 100, 2)
       FROM participacion_nacional
UNION ALL
SELECT 'Total votos nulos', total_votos_nulos FROM participacion_nacional
UNION ALL
-- DERIVED METRIC 2: Null vote share over total ballots cast
-- Interpretation: Proportion of voters who exercised active protest
SELECT 'Porcentaje votos nulos',
       ROUND(CAST(total_votos_nulos AS FLOAT) / total_votos_emitidos * 100, 2)
       FROM participacion_nacional
UNION ALL
SELECT 'Total votos válidos', total_votos_validos FROM participacion_nacional
UNION ALL
-- DERIVED METRIC 3: Valid vote share over total ballots cast
-- Interpretation: Proportion of ballots that were effectively allocated to candidates
-- Note: This is the key indicator of effective participation in the election
SELECT 'Porcentaje votos válidos',
       ROUND(CAST(total_votos_validos AS FLOAT) / total_votos_emitidos * 100, 2)
       FROM participacion_nacional
)
-- FINAL QUERY: Report output
-- Purpose: Return all turnout metrics in report-ready format
-- Row order: Defined by insertion sequence in the Estadisticas CTE
SELECT * FROM Estadisticas;
