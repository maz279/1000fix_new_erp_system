"""Owner decisions of 12 Nov 2026 on the third E2E rehearsal (E2E3_REPORT.md).

C8 (D2-11)   A statutory invoice dated on or before the lock date is refused at
             issue: issued after the October close, an invoice dated 25 Oct
             posted its GL on 11 Nov but kept a Mushak 6.3 dated 25 Oct, so
             the 9.1 could reconcile in neither month.
C11 (D-12)   Invoice issue and its reversals post on the company's Sales
             journal (fix_real: INV), not the first general journal (MISC);
             receipts and write-offs keep the general journal.
D3-01 (E3-01) An invoice from a closed service order whose amount differs from
             the customer's ACCEPTED quotation is refused until the customer
             re-accepts (QTN/2026/00012 accepted 4,025.00 was invoiced at
             4,945.00 after a revision, without consent).

Runs on private companies (``_gl_company``) inside the rolled-back odoo_env.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_billing_engine.tests.test_ar_engine_orm import (
    JOB,
    _closed_order,
    _gl_company,
)
from odoo.exceptions import UserError
from odoo.fields import Datetime

pytestmark = [pytest.mark.financial]

PARAM_INVOICE_JOURNAL = "cd_billing_engine.journal_code.invoice"


def _today(shop):
    return fields.Date.context_today(shop.env["fix.ar.invoice"])


def _month_closed(shop):
    """Lock the company's books through the end of last month, as the period
    close does (fix.period.close._fix_set_company_lock)."""
    lock = fields.Date.start_of(_today(shop), "month") - timedelta(days=1)
    shop.company.sudo().write({"fiscalyear_lock_date": lock})
    return lock


def _sales_journal(shop, code="INV", name="Sales"):
    return shop.env["account.journal"].create(
        {"name": name, "code": code, "type": "sale", "company_id": shop.company.id}
    )


def _manual(shop, invoice_date, taxable=2000.0):
    return shop.env["fix.ar.invoice"].create_manual_invoice(
        {
            "customer_id": shop.customer.id,
            "operating_unit_id": shop.ou.id,
            "invoice_date": invoice_date,
        },
        [
            {
                "description": "Exception job",
                "taxable_amount": taxable,
                "vat_amount": round(taxable * 0.15, 2),
                "line_total": round(taxable * 1.15, 2),
            }
        ],
        reason_code="E3 rehearsal back-dated job",
    )


# ------------------------------------------------------------------ C8
class TestBackDatedStatutoryInvoice:
    def test_an_invoice_dated_in_a_locked_period_is_refused_at_issue(self, odoo_env):
        shop = _gl_company(odoo_env, "c8lock")
        lock = _month_closed(shop)
        invoice = _manual(shop, lock - timedelta(days=6))  # "25 Oct", October locked
        mushak_before = shop.env["fix.mushak.register"].search_count(
            [("company_id", "=", shop.company.id)]
        )
        with pytest.raises(UserError, match="lock date") as refused, odoo_env.cr.savepoint():
            invoice.action_issue()
        assert "re-date" in str(refused.value).lower()
        invoice.invalidate_recordset()
        assert invoice.state == "draft" and invoice.name in (False, "New", "/")
        assert not invoice.mushak_id and not invoice.posted_move_id
        assert (
            shop.env["fix.mushak.register"].search_count([("company_id", "=", shop.company.id)])
            == mushak_before
        )

    def test_the_lock_date_itself_is_closed(self, odoo_env):
        shop = _gl_company(odoo_env, "c8edge")
        lock = _month_closed(shop)
        invoice = _manual(shop, lock)
        with pytest.raises(UserError, match="lock date"), odoo_env.cr.savepoint():
            invoice.action_issue()

    def test_re_dated_into_the_open_period_it_issues_and_6_3_matches_gl(self, odoo_env):
        shop = _gl_company(odoo_env, "c8redate")
        lock = _month_closed(shop)
        invoice = _manual(shop, lock - timedelta(days=6))
        with pytest.raises(UserError, match="lock date"), odoo_env.cr.savepoint():
            invoice.action_issue()
        invoice.write({"invoice_date": lock + timedelta(days=1)})
        invoice.action_issue()
        assert invoice.state == "issued"
        assert invoice.mushak_id.invoice_date == invoice.invoice_date
        assert invoice.posted_move_id.date == invoice.invoice_date

    def test_the_contract_draft_path_is_refused_too(self, odoo_env):
        """_fix_draft_invoice_from_source drafts (contract / OEM claim) are
        issued through the same action_issue."""
        shop = _gl_company(odoo_env, "c8src")
        lock = _month_closed(shop)
        invoice = shop.env["fix.ar.invoice"]._fix_draft_invoice_from_source(
            "e3.test.source",
            "E3-C8-1",
            shop.customer,
            [{"description": "AMC October", "taxable_amount": 1000.0}],
            "E3 contract period",
            company=shop.company,
            operating_unit=shop.ou,
            invoice_date=lock - timedelta(days=3),
        )
        with pytest.raises(UserError, match="lock date"), odoo_env.cr.savepoint():
            invoice.action_issue()

    def test_an_open_period_back_date_still_issues(self, odoo_env):
        """No lock covers the date: today's behaviour (the 6.3 and GL both
        carry the invoice date)."""
        shop = _gl_company(odoo_env, "c8open")
        invoice = _manual(shop, _today(shop) - timedelta(days=40))
        invoice.action_issue()
        assert invoice.state == "issued"
        assert invoice.posted_move_id.date == invoice.invoice_date


# ------------------------------------------------------------------ C11
class TestSalesJournal:
    def test_issue_posts_on_the_sales_journal_not_misc(self, odoo_env):
        shop = _gl_company(odoo_env, "c11iss")
        sales = _sales_journal(shop)
        order = _closed_order(shop, JOB)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        assert invoice.posted_move_id.journal_id == sales
        assert shop.journal.type == "general"  # the MISC journal it used to take

    def test_the_parameter_names_the_journal(self, odoo_env):
        shop = _gl_company(odoo_env, "c11par")
        _sales_journal(shop, "SAL1", "Sales one")
        chosen = _sales_journal(shop, "SAL2", "Sales two")
        odoo_env["ir.config_parameter"].sudo().set_param(PARAM_INVOICE_JOURNAL, "SAL2")
        invoice = _manual(shop, _today(shop))
        invoice.action_issue()
        assert invoice.posted_move_id.journal_id == chosen

    def test_without_a_sales_journal_the_general_fallback_holds(self, odoo_env):
        shop = _gl_company(odoo_env, "c11fb")
        order = _closed_order(shop, JOB)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        assert invoice.posted_move_id.journal_id == shop.journal

    def test_credit_note_and_cancel_reverse_on_the_sales_journal(self, odoo_env):
        shop = _gl_company(odoo_env, "c11rev")
        sales = _sales_journal(shop)
        order = _closed_order(shop, JOB)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        note = shop.env["fix.credit.note"].create(
            {
                "operating_unit_id": shop.ou.id,
                "invoice_id": invoice.id,
                "amount": 115.0,
                "reason_code": "service_failure",
            }
        )
        note.action_submit()
        note.action_approve()
        note.action_issue()
        assert note.posted_move_id.journal_id == sales

        order2 = _closed_order(shop, JOB)
        invoice2 = shop.env["fix.ar.invoice"].from_closed_service_order(order2, Datetime.now())
        before = shop.env["account.move"].search([("company_id", "=", shop.company.id)])
        invoice2.action_cancel(reason="duplicate issuance")
        mirror = shop.env["account.move"].search([("company_id", "=", shop.company.id)]) - before
        assert len(mirror) == 1 and mirror.journal_id == sales

    def test_receipts_and_write_offs_keep_the_general_journal(self, odoo_env):
        shop = _gl_company(odoo_env, "c11keep")
        _sales_journal(shop)
        order = _closed_order(shop, JOB)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        receipt = shop.env["fix.ar.receipt"].create(
            {"customer_id": shop.customer.id, "amount": 500.0, "method": "bkash"}
        )
        receipt.action_confirm()
        assert receipt.posted_move_id.journal_id == shop.journal
        request = invoice.action_write_off(reason="uncollectable", recovery_history="calls")
        request.action_approve()
        assert request.move_id.journal_id == shop.journal


# ------------------------------------------------------------------ D3-01
def _accepted_quotation(shop, order, value=None):
    """The customer's accepted service quotation on the order's approved
    estimate, as the trusted acceptance path leaves it."""
    estimate = order.estimate_ids.filtered(lambda e: e.state == "approved")[:1]
    quotation = (
        shop.env["fix.quotation"]
        .sudo()
        .create(
            {
                "customer_id": order.customer_id.id,
                "estimate_id": estimate.id,
                "company_id": shop.company.id,
                "quote_type": "service",
                "value": estimate.grand_total,
                "cost_amount": 100.0,
            }
        )
    )
    quotation._guarded().write(
        {
            "state": "accepted",
            "accepted_at": fields.Datetime.now(),
            "accepted_value": estimate.grand_total if value is None else value,
            "service_order_id": order.id,
        }
    )
    return quotation


def _revise(order, unit_price):
    """A revision after acceptance: v2 at a new price, approved."""
    old = order.estimate_ids.filtered(lambda e: e.state == "approved")[:1]
    old._guarded().write({"state": "rejected"})
    return order.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "version": old.version + 1,
            "state": "approved",
            "discount": 0.0,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "Labour (revised)",
                        "quantity": 1.0,
                        "unit_price": unit_price,
                        "line_type": "labour",
                    },
                )
            ],
        }
    )


class TestAcceptedQuotationBindsTheInvoice:
    def test_a_revision_after_acceptance_is_not_invoiced(self, odoo_env):
        """Q5: accepted 4,025.00, revised to 4,945.00 below the BDT 5,000
        consent threshold, invoiced at 4,945.00 with no consent."""
        shop = _gl_company(odoo_env, "d301rev")
        order = _closed_order(shop, [(None, "Labour", 1.0, 3500.0, "labour")])  # 4,025.00
        quotation = _accepted_quotation(shop, order)
        assert round(quotation.accepted_value, 2) == 4025.00
        _revise(order, 4300.0)  # 4,945.00
        Invoice = shop.env["fix.ar.invoice"]
        with pytest.raises(UserError, match="accepted") as refused, odoo_env.cr.savepoint():
            Invoice.from_closed_service_order(order, Datetime.now())
        assert "4025.00" in str(refused.value).replace(",", "")
        assert "4945.00" in str(refused.value).replace(",", "")
        assert not Invoice.search(
            [("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)]
        )

    def test_re_acceptance_at_the_new_value_releases_the_invoice(self, odoo_env):
        shop = _gl_company(odoo_env, "d301re")
        order = _closed_order(shop, [(None, "Labour", 1.0, 3500.0, "labour")])
        first = _accepted_quotation(shop, order)
        first.accepted_at = fields.Datetime.now() - timedelta(days=1)
        _revise(order, 4300.0)
        _accepted_quotation(shop, order)  # the customer re-accepts 4,945.00
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        assert round(invoice.total_payable, 2) == 4945.00

    def test_an_unrevised_accepted_quotation_invoices_as_accepted(self, odoo_env):
        shop = _gl_company(odoo_env, "d301ok")
        order = _closed_order(shop, [(None, "Labour", 1.0, 3500.0, "labour")])
        _accepted_quotation(shop, order)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        assert round(invoice.total_payable, 2) == 4025.00

    def test_no_accepted_quotation_keeps_todays_behaviour(self, odoo_env):
        shop = _gl_company(odoo_env, "d301none")
        order = _closed_order(shop, [(None, "Labour", 1.0, 3500.0, "labour")])
        _revise(order, 4300.0)
        invoice = shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())
        assert round(invoice.total_payable, 2) == 4945.00
