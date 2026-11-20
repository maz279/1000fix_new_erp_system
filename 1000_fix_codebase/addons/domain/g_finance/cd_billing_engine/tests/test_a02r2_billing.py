"""A02 ERP audit, pass 2 (20 Nov 2026): the service order's money in M20
(stream S1): the pinned credit release (M01-04), the refused repair billed
(D6, M01-03), one VAT source (X5-03, D23) and Dhaka GL dates (X5-10).

Driven in the counter / books world of cd_front_desk_finance (accounts, a
branch on its own OU, a Service Order Cashier and a Finance Manager)."""

# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
import datetime
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_a02_order_money_reaches_books import (  # noqa: F401
    books,
)
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import fin  # noqa: F401
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]

SUPERVISOR = "cd_service_order.group_so_supervisor"


def _supervisor(m):
    env = m.env
    vals = {
        "name": "A02R2 supervisor",
        "login": "a02r2.billing.sup.%d@test" % env["res.users"].search_count([]),
        "group_ids": [(6, 0, [env.ref("base.group_user").id, env.ref(SUPERVISOR).id])],
    }
    users = env["res.users"].with_context(no_reset_password=True)
    ous = [m.ou.id, m.ou2.id]
    if "assigned_operating_unit_ids" in users._fields:
        vals["assigned_operating_unit_ids"] = [(6, 0, ous)]
    elif "operating_unit_ids" in users._fields:
        vals["operating_unit_ids"] = [(6, 0, ous)]
    return users.create(vals)


def _credit_profile(m, order, limit=10000.0):
    m.env["fix.credit.profile"].create(
        {
            "customer_id": order.customer_id.id,
            "company_id": order.company_id.id,
            "credit_limit": limit,
        }
    )


def _new_price(m, order, price):
    """A later approved version of the order's estimate (a trusted load: the
    governing estimate is the latest approved version)."""
    old = order._fix_governing_estimate()
    return m.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "state": "approved",
            "version": (old.version or 1) + 1,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "More work",
                        "quantity": 1,
                        "unit_price": price,
                        "line_type": "labour",
                    },
                )
            ],
        }
    )


# ============================================== M01-04: pinned credit release
def test_m01_04_credit_is_honoured_only_up_to_the_released_amount(books):
    m = books
    order = m.job(1000.0)
    _credit_profile(m, order)
    order.with_user(m.fin_manager).action_release_on_credit()
    assert order.credit_released_amount == 1150.0
    assert order._fix_credit_covers(order._fix_amount_due())
    est = _new_price(m, order, 3000.0)
    assert not order._fix_credit_covers(order._fix_amount_due())
    # a delivery attempt is refused while the release covers less than is due
    with pytest.raises(UserError, match="released on credit for BDT 1150.00"):
        order.with_user(m.so_cashier)._check_delivery_settlement_gate()
    # any change to the estimate voids the stale release
    est.write({"diagnostic_notes": "price rose"})
    assert order.payment_settlement_state == "unpaid" and not order.credit_released_amount


def test_m01_04_the_released_amount_is_guarded(books):
    m = books
    order = m.job(1000.0)
    with pytest.raises(UserError, match="workflow"):
        order.with_user(m.fin_manager).write({"credit_released_amount": 99999.0})


# ======================================== D6 (M01-03): the refused repair is billed
def test_d6_refused_repair_is_billed_then_cancelled_without_refund(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(1000.0)  # ready, approved estimate
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=1150.0, reference="CTR-D6-1", source="counter"
    )
    sup = _supervisor(m)
    with pytest.raises(UserError, match="owes the approved estimate"):
        order.with_user(sup).action_cancel(reason_code="customer_declined")
    with pytest.raises(UserError, match="Supervisor"):
        order.with_user(m.so_cashier).action_bill_refused_repair()
    order.with_user(sup).action_bill_refused_repair()
    invoice = m.env["fix.ar.invoice"].search(
        [("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)]
    )
    invoice.invalidate_recordset()
    # the approved estimate in full (cd_front_desk_finance, when installed,
    # applies the counter receipt to it)
    assert invoice.total_payable == 1150.0 and invoice.state in ("issued", "paid")
    order.with_user(sup).action_cancel(reason_code="customer_declined")
    assert order.state == "cancelled"
    assert order.payment_settlement_state == "settled"  # owed, not refunded
    assert not m.env["fix.event.outbox"].search(
        [("event_type", "=", "service_order.refund_requested"), ("aggregate_id", "=", order.id)]
    )


# ============================================== X5-03 (D23): one VAT source
def test_x5_03_estimate_vat_is_m51_per_line_and_equals_the_invoice(books):
    m = books
    m.shift(as_user=m.so_cashier)
    order = m.job(333.33)
    est = order._fix_governing_estimate()
    # a header rate no longer moves the price: M51 decides per line
    total = est.grand_total
    est._guarded().write({"vat_rate": 5.0})
    est.invalidate_recordset()
    assert est.grand_total == total
    order.with_user(m.so_cashier).action_mark_settled(
        amount_bdt=order._fix_amount_due(), reference="CTR-VAT-1", source="counter"
    )
    invoice = m.deliver(order)
    invoice.invalidate_recordset()
    assert invoice.total_payable == pytest.approx(est.grand_total)
    assert order.amount_settled_bdt == pytest.approx(invoice.total_payable)
    # the billed-part exemption values a line at the invoice's own rate
    assert set(est._fix_line_vat_rates().values()) == set(invoice.line_ids.mapped("vat_rate"))


def test_x5_03_no_one_types_a_vat_rate(books):
    m = books
    order = m.job(1000.0)
    est = order._fix_governing_estimate()
    approver = (
        m.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A02R2 approver",
                "login": "a02r2.vat.approver@test",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            m.env.ref("base.group_user").id,
                            m.env.ref("cd_service_order.group_so_commercial_approver").id,
                        ],
                    )
                ],
            }
        )
    )
    draft = m.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "version": 9,
            "line_ids": [
                (
                    0,
                    0,
                    {"description": "x", "quantity": 1, "unit_price": 10.0, "line_type": "labour"},
                )
            ],
        }
    )
    with pytest.raises((UserError, ValidationError), match="M51"):
        draft.with_user(approver).write({"vat_rate": 0.0})
    assert est


# ============================================== X5-10: Dhaka GL dates
def test_x5_10_cancellation_posts_on_the_dhaka_day(books):
    m = books
    order = m.job(1000.0)
    _credit_profile(m, order)
    order.with_user(m.fin_manager).action_release_on_credit()
    invoice = m.deliver(order)
    assert invoice.posted_move_id
    late = datetime.datetime(2026, 11, 20, 20, 30)  # 02:30 on the 21st in Dhaka
    with mock.patch.object(fields.Datetime, "now", return_value=late):
        invoice.action_cancel(reason="customer disputes")
    move = m.env["account.move"].search(
        [("ref", "ilike", "CANCEL INV %s" % invoice.name)], order="id desc", limit=1
    )
    assert move and move.date == datetime.date(2026, 11, 21)
