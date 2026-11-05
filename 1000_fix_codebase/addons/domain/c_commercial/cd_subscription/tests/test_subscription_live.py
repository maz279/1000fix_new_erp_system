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


def test_consolidated_charge_publishes_advances_and_bills_the_cycle(ctx):
    sub = _sub(ctx)
    sub.action_generate_charge()
    # Jan 31 + 30 days = Mar 2 2026 (Feb has 28 days)
    assert sub.next_invoice_date == date(2026, 3, 2)
    assert _events(ctx.env, "subscription.charged", "fix.subscription", sub.id) == [
        {"customer_id": ctx.partner.id, "amount": 3000.0, "period_days": 30}
    ]
    # A08 M53: every cycle is a charge with ONE draft invoice; the consolidated
    # flag rolls these invoices into the customer's period bill (M20)
    (charge,) = sub.charge_ids
    assert (charge.period_start, charge.period_end) == (date(2026, 1, 31), date(2026, 3, 1))
    invoice = charge.invoice_id
    assert (invoice.source_model, invoice.source_id) == ("fix.subscription.charge", charge.id)
    assert invoice.state == "draft"
    # 3,000.00 + 15% VAT (M51 determination) = 3,450.00
    assert (invoice.taxable_amount, invoice.vat_amount, invoice.total_payable) == (
        3000.0,
        450.0,
        3450.0,
    )
    assert invoice._revenue_role() == "deferred_revenue"


def test_inactive_subscription_is_not_charged(ctx):
    sub = _sub(ctx, state="paused")
    sub.action_generate_charge()
    assert sub.next_invoice_date == date(2026, 1, 31)
    assert _events(ctx.env, "subscription.charged", "fix.subscription", sub.id) == []


def test_standalone_charge_opens_its_own_invoice(ctx):
    sub = _sub(ctx, consolidated=False, billing_cycle="quarterly")
    sub.action_generate_charge()
    invoice = sub.charge_ids.invoice_id
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
    invoice = sub.charge_ids.invoice_id
    assert invoice.company_id == company_b


# --- T03 dunning ladder -----------------------------------------------------
#
# A04 hand-off closure (2026-11-05): the ladder chases the UNPAID ISSUED
# INVOICE (fix.subscription.charge._fix_overdue_unpaid), not the billing
# calendar — an unpaid invoice used to be never chased (billing rolls
# next_invoice_date forward) and a never-billed customer could be suspended.


def _billed_unpaid(ctx, sub, invoice_date, terms_days=7):
    """Bill one cycle and leave its invoice ISSUED and unpaid with `terms_days`
    terms, dated `invoice_date` (trusted staging: M20 issues it)."""
    ctx.env["fix.credit.profile"].create(
        {
            "customer_id": ctx.partner.id,
            "company_id": sub.company_id.id,
            "payment_terms_days": terms_days,
        }
    )
    sub.action_generate_charge()
    (charge,) = sub.charge_ids
    charge.invoice_id.sudo().write({"invoice_date": invoice_date, "state": "issued"})
    ctx.env.flush_all()
    ctx.env.invalidate_all()
    return charge


def _pay(ctx, charge):
    """M20 records the customer's payment: a confirmed receipt allocated to
    the cycle's invoice (residual 0, state paid)."""
    invoice = charge.invoice_id
    receipt = ctx.env["fix.ar.receipt"].create(
        {
            "customer_id": invoice.customer_id.id,
            "amount": invoice.total_payable,
            "method": "bank_transfer",
            "reference": "T03-pay-%s" % charge.id,
        }
    )
    receipt.nid_captured = "1990123456789"
    receipt.action_confirm()
    ctx.env["fix.ar.allocation"].create(
        {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": invoice.total_payable}
    )
    ctx.env.flush_all()
    ctx.env.invalidate_all()
    assert invoice.amount_residual == 0.0 and invoice.state == "paid"


@pytest.mark.parametrize(
    ("as_of", "overdue", "state", "step"),
    [
        (date(2026, 2, 10), 3, "past_due", "reminder"),
        (date(2026, 2, 14), 7, "past_due", "reminder"),  # L1 boundary
        (date(2026, 2, 15), 8, "past_due", "final"),
        (date(2026, 2, 22), 15, "past_due", "final"),  # grace boundary
        (date(2026, 2, 23), 16, "hold", "escalate"),
    ],
)
def test_dunning_ladder(ctx, as_of, overdue, state, step):
    # invoice dated Jan 31 + 7-day terms = due Feb 7; as_of Feb 10 -> 3 days
    sub = _sub(ctx, next_invoice_date=date(2026, 1, 31))
    _billed_unpaid(ctx, sub, invoice_date=date(2026, 1, 31))
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
    _billed_unpaid(ctx, sub, invoice_date=date(2026, 1, 31))
    sub.action_trigger_dunning(as_of=date(2026, 2, 18))  # 11 days > 10 grace
    assert (sub.state, sub.dunning_step) == ("hold", "escalate")


def test_unpaid_invoice_within_terms_is_not_dunned(ctx):
    sub = _sub(ctx, next_invoice_date=date(2026, 1, 31))
    _billed_unpaid(ctx, sub, invoice_date=date(2026, 1, 31))
    sub.action_trigger_dunning(as_of=date(2026, 2, 7))  # due today: not overdue
    assert (sub.state, sub.dunning_step, sub.days_overdue) == ("active", "none", 0)
    assert _events(ctx.env, "subscription.dunning_escalated", "fix.subscription", sub.id) == []


def test_never_billed_subscription_is_never_dunned(ctx):
    """A missed billing run is a Finance omission, not customer non-payment
    (A04 report M39-2: the calendar basis suspended a never-billed customer)."""
    sub = _sub(ctx, next_invoice_date=date(2026, 1, 31))
    assert not sub.charge_ids
    sub.action_trigger_dunning(as_of=date(2026, 6, 1))
    assert (sub.state, sub.dunning_step, sub.days_overdue) == ("active", "none", 0)
    assert _events(ctx.env, "subscription.dunning_escalated", "fix.subscription", sub.id) == []


def test_paid_invoice_stops_the_ladder_and_self_heals(ctx):
    """The ladder follows the invoice: once nothing issued is unpaid past due,
    a suspended subscription self-heals to active."""
    sub = _sub(ctx, next_invoice_date=date(2026, 1, 31))
    charge = _billed_unpaid(ctx, sub, invoice_date=date(2026, 1, 31))
    sub.action_trigger_dunning(as_of=date(2026, 2, 23))
    assert (sub.state, sub.dunning_step) == ("hold", "escalate")
    _pay(ctx, charge)
    sub.action_trigger_dunning(as_of=date(2026, 2, 24))
    assert (sub.state, sub.dunning_step, sub.days_overdue) == ("active", "none", 0)
    assert _events(ctx.env, "subscription.reinstated", "fix.subscription", sub.id) == [
        {"customer_id": ctx.partner.id}
    ]


@pytest.mark.parametrize("closed_state", ["cancelled", "churned"])
def test_dunning_skips_closed_subscriptions(ctx, closed_state):
    sub = _sub(ctx, state=closed_state)
    sub.action_trigger_dunning(as_of=date(2026, 6, 1))
    assert (sub.state, sub.dunning_step) == (closed_state, "none")


def test_dunning_defaults_to_today(ctx):
    sub = _sub(ctx)
    _billed_unpaid(ctx, sub, invoice_date=date.today() - timedelta(days=10))
    sub.action_trigger_dunning()  # 10 days past the 7-day terms -> 3 days overdue
    assert (sub.days_overdue, sub.dunning_step) == (3, "reminder")


def test_reinstate_clears_the_ladder(ctx):
    sub = _sub(ctx)
    charge = _billed_unpaid(ctx, sub, invoice_date=date(2026, 1, 31))
    sub.action_trigger_dunning(as_of=date(2026, 3, 1))
    assert sub.state == "hold"
    _pay(ctx, charge)  # the payment M20 records
    sub.action_reinstate()
    assert (sub.state, sub.dunning_step, sub.days_overdue) == ("active", "none", 0)
    assert _events(ctx.env, "subscription.reinstated", "fix.subscription", sub.id) == [
        {"customer_id": ctx.partner.id}
    ]


def test_reinstate_refused_while_the_invoice_is_unpaid(ctx):
    """The docstring always said 'after payment receipt' — now it is enforced
    (A04 report M39-4)."""
    from odoo.exceptions import UserError

    sub = _sub(ctx)
    _billed_unpaid(ctx, sub, invoice_date=date(2026, 1, 31))
    sub.action_trigger_dunning(as_of=date(2026, 3, 1))
    assert sub.state == "hold"
    with pytest.raises(UserError, match="unpaid past their"), ctx.env.cr.savepoint():
        sub.action_reinstate()
    assert sub.state == "hold"


def test_reinstate_refuses_a_cancelled_subscription(ctx):
    """A cancelled subscription is closed — reinstatement does not revive it
    (A04 report M39-3)."""
    from odoo.exceptions import UserError

    sub = _sub(ctx)
    sub.action_cancel()
    with pytest.raises(UserError, match="does not revive"), ctx.env.cr.savepoint():
        sub.action_reinstate()
    assert sub.state == "cancelled"


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


# --- A04 hand-off closure: refund and substrate controls (2026-11-05) -------


def _clerk(ctx):
    """A plain internal user (base.group_user only) — the attacks run as them."""
    return (
        ctx.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M39 clerk %s" % TAG,
                "login": "m39_clerk_%s" % TAG,
                "group_ids": [(6, 0, [ctx.env.ref("base.group_user").id])],
            }
        )
    )


def test_backdated_cancellation_is_refused(ctx):
    """A cancellation date before the current cycle start used to refund a
    fully-earned cycle (A04 report M39 GAP 12)."""
    from odoo.exceptions import UserError

    sub = _sub(ctx, next_invoice_date=date.today() + timedelta(days=2))  # 28/30 consumed
    clerk = _clerk(ctx)
    with pytest.raises(UserError, match="before the current cycle"), ctx.env.cr.savepoint():
        sub.with_user(clerk).action_request_refund(
            cancellation_date=date.today() - timedelta(days=200)
        )
    assert sub.state == "active"


def test_future_cancellation_date_is_refused(ctx):
    from odoo.exceptions import UserError

    sub = _sub(ctx)
    with pytest.raises(UserError, match="in the future"), ctx.env.cr.savepoint():
        sub.action_request_refund(cancellation_date=date.today() + timedelta(days=5))


def test_over_threshold_refund_needs_an_accounting_manager(ctx):
    """The BDT 25,000 manager flag is now consumed: a plain user cannot cancel
    a subscription whose refund is over the line (A04 report M39 GAP 13)."""
    from odoo.exceptions import UserError

    sub = _sub(
        ctx,
        billing_cycle="annual",
        recurring_amount=120000.0,
        next_invoice_date=date(2027, 1, 1),
    )
    clerk = _clerk(ctx)
    with pytest.raises(UserError, match="Accounting Manager authorises"), ctx.env.cr.savepoint():
        sub.with_user(clerk).action_request_refund(cancellation_date=date(2026, 1, 1))
    assert sub.state == "active"
    # the legitimate path: the Accounting Manager authorises the cancellation
    manager = (
        ctx.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M39 finmgr %s" % TAG,
                "login": "m39_finmgr_%s" % TAG,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            ctx.env.ref("base.group_user").id,
                            ctx.env.ref("account.group_account_manager").id,
                        ],
                    )
                ],
            }
        )
    )
    (res,) = sub.with_user(manager).action_request_refund(cancellation_date=date(2026, 1, 1))
    assert str(res.net_refund_payable) == "120000.00"
    assert sub.state == "cancelled" and sub.refund_requires_approval is True


def test_refund_figures_are_guarded_after_the_fact(ctx):
    """refund_requires_approval / last_refund_amount are readonly AND guarded:
    a clerk cannot clear the flag or rewrite the amount by write()."""
    from odoo.exceptions import UserError

    sub = _sub(
        ctx,
        billing_cycle="annual",
        recurring_amount=120000.0,
        next_invoice_date=date(2027, 1, 1),
    )
    (res,) = sub.action_request_refund(cancellation_date=date(2026, 1, 1))
    assert sub.refund_requires_approval is True
    clerk = _clerk(ctx)
    with pytest.raises(UserError, match="cannot be set directly"), ctx.env.cr.savepoint():
        sub.with_user(clerk).write({"refund_requires_approval": False, "last_refund_amount": 1})


def test_workflow_stamps_are_guarded(ctx):
    """state / dunning_step / days_overdue change only through the lifecycle
    (dunning ladder, reinstate, cancel) — never a direct write."""
    from odoo.exceptions import UserError

    sub = _sub(ctx)
    clerk = _clerk(ctx)
    with pytest.raises(UserError, match="cannot be set directly"), ctx.env.cr.savepoint():
        sub.with_user(clerk).write(
            {"state": "hold", "dunning_step": "escalate", "days_overdue": 40}
        )
    with pytest.raises(UserError, match="cannot be set directly"), ctx.env.cr.savepoint():
        sub.with_user(clerk).write({"state": "cancelled"})


def test_midterm_price_and_plan_change_run_through_the_proration(ctx):
    """A direct plan/price write is refused for a plain user AND for the
    Subscription Officer: the DOFA-approved proration is the only path
    (A04 report M39 GAPs 1/16)."""
    from odoo.exceptions import UserError

    sub = _sub(ctx)
    clerk = _clerk(ctx)
    officer = (
        ctx.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M39 officer %s" % TAG,
                "login": "m39_officer_%s" % TAG,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            ctx.env.ref("base.group_user").id,
                            ctx.env.ref("cd_subscription.group_subscription_officer").id,
                        ],
                    )
                ],
            }
        )
    )
    for user in (clerk, officer):
        with pytest.raises(UserError, match="approved plan change"), ctx.env.cr.savepoint():
            sub.with_user(user).write({"plan": "premium", "recurring_amount": 60000.0})
    # the legitimate path: a proration the DOFA tier approves applies it (the
    # applier runs as the superuser service under the approval — trusted
    # staging of the approved state, then the apply)
    proration = ctx.env["fix.subscription.proration"].create_for_plan_change(
        sub, 60000.0, to_plan="premium"
    )
    proration.sudo()._guarded().write({"state": "approved"})
    proration._proration_apply_to_subscription()
    sub.invalidate_recordset()
    assert (sub.recurring_amount, sub.plan) == (60000.0, "premium")


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
        # the configured contract-liability / revenue accounts actually posted
        "gl_debit_account": "212000",
        "gl_credit_account": "400000",
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
