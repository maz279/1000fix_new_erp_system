"""A02 ERP review (20 Nov 2026): the order-to-cash defects an independent
review of the A02 money changes found, each driven through the ORM.

The settlement, top-up, refund, credit and invoice paths are run as the
counter, the drawer and finance run them, and the books are read back.
"""

# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
from datetime import datetime

import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_a02_order_money_reaches_books import (  # noqa: F401
    books,
)
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import (  # noqa: F401
    _balance,
    fin,
)
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]


def _receipt(m, customer, amount, reference, method="bkash"):
    """An M20 receipt finance booked for the customer (Dr channel / Cr AR)."""
    rec = (
        m.env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "company_id": m.env.company.id,
                "branch_id": m.branch.id,
                "customer_id": customer.id,
                "amount": amount,
                "method": method,
                "reference": reference,
            }
        )
    )
    rec.action_confirm()
    return rec


def _counter_methods(m):
    """(cash, a non-cash tender the counter takes), from the seeded list."""
    Method = m.env["fix.payment.method"]
    Sale = m.env["fix.counter.sale"]
    cash = other = Method
    for method in Method.search([("for_counter", "=", True)], order="id"):
        try:
            key = Sale._counter_method_for(method)
        except UserError:
            continue
        if key == "cash" and not cash:
            cash = method
        elif key != "cash" and not other:
            other = method
    return cash, other


def _revise(m, order, price, version=2):
    return m.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "version": version,
            "state": "approved",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "Board",
                        "quantity": 1,
                        "unit_price": price,
                        "line_type": "labour",
                    },
                )
            ],
        }
    )


def _order_receipts(m, order):
    return m.env["fix.ar.receipt"].search(
        [("source_order_id", "=", order.id), ("is_order_advance", "=", False)], order="id"
    )


# ---------------------------------------------------------------- 1. top-up
def test_a_cash_top_up_of_a_bkash_settlement_is_drawer_cash(books):
    m = books
    s = m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="BKX-TOP-1", source="counter", tender="bkash"
    )
    _revise(m, order, 2000.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="CTR-TOP-CASH", source="counter", tender="cash"
    )
    first, top = _order_receipts(m, order)
    assert (first.method, first.account_id) == ("bkash", m.acc.mfs)
    # the top-up is the cash it was, on the drawer, under its own reference
    assert (top.method, top.account_id, top.reference) == ("cash", m.acc.drawer, "CTR-TOP-CASH")
    assert s.sudo().cash_payments == 1150.0
    assert _balance(m.env, m.acc.drawer) == 1150.0
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.state == "paid" and m.ar_of(order.customer_id) == 0.0


def test_a_counter_top_up_of_an_m20_settled_order_is_booked(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    _receipt(m, order.customer_id, 1150.0, "BANK-M20-1")
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="BANK-M20-1", source="m20_receipt"
    )
    _revise(m, order, 2000.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="CTR-TOP-M20", source="counter", tender="cash"
    )
    cash = _order_receipts(m, order).filtered(lambda r: r.method == "cash")
    assert cash.amount == 1150.0 and cash.reference == "CTR-TOP-M20"
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.total_payable == 2300.0 and invoice.state == "paid"
    assert m.ar_of(order.customer_id) == 0.0


# ------------------------------------------------------- 2. one receipt, one order
def test_one_m20_receipt_never_releases_two_devices(books):
    m = books
    customer = m.env["res.partner"].create({"name": "Two orders customer"})
    a = m.job(1000.0, customer=customer)
    b = m.job(1000.0, customer=customer)
    _receipt(m, customer, 2300.0, "BANK-ONE")
    a.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="BANK-ONE", source="m20_receipt"
    )
    with pytest.raises(UserError, match="No confirmed M20 receipt"):
        b.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=1150.0, reference="BANK-ONE", source="m20_receipt"
        )
    assert b.payment_settlement_state == "unpaid"


def test_a_diagnostic_fee_advance_is_not_a_settlement_receipt(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0, customer=m.customer)
    intake = m.intake(
        device_id=m.device.id,
        diagnostic_fee_bdt=300.0,
        payment_channel="bkash",
        payment_trx_ref="BKX-ADV-1",
    )
    intake.sudo()._guarded().write({"service_order_id": order.id})
    intake.sudo()._fdf_raise_fee_receipt()
    assert order._fix_amount_due() == 850.0
    # the advance is already netted: settling with it again would release
    # the device owing 850
    with pytest.raises(UserError, match="No confirmed M20 receipt"):
        order.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=850.0, reference="BKX-ADV-1", source="m20_receipt"
        )


def test_another_orders_advance_never_settles_a_second_order(books):
    """The advance is netted from ITS order's amount due; settling a second
    order of the same customer against it would count the money twice."""
    m = books
    m.shift(as_user=m.so_cashier)
    first = m.job(3000.0, customer=m.customer)
    intake = m.intake(
        device_id=m.device.id,
        diagnostic_fee_bdt=1000.0,
        payment_channel="bkash",
        payment_trx_ref="BKX-ADV-BIG",
    )
    intake.sudo()._guarded().write({"service_order_id": first.id})
    intake.sudo()._fdf_raise_fee_receipt()
    assert first._fix_amount_due() == 2450.0  # 3,450 less the 1,000 advance
    second = m.job(500.0, customer=m.customer)  # 575 due, the advance would cover it
    with pytest.raises(UserError, match="No confirmed M20 receipt"):
        second.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=575.0, reference="BKX-ADV-BIG", source="m20_receipt"
        )
    assert second.payment_settlement_state == "unpaid"


def test_a_receipt_that_topped_up_one_order_settles_no_other(books):
    m = books
    m.shift(as_user=m.so_cashier)
    customer = m.env["res.partner"].create({"name": "Top-up receipt customer"})
    first = m.job(1000.0, customer=customer)
    first.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="CTR-TR-1", source="counter", tender="cash"
    )
    _revise(m, first, 2000.0)
    _receipt(m, customer, 1150.0, "BANK-TOPUP-1")
    first.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="BANK-TOPUP-1", source="m20_receipt"
    )
    assert first.amount_settled_bdt == 2300.0  # the receipt now pays the first order
    second = m.job(1000.0, customer=customer)
    with pytest.raises(UserError, match="No confirmed M20 receipt"):
        second.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=1150.0, reference="BANK-TOPUP-1", source="m20_receipt"
        )


# --------------------------------------------- 3. an advance that covers the job
def test_an_advance_covering_the_estimate_releases_without_new_money(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(300.0, customer=m.customer)  # 345 with VAT
    intake = m.intake(
        device_id=m.device.id,
        diagnostic_fee_bdt=400.0,
        payment_channel="bkash",
        payment_trx_ref="BKX-ADV-2",
    )
    intake.sudo()._guarded().write({"service_order_id": order.id})
    intake.sudo()._fdf_raise_fee_receipt()
    assert order._fix_amount_due() == 0.0
    order._check_delivery_settlement_gate()  # nothing more is owed: no refusal
    with pytest.raises(UserError, match="owes nothing more"):
        order.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=1.0, reference="CTR-EXTRA", source="counter", tender="cash"
        )


# ----------------------------------------------------- 4. refund off the receipt
def test_a_refund_takes_the_money_off_the_receipt(books):
    m = books
    if "fix.finance.handback" not in m.env:
        pytest.skip("cd_settlement_ext not installed")
    m.shift(as_user=m.so_cashier)
    order = m.job(500.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=575.0, reference="CTR-RFD-1", source="counter", tender="cash"
    )
    receipt = order.settlement_receipt_id
    order.action_cancel(reason_code="customer_declined")  # superuser = supervisor
    assert order.payment_settlement_state == "refund_due"
    event = m.env["fix.event.outbox"].search(
        [("event_type", "=", "service_order.refund_requested"), ("aggregate_id", "=", order.id)]
    )
    Handback = m.env["fix.finance.handback"]
    result = Handback.consume_service_order_refund_requested(event._relay_event_dict())
    assert result["model"] == "fix.ar.refund" and result["created"]
    refund = m.env["fix.ar.refund"].browse(result["id"])
    assert (refund.receipt_id, refund.amount, refund.method) == (receipt, 575.0, "cash")
    receipt.invalidate_recordset()
    # refunded money is no longer on account: auto-match cannot re-apply it
    assert receipt.unapplied_amount == 0.0
    proposals = m.env["fix.ar.receipt"].action_auto_match()
    assert receipt.id not in {p["receipt_id"] for p in proposals}
    # a replay requests nothing twice
    again = Handback.consume_service_order_refund_requested(event._relay_event_dict())
    assert again["created"] is False
    assert m.env["fix.ar.refund"].search_count([("receipt_id", "=", receipt.id)]) == 1


# ------------------------------------------------------------- 5. live exposure
def test_credit_release_counts_orders_already_released(books):
    m = books
    customer = m.env["res.partner"].create({"name": "Credit customer", "is_company": True})
    m.env["fix.credit.profile"].create(
        {"customer_id": customer.id, "company_id": m.env.company.id, "credit_limit": 2000.0}
    )
    a = m.job(1000.0, customer=customer)
    b = m.job(1000.0, customer=customer)
    a.with_user(m.fin_manager).action_release_on_credit()
    # 1,150 is already out on account: 850 left, b needs 1,150
    with pytest.raises(UserError, match="left under its"):
        b.with_user(m.fin_manager).action_release_on_credit()
    assert b.payment_settlement_state == "unpaid"


def test_credit_exposure_counts_invoices_of_contact_persons(books):
    m = books
    company = m.env["res.partner"].create({"name": "Credit group", "is_company": True})
    contact = m.env["res.partner"].create({"name": "Buyer", "parent_id": company.id})
    m.env["fix.credit.profile"].create(
        {"customer_id": company.id, "company_id": m.env.company.id, "credit_limit": 2000.0}
    )
    first = m.job(1000.0, customer=contact)
    first.with_user(m.fin_manager).action_release_on_credit()
    m.deliver(first)  # 1,150 invoiced to the contact person
    second = m.job(1000.0, customer=company)
    with pytest.raises(UserError, match="left under its"):
        second.with_user(m.fin_manager).action_release_on_credit()


# ------------------------------------------------------- 6. basket header change
def test_a_basket_switched_to_another_tender_re_drafts_its_sales(books):
    m = books
    cash, bkash = _counter_methods(m)
    if not (cash and bkash):
        pytest.skip("counter payment methods not seeded")
    basket = m.env["fix.counter.basket"].create(
        {
            "operating_unit_id": m.ou2.id,
            "branch_id": m.branch.id,
            "payment_method_id": bkash.id,
            "transaction_ref": "BKX-BSK-1",
        }
    )
    m.env["fix.counter.sale"].sudo().create(
        {
            "branch_id": m.branch.id,
            "operating_unit_id": m.ou2.id,
            "product_id": m.product.id,
            "quantity": 1,
            "unit_price": 1000.0,
            "payment_method_id": bkash.id,
            "transaction_ref": "BKX-BSK-1",
            "basket_id": basket.id,
        }
    )
    assert basket.sale_ids.filtered(lambda s: s.state == "draft")
    basket.write({"payment_method_id": cash.id, "transaction_ref": False})
    basket.invalidate_recordset()
    assert not basket.sale_ids  # nothing drafted on the old tender survives


# ------------------------------------------------ 7. cash fee with no open shift
def test_a_cash_fee_taken_with_no_shift_is_still_booked(books):
    m = books
    m.params.set_param("cd_front_desk.order_cash_requires_open_shift", "0")
    order = m.job(1000.0, customer=m.customer)
    intake = m.intake(device_id=m.device.id, diagnostic_fee_bdt=200.0, payment_channel="cash")
    intake.sudo()._guarded().write({"service_order_id": order.id})
    receipt = intake.sudo()._fdf_raise_fee_receipt()
    assert receipt.is_order_advance and receipt.account_id == m.acc.drawer
    assert order._fix_amount_due() == 950.0  # never charged twice


# ------------------------------------------------ 9. another customer's TrxID
def test_another_customers_receipt_never_stands_in_for_a_field_trxid(books):
    m = books
    stranger = m.env["res.partner"].create({"name": "Stranger"})
    _receipt(m, stranger, 575.0, "TRX-SHARED")
    order = m.job(500.0, state="in_repair")
    order.with_context(fd_settlement_tender="bkash")._fix_record_settlement(
        575.0, "TRX-SHARED", "field_collection"
    )
    order.with_user(m.so_cashier).action_verify_settlement()
    receipt = order.settlement_receipt_id
    assert receipt and receipt.customer_id == order.customer_id and receipt.amount == 575.0


# ----------------------------------------- 10. the drawer verifier's scope
def test_a_drawer_cashier_verifies_an_mfs_collection_but_never_her_own(books):
    """Replaces the cash version: a front-desk cashier verifies a wallet
    TrxID against the merchant statement; segregation of duties holds."""
    m = books
    order = m.job(500.0, state="in_repair")
    order.with_user(m.fd_cashier).sudo().with_context(
        fd_settlement_tender="bkash"
    )._fix_record_settlement(575.0, "TRX-FD-OWN", "field_collection")
    with pytest.raises(UserError, match="Segregation of duties"):
        order.with_user(m.fd_cashier).action_verify_settlement()
    other = m.fd_cashier.copy({"login": "a02.rev.fdcash2.%d@test" % order.id})
    order.invalidate_recordset()
    order.with_user(other).action_verify_settlement()
    assert order.settlement_verified and order.settlement_verified_by == other
    assert order.settlement_receipt_id.account_id == m.acc.mfs


def test_field_cash_is_verified_only_once_it_is_in_a_drawer(books):
    m = books
    order = m.job(500.0, state="in_repair")
    order.with_context(fd_settlement_tender="cash")._fix_record_settlement(
        575.0, "COD/FO-NOT-IN", "field_collection"
    )
    with pytest.raises(UserError, match="not in a drawer yet"):
        order.with_user(m.fd_cashier).action_verify_settlement()
    assert not order.settlement_verified and not order.settlement_receipt_id


def test_a_drawer_cashier_of_another_unit_cannot_verify(books):
    m = books
    far = m.env["operating.unit"].create(
        {
            "name": "Far branch OU",
            "code": "FARX",
            "company_id": m.env.company.id,
            "partner_id": m.env.company.partner_id.id,
        }
    )
    outsider = m.fd_cashier.copy({"login": "a02.rev.far.%d@test" % far.id})
    vals = {"default_operating_unit_id": far.id}
    if "assigned_operating_unit_ids" in outsider._fields:
        vals["assigned_operating_unit_ids"] = [(6, 0, [far.id])]
    outsider.write(vals)
    order = m.job(500.0, state="in_repair")
    order.with_context(fd_settlement_tender="bkash")._fix_record_settlement(
        575.0, "TRX-FAR", "field_collection"
    )
    with pytest.raises(UserError, match="not one of your operating units"):
        order.with_user(outsider).action_verify_settlement()


# ------------------------------------------------- 11. company receipt, contact
def test_a_company_receipt_pays_its_contact_persons_order_invoice(books):
    m = books
    company = m.env["res.partner"].create({"name": "B2B Ltd", "is_company": True})
    contact = m.env["res.partner"].create({"name": "B2B buyer", "parent_id": company.id})
    order = m.job(1000.0, customer=contact)
    _receipt(m, company, 1150.0, "B2B-BANK-1", method="bkash")
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="B2B-BANK-1", source="m20_receipt"
    )
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.state == "paid" and invoice.amount_residual == 0.0


# --------------------------------------- 12/14. invoice company and tax point
def test_the_delivery_invoice_is_dated_on_the_dhaka_day(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="CTR-TAXPT", source="counter", tender="cash"
    )
    order._guarded().write({"state": "delivered", "delivered_at": datetime(2026, 11, 30, 20, 30)})
    invoice = order._fix_invoice_at_delivery()
    if not invoice:
        pytest.skip("1 Dec 2026 is not an open AR date in this database")
    # 20:30 UTC on 30 Nov is 02:30 on 1 Dec in Dhaka: the December return
    assert str(invoice.invoice_date) == "2026-12-01"
    assert invoice.company_id == order.company_id


# ------------------------------------------- 13. the estimate charges invoice VAT
def test_the_estimate_collects_exactly_what_the_invoice_charges(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(0.10)
    est = order._fix_governing_estimate()
    est.write(
        {
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "Screw",
                        "quantity": 1,
                        "unit_price": 0.10,
                        "line_type": "labour",
                    },
                )
            ]
        }
    )
    # per line 0.10 x 15% = 0.015 -> 0.02, twice: 0.04 (header rounding gave 0.03)
    assert round(est.vat_amount, 2) == 0.04 and round(est.grand_total, 2) == 0.24
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=order._fix_amount_due(), reference="CTR-PAISA", source="counter", tender="cash"
    )
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.total_payable == 0.24 and invoice.state == "paid"


# ---------------------------------------------------- 15. never off the books
def test_a_settlement_that_cannot_post_is_refused(books):
    from odoo.addons.cd_front_desk_finance.models.fix_order_cash_receipt import (
        assert_receipt_posted,
    )

    m = books
    receipt = _receipt(m, m.customer, 100.0, "GL-CHECK")
    assert receipt.posted_move_id
    assert_receipt_posted(receipt, "probe")  # posted: no refusal
    receipt.sudo()._guarded().write({"posted_move_id": False, "gl_note": "no journal"})
    with pytest.raises(UserError, match="could not be posted"):
        assert_receipt_posted(receipt, "probe")


def test_a_re_drafted_basket_voids_its_pending_price_approval(books):
    m = books
    cash, other = _counter_methods(m)
    if not (cash and other):
        pytest.skip("counter payment methods not seeded")
    basket = m.env["fix.counter.basket"].create(
        {"operating_unit_id": m.ou2.id, "branch_id": m.branch.id, "payment_method_id": cash.id}
    )
    sale = (
        m.env["fix.counter.sale"]
        .sudo()
        .create(
            {
                "branch_id": m.branch.id,
                "operating_unit_id": m.ou2.id,
                "product_id": m.product.id,
                "quantity": 1,
                "unit_price": 500.0,  # below the 1,000 list price
                "payment_method_id": cash.id,
                "basket_id": basket.id,
            }
        )
    )
    if not sale._fd_price_blocked():
        pytest.skip("the price ladder lets this cashier sell at 500")
    # the books fixture's cashier works the branch's own operating unit
    sale.with_user(m.fd_cashier).action_request_price_approvals()
    request = sale.approval_request_id
    assert request.state == "pending"
    basket.write({"payment_method_id": other.id, "transaction_ref": "TRX-NEW"})
    request.invalidate_recordset()
    assert request.exists() and request.state == "voided"  # evidence kept, inbox cleared
