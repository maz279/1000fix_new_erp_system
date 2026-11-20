# ruff: noqa: F811  (the imported m fixture is used as a parameter)
"""A04 ERP audit (20 Nov 2026), B2 follow-ups in M39 / M53 (stream B3).

1. A contract period billed IN ADVANCE carries the contract family's revenue
   account (fix.contract.billing.period.revenue_account_id, set by B2's
   walker); M53's recognition of it credited the generic 400100 instead.
2. The quotation.accepted consumer acted on any event naming an id; the M01
   estimate now publishes estimate.quotation_accepted on another model.
Live ORM, rolled back (``odoo_env``)."""

import uuid
from datetime import timedelta

import pytest

pytest.importorskip("odoo.addons.cd_billing_engine.tests.test_a04erp_b2_contract_money")

from odoo.addons.cd_billing_engine.tests.test_a04erp_b2_contract_money import (
    _active,
    _periods,
    _walk,
    m,  # noqa: F401
)


def test_advance_contract_period_is_recognised_to_its_family_account(m):
    env = m.env
    # a family account distinct from the generic revenue role, so only the
    # period's account can explain the credit
    family = env["account.account"].create(
        {
            "code": "B3AMC%s" % uuid.uuid4().hex[:5].upper(),
            "name": "B3 AMC income",
            "account_type": "income",
        }
    )
    env["ir.config_parameter"].sudo().set_param(
        "cd_billing_engine.account_code.contract_revenue_amc", family.code
    )
    m.amc_income = family
    contract = _active(
        m, m.today - timedelta(days=10), billing_frequency="quarterly", billing_timing="advance"
    )
    assert _walk(m) == 1
    (period,) = _periods(m, contract)
    assert period.revenue_account_id == m.amc_income
    invoice = period.invoice_id.sudo()
    invoice.action_issue()
    sched = (
        env["fix.revenue.schedule"]
        .sudo()
        .search([("source_model", "=", "fix.ar.invoice"), ("source_id", "=", invoice.id)])
    )
    assert sched, "the advance invoice defers its period"
    sched.action_recognize_period(as_of=period.period_end)
    lines = sched.line_ids.mapped("move_id.line_ids").filtered(lambda line: line.credit > 0)
    assert lines and set(lines.mapped("account_id")) == {m.amc_income}
    assert round(sum(lines.mapped("credit")), 2) == round(sched.total_amount, 2)


def test_the_quotation_consumer_ignores_another_models_event(odoo_env):
    Sub = odoo_env["fix.subscription"].sudo()
    before = Sub.search_count([])
    out = Sub.consume_quotation_accepted(
        {"aggregate": "fix.estimate", "aggregate_id": 987654321, "payload": {}}
    )
    assert "not fix.quotation" in out.get("skipped", "")
    assert Sub.search_count([]) == before
