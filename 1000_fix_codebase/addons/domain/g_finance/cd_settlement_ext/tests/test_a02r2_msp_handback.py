# ruff: noqa: F811  (the imported sla fixture is used as a parameter)
"""A02 ERP pass-2 audit (2026-11-20), stream S4: the M05 money hand-backs.

  M05-S04 (owner decision D7)  an SLA credit is a share of the fee BEFORE VAT;
          its credit note is grossed up by the credited invoice's VAT ratio
          (so Mushak 6.7 reverses the VAT too); source_amount keeps the net.
  M05-S17 (D11)  remote-support hours above the entitlement become a draft
          invoice at the contract's overage rate, VAT by M51, once per report.

``odoo_env`` rolls back after each test.
"""

import pytest
from odoo import Command, fields
from odoo.addons.cd_settlement_ext.tests.test_a02_p1p2_cd_settlement_ext import (  # noqa: F401
    _applied_credit,
    _credit_notes,
    _relay,
    sla,
)
from odoo.exceptions import AccessError, UserError


def _vat_invoice(sla, name, source_model="manual", source_id=-555001):
    return sla.env["fix.ar.invoice"].create(
        {
            "operating_unit_id": sla.ou.id,
            "customer_id": sla.customer.id,
            "source_model": source_model,
            "source_id": source_id,
            "state": "issued",
            "name": name,
            "line_ids": [
                Command.create(
                    {
                        "description": "MSP fee",
                        "taxable_amount": 10000.0,
                        "vat_amount": 1500.0,
                        "line_total": 11500.0,
                    }
                )
            ],
        }
    )


def test_s04_the_credit_note_is_the_net_credit_grossed_up_by_the_invoice_vat(sla):
    if "fix.subscription.charge" not in sla.env:
        pytest.skip("cd_subscription not installed")
    sub = sla.env["fix.subscription"].create(
        {
            "name": "A02R2 MSP billing",
            "operating_unit_id": sla.ou.id,
            "customer_id": sla.customer.id,
            "contract_id": sla.contract.id,
            "recurring_amount": 10000.0,
        }
    )
    invoice = _vat_invoice(sla, "INV/A02R2/VAT", "fix.subscription.charge", -555002)
    sla.env["fix.subscription.charge"].create(
        {
            "operating_unit_id": sla.ou.id,
            "subscription_id": sub.id,
            "period_start": fields.Date.today().replace(day=1),
            "period_end": fields.Date.today(),
            "amount": 10000.0,
            "invoice_id": invoice.id,
        }
    )
    credit = _applied_credit(sla, "2026-06")  # 4,500 before VAT
    _relay(sla.env)
    (note,) = _credit_notes(sla.env, credit)
    assert note.invoice_id == invoice
    assert note.source_amount == 4500.0
    assert note.amount == 5175.0  # 4,500 + 15 % VAT
    taxable, vat = note._vat_split()
    assert (round(taxable, 2), round(vat, 2)) == (4500.0, 675.0)


def test_s04_linking_the_invoice_later_grosses_the_note_up(sla):
    credit = _applied_credit(sla, "2026-05")
    _relay(sla.env)
    (note,) = _credit_notes(sla.env, credit)
    assert note.amount == 4500.0 and not note.invoice_id  # no invoice yet: the net
    invoice = _vat_invoice(sla, "INV/A02R2/LATE")
    note.with_user(sla.accountant).write({"invoice_id": invoice.id})
    assert note.amount == 5175.0 and note.source_amount == 4500.0
    # never more than the net plus its VAT
    with pytest.raises(Exception, match="cannot exceed"), sla.env.cr.savepoint():
        note.with_user(sla.accountant).write({"amount": 5200.0})


def _overage_report(sla, amount=4000.0):
    return sla.env["fix.msp.service.report"].create(
        {
            "msp_contract_id": sla.msp.id,
            "period_label": "2026-04",
            "alert_count": 0,
            "sla_attainment": 1.0,
            "remote_minutes": 180.0,
            "remote_hours_entitled": 1.0,
            "overage_hours": 2.0,
            "overage_rate": amount / 2.0,
            "overage_amount": amount,
        }
    )


def test_s17_remote_hours_overage_becomes_a_draft_invoice_once(sla):
    report = _overage_report(sla)
    Handback = sla.env["fix.finance.handback"]
    event = {
        "event_id": "evt-a02r2-ovg",
        "aggregate": "fix.msp.service.report",
        "aggregate_id": report.id,
        "payload": {"amount": 4000.0},
    }
    with pytest.raises(AccessError):
        Handback.with_user(sla.eng).consume_msp_remote_hours_overage(event)
    forged = dict(event, payload={"amount": 40000.0})
    with pytest.raises(UserError, match="the event says"):
        Handback.sudo().consume_msp_remote_hours_overage(forged)
    out = Handback.sudo().consume_msp_remote_hours_overage(event)
    invoice = sla.env["fix.ar.invoice"].browse(out["id"])
    assert out["created"] and invoice.state == "draft"
    assert invoice.customer_id == sla.customer
    assert round(sum(invoice.line_ids.mapped("taxable_amount")), 2) == 4000.0
    assert sum(invoice.line_ids.mapped("vat_amount")) > 0  # M51 VAT on the overage
    again = Handback.sudo().consume_msp_remote_hours_overage(event)
    assert again == {"model": "fix.ar.invoice", "id": invoice.id, "created": False}
    assert sla.env["fix.event.consumer"].search(
        [("event_type", "=", "msp.remote_hours_overage"), ("model", "=", Handback._name)]
    )
