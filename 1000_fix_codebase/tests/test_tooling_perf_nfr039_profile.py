"""GV-009: tooling/performance/run_nfr039_profile.py measures only a LIVE
ClickHouse - an unreachable warehouse is UNMEASURED (no silent SQLite fallback,
no warehouse sync), failing or slow queries are a FAIL, and the status written
to both evidence files is the computed one."""

from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "performance" / "run_nfr039_profile.py"
EVIDENCE_FILES = ("r09-m01-nfr039-performance-evidence.json", "g8-pe004-performance-evidence.json")


def _load():
    spec = importlib.util.spec_from_file_location("run_nfr039_profile_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod(monkeypatch, tmp_path):
    def no_http(*args, **kwargs):
        raise urllib.error.URLError("network disabled in tests")

    monkeypatch.setattr(urllib.request, "urlopen", no_http)
    module = _load()
    monkeypatch.setattr(module, "EVIDENCE_DIR", tmp_path)
    return module


class FakeClickHouse:
    base_url = "http://stub:8123"
    database = "fix_analytics"

    def __init__(self, live=True, fail_queries=False, precheck_error=False):
        self.live = live
        self.fail_queries = fail_queries
        self.precheck_error = precheck_error
        self.statements: list[str] = []

    def is_connected(self):
        return self.live

    def execute(self, sql):
        self.statements.append(sql)
        if "count() AS n" in sql:
            if self.precheck_error:
                raise RuntimeError("Table fix_analytics.fact_service_orders doesn't exist")
            return [{"n": 42}]
        if self.fail_queries:
            raise RuntimeError("Code: 60. Unknown table")
        return [{"row": 1}, {"row": 2}]


def test_unreachable_clickhouse_is_unmeasured_in_both_evidence_files(mod, tmp_path):
    ch = FakeClickHouse(live=False)
    report = mod.run_nfr039_benchmark(concurrency=2, total_queries=5, ch=ch)
    assert report["status"] == "UNMEASURED"
    assert report["sla_met"] is None
    assert "latencies_sec" not in report
    assert ch.statements == []  # nothing executed, no embedded fallback
    for name in EVIDENCE_FILES:
        assert json.loads((tmp_path / name).read_text(encoding="utf-8"))["status"] == "UNMEASURED"


def test_missing_warehouse_tables_are_unmeasured_and_never_synced(mod):
    ch = FakeClickHouse(precheck_error=True)
    report = mod.run_nfr039_benchmark(concurrency=2, total_queries=5, ch=ch, write_evidence=False)
    assert report["status"] == "UNMEASURED"
    assert all(s.lstrip().upper().startswith("SELECT") for s in ch.statements)


def test_failing_queries_are_a_fail(mod):
    report = mod.run_nfr039_benchmark(
        concurrency=2, total_queries=10, ch=FakeClickHouse(fail_queries=True), write_evidence=False
    )
    assert report["error_count"] == 10
    assert report["status"] == "FAIL"


def test_p95_over_budget_is_a_fail(mod, monkeypatch):
    monkeypatch.setattr(mod, "NFR039_P95_BUDGET_SECONDS", -1.0)
    report = mod.run_nfr039_benchmark(
        concurrency=2, total_queries=10, ch=FakeClickHouse(), write_evidence=False
    )
    assert report["sla_met"] is False
    assert report["status"] == "FAIL"


def test_measured_live_run_within_budget_is_pass(mod):
    ch = FakeClickHouse()
    report = mod.run_nfr039_benchmark(concurrency=2, total_queries=10, ch=ch, write_evidence=False)
    assert report["status"] == "PASS"
    assert report["workload_measured"]["total_queries_executed"] == 10
    assert all(s.endswith("FORMAT JSON") for s in ch.statements)


def test_main_exit_code_for_unreachable_default_client(mod, tmp_path):
    assert mod.main() == 2
    assert (
        json.loads((tmp_path / EVIDENCE_FILES[0]).read_text(encoding="utf-8"))["status"]
        == "UNMEASURED"
    )
