# A10 remediation (2026-11-05), R1: workflow-locked states on the M60
# governance surfaces.
#
# The audit found every lifecycle field (risk state and acceptance, control
# and framework state, SoD waiver, licence state, policy approval, PDPA
# outcome, CAPA status) writable by whoever could see the record — the
# register said "accepted" because somebody typed it (report §6 R1,
# M60-4/-7/-11/-15 and the 56 no-action surfaces).
#
# Every control is exercised as NON-ADMIN users holding only the role groups
# each step needs (the superuser is trusted by the field guard and would
# hide a gap). Each gate is attacked three ways: the wrong role, a plain
# write() (the JSON-RPC path) and the real P03 endpoints. The legitimate
# path runs end to end through the real actions. The odoo_env fixture rolls
# everything back.
import itertools
import types

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import AccessError, UserError

REFUSED = (UserError, AccessError)
GUARD = "changes only through its workflow"
OFF_SCREEN = "is not editable on this screen"
OFFICER = "cd_grc.group_grc_officer"
RISK_OWNER = "cd_grc.group_grc_risk_owner"

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)

_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 R1 %s %d" % (login, n),
                "login": "a10r1.%s.%d@a10.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


def p03(x, endpoint, user=None, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return endpoint(g.P03GenericApiController(), **kw)


@pytest.fixture
def r(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")
    x.officer = _user(env, "officer", [OFFICER])
    x.owner = _user(env, "owner", [RISK_OWNER])
    x.owner_emp = env["hr.employee"].create({"name": "A10 R1 Risk Owner", "user_id": x.owner.id})
    x.other_emp = env["hr.employee"].create({"name": "A10 R1 Other Employee"})
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


# ------------------------------------------------------------------ risk register
def test_r1_residual_acceptance_is_a_risk_owners_act(r):
    Risk = r.env["fix.risk.register"]
    # P1-5: the residual (2×3) is assessed below the inherent (3×3), so the
    # acceptance needs the reduction grounded in a linked active control
    rec = Risk.create(
        {
            "name": "Parts markup arbitrage",
            "category": "financial",
            "control_ids": [(0, 0, {"name": "Markup ceiling in price list", "control_type": "preventive"})],
        }
    )
    # the wrong role cannot accept — the acceptance names a Risk Owner
    with pytest.raises(UserError, match="Only a Risk Owner"):
        rec.with_user(r.clerk).action_accept_residual()
    # the acceptance is assessed before it is accepted
    with pytest.raises(UserError, match="Assess the residual"):
        rec.with_user(r.owner).action_accept_residual()
    # the assessment itself is the owner's to edit (not guarded)
    rec.with_user(r.owner).write({"residual_likelihood": "2", "residual_impact": "3"})
    # a typed self-attestation is the finding: state + acceptor are guarded
    for vals in (
        {"state": "accepted"},
        {"residual_accepted_by_id": r.other_emp.id},
        {"residual_accepted_on": fields.Date.today()},
    ):
        with pytest.raises(UserError, match=GUARD):
            rec.with_user(r.owner).write(vals)
    with pytest.raises(UserError, match=GUARD):
        Risk.with_user(r.owner).create(
            {"name": "born accepted", "state": "accepted", "residual_accepted_by_id": r.other_emp.id}
        )
    # the act stamps the owner's OWN employee record and today's date
    rec.with_user(r.owner).action_accept_residual()
    assert rec.state == "accepted"
    assert rec.residual_accepted_by_id == r.owner_emp
    assert rec.residual_accepted_on == fields.Date.context_today(rec)
    assert rec.residual_accepted_by_id != r.other_emp


def test_r1_risk_acceptance_through_the_portal(r):
    """The same gate on the real endpoints: the surface takes the assessment
    but not the state, and the action needs the role."""
    Risk = r.env["fix.risk.register"]
    rec = Risk.create(
        {
            "name": "Warranty leakage",
            "category": "compliance",
            "control_ids": [(0, 0, {"name": "Warranty pre-authorisation gate", "control_type": "preventive"})],
        }
    )
    out = p03(
        r, _MW, user=r.owner, model="fix.risk.register", record_id=rec.id,
        values={"residual_likelihood": "2", "residual_impact": "3", "mitigation": "Pre-authorisation"},
    )
    assert "error" not in out and rec.mitigation == "Pre-authorisation"
    out = p03(
        r, _MW, user=r.owner, model="fix.risk.register", record_id=rec.id,
        values={"state": "accepted"},
    )
    assert "error" in out and GUARD in out["error"]
    out = p03(
        r, _MW, user=r.owner, model="fix.risk.register", record_id=rec.id,
        values={"residual_accepted_by_id": r.other_emp.id},
    )
    assert "error" in out and GUARD in out["error"]
    # the action endpoint carries the role gate
    out = p03(
        r, _MA, user=r.clerk, model="fix.risk.register", ids=rec.ids,
        method="action_accept_residual",
    )
    assert out.get("success") is False and "Risk Owner" in out.get("error", "")
    out = p03(
        r, _MA, user=r.owner, model="fix.risk.register", ids=rec.ids,
        method="action_accept_residual",
    )
    assert out.get("success") is True and rec.state == "accepted"


def test_r1_risk_close_and_reopen(r):
    Risk = r.env["fix.risk.register"]
    rec = Risk.create({"name": " obsolete branch exposure", "category": "operational"})
    with pytest.raises(UserError, match="Only a Risk Owner"):
        rec.with_user(r.clerk).action_close()
    with pytest.raises(UserError, match=GUARD):
        rec.with_user(r.owner).write({"state": "closed"})
    rec.with_user(r.owner).action_close()
    assert rec.state == "closed"
    with pytest.raises(UserError, match="already closed"):
        rec.with_user(r.owner).action_close()
    with pytest.raises(UserError, match="not closed"):
        fresh = Risk.create({"name": "never closed"})
        fresh.with_user(r.owner).action_reopen()
    rec.with_user(r.owner).action_reopen()
    assert rec.state == "open"


def test_r1_risk_owner_needs_an_employee_record(r):
    owner2 = _user(r.env, "owner2", [RISK_OWNER])  # in the group, no employee yet
    rec = r.env["fix.risk.register"].create(
        {
            "name": "accepting without a profile",
            "residual_likelihood": "2",
            "residual_impact": "2",
            "control_ids": [(0, 0, {"name": "Profile completion check", "control_type": "detective"})],
        }
    )
    with pytest.raises(UserError, match="no employee record"):
        rec.with_user(owner2).action_accept_residual()
    emp = r.env["hr.employee"].create({"name": "A10 R1 Owner Two", "user_id": owner2.id})
    rec.with_user(owner2).action_accept_residual()
    assert (rec.state, rec.residual_accepted_by_id) == ("accepted", emp)


# ------------------------------------------------------------------ controls & frameworks
def test_r1_control_and_framework_lifecycle_officer_only(r):
    Control = r.env["fix.control"]
    control = Control.create({"name": "Dual sign-off on refunds", "control_type": "preventive"})
    with pytest.raises(UserError, match="Only a Compliance Officer"):
        control.with_user(r.clerk).action_retire()
    with pytest.raises(UserError, match=GUARD):
        control.with_user(r.officer).write({"state": "inactive"})
    control.with_user(r.officer).action_retire()
    assert control.state == "inactive"
    with pytest.raises(UserError, match="is not active"):
        control.with_user(r.officer).action_retire()
    control.with_user(r.officer).action_activate()
    Framework = r.env["fix.compliance.framework"]
    fw = Framework.create({"name": "ISO 27001 (test)", "code": "iso_27001", "state": "draft"})
    with pytest.raises(UserError, match="Only a Compliance Officer"):
        fw.with_user(r.clerk).action_activate()
    with pytest.raises(UserError, match=GUARD):
        fw.with_user(r.officer).write({"state": "active"})
    fw.with_user(r.officer).action_activate()
    fw.with_user(r.officer).action_archive()
    assert fw.state == "archived"


# ------------------------------------------------------------------ SoD / licence / policy / PDPA
def test_r1_sod_waiver_is_an_officers_recorded_decision(r):
    Sod = r.env["fix.grc.sod.rule"]
    # A10 P1-3: both ends reference the reconciled register M29 checks
    purchaser = r.env["fix.role"].create({"code": "R-A1", "name": "Purchaser (test)"})
    accountant = r.env["fix.role"].create({"code": "R-A2", "name": "Accountant (test)"})
    rule = Sod.create(
        {"name": "Create vendor / pay vendor", "role_a": purchaser.id, "role_b": accountant.id}
    )
    with pytest.raises(UserError, match="Only a Compliance Officer"):
        rule.with_user(r.clerk).action_waive("because")
    with pytest.raises(UserError, match="State why"):
        rule.with_user(r.officer).action_waive()
    with pytest.raises(UserError, match=GUARD):
        rule.with_user(r.officer).write({"state": "waived"})
    rule.with_user(r.officer).action_waive("Quarter-end only; CFO reviews every run")
    assert rule.state == "waived"
    assert rule.waived_by_id == r.officer
    assert rule.waived_on == fields.Date.context_today(rule)


def test_r1_licence_suspension_records_its_reason(r):
    Licence = r.env["fix.grc.licence"]
    lic = Licence.create({"name": "Trade licence (test)", "licence_type": "trade"})
    with pytest.raises(UserError, match="Only a Compliance Officer"):
        lic.with_user(r.clerk).action_suspend("because")
    with pytest.raises(UserError, match="reason is the record"):
        lic.with_user(r.officer).action_suspend()
    with pytest.raises(UserError, match=GUARD):
        lic.with_user(r.officer).write({"state": "suspended"})
    lic.with_user(r.officer).action_suspend("DIFE show-cause pending")
    assert lic.state == "suspended"
    with pytest.raises(UserError, match="already suspended"):
        lic.with_user(r.officer).action_suspend("again")
    lic.with_user(r.officer).action_reinstate()
    assert lic.state == "valid"


def test_r1_policy_approval_is_separated_and_never_typed(r):
    Policy = r.env["fix.grc.policy"]
    policy_owner = _user(r.env, "powner")
    owner_emp = r.env["hr.employee"].create(
        {"name": "A10 R1 Policy Owner", "user_id": policy_owner.id}
    )
    policy = Policy.with_user(policy_owner).create(
        {
            "code": "POL-R1-%d" % next(_SEQ),
            "name": "Data Retention Policy",
            "policy_type": "security",
            "owner_id": owner_emp.id,
        }
    )
    # the owner does not approve their own policy (M60-11)
    with pytest.raises(UserError, match="does not approve their own policy"):
        policy.with_user(policy_owner).action_approve()
    with pytest.raises(UserError, match=GUARD):
        policy.with_user(policy_owner).write({"state": "approved", "approved_on": "2026-01-01"})
    policy.with_user(r.clerk).action_approve()
    assert (policy.state, policy.approved_on) == ("approved", fields.Date.context_today(policy))
    with pytest.raises(UserError, match="not a draft"):
        policy.with_user(r.clerk).action_approve()
    with pytest.raises(UserError, match="Only a Compliance Officer"):
        policy.with_user(r.clerk).action_retire()
    policy.with_user(r.officer).action_retire()
    assert policy.state == "retired"


def test_r1_pdpa_outcomes_move_through_actions(r):
    Pdpa = r.env["fix.grc.pdpa"]
    dsr = Pdpa.create(
        {"name": "DSR R1", "request_type": "access", "subject_name": "Subject", "company_id": r.env.company.id}
    )
    with pytest.raises(UserError, match="Only a Compliance Officer"):
        dsr.with_user(r.clerk).action_fulfil()
    with pytest.raises(UserError, match=GUARD):
        dsr.with_user(r.officer).write({"outcome": "fulfilled"})
    with pytest.raises(UserError, match="refusal ground"):
        dsr.with_user(r.officer).action_refuse()
    dsr.with_user(r.officer).action_fulfil()
    assert dsr.outcome == "fulfilled"
    with pytest.raises(UserError, match="already handled"):
        dsr.with_user(r.officer).action_fulfil()
    refusal = Pdpa.create(
        {"name": "DSR R1b", "request_type": "erasure", "subject_name": "Subject Two", "company_id": r.env.company.id}
    )
    refusal.with_user(r.officer).action_refuse("s.32 statutory retention obligation")
    assert refusal.outcome == "refused"


# ------------------------------------------------------------------ CAPA
def test_r1_capa_closure_authority(r):
    auditor_emp = r.env["hr.employee"].create({"name": "A10 R1 Auditor"})  # no login attached
    finding = r.env["fix.audit.finding"].create(
        {
            "name": "Unlogged calibration",
            "framework_id": r.env["fix.compliance.framework"].create(
                {"name": "ISO 9001 (R1)", "code": "iso_9001"}
            ).id,
            "auditor_id": auditor_emp.id,
            "target_closure_date": fields.Date.today(),
            "description": "Three multimeters without records",
            "remediation_plan": "Calibrate and log monthly",
        }
    )
    finding.action_submit_capa()
    # whoever happens to be logged in does not verify a closure (M60-15)
    with pytest.raises(UserError, match=r"auditor .* or a"):
        finding.with_user(r.clerk).action_verify_closure()
    with pytest.raises(UserError, match=GUARD):
        finding.with_user(r.officer).write({"capa_status": "closed"})
    finding.with_user(r.officer).action_verify_closure()
    assert finding.capa_status == "closed"
    with pytest.raises(UserError, match="not resubmitted"):
        finding.with_user(r.officer).action_submit_capa("again")
