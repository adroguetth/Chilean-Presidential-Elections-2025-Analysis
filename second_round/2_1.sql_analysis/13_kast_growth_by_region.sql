-- =====================================================
-- 13. KAST VOTE GROWTH BY REGION (1ST ROUND → 2ND ROUND)
-- =====================================================
-- Objective: Show where Kast grew most and least between rounds
-- Context: Identifies regions where Kast expanded or contracted his support
-- Database: SQL Server 2012+
-- Source tables: first_round_2025, second_round_2025


WITH kast_growth AS (
    SELECT
        f.region,
        SUM(f.kast_votes) AS kast_votes_1v,
        SUM(e.kast_votes) AS kast_votes_2v,
        ROUND(100.0 * SUM(f.kast_votes) / NULLIF(SUM(f.casted_votes), 0), 2) AS kast_pct_1v,
        ROUND(100.0 * SUM(e.kast_votes) / NULLIF(SUM(e.casted_votes), 0), 2) AS kast_pct_2v
    FROM first_round_2025 f
    INNER JOIN second_round_2025 e ON f.commune = e.commune
    GROUP BY f.region
)
SELECT 
    region,
    kast_votes_1v,
    kast_votes_2v,
    (kast_votes_2v - kast_votes_1v) AS kast_votes_growth,
    CAST(kast_pct_1v AS DECIMAL(5,2)) AS kast_pct_1v,
    CAST(kast_pct_2v AS DECIMAL(5,2)) AS kast_pct_2v,
    CAST((kast_pct_2v - kast_pct_1v) AS DECIMAL(5,2)) AS kast_pct_growth_pp
FROM kast_growth
ORDER BY 
    CASE region
        WHEN 'Arica y Parinacota' THEN 1
        WHEN 'Tarapacá' THEN 2
        WHEN 'Antofagasta' THEN 3
        WHEN 'Atacama' THEN 4
        WHEN 'Coquimbo' THEN 5
        WHEN 'Valparaíso' THEN 6
        WHEN 'Metropolitana' THEN 7
        WHEN 'Libertador' THEN 8
        WHEN 'Maule' THEN 9
        WHEN 'Ñuble' THEN 10
        WHEN 'Biobío' THEN 11
        WHEN 'La Araucanía' THEN 12
        WHEN 'Los Ríos' THEN 13
        WHEN 'Los Lagos' THEN 14
        WHEN 'Aysén' THEN 15
        WHEN 'Magallanes' THEN 16
    END;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- This shows Kast's growth from north to south, revealing geographic patterns:
-- - Northern regions (Arica → Atacama): [growth pattern]
-- - Central regions (Coquimbo → Maule): [growth pattern]  
-- - Southern regions (Ñuble → Magallanes): [growth pattern]
-- =====================================================
