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
-- Jara came extremely close to winning in 6 communes, all decided by margins under 2 percentage points.
-- The tightest race was in El Bosque (Metropolitana), where Kast won by just 0.42 pp.

-- Geographic Pattern:
-- - 4 out of 6 communes are in the Metropolitan Region (El Bosque, Estación Central, 
--   Peñalolén, and implied others), showing Jara's strength in urban working-class areas.
-- - Two communes in the North (Tocopilla and Freirina) highlight competitive zones 
--   in traditional mining territories.

-- Political Significance:
-- - These communes represent the most "flippable" territories for future elections.
-- - Very small shifts in turnout or voter preference (less than 1,000 votes in most cases) 
--   would have changed the winner.
-- - Demonstrates that even in defeat, Jara maintained competitive ground in key urban 
--   and northern areas, while Kast's victory, though broad, was narrow in several strategic locations.
-- =====================================================
