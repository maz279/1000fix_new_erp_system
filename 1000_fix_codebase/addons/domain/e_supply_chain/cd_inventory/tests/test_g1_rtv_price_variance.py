# G1 (owner decision 12 Nov 2026): the purchase-price variance of a return to
# vendor is posted.
#
# The stock leaves at its average cost through the valuation suspense (the
# rtv row the period-close cut-over moves off Inventory); the vendor credits
# the price it billed (the AP credit note, Dr AP / Cr GRNI). The difference,
# qty x (average cost - billed price), was stated on the RTV and posted
# nowhere, so after the cut-over and the GRNI clearing it sat in the suspense
# account. It is now a suspense row of its own (entry type price_variance)
# that moves no stock and names the PPV account the cut-over clears it to
# (cd_inventory.account_code.price_variance). Unset: recorded only, as
# before, and the RTV says so. The return is never blocked.
# ruff: noqa: F811  (the p2p fixture is imported and used as a parameter)
from odoo.addons.cd_inventory.tests.test_e3_rtv_credit import (  # noqa: F401
    _bill,
    _rtv,
    p2p,
)

PPV_PARAM = "cd_inventory.account_code.price_variance"


def _credited(w, ref):
    _bill(w)
    r = _rtv(w, 5.0, receipt_id=w.grn.id, rtv_ref="RMA-G1%s-%s" % (ref, w.tag))
    r.with_user(w.controller).action_approve()
    r.with_user(w.keeper).action_ship()
    r.with_user(w.controller).action_mark_credited("MUSHAK-67-G1%s-%s" % (ref, w.tag))
    assert r.state == "credited" and r.vendor_note_res_id
    return r.sudo()


def _ppv_account(env, code="990607"):
    Account = env["account.account"]
    found = Account.search([("code", "=", code), ("company_ids", "in", env.company.id)], limit=1)
    return found or Account.create(
        {
            "code": code,
            "name": "G1 Purchase Price Variance",
            "account_type": "expense_direct_cost",
            "company_ids": [(6, 0, [env.company.id])],
        }
    )


def test_g1_without_a_ppv_account_the_variance_is_recorded_only(p2p):
    p2p.env["ir.config_parameter"].sudo().set_param(PPV_PARAM, False)
    r = _credited(p2p, "A")
    avg = r.unit_cost
    assert abs(r.price_variance - round(5.0 * (avg - 1480.0), 2)) < 0.01
    assert abs(r.price_variance) > 0.005
    assert not p2p.suspense(source_ref=r.name, entry_type="price_variance")
    assert not r.price_variance_entry_id
    status = r.price_variance_status or ""
    assert "not posted" in status and PPV_PARAM in status


def test_g1_the_variance_is_a_suspense_row_the_cutover_clears_to_ppv(p2p):
    ppv = _ppv_account(p2p.env)
    p2p.env["ir.config_parameter"].sudo().set_param(PPV_PARAM, ppv.code)
    r = _credited(p2p, "B")
    stock = p2p.suspense(source_ref=r.name, entry_type="rtv")
    row = p2p.suspense(source_ref=r.name, entry_type="price_variance")
    assert len(stock) == 1 and len(row) == 1
    assert r.price_variance_entry_id == row
    assert row.status == "pending_gl_cutover"
    assert abs(row.total_valuation - r.price_variance) < 0.005
    assert row.clearing_account_code == ppv.code
    assert row.suspense_account_code == stock.suspense_account_code
    assert row.company_id == stock.company_id and row.product_id == p2p.ssd
    # it moves no stock: the cut-over's Inventory leg is the rtv row alone
    assert (stock | row)._fix_stock_effect_total() == stock._fix_stock_effect_total()
    assert (stock | row)._fix_cutover_clearings() == {ppv.code: round(r.price_variance, 2)}
    assert ppv.code in (r.price_variance_status or "")
    assert "cut-over" in (r.price_variance_status or "")


def test_g1_a_ppv_code_not_in_the_chart_records_only(p2p):
    p2p.env["ir.config_parameter"].sudo().set_param(PPV_PARAM, "G1NOPE")
    r = _credited(p2p, "C")
    assert abs(r.price_variance) > 0.005
    assert not p2p.suspense(source_ref=r.name, entry_type="price_variance")
    status = r.price_variance_status or ""
    assert "not posted" in status and "G1NOPE" in status
