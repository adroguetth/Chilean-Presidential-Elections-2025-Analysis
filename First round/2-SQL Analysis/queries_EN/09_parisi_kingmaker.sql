-- =====================================================
-- 9. "ANTI-ESTABLISHMENT VOTE" PHENOMENON - PARISI vs THE DUOPOLY
-- =====================================================
-- Objective: Identify communes where Parisi's share exceeds the combined Jara + Kast share
-- Context: Analysis of protest voting against the political establishment
-- Method: Direct percentage comparison between the outsider candidate
--         and the combined share of the traditional duopoly
-- Hypothesis: Communities where systemic rejection outweighs partisan loyalty

SELECT
    comuna,                          -- Base territorial unit of analysis
    region,                          -- Regional geographic context
    parisi_pct AS parisi_porcentaje, -- Franco Parisi's vote share

    jara_pct AS jara_porcentaje,     -- Jeannette Jara's vote share
    kast_pct AS kast_porcentaje,     -- José Antonio Kast's vote share

    -- CALCULATION: Combined share of the traditional "duopoly"
    -- Represents the aggregated vote for establishment candidates
    (jara_pct + kast_pct) AS jara_kast_combinados,

    -- PRIMARY CALCULATION: Parisi's advantage over the duopoly
    -- Formula: Parisi - (Jara + Kast)
    -- Interpretation:
    --   Positive value: Parisi dominates over the duopoly
    --   Negative value: The duopoly dominates over Parisi
    --   Zero: Perfect equilibrium (theoretical)
    ROUND(parisi_pct - (jara_pct + kast_pct), 2) AS diferencia_parisi_vs_duopolio,

    -- CONTEXT: Electoral volume of the commune
    -- Purpose: Distinguish between small communes (statistical noise)
    --          and large communes (statistically significant trend)
    emitidos_votos AS total_votos_emitidos

FROM resultados_elecciones

-- CRITICAL FILTER: Only communes where Parisi outpolls the duopoly
-- Condition: Parisi's share > combined Jara + Kast share
-- This filter isolates the core "anti-establishment zones"
WHERE parisi_pct > (jara_pct + kast_pct)

-- ORDER: Communes where Parisi most dominates over the duopoly (descending)
-- Purpose: Surface the strongest anti-establishment bastions
ORDER BY diferencia_parisi_vs_duopolio DESC;
