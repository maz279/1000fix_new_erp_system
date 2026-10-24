#!/usr/bin/env python3
"""
demonstrate-walkin-intake.py - Milestone R02-M05 Task T02 (Gate G1-02 Evidence):
Measure the 3-minute branch walk-in intake flow from fix_walkin_intake records and emit
evidence to tooling/fitness/evidence/walkin-intake-timing-latest.json.

GV-009 (measure, never fabricate). An earlier version of this script INSERTED ten rows with
random.randint(110, 142) "durations" and a hard-coded PASS / 100% compliance / named staff.
This version is READ-ONLY (a read-only Postgres session; no DDL, no INSERT):

- `application_recorded_intake_timings`: completed intakes are read from fix_walkin_intake;
  each duration is recomputed from intake_start -> handover_complete and cross-checked with the
  stored intake_duration_seconds. Rows matching the signature of the rows the earlier version
  synthesised are excluded and counted. FAIL if any measured intake exceeds the 180 s target or
  is internally inconsistent; UNMEASURED if the DB is unreachable or fewer than MIN_RUNS
  qualifying intakes exist; PASS otherwise.
- `branch_staff_demonstration`: G1-02 requires the intake to be performed by branch staff at a
  pilot branch. fix.walkin.intake records no staff-role attestation (access is base.group_user)
  and the local DB is synthetic-only (DE-12), so this is UNMEASURED - it needs a human-observed
  pilot session.

Overall verdict: FAIL if any check FAILs, else INCOMPLETE while anything is UNMEASURED.
Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5433"))
DB_NAME = os.environ.get("PGDATABASE", "fix_dev")
DB_USER = os.environ.get("PGUSER", "fix")
DB_PASS = os.environ.get("PGPASSWORD", "change-me-dev-only")
CONNECT_TIMEOUT_S = 5

CODEBASE_DIR = Path(__file__).resolve().parent.parent.parent
EVIDENCE_FILE = (
    CODEBASE_DIR / "tooling" / "fitness" / "evidence" / "walkin-intake-timing-latest.json"
)

TARGET_SECONDS = 180
MIN_RUNS = 10
DURATION_TOLERANCE_S = 1

# Signature of the rows the earlier (fabricating) version of this script inserted:
# customer_statement = f"Customer stated: {fault}" with fault taken from this list.
# Such rows carry random durations, so they are excluded from every measurement.
SYNTHESISED_STATEMENT_PREFIX = "Customer stated: "
COMMON_FAULTS = [
    "Display flickering and vertical green lines after drop",
    "Device not charging, loose USB-C port connection",
    "Battery draining rapidly, device overheating on idle",
    "Touch digitizer unresponsive on lower third of screen",
    "Rear camera module blurry, optical stabilization error",
    "Audio speaker crackling at volume above 50%",
    "Power button jammed, intermittent restart loop",
    "Liquid exposure, device fails to power on",
]

EXIT_CODES = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}

COMPLETED_INTAKES_SQL = """
    SELECT id, intake_start, handover_complete, intake_duration_seconds,
           handover_acknowledged, handover_method, fault_description,
           customer_statement, state
    FROM fix_walkin_intake
    WHERE state = 'completed' AND handover_complete IS NOT NULL
    ORDER BY id
"""


def overall_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if "FAIL" in statuses:
        return "FAIL"
    if any(s != "PASS" for s in statuses):
        return "INCOMPLETE"
    return "PASS"


def fetch_completed_intakes(connect=None) -> list[dict]:
    """Read completed intakes in a READ-ONLY session. Raises on any connection/query error."""
    if connect is None:
        import psycopg2

        connect = psycopg2.connect
    from psycopg2.extras import RealDictCursor

    conn = connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=CONNECT_TIMEOUT_S,
    )
    try:
        conn.set_session(readonly=True)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT to_regclass('fix_walkin_intake') AS t")
            if not cur.fetchone()["t"]:
                raise LookupError("table fix_walkin_intake is not present in the database")
            cur.execute(COMPLETED_INTAKES_SQL)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def is_synthesised(row: dict) -> bool:
    statement = row.get("customer_statement") or ""
    return (
        statement.startswith(SYNTHESISED_STATEMENT_PREFIX)
        and row.get("fault_description") in COMMON_FAULTS
    )


def measure_intakes(rows: list[dict]) -> tuple[dict, list[dict], dict]:
    """Return (check, measured_runs, stats) for the completed intake rows."""
    excluded = [r["id"] for r in rows if is_synthesised(r)]
    runs: list[dict] = []
    for row in rows:
        if is_synthesised(row):
            continue
        problems: list[str] = []
        start, end = row["intake_start"], row["handover_complete"]
        duration = (end - start).total_seconds()
        stored = row.get("intake_duration_seconds")
        if duration < 0:
            problems.append("handover_complete precedes intake_start")
        if stored is None or abs(stored - duration) > DURATION_TOLERANCE_S:
            problems.append(f"stored intake_duration_seconds {stored} != measured {duration:.0f}")
        if not row.get("handover_acknowledged"):
            problems.append("handover not acknowledged")
        within = 0 <= duration < TARGET_SECONDS
        if not within:
            problems.append(f"duration {duration:.0f}s not under {TARGET_SECONDS}s target")
        runs.append(
            {
                "intake_id": row["id"],
                "intake_start": start.isoformat(),
                "handover_complete": end.isoformat(),
                "duration_seconds": round(duration, 1),
                "stored_duration_seconds": stored,
                "acknowledged_method": row.get("handover_method"),
                "within_target": within,
                "status": "FAIL" if problems else "PASS",
                "problems": problems,
            }
        )

    durations = [r["duration_seconds"] for r in runs]
    stats = {
        "qualifying_intakes": len(runs),
        "excluded_synthesised_records": len(excluded),
        "excluded_synthesised_ids": excluded,
        "mean_duration_seconds": round(sum(durations) / len(durations), 1) if durations else None,
        "min_duration_seconds": min(durations) if durations else None,
        "max_duration_seconds": max(durations) if durations else None,
        "compliance_pct": (
            round(100.0 * sum(1 for r in runs if r["within_target"]) / len(runs), 1)
            if runs
            else None
        ),
    }
    failing = [r["intake_id"] for r in runs if r["status"] == "FAIL"]
    if failing:
        status = "FAIL"
        detail = f"{len(failing)} of {len(runs)} measured intakes failed: ids {failing}"
    elif len(runs) < MIN_RUNS:
        status = "UNMEASURED"
        detail = (
            f"only {len(runs)} application-recorded completed intake(s) (need {MIN_RUNS}); "
            f"{len(excluded)} row(s) excluded as synthesised by an earlier version of this script"
        )
    else:
        status = "PASS"
        detail = f"{len(runs)} measured intakes all under {TARGET_SECONDS}s"
    check = {"check": "application_recorded_intake_timings", "status": status, "detail": detail}
    return check, runs, stats


def run_measurement(fetch=None) -> dict:
    checks: list[dict] = []
    runs: list[dict] = []
    stats: dict = {}
    try:
        rows = (fetch or fetch_completed_intakes)()
    except Exception as exc:  # unreachable DB / missing table -> UNMEASURED, never PASS
        checks.append(
            {
                "check": "application_recorded_intake_timings",
                "status": "UNMEASURED",
                "detail": f"cannot read fix_walkin_intake ({DB_HOST}:{DB_PORT}/{DB_NAME}): "
                f"{type(exc).__name__}: {exc}",
            }
        )
    else:
        check, runs, stats = measure_intakes(rows)
        checks.append(check)
    checks.append(
        {
            "check": "branch_staff_demonstration",
            "status": "UNMEASURED",
            "detail": (
                "G1-02 requires intakes performed by branch staff at a pilot branch; "
                "fix.walkin.intake records no staff-role attestation and the local DB is "
                "synthetic-only (DE-12) - needs a human-observed pilot session"
            ),
        }
    )
    verdict = overall_verdict([c["status"] for c in checks])
    return {
        "milestone": "R02-M05",
        "task": "R02-M05-T02",
        "gate_criterion": "G1-02",
        "verdict": verdict,
        "target_seconds": TARGET_SECONDS,
        "min_runs_required": MIN_RUNS,
        "source": f"read-only SELECT on fix_walkin_intake @ {DB_HOST}:{DB_PORT}/{DB_NAME}",
        "recorded_at": datetime.now(UTC).isoformat(),
        "checks": checks,
        **stats,
        "runs": runs,
    }


def main() -> int:
    print("================================================================================")
    print("  1000FiX ERP v2.0 - Walk-in Intake 3-Minute Measurement (G1-02)")
    print("  Read-only: durations measured from fix_walkin_intake timestamps")
    print("================================================================================")

    evidence = run_measurement()
    for r in evidence["runs"]:
        print(
            f"Intake #{r['intake_id']}: {r['duration_seconds']}s "
            f"(stored {r['stored_duration_seconds']}) [{r['status']}]"
        )
    print("--------------------------------------------------------------------------------")
    for c in evidence["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")
    if evidence.get("qualifying_intakes"):
        print(
            f"  Mean {evidence['mean_duration_seconds']}s, max {evidence['max_duration_seconds']}s, "
            f"compliance {evidence['compliance_pct']}% over {evidence['qualifying_intakes']} intakes"
        )
    print("--------------------------------------------------------------------------------")

    EVIDENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(evidence, f, indent=2)

    print(f"[{evidence['verdict']}] Evidence JSON saved to: {EVIDENCE_FILE}")
    print("================================================================================")
    return EXIT_CODES.get(evidence["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
