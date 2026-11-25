#!/usr/bin/env python3
"""verify_r11_m04_all.py — Milestone R11-M04 Master Suite Verifier.

Executes and verifies all 4 tasks of Milestone R11-M04:
- T01: Benefits Measurement against BM-002 (BM-002..BM-005)
- T02: Commercial Closure against SoW Baseline (CO-003, B-11 Settlement)
- T03: Programme Financial Closure (GV-004, GV-008, IAS 38)
- T04: Operations Transition to Service Organisation (SV-001, SV-004)

Emits r11-m04-summary-audit.json.
Each task's status comes from its script's exit code (0 PASS / 1 FAIL /
2 INCOMPLETE - UNMEASURED checks); the milestone verdict is FAIL > INCOMPLETE
> PASS. Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "tooling" / "scripts"
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def status_from_exit(code: int) -> str:
    """Sub-scripts exit 0 PASS / 1 FAIL / 2 INCOMPLETE (UNMEASURED checks);
    anything else (a crash, a signal) is a FAIL."""
    return {0: "PASS", 2: "INCOMPLETE"}.get(code, "FAIL")


def overall(statuses: list[str]) -> str:
    """FAIL > INCOMPLETE > PASS; no task at all is a FAIL."""
    if not statuses or "FAIL" in statuses:
        return "FAIL"
    if "INCOMPLETE" in statuses:
        return "INCOMPLETE"
    return "PASS"


def run_task(task_name: str, script_name: str) -> dict:
    start = time.time()
    script_path = SCRIPTS_DIR / script_name
    print(f"\n>>> Running {task_name} ({script_name})...")
    proc = subprocess.run(
        [sys.executable, str(script_path)], capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    elapsed = time.time() - start

    stdout_snippet = "\n".join(proc.stdout.strip().splitlines()[-6:])
    print(stdout_snippet)

    return {
        "task": task_name,
        "script": script_name,
        "exit_code": proc.returncode,
        "elapsed_seconds": round(elapsed, 2),
        "status": status_from_exit(proc.returncode),
        "output_tail": stdout_snippet,
    }


def summarise(results: list[dict]) -> dict:
    statuses = [r["status"] for r in results]
    return {
        "$schema": "1000fix-erp/milestone-summary/1",
        "milestone": "R11-M04",
        "name": "Commercial, benefits and financial closure",
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "total_tasks": len(results),
        "passed_tasks": statuses.count("PASS"),
        "incomplete_tasks": statuses.count("INCOMPLETE"),
        "failed_tasks": statuses.count("FAIL"),
        "verdict": overall(statuses),
        "tasks": results,
    }


def main() -> int:
    print("=" * 76)
    print("1000FiX ERP — Milestone R11-M04 Master Verification Suite")
    print("Commercial, Benefits and Financial Closure (Tasks T01 - T04)")
    print("=" * 76)

    tasks = [
        ("R11-M04-T01: Benefits Measurement against BM-002", "measure_benefits_realisation.py"),
        ("R11-M04-T02: Commercial Closure against SoW Baseline", "execute_commercial_closure.py"),
        ("R11-M04-T03: Programme Financial Closure", "execute_financial_closure.py"),
        ("R11-M04-T04: Operations Transition to Service Org", "execute_service_transition.py"),
    ]

    results = [run_task(task_name, script_name) for task_name, script_name in tasks]
    summary = summarise(results)

    summary_file = EVIDENCE_DIR / "r11-m04-summary-audit.json"
    summary_file.write_bytes((json.dumps(summary, indent=2) + "\n").encode("utf-8"))

    print("\n" + "=" * 76)
    print("Milestone R11-M04 Execution Summary")
    print("=" * 76)
    for r in results:
        print(f" [{r['status']}] {r['task']:<50} ({r['elapsed_seconds']}s, exit {r['exit_code']})")

    print(f"\n[OK] Consolidated summary evidence written: {summary_file}")
    print(
        f"\nMilestone R11-M04: {summary['verdict']} ({summary['passed_tasks']} PASS / "
        f"{summary['incomplete_tasks']} INCOMPLETE / {summary['failed_tasks']} FAIL)"
    )
    return {"PASS": 0, "FAIL": 1}.get(summary["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
