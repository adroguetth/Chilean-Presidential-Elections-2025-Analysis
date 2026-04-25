-- =====================================================
-- 6. RESULTS BY REGION - GEOGRAPHIC ANALYSIS
-- =====================================================
-- Objective: Identify regional vote patterns per candidate
-- Method: Regional aggregation + hierarchical winner determination
-- Context: Geographic distribution of votes across Chile's 16 administrative regions

WITH ResultadosPorRegion AS (
    -- CTE 1: RAW VOTE AGGREGATION BY REGION
    -- Purpose: Sum per-candidate votes and compute valid votes at regional level
    -- Method: Direct vote summation per candidate; valid votes derived from emitted totals
    SELECT
        region, -- Primary geographic grouping (16 regions in Chile)

        -- PER-CANDIDATE VOTE TOTALS AT REGIONAL LEVEL
        -- Base figures for precise regional percentage calculations
        SUM(jara_votos) AS jara_votos_regional,         -- Jeannette Jara
        SUM(kast_votos) AS kast_votos_regional,         -- José Antonio Kast
        SUM(parisi_votos) AS parisi_votos_regional,     -- Franco Parisi
        SUM(kaiser_votos) AS kaiser_votos_regional,     -- Johannes Kaiser
        SUM(matthei_votos) AS matthei_votos_regional,   -- Evelyn Matthei

        -- CALCULATION: Total valid votes per region
        -- Formula: Ballots cast - Blank votes - Null votes
        -- Legal basis: Law 18.700, Article 109 (definition of valid votes)
        SUM(emitidos_votos) - SUM(blanco_votos) - SUM(nulo_votos) AS votos_validos_regional

    FROM resultados_elecciones
    -- GROUP BY: Region to consolidate territorial results
    GROUP BY region  -- Produces 16 rows (one per administrative region)
),
porcentajes_region AS (
    -- CTE 2: REGIONAL PERCENTAGE CALCULATION
    -- Purpose: Derive regional vote shares from aggregated raw vote totals
    -- Method: Candidate regional votes divided by regional valid votes
    -- Formula: (Candidate regional votes / Regional valid votes) × 100
    SELECT
        region,  -- Region name

        -- REGIONAL VOTE SHARES: 2-decimal precision
        -- Transformation: From absolute vote counts to comparable percentages
        ROUND(CAST(jara_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS jara_porcentaje,
        ROUND(CAST(kast_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS kast_porcentaje,
        ROUND(CAST(parisi_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS parisi_porcentaje,
        ROUND(CAST(kaiser_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS kaiser_porcentaje,
        ROUND(CAST(matthei_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS matthei_porcentaje

    FROM ResultadosPorRegion
    -- Note: Retains all 16 original rows, now expressed as percentages
)
-- FINAL QUERY: REGIONAL WINNER DETERMINATION WITH VOTE SHARES
-- Purpose: Identify the leading candidate in each region with precise percentage data
SELECT
    region,  -- Region name (16 administrative regions)

    -- REGIONAL WINNER DETERMINATION:
    -- Logic: Candidate with the highest regional share wins the region
    -- Method: Exhaustive comparison of percentages (each candidate vs all others)
    -- Note: In the event of an exact tie, evaluation order determines the winner
    CASE
        -- JEANNETTE JARA: Wins if her share is >= all other candidates
        WHEN jara_porcentaje >= kast_porcentaje
             AND jara_porcentaje >= parisi_porcentaje
             AND jara_porcentaje >= kaiser_porcentaje
             AND jara_porcentaje >= matthei_porcentaje
        THEN 'Jeannette Jara'

        -- JOSÉ ANTONIO KAST: Wins if he outpolls every other candidate
        WHEN kast_porcentaje >= jara_porcentaje
             AND kast_porcentaje >= parisi_porcentaje
             AND kast_porcentaje >= kaiser_porcentaje
             AND kast_porcentaje >= matthei_porcentaje
        THEN 'José Antonio Kast'

        -- FRANCO PARISI: Wins if he holds the highest share
        WHEN parisi_porcentaje >= jara_porcentaje
             AND parisi_porcentaje >= kast_porcentaje
             AND parisi_porcentaje >= kaiser_porcentaje
             AND parisi_porcentaje >= matthei_porcentaje
        THEN 'Franco Parisi'

        -- JOHANNES KAISER: Wins if he leads the region
        WHEN kaiser_porcentaje >= jara_porcentaje
             AND kaiser_porcentaje >= kast_porcentaje
             AND kaiser_porcentaje >= parisi_porcentaje
             AND kaiser_porcentaje >= matthei_porcentaje
        THEN 'Johannes Kaiser'

        -- EVELYN MATTHEI: Wins if she holds the highest share
        -- Evaluated last per established precedence order
        ELSE 'Evelyn Matthei'

    END AS ganador_regional,  -- Result: Candidate with the highest regional support

    -- SUPPORTING DATA: Regional vote shares for all candidates
    -- Purpose: Enable comparative analysis of relative strength across regions
    -- Format: Percentages with 2 decimal places; base = regional valid votes
    jara_porcentaje,      -- Jeannette Jara's electoral strength in the region
    kast_porcentaje,      -- José Antonio Kast's electoral strength in the region
    parisi_porcentaje,    -- Franco Parisi's electoral strength in the region
    kaiser_porcentaje,    -- Johannes Kaiser's electoral strength in the region
    matthei_porcentaje    -- Evelyn Matthei's electoral strength in the region

FROM porcentajes_region

-- ORDER: By region from north to south
-- Purpose: Geographically coherent visualization reflecting Chile's territorial layout
-- Method: Sequential integer mapping based on north-to-south geographic position
-- Benefit: Enables identification of political patterns and gradients across the national territory
ORDER BY
    CASE region
        WHEN 'Arica y Parinacota' THEN 1   -- Northernmost region
        WHEN 'Tarapacá' THEN 2
        WHEN 'Antofagasta' THEN 3
        WHEN 'Atacama' THEN 4
        WHEN 'Coquimbo' THEN 5
        WHEN 'Valparaíso' THEN 6
        WHEN 'Metropolitana' THEN 7        -- Central region
        WHEN 'Libertador' THEN 8
        WHEN 'Maule' THEN 9
        WHEN 'Ñuble' THEN 10
        WHEN 'Biobío' THEN 11
        WHEN 'La Araucanía' THEN 12
        WHEN 'Los Ríos' THEN 13
        WHEN 'Los Lagos' THEN 14
        WHEN 'Aysén' THEN 15
        WHEN 'Magallanes' THEN 16          -- Southernmost region
        ELSE 99  -- Fallback for any unexpected region value
    END;
