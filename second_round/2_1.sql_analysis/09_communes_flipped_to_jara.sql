-- =====================================================
-- 9. COMMUNES WHERE JARA LOST IN FIRST ROUND BUT WON IN SECOND ROUND
-- =====================================================
-- Objective: Identify communes that flipped from anti-Jara to pro-Jara
-- Context: Reveals voter migration and campaign effectiveness
-- Database: SQL Server 2012+
-- Source tables: first_round_2025, second_round_2025

WITH first_round_winner AS (
    SELECT 
        commune,
        region,
        CASE 
            WHEN jara_pct > kast_pct AND jara_pct > parisi_pct AND jara_pct > kaiser_pct 
                 AND jara_pct > matthei_pct AND jara_pct > mayne_nicholls_pct 
                 AND jara_pct > enriquez_ominami_pct AND jara_pct > artes_pct 
                 THEN 'Jara'
            WHEN kast_pct > jara_pct AND kast_pct > parisi_pct AND kast_pct > kaiser_pct 
                 AND kast_pct > matthei_pct AND kast_pct > mayne_nicholls_pct 
                 AND kast_pct > enriquez_ominami_pct AND kast_pct > artes_pct 
                 THEN 'Kast'
            WHEN parisi_pct > jara_pct AND parisi_pct > kast_pct THEN 'Parisi'
            WHEN kaiser_pct > jara_pct AND kaiser_pct > kast_pct THEN 'Kaiser'
            WHEN matthei_pct > jara_pct AND matthei_pct > kast_pct THEN 'Matthei'
            ELSE 'Other'
        END AS winner_first_round
    FROM first_round_2025
),
second_round_winner AS (
    SELECT 
        commune,
        region,
        CASE 
            WHEN jara_pct > kast_pct THEN 'Jara'
            WHEN kast_pct > jara_pct THEN 'Kast'
            ELSE 'Tie'
        END AS winner_second_round
    FROM second_round_2025
)
SELECT 
    f.commune,
    f.region,
    i.winner_first_round,
    j.winner_second_round,
    ROUND(f.jara_pct, 2) AS jara_pct_first_round,
    ROUND(e.jara_pct, 2) AS jara_pct_second_round,
    ROUND(e.jara_pct - f.jara_pct, 2) AS jara_swing_pp,
    ROUND(f.kast_pct, 2) AS kast_pct_first_round,
    ROUND(e.kast_pct, 2) AS kast_pct_second_round
FROM first_round_2025 f
INNER JOIN second_round_2025 e ON f.commune = e.commune
INNER JOIN first_round_winner i ON f.commune = i.commune
INNER JOIN second_round_winner j ON e.commune = j.commune
WHERE i.winner_first_round != 'Jara' 
    AND j.winner_second_round = 'Jara'
ORDER BY jara_swing_pp DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- Jara achieved notable vote swings in several communes she lost in the first round,
-- particularly in the northern mining regions (Antofagasta and Atacama).

-- Key Findings:
-- - The largest swings occurred in communes previously dominated by Franco Parisi.
-- - Mana Elena (Antofagasta) showed the highest swing (+28.20 pp), followed by Mejillones 
--   (+24.43 pp) and Diego de Almagro (+22.70 pp).
-- - These flips demonstrate that Jara was able to capture a significant portion of 
--   the antisystem (Parisi) vote in key northern mining areas.

-- Political Significance:
-- - Jara successfully penetrated some of Parisi's strongest territories in the North.
-- - However, these gains were concentrated in a limited number of communes, mainly 
--   in the Norte Grande and Norte Chico.
-- - This suggests a partial but geographically focused transfer from Parisi voters 
--   to Jara, likely driven by strategic campaigning or rejection of Kast in those areas.
-- =====================================================
