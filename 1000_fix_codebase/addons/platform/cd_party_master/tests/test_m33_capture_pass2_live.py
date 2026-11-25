# M33 capture audit pass 2 (2026-11-19): the server side of the records the
# spec names that nothing could capture before. Run as the people who use them
# (a Contact-manager clerk, a data steward, a DOFA Tier 2 manager, the Data
# Protection Officer, a 1000FiX registration administrator), never as the
# superuser. Rolled back per test.
import pytest
from odoo.exceptions import UserError, ValidationError

T2 = "cd_entity_config.group_dofa_tier_2"
DPO = "cd_party_master.group_party_dpo"
STEWARD = "cd_party_master.group_party_data_steward"
REG_ADMIN = "cd_party_master.group_party_registration_admin"
PARAM = "cd_party_master.require_verified_contact"


@pytest.fixture
def make_user(odoo_env):
    def _make(login, *groups):
        xmlids = ("base.group_user", "base.group_partner_manager", *groups)
        return (
            odoo_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M33 pass2 %s" % login,
                    "login": "m33p2-%s" % login,
                    "email": "%s@m33p2.invalid" % login,
                    "group_ids": [(6, 0, [odoo_env.ref(x).id for x in xmlids])],
                }
            )
        )

    return _make


def _refused(env, exc, match, fn):
    with pytest.raises(exc, match=match), env.cr.savepoint():
        fn()


def _partner(env, name, **vals):
    return env["res.partner"].create({"name": name, **vals})


# --- pages 1 / 5: contact points (FR-CPM-022, BRU-CPM-01) -------------------


def test_a_contact_point_is_normalised_and_validated(odoo_env, make_user):
    clerk = make_user("cp1")
    party = _partner(odoo_env, "P2 Contact One")
    Point = odoo_env["fix.contact.point"].with_user(clerk)
    mob = Point.create(
        {"partner_id": party.id, "contact_type": "mobile", "value": "+880 1711-234567"}
    )
    assert mob.value == "01711234567" and mob.state == "unverified"
    _refused(
        odoo_env,
        ValidationError,
        "Bangladesh mobile",
        lambda: Point.create({"partner_id": party.id, "contact_type": "mobile", "value": "12345"}),
    )
    _refused(
        odoo_env,
        ValidationError,
        "not an email",
        lambda: Point.create({"partner_id": party.id, "contact_type": "email", "value": "x@y"}),
    )
    _refused(
        odoo_env,
        ValidationError,
        "already holds",
        lambda: Point.create(
            {"partner_id": party.id, "contact_type": "mobile", "value": "01711234567"}
        ),
    )
    Point.create(
        {"partner_id": party.id, "contact_type": "email", "value": "A@B.com", "is_primary": True}
    )
    _refused(
        odoo_env,
        ValidationError,
        "already has a primary",
        lambda: Point.create(
            {
                "partner_id": party.id,
                "contact_type": "email",
                "value": "c@d.com",
                "is_primary": True,
            }
        ),
    )


def test_only_a_verified_code_verifies_a_contact_and_a_change_unverifies_it(odoo_env, make_user):
    clerk = make_user("cp2")
    party = _partner(odoo_env, "P2 Contact Two")
    point = (
        odoo_env["fix.contact.point"]
        .with_user(clerk)
        .create({"partner_id": party.id, "contact_type": "mobile", "value": "01811000222"})
    )
    _refused(odoo_env, UserError, "workflow", lambda: point.write({"state": "verified"}))
    point.action_request_verification()
    log = point.otp_log_id
    assert point.state == "pending" and log.contact_point_id == point
    assert log.destination_masked == "01***0222" and "01811000222" not in (
        log.destination_masked or ""
    )
    log.with_user(clerk).action_mark_verified(channel_ref="SMS-1")
    assert point.state == "verified" and point.verification_method == "otp" and point.verified_at
    assert party._fix_has_verified_contact()
    point.with_user(clerk).write({"value": "01811000333"})
    assert point.state == "unverified" and not point.verified_at and not point.otp_log_id
    landline = (
        odoo_env["fix.contact.point"]
        .with_user(clerk)
        .create({"partner_id": party.id, "contact_type": "landline", "value": "029001122"})
    )
    _refused(odoo_env, UserError, "one-time code", landline.action_request_verification)


def test_activation_needs_a_verified_contact_once_the_owner_switches_it_on(odoo_env, make_user):
    manager = make_user("cp3", T2)
    icp = odoo_env["ir.config_parameter"].sudo()
    first = _partner(odoo_env, "P2 Activation Off")
    icp.set_param(PARAM, "0")
    first.with_user(manager).action_reactivate_party("Walk-in verified at counter")
    assert first.party_status == "active"

    icp.set_param(PARAM, "1")
    second = _partner(odoo_env, "P2 Activation On")
    _refused(
        odoo_env,
        UserError,
        "BRU-CPM-01",
        lambda: second.with_user(manager).action_reactivate_party("please"),
    )
    assert second.party_status == "draft"
    point = odoo_env["fix.contact.point"].create(
        {"partner_id": second.id, "contact_type": "mobile", "value": "01911000444"}
    )
    point.action_request_verification()
    point.otp_log_id.action_mark_verified()
    second.with_user(manager).action_reactivate_party("Contact verified by OTP")
    assert second.party_status == "active"


# --- pages 1 / 3: relationships (FR-CPM-006) --------------------------------


def _rel(env, user, a, b, kind="guardian", evidence="Guardianship cert G-1"):
    return (
        env["fix.party.relationship"]
        .with_user(user)
        .create(
            {"party_a_id": a.id, "party_b_id": b.id, "relation_type": kind, "evidence": evidence}
        )
    )


def test_a_relationship_is_verified_by_another_steward_on_evidence(odoo_env, make_user):
    clerk, steward, steward2 = make_user("r1"), make_user("r1s", STEWARD), make_user("r1t", STEWARD)
    mum, kid = _partner(odoo_env, "P2 Mother"), _partner(odoo_env, "P2 Child")
    _refused(odoo_env, ValidationError, "itself", lambda: _rel(odoo_env, clerk, mum, mum))
    rel = _rel(odoo_env, steward, mum, kid, evidence="")
    _refused(
        odoo_env, UserError, "Party Data Steward", lambda: rel.with_user(clerk).action_verify()
    )
    _refused(odoo_env, UserError, "evidence", lambda: rel.with_user(steward2).action_verify())
    rel.with_user(steward).write({"evidence": "Birth certificate BRN-1"})
    _refused(
        odoo_env, UserError, "another data steward", lambda: rel.with_user(steward).action_verify()
    )
    _refused(
        odoo_env, UserError, "workflow", lambda: rel.with_user(clerk).write({"verified": True})
    )
    rel.with_user(steward2).action_verify()
    assert rel.verified and rel.verified_by == steward2
    _refused(
        odoo_env,
        UserError,
        "re-pointed",
        lambda: rel.with_user(steward).write({"party_b_id": mum.id}),
    )
    _refused(odoo_env, ValidationError, "already recorded", lambda: _rel(odoo_env, clerk, mum, kid))
    _refused(odoo_env, ValidationError, "reason", lambda: rel.with_user(clerk).action_end(""))
    rel.with_user(clerk).action_end("Child turned 18")
    assert rel.date_to and rel.exists()


# --- page 9: assisted consent (FR-CPM-052, BRU-CPM-16) ----------------------


def _notice(env):
    return env["fix.transparency.notice"].create(
        {"version": "P2-N1", "text_en": "EN", "text_bn": "বিজ্ঞপ্তি", "purpose_set": "marketing"}
    )


def _consent_vals(party, notice, helper=None):
    vals = {
        "partner_id": party.id,
        "purpose": "marketing",
        "channel": "sms",
        "proof": "FORM-P2",
        "notice_version_id": notice.id,
    }
    if helper:
        vals["assisted_by_id"] = helper.id
    return vals


def test_a_minor_consents_only_through_a_verified_guardian(odoo_env, make_user):
    clerk, dpo = make_user("c1"), make_user("c1d", DPO)
    steward, steward2 = make_user("c1s", STEWARD), make_user("c1t", STEWARD)
    kid, mum = _partner(odoo_env, "P2 Minor"), _partner(odoo_env, "P2 Guardian")
    notice = _notice(odoo_env)
    Consent = odoo_env["fix.consent"].with_user(clerk)

    _refused(
        odoo_env,
        UserError,
        "workflow",
        lambda: kid.with_user(clerk).write({"consent_handling": "minor"}),
    )
    _refused(
        odoo_env,
        ValidationError,
        "Say why",
        lambda: kid.with_user(clerk).action_set_consent_handling("minor", ""),
    )
    kid.with_user(clerk).action_set_consent_handling("minor", "Age 14 per birth certificate")
    assert kid.consent_handling == "minor"

    _refused(
        odoo_env, ValidationError, "BRU-CPM-16", lambda: Consent.create(_consent_vals(kid, notice))
    )
    rel = _rel(odoo_env, steward, mum, kid)
    _refused(
        odoo_env,
        ValidationError,
        "not a verified guardian",
        lambda: Consent.create(_consent_vals(kid, notice, mum)),
    )
    rel.with_user(steward2).action_verify()
    grant = Consent.create(_consent_vals(kid, notice, mum))
    assert grant.state == "granted" and grant.assisted_by_id == mum
    _refused(
        odoo_env,
        UserError,
        "cannot be edited",
        lambda: grant.write({"assisted_by_id": steward.partner_id.id}),
    )
    grant.with_user(clerk).action_withdraw()
    assert grant.superseded_by_id.assisted_by_id == mum

    _refused(
        odoo_env,
        UserError,
        "Data Protection Officer",
        lambda: kid.with_user(clerk).action_set_consent_handling("standard", "Turned 18"),
    )
    kid.with_user(dpo).action_set_consent_handling("standard", "Turned 18, ID seen")
    assert kid.consent_handling == "standard"
    # a standard party needs no helper
    Consent.create(_consent_vals(_partner(odoo_env, "P2 Adult"), notice))


# --- page 3: corporate contact roles (FR-CPM-009/011) -----------------------


def test_corporate_contact_roles_stay_inside_the_1000fix_limit(odoo_env, make_user):
    clerk, admin = make_user("cr1"), make_user("cr1a", REG_ADMIN)
    corp = _partner(odoo_env, "P2 Corp Ltd", is_company=True)
    person, person2 = _partner(odoo_env, "P2 Buyer"), _partner(odoo_env, "P2 Accountant")
    Role = odoo_env["fix.party.contact.role"].with_user(clerk)
    _refused(
        odoo_env,
        ValidationError,
        "not a corporate",
        lambda: Role.create(
            {"corporate_id": person.id, "contact_id": person2.id, "role": "billing"}
        ),
    )
    _refused(
        odoo_env,
        ValidationError,
        "approval limit",
        lambda: Role.create(
            {
                "corporate_id": corp.id,
                "contact_id": person.id,
                "role": "billing",
                "approval_limit": 10,
            }
        ),
    )
    _refused(
        odoo_env,
        UserError,
        "registration administrator",
        lambda: corp.with_user(clerk).write({"delegated_contact_limit": 1}),
    )
    corp.with_user(admin).write({"delegated_contact_limit": 1})
    buyer = Role.create(
        {"corporate_id": corp.id, "contact_id": person.id, "role": "authorised_requester"}
    )
    # a second role for the same person stays inside a one-person limit
    Role.create(
        {
            "corporate_id": corp.id,
            "contact_id": person.id,
            "role": "approver",
            "approval_limit": 50000,
        }
    )
    _refused(
        odoo_env,
        UserError,
        "at most 1",
        lambda: Role.create({"corporate_id": corp.id, "contact_id": person2.id, "role": "billing"}),
    )
    _refused(
        odoo_env,
        ValidationError,
        "already holds",
        lambda: Role.create(
            {"corporate_id": corp.id, "contact_id": person.id, "role": "authorised_requester"}
        ),
    )
    _refused(odoo_env, UserError, "re-pointed", lambda: buyer.write({"contact_id": person2.id}))
    _refused(odoo_env, UserError, "workflow", lambda: buyer.write({"state": "removed"}))
    _refused(odoo_env, ValidationError, "reason", lambda: buyer.action_suspend(""))
    buyer.action_suspend("On leave")
    assert buyer.state == "suspended" and buyer.status_note == "On leave"
    buyer.action_reinstate("Back from leave")
    buyer.action_remove("Left the company")
    assert buyer.state == "removed" and buyer.date_to
    _refused(odoo_env, UserError, "removed", lambda: buyer.action_reinstate("again"))


# --- page 9: rectification is notified (BRU-CPM-10) --------------------------


def test_a_rectification_closes_only_once_the_party_is_told(odoo_env, make_user):
    dpo = make_user("dsr1", DPO)
    party = _partner(odoo_env, "P2 Data Subject")
    req = (
        odoo_env["fix.rights.request"]
        .with_user(dpo)
        .create({"partner_id": party.id, "request_type": "rectification"})
    )
    req.action_verify()
    req.action_start()
    _refused(odoo_env, ValidationError, "BRU-CPM-10", lambda: req.action_fulfil(evidence="RECT-1"))
    req.write({"notified_at": "2026-11-19 10:00:00"})
    req.action_fulfil(evidence="RECT-1")
    assert req.state == "fulfilled"
