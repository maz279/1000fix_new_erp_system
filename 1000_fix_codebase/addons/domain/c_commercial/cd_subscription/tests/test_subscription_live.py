# cd_subscription live-ORM tests — M39 subscriptions + M53 W4 revenue slice.
#
# Behavioural battery on the real registry (addons/conftest.py `odoo_env`:
# superuser env on fix_test, rolled back after every test). Expected values
# are hand-computed in the comments next to each assertion.
import json
import uuid
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError

# per-run tag / source id: unique keys never collide with a concurrent run
TAG = uuid.uuid4().hex[:6].upper()
SOURCE_ID = uuid.uuid4().int % 2_000_000_000


def _events(env, event_type, aggregate, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", aggregate_id),
        ],
        order="id",
    )
    return [json.loads(row.payload) for row in rows]


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    partner = env["res.partner"].create({"name": "Apex Financial Group Ltd."})
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    assert ou, "fix_test ships the main company's operating unit"
    return SimpleNamespace(env=env, partner=partner, ou=ou)


def _sub(ctx, **overrides):
    vals = {
        "name": "AMC Gold",
        "customer_id": ctx.partner.id,
        "operating_unit_id": ctx.ou.id,
        "recurring_amount": 3000.0,
        "next_invoice_date": date(2026, 1, 31),
    }
    vals.update(overrides)
    return ctx.env["fix.subscription"].create(vals)


def _company_with_ou(env, name, with_ou=True):
    company = env["res.company"].create({"name": f"{name} {TAG}"})
    ou = env["operating.unit"]
    if with_ou:
        ou = env["operating.unit"].create(
            {
                "name": f"{name} OU",
                "code": name[:4].upper(),
                "partner_id": company.partner_id.id,
                "company_id": company.id,
            }
        )
    return company, ou


# --- defaults, constraint, cycle ------------------------------------------


def test_defaults_are_active_standard_monthly_consolidated(ctx):
    sub = _sub(ctx)
    assert (sub.state, sub.dunning_step, sub.plan, sub.billing_cycle) == (
        "active",
        "none",
        "standard",
        "monthly",
    )
    assert sub.consolidated is True
    assert sub.grace_period_days == 15
    assert sub.currency_id == ctx.env.ref("base.BDT")


def test_negative_recurring_amount_is_refused(ctx):
    with pytest.raises(UserError, match="cannot be negative"), ctx.env.cr.savepoint():
        _sub(ctx, recurring_amount=-1.0)


def test_zero_recurring_amount_is_allowed(ctx):
    assert _sub(ctx, recurring_amount=0.0).recurring_amount == 0.0


@pytest.mark.parametrize(("cycle", "days"), [("monthly", 30), ("quarterly", 91), ("annual", 365)])
def test_cycle_days(ctx, cycle, days):
    assert _sub(ctx, billing_cycle=cycle)._cycle_days() == days


# --- AUT-025 cycle charge ---------------------------------------------------


def test_consolidated_charge_publishes_and_advances_without_standalone_invoice(ctx):
    sub = _sub(ctx)
    sub.action_generate_charge()
    # Jan 31 + 30 days = Mar 2 2026 (Feb has 28 days)
    assert sub.next_invoice_date == date(2026, 3, 2)
    assert _events(ctx.env, "subscription.charged", "fix.subscription", sub.id) == [
        {"customer_id": ctx.partner.id, "amount": 3000.0, "period_days": 30}
    ]
    invoices = ctx.env["fix.ar.invoice"].search(
        [("source_model", "=", "fix.subscription"), ("source_id", "=", sub.id)]
    )
    assert not invoices  # consolidated: rolled into the customer's ONE invoice


def test_inactive_subscription_is_not_charged(ctx):
    sub = _sub(ctx, state="paused")
    sub.action_generate_charge()
    assert sub.next_invoice_date == date(2026, 1, 31)
    assert _events(ctx.env, "subscription.charged", "fix.subscription", sub.id) == []


def test_standalone_charge_opens_its_own_invoice(ctx):
    sub = _sub(ctx, consolidated=False, billing_cycle="quarterly")
    sub.action_generate_charge()
    invoice = ctx.env["fix.ar.invoice"].search(
        [("source_model", "=", "fix.subscription"), ("source_id", "=", sub.id)]
    )
    assert len(invoice) == 1
    assert invoice.customer_id == ctx.partner
    assert invoice.operating_unit_id == ctx.ou
    assert invoice.state == "draft"
    # Jan 31 + 91 days = May 2 2026
    assert sub.next_invoice_date == date(2026, 5, 2)


def test_standalone_invoice_lands_in_the_subscriptions_company(ctx):
    """Regression: the standalone invoice used the CALLER's active company
    (env.company), not the subscription's."""
    company_b, ou_b = _company_with_ou(ctx.env, "Branch Co B")
    sub = _sub(ctx, consolidated=False, company_id=company_b.id, operating_unit_id=ou_b.id)
    assert ctx.env.company != company_b
    sub.action_generate_charge()
    invoice = ctx.env["fix.ar.invoice"].search(
        [("source_model", "=", "fix.subscription"), ("source_id", "=", sub.id)]
    )
    assert invoice.company_id == company_b


# --- T03 dunning ladder -----------------------------------------------------


@pytest.mark.parametrize(
    ("as_of", "overdue", "state", "step"),
    [
        (date(2026, 2, 5), 5, "past_due", "reminder"),
        (date(2026, 2, 7), 7, "past_due", "reminder"),  # L1 boundary
        (date(2026, 2, 8), 8, "past_due", "final"),
        (date(2026, 2, 15), 15, "past_due", "final"),  # grace boundary
        (date(2026, 2, 16), 16, "hold", "escalate"),
    ],
)
def test_dunning_ladder(ctx, as_of, overdue, state, step):
    sub = _sub(ctx, next_invoice_date=date(2026, 1, 31))
    sub.action_trigger_dunning(as_of=as_of)
    assert (sub.days_overdue, sub.state, sub.dunning_step) == (overdue, state, step)
    assert _events(ctx.env, "subscription.dunning_escalated", "fix.subscription", sub.id) == [
        {
            "customer_id": ctx.partner.id,
            "dunning_step": step,
            "days_overdue": overdue,
            "state": state,
        }
    ]


def test_dunning_respects_a_custom_grace_period(ctx):
    sub = _sub(ctx, grace_period_days=10)
    sub.action_trigger_dunning(as_of=date(2026, 2, 11))  # 11 days > 10 grace
    assert (sub.state, sub.dunning_step) == ("hold", "escalate")


def test_not_yet_due_subscription_is_untouched(ctx):
    sub = _sub(ctx)
    sub.action_trigger_dunning(as_of=date(2026, 1, 31))  # due today: not overdue
    assert (sub.state, sub.dunning_step, sub.days_overdue) == ("active", "none", 0)
    assert _events(ctx.env, "subscription.dunning_escalated", "fix.subscription", sub.id) == []


@pytest.mark.parametrize("closed_state", ["cancelled", "churned"])
def test_dunning_skips_closed_subscriptions(ctx, closed_state):
    sub = _sub(ctx, state=closed_state)
    sub.action_trigger_dunning(as_of=date(2026, 6, 1))
    assert (sub.state, sub.dunning_step) == (closed_state, "none")


def test_dunning_defaults_to_today(ctx):
    sub = _sub(ctx, next_invoice_date=date.today() - timedelta(days=3))
    sub.action_trigger_dunning()
    assert (sub.days_overdue, sub.dunning_step) == (3, "reminder")


def test_reinstate_clears_the_ladder(ctx):
    sub = _sub(ctx)
    sub.action_trigger_dunning(as_of=date(2026, 3, 1))
    assert sub.state == "hold"
    sub.action_reinstate()
    assert (sub.state, sub.dunning_step, sub.days_overdue) == ("active", "none", 0)
    assert _events(ctx.env, "subscription.reinstated", "fix.subscription", sub.id) == [
        {"customer_id": ctx.partner.id}
    ]


def test_cancel_publishes(ctx):
    sub = _sub(ctx)
    sub.action_cancel()
    assert sub.state == "cancelled"
    assert _events(ctx.env, "subscription.cancelled", "fix.subscription", sub.id) == [{}]


# --- prorated refund --------------------------------------------------------


def test_mid_cycle_refund_prorates_and_charges_fee(ctx):
    # monthly: cycle = [Jan 1, Jan 31) = 30 days; cancel Jan 11 -> 10 days
    # earned = 3000 * 10/30 = 1000.00, unearned 2000.00, fee 10% = 200.00
    sub = _sub(ctx)
    (res,) = sub.action_request_refund(cancellation_date=date(2026, 1, 11), fee_pct=10.0)
    assert str(res.earned_revenue) == "1000.00"
    assert str(res.unearned_refund) == "2000.00"
    assert str(res.cancellation_fee) == "200.00"
    assert str(res.net_refund_payable) == "1800.00"
    assert res.requires_manager_approval is False
    assert sub.state == "cancelled"
    assert _events(ctx.env, "subscription.refund_requested", "fix.subscription", sub.id) == [
        {
            "customer_id": ctx.partner.id,
            "net_refund": 1800.0,
            "earned_revenue": 1000.0,
            "unearned_refund": 2000.0,
            "requires_manager_approval": False,
        }
    ]


def test_refund_defaults_to_today_without_fee(ctx):
    # cycle start = (today + 10) - 30 = today - 20 -> 20 of 30 days earned
    # earned = 3000 * 20/30 = 2000.00, net refund = 1000.00
    sub = _sub(ctx, next_invoice_date=date.today() + timedelta(days=10))
    (res,) = sub.action_request_refund()
    assert str(res.earned_revenue) == "2000.00"
    assert str(res.net_refund_payable) == "1000.00"


def test_large_refund_needs_manager_approval(ctx):
    # annual 120,000 cancelled on day 0 of the cycle -> all unearned
    sub = _sub(
        ctx,
        billing_cycle="annual",
        recurring_amount=120000.0,
        next_invoice_date=date(2027, 1, 1),
    )
    (res,) = sub.action_request_refund(cancellation_date=date(2026, 1, 1))
    assert str(res.net_refund_payable) == "120000.00"
    assert res.requires_manager_approval is True


# --- T02 consolidated B2B invoice -------------------------------------------


def test_consolidated_invoice_totals_lines_and_mushak(ctx):
    device_lines = [
        {"amount": 250.00},
        {
            "amount": 1999.99,
            "description": "POS Terminal #2",
            "device_id": 7,
            "serial_number": "SN-POS-00002",
            "branch_name": "Chittagong-Hub",
        },
        {},  # every key defaulted: 250.00 at Head Office
    ]
    out = ctx.env["fix.subscription"].generate_consolidated_b2b_invoice(
        ctx.partner.id, date(2026, 1, 1), date(2026, 1, 31), device_lines
    )
    # taxable 250 + 1999.99 + 250 = 2499.99
    # VAT 37.50 + 300.00 (299.9985 half-up) + 37.50 = 375.00
    assert out["total_taxable"] == 2499.99
    assert out["total_vat"] == 375.0
    assert out["total_payable"] == 2874.99
    assert out["line_count"] == out["device_count"] == 3
    mushak = f"2026-C{ctx.partner.id:04d}-0003"
    assert out["mushak_no"] == mushak
    assert out["lines"][0] == {
        "description": "Device Maintenance & Support",
        "device_id": None,
        "serial_number": "",
        "branch_name": "Head Office",
        "taxable_amount": 250.0,
        "vat_amount": 37.5,
        "line_total": 287.5,
    }
    assert out["lines"][1]["vat_amount"] == 300.0
    assert out["lines"][1]["line_total"] == 2299.99
    assert out["lines"][1]["branch_name"] == "Chittagong-Hub"
    assert out["invoice"] == {
        "company_id": ctx.env.company.id,
        "customer_id": ctx.partner.id,
        "operating_unit_id": ctx.ou.id,
        "source_model": "fix.subscription.consolidated",
        "source_id": ctx.partner.id,
        "invoice_date": date(2026, 1, 31),
        "taxable_amount": 2499.99,
        "vat_amount": 375.0,
        "total_payable": 2874.99,
        "state": "issued",
        "mushak_ref": mushak,
    }
    assert _events(
        ctx.env, "invoice.consolidated_b2b_created", "fix.ar.invoice", ctx.partner.id
    ) == [
        {
            "customer_id": ctx.partner.id,
            "customer_name": "Apex Financial Group Ltd.",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "total_payable": 2874.99,
            "taxable_amount": 2499.99,
            "vat_amount": 375.0,
            "device_count": 3,
            "mushak_no": mushak,
        }
    ]


def test_400_device_client_gets_one_invoice(ctx):
    lines = [{"amount": 250.00, "device_id": 1000 + i} for i in range(1, 401)]
    out = ctx.env["fix.subscription"].generate_consolidated_b2b_invoice(
        ctx.partner.id, date(2026, 3, 1), date(2026, 3, 31), lines
    )
    # 400 * 250 = 100,000 taxable; 15% = 15,000 VAT
    assert (out["total_taxable"], out["total_vat"], out["total_payable"]) == (
        100000.0,
        15000.0,
        115000.0,
    )
    assert out["mushak_no"].endswith("-0400")


def test_consolidated_invoice_without_devices_is_empty(ctx):
    out = ctx.env["fix.subscription"].generate_consolidated_b2b_invoice(
        ctx.partner.id, date(2026, 1, 1), date(2026, 1, 31)
    )
    assert (out["total_payable"], out["line_count"], out["lines"]) == (0.0, 0, [])
    assert out["mushak_no"] == f"2026-C{ctx.partner.id:04d}-0000"


def test_consolidated_invoice_carries_the_active_company(ctx):
    """Regression (R01-AUDIT): invoice_vals carried no company_id and its
    operating unit was any company's first OU."""
    company_b, ou_b = _company_with_ou(ctx.env, "Corp Co B")
    env_b = ctx.env(context=dict(ctx.env.context, allowed_company_ids=[company_b.id]))
    out = env_b["fix.subscription"].generate_consolidated_b2b_invoice(
        ctx.partner.id, date(2026, 1, 1), date(2026, 1, 31), [{"amount": 100}]
    )
    assert out["invoice"]["company_id"] == company_b.id
    assert out["invoice"]["operating_unit_id"] == ou_b.id


def test_consolidated_invoice_never_borrows_another_companys_unit(ctx):
    """Regression: a company without an operating unit used to get the
    hard-coded record id 1 (another company's OU)."""
    company_c, _ = _company_with_ou(ctx.env, "No OU Co", with_ou=False)
    env_c = ctx.env(context=dict(ctx.env.context, allowed_company_ids=[company_c.id]))
    out = env_c["fix.subscription"].generate_consolidated_b2b_invoice(
        ctx.partner.id, date(2026, 1, 1), date(2026, 1, 31)
    )
    assert out["invoice"]["company_id"] == company_c.id
    assert out["invoice"]["operating_unit_id"] is False


# --- T04 revenue recognition schedule ---------------------------------------


def _schedule(ctx, **overrides):
    vals = {
        "operating_unit_id": ctx.ou.id,
        "source_model": "fix.contract",
        "source_id": SOURCE_ID,
        "description": "AMC Gold 2026",
        "total_amount": 3650.0,
        "start_date": date(2026, 1, 1),
        "end_date": date(2027, 1, 1),  # 365-day term
    }
    vals.update(overrides)
    return ctx.env["fix.revenue.schedule"].create(vals)


def test_schedule_term_must_be_positive(ctx):
    with pytest.raises(UserError, match="term must be positive"), ctx.env.cr.savepoint():
        _schedule(ctx, end_date=date(2026, 1, 1))


def test_schedule_amount_must_be_positive(ctx):
    with pytest.raises(UserError, match="deferred amount must be positive"), ctx.env.cr.savepoint():
        _schedule(ctx, total_amount=0.0)


def test_create_from_deferral_inherits_the_source_unit_and_company(ctx):
    """Regression: create_from_deferral never set the REQUIRED
    operating_unit_id, so every call failed."""
    sub = _sub(ctx)
    schedule = ctx.env["fix.revenue.schedule"].create_from_deferral(
        "fix.subscription", sub.id, "AMC Gold FY26", 1200.0, date(2026, 1, 1), date(2026, 12, 31)
    )
    assert schedule.operating_unit_id == ctx.ou
    assert schedule.company_id == sub.company_id
    assert (schedule.source_model, schedule.source_id) == ("fix.subscription", sub.id)
    assert (schedule.total_amount, schedule.recognized_amount, schedule.state) == (
        1200.0,
        0.0,
        "active",
    )


def test_create_from_deferral_accepts_an_explicit_unit(ctx):
    ou_b = ctx.env["operating.unit"].create(
        {
            "name": f"Ctg Unit {TAG}",
            "code": f"CTG{TAG}",
            "partner_id": ctx.env.company.partner_id.id,
            "company_id": ctx.env.company.id,
        }
    )
    sub = _sub(ctx)
    schedule = ctx.env["fix.revenue.schedule"].create_from_deferral(
        "fix.subscription",
        sub.id,
        "AMC",
        500.0,
        date(2026, 1, 1),
        date(2026, 6, 30),
        operating_unit_id=ou_b.id,
    )
    assert schedule.operating_unit_id == ou_b


def test_one_schedule_per_source(ctx):
    _schedule(ctx)
    with pytest.raises(Exception, match=r"source_schedule_unique|unique"), ctx.env.cr.savepoint():
        _schedule(ctx)
        ctx.env.flush_all()


def test_recognition_straight_line_cumulative_and_completes(ctx):
    schedule = _schedule(ctx)
    # before the term: nothing
    schedule.action_recognize_period(as_of=date(2025, 12, 31))
    assert schedule.recognized_amount == 0.0
    # 10 of 365 days: 3650 * 10/365 = 100.00
    schedule.action_recognize_period(as_of=date(2026, 1, 11))
    assert (schedule.recognized_amount, schedule.state) == (100.0, "active")
    # idempotent: same as_of recognizes nothing new
    schedule.action_recognize_period(as_of=date(2026, 1, 11))
    # past the end: the remaining 3550.00, schedule complete
    schedule.action_recognize_period(as_of=date(2027, 3, 1))
    assert (schedule.recognized_amount, schedule.state) == (3650.0, "complete")
    # a complete schedule is skipped
    schedule.action_recognize_period(as_of=date(2027, 6, 1))
    events = _events(ctx.env, "revenue.recognized", "fix.revenue.schedule", schedule.id)
    common = {
        "source_model": "fix.contract",
        "source_id": SOURCE_ID,
        "gl_debit_account": "210200",
        "gl_credit_account": "410100",
    }
    assert events == [
        {"amount": 100.0, "cumulative": 100.0, **common},
        {"amount": 3550.0, "cumulative": 3650.0, **common},
    ]


def test_recognition_defaults_to_today(ctx):
    schedule = _schedule(
        ctx,
        start_date=date.today() - timedelta(days=10),
        end_date=date.today() + timedelta(days=355),
    )
    schedule.action_recognize_period()
    assert schedule.recognized_amount == 100.0  # 10/365 of 3650


def test_cancelled_schedule_recognizes_nothing(ctx):
    schedule = _schedule(ctx, state="cancelled")
    schedule.action_recognize_period(as_of=date(2026, 6, 1))
    assert schedule.recognized_amount == 0.0
    assert _events(ctx.env, "revenue.recognized", "fix.revenue.schedule", schedule.id) == []
