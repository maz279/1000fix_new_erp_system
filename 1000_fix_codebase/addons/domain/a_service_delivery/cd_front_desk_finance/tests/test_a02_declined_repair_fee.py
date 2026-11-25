"""FR-SRM-029 / SP-013 step 19: a declined repair is charged its diagnostic fee.

The fee taken at intake is an ADVANCE receipt on the order. When the customer
declined the repair, the advance stayed as their credit in the unapplied-cash
queue: the diagnosis was supplied but never invoiced (no Mushak 6.3, no
revenue, no VAT), and auto-match could offer the money to the customer's next
invoice. Cancelling with a decline reason now invoices the fee and pays it
from the advance. ``odoo_env`` rolls back after each test.
"""

# ruff: noqa: F811  (the imported fixtures are used as parameters)
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_a02_order_money_reaches_books import (  # noqa: F401
    books,
)
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import fin  # noqa: F401
from odoo.exceptions import AccessError, UserError

pytestmark = [pytest.mark.financial]

FEE = 300.0


def _charge_code(env):
    Product = env["product.product"]
    product = Product.search([("default_code", "=", "CHG-DIAG")], limit=1)
    return product or Product.create(
        {"name": "Diagnostic / Inspection Fee", "default_code": "CHG-DIAG", "type": "service"}
    )


def _declinable(m, fee=FEE, channel="bkash"):
    """An order awaiting the customer's decision, its fee paid at intake."""
    m.shift(as_user=m.so_cashier)
    order = m.job(2000.0, customer=m.customer, state="awaiting_approval")
    intake = m.intake(
        device_id=m.device.id,
        diagnostic_fee_bdt=fee,
        payment_channel=channel,
        payment_trx_ref="BKX-DECL" if channel != "waived" else False,
    )
    intake.sudo()._guarded().write({"service_order_id": order.id})
    receipt = intake.sudo()._fdf_raise_fee_receipt()
    return order, receipt


def _fee_invoice(order):
    return (
        order.env["fix.ar.invoice"]
        .sudo()
        .search([("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)])
    )


def test_a_declined_repair_is_invoiced_its_fee_paid_from_the_advance(books):
    m = books
    product = _charge_code(m.env)
    order, receipt = _declinable(m)
    assert receipt.unapplied_amount == FEE

    order.action_cancel(reason_code="estimate_declined")

    invoice = _fee_invoice(order)
    invoice.invalidate_recordset()
    assert len(invoice) == 1 and invoice.state == "paid"
    assert invoice.total_payable == FEE  # the price the customer agreed, VAT inside
    assert round(invoice.taxable_amount + invoice.vat_amount, 2) == FEE
    assert invoice.mushak_id, "the fee is a supply: it carries its Mushak 6.3"
    (line,) = invoice.line_ids
    assert line.line_type == "diagnostic" and line.product_id == product
    receipt.invalidate_recordset()
    assert receipt.unapplied_amount == 0.0  # no longer offered to the next invoice
    assert m.ar_of(order.customer_id) == 0.0
    # replay-safe: a second cancel path never raises a second invoice
    assert order.env["fix.ar.invoice"].sudo().from_declined_service_order(order) == invoice


def test_a_refused_fee_invoice_never_undoes_the_cancel_and_finance_retries(books):
    m = books
    order, receipt = _declinable(m)
    m.params.set_param("cd_billing_engine.diagnostic_fee_product_code", "NO-SUCH-CODE")

    order.action_cancel(reason_code="customer_declined")

    assert order.state == "cancelled" and not _fee_invoice(order)
    assert "Diagnostic fee not invoiced" in " ".join(order.message_ids.mapped("body"))
    receipt.invalidate_recordset()
    assert receipt.unapplied_amount == FEE  # still the customer's credit meanwhile

    m.params.set_param(
        "cd_billing_engine.diagnostic_fee_product_code", _charge_code(m.env).default_code
    )
    with pytest.raises(AccessError):
        order.with_user(m.so_cashier).action_invoice_diagnostic_fee()
    order.with_user(m.fin_manager).action_invoice_diagnostic_fee()
    invoice = _fee_invoice(order)
    invoice.invalidate_recordset()
    assert invoice.state == "paid" and invoice.total_payable == FEE


def test_only_a_decline_charges_the_fee(books):
    m = books
    _charge_code(m.env)
    order, receipt = _declinable(m)

    order.action_cancel(reason_code="duplicate")

    # a duplicate order's fee is the customer's money: it stays their credit
    # (moved to the live order or refunded by finance), never invoiced
    assert not _fee_invoice(order)
    receipt.invalidate_recordset()
    assert receipt.unapplied_amount == FEE
    with pytest.raises(UserError, match="not a declined repair"):
        order.with_user(m.fin_manager).action_invoice_diagnostic_fee()


def test_a_waived_fee_raises_no_invoice(books):
    m = books
    _charge_code(m.env)
    order = m.job(2000.0, customer=m.customer, state="awaiting_approval")

    order.action_cancel(reason_code="customer_declined")

    assert order.state == "cancelled" and not _fee_invoice(order)


def test_a_refused_repair_billed_then_declined_is_billed_once(books):
    """D6 then FR-SRM-029: a repair refused after it was done is billed its
    approved estimate (the intake fee applied to it); cancelling it as
    declined raises no second, fee-only invoice."""
    m = books
    _charge_code(m.env)
    m.shift(as_user=m.so_cashier)
    order = m.job(2000.0, customer=m.customer, state="ready")
    intake = m.intake(
        device_id=m.device.id,
        diagnostic_fee_bdt=FEE,
        payment_channel="bkash",
        payment_trx_ref="BKX-REFUSED",
    )
    intake.sudo()._guarded().write({"service_order_id": order.id})
    receipt = intake.sudo()._fdf_raise_fee_receipt()

    order.action_bill_refused_repair()
    order.action_cancel(reason_code="customer_declined")

    invoices = _fee_invoice(order)
    assert len(invoices) == 1, invoices
    invoices.invalidate_recordset()
    assert invoices.total_payable > FEE  # the estimate, not the fee
    assert not invoices.line_ids.filtered(lambda line: line.line_type == "diagnostic")
    receipt.invalidate_recordset()
    assert receipt.unapplied_amount == 0.0  # the fee went to the estimate invoice
    assert "no separate diagnostic fee" in " ".join(order.message_ids.mapped("body"))
