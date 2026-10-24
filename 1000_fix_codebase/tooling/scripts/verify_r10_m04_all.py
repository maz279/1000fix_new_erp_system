#!/usr/bin/env python3
"""verify_r10_m04_all.py — Milestone R10-M04 Comprehensive Verification & Master Audit Runner.

Verifies:
- Task R10-M04-T01: 12-Environment Ladder & Data Rules Audit (12/12 environments live & isolated)
- Task R10-M04-T02: In-Stream Masking Validation on Clones (NFR-086c zero PII leakage)
- Task R10-M04-T03: Disaster Recovery Warm Standby Rehearsal (RPO <= 15m, RTO <= 2h, RB-52)
- Task R10-M04-T04: Gate GP-12 Build-Once-Promote & Rollback Rehearsal Drill (immutable digest)
- Task R10-M04-T05: Master Operator Manual & Knowledge Handover Sign-Off
- Task R10-M04-T06: HA Pairs Kill-One-Node Drills (4 components) + Vault Secret Scan (EP-06) + D-042

Every task status and detail line is derived from the producing tool's
evidence (GV-009): a task is PASS only when its evidence says PASS, FAIL when
it says FAIL or is missing/unreadable, INCOMPLETE when it reports anything
UNMEASURED/INCOMPLETE. A producer is (re)run only when its evidence file is
missing, and its non-zero exit (FAIL=1 / INCOMPLETE=2) never aborts the audit.
Overall: FAIL if any task FAILs, INCOMPLETE if any is INCOMPLETE, else PASS.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.

Emits docs/traceability/evidence/r10-m04-summary-audit.json
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
EVIDENCE_DIR = DOCS_DIR / "traceability" / "evidence"

INCOMPLETE_STATES = {"INCOMPLETE", "UNMEASURED"}


def load_evidence(name: str, producer: Path | None = None) -> tuple[dict | None, str]:
    """(evidence, problem). Runs the producer only when the file is missing."""
    ev_file = EVIDENCE_DIR / name
    if not ev_file.exists() and producer is not None:
        subprocess.run([sys.executable, str(producer)], check=False, cwd=str(REPO_ROOT))
    if not ev_file.exists():
        return None, f"evidence {name} missing"
    try:
        data = json.loads(ev_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"evidence {name} unreadable: {exc}"
    if not isinstance(data, dict):
        return None, f"evidence {name} is not an object"
    return data, ""


def status_of(*states: object) -> str:
    """Combine evidence states: any FAIL-ish -> FAIL, any INCOMPLETE -> INCOMPLETE."""
    normalised = [str(s).upper() if s is not None else "MISSING" for s in states]
    if any(s not in ("PASS", *INCOMPLETE_STATES) for s in normalised):
        return "FAIL"
    if any(s in INCOMPLETE_STATES for s in normalised):
        return "INCOMPLETE"
    return "PASS"


def _task(task: str, title: str, status: str, details: str, **measured) -> dict:
    return {
        "task": task,
        "title": title,
        **measured,
        "status": status,
        "passed": status == "PASS",
        "details": details,
    }


def check_t01_environments() -> dict:
    data, problem = load_evidence(
        "r10-m04-environment-data-rules-audit.json",
        REPO_ROOT / "tooling" / "scripts" / "audit_environment_data_rules.py",
    )
    title = "12-Environment Ladder Provisioning & Data Rules Enforcement"
    if data is None:
        return _task("R10-M04-T01", title, "FAIL", problem)
    total = data.get("total_environments", 0)
    violations = len(data.get("violations", []))
    ok = data.get("passed") is True and total == 12 and violations == 0
    return _task(
        "R10-M04-T01",
        title,
        "PASS" if ok else "FAIL",
        f"{total}/12 environments audited; {violations} data-rule violation(s)",
        environments_audited=total,
        violations_count=violations,
    )


def check_t02_clone_masking() -> dict:
    data, problem = load_evidence(
        "r10-m04-clone-masking-evidence.json",
        REPO_ROOT / "tooling" / "dr" / "test_clone_with_masking.py",
    )
    title = "NFR-086c In-Stream Sovereign Masking on Clones"
    if data is None:
        return _task("R10-M04-T02", title, "FAIL", problem)
    compliant = data.get("nfr_086c_compliant") is True
    status = status_of(data.get("status"), "PASS" if compliant else "FAIL")
    return _task(
        "R10-M04-T02",
        title,
        status,
        f"{data.get('lines_processed', 0)} lines processed, "
        f"{data.get('residual_pii_lines', 'unknown')} residual PII line(s); "
        f"evidence status {data.get('status')}",
        lines_processed=data.get("lines_processed", 0),
        nfr_086c_compliant=compliant,
    )


def check_t03_dr_rehearsal() -> dict:
    data, problem = load_evidence(
        "r10-m04-dr-rehearsal-evidence.json",
        REPO_ROOT / "tooling" / "dr" / "run_r10_m04_dr_rehearsal.py",
    )
    title = "Disaster Recovery Warm Standby & Cutover Rehearsal (RB-52)"
    runbook = (
        REPO_ROOT / "docs" / "runbooks" / "RB-52-dr-disaster-recovery-and-cutover.md"
    ).exists()
    if data is None:
        return _task("R10-M04-T03", title, "FAIL", problem, runbook_present=runbook)
    rpo, rto = data.get("actual_rpo_seconds"), data.get("actual_rto_seconds")
    states = [data.get("status"), "PASS" if runbook else "FAIL"]
    for compliant in (data.get("rpo_compliant"), data.get("rto_compliant")):
        states.append("UNMEASURED" if compliant is None else ("PASS" if compliant else "FAIL"))
    return _task(
        "R10-M04-T03",
        title,
        status_of(*states),
        f"evidence status {data.get('status')}; RPO "
        f"{'unmeasured' if rpo is None else f'{rpo}s'}, RTO "
        f"{'unmeasured' if rto is None else f'{rto}s'}; RB-52 runbook "
        f"{'present' if runbook else 'missing'}",
        rpo_seconds=rpo,
        rto_seconds=rto,
        runbook_present=runbook,
    )


def check_t04_gp12_drill() -> dict:
    data, problem = load_evidence(
        "r10-m04-gp12-drill-evidence.json",
        REPO_ROOT / "tooling" / "scripts" / "drill_build_once_promote.py",
    )
    title = "Gate GP-12 Build-Once-Promote & Rollback Rehearsal Drill"
    if data is None:
        return _task("R10-M04-T04", title, "FAIL", problem)
    discharged = data.get("gp_12_discharged") is True
    status = status_of(data.get("status"))
    if status == "PASS" and not discharged:
        status = "FAIL"
    return _task(
        "R10-M04-T04",
        title,
        status,
        f"evidence status {data.get('status')}; digest "
        f"{data.get('immutable_digest') or 'not resolved'}; GP-12 "
        f"{'discharged' if discharged else 'not discharged'}",
        immutable_digest=data.get("immutable_digest"),
        promotion_ladder_stages=len(data.get("promotion_ladder", [])),
    )


def check_t05_handover() -> dict:
    title = "Operator Manual & Knowledge Handover Sign-Off"
    manual_path = REPO_ROOT / "docs" / "operator" / "OPERATOR_MANUAL.md"
    dossier_path = REPO_ROOT / "docs" / "traceability" / "r10-m04-operator-handover.md"
    data, problem = load_evidence("r10-m04-handover-signoff.json")
    missing = [
        p.relative_to(REPO_ROOT).as_posix() for p in (manual_path, dossier_path) if not p.exists()
    ]
    if data is None:
        return _task("R10-M04-T05", title, "FAIL", "; ".join([problem, *missing]))
    signoffs = data.get("signoffs", [])
    approved = data.get("all_approved") is True
    # The documents are measured; a named human's sign-off cannot be observed
    # by this run, so recorded approvals leave the task UNMEASURED, never PASS.
    status = "INCOMPLETE" if approved and not missing and signoffs else "FAIL"
    return _task(
        "R10-M04-T05",
        title,
        status,
        f"operator manual and handover dossier present={not missing}; {len(signoffs)} sign-off(s) "
        f"recorded as approved={approved} - human attestations, UNMEASURED by this run"
        + (f"; missing: {', '.join(missing)}" if missing else ""),
        operator_manual=manual_path.relative_to(REPO_ROOT).as_posix(),
        handover_dossier=dossier_path.relative_to(REPO_ROOT).as_posix(),
        signoffs_count=len(signoffs),
    )


def check_t06_ha_vault() -> dict:
    title = "HA Platform Hardening, Vault Secrets (EP-06) & D-042"
    adr_path = (
        REPO_ROOT
        / "docs"
        / "decisions"
        / "D-042-three-release-expand-contract-migration-protocol.md"
    )
    ha, ha_problem = load_evidence(
        "r10-m04-ha-kill-node-evidence.json",
        REPO_ROOT / "tooling" / "dr" / "run_ha_kill_node_drills.py",
    )
    sec, sec_problem = load_evidence(
        "r10-m04-secret-scan-evidence.json",
        REPO_ROOT / "tooling" / "scripts" / "check-secrets.py",
    )
    problems = [p for p in (ha_problem, sec_problem) if p]
    if not adr_path.exists():
        problems.append("D-042 decision record missing")
    status = status_of(
        (ha or {}).get("status"), (sec or {}).get("status"), "FAIL" if problems else "PASS"
    )
    drills = (ha or {}).get("drills", [])
    drills_passed = sum(
        1 for d in drills if str(d.get("status", d.get("outcome", ""))).upper() == "PASS"
    )
    return _task(
        "R10-M04-T06",
        title,
        status,
        f"HA drills: evidence status {(ha or {}).get('status')}, {drills_passed}/{len(drills)} "
        f"drill(s) PASS; secret scan: {(sec or {}).get('violations_found', 'n/a')} violation(s) in "
        f"{(sec or {}).get('files_scanned', 'n/a')} files"
        + (f"; {'; '.join(problems)}" if problems else ""),
        ha_drills_passed=drills_passed,
        ha_drills_total=len(drills),
        secret_violations=(sec or {}).get("violations_found"),
        files_scanned=(sec or {}).get("files_scanned"),
        d042_ratified=adr_path.exists(),
    )


def summarise(tasks: list[dict]) -> dict:
    status = status_of(*(t["status"] for t in tasks)) if tasks else "FAIL"
    return {
        "milestone": "R10-M04",
        "title": "The Real Environment Ladder and Operational Readiness",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_tasks": len(tasks),
        "tasks_passed": sum(1 for t in tasks if t["status"] == "PASS"),
        "tasks_incomplete": sum(1 for t in tasks if t["status"] == "INCOMPLETE"),
        "tasks_failed": sum(1 for t in tasks if t["status"] == "FAIL"),
        "status": status,
        "tasks": tasks,
    }


def run_milestone_audit() -> dict:
    tasks = [
        check_t01_environments(),
        check_t02_clone_masking(),
        check_t03_dr_rehearsal(),
        check_t04_gp12_drill(),
        check_t05_handover(),
        check_t06_ha_vault(),
    ]
    summary = summarise(tasks)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / "r10-m04-summary-audit.json"
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print("=" * 80)
    print("1000FiX — Milestone R10-M04 Master Audit & Comprehensive Verification")
    print("=" * 80)
    audit = run_milestone_audit()
    for t in audit["tasks"]:
        print(f"[{t['status']}] {t['task']}: {t['title']:<48} -> {t['details']}")

    print("-" * 80)
    print(
        f"Milestone Outcome: {audit['status']} ({audit['tasks_passed']}/{audit['total_tasks']} "
        f"Tasks PASS, {audit['tasks_incomplete']} INCOMPLETE, {audit['tasks_failed']} FAIL)"
    )
    print("Master evidence written to: docs/traceability/evidence/r10-m04-summary-audit.json")
    print("=" * 80)
    sys.exit({"PASS": 0, "FAIL": 1}.get(audit["status"], 2))
