#!/usr/bin/env python3
"""mig-totals — MIG-02 control-totals verifier (PP6 E5).

Reconciliation gate for every migration load into migration-staging:
compares a run's control-totals manifest (produced at EXTRACT time by
the pipeline) against the counts as loaded (either a loaded-counts file
or a live psql query via --dsn). Mismatch fails closed — MG-004
reconciliation with business sign-off precedes any decommission
(MIG-08); this tool produces the report that sign-off reads.

Usage:
  python tooling/scripts/mig-totals.py --manifest migrations/<run>/control-totals.json \
      [--loaded migrations/<run>/loaded-counts.json | --dsn postgresql://...]

Exit: 0 reconciled / 1 mismatch-or-error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from urllib.parse import urlparse


def validate_dsn(dsn: str) -> None:
    """SSRF guard: postgres schemes only, no literal credentials in code."""
    p = urlparse(dsn)
    if p.scheme not in ("postgres", "postgresql"):
        raise ValueError(f"mig-totals: refusing non-postgres DSN {dsn!r}")
    host = p.hostname or ""
    if host in ("localhost", "127.0.0.1", "::1") and "migration" not in (p.path or ""):
        # rehearsal DSNs point at the migration-staging DB; anything else
        # on loopback is likely the DEV database — refuse (DE-12)
        raise ValueError(
            "mig-totals: loopback DSN must target the fix_migration database "
            "(never the dev database)")


def query_live_counts(dsn: str, entities: list[str]) -> dict:
    """Live counts via psql (subprocess) — no DB driver dependency."""
    import subprocess
    validate_dsn(dsn)
    counts = {}
    for entity in entities:
        table = re.sub(r"[^a-z_.]", "", entity.lower())
        if not table:
            continue
        r = subprocess.run(
            ["psql", dsn, "-At", "-c", f"SELECT count(*) FROM {table};"],
            capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(f"psql failed for {table}: {r.stderr.strip()[:120]}")
        counts[entity] = int(r.stdout.strip() or 0)
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", required=True,
                    help="control-totals.json produced at extract time")
    ap.add_argument("--loaded",
                    help="loaded-counts.json produced by the loader")
    ap.add_argument("--dsn",
                    help="query the loaded counts live (postgresql://…, "
                         "must target the fix_migration database)")
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    control: dict[str, int] = manifest.get("control_totals", manifest)

    if args.loaded:
        loaded = json.loads(Path(args.loaded).read_text(encoding="utf-8"))
        got: dict[str, int] = loaded.get("loaded_totals", loaded)
    elif args.dsn:
        try:
            got = query_live_counts(args.dsn, list(control))
        except Exception as e:
            print(f"mig-totals: ERROR - {e}")
            return 1
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
    missing = [e for e in control if e not in got]
    for e in missing:
        mismatches.append(e)

    run = manifest.get("run", Path(args.manifest).parent.name)
    print(f"MIG-02 control totals — run {run}")
    print("\n".join(lines))
    if mismatches:
        print(f"\nmig-totals: FAIL - {len(mismatches)} mismatch(es): "
              f"{mismatches}\n  MG-004 reconciliation BLOCKED until "
              "business sign-off on every variance (MIG-08 decommission "
              "gate)")
        return 1
    print("\nmig-totals: OK — every control total reconciled; emit this "
          "report with the MG-004 sign-off request")
    return 0


if __name__ == "__main__":
    sys.exit(main())
