# cd_subscription — A08 M53 IFRS 15 behaviour on the live registry
# (addons/conftest.py `odoo_env`: superuser env on fix_test, rolled back after
# every test): cycle charges billed to the contract liability, SSP price
# allocation to performance obligations, schedules per obligation, recognition
# posted Dr contract liability / Cr revenue, and the cancellation refund.
# Money expectations are hand-computed next to each assertion.
import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    partner = env["res.partner"].create({"name": f"Delta Bank Ltd {TAG}"})
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    assert ou, "fix_test ships the main company's operating unit"
    if not env.company.vat:
        env.company.vat = "1234567890123"  # a Mushak 6.3 needs the supplier BIN
    return SimpleNamespace(env=env, partner=partner, ou=ou)


def _contract(ctx, **overrides):
    vals = {
        "name": f"AMC Platinum {TAG}",
        "customer_id": ctx.partner.id,
        "operating_unit_id": ctx.ou.id,
        "recurring_amount": 3000.0,
        "billing_cycle": "monthly",
        "start_date": date(2026, 1, 1),
        "next_invoice_date": date(2026, 1, 1),
        "contract_value": 36000.0,
        "contract_end_date": date(2027, 1, 1),
    }
    vals.update(overrides)
    return ctx.env["fix.subscription"].create(vals)


def _obligation(sub, name, kind, ssp, **vals):
    return sub.env["fix.performance.obligation"].create(
        {
            "subscription_id": sub.id,
            "name": name,
            "obligation_type": kind,
            "standalone_price": ssp,
            **vals,
        }
    )


def _codes(move):
    return sorted(
        (line.account_id.with_company(move.company_id).code, line.debit, line.credit)
        for line in move.line_ids
    )


def test_allocation_by_relative_ssp_sums_exactly(ctx):
    sub = _contract(ctx, contract_value=1000.0)
    with pytest.raises(UserError, match="Add the performance obligations"), ctx.env.cr.savepoint():
        sub.action_allocate_price()
    a = _obligation(sub, "AMC visits", "amc_service", 100.0)
    b = _obligation(sub, "Workmanship warranty", "workmanship_warranty", 100.0)
    c = _obligation(sub, "Parts kit", "parts", 100.0, satisfaction="point_in_time")
    sub.action_allocate_price()
    # 1000 / 3 = 333.33 each; the 0.01 residue lands on the largest (first)
    assert [a.allocated_amount, b.allocated_amount, c.allocated_amount] == [333.34, 333.33, 333.33]
    assert {a.state, b.state, c.state} == {"allocated"}

    # no value and no term: nothing says what the price is (with a term it is
    # what the term bills, recurring x cycles: M53-13)
    zero = _contract(ctx, name=f"Zero {TAG}", contract_value=0.0, contract_end_date=False)
    _obligation(zero, "AMC", "amc_service", 10.0)
    with pytest.raises(UserError, match="transaction price"), ctx.env.cr.savepoint():
        zero.action_allocate_price()


def test_obligation_schedule_and_recognition_post_to_gl(ctx):
    sub = _contract(ctx, contract_value=36500.0)
    amc = _obligation(sub, "AMC visits", "amc_service", 36500.0)
    with pytest.raises(UserError, match="Allocate the transaction price"), ctx.env.cr.savepoint():
        amc.action_create_schedule()
    sub.action_allocate_price()
    amc.action_create_schedule()
    schedule = amc.schedule_id
    assert (schedule.source_model, schedule.source_id) == ("fix.performance.obligation", amc.id)
    assert (schedule.start_date, schedule.end_date, schedule.total_amount) == (
        date(2026, 1, 1),
        date(2027, 1, 1),
        36500.0,
    )
    assert amc.state == "scheduled"
    # a scheduled contract cannot be re-allocated (contract modification)
    with pytest.raises(UserError, match="contract modification"), ctx.env.cr.savepoint():
        sub.action_allocate_price()

    # 31 of 365 days: 36500 * 31/365 = 3100.00
    schedule.action_recognize_period(as_of=date(2026, 2, 1))
    (line,) = schedule.line_ids
    assert (line.date, line.amount) == (date(2026, 2, 1), 3100.0)
    assert _codes(line.move_id) == [("212000", 3100.0, 0.0), ("400000", 0.0, 3100.0)]
    assert (schedule.recognized_amount, schedule.deferred_balance) == (3100.0, 33400.0)
    # idempotent: the same date posts nothing more
    schedule.action_recognize_period(as_of=date(2026, 2, 1))
    assert len(schedule.line_ids) == 1


def test_recognition_refuses_without_the_account(ctx):
    sub = _contract(ctx)
    amc = _obligation(sub, "AMC", "amc_service", 1.0)
    sub.action_allocate_price()
    amc.action_create_schedule()
    param = ctx.env["ir.config_parameter"]
    key = "cd_billing_engine.account_code.deferred_revenue"
    param.set_param(key, "999999-NOPE")
    try:
        with pytest.raises(UserError, match="deferred_revenue"), ctx.env.cr.savepoint():
            amc.schedule_id.action_recognize_period(as_of=date(2026, 6, 1))
    finally:
        param.set_param(key, False)  # also clears the parameter cache
    assert amc.schedule_id.recognized_amount == 0.0 and not amc.schedule_id.line_ids


def test_point_in_time_obligation_is_recognised_on_its_date(ctx):
    sub = _contract(ctx, contract_value=500.0)
    parts = _obligation(
        sub, "Parts kit", "parts", 500.0, satisfaction="point_in_time", end_date=date(2026, 3, 15)
    )
    sub.action_allocate_price()
    parts.action_create_schedule()
    parts.schedule_id.action_recognize_period(as_of=date(2026, 3, 14))
    assert parts.schedule_id.recognized_amount == 0.0
    parts.schedule_id.action_recognize_period(as_of=date(2026, 3, 15))
    assert (parts.schedule_id.recognized_amount, parts.schedule_id.state) == (500.0, "complete")


def test_charge_invoice_is_a_contract_liability_and_unique_per_cycle(ctx):
    sub = _contract(ctx)
    sub.action_generate_charge()
    (charge,) = sub.charge_ids
    invoice = charge.invoice_id
    invoice.action_issue()
    assert invoice.state == "issued" and invoice.posted_move_id
    # Dr AR 3450 / Cr contract liability 3000 / Cr VAT 450 - no revenue at billing
    codes = {c: (d, cr) for c, d, cr in _codes(invoice.posted_move_id)}
    assert codes["212000"] == (0.0, 3000.0)
    assert "400000" not in codes
    # the same cycle cannot be charged twice
    with pytest.raises(Exception, match=r"cycle_unique|unique"), ctx.env.cr.savepoint():
        ctx.env["fix.subscription.charge"].create(
            {
                "subscription_id": sub.id,
                "operating_unit_id": ctx.ou.id,
                "period_start": charge.period_start,
                "period_end": charge.period_end,
                "amount": 1.0,
            }
        )
        ctx.env.flush_all()


def test_refund_raises_a_draft_credit_note_and_stops_recognition(ctx):
    sub = _contract(ctx, contract_value=3000.0, contract_end_date=date(2026, 1, 31))
    amc = _obligation(sub, "AMC", "amc_service", 3000.0)
    sub.action_allocate_price()
    amc.action_create_schedule()
    sub.action_generate_charge()  # cycle Jan 1 - Jan 30, next Jan 31
    invoice = sub.charge_ids.invoice_id
    invoice.action_issue()
    # cancel Jan 11: 10 of 30 days earned -> 1000.00; net refund 2000.00
    (res,) = sub.action_request_refund(cancellation_date=date(2026, 1, 11))
    assert str(res.net_refund_payable) == "2000.00"
    assert (sub.last_refund_amount, sub.last_refund_earned) == (2000.0, 1000.0)
    note = sub.refund_credit_note_id
    # 3450 gross * 2000/3000 = 2300.00, draft on M20's approval ladder
    assert (note.amount, note.state, note.reason_code, note.invoice_id) == (
        2300.0,
        "draft",
        "subscription_refund",
        invoice,
    )
    schedule = amc.schedule_id
    # recognised to Jan 11 (10 of 30 days of 3000 = 1000.00), then stopped
    assert (schedule.recognized_amount, schedule.state, schedule.cancelled_date) == (
        1000.0,
        "cancelled",
        date(2026, 1, 11),
    )
    assert amc.state == "cancelled"
    with pytest.raises(UserError, match="already cancelled"), ctx.env.cr.savepoint():
        sub.action_request_refund()
