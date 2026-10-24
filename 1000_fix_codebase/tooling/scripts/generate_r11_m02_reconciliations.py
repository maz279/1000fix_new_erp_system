#!/usr/bin/env python3
"""
generate_r11_m02_reconciliations.py — 48-Source Business Reconciliation Register (measured)
Milestone: R11-M02-T01 (Legacy decommissioning)
Standards: MIG-08, MG-004, MIG-02, RL-006 DCM-06, GV-001 §12.1

MIG-08: "Legacy systems decommissioned only after reconciliation sign-off — not on go-live day."
This tool produces the reconciliation register that sign-off reads; it never declares a
source reconciled or approved.

GV-009 — what is measured, and what cannot be:
- Per legacy source: LEGACY_SOURCES below is the DECLARED 48-source inventory (id, class,
  name, technology, target, custodian, required signatory). The real legacy system and its
  production extract are not on this workstation (DE-12: no production data on a
  workstation; DE-11: the local environment never reaches non-local endpoints), so each
  source's legacy-vs-migrated count reconciliation and its MG-004 business sign-off are
  UNMEASURED with that reason. No record count, variance, signatory or sign-off date is
  invented.
- Rehearsal reconciliation (MEASURED): the committed Wave-1 rehearsal extracts
  (migrations/extracts, synthetic) are recounted and re-hashed (LF-normalised sha256)
  against their control-totals manifest (MIG-02); the pipeline's loaded-counts report is
  reconciled against the manifest (accepted + quarantined = control; every quarantine must
  carry a reason); and, when the rehearsal database is reachable
  (migrations/target_db.py: fix_migration, never fix_dev), the accepted rows are recounted
  live by legacy reference with read-only SELECTs (DRIFT check). A quarantine needs a data
  steward's sign-off that cannot be observed -> UNMEASURED. The rehearsal proves the
  reconciliation machinery on synthetic data; it never counts as a legacy source's
  reconciliation.

Verdict: FAIL if any check failed, INCOMPLETE if any is UNMEASURED, else PASS.
Exit 0 PASS / 1 FAIL / 2 INCOMPLETE. Read-only: writes only the evidence JSON and its
Markdown record.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import os
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
EXTRACTS_DIR = REPO_ROOT / "migrations" / "extracts"
TARGET_DB_MODULE = REPO_ROOT / "migrations" / "target_db.py"
MANIFEST_NAME = "control-totals.json"
LOADED_NAME = "loaded-counts.json"
EVIDENCE_NAME = "r11-m02-legacy-48-reconciliations.json"
MD_NAME = "r11-m02-reconciliation-signoffs.md"

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

# Live-count sources (MIG-03): entity -> (table, legacy-key column). The same mapping as
# tooling/scripts/mig-totals.py LIVE_COUNT_SOURCES - fixed constants, never user input.
LIVE_COUNT_SOURCES: dict[str, tuple[str, str]] = {
    "branches": ("fix_branch", "legacy_reference"),
    "customers": ("res_partner", "legacy_reference"),
    "devices": ("fix_device", "legacy_reference"),
    "employees": ("hr_employee", "legacy_reference"),
    "attendance_opening": ("fix_attendance_record", "device_ref"),
}

SOURCE_UNMEASURED_REASON = (
    "the legacy source system and its production extract are not reachable from this "
    "workstation (DE-11 local-only endpoints; DE-12 no production data on a workstation) and "
    "no committed extract + control-totals manifest belongs to this source, so its legacy vs "
    "migrated counts cannot be measured here"
)
SIGNOFF_UNMEASURED_REASON = (
    "the MG-004 business sign-off is a human act by the required signatory; no signed "
    "sign-off is observable by this tool"
)
QUARANTINE_SIGNOFF_REASON = (
    "quarantined records await a data steward's disposition; that sign-off is a human act "
    "this tool cannot observe"
)

LEGACY_SOURCES = [
    # Class 1: Live Tracker DBs
    {
        "id": "SRC-01",
        "class": "1. Live Tracker",
        "name": "station.1000fix.com",
        "system": "MySQL 5.7",
        "target": "M01, P01",
        "custodian": "Lead Data Steward (Mohammad Ali)",
        "required_signatory": "Mohammad Ali (Data Steward) & Shafiul Alam (CTO)",
    },
    {
        "id": "SRC-02",
        "class": "1. Live Tracker",
        "name": "123.0.26.238/orderTracking",
        "system": "MS SQL Server 2014",
        "target": "M01, P01",
        "custodian": "Lead Data Steward (Mohammad Ali)",
        "required_signatory": "Mohammad Ali (Data Steward) & Shafiul Alam (CTO)",
    },
    # Class 2: Branch Service-Order Spreadsheets (SRC-03 to SRC-26)
    {
        "id": "SRC-03",
        "class": "2. Branch Sheet",
        "name": "Tejgaon Central Hub Orders",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Tariqul Islam (Central Hub Manager)",
    },
    {
        "id": "SRC-04",
        "class": "2. Branch Sheet",
        "name": "Dhanmondi Service Center",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Tanvir Ahmed (Dhanmondi Branch Lead)",
    },
    {
        "id": "SRC-05",
        "class": "2. Branch Sheet",
        "name": "Mirpur-10 Service Center",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Kamrul Hassan (Mirpur Branch Lead)",
    },
    {
        "id": "SRC-06",
        "class": "2. Branch Sheet",
        "name": "Uttara Sector-3 Center",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Mahmudur Rahman (Uttara Branch Lead)",
    },
    {
        "id": "SRC-07",
        "class": "2. Branch Sheet",
        "name": "Motijheel Commercial Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Farhana Yasmin (Motijheel Branch Lead)",
    },
    {
        "id": "SRC-08",
        "class": "2. Branch Sheet",
        "name": "Banani Luxury Care Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Zahid Hossain (Banani Branch Lead)",
    },
    {
        "id": "SRC-09",
        "class": "2. Branch Sheet",
        "name": "Chittagong Agrabad Center",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Nasir Uddin (Chittagong Regional Lead)",
    },
    {
        "id": "SRC-10",
        "class": "2. Branch Sheet",
        "name": "Chittagong GEC Circle Center",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Anisur Rahman (GEC Branch Lead)",
    },
    {
        "id": "SRC-11",
        "class": "2. Branch Sheet",
        "name": "Sylhet Zindabazar Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Jashim Uddin (Sylhet Branch Lead)",
    },
    {
        "id": "SRC-12",
        "class": "2. Branch Sheet",
        "name": "Rajshahi Alokar More Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Sabbir Hossain (Rajshahi Branch Lead)",
    },
    {
        "id": "SRC-13",
        "class": "2. Branch Sheet",
        "name": "Khulna KDA Avenue Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Abdur Razzak (Khulna Branch Lead)",
    },
    {
        "id": "SRC-14",
        "class": "2. Branch Sheet",
        "name": "Barisal Sadar Road Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Shahadat Hossain (Barisal Branch Lead)",
    },
    {
        "id": "SRC-15",
        "class": "2. Branch Sheet",
        "name": "Rangpur Station Road Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Mostafa Kamal (Rangpur Branch Lead)",
    },
    {
        "id": "SRC-16",
        "class": "2. Branch Sheet",
        "name": "Bogra Satmatha Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Ashraful Islam (Bogra Branch Lead)",
    },
    {
        "id": "SRC-17",
        "class": "2. Branch Sheet",
        "name": "Comilla Kandirpar Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Enamul Haque (Comilla Branch Lead)",
    },
    {
        "id": "SRC-18",
        "class": "2. Branch Sheet",
        "name": "Mymensingh Town Hall Branch",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Saiful Islam (Mymensingh Branch Lead)",
    },
    {
        "id": "SRC-19",
        "class": "2. Branch Sheet",
        "name": "Gazipur Chowrasta Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Abdul Mannan (Gazipur Point Lead)",
    },
    {
        "id": "SRC-20",
        "class": "2. Branch Sheet",
        "name": "Narayanganj Chasara Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Monirul Islam (Narayanganj Point Lead)",
    },
    {
        "id": "SRC-21",
        "class": "2. Branch Sheet",
        "name": "Savar Bus Stand Center",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Branch Operations Lead (Tariqul Islam)",
        "required_signatory": "Delwar Hossain (Savar Point Lead)",
    },
    {
        "id": "SRC-22",
        "class": "2. Branch Sheet",
        "name": "Jessore MK Road Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Habibur Rahman (Jessore Point Lead)",
    },
    {
        "id": "SRC-23",
        "class": "2. Branch Sheet",
        "name": "Kushtia NS Road Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Sharif Ahmed (Kushtia Point Lead)",
    },
    {
        "id": "SRC-24",
        "class": "2. Branch Sheet",
        "name": "Dinajpur Ganeshtola Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Nazrul Islam (Dinajpur Point Lead)",
    },
    {
        "id": "SRC-25",
        "class": "2. Branch Sheet",
        "name": "Feni Trunk Road Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Mizanur Rahman (Feni Point Lead)",
    },
    {
        "id": "SRC-26",
        "class": "2. Branch Sheet",
        "name": "Cox's Bazar Main Road Point",
        "system": "Excel / XLSX",
        "target": "M01 Kernel",
        "custodian": "Regional Operations Head (Nasir Uddin)",
        "required_signatory": "Shah Alam (Cox's Bazar Point Lead)",
    },
    # Class 3: Accounting History (SRC-27 to SRC-30)
    {
        "id": "SRC-27",
        "class": "3. Accounting",
        "name": "Tally ERP 9 Company File A",
        "system": "Tally XML / DB",
        "target": "M19, M55",
        "custodian": "Financial Controller (Mustafizur Rahman)",
        "required_signatory": "Mustafizur Rahman (Financial Controller)",
    },
    {
        "id": "SRC-28",
        "class": "3. Accounting",
        "name": "Tally ERP 9 Company File B",
        "system": "Tally XML / DB",
        "target": "M19, M55",
        "custodian": "Financial Controller (Mustafizur Rahman)",
        "required_signatory": "Mustafizur Rahman (Financial Controller)",
    },
    {
        "id": "SRC-29",
        "class": "3. Accounting",
        "name": "Branch Cash Book Spreadsheets",
        "system": "Excel / CSV",
        "target": "M59, M60",
        "custodian": "Financial Controller (Mustafizur Rahman)",
        "required_signatory": "Mohammad Harun (Chief Treasury Officer)",
    },
    {
        "id": "SRC-30",
        "class": "3. Accounting",
        "name": "Corporate Invoicing Register",
        "system": "Excel / XLSX",
        "target": "M19, M36",
        "custodian": "Corporate Billing Manager (Arifur Rahman)",
        "required_signatory": "Arifur Rahman (Corporate Billing Lead)",
    },
    # Class 4: HR & Payroll (SRC-31 to SRC-34)
    {
        "id": "SRC-31",
        "class": "4. HR & Payroll",
        "name": "Staff Master Register",
        "system": "Excel / XLSX",
        "target": "M21 Core",
        "custodian": "Head of Human Resources (Nasreen Sultana)",
        "required_signatory": "Nasreen Sultana (Head of HR)",
    },
    {
        "id": "SRC-32",
        "class": "4. HR & Payroll",
        "name": "Monthly Payroll Sheets 2025-26",
        "system": "Excel / XLSX",
        "target": "M22 Payroll",
        "custodian": "Payroll Manager (Kazi Touhid)",
        "required_signatory": "Kazi Touhid (Payroll Lead)",
    },
    {
        "id": "SRC-33",
        "class": "4. HR & Payroll",
        "name": "Technician Commission Logs",
        "system": "Excel / CSV",
        "target": "M22 Payroll",
        "custodian": "Payroll Manager (Kazi Touhid)",
        "required_signatory": "Kazi Touhid (Payroll Lead)",
    },
    {
        "id": "SRC-34",
        "class": "4. HR & Payroll",
        "name": "Statutory Tax Deduction Sheets",
        "system": "Excel / XLSX",
        "target": "M51 Tax",
        "custodian": "Tax Compliance Lead (Rezaul Karim)",
        "required_signatory": "Rezaul Karim (Tax Compliance Lead)",
    },
    # Class 5: WordPress CMS (SRC-35, SRC-36)
    {
        "id": "SRC-35",
        "class": "5. WordPress CMS",
        "name": "WordPress Portal Database",
        "system": "MySQL 8.0",
        "target": "Portal CMS",
        "custodian": "Marketing & Content Lead (Shumona Akter)",
        "required_signatory": "Shumona Akter (Marketing Head)",
    },
    {
        "id": "SRC-36",
        "class": "5. WordPress CMS",
        "name": "Media Uploads Repository",
        "system": "WP Media / S3",
        "target": "Ceph Store",
        "custodian": "Content Administrator (Tanvir Mahmud)",
        "required_signatory": "Tanvir Mahmud (Media Custodian)",
    },
    # Class 6: Inventory & Asset Registers (SRC-37 to SRC-40)
    {
        "id": "SRC-37",
        "class": "6. Inventory",
        "name": "Central Warehouse SKU Catalog",
        "system": "Excel / CSV",
        "target": "M15, M37",
        "custodian": "Warehouse Operations Lead (Mahbub Alam)",
        "required_signatory": "Mahbub Alam (Warehouse Manager)",
    },
    {
        "id": "SRC-38",
        "class": "6. Inventory",
        "name": "Branch Spare Parts Stock Count",
        "system": "Excel / XLSX",
        "target": "M15 Inventory",
        "custodian": "Warehouse Operations Lead (Mahbub Alam)",
        "required_signatory": "Mahbub Alam (Warehouse Manager)",
    },
    {
        "id": "SRC-39",
        "class": "6. Inventory",
        "name": "Supplier Part Number Crosswalk",
        "system": "Excel / CSV",
        "target": "M39 Vendor",
        "custodian": "Procurement Lead (Selim Reza)",
        "required_signatory": "Selim Reza (Head of Procurement)",
    },
    {
        "id": "SRC-40",
        "class": "6. Inventory",
        "name": "Damaged / Scrapped Parts Log",
        "system": "Excel / XLSX",
        "target": "M50 E-Waste",
        "custodian": "E-Waste Compliance Officer (Tareq Hasan)",
        "required_signatory": "Tareq Hasan (E-Waste Compliance Lead)",
    },
    # Class 7: Contacts & Warranty (SRC-41 to SRC-44)
    {
        "id": "SRC-41",
        "class": "7. Contacts",
        "name": "Corporate Client Contact List",
        "system": "Excel / CSV",
        "target": "M09, M33",
        "custodian": "B2B Accounts Lead (Fahim Chowdhury)",
        "required_signatory": "Fahim Chowdhury (B2B Accounts Director)",
    },
    {
        "id": "SRC-42",
        "class": "7. Contacts",
        "name": "Retail SMS Gateway Delivery Log",
        "system": "SQL / CSV",
        "target": "M26, M33",
        "custodian": "Customer Communications Lead (Farzana Haque)",
        "required_signatory": "Farzana Haque (Customer Service Head)",
    },
    {
        "id": "SRC-43",
        "class": "7. Contacts",
        "name": "Warranty Card Registration Store",
        "system": "MySQL 5.6",
        "target": "M05, M17",
        "custodian": "Warranty Operations Lead (Imtiaz Ahmed)",
        "required_signatory": "Imtiaz Ahmed (Warranty Operations Lead)",
    },
    {
        "id": "SRC-44",
        "class": "7. Contacts",
        "name": "Customer Inbound Feedback Log",
        "system": "Excel / XLSX",
        "target": "M34 CSAT",
        "custodian": "Quality Assurance Manager (Zubair Hossain)",
        "required_signatory": "Zubair Hossain (QA Manager)",
    },
    # Class 8: Misc Documents & Evidence (SRC-45 to SRC-48)
    {
        "id": "SRC-45",
        "class": "8. Misc Records",
        "name": "Brand RMA Authorisation Forms",
        "system": "PDF / Scans",
        "target": "M05 Warranty",
        "custodian": "Brand Relations Manager (Kamrul Islam)",
        "required_signatory": "Kamrul Islam (Brand Relations Lead)",
    },
    {
        "id": "SRC-46",
        "class": "8. Misc Records",
        "name": "Workshop Machine Calibration Logs",
        "system": "Excel / XLSX",
        "target": "M62 Tools",
        "custodian": "Technical Services Supervisor (Shahin Alam)",
        "required_signatory": "Shahin Alam (Technical Services Supervisor)",
    },
    {
        "id": "SRC-47",
        "class": "8. Misc Records",
        "name": "Branch Fixed Assets Register",
        "system": "Excel / XLSX",
        "target": "M56 Assets",
        "custodian": "Fixed Assets Accountant (Jamil Ahmed)",
        "required_signatory": "Jamil Ahmed (Fixed Assets Accountant)",
    },
    {
        "id": "SRC-48",
        "class": "8. Misc Records",
        "name": "Environmental Disposal Certificates",
        "system": "PDF / Scans",
        "target": "M50 E-Waste",
        "custodian": "E-Waste Compliance Officer (Tareq Hasan)",
        "required_signatory": "Tareq Hasan (E-Waste Compliance Lead)",
    },
]


def derive_verdict(statuses: list[str]) -> str:
    """FAIL if any check failed, INCOMPLETE if any is not PASS, else PASS."""
    if not statuses:
        return INCOMPLETE
    if FAIL in statuses:
        return FAIL
    if any(s != PASS for s in statuses):
        return INCOMPLETE
    return PASS


def exit_code_for(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def _check(status: str, detail: str) -> dict[str, str]:
    return {"status": status, "detail": detail}


def compute_sha256(path: Path) -> str:
    """sha256 over LF-normalised bytes - the method migrations/extracts_generator.py records."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _read_json(path: Path) -> tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"{path.name} not found"
    except (OSError, ValueError) as exc:
        return None, f"{path.name} unreadable: {exc}"


def _records(payload: Any) -> list | None:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("records", "lines", "rows"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return None


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _pct(part: float, whole: float) -> float | None:
    return round(part / whole * 100.0, 2) if whole else None


def open_rehearsal_db(dsn: str | None = None):
    """Read-only connection to the rehearsal target -> (conn, 'host:port/db').

    Resolution and the DE-12 refusals (never fix_dev) are migrations/target_db.py's; the
    session is set read-only, so no statement of this tool can write.
    """
    os.environ.setdefault("PGCONNECT_TIMEOUT", "5")
    spec = importlib.util.spec_from_file_location("r11_m02_t01_target_db", TARGET_DB_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    conn = module.connect(dsn)
    conn.set_session(readonly=True, autocommit=True)
    return conn, module.describe(module.resolve_dsn(dsn))


def count_live(conn, entity: str, refs: list[str]) -> int:
    """Rows on the target carrying one of the extract's legacy references (read-only)."""
    table, column = LIVE_COUNT_SOURCES[entity]
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {table} WHERE {column} = ANY(%s)", (refs,))
        return int(cur.fetchone()[0])


def source_entry(src: dict[str, str]) -> dict[str, Any]:
    """One declared legacy source: nothing about it is measurable from this workstation."""
    return {
        "source_id": src["id"],
        "functional_class": src["class"],
        "source_name": src["name"],
        "source_technology": src["system"],
        "target_module": src["target"],
        "designated_custodian": src["custodian"],
        "required_signatory": src["required_signatory"],
        "legacy_record_count": None,
        "migrated_record_count": None,
        "unreconciled_delta": None,
        "variance_percentage": None,
        "reconciliation_status": UNMEASURED,
        "reconciliation_reason": SOURCE_UNMEASURED_REASON,
        "approval_status": UNMEASURED,
        "approval_reason": SIGNOFF_UNMEASURED_REASON,
        "governing_standard": "MIG-08 / MG-004 / RL-006 DCM-06",
    }


def reconcile_entity(
    entity: str,
    control: Any,
    manifest: dict,
    loaded: dict | None,
    extracts_dir: Path,
    live: Callable[[str, list[str]], int] | None,
    live_reason: str,
) -> dict[str, Any]:
    """MIG-02 / MG-004 reconciliation of one rehearsal entity, every figure measured here."""
    checks: dict[str, dict[str, str]] = {}
    fname = (manifest.get("extract_files") or {}).get(entity)
    expected_sum = (manifest.get("checksums") or {}).get(entity)
    records: list | None = None
    actual_sum: str | None = None

    if not fname:
        checks["extract_count"] = _check(FAIL, "the manifest names no extract file")
        checks["extract_checksum"] = _check(FAIL, "the manifest names no extract file")
    else:
        path = extracts_dir / fname
        payload, err = _read_json(path)
        records = None if err else _records(payload)
        if err or records is None:
            checks["extract_count"] = _check(FAIL, err or f"{fname} holds no record list")
        else:
            ok = _is_int(control) and len(records) == control
            checks["extract_count"] = _check(
                PASS if ok else FAIL, f"{fname}: {len(records)} records, control total {control}"
            )
        if not path.is_file():
            checks["extract_checksum"] = _check(FAIL, f"{fname} not found")
        else:
            actual_sum = compute_sha256(path)
            if not expected_sum:
                checks["extract_checksum"] = _check(FAIL, "the manifest carries no checksum")
            else:
                checks["extract_checksum"] = _check(
                    PASS if actual_sum == expected_sum else FAIL,
                    "extract sha256 matches the manifest"
                    if actual_sum == expected_sum
                    else f"extract sha256 {actual_sum[:12]}... != manifest {expected_sum[:12]}...",
                )

    loaded_total = accepted = quarantined = None
    if loaded is None:
        for key in ("load_accounted", "quarantine_explained", "quarantine_signoff"):
            checks[key] = _check(UNMEASURED, f"no {LOADED_NAME} load report to reconcile")
    else:
        loaded_total = (loaded.get("loaded_totals") or {}).get(entity)
        accepted = (loaded.get("accepted_records") or {}).get(entity)
        quarantined = (loaded.get("quarantined_records") or {}).get(entity)
        ints = all(_is_int(v) for v in (control, loaded_total, accepted, quarantined))
        ok = ints and loaded_total == control and accepted + quarantined == control
        checks["load_accounted"] = _check(
            PASS if ok else FAIL,
            f"control={control} loaded={loaded_total} accepted={accepted} "
            f"quarantined={quarantined}",
        )
        rejections = (loaded.get("rejections") or {}).get(entity) or []
        if not _is_int(quarantined):
            checks["quarantine_explained"] = _check(FAIL, "no quarantine count reported")
            checks["quarantine_signoff"] = _check(FAIL, "no quarantine count reported")
        elif quarantined == 0:
            checks["quarantine_explained"] = _check(PASS, "no quarantined records")
            checks["quarantine_signoff"] = _check(PASS, "no quarantined records to dispose")
        else:
            reasoned = sum(
                1 for r in rejections if isinstance(r, dict) and str(r.get("reason") or "").strip()
            )
            explained = len(rejections) == quarantined and reasoned == quarantined
            checks["quarantine_explained"] = _check(
                PASS if explained else FAIL,
                f"{reasoned} of {quarantined} quarantined records carry a reason "
                f"({len(rejections)} listed)",
            )
            checks["quarantine_signoff"] = _check(UNMEASURED, QUARANTINE_SIGNOFF_REASON)

    live_accepted = None
    if live is None:
        checks["live_drift"] = _check(UNMEASURED, live_reason)
    elif entity not in LIVE_COUNT_SOURCES:
        checks["live_drift"] = _check(UNMEASURED, f"no live-count source mapped for {entity!r}")
    elif records is None:
        checks["live_drift"] = _check(FAIL, "no extract records to look up")
    elif not _is_int(accepted):
        checks["live_drift"] = _check(UNMEASURED, "no accepted count reported to compare")
    else:
        refs = sorted({str(r["legacy_reference"]) for r in records if r.get("legacy_reference")})
        try:
            live_accepted = live(entity, refs)
        except Exception as exc:  # a failed query is a failed check, not an aborted run
            checks["live_drift"] = _check(FAIL, f"live count query failed: {exc}")
        else:
            checks["live_drift"] = _check(
                PASS if live_accepted == accepted else FAIL,
                f"target rows by legacy reference={live_accepted}, load report accepted={accepted}"
                + ("" if live_accepted == accepted else " [DRIFT]"),
            )

    delta = (
        control - (accepted + quarantined)
        if all(_is_int(v) for v in (control, accepted, quarantined))
        else None
    )
    return {
        "entity": entity,
        "extract_file": fname,
        "control_total": control,
        "extract_records": None if records is None else len(records),
        "manifest_checksum": expected_sum,
        "measured_checksum": actual_sum,
        "loaded_total": loaded_total,
        "accepted_records": accepted,
        "quarantined_records": quarantined,
        "live_accepted_records": live_accepted,
        "unaccounted_delta": delta,
        "variance_percentage": None if delta is None else _pct(abs(delta), control),
        "quarantine_percentage": _pct(quarantined, control)
        if _is_int(quarantined) and _is_int(control)
        else None,
        "checks": checks,
        "status": derive_verdict([c["status"] for c in checks.values()]),
    }


def measure_rehearsal(extracts_dir: Path, connector: Callable[[], tuple]) -> dict[str, Any]:
    """Reconcile the committed rehearsal extracts, load report and (if reachable) database."""
    manifest_path = extracts_dir / MANIFEST_NAME
    manifest, err = _read_json(manifest_path)
    base: dict[str, Any] = {
        "scope": "Wave-1 rehearsal on SYNTHETIC extracts (DE-12) - proves the reconciliation "
        "machinery; it is not a legacy source's reconciliation",
        "manifest": str(manifest_path.relative_to(REPO_ROOT))
        if manifest_path.is_relative_to(REPO_ROOT)
        else str(manifest_path),
    }
    if err:
        status = UNMEASURED if "not found" in err else FAIL
        base.update(
            checks={"manifest": _check(status, err)}, entities=[], status=derive_verdict([status])
        )
        return base
    control_totals = manifest.get("control_totals") if isinstance(manifest, dict) else None
    if not isinstance(control_totals, dict) or not control_totals:
        base.update(
            checks={"manifest": _check(FAIL, "manifest carries no control_totals")},
            entities=[],
            status=FAIL,
        )
        return base

    checks: dict[str, dict[str, str]] = {"manifest": _check(PASS, f"{MANIFEST_NAME} read")}
    loaded, lerr = _read_json(extracts_dir / LOADED_NAME)
    if lerr:
        loaded = None
        checks["load_report"] = _check(UNMEASURED if "not found" in lerr else FAIL, lerr)
    elif not isinstance(loaded, dict):
        loaded = None
        checks["load_report"] = _check(FAIL, f"{LOADED_NAME} is not an object")
    else:
        same_run = loaded.get("run") == manifest.get("run")
        checks["load_report"] = _check(
            PASS if same_run else FAIL,
            f"load report run {loaded.get('run')!r} vs manifest run {manifest.get('run')!r}",
        )

    conn = None
    target = None
    live: Callable[[str, list[str]], int] | None = None
    live_reason = ""
    try:
        conn, target = connector()
    except Exception as exc:  # unreachable infrastructure is UNMEASURED, never PASS
        live_reason = f"rehearsal database unreachable: {exc}".strip()
    else:
        live = functools.partial(count_live, conn)
    try:
        entities = [
            reconcile_entity(entity, control, manifest, loaded, extracts_dir, live, live_reason)
            for entity, control in sorted(control_totals.items())
        ]
    finally:
        if conn is not None:
            conn.close()

    total_control = sum(e["control_total"] for e in entities if _is_int(e["control_total"]))
    deltas = [e["unaccounted_delta"] for e in entities]
    variance = (
        f"{sum(abs(d) for d in deltas) / total_control * 100:.2f}%"
        if total_control and all(_is_int(d) for d in deltas)
        else None
    )
    statuses = [c["status"] for c in checks.values()] + [e["status"] for e in entities]
    base.update(
        run=manifest.get("run"),
        target_database=target,
        checks=checks,
        total_control_records=total_control,
        total_accepted_records=sum(
            e["accepted_records"] for e in entities if _is_int(e["accepted_records"])
        ),
        total_quarantined_records=sum(
            e["quarantined_records"] for e in entities if _is_int(e["quarantined_records"])
        ),
        unaccounted_variance_rate=variance,
        entities=entities,
        status=derive_verdict(statuses),
    )
    return base


def build_evidence(
    extracts_dir: Path | None = None,
    connector: Callable[[], tuple] | None = None,
) -> dict[str, Any]:
    sources = [source_entry(src) for src in LEGACY_SOURCES]
    rehearsal = measure_rehearsal(extracts_dir or EXTRACTS_DIR, connector or open_rehearsal_db)
    statuses = [s["reconciliation_status"] for s in sources]
    statuses += [s["approval_status"] for s in sources]
    statuses.append(rehearsal["status"])
    verdict = derive_verdict(statuses)
    measured = [s for s in sources if s["reconciliation_status"] in (PASS, FAIL)]
    return {
        "milestone": "R11-M02",
        "task": "R11-M02-T01",
        "title": "Legacy 48-Source MG-004 Business Reconciliation Register",
        "execution_timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "governing_standards": ["MIG-08", "MG-004", "MIG-02", "RL-006 DCM-06", "GV-001 §12.1"],
        "measurement_policy": "GV-009: every status is measured in this run; what cannot be "
        "observed from this workstation is UNMEASURED with its reason",
        "total_sources_in_register": len(sources),
        "total_sources_evaluated": len(measured),
        "total_sources_reconciled": sum(1 for s in sources if s["reconciliation_status"] == PASS),
        "total_sources_approved": sum(1 for s in sources if s["approval_status"] == PASS),
        "total_sources_unmeasured": sum(
            1 for s in sources if s["reconciliation_status"] == UNMEASURED
        ),
        "total_records_profiled_and_reconciled": None,
        "estate_variance_rate": None,
        "estate_variance_reason": "no legacy source's counts were measured in this run",
        "rehearsal_reconciliation": rehearsal,
        "verdict": verdict,
        "overall_status": verdict,
        "sources": sources,
    }


def _md_cell(value: Any) -> str:
    return "n/a" if value is None else str(value).replace("|", "/")


def render_markdown(ev: dict[str, Any]) -> str:
    reh = ev["rehearsal_reconciliation"]
    out = [
        "# Legacy 48-Source Business Reconciliation Register (MIG-08 / MG-004)",
        "",
        "## Task R11-M02-T01 Verification & Audit Record",
        "",
        f"- **Execution Timestamp**: {ev['execution_timestamp']}",
        f"- **Verdict (computed)**: `{ev['verdict']}`",
        f"- **Sources in register**: {ev['total_sources_in_register']}",
        f"- **Sources reconciled (measured)**: {ev['total_sources_reconciled']} / "
        f"{ev['total_sources_in_register']}",
        f"- **Sources with an observed MG-004 sign-off**: {ev['total_sources_approved']} / "
        f"{ev['total_sources_in_register']}",
        f"- **Sources UNMEASURED**: {ev['total_sources_unmeasured']}",
        "- **Binding Standard**: `MIG-08` (*Legacy systems decommissioned only after "
        "reconciliation sign-off*)",
        "",
        "Measurement policy (GV-009): a legacy source's counts and its business sign-off are "
        "not observable from a workstation (DE-11 / DE-12); each is reported `UNMEASURED` "
        "with its reason, never as reconciled or approved.",
        "",
        "---",
        "",
        "### Rehearsal reconciliation (measured, synthetic extracts)",
        "",
        f"- **Run**: `{_md_cell(reh.get('run'))}` — status `{reh['status']}`",
        f"- **Target database**: {_md_cell(reh.get('target_database'))}",
        f"- **Unaccounted variance**: {_md_cell(reh.get('unaccounted_variance_rate'))}",
        "",
        "| Entity | Control | Extract | Accepted | Quarantined | Live (target) | Delta | Status |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for e in reh.get("entities", []):
        out.append(
            f"| `{e['entity']}` | {_md_cell(e['control_total'])} | {_md_cell(e['extract_records'])} "
            f"| {_md_cell(e['accepted_records'])} | {_md_cell(e['quarantined_records'])} "
            f"| {_md_cell(e['live_accepted_records'])} | {_md_cell(e['unaccounted_delta'])} "
            f"| `{e['status']}` |"
        )
    problems = [
        f"- `{e['entity']}.{name}` — {c['status']}: {c['detail']}"
        for e in reh.get("entities", [])
        for name, c in e["checks"].items()
        if c["status"] != PASS
    ] + [
        f"- `{name}` — {c['status']}: {c['detail']}"
        for name, c in reh.get("checks", {}).items()
        if c["status"] != PASS
    ]
    if problems:
        out += ["", "Checks not passed:", "", *problems]
    out += [
        "",
        "---",
        "",
        "### 48-Source Reconciliation Register",
        "",
        "| Source ID | Class | Source Name | Target | Reconciliation | Sign-off | Required signatory |",
        "|---|---|---|---|:---:|:---:|---|",
    ]
    for s in ev["sources"]:
        out.append(
            f"| **{s['source_id']}** | {_md_cell(s['functional_class'])} "
            f"| {_md_cell(s['source_name'])} | {_md_cell(s['target_module'])} "
            f"| `{s['reconciliation_status']}` | `{s['approval_status']}` "
            f"| {_md_cell(s['required_signatory'])} |"
        )
    out += ["", f"UNMEASURED reconciliation: {SOURCE_UNMEASURED_REASON}.", ""]
    out += [f"UNMEASURED sign-off: {SIGNOFF_UNMEASURED_REASON}.", ""]
    if ev["verdict"] == PASS:
        out += ["Every reconciliation check and sign-off above was measured as passed.", ""]
    else:
        out += [
            f"No source is approved for decommission by this record (verdict `{ev['verdict']}`).",
            "",
        ]
    return "\n".join(out)


def write_outputs(ev: dict[str, Any]) -> tuple[Path, Path]:
    evidence_dir, docs_dir = Path(EVIDENCE_DIR), Path(DOCS_DIR)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / EVIDENCE_NAME
    md_path = docs_dir / MD_NAME
    json_path.write_bytes((json.dumps(ev, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    md_path.write_bytes(render_markdown(ev).encode("utf-8"))
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="R11-M02-T01 reconciliation register (measured)")
    ap.add_argument("--dsn", help="rehearsal database DSN (default: migrations/target_db.py)")
    ap.add_argument("--extracts-dir", type=Path, default=None, help="rehearsal extracts dir")
    args = ap.parse_args(argv)
    ev = build_evidence(args.extracts_dir, lambda: open_rehearsal_db(args.dsn))
    json_path, md_path = write_outputs(ev)
    reh = ev["rehearsal_reconciliation"]
    print(
        f"R11-M02-T01: {ev['total_sources_reconciled']}/{ev['total_sources_in_register']} sources "
        f"reconciled, {ev['total_sources_unmeasured']} UNMEASURED; rehearsal {reh['status']}"
    )
    print(f"Verdict: {ev['verdict']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    return exit_code_for(ev["verdict"])


if __name__ == "__main__":
    sys.exit(main())
