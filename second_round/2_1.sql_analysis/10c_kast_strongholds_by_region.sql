--- =====================================================
-- 10c. KAST STRONGHOLDS BY REGION (>60%)
-- =====================================================
-- Objective: Show regional distribution of communes where Kast exceeded 60%
-- Context: Identifies geographic concentration of Kast's strongest support
-- Database: SQL Server 2012+
-- Source table: second_round_2025

WITH total_strongholds AS (
    SELECT COUNT(*) AS total FROM second_round_2025 WHERE kast_pct > 60
)
SELECT 
    s.region,
    COUNT(*) AS communes_with_kast_60plus,
    CAST(100.0 * COUNT(*) / t.total AS DECIMAL(5,2)) AS pct_of_total_strongholds,
    CAST(AVG(s.kast_pct) AS DECIMAL(5,2)) AS avg_kast_pct,
    CAST(AVG(s.kast_pct - s.jara_pct) AS DECIMAL(5,2)) AS avg_margin_pp,
    CAST(MIN(s.kast_pct) AS DECIMAL(5,2)) AS min_kast_pct,
    CAST(MAX(s.kast_pct) AS DECIMAL(5,2)) AS max_kast_pct
FROM second_round_2025 s
CROSS JOIN total_strongholds t
WHERE s.kast_pct > 60
GROUP BY s.region, t.total
ORDER BY communes_with_kast_60plus DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Kast's strongest support (>60% of valid votes) is heavily concentrated in the 
-- Center-South and South regions:

-- Regional Distribution of Strongholds:
-- • La Araucanía      : 32 communes (14.55% of all strongholds)
-- • Los Lagos         : 28 communes
-- • Maule             : 28 communes
-- • Biobío            : 27 communes

-- Key Insights:
-- - The southern and central-southern regions (La Araucanía, Los Lagos, Maule, Biobío) 
--   represent the core of Kast's "deep territory", accounting for the majority of his 
--   landslide and stronghold communes.
-- - Average Kast vote in these strongholds exceeds 67-72%, with very comfortable margins.
-- - In contrast, the Metropolitan Region has only 12 strongholds (5.45%), showing that 
--   even in victory, Kast's support in the capital was more competitive.

-- Strategic Significance:
-- - These southern regions form Kast's electoral "iron belt" — territories with very 
--   high loyalty and low risk of flipping.
-- - This geographic concentration confirms Kast's strength in rural, agricultural, 
--   and traditionally conservative areas.
-- =====================================================
