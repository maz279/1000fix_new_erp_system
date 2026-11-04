"""A07 P0 recipe (2026-11-03) M48-2 / M48-3 / M48-5: prescriptive-action
approval on the M63 engine, rule-suppression governance, the alert lifecycle,
and predictions whose outcome and work-order flag only actions set.

Every attacker is a NON-ADMIN user created in the rolled-back transaction
(base.group_user + an operating unit; approvers also hold one DOFA tier group),
because the superuser is trusted by the guards and would hide the gaps. Each
refusal is paired with the proper path working end to end through the
approver's inbox (approve_via_inbox)."""

from __future__ import annotations

import types
import uuid
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
REFUSED = (UserError, ValidationError, AccessError)
# A07 P1 (2026-11-04): the approvers are the spec's roles. A prescriptive
# action goes to the Operations Director (M47) when that role is installed,
# else the DOFA Tier 2 stand-in; a suppression goes to the IoT Manager (CTO).
# The clerks hold the IoT Administrator role (which implies IoT Operator):
# since P1 a plain internal user can no longer author rules, ingest, work the
# alert queue or dispatch, and these suites test the governance on top.
IOT_ADMIN = "cd_stream_registry.group_iot_admin"
T4 = "cd_stream_registry.group_iot_manager"
MODEL = "m26.predictive.maintenance"  # the published M26 PdM model (catalog data)


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED:
        return True
    return False


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    n = {"i": 0}

    def user(*xmlids):
        n["i"] += 1
        login = "a07r48_%d_%s" % (n["i"], TAG)
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [(6, 0, groups)],
                    "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )

    x = types.SimpleNamespace(env=env, user=user)
    x.clerk, x.clerk2 = user(IOT_ADMIN), user(IOT_ADMIN)
    x.t2 = env["fix.iot.action"]._approval_group_xmlid()
    x.mgr = user(x.t2)  # Operations Director (or Tier 2): approves prescriptive actions
    x.cto = user(T4)  # IoT Manager (CTO): approves rule suppressions
    x.equipment = env["fix.equipment"].create(
        {"code": f"R48-EQ-{TAG}", "name": f"R48 Generator {TAG}", "category": "Electrical"}
    )
    x.device = env["fix.iot.device"].create(
        {"name": f"R48 Dev {TAG}", "device_id": f"R48-{TAG}", "equipment_id": x.equipment.id}
    )
    x.stream = env["fix.iot.stream"].create(
        {"device_id": x.device.id, "metric": "vibration", "unit": "mm/s"}
    )
    x.stream.action_activate()
    x.tech = env["hr.employee"].create({"name": f"R48 Technician {TAG}"})
    return x


def pred(c, user=None, **kw):
    vals = {
        "name": f"R48-PDM-{TAG}",
        "equipment_id": c.equipment.id,
        "prediction": "failure_predicted",
        "confidence": 0.8,
        "estimated_days_to_failure": 10,
        "model_name": MODEL,
    }
    vals.update(kw)
    return c.env["fix.predictive.maintenance"].with_user(user or c.clerk).create(vals)


def act(c, user=None, prediction=None, **kw):
    vals = {"prediction_id": (prediction or pred(c, user)).id, "action_type": "replace"}
    vals.update(kw)
    return c.env["fix.iot.action"].with_user(user or c.clerk).create(vals)


def rule(c, user=None, **kw):
    vals = {"stream_id": c.stream.id, "operator": "gt", "threshold": 5.0, "severity": "major"}
    vals.update(kw)
    return c.env["fix.iot.rule"].with_user(user or c.clerk).create(vals)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(u):
        g.request = s.request = types.SimpleNamespace(env=c.env(user=u.id))

    as_user(c.clerk)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), as_user=as_user
        )
    finally:
        g.request, s.request = old_g, old_s


# ================================================== prescriptive action (M48-2)
def test_action_is_approved_only_from_the_inbox(c, p03):
    a = act(c)
    # Pressing Approve is refused for the proposer, another clerk and even a
    # Tier 2 holder: the engine is the only way in.
    for u in (c.clerk, c.clerk2, c.mgr):
        assert refused(c.env, lambda u=u: a.with_user(u).action_approve())
    r = p03.action(model="fix.iot.action", ids=[a.id], method="action_approve")
    assert not r["success"]
    a.invalidate_recordset()
    assert a.state == "proposed" and not a.approved_by


def test_action_state_and_stamps_are_guarded(c, p03):
    assert refused(c.env, lambda: act(c, state="done"))
    assert refused(c.env, lambda: act(c, state="approved"))
    a = act(c)
    for vals in (
        {"state": "dispatched"},
        {"state": "approved"},
        {"approved_by": c.mgr.id},
        {"outcome": "confirmed"},
    ):
        assert refused(c.env, lambda vals=vals: a.with_user(c.clerk).write(vals)), vals
    r = p03.write(model="fix.iot.action", record_id=a.id, values={"state": "approved"})
    a.invalidate_recordset()
    assert "error" in r and a.state == "proposed"
    # The form's echo of the unchanged state is accepted.
    a.with_user(c.clerk).write({"state": "proposed", "notes": "echo"})
    # A P03 create drops the state: the action is born proposed.
    r = p03.write(
        model="fix.iot.action",
        values={"prediction_id": pred(c).id, "action_type": "inspect", "state": "done"},
    )
    assert c.env["fix.iot.action"].browse(r["id"]).state == "proposed"


def test_proposer_and_requester_never_decide(c):
    c.clerk.group_ids = [(4, c.env.ref(c.t2).id)]  # the proposer also holds the approver role
    a = act(c)
    a.with_user(c.clerk).action_request_approval(justification="bearing noise")
    assert a.approval_state == "pending"
    assert c.clerk not in assigned(a) and c.mgr in assigned(a)
    assert not inbox_task(a, c.clerk)
    # A Tier 2 holder who requests someone else's proposal is excluded too.
    b = act(c, user=c.clerk2)
    b.with_user(c.mgr).action_request_approval(justification="noise")
    assert c.mgr not in assigned(b) and c.clerk2 not in assigned(b)


def test_no_approval_on_a_healthy_prediction(c):
    healthy = pred(c, prediction="healthy", confidence=0.97, estimated_days_to_failure=240)
    a = act(c, prediction=healthy)
    assert refused(c.env, lambda: a.with_user(c.clerk).action_request_approval())
    assert a.approval_state == "none"


def test_action_full_path_records_the_outcome(c, p03):
    a = act(c)
    approve_via_inbox(a, c.mgr, requester=c.clerk, justification="vibration trend")
    assert (a.state, a.approval_state, a.approved_by) == ("approved", "approved", c.mgr)
    # Dispatch needs a technician.
    assert refused(c.env, lambda: a.with_user(c.clerk).action_dispatch())
    a.with_user(c.clerk).write({"technician_id": c.tech.id})
    a.with_user(c.clerk).action_dispatch()
    assert a.state == "dispatched" and a.dispatched_on
    assert refused(c.env, lambda: a.with_user(c.clerk).write({"technician_id": False}))
    # Done needs an outcome and a note.
    assert refused(c.env, lambda: a.with_user(c.clerk).action_done())
    assert refused(c.env, lambda: a.with_user(c.clerk).action_done(outcome="confirmed"))
    assert refused(c.env, lambda: a.with_user(c.clerk).action_done_confirmed(note="  "))
    # A07 P1: and outcome evidence.
    assert refused(c.env, lambda: a.with_user(c.clerk).action_done_confirmed(note="worn"))
    a.with_user(c.clerk).write({"outcome_evidence_ref": "JC-48-001"})
    r = p03.action(
        model="fix.iot.action",
        ids=[a.id],
        method="action_done_confirmed",
        kwargs={"note": "bearing worn, replaced"},
    )
    assert r["success"], r
    a.invalidate_recordset()
    p = a.prediction_id
    assert (a.state, a.outcome, a.completed_by) == ("done", "confirmed", c.clerk)
    assert (p.outcome, p.outcome_action_id, p.outcome_recorded_by) == ("confirmed", a, c.clerk)
    assert p.outcome_note == "bearing worn, replaced"
    # Terminal: the terms and the technician no longer change.
    for vals in ({"priority": "high"}, {"technician_id": False}, {"state": "proposed"}):
        assert refused(c.env, lambda vals=vals: a.with_user(c.clerk).write(vals)), vals


def test_not_confirmed_outcome_is_a_false_alarm(c):
    a = act(c, technician_id=c.tech.id)
    approve_via_inbox(a, c.mgr, requester=c.clerk)
    a.with_user(c.clerk2).action_dispatch()
    a.with_user(c.clerk2).write({"outcome_evidence_ref": "JC-48-002"})
    a.with_user(c.clerk2).action_done_not_confirmed(note="no wear found")
    assert a.outcome == "not_confirmed" and a.prediction_id.outcome == "false_alarm"


def test_approved_terms_are_pinned(c):
    a = act(c, action_type="inspect", priority="low")
    approve_via_inbox(a, c.mgr, requester=c.clerk)
    # A07 P1 M48-12: an approved action's terms are refused outright ...
    assert refused(c.env, lambda: a.with_user(c.clerk).write({"priority": "high"}))
    assert (a.state, a.priority) == ("approved", "low")
    # ... and change only after Revise Terms, which needs a reason and withdraws
    # the approval, so the changed terms are approved again.
    assert refused(c.env, lambda: a.with_user(c.clerk).action_revise_terms())
    a.with_user(c.clerk).action_revise_terms(reason="vibration rose: replace, not inspect")
    assert (a.state, a.approval_state, a.approved_by.id) == ("proposed", "none", False)
    assert "vibration rose" in a.revision_note
    a.with_user(c.clerk).write({"priority": "high"})
    # A change while approval is pending voids the request.
    a.with_user(c.clerk).action_request_approval()
    req = a.approval_request_id
    a.with_user(c.clerk).write({"action_type": "replace"})
    assert req.state == "voided" and a.approval_state == "none"
    # The proper path again, then dispatched: a change is refused outright.
    approve_via_inbox(a, c.mgr, requester=c.clerk)
    a.with_user(c.clerk).write({"technician_id": c.tech.id})
    a.with_user(c.clerk).action_dispatch()
    other = pred(c, name=f"R48-PDM2-{TAG}")
    assert refused(c.env, lambda: a.with_user(c.clerk).write({"prediction_id": other.id}))
    assert a.prediction_id != other and a.state == "dispatched"


def test_action_wrong_state_transitions_refused(c):
    a = act(c, technician_id=c.tech.id)
    assert refused(c.env, lambda: a.with_user(c.clerk).action_dispatch())
    assert refused(c.env, lambda: a.with_user(c.clerk).action_done_confirmed(note="x"))
    approve_via_inbox(a, c.mgr, requester=c.clerk)
    assert refused(c.env, lambda: a.with_user(c.clerk).action_request_approval())
    a.with_user(c.clerk).action_dispatch()
    assert refused(c.env, lambda: a.with_user(c.clerk).action_dispatch())


# ================================================== rule governance (M48-3)
def test_rule_state_and_terms_are_guarded(c, p03):
    r = rule(c)  # a new rule is born with its threshold
    assert r.threshold == 5.0
    assert refused(c.env, lambda: rule(c, state="paused"))
    for vals in (
        {"state": "paused"},
        {"threshold": 1e9},
        {"operator": "lt"},
        {"suppressed_by": c.cto.id},
    ):
        assert refused(c.env, lambda vals=vals: r.with_user(c.clerk2).write(vals)), vals
    for vals in ({"state": "paused"}, {"threshold": 1e9}):
        res = p03.write(model="fix.iot.rule", record_id=r.id, values=vals)
        assert "error" in res, (vals, res)
    r.invalidate_recordset()
    assert (r.state, r.threshold, r.operator) == ("active", 5.0, "gt")


def test_pause_needs_reason_and_expiry(c):
    r = rule(c)
    assert refused(c.env, lambda: r.with_user(c.clerk2).action_pause())
    assert refused(c.env, lambda: r.with_user(c.clerk2).action_pause(reason="maintenance"))
    r.with_user(c.clerk2).write({"suppression_until": date.today() - timedelta(days=1)})
    assert refused(c.env, lambda: r.with_user(c.clerk2).action_pause(reason="maintenance"))
    assert r.state == "active" and r.approval_state == "none"


def test_pause_routed_to_someone_other_than_requester_and_author(c):
    r = rule(c)  # authored by clerk
    for u in (c.clerk, c.clerk2):  # author and requester both hold the approving tier
        u.group_ids = [(4, c.env.ref(T4).id)]
    r.with_user(c.clerk2).write({"suppression_until": date.today() + timedelta(days=3)})
    r.with_user(c.clerk2).action_pause(reason="bearing swap, sensor off")
    assert r.approval_state == "pending" and r.state == "active"
    assert c.cto in assigned(r)
    assert c.clerk not in assigned(r) and c.clerk2 not in assigned(r)
    # Still alerting while pending; the requester cannot press approve.
    _, raised = c.stream.ingest(50.0)
    assert len(raised) == 1
    assert refused(c.env, lambda: r.with_user(c.clerk2).action_approve_suppression())
    # The proposal is frozen while pending.
    assert refused(
        c.env,
        lambda: r.with_user(c.clerk2).write(
            {"suppression_until": date.today() + timedelta(days=90)}
        ),
    )
    approve_via_inbox(r, c.cto)
    assert (r.state, r.suppressed_by, r.approval_state) == ("paused", c.cto, "approved")
    _, raised = c.stream.ingest(50.0)
    assert not raised
    # Resuming restores alerting at once. A07 P1: the alert raised before the
    # pause is still open, so the new breach is counted on it (FR-IOT-033).
    alert = c.env["fix.iot.alert"].search([("rule_id", "=", r.id)])
    assert len(alert) == 1 and alert.occurrence_count == 1
    r.with_user(c.clerk).action_activate()
    assert (r.state, r.suppression_kind, r.suppressed_by.id) == ("active", False, False)
    _, raised = c.stream.ingest(50.0)
    assert not raised and alert.occurrence_count == 2


def test_tightening_applies_directly_loosening_is_routed(c):
    r = rule(c)
    r.with_user(c.clerk2).action_change_threshold(threshold="3")
    assert r.threshold == 3.0 and r.approval_state == "none"
    assert refused(c.env, lambda: r.with_user(c.clerk2).action_change_threshold(threshold=10))
    r.with_user(c.clerk2).write(
        {
            "suppression_reason": "known resonance during commissioning",
            "suppression_until": date.today() + timedelta(days=2),
        }
    )
    r.with_user(c.clerk2).action_change_threshold(threshold=10)
    assert (r.threshold, r.proposed_threshold, r.approval_state) == (3.0, 10.0, "pending")
    approve_via_inbox(r, c.cto)
    assert (r.threshold, r.baseline_threshold, r.state) == (10.0, 3.0, "active")
    _, raised = c.stream.ingest(6.0)
    assert not raised
    # The expiry ends it: the next ingest restores the earlier threshold.
    r.sudo().write({"suppression_until": date.today() - timedelta(days=1)})
    _, raised = c.stream.ingest(6.0)
    assert len(raised) == 1
    assert (r.threshold, r.suppressed_by.id, r.suppression_kind) == (3.0, False, False)


def test_tightening_while_pending_voids_the_request(c):
    r = rule(c)
    r.with_user(c.clerk2).write(
        {"suppression_reason": "noisy", "suppression_until": date.today() + timedelta(days=1)}
    )
    r.with_user(c.clerk2).action_change_threshold(threshold=8)
    req = r.approval_request_id
    r.with_user(c.clerk).action_change_threshold(threshold=4)
    assert req.state == "voided" and r.approval_state == "none"
    assert (r.threshold, r.suppression_kind) == (4.0, False)


def test_rejected_suppression_leaves_rule_alerting(c):
    r = rule(c)
    r.with_user(c.clerk2).write({"suppression_until": date.today() + timedelta(days=1)})
    r.with_user(c.clerk2).action_pause(reason="annoying")
    inbox_task(r, c.cto).with_user(c.cto).action_reject(comment="fix the root cause")
    assert (r.state, r.approval_state, r.suppression_kind) == ("active", "rejected", False)


# ================================================== alert lifecycle (M48-3)
def test_alert_resolves_only_after_ack_with_a_note(c, p03):
    rule(c)
    _, raised = c.stream.ingest(10.0)
    assert len(raised) == 1
    alert = raised
    assert refused(
        c.env, lambda: alert.with_user(c.clerk2).action_resolve(resolution_note="cleared")
    )
    for vals in ({"state": "resolved"}, {"resolved_on": fields.Datetime.now()}):
        assert refused(c.env, lambda vals=vals: alert.with_user(c.clerk2).write(vals)), vals
    res = p03.write(model="fix.iot.alert", record_id=alert.id, values={"state": "resolved"})
    alert.invalidate_recordset()
    assert "error" in res and alert.state == "new"
    assert refused(
        c.env,
        lambda: (
            c.env["fix.iot.alert"]
            .with_user(c.clerk)
            .create({"device_id": c.device.id, "message": "born resolved", "state": "resolved"})
        ),
    )
    alert.with_user(c.clerk).action_ack()
    assert (alert.state, alert.acked_by) == ("acked", c.clerk)
    assert refused(c.env, lambda: alert.with_user(c.clerk2).action_resolve())
    alert.with_user(c.clerk2).action_resolve(resolution_note="loose mount tightened")
    assert (alert.state, alert.resolved_by) == ("resolved", c.clerk2)
    assert alert.resolved_on and alert.resolution_note == "loose mount tightened"
    assert refused(c.env, lambda: alert.with_user(c.clerk).write({"severity": "minor"}))


# ================================================== predictions (M48-5)
def test_prediction_outcome_and_wo_flag_set_only_by_actions(c, p03):
    p = pred(c)
    for vals in ({"outcome": "confirmed"}, {"work_order_created": True}):
        assert refused(c.env, lambda vals=vals: p.with_user(c.clerk2).write(vals)), vals
    assert refused(c.env, lambda: pred(c, outcome="confirmed"))
    res = p03.write(
        model="fix.predictive.maintenance", record_id=p.id, values={"outcome": "confirmed"}
    )
    p.invalidate_recordset()
    assert "error" in res and p.outcome == "pending"
    p.with_user(c.clerk2).action_create_preventive_wo()
    assert p.work_order_created is True


@pytest.mark.parametrize(
    "vals",
    [{"confidence": 5.0}, {"confidence": -0.1}, {"estimated_days_to_failure": -30}],
)
def test_prediction_score_bounds(c, vals):
    assert refused(c.env, lambda: pred(c, **vals))
    p = pred(c, confidence=1.0, estimated_days_to_failure=0)
    assert refused(c.env, lambda: p.with_user(c.clerk).write(vals))
    assert pred(c, confidence=0.0).confidence == 0.0


# ================================================== stream / adapter / device
def test_stream_adapter_device_state_guarded(c):
    s = (
        c.env["fix.iot.stream"]
        .with_user(c.clerk)
        .create({"device_id": c.device.id, "metric": "temperature"})
    )
    assert refused(
        c.env,
        lambda: (
            c.env["fix.iot.stream"]
            .with_user(c.clerk)
            .create({"device_id": c.device.id, "metric": "humidity", "state": "active"})
        ),
    )
    assert refused(c.env, lambda: s.with_user(c.clerk).write({"state": "active"}))
    s.with_user(c.clerk).action_activate()
    assert s.state == "active"
    ad = c.env["fix.iot.adapter"].with_user(c.clerk).create({"name": f"R48 ADP {TAG}"})
    assert refused(c.env, lambda: ad.with_user(c.clerk).write({"state": "disabled"}))
    assert refused(c.env, lambda: ad.with_user(c.clerk).action_enable())
    ad.with_user(c.clerk).action_disable()
    assert ad.state == "disabled"
    assert refused(c.env, lambda: c.device.with_user(c.clerk).write({"status": "offline"}))
