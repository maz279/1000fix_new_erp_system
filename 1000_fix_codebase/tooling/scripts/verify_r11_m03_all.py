#!/usr/bin/env python3
"""verify_r11_m03_all.py — Milestone R11-M03 Master Suite Verifier.

Executes and verifies all 5 tasks of Milestone R11-M03:
- T01: Final Security Review in Production (SC-009, DoD-15)
- T02: PDPA Closure & Regulatory Supply-Chain Check (§0.7.4 item 3, R05)
- T03: ISO 9001:2015 Surveillance Audit (CON-11 Zero Non-Conformance)
- T04: Licence Register Annual Review (D-030) & SBOM/VEX Refresh
- T05: Internal Audit of Programme Controls (GV-009, G0a->G9)

Emits r11-m03-summary-audit.json.
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
        "milestone": "R11-M03",
        "name": "Security, compliance and audit closure",
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
    print("1000FiX ERP — Milestone R11-M03 Master Verification Suite")
    print("Security, Compliance and Audit Closure (Tasks T01 - T05)")
    print("=" * 76)

    tasks = [
        ("R11-M03-T01: Final Security Review", "run_r11_m03_security_review.py"),
        ("R11-M03-T02: PDPA & CII Supply-Chain Closure", "verify_pdpa_closure.py"),
        ("R11-M03-T03: ISO 9001:2015 Surveillance Audit", "verify_iso9001_surveillance.py"),
        ("R11-M03-T04: Annual D-030 Licence Audit", "run_license_register_audit.py"),
        ("R11-M03-T05: Internal Audit of Controls", "audit_programme_controls.py"),
    ]

    results = [run_task(task_name, script_name) for task_name, script_name in tasks]
    summary = summarise(results)

    summary_file = EVIDENCE_DIR / "r11-m03-summary-audit.json"
    summary_file.write_bytes((json.dumps(summary, indent=2) + "\n").encode("utf-8"))

    print("\n" + "=" * 76)
    print("Milestone R11-M03 Execution Summary")
    print("=" * 76)
    for r in results:
        print(f" [{r['status']}] {r['task']:<50} ({r['elapsed_seconds']}s, exit {r['exit_code']})")

    print(f"\n[OK] Consolidated summary evidence written: {summary_file}")
    print(
        f"\nMilestone R11-M03: {summary['verdict']} ({summary['passed_tasks']} PASS / "
        f"{summary['incomplete_tasks']} INCOMPLETE / {summary['failed_tasks']} FAIL)"
    )
    return {"PASS": 0, "FAIL": 1}.get(summary["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
