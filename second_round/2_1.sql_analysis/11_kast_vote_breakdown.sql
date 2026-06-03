-- =====================================================
-- 11. KAST VOTE SOURCES IN SECOND ROUND (SIMULATION)
-- =====================================================
-- Objective: Breakdown of where Kast's second round votes came from
-- Context: Estimates loyalty + coalition transfer + other sources
-- Important Note: 
--   This is a SIMULATION. It assumes that all votes from Kaiser and Matthei 
--   went to Kast. In reality, a portion of those voters likely abstained, 
--   voted blank, or null. Therefore, the "Transferred from Kaiser + Matthei" 
--   figure represents the MAXIMUM possible transfer.
-- Database: SQL Server 2012+
-- Source tables: first_round_2025, second_round_2025

WITH national_totals AS (
    SELECT
        SUM(e.kast_votes) AS kast_2v,
        SUM(f.kast_votes) AS kast_1v,
        SUM(f.kaiser_votes + f.matthei_votes) AS kaiser_matthei_1v
    FROM first_round_2025 f
    INNER JOIN second_round_2025 e ON f.commune = e.commune
)
SELECT 
    'Kast Second Round Votes (TOTAL)' AS source,
    kast_2v AS votes,
    CAST(100.00 AS DECIMAL(5,2)) AS percentage
FROM national_totals

UNION ALL

SELECT 
    'Kast Loyal Voters (1st round)',
    kast_1v,
    CAST(ROUND(100.0 * kast_1v / kast_2v, 2) AS DECIMAL(5,2))
FROM national_totals

UNION ALL

SELECT 
    'Transferred from Kaiser + Matthei',
    kaiser_matthei_1v,
    CAST(ROUND(100.0 * kaiser_matthei_1v / kast_2v, 2) AS DECIMAL(5,2))
FROM national_totals

UNION ALL

SELECT 
    'Other Sources',
    kast_2v - (kast_1v + kaiser_matthei_1v),
    CAST(ROUND(100.0 * (kast_2v - (kast_1v + kaiser_matthei_1v)) / kast_2v, 2) AS DECIMAL(5,2))
FROM national_totals;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Kast built his victory with a solid core of loyal voters (42.7%) and a very 
-- strong transfer from the fragmented right (Kaiser + Matthei), which contributed 
-- up to 47% of his total.
-- The remaining ~10.3% came from other sources, including partial transfer from 
-- Parisi voters, new voters, and compensation for abstention.
-- 
-- However, it is important to note that not all right-wing voters from the first 
-- round supported Kast in the second. A significant portion likely abstained or 
-- cast null/blank votes, meaning the real transfer rate from Kaiser+Matthei was 
-- lower than the theoretical maximum shown here.
-- 
-- Overall, Kast succeeded in unifying most of the right-wing vote while also 
-- attracting additional support, achieving a decisive 16.5-point victory.
-- =====================================================
