-- =====================================================
-- 1. ESTADÍSTICAS GENERALES DE PARTICIPACIÓN ELECTORAL
-- =====================================================
-- Objetivo: Calcular métricas fundamentales de participación ciudadana
-- Contexto: Base para todos los análisis posteriores

WITH participacion_nacional AS (
-- CTE 1: Agregación de resultados electorales a nivel nacional
-- Propósito: Consolidar las métricas básicas de participación electoral para todo el territorio
-- Nota: Esta CTE sirve como base para todos los cálculos posteriores de porcentajes
SELECT
    -- MÉTRICA 1: COBERTURA GEOGRÁFICA DEL ANÁLISIS
    -- Representa el 100% del territorio electoral nacional
    -- Unidad: cantidad de comunas
    COUNT(*) AS total_comunas,

    -- MÉTRICA 2: PARTICIPACIÓN CIUDADANA ABSOLUTA
    -- Total de votos emitidos (base para cálculos porcentuales)
    -- Unidad: cantidad de votos
    SUM(emitidos_votos) AS total_votos_emitidos,

    -- MÉTRICA 3: VOTO DE PROTESTA PASIVA
    -- Votos blancos: expresión de descontento no vinculado a candidatos
    -- Unidad: cantidad de votos
    SUM(blanco_votos) AS total_votos_blancos,

    -- MÉTRICA 4: VOTO DE PROTESTA ACTIVA
    -- Votos nulos: expresión de rechazo al sistema electoral
    -- Unidad: cantidad de votos
    SUM(nulo_votos) AS total_votos_nulos,

    -- MÉTRICA 5: VOTO VÁLIDO (CÁLCULO DERIVADO)
    -- Diferencia entre emitidos y (blancos + nulos)
    -- Representa los votos que efectivamente fueron asignados a candidatos
    -- Unidad: cantidad de votos
    SUM(emitidos_votos) - (SUM(blanco_votos) + SUM(nulo_votos)) AS total_votos_validos
FROM resultados_elecciones  -- Tabla fuente: resultados electorales por comuna
),
Estadisticas AS (
-- CTE 2: Transformación de métricas a formato indicador-valor
-- Propósito: Convertir las métricas agregadas a un formato tabular legible para reporting
-- Estructura de salida: dos columnas (indicador, valor)
SELECT 'Total comunas' AS indicador, total_comunas AS valor FROM participacion_nacional
UNION ALL
SELECT 'Total votos emitidos', total_votos_emitidos FROM participacion_nacional
UNION ALL
SELECT 'Total votos blancos', total_votos_blancos FROM participacion_nacional
UNION ALL
-- MÉTRICA DERIVADA 1: Porcentaje de votos blancos sobre el total emitido
-- Interpretación: Proporción de electores que ejercieron protesta pasiva
SELECT 'Porcentaje votos blancos',
       ROUND(CAST(total_votos_blancos AS FLOAT) / total_votos_emitidos * 100, 2)
       FROM participacion_nacional
UNION ALL
SELECT 'Total votos nulos', total_votos_nulos FROM participacion_nacional
UNION ALL
-- MÉTRICA DERIVADA 2: Porcentaje de votos nulos sobre el total emitido
-- Interpretación: Proporción de electores que ejercieron protesta activa
SELECT 'Porcentaje votos nulos',
       ROUND(CAST(total_votos_nulos AS FLOAT) / total_votos_emitidos * 100, 2)
       FROM participacion_nacional
UNION ALL
SELECT 'Total votos válidos', total_votos_validos FROM participacion_nacional
UNION ALL
-- MÉTRICA DERIVADA 3: Porcentaje de votos válidos sobre el total emitido
-- Interpretación: Proporción de votos que efectivamente eligieron candidatos
-- Nota: Este es el indicador clave de participación efectiva en el proceso
SELECT 'Porcentaje votos válidos',
       ROUND(CAST(total_votos_validos AS FLOAT) / total_votos_emitidos * 100, 2)
       FROM participacion_nacional
)
-- CONSULTA FINAL: Presentación de resultados
-- Propósito: Mostrar todas las métricas de participación electoral en formato de reporte
-- Orden de resultados: Según el orden definido en la CTE Estadisticas
SELECT * FROM Estadisticas;
