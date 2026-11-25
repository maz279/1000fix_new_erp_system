#!/usr/bin/env python3
"""
demonstrate-sla-engine.py - Milestone R02-M05 Task T01:
Demonstrate SLA clocks and escalation firing including breach/near-breach paths at runtime (G1-04).
Generates telemetry evidence in tooling/fitness/evidence/sla-demo-evidence-latest.json.

GV-009: the verdict is derived from explicit checks on what services/sla-engine actually
returned in this run (in-process, simulated clock). Each case carries an expected state,
escalation tier and resolution deadline computed from the case parameters; a mismatch is
a FAIL for that case and the run continues. Scope: SlaEngine clock / state / escalation-tier
computation only - delivery of the escalation notification (template NT-020) is not
exercised by this demonstration.
Exit code: 0 PASS, 1 FAIL.
"""

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add services/sla-engine/src to path
CODEBASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(CODEBASE_DIR / "services" / "sla-engine" / "src"))

try:
    from sla_engine import (
        EscalationTier,
        SlaClock,
        SlaEngine,
        SlaPolicy,
        SlaPriority,
        SlaState,
    )

    SLA_IMPORT_ERROR = None
except ImportError as exc:  # recorded as a FAIL check, never a crash
    SLA_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"

EVIDENCE_FILE = CODEBASE_DIR / "tooling" / "fitness" / "evidence" / "sla-demo-evidence-latest.json"
EXIT_CODES = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}


def overall_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if "FAIL" in statuses:
        return "FAIL"
    if any(s != "PASS" for s in statuses):
        return "INCOMPLETE"
    return "PASS"


def build_policies() -> dict:
    return {
        SlaPriority.NORMAL: SlaPolicy(
            code="SLA-NORM-01",
            name="Standard Walk-in Policy",
            service_type="walk_in",
            priority=SlaPriority.NORMAL,
            response_hours=2.0,
            resolution_hours=24.0,
            escalation_template="NT-020",
        ),
        SlaPriority.HIGH: SlaPolicy(
            code="SLA-HIGH-01",
            name="High Priority Repair Policy",
            service_type="walk_in",
            priority=SlaPriority.HIGH,
            response_hours=1.0,
            resolution_hours=12.0,
            escalation_template="NT-020",
        ),
        SlaPriority.URGENT: SlaPolicy(
            code="SLA-URG-01",
            name="Urgent Business Policy",
            service_type="onsite",
            priority=SlaPriority.URGENT,
            response_hours=0.5,
            resolution_hours=4.0,
            escalation_template="NT-020",
        ),
        SlaPriority.EMERGENCY: SlaPolicy(
            code="SLA-EMERG-01",
            name="Mission Critical SLA",
            service_type="corporate",
            priority=SlaPriority.EMERGENCY,
            response_hours=0.25,
            resolution_hours=2.0,
            escalation_template="NT-020",
        ),
    }


def build_cases(policies: dict, current_time: datetime) -> list[dict]:
    """Demonstration cases; `expect_*` are the outcomes the case is designed to show."""
    base_time = current_time - timedelta(hours=5.0)
    return [
        {
            "id": "CASE-01",
            "ref": "SO-2026-00101",
            "desc": "Standard normal order: 5h elapsed of 24h limit (ON TRACK)",
            "policy": policies[SlaPriority.NORMAL],
            "created_at": base_time,
            "expect_state": SlaState.ON_TRACK.value,
            "expect_tier": EscalationTier.NONE.value,
        },
        {
            "id": "CASE-02",
            "ref": "SO-2026-00102",
            "desc": "Urgent repair order: 3.5h elapsed of 4h limit (NEAR BREACH: 87.5% consumed)",
            "policy": policies[SlaPriority.URGENT],
            "created_at": current_time - timedelta(hours=3.5),
            "expect_state": SlaState.NEAR_BREACH.value,
            "expect_tier": EscalationTier.TIER_1_WARNING.value,
        },
        {
            "id": "CASE-03",
            "ref": "SO-2026-00103",
            "desc": "High priority order: 12.5h elapsed of 12h limit (BREACHED - Tier 2 Supervisor Alert)",
            "policy": policies[SlaPriority.HIGH],
            "created_at": current_time - timedelta(hours=12.5),
            "expect_state": SlaState.BREACHED.value,
            "expect_tier": EscalationTier.TIER_2_SUPERVISOR.value,
        },
        {
            "id": "CASE-04",
            "ref": "SO-2026-00104",
            "desc": "Emergency order: 5.5h elapsed of 2h limit (SEVERELY BREACHED >2h - Tier 3 Ops Escalation)",
            "policy": policies[SlaPriority.EMERGENCY],
            "created_at": current_time - timedelta(hours=5.5),
            "expect_state": SlaState.BREACHED.value,
            "expect_tier": EscalationTier.TIER_3_OPERATIONS.value,
        },
        {
            "id": "CASE-05",
            "ref": "SO-2026-00105",
            "desc": "Standard order with clock PAUSED awaiting parts shipment",
            "policy": policies[SlaPriority.NORMAL],
            "created_at": current_time - timedelta(hours=10.0),
            "pause_hours_ago": 6.0,
            "expect_state": SlaState.PAUSED.value,
            "expect_tier": EscalationTier.NONE.value,
        },
    ]


def evaluate_case(case: dict, current_time: datetime) -> dict:
    """Run one case through SlaEngine and compare every observed field with its expectation."""
    policy = case["policy"]
    clock = SlaClock(service_order_ref=case["ref"], policy=policy, created_at=case["created_at"])
    paused_seconds = 0.0
    if case.get("pause_hours_ago") is not None:
        pause_time = current_time - timedelta(hours=case["pause_hours_ago"])
        clock.pause(when=pause_time)
        paused_seconds = (current_time - pause_time).total_seconds()

    expected_deadline = case["created_at"] + timedelta(
        seconds=policy.resolution_hours * 3600.0 + paused_seconds
    )
    elapsed = (current_time - case["created_at"]).total_seconds() - paused_seconds
    expected_pct = round(min(5.0, max(0.0, elapsed) / (policy.resolution_hours * 3600.0)) * 100, 1)

    problems: list[str] = []
    try:
        res = SlaEngine.evaluate(clock, current_time=current_time)
    except Exception as exc:  # product failure is a FAIL for this case, the run continues
        res = {"error": f"{type(exc).__name__}: {exc}"}
        problems.append(f"SlaEngine.evaluate raised {res['error']}")
    else:
        if res.get("state") != case["expect_state"]:
            problems.append(f"state {res.get('state')!r} != expected {case['expect_state']!r}")
        if res.get("escalation_tier") != case["expect_tier"]:
            problems.append(
                f"escalation_tier {res.get('escalation_tier')!r} != expected {case['expect_tier']!r}"
            )
        if res.get("resolution_deadline") != expected_deadline.isoformat():
            problems.append(
                f"resolution_deadline {res.get('resolution_deadline')} != expected "
                f"{expected_deadline.isoformat()}"
            )
        if res.get("consumed_pct") != expected_pct:
            problems.append(f"consumed_pct {res.get('consumed_pct')} != expected {expected_pct}")
        escalates = case["expect_tier"] != EscalationTier.NONE.value
        expected_template = policy.escalation_template if escalates else None
        if res.get("escalation_template") != expected_template:
            problems.append(
                f"escalation_template {res.get('escalation_template')!r} != expected "
                f"{expected_template!r}"
            )

    return {
        **res,
        "case_id": case["id"],
        "case_description": case["desc"],
        "expected": {
            "state": case["expect_state"],
            "escalation_tier": case["expect_tier"],
            "resolution_deadline": expected_deadline.isoformat(),
            "consumed_pct": expected_pct,
        },
        "status": "FAIL" if problems else "PASS",
        "problems": problems,
    }


def run_demonstration(current_time: datetime | None = None) -> dict:
    checks: list[dict] = []
    if SLA_IMPORT_ERROR is not None:
        checks.append({"check": "sla_engine_import", "status": "FAIL", "detail": SLA_IMPORT_ERROR})
        return {"checks": checks, "cases": [], "states": [], "tiers": []}

    current_time = current_time or datetime(2026, 10, 16, 13, 0, 0, tzinfo=UTC)
    cases = build_cases(build_policies(), current_time)
    results = [evaluate_case(case, current_time) for case in cases]
    for r in results:
        checks.append(
            {
                "check": f"case:{r['case_id']}",
                "status": r["status"],
                "detail": "; ".join(r["problems"]) or "observed state/tier/deadline/consumed match",
            }
        )

    states = sorted({r["state"] for r in results if "state" in r})
    tiers = sorted({r["escalation_tier"] for r in results if "escalation_tier" in r})
    required_states = {
        SlaState.ON_TRACK.value,
        SlaState.NEAR_BREACH.value,
        SlaState.BREACHED.value,
        SlaState.PAUSED.value,
    }
    required_tiers = {
        EscalationTier.TIER_1_WARNING.value,
        EscalationTier.TIER_2_SUPERVISOR.value,
        EscalationTier.TIER_3_OPERATIONS.value,
    }
    missing_states = sorted(required_states - set(states))
    missing_tiers = sorted(required_tiers - set(tiers))
    checks.append(
        {
            "check": "state_coverage",
            "status": "FAIL" if missing_states else "PASS",
            "detail": f"missing states: {missing_states}" if missing_states else "all observed",
        }
    )
    checks.append(
        {
            "check": "escalation_tier_coverage",
            "status": "FAIL" if missing_tiers else "PASS",
            "detail": f"missing tiers: {missing_tiers}" if missing_tiers else "all observed",
        }
    )
    return {
        "checks": checks,
        "cases": results,
        "states": states,
        "tiers": tiers,
        "simulated_time": current_time.isoformat(),
    }


def main() -> int:
    print("================================================================================")
    print("  1000FiX ERP v2.0 - SLA Clock Engine & Escalation Runtime Demonstration")
    print("  Milestone R02-M05 Task T01 (Gate G1-04 Evidence)")
    print("================================================================================")

    run = run_demonstration()
    print(f"\nSimulated Runtime Time: {run.get('simulated_time')}")
    print("--------------------------------------------------------------------------------")
    for r in run["cases"]:
        print(f"[{r['case_id']}] {r.get('service_order_ref')} [{r['status']}]")
        print(f"       Description:  {r['case_description']}")
        print(
            f"       State:        {r.get('state')} (expected {r['expected']['state']}; "
            f"consumed {r.get('consumed_pct')}%)"
        )
        print(
            f"       Escalation:   {r.get('escalation_tier')} (expected "
            f"{r['expected']['escalation_tier']}; template {r.get('escalation_template')})"
        )
        for p in r["problems"]:
            print(f"       PROBLEM:      {p}")
        print("--------------------------------------------------------------------------------")

    statuses = [c["status"] for c in run["checks"]]
    verdict = overall_verdict(statuses)
    evidence_data = {
        "milestone": "R02-M05",
        "task": "R02-M05-T01",
        "gate": "G1-04",
        "verdict": verdict,
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": (
            "in-process services/sla-engine SlaEngine.evaluate with a simulated clock; "
            "escalation notification delivery is not exercised"
        ),
        "simulated_time": run.get("simulated_time"),
        "checks_total": len(statuses),
        "checks_passed": statuses.count("PASS"),
        "checks": run["checks"],
        "total_cases_demonstrated": len(run["cases"]),
        "states_demonstrated": run["states"],
        "escalation_tiers_demonstrated": run["tiers"],
        "cases": run["cases"],
    }

    EVIDENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(evidence_data, f, indent=2)

    print(
        f"\n[{verdict}] SLA demonstration: {statuses.count('PASS')}/{len(statuses)} checks passed."
    )
    for c in run["checks"]:
        if c["status"] != "PASS":
            print(f"       {c['check']}: {c['detail']}")
    print(f"       Evidence saved to: {EVIDENCE_FILE}")
    print("================================================================================")
    return EXIT_CODES.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
