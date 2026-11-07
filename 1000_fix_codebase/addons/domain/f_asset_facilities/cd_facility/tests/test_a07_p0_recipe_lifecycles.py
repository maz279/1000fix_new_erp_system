"""A07 P0 recipe (M47): guarded workflow fields, closed lifecycles and routed
approvals (findings M47-1, -5, -6, -7, -8, -10, -11, -12). Live ORM, rolled back.

Every attack runs as a NON-ADMIN user created in the transaction
(base.group_user, plus a DOFA tier group for the approvers). The records live
in a company of their own, so the approval engine routes only to the users
made here. Each control is checked both ways: the attack is refused, and the
proper path works end to end through the approver's M63 inbox.
"""

from __future__ import annotations

import json
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
WO = "fix.facility.work.order"
TIER = "cd_entity_config.group_dofa_tier_%d"
FM = "cd_facility.group_facility_manager"
BOL = "cd_facility.group_branch_operations_lead"


def _user(env, login, company, ou, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, company.ids)],
                "company_id": company.id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.site"])
    x.co = env["res.company"].create({"name": "A07P0R M47 Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "A07P0R M47 OU",
            "code": "A7P0RM47",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    # A07 P1 roles: site, lease and licence records are maintained by a
    # Facility Manager, a WO is verified by one, an injury is closed by a
    # Branch Operations Lead
    x.clerk = _user(env, "a07p0r_m47_clerk", x.co, x.ou, FM)
    x.clerk2 = _user(env, "a07p0r_m47_clerk2", x.co, x.ou, BOL)
    x.t3 = _user(env, "a07p0r_m47_t3", x.co, x.ou, TIER % 3, FM)
    x.t4 = _user(env, "a07p0r_m47_t4", x.co, x.ou, TIER % 4, FM)
    x.t5 = _user(env, "a07p0r_m47_t5", x.co, x.ou, TIER % 5)
    x.cenv = env(user=x.clerk.id, context=dict(env.context, allowed_company_ids=x.co.ids))
    # an operational site (A07 P1: a new one is born Planned and opens
    # through the readiness gate, tested in test_a07_p1_site_lifecycle.py)
    x.site = env["fix.site"].create(
        {"name": "A07P0R Branch", "company_id": x.co.id, "floor_area_sqm": 100.0, "state": "active"}
    )
    x.landlord = env["res.partner"].create({"name": "A07P0R Landlord"})
    return x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    cls = g.P03GenericApiController
    mw = getattr(cls.model_write, "original_endpoint", cls.model_write)
    ma = getattr(cls.model_action, "original_endpoint", cls.model_action)
    old = getattr(g, "request", None)
    g.request = types.SimpleNamespace(env=c.cenv)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw)
        )
    finally:
        g.request = old


def _wo(c, user=None, **kw):
    vals = {
        "site_id": c.site.id,
        "company_id": c.co.id,
        "work_type": "repair",
        "description": "A07P0R generator failure",
        "estimated_cost": 20000.0,
    }
    vals.update(kw)
    order = c.env[WO].with_user(user or c.clerk).create(vals)
    # a person's request is triaged first (tested in test_a07_m47_operability.py)
    order.sudo().action_triage("normal")
    return order


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), fn.__self__.env.cr.savepoint():
        fn(*args, **kw)


def _events(c, event_type, res_id):
    rows = c.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


# ================================================================ work order
def test_wo_workflow_fields_cannot_be_forged(c, p03):
    w = _wo(c)
    for vals in (
        {"state": "completed"},
        {"state": "verified"},
        {"completed_by_id": c.clerk2.id},
        {"verified_by_id": c.clerk2.id},
        {"dofa_approved": True},
        {"approval_state": "approved"},
    ):
        _refused(w.with_user(c.clerk2).write, vals, match="cannot be set directly")
    # born completed
    with pytest.raises(UserError, match="cannot be set directly"), c.env.cr.savepoint():
        _wo(c, state="completed", actual_cost=99000.0)
    # the P03 form save
    res = p03.write(model=WO, record_id=w.id, values={"state": "completed", "actual_cost": 1.0})
    w.invalidate_recordset()
    assert w.state == "draft" and res.get("error"), res


def test_wo_wrong_state_transitions_are_refused(c, p03):
    free = _wo(c, estimated_cost=0.0)  # no spend: no approval needed
    _refused(free.action_complete, notes="x", match="cannot be completed")
    _refused(free.action_start, match="cannot be started")
    _refused(free.action_verify, match="cannot be verified")
    _refused(free.action_reopen, reason="x", match="cannot be reopened")
    res = p03.action(model=WO, ids=[free.id], method="action_complete", kwargs={"notes": "x"})
    assert res.get("success") is False, res
    free.action_cancel()
    _refused(free.action_start, match="cannot be started")
    _refused(free.action_schedule, match="cannot be scheduled")
    _refused(free.action_cancel, match="cannot be cancelled")
    done = _wo(c, estimated_cost=0.0)
    done.action_schedule()
    done.action_start()
    # completion needs evidence (BRU-FAC-07)
    _refused(done.action_complete, match="completion evidence")
    done.action_complete(notes="Fuse replaced, photo ref IMG-1")
    _refused(done.action_schedule, match="cannot be scheduled")
    _refused(done.action_cancel, match="cannot be cancelled")


def test_wo_spend_is_approved_routed_and_reapproved_on_overrun(c, p03):
    w = _wo(c)  # BDT 20,000 -> Tier 3 on the repair ladder
    assert w.dofa_tier_required == "tier_3"
    _refused(w.action_schedule, match="sign-off")
    # the approve method is reached only from an inbox task
    _refused(w.with_user(c.t3).action_dofa_approve, match="inbox")
    task = approve_via_inbox(w, c.t3, justification="Generator down, branch on UPS")
    assert task.assigned_user_id == c.t3
    assert w.dofa_approved and w.dofa_approved_by == c.t3
    # the P03 buttons
    for method in ("action_schedule", "action_start"):
        res = p03.action(model=WO, ids=[w.id], method=method)
        assert res.get("success"), (method, res)
    w.invalidate_recordset()
    assert w.state == "in_progress"
    # the actual passes the approved amount: the approval is voided
    w.with_user(c.clerk).write({"actual_cost": 60000.0})
    assert not w.dofa_approved
    _refused(w.with_user(c.clerk).action_complete, notes="done", match="sign-off")
    # re-approval at the new tier, then completion with evidence
    approve_via_inbox(w, c.t4, requester=c.clerk, justification="Alternator also failed")
    res = p03.action(
        model=WO, ids=[w.id], method="action_complete", kwargs={"notes": "Alternator replaced"}
    )
    assert res.get("success"), res
    w.invalidate_recordset()
    assert (w.state, w.completed_by_id, w.completion_notes) == (
        "completed",
        c.clerk,
        "Alternator replaced",
    )
    ev = _events(c, "facility.work_order_completed", w.id)
    assert ev and ev[-1]["cost"] == 60000.0
    # actual cost locked after completion (ORM and P03)
    _refused(w.with_user(c.clerk2).write, {"actual_cost": 1800000.0}, match="cannot be edited")
    res = p03.write(model=WO, record_id=w.id, values={"actual_cost": 1800000.0})
    w.invalidate_recordset()
    assert w.actual_cost == 60000.0 and res.get("error"), res


def test_wo_self_approval_and_self_verification_are_refused(c):
    # a Tier 3 holder raising and requesting their own WO is never routed it
    own = _wo(c, user=c.t3)
    own.with_user(c.t3).action_request_approval(justification="mine")
    assert assigned(own) and c.t3 not in assigned(own)
    _refused(own.with_user(c.t3).action_dofa_approve, match="inbox")
    # the creator is never routed the task
    w = _wo(c, estimated_cost=0.0)
    w.with_user(c.clerk).action_schedule()
    w.with_user(c.clerk2).action_start()
    w.with_user(c.clerk2).action_complete(notes="Done by clerk2")
    # neither the raiser nor the completer verifies
    _refused(w.with_user(c.clerk).action_verify, match="Segregation")
    _refused(w.with_user(c.clerk2).action_verify, match="Segregation")
    w.with_user(c.t3).action_verify(notes="Checked on site")
    assert (w.state, w.verified_by_id) == ("verified", c.t3)
    # verified is final
    _refused(w.with_user(c.t3).action_reopen, reason="x", match="cannot be reopened")
    _refused(w.with_user(c.t3).write, {"state": "in_progress"}, match="cannot be set directly")


def test_wo_reopen_voids_the_completion(c, p03):
    w = _wo(c, estimated_cost=0.0)
    w.action_schedule()
    w.action_start()
    w.action_complete(notes="Painted the wall")
    _refused(w.action_reopen, match="why")
    res = p03.action(model=WO, ids=[w.id], method="action_reopen", kwargs={"reason": "Leak back"})
    assert res.get("success"), res
    w.invalidate_recordset()
    assert (w.state, w.completed_by_id, w.completion_notes) == (
        "in_progress",
        c.env["res.users"],
        False,
    )
    assert _events(c, "facility.work_order_reopened", w.id)[0]["reason"] == "Leak back"
    # it completes again with fresh evidence
    w.action_complete(notes="Pipe resealed")
    assert w.state == "completed"
    # cancel from the workspace
    other = _wo(c, estimated_cost=0.0)
    res = p03.action(model=WO, ids=[other.id], method="action_cancel", kwargs={"reason": "dup"})
    assert res.get("success"), res


# ================================================================ site
def _lease(c, user=None, **kw):
    vals = {
        "site_id": c.site.id,
        "lessor_id": c.landlord.id,
        "start_date": c.today - timedelta(days=365),
        "end_date": c.today + timedelta(days=365),
        "monthly_rent": 100000.0,
        "deposit": 600000.0,
    }
    vals.update(kw)
    return c.env["fix.site.lease"].with_user(user or c.clerk).create(vals)


def test_site_close_needs_checklist_and_cfo_then_ceo(c, p03):
    site = c.site
    _lease(c)
    _wo(c, estimated_cost=0.0).action_schedule()
    c.env["fix.site.licence"].create(
        {"site_id": site.id, "licence_type": "trade", "valid_to": c.today + timedelta(days=60)}
    )
    S = site.with_user(c.clerk)
    # open obligations: refused at request and at close, by ORM and P03
    _refused(S.action_request_approval, match="recovery checklist")
    _refused(S.action_close, match="recovery checklist")
    res = p03.action(model="fix.site", ids=[site.id], method="action_close")
    assert res.get("success") is False, res
    # state cannot be written
    _refused(site.with_user(c.clerk2).write, {"state": "closed"}, match="cannot be set directly")
    S.write(
        {
            "closure_assets_recovered": True,
            "closure_licences_surrendered": True,
            "closure_deposit_settled": True,
            "closure_notes": "Plant moved to Tejgaon; trade licence surrendered; deposit offset",
        }
    )
    # CFO sign-off (Tier 4 only: the Tier 5 CEO signs second)
    S.action_request_approval(justification="Branch consolidation")
    assert assigned(site) == c.t4
    _refused(site.with_user(c.t4).action_approve_status_change, match="inbox")
    approve_via_inbox(site, c.t4)
    assert site.status_cfo_approved_by_id == c.t4
    _refused(S.action_close, match="CEO")
    # CEO sign-off
    S.action_request_approval(justification="Branch consolidation")
    assert assigned(site) == c.t5
    approve_via_inbox(site, c.t5)
    res = p03.action(model="fix.site", ids=[site.id], method="action_close")
    assert res.get("success"), res
    site.invalidate_recordset()
    assert site.state == "closed"
    # the sign-offs were consumed: reopening needs its own
    assert not site.status_cfo_approved_by_id and site.approval_state == "none"
    _refused(S.action_reopen, match="sign-off")
    _refused(site.with_user(c.clerk2).write, {"state": "active"}, match="cannot be set directly")


def test_site_signoff_is_pinned_to_the_checklist(c):
    S = c.site.with_user(c.clerk)
    S.action_request_approval(justification="close")
    approve_via_inbox(c.site, c.t4)
    assert c.site.status_cfo_approved_by_id
    S.write({"closure_notes": "changed after the CFO signed"})
    assert not c.site.status_cfo_approved_by_id and c.site.approval_state == "none"
    # the requester is never the approver
    c.site.with_user(c.t4).action_request_approval(justification="self")
    assert assigned(c.site) and c.t4 not in assigned(c.site)


# ================================================================ capex project
def test_capex_start_needs_approval_and_budget_raise_voids_it(c, p03):
    P = c.env["fix.site.project"].with_user(c.clerk)
    p = P.create({"site_id": c.site.id, "project_type": "open", "budget": 2_000_000.0})
    assert p.dofa_tier_required == "tier_4"
    _refused(p.action_start, match="sign-off")
    _refused(p.with_user(c.clerk2).write, {"state": "done"}, match="cannot be set directly")
    approve_via_inbox(p, c.t4, justification="New Sylhet branch")
    res = p03.action(model="fix.site.project", ids=[p.id], method="action_start")
    assert res.get("success"), res
    p.invalidate_recordset()
    assert p.state == "in_progress"
    # A07 P1 M47-81: another user can no longer raise the budget by a plain write
    # (ORM or P03); the approved budget stands as signed off
    _refused(p.with_user(c.clerk2).write, {"budget": 9_000_000.0}, match="Revise Budget")
    res = p03.write(model="fix.site.project", record_id=p.id, values={"budget": 9_000_000.0})
    p.invalidate_recordset()
    assert res.get("error") and p.budget == 2_000_000.0 and p.dofa_approved, res
    # Revise Budget needs a reason and the Facility Manager role
    p.with_user(c.clerk).write({"budget_proposed": 9_000_000.0})
    _refused(p.with_user(c.clerk).action_revise_budget, match="reason")
    plain = _user(c.env, "a07p1_m47_plain", c.co, c.ou)
    _refused(p.with_user(plain).action_revise_budget, reason="x", match="Facility Manager")
    # the revision withdraws the approval and is recorded
    p.with_user(c.clerk).action_revise_budget(reason="Scope grew: second floor")
    assert p.budget == 9_000_000.0 and not p.dofa_approved
    assert p.budget_revised_by == c.clerk and "Scope grew" in p.budget_revision_note
    _refused(p.action_done, match="sign-off")
    # the reviser moved the amount, so the reviser never decides it; re-approval
    approve_via_inbox(p, c.t4, requester=c.clerk2, justification="Scope grew")
    p.action_done()
    assert p.state == "done" and p.done_on
    _refused(p.with_user(c.clerk2).write, {"state": "planned"}, match="cannot be set directly")


# ================================================================ lease
def test_lease_terms_change_only_through_an_approved_modification(c, p03):
    ls = _lease(c)
    # direct term changes and state forging are refused (ORM and P03)
    _refused(
        ls.with_user(c.clerk2).write,
        {"end_date": c.today + timedelta(days=5 * 365), "monthly_rent": 60000.0},
        match="modification",
    )
    res = p03.write(model="fix.site.lease", record_id=ls.id, values={"monthly_rent": 60000.0})
    ls.invalidate_recordset()
    assert ls.monthly_rent == 100000.0 and res.get("error"), res
    _refused(ls.with_user(c.clerk2).write, {"state": "terminated"}, match="cannot be set directly")
    with pytest.raises(UserError, match="cannot be set directly"), c.env.cr.savepoint():
        _lease(c, state="terminated")
    # nothing to approve until a modification is open
    _refused(ls.action_request_approval, match="Open a modification")
    _refused(ls.write, {"proposed_monthly_rent": 1.0}, match="Open a modification")
    res = p03.action(model="fix.site.lease", ids=[ls.id], method="action_open_modification")
    assert res.get("success"), res
    ls.invalidate_recordset()
    ls.write(
        {
            "proposed_end_date": c.today + timedelta(days=3 * 365),
            "proposed_monthly_rent": 110000.0,
            "modification_reason": "Renewal for 3 years",
        }
    )
    assert ls.dofa_tier_required == "tier_4"  # > BDT 1M remaining commitment
    _refused(ls.action_apply_modification, match="sign-off")
    approve_via_inbox(ls, c.t4, justification="Renewal at market rent")
    # pin: changing the approved proposal voids the approval, even a rent cut
    ls.with_user(c.clerk).write({"proposed_monthly_rent": 90000.0})
    assert not ls.dofa_approved and ls.approval_state == "none"
    approve_via_inbox(ls, c.t4, requester=c.clerk, justification="Negotiated down")
    res = p03.action(model="fix.site.lease", ids=[ls.id], method="action_apply_modification")
    assert res.get("success"), res
    ls.invalidate_recordset()
    assert (ls.end_date, ls.monthly_rent) == (c.today + timedelta(days=3 * 365), 90000.0)
    assert not ls.modification_open and not ls.dofa_approved and ls.approval_state == "none"
    assert _events(c, "lease.modified", ls.id)[0]["after"]["monthly_rent"] == 90000.0
    # terminate needs a reason; terminated is final
    _refused(ls.action_terminate, reason="x", match="Branch Operations Lead")
    _refused(ls.with_user(c.clerk2).action_terminate, match="why")
    ls.with_user(c.clerk2).action_terminate(reason="Landlord sold the building")
    assert ls.state == "terminated"
    _refused(ls.action_open_modification, match="cannot be renewed")


# ================================================================ site asset
def test_asset_retirement_is_dofa_and_restore_is_an_action(c, p03):
    A = c.env["fix.site.asset"].with_user(c.clerk)
    gen = A.create({"site_id": c.site.id, "asset_type": "generator", "value": 4_000_000.0})
    _refused(gen.with_user(c.clerk2).action_retire, match="sign-off")
    _refused(gen.with_user(c.clerk2).write, {"state": "retired"}, match="cannot be set directly")
    approve_via_inbox(gen, c.t4, justification="Beyond economic repair")
    res = p03.action(
        model="fix.site.asset", ids=[gen.id], method="action_retire", kwargs={"reason": "BER"}
    )
    assert res.get("success"), res
    gen.invalidate_recordset()
    assert (gen.state, gen.retire_reason) == ("retired", "BER")
    # restore is an action from maintenance, never a write; retired is final
    _refused(gen.with_user(c.clerk2).write, {"state": "operational"}, match="cannot be set")
    _refused(gen.action_restore, match="under maintenance")
    _refused(gen.with_user(c.clerk2).write, {"value": 1.0}, match="written off")
    ups = A.create({"site_id": c.site.id, "asset_type": "ups"})
    ups.action_maintenance()
    ups.with_user(c.clerk2).action_restore()
    assert ups.state == "operational"


# ================================================================ incident
def test_incident_close_needs_resolution_and_another_closer(c, p03):
    inc = (
        c.env["fix.site.incident"]
        .with_user(c.clerk)
        .create(
            {
                "site_id": c.site.id,
                "incident_type": "injury",
                "severity": "high",
                "description": "Technician fell from ladder",
            }
        )
    )
    _refused(inc.with_user(c.clerk).action_close, resolution="fine", match="Segregation")
    _refused(inc.with_user(c.clerk2).action_close, match="resolution")
    _refused(inc.with_user(c.clerk2).write, {"state": "closed"}, match="cannot be set directly")
    res = p03.write(model="fix.site.incident", record_id=inc.id, values={"state": "closed"})
    inc.invalidate_recordset()
    assert inc.state == "open" and res.get("error"), res
    inc.with_user(c.clerk2).action_close(resolution="Ladder replaced; HSE briefed")
    assert (inc.state, inc.closed_by_id) == ("closed", c.clerk2)
    _refused(inc.with_user(c.clerk2).write, {"resolution": "edited"}, match="closed on")


# ================================================================ building PM
def test_pm_done_only_by_action_and_records_the_date(c):
    pm = (
        c.env["fix.site.pm"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "service_type": "fire", "cost": 36000})
    )
    _refused(pm.with_user(c.clerk2).write, {"state": "done"}, match="cannot be set directly")
    _refused(pm.with_user(c.clerk2).write, {"done_on": c.today}, match="cannot be set directly")
    _refused(pm.action_done, done_on=str(c.today + timedelta(days=2)), match="future")
    pm.with_user(c.clerk2).action_done()
    assert (pm.state, pm.done_on) == ("done", c.today)
    with pytest.raises(ValidationError, match="date"), c.env.cr.savepoint():
        c.env["fix.site.pm"].create({"site_id": c.site.id, "state": "done"})
        c.env.flush_all()


# ================================================================ P03 wiring
def test_p03_surfaces_offer_the_new_actions_only(c):
    from odoo.addons.cd_p03_portal.controllers.a07.m47 import SURFACES

    assert {
        "action_request_approval",
        "action_verify",
        "action_reopen",
        "action_cancel",
    } <= SURFACES[WO]["actions"]
    assert "action_dofa_approve" not in set().union(*(s["actions"] for s in SURFACES.values()))
    assert "action_approve_status_change" not in SURFACES["fix.site"]["actions"]
    for model in ("fix.site", "fix.site.lease", "fix.site.asset", "fix.site.project"):
        assert "action_request_approval" in SURFACES[model]["actions"], model
