#!/usr/bin/env python3
"""run_production_migration_rehearsal.py — Milestone R10-M05 Task T02 (measure-only).

Measures the evidence of the production migration rehearsal (MG-005) that
discharges Gate GP-11. GV-009: every status below is computed from a check made
in this run - nothing is hard-coded - and a check that cannot be observed from
here is UNMEASURED (with its reason), which keeps the verdict off PASS.

  MG005_PRODUCTION_VOLUME  production volume on migration-staging (not observable here)
  MIG02_EXTRACT_<STREAM>   record count + LF-normalised sha256 of each committed
                           extract vs the extract-time control-totals.json
  MIG02_CONTROL_TOTALS     control totals vs the pipeline's loaded-counts.json
  MIG02_LIVE_COUNTS        loaded-counts accepted records vs a read-only count in
                           the rehearsal database (fix_migration, never fix_dev)
  MIG06_RESIDENCY          no classified extract value (NID/TIN) stored in
                           plaintext in the migrated tables (read-only scan)
  MG007_ROLLBACK           rollback rehearsal - destructive, never run by this tool
  MG004_BUSINESS_SIGNOFF   the named business owner's signature

Read-only by construction: it never writes under migrations/ or to a database
(the previous version generated "production-volume" manifests into
migrations/extracts/ and reconciled them against themselves). Outputs:
  docs/traceability/evidence/r10-m05-migration-rehearsal-evidence.json
  docs/traceability/evidence/r10-m05-mg004-business-signoff.json (sign-off request)

The measurement functions are shared with run_final_cutover_rehearsal.py (R11-M01-T02).

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

CODEBASE_ROOT = Path(__file__).resolve().parents[2]
if str(CODEBASE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODEBASE_ROOT))

from migrations.extracts_generator import compute_sha256

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migration_rehearsal")

MIGRATIONS_DIR = CODEBASE_ROOT / "migrations"
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"
EVIDENCE_DIR = CODEBASE_ROOT / "docs" / "traceability" / "evidence"
MIG_TOTALS_SCRIPT = CODEBASE_ROOT / "tooling" / "scripts" / "mig-totals.py"

MANIFEST_NAME = "control-totals.json"
LOADED_NAME = "loaded-counts.json"
EVIDENCE_NAME = "r10-m05-migration-rehearsal-evidence.json"
SIGNOFF_NAME = "r10-m05-mg004-business-signoff.json"

PASS = "PASS"  # noqa: S105 - a verdict label, not a credential
FAIL = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

# MIG-06: extract fields that may only ever live in the Z4 vault, never in plaintext.
CLASSIFIED_FIELDS = ("nid", "tin")
# Tables the Wave-1 loaders write (migrations/load_*.py) - scanned for plaintext leaks.
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
TEXT_COLUMN_TYPES = ("character varying", "character", "text", "json", "jsonb")

Connector = Callable[[], tuple[Any, str]]


def make_check(check_id: str, status: str, detail: str, **measured: Any) -> dict:
    return {"id": check_id, "status": status, "detail": detail, **measured}


def overall_verdict(checks: list[dict]) -> str:
    """FAIL if any check failed, PASS only if every check passed, else INCOMPLETE."""
    statuses = {check["status"] for check in checks}
    if not statuses:
        return UNMEASURED
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def count_statuses(checks: list[dict]) -> dict[str, int]:
    return {s.lower(): sum(1 for c in checks if c["status"] == s) for s in (PASS, FAIL, UNMEASURED)}


def read_json(path: Path) -> tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"{path.name} not found"
    except (OSError, ValueError) as exc:
        return None, f"{path.name} unreadable: {exc}"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def load_mig_totals() -> ModuleType:
    """tooling/scripts/mig-totals.py - the single source of the live-count SQL."""
    spec = importlib.util.spec_from_file_location("mig_totals_for_rehearsal", MIG_TOTALS_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def connect_rehearsal_db() -> tuple[Any, str]:
    """Read-only connection to the rehearsal target (migrations/target_db: never fix_dev)."""
    import psycopg2

    from migrations import target_db

    dsn = target_db.resolve_dsn()
    conn = psycopg2.connect(dsn, connect_timeout=5)
    conn.set_session(readonly=True, autocommit=True)
    return conn, target_db.describe(dsn)


def extract_path(extracts_dir: Path, manifest: dict, stream: str) -> Path:
    return extracts_dir / (manifest.get("extract_files") or {}).get(
        stream, f"{stream}_extract.json"
    )


def measure_extracts(extracts_dir: Path, manifest: dict) -> list[dict]:
    """MIG-02: each extract still has the record count and checksum taken at extract time."""
    control = manifest.get("control_totals") or {}
    checksums = manifest.get("checksums") or {}
    checks = []
    for stream in sorted(control):
        path = extract_path(extracts_dir, manifest, stream)
        measured: dict[str, Any] = {
            "stream": stream,
            "extract_file": path.name,
            "control_total": control[stream],
            "manifest_sha256": checksums.get(stream),
            "record_count": None,
            "sha256": None,
        }
        check_id = f"MIG02_EXTRACT_{stream.upper()}"
        records, error = read_json(path)
        if error:
            checks.append(make_check(check_id, FAIL, error, **measured))
            continue
        measured["record_count"] = len(records) if isinstance(records, list) else None
        measured["sha256"] = compute_sha256(path)
        problems = []
        if measured["record_count"] != control[stream]:
            problems.append(
                f"record count {measured['record_count']} != control total {control[stream]}"
            )
        if measured["manifest_sha256"] is None:
            problems.append("no checksum for this stream in the manifest")
        elif measured["sha256"] != measured["manifest_sha256"]:
            problems.append("sha256 differs from the manifest (extract changed after extraction)")
        detail = "; ".join(problems) or (
            f"{measured['record_count']} records; sha256 matches the extract-time manifest"
        )
        checks.append(make_check(check_id, FAIL if problems else PASS, detail, **measured))
    if not checks:
        checks.append(make_check("MIG02_EXTRACTS", FAIL, "the manifest declares no control totals"))
    return checks


def measure_control_totals(manifest: dict, loaded: dict | None, loaded_error: str | None) -> dict:
    """MIG-02: control totals vs the pipeline's load report (loaded = accepted + quarantined)."""
    if loaded is None:
        return make_check(
            "MIG02_CONTROL_TOTALS",
            UNMEASURED,
            f"no load report to reconcile ({loaded_error}); run migrations/pipeline.py",
        )
    control = manifest.get("control_totals") or {}
    totals = loaded.get("loaded_totals") or {}
    accepted = loaded.get("accepted_records") or {}
    quarantined = loaded.get("quarantined_records") or {}
    problems = []
    if loaded.get("run") != manifest.get("run"):
        problems.append(
            f"load report run {loaded.get('run')!r} != manifest run {manifest.get('run')!r}"
        )
    streams = {}
    reconciled = 0
    for stream in sorted(control):
        row = {
            "control": control[stream],
            "loaded": totals.get(stream),
            "accepted": accepted.get(stream),
            "quarantined": quarantined.get(stream),
        }
        streams[stream] = row
        if row["loaded"] != row["control"]:
            problems.append(f"{stream}: loaded {row['loaded']} != control {row['control']}")
        elif not (
            isinstance(row["accepted"], int)
            and isinstance(row["quarantined"], int)
            and row["accepted"] + row["quarantined"] == row["loaded"]
        ):
            problems.append(
                f"{stream}: accepted {row['accepted']} + quarantined {row['quarantined']} "
                f"!= loaded {row['loaded']}"
            )
        else:
            reconciled += 1
    if not control:
        problems.append("the manifest declares no control totals")
    detail = "; ".join(problems) or f"{reconciled}/{len(control)} streams reconciled"
    return make_check(
        "MIG02_CONTROL_TOTALS",
        FAIL if problems else PASS,
        detail,
        streams=streams,
        streams_in_manifest=len(control),
        streams_reconciled=reconciled,
        variance_count=len(control) - reconciled,
        quarantined_total=sum(v for v in quarantined.values() if isinstance(v, int)),
    )


def measure_live_counts(
    loaded: dict | None, conn: Any, target: str | None, conn_error: str | None
) -> dict:
    """MIG-02: the load report's accepted records are really in the rehearsal database."""
    if loaded is None:
        return make_check("MIG02_LIVE_COUNTS", UNMEASURED, "no load report to compare")
    if conn is None:
        return make_check(
            "MIG02_LIVE_COUNTS", UNMEASURED, f"rehearsal database not reachable: {conn_error}"
        )
    mig_totals = load_mig_totals()
    accepted = loaded.get("accepted_records") or {}
    live: dict[str, int] = {}
    drift = []
    unmapped = []
    try:
        with conn.cursor() as cur:
            for stream in sorted(accepted):
                if stream not in mig_totals.LIVE_COUNT_SOURCES:
                    unmapped.append(stream)
                    continue
                cur.execute(mig_totals.live_count_sql(stream))
                live[stream] = int(cur.fetchone()[0])
                if live[stream] != accepted[stream]:
                    drift.append(
                        f"{stream}: load report accepted {accepted[stream]} != database {live[stream]}"
                    )
    except Exception as exc:  # driver/schema errors: the database could not be measured
        return make_check(
            "MIG02_LIVE_COUNTS", UNMEASURED, f"live count query failed on {target}: {exc}"
        )
    if drift:
        status, detail = FAIL, "; ".join(drift)
    elif unmapped:
        status, detail = UNMEASURED, f"no live-count source mapped for {unmapped}"
    else:
        status, detail = PASS, f"{len(live)} streams: accepted records == rows in {target}"
    return make_check("MIG02_LIVE_COUNTS", status, detail, target_database=target, live_counts=live)


def classified_values(extracts_dir: Path, manifest: dict) -> dict[str, set[str]]:
    """stream -> the classified (NID/TIN) values its extract carries."""
    found: dict[str, set[str]] = {}
    for stream in manifest.get("control_totals") or {}:
        records, _ = read_json(extract_path(extracts_dir, manifest, stream))
        for record in records if isinstance(records, list) else []:
            if not isinstance(record, dict):
                continue
            for field in CLASSIFIED_FIELDS:
                value = str(record.get(field) or "").strip()
                if value:
                    found.setdefault(stream, set()).add(value)
    return found


def _like_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def measure_residency(
    extracts_dir: Path, manifest: dict, conn: Any, target: str | None, conn_error: str | None
) -> dict:
    """MIG-06: no classified extract value appears in plaintext in the migrated tables."""
    by_stream = classified_values(extracts_dir, manifest)
    values = sorted(set().union(*by_stream.values())) if by_stream else []
    if not values:
        return make_check(
            "MIG06_RESIDENCY", UNMEASURED, "the extracts carry no classified values to trace"
        )
    if conn is None:
        return make_check(
            "MIG06_RESIDENCY", UNMEASURED, f"rehearsal database not reachable: {conn_error}"
        )
    from psycopg2 import sql

    mig_totals = load_mig_totals()
    patterns = [_like_pattern(v) for v in values]
    leaks: dict[str, int] = {}
    migrated_rows = 0
    try:
        with conn.cursor() as cur:
            for stream in sorted(by_stream):
                if stream in mig_totals.LIVE_COUNT_SOURCES:
                    cur.execute(mig_totals.live_count_sql(stream))
                    migrated_rows += int(cur.fetchone()[0])
            cur.execute(
                "SELECT table_name, column_name FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = ANY(%s) "
                "AND data_type = ANY(%s) ORDER BY table_name, column_name",
                (list(RESIDENCY_SCAN_TABLES), list(TEXT_COLUMN_TYPES)),
            )
            columns = cur.fetchall()
            for table, column in columns:
                cur.execute(
                    sql.SQL("SELECT count(*) FROM {} WHERE {}::text LIKE ANY(%s)").format(
                        sql.Identifier(table), sql.Identifier(column)
                    ),
                    (patterns,),
                )
                hits = int(cur.fetchone()[0])
                if hits:
                    leaks[f"{table}.{column}"] = hits
    except Exception as exc:  # driver/schema errors: the database could not be measured
        return make_check(
            "MIG06_RESIDENCY", UNMEASURED, f"residency scan failed on {target}: {exc}"
        )
    measured = {
        "target_database": target,
        "classified_values_scanned": len(values),
        "classified_streams": sorted(by_stream),
        "migrated_rows_in_scope": migrated_rows,
        "tables_scanned": sorted({table for table, _ in columns}),
        "columns_scanned": len(columns),
        "plaintext_leaks": leaks,
    }
    if not columns or migrated_rows == 0:
        return make_check(
            "MIG06_RESIDENCY",
            UNMEASURED,
            "nothing migrated to scan (no classified-stream rows / migrated tables in the target)",
            **measured,
        )
    if leaks:
        detail = f"plaintext classified values found in {sorted(leaks)}"
        return make_check("MIG06_RESIDENCY", FAIL, detail, **measured)
    detail = (
        f"{len(values)} classified values absent from {len(columns)} text columns "
        f"over {migrated_rows} migrated rows"
    )
    return make_check("MIG06_RESIDENCY", PASS, detail, **measured)


def measure_migration(extracts_dir: Path = EXTRACTS_DIR, connect: Connector | None = None) -> dict:
    """Run every locally observable migration measurement (shared with R11-M01-T02)."""
    connect = connect or connect_rehearsal_db
    manifest, manifest_error = read_json(extracts_dir / MANIFEST_NAME)
    loaded, loaded_error = read_json(extracts_dir / LOADED_NAME)
    if loaded is not None and not isinstance(loaded, dict):
        loaded, loaded_error = None, f"{LOADED_NAME} is not a JSON object"
    conn = target = conn_error = None
    try:
        conn, target = connect()
    except Exception as exc:  # any driver/config failure: the database is not observable
        conn_error = f"{type(exc).__name__}: {str(exc).strip()}"
    try:
        if isinstance(manifest, dict):
            extract_checks = measure_extracts(extracts_dir, manifest)
        else:
            reason = manifest_error or f"{MANIFEST_NAME} is not a JSON object"
            extract_checks = [make_check("MIG02_MANIFEST", FAIL, reason)]
            manifest = {}
        totals_check = measure_control_totals(manifest, loaded, loaded_error)
        live_check = measure_live_counts(loaded, conn, target, conn_error)
        residency_check = measure_residency(extracts_dir, manifest, conn, target, conn_error)
    finally:
        if conn is not None:
            conn.close()
    return {
        "run_id": manifest.get("run"),
        "manifest": manifest,
        "loaded": loaded,
        "target_database": target,
        "extract_checks": extract_checks,
        "control_totals_check": totals_check,
        "live_counts_check": live_check,
        "residency_check": residency_check,
    }


def production_volume_check(measured: dict, check_id: str = "MG005_PRODUCTION_VOLUME") -> dict:
    control = measured["manifest"].get("control_totals") or {}
    records = sum(v for v in control.values() if isinstance(v, int))
    return make_check(
        check_id,
        UNMEASURED,
        f"the committed rehearsal run {measured['run_id']!r} is {records} records over "
        f"{len(control)} streams on the local rehearsal target; a production-volume run on "
        "migration-staging is not observable by this tool",
        local_records=records,
        local_streams=len(control),
    )


def rollback_check() -> dict:
    return make_check(
        "MG007_ROLLBACK",
        UNMEASURED,
        "MG-007 rollback (migrations/rollback.py) deletes migrated rows; this measure-only "
        "tool never runs it and no rollback-rehearsal record from migration-staging exists",
    )


def signoff_check(measured: dict, check_id: str = "MG004_BUSINESS_SIGNOFF") -> dict:
    loaded = measured["loaded"] or {}
    quarantined = {
        stream: n
        for stream, n in (loaded.get("quarantined_records") or {}).items()
        if isinstance(n, int) and n
    }
    return make_check(
        check_id,
        UNMEASURED,
        "requires the named business owner's signature on this measured reconciliation "
        f"(and a steward disposition of every quarantined record: {quarantined or 'none'}); "
        "no signed record exists",
        quarantined_records=quarantined,
    )


def run(
    extracts_dir: Path = EXTRACTS_DIR,
    evidence_dir: Path = EVIDENCE_DIR,
    connect: Connector | None = None,
) -> dict:
    measured = measure_migration(extracts_dir, connect)
    signoff = signoff_check(measured)
    checks = [
        production_volume_check(measured),
        *measured["extract_checks"],
        measured["control_totals_check"],
        measured["live_counts_check"],
        measured["residency_check"],
        rollback_check(),
        signoff,
    ]
    verdict = overall_verdict(checks)
    reconciliation = [*measured["extract_checks"], measured["control_totals_check"]]
    now = datetime.now(UTC).isoformat()

    # MG-004 sign-off REQUEST: the measured reconciliation awaiting a named signature.
    signoff_record = {
        "governance_standard": "MG-004",
        "run_id": measured["run_id"],
        "prepared_at": now,
        "verdict": signoff["status"],
        "reason": signoff["detail"],
        "signatory": None,
        "measured_reconciliation_verdict": overall_verdict(reconciliation),
        "measured_reconciliation": measured["control_totals_check"].get("streams"),
        "quarantined_records": signoff["quarantined_records"],
        "decommission_authorization": None,
    }
    write_json(evidence_dir / SIGNOFF_NAME, signoff_record)

    evidence = {
        "milestone": "R10-M05",
        "task": "R10-M05-T02",
        "tool": "tooling/scripts/run_production_migration_rehearsal.py",
        "run_id": measured["run_id"],
        "measured_at": now,
        "status": verdict,
        "gp_11_discharged": verdict == PASS,
        "summary": count_statuses(checks),
        "checks": checks,
        "volume_loaded": (measured["loaded"] or {}).get("loaded_totals"),
        "business_signoff_file": f"docs/traceability/evidence/{SIGNOFF_NAME}",
    }
    write_json(evidence_dir / EVIDENCE_NAME, evidence)
    return evidence


def main() -> int:
    logger.info("Measuring production migration rehearsal evidence (MG-005 / GP-11)")
    evidence = run()
    for check in evidence["checks"]:
        logger.info("[%s] %s: %s", check["status"], check["id"], check["detail"])
    logger.info(
        "Verdict: %s (gp_11_discharged=%s) -> %s",
        evidence["status"],
        evidence["gp_11_discharged"],
        EVIDENCE_DIR / EVIDENCE_NAME,
    )
    return exit_code(evidence["status"])


if __name__ == "__main__":
    sys.exit(main())
