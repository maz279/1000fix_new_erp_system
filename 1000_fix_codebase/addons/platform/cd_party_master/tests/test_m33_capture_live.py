# M33 capture audit 2026-11-14: the server side of the new captures, run as
# the people who use them (a Contact-manager clerk, a DOFA Tier 2 manager, a
# Data Protection Officer), never as the superuser. Rolled back per test.
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

T2 = "cd_entity_config.group_dofa_tier_2"
DPO = "cd_party_master.group_party_dpo"


@pytest.fixture
def make_user(odoo_env):
    def _make(login, *groups):
        xmlids = ("base.group_user", "base.group_partner_manager", *groups)
        return (
            odoo_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M33 capture %s" % login,
                    "login": "m33cap-%s" % login,
                    "email": "%s@m33cap.invalid" % login,
                    "group_ids": [(6, 0, [odoo_env.ref(x).id for x in xmlids])],
                }
            )
        )

    return _make


def _partner(env, name, **vals):
    return env["res.partner"].create({"name": name, **vals})


def _notice(env, version):
    return env["fix.transparency.notice"].create(
        {
            "version": version,
            "text_en": "Notice EN",
            "text_bn": "বিজ্ঞপ্তি",
            "purpose_set": "marketing",
        }
    )


def _consent(env, partner, notice):
    return env["fix.consent"].create(
        {
            "partner_id": partner.id,
            "purpose": "marketing",
            "channel": "sms",
            "proof": "FORM-1",
            "notice_version_id": notice.id,
        }
    )


# --- 12 Status Lifecycle: Change Party Status / Reactivate a Party ----------


def test_a_clerk_restricts_a_party_with_a_reason(odoo_env, make_user):
    clerk = make_user("clerk1")
    party = _partner(odoo_env, "M33 Status One")
    party.with_user(clerk).action_set_party_status("blocked", "Chargeback dispute #44")
    assert party.party_status == "blocked"
    assert party.status_reason == "Chargeback dispute #44"
    assert party.status_since
    assert "Chargeback dispute #44" in party.message_ids[:1].body


def test_a_status_change_needs_a_reason_and_a_restrictive_status(odoo_env, make_user):
    clerk = make_user("clerk2")
    party = _partner(odoo_env, "M33 Status Two")
    with pytest.raises(ValidationError, match="reason"):
        party.with_user(clerk).action_set_party_status("dormant", "  ")
    with pytest.raises(ValidationError, match="Reactivate"):
        party.with_user(clerk).action_set_party_status("active", "please")
    assert party.party_status == "draft"


def test_blacklisting_is_a_tier2_decision_by_form_or_by_edit(odoo_env, make_user):
    clerk = make_user("clerk3")
    party = _partner(odoo_env, "M33 Status Three")
    with pytest.raises(UserError, match="Tier 2"):
        party.with_user(clerk).action_set_party_status("blacklisted", "fraud")
    with pytest.raises(UserError, match="Tier 2"):
        party.with_user(clerk).write({"party_status": "blacklisted"})
    assert party.party_status == "draft"
    manager = make_user("t2-1", T2)
    party.with_user(manager).action_set_party_status("blacklisted", "Confirmed fraud ring")
    assert party.party_status == "blacklisted"
    with pytest.raises(ValidationError):
        party.with_user(manager).action_set_party_status("dormant", "undo")


def test_restricting_by_edit_stays_open_to_a_clerk(odoo_env, make_user):
    """The A03 decision (test_a03_approval_bypass) is kept for non-terminal states."""
    clerk = make_user("clerk4")
    party = _partner(odoo_env, "M33 Status Four")
    party.with_user(clerk).write({"party_status": "dormant"})
    assert party.party_status == "dormant"


def test_reactivation_from_the_form_stays_tier2(odoo_env, make_user):
    party = _partner(odoo_env, "M33 Status Five")
    party.with_user(make_user("clerk5")).action_set_party_status("blocked", "dispute")
    with pytest.raises(UserError, match="Tier 2"):
        party.with_user(make_user("clerk6")).action_reactivate_party("settled")
    party.with_user(make_user("t2-2", T2)).action_reactivate_party("Dispute settled")
    assert party.party_status == "active"


# --- 8 Golden Record & Quality: Score a Party -------------------------------


def test_a_steward_scores_the_party_in_front_of_them(odoo_env, make_user):
    clerk = make_user("clerk7")
    party = _partner(odoo_env, "M33 Score", phone="01711222333", email="score@x.invalid")
    Quality = odoo_env["fix.party.quality"]
    assert not Quality.search([("partner_id", "=", party.id)])
    party.with_user(clerk).action_score_quality()
    row = Quality.search([("partner_id", "=", party.id)])
    assert len(row) == 1 and row.composite > 0 and row.evaluated_at
    first = row.completeness
    party.write({"name_bn": "স্কোর"})
    party.with_user(clerk).action_score_quality()  # an upsert, not a second row
    assert len(Quality.search([("partner_id", "=", party.id)])) == 1
    assert row.completeness > first


# --- 7 Deduplication: a raised pair is scored by the rules -----------------


def test_a_raised_pair_is_scored_by_the_rules_not_by_the_user(odoo_env, make_user):
    clerk = make_user("clerk8")
    a = _partner(odoo_env, "Rahim Uddin", phone="01719998881")
    b = _partner(odoo_env, "R. Uddin", phone="01719998881")
    c = _partner(odoo_env, "Karim Traders", phone="01810000001")
    Dup = odoo_env["fix.party.duplicate"].with_user(clerk)
    same = Dup.create(
        {"party_a": a.id, "party_b": b.id, "score": 5.0, "factors": '{"typed": true}'}
    )
    assert same.score == 100.0  # the exact phone rule measured it
    assert '"source": "raised_by_user"' in same.factors and "typed" not in same.factors
    unlike = Dup.create({"party_a": a.id, "party_b": c.id, "score": 99.0})
    assert unlike.score == 0.0 and '"matched": false' in unlike.factors


def test_a_candidate_pair_and_score_cannot_be_retyped(odoo_env, make_user):
    clerk = make_user("clerk9")
    a = _partner(odoo_env, "Dup Edit A", phone="01712121212")
    b = _partner(odoo_env, "Dup Edit B", phone="01712121212")
    c = _partner(odoo_env, "Dup Edit C")
    cand = (
        odoo_env["fix.party.duplicate"].with_user(clerk).create({"party_a": a.id, "party_b": b.id})
    )
    with pytest.raises(ValidationError, match="measured"):
        cand.write({"score": 1.0})
    with pytest.raises(ValidationError, match="measured"):
        cand.write({"party_b": c.id})
    cand.write({"decision": "Same mobile, two spellings"})  # a note is still the steward's
    with pytest.raises(ValidationError, match="already in the stewardship queue"):
        odoo_env["fix.party.duplicate"].with_user(clerk).create({"party_a": b.id, "party_b": a.id})


# --- 9 Consent & DSR: record of processing ---------------------------------


def test_consent_capture_and_withdrawal_record_processing(odoo_env, make_user):
    clerk = make_user("clerk10")
    party = _partner(odoo_env, "M33 Processing One")
    notice = _notice(odoo_env, "m33cap-1")
    consent = _consent(odoo_env(user=clerk), party, notice)
    Proc = odoo_env["fix.processing.record"]
    rows = Proc.search([("party_id", "=", party.id)])
    assert rows.mapped("source") == ["consent_capture"]
    assert rows.lawful_basis == "consent" and rows.consent_id == consent
    consent.with_user(clerk).action_withdraw()
    rows = Proc.search([("party_id", "=", party.id)])
    assert sorted(rows.mapped("source")) == ["consent_capture", "consent_withdrawal"]


def test_only_the_dpo_records_processing_and_nobody_edits_or_deletes_it(odoo_env, make_user):
    party = _partner(odoo_env, "M33 Processing Two")
    vals = {
        "party_id": party.id,
        "purpose": "service_delivery",
        "lawful_basis": "contract",
        "categories": "name, mobile, service address",
        "recipients": "Courier partner",
        "source": "consent_capture",  # a person cannot claim a system source
    }
    Proc = odoo_env["fix.processing.record"]
    with pytest.raises((AccessError, UserError)):
        Proc.with_user(make_user("clerk11")).create(vals)
    dpo = make_user("dpo1", DPO)
    rec = Proc.with_user(dpo).create(vals)
    assert rec.source == "manual" and rec.party_ref_id == party.id
    with pytest.raises((AccessError, UserError)):
        rec.with_user(dpo).write({"recipients": "nobody"})
    with pytest.raises((AccessError, UserError)):
        rec.with_user(dpo).unlink()
    with pytest.raises(UserError, match="five|5"):
        rec.sudo().unlink()  # inside the statutory period even the system keeps it


def test_processing_on_consent_must_name_the_consent(odoo_env, make_user):
    dpo = make_user("dpo2", DPO)
    party = _partner(odoo_env, "M33 Processing Three")
    other = _partner(odoo_env, "M33 Processing Other")
    base = {
        "party_id": party.id,
        "purpose": "marketing",
        "lawful_basis": "consent",
        "categories": "mobile",
    }
    Proc = odoo_env["fix.processing.record"].with_user(dpo)
    with pytest.raises(ValidationError, match="consent"):
        Proc.create(base)
    foreign = _consent(odoo_env, other, _notice(odoo_env, "m33cap-2"))
    with pytest.raises(ValidationError, match="another party"):
        Proc.create({**base, "consent_id": foreign.id})


# --- 9 Consent & DSR: transparency notice wording -----------------------------


def test_a_notice_with_consents_keeps_its_wording(odoo_env, make_user):
    clerk = make_user("clerk12")
    used = _notice(odoo_env, "m33cap-3")
    _consent(odoo_env, _partner(odoo_env, "M33 Notice Party"), used)
    with pytest.raises(UserError, match="new version"):
        used.with_user(clerk).write({"text_en": "Rewritten after the fact"})
    with pytest.raises(UserError, match="evidence"):
        used.unlink()
    fresh = _notice(odoo_env, "m33cap-4")
    fresh.with_user(clerk).write({"text_en": "Corrected before anyone accepted it"})
    assert fresh.text_en.startswith("Corrected")


# --- 4 Addresses: one default per purpose ------------------------------------


def test_one_default_address_per_tag(odoo_env, make_user):
    clerk = make_user("clerk13")
    party = _partner(odoo_env, "M33 Address Party")
    Addr = odoo_env["fix.bd.address"].with_user(clerk)
    base = {"party_id": party.id, "division": "Dhaka", "district": "Dhaka", "postcode": "1207"}
    Addr.create({**base, "address_tag": "home", "is_default": True, "latitude": 23.75})
    Addr.create({**base, "address_tag": "office", "is_default": True})
    with pytest.raises(ValidationError, match="already has a default"):
        Addr.create({**base, "address_tag": "home", "is_default": True})
    Addr.create({**base, "address_tag": "home"})  # a second home address, not the default
