-- =====================================================
-- 10a. TOP 10 KAST STRONGHOLDS (HIGHEST PERCENTAGES)
-- =====================================================
-- Objective: Identify communes where Kast achieved his largest margins
-- Context: Reveals geographic base of Kast's electoral support
-- Database: SQL Server 2012+
-- Source table: second_round_2025

SELECT TOP 10
    commune AS comuna,
    region,
    kast_pct AS kast_percentage,
    ROUND(kast_pct - jara_pct, 2) AS margin_pp,
    CASE 
        WHEN kast_pct > 80 THEN 'Landslide (>80%)'
        WHEN kast_pct > 70 THEN 'Stronghold (70-80%)'
        WHEN kast_pct > 60 THEN 'Solid (60-70%)'
    END AS victory_type
FROM second_round_2025
WHERE kast_pct > 60
ORDER BY kast_pct DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Kast achieved overwhelming victories in his strongest communes:
-- - Colchane (Tarapacá) stands out with 93.81%, the highest in the country.
-- - Multiple communes exceeded 80% (Landslide category), especially in the North (Tarapacá, Arica y Parinacota) and rural areas of the Center-South.

-- Geographic Pattern:
-- - Strong presence in northern border communes (Colchane, General Lagos, Camarones) 
--   and traditional rural communes in Ñuble and Maule.
-- - Also includes elite urban communes like Vitacura and Lo Barnechea, showing Kast's 
--   ability to penetrate high-income areas.

-- Political Significance:
-- - These communes represent Kast's "iron core" — territories with very high loyalty 
--   and minimal competition.
-- - The combination of northern border strongholds and southern rural areas confirms 
--   Kast's broad territorial appeal, spanning from the extreme north to the south.
-- - Contrast with Jara's strongholds (highly concentrated in Metropolitana) highlights 
--   Kast's superior geographic diversification.
-- =====================================================
