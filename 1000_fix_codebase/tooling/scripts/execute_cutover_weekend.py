#!/usr/bin/env python3
"""execute_cutover_weekend.py — Milestone R11-M01 Task T03 (execution record, measure-only).

Records the RB-53 production cutover weekend:
  1. Freeze legacy sources & engage maintenance landing mode
  2. Final incremental delta capture
  3. Production database ingestion & MIG-02 control totals verification
  4. 15/15 critical user journey smoke test gates
  5. 53/53 branch heartbeat handshake check
  6. Business sign-off & traffic unfreeze

GV-009: the previous version logged every step "PASS" (with invented delta
counts, control totals, smoke results, branch heartbeats and signatures) without
any of it happening. A production cutover is an event in the production estate
that this tool cannot observe, so every cutover step is UNMEASURED with its
reason; only the entry preconditions it can check locally are measured:
  PRE-01-RUNBOOK    RB-53 master runbook present; its smoke-gate journey table
                    is the gate scope (no hard-coded journey list)
  PRE-02-REHEARSAL  the R11-M01-T02 final rehearsal evidence verdict

The tool never touches the estate (no freeze, DNS switch or load). Outputs:
  docs/traceability/evidence/r11-m01-cutover-execution-evidence.json
  docs/traceability/r11-m01-cutover-execution-log.md

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a step is UNMEASURED).
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

CODEBASE_ROOT = Path(__file__).resolve().parents[2]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cutover_weekend")

EVIDENCE_DIR = CODEBASE_ROOT / "docs" / "traceability" / "evidence"
TRACEABILITY_DIR = CODEBASE_ROOT / "docs" / "traceability"
RUNBOOK_PATH = CODEBASE_ROOT / "docs" / "runbooks" / "RB-53-production-cutover-master-runbook.md"
REHEARSAL_EVIDENCE_NAME = "r11-m01-final-volume-rehearsal.json"
EVIDENCE_NAME = "r11-m01-cutover-execution-evidence.json"
LOG_NAME = "r11-m01-cutover-execution-log.md"

PASS = "PASS"  # noqa: S105 - a verdict label, not a credential
FAIL = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

PRODUCTION_EVENT = (
    "production cutover event - not observable by this tool; requires the "
    "Incident Commander's timestamped execution record from the production estate"
)

# RB-53 cutover steps: (step id, description, why it cannot be measured here).
CUTOVER_STEPS = (
    (
        "STEP-01-FREEZE",
        "Legacy databases set to read-only; edge maintenance page activated",
        PRODUCTION_EVENT,
    ),
    (
        "STEP-02-DELTA",
        "Capture final transactional deltas across legacy sources",
        PRODUCTION_EVENT,
    ),
    (
        "STEP-03-INGEST",
        "Execute production ingestion pipeline into the production PostgreSQL cluster",
        PRODUCTION_EVENT,
    ),
    (
        "STEP-04-MIG02",
        "MIG-02 control totals verification of the production load",
        "requires the production load report and a read-only count in the production "
        "database; neither is reachable from this tool",
    ),
    (
        "STEP-05-SMOKE",
        "Critical-journey smoke gates against the production database",
        "requires the smoke-gate run results against production; none recorded",
    ),
    (
        "STEP-06-BRANCHES",
        "Service centre POS & workshop terminal heartbeat check",
        "requires live heartbeats from production branch terminals; none observable here",
    ),
    (
        "STEP-07-SIGNOFF",
        "Incident Commander & Steering Committee final authorization",
        "requires named human signatures; no signed authorization exists",
    ),
    (
        "STEP-08-UNFREEZE",
        "Deactivate maintenance mode; switch DNS to the production cluster",
        PRODUCTION_EVENT,
    ),
)

# RB-53 section 4 smoke-gate table rows: | `J01` | Customer Online Booking | ... |
JOURNEY_ROW = re.compile(r"^\|\s*`(J\d{2})`\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)


def make_step(step_id: str, description: str, status: str, detail: str) -> dict:
    return {
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "step": step_id,
        "description": description,
        "verdict": status,
        "detail": detail,
    }


def overall_verdict(steps: list[dict]) -> str:
    statuses = {step["verdict"] for step in steps}
    if not statuses:
        return UNMEASURED
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def check_runbook(runbook_path: Path) -> tuple[dict, list[str]]:
    """PRE-01: RB-53 exists and declares the smoke-gate journeys (returned as the gate scope)."""
    description = "RB-53 master cutover runbook present with its smoke-gate journey table"
    if not runbook_path.exists():
        step = make_step("PRE-01-RUNBOOK", description, FAIL, f"{runbook_path.name} missing")
        return step, []
    text = runbook_path.read_text(encoding="utf-8", errors="replace")
    journeys = [f"{jid}: {name}" for jid, name in JOURNEY_ROW.findall(text)]
    missing = [t for t in ("RB-53", "Freeze", "Smoke", "Rollback") if t.lower() not in text.lower()]
    if not journeys:
        missing.append("smoke-gate journey table")
    if missing:
        step = make_step(
            "PRE-01-RUNBOOK", description, FAIL, f"{runbook_path.name} lacks {missing}"
        )
        return step, journeys
    detail = f"{runbook_path.name} present; {len(journeys)} smoke-gate journeys declared"
    return make_step("PRE-01-RUNBOOK", description, PASS, detail), journeys


def check_rehearsal(evidence_path: Path) -> dict:
    description = "R11-M01-T02 final full-volume rehearsal verdict (cutover entry criterion)"
    try:
        data = json.loads(evidence_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return make_step(
            "PRE-02-REHEARSAL", description, UNMEASURED, f"{evidence_path.name} not found"
        )
    except (OSError, ValueError) as exc:
        return make_step("PRE-02-REHEARSAL", description, FAIL, f"unreadable: {exc}")
    rehearsal_status = data.get("status") if isinstance(data, dict) else None
    status = {PASS: PASS, FAIL: FAIL}.get(rehearsal_status, UNMEASURED)
    return make_step(
        "PRE-02-REHEARSAL",
        description,
        status,
        f"{evidence_path.name} status = {rehearsal_status!r}",
    )


def _shown(value: object) -> str:
    return "not measured" if value is None else str(value)


def render_log(evidence: dict) -> str:
    verdict = evidence["status"]
    lines = [
        "# 1000FiX Services Ltd. — Enterprise ERP v2.0",
        "## Production Cutover Weekend Execution Record (R11-M01-T03)",
        "",
        f"**Recorded at**: {evidence['measured_at']}",
        "**Runbook Ref**: `RB-53-PRODUCTION-CUTOVER-MASTER`",
        f"**Computed status**: {verdict}",
        f"**Tool**: `{evidence['tool']}` (GV-009: every status below is computed in this run)",
        "",
        "---",
        "",
        "### Step Record",
        "",
        "| Recorded | Step ID | Description | Status | Details |",
        "|---|---|---|---|---|",
    ]
    for e in evidence["steps_executed"]:
        lines.append(
            f"| {e['timestamp']} | `{e['step']}` | {e['description']} | {e['verdict']} | {e['detail']} |"
        )
    smoke = evidence["smoke_gate"]
    branches = evidence["branch_readiness"]
    lines += [
        "",
        "---",
        "",
        "### Verification Summary",
        f"- **Steps**: {evidence['summary']['pass']} PASS / {evidence['summary']['fail']} FAIL / "
        f"{evidence['summary']['unmeasured']} UNMEASURED.",
        f"- **MIG-02 control totals (production load)**: {evidence['control_totals']['status']}.",
        f"- **Smoke gate**: {smoke['verdict']} (passed journeys: "
        f"{_shown(smoke['passed_journeys'])} of {smoke['total_journeys']} in RB-53).",
        f"- **Branch heartbeats**: {branches['status']} (online centres: "
        f"{_shown(branches['online_service_centres'])}).",
        f"- **Live traffic**: {evidence['live_traffic_status']}.",
        "",
        "### Sign-off",
        "",
    ]
    if verdict == PASS:
        lines.append("All cutover steps and sign-offs were measured as passed in this run.")
    else:
        lines.append(
            f"Not signed: the computed status is {verdict}. A cutover record can only be "
            "certified from the production execution evidence and named signatures."
        )
    return "\n".join(lines) + "\n"


def execute_cutover(
    evidence_dir: Path = EVIDENCE_DIR,
    traceability_dir: Path = TRACEABILITY_DIR,
    runbook_path: Path = RUNBOOK_PATH,
) -> tuple[dict, str]:
    runbook_step, journeys = check_runbook(runbook_path)
    steps = [
        runbook_step,
        check_rehearsal(evidence_dir / REHEARSAL_EVIDENCE_NAME),
        *(make_step(sid, desc, UNMEASURED, why) for sid, desc, why in CUTOVER_STEPS),
    ]
    verdict = overall_verdict(steps)
    by_id = {step["step"]: step for step in steps}
    evidence = {
        "milestone": "R11-M01",
        "task": "R11-M01-T03",
        "title": "Production Cutover Weekend Execution Record",
        "tool": "tooling/scripts/execute_cutover_weekend.py",
        "measured_at": datetime.now(UTC).isoformat(),
        "status": verdict,
        "summary": {
            s.lower(): sum(1 for step in steps if step["verdict"] == s)
            for s in (PASS, FAIL, UNMEASURED)
        },
        "steps_executed": steps,
        "control_totals": {
            "status": by_id["STEP-04-MIG02"]["verdict"],
            "totals": None,
        },
        "smoke_gate": {
            "journeys": journeys,
            "total_journeys": len(journeys),
            "passed_journeys": None,
            "failed_journeys": None,
            "verdict": by_id["STEP-05-SMOKE"]["verdict"],
        },
        "branch_readiness": {
            "online_service_centres": None,
            "status": by_id["STEP-06-BRANCHES"]["verdict"],
        },
        "live_traffic_status": by_id["STEP-08-UNFREEZE"]["verdict"],
    }
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / EVIDENCE_NAME
    evidence_path.write_bytes((json.dumps(evidence, indent=2) + "\n").encode("utf-8"))
    traceability_dir.mkdir(parents=True, exist_ok=True)
    log_md_path = traceability_dir / LOG_NAME
    log_md_path.write_bytes(render_log(evidence).encode("utf-8"))
    return evidence, str(log_md_path)


def main() -> int:
    evidence, log_path = execute_cutover()
    for step in evidence["steps_executed"]:
        logger.info("[%s] %s: %s", step["verdict"], step["step"], step["detail"])
    logger.info("Cutover record verdict: %s -> %s, %s", evidence["status"], EVIDENCE_NAME, log_path)
    return exit_code(evidence["status"])


if __name__ == "__main__":
    sys.exit(main())
