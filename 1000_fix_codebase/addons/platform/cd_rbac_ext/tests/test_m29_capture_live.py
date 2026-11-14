"""M29 capture audit (2026-11-14): the captures the seven sub-module pages now
offer, driven through /p03/model/form, /p03/model/write and /p03/model/action
as NON-ADMIN users with the fields m29.js posts. The superuser is trusted by
the model guards and would hide a gap.

  * Identity & MFA - "Record a Joiner / Mover / Leaver" (M29-form-jml).
  * Monitoring & Audit - "Report a Security Incident" (writes its own audit row,
    so the capture lands on the page's audit-trail grid), the break-glass
    request, and the new vulnerability register (spec §10.1, BRU-SEC-21).
  * Every chip form of every page opens for its intended actor.
"""

from __future__ import annotations

import datetime
import re
import types
from pathlib import Path

import pytest
from odoo import fields

JS = Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src" / "a12" / "m29.js"
OFFICER = "cd_rbac_ext.group_security_officer"
APPROVER = "cd_rbac_ext.group_access_approver"


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
                "email": "%s@m29cap.test" % login,
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
    x.plain = _user(env, "m29cap_plain")
    x.other = _user(env, "m29cap_other")
    x.off1 = _user(env, "m29cap_off1", [OFFICER])
    x.off2 = _user(env, "m29cap_off2", [OFFICER])
    x.appr1 = _user(env, "m29cap_appr1", [APPROVER])
    x.appr2 = _user(env, "m29cap_appr2", [APPROVER])
    x.sys = _user(env, "m29cap_sys", ["base.group_system"])
    x.today = fields.Date.context_today(env["fix.vulnerability"].with_user(x.plain))
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
            action=lambda user, record_id=None, **kw: call(
                user, "model_action", ids=[record_id], **kw
            ),
            records=lambda user, **kw: call(user, "model_records", **kw),
            form=lambda user, **kw: call(user, "model_form", **kw),
        )
    finally:
        g.request = old


def _form_fields(screen):
    """The field list one m29.js form posts (its block, up to the next screen)."""
    js = JS.read_text(encoding="utf-8")
    start = js.index("'%s': {" % screen)
    nxt = re.compile(r"^  '(M29[-:][\w-]+)': \{", re.M).search(js, start + 10)
    block = js[start : nxt.start() if nxt else len(js)]
    return [{"name": n} for n in re.findall(r"name: '(\w+)'", block)]


def _audit_rows(c, ref):
    return c.env["fix.security.audit"].sudo().search([("object_ref", "=", ref)])


# ---------------------------------------------------------------- every chip opens
CHIP_ACTORS = {
    "M29-form-jml": "appr1",
    "M29-form-role": "sys",
    "M29-form-acl": "sys",
    "M29-form-rule": "sys",
    "M29-form-fieldrule": "sys",
    "M29-form-isolation-tier": "sys",
    "M29-form-request": "plain",
    "M29-form-campaign": "appr1",
    "M29-form-cert": "appr1",
    "M29-form-sodtest": "plain",
    "M29-form-sodcontrol": "sys",
    "M29-form-sodexception": "plain",
    "M29-form-sensitive": "sys",
    "M29-form-key": "sys",
    "M29-form-incident": "plain",
    "M29-form-session": "plain",
    "M29-form-vulnerability": "plain",
}
MODELS = {
    "M29-form-jml": "fix.jml.event",
    "M29-form-role": "fix.role",
    "M29-form-acl": "ir.model.access",
    "M29-form-rule": "ir.rule",
    "M29-form-fieldrule": "fix.field.rule",
    "M29-form-isolation-tier": "fix.isolation.tier",
    "M29-form-request": "fix.access.request",
    "M29-form-campaign": "fix.access.certification.campaign",
    "M29-form-cert": "fix.access.certification",
    "M29-form-sodtest": "fix.sod.test",
    "M29-form-sodcontrol": "fix.sod.control",
    "M29-form-sodexception": "fix.sod.mitigation",
    "M29-form-sensitive": "fix.sensitive.field",
    "M29-form-key": "fix.encryption.key",
    "M29-form-incident": "fix.security.incident",
    "M29-form-session": "fix.privileged.session",
    "M29-form-vulnerability": "fix.vulnerability",
}


@pytest.mark.parametrize("screen", sorted(CHIP_ACTORS))
def test_every_page_capture_opens_blank_for_its_actor(c, p03, screen):
    who = getattr(c, CHIP_ACTORS[screen])
    got = p03.form(who, model=MODELS[screen], fields=_form_fields(screen))
    assert not got.get("error"), (screen, got)


# ---------------------------------------------------------------- 1 Identity & MFA
def test_identity_page_records_a_joiner_applied_by_a_second_person(c, p03):
    target = _user(c.env, "m29cap_joiner")
    emp = c.env["hr.employee"].sudo().create({"name": "m29cap joiner", "user_id": target.id})
    role = c.env["fix.role"].sudo().search([("code", "=", "R-34")], limit=1) or c.env[
        "fix.role"
    ].sudo().search([], limit=1)
    res = p03.write(
        c.appr1,
        model="fix.jml.event",
        values={
            "event_type": "joiner",
            "employee_id": emp.id,
            "role_id": role.id,
            "effective_on": str(c.today),
        },
    )
    assert not res.get("error"), res
    event = c.env["fix.jml.event"].sudo().browse(res["id"])
    assert event.user_id == target and event.state == "pending"
    # the filer cannot apply their own event; a second approver can
    assert p03.action(
        c.appr1, model="fix.jml.event", record_id=event.id, method="action_apply"
    ).get("error")
    got = p03.action(c.appr2, model="fix.jml.event", record_id=event.id, method="action_apply")
    if got.get("error"):
        # a role that maps to no group, or an SoD block, refuses honestly - never silently
        assert "group" in got["error"] or "SoD" in got["error"] or "duty" in got["error"], got
        assert event.state == "pending"
    else:
        assert event.state == "applied"


def test_a_login_is_never_created_from_the_user_form_chip():
    js = JS.read_text(encoding="utf-8")
    block = js[js.index("'M29-form-user': {") : js.index("'M29-form-jml': {")]
    assert "create: false," in block


# ---------------------------------------------------------------- 7 Monitoring & Audit
def test_a_plain_user_reports_an_incident_and_it_lands_on_the_audit_trail(c, p03):
    res = p03.write(
        c.plain,
        model="fix.security.incident",
        values={
            "title": "Phishing mail asking for the payroll password",
            "category": "phishing",
            "severity": "high",
            "detected_at": fields.Datetime.to_string(fields.Datetime.now()),
        },
    )
    assert not res.get("error"), res
    rows = _audit_rows(c, "fix.security.incident,%d" % res["id"])
    assert len(rows) == 1 and rows.event == "incident"
    assert "incident reported" in rows.detail and "high" in rows.detail
    assert "payroll" not in rows.detail, "the title must not reach the trail every user reads"
    assert rows.actor_id == c.plain


def test_a_plain_user_requests_break_glass_access_in_their_own_name(c, p03):
    res = p03.write(
        c.plain,
        model="fix.privileged.session",
        values={"access_kind": "db_console", "reason": "Restore the stuck payroll batch"},
    )
    assert not res.get("error"), res
    session = c.env["fix.privileged.session"].sudo().browse(res["id"])
    assert session.user_id == c.plain and session.state == "requested"


def _report(c, p03, **values):
    vals = {
        "title": "OpenSSL in the API image",
        "severity": "critical",
        "source": "container",
        "component": "api-gateway image",
        "discovered_on": str(c.today),
    }
    vals.update(values)
    res = p03.write(c.plain, model="fix.vulnerability", values=vals)
    assert not res.get("error"), res
    return c.env["fix.vulnerability"].sudo().browse(res["id"])


def test_a_plain_user_records_a_vulnerability(c, p03):
    v = _report(c, p03, owner_id=c.other.id)
    assert v.name.startswith("VULN/")
    assert v.reported_by_id == c.plain and v.state == "open"
    assert v.sla_due == c.today + datetime.timedelta(days=7), "critical: 7 days (BRU-SEC-21)"
    rows = _audit_rows(c, "fix.vulnerability,%d" % v.id)
    assert rows and "api-gateway" not in rows[0].detail
    # a typed stamp is refused, not honoured
    res = p03.write(
        c.plain,
        model="fix.vulnerability",
        values={
            "title": "x",
            "severity": "low",
            "source": "sast",
            "component": "y",
            "state": "verified",
            "reported_by_id": c.other.id,
        },
    )
    if not res.get("error"):
        rec = c.env["fix.vulnerability"].sudo().browse(res["id"])
        assert rec.state == "open" and rec.reported_by_id == c.plain


def test_vulnerabilities_are_read_by_reporter_owner_and_officers_only(c, p03):
    v = _report(c, p03, owner_id=c.other.id)
    stranger = _user(c.env, "m29cap_stranger")
    for who, sees in ((c.plain, True), (c.other, True), (c.off1, True), (stranger, False)):
        rows = p03.records(
            who, model="fix.vulnerability", cols=["name"], domain=[("id", "=", v.id)]
        )
        assert bool(rows.get("rows")) is sees, who.login


def test_only_an_officer_re_rates_and_the_change_is_audited(c, p03):
    v = _report(c, p03)
    res = p03.write(c.plain, model="fix.vulnerability", record_id=v.id, values={"severity": "low"})
    assert res.get("error") and v.severity == "critical"
    res = p03.write(c.off1, model="fix.vulnerability", record_id=v.id, values={"severity": "high"})
    assert not res.get("error"), res
    assert v.severity == "high" and v.sla_due == c.today + datetime.timedelta(days=30)
    assert any(
        "critical -> high" in r.detail for r in _audit_rows(c, "fix.vulnerability,%d" % v.id)
    )


def test_remediation_needs_the_owner_and_closure_a_second_officer(c, p03):
    v = _report(c, p03, owner_id=c.other.id)
    note = "Rebuilt the image on openssl 3.0.15 and redeployed"
    assert p03.action(
        c.plain,
        model="fix.vulnerability",
        record_id=v.id,
        method="action_remediate",
        kwargs={"note": note},
    ).get("error")
    got = p03.action(
        c.other,
        model="fix.vulnerability",
        record_id=v.id,
        method="action_remediate",
        kwargs={"note": note},
    )
    assert not got.get("error"), got
    assert v.state == "remediated" and v.remediated_by_id == c.other
    # the owner is no officer; an officer who remediated could not verify
    assert p03.action(
        c.other, model="fix.vulnerability", record_id=v.id, method="action_verify"
    ).get("error")
    got = p03.action(c.off1, model="fix.vulnerability", record_id=v.id, method="action_verify")
    assert not got.get("error"), got
    assert v.state == "verified" and v.verified_by_id == c.off1
    res = p03.write(c.off1, model="fix.vulnerability", record_id=v.id, values={"title": "edited"})
    assert res.get("error"), "a closed finding cannot change"


def test_an_officer_cannot_verify_their_own_remediation(c, p03):
    v = _report(c, p03)
    p03.action(
        c.off1,
        model="fix.vulnerability",
        record_id=v.id,
        method="action_remediate",
        kwargs={"note": "Patched the host kernel and rebooted it"},
    )
    assert p03.action(
        c.off1, model="fix.vulnerability", record_id=v.id, method="action_verify"
    ).get("error")
    assert not p03.action(
        c.off2, model="fix.vulnerability", record_id=v.id, method="action_verify"
    ).get("error")


def test_risk_acceptance_is_a_second_officer_decision_and_lapses(c, p03):
    reason = "Compensating WAF rule blocks the vector until the vendor ships a fix"
    v = _report(c, p03, owner_id=c.off1.id)
    # the owner may not accept their own finding
    assert p03.action(
        c.off1,
        model="fix.vulnerability",
        record_id=v.id,
        method="action_accept_risk",
        kwargs={"reason": reason},
    ).get("error")
    got = p03.action(
        c.off2,
        model="fix.vulnerability",
        record_id=v.id,
        method="action_accept_risk",
        kwargs={"reason": reason},
    )
    assert not got.get("error"), got
    assert v.state == "accepted" and v.accepted_until == c.today + datetime.timedelta(days=90)
    v.sudo()._guarded().write({"accepted_until": c.today - datetime.timedelta(days=1)})
    c.env["fix.vulnerability"]._cron_escalate_critical()
    assert v.state == "open"


def test_a_critical_past_due_is_escalated_once(c, p03):
    v = _report(c, p03, discovered_on=str(c.today - datetime.timedelta(days=10)))
    assert v.with_user(c.plain).is_overdue
    Vuln = c.env["fix.vulnerability"]
    assert Vuln._cron_escalate_critical() >= 1
    assert v.escalated_on
    assert any(
        r.event == "vulnerability.critical_open"
        for r in _audit_rows(c, "fix.vulnerability,%d" % v.id)
    )
    assert v.activity_ids
    escalated = v.escalated_on
    Vuln._cron_escalate_critical()
    assert v.escalated_on == escalated


def test_register_report_and_kpi_read_as_the_caller(c, p03):
    from odoo.addons.cd_p03_portal.controllers.a12 import m29

    mine = _report(c, p03, discovered_on=str(c.today - datetime.timedelta(days=10)))
    stranger = _user(c.env, "m29cap_stranger2")
    pack = m29.vulnerability_register(c.env(user=c.plain.id))
    assert mine.name in [r["name"] for r in pack["rows"]]
    assert "critical past due" in pack["title"]
    assert mine.name not in [
        r["name"] for r in m29.vulnerability_register(c.env(user=stranger.id))["rows"]
    ]
    assert m29.kpis(c.env(user=c.plain.id))["critical_vulns_overdue"] >= 1
    assert m29.kpis(c.env(user=stranger.id))["critical_vulns_overdue"] == 0
