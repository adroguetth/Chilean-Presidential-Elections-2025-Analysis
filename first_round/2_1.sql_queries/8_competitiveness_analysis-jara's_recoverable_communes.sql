-- =====================================================
-- 8. COMPETITIVENESS ANALYSIS - JARA'S RECOVERABLE COMMUNES
-- =====================================================
-- Objective: Identify communes where Jara lost by a margin of less than 1,000 votes
-- Context: Quantify minimum vote transfer needed to flip communes in runoff
-- Database: SQL Server 2012+
-- Source table: resultados_elecciones (columns: commune, casted_votes, blank_votes, null_votes,
--              jara_pct, artes_pct, enriquez_ominami_pct, kaiser_pct, kast_pct, 
--              matthei_pct, mayne_nicholls_pct, parisi_pct)

WITH votos_por_comuna AS (
    SELECT
        commune,
        -- Calculate total valid votes per commune (casted - blank - null)
        SUM(casted_votes) - (SUM(blank_votes) + SUM(null_votes)) AS votos_validos,
        SUM(jara_votes) AS votos_jara,
        -- Determine the winner's percentage in each commune
        CASE 
            WHEN artes_pct >= enriquez_ominami_pct AND artes_pct >= jara_pct AND artes_pct >= kaiser_pct 
                 AND artes_pct >= kast_pct AND artes_pct >= matthei_pct AND artes_pct >= mayne_nicholls_pct 
                 AND artes_pct >= parisi_pct
            THEN artes_pct
            WHEN enriquez_ominami_pct >= artes_pct AND enriquez_ominami_pct >= jara_pct 
                 AND enriquez_ominami_pct >= kaiser_pct AND enriquez_ominami_pct >= kast_pct 
                 AND enriquez_ominami_pct >= matthei_pct AND enriquez_ominami_pct >= mayne_nicholls_pct 
                 AND enriquez_ominami_pct >= parisi_pct
            THEN enriquez_ominami_pct
            WHEN kaiser_pct >= artes_pct AND kaiser_pct >= enriquez_ominami_pct AND kaiser_pct >= jara_pct 
                 AND kaiser_pct >= kast_pct AND kaiser_pct >= matthei_pct AND kaiser_pct >= mayne_nicholls_pct 
                 AND kaiser_pct >= parisi_pct
            THEN kaiser_pct
            WHEN kast_pct >= artes_pct AND kast_pct >= enriquez_ominami_pct AND kast_pct >= kaiser_pct 
                 AND kast_pct >= jara_pct AND kast_pct >= matthei_pct AND kast_pct >= mayne_nicholls_pct 
                 AND kast_pct >= parisi_pct
            THEN kast_pct
            WHEN matthei_pct >= artes_pct AND matthei_pct >= enriquez_ominami_pct AND matthei_pct >= kaiser_pct 
                 AND matthei_pct >= kast_pct AND matthei_pct >= jara_pct AND matthei_pct >= mayne_nicholls_pct 
                 AND matthei_pct >= parisi_pct
            THEN matthei_pct
            WHEN mayne_nicholls_pct >= artes_pct AND mayne_nicholls_pct >= enriquez_ominami_pct 
                 AND mayne_nicholls_pct >= kaiser_pct AND mayne_nicholls_pct >= kast_pct 
                 AND mayne_nicholls_pct >= matthei_pct AND mayne_nicholls_pct >= jara_pct 
                 AND mayne_nicholls_pct >= parisi_pct
            THEN mayne_nicholls_pct
            WHEN parisi_pct >= artes_pct AND parisi_pct >= enriquez_ominami_pct AND parisi_pct >= kaiser_pct 
                 AND parisi_pct >= kast_pct AND parisi_pct >= matthei_pct AND parisi_pct >= mayne_nicholls_pct 
                 AND parisi_pct >= jara_pct
            THEN parisi_pct
            ELSE jara_pct
        END AS pct_ganador,
        -- Identify which candidate won
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
            ELSE 'Jeannette Jara'
        END AS candidato_ganador
    FROM resultados_elecciones
    GROUP BY commune, artes_pct, enriquez_ominami_pct, jara_pct, kaiser_pct, kast_pct, 
             matthei_pct, mayne_nicholls_pct, parisi_pct
),
diferencia_votos AS (
    SELECT
        commune,
        votos_validos,
        votos_jara,
        candidato_ganador,
        ROUND((pct_ganador / 100.0) * votos_validos, 0) AS votos_ganador,
        ROUND(((pct_ganador / 100.0) * votos_validos) - votos_jara, 0) AS votos_faltantes
    FROM votos_por_comuna
    WHERE candidato_ganador != 'Jeannette Jara'
)
SELECT
    'Jeannette Jara' AS candidato,
    COUNT(commune) AS comunas_recuperables,
    SUM(votos_faltantes) AS total_votos_faltantes,
    ROUND(AVG(votos_faltantes), 0) AS promedio_votos_faltantes,
    ROUND(CAST(COUNT(commune) AS FLOAT) / (SELECT COUNT(*) FROM diferencia_votos) * 100, 1) AS porcentaje_comunas_competitivas
FROM diferencia_votos
WHERE votos_faltantes <= 1000;
