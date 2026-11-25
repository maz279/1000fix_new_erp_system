"""A04 C2-C13 build (2026-11-04): M39 controls on the models other than
fix.subscription (A08's): cycle charges, usage, plan-change prorations and
autopay mandates. Live ORM, rolled back; attacks run as non-admin users with
and without the role that is the control.
"""

from __future__ import annotations

import json
import types
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = uuid.uuid4().hex[:6].upper()
SUB_OFFICER = "cd_subscription.group_subscription_officer"
BILLING = "account.group_account_user"


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


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(r.payload) for r in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.today = fields.Date.context_today(env["fix.subscription"])
    x.clerk = _user(env, "a4b1s_clerk")
    x.officer = _user(env, "a4b1s_officer", SUB_OFFICER)
    x.officer2 = _user(env, "a4b1s_officer2", SUB_OFFICER)
    x.billing = _user(env, "a4b1s_billing", BILLING)
    x.billing2 = _user(env, "a4b1s_billing2", BILLING)
    x.tier1 = _user(env, "a4b1s_tier1", "cd_entity_config.group_dofa_tier_1")
    x.tier2 = _user(env, "a4b1s_tier2", "cd_entity_config.group_dofa_tier_2")
    x.customer = env["res.partner"].create({"name": "A04B1 Sub %s" % TAG, "phone": "01711003901"})
    return x


def _sub(c, **kw):
    vals = {
        "name": "A04B1 sub %s" % TAG,
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
    return c.env["fix.subscription"].create(vals)  # A08's model: set up as the system


def _bill(c, sub):
    # A04 ERP M39-F9: a cycle is billed with a reviewed run's authority (the
    # guard token the run's commit carries), never from the plain button
    sub.with_user(c.billing)._guarded().action_generate_charge()
    return sub.charge_ids.sorted("period_start")[-1]


# =========================================================================== charges
def test_charge_is_frozen_once_invoiced(c, p03):
    charge = _bill(c, _sub(c))
    assert charge.invoice_id
    with pytest.raises(UserError, match="invoiced"):
        charge.with_user(c.billing).write({"amount": 1.0})
    with pytest.raises(UserError):
        charge.with_user(c.billing).write({"invoice_id": False})
    res = p03(c.billing).write(
        model="fix.subscription.charge", record_id=charge.id, values={"amount": 1}
    )
    charge.invalidate_recordset()
    assert res.get("error") and charge.amount == 30000.0


def test_charge_cannot_be_backdated_or_bill_a_cycle_twice(c):
    sub = _sub(c, next_invoice_date=c.today - timedelta(days=365))
    with pytest.raises(UserError, match="backdated"):
        sub.with_user(c.billing)._guarded().action_generate_charge()
    sub2 = _sub(c)
    charge = _bill(c, sub2)
    with pytest.raises(ValidationError, match="billed once"):
        c.env["fix.subscription.charge"].create(
            {
                "company_id": charge.company_id.id,
                "operating_unit_id": charge.operating_unit_id.id,
                "subscription_id": sub2.id,
                "period_start": charge.period_start + timedelta(days=5),
                "period_end": charge.period_end + timedelta(days=5),
                "amount": 100.0,
            }
        )
    with pytest.raises(ValidationError):
        c.env["fix.subscription.charge"].create(
            {
                "company_id": charge.company_id.id,
                "operating_unit_id": charge.operating_unit_id.id,
                "subscription_id": sub2.id,
                "period_start": charge.period_end + timedelta(days=1),
                "period_end": charge.period_end + timedelta(days=30),
                "amount": 0.0,
            }
        )


def test_overage_is_billed_and_the_usage_locked(c, p03):
    sub = _sub(c)
    with pytest.raises(REFUSED):
        c.env["fix.subscription.usage"].with_user(c.clerk).create(
            {
                "subscription_id": sub.id,
                "period_start": c.today,
                "period_end": c.today,
                "metric": "x",
            }
        )
    usage = (
        c.env["fix.subscription.usage"]
        .with_user(c.officer)
        .create(
            {
                "subscription_id": sub.id,
                "period_start": c.today,
                "period_end": c.today + timedelta(days=29),
                "metric": "prints",
                "quantity": 150,
                "committed": 100,
                "overage_rate": 100,
            }
        )
    )
    assert usage.overage_charge == 5000.0 and usage._fields["overage_charge"].store
    charge = _bill(c, sub)
    usage.invalidate_recordset()
    assert charge.amount == 35000.0 and charge.overage_amount == 5000.0
    assert usage.state == "billed" and usage.charge_id == charge
    line_total = sum(charge.invoice_id.line_ids.mapped("taxable_amount"))
    assert abs(line_total - 35000.0) < 0.01, "the invoice bills the overage too"
    with pytest.raises(UserError, match="locked"):
        usage.write({"quantity": 0})
    res = p03(c.officer).write(
        model="fix.subscription.usage", record_id=usage.id, values={"quantity": 0}
    )
    usage.invalidate_recordset()
    assert res.get("error") and usage.quantity == 150


def test_overdue_unpaid_charges_are_the_dunning_basis(c):
    sub = _sub(c)
    charge = _bill(c, sub)
    Charge = c.env["fix.subscription.charge"]
    assert not Charge._fix_overdue_unpaid(
        sub, as_of=c.today + timedelta(days=60)
    ), "a draft invoice is not a debt"
    charge.invoice_id.sudo().write({"state": "issued"})
    charge.invalidate_recordset()
    overdue = Charge._fix_overdue_unpaid(sub, as_of=c.today + timedelta(days=60))
    assert overdue == charge


# =========================================================================== proration
def test_proration_is_computed_not_typed(c, p03):
    sub = _sub(c)
    _bill(c, sub)  # the cycle today .. today+29 is billed at 30,000
    with pytest.raises(UserError):
        c.env["fix.subscription.proration"].with_user(c.officer).create(
            {
                "name": "typed",
                "subscription_id": sub.id,
                "effective_date": c.today,
                "amount": -50000,
                "state": "invoiced",
            }
        )
    res = p03(c.officer).write(
        model="fix.subscription.proration",
        values={
            "name": "p03",
            "subscription_id": sub.id,
            "change_type": "downgrade",
            "new_amount": 15000,
            "amount": -50000,
            "effective_date": str(c.today + timedelta(days=15)),
            "state": "invoiced",
        },
    )
    p = c.env["fix.subscription.proration"].browse(res.get("id") or 0)
    assert p.state == "draft" and p.amount != -50000, "state and amount are not taken from the form"
    p = (
        c.env["fix.subscription.proration"]
        .with_user(c.officer)
        .create(
            {
                "name": "orm",
                "subscription_id": sub.id,
                "change_type": "downgrade",
                "new_amount": 15000,
                "effective_date": c.today + timedelta(days=15),
            }
        )
    )
    # (15,000 - 30,000) x 15 unused days / 30-day cycle = -7,500
    assert p.amount == -7500.0 and p.old_amount == 30000.0 and p.days_remaining == 15
    with pytest.raises(UserError, match="backdated"):
        c.env["fix.subscription.proration"].with_user(c.officer).create(
            {
                "name": "back",
                "subscription_id": sub.id,
                "new_amount": 1,
                "effective_date": c.today - timedelta(days=90),
            }
        )


def test_proration_credit_is_approved_under_dofa_and_applied(c):
    sub = _sub(c)
    _bill(c, sub)
    P = c.env["fix.subscription.proration"].with_user(c.officer)
    p = P.create_for_plan_change(
        sub, 15000.0, to_plan="basic", effective_date=c.today + timedelta(days=15)
    )
    assert p.change_type == "downgrade" and p.dofa_tier_required == "tier_1"
    with pytest.raises(UserError):
        p.action_dofa_approve()  # routed only
    p.action_request_approval()
    assert c.officer not in assigned(p)
    approve_via_inbox(p, c.tier1, requester=c.officer)
    p.invalidate_recordset()
    sub.invalidate_recordset()
    # A04 ERP M39-F7: dated 15 days ahead, it applies on its date, not at approval
    assert p.state == "approved" and not p.applied_to_subscription
    assert sub.recurring_amount == 30000.0
    assert _events(c.env, "subscription.proration_approved", p.id)[0]["amount"] == -7500.0
    p.sudo()._guarded().write({"effective_date": c.today})  # the date comes
    assert c.env["fix.subscription.proration"].cron_apply_due_prorations() >= 1
    p.invalidate_recordset()
    sub.invalidate_recordset()
    assert p.applied_to_subscription
    assert sub.recurring_amount == 15000.0 and sub.plan == "basic"
    with pytest.raises(UserError):
        p.with_user(c.billing)._fix_mark_invoiced()  # the finance bridge only


def test_upgrade_is_decided_by_a_billing_user_who_did_not_raise_it(c):
    sub = _sub(c)
    _bill(c, sub)
    p = (
        c.env["fix.subscription.proration"]
        .with_user(c.officer)
        .create_for_plan_change(sub, 60000.0, to_plan="premium")
    )
    assert p.amount > 0 and p.dofa_tier_required == "tier_0"
    p.action_request_approval()
    approver = assigned(p) & (c.billing | c.billing2)
    assert approver, "routed to the billing role"
    approve_via_inbox(p, approver[:1], requester=c.officer)
    p.invalidate_recordset()
    assert p.state == "approved"


# =========================================================================== autopay
def _mandate(c, **kw):
    sub = kw.pop("sub", None) or _sub(c)
    vals = {
        "subscription_id": sub.id,
        "method": "bkash",
        "max_amount": 40000.0,
        "consent_channel": "otp",
    }
    vals.update(kw)
    return c.env["fix.subscription.autopay"].with_user(c.officer).create(vals)


def test_mandate_needs_the_role_and_is_born_awaiting_consent(c):
    sub = _sub(c)
    with pytest.raises(REFUSED):
        c.env["fix.subscription.autopay"].with_user(c.clerk).create({"subscription_id": sub.id})
    with pytest.raises(UserError):
        c.env["fix.subscription.autopay"].with_user(c.officer).create(
            {"subscription_id": sub.id, "state": "active"}
        )
    m = _mandate(c, sub=sub)
    assert m.state == "draft"
    with pytest.raises(UserError, match="consent"):
        m.action_activate()
    with pytest.raises(UserError):
        m.write({"last_result": "success", "last_attempt_at": fields.Datetime.now()})


def test_otp_consent_activates_the_mandate(c, monkeypatch):
    sent = {}
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.update(code=code)
    )
    m = _mandate(c)
    m.action_send_consent_otp()
    assert sent.get("code")
    assert (
        m.action_verify_consent_otp(otp="000000" if sent["code"] != "000000" else "111111")[
            "verified"
        ]
        is False
    )
    assert m.action_verify_consent_otp(otp=sent["code"])["verified"]
    assert m.consent_at and "OTP" in m.consent_evidence
    with pytest.raises(UserError):
        m.write({"max_amount": 9_000_000.0})  # the consented terms are fixed
    m.action_activate()
    assert m.state == "active"


def test_signed_form_is_verified_by_another_officer(c):
    att = c.env["ir.attachment"].create({"name": "mandate.pdf", "raw": b"%PDF-1.4 mandate"})
    Doc = c.env["fix.document"]
    dtype = Doc._fields["document_type"]._description_selection(c.env)[0][0]
    doc = Doc.create({"name": "Mandate form", "attachment_id": att.id, "document_type": dtype})
    m = _mandate(
        c,
        consent_channel="signed_form",
        consent_document_id=doc.id,
        consent_signatory="Account Holder",
    )
    with pytest.raises(UserError, match="Segregation of duties"):
        m.action_verify_signed_form()
    m.with_user(c.officer2).action_verify_signed_form()
    assert m.consent_verified_by == c.officer2
    m.action_activate()
    assert m.state == "active"


def test_collection_requests_retries_and_suspends(c, monkeypatch):
    monkeypatch.setattr(fix_otp_util, "dispatch_otp", lambda *a, **k: None)
    sub = _sub(c)
    m = _mandate(c, sub=sub)
    m.sudo()._guarded().write({"consent_at": fields.Datetime.now(), "consent_evidence": "test"})
    m.action_activate()
    charge = _bill(c, sub)
    charge.invoice_id.sudo().write({"state": "issued"})
    Autopay = c.env["fix.subscription.autopay"]
    assert Autopay.cron_autopay_collect() == 1
    assert Autopay.cron_autopay_collect() == 0, "one open request per charge"
    attempt = m.attempt_ids
    assert attempt.state == "requested"
    assert _events(c.env, "subscription.autopay_collection_requested", m.id)
    with pytest.raises(UserError):
        attempt.with_user(c.officer).action_record_result("success")  # the gateway only
    for n in range(1, 5):
        attempt.sudo().action_record_result("failed", reason="insufficient balance")
        m.invalidate_recordset()
        if n <= 3:
            assert m.state == "active" and m.failure_count == n and m.next_retry_on
            m.sudo()._guarded().write({"next_retry_on": c.today})
            Autopay.cron_autopay_collect()
            attempt = m.attempt_ids.filtered(lambda a: a.state == "requested")
        else:
            assert m.state == "suspended"
    assert _events(c.env, "subscription.autopay_failed", m.id)


def test_collection_above_the_consented_limit_is_not_taken(c):
    sub = _sub(c, recurring_amount=90000.0)
    m = _mandate(c, sub=sub, max_amount=40000.0)
    m.sudo()._guarded().write({"consent_at": fields.Datetime.now(), "consent_evidence": "test"})
    m.action_activate()
    charge = _bill(c, sub)
    charge.invoice_id.sudo().write({"state": "issued"})
    assert c.env["fix.subscription.autopay"].cron_autopay_collect() == 0
    assert m.attempt_ids.state == "over_limit"


# =========================================================================== wiring
@pytest.mark.parametrize(
    "xmlid,model,method",
    [
        (
            "cd_subscription.ir_cron_subscription_billing",
            "fix.subscription.charge",
            "cron_generate_due_charges",
        ),
        (
            "cd_subscription.ir_cron_subscription_autopay",
            "fix.subscription.autopay",
            "cron_autopay_collect",
        ),
    ],
)
def test_cron_records_exist_and_name_their_method(c, xmlid, model, method):
    cron = c.env.ref(xmlid)
    assert cron.active and cron.model_id.model == model and method in cron.code
    getattr(c.env[model], method)()
    getattr(c.env[model], method)()


def test_billing_job_is_off_until_finance_switches_it_on(c):
    sub = _sub(c)
    Charge = c.env["fix.subscription.charge"]
    assert Charge.cron_generate_due_charges() == 0 and not sub.charge_ids
    c.env["ir.config_parameter"].sudo().set_param("cd_subscription.auto_billing", "1")
    Run = c.env["fix.subscription.billing.run"]
    Run.search(
        [("state", "in", ("draft", "dry_run", "reviewed", "partial"))]
    ).sudo()._guarded().write({"state": "void"})
    # A04 ERP M39-F9 (BRU-SUB-17): switched on, the job prepares a dry run for
    # review; it bills nothing itself, and prepares one open run at a time
    assert Charge.cron_generate_due_charges() >= 1
    sub.invalidate_recordset()
    assert not sub.charge_ids
    assert Charge.cron_generate_due_charges() == 0
    run = Run.search([("state", "=", "dry_run")], limit=1)
    assert sub in run.unit_ids.mapped("subscription_id")


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
