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

-- =====================================================
-- KEY FINDINGS:
-- =====================================================
-- José Antonio Kast achieved a complete regional sweep, winning ALL 16 regions (100%).
-- Jeannette Jara only won communes in 5 regions, with her strongest performance in 
-- the Metropolitan Region (21 communes), followed by Valparaíso (5), Atacama (4), 
-- Coquimbo (3), and Antofagasta (3).

-- POLITICAL SIGNIFICANCE:
-- =====================================================
-- This represents an unprecedented territorial victory for Kast. Despite Jara 
-- obtaining a respectable 41.76% of the national vote, her support was extremely 
-- concentrated in a few urban pockets, mainly in the Metropolitan Region.
-- Kast demonstrated truly national appeal, dominating both rural and most urban 
-- areas outside the core of Santiago.
-- The left's geographic fragmentation is severe: Jara was unable to win a single 
-- region, highlighting the collapse of progressive support beyond dense urban centers.
-- =====================================================
