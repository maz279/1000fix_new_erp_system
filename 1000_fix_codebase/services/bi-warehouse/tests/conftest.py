"""Per-test isolation for the bi-warehouse suites (autouse).

The embedded analytics engine defaults to ONE fixed file,
``%TEMP%/1000fix_analytics_embedded.db``, shared by every ClickHouseClient in every
process on the machine. Tests sharing it collided ("database is locked") with any
concurrent run and accumulated a duplicate snapshot per sync. Every test here gets:

- its own embedded DB file under ``tmp_path`` (``CLICKHOUSE_EMBEDDED_PATH``);
- no network: ``urllib.request.urlopen`` raises, so the ClickHouse ping falls back to
  the embedded engine, and ``psycopg2`` is unimportable, so the replica extract falls
  back to the conformed baseline (tests that exercise those paths patch fakes in);
- evidence JSON redirected under ``tmp_path`` instead of ``docs/traceability/evidence``;
- every sqlite connection opened during the test closed at teardown.
"""

from __future__ import annotations

import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import pytest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[3]
for _path in (str(REPO_ROOT), str(SRC_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Modules whose EVIDENCE_DIR global points into the repository.
EVIDENCE_MODULES = ("catalogue_engine", "warehouse_sync", "dbt_runner", "run_nfr039_profile")


def _no_network(*args, **kwargs):
    raise urllib.error.URLError("network disabled in bi-warehouse tests")


@pytest.fixture(autouse=True)
def isolated_warehouse(tmp_path, monkeypatch):
    """Isolates the embedded DB, network, Postgres driver and evidence output."""
    db_path = tmp_path / "analytics_embedded.db"
    evidence_dir = tmp_path / "evidence"
    monkeypatch.setenv("CLICKHOUSE_EMBEDDED_PATH", str(db_path))
    monkeypatch.setattr(urllib.request, "urlopen", _no_network)
    monkeypatch.setitem(sys.modules, "psycopg2", None)
    monkeypatch.setitem(sys.modules, "psycopg2.extras", None)
    for name in EVIDENCE_MODULES:
        module = sys.modules.get(name)
        if module is not None:
            monkeypatch.setattr(module, "EVIDENCE_DIR", evidence_dir)

    opened: list[sqlite3.Connection] = []
    real_connect = sqlite3.connect

    def tracking_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        opened.append(conn)
        return conn

    monkeypatch.setattr(sqlite3, "connect", tracking_connect)
    yield SimpleNamespace(db_path=db_path, evidence_dir=evidence_dir, tmp_path=tmp_path)
    for conn in opened:
        conn.close()
