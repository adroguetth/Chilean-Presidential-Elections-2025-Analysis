-- =====================================================
-- 7. REGIONAL CAPITALS ANALYSIS
-- =====================================================
-- Objective: Analyze voting patterns in Chile's 16 regional capitals
-- Context: Compare capital city behavior against regional hinterlands
-- Database: SQL Server 2012+
-- Source table: resultados_elecciones (columns: commune, region, jara_pct, kast_pct, parisi_pct, kaiser_pct)

WITH capitales_regionales AS (
    SELECT
        commune AS capital,
        region,
        jara_pct,
        kast_pct,
        parisi_pct,
        kaiser_pct,
        CASE
            WHEN jara_pct >= kast_pct AND jara_pct >= parisi_pct AND jara_pct >= kaiser_pct
            THEN 'Jeannette Jara'
            WHEN kast_pct >= jara_pct AND kast_pct >= parisi_pct AND kast_pct >= kaiser_pct
            THEN 'José Antonio Kast'
            WHEN parisi_pct >= jara_pct AND parisi_pct >= kast_pct AND parisi_pct >= kaiser_pct
            THEN 'Franco Parisi'
            ELSE 'Johannes Kaiser'
        END AS ganador,
        CASE
            WHEN jara_pct >= kast_pct AND jara_pct >= parisi_pct AND jara_pct >= kaiser_pct THEN jara_pct
            WHEN kast_pct >= jara_pct AND kast_pct >= parisi_pct AND kast_pct >= kaiser_pct THEN kast_pct
            WHEN parisi_pct >= jara_pct AND parisi_pct >= kast_pct AND parisi_pct >= kaiser_pct THEN parisi_pct
            ELSE kaiser_pct
        END AS porcentaje_ganador
    FROM resultados_elecciones
    WHERE commune IN (
        'Arica', 'Iquique', 'Antofagasta', 'Copiapó', 'La Serena', 'Valparaíso',
        'Santiago', 'Rancagua', 'Talca', 'Chillán', 'Concepción', 'Temuco',
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
ORDER BY region;
