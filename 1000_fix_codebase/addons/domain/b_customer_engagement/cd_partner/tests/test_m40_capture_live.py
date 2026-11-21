"""M40 capture audit (19 Nov 2026): the registers each sub-module page
captures, exercised against the live ORM as non-admin users.

Each test names the rule it proves; each was written to fail on the defect
it guards (mutation check in the audit report)."""

import base64
import types
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_partner.tests.m40_fixtures import (
    configure_payout_accounts,
    guarded_write,
    make_onboardable,
    paid_invoice,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)


def _mk(env, login, *xmlids):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                ],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    pa = "cd_partner.group_fix_channel_"
    x = types.SimpleNamespace(env=env)
    x.clerk = _mk(env, "m40c_clerk")
    x.officer = _mk(env, "m40c_officer", pa + "officer")
    x.officer2 = _mk(env, "m40c_officer2", pa + "officer")
    x.kyc = _mk(env, "m40c_kyc", pa + "kyc_officer")
    x.manager = _mk(env, "m40c_manager", pa + "manager")
    x.manager2 = _mk(env, "m40c_manager2", pa + "manager")
    x.cco = _mk(env, "m40c_cco", "cd_entity_config.group_dofa_tier_3", pa + "officer")
    x.cco2 = _mk(env, "m40c_cco2", "cd_entity_config.group_dofa_tier_3", pa + "officer")
    x.finance = _mk(env, "m40c_finance", "account.group_account_invoice")
    x.today = fields.Date.context_today(env.user)
    x.n = 0
    return x


def _party(w, name):
    return w.env["res.partner"].create({"name": name})


def _doc(w, record, name="evidence.pdf", user=None):
    return (
        w.env["ir.attachment"]
        .with_user(user or w.officer)
        .create(
            {
                "name": name,
                "res_model": record._name,
                "res_id": record.id,
                "datas": base64.b64encode(b"%PDF-1.4 m40 evidence"),
            }
        )
    )


def _partner(w, ptype="reseller", onboard=True, **kw):
    w.n += 1
    vals = {
        "name": "M40C %s %d" % (ptype, w.n),
        "partner_id": _party(w, "M40C party %d" % w.n).id,
        "partner_type": ptype,
        "tin_number": "123456789012",
        "trade_license_no": "TL-%d" % w.n,
    }
    vals.update(kw)
    p = w.env["fix.partner"].with_user(w.officer).create(vals)
    if ptype == "franchise":
        p.with_user(w.officer).write(
            {
                "trade_license_attachment_id": _doc(w, p, "tl.pdf").id,
                "bank_solvency_attachment_id": _doc(w, p, "bs.pdf").id,
            }
        )
        p.with_user(w.kyc).action_verify_kyc()
    if onboard:
        # A04 ERP audit M40-F11: programme, agreement, checklist (set-up only)
        make_onboardable(w.env, p)
        p.with_user(w.manager).action_onboard()
    return p


# =========================================================== p1 programme
def _programme(w, code="REF-STD", ptype="referral", tiers=1, user=None):
    prog = (
        w.env["fix.partner.programme"]
        .with_user(user or w.officer)
        .create(
            {
                "name": "Referral Standard",
                "code": code,
                "partner_type": ptype,
                "entry_criteria": "Registered business, 6 months trading",
                "tier_ids": [
                    (0, 0, {"code": "T%d" % i, "name": "Tier %d" % i, "criteria": "c%d" % i})
                    for i in range(1, tiers + 1)
                ],
            }
        )
    )
    return prog


def test_programme_publishes_with_a_tier_by_someone_else(w):
    bare = _programme(w, code="BARE", tiers=0)
    with pytest.raises(ValidationError, match="tier"), w.env.cr.savepoint():
        bare.with_user(w.manager).action_publish()
    prog = _programme(w)
    # a manager who drafted a programme does not publish it
    own = _programme(w, code="OWN", user=w.manager)
    with pytest.raises(UserError, match="Segregation"), w.env.cr.savepoint():
        own.with_user(w.manager).action_publish()
    prog.with_user(w.manager).action_publish()
    assert prog.state == "published" and prog.published_by_id == w.manager


def test_published_terms_and_tiers_never_change(w):
    prog = _programme(w)
    prog.with_user(w.manager).action_publish()
    with pytest.raises(UserError), w.env.cr.savepoint():
        prog.with_user(w.officer).write({"entry_criteria": "anyone"})
    with pytest.raises(UserError, match="new version"), w.env.cr.savepoint():
        prog.tier_ids[0].with_user(w.officer).write({"criteria": "softer"})
    with pytest.raises(UserError), w.env.cr.savepoint():
        prog.with_user(w.officer).write({"state": "draft"})


def test_a_new_version_supersedes_and_binds_partners_to_theirs(w):
    v1 = _programme(w)
    v1.with_user(w.manager).action_publish()
    p = _partner(w, "referral", onboard=False, programme_id=v1.id)
    p.with_user(w.officer).action_submit_onboarding()
    res = v1.with_user(w.officer).action_new_version()
    v2 = w.env["fix.partner.programme"].browse(res["res_id"])
    assert v2.version == 2 and v2.state == "draft" and v2.tier_ids
    v2.with_user(w.manager).action_publish()
    assert v1.state == "superseded"
    # BRU-PCM-12: the partner stays on the version it joined on
    with pytest.raises(UserError, match="BRU-PCM-12"), w.env.cr.savepoint():
        p.with_user(w.officer).write({"programme_id": v2.id})


def test_tier_moves_only_through_the_manager_action(w):
    prog = _programme(w, tiers=2)
    prog.with_user(w.manager).action_publish()
    p = _partner(w, "referral", programme_id=prog.id)
    with pytest.raises(UserError), w.env.cr.savepoint():
        p.with_user(w.officer).write({"tier_id": prog.tier_ids[1].id})
    with pytest.raises(UserError, match="no tier"), w.env.cr.savepoint():
        p.with_user(w.manager).action_change_tier("T9")
    # A04 ERP audit M40-F30: the move takes effect after the tier's notice
    p.with_user(w.manager).action_change_tier("T2")
    assert p.pending_tier_id.code == "T2" and p.tier_id.code != "T2"
    assert p.tier_effective_on == w.today + timedelta(days=30)


def test_programme_type_must_match_the_partner(w):
    prog = _programme(w, ptype="reseller")
    prog.with_user(w.manager).action_publish()
    with pytest.raises(ValidationError, match="reseller partners"), w.env.cr.savepoint():
        _partner(w, "referral", onboard=False, programme_id=prog.id)


def test_one_primary_contact_per_role(w):
    p = _partner(w, onboard=False)
    roles = w.env["fix.partner.contact.role"].with_user(w.officer)
    roles.create(
        {"partner_id": p.id, "contact_id": _party(w, "Rina").id, "role": "finance", "primary": True}
    )
    with pytest.raises(ValidationError, match="primary"), w.env.cr.savepoint():
        roles.create(
            {
                "partner_id": p.id,
                "contact_id": _party(w, "Sumon").id,
                "role": "finance",
                "primary": True,
            }
        )


# ========================================================== p2 onboarding
def test_onboarding_waits_for_required_steps(w):
    p = _partner(w, onboard=False)
    p.with_user(w.officer).action_generate_onboarding()
    p.with_user(w.officer).action_generate_onboarding()  # idempotent
    assert len(p.onboarding_ids) == 6
    # programme and agreement in place (M40-F11): only the pending steps refuse
    make_onboardable(w.env, p, checklist=False)
    with pytest.raises(ValidationError, match="steps are pending"), w.env.cr.savepoint():
        p.with_user(w.manager).action_onboard()


def test_a_step_is_completed_on_its_evidence_and_never_waived_if_required(w):
    p = _partner(w, onboard=False)
    step = (
        w.env["fix.partner.onboarding"]
        .with_user(w.officer)
        .create({"partner_id": p.id, "step": "banking", "name": "Bank details"})
    )
    with pytest.raises(UserError, match="never waived"), w.env.cr.savepoint():
        step.with_user(w.manager).action_waive("not needed")
    with pytest.raises(ValidationError, match="evidence"), w.env.cr.savepoint():
        step.with_user(w.officer).action_complete()
    step.with_user(w.officer).write({"evidence_attachment_id": _doc(w, step).id})
    step.with_user(w.officer).action_complete()
    assert step.state == "done"
    # done: the evidence is frozen
    with pytest.raises(UserError), w.env.cr.savepoint():
        step.with_user(w.officer).write({"evidence_attachment_id": False})
    make_onboardable(w.env, p, checklist=False)  # M40-F11: programme + agreement
    p.with_user(w.manager).action_onboard()
    assert p.state == "onboarded"


def test_evidence_must_be_the_steps_own_document(w):
    p = _partner(w, onboard=False)
    step = (
        w.env["fix.partner.onboarding"]
        .with_user(w.officer)
        .create({"partner_id": p.id, "step": "documents", "name": "Docs"})
    )
    foreign = _doc(w, p, "someone-else.pdf")
    with pytest.raises(ValidationError, match="not attached"), w.env.cr.savepoint():
        step.with_user(w.officer).write({"evidence_attachment_id": foreign.id})


def test_the_agreement_step_needs_the_linked_agreement(w):
    p = _partner(w, onboard=False)
    step = (
        w.env["fix.partner.onboarding"]
        .with_user(w.officer)
        .create({"partner_id": p.id, "step": "agreement", "name": "Agreement"})
    )
    step.with_user(w.officer).write({"evidence_attachment_id": _doc(w, step).id})
    with pytest.raises(ValidationError, match="FR-PCM-008"), w.env.cr.savepoint():
        step.with_user(w.officer).action_complete()


def test_an_optional_step_is_waived_by_another_manager_with_a_reason(w):
    p = _partner(w, onboard=False)
    step = (
        w.env["fix.partner.onboarding"]
        .with_user(w.officer)
        .create({"partner_id": p.id, "step": "other", "name": "Site photo", "required": False})
    )
    with pytest.raises(UserError, match="why"), w.env.cr.savepoint():
        step.with_user(w.manager).action_waive("")
    step.with_user(w.manager).action_waive("remote partner")
    assert step.state == "waived" and step.waive_reason == "remote partner"


def _rebate(w, partner):
    # A04 ERP audit M40-F12: the basis is the partner's paid M20 invoices
    paid_invoice(w.env, partner.partner_id, 10000.0, w.today - timedelta(days=5))
    return (
        w.env["fix.partner.rebate"]
        .with_user(w.officer)
        .create(
            {
                "name": "Q4",
                "partner_id": partner.id,
                "period": "2026-Q4",
                "period_from": w.today - timedelta(days=30),
                "period_to": w.today,
                "rate": 0.02,
            }
        )
    )


def test_required_certification_gates_the_rebate(w):
    p = _partner(w)
    cert = (
        w.env["fix.partner.enablement"]
        .with_user(w.officer)
        .create({"partner_id": p.id, "course": "Samsung L2"})
    )
    with pytest.raises(ValidationError, match="FR-PCM-041"), w.env.cr.savepoint():
        _rebate(w, p).with_user(w.officer).action_accrue()
    with pytest.raises(ValidationError, match="certificate"), w.env.cr.savepoint():
        cert.with_user(w.officer).action_certify()
    cert.with_user(w.officer).write(
        {
            "completed_on": w.today,
            "certificate_attachment_id": _doc(w, cert).id,
            "expires_on": w.today + timedelta(days=365),
        }
    )
    cert.with_user(w.officer).action_certify()
    reb = _rebate(w, p)
    reb.with_user(w.officer).action_accrue()
    assert reb.state == "accrued"


def test_an_expired_certification_gates_again(w):
    p = _partner(w)
    cert = (
        w.env["fix.partner.enablement"]
        .with_user(w.officer)
        .create({"partner_id": p.id, "course": "ESD"})
    )
    cert.with_user(w.officer).write(
        {
            "completed_on": w.today - timedelta(days=400),
            "certificate_attachment_id": _doc(w, cert).id,
            "expires_on": w.today + timedelta(days=1),
        }
    )
    cert.with_user(w.officer).action_certify()
    cert.sudo().write({"expires_on": w.today - timedelta(days=1)})
    assert w.env["fix.partner.enablement"].cron_enablement_expiry() >= 1
    assert cert.state == "expired"
    with pytest.raises(ValidationError, match="FR-PCM-041"), w.env.cr.savepoint():
        _rebate(w, p).with_user(w.officer).action_accrue()


# ========================================================= p3 brand relations
def _authorisation(w, partner, brand):
    auth = (
        w.env["fix.partner.authorisation"]
        .with_user(w.officer)
        .create(
            {
                "name": "Auth",
                "partner_id": partner.id,
                "brand_id": brand.id,
                "valid_from": w.today,
                "valid_to": w.today + timedelta(days=365),
                "certificate_ref": "CERT-1",
            }
        )
    )
    auth.with_user(w.officer).write({"certificate_attachment_id": _doc(w, auth).id})
    auth.with_user(w.manager).action_activate()
    return auth


def _brand(w):
    brand = w.env["fix.brand"].search([], limit=1)
    return brand or w.env["fix.brand"].create({"name": "M40C Brand", "code": "M40CB"})


def test_obligation_is_met_on_evidence_and_recurs(w):
    auth = _authorisation(w, _partner(w, "brand"), _brand(w))
    ob = (
        w.env["fix.brand.obligation"]
        .with_user(w.officer)
        .create(
            {
                "authorisation_id": auth.id,
                "obligation_type": "reporting",
                "description": "Quarterly claim report",
                "due_date": w.today + timedelta(days=10),
                "recurrence": "quarterly",
            }
        )
    )
    with pytest.raises(ValidationError, match="evidence"), w.env.cr.savepoint():
        ob.with_user(w.officer).action_mark_met()
    ob.with_user(w.officer).write({"evidence_attachment_id": _doc(w, ob).id})
    ob.with_user(w.officer).action_mark_met()
    nxt = w.env["fix.brand.obligation"].search(
        [("authorisation_id", "=", auth.id), ("state", "=", "open")]
    )
    assert ob.state == "met" and len(nxt) == 1
    assert nxt.due_date > ob.due_date and not nxt.evidence_attachment_id
    with pytest.raises(UserError), w.env.cr.savepoint():
        ob.with_user(w.officer).write({"description": "rewritten"})


def test_overdue_obligations_are_flagged(w):
    auth = _authorisation(w, _partner(w, "brand"), _brand(w))
    ob = (
        w.env["fix.brand.obligation"]
        .with_user(w.officer)
        .create(
            {
                "authorisation_id": auth.id,
                "obligation_type": "tooling",
                "description": "ESD mats",
                "due_date": w.today - timedelta(days=1),
            }
        )
    )
    w.env["fix.brand.obligation"].cron_obligation_overdue()
    assert ob.state == "overdue"
    with pytest.raises(UserError), w.env.cr.savepoint():
        ob.with_user(w.officer).write({"state": "met"})


def test_brand_audit_lifecycle_and_closure_by_another_manager(w):
    audit = (
        w.env["fix.brand.audit"]
        .with_user(w.manager)
        .create(
            {
                "name": "Brand audit 2026",
                "brand_id": _brand(w).id,
                "scheduled_on": w.today,
                "scope": "Workshop and parts store",
            }
        )
    )
    with pytest.raises(ValidationError, match="findings"), w.env.cr.savepoint():
        audit.with_user(w.officer).action_record_findings()
    audit.with_user(w.officer).write({"conducted_on": w.today, "findings": "2 minor"})
    audit.with_user(w.officer).action_record_findings()
    with pytest.raises(UserError), w.env.cr.savepoint():
        audit.with_user(w.officer).write({"findings": "none"})
    with pytest.raises(ValidationError, match="response"), w.env.cr.savepoint():
        audit.with_user(w.officer).action_respond()
    audit.with_user(w.officer).write({"response": "Fixed both"})
    audit.with_user(w.officer).action_respond()
    with pytest.raises(UserError, match="Segregation"), w.env.cr.savepoint():
        audit.with_user(w.manager).action_close()
    audit.with_user(w.manager2).action_close()
    assert audit.state == "closed" and audit.closed_by_id == w.manager2


def test_engagement_log_is_append_only(w):
    p = _partner(w, "brand")
    entry = (
        w.env["fix.partner.engagement"]
        .with_user(w.officer)
        .create(
            {
                "partner_id": p.id,
                "engagement_type": "brand_assessment",
                "direction": "inbound",
                "summary": "1000FiX TAT below target in Q3",
            }
        )
    )
    assert entry.logged_by_id == w.officer
    with pytest.raises(UserError, match="BRU-PCM-20"), w.env.cr.savepoint():
        entry.with_user(w.manager).write({"summary": "TAT fine"})
    with pytest.raises(ValidationError, match="inbound"), w.env.cr.savepoint():
        w.env["fix.partner.engagement"].with_user(w.officer).create(
            {
                "partner_id": p.id,
                "engagement_type": "brand_assessment",
                "direction": "outbound",
                "summary": "We are great",
            }
        )


# ============================================================ p4 alliances
def _scheme(w, partner, **kw):
    vals = {
        "name": "Insurer members",
        "code": "ALL-%d" % partner.id,
        "partner_id": partner.id,
        "member_definition": "Policy holders",
        "eligibility_method": "member_id",
        "benefit_description": "10% labour",
    }
    vals.update(kw)
    return w.env["fix.alliance.scheme"].with_user(w.officer).create(vals)


def test_scheme_needs_an_m11_rule_and_an_onboarded_alliance(w):
    sch = _scheme(w, _partner(w, "alliance"))
    with pytest.raises(ValidationError, match="BRU-PCM-19"), w.env.cr.savepoint():
        sch.with_user(w.manager).action_activate()
    sch.with_user(w.officer).write({"benefit_ref": "M11-ALLIANCE-INS"})
    raw = _scheme(w, _partner(w, "alliance", onboard=False), benefit_ref="X")
    with pytest.raises(ValidationError, match="onboarded alliance"), w.env.cr.savepoint():
        raw.with_user(w.manager).action_activate()
    sch.with_user(w.manager).action_activate()
    assert sch.state == "active"
    with pytest.raises(UserError), w.env.cr.savepoint():
        sch.with_user(w.officer).write({"benefit_ref": "ad-hoc 50%"})


def test_eligibility_is_checked_only_under_a_live_scheme_and_is_a_log(w):
    sch = _scheme(w, _partner(w, "alliance"), benefit_ref="M11-R", volume_commitment=4)
    checks = w.env["fix.alliance.eligibility.check"].with_user(w.officer)
    vals = {
        "scheme_id": sch.id,
        "member_ref": "POL-1",
        "result": "eligible",
        "evidence_ref": "card",
    }
    with pytest.raises(ValidationError, match="active"), w.env.cr.savepoint():
        checks.create(vals)
    sch.with_user(w.manager).action_activate()
    chk = checks.create(vals)
    assert chk.checked_by_id == w.officer
    assert sch.eligible_count == 1 and sch.commitment_pct == 25.0
    with pytest.raises(UserError), w.env.cr.savepoint():
        chk.with_user(w.officer).write({"result": "not_eligible"})
    sch.sudo().write(
        {"valid_to": w.today - timedelta(days=1), "valid_from": w.today - timedelta(days=9)}
    )
    with pytest.raises(ValidationError, match="validity"), w.env.cr.savepoint():
        checks.create(vals)


# ============================================================ p5 referrals
def _link(w, partner):
    return w.env["fix.referral.link"].with_user(w.officer).create({"partner_id": partner.id})


def test_referral_codes_are_generated_unique_and_not_typed(w):
    p = _partner(w, "referral")
    a, b = _link(w, p), _link(w, p)
    assert a.code and b.code and a.code != b.code and len(a.code.split("-")[-1]) >= 12
    with pytest.raises(UserError), w.env.cr.savepoint():
        a.with_user(w.officer).write({"code": "EASY1"})
    with pytest.raises(ValidationError, match="onboarded"), w.env.cr.savepoint():
        _link(w, _partner(w, "referral", onboard=False))
    with pytest.raises(UserError, match="why"), w.env.cr.savepoint():
        a.with_user(w.officer).action_revoke("")
    a.with_user(w.officer).action_revoke("leaked")
    assert a.state == "revoked"


def _lead(w, partner, **kw):
    vals = {
        "partner_id": partner.id,
        "customer_name": "Karim",
        "customer_phone": "01711000000",
        "consent_given": True,
        "consent_method": "digital",
    }
    vals.update(kw)
    return w.env["fix.partner.lead"].with_user(w.officer).create(vals)


def test_no_consent_no_lead(w):
    p = _partner(w, "referral")
    before = w.env["fix.partner.lead"].search_count([])
    with pytest.raises(ValidationError, match="BRU-PCM-06"), w.env.cr.savepoint():
        _lead(w, p, consent_given=False)
    with pytest.raises(ValidationError, match="BRU-PCM-06"), w.env.cr.savepoint():
        _lead(w, p, consent_method=False)
    assert w.env["fix.partner.lead"].search_count([]) == before


def test_attribution_is_written_once(w):
    p, other = _partner(w, "referral"), _partner(w, "referral")
    lead = _lead(w, p, link_id=_link(w, p).id)
    assert lead.attribution_expires_on == w.today + timedelta(days=lead.attribution_window_days)
    with pytest.raises(UserError, match="BRU-PCM-04"), w.env.cr.savepoint():
        lead.with_user(w.manager).write({"partner_id": other.id})
    with pytest.raises(UserError), w.env.cr.savepoint():
        lead.with_user(w.manager).write({"attribution_expires_on": w.today + timedelta(days=900)})
    with pytest.raises(ValidationError, match="not"), w.env.cr.savepoint():
        _lead(w, other, link_id=_link(w, p).id)


def test_conversion_inside_the_window_raises_the_referral(w):
    p = _partner(w, "referral")
    lead = _lead(w, p)
    lead.with_user(w.officer).write({"customer_id": _party(w, "Karim Ltd").id})
    with pytest.raises(UserError, match="Qualify"), w.env.cr.savepoint():
        lead.with_user(w.officer).action_convert()
    lead.with_user(w.officer).action_qualify()
    lead.with_user(w.officer).action_convert()
    assert lead.state == "converted" and lead.referral_id
    assert lead.referral_id.partner_id == p and lead.referral_id.state == "submitted"


def test_conversion_outside_the_window_attributes_to_no_one(w):
    p = _partner(w, "referral")
    lead = _lead(w, p)
    lead.with_user(w.officer).write({"customer_id": _party(w, "Late Ltd").id})
    lead.with_user(w.officer).action_qualify()
    lead.sudo().write({"attribution_expires_on": w.today - timedelta(days=1)})
    lead.with_user(w.officer).action_convert()
    assert lead.state == "converted" and lead.attribution_lapsed and not lead.referral_id


def test_a_lost_lead_says_why(w):
    lead = _lead(w, _partner(w, "referral"))
    with pytest.raises(UserError, match="reason"), w.env.cr.savepoint():
        lead.with_user(w.officer).action_mark_lost("")
    lead.with_user(w.officer).action_mark_lost("chose a competitor")
    assert lead.loss_reason == "chose a competitor"


# ===================================================== p6 precedence rules
def _rule(w, user, territory=False):
    return (
        w.env["fix.channel.conflict.rule"]
        .with_user(user)
        .create(
            {
                "name": "National precedence",
                "scope": "All B2C service jobs",
                "territory": territory,
                "first_channel": "direct",
                "second_channel": "franchise",
            }
        )
    )


def test_precedence_rule_is_activated_by_another_tier3_and_supersedes(w):
    r1 = _rule(w, w.officer)
    with pytest.raises(UserError), w.env.cr.savepoint():
        r1.with_user(w.manager).action_activate()
    r1.with_user(w.cco).action_activate()
    mine = _rule(w, w.cco)
    with pytest.raises(UserError, match="Segregation"), w.env.cr.savepoint():
        mine.with_user(w.cco).action_activate()
    mine.with_user(w.cco2).action_activate()
    assert r1.state == "retired" and mine.state == "active"
    assert mine.precedence.startswith("Direct sales > Franchise")
    with pytest.raises(ValidationError, match="once"), w.env.cr.savepoint():
        w.env["fix.channel.conflict.rule"].with_user(w.officer).create(
            {"name": "x", "scope": "x", "first_channel": "direct", "second_channel": "direct"}
        )


# ============================================================ p7 resellers
def test_reseller_draws_never_exceed_the_allocation(w):
    product = (
        w.env["product.product"].sudo().create({"name": "M40C phone", "default_code": "M40C-P"})
    )
    alloc = (
        w.env["fix.reseller.allocation"]
        .with_user(w.officer)
        .create(
            {
                "partner_id": _partner(w, "reseller").id,
                "allocation_type": "capacity",
                "item_description": "Refurbished phones grade A",
                "product_id": product.id,
                "qty": 10,
                "period": "2026-11",
            }
        )
    )
    assert alloc.name.startswith("RAL/")
    with pytest.raises(UserError), w.env.cr.savepoint():
        alloc.with_user(w.officer).action_record_draw(1)
    # A04 ERP audit M40-F16: the price is M11's (price service mocked here)
    quote = {"price": 100.0, "source": "card", "card_id": False, "reason": ""}
    with mock.patch.object(type(w.env["fix.rate.card"]), "price_for", return_value=quote):
        alloc.with_user(w.manager).action_allocate()
    alloc.with_user(w.officer).action_record_draw("6")
    with pytest.raises(ValidationError, match="left"), w.env.cr.savepoint():
        alloc.with_user(w.officer).action_record_draw(5)
    assert alloc.remaining_qty == 4
    with pytest.raises(UserError), w.env.cr.savepoint():
        alloc.with_user(w.officer).write({"consumed_qty": 0})
    with pytest.raises(UserError), w.env.cr.savepoint():
        alloc.with_user(w.officer).write({"qty": 100})


# ============================================================ p8 franchise
def _territory(w, partner, code, districts, excl="exclusive"):
    return (
        w.env["fix.franchise.territory"]
        .with_user(w.officer)
        .create(
            {
                "code": code,
                "name": code,
                "districts": districts,
                "exclusivity": excl,
                "partner_id": partner.id,
                "valid_from": w.today,
            }
        )
    )


def test_exclusive_territories_never_share_a_district(w):
    f1, f2 = _partner(w, "franchise"), _partner(w, "franchise")
    _territory(w, f1, "GAZ", "Gazipur, Narayanganj").with_user(w.manager).action_activate()
    clash = _territory(w, f2, "NGJ", " narayanganj ,Munshiganj")
    with pytest.raises(ValidationError, match="BRU-PCM-16"), w.env.cr.savepoint():
        clash.with_user(w.manager).action_activate()
    free = _territory(w, f2, "MUN", "Munshiganj")
    free.with_user(w.manager).action_activate()
    assert free.state == "active"


def _franchise(w, **kw):
    partner = _partner(w, "franchise")
    vals = {
        "name": "Franchise",
        "partner_id": partner.id,
        "territory": "Gazipur",
        "start_date": w.today - timedelta(days=60),
        "royalty_rate": 0.06,
        "marketing_levy_rate": 0.01,
    }
    vals.update(kw)
    fr = w.env["fix.partner.franchise"].with_user(w.officer).create(vals)
    fr.with_user(w.manager).action_activate()
    return fr


def _royalty(w, fr):
    return (
        w.env["fix.franchise.royalty"]
        .with_user(w.officer)
        .create(
            {
                "franchise_id": fr.id,
                "period_from": w.today - timedelta(days=40),
                "period_to": w.today - timedelta(days=10),
            }
        )
    )


def test_royalty_is_never_self_declared(w):
    fr = _franchise(w)
    roy = _royalty(w, fr)
    with pytest.raises(ValidationError, match="BRU-PCM-17"), w.env.cr.savepoint():
        roy.with_user(w.officer).action_compute()
    with pytest.raises(UserError), w.env.cr.savepoint():
        roy.with_user(w.officer).write({"revenue_basis": 1.0})
    # the rates froze with the agreement
    with pytest.raises(UserError), w.env.cr.savepoint():
        fr.with_user(w.officer).write({"royalty_rate": 0.01})


def test_royalty_is_computed_from_the_branchs_m20_revenue(w):
    """A04 ERP audit M40-F19: the basis is the branch's M20 invoices (ex-VAT,
    net of credit notes), not settled service-order cash."""
    ou = w.env["operating.unit"].search([], limit=1)
    if not ou:
        pytest.skip("no operating unit on this database")
    fr = _franchise(w, operating_unit_id=ou.id)
    roy = _royalty(w, fr)
    domains = []
    invoice_cls = type(w.env["fix.ar.invoice"])
    real_search = invoice_cls.search

    def spy(self, domain, *a, **k):
        domains.append(domain)
        return real_search(self, domain, *a, **k)

    with mock.patch.object(invoice_cls, "search", spy):
        roy.with_user(w.officer).action_compute()
    dom = {c[0]: c[2] for d in domains for c in d if isinstance(c, list | tuple)}
    assert dom["operating_unit_id"] == ou.id and "paid" in dom["state"]
    assert roy.state == "computed" and roy.royalty_rate == 0.06
    with pytest.raises(UserError, match="finance"), w.env.cr.savepoint():
        roy.with_user(w.officer).action_raise_invoice()


def test_royalty_amounts_follow_the_basis(w):
    ou = w.env["operating.unit"].search([], limit=1)
    if not ou:
        pytest.skip("no operating unit on this database")
    roy = _royalty(w, _franchise(w, operating_unit_id=ou.id))
    royalty_cls = type(w.env["fix.franchise.royalty"])
    with mock.patch.object(royalty_cls, "_erp_revenue", lambda self: (250000.0, 0.0, 7)):
        roy.with_user(w.officer).action_compute()
    assert roy.royalty_amount == 15000.0 and roy.levy_amount == 2500.0 and roy.order_count == 7


# ================================================================== p9 MDF
def _fund(w, amount=10000):
    fund = (
        w.env["fix.mdf.fund"]
        .with_user(w.officer)
        .create(
            {
                "name": "MDF Q4",
                "partner_id": _partner(w).id,
                "period": "2026-Q4",
                "allocated": amount,
            }
        )
    )
    fund.with_user(w.manager).action_open()
    return fund


def _claim(w, fund, amount, evidence=True):
    claim = (
        w.env["fix.mdf.claim"]
        .with_user(w.officer)
        .create({"fund_id": fund.id, "amount": amount, "description": "Leaflets"})
    )
    if evidence:
        claim.with_user(w.officer).write({"evidence_attachment_id": _doc(w, claim).id})
    return claim


def test_mdf_claim_needs_evidence_and_an_independent_decider(w):
    fund = _fund(w)
    bare = _claim(w, fund, 1000, evidence=False)
    with pytest.raises(ValidationError, match="BRU-PCM-11"), w.env.cr.savepoint():
        bare.with_user(w.officer).action_submit()
    claim = _claim(w, fund, 4000)
    claim.with_user(w.officer).action_submit()
    # the fund's allocator may not decide it
    with pytest.raises(UserError, match="Segregation"), w.env.cr.savepoint():
        claim.with_user(w.manager).action_approve()
    configure_payout_accounts(w.env)  # A04 ERP audit M40-F3: fail closed without them
    claim.with_user(w.manager2).action_approve()
    assert claim.state == "approved" and fund.approved == 4000 and fund.balance == 6000


def test_mdf_claims_never_exceed_the_fund(w):
    fund = _fund(w, 5000)
    _claim(w, fund, 4000).with_user(w.officer).action_submit()
    over = _claim(w, fund, 1500)
    with pytest.raises(ValidationError, match="exceeds"), w.env.cr.savepoint():
        over.with_user(w.officer).action_submit()


def test_mdf_refusal_and_payment(w):
    fund = _fund(w)
    a, b = _claim(w, fund, 1000), _claim(w, fund, 2000)
    a.with_user(w.officer).action_submit()
    b.with_user(w.officer).action_submit()
    with pytest.raises(UserError, match="reason"), w.env.cr.savepoint():
        a.with_user(w.manager2).action_refuse("")
    a.with_user(w.manager2).action_refuse("no proof of distribution")
    configure_payout_accounts(w.env)
    b.with_user(w.manager2).action_approve()
    with pytest.raises(UserError, match="finance"), w.env.cr.savepoint():
        b.with_user(w.officer).action_record_payment()
    # A04 ERP audit M40-F3: paid on the executed M50 instruction only
    with pytest.raises(UserError, match="no M50 payout"), w.env.cr.savepoint():
        b.with_user(w.finance).action_record_payment()
    pay = (
        w.env["fix.payment.execution"]
        .sudo()
        .create(
            {
                "company_id": w.env.company.id,
                "operating_unit_id": w.env["operating.unit"].search([], limit=1).id,
                "payee": "p",
                "amount": 2000.0,
                "source_model": b._name,
                "source_id": b.id,
            }
        )
    )
    guarded_write(pay, {"state": "executed", "bank_reference": "TRX-1"})
    b.with_user(w.finance).action_record_payment()
    assert b.state == "paid" and b.payment_ref == "TRX-1"
    assert fund.paid == 2000 and fund.balance == 8000
    with pytest.raises(UserError), w.env.cr.savepoint():
        b.with_user(w.officer).write({"amount": 9000})


# ================================================================ access
@pytest.mark.parametrize(
    "model",
    [
        "fix.partner.programme",
        "fix.partner.onboarding",
        "fix.brand.audit",
        "fix.alliance.scheme",
        "fix.partner.lead",
        "fix.reseller.allocation",
        "fix.franchise.territory",
        "fix.mdf.fund",
    ],
)
def test_a_plain_employee_reads_but_never_captures(w, model):
    w.env[model].with_user(w.clerk).search([], limit=1)
    with pytest.raises(AccessError), w.env.cr.savepoint():
        w.env[model].with_user(w.clerk).create({})


def test_nobody_deletes_a_register(w):
    p = _partner(w, onboard=False)
    step = (
        w.env["fix.partner.onboarding"]
        .with_user(w.officer)
        .create({"partner_id": p.id, "step": "banking", "name": "Bank"})
    )
    with pytest.raises(AccessError), w.env.cr.savepoint():
        step.with_user(w.manager).unlink()


def test_crons_exist_and_run(w):
    for xmlid in (
        "cd_partner.ir_cron_brand_obligation_overdue",
        "cd_partner.ir_cron_partner_enablement_expiry",
    ):
        cron = w.env.ref(xmlid)
        assert cron.active
    for code in ("fix.partner.lead", "fix.mdf.claim", "fix.reseller.allocation"):
        assert w.env["ir.sequence"].search_count([("code", "=", code)])
