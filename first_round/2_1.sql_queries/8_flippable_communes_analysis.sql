-- =====================================================
-- 8. FLIPPABLE COMMUNES ANALYSIS (MARGIN < 1,000 VOTES)
-- =====================================================
-- Objective: Identify communes where the Jara–Kast margin is under 1,000 votes
-- Method: Convert percentage shares to absolute votes + competitive margin analysis
-- Strategic context: These communes represent pivotal battlegrounds where small
--                   campaign-level shifts could flip the outcome in a runoff
-- Critical threshold: 1,000 votes (adjustable based on electoral context)
-- Database: SQL Server 2012+
-- Source table: resultados_elecciones (columns: commune, region, jara_pct, kast_pct,
--              blank_votes, null_votes, casted_votes)

WITH votos_comuna AS (
    SELECT
        commune AS comuna,
        region,
        (casted_votes - null_votes - blank_votes) AS votos_validos,
        jara_pct,
        kast_pct
    FROM resultados_elecciones
),
votos_absolutos AS (
    SELECT
        comuna,
        region,
        ROUND((jara_pct / 100.0) * votos_validos, 0) AS votos_jara,
        ROUND((kast_pct / 100.0) * votos_validos, 0) AS votos_kast,
        ABS(
            ROUND((jara_pct / 100.0) * votos_validos, 0) -
            ROUND((kast_pct / 100.0) * votos_validos, 0)
        ) AS diferencia_votos
    FROM votos_comuna
    WHERE jara_pct > 0 AND kast_pct > 0
),
analisis_jara AS (
    SELECT
        'Jeannette Jara' AS candidato_analizado,
        COUNT(*) AS comunas_recuperables,
        SUM(diferencia_votos) AS votos_necesarios_totales,
        ROUND(AVG(diferencia_votos), 0) AS promedio_votos_necesarios
    FROM votos_absolutos
    WHERE votos_kast > votos_jara AND diferencia_votos < 1000
),
analisis_kast AS (
    SELECT
        'José Antonio Kast' AS candidato_analizado,
        COUNT(*) AS comunas_recuperables,
        SUM(diferencia_votos) AS votos_necesarios_totales,
        ROUND(AVG(diferencia_votos), 0) AS promedio_votos_necesarios
    FROM votos_absolutos
    WHERE votos_jara > votos_kast AND diferencia_votos < 1000
)
SELECT
    candidato_analizado,
    comunas_recuperables,
    votos_necesarios_totales,
    promedio_votos_necesarios,
    CASE
        WHEN votos_necesarios_totales < 5000 THEN 'Minor challenge'
        WHEN votos_necesarios_totales < 20000 THEN 'Moderate challenge'
        ELSE 'Significant challenge'
    END AS difficulty_level
FROM (
    SELECT * FROM analisis_jara
    UNION ALL
    SELECT * FROM analisis_kast
) resultados
ORDER BY candidato_analizado;
