"""A04 §7.10 item 4 (2026-11-04): the C10 contract billing walker.

working/A04_Workflow_and_Approval_Report.md: fix.contract carried
_fix_billing_schedule() and mark_billed_through() as service APIs, but
nothing between them and M20 - no contract period ever reached the AR
ledger. This suite proves the bridge: due periods of an in-force contract
become DRAFT invoices (VAT by M51's determination, one per period,
idempotent), the billed-through date advances, and the freeze it drives is
the one the C2-C13 amendment controls enforce.

The contract world (officer, clerk, customer, an activated contract) is
built here rather than imported: cd_contract_core's ``c`` fixture lives in
its test module, not a conftest. ``odoo_env`` rolls back after each test.
"""

import types
import uuid
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

import pytest
from odoo import fields
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import AccessError, UserError

TAG = uuid.uuid4().hex[:6].upper()
SWITCH = "cd_billing_engine.contract_auto_billing"
TWO = Decimal("0.01")


@pytest.fixture
def k(odoo_env):
    env = odoo_env
    ns = types.SimpleNamespace(env=env)
    ns.today = fields.Date.context_today(env["fix.contract"])
    ns.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    ids = [env.ref("base.group_user").id]
    ns.officer = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a4c10 officer",
                "login": "a4c10_officer_%s" % TAG,
                "group_ids": [
                    (6, 0, [*ids, env.ref("cd_contract_core.group_contract_officer").id])
                ],
                "assigned_operating_unit_ids": [(6, 0, ns.ou.ids)],
                "default_operating_unit_id": ns.ou.id,
            }
        )
    )
    ns.clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a4c10 clerk",
                "login": "a4c10_clerk_%s" % TAG,
                "group_ids": [(6, 0, ids)],
                "assigned_operating_unit_ids": [(6, 0, ns.ou.ids)],
                "default_operating_unit_id": ns.ou.id,
            }
        )
    )
    ns.customer = env["res.partner"].create(
        {"name": "A04C10 Customer %s" % TAG, "phone": "01711000910"}
    )
    return ns


def _active(k, value=120000.0, start_days_ago=65, **kw):
    """An in-force contract (the superuser stands in for one approved and
    signed earlier), backdated far enough that its first two 30-day billing
    periods have ended and the third is still running."""
    vals = {
        "name": "A04C10 AMC",
        "family": "amc",
        "customer_id": k.customer.id,
        "operating_unit_id": k.ou.id,
        "date_start": k.today - timedelta(days=start_days_ago),
        "date_end": k.today + timedelta(days=300),
        "annual_value": value,
        "stamp_duty_cert_no": "SD-%s" % TAG,
        "stamp_duty_amount": 300.0,
        "has_signed_contract_doc": True,
    }
    vals.update(kw)
    contract = k.env["fix.contract"].with_user(k.officer).create(vals)
    contract.sudo().action_activate()
    contract.invalidate_recordset()
    assert contract.state == "active"
    return contract


def _walk(k):
    return k.env["fix.contract.billing.period"].sudo().cron_bill_contracts()


def _on(k):
    k.env["ir.config_parameter"].sudo().set_param(SWITCH, "1")


def _periods(k, contract):
    return (
        k.env["fix.contract.billing.period"]
        .sudo()
        .search([("contract_id", "=", contract.id)], order="period_start")
    )


def _invoices(k, contract):
    periods = _periods(k, contract)
    return (
        k.env["fix.ar.invoice"]
        .sudo()
        .search(
            [
                ("source_model", "=", "fix.contract.billing.period"),
                ("source_id", "in", periods.ids),
            ],
            order="id",
        )
    )


def _determined(period, on_date):
    """What M51 says for one AMC line of this period on the invoice date (the
    walker must carry the determination, never a local VAT constant)."""
    determination = period.env["fix.vat.treatment"]._fix_determine_tax(
        [
            tax_logic.TaxLine(
                product_code="AMC",
                qty=Decimal("1"),
                unit_price=Decimal(str(period.amount)).quantize(TWO, ROUND_HALF_UP),
            )
        ],
        on_date=on_date,
        company=period.contract_id.company_id,
    )
    det = determination.lines[0]
    return float(det.taxable_amount), float(det.vat_amount), float(det.line_total)


# ---------------------------------------------------------------- wiring


def test_the_cron_row_is_wired(k):
    cron = k.env.ref("cd_billing_engine.ir_cron_contract_billing")
    assert cron.active
    assert cron.model_id.model == "fix.contract.billing.period"
    assert "cron_bill_contracts()" in cron.code


def test_the_walker_is_off_until_finance_switches_it_on(k):
    contract = _active(k)
    assert _walk(k) == 0
    assert not _periods(k, contract)
    assert not _invoices(k, contract)
    assert contract.billed_through_date is False


# ---------------------------------------------------------------- the walk


def test_due_periods_raise_draft_invoices_and_advance_billed_through(k):
    _on(k)
    contract = _active(k)
    schedule = contract._fix_billing_schedule()
    due = [row for row in schedule if row["period_end"] <= k.today]
    assert len(due) == 2, "the fixture must leave exactly two ended periods"

    assert _walk(k) == 2
    periods = _periods(k, contract)
    invoices = _invoices(k, contract)
    assert len(periods) == len(invoices) == 2
    assert contract.billed_through_date == max(row["period_end"] for row in due)

    for period, invoice in zip(periods, invoices, strict=True):
        assert period.invoice_id == invoice
        assert invoice.state == "draft"  # issue (Mushak, number, GL) stays finance's
        assert invoice.customer_id == contract.customer_id
        assert invoice.currency_id == contract.currency_id
        assert invoice.company_id == contract.company_id
        assert (invoice.source_model, invoice.source_id) == (period._name, period.id)
        # E3-04 (third rehearsal): billed in arrears, the invoice is dated at
        # the period END. It used to be the period START, which put the GL
        # entry and the Mushak 6.3 of an invoice issued on 11 Nov into October.
        assert invoice.invoice_date == period.period_end
        assert contract.code in (invoice.manual_reason or "")
        # A04 ERP audit M08-F5: billed in arrears, the period is earned when it
        # is invoiced: it credits the family's revenue account, not the
        # contract liability (advance billing stays deferred).
        assert invoice.revenue_account_id
        assert invoice._revenue_role() == "revenue"
        expected = _determined(period, invoice.invoice_date)
        (line,) = invoice.line_ids
        assert (
            round(line.taxable_amount, 2),
            round(line.vat_amount, 2),
            round(line.line_total, 2),
        ) == tuple(round(part, 2) for part in expected)
        assert str(period.period_start) in line.description


def test_a_period_ending_in_a_locked_month_is_dated_in_the_open_period(k):
    """E3-04 with C8: once the month the period ended in is closed, the
    arrears invoice is dated on the first open day after the lock - never
    inside the closed period, where action_issue would refuse it."""
    _on(k)
    contract = _active(k)
    lock = fields.Date.start_of(k.today, "month") - timedelta(days=1)
    contract.company_id.sudo().write({"fiscalyear_lock_date": lock})
    assert _walk(k) == 2
    periods = _periods(k, contract)
    assert any(p.period_end <= lock for p in periods), "one period must end in the locked month"
    for period in periods:
        invoice = period.invoice_id
        assert invoice.invoice_date == max(period.period_end, lock + timedelta(days=1))
        assert invoice.invoice_date > lock
        invoice.action_issue()  # issues: the date is open (C8)
        assert invoice.mushak_id.invoice_date == invoice.invoice_date


def test_a_rerun_raises_nothing(k):
    _on(k)
    contract = _active(k)
    assert _walk(k) == 2
    assert _walk(k) == 0  # one period, one invoice - the UNIQUE keys back it
    assert len(_periods(k, contract)) == len(_invoices(k, contract)) == 2


def test_a_walked_period_freezes_amendments(k):
    """End-to-end C2-C13 tie-in: the walker advances the billed-through
    date, so an amendment cannot take effect inside a billed period. The
    fixture backdates the term so the second calendar-month period ends exactly
    today - today itself is then billed, and an amendment effective today
    (the earliest the backdate guard allows) is refused."""
    _on(k)
    # A04 ERP audit M08-F6: calendar-month periods - the second one ends today
    # when the term started two months ago tomorrow
    from dateutil.relativedelta import relativedelta

    start = k.today - relativedelta(months=2) + timedelta(days=1)
    contract = _active(k, start_days_ago=(k.today - start).days)
    assert _walk(k) == 2
    assert contract.billed_through_date == k.today
    amendment = (
        k.env["fix.contract.amendment"]
        .with_user(k.officer)
        .create(
            {
                "name": "price cut today",
                "contract_id": contract.id,
                "kind": "pricing",
                "delta_value": -10000.0,
                "effective_from": k.today,
            }
        )
    )
    with pytest.raises(UserError, match="billed through"):
        amendment.action_request_approval(justification="renegotiated")


def test_a_suspended_contract_is_not_billed(k):
    _on(k)
    contract = _active(k)
    contract.sudo()._guarded().write({"state": "suspended"})
    assert _walk(k) == 0
    assert not _periods(k, contract)
    assert not _invoices(k, contract)


def test_a_contract_not_in_force_is_not_billed(k):
    _on(k)
    contract = _active(k)
    contract.sudo()._guarded().write({"state": "terminated"})
    other = (
        k.env["fix.contract"]
        .with_user(k.officer)
        .create(
            {
                "name": "A04C10 draft",
                "family": "amc",
                "customer_id": k.customer.id,
                "operating_unit_id": k.ou.id,
                "date_start": k.today - timedelta(days=65),
                "date_end": k.today + timedelta(days=300),
                "annual_value": 120000.0,
            }
        )
    )
    assert other.state == "draft"
    assert _walk(k) == 0
    assert not _periods(k, contract) and not _periods(k, other)


def test_only_the_hand_off_runs_the_walker(k):
    contract = _active(k)
    walker = k.env["fix.contract.billing.period"].with_user(k.clerk)
    with pytest.raises(AccessError, match="hand-off"):
        walker.cron_bill_contracts()
    assert not _periods(k, contract)
