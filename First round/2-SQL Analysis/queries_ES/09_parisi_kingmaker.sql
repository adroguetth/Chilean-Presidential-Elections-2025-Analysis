-- =====================================================
-- 9. FENÓMENO "VOTO ANTISISTEMA" - PARISI vs DÚOPOLIO
-- =====================================================
-- Objetivo: Identificar comunas donde Parisi supera la suma de Jara y Kast
-- Contexto: Análisis del voto de protesta contra el establishment político
-- Metodología: Comparación directa de porcentajes entre candidato antisistema
--              vs la suma de los candidatos del duopolio tradicional
-- Hipótesis: Comunidades donde el rechazo al sistema supera la lealtad partidaria

SELECT
    comuna,                          -- Unidad territorial básica de análisis
    region,                          -- Contexto geográfico regional
    parisi_pct AS parisi_porcentaje, -- Porcentaje obtenido por Franco Parisi

    jara_pct AS jara_porcentaje,     -- Porcentaje obtenido por Jeannette Jara
    kast_pct AS kast_porcentaje,     -- Porcentaje obtenido por José Antonio Kast

    -- CÁLCULO: Suma de porcentajes del "duopolio" tradicional
    -- Representa la votación combinada de candidatos del establishment
    (jara_pct + kast_pct) AS jara_kast_combinados,

    -- CÁLCULO PRINCIPAL: Diferencia entre Parisi y el duopolio
    -- Fórmula: Parisi - (Jara + Kast)
    -- Interpretación:
    --   Valor positivo: Parisi domina sobre el duopolio
    --   Valor negativo: El duopolio domina sobre Parisi
    --   Cero: Equilibrio perfecto (teórico)
    ROUND(parisi_pct - (jara_pct + kast_pct), 2) AS diferencia_parisi_vs_duopolio,

    -- CONTEXTO: Volumen electoral de la comuna
    -- Propósito: Diferenciar entre comunas pequeñas (efecto estadístico)
    --            y grandes (tendencia significativa)
    emitidos_votos AS total_votos_emitidos

FROM resultados_elecciones

-- FILTRO CRÍTICO: Solo comunas donde Parisi supera al duopolio
-- Condición: Porcentaje de Parisi > Suma de porcentajes de Jara y Kast
-- Este filtro identifica las "zonas antisistema" por excelencia
WHERE parisi_pct > (jara_pct + kast_pct)

-- ORDENAMIENTO: Comunas donde Parisi domina más sobre el duopolio
-- Propósito: Identificar los bastiones más sólidos del voto antisistema
ORDER BY diferencia_parisi_vs_duopolio DESC;
