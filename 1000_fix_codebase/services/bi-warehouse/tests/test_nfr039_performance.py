#!/usr/bin/env python3
"""test_nfr039_performance.py — Unit tests for NFR-039 performance profiling harness.

Milestone R09-M01-T03:
Verifies analytical query execution, latency measurements, and SLA validation.

GV-009 contract of the harness: latencies are measured against a LIVE ClickHouse
only. Without one the run is UNMEASURED (the embedded SQLite fallback is not a
measurement of the warehouse), and the tool never writes to the warehouse. The
live engine is replaced here by a scripted double - no network.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PERF_DIR = REPO_ROOT / "tooling" / "performance"
SRC_DIR = REPO_ROOT / "services" / "bi-warehouse" / "src"

sys.path.insert(0, str(PERF_DIR))
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(REPO_ROOT))

from run_nfr039_profile import (
    ANALYTICAL_BENCHMARK_QUERIES,
    FAILED,
    NFR039_P95_BUDGET_SECONDS,
    PASSED,
    UNMEASURED,
    run_nfr039_benchmark,
)


class LiveWarehouseDouble:
    """Stands in for a reachable ClickHouse: read-only, returns FORMAT JSON rows."""

    base_url = "http://clickhouse.test:8123"
    database = "fix_analytics"

    def __init__(self, connected=True, precheck=None, failing_query=None):
        self.connected = connected
        self.precheck = [{"n": 1200}] if precheck is None else precheck
        self.failing_query = failing_query
        self.statements: list[str] = []

    def is_connected(self) -> bool:
        return self.connected

    def execute(self, sql: str):
        self.statements.append(sql)
        if "count() AS n FROM fact_service_orders" in sql:
            if isinstance(self.precheck, Exception):
                raise self.precheck
            return self.precheck
        if self.failing_query and self.failing_query in sql:
            raise RuntimeError("Code: 60. Table fix_analytics.fact_nps does not exist")
        return [{"row": 1}, {"row": 2}]


def test_unreachable_clickhouse_is_unmeasured_never_a_sqlite_pass():
    """No live server (network disabled by conftest): no latency figure is reported."""
    report = run_nfr039_benchmark(concurrency=8, total_queries=40, write_evidence=False)
    assert report["status"] == UNMEASURED
    assert report["sla_met"] is None
    assert "not reachable" in report["reason"]
    assert "latencies_sec" not in report


def test_live_warehouse_within_budget_passes():
    live = LiveWarehouseDouble()
    report = run_nfr039_benchmark(concurrency=8, total_queries=40, ch=live, write_evidence=False)

    assert report["status"] == PASSED
    assert report["sla_met"] is True
    assert report["latencies_sec"]["p95"] <= NFR039_P95_BUDGET_SECONDS
    assert report["error_rate_pct"] == 0.0
    assert report["workload_measured"]["total_queries_executed"] == 40
    assert report["engine"]["fact_service_orders_rows"] == 1200
    assert set(report["query_breakdown"]) == {name for name, _ in ANALYTICAL_BENCHMARK_QUERIES}
    assert all(
        q["executions"] == 8 and q["rows_last"] == 2 for q in report["query_breakdown"].values()
    )
    # Read-only: precheck + 40 SELECTs, every one FORMAT JSON, nothing else issued.
    assert len(live.statements) == 41
    assert all(s.lstrip().upper().startswith("SELECT") for s in live.statements)
    assert all(s.endswith(" FORMAT JSON") for s in live.statements)


def test_query_errors_fail_the_sla():
    live = LiveWarehouseDouble(failing_query="FROM fact_nps")
    report = run_nfr039_benchmark(concurrency=4, total_queries=10, ch=live, write_evidence=False)

    assert report["status"] == FAILED
    assert report["sla_met"] is False
    assert report["error_count"] == 2
    assert report["error_rate_pct"] == 20.0
    assert report["query_breakdown"]["Q4_NPS_SENTIMENT_DISTRIBUTION"]["errors"] == 2
    assert report["query_breakdown"]["Q4_NPS_SENTIMENT_DISTRIBUTION"]["rows_last"] is None
    assert "does not exist" in report["error_samples"][0]


@pytest.mark.parametrize(
    ("precheck", "reason"),
    [
        (RuntimeError("Table fact_service_orders does not exist"), "precheck failed"),
        (1, "returned no rows"),
    ],
)
def test_unpopulated_warehouse_is_unmeasured_and_not_synced(precheck, reason):
    live = LiveWarehouseDouble(precheck=precheck)
    report = run_nfr039_benchmark(concurrency=2, total_queries=5, ch=live, write_evidence=False)
    assert report["status"] == UNMEASURED
    assert reason in report["reason"]
    assert len(live.statements) == 1  # only the read-only precheck, no sync / no benchmark


def test_evidence_is_written_for_every_outcome(isolated_warehouse):
    report = run_nfr039_benchmark(
        concurrency=2, total_queries=5, ch=LiveWarehouseDouble(connected=False)
    )
    written = sorted(p.name for p in isolated_warehouse.evidence_dir.iterdir())
    assert written == [
        "g8-pe004-performance-evidence.json",
        "r09-m01-nfr039-performance-evidence.json",
    ]
    assert report["status"] == UNMEASURED
