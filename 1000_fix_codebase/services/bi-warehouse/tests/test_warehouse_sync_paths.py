"""test_warehouse_sync_paths.py - replica extract, honest 0-row reporting, load and audit.

The PostgreSQL read replica is never contacted: a fake ``psycopg2`` (and
``psycopg2.extras``) module is placed in ``sys.modules``. ClickHouse runs on the
per-test embedded file from ``conftest.isolated_warehouse``.

GV-009: the sync never invents conformed rows. Tables the replica does not
feed stay empty and are reported as 0 - these tests pin that contract.
"""

from __future__ import annotations

import json
import logging
import sys
import types

import pytest
import warehouse_sync
from clickhouse_client import ClickHouseClient
from warehouse_sync import WarehouseSyncEngine

TABLES = [
    "dim_date",
    "dim_branch",
    "dim_customer",
    "dim_device",
    "dim_technician",
    "fact_service_orders",
    "fact_invoices",
    "fact_warranty_claims",
    "fact_conversations",
    "fact_nps",
]


class RealDictCursor:
    """Sentinel standing in for psycopg2.extras.RealDictCursor."""


class FakeCursor:
    def __init__(self, replica: FakeReplica) -> None:
        self.replica = replica
        self._last_sql = ""

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False

    def execute(self, sql: str) -> None:
        self.replica.executed.append(sql)
        self._last_sql = sql

    def fetchall(self) -> list[dict]:
        # dim_branch now reads fix_branch (res_branch never existed - R01 fix),
        # joined to fix_entity/res_country, so match on any FROM-mention.
        for table, rows in self.replica.tables.items():
            if table == "res_branch" and "FROM fix_branch" in self._last_sql:
                return rows
            if f"FROM {table}" in self._last_sql:
                return rows
        raise AssertionError(f"unexpected query: {self._last_sql}")

    def fetchone(self) -> dict:
        assert "information_schema.tables" in self._last_sql
        return {"exists": self.replica.has_service_orders}


class FakeConnection:
    def __init__(self, replica: FakeReplica) -> None:
        self.replica = replica
        self.session: dict | None = None
        self.closed = False

    def set_session(self, **kwargs: object) -> None:
        self.session = kwargs

    def cursor(self, cursor_factory: type) -> FakeCursor:
        assert cursor_factory is RealDictCursor
        return FakeCursor(self.replica)

    def close(self) -> None:
        self.closed = True


class FakeReplica:
    def __init__(self, tables: dict[str, list[dict]], has_service_orders: bool) -> None:
        self.tables = tables
        self.has_service_orders = has_service_orders
        self.executed: list[str] = []
        self.connect_calls: list[tuple[str, dict]] = []
        self.connection = FakeConnection(self)

    def connect(self, dsn: str, **kwargs: object) -> FakeConnection:
        self.connect_calls.append((dsn, kwargs))
        return self.connection


def _install_replica(monkeypatch, replica: FakeReplica) -> None:
    psycopg2 = types.ModuleType("psycopg2")
    psycopg2.connect = replica.connect
    extras = types.ModuleType("psycopg2.extras")
    extras.RealDictCursor = RealDictCursor
    psycopg2.extras = extras
    monkeypatch.setitem(sys.modules, "psycopg2", psycopg2)
    monkeypatch.setitem(sys.modules, "psycopg2.extras", extras)


def _rows(n: int, key: str, **extra: object) -> list[dict]:
    return [{key: i, **extra} for i in range(1, n + 1)]


@pytest.fixture
def ch():
    client = ClickHouseClient(database="fix_analytics")
    yield client
    client.close()


def test_dsn_defaults_to_replica_port_env(monkeypatch):
    monkeypatch.delenv("PG_READ_REPLICA_DSN", raising=False)
    monkeypatch.setenv("PG_REPLICA_PORT", "6543")

    engine = WarehouseSyncEngine(ch_client=ClickHouseClient())
    assert engine.pg_dsn == "postgresql://fix:change-me-dev-only@127.0.0.1:6543/fix_dev"
    assert WarehouseSyncEngine(pg_dsn="postgresql://x/y").pg_dsn == "postgresql://x/y"


def test_dsn_defaults_to_the_compose_replica_not_the_primary(monkeypatch):
    """The compose PRIMARY port is never used; the replica (docker-compose.superset.yml)
    lives on 5434 and is the only legal analytics source (LB-06)."""
    monkeypatch.delenv("PG_READ_REPLICA_DSN", raising=False)
    monkeypatch.delenv("PG_REPLICA_PORT", raising=False)

    assert WarehouseSyncEngine(ch_client=ClickHouseClient()).pg_dsn.endswith(
        "@127.0.0.1:5434/fix_dev"
    )


def test_extract_reads_replica_read_only_and_keeps_only_real_rows(monkeypatch, ch):
    branches = _rows(60, "branch_key", zone="Zone-1")
    customers = _rows(55, "customer_key", city="Dhaka")
    orders = _rows(120, "order_key", order_state="completed")
    replica = FakeReplica(
        {"res_branch": branches, "res_partner": customers, "fix_service_order": orders},
        has_service_orders=True,
    )
    _install_replica(monkeypatch, replica)
    engine = WarehouseSyncEngine(ch_client=ch, pg_dsn="postgresql://replica/fix")

    data = engine.extract_from_postgres()

    assert replica.connect_calls == [("postgresql://replica/fix", {"connect_timeout": 3})]
    assert replica.connection.session == {"readonly": True, "autocommit": True}  # LB-06
    assert replica.connection.closed is True
    assert all(sql.strip().upper().startswith("SELECT") for sql in replica.executed)
    assert len(replica.executed) == 4
    # Replica rows are kept verbatim ...
    assert data["dim_branch"] == branches
    assert data["dim_customer"] == customers
    assert data["fact_service_orders"] == orders
    # ... and every OTHER conformed object is reported empty - no synthesis.
    assert sorted(data) == sorted(TABLES)
    assert data["dim_date"] == []
    assert data["dim_device"] == []
    assert data["fact_nps"] == []
    assert engine.replica_reachable is True
    assert engine.extract_error is None


def test_extract_without_service_order_table_reports_orders_empty(monkeypatch, ch, caplog):
    caplog.set_level(logging.INFO, logger="warehouse_sync")
    replica = FakeReplica(
        {"res_branch": _rows(3, "branch_key"), "res_partner": _rows(2, "customer_key")},
        has_service_orders=False,
    )
    _install_replica(monkeypatch, replica)

    data = WarehouseSyncEngine(ch_client=ch).extract_from_postgres()

    assert len(replica.executed) == 3  # no fix_service_order SELECT
    assert "Extracted 3 branches, 2 customers from the read replica." in caplog.text
    # Only the rows the replica really holds; nothing is padded.
    assert len(data["dim_branch"]) == 3
    assert len(data["dim_customer"]) == 2
    assert data["fact_service_orders"] == []


def test_extract_reports_zero_rows_when_replica_unreachable(monkeypatch, ch, caplog):
    """A refused connection yields 0 real rows for EVERY table plus the reason -
    never the former synthetic baseline (53 branches, 730 dates, 200 orders...)."""
    caplog.set_level(logging.ERROR, logger="warehouse_sync")

    def refuse(dsn: str, **kwargs: object) -> None:
        raise ConnectionError("replica refused connection")

    replica = FakeReplica({}, has_service_orders=False)
    replica.connect = refuse
    _install_replica(monkeypatch, replica)

    engine = WarehouseSyncEngine(ch_client=ch)
    data = engine.extract_from_postgres()

    assert "Replica extract FAILED (replica refused connection)" in caplog.text
    assert "no synthetic baseline" in caplog.text
    assert {t: len(rows) for t, rows in data.items()} == dict.fromkeys(TABLES, 0)
    assert engine.replica_reachable is False
    assert engine.extract_error == "replica refused connection"


def test_run_full_sync_fails_vacuously_without_replica_rows(ch):
    """0 == 0 across ten empty tables proves nothing: the sync FAILs with the
    reason instead of certifying a padded reconciliation."""
    report = WarehouseSyncEngine(ch_client=ch).run_full_sync()

    assert report["status"] == "FAIL"
    assert report["replica_reachable"] is False
    assert "vacuous" in report["reason"]
    assert "unreachable" in report["reason"]
    assert report["lb06_read_replica_compliant"] is False


def test_regression_reconciliation_reads_back_the_warehouse(ch, isolated_warehouse):
    """Regression: reconciliation compared the source with the insert return values
    and hard-coded checksum_verified=True, so it passed whatever the warehouse held.

    Here every insert "reported" the full source count, yet the warehouse has a
    duplicated key, a missing table and stray rows - each must be caught.
    """
    source = {
        "dim_branch": _rows(3, "branch_key"),  # loaded faithfully
        "fact_nps": _rows(2, "survey_key"),  # same count, wrong keys (1, 1)
        "dim_device": _rows(2, "device_key"),  # never loaded
        "dim_technician": [],  # empty source, empty warehouse table
        "fact_invoices": [],  # empty source, but the warehouse holds a row
    }
    ch.insert_rows("dim_branch", _rows(3, "branch_key"))
    ch.insert_rows("fact_nps", [{"survey_key": 1}, {"survey_key": 1}])
    ch.execute("CREATE TABLE dim_technician (technician_key UInt32)")
    ch.insert_rows("fact_invoices", [{"invoice_key": 9}])
    claimed = {table: len(rows) for table, rows in source.items()}

    report = WarehouseSyncEngine(ch_client=ch).verify_reconciliation(source, claimed)

    tables = report["tables"]
    assert {
        t: (e["clickhouse_count"], e["checksum_verified"], e["reconciled"])
        for t, e in tables.items()
    } == {
        "dim_branch": (3, True, True),
        "fact_nps": (2, False, False),
        "dim_device": (None, False, False),
        "dim_technician": (0, True, True),
        "fact_invoices": (1, False, False),
    }
    assert tables["fact_nps"]["loaded_count"] == 2
    assert "no such table: dim_device" in tables["dim_device"]["error"]
    assert tables["dim_branch"]["error"] is None
    assert report["status"] == "FAIL"
    assert (report["total_source_rows"], report["total_clickhouse_rows"]) == (7, 6)
    evidence = isolated_warehouse.evidence_dir / "r09-m01-migration-reconciliation.json"
    assert json.loads(evidence.read_text(encoding="utf-8")) == report


def test_reconciliation_passes_only_with_tables_to_reconcile(ch):
    engine = WarehouseSyncEngine(ch_client=ch)
    ch.insert_rows("dim_branch", _rows(2, "branch_key"))

    assert engine.verify_reconciliation({"dim_branch": _rows(2, "branch_key")}, {})["status"] == (
        "PASS"
    )
    assert engine.verify_reconciliation({}, {})["status"] == "FAIL"  # nothing reconciled


def test_regression_repeated_full_sync_does_not_duplicate_rows(monkeypatch, ch):
    """Regression: every run_full_sync appended a full duplicate snapshot.

    The tables have no upsert key (MergeTree, and the embedded engine's
    INSERT OR REPLACE never conflicts), so the load is a full refresh. A fake
    replica supplies the real extracted rows.
    """
    _install_replica(
        monkeypatch,
        FakeReplica(
            {"res_branch": _rows(3, "branch_key"), "res_partner": _rows(2, "customer_key")},
            has_service_orders=False,
        ),
    )
    engine = WarehouseSyncEngine(ch_client=ch)
    first = engine.run_full_sync()
    second = engine.run_full_sync()

    assert first["status"] == second["status"] == "PASS"
    for table in TABLES:
        expected = second["tables"][table]["source_count"]
        actual = ch.execute(f"SELECT count(*) AS cnt FROM {table}")[0]["cnt"]
        assert actual == expected, table
    assert ch.execute("SELECT count(DISTINCT branch_key) AS d, count(*) AS n FROM dim_branch") == [
        {"d": 3, "n": 3}
    ]


def test_main_exit_code_follows_reconciliation(monkeypatch, isolated_warehouse):
    # No replica reachable in tests: the honest sync FAILs (0 real rows).
    assert warehouse_sync.main() == 1
    assert (isolated_warehouse.evidence_dir / "r09-m01-migration-reconciliation.json").exists()

    monkeypatch.setattr(WarehouseSyncEngine, "run_full_sync", lambda self: {"status": "PASS"})
    assert warehouse_sync.main() == 0
