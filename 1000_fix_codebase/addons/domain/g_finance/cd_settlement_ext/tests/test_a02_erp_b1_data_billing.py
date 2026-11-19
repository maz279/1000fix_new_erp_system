# ruff: noqa: F401, F811 (the m6 fixture is imported, and named as test parameters)
"""A02 ERP audit M06-F1 (P0), builder stream B1: M06 data recovery billing.

The relay turns a recovered (or unrecoverable) data case into its M20
invoice, in draft: the accepted quotation's recovery fee and donor fee, VAT
by M51; under no-data-no-fee an unrecoverable case owes only the donor fee.
The case's hand-over then waits for that invoice to be paid.

``odoo_env`` (addons/conftest.py): rolled back after every test.
"""

import pytest
from odoo.exceptions import AccessError, UserError

pytest.importorskip("odoo.addons.cd_data_case")
from odoo.addons.cd_data_case.tests.test_a02_p1p2_cd_data_case import CASE, m6

INVOICE = "fix.ar.invoice"


def _event(case, event_type="data_case.recovered"):
    return {
        "event_type": event_type,
        "aggregate": CASE,
        "aggregate_id": case.id,
        "event_id": "evt-b1-%d" % case.id,
        "payload": {"case": case.name},
    }


def _billing(m6):
    if CASE not in m6.env:
        pytest.skip("cd_data_case is not installed")
    return m6.env["fix.data.case.billing"].sudo()


def _invoice(m6, case):
    return m6.env[INVOICE].sudo().search([("source_model", "=", CASE), ("source_id", "=", case.id)])


def test_a_recovered_case_raises_its_draft_invoice_once(m6):
    Billing = _billing(m6)
    case = m6.recovered(m6.new_case())
    case.quote_ids.filtered(lambda q: q.state == "accepted")._guarded().write(
        {"donor_fee_bdt": 4000.0}
    )
    out = Billing.consume_data_case_recovered(_event(case))
    invoice = _invoice(m6, case)
    assert out["created"] and out["billed"] == 19000.0 and len(invoice) == 1
    assert invoice.state == "draft" and invoice.customer_id == case.customer_id
    assert sorted(invoice.line_ids.mapped("taxable_amount")) == [4000.0, 15000.0]
    assert invoice.taxable_amount == 19000.0
    # VAT is M51's determination, not a figure typed here
    assert invoice.total_payable == pytest.approx(invoice.taxable_amount + invoice.vat_amount)
    again = Billing.consume_data_case_recovered(_event(case))
    assert not again["created"] and again["id"] == invoice.id
    assert len(_invoice(m6, case)) == 1


def test_the_gate_opens_on_the_paid_invoice(m6):
    case = m6.recovered(m6.new_case())
    _billing(m6).consume_data_case_recovered(_event(case))
    invoice = _invoice(m6, case)
    assert "is draft, not paid" in case._handover_settlement_denial()
    invoice._guarded().write({"state": "issued"})
    assert "is issued, not paid" in case._handover_settlement_denial()
    # M20's receipt allocation marks it paid (_mark_paid); the gate reads that
    invoice._guarded().write({"state": "paid"})
    assert case._handover_settlement_denial() == ""


def test_unrecoverable_under_no_data_no_fee_bills_only_the_donor_fee(m6):
    Billing = _billing(m6)
    case = m6.recovering(m6.new_case())
    quote = case.quote_ids.filtered(lambda q: q.state == "accepted")
    m6.env["fix.data.recovery.attempt"].with_user(m6.tech).create(
        {"case_id": case.id, "method": "software_scan"}
    ).action_finish(outcome="failed")
    case.action_mark_unrecoverable(reason="no readable sectors")
    # the event fits the outcome; a forged 'recovered' does not
    with pytest.raises(UserError, match="not recovered"):
        Billing.consume_data_case_recovered(_event(case))
    out = Billing.consume_data_case_unrecoverable(_event(case, "data_case.unrecoverable"))
    assert not out["created"] and not _invoice(m6, case)  # no donor fee: nothing owed
    assert "nothing to bill" in case.message_ids[:1].body
    other = m6.recovering(m6.new_case(serial="WD-DONOR-%d" % m6.n))
    other.quote_ids.filtered(lambda q: q.state == "accepted")._guarded().write(
        {"donor_fee_bdt": 2500.0}
    )
    m6.env["fix.data.recovery.attempt"].with_user(m6.tech).create(
        {"case_id": other.id, "method": "software_scan"}
    ).action_finish(outcome="failed")
    other.action_mark_unrecoverable(reason="heads crashed")
    Billing.consume_data_case_unrecoverable(_event(other, "data_case.unrecoverable"))
    assert _invoice(m6, other).line_ids.mapped("taxable_amount") == [2500.0]
    assert quote.no_data_no_fee_applies


def test_only_the_relay_bills_and_no_one_pre_creates_the_invoice(m6):
    Billing = _billing(m6)
    case = m6.recovered(m6.new_case())
    with pytest.raises(AccessError, match="event relay"):
        Billing.with_user(m6.tech).consume_data_case_recovered(_event(case))
    with pytest.raises(UserError, match="relay"):
        m6.env[INVOICE].with_user(m6.tech).create(
            {"customer_id": case.customer_id.id, "source_model": CASE, "source_id": case.id}
        )
    with pytest.raises(UserError, match="refused"):
        Billing.consume_data_case_recovered(dict(_event(case), aggregate_id=0))
