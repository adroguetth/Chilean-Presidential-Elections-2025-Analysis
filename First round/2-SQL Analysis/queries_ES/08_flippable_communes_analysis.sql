-- =====================================================
-- 8. ANÁLISIS DE COMUNAS RECUPERABLES (DIFERENCIA < 1000 VOTOS)
-- =====================================================
-- Objetivo: Identificar comunas donde la diferencia entre Jara y Kast es menor a 1000 votos
-- Metodología: Cálculo de votos absolutos + análisis de márgenes competitivos
-- Contexto Estratégico: Estas comunas representan "territorios pivotales" donde pequeños
--                      cambios en la campaña podrían cambiar el resultado en segunda vuelta
-- Umbral Crítico: 1000 votos (ajustable según contexto electoral)

WITH votos_comuna AS (
    -- CTE 1: PREPARACIÓN DE DATOS POR COMUNA
    -- Propósito: Calcular votos válidos y preparar datos base para análisis
    -- Nota: Solo se consideran votos válidos (excluyen nulos y blancos)
    SELECT
        comuna,          -- Unidad territorial básica
        region,          -- Contexto geográfico regional
        -- CÁLCULO: Votos válidos por comuna
        -- Fórmula: Votos emitidos - Votos nulos - Votos blancos
        (emitidos_votos - nulo_votos - blanco_votos) AS votos_validos,
        jara_pct,        -- Porcentaje de Jeannette Jara (formato: 0-100)
        kast_pct         -- Porcentaje de José Antonio Kast (formato: 0-100)
    FROM resultados_elecciones
),
votos_absolutos AS (
    -- CTE 2: CONVERSIÓN A VOTOS ABSOLUTOS Y CÁLCULO DE DIFERENCIAS
    -- Propósito: Transformar porcentajes a números absolutos y calcular márgenes
    -- Método: Porcentaje × Votos válidos / 100
    SELECT
        comuna,
        region,
        -- CONVERSIÓN: Porcentajes a votos absolutos
        -- Jara: (porcentaje / 100) × votos válidos
        ROUND((jara_pct / 100.0) * votos_validos, 0) AS votos_jara,
        -- Kast: (porcentaje / 100) × votos válidos
        ROUND((kast_pct / 100.0) * votos_validos, 0) AS votos_kast,
        -- CÁLCULO: Diferencia absoluta entre ambos candidatos
        -- Fórmula: |Votos Jara - Votos Kast|
        -- Propósito: Medir cuán competitiva es la comuna
        ABS(
            ROUND((jara_pct / 100.0) * votos_validos, 0) -
            ROUND((kast_pct / 100.0) * votos_validos, 0)
        ) AS diferencia_votos
    FROM votos_comuna
    -- FILTRO: Solo comunas donde ambos candidatos tienen votos (> 0%)
    -- Excluye comunas donde uno de ellos no compitió o tuvo 0 apoyo
    WHERE jara_pct > 0 AND kast_pct > 0
),
analisis_jara AS (
    -- CTE 3: ANÁLISIS DE COMUNAS RECUPERABLES PARA JEANNETTE JARA
    -- Propósito: Identificar dónde Jara perdió por menos de 1000 votos
    -- Contexto: Comunas donde Kast ganó pero el margen es pequeño
    SELECT
        'Jeannette Jara' AS candidato_analizado,
        -- MÉTRICA 1: Cantidad de comunas recuperables
        COUNT(*) AS comunas_recuperables,
        -- MÉTRICA 2: Total de votos necesarios para dar vuelta resultados
        -- Si Jara gana estos votos, gana las comunas
        SUM(diferencia_votos) AS votos_necesarios_totales,
        -- MÉTRICA 3: Promedio de votos necesarios por comuna
        ROUND(AVG(diferencia_votos), 0) AS promedio_votos_necesarios
    FROM votos_absolutos
    WHERE
        -- CONDICIÓN: Jara perdió en esta comuna
        votos_kast > votos_jara
        -- CONDICIÓN: La diferencia es menor a 1000 votos (UMBRAL CRÍTICO)
        AND diferencia_votos < 1000
),
analisis_kast AS (
    -- CTE 4: ANÁLISIS DE COMUNAS RECUPERABLES PARA JOSÉ ANTONIO KAST
    -- Propósito: Identificar dónde Kast perdió por menos de 1000 votos
    -- Contexto: Comunas donde Jara ganó pero el margen es pequeño
    SELECT
        'José Antonio Kast' AS candidato_analizado,
        COUNT(*) AS comunas_recuperables,
        SUM(diferencia_votos) AS votos_necesarios_totales,
        ROUND(AVG(diferencia_votos), 0) AS promedio_votos_necesarios
    FROM votos_absolutos
    WHERE
        -- CONDICIÓN: Kast perdió en esta comuna
        votos_jara > votos_kast
        -- CONDICIÓN: La diferencia es menor a 1000 votos (UMBRAL CRÍTICO)
        AND diferencia_votos < 1000
)
-- CONSULTA FINAL: REPORTE COMPARATIVO DE RECUPERABILIDAD
-- Propósito: Presentar panorama estratégico para ambos candidatos
SELECT
    candidato_analizado,
    comunas_recuperables,
    -- INTERPRETACIÓN: Total de votos que necesitaría movilizar/convencer
    votos_necesarios_totales,
    -- INTERPRETACIÓN: Esfuerzo promedio por comuna
    promedio_votos_necesarios,
    -- ANÁLISIS ESTRATÉGICO: Clasificación del desafío
    CASE
        WHEN votos_necesarios_totales < 5000 THEN 'Desafío menor'
        WHEN votos_necesarios_totales < 20000 THEN 'Desafío moderado'
        ELSE 'Desafío significativo'
    END AS nivel_dificultad
FROM (
    SELECT * FROM analisis_jara
    UNION ALL
    SELECT * FROM analisis_kast
) resultados
-- ORDENAMIENTO: Por candidato (Jara primero, luego Kast)
ORDER BY candidato_analizado;
