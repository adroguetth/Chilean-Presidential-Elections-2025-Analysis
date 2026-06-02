-- =====================================================
-- 8. COMMUNES WHERE JARA ALMOST WON (KAST MARGIN ≤ 2%)
-- =====================================================
-- Objective: Identify competitive communes where Jara narrowly lost
-- Context: These are "flippable" communes for future elections
-- Database: SQL Server 2012+
-- Source table: second_round_2025

SELECT
    commune AS comuna,
    region,
    jara_pct AS jara_percentage,
    kast_pct AS kast_percentage,
    ROUND(kast_pct - jara_pct, 2) AS kast_margin_pp,
    CASE 
        WHEN ROUND(kast_pct - jara_pct, 2) <= 1 THEN 'Ultra-tight (<1pp)'
        WHEN ROUND(kast_pct - jara_pct, 2) <= 2 THEN 'Competitive (1-2pp)'
    END AS competitiveness
FROM second_round_2025
WHERE kast_pct > jara_pct 
    AND (kast_pct - jara_pct) <= 2
ORDER BY kast_margin_pp ASC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- These communes represent the closest races in the runoff:
-- - Margins under 1%: True toss-ups that could have flipped
-- - Margins 1-2%: Competitive but Kast held on
-- 
-- Political significance:
-- - These are priority targets for future campaigns
-- - Small shifts in voter behavior would flip these communes
-- - Likely urban/suburban areas with mixed demographics
-- =====================================================
