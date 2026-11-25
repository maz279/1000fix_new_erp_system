#!/usr/bin/env python3
"""
Verify Operational Runbook Coverage (DoD-11 / AR-007 §3.1)
Milestone: R09-M04 - Task: R09-M04-T04
Audits per-module runbooks across all shipped addons and validates master index.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ADDONS_DIR = REPO_ROOT / "addons"
MASTER_INDEX_PATH = REPO_ROOT / "docs" / "runbooks" / "master-runbook-index.json"
EVIDENCE_PATH = REPO_ROOT / "docs" / "traceability" / "evidence" / "r09-m04-runbooks-evidence.json"

REQUIRED_SECTIONS = [
    "Operational Overview & Core Responsibilities",
    "Module Topology & Dependencies",
    "Data Models & Database Schemas",
    "Routine Operations & Administrative Tasks",
    "Troubleshooting & Diagnostic Playbooks",
    "Disaster Recovery & Data Remediation",
    "Telemetry, Observability & SLA Thresholds",
]


def verify_runbooks():
    print(f"[*] Auditing per-module runbooks in {ADDONS_DIR}...")
    modules = []
    for manifest_path in sorted(ADDONS_DIR.rglob("__manifest__.py")):
        if any(k in manifest_path.parts for k in ("vendor", "__pycache__", ".mimosa")):
            continue
        modules.append(manifest_path.parent)

    total_modules = len(modules)
    print(f"[*] Total active modules detected: {total_modules}")

    missing_runbooks = []
    incomplete_runbooks = []
    verified_modules = []

    for mod in modules:
        tech_id = mod.name
        runbook_path = mod / "runbook.md"
        if not runbook_path.is_file():
            missing_runbooks.append(tech_id)
            continue

        try:
            content = runbook_path.read_text(encoding="utf-8")
            missing_sections = [sec for sec in REQUIRED_SECTIONS if sec not in content]
            if missing_sections:
                incomplete_runbooks.append(
                    {"module": tech_id, "missing_sections": missing_sections}
                )
            else:
                verified_modules.append(tech_id)
        except Exception as e:
            incomplete_runbooks.append({"module": tech_id, "error": str(e)})

    # Verify master index
    print(f"[*] Verifying master index at {MASTER_INDEX_PATH}...")
    index_valid = False
    index_modules_count = 0
    if MASTER_INDEX_PATH.is_file():
        with open(MASTER_INDEX_PATH, encoding="utf-8") as f:
            index_data = json.load(f)
            index_modules_count = len(index_data.get("modules", []))
            index_valid = index_modules_count == total_modules

    coverage_pct = (
        round((len(verified_modules) / total_modules) * 100.0, 2) if total_modules > 0 else 0.0
    )
    is_pass = len(missing_runbooks) == 0 and len(incomplete_runbooks) == 0 and index_valid

    evidence = {
        "$schema": "1000fix-erp/evidence/1",
        "milestone": "R09-M04",
        "task": "R09-M04-T04",
        "title": "Per-Module Operational Runbook Coverage Verification (DoD-11)",
        "standard": "DoD-11 / AR-007 §3.1 / V-7 Remediation",
        "timestamp": "2026-10-20T23:22:00Z",
        "summary": {
            "total_modules": total_modules,
            "verified_runbooks": len(verified_modules),
            "missing_runbooks": len(missing_runbooks),
            "incomplete_runbooks": len(incomplete_runbooks),
            "index_modules_count": index_modules_count,
            "coverage_pct": coverage_pct,
            "status": "PASS" if is_pass else "FAIL",
        },
        "missing_modules": missing_runbooks,
        "incomplete_modules": incomplete_runbooks,
        "status": "PASS" if is_pass else "FAIL",
    }

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_PATH, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    print(f"[+] Evidence emitted to: {EVIDENCE_PATH}")
    print(
        f"[+] Coverage: {coverage_pct}% ({len(verified_modules)}/{total_modules} modules verified)"
    )

    if not is_pass:
        print(
            f"[!] FAILED: missing={missing_runbooks}, incomplete={incomplete_runbooks}, index_valid={index_valid}"
        )
        sys.exit(1)
    else:
        print(
            f"[+] SUCCESS: All {total_modules} modules have complete, valid operational runbooks!"
        )


if __name__ == "__main__":
    verify_runbooks()
