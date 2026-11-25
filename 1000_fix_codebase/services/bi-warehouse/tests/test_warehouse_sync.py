#!/usr/bin/env python3
"""test_warehouse_sync.py — Unit Tests for Warehouse Sync and Migration Reconciliation.

Milestone R09-M01-T01:
Validates ClickHouse schema initialization, REAL replica extraction (via a fake
read-only psycopg2), reconciliation between source and analytical warehouse,
and the honest 0-row reporting when the replica is unreachable (conftest makes
psycopg2 unimportable, which is exactly that case).
"""

from __future__ import annotations

import sys
import types
import unittest
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "services" / "bi-warehouse" / "src"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(REPO_ROOT))

from clickhouse_client import ClickHouseClient
from warehouse_sync import WarehouseSyncEngine


class _FakeReplica:
    """Minimal read-only psycopg2 double serving fixed rows."""

    def __init__(self) -> None:
        self.rows_by_table = {
            "res_branch": [
                {
                    "branch_key": i,
                    "branch_code": f"BR-{i:03d}",
                    "name": f"Branch {i}",
                    "division": "Dhaka",
                    "district": "Dhaka",
                    "zone": "Zone-1",
                    "is_active": True,
                    "service_capacity_daily": 50,
                }
                for i in range(1, 54)
            ],
            "res_partner": [
                {
                    "customer_key": i,
                    "pseudonym_hash": f"{i:032x}",
                    "customer_type": "retail",
                    "city": "Dhaka",
                    "division": "Dhaka",
                    "is_verified": 1,
                    "created_at": datetime(2025, 6, 1, tzinfo=UTC),
                }
                for i in range(1, 11)
            ],
        }

    def connect(self, dsn: str, **kwargs: object):
        outer = self

        class _Cur:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def execute(self, sql: str):
                self.sql = sql

            def fetchall(self):
                # dim_branch reads fix_branch (joined to fix_entity/res_country
                # - R01 re-audit fix; res_branch never existed); route on it.
                for table, rows in outer.rows_by_table.items():
                    if table == "res_branch" and "FROM fix_branch" in self.sql:
                        return rows
                    if f"FROM {table}" in self.sql:
                        return rows
                return []

            def fetchone(self):
                assert "information_schema.tables" in self.sql
                return {"exists": False}  # no fix_service_order table

        class _Conn:
            def set_session(self, **kw):
                pass

            def cursor(self, cursor_factory=None):
                return _Cur()

            def close(self):
                pass

        return _Conn()


def _install_fake_replica(testcase: unittest.TestCase) -> _FakeReplica:
    """Puts a fake psycopg2 into sys.modules; removed on teardown."""
    replica = _FakeReplica()
    psycopg2 = types.ModuleType("psycopg2")
    psycopg2.connect = replica.connect
    extras = types.ModuleType("psycopg2.extras")
    extras.RealDictCursor = object()  # sentinel cursor factory
    psycopg2.extras = extras
    old = {name: sys.modules.get(name) for name in ("psycopg2", "psycopg2.extras")}
    sys.modules["psycopg2"] = psycopg2
    sys.modules["psycopg2.extras"] = extras

    def restore():
        for name, module in old.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    testcase.addCleanup(restore)
    return replica


class TestWarehouseSync(unittest.TestCase):
    def setUp(self):
        self.ch = ClickHouseClient(database="fix_analytics")
        self.engine = WarehouseSyncEngine(ch_client=self.ch)
        # Per-test embedded DB comes from conftest.isolated_warehouse; release it.
        self.addCleanup(self.ch.close)

    def test_schema_initialization(self):
        """Verifies that all 10 dimensional tables and views are initialized."""
        self.engine.init_clickhouse_schema()
        # Verify tables can be queried
        for tbl in WarehouseSyncEngine.CONFORMED_TABLES:
            res = self.ch.execute(f"SELECT count(*) as cnt FROM {tbl}")
            self.assertIsInstance(res, list)

    def test_end_to_end_sync_with_real_replica_rows(self):
        """Full sync over REAL extracted rows reconciles 100% (53 branches)."""
        replica = _install_fake_replica(self)

        report = self.engine.run_full_sync()

        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["lb06_read_replica_compliant"])
        self.assertTrue(report["nfr086c_pii_pseudonymized"])
        self.assertEqual(report["tables"]["dim_branch"]["source_count"], 53)
        self.assertEqual(report["tables"]["dim_customer"]["source_count"], 10)
        self.assertEqual(report["total_source_rows"], report["total_clickhouse_rows"])
        self.assertGreater(report["total_source_rows"], 0)

        # dim_customer carries md5 pseudonym_hash only (NFR-086c)
        cust_rows = self.ch.execute("SELECT pseudonym_hash, is_verified FROM dim_customer")
        self.assertEqual(len(cust_rows), len(replica.rows_by_table["res_partner"]))
        for r in cust_rows:
            self.assertEqual(len(r["pseudonym_hash"]), 32)
            self.assertEqual(r["is_verified"], 1)

    def test_tables_without_a_replica_source_report_zero_honestly(self):
        """Tables the replica does not feed (dim_date, facts other than service
        orders) load 0 rows - never a synthetic baseline."""
        _install_fake_replica(self)

        self.engine.run_full_sync()

        for table in ("dim_date", "dim_device", "dim_technician", "fact_invoices"):
            self.assertEqual(self.ch.execute(f"SELECT count(*) as cnt FROM {table}")[0]["cnt"], 0)

    def test_unreachable_replica_reports_zero_rows_and_fails(self):
        """conftest leaves psycopg2 unimportable: the sync must report 0 rows
        with the reason and FAIL - not reconcile a fabricated baseline."""
        report = self.engine.run_full_sync()

        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["lb06_read_replica_compliant"])
        self.assertFalse(report["replica_reachable"])
        self.assertIn("reason", report)
        self.assertIn("vacuous", report["reason"])
        self.assertIn("unreachable", report["reason"])
        self.assertIsNotNone(report["extract_error"])
        self.assertEqual(report["total_source_rows"], 0)
        self.assertEqual(report["total_clickhouse_rows"], 0)
        for entry in report["tables"].values():
            self.assertEqual(entry["source_count"], 0)


if __name__ == "__main__":
    unittest.main()
