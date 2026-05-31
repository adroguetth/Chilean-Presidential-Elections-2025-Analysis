## 🚀 Quick Start

### 1. Create the database and table

```sql
CREATE DATABASE EleccionesChile2025;
GO

USE EleccionesChile2025;
GO

CREATE TABLE first_round_2025 (
    commune NVARCHAR(100),
    region NVARCHAR(100),
    artes_votes INT,
    artes_pct DECIMAL(5,2),
    enriquez_ominami_votes INT,
    enriquez_ominami_pct DECIMAL(5,2),
    jara_votes INT,
    jara_pct DECIMAL(5,2),
    kaiser_votes INT,
    kaiser_pct DECIMAL(5,2),
    kast_votes INT,
    kast_pct DECIMAL(5,2),
    matthei_votes INT,
    matthei_pct DECIMAL(5,2),
    mayne_nicholls_votes INT,
    mayne_nicholls_pct DECIMAL(5,2),
    parisi_votes INT,
    parisi_pct DECIMAL(5,2),
    blank_votes INT,
    blank_pct DECIMAL(5,2),
    casted_votes INT,
    casted_pct DECIMAL(5,2),
    null_votes INT,
    null_pct DECIMAL(5,2)
);
GO
