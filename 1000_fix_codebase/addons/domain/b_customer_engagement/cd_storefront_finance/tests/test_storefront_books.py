"""cd_storefront_finance — the storefront order reaches the books (E2E3 flow 4).

On a copy of fix_real (12 Nov 2026) a paid, delivered and refunded storefront
order produced no invoice, no Mushak 6.3, no revenue, no output VAT, no
stock-out and no restock; its M20 receipt sat unapplied as a customer credit;
the refund was a native out_refund that debited revenue never credited and
wrote a 6.7 with no 6.3, outside the M20 sub-ledger (E3-08).

These tests drive the storefront as its users do (a payment officer, a
storefront operator, a refund approver deciding from the M63 inbox, two
accountants) and read what reached M20, the VAT register, the GL and the M15
stock ledger. ``odoo_env`` rolls every test back.
"""

# ruff: noqa: F811  (the A04 storefront fixture is imported and used as a parameter)
import itertools
from types import SimpleNamespace

import pytest
from odoo.addons.cd_storefront.tests.test_a04_c2_c13_storefront import (  # noqa: F401
    _consignment,
    _events,
    _mk,
    w,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial, pytest.mark.tax]

REFUSED = (UserError, ValidationError, AccessError)
PARAM = "cd_storefront_finance.account_code.revenue"
BILLING = "cd_billing_engine.account_code."
_SEQ = itertools.count(1)


def _balance(env, account, partner=None):
    env.flush_all()
    domain = [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    if partner:
        domain.append(("partner_id", "=", partner.id))
    return round(sum(env["account.move.line"].search(domain).mapped("balance")), 2)


def _lines(move):
    """{account code: (debit, credit)} of a move."""
    out = {}
    for line in move.line_ids:
        dr, cr = out.get(line.account_id.code, (0.0, 0.0))
        out[line.account_id.code] = (round(dr + line.debit, 2), round(cr + line.credit, 2))
    return out


def _suspense(env, order):
    return (
        env["fix.inventory.valuation.suspense"]
        .sudo()
        .search([("source_ref", "like", order.name)], order="id")
    )


@pytest.fixture
def sf(w):
    """The A04 storefront world plus the books: the billing roles named by
    their parameters, two accountants, and the charger sold on the storefront
    as a spare part with stock in a central store."""
    env = w.env
    n = next(_SEQ)
    params = env["ir.config_parameter"].sudo()

    def account(key, kind, name):
        return env["account.account"].create(
            {"code": "SFB%d%s" % (n, key), "name": "SF %s %d" % (name, n), "account_type": kind}
        )

    acc = SimpleNamespace(
        ar=account("AR", "asset_receivable", "receivables"),
        revenue=account("REV", "income", "storefront revenue"),
        billing_revenue=account("BRV", "income", "service revenue"),
        vat=account("VAT", "liability_current", "VAT output"),
        mfs=account("MFS", "asset_current", "MFS / card clearing"),
    )
    params.set_param(BILLING + "ar", acc.ar.code)
    params.set_param(BILLING + "revenue", acc.billing_revenue.code)
    params.set_param(BILLING + "vat_output", acc.vat.code)
    params.set_param(BILLING + "channel_mfs", acc.mfs.code)
    params.set_param(PARAM, acc.revenue.code)

    w.acct = _mk(env, "sfb_acct_%d" % n, "account.group_account_user")
    w.acct2 = _mk(env, "sfb_acct2_%d" % n, "account.group_account_user")
    variant = w.product.product_variant_id
    variant.default_code = "SFB-CHG-%d" % n
    w.part = env["fix.spare.part"].create(
        {
            "name": "SF charger %d" % n,
            "part_number": "SFBP-%d" % n,
            "unit_cost": 1500.0,
            "product_id": variant.id,
        }
    )
    w.loc = env["fix.stock.location"].create(
        {
            "name": "SF central store %d" % n,
            "code": "SFBL%d" % n,
            "location_type": "central",
            "operating_unit_id": w.ou.id,
        }
    )
    env["fix.stock.onhand"]._apply(w.part, w.loc, "owned", 10.0, 1500.0)
    w.acc, w.params = acc, params

    def onhand(status="unrestricted"):
        env.invalidate_all()
        row = env["fix.stock.onhand"]._bucket(w.part, w.loc, "owned", status)
        return row.qty if row else 0.0

    def placed(qty=2, rail="bkash", method="branch_pickup"):
        cart = env["fix.storefront.cart"].with_user(w.clerk).create({"customer_id": w.customer.id})
        env["fix.storefront.cart.line"].with_user(w.clerk).create(
            {"cart_id": cart.id, "product_id": w.product.id, "quantity": qty}
        )
        return cart.action_place_order(shipping_method=method, payment_rail=rail)

    def receipt(order, ref):
        """The bKash receipt finance records in M20 (Dr channel / Cr AR)."""
        rec = (
            env["fix.ar.receipt"]
            .with_user(w.acct)
            .create(
                {
                    "customer_id": w.customer.id,
                    "amount": order.sudo().total_amount,
                    "method": "bkash",
                    "reference": ref,
                }
            )
        )
        rec.action_confirm()
        return rec

    def paid(qty=2, ref=None, **kw):
        order = placed(qty, **kw)
        ref = ref or "BKX-SFB-%d-%d" % (n, order.id)
        rcpt = receipt(order, ref)
        order.with_user(w.cashier).action_confirm_payment(payment_ref=ref)
        order.invalidate_recordset()
        return order, rcpt

    def delivered(qty=2, **kw):
        order, rcpt = paid(qty, **kw)
        order.with_user(w.operator).action_dispatch()
        order.with_user(w.operator).action_deliver()
        order.invalidate_recordset()
        return order, rcpt

    def returned(
        order, reason="defective", condition="grade_a", amount=None, model="fix.storefront.return"
    ):
        ret = (
            env[model]
            .with_user(w.operator)
            .create(
                {
                    "order_id": order.id,
                    "customer_id": order.customer_id.id,
                    "reason": reason,
                    "refund_amount": order.sudo().total_amount if amount is None else amount,
                }
            )
        )
        ret.with_user(w.operator).action_approve()
        ret.with_user(w.operator2).action_receive_and_inspect(condition=condition)
        ret.invalidate_recordset()
        return ret

    def refund_approved(ret):
        approve_via_inbox(ret, w.approver, requester=w.operator, justification="E2E3 flow 4")
        ret.invalidate_recordset()
        return ret

    w.onhand, w.placed, w.receipt, w.paid = onhand, placed, receipt, paid
    w.delivered, w.returned, w.refund_approved = delivered, returned, refund_approved
    return w


# ============================================================ the sale
def test_a_paid_order_is_invoiced_in_m20_and_its_receipt_applied(sf):
    """E2E3 s05/s07: the order is invoiced the moment it is paid (the tax
    point): an M20 invoice with its Mushak 6.3 and GL (Dr AR / Cr revenue /
    Cr VAT), and the receipt finance recorded is applied to it, not left as
    a customer credit."""
    w = sf
    env = w.env
    order, rcpt = w.paid(2)
    order = order.sudo()
    assert order.state == "paid"
    inv = order.ar_invoice_id
    assert inv, "no M20 invoice for the paid storefront order"
    assert (inv.source_model, inv.source_id) == ("fix.storefront.order", order.id)
    assert inv.state == "paid" and inv.customer_id == w.customer
    # the order's own price, VAT-inclusive: 5,000.00 = 4,347.83 + 652.17
    assert (inv.taxable_amount, inv.vat_amount, inv.total_payable) == (4347.83, 652.17, 5000.0)
    assert inv.revenue_account_id == w.acc.revenue

    row = inv.mushak_id
    assert row and row.row_type == "invoice" and row.posted
    assert (row.taxable_amount, row.vat_amount, row.total_payable) == (4347.83, 652.17, 5000.0)

    assert _lines(inv.posted_move_id) == {
        w.acc.ar.code: (5000.0, 0.0),
        w.acc.revenue.code: (0.0, 4347.83),
        w.acc.vat.code: (0.0, 652.17),
    }
    # the receipt is applied: nothing unapplied, the customer owes nothing
    rcpt.invalidate_recordset()
    assert rcpt.unapplied_amount == 0.0
    assert inv.allocation_ids.receipt_id == rcpt and inv.amount_residual == 0.0
    assert order.ar_receipt_id == rcpt
    assert _balance(env, w.acc.ar, w.customer) == 0.0
    assert _balance(env, w.acc.mfs) == 5000.0
    assert order.posting_state == "posted" and not order.posting_note
    # payment moves no stock: the goods are still on the shelf
    assert w.onhand() == 10.0


def test_the_invoice_uses_the_order_line_prices(sf):
    """fix_real D2-05: every list price is 1.00. The bridge invents nothing:
    2 x 1.00 is invoiced as 1.74 + 0.26, and a later catalogue change does
    not reach an order already placed."""
    w = sf
    w.product.list_price = 1.0
    order = w.placed(2)
    w.product.list_price = 9999.0
    rcpt = w.receipt(order, "BKX-SFB-PRICE-%d" % order.id)
    order.with_user(w.cashier).action_confirm_payment(payment_ref=rcpt.reference)
    inv = order.sudo().ar_invoice_id
    assert (inv.taxable_amount, inv.vat_amount, inv.total_payable) == (1.74, 0.26, 2.0)
    assert inv.state == "paid"


def test_a_gateway_payment_is_captured_as_an_m20_receipt(sf):
    """The signed gateway callback is the proof of payment: the bridge books
    it as an M20 receipt on the channel clearing (Dr MFS / Cr AR) and applies
    it, so a customer who paid online is never left owing."""
    w = sf
    env = w.env
    order = w.placed(1, rail="bkash")
    env["fix.storefront.order"]._sf_gateway_confirm("bkash", order.name, "GW-TRX-SFB-1", 2500.0)
    order = order.sudo()
    order.invalidate_recordset()
    assert order.state == "paid" and order.payment_source == "gateway"
    inv, rcpt = order.ar_invoice_id, order.ar_receipt_id
    assert inv.state == "paid"
    assert (rcpt.state, rcpt.method, rcpt.reference, rcpt.amount) == (
        "confirmed",
        "bkash",
        "GW-TRX-SFB-1",
        2500.0,
    )
    assert _balance(env, w.acc.mfs) == 2500.0
    assert _balance(env, w.acc.ar, w.customer) == 0.0
    assert order.posting_state == "posted"
    # the bridge's receipt pays this order only
    other = w.placed(1)
    with pytest.raises(UserError, match="No confirmed M20 receipt"), env.cr.savepoint():
        other.with_user(w.cashier).action_confirm_payment(payment_ref="GW-TRX-SFB-1")


def test_dispatch_issues_the_stock_once(sf):
    """The goods leave the M15 ledger when they leave the store (dispatch),
    at the average cost, with their valuation suspense row (the COGS the
    period close moves to the GL). Delivery and retries move nothing more."""
    w = sf
    env = w.env
    order, _rcpt = w.paid(2)
    order.with_user(w.operator).action_dispatch()
    assert w.onhand() == 8.0
    susp = _suspense(env, order)
    assert [(s.entry_type, s.quantity, s.total_valuation) for s in susp] == [
        ("storefront_sale", -2.0, -3000.0)
    ]
    assert susp._fix_stock_effect_total() == -3000.0
    line = order.sudo().line_ids
    assert (line.stock_state, line.stock_location_id, line.stock_part_id) == (
        "issued",
        w.loc,
        w.part,
    )
    order.with_user(w.operator).action_deliver()
    order.with_user(w.operator).action_retry_posting()
    env["fix.storefront.order"]._cron_retry_storefront_postings()
    assert w.onhand() == 8.0 and len(_suspense(env, order)) == 1
    assert len(order.sudo().ar_invoice_id) == 1
    assert (
        env["fix.ar.invoice"].search_count(
            [("source_model", "=", "fix.storefront.order"), ("source_id", "=", order.id)]
        )
        == 1
    )
    assert order.sudo().posting_state == "posted"
    # the posting outcome is the system's: nobody types it
    for vals in ({"posting_state": "pending"}, {"ar_invoice_id": False}):
        with pytest.raises(REFUSED), env.cr.savepoint():
            order.with_user(w.operator).write(vals)


# ============================================================ the refund
def test_a_return_restocks_and_the_refund_is_an_m20_credit_note(sf):
    """E2E3 s10-s19: the item comes back into stock when it is received; the
    approved refund is an M20 credit note against the order's invoice (6.7
    against the 6.3, revenue and VAT reversed, AR credited, the money back
    through an M50 instruction), and issuing it completes the return."""
    w = sf
    env = w.env
    order, _rcpt = w.delivered(2)
    inv = order.sudo().ar_invoice_id
    assert w.onhand() == 8.0
    ret = w.returned(order, reason="defective", condition="grade_a")
    # received and inspected as resalable: back on the shelf, at its cost
    assert w.onhand() == 10.0
    assert [s.total_valuation for s in _suspense(env, order)] == [-3000.0, 3000.0]
    assert _suspense(env, order)._fix_stock_effect_total() == 0.0
    assert ret.sudo().restock_state == "restocked"

    w.refund_approved(ret)
    ret = ret.sudo()
    assert ret.state == "refund_approved"
    note = ret.ar_credit_note_id
    assert note, "no M20 credit note requested for the approved refund"
    assert (note.invoice_id, note.amount, note.reason_code, note.state) == (
        inv,
        5000.0,
        "return",
        "pending_approval",
    )
    # the native out_refund path is closed
    with pytest.raises(UserError, match="M20 credit note"), env.cr.savepoint():
        ret.with_user(w.cashier).action_record_credit_note(credit_note="RINV/2026/00001")
    # the treasury hand-off of storefront.refund_approved finds this note and
    # raises neither a second credit note nor a second refund instruction
    if "fix.a04.storefront.consumers" in env:
        [event] = _events(w, "storefront.refund_approved", ret)
        out = env["fix.a04.storefront.consumers"].consume_storefront_refund_approved(
            {"aggregate": ret._name, "aggregate_id": ret.id, "payload": {"refund_amount": 5000.0}}
        )
        assert out == {"model": "fix.credit.note", "id": note.id, "created": False}, event
    assert env["fix.credit.note"].search_count([("invoice_id", "=", inv.id)]) == 1
    # not complete until finance issues it
    with pytest.raises(UserError, match="issues it"), env.cr.savepoint():
        ret.with_user(w.cashier).action_record_credit_note(credit_note=note)

    # finance decides the credit note under M20's own controls
    note.with_user(w.acct).action_approve()
    note.with_user(w.acct).action_issue()
    ret.invalidate_recordset()
    note.invalidate_recordset()
    assert note.state == "issued"
    assert ret.state == "refunded" and ret.refunded_at
    assert "CN/%d" % note.id in (ret.credit_note_ref or "")
    assert not ret.credit_note_id  # no native account.move anywhere
    assert len(_events(w, "storefront.refund_processed", ret)) == 1

    six7 = note.mushak_note_id
    assert six7.row_type == "credit_note" and six7.original_id == inv.mushak_id
    assert (six7.taxable_amount, six7.vat_amount) == (-4347.83, -652.17)
    assert _lines(note.posted_move_id) == {
        w.acc.revenue.code: (4347.83, 0.0),
        w.acc.vat.code: (652.17, 0.0),
        w.acc.ar.code: (0.0, 5000.0),
    }
    # revenue and VAT are back to nothing; the money goes back via treasury
    assert _balance(env, w.acc.revenue) == 0.0 and _balance(env, w.acc.vat) == 0.0
    assert note.refund_amount == 5000.0 and note.refund_ref
    pay = env["fix.payment.execution"].sudo().search([("name", "=", note.refund_ref)])
    assert pay.amount == 5000.0


def test_a_worn_return_goes_to_quarantine_and_credits_the_refund_only(sf):
    """Change of mind, grade B: the 20% restocking fee stays revenue; the
    item is not resalable as it is, so it comes back into quarantine."""
    w = sf
    order, _rcpt = w.delivered(1)
    ret = w.returned(order, reason="changed_mind", condition="grade_b")
    assert ret.sudo().refund_amount == 2000.0
    assert w.onhand() == 9.0 and w.onhand("quarantine") == 1.0
    quarantine = w.env["fix.stock.quarantine"].sudo().search([("source_ref", "=", ret.name)])
    assert quarantine.qty == 1.0 and quarantine.reason == "customer_return"
    w.refund_approved(ret)
    note = ret.sudo().ar_credit_note_id
    assert note.amount == 2000.0
    note.with_user(w.acct).action_approve()
    note.with_user(w.acct).action_issue()
    assert ret.sudo().state == "refunded"
    # 500.00 of the 2,500.00 sale stays earned: 434.78 revenue + 65.22 VAT
    assert _balance(w.env, w.acc.revenue) == -434.78
    assert _balance(w.env, w.acc.vat) == -65.22


def test_the_rma_model_restocks_and_is_refunded_the_same_way(sf):
    """The second return model shares the refund lifecycle, and so the books."""
    w = sf
    order, _rcpt = w.delivered(1)
    rma = w.returned(order, reason="doa", condition="scrap", model="fix.storefront.rma")
    # a faulty item never goes back on the shelf
    assert w.onhand() == 9.0 and w.onhand("quarantine") == 1.0
    quarantine = w.env["fix.stock.quarantine"].sudo().search([("source_ref", "=", rma.name)])
    assert quarantine.reason == "defective"
    w.refund_approved(rma)
    note = rma.sudo().ar_credit_note_id
    assert note.invoice_id == order.sudo().ar_invoice_id and note.amount == 2500.0
    note.with_user(w.acct).action_approve()
    note.with_user(w.acct).action_issue()
    assert rma.sudo().state == "refunded"
    # one credit note pays one refund
    other = w.returned(w.delivered(1)[0], reason="warranty", model="fix.storefront.rma")
    w.refund_approved(other)
    with (
        pytest.raises(UserError, match="already pays|is paid by|not the invoice"),
        w.env.cr.savepoint(),
    ):
        other.with_user(w.cashier).action_record_credit_note(credit_note="CN/%d" % note.id)


def test_cancelling_a_paid_order_requests_the_credit_note(sf):
    """A paid order is invoiced; cancelling it before dispatch credits the
    whole invoice through M20 (and moves no stock)."""
    w = sf
    order, _rcpt = w.paid(1)
    inv = order.sudo().ar_invoice_id
    order.with_user(w.operator).action_cancel(reason="customer called")
    order = order.sudo()
    note = order.ar_credit_note_id
    assert (note.invoice_id, note.amount, note.state) == (inv, 2500.0, "pending_approval")
    assert w.onhand() == 10.0
    assert order.posting_state == "posted"


def test_cash_on_delivery_is_invoiced_at_dispatch(sf):
    """No payment comes first: the 6.3 goes with the goods. The cash is
    collected at the door, so the receivable stays open on delivery until it
    is applied; the order says so instead of claiming it is settled."""
    w = sf
    order = w.placed(1, rail="cod")
    assert not order.sudo().ar_invoice_id
    order.with_user(w.operator).action_dispatch()
    order = order.sudo()
    inv = order.ar_invoice_id
    assert inv.state == "issued" and inv.total_payable == 2500.0
    assert w.onhand() == 9.0
    assert order.posting_state == "posted"
    order.with_user(w.operator).action_deliver()
    order.invalidate_recordset()
    assert order.posting_state == "pending"
    assert "cash on delivery" in (order.posting_note or "").lower()


# ============================================================ fail closed, not blocking
def test_an_unresolved_revenue_account_leaves_the_order_pending_until_configured(sf):
    w = sf
    env = w.env
    w.params.set_param(PARAM, "NOSUCH9")
    order, rcpt = w.paid(1)
    order = order.sudo()
    # the storefront is not blocked: the order is paid
    assert order.state == "paid" and order.posting_state == "pending"
    assert PARAM in (order.posting_note or "")
    assert not order.ar_invoice_id
    # still unconfigured: the job changes nothing
    env["fix.storefront.order"]._cron_retry_storefront_postings()
    order.invalidate_recordset()
    assert order.posting_state == "pending" and not order.ar_invoice_id
    # configured: the job posts it once and applies the receipt
    w.params.set_param(PARAM, w.acc.revenue.code)
    env["fix.storefront.order"]._cron_retry_storefront_postings()
    env["fix.storefront.order"]._cron_retry_storefront_postings()
    order.invalidate_recordset()
    assert order.posting_state == "posted" and not order.posting_note
    assert order.ar_invoice_id.state == "paid"
    assert (
        env["fix.ar.invoice"].search_count(
            [("source_model", "=", "fix.storefront.order"), ("source_id", "=", order.id)]
        )
        == 1
    )
    assert _balance(env, w.acc.revenue) == -2173.91


def test_without_the_storefront_parameter_the_billing_revenue_role_is_used(sf):
    w = sf
    w.params.set_param(PARAM, False)
    order, _rcpt = w.paid(1)
    inv = order.sudo().ar_invoice_id
    assert inv.state == "paid" and not inv.revenue_account_id
    assert _lines(inv.posted_move_id)[w.acc.billing_revenue.code] == (0.0, 2173.91)


def test_an_unknown_issue_location_keeps_the_stock_pending(sf):
    """Two stores hold the part: the bridge does not guess where it left."""
    w = sf
    env = w.env
    other = env["fix.stock.location"].create(
        {
            "name": "SF second store",
            "code": "SFBX%d" % w.loc.id,
            "location_type": "central",
            "operating_unit_id": w.ou.id,
        }
    )
    env["fix.stock.onhand"]._apply(w.part, other, "owned", 5.0, 1500.0)
    order, _rcpt = w.paid(1)
    order.with_user(w.operator).action_dispatch()
    order = order.sudo()
    assert order.state == "dispatched"  # dispatch is not blocked
    assert order.posting_state == "pending" and "Issue From Location" in order.posting_note
    assert order.line_ids.stock_state == "pending" and w.onhand() == 10.0
    order.with_user(w.operator).write({"stock_location_id": other.id})
    order.with_user(w.operator).action_retry_posting()
    order.invalidate_recordset()
    assert order.posting_state == "posted" and order.line_ids.stock_location_id == other
    with pytest.raises(UserError, match="issued"), env.cr.savepoint():
        order.with_user(w.operator).write({"stock_location_id": w.loc.id})
