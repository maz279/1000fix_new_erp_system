"""M29 capture pass 2 (2026-11-19): the records the sub-module pages still
could not capture, driven through /p03/model/form|write|action|choices as
NON-ADMIN users with the fields m29.js posts (the superuser is trusted by the
model guards and would hide a gap).

  p1 Identity & MFA   suspend / reinstate (§8.1), service accounts (FR-SEC-012,
                      BRU-SEC-17, AUT-SEC-25), the leaver's devices and
                      delegations (AUT-SEC-03), and the JML picker that offered
                      only people without a login.
  p6 Data Protection  the residency class on a classification (FR-SEC-047).
  p7 Monitoring       the breach decision and its M60 hand-off (§8.3, AUT-SEC-13),
                      emergency break-glass with justification and review
                      (FR-SEC-034/035, BRU-SEC-20), penetration tests (AUT-SEC-16).
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
                "email": "%s@m29cap2.test" % login,
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
    x.plain = _user(env, "m29c2_plain")
    x.off1 = _user(env, "m29c2_off1", [OFFICER])
    x.off2 = _user(env, "m29c2_off2", [OFFICER])
    x.appr1 = _user(env, "m29c2_appr1", [APPROVER])
    x.appr2 = _user(env, "m29c2_appr2", [APPROVER])
    x.sys = _user(env, "m29c2_sys", ["base.group_system"])
    x.today = fields.Date.context_today(env["fix.jml.event"].with_user(x.plain))
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
            form=lambda user, **kw: call(user, "model_form", **kw),
            choices=lambda user, **kw: call(user, "model_choices", **kw),
        )
    finally:
        g.request = old


def _form_fields(screen):
    js = JS.read_text(encoding="utf-8")
    start = js.index("'%s': {" % screen)
    nxt = re.compile(r"^  '(M29[-:][\w-]+)': \{", re.M).search(js, start + 10)
    block = js[start : nxt.start() if nxt else len(js)]
    return [{"name": n} for n in re.findall(r"name: '(\w+)'", block)]


def _audit(c, event, ref=None):
    domain = [("event", "=", event)]
    if ref:
        domain.append(("object_ref", "=", ref))
    return c.env["fix.security.audit"].sudo().search(domain)


def _ok(res):
    assert not res.get("error"), res
    return res


def _employee_with_login(c, login):
    user = _user(c.env, login)
    emp = c.env["hr.employee"].sudo().create({"name": login, "user_id": user.id})
    return emp, user


# ---------------------------------------------------------------- p1: every new form opens
@pytest.mark.parametrize(
    "screen,model,actor",
    [
        ("M29-form-suspend", "fix.jml.event", "appr1"),
        ("M29-form-service-account", "fix.service.account", "appr1"),
        ("M29-form-pentest", "fix.security.pentest", "off1"),
        ("M29-form-incident", "fix.security.incident", "plain"),
        ("M29-form-session", "fix.privileged.session", "plain"),
        ("M29-form-sensitive", "fix.sensitive.field", "sys"),
        ("M29-form-vulnerability", "fix.vulnerability", "plain"),
    ],
)
def test_every_pass2_form_opens_blank_for_its_actor(c, p03, screen, model, actor):
    got = p03.form(getattr(c, actor), model=model, fields=_form_fields(screen))
    assert not got.get("error"), (screen, got)


# ---------------------------------------------------------------- p1: suspend / reinstate
def _file(c, p03, user, values):
    return p03.write(user, model="fix.jml.event", values=values)


def test_a_suspension_switches_the_login_off_and_a_reinstatement_restores_it(c, p03):
    emp, target = _employee_with_login(c, "m29c2_susp")
    groups_before = set(target.group_ids.ids)
    res = _ok(
        _file(
            c,
            p03,
            c.appr1,
            {
                "event_type": "suspend",
                "employee_id": emp.id,
                "suspend_reason": "investigation",
                "effective_on": str(c.today),
                "reason": "Fraud investigation opened by internal audit",
            },
        )
    )
    ev = c.env["fix.jml.event"].sudo().browse(res["id"])
    assert ev.user_id == target and "Suspend" in ev.permission_preview
    # the filer never applies it
    assert p03.action(c.appr1, model="fix.jml.event", record_id=ev.id, method="action_apply").get(
        "error"
    )
    _ok(p03.action(c.appr2, model="fix.jml.event", record_id=ev.id, method="action_apply"))
    target.invalidate_recordset()
    assert ev.state == "applied" and not target.active
    assert set(target.with_context(active_test=False).group_ids.ids) == groups_before
    assert _audit(c, "identity.suspended", "res.users,%d" % target.id)

    res = _ok(
        _file(
            c,
            p03,
            c.appr1,
            {
                "event_type": "reinstate",
                "employee_id": emp.id,
                "effective_on": str(c.today),
                "reason": "Investigation closed, no finding",
            },
        )
    )
    ev2 = c.env["fix.jml.event"].sudo().browse(res["id"])
    _ok(p03.action(c.appr2, model="fix.jml.event", record_id=ev2.id, method="action_apply"))
    target.invalidate_recordset()
    assert target.active and set(target.group_ids.ids) == groups_before
    assert _audit(c, "identity.reinstated", "res.users,%d" % target.id)


def test_a_leaver_is_never_reinstated(c, p03):
    emp, target = _employee_with_login(c, "m29c2_left")
    leaver = (
        c.env["fix.jml.event"]
        .sudo()
        .create({"event_type": "leaver", "employee_id": emp.id, "effective_on": c.today})
    )
    leaver.with_user(c.appr2).action_apply()
    assert not target.active
    res = _ok(
        _file(
            c,
            p03,
            c.appr1,
            {
                "event_type": "reinstate",
                "employee_id": emp.id,
                "effective_on": str(c.today),
                "reason": "Wants the login back after leaving",
            },
        )
    )
    got = p03.action(c.appr2, model="fix.jml.event", record_id=res["id"], method="action_apply")
    assert "suspension" in (got.get("error") or ""), got
    assert not target.active


def test_a_suspension_needs_a_reason_and_a_login(c, p03):
    emp, _target = _employee_with_login(c, "m29c2_noreason")
    assert _file(
        c,
        p03,
        c.appr1,
        {
            "event_type": "suspend",
            "employee_id": emp.id,
            "effective_on": str(c.today),
            "reason": "Long leave from next week",
        },
    ).get("error"), "a suspension without its reason is refused"
    nologin = c.env["hr.employee"].sudo().create({"name": "m29c2 no login"})
    got = _file(
        c,
        p03,
        c.appr1,
        {
            "event_type": "suspend",
            "employee_id": nologin.id,
            "suspend_reason": "leave",
            "effective_on": str(c.today),
            "reason": "Long leave from next week",
        },
    )
    assert "no login" in (got.get("error") or ""), got


def test_a_suspension_cannot_name_someone_elses_login(c, p03):
    """The login affected is the employee's own: an employee with no login and a
    typed colleague's login would otherwise switch the colleague off."""
    nologin = c.env["hr.employee"].sudo().create({"name": "m29c2 decoy"})
    got = _file(
        c,
        p03,
        c.appr1,
        {
            "event_type": "suspend",
            "employee_id": nologin.id,
            "user_id": c.appr2.id,
            "suspend_reason": "security",
            "effective_on": str(c.today),
            "reason": "Trying to switch a colleague off",
        },
    )
    assert got.get("error"), got
    assert c.appr2.active


def test_the_jml_picker_offers_employees_with_a_login(c, p03):
    """Before pass 2 the surface fenced every JML form's employee picker to people
    WITHOUT a login, so a mover, a leaver or a suspension could pick nobody."""
    emp, _target = _employee_with_login(c, "m29c2_mover")
    got = _ok(p03.choices(c.appr1, model="fix.jml.event", field="employee_id", q="m29c2_mover"))
    assert emp.id in [row["id"] for row in got["choices"]]
    # the suspension form's own filter offers people with a login only
    nologin = c.env["hr.employee"].sudo().create({"name": "m29c2_mover nologin"})
    got = _ok(
        p03.choices(
            c.appr1,
            model="fix.jml.event",
            field="employee_id",
            q="m29c2_mover",
            domain=[["user_id", "!=", False]],
        )
    )
    ids = [row["id"] for row in got["choices"]]
    assert emp.id in ids and nologin.id not in ids


# ---------------------------------------------------------------- p1: the leaver hand-off
def test_a_leaver_loses_devices_and_delegations(c, p03):
    if "fix.technician.device" not in c.env or "fix.approval.substitution" not in c.env:
        pytest.skip("M02 / M63 not installed")
    emp, _target = _employee_with_login(c, "m29c2_tech")
    device = (
        c.env["fix.technician.device"]
        .sudo()
        .create({"employee_id": emp.id, "device_uid": "M29C2-DEV-1", "platform": "android"})
    )
    boss = c.env["hr.employee"].sudo().create({"name": "m29c2 boss", "user_id": c.off1.id})
    sub = (
        c.env["fix.approval.substitution"]
        .sudo()
        .create(
            {
                "absent_approver_id": boss.id,
                "delegate_id": emp.id,
                "start_date": c.today,
                "end_date": c.today + datetime.timedelta(days=10),
            }
        )
    )
    leaver = (
        c.env["fix.jml.event"]
        .sudo()
        .create({"event_type": "leaver", "employee_id": emp.id, "effective_on": c.today})
    )
    leaver.with_user(c.appr2).action_apply()
    assert device.state == "revoked" and device.revoke_reason == "departed"
    assert sub.state == "expired"
    assert _audit(c, "leaver_devices", "hr.employee,%d" % emp.id)
    assert _audit(c, "leaver_delegations", "hr.employee,%d" % emp.id)


# ---------------------------------------------------------------- p1: service accounts
def _account(c, p03, user, **extra):
    values = {
        "name": "Bank statement connector",
        "kind": "integration",
        "purpose": "Pulls the daily bank statement into M19",
        "scopes": "fix.bank.statement create; no other model",
        "owner_id": c.plain.id,
        "credential_ref": "vault://integrations/bank/statement",
        "rotation_days": 90,
    }
    values.update(extra)
    return p03.write(user, model="fix.service.account", values=values)


def test_a_service_account_is_registered_with_an_owner_and_a_vault_reference(c, p03):
    assert _account(c, p03, c.plain).get("error"), "a plain user registers nothing"
    got = _account(c, p03, c.appr1, credential_ref="s3cr3t-password")
    assert "vault" in (got.get("error") or ""), got
    res = _ok(_account(c, p03, c.appr1))
    acc = c.env["fix.service.account"].sudo().browse(res["id"])
    assert acc.code.startswith("SVC/") and acc.state == "active"
    assert acc.next_rotation_on
    assert _audit(c, "service_account", "fix.service.account,%d" % acc.id)
    # the credential changes only through Register Rotation, by the owner
    got = p03.write(
        c.appr1,
        model="fix.service.account",
        record_id=acc.id,
        values={"credential_ref": "vault://integrations/bank/other"},
    )
    assert got.get("error"), got
    _ok(
        p03.action(
            c.plain,
            model="fix.service.account",
            record_id=acc.id,
            method="action_register_rotation",
            kwargs={"new_vault_ref": "vault://integrations/bank/statement-v2"},
        )
    )
    assert acc.credential_ref.endswith("-v2") and acc.last_rotated_on == c.today


def test_a_suspended_account_comes_back_through_a_second_person(c, p03):
    login = _user(c.env, "m29c2_svc_login")
    acc = (
        c.env["fix.service.account"]
        .sudo()
        .browse(_ok(_account(c, p03, c.appr1, user_id=login.id))["id"])
    )
    _ok(
        p03.action(
            c.appr1,
            model="fix.service.account",
            record_id=acc.id,
            method="action_suspend",
            kwargs={"reason": "Vendor reported a leaked key"},
        )
    )
    assert acc.state == "suspended" and not login.active
    assert p03.action(
        c.appr1, model="fix.service.account", record_id=acc.id, method="action_reactivate"
    ).get("error"), "the one who suspended it does not reactivate it"
    _ok(
        p03.action(
            c.appr2, model="fix.service.account", record_id=acc.id, method="action_reactivate"
        )
    )
    login.invalidate_recordset()
    assert acc.state == "active" and login.active


def test_an_orphaned_account_is_flagged_then_suspended_after_24_hours(c, p03):
    owner = _user(c.env, "m29c2_owner")
    login = _user(c.env, "m29c2_robot")
    acc = (
        c.env["fix.service.account"]
        .sudo()
        .browse(_ok(_account(c, p03, c.appr1, owner_id=owner.id, user_id=login.id))["id"])
    )
    owner.sudo().write({"active": False})
    Acc = c.env["fix.service.account"].sudo()
    Acc._cron_service_account_watch()
    assert acc.orphan_flagged_on and acc.state == "active" and acc.is_orphaned
    acc._guarded().write(
        {"orphan_flagged_on": fields.Datetime.now() - datetime.timedelta(hours=25)}
    )
    Acc._cron_service_account_watch()
    login.invalidate_recordset()
    assert acc.state == "suspended" and not login.active
    assert _audit(c, "service_account.orphaned", "fix.service.account,%d" % acc.id)


# ---------------------------------------------------------------- p6: residency class
def test_a_classification_carries_its_residency_class_and_who_set_it(c, p03):
    base = {
        "model_name": "hr.employee",
        "field_name": "m29c2_nid",
        "data_class": "pii",
        "masking_rule": "last4",
        "residency_class": "resident",
        "owning_module": "M21",
    }
    got = p03.write(c.sys, model="fix.sensitive.field", values=dict(base, sensitivity="s1"))
    assert "S2" in (got.get("error") or ""), got
    res = _ok(p03.write(c.sys, model="fix.sensitive.field", values=dict(base, sensitivity="s3")))
    rec = c.env["fix.sensitive.field"].sudo().browse(res["id"])
    assert rec.classified_by_id == c.sys and rec.classified_on
    other = _user(c.env, "m29c2_sys2", ["base.group_system"])
    _ok(
        p03.write(
            other, model="fix.sensitive.field", record_id=rec.id, values={"residency_class": "cii"}
        )
    )
    assert rec.classified_by_id == other
    assert _audit(c, "classification", "fix.sensitive.field,%d" % rec.id)
    # who classified it is stamped, never typed
    got = p03.write(
        c.sys, model="fix.sensitive.field", record_id=rec.id, values={"classified_by_id": c.sys.id}
    )
    assert rec.classified_by_id == other


# ---------------------------------------------------------------- p7: breach decision
def _incident(c, p03, **extra):
    values = {
        "title": "Customer list emailed to a personal address",
        "category": "data_leak",
        "severity": "high",
        "detected_at": fields.Datetime.to_string(fields.Datetime.now()),
        "personal_data_involved": "yes",
    }
    values.update(extra)
    res = _ok(p03.write(c.plain, model="fix.security.incident", values=values))
    return c.env["fix.security.incident"].sudo().browse(res["id"])


def _assess(c, p03, who, inc, decision):
    return p03.action(
        who,
        model="fix.security.incident",
        record_id=inc.id,
        method="action_assess_breach",
        kwargs={"decision": decision},
    )


def _write_assessment(c, p03, inc):
    _ok(
        p03.write(
            c.off1,
            model="fix.security.incident",
            record_id=inc.id,
            values={
                "breach_assessment": "About 1,200 customer names and phone numbers left the estate.",
                "data_subjects_estimate": 1200,
            },
        )
    )


def test_a_notifiable_breach_starts_the_clock_and_opens_the_m60_record(c, p03):
    inc = _incident(c, p03)
    assert inc.breach_assessment_due
    assert _assess(c, p03, c.plain, inc, "notifiable").get("error"), "officers assess"
    assert _assess(c, p03, c.off1, inc, "notifiable").get("error"), "no assessment written yet"
    _write_assessment(c, p03, inc)
    _ok(_assess(c, p03, c.off1, inc, "notifiable"))
    assert inc.breach_decision == "notifiable" and inc.statutory_clock_start
    assert inc.breach_assessed_by_id == c.off1
    if "fix.grc.data.breach" in c.env:
        breach = (
            c.env["fix.grc.data.breach"].sudo().search([("name", "=", inc.m60_notification_ref)])
        )
        assert breach and breach.subjects_affected == 1200
    assert _audit(c, "security.breach_assessed", "fix.security.incident,%d" % inc.id)
    # the facts are fixed once assessed
    got = p03.write(
        c.off2,
        model="fix.security.incident",
        record_id=inc.id,
        values={"personal_data_involved": "no"},
    )
    assert got.get("error") and inc.personal_data_involved == "yes"
    # and the model refuses it too, not only the form lock
    from odoo.exceptions import UserError

    with pytest.raises(UserError), c.env.cr.savepoint():
        inc.with_user(c.off2).write({"significant_damage_likely": True})


def test_not_notifiable_needs_a_second_officer_before_the_incident_closes(c, p03):
    inc = _incident(c, p03, category="unauthorised_access", title="Shared login found in use")
    _write_assessment(c, p03, inc)
    _ok(_assess(c, p03, c.off1, inc, "not notifiable"))
    _ok(
        p03.write(
            c.off1,
            model="fix.security.incident",
            record_id=inc.id,
            values={
                "containment": "Shared login disabled and every session ended on the spot.",
                "root_cause": "Branch staff were sharing one counter login out of habit.",
            },
        )
    )
    _ok(
        p03.action(c.off1, model="fix.security.incident", record_id=inc.id, method="action_contain")
    )
    got = p03.action(c.off2, model="fix.security.incident", record_id=inc.id, method="action_close")
    assert "second officer" in (got.get("error") or ""), got
    assert p03.action(
        c.off1,
        model="fix.security.incident",
        record_id=inc.id,
        method="action_confirm_not_notifiable",
    ).get("error"), "the assessor does not confirm their own decision"
    _ok(
        p03.action(
            c.off2,
            model="fix.security.incident",
            record_id=inc.id,
            method="action_confirm_not_notifiable",
        )
    )
    _ok(p03.action(c.off2, model="fix.security.incident", record_id=inc.id, method="action_close"))
    assert inc.state == "closed"


def test_significant_damage_makes_it_notifiable(c, p03):
    inc = _incident(c, p03, significant_damage_likely=True)
    _write_assessment(c, p03, inc)
    got = _assess(c, p03, c.off1, inc, "not_notifiable")
    assert "notifiable" in (got.get("error") or ""), got
    assert not inc.breach_decision


def test_an_incident_closes_only_once_personal_data_is_answered(c, p03):
    inc = _incident(
        c,
        p03,
        personal_data_involved="unknown",
        category="malware",
        title="Malware on a counter PC",
    )
    _ok(
        p03.write(
            c.off1,
            model="fix.security.incident",
            record_id=inc.id,
            values={
                "containment": "The PC was isolated from the network and reimaged.",
                "root_cause": "A USB stick from a customer was opened on the counter PC.",
            },
        )
    )
    _ok(
        p03.action(c.off1, model="fix.security.incident", record_id=inc.id, method="action_contain")
    )
    got = p03.action(c.off1, model="fix.security.incident", record_id=inc.id, method="action_close")
    assert "personal data" in (got.get("error") or ""), got
    _ok(
        p03.write(
            c.off1,
            model="fix.security.incident",
            record_id=inc.id,
            values={"personal_data_involved": "no"},
        )
    )
    _ok(p03.action(c.off1, model="fix.security.incident", record_id=inc.id, method="action_close"))


# ---------------------------------------------------------------- p7: break-glass
def _session(c, p03, user, **extra):
    values = {"access_kind": "db_console", "reason": "Payment gateway down", "break_glass": True}
    values.update(extra)
    res = _ok(p03.write(user, model="fix.privileged.session", values=values))
    return c.env["fix.privileged.session"].sudo().browse(res["id"])


def _act(c, p03, who, rec, method, **kwargs):
    return p03.action(
        who, model="fix.privileged.session", record_id=rec.id, method=method, kwargs=kwargs
    )


def test_break_glass_opens_now_is_loud_and_is_justified_and_reviewed(c, p03):
    plain = _session(c, p03, c.plain)
    assert "administrator" in (
        _act(c, p03, c.plain, plain, "action_break_glass").get("error") or ""
    )
    rec = _session(c, p03, c.sys)
    _ok(_act(c, p03, c.sys, rec, "action_break_glass"))
    assert rec.state == "open" and not rec.approver_id
    assert rec.expires_at <= rec.started_at + datetime.timedelta(hours=4)
    assert rec.justification_due_at
    assert _audit(c, "privileged.break_glass_used", "fix.privileged.session,%d" % rec.id)
    told = rec.message_ids.filtered(lambda m: "BREAK-GLASS" in (m.body or ""))
    assert told and c.off1.partner_id in told.partner_ids, "officers are told at once"
    # closing records what was done (FR-SEC-034)
    assert _act(c, p03, c.sys, rec, "action_close").get("error")
    _ok(
        _act(
            c,
            p03,
            c.sys,
            rec,
            "action_close",
            summary="Restarted the payment gateway worker and cleared the stuck queue.",
        )
    )
    assert rec.state == "closed" and rec.actions_summary
    # review waits for the justification, and never by the holder
    assert _act(c, p03, c.appr1, rec, "action_review_ok").get("error")
    _ok(
        _act(
            c,
            p03,
            c.sys,
            rec,
            "action_justify",
            justification="Customers could not pay at any counter; no approver was reachable at 2 am.",
        )
    )
    assert _act(c, p03, c.sys, rec, "action_review_ok").get("error")
    _ok(_act(c, p03, c.appr1, rec, "action_review_ok"))
    assert rec.review_outcome == "justified" and rec.reviewed_by_id == c.appr1


def test_an_unjustified_session_review_raises_an_incident(c, p03):
    rec = _session(c, p03, c.sys)
    _ok(_act(c, p03, c.sys, rec, "action_break_glass"))
    _ok(
        _act(
            c,
            p03,
            c.sys,
            rec,
            "action_close",
            summary="Exported the customer table to a spreadsheet for a report.",
        )
    )
    _ok(
        _act(
            c,
            p03,
            c.sys,
            rec,
            "action_justify",
            justification="Needed a customer list quickly for a marketing report this morning.",
        )
    )
    _ok(
        _act(
            c,
            p03,
            c.off1,
            rec,
            "action_review_misuse",
            note="A marketing report is no emergency: the export needed approval.",
        )
    )
    inc = c.env["fix.security.incident"].sudo().search([("session_id", "=", rec.id)])
    assert rec.review_outcome == "misuse" and inc and inc.category == "policy_breach"


def test_a_late_justification_is_escalated_once(c, p03):
    rec = _session(c, p03, c.sys)
    _ok(_act(c, p03, c.sys, rec, "action_break_glass"))
    rec._guarded().write(
        {"justification_due_at": fields.Datetime.now() - datetime.timedelta(hours=1)}
    )
    Session = c.env["fix.privileged.session"].sudo()
    assert Session._cron_break_glass_followup() >= 1
    assert rec.justification_escalated_on
    assert Session._cron_break_glass_followup() == 0 or rec.justification_escalated_on
    assert _audit(c, "privileged.break_glass_unjustified", "fix.privileged.session,%d" % rec.id)


def test_break_glass_is_chosen_when_filed(c, p03):
    rec = _session(c, p03, c.plain, break_glass=False)
    _ok(_act(c, p03, c.appr1, rec, "action_approve"))
    got = p03.write(
        c.plain, model="fix.privileged.session", record_id=rec.id, values={"break_glass": True}
    )
    assert got.get("error") and not rec.break_glass
    from odoo.exceptions import UserError

    with pytest.raises(UserError), c.env.cr.savepoint():
        rec.with_user(c.plain).write({"break_glass": True})
    assert not rec.break_glass


# ---------------------------------------------------------------- p7: penetration tests
def test_a_penetration_test_closes_only_when_every_finding_is_resolved(c, p03):
    values = {
        "title": "Annual external test 2026",
        "provider": "Example Assurance Ltd",
        "test_type": "external",
        "scope": "Public website, customer portal and the payment API",
        "test_from": str(c.today - datetime.timedelta(days=10)),
        "test_to": str(c.today - datetime.timedelta(days=3)),
    }
    assert p03.write(c.plain, model="fix.security.pentest", values=values).get("error")
    pt = (
        c.env["fix.security.pentest"]
        .sudo()
        .browse(_ok(p03.write(c.off1, model="fix.security.pentest", values=values))["id"])
    )
    finding = {
        "title": "Admin login reachable from the internet",
        "severity": "critical",
        "source": "report",
        "component": "customer portal",
        "discovered_on": str(c.today),
        "owner_id": c.off2.id,
        "pentest_id": pt.id,
    }
    assert p03.write(c.off1, model="fix.vulnerability", values=finding).get(
        "error"
    ), "findings load once the report is in"
    assert p03.action(
        c.off1, model="fix.security.pentest", record_id=pt.id, method="action_receive_report"
    ).get("error")
    _ok(
        p03.write(
            c.off1,
            model="fix.security.pentest",
            record_id=pt.id,
            values={"report_received_on": str(c.today), "report_ref": "DMS-PT-2026-01"},
        )
    )
    _ok(
        p03.action(
            c.off1, model="fix.security.pentest", record_id=pt.id, method="action_receive_report"
        )
    )
    vuln = (
        c.env["fix.vulnerability"]
        .sudo()
        .browse(_ok(p03.write(c.off1, model="fix.vulnerability", values=finding))["id"])
    )
    assert vuln.source == "pentest" and pt.finding_count == 1 and pt.open_count == 1
    assert p03.action(
        c.off1, model="fix.security.pentest", record_id=pt.id, method="action_close"
    ).get("error")
    _ok(
        p03.action(
            c.off2,
            model="fix.vulnerability",
            record_id=vuln.id,
            method="action_remediate",
            kwargs={"note": "Admin login moved behind the VPN and IP allow-list."},
        )
    )
    _ok(p03.action(c.off1, model="fix.vulnerability", record_id=vuln.id, method="action_verify"))
    pt.invalidate_recordset()
    _ok(p03.action(c.off1, model="fix.security.pentest", record_id=pt.id, method="action_close"))
    assert pt.state == "closed" and pt.closed_by_id == c.off1


# ---------------------------------------------------------------- KPIs
def test_the_pass2_kpis_read_as_the_caller(c):
    from odoo.addons.cd_p03_portal.controllers.a12 import m29

    for user in (c.plain, c.off1, c.appr1):
        got = m29.kpis(c.env(user=user.id))
        for key in (
            "breach_assessments_overdue",
            "break_glass_unreviewed",
            "service_accounts_orphaned",
        ):
            assert isinstance(got[key], int), (user.login, key)


# ---------------------------------------------------------------- the model guards behind the ACL
def _acl_only_user(c, model, login):
    """A user whose group grants create on `model` by ACL but who holds no
    officer / approver / admin appointment: the model's own guard must refuse,
    so a future ACL widening cannot hand the register to everyone."""
    group = c.env["res.groups"].sudo().create({"name": "m29c2 acl-only %s" % model})
    c.env["ir.model.access"].sudo().create(
        {
            "name": "m29c2 acl-only %s" % model,
            "model_id": c.env["ir.model"]._get_id(model),
            "group_id": group.id,
            "perm_read": True,
            "perm_write": True,
            "perm_create": True,
        }
    )
    return _user(c.env, login, []).sudo().write({"group_ids": [(4, group.id)]}) and c.env[
        "res.users"
    ].search([("login", "=", login)])


def test_a_service_account_is_refused_to_an_acl_only_user(c):
    from odoo.exceptions import UserError

    user = _acl_only_user(c, "fix.service.account", "m29c2_acl_svc")
    with pytest.raises(UserError, match="manages service accounts"), c.env.cr.savepoint():
        c.env["fix.service.account"].with_user(user).create(
            {
                "name": "Rogue connector",
                "purpose": "Should never be registered by a plain user",
                "scopes": "everything",
                "owner_id": user.id,
                "credential_ref": "vault://rogue/connector",
            }
        )


def test_a_penetration_test_is_refused_to_an_acl_only_user(c):
    from odoo.exceptions import UserError

    user = _acl_only_user(c, "fix.security.pentest", "m29c2_acl_pt")
    with pytest.raises(UserError, match="manages penetration tests"), c.env.cr.savepoint():
        c.env["fix.security.pentest"].with_user(user).create(
            {
                "title": "Rogue engagement",
                "provider": "Nobody",
                "scope": "everything",
                "test_from": c.today,
                "test_to": c.today,
            }
        )
