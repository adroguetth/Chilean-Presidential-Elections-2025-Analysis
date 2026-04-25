-- =====================================================
-- 6. RESULTADOS POR REGIÓN - ANÁLISIS GEOGRÁFICO
-- =====================================================
-- Objetivo: Identificar patrones regionales de apoyo
-- Metodología: Agregación regional + determinación jerárquica
-- Contexto: Análisis de distribución geográfica del voto en las 16 regiones de Chile

WITH ResultadosPorRegion AS (
    -- CTE 1: AGREGACIÓN REGIONAL DE VOTOS BRUTOS
    -- Propósito: Sumar votos por candidato y votos válidos a nivel regional
    -- Método: Suma directa de votos por candidato, cálculo de votos válidos regionales
    SELECT
        region, -- Agrupación geográfica principal (16 regiones en Chile)

        -- SUMA DE VOTOS POR CANDIDATO A NIVEL REGIONAL
        -- Base para cálculo de porcentajes regionales precisos
        SUM(jara_votos) AS jara_votos_regional,         -- Jeannette Jara
        SUM(kast_votos) AS kast_votos_regional,         -- José Antonio Kast
        SUM(parisi_votos) AS parisi_votos_regional,     -- Franco Parisi
        SUM(kaiser_votos) AS kaiser_votos_regional,     -- Johannes Kaiser
        SUM(matthei_votos) AS matthei_votos_regional,   -- Evelyn Matthei

        -- CÁLCULO: Votos válidos totales por región
        -- Fórmula: Votos emitidos - Votos blancos - Votos nulos
        -- Base legal: Ley 18.700, Artículo 109 (definición de votos válidos)
        SUM(emitidos_votos) - SUM(blanco_votos) - SUM(nulo_votos) AS votos_validos_regional

    FROM resultados_elecciones
    -- AGRUPACIÓN: Por región para consolidar resultados territoriales
    GROUP BY region  -- Produce 16 filas (una por región administrativa)
),
porcentajes_region AS (
    -- CTE 2: CÁLCULO DE PORCENTAJES REGIONALES
    -- Propósito: Calcular porcentaje regional desde votos brutos agregados
    -- Método: División de votos por candidato entre votos válidos regionales
    -- Fórmula: (Votos candidato regional / Votos válidos regional) × 100
    SELECT
        region,  -- Nombre de la región

        -- PORCENTAJES REGIONALES: Precisión de 2 decimales
        -- Transformación: De votos absolutos a porcentajes comparables
        ROUND(CAST(jara_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS jara_porcentaje,
        ROUND(CAST(kast_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS kast_porcentaje,
        ROUND(CAST(parisi_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS parisi_porcentaje,
        ROUND(CAST(kaiser_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS kaiser_porcentaje,
        ROUND(CAST(matthei_votos_regional AS FLOAT) / votos_validos_regional * 100, 2) AS matthei_porcentaje

    FROM ResultadosPorRegion
    -- Nota: Mantiene las 16 filas originales, ahora con porcentajes
)
-- CONSULTA FINAL: DETERMINACIÓN DEL GANADOR REGIONAL CON PORCENTAJES
-- Propósito: Identificar qué candidato lidera en cada región con cálculo preciso
SELECT
    region,  -- Nombre de la región (16 regiones administrativas)

    -- DETERMINACIÓN DEL GANADOR REGIONAL:
    -- Lógica: Candidato con mayor porcentaje regional gana la región
    -- Método: Comparación exhaustiva de porcentajes (cada candidato vs todos)
    -- Nota: En caso de empate exacto, el orden de evaluación determina el ganador
    CASE
        -- JEANNETTE JARA: Gana si su porcentaje es igual o mayor a todos los demás
        WHEN jara_porcentaje >= kast_porcentaje
             AND jara_porcentaje >= parisi_porcentaje
             AND jara_porcentaje >= kaiser_porcentaje
             AND jara_porcentaje >= matthei_porcentaje
        THEN 'Jeannette Jara'

        -- JOSÉ ANTONIO KAST: Gana si supera a todos los demás candidatos
        WHEN kast_porcentaje >= jara_porcentaje
             AND kast_porcentaje >= parisi_porcentaje
             AND kast_porcentaje >= kaiser_porcentaje
             AND kast_porcentaje >= matthei_porcentaje
        THEN 'José Antonio Kast'

        -- FRANCO PARISI: Gana si tiene el porcentaje más alto
        WHEN parisi_porcentaje >= jara_porcentaje
             AND parisi_porcentaje >= kast_porcentaje
             AND parisi_porcentaje >= kaiser_porcentaje
             AND parisi_porcentaje >= matthei_porcentaje
        THEN 'Franco Parisi'

        -- JOHANNES KAISER: Gana si lidera en la región
        WHEN kaiser_porcentaje >= jara_porcentaje
             AND kaiser_porcentaje >= kast_porcentaje
             AND kaiser_porcentaje >= parisi_porcentaje
             AND kaiser_porcentaje >= matthei_porcentaje
        THEN 'Johannes Kaiser'

        -- EVELYN MATTHEI: Gana si tiene el mayor porcentaje
        -- Evaluada al final según orden de precedencia establecido
        ELSE 'Evelyn Matthei'

    END AS ganador_regional,  -- Resultado: Candidato con mayor apoyo regional

    -- DATOS DE APOYO: Porcentajes regionales para todos los candidatos
    -- Propósito: Permitir análisis comparativo de fuerza relativa entre regiones
    -- Formato: Porcentajes con 2 decimales, base = votos válidos regionales
    jara_porcentaje,      -- Fuerza electoral de Jeannette Jara en la región
    kast_porcentaje,      -- Fuerza electoral de José Antonio Kast en la región
    parisi_porcentaje,    -- Fuerza electoral de Franco Parisi en la región
    kaiser_porcentaje,    -- Fuerza electoral de Johannes Kaiser en la región
    matthei_porcentaje    -- Fuerza electoral de Evelyn Matthei en la región

FROM porcentajes_region

-- ORDENAMIENTO: Por región (norte a sur)
-- Propósito: Visualización geográfica coherente que refleja la distribución territorial de Chile
-- Método: Ordenamiento secuencial basado en posición geográfica de norte a sur
-- Beneficio: Permite identificar patrones y gradientes políticos a lo largo del territorio nacional
ORDER BY
    CASE region
        WHEN 'Arica y Parinacota' THEN 1   -- Región más al norte
        WHEN 'Tarapacá' THEN 2
        WHEN 'Antofagasta' THEN 3
        WHEN 'Atacama' THEN 4
        WHEN 'Coquimbo' THEN 5
        WHEN 'Valparaíso' THEN 6
        WHEN 'Metropolitana' THEN 7        -- Región central
        WHEN 'Libertador' THEN 8
        WHEN 'Maule' THEN 9
        WHEN 'Ñuble' THEN 10
        WHEN 'Biobío' THEN 11
        WHEN 'La Araucanía' THEN 12
        WHEN 'Los Ríos' THEN 13
        WHEN 'Los Lagos' THEN 14
        WHEN 'Aysén' THEN 15
        WHEN 'Magallanes' THEN 16          -- Región más al sur
        ELSE 99  -- Categoría residual para cualquier valor inesperado
    END;
