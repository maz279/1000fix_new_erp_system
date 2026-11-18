"""M65 capture audit (2026-11-18): the captures the six sub-module pages now
offer, driven through /p03/model/form, /p03/model/write, /p03/model/action and
/p03/model/report as NON-ADMIN users (Platform Admins who are not system
administrators, an accountant) with the fields m65.js posts. The superuser is
trusted by the model guards and would hide a gap.

  * Every chip form of every page opens blank for its actor.
  * Entity Structure: an entity is assigned an ACTIVE pack only; the version is
    recorded; a new assignment supersedes the old one, which stays; an
    assignment is never edited or deleted; the report shows the packs in use.
  * Jurisdiction: a residency rule is verified by a second Platform Admin, a
    contradictory rule is refused, verifying a newer rule retires the old one.
  * Jurisdiction: a country onboarding is refused each step until its
    registers hold what it needs; the zero-core-change gate refuses the pilot;
    a second person activates.
  * Translation: a second person approves; machine translation is refused; an
    approved record translation is written into the record in that language,
    as the reviewer; a stale source is refused.
  * Translation: rendering evidence is never edited, a failure names its
    issues, and the Bengali report lists per target what was verified.
  * A plain employee reads the registers but captures none of them.
"""

from __future__ import annotations

import re
import types
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

JS = Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src" / "a12" / "m65.js"
JS19 = Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src" / "a08" / "m19.js"
PA = "cd_entity_config.group_platform_admin"
STEWARD = "cd_entity_config.group_mdm_domain_steward"
SYSTEM = "base.group_system"
ACCOUNTANT = "account.group_account_manager"
REFUSED = (UserError, ValidationError, AccessError)


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "email": "%s@m65cap.test" % login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.plain = _user(env, "m65cap_plain")
    x.pa1 = _user(env, "m65cap_pa1", [PA])
    x.pa2 = _user(env, "m65cap_pa2", [PA])
    x.steward = _user(env, "m65cap_steward", [STEWARD])
    x.sys = _user(env, "m65cap_sys", [SYSTEM, PA])
    x.acct = _user(env, "m65cap_acct", [ACCOUNTANT])
    assert not x.pa1.has_group(SYSTEM), "the Platform Admin under test must not be a system admin"
    return x


@pytest.fixture
def p03(odoo_env):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()

    def ep(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    old = getattr(g, "request", None)

    def call(user, name, **kw):
        g.request = types.SimpleNamespace(env=odoo_env(user=user.id))
        return ep(name)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            write=lambda user, **kw: call(user, "model_write", **kw),
            action=lambda user, model, record_id, method, **kwargs: call(
                user, "model_action", model=model, ids=[record_id], method=method, kwargs=kwargs
            ),
            records=lambda user, **kw: call(user, "model_records", **kw),
            form=lambda user, **kw: call(user, "model_form", **kw),
        )
    finally:
        g.request = old


def _form_fields(screen, js=JS):
    """The field list one form posts (its block, up to the next screen)."""
    text = js.read_text(encoding="utf-8")
    start = text.index("'%s': {" % screen)
    nxt = re.compile(r"^  '(M\d\d[-:][\w-]+)': \{", re.M).search(text, start + 10)
    block = text[start : nxt.start() if nxt else len(text)]
    return [{"name": n} for n in re.findall(r"name: '(\w+)'", block)]


def _err(res):
    return res.get("error") or (res.get("success") is False and "failed")


def _report(env, user, name):
    from odoo.addons.cd_p03_portal.controllers.a12 import m65

    return getattr(m65, name)(env(user=user.id))


# ------------------------------------------------------------------ fixtures
def _active_pack(c, code, kind="holidays", version="2026.1"):
    """A pack walked through its real lifecycle: pa1 authors, pa2 certifies."""
    Pack = c.env["fix.country.pack"]
    pack = Pack.with_user(c.pa1).create(
        {"name": "M65 cap %s" % code, "code": code, "kind": kind, "version": version}
    )
    c.env["fix.country.pack.line"].with_user(c.pa1).create(
        {
            "pack_id": pack.id,
            "code": code + "-1",
            "name": "Day One",
            "name_bn": "প্রথম দিন",
            "date_value": "2026-12-16",
        }
    )
    pack.with_user(c.pa1).action_validate()
    pack.with_user(c.pa2).action_certify(note="Checked against the 2026 gazette, 01/01/2026")
    pack.with_user(c.pa1).action_activate()
    assert pack.state == "active"
    return pack


def _entity(c, code="M65CAP"):
    return (
        c.env["fix.entity"]
        .sudo()
        .create(
            {
                "code": code,
                "legal_name": "M65 Capture Test Ltd",
                "company_id": c.env.company.id,
                "country_id": c.env.ref("base.bd").id,
                "currency_id": c.env.ref("base.BDT").id,
            }
        )
    )


def _active_locale(c, code):
    Locale = c.env["fix.locale.pack"].sudo()
    # one pack per code and company: reuse it (the live estate has bn_BD active)
    pack = Locale.search([("code", "=", code), ("company_id", "=", c.env.company.id)], limit=1)
    c.env["res.lang"]._activate_lang(code)
    if pack and pack.state != "active":
        pack._guarded().write({"state": "active"})
    if not pack:
        pack = Locale.create(
            {
                "code": code,
                "name": "Locale %s" % code,
                "number_format": Locale._fields["number_format"].selection[0][0],
                "date_format": "DD/MM/YYYY",
            }
        )
        pack._guarded().write({"state": "active"})
    return pack


# ---------------------------------------------------------------- every chip opens
CHIPS = {
    "M65-form-entity": ("fix.entity", "pa1", JS),
    "M65-form-entity-pack": ("fix.entity.jurisdiction", "pa1", JS),
    "M65-form-country": ("fix.country.pack", "pa1", JS),
    "M65-form-packline": ("fix.country.pack.line", "pa1", JS),
    "M65-form-gateway": ("fix.payment.gateway", "pa1", JS),
    "M65-form-locale": ("fix.locale.pack", "pa1", JS),
    "M65-form-jurisdiction": ("fix.jurisdiction.rule", "pa1", JS),
    "M65-form-residency": ("fix.jurisdiction.residency.rule", "pa1", JS),
    "M65-form-onboarding": ("fix.country.onboarding", "pa1", JS),
    "M65-form-translation": ("fix.translation.entry", "steward", JS),
    "M65-form-rendering": ("fix.rendering.verification", "steward", JS),
    "M19-form-icrule": ("fix.intercompany.rule", "acct", JS19),
    "M19-form-ic": ("fix.intercompany.transaction", "acct", JS19),
    "M19-form-tp-rate": ("fix.transfer.price.rate", "acct", JS19),
}


@pytest.mark.parametrize("screen", sorted(CHIPS))
def test_every_page_capture_opens_blank_for_its_actor(c, p03, screen):
    model, who, js = CHIPS[screen]
    got = p03.form(getattr(c, who), model=model, fields=_form_fields(screen, js))
    assert not got.get("error"), (screen, got)


NEW = (
    "fix.entity.jurisdiction",
    "fix.jurisdiction.residency.rule",
    "fix.country.onboarding",
    "fix.translation.entry",
    "fix.rendering.verification",
)


@pytest.mark.parametrize("model", NEW)
def test_a_plain_employee_reads_but_never_captures(c, p03, model):
    got = p03.records(c.plain, model=model, cols=["id"])
    assert not got.get("error"), (model, got)
    assert not c.env[model].with_user(c.plain).has_access("create")


def test_the_page_lists_serve_their_records(c, p03):
    for model, who in (
        ("fix.entity.jurisdiction", c.pa1),
        ("fix.intercompany.rule", c.acct),
        ("fix.intercompany.transaction", c.acct),
        ("fix.transfer.price.rate", c.acct),
    ):
        got = p03.records(who, model=model, cols=["id"])
        assert not got.get("error"), (model, got)


# ---------------------------------------------------------------- 1 Entity Structure
def test_an_entity_is_assigned_an_active_pack_and_reassigning_supersedes(c, p03):
    entity = _entity(c)
    draft = (
        c.env["fix.country.pack"]
        .with_user(c.pa1)
        .create({"name": "Draft pack", "code": "M65C-DRAFT", "kind": "holidays"})
    )
    res = p03.write(
        c.pa1,
        model="fix.entity.jurisdiction",
        values={"entity_id": entity.id, "country_pack_id": draft.id},
    )
    assert _err(res) and "active" in str(res), res

    first = _active_pack(c, "M65C-H1", version="2026.1")
    res = p03.write(
        c.pa1,
        model="fix.entity.jurisdiction",
        values={
            "entity_id": entity.id,
            "country_pack_id": first.id,
            "reporting_currency_id": c.env.ref("base.USD").id,
            # a stamp typed by the form is dropped: the version is the pack's
            "pack_version": "9.9",
            "state": "superseded",
        },
    )
    assert not _err(res), res
    a1 = c.env["fix.entity.jurisdiction"].browse(res["id"])
    assert (a1.state, a1.pack_version, a1.assigned_by_id) == ("current", "2026.1", c.pa1)

    # an assignment is history
    second = _active_pack(c, "M65C-H2", version="2027.1")
    with pytest.raises(REFUSED):
        a1.with_user(c.pa1).write({"country_pack_id": second.id})
    with pytest.raises(REFUSED):
        a1.with_user(c.pa1).unlink()

    res = p03.write(
        c.pa1,
        model="fix.entity.jurisdiction",
        values={"entity_id": entity.id, "country_pack_id": second.id},
    )
    assert not _err(res), res
    a2 = c.env["fix.entity.jurisdiction"].browse(res["id"])
    assert a1.state == "superseded" and a1.superseded_by_id == a2
    assert a2.state == "current"

    # only a Platform Admin assigns
    res = p03.write(
        c.plain,
        model="fix.entity.jurisdiction",
        values={"entity_id": entity.id, "country_pack_id": second.id},
    )
    assert _err(res), res

    rows = _report(c.env, c.pa1, "entity_structure")["rows"]
    row = next(r for r in rows if r["code"] == "M65CAP")
    assert row["packs"] == "M65C-H2 v2027.1", row


# ---------------------------------------------------------------- 4 Jurisdiction
def _residency(c, p03, user, **extra):
    vals = {
        "country_id": c.env.ref("base.np").id,
        "data_class": "personal",
        "residency_required": False,
        "cross_border_permitted": True,
        "notification_required": True,
        "safeguard_required": "Explicit consent",
        "authority_name": "Department of Information Technology",
        "statute_reference": "Privacy Act 2075 s.21",
        "effective_from": "2026-01-01",
    }
    vals.update(extra)
    return p03.write(user, model="fix.jurisdiction.residency.rule", values=vals)


def test_a_residency_rule_is_verified_by_a_second_admin_and_frozen(c, p03):
    bad = _residency(c, p03, c.pa1, residency_required=True, cross_border_permitted=True)
    assert _err(bad), bad

    res = _residency(c, p03, c.pa1)
    assert not _err(res), res
    rule = c.env["fix.jurisdiction.residency.rule"].browse(res["id"])

    own = p03.action(
        c.pa1,
        "fix.jurisdiction.residency.rule",
        rule.id,
        "action_verify",
        note="Privacy Act 2075 section 21",
    )
    assert _err(own) and rule.state == "draft", own
    short = p03.action(
        c.pa2, "fix.jurisdiction.residency.rule", rule.id, "action_verify", note="ok"
    )
    assert _err(short) and rule.state == "draft", short
    ok = p03.action(
        c.pa2,
        "fix.jurisdiction.residency.rule",
        rule.id,
        "action_verify",
        note="Privacy Act 2075 section 21, gazette 2018",
    )
    assert not _err(ok), ok
    assert (rule.state, rule.verified_by_id) == ("verified", c.pa2)

    with pytest.raises(REFUSED):
        rule.with_user(c.pa1).write({"authority_name": "Someone else"})

    newer = _residency(c, p03, c.pa1, effective_from="2027-01-01")
    newer_rule = c.env["fix.jurisdiction.residency.rule"].browse(newer["id"])
    newer_rule.with_user(c.pa2).action_verify(note="Privacy Act 2075 as amended 2026")
    assert rule.state == "retired" and newer_rule.state == "verified"


def test_an_onboarding_is_gated_step_by_step(c, p03):
    nepal = c.env.ref("base.np")
    res = p03.write(
        c.pa1, model="fix.country.onboarding", values={"country_id": nepal.id, "lead_id": c.pa1.id}
    )
    assert not _err(res), res
    onb = c.env["fix.country.onboarding"].browse(res["id"])
    assert onb.phase == "discovery" and onb.initiated_on and onb.name.startswith("ONB/")

    def advance(user=c.pa1):
        return p03.action(user, "fix.country.onboarding", onb.id, "action_advance")

    assert _err(advance()) and onb.phase == "discovery"  # no obligations yet
    c.env["fix.jurisdiction.rule"].with_user(c.pa1).create(
        {
            "jurisdiction": "NP-IRD",
            "rule_area": "tax",
            "requirement": "VAT return",
            "frequency": "monthly",
        }
    )
    assert onb.obligations_discovered >= 1
    assert not _err(advance()) and onb.phase == "pack_authoring"

    assert _err(advance())  # no packs named
    pack = _active_pack(c, "M65C-NP")
    onb.with_user(c.pa1).write({"pack_ids": [(6, 0, pack.ids)]})
    assert not _err(advance()) and onb.phase == "translation"

    assert _err(advance())  # no locale
    locale = _active_locale(c, "ne_NP")
    onb.with_user(c.pa1).write({"locale_pack_id": locale.id})
    assert not _err(advance()) and onb.phase == "integration"

    assert _err(advance())  # no gateway
    gateway = (
        c.env["fix.payment.gateway"]
        .sudo()
        .create(
            {
                "provider": "eSewa",
                "country_code": "NP",
                "currencies": "NPR",
                "credential_ref": "vault://m65cap/esewa",
            }
        )
    )
    onb.with_user(c.pa1).write({"gateway_ids": [(6, 0, gateway.ids)]})
    assert not _err(advance()) and onb.phase == "validation"

    # BRU-GLO-02: a core code change fails the gate
    onb.with_user(c.pa1).write({"core_changes_required": True, "core_change_note": "NP VAT"})
    blocked = advance()
    assert "Zero-core-change gate FAILED" in str(blocked) and onb.gate_result == "failed"
    onb.with_user(c.pa1).write({"core_changes_required": False})
    assert _err(advance()) and onb.phase == "validation"  # no verified residency rule
    rule = c.env["fix.jurisdiction.residency.rule"].browse(_residency(c, p03, c.pa1)["id"])
    rule.with_user(c.pa2).action_verify(note="Privacy Act 2075 section 21")
    assert onb.residency_assessed
    assert not _err(advance()) and onb.phase == "pilot" and onb.piloted_on
    assert onb.gate_result == "passed"

    assert _err(advance())  # the gateway is not active
    gateway.sudo().write({"state": "active"})
    assert _err(advance()) and onb.phase == "pilot"  # the creator cannot activate
    assert not _err(advance(c.pa2)), onb.phase
    assert onb.phase == "active" and onb.activated_by_id == c.pa2
    with pytest.raises(REFUSED):
        onb.with_user(c.pa1).write({"core_change_note": "edited afterwards"})

    rows = _report(c.env, c.pa1, "expansion_assessment")["rows"]
    row = next(r for r in rows if r["country"] == "NP")
    assert row["residency_rules"] >= 1 and onb.name in row["onboarding"], row


def test_abandoning_needs_a_reason(c, p03):
    onb = (
        c.env["fix.country.onboarding"]
        .with_user(c.pa1)
        .create({"country_id": c.env.ref("base.mm").id})
    )
    assert _err(p03.action(c.pa1, "fix.country.onboarding", onb.id, "action_abandon", reason="no"))
    ok = p03.action(
        c.pa1, "fix.country.onboarding", onb.id, "action_abandon", reason="Market entry postponed"
    )
    assert not _err(ok) and onb.phase == "abandoned"


# ---------------------------------------------------------------- 5 Translation
def _bn(c):
    return _active_locale(c, "bn_BD")


def test_a_record_translation_is_approved_by_a_second_person_and_written(c, p03):
    bn = _bn(c)
    nepal = c.env.ref("base.np")
    res = p03.write(
        c.pa1,
        model="fix.translation.entry",
        values={
            "locale_pack_id": bn.id,
            "module_code": "M65",
            "target_model": "res.country",
            "target_id": nepal.id,
            "target_field": "name",
            "translated_string": "নেপাল",
        },
    )
    assert not _err(res), res
    entry = c.env["fix.translation.entry"].browse(res["id"])
    assert entry.source_string == nepal.with_context(lang="en_US").name
    assert entry.translated_by_id == c.pa1 and entry.state == "submitted"

    own = p03.action(
        c.pa1, "fix.translation.entry", entry.id, "action_approve", note="Native check done"
    )
    assert _err(own) and entry.state == "submitted", own
    # a reviewer who may not edit countries cannot write the translation
    blocked = p03.action(
        c.pa2, "fix.translation.entry", entry.id, "action_approve", note="Native check done"
    )
    assert _err(blocked) and entry.state == "submitted", blocked
    ok = p03.action(
        c.sys, "fix.translation.entry", entry.id, "action_approve", note="Native check done"
    )
    assert not _err(ok), ok
    assert entry.state == "approved" and entry.applied and entry.reviewed_by_id == c.sys
    assert nepal.with_context(lang="bn_BD").name == "নেপাল"
    assert nepal.with_context(lang="en_US").name == entry.source_string
    with pytest.raises(REFUSED):
        entry.with_user(c.pa1).write({"translated_string": "changed"})


def test_a_translator_never_approves_their_own_translation(c, p03):
    """An interface string needs no write access on any record, so only the
    second-person rule stops the translator approving it."""
    bn = _bn(c)
    entry = (
        c.env["fix.translation.entry"]
        .with_user(c.pa1)
        .create(
            {
                "locale_pack_id": bn.id,
                "module_code": "P03",
                "source_string": "Submit",
                "translated_string": "জমা দিন",
            }
        )
    )
    got = p03.action(
        c.pa1, "fix.translation.entry", entry.id, "action_approve", note="Native check done"
    )
    assert "second person" in str(got) and entry.state == "submitted", got
    ok = p03.action(
        c.steward, "fix.translation.entry", entry.id, "action_approve", note="Native check done"
    )
    assert not _err(ok) and entry.reviewed_by_id == c.steward, ok


def test_machine_translation_and_stale_sources_are_refused(c, p03):
    bn = _bn(c)
    mt = (
        c.env["fix.translation.entry"]
        .with_user(c.steward)
        .create(
            {
                "locale_pack_id": bn.id,
                "module_code": "P03",
                "source_string": "Save",
                "translated_string": "সংরক্ষণ",
                "machine_translated": True,
            }
        )
    )
    got = p03.action(
        c.pa1, "fix.translation.entry", mt.id, "action_approve", note="Native check done"
    )
    assert "Machine translation" in str(got) and mt.state == "submitted", got
    assert not _err(
        p03.action(
            c.pa1, "fix.translation.entry", mt.id, "action_reject", note="Machine translated"
        )
    )
    assert mt.state == "rejected"

    ui = (
        c.env["fix.translation.entry"]
        .with_user(c.steward)
        .create(
            {
                "locale_pack_id": bn.id,
                "module_code": "P03",
                "source_string": "Cancel",
                "translated_string": "বাতিল",
            }
        )
    )
    assert not _err(
        p03.action(
            c.pa1, "fix.translation.entry", ui.id, "action_approve", note="Native check done"
        )
    )
    assert ui.state == "approved" and not ui.applied

    nepal = c.env.ref("base.np")
    stale = (
        c.env["fix.translation.entry"]
        .with_user(c.steward)
        .create(
            {
                "locale_pack_id": bn.id,
                "target_model": "res.country",
                "target_id": nepal.id,
                "target_field": "name",
                "translated_string": "নেপাল",
            }
        )
    )
    nepal.sudo().with_context(lang="en_US").write({"name": "Federal Nepal"})
    assert stale.is_stale
    got = p03.action(
        c.sys, "fix.translation.entry", stale.id, "action_approve", note="Native check done"
    )
    assert _err(got) and stale.state == "submitted", got

    rows = _report(c.env, c.pa1, "translation_completeness")["rows"]
    row = next(r for r in rows if r["locale"] == "bn_BD")
    assert row["rejected"] >= 1 and row["approved"] >= 1 and row["in_review"] >= 1, row


def test_a_target_must_be_a_real_translatable_field(c):
    bn = _bn(c)
    with pytest.raises(ValidationError):
        c.env["fix.translation.entry"].with_user(c.steward).create(
            {
                "locale_pack_id": bn.id,
                "target_model": "res.country",
                "target_id": c.env.ref("base.np").id,
                "target_field": "code",
                "translated_string": "x",
            }
        )


def test_rendering_evidence_is_kept_and_reported(c, p03):
    bn = _bn(c)
    fail = p03.write(
        c.steward,
        model="fix.rendering.verification",
        values={
            "locale_pack_id": bn.id,
            "target": "thermal",
            "device": "Xprinter XP-58",
            "test_set_ref": "Conjunct set v1",
            "verified_on": "2026-11-18",
            "result": "fail",
        },
    )
    assert _err(fail), fail
    ok = p03.write(
        c.steward,
        model="fix.rendering.verification",
        values={
            "locale_pack_id": bn.id,
            "target": "android",
            "device": "Samsung A15",
            "test_set_ref": "Conjunct set v1",
            "verified_on": "2026-11-18",
            "result": "pass",
        },
    )
    assert not _err(ok), ok
    rec = c.env["fix.rendering.verification"].browse(ok["id"])
    assert rec.verified_by_id == c.steward
    with pytest.raises(REFUSED):
        rec.with_user(c.steward).write({"result": "fail", "issues": "changed my mind"})
    with pytest.raises(REFUSED):
        rec.with_user(c.pa1).unlink()

    rows = _report(c.env, c.pa1, "bengali_support")["rows"]
    row = next(r for r in rows if r["locale"] == "bn_BD")
    assert "Android" in row["rendering_pass"], row
    assert "Android" not in row["rendering_fail"] + row["rendering_unverified"], row
    # every target with no verification of its own is listed as not verified
    Verification = c.env["fix.rendering.verification"]
    labels = dict(Verification._fields["target"].selection)
    done = set(Verification.search([("locale_pack_id", "=", bn.id)]).mapped("target"))
    for target, label in labels.items():
        if target not in done:
            assert label in row["rendering_unverified"], (label, row)


# ---------------------------------------------------------------- KPIs
def test_the_new_kpis_are_served(c):
    from odoo.addons.cd_p03_portal.controllers.a12 import m65

    out = m65.kpis(c.env(user=c.pa1.id))
    assert {"translations_in_review", "onboardings_open"} <= set(out)
