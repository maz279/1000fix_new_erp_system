# A local supplier's advance paid through treasury and taken back on its
# bill (user request, 13 Nov 2026). Runs on the M52 control-suite fixture:
# non-admin accountants and managers, a vendor with a confirmed bank account,
# an issued and received purchase order. Treasury (M50) is driven the way the
# operability suite drives it: the relay delivers the events, the bank's
# confirmation is posted as the superuser.
import pytest
from odoo.addons.cd_ap_ext.tests.test_a08_m52_controls import (
    approve,
    balance,
    bill,
    c,  # noqa: F401 - the fixture
    issued_po,
    refused,
)
from odoo.addons.cd_ap_ext.tests.test_a08_m52_operability import (
    execution_of,
    paying,  # noqa: F401 - the fixture
    relay,
    treasury_paid,
)
from odoo.exceptions import UserError

ADVANCE_CODE = "113950"


@pytest.fixture
def adv_account(c):  # noqa: F811
    Account = c.env["account.account"]
    account = Account.search(
        [("code", "=", ADVANCE_CODE), ("company_ids", "in", c.company.id)], limit=1
    ) or Account.create(
        {
            "code": ADVANCE_CODE,
            "name": "Test advances to suppliers",
            "account_type": "asset_current",
            "company_ids": [(6, 0, c.company.ids)],
        }
    )
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_ap_ext.account_code.supplier_advance", ADVANCE_CODE
    )
    return account


def _approved_advance(c, po, amount):  # noqa: F811
    """M16 as it leaves an advance: an approved proforma, an approved advance
    (the second-person rules are proven in cd_requisition's suite)."""
    env = c.env
    pi = env["fix.purchase.proforma"].create(
        {"purchase_order_id": po.id, "proforma_no": "PI-ADV-%s" % po.id, "amount": po.amount_total}
    )
    pi.action_approve()
    adv = env["fix.purchase.advance"].create({"proforma_id": pi.id, "amount": amount})
    adv.action_request()
    adv.action_approve(reason="supplier terms: advance before dispatch")
    assert adv.state == "approved"
    return adv


def _paid_advance(c, po, amount):  # noqa: F811
    adv = _approved_advance(c, po, amount)
    adv.with_user(c.acc1).action_request_payment()
    assert adv.state == "payment_requested"
    relay(c, "payment.requested", "fix.purchase.advance", adv.id)
    ex = execution_of(c, "fix.purchase.advance", adv.id)
    assert len(ex) == 1 and ex.amount == pytest.approx(amount)
    treasury_paid(c, ex)
    relay(c, "payment.executed", "fix.payment.execution", ex.id)
    assert adv.state == "paid" and adv.payment_move_id
    return adv


def _receive(c, po, qty):  # noqa: F811
    """The goods arrive after the advance: a posted, inspected receipt."""
    env = c.env
    po.sudo().action_record_receipt({po.line_ids.id: qty})
    receipt = po.receipt_ids.sorted("id")[-1]
    for line in receipt.line_ids:
        env["fix.procurement.inspection"].create(
            {"receipt_line_id": line.id, "qty_accepted": line.qty_received}
        ).action_confirm()


def test_an_approved_advance_is_paid_through_treasury(c, paying, adv_account):  # noqa: F811
    po = issued_po(c, 10, 1000.0)
    adv = _paid_advance(c, po, 4000.0)
    ex = execution_of(c, "fix.purchase.advance", adv.id)
    assert ex.partner_id == c.vendor.commercial_partner_id
    assert balance(c.env, adv_account) == pytest.approx(4000.0)
    assert adv.remaining_amount == pytest.approx(4000.0)
    # paid is paid: it is neither cancelled nor requested again
    with pytest.raises(UserError):
        adv.action_cancel()
    with pytest.raises(UserError):
        adv.with_user(c.acc1).action_request_payment()


def test_only_finance_requests_the_payment_and_only_when_approved(c, paying, adv_account):  # noqa: F811
    po = issued_po(c, 10, 1000.0)
    adv = _approved_advance(c, po, 2000.0)
    assert refused(c.env, lambda: adv.with_user(c.plain).action_request_payment())
    draft = c.env["fix.purchase.advance"].create(
        {"proforma_id": adv.proforma_id.id, "amount": 100.0}
    )
    with pytest.raises(UserError, match="Only an approved advance"):
        draft.with_user(c.acc1).action_request_payment()


def test_the_bill_takes_the_paid_advance_back(c, paying, adv_account):  # noqa: F811
    po = issued_po(c, 10, 1000.0)
    _paid_advance(c, po, 4000.0)
    _receive(c, po, 10)
    b = bill(c, 1000.0, qty=10, po=po)
    before = b.total_payable
    approve(c, b)
    assert b.move_id.state == "posted"
    assert b.advance_applied == pytest.approx(4000.0)
    assert b.total_payable == pytest.approx(before - 4000.0)
    # the asset is cleared and trade payables carry only what is still owed
    assert balance(c.env, adv_account) == pytest.approx(0.0)
    ap_line = b.move_id.line_ids.filtered(lambda line: line.account_id == c.ap)
    assert sum(ap_line.mapped("credit")) == pytest.approx(b.total_payable)
    assert b.advance_application_ids.amount == pytest.approx(4000.0)


def test_an_advance_above_one_bill_carries_to_the_next(c, paying, adv_account):  # noqa: F811
    po = issued_po(c, 10, 1000.0)
    adv = _paid_advance(c, po, 8000.0)
    _receive(c, po, 10)
    first = bill(c, 1000.0, qty=5, po=po)
    room = first.total_payable
    approve(c, first)
    assert first.advance_applied == pytest.approx(room)
    assert first.total_payable == pytest.approx(0.0)
    assert adv.remaining_amount == pytest.approx(8000.0 - room)
    second = bill(c, 1000.0, qty=5, po=po)
    approve(c, second)
    assert second.advance_applied == pytest.approx(8000.0 - room)
    assert adv.remaining_amount == pytest.approx(0.0)
    assert balance(c.env, adv_account) == pytest.approx(0.0)


def test_a_returned_advance_payment_waits_for_treasury(c, paying, adv_account):  # noqa: F811
    po = issued_po(c, 10, 1000.0)
    adv = _paid_advance(c, po, 3000.0)
    ex = execution_of(c, "fix.purchase.advance", adv.id)
    ex.sudo()._guarded().write({"state": "failed", "failure_reason": "account closed"})
    ex.sudo()._publish_failed("account closed")
    relay(c, "payment.failed", "fix.payment.execution", ex.id)
    assert adv.state == "payment_requested" and adv.payment_failure == "account closed"
    assert not adv.payment_move_id
    assert balance(c.env, adv_account) == pytest.approx(0.0)
