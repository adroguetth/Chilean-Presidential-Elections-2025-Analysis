-- =====================================================
-- 5. MAPEO TERRITORIAL DE VICTORIAS POR CANDIDATO
-- =====================================================
-- Objetivo: Determinar número de comunas ganadas por cada candidato
-- Metodología: Análisis exhaustivo por comuna (346 comunas en total)
-- Contexto: Muestra la distribución geográfica del poder electoral por territorio

WITH victorias_por_candidato AS (
    -- CTE 1: Determinación del candidato ganador en cada comuna
    -- Propósito: Identificar quién obtuvo el mayor porcentaje de votos en cada territorio
    -- Método: Comparación exhaustiva de porcentajes entre todos los candidatos
    SELECT
        comuna,  -- Unidad territorial básica de análisis

        -- LÓGICA DE DETERMINACIÓN DEL GANADOR:
        -- Compara el porcentaje de cada candidato contra todos los demás
        -- El candidato con el porcentaje más alto gana la comuna
        -- Nota: En caso de empate exacto, el orden de evaluación determina el ganador
        CASE
            -- JEANNETTE JARA: Gana si su porcentaje es igual o mayor a todos los demás
            WHEN jara_pct >= kast_pct AND jara_pct >= parisi_pct AND jara_pct >= kaiser_pct
                 AND jara_pct >= matthei_pct AND jara_pct >= mayne_nicholls_pct
                 AND jara_pct >= enriquez_ominami_pct AND jara_pct >= artes_pct
            THEN 'Jeannette Jara'

            -- JOSÉ ANTONIO KAST: Gana si supera a todos los demás candidatos
            WHEN kast_pct >= jara_pct AND kast_pct >= parisi_pct AND kast_pct >= kaiser_pct
                 AND kast_pct >= matthei_pct AND kast_pct >= mayne_nicholls_pct
                 AND kast_pct >= enriquez_ominami_pct AND kast_pct >= artes_pct
            THEN 'José Antonio Kast'

            -- FRANCO PARISI: Gana si tiene el porcentaje más alto
            WHEN parisi_pct >= jara_pct AND parisi_pct >= kast_pct AND parisi_pct >= kaiser_pct
                 AND parisi_pct >= matthei_pct AND parisi_pct >= mayne_nicholls_pct
                 AND parisi_pct >= enriquez_ominami_pct AND parisi_pct >= artes_pct
            THEN 'Franco Parisi'

            -- JOHANNES KAISER: Gana si lidera en la comuna
            WHEN kaiser_pct >= jara_pct AND kaiser_pct >= kast_pct AND kaiser_pct >= parisi_pct
                 AND kaiser_pct >= matthei_pct AND kaiser_pct >= mayne_nicholls_pct
                 AND kaiser_pct >= enriquez_ominami_pct AND kaiser_pct >= artes_pct
            THEN 'Johannes Kaiser'

            -- EVELYN MATTHEI: Gana si tiene el mayor porcentaje
            WHEN matthei_pct >= jara_pct AND matthei_pct >= kast_pct AND matthei_pct >= parisi_pct
                 AND matthei_pct >= kaiser_pct AND matthei_pct >= mayne_nicholls_pct
                 AND matthei_pct >= enriquez_ominami_pct AND matthei_pct >= artes_pct
            THEN 'Evelyn Matthei'

            -- CATEGORÍA RESIDUAL: Para candidatos no incluidos en el análisis principal
            -- Incluye: Harold Mayne-Nicholls, Marco Enriquez-Ominami, Eduardo Artes
            ELSE 'Otro'
        END AS candidato_ganador  -- Resultado: Candidato que gana en la comuna

    FROM resultados_elecciones  -- Tabla fuente con resultados por comuna
)
-- CONSULTA FINAL: Agregación y análisis de victorias territoriales
-- Propósito: Resumir cuántas comunas ganó cada candidato y su porcentaje territorial
SELECT
    candidato_ganador AS candidato,       -- Nombre del candidato o categoría
    COUNT(*) AS comunas_ganadas,          -- Número total de comunas donde ganó

    -- CÁLCULO: Porcentaje del territorio nacional controlado
    -- Fórmula: (Comunas ganadas / Total comunas en Chile) * 100
    -- Total de referencia: 346 comunas (división administrativa vigente)
    -- Precisión: Un decimal para análisis territorial
    ROUND(CAST(COUNT(*) AS FLOAT) / 346 * 100, 1) AS porcentaje_comunas

FROM victorias_por_candidato
-- AGRUPACIÓN: Por candidato para consolidar resultados
GROUP BY candidato_ganador
-- ORDENAMIENTO: De mayor a menor número de comunas ganadas
-- Propósito: Identificar rápidamente al candidato con mayor alcance territorial
ORDER BY comunas_ganadas DESC;
