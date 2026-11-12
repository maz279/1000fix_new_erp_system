# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
# Quote-to-cash P2 (13 Nov 2026): a multi-item counter sale, and the counter
# on the one M20 payment-method list (Rocket, Upay included).
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import (  # noqa: F401
    _balance,
    fin,
)
from odoo.exceptions import UserError


def _basket(m, method_code, lines, **kw):
    method = m.env["fix.payment.method"].search([("code", "=", method_code)])
    vals = {
        "operating_unit_id": m.ou.id,
        "branch_id": m.branch.id,
        "payment_method_id": method.id,
        "line_ids": [(0, 0, line) for line in lines],
    }
    vals.update(kw)
    return m.env["fix.counter.basket"].with_user(m.cashier).create(vals)


def test_a_basket_confirms_one_posted_sale_per_item(fin):
    m = fin
    basket = _basket(
        m,
        "ROCKET",
        [
            {"product_id": m.product.id, "quantity": 1, "unit_price": 1150.0},
            {"product_id": m.service.id, "quantity": 1, "unit_price": 575.0},
        ],
        transaction_ref="RKT-77AB",
    )
    assert basket.total == 1725.0 and basket.name.startswith("CB/")
    basket.action_confirm()
    sales = basket.sale_ids
    assert basket.state == "confirmed" and len(sales) == 2
    assert set(sales.mapped("payment_method")) == {"rocket"}
    assert set(sales.mapped("state")) == {"confirmed"}
    assert all(s.sudo().posting_state == "posted" for s in sales)
    # Rocket clears through the MFS clearing account, like bKash
    assert _balance(m.env, m.acc.mfs) == 1725.0
    with pytest.raises(UserError, match="final"), m.env.cr.savepoint():
        basket.line_ids[:1].with_user(m.cashier).write({"quantity": 3})


def test_a_wallet_basket_needs_its_trxid_and_nothing_posts_without_it(fin):
    m = fin
    basket = _basket(m, "UPAY", [{"product_id": m.product.id, "unit_price": 1150.0}])
    with pytest.raises(UserError, match="TrxID"), m.env.cr.savepoint():
        basket.action_confirm()
    assert basket.state == "draft" and not basket.sale_ids


def test_a_method_the_counter_does_not_take_is_refused(fin):
    m = fin
    basket = _basket(
        m, "RTGS", [{"product_id": m.product.id, "unit_price": 1150.0}], transaction_ref="X"
    )
    with pytest.raises(UserError, match="not taken at the counter"), m.env.cr.savepoint():
        basket.action_confirm()


def test_a_counter_sale_takes_its_tender_from_the_payment_method(fin):
    m = fin
    bkash = m.env.ref("cd_billing_engine.payment_method_bkash")
    sale = m.sale(None, price=1150.0)
    sale.write({"payment_method_id": bkash.id})
    assert sale.payment_method == "bkash"
