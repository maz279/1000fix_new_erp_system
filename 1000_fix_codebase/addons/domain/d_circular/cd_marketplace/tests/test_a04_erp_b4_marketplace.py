# ruff: noqa: F811  (the marketplace fixture is imported and used as a parameter)
"""A04 ERP audit (20 Nov 2026), stream B4 - M12 marketplace money and controls.

M12-F1  commission is earned and accrued only on the customer's money
        received in M20; the accrual debits that collection (AR / customer),
        never the static 101404 cash account
M12-F9  the output VAT on the commission (M51 declared D-03 position) is
        booked and deducted from the seller's share
M12-F2  "Payout Complete" only from the M53 discharge
M12-F3  dispute_resolved / chargeback_lost are consumed
M12-F4  no award before the seller commission scheme is configured
M12-F5  the seller board shows open and quoted jobs
M12-F8  KYC needs its documents
M12-F10 one commission rate (pinned at award)
M12-F11 a CFO-approved seller's categories are not changed under the approval
M12-F12 SOD-06: the seller's CFO approver does not approve its payout
M12-F13 order and dispute sequences
M12-F16 the tier is restored when the escalated dispute is resolved
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_billing_engine.models.fix_finance_approval import GROUP_ACCOUNTANT

from .b4_helpers import seller_scheme
from .test_a04_m12_controls import (  # noqa: F401
    ARBITRATOR,
    CHARGEBACK,
    DISPUTE,
    OPERATOR,
    QUOTE,
    SELLER,
    _job_evidence,
    mk,
)


def _accounts(mk):
    env = mk.env
    params = env["ir.config_parameter"].sudo()

    def account(code, kind):
        return env["account.account"].create(
            {"code": code, "name": "B4 %s" % code, "account_type": kind}
        )

    acc = {
        "ar": account("B4MAR1", "asset_receivable"),
        "vat": account("B4MVT1", "liability_current"),
        "rev": account("B4MRV1", "income"),
        "pay": account("B4MPY1", "liability_current"),
    }
    params.set_param("cd_billing_engine.account_code.ar", acc["ar"].code)
    params.set_param("cd_billing_engine.account_code.vat_output", acc["vat"].code)
    params.set_param("cd_settlement_ext.account_code.commission_revenue", acc["rev"].code)
    params.set_param("cd_settlement_ext.account_code.seller_payable", acc["pay"].code)
    params.set_param("cd_settlement_ext.account_code.marketplace_collections", False)
    params.set_param("cd_settlement_ext.account_code.clearing", "101404")
    return acc


def _declared_agent_vat(env, rate=15.0):
    """The M51 D-03 position, declared (setup as the superuser: its own
    adviser / CFO sign-off is M51's suite)."""
    Model = env["fix.marketplace.tax.model"].sudo()
    row = Model.create(
        {
            "company_id": env.company.id,
            "model": "agent",
            "rate": rate,
            "external_opinion_ref": "B4-D03",
            "date_from": "2026-01-01",
        }
    )
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_marketplace_tax_model SET state='active', signoff_state='signed', "
        "verify_with_adviser=false WHERE id=%s",
        (row.id,),
    )
    env.invalidate_all()
    # ... and the IFRS 15 presentation of the same D-03 decision (M53)
    Presentation = env.get("fix.revenue.presentation")
    if Presentation is not None:
        pos = Presentation.sudo().create(
            {
                "company_id": env.company.id,
                "arrangement": "marketplace",
                "position": "agent",
                "decision_ref": "B4-D03",
                "opinion_ref": "B4-OPINION",
                "effective_from": "2026-01-01",
            }
        )
        pos._guarded().write({"state": "active"})
    env.invalidate_all()
    return row


def _earned_row(mk, price=4000.0):
    order = mk.reviewed(price=price)
    order.with_user(mk.operator).action_earn_commission()
    out = (
        mk.env["fix.a04.finance.consumers"]
        .sudo()
        .consume_commission_earned(
            {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
        )
    )
    return order, mk.env["fix.commission.ledger"].sudo().browse(out["id"])


def _acct(mk, login="b4_mkt_acct"):
    return mk.user(login, "base.group_user", GROUP_ACCOUNTANT)


# ============================================================ M12-F1 / F9
def test_f1_no_commission_on_money_never_received(mk):
    o, _q = mk.awarded(price=4000.0)
    as_op = o.with_user(mk.operator)
    as_op.action_start_job()
    _job_evidence(o)
    as_op.action_complete()
    as_op.action_review(rating=5)
    with mk.refused(match="no confirmed M20 receipt"):
        as_op.action_earn_commission()


def test_f1_receipt_is_checked_and_recorded_by_finance(mk):
    o, _q = mk.awarded(price=4000.0)
    other = mk.env["res.partner"].create({"name": "B4 other customer"})
    wrong = (
        mk.env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "customer_id": other.id,
                "amount": 4000.0,
                "method": "bkash",
                "reference": "B4W",
                "state": "confirmed",
            }
        )
    )
    short = (
        mk.env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "customer_id": mk.customer.id,
                "amount": 100.0,
                "method": "bkash",
                "reference": "B4S",
                "state": "confirmed",
            }
        )
    )
    acct = _acct(mk)
    with mk.refused(match="Accountant"):
        o.with_user(mk.operator).action_record_customer_receipt(short)
    with mk.refused(match="not from the customer"):
        o.with_user(acct).action_record_customer_receipt(wrong)
    with mk.refused(match="awarded price"):
        o.with_user(acct).action_record_customer_receipt(short)


def test_f1_f9_accrual_debits_the_collection_and_books_vat(mk):
    acc = _accounts(mk)
    _declared_agent_vat(mk.env)
    order, row = _earned_row(mk, 4000.0)
    assert row.commission_rate == pytest.approx(0.10)
    row.with_user(_acct(mk)).action_post_to_gl()
    move = row.gl_move_id
    lines = {
        (ln.account_id.code, ln.partner_id.id or False): (ln.debit, ln.credit)
        for ln in move.line_ids
    }
    receipt = order.sudo().customer_receipt_id
    assert lines == {
        (acc["ar"].code, receipt.customer_id.commercial_partner_id.id): (4000.0, 0.0),
        (acc["rev"].code, False): (0.0, 400.0),
        (acc["vat"].code, False): (0.0, 60.0),
        (acc["pay"].code, row.seller_partner_id.id): (0.0, 3540.0),
    }
    assert "101404" not in [ln.account_id.code for ln in move.line_ids]
    assert (row.vat_amount, row.net_payable) == (60.0, 3540.0 - (row.tds_amount or 0.0))


def test_f9_no_declared_vat_position_no_accrual(mk):
    _accounts(mk)
    _order, row = _earned_row(mk, 4000.0)
    with mk.refused(match="BRU-TAX-17|D-03"):
        row.with_user(_acct(mk)).action_post_to_gl()


# ============================================================ M12-F2
def test_f2_payout_complete_only_from_the_discharge(mk):
    order, _row = _earned_row(mk, 4000.0)
    # the escrow has run (setup): every other guard of the payout is met
    env = mk.env
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_marketplace_order SET delivery_confirmed_at = %s, completed_at = %s WHERE id = %s",
        [
            fields.Datetime.now() - timedelta(days=8),
            fields.Datetime.now() - timedelta(days=9),
            order.id,
        ],
    )
    order.invalidate_recordset()
    order._compute_payout_escrow()
    with mk.refused(match="payout run"):
        order.with_user(mk.operator).action_paid()
    from odoo.addons.cd_p03_portal.controllers.a04 import m12

    assert "action_paid" not in m12.SURFACES["fix.marketplace.order"]["actions"]


# ============================================================ M12-F3
def test_f3_dispute_ruling_refunds_the_customer_from_m20(mk):
    env = mk.env
    order, _row = _earned_row(mk, 4000.0)
    seller = order.selected_quote_id.seller_id
    dispute = (
        env[DISPUTE]
        .with_user(mk.operator)
        .create(
            {
                "order_id": order.id,
                "seller_id": seller.id,
                "customer_id": mk.customer.id,
                "disputed_amount": 4000.0,
                "description": "never fixed",
            }
        )
    )
    dispute.sudo().action_resolve(resolution_type="refund_customer", notes="ruled")
    out = (
        env[DISPUTE]
        .sudo()
        .consume_dispute_resolved({"aggregate": DISPUTE, "aggregate_id": dispute.id})
    )
    refund = env["fix.ar.refund"].sudo().browse(out["refund"]["id"])
    assert refund.amount == 4000.0 and refund.receipt_id == order.sudo().customer_receipt_id
    assert refund.method == "bkash"
    # idempotent
    again = (
        env[DISPUTE]
        .sudo()
        .consume_dispute_resolved({"aggregate": DISPUTE, "aggregate_id": dispute.id})
    )
    assert again["refund"]["id"] == refund.id and not again["refund"]["created"]


def test_f3_lost_chargeback_recovers_from_a_paid_seller(mk):
    env = mk.env
    order, row = _earned_row(mk, 4000.0)
    row._guarded().write({"state": "paid"})  # setup: the seller was paid
    cb = (
        env[CHARGEBACK]
        .with_user(mk.operator)
        .create({"order_id": order.id, "amount": 1000.0, "gateway_ref": "CB-B4"})
    )
    cb.with_user(mk.operator).action_accept(note="no contest")
    out = (
        env[CHARGEBACK]
        .sudo()
        .consume_chargeback_lost({"aggregate": CHARGEBACK, "aggregate_id": cb.id})
    )
    claw = env["fix.settlement.adjustment"].sudo().browse(out["id"])
    assert claw.adjustment_type == "clawback" and claw.state == "draft"
    assert claw.amount == 900.0  # the seller's share of 1,000 at 10%


# ============================================================ M12-F4 / F10
def test_f4_no_award_without_a_commission_scheme(mk):
    env = mk.env
    env["fix.commission.scheme"].sudo().search([("scheme_type", "=", "seller")]).write(
        {"active": False}
    )
    with mk.refused(match="commission scheme"):
        mk.awarded(price=4000.0)


def test_f10_the_rate_pinned_at_award_is_the_ledger_rate(mk):
    env = mk.env
    env["fix.commission.scheme"].sudo().search([("scheme_type", "=", "seller")]).write(
        {"active": False}
    )
    scheme = seller_scheme(env, rate=0.12)
    order = mk.reviewed(price=4000.0)
    assert order.commission_rate == pytest.approx(0.12)  # pinned at award
    # the scheme changes after the award: the order keeps its one rate, and
    # the ledger row raised from it takes that rate, not a second one
    scheme.write({"commission_rate": 0.20})
    order.with_user(mk.operator).action_earn_commission()
    out = (
        env["fix.a04.finance.consumers"]
        .sudo()
        .consume_commission_earned(
            {"aggregate": "fix.marketplace.order", "aggregate_id": order.id, "payload": {}}
        )
    )
    row = env["fix.commission.ledger"].sudo().browse(out["id"])
    assert row.commission_rate == pytest.approx(0.12)
    assert row.commission_amount == pytest.approx(480.0)


# ============================================================ M12-F5
def test_f5_other_sellers_still_see_a_quoted_job(mk):
    env = mk.env
    o, _q = mk.order(), None
    seller_a = mk.seller("B4 A")
    env[QUOTE].create({"marketplace_order_id": o.id, "seller_id": seller_a.id, "quoted_price": 900})
    assert o.state == "quoted"
    portal = mk.seller_user
    assert env(user=portal)["fix.marketplace.order"].search([("id", "=", o.id)])


# ============================================================ M12-F8
def test_f8_kyc_needs_documents(mk):
    env = mk.env
    seller = mk.seller("B4 KYC", ready=False)
    with mk.refused(match="KYC documents"):
        seller.with_user(mk.operator).action_submit_kyc(
            nid_number="1234567890", trade_license_no="TL-B4", tin_number="123456789012"
        )
    env["ir.attachment"].create(
        {"name": "nid.pdf", "datas": "UERG", "res_model": SELLER, "res_id": seller.id}
    )
    seller.with_user(mk.operator).action_submit_kyc(
        nid_number="1234567890", trade_license_no="TL-B4", tin_number="123456789012"
    )
    assert seller.kyc_doc_z4_ref.startswith("attachment:")
    seller.with_user(mk.compliance).action_verify_kyc()
    assert seller.kyc_status == "verified"
    # a legacy made-up token is not verified
    legacy = mk.seller("B4 legacy", ready=False)
    legacy.write({"trade_license_no": "TL-L", "tin_number": "123456789013"})
    legacy._guarded().write({"kyc_status": "in_review", "kyc_doc_z4_ref": "z4-token-1-2"})
    with mk.refused(match="no KYC documents"):
        legacy.with_user(mk.compliance).action_verify_kyc()


# ============================================================ M12-F11
def test_f11_category_change_withdraws_cfo_approval(mk):
    env = mk.env
    seller = mk.seller("B4 categories")
    categ = env["product.category"].create({"name": "B4 categ"})
    assert seller.cfo_approved
    seller.with_user(mk.operator).write({"category_ids": [(4, categ.id)]})
    assert not seller.cfo_approved


# ============================================================ M12-F12
def test_f12_cfo_approver_conflicts_with_the_payout(mk):
    env = mk.env
    seller = mk.seller("B4 SOD")
    seller._guarded().write({"cfo_approved_by": mk.cfo.id})
    run = env["fix.payout.run"].sudo().new({"company_id": env.company.id})
    ledger = env["fix.commission.ledger"].sudo().new({"seller_partner_id": seller.partner_id.id})
    run.commission_ids = ledger
    assert mk.cfo in run._fin_extra_conflicts()


# ============================================================ M12-F13 / F16
def test_f13_orders_and_disputes_are_numbered(mk):
    order = mk.order()
    assert order.name.startswith("MKT/") and order.name != "MKT/New"
    o, q = mk.awarded()
    d = (
        mk.env[DISPUTE]
        .with_user(mk.operator)
        .create(
            {
                "order_id": o.id,
                "seller_id": q.seller_id.id,
                "customer_id": mk.customer.id,
                "description": "late",
            }
        )
    )
    assert d.name.startswith("DSP/") and d.name != "DSP/New"


def test_f16_tier_restored_after_the_escalation_is_resolved(mk):
    env = mk.env
    o, q = mk.awarded()
    seller = q.seller_id
    seller._guarded().write({"tier": "gold"})
    d = (
        env[DISPUTE]
        .with_user(mk.operator)
        .create(
            {
                "order_id": o.id,
                "seller_id": seller.id,
                "customer_id": mk.customer.id,
                "description": "late",
            }
        )
    )
    d.with_user(mk.operator).action_escalate()
    assert seller.tier == "at_risk"
    d.sudo().action_resolve(resolution_type="payout_seller", notes="dismissed")
    assert seller.tier == "unrated"  # no measured score: back to unrated, not at_risk


class TestDeployment:
    def test_consumers_and_sequences(self, odoo_env):
        env = odoo_env
        for xmlid, event, model in (
            (
                "cd_marketplace.consumer_marketplace_dispute_resolved",
                "marketplace.dispute_resolved",
                DISPUTE,
            ),
            (
                "cd_marketplace.consumer_marketplace_chargeback_lost",
                "marketplace.chargeback_lost",
                CHARGEBACK,
            ),
        ):
            row = env.ref(xmlid)
            assert (row.event_type, row.model) == (event, model)
            assert hasattr(env[model], row.method)
        for code in ("fix.marketplace.order", "fix.marketplace.dispute"):
            assert env["ir.sequence"].sudo().search_count([("code", "=", code)])
        rule = env.ref("cd_marketplace.rule_fix_marketplace_order_seller")
        assert "quoted" in rule.domain_force
        assert ARBITRATOR and OPERATOR
