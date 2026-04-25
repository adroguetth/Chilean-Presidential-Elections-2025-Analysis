-- =====================================================
-- 3. IDENTIFICACIÓN DE CANDIDATOS PARA SEGUNDA VUELTA
-- =====================================================
-- Objetivo: Determinar los dos candidatos más votados según ley chilena
-- Metodología: Porcentaje calculado sobre votos válidos (excluye nulos y blancos)
-- Base Legal: Ley 18.700 - Sistema de dos vueltas
-- Criterio: Los dos candidatos con mayor porcentaje de votos válidos pasan a segunda vuelta

WITH suma_votos AS (
    -- CTE 1: Agregación nacional de votos por candidato
    -- Propósito: Calcular el total de votos válidos y los votos individuales por candidato
    -- Nota: Según la ley electoral chilena, solo se consideran votos válidos
    SELECT
        -- CÁLCULO: Total de votos válidos a nivel nacional
        -- Fórmula: Votos emitidos - Votos nulos - Votos blancos
        -- Base legal: Ley 18.700, Artículo 109
        SUM(emitidos_votos) - SUM(nulo_votos) - SUM(blanco_votos) AS total_votos_validos,

        -- AGRUPACIONES: Suma de votos por cada candidato presidencial
        -- Orden: Los candidatos están listados según orden de aparición en el código original
        SUM(jara_votos) AS jara_total,
        SUM(kast_votos) AS kast_total,
        SUM(parisi_votos) AS parisi_total,
        SUM(kaiser_votos) AS kaiser_total,
        SUM(matthei_votos) AS matthei_total,
        SUM(mayne_nicholls_votos) AS mayne_nicholls_total,
        SUM(enriquez_ominami_votos) AS meo_total,
        SUM(artes_votos) AS artes_total
    FROM resultados_elecciones
),
porcentajes_candidatos AS (
    -- CTE 2: Cálculo de porcentajes individuales
    -- Propósito: Calcular el porcentaje de votos válidos obtenido por cada candidato
    -- Método: Unión de consultas individuales para cada candidato
    -- Fórmula: (Votos del candidato / Total votos válidos) * 100
    SELECT
        'Jeannette Jara' AS candidato,
        ROUND(CAST(jara_total AS FLOAT) / total_votos_validos * 100, 2) AS porcentaje
    FROM suma_votos

    UNION ALL  -- Mantiene todos los registros incluyendo duplicados (no hay en este caso)

    SELECT
        'José Antonio Kast',
        ROUND(CAST(kast_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Franco Parisi',
        ROUND(CAST(parisi_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Johannes Kaiser',
        ROUND(CAST(kaiser_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Evelyn Matthei',
        ROUND(CAST(matthei_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Harold Mayne-Nicholls',
        ROUND(CAST(mayne_nicholls_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Marco Enriquez-Ominami',
        ROUND(CAST(meo_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos

    UNION ALL

    SELECT
        'Eduardo Artes',
        ROUND(CAST(artes_total AS FLOAT) / total_votos_validos * 100, 2)
    FROM suma_votos
),
ranking_candidatos AS (
    -- CTE 3: Clasificación por orden de votación
    -- Propósito: Ordenar candidatos de mayor a menor porcentaje y asignar posición
    -- Método: ROW_NUMBER() para ranking secuencial sin empates
    -- Nota: En caso de empate exacto, el orden se define por la secuencia del UNION ALL
    SELECT
        candidato,
        porcentaje,
        ROW_NUMBER() OVER (ORDER BY porcentaje DESC) AS posicion  -- Ranking descendente
    FROM porcentajes_candidatos
)
-- CONSULTA FINAL: Identificación de candidatos para segunda vuelta
-- Propósito: Mostrar los dos candidatos más votados con análisis contextual
-- Criterio de selección: WHERE posicion <= 2 (primer y segundo lugar)
SELECT
    candidato,  -- Nombre del candidato
    porcentaje,  -- Porcentaje de votos válidos obtenidos

    -- CLASIFICACIÓN: Posición en el ranking electoral
    -- Propósito: Identificar claramente al primer y segundo lugar
    CASE
        WHEN posicion = 1 THEN '1er Lugar'
        WHEN posicion = 2 THEN '2do Lugar'
    END AS posicion,

    -- ANÁLISIS: Contexto competitivo del resultado
    -- Propósito: Interpretación cualitativa del porcentaje obtenido
    -- Criterios:
    --   - Mayoría absoluta: Más del 50% (evitaría segunda vuelta según ley)
    --   - Umbral competitivo: Más del 20% (considerado competitivo)
    --   - Umbral mínimo: Menos del 20% (baja competitividad)
    -- Base legal: Ley 18.700, Artículo 110 (mayoría absoluta)
    CASE
        WHEN porcentaje > 50 THEN 'Mayoría absoluta (Sin 2da vuelta)'
        WHEN porcentaje > 20 THEN 'Umbral competitivo'
        ELSE 'Umbral mínimo'
    END AS contexto_competitividad

FROM ranking_candidatos
-- FILTRO: Solo los dos primeros candidatos
-- Propósito: Identificar quiénes pasarían a segunda vuelta
WHERE posicion <= 2
-- ORDENAMIENTO: Por posición ascendente (1° luego 2°)
-- Propósito: Presentación clara del orden de clasificación
ORDER BY posicion;
