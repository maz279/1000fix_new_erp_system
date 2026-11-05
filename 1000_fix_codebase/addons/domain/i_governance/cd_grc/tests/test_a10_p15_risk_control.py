# A10 remediation (2026-11-05), P1-5: risk and control (M60-7/-8/-9).
#
# The audit found an appetite nobody stated (the KPI hardcoded score 15),
# above-appetite residuals the risk owner accepted alone, a residual
# assessment that cited no control, controls with no accountable owner, the
# owner free to test their own control, and failed tests that changed a
# colour and nothing else. Now: the appetite is stated per category by the
# Compliance Officer; a residual above it routes through M63 to the Delegated
# Authority Owner, who is stamped as the acceptor; the residual may not
# exceed the inherent score and a reduction must be grounded in linked,
# tested controls; a failed test stamps the control, raises the deficiency
# (an NCR) and drives it to a CAPA owned by the control owner.
import itertools
from unittest import mock

import psycopg2
import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

RISK_OWNER = "cd_grc.group_grc_risk_owner"
OFFICER = "cd_grc.group_grc_officer"
CFO = "cd_grc.group_grc_dofa_admin"
TASK_KEY = "fix_approval_task"

_SEQ = itertools.count(1)


def _user(env, name, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 P15 %s %d" % (name, n),
                "login": "a10p15.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


def _emp(env, user, name):
    return env["hr.employee"].create({"name": "A10 P15 %s" % name, "user_id": user.id})


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    x = lambda: None  # noqa: E731  (tiny namespace)
    x.env = env
    x.clerk = _user(env, "clerk")
    x.clerk_emp = _emp(env, x.clerk, "Clerk")
    x.officer = _user(env, "officer", [OFFICER])
    x.owner = _user(env, "owner", [RISK_OWNER])
    x.owner_emp = _emp(env, x.owner, "Risk Owner")
    x.owner2 = _user(env, "owner2", [RISK_OWNER])
    x.owner2_emp = _emp(env, x.owner2, "Risk Owner Two")
    x.cfo = _user(env, "cfo", [CFO])
    x.cfo_emp = _emp(env, x.cfo, "CFO")
    return x


def _risk(env, **kw):
    vals = {"name": kw.pop("name", "P15 risk"), "category": kw.pop("category", "operational")}
    if "control" in kw:
        vals["control_ids"] = [(0, 0, {"name": kw.pop("control"), "control_type": "preventive"})]
    if "control_owner" in kw:
        vals["control_ids"] = [
            (
                0,
                0,
                {
                    "name": kw.pop("control_owner_name", "P15 owned control"),
                    "control_type": "preventive",
                    "owner_id": kw.pop("control_owner").id,
                },
            )
        ]
    vals.update(kw)
    return env["fix.risk.register"].create(vals)


def _appetite(env, category="operational", score=8):
    return env["fix.risk.appetite"].create({"category": category, "max_residual_score": score})


def _cfo_only(env, *keep):
    """The dev admin sits in every A10 group by design; a test that reasons
    about WHO the routed decision reaches keeps only its own members (the
    odoo_env fixture rolls the change back)."""
    group = env.ref(CFO).sudo()
    keep_ids = {u.id for u in keep}
    others = group.user_ids.filtered(lambda u: u.id not in keep_ids)
    if others:
        group.write({"user_ids": [(3, u.id) for u in others]})


# --------------------------------------------------------------- the appetite
def test_the_appetite_is_stated_per_category_and_drives_above_appetite(m):
    env = m.env
    Appetite = env["fix.risk.appetite"]
    # it is the Compliance Officer's statement — a plain user reads it, never
    # writes it (the ACL layer the portal writer checks)
    with pytest.raises(AccessError):
        Appetite.with_user(m.clerk).check_access_rights("create")
    row = Appetite.with_user(m.officer).create({"category": "operational", "max_residual_score": 8})
    assert row.max_residual_score == 8
    # one statement per category and company (the Odoo 19 models.Constraint
    # surfaces as the raw SQL violation)
    with (
        pytest.raises(psycopg2.errors.UniqueViolation),
        env.cr.savepoint(),
        mock.patch("odoo.sql_db._logger"),
    ):
        _appetite(env, "operational", 4)
    with pytest.raises(ValidationError, match="1-25"), env.cr.savepoint():
        Appetite.create({"category": "financial", "max_residual_score": 30})
    # an unassessed residual is judged on the inherent score — an unknown
    # residual is never quietly 'within appetite'
    unassessed = _risk(env, likelihood="4", impact="4")  # inherent 16 > 8
    assert unassessed.above_appetite is True
    assessed_within = _risk(
        env, likelihood="4", impact="4", residual_likelihood="2", residual_impact="3"
    )  # 6
    assert assessed_within.above_appetite is False
    assessed_above = _risk(
        env, likelihood="4", impact="4", residual_likelihood="3", residual_impact="4"
    )  # 12
    assert assessed_above.above_appetite is True
    assert assessed_above.appetite_limit == 8 and assessed_above.appetite_stated
    # a category with no statement bounds nothing
    unstated = _risk(env, category="financial", likelihood="5", impact="5")
    assert unstated.above_appetite is False and unstated.appetite_stated is False


def test_the_kpi_reads_the_stated_appetite_not_a_hardcoded_band(m):
    from odoo.addons.cd_p03_portal.controllers.a10 import m60

    _appetite(m.env, "operational", 8)
    _risk(m.env, likelihood="4", impact="4", residual_likelihood="3", residual_impact="4")
    _risk(m.env, likelihood="2", impact="2", residual_likelihood="1", residual_impact="2")
    out = m60.kpis(m.env)
    assert out["risks_above_appetite"] == 1


# ---------------------------------------------- grounding and inherent ceiling
def test_the_residual_is_bounded_and_grounded(m):
    env = m.env
    # it may not exceed the inherent score: controls mitigate, never add
    # (2×2 inherent, 3×3 residual: a medium-band breach, so the HIGH-band
    # acceptance constraint keeps out of the way and this one is the blocker)
    with pytest.raises(ValidationError, match="may not exceed its inherent"), env.cr.savepoint():
        _risk(env, likelihood="2", impact="2", residual_likelihood="3", residual_impact="3")
    # a reduction with nothing behind it is refused
    naked = _risk(env, likelihood="3", impact="3", residual_likelihood="2", residual_impact="3")
    with pytest.raises(UserError, match="not grounded"):
        naked.with_user(m.owner).action_accept_residual()
    # a residual equal to the inherent score cites no control — honest
    raw = _risk(env, likelihood="3", impact="3", residual_likelihood="3", residual_impact="3")
    raw.with_user(m.owner).action_accept_residual()
    assert raw.state == "accepted"
    # an ineffective control grounds nothing
    weak = _risk(
        env,
        likelihood="3",
        impact="3",
        control_owner=m.owner2_emp,
        residual_likelihood="2",
        residual_impact="3",
    )
    weak.owner_id = m.owner_emp
    env["fix.grc.control.test"].with_user(m.clerk).create(
        {
            "control_id": weak.control_ids.id,
            "tested_on": fields.Date.today(),
            "tester_id": m.clerk_emp.id,
            "sample_size": 10,
            "exceptions": 6,
            "result": "ineffective",
        }
    )
    assert weak.control_ids.test_result == "ineffective"
    with pytest.raises(UserError, match="INEFFECTIVE"):
        weak.with_user(m.owner).action_accept_residual()
    # a tested-effective control grounds the reduction
    ok = _risk(
        env,
        likelihood="3",
        impact="3",
        control_owner=m.owner2_emp,
        residual_likelihood="2",
        residual_impact="3",
    )
    ok.owner_id = m.owner_emp
    env["fix.grc.control.test"].with_user(m.clerk).create(
        {
            "control_id": ok.control_ids.id,
            "tested_on": fields.Date.today(),
            "tester_id": m.clerk_emp.id,
            "sample_size": 10,
            "result": "effective",
        }
    )
    ok.with_user(m.owner).action_accept_residual()
    assert (ok.state, ok.residual_accepted_by_id.name) == ("accepted", m.owner_emp.name)


# ------------------------------------------------------------ the routed acceptance
def test_within_appetite_acceptance_stays_the_owners_signature(m):
    _appetite(m.env, "operational", 20)
    rec = _risk(
        m.env,
        likelihood="3",
        impact="3",
        control="Pre-auth gate",
        residual_likelihood="2",
        residual_impact="3",
    )
    rec.with_user(m.owner).action_accept_residual(justification="Within appetite")
    assert rec.state == "accepted"
    assert rec.residual_accepted_by_id == m.owner_emp
    assert rec.residual_accepted_on == fields.Date.context_today(rec)
    assert rec.approval_state == "none"  # no request was made or needed


def test_above_appetite_acceptance_is_routed_and_decided_by_someone_else(m):
    env = m.env
    _cfo_only(env, m.cfo)
    _appetite(env, "operational", 5)
    rec = _risk(
        env,
        likelihood="3",
        impact="3",
        control="Pre-auth gate",
        residual_likelihood="2",
        residual_impact="3",
    )  # residual 6 > 5
    rec.owner_id = m.owner_emp
    # the owner's press does NOT accept — it asks
    rec.with_user(m.owner).action_accept_residual(justification="Cheap to bear")
    assert rec.state != "accepted" and not rec.residual_accepted_by_id
    assert rec.approval_state == "pending"
    req = rec.approval_request_id
    assert req.justification == "Cheap to bear"
    assert req.decision_domain == "risk_acceptance"
    # the deciding task is in the CFO's inbox, not the owner's
    Task = env["fix.workflow.task"].sudo()
    task = Task.search([("res_model", "=", "fix.risk.register"), ("res_id", "=", rec.id)])
    assert task.assigned_user_id == m.cfo and task.state == "pending"
    assert not Task.search(
        [
            ("res_model", "=", "fix.risk.register"),
            ("res_id", "=", rec.id),
            ("assigned_user_id", "=", m.owner.id),
        ]
    )
    # the decision applies the acceptance and stamps the APPROVER
    task.with_user(m.cfo).action_approve(comment="Accepted for FY27")
    assert rec.state == "accepted"
    assert rec.residual_accepted_by_id == m.cfo_emp
    assert rec.residual_accepted_by_id != m.owner_emp
    assert rec.approval_state == "approved"


def test_no_one_self_accepts_above_appetite(m):
    env = m.env
    _appetite(env, "operational", 5)
    # a dual-hatted owner (Risk Owner AND CFO group) is still routed: the
    # engine excludes the requester and the creator, and alone there is
    # nobody left to ask
    dual = _user(env, "dual", [RISK_OWNER, CFO])
    _cfo_only(env, dual)
    dual_emp = _emp(env, dual, "Dual Hat")
    rec = _risk(
        env,
        likelihood="3",
        impact="3",
        control="Pre-auth gate",
        residual_likelihood="2",
        residual_impact="3",
    )
    rec.owner_id = dual_emp
    with pytest.raises(UserError, match="No one can approve"):
        rec.with_user(dual).action_accept_residual()
    assert rec.state != "accepted"
    # and the explicit segregation: a routed decision landing on the risk
    # owner (an approver who did not request) may not be the acceptor either
    rec2 = _risk(
        env,
        likelihood="3",
        impact="3",
        control="Second gate",
        residual_likelihood="2",
        residual_impact="3",
    )
    rec2.owner_id = m.owner2_emp  # owner2 holds Risk Owner AND CFO groups
    m.owner2.write({"group_ids": [(4, env.ref(CFO).id)]})
    rec2.with_user(m.owner).action_request_approval(justification="owner asks")
    task = (
        env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("res_model", "=", "fix.risk.register"),
                ("res_id", "=", rec2.id),
                ("assigned_user_id", "=", m.owner2.id),
            ]
        )
    )
    assert task
    with pytest.raises(UserError, match="may not also be the acceptor"):
        rec2.with_context(**{TASK_KEY: task}).with_user(m.owner2).action_accept_residual()
    assert rec2.state != "accepted"


def test_moving_the_assessment_voids_the_pending_acceptance(m):
    env = m.env
    _appetite(env, "operational", 5)
    rec = _risk(
        env,
        likelihood="3",
        impact="3",
        control="Pre-auth gate",
        residual_likelihood="2",
        residual_impact="3",
    )
    rec.with_user(m.owner).action_accept_residual()
    assert rec.approval_state == "pending"
    # the acceptance was decided ON this assessment: moving it voids the
    # request (A11 E4, M63-6)
    rec.with_user(m.owner).write({"residual_impact": "2"})  # 6 -> 4, now within
    assert rec.approval_state != "pending"
    assert rec.approval_request_id.state == "voided"
    # within appetite again, the owner's own signature applies
    rec.with_user(m.owner).action_accept_residual()
    assert (rec.state, rec.residual_accepted_by_id) == ("accepted", m.owner_emp)


# ------------------------------------------------------------ the failed test
def test_a_failed_test_raises_a_deficiency_and_a_capa(m):
    env = m.env
    Ncr = env["fix.ncr"].sudo()
    rec = _risk(env, likelihood="3", impact="3", control_owner=m.owner2_emp)
    rec.owner_id = m.owner_emp
    control = rec.control_ids
    Test = env["fix.grc.control.test"]
    # the tester is stamped from the session and is never the control's owner
    failed = Test.with_user(m.clerk).create(
        {
            "control_id": control.id,
            "tested_on": fields.Date.today(),
            "sample_size": 10,
            "exceptions": 3,
            "result": "ineffective",
        }
    )
    assert failed.tester_id == m.clerk_emp  # stamped, not typed
    with pytest.raises(ValidationError, match="may not be its owner"), env.cr.savepoint():
        Test.create(
            {
                "control_id": control.id,
                "tested_on": fields.Date.today(),
                "tester_id": m.owner2_emp.id,
                "result": "effective",
            }
        )
    # the control's assessment record is the test's conclusion
    assert control.test_result == "ineffective" and control.last_tested == fields.Date.today()
    # the deficiency: an NCR linked to the test, driven to a CAPA owned by the
    # control owner
    ncr = Ncr.search([("control_test_id", "=", failed.id)])
    assert len(ncr) == 1
    assert (ncr.source, ncr.severity, ncr.state) == ("control_test", "major", "capa_open")
    capa = ncr.capa_id
    assert capa.owner_id == m.owner2_emp and control.name in capa.corrective_action
    # the risk is flagged: a linked control was found not fully effective
    rec.invalidate_recordset()
    assert rec.control_deficient is True
    # a partially effective test is a failure too, but a minor one
    partial = Test.with_user(m.clerk).create(
        {
            "control_id": control.id,
            "tested_on": fields.Date.today(),
            "sample_size": 10,
            "exceptions": 1,
            "result": "partially_effective",
        }
    )
    assert Ncr.search([("control_test_id", "=", partial.id)]).severity == "minor"
    # idempotent: editing the test record does not raise a second deficiency
    failed.write({"notes": "re-checked the exceptions list"})
    assert Ncr.search_count([("control_test_id", "=", failed.id)]) == 1
    # an effective test stamps the control and raises nothing
    ok = Test.with_user(m.clerk).create(
        {
            "control_id": control.id,
            "tested_on": fields.Date.today(),
            "sample_size": 10,
            "result": "effective",
        }
    )
    assert control.test_result == "effective"
    assert not Ncr.search([("control_test_id", "=", ok.id)])
    rec.invalidate_recordset()
    assert rec.control_deficient is False


def test_a_failed_test_on_an_unowned_control_names_its_owner_first(m):
    env = m.env
    rec = _risk(env, likelihood="3", impact="3", control="Orphan control")
    with pytest.raises(UserError, match="no owner"), env.cr.savepoint():
        env["fix.grc.control.test"].create(
            {
                "control_id": rec.control_ids.id,
                "tested_on": fields.Date.today(),
                "result": "ineffective",
            }
        )
    # naming the control's owner (or the risk's) is the fix
    rec.control_ids.owner_id = m.owner2_emp
    env["fix.grc.control.test"].create(
        {
            "control_id": rec.control_ids.id,
            "tested_on": fields.Date.today(),
            "result": "ineffective",
        }
    )
    assert (
        env["fix.ncr"]
        .sudo()
        .search_count(
            [
                ("source", "=", "control_test"),
                ("control_test_id.control_id", "=", rec.control_ids.id),
            ]
        )
        == 1
    )
