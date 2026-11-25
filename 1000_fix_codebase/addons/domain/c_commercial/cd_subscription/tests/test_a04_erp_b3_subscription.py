"""A04 ERP audit (20 Nov 2026), stream B3: M39 money and billing controls.

R3 findings (audit_analysis/evidence_a04_erp/R3_M09_M39_findings.md):
  M39-F1  revenue recognised twice (invoice deferral + contract schedule)
  M39-F2  a lifecycle cancel stopped nothing and settled nothing
  M39-F3  a refund left the invoice deferral running (200401 left in debit)
  M39-F4  autopay success never reached M20
  M39-F5  30-day roll billed 13 cycles on a 12-month term
  M39-F6  no value / no end date: billed to 200401, never recognised
  M39-F7  a future price change applied at once with 0 proration
  M39-F8  scheduled periods frozen at the old price
  M39-F9  billing without a reviewed run; billing terms writable
  M39-F12 dry run counted base + recurring lines only
  M39-F15 billing stopped at past_due; reinstatement back-billed
  M39-F19 a fabricated Mushak number
Real users, the live ORM, rolled back (``odoo_env``). Money is checked on
the posted journal lines (account code, debit, credit).
"""

import uuid
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
TAG = uuid.uuid4().hex[:6].upper()
SUB_OFFICER = "cd_subscription.group_subscription_officer"
BILLING = "account.group_account_user"
FINANCE_MANAGER = "account.group_account_manager"
DEFERRED, REVENUE = "212000", "400000"


def _user(env, login, *groups):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": "%s_%s" % (login, TAG),
                "group_ids": [(6, 0, ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    if not env.company.vat:
        env.company.vat = "1234567890123"
    params = env["ir.config_parameter"].sudo()
    for role, code in (("deferred_revenue", DEFERRED), ("revenue", REVENUE)):
        params.set_param("cd_billing_engine.account_code.%s" % role, code)
    mfs = env["account.account"].create(
        {"code": "B3MFS%s" % TAG[:4], "name": "B3 MFS clearing", "account_type": "asset_current"}
    )
    params.set_param("cd_billing_engine.account_code.channel_mfs", mfs.code)

    class C:
        pass

    x = C()
    x.env, x.ou = env, ou
    x.today = fields.Date.context_today(env["fix.subscription"])
    x.partner = env["res.partner"].create({"name": "B3 Customer %s" % TAG, "phone": "01711003955"})
    x.acct = _user(env, "b3_acct", BILLING)
    x.acct2 = _user(env, "b3_acct2", BILLING)
    x.fm = _user(env, "b3_fm", BILLING, FINANCE_MANAGER)
    x.officer = _user(env, "b3_officer", SUB_OFFICER)
    return x


def _sub(c, **kw):
    vals = {
        "name": "B3 sub %s %s" % (TAG, uuid.uuid4().hex[:4]),
        "customer_id": c.partner.id,
        "operating_unit_id": c.ou.id,
        "plan": "standard",
        "billing_cycle": "monthly",
        "recurring_amount": 3000.0,
        "start_date": date(2026, 1, 1),
        "next_invoice_date": date(2026, 1, 1),
        "state": "active",
    }
    vals.update(kw)
    return c.env["fix.subscription"].create(vals)


def _bill(sub):
    """The billing run's authority (the guard token), as the commit uses it."""
    before = sub.charge_ids
    sub._guarded().action_generate_charge()
    return sub.charge_ids - before


def _issued(charge):
    charge.invoice_id.action_issue()
    return charge.invoice_id


def _net(env, moves, code):
    lines = moves.mapped("line_ids").filtered(
        lambda line: line.account_id.with_company(env.company).code == code
    )
    return round(sum(lines.mapped("debit")) - sum(lines.mapped("credit")), 2)


def _schedules(env, sub):
    return env["fix.revenue.schedule"].search([("subscription_id", "=", sub.id)])


def _moves(env, sub):
    invoices = sub.charge_ids.mapped("invoice_id")
    notes = invoices.mapped("credit_note_ids")
    lines = _schedules(env, sub).mapped("line_ids")
    return (
        invoices.mapped("posted_move_id") | notes.mapped("posted_move_id") | lines.mapped("move_id")
    )


# ------------------------------------------------------------------ M39-F1
def test_f1_invoice_basis_refuses_a_second_contract_schedule(c):
    sub = _sub(c, contract_value=36000.0, contract_end_date=date(2026, 12, 31))
    inv = _issued(_bill(sub))
    (sched,) = _schedules(c.env, sub)
    assert (sched.source_model, sched.source_id, sched.total_amount) == (
        "fix.ar.invoice",
        inv.id,
        3000.0,
    )
    assert sub._fix_recognition_basis() == "invoice"
    with pytest.raises(UserError, match="twice"), c.env.cr.savepoint():
        sub.with_user(c.acct).action_generate_revrec_schedule()
    # January recognised = January billed, once
    sched.action_recognize_period(as_of=date(2026, 1, 31))
    assert _net(c.env, _moves(c.env, sub), REVENUE) == -3000.0
    assert _net(c.env, _moves(c.env, sub), DEFERRED) == 0.0


def test_f1_contract_basis_issues_without_an_invoice_schedule(c):
    sub = _sub(c, contract_value=36000.0, contract_end_date=date(2026, 12, 31))
    sub.with_user(c.acct).action_generate_revrec_schedule()
    assert sub._fix_recognition_basis() == "contract"
    _issued(_bill(sub))
    scheds = _schedules(c.env, sub)
    assert scheds.mapped("source_model") == ["fix.performance.obligation"]
    # a legacy invoice schedule beside the obligation never posts (held)
    inv = sub.charge_ids.invoice_id
    stray = c.env["fix.revenue.schedule"].create_from_deferral(
        "fix.ar.invoice", inv.id, "stray", 3000.0, date(2026, 1, 1), date(2026, 1, 31)
    )
    stray.write({"subscription_id": sub.id})
    stray._hold_unbased()
    assert stray.state == "held" and "one basis" in stray.hold_reason


# ------------------------------------------------------------------ M39-F6
def test_f6_an_open_ended_subscription_recognises_what_it_billed(c):
    sub = _sub(c)  # no contract value, no end date
    inv = _issued(_bill(sub))
    (sched,) = _schedules(c.env, sub)
    assert sched.state == "active" and not sched.hold_reason
    sched.action_recognize_period(as_of=date(2026, 1, 31))
    assert sched.recognized_amount == 3000.0
    assert inv.posted_move_id


# ------------------------------------------------------------------ M39-F5
def test_f5_monthly_term_bills_twelve_calendar_cycles_and_stops(c):
    sub = _sub(c, recurring_amount=1000.0, contract_end_date=date(2026, 12, 31))
    for _i in range(14):
        _bill(sub)
    charges = sub.charge_ids.sorted("period_start")
    assert len(charges) == 12
    assert (charges[0].period_start, charges[0].period_end) == (date(2026, 1, 1), date(2026, 1, 31))
    assert (charges[1].period_start, charges[1].period_end) == (date(2026, 2, 1), date(2026, 2, 28))
    assert charges[-1].period_end == date(2026, 12, 31)
    assert round(sum(charges.mapped("amount")), 2) == 12000.0


def test_f5_a_partial_last_cycle_bills_its_days(c):
    sub = _sub(
        c,
        recurring_amount=3100.0,
        start_date=date(2026, 3, 1),
        next_invoice_date=date(2026, 3, 1),
        contract_end_date=date(2026, 3, 10),
    )
    (charge,) = _bill(sub)
    assert (charge.period_end, charge.amount) == (date(2026, 3, 10), 1000.0)  # 10 of 31 days


# ------------------------------------------------------------------ M39-F3 / F14
def test_f3_refund_stops_the_invoice_deferral_and_nets_the_liability(c):
    sub = _sub(c)
    inv = _issued(_bill(sub))  # Jan 1 - Jan 31, 3000 + 450 VAT
    (res,) = sub.action_request_refund(cancellation_date=date(2026, 1, 11))
    # schedule convention: 10 of 30 days earned -> 1000.00; 2000.00 refunded
    assert (str(res.earned_revenue), str(res.net_refund_payable)) == ("1000.00", "2000.00")
    note = sub.refund_credit_note_id
    assert (note.amount, note.state, note.invoice_id) == (2300.0, "draft", inv)
    (sched,) = _schedules(c.env, sub)
    assert (sched.state, sched.recognized_amount) == ("cancelled", 1000.0)
    note.with_user(c.acct).action_submit()
    note.with_user(c.acct2).action_approve()
    note.with_user(c.acct).action_issue()
    moves = _moves(c.env, sub)
    assert _net(c.env, moves, DEFERRED) == 0.0
    assert _net(c.env, moves, REVENUE) == -1000.0
    # the run after the cycle end recognises nothing more
    c.env["fix.revenue.schedule"]._cron_recognize()
    assert _net(c.env, _moves(c.env, sub), REVENUE) == -1000.0


def test_f3_a_cancellation_fee_is_earned_not_left_deferred(c):
    sub = _sub(c)
    _issued(_bill(sub))
    (res,) = sub.action_request_refund(cancellation_date=date(2026, 1, 11), fee_pct=10.0)
    assert (str(res.cancellation_fee), str(res.net_refund_payable)) == ("200.00", "1800.00")
    note = sub.refund_credit_note_id
    note.with_user(c.acct).action_submit()
    note.with_user(c.acct2).action_approve()
    note.with_user(c.acct).action_issue()
    moves = _moves(c.env, sub)
    assert _net(c.env, moves, DEFERRED) == 0.0
    assert _net(c.env, moves, REVENUE) == -1200.0  # 1000 earned + 200 fee


# ------------------------------------------------------------------ M39-F2
def test_f2_lifecycle_cancel_settles_and_stops_both_schedule_kinds(c):
    today = c.today
    start = today - timedelta(days=5)
    sub = _sub(c, start_date=start, next_invoice_date=start)
    inv = _issued(_bill(sub))
    req = (
        c.env["fix.subscription.lifecycle"]
        .with_user(c.officer)
        .create(
            {
                "subscription_id": sub.id,
                "action_type": "cancel",
                "reason": "customer leaves",
                "effective_date": today,
                "notice_received_on": today - timedelta(days=40),
            }
        )
    )
    req.with_user(c.officer).action_submit()
    req.with_user(c.acct).action_approve()
    assert req.state == "applied" and sub.state == "cancelled"
    assert sub.refund_credit_note_id.invoice_id == inv
    assert set(_schedules(c.env, sub).mapped("state")) == {"cancelled"}
    # nothing recognises after the cancellation
    before = _net(c.env, _moves(c.env, sub), REVENUE)
    c.env["fix.revenue.schedule"]._cron_recognize()
    assert _net(c.env, _moves(c.env, sub), REVENUE) == before


def test_f2_unbilled_service_up_to_the_cancellation_is_billed(c):
    start = c.today - timedelta(days=45)
    sub = _sub(c, start_date=start, next_invoice_date=start)
    _issued(_bill(sub))  # one cycle; the next has not been billed yet
    last = sub.charge_ids.period_end
    sub.with_user(c.acct).action_cancel()
    final = sub.charge_ids.filtered(lambda ch: ch.period_start == last + timedelta(days=1))
    assert final and final.invoice_id.state == "draft"
    assert final.period_end == c.today - timedelta(days=1)
    assert 0 < final.amount < sub.recurring_amount


# ------------------------------------------------------------------ M39-F4
def test_f4_autopay_success_becomes_an_allocated_receipt_once(c):
    sub = _sub(c, start_date=c.today, next_invoice_date=c.today)
    inv = _issued(_bill(sub))
    mandate = (
        c.env["fix.subscription.autopay"]
        .sudo()
        .create({"subscription_id": sub.id, "method": "bkash", "max_amount": 10000.0})
    )
    mandate._guarded().write({"state": "active", "consent_at": fields.Datetime.now()})
    assert c.env["fix.subscription.autopay"].cron_autopay_collect() == 1
    attempt = mandate.attempt_ids
    attempt.action_record_result("success", provider_ref="BK-%s" % TAG)
    event = (
        c.env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "subscription.autopay_succeeded"),
                ("aggregate_id", "=", mandate.id),
            ],
            limit=1,
        )
    )._relay_event_dict()
    Attempt = c.env["fix.subscription.autopay.attempt"]
    out = Attempt.consume_autopay_succeeded(event)
    assert out["created"] is True
    receipt = attempt.receipt_id
    assert (receipt.state, receipt.amount, receipt.customer_id) == ("confirmed", 3450.0, c.partner)
    inv.invalidate_recordset()
    assert inv.amount_residual == 0.0
    # idempotent per attempt
    assert Attempt.consume_autopay_succeeded(event)["created"] is False
    assert len(c.env["fix.ar.receipt"].search([("reference", "=", "BK-%s" % TAG)])) == 1
    with pytest.raises(AccessError):
        Attempt.with_user(c.acct).consume_autopay_succeeded(event)


# ------------------------------------------------------------------ M39-F7
def test_f7_a_change_dated_ahead_applies_on_its_date(c):
    sub = _sub(c, start_date=c.today, next_invoice_date=c.today)
    _bill(sub)
    ahead = c.today + timedelta(days=75)
    P = c.env["fix.subscription.proration"]
    pr = P.with_user(c.officer).create_for_plan_change(sub, 4500.0, effective_date=ahead)
    approve_via_inbox(
        pr, (assigned(pr) & (c.acct | c.acct2 | c.fm))[:1] or c.acct2, requester=c.officer
    )
    pr.invalidate_recordset()
    assert pr.state == "approved" and not pr.applied_to_subscription
    assert sub.recurring_amount == 3000.0  # nothing applied before its date
    assert P.cron_apply_due_prorations() == 0
    # A04 ERP round 2 M39-F16: an increase is told to the customer first
    pr.with_user(c.officer).action_send_price_notice("email")
    assert pr.effective_date == ahead  # already beyond the 30 days' notice
    # the date comes (the notice has run): the daily job applies it
    pr.sudo()._guarded().write(
        {"effective_date": c.today, "notice_sent_at": fields.Datetime.now() - timedelta(days=31)}
    )
    assert P.cron_apply_due_prorations() == 1
    pr.invalidate_recordset()
    assert pr.applied_to_subscription and sub.recurring_amount == 4500.0
    assert pr.amount > 0 and pr.charge_id  # priced on the cycle covering its date


# ------------------------------------------------------------------ M39-F9
def test_f9_no_cycle_is_billed_outside_a_reviewed_run(c):
    sub = _sub(c, start_date=c.today, next_invoice_date=c.today)
    with pytest.raises(UserError, match="billing run"), c.env.cr.savepoint():
        sub.with_user(c.acct).action_generate_charge()
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.subscription.charge"].with_user(c.fm).create(
            {
                "subscription_id": sub.id,
                "operating_unit_id": c.ou.id,
                "period_start": c.today + timedelta(days=40),
                "period_end": c.today + timedelta(days=60),
                "amount": 1.0,
            }
        )
    for vals in (
        {"next_invoice_date": c.today + timedelta(days=365)},
        {"grace_period_days": 999},
        {"contract_end_date": c.today + timedelta(days=900)},
    ):
        with pytest.raises(UserError, match="billing terms"), c.env.cr.savepoint():
            sub.with_user(c.fm).write(vals)
    assert not sub.charge_ids


def test_f9_f12_reviewed_run_bills_what_the_dry_run_showed(c):
    sub = _sub(
        c,
        start_date=c.today,
        next_invoice_date=c.today,
        contract_id=False,
    )
    line = (
        c.env["fix.subscription.line"]
        .with_user(c.officer)
        .create(
            {
                "subscription_id": sub.id,
                "name": "Install",
                "charge_type": "one_time",
                "quantity": 1,
                "unit_rate": 5000.0,
                "start_date": c.today,
            }
        )
    )
    line.with_user(c.acct).action_approve()
    run = (
        c.env["fix.subscription.billing.run"]
        .with_user(c.acct)
        .create({"customer_id": c.partner.id})
    )
    run.with_user(c.acct).action_dry_run()
    (unit,) = run.unit_ids
    assert unit.amount == 8000.0  # 3000 base + 5000 one-time (it showed 3000)
    if unit.state == "exception":
        unit.with_user(c.fm).write({"disposition": "bill", "disposition_note": "no M08 yet"})
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        run.with_user(c.acct).action_review()  # not a Finance Manager
    run.with_user(c.fm).action_review()
    run.with_user(c.acct).action_commit()
    assert run.state == "committed"
    assert sub.charge_ids.amount == unit.amount == 8000.0


def test_f9_the_auto_billing_cron_prepares_a_run_it_does_not_bill(c):
    sub = _sub(c, start_date=c.today, next_invoice_date=c.today)
    c.env["ir.config_parameter"].sudo().set_param("cd_subscription.auto_billing", "1")
    Run = c.env["fix.subscription.billing.run"]
    Run.search(
        [("state", "in", ("draft", "dry_run", "reviewed", "partial"))]
    ).sudo()._guarded().write({"state": "void"})
    assert c.env["fix.subscription.charge"].cron_generate_due_charges() >= 1
    assert not sub.charge_ids
    run = Run.search([("state", "=", "dry_run"), ("company_id", "=", sub.company_id.id)], limit=1)
    assert sub in run.unit_ids.mapped("subscription_id")


# ------------------------------------------------------------------ M39-F8
def test_f8_a_scheduled_period_bills_at_the_price_in_force(c):
    sub = _sub(c, start_date=c.today, next_invoice_date=c.today)
    sched = (
        c.env["fix.subscription.schedule"]
        .with_user(c.officer)
        .create({"subscription_id": sub.id, "anchor_date": c.today, "horizon": 3})
    )
    sched.with_user(c.acct).action_activate()
    sub.sudo()._guarded().write({"recurring_amount": 4500.0})  # an approved change
    (charge,) = _bill(sub)
    assert charge.amount == 4500.0


# ------------------------------------------------------------------ M39-F15
def test_f15_past_due_bills_and_reinstatement_skips_the_hold(c):
    start = c.today - timedelta(days=20)
    sub = _sub(c, start_date=start, next_invoice_date=start)
    sub.sudo()._guarded().write({"state": "past_due"})
    assert _bill(sub)
    sub.sudo()._guarded().write(
        {"state": "hold", "next_invoice_date": c.today - timedelta(days=60)}
    )
    sub.with_user(c.acct).action_reinstate()
    assert sub.state == "active" and sub.next_invoice_date == c.today


# ------------------------------------------------------------------ M39-F19
def test_f19_no_fabricated_mushak_number(c):
    out = c.env["fix.subscription"].generate_consolidated_b2b_invoice(
        c.partner.id, date(2026, 1, 1), date(2026, 1, 31), [{"amount": 250.0}]
    )
    assert out["mushak_no"] is False and "mushak_ref" not in out["invoice"]


# ------------------------------------------------------------------ deployment
def test_deployment_wiring(c):
    env = c.env
    (row,) = (
        env["fix.event.consumer"]
        .sudo()
        .search([("event_type", "=", "subscription.autopay_succeeded")])
    )
    assert (row.model, row.method) == (
        "fix.subscription.autopay.attempt",
        "consume_autopay_succeeded",
    )
    cron = env.ref("cd_subscription.ir_cron_subscription_proration_due")
    assert cron.active and "cron_apply_due_prorations" in cron.code
    assert "receipt_id" in env["fix.subscription.autopay.attempt"]._fields
    assert "fraction" in env["fix.subscription.schedule.period"]._fields
