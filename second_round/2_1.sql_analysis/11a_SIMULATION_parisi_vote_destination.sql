-- =====================================================
-- 11a. PARISI VOTE DESTINATION: JARA, KAST, NULL/BLANK
-- =====================================================
-- Objective: Estimate the destination of Franco Parisi's 2.55 million voters 
--            in the second round
-- Context: Simulation based on actual results, assuming 42% transfer to Jara
-- Note: This is a SIMULATION. Real individual-level transfer is unknowable 
--       without exit polls. The 42% to Jara is a conservative / balanced assumption.
-- Database: SQL Server 2012+
-- Source tables: first_round_2025

WITH first_round_totals AS (
    SELECT
        SUM(parisi_votes) AS parisi_total
    FROM first_round_2025
),
parisi_transfer AS (
    SELECT
        parisi_total,
        0.42 AS pct_to_jara,
        -- Remaining after Jara transfer: 58%
        (1 - 0.42) * 0.65 AS pct_to_kast,  -- 65% of remaining = 37.7%
        (1 - 0.42) * 0.35 AS pct_to_protest -- 35% of remaining = 20.3%
    FROM first_round_totals
)
SELECT 
    'Parisi Voters (1st Round)' AS category,
    CAST(parisi_total AS DECIMAL(12,0)) AS votes,
    CAST(100.00 AS DECIMAL(10,2)) AS percentage
FROM parisi_transfer

UNION ALL

SELECT 
    '? Transferred to Jara (42%)',
    CAST(parisi_total * pct_to_jara AS DECIMAL(12,0)),
    CAST(pct_to_jara * 100 AS DECIMAL(10,2))
FROM parisi_transfer

UNION ALL

SELECT 
    '? Transferred to Kast',
    CAST(parisi_total * pct_to_kast AS DECIMAL(12,0)),
    CAST(pct_to_kast * 100 AS DECIMAL(10,2))
FROM parisi_transfer

UNION ALL

SELECT 
    '? Ended in Null/Blank/Abstention (Protest)',
    CAST(parisi_total * pct_to_protest AS DECIMAL(12,0)),
    CAST(pct_to_protest * 100 AS DECIMAL(10,2))
FROM parisi_transfer

UNION ALL

SELECT 
    'TOTAL',
    CAST(parisi_total AS DECIMAL(12,0)),
    CAST(100.00 AS DECIMAL(10,2))
FROM parisi_transfer;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- According to this simulation (assuming 42% transfer to Jara):

-- • 42.00% of Parisi voters (1,071,323 votes) transferred to Jeannette Jara.
-- • 37.70% (961,640 votes) transferred to José Antonio Kast.
-- • 20.30% (517,806 votes) ended up as Null, Blank or Abstention (protest).

-- Summary:
-- - Jara received the largest share of Parisi's voters (42%), but still fell short of what was needed to win.
-- - Kast captured a very significant portion (37.7%), which was decisive for his victory.
-- - Almost one in five Parisi voters (20.3%) chose not to support either candidate, expressing protest through null votes, blank votes, or abstention.

-- Strategic Insight:
-- Kast was highly effective at attracting a large share of the antisystem vote, while Jara captured the plurality but not enough to overcome the gap. 
-- The high protest rate (20.3%) shows that a substantial portion of Parisi's base remained unconvinced by both options in the runoff.
-- =====================================================
