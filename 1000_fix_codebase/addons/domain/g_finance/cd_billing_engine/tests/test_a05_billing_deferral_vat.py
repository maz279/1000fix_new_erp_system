"""A05 ERP audit, stream S4 — the billing engine side (live ORM, rolled back).

FIN-14 / M13-17  An invoice line earned over a service period, raised for a
                 source that opts in (`_fix_defer_revenue = True`), is
                 deferred at issue (contract liability) and released
                 straight-line by day over the period; a credit note releases
                 its share at once, a cancellation releases the rest; lines
                 without a period (a late fee) stay recognised at issue.
FIN-26           A 0% / exempt invoice posts no zero-value VAT output line
                 (nor do its credit note and cancellation mirrors).
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_billing_engine.tests.test_ar_engine_orm import _gl_company
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]


def _balance(env, account):
    env.flush_all()
    lines = env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("debit")) - sum(lines.mapped("credit")), 2)


def _dhaka_today(env):
    return fields.Date.context_today(env["fix.ar.invoice"].with_context(tz="Asia/Dhaka"))


@pytest.fixture
def shop(odoo_env, monkeypatch):
    shop = _gl_company(odoo_env, "a05s4")
    shop.rental_income = (
        shop.env["account.account"]
        .with_company(shop.company)
        .create(
            {
                "name": "Rental Service Income (test)",
                "code": "A5S4RI",
                "account_type": "income",
                "company_ids": [(6, 0, shop.company.ids)],
            }
        )
    )
    # the rental source opts in; here a partner record stands for it
    shop.source_class = type(shop.env["res.partner"])
    monkeypatch.setattr(shop.source_class, "_fix_defer_revenue", True, raising=False)
    shop.monkeypatch = monkeypatch
    return shop


def _rental_invoice(shop, hire=3000.0, late_fee=0.0, run_days=10, term=30):
    start = _dhaka_today(shop.env) - timedelta(days=run_days - 1)
    end = start + timedelta(days=term - 1)
    lines = [
        {
            "description": "Rental hire",
            "taxable_amount": hire,
            "service_period_start": start,
            "service_period_end": end,
        }
    ]
    if late_fee:
        lines.append({"description": "Late fee", "taxable_amount": late_fee})
    source = shop.env["res.partner"].create({"name": "Rental source"})
    invoice = shop.env["fix.ar.invoice"]._fix_ar_invoice_from_source(
        source,
        shop.customer,
        lines,
        "Rental R/A05",
        credit_account=shop.rental_income,
        operating_unit=shop.ou,
        branch=shop.branch,
    )
    return invoice, start, end


# ------------------------------------------------------------------ FIN-14
def test_fin14_period_line_deferred_and_released_straight_line(shop):
    deferred = shop.accounts["deferred_revenue"]
    invoice, _start, end = _rental_invoice(shop, hire=3000.0, late_fee=500.0)
    assert invoice.state == "issued" and invoice.posted_move_id
    deferral = invoice.revenue_deferral_ids
    assert len(deferral) == 1 and deferral.amount == 3000.0
    # 10 of 30 days have run: 1,000 earned; the late fee is earned at issue
    assert deferral.released_amount == 1000.0 and deferral.balance == 2000.0
    assert _balance(shop.env, shop.rental_income) == -1500.0
    assert _balance(shop.env, deferred) == -2000.0
    # a re-run on the same day releases nothing more
    deferral._fix_release()
    assert _balance(shop.env, shop.rental_income) == -1500.0
    # at the end of the period all of it is revenue, once
    deferral._fix_release(as_of=end)
    deferral._fix_release(as_of=end + timedelta(days=5))
    assert _balance(shop.env, shop.rental_income) == -3500.0
    assert _balance(shop.env, deferred) == 0.0
    assert deferral.state == "done"


def test_fin14_daily_job_releases_up_to_today(shop):
    invoice, start, _end = _rental_invoice(shop, hire=3000.0, run_days=1)
    deferral = invoice.revenue_deferral_ids
    assert deferral.released_amount == 100.0  # day 1 of 30
    shop.env["fix.ar.revenue.deferral"]._cron_release()
    assert deferral.released_amount == 100.0


def test_fin14_no_opt_in_means_no_deferral(shop):
    shop.monkeypatch.setattr(shop.source_class, "_fix_defer_revenue", False)
    invoice, _s, _e = _rental_invoice(shop, hire=3000.0)
    assert not invoice.revenue_deferral_ids
    assert _balance(shop.env, shop.rental_income) == -3000.0


def test_fin14_cancel_nets_revenue_and_liability_to_zero(shop):
    deferred = shop.accounts["deferred_revenue"]
    invoice, _s, _e = _rental_invoice(shop, hire=3000.0)
    invoice.action_cancel(reason="booking cancelled")
    assert invoice.state == "cancelled"
    assert _balance(shop.env, shop.rental_income) == 0.0
    assert _balance(shop.env, deferred) == 0.0
    assert invoice.revenue_deferral_ids.state == "cancelled"


def test_fin14_credit_note_releases_its_share(shop):
    deferred = shop.accounts["deferred_revenue"]
    invoice, _s, end = _rental_invoice(shop, hire=3000.0)
    note = shop.env["fix.credit.note"].create(
        {
            "operating_unit_id": shop.ou.id,
            "invoice_id": invoice.id,
            "amount": 345.0,  # 300 + VAT 45
            "reason_code": "service_failure",
        }
    )
    note.action_submit()
    note.action_approve()
    note.action_issue()
    deferral = invoice.revenue_deferral_ids
    assert deferral.credited_amount == 300.0
    deferral._fix_release(as_of=end)
    assert _balance(shop.env, deferred) == 0.0
    assert _balance(shop.env, shop.rental_income) == -2700.0


def test_fin14_no_contract_liability_account_refuses_the_issue(shop):
    shop.env["ir.config_parameter"].sudo().set_param(
        "cd_billing_engine.account_code.deferred_revenue", "A5S4-NONE"
    )
    with pytest.raises(UserError, match="deferred_revenue"), shop.env.cr.savepoint():
        _rental_invoice(shop, hire=3000.0)


def test_fin14_period_must_have_both_ends_in_order(shop):
    invoice, start, _e = _rental_invoice(shop, hire=100.0)
    Line = shop.env["fix.ar.invoice.line"].sudo()
    with pytest.raises(Exception, match="service period"), shop.env.cr.savepoint():
        Line.create(
            {
                "invoice_id": invoice.id,
                "description": "bad",
                "taxable_amount": 10.0,
                "service_period_start": start,
                "service_period_end": start - timedelta(days=1),
            }
        )


# ------------------------------------------------------------------ FIN-26
def _exempt_code(shop):
    row = shop.env["fix.vat.treatment"].create(
        {"code": "A5S4-EXEMPT", "name": "Exempt supply", "treatment_type": "exempt", "rate": 0.0}
    )
    if row.state != "active":
        row.sudo()._guarded().write({"state": "active"})
    return row.code


def test_fin26_zero_vat_invoice_posts_no_vat_line(shop):
    shop.monkeypatch.setattr(shop.source_class, "_fix_defer_revenue", False)
    vat = shop.accounts["vat_output"]
    source = shop.env["res.partner"].create({"name": "Exempt source"})
    invoice = shop.env["fix.ar.invoice"]._fix_ar_invoice_from_source(
        source,
        shop.customer,
        [
            {
                "description": "Exempt service",
                "taxable_amount": 800.0,
                "vat_treatment_code": _exempt_code(shop),
            }
        ],
        "A05 exempt",
        operating_unit=shop.ou,
        branch=shop.branch,
    )
    assert invoice.vat_amount == 0.0 and invoice.posted_move_id
    move_lines = invoice.posted_move_id.line_ids
    assert vat not in move_lines.mapped("account_id")
    assert all(ln.debit or ln.credit for ln in move_lines)
    # the cancellation mirror carries no zero VAT line either
    before = shop.env["account.move"].search([("company_id", "=", shop.company.id)])
    invoice.action_cancel(reason="raised in error")
    mirror = shop.env["account.move"].search([("company_id", "=", shop.company.id)]) - before
    assert mirror and vat not in mirror.line_ids.mapped("account_id")
    assert _balance(shop.env, vat) == 0.0
