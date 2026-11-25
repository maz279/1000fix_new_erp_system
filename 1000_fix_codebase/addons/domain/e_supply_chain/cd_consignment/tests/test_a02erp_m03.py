"""A02 ERP audit (19 Nov 2026) - M03 Service Logistics, findings M03-F1..F7,
F10, F11 and the M03 side of F20/F21.

Every control is exercised through the ORM as a non-admin user created by
the P0 fixture (``w``), with the legitimate path alongside. ``odoo_env``
rolls back after every test.
"""

# ruff: noqa: F811  (the P0 suite's fixture `w` is imported and used as a parameter)
import base64
import itertools
from datetime import timedelta

from odoo import fields
from odoo.addons.cd_consignment.tests.test_a02_p0_m03 import events, refused, w  # noqa: F401

PDF = base64.b64encode(b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF").decode()


def _pickup(w, **kw):
    """A pickup leg (ends at our hub), in transit with the rider."""
    return w.moving(ctype="pickup", **kw)


# ============================================================ F1 hub scan
def test_f1_hub_scan_cannot_be_typed(w):
    c = _pickup(w)
    err = refused(
        w.env,
        lambda: w.env["fix.custody.scan"]
        .with_user(w.hub)
        .create({"consignment_id": c.id, "step": "hub_scan"}),
    )
    assert err and "recorded by its transition" in err
    assert "hub_scan" not in c.custody_ids.mapped("step")


def test_f1_receipt_needs_the_completed_intake(w):
    c = _pickup(w, outbound_seal_number="SEAL-F1", dispatch_weight_g=500.0)
    # the seal alone: the intake is incomplete, nothing is stamped
    c.with_user(w.hub).action_verify_hub_intake(inbound_seal="SEAL-F1")
    assert c.seal_status == "verified" and "hub_scan" not in c.custody_ids.mapped("step")
    assert refused(w.env, lambda: c.with_user(w.hub).action_confirm_receipt())
    # even with a hub scan on the chain (the old bypass), the missing weight refuses
    c._scan("hub_scan")
    err = refused(w.env, lambda: c.with_user(w.hub).action_confirm_receipt())
    assert err and "receive weight" in err
    c.with_user(w.hub).action_verify_hub_intake(receive_weight_g=505)
    c.with_user(w.hub).action_confirm_receipt()
    assert c.state == "delivered"


def test_f1_a_failed_seal_needs_the_released_hold(w):
    c = _pickup(w, outbound_seal_number="SEAL-F1B", dispatch_weight_g=500.0)
    c.with_user(w.hub).action_verify_hub_intake(inbound_seal="SEAL-OTHER", receive_weight_g=500)
    assert c.state == "held"
    c.with_user(w.manager).action_release_hold(reason="Seal replaced at origin, photos on file")
    c.with_user(w.hub).action_verify_hub_intake()
    c.with_user(w.hub).action_confirm_receipt()
    assert c.state == "delivered"


# ============================================================ F2 dispatch evidence
def test_f2_dispatch_evidence_is_fixed_from_confirm(w):
    draft = w.cons(outbound_seal_number="SEAL-F2")
    draft.with_user(w.hub).write({"outbound_seal_number": "SEAL-F2B"})  # draft: allowed
    draft.with_user(w.hub).action_confirm()
    for vals in (
        {"outbound_seal_number": "SEAL-F2C"},
        {"dispatch_weight_g": 10.0},
        {"declared_value_bdt": 99999.0},
    ):
        err = refused(w.env, lambda v=vals: draft.with_user(w.hub).write(v))
        assert err and "confirmed for dispatch" in err, vals
    assert draft.outbound_seal_number == "SEAL-F2B"


def test_f2_start_transit_runs_the_dispatch_gates_again(w):
    from odoo.addons.cd_consignment.models.fix_logistics_controls import HIGH_VALUE_PARAM

    w.env["ir.config_parameter"].sudo().set_param(HIGH_VALUE_PARAM, "50000")
    c = w.cons()
    c.with_user(w.hub).action_confirm()
    # the high-value policy changes before the hand-over: the leg is now
    # high value with no insurance and no countersignature
    w.env["ir.config_parameter"].sudo().set_param(HIGH_VALUE_PARAM, "500")
    c.invalidate_recordset(["high_value"])
    err = refused(w.env, lambda: c.with_user(w.rider).action_start_transit())
    assert err and "BRU-LOG-03" in err
    assert c.state == "confirmed"


# ============================================================ F3 one live leg
def test_f3_one_device_one_live_leg_on_every_create_path(w):
    first = w.cons()
    for env in (w.env, w.env(user=w.hub.id)):
        err = refused(
            w.env,
            lambda e=env: e["fix.consignment"].create(
                {
                    "consignment_type": "branch_transfer",
                    "scheduled_date": fields.Datetime.now(),
                    "operating_unit_id": w.ou.id,
                    "service_order_id": first.service_order_id.id,
                    "declared_value_bdt": 500.0,
                }
            ),
        )
        assert err and "one leg at a time" in err
    # moving the order onto another live leg is refused too
    other = w.cons()
    assert refused(
        w.env,
        lambda: other.write({"service_order_id": first.service_order_id.id}),
    )
    # once the first leg is closed, the next leg is raised
    first.with_user(w.hub).action_confirm()
    first.with_user(w.hub).action_return(reason="customer cancelled the pickup")
    assert first.state == "returned"
    nxt = w.cons(service_order_id=first.service_order_id.id)
    assert nxt.state == "draft"


# ============================================================ F4 returns
def test_f4_a_return_closes_only_on_the_origin_receipt(w):
    c = w.moving()
    c.with_user(w.hub).action_return(reason="customer absent")
    assert c.state == "returning" and c.rto_flag
    assert not events(w.env, "consignment.returned", "fix.consignment", c.id)
    assert "returned" not in c.custody_ids.mapped("step")
    # still live: no second leg for the device, no typed scans
    assert refused(w.env, lambda: w.cons(service_order_id=c.service_order_id.id))
    assert refused(
        w.env,
        lambda: w.env["fix.custody.scan"]
        .with_user(w.rider)
        .create({"consignment_id": c.id, "step": "out_for_delivery"}),
    )
    # the rider who carried it does not sign its arrival
    rider_hub = w.rider_emp.user_id
    rider_hub.group_ids = [(4, w.env.ref("cd_consignment.group_fix_logistics_hub").id)]
    err = refused(w.env, lambda: c.with_user(rider_hub).action_receive_return())
    assert err and "Segregation of duties" in err
    c.with_user(w.hub).action_receive_return()
    assert c.state == "returned"
    assert c.custody_ids.sorted("id")[-1].step == "returned"
    (event,) = events(w.env, "consignment.returned", "fix.consignment", c.id)
    assert event["service_order_id"] == c.service_order_id.id
    assert refused(w.env, lambda: c.with_user(w.hub).action_receive_return())


def test_f4_a_leg_that_never_left_closes_at_once(w):
    c = w.cons()
    c.with_user(w.hub).action_confirm()
    c.with_user(w.hub).action_return(reason="customer cancelled")
    assert c.state == "returned"
    assert events(w.env, "consignment.returned", "fix.consignment", c.id)


def test_f4_a_lost_leg_opens_its_claim(w):
    c = w.moving(declared_value_bdt=7500.0)
    c.with_user(w.hub).action_report_lost(reason="bike accident, parcel missing")
    (event,) = events(w.env, "consignment.lost", "fix.consignment", c.id)
    Cons = w.env["fix.consignment"].sudo()
    res = Cons.consume_lost({"aggregate_id": c.id, "payload": event})
    claim = w.env["fix.damage.claim"].browse(res["claim"])
    assert claim.consignment_id == c and claim.state == "open"
    assert claim.damage_kind == "missing" and claim.liability == "pending"
    assert claim.claimed_amount == 7500.0 and claim.claimant == "customer"
    # idempotent: the relay may deliver twice
    again = Cons.consume_lost({"aggregate_id": c.id, "payload": event})
    assert again["claim"] == claim.id and again["scheduled"] == 0
    assert len(c.damage_claim_ids) == 1
    # the relay only
    assert refused(w.env, lambda: Cons.with_user(w.manager).consume_lost({"aggregate_id": c.id}))


# ============================================================ F5 carrier fixed
def test_f5_rider_and_courier_are_fixed_in_custody(w):
    rider2_emp = w.env["hr.employee"].search([("user_id", "=", w.rider2.id)], limit=1)
    partner = w.env["fix.courier.partner"].create({"name": "F5 Courier", "code": "F5C"})
    planned = w.cons()
    planned.with_user(w.hub).action_confirm()
    planned.with_user(w.hub).write({"rider_id": rider2_emp.id})  # before custody: allowed
    c = w.moving()
    for vals in ({"rider_id": rider2_emp.id}, {"courier_partner_id": partner.id}):
        err = refused(w.env, lambda v=vals: c.with_user(w.manager).write(v))
        assert err and "in custody" in err, vals
    assert c.rider_id == w.rider_emp


# ============================================================ F6 bookings
_SEQ = itertools.count(1)


def _booking(w, consignment=None):
    n = next(_SEQ)
    partner = w.env["fix.courier.partner"].create(
        {"name": "F6 Courier %d" % n, "code": "F6C%d" % n}
    )
    return (
        w.env["fix.courier.booking"]
        .with_user(w.hub)
        .create(
            {"partner_id": partner.id, "consignment_id": consignment.id if consignment else False}
        )
    )


def test_f6_cancel_and_return_are_reachable(w):
    b = _booking(w)
    assert refused(w.env, lambda: b.with_user(w.hub).action_cancel())  # no reason
    b.with_user(w.hub).action_cancel(reason="customer brought it in")
    assert b.state == "cancelled" and b.close_reason == "customer brought it in"
    b2 = _booking(w)
    assert refused(
        w.env, lambda: b2.with_user(w.hub).action_mark_returned(reason="x")
    )  # not picked
    b2.with_user(w.hub).action_pick_up()
    b2.with_user(w.hub).action_mark_returned(reason="recipient refused")
    assert b2.state == "returned"


def test_f6_a_booking_closes_with_its_consignment(w):
    c = w.cons(rider_id=False)  # a courier leg (A02 pass 2 M03-03)
    c.with_user(w.hub).action_confirm()
    b = _booking(w, c)
    b.with_user(w.hub).action_pick_up()
    assert c.state == "in_transit" and c.courier_partner_id == b.partner_id
    err = refused(w.env, lambda: b.with_user(w.hub).action_mark_returned(reason="back"))
    assert err and "follows consignment" in err
    c.with_user(w.hub).action_return(reason="address not found")
    assert b.state == "picked_up"  # the parcel is not back yet
    c.with_user(w.hub).action_receive_return()
    assert b.state == "returned" and "address not found" in b.close_reason
    lost = w.cons(rider_id=False)
    lost.with_user(w.hub).action_confirm()
    b2 = _booking(w, lost)
    lost.with_user(w.hub).action_report_lost(reason="never collected")
    assert b2.state == "cancelled"


# ============================================================ F7 POD scan
def test_f7_the_pod_is_a_scan_uploaded_on_the_booking(w):
    b = _booking(w)
    Att = w.env["ir.attachment"].with_user(w.hub)
    elsewhere = Att.create({"name": "logo.pdf", "datas": PDF})
    err = refused(w.env, lambda: b.with_user(w.hub).action_record_pod(attachment_id=elsewhere.id))
    assert err and "on booking" in err
    text = Att.create(
        {"name": "x.txt", "datas": base64.b64encode(b"hello").decode(), "mimetype": "text/plain"}
    )
    text.sudo().write({"res_model": b._name, "res_id": b.id})
    assert refused(w.env, lambda: b.with_user(w.hub).action_record_pod(attachment_id=text.id))
    scan = Att.create({"name": "pod.pdf", "datas": PDF, "mimetype": "application/pdf"})
    scan.sudo().write({"res_model": b._name, "res_id": b.id})
    b.with_user(w.hub).action_record_pod(attachment_id=scan.id)
    assert b.pod_attachment_id == scan
    # one scan proves one booking
    b2 = _booking(w)
    scan2 = Att.create({"name": "pod2.pdf", "datas": PDF, "mimetype": "application/pdf"})
    scan2.sudo().write({"res_model": b2._name, "res_id": b2.id})
    b2.with_user(w.hub).action_record_pod(attachment_id=scan2.id)
    scan.sudo().write({"res_id": b2.id})  # the used scan, re-filed on b2
    err = refused(w.env, lambda: b2.with_user(w.hub).action_record_pod(attachment_id=scan.id))
    assert err and "already proves" in err


# ============================================================ F10 aggregate cap
def test_f10_claims_on_one_leg_share_its_insured_value(w):
    first = w.claim(4000.0, declared=5000.0)
    assert first.dofa_tier_required == "tier_2"
    second = w.claim(4000.0, consignment=first.consignment_id)
    # 5,000 insured, 4,000 already claimed: the second payout is above the
    # 1,000 left, so it needs the above-insured tier (never below Tier 4)
    assert second._claim_ceiling() == 1000.0
    assert second.dofa_tier_required in ("tier_4", "tier_5")
    # a rejected claim takes nothing out of the insured value
    first.with_user(w.approver_t2).action_reject(reason="duplicate")
    second.invalidate_recordset()
    assert second._claim_ceiling() == 5000.0
    assert second.dofa_tier_required == "tier_2"


def test_f10_a_settlement_elsewhere_reopens_the_tier(w):
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    b = w.claim(3000.0, declared=5000.0)
    b.with_user(w.clerk).action_request_approval()
    approve_via_inbox(b, w.approver_t2, requester=w.clerk)
    assert b.state == "approved" and b.dofa_approved_tier == "tier_2"
    # a second claim on the same leg: 2,000 of insured value left for it
    a = w.claim(3000.0, consignment=b.consignment_id)
    assert a._claim_ceiling() == 2000.0
    a.with_user(w.clerk).action_request_approval()
    approve_via_inbox(a, w.approver, requester=w.clerk)
    a.with_user(w.manager).action_settle()
    # b's tier-2 approval no longer covers it: 3,000 paid already of 5,000
    b.invalidate_recordset()
    err = refused(w.env, lambda: b.with_user(w.manager).action_settle())
    assert err and "approved at" in err
    assert b.state == "approved"


# ============================================================ F11 liability
def test_f11_a_payout_needs_a_decided_liability(w):
    cl = w.claim(3000.0, declared=5000.0, liability="pending")
    err = refused(w.env, lambda: cl.with_user(w.clerk).action_request_approval())
    assert err and "decide who is liable" in err
    cl.with_user(w.clerk).write({"liability": "branch"})
    cl.with_user(w.clerk).action_request_approval()
    assert cl.approval_state == "pending"


def test_f11_the_courier_cannot_claim_its_own_liability(w):
    err = refused(w.env, lambda: w.claim(3000.0, declared=5000.0, claimant="courier"))
    assert err and "payee and the debtor" in err
    cl = w.claim(3000.0, declared=5000.0, claimant="courier", liability="branch")
    assert refused(w.env, lambda: cl.with_user(w.clerk).write({"liability": "carrier"}))


# ============================================================ F20/F21 KPI + reports
def test_f20_on_time_is_judged_against_the_promise(w):
    from odoo.addons.cd_consignment.models.fix_consignment_ext import OWN_FLEET_SLA_PARAM
    from odoo.addons.cd_p03_portal.controllers.a02 import m03

    params = w.env["ir.config_parameter"].sudo()
    params.set_param(OWN_FLEET_SLA_PARAM, "")
    c, code = w.at_door()
    c.with_user(w.rider).action_verify_pod(otp=code)
    # only this leg in the company's delivered set (the DB may hold others)
    elsewhere = w.env["res.company"].create({"name": "A02 F20 Elsewhere"})
    w.env.cr.execute(
        "UPDATE fix_consignment SET company_id = %s WHERE state = 'delivered' AND id != %s",
        (elsewhere.id, c.id),
    )
    w.env.invalidate_all()
    # stamped at creation, delivered seconds later: the old KPI judged it late
    assert c.delivered_at >= c.scheduled_date
    # no promise configured: not judged (never reported as 0% on time)
    assert m03._cons(w.env).browse(c.id)._m03_due_at() is None
    params.set_param(OWN_FLEET_SLA_PARAM, "24")
    assert m03.kpis(w.env)["on_time_delivery"] == 100.0
    late = w.env["fix.consignment"].browse(c.id)
    late._guarded().write({"delivered_at": c.scheduled_date + timedelta(hours=30)})
    assert m03.kpis(w.env)["on_time_delivery"] == 0.0


def test_f21_reports_stay_in_the_callers_companies(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m03

    c = w.moving()
    c.with_user(w.hub).action_report_lost(reason="F21 probe")
    other = w.env["res.company"].create({"name": "A02 F21 Other Co"})
    mine = w.env
    theirs = w.env(context=dict(w.env.context, allowed_company_ids=[other.id]))

    def names(env, report):
        rows = m03.REPORTS[report](env)["rows"]
        return " ".join(str(v) for r in rows for v in r.values())

    for report in ("custody_exceptions", "manifest_register", "damage_claims"):
        assert c.name in names(mine, report), report
        assert c.name not in names(theirs, report), report
    # the rider's day is grouped by rider, not by leg
    assert w.rider_emp.name in names(mine, "rider_day")
    assert w.rider_emp.name not in names(theirs, "rider_day")
    # the period: a leg raised today is outside last year
    year_ago = (fields.Date.today() - timedelta(days=400)).isoformat()
    rows = m03.REPORTS["manifest_register"](mine, date_from=year_ago, date_to=year_ago)["rows"]
    assert c.name not in [r["name"] for r in rows]
