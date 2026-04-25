-- =====================================================
-- 4. BASTIONES ELECTORALES: TOP 10 COMUNAS POR CANDIDATO
-- =====================================================
-- Objetivo: Identificar y analizar las comunas donde cada uno de los 5 candidatos
--           más votados obtuvo su mayor porcentaje de apoyo, determinando si fueron
--           efectivamente ganadores en esos territorios.

-- Contexto Estratégico: Este análisis revela los "bastiones electorales" de cada
--                      candidato, mostrando sus zonas de mayor influencia y la
--                      distribución geográfica de su apoyo político a nivel nacional

-- Metodología: Consultas paralelas para cada candidato + determinación de victoria
--              por comuna + ranking por porcentaje de votación.

-- PERFILES POLÍTICOS DE LOS CANDIDATOS ANALIZADOS:
-- 1. Jeannette Jara: Izquierda oficialista (Boric - Unidad por Chile)
-- 2. José Antonio Kast: Derecha conservadora (Partido Republicano)
-- 3. Franco Parisi: Tercera vía (Partido de la Gente)
-- 4. Johannes Kaiser: Derecha libertaria (Partido Nacional Libertario)
-- 5. Evelyn Matthei: Derecha histórica - Piñerismo (Chile Vamos)

-- =====================================================
-- 4.1 JEANNETTE JARA - IZQUIERDA OFICIALISTA (UNIDAD POR CHILE)
-- =====================================================
-- Análisis: Jara domina en comunas populares del Gran Santiago y Valparaíso
-- Perfil electoral: Zonas urbanas, poblacionales, sectores trabajadores
SELECT TOP 10
    comuna,                     -- Nombre de la comuna
    region,                     -- Región administrativa
    jara_pct AS porcentaje,     -- Porcentaje de votos obtenido por Jara en la comuna

    -- DETERMINACIÓN DE VICTORIA LOCAL:
    -- Compara el porcentaje de Jara contra todos los demás candidatos
    -- Si tiene el mayor porcentaje, gana en esa comuna
    CASE
        WHEN jara_pct >= artes_pct AND
             jara_pct >= enriquez_ominami_pct AND
             jara_pct >= kaiser_pct AND
             jara_pct >= kast_pct AND
             jara_pct >= matthei_pct AND
             jara_pct >= mayne_nicholls_pct AND
             jara_pct >= parisi_pct
        THEN 'Gana en esa comuna'
        ELSE 'Pierde en esa comuna'
    END AS ganador_comuna  -- Resultado electoral en el territorio

FROM resultados_elecciones
-- ORDENAMIENTO: Comunas con mayor porcentaje de apoyo a Jara (descendente)
-- Propósito: Identificar los bastiones más sólidos del candidato
ORDER BY jara_pct DESC;

-- =====================================================
-- 4.2 JOSÉ ANTONIO KAST - DERECHA CONSERVADORA (PARTIDO REPUBLICANO)
-- =====================================================
-- Análisis: Kast domina en comunas rurales de Maule, Araucanía y extremo sur
-- Perfil electoral: Zonas rurales, conservadoras, con alta identidad local
SELECT TOP 10
    comuna,
    region,
    kast_pct AS porcentaje,     -- Porcentaje de votos obtenido por Kast en la comuna

    -- DETERMINACIÓN DE VICTORIA LOCAL:
    -- Compara el porcentaje de Kast contra todos los demás candidatos
    CASE
        WHEN kast_pct >= artes_pct AND
             kast_pct >= enriquez_ominami_pct AND
             kast_pct >= kaiser_pct AND
             kast_pct >= jara_pct AND
             kast_pct >= matthei_pct AND
             kast_pct >= mayne_nicholls_pct AND
             kast_pct >= parisi_pct
        THEN 'Gana en esa comuna'
        ELSE 'Pierde en esa comuna'
    END AS resultado_comuna

FROM resultados_elecciones
-- ORDENAMIENTO: Comunas con mayor porcentaje de apoyo a Kast
ORDER BY kast_pct DESC;

-- =====================================================
-- 4.3 FRANCO PARISI - TERCERA VÍA (PARTIDO DE LA GENTE)
-- =====================================================
-- Análisis: Parisi domina absolutamente en el norte grande (Tarapacá, Antofagasta)
-- Perfil electoral: Zonas mineras, descontento con partidos tradicionales
SELECT TOP 10
    comuna,
    region,
    parisi_pct AS porcentaje,   -- Porcentaje de votos obtenido por Parisi en la comuna

    -- DETERMINACIÓN DE VICTORIA LOCAL:
    -- Compara el porcentaje de Parisi contra todos los demás candidatos
    CASE
        WHEN parisi_pct >= artes_pct AND
             parisi_pct >= enriquez_ominami_pct AND
             parisi_pct >= kaiser_pct AND
             parisi_pct >= kast_pct AND
             parisi_pct >= matthei_pct AND
             parisi_pct >= mayne_nicholls_pct AND
             parisi_pct >= jara_pct
        THEN 'Gana en esa comuna'
        ELSE 'Pierde en esa comuna'
    END AS resultado_comuna

FROM resultados_elecciones
-- ORDENAMIENTO: Comunas con mayor porcentaje de apoyo a Parisi
ORDER BY parisi_pct DESC;

-- =====================================================
-- 4.4 JOHANNES KAISER - DERECHA LIBERTARIA (PARTIDO NACIONAL LIBERTARIO)
-- =====================================================
-- Análisis: Kaiser tiene fuerza en la Patagonia, pero compite con Kast en varias comunas
-- Perfil electoral: Zonas extremas, jóvenes profesionales, votantes anti-estatistas
SELECT TOP 10
    comuna,
    region,
    kaiser_pct AS porcentaje,   -- Porcentaje de votos obtenido por Kaiser en la comuna

    -- DETERMINACIÓN DE VICTORIA LOCAL:
    -- Compara el porcentaje de Kaiser contra todos los demás candidatos
    CASE
        WHEN kaiser_pct >= artes_pct AND
             kaiser_pct >= enriquez_ominami_pct AND
             kaiser_pct >= jara_pct AND
             kaiser_pct >= kast_pct AND
             kaiser_pct >= matthei_pct AND
             kaiser_pct >= mayne_nicholls_pct AND
             kaiser_pct >= parisi_pct
        THEN 'Gana en esa comuna'
        ELSE 'Pierde en esa comuna'
    END AS resultado_comuna

FROM resultados_elecciones
-- ORDENAMIENTO: Comunas con mayor porcentaje de apoyo a Kaiser
ORDER BY kaiser_pct DESC;

-- =====================================================
-- 4.5 EVELYN MATTHEI - DERECHA HISTÓRICA (CHILE VAMOS)
-- =====================================================
-- Análisis: Matthei domina en comunas de alto nivel socioeconómico,
--           pierde en algunas ante Kast
-- Perfil electoral: Sectores acomodados urbanos, votantes tradicionales de derecha
SELECT TOP 10
    comuna,
    region,
    matthei_pct AS porcentaje,  -- Porcentaje de votos obtenido por Matthei en la comuna

    -- DETERMINACIÓN DE VICTORIA LOCAL:
    -- Compara el porcentaje de Matthei contra todos los demás candidatos
    -- Nota: Competencia directa con Kast por el electorado de derecha
    CASE
        WHEN matthei_pct >= artes_pct AND
             matthei_pct >= enriquez_ominami_pct AND
             matthei_pct >= kaiser_pct AND
             matthei_pct >= kast_pct AND
             matthei_pct >= jara_pct AND
             matthei_pct >= mayne_nicholls_pct AND
             matthei_pct >= parisi_pct
        THEN 'Gana en esa comuna'
        ELSE 'Pierde en esa comuna'
    END AS resultado_comuna

FROM resultados_elecciones
-- ORDENAMIENTO: Comunas con mayor porcentaje de apoyo a Matthei
ORDER BY matthei_pct DESC;
