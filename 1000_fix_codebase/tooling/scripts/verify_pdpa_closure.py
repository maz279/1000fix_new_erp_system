#!/usr/bin/env python3
"""verify_pdpa_closure.py — PDPA Closure & Regulatory Supply-Chain Check (R11-M03-T02).

Implements:
1. DSR & 7-step Erasure SAGA drills run in-process against the real
   services/dsr-orchestrator code with a simulated residency vault: the forward
   drill, a failure-injection compensation drill, the NFR-093 30-day clock and
   the NFR-095 five-year processing record.
2. Breach-notification readiness: the orchestrator's BREACH_RUNBOOK is checked
   and the repo's breach-drill test (tests/test_pdpa_breach_notification_drill.py)
   is run.
3. CII supply-chain flow-down: the MSP contract model is scanned for a CII
   designation / flow-down covenant field.
4. Data Protection Forum attestation.
5. Emits r11-m03-pdpa-compliance-attestation.json and the Markdown closure record.

GV-009: every status is measured in this run. A production drill, a live
regulatory filing, executed-contract covenants and a minuted Forum attestation
cannot be observed from this workstation - each is UNMEASURED with its reason,
so the verdict is never PASS on this tool's word alone. Verdict: FAIL if any
check failed, INCOMPLETE if any is UNMEASURED, else PASS.
Exit 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DSR_SRC = REPO_ROOT / "services" / "dsr-orchestrator" / "src"
sys.path.insert(0, str(DSR_SRC))

from dsr_orchestrator import (
    BREACH_RUNBOOK,
    NOTIFICATION_DAYS,
    PROCESSING_RECORD_YEARS,
    DsrError,
    DsrRequest,
    DsrState,
    DsrType,
    ResidencyClientProtocol,
    SagaState,
    SagaStep,
    erasure_preserves_record,
    run_erasure_saga,
)

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
BREACH_DRILL_TEST = "tests/test_pdpa_breach_notification_drill.py"
MSP_CONTRACT_MODEL = (
    REPO_ROOT
    / "addons"
    / "domain"
    / "a_service_delivery"
    / "cd_msp_contract"
    / "models"
    / "fix_msp.py"
)

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
NFR093_DAYS = 30
NFR095_YEARS = 5
CII_FIELD_HINTS = ("cii", "flow_down", "flowdown", "critical_infra")
RUNBOOK_PHASES = ("CONTAIN", "ASSESS", "NOTIFY", "RECORD", "REVIEW")


def derive_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if FAIL in statuses:
        return FAIL
    if any(s != PASS for s in statuses):
        return "INCOMPLETE"
    return PASS


def exit_code_for(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


class SimulatedResidencyVault(ResidencyClientProtocol):
    """In-memory stand-in for the Z4 residency service (synthetic data only)."""

    def __init__(self):
        self.vault: dict[str, dict] = {
            "party:synthetic_01": {"nid_number": "SYNTHETIC-NID-01", "contact_phone": "SYN-01"},
            "party:synthetic_02": {"nid_number": "SYNTHETIC-NID-02", "biometric_hash": "SYN-H2"},
        }
        self.shred_log: list[str] = []

    def fetch_resident(self, party_ref: str) -> dict:
        return self.vault.get(party_ref, {})

    def tombstone(self, party_ref: str, key: str) -> None:
        if party_ref in self.vault:
            self.shred_log.append(f"{party_ref}:{key}")
            if key == "all":
                self.vault[party_ref] = {
                    "_tombstoned": True,
                    "_timestamp": date.today().isoformat(),
                }
            else:
                self.vault[party_ref].pop(key, None)


def _executors(trace: list[str], fail_at: SagaStep | None = None) -> dict:
    def make(step: SagaStep):
        def run(party_ref: str) -> None:
            if step is fail_at:
                raise RuntimeError(f"injected failure at {step.value}")
            trace.append(step.value)

        return run

    return {step: make(step) for step in SagaStep}


def execute_dsr_erasure_drill(party_ref: str = "party:synthetic_02") -> dict[str, Any]:
    """Forward drill: all seven steps, in order, with the resident record tombstoned."""
    vault = SimulatedResidencyVault()
    trace: list[str] = []
    state = SagaState(request_id="DSR-DRILL-ERASURE-01", party_ref=party_ref)
    problems: list[str] = []
    try:
        state = run_erasure_saga(state, _executors(trace), vault)
    except Exception as exc:  # a crash is a failed drill, not an aborted run
        problems.append(f"saga raised: {exc}")
    expected = [s.value for s in SagaStep]
    resident = vault.fetch_resident(party_ref)
    if state.status != "completed":
        problems.append(f"saga status {state.status!r}, expected 'completed'")
    if trace != expected:
        problems.append(f"executed {trace}, expected {expected}")
    if not resident.get("_tombstoned") or "nid_number" in resident:
        problems.append("resident record not tombstoned in the residency vault")
    return {
        "status": FAIL if problems else PASS,
        "mode": "in-process against services/dsr-orchestrator with a simulated residency vault",
        "saga_status": state.status,
        "steps_expected": len(expected),
        "steps_executed": len(trace),
        "execution_trace": trace,
        "resident_tombstoned": bool(resident.get("_tombstoned")),
        "problems": problems,
    }


def execute_compensation_drill(fail_at: SagaStep = SagaStep.PURGE_WAREHOUSE) -> dict[str, Any]:
    """Failure injection: the saga must roll back the completed steps in reverse."""
    trace: list[str] = []
    state = SagaState(request_id="DSR-DRILL-COMPENSATION-01", party_ref="party:synthetic_01")
    raised = False
    try:
        run_erasure_saga(state, _executors(trace, fail_at), SimulatedResidencyVault())
    except DsrError:
        raised = True
    except Exception as exc:  # wrong exception type is a failed drill
        return {"status": FAIL, "problems": [f"unexpected {type(exc).__name__}: {exc}"]}
    order = list(SagaStep)
    done_before = order[: order.index(fail_at)]
    expected_comp = [s.compensation for s in reversed(done_before)]
    problems = []
    if not raised:
        problems.append("saga did not raise DsrError on the injected failure")
    if state.status != "rolled_back":
        problems.append(f"saga status {state.status!r}, expected 'rolled_back'")
    if state.compensations_run != expected_comp:
        problems.append(f"compensations {state.compensations_run}, expected {expected_comp}")
    return {
        "status": FAIL if problems else PASS,
        "injected_failure_at": fail_at.value,
        "saga_status": state.status,
        "compensations_run": state.compensations_run,
        "problems": problems,
    }


def check_statutory_clocks(today: date | None = None) -> dict[str, Any]:
    """NFR-093 30-day notification clock and NFR-095 five-year processing record."""
    today = today or date.today()
    req = DsrRequest(
        request_id="DSR-DRILL-CLOCK-01",
        party_ref="party:synthetic_01",
        dsr_type=DsrType.ERASURE,
        received_on=today,
        state=DsrState.RECEIVED,
    )
    notify_days = (req.due_on - req.received_on).days
    record_until = erasure_preserves_record(today)
    # NFR-095 as the orchestrator defines a year (365 days x PROCESSING_RECORD_YEARS)
    min_until = today + timedelta(days=365 * NFR095_YEARS)
    problems = []
    if notify_days != NFR093_DAYS or NOTIFICATION_DAYS != NFR093_DAYS:
        problems.append(f"notification clock {notify_days}d, NFR-093 requires {NFR093_DAYS}d")
    if record_until < min_until or PROCESSING_RECORD_YEARS < NFR095_YEARS:
        problems.append(f"processing record kept until {record_until}, NFR-095 needs 5 years")
    return {
        "status": FAIL if problems else PASS,
        "notification_clock_days": notify_days,
        "processing_record_retention_years": PROCESSING_RECORD_YEARS,
        "processing_record_survives_until": record_until.isoformat(),
        "problems": problems,
    }


def check_breach_runbook(runbook: list[str] | None = None) -> dict[str, Any]:
    runbook = BREACH_RUNBOOK if runbook is None else runbook
    text = " ".join(runbook).upper()
    missing = [p for p in RUNBOOK_PHASES if p not in text]
    has_72h = "72 HOURS" in text or "72H" in text
    problems = [f"runbook lacks the {p} phase" for p in missing]
    if not has_72h:
        problems.append("runbook states no 72-hour assessment/notification window")
    return {
        "status": FAIL if problems else PASS,
        "runbook_steps": len(runbook),
        "phases_missing": missing,
        "states_72_hour_window": has_72h,
        "problems": problems,
    }


def run_pytest_file(target: str, timeout: int = 600) -> dict[str, Any]:
    path = REPO_ROOT / target
    if not path.is_file():
        return {"status": FAIL, "reason": f"{target} missing"}
    cmd = [sys.executable, "-m", "pytest", str(path), "-p", "no:cacheprovider", "-W", "ignore"]
    try:
        proc = subprocess.run(
            cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": UNMEASURED, "reason": f"pytest not runnable: {exc}"}
    if proc.returncode == 5:
        return {"status": UNMEASURED, "reason": f"{target}: no tests collected"}
    return {
        "status": PASS if proc.returncode == 0 else FAIL,
        "target": target,
        "exit_code": proc.returncode,
        "output_tail": "" if proc.returncode == 0 else (proc.stdout + proc.stderr)[-600:],
    }


def scan_cii_contract_fields(model_file: Path = MSP_CONTRACT_MODEL) -> list[str]:
    """Field names on fix.msp.contract that could carry CII designation / flow-down."""
    tree = ast.parse(model_file.read_text(encoding="utf-8", errors="ignore"))
    found = []
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        names = {
            s.targets[0].id: s.value
            for s in cls.body
            if isinstance(s, ast.Assign)
            and len(s.targets) == 1
            and isinstance(s.targets[0], ast.Name)
        }
        model = names.get("_name")
        if not (isinstance(model, ast.Constant) and model.value == "fix.msp.contract"):
            continue
        found += [n for n in names if any(h in n.lower() for h in CII_FIELD_HINTS)]
    return sorted(found)


def check_cii_flow_down(model_file: Path = MSP_CONTRACT_MODEL) -> dict[str, Any]:
    if not model_file.is_file():
        return {"status": UNMEASURED, "reason": f"MSP contract model missing: {model_file.name}"}
    fields = scan_cii_contract_fields(model_file)
    reason = (
        "fix.msp.contract carries no CII-designation or flow-down covenant field, so the "
        "system holds nothing to audit; executed-contract covenants need legal review"
        if not fields
        else f"fields {fields} exist, but executed-contract covenants need legal review "
        "of the signed contracts - not observable here"
    )
    return {"status": UNMEASURED, "contract_model_fields": fields, "reason": reason}


def build_evidence(pytest_fn=run_pytest_file) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {
        "dsr_erasure_drill": execute_dsr_erasure_drill(),
        "dsr_compensation_drill": execute_compensation_drill(),
        "dsr_statutory_clocks": check_statutory_clocks(),
        "production_dsr_drill": {
            "status": UNMEASURED,
            "reason": "no production residency vault / regional database is reachable from this "
            "workstation; the drills above ran in-process",
        },
        "breach_runbook": check_breach_runbook(),
        "breach_drill_tests": pytest_fn(BREACH_DRILL_TEST),
        "regulatory_breach_filing": {
            "status": UNMEASURED,
            "reason": "a statutory filing to the authority and customer dispatch are external "
            "acts with no incident timestamps here to time against the 72-hour window",
        },
        "cii_flow_down": check_cii_flow_down(),
        "dp_forum_attestation": {
            "status": UNMEASURED,
            "reason": "a minuted Data Protection Forum resolution signed by DPO/CDO/CISO is a "
            "human act; no signed minute is observable here",
        },
    }
    statuses = [c["status"] for c in checks.values()]
    return {
        "task_id": "R11-M03-T02",
        "milestone": "R11-M03",
        "evaluated_at_utc": datetime.now(UTC).isoformat(),
        "standards": [
            "PDPA 2026 (Law 63 of 2026)",
            "Cyber Security Ordinance 2025 (No. 25 of 2025)",
            "Section 0.7.4 item 3",
            "NFR-093",
            "NFR-095",
        ],
        "checks": checks,
        "checks_total": len(statuses),
        "checks_passed": statuses.count(PASS),
        "checks_failed": statuses.count(FAIL),
        "checks_unmeasured": statuses.count(UNMEASURED),
        "verdict": derive_verdict(statuses),
    }


def _detail(chk: dict[str, Any]) -> str:
    if chk.get("reason"):
        return chk["reason"]
    if chk.get("problems"):
        return "; ".join(chk["problems"])
    keys = (
        "steps_executed",
        "saga_status",
        "notification_clock_days",
        "processing_record_survives_until",
        "runbook_steps",
        "exit_code",
    )
    return ", ".join(f"{k}={chk[k]}" for k in keys if k in chk) or "—"


def render_markdown(ev: dict[str, Any]) -> str:
    lines = [
        "# PDPA Compliance Closure Record (R11-M03-T02)",
        "",
        "**Document ID**: `PDPA-CLOSE-R11-M03`  ",
        "**Governing Statutes**: Bangladesh Data Protection Act 2026 · Cyber Security Ordinance 2025 "
        "· Section 0.7.4 item 3  ",
        f"**Evaluation Date**: {ev['evaluated_at_utc']}  ",
        f"**Computed Verdict**: **`{ev['verdict']}`** ({ev['checks_passed']} PASS, "
        f"{ev['checks_failed']} FAIL, {ev['checks_unmeasured']} UNMEASURED)  ",
        "",
        "Every status below was measured by `tooling/scripts/verify_pdpa_closure.py` in this run "
        "(GV-009). UNMEASURED checks need an observation this workstation cannot make and keep "
        "the verdict from PASS.",
        "",
        "| Check | Result | Detail |",
        "|---|:---:|---|",
    ]
    lines += [
        f"| `{name}` | **{chk['status']}** | {_detail(chk)} |" for name, chk in ev["checks"].items()
    ]
    trace = ev["checks"]["dsr_erasure_drill"].get("execution_trace") or []
    lines += ["", "## Erasure SAGA forward trace (this run)", ""]
    lines += [f"{i}. `{step}`" for i, step in enumerate(trace, 1)] or ["- no steps executed"]
    lines += [
        "",
        "## Attestation",
        "",
        "No Data Protection Forum minute or signature is recorded by this tool; "
        f"`dp_forum_attestation` is **{ev['checks']['dp_forum_attestation']['status']}**.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):  # a cp1252 console must not crash the run
        sys.stdout.reconfigure(errors="replace")
    print("=" * 72)
    print("1000FiX ERP — Task R11-M03-T02: PDPA Closure & Regulatory Supply-Chain Check")
    print("=" * 72)
    evidence = build_evidence()
    for name, chk in evidence["checks"].items():
        print(f"  [{chk['status']}] {name}: {_detail(chk)}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EVIDENCE_DIR / "r11-m03-pdpa-compliance-attestation.json"
    json_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"\n[OK] PDPA evidence JSON written: {json_path}")

    md_path = DOCS_DIR / "r11-m03-pdpa-closure-record.md"
    md_path.write_text(render_markdown(evidence), encoding="utf-8")
    print(f"[OK] PDPA closure record written: {md_path}")
    print(f"\nVerdict: {evidence['verdict']}")
    return exit_code_for(evidence["verdict"])


if __name__ == "__main__":
    sys.exit(main())
