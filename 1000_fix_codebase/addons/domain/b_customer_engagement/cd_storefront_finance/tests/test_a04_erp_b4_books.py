# ruff: noqa: F811  (the storefront fixtures are imported and used as parameters)
"""A04 ERP audit (20 Nov 2026), stream B4 - the storefront money paths.

M38-F1  the M11 VAT-exclusive price + M51 VAT is the customer's price, and
        the M20 invoice reproduces it to the paisa (journal lines shown)
M38-F2  a gateway-paid order cancelled while its invoice was still pending
        is refunded from its M20 receipt on the rail it came by; posting
        never reads "nothing to post" while a refund is owed
M38-F3  one refund per return: the relay hand-off no longer raises a second
        M50 instruction, and a second credit note is refused
M38-F10 dispatch is refused while the M20 invoice is owed
M38-F18 the invoice's operating unit is the fulfilling store's
"""

import pytest
from odoo.addons.cd_storefront.tests.test_a04_c2_c13_storefront import (  # noqa: F401
    _events,
    _mk,
    w,
)
from odoo.exceptions import AccessError, UserError, ValidationError

from .test_storefront_books import PARAM, _lines, sf  # noqa: F401

pytestmark = [pytest.mark.financial]
REFUSED = (UserError, ValidationError, AccessError)


def _gateway_paid(w, qty=1, method="branch_pickup"):
    order = w.placed(qty, rail="bkash", method=method)
    order.sudo()._sf_gateway_confirm(
        "bkash", order.sudo().name, "TRX-B4-%s" % order.id, order.sudo().total_amount
    )
    order.invalidate_recordset()
    return order


# ============================================================ M38-F1 / F18
def test_f1_the_invoice_reproduces_the_m11_price_with_vat(sf):
    w = sf
    order, _rcpt = w.paid(2)
    order = order.sudo()
    line = order.line_ids
    assert (line.unit_price_excl, line.unit_price) == (2173.91, 2500.0)
    inv = order.ar_invoice_id
    assert inv.total_payable == 5000.0
    assert _lines(inv.posted_move_id) == {
        w.acc.ar.code: (5000.0, 0.0),
        w.acc.revenue.code: (0.0, 4347.83),
        w.acc.vat.code: (0.0, 652.17),
    }


def test_f18_invoice_ou_is_the_fulfilling_store(sf):
    w = sf
    env = w.env
    ou2 = env["operating.unit"].search([("id", "!=", w.ou.id)], limit=1)
    if not ou2:
        pytest.skip("one operating unit only on this database")
    store = env["fix.stock.location"].create(
        {
            "name": "B4 OU2 store",
            "code": "B4OU2%s" % w.part.id,
            "location_type": "branch",
            "operating_unit_id": ou2.id,
        }
    )
    order = w.placed(1, rail="bkash")
    order.sudo().write({"stock_location_id": store.id})
    rcpt = w.receipt(order, "B4-OU-%s" % order.id)
    order.with_user(w.cashier).action_confirm_payment(payment_ref=rcpt.reference)
    order.invalidate_recordset()
    assert order.sudo().ar_invoice_id.operating_unit_id == ou2


# ============================================================ M38-F2
def test_f2_cancelled_gateway_payment_is_refunded_from_its_receipt(sf):
    w = sf
    env = w.env
    w.params.set_param(PARAM, "NOPE-B4")  # the invoice leg fails closed (setup)
    order = _gateway_paid(w)
    s = order.sudo()
    assert (s.state, s.posting_state, s.ar_invoice_id) == (
        "paid",
        "pending",
        s.ar_invoice_id.browse(),
    )
    order.with_user(w.operator).action_cancel(reason="customer changed mind")
    order.invalidate_recordset()
    s = order.sudo()
    assert s.state == "cancelled" and s.refund_due == 2500.0
    assert s.posting_state == "posted", s.posting_note
    refund = s.ar_refund_id
    assert refund and refund.amount == 2500.0 and refund.method == "bkash"
    receipt = s.ar_receipt_id
    assert receipt.method == "bkash" and receipt.reference == s.payment_ref
    assert _lines(receipt.posted_move_id) == {
        w.acc.mfs.code: (2500.0, 0.0),
        w.acc.ar.code: (0.0, 2500.0),
    }
    # another accountant authorises it: treasury pays it back on the wallet
    refund.with_user(w.acct).action_authorise()
    pay = (
        env["fix.payment.execution"]
        .sudo()
        .search([("source_model", "=", "fix.ar.refund"), ("source_id", "=", refund.id)])
    )
    assert pay.amount == 2500.0 and pay.method == "mobile_fs"
    # idempotent: a retry and the relay raise nothing more
    s._sfb_post()
    out = (
        env["fix.storefront.order"]
        .sudo()
        .consume_storefront_order_cancelled(
            {"aggregate": "fix.storefront.order", "aggregate_id": s.id}
        )
    )
    assert out["refund"] == refund.name
    assert env["fix.ar.refund"].sudo().search_count([("receipt_id", "=", receipt.id)]) == 1


def test_f2_unpaid_cancellation_posts_nothing(sf):
    w = sf
    order = w.placed(1, rail="bkash")
    order.with_user(w.operator).action_cancel(reason="never paid")
    s = order.sudo()
    assert s.refund_due == 0.0 and s.posting_state == "none" and not s.ar_refund_id


# ============================================================ M38-F3
def test_f3_one_refund_per_return(sf):
    """p2 on fix_real: the approved refund's credit note was pending (no
    invoice yet), the relay hand-off raised M50 instruction 56, and the
    credit note, once issued, raised 57 - 1,150 refunded twice."""
    w = sf
    env = w.env
    w.params.set_param(PARAM, "NOPE-B4")
    order = _gateway_paid(w)
    ret = (
        env["fix.storefront.return"]
        .with_user(w.operator)
        .create(
            {
                "order_id": order.id,
                "customer_id": order.customer_id.id,
                "reason": "defective",
                "refund_amount": 2500.0,
            }
        )
    )
    ret.with_user(w.operator).action_approve()
    ret.with_user(w.operator2).action_receive_and_inspect(condition="grade_a")
    w.refund_approved(ret)
    assert ret.sudo().state == "refund_approved" and not ret.sudo().ar_credit_note_id
    Consumers = env["fix.a04.storefront.consumers"].sudo()
    with pytest.raises(UserError, match="waits for the storefront bridge"), env.cr.savepoint():
        Consumers.consume_storefront_refund_approved(
            {"aggregate": ret._name, "aggregate_id": ret.id, "payload": {"refund_amount": 2500.0}}
        )
    Exec = env["fix.payment.execution"].sudo()
    assert not Exec.search([("source_model", "=", ret._name), ("source_id", "=", ret.id)])
    # the cause is fixed; the hourly job posts the order and the return
    w.params.set_param(PARAM, w.acc.revenue.code)
    env["fix.storefront.order"]._cron_retry_storefront_postings()
    ret.invalidate_recordset()
    note = ret.sudo().ar_credit_note_id
    assert note
    out = Consumers.consume_storefront_refund_approved(
        {"aggregate": ret._name, "aggregate_id": ret.id, "payload": {"refund_amount": 2500.0}}
    )
    assert out["id"] == note.id and not out["created"]
    # a second credit note for the same return is refused, whoever raises it
    with pytest.raises(UserError, match="one refund per"), env.cr.savepoint():
        env["fix.credit.note"].sudo().create(
            {
                "company_id": note.company_id.id,
                "operating_unit_id": note.operating_unit_id.id,
                "invoice_id": note.invoice_id.id,
                "customer_id": note.customer_id.id,
                "amount": 2500.0,
                "reason_code": "return",
                "source_model": ret._name,
                "source_id": ret.id,
                "source_amount": 2500.0,
            }
        )
    note.with_user(w.acct).action_approve()
    note.with_user(w.acct).action_issue()
    refunds = Exec.search([("partner_id", "=", w.customer.id)]) | Exec.search(
        [("source_model", "=", ret._name), ("source_id", "=", ret.id)]
    )
    assert len(refunds.filtered(lambda p: p.amount == 2500.0)) == 1


# ============================================================ M38-F10
def test_f10_dispatch_refused_while_the_invoice_is_owed(sf):
    w = sf
    w.params.set_param(PARAM, "NOPE-B4")
    order = _gateway_paid(w)
    with pytest.raises(UserError, match="BRU-ECM-20"), w.env.cr.savepoint():
        order.with_user(w.operator).action_dispatch()
    assert order.sudo().state == "paid"
    w.params.set_param(PARAM, w.acc.revenue.code)
    order.with_user(w.operator).action_dispatch()
    assert order.sudo().state == "dispatched" and order.sudo().ar_invoice_id


def test_f10_cod_dispatch_undone_when_its_invoice_cannot_be_raised(sf):
    w = sf
    w.params.set_param(PARAM, "NOPE-B4")
    order = w.placed(1, rail="cod")
    with pytest.raises(UserError, match="BRU-ECM-20"), w.env.cr.savepoint():
        order.with_user(w.operator).action_dispatch()
    order.invalidate_recordset()
    assert order.sudo().state == "pending_payment"


# ============================================================ M38-F6
def _bucket(w):
    w.env.invalidate_all()
    return w.env["fix.stock.onhand"]._bucket(w.part, w.loc, "owned")


def test_f6_placement_reserves_and_cancel_releases(sf):
    w = sf
    order = w.placed(2, rail="bkash")
    assert (_bucket(w).qty, _bucket(w).reserved) == (10.0, 2.0)
    # the reserved units are not sold twice: 10 on hand, 2 held, 9 refused
    with pytest.raises(UserError), w.env.cr.savepoint():
        w.placed(9, rail="bkash")
    order.with_user(w.operator).action_cancel(reason="changed mind")
    assert _bucket(w).reserved == 0.0


def test_f6_dispatch_consumes_the_reservation(sf):
    w = sf
    order, _rcpt = w.paid(2)
    assert _bucket(w).reserved == 2.0
    order.with_user(w.operator).action_dispatch()
    assert (_bucket(w).qty, _bucket(w).reserved) == (8.0, 0.0)


class TestDeployment:
    def test_consumer_registered(self, odoo_env):
        row = odoo_env.ref("cd_storefront_finance.consumer_storefront_order_cancelled")
        assert (row.event_type, row.model, row.method) == (
            "storefront.order_cancelled",
            "fix.storefront.order",
            "consume_storefront_order_cancelled",
        )
        assert hasattr(odoo_env["fix.storefront.order"], row.method)
