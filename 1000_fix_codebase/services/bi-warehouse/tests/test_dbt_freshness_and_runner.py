#!/usr/bin/env python3
"""test_dbt_freshness_and_runner.py — Unit tests for dbt execution and freshness checking.

Milestone R09-M01-T02:
Tests source freshness calculated from the replica's REAL max(write_date) (the
previous implementation simulated an age of 30 minutes for every table), dbt
compilation, model builds, and evidence output.
"""

from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "services" / "bi-warehouse" / "src"
DBT_DIR = REPO_ROOT / "services" / "bi-warehouse" / "dbt"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(REPO_ROOT))

from clickhouse_client import ClickHouseClient
from dbt_runner import DbtWarehouseRunner


class TestDbtFreshnessAndRunner(unittest.TestCase):
    def setUp(self):
        self.ch = ClickHouseClient(database="fix_analytics")
        self.runner = DbtWarehouseRunner(ch_client=self.ch)
        # Per-test embedded DB comes from conftest.isolated_warehouse; release it.
        self.addCleanup(self.ch.close)

    def test_sources_yaml_exists_and_declares_freshness(self):
        """Verifies that sources.yml correctly declares oltp_replica and freshness rules."""
        sources_path = DBT_DIR / "models" / "sources.yml"
        self.assertTrue(sources_path.exists())
        text = sources_path.read_text(encoding="utf-8")
        self.assertIn("name: oltp_replica", text)
        self.assertIn("warn_after", text)
        self.assertIn("error_after", text)
        self.assertIn("loaded_at_field: write_date", text)

    def test_profiles_yaml_exists_for_clickhouse(self):
        """Verifies that profiles.yml defines ClickHouse targets."""
        profiles_path = DBT_DIR / "profiles.yml"
        self.assertTrue(profiles_path.exists())
        text = profiles_path.read_text(encoding="utf-8")
        self.assertIn("bi_warehouse:", text)
        self.assertIn("type: clickhouse", text)
        self.assertIn("schema: fix_analytics", text)

    def test_source_freshness_measured_from_real_write_date(self):
        """Freshness ages come from the replica's max(write_date), measured
        per table - never simulated."""
        now = datetime.now(UTC)
        ages = {
            "fix_service_order": timedelta(minutes=30),
            "account_move": timedelta(hours=2),
            "fix_warranty_claim": timedelta(hours=30),  # > warn (24h)
            "mail_message": timedelta(hours=50),  # > error (48h)
            "fix_nps": timedelta(hours=70),
            "res_partner": timedelta(hours=80),
            "res_branch": timedelta(hours=90),
        }
        self.runner._fetch_max_write_date = lambda table: now - ages[table]

        res = self.runner.run_source_freshness()

        self.assertEqual(res["status"], "FAIL")  # warn/error entries present
        by_table = {s["table"]: s for s in res["sources"]}
        self.assertGreaterEqual(len(res["sources"]), 7)
        self.assertEqual(by_table["fix_service_order"]["status"], "PASS")
        self.assertEqual(by_table["fix_warranty_claim"]["status"], "WARN")
        self.assertEqual(by_table["mail_message"]["status"], "ERROR")
        self.assertAlmostEqual(by_table["fix_service_order"]["age_hours"], 0.5, places=1)
        self.assertEqual(
            by_table["account_move"]["max_loaded_at"], (now - ages["account_move"]).isoformat()
        )

    def test_source_freshness_errors_honestly_when_replica_unreadable(self):
        """No replica reachable (conftest disables psycopg2): every table is
        ERROR with the real reason; no age is invented."""
        res = self.runner.run_source_freshness()

        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(res["sources"])
        for s in res["sources"]:
            self.assertEqual(s["status"], "ERROR", s)
            self.assertIsNone(s["age_hours"])
            self.assertIsNone(s["max_loaded_at"])
            self.assertIn("write_date not readable", s["error"])

    def test_scheduled_build_gated_by_unreadable_freshness(self):
        """Without a readable replica the scheduled run must FAIL at the
        freshness gate instead of building over invented freshness."""
        ev = self.runner.execute_scheduled_dbt_run()

        self.assertEqual(ev["status"], "FAIL")
        self.assertEqual(ev["reason"], "source_freshness_failed")
        self.assertEqual(ev["freshness"]["status"], "FAIL")

    def test_scheduled_build_with_measured_freshness(self):
        """With real (faked) write_date ages the build runs and counts the
        warehouse's true (0-row) contents."""
        now = datetime.now(UTC)
        self.runner._fetch_max_write_date = lambda table: now - timedelta(minutes=30)

        ev = self.runner.execute_scheduled_dbt_run()

        self.assertEqual(ev["milestone"], "R09-M01")
        self.assertEqual(ev["task"], "R09-M01-T02")
        # Sync had no replica rows: 0-row tables build and count honestly.
        self.assertEqual(ev["build"]["built_models_count"], 10)
        self.assertEqual(ev["build"]["models"][0]["rows_affected"], 0)
        self.assertEqual(ev["status"], "SUCCESS")
        self.assertEqual(ev["warehouse_mode"], "sqlite-fallback")  # labelled, not silent
        self.assertFalse(ev["lb06_read_only_downstream_verified"])


if __name__ == "__main__":
    unittest.main()
