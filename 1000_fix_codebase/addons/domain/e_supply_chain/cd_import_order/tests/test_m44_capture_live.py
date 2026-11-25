"""M44 capture audit (2026-11-16), live: the records the sub-module pages now
capture behave as the spec requires, attacked as non-admin users with the
real roles inside the rolled-back odoo_env.

  * fix.import.cost (FR-ITC-018/030/031, BRU-ITC-14/16/18): recorded by an
    officer, reconciled by another person with the bill attached, a variance
    classified, and the final landed-cost sheet agrees with the reconciled
    documents;
  * fix.import.lc.discrepancy (FR-ITC-016): no LC payment while undecided;
  * fix.import.customs.query (FR-ITC-028): no assessment while unresolved;
  * fix.import.arrival forwarder (FR-ITC-021, BRU-ITC-12).

Amounts are test inputs; no statutory figure is asserted.
"""

from __future__ import annotations

import base64
from datetime import timedelta

import pytest
from odoo.addons.cd_import_order.tests.test_a06_m44_controls import (
    APPROVER,
    OFFICER,
    _refused,
    _user,
    boe,
    landed,
    stage_lc_open,
    stage_received,
    stage_shipped,
)

PDF = base64.b64encode(b"%PDF-1.4 M44 capture test")


def _cost(c, user=None, **kw):
    vals = {
        "order_id": c.order.id,
        "category": "port",
        "billed_by_id": c.supplier.id,
        "document_ref": "PORT-%s" % c.tag,
        "incurred_on": c.today,
        "amount": 25000.0,
        "document": PDF,
        "document_name": "port.pdf",
    }
    vals.update(kw)
    return c.env["fix.import.cost"].with_user(user or c.officer).create(vals)


# ================================================================ cost documents
def test_cost_plain_user_reads_only(c):
    Cost = c.env["fix.import.cost"]
    _refused(lambda: _cost(c, user=c.clerk))
    doc = _cost(c)
    assert Cost.with_user(c.clerk).browse(doc.id).document_ref == doc.document_ref
    assert doc.state == "draft" and doc.recorded_by_id == c.officer
    assert doc.name.startswith("ICOST/")


def test_cost_finance_officer_records(c):
    doc = _cost(c, user=c.finance, category="bank", document_ref="BANK-%s" % c.tag)
    assert doc.landed_bucket == "LC & Bank Charges"


def test_cost_recorder_cannot_reconcile_and_bill_is_attached(c):
    both = _user(c.env, "m44t_costboth_%s" % c.tag, c.ou, OFFICER, APPROVER)
    doc = _cost(c, user=both, document=False, document_name=False)
    _refused(doc.with_user(both).action_reconcile, match="Segregation")
    _refused(doc.with_user(c.officer2).action_reconcile, match="role")
    _refused(doc.with_user(c.approver).action_reconcile, match="Attach")
    doc.with_user(both).write({"document": PDF, "document_name": "p.pdf"})
    doc.with_user(c.approver).action_reconcile()
    assert doc.state == "reconciled" and doc.reconciled_by_id == c.approver


def test_cost_variance_is_classified_not_absorbed(c):
    doc = _cost(c, expected_amount=20000.0)
    assert doc.variance == pytest.approx(5000.0) and doc.variance_pct == pytest.approx(25.0)
    _refused(doc.with_user(c.approver).action_reconcile, match="classify the variance")
    doc.with_user(c.officer).write({"variance_cause": "other"})
    _refused(doc.with_user(c.approver).action_reconcile, match="Explain")
    doc.with_user(c.officer).write({"variance_note": "Two extra storage days"})
    doc.with_user(c.approver).action_reconcile()
    _refused(lambda: doc.with_user(c.officer).write({"amount": 1.0}), match="evidence")


def test_cost_tolerance_is_configurable(c):
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_import_order.cost_variance_tolerance_pct", "30"
    )
    doc = _cost(c, expected_amount=20000.0)
    doc.with_user(c.approver).action_reconcile()
    assert doc.state == "reconciled"


def test_cost_foreign_currency_needs_rate_and_source(c):
    _refused(lambda: _cost(c, currency_id=c.usd.id, amount=100.0), match="BRU-ITC-14")
    _refused(
        lambda: _cost(c, currency_id=c.usd.id, amount=100.0, rate=118.0),
        match="BRU-ITC-14",
    )
    doc = _cost(c, currency_id=c.usd.id, amount=100.0, rate=118.0, rate_source="AD bank TT")
    assert doc.amount_bdt == pytest.approx(11800.0)


def test_cost_agency_fee_names_its_agent_and_lc_is_the_orders(c):
    _refused(lambda: _cost(c, category="clearing"), match="FR-ITC-030")
    _cost(c, category="clearing", cnf_agent_id=c.agent.id, document_ref="CNF-%s" % c.tag)
    letter = stage_lc_open(c)
    other = (
        c.env["fix.import.order"]
        .with_user(c.officer)
        .create(
            {
                "name": "M44T-OTHER-%s" % c.tag,
                "supplier_id": c.supplier.id,
                "operating_unit_id": c.ou.id,
                "currency_id": c.bdt.id,
                "fob_value": 1000.0,
                "incoterm": "cif",
                "location_id": c.loc.id,
            }
        )
    )
    _refused(
        lambda: _cost(c, order_id=other.id, category="bank", lc_id=letter.id),
        match="belongs to",
    )


def test_rejection_needs_a_reason(c):
    doc = _cost(c)
    _refused(doc.with_user(c.approver).action_reject, match="why")
    doc.with_user(c.approver).action_reject("Duplicate of the agent's bill")
    assert doc.state == "rejected"


def test_landed_sheet_is_filled_from_and_held_to_the_reconciled_documents(c):
    _arr, bill = stage_received(c)
    freight = _cost(c, category="freight", amount=40000.0, document_ref="FR-%s" % c.tag)
    port = _cost(c, category="port", amount=20000.0)
    inland = _cost(c, category="inland", amount=5000.0, document_ref="INL-%s" % c.tag)
    sheet = landed(c)  # typed: freight 45,000, insurance 8,000, clearing 25,000

    # an unreconciled document blocks the final cost (BRU-ITC-16)
    _refused(sheet.with_user(c.approver).action_finalise, match="Reconcile or reject")
    for doc in freight | port | inland:
        doc.with_user(c.approver).action_reconcile()
    # a typed line the documents contradict is refused
    _refused(sheet.with_user(c.approver).action_finalise, match="Freight")

    _refused(
        lambda: sheet.with_user(c.clerk).action_pull_costs(),
        match="role",
    )
    sheet.with_user(c.officer2).action_pull_costs()
    assert sheet.freight == pytest.approx(40000.0)
    assert sheet.clearing_charges == pytest.approx(25000.0)
    assert sheet.insurance == pytest.approx(8000.0)  # no document: kept as typed
    assert sheet.amounts_changed_by_id == c.officer2
    _refused(sheet.with_user(c.officer2).action_finalise, match="role")
    sheet.with_user(c.approver).action_finalise()
    duty = bill.cd_amount + bill.rd_amount + bill.sd_amount
    assert sheet.state == "finalised"
    assert sheet.total_landed == pytest.approx(40000 + 8000 + 25000 + duty)

    # a capitalisable cost after the final cost is not a landed-cost document
    _refused(lambda: _cost(c, document_ref="LATE-%s" % c.tag), match="already applied")
    _cost(c, category="other", document_ref="LATE-OTHER-%s" % c.tag)


def test_close_refuses_an_unreconciled_cost_document(c):
    doc = _cost(c)
    _refused(c.order.with_user(c.approver).action_close, match="BRU-ITC-18")
    doc.with_user(c.approver).action_reject("Not ours")
    _refused(c.order.with_user(c.approver).action_close, match="Landed Cost Applied|close it")


# ================================================================ LC discrepancy
def _discrepancy(c, letter, user=None, **kw):
    vals = {
        "lc_id": letter.id,
        "raised_by_bank": "Negotiating bank",
        "raised_on": c.today,
        "description": "Late shipment: B/L dated after the latest shipment date",
        "discrepancy_fee": 80.0,
        "delay_days": 3,
    }
    vals.update(kw)
    return c.env["fix.import.lc.discrepancy"].with_user(user or c.officer).create(vals)


def test_discrepancy_only_on_an_opened_lc(c):
    from odoo.addons.cd_import_order.tests.test_a06_m44_controls import lc

    _refused(lambda: _discrepancy(c, lc(c)), match="opened LC")


def test_undecided_discrepancy_blocks_payment(c):
    letter = stage_lc_open(c)
    disc = _discrepancy(c, letter)
    assert disc.name.startswith("ILCD/") and disc.order_id == c.order
    Pay = c.env["fix.import.lc.payment"]
    _refused(
        lambda: Pay.with_user(c.finance).create(
            {"lc_id": letter.id, "amount": 1000.0, "reference": "TT-D1"}
        ),
        match="undecided discrepancy",
    )
    _refused(lambda: disc.with_user(c.officer).action_accept("ok"), match="role")
    _refused(lambda: disc.with_user(c.approver).action_accept(""), match="reason")
    disc.with_user(c.approver).action_accept("Waived: goods needed, fee accepted")
    assert disc.state == "accepted" and disc.decided_by_id == c.approver
    Pay.with_user(c.finance).create({"lc_id": letter.id, "amount": 1000.0, "reference": "TT-D1"})
    _refused(lambda: disc.with_user(c.officer).write({"delay_days": 9}), match="final")


def test_discrepancy_recorder_cannot_decide(c):
    letter = stage_lc_open(c)
    both = _user(c.env, "m44t_both_%s" % c.tag, c.ou, OFFICER, APPROVER)
    disc = _discrepancy(c, letter, user=both)
    _refused(lambda: disc.with_user(both).action_refuse("no"), match="Segregation")
    disc.with_user(c.approver).action_refuse("Bank to re-present")
    assert disc.state == "refused"


# ================================================================ customs query
def _query(c, bill, user=None, **kw):
    vals = {
        "boe_id": bill.id,
        "query_type": "valuation",
        "raised_on": c.today,
        "description": "Assessable value below the reference price",
    }
    vals.update(kw)
    return c.env["fix.import.customs.query"].with_user(user or c.officer).create(vals)


def test_unresolved_query_blocks_assessment(c):
    stage_shipped(c)
    bill = boe(c)
    query = _query(c, bill)
    assert query.name.startswith("ICQ/") and query.order_id == c.order
    _refused(bill.with_user(c.officer).action_assess, match="FR-ITC-028")
    _refused(lambda: query.with_user(c.officer).action_resolve("x"), match="answered")
    _refused(lambda: query.with_user(c.officer).action_answer(""), match="response")
    query.with_user(c.officer).action_answer("Supplier invoice and SWIFT copy submitted")
    _refused(bill.with_user(c.officer).action_assess, match="FR-ITC-028")
    _refused(lambda: query.with_user(c.officer).write({"description": "x"}), match="fixed")
    query.with_user(c.officer).action_resolve("Declared value accepted")
    assert query.state == "resolved" and query.resolved_by_id == c.officer
    bill.with_user(c.officer).action_assess()
    assert bill.state == "assessed"
    _refused(lambda: _query(c, bill), match="lodged Bill of Entry")


def test_examination_needs_its_result(c):
    stage_shipped(c)
    bill = boe(c)
    query = _query(c, bill, query_type="examination", description="Physical examination")
    query.with_user(c.officer).action_answer("Container opened at the examination shed")
    _refused(lambda: query.with_user(c.officer).action_resolve("done"), match="examination")
    query.with_user(c.officer).write({"examination_result": "matched"})
    query.with_user(c.officer).action_resolve("Released after examination")
    assert query.state == "resolved"
    _refused(lambda: _query(c, bill, user=c.clerk))


# ================================================================ freight forwarder
def _forwarder(c, status):
    return c.env["fix.supplier"].create(
        {
            "name": "M44T Forwarder %s %s" % (status, c.tag),
            "partner_id": c.env["res.partner"].create({"name": "M44T FWD %s" % c.tag}).id,
            "status": status,
        }
    )


def test_forwarder_must_be_active_in_m42_and_booking_freezes_on_arrival(c):
    from odoo.addons.cd_import_order.tests.test_a06_m44_controls import arrival

    stage_shipped(c)  # an arrival follows a received B/L
    inactive = _forwarder(c, "qualified")
    _refused(lambda: arrival(c, forwarder_id=inactive.id), match="BRU-ITC-12")
    active = _forwarder(c, "active")
    arr = arrival(c, forwarder_id=active.id, carrier="MSC", booking_ref="BK-%s" % c.tag)
    assert arr.forwarder_id == active
    arr.with_user(c.officer).action_arrive()
    _refused(lambda: arr.with_user(c.officer).write({"booking_ref": "BK-2"}), match="fixed")


# ================================================================ P03 form path
def test_cost_document_captured_through_the_workspace_form(c, p03):
    p03.as_user(c.officer)
    out = p03.write(
        model="fix.import.cost",
        values={
            "order_id": c.order.id,
            "category": "freight",
            "billed_by_id": c.supplier.id,
            "document_ref": "WS-%s" % c.tag,
            "incurred_on": str(c.today),
            "amount": 1234.0,
            "currency_id": c.bdt.id,
        },
    )
    assert not out.get("error"), out
    doc = c.env["fix.import.cost"].search([("document_ref", "=", "WS-%s" % c.tag)])
    assert doc and doc.recorded_by_id == c.officer and doc.state == "draft"
    # a stamp is not typed through the workspace
    out = p03.write(model="fix.import.cost", record_id=doc.id, values={"state": "reconciled"})
    doc.invalidate_recordset()
    assert doc.state == "draft", out
    p03.as_user(c.approver)
    out = p03.action(model="fix.import.cost", ids=[doc.id], method="action_reject")
    assert not out["success"]
    out = p03.action(
        model="fix.import.cost", ids=[doc.id], method="action_reject", kwargs={"reason": "Dup"}
    )
    assert out["success"], out
    assert doc.state == "rejected"


def test_discrepancy_and_query_captured_through_the_workspace_form(c, p03):
    letter = stage_lc_open(c)
    p03.as_user(c.officer)
    out = p03.write(
        model="fix.import.lc.discrepancy",
        values={
            "lc_id": letter.id,
            "raised_by_bank": "Bank",
            "raised_on": str(c.today),
            "description": "Invoice description differs",
        },
    )
    assert not out.get("error"), out
    assert letter.discrepancy_ids
    bill = boe(c, boe_no="BE-Q-%s" % c.tag)
    out = p03.write(
        model="fix.import.customs.query",
        values={
            "boe_id": bill.id,
            "query_type": "classification",
            "raised_on": str(c.today - timedelta(days=1)),
            "description": "HS heading questioned",
        },
    )
    assert not out.get("error"), out
    assert bill.query_ids.query_type == "classification"
