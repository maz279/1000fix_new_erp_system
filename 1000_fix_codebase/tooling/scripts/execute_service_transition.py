#!/usr/bin/env python3
"""execute_service_transition.py — Milestone R11-M04-T04: Operations Transition to Service Organisation.

Standard: SV-001 / SV-002 / SV-004 / ISO/IEC 20000-1:2018 / ITIL 4
Governing finding: P12-M04-T09 / R11-M04-T04

Records the transition of platform operations to the standing BAU Service
Organisation. GV-009: the previous version wrote invented "measured" SLA
actuals (4.2 min, 99.98% uptime, ...), "COMPLIANT"/"TRANSFERRED" literals and an
"unconditionally accepted" verdict with four signatures. Every status below is
now computed from a check made in this run:

  SV001_*                   SLA actuals need production ITSM incident records and
                            availability monitoring -> UNMEASURED here
  SV004_ROTA_DOCUMENTED     each divisional on-call lead is the lead named for that
                            division in the SV-004 hypercare manual
  SV004_ROTA_ACCEPTED       acceptance of the rota by the BAU leads -> UNMEASURED
  CUSTODY_<ASSET>           each handed-over artefact exists in the repository
                            (the runbook index: every indexed runbook file exists)
  CUSTODY_ACCEPTED          receipt acknowledged by the recipients -> UNMEASURED
  HANDOVER_SIGNATURES       named signatures -> UNMEASURED

Emits:
- docs/traceability/evidence/r11-m04-service-transition-handover.json
- docs/traceability/r11-m04-service-transition-handover.md

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
TRACEABILITY_DIR = REPO_ROOT / "docs" / "traceability"
SV004_MANUAL = REPO_ROOT / "docs" / "operations" / "SV-004-hypercare-operating-manual.md"
RUNBOOK_INDEX = "docs/runbooks/master-runbook-index.json"

PASS = "PASS"  # noqa: S105 - a verdict label, not a credential
FAIL = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

SLA_UNMEASURED = (
    "requires production ITSM incident records / availability monitoring for the "
    "measurement window; none are available to this tool"
)

# SV-001 contract targets: (severity, metric, contract target).
SLA_TARGETS = (
    ("P1_Critical", "Target Ack Time", "<= 15 min"),
    ("P1_Critical", "Target Resolution Time", "<= 4 hours"),
    ("P2_Major", "Target Ack Time", "<= 30 min"),
    ("P2_Major", "Target Resolution Time", "<= 8 hours"),
    ("P3_Moderate", "Target Ack Time", "<= 2 hours"),
    ("P4_Minor", "Target Ack Time", "<= 4 hours"),
    ("Global", "System Availability (Uptime)", ">= 99.90%"),
)

# Planned permanent regional on-call rota (8 divisions), checked against SV-004.
ON_CALL_ROTA = (
    ("Dhaka Central", "Tanvir Ahmed", "Senior Infrastructure Lead", "Motijheel Flagship Hub"),
    (
        "Dhaka North & Suburbs",
        "Mahfuzur Rahman",
        "Systems Administrator",
        "Uttara Diagnostic Centre",
    ),
    ("Chattogram", "Farzana Yasmin", "Regional Service Lead", "Agrabad Commercial Centre"),
    ("Rajshahi", "Shahriar Kabir", "Field Support Engineer", "Shaheb Bazar Service Hub"),
    ("Khulna", "Masud Rana", "Regional Operations Engineer", "Shib Bari Service Centre"),
    ("Barisal", "Nusrat Jahan", "Support Specialist", "Sadar Road Centre"),
    ("Sylhet", "Rezwanul Hoque", "Service Operations Lead", "Zindabazar Regional Bay"),
    ("Rangpur & Mymensingh", "Kamrul Islam", "Field Network Engineer", "Station Road Service Bay"),
)

# Operational artefacts handed over: (check id, asset, repository path, recipient).
CUSTODY_ASSETS = (
    (
        "CUSTODY_RUNBOOK_INDEX",
        "Module operational runbooks",
        RUNBOOK_INDEX,
        "ITSM Knowledge Base (M66)",
    ),
    (
        "CUSTODY_RB53",
        "Master Cutover Runbook",
        "docs/runbooks/RB-53-production-cutover-master-runbook.md",
        "SRE Documentation Repository",
    ),
    (
        "CUSTODY_RB51",
        "Branch Rollout Runbook",
        "docs/runbooks/RB-51-branch-rollout-runbook.md",
        "Field Operations Management",
    ),
    (
        "CUSTODY_RB52",
        "Disaster Recovery & Failover Manual",
        "docs/runbooks/RB-52-dr-disaster-recovery-and-cutover.md",
        "Principal DBA & DR Lead",
    ),
    (
        "CUSTODY_DOCTOR",
        "Doctor Health Diagnostic Harness",
        "tooling/scripts/doctor.ps1",
        "ITSM Level-2 Support Desk",
    ),
    (
        "CUSTODY_ALERT_RULES",
        "Prometheus Alert Rules",
        "infra/observability/prometheus/fix-alerts.yml",
        "SOC / NOC Operations Team",
    ),
)

# Designated signatories (role, designated name, entity) - none has signed.
SIGNATORIES = (
    ("Head of IT Service Management (ITSM)", "Anisur Rahman", "1000FiX Services Limited"),
    ("Head of Customer Care & Contact Centre", "Shabnam Mustari", "1000FiX Services Limited"),
    ("Service Delivery Director", "Khandaker Farhad", "1000FiX Services Limited"),
    ("Outgoing Programme Director", "Syed Tarique Hasan", "Enterprise Solutions International Ltd"),
)


def make_check(check_id: str, status: str, detail: str, **measured: object) -> dict:
    return {"id": check_id, "status": status, "detail": detail, **measured}


def overall_verdict(checks: list[dict]) -> str:
    statuses = {check["status"] for check in checks}
    if not statuses:
        return UNMEASURED
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def sla_checks() -> list[dict]:
    return [
        make_check(
            f"SV001_{severity.upper()}_{metric.split('(')[0].strip().upper().replace(' ', '_')}",
            UNMEASURED,
            SLA_UNMEASURED,
            severity=severity,
            metric=metric,
            contract_target=target,
            measured_actual=None,
        )
        for severity, metric, target in SLA_TARGETS
    ]


def rota_documented_check(manual_path: Path) -> dict:
    """Each planned divisional lead is the lead named on that division's SV-004 rota row."""
    if not manual_path.exists():
        return make_check("SV004_ROTA_DOCUMENTED", FAIL, f"{manual_path.name} missing")
    lines = manual_path.read_text(encoding="utf-8", errors="replace").splitlines()
    mismatched = []
    for division, lead, _role, _hub in ON_CALL_ROTA:
        rows = [line for line in lines if line.startswith(f"| **{division}** |")]
        if not any(f"| {lead} " in row or f"| {lead} (" in row for row in rows):
            mismatched.append(f"{division}: {lead}")
    if mismatched:
        return make_check(
            "SV004_ROTA_DOCUMENTED",
            FAIL,
            f"not the SV-004 rota lead for the division: {mismatched}",
            mismatched=mismatched,
        )
    return make_check(
        "SV004_ROTA_DOCUMENTED",
        PASS,
        f"{len(ON_CALL_ROTA)}/{len(ON_CALL_ROTA)} divisional leads match {manual_path.name}",
    )


def runbook_index_check(check_id: str, asset: str, index_path: Path, repo_root: Path) -> dict:
    """The runbook index exists and every runbook it lists exists."""
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return make_check(check_id, FAIL, f"{index_path.name} missing", asset=asset)
    except (OSError, ValueError) as exc:
        return make_check(check_id, FAIL, f"{index_path.name} unreadable: {exc}", asset=asset)
    modules = index.get("modules") if isinstance(index, dict) else None
    if not isinstance(modules, list) or not modules:
        return make_check(check_id, FAIL, "runbook index lists no modules", asset=asset)
    paths = [m.get("runbook_path") for m in modules if isinstance(m, dict)]
    missing = [p for p in paths if not p or not (repo_root / p).is_file()]
    present = len(modules) - len(missing)
    detail = f"{present}/{len(modules)} indexed module runbooks present"
    if missing:
        detail += f"; missing: {missing[:10]}"
    return make_check(
        check_id,
        FAIL if missing else PASS,
        detail,
        asset=asset,
        runbooks_indexed=len(modules),
        runbooks_present=present,
    )


def custody_checks(repo_root: Path) -> list[dict]:
    checks = []
    for check_id, asset, rel_path, recipient in CUSTODY_ASSETS:
        path = repo_root / rel_path
        if rel_path == RUNBOOK_INDEX:
            check = runbook_index_check(check_id, asset, path, repo_root)
        elif path.is_file():
            check = make_check(check_id, PASS, f"{rel_path} present", asset=asset)
        else:
            check = make_check(check_id, FAIL, f"{rel_path} missing", asset=asset)
        check.update(identifier=rel_path, recipient=recipient)
        checks.append(check)
    return checks


def verify_service_transition(
    repo_root: Path = REPO_ROOT, manual_path: Path = SV004_MANUAL
) -> dict:
    checks = [
        *sla_checks(),
        rota_documented_check(manual_path),
        make_check(
            "SV004_ROTA_ACCEPTED",
            UNMEASURED,
            "requires the paging configuration and each BAU lead's acceptance of the rota",
        ),
        *custody_checks(repo_root),
        make_check(
            "CUSTODY_ACCEPTED",
            UNMEASURED,
            "requires each recipient's acknowledgement of operational custody",
        ),
        make_check(
            "HANDOVER_SIGNATURES",
            UNMEASURED,
            "requires named human signatures; none has been recorded",
        ),
    ]
    verdict = overall_verdict(checks)
    return {
        "$schema": "1000fix-erp/service-transition/1",
        "standard": "SV-001 / SV-002 / SV-004 / ISO/IEC 20000-1:2018 / ITIL 4",
        "milestone": "R11-M04",
        "task": "R11-M04-T04",
        "tool": "tooling/scripts/execute_service_transition.py",
        "measured_at": datetime.now(UTC).isoformat(),
        "handover_verdict": verdict,
        "summary": {
            s.lower(): sum(1 for c in checks if c["status"] == s) for s in (PASS, FAIL, UNMEASURED)
        },
        "checks": checks,
        "sla_performance": [c for c in checks if c["id"].startswith("SV001_")],
        "permanent_on_call_rota": [
            {"division": d, "bau_lead": lead, "role": role, "hub": hub, "shift": "24/7 Primary"}
            for d, lead, role, hub in ON_CALL_ROTA
        ],
        "operational_asset_custody": [c for c in checks if c["id"].startswith("CUSTODY_")],
        "signatories": [
            {"role": role, "designated_name": name, "entity": entity, "signed": None}
            for role, name, entity in SIGNATORIES
        ],
    }


def render_markdown(report: dict) -> str:
    verdict = report["handover_verdict"]
    s = report["summary"]
    lines = [
        "# Service Transition Handover Record — Milestone R11-M04-T04",
        "## 1000FiX ERP System v2.0 · Category 11 (Service Operations & Support) · SV-001",
        "",
        "| Metadata | Details |",
        "|---|---|",
        "| **Document Ref** | `R11-M04-T04-SERVICE-TRANSITION-HANDOVER` |",
        "| **Standards Basis** | ISO/IEC 20000-1:2018 · ITIL 4 · SV-001 / SV-004 |",
        f"| **Computed handover status** | {verdict} |",
        f"| **Checks** | {s['pass']} PASS / {s['fail']} FAIL / {s['unmeasured']} UNMEASURED |",
        f"| **Recorded at** | {report['measured_at']} |",
        f"| **Tool** | `{report['tool']}` (GV-009: statuses computed in this run) |",
        "",
        "---",
        "",
        "### 1. Service Level Performance (SV-001)",
        "",
        "| Severity | Metric | Contract Target | Measured Actual | Status |",
        "|---|---|:---:|:---:|:---:|",
    ]
    for row in report["sla_performance"]:
        actual = row["measured_actual"] if row["measured_actual"] is not None else "not measured"
        lines.append(
            f"| {row['severity']} | {row['metric']} | {row['contract_target']} | {actual} | {row['status']} |"
        )
    lines += ["", f"_{SLA_UNMEASURED}._", "", "---", "", "### 2. On-Call Escalation Rota", ""]
    lines += [
        f"{i}. **{r['division']}** ({r['hub']}): {r['bau_lead']} ({r['role']})"
        for i, r in enumerate(report["permanent_on_call_rota"], 1)
    ]
    by_id = {c["id"]: c for c in report["checks"]}
    for check_id in ("SV004_ROTA_DOCUMENTED", "SV004_ROTA_ACCEPTED"):
        lines.append(f"\n- `{check_id}`: {by_id[check_id]['status']} — {by_id[check_id]['detail']}")
    lines += [
        "",
        "---",
        "",
        "### 3. Operational Artefacts",
        "",
        "| Asset | Identifier | Recipient | Status | Detail |",
        "|---|---|---|:---:|---|",
    ]
    for c in report["operational_asset_custody"]:
        lines.append(
            f"| {c.get('asset', 'custody acceptance')} | `{c.get('identifier', '-')}` | "
            f"{c.get('recipient', '-')} | {c['status']} | {c['detail']} |"
        )
    lines += ["", "---", "", "### 4. Acceptance & Transition Sign-Off", ""]
    for sig in report["signatories"]:
        lines.append(
            f"- {sig['role']} — {sig['designated_name']} ({sig['entity']}): signature not recorded"
        )
    lines.append("")
    if verdict == PASS:
        lines.append("Every check passed in this run.")
    else:
        lines.append(
            f"Not accepted: the computed handover status is {verdict}; acceptance requires "
            "every check to pass, including the named signatures."
        )
    return "\n".join(lines) + "\n"


def main(evidence_dir: Path = EVIDENCE_DIR, traceability_dir: Path = TRACEABILITY_DIR) -> int:
    print("=" * 76)
    print("1000FiX ERP — Task R11-M04-T04: Operations Transition to Service Org")
    print("Governing Standard: SV-001 / SV-002 / SV-004 / ISO/IEC 20000-1:2018 / ITIL 4")
    print("=" * 76)
    report = verify_service_transition()
    for check in report["checks"]:
        print(f"  [{check['status']:<10}] {check['id']}: {check['detail']}")

    evidence_dir.mkdir(parents=True, exist_ok=True)
    traceability_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / "r11-m04-service-transition-handover.json"
    json_path.write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    md_path = traceability_dir / "r11-m04-service-transition-handover.md"
    md_path.write_bytes(render_markdown(report).encode("utf-8"))

    print(f"Handover verdict: {report['handover_verdict']}")
    print(f"Evidence JSON: {json_path}")
    print(f"Handover record: {md_path}")
    return exit_code(report["handover_verdict"])


if __name__ == "__main__":
    raise SystemExit(main())
