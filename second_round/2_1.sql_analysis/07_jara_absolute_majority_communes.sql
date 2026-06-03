-- =====================================================
-- 7. COMMUNES WHERE JARA ACHIEVED ABSOLUTE MAJORITY (>50%)
-- =====================================================
-- Objective: Identify communes where Jara exceeded 50% of valid votes
-- Context: Absolute majority indicates stronghold territory
-- Database: SQL Server 2012+
-- Source table: second_round_2025

SELECT
    commune AS comuna,
    region,
    jara_pct AS percentage,
    CASE
        WHEN jara_pct >= kast_pct
        THEN 'Wins in this commune'
        ELSE 'Loses in this commune'
    END AS commune_result
FROM second_round_2025
WHERE jara_pct > 50
ORDER BY jara_pct DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Jeannette Jara achieved absolute majority (>50%) in only 36 communes (10.4% of total).
-- Her strongest performances were in Juan Fernández (59.29%) and Pedro Aguirre Cerda (58.75%).

-- Geographic Concentration:
-- - Metropolitana: 21 communes (the clear core of her support)
-- - Valparaíso: 5 communes (including Easter Island and Juan Fernández)
-- - Atacama: 4 communes
-- - Coquimbo: 3 communes
-- - Antofagasta: 3 communes

-- Key Observations:
-- - Jara's absolute majorities are heavily concentrated in the **Metropolitan Region** 
--   and a few northern/port areas. 
-- - She did not achieve absolute majority in any commune in the entire Center-South, 
--   South, or Patagonia (Biobío, Ñuble, La Araucanía, Los Lagos, etc.).
-- - Even in her winning communes, many results were narrow (just above 50%), 
--   showing limited enthusiasm in her base.

-- Political Significance:
-- - Jara's support remained extremely concentrated in urban and mining areas.
-- - The complete absence of absolute majorities outside the center-north highlights 
--   the geographic weakness of the progressive coalition in the rest of the country.
-- =====================================================
