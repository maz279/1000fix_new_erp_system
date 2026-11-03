# Behavioural tests for the M33 registry-screen surfaces (2026-10-27
# rebuild): OTP log, registration approvals, duplicate candidates,
# supervised merges, quality scoring, data-subject requests, segments,
# credit profiles, and the party-status lifecycle. Same `odoo_env`
# convention as test_party_master_behaviour.py — rolled back after every
# test, nothing persists.
import json

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


def _partner(env, name="Test Party", **vals):
    return env["res.partner"].create({"name": name, **vals})


def _steward(env):
    """A second internal user for the segregation-of-duties checks — with
    Contact write access (the merge moves res.partner-owned records)."""
    existing = env["res.users"].search([("login", "=", "m33-steward-test")], limit=1)
    if existing:
        return existing
    return env["res.users"].create(
        {
            "name": "M33 Steward (test)",
            "login": "m33-steward-test",
            "email": "steward@test.invalid",
            # A03 audit M33-6: merges are a data-steward decision.
            "group_ids": [
                (
                    6,
                    0,
                    [
                        env.ref("base.group_user").id,
                        env.ref("base.group_partner_manager").id,
                        env.ref("cd_party_master.group_party_data_steward").id,
                    ],
                )
            ],
        }
    )


def _notice(env, version="1.0"):
    return env["fix.transparency.notice"].create(
        {"version": version, "text_en": "Notice EN", "text_bn": "বিজ্ঞপ্তি"}
    )


def _granted_consent(env, partner, **extra):
    return env["fix.consent"].create(
        {
            "partner_id": partner.id,
            "purpose": "marketing",
            "channel": "sms",
            "proof": "OTP-1",
            "notice_version_id": _notice(env).id,
            **extra,
        }
    )


def _events(env, event_type, aggregate, aggregate_id):
    return env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", aggregate_id),
        ]
    )


# --- fix.transparency.notice ---------------------------------------------------


def test_notice_version_is_unique(odoo_env):
    _notice(odoo_env, version="2.0")
    with pytest.raises(IntegrityError):
        _notice(odoo_env, version="2.0")


# --- fix.otp.log ---------------------------------------------------------------


def test_otp_verification_emits_contact_point_event(odoo_env):
    partner = _partner(odoo_env)
    log = odoo_env["fix.otp.log"].create(
        {"partner_id": partner.id, "channel": "mobile", "destination_masked": "01***4471"}
    )
    log.action_mark_verified(channel_ref="SMS-77")
    assert log.state == "verified"
    assert log.verified_at
    events = _events(odoo_env, "contact_point.verified", "res.partner", partner.id)
    assert json.loads(events.payload) == {"channel": "mobile"}


# --- fix.registration.approval (BRU-CPM-02) -------------------------------------


def test_admin_cannot_approve_before_the_line_manager(odoo_env):
    partner = _partner(odoo_env, "Corporate Ltd")
    approval = odoo_env["fix.registration.approval"].create(
        {"partner_id": partner.id, "party_class": "corporate"}
    )
    with pytest.raises(ValidationError, match="BRU-CPM-02"):
        approval.action_admin_approve()


def _approver(env, login, *xmlids):
    groups = [env.ref("base.group_user").id, env.ref("base.group_partner_manager").id]
    groups += [env.ref(x).id for x in xmlids]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": login, "login": login, "group_ids": [(6, 0, groups)]})
    )


def test_two_tier_approval_activates_the_party_and_emits(odoo_env):
    partner = _partner(odoo_env, "Dealer Rahman & Sons")
    approval = odoo_env["fix.registration.approval"].create(
        {"partner_id": partner.id, "party_class": "dealer"}
    )
    # BRU-CPM-02 is a two-PERSON chain: neither step may be the requester's,
    # and the administrator may not be the line manager. Since A03 audit
    # M33-1 each step is decided from the M63 approval inbox.
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    lm = _approver(odoo_env, "lm.approver@a03.test", "cd_party_master.group_party_registration_lm")
    admin = _approver(
        odoo_env, "admin.approver@a03.test", "cd_party_master.group_party_registration_admin"
    )
    approve_via_inbox(approval, lm)
    approve_via_inbox(approval, admin)
    assert approval.lm_state == "approved" and approval.admin_state == "approved"
    partner.invalidate_recordset()
    assert partner.party_status == "active"
    assert _events(odoo_env, "party.activated", "res.partner", partner.id)


# --- res.partner party_status lifecycle (BRU-CPM-13) ----------------------------


def test_blacklisted_party_cannot_be_reactivated(odoo_env):
    partner = _partner(odoo_env)
    partner.write({"party_status": "active"})
    partner.write({"party_status": "blacklisted"})
    with pytest.raises(ValidationError, match="BRU-CPM-13"):
        partner.write({"party_status": "active"})


def test_merged_tombstone_is_restored_only_by_merge_reversal(odoo_env):
    partner = _partner(odoo_env)
    partner.write({"party_status": "merged"})
    with pytest.raises(ValidationError, match="reversing its merge"):
        partner.write({"party_status": "active"})


# --- fix.party.duplicate + fix.party.merge --------------------------------------


def _merge_fixture(env):
    victim = _partner(env, "Dup One", phone="01711000001")
    survivor = _partner(env, "Dup Two", phone="01711000001")
    env["fix.party.role"].create({"partner_id": victim.id, "role_type": "customer"})
    env["fix.party.role"].create({"partner_id": survivor.id, "role_type": "customer"})
    _granted_consent(env, victim)
    cand = env["fix.party.duplicate"].create(
        {
            "party_a": victim.id,
            "party_b": survivor.id,
            "score": 92.0,
            "factors": json.dumps({"phone": "exact"}),
        }
    )
    return victim, survivor, cand


def test_duplicate_candidate_rejects_self_pairs(odoo_env):
    partner = _partner(odoo_env)
    with pytest.raises(ValidationError, match="duplicate of itself"):
        odoo_env["fix.party.duplicate"].create(
            {"party_a": partner.id, "party_b": partner.id, "score": 100.0}
        )


def test_confirming_a_duplicate_opens_a_merge_draft(odoo_env):
    victim, survivor, cand = _merge_fixture(odoo_env)
    cand.action_review()
    cand.action_confirm()
    assert cand.state == "confirmed"
    merge = odoo_env["fix.party.merge"].search(
        [("survivor_id", "in", (victim | survivor).ids), ("state", "=", "draft")]
    )
    assert len(merge) == 1


def test_merge_is_sod_guarded_transfers_activity_and_is_reversible(odoo_env):
    victim, survivor, cand = _merge_fixture(odoo_env)
    cand.action_review()
    cand.action_confirm()
    merge = odoo_env["fix.party.merge"].search([("state", "=", "draft")], limit=1)

    # SOD-15: the superuser created both records — executing is refused.
    with pytest.raises(ValidationError, match="SOD-15"):
        merge.action_execute()

    # A03 audit W4: the steward executes it from the M63 approval inbox.
    steward = _steward(odoo_env)
    approve_via_inbox(merge, steward)
    assert merge.state == "executed"
    victim.invalidate_recordset()
    assert victim.party_status == "merged" and not victim.active
    survivor.invalidate_recordset()
    # The duplicate 'customer' role was SKIPPED (survivor holds it); the
    # consent moved; the audit records both.
    assert sorted(survivor.role_ids.mapped("role_type")) == ["customer"]
    assert survivor.consent_ids
    audit = json.loads(merge.attribute_decisions)
    assert audit["moved"]["fix.consent"]
    assert audit["skipped"]["fix.party.role"]
    assert _events(odoo_env, "party.merged", "res.partner", survivor.id)

    # Reversal restores the victim inside the window — to its PRIOR status
    # (the victim was 'draft' before the merge), not a hard-coded one.
    merge.action_reverse()
    victim.invalidate_recordset()
    assert victim.active and victim.party_status == "draft"
    assert _events(odoo_env, "party.merge_reversed", "res.partner", survivor.id)


def test_merge_reversal_is_refused_after_the_window(odoo_env):
    victim, survivor, cand = _merge_fixture(odoo_env)
    cand.action_review()
    cand.action_confirm()
    merge = odoo_env["fix.party.merge"].search([("state", "=", "draft")], limit=1)
    approve_via_inbox(merge, _steward(odoo_env))  # A03 audit W4: routed
    merge.reversible_until = "2020-01-01 00:00:00"  # window closed (test surgery)
    with pytest.raises(ValidationError, match="reversal window closed"):
        merge.action_reverse()


# --- fix.party.quality ----------------------------------------------------------


def test_quality_score_is_deterministic_and_deficiency_driven(odoo_env):
    partner = _partner(
        odoo_env, "Full Record", phone="01711234567", email="full@test.invalid", name_bn="পূর্ণ নথি"
    )
    odoo_env["fix.party.role"].create({"partner_id": partner.id, "role_type": "customer"})
    quality = odoo_env["fix.party.quality"].create({"partner_id": partner.id})
    quality.action_recompute()
    assert quality.completeness == 100.0
    assert quality.deficiencies == "[]"

    sparse = _partner(odoo_env, "Sparse Record")
    sparse_quality = odoo_env["fix.party.quality"].create({"partner_id": sparse.id})
    sparse_quality.action_recompute()
    assert sparse_quality.completeness < 100.0
    assert "phone" in json.loads(sparse_quality.deficiencies)


def test_quality_record_is_unique_per_party(odoo_env):
    partner = _partner(odoo_env)
    odoo_env["fix.party.quality"].create({"partner_id": partner.id})
    with pytest.raises(IntegrityError):
        odoo_env["fix.party.quality"].create({"partner_id": partner.id})


# --- fix.rights.request ---------------------------------------------------------


def test_dsr_statutory_clock_is_30_days(odoo_env):
    partner = _partner(odoo_env)
    req = odoo_env["fix.rights.request"].create(
        {"partner_id": partner.id, "request_type": "access"}
    )
    delta = (req.statutory_due - req.received_at.date()).days
    assert delta == 30
    assert _events(odoo_env, "rights_request.received", "fix.rights.request", req.id)


def test_dsr_fulfilment_requires_evidence_and_rejection_a_basis(odoo_env):
    partner = _partner(odoo_env)
    req = odoo_env["fix.rights.request"].create(
        {"partner_id": partner.id, "request_type": "erasure"}
    )
    req.action_verify()
    req.action_start()
    with pytest.raises(ValidationError, match="evidence reference"):
        req.action_fulfil()
    req.action_fulfil(evidence="EXPORT-2026-001")
    assert req.state == "fulfilled" and req.evidence_ref == "EXPORT-2026-001"
    assert _events(odoo_env, "rights_request.fulfilled", "fix.rights.request", req.id)

    other = odoo_env["fix.rights.request"].create(
        {"partner_id": partner.id, "request_type": "portability"}
    )
    with pytest.raises(ValidationError, match="stated basis"):
        other.action_reject()


# --- fix.segment (+ membership) --------------------------------------------------


def test_segment_membership_is_governed_and_idempotent(odoo_env):
    partner = _partner(odoo_env)
    segment = odoo_env["fix.segment"].create(
        {"code": "VIP-DHK", "name": "VIP Dhaka", "name_bn": "ভিআইপি ঢাকা"}
    )
    segment.action_add_members(partner_ids=[partner.id])
    assert segment.member_count == 1
    segment.action_add_members(partner_ids=[partner.id])  # idempotent
    assert segment.member_count == 1
    assert len(segment.membership_ids) == 1

    segment.action_remove_member(partner_id=partner.id)
    segment.invalidate_recordset()
    assert segment.member_count == 0
    assert segment.membership_ids.exited_at  # dated exit, never deleted


# --- fix.credit.profile (surfaced from cd_billing_engine, spec §3.3) -------------


def test_credit_profile_is_surfaced_from_the_billing_engine(odoo_env):
    """The model of record is M20's (cd_billing_engine): M33 surfaces it —
    the hold workflow is the model's own toggle, stamped with who and when."""
    partner = _partner(odoo_env)
    profile = odoo_env["fix.credit.profile"].create(
        {"customer_id": partner.id, "credit_limit": 50000.0}
    )
    assert profile.payment_terms_days == 30
    profile.action_toggle_hold(reason="Overdue balance")
    profile.invalidate_recordset()
    assert profile.credit_hold and profile.hold_reason == "Overdue balance"
    assert profile.hold_by.id == odoo_env.user.id
    profile.action_toggle_hold()
    profile.invalidate_recordset()
    assert not profile.credit_hold
