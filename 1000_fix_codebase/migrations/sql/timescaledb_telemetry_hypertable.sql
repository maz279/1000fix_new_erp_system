-- ============================================================================
-- 1000FiX ERP v2.0 - Milestone R03-M03: Geospatial & Telemetry Storage Engine
-- TimescaleDB Hypertable & Compression Policy for Technician Telemetry
-- Architecture Reference: ARCH-040, NFR-056 (30s / 100m throttle), PDPA Tier-1
-- ============================================================================

-- Ensure TimescaleDB extension is active
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

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

-- 4. TimescaleDB Columnar Compression (7-day policy for archival performance)
-- Compress by technician_id segment, ordered by time DESC
ALTER TABLE fix_technician_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'technician_id,operating_unit_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- Apply automatic compression policy after 7 days
SELECT add_compression_policy(
    'fix_technician_telemetry',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- 5. Data Retention Policy (90-day retention according to PDPA Tier-1 telemetry lifecycle)
SELECT add_retention_policy(
    'fix_technician_telemetry',
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- 6. Helper analytical view for latest technician locations
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
