# A06 ERP audit D6 (X09 / M44-11): an LC remittance settles the supplier in
# AP. Before the bill it is an advance on the supplier-advance account that
# the bill takes back; after the bill it settles the bill, which then is never
# paid a second time. Runs on the M52 control-suite fixture.
import pytest
from odoo.addons.cd_ap_ext.models.ap_gl import ap_journal, post_ap_move
from odoo.addons.cd_ap_ext.tests.test_a08_m52_controls import (
    approve,
    balance,
    bill,
    c,  # noqa: F401 - the fixture
    issued_po,
)
from odoo.addons.cd_ap_ext.tests.test_supplier_advance_payment import (
    ADVANCE_CODE,
    _receive,
    adv_account,  # noqa: F401 - the fixture
)
from odoo.exceptions import UserError


def _remit(c, amount, po=None, bills=None, scope_key=None):  # noqa: F811
    """What M44's LC payment does: settle in AP, post one balanced entry
    (the bank side is a stand-in account here), attach it."""
    env = c.env
    Settlement = env["fix.ap.lc.settlement"].sudo()
    source = po or c.vendor
    settlements, legs = Settlement._fix_settle(
        c.company,
        c.ou,
        c.vendor,
        env.ref("base.BDT"),
        amount,
        amount,
        "2026-11-20",
        "LC-TEST",
        source,
        purchase_order=po,
        scope_key=scope_key,
        bills=bills,
    )
    lines = [(acc, label, amt, 0.0, partner) for acc, label, amt, partner in legs]
    lines.append((c.a["expense"], "bank stand-in", 0.0, amount, None))
    move = post_ap_move(
        env, c.company, ap_journal(env, c.company, "purchase"), "2026-11-20", "LC-TEST", lines, c.ou
    )
    settlements._fix_attach_move(move)
    return settlements, move


def test_lc_remittance_before_the_bill_is_an_advance_the_bill_takes_back(c, adv_account):  # noqa: F811
    po = issued_po(c, 10, 1000.0)
    settlements, _move = _remit(c, 4000.0, po=po)
    assert settlements.kind == "advance"
    assert balance(c.env, adv_account) == pytest.approx(4000.0)
    _receive(c, po, 10)
    b = bill(c, 1000.0, qty=10, po=po)
    before = b.total_payable
    approve(c, b)
    assert b.advance_applied == pytest.approx(4000.0)
    assert b.total_payable == pytest.approx(before - 4000.0)
    assert balance(c.env, adv_account) == pytest.approx(0.0)
    assert settlements.remaining_amount == pytest.approx(0.0)


def test_lc_remittance_after_the_bill_settles_it_and_it_is_not_paid_again(c, adv_account):  # noqa: F811
    b = bill(c, 5000.0)
    approve(c, b)
    payable = b.total_payable
    settlements, move = _remit(c, payable, bills=b)
    assert settlements.kind == "bill" and settlements.bill_id == b
    ap_debit = move.line_ids.filtered(lambda ln: ln.account_id == c.ap)
    assert sum(ap_debit.mapped("debit")) == pytest.approx(payable)
    assert b.total_payable == pytest.approx(0.0)
    assert b.payment_state == "paid", "a settled bill leaves every payment run"
    # a second remittance finds nothing payable on it: it becomes an advance
    again, _m = _remit(c, 100.0, bills=b)
    assert again.kind == "advance"


def test_partial_remittance_lowers_what_the_bill_still_pays(c, adv_account):  # noqa: F811
    b = bill(c, 5000.0)
    approve(c, b)
    payable = b.total_payable
    _remit(c, 1000.0, bills=b)
    assert b.lc_settled_amount == pytest.approx(1000.0)
    assert b.total_payable == pytest.approx(payable - 1000.0)
    assert b.payment_state == "not_paid"


def test_a_bill_in_a_payment_run_is_not_settled_again(c, adv_account):  # noqa: F811
    b = bill(c, 5000.0)
    approve(c, b)
    b.sudo()._guarded().write({"payment_state": "in_run"})
    with pytest.raises(UserError, match="payment run"):
        _remit(c, 1000.0, bills=b)


def test_settlement_records_are_evidence(c, adv_account):  # noqa: F811
    settlements, _m = _remit(c, 50.0)
    with pytest.raises(UserError):
        settlements.with_user(c.acc1).write({"amount": 1.0})
    with pytest.raises(UserError):
        settlements.sudo().unlink()


def test_supplier_advance_account_defaults_to_10255(c):  # noqa: F811
    icp = c.env["ir.config_parameter"].sudo()
    icp.search([("key", "=", "cd_ap_ext.account_code.supplier_advance")]).unlink()
    c.env["fix.ap.lc.settlement"]._fix_default_params()
    assert icp.get_param("cd_ap_ext.account_code.supplier_advance") == "10255"
    icp.set_param("cd_ap_ext.account_code.supplier_advance", ADVANCE_CODE)
    c.env["fix.ap.lc.settlement"]._fix_default_params()
    assert icp.get_param("cd_ap_ext.account_code.supplier_advance") == ADVANCE_CODE
