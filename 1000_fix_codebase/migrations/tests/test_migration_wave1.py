"""
test_migration_wave1.py - Unit and Integration tests for Milestone R02-M04 Wave-1 Migration Loads.
Tests:
  - Pipeline execution and end-to-end topological loading
  - Branch loader: 6 branches, code mapping (BR:*)
  - Customer loader: M64 phone dedup (49/50), Z4 residency routing, no raw NID in res_partner
  - Device loader: 49 devices + 1 duplicate-serial MDM quarantine, warranty with BDT
    currency, warranty state derived from the end date at load time
  - Employee loader: 20 employees, resource_resource defaults, outbox JML event
  - Control totals: MIG-02 verification passes
  - Master data: 48 datasets across 10 tiers loaded into fix_master_data_register

Target: the dedicated, clean rehearsal database `fix_migration` (db_conn /
rehearsal_dsn / pipeline_run fixtures in conftest.py) - skipped with the build
command when it does not exist. Procedure: migrations/REHEARSAL.md.
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
from psycopg2.extras import RealDictCursor

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# every DB assertion below reads the state the (once-per-session) pipeline run left
pytestmark = pytest.mark.usefixtures("pipeline_run")


def test_pipeline_execution(pipeline_run):
    """Verify that running the pipeline succeeds and reconciles all control totals."""
    res, loaded_counts, before, after = pipeline_run
    assert res.returncode == 0, f"Pipeline failed: {res.stderr}\n{res.stdout}"
    assert "Wave-1 Migration Pipeline COMPLETED: control totals reconciled (MIG-02)" in res.stdout
    counts = json.loads(loaded_counts.read_text(encoding="utf-8"))
    quarantined = sum(counts["quarantined_records"].values())
    # the banner states the measured quarantine count - never a bare "RECONCILED"
    assert f"{quarantined} quarantined" in res.stdout
    if quarantined:
        assert "pending MG-004 steward disposition" in res.stdout
    assert loaded_counts.is_file()
    assert after == before, "the pipeline test run mutated committed migrations/extracts"


def test_branches_loaded(db_conn):
    """Verify 6 branches are loaded with legacy references."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT code, name, legacy_reference FROM fix_branch WHERE legacy_reference LIKE 'BR:%'"
        )
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
        cur.execute(
            "SELECT id, name, phone, legacy_reference FROM res_partner WHERE legacy_reference LIKE 'CUST:%'"
        )
        customers = cur.fetchall()
        assert len(customers) == 49, f"Expected 49 loaded customers, found {len(customers)}"

        # Verify residency tokens exist in fix_identity_document
        cur.execute("""
            SELECT id, residency_ref, document_type
            FROM fix_identity_document
            WHERE partner_id IN (SELECT id FROM res_partner WHERE legacy_reference LIKE 'CUST:%')
        """)
        id_docs = cur.fetchall()
        assert (
            len(id_docs) == 49
        ), f"Expected 49 identity documents with Z4 tokens, found {len(id_docs)}"
        assert all(doc["residency_ref"] is not None for doc in id_docs)

        # Assert no raw NID columns exist on res_partner that contain unclassified NIDs
        cur.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'res_partner' AND column_name LIKE '%nid%'"
        )
        nid_cols = [r["column_name"] for r in cur.fetchall()]
        for col in nid_cols:
            cur.execute(
                f"SELECT COUNT(*) as count FROM res_partner WHERE {col} IS NOT NULL AND {col} != ''"
            )
            count = cur.fetchone()["count"]
            assert (
                count == 0
            ), f"MIG-06 VIOLATION: Raw NID found in res_partner.{col} ({count} rows)"


def test_devices_and_warranties(db_conn):
    """Verify 49 devices loaded (device 50 = duplicate serial, quarantined) with BDT
    warranties, and the warranty state derived from the end date at load time."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, serial_number, imei_1, state, warranty_status, legacy_reference "
            "FROM fix_device WHERE legacy_reference LIKE 'DEV:%'"
        )
        devices = cur.fetchall()
        assert len(devices) == 49, f"Expected 49 devices, found {len(devices)}"
        assert all(d["state"] == "registered" for d in devices)
        # the duplicate (DEV-AST-2050) never overwrote device 1
        dup = [d for d in devices if d["serial_number"] == "SN-OPP-2026001"]
        assert len(dup) == 1
        assert dup[0]["imei_1"] == "358901000000001"

        cur.execute("""
            SELECT w.id, w.end_date, w.warranty_type, w.status, c.name as curr_name,
                   d.warranty_status
            FROM fix_warranty w
            LEFT JOIN res_currency c ON w.currency_id = c.id
            JOIN fix_device d ON w.device_id = d.id
            WHERE d.legacy_reference LIKE 'DEV:%'
        """)
        warranties = cur.fetchall()
        assert len(warranties) == 49, f"Expected 49 warranties, found {len(warranties)}"
        assert all(w["curr_name"] == "BDT" for w in warranties)
        assert all(w["warranty_type"] == "manufacturer" for w in warranties)
        assert all(w["status"] == "active" for w in warranties)
        # extract warranties end 2026-06-15: out of warranty for any load after that date
        for w in warranties:
            expected = "in_warranty" if w["end_date"] >= date.today() else "out_of_warranty"
            assert w["warranty_status"] == expected, w
        assert any(w["warranty_status"] == "out_of_warranty" for w in warranties)


def test_device_duplicate_serial_quarantined(pipeline_run):
    """ETL-2 MDM gate: the extract's duplicate serial is quarantined, not loaded."""
    counts = json.loads(pipeline_run[1].read_text(encoding="utf-8"))
    assert counts["accepted_records"]["devices"] == 49
    assert counts["quarantined_records"]["devices"] == 1
    assert counts["loaded_totals"]["devices"] == 50  # every extracted record dispositioned
    (rejection,) = counts["rejections"]["devices"]
    assert rejection["source_id"] == "DEV-AST-2050"
    assert rejection["serial_number"] == "SN-OPP-2026001"
    assert rejection["reason"].startswith("MDM collision")


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
        cur.execute(
            "SELECT COUNT(*) as count FROM fix_event_outbox WHERE event_type = 'employee.imported'"
        )
        outbox_count = cur.fetchone()["count"]
        assert (
            outbox_count >= 20
        ), f"Expected at least 20 employee.imported outbox events, got {outbox_count}"


def test_mig_totals_control_verification(pipeline_run):
    """Verify mig-totals.py runs cleanly against extracts and loaded counts."""
    cmd = [
        sys.executable,
        "tooling/scripts/mig-totals.py",
        "--manifest",
        "migrations/extracts/control-totals.json",
        "--loaded",
        str(pipeline_run[1]),
    ]
    res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)  # noqa: S603 - fixed argv list built in-process, no shell
    assert res.returncode == 0, f"mig-totals verification failed: {res.stderr}\n{res.stdout}"
    assert "every control total reconciled" in res.stdout


def test_master_data_loaded(db_conn):
    """Verify 48 master data specifications across 10 tiers exist in fix_master_data_register."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT COUNT(*) as total, COUNT(DISTINCT tier) as tiers FROM fix_master_data_register"
        )
        row = cur.fetchone()
        assert row["total"] == 48, f"Expected 48 master data records, found {row['total']}"
        assert row["tiers"] == 10, f"Expected 10 tiers (T0-T9), found {row['tiers']}"

        cur.execute("SELECT COUNT(*) as payload_count FROM fix_master_data_payload")
        prow = cur.fetchone()
        assert (
            prow["payload_count"] >= 146
        ), f"Expected at least 146 payloads, found {prow['payload_count']}"
