#!/usr/bin/env python3
"""migrations/load_attendance_opening.py — ETL for Attendance Opening Balances.

Specification: R06-M02-T05 / P08-M02-T07.
Standing Ruling: TSS 19.1 / P01-M07-T06 Non-migration ruling:
  - Historical punch card transactions / closed attendance books are NOT migrated.
  - Only active opening balances from sign-in books (present days, leave days, OT hours) are migrated.
Target models: fix.attendance.record / opening attendance balances.
Legacy reference: LEG:SIGNIN_BOOK:<branch_code>:<employee_code> (stored in device_ref)
Pipeline stage 5 (after ETL-4 employees) in migrations/pipeline.py.

GV-009: without a target connection the migrator only VALIDATES (mode "dry_run"):
it reports how many records are eligible, never that anything was accepted/loaded.
An opening balance is stored as the sign-in book states it: check_in is the first
day of its opening_period, overtime is the book's figure, and present/leave days
are kept verbatim in statutory_notes - no hours are invented from day counts.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

MIGRATIONS_DIR = Path(__file__).resolve().parent
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"
EXTRACT_FILE = EXTRACTS_DIR / "attendance_opening_extract.json"
# Opening-balance rows carry their legacy reference in device_ref (MIG-03): it is the
# idempotency key of a re-run and the MG-007 rollback key (LEG:SIGNIN_BOOK:%).
LEGACY_PREFIX = "LEG:SIGNIN_BOOK:"


def generate_attendance_opening_extract() -> Path:
    """Returns path to verified attendance opening extract."""
    if not EXTRACT_FILE.exists():
        raise FileNotFoundError(f"Extract file missing at {EXTRACT_FILE}")
    return EXTRACT_FILE


class AttendanceOpeningMigrator:
    """Migrator for attendance sign-in book opening balances adhering to TSS 19.1.

    Control totals are produced at EXTRACT time (migrations/extracts_generator.py) and
    the loaded counts are emitted by the pipeline (migrations/pipeline.py) from the
    stats returned here - this class never rewrites control-totals.json or
    loaded-counts.json (that made the control total circular and was lost whenever the
    pipeline re-emitted loaded-counts.json: attendance_opening loaded=None).
    """

    def __init__(self, extract_path: Path | None = None):
        self.extract_path = extract_path or EXTRACT_FILE

    def run_migration(self, extract_file: Path | None = None, db_conn=None) -> dict[str, Any]:
        target_path = extract_file or self.extract_path
        if not target_path.exists():
            raise FileNotFoundError(f"Extract not found: {target_path}")

        data = json.loads(target_path.read_text(encoding="utf-8"))
        total_extracted = len(data)
        processed = 0
        accepted = 0
        dry_run = db_conn is None
        skipped_historical = 0
        unresolved = 0
        rejections = []

        for record in data:
            legacy_ref = record.get("legacy_reference", "")
            is_historical = record.get("is_historical", False)
            status = record.get("status", "active")

            # TSS 19.1 / P01-M07-T06 Non-migration ruling enforcement:
            # Historical punch cards / closed logs are ruled out from migration.
            if is_historical or status != "active":
                skipped_historical += 1
                rejections.append(
                    {
                        "legacy_reference": legacy_ref,
                        "reason": "TSS 19.1 Non-migration ruling: closed historical attendance records excluded from cutover",
                    }
                )
                continue

            processed += 1

            # Ingest / record opening balance (validation only when no target is given)
            if dry_run:
                continue
            with db_conn.cursor() as cur:
                cur.execute("SAVEPOINT attendance_sp;")
                try:
                    error = self._load_opening_balance(db_conn, record)
                    cur.execute("RELEASE SAVEPOINT attendance_sp;")
                except Exception as e:
                    cur.execute("ROLLBACK TO SAVEPOINT attendance_sp;")
                    error = f"load error: {e}"
            if error:
                unresolved += 1
                rejections.append({"legacy_reference": legacy_ref, "reason": error})
                continue
            accepted += 1

        if not dry_run:
            db_conn.commit()

        # every extracted record dispositioned - only meaningful when something was loaded
        reconciled = (
            None
            if dry_run
            else (total_extracted == accepted + skipped_historical + unresolved)
            and (processed == accepted + unresolved)
        )

        return {
            "entity": "attendance_opening",
            "mode": "dry_run" if dry_run else "load",
            "total_extracted": total_extracted,
            "validated": processed,
            "processed": processed,
            "accepted": accepted,
            "skipped_historical": skipped_historical,
            "unresolved": unresolved,
            "reconciled": reconciled,
            "rejections": rejections,
            # pipeline loader contract (same keys as load_branches/... results)
            "total_records": total_extracted,
            "loaded_count": accepted,
            "rejected_count": skipped_historical + unresolved,
        }

    @staticmethod
    def _load_opening_balance(db_conn, record: dict[str, Any]) -> str | None:
        """Insert one opening balance; return a quarantine reason, or None when loaded."""
        legacy_ref = record.get("legacy_reference", "")
        emp_code = record.get("employee_code", "")
        with db_conn.cursor() as cur:
            # Exact employee key only - a name match would post balances to a
            # different person who merely shares the name.
            cur.execute(
                "SELECT id, company_id, operating_unit_id FROM hr_employee "
                "WHERE employee_code = %s LIMIT 1;",
                (emp_code,),
            )
            emp_row = cur.fetchone()
            if not emp_row:
                return (
                    f"employee {emp_code!r} not found on target (hr_employee.employee_code) "
                    "- opening balance quarantined for HR steward review"
                )
            emp_id, company_id, ou_id = emp_row
            period = str(record.get("opening_period") or "")
            try:
                check_in = datetime.strptime(period, "%Y-%m")
            except ValueError:
                return (
                    f"opening_period {period!r} is not YYYY-MM - quarantined for HR steward review"
                )
            cur.execute(
                "SELECT id FROM fix_attendance_record WHERE employee_id = %s AND device_ref = %s;",
                (emp_id, legacy_ref),
            )
            if cur.fetchone():
                return None  # idempotent re-run
            cur.execute(
                """
                INSERT INTO fix_attendance_record
                (employee_id, check_in, source, device_ref, overtime_hours, statutory_notes,
                 company_id, operating_unit_id, create_date, write_date)
                VALUES (%s, %s, 'manual', %s, %s, %s, %s, %s, NOW(), NOW());
                """,
                (
                    emp_id,
                    check_in,
                    legacy_ref,
                    record.get("opening_overtime_hours"),
                    f"Opening balance {period} (sign-in book): present_days="
                    f"{record.get('present_days')}, leave_days={record.get('leave_days')}",
                    company_id,
                    ou_id,
                ),
            )
        return None


if __name__ == "__main__":
    migrator = AttendanceOpeningMigrator()
    result = migrator.run_migration()
    print(json.dumps(result, indent=2))
