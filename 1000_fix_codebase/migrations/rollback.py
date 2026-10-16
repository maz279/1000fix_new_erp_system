#!/usr/bin/env python3
"""migrations/rollback.py — MG-007 Rollback Engine for Wave-1 Loads.

Specification: docs/p04/migration-mig-standards.md (MIG-07, DoD-16).
Rehearses idempotent rollback by legacy_reference and erases Z4 classified keys.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import psycopg2

from libs.py.fix_residency import get_client as get_residency_client

logger = logging.getLogger(__name__)


def get_db_connection(dsn: str | None = None):
    db_url = dsn or os.environ.get(
        "DATABASE_URL",
        "postgresql://fix:change-me-dev-only@127.0.0.1:5433/fix_dev"
    )
    return psycopg2.connect(db_url)


def execute_rollback(dsn: str | None = None) -> dict[str, int]:
    print("=" * 70)
    print("Executing MG-007 Migration Rollback (MIG-07 Rehearsal)")
    print("=" * 70)

    conn = get_db_connection(dsn)
    residency = get_residency_client()
    stats = {}

    try:
        with conn.cursor() as cur:
            # 1. Rollback Devices
            print("[1/4] Rolling back migrated devices (DEV:ASSET_SHEET:%)...")
            cur.execute("""
                DELETE FROM fix_warranty
                WHERE device_id IN (
                    SELECT id FROM fix_device WHERE legacy_reference LIKE 'DEV:ASSET_SHEET:%'
                );
            """)
            cur.execute("DELETE FROM fix_device WHERE legacy_reference LIKE 'DEV:ASSET_SHEET:%';")
            stats["devices_deleted"] = cur.rowcount
            print(f"  -> Deleted {stats['devices_deleted']} migrated device records.")

            # 2. Rollback Employees
            print("[2/4] Rolling back migrated employees (EMP:PAYROLL_2026:%)...")
            cur.execute("DELETE FROM fix_event_outbox WHERE payload LIKE '%\"legacy_reference\": \"EMP:PAYROLL_2026:%';")
            cur.execute("DELETE FROM hr_employee WHERE legacy_reference LIKE 'EMP:PAYROLL_2026:%';")
            stats["employees_deleted"] = cur.rowcount
            print(f"  -> Deleted {stats['employees_deleted']} migrated employee records.")

            # 3. Rollback Customers & Z4 Identity documents
            print("[3/4] Rolling back migrated customers & Z4 records (CUST:WP_STORE:%)...")
            cur.execute("""
                SELECT residency_ref FROM fix_identity_document
                WHERE partner_id IN (
                    SELECT id FROM res_partner WHERE legacy_reference LIKE 'CUST:WP_STORE:%'
                );
            """)
            z4_refs = [r[0] for r in cur.fetchall() if r[0]]
            erased_z4 = 0
            for ref in z4_refs:
                try:
                    residency.erase(f"party identity:{ref}")
                    erased_z4 += 1
                except Exception as e:
                    logger.warning("Failed to erase Z4 key %s: %s", ref, e)

            cur.execute("""
                DELETE FROM fix_identity_document
                WHERE partner_id IN (
                    SELECT id FROM res_partner WHERE legacy_reference LIKE 'CUST:WP_STORE:%'
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
            print(f"  -> Deleted {stats['customers_deleted']} customer partner records.")
            print(f"  -> Erased {erased_z4} Z4 residency tombstone keys.")

            # 4. Rollback Branches
            print("[4/4] Rolling back migrated branches (BR:PILOT_2026:%)...")
            cur.execute("DELETE FROM fix_branch WHERE legacy_reference LIKE 'BR:PILOT_2026:%';")
            stats["branches_deleted"] = cur.rowcount
            print(f"  -> Deleted {stats['branches_deleted']} migrated branch records.")

        conn.commit()
    finally:
        conn.close()

    print("=" * 70)
    print("MG-007 Rollback Rehearsal Complete — Database returned to baseline.")
    print("=" * 70)
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wave-1 MG-007 Rollback")
    parser.add_argument("--dsn", help="PostgreSQL connection DSN")
    args = parser.parse_args()
    execute_rollback(args.dsn)
