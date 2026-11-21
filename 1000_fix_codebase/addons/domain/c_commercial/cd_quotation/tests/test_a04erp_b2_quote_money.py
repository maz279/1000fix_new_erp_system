# ruff: noqa: F811  (the c fixture is imported from the M36 suite)
"""A04 ERP audit (20 Nov 2026), stream B2: M36 quotation and tender money.

  M36-F1  the tender award's contract is priced before VAT;
  M36-F2  quotation VAT is M51's per line and is not typed;
  M36-F3  a converted contract carries the term value and accepted total, and
          bills exactly the quoted value;
  M36-F4  a contract invoice finds the quotation its advance was paid on;
  M36-F5  quotation.declined is closed out by a consumer;
  M36-F6  bond cash legs post to the GL (fail closed); retention is
          withheld on a tender contract's bills;
  M36-F7  an approved variation amends the tender's contract;
  M36-F9  a won tender's contract carries scope, retention and LD terms,
          and its pricing quotation is closed.
Live ORM, rolled back per test.
"""

from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import (  # noqa: F401  (fixtures)
    _quote,
    _sent_quote,
    c,
)
from odoo.exceptions import AccessError, UserError

REFUSED = (UserError, AccessError)


def _won_tender(c, awarded=115000.0, months=12, retention=10.0):
    """A tender priced on a quotation and awarded (the superuser stands in
    for the committee's routed decision, tested in the M36 suite)."""
    env = c.env
    t = (
        env["fix.tender"]
        .sudo()
        .create(
            {
                "name": "B2 tender",
                "client_name": "Ministry",
                "client_id": c.agency.id,
                "due_date": c.today + timedelta(days=10),
                "operating_unit_id": c.ou.id,
                "contract_family": "managed",
                "contract_months": months,
                "bid_validity_days": 90,
                "retention_pct": retention,
                "boq_line_ids": [
                    (
                        0,
                        0,
                        {
                            "item_no": "1",
                            "description": "Managed print service",
                            "quantity": 1,
                            "unit_price_incl_vat": awarded,
                            "line_kind": "related_service",
                        },
                    )
                ],
            }
        )
    )
    t.action_price_as_quotation()
    t._guarded().write(
        {
            "state": "won",
            "awarded_value": awarded,
            "award_ref": "NOA-B2",
            "award_date": c.today,
        }
    )
    contract = env["fix.contract"].browse(t._create_contract())
    return t, contract


# ------------------------------------------------------------- M36-F1 / F9
def test_the_tender_contract_is_priced_before_vat(c):
    """115,000 awarded (incl. VAT) was billed 132,250."""
    t, contract = _won_tender(c)
    quote = t.quotation_id
    assert round(quote.amount_total, 2) == 115000.0
    assert contract.term_value == round(quote.value, 2) == 100000.0
    assert contract.accepted_total == 115000.0
    assert round(sum(r["amount"] for r in contract._fix_billing_schedule()), 2) == 100000.0


def test_the_tender_contract_carries_scope_terms_and_closes_its_quotation(c):
    t, contract = _won_tender(c)
    assert contract.retention_pct == 10.0
    assert contract.ld_rate_pct_per_day == t.ld_rate_pct_per_day
    assert contract.tender_id == t
    assert contract.scope_line_ids and contract.quotation_id == t.quotation_id
    quote = t.quotation_id
    assert quote.state == "accepted" and quote.acceptance_method == "tender_award"
    assert quote.converted_res_id == contract.id


# ------------------------------------------------------------- M36-F2
def test_quotation_vat_is_m51_per_line_and_never_typed(c):
    q = _quote(
        c,
        line_ids=[
            (0, 0, {"description": "AMC year", "line_type": "recurring", "unit_price": 10000.33}),
            (0, 0, {"description": "Visit pack", "line_type": "recurring", "unit_price": 2000.33}),
        ],
    )
    determined = q._fix_quote_determination()
    assert len(determined) == 2
    assert q.vat_amount == round(sum(float(d.vat_amount) for _l, d in determined), 2)
    assert q.vat_rate == 15.0
    assert q.amount_total == round(q.value + q.vat_amount, 2)
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        q.with_user(c.author).write({"vat_rate": 5.0})
    assert q.vat_rate == 15.0


# ------------------------------------------------------------- M36-F3
@pytest.mark.parametrize("months,value", [(6, 120000.0), (1, 10000.0), (24, 240000.0)])
def test_a_converted_contract_bills_exactly_the_quoted_value(c, months, value):
    q = _quote(c, value=value, contract_months=months, contract_start=c.today + timedelta(days=1))
    q.sudo()._guarded().write(
        {
            "state": "accepted",
            "acceptance_ref": "probe",
            "accepted_value": q.value,
            "accepted_total": q.amount_total,
        }
    )
    model, cid = q._convert()
    contract = c.env[model].browse(cid)
    assert contract.term_value == value
    assert contract.accepted_total == q.amount_total
    rows = contract._fix_billing_schedule()
    assert len(rows) == months
    assert round(sum(r["amount"] for r in rows), 2) == value


# ------------------------------------------------------------- M36-F4
def test_a_contract_invoice_finds_the_quotation_of_its_advance(c):
    q = _quote(
        c, value=12000.0, contract_months=12, contract_start=c.today - relativedelta(months=1)
    )
    q.sudo()._guarded().write(
        {
            "state": "accepted",
            "acceptance_ref": "probe",
            "accepted_value": q.value,
            "accepted_total": q.amount_total,
        }
    )
    model, cid = q._convert()
    contract = c.env[model].browse(cid).sudo()
    contract.write({"stamp_duty_applicable": False, "stamp_duty_exemption_reason": "test"})
    contract.action_activate()
    Period = c.env["fix.contract.billing.period"].sudo()
    row = contract._fix_billing_schedule()[0]
    period = Period._period_for(contract, row)
    invoice = Period._period_invoice(contract, period)
    assert invoice._fix_quotation_for_advances() == q


# ------------------------------------------------------------- M36-F5
def test_a_declined_quotation_is_closed_out_once(c):
    q = _sent_quote(c)
    q.with_user(c.author).action_decline(reason="too dear", code="price")
    Consumers = c.env["fix.a04.quotation.consumers"].sudo()
    event = {"aggregate": "fix.quotation", "aggregate_id": q.id, "payload": {}}
    result = Consumers.consume_quotation_declined(event)
    assert result["created"]
    assert q.activity_ids.filtered(lambda a: "declined" in (a.summary or ""))
    assert q.handoff_ids.filtered(lambda h: h.kind == "task" and h.note.startswith("Declined"))
    assert Consumers.consume_quotation_declined(event)["created"] is False
    with pytest.raises(AccessError):
        c.env["fix.a04.quotation.consumers"].with_user(c.author).consume_quotation_declined(event)


def test_the_decline_consumer_refuses_a_quotation_that_is_not_declined(c):
    q = _sent_quote(c)
    with pytest.raises(UserError, match="not declined"):
        c.env["fix.a04.quotation.consumers"].sudo().consume_quotation_declined(
            {"aggregate": "fix.quotation", "aggregate_id": q.id, "payload": {}}
        )


# ------------------------------------------------------------- M36-F7
def test_an_approved_variation_amends_the_contract(c):
    t, contract = _won_tender(c)
    contract = contract.sudo()
    contract.write(
        {
            "date_start": c.today - timedelta(days=5),
            "date_end": c.today - timedelta(days=5) + relativedelta(years=1) - timedelta(days=1),
            "stamp_duty_applicable": False,
            "stamp_duty_exemption_reason": "test",
        }
    )
    contract.action_activate()
    before_term, before_total = contract.term_value, contract.accepted_total
    variation = (
        c.env["fix.tender.variation"]
        .sudo()
        .create({"name": "VO-1", "tender_id": t.id, "amount": 11500.0, "reason": "extra printers"})
    )
    variation._guarded().write({"state": "approved"})
    result = (
        c.env["fix.a04.quotation.consumers"]
        .sudo()
        .consume_tender_variation_approved(
            {"aggregate": "fix.tender.variation", "aggregate_id": variation.id, "payload": {}}
        )
    )
    amendment = c.env["fix.contract.amendment"].browse(result["id"])
    assert amendment.state == "applied" and variation.amendment_id == amendment
    assert contract.accepted_total == round(before_total + 11500.0, 2)
    # 11,500 incl. VAT is 10,000 before VAT, spread over the unbilled term
    assert abs(contract.term_value - (before_term + 10000.0)) <= 0.05


# ------------------------------------------------------------- M36-F6 bonds
def _bond_accounts(c):
    Account = c.env["account.account"]
    deposit = Account.search(
        [("account_type", "=", "asset_current"), ("company_ids", "in", c.env.company.id)], limit=1
    )
    bank = Account.search(
        [("account_type", "=", "asset_cash"), ("company_ids", "in", c.env.company.id)], limit=1
    ) or Account.search(
        [
            ("account_type", "=", "asset_current"),
            ("company_ids", "in", c.env.company.id),
            ("id", "!=", deposit.id),
        ],
        limit=1,
    )
    params = c.env["ir.config_parameter"].sudo()
    params.set_param("cd_quotation.account_code.bond_deposit", deposit.code)
    params.set_param("cd_quotation.account_code.bond_margin", deposit.code)
    params.set_param("cd_quotation.account_code.bond_funding", bank.code)
    return deposit, bank


def test_a_pay_order_emd_posts_its_deposit(c):
    deposit, bank = _bond_accounts(c)
    t = (
        c.env["fix.tender"]
        .sudo()
        .create(
            {
                "name": "B2 EMD",
                "client_name": "Ministry",
                "client_id": c.agency.id,
                "due_date": c.today + timedelta(days=10),
                "operating_unit_id": c.ou.id,
                "estimated_value": 1000000.0,
            }
        )
    )
    bond = (
        c.env["fix.tender.bond"]
        .sudo()
        .create(
            {
                "tender_id": t.id,
                "bond_type": "bid",
                "instrument": "pay_order",
                "amount": 20000.0,
                "bank": "Sonali Bank",
                "guarantee_no": "PO-1",
                "expires_on": c.today + timedelta(days=120),
            }
        )
    )
    bond.action_activate()
    move = bond.funding_move_id
    assert move, "the EMD left the bank: the GL must say so"
    dr = move.line_ids.filtered(lambda line: line.debit > 0)
    cr = move.line_ids.filtered(lambda line: line.credit > 0)
    assert dr.account_id == deposit and round(dr.debit, 2) == 20000.0
    assert cr.account_id == bank and round(cr.credit, 2) == 20000.0


def test_a_bond_posting_fails_closed_without_its_account(c):
    _bond_accounts(c)
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_quotation.account_code.bond_deposit", "NOPE-B2"
    )
    t = (
        c.env["fix.tender"]
        .sudo()
        .create(
            {
                "name": "B2 EMD2",
                "client_name": "Ministry",
                "client_id": c.agency.id,
                "due_date": c.today + timedelta(days=10),
                "operating_unit_id": c.ou.id,
                "estimated_value": 1000000.0,
            }
        )
    )
    bond = (
        c.env["fix.tender.bond"]
        .sudo()
        .create(
            {
                "tender_id": t.id,
                "bond_type": "bid",
                "instrument": "pay_order",
                "amount": 20000.0,
                "bank": "Sonali Bank",
                "guarantee_no": "PO-2",
                "expires_on": c.today + timedelta(days=120),
            }
        )
    )
    with pytest.raises(UserError, match="bond_deposit"):
        bond.action_activate()


def test_a_plain_guarantee_without_margin_posts_nothing(c):
    t = (
        c.env["fix.tender"]
        .sudo()
        .create(
            {
                "name": "B2 BG",
                "client_name": "Ministry",
                "client_id": c.agency.id,
                "due_date": c.today + timedelta(days=10),
                "operating_unit_id": c.ou.id,
                "estimated_value": 1000000.0,
            }
        )
    )
    bond = (
        c.env["fix.tender.bond"]
        .sudo()
        .create(
            {
                "tender_id": t.id,
                "bond_type": "bid",
                "amount": 20000.0,
                "bank": "Sonali Bank",
                "guarantee_no": "BG-B2",
                "expires_on": c.today + timedelta(days=120),
            }
        )
    )
    bond.action_activate()
    assert bond.state == "active" and not bond.funding_move_id


# ------------------------------------------------------------- M36-F6 retention
def test_retention_is_withheld_on_a_tender_contract_bill(c):
    t, contract = _won_tender(c)
    contract = contract.sudo()
    start = c.today - relativedelta(months=2)
    contract.write(
        {
            "date_start": start,
            "date_end": start + relativedelta(years=1) - timedelta(days=1),
            "stamp_duty_applicable": False,
            "stamp_duty_exemption_reason": "test",
        }
    )
    contract.action_activate()
    Period = c.env["fix.contract.billing.period"].sudo()
    row = contract._fix_billing_schedule()[0]
    period = Period._period_for(contract, row)
    invoice = Period._period_invoice(contract, period)
    invoice.action_issue()
    expected = round(invoice.taxable_amount * 0.10, 2)
    assert invoice.retention_withheld == expected
    assert round(invoice.amount_residual, 2) == round(invoice.total_payable - expected, 2)
    invoice.action_release_retention()
    assert round(invoice.amount_residual, 2) == round(invoice.total_payable, 2)


# ------------------------------------------------------------- wiring
def test_the_quotation_consumers_are_wired(c):
    Consumer = c.env["fix.event.consumer"].sudo()
    for event, method in (
        ("quotation.declined", "consume_quotation_declined"),
        ("tender.variation_approved", "consume_tender_variation_approved"),
    ):
        assert Consumer.search(
            [
                ("event_type", "=", event),
                ("model", "=", "fix.a04.quotation.consumers"),
                ("method", "=", method),
            ]
        )


# ------------------------------------------------------------- M36-F10
def test_the_contract_carries_the_proposed_cover(c):
    device = c.env["fix.device"].create(
        {"device_model_id": c.model.id, "serial_number": "B2Q-DEV-1", "owner_id": c.customer.id}
    )
    policy = c.env["fix.sla.policy"].search([], limit=1)
    q = _quote(
        c,
        line_ids=[
            (
                0,
                0,
                {
                    "description": "AMC printer",
                    "line_type": "recurring",
                    "unit_price": 12000.0,
                    "device_id": device.id,
                },
            )
        ],
        contract_sla_policy_ids=[(6, 0, policy.ids)],
        contract_entitlement_ids=[(0, 0, {"entitlement_type": "visits", "quantity_included": 4})],
    )
    q.sudo()._guarded().write(
        {
            "state": "accepted",
            "acceptance_ref": "probe",
            "accepted_value": q.value,
            "accepted_total": q.amount_total,
        }
    )
    q._convert()
    contract = c.env["fix.contract"].browse(q.converted_res_id)
    assert device in contract.covered_device_ids
    assert policy in contract.sla_policy_ids
    assert contract.entitlement_ids.mapped("quantity_included") == [4.0]


# ------------------------------------------------------------- M36-F14 / F15 / F17
def test_the_cost_is_the_lines_cost_at_m15(c):
    part = c.env["product.product"].create(
        {"name": "B2Q part", "lst_price": 5000.0, "standard_price": 3200.0, "type": "consu"}
    )
    q = _quote(
        c,
        line_ids=[
            (
                0,
                0,
                {"product_id": part.id, "line_type": "goods", "quantity": 2, "unit_price": 5000.0},
            )
        ],
    )
    assert q.cost_amount == 6400.0
    assert q.margin_pct == round((10000.0 - 6400.0) / 10000.0 * 100.0, 2)


def test_po_template_and_language_freeze_once_accepted(c):
    q = _quote(c)
    q.with_user(c.author).write({"customer_po_ref": "PO-1"})
    q.sudo()._guarded().write({"state": "accepted"})
    with pytest.raises(UserError, match="decided"), c.env.cr.savepoint():
        q.with_user(c.author).write({"customer_po_ref": "PO-2"})
    assert q.customer_po_ref == "PO-1"


def test_a_resent_code_does_not_reset_the_failed_attempts(c, monkeypatch):
    from odoo.addons.cd_service_order.models import fix_otp_util

    q = _sent_quote(c)
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    q.with_user(c.author).action_send_acceptance_otp()
    q.with_user(c.author).action_verify_acceptance_otp(otp="000000x")
    assert q.acceptance_otp_attempts == 1
    q.with_user(c.author).action_send_acceptance_otp()
    assert q.acceptance_otp_attempts == 1, "a resend used to give three fresh guesses"
    q.sudo()._guarded().write({"acceptance_otp_attempts": fix_otp_util.OTP_MAX_ATTEMPTS * 3})
    with pytest.raises(UserError, match="Too many"):
        q.with_user(c.author).action_send_acceptance_otp()
