-- =====================================================
-- 1. COMPARATIVE VOTER TURNOUT: FIRST ROUND VS SECOND ROUND
-- =====================================================
-- Objective: Compare core voter participation metrics between both rounds
-- Context: Identifies anomalous turnout patterns (decrease in second round)
-- Database: SQL Server 2012+
-- Source tables: first_round_2025, second_round_2025
-- Key finding: Detects 500k+ valid vote drop anomaly

WITH first_round_statistics AS (
    SELECT
        COUNT(*) AS total_municipalities,
        SUM(casted_votes) AS total_votes_cast,
        SUM(blank_votes) AS total_blank_votes,
        SUM(null_votes) AS total_null_votes,
        SUM(casted_votes) - SUM(blank_votes) - SUM(null_votes) AS total_valid_votes
    FROM first_round_2025
),
second_round_statistics AS (
    SELECT
        COUNT(*) AS total_municipalities,
        SUM(casted_votes) AS total_votes_cast,
        SUM(blank_votes) AS total_blank_votes,
        SUM(null_votes) AS total_null_votes,
        SUM(casted_votes) - SUM(blank_votes) - SUM(null_votes) AS total_valid_votes
    FROM second_round_2025
)
SELECT 
    'Total municipalities' AS indicator,
    f.total_municipalities AS first_round,
    e.total_municipalities AS second_round,
    e.total_municipalities - f.total_municipalities AS diff,
    CASE 
        WHEN e.total_municipalities > f.total_municipalities THEN 'INCREASE'
        WHEN e.total_municipalities < f.total_municipalities THEN 'DECREASE'
        ELSE 'NO CHANGE'
    END AS trend
FROM first_round_statistics f
CROSS JOIN second_round_statistics e

UNION ALL

SELECT 
    'Votes cast' AS indicator,
    f.total_votes_cast,
    e.total_votes_cast,
    e.total_votes_cast - f.total_votes_cast,
    CASE 
        WHEN e.total_votes_cast > f.total_votes_cast THEN 'INCREASE'
        WHEN e.total_votes_cast < f.total_votes_cast THEN 'DECREASE'
        ELSE 'NO CHANGE'
    END
FROM first_round_statistics f
CROSS JOIN second_round_statistics e

UNION ALL

SELECT 
    'Blank votes' AS indicator,
    f.total_blank_votes,
    e.total_blank_votes,
    e.total_blank_votes - f.total_blank_votes,
    CASE 
        WHEN e.total_blank_votes > f.total_blank_votes THEN 'INCREASE'
        WHEN e.total_blank_votes < f.total_blank_votes THEN 'DECREASE'
        ELSE 'NO CHANGE'
    END
FROM first_round_statistics f
CROSS JOIN second_round_statistics e

UNION ALL

SELECT 
    'Null votes' AS indicator,
    f.total_null_votes,
    e.total_null_votes,
    e.total_null_votes - f.total_null_votes,
    CASE 
        WHEN e.total_null_votes > f.total_null_votes THEN 'INCREASE'
        WHEN e.total_null_votes < f.total_null_votes THEN 'DECREASE'
        ELSE 'NO CHANGE'
    END
FROM first_round_statistics f
CROSS JOIN second_round_statistics s

UNION ALL

SELECT 
    'Valid votes' AS indicator,
    f.total_valid_votes,
    e.total_valid_votes,
    e.total_valid_votes - f.total_valid_votes,
    CASE 
        WHEN e.total_valid_votes > f.total_valid_votes THEN 'INCREASE'
        WHEN e.total_valid_votes < f.total_valid_votes THEN 'DECREASE'
        ELSE 'NO CHANGE'
    END
FROM first_round_statistics f
CROSS JOIN second_round_statistics e;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Normal pattern: Votes cast INCREASE in second round
-- Anomaly detected: Votes cast DECREASE + Valid votes DECREASE
-- Historical comparison needed: 2017, 2021 elections
