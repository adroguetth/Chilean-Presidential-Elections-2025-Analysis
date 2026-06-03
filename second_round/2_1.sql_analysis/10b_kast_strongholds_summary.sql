-- =====================================================
-- 10b. KAST STRONGHOLDS SUMMARY BY CATEGORY
-- =====================================================
-- Objective: Show distribution of Kast's winning communes by margin intensity
-- Context: Reveals that most Kast wins are narrow, not landslides
-- Database: SQL Server 2012+
-- Source table: second_round_2025

SELECT 
    CASE 
        WHEN kast_pct > 80 THEN 'Landslide (>80%)'
        WHEN kast_pct > 70 THEN 'Stronghold (70-80%)'
        WHEN kast_pct > 60 THEN 'Solid (60-70%)'
        WHEN kast_pct > 50 THEN 'Bare majority (50-60%)'
    END AS victory_type,
    COUNT(*) AS communes_count,
    ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM second_round_2025 WHERE kast_pct > 50) * 100, 1) AS percentage_of_wins,
    ROUND(AVG(kast_pct), 2) AS avg_kast_pct,
    ROUND(MIN(kast_pct), 2) AS min_kast_pct,
    ROUND(MAX(kast_pct), 2) AS max_kast_pct
FROM second_round_2025
WHERE kast_pct > 50
GROUP BY 
    CASE 
        WHEN kast_pct > 80 THEN 'Landslide (>80%)'
        WHEN kast_pct > 70 THEN 'Stronghold (70-80%)'
        WHEN kast_pct > 60 THEN 'Solid (60-70%)'
        WHEN kast_pct > 50 THEN 'Bare majority (50-60%)'
    END
ORDER BY avg_kast_pct DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Kast achieved a dominant performance across different levels of victory:

-- Victory Type Distribution:
-- • Landslide (>80%): 6 communes (average 86.62%)
-- • Stronghold (70-80%): 77 communes (average 73.54%)
-- • Solid (60-70%): 137 communes (average 65.11%)
-- • Bare Majority (50-60%): 90 communes (average 55.64%)

-- Key Insights:
-- - Kast secured **Landslide victories** in 6 communes, reaching up to 93.81% in Colchane.
-- - A total of **220 communes** (63.6% of the country) gave him more than 60% of the vote.
-- - His support was not only broad but also deep in many territories.

-- Political Significance:
-- - This distribution demonstrates exceptional territorial strength. Kast didn't just win — 
--   he dominated large parts of the country with very high percentages.
-- - The combination of extreme strongholds in the North (border areas) and massive 
--   numbers of solid victories in the Center-South and South confirms Kast built a 
--   truly national coalition with varying intensities.
-- - Contrast with Jara (only 36 absolute majority communes) highlights the difference 
--   in depth of support between both candidates.
-- =====================================================
