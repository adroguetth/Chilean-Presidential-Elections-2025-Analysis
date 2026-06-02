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
CROSS JOIN second_round_statistics e

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
-- The 2025 runoff election saw an unexpected drop in voter turnout.
-- 52,379 fewer votes were cast compared to the first round, and nearly 
-- 497,000 valid votes were lost.
-- The most notable change was the sharp increase in null votes (+421,458, 
-- almost doubling), while blank votes also rose moderately.
-- This indicates a significant increase in active protest and discontent 
-- between the two rounds.
-- This trend is anomalous, as runoff elections typically maintain or 
-- increase voter participation.
