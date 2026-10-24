#!/usr/bin/env python3
"""migrations/rollback.py — MG-007 Rollback Engine for the rehearsal loads.

Specification: docs/p04/migration-mig-standards.md (MIG-07, DoD-16).
Rehearses idempotent rollback by legacy_reference and erases Z4 classified keys.
Covers the Wave-1 pipeline (attendance, devices, employees, parties, branches) and
the ETL-5 inventory baseline (migrations/load_inventory.py: LEG:SRC37 / LEG:SRC38).
Target: the dedicated rehearsal database `fix_migration` (never fix_dev, DE-12);
--dsn / DATABASE_URL / PG* override (migrations/target_db.py). ETL-0 reference
data (entity, operating units, brands/models) and the MD-* register are kept:
they are prerequisites, not migrated records.

GV-009: "returned to baseline" is only reported when a read-back after the deletes
finds no migrated row left and every Z4 key was erased; otherwise the run reports
INCOMPLETE (exit 1) with what remains.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from libs.py.fix_residency import get_client as get_residency_client  # noqa: E402 - path bootstrap
from migrations.target_db import connect  # noqa: E402 - path bootstrap

logger = logging.getLogger(__name__)

# party legacy pattern -> Z4 key namespace used by the loader that stored it
Z4_NAMESPACES = {
    "CUST:WP_STORE:%": "party identity",
    "PARTNER:EMP:PAYROLL_2026:%": "employee identity",
}

# (table, legacy column, LIKE pattern): every migrated row the rollback must remove;
# read back after the deletes to prove the baseline.
RESIDUAL_CHECKS = (
    ("fix_inventory_valuation_suspense", "legacy_reference", "LEG:SRC38:%"),
    ("fix_stock_location", "legacy_reference", "LEG:SRC38:%"),
    ("fix_spare_part", "legacy_reference", "LEG:SRC37:%"),
    ("fix_attendance_record", "device_ref", "LEG:SIGNIN_BOOK:%"),
    ("fix_device", "legacy_reference", "DEV:ASSET_SHEET:%"),
    ("hr_employee", "legacy_reference", "EMP:PAYROLL_2026:%"),
    ("res_partner", "legacy_reference", "CUST:WP_STORE:%"),
    ("res_partner", "legacy_reference", "PARTNER:EMP:PAYROLL_2026:%"),
    ("fix_branch", "legacy_reference", "BR:PILOT_2026:%"),
)


def get_db_connection(dsn: str | None = None):
    return connect(dsn)


def residual_rows(cur) -> dict[str, int]:
    """Migrated rows still present, per table/pattern (only the non-zero ones)."""
    left: dict[str, int] = {}
    for table, column, pattern in RESIDUAL_CHECKS:
        # identifiers are module constants above, never input
        cur.execute(f"SELECT count(*) FROM {table} WHERE {column} LIKE %s;", (pattern,))  # noqa: S608
        count = cur.fetchone()[0]
        if count:
            left[f"{table}:{pattern}"] = count
    return left


def execute_rollback(dsn: str | None = None) -> dict:
    print("=" * 70)
    print("Executing MG-007 Migration Rollback (MIG-07 Rehearsal)")
    print("=" * 70)

    conn = get_db_connection(dsn)
    residency = get_residency_client()
    stats: dict = {}

    try:
        with conn.cursor() as cur:
            # 0. ETL-5 inventory baseline (suspense -> locations -> parts: FK RESTRICT order;
            # locations reference van custodians in hr_employee, so before the employees)
            print("[0/5] Rolling back the inventory baseline (LEG:SRC38:% / LEG:SRC37:%)...")
            cur.execute(
                "DELETE FROM fix_inventory_valuation_suspense WHERE legacy_reference LIKE 'LEG:SRC38:%';"
            )
            stats["inventory_suspense_deleted"] = cur.rowcount
            cur.execute("DELETE FROM fix_stock_location WHERE legacy_reference LIKE 'LEG:SRC38:%';")
            stats["inventory_locations_deleted"] = cur.rowcount
            cur.execute("DELETE FROM fix_spare_part WHERE legacy_reference LIKE 'LEG:SRC37:%';")
            stats["inventory_parts_deleted"] = cur.rowcount
            print(
                f"  -> Deleted {stats['inventory_suspense_deleted']} suspense rows, "
                f"{stats['inventory_locations_deleted']} locations, "
                f"{stats['inventory_parts_deleted']} parts."
            )

            # 1. Rollback attendance opening balances (FK RESTRICT on hr_employee)
            print("[1/5] Rolling back attendance opening balances (LEG:SIGNIN_BOOK:%)...")
            cur.execute(
                "DELETE FROM fix_attendance_record WHERE device_ref LIKE 'LEG:SIGNIN_BOOK:%';"
            )
            stats["attendance_opening_deleted"] = cur.rowcount
            print(f"  -> Deleted {stats['attendance_opening_deleted']} opening balance records.")

            # 2. Rollback Devices
            print("[2/5] Rolling back migrated devices (DEV:ASSET_SHEET:%)...")
            cur.execute("""
                DELETE FROM fix_warranty
                WHERE device_id IN (
                    SELECT id FROM fix_device WHERE legacy_reference LIKE 'DEV:ASSET_SHEET:%'
                );
            """)
            cur.execute("DELETE FROM fix_device WHERE legacy_reference LIKE 'DEV:ASSET_SHEET:%';")
            stats["devices_deleted"] = cur.rowcount
            print(f"  -> Deleted {stats['devices_deleted']} migrated device records.")

            # 3. Rollback Employees (and the resource.resource rows the loader created)
            print("[3/5] Rolling back migrated employees (EMP:PAYROLL_2026:%)...")
            cur.execute(
                'DELETE FROM fix_event_outbox WHERE payload LIKE \'%"legacy_reference": "EMP:PAYROLL_2026:%\';'
            )
            cur.execute(
                "SELECT resource_id FROM hr_employee WHERE legacy_reference LIKE 'EMP:PAYROLL_2026:%';"
            )
            resource_ids = [r[0] for r in cur.fetchall() if r[0]]
            cur.execute("DELETE FROM hr_employee WHERE legacy_reference LIKE 'EMP:PAYROLL_2026:%';")
            stats["employees_deleted"] = cur.rowcount
            if resource_ids:
                cur.execute("DELETE FROM resource_resource WHERE id = ANY(%s);", (resource_ids,))
            print(f"  -> Deleted {stats['employees_deleted']} migrated employee records.")

            # 4. Rollback Customers / employee parties & their Z4 identity documents
            print(
                "[4/5] Rolling back migrated parties & Z4 records (CUST:WP_STORE:%, PARTNER:EMP:%)..."
            )
            erased_z4 = 0
            erase_failures: list[str] = []
            for pattern, namespace in Z4_NAMESPACES.items():
                cur.execute(
                    """
                    SELECT residency_ref FROM fix_identity_document
                    WHERE partner_id IN (
                        SELECT id FROM res_partner WHERE legacy_reference LIKE %s
                    );
                    """,
                    (pattern,),
                )
                for (ref,) in cur.fetchall():
                    if not ref:
                        continue
                    try:
                        residency.erase(f"{namespace}:{ref}")
                        erased_z4 += 1
                    except Exception as e:
                        logger.warning("Failed to erase Z4 key %s: %s", ref, e)
                        erase_failures.append(f"{namespace}:{ref}")

            cur.execute("""
                DELETE FROM fix_identity_document
                WHERE partner_id IN (
                    SELECT id FROM res_partner WHERE legacy_reference LIKE 'CUST:WP_STORE:%'
                       OR legacy_reference LIKE 'PARTNER:EMP:PAYROLL_2026:%'
                );
            """)
            cur.execute("""
                DELETE FROM fix_party_role
                WHERE partner_id IN (
                    SELECT id FROM res_partner WHERE legacy_reference LIKE 'CUST:WP_STORE:%'
                       OR legacy_reference LIKE 'PARTNER:EMP:PAYROLL_2026:%'
                );
            """)
            cur.execute("""
                DELETE FROM res_partner
                WHERE legacy_reference LIKE 'CUST:WP_STORE:%'
                   OR legacy_reference LIKE 'PARTNER:EMP:PAYROLL_2026:%';
            """)
            stats["customers_deleted"] = cur.rowcount
            stats["z4_keys_erased"] = erased_z4
            stats["z4_erase_failures"] = erase_failures
            print(f"  -> Deleted {stats['customers_deleted']} customer/employee partner records.")
            print(f"  -> Erased {erased_z4} Z4 residency keys ({len(erase_failures)} failed).")

            # 5. Rollback Branches
            print("[5/5] Rolling back migrated branches (BR:PILOT_2026:%)...")
            cur.execute("DELETE FROM fix_branch WHERE legacy_reference LIKE 'BR:PILOT_2026:%';")
            stats["branches_deleted"] = cur.rowcount
            print(f"  -> Deleted {stats['branches_deleted']} migrated branch records.")

        conn.commit()
        with conn.cursor() as cur:
            stats["residual_rows"] = residual_rows(cur)
    finally:
        conn.close()

    stats["baseline_restored"] = not stats["residual_rows"] and not stats["z4_erase_failures"]
    print("=" * 70)
    if stats["baseline_restored"]:
        print("MG-007 Rollback Rehearsal Complete — read-back finds no migrated row left.")
    else:
        print("MG-007 Rollback INCOMPLETE:")
        for key, count in stats["residual_rows"].items():
            print(f"  - {count} rows remain in {key}")
        if stats["z4_erase_failures"]:
            print(f"  - {len(stats['z4_erase_failures'])} Z4 keys could not be erased")
    print("=" * 70)
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MG-007 Rollback (Wave-1 + ETL-5 inventory)")
    parser.add_argument(
        "--dsn", help="PostgreSQL DSN (default: DATABASE_URL / PG* / fix_migration on loopback)"
    )
    args = parser.parse_args()
    sys.exit(0 if execute_rollback(args.dsn)["baseline_restored"] else 1)
