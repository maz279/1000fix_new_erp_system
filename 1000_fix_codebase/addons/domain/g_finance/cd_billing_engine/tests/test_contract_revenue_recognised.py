# ruff: noqa: F811  (the imported `k` fixture is the parameter pytest injects)
"""E3-03 (E2E rehearsal on a fix_real copy, 11 Nov 2026): an AMC period billed
in arrears was issued to deferred revenue and never reached revenue. Nothing
created the recognition schedule M53's cron draws down.

The issue posting now creates it (cd_subscription.fix_invoice_deferral):
the liability it credited, over the billed period, against the contract.
"""

import pytest
from odoo.addons.cd_billing_engine.tests.test_a04_c10_contract_walker import (  # noqa: F401
    _active,
    _invoices,
    _on,
    _walk,
    k,
)

pytestmark = [pytest.mark.financial]


def _issued_period_invoice(k, timing="advance"):
    """A04 ERP audit M08-F5: only a period billed IN ADVANCE is a contract
    liability recognised over the period; a period billed in arrears is
    already earned when it is invoiced (it credits revenue, no schedule)."""
    if "fix.revenue.schedule" not in k.env:
        pytest.skip("cd_subscription (M53 recognition) not installed")
    _on(k)
    contract = _active(k, billing_timing=timing)
    assert _walk(k) == (3 if timing == "advance" else 2)
    invoice = _invoices(k, contract)[0]
    invoice.sudo().action_issue()
    assert invoice.state != "draft"
    assert invoice.posted_move_id, invoice.gl_note
    return contract, invoice


def _schedule(k, invoice):
    return (
        k.env["fix.revenue.schedule"]
        .sudo()
        .search([("source_model", "=", "fix.ar.invoice"), ("source_id", "=", invoice.id)])
    )


def test_issuing_a_contract_period_creates_its_recognition_schedule(k):
    contract, invoice = _issued_period_invoice(k)
    schedule = _schedule(k, invoice)
    assert len(schedule) == 1
    period = k.env["fix.contract.billing.period"].sudo().browse(invoice.source_id)
    assert schedule.contract_id == contract
    assert schedule.total_amount == pytest.approx(invoice.total_payable - invoice.vat_amount)
    assert (schedule.start_date, schedule.end_date) == (period.period_start, period.period_end)
    assert schedule.state == "active"
    assert schedule._recognition_refusal() is None


def test_an_ended_period_is_recognised_in_full_by_the_daily_run(k):
    _contract, invoice = _issued_period_invoice(k)
    schedule = _schedule(k, invoice)
    k.env["fix.revenue.schedule"]._cron_recognize()
    schedule.invalidate_recordset()
    assert schedule.recognized_amount == pytest.approx(schedule.total_amount)
    assert schedule.deferred_balance == pytest.approx(0.0)
    assert schedule.state == "complete"
    line = schedule.line_ids
    assert line.move_id.state == "posted"
    assert (
        line.move_id.line_ids.filtered(lambda ml: ml.credit > 0).account_id
        != line.move_id.line_ids.filtered(lambda ml: ml.debit > 0).account_id
    )


def test_an_arrears_period_is_earned_at_issue_and_never_deferred(k):
    """M08-F5: the walker bills arrears periods once served, so their issue
    credits the family's revenue account and M53 schedules no deferral."""
    _contract, invoice = _issued_period_invoice(k, timing="arrears")
    assert invoice._revenue_role() == "revenue" and invoice.revenue_account_id
    assert not _schedule(k, invoice)
    credit = invoice.posted_move_id.line_ids.filtered(lambda ml: ml.credit > 0)
    assert invoice.revenue_account_id in credit.mapped("account_id")


def test_the_schedule_is_created_once(k):
    _contract, invoice = _issued_period_invoice(k)
    first = _schedule(k, invoice)
    again = invoice._fix_schedule_deferral()
    assert again == first
    assert len(_schedule(k, invoice)) == 1


# ---- /p03/gl/recon (E2E3 F4 / D3-16) ------------------------------------------
def _recon(env):
    import types

    import odoo.addons.cd_p03_portal.controllers.p03_gl_api as gl

    ctl = gl.P03GlApiController()
    old = getattr(gl, "request", None)
    gl.request = types.SimpleNamespace(env=env)
    try:
        f = gl.P03GlApiController.gl_recon
        return getattr(f, "original_endpoint", f)(ctl)
    finally:
        gl.request = old


def test_recon_counts_what_issued_invoices_still_owe_never_drafts(k):
    if "fix.revenue.schedule" not in k.env:
        pytest.skip("cd_subscription not installed")
    _on(k)
    contract = _active(k)
    _walk(k)
    issued, draft = _invoices(k, contract)
    issued.sudo().action_issue()
    env = k.env
    (row,) = [r for r in _recon(env)["rows"] if r["label"].startswith("AR")]
    expected = sum(
        env["fix.ar.invoice"]
        .sudo()
        .search([("state", "not in", ("draft", "cancelled")), ("company_id", "=", env.company.id)])
        .mapped("amount_residual")
    )
    assert row["breakdown"]["open_invoices"] == pytest.approx(round(expected, 2))
    assert draft.state == "draft"
    assert issued.amount_residual > 0
    assert row["status"] in ("matched", "variance")  # configured: never "not_configured"


def test_recon_falls_back_to_the_posting_control_account(k):
    import odoo.addons.cd_p03_portal.controllers.p03_gl_api as gl

    env = k.env
    ar = env["account.account"].search(
        [("account_type", "=", "asset_receivable"), ("company_ids", "in", env.company.id)],
        limit=1,
    )
    env["ir.config_parameter"].sudo().set_param("cd_billing_engine.account_code.ar", ar.code)
    control = gl.P03GlApiController._posting_control(env, env.company, "receivable")
    assert control.odoo_account_id == ar
    assert control.account_code == ar.code
    vat = env["account.account"].search(
        [("account_type", "=", "liability_current"), ("company_ids", "in", env.company.id)],
        limit=1,
    )
    env["ir.config_parameter"].sudo().set_param(
        "cd_billing_engine.account_code.vat_output", vat.code
    )
    assert gl.P03GlApiController._posting_control(env, env.company, "tax").odoo_account_id == vat
    assert gl.P03GlApiController._posting_control(env, env.company, "no such ledger") is None
