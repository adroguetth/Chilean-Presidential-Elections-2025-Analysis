-- =====================================================
-- 14. COMMUNES WHERE KAST LOST VOTES (1ST ROUND → 2ND ROUND)
-- =====================================================
-- Objective: Identify communes where Kast received fewer votes in 2nd round than 1st
-- Context: Reveals zones of voter defection or resistance to Kast
-- Database: SQL Server 2012+
-- Source tables: first_round_2025, second_round_2025

WITH kast_lost AS (
    SELECT
        f.commune,
        f.region,
        f.kast_votes AS kast_votes_1v,
        s.kast_votes AS kast_votes_2v,
        f.kast_pct AS kast_pct_1v,
        s.kast_pct AS kast_pct_2v,
        -- Vote difference
        (s.kast_votes - f.kast_votes) AS kast_vote_diff,
        -- Percentage point difference
        ROUND(s.kast_pct - f.kast_pct, 2) AS kast_pct_diff_pp,
        -- Which candidate won the commune in 2nd round?
        CASE 
            WHEN s.kast_pct > s.jara_pct THEN 'Kast'
            ELSE 'Jara'
        END AS winner_2v
    FROM first_round_2025 f
    INNER JOIN second_round_2025 s ON f.commune = s.commune
    WHERE s.kast_votes < f.kast_votes  -- Kast received FEWER votes in 2nd round
)
SELECT 
    commune,
    region,
    kast_votes_1v,
    kast_votes_2v,
    kast_vote_diff,
    CAST(kast_pct_1v AS DECIMAL(5,2)) AS kast_pct_1v,
    CAST(kast_pct_2v AS DECIMAL(5,2)) AS kast_pct_2v,
    CAST(kast_pct_diff_pp AS DECIMAL(5,2)) AS kast_pct_diff_pp,
    winner_2v
FROM kast_lost
ORDER BY kast_vote_diff ASC;  -- Most negative first (biggest losses)

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Kast experienced a decrease in absolute votes in several communes between the 
-- first and second round, with Antártica (Magallanes) being a notable example 
-- (-18 votes, from 35 to 17).

-- Key Observations:
-- - Most communes where Kast lost absolute votes are small or very low-population 
--   territories (such as Antarctic bases, isolated islands, or remote rural areas).
-- - In many cases, even though absolute votes decreased, Kast's **percentage increased**, 
--   indicating that his supporters were more loyal than the overall turnout.
-- - The drop in total votes cast in the second round explains much of this phenomenon.

-- Political Significance:
-- - These losses are marginal and concentrated in low-impact communes (very few voters).
-- - They do not represent a significant defection from Kast's base, but rather a 
--   general decline in participation in remote areas.
-- - This reinforces Kast's strong loyalty among his core voters, even in territories 
--   with lower mobilization in the runoff.
-- =====================================================
