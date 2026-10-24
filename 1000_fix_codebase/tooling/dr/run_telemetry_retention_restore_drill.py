#!/usr/bin/env python3
"""
run_telemetry_retention_restore_drill.py — Telemetry Retention & Restore Drill
Milestone R09-M03 Task T03: GPS/telemetry retention and compression policy
(420M rows/year storage decision) and prove restore.

GV-009: this runner never connects to a database, so it never reports a
compression ratio, row count, checksum or restore throughput it did not
observe.

Measured (read-only inspection of migrations/sql/timescaledb_telemetry_hypertable.sql,
SQL comments stripped, and of the scheduler DAGs under dags/):
1. D-030 licence: no TSL-only TimescaleDB feature is called (native compression,
   add_*_policy, add_job, continuous aggregates) and the DDL refuses a server
   whose timescaledb.license is not 'apache'
2. 90-day retention: an Apache-2.0 drop_chunks() wrapper over the hypertable
3. the retention wrapper is actually scheduled (a DAG calls it)
4. the 7-day columnar compression the requirement asks for - TSL-only, so it
   FAILs under D-030 until an ADR re-decides the storage footprint
5. an archival step runs before the retention drop

UNMEASURED: the achieved compression ratio, the cold-archive chunk export and
the restore into a staging hypertable with row-count + checksum matching
(all need a populated TimescaleDB and an archived chunk).

The 420M rows/year capacity model is reported as a projection from stated
planning assumptions; it is not a measurement and is not a check.

Verdict: FAIL if any check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check was measured and passed.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.

Outputs structured evidence to:
  docs/traceability/evidence/r09-m03-retention-restore-drill.json
"""

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = ROOT_DIR / "docs" / "traceability" / "evidence"
DDL_PATH = ROOT_DIR / "migrations" / "sql" / "timescaledb_telemetry_hypertable.sql"
EVIDENCE_FILE = "r09-m03-retention-restore-drill.json"
HYPERTABLE = "fix_technician_telemetry"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"
EXIT_CODES = {PASS: 0, FAIL: 1}
NO_DATABASE = (
    f"requires a running TimescaleDB with {HYPERTABLE} populated; this tool never connects to "
    "or restores into a database"
)

COMPRESSION_TARGET_PCT = 85.0
DAGS_DIR = ROOT_DIR / "dags"
RETENTION_FUNCTION = "fix_telemetry_apply_retention"
TSL_FEATURE_RES = {
    "native compression": re.compile(
        r"\btimescaledb\.compress\b|\bcompress_chunk\s*\(|\badd_compression_policy\s*\(",
        re.IGNORECASE,
    ),
    "retention policy": re.compile(r"\badd_retention_policy\s*\(", re.IGNORECASE),
    "continuous aggregate": re.compile(
        r"timescaledb\.continuous\b|\badd_continuous_aggregate_policy\s*\(", re.IGNORECASE
    ),
    "reorder policy": re.compile(r"\badd_reorder_policy\s*\(", re.IGNORECASE),
    "job scheduler": re.compile(r"\badd_job\s*\(", re.IGNORECASE),
}
LICENCE_GUARD_RE = re.compile(
    r"current_setting\(\s*'timescaledb\.license'[^)]*\)[^;]*?(?:<>|!=)\s*'apache'"
    r"[\s\S]*?raise\s+exception",
    re.IGNORECASE,
)
RETENTION_FUNCTION_RE = re.compile(
    rf"create\s+(?:or\s+replace\s+)?function\s+{RETENTION_FUNCTION}\s*\("
    r"[\s\S]*?interval\s*'90 days'[\s\S]*?"
    rf"drop_chunks\s*\(\s*'{HYPERTABLE}'",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- helpers
def _result(
    check_id: str, name: str, problems: list[str], unknowns: list[str], detail: str
) -> dict:
    """FAIL on any problem, UNMEASURED on anything not observable, else PASS."""
    if problems:
        status, detail = FAIL, "; ".join(problems)
    elif unknowns:
        status, detail = UNMEASURED, "; ".join(unknowns)
    else:
        status = PASS
    return {"id": check_id, "name": name, "status": status, "detail": detail}


def _unmeasured(check_id: str, name: str, reason: str) -> dict:
    return _result(check_id, name, [], [reason], "")


def overall_verdict(checks: list[dict]) -> str:
    statuses = [c["status"] for c in checks]
    if FAIL in statuses:
        return FAIL
    if not statuses or UNMEASURED in statuses:
        return INCOMPLETE
    return PASS


def _summary(checks: list[dict]) -> dict:
    return {
        "checks_total": len(checks),
        "checks_passed": sum(c["status"] == PASS for c in checks),
        "checks_failed": sum(c["status"] == FAIL for c in checks),
        "checks_unmeasured": sum(c["status"] == UNMEASURED for c in checks),
    }


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return path.as_posix()


def _read_ddl() -> tuple[str, str | None]:
    """The hypertable DDL without `--` comments, or the reason it is unavailable."""
    if not DDL_PATH.is_file():
        return "", f"{DDL_PATH.name} not found"
    try:
        text = DDL_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        return "", f"{DDL_PATH.name} unreadable: {exc}"
    return re.sub(r"/\*[\s\S]*?\*/|--[^\n]*", "", text), None


def _scheduler_sources() -> dict[str, str]:
    """Scheduler definitions (DAG modules) that could run the retention wrapper."""
    if not DAGS_DIR.is_dir():
        return {}
    return {
        _display_path(p): p.read_text(encoding="utf-8", errors="ignore")
        for p in sorted(DAGS_DIR.glob("*.py"))
    }


# --------------------------------------------------------------------------- capacity model
def calculate_storage_model() -> dict:
    """Projected 420M rows/year footprint. Every input is a planning assumption."""
    annual_rows = 420_000_000
    daily_rows = int(annual_rows / 365)
    bytes_per_row = 128
    index_overhead_ratio = 0.45
    assumed_compression_pct = 87.5
    compressed_index_ratio = 0.20
    retention_days = 90

    raw_data_gb_year = (annual_rows * bytes_per_row) / (1024**3)
    index_overhead_gb = raw_data_gb_year * index_overhead_ratio
    total_uncompressed_gb_year = raw_data_gb_year + index_overhead_gb
    compressed_data_gb_year = raw_data_gb_year * (1 - assumed_compression_pct / 100)
    total_compressed_gb_year = compressed_data_gb_year + index_overhead_gb * compressed_index_ratio

    return {
        "basis": "projection from planning assumptions - not measured",
        "assumptions": {
            "annual_volume_rows": annual_rows,
            "bytes_per_row_avg": bytes_per_row,
            "index_overhead_ratio": index_overhead_ratio,
            "compression_ratio_pct": assumed_compression_pct,
            "compressed_index_ratio": compressed_index_ratio,
            "active_window_days": retention_days,
        },
        "daily_chunk_rows": daily_rows,
        "projected_uncompressed_gb_year": round(total_uncompressed_gb_year, 2),
        "projected_compressed_gb_year": round(total_compressed_gb_year, 2),
        "projected_active_table_rows": daily_rows * retention_days,
        "projected_active_table_compressed_gb": round(
            total_compressed_gb_year / 365 * retention_days, 2
        ),
    }


# --------------------------------------------------------------------------- checks
def check_licence_d030(ddl: str, error: str | None) -> dict:
    problems = [error] if error else []
    if not error:
        used = [name for name, rx in TSL_FEATURE_RES.items() if rx.search(ddl)]
        if used:
            problems.append(
                f"TSL-only TimescaleDB features called (D-030 breach): {', '.join(used)}"
            )
        if not LICENCE_GUARD_RE.search(ddl):
            problems.append(
                "the DDL does not refuse a server whose timescaledb.license is not 'apache'"
            )
    return _result(
        "licence_d030",
        "Apache-2.0 TimescaleDB features only (D-030)",
        problems,
        [],
        f"{DDL_PATH.name}: no TSL feature called; refuses non-'apache' timescaledb.license",
    )


def check_compression_policy(ddl: str, error: str | None) -> dict:
    problems = [error] if error else []
    if not error:
        problems.append(
            "the 7-day columnar compression the requirement asks for is TSL-only and D-030 "
            "allows Apache-2.0 TimescaleDB features only - not achievable as specified; needs an "
            "ADR re-deciding the 420M rows/year storage footprint"
        )
    return _result("compression_policy", "7-day columnar compression policy", problems, [], "")


def check_retention_policy(ddl: str, error: str | None) -> dict:
    problems = [error] if error else []
    if not error and not RETENTION_FUNCTION_RE.search(ddl):
        problems.append(
            f"no {RETENTION_FUNCTION}() wrapping drop_chunks('{HYPERTABLE}') with a 90-day window"
        )
    return _result(
        "retention_policy",
        "90-day retention (Apache-2.0 drop_chunks wrapper) declared",
        problems,
        [],
        f"{DDL_PATH.name}: {RETENTION_FUNCTION}() drops chunks older than INTERVAL '90 days'",
    )


def check_retention_schedule(sources: dict[str, str]) -> dict:
    scheduled = [
        path
        for path, text in sources.items()
        if RETENTION_FUNCTION in text and re.search(r"schedule\s*=\s*['\"]", text)
    ]
    problems = (
        []
        if scheduled
        else [f"no scheduler DAG calls {RETENTION_FUNCTION}() - retention would never run"]
    )
    return _result(
        "retention_schedule",
        "Retention wrapper scheduled by the platform scheduler",
        problems,
        [],
        f"scheduled by {', '.join(scheduled)}",
    )


def check_archive_before_drop(sources: dict[str, str]) -> dict:
    archiving = [
        path
        for path, text in sources.items()
        if RETENTION_FUNCTION in text
        and re.search(r"archiv", text, re.IGNORECASE)
        and re.search(r"task_id\s*=\s*['\"][^'\"]*archiv", text, re.IGNORECASE)
    ]
    problems = (
        []
        if archiving
        else [
            "no archival task runs before the retention drop: chunks past the 90-day window are "
            "dropped with no cold-archive copy"
        ]
    )
    return _result(
        "archive_before_drop",
        "Chunks archived to cold storage before the retention drop",
        problems,
        [],
        f"archival task declared in {', '.join(archiving)}",
    )


def drill_checks() -> list[dict]:
    return [
        _unmeasured(
            "compression_ratio",
            f"Achieved compression > {COMPRESSION_TARGET_PCT:g}% (hypertable_compression_stats)",
            NO_DATABASE + " and compressed chunks",
        ),
        _unmeasured(
            "chunk_archive_export",
            "Chunk exported to the cold archive with a manifest checksum",
            "no archived chunk artefact exists to inspect; needs the archival job and cold storage",
        ),
        _unmeasured(
            "restore_to_staging",
            "Archived chunk restored into a staging hypertable (row count + SHA-256 match)",
            NO_DATABASE + " and an archived chunk to restore",
        ),
    ]


def execute_restore_drill() -> dict:
    ddl, error = _read_ddl()
    sources = _scheduler_sources()
    checks = [
        check_licence_d030(ddl, error),
        check_retention_policy(ddl, error),
        check_retention_schedule(sources),
        check_compression_policy(ddl, error),
        check_archive_before_drop(sources),
        *drill_checks(),
    ]
    verdict = overall_verdict(checks)
    summary = _summary(checks)
    return {
        "milestone": "R09-M03",
        "task": "R09-M03-T03",
        "standard": "GPS/Telemetry Retention & Compression Policy / 420M Rows Storage Decision / Restore Drill",
        "timestamp": datetime.now(UTC).isoformat(),
        "ddl": _display_path(DDL_PATH),
        "storage_model": calculate_storage_model(),
        "restore_verification": {
            "target_table": f"{HYPERTABLE}_restore_staging",
            "expected_records": None,
            "restored_records": None,
            "checksum_verified": None,
            "status": next(c["status"] for c in checks if c["id"] == "restore_to_staging"),
        },
        "summary": summary,
        "checks": checks,
        "status": verdict,
        "finding": (
            f"{verdict}: {summary['checks_passed']} passed, {summary['checks_failed']} failed, "
            f"{summary['checks_unmeasured']} UNMEASURED of {summary['checks_total']} checks."
        ),
    }


def main() -> int:
    print("Executing Telemetry Retention & Restore Drill (R09-M03-T03)...")
    evidence = execute_restore_drill()
    for check in evidence["checks"]:
        print(f"  [{check['status']}] {check['name']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes((json.dumps(evidence, indent=2) + "\n").encode("utf-8"))
    print(f"{evidence['finding']}\nEvidence written to {out_file}")
    return EXIT_CODES.get(evidence["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
