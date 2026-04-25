-- =====================================================
-- 7. RESULTS BY REGIONAL CAPITAL - URBAN CENTER ANALYSIS
-- =====================================================
-- Objective: Analyze electoral behavior in Chile's 16 regional capitals
-- Method: Filter on capital communes + comparative winner analysis
-- Context: Regional capitals concentrate approximately 65-70% of the national population

WITH CapitalesRegionales AS (
    -- CTE 1: REGIONAL CAPITAL FILTER
    -- Purpose: Select the 16 communes that serve as regional administrative capitals
    -- Criterion: Explicit allowlist of Chile's administrative capitals
    -- Note: Covers all regions from Arica in the north to Magallanes in the south
    SELECT
        comuna,          -- Regional capital name
        region,          -- Corresponding region
        jara_pct,        -- Jeannette Jara's vote share
        kast_pct,        -- José Antonio Kast's vote share
        parisi_pct,      -- Franco Parisi's vote share
        kaiser_pct,      -- Johannes Kaiser's vote share
        matthei_pct      -- Evelyn Matthei's vote share
    FROM resultados_elecciones
    WHERE comuna IN (
        'Arica',           -- ARICA Y PARINACOTA REGION
        'Iquique',         -- TARAPACÁ REGION
        'Antofagasta',     -- ANTOFAGASTA REGION
        'Copiapo',         -- ATACAMA REGION
        'La Serena',       -- COQUIMBO REGION
        'Valparaiso',      -- VALPARAÍSO REGION
        'Santiago',        -- METROPOLITAN REGION
        'Rancagua',        -- LIBERTADOR BERNARDO O'HIGGINS REGION
        'Talca',           -- MAULE REGION
        'Chillan',         -- ÑUBLE REGION
        'Concepcion',      -- BIOBÍO REGION
        'Temuco',          -- LA ARAUCANÍA REGION
        'Valdivia',        -- LOS RÍOS REGION
        'Puerto Montt',    -- LOS LAGOS REGION
        'Coyhaique',       -- AYSÉN REGION
        'Punta Arenas'     -- MAGALLANES REGION
    )
),
GanadoresCapitales AS (
    -- CTE 2: WINNER DETERMINATION PER REGIONAL CAPITAL
    -- Purpose: Identify which candidate won in each regional capital
    -- Logic: Hierarchical comparison across the 5 most electorally relevant urban candidates
    SELECT
        comuna,
        region,
        jara_pct,
        kast_pct,
        parisi_pct,
        kaiser_pct,
        matthei_pct,

        -- WINNING CANDIDATE DETERMINATION
        -- Evaluation order based on national performance and observed urban patterns
        CASE
            -- JEANNETTE JARA: Strong in major metropolitan urban areas
            WHEN jara_pct >= kast_pct
                 AND jara_pct >= parisi_pct
                 AND jara_pct >= kaiser_pct
                 AND jara_pct >= matthei_pct
            THEN 'Jeannette Jara'

            -- JOSÉ ANTONIO KAST: Strong in some southern capitals and rural-adjacent areas
            WHEN kast_pct >= jara_pct
                 AND kast_pct >= parisi_pct
                 AND kast_pct >= kaiser_pct
                 AND kast_pct >= matthei_pct
            THEN 'José Antonio Kast'

            -- FRANCO PARISI: Surprisingly strong in northern capitals and mining areas
            WHEN parisi_pct >= jara_pct
                 AND parisi_pct >= kast_pct
                 AND parisi_pct >= kaiser_pct
                 AND parisi_pct >= matthei_pct
            THEN 'Franco Parisi'

            -- JOHANNES KAISER: Expected strength in Patagonian capitals and urban niches
            WHEN kaiser_pct >= jara_pct
                 AND kaiser_pct >= kast_pct
                 AND kaiser_pct >= parisi_pct
                 AND kaiser_pct >= matthei_pct
            THEN 'Johannes Kaiser'

            -- EVELYN MATTHEI: Competitive in high-income regional capitals
            ELSE 'Evelyn Matthei'

        END as ganador,  -- Winning candidate in the regional capital

        -- WINNER'S VOTE SHARE
        -- Mirrors the winner-determination logic to extract the corresponding numeric value
        CASE
            -- JEANNETTE JARA
            WHEN jara_pct >= kast_pct
                 AND jara_pct >= parisi_pct
                 AND jara_pct >= kaiser_pct
                 AND jara_pct >= matthei_pct
            THEN jara_pct

            -- JOSÉ ANTONIO KAST
            WHEN kast_pct >= jara_pct
                 AND kast_pct >= parisi_pct
                 AND kast_pct >= kaiser_pct
                 AND kast_pct >= matthei_pct
            THEN kast_pct

            -- FRANCO PARISI
            WHEN parisi_pct >= jara_pct
                 AND parisi_pct >= kast_pct
                 AND parisi_pct >= kaiser_pct
                 AND parisi_pct >= matthei_pct
            THEN parisi_pct

            -- JOHANNES KAISER
            WHEN kaiser_pct >= jara_pct
                 AND kaiser_pct >= kast_pct
                 AND kaiser_pct >= parisi_pct
                 AND kaiser_pct >= matthei_pct
            THEN kaiser_pct

            -- EVELYN MATTHEI
            ELSE matthei_pct

        END AS porcentaje_ganador  -- Vote share obtained by the winner
    FROM CapitalesRegionales
)
-- FINAL QUERY: URBAN ELECTORAL LANDSCAPE BY REGION
-- Purpose: Display the political map of Chile's regional capitals
-- Order: Geographic north-to-south following administrative sequence
SELECT
    comuna AS capital_regional,      -- Capital name
    region,                          -- Corresponding region
    ganador,                         -- Winning candidate
    porcentaje_ganador,              -- Winner's vote share
    jara_pct,                        -- Jeannette Jara's vote share
    kast_pct,                        -- José Antonio Kast's vote share
    parisi_pct,                      -- Franco Parisi's vote share
    kaiser_pct,                      -- Johannes Kaiser's vote share
    matthei_pct                      -- Evelyn Matthei's vote share
FROM GanadoresCapitales
-- ORDER: By region from north to south
-- Purpose: Geographically coherent presentation
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
