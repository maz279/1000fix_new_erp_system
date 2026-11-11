"""A04 audit C2-C13 (M38): the storefront order and refund lifecycles.

Behaviour tests, run as non-admin users created in the transaction: a plain
internal clerk, a storefront operator, a payment officer and refund approvers
holding DOFA tiers. They replace the October source-text tests
(test_storefront.py) for what the audit found open:
  - M38-1/6: order and return states forged by a write (ORM and /p03);
  - M38-2: payment confirmed on a typed TrxID, one TrxID paying two orders;
  - M38-4/5: refunds uncapped, unpinned, self-approved, with no tier;
  - M38-7/17: a self-minted "Mushak 6.7" reference;
  - M38-8/9/10/11/12/14/15: stock, slots, window, inspection, POD, total,
    the frozen SLA and the paid cancellation.
"""

import types
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_storefront.controllers import storefront_api
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GUARD = "changes only through its workflow"


def _mk(env, login, *xmlids, portal_partner=None):
    base = "base.group_portal" if portal_partner else "base.group_user"
    vals = {
        "name": login,
        "login": login,
        "group_ids": [(6, 0, [env.ref(base).id] + [env.ref(x).id for x in xmlids])],
    }
    if portal_partner:
        vals["partner_id"] = portal_partner.id
    return env["res.users"].with_context(no_reset_password=True).create(vals)


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    sf = "cd_storefront.group_fix_storefront_"
    tiers = ["cd_entity_config.group_dofa_tier_%d" % n for n in (1, 2, 3, 4)]
    x = types.SimpleNamespace(env=env)
    x.clerk = _mk(env, "a4sf_clerk")
    x.operator = _mk(env, "a4sf_operator", sf + "operator")
    x.operator2 = _mk(env, "a4sf_operator2", sf + "operator")
    x.cashier = _mk(env, "a4sf_cashier", sf + "payment_officer")
    x.approver = _mk(env, "a4sf_approver", sf + "refund_approver", *tiers)
    x.approver_t1 = _mk(env, "a4sf_approver_t1", sf + "refund_approver", tiers[0])
    x.tier_only = _mk(env, "a4sf_tier_only", *tiers)
    x.customer = env["res.partner"].create(
        {"name": "A4 SF Customer", "street": "House 1", "city": "Dhaka"}
    )
    x.other = env["res.partner"].create({"name": "A4 SF Other", "city": "Dhaka"})
    x.portal = _mk(env, "a4sf_portal", portal_partner=x.customer)
    x.product = env["product.template"].create(
        {"name": "A4 SF Charger", "list_price": 2500.0, "sale_ok": True}
    )
    x.ou = env["operating.unit"].search([], limit=1)
    return x


def _placed(w, user=None, qty=1, method="standard_delivery", rail="bkash", **kw):
    u = user or w.clerk
    cart = w.env["fix.storefront.cart"].with_user(u).create({"customer_id": w.customer.id})
    w.env["fix.storefront.cart.line"].with_user(u).create(
        {"cart_id": cart.id, "product_id": w.product.id, "quantity": qty}
    )
    return cart.action_place_order(shipping_method=method, payment_rail=rail, **kw)


def _receipt(w, ref, amount, customer=None, state="confirmed"):
    return w.env["fix.ar.receipt"].create(
        {
            "customer_id": (customer or w.customer).id,
            "amount": amount,
            "method": "bkash",
            "reference": ref,
            "state": state,
        }
    )


def _paid(w, order, ref=None):
    ref = ref or "TRX-%s" % order.id
    _receipt(w, ref, order.sudo().total_amount)
    order.with_user(w.cashier).action_confirm_payment(payment_ref=ref)
    return order


def _consignment(w, state="delivered"):
    rec = w.env["fix.consignment"].create(
        {
            "operating_unit_id": w.ou.id,
            "consignment_type": "delivery",
            "scheduled_date": fields.Datetime.now(),
        }
    )
    if state != "draft":
        rec.write({"state": state})  # setup by the superuser (M03 POD is its own suite)
    return rec


def _delivered(w, order=None):
    order = order or _paid(w, _placed(w))
    cons = _consignment(w)
    order.with_user(w.operator).action_dispatch(carrier_consignment_id=cons.id)
    order.with_user(w.operator).action_deliver()
    return order


def _return(w, order, amount=None, user=None, reason="defective", model="fix.storefront.return"):
    vals = {
        "order_id": order.id,
        "customer_id": order.customer_id.id,
        "reason": reason,
        "refund_amount": order.sudo().total_amount if amount is None else amount,
    }
    if model == "fix.storefront.rma":
        vals["reason"] = {"changed_mind": "change_of_mind"}.get(reason, "warranty")
    return w.env[model].with_user(user or w.operator).create(vals)


def _credit_note(w, amount, partner=None):
    # A08 M51-9: a posted credit note reaches the Mushak register, which needs the
    # supplier BIN (a real company has one; the test company may not)
    company = w.env.company.sudo()
    if not company.vat or len(set(company.vat)) < 2:
        company.vat = "1234567890128"
    move = w.env["account.move"].create(
        {
            "move_type": "out_refund",
            "partner_id": (partner or w.customer).id,
            "currency_id": w.env.ref("base.BDT").id,
            "invoice_line_ids": [
                (0, 0, {"name": "Storefront refund", "quantity": 1, "price_unit": amount})
            ],
        }
    )
    move.action_post()
    return move


def _events(w, etype, rec):
    return (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", etype), ("aggregate_id", "=", rec.id)])
    )


# ============================================================ order: guard
def test_a_clerk_cannot_write_an_order_paid_or_delivered(w):
    order = _placed(w)
    for vals in ({"state": "paid"}, {"state": "delivered"}, {"total_amount": 1.0}):
        with pytest.raises(REFUSED), w.env.cr.savepoint():
            order.with_user(w.clerk).write(vals)
    # an operator holds order write, and the guard still refuses the forgery
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        order.with_user(w.operator).write({"state": "delivered", "payment_ref": "x"})
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        order.with_user(w.operator).write({"total_amount": 1.0})
    order.invalidate_recordset()
    assert (order.state, order.total_amount) == ("pending_payment", 2500.0)


def test_placement_is_a_service_and_lines_are_frozen(w):
    order = _placed(w)
    assert order.sudo().placed_by_id == w.clerk
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        order.sudo().line_ids.with_user(w.operator).write({"unit_price": 1.0})
    with pytest.raises(ValidationError, match="sum of its lines"), w.env.cr.savepoint():
        order.sudo().write({"total_amount": 1.0})
    # the clerk cannot create an order directly either
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        w.env["fix.storefront.order"].with_user(w.clerk).create(
            {"customer_id": w.customer.id, "total_amount": 1.0, "shipping_address": "x"}
        )


def test_a_cart_is_ordered_once(w):
    cart = w.env["fix.storefront.cart"].create({"customer_id": w.customer.id})
    w.env["fix.storefront.cart.line"].create(
        {"cart_id": cart.id, "product_id": w.product.id, "quantity": 1}
    )
    cart.action_place_order(shipping_address="Road 1")
    with pytest.raises(UserError, match="already been ordered"), w.env.cr.savepoint():
        cart.action_place_order(shipping_address="Road 1")
    with pytest.raises(UserError, match=GUARD), w.env.cr.savepoint():
        cart.with_user(w.clerk).write({"state": "open"})


# ============================================================ order: payment
def test_payment_needs_the_role_and_an_m20_receipt(w):
    order = _placed(w)
    with pytest.raises(UserError, match="Payment Officer"), w.env.cr.savepoint():
        order.with_user(w.clerk).action_confirm_payment(payment_ref="made-up-123")
    with pytest.raises(UserError, match="No confirmed M20 receipt"), w.env.cr.savepoint():
        order.with_user(w.cashier).action_confirm_payment(payment_ref="made-up-123")
    # a draft receipt, another customer's receipt, or one short of the total: no
    _receipt(w, "R-DRAFT", 2500.0, state="draft")
    _receipt(w, "R-OTHER", 2500.0, customer=w.other)
    _receipt(w, "R-SHORT", 100.0)
    for ref in ("R-DRAFT", "R-OTHER", "R-SHORT"):
        with pytest.raises(UserError, match="No confirmed M20 receipt"), w.env.cr.savepoint():
            order.with_user(w.cashier).action_confirm_payment(payment_ref=ref)
    receipt = _receipt(w, "BKX-OK-1", 2500.0)
    order.with_user(w.cashier).action_confirm_payment(payment_ref="BKX-OK-1")
    order.invalidate_recordset()
    assert (order.state, order.payment_source, order.payment_receipt_id) == (
        "paid",
        "m20_receipt",
        receipt,
    )
    assert order.payment_confirmed_by_id == w.cashier
    assert len(_events(w, "storefront.payment_confirmed", order)) == 1


def test_one_reference_and_one_receipt_pay_one_order(w):
    first, second = _placed(w), _placed(w)
    _paid(w, first, ref="BKX-DUP")
    with pytest.raises(UserError), w.env.cr.savepoint():
        second.with_user(w.cashier).action_confirm_payment(payment_ref="BKX-DUP")
    # not even trusted server code reuses a gateway transaction
    with pytest.raises(UserError, match="already paid order"), w.env.cr.savepoint():
        second.sudo().action_confirm_payment(payment_ref="BKX-DUP")
    assert second.sudo().state == "pending_payment"


def _sign(secret, order, trx, amount):
    return storefront_api.gateway_signature(secret, order.sudo().name, trx, amount)


def test_the_gateway_callback_confirms_only_a_signed_exact_notice(w):
    env = w.env
    order = _placed(w)
    name = order.sudo().name
    handle = storefront_api.handle_gateway_callback
    payload = {"order": name, "trx_id": "GW-1", "amount": "2500.00"}
    # no secret configured: refused, the order stays unpaid
    assert handle(env, "bkash", dict(payload, signature="x"))[1] == 503
    env["ir.config_parameter"].sudo().set_param("cd_storefront.gateway_secret.bkash", "s3cr3t")
    assert handle(env, "bkash", dict(payload, signature="forged"))[1] == 403
    assert handle(env, "paypal", dict(payload, signature="x"))[1] == 404
    low = {"order": name, "trx_id": "GW-1", "amount": "1.00"}
    body, status = handle(env, "bkash", dict(low, signature=_sign("s3cr3t", order, "GW-1", "1.00")))
    assert status == 409 and "total" in body["message"]
    assert order.sudo().state == "pending_payment"
    good = dict(payload, signature=_sign("s3cr3t", order, "GW-1", "2500.00"))
    body, status = handle(env, "bkash", good)
    assert (status, body["status"]) == (200, "paid")
    assert order.sudo().payment_source == "gateway"
    assert handle(env, "bkash", good)[1] == 200  # the gateway re-sends: idempotent
    again = {"order": name, "trx_id": "GW-2", "amount": "2500.00"}
    body, status = handle(
        env, "bkash", dict(again, signature=_sign("s3cr3t", order, "GW-2", "2500.00"))
    )
    assert status == 409 and "second capture" in body["message"]
    # the rail must be the order's own
    env["ir.config_parameter"].sudo().set_param("cd_storefront.gateway_secret.nagad", "n4g4d")
    other = _placed(w)
    nag = {"order": other.sudo().name, "trx_id": "NG-1", "amount": "2500.00"}
    body, status = handle(
        env, "nagad", dict(nag, signature=_sign("n4g4d", other, "NG-1", "2500.00"))
    )
    assert status == 409 and other.sudo().state == "pending_payment"


# ============================================================ order: fulfilment
def test_dispatch_needs_the_role_payment_and_a_consignment(w):
    order = _placed(w)
    with pytest.raises(UserError, match="Operator"), w.env.cr.savepoint():
        order.with_user(w.clerk).action_dispatch()
    with pytest.raises(UserError, match="paid before dispatch"), w.env.cr.savepoint():
        order.with_user(w.operator).action_dispatch()
    _paid(w, order)
    with pytest.raises(UserError, match="consignment"), w.env.cr.savepoint():
        order.with_user(w.operator).action_dispatch()
    lost = _consignment(w, state="lost")
    with pytest.raises(UserError, match="lost"), w.env.cr.savepoint():
        order.with_user(w.operator).action_dispatch(carrier_consignment_id=lost.id)
    cons = _consignment(w, state="in_transit")
    order.with_user(w.operator).action_dispatch(carrier_consignment_id=cons.name)
    assert (order.sudo().state, order.sudo().carrier_consignment_id) == ("dispatched", cons)
    # delivered only once the consignment's POD is in
    with pytest.raises(UserError, match="proof of delivery"), w.env.cr.savepoint():
        order.with_user(w.operator).action_deliver()
    cons.write({"state": "delivered"})
    order.with_user(w.operator).action_deliver()
    assert order.sudo().state == "delivered" and order.sudo().delivered_by_id == w.operator


def test_a_branch_pickup_needs_no_consignment(w):
    order = _paid(w, _placed(w, method="branch_pickup"))
    order.with_user(w.operator).action_dispatch()
    order.with_user(w.operator).action_deliver()
    assert order.sudo().state == "delivered"


def test_the_sla_status_follows_the_clock(w):
    order = _placed(w)
    assert order.delivery_sla_status == "on_time"
    later = fields.Datetime.now() + timedelta(days=5)
    with mock.patch.object(fields.Datetime, "now", return_value=later):
        order.invalidate_recordset()
        assert order.delivery_sla_status == "breached"
        found = w.env["fix.storefront.order"].search(
            [("delivery_sla_status", "=", "breached"), ("id", "=", order.id)]
        )
        assert found == order


def test_cancelling_a_paid_order_sends_finance_the_refund(w):
    order = _paid(w, _placed(w))
    with pytest.raises(UserError, match="Operator"), w.env.cr.savepoint():
        order.with_user(w.clerk).action_cancel()
    order.with_user(w.operator).action_cancel(reason="customer called")
    assert (order.sudo().state, order.sudo().refund_due) == ("cancelled", 2500.0)
    [event] = _events(w, "storefront.order_cancelled", order)
    assert '"refund_due": 2500.0' in event.payload


# ============================================================ graded stock and slots
@pytest.fixture
def refurb(w):
    env = w.env
    model = env["fix.device.model"].search([], limit=1)
    if not model:
        brand = env["fix.brand"].create({"name": "A4SF Brand", "code": "A4SB"})
        model = env["fix.device.model"].create({"name": "A4SF Phone", "brand_id": brand.id})

    def make(serial, price=9000.0):
        dev = env["fix.device"].create(
            {"device_model_id": model.id, "owner_id": w.customer.id, "serial_number": serial}
        )
        return env["fix.graded.stock"].create(
            {
                "device_id": dev.id,
                "grade_id": env["fix.refurb.grade"].search([], limit=1).id,
                "acquisition_cost": 5000.0,
                "resale_price": price,
            }
        )

    return make


def _refurb_order(w, item, user=None, **kw):
    u = user or w.clerk
    cart = w.env["fix.storefront.cart"].with_user(u).create({"customer_id": w.customer.id})
    w.env["fix.storefront.cart.line"].with_user(u).create(
        {
            "cart_id": cart.id,
            "product_id": w.product.id,
            "graded_stock_id": item.id,
            "unit_price": 1,
        }
    )
    return cart.action_place_order(shipping_address="Road 7", **kw)


def test_graded_stock_is_reserved_sold_and_released_by_orders(w, refurb):
    item = refurb("A4SF-SN-1")
    order = _refurb_order(w, item)
    assert order.sudo().total_amount == 9000.0  # the item's own resale price
    assert item.state == "reserved"
    with pytest.raises(UserError, match="can no longer be sold"), w.env.cr.savepoint():
        _refurb_order(w, item)
    _delivered(w, _paid(w, order))
    assert item.state == "sold"
    events = w.env["fix.event.outbox"].search(
        [("event_type", "=", "graded_stock.sold"), ("aggregate_id", "=", item.id)]
    )
    assert len(events) == 1
    spare = refurb("A4SF-SN-2")
    cancelled = _refurb_order(w, spare)
    cancelled.with_user(w.operator).action_cancel()
    assert spare.state == "in_stock"


def test_a_slot_takes_no_more_than_its_capacity(w):
    slot = (
        w.env["fix.storefront.slot"]
        .with_user(w.operator)
        .create(
            {"name": "A4SF slot", "slot_date": fields.Date.context_today(w.env.user), "capacity": 2}
        )
    )
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        slot.with_user(w.operator).write({"booked": 50})
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.env["fix.storefront.slot"].with_user(w.clerk).create(
            {"name": "x", "slot_date": fields.Date.context_today(w.env.user)}
        )
    _placed(w, slot_id=slot.id)
    _placed(w, slot_id=slot.id)
    assert (slot.booked, slot.state) == (2, "full")
    with pytest.raises(UserError, match="full"), w.env.cr.savepoint():
        _placed(w, slot_id=slot.id)
    slot.with_user(w.operator).action_close()
    assert slot.state == "closed"


# ============================================================ returns
def test_a_return_needs_a_paid_order_inside_the_window(w):
    unpaid = _placed(w)
    with pytest.raises(ValidationError, match="has not been paid"), w.env.cr.savepoint():
        _return(w, unpaid)
    with pytest.raises(AccessError), w.env.cr.savepoint():
        _return(w, _delivered(w), user=w.clerk)
    old = _delivered(w)
    old.sudo()._guarded().write({"delivered_at": fields.Datetime.now() - timedelta(days=400)})
    with pytest.raises(ValidationError, match="return window"), w.env.cr.savepoint():
        _return(w, old, reason="changed_mind")
    # the daily job closes the window for good
    assert w.env["fix.storefront.order"].cron_close_return_windows() >= 1
    assert old.sudo().returns_closed


def test_the_refund_is_capped_at_what_was_paid(w):
    order = _delivered(w)
    with pytest.raises(ValidationError, match="exceeds what is refundable"), w.env.cr.savepoint():
        _return(w, order, amount=100000.0)
    first = _return(w, order, amount=2000.0)
    with pytest.raises(ValidationError, match="exceeds"), w.env.cr.savepoint():
        _return(w, order, amount=600.0, model="fix.storefront.rma")
    _return(w, order, amount=500.0, model="fix.storefront.rma")
    first.with_user(w.operator).action_approve()
    with pytest.raises(UserError, match="authorised"), w.env.cr.savepoint():
        first.with_user(w.operator).write({"refund_amount": 100000.0})


def test_one_clerk_cannot_run_a_refund_and_states_cannot_be_forged(w):
    order = _delivered(w)
    ret = _return(w, order)
    for user in (w.clerk, w.operator):
        with pytest.raises(REFUSED), w.env.cr.savepoint():
            ret.with_user(user).write({"state": "refunded"})
        with pytest.raises(REFUSED), w.env.cr.savepoint():
            ret.with_user(user).write({"credit_note_ref": "MUSHAK-6.7/FAKE"})
    with pytest.raises(UserError, match="Operator"), w.env.cr.savepoint():
        ret.with_user(w.clerk).action_approve()


def test_inspection_drives_the_refund(w):
    scrap = _return(w, _delivered(w), reason="changed_mind")
    scrap.with_user(w.operator).action_approve()
    scrap.with_user(w.operator).action_receive_and_inspect(condition="scrap")
    assert (scrap.state, scrap.refund_amount, scrap.disposition) == ("rejected", 0.0, "scrap")
    worn = _return(w, _delivered(w), reason="changed_mind")
    worn.with_user(w.operator).action_approve()
    worn.with_user(w.operator).action_receive_and_inspect(condition="grade_b")
    assert (worn.state, worn.refund_amount) == ("received", 2000.0)  # 20% restocking fee
    fault = _return(w, _delivered(w), reason="defective")
    fault.with_user(w.operator).action_approve()
    with pytest.raises(UserError, match="inspection result"), w.env.cr.savepoint():
        fault.with_user(w.operator).action_receive_and_inspect()
    fault.with_user(w.operator).action_receive_and_inspect(condition="scrap")
    assert (fault.state, fault.refund_amount) == ("received", 2500.0)


def _inspected(w, model="fix.storefront.return"):
    ret = _return(w, _delivered(w), model=model)
    ret.with_user(w.operator).action_approve()
    ret.with_user(w.operator2).action_receive_and_inspect(condition="grade_a")
    return ret


@pytest.mark.parametrize("model", ["fix.storefront.return", "fix.storefront.rma"])
def test_the_refund_is_a_routed_dofa_approval_then_an_m20_credit_note(w, model):
    ret = _inspected(w, model)
    # pressing Approve is refused: the refund is decided from the inbox
    with pytest.raises(UserError, match="inbox"), w.env.cr.savepoint():
        ret.with_user(w.approver).action_approve_refund()
    task = approve_via_inbox(
        ret, w.approver, requester=w.operator, justification="Defective on arrival"
    )
    assert task
    ret.invalidate_recordset()
    assert (ret.state, ret.dofa_approved_by, ret.dofa_approved_amount) == (
        "refund_approved",
        w.approver,
        2500.0,
    )
    assert w.operator not in ret.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    assert w.tier_only not in ret.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    [instruction] = _events(w, "storefront.refund_approved", ret)
    assert '"refund_amount": 2500.0' in instruction.payload
    # the amount is pinned
    with pytest.raises(UserError), w.env.cr.savepoint():
        ret.with_user(w.operator).write({"refund_amount": 100000.0})
    # finance completes it on the M20 credit note - never a typed reference
    with pytest.raises(UserError, match="Payment Officer"), w.env.cr.savepoint():
        ret.with_user(w.operator).action_record_credit_note(credit_note="anything")
    if "ar_credit_note_id" in ret._fields:
        # E3-08: with cd_storefront_finance installed the order is invoiced in
        # M20 and the refund is the M20 credit note against that invoice; a
        # native out_refund is refused (its suite covers the M20 path).
        native = _credit_note(w, 2500.0)
        with pytest.raises(UserError, match="not a storefront refund"), w.env.cr.savepoint():
            ret.with_user(w.cashier).action_record_credit_note(credit_note=native.name)
        assert ret.state == "refund_approved" and not ret.credit_note_id
        return
    with pytest.raises(UserError, match="No M20 credit note"), w.env.cr.savepoint():
        ret.with_user(w.cashier).action_record_credit_note(credit_note="anything")
    wrong = _credit_note(w, 100.0)
    with pytest.raises(UserError, match="approved refund"), w.env.cr.savepoint():
        ret.with_user(w.cashier).action_record_credit_note(credit_note=wrong.id)
    other = _credit_note(w, 2500.0, partner=w.other)
    with pytest.raises(UserError, match="not for"), w.env.cr.savepoint():
        ret.with_user(w.cashier).action_record_credit_note(credit_note=other.id)
    note = _credit_note(w, 2500.0)
    ret.with_user(w.cashier).action_record_credit_note(credit_note=note.name)
    assert (ret.state, ret.credit_note_id, ret.credit_note_ref) == ("refunded", note, note.name)
    assert len(_events(w, "storefront.refund_processed", ret)) == 1
    # a credit note pays one refund
    twin = _inspected(w, model)
    approve_via_inbox(twin, w.approver, requester=w.operator, justification="same")
    with pytest.raises(UserError, match="already pays"), w.env.cr.savepoint():
        twin.with_user(w.cashier).action_record_credit_note(credit_note=note.id)


def test_segregation_of_duties_and_tier(w):
    # the approver raised the return: the engine never routes it to them,
    # and a Tier-1 approver cannot clear a Tier-2 refund
    w.approver_t1.group_ids = [(4, w.env.ref("cd_storefront.group_fix_storefront_operator").id)]
    ret = _return(w, _delivered(w), user=w.approver_t1)
    ret.with_user(w.operator).action_approve()
    ret.with_user(w.operator).action_receive_and_inspect(condition="grade_a")
    ret.with_user(w.operator).action_request_approval(justification="customer refund")
    assigned = ret.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    assert w.approver_t1 not in assigned and w.approver in assigned
    task = ret.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == w.approver
    )
    with pytest.raises(UserError), w.env.cr.savepoint():
        task.with_user(w.approver_t1).action_approve()


def test_an_approval_does_not_survive_a_raised_amount(w):
    ret = _inspected(w)
    ret.sudo()._guarded().write({"refund_amount": 1000.0})
    # BDT 1,000 is Tier 1: it goes to the Tier-1 refund approver
    approve_via_inbox(ret, w.approver_t1, requester=w.operator, justification="partial")
    assert ret.dofa_approved_amount == 1000.0
    with pytest.raises(UserError), w.env.cr.savepoint():
        ret.with_user(w.cashier).write({"refund_amount": 2500.0})


def test_a_rejected_return_frees_the_refundable_amount(w):
    order = _delivered(w)
    ret = _return(w, order)
    ret.with_user(w.operator).action_reject(reason="duplicate request")
    assert ret.state == "rejected"
    _return(w, order)  # the full amount is refundable again


def test_an_rma_needs_an_order(w):
    with pytest.raises(ValidationError, match="order"), w.env.cr.savepoint():
        w.env["fix.storefront.rma"].with_user(w.operator).create(
            {"customer_id": w.customer.id, "refund_amount": 999999.0}
        )
    rma = _return(w, _delivered(w), model="fix.storefront.rma")
    assert rma.name.startswith("SRMA/")


def test_the_customer_api_respects_the_window(w):
    order = _delivered(w)
    order.sudo()._guarded().write({"delivered_at": fields.Datetime.now() - timedelta(days=30)})
    browser = types.SimpleNamespace(env=w.env(user=w.portal.id))
    with mock.patch.object(storefront_api, "request", browser):
        res = storefront_api.StorefrontApiController().create_return(order_id=order.id)
    assert res["error"]["code"] == "RETURN_NOT_ALLOWED"


# ============================================================ the workspace
@pytest.fixture
def p03(w):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()

    def raw(fn):
        return getattr(fn, "original_endpoint", fn)

    def call(user):
        old = getattr(g, "request", None)

        def run(fn, **kw):
            g.request = types.SimpleNamespace(env=w.env(user=user.id))
            try:
                return fn(ctl, **kw)
            finally:
                g.request = old

        return types.SimpleNamespace(
            write=lambda **kw: run(raw(g.P03GenericApiController.model_write), **kw),
            action=lambda **kw: run(raw(g.P03GenericApiController.model_action), **kw),
        )

    return call


def test_the_workspace_refuses_forged_states_and_runs_the_lifecycle(w, p03):
    order = _placed(w)
    op = p03(w.operator)
    res = op.write(
        model="fix.storefront.order",
        record_id=order.id,
        values={"state": "paid", "payment_ref": "typed-in-form", "total_amount": 1},
    )
    assert res.get("error") and order.sudo().state == "pending_payment"
    _receipt(w, "P03-RCPT", 2500.0)
    res = p03(w.cashier).action(
        model="fix.storefront.order",
        ids=[order.id],
        method="action_confirm_payment",
        kwargs={"payment_ref": "P03-RCPT"},
    )
    assert res["success"], res
    res = p03(w.clerk).action(
        model="fix.storefront.order", ids=[order.id], method="action_cancel", kwargs={}
    )
    assert not res["success"] and "Operator" in res["error"]
    ret = _return(w, _delivered(w))
    res = op.write(
        model="fix.storefront.return",
        record_id=ret.id,
        values={"state": "refunded", "refund_amount": 99999},
    )
    assert res.get("error") and ret.state == "requested"
    res = op.action(model="fix.storefront.return", ids=[ret.id], method="action_approve", kwargs={})
    assert res["success"], res
    res = op.action(
        model="fix.storefront.return", ids=[ret.id], method="action_approve_refund", kwargs={}
    )
    assert "not available" in res["error"]  # the refund is approved from the inbox


# ============================================================ crons
@pytest.mark.parametrize(
    ("xmlid", "method"),
    [
        ("cd_storefront.ir_cron_storefront_close_return_windows", "cron_close_return_windows"),
        ("cd_storefront.ir_cron_storefront_abandoned_carts", "cron_publish_abandoned_carts"),
    ],
)
def test_the_storefront_jobs_are_scheduled(w, xmlid, method):
    cron = w.env.ref(xmlid)
    assert cron.active and method in cron.code


def test_an_abandoned_cart_is_published_once(w):
    cart = w.env["fix.storefront.cart"].create({"customer_id": w.customer.id})
    w.env["fix.storefront.cart.line"].create(
        {"cart_id": cart.id, "product_id": w.product.id, "quantity": 1}
    )
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_storefront_cart SET write_date = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(hours=30), cart.id),
    )
    cart.invalidate_recordset()
    carts = w.env["fix.storefront.cart"]
    assert carts.cron_publish_abandoned_carts() >= 1
    carts.cron_publish_abandoned_carts()
    events = _events(w, "storefront.cart_abandoned", cart)
    assert len(events) == 1 and '"customer_id": %d' % w.customer.id in events.payload


# ============================================================ M37 / M11 sale check
def test_every_priced_line_runs_the_catalogue_and_floor_check(w):
    """B3 (M37/M11) exposes product._fix_check_sale; the storefront calls it on
    the storefront channel whenever a line is priced and again at checkout."""
    calls = []
    Product = type(w.env["product.product"])
    original = Product._fix_check_sale

    def spy(self, unit_price=None, channel=None):
        calls.append((self.product_tmpl_id, unit_price, channel))
        if self.product_tmpl_id.name == "A4SF Withdrawn":
            raise UserError("A4SF Withdrawn is restricted: not sold on the storefront")
        return original(self, unit_price=unit_price, channel=channel)

    withdrawn = w.env["product.template"].create(
        {"name": "A4SF Withdrawn", "list_price": 100.0, "sale_ok": True}
    )
    with mock.patch.object(Product, "_fix_check_sale", spy):
        order = _placed(w)
        assert (w.product, 2500.0, "storefront") in calls
        assert calls.count((w.product, 2500.0, "storefront")) >= 2  # line + checkout
        cart = (
            w.env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
        )
        with pytest.raises(UserError, match="restricted"), w.env.cr.savepoint():
            w.env["fix.storefront.cart.line"].with_user(w.clerk).create(
                {"cart_id": cart.id, "product_id": withdrawn.id, "quantity": 1}
            )
        browser = types.SimpleNamespace(env=w.env(user=w.portal.id), session={})
        with mock.patch.object(storefront_api, "request", browser):
            res = storefront_api.StorefrontApiController().get_or_update_cart(
                product_id=withdrawn.id
            )
        assert res["error"]["code"] == "PRODUCT_NOT_SELLABLE"
    assert order.sudo().state == "pending_payment"
