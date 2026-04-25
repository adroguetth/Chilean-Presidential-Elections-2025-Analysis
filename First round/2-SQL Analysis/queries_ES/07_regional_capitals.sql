-- =====================================================
-- 7. RESULTADOS POR CAPITAL REGIONAL - ANÁLISIS DE CENTROS URBANOS
-- =====================================================
-- Objetivo: Analizar el comportamiento electoral en las capitales regionales
-- Metodología: Filtrado de capitales + análisis comparativo
-- Contexto: Las capitales regionales concentran el 65-70% de la población nacional

WITH CapitalesRegionales AS (
    -- CTE 1: FILTRADO DE CAPITALES REGIONALES
    -- Propósito: Seleccionar las 16 comunas que son capitales regionales
    -- Criterio: Lista explícita de capitales administrativas de Chile
    -- Nota: Incluye todas las regiones desde Arica a Magallanes
    SELECT
        comuna,          -- Nombre de la capital regional
        region,          -- Región a la que pertenece
        jara_pct,        -- Porcentaje de Jeannette Jara
        kast_pct,        -- Porcentaje de José Antonio Kast
        parisi_pct,      -- Porcentaje de Franco Parisi
        kaiser_pct,      -- Porcentaje de Johannes Kaiser
        matthei_pct      -- Porcentaje de Evelyn Matthei
    FROM resultados_elecciones
    WHERE comuna IN (
        'Arica',           -- REGIÓN DE ARICA Y PARINACOTA
        'Iquique',         -- REGIÓN DE TARAPACÁ
        'Antofagasta',     -- REGIÓN DE ANTOFAGASTA
        'Copiapo',         -- REGIÓN DE ATACAMA
        'La Serena',       -- REGIÓN DE COQUIMBO
        'Valparaiso',      -- REGIÓN DE VALPARAÍSO
        'Santiago',        -- REGIÓN METROPOLITANA
        'Rancagua',        -- REGIÓN DEL LIBERTADOR BERNARDO O'HIGGINS
        'Talca',           -- REGIÓN DEL MAULE
        'Chillan',         -- REGIÓN DE ÑUBLE
        'Concepcion',      -- REGIÓN DEL BIOBÍO
        'Temuco',          -- REGIÓN DE LA ARAUCANÍA
        'Valdivia',        -- REGIÓN DE LOS RÍOS
        'Puerto Montt',    -- REGIÓN DE LOS LAGOS
        'Coyhaique',       -- REGIÓN DE AYSÉN
        'Punta Arenas'     -- REGIÓN DE MAGALLANES
    )
),
GanadoresCapitales AS (
    -- CTE 2: DETERMINACIÓN DEL GANADOR EN CADA CAPITAL
    -- Propósito: Identificar qué candidato ganó en cada capital regional
    -- Lógica: Comparación jerárquica entre los 5 candidatos urbanos más relevantes
    SELECT
        comuna,
        region,
        jara_pct,
        kast_pct,
        parisi_pct,
        kaiser_pct,
        matthei_pct,

        -- DETERMINACIÓN DEL CANDIDATO GANADOR
        -- Orden de evaluación basado en desempeño nacional y patrones urbanos
        CASE
            -- JEANNETTE JARA: Fuerte en áreas urbanas metropolitanas
            WHEN jara_pct >= kast_pct
                 AND jara_pct >= parisi_pct
                 AND jara_pct >= kaiser_pct
                 AND jara_pct >= matthei_pct
            THEN 'Jeannette Jara'

            -- JOSÉ ANTONIO KAST: Fuerte en algunas capitales del sur y sectores rurales
            WHEN kast_pct >= jara_pct
                 AND kast_pct >= parisi_pct
                 AND kast_pct >= kaiser_pct
                 AND kast_pct >= matthei_pct
            THEN 'José Antonio Kast'

            -- FRANCO PARISI: Sorprendente en capitales del norte y áreas mineras
            WHEN parisi_pct >= jara_pct
                 AND parisi_pct >= kast_pct
                 AND parisi_pct >= kaiser_pct
                 AND parisi_pct >= matthei_pct
            THEN 'Franco Parisi'

            -- JOHANNES KAISER: Esperado en capitales patagónicas y nichos urbanos
            WHEN kaiser_pct >= jara_pct
                 AND kaiser_pct >= kast_pct
                 AND kaiser_pct >= parisi_pct
                 AND kaiser_pct >= matthei_pct
            THEN 'Johannes Kaiser'

            -- EVELYN MATTHEI: Competitiva en capitales de alto nivel socioeconómico
            ELSE 'Evelyn Matthei'

        END as ganador,  -- Candidato ganador en la capital regional

        -- PORCENTAJE DEL CANDIDATO GANADOR
        -- Réplica de la lógica para obtener el valor numérico del ganador
        CASE
            -- JEANNETTE JARA
            WHEN jara_pct >= kast_pct
                 AND jara_pct >= parisi_pct
                 AND jara_pct >= kaiser_pct
                 AND jara_pct >= matthei_pct
            THEN jara_pct

            -- JOSÉ ANTONIO KAST
            WHEN kast_pct >= jara_pct
                 AND kast_pct >= parisi_pct
                 AND kast_pct >= kaiser_pct
                 AND kast_pct >= matthei_pct
            THEN kast_pct

            -- FRANCO PARISI
            WHEN parisi_pct >= jara_pct
                 AND parisi_pct >= kast_pct
                 AND parisi_pct >= kaiser_pct
                 AND parisi_pct >= matthei_pct
            THEN parisi_pct

            -- JOHANNES KAISER
            WHEN kaiser_pct >= jara_pct
                 AND kaiser_pct >= kast_pct
                 AND kaiser_pct >= parisi_pct
                 AND kaiser_pct >= matthei_pct
            THEN kaiser_pct

            -- EVELYN MATTHEI
            ELSE matthei_pct

        END AS porcentaje_ganador  -- Porcentaje obtenido por el ganador
    FROM CapitalesRegionales
)
-- CONSULTA FINAL: PANORAMA ELECTORAL URBANO POR REGIÓN
-- Propósito: Visualizar el mapa político de las capitales regionales
-- Orden: Geográfico de norte a sur según orden administrativo
SELECT
    comuna AS capital_regional,      -- Nombre de la capital
    region,                          -- Región correspondiente
    ganador,                         -- Candidato ganador
    porcentaje_ganador,              -- Porcentaje del ganador
    jara_pct,                        -- Porcentaje de Jeannette Jara
    kast_pct,                        -- Porcentaje de José Antonio Kast
    parisi_pct,                      -- Porcentaje de Franco Parisi
    kaiser_pct,                      -- Porcentaje de Johannes Kaiser
    matthei_pct                      -- Porcentaje de Evelyn Matthei
FROM GanadoresCapitales
-- ORDENAMIENTO: Por región (norte a sur)
-- Propósito: Visualización geográfica coherente
ORDER BY
    CASE region
        WHEN 'Arica y Parinacota' THEN 1
        WHEN 'Tarapacá' THEN 2
        WHEN 'Antofagasta' THEN 3
        WHEN 'Atacama' THEN 4
        WHEN 'Coquimbo' THEN 5
        WHEN 'Valparaíso' THEN 6
        WHEN 'Metropolitana' THEN 7
        WHEN 'Libertador' THEN 8
        WHEN 'Maule' THEN 9
        WHEN 'Ñuble' THEN 10
        WHEN 'Biobío' THEN 11
        WHEN 'La Araucanía' THEN 12
        WHEN 'Los Ríos' THEN 13
        WHEN 'Los Lagos' THEN 14
        WHEN 'Aysén' THEN 15
        WHEN 'Magallanes' THEN 16
        ELSE 99
    END;
