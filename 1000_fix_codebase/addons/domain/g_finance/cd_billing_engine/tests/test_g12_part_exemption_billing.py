"""G12 (owner decision 12 Nov 2026): the customer is never billed for a part
that was never fitted.

An APPROVED "billed part not fitted" exemption (fix.so.part.exemption,
cd_service_order) on a part line of the order's approved estimate:

* before the invoice: ``from_closed_service_order`` leaves the exempted
  quantity off the invoice, and D3-01 accepts an invoice lower than the
  customer's accepted quotation by EXACTLY the approved exemptions (any other
  difference is still refused);
* after the invoice: approving it raises an M20 credit note for that part
  through the credit-note API (``fix.credit.note._fix_request_credit``),
  which then runs its own approval ladder.

The routing (who raises, who decides) is tested in cd_service_order
(test_g12_part_exemption). Here the decision is the trusted service path, as
in the sibling D3-01 suite: private companies inside the rolled-back odoo_env.
"""

from __future__ import annotations

import pytest
from odoo.addons.cd_billing_engine.tests.test_ar_engine_orm import _closed_order, _gl_company
from odoo.addons.cd_billing_engine.tests.test_e3_finance_controls import _accepted_quotation
from odoo.exceptions import UserError
from odoo.fields import Datetime

pytestmark = [pytest.mark.financial]


def _part_order(shop, qty=2.0, price=1000.0, discount=0.0):
    """A closed order billing `qty` x `price` of a part plus BDT 500 labour."""
    order = _closed_order(
        shop,
        [
            (shop.lcd, "LCD panel", qty, price, "part"),
            (None, "Labour", 1.0, 500.0, "labour"),
        ],
    )
    if discount:
        est = order.estimate_ids[:1]
        est.sudo()._guarded().write({"discount": discount})
    return order


def _part_line(order):
    est = order.estimate_ids.filtered(lambda e: e.state == "approved")[:1]
    return est.line_ids.filtered(lambda line: line.line_type == "part")[:1]


def _branch_manager(order):
    """A Tier-2 holder in the order's private company, so the request routes."""
    env = order.env
    company = order.company_id
    login = "g12.bm.%s@g12.test" % company.id
    user = env["res.users"].search([("login", "=", login)])
    if not user:
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "G12 BM %s" % company.id,
                    "login": login,
                    "company_id": company.id,
                    "company_ids": [(6, 0, company.ids)],
                    "group_ids": [
                        (
                            6,
                            0,
                            [
                                env.ref("base.group_user").id,
                                env.ref("cd_entity_config.group_dofa_tier_2").id,
                            ],
                        )
                    ],
                }
            )
        )
    return user


def _exempt(order, qty, approve=True):
    _branch_manager(order)
    ex = order.action_request_part_exemption(
        _part_line(order).id, qty, "customer_declined", "customer declined the LCD on the bench"
    )
    if approve:
        # the trusted decision path (the inbox routing is cd_service_order's test)
        ex.action_apply()
    return ex


def _invoice(shop, order):
    return shop.env["fix.ar.invoice"].from_closed_service_order(order, Datetime.now())


class TestExemptedPartIsNotInvoiced:
    def test_the_exempted_quantity_is_left_off_the_invoice(self, odoo_env):
        shop = _gl_company(odoo_env, "g12qty")
        order = _part_order(shop)  # 2 x 1000 + 500 = 2500 + 15% = 2875.00
        ex = _exempt(order, 1.0)
        assert ex.state == "approved"
        assert round(ex.amount, 2) == 1150.00  # 1 x 1000 + VAT
        invoice = _invoice(shop, order)
        assert round(invoice.taxable_amount, 2) == 1500.00
        assert round(invoice.total_payable, 2) == 1725.00
        lcd = invoice.line_ids.filtered(lambda line: line.product_id == shop.lcd)
        assert round(lcd.taxable_amount, 2) == 1000.00

    def test_a_fully_exempted_line_is_dropped(self, odoo_env):
        shop = _gl_company(odoo_env, "g12full")
        order = _part_order(shop, qty=1.0)
        _exempt(order, 1.0)
        invoice = _invoice(shop, order)
        assert not invoice.line_ids.filtered(lambda line: line.product_id == shop.lcd)
        assert round(invoice.taxable_amount, 2) == 500.00

    def test_a_pending_exemption_does_not_change_the_bill(self, odoo_env):
        shop = _gl_company(odoo_env, "g12pend")
        order = _part_order(shop)
        _exempt(order, 1.0, approve=False)
        assert round(_invoice(shop, order).total_payable, 2) == 2875.00

    def test_the_discount_share_of_the_exempted_part_goes_with_it(self, odoo_env):
        shop = _gl_company(odoo_env, "g12disc")
        order = _part_order(shop, discount=250.0)  # (2500 - 250) x 1.15 = 2587.50
        est = order.estimate_ids[:1]
        assert round(est.grand_total, 2) == 2587.50
        ex = _exempt(order, 1.0)
        # 1000 of 2500 gross carries 100 of the 250 discount: (1000 - 100) x 1.15
        assert round(ex.amount, 2) == 1035.00
        invoice = _invoice(shop, order)
        assert abs(invoice.total_payable - (2587.50 - 1035.00)) <= 0.011


class TestAcceptedQuotationLessExemptions:
    def test_lower_by_exactly_the_exemptions_is_invoiced(self, odoo_env):
        shop = _gl_company(odoo_env, "g12d301")
        order = _part_order(shop)
        _accepted_quotation(shop, order)  # accepted 2875.00
        _exempt(order, 1.0)
        invoice = _invoice(shop, order)
        assert round(invoice.total_payable, 2) == 1725.00

    def test_any_other_difference_is_still_refused(self, odoo_env):
        shop = _gl_company(odoo_env, "g12d301x")
        order = _part_order(shop)
        _accepted_quotation(shop, order, value=2775.00)  # accepted 100 less
        _exempt(order, 1.0)
        Invoice = shop.env["fix.ar.invoice"]
        with pytest.raises(UserError, match="accepted") as refused, odoo_env.cr.savepoint():
            Invoice.from_closed_service_order(order, Datetime.now())
        text = str(refused.value).replace(",", "")
        assert "2775.00" in text and "1150.00" in text  # accepted, and the exemption
        assert not Invoice.search(
            [("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)]
        )

    def test_without_exemptions_the_d301_rule_is_unchanged(self, odoo_env):
        shop = _gl_company(odoo_env, "g12d301n")
        order = _part_order(shop)
        _accepted_quotation(shop, order, value=1725.00)  # as if exempted, but none is
        with pytest.raises(UserError, match="accepted"), odoo_env.cr.savepoint():
            _invoice(shop, order)


class TestExemptionAfterTheInvoiceIsACreditNote:
    def test_approval_raises_a_credit_note_for_the_part(self, odoo_env):
        shop = _gl_company(odoo_env, "g12cn")
        order = _part_order(shop)
        invoice = _invoice(shop, order)
        assert round(invoice.total_payable, 2) == 2875.00
        ex = _exempt(order, 1.0)
        note = ex.credit_note_id
        assert note and note._name == "fix.credit.note"
        assert note.invoice_id == invoice
        assert round(note.amount, 2) == 1150.00
        assert note.reason_code == "part_not_fitted"
        # raised and submitted, never approved here: it runs its own ladder
        assert note.state == "pending_approval"
        # the invoice itself is untouched until the credit note issues
        assert round(invoice.total_payable, 2) == 2875.00
        bodies = " ".join(order.message_ids.mapped("body"))
        assert "credit note" in bodies.lower()
        # re-running the auto-invoice stays idempotent: no second invoice
        assert _invoice(shop, order) == invoice

    def test_a_pending_exemption_raises_nothing(self, odoo_env):
        shop = _gl_company(odoo_env, "g12cnp")
        order = _part_order(shop)
        invoice = _invoice(shop, order)
        ex = _exempt(order, 1.0, approve=False)
        assert not ex.credit_note_id and not invoice.credit_note_ids
