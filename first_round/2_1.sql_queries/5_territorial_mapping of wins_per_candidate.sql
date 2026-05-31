-- =====================================================
-- 5. TERRITORIAL MAPPING OF WINS PER CANDIDATE
-- =====================================================
-- Objective: Count how many communes each candidate won across the country
-- Context: Reveal territorial dominance and geographic fragmentation of vote
-- Database: SQL Server 2012+
-- Source table: first_round_2025 (columns: commune, region, artes_pct, enriquez_ominami_pct, 
--              jara_pct, kaiser_pct, kast_pct, matthei_pct, mayne_nicholls_pct, parisi_pct)

WITH ranked_communes AS (
    SELECT
        commune,
        region,
        artes_pct,
        enriquez_ominami_pct,
        jara_pct,
        kaiser_pct,
        kast_pct,
        matthei_pct,
        mayne_nicholls_pct,
        parisi_pct,
        -- Identify the candidate with the highest percentage in each commune
        CASE 
            WHEN artes_pct >= enriquez_ominami_pct AND artes_pct >= jara_pct AND artes_pct >= kaiser_pct 
                 AND artes_pct >= kast_pct AND artes_pct >= matthei_pct AND artes_pct >= mayne_nicholls_pct 
                 AND artes_pct >= parisi_pct
            THEN 'Eduardo Artes'
            WHEN enriquez_ominami_pct >= artes_pct AND enriquez_ominami_pct >= jara_pct 
                 AND enriquez_ominami_pct >= kaiser_pct AND enriquez_ominami_pct >= kast_pct 
                 AND enriquez_ominami_pct >= matthei_pct AND enriquez_ominami_pct >= mayne_nicholls_pct 
                 AND enriquez_ominami_pct >= parisi_pct
            THEN 'Marco Enriquez-Ominami'
            WHEN jara_pct >= artes_pct AND jara_pct >= enriquez_ominami_pct AND jara_pct >= kaiser_pct 
                 AND jara_pct >= kast_pct AND jara_pct >= matthei_pct AND jara_pct >= mayne_nicholls_pct 
                 AND jara_pct >= parisi_pct
            THEN 'Jeannette Jara'
            WHEN kaiser_pct >= artes_pct AND kaiser_pct >= enriquez_ominami_pct AND kaiser_pct >= jara_pct 
                 AND kaiser_pct >= kast_pct AND kaiser_pct >= matthei_pct AND kaiser_pct >= mayne_nicholls_pct 
                 AND kaiser_pct >= parisi_pct
            THEN 'Johannes Kaiser'
            WHEN kast_pct >= artes_pct AND kast_pct >= enriquez_ominami_pct AND kast_pct >= kaiser_pct 
                 AND kast_pct >= jara_pct AND kast_pct >= matthei_pct AND kast_pct >= mayne_nicholls_pct 
                 AND kast_pct >= parisi_pct
            THEN 'José Antonio Kast'
            WHEN matthei_pct >= artes_pct AND matthei_pct >= enriquez_ominami_pct AND matthei_pct >= kaiser_pct 
                 AND matthei_pct >= kast_pct AND matthei_pct >= jara_pct AND matthei_pct >= mayne_nicholls_pct 
                 AND matthei_pct >= parisi_pct
            THEN 'Evelyn Matthei'
            WHEN mayne_nicholls_pct >= artes_pct AND mayne_nicholls_pct >= enriquez_ominami_pct 
                 AND mayne_nicholls_pct >= kaiser_pct AND mayne_nicholls_pct >= kast_pct 
                 AND mayne_nicholls_pct >= matthei_pct AND mayne_nicholls_pct >= jara_pct 
                 AND mayne_nicholls_pct >= parisi_pct
            THEN 'Harold Mayne-Nicholls'
            WHEN parisi_pct >= artes_pct AND parisi_pct >= enriquez_ominami_pct AND parisi_pct >= kaiser_pct 
                 AND parisi_pct >= kast_pct AND parisi_pct >= matthei_pct AND parisi_pct >= mayne_nicholls_pct 
                 AND parisi_pct >= jara_pct
            THEN 'Franco Parisi'
            ELSE 'Tie / No data'
        END AS ganador_comuna
    FROM first_round_2025
)
SELECT
    ganador_comuna AS candidato,
    COUNT(*) AS comunas_ganadas,
    ROUND(CAST(COUNT(*) AS FLOAT) / 346 * 100, 1) AS porcentaje_comunas
FROM ranked_communes
WHERE ganador_comuna != 'Tie / No data'
GROUP BY ganador_comuna
ORDER BY comunas_ganadas DESC;
