-- =====================================================
-- 4. SECOND ROUND WINNER DECLARATION
-- =====================================================
-- Objective: Determine the winner of the runoff election
-- Context: Calculates final percentages and declares president-elect
-- Database: SQL Server 2012+
-- Source table: second_round_2025

WITH suma_votos AS (
    SELECT
        SUM(casted_votes) - (SUM(blank_votes) + SUM(null_votes)) AS total_votos_validos,
        SUM(jara_votes) AS jara_total,
        SUM(kast_votes) AS kast_total
    FROM second_round_2025
)
SELECT 
    'Jeannette Jara' AS candidate,
    ROUND(CAST(jara_total AS FLOAT) / NULLIF(total_votos_validos, 0) * 100, 2) AS percentage,
    jara_total AS total_votes,
    CASE WHEN jara_total > kast_total THEN 'PRESIDENT-ELECT' ELSE 'defeated' END AS result
FROM suma_votos
UNION ALL
SELECT 
    'José Antonio Kast',
    ROUND(CAST(kast_total AS FLOAT) / NULLIF(total_votos_validos, 0) * 100, 2),
    kast_total,
    CASE WHEN kast_total > jara_total THEN 'PRESIDENT-ELECT' ELSE 'defeated' END
FROM suma_votos
UNION ALL
SELECT 
    'Margin',
    ROUND(ABS(CAST(jara_total - kast_total AS FLOAT)) / NULLIF(total_votos_validos, 0) * 100, 2),
    ABS(jara_total - kast_total),
    'winning margin'
FROM suma_votos
ORDER BY percentage DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- WINNER: José Antonio Kast elected President with 58.24% of valid votes
-- Final Result: Kast 7,231,018 votes (58.24%) vs Jara 5,184,026 votes (41.76%)
-- Winning Margin: 16.49 percentage points (2,046,992 votes)
-- Total valid votes: 12,415,044

-- Key Insights:
-- - Kast achieved a decisive victory with a double-digit margin (+16.49 pp), 
--   significantly larger than most pre-election projections.
-- - Jara retained a solid base (41.76%), but failed to attract sufficient 
--   transfer from Parisi voters or centrists.
-- - This margin ranks among the largest in Chilean presidential runoff history 
--   since the return to democracy.
-- - The result confirms a clear shift toward the right and a rejection of the 
--   outgoing government's continuity.
-- =====================================================
