"""A02 ERP pass 2, X5-09 (owner decision D25): loyalty points are earned on
the paid amount excluding VAT, never on a warranty / zero-charge job, and
are taken back when the invoice is credited or cancelled (FR-LOY-020,
BRU-LOY-05, AUT-LOY-04).

Events are delivered the way production delivers them (cron_relay as the
superuser); the member-facing reads are made by a NON-admin user.
``odoo_env`` rolls back after each test.
"""

# ruff: noqa: F811  (fixtures are imported and used as parameters)

import pytest
from odoo.addons.cd_loyalty.tests.test_a03_p2_loyalty import (  # noqa: F401
    _close,
    _lines,
    _relay,
    account,
    customer,
    env,
    make_order,
    make_user,
    program,
)
from odoo.exceptions import AccessError

from libs.py.fix_events import publish


def _invoice(env, order, taxable, vat):
    invoice = (
        env["fix.ar.invoice"]
        .sudo()
        .create(
            {
                "company_id": order.company_id.id,
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id,
                "customer_id": order.customer_id.id,
                "source_model": order._name,
                "source_id": order.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "description": "Repair %s" % order.name,
                            "taxable_amount": taxable,
                            "vat_amount": vat,
                            "line_total": taxable + vat,
                        },
                    )
                ],
            }
        )
    )
    invoice._guarded().write({"state": "issued"})
    return invoice


def _earn(env, order):
    _close(env, order)
    _relay(env)


def _credit(env, invoice, amount):
    note = (
        env["fix.credit.note"]
        .sudo()
        .create(
            {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id,
                "invoice_id": invoice.id,
                "amount": amount,
                "reason_code": "service_failure",
            }
        )
    )
    note._guarded().write({"state": "issued"})
    publish(
        env,
        "credit_note.issued",
        "fix.credit.note",
        note.id,
        {"invoice_ref": "AR/%s" % invoice.id, "invoice": invoice.name, "amount": amount},
    )
    _relay(env)
    return note


def _cancel(env, invoice):
    invoice._guarded().write({"state": "cancelled"})
    publish(env, "invoice.cancelled", "fix.ar.invoice", invoice.id, {"invoice": invoice.name})
    _relay(env)


def _balance(env, account):
    account.invalidate_recordset()
    return account.points_balance


# ------------------------------------------------------------------ earn base
def test_points_are_earned_on_the_paid_amount_excluding_vat(env, account, make_order):
    order = make_order(account.partner_id, 23000.0)  # 20,000 + 15% VAT
    _invoice(env, order, 20000.0, 3000.0)
    _earn(env, order)
    (earned,) = _lines(env, account, transaction_type="accrual")
    assert earned.points == 200  # 20,000 x 0.01, not 230
    assert earned.order_amount_bdt == 20000.0


def test_a_zero_charge_job_earns_nothing(env, account, make_order):
    order = make_order(account.partner_id, 5000.0)
    order.sudo()._guarded().write({"payment_settlement_state": "covered_zero_charge"})
    _earn(env, order)
    assert not _lines(env, account, transaction_type="accrual")
    assert _balance(env, account) == 0


# ------------------------------------------------------------------ reversal
def test_the_consumers_are_registered(env):
    rows = env["fix.event.consumer"].sudo().search([("module", "=", "cd_loyalty")])
    assert {(r.event_type, r.method) for r in rows} >= {
        ("credit_note.issued", "consume_credit_note_issued"),
        ("invoice.cancelled", "consume_invoice_cancelled"),
    }


def test_a_credit_note_takes_back_its_share_once(env, account, make_order):
    order = make_order(account.partner_id, 25000.0)
    invoice = _invoice(env, order, 25000.0, 0.0)
    _earn(env, order)
    assert _balance(env, account) == 250
    note = _credit(env, invoice, 10000.0)
    (back,) = _lines(env, account, transaction_type="clawback")
    assert (back.points, back.state, back.service_order_id) == (-100, "posted", order)
    assert _balance(env, account) == 150
    # redelivery of the same event takes nothing more
    row = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "credit_note.issued"), ("aggregate_id", "=", note.id)], limit=1
        )
    )
    env["fix.loyalty.account"].sudo().consume_credit_note_issued(row._relay_event_dict())
    assert _balance(env, account) == 150
    # the rest of the invoice credited: cumulative, never more than earned
    _credit(env, invoice, 15000.0)
    assert _balance(env, account) == 0
    assert sum(_lines(env, account, transaction_type="clawback").mapped("points")) == -250
    account.invalidate_recordset()
    assert account.lifetime_points_earned == 0 and account.lifetime_points_redeemed == 0


def test_a_cancelled_invoice_takes_back_what_is_left(env, account, make_order):
    order = make_order(account.partner_id, 25000.0)
    invoice = _invoice(env, order, 25000.0, 0.0)
    _earn(env, order)
    _credit(env, invoice, 5000.0)
    assert _balance(env, account) == 200
    _cancel(env, invoice)
    assert _balance(env, account) == 0


def test_points_already_spent_are_not_taken_twice(env, make_user, account, make_order):
    order = make_order(account.partner_id, 25000.0)
    invoice = _invoice(env, order, 25000.0, 0.0)
    _earn(env, order)
    spend = (
        env["fix.loyalty.ledger"]
        .sudo()
        .create({"account_id": account.id, "transaction_type": "redemption", "points": -200})
    )
    spend.action_post()
    assert _balance(env, account) == 50
    _cancel(env, invoice)
    assert _balance(env, account) == 0  # never negative
    receipt = (
        env["fix.loyalty.event.receipt"]
        .sudo()
        .search([("key", "like", "clawback:invoice_cancelled:%d:" % invoice.id)])
    )
    assert "200 more were due" in receipt.outcome


def test_only_the_relay_may_reverse_points(env, make_user, account, make_order):
    order = make_order(account.partner_id, 25000.0)
    invoice = _invoice(env, order, 25000.0, 0.0)
    _earn(env, order)
    clerk = make_user()
    with pytest.raises(AccessError):
        env["fix.loyalty.account"].with_user(clerk).consume_invoice_cancelled(
            {"aggregate_id": invoice.id}
        )
    assert _balance(env, account) == 250
