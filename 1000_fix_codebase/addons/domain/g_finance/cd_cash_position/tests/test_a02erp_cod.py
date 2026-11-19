"""A02 ERP audit (19 Nov 2026) - M03-F8 / M03-F9 on the rider COD settlement
(finance side, M50), and the M03 KPI 'COD Today' (F20).

F8 P0: a rider's COD shortage was debited to rider_shortage with no partner
and never cleared: action_mark_recovered only set a label. The shortage line
now names the rider, and the recovery posts (cash repayment or payroll
deduction) crediting rider_shortage for the rider, by someone other than the
settler. F9: an order whose COD receipt is not booked yet is not settled.

Uses the A08 M50 fixture (``c``); ``odoo_env`` rolls back after every test.
"""

# ruff: noqa: F811  (the A08 fixture `c` is imported and used as a parameter)
import pytest
from odoo.exceptions import UserError

from .test_a08_m50_controls import _cod, _cod_orders, bal, c  # noqa: F401 - fixture

pytestmark = [pytest.mark.financial]

PAYROLL = "cd_cash_position.account_code.rider_shortage_payroll"


def _short(c, amount=5000.0, remitted=0.0):
    """A settled rider settlement with a booked shortage."""
    _cod_orders(c, [amount])
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    s.with_user(c.acct).write({"remitted_amount": remitted})
    s.with_user(c.acct).action_submit()
    s.with_user(c.mgr).action_approve_shortage(note="F8 probe: cash bag stolen, GD 12")
    s.with_user(c.mgr2).action_settle()
    assert s.recovery_state == "open"
    return s


def _rider_balance(c, partner):
    lines = c.env["account.move.line"].search(
        [
            ("account_id", "=", c.acc["rider_shortage"].id),
            ("partner_id", "=", partner.id),
            ("parent_state", "=", "posted"),
        ]
    )
    return round(sum(lines.mapped("balance")), 2)


def test_f8_the_shortage_is_booked_against_the_rider(c):
    s = _short(c)
    rider = c.rider.work_contact_id
    assert rider
    line = s.move_id.line_ids.filtered(lambda ln: ln.account_id == c.acc["rider_shortage"])
    assert line.partner_id == rider and line.debit == 5000.0
    assert _rider_balance(c, rider) == 5000.0


def test_f8_a_cash_repayment_posts_and_clears_the_rider(c):
    s = _short(c)
    rider = c.rider.work_contact_id
    before_bank = bal(c, c.bank_acc)
    # the settler does not also close the recovery
    with pytest.raises(UserError, match="Segregation"):
        s.with_user(c.mgr2).action_mark_recovered(reference="RCPT-1")
    with pytest.raises(UserError, match="needs the"):
        s.with_user(c.acct).action_mark_recovered(reference="RCPT-1")
    s.with_user(c.mgr).action_mark_recovered(reference="RCPT-1", method="cash")
    assert s.recovery_state == "recovered" and s.recovery_method == "cash"
    assert s.recovery_move_id.state == "posted" and s.recovered_by_id == c.mgr
    assert _rider_balance(c, rider) == 0.0
    assert bal(c, c.acc["rider_shortage"]) == 0.0
    assert round(bal(c, c.bank_acc) - before_bank, 2) == 5000.0
    assert not c.env["fix.cod.settlement"]._fix_rider_has_open_variance(c.rider)


def test_f8_a_payroll_recovery_fails_closed_without_its_account(c):
    s = _short(c)
    c.env["ir.config_parameter"].sudo().set_param(PAYROLL, "")
    with pytest.raises(UserError, match="rider_shortage_payroll"):
        s.with_user(c.mgr).action_mark_recovered(reference="PAYSLIP-11", method="payroll")
    assert s.recovery_state == "open" and not s.recovery_move_id
    payable = c.env["account.account"].create(
        {
            "code": "A2F8P%d" % c.n,
            "name": "F8 salaries payable",
            "account_type": "liability_current",
        }
    )
    c.env["ir.config_parameter"].sudo().set_param(PAYROLL, payable.code)
    s.with_user(c.mgr).action_mark_recovered(reference="PAYSLIP-11", method="payroll")
    assert s.recovery_method == "payroll"
    assert bal(c, payable) == 5000.0
    assert _rider_balance(c, c.rider.work_contact_id) == 0.0


def test_f8_the_recovery_stamps_cannot_be_typed(c):
    s = _short(c)
    with pytest.raises(UserError, match="changes only through its workflow"):
        s.with_user(c.mgr).write({"recovery_state": "recovered"})
    with pytest.raises(UserError, match="changes only through its workflow"):
        s.with_user(c.mgr).write({"recovery_method": "cash"})


def test_f9_an_order_with_a_pending_cod_receipt_is_not_settled(c):
    orders = _cod_orders(c, [1500.0])
    if "posting_state" not in orders._fields:
        pytest.skip("the storefront finance bridge (posting_state) is not installed")
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    assert orders <= s.order_ids
    c.env.cr.execute(
        "UPDATE fix_storefront_order SET posting_state = 'pending' WHERE id IN %s",
        (tuple(orders.ids),),
    )
    c.env.invalidate_all()
    s.with_user(c.acct).write({"remitted_amount": 1500.0})
    with pytest.raises(UserError, match="not booked yet"):
        s.with_user(c.acct).action_submit()
    # nor is it offered to a new settlement
    fresh = _cod(c, c.acct)
    assert not (fresh._open_cod_orders(c.rider, c.company) & orders)


def test_f20_cod_today_is_cash_handed_over_not_drafts(c):
    from odoo.addons.cd_p03_portal.controllers.a02 import m03

    c.env["fix.cod.settlement"].search([]).write({"settlement_date": "2000-01-01"})
    _cod_orders(c, [1200.0])
    s = _cod(c, c.acct)
    s.with_user(c.acct).action_load_orders()
    s.with_user(c.acct).write({"remitted_amount": 1200.0, "settlement_date": c.today})
    assert m03.kpis(c.env)["cod_today"] == 0.0  # a draft sheet is not cash handed over
    s.with_user(c.acct).action_submit()
    assert m03.kpis(c.env)["cod_today"] == 1200.0
