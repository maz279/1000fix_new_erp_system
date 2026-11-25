"""D-030: telemetry retention runs as an Apache-2.0 drop_chunks wrapper called
daily by the telemetry_retention_daily DAG (TimescaleDB's own TSL scheduler is
never used)."""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from typing import ClassVar

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import dags.telemetry_retention_dag as dag_module

HOOK_MODULE = "airflow.providers.postgres.hooks.postgres"


class FakeHook:
    calls: ClassVar[list[tuple[str, str]]] = []
    row: ClassVar[tuple | None] = (3,)

    def __init__(self, postgres_conn_id: str):
        self.conn_id = postgres_conn_id

    def get_first(self, sql: str):
        FakeHook.calls.append((self.conn_id, sql))
        return FakeHook.row


class TestTelemetryRetentionDag(unittest.TestCase):
    def setUp(self):
        FakeHook.calls = []
        FakeHook.row = (3,)
        self._saved = {k: sys.modules.get(k) for k in (HOOK_MODULE,)}
        fake = types.ModuleType(HOOK_MODULE)
        fake.PostgresHook = FakeHook
        sys.modules[HOOK_MODULE] = fake

    def tearDown(self):
        for name, module in self._saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def test_daily_dag_calls_the_apache_retention_wrapper(self):
        self.assertEqual(dag_module.dag.schedule, "@daily")
        task = dag_module.dag.tasks["apply_telemetry_retention"]
        dropped = task.python_callable(**task.op_kwargs)
        self.assertEqual(dropped, 3)
        self.assertEqual(
            FakeHook.calls, [("fix_telemetry_db", "SELECT fix_telemetry_apply_retention();")]
        )

    def test_no_row_fails_the_task(self):
        FakeHook.row = None
        with self.assertRaises(dag_module.AirflowFailException):
            dag_module.apply_retention()

    def test_missing_postgres_provider_fails_the_task(self):
        sys.modules[HOOK_MODULE] = None  # makes the import raise ImportError
        with self.assertRaises(dag_module.AirflowFailException):
            dag_module.apply_retention()

    def test_dag_uses_no_tsl_feature(self):
        source = (REPO_ROOT / "dags" / "telemetry_retention_dag.py").read_text(encoding="utf-8")
        for tsl in ("add_retention_policy(", "add_job(", "add_compression_policy("):
            self.assertNotIn(tsl, source)


if __name__ == "__main__":
    unittest.main()
