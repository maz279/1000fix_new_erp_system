"""
migrations/tests/test_migration_inventory.py — Tests for Wave-2 M15 Inventory Physical Baseline Migration.
Verifies:
  - Inventory ETL load execution
  - 150 SKUs loaded into fix_spare_part
  - 10 stock locations (5 hubs + 5 vans) loaded into fix_stock_location
  - Suspense entries in fix_inventory_valuation_suspense with STUB-M15-M19-001 and account 110999
  - Physical count accuracy >= 95.0%
  - G2-04 reconciliation signoff artifact existence and contents
"""
from __future__ import annotations

import os
import subprocess
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

DB_HOST = os.environ.get("PGHOST", "127.0.0.1")
DB_PORT = int(os.environ.get("PGPORT", "5433"))
DB_NAME = os.environ.get("PGDATABASE", "fix_dev")
DB_USER = os.environ.get("PGUSER", "fix")
DB_PASS = os.environ.get("PGPASSWORD", "change-me-dev-only")

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="module")
def db_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    conn.autocommit = True
    yield conn
    conn.close()


def test_inventory_migration_execution():
    """Verify that running load_inventory.py succeeds."""
    cmd = ["python", "migrations/load_inventory.py"]
    res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
    assert res.returncode == 0, f"Migration failed: {res.stderr}\n{res.stdout}"
    assert "Gate Criterion G2-04 Status: PASS" in res.stdout
    assert "Inventory Accuracy: 99.51%" in res.stdout


def test_spare_parts_catalog_loaded(db_conn):
    """Verify 150 SKUs are loaded in fix_spare_part."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT count(*) as cnt FROM fix_spare_part WHERE legacy_reference LIKE 'LEG:SRC37:%';")
        cnt = cur.fetchone()["cnt"]
        assert cnt >= 150, f"Expected at least 150 parts, got {cnt}"


def test_stock_locations_loaded(db_conn):
    """Verify 10 stock locations (5 Hubs + 5 Vans) are present."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT code, location_type, is_van_location FROM fix_stock_location;")
        rows = cur.fetchall()
        assert len(rows) >= 10, f"Expected at least 10 locations, got {len(rows)}"
        van_locations = [r for r in rows if r["is_van_location"] or r["location_type"] == "van"]
        assert len(van_locations) >= 5, f"Expected at least 5 van locations, got {len(van_locations)}"


def test_valuation_suspense_entries(db_conn):
    """Verify suspense entries posted to account 110999 with STUB-M15-M19-001."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT count(*) as cnt, sum(total_valuation) as val, stub_reference, suspense_account_code
            FROM fix_inventory_valuation_suspense
            GROUP BY stub_reference, suspense_account_code;
        """)
        rows = cur.fetchall()
        assert len(rows) > 0
        match = [r for r in rows if r["stub_reference"] == "STUB-M15-M19-001" and r["suspense_account_code"] == "110999"]
        assert len(match) == 1, "Expected STUB-M15-M19-001 row in fix_inventory_valuation_suspense"
        assert match[0]["val"] > 0, "Valuation sum must be positive"


def test_reconciliation_signoff_document():
    """Verify inventory reconciliation signoff artifact exists and discharges G2-04."""
    signoff_path = BASE_DIR / "docs" / "traceability" / "inventory-reconciliation-signoff.md"
    assert signoff_path.is_file(), "Reconciliation signoff document must exist"
    content = signoff_path.read_text(encoding="utf-8")
    assert "PASSED (G2-04 DISCHARGED)" in content
    assert "99.51%" in content
    assert "STUB-M15-M19-001" in content
