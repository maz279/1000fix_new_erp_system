"""
test_migration_wave1.py - Unit and Integration tests for Milestone R02-M04 Wave-1 Migration Loads.
Tests:
  - Pipeline execution and end-to-end topological loading
  - Branch loader: 6 branches, code mapping (BR:*)
  - Customer loader: M64 phone dedup (49/50), Z4 residency routing, no raw NID in res_partner
  - Device loader: 50 devices, warranty creation with BDT currency, state registered
  - Employee loader: 20 employees, resource_resource defaults, outbox JML event
  - Control totals: MIG-02 verification passes
  - Master data: 48 datasets across 10 tiers loaded into fix_master_data_register
"""

import os
import subprocess
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

DB_HOST = os.environ.get("PGHOST", "localhost")
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

def test_pipeline_execution():
    """Verify that running the pipeline succeeds and reconciles all control totals."""
    cmd = ["python", "migrations/pipeline.py"]
    res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
    assert res.returncode == 0, f"Pipeline failed: {res.stderr}\n{res.stdout}"
    assert "Wave-1 Migration Pipeline COMPLETED & RECONCILED" in res.stdout

def test_branches_loaded(db_conn):
    """Verify 6 branches are loaded with legacy references."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT code, name, legacy_reference FROM fix_branch WHERE legacy_reference LIKE 'BR:%'")
        rows = cur.fetchall()
        assert len(rows) == 6, f"Expected 6 branches, found {len(rows)}"
        codes = {r["code"] for r in rows}
        assert "HQ" in codes
        assert "PC-01" in codes

def test_customer_deduplication_and_residency(db_conn):
    """
    Verify 49 customers loaded (1 duplicate phone quarantined).
    Verify MIG-06: zero raw NID numbers in res_partner and Z4 residency tokens created.
    """
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name, phone, legacy_reference FROM res_partner WHERE legacy_reference LIKE 'CUST:%'")
        customers = cur.fetchall()
        assert len(customers) == 49, f"Expected 49 loaded customers, found {len(customers)}"
        
        # Verify residency tokens exist in fix_identity_document
        cur.execute("""
            SELECT id, residency_ref, document_type 
            FROM fix_identity_document 
            WHERE partner_id IN (SELECT id FROM res_partner WHERE legacy_reference LIKE 'CUST:%')
        """)
        id_docs = cur.fetchall()
        assert len(id_docs) == 49, f"Expected 49 identity documents with Z4 tokens, found {len(id_docs)}"
        assert all(doc["residency_ref"] is not None for doc in id_docs)

        # Assert no raw NID columns exist on res_partner that contain unclassified NIDs
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'res_partner' AND column_name LIKE '%nid%'")
        nid_cols = [r["column_name"] for r in cur.fetchall()]
        for col in nid_cols:
            cur.execute(f"SELECT COUNT(*) as count FROM res_partner WHERE {col} IS NOT NULL AND {col} != ''")
            count = cur.fetchone()["count"]
            assert count == 0, f"MIG-06 VIOLATION: Raw NID found in res_partner.{col} ({count} rows)"

def test_devices_and_warranties(db_conn):
    """Verify 50 devices loaded with warranty records and BDT currency."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, serial_number, state, legacy_reference FROM fix_device WHERE legacy_reference LIKE 'DEV:%'")
        devices = cur.fetchall()
        assert len(devices) == 50, f"Expected 50 devices, found {len(devices)}"
        assert all(d["state"] == "registered" for d in devices)

        cur.execute("""
            SELECT w.id, w.currency_id, c.name as curr_name
            FROM fix_warranty w
            LEFT JOIN res_currency c ON w.currency_id = c.id
            JOIN fix_device d ON w.device_id = d.id
            WHERE d.legacy_reference LIKE 'DEV:%'
        """)
        warranties = cur.fetchall()
        assert len(warranties) == 50, f"Expected 50 warranties, found {len(warranties)}"
        assert all(w["curr_name"] == "BDT" for w in warranties)

def test_employees_and_outbox_events(db_conn):
    """Verify 20 employees loaded, Dhaka tz, 100% efficiency, and outbox event recorded."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT e.id, e.work_email, r.tz, r.time_efficiency
            FROM hr_employee e
            JOIN resource_resource r ON e.resource_id = r.id
            WHERE e.legacy_reference LIKE 'EMP:%'
        """)
        employees = cur.fetchall()
        assert len(employees) == 20, f"Expected 20 employees, found {len(employees)}"
        assert all(e["tz"] == "Asia/Dhaka" for e in employees)
        assert all(e["time_efficiency"] == 100.0 for e in employees)

        # Check outbox events
        cur.execute("SELECT COUNT(*) as count FROM fix_event_outbox WHERE event_type = 'employee.imported'")
        outbox_count = cur.fetchone()["count"]
        assert outbox_count >= 20, f"Expected at least 20 employee.imported outbox events, got {outbox_count}"

def test_mig_totals_control_verification():
    """Verify mig-totals.py runs cleanly against extracts and loaded counts."""
    cmd = [
        "python", "tooling/scripts/mig-totals.py",
        "--manifest", "migrations/extracts/control-totals.json",
        "--loaded", "migrations/extracts/loaded-counts.json"
    ]
    res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
    assert res.returncode == 0, f"mig-totals verification failed: {res.stderr}\n{res.stdout}"
    assert "every control total reconciled" in res.stdout

def test_master_data_loaded(db_conn):
    """Verify 48 master data specifications across 10 tiers exist in fix_master_data_register."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT COUNT(*) as total, COUNT(DISTINCT tier) as tiers FROM fix_master_data_register")
        row = cur.fetchone()
        assert row["total"] == 48, f"Expected 48 master data records, found {row['total']}"
        assert row["tiers"] == 10, f"Expected 10 tiers (T0-T9), found {row['tiers']}"

        cur.execute("SELECT COUNT(*) as payload_count FROM fix_master_data_payload")
        prow = cur.fetchone()
        assert prow["payload_count"] >= 146, f"Expected at least 146 payloads, found {prow['payload_count']}"
