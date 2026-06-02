-- =====================================================
-- 3. REGIONS WITH BLANK VOTE COMPARISON
-- =====================================================
-- Objective: Compare blank votes across all regions (increase AND decrease)
-- Context: Blank votes indicate intentional vote nullification or protest
-- Database: SQL Server 2012+
-- Source tables: first_round_2025, second_round_2025

WITH regional_blank_votes AS (
    SELECT 
        f.region,
        -- First round metrics
        SUM(f.blank_votes) AS blank_votes_first_round,
        SUM(f.casted_votes) AS total_votes_first_round,
        ROUND(100.0 * SUM(f.blank_votes) / NULLIF(SUM(f.casted_votes), 0), 2) AS blank_pct_first_round,
        -- Second round metrics  
        SUM(e.blank_votes) AS blank_votes_second_round,
        SUM(e.casted_votes) AS total_votes_second_round,
        ROUND(100.0 * SUM(e.blank_votes) / NULLIF(SUM(e.casted_votes), 0), 2) AS blank_pct_second_round
    FROM first_round_2025 f
    INNER JOIN second_round_2025 e ON f.commune = e.commune AND f.region = e.region
    GROUP BY f.region
)
SELECT 
    region,
    blank_votes_first_round,
    blank_votes_second_round,
    CONVERT(DECIMAL(10,2), (blank_votes_second_round - blank_votes_first_round)) AS blank_votes_change,
    CONVERT(DECIMAL(10,2), blank_pct_first_round) AS blank_pct_first_round,
    CONVERT(DECIMAL(10,2), blank_pct_second_round) AS blank_pct_second_round,
    CONVERT(DECIMAL(10,2), (blank_pct_second_round - blank_pct_first_round)) AS blank_pct_point_change,
    CASE 
        WHEN blank_votes_second_round > blank_votes_first_round THEN 'INCREASE'
        WHEN blank_votes_second_round < blank_votes_first_round THEN 'DECREASE'
        ELSE 'NO CHANGE'
    END AS trend
FROM regional_blank_votes
ORDER BY blank_votes_change DESC

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Blank votes increased in 11 out of 16 regions (69%), but showed more regional variation 
-- than null votes, which rose universally.
-- The Metropolitan Region led the increase both in absolute (+15,674 votes) and percentage 
-- point terms (+0.31 pp).
-- In contrast, five regions in the Center-South and South (Maule, La Araucanía, Ñuble, 
-- Los Lagos, and Aysén) actually reduced blank votes.
--
-- CONCLUSION:
-- While null votes surged across the entire country as a form of active protest, blank 
-- votes presented a more mixed pattern. The significant rise in the Metropolitan Region 
-- suggests higher passive discontent in urban centers, whereas some southern regions 
-- appear to have shifted from blank to null votes, indicating a more radicalized protest 
-- against the Jara-Kast duopoly.
-- =====================================================
