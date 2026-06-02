-- =====================================================
-- 6. TERRITORIAL MAPPING BY REGION 
-- =====================================================
-- Objective: Show which candidate won each region and commune count per region
-- Context: Regional-level territorial dominance analysis
-- Database: SQL Server 2012+
-- Source table: second_round_2025

WITH regional_winners AS (
    SELECT
        region,
        commune,
        CASE 
            WHEN jara_pct > kast_pct THEN 'Jara'
            WHEN kast_pct > jara_pct THEN 'Kast'
            ELSE 'Tie'
        END AS winner
    FROM second_round_2025
)
SELECT 
    region,
    COUNT(CASE WHEN winner = 'Jara' THEN 1 END) AS communes_jara,
    COUNT(CASE WHEN winner = 'Kast' THEN 1 END) AS communes_kast,
    COUNT(CASE WHEN winner = 'Tie' THEN 1 END) AS communes_tie,
    CASE 
        WHEN COUNT(CASE WHEN winner = 'Jara' THEN 1 END) > COUNT(CASE WHEN winner = 'Kast' THEN 1 END) THEN 'Jara'
        WHEN COUNT(CASE WHEN winner = 'Kast' THEN 1 END) > COUNT(CASE WHEN winner = 'Jara' THEN 1 END) THEN 'Kast'
        ELSE 'Tie'
    END AS regional_winner
FROM regional_winners
GROUP BY region
ORDER BY region;

-- KEY FINDINGS:
-- =====================================================
-- Kast won ALL 16 regions (100% regional victory)
-- Only 4 regions had any Jara commune wins: Metropolitana (21), Atacama (4), 
--   Antofagasta (3), Coquimbo (3), Valparaíso (5)
-- Jara's strongest region: Metropolitana (21 communes, but still lost region 31-21)

-- POLITICAL SIGNIFICANCE:
-- =====================================================
-- This is an unprecedented territorial victory. Kast's support is not regional
-- but national. Jara's coalition was reduced to isolated urban pockets, 
-- unable to flip a single region despite winning 41.76% of the national vote.
-- The geographic fragmentation of the left vote is extreme.
-- =====================================================
