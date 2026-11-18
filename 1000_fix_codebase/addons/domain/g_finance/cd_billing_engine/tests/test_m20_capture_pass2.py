# M20 second capture pass (19 Nov 2026): the records the spec says a person
# captures on the sub-module pages (fix_ar_capture.py), run against the
# rolled-back test database as non-admin users holding the real finance
# roles. Each test states the rule it holds and the refusal that proves it.
#   acct / acct2 : Accountant        mgr / mgr2 : Accounting Administrator
#   billing      : billing clerk     plain      : internal user, no finance role
from datetime import date, timedelta

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a08_m20_controls as _controls
from .test_a08_m20_controls import as_, inv, rcpt
from .test_ar_engine_orm import JOB, _closed_order, _gl_company

REFUSED = (UserError, ValidationError, AccessError)
# the control suite's fixtures, registered here under their own names
c_raw = _controls.c_raw
c = _controls.c
p03 = _controls.p03
TODAY = date.today()


def overdue(c, days=40, **kw):
    """An issued invoice (11,500) whose net-30 due date is `days` - 30 ago."""
    return inv(c, when=TODAY - timedelta(days=days), **kw)


def run_for(c, invoice):
    return c.env["fix.dunning"].search([("invoice_id", "=", invoice.id)])


def policy(c, user=None, **vals):
    base = {
        "name": "Ladder %s" % c.tag,
        "company_id": c.company.id,
        "segment": "all",
        "first_offset_days": 1,
        "l2_days": 7,
        "l3_days": 14,
    }
    base.update(vals)
    return as_(c, user or c.mgr)["fix.ar.dunning.policy"].create(base)


# ================================================================ p8 ladder
def test_ladder_is_activated_by_a_second_administrator_and_then_frozen(c):
    pol = policy(c)
    with pytest.raises(REFUSED):
        pol.with_user(c.mgr).action_activate()  # its author
    with pytest.raises(REFUSED):
        pol.with_user(c.acct).action_activate()  # not an administrator
    with pytest.raises(REFUSED):
        pol.with_user(c.mgr).write({"state": "active"})
    pol.with_user(c.mgr2).action_activate()
    assert pol.state == "active" and pol.activated_by_id == c.mgr2
    with pytest.raises(REFUSED):
        pol.with_user(c.mgr).write({"l2_days": 3})
    # a second segment ladder for the same segment is refused until the first retires
    other = policy(c, name="Second %s" % c.tag)
    with pytest.raises(REFUSED):
        other.with_user(c.mgr2).action_activate()
    pol.with_user(c.mgr2).action_retire(reason="replaced")
    other.with_user(c.mgr2).action_activate()


def test_dunning_run_follows_the_ladder_in_force(c):
    pol = policy(c, first_offset_days=20, l2_days=2, l2_channel="sms")
    pol.with_user(c.mgr2).action_activate()
    young = overdue(c, days=40)  # 10 days past due: before L1 at 20
    old = overdue(c, days=60)  # 30 days past due
    c.env["fix.dunning"].action_run_dunning()
    assert not run_for(c, young), "L1 went out before the ladder's offset"
    run = run_for(c, old)
    assert run.step == "reminder" and run.policy_id == pol and run.channel == pol.l1_channel
    run._guarded().write({"step_date": TODAY - timedelta(days=3)})
    c.env["fix.dunning"].action_run_dunning()
    assert run.step == "final", "the ladder's 2-day grace was not used"
    assert run.channel == "sms"


def test_named_account_ladder_wins_over_the_segment(c):
    seg = policy(c, name="All %s" % c.tag)
    seg.with_user(c.mgr2).action_activate()
    named = policy(c, name="Named %s" % c.tag, customer_ids=[(6, 0, c.customer.ids)])
    named.with_user(c.mgr2).action_activate()
    i = overdue(c)
    assert c.env["fix.ar.dunning.policy"]._fix_policy_for(i) == named
    i2 = as_(c, c.acct)["fix.ar.invoice"].create_manual_invoice(
        {"customer_id": c.customer2.id, "operating_unit_id": c.ou.id, "company_id": c.company.id},
        [{"description": "Job", "taxable_amount": 1000.0}],
        reason_code="pass2",
    )
    assert c.env["fix.ar.dunning.policy"]._fix_policy_for(i2) == seg


# ============================================================== p8 promises
def test_promise_holds_dunning_and_a_broken_one_escalates(c):
    i = overdue(c, days=60)
    c.env["fix.dunning"].action_run_dunning()
    run = run_for(c, i)
    assert run and not run.suppressed
    Promise = as_(c, c.acct)["fix.ar.promise"]
    for bad in (
        {"amount": 99999.0, "promised_date": TODAY + timedelta(days=3)},
        {"amount": 1000.0, "promised_date": TODAY - timedelta(days=1)},
        {"amount": 1000.0, "promised_date": TODAY + timedelta(days=90)},
    ):
        with pytest.raises(REFUSED):
            Promise.create(dict({"invoice_id": i.id, "made_by": "Mr Karim"}, **bad))
    with pytest.raises(REFUSED):
        as_(c, c.plain)["fix.ar.promise"].create(
            {"invoice_id": i.id, "amount": 1000.0, "promised_date": TODAY, "made_by": "x"}
        )
    p = Promise.create(
        {
            "invoice_id": i.id,
            "amount": 5000.0,
            "promised_date": TODAY + timedelta(days=5),
            "made_by": "Mr Karim",
        }
    )
    assert p.recorded_by == c.acct and p.residual_at_promise == pytest.approx(11500.0)
    assert run.suppressed and run.suppression_reason == "promise"
    assert run.suppressed_until == p.promised_date and run.suppressed_by_id == c.acct
    with pytest.raises(REFUSED):
        Promise.create({"invoice_id": i.id, "amount": 10.0, "promised_date": TODAY, "made_by": "y"})
    with pytest.raises(REFUSED):
        p.with_user(c.acct).write({"state": "kept"})
    # the run keeps the hold while the promise stands
    c.env["fix.dunning"].action_run_dunning()
    assert run.suppressed
    # the date passes with nothing paid: broken, dunning resumes, case escalates
    res = c.env["fix.ar.promise"]._cron_check_promises(as_of=TODAY + timedelta(days=6))
    assert res["broken"] >= 1 and p.state == "broken" and p.broken_at
    assert not run.suppressed
    case = c.env["fix.ar.collection.case"].search(
        [("customer_id", "=", c.customer.id), ("state", "!=", "closed")]
    )
    assert case and case.broken_promises == 1 and p.case_id == case
    assert case.priority_score >= 50


def test_promise_is_kept_when_the_money_arrives(c):
    i = overdue(c, days=60)
    p = as_(c, c.acct)["fix.ar.promise"].create(
        {
            "invoice_id": i.id,
            "amount": 5000.0,
            "promised_date": TODAY + timedelta(days=5),
            "made_by": "Ms Rina",
        }
    )
    r = rcpt(c, c.acct, 5000.0)
    c.env["fix.ar.allocation"].create({"receipt_id": r.id, "invoice_id": i.id, "amount": 5000.0})
    c.env["fix.ar.promise"]._cron_check_promises()
    assert p.state == "kept"


def test_promise_holds_a_first_reminder(c):
    i = overdue(c, days=60)
    as_(c, c.acct)["fix.ar.promise"].create(
        {
            "invoice_id": i.id,
            "amount": 1000.0,
            "promised_date": TODAY + timedelta(days=2),
            "made_by": "z",
        }
    )
    c.env["fix.dunning"].action_run_dunning()
    assert not run_for(c, i), "a reminder went out on a promised invoice"


# ========================================================= p8 payment plans
def _plan(c, invoices, amounts, user=None, first=10):
    return as_(c, user or c.acct)["fix.ar.payment.plan"].create(
        {
            "customer_id": c.customer.id,
            "company_id": c.company.id,
            "invoice_ids": [(6, 0, invoices.ids)],
            "reason": "cash flow",
            "line_ids": [
                (0, 0, {"due_date": TODAY + timedelta(days=first + 30 * n), "amount": a})
                for n, a in enumerate(amounts)
            ],
        }
    )


def test_payment_plan_is_agreed_by_a_second_person_and_adds_up(c):
    i = overdue(c, days=60)
    c.env["fix.dunning"].action_run_dunning()
    short = _plan(c, i, [5000.0, 5000.0])
    with pytest.raises(REFUSED):
        short.with_user(c.acct2).action_activate()  # 10,000 against 11,500 open
    plan = _plan(c, i, [5750.0, 5750.0])
    with pytest.raises(REFUSED):
        plan.with_user(c.acct).action_activate()  # its proposer
    with pytest.raises(REFUSED):
        plan.with_user(c.acct).write({"state": "active"})
    plan.with_user(c.acct2).action_activate()
    assert plan.state == "active" and plan.total_amount == pytest.approx(11500.0)
    run = run_for(c, i)
    assert (
        run.suppressed
        and run.suppression_reason == "payment_plan"
        and run.suppressed_by_id == c.acct2
    )
    with pytest.raises(REFUSED):
        plan.line_ids[:1].with_user(c.acct).write({"amount": 1.0})
    c.env["fix.dunning"].action_run_dunning()
    assert run.suppressed


def test_missed_instalment_defaults_the_plan(c):
    i = overdue(c, days=60)
    c.env["fix.dunning"].action_run_dunning()
    plan = _plan(c, i, [5750.0, 5750.0], first=1)
    plan.with_user(c.acct2).action_activate()
    res = c.env["fix.ar.payment.plan"]._cron_check_plans(as_of=TODAY + timedelta(days=5))
    assert res["defaulted"] == 1 and plan.state == "defaulted" and plan.missed_count == 1
    assert not run_for(c, i).suppressed
    case = c.env["fix.ar.collection.case"].search([("customer_id", "=", c.customer.id)])
    assert case.origin == "plan_default"


def test_paid_instalment_is_not_missed(c):
    i = overdue(c, days=60)
    plan = _plan(c, i, [5750.0, 5750.0], first=1)
    plan.with_user(c.acct2).action_activate()
    r = rcpt(c, c.acct, 5750.0)
    c.env["fix.ar.allocation"].create({"receipt_id": r.id, "invoice_id": i.id, "amount": 5750.0})
    res = c.env["fix.ar.payment.plan"]._cron_check_plans(as_of=TODAY + timedelta(days=5))
    assert res["defaulted"] == 0 and plan.state == "active"


# ======================================================= p8 collection case
def test_escalated_run_opens_one_case_per_customer(c):
    i = overdue(c, days=90)
    c.env["fix.dunning"].action_run_dunning()
    run = run_for(c, i)
    run._guarded().write({"step": "escalate"})
    res = c.env["fix.dunning"].action_run_dunning()
    assert res["cases_opened"] == 1
    case = c.env["fix.ar.collection.case"].search([("customer_id", "=", c.customer.id)])
    assert case.origin == "dunning_escalation" and case.total_overdue == pytest.approx(11500.0)
    c.env["fix.dunning"].action_run_dunning()
    assert c.env["fix.ar.collection.case"].search_count([("customer_id", "=", c.customer.id)]) == 1
    with pytest.raises(REFUSED):
        as_(c, c.acct)["fix.ar.collection.case"].create(
            {"customer_id": c.customer.id, "company_id": c.company.id}
        )
    with pytest.raises(REFUSED):
        case.with_user(c.acct).write({"priority_score": 1})
    case.with_user(c.acct).action_log_contact(note="will pay Friday", next_action=str(TODAY))
    assert case.state == "in_progress" and case.last_contact_note == "will pay Friday"
    with pytest.raises(REFUSED):
        case.with_user(c.acct).action_close_paid(note="paid")  # 11,500 still overdue
    with pytest.raises(REFUSED):
        case.with_user(c.acct).action_close_promise(note="x")  # no promise recorded
    case.with_user(c.acct).action_close_legal(note="lawyer letter")
    assert case.state == "closed" and case.outcome == "legal" and case.closed_by == c.acct
    with pytest.raises(REFUSED):
        case.with_user(c.acct).write({"next_action_at": TODAY})


def test_collector_opens_a_case_by_hand(c):
    overdue(c, days=70)
    case = as_(c, c.acct)["fix.ar.collection.case"].create(
        {"customer_id": c.customer.id, "company_id": c.company.id, "note": "big account"}
    )
    assert case.name.startswith("COL") and case.origin == "manual"
    assert case.overdue_count == 1 and case.oldest_age == 40


# ============================================================ p4 delivery
def test_invoice_delivery_is_one_record_per_channel_with_retries(c):
    draft = inv(c, issue=False)
    Delivery = as_(c, c.billing)["fix.ar.invoice.delivery"]
    with pytest.raises(REFUSED):
        Delivery.create({"invoice_id": draft.id, "channel": "email", "recipient": "a@b.co"})
    i = inv(c)
    with pytest.raises(REFUSED):
        Delivery.create({"invoice_id": i.id, "channel": "email", "recipient": "not-an-email"})
    with pytest.raises(REFUSED):
        Delivery.create({"invoice_id": i.id, "channel": "sms", "recipient": "123"})
    with pytest.raises(REFUSED):
        as_(c, c.plain)["fix.ar.invoice.delivery"].create(
            {"invoice_id": i.id, "channel": "email", "recipient": "a@b.co"}
        )
    link = as_(c, c.acct)["fix.ar.payment.link"].create({"invoice_id": i.id})
    d = Delivery.create({"invoice_id": i.id, "channel": "email", "recipient": "buyer@corp.com.bd"})
    assert d.status == "queued" and d.payment_link_id == link
    with pytest.raises(REFUSED):
        Delivery.create({"invoice_id": i.id, "channel": "email", "recipient": "x@y.com"})
    with pytest.raises(REFUSED):
        d.with_user(c.billing).write({"status": "delivered"})
    with pytest.raises(REFUSED):
        d.with_user(c.billing).action_mark_delivered()  # not sent yet
    d.with_user(c.billing).action_mark_sent()
    d.with_user(c.billing).action_mark_failed(reason="mailbox full")
    assert d.status == "failed" and d.failure_reason == "mailbox full"
    for _n in range(3):
        d.with_user(c.billing).action_retry()
        d.with_user(c.billing).action_mark_failed(reason="bounced")
    assert d.retry_count == 3
    with pytest.raises(REFUSED):
        d.with_user(c.billing).action_retry()  # past the retries: another channel
    w = Delivery.create({"invoice_id": i.id, "channel": "whatsapp", "recipient": "+8801711000000"})
    w.with_user(c.billing).action_mark_sent()
    w.with_user(c.billing).action_mark_delivered()
    w.with_user(c.billing).action_mark_opened()
    assert w.status == "opened" and w.delivered_at and w.opened_at
    assert c.env["fix.ar.payment.link"].search_count([("invoice_id", "=", i.id)]) == 1


# ============================================================ p4 statement
def test_statement_is_generated_from_the_ledger_and_frozen(c):
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import compute_customer_statement

    inv(c, when=TODAY - timedelta(days=40))
    inv(c, when=TODAY - timedelta(days=5))
    rcpt(c, c.acct, 2000.0)
    st = as_(c, c.billing)["fix.ar.statement"].create(
        {
            "customer_id": c.customer.id,
            "company_id": c.company.id,
            "period_from": TODAY - timedelta(days=10),
            "period_to": TODAY,
        }
    )
    with pytest.raises(REFUSED):
        st.with_user(c.billing).write({"closing_balance": 1.0})
    st.with_user(c.billing).action_generate()
    ref = compute_customer_statement(c.env, c.customer.id, st.period_from, st.period_to)
    assert st.state == "generated"
    assert st.opening_balance == pytest.approx(ref["opening"]) == pytest.approx(11500.0)
    assert (
        st.closing_balance
        == pytest.approx(ref["closing"])
        == pytest.approx(11500.0 + 11500.0 - 2000.0)
    )
    assert st.line_count == 2 and st.total_charges == pytest.approx(11500.0)
    with pytest.raises(REFUSED):
        st.with_user(c.billing).write({"period_from": TODAY - timedelta(days=100)})
    with pytest.raises(REFUSED):
        st.with_user(c.billing).action_generate()
    with pytest.raises(REFUSED):
        st.with_user(c.billing).action_mark_delivered(channel="pigeon")
    st.with_user(c.billing).action_mark_delivered(channel="email")
    assert st.state == "delivered" and st.delivery_channel == "email"


# ============================================================== p5 deposits
def test_deposit_is_held_apart_then_applied(c):
    r = rcpt(c, c.acct, 20000.0)
    Deposit = as_(c, c.acct)["fix.ar.deposit"]
    with pytest.raises(REFUSED):
        Deposit.create({"receipt_id": r.id, "amount": 25000.0, "deposit_type": "advance"})
    with pytest.raises(REFUSED):
        as_(c, c.billing)["fix.ar.deposit"].create({"receipt_id": r.id, "amount": 100.0})
    dep = Deposit.create({"receipt_id": r.id, "amount": 15000.0, "deposit_type": "advance"})
    assert r.deposit_held_amount == pytest.approx(15000.0)
    assert r.unapplied_amount == pytest.approx(5000.0), "a held deposit still counted as unapplied"
    i = inv(c)
    # the held money cannot be allocated around the deposit
    with pytest.raises(REFUSED):
        c.env["fix.ar.allocation"].create(
            {"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0}
        )
    dep.with_user(c.acct).action_apply(invoice=i.name)
    assert dep.state == "applied" and dep.applied_to_invoice_id == i
    assert i.state == "paid"
    assert r.unapplied_amount == pytest.approx(20000.0 - 11500.0)
    with pytest.raises(REFUSED):
        dep.with_user(c.acct).write({"amount": 1.0})


def test_released_deposit_becomes_a_refund_for_another_person(c):
    r = rcpt(c, c.acct, 8000.0)
    dep = as_(c, c.acct)["fix.ar.deposit"].create(
        {"receipt_id": r.id, "amount": 8000.0, "deposit_type": "retention"}
    )
    dep.with_user(c.acct).action_release(reason="contract completed")
    assert dep.state == "released" and dep.refund_id.state == "requested"
    assert dep.refund_id.amount == pytest.approx(8000.0)
    assert r.unapplied_amount == pytest.approx(0.0)
    dep.refund_id.with_user(c.acct2).action_reject(reason="retention period not over")
    assert dep.state == "held"


# =============================================================== p9 refunds
def test_refund_of_on_account_money(c):
    r = rcpt(c, c.acct, 12000.0, method="bank_transfer", reference="TRX1")
    i = inv(c)
    c.env["fix.ar.allocation"].create({"receipt_id": r.id, "invoice_id": i.id, "amount": 11500.0})
    Refund = as_(c, c.acct)["fix.ar.refund"]
    with pytest.raises(REFUSED):
        Refund.create(
            {"receipt_id": r.id, "amount": 600.0, "method": "bank_transfer", "reason": "overpaid"}
        )
    with pytest.raises(REFUSED):
        Refund.create(
            {
                "receipt_id": r.id,
                "amount": 500.0,
                "method": "bkash",
                "reason": "x",
                "state": "authorised",
            }
        )
    with pytest.raises(REFUSED):
        as_(c, c.billing)["fix.ar.refund"].create(
            {"receipt_id": r.id, "amount": 500.0, "method": "bkash", "reason": "x"}
        )
    rf = Refund.create(
        {"receipt_id": r.id, "amount": 500.0, "method": "bkash", "reason": "overpaid"}
    )
    assert rf.requested_by_id == c.acct and r.unapplied_amount == pytest.approx(0.0)
    with pytest.raises(REFUSED):
        Refund.create({"receipt_id": r.id, "amount": 1.0, "method": "bkash", "reason": "again"})
    with pytest.raises(REFUSED):
        rf.with_user(c.acct).action_authorise()  # its requester
    if "fix.payment.execution" not in c.env:
        pytest.skip("treasury (M50) is not installed in this database")
    rf.with_user(c.acct2).action_authorise()
    assert rf.state == "authorised" and rf.authorised_by_id == c.acct2 and rf.payment_instruction
    pay = (
        c.env["fix.payment.execution"]
        .sudo()
        .search([("name", "=", rf.payment_instruction)], limit=1)
    )
    assert pay and pay.amount == pytest.approx(500.0)


def test_cash_refund_above_threshold_and_large_refund_need_more(c):
    r = rcpt(c, c.acct, 60000.0, method="bank_transfer", reference="TRX2")
    Refund = as_(c, c.acct)["fix.ar.refund"]
    with pytest.raises(REFUSED):
        Refund.create({"receipt_id": r.id, "amount": 20000.0, "method": "cash", "reason": "x"})
    big = Refund.create(
        {
            "receipt_id": r.id,
            "amount": 50000.0,
            "method": "bank_transfer",
            "reason": "deal cancelled",
        }
    )
    with pytest.raises(REFUSED):
        big.with_user(c.acct2).action_authorise()  # above the direct band
    if "fix.payment.execution" not in c.env:
        pytest.skip("treasury (M50) is not installed in this database")
    big.with_user(c.mgr).action_authorise()
    assert big.state == "authorised"


# ========================================================= p10 unbilled
def test_unbilled_exception_escalates_and_needs_a_second_person(c):
    Ubx = as_(c, c.billing)["fix.ar.unbilled.exception"]
    with pytest.raises(REFUSED):
        Ubx.create(
            {
                "source_module": "rental",
                "source_ref": "RENT/1",
                "customer_id": c.customer.id,
                "company_id": c.company.id,
                "delivered_at": TODAY + timedelta(days=2),
            }
        )
    with pytest.raises(REFUSED):
        as_(c, c.plain)["fix.ar.unbilled.exception"].create(
            {
                "source_module": "rental",
                "source_ref": "R",
                "customer_id": c.customer.id,
                "delivered_at": TODAY,
            }
        )
    x = Ubx.create(
        {
            "source_module": "rental",
            "source_ref": "RENT/2026/0042",
            "customer_id": c.customer.id,
            "company_id": c.company.id,
            "delivered_at": TODAY - timedelta(days=10),
            "estimated_value": 4000.0,
        }
    )
    assert x.reported_by == c.billing and x.detected_by == "manual"
    assert x.age_days == 10 and x.escalated_to == "cfo" and x.state == "escalated"
    with pytest.raises(REFUSED):
        x.with_user(c.billing).write({"state": "resolved"})
    with pytest.raises(REFUSED):
        x.with_user(c.billing).action_resolve_not_billable(note="free")
    with pytest.raises(REFUSED):
        x.with_user(c.billing).action_resolve_invoiced(invoice="NOPE")
    x.with_user(c.mgr).action_resolve_not_billable(note="warranty goodwill, approved")
    assert x.state == "resolved" and x.resolution == "not_billable" and x.resolved_by == c.mgr
    # BRU-ARB-01: an administrator who reported the work does not approve it
    y = as_(c, c.mgr)["fix.ar.unbilled.exception"].create(
        {
            "source_module": "other",
            "source_ref": "VISIT-77",
            "customer_id": c.customer.id,
            "company_id": c.company.id,
            "delivered_at": TODAY,
        }
    )
    with pytest.raises(REFUSED):
        y.with_user(c.mgr).action_resolve_not_billable(note="my own call")
    y.with_user(c.mgr2).action_resolve_not_billable(note="reviewed")
    assert y.resolved_by == c.mgr2
    with pytest.raises(REFUSED):
        x.with_user(c.mgr).write({"estimated_value": 1.0})


def test_unbilled_resolved_by_its_invoice(c):
    x = as_(c, c.billing)["fix.ar.unbilled.exception"].create(
        {
            "source_module": "contract",
            "source_ref": "AMC-7 Oct",
            "customer_id": c.customer.id,
            "company_id": c.company.id,
            "delivered_at": TODAY,
        }
    )
    assert x.state == "open" and not x.escalated_to
    draft = inv(c, issue=False)
    i = inv(c)
    with pytest.raises(REFUSED):
        x.with_user(c.billing).action_resolve_invoiced(invoice=draft.name)
    x.with_user(c.billing).action_resolve_invoiced(invoice=i.name)
    assert x.resolution == "invoiced" and x.invoice_id == i


def test_daily_reconciliation_raises_and_clears_unbilled_orders(odoo_env):
    shop = _gl_company(odoo_env, "ubx")
    order = _closed_order(shop, JOB)
    Ubx = odoo_env["fix.ar.unbilled.exception"]
    res = Ubx._cron_reconcile()
    x = Ubx.search([("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)])
    assert (
        res["created"] >= 1
        and x.detected_by == "reconciliation"
        and x.state in ("open", "escalated")
    )
    Ubx._cron_reconcile()
    assert (
        Ubx.search_count([("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)])
        == 1
    )
    shop.env["fix.ar.invoice"].from_closed_service_order(order, odoo_env.cr.now())
    Ubx._cron_reconcile()
    assert x.state == "resolved" and x.resolution == "invoiced" and x.invoice_id


# ============================================ every new form saves as it is
# Through /p03/model/write, as the browser sends it: the form's own editable
# fields only (controllers/a08/writable.py), so a required field the form
# omits, or a whitelist that drops one, fails here (the M07 renewal-form trap).
def _saved(out):
    assert not out.get("error"), out
    return out["id"]


def test_each_new_form_saves_through_the_workspace(c, p03):
    i = inv(c)
    old = overdue(c, days=60)
    r = rcpt(c, c.acct, 3000.0)
    W = p03.write
    _saved(
        W(
            c.billing,
            model="fix.ar.invoice.delivery",
            values={"invoice_id": i.id, "channel": "print", "recipient": ""},
        )
    )
    _saved(
        W(
            c.billing,
            model="fix.ar.statement",
            values={
                "customer_id": c.customer.id,
                "period_from": str(TODAY - timedelta(days=30)),
                "period_to": str(TODAY),
            },
        )
    )
    _saved(
        W(
            c.acct,
            model="fix.ar.deposit",
            values={
                "deposit_type": "deposit",
                "receipt_id": r.id,
                "amount": 1000.0,
                "release_due_at": str(TODAY + timedelta(days=30)),
            },
        )
    )
    _saved(
        W(
            c.mgr,
            model="fix.ar.dunning.policy",
            values={
                "name": "Corporate %s" % c.tag,
                "segment": "corporate",
                "first_offset_days": 3,
                "l1_channel": "email",
                "l1_tone": "friendly",
                "l2_days": 7,
                "l2_channel": "whatsapp",
                "l2_tone": "firm",
                "l3_days": 14,
                "l3_channel": "call",
                "l3_tone": "final",
                "escalation_role": "finance_manager",
            },
        )
    )
    _saved(
        W(
            c.acct,
            model="fix.ar.promise",
            values={
                "invoice_id": old.id,
                "amount": 2000.0,
                "promised_date": str(TODAY + timedelta(days=3)),
                "made_by": "Accounts head",
                "contact_channel": "call",
            },
        )
    )
    plan_id = _saved(
        W(
            c.acct,
            model="fix.ar.payment.plan",
            values={
                "customer_id": c.customer.id,
                "invoice_ids": [[6, 0, [i.id]]],
                "reason": "seasonal cash flow",
            },
            grids=[
                {
                    "field": "line_ids",
                    "rows": [
                        {"values": {"due_date": str(TODAY + timedelta(days=10)), "amount": 5750.0}},
                        {"values": {"due_date": str(TODAY + timedelta(days=40)), "amount": 5750.0}},
                    ],
                    "removed": [],
                }
            ],
        )
    )
    plan = c.env["fix.ar.payment.plan"].browse(plan_id)
    assert len(plan.line_ids) == 2 and plan.invoice_ids == i
    plan.with_user(c.acct2).action_activate()
    assert plan.state == "active"
    _saved(
        W(
            c.acct,
            model="fix.ar.collection.case",
            values={"customer_id": c.customer2.id, "note": "opened by hand"},
        )
    )
    _saved(
        W(
            c.acct,
            model="fix.ar.refund",
            values={
                "receipt_id": r.id,
                "amount": 500.0,
                "method": "nagad",
                "payee_account": "01711000000",
                "reason": "overpaid",
            },
        )
    )
    _saved(
        W(
            c.billing,
            model="fix.ar.unbilled.exception",
            values={
                "source_module": "marketplace",
                "source_ref": "MKT-991",
                "customer_id": c.customer.id,
                "delivered_at": str(TODAY),
                "estimated_value": 900.0,
            },
        )
    )


def test_workspace_cannot_type_the_system_fields(c, p03):
    i = inv(c)
    out = p03.write(
        c.billing,
        model="fix.ar.invoice.delivery",
        values={"invoice_id": i.id, "channel": "print", "status": "delivered"},
    )
    if not out.get("error"):
        d = c.env["fix.ar.invoice.delivery"].browse(out["id"])
        assert d.status == "queued", "the endpoint let a delivery be typed as delivered"
    out = p03.write(
        c.billing,
        model="fix.ar.unbilled.exception",
        values={
            "source_module": "other",
            "source_ref": "X",
            "customer_id": c.customer.id,
            "delivered_at": str(TODAY),
            "state": "resolved",
            "resolution": "not_billable",
        },
    )
    if not out.get("error"):
        x = c.env["fix.ar.unbilled.exception"].browse(out["id"])
        assert x.state != "resolved" and not x.resolution
