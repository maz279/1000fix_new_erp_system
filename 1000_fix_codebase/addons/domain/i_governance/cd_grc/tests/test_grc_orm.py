"""cd_grc — live-ORM behaviour of M60 risk, compliance scoring and CAPA."""

from __future__ import annotations

import json
from datetime import date

import pytest
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def test_risk_score_is_likelihood_times_impact(odoo_env):
    risks = odoo_env["fix.risk.register"]
    default = risks.create({"name": "Courier delays on parts"})
    assert default.risk_score == 9  # 3 x 3
    cyber = risks.create(
        {"name": "Ransomware on POS", "category": "cyber", "likelihood": "4", "impact": "5"}
    )
    assert cyber.risk_score == 20
    control = odoo_env["fix.control"].create(
        {"name": "Offline backups", "control_type": "corrective", "risk_id": cyber.id}
    )
    assert cyber.control_ids == control
    cyber.impact = "2"
    assert cyber.risk_score == 8


def _framework(env, statuses):
    framework = env["fix.compliance.framework"].create(
        {"name": "ISO 9001:2015 (test map)", "code": "iso_9001"}
    )
    for i, status in enumerate(statuses, start=1):
        env["fix.compliance.obligation"].create(
            {
                "framework_id": framework.id,
                "name": f"Clause {i}",
                "clause_reference": f"8.{i}",
                "compliance_status": status,
            }
        )
    return framework


def test_compliance_score_excludes_not_applicable(odoo_env):
    """Regression: 'not_applicable' clauses stayed in the denominator and
    scored as failures (2 compliant + 1 partial of 4 applicable = 62.5%,
    previously reported as 50.0% over all 5 clauses)."""
    framework = _framework(
        odoo_env,
        ["compliant", "compliant", "partially_compliant", "non_compliant", "not_applicable"],
    )
    assert framework.clause_count == 5
    assert framework.compliance_score == 62.5
    framework.obligation_ids.filtered(lambda o: o.compliance_status == "non_compliant").write(
        {"compliance_status": "compliant"}
    )
    assert framework.compliance_score == 87.5  # (3 + 0.5) / 4


def test_compliance_score_without_applicable_clauses(odoo_env):
    assert _framework(odoo_env, []).compliance_score == 100.0
    only_na = _framework(odoo_env, ["not_applicable", "not_applicable"])
    assert (only_na.clause_count, only_na.compliance_score) == (2, 100.0)


def test_audit_finding_capa_lifecycle(odoo_env):
    framework = _framework(odoo_env, ["non_compliant"])
    auditor = odoo_env["hr.employee"].create({"name": "Lead Auditor Selina"})
    finding = odoo_env["fix.audit.finding"].create(
        {
            "name": "Calibration records missing",
            "framework_id": framework.id,
            "obligation_id": framework.obligation_ids.id,
            "auditor_id": auditor.id,
            "target_closure_date": date(2026, 12, 31),
            "description": "No calibration evidence for 3 multimeters",
        }
    )
    assert (finding.capa_status, finding.finding_type) == ("open", "minor_nc")
    finding.action_submit_capa()
    assert (finding.capa_status, finding.remediation_plan) == ("capa_submitted", False)
    with (
        pytest.raises(UserError, match="remediation plan must be documented"),
        odoo_env.cr.savepoint(),
    ):
        finding.action_verify_closure()
    finding.action_submit_capa("Calibrate monthly; log in M24")
    assert finding.remediation_plan == "Calibrate monthly; log in M24"
    finding.action_verify_closure()
    assert finding.capa_status == "closed"
    assert _events(odoo_env, "grc.capa_closed", finding.id) == [
        {"code": "Calibration records missing", "framework": "ISO 9001:2015 (test map)"}
    ]
    finding.finding_code = "AUD-2026-014"
    finding.action_verify_closure()
    assert _events(odoo_env, "grc.capa_closed", finding.id)[-1]["code"] == "AUD-2026-014"
