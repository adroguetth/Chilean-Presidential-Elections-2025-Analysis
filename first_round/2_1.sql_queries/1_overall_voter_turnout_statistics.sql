-- =====================================================
-- 1. OVERALL VOTER TURNOUT STATISTICS
-- =====================================================
-- Objective: Compute core voter participation metrics
-- Context: Foundational dataset for all subsequent analyses
-- Database: SQL Server 2012+
-- Source table: resultados_elecciones (columns: blank_votes, null_votes, casted_votes)

WITH participacion_nacional AS (
SELECT
    COUNT(*) AS total_comunas,
    SUM(casted_votes) AS total_votos_emitidos,
    SUM(blank_votes) AS total_votos_blancos,
    SUM(null_votes) AS total_votos_nulos,
    SUM(casted_votes) - (SUM(blank_votes) + SUM(null_votes)) AS total_votos_validos
FROM first_round_2025
)
SELECT 'Total comunas' AS indicador, total_comunas AS valor FROM participacion_nacional
UNION ALL
SELECT 'Total votos emitidos', total_votos_emitidos FROM participacion_nacional
UNION ALL
SELECT 'Total votos blancos', total_votos_blancos FROM participacion_nacional
UNION ALL
SELECT 'Porcentaje votos blancos',
       ROUND(CAST(total_votos_blancos AS FLOAT) / total_votos_emitidos * 100, 2)
FROM participacion_nacional
UNION ALL
SELECT 'Total votos nulos', total_votos_nulos FROM participacion_nacional
UNION ALL
SELECT 'Porcentaje votos nulos',
       ROUND(CAST(total_votos_nulos AS FLOAT) / total_votos_emitidos * 100, 2)
FROM participacion_nacional
UNION ALL
SELECT 'Total votos válidos', total_votos_validos FROM participacion_nacional
UNION ALL
SELECT 'Porcentaje votos válidos',
       ROUND(CAST(total_votos_validos AS FLOAT) / total_votos_emitidos * 100, 2)
FROM participacion_nacional;
