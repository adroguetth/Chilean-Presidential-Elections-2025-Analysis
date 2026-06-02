-- =====================================================
-- 5. TERRITORIAL MAPPING OF WINS PER CANDIDATE (SECOND ROUND)
-- =====================================================
-- Objective: Count how many communes each candidate won across the country
-- Context: Reveal territorial dominance and geographic fragmentation of vote
-- Database: SQL Server 2012+
-- Source table: second_round_2025 (columns: commune, region, jara_pct, kast_pct)

WITH ranked_communes AS (
    SELECT
        commune,
        region,
        jara_pct,
        kast_pct,
        -- Identify the candidate with the highest percentage in each commune
        CASE 
            WHEN jara_pct > kast_pct THEN 'Jeannette Jara'
            WHEN kast_pct > jara_pct THEN 'José Antonio Kast'
            WHEN jara_pct = kast_pct THEN 'Tie'
            ELSE 'No data'
        END AS winner_commune
    FROM second_round_2025
)
SELECT
    winner_commune AS candidate,
    COUNT(*) AS communes_won,
    ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM second_round_2025) * 100, 1) AS percentage_communes
FROM ranked_communes
WHERE winner_commune != 'Tie' AND winner_commune != 'No data'
GROUP BY winner_commune
ORDER BY communes_won DESC;

-- KEY FINDINGS:
-- =====================================================
-- Territorial dominance: Kast won 89.6% of communes (310 of 346)
-- Jara's strongholds: Only 36 communes (10.4%) voted for Jara
-- Disconnect between vote share and territory: 
--   - Kast: 58.24% of votes, 89.6% of communes
--   - Jara: 41.76% of votes, 10.4% of communes
-- =====================================================
