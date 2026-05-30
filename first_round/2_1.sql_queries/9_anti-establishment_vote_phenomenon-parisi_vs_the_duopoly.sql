-- =====================================================
-- 9. "ANTI-ESTABLISHMENT VOTE" PHENOMENON - PARISI vs THE DUOPOLY
-- =====================================================
-- Objective: Identify communes where Parisi's share exceeds the combined Jara + Kast share
-- Context: Analysis of protest voting against the political establishment
-- Method: Direct percentage comparison between the outsider candidate
--         and the combined share of the traditional duopoly
-- Hypothesis: Communities where systemic rejection outweighs partisan loyalty
-- Database: SQL Server 2012+
-- Source table: resultados_elecciones (columns: commune, region, parisi_pct, jara_pct, kast_pct, casted_votes)

SELECT
    commune AS comuna,
    region,
    parisi_pct AS parisi_porcentaje,
    jara_pct AS jara_porcentaje,
    kast_pct AS kast_porcentaje,
    (jara_pct + kast_pct) AS jara_kast_combinados,
    ROUND(parisi_pct - (jara_pct + kast_pct), 2) AS diferencia_parisi_vs_duopolio,
    casted_votes AS total_votos_emitidos
FROM resultados_elecciones
WHERE parisi_pct > (jara_pct + kast_pct)
ORDER BY diferencia_parisi_vs_duopolio DESC;
