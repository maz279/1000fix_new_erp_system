"""A04 ERP audit (20 Nov 2026), stream B2: the contract money legs in M20.

  M08-F4   contract invoices carry the branch of the contract's unit;
  M08-F5   arrears invoices credit the family's revenue account (no
           deferral); advance invoices stay a contract liability;
  M08-F6   advance billing, and the term's VAT reconciles to the paisa;
  M36-F2   the term never invoices above the accepted total;
  M08-F1   a suspended stretch is never back-billed on resume;
  M08-F2   termination: stub billed, over-billing credited, penalty invoiced;
  M08-F3   an entitlement top-up is invoiced;
  M08-F11  SLA breaches earn the contract's service credit;
  M08-F18  an expired contract's last period is still billed.
Live ORM, rolled back per test.
"""

import types
import uuid
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import AccessError, UserError

TAG = uuid.uuid4().hex[:6].upper()
SWITCH = "cd_billing_engine.contract_auto_billing"


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    ns = types.SimpleNamespace(env=env)
    ns.today = fields.Date.context_today(env["fix.contract"])
    ns.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    ns.branch = env["fix.branch"].sudo().search([("operating_unit_id", "=", ns.ou.id)], limit=1)
    if not ns.branch:
        entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1)
        if not entity:  # the template has none to reuse
            entity = env["fix.entity"].create(
                {"legal_name": "B2M Entity", "code": "B2ME%s" % TAG, "company_id": env.company.id}
            )
        ns.branch = env["fix.branch"].create(
            {
                "name": "B2M Branch",
                "code": "B2M-BR-%s" % TAG,
                "entity_id": entity.id,
                "operating_unit_id": ns.ou.id,
            }
        )
    ids = [env.ref("base.group_user").id]
    ns.officer = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "b2m officer",
                "login": "b2m_officer_%s" % TAG,
                "group_ids": [
                    (6, 0, [*ids, env.ref("cd_contract_core.group_contract_officer").id])
                ],
                "assigned_operating_unit_ids": [(6, 0, ns.ou.ids)],
                "default_operating_unit_id": ns.ou.id,
            }
        )
    )
    ns.customer = env["res.partner"].create(
        {"name": "B2M Customer %s" % TAG, "phone": "01711000912"}
    )
    env["ir.config_parameter"].sudo().set_param(SWITCH, "1")
    income = env["account.account"].search(
        [("account_type", "=", "income"), ("company_ids", "in", env.company.id)], limit=1
    )
    other = env["account.account"].search(
        [
            ("account_type", "in", ("income_other", "income")),
            ("company_ids", "in", env.company.id),
            ("id", "!=", income.id),
        ],
        limit=1,
    )
    ns.amc_income, ns.other_income = income, other
    env["ir.config_parameter"].sudo().set_param(
        "cd_billing_engine.account_code.contract_revenue_amc", income.code
    )
    env["ir.config_parameter"].sudo().set_param(
        "cd_billing_engine.account_code.contract_penalty_income", other.code or income.code
    )
    return ns


def _active(m, start, months=12, annual=120000.0, **kw):
    vals = {
        "name": "B2M AMC",
        "family": "amc",
        "customer_id": m.customer.id,
        "operating_unit_id": m.ou.id,
        "date_start": start,
        "date_end": start + relativedelta(months=months) - timedelta(days=1),
        "annual_value": annual,
        "stamp_duty_cert_no": "SD-%s" % TAG,
        "stamp_duty_amount": 300.0,
        "has_signed_contract_doc": True,
    }
    vals.update(kw)
    contract = m.env["fix.contract"].with_user(m.officer).create(vals)
    contract.sudo().action_activate()
    contract.invalidate_recordset()
    return contract


def _walk(m):
    return m.env["fix.contract.billing.period"].sudo().cron_bill_contracts()


def _periods(m, contract):
    return (
        m.env["fix.contract.billing.period"]
        .sudo()
        .search([("contract_id", "=", contract.id)], order="period_start")
    )


def _invoices(m, contract):
    return _periods(m, contract).mapped("invoice_id")


# ================================================================ wiring


def test_the_money_consumers_and_the_credit_job_are_wired(m):
    env = m.env
    for event, method in (
        ("contract.terminated", "consume_contract_terminated"),
        ("contract.entitlement_topped_up", "consume_contract_entitlement_topped_up"),
    ):
        row = env["fix.event.consumer"].sudo().search([("event_type", "=", event)])
        assert row.filtered(
            lambda r, me=method: r.method == me and r.model == "fix.a04.contract.consumers"
        )
    cron = env.ref("cd_billing_engine.ir_cron_contract_service_credits")
    assert cron.active and "cron_contract_service_credits()" in cron.code
    assert "contract_termination" in dict(env["fix.credit.note"]._fields["reason_code"].selection)


def test_only_the_relay_runs_the_contract_consumers(m):
    consumers = m.env["fix.a04.contract.consumers"].with_user(m.officer)
    with pytest.raises(AccessError):
        consumers.consume_contract_terminated({"aggregate_id": 1})
    with pytest.raises(AccessError):
        m.env["fix.contract.billing.period"].with_user(m.officer).cron_contract_service_credits()


# ================================================================ M08-F4 / F5 / F6


def test_arrears_invoices_carry_the_branch_and_the_family_revenue_account(m):
    contract = _active(m, m.today - timedelta(days=65))
    assert _walk(m) == 2
    for period in _periods(m, contract):
        invoice = period.invoice_id
        assert invoice.branch_id == contract._fix_billing_branch()
        assert invoice.branch_id, "every unit of the estate has its branch"
        assert invoice.revenue_account_id == m.amc_income
        assert invoice._revenue_role() == "revenue"  # earned: no deferral
        assert period.billing_timing == "arrears" and period.revenue_account_id == m.amc_income
        assert invoice.invoice_date == period.period_end
    invoice = _invoices(m, contract)[:1]
    invoice.sudo().action_issue()
    move = invoice.posted_move_id
    if move:  # the template chart carries the AR roles: show the journal lines
        credit = move.line_ids.filtered(lambda line: line.account_id == m.amc_income)
        assert round(credit.credit, 2) == round(invoice.taxable_amount, 2)
        ar = move.line_ids.filtered(lambda line: line.debit > 0)
        assert round(sum(ar.mapped("debit")), 2) == round(invoice.total_payable, 2)


def test_advance_billing_invoices_at_the_period_start_as_a_liability(m):
    contract = _active(
        m, m.today - timedelta(days=10), billing_frequency="quarterly", billing_timing="advance"
    )
    assert _walk(m) == 1
    (period,) = _periods(m, contract)
    assert period.period_end == contract.date_start + relativedelta(months=3) - timedelta(days=1)
    assert period.amount == 30000.0
    invoice = period.invoice_id
    assert invoice.invoice_date == period.period_start
    assert not invoice.revenue_account_id
    assert invoice._revenue_role() == "deferred_revenue"
    assert period.revenue_account_id == m.amc_income  # where M53 recognises it
    assert contract.billed_through_date == period.period_end


def test_the_term_vat_reconciles_to_the_accepted_total(m):
    """M08-F6: per-period VAT rounding gave 17,100.01; the last period now
    carries the term's VAT rounding."""
    start = m.today - relativedelta(months=7)
    contract = _active(
        m,
        start,
        months=7,
        annual=round(100000.0 * 12 / 7, 2),
        term_value=100000.0,
        accepted_total=115000.0,
    )
    assert _walk(m) == 7
    invoices = _invoices(m, contract)
    assert round(sum(invoices.mapped("taxable_amount")), 2) == 100000.0
    assert round(sum(invoices.mapped("vat_amount")), 2) == 15000.0
    assert round(sum(invoices.mapped("total_payable")), 2) == 115000.0


def test_the_term_never_invoices_above_the_accepted_total(m):
    """M36-F2: 77,050 was invoiced on 70,350 accepted."""
    start = m.today - relativedelta(months=3)
    contract = _active(
        m, start, months=3, annual=120000.0, term_value=30000.0, accepted_total=33000.0
    )
    assert _walk(m) == 0
    assert not _periods(m, contract)
    assert "accepted" in contract.message_ids[:1].body


# ================================================================ M08-F1 / F18


def test_a_suspension_is_not_back_billed_on_resume(m):
    contract = _active(m, m.today.replace(day=1) - relativedelta(months=3))
    first = contract.date_start
    contract.sudo()._guarded().write(
        {"state": "suspended", "suspended_on": first + relativedelta(months=1)}
    )
    assert _walk(m) == 0  # nothing is billed while suspended
    manager = m.env.ref("cd_contract_core.group_contract_manager")
    m.officer.sudo().write({"group_ids": [(4, manager.id)]})
    contract.with_user(m.officer).action_resume(treatment="forfeit", note="resumed")
    assert _walk(m) == 1
    # the month before the suspension is billed in full; the two suspended
    # months are never billed (the probe back-billed 69,041 on resume)
    (period,) = _periods(m, contract)
    assert period.period_start == first and period.amount == 10000.0
    rows = contract._fix_billing_schedule()
    assert [r["amount"] for r in rows[1:3]] == [0.0, 0.0]
    # the month of the resume bills only from the resume day
    expected = 10000.0 if m.today.day == 1 else None
    assert 0.0 < rows[3]["amount"] <= 10000.0
    if expected is None:
        assert rows[3]["amount"] < 10000.0


def test_an_expired_contract_still_bills_its_last_period(m):
    contract = _active(m, m.today - relativedelta(months=3), months=2)
    contract.sudo()._guarded().write({"state": "expired"})
    assert _walk(m) == 2
    assert contract.billed_through_date == contract.date_end


# ================================================================ M08-F2 termination


def _terminate(m, contract, effective, penalty=0.0):
    term = (
        m.env["fix.contract.termination"]
        .sudo()
        .create(
            {
                "name": "B2M term %s" % TAG,
                "contract_id": contract.id,
                "kind": "termination",
                "reason": "customer exit",
                "effective_date": effective,
                "penalty_amount": penalty,
            }
        )
    )
    term._guarded().write(
        {
            "state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": "tier_5",
            "dofa_approved_amount": 10**9,
        }
    )
    term.sudo().action_execute_termination()
    return term


def _consume(m, termination):
    return (
        m.env["fix.a04.contract.consumers"]
        .sudo()
        .consume_contract_terminated(
            {"aggregate": "fix.contract.termination", "aggregate_id": termination.id, "payload": {}}
        )
    )


def test_termination_bills_the_stub_and_invoices_the_penalty(m):
    contract = _active(m, m.today - timedelta(days=65))
    assert _walk(m) == 2
    before = len(_periods(m, contract))
    term = _terminate(m, contract, m.today, penalty=50000.0)
    result = _consume(m, term)
    assert result["stub_invoices"] == 1, "the delivered days since the last period are billed"
    periods = _periods(m, contract)
    assert len(periods) == before + 1
    assert periods[-1].period_end == contract.date_end == m.today - timedelta(days=1)
    assert round(sum(periods.mapped("amount")), 2) == contract._fix_billing_target()
    penalty = term.penalty_invoice_id
    assert penalty.state == "draft" and round(penalty.taxable_amount, 2) == 50000.0
    assert penalty.branch_id == contract._fix_billing_branch()
    assert penalty.revenue_account_id.code in (m.other_income.code, m.amc_income.code)
    assert _consume(m, term)["created"] is False  # idempotent


def test_termination_credits_what_was_billed_beyond_the_end(m):
    contract = _active(
        m, m.today - timedelta(days=20), billing_frequency="quarterly", billing_timing="advance"
    )
    assert _walk(m) == 1
    invoice = _invoices(m, contract)
    invoice.sudo().action_issue()
    term = _terminate(m, contract, m.today)
    result = _consume(m, term)
    (credit,) = m.env["fix.credit.note"].sudo().browse(result["credit_notes"])
    assert credit.reason_code == "contract_termination"
    assert credit.state == "pending_approval"  # routed, never auto-approved
    over = round(30000.0 - contract._fix_billing_target(), 2)
    assert over > 0
    assert round(credit.amount, 2) == round(
        over * invoice.total_payable / invoice.taxable_amount, 2
    )


def test_a_suspension_notice_moves_no_money(m):
    contract = _active(m, m.today - timedelta(days=65))
    term = (
        m.env["fix.contract.termination"]
        .sudo()
        .create(
            {
                "name": "B2M susp %s" % TAG,
                "contract_id": contract.id,
                "kind": "suspension",
                "reason": "non-payment",
                "effective_date": m.today,
            }
        )
    )
    term._guarded().write(
        {
            "state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": "tier_5",
            "dofa_approved_amount": 10**9,
        }
    )
    term.sudo().action_execute_termination()
    assert contract.state == "suspended" and contract.sudo().suspension_ids
    assert "skipped" in _consume(m, term)


# ================================================================ M08-F3 top-up


def test_an_applied_top_up_is_invoiced(m):
    contract = _active(m, m.today - timedelta(days=10))
    ent = (
        m.env["fix.contract.entitlement"]
        .sudo()
        ._guarded()
        .create(
            {"contract_id": contract.id, "entitlement_type": "incidents", "quantity_included": 5}
        )
    )
    topup = (
        m.env["fix.contract.entitlement.topup"]
        .sudo()
        .create(
            {
                "name": "TU-%s" % TAG,
                "entitlement_id": ent.id,
                "quantity": 3,
                "customer_reference": "PO-9",
                "amount": 20000.0,
            }
        )
    )
    topup.action_submit()
    topup.action_apply()
    event = {
        "aggregate": "fix.contract",
        "aggregate_id": contract.id,
        "payload": {"topup_id": topup.id, "amount": 20000.0},
    }
    Consumers = m.env["fix.a04.contract.consumers"].sudo()
    result = Consumers.consume_contract_entitlement_topped_up(event)
    invoice = m.env["fix.ar.invoice"].browse(result["id"])
    assert invoice == topup.invoice_id and invoice.state == "draft"
    assert round(invoice.taxable_amount, 2) == 20000.0
    assert invoice.source_model == topup._name and invoice.source_id == topup.id
    assert invoice.branch_id == contract._fix_billing_branch()
    forged = dict(event, payload={"topup_id": topup.id, "amount": 1.0})
    topup.sudo()._guarded().write({"invoice_id": False})
    with pytest.raises(UserError, match="says"):
        Consumers.consume_contract_entitlement_topped_up(forged)


# ================================================================ M08-F11 service credits


def test_sla_breaches_earn_the_service_credit(m):
    contract = _active(m, m.today - timedelta(days=65))
    m.env["fix.contract.credit.scheme"].sudo().create(
        {
            "contract_id": contract.id,
            "breach_type": "resolution",
            "credit_basis": "pct_fee",
            "credit_value": 5.0,
            "cap_pct": 10.0,
        }
    )
    assert _walk(m) == 2
    first = _periods(m, contract)[0]
    first.invoice_id.sudo().action_issue()
    brand = m.env["fix.brand"].create({"name": "B2M Brand %s" % TAG, "code": "B2M%s" % TAG})
    model = m.env["fix.device.model"].create({"name": "B2M Model", "brand_id": brand.id})
    device = m.env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": m.customer.id,
            "serial_number": "B2M-%s" % TAG,
            "branch_id": m.branch.id,
        }
    )
    order = m.env["fix.service.order"].create(
        {
            "customer_id": m.customer.id,
            "device_id": device.id,
            "branch_id": m.branch.id,
            "service_type": "walk_in",
            "fault_description": "B2M breach",
            "contract_id": contract.id,
        }
    )
    policy = m.env["fix.sla.policy"].sudo().search([], limit=1)
    when = fields.Datetime.to_datetime(first.period_start) + timedelta(days=3)
    m.env["fix.sla.kpi.instance"].sudo().create(
        {
            "res_model": "fix.service.order",
            "res_id": order.id,
            "policy_id": policy.id,
            "kpi_code": "resolution",
            "target_hours": 24.0,
            "started_at": when - timedelta(days=2),
            "target_at": when - timedelta(days=1),
            "state": "breached",
            "breached_at": when,
        }
    )
    assert m.env["fix.contract.billing.period"].sudo().cron_contract_service_credits() == 1
    note = first.service_credit_note_id
    assert note.reason_code == "service_credit" and first.service_credit_breaches == 1
    # 5% of the period fee, VAT-inclusive on the invoice's ratio
    expected = round(
        first.amount * 0.05 * first.invoice_id.total_payable / first.invoice_id.taxable_amount, 2
    )
    assert round(note.amount, 2) == expected
    assert m.env["fix.contract.billing.period"].sudo().cron_contract_service_credits() == 0
