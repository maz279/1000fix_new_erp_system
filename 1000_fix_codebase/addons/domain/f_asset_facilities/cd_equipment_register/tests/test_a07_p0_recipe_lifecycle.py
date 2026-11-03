"""A07 P0 recipe (M45): guarded lifecycle fields, real transitions and a routed
write-off approval, attacked as NON-ADMIN users on the live ORM (``odoo_env``:
rolled back). Each refusal is paired with the proper path working.

A07 audit 2026-11-03 findings:
  M45-2  calibration evidence typed and mutable (FAIL->PASS, next_due extended)
  M45-5  issue state forgeable; a damaged return went back to available
  M45-6  retirement by a plain write, no authority matrix, no SoD
  M45-7  out-of-service resolved by its opener with no re-calibration
  M45-8  a transfer was born "posted" and moved nothing
  M45-11 PM completion with no evidence; PM state forgeable
"""

import itertools
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

TAG = "A7M45R"
TIER_2 = "cd_entity_config.group_dofa_tier_2"  # Quality Manager rung
TIER_4 = "cd_entity_config.group_dofa_tier_4"  # CFO rung
REFUSED = (UserError, ValidationError, AccessError, IntegrityError)
_SEQ = itertools.count(1)


def _user(env, tag, groups=()):
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@a07.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    emp = env["hr.employee"].create({"name": "%s %s %d (emp)" % (TAG, tag, n), "user_id": user.id})
    return user, emp


def refused(env, fn, match=None):
    """True when fn is refused (run in a savepoint and flushed)."""
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        env.invalidate_all()
        if match and match not in str(exc):
            raise AssertionError("refused for another reason: %s" % exc) from exc
        return True
    return False


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env["fix.equipment"])
    x.clerk, x.clerk_emp = _user(env, "clerk")
    x.clerk2, x.clerk2_emp = _user(env, "clerk2")
    x.qm, x.qm_emp = _user(env, "qm", [TIER_2])
    x.cfo, x.cfo_emp = _user(env, "cfo", [TIER_4])
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": TAG[:5], "legal_name": "%s Entity" % TAG, "company_id": env.company.id}
    )
    x.br1, x.br2 = (
        env["fix.branch"].create(
            {
                "name": "%s %s" % (TAG, code),
                "code": code,
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
        for code in ("A7RB1", "A7RB2")
    )
    return x


def eq(c, user=None, **kw):
    c.n += 1
    vals = {"code": "%s-EQ-%02d" % (TAG, c.n), "name": "%s meter %d" % (TAG, c.n)}
    vals.update(kw)
    Model = c.env["fix.equipment"]
    return (Model.with_user(user) if user else Model).create(vals)


def cal(c, e, user=None, on=None, due=None, result="pass", **kw):
    vals = {
        "equipment_id": e.id,
        "calibrated_on": on or c.today - timedelta(days=10),
        "next_due": due or c.today + timedelta(days=355),
        "standard_ref": "STD-%s" % TAG,
        "result": result,
        "certificate_ref": "CERT-%s" % TAG,
        "performed_by": "%s Lab" % TAG,
    }
    vals.update(kw)
    return c.env["fix.calibration"].with_user(user or c.clerk).create(vals)


def fit(c, **kw):
    e = eq(c, **kw)
    cal(c, e)
    return e


def issue(c, e, user=None, custodian=None):
    return (
        c.env["fix.equipment.issue"]
        .with_user(user or c.clerk)
        .create({"equipment_id": e.id, "custodian_id": (custodian or c.clerk_emp).id})
    )


def oos(c, e, user=None):
    return (
        c.env["fix.equipment.oos"]
        .with_user(user or c.clerk)
        .create({"equipment_id": e.id, "reason": "%s fault" % TAG})
    )


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()

    def ep(name):
        fn = getattr(g.P03GenericApiController, name)
        return getattr(fn, "original_endpoint", fn)

    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def call(name, user, **kw):
        req = types.SimpleNamespace(env=c.env(user=(user or c.clerk).id))
        g.request = s.request = req
        try:
            return ep(name)(ctl, **kw)
        finally:
            g.request, s.request = old_g, old_s

    return types.SimpleNamespace(
        write=lambda user=None, **kw: call("model_write", user, **kw),
        action=lambda user=None, **kw: call("model_action", user, **kw),
    )


# ============================================================ M45-2 calibration
def test_calibration_is_insert_only(c, p03):
    e = eq(c)
    failed = cal(c, e, result="fail")
    assert refused(c.env, lambda: failed.with_user(c.clerk2).write({"result": "pass"}))
    assert refused(c.env, lambda: failed.with_user(c.clerk).write({"result": "pass"}))
    passed = cal(c, eq(c), on=c.today - timedelta(days=400), due=c.today - timedelta(days=5))
    assert refused(
        c.env, lambda: passed.with_user(c.clerk).write({"next_due": c.today + timedelta(days=3650)})
    )
    out = p03.write(
        model="fix.calibration",
        record_id=failed.id,
        values={"result": "pass", "next_due": str(c.today + timedelta(days=3650))},
    )
    failed.invalidate_recordset()
    assert out.get("error") and failed.result == "fail"
    # the notes stay open, and the form echo of an unchanged value passes
    failed.with_user(c.clerk2).write({"notes": "probe tip cracked", "result": "fail"})
    assert failed.notes == "probe tip cracked"


def test_pass_needs_certificate_and_performer_and_no_future_date(c):
    e = eq(c)
    assert refused(c.env, lambda: cal(c, e, certificate_ref=False), "certificate reference")
    assert refused(c.env, lambda: cal(c, e, performed_by="  "), "who performed it")
    assert refused(c.env, lambda: cal(c, e, on=c.today + timedelta(days=60)), "future")
    # a fail certifies nothing, so it needs no certificate
    cal(c, e, result="fail", certificate_ref=False, performed_by=False)
    good = cal(c, e, on=c.today)
    assert e.calibration_state == "current" and e._m45_latest_calibration() == good


def test_a_correction_supersedes_and_the_trail_stays(c):
    e = eq(c)
    wrong = cal(c, e, certificate_ref="CERT-TYPO")
    assert refused(c.env, lambda: wrong.with_user(c.clerk).write({"certificate_ref": "CERT-OK"}))
    fixed = cal(c, e, user=c.clerk2, certificate_ref="CERT-OK", supersedes_id=wrong.id)
    assert wrong.superseded_by_id == fixed
    assert e._m45_latest_calibration() == fixed
    # superseded once only; never typed; never across instruments
    assert refused(c.env, lambda: cal(c, e, supersedes_id=wrong.id), "already superseded")
    assert refused(c.env, lambda: wrong.with_user(c.clerk).write({"superseded_by_id": False}))
    assert refused(c.env, lambda: cal(c, e, superseded_by_id=fixed.id))
    assert refused(c.env, lambda: cal(c, eq(c), supersedes_id=fixed.id), "same equipment")


def test_a_fail_cannot_be_corrected_into_a_pass(c):
    e = eq(c)
    failed = cal(c, e, result="fail")
    assert refused(c.env, lambda: cal(c, e, supersedes_id=failed.id), "cannot be corrected")
    assert e.calibration_state == "failed"
    # the proper path: recalibrate and record a new pass of its own
    cal(c, e, on=c.today)
    assert e.calibration_state == "current" and not failed.superseded_by_id


# ============================================================ M45-6 status + write-off
def test_operational_status_changes_only_through_actions(c, p03):
    e = fit(c)
    for status in ("retired", "out_of_service", "issued"):
        assert refused(
            c.env, lambda s=status: e.with_user(c.clerk).write({"operational_status": s})
        ), status
    assert refused(c.env, lambda: eq(c, user=c.clerk, operational_status="retired"))
    out = p03.write(model="fix.equipment", record_id=e.id, values={"operational_status": "retired"})
    e.invalidate_recordset()
    assert out.get("error") and e.operational_status == "available"
    # an open out-of-service hold is not cleared by writing the status
    oos(c, e)
    assert refused(c.env, lambda: e.with_user(c.clerk2).write({"operational_status": "available"}))
    assert e.operational_status == "out_of_service"


def test_branch_and_custodian_are_set_at_registration_then_move_by_transfer(c):
    e = eq(c, user=c.clerk, branch_id=c.br1.id, custodian_id=c.clerk_emp.id)
    assert (e.branch_id, e.custodian_id) == (c.br1, c.clerk_emp)
    assert refused(c.env, lambda: e.with_user(c.clerk).write({"branch_id": c.br2.id}))
    assert refused(c.env, lambda: e.with_user(c.clerk).write({"custodian_id": c.clerk2_emp.id}))
    e.with_user(c.clerk).write({"category": "multimeter"})  # register detail stays editable


def test_writeoff_request_needs_reason_cost_and_a_returned_item(c):
    e = fit(c)
    req = e.with_user(c.clerk)
    assert refused(c.env, lambda: req.action_request_approval(), "Write-Off Reason")
    req.write({"retirement_reason": "drift beyond repair"})
    assert refused(c.env, lambda: req.action_request_approval(), "acquisition cost")
    req.write({"acquisition_cost": 18000})
    issue(c, e)
    assert refused(c.env, lambda: req.action_request_approval(), "return it first")
    assert e.approval_state == "none"


def test_writeoff_up_to_25k_is_a_quality_manager_decision(c, p03):
    e = fit(c, acquisition_cost=18000)
    assert e.dofa_tier_required == "tier_2"
    e.with_user(c.clerk).action_request_approval(justification="dropped, display dead")
    assert e.approval_state == "pending" and e.retirement_reason == "dropped, display dead"
    assert c.qm in assigned(e) and c.clerk not in assigned(e)
    # the terms are pinned while pending
    assert refused(c.env, lambda: e.with_user(c.clerk).write({"acquisition_cost": 9000}))
    assert refused(c.env, lambda: e.with_user(c.clerk).write({"retirement_reason": "other"}))
    # the approve method runs only from the approver's inbox task
    assert refused(c.env, lambda: e.with_user(c.qm).action_approve_writeoff(), "inbox")
    out = p03.action(user=c.qm, model="fix.equipment", ids=[e.id], method="action_approve_writeoff")
    assert out == {"success": False, "error": "Action not available for this surface"}
    assert e.operational_status == "available"
    approve_via_inbox(e, c.qm, requester=c.clerk)
    assert (e.operational_status, e.approval_state, e.retired_by_id) == (
        "retired",
        "approved",
        c.qm,
    )
    assert e.dofa_approved and e.dofa_approved_tier == "tier_2" and e.retired_on == c.today
    # retired is terminal: not issued, not repaired, not edited
    assert refused(c.env, lambda: e.with_user(c.clerk).write({"acquisition_cost": 1}))
    assert refused(c.env, lambda: e.with_user(c.clerk).write({"name": "renamed"}))
    assert refused(c.env, lambda: oos(c, e), "retired")
    assert refused(c.env, lambda: issue(c, e), "retired")


def test_writeoff_above_25k_is_a_cfo_decision(c):
    e = fit(c, acquisition_cost=30000)
    assert e.dofa_tier_required == "tier_4"
    e.with_user(c.clerk).write({"retirement_reason": "lost in transit"})
    e.with_user(c.clerk).action_request_approval()
    assert c.cfo in assigned(e) and c.qm not in assigned(e)
    assert not inbox_task(e, c.qm)
    approve_via_inbox(e, c.cfo, requester=c.clerk)
    assert (e.operational_status, e.dofa_approved_tier) == ("retired", "tier_4")


def test_the_reporter_cannot_approve_the_writeoff(c):
    """BRU-EAM-12: a Quality Manager who reports the loss is not routed it."""
    qm2, _emp = _user(c.env, "qm2", [TIER_2])
    e = fit(c, acquisition_cost=12000, retirement_reason="missing at count")
    e.with_user(c.qm).action_request_approval()
    assert c.qm not in assigned(e) and qm2 in assigned(e)
    assert not inbox_task(e, c.qm)
    approve_via_inbox(e, qm2, requester=c.qm)
    assert e.operational_status == "retired" and e.retired_by_id == qm2


def test_writeoff_rejection_leaves_the_item_in_service(c):
    e = fit(c, acquisition_cost=5000, retirement_reason="looks worn")
    e.with_user(c.clerk).action_request_approval()
    inbox_task(e, c.qm).with_user(c.qm).action_reject(comment="still within tolerance")
    assert (e.approval_state, e.operational_status) == ("rejected", "available")
    e.with_user(c.clerk).write({"acquisition_cost": 6000})  # unpinned again


# ============================================================ M45-7 out of service
def test_oos_resolution_needs_a_new_pass_and_another_person(c, p03):
    e = fit(c)
    cal(c, e, on=c.today, result="fail")
    hold = oos(c, e, user=c.clerk)
    assert hold.started_on == c.today
    # forged state, back-dated start: refused
    assert refused(c.env, lambda: hold.with_user(c.clerk2).write({"state": "resolved"}))
    assert refused(
        c.env,
        lambda: hold.with_user(c.clerk).write({"started_on": c.today - timedelta(days=30)}),
    )
    out = p03.write(model="fix.equipment.oos", record_id=hold.id, values={"state": "resolved"})
    hold.invalidate_recordset()
    assert out.get("error") and hold.state == "open"
    # the opener cannot resolve; nobody can without a passing re-calibration
    assert refused(c.env, lambda: hold.with_user(c.clerk).action_resolve(), "Segregation")
    assert refused(c.env, lambda: hold.with_user(c.clerk2).action_resolve(), "passing calibration")
    recal = cal(c, e, on=c.today, user=c.clerk)
    hold.with_user(c.clerk2).action_resolve()
    assert (hold.state, hold.resolved_by_id, hold.resolution_calibration_id) == (
        "resolved",
        c.clerk2,
        recal,
    )
    assert e.operational_status == "available"
    assert refused(c.env, lambda: hold.with_user(c.clerk2).action_resolve(), "open")


def test_an_older_pass_does_not_resolve_a_new_hold(c):
    e = eq(c)
    cal(c, e, on=c.today - timedelta(days=5))  # passed before the fault was found
    hold = oos(c, e)
    assert refused(c.env, lambda: hold.with_user(c.clerk2).action_resolve(), "passing calibration")
    assert e.operational_status == "out_of_service"


def test_a_resolved_hold_on_an_issued_item_returns_it_to_its_holder(c):
    e = fit(c)
    issue(c, e)
    hold = oos(c, e, user=c.clerk2)
    assert e.operational_status == "out_of_service"
    cal(c, e, on=c.today)
    hold.with_user(c.clerk).action_resolve()
    assert e.operational_status == "issued"


# ============================================================ M45-8 transfer
def test_transfer_moves_the_item_only_on_receipt_by_another_user(c):
    e = fit(c, branch_id=c.br1.id, custodian_id=c.clerk_emp.id)
    Transfer = c.env["fix.equipment.transfer"].with_user(c.clerk)
    t = Transfer.create(
        {"equipment_id": e.id, "to_branch_id": c.br2.id, "to_custodian_id": c.clerk2_emp.id}
    )
    assert (t.state, t.from_branch_id, t.from_custodian_id) == ("draft", c.br1, c.clerk_emp)
    assert refused(c.env, lambda: t.write({"state": "received"}))
    assert refused(c.env, lambda: t.action_receive(), "dispatched")
    t.action_dispatch()
    assert (t.state, t.dispatched_by_id) == ("dispatched", c.clerk)
    assert (e.branch_id, e.custodian_id) == (c.br1, c.clerk_emp)  # sender still accountable
    assert refused(c.env, lambda: t.write({"to_branch_id": c.br1.id}))
    assert refused(c.env, lambda: t.action_dispatch(), "draft")
    assert refused(c.env, lambda: issue(c, e, user=c.clerk2), "in transit")
    assert refused(c.env, lambda: t.action_receive(), "Segregation")
    t.with_user(c.clerk2).action_receive()
    assert (t.state, t.received_by_id) == ("received", c.clerk2)
    assert (e.branch_id, e.custodian_id) == (c.br2, c.clerk2_emp)
    assert refused(c.env, lambda: t.with_user(c.clerk2).action_cancel())
    assert refused(c.env, lambda: t.with_user(c.clerk2).write({"notes": "edited"}))


def test_issued_or_out_of_service_items_do_not_travel(c):
    issued = fit(c, branch_id=c.br1.id)
    issue(c, issued)
    held = fit(c, branch_id=c.br1.id)
    oos(c, held)
    Transfer = c.env["fix.equipment.transfer"].with_user(c.clerk)
    for e in (issued, held):
        assert refused(
            c.env, lambda e=e: Transfer.create({"equipment_id": e.id, "to_branch_id": c.br2.id})
        )
    # a typed origin that is not where the item sits is refused
    e = fit(c, branch_id=c.br1.id)
    assert refused(
        c.env,
        lambda: Transfer.create(
            {"equipment_id": e.id, "from_branch_id": c.br2.id, "to_branch_id": c.br2.id}
        ),
        "typed origin",
    )
    # an item that goes out of service after the draft is refused at dispatch
    t = Transfer.create({"equipment_id": e.id, "to_branch_id": c.br2.id})
    oos(c, e)
    assert refused(c.env, lambda: t.action_dispatch(), "only an available item travels")
    t.action_cancel()
    assert t.state == "cancelled" and e.branch_id == c.br1


# ============================================================ verification
def test_a_missing_result_cannot_be_rewritten(c, p03):
    e = fit(c)
    Ver = c.env["fix.equipment.verification"].with_user(c.clerk)
    lost = Ver.create({"equipment_id": e.id, "campaign_ref": "A7R-AUD", "found": False})
    assert lost.state == "missing"
    assert refused(
        c.env, lambda: lost.with_user(c.clerk2).write({"state": "verified", "found": True})
    )
    assert refused(c.env, lambda: lost.with_user(c.clerk2).write({"found": True}))
    out = p03.write(
        model="fix.equipment.verification", record_id=lost.id, values={"state": "verified"}
    )
    lost.invalidate_recordset()
    assert out.get("error") and lost.state == "missing"
    # a typed state never decides the result; found does
    typed = Ver.create({"equipment_id": e.id, "campaign_ref": "A7R-AUD", "state": "missing"})
    assert typed.state == "verified"
    seen = Ver.create({"equipment_id": e.id, "campaign_ref": "A7R-AUD"})
    assert refused(c.env, lambda: seen.write({"state": "missing"}))
    seen.write({"found": False})  # not found after all: the result follows
    assert seen.state == "missing"


# ============================================================ M45-11 PM
def test_pm_done_needs_notes_and_technician_and_is_then_frozen(c, p03):
    e = fit(c)
    job = (
        c.env["fix.equipment.pm"]
        .with_user(c.clerk)
        .create({"equipment_id": e.id, "pm_type": "corrective"})
    )
    assert refused(c.env, lambda: job.write({"state": "done"}))
    out = p03.write(model="fix.equipment.pm", record_id=job.id, values={"state": "done"})
    job.invalidate_recordset()
    assert out.get("error") and job.state == "open"
    assert refused(c.env, lambda: job.action_done(), "completion notes and the technician")
    job.write({"notes": "replaced fuse F2, verified on reference"})
    assert refused(c.env, lambda: job.action_done(), "the technician")
    job.write({"technician_id": c.clerk2_emp.id})
    job.action_done()
    assert (job.state, job.done_on) == ("done", c.today)
    assert refused(c.env, lambda: job.write({"notes": "rewritten"}))
    assert refused(c.env, lambda: job.action_done(), "open job")


# ============================================================ M45-5 issue / return
def test_issue_state_is_guarded_and_return_records_the_condition(c, p03):
    e = fit(c)
    i = issue(c, e)
    assert refused(c.env, lambda: i.write({"state": "returned"}))
    out = p03.write(model="fix.equipment.issue", record_id=i.id, values={"state": "returned"})
    i.invalidate_recordset()
    assert out.get("error") and i.state == "issued"
    other = fit(c)
    born_returned = {"equipment_id": other.id, "custodian_id": c.clerk_emp.id, "state": "returned"}
    Issue = c.env["fix.equipment.issue"].with_user(c.clerk)
    assert refused(c.env, lambda: Issue.create(born_returned))
    assert refused(c.env, lambda: i.action_return(), "condition")
    assert refused(c.env, lambda: i.action_return(condition="mint"), "must be one of")
    i.action_return(condition="good")
    assert (i.state, i.return_condition, e.operational_status) == ("returned", "good", "available")
    assert refused(c.env, lambda: i.write({"return_condition": "damaged"}))


def test_a_damaged_return_goes_out_of_service_not_available(c):
    e = fit(c)
    i = issue(c, e)
    i.write({"return_condition": "damaged", "condition_in": "cracked probe, display dead"})
    i.action_return()
    assert e.operational_status == "out_of_service"
    hold = c.env["fix.equipment.oos"].search([("equipment_id", "=", e.id), ("state", "=", "open")])
    assert len(hold) == 1 and "cracked probe" in hold.reason and hold.create_uid == c.clerk
    # the returner cannot clear the hold they opened
    cal(c, e, on=c.today)
    assert refused(c.env, lambda: hold.with_user(c.clerk).action_resolve(), "Segregation")
    hold.with_user(c.clerk2).action_resolve()
    assert e.operational_status == "available"
