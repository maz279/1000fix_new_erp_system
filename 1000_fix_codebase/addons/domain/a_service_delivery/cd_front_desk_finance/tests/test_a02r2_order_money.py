"""A02 pass 2: a service order's money at the counter and in the field.

X5-01 (P0): the workspace sent no tender and a counter settlement defaulted to
cash, so a bKash / card payment went into the drawer (and the GL) as cash.
M04-02 (P1): a wallet / card TrxID could pay two orders, or an order and a
diagnostic fee; a receptionist took wallet fees with no cashier.
D3 / M02-01 (P0): field cash that M01 did not record as the settlement (a part
payment) still entered the drawer with no receipt.
D1: cash on delivery is booked Dr COD clearing, never the drawer.

Non-admin users throughout (the cashiers hold no accounting role).
"""

# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
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

BILLING = "cd_billing_engine.account_code."


def _s1_has(env, field, value):
    """The interface contract's S1 side (source 'cod', state 'partial') is
    integrated by the lead; on a worktree without it these tests skip."""
    return value in dict(env["fix.service.order"]._fields[field].selection)


# ------------------------------------------------------------------ X5-01
def test_a_counter_settlement_names_its_tender(books):
    m = books
    s = m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    # what the workspace sent: no tender
    with pytest.raises(UserError, match="how the customer paid"):
        order.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=1150.0, reference="CTR-NOTENDER", source="counter"
        )
    with pytest.raises(UserError, match="how the customer paid"):
        order.with_user(m.so_cashier)._fix_record_settlement(1150.0, "CTR-NOT-2", "counter")
    order.invalidate_recordset()
    assert order.payment_settlement_state == "unpaid"
    assert s.sudo().cash_payments == 0.0
    # a card payment named as such never reaches the drawer
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="POS-SLIP-77", source="counter", tender="card"
    )
    assert order.settlement_tender == "card" and s.sudo().cash_payments == 0.0
    assert _balance(m.env, m.acc.drawer) == 0.0
    assert order.settlement_receipt_id.method == "card"


def test_cash_on_delivery_is_never_taken_at_the_counter(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)
    with pytest.raises(UserError, match="delivery leg"):
        order.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=1150.0, reference="CTR-COD", source="counter", tender="cod"
        )


# ------------------------------------------------------------------ M04-02
def test_a_wallet_trxid_pays_one_order_only(books):
    m = books
    m.shift(as_user=m.so_cashier)
    first, second = m.job(1000.0), m.job(1000.0)
    first.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="BKX-DUP-1", source="counter", tender="bkash"
    )
    with pytest.raises(UserError, match="pays once"):
        second.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=1150.0, reference="bkx-dup-1", source="counter", tender="bkash"
        )
    assert second.payment_settlement_state == "unpaid"
    # a technician's field claim with the same TrxID is refused too
    third = m.job(500.0, state="in_repair")
    with pytest.raises(UserError, match="pays once"):
        third.with_context(fd_settlement_tender="bkash")._fix_record_settlement(
            575.0, "BKX-DUP-1", "field_collection"
        )
    # an unverified claim already holding a TrxID blocks another order's use
    fourth, fifth = m.job(500.0, state="in_repair"), m.job(500.0)
    fourth.with_context(fd_settlement_tender="nagad")._fix_record_settlement(
        575.0, "NGD-CLAIM-9", "field_collection"
    )
    with pytest.raises(UserError, match="pays once"):
        fifth.with_user(m.so_cashier).action_mark_settled(
            amount_bdt=575.0, reference="NGD-CLAIM-9", source="counter", tender="nagad"
        )


def test_a_field_trxid_may_match_the_customers_own_receipt(books):
    """The legitimate path stays open: finance booked the customer's bKash
    receipt from the merchant statement first, the technician's claim names
    the same TrxID, and the verification uses that receipt."""
    m = books
    order = m.job(500.0, state="in_repair")
    receipt = (
        m.env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "customer_id": order.customer_id.id,
                "amount": 575.0,
                "method": "bkash",
                "reference": "BKX-OWN-1",
                "branch_id": order.branch_id.id,
            }
        )
    )
    receipt.action_confirm()
    order.with_context(fd_settlement_tender="bkash")._fix_record_settlement(
        575.0, "BKX-OWN-1", "field_collection"
    )
    assert order.payment_settlement_state == "settled"


def test_a_wallet_fee_trxid_is_not_reused_and_needs_a_cashier(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0, customer=m.customer)
    m.env["fix.ar.receipt"].sudo().create(
        {
            "customer_id": m.customer.id,
            "amount": 300.0,
            "method": "bkash",
            "reference": "BKX-FEE-1",
            "branch_id": m.branch.id,
        }
    ).action_confirm()
    intake = m.intake(
        device_id=m.device.id,
        diagnostic_fee_bdt=300.0,
        payment_channel="bkash",
        payment_trx_ref="BKX-FEE-1",
    )
    intake.sudo()._guarded().write({"service_order_id": order.id})
    with pytest.raises(UserError, match="pays once"):
        intake.sudo()._fdf_raise_fee_receipt()
    # a receptionist (queue agent, no cashier role) cannot take a wallet fee
    agent = (
        m.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "queue agent r2",
                "login": "a02r2.agent.%s@test" % m.acc.drawer.code,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            m.env.ref("base.group_user").id,
                            m.env.ref("cd_front_desk.group_fd_queue_agent").id,
                        ],
                    )
                ],
            }
        )
    )
    other = m.intake(
        as_user=agent,
        device_id=m.device.id,
        diagnostic_fee_bdt=200.0,
        payment_channel="nagad",
        payment_trx_ref="NGD-FEE-2",
        handover_method="signature",
        customer_signature_attachment_id=m.signature.id,
    )
    with pytest.raises(UserError, match="Front Desk Cashier"):
        other.with_user(agent).action_complete_handover()


# ------------------------------------------------------------------ D3 / M02-01
def test_field_cash_never_enters_a_drawer_without_a_receipt(books):
    m = books
    s = m.shift(as_user=m.so_cashier)
    order = m.job(1000.0, state="in_repair")
    # a part payment on site: BDT 400 of 1,150, never recorded as settlement
    s.sudo()._post_field_cash(400.0, reference="Field cash FO/TEST/1 / %s" % order.name)
    advance = m.env["fix.ar.receipt"].search(
        [("source_order_id", "=", order.id), ("is_order_advance", "=", True)]
    )
    assert advance.state == "confirmed" and advance.amount == 400.0
    assert advance.method == "cash" and advance.account_id == m.acc.drawer
    assert s.sudo().field_cash_deposited == 400.0
    assert _balance(m.env, m.acc.drawer) == 400.0
    assert m.ar_of(order.customer_id) == -400.0
    # the order stays unpaid for the rest
    assert order.payment_settlement_state == "unpaid"
    assert order._fix_amount_due() == 750.0
    # no order behind the cash: refused, nothing moves
    with pytest.raises(UserError, match="names no service order"):
        s.sudo()._post_field_cash(100.0, reference="Field cash with no order")
    assert s.sudo().field_cash_deposited == 400.0


def test_recorded_field_cash_is_booked_once(books):
    m = books
    s = m.shift(as_user=m.so_cashier)
    order = m.job(500.0, state="in_repair")
    order.with_context(fd_settlement_tender="cash")._fix_record_settlement(
        575.0, "COD/FO-T-2", "field_collection"
    )
    s.sudo()._post_field_cash(575.0, reference="Field cash FO-T-2 / %s" % order.name, order=order)
    receipts = m.env["fix.ar.receipt"].search([("source_order_id", "=", order.id)])
    assert len(receipts) == 1 and receipts.amount == 575.0 and not receipts.is_order_advance
    # the cashier's verification right after finds it booked: no second receipt
    order.with_user(m.so_cashier).action_verify_settlement()
    receipts = m.env["fix.ar.receipt"].search([("source_order_id", "=", order.id)])
    assert len(receipts) == 1 and order.settlement_verified
    assert _balance(m.env, m.acc.drawer) == 575.0


# ------------------------------------------------------------------ D1
def test_cash_on_delivery_debits_cod_clearing_never_the_drawer(books):
    m = books
    env = m.env
    s = m.shift(as_user=m.so_cashier)
    clearing = env["account.account"].create(
        {
            "code": "R2COD%s" % m.acc.drawer.code[-6:],
            "name": "COD clearing r2",
            "account_type": "asset_current",
        }
    )
    m.params.set_param("cd_cash_position.account_code.cod_clearing", clearing.code)
    m.params.set_param(BILLING + "cod_clearing", clearing.code)
    order = m.job(1000.0)
    # COD is never a field collection (interface contract: source "cod")
    with pytest.raises(UserError, match="COD settlement"):
        order.with_context(fd_settlement_tender="cod")._fix_record_settlement(
            1150.0, "COD/LEG-1", "field_collection"
        )
    if not _s1_has(env, "settlement_source", "cod"):
        pytest.skip("S1's 'cod' settlement source is not in this worktree")
    order.with_context(fd_settlement_tender="cod")._fix_record_settlement(
        1150.0, "COD/LEG-1", source="cod"
    )
    assert order.settlement_tender == "cod" and not order.settlement_verified
    receipt = env["fix.ar.receipt"].search([("source_order_id", "=", order.id)])
    assert receipt.method == "cod" and receipt.state == "confirmed"
    assert _balance(env, clearing) == 1150.0
    assert _balance(env, m.acc.drawer) == 0.0 and s.sudo().cash_payments == 0.0
    assert m.ar_of(order.customer_id) == -1150.0


def test_a_verified_part_payment_is_booked_for_the_part(books):
    """Interface contract (D3): a part payment's verification raises the M20
    receipt for the part paid; the order stays not fully paid."""
    m = books
    if not _s1_has(m.env, "payment_settlement_state", "partial"):
        pytest.skip("S1's 'partial' settlement state is not in this worktree")
    order = m.job(1000.0, state="in_repair")
    order.with_context(fd_settlement_tender="nagad")._fix_record_settlement(
        400.0, "NGD-PART-1", "field_collection"
    )
    assert order.payment_settlement_state == "partial"
    order.with_user(m.so_cashier).action_verify_settlement()
    receipt = order.settlement_receipt_id
    assert receipt.amount == 400.0 and receipt.method == "nagad"
    assert m.ar_of(order.customer_id) == -400.0
    assert order._fix_amount_outstanding() == 750.0
