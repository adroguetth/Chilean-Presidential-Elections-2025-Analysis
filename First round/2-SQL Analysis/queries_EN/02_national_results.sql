-- =====================================================
-- 2. NATIONAL RESULTS BY CANDIDATE
-- =====================================================
-- Objective: Compute and classify each candidate's vote share nationally
-- Method: National aggregation + columnar-to-row structural transformation
-- Output: Candidates ranked by vote percentage with support-level classification

WITH suma_votos AS (
    -- CTE 1: National vote aggregation by candidate
    -- Purpose: Compute total valid votes and per-candidate vote totals
    -- Note: Valid votes exclude null and blank ballots
    SELECT
        -- CALCULATION: Total valid votes nationwide
        -- Formula: Ballots cast - Null votes - Blank votes
        (SUM(emitidos_votos) - SUM(nulo_votos) - SUM(blanco_votos)) AS total_votos_validos,

        -- AGGREGATIONS: National vote totals per candidate
        -- Each field holds the nationwide sum for a specific candidate
        SUM(artes_votos) AS artes_total,
        SUM(enriquez_ominami_votos) AS meo_total,
        SUM(jara_votos) AS jara_total,
        SUM(kaiser_votos) AS kaiser_total,
        SUM(kast_votos) AS kast_total,
        SUM(matthei_votos) AS matthei_total,
        SUM(parisi_votos) AS parisi_total,
        SUM(mayne_nicholls_votos) AS mayne_nicholls_total
    FROM resultados_elecciones
),
candidatos_votos AS (
    -- CTE 2: Unpivot candidate votes to (candidate, votes) row format
    -- Purpose: Normalize the wide columnar structure into rows for uniform processing
    -- Method: UNION ALL preserves all candidate records, including zero-vote cases
    SELECT 'Eduardo Artes' AS candidato, artes_total AS votos FROM suma_votos
    UNION ALL SELECT 'Marco Enriquez-Ominami', meo_total FROM suma_votos
    UNION ALL SELECT 'Jeannette Jara', jara_total FROM suma_votos
    UNION ALL SELECT 'Johannes Kaiser', kaiser_total FROM suma_votos
    UNION ALL SELECT 'José Antonio Kast', kast_total FROM suma_votos
    UNION ALL SELECT 'Evelyn Matthei', matthei_total FROM suma_votos
    UNION ALL SELECT 'Franco Parisi', parisi_total FROM suma_votos
    UNION ALL SELECT 'Harold Mayne-Nicholls', mayne_nicholls_total FROM suma_votos
)
-- FINAL QUERY: Percentage calculation and support-level classification
-- Purpose: Return results with vote shares and qualitative support tier
SELECT
    candidato,  -- Candidate name

    -- CALCULATION: Vote share over total valid votes
    -- Formula: (Candidate votes / Total valid votes) * 100
    -- Precision: Rounded to 2 decimal places
    ROUND(CAST(votos AS FLOAT) / (SELECT total_votos_validos FROM suma_votos) * 100, 2) AS votos_porcentaje,

    -- CLASSIFICATION: Categorical support level based on vote share
    -- Thresholds:
    --   - High support:   >= 20% of valid votes
    --   - Medium support: >= 10% and < 20% of valid votes
    --   - Low support:    <  10% of valid votes
    -- Purpose: Qualitative benchmarking of electoral performance
    CASE
        WHEN ROUND(CAST(votos AS FLOAT) / (SELECT total_votos_validos FROM suma_votos) * 100, 2) >= 20 THEN 'Alto apoyo'
        WHEN ROUND(CAST(votos AS FLOAT) / (SELECT total_votos_validos FROM suma_votos) * 100, 2) >= 10 THEN 'Medio apoyo'
        ELSE 'Bajo apoyo'
    END AS nivel_apoyo

FROM candidatos_votos
-- ORDER: Descending by vote percentage
-- Purpose: Rank candidates from highest to lowest vote share
ORDER BY votos_porcentaje DESC;
