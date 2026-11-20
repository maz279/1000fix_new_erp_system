"""A02 ERP audit pass 2 (20 Nov 2026) - M03 findings, as non-admin ORM tests.

  M03-01/02, X5-04 (D1)  a delivery leg leaves only for a Ready order that is
                         paid / credit-released, or as a cash-on-delivery leg;
                         the COD is recorded on the order at the verified POD
  M03-03                 a courier booking closes only the leg that courier
                         picked up; what a booking is for is fixed
  M03-04                 proof of collection at a pickup
  M03-05 (D22)           the pick & drop tariff charge, waived for warranty/AMC
  M03-07                 no payout to a liable party; a liable rider is recovered
  M03-08 (D20)           a rider holding COD past the hand-in deadline gets no leg
  M03-09                 riders do not assign legs; a rider moves only his own

``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (the P0 suite's fixture `w` is imported and used as a parameter)
import base64
import itertools
from datetime import timedelta

from odoo import fields
from odoo.addons.cd_consignment.models.fix_consignment_release import PICKUP_PROOF_PARAM
from odoo.addons.cd_consignment.tests.test_a02_p0_m03 import events, refused, w  # noqa: F401

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="
)
_SEQ = itertools.count(1)


def _due(w, monkeypatch, amount):
    """The service orders owe ``amount`` (their governing estimate less
    advances); a stand-in for an approved estimate."""
    Order = type(w.env["fix.service.order"])
    monkeypatch.setattr(Order, "_fix_amount_due", lambda self: amount)


def _record_settlement_stub(w, monkeypatch):
    """M01's settlement method (S1 adds source 'cod'); records what it gets."""
    calls = []

    def stub(self, amount, reference, source):
        calls.append(
            (self.id, amount, reference, source, self.env.context.get("fd_settlement_tender"))
        )
        self._guarded().write(
            {
                "payment_settlement_state": "settled",
                "amount_settled_bdt": amount,
                "invoice_ref": reference,
            }
        )
        return True

    Order = type(w.env["fix.service.order"])
    monkeypatch.setattr(Order, "_fix_record_settlement", stub)
    return calls


def _unready_order(w):
    order = w.free_order()
    assert order.state != "ready"
    return order


# ================================================== M03-01 / D1 the release gate
def test_m03_01_a_delivery_leg_waits_for_the_ready_order(w):
    order = _unready_order(w)
    leg = w.cons(service_order_id=order.id)
    err = refused(w.env, lambda: leg.with_user(w.hub).action_confirm())
    assert err and "Ready" in err and leg.state == "draft"
    # the M01 hand-over does not even raise the delivery leg before Ready
    walk_in = w.free_order()
    walk_in.sudo().write({"service_type": "walk_in"})
    leg.sudo().unlink()
    err = refused(w.env, lambda: walk_in.action_create_consignment())
    assert err and "raised once the order is Ready" in err
    # the legitimate path: once Ready (and owing nothing) it leaves
    w.make_ready(order)
    leg2 = w.cons(service_order_id=order.id)
    leg2.with_user(w.hub).action_confirm()
    leg2.with_user(w.rider).action_start_transit()
    assert leg2.state == "in_transit" and not leg2.cod_amount


def test_m03_01_an_unpaid_ready_order_leaves_only_as_cod(w, monkeypatch):
    _due(w, monkeypatch, 2300.0)
    order = w.make_ready(_unready_order(w))
    leg = w.cons(service_order_id=order.id)
    assert leg.cod_amount == 2300.0
    # the rider cannot forge it away
    assert refused(w.env, lambda: leg.with_user(w.hub).write({"cod_amount": 0.0}))
    # a leg whose COD no longer covers what is due does not leave
    leg.sudo()._guarded().write({"cod_amount": 100.0})
    leg.invalidate_recordset()
    monkeypatch.setattr(type(leg), "_m03_set_cod_amount", lambda self: None)
    err = refused(w.env, lambda: leg.with_user(w.hub).action_confirm())
    assert err and "BDT 2300.00 is due" in err
    leg.sudo()._guarded().write({"cod_amount": 0.0})
    err = refused(w.env, lambda: leg.with_user(w.hub).action_confirm())
    assert err and "neither paid, credit-released nor a cash-on-delivery leg" in err


def test_m03_02_the_cod_is_recorded_on_the_order_at_the_pod(w, monkeypatch):
    _due(w, monkeypatch, 1800.0)
    calls = _record_settlement_stub(w, monkeypatch)
    order = w.make_ready(_unready_order(w))
    leg, code = w.at_door(service_order_id=order.id)
    assert leg.cod_amount == 1800.0 and not calls
    leg.with_user(w.rider).action_verify_pod(otp=code)
    assert leg.state == "delivered"
    assert calls == [(order.id, 1800.0, "COD/%s" % leg.name, "cod", "cod")]
    assert leg.cod_collected_at and leg.cod_reference == "COD/%s" % leg.name
    (event,) = events(w.env, "consignment.cod_collected", "fix.consignment", leg.id)
    assert event["amount_bdt"] == 1800.0 and event["rider_id"] == w.rider_emp.id
    # recorded once: a second pass collects nothing more
    leg._m03_record_cod_collection()
    assert len(calls) == 1
    # the M01 hand-back delivers the COD-paid order
    res = (
        w.env["fix.service.order"]
        .sudo()
        .consume_consignment_delivered(
            {"aggregate_id": leg.id, "payload": {"service_order_id": order.id}}
        )
    )
    assert res.get("moved") and order.state == "delivered", res


def test_m03_02_an_order_paid_meanwhile_collects_nothing(w, monkeypatch):
    _due(w, monkeypatch, 900.0)
    calls = _record_settlement_stub(w, monkeypatch)
    order = w.make_ready(_unready_order(w))
    leg, code = w.at_door(service_order_id=order.id)
    # paid at the counter while the rider was on the way
    _due(w, monkeypatch, 0.0)
    leg.with_user(w.rider).action_verify_pod(otp=code)
    assert leg.state == "delivered" and not calls and not leg.cod_amount


# ================================================== M03-03 courier booking
def _partner(w, **kw):
    n = next(_SEQ)
    return w.env["fix.courier.partner"].create(
        {"name": "R2 Courier %d" % n, "code": "R2C%d" % n, **kw}
    )


def test_m03_03_a_booking_closes_only_its_own_picked_up_leg(w):
    partner, other = _partner(w), _partner(w)
    own = w.cons()
    own.with_user(w.hub).action_confirm()
    err = refused(
        w.env,
        lambda: w.env["fix.courier.booking"]
        .with_user(w.hub)
        .create({"partner_id": partner.id, "consignment_id": own.id}),
    )
    assert err and "carried by our rider" in err
    leg = w.cons(rider_id=False)
    leg.with_user(w.hub).action_confirm()
    booking = (
        w.env["fix.courier.booking"]
        .with_user(w.hub)
        .create({"partner_id": partner.id, "consignment_id": leg.id})
    )
    # what the booking is for is fixed once made
    for vals in ({"partner_id": other.id}, {"consignment_id": own.id}, {"cod_amount": 5.0}):
        err = refused(w.env, lambda v=vals: booking.with_user(w.hub).write(v))
        assert err and "cannot change once the booking is made" in err, vals
    # a POD scan on a booking the courier never picked up does not close the leg
    att = (
        w.env["ir.attachment"]
        .with_user(w.hub)
        .create({"name": "pod.png", "raw": PNG, "mimetype": "image/png"})
    )
    att.sudo().write({"res_model": booking._name, "res_id": booking.id})
    booking.with_user(w.hub).action_record_pod(attachment_id=att.id)
    leg.sudo().write({"state": "in_transit"})  # e.g. our rider took it on the road
    err = refused(w.env, lambda: booking.with_user(w.hub).action_deliver())
    assert err and "never picked up" in err
    assert leg.state == "in_transit"


# ================================================== M03-04 proof of collection
def test_m03_04_a_pickup_leaves_the_door_only_with_its_proof(w):
    w.env["ir.config_parameter"].sudo().set_param(PICKUP_PROOF_PARAM, "1")
    leg = w.cons(ctype="pickup", outbound_seal_number=False, dispatch_weight_g=0.0)
    leg.with_user(w.hub).action_confirm()
    err = refused(w.env, lambda: leg.with_user(w.rider).action_start_transit())
    assert err and "sign-off" in err and "photo" in err and "serial" in err
    assert leg.state == "confirmed"
    rider = leg.with_user(w.rider)
    # the customer's code (the rider never sees it: it goes to the phone)
    rider.action_send_pickup_otp()
    code = w.sms[-1][1]
    assert refused(w.env, lambda: rider.action_verify_pickup_otp(otp="000000x"))
    rider.action_verify_pickup_otp(otp=code)
    # a serial that is not the order's device is refused
    err = refused(w.env, lambda: rider.action_scan_pickup_serial(serial="SN-OTHER"))
    assert err and "does not match" in err
    rider.action_scan_pickup_serial(serial=leg.service_order_id.device_serial)
    photo = (
        w.env["ir.attachment"]
        .with_user(w.rider)
        .create({"name": "parcel.png", "raw": PNG, "mimetype": "image/png"})
    )
    elsewhere_err = refused(
        w.env, lambda: rider.action_attach_pickup_evidence(attachment_id=photo.id)
    )
    assert elsewhere_err and "on %s itself" % leg.name in elsewhere_err
    photo.sudo().write({"res_model": leg._name, "res_id": leg.id})
    rider.action_attach_pickup_evidence(attachment_id=photo.id)
    err = refused(w.env, lambda: rider.action_start_transit())
    assert err and "seal" in err and "weight" in err
    # seal and weight are recorded before the confirm in practice; here the hub
    # puts the confirmed leg back to draft to fit them (setup)
    leg.sudo().write({"outbound_seal_number": "SEAL-R2", "dispatch_weight_g": 420.0})
    rider.action_start_transit()
    assert (
        leg.state == "in_transit"
        and leg.pickup_otp_verified_at
        and leg.pickup_proof_by_id == w.rider
    )


# ================================================== M03-05 tariff charge
def test_m03_05_the_tariff_charges_the_leg_at_confirm(w):
    zone = w.env["fix.zone"].create({"name": "R2 Zone", "code": "R2Z"})
    Tariff = w.env["fix.logistics.tariff"]
    assert refused(
        w.env,
        lambda: Tariff.with_user(w.hub).create(
            {"zone_id": zone.id, "weight_from_kg": 0, "weight_to_kg": 5, "charge_bdt": 150}
        ),
    )  # the table is the logistics manager's
    Tariff.with_user(w.manager).create(
        {"zone_id": zone.id, "weight_from_kg": 0, "weight_to_kg": 5, "charge_bdt": 150}
    )
    leg = w.cons(zone_id=zone.id, actual_weight_kg=1.2)
    leg.with_user(w.hub).action_confirm()
    assert leg.logistics_charge_bdt == 150.0 and leg.logistics_tariff_id
    (event,) = events(w.env, "logistics.charge_calculated", "fix.consignment", leg.id)
    assert event["amount_bdt"] == 150.0 and event["service_order_id"] == leg.service_order_id.id
    assert leg.service_order_id._fix_logistics_charges() == 150.0
    assert refused(w.env, lambda: leg.with_user(w.hub).write({"logistics_charge_bdt": 0.0}))
    # a warranty order is waived; no tariff band is no charge (D22 default)
    warranty = w.cons(zone_id=zone.id, actual_weight_kg=1.2)
    # setup: the category (a warranty order needs an active warranty to be set)
    w.env.cr.execute(
        "UPDATE fix_service_order SET order_category = 'warranty' WHERE id = %s",
        (warranty.service_order_id.id,),
    )
    warranty.service_order_id.invalidate_recordset(["order_category"])
    warranty.with_user(w.hub).action_confirm()
    assert warranty.logistics_charge_bdt == 0.0 and "waived" in warranty.logistics_charge_note
    heavy = w.cons(zone_id=zone.id, actual_weight_kg=12.0)
    heavy.with_user(w.hub).action_confirm()
    assert heavy.logistics_charge_bdt == 0.0 and not heavy.logistics_tariff_id


# ================================================== M03-07 liable parties
def test_m03_07_no_payout_to_the_liable_party(w):
    cl = w.claim(3000.0, declared=5000.0, liability="customer")
    err = refused(w.env, lambda: cl.with_user(w.clerk).action_request_approval())
    assert err and "no payout is made to them" in err
    cl.with_user(w.clerk).write({"liability": "branch"})
    cl.with_user(w.clerk).action_request_approval()
    assert cl.approval_state == "pending"


def test_m03_07_a_liable_rider_is_recovered(w):
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    cl = w.claim(2000.0, declared=5000.0, liability="rider")
    cl.with_user(w.clerk).action_request_approval()
    approve_via_inbox(cl, w.approver_t2, requester=w.clerk)
    cl.with_user(w.manager).action_settle()
    (event,) = events(w.env, "damage.claim.rider_recovery_requested", "fix.damage.claim", cl.id)
    assert event["rider_id"] == w.rider_emp.id and event["amount"] == 2000.0


# ================================================== M03-09 rider assignment
def test_m03_09_riders_do_not_assign_legs(w):
    rider2_emp = w.env["hr.employee"].search([("user_id", "=", w.rider2.id)], limit=1)
    leg = w.cons(rider_id=False)
    err = refused(w.env, lambda: leg.with_user(w.rider).write({"rider_id": w.rider_emp.id}))
    assert err and "Hub Operator" in err
    leg.with_user(w.hub).write({"rider_id": rider2_emp.id})
    assert leg.rider_id == rider2_emp
    leg.with_user(w.hub).action_confirm()
    # another rider cannot take it on the road
    err = refused(w.env, lambda: leg.with_user(w.rider).action_start_transit())
    assert err and leg.state == "confirmed"
    leg.with_user(w.rider2).action_start_transit()
    assert leg.state == "in_transit"


# ================================================== M03-08 / D20 COD hand-in
def test_m03_08_a_rider_holding_overdue_cod_gets_no_new_leg(w, monkeypatch):
    held = w.cons()
    held.sudo()._guarded().write(
        {
            "cod_amount": 700.0,
            "cod_collected_at": fields.Datetime.now() - timedelta(days=5),
            "state": "delivered",
        }
    )
    err = refused(w.env, lambda: w.cons())  # the fixture names that rider
    assert err and "hand-in deadline" in err
    leg = w.cons(rider_id=False)
    err = refused(w.env, lambda: leg.with_user(w.hub).write({"rider_id": w.rider_emp.id}))
    assert err and "hand-in deadline" in err
    # handed in (the rider settlement / courier remittance marks it): unblocked
    held._m03_mark_cod_remitted()
    leg.with_user(w.hub).write({"rider_id": w.rider_emp.id})
    assert leg.rider_id == w.rider_emp
    # the deadline alert reaches the logistics manager, once
    held.sudo()._guarded().write({"cod_remitted_at": False})
    assert w.env["fix.consignment"]._cron_alert_overdue_cod() >= 1
    assert w.env["fix.consignment"]._cron_alert_overdue_cod() == 0 or held.activity_ids
