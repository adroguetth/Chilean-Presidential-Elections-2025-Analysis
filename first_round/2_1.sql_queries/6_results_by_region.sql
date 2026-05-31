-- =====================================================
-- 6. RESULTS BY REGION (NORTH-SOUTH ORDER)
-- =====================================================
-- Objective: Calculate average vote shares and identify winners at regional level
-- Context: Reveal geographic voting patterns and regional strongholds
-- Database: SQL Server 2012+
-- Source table: first_round_2025 (columns: region, jara_pct, kast_pct, parisi_pct, kaiser_pct)

WITH resultados_region AS (
    SELECT
        region,
        CAST(ROUND(AVG(jara_pct), 2) AS DECIMAL(5,2)) AS jara_promedio,
        CAST(ROUND(AVG(kast_pct), 2) AS DECIMAL(5,2)) AS kast_promedio,
        CAST(ROUND(AVG(parisi_pct), 2) AS DECIMAL(5,2)) AS parisi_promedio,
        CAST(ROUND(AVG(kaiser_pct), 2) AS DECIMAL(5,2)) AS kaiser_promedio
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
        CAST(ROUND(
            CASE
                WHEN jara_promedio >= kast_promedio AND jara_promedio >= parisi_promedio AND jara_promedio >= kaiser_promedio 
                THEN jara_promedio
                WHEN kast_promedio >= jara_promedio AND kast_promedio >= parisi_promedio AND kast_promedio >= kaiser_promedio 
                THEN kast_promedio
                WHEN parisi_promedio >= jara_promedio AND parisi_promedio >= kast_promedio AND parisi_promedio >= kaiser_promedio 
                THEN parisi_promedio
                ELSE kaiser_promedio
            END, 2) AS DECIMAL(5,2)
        ) AS porcentaje_ganador
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
ORDER BY
    CASE region
        WHEN 'Arica y Parinacota' THEN 1
        WHEN 'Tarapacá' THEN 2
        WHEN 'Antofagasta' THEN 3
        WHEN 'Atacama' THEN 4
        WHEN 'Coquimbo' THEN 5
        WHEN 'Valparaíso' THEN 6
        WHEN 'Metropolitana' THEN 7
        WHEN 'Libertador' THEN 8
        WHEN 'Maule' THEN 9
        WHEN 'Ñuble' THEN 10
        WHEN 'Biobío' THEN 11
        WHEN 'La Araucanía' THEN 12
        WHEN 'Los Ríos' THEN 13
        WHEN 'Los Lagos' THEN 14
        WHEN 'Aysén' THEN 15
        WHEN 'Magallanes' THEN 16
        ELSE 99
    END;
