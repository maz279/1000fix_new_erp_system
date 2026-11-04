"""A02 audit P1/P2 for M03 Service Logistics (cd_consignment).

B1: the damage-claim payout is a routed M63 approval (inbox only).
B2: consignment.delivered carries the service order; consignment.tamper_detected
    has a reader that puts the hold in the logistics managers' queue.
P2: the hub intake takes the receive weight from the workspace; a courier
    booking moves its consignment; the cycle-time report reads delivered_at.

Every control is tested both ways as non-admin users created in the test
(the fixture is the P0 suite's). ``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (the P0 suite's fixture `w` is imported and used as a parameter)
from datetime import timedelta

from odoo.addons.cd_consignment.tests.test_a02_p0_m03 import events, p03, refused, w  # noqa: F401
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)

ROUTED = "approver's inbox"


# ============================================================ B1 damage claim
def test_claim_payout_refuses_a_direct_press(w, monkeypatch):
    """B1: Approve on the claim no longer grants anything, by ORM or P03."""
    cl = w.claim(4500.0, declared=10000.0)
    err = refused(w.env, lambda: cl.with_user(w.approver_t2).action_approve())
    assert err and ROUTED in err
    err = refused(w.env, lambda: cl.with_user(w.approver_t2).action_dofa_approve())
    assert err and ROUTED in err
    _mw, ma = p03(w, w.approver_t2, monkeypatch)
    res = ma(model="fix.damage.claim", ids=[cl.id], method="action_approve")
    assert not res.get("success"), res
    w.env.invalidate_all()
    assert cl.state == "open" and not cl.approved_by_id and not cl.dofa_approved


def test_claim_payout_is_approved_from_the_inbox(w, monkeypatch):
    """B1: the handler requests from P03; the tier-2 claim approver decides."""
    cl = w.claim(4500.0, declared=10000.0)
    _mw, ma = p03(w, w.clerk, monkeypatch)
    res = ma(
        model="fix.damage.claim",
        ids=[cl.id],
        method="action_request_approval",
        kwargs={"justification": "Hub photos show the crack."},
    )
    w.env.invalidate_all()
    assert res.get("success"), res
    assert cl.approval_state == "pending"
    # the lowest competent tier, and only claim approvers
    assert assigned(cl) == w.approver_t2
    approve_via_inbox(cl, w.approver_t2, requester=w.clerk)
    assert cl.state == "approved" and cl.approval_state == "approved"
    assert cl.approved_by_id == w.approver_t2 and cl.approved_amount == 4500.0
    assert cl.dofa_approved_amount == 4500.0
    # the payout still settles as before, capped at the approved amount
    assert refused(w.env, lambda: cl.with_user(w.manager).action_settle(settled_amount=4600))
    cl.with_user(w.manager).action_settle()
    assert cl.state == "settled" and cl.settled_amount == 4500.0


def test_a_tier_holder_without_the_claim_role_gets_no_task(w):
    tier_only = w.env["res.users"].create(
        {
            "name": "a2p1_tier2_only",
            "login": "a2p1_tier2_only",
            "group_ids": [
                (
                    6,
                    0,
                    [
                        w.env.ref("base.group_user").id,
                        w.env.ref("cd_entity_config.group_dofa_tier_2").id,
                    ],
                )
            ],
            "operating_unit_ids": [(6, 0, w.ou.ids)],
        }
    )
    cl = w.claim(3000.0, declared=10000.0)
    cl.with_user(w.clerk).action_request_approval()
    assert tier_only not in assigned(cl) and w.approver_t2 in assigned(cl)


def test_the_claim_creator_is_never_routed_the_claim(w):
    """SoD survives routing: an approver who raised the claim gets no task."""
    cl = w.claim(4500.0, user=w.approver, declared=10000.0)
    cl.with_user(w.approver).action_request_approval()
    assert assigned(cl) == w.approver_t2
    assert not inbox_task(cl, w.approver)


def test_requested_payout_is_what_the_inbox_approves(w):
    """The approver decides the payout put to them; above the claim is refused,
    and a change while pending withdraws the request."""
    cl = w.claim(10000.0, declared=5000.0)
    assert refused(w.env, lambda: cl.with_user(w.clerk).write({"requested_payout": 20000.0}))
    cl.with_user(w.clerk).write({"requested_payout": 6000.0})
    assert cl.dofa_tier_required == "tier_4"  # above the declared value
    cl.with_user(w.clerk).action_request_approval()
    assert w.approver in assigned(cl)
    cl.with_user(w.clerk).write({"requested_payout": 5000.0})
    assert cl.approval_state == "none"  # voided by the change
    approve_via_inbox(cl, w.approver_t2, requester=w.clerk)
    assert cl.state == "approved" and cl.approved_amount == 5000.0
    # decided: the request is fixed
    assert refused(w.env, lambda: cl.with_user(w.clerk).write({"requested_payout": 4000.0}))


def test_an_inbox_rejection_rejects_the_claim(w):
    cl = w.claim(4500.0, declared=10000.0)
    cl.with_user(w.clerk).action_request_approval()
    task = inbox_task(cl, w.approver_t2)
    assert refused(w.env, lambda: task.with_user(w.approver_t2).action_reject())  # no reason
    task.with_user(w.approver_t2).action_reject(comment="Damage predates pickup")
    assert cl.state == "rejected" and cl.rejection_reason == "Damage predates pickup"
    assert cl.rejected_by_id == w.approver_t2 and cl.approval_state == "rejected"


def test_a_direct_rejection_withdraws_the_pending_request(w):
    cl = w.claim(4500.0, declared=10000.0)
    cl.with_user(w.clerk).action_request_approval()
    cl.with_user(w.approver_t2).action_reject(reason="duplicate claim")
    assert cl.state == "rejected" and cl.approval_state == "none"
    assert cl.approval_request_id.state == "voided"


# ============================================================ B2 events
def _relay(env, *event_types):
    Consumer = env["fix.event.consumer"].sudo()
    mine = Consumer.search([("event_type", "in", list(event_types))])
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active": True, "active_from": env.cr.now() - timedelta(minutes=1)})
    return env["fix.event.outbox"].cron_relay()


def test_delivered_event_carries_the_service_order(w):
    c, code = w.at_door()
    c.with_user(w.rider).action_verify_pod(otp=code)
    (event,) = events(w.env, "consignment.delivered", "fix.consignment", c.id)
    assert event["service_order_id"] == w.order.id
    assert event["consignment_type"] == "delivery" and event["delivered_at"]


def test_tamper_hold_reaches_the_logistics_managers(w):
    """B2: consignment.tamper_detected had no reader."""
    consumer = w.env.ref("cd_consignment.consumer_consignment_tamper_detected")
    assert consumer.method == "consume_tamper_detected"
    c = w.moving(outbound_seal_number="SEAL-T1")
    c.with_user(w.hub).action_verify_hub_intake(inbound_seal="SEAL-T9")
    assert c.state == "held"
    _relay(w.env, "consignment.tamper_detected")
    todo = c.activity_ids.filtered(lambda a: a.user_id == w.manager)
    assert len(todo) == 1 and c.name in todo.summary
    assert not c.activity_ids.filtered(lambda a: a.user_id in (w.hub | w.rider))
    # idempotent: a redelivery schedules nothing more
    (row,) = w.env["fix.event.outbox"].search(
        [("event_type", "=", "consignment.tamper_detected"), ("aggregate_id", "=", c.id)]
    )
    again = w.env["fix.consignment"].sudo().consume_tamper_detected(row._relay_event_dict())
    assert again["scheduled"] == 0
    # the consumer is not callable as a user
    assert refused(
        w.env,
        lambda: w.env["fix.consignment"]
        .with_user(w.manager)
        .consume_tamper_detected(row._relay_event_dict()),
    )
    # releasing the hold closes the to-do
    c.with_user(w.manager).action_release_hold(reason="Seal swapped at origin, photos on file")
    assert not c.activity_ids.filtered(lambda a: a.user_id == w.manager)


# ============================================================ P2 hub intake
def test_hub_intake_takes_the_weight_from_the_workspace(w, monkeypatch):
    """M03-P2: P03 could not send a receive weight, so the gate never ran."""
    c = w.moving(ctype="pickup", outbound_seal_number="SEAL-W1", dispatch_weight_g=500.0)
    _mw, ma = p03(w, w.hub, monkeypatch)
    res = ma(
        model="fix.consignment",
        ids=[c.id],
        method="action_verify_hub_intake",
        kwargs={"inbound_seal": "SEAL-W1"},
    )
    w.env.invalidate_all()
    assert res.get("success") and "receive weight" in res["result"]["warning"], res
    assert c.seal_status == "verified" and "Hub Scan" not in c.custody_summary
    assert refused(w.env, lambda: c.with_user(w.hub).action_confirm_receipt())  # no intake yet
    res = ma(
        model="fix.consignment",
        ids=[c.id],
        method="action_record_receive_weight",
        kwargs={"receive_weight_g": "510"},
    )
    w.env.invalidate_all()
    assert res.get("success") and not (res.get("result") or {}).get("warning"), res
    assert c.receive_weight_g == 510.0 and c.weight_variance_g == 10.0
    assert c.custody_summary.endswith("Hub Scan")
    # a recorded weight is evidence
    err = refused(w.env, lambda: c.with_user(w.hub).action_record_receive_weight("490"))
    assert err and "not replaced" in err
    c.with_user(w.hub).action_confirm_receipt()
    assert c.state == "delivered"


def test_a_workspace_weight_outside_tolerance_holds(w, monkeypatch):
    c = w.moving(dispatch_weight_g=500.0)
    _mw, ma = p03(w, w.hub, monkeypatch)
    res = ma(
        model="fix.consignment",
        ids=[c.id],
        method="action_record_receive_weight",
        kwargs={"receive_weight_g": "560"},
    )
    w.env.invalidate_all()
    assert "Weight Variance" in res["result"]["warning"], res
    assert c.state == "held" and c.seal_status == "tampered_mismatch"
    assert refused(w.env, lambda: c.with_user(w.clerk).action_record_receive_weight("560"))
    # released by a manager, the intake completes without holding it again
    c.with_user(w.manager).action_release_hold(reason="Bubble wrap added at origin")
    assert c.with_user(w.hub).action_verify_hub_intake() is True
    assert c.state == "in_transit" and "Hub Scan" in c.custody_summary


# ============================================================ P2 courier
def _booking(w, c, **kw):
    partner = w.env["fix.courier.partner"].create({"name": "A2P1 Courier", "code": "A2P1C"})
    return (
        w.env["fix.courier.booking"]
        .with_user(w.hub)
        .create({"partner_id": partner.id, "consignment_id": c.id, **kw})
    )


def test_courier_pickup_starts_the_consignment(w, monkeypatch):
    c = w.cons()
    c.with_user(w.hub).action_confirm()
    b = _booking(w, c)
    assert refused(w.env, lambda: b.with_user(w.clerk).action_pick_up())
    _mw, ma = p03(w, w.hub, monkeypatch)
    res = ma(model="fix.courier.booking", ids=[b.id], method="action_pick_up")
    w.env.invalidate_all()
    assert res.get("success"), res
    assert b.state == "picked_up" and c.state == "in_transit"
    assert c.custody_summary == "Picked Up -> In Transit"
    assert c.courier_partner_id == b.partner_id


def test_courier_pod_closes_the_consignment(w):
    """M03-P2: the booking closed, the consignment stayed in transit."""
    c = w.moving()
    b = _booking(w, c)
    # no proof: refused; a booking never closes over a moving consignment
    assert refused(w.env, lambda: b.with_user(w.hub).action_deliver())
    pod = w.env["ir.attachment"].create({"name": "courier-pod.pdf", "raw": b"signed"})
    b.with_user(w.hub).action_record_pod(attachment_id=pod.id)
    b.with_user(w.hub).action_deliver()
    assert b.state == "delivered"
    assert c.state == "delivered" and c.delivered_at and c.pod_verified_by == w.hub
    assert c.custody_summary.endswith("Out for Delivery -> Delivered") and not c.chain_broken
    assert c.waybill_attachment_id == pod
    (event,) = events(w.env, "consignment.delivered", "fix.consignment", c.id)
    assert event["service_order_id"] == w.order.id


def test_a_booking_does_not_close_over_a_held_or_branch_leg(w):
    pod = w.env["ir.attachment"].create({"name": "courier-pod.pdf", "raw": b"signed"})
    held = w.moving(dispatch_weight_g=500.0)
    held.with_user(w.hub).action_verify_hub_intake(receive_weight_g=600)
    b = _booking(w, held)
    b.with_user(w.hub).action_record_pod(attachment_id=pod.id)
    err = refused(w.env, lambda: b.with_user(w.hub).action_deliver())
    assert err and "cannot close while" in err
    branch_leg = w.moving(ctype="pickup")
    b2 = (
        w.env["fix.courier.booking"]
        .with_user(w.hub)
        .create({"partner_id": b.partner_id.id, "consignment_id": branch_leg.id})
    )
    b2.with_user(w.hub).action_record_pod(attachment_id=pod.id)
    err = refused(w.env, lambda: b2.with_user(w.hub).action_deliver())
    assert err and "confirm receipt" in err
    assert branch_leg.state == "in_transit" and b2.state == "booked"


# ============================================================ P2 report
def test_cycle_time_reads_the_delivery_stamp(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m03

    c, code = w.at_door()
    c.with_user(w.rider).action_verify_pod(otp=code)
    stamp = c.delivered_at
    w.env.cr.execute(
        "UPDATE fix_consignment SET write_date = write_date + interval '9 days' WHERE id = %s",
        (c.id,),
    )
    w.env.invalidate_all()
    assert m03._closed_at(c) == stamp
    report = m03._cycle_time_report(w.env)
    assert "delivery stamp" in report["notes"][0]


def test_the_m03_surface_offers_the_routed_buttons(w):
    from odoo.addons.cd_p03_portal.controllers import a02

    claim = a02.SURFACES["fix.damage.claim"]["actions"]
    assert "action_approve" not in claim
    assert {"action_request_approval", "action_recall_approval", "action_settle"} <= claim
    assert "action_pick_up" in a02.SURFACES["fix.courier.booking"]["actions"]
    assert "action_record_receive_weight" in a02.SURFACES["fix.consignment"]["actions"]
