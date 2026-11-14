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
    "M29-form-provision": "appr1",
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
    "M29-form-provision": "fix.jml.event",
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


# ---------------------------------------------------------------- Provision a New Login
# The user's report (14 Nov): the M29 Users screen offered no way to enter a new
# user, and the joiner path never created the Odoo login (Keycloak only).
def _roles(c):
    def mk(code, xmlid):
        return (
            c.env["fix.role"]
            .sudo()
            .create(
                {
                    "code": code,
                    "name": "m29cap %s" % code,
                    "group_ids": [(6, 0, [c.env.ref(xmlid).id])],
                }
            )
        )

    return mk("R-91", "base.group_partner_manager"), mk("R-92", "base.group_multi_currency")


def _newcomer(c, email="m29cap.newcomer@1000fix.test", code="M29CAP-NEW"):
    vals = {"name": "m29cap Newcomer", "employee_code": code}
    if email is not None:
        vals["work_email"] = email
    return c.env["hr.employee"].sudo().create(vals)


def _file_provision(c, p03, emp, role, extra=(), units=None, default=None):
    values = {
        "employee_id": emp.id,
        "role_id": role.id,
        "extra_role_ids": [r.id for r in extra],
        "effective_on": str(c.today),
    }
    if units is not None:
        values["operating_unit_ids"] = units.ids
    if default is not None:
        values["default_operating_unit_id"] = default.id
    res = p03.write(c.appr1, model="fix.jml.event", values=values)
    assert not res.get("error"), res
    return c.env["fix.jml.event"].sudo().browse(res["id"])


def test_provisioning_creates_the_login_with_the_stated_access(c, p03):
    main, extra = _roles(c)
    units = c.env["operating.unit"].sudo().search([], limit=2)
    emp = _newcomer(c)
    ev = _file_provision(c, p03, emp, main, [extra], units=units, default=units[-1:])
    assert ev.event_type == "joiner" and not ev.user_id
    assert ev.proposed_login == "m29cap.newcomer@1000fix.test"
    assert "R-91" in ev.permission_preview and "R-92" in ev.permission_preview
    assert "New login" in ev.permission_preview
    # the filer cannot apply it; a second Access Approver can
    assert p03.action(c.appr1, model="fix.jml.event", record_id=ev.id, method="action_apply").get(
        "error"
    )
    mails_before = (
        c.env["mail.mail"].sudo().search_count([("email_to", "=", "m29cap.newcomer@1000fix.test")])
    )
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert not got.get("error"), got
    user = emp.user_id
    assert user and user.login == "m29cap.newcomer@1000fix.test"
    assert ev.state == "applied" and ev.user_id == user
    assert "provisioned" in ev.result_note
    held = user.sudo().all_group_ids
    assert c.env.ref("base.group_partner_manager") in held
    assert c.env.ref("base.group_multi_currency") in held
    assert c.env.ref("base.group_system") not in held
    if "assigned_operating_unit_ids" in user._fields and units:
        assert set(units.ids) <= set(user.sudo().assigned_operating_unit_ids.ids)
        assert user.sudo().default_operating_unit_id == units[-1:]
    roles = (
        c.env["fix.role.assignment"].sudo().search([("user_id", "=", user.id)]).mapped("role_id")
    )
    assert {main, extra} <= set(roles)
    assert _audit_rows(c, "res.users,%d" % user.id).filtered(lambda r: r.event == "joiner_login")
    # the invitation is queued for the mail job, never sent inside the click
    assert (
        c.env["mail.mail"].sudo().search_count([("email_to", "=", "m29cap.newcomer@1000fix.test")])
        == mails_before + 1
    )


def test_provisioning_refuses_a_login_that_already_exists(c, p03):
    main, _extra = _roles(c)
    taken = _user(c.env, "m29cap.taken@1000fix.test")
    emp = _newcomer(c, email=taken.login.upper())
    ev = _file_provision(c, p03, emp, main)
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert got.get("error") and "already belongs" in got["error"]
    assert ev.state == "pending" and not emp.user_id


def test_provisioning_needs_a_work_email(c, p03):
    main, _extra = _roles(c)
    emp = _newcomer(c, email=None, code="M29CAP-NOMAIL")
    ev = _file_provision(c, p03, emp, main)
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert got.get("error") and "work email" in got["error"]
    assert not emp.user_id


def test_a_refused_grant_leaves_no_login_behind(c, p03):
    empty = c.env["fix.role"].sudo().create({"code": "R-93", "name": "m29cap empty"})
    emp = _newcomer(c, email="m29cap.refused@1000fix.test", code="M29CAP-REF")
    ev = _file_provision(c, p03, emp, empty)
    assert "no permission group" in ev.permission_preview
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert got.get("error")
    Users = c.env["res.users"].sudo().with_context(active_test=False)
    assert not Users.search_count([("login", "=", "m29cap.refused@1000fix.test")])
    assert not emp.user_id and ev.state == "pending"


def test_the_preview_flags_a_duty_conflict_between_the_chosen_roles(c, p03):
    main, extra = _roles(c)
    c.env["fix.sod.control"].sudo().create(
        {
            "code": "SOD-M29CAP",
            "name": "m29cap pair",
            "role_a_id": main.id,
            "role_b_id": extra.id,
            "conflict_action": "block",
        }
    )
    emp = _newcomer(c, email="m29cap.conflict@1000fix.test", code="M29CAP-SOD")
    ev = _file_provision(c, p03, emp, main, [extra])
    assert "DUTY CONFLICT SOD-M29CAP" in ev.permission_preview
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert got.get("error"), "a blocked pair refuses the whole event"
    Users = c.env["res.users"].sudo().with_context(active_test=False)
    assert not Users.search_count([("login", "=", "m29cap.conflict@1000fix.test")])


def test_the_employee_picker_offers_only_people_without_a_login(c, p03):
    spec = _form_fields("M29-form-provision")
    for f in spec:
        if f["name"] == "employee_id":
            f["domain"] = [["user_id", "=", False]]
    got = p03.form(c.appr1, model="fix.jml.event", fields=spec)
    assert not got.get("error"), got


# ---------------------------------------------------------------- the New User form (14 Nov, round 2)
# Per-module permission checklist (NetSuite-style levels, D365-style effective
# review, SAP-style "restrictions only narrow"), enforced by the workspace.
def _catalogue():
    from odoo.addons.cd_p03_portal.models.fix_jml_event_permissions import module_catalogue

    return {code: models_ for code, _n, _a, models_ in module_catalogue()}


def _lines_payload(ev, changes):
    rows = []
    for line in ev.permission_line_ids:
        if line.module_code in changes:
            rows.append({"id": line.id, "values": changes[line.module_code]})
    return {"field": "permission_line_ids", "rows": rows, "removed": []}


def _readable_line(c, ev, user):
    """A checklist module with a served model the given user can read."""
    cat = _catalogue()
    for line in ev.permission_line_ids:
        for model in sorted(cat.get(line.module_code, ())):
            if model in c.env and c.env[model].with_user(user).has_access("read"):
                return line, model
    raise AssertionError("no readable module on the checklist")


def test_the_checklist_fills_in_from_the_roles(c, p03):
    main, extra = _roles(c)
    emp = _newcomer(c, email="m29cap.check@1000fix.test", code="M29CAP-CHK")
    ev = _file_provision(c, p03, emp, main, [extra])
    assert ev.permission_line_ids, "saving the roles fills the module checklist"
    for line in ev.permission_line_ids:
        assert line.allowed_level in ("view", "create", "edit")
        assert line.level == line.allowed_level, "starts at what the roles allow"
        assert line.can_print and line.can_export and line.can_email
    got = p03.form(
        c.appr1,
        model="fix.jml.event",
        record_id=ev.id,
        fields=_form_fields("M29-form-provision"),
        lines={
            "field": "permission_line_ids",
            "fields": [{"name": n} for n in ("module_name", "allowed_label", "level", "can_print")],
        },
    )
    assert not got.get("error"), got


def test_the_checklist_never_grants_more_than_the_roles(c, p03):
    main, _extra = _roles(c)
    emp = _newcomer(c, email="m29cap.more@1000fix.test", code="M29CAP-MORE")
    ev = _file_provision(c, p03, emp, main)
    line = ev.permission_line_ids.filtered(lambda r: r.allowed_level != "edit")[:1]
    if not line:
        pytest.skip("every module allows edit for this role")
    res = p03.write(
        c.appr1,
        model="fix.jml.event",
        record_id=ev.id,
        values={},
        lines=_lines_payload(ev, {line.module_code: {"level": "edit"}}),
    )
    assert res.get("error") and "add a role" in res["error"]
    assert line.level == line.allowed_level


def test_narrowing_is_applied_and_enforced_by_the_workspace(c, p03):
    main, extra = _roles(c)
    emp = _newcomer(c, email="m29cap.narrow@1000fix.test", code="M29CAP-NAR")
    ev = _file_provision(c, p03, emp, main, [extra])
    probe_user = _user(c.env, "m29cap_probe")
    line, model = _readable_line(c, ev, probe_user)
    res = p03.write(
        c.appr1,
        model="fix.jml.event",
        record_id=ev.id,
        values={},
        lines=_lines_payload(ev, {line.module_code: {"level": "none"}}),
    )
    assert not res.get("error"), res
    assert line.level == "none" and not line.can_print, "No access clears the switches"
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert not got.get("error"), got
    user = emp.user_id
    perm = c.env["fix.module.permission"].sudo().search([("user_id", "=", user.id)])
    assert perm.mapped("module_code") == [line.module_code], "only narrowed modules are stored"
    assert "1 module(s) narrowed" in ev.result_note
    # the workspace refuses the denied module for this person ...
    res = p03.records(user, model=model, cols=["id"], domain=[])
    assert res.get("error") and "does not include viewing" in res["error"]
    # ... and not for anyone else
    res = p03.records(probe_user, model=model, cols=["id"], domain=[])
    assert not res.get("error"), res


def test_view_only_blocks_saves_and_actions_but_not_reading(c, p03):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    user = _user(c.env, "m29cap_viewonly")
    cat = _catalogue()
    code = next(code for code, ms in cat.items() if "fix.vulnerability" in ms)
    c.env["fix.module.permission"].sudo().create(
        {
            "user_id": user.id,
            "module_code": code,
            "module_name": code,
            "level": "view",
            "can_print": False,
            "can_export": True,
            "can_email": False,
        }
    )
    env = c.env(user=user.id)
    assert g._gate(env, "view", model="fix.vulnerability") is None
    assert g._gate(env, "export", module=code) is None
    for need in ("create", "edit", "approve", "print", "email"):
        assert g._gate(env, need, model="fix.vulnerability"), need
    res = p03.write(
        user,
        model="fix.vulnerability",
        values={"title": "x", "severity": "low", "source": "sast", "component": "y"},
    )
    assert res.get("error") and "creating records" in res["error"]
    assert not p03.records(user, model="fix.vulnerability", cols=["name"], domain=[]).get("error")


def test_a_mover_replaces_the_previous_narrowing(c, p03):
    main, extra = _roles(c)
    emp = _newcomer(c, email="m29cap.mover@1000fix.test", code="M29CAP-MOV")
    ev = _file_provision(c, p03, emp, main, [extra])
    first = ev.permission_line_ids[:1]
    p03.write(
        c.appr1,
        model="fix.jml.event",
        record_id=ev.id,
        values={},
        lines=_lines_payload(ev, {first.module_code: {"level": "none"}}),
    )
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert not got.get("error"), got
    user = emp.user_id
    assert c.env["fix.module.permission"].sudo().search_count([("user_id", "=", user.id)]) == 1
    res = p03.write(
        c.appr1,
        model="fix.jml.event",
        values={
            "event_type": "mover",
            "employee_id": emp.id,
            "role_id": main.id,
            "effective_on": str(c.today),
        },
    )
    assert not res.get("error"), res
    mover = c.env["fix.jml.event"].sudo().browse(res["id"])
    assert all(not ln._fix_narrowed() for ln in mover.permission_line_ids)
    got = p03.action(c.appr2, model="fix.jml.event", record_id=mover.id, method="action_apply")
    assert not got.get("error"), got
    assert not c.env["fix.module.permission"].sudo().search_count([("user_id", "=", user.id)])


def test_language_time_zone_and_end_date_are_applied_and_expiry_deprovisions(c, p03):
    main, _extra = _roles(c)
    emp = _newcomer(c, email="m29cap.temp@1000fix.test", code="M29CAP-TMP")
    ev = _file_provision(c, p03, emp, main)
    langs = dict(c.env["res.lang"].get_installed())
    lang = "en_US" if "en_US" in langs else next(iter(langs))
    res = p03.write(
        c.appr1,
        model="fix.jml.event",
        record_id=ev.id,
        values={
            "lang": lang,
            "tz": "Asia/Dhaka",
            "valid_until": str(c.today + datetime.timedelta(days=30)),
            "reason": "Six-month contract to clear the service-centre backlog",
        },
    )
    assert not res.get("error"), res
    got = p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply")
    assert not got.get("error"), got
    user = emp.user_id.sudo()
    assert user.lang == lang and user.tz == "Asia/Dhaka"
    assert user.fix_access_expires_on == c.today + datetime.timedelta(days=30)
    assert "access ends" in ev.result_note
    Jml = c.env["fix.jml.event"]
    Jml._cron_expire_access()
    assert user.active, "not before the end date"
    user.write({"fix_access_expires_on": c.today - datetime.timedelta(days=1)})
    assert Jml._cron_expire_access() >= 1
    assert not user.active and not user.group_ids


def test_employee_details_show_on_the_form(c, p03):
    emp = _newcomer(c, email="m29cap.card@1000fix.test", code="M29CAP-CARD")
    main, _extra = _roles(c)
    ev = _file_provision(c, p03, emp, main)
    assert ev.emp_code == "M29CAP-CARD"
    assert ev.proposed_login == "m29cap.card@1000fix.test"


def test_the_one_click_preset_sets_every_module_within_the_roles(c, p03):
    main, extra = _roles(c)
    emp = _newcomer(c, email="m29cap.bulk@1000fix.test", code="M29CAP-BULK")
    ev = _file_provision(c, p03, emp, main, [extra])
    res = p03.write(
        c.appr1, model="fix.jml.event", record_id=ev.id, values={"permission_bulk": "view"}
    )
    assert not res.get("error"), res
    assert not ev.permission_bulk, "the preset is an instruction, not a state"
    assert set(ev.permission_line_ids.mapped("level")) == {"view"}
    assert not any(ev.permission_line_ids.mapped("can_approve"))
    res = p03.write(
        c.appr1, model="fix.jml.event", record_id=ev.id, values={"permission_bulk": "none"}
    )
    assert not res.get("error"), res
    assert set(ev.permission_line_ids.mapped("level")) == {"none"}
    assert not any(ev.permission_line_ids.mapped("can_print"))
    res = p03.write(
        c.appr1, model="fix.jml.event", record_id=ev.id, values={"permission_bulk": "roles"}
    )
    assert not res.get("error"), res
    for line in ev.permission_line_ids:
        assert line.level == line.allowed_level and not line._fix_narrowed()
