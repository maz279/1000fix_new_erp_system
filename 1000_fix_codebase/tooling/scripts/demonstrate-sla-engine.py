#!/usr/bin/env python3
"""
demonstrate-sla-engine.py - Milestone R02-M05 Task T01:
Demonstrate SLA clocks and escalation firing including breach/near-breach paths at runtime (G1-04).
Generates telemetry evidence in tooling/fitness/evidence/sla-demo-evidence-latest.json.
"""

import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add services/sla-engine/src to path
CODEBASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(CODEBASE_DIR / "services" / "sla-engine" / "src"))

from sla_engine import (
    SlaPriority,
    SlaState,
    EscalationTier,
    SlaPolicy,
    SlaClock,
    SlaEngine,
)

EVIDENCE_FILE = CODEBASE_DIR / "tooling" / "fitness" / "evidence" / "sla-demo-evidence-latest.json"

def main():
    print("================================================================================")
    print("  1000FiX ERP v2.0 - SLA Clock Engine & Escalation Runtime Demonstration")
    print("  Milestone R02-M05 Task T01 (Gate G1-04 Evidence)")
    print("================================================================================")

    # Define standard policies
    policies = {
        SlaPriority.NORMAL: SlaPolicy(
            code="SLA-NORM-01",
            name="Standard Walk-in Policy",
            service_type="walk_in",
            priority=SlaPriority.NORMAL,
            response_hours=2.0,
            resolution_hours=24.0,
            escalation_template="NT-020"
        ),
        SlaPriority.HIGH: SlaPolicy(
            code="SLA-HIGH-01",
            name="High Priority Repair Policy",
            service_type="walk_in",
            priority=SlaPriority.HIGH,
            response_hours=1.0,
            resolution_hours=12.0,
            escalation_template="NT-020"
        ),
        SlaPriority.URGENT: SlaPolicy(
            code="SLA-URG-01",
            name="Urgent Business Policy",
            service_type="onsite",
            priority=SlaPriority.URGENT,
            response_hours=0.5,
            resolution_hours=4.0,
            escalation_template="NT-020"
        ),
        SlaPriority.EMERGENCY: SlaPolicy(
            code="SLA-EMERG-01",
            name="Mission Critical SLA",
            service_type="corporate",
            priority=SlaPriority.EMERGENCY,
            response_hours=0.25,
            resolution_hours=2.0,
            escalation_template="NT-020"
        )
    }

    base_time = datetime(2026, 10, 16, 8, 0, 0, tzinfo=timezone.utc)
    current_time = base_time + timedelta(hours=5.0)  # Current simulated time: 13:00 UTC

    demonstration_cases = [
        {
            "id": "CASE-01",
            "ref": "SO-2026-00101",
            "desc": "Standard normal order: 5h elapsed of 24h limit (ON TRACK)",
            "policy": policies[SlaPriority.NORMAL],
            "created_at": base_time,
            "simulate_pause": False,
            "resolved": False,
        },
        {
            "id": "CASE-02",
            "ref": "SO-2026-00102",
            "desc": "Urgent repair order: 3.5h elapsed of 4h limit (NEAR BREACH: 87.5% consumed)",
            "policy": policies[SlaPriority.URGENT],
            "created_at": current_time - timedelta(hours=3.5),
            "simulate_pause": False,
            "resolved": False,
        },
        {
            "id": "CASE-03",
            "ref": "SO-2026-00103",
            "desc": "High priority order: 12.5h elapsed of 12h limit (BREACHED - Tier 2 Supervisor Alert)",
            "policy": policies[SlaPriority.HIGH],
            "created_at": current_time - timedelta(hours=12.5),
            "simulate_pause": False,
            "resolved": False,
        },
        {
            "id": "CASE-04",
            "ref": "SO-2026-00104",
            "desc": "Emergency order: 5.5h elapsed of 2h limit (SEVERELY BREACHED >2h - Tier 3 Ops Escalation)",
            "policy": policies[SlaPriority.EMERGENCY],
            "created_at": current_time - timedelta(hours=5.5),
            "simulate_pause": False,
            "resolved": False,
        },
        {
            "id": "CASE-05",
            "ref": "SO-2026-00105",
            "desc": "Standard order with clock PAUSED awaiting parts shipment",
            "policy": policies[SlaPriority.NORMAL],
            "created_at": current_time - timedelta(hours=10.0),
            "simulate_pause": True,
            "pause_hours_ago": 6.0,
            "resolved": False,
        }
    ]

    eval_results = []
    print(f"\nSimulated Runtime Time: {current_time.isoformat()}")
    print("--------------------------------------------------------------------------------")

    for case in demonstration_cases:
        clock = SlaClock(
            service_order_ref=case["ref"],
            policy=case["policy"],
            created_at=case["created_at"]
        )

        if case.get("simulate_pause"):
            pause_time = current_time - timedelta(hours=case["pause_hours_ago"])
            clock.pause(when=pause_time)

        eval_res = SlaEngine.evaluate(clock, current_time=current_time)
        eval_res["case_id"] = case["id"]
        eval_res["case_description"] = case["desc"]
        eval_results.append(eval_res)

        print(f"[{case['id']}] {case['ref']} ({case['policy'].priority.value.upper()}):")
        print(f"       Description:  {case['desc']}")
        print(f"       State:        {eval_res['state'].upper()} (Consumed: {eval_res['consumed_pct']}%)")
        print(f"       Escalation:   {eval_res['escalation_tier'].upper()} (Template: {eval_res['escalation_template'] or 'None'})")
        print(f"       Deadline:     {eval_res['resolution_deadline']}")
        print("--------------------------------------------------------------------------------")

    # Assert that all expected paths were demonstrated
    states_observed = {r["state"] for r in eval_results}
    escalations_observed = {r["escalation_tier"] for r in eval_results}

    assert SlaState.ON_TRACK.value in states_observed, "Missing ON_TRACK demonstration"
    assert SlaState.NEAR_BREACH.value in states_observed, "Missing NEAR_BREACH demonstration"
    assert SlaState.BREACHED.value in states_observed, "Missing BREACHED demonstration"
    assert SlaState.PAUSED.value in states_observed, "Missing PAUSED demonstration"
    assert EscalationTier.TIER_1_WARNING.value in escalations_observed, "Missing Tier 1 escalation"
    assert EscalationTier.TIER_2_SUPERVISOR.value in escalations_observed, "Missing Tier 2 escalation"
    assert EscalationTier.TIER_3_OPERATIONS.value in escalations_observed, "Missing Tier 3 escalation"

    evidence_data = {
        "milestone": "R02-M05",
        "task": "R02-M05-T01",
        "gate": "G1-04",
        "verdict": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cases_demonstrated": len(eval_results),
        "states_demonstrated": sorted(list(states_observed)),
        "escalation_tiers_demonstrated": sorted(list(escalations_observed)),
        "cases": eval_results
    }

    EVIDENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(evidence_data, f, indent=2)

    print("\n[PASS] SLA Demonstration successfully proved runtime clock and escalation firing.")
    print(f"       Evidence saved to: {EVIDENCE_FILE}")
    print("================================================================================")

if __name__ == "__main__":
    main()
