-- =====================================================
-- 7. REGIONAL CAPITALS ANALYSIS (NORTH-SOUTH ORDER)
-- =====================================================
-- Objective: Analyze voting patterns in Chile's 16 regional capitals
-- Context: Compare capital city behavior against regional hinterlands
-- Database: SQL Server 2012+
-- Source table: first_round_2025 (columns: commune, region, jara_pct, kast_pct, parisi_pct, kaiser_pct)

WITH capitales_regionales AS (
    SELECT
        commune AS capital,
        region,
        CAST(ROUND(jara_pct, 2) AS DECIMAL(5,2)) AS jara_pct,
        CAST(ROUND(kast_pct, 2) AS DECIMAL(5,2)) AS kast_pct,
        CAST(ROUND(parisi_pct, 2) AS DECIMAL(5,2)) AS parisi_pct,
        CAST(ROUND(kaiser_pct, 2) AS DECIMAL(5,2)) AS kaiser_pct,
        CASE
            WHEN jara_pct >= kast_pct AND jara_pct >= parisi_pct AND jara_pct >= kaiser_pct
            THEN 'Jeannette Jara'
            WHEN kast_pct >= jara_pct AND kast_pct >= parisi_pct AND kast_pct >= kaiser_pct
            THEN 'José Antonio Kast'
            WHEN parisi_pct >= jara_pct AND parisi_pct >= kast_pct AND parisi_pct >= kaiser_pct
            THEN 'Franco Parisi'
            ELSE 'Johannes Kaiser'
        END AS ganador,
        CAST(ROUND(
            CASE
                WHEN jara_pct >= kast_pct AND jara_pct >= parisi_pct AND jara_pct >= kaiser_pct THEN jara_pct
                WHEN kast_pct >= jara_pct AND kast_pct >= parisi_pct AND kast_pct >= kaiser_pct THEN kast_pct
                WHEN parisi_pct >= jara_pct AND parisi_pct >= kast_pct AND parisi_pct >= kaiser_pct THEN parisi_pct
                ELSE kaiser_pct
            END, 2) AS DECIMAL(5,2)
        ) AS porcentaje_ganador
    FROM first_round_2025
    WHERE commune IN (
        'Arica', 'Iquique', 'Antofagasta', 'Copiapo', 'La Serena', 'Valparaiso',
        'Santiago', 'Rancagua', 'Talca', 'Chillan', 'Concepcion', 'Temuco',
        'Valdivia', 'Puerto Montt', 'Coyhaique', 'Punta Arenas'
    )
)
SELECT
    capital,
    region,
    ganador,
    porcentaje_ganador,
    jara_pct,
    kast_pct,
    parisi_pct,
    kaiser_pct
FROM capitales_regionales
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
