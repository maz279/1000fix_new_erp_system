"""A02 authorization / accuracy pass for M04 (cd_front_desk).

4. a non-cash counter sale carries the transaction reference that proves it;
5. the opening float is locked once the shift is open;
6. counter cash is not taken with no open shift unless the branch switched
   that off explicitly.

Non-admin users created by the P0 fixture act throughout; ``odoo_env`` rolls
back after every test.
"""

# ruff: noqa: F811  (the P0 suite's fixtures are imported and used as parameters)
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import (  # noqa: F401
    _refused,
    call,
    m04,
)
from odoo.addons.cd_front_desk.tests.test_a02_p1p2_cd_front_desk import _order, _user
from odoo.exceptions import UserError

SHIFT_PARAM = "cd_front_desk.order_cash_requires_open_shift"


# ============================================================ 4. non-cash reference
@pytest.mark.parametrize("method", ["bkash", "nagad", "card"])
def test_a_non_cash_sale_needs_its_transaction_reference(m04, method):
    m = m04
    s = m.shift()
    sale = m.sale(s, method=method)
    with _refused(m.env, UserError, "transaction reference"):
        sale.action_confirm()
    sale.write({"transaction_ref": "   "})  # blanks are not a reference
    with _refused(m.env, UserError, "transaction reference"):
        sale.action_confirm()
    assert sale.sudo().state == "draft"
    sale.write({"transaction_ref": "TRX-G3-%s" % method})
    sale.action_confirm()
    assert sale.state == "confirmed" and s.sudo().cash_payments == 0.0


def test_a_cash_sale_needs_no_transaction_reference(m04):
    m = m04
    s = m.shift()
    sale = m.sale(s)
    sale.action_confirm()
    assert sale.state == "confirmed" and s.sudo().cash_payments == 1000.0


# ============================================================ 5. opening float
def test_the_opening_float_is_locked_once_the_shift_is_open(m04, call):
    """BDT 3,000 taken, the float lowered by 3,000: the drawer balanced short."""
    m = m04
    s = m.shift()
    m.sale(s, qty=3).action_confirm()
    assert s.sudo().expected_closing == 8000.0
    with _refused(m.env, UserError, "can no longer be changed"):
        s.write({"opening_float": 2000.0})
    # a Branch Manager working the till is not exempt, nor is the workspace save
    with _refused(m.env, UserError, "can no longer be changed"):
        m.as_(m.manager_cashier, s).write({"opening_float": 2000.0})
    res = call(
        m.env(user=m.cashier.id),
        "model_write",
        model="fix.cash.shift",
        record_id=s.id,
        values={"opening_float": 2000.0},
    )
    assert "error" in res, res
    s.invalidate_recordset()
    assert (s.opening_float, s.sudo().expected_closing) == (5000.0, 8000.0)
    assert "opening_float" in s._fix_form_locked_fields()
    # the form posts the float it shows along with the count: no change, no refusal
    s.write({"opening_float": 5000.0, "denom_1000_count": 8})
    assert s.denom_1000_count == 8


# ============================================================ 6. order cash
def test_counter_cash_needs_an_open_shift_when_the_switch_is_absent(m04):
    m = m04
    m.env["ir.config_parameter"].search([("key", "=", SHIFT_PARAM)]).unlink()
    so_cashier = _user(m, "socash3", "cd_service_order.group_so_cashier")
    order = _order(m)
    with _refused(m.env, UserError, "no open cash shift"):
        order.with_user(so_cashier).with_context(
            fd_settlement_tender="cash"
        )._fix_record_settlement(400.0, "CTR-G3-1", "counter")
    assert order.payment_settlement_state == "unpaid"
    # with the drawer open the same settlement lands in it
    s = m.shift()
    order.with_user(so_cashier).with_context(fd_settlement_tender="cash")._fix_record_settlement(
        400.0, "CTR-G3-1", "counter"
    )
    assert order.counter_shift_id == s and s.sudo().cash_payments == 400.0


def test_an_explicit_zero_still_switches_the_open_shift_rule_off(m04):
    m = m04
    m.env["ir.config_parameter"].set_param(SHIFT_PARAM, "0")
    so_cashier = _user(m, "socash4", "cd_service_order.group_so_cashier")
    order = _order(m)
    order.with_user(so_cashier).with_context(fd_settlement_tender="cash")._fix_record_settlement(
        400.0, "CTR-G3-2", "counter"
    )
    assert not order.counter_shift_id and order.payment_settlement_state == "settled"
