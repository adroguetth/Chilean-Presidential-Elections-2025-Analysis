-- =====================================================
-- 6. RESULTS BY REGION
-- =====================================================
-- Objective: Calculate average vote shares and identify winners at regional level
-- Context: Reveal geographic voting patterns and regional strongholds
-- Database: SQL Server 2012+
-- Source table: first_round_2025 (columns: region, jara_pct, kast_pct, parisi_pct, kaiser_pct)

WITH resultados_region AS (
    SELECT
        region,
        ROUND(AVG(jara_pct), 2) AS jara_promedio,
        ROUND(AVG(kast_pct), 2) AS kast_promedio,
        ROUND(AVG(parisi_pct), 2) AS parisi_promedio,
        ROUND(AVG(kaiser_pct), 2) AS kaiser_promedio
    FROM first_round_2025
    GROUP BY region
),
ganadores_region AS (
    SELECT
        region,
        jara_promedio,
        kast_promedio,
        parisi_promedio,
        kaiser_promedio,
        CASE
            WHEN jara_promedio >= kast_promedio AND jara_promedio >= parisi_promedio AND jara_promedio >= kaiser_promedio 
            THEN 'Jeannette Jara'
            WHEN kast_promedio >= jara_promedio AND kast_promedio >= parisi_promedio AND kast_promedio >= kaiser_promedio 
            THEN 'José Antonio Kast'
            WHEN parisi_promedio >= jara_promedio AND parisi_promedio >= kast_promedio AND parisi_promedio >= kaiser_promedio 
            THEN 'Franco Parisi'
            ELSE 'Johannes Kaiser'
        END AS ganador,
        CASE
            WHEN jara_promedio >= kast_promedio AND jara_promedio >= parisi_promedio AND jara_promedio >= kaiser_promedio 
            THEN jara_promedio
            WHEN kast_promedio >= jara_promedio AND kast_promedio >= parisi_promedio AND kast_promedio >= kaiser_promedio 
            THEN kast_promedio
            WHEN parisi_promedio >= jara_promedio AND parisi_promedio >= kast_promedio AND parisi_promedio >= kaiser_promedio 
            THEN parisi_promedio
            ELSE kaiser_promedio
        END AS porcentaje_ganador
    FROM resultados_region
)
SELECT
    region,
    ganador,
    porcentaje_ganador,
    jara_promedio,
    kast_promedio,
    parisi_promedio,
    kaiser_promedio
FROM ganadores_region
ORDER BY porcentaje_ganador DESC;
