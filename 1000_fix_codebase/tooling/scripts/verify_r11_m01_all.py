#!/usr/bin/env python3
"""verify_r11_m01_all.py — Master Verifier for Milestone R11-M01: Cutover and Go-Live.

Validates all 5 milestone tasks:
  T01: Cutover runbook RB-53 & dry-walkthrough complete
  T02: Final full-volume rehearsal (counts, values, checksums) & pre-signature
  T03: Cutover weekend execution (freeze -> delta -> control totals -> smoke 15/15 -> unfreeze)
  T04: Hypercare stand-up SV-004 (24/7 on-call, SV-001 SLAs, Day-1 stability report)
  T05: Month-1 operational proofs (5-day close, Mushak 9.1, 380-employee payroll green)

GV-009: each task verdict comes from the CURRENT computed verdict of the
evidence its producing tool wrote (run_final_cutover_rehearsal.py,
execute_cutover_weekend.py) or from structural checks of the documents -
never from a success headline found in a document, and never from comparing
evidence with the figures a document promised (15 journeys, 53 centres, ...).
Human attestations (dry-walkthrough sign-off, named pre-signatures) are
UNMEASURED. Post-go-live claims (hypercare telemetry, month-1 proofs) cannot
stand while the cutover itself is not evidenced: they FAIL until T03 PASSes,
and are UNMEASURED production facts after that.
Overall: FAIL if any task FAILs, INCOMPLETE if any is INCOMPLETE, else PASS.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

CODEBASE_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = CODEBASE_ROOT / "docs" / "traceability" / "evidence"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_r11_m01")

PASS_WORDS = {"PASS", "PASSED", "GREEN", "SUCCESS"}
INCOMPLETE_WORDS = {"INCOMPLETE", "UNMEASURED", "CONDITION", "CONDITIONAL"}
VERDICT_KEYS = ("overall_status", "overall_verdict", "verdict", "status")

RB53_SECTIONS = (
    "RB-53-PRODUCTION-CUTOVER-MASTER",
    "Incident Commander",
    "T-48h",
    "T-4h",
    "Topological Source Load Ordering",
    "Smoke Gates",
    "Hard Rollback Triggers",
    "MG-007",
)


def normalise(value: object) -> str:
    word = str(value).strip().upper() if value is not None else ""
    if word in PASS_WORDS:
        return "PASS"
    if word in INCOMPLETE_WORDS:
        return "INCOMPLETE"
    return "FAIL"


def combine(*states: str) -> str:
    if any(s == "FAIL" for s in states):
        return "FAIL"
    if any(s == "INCOMPLETE" for s in states):
        return "INCOMPLETE"
    return "PASS"


def check(name: str, status: str, detail: str) -> dict:
    return {"check": name, "status": status, "detail": detail}


def read_json(path: Path) -> tuple[dict | None, str]:
    if not path.is_file():
        return None, f"{path.name} missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"{path.name} unreadable: {exc}"
    return (data, "") if isinstance(data, dict) else (None, f"{path.name} is not an object")


def evidence_verdict(data: dict) -> str:
    for key in VERDICT_KEYS:
        if isinstance(data.get(key), str):
            return normalise(data[key])
    return "FAIL"


def evidence_check(name: str, filename: str) -> tuple[dict, dict | None]:
    data, problem = read_json(EVIDENCE_DIR / filename)
    if data is None:
        return check(name, "FAIL", problem), None
    verdict = evidence_verdict(data)
    return check(name, verdict, f"{filename} currently states {verdict}"), data


def task(task_id: str, title: str, checks: list[dict], **extra) -> dict:
    status = combine(*(c["status"] for c in checks)) if checks else "FAIL"
    logger.info("Task %s: %s", task_id, status)
    for c in checks:
        if c["status"] != "PASS":
            logger.info("  [%s] %s: %s", c["status"], c["check"], c["detail"])
    return {"task_id": task_id, "title": title, "status": status, **extra, "checks": checks}


def verify_t01_cutover_runbook() -> dict:
    logger.info("--- [1/5] Verifying Task R11-M01-T01: Master Cutover Runbook (RB-53) ---")
    checks = []
    rb_path = CODEBASE_ROOT / "docs" / "runbooks" / "RB-53-production-cutover-master-runbook.md"
    trc_path = CODEBASE_ROOT / "docs" / "traceability" / "r11-m01-cutover-runbook.md"
    if rb_path.is_file():
        text = rb_path.read_text(encoding="utf-8")
        missing = [s for s in RB53_SECTIONS if s not in text]
        checks.append(
            check(
                "RB-53 runbook sections",
                "FAIL" if missing else "PASS",
                f"missing sections {missing}"
                if missing
                else f"{len(RB53_SECTIONS)} sections present",
            )
        )
    else:
        checks.append(check("RB-53 runbook", "FAIL", "runbook missing"))
    checks.append(
        check(
            "dry-walkthrough",
            "INCOMPLETE" if trc_path.is_file() else "FAIL",
            "walkthrough record present - a human walkthrough, UNMEASURED by this run"
            if trc_path.is_file()
            else "walkthrough record missing",
        )
    )
    return task("R11-M01-T01", "Finalise cutover runbook RB-53", checks)


def verify_t02_rehearsal_presignature() -> dict:
    logger.info(
        "--- [2/5] Verifying Task R11-M01-T02: Final Full-Volume Rehearsal & Pre-Signature ---"
    )
    rehearsal, reh = evidence_check(
        "final full-volume rehearsal", "r11-m01-final-volume-rehearsal.json"
    )
    presign, _ = evidence_check(
        "reconciliation pre-signature", "r11-m01-reconciliation-presignature.json"
    )
    return task(
        "R11-M01-T02",
        "Final full-volume rehearsal & pre-signature",
        [rehearsal, presign],
        run_id=(reh or {}).get("run_id"),
    )


def verify_t03_cutover_weekend_execution() -> dict:
    logger.info("--- [3/5] Verifying Task R11-M01-T03: Cutover Weekend Execution & Smoke Gates ---")
    execution, ev = evidence_check(
        "cutover weekend execution", "r11-m01-cutover-execution-evidence.json"
    )
    return task(
        "R11-M01-T03",
        "Execute cutover weekend & smoke gates",
        [execution],
        live_traffic_status=(ev or {}).get("live_traffic_status"),
    )


def _post_go_live(task_id: str, title: str, document: Path, filename: str, cutover: str) -> dict:
    checks = [
        check(
            f"document {document.name}",
            "PASS" if document.is_file() else "FAIL",
            "present" if document.is_file() else "missing",
        )
    ]
    data, problem = read_json(EVIDENCE_DIR / filename)
    if data is None:
        checks.append(check(filename, "FAIL", problem))
    elif cutover != "PASS":
        checks.append(
            check(
                "post-go-live claims",
                "FAIL",
                f"{filename} reports production operations, but the cutover is not evidenced "
                f"(T03 {cutover}) - the claim has nothing to stand on",
            )
        )
    else:
        checks.append(
            check(
                "post-go-live claims",
                "INCOMPLETE",
                f"{filename}: production telemetry/filings are not observable by this run",
            )
        )
    return task(task_id, title, checks)


def verify_t04_hypercare_operations(cutover: str = "FAIL") -> dict:
    logger.info("--- [4/5] Verifying Task R11-M01-T04: Hypercare Stand-up (SV-004) ---")
    return _post_go_live(
        "R11-M01-T04",
        "Stand up hypercare operations SV-004",
        CODEBASE_ROOT / "docs" / "operations" / "SV-004-hypercare-operating-manual.md",
        "r11-m01-hypercare-day1-stability-report.json",
        cutover,
    )


def verify_t05_month1_operational_proofs(cutover: str = "FAIL") -> dict:
    logger.info(
        "--- [5/5] Verifying Task R11-M01-T05: Month-1 Operational Proofs (The 3 Proofs) ---"
    )
    return _post_go_live(
        "R11-M01-T05",
        "Verify month-1 operational proofs",
        CODEBASE_ROOT / "docs" / "traceability" / "r11-m01-month1-close-report.md",
        "r11-m01-month1-operational-proofs.json",
        cutover,
    )


def summarise(results: list[dict]) -> dict:
    status = combine(*(r["status"] for r in results)) if results else "FAIL"
    return {
        "milestone": "R11-M01",
        "title": "Cutover and go-live",
        "verified_at": datetime.now(UTC).isoformat(),
        "overall_status": status,
        "tasks_passed": sum(1 for r in results if r["status"] == "PASS"),
        "tasks_incomplete": sum(1 for r in results if r["status"] == "INCOMPLETE"),
        "tasks_failed": sum(1 for r in results if r["status"] == "FAIL"),
        "tasks_summary": {r["task_id"]: r for r in results},
        "all_tasks_completed": status == "PASS",
    }


def main() -> int:
    logger.info("======================================================================")
    logger.info("STARTING MASTER VERIFICATION: MILESTONE R11-M01 (CUTOVER AND GO-LIVE)")
    logger.info("======================================================================")
    t01 = verify_t01_cutover_runbook()
    t02 = verify_t02_rehearsal_presignature()
    t03 = verify_t03_cutover_weekend_execution()
    t04 = verify_t04_hypercare_operations(t03["status"])
    t05 = verify_t05_month1_operational_proofs(t03["status"])
    summary = summarise([t01, t02, t03, t04, t05])
    summary_path = EVIDENCE_DIR / "r11-m01-summary-audit.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    logger.info("Saved summary audit to %s", summary_path)
    logger.info(
        "MILESTONE R11-M01: %s (%d PASS / %d INCOMPLETE / %d FAIL)",
        summary["overall_status"],
        summary["tasks_passed"],
        summary["tasks_incomplete"],
        summary["tasks_failed"],
    )
    return {"PASS": 0, "FAIL": 1}.get(summary["overall_status"], 2)


if __name__ == "__main__":
    sys.exit(main())
