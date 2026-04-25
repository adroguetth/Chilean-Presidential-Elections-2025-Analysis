-- =====================================================
-- 3. RUNOFF QUALIFICATION - TOP TWO CANDIDATES
-- =====================================================
-- Objective: Identify the two highest-polling candidates under Chilean electoral law
-- Method: Percentage calculated over valid votes (excludes null and blank ballots)
-- Legal basis: Law 18.700 - Two-round electoral system
-- Criterion: The two candidates with the highest share of valid votes advance to the runoff

WITH suma_votos AS (
    -- CTE 1: National vote aggregation by candidate
    -- Purpose: Compute total valid votes and individual per-candidate totals
    -- Note: Chilean electoral law considers only valid votes for runoff determination
    SELECT
        -- CALCULATION: Total valid votes nationwide
        -- Formula: Ballots cast - Null votes - Blank votes
        -- Legal basis: Law 18.700, Article 109
        SUM(emitidos_votos) - SUM(nulo_votos) - SUM(blanco_votos) AS total_votos_validos,

        -- AGGREGATIONS: National vote totals per presidential candidate
        -- Order: Candidates listed in the same sequence as the original source schema
        SUM(jara_votos) AS jara_total,
        SUM(kast_votos) AS kast_total,
        SUM(parisi_votos) AS parisi_total,
        SUM(kaiser_votos) AS kaiser_total,
        SUM(matthei_votos) AS matthei_total,
        SUM(mayne_nicholls_votos) AS mayne_nicholls_total,
        SUM(enriquez_ominami_votos) AS meo_total,
        SUM(artes_votos) AS artes_total
    FROM resultados_elecciones
),
porcentajes_candidatos AS (
    -- CTE 2: Per-candidate percentage calculation
    -- Purpose: Compute each candidate's share of valid votes
    -- Method: Individual SELECT per candidate joined via UNION ALL
    -- Formula: (Candidate votes / Total valid votes) * 100
    SELECT
        'Jeannette Jara' AS candidato,
        ROUND(CAST(jara_total AS FLOAT) / total_votos_validos * 100, 2) AS porcentaje
    FROM suma_votos

    UNION ALL  -- Retains all rows including potential duplicates (none expected here)

    SELECT
        'José Antonio Kast',
        ROUND(CAST(kast_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Franco Parisi',
        ROUND(CAST(parisi_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Johannes Kaiser',
        ROUND(CAST(kaiser_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Evelyn Matthei',
        ROUND(CAST(matthei_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Harold Mayne-Nicholls',
        ROUND(CAST(mayne_nicholls_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Marco Enriquez-Ominami',
        ROUND(CAST(meo_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Eduardo Artes',
        ROUND(CAST(artes_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
),
ranking_candidatos AS (
    -- CTE 3: Rank candidates by descending vote share
    -- Purpose: Sort candidates and assign sequential position (1 = highest vote share)
    -- Method: ROW_NUMBER() for strict ranking with no ties
    -- Note: In the event of an exact tie, rank is determined by UNION ALL sequence order
    SELECT
        candidato,
        porcentaje,
        ROW_NUMBER() OVER (ORDER BY porcentaje DESC) AS posicion  -- Descending rank
    FROM porcentajes_candidatos
)
-- FINAL QUERY: Runoff qualification with competitive context
-- Purpose: Return the top two candidates with their vote share and competitiveness label
-- Selection criterion: WHERE posicion <= 2 (1st and 2nd place)
SELECT
    candidato,  -- Candidate name
    porcentaje,  -- Share of valid votes obtained

    -- CLASSIFICATION: Ordinal position in the electoral ranking
    -- Purpose: Explicitly label first- and second-place finishers
    CASE
        WHEN posicion = 1 THEN '1er Lugar'
        WHEN posicion = 2 THEN '2do Lugar'
    END AS posicion,

    -- ANALYSIS: Competitive context of the result
    -- Purpose: Qualitative interpretation of the obtained percentage
    -- Thresholds:
    --   - Absolute majority: > 50% (eliminates runoff under electoral law)
    --   - Competitive threshold: > 20% (considered a strong first-round result)
    --   - Minimum threshold: <= 20% (weak first-round performance)
    -- Legal basis: Law 18.700, Article 110 (absolute majority rule)
    CASE
        WHEN porcentaje > 50 THEN 'Mayoría absoluta (Sin 2da vuelta)'
        WHEN porcentaje > 20 THEN 'Umbral competitivo'
        ELSE 'Umbral mínimo'
    END AS contexto_competitividad

FROM ranking_candidatos
-- FILTER: Restrict to top two candidates only
-- Purpose: Identify who advances to the second round
WHERE posicion <= 2
-- ORDER: Ascending by rank position (1st then 2nd)
-- Purpose: Present runoff qualifiers in podium order
ORDER BY posicion;
