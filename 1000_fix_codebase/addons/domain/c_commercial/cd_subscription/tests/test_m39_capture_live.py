"""M39 capture audit (2026-11-19): the records each sub-module page captures,
exercised on the live ORM and through the workspace endpoints as non-admin
users with and without the role that is the control. Rolled back.

Before this pass (HEAD 742e46bc):
  * an approved proration was never billed (nothing called _fix_mark_invoiced);
  * there was no billing schedule, charge line, usage tariff, billing run,
    credit/adjustment, pause/renew request or churn record to capture;
  * a usage reading's overage rate was typed on every reading, the same source
    record could be metered twice, and unrateable usage had no queue;
  * MRR counted a quarterly amount as monthly.
"""

from __future__ import annotations

import types
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (UserError, ValidationError, AccessError)
TAG = uuid.uuid4().hex[:6].upper()
SUB_OFFICER = "cd_subscription.group_subscription_officer"
BILLING = "account.group_account_user"
FINANCE_MANAGER = "account.group_account_manager"


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
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.today = fields.Date.context_today(env["fix.subscription"])
    x.clerk = _user(env, "m39c_clerk")
    x.officer = _user(env, "m39c_officer", SUB_OFFICER)
    x.officer2 = _user(env, "m39c_officer2", SUB_OFFICER)
    x.billing = _user(env, "m39c_billing", BILLING)
    x.billing2 = _user(env, "m39c_billing2", BILLING)
    x.fm = _user(env, "m39c_fm", BILLING, FINANCE_MANAGER)
    x.tier1 = _user(env, "m39c_tier1", "cd_entity_config.group_dofa_tier_1")
    x.customer = env["res.partner"].create({"name": "M39C %s" % TAG, "phone": "01711003955"})
    return x


def _sub(c, **kw):
    vals = {
        "name": "M39C sub %s %s" % (TAG, uuid.uuid4().hex[:4]),
        "customer_id": c.customer.id,
        "operating_unit_id": c.ou.id,
        "plan": "standard",
        "billing_cycle": "monthly",
        "recurring_amount": 30000.0,
        "start_date": c.today - timedelta(days=60),
        "next_invoice_date": c.today,
        "state": "active",
    }
    vals.update(kw)
    return c.env["fix.subscription"].create(vals)


def _bill(c, sub):
    sub.with_user(c.billing).action_generate_charge()
    return sub.charge_ids.sorted("period_start")[-1]


def _line(c, sub, **kw):
    vals = {
        "subscription_id": sub.id,
        "name": "Devices",
        "charge_type": "recurring",
        "quantity": 10,
        "unit_rate": 500.0,
        "start_date": c.today - timedelta(days=1),
    }
    vals.update(kw)
    line = c.env["fix.subscription.line"].with_user(c.officer).create(vals)
    return line


def _approved(c, line):
    line.with_user(c.billing).action_approve()
    return line


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        return types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw)
        )

    try:
        yield as_user
    finally:
        g.request, s.request = old_g, old_s


# =========================================================================== page 3
def test_charge_line_is_approved_by_another_billing_user_then_fixed(c):
    sub = _sub(c)
    with pytest.raises(REFUSED):
        c.env["fix.subscription.line"].with_user(c.clerk).create(
            {"subscription_id": sub.id, "name": "x", "quantity": 1, "unit_rate": 1}
        )
    line = _line(c, sub)
    assert line.amount == 5000.0 and line.state == "draft"
    with pytest.raises(REFUSED):
        line.with_user(c.officer).action_approve()  # not a billing user
    _approved(c, line)
    assert line.state == "active" and line.approved_by_id == c.billing
    with pytest.raises(UserError, match="fixed"):
        line.with_user(c.officer).write({"quantity": 1})
    with pytest.raises(UserError, match="fixed"):
        line.with_user(c.officer).write({"unit_rate": 1.0})


def test_line_author_cannot_approve_it(c):
    both = _user(c.env, "m39c_both", SUB_OFFICER, BILLING)
    line = (
        c.env["fix.subscription.line"]
        .with_user(both)
        .create({"subscription_id": _sub(c).id, "name": "x", "quantity": 1, "unit_rate": 10})
    )
    with pytest.raises(UserError, match="Segregation"):
        line.with_user(both).action_approve()


def test_recurring_and_one_time_lines_are_billed_on_the_cycle(c):
    sub = _sub(c)
    _approved(c, _line(c, sub))
    once = _approved(
        c, _line(c, sub, name="Setup", charge_type="one_time", quantity=1, unit_rate=2000.0)
    )
    charge = _bill(c, sub)
    assert charge.amount == 30000.0 + 5000.0 + 2000.0
    assert "Recurring line Devices" in charge.composition and "One-time Setup" in charge.composition
    once.invalidate_recordset()
    assert once.billed_charge_id == charge
    nxt = _bill(c, sub)
    assert nxt.amount == 35000.0, "a one-time line is billed once"


def test_monthly_value_normalises_the_cycle(c):
    sub = _sub(c, billing_cycle="quarterly", recurring_amount=30000.0)
    assert sub.monthly_value == 10000.0
    from odoo.addons.cd_p03_portal.controllers.a04 import m39

    assert m39.kpis(c.env)["mrr"] >= 10000.0


# =========================================================================== page 5
def test_tiered_and_volume_rating(c):
    sub = _sub(c)
    tiers = [(0, 0, {"from_qty": 0, "rate": 10.0}), (0, 0, {"from_qty": 100, "rate": 5.0})]
    tiered = _line(
        c,
        sub,
        name="Hours",
        charge_type="usage",
        metric="hours",
        included_qty=50,
        rating_model="tiered",
        tier_ids=tiers,
    )
    volume = _line(
        c,
        sub,
        name="GB",
        charge_type="usage",
        metric="gb",
        included_qty=50,
        rating_model="volume",
        tier_ids=tiers,
    )
    # 200 used, 50 included -> 150 billable
    assert tiered._rate_usage(200) == (150, 100 * 10.0 + 50 * 5.0)
    assert volume._rate_usage(200) == (150, 150 * 5.0)
    assert volume._rate_usage(120) == (70, 70 * 10.0)


def test_usage_rates_against_its_tariff_not_a_typed_rate(c):
    sub = _sub(c)
    tariff = _approved(
        c,
        _line(
            c,
            sub,
            name="Remote hours",
            charge_type="usage",
            metric="hours",
            included_qty=10,
            overage_rate=200.0,
            quantity=0,
            unit_rate=0,
        ),
    )
    U = c.env["fix.subscription.usage"].with_user(c.officer)
    u = U.create(
        {
            "subscription_id": sub.id,
            "metric": "hours",
            "quantity": 15,
            "committed": 999,
            "overage_rate": 0.0,
            "period_start": c.today - timedelta(days=5),
            "period_end": c.today,
        }
    )
    assert u.line_id == tariff, "matched to the tariff by metric"
    assert u.committed == 10 and u.overage_rate == 200.0
    assert u.overage_charge == 1000.0 and u.state == "open"


def test_a_source_record_is_metered_once(c):
    sub = _sub(c)
    U = c.env["fix.subscription.usage"].with_user(c.officer)
    vals = {
        "subscription_id": sub.id,
        "metric": "gb",
        "quantity": 5,
        "committed": 10,
        "period_start": c.today,
        "period_end": c.today,
        "source_module": "m06",
        "source_key": "VOL-1",
    }
    U.create(vals)
    with pytest.raises((IntegrityError, ValidationError)), c.env.cr.savepoint():
        U.create(dict(vals))


def test_unrateable_usage_is_queued_not_billed_then_rerated(c):
    sub = _sub(c)
    U = c.env["fix.subscription.usage"].with_user(c.officer)
    u = U.create(
        {
            "subscription_id": sub.id,
            "metric": "prints",
            "quantity": 500,
            "committed": 100,
            "period_start": c.today - timedelta(days=3),
            "period_end": c.today,
        }
    )
    assert u.state == "exception" and "No tariff" in u.exception_cause
    charge = _bill(c, sub)
    assert charge.amount == 30000.0 and u.state == "exception", "never billed, never dropped"
    with pytest.raises(UserError, match="Still not rateable"):
        u.with_user(c.officer).action_rerate()
    tariff = _approved(
        c,
        _line(
            c,
            sub,
            name="Prints",
            charge_type="usage",
            metric="prints",
            included_qty=100,
            overage_rate=2.0,
            quantity=0,
            unit_rate=0,
        ),
    )
    u.with_user(c.officer).write({"line_id": tariff.id})
    assert u.state == "open" and u.overage_charge == 800.0


# =========================================================================== page 4
def test_quantity_change_is_prorated_and_applied_to_the_line(c):
    sub = _sub(c)
    line = _approved(c, _line(c, sub))
    _bill(c, sub)
    P = c.env["fix.subscription.proration"].with_user(c.officer)
    p = P.create(
        {
            "name": "qty %s" % TAG,
            "subscription_id": sub.id,
            "change_type": "quantity",
            "line_id": line.id,
            "new_quantity": 16,
            "effective_date": c.today,
        }
    )
    assert p.old_quantity == 10 and p.new_amount == 8000.0
    assert p.amount == round(3000.0 * p.days_remaining / p.cycle_days, 2) and p.amount > 0
    approve_via_inbox(
        p, (assigned(p) & (c.billing | c.billing2 | c.fm))[:1] or c.billing2, requester=c.officer
    )
    p.invalidate_recordset()
    line.invalidate_recordset()
    assert p.state == "approved" and line.quantity == 16
    assert sub.recurring_amount == 30000.0, "a quantity change does not rewrite the base price"


def test_an_approved_proration_is_billed_on_the_next_cycle(c):
    """The defect: an approved plan change reached no bill at all."""
    sub = _sub(c)
    _bill(c, sub)
    P = c.env["fix.subscription.proration"].with_user(c.officer)
    p = P.create_for_plan_change(sub, 45000.0, to_plan="premium", effective_date=c.today)
    approve_via_inbox(
        p, (assigned(p) & (c.billing | c.billing2 | c.fm))[:1] or c.billing2, requester=c.officer
    )
    p.invalidate_recordset()
    assert p.state == "approved" and p.amount > 0
    charge = _bill(c, sub)
    p.invalidate_recordset()
    assert (
        p.billed_charge_id == charge and p.state == "invoiced" and p.invoice_id == charge.invoice_id
    )
    assert charge.amount == round(45000.0 + p.amount, 2)
    again = _bill(c, sub)
    assert again.amount == 45000.0, "billed once"


# =========================================================================== page 7
def _adjustment(c, sub, **kw):
    vals = {
        "name": "ADJ %s" % uuid.uuid4().hex[:4],
        "subscription_id": sub.id,
        "adjustment_type": "service_credit",
        "direction": "credit",
        "amount": 5000.0,
        "reason": "SLA breach on 3 jobs",
    }
    vals.update(kw)
    return c.env["fix.subscription.adjustment"].with_user(c.officer).create(vals)


def test_a_service_credit_is_approved_under_dofa_and_applied_once(c):
    sub = _sub(c)
    with pytest.raises(REFUSED):
        c.env["fix.subscription.adjustment"].with_user(c.clerk).create(
            {"name": "x", "subscription_id": sub.id, "amount": 1, "reason": "x"}
        )
    a = _adjustment(c, sub)
    assert a.dofa_tier_required == "tier_1"
    with pytest.raises(UserError):
        a.with_user(c.billing).action_dofa_approve()  # routed only
    approve_via_inbox(a, c.tier1, requester=c.officer)
    a.invalidate_recordset()
    assert a.state == "approved"
    with pytest.raises(UserError, match="fixed"):
        a.with_user(c.officer).write({"amount": 1.0})
    charge = _bill(c, sub)
    a.invalidate_recordset()
    assert charge.amount == 25000.0 and a.state == "applied" and a.applied_charge_id == charge
    assert _bill(c, sub).amount == 30000.0


def test_a_credit_larger_than_the_cycle_waits_for_the_next(c):
    sub = _sub(c, recurring_amount=3000.0)
    a = _adjustment(c, sub, amount=5000.0)
    approve_via_inbox(a, c.tier1, requester=c.officer)
    charge = _bill(c, sub)
    a.invalidate_recordset()
    assert charge.amount == 3000.0 and a.state == "approved" and not a.applied_charge_id
    assert "Carried to the next cycle" in charge.composition


def test_adjustment_author_cannot_approve_a_debit(c):
    both = _user(c.env, "m39c_both2", SUB_OFFICER, BILLING)
    sub = _sub(c)
    a = (
        c.env["fix.subscription.adjustment"]
        .with_user(both)
        .create(
            {
                "name": "DEB",
                "subscription_id": sub.id,
                "direction": "debit",
                "amount": 100.0,
                "adjustment_type": "correction",
                "reason": "under-billed",
            }
        )
    )
    a.with_user(both).action_request_approval()
    assert both not in assigned(a)


# =========================================================================== page 6
def test_billing_run_dry_run_review_commit_and_resume(c):
    sub = _sub(c)
    other = _sub(c)
    R = c.env["fix.subscription.billing.run"]
    with pytest.raises(REFUSED):
        R.with_user(c.officer).create({"as_of": c.today})
    run = R.with_user(c.billing).create({"as_of": c.today, "customer_id": c.customer.id})
    with pytest.raises(UserError, match="reviewed"):
        run.with_user(c.billing).action_commit()
    run.with_user(c.billing).action_dry_run()
    units = run.unit_ids.filtered(lambda u: u.subscription_id in (sub | other))
    assert len(units) == 2 and set(units.mapped("cause")) == {"no_contract"}
    assert not sub.charge_ids, "a dry run bills nothing"
    with pytest.raises(UserError, match="Disposition"):
        run.with_user(c.fm).action_review()
    with pytest.raises(UserError, match="dry run"):
        units[0].with_user(c.billing).write({"amount": 1.0})
    for unit in run.unit_ids:
        unit.with_user(c.billing).write(
            {
                "disposition": "skip" if unit.subscription_id == other else "bill",
                "disposition_note": "ok",
            }
        )
    with pytest.raises(REFUSED):
        run.with_user(c.billing2).action_review()  # not a Finance Manager
    run.with_user(c.fm).action_review()
    run.with_user(c.billing).action_commit()
    assert sub.charge_ids and not other.charge_ids
    assert units.filtered(lambda u: u.subscription_id == sub).state == "committed"
    run.with_user(c.billing).action_commit() if run.state == "partial" else None
    assert len(sub.charge_ids) == 1, "a committed unit is never billed again"


def test_the_dry_run_author_cannot_review_it(c):
    _sub(c)
    run = (
        c.env["fix.subscription.billing.run"]
        .with_user(c.fm)
        .create({"as_of": c.today, "customer_id": c.customer.id})
    )
    run.with_user(c.fm).action_dry_run()
    for unit in run.unit_ids:
        unit.with_user(c.fm).write({"disposition": "skip"})
    with pytest.raises(UserError, match="Segregation"):
        run.with_user(c.fm).action_review()


# =========================================================================== page 2
def test_calendar_schedule_prorates_the_first_period_and_drives_billing(c):
    sub = _sub(c, next_invoice_date=c.today)
    anchor = c.today.replace(day=1) + timedelta(days=9) if c.today.day <= 10 else c.today
    S = c.env["fix.subscription.schedule"]
    with pytest.raises(REFUSED):
        S.with_user(c.clerk).create({"subscription_id": sub.id, "anchor_date": anchor})
    sch = S.with_user(c.officer).create(
        {
            "subscription_id": sub.id,
            "alignment": "calendar",
            "timing": "advance",
            "first_period": "prorate",
            "anchor_date": anchor,
            "horizon": 3,
        }
    )
    first, second = sch.period_ids.sorted("period_start")[:2]
    assert first.partial and first.period_end.month == anchor.month
    assert first.amount_planned < 30000.0 and second.amount_planned == 30000.0
    assert second.period_start.day == 1
    with pytest.raises(UserError):
        first.with_user(c.officer).write({"amount_planned": 1})
    with pytest.raises(REFUSED):
        sch.with_user(c.officer).action_activate()  # not a billing user
    sch.with_user(c.billing).action_activate()
    assert sch.state == "active" and sub.next_invoice_date == first.billing_date
    charge = _bill(c, sub)
    assert (charge.period_start, charge.period_end) == (first.period_start, first.period_end)
    assert charge.amount == first.amount_planned and first.state == "billed"
    assert sub.next_invoice_date == second.billing_date


def test_arrears_schedule_bills_after_the_period(c):
    sub = _sub(c)
    sch = (
        c.env["fix.subscription.schedule"]
        .with_user(c.officer)
        .create(
            {
                "subscription_id": sub.id,
                "alignment": "anniversary",
                "timing": "arrears",
                "anchor_date": c.today,
                "horizon": 2,
            }
        )
    )
    p = sch.period_ids.sorted("period_start")[0]
    assert p.billing_date == p.period_end + timedelta(days=1)


# =========================================================================== page 8
def _life(c, sub, **kw):
    vals = {
        "subscription_id": sub.id,
        "action_type": "cancel",
        "reason": "Customer request",
        "effective_date": c.today,
        "notice_received_on": c.today,
    }
    vals.update(kw)
    return c.env["fix.subscription.lifecycle"].with_user(c.officer).create(vals)


def test_cancellation_validates_notice_and_needs_another_person(c):
    sub = _sub(c)
    req = _life(c, sub)
    assert req.notice_required_days == 30 and not req.notice_ok
    with pytest.raises(UserError, match="BRU-SUB-13"):
        req.with_user(c.officer).action_submit()
    ok = _life(c, sub, effective_date=c.today, notice_received_on=c.today - timedelta(days=31))
    assert ok.notice_ok
    ok.with_user(c.officer).action_submit()
    with pytest.raises(REFUSED):
        ok.with_user(c.officer2).action_approve()  # not a billing user
    ok.with_user(c.billing).action_approve()
    sub.invalidate_recordset()
    assert ok.state == "applied" and sub.state == "cancelled"


def test_a_pause_needs_a_finance_manager_and_stops_billing(c):
    sub = _sub(c)
    req = _life(c, sub, action_type="pause", pause_until=c.today + timedelta(days=30))
    req.with_user(c.officer).action_submit()
    with pytest.raises(REFUSED):
        req.with_user(c.billing).action_approve()
    req.with_user(c.fm).action_approve()
    sub.invalidate_recordset()
    assert sub.state == "paused"
    sub.with_user(c.billing).action_generate_charge()
    assert not sub.charge_ids, "BRU-SUB-12: a paused subscription is not charged"


def test_a_renewal_escalation_needs_evidenced_notice(c):
    sub = _sub(c, contract_end_date=c.today + timedelta(days=40))
    eff = c.today + timedelta(days=40)
    req = _life(
        c,
        sub,
        action_type="renew",
        effective_date=eff,
        renewal_end_date=c.today + timedelta(days=405),
        escalation_pct=10.0,
    )
    with pytest.raises(UserError, match="BRU-SUB-07"):
        req.with_user(c.officer).action_submit()
    req.with_user(c.officer).write(
        {
            "notice_sent_on": c.today - timedelta(days=1),
            "notice_channel": "email",
            "notice_evidence": "MAIL-123",
        }
    )
    assert req.notice_ok
    req.with_user(c.officer).action_submit()
    req.with_user(c.billing).action_approve()
    assert req.state == "scheduled", "takes effect on its date"
    with c.env.cr.savepoint():
        req.sudo().write({"effective_date": c.today})
    req.sudo()._apply()
    sub.invalidate_recordset()
    assert sub.contract_end_date == c.today + timedelta(days=405)
    assert req.escalation_proration_id.new_amount == 33000.0
    assert req.escalation_proration_id.state == "pending", "the price change still needs approval"


# =========================================================================== page 10
def test_churn_reason_is_recorded_once_on_a_cancelled_subscription(c):
    sub = _sub(c, billing_cycle="quarterly", recurring_amount=9000.0)
    Ch = c.env["fix.subscription.churn"].with_user(c.officer)
    with pytest.raises(UserError, match="cancelled"), c.env.cr.savepoint():
        Ch.create({"subscription_id": sub.id, "reason_code": "price"})
    sub.sudo().action_cancel()
    with pytest.raises(ValidationError, match="competitor"), c.env.cr.savepoint():
        Ch.create({"subscription_id": sub.id, "reason_code": "competitor"})
    rec = Ch.create(
        {"subscription_id": sub.id, "reason_code": "competitor", "competitor": "Rival Ltd"}
    )
    assert rec.lost_mrr == 3000.0
    with pytest.raises(ValidationError):
        Ch.create({"subscription_id": sub.id, "reason_code": "price"})
    with pytest.raises(UserError):
        rec.with_user(c.officer).write({"lost_mrr": 1.0})


# =========================================================================== endpoints
def test_workspace_saves_a_credit_and_refuses_a_forged_state(c, p03):
    sub = _sub(c)
    res = p03(c.officer).write(
        model="fix.subscription.adjustment",
        values={
            "name": "WS-ADJ",
            "subscription_id": sub.id,
            "adjustment_type": "goodwill",
            "direction": "credit",
            "amount": 100.0,
            "reason": "goodwill",
            "state": "applied",
        },
    )
    rec = c.env["fix.subscription.adjustment"].search([("name", "=", "WS-ADJ")])
    assert rec, res
    assert rec.state == "draft", "state is not writable from the form"
    res = p03(c.clerk).write(
        model="fix.subscription.lifecycle",
        values={
            "subscription_id": sub.id,
            "action_type": "pause",
            "reason": "x",
            "effective_date": str(c.today),
        },
    )
    assert res.get("error")


def test_workspace_runs_the_lifecycle_actions(c, p03):
    sub = _sub(c)
    req = _life(c, sub, notice_received_on=c.today - timedelta(days=40))
    res = p03(c.officer).action(
        model="fix.subscription.lifecycle", ids=[req.id], method="action_submit"
    )
    assert not res.get("error"), res
    res = p03(c.officer).action(
        model="fix.subscription.lifecycle", ids=[req.id], method="action_approve"
    )
    assert res.get("error") or res.get("success") is False, "the requester never approves"
    req.invalidate_recordset()
    assert req.state == "pending"


# =========================================================================== mutation gaps
def test_a_reading_on_a_tiered_tariff_is_rated_by_its_bands(c):
    """The tariff rates the reading; the flat formula (used - committed) x rate
    would give 0 here, as the tiered line carries no flat rate."""
    sub = _sub(c)
    tiers = [(0, 0, {"from_qty": 0, "rate": 10.0}), (0, 0, {"from_qty": 100, "rate": 5.0})]
    tariff = _approved(
        c,
        _line(
            c,
            sub,
            name="Hours",
            charge_type="usage",
            metric="hours",
            included_qty=50,
            rating_model="tiered",
            tier_ids=tiers,
            quantity=0,
            unit_rate=0,
        ),
    )
    u = (
        c.env["fix.subscription.usage"]
        .with_user(c.officer)
        .create(
            {
                "subscription_id": sub.id,
                "line_id": tariff.id,
                "metric": "hours",
                "quantity": 200,
                "committed": 0,
                "period_start": c.today,
                "period_end": c.today,
            }
        )
    )
    assert u.overage_quantity == 150 and u.overage_charge == 1250.0


def test_the_schedule_author_cannot_activate_it(c):
    both = _user(c.env, "m39c_both3", SUB_OFFICER, BILLING)
    sch = (
        c.env["fix.subscription.schedule"]
        .with_user(both)
        .create({"subscription_id": _sub(c).id, "anchor_date": c.today, "horizon": 2})
    )
    with pytest.raises(UserError, match="Segregation"):
        sch.with_user(both).action_activate()


def test_the_requester_cannot_approve_their_own_lifecycle_request(c):
    both = _user(c.env, "m39c_both4", SUB_OFFICER, BILLING)
    req = (
        c.env["fix.subscription.lifecycle"]
        .with_user(both)
        .create(
            {
                "subscription_id": _sub(c).id,
                "action_type": "cancel",
                "reason": "x",
                "effective_date": c.today,
                "notice_received_on": c.today - timedelta(days=40),
            }
        )
    )
    req.with_user(both).action_submit()
    with pytest.raises(UserError, match="Segregation"):
        req.with_user(both).action_approve()
