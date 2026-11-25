"""A04 ERP audit (20 Nov 2026), stream B3: the brand claim's value,
uniqueness and window, and the protection plan's limits.

  M09-F4  the claim asked for the VAT-inclusive estimate, not the M11 rate
  M09-F5  a second claim on the same order was accepted; no cancel
  M09-F6  two approved claims overran the aggregate limit; reserve covered one
  M09-F10 a claim 20 days past the brand's window was accepted; no LAPSED
  M09-F15 a policy's terms stayed writable after activation
Non-admin users on the live ORM, rolled back (``odoo_env``)."""

import base64
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_warranty_claims.group_warranty_claims_officer"


def _rate(wc, labour=800.0, markup=10.0, level="l1"):
    rate = (
        wc.env["fix.brand.reimbursement.rate"]
        .sudo()
        .create(
            {
                "brand_id": wc.brand.id,
                "repair_level": level,
                "labour_rate": labour,
                "parts_markup_pct": markup,
                "valid_from": wc.today - timedelta(days=400),
                "company_id": wc.env.company.id,
            }
        )
    )
    rate._guarded().write({"state": "active"})
    return rate


# ------------------------------------------------------------ M09-F4
def test_f4_a_claim_is_valued_at_the_released_brand_rate_ex_vat(wc):
    rate = _rate(wc)
    so = wc.closed_order(total=2000.0)  # estimate: 2000 parts + 15% VAT = 2300
    claim = (
        wc.env["fix.warranty.claim"]
        .with_user(wc.clerk)
        .create({"operating_unit_id": wc.ou.id, "service_order_id": so.id, "brand_id": wc.brand.id})
    )
    # 800 labour + 2000 parts x 1.10 = 3000.00 (not the 2300 the customer was quoted)
    assert claim.claim_amount == 3000.0
    assert (claim.rate_id, claim.valuation_basis, claim.parts_value) == (rate, "brand_rate", 2000.0)
    with pytest.raises(ValidationError, match="not a typed figure"), wc.env.cr.savepoint():
        wc.env["fix.warranty.claim"].with_user(wc.clerk2).create(
            {
                "operating_unit_id": wc.ou.id,
                "service_order_id": wc.closed_order(total=2000.0).id,
                "brand_id": wc.brand.id,
                "claim_amount": 2300.0,
            }
        )


def test_f4_without_a_brand_rate_the_estimate_is_claimed_ex_vat_and_flagged(wc):
    so = wc.closed_order(total=2000.0)
    claim = (
        wc.env["fix.warranty.claim"]
        .with_user(wc.clerk)
        .create({"operating_unit_id": wc.ou.id, "service_order_id": so.id, "brand_id": wc.brand.id})
    )
    assert (claim.claim_amount, claim.valuation_basis, claim.rate_id.id) == (
        2000.0,
        "estimate",
        False,
    )
    # the owner's switch: no released rate, no claim value
    wc.env["ir.config_parameter"].sudo().set_param("cd_warranty_claims.require_brand_rate", "1")
    with pytest.raises(UserError, match="no approved estimate"), wc.env.cr.savepoint():
        claim.with_user(wc.clerk).action_refresh_amount()
    so2 = wc.closed_order(total=2000.0)
    with pytest.raises(ValidationError, match="no approved estimate"), wc.env.cr.savepoint():
        wc.env["fix.warranty.claim"].with_user(wc.clerk).create(
            {"operating_unit_id": wc.ou.id, "service_order_id": so2.id, "brand_id": wc.brand.id}
        )


def test_f4_the_repair_level_reads_its_own_rate(wc):
    _rate(wc)
    _rate(wc, labour=1500.0, markup=0.0, level="l2")
    so = wc.closed_order(total=2000.0)
    claim = (
        wc.env["fix.warranty.claim"]
        .with_user(wc.clerk)
        .create(
            {
                "operating_unit_id": wc.ou.id,
                "service_order_id": so.id,
                "brand_id": wc.brand.id,
                "repair_level": "l2",
            }
        )
    )
    assert claim.claim_amount == 3500.0
    claim.with_user(wc.clerk).write({"repair_level": "l1"})
    assert claim.claim_amount == 3000.0


# ------------------------------------------------------------ M09-F5
def test_f5_one_live_claim_per_order_and_a_cancelled_one_frees_it(wc):
    so = wc.closed_order(total=2000.0)
    Claim = wc.env["fix.warranty.claim"]
    first = Claim.with_user(wc.clerk).create(
        {"operating_unit_id": wc.ou.id, "service_order_id": so.id, "brand_id": wc.brand.id}
    )
    with (
        pytest.raises(ValidationError, match="already has a warranty claim"),
        wc.env.cr.savepoint(),
    ):
        Claim.with_user(wc.clerk2).create(
            {"operating_unit_id": wc.ou.id, "service_order_id": so.id, "brand_id": wc.brand.id}
        )
    with pytest.raises(UserError, match="Say why"), wc.env.cr.savepoint():
        first.with_user(wc.clerk).action_cancel("")
    with pytest.raises(AccessError), wc.env.cr.savepoint():
        first.with_user(wc.plain).action_cancel("duplicate")
    first.with_user(wc.clerk).action_cancel("raised on the wrong brand")
    assert (first.state, first.cancelled_by_id) == ("cancelled", wc.clerk)
    second = Claim.with_user(wc.clerk2).create(
        {"operating_unit_id": wc.ou.id, "service_order_id": so.id, "brand_id": wc.brand.id}
    )
    assert second.state == "draft"


def test_f5_a_submitted_claim_is_withdrawn_by_an_officer_a_decided_one_is_not(wc):
    claim = wc.full_pack(wc.claim(amount=5000.0))
    claim.with_user(wc.clerk).action_submit()
    with pytest.raises(AccessError), wc.env.cr.savepoint():
        claim.with_user(wc.clerk).action_cancel("brand asked")
    claim.with_user(wc.officer).action_cancel("withdrawn: brand asked us to resubmit")
    assert claim.state == "cancelled"
    decided = wc.full_pack(wc.claim(amount=5000.0))
    decided.with_user(wc.clerk).action_submit()
    decided.action_decide(approved=True)
    with pytest.raises(UserError, match="written off"), wc.env.cr.savepoint():
        decided.with_user(wc.officer).action_cancel("changed our mind")


# ------------------------------------------------------------ M09-F10
def test_f10_a_claim_past_its_window_lapses_and_needs_an_officer(wc):
    claim = wc.full_pack(wc.claim(amount=5000.0))
    claim._guarded().write({"submission_deadline": fields.Datetime.now() - timedelta(days=20)})
    with pytest.raises(UserError, match="lapsed"), wc.env.cr.savepoint():
        claim.with_user(wc.clerk).action_submit()
    wc.env["fix.warranty.claim"].cron_claim_overdue_escalation()
    assert claim.state == "lapsed" and claim.lapsed_at
    new_window = fields.Datetime.now() + timedelta(days=2)
    with pytest.raises(AccessError), wc.env.cr.savepoint():
        claim.with_user(wc.clerk).action_extend_deadline(new_window, "brand ok")
    claim.with_user(wc.officer).action_extend_deadline(new_window, "Brand email REF-77 accepts it")
    assert claim.state in ("draft", "ready") and claim.deadline_extended_by_id == wc.officer
    claim.with_user(wc.clerk).action_submit()
    assert claim.state == "submitted"


# ------------------------------------------------------------ M09-F6 / F15
def _product(wc, **vals):
    return wc.env["fix.warranty.product"].create(
        {
            "name": "AD plan",
            "product_type": "protection",
            "duration_months": 12,
            "waiting_days": 0,
            "claim_limit": 10000.0,
            "excess_amount": 0.0,
            "reserve_rate": 40.0,
            **vals,
        }
    )


def _assessed(wc, policy, value):
    claim = (
        wc.env["fix.protection.claim"]
        .with_user(wc.clerk)
        .create(
            {
                "policy_id": policy.id,
                "incident_date": wc.today - timedelta(days=1),
                "cause": "screen",
                "description": "Cracked",
                "evidence_file": base64.b64encode(("b3-%s" % value).encode()),
                "evidence_filename": "crack.jpg",
            }
        )
    )
    claim.with_user(wc.clerk2).write(
        {"assessed_value": value, "remedy": "repair", "assessment_note": "Panel"}
    )
    claim.with_user(wc.clerk2).action_assess()
    return claim


def test_f6_approved_claims_count_against_the_limit_and_the_reserve_covers_all(wc):
    policy = (
        wc.env["fix.protection.policy"]
        .with_user(wc.clerk)
        .create(
            {
                "product_id": _product(wc).id,
                "partner_id": wc.customer.id,
                "device_id": wc.device.id,
                "premium": 3000.0,
                "term_start": wc.today - timedelta(days=60),
            }
        )
    )
    policy.with_user(wc.clerk).action_activate()
    a = _assessed(wc, policy, 7500.0)
    b = _assessed(wc, policy, 7500.0)
    for claim in (a, b):
        if claim.fraud_score >= 50:
            wc.env["fix.warranty.fraud.review"].with_user(wc.officer2).create(
                {"protection_claim_id": claim.id, "finding": "cleared", "note": "checked"}
            )
    a.with_user(wc.officer).action_approve()
    assert policy.remaining_limit == 2500.0  # approved, not yet settled, counts
    with pytest.raises(UserError, match="BRU-WTY-14"), wc.env.cr.savepoint():
        b.with_user(wc.officer).action_approve()
    c = _assessed(wc, policy, 2000.0)
    if c.fraud_score >= 50:
        wc.env["fix.warranty.fraud.review"].with_user(wc.officer2).create(
            {"protection_claim_id": c.id, "finding": "cleared", "note": "checked"}
        )
    c.with_user(wc.officer).action_approve()
    policy.invalidate_recordset()
    # reserve covers both approved, unsettled claims (7500 + 2000)
    assert policy.reserve_balance == 9500.0
    for claim in (a, c):
        claim.with_user(wc.clerk).write(
            {"fulfilment_type": "repair", "fulfilment_ref": "SO-%s" % claim.id}
        )
    a.with_user(wc.clerk).action_settle()
    assert policy.state == "active"  # c is still owed: not exhausted, reserve kept
    assert policy.reserve_balance == 2000.0
    c.with_user(wc.clerk).action_settle()
    assert policy.committed_amount == 9500.0 <= policy.claim_limit


def test_f15_an_active_policys_cover_is_fixed(wc):
    policy = (
        wc.env["fix.protection.policy"]
        .with_user(wc.clerk)
        .create(
            {
                "product_id": _product(wc).id,
                "partner_id": wc.customer.id,
                "device_id": wc.device.id,
                "premium": 3000.0,
                "term_start": wc.today - timedelta(days=10),
            }
        )
    )
    policy.with_user(wc.clerk).action_activate()
    with pytest.raises(UserError, match="cover the customer bought"), wc.env.cr.savepoint():
        policy.with_user(wc.clerk).write({"premium": 1.0})


# ------------------------------------------------------------ B5 brand authorisation (gated)
def test_brand_authorisation_gate_blocks_submission_only_when_switched_on(wc):
    if "fix.partner.authorisation" not in wc.env:
        pytest.skip("M40 partner authorisations not installed")
    claim = wc.full_pack(wc.claim(amount=5000.0))
    params = wc.env["ir.config_parameter"].sudo()
    params.set_param("cd_warranty_claims.require_brand_authorisation", "1")
    with pytest.raises(UserError, match="BRU-PCM-08"), wc.env.cr.savepoint():
        claim.with_user(wc.clerk).action_submit()
    params.set_param("cd_warranty_claims.require_brand_authorisation", "0")
    claim.with_user(wc.clerk).action_submit()
    assert claim.state == "submitted"
