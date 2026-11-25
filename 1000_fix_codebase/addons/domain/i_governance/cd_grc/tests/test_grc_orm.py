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


# --- A10 S6: the compliance assessment is an act, not a typed default --------


def _obligation(env, framework=None):
    framework = framework or env["fix.compliance.framework"].create(
        {"name": "ISO 27001 (assess test)", "code": "iso_27001"}
    )
    return env["fix.compliance.obligation"].create(
        {
            "framework_id": framework.id,
            "name": "Clause A.8 Asset inventory",
            "clause_reference": "A.8.1",
        }
    )


def _user(env, login, groups=()):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "grc.%s@a10.test" % login.replace(" ", "."),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )


def test_an_obligation_is_born_unassessed_and_scores_zero(odoo_env):
    """A10 S6 (D5): the default was 'compliant' — a register nobody had
    assessed scored 100%. Nothing is compliant until assessed."""
    framework = odoo_env["fix.compliance.framework"].create(
        {"name": "ISO 27001 (assess default)", "code": "iso_27001"}
    )
    ob = _obligation(odoo_env, framework)
    assert ob.compliance_status == "unassessed"
    assert framework.compliance_score == 0.0


def test_the_assessment_is_the_officers_act_not_a_typed_field(odoo_env):
    ob = _obligation(odoo_env)
    clerk = _user(odoo_env, "Assess Clerk")
    officer = _user(odoo_env, "Assess Officer", ("cd_grc.group_grc_officer",))
    with (
        pytest.raises(UserError, match="changes only through its workflow"),
        odoo_env.cr.savepoint(),
    ):
        ob.with_user(clerk).write({"compliance_status": "compliant"})
    with (
        pytest.raises(UserError, match="Only a Compliance Officer"),
        odoo_env.cr.savepoint(),
    ):
        ob.with_user(clerk).action_assess("compliant")
    with (
        pytest.raises(UserError, match="Assess Compliance Obligation"),
        odoo_env.cr.savepoint(),
    ):
        # superuser passes the role gate; the fixed vocabulary still refuses
        ob.action_assess("verdict-of-the-day")
    ob.with_user(officer).action_assess("partially_compliant", "Evidence covers 3 of 4 sites")
    assert ob.compliance_status == "partially_compliant"
    assert ob.framework_id.compliance_score == 50.0  # 0.5 / 1 assessed clause
    ob.with_user(officer).action_assess("compliant")
    assert ob.framework_id.compliance_score == 100.0


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
    # A10 R1 (M60-15): closure is once — a closed finding is neither
    # re-verified nor reopened by resubmitting.
    with pytest.raises(UserError, match="before verifying"):
        finding.action_verify_closure()
    with pytest.raises(UserError, match="not resubmitted"):
        finding.action_submit_capa("again")
    assert finding.capa_status == "closed"
