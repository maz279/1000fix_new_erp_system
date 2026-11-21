"""A02 ERP audit (19 Nov 2026): a service order's money reaches the books.

On a copy of fix_real a BDT 1,150 counter settlement reached the drawer and
nothing else: no AR receipt, no GL. When the order was invoiced (Dr AR 1,150 /
Cr revenue / Cr VAT), nothing paid the invoice, so the customer who had paid
showed BDT 1,150 owing, and the M50 deposit credited the drawer account for
cash never debited to it. The invoice could not even post at 57 of 73 real
branches (the GL dimension took the company's FIRST operating unit).

These tests drive the order as the counter does and read the ledger.
"""

# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
import itertools

import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import (  # noqa: F401
    _balance,
    fin,
)
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

_SEQ = itertools.count(1)
BILLING = "cd_billing_engine.account_code."


@pytest.fixture
def books(fin):
    """The counter world plus AR / revenue / MFS accounts, a branch on its OWN
    operating unit (as every real branch is), a Service Order Cashier and a
    priced, approved job ready for collection."""
    m = fin
    env = m.env
    n = next(_SEQ)

    def account(key, kind, name):
        return env["account.account"].create(
            {"code": "OMB%d%s" % (n, key), "name": "Order %s %d" % (name, n), "account_type": kind}
        )

    m.ar = account("AR", "asset_receivable", "receivable")
    m.rev = account("REV", "income", "service revenue")
    # head-office cash differs from the branch drawer: counter cash must land
    # on the DRAWER (the account the M50 deposit credits), not the AR cash role
    m.ho_cash = account("HOC", "asset_cash", "head office cash")
    for role, acc in (
        ("ar", m.ar),
        ("revenue", m.rev),
        ("vat_output", m.acc.vat),
        ("cash", m.ho_cash),
        ("channel_mfs", m.acc.mfs),
    ):
        m.params.set_param(BILLING + role, acc.code)
    # a branch on its own OU, not the company's first one (X1)
    ou2 = env["operating.unit"].create(
        {
            "name": "Order books OU %d" % n,
            "code": "OB%d" % n,
            "company_id": env.company.id,
            "partner_id": env.company.partner_id.id,
        }
    )
    m.ou2 = ou2
    m.branch.operating_unit_id = ou2.id
    users = env["res.users"].with_context(no_reset_password=True)
    ous = [m.ou.id, ou2.id]

    def user(login, *groups):
        vals = {
            "name": "%s %d" % (login, n),
            "login": "a02.omb.%s.%d@test" % (login, n),
            "group_ids": [
                (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
            ],
        }
        if "assigned_operating_unit_ids" in users._fields:
            vals["assigned_operating_unit_ids"] = [(6, 0, ous)]
        elif "operating_unit_ids" in users._fields:
            vals["operating_unit_ids"] = [(6, 0, ous)]
        if "default_operating_unit_id" in users._fields:
            vals["default_operating_unit_id"] = ou2.id
        u = users.create(vals)
        env["hr.employee"].create({"name": "%s %d" % (login, n), "user_id": u.id})
        return u

    m.so_cashier = user(
        "socash", "cd_service_order.group_so_cashier", "cd_front_desk.group_fd_cashier"
    )
    m.fin_manager = user("finmgr", "account.group_account_manager")
    m.fd_cashier = user("fdcash", "cd_front_desk.group_fd_cashier")  # drawer only

    def job(price=1000.0, customer=None, state="ready"):
        customer = customer or env["res.partner"].create({"name": "Order books customer %d" % n})
        device = env["fix.device"].create({"device_model_id": m.device.device_model_id.id})
        order = env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": customer.id,
                "branch_id": m.branch.id,
                "operating_unit_id": ou2.id,
                "fault_description": "no power",
                "state": state,
            }
        )
        env["fix.estimate"].create(
            {
                "order_id": order.id,
                "state": "approved",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "description": "Board repair",
                            "quantity": 1,
                            "unit_price": price,
                            "line_type": "labour",
                        },
                    )
                ],
            }
        )
        return order

    def ar_of(partner):
        env.flush_all()
        lines = env["account.move.line"].search(
            [
                ("account_id", "=", m.ar.id),
                ("partner_id", "=", partner.id),
                ("parent_state", "=", "posted"),
            ]
        )
        return round(sum(lines.mapped("balance")), 2)

    def deliver(order):
        order._guarded().write({"state": "delivered"})
        return order._fix_invoice_at_delivery()

    m.job, m.ar_of, m.deliver = job, ar_of, deliver
    return m


def test_counter_cash_is_a_receipt_on_the_drawer_and_pays_the_invoice(books):
    m = books
    s = m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    due = order._fix_amount_due()
    assert due == 1150.0  # 1,000 + 15% VAT
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=due, reference="CTR-OMB-1", source="counter", tender="cash"
    )
    receipt = order.settlement_receipt_id
    assert receipt.state == "confirmed" and receipt.method == "cash"
    assert receipt.account_id == m.acc.drawer and receipt.source_order_id == order
    # the drawer took it and the books hold it: the customer is in credit
    assert s.sudo().cash_payments == 1150.0
    assert _balance(m.env, m.acc.drawer) == 1150.0
    assert m.ar_of(order.customer_id) == -1150.0
    # delivery raises the tax invoice, posted at the branch's own OU (X1),
    # and the receipt pays it: nothing is owed
    invoice = m.deliver(order)
    assert invoice and invoice.posted_move_id, invoice and invoice.gl_note
    invoice.invalidate_recordset()
    assert invoice.state == "paid" and invoice.amount_residual == 0.0
    assert m.ar_of(order.customer_id) == 0.0
    dims = m.env["fix.journal.dimension"].search(
        [("move_line_id.move_id", "=", invoice.posted_move_id.id)]
    )
    assert dims and set(dims.mapped("operating_unit_id")) == {m.ou2}


def test_a_wallet_payment_never_enters_the_drawer(books):
    m = books
    s = m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="BKX-OMB-1", source="counter", tender="bkash"
    )
    assert order.settlement_tender == "bkash"
    assert s.sudo().cash_payments == 0.0 and not order.counter_shift_id
    receipt = order.settlement_receipt_id
    assert receipt.method == "bkash" and receipt.account_id == m.acc.mfs
    assert _balance(m.env, m.acc.drawer) == 0.0
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.state == "paid"


def test_more_than_the_amount_due_is_refused_at_the_counter(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(500.0)
    with pytest.raises(UserError, match="more than the BDT 575.00 due"):
        order.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=50000.0, reference="CTR-OVER", source="counter", tender="cash"
        )
    assert order.payment_settlement_state == "unpaid"


def test_a_price_rise_after_payment_is_topped_up_not_deadlocked(books):
    m = books
    s = m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="CTR-TOP-1", source="counter", tender="cash"
    )
    # the approved estimate is revised upwards: 2,000 + VAT = 2,300 due
    m.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "version": 2,
            "state": "approved",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "Board",
                        "quantity": 1,
                        "unit_price": 2000.0,
                        "line_type": "labour",
                    },
                )
            ],
        }
    )
    assert order._fix_amount_due() == 2300.0
    with pytest.raises(UserError, match="does not cover"):
        order.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=100.0, reference="CTR-TOP-2", source="counter", tender="cash"
        )
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="CTR-TOP-2", source="counter", tender="cash"
    )
    assert order.amount_settled_bdt == 2300.0
    assert s.sudo().cash_payments == 2300.0  # the drawer took only the difference
    receipts = m.env["fix.ar.receipt"].search([("source_order_id", "=", order.id)])
    assert sorted(receipts.mapped("amount")) == [1150.0, 1150.0]
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.total_payable == 2300.0 and invoice.state == "paid"
    assert m.ar_of(order.customer_id) == 0.0


def test_an_unverified_field_claim_is_voided_not_refunded(books):
    m = books
    order = m.job(500.0, state="in_repair")
    order.with_context(fd_settlement_tender="bkash")._fix_record_settlement(
        575.0, "TRX-UNVERIFIED", "field_collection"
    )
    assert order.payment_settlement_state == "settled" and not order.settlement_verified
    assert not order.settlement_receipt_id  # a typed TrxID is not money yet
    order.action_cancel(reason_code="customer_declined")
    assert order.state == "cancelled" and order.payment_settlement_state == "unpaid"
    events = m.env["fix.event.outbox"].search(
        [("event_type", "=", "service_order.refund_requested"), ("aggregate_id", "=", order.id)]
    )
    assert not events


def test_a_verified_field_collection_is_booked_when_the_cashier_verifies(books):
    m = books
    order = m.job(500.0, state="in_repair")
    order.with_context(fd_settlement_tender="nagad")._fix_record_settlement(
        575.0, "TRX-NGD-1", "field_collection"
    )
    order.with_user(m.so_cashier).action_verify_settlement()
    receipt = order.settlement_receipt_id
    assert receipt.method == "nagad" and receipt.amount == 575.0
    assert m.ar_of(order.customer_id) == -575.0


def test_only_a_supervisor_cancels_a_paid_order(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(500.0)
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=575.0, reference="CTR-CAN-1", source="counter", tender="cash"
    )
    with pytest.raises(UserError, match="only a Service Supervisor"):
        order.with_user(m.so_cashier).action_cancel(reason_code="customer_declined")


def test_a_paid_diagnostic_fee_is_an_advance_the_repair_nets(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0, customer=m.customer)  # the intake creates it for its customer
    intake = m.intake(
        device_id=m.device.id,
        diagnostic_fee_bdt=300.0,
        payment_channel="bkash",
        payment_trx_ref="BKX-DIAG",
    )
    intake.sudo()._guarded().write({"service_order_id": order.id})
    receipt = intake.sudo()._fdf_raise_fee_receipt()
    assert receipt.is_order_advance and receipt.source_order_id == order
    # the customer pays the repair less what they already paid
    assert order._fix_amount_due() == 850.0
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=850.0, reference="CTR-DIAG-1", source="counter", tender="cash"
    )
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.total_payable == 1150.0 and invoice.state == "paid"
    assert m.ar_of(order.customer_id) == 0.0


def test_a_credit_customer_is_released_by_finance_within_the_limit(books):
    m = books
    order = m.job(1000.0)
    manager = m.fin_manager
    with pytest.raises(UserError, match="no credit limit"):
        order.with_user(manager).action_release_on_credit()
    m.env["fix.credit.profile"].create(
        {
            "customer_id": order.customer_id.id,
            "company_id": order.company_id.id,
            "credit_limit": 1000.0,
        }
    )
    with pytest.raises(UserError, match="left under its"):
        order.with_user(manager).action_release_on_credit()
    m.env["fix.credit.profile"].search(
        [("customer_id", "=", order.customer_id.id)]
    ).credit_limit = 5000.0
    with pytest.raises(UserError, match="Finance Manager"):
        order.with_user(m.so_cashier).action_release_on_credit()
    order.with_user(manager).action_release_on_credit()
    assert order.payment_settlement_state == "credit_approved"
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.state == "issued" and invoice.amount_residual == 1150.0
    assert m.ar_of(order.customer_id) == 1150.0


def test_d21_d22_charges_are_paid_with_the_repair_and_billed(books, monkeypatch):
    """A03 review (s3 P2): the wasted-visit fee (D21) and the pick-and-drop
    charge (D22) were recorded and reported, and never reached the amount
    due, the tax invoice or revenue. They are collected with the repair and
    billed on its invoice, VAT added by M51 on their charge codes."""
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    assert order._fix_amount_due() == 1150.0
    charges = [
        {
            "code": "CHG-TRANSPORT",
            "line_type": "transport",
            "description": "Delivery charge CN-OMB",
            "net": 100.0,
        },
        {
            "code": "CHG-CALLOUT",
            "line_type": "callout",
            "description": "Wasted visit FVX-OMB",
            "net": 200.0,
        },
    ]
    # the M02/M03 records are their own suites' (test_a02r2_field,
    # test_a02r2_release); here the order carries their two charges
    monkeypatch.setattr(type(order), "_fix_extra_charges", lambda self: [dict(c) for c in charges])
    due = order._fix_amount_due()
    assert due == 1495.0  # (1,000 + 100 + 200) + 15% VAT
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=due, reference="CTR-OMB-D22", source="counter", tender="cash"
    )
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.state == "paid" and invoice.amount_residual == 0.0
    assert invoice.total_payable == 1495.0 and invoice.vat_amount == 195.0
    by_type = {line.line_type: line for line in invoice.line_ids}
    assert set(by_type) == {"labour", "transport", "callout"}
    assert by_type["transport"].product_id.default_code == "CHG-TRANSPORT"
    assert by_type["transport"].line_total == 115.0
    assert by_type["callout"].product_id.default_code == "CHG-CALLOUT"
    assert by_type["callout"].line_total == 230.0
    assert _balance(m.env, m.rev) == -1300.0
    assert m.ar_of(order.customer_id) == 0.0


def test_a_free_repair_still_collects_and_bills_its_charges(books, monkeypatch):
    """A03 re-check of 88d85640: with a BDT 0 estimate the extras were
    skipped in the amount due, yet the invoice billed them and left AR open.
    A free (but customer-charged) repair owes its charges."""
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(0.0)
    assert order._fix_amount_due() == 0.0
    charge = {
        "code": "CHG-CALLOUT",
        "line_type": "callout",
        "description": "Wasted visit FVX-FREE",
        "net": 300.0,
    }
    monkeypatch.setattr(type(order), "_fix_extra_charges", lambda self: [dict(charge)])
    assert not order._fix_zero_charge_basis()
    due = order._fix_amount_due()
    assert due == 345.0
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=due, reference="CTR-OMB-FREE", source="counter", tender="cash"
    )
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.state == "paid" and invoice.amount_residual == 0.0
    assert invoice.total_payable == 345.0
    assert m.ar_of(order.customer_id) == 0.0
