-- ============================================================================
-- 1000FiX ERP v2.0 - Milestone R03-M03: Geospatial & Telemetry Storage Engine
-- TimescaleDB hypertable for technician telemetry - APACHE-2.0 FEATURES ONLY
-- Architecture Reference: ARCH-040, NFR-056 (30s / 100m throttle), PDPA Tier-1
--
-- Licence (D-030; tooling/licence/register.yaml: timescaledb is approved WITH
-- CONDITION "Apache-2.0-licensed features ONLY; TSL features must never be
-- enabled"). This file uses only Apache-2.0 TimescaleDB features:
-- create_hypertable and drop_chunks. Native columnar compression and its
-- policy, the automated retention policy, continuous aggregates and the
-- background job scheduler are TSL-licensed and are deliberately NOT used.
--
-- Prerequisites (server configuration, not this file):
--   * PostgreSQL with the TimescaleDB extension available, and in postgresql.conf
--       shared_preload_libraries = 'timescaledb'
--       timescaledb.license      = 'apache'
--   The guard below refuses to run on a server whose TimescaleDB licence is not
--   'apache': a TSL-enabled server would let TSL features in silently.
--
-- Retention (PDPA Tier-1 telemetry lifecycle, 90 days): the function
-- fix_telemetry_apply_retention() drops whole chunks older than 90 days with
-- drop_chunks (Apache-2.0). TimescaleDB's own scheduler cannot run it (that
-- scheduler is TSL), so the platform scheduler must call it once a day, e.g.
-- a daily cron entry / Airflow task on the database host running:
--     SELECT fix_telemetry_apply_retention();
-- ============================================================================

-- Ensure TimescaleDB extension is active
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- D-030 guard: refuse a server whose TimescaleDB licence is not Apache-only
DO $$
BEGIN
    IF coalesce(current_setting('timescaledb.license', true), '') <> 'apache' THEN
        RAISE EXCEPTION
            'D-030: timescaledb.license must be ''apache'' (found %) - TSL features must never be enabled',
            coalesce(current_setting('timescaledb.license', true), 'unset');
    END IF;
END
$$;

-- 1. Base telemetry hypertable schema
CREATE TABLE IF NOT EXISTS fix_technician_telemetry (
    time TIMESTAMPTZ NOT NULL,
    technician_id INTEGER NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy_meters REAL DEFAULT 0.0,
    speed_mps REAL DEFAULT 0.0,
    bearing_deg REAL DEFAULT 0.0,
    battery_level REAL DEFAULT 100.0,
    is_charging BOOLEAN DEFAULT FALSE,
    connectivity_state VARCHAR(32) DEFAULT 'online', -- 'online', 'degraded', 'offline_buffered'
    is_throttled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    operating_unit_id INTEGER,
    company_id INTEGER DEFAULT 1
);

-- 2. Convert to TimescaleDB hypertable partitioned by time (1-day chunk interval)
SELECT create_hypertable(
    'fix_technician_telemetry',
    'time',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- 3. Composite performance indexes for point queries and spatial-temporal range queries
CREATE INDEX IF NOT EXISTS idx_telemetry_tech_time
    ON fix_technician_telemetry (technician_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_telemetry_spatial_grid
    ON fix_technician_telemetry (latitude, longitude, time DESC);

CREATE INDEX IF NOT EXISTS idx_telemetry_ou_time
    ON fix_technician_telemetry (operating_unit_id, time DESC);

-- 4. Data retention (90 days, PDPA Tier-1) - Apache-2.0 drop_chunks, called
--    daily by the platform scheduler (see header). Returns the chunks dropped.
CREATE OR REPLACE FUNCTION fix_telemetry_apply_retention(
    retain INTERVAL DEFAULT INTERVAL '90 days'
) RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    dropped INTEGER;
BEGIN
    SELECT count(*) INTO dropped
    FROM drop_chunks('fix_technician_telemetry', older_than => retain);
    RETURN dropped;
END
$$;

-- 5. Helper analytical view for latest technician locations
CREATE OR REPLACE VIEW view_technician_current_locations AS
SELECT DISTINCT ON (technician_id)
    technician_id,
    time AS last_ping_time,
    latitude,
    longitude,
    accuracy_meters,
    speed_mps,
    battery_level,
    connectivity_state,
    operating_unit_id
FROM fix_technician_telemetry
WHERE time > NOW() - INTERVAL '24 hours'
ORDER BY technician_id, time DESC;
