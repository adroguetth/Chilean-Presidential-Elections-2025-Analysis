-- =====================================================
-- 2. RESULTADOS NACIONALES POR CANDIDATO
-- =====================================================
-- Objetivo: Calcular y clasificar porcentaje de votación por candidato
-- Metodología: Agregación nacional + transformación estructural
-- Salida: Candidatos con su porcentaje de votación y clasificación de apoyo

WITH suma_votos AS (
    -- CTE 1: Agregación de votos por candidato a nivel nacional
    -- Propósito: Consolidar el total de votos válidos y los votos por cada candidato
    -- Nota: Los votos válidos excluyen votos nulos y blancos
    SELECT
        -- CÁLCULO: Total de votos válidos a nivel nacional
        -- Fórmula: Votos emitidos - Votos nulos - Votos blancos
        (SUM(emitidos_votos) - SUM(nulo_votos) - SUM(blanco_votos)) AS total_votos_validos,

        -- AGRUPACIONES: Suma de votos por cada candidato
        -- Cada campo representa el total nacional de votos para un candidato específico
        SUM(artes_votos) AS artes_total,
        SUM(enriquez_ominami_votos) AS meo_total,
        SUM(jara_votos) AS jara_total,
        SUM(kaiser_votos) AS kaiser_total,
        SUM(kast_votos) AS kast_total,
        SUM(matthei_votos) AS matthei_total,
        SUM(parisi_votos) AS parisi_total,
        SUM(mayne_nicholls_votos) AS mayne_nicholls_total
    FROM resultados_elecciones
),
candidatos_votos AS (
    -- CTE 2: Transformación a formato candidato-votos
    -- Propósito: Convertir la estructura columnar a formato fila para facilitar análisis
    -- Método: UNION ALL para preservar todos los registros de cada candidato
    SELECT 'Eduardo Artes' AS candidato, artes_total AS votos FROM suma_votos
    UNION ALL SELECT 'Marco Enriquez-Ominami', meo_total FROM suma_votos
    UNION ALL SELECT 'Jeannette Jara', jara_total FROM suma_votos
    UNION ALL SELECT 'Johannes Kaiser', kaiser_total FROM suma_votos
    UNION ALL SELECT 'José Antonio Kast', kast_total FROM suma_votos
    UNION ALL SELECT 'Evelyn Matthei', matthei_total FROM suma_votos
    UNION ALL SELECT 'Franco Parisi', parisi_total FROM suma_votos
    UNION ALL SELECT 'Harold Mayne-Nicholls', mayne_nicholls_total FROM suma_votos
)
-- CONSULTA FINAL: Cálculo de porcentajes y clasificación
-- Propósito: Presentar resultados con porcentajes y categorización de nivel de apoyo
SELECT
    candidato,  -- Nombre del candidato

    -- CÁLCULO: Porcentaje de votación sobre el total válido
    -- Fórmula: (Votos del candidato / Total votos válidos) * 100
    -- Precisión: Redondeado a 2 decimales
    ROUND(CAST(votos AS FLOAT) / (SELECT total_votos_validos FROM suma_votos) * 100, 2) AS votos_porcentaje,

    -- CLASIFICACIÓN: Categorización del nivel de apoyo recibido
    -- Lógica:
    --   - Alto apoyo: 20% o más de los votos válidos
    --   - Medio apoyo: Entre 10% y 19.99% de los votos válidos
    --   - Bajo apoyo: Menos del 10% de los votos válidos
    -- Propósito: Análisis cualitativo del desempeño electoral
    CASE
        WHEN ROUND(CAST(votos AS FLOAT) / (SELECT total_votos_validos FROM suma_votos) * 100, 2) >= 20 THEN 'Alto apoyo'
        WHEN ROUND(CAST(votos AS FLOAT) / (SELECT total_votos_validos FROM suma_votos) * 100, 2) >= 10 THEN 'Medio apoyo'
        ELSE 'Bajo apoyo'
    END AS nivel_apoyo

FROM candidatos_votos
-- ORDENAMIENTO: De mayor a menor porcentaje de votación
-- Propósito: Facilitar identificación de candidatos más votados
ORDER BY votos_porcentaje DESC;
