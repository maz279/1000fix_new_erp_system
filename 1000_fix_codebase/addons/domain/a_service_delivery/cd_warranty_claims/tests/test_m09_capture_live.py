"""M09 capture audit, second pass (2026-11-18): the records eight M09 pages
could not capture, exercised as NON-ADMIN users against the live ORM.

Each test is one rule from the M09 specification (FR-WTY / BRU-WTY) that the
new record carries: what a person may enter, who may decide it, and what the
decision does to the warranty, the policy, the claim or the money."""

import base64
from datetime import timedelta

from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
WTY_OFFICER = "cd_device_registry.group_warranty_officer"
CLERK = "cd_warranty_claims.group_warranty_claims_clerk"
OFFICER = "cd_warranty_claims.group_warranty_claims_officer"
FINANCE = "account.group_account_manager"


def _as(rec, user):
    return rec.with_user(user)


def _png(tag):
    return base64.b64encode(("m09-%s" % tag).encode())


def _product(wc, **vals):
    return wc.env["fix.warranty.product"].create(
        {
            "name": "Accidental Damage 12m",
            "product_type": "protection",
            "duration_months": 12,
            "waiting_days": 10,
            "claim_limit": 20000.0,
            "excess_amount": 500.0,
            "reserve_rate": 40.0,
            **vals,
        }
    )


def _policy(wc, product=None, start=None, **vals):
    return _as(wc.env["fix.protection.policy"], wc.clerk).create(
        {
            "product_id": (product or _product(wc)).id,
            "partner_id": wc.customer.id,
            "device_id": wc.device.id,
            "premium": 3000.0,
            "term_start": start or wc.today - timedelta(days=60),
            **vals,
        }
    )


def _active_policy(wc, **vals):
    policy = _policy(wc, **vals)
    _as(policy, wc.clerk).action_activate()
    assert policy.state == "active"
    return policy


def _pclaim(wc, policy, incident=None, evidence=True, **vals):
    data = {
        "policy_id": policy.id,
        "incident_date": incident or wc.today - timedelta(days=5),
        "cause": "screen",
        "description": "Dropped on the stairs; screen cracked",
    }
    if evidence:
        data.update(evidence_file=_png("pc"), evidence_filename="crack.jpg")
    data.update(vals)
    return _as(wc.env["fix.protection.claim"], wc.clerk).create(data)


def _assessed(wc, claim, value=6000.0, **vals):
    _as(claim, wc.clerk2).write(
        {
            "assessed_value": value,
            "remedy": "repair",
            "assessment_note": "Panel and digitiser",
            **vals,
        }
    )
    _as(claim, wc.clerk2).action_assess()
    return claim


def _approved_claim(wc, amount=12500.0):
    claim = wc.full_pack(wc.claim(amount=amount))
    _as(claim, wc.clerk).action_submit()
    claim.action_decide(approved=True)  # the brand path
    assert claim.state == "approved"
    return claim


# ------------------------------------------------------------ pages 1/4: void


def test_a_typed_reason_no_longer_voids_a_warranty(wc):
    officer = wc.user("m09_wty_officer", WTY_OFFICER)
    with wc.refused(UserError, "evidenced void condition"):
        _as(wc.warranty, officer).action_void("liquid inside")
    assert wc.warranty.status == "active"


def test_a_void_condition_is_evidenced_and_applied_by_another_officer(wc):
    officer = wc.user("m09_wty_officer", WTY_OFFICER)
    Void = _as(wc.env["fix.warranty.void"], wc.clerk)
    bare = Void.create(
        {"warranty_id": wc.warranty.id, "condition": "liquid_damage", "description": "LCI tripped"}
    )
    assert bare.name.startswith("WVD/")
    with wc.refused(UserError, "no evidence"):
        _as(bare, officer).action_apply()
    with wc.refused(AccessError, "Warranty Officer"):
        _as(bare, wc.clerk2).action_apply()
    void = Void.create(
        {
            "warranty_id": wc.warranty.id,
            "condition": "seal_breach",
            "description": "Seal sticker torn",
            "evidence_file": _png("seal"),
            "evidence_filename": "seal.jpg",
        }
    )
    assert void.evidence_document_id.res_model == "fix.warranty.void"
    # the officer who declared it cannot apply it
    declarer = wc.user("m09_wty_declarer", WTY_OFFICER, CLERK)
    own = _as(wc.env["fix.warranty.void"], declarer).create(
        {
            "warranty_id": wc.warranty.id,
            "condition": "tampering",
            "description": "screws stripped",
            "evidence_document_id": wc.document("tamper").id,
        }
    )
    with wc.refused(AccessError, "Segregation of duties"):
        _as(own, declarer).action_apply()
    with wc.refused(UserError, "Say why"):
        _as(own, officer).action_reject("")
    _as(own, officer).action_reject("Screws were stripped at the factory")
    assert own.state == "rejected" and wc.warranty.status == "active"
    _as(void, officer).action_apply()
    assert (void.state, void.decided_by_id) == ("applied", officer)
    assert wc.warranty.status == "voided" and "Seal" in wc.warranty.void_reason
    with wc.refused(UserError, "closed for edits"):
        _as(void, wc.clerk).write({"description": "changed"})


# ------------------------------------------------------------ page 5: policies


def test_a_policy_is_sold_by_a_clerk_with_its_terms_from_the_product(wc):
    product = _product(wc)
    with wc.refused(AccessError, "Warranty Claims Clerk"):
        _as(wc.env["fix.protection.policy"], wc.plain).create(
            {
                "product_id": product.id,
                "partner_id": wc.customer.id,
                "device_id": wc.device.id,
                "premium": 3000.0,
                "term_start": wc.today,
            }
        )
    with wc.refused(ValidationError, "premium"):
        _policy(wc, product=product, premium=0.0)
    policy = _policy(wc, product=product, start=wc.today)
    assert policy.name.startswith("PPL/") and policy.state == "sold"
    assert (policy.term_end - wc.today).days in (364, 365)  # 12 months, the last day included
    assert policy.waiting_until == wc.today + timedelta(days=10)
    assert (policy.excess, policy.claim_limit) == (500.0, 20000.0)
    with wc.refused(UserError):
        _as(policy, wc.clerk).write({"excess": 0.0})


def test_activation_checks_eligibility_inspection_and_establishes_the_reserve(wc):
    no_reserve = _product(wc, name="No reserve plan", reserve_rate=0.0)
    with wc.refused(UserError, "reserve"):
        _as(_policy(wc, product=no_reserve), wc.clerk).action_activate()
    young = _product(wc, name="New devices only", max_device_age_months=6)
    wc.device.purchase_date = wc.today - timedelta(days=400)
    with wc.refused(UserError, "older than"):
        _as(_policy(wc, product=young), wc.clerk).action_activate()
    inspected = _product(wc, name="Inspected plan", inspection_required=True)
    policy = _policy(wc, product=inspected)
    with wc.refused(UserError, "pre-sale inspection"):
        _as(policy, wc.clerk).action_activate()
    Insp = _as(wc.env["fix.protection.inspection"], wc.clerk)
    with wc.refused(ValidationError, "photograph"):
        Insp.create({"policy_id": policy.id, "condition_grade": "a", "outcome": "pass"})
    insp = Insp.create(
        {
            "policy_id": policy.id,
            "condition_grade": "a",
            "outcome": "pass",
            "photo_file": _png("insp"),
            "photo_filename": "front.jpg",
        }
    )
    with wc.refused(UserError, "record of what happened"):
        _as(insp, wc.clerk).write({"outcome": "fail"})
    _as(policy, wc.clerk).action_activate()
    assert policy.state == "active" and policy.activated_by_id == wc.clerk
    assert policy.reserve_balance == 1200.0  # 40% of 3000
    assert policy.reserve_ids.movement_type == "establish"
    with wc.refused(AccessError):
        _as(wc.env["fix.protection.reserve"], wc.officer).create(
            {"policy_id": policy.id, "movement_type": "adjust", "amount": 1.0, "reason": "x"}
        )
    with wc.refused(UserError, "append-only"):
        policy.reserve_ids.write({"amount": 0.0})


def test_a_failed_inspection_declines_the_policy(wc):
    policy = _policy(wc, product=_product(wc, inspection_required=True))
    _as(wc.env["fix.protection.inspection"], wc.clerk).create(
        {
            "policy_id": policy.id,
            "condition_grade": "d",
            "outcome": "fail",
            "note": "Cracked back glass",
            "photo_file": _png("bad"),
            "photo_filename": "back.jpg",
        }
    )
    assert policy.state == "declined"


def test_cancellation_refunds_pro_rata_and_releases_the_reserve(wc):
    policy = _active_policy(wc, start=wc.today - timedelta(days=100))
    with wc.refused(AccessError, "Claim Decision Officer"):
        _as(policy, wc.clerk).action_cancel("customer asked")
    _as(policy, wc.officer).action_cancel("Customer returned the phone")
    assert policy.state == "cancelled"
    total = (policy.term_end - policy.term_start).days + 1
    unused = (policy.term_end - wc.today).days + 1
    assert policy.refund_amount == round(3000.0 * unused / total, 2) < 3000.0
    assert policy.reserve_balance == 0.0
    assert policy.reserve_ids.filtered(lambda m: m.movement_type == "release")


# ------------------------------------------------------------ page 6: protection claims


def test_a_claim_inside_the_waiting_period_is_rejected_at_intake(wc):
    policy = _active_policy(wc, start=wc.today - timedelta(days=3))
    claim = _pclaim(wc, policy, incident=wc.today - timedelta(days=1))
    assert claim.state == "rejected" and "BRU-WTY-12" in claim.decision_reason
    with wc.refused(ValidationError, "only an active policy"):
        _pclaim(wc, _policy(wc))


def test_a_protection_claim_is_assessed_decided_by_another_and_settled(wc):
    policy = _active_policy(wc)
    claim = _pclaim(wc, policy)
    assert claim.name.startswith("PCL/") and claim.excess_amount == 500.0
    with wc.refused(UserError, "assessed value"):
        _as(claim, wc.clerk2).action_assess()
    _assessed(wc, claim)
    assert claim.state == "assessed" and claim.fraud_score == 40  # incident soon after activation
    for person in (wc.clerk, wc.clerk2):
        with wc.refused((AccessError,)):
            _as(claim, person).action_approve()
    receiver = wc.user("m09_receiver", OFFICER)
    mine = _assessed(
        wc,
        _as(wc.env["fix.protection.claim"], receiver).create(
            {
                "policy_id": policy.id,
                "incident_date": wc.today - timedelta(days=2),
                "cause": "liquid",
                "description": "Rain",
                "evidence_document_id": wc.document("rain").id,
            }
        ),
    )
    with wc.refused(AccessError, "Segregation of duties"):
        _as(mine, receiver).action_approve()
    _as(claim, wc.officer).action_approve()
    assert (claim.state, claim.approved_amount) == ("approved", 5500.0)
    # the reserve covers the incurred claim (1200 established + 4300 adjusted)
    assert policy.reserve_balance == 5500.0
    with wc.refused(UserError, "excess"):
        _as(claim, wc.clerk).action_settle()
    _as(claim, wc.clerk).action_record_excess("RCPT-77")
    with wc.refused(UserError, "fulfilled"):
        _as(claim, wc.clerk).action_settle()
    _as(claim, wc.clerk).write({"fulfilment_type": "repair", "fulfilment_ref": "SO-REPAIR-1"})
    _as(claim, wc.clerk).action_settle()
    assert claim.state == "settled"
    assert (policy.claimed_amount, policy.remaining_limit) == (5500.0, 14500.0)
    assert policy.reserve_balance == 0.0
    event = wc.env["fix.event.outbox"].search(
        [("aggregate_id", "=", claim.id), ("event_type", "=", "protection_claim.settled")]
    )
    assert event


def test_the_limit_is_enforced_and_a_waiver_needs_another_person(wc):
    policy = _active_policy(wc, product=_product(wc, claim_limit=3000.0))
    claim = _assessed(wc, _pclaim(wc, policy), value=9000.0)
    with wc.refused(UserError, "BRU-WTY-14"):
        _as(claim, wc.officer).action_approve()
    _as(claim, wc.officer).action_reject("Beyond the plan's remaining limit")
    assert claim.state == "rejected"
    small = _assessed(wc, _pclaim(wc, policy, incident=wc.today - timedelta(days=4)), value=2500.0)
    _as(small, wc.officer).action_approve()
    with wc.refused(AccessError):
        _as(small, wc.clerk).action_waive_excess("goodwill")
    _as(small, wc.officer2).action_waive_excess("Long-standing customer")
    assert small.excess_state == "waived"


def test_a_high_fraud_score_needs_a_cleared_review_and_a_confirmed_one_blocks(wc):
    policy = _active_policy(wc)
    claim = _assessed(wc, _pclaim(wc, policy, evidence=False), damage_consistent=False)
    assert claim.fraud_score >= 50
    with wc.refused(UserError, "BRU-WTY-21"):
        _as(claim, wc.officer).action_approve()
    Review = wc.env["fix.warranty.fraud.review"]
    with wc.refused(AccessError):
        _as(Review, wc.clerk).create(
            {"protection_claim_id": claim.id, "finding": "cleared", "note": "ok"}
        )
    with wc.refused(ValidationError, "one claim"):
        _as(Review, wc.officer).create({"finding": "cleared", "note": "ok"})
    review = _as(Review, wc.officer2).create(
        {
            "protection_claim_id": claim.id,
            "finding": "cleared",
            "note": "Called the customer; CCTV matches",
        }
    )
    assert review.name.startswith("FRV/") and "Score" in review.signals
    with wc.refused(UserError, "record of what happened"):
        _as(review, wc.officer2).write({"finding": "confirmed"})
    _as(claim, wc.officer).action_approve()
    assert claim.state == "approved"
    other = _assessed(
        wc, _pclaim(wc, policy, evidence=False, incident=wc.today - timedelta(days=3))
    )
    _as(Review, wc.officer2).create(
        {"protection_claim_id": other.id, "finding": "confirmed", "note": "Staged"}
    )
    with wc.refused(UserError, "confirmed fraud"):
        _as(other, wc.officer).action_approve()


# ------------------------------------------------------------ page 8: brand rules


def test_brand_rules_decide_the_pack_and_the_window(wc):
    Rule = wc.env["fix.brand.claim.rule"]
    with wc.refused(AccessError, "Claim Decision Officer"):
        _as(Rule, wc.clerk).create({"brand_id": wc.brand.id})
    rule = _as(Rule, wc.officer).create(
        {
            "brand_id": wc.brand.id,
            "submission_window_days": 10,
            "req_technician_cert": False,
            "req_purchase_proof": False,
        }
    )
    assert rule.version == 1 and rule.state == "draft"
    claim = wc.claim()
    claim.evidence_ids = [
        Command.create({"requirement_key": k, "document_id": wc.document(k).id})
        for k in ("photo_before", "photo_after", "diagnostic", "parts_issued", "device_serial")
    ]
    assert not claim.evidence_complete  # all seven, while no rule is active
    with wc.refused(AccessError, "Segregation of duties"):
        _as(rule, wc.officer).action_activate()
    _as(rule, wc.officer2).action_activate()
    assert rule.state == "active"
    claim.invalidate_recordset(["evidence_complete", "missing_evidence"])
    assert claim.evidence_complete, claim.missing_evidence
    later = wc.claim(so=wc.closed_order())
    assert (later.submission_deadline - later.job_completed_at).days == 10
    with wc.refused(UserError, "new version"):
        _as(rule, wc.officer).write({"submission_window_days": 30})
    v2 = _as(Rule, wc.officer).create({"brand_id": wc.brand.id, "submission_window_days": 5})
    _as(v2, wc.officer2).action_activate()
    assert (v2.version, rule.state) == (2, "retired")


# ------------------------------------------------------------ page 9: information requests


def test_a_brand_request_for_information_is_recorded_and_answered(wc):
    Req = _as(wc.env["fix.warranty.claim.info.request"], wc.clerk)
    draft = wc.claim()
    with wc.refused(ValidationError, "deciding"):
        Req.create({"claim_id": draft.id, "request_text": "IMEI photo", "due_date": wc.today})
    claim = wc.full_pack(wc.claim(so=wc.closed_order()))
    _as(claim, wc.clerk).action_submit()
    req = Req.create(
        {
            "claim_id": claim.id,
            "request_text": "Photo of the IMEI label",
            "due_date": wc.today + timedelta(days=2),
        }
    )
    assert req.name.startswith("RFI/") and not req.overdue
    _as(req, wc.clerk2).action_answer("IMEI label photo sent by portal")
    assert (req.state, req.responded_by_id) == ("answered", wc.clerk2)


# ------------------------------------------------------------ page 10: money


def test_one_brand_payment_is_matched_across_claims_and_the_rest_is_unmatched(wc):
    a = _approved_claim(wc, 12500.0)
    b = _approved_claim(wc, 4000.0)
    rem = _as(wc.env["fix.brand.remittance"], wc.clerk).create(
        {
            "brand_id": wc.brand.id,
            "bank_ref": "BANK-REF-9",
            "total_amount": 17000.0,
            "line_ids": [
                Command.create({"claim_id": a.id, "amount": 12500.0}),
                Command.create({"claim_id": b.id, "amount": 4000.0}),
            ],
        }
    )
    assert rem.unmatched_amount == 500.0
    with wc.refused(AccessError, "Claim Decision Officer"):
        _as(rem, wc.clerk).action_match()
    _as(rem, wc.officer).action_match()
    assert rem.state == "unmatched"  # 500 the lines do not account for stays visible
    assert (a.state, b.state) == ("remitted", "remitted")
    assert "BANK-REF-9" in a.remittance_ref
    with wc.refused(UserError, "record of what the bank received"):
        _as(rem, wc.clerk).write({"total_amount": 16500.0})


def test_a_write_off_is_decided_by_a_finance_manager_who_raised_nothing(wc):
    claim = _approved_claim(wc, 6000.0)
    claim.action_record_remittance(5000.0, "BANK-SHORT")  # short paid
    W = _as(wc.env["fix.claim.writeoff"], wc.clerk)
    with wc.refused(ValidationError, "up to the 1000.00"):
        W.create({"claim_id": claim.id, "amount": 1500.0, "reason": "brand cap"})
    wo = W.create({"claim_id": claim.id, "amount": 1000.0, "reason": "Brand capped labour"})
    with wc.refused(AccessError):
        _as(wo, wc.officer).action_approve()
    # the clerk who submitted the claim, even holding the finance role, may not
    wc.clerk.group_ids = [Command.link(wc.env.ref(FINANCE).id)]
    with wc.refused(AccessError, "BRU-WTY-07"):
        _as(wo, wc.clerk).action_approve()
    finance = wc.user("m09_finance", FINANCE)
    _as(wo, finance).action_approve()
    assert (wo.state, claim.state, claim.written_off_amount) == ("approved", "written_off", 1000.0)
    event = wc.env["fix.event.outbox"].search(
        [("aggregate_id", "=", claim.id), ("event_type", "=", "warranty_claim.written_off")]
    )
    assert event


def test_the_requester_of_a_write_off_cannot_approve_it(wc):
    claim = _approved_claim(wc, 3000.0)
    both = wc.user("m09_fin_both", FINANCE, CLERK)
    wo = _as(wc.env["fix.claim.writeoff"], both).create(
        {"claim_id": claim.id, "amount": 3000.0, "reason": "Brand insolvent"}
    )
    with wc.refused(AccessError, "Segregation of duties"):
        _as(wo, both).action_approve()


def test_the_period_statement_is_computed_and_signed_by_another(wc):
    _approved_claim(wc, 12500.0)
    rec = _as(wc.env["fix.brand.reconciliation"], wc.clerk).create(
        {"brand_id": wc.brand.id, "date_from": wc.today - timedelta(days=30), "date_to": wc.today}
    )
    with wc.refused(UserError, "Compute"):
        _as(rec, wc.officer).action_sign()
    _as(rec, wc.officer).action_compute()
    assert rec.approved >= 12500.0 and rec.outstanding >= 12500.0
    with wc.refused(AccessError, "Segregation of duties"):
        _as(rec, wc.officer).action_sign()
    _as(rec, wc.officer2).action_sign()
    assert rec.state == "signed"
    with wc.refused(UserError, "frozen"):
        _as(rec, wc.clerk).write({"note": "late edit"})


def test_a_brand_that_wants_the_part_back_gets_it_before_the_claim_closes(wc):
    rule = _as(wc.env["fix.brand.claim.rule"], wc.officer).create(
        {"brand_id": wc.brand.id, "requires_defective_return": True}
    )
    _as(rule, wc.officer2).action_activate()
    claim = _approved_claim(wc, 2000.0)
    claim.action_record_remittance(2000.0, "BANK-DPR")
    with wc.refused(UserError, "BRU-WTY-19"):
        _as(claim, wc.officer).action_close()
    ret = _as(wc.env["fix.defective.return"], wc.clerk).create(
        {"claim_id": claim.id, "part_description": "Main board", "part_serial": "MB-1"}
    )
    with wc.refused(UserError, "waybill"):
        _as(ret, wc.clerk).action_ship()
    _as(ret, wc.clerk).write(
        {
            "waybill_ref": "SA-123",
            "shipped_on": wc.today,
            "proof_file": _png("wb"),
            "proof_filename": "wb.pdf",
        }
    )
    _as(ret, wc.clerk).action_ship()
    assert ret.state == "shipped" and not claim.defective_return_pending()


# ------------------------------------------------------------ page 12: outbound fraud


def test_a_confirmed_fraud_review_blocks_brand_submission(wc):
    claim = wc.full_pack(wc.claim())
    Review = wc.env["fix.warranty.fraud.review"]
    # the person who submitted a claim does not review it
    raiser = wc.user("m09_raiser", OFFICER)
    theirs = wc.full_pack(wc.claim(so=wc.closed_order()))
    _as(theirs, raiser).action_submit()
    with wc.refused(AccessError, "Segregation of duties"):
        _as(Review, raiser).create({"claim_id": theirs.id, "finding": "cleared", "note": "fine"})
    _as(Review, wc.officer).create(
        {"claim_id": claim.id, "finding": "confirmed", "note": "Parts claimed were never issued"}
    )
    with wc.refused(UserError, "FR-WTY-051"):
        _as(claim, wc.clerk).action_submit()
    assert claim.state == "draft"


# ------------------------------------------------------------ the workspace path


def test_the_new_lists_decide_through_the_workspace_whitelist(wc):
    from .test_a04_m09_controls import _workspace

    officer = wc.user("m09_ws_officer", WTY_OFFICER)
    void = _as(wc.env["fix.warranty.void"], wc.clerk).create(
        {
            "warranty_id": wc.warranty.id,
            "condition": "liquid_damage",
            "description": "LCI red",
            "evidence_document_id": wc.document("lci").id,
        }
    )
    res = _workspace(wc.env(user=officer.id))("fix.warranty.void", void, "action_apply")
    assert res["success"], res
    assert wc.warranty.status == "voided"
    res = _workspace(wc.env(user=officer.id))("fix.warranty", wc.warranty, "action_unlink")
    assert not res["success"]
