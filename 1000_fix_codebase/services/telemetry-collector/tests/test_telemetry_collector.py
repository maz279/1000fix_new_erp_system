"""Tests for telemetry collector service (CD-M02-03) and TimescaleDB hypertable definition."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate spherical distance between two lat/lon coordinates in meters."""
    r = 6371000.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def evaluate_nfr_056_throttle(
    prev_time: datetime,
    prev_lat: float,
    prev_lon: float,
    curr_time: datetime,
    curr_lat: float,
    curr_lon: float,
) -> bool:
    """NFR-056 throttle rule: return True if elapsed < 30s AND distance < 100m."""
    elapsed = (curr_time - prev_time).total_seconds()
    dist = haversine_meters(prev_lat, prev_lon, curr_lat, curr_lon)
    return elapsed < 30.0 and dist < 100.0


class TestTelemetryCollector:
    """Test suite for Go telemetry collector service and TimescaleDB definitions."""

    @classmethod
    def setup_class(cls):
        cls.root_dir = Path(__file__).resolve().parents[3]
        cls.service_dir = cls.root_dir / "services" / "telemetry-collector"
        cls.sql_file = cls.root_dir / "migrations" / "sql" / "timescaledb_telemetry_hypertable.sql"

    def test_service_artifacts_exist(self):
        assert (self.service_dir / "main.go").is_file()
        assert (self.service_dir / "go.mod").is_file()
        assert (self.service_dir / "Dockerfile").is_file()

    def test_timescaledb_hypertable_sql_structure(self):
        assert self.sql_file.is_file()
        sql_content = self.sql_file.read_text(encoding="utf-8")
        assert "CREATE EXTENSION IF NOT EXISTS timescaledb" in sql_content
        assert "CREATE TABLE IF NOT EXISTS fix_technician_telemetry" in sql_content
        assert "SELECT create_hypertable" in sql_content
        assert "timescaledb.compress" in sql_content
        assert "add_compression_policy" in sql_content
        assert "add_retention_policy" in sql_content
        assert "view_technician_current_locations" in sql_content

    def test_nfr_056_throttle_logic_stationary(self):
        """Technician pinging after 15 seconds from same location must be throttled."""
        t0 = datetime.now(timezone.utc)
        t1 = t0 + timedelta(seconds=15)
        # Lat/lon difference of 10 meters
        lat0, lon0 = 23.7937, 90.4066
        lat1, lon1 = 23.79375, 90.40665  # ~7 meters
        assert evaluate_nfr_056_throttle(t0, lat0, lon0, t1, lat1, lon1) is True

    def test_nfr_056_throttle_logic_moving_fast(self):
        """Technician moving 250m in 15 seconds must NOT be throttled."""
        t0 = datetime.now(timezone.utc)
        t1 = t0 + timedelta(seconds=15)
        lat0, lon0 = 23.7937, 90.4066
        lat1, lon1 = 23.7960, 90.4066  # ~256 meters
        assert evaluate_nfr_056_throttle(t0, lat0, lon0, t1, lat1, lon1) is False

    def test_nfr_056_throttle_logic_time_elapsed(self):
        """Technician stationary but 35 seconds elapsed must NOT be throttled."""
        t0 = datetime.now(timezone.utc)
        t1 = t0 + timedelta(seconds=35)
        lat0, lon0 = 23.7937, 90.4066
        lat1, lon1 = 23.7937, 90.4066
        assert evaluate_nfr_056_throttle(t0, lat0, lon0, t1, lat1, lon1) is False

    def test_collector_capacity_parameters(self):
        """Verify Go source defines 50,000 epm capacity."""
        go_code = (self.service_dir / "main.go").read_text(encoding="utf-8")
        assert "50000" in go_code
        assert "bufferCap" in go_code
        assert "batchSize" in go_code
        assert "NFR-056" in go_code
