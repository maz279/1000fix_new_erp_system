# A02 workflow audit, P1/P2 for M01 (cd_service_order).
#
# B1 routed approvals (manager key, goodwill, rework), B2 hand-back consumers
# and literal events, B3 SLA (default policy, derived holds, supervisor-only
# clock decisions, breach escalation), and the M01 P2 lifecycle repairs
# (estimate send/await, close gate, comeback, cancel cascade, abandoned path,
# work-order dispatch). Each control is tested both ways as NON-ADMIN users;
# events are published here, as S2/S3 will publish them, and delivered by
# the real R8 relay.
# ruff: noqa: F811 - `w` is the shared M01 fixture of test_a02_p0_m01, imported
# so pytest registers it here; each test then names it as a parameter.
from datetime import timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo import Command, fields
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import (  # noqa: F401 (fixture)
    GUARD,
    _user,
    approved,
    attempt,
    device,
    estimate,
    handover_evidence,
    order,
    so_request,
    to_estimating,
    to_ready,
    w,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned

from libs.py.fix_events import publish

INBOX = "approver's inbox"
SUPERVISOR = "cd_service_order.group_so_supervisor"
DISPATCHER = "cd_field_service.group_fix_field_service_manager"
NO_SOURCE = 2147480000  # a source-record id that does not exist
MY_EVENTS = (
    "field.order.completed",
    "workshop.job.delivered",
    "consignment.delivered",
    "sla.instance_breached",
)


def relay(env):
    """Deliver this test's events to the M01 consumers only."""
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "in", MY_EVENTS), ("module", "=", "cd_service_order")])
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return env["fix.event.outbox"].sudo().cron_relay()


def supervisor(w):
    user = _user(w.env, "supervisor", [SUPERVISOR])
    ou = w.branch.operating_unit_id
    if ou and "operating_unit_ids" in user._fields:
        user.write({"operating_unit_ids": [Command.link(ou.id)]})
    return user


# =========================================================================== B1 routed
def test_manager_key_is_given_from_the_inbox_only(w):
    est = estimate(w, to_estimating(order(w)), 30000)
    est.action_send()
    w.env["fix.estimate"].browse(est.id).write({"customer_approval_ref": "portal-OTP"})  # su
    # pressed directly, even by a Tier 2 manager: refused
    assert INBOX in attempt(w, lambda: est.with_user(w.bm).action_manager_approve())
    est.with_user(w.clerk).action_request_manager_key("Board-level repair")
    req = so_request(w, "manager_key", est)
    assert req.approval_state == "pending" and w.bm in assigned(req)
    assert w.clerk not in assigned(req)  # the requester and preparer are never routed to
    assert "already awaiting" in attempt(
        w, lambda: est.with_user(w.clerk).action_request_manager_key("again")
    )
    approve_via_inbox(req, w.bm, requester=w.clerk)
    assert (est.manager_approval_uid, req.approval_state) == (w.bm, "approved")
    assert est.manager_approved_total == est.grand_total


def test_manager_key_request_covers_the_amount_requested(w):
    est = estimate(w, to_estimating(order(w)), 30000)
    est.action_send()
    w.env["fix.estimate"].browse(est.id).write({"customer_approval_ref": "portal-OTP"})
    est.with_user(w.clerk).action_request_manager_key("Board-level repair")
    req = so_request(w, "manager_key", est)
    line = {"line_type": "part", "description": "x", "quantity": 1, "unit_price": 90000}
    est.with_user(w.clerk).write({"line_ids": [Command.create(line)]})
    # the raise voided the customer's approval and outgrew the request
    assert attempt(w, lambda: approve_via_inbox(req, w.bm, requester=w.clerk))
    assert not est.manager_approval_uid


def test_goodwill_and_rework_requests_route_to_a_commercial_approver(w):
    o = to_ready(w, order(w), 10000)
    handover_evidence(w, o)
    assert INBOX in attempt(w, lambda: o.with_user(w.approver).action_approve_goodwill("x"))
    o.with_user(w.clerk).action_request_goodwill("Second visit for the same fault")
    req = so_request(w, "goodwill", o)
    assert assigned(req) == w.approver
    approve_via_inbox(req, w.approver, requester=w.clerk)
    assert o.goodwill_approved_by == w.approver and o.goodwill_cost_attribution_bdt == 11500.0
    o.with_user(w.clerk).action_deliver()
    assert o.payment_settlement_state == "covered_zero_charge"


def test_routed_requests_cannot_be_forged(w):
    o = to_estimating(order(w))
    o.with_user(w.clerk).action_request_goodwill("loyal customer")
    req = so_request(w, "goodwill", o)
    assert GUARD in attempt(w, lambda: req.with_user(w.clerk).write({"amount": 1.0}))
    assert INBOX in attempt(w, lambda: req.with_user(w.approver).action_apply())


# =========================================================================== B2 hand-backs
def test_completed_field_job_moves_the_order_to_qc_once(w):
    o = order(w)
    approved(w, o)
    payload = {"service_order_id": o.id, "field_order_id": NO_SOURCE}
    publish(w.env, "field.order.completed", "fix.field.order", NO_SOURCE, payload)
    relay(w.env)
    assert o.state == "qc_pending"
    publish(w.env, "field.order.completed", "fix.field.order", NO_SOURCE, payload)
    relay(w.env)
    assert o.state == "qc_pending"  # idempotent
    stale = to_estimating(order(w))
    publish(
        w.env, "field.order.completed", "fix.field.order", NO_SOURCE, {"service_order_id": stale.id}
    )
    relay(w.env)
    assert stale.state == "estimate_pending"  # not approved: refused, not moved
    assert "not moved" in (stale.message_ids[:1].body or "")
    assert attempt(
        w,
        lambda: w.env["fix.service.order"]
        .with_user(w.clerk)
        .consume_field_order_completed({"payload": {"service_order_id": o.id}}),
    )


def test_workshop_release_moves_the_order_to_qc_then_ready(w):
    o = order(w)
    approved(w, o)
    o.action_start_repair()
    payload = {"service_order_id": o.id}
    publish(w.env, "workshop.job.delivered", "fix.workshop.job", NO_SOURCE, payload)
    relay(w.env)
    assert o.state == "qc_pending"
    qc = (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "item_ids": [Command.create({"name": "boot", "passed": True})]})
    )
    qc.with_user(w.inspector).action_complete()
    publish(w.env, "workshop.job.delivered", "fix.workshop.job", NO_SOURCE, payload)
    relay(w.env)
    assert o.state == "ready"


def _leg(w, o, kind):
    if "fix.consignment" not in w.env:
        pytest.skip("cd_consignment not installed")
    return (
        w.env["fix.consignment"]
        .sudo()
        .create(
            {
                "consignment_type": kind,
                "scheduled_date": fields.Datetime.now(),
                "dest_branch_id": w.branch.id if kind == "pickup" else False,
                "origin_branch_id": w.branch.id if kind == "delivery" else False,
                "service_order_id": o.id,
                "operating_unit_id": w.branch.operating_unit_id.id,
            }
        )
    )


def _deliver_leg(w, leg, **extra):
    leg._guarded().write(dict({"state": "delivered"}, **extra))  # su: the leg's own path
    publish(
        w.env,
        "consignment.delivered",
        "fix.consignment",
        leg.id,
        {"service_order_id": leg.service_order_id.id},
    )
    relay(w.env)


def test_pickup_holds_the_clock_and_its_delivery_takes_the_order_in(w):
    held = order(w, service_type="collection")
    leg = _leg(w, held, "pickup")
    held.with_user(w.clerk).action_intake()
    assert held.sla_clock_paused and held._fix_sla_hold_reason().startswith("Awaiting pickup")
    _deliver_leg(w, leg)
    assert not held.sla_clock_paused and held.sla_total_paused_minutes >= 0
    draft = order(w, service_type="collection")
    _deliver_leg(w, _leg(w, draft, "pickup"))
    assert draft.state == "intake"


def test_delivery_leg_delivers_only_a_settled_order(w):
    o = to_ready(w, order(w), 3000)
    leg = _leg(w, o, "delivery")
    _deliver_leg(w, leg, pod_verified_at=fields.Datetime.now())
    assert o.state == "ready"  # BDT 3,450 due, nothing settled
    o.with_user(w.cashier).action_mark_settled(amount_bdt=3450.0, reference="CASH-P1-1")
    publish(w.env, "consignment.delivered", "fix.consignment", leg.id, {"service_order_id": o.id})
    relay(w.env)
    assert o.state == "delivered"


def test_m01_events_are_literal_publish_calls():
    root = Path(__file__).resolve().parents[1] / "models"
    for name in ("fix_service_order.py", "fix_estimate.py"):
        src = (root / name).read_text(encoding="utf-8")
        assert "_emit(" not in src.replace('_emit(f"service_order.{state}")', "")
        assert "publish(self.env, event" not in src
    order_src = (root / "fix_service_order.py").read_text(encoding="utf-8")
    for state in ("intake", "ready", "delivered", "closed", "cancelled"):
        assert '"service_order.%s"' % state in order_src


def test_hand_back_consumers_are_registered(w):
    Consumer = w.env["fix.event.consumer"].sudo()
    for event_type, method in (
        ("field.order.completed", "consume_field_order_completed"),
        ("workshop.job.delivered", "consume_workshop_job_delivered"),
        ("consignment.delivered", "consume_consignment_delivered"),
        ("sla.instance_breached", "consume_sla_instance_breached"),
    ):
        assert Consumer.search_count([("event_type", "=", event_type), ("method", "=", method)])


# =========================================================================== B3 SLA
def test_every_order_gets_a_clock_from_the_default_policy(w):
    o = order(w, service_type="web_portal")  # no policy names this channel
    o.with_user(w.clerk).action_intake()
    default = w.env.ref("cd_service_order.sla_policy_m01_default")
    assert o.sla_policy_id == default and o.sla_resolution_deadline
    assert w.env["fix.sla.kpi.instance"].for_record(o)


def test_deferred_hold_is_a_supervisors_and_pauses_the_clock(w):
    boss = supervisor(w)
    o = order(w)
    o.with_user(w.clerk).action_intake()
    assert GUARD in attempt(w, lambda: o.with_user(w.clerk).write({"is_deferred_block": True}))
    assert "Service Supervisor" in attempt(w, lambda: o.with_user(w.clerk).action_defer_order())
    o.with_user(boss).action_defer_order(reason="parts_backorder", notes="LCD on order")
    inst = w.env["fix.sla.kpi.instance"].for_record(o)
    assert o.sla_clock_paused and inst.state == "paused"
    assert inst.pause_reason == "Awaiting parts (deferred hold)"
    assert "Service Supervisor" in attempt(w, lambda: o.with_user(w.clerk).action_resume_order())
    o.with_user(boss).action_resume_order()
    assert not o.sla_clock_paused
    assert w.env["fix.sla.kpi.instance"].for_record(o).state == "in_progress"


def test_sla_clock_decisions_are_a_supervisors(w):
    boss = supervisor(w)
    o = order(w)
    o.with_user(w.clerk).action_intake()
    inst = w.env["fix.sla.kpi.instance"].for_record(o).with_user(w.clerk)
    assert "Service Supervisor" in attempt(w, lambda: inst.succeed())
    assert "Service Supervisor" in attempt(w, lambda: inst.pause("lunch"))
    assert GUARD in attempt(w, lambda: inst.write({"state": "succeeded"}))
    inst.with_user(boss).succeed()
    assert inst.state == "succeeded"


def test_a_breach_escalates_to_the_branch_supervisor_once(w):
    boss = supervisor(w)
    o = order(w)
    o.with_user(w.clerk).action_intake()
    payload = {"res_model": "fix.service.order", "res_id": o.id, "kpi": "resolution"}
    for _ in range(2):
        publish(w.env, "sla.instance_breached", "fix.sla.kpi.instance", NO_SOURCE, payload)
        relay(w.env)
    acts = o.activity_ids.filtered(lambda a: a.user_id == boss and "SLA breached" in a.summary)
    assert len(acts) == 1


# =========================================================================== P2 lifecycle
def test_await_approval_needs_a_valid_estimate_with_the_customer(w):
    o = to_estimating(order(w))
    assert "no estimate to send" in attempt(w, lambda: o.with_user(w.clerk).action_send_estimate())
    assert "not awaiting a decision" in attempt(
        w, lambda: o.with_user(w.clerk).action_await_approval()
    )
    est = estimate(w, o, 2000)
    o.with_user(w.clerk).action_send_estimate()
    o.with_user(w.clerk).action_await_approval()
    assert (est.state, o.state) == ("sent", "awaiting_approval")


def test_cancel_after_repair_refunds_and_returns_the_logistics_leg(w):
    o = to_ready(w, order(w), 3000)
    o.with_user(w.cashier).action_mark_settled(amount_bdt=3450.0, reference="CASH-P1-2")
    leg = _leg(w, o, "delivery")
    leg._guarded().write({"state": "confirmed"})
    o.with_user(w.clerk).action_cancel(reason="customer_declined: will not collect")
    assert (o.state, o.payment_settlement_state) == ("cancelled", "refund_due")
    assert leg.state == "returned"


def _delivered(w, amount=3000):
    o = to_ready(w, order(w), amount)
    due = o._fix_amount_due()
    o.with_user(w.cashier).action_mark_settled(amount_bdt=due, reference="CASH-%d" % o.id)
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    return o


def test_comeback_within_the_repair_warranty_opens_a_linked_rework(w):
    o = _delivered(w)
    assert "no repair warranty" in attempt(
        w, lambda: o.with_user(w.clerk).action_reopen_comeback("x")
    )
    o.with_user(w.clerk).action_issue_repair_warranty()
    ids = o.with_user(w.clerk).action_reopen_comeback("Same charging fault")
    rework = w.env["fix.service.order"].browse(ids)
    assert (rework.rework_of_id, rework.is_rework, rework.state) == (o, True, "intake")
    assert not rework.rework_approved_by  # still charged until an approver confirms it
    assert "open comeback" in attempt(w, lambda: o.with_user(w.clerk).action_reopen_comeback("y"))
    late = _delivered(w)
    late.with_user(w.clerk).action_issue_repair_warranty()
    late._guarded().write({"service_warranty_until": fields.Date.today() - timedelta(days=1)})
    assert "ended" in attempt(w, lambda: late.with_user(w.clerk).action_reopen_comeback("z"))


def test_warranty_job_raises_its_claim_before_it_closes(w):
    if "fix.warranty.claim" not in w.env:
        pytest.skip("cd_warranty_claims not installed")
    o = order(w, dev=device(w, warranty="active"), order_category="warranty")
    to_estimating(o)
    o.with_user(w.clerk).action_send_estimate()
    o.with_user(w.clerk).action_await_approval()
    o.with_user(w.clerk).action_approve()
    o.action_start_repair()
    o.action_submit_qc()
    qc = (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "item_ids": [Command.create({"name": "boot", "passed": True})]})
    )
    qc.with_user(w.inspector).action_complete()
    o.action_ready()
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    o.with_user(w.clerk).action_close()
    claim = w.env["fix.warranty.claim"].sudo().search([("service_order_id", "=", o.id)])
    assert o.state == "closed" and claim


def test_abandoned_devices_are_flagged_only_when_switched_on(w):
    o = to_ready(w, order(w), 3000)
    o._guarded().write({"ready_at": fields.Datetime.now() - timedelta(days=10)})
    Order = w.env["fix.service.order"]
    assert Order._cron_flag_abandoned() == 0 and not o.is_abandoned  # default: off
    w.env["ir.config_parameter"].sudo().set_param("cd_service_order.abandon_after_days", "7")
    assert Order._cron_flag_abandoned() >= 1
    assert o.is_abandoned and "Uncollected 7 days" in o.abandon_reason
    assert GUARD in attempt(w, lambda: o.with_user(w.clerk).write({"is_abandoned": False}))
    o.with_user(w.clerk).action_cancel(reason_code="abandoned")
    assert o.cancel_reason_code == "abandoned"


def test_unrepairable_from_a_failed_qc(w):
    o = order(w)
    approved(w, o)
    o.action_start_repair()
    o.action_submit_qc()
    o.action_qc_fail()
    o.with_user(w.clerk).action_mark_unrepairable("Board corroded after rework")
    assert (o.state, o.cancel_reason_code) == ("cancelled", "unrepairable")


def test_work_order_technician_is_a_dispatchers(w):
    if not w.env.ref(DISPATCHER, raise_if_not_found=False):
        pytest.skip("cd_field_service not installed")
    o = order(w)
    tech = w.env["hr.employee"].create({"name": "A02 P1 Tech"})
    WO = w.env["fix.work.order"]
    assert "dispatcher" in attempt(
        w, lambda: WO.with_user(w.clerk).create({"order_id": o.id, "technician_id": tech.id})
    )
    wo = WO.with_user(w.clerk).create({"order_id": o.id})
    assert GUARD in attempt(w, lambda: wo.with_user(w.clerk).write({"state": "assigned"}))
    assert "dispatcher" in attempt(w, lambda: wo.with_user(w.clerk).action_assign(tech.id))
    dispatcher = _user(w.env, "dispatcher", [DISPATCHER])
    # the M55 roster and M22 certification gates are not the control under test
    cls = type(WO)
    with (
        mock.patch.object(cls, "action_check_technician_availability", lambda s: True, create=True),
        mock.patch.object(cls, "action_check_certification", lambda s: True, create=True),
    ):
        wo.with_user(dispatcher).action_assign(tech.id)
    assert (wo.technician_id, wo.state) == (tech, "assigned")
