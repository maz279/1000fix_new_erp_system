#!/usr/bin/env python3
"""migrations/pipeline.py — Wave-1 Migration Pipeline Orchestrator.

Conforms to docs/p04/migration-etl-specs.md and docs/p04/migration-mig-standards.md:
  Topological sequence (on a CLEAN target, see migrations/REHEARSAL.md):
    ETL-0: Reference data (entity, operating units, brands/models) + MD-* register
    ETL-3: Branches -> ETL-1: Customers -> ETL-2: Devices -> ETL-4: Employees
    -> Attendance opening balances (R06-M02-T05, needs ETL-4)
  Enforces:
    MIG-02: Control totals reconciliation via mig-totals.py; extract checksums are
            re-verified against the manifest BEFORE anything is loaded
    MIG-03: Permanent legacy_reference on every target model
    MIG-06: Z4 residency routing via fix_residency (no plain NID/TIN in regional DB),
            measured by scanning the loaded tables for the extracts' classified values

GV-009: the closing banner states what was measured - accepted and quarantined
counts per entity - and never calls a run with quarantined records "reconciled"
without saying they await MG-004 steward disposition.

Target: the dedicated rehearsal database `fix_migration` (never fix_dev, DE-12);
--dsn / DATABASE_URL / PG* override (migrations/target_db.py).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from psycopg2 import sql

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from libs.py.fix_residency import ResidencyError  # noqa: E402 - after sys.path bootstrap
from libs.py.fix_residency import get_client as get_residency_client  # noqa: E402
from migrations.extracts_generator import compute_sha256  # noqa: E402
from migrations.load_attendance_opening import AttendanceOpeningMigrator  # noqa: E402
from migrations.load_branches import load_branches  # noqa: E402
from migrations.load_customers import load_customers  # noqa: E402
from migrations.load_devices import load_devices  # noqa: E402
from migrations.load_employees import load_employees  # noqa: E402
from migrations.load_reference_data import load_reference_data  # noqa: E402
from migrations.target_db import (  # noqa: E402
    RehearsalTargetError,
    connect,
    describe,
    resolve_dsn,
)

MIGRATIONS_DIR = Path(__file__).resolve().parent
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"
MASTER_DATA_SCRIPT = REPO_ROOT / "tooling" / "scripts" / "load-master-data.py"
MIG_TOTALS_SCRIPT = REPO_ROOT / "tooling" / "scripts" / "mig-totals.py"

# Loader stages that report into loaded-counts.json (MIG-02 entities)
ENTITIES = ("branches", "customers", "devices", "employees", "attendance_opening")

# MIG-06: extract fields that may only ever live in the Z4 vault, and the tables the
# Wave-1 loaders write (scanned for those values in plaintext after the load).
CLASSIFIED_FIELDS = ("nid", "tin")
CLASSIFIED_EXTRACTS = ("customers_extract.json", "employees_extract.json")
RESIDENCY_SCAN_TABLES = (
    "res_partner",
    "hr_employee",
    "resource_resource",
    "fix_identity_document",
    "fix_party_role",
    "fix_device",
    "fix_branch",
    "fix_attendance_record",
    "fix_event_outbox",
)
TEXT_TYPES = ("character varying", "character", "text", "json", "jsonb")


def classified_values(extracts_dir: Path = EXTRACTS_DIR) -> list[str]:
    values: set[str] = set()
    for name in CLASSIFIED_EXTRACTS:
        for record in json.loads((extracts_dir / name).read_text(encoding="utf-8")):
            for field in CLASSIFIED_FIELDS:
                value = str(record.get(field) or "").strip()
                if value:
                    values.add(value)
    return sorted(values)


def residency_leaks(cur, values: list[str]) -> tuple[dict[str, int], int]:
    """{table.column: rows holding a classified value in plaintext}, columns scanned."""
    patterns = [
        "%" + v.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%" for v in values
    ]
    cur.execute(
        "SELECT table_name, column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = ANY(%s) AND data_type = ANY(%s) "
        "ORDER BY table_name, column_name;",
        (list(RESIDENCY_SCAN_TABLES), list(TEXT_TYPES)),
    )
    columns = cur.fetchall()
    leaks: dict[str, int] = {}
    for table, column in columns:
        cur.execute(
            sql.SQL("SELECT count(*) FROM {} WHERE {}::text LIKE ANY(%s)").format(
                sql.Identifier(table), sql.Identifier(column)
            ),
            (patterns,),
        )
        hits = cur.fetchone()[0]
        if hits:
            leaks[f"{table}.{column}"] = hits
    return leaks, len(columns)


def get_db_connection(dsn: str | None = None):
    """Connect to the rehearsal target (fix_migration unless overridden)."""
    return connect(dsn)


def verify_extracts(manifest: dict) -> list[str]:
    """MIG-02: every extract must still be the one the control totals were taken from."""
    problems = []
    files = manifest.get("extract_files", {})
    for entity, expected in manifest.get("checksums", {}).items():
        path = EXTRACTS_DIR / files.get(entity, f"{entity}_extract.json")
        if not path.exists():
            problems.append(f"{entity}: extract {path.name} missing")
        elif compute_sha256(path) != expected:
            problems.append(f"{entity}: {path.name} changed since control totals were produced")
    missing = [
        e for e in manifest.get("control_totals", {}) if e not in manifest.get("checksums", {})
    ]
    problems.extend(f"{e}: no checksum in manifest" for e in missing)
    return problems


def load_master_data_register(conn) -> tuple[int, int]:
    """MD-048 tiered MD-* register (tooling/scripts/load-master-data.py) on this target."""
    spec = importlib.util.spec_from_file_location("load_master_data_script", MASTER_DATA_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary, rows = module.load_master_data(conn, verbose=False)
    return len(summary), rows


def run_pipeline(dsn: str | None = None, loaded_counts_path: Path | None = None) -> int:
    print("=" * 70)
    print("Starting 1000FiX Wave-1 Migration Load Pipeline (MIG-01..MIG-08)")
    print("=" * 70)

    # 1. Verify extract files & control-totals exist
    manifest_path = EXTRACTS_DIR / "control-totals.json"
    if not manifest_path.exists():
        # never fabricate the source: a missing manifest is a missing extract run
        print(f"MIG-02 FAIL: extract manifest {manifest_path} not found.")
        print(
            "Produce the run's extracts + manifest first (synthetic rehearsal: "
            "python migrations/extracts_generator.py)."
        )
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(f"Loaded extract manifest for run: {manifest.get('run')}")
    print(f"Target control totals: {manifest.get('control_totals')}")
    drift = verify_extracts(manifest)
    if drift:
        print("MIG-02 FAIL: extract checksums do not match control-totals.json:")
        for line in drift:
            print(f"  - {line}")
        print("Regenerate the run's extracts + manifest: python migrations/extracts_generator.py")
        return 1
    print("Extract checksums verified against the manifest (MIG-02).")

    # 2. Preflight: target database (dedicated, clean) and the residency service (MIG-06)
    try:
        resolved = resolve_dsn(dsn)
        conn = get_db_connection(resolved)
    except RehearsalTargetError as exc:
        print(f"TARGET ERROR: {exc}")
        return 2
    print(f"Connected to target database {describe(resolved)}.")
    try:
        get_residency_client().health()
    except ResidencyError as exc:
        conn.close()
        print(f"RESIDENCY ERROR: {exc}")
        print(
            "Start the local residency stub first: docker compose -f "
            "infra/compose/docker-compose.yml --profile core up -d residency-stub"
        )
        return 2
    print("Residency service (Z4) healthy.\n")

    results = {}
    try:
        # Step 0: prerequisite reference data + MD-* register (clean target)
        print("[0/5] Executing ETL-0: Reference data + MD-* master data register...")
        ref = load_reference_data(EXTRACTS_DIR, conn)
        print(
            f"  -> Entity id {ref['entity_id']} (created: {ref['entity_created']}); "
            f"operating units {ref['operating_units']} (created {ref['operating_units_created']}); "
            f"device models {ref['device_models']} (created {ref['device_models_created']}, "
            f"brands created {ref['brands_created']})"
        )
        if ref["operating_units_missing"] or ref["brands_without_code"]:
            print(
                f"  -> NOT created (no fixture entry, never invented): operating units "
                f"{ref['operating_units_missing']}, brands {ref['brands_without_code']}"
            )
        md_sets, md_rows = load_master_data_register(conn)
        print(f"  -> MD-* register: {md_sets} datasets, {md_rows} payload rows")

        # Step 1: ETL-3 Branches
        print("\n[1/5] Executing ETL-3: Branch Master Load...")
        b_res = load_branches(EXTRACTS_DIR / "branches_extract.json", conn)
        results["branches"] = b_res
        print(
            f"  -> Branches loaded: {b_res['loaded_count']} / {b_res['total_records']} (rejections: {b_res['rejected_count']})"
        )

        # Step 2: ETL-1 Customers
        print("\n[2/5] Executing ETL-1: Customer Master Load (M64 Dedup + Z4 Residency)...")
        c_res = load_customers(EXTRACTS_DIR / "customers_extract.json", conn)
        results["customers"] = c_res
        print(
            f"  -> Customers loaded: {c_res['loaded_count']} / {c_res['total_records']} (quarantined: {c_res['rejected_count']})"
        )

        # Step 3: ETL-2 Devices
        print("\n[3/5] Executing ETL-2: Device Master Load (Serial/IMEI Gate + Warranty)...")
        d_res = load_devices(EXTRACTS_DIR / "devices_extract.json", conn)
        results["devices"] = d_res
        print(
            f"  -> Devices loaded: {d_res['loaded_count']} / {d_res['total_records']} (flagged for MDM review: {d_res['rejected_count']})"
        )

        # Step 4: ETL-4 Employees
        print("\n[4/5] Executing ETL-4: Employee Master Load (JML Events + Roles)...")
        e_res = load_employees(EXTRACTS_DIR / "employees_extract.json", conn)
        results["employees"] = e_res
        print(
            f"  -> Employees loaded: {e_res['loaded_count']} / {e_res['total_records']} (rejections: {e_res['rejected_count']})"
        )

        # Step 5: Attendance opening balances (TSS 19.1), after the employees they reference
        print("\n[5/5] Executing R06-M02-T05: Attendance Opening Balances (TSS 19.1)...")
        a_res = AttendanceOpeningMigrator().run_migration(
            EXTRACTS_DIR / "attendance_opening_extract.json", db_conn=conn
        )
        results["attendance_opening"] = a_res
        print(
            f"  -> Opening balances loaded: {a_res['loaded_count']} / {a_res['total_records']} "
            f"(TSS 19.1 excluded: {a_res['skipped_historical']}, "
            f"quarantined: {a_res['unresolved']})"
        )

    finally:
        conn.close()

    # 3. Emit loaded-counts.json for mig-totals.py. loaded_totals = every extracted
    # record the load dispositioned (accepted + quarantined); quarantines are the
    # variances MG-004 signs off.
    loaded_counts_path = loaded_counts_path or (EXTRACTS_DIR / "loaded-counts.json")
    loaded_counts_path.parent.mkdir(parents=True, exist_ok=True)
    loaded_manifest = {
        "run": manifest.get("run"),
        "loaded_at": datetime.now(UTC).isoformat(),
        "target_database": describe(resolved),
        "loaded_totals": {
            e: results[e]["loaded_count"] + results[e]["rejected_count"] for e in ENTITIES
        },
        "accepted_records": {e: results[e]["loaded_count"] for e in ENTITIES},
        "quarantined_records": {e: results[e]["rejected_count"] for e in ENTITIES},
        "rejections": {e: results[e]["rejections"] for e in ENTITIES if results[e]["rejections"]},
    }
    loaded_counts_path.write_text(
        json.dumps(loaded_manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"\nEmitted loaded counts to: {loaded_counts_path}")
    print(f"  accepted:    {loaded_manifest['accepted_records']}")
    print(f"  quarantined: {loaded_manifest['quarantined_records']}")

    # 4. Enforce MIG-02 Control Totals Reconciliation
    print("\n[MIG-02 Reconciliation] Running tooling/scripts/mig-totals.py...")
    cmd = [
        sys.executable,
        str(MIG_TOTALS_SCRIPT),
        "--manifest",
        str(manifest_path),
        "--loaded",
        str(loaded_counts_path),
    ]
    rec_res = subprocess.run(  # noqa: S603 - fixed argv list built in-process, no shell
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    print(rec_res.stdout)
    if rec_res.returncode != 0:
        print(f"mig-totals FAILED:\n{rec_res.stderr}")
        return 1

    # 5. MIG-06 residency: no classified extract value in plaintext in the loaded tables
    print("[MIG-06 Check] Scanning the loaded tables for the extracts' NID/TIN values...")
    values = classified_values()
    check_conn = get_db_connection(resolved)
    try:
        with check_conn.cursor() as cur:
            leaks, columns = residency_leaks(cur, values) if values else ({}, 0)
    finally:
        check_conn.close()
    if leaks:
        print(f"MIG-06 VIOLATION: classified values stored in plaintext in {leaks}")
        return 1
    if not values or not columns:
        print("  MIG-06 NOT MEASURED: no classified values / scannable columns")
    else:
        print(
            f"  PASS: {len(values)} classified values absent from {columns} text columns "
            f"of {len(RESIDENCY_SCAN_TABLES)} loaded tables."
        )

    quarantined = sum(loaded_manifest["quarantined_records"].values())
    accepted = sum(loaded_manifest["accepted_records"].values())
    print("\n" + "=" * 70)
    print(
        f"Wave-1 Migration Pipeline COMPLETED: control totals reconciled (MIG-02); "
        f"{accepted} records accepted, {quarantined} quarantined"
        + (" pending MG-004 steward disposition" if quarantined else "")
    )
    print("=" * 70)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wave-1 Migration Pipeline")
    parser.add_argument(
        "--dsn", help="PostgreSQL DSN (default: DATABASE_URL / PG* / fix_migration on loopback)"
    )
    parser.add_argument(
        "--loaded-counts",
        type=Path,
        help="where to emit loaded-counts.json (default: migrations/extracts/loaded-counts.json)",
    )
    args = parser.parse_args()
    sys.exit(run_pipeline(args.dsn, args.loaded_counts))
