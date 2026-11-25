#!/usr/bin/env python3
"""mig-totals — MIG-02 control-totals verifier (PP6 E5).

Reconciliation gate for every migration load into migration-staging:
compares a run's control-totals manifest (produced at EXTRACT time by
migrations/extracts_generator.py) against the counts as loaded. Mismatch
fails closed — MG-004 reconciliation with business sign-off precedes any
decommission (MIG-08); this tool produces the report that sign-off reads.

Loaded counts come from:
  --loaded FILE        the loaded-counts.json the pipeline emitted
                       (loaded_totals = accepted + quarantined per entity)
  --dsn URL            live: migrated rows counted in the target database by
                       their permanent legacy reference (LIVE_COUNT_SOURCES).
                       Alone, only accepted rows exist in the database, so every
                       quarantined record surfaces as a variance.
  --loaded + --dsn     the file's accepted_records must equal the live counts
                       (else DRIFT, fail), and live + quarantined is reconciled.

Usage:
  python tooling/scripts/mig-totals.py --manifest migrations/<run>/control-totals.json \
      [--loaded migrations/<run>/loaded-counts.json] [--dsn postgresql://.../fix_migration]

Exit: 0 reconciled / 1 mismatch-or-error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

# Live-count sources (MIG-03): entity -> (table, legacy-key column, legacy prefix).
# The keys the Wave-1 loaders write (migrations/load_*.py) and MG-007 rollback
# deletes by (migrations/rollback.py). Fixed constants - never user input.
LIVE_COUNT_SOURCES: dict[str, tuple[str, str, str]] = {
    "branches": ("fix_branch", "legacy_reference", "BR:PILOT_2026:"),
    "customers": ("res_partner", "legacy_reference", "CUST:WP_STORE:"),
    "devices": ("fix_device", "legacy_reference", "DEV:ASSET_SHEET:"),
    "employees": ("hr_employee", "legacy_reference", "EMP:PAYROLL_2026:"),
    "attendance_opening": ("fix_attendance_record", "device_ref", "LEG:SIGNIN_BOOK:"),
}


def validate_dsn(dsn: str) -> None:
    """SSRF guard: postgres schemes only, no literal credentials in code."""
    p = urlparse(dsn)
    if p.scheme not in ("postgres", "postgresql"):
        raise ValueError(f"mig-totals: refusing non-postgres DSN {dsn!r}")
    host = p.hostname or ""
    if host in ("localhost", "127.0.0.1", "::1") and (p.path or "").lstrip("/") != "fix_migration":
        # rehearsal DSNs point at the dedicated fix_migration DB (built by
        # tooling/scripts/build-test-db.py --db fix_migration); anything else
        # on loopback is likely the DEV database — refuse (DE-12)
        raise ValueError(
            "mig-totals: loopback DSN must target the fix_migration database "
            "(never the dev database)"
        )


def live_count_sql(entity: str) -> str:
    """SELECT counting the migrated rows of `entity`; unmapped entities fail closed."""
    try:
        table, column, prefix = LIVE_COUNT_SOURCES[entity]
    except KeyError:
        raise ValueError(
            f"no live-count source mapped for entity {entity!r} "
            f"(known: {sorted(LIVE_COUNT_SOURCES)})"
        ) from None
    return f"SELECT count(*) FROM {table} WHERE {column} LIKE '{prefix}%'"


def query_live_counts(dsn: str, entities: list[str]) -> dict[str, int]:
    """Migrated (accepted) rows per entity, counted live in the target database.

    psycopg2 when importable (the pipeline's environment), else the psql client.
    """
    validate_dsn(dsn)
    queries = {entity: live_count_sql(entity) for entity in entities}
    counts: dict[str, int] = {}
    try:
        import psycopg2
    except ImportError:  # e.g. a bare python:3.12-slim runner with psql installed
        import subprocess

        for entity, sql in queries.items():
            r = subprocess.run(
                ["psql", dsn, "-At", "-c", f"{sql};"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if r.returncode != 0:
                raise RuntimeError(f"psql failed for {entity}: {r.stderr.strip()[:120]}") from None
            counts[entity] = int(r.stdout.strip() or 0)
        return counts

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            for entity, sql in queries.items():
                cur.execute(sql)
                counts[entity] = int(cur.fetchone()[0])
    finally:
        conn.close()
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--manifest", required=True, help="control-totals.json produced at extract time"
    )
    ap.add_argument("--loaded", help="loaded-counts.json produced by the loader")
    ap.add_argument(
        "--dsn",
        help="count the loaded rows live (postgresql://…, "
        "must target the fix_migration database)",
    )
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    control: dict[str, int] = manifest.get("control_totals", manifest)
    loaded = json.loads(Path(args.loaded).read_text(encoding="utf-8")) if args.loaded else None

    drift: list[str] = []
    if args.dsn:
        try:
            live = query_live_counts(args.dsn, list(control))
        except Exception as e:
            print(f"mig-totals: ERROR - {e}")
            return 1
        if loaded is None:
            source = "live database (accepted rows only)"
            got: dict[str, int] = live
        else:
            source = "live database accepted rows + loaded-counts quarantines"
            accepted = loaded.get("accepted_records", {})
            quarantined = loaded.get("quarantined_records", {})
            drift = [
                f"  [DRIFT] {entity}: loaded-counts accepted={accepted.get(entity)} "
                f"database={live[entity]}"
                for entity in sorted(live)
                if accepted.get(entity) != live[entity]
            ]
            got = {entity: live[entity] + quarantined.get(entity, 0) for entity in live}
    elif loaded is not None:
        source = "loaded-counts file"
        got = loaded.get("loaded_totals", loaded)
    else:
        print("mig-totals: ERROR - one of --loaded or --dsn is required")
        return 1

    mismatches = []
    lines = []
    for entity, expected in sorted(control.items()):
        actual = got.get(entity)
        status = "OK" if actual == expected else "MISMATCH"
        if actual != expected:
            mismatches.append(entity)
        lines.append(f"  [{status}] {entity}: control={expected} loaded={actual}")
    # an entity absent from the loaded counts is already a MISMATCH above
    # (loaded=None) - never count it twice

    run = manifest.get("run", Path(args.manifest).parent.name)
    print(f"MIG-02 control totals — run {run} (loaded: {source})")
    print("\n".join(lines + drift))
    if drift:
        print(
            f"\nmig-totals: FAIL - loaded-counts disagrees with the database for "
            f"{len(drift)} entit(y/ies); the load report cannot be trusted"
        )
        return 1
    if mismatches:
        print(
            f"\nmig-totals: FAIL - {len(mismatches)} mismatch(es): "
            f"{mismatches}\n  MG-004 reconciliation BLOCKED until "
            "business sign-off on every variance (MIG-08 decommission "
            "gate)"
        )
        return 1
    print(
        "\nmig-totals: OK — every control total reconciled; emit this "
        "report with the MG-004 sign-off request"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
