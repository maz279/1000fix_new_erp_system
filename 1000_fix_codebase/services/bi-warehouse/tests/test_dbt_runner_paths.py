"""test_dbt_runner_paths.py - freshness gating, build failures and the CLI entry point.

dbt project files are written under ``tmp_path``; no dbt binary or subprocess is
involved (the runner compiles/validates the SQL itself and counts rows through the
ClickHouse client, which runs on the per-test embedded file).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import ClassVar

import dbt_runner
import pytest
import yaml
from clickhouse_client import ClickHouseClient
from dbt_runner import DbtWarehouseRunner
from warehouse_sync import WarehouseSyncEngine


@pytest.fixture
def ch():
    client = ClickHouseClient(database="fix_analytics")
    yield client
    client.close()


def _write_project(root: Path, sources: list[dict], models: dict[str, str | None]) -> None:
    """Writes sources.yml, dbt_project.yml and the core model SQL (None = missing)."""
    core = root / "models" / "core"
    core.mkdir(parents=True)
    (root / "models" / "sources.yml").write_text(
        yaml.safe_dump({"version": 2, "sources": sources}), encoding="utf-8"
    )
    (root / "dbt_project.yml").write_text(
        yaml.safe_dump({"models": [{"name": name} for name in models]}), encoding="utf-8"
    )
    for name, sql in models.items():
        if sql is not None:
            (core / f"{name}.sql").write_text(sql, encoding="utf-8")


def _runner_on(root: Path, ch: ClickHouseClient) -> DbtWarehouseRunner:
    runner = DbtWarehouseRunner(ch_client=ch)
    runner.dbt_dir = root
    runner.models_dir = root / "models" / "core"
    return runner


def test_default_runner_targets_repo_dbt_project():
    runner = DbtWarehouseRunner()
    assert runner.ch.database == "fix_analytics"
    assert runner.dbt_dir == dbt_runner.REPO_ROOT / "services" / "bi-warehouse" / "dbt"
    assert runner.models_dir == runner.dbt_dir / "models" / "core"


def test_freshness_classifies_pass_warn_and_error(tmp_path, ch, monkeypatch):
    """Ages come from the replica's max(write_date) (faked here): 0.5 h real
    ages classify against each source's warn/error thresholds."""
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    ages = {
        "t_pass": timedelta(minutes=30),
        "t_warn": timedelta(minutes=30),
        "t_error": timedelta(minutes=30),
    }
    sources = [
        {"name": "healthy", "tables": [{"name": "t_pass"}]},  # default 24 h / 48 h
        {
            "name": "stale",
            "freshness": {"warn_after": {"count": 0}, "error_after": {"count": 48}},
            "tables": [{"name": "t_warn"}],
        },
        {
            "name": "dead",
            "freshness": {"warn_after": {"count": 0}, "error_after": {"count": 0}},
            "tables": [{"name": "t_error"}],
        },
        {"name": "empty_source"},
    ]
    _write_project(tmp_path, sources, {})
    runner = _runner_on(tmp_path, ch)
    monkeypatch.setattr(runner, "_fetch_max_write_date", lambda table: now - ages[table])

    res = runner.run_source_freshness()

    assert res["status"] == "FAIL"
    by_table = {s["table"]: s for s in res["sources"]}
    assert {t: s["status"] for t, s in by_table.items()} == {
        "t_pass": "PASS",
        "t_warn": "WARN",
        "t_error": "ERROR",
    }
    assert by_table["t_pass"]["warn_threshold_hours"] == 24
    assert by_table["t_pass"]["error_threshold_hours"] == 48
    assert by_table["t_warn"]["age_hours"] == 0.5


def test_freshness_is_never_simulated_when_replica_unreadable(tmp_path, ch):
    """No readable replica (conftest disables psycopg2): every declared table is
    ERROR with the real reason and NO age - the old code invented a 30-minute-
    old write_date for every table and passed."""
    _write_project(
        tmp_path,
        [{"name": "oltp_replica", "tables": [{"name": "fix_service_order"}]}],
        {},
    )

    res = _runner_on(tmp_path, ch).run_source_freshness()

    assert res["status"] == "FAIL"
    (entry,) = res["sources"]
    assert entry["status"] == "ERROR"
    assert entry["age_hours"] is None
    assert entry["max_loaded_at"] is None
    assert "write_date not readable" in entry["error"]


def test_freshness_reports_null_write_date_as_error(tmp_path, ch, monkeypatch):
    _write_project(tmp_path, [{"name": "oltp_replica", "tables": [{"name": "empty_table"}]}], {})
    runner = _runner_on(tmp_path, ch)
    monkeypatch.setattr(runner, "_fetch_max_write_date", lambda table: None)

    res = runner.run_source_freshness()

    (entry,) = res["sources"]
    assert entry["status"] == "ERROR"
    assert "holds no rows" in entry["error"]


def test_build_reports_missing_mutating_and_uncountable_models(tmp_path, ch, caplog):
    _write_project(
        tmp_path,
        [],
        {
            "ok_model": "select 1 as a from {{ source('oltp_replica', 'x') }}",
            "missing_model": None,
            "mutating_model": "DELETE FROM oltp_table WHERE 1 = 1",
            "unbuilt_model": "select 2 as a",
        },
    )
    ch.insert_rows("fix_analytics.ok_model", [{"a": 1}, {"a": 2}])

    res = _runner_on(tmp_path, ch).compile_and_build_models()

    assert res["status"] == "FAIL"
    assert res["built_models_count"] == 4
    models = {m["model"]: m for m in res["models"]}
    assert models["ok_model"]["status"] == "SUCCESS"
    assert models["ok_model"]["rows_affected"] == 2
    assert models["ok_model"]["error"] is None
    assert models["missing_model"] == {
        "model": "missing_model",
        "status": "FAIL",
        "error": "file_not_found",
    }
    assert models["mutating_model"] == {
        "model": "mutating_model",
        "status": "FAIL",
        "error": "LB-06 violation: mutating keyword found",
    }
    # A failed count is UNVERIFIED with the real error - never a made-up row count.
    assert models["unbuilt_model"]["status"] == "UNVERIFIED"
    assert models["unbuilt_model"]["rows_affected"] is None
    assert "no such table: unbuilt_model" in models["unbuilt_model"]["error"]
    assert "Missing SQL file for declared model: missing_model" in caplog.text


def test_build_succeeds_when_every_model_counts(tmp_path, ch):
    _write_project(tmp_path, [], {"dim_a": "select 1", "dim_b": "select 2"})
    ch.insert_rows("dim_a", [{"k": 1}])
    ch.insert_rows("dim_b", [{"k": 1}, {"k": 2}, {"k": 3}])

    res = _runner_on(tmp_path, ch).compile_and_build_models()

    assert res["status"] == "SUCCESS"
    assert [(m["model"], m["rows_affected"]) for m in res["models"]] == [
        ("dim_a", 1),
        ("dim_b", 3),
    ]


DECLARED_SCHEMA_TESTS = [
    "unique_dim_date_date_key",
    "not_null_dim_date_date_key",
    "unique_dim_branch_branch_key",
    "not_null_dim_branch_branch_key",
    "unique_dim_customer_customer_key",
    "not_null_dim_customer_customer_key",
    "unique_dim_device_device_key",
    "not_null_dim_device_device_key",
    "unique_fact_service_orders_order_key",
    "not_null_fact_service_orders_order_key",
    "accepted_values_fact_service_orders_order_category",
    "unique_fact_invoices_invoice_key",
    "not_null_fact_invoices_invoice_key",
    "unique_fact_warranty_claims_claim_key",
    "not_null_fact_warranty_claims_claim_key",
]


def _write_schema_project(root: Path, models: list[dict]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "dbt_project.yml").write_text(yaml.safe_dump({"models": models}), encoding="utf-8")


def test_schema_tests_run_every_declared_test_against_synced_warehouse(ch):
    WarehouseSyncEngine(ch_client=ch).run_full_sync()

    res = DbtWarehouseRunner(ch_client=ch).run_schema_tests()

    assert [t["test_name"] for t in res["tests"]] == DECLARED_SCHEMA_TESTS
    assert (res["status"], res["passed_tests"], res["failed_tests"], res["errored_tests"]) == (
        "PASS",
        15,
        0,
        0,
    )
    assert all(t["failing_rows"] == 0 and t["error"] is None for t in res["tests"])


def test_regression_schema_tests_fail_on_bad_data_and_error_on_missing_tables(tmp_path, ch):
    """Regression: run_schema_tests returned a hard-coded PASS for every test.

    Duplicate keys, NULL keys and values outside accepted_values must FAIL with the
    number of offending rows; a test whose model table does not exist must not PASS.
    """
    _write_schema_project(
        tmp_path,
        [
            {
                "name": "dim_x",
                "columns": [
                    {"name": "x_key", "tests": ["unique", "not_null"]},
                    {"name": "kind", "tests": [{"accepted_values": {"values": ["a", "b'c"]}}]},
                ],
            },
            {"name": "dim_clean", "columns": [{"name": "k", "tests": ["unique", "not_null"]}]},
            {"name": "dim_never_built", "columns": [{"name": "k", "tests": ["unique"]}]},
            {"name": "dim_no_tests"},
        ],
    )
    ch.insert_rows(
        "dim_x",
        [
            {"x_key": 1, "kind": "a"},
            {"x_key": 1, "kind": "b'c"},
            {"x_key": 1, "kind": "zzz"},
            {"x_key": 2, "kind": "a"},
            {"x_key": 2, "kind": None},
            {"x_key": None, "kind": "other"},
        ],
    )
    ch.insert_rows("dim_clean", [{"k": 1}, {"k": 2}])

    res = _runner_on(tmp_path, ch).run_schema_tests()

    by_name = {t["test_name"]: t for t in res["tests"]}
    assert {n: (t["status"], t["failing_rows"]) for n, t in by_name.items()} == {
        "unique_dim_x_x_key": ("FAIL", 5),  # 3 rows share key 1, 2 share key 2
        "not_null_dim_x_x_key": ("FAIL", 1),
        "accepted_values_dim_x_kind": ("FAIL", 2),  # 'zzz', 'other' (NULL is not tested)
        "unique_dim_clean_k": ("PASS", 0),
        "not_null_dim_clean_k": ("PASS", 0),
        "unique_dim_never_built_k": ("ERROR", None),
    }
    assert "no such table: dim_never_built" in by_name["unique_dim_never_built_k"]["error"]
    assert (res["status"], res["passed_tests"], res["failed_tests"], res["errored_tests"]) == (
        "FAIL",
        2,
        3,
        1,
    )


def test_schema_tests_error_on_unsupported_type_bad_identifier_and_no_result(
    tmp_path, ch, monkeypatch
):
    _write_schema_project(
        tmp_path,
        [
            {
                "name": "dim_y",
                "columns": [
                    {"name": "k", "tests": [{"relationships": {"to": "ref('dim_z')"}}]},
                    {"name": "k; DROP TABLE dim_y", "tests": ["not_null"]},
                    {"name": "k", "tests": ["not_null"]},
                ],
            }
        ],
    )
    ch.insert_rows("dim_y", [{"k": 1}])
    runner = _runner_on(tmp_path, ch)
    real_execute = ch.execute
    # A live ClickHouse reply that is not parsed into rows (execute() returns 1).
    monkeypatch.setattr(ch, "execute", lambda sql: 1 if "IS NULL" in sql else real_execute(sql))

    res = runner.run_schema_tests()

    assert [(t["status"], t["error"]) for t in res["tests"]] == [
        ("ERROR", "unsupported schema test type: relationships"),
        ("ERROR", "invalid identifier in schema test: dim_y.k; DROP TABLE dim_y"),
        ("ERROR", "schema test query returned no result rows: 1"),
    ]
    assert res["status"] == "FAIL"
    assert real_execute("SELECT count(*) AS n FROM dim_y") == [{"n": 1}]  # nothing dropped


def test_schema_tests_with_nothing_declared_do_not_pass(tmp_path, ch):
    _write_schema_project(tmp_path, [{"name": "dim_untested", "columns": [{"name": "k"}]}])

    res = _runner_on(tmp_path, ch).run_schema_tests()

    assert res == {
        "status": "FAIL",
        "passed_tests": 0,
        "failed_tests": 0,
        "errored_tests": 0,
        "tests": [],
    }


class _RecordingSync:
    instances: ClassVar[list[_RecordingSync]] = []

    def __init__(self, ch_client: ClickHouseClient, pg_dsn: str | None = None) -> None:
        self.ch_client = ch_client
        self.pg_dsn = pg_dsn
        self.synced = False
        _RecordingSync.instances.append(self)

    def run_full_sync(self) -> dict:
        self.synced = True
        return {"status": "PASS"}


@pytest.fixture
def recording_sync(monkeypatch):
    _RecordingSync.instances = []
    monkeypatch.setattr(dbt_runner, "WarehouseSyncEngine", _RecordingSync)
    return _RecordingSync


def _freshness_pass(runner: DbtWarehouseRunner, monkeypatch) -> None:
    """Fakes a healthy replica so a test can target the build/test stages.

    The freshness path itself is covered by its own (real) tests above.
    """
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    monkeypatch.setattr(runner, "_fetch_max_write_date", lambda table: now - timedelta(minutes=30))


def test_scheduled_run_gates_build_on_failed_freshness(
    monkeypatch, ch, recording_sync, isolated_warehouse, caplog
):
    runner = DbtWarehouseRunner(ch_client=ch)
    stale = {
        "status": "FAIL",
        "evaluated_at": "t",
        "sources": [{"table": "t", "status": "ERROR", "error": "unread"}],
    }
    monkeypatch.setattr(runner, "run_source_freshness", lambda: stale)

    def must_not_build() -> dict:
        raise AssertionError("dbt build must be gated by failed freshness")

    monkeypatch.setattr(runner, "compile_and_build_models", must_not_build)

    ev = runner.execute_scheduled_dbt_run()

    assert ev["status"] == "FAIL"
    assert ev["reason"] == "source_freshness_failed"
    assert ev["freshness"] is stale
    assert ev["build"] is None and ev["tests"] is None
    assert [s.ch_client for s in recording_sync.instances] == [ch]
    assert recording_sync.instances[0].synced is True
    assert "Source freshness failed! Gating dbt build." in caplog.text
    # A gated run overwrites the evidence - a stale SUCCESS must not survive.
    evidence = isolated_warehouse.evidence_dir / "r09-m01-dbt-build-evidence.json"
    assert json.loads(evidence.read_text(encoding="utf-8")) == ev


def test_scheduled_run_fails_and_records_evidence_when_build_fails(
    monkeypatch, ch, recording_sync, isolated_warehouse
):
    runner = DbtWarehouseRunner(ch_client=ch)
    _freshness_pass(runner, monkeypatch)
    monkeypatch.setattr(
        runner, "compile_and_build_models", lambda: {"status": "FAIL", "models": []}
    )

    ev = runner.execute_scheduled_dbt_run()

    assert ev["status"] == "FAIL"
    assert ev["freshness"]["status"] == "PASS"
    # The sync is real here (no replica rows), so no model table exists beyond
    # the schema init: every schema test runs against the empty tables.
    assert (ev["tests"]["status"], ev["tests"]["errored_tests"]) == ("FAIL", 15)
    evidence = isolated_warehouse.evidence_dir / "r09-m01-dbt-build-evidence.json"
    assert json.loads(evidence.read_text(encoding="utf-8")) == ev


def test_scheduled_run_success_writes_evidence(ch, isolated_warehouse, monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="dbt_runner")
    runner = DbtWarehouseRunner(ch_client=ch)
    _freshness_pass(runner, monkeypatch)

    ev = runner.execute_scheduled_dbt_run()

    assert ev["status"] == "SUCCESS"
    assert all(m["status"] == "SUCCESS" for m in ev["build"]["models"])
    # The warehouse is honestly empty (no replica rows were extracted): the
    # build counts 0 rows per model instead of the former 730 padded dates.
    assert {m["model"]: m["rows_affected"] for m in ev["build"]["models"]}["dim_date"] == 0
    assert (ev["tests"]["status"], ev["tests"]["passed_tests"]) == ("PASS", 15)
    assert ev["warehouse_mode"] == "sqlite-fallback"
    assert ev["sync"]["total_source_rows"] == 0
    assert ev["lb06_read_only_downstream_verified"] is False
    evidence = isolated_warehouse.evidence_dir / "r09-m01-dbt-build-evidence.json"
    assert json.loads(evidence.read_text(encoding="utf-8")) == ev
    assert "Status=SUCCESS" in caplog.text


@pytest.mark.parametrize(("status", "exit_code"), [("SUCCESS", 0), ("FAIL", 1), (None, 1)])
def test_main_exit_code_follows_scheduled_run(monkeypatch, status, exit_code):
    seen: list[DbtWarehouseRunner] = []

    def fake_run(self: DbtWarehouseRunner) -> dict:
        seen.append(self)
        return {} if status is None else {"status": status}

    monkeypatch.setattr(DbtWarehouseRunner, "execute_scheduled_dbt_run", fake_run)

    assert dbt_runner.main() == exit_code
    assert len(seen) == 1
    assert seen[0].ch.database == "fix_analytics"
