-- =====================================================
-- 4. TOP 10 COMMUNES BY CANDIDATE
-- =====================================================
-- Objective: Identify communes where each candidate achieved their highest vote shares
-- Context: Reveal geographic strongholds and territorial concentration patterns
-- Database: SQL Server 2012+
-- Source table: first_round_2025 (columns: commune, region, jara_pct, kast_pct, parisi_pct, 
--              kaiser_pct, matthei_pct, artes_pct, enriquez_ominami_pct, mayne_nicholls_pct)

-- 4.1 JEANNETTE JARA
SELECT TOP 10
    commune AS comuna,
    region,
    jara_pct AS porcentaje,
    CASE
        WHEN jara_pct >= artes_pct AND jara_pct >= enriquez_ominami_pct AND jara_pct >= kaiser_pct 
             AND jara_pct >= kast_pct AND jara_pct >= matthei_pct AND jara_pct >= mayne_nicholls_pct 
             AND jara_pct >= parisi_pct
        THEN 'Wins in this commune'
        ELSE 'Loses in this commune'
    END AS resultado_comuna
FROM first_round_2025
ORDER BY jara_pct DESC;

-- 4.2 JOSÉ ANTONIO KAST
SELECT TOP 10
    commune AS comuna,
    region,
    kast_pct AS porcentaje,
    CASE
        WHEN kast_pct >= artes_pct AND kast_pct >= enriquez_ominami_pct AND kast_pct >= kaiser_pct 
             AND kast_pct >= jara_pct AND kast_pct >= matthei_pct AND kast_pct >= mayne_nicholls_pct 
             AND kast_pct >= parisi_pct
        THEN 'Wins in this commune'
        ELSE 'Loses in this commune'
    END AS resultado_comuna
FROM first_round_2025
ORDER BY kast_pct DESC;

-- 4.3 FRANCO PARISI
SELECT TOP 10
    commune AS comuna,
    region,
    parisi_pct AS porcentaje,
    CASE
        WHEN parisi_pct >= artes_pct AND parisi_pct >= enriquez_ominami_pct AND parisi_pct >= kaiser_pct 
             AND parisi_pct >= kast_pct AND parisi_pct >= matthei_pct AND parisi_pct >= mayne_nicholls_pct 
             AND parisi_pct >= jara_pct
        THEN 'Wins in this commune'
        ELSE 'Loses in this commune'
    END AS resultado_comuna
FROM first_round_2025
ORDER BY parisi_pct DESC;

-- 4.4 JOHANNES KAISER
SELECT TOP 10
    commune AS comuna,
    region,
    kaiser_pct AS porcentaje,
    CASE
        WHEN kaiser_pct >= artes_pct AND kaiser_pct >= enriquez_ominami_pct AND kaiser_pct >= jara_pct 
             AND kaiser_pct >= kast_pct AND kaiser_pct >= matthei_pct AND kaiser_pct >= mayne_nicholls_pct 
             AND kaiser_pct >= parisi_pct
        THEN 'Wins in this commune'
        ELSE 'Loses in this commune'
    END AS resultado_comuna
FROM first_round_2025
ORDER BY kaiser_pct DESC;

-- 4.5 EVELYN MATTHEI
SELECT TOP 10
    commune AS comuna,
    region,
    matthei_pct AS porcentaje,
    CASE
        WHEN matthei_pct >= artes_pct AND matthei_pct >= enriquez_ominami_pct AND matthei_pct >= kaiser_pct 
             AND matthei_pct >= kast_pct AND matthei_pct >= jara_pct AND matthei_pct >= mayne_nicholls_pct 
             AND matthei_pct >= parisi_pct
        THEN 'Wins in this commune'
        ELSE 'Loses in this commune'
    END AS resultado_comuna
FROM first_round_2025
ORDER BY matthei_pct DESC;
