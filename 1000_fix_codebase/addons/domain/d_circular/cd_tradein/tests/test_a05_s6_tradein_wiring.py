# ruff: noqa: F811 - the S2 suite's pytest fixture (w) is imported
# A05 ERP remediation, stream S6 (integration wiring), M14 side, 21 Nov 2026:
#   * D10(b): every refurbished resale AR invoice (counter, marketplace)
#     credits cd_tradein.account_code.resale_revenue (400101 on fix_real),
#     never the M20 service-revenue default; unset, the sale refuses;
#   * I3: the seller payout instruction carries the trade-in's branch;
#   * D11: grade D's warranty provision ships as 7%.
# Live ORM as non-admin users (the S2 suite's fixture and helpers), rolled
# back by odoo_env.
import pytest
from odoo.addons.cd_tradein.tests.test_a05_erp_m14 import (  # noqa: F401 - the fixture
    TRD,
    acct,
    buyer,
    listed,
    paid,
    refused,
    w,
)

pytestmark = [pytest.mark.financial]

PARAM = "cd_tradein.account_code.resale_revenue"


def _branch_of(w):
    branch = w.env["fix.branch"].search([("operating_unit_id", "=", w.ou.id)], limit=1)
    if branch:
        return branch
    entity = w.env["fix.entity"].search([("company_id", "=", w.env.company.id)], limit=1)
    entity = entity or w.env["fix.entity"].create(
        {"legal_name": "A05 S6 Entity", "code": "A5S6E", "company_id": w.env.company.id}
    )
    return w.env["fix.branch"].create(
        {
            "name": "A05 S6 Intake Branch",
            "code": "A5S6-BR",
            "entity_id": entity.id,
            "operating_unit_id": w.ou.id,
        }
    )


def test_counter_sale_credits_the_resale_revenue_account(w):
    rec = listed(w)
    rec.with_user(w.controller).action_counter_sell(buyer(w).id)
    inv = rec.sale_invoice_id.sudo()
    revenue = acct(w, "resale_revenue")
    assert revenue and inv.revenue_account_id == revenue
    move = inv.posted_move_id
    credited = move.line_ids.filtered(lambda ln: ln.credit and ln.account_id == revenue)
    taxable = round(sum(inv.line_ids.mapped("taxable_amount")), 2)
    assert credited and round(sum(credited.mapped("credit")), 2) == taxable


def test_resale_without_the_revenue_parameter_refuses_before_anything_moves(w):
    rec = listed(w)
    w.env["ir.config_parameter"].sudo().set_param(PARAM, "")
    refused(lambda: rec.with_user(w.controller).action_counter_sell(buyer(w).id), PARAM)
    assert rec.graded_stock_id.state == "in_stock" and not rec.sale_invoice_id
    w.env["ir.config_parameter"].sudo().set_param(PARAM, "A05S6-NO-SUCH")
    refused(lambda: rec.with_user(w.controller).action_counter_sell(buyer(w).id), "A05S6-NO-SUCH")


def test_marketplace_sale_credits_the_resale_revenue_account(w):
    if "fix.marketplace.order" not in w.env:
        pytest.skip("cd_marketplace not installed")
    rec = listed(w, channel="marketplace")
    order = w.env["fix.marketplace.order"].sudo().browse(rec.marketplace_order_id)
    order.action_sell_refurb(buyer(w).id)
    assert order.refurb_invoice_id.sudo().revenue_account_id == acct(w, "resale_revenue")


def test_payout_instruction_carries_the_trade_in_branch(w):
    branch = _branch_of(w)
    if not branch:
        pytest.skip("no branch in the trade-in's operating unit")
    rec = paid(w, branch_id=branch.id)
    pay = rec.payout_execution_id.sudo()
    assert pay.branch_id == branch and pay.operating_unit_id == rec.operating_unit_id


def test_grade_d_provision_ships_at_seven_percent(w):
    param = w.env.ref("cd_tradein.param_warranty_provision_pct_d")
    assert param.key == "cd_tradein.warranty_provision_pct.d" and param.value == "7"
    rec = w.env[TRD].sudo().new({"grade": "d"})
    assert rec._provision_pct() == 7.0
