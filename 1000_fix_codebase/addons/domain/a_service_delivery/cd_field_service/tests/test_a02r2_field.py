"""A02 ERP audit pass 2 (20 Nov 2026) - M02 findings, as non-admin ORM tests.

  M02-01 (P0, D3)  field cash reaches a drawer only with the order's settlement
                   record; less than due is a part payment (warned)
  M02-02           a job that took money is not cancelled (nor by the cascade)
  M02-03 (D4)      on-site completion is the order's QC and delivery
  M02-04 (D5)      parts not on the approved estimate are refused
  M02-05           site coordinates from the customer; dispatcher's after draft
  M02-06           a failed visit converted to a pickup raises the M03 leg
  M02-07           a re-queued visit loses its evidence
  M02-08           technicians change only their own orders and own pings
  M02-09 (D19)     6 jobs / 8 h (10 h with approved overtime) a day
  M02-10           FTFR from real completions only
  M02-11 (D20)     overdue field cash blocks dispatch; shortage goes to finance
  M02-12 (D21)     the wasted-visit fee and its waiver
  M02-13           the collection is a numbered receipt, recorded once
  M02-15           on time = arrival by the end of the window
  X5-18            the geofence log reads the arrivals, company-fenced

``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (fixtures are imported and used as parameters)
from datetime import timedelta
from unittest.mock import patch

import pytest
from odoo import fields
from odoo.addons.cd_field_service.tests.test_a02_erp_m02 import (  # noqa: F401 (fixture)
    CASHIER_GROUPS,
    _open_shift,
    _user,
    _walk,
    give_evidence,
    refused,
    w,
)
from odoo.exceptions import AccessError, UserError

PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="


def _so_cls(w):
    return type(w.env["fix.service.order"])


def _on_site(w, so=None, tech=None, user=None):
    rec = w.fo("dispatched", tech or w.ea, order_id=(so or w.so()).id)
    _walk(rec, user or w.ua)
    return rec


def _completed_with(w, so, payment):
    rec = _on_site(w, so)
    rec.with_user(w.ua).action_record_collection(payment=payment)
    give_evidence(rec)
    rec.with_user(w.ua).action_complete()
    return rec


# ===================================================== M02-01 / D3 field cash
def test_m02_01_cash_is_not_declared_without_the_orders_settlement(w):
    so = w.so()
    rec = _completed_with(w, so, "cash 2500")
    assert rec.onsite_payment_state == "pending_handover"

    def refuse(self, amount, reference, source):
        raise UserError("Order %s is cancelled; it takes no settlement." % self.name)

    with patch.object(_so_cls(w), "_fix_record_settlement", new=refuse):
        err = refused(w.env, lambda: rec.with_user(w.ua).action_handover_field_cash())
    assert err and "takes no settlement" in err
    assert rec.onsite_payment_state == "pending_handover" and not rec.cash_settlement_ref
    # the legitimate path records it
    rec.with_user(w.ua).action_handover_field_cash()
    assert rec.onsite_payment_state == "pending_acceptance"
    assert rec.cash_settlement_ref == "COD/%s" % rec.name == so.invoice_ref


def test_m02_01_a_declaration_without_a_settlement_is_not_put_in_a_drawer(w):
    """A declaration from before the rule (no settlement recorded): the cashier's
    acceptance records it first, or refuses the cash."""
    so = w.so()
    rec = _completed_with(w, so, "cash 1200")
    shift = _open_shift(w)
    cashier = _user(w, "r2_m02_cashier", *CASHIER_GROUPS)
    rec.sudo()._guarded().write(
        {
            "onsite_payment_state": "pending_acceptance",
            "cash_declared_by_id": w.ua.id,
            "cash_declared_at": fields.Datetime.now(),
        }
    )

    def refuse(self, amount, reference, source):
        raise UserError("Order %s refuses the settlement." % self.name)

    with patch.object(_so_cls(w), "_fix_record_settlement", new=refuse):
        err = refused(w.env, lambda: rec.with_user(cashier).action_accept_field_cash())
    assert err and "refuses the settlement" in err
    assert not shift.field_cash_deposited and not rec.cash_shift_id
    rec.with_user(cashier).action_accept_field_cash()
    assert shift.field_cash_deposited == 1200.0 and rec.cash_settlement_ref


def test_m02_01_a_part_payment_is_warned_and_handed_over(w, monkeypatch):
    so = w.so()
    monkeypatch.setattr(_so_cls(w), "_fix_amount_due", lambda self: 5000.0)
    rec = _on_site(w, so)
    res = rec.with_user(w.ua).action_record_collection(payment="cash 3000")
    assert isinstance(res, dict) and "part payment" in res["warning"]
    assert "BDT 2000.00 stays due" in res["warning"]
    give_evidence(rec)
    rec.with_user(w.ua).action_complete()
    recorded = []

    def part(self, amount, reference, source):
        # S1: a field collection below the amount due is an advance (D3)
        recorded.append((amount, reference, source, self.env.context.get("fd_settlement_tender")))
        return True

    monkeypatch.setattr(_so_cls(w), "_fix_record_settlement", part)
    rec.with_user(w.ua).action_handover_field_cash()
    assert recorded == [(3000.0, "COD/%s" % rec.name, "field_collection", "cash")]
    shift = _open_shift(w)
    posted = []
    orig = type(shift)._post_field_cash

    def spy(self, amount, reference=None):
        posted.append(amount)
        return orig(self, amount, reference=reference)

    monkeypatch.setattr(type(shift), "_post_field_cash", spy)
    cashier = _user(w, "r2_m02_cashier2", *CASHIER_GROUPS)
    rec.with_user(cashier).action_accept_field_cash()
    assert posted == [3000.0] and rec.onsite_payment_state == "settled"


def test_m02_01_more_than_is_still_to_collect_is_refused_on_site(w, monkeypatch):
    """A02 pass 2 review (D20): an over-collection was recorded, the cash
    hand-over then refused it for ever (M01 records no more than is due) and
    the technician got no new cash job."""
    so = w.so()
    monkeypatch.setattr(_so_cls(w), "_fix_amount_due", lambda self: 1000.0)
    rec = _on_site(w, so)
    err = refused(w.env, lambda: rec.with_user(w.ua).action_record_collection(payment="cash 1500"))
    assert err and "more than the BDT 1000.00 still to collect" in err
    assert not rec.onsite_receipt_no and not rec.onsite_collection_amount
    # a part payment already recorded on the order lowers what is still to collect
    so._fix_record_settlement(400.0, "FIELD/R2-EARLIER", source="field_collection")
    err = refused(w.env, lambda: rec.with_user(w.ua).action_record_collection(payment="cash 1000"))
    assert err and "BDT 600.00 still to collect" in err
    # the amount still due is recorded and handed over
    rec.with_user(w.ua).action_record_collection(payment="cash 600")
    give_evidence(rec)
    rec.with_user(w.ua).action_complete()
    rec.with_user(w.ua).action_handover_field_cash()
    assert rec.onsite_payment_state == "pending_acceptance"
    assert so.payment_settlement_state == "settled" and so.amount_settled_bdt == 1000.0


def test_m02_01_an_accepted_part_payment_is_verified_and_booked(w, monkeypatch):
    """A02 pass 2 review: a part payment (D3) was marked settled at the
    cashier's acceptance but never verified on the order, so the order kept
    it as a claim and the balance could never verify it."""
    so = w.so()
    monkeypatch.setattr(_so_cls(w), "_fix_amount_due", lambda self: 5000.0)
    rec = _on_site(w, so)
    rec.with_user(w.ua).action_record_collection(payment="cash 3000")
    give_evidence(rec)
    rec.with_user(w.ua).action_complete()
    rec.with_user(w.ua).action_handover_field_cash()  # M01 records the part payment
    assert (so.payment_settlement_state, so.settlement_verified) == ("partial", False)
    _open_shift(w)
    cashier = _user(w, "r2_m02_cashier3", *CASHIER_GROUPS)
    rec.with_user(cashier).action_accept_field_cash()
    assert rec.onsite_payment_state == "settled"
    assert so.payment_settlement_state == "partial" and so.settlement_verified
    assert so.amount_verified_bdt == 3000.0 and so.settlement_verified_by == cashier
    assert so._fix_amount_outstanding() == 2000.0
    if "fix.ar.receipt" in w.env:
        receipts = w.env["fix.ar.receipt"].search([("source_order_id", "=", so.id)])
        assert sum(receipts.mapped("amount")) == 3000.0  # booked once


# ===================================================== M02-13 receipt
def test_m02_13_the_collection_is_a_numbered_receipt_recorded_once(w):
    rec = _on_site(w)
    rec.with_user(w.ua).action_record_collection(payment="bkash 1500 TRX9R2")
    assert rec.onsite_receipt_no and rec.onsite_receipt_no.startswith("ORC/")
    assert rec.onsite_collected_at
    err = refused(
        w.env, lambda: rec.with_user(w.ua).action_record_collection(payment="bkash 150 TRX9R3")
    )
    assert err and "recorded once" in err
    assert rec.onsite_collection_amount == 1500.0
    assert refused(w.env, lambda: rec.with_user(w.ua).write({"onsite_receipt_no": "X"}))
    event = w.env["fix.event.outbox"].search(
        [("event_type", "=", "field_payment.collected"), ("aggregate_id", "=", rec.id)]
    )
    assert len(event) == 1
    payload = event._relay_event_dict()["payload"]
    assert payload["receipt_no"] == rec.onsite_receipt_no and payload["amount_bdt"] == 1500.0


# ===================================================== M02-02 cancel
def test_m02_02_a_job_that_took_money_is_not_cancelled(w):
    so = w.so()
    rec = _on_site(w, so)
    rec.with_user(w.ua).action_record_collection(payment="cash 800")
    err = refused(w.env, lambda: rec.with_user(w.ud).action_cancel(reason="customer changed mind"))
    assert err and "holds an on-site collection" in err and rec.state == "in_progress"
    # the service order's cancellation cascade stops on it, with the reason
    err = refused(w.env, lambda: so.action_cancel(reason_code="customer_declined"))
    assert err and rec.name in err and so.state != "cancelled"
    # a job with no collection is cancelled as before
    other = _on_site(w, w.so())
    other.with_user(w.ud).action_cancel(reason="duplicate visit")
    assert other.state == "cancelled"


# ===================================================== M02-03 / D4 on-site completion
def test_m02_03_on_site_completion_delivers_the_order(w, monkeypatch):
    so = w.so()
    calls = []

    def complete_onsite(self, field_order):
        calls.append((self.id, field_order.id))
        return True

    monkeypatch.setattr(_so_cls(w), "action_complete_onsite", complete_onsite, raising=False)
    rec = _completed_with(w, so, "none 0")
    Order = w.env["fix.service.order"].sudo()
    res = Order.consume_field_order_completed(
        {"aggregate_id": rec.id, "payload": {"field_order_id": rec.id, "service_order_id": so.id}}
    )
    assert res.get("moved") and calls == [(so.id, rec.id)], res


# ===================================================== M02-04 / D5 parts
def _product(w, code):
    return w.env["product.product"].create(
        {"name": "Part %s" % code, "default_code": code, "type": "consu", "standard_price": 100}
    )


def _approved_estimate(w, so, lines):
    est = w.env["fix.estimate"].create(
        {
            "order_id": so.id,
            "line_ids": [
                (0, 0, {"line_type": "part", "product_id": p.id, "quantity": q, "unit_price": 500})
                for p, q in lines
            ],
        }
    )
    est.sudo().write({"state": "approved"})
    return est


def test_m02_04_only_approved_parts_are_fitted(w, monkeypatch):
    # the M15 issue is A06's; here only the estimate check is under test
    from odoo.addons.cd_field_service.models import fix_field_order_part_m15 as m15

    monkeypatch.setattr(m15.FixFieldOrderPartM15, "_a06_issue_from_m15", lambda self: None)
    so = w.so()
    fan, relay, screw = _product(w, "R2-FAN"), _product(w, "R2-RELAY"), _product(w, "SCREW")
    _approved_estimate(w, so, [(fan, 1)])
    rec = _on_site(w, so)
    Line = w.env["fix.field.order.part"].with_user(w.ua)

    def fit(product, qty=1):
        line = Line.create({"field_order_id": rec.id, "product_id": product.id, "quantity": qty})
        line.action_consume()
        return line

    assert fit(fan).state == "consumed"
    err = refused(w.env, lambda: fit(fan))
    assert err and "covers 1" in err
    err = refused(w.env, lambda: fit(relay))
    assert err and "Revise the estimate" in err
    assert fit(screw).state == "consumed"  # configured consumable (D5)
    # the offline sync is refused before any line exists
    assert rec._fix_part_estimate_problem(relay, 1)
    assert not rec._fix_part_estimate_problem(screw, 5)


# ===================================================== M02-05 coordinates
def test_m02_05_site_coordinates_come_from_the_customer_and_are_the_dispatchers(w):
    so = w.so()
    so.customer_id.sudo().write({"partner_latitude": 23.81, "partner_longitude": 90.41})
    so.branch_id.sudo().write({"zone_id": w.zone.id})
    fo = so.action_create_field_order()
    assert (round(fo.latitude, 2), round(fo.longitude, 2)) == (23.81, 90.41)
    rec = w.fo("dispatched", w.ea)
    err = refused(w.env, lambda: rec.with_user(w.ua).write({"latitude": 22.0}))
    assert err and "dispatcher" in err
    rec.with_user(w.ud).write({"latitude": 23.9, "longitude": 90.5})
    assert rec.latitude == 23.9


def test_m02_05_a_failed_visit_needs_a_site_position_or_a_waiver(w):
    rec = w.fo("en_route", w.ea)
    rec.sudo()._guarded().write({"en_route_at": fields.Datetime.now()})
    vals = {
        "field_order_id": rec.id,
        "exception_type": "customer_absent",
        "reason": "Door locked, phone off",
        "evidence_photo": PNG,
        "latitude": 23.8,
        "longitude": 90.4,
    }
    Visit = w.env["fix.field.visit.exception"].with_user(w.ua)
    err = refused(w.env, lambda: Visit.create(dict(vals)))
    assert err and "no site position" in err
    rec.with_user(w.ud).action_waive_geofence(reason="customer moved flats")
    assert Visit.create(dict(vals)).field_order_id == rec


# ===================================================== M02-06/07 failed visits
def test_m02_07_a_requeued_visit_loses_its_evidence(w):
    rec = _on_site(w)
    give_evidence(rec)
    assert rec.customer_signature_attachment_id and rec.post_work_photo_attachment_id
    w.env["fix.field.visit.exception"].with_user(w.ua).create(
        {
            "field_order_id": rec.id,
            "exception_type": "cannot_parts",
            "reason": "Compressor not on the van",
            "evidence_photo": PNG,
            "latitude": 23.8,
            "longitude": 90.4,
        }
    )
    assert rec.state == "pending_dispatch"
    assert not (rec.customer_signature_attachment_id or rec.post_work_photo_attachment_id)
    assert not (rec.customer_otp_verified or rec.started_work_at or rec.arrival_latitude)


def test_m02_06_convert_to_pickup_raises_the_leg(w):
    so = w.so()
    rec = _on_site(w, so)
    w.env["fix.field.visit.exception"].with_user(w.ua).create(
        {
            "field_order_id": rec.id,
            "exception_type": "cannot_complexity",
            "reason": "Board-level fault, needs the bench",
            "follow_up": "workshop_transfer",
            "evidence_photo": PNG,
            "latitude": 23.8,
            "longitude": 90.4,
        }
    )
    assert rec.state == "cancelled" and "Transfer to the workshop" in rec.cancel_reason
    assert so.field_pickup_requested and so.field_workshop_transfer
    assert so._fix_field_pickup_requested()
    if "consignment_ids" in so._fields:
        legs = so.consignment_ids
        assert legs and legs[0].consignment_type == "pickup"
    event = w.env["fix.event.outbox"].search(
        [("event_type", "=", "field.workshop_transfer_requested")]
    )
    assert event


# ===================================================== M02-08 own orders / pings
def test_m02_08_a_technician_changes_only_his_own_orders(w):
    mine = w.fo("dispatched", w.ea)
    theirs = w.fo("dispatched", w.eb)
    mine.with_user(w.ua).write({"work_summary": "note"})
    # A02 pass 2 review: the own-orders rule was ORed with the operating-unit
    # rule and restricted nothing. The field order's write check refuses now.
    with pytest.raises(AccessError), w.env.cr.savepoint():
        theirs.with_user(w.ua).write({"work_summary": "x"})
    theirs.invalidate_recordset()
    assert theirs.work_summary != "x"
    # he still reads them (his unit), and a dispatcher changes any of them
    assert theirs.with_user(w.ua).read(["name"])
    theirs.with_user(w.ud).write({"work_summary": "dispatcher note"})
    assert theirs.work_summary == "dispatcher note"
    # an unassigned order he raised is his to change
    raised = (
        w.env["fix.field.order"]
        .with_user(w.ua)
        .create({"order_id": w.so().id, "zone_id": w.zone.id, "operating_unit_id": w.ou.id})
    )
    raised.with_user(w.ua).write({"work_summary": "raised by me"})
    err = refused(
        w.env,
        lambda: mine.with_user(w.ua).write(
            {"scheduled_start": fields.Datetime.now() + timedelta(days=2)}
        ),
    )
    assert err and "dispatcher" in err
    Ping = w.env["fix.technician.location"]
    err = refused(
        w.env,
        lambda: Ping.with_user(w.ua).create(
            {"technician_id": w.eb.id, "latitude": 23.8, "longitude": 90.4}
        ),
    )
    assert err and "own location" in err
    old = fields.Datetime.now() - timedelta(days=3)
    ping = Ping.with_user(w.ua).create(
        {"technician_id": w.ea.id, "latitude": 23.8, "longitude": 90.4, "timestamp": old}
    )
    assert ping.timestamp > old  # stamped by the server
    assert refused(w.env, lambda: ping.with_user(w.ua).write({"latitude": 1.0}))


# ===================================================== M02-09 / D19 day limits
def test_m02_09_dispatch_respects_the_working_day(w):
    start = fields.Datetime.now().replace(hour=3, minute=0, second=0, microsecond=0)
    day_orders = []
    for i in range(6):
        fo = w.fo("draft", None, scheduled_start=start + timedelta(minutes=10 * i))
        fo.sudo().write({"scheduled_end": fo.scheduled_start + timedelta(minutes=30)})
        day_orders.append(fo)
    for fo in day_orders:
        fo.with_user(w.ud).action_dispatch(technician_id=w.ea.id)
    seventh = w.fo("draft", None, scheduled_start=start + timedelta(hours=2))
    err = refused(w.env, lambda: seventh.with_user(w.ud).action_dispatch(technician_id=w.ea.id))
    assert err and "at most 6" in err
    # hours: one 9-hour job needs approved overtime, an 11-hour job never goes
    long_job = w.fo("draft", None, scheduled_start=start)
    long_job.sudo().write({"scheduled_end": start + timedelta(hours=9)})
    err = refused(w.env, lambda: long_job.with_user(w.ud).action_dispatch(technician_id=w.eb.id))
    assert err and "overtime" in err
    day = long_job._fix_dhaka_day()
    ot = (
        w.env["fix.overtime.request"]
        .sudo()
        .create({"employee_id": w.eb.id, "date": day, "hours": 2.0, "reason": "backlog"})
    )
    ot.sudo().write({"state": "approved", "approved_hours": 2.0, "decided_by_id": w.ud.id})
    long_job.with_user(w.ud).action_dispatch(technician_id=w.eb.id)
    assert long_job.state == "dispatched"
    too_long = w.fo("draft", None, scheduled_start=start)
    too_long.sudo().write({"scheduled_end": start + timedelta(hours=11)})
    err = refused(w.env, lambda: too_long.with_user(w.ud).action_dispatch(technician_id=w.eb.id))
    assert err and "never more than 10 hours" in err


# ===================================================== M02-11 / D20 field cash
def test_m02_11_overdue_field_cash_blocks_dispatch(w):
    held = _completed_with(w, w.so(), "cash 600")
    held.sudo()._guarded().write({"onsite_collected_at": fields.Datetime.now() - timedelta(days=4)})
    nxt = w.fo("draft", None)
    err = refused(w.env, lambda: nxt.with_user(w.ud).action_dispatch(technician_id=w.ea.id))
    assert err and "hand-in deadline" in err
    # another technician is sent; once accepted into a drawer, A is free again
    held.sudo()._guarded().write({"cash_handed_over_at": fields.Datetime.now()})
    nxt.with_user(w.ud).action_dispatch(technician_id=w.ea.id)
    assert nxt.state == "dispatched"


def test_m02_11_a_confirmed_shortage_is_put_to_finance(w):
    _completed_with(w, w.so(), "cash 900")
    recon = w.env["fix.field.cash.recon"].with_user(w.ua).create({"employee_id": w.ea.id})
    recon.with_user(w.ua).write({"counted_amount": 600.0, "variance_reason": "lost on the bus"})
    recon.with_user(w.ua).action_submit()
    assert recon.variance == -300.0
    finance = _user(w, "r2_m02_fin", "account.group_account_manager")
    recon.with_user(finance).action_confirm()
    todo = recon.activity_ids.filtered(lambda a: "shortage" in (a.summary or "").lower())
    assert todo or recon.shortage_booked


# ===================================================== M02-12 / D21 wasted visit
def test_m02_12_a_wasted_visit_carries_the_fee_a_dispatcher_waives(w):
    w.env["ir.config_parameter"].sudo().set_param("cd_field_service.wasted_visit_fee_bdt", "300")
    rec = _on_site(w)
    visit = (
        w.env["fix.field.visit.exception"]
        .with_user(w.ua)
        .create(
            {
                "field_order_id": rec.id,
                "exception_type": "customer_absent",
                "reason": "Nobody home",
                "evidence_photo": PNG,
                "latitude": 23.8,
                "longitude": 90.4,
            }
        )
    )
    assert visit.wasted_fee_bdt == 300.0 and visit.zone_id == rec.zone_id
    assert refused(w.env, lambda: visit.with_user(w.ua).action_waive_fee(reason="regular customer"))
    visit.with_user(w.ud).action_waive_fee(reason="regular customer, phoned ahead")
    assert visit.fee_waived_by_id == w.ud
    from odoo.addons.cd_p03_portal.controllers.a02 import m02

    rows = m02._field_exceptions_report(w.env)["rows"]
    row = next(r for r in rows if r["exception"] == "Failed visit: Customer absent")
    assert row["waived"] == 300.0 and row["technician"] == w.ea.name


# ===================================================== M02-10 FTFR
def test_m02_10_ftfr_counts_only_real_completions(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m02

    report = m02._ftfr_by_skill_report(w.env)
    for row in report["rows"]:
        assert row["total_jobs"] >= 1  # no skill without a completed job
    before = {r["skill"]: r for r in report["rows"]}
    w.ea.sudo().write({"job_title": "R2 Field AC Engineer"})
    w.eb.sudo().write({"job_title": "R2 Idle Skill"})  # technicians, no completed job
    _completed_with(w, w.so(), "none 0")
    rows = {r["skill"]: r for r in m02._ftfr_by_skill_report(w.env)["rows"]}
    assert rows["R2 Field AC Engineer"]["total_jobs"] == 1
    assert rows["R2 Field AC Engineer"]["first_time_fixes"] == 1
    assert "R2 Field AC Engineer" not in before
    assert "R2 Idle Skill" not in rows  # no fabricated rate for a skill with no job


# ===================================================== M02-15 on time
def test_m02_15_on_time_is_arrival_by_the_window_end(w):
    rec = w.fo("en_route", w.ea)
    now = fields.Datetime.now()
    rec.sudo().write(
        {"scheduled_start": now - timedelta(hours=1), "scheduled_end": now + timedelta(hours=1)}
    )
    rec.sudo()._guarded().write({"arrived_at": now})
    assert rec.on_time_arrival
    rec.sudo().write({"scheduled_end": now - timedelta(minutes=30)})
    assert not rec.on_time_arrival


# ===================================================== X5-18 geofence log
def test_x5_18_the_geofence_log_lists_unproven_arrivals_of_my_companies(w):
    from odoo.addons.cd_p03_portal.controllers.a02 import m02

    rec = w.fo("en_route", w.ea)
    rec.with_user(w.ud).action_waive_geofence(reason="gate code changed")
    rec.with_user(w.ua).action_arrive(position="23.9, 90.5")
    rows = m02._geofence_delay_report(w.env)["rows"]
    mine = [r for r in rows if r["ref"] == rec.name]
    assert mine and mine[0]["event_type"] == "Arrival under dispatcher waiver"
    assert "gate code changed" in mine[0]["detail"]
    other_co = w.env["res.company"].create({"name": "R2 Other Co"})
    rows = m02._geofence_delay_report(w.env(context={"allowed_company_ids": [other_co.id]}))
    assert not [r for r in rows["rows"] if r["ref"] == rec.name]
