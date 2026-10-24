"""Wave-1 loader rules (GV-009): no fallback ids, no silent drops, idempotent re-runs.

  - company / operating unit of every migrated device, warranty, employee and
    customer are its branch's - never "the first company" or OU1 by default
  - a record whose branch / role / owner is not on the target, or whose serial or
    phone is already held by a DIFFERENT target record, is REJECTED with a reason
    (counted and listed) and nothing is written - it never overwrites the holder
  - re-running every Wave-1 loader on the committed extracts changes no row count
  - ETL-0 never invents a brand code or an operating-unit name, and refuses to guess
    a company on a multi-company target

DB-backed tests run against `fix_migration` after the session's pipeline run and
are skipped (with the build command) when it does not exist. Rejected records are
never written, so these tests leave the rehearsal state unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path

import psycopg2
import pytest

from migrations.load_branches import load_branches
from migrations.load_customers import load_customers
from migrations.load_devices import load_devices
from migrations.load_employees import load_employees
from migrations.load_reference_data import _company, _ensure_catalogue, _ensure_operating_units

EXTRACTS_DIR = Path(__file__).resolve().parents[1] / "extracts"


@pytest.fixture
def conn(rehearsal_dsn, pipeline_run):
    connection = psycopg2.connect(rehearsal_dsn)
    yield connection
    connection.rollback()
    connection.close()


def _extract(tmp_path: Path, records: list[dict]) -> Path:
    path = tmp_path / "extract.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return path


def _counts(cur) -> dict[str, int]:
    queries = {
        "branches": "SELECT count(*) FROM fix_branch WHERE legacy_reference LIKE 'BR:%'",
        "customers": "SELECT count(*) FROM res_partner WHERE legacy_reference LIKE 'CUST:%'",
        "party_roles": "SELECT count(*) FROM fix_party_role",
        "identity_docs": "SELECT count(*) FROM fix_identity_document",
        "devices": "SELECT count(*) FROM fix_device WHERE legacy_reference LIKE 'DEV:%'",
        "warranties": "SELECT count(*) FROM fix_warranty",
        "employees": "SELECT count(*) FROM hr_employee WHERE legacy_reference LIKE 'EMP:%'",
        "resources": "SELECT count(*) FROM resource_resource",
        "outbox": "SELECT count(*) FROM fix_event_outbox WHERE event_type = 'employee.imported'",
    }
    out = {}
    for key, query in queries.items():
        cur.execute(query)
        out[key] = cur.fetchone()[0]
    return out


def test_company_and_operating_unit_come_from_the_branch(db_conn):
    with db_conn.cursor() as cur:
        for table, pattern in (
            ("fix_device", "DEV:%"),
            ("hr_employee", "EMP:%"),
        ):
            cur.execute(
                f"""SELECT count(*), count(*) FILTER (
                        WHERE t.company_id = b.company_id
                          AND t.operating_unit_id IS NOT DISTINCT FROM b.operating_unit_id)
                    FROM {table} t JOIN fix_branch b ON b.id = t.branch_id
                    WHERE t.legacy_reference LIKE %s""",
                (pattern,),
            )
            total, matching = cur.fetchone()
            assert total > 0 and total == matching, table
        cur.execute("""
            SELECT count(*), count(*) FILTER (WHERE w.company_id = d.company_id
                                 AND w.operating_unit_id IS NOT DISTINCT FROM d.operating_unit_id)
            FROM fix_warranty w JOIN fix_device d ON d.id = w.device_id
            WHERE d.legacy_reference LIKE 'DEV:%'
        """)
        total, matching = cur.fetchone()
        assert total == matching == 49
        cur.execute(
            "SELECT count(*) FROM fix_device WHERE legacy_reference LIKE 'DEV:%' AND branch_id IS NULL"
        )
        assert cur.fetchone()[0] == 0


def test_device_with_unknown_branch_or_owner_or_held_serial_is_rejected(conn, tmp_path):
    base = {"brand_name": "Oppo", "device_model_name": "Reno 11", "imei_1": "", "imei_2": ""}
    records = [
        {
            **base,
            "serial_number": "SN-TST-0001",
            "branch_code": "NO-SUCH-BRANCH",
            "legacy_reference": "DEV:ASSET_SHEET:SN-TST-0001",
        },
        {
            **base,
            "serial_number": "SN-TST-0002",  # no branch_code at all: no default HQ
            "legacy_reference": "DEV:ASSET_SHEET:SN-TST-0002",
        },
        {
            **base,
            "serial_number": "SN-TST-0003",
            "branch_code": "HQ",
            "customer_legacy_ref": "CUST:WP_STORE:NOPE",
            "legacy_reference": "DEV:ASSET_SHEET:SN-TST-0003",
        },
        {
            **base,
            "serial_number": "SN-OPP-2026001",
            "branch_code": "HQ",  # held by device 1
            "legacy_reference": "DEV:ASSET_SHEET:TST-DUP",
        },
    ]
    result = load_devices(_extract(tmp_path, records), conn)
    assert result["loaded_count"] == 0
    assert result["rejected_count"] == 4
    reasons = [r.get("reason") or r.get("error") for r in result["rejections"]]
    assert "branch 'NO-SUCH-BRANCH' not found" in reasons[0]
    assert "branch None not found" in reasons[1]
    assert "owner 'CUST:WP_STORE:NOPE' not loaded" in reasons[2]
    assert "MDM collision: serial already held by target device" in reasons[3]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM fix_device WHERE legacy_reference LIKE 'DEV:ASSET_SHEET:%TST%'"
        )
        assert cur.fetchone()[0] == 0
        cur.execute(
            "SELECT legacy_reference, imei_1 FROM fix_device WHERE serial_number = 'SN-OPP-2026001'"
        )
        assert cur.fetchall() == [("DEV:ASSET_SHEET:SN-OPP-2026001", "358901000000001")]


def test_employee_with_unknown_branch_or_role_is_rejected(conn, tmp_path):
    base = {"name": "Test Person", "email": "", "phone": "", "nid": ""}
    records = [
        {
            **base,
            "employee_code": "TST-E-1",
            "branch_code": "NO-SUCH-BRANCH",
            "primary_role": "R-01",
            "legacy_reference": "EMP:PAYROLL_2026:TST-E-1",
        },
        {
            **base,
            "employee_code": "TST-E-2",
            "branch_code": "HQ",
            "primary_role": "R-NOPE",
            "legacy_reference": "EMP:PAYROLL_2026:TST-E-2",
        },
        {
            **base,
            "employee_code": "TST-E-3",
            "branch_code": "HQ",  # no role: no default R-01
            "legacy_reference": "EMP:PAYROLL_2026:TST-E-3",
        },
    ]
    result = load_employees(_extract(tmp_path, records), conn)
    assert (result["loaded_count"], result["rejected_count"]) == (0, 3)
    reasons = [r["reason"] for r in result["rejections"]]
    assert "branch 'NO-SUCH-BRANCH' not found" in reasons[0]
    assert "primary role 'R-NOPE' not found" in reasons[1]
    assert "primary role None not found" in reasons[2]
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM hr_employee WHERE employee_code LIKE 'TST-E-%'")
        assert cur.fetchone()[0] == 0


def test_customer_with_unknown_branch_or_held_phone_is_rejected(conn, tmp_path):
    base = {"name": "Test Customer", "email": "", "nid": "", "roles": ["customer"]}
    records = [
        {
            **base,
            "phone": "880199000001",
            "branch_code": "NO-SUCH-BRANCH",
            "legacy_reference": "CUST:WP_STORE:TST-1",
        },
        {
            **base,
            "phone": "880171000001",
            "branch_code": "HQ",  # held by CUST:WP_STORE:1001
            "legacy_reference": "CUST:WP_STORE:TST-2",
        },
    ]
    result = load_customers(_extract(tmp_path, records), conn)
    assert (result["loaded_count"], result["rejected_count"]) == (0, 2)
    reasons = [r["reason"] for r in result["rejections"]]
    assert "branch 'NO-SUCH-BRANCH' not found" in reasons[0]
    assert "M64 dedup: phone already held by target partner" in reasons[1]
    assert "CUST:WP_STORE:1001" in reasons[1]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM res_partner WHERE legacy_reference LIKE 'CUST:WP_STORE:TST%'"
        )
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT name FROM res_partner WHERE legacy_reference = 'CUST:WP_STORE:1001'")
        assert cur.fetchone()[0] == "Rahim Ahmed"  # the holder was not overwritten


def test_rerunning_every_wave1_loader_is_idempotent(conn):
    with conn.cursor() as cur:
        before = _counts(cur)
    conn.rollback()
    results = [
        load_branches(EXTRACTS_DIR / "branches_extract.json", conn),
        load_customers(EXTRACTS_DIR / "customers_extract.json", conn),
        load_devices(EXTRACTS_DIR / "devices_extract.json", conn),
        load_employees(EXTRACTS_DIR / "employees_extract.json", conn),
    ]
    with conn.cursor() as cur:
        after = _counts(cur)
    assert after == before
    assert [(r["loaded_count"], r["rejected_count"]) for r in results] == [
        (6, 0),
        (49, 1),
        (49, 1),
        (20, 0),
    ]


def test_reference_data_never_invents_codes_or_names(conn):
    with conn.cursor() as cur:
        company_id, partner_id = _company(cur)
        devices = [{"brand_name": "TstNoCode", "device_model_name": "X1", "device_type": "mobile"}]
        total, brands_created, models_created, without_code = _ensure_catalogue(
            cur, devices, {"brand_codes": {}}, company_id
        )
        assert (total, brands_created, models_created, without_code) == (1, 0, 0, ["TstNoCode"])
        cur.execute("SELECT count(*) FROM fix_brand WHERE name = 'TstNoCode'")
        assert cur.fetchone()[0] == 0
        created, missing = _ensure_operating_units(cur, ["OU-TST-NOPE"], {}, company_id, partner_id)
        assert (created, missing) == (0, ["OU-TST-NOPE"])
        cur.execute("SELECT count(*) FROM operating_unit WHERE code = 'OU-TST-NOPE'")
        assert cur.fetchone()[0] == 0


class _TwoCompanies:
    def execute(self, *_args):
        return None

    def fetchall(self):
        return [(1, 10), (2, 20)]


def test_reference_data_refuses_to_guess_a_company():
    with pytest.raises(RuntimeError, match=r"2 res.company rows"):
        _company(_TwoCompanies())
