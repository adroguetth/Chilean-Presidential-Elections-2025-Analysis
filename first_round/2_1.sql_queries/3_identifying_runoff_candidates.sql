-- =====================================================
-- 3. IDENTIFYING RUNOFF CANDIDATES (JARA VS KAST)
-- =====================================================
-- Objective: Determine the two candidates who advanced to the second round
-- Context: Identify winner and runner-up based on valid vote share
-- Database: SQL Server 2012+
-- Source table: resultados_elecciones (columns: artes_votes, enriquez_ominami_votes, jara_votes, 
--              kaiser_votes, kast_votes, matthei_votes, mayne_nicholls_votes, parisi_votes,
--              blank_votes, null_votes, casted_votes)

WITH suma_votos AS (
    SELECT
        SUM(casted_votes) - (SUM(blank_votes) + SUM(null_votes)) AS total_votos_validos,
        SUM(artes_votes) AS artes_total,
        SUM(enriquez_ominami_votes) AS meo_total,
        SUM(jara_votes) AS jara_total,
        SUM(kaiser_votes) AS kaiser_total,
        SUM(kast_votes) AS kast_total,
        SUM(matthei_votes) AS matthei_total,
        SUM(mayne_nicholls_votes) AS mayne_nicholls_total,
        SUM(parisi_votes) AS parisi_total
    FROM resultados_elecciones
),
candidatos_votos AS (
    SELECT 'Eduardo Artes' AS candidato,
           ROUND(CAST(artes_total AS FLOAT) / total_votos_validos * 100, 2) AS porcentaje
    FROM suma_votos
    UNION ALL
    SELECT 'Marco Enriquez-Ominami',
           ROUND(CAST(meo_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
    UNION ALL
    SELECT 'Jeannette Jara',
           ROUND(CAST(jara_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
    UNION ALL
    SELECT 'Johannes Kaiser',
           ROUND(CAST(kaiser_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
    UNION ALL
    SELECT 'José Antonio Kast',
           ROUND(CAST(kast_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
    UNION ALL
    SELECT 'Evelyn Matthei',
           ROUND(CAST(matthei_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
    UNION ALL
    SELECT 'Franco Parisi',
           ROUND(CAST(parisi_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
    UNION ALL
    SELECT 'Harold Mayne-Nicholls',
           ROUND(CAST(mayne_nicholls_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
),
ranked_candidates AS (
    SELECT
        candidato,
        porcentaje,
        ROW_NUMBER() OVER (ORDER BY porcentaje DESC) AS posicion
    FROM candidatos_votos
)
SELECT
    candidato,
    porcentaje,
    CASE
        WHEN posicion = 1 THEN 'First place - Advances to runoff'
        WHEN posicion = 2 THEN 'Second place - Advances to runoff'
        ELSE 'Eliminated'
    END AS resultado_segunda_vuelta
FROM ranked_candidates
WHERE posicion IN (1, 2)
ORDER BY posicion;
