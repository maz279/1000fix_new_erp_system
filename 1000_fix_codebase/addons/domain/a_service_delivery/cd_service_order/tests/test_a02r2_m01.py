# A02 ERP audit, pass 2 (20 Nov 2026): M01 service orders (stream S1).
#
# Every control is tested both ways as NON-ADMIN users with their real roles:
# the bypass is refused, the legitimate path works. Owner decisions D1, D3,
# D4, D6, D12, D13. ``odoo_env`` rolls back after each test.

# ruff: noqa: F811  (the imported fixture is used as a parameter)
import base64
import json
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import (  # noqa: F401
    _PNG_B64,
    _user,
    approved,
    attempt,
    device,
    estimate,
    handover_evidence,
    order,
    to_estimating,
    to_ready,
    w,
)
from odoo.addons.cd_service_order.tests.test_a02_p1p2_cd_service_order import supervisor


def _image(w, o=None, name="photo.png"):
    vals = {"name": name, "datas": _PNG_B64, "mimetype": "image/png"}
    if o:
        vals.update(res_model=o._name, res_id=o.id)
    return w.env["ir.attachment"].create(vals)


def _force_state(o, state):
    """A legacy row in ``state`` (the transition map is not under test)."""
    o.env.cr.execute("UPDATE fix_service_order SET state=%s WHERE id=%s", (state, o.id))
    o.invalidate_recordset()


def _payload(ev):
    payload = ev.payload
    return json.loads(payload) if isinstance(payload, str) else payload


def _events(w, event_type, aggregate_id):
    return (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)])
    )


def _deliver(w, o, amount=3000):
    """Ready -> paid at the counter -> handed over."""
    to_ready(w, o, amount)
    due = o._fix_amount_due()
    o.with_user(w.cashier).action_mark_settled("POS-%d" % o.id, due, tender="cash")
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered"
    return o


# ===================================================== M01-02: customer / device
def test_m01_02_customer_and_device_are_fixed_after_intake(w):
    o = order(w, state="intake")
    other = w.env["res.partner"].create({"name": "Someone Else", "phone": "01711000888"})
    assert "Correct Customer / Device" in attempt(
        w, lambda: o.with_user(w.clerk).write({"customer_id": other.id})
    )
    assert "Correct Customer / Device" in attempt(
        w, lambda: o.with_user(w.clerk).write({"device_id": device(w).id})
    )
    # a draft is still being taken in: it may change
    draft = order(w)
    draft.with_user(w.clerk).write({"customer_id": other.id})
    assert draft.customer_id == other


def test_m01_02_supervisor_corrects_before_the_estimate_and_voids_approvals(w):
    o = to_estimating(order(w))
    est = estimate(w, o, 3000)
    est._guarded().write({"customer_approval_ref": "OTP x", "customer_approved_total": 1.0})
    other = w.env["res.partner"].create({"name": "Right Customer", "phone": "01711000999"})
    # a clerk cannot
    assert "Supervisor" in attempt(
        w,
        lambda: o.with_user(w.clerk).action_correct_customer_device(
            customer_id=other.id, reason="wrong file"
        ),
    )
    boss = supervisor(w)
    assert "reason" in attempt(
        w, lambda: o.with_user(boss).action_correct_customer_device(customer_id=other.id)
    )
    o.with_user(boss).action_correct_customer_device(customer_id=other.id, reason="wrong file")
    assert o.customer_id == other
    assert not est.customer_approval_ref and not est.customer_approved_total
    # once the customer has the estimate, it is a new order
    est.action_send()
    third = w.env["res.partner"].create({"name": "Third", "phone": "01711000666"})
    assert "before the estimate goes" in attempt(
        w,
        lambda: o.with_user(boss).action_correct_customer_device(
            customer_id=third.id, reason="again"
        ),
    )


# ======================================================== M01-07: the LCI finding
def test_m01_07_lci_finding_is_corrected_by_a_supervisor_with_a_photo(w):
    o = order(w, state="intake")
    assert "Correct LCI Finding" in attempt(
        w, lambda: o.with_user(w.clerk).write({"lci_tripped": True})
    )
    boss = supervisor(w)
    assert "photo" in attempt(
        w, lambda: o.with_user(boss).action_correct_lci(tripped="yes", reason="red under tray")
    )
    _image(w, o, "lci.png")
    assert "Supervisor" in attempt(
        w, lambda: o.with_user(w.clerk).action_correct_lci(tripped="yes", reason="red")
    )
    o.with_user(boss).action_correct_lci(tripped="yes", reason="red under the SIM tray")
    assert o.lci_tripped


# ===================================================== M01-15: branch transfer
def test_m01_15_branch_moves_only_by_transfer_and_the_ou_follows(w):
    o = order(w, state="intake")
    ou2 = w.env["operating.unit"].create(
        {
            "name": "A02R2 OU2",
            "code": "A2R2O2",
            "company_id": o.company_id.id,
            "partner_id": o.company_id.partner_id.id,
        }
    )
    branch2 = w.env["fix.branch"].create(
        {
            "name": "A02R2 Branch 2",
            "code": "A2R2-BR2",
            "entity_id": w.branch.entity_id.id,
            "operating_unit_id": ou2.id,
        }
    )
    assert "Transfer Branch" in attempt(
        w, lambda: o.with_user(w.clerk).write({"branch_id": branch2.id})
    )
    boss = supervisor(w)
    o.with_user(boss).action_transfer_branch(branch_id=branch2.id, reason="customer moved")
    assert o.branch_id == branch2 and o.operating_unit_id == ou2


# ======================================================== M01-03 (D6): cancel
def test_m01_03_only_a_supervisor_cancels_a_repaired_order(w):
    o = to_ready(w, order(w), 3000)
    assert "only a Service Supervisor" in attempt(
        w, lambda: o.with_user(w.clerk).action_cancel(reason_code="duplicate")
    )
    o.with_user(supervisor(w)).action_cancel(reason_code="duplicate")
    assert o.state == "cancelled"


def test_m01_03_a_refused_repair_owes_the_approved_estimate(w):
    o = to_ready(w, order(w), 3000)
    boss = supervisor(w)
    msg = attempt(w, lambda: o.with_user(boss).action_cancel(reason_code="customer_declined"))
    assert msg and "owes the approved estimate" in msg
    assert o.state == "ready"


# ===================================================== M01-05: the close cron
def test_m01_05_cron_closes_a_paid_delivered_order_once(w):
    o = _deliver(w, order(w))
    unpaid = to_ready(w, order(w), 3000)
    Order = w.env["fix.service.order"]
    Order._cron_close_delivered()
    assert o.state == "closed" and o.closed_at
    assert unpaid.state == "ready"
    Order._cron_close_delivered()
    assert len(_events(w, "service_order.closed", o.id)) == 1


def test_m01_05_cron_leaves_an_order_the_gate_refuses(w):
    # Since the A02 ERP audit a delivery raises the tax invoice and pays it
    # from the receipt, and the delivery gate refuses an unpaid order, so a
    # delivered order the close gate refuses cannot be built through the
    # flow. The cron must still respect the gate: it is made to refuse.
    from unittest import mock

    o = _deliver(w, order(w))
    Order = type(o)
    with mock.patch.object(Order, "_fix_close_problem", return_value="money not proven"):
        w.env["fix.service.order"]._cron_close_delivered()
    assert o.state == "delivered"
    w.env["fix.service.order"]._cron_close_delivered()  # the gate passes: it closes
    assert o.state == "closed"


# ================================================= M01-06: before/after photos
def test_m01_06_warranty_order_closes_only_with_both_photos_on_the_order(w):
    o = order(w, dev=device(w, warranty="active"), order_category="warranty")
    _force_state(o, "delivered")  # only the close gate is under test
    msg = o.with_user(w.clerk)._fix_close_problem()
    assert "intake photo" in msg and "after-repair photo" in msg
    stray = _image(w, None, "elsewhere.png")
    stray.sudo().write({"res_model": "res.partner", "res_id": w.customer.id})
    o.sudo().write({"intake_photo_attachment_id": stray.id})
    assert "intake photo" in o.with_user(w.clerk)._fix_close_problem()
    o.sudo().write(
        {
            "intake_photo_attachment_id": _image(w, o, "in.png").id,
            "after_repair_photo_attachment_id": _image(w, o, "out.png").id,
        }
    )
    assert "photo" not in (o.with_user(w.clerk)._fix_close_problem() or "")


def test_m01_06_walk_in_photo_is_copied_onto_the_order(w):
    Intake = w.env.get("fix.walkin.intake")
    if Intake is None:
        pytest.skip("cd_front_desk not installed")
    o = order(w, state="intake")
    photo = _image(w, None, "walkin.png")
    intake = Intake.sudo().search([], limit=1)
    if not intake:
        pytest.skip("no walk-in intake to borrow")
    w.env.cr.execute(
        "UPDATE fix_walkin_intake SET service_order_id=%s, intake_photo_attachment_id=%s "
        "WHERE id=%s",
        (o.id, photo.id, intake.id),
    )
    intake.invalidate_recordset()
    o._fix_adopt_intake_photo()
    assert o._fix_own_attachment(o.intake_photo_attachment_id, image=True)


# ============================================== M01-08 (D12): estimate validity
def test_m01_08_estimate_is_valid_15_days_from_sending_and_locked(w):
    o = to_estimating(order(w))
    est = estimate(w, o, 3000)
    est.action_send()
    from odoo.addons.cd_service_order.models.fix_estimate import _dhaka_today

    assert est.expiry_date == _dhaka_today() + timedelta(days=15)
    later = est.expiry_date + timedelta(days=30)
    assert "validity is fixed" in attempt(
        w, lambda: est.with_user(w.clerk).write({"expiry_date": later})
    )


# =========================================== M01-09: QC completes in QC Pending
def test_m01_09_qc_checklist_completes_only_in_qc_pending(w):
    o = order(w)
    approved(w, o)
    o.action_start_repair()
    qc = (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create({"order_id": o.id, "item_ids": [Command.create({"name": "power", "passed": True})]})
    )
    assert "QC Pending" in attempt(w, lambda: qc.with_user(w.inspector).action_complete())
    o.action_submit_qc()
    qc.with_user(w.inspector).action_complete()
    assert qc.state == "passed" and qc.qc_round == o.qc_round == 1


def test_m01_09_a_round_zero_inspection_does_not_open_ready(w):
    o = order(w)
    approved(w, o)
    o.action_start_repair()
    qc = w.env["fix.qc.checklist"].create(
        {"order_id": o.id, "item_ids": [Command.create({"name": "power", "passed": True})]}
    )
    qc._guarded().write({"state": "passed", "qc_round": 0})  # completed before QC
    o.action_submit_qc()
    assert "no QC checklist" in attempt(w, lambda: o.with_user(w.clerk).action_ready())


# ================================================= M01-10: rework across branches
def test_m01_10_rework_found_at_another_branch_and_published(w):
    code = w.env["fix.fault.code"].sudo().search([("category", "!=", False)], limit=1)
    if not code:
        pytest.skip("no fault code")
    dev = device(w)
    first = order(w, dev=dev)
    w.env["fix.service.order.fault"].create(
        {"order_id": first.id, "fault_code": code.code, "description": "first"}
    )
    _force_state(first, "delivered")
    first.sudo()._guarded().write({"delivered_at": fields.Datetime.now() - timedelta(days=3)})
    ou2 = w.env["operating.unit"].create(
        {
            "name": "A02R2 OU3",
            "code": "A2R2O3",
            "company_id": first.company_id.id,
            "partner_id": first.company_id.partner_id.id,
        }
    )
    first.sudo().write({"operating_unit_id": ou2.id})  # delivered at another branch
    clerk = _user(w.env, "ou_clerk")
    if "operating_unit_ids" in clerk._fields:
        clerk.write({"operating_unit_ids": [Command.set([w.branch.operating_unit_id.id])]})
    assert not w.env["fix.service.order"].with_user(clerk).search([("id", "=", first.id)])
    second = order(w, user=clerk, dev=dev)
    w.env["fix.service.order.fault"].create(
        {"order_id": second.id, "fault_code": code.code, "description": "again"}
    )
    second.with_user(clerk)._flag_rework()
    assert second.is_rework and second.rework_of_id == first
    ev = _events(w, "rework.detected", second.id)
    assert ev and _payload(ev)["original_order_id"] == first.id


# =================================== M01-12: warranty days and the signed report
def test_m01_12_warranty_days_come_from_the_policy(w):
    w.env["ir.config_parameter"].sudo().set_param("cd_service_order.repair_warranty_days", "120")
    o = order(w)
    assert o.service_warranty_days == 120
    assert "workflow" in attempt(
        w, lambda: o.with_user(w.clerk).write({"service_warranty_days": 365})
    )


def test_m01_12_signed_report_must_be_on_the_order(w):
    o = to_ready(w, order(w), 3000)
    o.with_user(w.cashier).action_mark_settled("POS-R", o._fix_amount_due(), tender="cash")
    handover_evidence(w, o)
    other = order(w)
    foreign = w.env["ir.attachment"].create(
        {
            "name": "other.pdf",
            "datas": base64.b64encode(b"%PDF other"),
            "res_model": other._name,
            "res_id": other.id,
        }
    )
    o.with_user(w.clerk).write({"service_report_attachment_id": foreign.id})
    assert "uploaded on this order" in attempt(w, lambda: o.with_user(w.clerk).action_deliver())


# ================================================ M01-13 (D13): uncollected
def test_m01_13_reminders_notice_and_disposal(w):
    o = to_ready(w, order(w), 3000)
    Order = w.env["fix.service.order"]
    o._guarded().write({"ready_at": fields.Datetime.now() - timedelta(days=8)})
    assert Order._cron_uncollected_reminders() >= 1
    assert o.uncollected_reminder_stage == 7 and not o.uncollected_notice_at
    Order._cron_uncollected_reminders()
    assert o.uncollected_reminder_stage == 7  # once per stage
    o._guarded().write({"ready_at": fields.Datetime.now() - timedelta(days=31)})
    Order._cron_uncollected_reminders()
    assert o.uncollected_reminder_stage == 30 and o.uncollected_notice_at
    # disposal only once abandoned (90 days) and with a branch manager
    boss = supervisor(w)
    assert "not abandoned" in attempt(
        w, lambda: o.with_user(w.bm).action_cancel(reason_code="abandoned")
    )
    o._guarded().write({"ready_at": fields.Datetime.now() - timedelta(days=91)})
    assert Order._cron_flag_abandoned() >= 1 and o.is_abandoned
    assert "branch manager" in attempt(
        w, lambda: o.with_user(boss).action_cancel(reason_code="abandoned")
    )
    o.with_user(w.bm).action_cancel(reason_code="abandoned")
    assert o.state == "cancelled"


def test_m01_13_one_policy(w):
    policy = w.env["fix.service.order"]._fix_uncollected_policy()
    assert policy == {"reminders": [3, 7, 15, 30], "notice": 30, "dispose_after": 90}


# ============================================== D1: cash on delivery / the leg
def _cod_clearing(w):
    """D1: a COD collection books an M20 receipt Dr COD clearing / Cr AR (the
    finance bridge). The clearing account is the test's, as in the finance
    fixtures: no chart is configured in the test database."""
    if "fix.ar.receipt" not in w.env:
        return
    account = w.env["account.account"].create(
        {"code": "R2M01COD", "name": "R2 M01 COD clearing", "account_type": "asset_current"}
    )
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_billing_engine.account_code.cod_clearing", account.code
    )


def test_d1_delivery_leg_needs_payment_or_goes_cod(w):
    _cod_clearing(w)
    o = to_ready(w, order(w), 3000)
    ok, why = o._fix_delivery_leg_allowed()
    assert not ok and "cash-on-delivery" in why
    rider = _user(w.env, "rider")
    due = o._fix_amount_due()
    o.with_user(rider)._fix_record_settlement(due, "COD-1", source="cod")
    assert (o.settlement_source, o.settlement_verified) == ("cod", False)
    # the leg is not "paid" yet, but the doorstep handover is (cash in hand)
    assert not o._fix_delivery_leg_allowed()[0]
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered"
    # never closes on unremitted cash
    assert "cannot be closed" in attempt(w, lambda: o.with_user(w.clerk).action_close())
    assert "Cashier" in attempt(w, lambda: o.with_user(rider).action_confirm_cod_remitted())
    o.with_user(w.cashier).action_confirm_cod_remitted()
    assert o.settlement_verified and o.amount_verified_bdt == due
    o.with_user(w.clerk).action_close()
    assert o.state == "closed"


def test_d1_a_paid_order_may_travel(w):
    o = to_ready(w, order(w), 3000)
    o.with_user(w.cashier).action_mark_settled("POS-L", o._fix_amount_due(), tender="cash")
    assert o._fix_delivery_leg_allowed() == (True, "")


# ============================================= D3: part payment on site
def test_d3_part_payment_is_recorded_not_refused(w):
    o = to_ready(w, order(w), 3000)
    due = o._fix_amount_due()
    tech = _user(w.env, "fieldtech_d3")
    o.with_user(tech)._fix_record_settlement(1000, "BKASH-P1", source="field_collection")
    assert o.payment_settlement_state == "partial" and o.amount_settled_bdt == 1000
    assert not o.settlement_verified
    assert o._fix_amount_outstanding() == pytest.approx(due - 1000)
    assert o._fix_amount_due() == pytest.approx(due)  # gross, before payments
    # the rest is still due: no release
    handover_evidence(w, o)
    assert attempt(w, lambda: o.with_user(w.clerk).action_deliver())
    # a second part is recorded too, and counts against what is outstanding
    o.with_user(tech)._fix_record_settlement(500, "BKASH-P2", "field_collection")
    assert o.amount_settled_bdt == 1500 and o._fix_amount_outstanding() == pytest.approx(due - 1500)
    # Verify Settlement works on a part payment and verifies the part paid
    o.with_user(w.cashier).action_verify_settlement()
    assert o.payment_settlement_state == "partial" and o.amount_verified_bdt == 1500
    # more than what is still to collect is refused
    assert "balance" in attempt(
        w,
        lambda: o.with_user(w.cashier2).action_mark_settled(
            reference="POS-OVER", amount_bdt=due, source="counter", tender="cash"
        ),
    )
    o.with_user(w.cashier2).action_mark_settled(
        reference="POS-BAL", amount_bdt=due - 1500, tender="cash"
    )
    assert o.payment_settlement_state == "settled" and o.settlement_verified
    assert o.amount_settled_bdt == pytest.approx(due) and o._fix_amount_outstanding() == 0.0
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered"


def test_d1_cod_is_exactly_what_is_outstanding(w):
    _cod_clearing(w)
    o = to_ready(w, order(w), 3000)
    tech = _user(w.env, "fieldtech_cod")
    o.with_user(tech)._fix_record_settlement(1000, "BKASH-C1", "field_collection")
    rest = o._fix_amount_outstanding()
    rider = _user(w.env, "rider_cod")
    assert "still to collect" in attempt(
        w, lambda: o.with_user(rider)._fix_record_settlement(rest + 100, "COD-X", "cod")
    )
    assert "still to collect" in attempt(
        w, lambda: o.with_user(rider)._fix_record_settlement(rest - 100, "COD-X", "cod")
    )
    o.with_user(rider)._fix_record_settlement(rest, "COD-2", "cod")
    assert o.payment_settlement_state == "settled" and o.settlement_source == "cod"
    assert not o.settlement_verified and o._fix_amount_outstanding() == 0.0


def test_d3_cancel_voids_only_the_unverified_part(w):
    o = to_ready(w, order(w), 3000)
    tech = _user(w.env, "fieldtech_d3b")
    o.with_user(tech)._fix_record_settlement(1000, "BKASH-Q1", "field_collection")
    o.with_user(w.cashier).action_verify_settlement()
    o.with_user(tech)._fix_record_settlement(500, "BKASH-Q2", "field_collection")
    assert o.amount_settled_bdt == 1500 and not o.settlement_verified
    o.with_user(supervisor(w)).action_cancel(reason_code="duplicate")
    assert o.state == "cancelled" and o.payment_settlement_state == "refund_due"
    ev = _events(w, "service_order.refund_requested", o.id)
    assert ev and _payload(ev)["amount_bdt"] == 1000


# ============================================== D4: on-site completion
def _field_order(w, o):
    Field = w.env.get("fix.field.order")
    if Field is None:
        pytest.skip("cd_field_service not installed")
    zone = w.branch.zone_id if "zone_id" in w.branch._fields else None
    if "zone_id" in w.branch._fields and not zone:
        zone = w.env["fix.zone"].create({"name": "A02R2 zone", "code": "A2R2Z"})
        w.branch.zone_id = zone
    vals = {"order_id": o.id}
    if zone and "zone_id" in Field._fields:
        vals["zone_id"] = zone.id
    return Field.sudo().create(vals)


def test_d4_on_site_completion_delivers_the_order(w):
    o = order(w, service_type="onsite")
    approved(w, o)
    o.action_start_repair()
    fo = _field_order(w, o)
    assert "not completed" in attempt(w, lambda: o.sudo().action_complete_onsite(fo))
    fo.sudo().write({"state": "completed"})
    assert "sign-off" in attempt(w, lambda: o.sudo().action_complete_onsite(fo))
    sig = _image(w, None, "sig.png")
    pic = _image(w, None, "after.png")
    fo.sudo().write(
        {"customer_signature_attachment_id": sig.id, "post_work_photo_attachment_id": pic.id}
    )
    assert "field order's hand-back" in attempt(
        w, lambda: o.with_user(w.clerk).action_complete_onsite(fo)
    )
    o.sudo().action_complete_onsite(fo)
    assert o.state == "delivered" and o.onsite_field_order_ref == fo.name
    assert o.service_warranty_until and o.after_repair_photo_attachment_id
    o.sudo().action_complete_onsite(fo)  # idempotent


def test_d4_a_walk_in_order_is_not_delivered_on_site(w):
    o = order(w)
    approved(w, o)
    fo = _field_order(w, o)
    fo.sudo().write({"state": "completed"})
    assert "on-site job" in attempt(w, lambda: o.sudo().action_complete_onsite(fo))


# ============================================== X5-16: M15 part reservation
def test_x5_16_estimate_approval_reserves_its_m15_parts(w):
    """The approved part is asked of M15 for the order; a store that cannot
    hold it is reported on the order, never silently skipped."""
    env = w.env
    product = env["product.product"].create({"name": "A02R2 Panel", "default_code": "A2R2-PNL"})
    part = env["fix.spare.part"].create(
        {"name": "A02R2 Panel", "part_number": "A2R2-PNL", "product_id": product.id}
    )
    env["fix.stock.location"].create(
        {
            "name": "A02R2 Branch Store",
            "code": "A2R2-BST",
            "location_type": "branch",
            "branch_id": w.branch.id,
            "operating_unit_id": w.branch.operating_unit_id.id,
        }
    )
    o = to_estimating(order(w))
    est = env["fix.estimate"].create(  # a trusted load: the catalogue is not under test
        {
            "order_id": o.id,
            "line_ids": [
                Command.create(
                    {
                        "line_type": "part",
                        "product_id": product.id,
                        "description": "panel",
                        "quantity": 1,
                        "unit_price": 1000.0,
                    }
                )
            ],
        }
    )
    est.with_user(w.clerk).action_send()
    est.with_user(w.clerk2).action_approve()
    held = (
        env["fix.stock.reservation"]
        .sudo()
        .search([("service_order_ref", "=", o.name), ("part_id", "=", part.id)])
    )
    body = " ".join(o.message_ids.mapped("body"))
    # held when the store has it, reported when it does not: never silent
    assert held.filtered(lambda r: r.state == "active") or (
        "NOT held" in body and part.part_number in body
    )
