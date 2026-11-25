#!/usr/bin/env python3
"""
verify_r11_m02_all.py — Milestone R11-M02 Master Verification & Audit Runner
Milestone: R11-M02 — Legacy decommissioning
Scope: Tasks R11-M02-T01 through R11-M02-T04

Audits and validates the complete delivery of Milestone R11-M02:
- T01: 48-source MG-004 reconciliation sign-offs (MIG-08)
- T02: MIG-03 / FR-SRM-088 legacy-reference survival & real-time lookup
- T03: 48-source 7-state decommission execution ladder (RL-006 / DA-006)
- T04: 8-class archive integrity & restorability proof with DA-006 retention clocks
Emits machine-readable summary audit record to r11-m02-summary-audit.json.

Every task status is derived from explicit checks (never `assert`, which
`python -O` strips); a missing or unreadable evidence file FAILS its task;
every task is audited even when an earlier one fails; overall_status is PASS
only when every task passed. Exit: 0 all PASS / 1 any FAIL.
"""

import json
import os
import sys
from datetime import UTC, datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVIDENCE_DIR = os.path.join(REPO_ROOT, "docs", "traceability", "evidence")
DOCS_DIR = os.path.join(REPO_ROOT, "docs", "traceability")


class TaskAudit:
    """Collects failed checks for one task; status is derived, never declared."""

    def __init__(self, task_id: str, description: str):
        self.task_id = task_id
        self.description = description
        self.failures: list[str] = []
        self.unmeasured: list[str] = []

    def check(self, condition: bool, message: str) -> bool:
        if not condition:
            self.failures.append(message)
        return condition

    def load(self, json_name: str, md_name: str) -> dict | None:
        json_path = os.path.join(EVIDENCE_DIR, json_name)
        md_path = os.path.join(DOCS_DIR, md_name)
        self.check(os.path.exists(md_path), f"missing documentation: {md_path}")
        if not self.check(os.path.exists(json_path), f"missing evidence: {json_path}"):
            return None
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as exc:
            self.check(False, f"unreadable evidence {json_path}: {exc}")
            return None
        if not self.check(isinstance(data, dict), f"evidence {json_path} is not an object"):
            return None
        # the producing tool's own computed verdict comes first: a field-level
        # match must never upgrade an evidence file that says INCOMPLETE/FAIL
        state = next(
            (
                data[k]
                for k in ("overall_status", "status", "verdict")
                if isinstance(data.get(k), str)
            ),
            None,
        )
        word = (state or "").strip().upper()
        if word in ("INCOMPLETE", "UNMEASURED"):
            self.unmeasured.append(f"evidence {json_name} states {state}")
        elif word != "PASS":
            self.check(False, f"evidence {json_name} states {state!r}, not a computed PASS")
        return data

    def result(self, **measured) -> dict:
        status = "FAIL" if self.failures else ("INCOMPLETE" if self.unmeasured else "PASS")
        notes = self.failures + self.unmeasured
        print(f"  -> {status}" + "".join(f"\n     - {f}" for f in notes))
        return {
            "task_id": self.task_id,
            "description": self.description,
            **measured,
            "status": status,
            "failed_checks": self.failures,
            "unmeasured_checks": self.unmeasured,
        }


def _get(data: dict | None, *path, default=None):
    cur = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _is_number(value) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def audit_t01():
    print("[TASK-AUDIT] Auditing Task R11-M02-T01: 48-Source Business Reconciliations (MIG-08)...")
    audit = TaskAudit("R11-M02-T01", "48-Source Business Reconciliation Sign-offs (MIG-08)")
    data = audit.load(
        "r11-m02-legacy-48-reconciliations.json", "r11-m02-reconciliation-signoffs.md"
    )
    sources = _get(data, "sources", default=[])
    if data is not None:
        audit.check(data.get("milestone") == "R11-M02", "milestone is not R11-M02")
        audit.check(data.get("task") == "R11-M02-T01", "task is not R11-M02-T01")
        audit.check(
            data.get("total_sources_evaluated") == 48,
            f"total_sources_evaluated={data.get('total_sources_evaluated')} (expected 48)",
        )
        audit.check(
            data.get("total_sources_approved") == 48,
            f"total_sources_approved={data.get('total_sources_approved')} (expected 48)",
        )
        audit.check(
            data.get("estate_variance_rate") == "0.00%",
            f"estate_variance_rate={data.get('estate_variance_rate')} (expected 0.00%)",
        )
        audit.check(
            isinstance(sources, list) and len(sources) == 48,
            f"{len(sources) if isinstance(sources, list) else 'no'} source rows (expected 48)",
        )
        for s in sources if isinstance(sources, list) else []:
            sid = _get(s, "source_id", default="?")
            audit.check(
                _get(s, "reconciliation_status") == "RECONCILED_100_PERCENT",
                f"source {sid}: reconciliation_status={_get(s, 'reconciliation_status')}",
            )
            audit.check(
                _get(s, "approval_status") == "APPROVED_FOR_DECOMMISSION",
                f"source {sid}: approval_status={_get(s, 'approval_status')}",
            )
            audit.check(
                _get(s, "variance_percentage") == 0.0,
                f"source {sid}: variance_percentage={_get(s, 'variance_percentage')}",
            )
    return audit.result(
        sources_reconciled=sum(
            1
            for s in (sources if isinstance(sources, list) else [])
            if _get(s, "reconciliation_status") == "RECONCILED_100_PERCENT"
        ),
        records_reconciled=_get(data, "total_records_profiled_and_reconciled"),
        variance=_get(data, "estate_variance_rate"),
    )


def audit_t02():
    print(
        "[TASK-AUDIT] Auditing Task R11-M02-T02: Legacy Reference Survival (MIG-03 / FR-SRM-088)..."
    )
    audit = TaskAudit("R11-M02-T02", "Legacy Reference Survival & Real-Time Lookup (FR-SRM-088)")
    data = audit.load(
        "r11-m02-legacy-reference-verification.json", "r11-m02-legacy-lookup-proof.md"
    )
    latency = _get(data, "performance_metrics", "average_lookup_latency_ms")
    if data is not None:
        audit.check(data.get("milestone") == "R11-M02", "milestone is not R11-M02")
        audit.check(data.get("task") == "R11-M02-T02", "task is not R11-M02-T02")
        audit.check(
            data.get("resolution_success_rate") == "100.0%",
            f"resolution_success_rate={data.get('resolution_success_rate')} (expected 100.0%)",
        )
        audit.check(
            _is_number(latency) and latency < 50.0,
            f"average_lookup_latency_ms={latency} (expected < 50)",
        )
        samples = data.get("sample_verifications", [])
        audit.check(
            isinstance(samples, list) and len(samples) >= 10,
            "fewer than 10 sample verifications",
        )
        for v in samples if isinstance(samples, list) else []:
            ref = _get(v, "legacy_reference_queried", default="?")
            audit.check(
                _get(v, "status") == "LOOKUP_SUCCESS", f"lookup {ref}: status={_get(v, 'status')}"
            )
            duration = _get(v, "lookup_duration_ms")
            audit.check(
                _is_number(duration) and duration < 50.0,
                f"lookup {ref}: lookup_duration_ms={duration} (expected < 50)",
            )
    return audit.result(
        resolution_rate=_get(data, "resolution_success_rate"),
        average_latency_ms=latency,
    )


def audit_t03():
    print(
        "[TASK-AUDIT] Auditing Task R11-M02-T03: 48-Source Decommission Execution Ladder (RL-006)..."
    )
    audit = TaskAudit("R11-M02-T03", "48-Source Decommission Execution Ladder (RL-006)")
    data = audit.load("r11-m02-decommission-register.json", "r11-m02-decommission-records.md")
    disp = _get(data, "disposition_summary", default={})
    if data is not None:
        audit.check(data.get("milestone") == "R11-M02", "milestone is not R11-M02")
        audit.check(data.get("task") == "R11-M02-T03", "task is not R11-M02-T03")
        for key, expected in (
            ("retirable_sources_decommissioned_d7", 32),
            ("deliberately_retained_sources_k", 4),
            ("purge_disposition_sources_p", 1),
            ("non_system_sources_transitioned_n", 11),
            ("total_estate_accounted_for", 48),
        ):
            audit.check(
                _get(disp, key) == expected,
                f"disposition_summary.{key}={_get(disp, key)} (expected {expected})",
            )
        audit.check(
            _get(disp, "restated_gv001_closure_criteria_met") is True,
            "restated_gv001_closure_criteria_met is not true",
        )
        audit.check(
            _get(data, "compliance_summary", "negative_connection_tests_passed") == 44,
            "negative_connection_tests_passed is not 44",
        )
        audit.check(
            _get(data, "compliance_summary", "shadow_system_scan_findings") == 0,
            "shadow_system_scan_findings is not 0",
        )
    return audit.result(
        retired_d7=_get(disp, "retirable_sources_decommissioned_d7"),
        retained_k=_get(disp, "deliberately_retained_sources_k"),
        purged_p=_get(disp, "purge_disposition_sources_p"),
        non_system_n=_get(disp, "non_system_sources_transitioned_n"),
        annual_cost_released_bdt=_get(
            data, "financial_summary", "total_annual_run_cost_released_bdt"
        ),
    )


def audit_t04():
    print(
        "[TASK-AUDIT] Auditing Task R11-M02-T04: 8-Class Archive Integrity & Restorability (DA-006)..."
    )
    audit = TaskAudit("R11-M02-T04", "8-Class Archive Integrity & Restorability (DA-006)")
    data = audit.load("r11-m02-archive-register.json", "r11-m02-archive-integrity-proof.md")
    classes = _get(data, "archive_classes", default=[])
    if data is not None:
        audit.check(data.get("milestone") == "R11-M02", "milestone is not R11-M02")
        audit.check(data.get("task") == "R11-M02-T04", "task is not R11-M02-T04")
        audit.check(
            data.get("total_archive_classes_tested") == 8,
            f"total_archive_classes_tested={data.get('total_archive_classes_tested')} (expected 8)",
        )
        audit.check(
            data.get("total_archive_classes_restorable") == 8,
            f"total_archive_classes_restorable={data.get('total_archive_classes_restorable')} "
            "(expected 8)",
        )
        audit.check(
            data.get("restorability_success_rate") == "100.0%",
            f"restorability_success_rate={data.get('restorability_success_rate')}",
        )
        audit.check(
            isinstance(classes, list) and len(classes) == 8,
            f"{len(classes) if isinstance(classes, list) else 'no'} archive classes (expected 8)",
        )
        for c in classes if isinstance(classes, list) else []:
            cid = _get(c, "archive_class_id", default="?")
            audit.check(
                _get(c, "verification_status") == "RESTORE_VERIFIED_PASS",
                f"class {cid}: verification_status={_get(c, 'verification_status')}",
            )
            audit.check(
                _get(c, "restorability_drill", "human_sample_read_status")
                == "DCM-25_COMPLIANT_READABLE",
                f"class {cid}: human_sample_read_status not DCM-25_COMPLIANT_READABLE",
            )
            audit.check(
                _get(c, "retention_governance", "retention_clock_status") == "CLOCK_RUNNING_ACTIVE",
                f"class {cid}: retention_clock_status not CLOCK_RUNNING_ACTIVE",
            )
    return audit.result(
        archive_classes_restorable=sum(
            1
            for c in (classes if isinstance(classes, list) else [])
            if _get(c, "verification_status") == "RESTORE_VERIFIED_PASS"
        ),
        total_archive_volume=_get(data, "formatted_total_archive_volume"),
        restorability_rate=_get(data, "restorability_success_rate"),
    )


def summarise(results: list[dict]) -> dict:
    passed = sum(1 for r in results if r["status"] == "PASS")
    all_passed = bool(results) and passed == len(results)
    any_failed = not results or any(r["status"] == "FAIL" for r in results)
    return {
        "milestone": "R11-M02",
        "title": "Legacy decommissioning",
        "audit_timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "overall_status": (
            "MILESTONE_R11_M02_CERTIFIED_PASS"
            if all_passed
            else ("MILESTONE_R11_M02_FAIL" if any_failed else "MILESTONE_R11_M02_INCOMPLETE")
        ),
        "total_tasks_evaluated": len(results),
        "total_tasks_passed": passed,
        "task_results": results,
        "governing_authorities": {
            "chief_technology_officer": "Shafiul Alam",
            "lead_data_steward": "Mohammad Ali",
            "data_protection_officer": "Tanvir Haque, CIPP/E",
            "financial_controller": "Mustafizur Rahman",
        },
    }


def main():
    print("================================================================================")
    print(" 1000FiX ERP v2.0 — Milestone R11-M02 Master Audit & Verification")
    print(" Standard: R11_Cutover_Decommissioning_Programme_Closure / Milestone R11-M02")
    print("================================================================================\n")

    results = [audit() for audit in (audit_t01, audit_t02, audit_t03, audit_t04)]
    summary = summarise(results)

    summary_path = os.path.join(EVIDENCE_DIR, "r11-m02-summary-audit.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n================================================================================")
    print(
        f" AUDIT VERDICT: {summary['overall_status']} "
        f"({summary['total_tasks_passed']}/{summary['total_tasks_evaluated']} Tasks PASS)"
    )
    print(f" Summary Receipt: {summary_path}")
    print("================================================================================")
    if summary["overall_status"] == "MILESTONE_R11_M02_FAIL":
        sys.exit(1)
    if summary["overall_status"] != "MILESTONE_R11_M02_CERTIFIED_PASS":
        sys.exit(2)


if __name__ == "__main__":
    main()
