# ruff: noqa: F811  (the storefront fixtures are imported and used as parameters)
"""A04 ERP audit, round 2 (21 Nov 2026) - checkout and per-line returns in
the books.

M38-F14 the delivery fee is an invoice line of its own; the voucher is
        spread over the goods it priced (an M20 line takes no negative
        amount), so the invoice still equals what the customer pays to the
        paisa - journal lines shown
M38-F8  a line return restocks only its own units, at the cost they left
        with, and its credit note is split over the returned lines
M38-F20 the customer's own cancellation of a paid order runs the round-1
        refund path (M20 credit note against the issued invoice)
"""

import itertools
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_storefront.tests.test_a04_c2_c13_storefront import (  # noqa: F401
    _consignment,
    _mk,
    released_card,
    w,
)

from .test_storefront_books import _lines, _suspense, sf  # noqa: F401

pytestmark = [pytest.mark.financial]
_SEQ = itertools.count(1)


def _fee(w, price=100.0):
    n = next(_SEQ)
    fee = w.env["product.template"].create({"name": "R2 Courier fee %d" % n, "sale_ok": True})
    fee.product_variant_id.default_code = "R2B-DLV-%d" % n
    released_card(w.env, fee, price)
    w.params.set_param(
        "cd_storefront.delivery_fee_code.standard_delivery", fee.product_variant_id.default_code
    )
    return fee


def _voucher(w, value=10.0):
    w.params.set_param("cd_rate_card.margin_floor_pct", "0")
    today = fields.Date.context_today(w.env["res.partner"])
    promo = (
        w.env["fix.promotion"]
        .sudo()
        .create(
            {
                "name": "R2 books voucher",
                "code": "R2BV%d" % next(_SEQ),
                "value": value,
                "channel": "portal",
                "valid_from": today - timedelta(days=1),
                "valid_until": today + timedelta(days=5),
                "storefront_voucher": True,
            }
        )
    )
    promo._guarded().write({"state": "active"})
    return promo


def _order(w, qty=2, method="standard_delivery", voucher=None):
    env = w.env
    cart = env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
    env["fix.storefront.cart.line"].with_user(w.clerk).create(
        {"cart_id": cart.id, "product_id": w.product.id, "quantity": qty}
    )
    return cart.action_place_order(
        shipping_method=method, payment_rail="bkash", voucher_code=voucher
    )


def _pay(w, order):
    rcpt = w.receipt(order, "R2B-%s" % order.id)
    order.with_user(w.cashier).action_confirm_payment(payment_ref=rcpt.reference)
    order.invalidate_recordset()
    return order


def test_f14_invoice_carries_the_fee_and_the_voucher_to_the_paisa(sf):
    w = sf
    _fee(w, 100.0)
    promo = _voucher(w, 10.0)
    order = _pay(w, _order(w, qty=2, voucher=promo.code)).sudo()
    # goods 5,000.00 less voucher 500.00, plus fee 115.00
    assert order.total_amount == 4615.0
    inv = order.ar_invoice_id
    assert inv.total_payable == 4615.0
    assert sorted(inv.line_ids.mapped("taxable_amount")) == [100.0, 3913.04]
    assert _lines(inv.posted_move_id) == {
        w.acc.ar.code: (4615.0, 0.0),
        w.acc.revenue.code: (0.0, 4013.04),
        w.acc.vat.code: (0.0, 601.96),
    }
    # the fee and the voucher line are no stock: only the goods leave M15
    order.with_user(w.operator).action_dispatch(carrier_consignment_id=_consignment(w).id)
    order.invalidate_recordset()
    states = {ln.line_type: ln.stock_state for ln in order.line_ids}
    assert states == {"product": "issued", "delivery": "not_required", "discount": "not_required"}
    assert w.onhand() == 8.0


def _delivered(w, qty=3):
    order = _pay(w, _order(w, qty=qty, method="branch_pickup"))
    order.with_user(w.operator).action_dispatch()
    order.with_user(w.operator).action_deliver()
    order.invalidate_recordset()
    return order


def _line_return(w, order, qty, condition="grade_a"):
    line = order.sudo().line_ids.filtered(lambda ln: ln.line_type == "product")
    ret = (
        w.env["fix.storefront.return"]
        .with_user(w.operator)
        .create(
            {
                "order_id": order.id,
                "customer_id": order.customer_id.id,
                "reason": "defective",
                "line_ids": [Command.create({"order_line_id": line.id, "quantity": qty})],
            }
        )
    )
    ret.with_user(w.operator).action_approve()
    ret.with_user(w.operator2).action_receive_and_inspect(condition=condition)
    ret.invalidate_recordset()
    return ret


def test_f8_a_line_return_restocks_only_its_units(sf):
    w = sf
    order = _delivered(w, qty=3)
    assert w.onhand() == 7.0
    ret = _line_return(w, order, 1)
    s = ret.sudo()
    assert (s.restock_state, s.line_ids.restock_state) == ("restocked", "restocked")
    assert w.onhand() == 8.0  # one unit back, not three
    line = order.sudo().line_ids
    assert line.stock_state == "issued"  # two units are still sold
    rows = _suspense(w.env, order).filtered(lambda r: ret.name in (r.source_ref or ""))
    assert [(r.quantity, r.unit_cost) for r in rows] == [(1.0, 1500.0)]
    # the other two come back on a second return; then the line is returned
    _line_return(w, order, 2)
    assert w.onhand() == 10.0 and line.stock_state == "returned"


def test_f8_a_non_resalable_line_is_quarantined_by_its_units(sf):
    w = sf
    order = _delivered(w, qty=3)
    _line_return(w, order, 2, condition="grade_b")
    assert w.onhand() == 7.0 and w.onhand("quarantine") == 2.0


def test_f8_the_credit_note_is_split_over_the_returned_lines(sf):
    w = sf
    order = _delivered(w, qty=3)
    ret = _line_return(w, order, 2)
    w.refund_approved(ret)
    s = ret.sudo()
    note = s.ar_credit_note_id
    assert note and note.amount == 5000.0 and note.invoice_id == order.sudo().ar_invoice_id
    assert s.line_ids.credit_amount == 5000.0
    body = " ".join(note.message_ids.mapped("body"))
    assert "Lines returned" in body


def test_f20_customer_cancel_of_an_invoiced_order_is_credited(sf):
    w = sf
    order = _pay(w, _order(w, qty=1, method="branch_pickup"))
    assert order.sudo().ar_invoice_id.state in ("issued", "paid")
    order.with_user(w.portal).action_customer_cancel(reason="no longer needed")
    s = order.sudo()
    assert s.state == "cancelled" and s.cancelled_by_customer
    note = s.ar_credit_note_id
    assert note and note.amount == 2500.0 and note.state != "rejected"
    assert s.posting_state == "posted"
