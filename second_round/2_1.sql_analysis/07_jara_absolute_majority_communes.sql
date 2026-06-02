-- =====================================================
-- 7. COMMUNES WHERE JARA ACHIEVED ABSOLUTE MAJORITY (>50%)
-- =====================================================
-- Objective: Identify communes where Jara exceeded 50% of valid votes
-- Context: Absolute majority indicates stronghold territory
-- Database: SQL Server 2012+
-- Source table: second_round_2025

SELECT
    commune AS comuna,
    region,
    jara_pct AS percentage,
    CASE
        WHEN jara_pct >= kast_pct
        THEN 'Wins in this commune'
        ELSE 'Loses in this commune'
    END AS commune_result
FROM second_round_2025
WHERE jara_pct > 50
ORDER BY jara_pct DESC;

-- =====================================================
-- EXPECTED OUTPUT INTERPRETATION:
-- =====================================================
-- | Comuna | Region | Percentage |
-- |--------|--------|------------|
-- | Juan Fernandez | Valparaíso | 59.29% |
-- | Pedro Aguirre Cerda | Metropolitana | 58.75% |
-- | Lo Espejo | Metropolitana | 56.17% |
-- | San Joaquin | Metropolitana | 55.60% |
-- | Andacollo | Coquimbo | 55.29% |
-- | Isla de Pascua | Valparaíso | 54.47% |
-- | San Antonio | Valparaíso | 53.85% |
-- | Puente Alto | Metropolitana | 53.75% |
-- | La Granja | Metropolitana | 53.50% |
-- | Chañaral | Atacama | 53.43% |
-- [36 comunas total]
--
-- Geographic pattern:
-- =====================================================
-- Jara's absolute majority communes are exclusively in 5 regions:
-- 1. Metropolitana (21) - The urban heartland
-- 2. Valparaíso (5) - Port cities and special territories
-- 3. Atacama (4) - Northern mining region
-- 4. Coquimbo (3) - Norte Chico
-- 5. Antofagasta (3) - Northern mining
--
-- Notable observations:
-- =====================================================
-- - Juan Fernandez (59.29%) is Jara's strongest commune nationally
-- - Isla de Pascua (Easter Island) also voted for Jara with 54.47%
-- - Pedro Aguirre Cerda (58.75%) is her strongest in Metropolitana
-- - Despite winning 36 communes, only these 36 exceed 50% (no other commune gave her majority)
-- - Even in her winning communes, the margin is often narrow (many below 55%)
--
-- Political significance:
-- =====================================================
-- Jara's support is geographically concentrated in working-class 
-- municipalities of Greater Santiago (Pedro Aguirre Cerda, Lo Espejo, 
-- San Joaquin, La Granja, Renca, Lo Prado, Conchalí, Cerro Navia, Pudahuel)
-- plus isolated pockets in mining regions and port cities.
--
-- The complete absence of Jara majority communes in: Biobío, Los Lagos, 
-- La Araucanía, Maule, Ñuble, Los Ríos, Magallanes, Aysén, Tarapacá, 
-- Arica, Libertador is striking.
-- =====================================================
