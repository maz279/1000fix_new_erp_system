"""A04 ERP audit (20 Nov 2026), stream B3: the M09 money legs on M20 / the GL.

R3 / R5 findings:
  M09-F1 / X4  the OEM receivable dead-lettered: no brand billing partner
  M09-F2       protection premium, reserve, settlement and refund posted nothing
  M09-F3       an approved claim write-off left the OEM invoice open, no GL
  M09-F7       an appeal re-decision left the old OEM invoice on AR
  M09-F9       the reimbursement credited 400100, not 400110
  M09-F14      the unallocated part of a brand remittance was never booked
Real users, the live ORM, rolled back. Journal lines are checked by account.
"""

import base64
from datetime import timedelta

import pytest
from odoo import Command
from odoo.addons.cd_billing_engine.tests.test_a04_c7_claim_consumer import (
    _invoices,
    _relay,
    _submitted,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
ROLE = "cd_billing_engine.account_code."
FINANCE = "account.group_account_manager"
ACCOUNTANT = "account.group_account_user"


@pytest.fixture
def m(w):
    env = w.env
    params = env["ir.config_parameter"].sudo()

    def account(key, kind):
        return env["account.account"].create(
            {"code": "B3%s%d" % (key, w.brand.id), "name": "B3 %s" % key, "account_type": kind}
        )

    w.acc = {
        "ar": account("AR", "asset_receivable"),
        "bank": account("BNK", "asset_cash"),
        "vat_output": account("VAT", "liability_current"),
        "revenue": account("REV", "income"),
        "deferred_revenue": account("DEF", "liability_current"),
        "warranty_claim_income": account("WCI", "income"),
        "warranty_provision": account("PRV", "liability_current"),
        "warranty_cost": account("WCE", "expense"),
        "writeoff_expense": account("BDX", "expense"),
        "channel_mfs": account("MFS", "asset_current"),
    }
    for role, acc in w.acc.items():
        params.set_param(ROLE + role, acc.code)
    w.oem = env["res.partner"].create(
        {"name": "OEM Legal Entity %s" % w.brand.name, "is_company": True}
    )
    w.finance = w.user("b3_finance", FINANCE)
    w.acct = w.user("b3_accountant", ACCOUNTANT)
    w.acct2 = w.user("b3_accountant_two", ACCOUNTANT)
    return w


def _lines(move, env):
    """(code, debit, credit) of the move's non-zero lines."""
    return sorted(
        (line.account_id.with_company(move.company_id).code, line.debit, line.credit)
        for line in move.line_ids
        if line.debit or line.credit
    )


def _decided(m, approved=True, amount=None, reason=None):
    claim = _submitted(m)
    claim.action_decide(approved=approved, approved_amount=amount, reason=reason or "")
    claim.invalidate_recordset()
    _relay(m.env)
    return claim


# ------------------------------------------------------------ M09-F1 / X4
def test_f1_the_receivable_is_raised_on_the_brands_billing_partner(m):
    m.brand.partner_id = m.oem  # no partner carries the brand code as ref
    claim = _decided(m)
    (invoice,) = _invoices(m.env, claim)
    assert invoice.customer_id == m.oem and invoice.state == "draft"


def test_f1_no_billing_partner_refuses_with_what_to_link(m):
    claim = _submitted(m)
    claim.action_decide(approved=True)
    event = (
        m.env["fix.event.outbox"]
        .sudo()
        .search(
            [("event_type", "=", "warranty_claim.decided"), ("aggregate_id", "=", claim.id)],
            limit=1,
        )
    )._relay_event_dict()
    with pytest.raises(UserError, match="OEM Billing Partner"), m.env.cr.savepoint():
        m.env["fix.a04.claim.consumers"].consume_warranty_claim_decided(event)
    assert not _invoices(m.env, claim)


def test_f1_creating_brand_partners_is_an_administrators_master_data_step(m):
    with pytest.raises(AccessError), m.env.cr.savepoint():
        m.brand.with_user(m.finance).action_create_billing_partner()
    m.other_brand.action_create_billing_partner()
    assert m.other_brand.partner_id.ref == m.other_brand.code


# ------------------------------------------------------------ M09-F9
def test_f9_the_reimbursement_credits_warranty_claim_income(m):
    m.brand.partner_id = m.oem
    claim = _decided(m)
    (invoice,) = _invoices(m.env, claim)
    invoice.action_issue()
    assert _lines(invoice.posted_move_id, m.env) == sorted(
        [
            (m.acc["ar"].code, claim.approved_amount, 0.0),
            (m.acc["warranty_claim_income"].code, 0.0, claim.approved_amount),
        ]
    )
    assert "pending the M51/owner decision" in " ".join(invoice.message_ids.mapped("body"))


# ------------------------------------------------------------ M09-F7
def _appeal_upheld(m, claim):
    appeal = (
        m.env["fix.claim.appeal"]
        .with_user(m.clerk)
        .create(
            {
                "name": "Appeal %s" % claim.claim_no,
                "claim_id": claim.id,
                "reason": "Brand under-paid",
            }
        )
    )
    appeal.with_user(m.officer2).action_uphold("evidence re-sent")
    assert claim.state == "submitted"
    return appeal


def test_f7_a_rejection_on_appeal_credits_the_issued_oem_invoice(m):
    m.brand.partner_id = m.oem
    claim = _decided(m, amount=1500.0, reason="labour cap")
    assert claim.state == "partially_approved"
    (invoice,) = _invoices(m.env, claim)
    invoice.action_issue()
    _appeal_upheld(m, claim)
    claim.action_decide(approved=False, reason="Rejected after review")
    _relay(m.env)
    (note,) = invoice.credit_note_ids
    assert (note.amount, note.reason_code, note.state) == (
        1500.0,
        "warranty_claim",
        "pending_approval",
    )
    note.with_user(m.acct).action_approve()
    note.with_user(m.acct2).action_issue()
    invoice.invalidate_recordset()
    assert invoice.amount_residual == 0.0


def test_f7_a_higher_re_decision_raises_a_supplementary_draft(m):
    m.brand.partner_id = m.oem
    claim = _decided(m, amount=1500.0, reason="labour cap")
    (first,) = _invoices(m.env, claim)
    first.action_issue()
    _appeal_upheld(m, claim)
    claim.action_decide(approved=True)  # in full this time
    _relay(m.env)
    extra = m.env["fix.ar.invoice"].search(
        [
            ("source_model", "=", "fix.warranty.claim.decision"),
            ("source_id", "in", claim.decision_ids.ids),
        ]
    )
    assert extra.state == "draft"
    assert round(extra.total_payable, 2) == round(claim.approved_amount - 1500.0, 2)


def test_f7_a_draft_oem_invoice_is_dropped_not_credited(m):
    m.brand.partner_id = m.oem
    claim = _decided(m, amount=1500.0, reason="labour cap")
    (first,) = _invoices(m.env, claim)
    _appeal_upheld(m, claim)
    claim.action_decide(approved=False, reason="Rejected after review")
    _relay(m.env)
    assert first.state == "cancelled" and not first.credit_note_ids


# ------------------------------------------------------------ M09-F3
def test_f3_an_approved_write_off_writes_off_the_oem_invoice_and_posts(m):
    m.brand.partner_id = m.oem
    claim = _decided(m, amount=1500.0, reason="labour cap")
    (invoice,) = _invoices(m.env, claim)
    invoice.action_issue()
    claim.with_user(m.officer).action_record_remittance(1200.0, "BANK-SHORT")
    wo = (
        m.env["fix.claim.writeoff"]
        .with_user(m.clerk2)
        .create({"claim_id": claim.id, "amount": 300.0, "reason": "Brand will not pay the rest"})
    )
    wo.with_user(m.finance).action_approve()
    ar_wo = wo.ar_writeoff_id
    assert (ar_wo.state, ar_wo.amount, ar_wo.expense_amount) == ("posted", 300.0, 300.0)
    assert _lines(ar_wo.move_id, m.env) == sorted(
        [(m.acc["writeoff_expense"].code, 300.0, 0.0), (m.acc["ar"].code, 0.0, 300.0)]
    )
    invoice.invalidate_recordset()
    assert invoice.amount_residual == 0.0 and invoice.state == "written_off"
    assert claim.state == "written_off"


def test_f3_a_write_off_waits_for_the_issued_receivable(m):
    m.brand.partner_id = m.oem
    claim = _decided(m, amount=1500.0, reason="labour cap")  # its invoice is still a draft
    wo = (
        m.env["fix.claim.writeoff"]
        .with_user(m.clerk2)
        .create({"claim_id": claim.id, "amount": 500.0, "reason": "dispute"})
    )
    with pytest.raises(UserError, match="issued first"), m.env.cr.savepoint():
        wo.with_user(m.finance).action_approve()
    assert wo.state == "requested" and claim.state == "partially_approved"


def test_f3_a_partial_write_off_keeps_the_rest_owing(m):
    m.brand.partner_id = m.oem
    claim = _decided(m, amount=1500.0, reason="labour cap")
    (invoice,) = _invoices(m.env, claim)
    invoice.action_issue()
    wo = (
        m.env["fix.claim.writeoff"]
        .with_user(m.clerk2)
        .create({"claim_id": claim.id, "amount": 500.0, "reason": "part disputed"})
    )
    wo.with_user(m.finance).action_approve()
    invoice.invalidate_recordset()
    assert invoice.state == "issued" and invoice.amount_residual == 1000.0
    assert wo.ar_writeoff_id.move_id


# ------------------------------------------------------------ M09-F2
def _product(m, **vals):
    return m.env["fix.warranty.product"].create(
        {
            "name": "Accidental Damage 12m",
            "product_type": "protection",
            "duration_months": 12,
            "waiting_days": 0,
            "claim_limit": 10000.0,
            "excess_amount": 0.0,
            "reserve_rate": 40.0,
            **vals,
        }
    )


def _policy(m, start=None):
    policy = (
        m.env["fix.protection.policy"]
        .with_user(m.clerk)
        .create(
            {
                "product_id": _product(m).id,
                "partner_id": m.customer.id,
                "device_id": m.device.id,
                "premium": 3450.0,
                "term_start": start or m.today - timedelta(days=30),
            }
        )
    )
    policy.with_user(m.clerk).action_activate()
    return policy


def test_f2_activation_raises_the_premium_and_posts_the_reserve(m):
    policy = _policy(m)
    invoice = policy.premium_invoice_id.sudo()
    assert (invoice.state, invoice.customer_id, invoice.total_payable) == (
        "draft",
        m.customer,
        3450.0,
    )
    assert (invoice.vat_amount, invoice.total_payable - invoice.vat_amount) == (450.0, 3000.0)
    (reserve,) = policy.reserve_ids
    assert _lines(reserve.move_id, m.env) == sorted(
        [
            (m.acc["warranty_cost"].code, 1380.0, 0.0),
            (m.acc["warranty_provision"].code, 0.0, 1380.0),
        ]
    )
    invoice.action_issue()
    # the premium is a contract liability, released over the cover term
    assert _lines(invoice.posted_move_id, m.env) == sorted(
        [
            (m.acc["ar"].code, 3450.0, 0.0),
            (m.acc["deferred_revenue"].code, 0.0, 3000.0),
            (m.acc["vat_output"].code, 0.0, 450.0),
        ]
    )
    sched = m.env["fix.revenue.schedule"].search(
        [("source_model", "=", "fix.ar.invoice"), ("source_id", "=", invoice.id)]
    )
    assert (sched.state, sched.total_amount, sched.start_date, sched.end_date) == (
        "active",
        3000.0,
        policy.term_start,
        policy.term_end,
    )


def test_f2_cancellation_credits_the_refund_and_stops_the_deferral(m):
    policy = _policy(m)
    invoice = policy.premium_invoice_id.sudo()
    invoice.action_issue()
    policy.with_user(m.officer).action_cancel("customer returned the phone")
    note = policy.refund_credit_note_id
    assert note.invoice_id == invoice and note.amount == policy.refund_amount
    assert note.reason_code == "protection_refund" and note.state == "pending_approval"
    sched = m.env["fix.revenue.schedule"].search(
        [("source_model", "=", "fix.ar.invoice"), ("source_id", "=", invoice.id)]
    )
    assert sched.state == "cancelled"
    # recognised + the refund's ex-VAT part = what was deferred
    taxable_part, _vat = note._vat_split()
    assert round(sched.recognized_amount + taxable_part, 2) == 3000.0
    release = policy.reserve_ids.filtered(lambda r: r.movement_type == "release")
    assert release.move_id and _lines(release.move_id, m.env) == sorted(
        [
            (m.acc["warranty_provision"].code, 1380.0, 0.0),
            (m.acc["warranty_cost"].code, 0.0, 1380.0),
        ]
    )


def test_f2_a_cash_settlement_is_a_treasury_payment_on_the_provision(m):
    if "fix.payment.execution" not in m.env:
        pytest.skip("treasury (M50) is not installed")
    policy = _policy(m, start=m.today - timedelta(days=60))
    claim = (
        m.env["fix.protection.claim"]
        .with_user(m.clerk)
        .create(
            {
                "policy_id": policy.id,
                "incident_date": m.today - timedelta(days=2),
                "cause": "screen",
                "description": "Cracked",
                "evidence_file": base64.b64encode(b"b3-crack"),
                "evidence_filename": "crack.jpg",
            }
        )
    )
    claim.with_user(m.clerk2).write(
        {"assessed_value": 2000.0, "remedy": "replace", "assessment_note": "Panel"}
    )
    claim.with_user(m.clerk2).action_assess()
    claim.with_user(m.officer).action_approve()
    claim.with_user(m.clerk).write({"fulfilment_type": "cash", "fulfilment_ref": "CASH-1"})
    claim.with_user(m.clerk).action_settle()
    pay = m.env["fix.payment.execution"].search(
        [("source_model", "=", "fix.protection.claim"), ("source_id", "=", claim.id)]
    )
    assert pay and pay.amount == 2000.0 and claim.payment_ref == pay.name
    release = policy.reserve_ids.filtered(lambda r: r.claim_id == claim and r.amount < 0)
    assert release and not release.move_id  # the payment, not the movement, debits it


# ------------------------------------------------------------ M09-F14
def test_f14_the_unallocated_part_of_a_remittance_is_booked(m):
    m.brand.partner_id = m.oem
    claim = _decided(m, amount=1500.0, reason="labour cap")
    (invoice,) = _invoices(m.env, claim)
    invoice.action_issue()
    rem = (
        m.env["fix.brand.remittance"]
        .with_user(m.clerk)
        .create(
            {
                "brand_id": m.brand.id,
                "bank_ref": "BANK-B3",
                "total_amount": 2000.0,
                "line_ids": [Command.create({"claim_id": claim.id, "amount": 1500.0})],
            }
        )
    )
    rem.with_user(m.officer).action_match()
    receipt = rem.unmatched_receipt_id
    assert (receipt.state, receipt.amount, receipt.customer_id) == ("confirmed", 500.0, m.oem)
    with pytest.raises(REFUSED), m.env.cr.savepoint():
        rem.line_ids.with_user(m.clerk).write({"amount": 1.0})
