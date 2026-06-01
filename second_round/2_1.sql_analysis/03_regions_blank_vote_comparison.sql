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
-- Blank votes increased in 11 regions, decreased in 5 regions (Maule, La Araucanía, 
-- Ñuble, Los Lagos, Aysén). Largest increase: Metropolitana (+15,674 votes, +0.31pp).
-- Largest decrease: Maule (-1,308 votes, -0.15pp). Unlike null votes which increased 
-- universally (16/16 regions), blank votes showed regional variation.
-- 
-- CONCLUSION:
-- Blank votes increased in 11 of 16 regions (69%), contrasting with null votes which
-- increased in all 16 regions (100%). The Metropolitana region contributed nearly half
-- (47%) of the national blank vote increase. Five southern/central-south regions 
-- (Maule, La Araucanía, Ñuble, Los Lagos, Aysén) actually reduced blank votes, 
-- suggesting voters there shifted from blank to null as their preferred protest 
-- mechanism against the Jara-Kast duopoly.
-- =====================================================
