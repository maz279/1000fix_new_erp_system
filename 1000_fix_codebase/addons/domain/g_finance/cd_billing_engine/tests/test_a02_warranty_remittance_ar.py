"""A02 ERP audit X-10 (19 Nov 2026): an OEM remittance is booked on AR.

Recording the brand's payment on the claim wrote the claim only; the brand's
M20 invoice stayed open on AR after the claim was remitted and closed. Now the
remittance is a bank receipt on the brand, applied to the claim's invoice.
``odoo_env`` rolls back after each test.
"""

import pytest
from odoo.addons.cd_billing_engine.tests.test_a04_c7_claim_consumer import (
    _invoices,
    _relay,
    _submitted,
)

BILLING = "cd_billing_engine.account_code."


@pytest.fixture
def remit(w):
    env = w.env
    params = env["ir.config_parameter"].sudo()

    def account(key, kind):
        return env["account.account"].create(
            {"code": "WRA%s%d" % (key, w.brand.id), "name": "Remit %s" % key, "account_type": kind}
        )

    w.ar = account("AR", "asset_receivable")
    w.bank = account("BNK", "asset_cash")
    params.set_param(BILLING + "ar", w.ar.code)
    params.set_param(BILLING + "bank", w.bank.code)
    env["res.partner"].create({"name": "OEM %s" % w.brand.name, "ref": w.brand.code})
    claim = _submitted(w)
    claim.action_decide(approved=True)
    _relay(env)
    (w.invoice,) = _invoices(env, claim)
    w.claim = claim
    return w


def test_a_remittance_before_the_invoice_is_booked_when_it_is_issued(remit):
    w = remit
    assert w.invoice.state == "draft"
    w.claim.with_user(w.officer).action_record_remittance(w.claim.approved_amount, "BANK-EARLY")
    assert not w.claim.remittance_receipt_ids  # nothing to collect against yet
    w.invoice.sudo().action_issue()
    (receipt,) = w.claim.remittance_receipt_ids
    assert receipt.reference == "BANK-EARLY"
    w.invoice.invalidate_recordset()
    assert w.invoice.state == "paid"


def test_the_remittance_pays_the_oem_invoice(remit):
    w = remit
    w.invoice.sudo().action_issue()
    w.claim.with_user(w.officer).action_record_remittance(w.claim.approved_amount, "BANK-OK")
    (receipt,) = w.claim.remittance_receipt_ids
    assert receipt.state == "confirmed" and receipt.method == "bank_transfer"
    assert receipt.customer_id == w.invoice.customer_id
    w.invoice.invalidate_recordset()
    assert w.invoice.state == "paid" and w.invoice.amount_residual == 0.0
    assert w.claim.state == "remitted"


def test_a_short_remittance_leaves_the_rest_owing(remit):
    w = remit
    w.invoice.sudo().action_issue()
    total = w.invoice.total_payable
    w.claim.with_user(w.officer).action_record_remittance(1000.0, "BANK-SHORT")
    w.invoice.invalidate_recordset()
    assert w.invoice.state == "issued"
    assert round(w.invoice.amount_residual, 2) == round(total - 1000.0, 2)
    assert w.claim.remittance_mismatch
