-- =====================================================
-- 5. TERRITORIAL WIN MAPPING BY CANDIDATE
-- =====================================================
-- Objective: Count communes won by each candidate
-- Method: Exhaustive per-commune winner determination (346 communes total)
-- Context: Maps the geographic distribution of electoral dominance across the territory

WITH victorias_por_candidato AS (
    -- CTE 1: Determine the winning candidate in each commune
    -- Purpose: Identify which candidate obtained the highest vote share per territory
    -- Method: Exhaustive percentage comparison across all candidates
    SELECT
        comuna,  -- Base territorial unit of analysis

        -- WINNER DETERMINATION LOGIC:
        -- Compares each candidate's percentage against all others
        -- The candidate with the highest share wins the commune
        -- Note: In the event of an exact tie, evaluation order determines the winner
        CASE
            -- JEANNETTE JARA: Wins if her share is >= all other candidates
            WHEN jara_pct >= kast_pct AND jara_pct >= parisi_pct AND jara_pct >= kaiser_pct
                 AND jara_pct >= matthei_pct AND jara_pct >= mayne_nicholls_pct
                 AND jara_pct >= enriquez_ominami_pct AND jara_pct >= artes_pct
            THEN 'Jeannette Jara'

            -- JOSÉ ANTONIO KAST: Wins if he outpolls every other candidate
            WHEN kast_pct >= jara_pct AND kast_pct >= parisi_pct AND kast_pct >= kaiser_pct
                 AND kast_pct >= matthei_pct AND kast_pct >= mayne_nicholls_pct
                 AND kast_pct >= enriquez_ominami_pct AND kast_pct >= artes_pct
            THEN 'José Antonio Kast'

            -- FRANCO PARISI: Wins if he holds the highest share
            WHEN parisi_pct >= jara_pct AND parisi_pct >= kast_pct AND parisi_pct >= kaiser_pct
                 AND parisi_pct >= matthei_pct AND parisi_pct >= mayne_nicholls_pct
                 AND parisi_pct >= enriquez_ominami_pct AND parisi_pct >= artes_pct
            THEN 'Franco Parisi'

            -- JOHANNES KAISER: Wins if he leads in the commune
            WHEN kaiser_pct >= jara_pct AND kaiser_pct >= kast_pct AND kaiser_pct >= parisi_pct
                 AND kaiser_pct >= matthei_pct AND kaiser_pct >= mayne_nicholls_pct
                 AND kaiser_pct >= enriquez_ominami_pct AND kaiser_pct >= artes_pct
            THEN 'Johannes Kaiser'

            -- EVELYN MATTHEI: Wins if she holds the highest share
            WHEN matthei_pct >= jara_pct AND matthei_pct >= kast_pct AND matthei_pct >= parisi_pct
                 AND matthei_pct >= kaiser_pct AND matthei_pct >= mayne_nicholls_pct
                 AND matthei_pct >= enriquez_ominami_pct AND matthei_pct >= artes_pct
            THEN 'Evelyn Matthei'

            -- FALLBACK: Candidates not included in the primary analysis
            -- Covers: Harold Mayne-Nicholls, Marco Enriquez-Ominami, Eduardo Artes
            ELSE 'Otro'
        END AS candidato_ganador  -- Result: Candidate who wins in this commune

    FROM resultados_elecciones  -- Source table: per-commune electoral results
)
-- FINAL QUERY: Aggregation and territorial win analysis
-- Purpose: Summarize communes won per candidate and their territorial coverage share
SELECT
    candidato_ganador AS candidato,       -- Candidate name or fallback category
    COUNT(*) AS comunas_ganadas,          -- Total communes won

    -- CALCULATION: Share of national territory controlled
    -- Formula: (Communes won / Total communes in Chile) * 100
    -- Reference total: 346 communes (current administrative division)
    -- Precision: One decimal place for territorial analysis
    ROUND(CAST(COUNT(*) AS FLOAT) / 346 * 100, 1) AS porcentaje_comunas

FROM victorias_por_candidato
-- GROUP BY: Candidate to consolidate per-candidate totals
GROUP BY candidato_ganador
-- ORDER: Descending by communes won
-- Purpose: Quickly identify the candidate with the broadest territorial reach
ORDER BY comunas_ganadas DESC;
