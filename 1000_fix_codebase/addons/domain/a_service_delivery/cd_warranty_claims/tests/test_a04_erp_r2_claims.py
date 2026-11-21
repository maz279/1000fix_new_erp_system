"""A04 ERP audit, round 2 (21 Nov 2026), stream R2-2: the deferred M09 items.

  M09-F13 brand rule flags (certified technician, labour allowance, fault
          code scheme, resubmission window) enforced; parts-issued evidence
          is the M15 issue record, not a name match
  M09-F16 outbound submission record with resubmission history and the
          brand's reference; brand fault codes through the M37 brand map
  M09-F12 ageing buckets on the OEM receivable and the chase cron
  M09-F15 per-claim limit, claim-count limit, depreciation, value-band
          routing through M63
Non-admin users on the live ORM, rolled back (``odoo_env``)."""

import base64
import uuid
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import assigned, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
TIER1 = "cd_entity_config.group_dofa_tier_1"


def _rule(wc, **vals):
    """An ACTIVE brand rule set: written by one officer, activated by another."""
    rule = (
        wc.env["fix.brand.claim.rule"]
        .with_user(wc.officer)
        .create({"brand_id": wc.brand.id, "submission_window_days": 30, **vals})
    )
    rule.with_user(wc.officer2).action_activate()
    return rule


def _employee(wc, name):
    return wc.env["hr.employee"].create({"name": "%s %s" % (name, TAG)})


def _work_order(wc, so, tech, minutes, code=None):
    start = fields.Datetime.now() - timedelta(hours=5)
    return wc.env["fix.work.order"].create(
        {
            "order_id": so.id,
            "technician_id": tech.id if tech else False,
            "start_time": start,
            "end_time": start + timedelta(minutes=minutes),
            "diagnosed_fault_code": code or False,
        }
    )


def _certify(wc, tech, brand):
    competency = wc.env["fix.competency"].create(
        {"code": "R2C%s" % uuid.uuid4().hex[:5], "name": "Brand repair %s" % TAG}
    )
    return wc.env["fix.certification"].create(
        {
            "employee_id": tech.id,
            "competency_id": competency.id,
            "brand_id": brand.id,
            "issued_on": wc.today - timedelta(days=30),
            "expires_on": wc.today + timedelta(days=300),
        }
    )


def _submitted_claim(wc, amount=5000.0):
    claim = wc.full_pack(wc.claim(amount=amount))
    claim.with_user(wc.clerk).action_submit()
    return claim


def _m15_issue(wc, so):
    part = wc.env["fix.spare.part"].create(
        {"name": "Board %s" % TAG, "part_number": "R2P-%s" % uuid.uuid4().hex[:6]}
    )
    location = wc.env["fix.stock.location"].create(
        {"name": "R2 store %s" % TAG, "code": "R2%s" % uuid.uuid4().hex[:5].upper()}
    )
    issue = wc.env["fix.stock.consumption"].create(
        {
            "service_order_ref": so.name,
            "product_id": part.id,
            "location_id": location.id,
            "technician_id": _employee(wc, "Issuing tech").id,
            "quantity": 1.0,
            "scanned_code": part.part_number,
            "operating_unit_id": wc.ou.id,
        }
    )
    issue._guarded().write({"state": "consumed"})
    return issue


# ------------------------------------------------------------ M09-F13 certification
def test_f13_only_certified_work_is_claimed_when_the_brand_requires_it(wc):
    _rule(wc, requires_certified_technician=True)
    tech = _employee(wc, "Uncertified")
    wc.order.sudo().write({"technician_id": tech.id})
    claim = wc.full_pack(wc.claim(amount=5000.0))
    with wc.refused(UserError, "BRU-WTY-10"):
        claim.with_user(wc.clerk).action_submit()
    # a certification for ANOTHER brand does not count
    _certify(wc, tech, wc.other_brand)
    with wc.refused(UserError, "BRU-WTY-10"):
        claim.with_user(wc.clerk).action_submit()
    _certify(wc, tech, wc.brand)
    claim.with_user(wc.clerk).action_submit()
    assert claim.state == "submitted"


def test_f13_without_an_active_rule_no_certification_is_asked(wc):
    wc.order.sudo().write({"technician_id": _employee(wc, "Anyone").id})
    claim = _submitted_claim(wc)
    assert claim.state == "submitted"


# ------------------------------------------------------------ M09-F13 labour
def test_f13_labour_beyond_the_brands_allowance_is_blocked(wc):
    _rule(wc, labour_allowance_minutes=60)
    # no technician on the work order: M22 gates assignment, not this rule
    tech = None
    claim = wc.full_pack(wc.claim(amount=5000.0))
    with wc.refused(UserError, "no labour time"):
        claim.with_user(wc.clerk).action_submit()
    wo = _work_order(wc, wc.order, tech, 90)
    with wc.refused(UserError, "90 minutes of labour exceeds"):
        claim.with_user(wc.clerk).action_submit()
    wo.write({"end_time": wo.start_time + timedelta(minutes=45)})
    claim.with_user(wc.clerk).action_submit()
    assert (claim.state, claim.labour_minutes) == ("submitted", 45)


# ------------------------------------------------------------ M09-F13 / F16 fault codes
def test_f13_the_brands_code_scheme_needs_every_code_translated(wc):
    _rule(wc, code_scheme="WCL-GSX")
    claim = wc.full_pack(wc.claim(amount=5000.0))
    with wc.refused(UserError, "carries no fault code"):
        claim.with_user(wc.clerk).action_submit()
    code = "R2PW%s" % uuid.uuid4().hex[:4].upper()
    wc.env["fix.service.order.fault"].create(
        {"order_id": wc.order.id, "fault_code": code, "description": "No power"}
    )
    with wc.refused(UserError, "FR-WTY-043"):
        claim.with_user(wc.clerk).action_submit()
    fault = wc.env["fix.fault.code"].create({"code": code, "name": "No power"})
    wc.env["fix.fault.brand.map"].create(
        {"fault_id": fault.id, "brand_id": wc.brand.id, "brand_code": "GSX-P01"}
    )
    claim.with_user(wc.clerk).action_submit()
    assert claim.brand_fault_codes == "%s=GSX-P01" % code
    assert claim.submission_ids.brand_codes == claim.brand_fault_codes


# ------------------------------------------------------------ M09-F13 parts issued
def test_f13_parts_evidence_must_be_the_m15_issue_of_this_job(wc):
    _rule(wc)  # req_parts_issued is on by default
    so = wc.closed_order(total=2000.0)
    claim = wc.claim(so=so, amount=2000.0)
    assert claim.parts_value == 2000.0
    claim.evidence_ids = [
        Command.create({"requirement_key": key, "document_id": wc.document(key, so=so).id})
        for key in (
            "photo_before",
            "photo_after",
            "diagnostic",
            "parts_issued",
            "device_serial",
            "technician_cert",
            "purchase_proof",
        )
    ]
    # parts claimed, nothing issued from stock
    with wc.refused(UserError, "no part was issued from stock"):
        claim.with_user(wc.clerk).action_submit()
    _m15_issue(wc, so)
    # a file named "parts_issued.jpg" is not the issue record
    with wc.refused(UserError, "not the M15 issue record"):
        claim.with_user(wc.clerk).action_submit()
    claim.evidence_ids.filtered(lambda e: e.requirement_key == "parts_issued").with_user(
        wc.clerk
    ).unlink()
    claim.with_user(wc.clerk).action_assemble_workshop_evidence_pack()
    item = claim.evidence_ids.filtered(lambda e: e.requirement_key == "parts_issued")
    assert item.document_id.res_model == "fix.stock.consumption" and item.evidence_hash
    claim.with_user(wc.clerk).action_submit()
    assert claim.state == "submitted"


def test_f13_assembly_no_longer_matches_parts_evidence_by_name(wc):
    so = wc.closed_order(total=2000.0)
    wc.document("parts_issued", so=so)  # a file whose name says parts_issued
    claim = wc.claim(so=so, amount=2000.0)
    claim.with_user(wc.clerk).action_assemble_workshop_evidence_pack()
    assert not claim.evidence_ids.filtered(lambda e: e.requirement_key == "parts_issued")


# ------------------------------------------------------------ M09-F16 submissions
def test_f16_each_sending_is_recorded_and_the_brand_reference_once(wc):
    claim = _submitted_claim(wc)
    sub = claim.submission_ids
    assert (len(sub), sub.attempt, sub.kind, sub.submitted_by_id) == (1, 1, "submission", wc.clerk)
    assert sub.payload_sha256 and '"amount": 5000.0' in sub.payload
    with pytest.raises(UserError), wc.env.cr.savepoint():
        sub.with_user(wc.clerk).write({"claim_amount": 1.0})
    with pytest.raises(AccessError), wc.env.cr.savepoint():
        claim.with_user(wc.plain).action_record_brand_reference("BR-1")
    claim.with_user(wc.clerk).action_record_brand_reference("BR-%s" % TAG)
    assert sub.brand_reference == "BR-%s" % TAG
    with wc.refused(UserError, "already carries"):
        claim.with_user(wc.clerk2).action_record_brand_reference("BR-2")


# ------------------------------------------------------------ M09-F13 resubmission window
def test_f13_resubmission_only_inside_the_brands_window(wc):
    _rule(wc, resubmission_window_days=7)
    claim = _submitted_claim(wc)
    claim.action_decide(False, reason="Photo unreadable")
    claim._guarded().write({"decided_at": fields.Datetime.now() - timedelta(days=10)})
    Appeal = wc.env["fix.claim.appeal"].with_user(wc.clerk)
    with wc.refused(ValidationError, "resubmission within 7 days"):
        Appeal.create({"name": "AP late", "claim_id": claim.id, "reason": "clear photo"})
    claim._guarded().write({"decided_at": fields.Datetime.now() - timedelta(days=2)})
    appeal = Appeal.create({"name": "AP", "claim_id": claim.id, "reason": "clear photo"})
    claim._guarded().write({"decided_at": fields.Datetime.now() - timedelta(days=9)})
    with wc.refused(UserError, "not resubmitted"):
        appeal.with_user(wc.officer).action_uphold("brand accepts")
    claim._guarded().write({"decided_at": fields.Datetime.now() - timedelta(days=3)})
    appeal.with_user(wc.officer).action_uphold("brand accepts the new photo")
    assert claim.state == "submitted"
    assert claim.submission_ids.mapped("kind") == ["submission", "resubmission"]
    assert claim.submission_ids[-1].appeal_id == appeal


# ------------------------------------------------------------ M09-F12 ageing and chase
def test_f12_unpaid_receivable_ages_in_buckets_and_is_chased_by_level(wc):
    claim = _submitted_claim(wc)
    claim.action_decide(True)
    claim._guarded().write({"decided_at": fields.Datetime.now() - timedelta(days=35)})
    claim.invalidate_recordset()
    assert (claim.receivable_outstanding, claim.ageing_bucket) == (5000.0, "b31_60")
    Claim = wc.env["fix.warranty.claim"]
    assert claim in Claim.with_user(wc.officer).search([("ageing_bucket", "=", "b31_60")])
    assert claim not in Claim.search([("ageing_bucket", "=", "b0_30")])
    Activity = wc.env["mail.activity"]
    before = Activity.search_count([("res_model", "=", claim._name), ("res_id", "=", claim.id)])
    Claim.cron_chase_oem_receivables()
    acts = Activity.search([("res_model", "=", claim._name), ("res_id", "=", claim.id)])
    assert claim.chase_level == 1 and len(acts) == before + 1
    assert acts[-1:].user_id.has_group("cd_warranty_claims.group_warranty_claims_officer")
    Claim.cron_chase_oem_receivables()  # same level: not chased again
    assert Activity.search_count(
        [("res_model", "=", claim._name), ("res_id", "=", claim.id)]
    ) == len(acts)
    claim._guarded().write({"decided_at": fields.Datetime.now() - timedelta(days=65)})
    Claim.cron_chase_oem_receivables()
    assert claim.chase_level == 2 and claim.ageing_bucket == "b61_90"
    # paid in full: no longer owed, no longer aged
    claim.with_user(wc.officer).action_record_remittance(5000.0, "BANK-%s" % TAG)
    claim.invalidate_recordset()
    assert (claim.receivable_outstanding, claim.ageing_bucket) == (0.0, False)


# ------------------------------------------------------------ M09-F15 plan limits
def _product(wc, **vals):
    return wc.env["fix.warranty.product"].create(
        {
            "name": "R2 plan %s" % TAG,
            "product_type": "protection",
            "duration_months": 12,
            "claim_limit": 0.0,
            "reserve_rate": 40.0,
            **vals,
        }
    )


def _policy(wc, product, days_ago=100):
    policy = (
        wc.env["fix.protection.policy"]
        .with_user(wc.clerk)
        .create(
            {
                "product_id": product.id,
                "partner_id": wc.customer.id,
                "device_id": wc.device.id,
                "premium": 3000.0,
                "term_start": wc.today - timedelta(days=days_ago),
            }
        )
    )
    policy.with_user(wc.clerk).action_activate()
    return policy


def _assessed(wc, policy, value, remedy="replace"):
    claim = (
        wc.env["fix.protection.claim"]
        .with_user(wc.clerk)
        .create(
            {
                "policy_id": policy.id,
                "incident_date": wc.today - timedelta(days=1),
                "cause": "screen",
                "description": "Cracked",
                "evidence_file": base64.b64encode(("r2-%s-%s" % (value, uuid.uuid4())).encode()),
                "evidence_filename": "crack.jpg",
            }
        )
    )
    claim.with_user(wc.clerk2).write(
        {"assessed_value": value, "remedy": remedy, "assessment_note": "Panel"}
    )
    claim.with_user(wc.clerk2).action_assess()
    if claim.fraud_score >= 50:
        wc.env["fix.warranty.fraud.review"].with_user(wc.officer2).create(
            {"protection_claim_id": claim.id, "finding": "cleared", "note": "checked"}
        )
    return claim


def test_f15_depreciation_and_the_per_claim_limit_set_the_payable(wc):
    product = _product(
        wc,
        per_claim_limit=9000.0,
        depreciation_pct_per_month=2.0,
        depreciation_cap_pct=30.0,
        depreciation_basis="replace",
    )
    policy = _policy(wc, product, days_ago=100)  # 3 full months of cover: 6%
    assert (policy.per_claim_limit, policy.depreciation_pct_per_month) == (9000.0, 2.0)
    repair = _assessed(wc, policy, 5000.0, remedy="repair")
    repair.with_user(wc.officer).action_approve()
    assert (repair.approved_amount, repair.depreciation_amount) == (5000.0, 0.0)  # replace only
    replace = _assessed(wc, policy, 9000.0)
    replace.with_user(wc.officer).action_approve()
    assert (replace.approved_amount, replace.depreciation_amount) == (8460.0, 540.0)
    big = _assessed(wc, policy, 20000.0)
    big.with_user(wc.officer).action_approve()
    assert big.approved_amount == 9000.0  # 20000 - 6% = 18800, capped
    assert "per-claim limit" in big.payable_note


def test_f15_the_claim_count_limit_refuses_one_claim_too_many(wc):
    policy = _policy(wc, _product(wc, max_claim_count=1))
    first = _assessed(wc, policy, 1000.0)
    second = _assessed(wc, policy, 1000.0)
    first.with_user(wc.officer).action_approve()
    with wc.refused(UserError, "claim-count limit"):
        second.with_user(wc.officer).action_approve()


def test_f15_a_policy_keeps_the_limits_it_was_sold_with(wc):
    product = _product(wc, per_claim_limit=1000.0)
    policy = _policy(wc, product)
    product.write({"per_claim_limit": 99999.0})
    assert policy.per_claim_limit == 1000.0
    with wc.refused(UserError):
        policy.with_user(wc.clerk).write({"per_claim_limit": 5.0})
    with wc.refused(ValidationError, "between 0 and 100"):
        product.write({"depreciation_pct_per_month": 150.0})


def test_f15_a_claim_above_a_value_band_is_routed_through_m63(wc):
    params = wc.env["ir.config_parameter"].sudo()
    params.set_param("cd_warranty_claims.protection_claim_dofa_bands", "5000:tier_1")
    tier1 = wc.user("r2_tier1_%s" % TAG.lower(), TIER1)
    policy = _policy(wc, _product(wc))
    small = _assessed(wc, policy, 3000.0)
    small.with_user(wc.officer).action_approve()
    assert small.state == "approved"  # below every band: the officer decides
    big = _assessed(wc, policy, 7500.0)
    big.with_user(wc.officer).action_approve()
    assert (big.state, big.approval_state, big.dofa_band_tier) == ("assessed", "pending", "tier_1")
    assert tier1 in assigned(big) and wc.officer not in assigned(big)
    with wc.refused(UserError, "approver's inbox"):
        big.with_user(tier1).action_apply_band_approval()
    inbox_task(big, tier1).with_user(tier1).action_approve(comment="within band")
    assert (big.state, big.approved_amount, big.decided_by_id) == ("approved", 7500.0, tier1)
    params.set_param("cd_warranty_claims.protection_claim_dofa_bands", "lots:tier_9")
    other = _assessed(wc, policy, 6000.0)
    with wc.refused(UserError, "malformed"):
        other.with_user(wc.officer).action_approve()


def test_f15_with_no_bands_configured_nothing_extra_is_routed(wc):
    wc.env["ir.config_parameter"].sudo().set_param(
        "cd_warranty_claims.protection_claim_dofa_bands", ""
    )
    claim = _assessed(wc, _policy(wc, _product(wc)), 50000.0)
    claim.with_user(wc.officer).action_approve()
    assert (claim.state, claim.approval_state) == ("approved", "none")


def test_f16_brand_performance_pack_measures_approval_pay_time_and_short_pay(wc):
    from odoo.addons.cd_p03_portal.controllers.a04.m09 import brand_performance

    paid = _submitted_claim(wc, 5000.0)
    paid.action_decide(True)
    paid.with_user(wc.officer).action_record_remittance(4000.0, "BANK-SHORT-%s" % TAG)
    refused = _submitted_claim(wc, 3000.0)
    refused.action_decide(False, reason="Out of warranty")
    pack = brand_performance(wc.env(user=wc.officer), wc.today, wc.today)
    row = next(r for r in pack["rows"] if r["brand"] == wc.brand.name)
    assert (row["submitted"], row["approval_pct"]) == (2, 50.0)
    assert (row["short_pay_pct"], row["short_pay_amount_pct"]) == (100.0, 20.0)
    assert row["days_to_pay"] is not None
    earlier = brand_performance(wc.env, wc.today - timedelta(days=10), wc.today - timedelta(days=5))
    assert not [r for r in earlier["rows"] if r["brand"] == wc.brand.name]


# ------------------------------------------------------------ M37-F5 (with R2-3)
def test_m37_f5_a_warranty_product_resolves_to_its_catalogue_definition(wc):
    code = "R2WP-%s" % uuid.uuid4().hex[:6].upper()
    tmpl = wc.env["product.template"].create({"name": "Care %s" % code, "default_code": code})
    product = _product(wc, catalogue_item_id=tmpl.id)
    assert not product.catalogue_def_id  # the template has no catalogue item yet
    item = wc.env["fix.catalogue.item"].create(
        {"product_tmpl_id": tmpl.id, "item_type": "protection"}
    )
    assert product.catalogue_def_id == item
    assert wc.env["fix.warranty.product"].search([("catalogue_def_id", "=", item.id)]) == product


# ------------------------------------------------------------ wiring
class TestDeployment:
    def test_cron_acl_rules_and_surfaces_exist(self, odoo_env):
        env = odoo_env
        cron = env.ref("cd_warranty_claims.ir_cron_warranty_claim_chase")
        assert cron.active and "cron_chase_oem_receivables" in cron.code
        assert env.ref("cd_warranty_claims.access_fix_warranty_claim_submission").perm_read
        assert env.ref("cd_warranty_claims.rule_fix_warranty_claim_submission_company")
        matrix = dict(env["fix.approval.matrix"]._fields["decision_domain"].selection)
        assert "protection_claim_decision" in matrix
        from odoo.addons.cd_p03_portal.controllers.a04 import m09

        assert "fix.warranty.claim.submission" in m09.SURFACES
        assert "action_record_brand_reference" in m09.SURFACES["fix.warranty.claim"]["actions"]
        assert "brand_performance" in m09.REPORTS
