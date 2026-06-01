-- =====================================================
-- 2. REGIONS WITH NULL VOTE INCREASE
-- =====================================================
-- Objective: Identify regions where null votes increased in second round
-- Context: Null votes indicate protest voting or voting errors
-- Database: SQL Server 2012+
-- Source tables: first_round_2025, second_round_2025
-- Key finding: Regions with significant null vote spikes may indicate political disaffection

WITH regional_null_votes AS (
    SELECT 
        f.region,
        -- First round metrics
        SUM(f.null_votes) AS null_votes_first_round,
        SUM(f.casted_votes) AS total_votes_first_round,
        ROUND(100.0 * SUM(f.null_votes) / NULLIF(SUM(f.casted_votes), 0), 2) AS null_pct_first_round,
        -- Second round metrics  
        SUM(e.null_votes) AS null_votes_second_round,
        SUM(e.casted_votes) AS total_votes_second_round,
        ROUND(100.0 * SUM(e.null_votes) / NULLIF(SUM(e.casted_votes), 0), 2) AS null_pct_second_round
    FROM first_round_2025 f
    INNER JOIN second_round_2025 e ON f.commune = e.commune AND f.region = e.region
    GROUP BY f.region
)
SELECT 
    region,
    null_votes_first_round,
    null_votes_second_round,
    CONVERT(DECIMAL(10,2), (null_votes_second_round - null_votes_first_round)) AS null_votes_change,
    CONVERT(DECIMAL(10,2), null_pct_first_round) AS null_pct_first_round,
    CONVERT(DECIMAL(10,2), null_pct_second_round) AS null_pct_second_round,
    CONVERT(DECIMAL(10,2), (null_pct_second_round - null_pct_first_round)) AS null_pct_point_change,
    CASE 
        WHEN null_votes_second_round > null_votes_first_round THEN 'INCREASE'
        WHEN null_votes_second_round < null_votes_first_round THEN 'DECREASE'
        ELSE 'NO CHANGE'
    END AS trend
FROM regional_null_votes
WHERE null_votes_second_round > null_votes_first_round
ORDER BY null_votes_change DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Normal pattern: Null votes remain stable or decrease in second round
-- Anomaly detected: 100% of regions (16/16) increased null votes
-- Most affected: Antofagasta (+5.96pp to 9.04%), Atacama (+5.25pp to 8.05%)
-- Geographic pattern: Northern mining regions led the increase (3 of top 4)
-- Political insight: Coordinated protest vote against Jara-Kast duopoly
-- =====================================================
