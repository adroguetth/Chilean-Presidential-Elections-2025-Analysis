-- =====================================================
-- 4. ELECTORAL STRONGHOLDS: TOP 10 COMMUNES PER CANDIDATE
-- =====================================================
-- Objective: Identify the 10 communes where each of the 5 leading candidates
--            achieved their highest vote share, and determine whether they
--            actually won those communes.

-- Strategic context: This analysis surfaces each candidate's electoral strongholds,
--                   exposing zones of maximum influence and the geographic
--                   distribution of their political support nationwide.

-- Method: Parallel queries per candidate + per-commune victory determination
--         + ranking by vote percentage descending.

-- POLITICAL PROFILES OF ANALYZED CANDIDATES:
-- 1. Jeannette Jara:      Ruling-coalition left (Boric / Unidad por Chile)
-- 2. José Antonio Kast:   Conservative right (Partido Republicano)
-- 3. Franco Parisi:       Third-way outsider (Partido de la Gente)
-- 4. Johannes Kaiser:     Libertarian right (Partido Nacional Libertario)
-- 5. Evelyn Matthei:      Establishment right / Piñerismo (Chile Vamos)

-- =====================================================
-- 4.1 JEANNETTE JARA - RULING-COALITION LEFT (UNIDAD POR CHILE)
-- =====================================================
-- Analysis: Jara leads in working-class communes of Greater Santiago and Valparaíso
-- Electoral profile: Dense urban areas, public housing districts, labour sectors
SELECT TOP 10
    comuna,                     -- Commune name
    region,                     -- Administrative region
    jara_pct AS porcentaje,     -- Jara's vote share in this commune

    -- LOCAL VICTORY DETERMINATION:
    -- Compares Jara's percentage against every other candidate
    -- Returns win if Jara holds the highest share in the commune
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
    END AS ganador_comuna  -- Electoral outcome in this territory

FROM resultados_elecciones
-- ORDER: Communes with highest Jara support share (descending)
-- Purpose: Surface the candidate's most solid strongholds
ORDER BY jara_pct DESC;

-- =====================================================
-- 4.2 JOSÉ ANTONIO KAST - CONSERVATIVE RIGHT (PARTIDO REPUBLICANO)
-- =====================================================
-- Analysis: Kast leads in rural communes of Maule, La Araucanía, and the far south
-- Electoral profile: Rural, traditionalist areas with strong local identity
SELECT TOP 10
    comuna,
    region,
    kast_pct AS porcentaje,     -- Kast's vote share in this commune

    -- LOCAL VICTORY DETERMINATION:
    -- Compares Kast's percentage against every other candidate
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
-- ORDER: Communes with highest Kast support share (descending)
ORDER BY kast_pct DESC;

-- =====================================================
-- 4.3 FRANCO PARISI - THIRD-WAY OUTSIDER (PARTIDO DE LA GENTE)
-- =====================================================
-- Analysis: Parisi dominates in the far north (Tarapacá, Antofagasta)
-- Electoral profile: Mining regions, anti-establishment voters, outsider appeal
SELECT TOP 10
    comuna,
    region,
    parisi_pct AS porcentaje,   -- Parisi's vote share in this commune

    -- LOCAL VICTORY DETERMINATION:
    -- Compares Parisi's percentage against every other candidate
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
-- ORDER: Communes with highest Parisi support share (descending)
ORDER BY parisi_pct DESC;

-- =====================================================
-- 4.4 JOHANNES KAISER - LIBERTARIAN RIGHT (PARTIDO NACIONAL LIBERTARIO)
-- =====================================================
-- Analysis: Kaiser shows strength in Patagonia but competes with Kast in several communes
-- Electoral profile: Remote areas, young professionals, anti-statist voters
SELECT TOP 10
    comuna,
    region,
    kaiser_pct AS porcentaje,   -- Kaiser's vote share in this commune

    -- LOCAL VICTORY DETERMINATION:
    -- Compares Kaiser's percentage against every other candidate
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
-- ORDER: Communes with highest Kaiser support share (descending)
ORDER BY kaiser_pct DESC;

-- =====================================================
-- 4.5 EVELYN MATTHEI - ESTABLISHMENT RIGHT (CHILE VAMOS)
-- =====================================================
-- Analysis: Matthei leads in high-income communes but loses some to Kast
-- Electoral profile: Affluent urban sectors, traditional right-wing voters
SELECT TOP 10
    comuna,
    region,
    matthei_pct AS porcentaje,  -- Matthei's vote share in this commune

    -- LOCAL VICTORY DETERMINATION:
    -- Compares Matthei's percentage against every other candidate
    -- Note: Direct competition with Kast for the right-wing electorate
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
-- ORDER: Communes with highest Matthei support share (descending)
ORDER BY matthei_pct DESC;
