"""A12 finish build: M66 (ITSM), proven as real role-holding NON-admin users through
the same controller the workspace calls, with the kwargs the JS sends.

Source: working/A12_evidence/finish/m28_m66/FINDINGS.md and the probes beside it.
Hand-offs run through the real publisher and cron_relay, never a hand-made payload.
"""

from __future__ import annotations

import inspect
import re
import types
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
AGENT = "cd_itsm.group_itsm_agent"
CM = "cd_itsm.group_itsm_change_manager"
CAB = "cd_itsm.group_itsm_cab_member"


def _user(env, login, groups=(), ou=None, employee=True):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = ou or env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    emp = env["hr.employee"].create({"name": login, "user_id": user.id}) if employee else None
    return user, emp


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.itsm.change"])
    x.plain, x.plain_e = _user(env, "m66f_plain")
    x.plain2, x.plain2_e = _user(env, "m66f_plain2")
    x.agent, x.agent_e = _user(env, "m66f_agent", [AGENT])
    x.agent2, x.agent2_e = _user(env, "m66f_agent2", [AGENT])
    x.cm, x.cm_e = _user(env, "m66f_cm", [CM])
    x.cm2, x.cm2_e = _user(env, "m66f_cm2", [CM])
    x.cab, x.cab_e = _user(env, "m66f_cab", [CAB])
    x.cab2, x.cab2_e = _user(env, "m66f_cab2", [CAB])
    env["ir.config_parameter"].sudo().set_param("cd_itsm.change_freeze_windows", False)
    return x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.a12 as a12mod
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    klass = g.P03GenericApiController

    def _orig(fn):
        return getattr(fn, "original_endpoint", fn)

    write, action, records, form = (
        _orig(klass.model_write),
        _orig(klass.model_action),
        _orig(klass.model_records),
        _orig(klass.model_form),
    )
    saved = (g.request, s.request, a12mod.request)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        a12mod.request = req

    as_user(c.plain)
    try:
        yield types.SimpleNamespace(
            write=lambda **k: write(ctl, **k),
            action=lambda **k: action(ctl, **k),
            records=lambda **k: records(ctl, **k),
            form=lambda **k: form(ctl, **k),
            as_user=as_user,
        )
    finally:
        g.request, s.request, a12mod.request = saved


def refused(env, fn):
    """Run fn in a savepoint: the refusal text, or None if it succeeded."""
    try:
        with env.cr.savepoint():
            fn()
        return None
    except REFUSED as exc:
        return str(exc)


def ticket(c, user=None, **kw):
    vals = {
        "title": "Laptop dead",
        "requester_id": c.plain_e.id,
        "category": "hardware",
        "priority": "medium",
        "description": "Black screen",
    }
    vals.update(kw)
    return c.env["fix.itsm.ticket"].with_user(user or c.agent).create(vals)


def working(c, user=None, **kw):
    t = ticket(c, **kw)
    t.with_user(user or c.agent).action_assign()
    return t


def overdue(c, rec, hours=2):
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_itsm_ticket SET sla_deadline = now() AT TIME ZONE 'UTC' - (%s || ' hours')::interval "
        "WHERE id = %s",
        (str(hours), rec.id),
    )
    rec.invalidate_recordset()


def change(c, user=None, **kw):
    vals = {
        "title": "Switch firmware",
        "change_type": "normal",
        "risk": "medium",
        "risk_probability": "2",
        "risk_impact": "2",
        "requested_by_id": c.agent_e.id,
        "planned_on": c.today + timedelta(days=1),
        "implementation_plan": "Flash stack A then B",
        "test_plan": "Ping sweep",
        "rollback_plan": "Boot previous image",
        "change_window_hours": 2,
    }
    vals.update(kw)
    return c.env["fix.itsm.change"].with_user(user or c.agent).create(vals)


def decide(ch, approver, comment="ok"):
    tasks = ch.sudo().approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert tasks, "no inbox task for %s on %s" % (approver.login, ch.name)
    tasks.with_user(approver).action_approve(comment=comment)


def approved_change(c, approver=None, user=None, **kw):
    ch = change(c, user=user, **kw)
    ch.with_user(user or c.agent).action_submit()
    if ch.state != "approved":
        decide(ch, approver or c.cm)
    assert ch.state == "approved"
    return ch


def template(c, **kw):
    vals = {
        "code": "STD-LOG-%d" % c.env["fix.itsm.change.template"].search_count([]),
        "name": "Rotate a log file",
        "implementation_plan": "Rotate the log",
        "test_plan": "Tail the new log",
        "rollback_plan": "Restore the previous log",
        "risk_probability": "1",
        "risk_impact": "2",
        "max_window_hours": 2,
    }
    vals.update(kw)
    tpl = c.env["fix.itsm.change.template"].with_user(c.agent).create(vals)
    tpl.with_user(c.cm).action_authorise()
    return tpl


def asset(c, **kw):
    vals = {
        "name": "Laptop",
        "asset_tag": "M66F-%s" % c.env["ir.sequence"].next_by_code("fix.itsm.ticket"),
    }
    vals.update(kw)
    return c.env["fix.itsm.asset"].with_user(c.agent).create(vals)


def allocated(c, employee=None):
    a = asset(c)
    a.with_user(c.agent).action_allocate(assigned_to=(employee or c.plain_e).id)
    return a


def retired(c, a):
    a.with_user(c.agent).action_retire(wipe_certificate="WIPE-2026-9")
    a.with_user(c.cm).action_approve_writeoff()
    return a


def licence(c, **kw):
    vals = {"name": "Office", "vendor": "V", "seats_owned": 2}
    vals.update(kw)
    return c.env["fix.itsm.licence"].with_user(c.agent).create(vals)


# ============================================================ N-M66-1, M66-5, N-M66-4
def test_a12f_n_m66_1_employee_raises_a_ticket_through_the_screen(c, p03):
    p03.as_user(c.plain)
    out = p03.write(
        model="fix.itsm.ticket",
        values={"title": "My laptop", "category": "hardware", "description": "Dead"},
    )
    assert "error" not in out, out
    t = c.env["fix.itsm.ticket"].browse(out["id"])
    assert t.requester_id == c.plain_e
    assert t.state == "new"
    assert "New" not in t.name


def test_a12f_n_m66_1_requester_is_forced_to_the_caller(c, p03):
    p03.as_user(c.plain)
    out = p03.write(
        model="fix.itsm.ticket",
        values={
            "title": "On behalf",
            "category": "other",
            "description": "x",
            "requester_id": c.plain2_e.id,
            "priority": "urgent",
        },
    )
    assert "error" not in out, out
    t = c.env["fix.itsm.ticket"].browse(out["id"])
    assert t.requester_id == c.plain_e, "an employee raised a ticket in another's name"
    assert t.priority == "medium", "an employee typed his own ticket to urgent"
    # By ORM too, past the screen.
    direct = (
        c.env["fix.itsm.ticket"]
        .with_user(c.plain)
        .create({"title": "D", "description": "d", "requester_id": c.plain2_e.id})
    )
    assert direct.requester_id == c.plain_e


def test_a12f_n_m66_1_employee_states_impact_and_urgency(c, p03):
    p03.as_user(c.plain)
    out = p03.write(
        model="fix.itsm.ticket",
        values={"title": "T", "description": "d", "impact": "high", "urgency": "high"},
    )
    assert c.env["fix.itsm.ticket"].browse(out["id"]).priority == "urgent"


def test_a12f_n_m66_1_user_with_no_employee_gets_a_clear_message(c, p03):
    user, _ = _user(c.env, "m66f_noemp", employee=False)
    p03.as_user(user)
    out = p03.write(model="fix.itsm.ticket", values={"title": "T", "description": "d"})
    assert "not linked to an employee" in out.get("error", ""), out


def test_a12f_n_m66_1_form_offers_no_requester_input_to_an_employee(c, p03):
    p03.as_user(c.plain)
    out = p03.form(model="fix.itsm.ticket", fields=[{"name": "requester_id"}, {"name": "title"}])
    meta = {f["name"]: f for f in out["fields"]}
    assert meta["requester_id"]["readonly"] is True
    assert meta["title"]["readonly"] is False


def test_a12f_n_m66_4_requester_closes_and_reopens_through_the_screen(c, p03):
    t = working(c)
    t.with_user(c.agent).action_resolve(resolution="Replaced PSU")
    p03.as_user(c.plain)
    out = p03.action(
        model="fix.itsm.ticket", ids=[t.id], method="action_reopen", kwargs={"reason": "Still dead"}
    )
    assert out.get("success"), out
    assert t.state == "in_progress" and t.reopen_count == 1 and not t.resolution
    t.with_user(c.agent).action_resolve(resolution="Replaced board")
    out = p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_close")
    assert out.get("success"), out
    assert t.state == "closed" and t.closed_on


def test_a12f_m66_8_a_stranger_neither_closes_nor_reopens(c):
    t = working(c)
    t.with_user(c.agent).action_resolve(resolution="done")
    # A stranger does not even read it; the method's own check stands behind the rule.
    assert refused(c.env, lambda: t.with_user(c.plain2).action_close())
    assert refused(c.env, lambda: t.with_user(c.plain2).action_reopen(reason="no"))


def test_a12f_m66_8_reopen_window_is_a_parameter(c):
    t = working(c)
    t.with_user(c.agent).action_resolve(resolution="done")
    assert refused(c.env, lambda: t.with_user(c.plain).action_reopen())  # no reason
    t.sudo()._guarded().write({"resolved_on": fields.Datetime.now() - timedelta(days=8)})
    assert "window" in refused(c.env, lambda: t.with_user(c.plain).action_reopen(reason="no"))
    c.env["ir.config_parameter"].sudo().set_param("cd_itsm.ticket_reopen_days", "30")
    t.with_user(c.plain).action_reopen(reason="back")
    assert t.state == "in_progress"


def test_a12f_m66_8_cron_auto_closes_after_the_window(c):
    young, old = working(c), working(c)
    for t in young | old:
        t.with_user(c.agent).action_resolve(resolution="done")
    old.sudo()._guarded().write({"resolved_on": fields.Datetime.now() - timedelta(days=8)})
    c.env["fix.itsm.ticket"].sudo().cron_ticket_housekeeping()
    assert old.state == "closed" and young.state == "resolved"
    assert c.env.ref("cd_itsm.ir_cron_itsm_ticket_housekeeping").active


def test_a12f_m66_14_ticket_numbers_are_real_and_unique(c):
    a, b = ticket(c), ticket(c)
    assert a.name != b.name
    assert "New" not in a.name and "New" not in b.name


# ============================================================ N-M66-5 dispatch
def test_a12f_n_m66_5_lead_dispatches_with_the_kwargs_the_screen_sends(c, p03):
    t = ticket(c)
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.ticket",
        ids=[t.id],
        method="action_assign",
        kwargs={"assigned_to": str(c.agent2_e.id)},
    )
    assert out.get("success"), out
    assert t.assigned_to == c.agent2_e and t.assigned_user_id == c.agent2 and t.state == "assigned"
    assert t.sudo().activity_ids.filtered(lambda a: a.user_id == c.agent2)


def test_a12f_n_m66_5_assign_accepts_an_id_a_name_and_blank(c, p03):
    p03.as_user(c.agent)
    by_id, by_name, blank = ticket(c), ticket(c), ticket(c)
    for rec, value, who in (
        (by_id, c.agent2_e.id, c.agent2_e),
        (by_name, c.agent2_e.name, c.agent2_e),
        (blank, "", c.agent_e),
    ):
        out = p03.action(
            model="fix.itsm.ticket",
            ids=[rec.id],
            method="action_assign",
            kwargs={"assigned_to": value},
        )
        assert out.get("success"), out
        assert rec.assigned_to == who


def test_a12f_n_m66_5_unknown_agent_is_a_clear_refusal(c, p03):
    t = ticket(c)
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.ticket",
        ids=[t.id],
        method="action_assign",
        kwargs={"assigned_to": "nobody-x"},
    )
    assert not out["success"] and "No employee matches" in out["error"]
    out = p03.action(
        model="fix.itsm.ticket",
        ids=[t.id],
        method="action_assign",
        kwargs={"assigned_to": c.plain2_e.id},
    )
    assert not out["success"] and "ITSM Agent" in out["error"]


def test_a12f_n_m66_5_assignee_is_not_typed_on_the_form(c, p03):
    t = ticket(c)
    p03.as_user(c.agent)
    out = p03.write(model="fix.itsm.ticket", record_id=t.id, values={"assigned_to": c.agent2_e.id})
    assert "error" in out
    assert not t.assigned_to and t.state == "new"
    assert refused(c.env, lambda: t.with_user(c.agent).write({"assigned_to": c.agent2_e.id}))


def test_a12f_n_m66_5_agent_with_no_employee_takes_a_ticket(c, p03):
    user, _ = _user(c.env, "m66f_agent_noemp", [AGENT], employee=False)
    t = ticket(c)
    p03.as_user(user)
    out = p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_assign")
    assert out.get("success"), out
    assert t.assigned_user_id == user and not t.assigned_to
    assert p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_start").get("success")


def test_a12f_m66_8_only_the_assignee_works_it_until_reassigned(c):
    t = working(c)
    assert "Reassign" in refused(
        c.env, lambda: t.with_user(c.agent2).action_resolve(resolution="x")
    )
    assert refused(c.env, lambda: t.with_user(c.agent2).action_start())
    t.with_user(c.agent2).action_reassign(assigned_to=c.agent2_e.id)
    assert t.assigned_user_id == c.agent2
    t.with_user(c.agent2).action_resolve(resolution="done")
    assert t.state == "resolved"


def test_a12f_m66_8_an_agent_does_not_resolve_his_own_request(c):
    t = working(c, requester_id=c.agent_e.id)
    assert "another agent" in refused(
        c.env, lambda: t.with_user(c.agent).action_resolve(resolution="x")
    )
    t.with_user(c.agent2).action_reassign(assigned_to=c.agent2_e.id)
    t.with_user(c.agent2).action_resolve(resolution="done")


def test_a12f_walk_ticket_new_to_closed_as_real_users_via_screen(c, p03):
    p03.as_user(c.plain)
    out = p03.write(
        model="fix.itsm.ticket",
        values={"title": "VPN", "description": "drops", "category": "network"},
    )
    tid = out["id"]
    p03.as_user(c.agent)
    for method, kwargs in (
        ("action_classify", None),
        ("action_assign", {"assigned_to": ""}),
        ("action_start", None),
        ("action_await_user", {"reason": "Which site?"}),
    ):
        res = p03.action(model="fix.itsm.ticket", ids=[tid], method=method, kwargs=kwargs)
        assert res.get("success"), (method, res)
    p03.as_user(c.plain)
    assert p03.action(model="fix.itsm.ticket", ids=[tid], method="action_resume").get("success")
    p03.as_user(c.agent)
    res = p03.action(
        model="fix.itsm.ticket", ids=[tid], method="action_resolve", kwargs={"resolution": "Fixed"}
    )
    assert res.get("success"), res
    p03.as_user(c.plain)
    assert p03.action(model="fix.itsm.ticket", ids=[tid], method="action_close").get("success")
    t = c.env["fix.itsm.ticket"].browse(tid)
    assert t.state == "closed" and t.classified_by_id == c.agent


# ============================================================ M66-7 SLA
def test_a12f_m66_7_awaiting_user_pauses_the_clock(c):
    t = working(c)
    deadline = t.sla_deadline
    t.with_user(c.agent).action_await_user(reason="Which floor?")
    assert t.state == "awaiting_user" and t.sla_paused_since
    overdue(c, t)
    c.env["fix.itsm.ticket"].sudo().cron_escalate_sla()
    assert not t.escalated, "a paused ticket was escalated"
    t.sudo()._guarded().write({"sla_paused_since": fields.Datetime.now() - timedelta(hours=3)})
    t.with_user(c.agent).action_resume()
    assert t.state == "in_progress" and not t.sla_paused_since
    assert 2.9 < t.sla_paused_hours < 3.1
    assert abs((t.sla_deadline - deadline).total_seconds() - 3 * 3600) < 120


def test_a12f_m66_7_await_needs_a_reason(c):
    t = working(c)
    assert "reason" in refused(c.env, lambda: t.with_user(c.agent).action_await_user())


def test_a12f_m66_7_calendar_aware_deadline(c):
    cal = (
        c.env["fix.working.calendar"]
        .sudo()
        .create(
            {
                "name": "M66F calendar",
                "line_ids": [
                    (0, 0, {"weekday": w, "hour_from": 9.0, "hour_to": 17.0})
                    for w in ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
                ],
            }
        )
    )
    cat = (
        c.env["fix.itsm.catalogue"]
        .with_user(c.agent)
        .create({"code": "M66F-C", "name": "C", "target_hours": 16.0, "calendar_id": cal.id})
    )
    t = ticket(c, catalogue_id=cat.id)
    assert t.sla_calendar_id == cal
    # 16 working hours at 8 a day cannot finish in a wall-clock 16 hours.
    assert t.sla_deadline > t.create_date + timedelta(hours=16)
    plain = ticket(c)
    assert not plain.sla_calendar_id
    assert plain.sla_deadline == plain.create_date + timedelta(hours=8.0)
    # And a pause outside working hours costs the clock nothing.
    day = fields.Datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
    assert t._sla_hours_between(day, day + timedelta(hours=4)) == 0.0


def test_a12f_m66_7_tiers_climb_and_are_parameters(c):
    t = ticket(c, priority="low")
    overdue(c, t, hours=2)
    Tk = c.env["fix.itsm.ticket"].sudo()
    Tk.cron_escalate_sla()
    assert (t.escalation_level, t.priority) == (1, "medium")
    Tk.cron_escalate_sla()
    assert (t.escalation_level, t.priority) == (2, "high")
    Tk.cron_escalate_sla()  # the third tier falls due at 8 h, this is 2 h late
    assert (t.escalation_level, t.priority) == (2, "high")
    c.env["ir.config_parameter"].sudo().set_param("cd_itsm.sla_escalation_tiers", "0,1,2")
    Tk.cron_escalate_sla()
    assert (t.escalation_level, t.priority) == (3, "urgent")


def test_a12f_m66_7_escalation_tells_the_assignee(c):
    t = working(c)
    overdue(c, t)
    c.env["fix.itsm.ticket"].sudo().cron_escalate_sla()
    assert t.sudo().activity_ids.filtered(lambda a: a.user_id == c.agent)


def test_a12f_m66_7_escalation_tells_the_queue_when_unassigned(c):
    t = ticket(c)
    overdue(c, t)
    c.env["fix.itsm.ticket"].sudo().cron_escalate_sla()
    holders = t.sudo().activity_ids.mapped("user_id")
    assert holders, "an unassigned escalated ticket told nobody (158 live tickets)"
    assert holders[0].has_group(AGENT)


def test_a12f_m66_7_manager_is_told_too_and_never_twice(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_itsm.sla_escalation_manager", c.cm.login)
    t = ticket(c)
    overdue(c, t)
    Tk = c.env["fix.itsm.ticket"].sudo()
    Tk.cron_escalate_sla()
    Tk.cron_escalate_sla()
    mine = t.sudo().activity_ids.filtered(lambda a: a.user_id == c.cm)
    assert len(mine) == 1


def test_a12f_m66_7_priority_is_not_typed_down_after_escalation(c, p03):
    t = ticket(c)
    overdue(c, t)
    c.env["fix.itsm.ticket"].sudo().cron_escalate_sla()
    raised = t.priority
    assert "cannot be lowered" in refused(
        c.env, lambda: t.with_user(c.agent).write({"priority": "low"})
    )
    p03.as_user(c.agent)
    assert "error" in p03.write(model="fix.itsm.ticket", record_id=t.id, values={"priority": "low"})
    t.with_user(c.agent).action_classify(impact="low", urgency="low")
    assert t.priority == raised, "classification undid the escalation"
    t.with_user(c.agent).write({"priority": "urgent"})  # raising it stays open
    assert t.priority == "urgent"


# ============================================================ I2 / BRU-ITS-20
def test_a12f_i2_classify_sets_priority_from_impact_and_urgency(c, p03):
    t = ticket(c)
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.ticket",
        ids=[t.id],
        method="action_classify",
        kwargs={"impact": "high", "urgency": "medium", "ticket_type": "request"},
    )
    assert out.get("success"), out
    assert t.priority == "high" and t.ticket_type == "request" and t.classified_on
    p03.as_user(c.plain)
    assert not p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_classify").get(
        "success"
    )


def test_a12f_bru_its_20_major_incident_has_a_named_manager(c, p03):
    t = working(c)
    p03.as_user(c.agent)
    out = p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_declare_major")
    assert not out["success"] and "Name the major incident manager" in out["error"]
    out = p03.action(
        model="fix.itsm.ticket",
        ids=[t.id],
        method="action_declare_major",
        kwargs={"manager": c.cm.login},
    )
    assert out.get("success"), out
    assert t.major_incident and t.major_incident_manager_id == c.cm and t.priority == "urgent"
    assert t.sudo().activity_ids.filtered(lambda a: a.user_id == c.cm)
    assert refused(c.env, lambda: t.with_user(c.agent).write({"major_incident": False}))
    # The communication cadence is chased, and an update resets it.
    t.sudo()._guarded().write({"major_last_comms_on": fields.Datetime.now() - timedelta(hours=2)})
    c.env["fix.itsm.ticket"].sudo().cron_escalate_sla()
    assert t.sudo().activity_ids.filtered(lambda a: (a.summary or "").startswith("Update due"))
    t.with_user(c.agent).action_major_update(note="Vendor engaged")
    assert fields.Datetime.now() - t.major_last_comms_on < timedelta(minutes=5)


def test_a12f_bru_its_20_manager_must_be_a_desk_person(c):
    t = ticket(c)
    assert "ITSM Agent" in refused(
        c.env, lambda: t.with_user(c.agent).action_declare_major(manager=c.plain.login)
    )


# ============================================================ N-M66-7 visibility
def test_a12f_n_m66_7_employee_reads_only_his_own_tickets(c, p03):
    other = ticket(c, requester_id=c.plain2_e.id, title="Private")
    mine = ticket(c)
    p03.as_user(c.plain)
    out = p03.records(
        model="fix.itsm.ticket", cols=["title"], domain=[("id", "in", [other.id, mine.id])]
    )
    assert [r["id"] for r in out["rows"]] == [mine.id]
    form = p03.form(model="fix.itsm.ticket", record_id=other.id, fields=[{"name": "title"}])
    assert "error" in form or not form.get("record")


def test_a12f_n_m66_7_agent_reads_his_units_only(c, p03):
    Unit = c.env["operating.unit"]
    far = Unit.create(
        {
            "name": "M66F far",
            "code": "M66FF",
            "partner_id": c.env.company.partner_id.id,
            "company_id": c.env.company.id,
        }
    )
    near, away = ticket(c), ticket(c)
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_itsm_ticket SET operating_unit_id=%s WHERE id=%s", (far.id, away.id)
    )
    away.invalidate_recordset()
    p03.as_user(c.agent)
    out = p03.records(
        model="fix.itsm.ticket", cols=["name"], domain=[("id", "in", [near.id, away.id])]
    )
    assert [r["id"] for r in out["rows"]] == [near.id]


def test_a12f_n_m66_7_security_ticket_is_masked_from_other_agents(c, p03):
    t = ticket(c, category="security", title="Account compromised", user=c.cm)
    p03.as_user(c.agent)
    out = p03.records(model="fix.itsm.ticket", cols=["title"], domain=[("id", "=", t.id)])
    assert not out["rows"], "an agent not on the case read a security incident"
    p03.as_user(c.cm)
    assert p03.records(model="fix.itsm.ticket", cols=["title"], domain=[("id", "=", t.id)])["rows"]
    t.with_user(c.cm).action_assign(assigned_to=c.agent2_e.id)
    p03.as_user(c.agent2)
    assert p03.records(model="fix.itsm.ticket", cols=["title"], domain=[("id", "=", t.id)])["rows"]
    p03.as_user(c.agent)
    assert not p03.records(model="fix.itsm.ticket", cols=["title"], domain=[("id", "=", t.id)])[
        "rows"
    ]


def test_a12f_n_m66_7_security_ticket_goes_to_someone_who_may_read_it(c):
    t = ticket(c, category="security", title="Account compromised", user=c.cm)
    owner = t._queue_owner()
    assert owner and (owner.has_group(CM) or owner.has_group(CAB))


def test_a12f_n_m66_7_employee_sees_only_his_own_assets(c, p03):
    mine, other = allocated(c), allocated(c, c.plain2_e)
    p03.as_user(c.plain)
    out = p03.records(
        model="fix.itsm.asset",
        cols=["name", "serial_no"],
        domain=[("id", "in", [mine.id, other.id])],
    )
    assert [r["id"] for r in out["rows"]] == [mine.id]


def test_a12f_n_m66_7_licence_cost_is_restricted(c, p03):
    x = licence(c, unit_cost=1000, seats_owned=10)
    p03.as_user(c.plain)
    out = p03.records(
        model="fix.itsm.licence",
        cols=["name", "unit_cost", "annual_cost"],
        domain=[("id", "=", x.id)],
    )
    assert out["rows"] and "annual_cost" not in out["rows"][0] and "unit_cost" not in out["rows"][0]
    p03.as_user(c.agent)
    out = p03.records(
        model="fix.itsm.licence", cols=["name", "annual_cost"], domain=[("id", "=", x.id)]
    )
    assert out["rows"][0]["annual_cost"] == 10000


def test_a12f_n_m66_7_kpis_are_scoped(c):
    import odoo.addons.cd_p03_portal.controllers.a12.m66 as m

    ticket(c, requester_id=c.plain2_e.id)
    ticket(c)
    env_p = c.env(user=c.plain.id)
    assert m.kpis(env_p)["tickets_total"] == 1


# ============================================================ N-M66-10 + screen wiring
def _m66_js():
    from odoo.addons.cd_p03_portal.controllers.a12 import m66

    return (Path(m66.__file__).parents[2] / "static" / "src" / "a12" / "m66.js").read_text(
        encoding="utf-8"
    )


def test_a12f_n_m66_10_incidents_and_requests_show_different_rows(c, p03):
    inc = ticket(c)
    cat = c.env["fix.itsm.catalogue"].with_user(c.agent).create({"code": "M66F-R", "name": "R"})
    req = ticket(c, catalogue_id=cat.id)
    assert inc.ticket_type == "incident" and req.ticket_type == "request"
    js = _m66_js()
    assert "domain: [['ticket_type', '=', 'incident']]" in js
    assert "domain: [['ticket_type', '=', 'request']]" in js
    p03.as_user(c.agent)
    ids = [inc.id, req.id]
    only_inc = p03.records(
        model="fix.itsm.ticket",
        cols=["name"],
        domain=[["ticket_type", "=", "incident"], ["id", "in", ids]],
    )
    only_req = p03.records(
        model="fix.itsm.ticket",
        cols=["name"],
        domain=[["ticket_type", "=", "request"], ["id", "in", ids]],
    )
    assert [r["id"] for r in only_inc["rows"]] == [inc.id]
    assert [r["id"] for r in only_req["rows"]] == [req.id]


def test_a12f_every_screen_action_is_whitelisted_and_its_kwarg_exists(c):
    from odoo.addons.cd_p03_portal.controllers.a12 import m66

    js = _m66_js()
    declared = set()
    for conf in m66.SURFACES.values():
        declared |= set(conf["actions"])
    used = re.findall(r"m:\s*'(action_[a-z_]+)'(?:[^}]*?kwarg:\s*'([a-z_]+)')?", js)
    assert used
    for method, kwarg in used:
        assert method in declared, "%s has no surface whitelist" % method
        owners = [model for model, conf in m66.SURFACES.items() if method in conf["actions"]]
        # One method name can live on two surfaces (ticket and problem both resolve):
        # the button's kwarg has to exist on at least the one it belongs to.
        if kwarg:
            assert any(
                kwarg in inspect.signature(getattr(c.env[model], method)).parameters
                for model in owners
            ), "%s has no kwarg %s on %s" % (method, kwarg, owners)


def test_a12f_every_screen_column_and_form_field_exists(c):
    from odoo.addons.cd_p03_portal.controllers.a12 import m66

    js = _m66_js()
    blocks = re.findall(
        r"model: '(fix\.itsm\.[a-z.]+)'[^\n]*\n?\s*(?:domain[^\n]*\n\s*)?cols: \[([^\]]+)\]", js
    )
    assert blocks
    for model, cols in blocks:
        for col in re.findall(r"'([a-z_0-9]+)'", cols):
            assert col in c.env[model]._fields, "%s.%s is on a screen and not the model" % (
                model,
                col,
            )
    forms = re.split(r"\n  '(M66-form-[a-z]+)': \{", js)[1:]
    for name, body in zip(forms[0::2], forms[1::2], strict=True):
        model = re.search(r"model: '([a-z.]+)'", body).group(1)
        for field in re.findall(r"\{ name: '([a-z_0-9]+)'", body):
            assert field in c.env[model]._fields, "%s: %s.%s" % (name, model, field)
    for model, writable in m66.WRITABLE.items():
        for field in writable:
            assert field in c.env[model]._fields, "%s.%s in WRITABLE" % (model, field)
    assert "assigned_to" not in m66.WRITABLE["fix.itsm.ticket"]
    assert "seats_assigned" not in m66.WRITABLE["fix.itsm.licence"]
    for model in ("fix.itsm.ticket", "fix.itsm.asset", "fix.itsm.licence"):
        assert m66.SURFACES[model].get("rules") is True


def test_a12f_n_m66_9_approver_and_review_are_on_the_screen():
    js = _m66_js()
    for field in ("approved_by_id", "pir_notes", "implemented_on", "asset_ids", "ci_ids"):
        assert "name: '%s'" % field in js
    assert "m: 'action_recall_approval'" in js


# ============================================================ M66-12 catalogue
def test_a12f_m66_12_requires_approval_gates_fulfilment_end_to_end(c, p03):
    cat = (
        c.env["fix.itsm.catalogue"]
        .with_user(c.agent)
        .create({"code": "M66F-A", "name": "Admin rights", "requires_approval": True})
    )
    p03.as_user(c.plain)
    out = p03.write(
        model="fix.itsm.ticket",
        values={"title": "Admin", "description": "Need it", "catalogue_id": cat.id},
    )
    assert "error" not in out, out
    t = c.env["fix.itsm.ticket"].browse(out["id"])
    assert t.ticket_type == "request"
    assert t.approval_state == "pending", "the employee's request did not reach an approver"
    p03.as_user(c.agent)
    res = p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_assign")
    assert not res["success"] and "requires approval" in res["error"]
    assert t.state == "new"
    decide(t, c.cm)
    assert t.approval_state == "approved" and t.fulfilment_approved_by_id == c.cm
    res = p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_assign")
    assert res.get("success"), res


def test_a12f_m66_12_refused_request_is_rejected_and_requester_told(c):
    cat = (
        c.env["fix.itsm.catalogue"]
        .with_user(c.agent)
        .create({"code": "M66F-A2", "name": "Admin", "requires_approval": True})
    )
    t = ticket(c, catalogue_id=cat.id, requester_id=c.plain_e.id)
    tasks = t.sudo().approval_request_id.task_ids.filtered(lambda x: x.assigned_user_id == c.cm)
    tasks.with_user(c.cm).action_reject(comment="No business case")
    assert t.state == "rejected"
    assert t.sudo().activity_ids.filtered(lambda a: a.user_id == c.plain)
    assert refused(c.env, lambda: t.with_user(c.agent).action_assign())


def test_a12f_m66_12_requester_never_approves_his_own_request(c):
    cat = (
        c.env["fix.itsm.catalogue"]
        .with_user(c.agent)
        .create({"code": "M66F-A3", "name": "Admin", "requires_approval": True})
    )
    t = ticket(c, catalogue_id=cat.id, requester_id=c.cm_e.id)
    holders = t.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.cm not in holders and c.cm2 in holders


def test_a12f_m66_12_request_with_no_approver_stays_and_is_gated(c):
    cat = (
        c.env["fix.itsm.catalogue"]
        .with_user(c.agent)
        .create({"code": "M66F-A4", "name": "Admin", "requires_approval": True})
    )
    c.env.ref(CM).sudo().write({"user_ids": [(5,)]})
    c.env.ref(CAB).sudo().write({"user_ids": [(5,)]})
    t = ticket(c, catalogue_id=cat.id)
    assert t.state == "new" and t.approval_state == "none"
    assert refused(c.env, lambda: t.with_user(c.agent).action_assign())
    assert "No one can approve" in refused(
        c.env, lambda: t.with_user(c.agent).action_request_fulfilment()
    )


def test_a12f_m66_12_policy_is_controlled_and_leaves_a_trail(c, p03):
    cat = (
        c.env["fix.itsm.catalogue"]
        .with_user(c.agent)
        .create({"code": "M66F-B", "name": "B", "requires_approval": True, "target_hours": 4})
    )
    assert refused(c.env, lambda: cat.with_user(c.plain).write({"requires_approval": False}))
    assert "Change Manager" in refused(
        c.env, lambda: cat.with_user(c.agent).write({"requires_approval": False})
    )
    p03.as_user(c.agent)
    assert "error" in p03.write(
        model="fix.itsm.catalogue", record_id=cat.id, values={"requires_approval": False}
    )
    # The agent's own echo of the form still saves.
    assert "error" not in p03.write(
        model="fix.itsm.catalogue",
        record_id=cat.id,
        values={"requires_approval": True, "target_hours": 6},
    )
    cat.with_user(c.cm).write({"requires_approval": False})
    c.env.flush_all()
    c.env.cr.precommit.run()  # field tracking is finalised at commit
    tracked = cat.sudo().message_ids.mapped("tracking_value_ids.field_id.name")
    assert "requires_approval" in tracked and "target_hours" in tracked


def test_a12f_m66_12_ci_depends_on_is_a_relation_without_cycles(c):
    a = c.env["fix.itsm.ci"].with_user(c.agent).create({"name": "DB", "ci_key": "m66f-db"})
    b = (
        c.env["fix.itsm.ci"]
        .with_user(c.agent)
        .create({"name": "App", "ci_key": "m66f-app", "depends_on": [(6, 0, a.ids)]})
    )
    assert b.depends_on == a
    assert refused(c.env, lambda: a.with_user(c.agent).write({"depends_on": [(6, 0, b.ids)]}))


# ============================================================ M66-9 problem, P1, P3, BRU-03/04/05
def problem(c, **kw):
    vals = {"title": "VPN drop", "severity": "high", "owner_id": c.agent.id}
    vals.update(kw)
    return c.env["fix.itsm.problem"].with_user(c.agent).create(vals)


def test_a12f_m66_9_known_error_comes_from_investigation(c):
    p = problem(c, root_cause="rc", workaround="wa")
    assert "under investigation" in refused(
        c.env, lambda: p.with_user(c.agent).action_known_error()
    )
    p.with_user(c.agent).action_investigate()
    p.with_user(c.agent).action_known_error()
    assert p.state == "known_error" and p.known_error


def test_a12f_bru_its_05_close_needs_a_clean_verification_window(c):
    p = problem(c, root_cause="rc", workaround="wa")
    p.with_user(c.agent).action_investigate()
    p.with_user(c.agent).action_resolve()
    assert "verif" in refused(c.env, lambda: p.with_user(c.agent).action_close())
    p.with_user(c.agent).action_verify()
    assert p.state == "verifying" and p.verify_until > c.today
    assert "being verified" in refused(c.env, lambda: p.with_user(c.agent).action_close())
    p.sudo()._guarded().write({"verify_until": c.today})
    c.env["fix.itsm.problem"].sudo().cron_problem_verification()
    assert p.sudo().activity_ids.filtered(lambda a: a.user_id == c.agent)
    p.with_user(c.agent).action_close()
    assert p.state == "closed"


def test_a12f_bru_its_05_recurrence_reopens_investigation(c):
    p = problem(c, root_cause="rc", workaround="wa")
    p.with_user(c.agent).action_investigate()
    p.with_user(c.agent).action_resolve()
    p.with_user(c.agent).action_verify()
    # One test transaction has one create_date: open the window before it.
    p.sudo()._guarded().write({"verify_started_on": fields.Datetime.now() - timedelta(days=2)})
    t = ticket(c, problem_id=p.id)
    assert t.problem_id == p
    assert p.state == "investigating", "an incident during the window did not reopen the problem"
    assert p.incident_count == 1


def test_a12f_p3_fix_change_must_be_implemented_before_resolve(c):
    ch = approved_change(c, implementer_id=c.agent2_e.id)
    p = problem(c, root_cause="rc", workaround="wa", fix_change_id=ch.id)
    p.with_user(c.agent).action_investigate()
    assert "is approved" in refused(c.env, lambda: p.with_user(c.agent).action_resolve())
    ch.with_user(c.agent2).action_implement()
    c.env["fix.event.outbox"].sudo().cron_relay()
    assert p.sudo().activity_ids.filtered(lambda a: (a.summary or "").startswith("Fix implemented"))
    p.with_user(c.agent).action_resolve()
    assert p.state == "resolved"


def test_a12f_m66_9_closed_problem_is_locked(c, p03):
    p = problem(c, root_cause="rc", workaround="wa")
    p.with_user(c.agent).action_investigate()
    p.with_user(c.agent).action_resolve()
    p.with_user(c.agent).action_verify()
    p.sudo()._guarded().write({"verify_until": c.today})
    p.with_user(c.agent).action_close()
    assert refused(c.env, lambda: p.with_user(c.agent).write({"root_cause": "rewritten"}))
    assert refused(c.env, lambda: p.with_user(c.agent).action_known_error())
    p03.as_user(c.agent)
    assert "error" in p03.write(
        model="fix.itsm.problem", record_id=p.id, values={"root_cause": "z"}
    )


def test_a12f_p1_incident_links_and_raises_a_problem(c, p03):
    t = ticket(c, priority="urgent")
    p03.as_user(c.agent)
    assert p03.action(model="fix.itsm.ticket", ids=[t.id], method="action_raise_problem").get(
        "success"
    )
    assert t.problem_id and t.problem_id.severity == "critical"
    assert t.problem_id.ticket_ids == t
    assert refused(c.env, lambda: t.with_user(c.agent).action_raise_problem())


def test_a12f_bru_its_03_incident_closes_while_the_problem_stays_open(c):
    p = problem(c)
    t = working(c, problem_id=p.id)
    t.with_user(c.agent).action_resolve(resolution="restart")
    t.with_user(c.agent).action_close()
    assert t.state == "closed" and p.state == "open"


def test_a12f_bru_its_04_recurring_incidents_raise_a_problem(c):
    ci = c.env["fix.itsm.ci"].with_user(c.agent).create({"name": "Gateway", "ci_key": "m66f-gw"})
    first = ticket(c, ci_id=ci.id) | ticket(c, ci_id=ci.id)
    Tk = c.env["fix.itsm.ticket"].sudo()
    Tk.cron_ticket_housekeeping()
    assert not first[0].problem_id, "two is below the default threshold of three"
    third = ticket(c, ci_id=ci.id)
    Tk.cron_ticket_housekeeping()
    assert third.problem_id and third.problem_id == first[0].problem_id == first[1].problem_id
    assert "Gateway" in third.problem_id.title


# ============================================================ M66-1 standard + SoD
def test_a12f_m66_1_self_declared_standard_does_not_auto_approve(c):
    ch = change(c, title="Replace the core firewall", change_type="standard", risk="low",
                risk_probability="1", risk_impact="1")  # fmt: skip
    ch.with_user(c.agent).action_submit()
    assert ch.state == "draft" and ch.approval_state == "pending"
    assert c.cab in ch.sudo().approval_request_id.task_ids.mapped("assigned_user_id")


def test_a12f_m66_1_standard_from_an_authorised_template_is_pre_approved(c, p03):
    tpl = template(c)
    p03.as_user(c.agent)
    out = p03.write(
        model="fix.itsm.change",
        values={
            "title": "Rotate app log",
            "template_id": tpl.id,
            "requested_by_id": c.agent_e.id,
            "implementer_id": c.agent2_e.id,
            "planned_on": str(c.today),
        },
    )
    assert "error" not in out, out
    ch = c.env["fix.itsm.change"].browse(out["id"])
    assert ch.change_type == "standard" and ch.implementation_plan == tpl.implementation_plan
    res = p03.action(model="fix.itsm.change", ids=[ch.id], method="action_submit")
    assert res.get("success"), res
    assert ch.state == "approved" and ch.approval_state == "approved" and not ch.approved_by_id
    assert tpl.code in " ".join(str(m.body) for m in ch.sudo().message_ids)


def test_a12f_m66_1_departing_from_the_template_routes_for_approval(c):
    tpl = template(c)
    ch = change(c, template_id=tpl.id, change_type="standard",
                implementation_plan="Rip out the core firewall")  # fmt: skip
    ch.with_user(c.agent).action_submit()
    assert ch.state == "draft" and ch.approval_state == "pending"
    too_long = change(c, template_id=tpl.id, change_window_hours=48)
    too_long.with_user(c.agent).action_submit()
    assert too_long.approval_state == "pending"


def test_a12f_m66_1_template_risk_is_a_floor(c):
    tpl = template(c, risk_probability="1", risk_impact="5")  # 5, below the CAB line
    ch = change(c, template_id=tpl.id, risk_probability="1", risk_impact="1")
    assert ch.risk_floor_score == 5 and not ch.high_risk
    assert "floor" in ch.risk_basis
    c.env["ir.config_parameter"].sudo().set_param("cd_itsm.change_cab_risk_score", "5")
    ch.with_user(c.agent).write({"risk_impact": "2"})
    assert ch.high_risk


def test_a12f_m66_1_template_needs_authority_and_a_second_person(c):
    tpl = (
        c.env["fix.itsm.change.template"]
        .with_user(c.cm)
        .create(
            {
                "code": "STD-X",
                "name": "X",
                "implementation_plan": "i",
                "test_plan": "t",
                "rollback_plan": "r",
            }
        )
    )
    assert refused(c.env, lambda: tpl.with_user(c.agent).action_authorise())
    assert "another person" in refused(c.env, lambda: tpl.with_user(c.cm).action_authorise())
    tpl.with_user(c.cab).action_authorise()
    assert tpl.state == "authorised" and tpl.authorised_by_id == c.cab
    tpl.with_user(c.agent).write({"implementation_plan": "something else"})
    assert tpl.state == "draft", "an edited template kept its authorisation"
    risky = (
        c.env["fix.itsm.change.template"]
        .with_user(c.agent)
        .create(
            {
                "code": "STD-Y",
                "name": "Y",
                "implementation_plan": "i",
                "test_plan": "t",
                "rollback_plan": "r",
                "risk_probability": "3",
                "risk_impact": "3",
            }
        )
    )
    assert "CAB threshold" in refused(c.env, lambda: risky.with_user(c.cm).action_authorise())


def test_a12f_m66_1_a_critical_ci_overrides_the_requesters_score(c):
    ci = (
        c.env["fix.itsm.ci"]
        .with_user(c.agent)
        .create({"name": "Core FW", "ci_key": "m66f-fw", "criticality": "critical"})
    )
    ch = change(c, title="Replace core firewall", risk="low", risk_probability="1", risk_impact="1",
                ci_ids=[(6, 0, ci.ids)])  # fmt: skip
    assert ch.high_risk and ch.risk_floor_score == 16
    ch.with_user(c.agent).action_submit()
    routed = ch.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.cab in routed and c.cm not in routed


def test_a12f_m66_1_low_score_with_nothing_linked_goes_to_the_cab(c):
    ch = change(c, title="Replace core firewall", risk="low", risk_probability="1", risk_impact="1")
    ch.with_user(c.agent).action_submit()
    assert c.cab in ch.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    low_ci = (
        c.env["fix.itsm.ci"]
        .with_user(c.agent)
        .create({"name": "P", "ci_key": "m66f-p", "criticality": "low"})
    )
    checked = change(
        c, risk="low", risk_probability="1", risk_impact="1", ci_ids=[(6, 0, low_ci.ids)]
    )
    assert not checked.high_risk


def test_a12f_n_m66_8_untouched_normal_change_reaches_the_change_manager(c):
    ch = (
        c.env["fix.itsm.change"]
        .with_user(c.agent)
        .create({"title": "D", "requested_by_id": c.agent_e.id})
    )
    assert ch.risk_score == 4
    assert ch._approval_group_xmlid() == CM


def test_a12f_m66_1_acting_user_must_be_the_implementer(c):
    ch = approved_change(c, implementer_id=c.agent2_e.id)
    assert "not that person" in refused(c.env, lambda: ch.with_user(c.agent).action_implement())
    assert "not that person" in refused(c.env, lambda: ch.with_user(c.cm).action_implement())
    ch.with_user(c.agent2).action_implement()
    assert ch.state == "implemented" and ch.implemented_by_id == c.agent2


def test_a12f_m66_1_sod_compares_employees_not_logins(c):
    nobody = c.env["hr.employee"].create({"name": "M66F No Login"})
    ch = approved_change(c, requested_by_id=nobody.id, implementer_id=nobody.id)
    assert "not the requester" in refused(c.env, lambda: ch.with_user(c.agent).action_implement())


def test_a12f_m66_1_implementer_with_no_login_is_recorded_by_an_independent_agent(c):
    nobody = c.env["hr.employee"].create({"name": "M66F No Login 2"})
    ch = approved_change(c, implementer_id=nobody.id)  # requested by agent, approved by cm
    assert refused(c.env, lambda: ch.with_user(c.agent).action_implement())
    assert refused(c.env, lambda: ch.with_user(c.cm).action_implement())
    ch.with_user(c.agent2).action_implement()
    assert ch.state == "implemented"


def test_a12f_m66_1_legacy_approved_row_with_no_approval_is_not_implementable(c):
    ch = change(c, implementation_plan=False, test_plan=False, implementer_id=c.agent2_e.id)
    ch.sudo()._guarded().write({"state": "approved", "approval_state": "none"})
    assert "no recorded approval" in refused(
        c.env, lambda: ch.with_user(c.agent2).action_implement()
    )


def test_a12f_c03_bru_its_06_every_plan_is_needed_to_submit(c):
    for missing in ("implementation_plan", "test_plan", "rollback_plan"):
        ch = change(c, **{missing: False})
        assert refused(c.env, lambda x=ch: x.with_user(c.agent).action_submit()), missing


# ============================================================ M66-2 pinned
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "Replace core firewall"),
        ("planned_on", "2031-01-01"),
        ("rollback_plan", "none"),
        ("change_window_hours", 48),
        ("risk", "high"),
        ("risk_probability", "5"),
        ("risk_impact", "5"),
        ("change_type", "emergency"),
        ("implementation_plan", "Rip out the whole core"),
        ("test_plan", "No test"),
    ],
)
def test_a12f_m66_2_editing_the_approved_terms_voids_the_approval(c, field, value):
    ch = approved_change(c)
    ch.with_user(c.agent).write({field: value})
    assert ch.state == "draft" and ch.approval_state == "none", field


def test_a12f_m66_2_requester_and_scope_are_pinned_too(c):
    a = asset(c)
    ci = c.env["fix.itsm.ci"].with_user(c.agent).create({"name": "C", "ci_key": "m66f-pin"})
    for vals in (
        {"requested_by_id": c.plain2_e.id},
        {"asset_ids": [(6, 0, a.ids)]},
        {"ci_ids": [(6, 0, ci.ids)]},
    ):
        ch = approved_change(c)
        ch.with_user(c.agent).write(vals)
        assert ch.state == "draft", vals


def test_a12f_m66_2_implemented_change_is_not_rewritten(c, p03):
    ch = approved_change(c, implementer_id=c.agent2_e.id)
    ch.with_user(c.agent2).action_implement()
    assert "stands as the record" in refused(
        c.env, lambda: ch.with_user(c.agent).write({"title": "x"})
    )
    p03.as_user(c.agent)
    assert "error" in p03.write(model="fix.itsm.change", record_id=ch.id, values={"title": "x"})


# ============================================================ M66-3 emergency, N-M66-2
def test_a12f_m66_3_emergency_implement_first_walk_via_screen(c, p03):
    ch = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    p03.as_user(c.agent2)
    # The ordinary button keeps refusing; the emergency path is an explicit action.
    assert not p03.action(model="fix.itsm.change", ids=[ch.id], method="action_implement")[
        "success"
    ]
    out = p03.action(
        model="fix.itsm.change",
        ids=[ch.id],
        method="action_emergency_implement",
        kwargs={"reason": "Payment gateway down"},
    )
    assert out.get("success"), out
    assert ch.state == "implemented" and ch.emergency_path and ch.retro_approval_state == "pending"
    routed = ch.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.cab in routed
    assert c.agent2 not in routed and c.agent not in routed
    decide(ch, c.cab)
    assert ch.state == "implemented", "retro approval must not rewind the change"
    assert ch.retro_approval_state == "approved" and ch.approved_by_id == c.cab


def test_a12f_m66_3_emergency_needs_reason_plans_and_type(c):
    ch = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    assert "reason" in refused(c.env, lambda: ch.with_user(c.agent2).action_emergency_implement())
    bare = change(c, change_type="emergency", implementer_id=c.agent2_e.id, rollback_plan=False)
    assert "rollback plan" in refused(
        c.env, lambda: bare.with_user(c.agent2).action_emergency_implement(reason="now")
    )
    normal = change(c, implementer_id=c.agent2_e.id)
    assert "Only an emergency" in refused(
        c.env, lambda: normal.with_user(c.agent2).action_emergency_implement(reason="now")
    )
    same = change(c, change_type="emergency", implementer_id=c.agent_e.id)
    assert "not the requester" in refused(
        c.env, lambda: same.with_user(c.agent).action_emergency_implement(reason="now")
    )
    assert refused(c.env, lambda: ch.with_user(c.plain).action_emergency_implement(reason="now"))


def test_a12f_m66_3_retro_goes_to_change_manager_when_the_cab_is_empty(c):
    c.env.ref(CAB).sudo().write({"user_ids": [(5,)]})
    ch = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    ch.with_user(c.agent2).action_emergency_implement(reason="now")
    assert ch.retro_approval_state == "pending" and ch.retro_approval_group == "cm"
    decide(ch, c.cm)
    assert ch.retro_approval_state == "approved"


def test_a12f_m66_3_nobody_to_approve_never_blocks_and_the_cron_retries(c):
    c.env.ref(CAB).sudo().write({"user_ids": [(5,)]})
    c.env.ref(CM).sudo().write({"user_ids": [(5,)]})
    ch = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    ch.with_user(c.agent2).action_emergency_implement(reason="now")
    assert ch.state == "implemented" and ch.retro_approval_state == "unrouted"
    c.cm.sudo().write({"group_ids": [(4, c.env.ref(CM).id)]})
    c.env["fix.itsm.change"].sudo().cron_chase_pir()
    assert ch.retro_approval_state == "pending"
    assert c.cm in ch.sudo().approval_request_id.task_ids.mapped("assigned_user_id")


def test_a12f_m66_3_refused_retro_tells_the_implementer_to_roll_back(c):
    ch = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    ch.with_user(c.agent2).action_emergency_implement(reason="now")
    tasks = ch.sudo().approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == c.cab)
    tasks.with_user(c.cab).action_reject(comment="Not an emergency")
    assert ch.state == "implemented" and ch.retro_approval_state == "rejected"
    assert ch.sudo().activity_ids.filtered(lambda a: a.user_id == c.agent2)
    assert refused(c.env, lambda: ch.with_user(c.agent2).action_recall_approval())


def test_a12f_m66_3_pir_is_chased_by_a_cron_that_exists(c):
    cron = c.env.ref("cd_itsm.ir_cron_itsm_chase_pir")
    assert cron.active and cron.model_id.model == "fix.itsm.change"
    ch = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    ch.with_user(c.agent2).action_emergency_implement(reason="now")
    assert ch.pir_required and ch.pir_due_on
    Change = c.env["fix.itsm.change"].sudo()
    Change.cron_chase_pir()
    assert not ch.sudo().activity_ids.filtered(lambda a: (a.summary or "").startswith("Post-impl"))
    ch.sudo()._guarded().write({"pir_due_on": c.today - timedelta(days=1)})
    Change.cron_chase_pir()
    chased = ch.sudo().activity_ids.filtered(lambda a: (a.summary or "").startswith("Post-impl"))
    assert c.agent in chased.mapped("user_id") and c.cm in chased.mapped("user_id")
    assert c.agent2 not in chased.mapped("user_id"), "the implementer cannot write it"


def test_a12f_c21_implementer_does_not_review_his_own_change(c, p03):
    ch = approved_change(c, implementer_id=c.agent2_e.id)
    p03.as_user(c.agent2)
    assert p03.action(model="fix.itsm.change", ids=[ch.id], method="action_implement").get(
        "success"
    )
    out = p03.action(
        model="fix.itsm.change",
        ids=[ch.id],
        method="action_record_pir",
        kwargs={"pir_notes": "fine"},
    )
    assert not out["success"] and "another person" in out["error"]
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.change",
        ids=[ch.id],
        method="action_record_pir",
        kwargs={"pir_notes": "fine"},
    )
    assert out.get("success"), out
    assert ch.state == "reviewed" and ch.pir_by_id == c.agent


def test_a12f_n_m66_2_emergency_rolls_back_before_and_after_its_review(c, p03):
    # Before the review: it is failing now and comes out now.
    early = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    early.with_user(c.agent2).action_emergency_implement(reason="now")
    p03.as_user(c.agent2)
    out = p03.action(
        model="fix.itsm.change",
        ids=[early.id],
        method="action_rollback",
        kwargs={"reason": "Worse"},
    )
    assert out.get("success"), out
    assert early.state == "rolled_back" and early.pir_required and not early.pir_on
    # The failed change still owes its review; it stays rolled back.
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.change",
        ids=[early.id],
        method="action_record_pir",
        kwargs={"pir_notes": "RCA"},
    )
    assert out.get("success"), out
    assert early.state == "rolled_back" and early.pir_on
    # After the review.
    late = approved_change(c, approver=c.cab, change_type="emergency", implementer_id=c.agent2_e.id)
    late.with_user(c.agent2).action_implement()
    late.with_user(c.agent).action_record_pir(pir_notes="failed, roll back")
    assert late.state == "reviewed"
    late.with_user(c.agent2).action_rollback()  # the review is the reason
    assert late.state == "rolled_back" and late.rollback_reason == "failed, roll back"


def test_a12f_bru_its_10_failed_change_owes_a_review(c):
    ch = approved_change(c, implementer_id=c.agent2_e.id)
    ch.with_user(c.agent2).action_implement()
    assert "reason" in refused(c.env, lambda: ch.with_user(c.agent2).action_rollback())
    ch.with_user(c.agent2).action_rollback(reason="Bad firmware")
    assert ch.pir_required and ch.pir_due_on and not ch.pir_on


def test_a12f_n_m66_9_requester_recalls_through_the_screen(c, p03):
    ch = change(c)
    ch.with_user(c.agent).action_submit()
    p03.as_user(c.agent)
    out = p03.action(model="fix.itsm.change", ids=[ch.id], method="action_recall_approval")
    assert out.get("success"), out
    assert ch.approval_state == "none" and ch.state == "draft"


# ============================================================ C4: collision, freeze
def test_a12f_bru_its_09_collision_on_an_asset_and_a_ci(c):
    a = asset(c)
    ci = c.env["fix.itsm.ci"].with_user(c.agent).create({"name": "C", "ci_key": "m66f-col"})
    day = c.today + timedelta(days=3)
    approved_change(c, asset_ids=[(6, 0, a.ids)], planned_on=day)
    clash = change(c, asset_ids=[(6, 0, a.ids)], planned_on=day, title="Other")
    assert "collides" in refused(c.env, lambda: clash.with_user(c.agent).action_submit())
    pending = change(c, ci_ids=[(6, 0, ci.ids)], planned_on=day)
    pending.with_user(c.agent).action_submit()
    clash2 = change(c, ci_ids=[(6, 0, ci.ids)], planned_on=day)
    assert "collides" in refused(c.env, lambda: clash2.with_user(c.agent).action_submit())
    # Another day, and a window that runs into the next day.
    fine = change(c, asset_ids=[(6, 0, a.ids)], planned_on=day + timedelta(days=1))
    fine.with_user(c.agent).action_submit()
    long = change(
        c, ci_ids=[(6, 0, ci.ids)], planned_on=day - timedelta(days=1), change_window_hours=30
    )
    assert "collides" in refused(c.env, lambda: long.with_user(c.agent).action_submit())


def test_a12f_bru_its_08_freeze_stops_all_but_the_emergency_path(c):
    start, end = c.today, c.today + timedelta(days=10)
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_itsm.change_freeze_windows", "%s:%s" % (start, end)
    )
    ch = change(c, planned_on=c.today + timedelta(days=1))
    assert ch.freeze_conflict
    assert "freeze window" in refused(c.env, lambda: ch.with_user(c.agent).action_submit())
    emergency = change(c, change_type="emergency", implementer_id=c.agent2_e.id)
    emergency.with_user(c.agent2).action_emergency_implement(reason="Outage")
    assert emergency.state == "implemented"
    assert "freeze" in " ".join(str(m.body) for m in emergency.sudo().message_ids)
    # Approved earlier, then a freeze arrives: implementing is what is refused.
    c.env["ir.config_parameter"].sudo().set_param("cd_itsm.change_freeze_windows", False)
    later = approved_change(c, implementer_id=c.agent2_e.id, planned_on=c.today)
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_itsm.change_freeze_windows", "%s:%s" % (start, end)
    )
    assert "freeze window" in refused(c.env, lambda: later.with_user(c.agent2).action_implement())


def test_a12f_bru_its_08_a_malformed_freeze_value_refuses(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_itsm.change_freeze_windows", "christmas")
    ch = change(c)
    assert "malformed" in refused(c.env, lambda: ch.with_user(c.agent).action_submit())
    assert ch.freeze_conflict


# ============================================================ M66-10, N-M66-11 assets
def test_a12f_m66_10_retirement_is_two_people(c, p03):
    a = asset(c)
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.asset",
        ids=[a.id],
        method="action_retire",
        kwargs={"wipe_certificate": "WIPE-1234"},
    )
    assert out.get("success"), out
    assert a.state == "in_stock" and a.writeoff_state == "requested"
    assert a.sudo().activity_ids.filtered(lambda x: x.user_id == c.cm)
    out = p03.action(model="fix.itsm.asset", ids=[a.id], method="action_approve_writeoff")
    assert not out["success"], "an agent decided a write-off"
    # Even a Change Manager does not approve his own record.
    b = asset(c)
    b.with_user(c.cm).action_retire(wipe_certificate="WIPE-5678")
    assert "second person" in refused(c.env, lambda: b.with_user(c.cm).action_approve_writeoff())
    b.with_user(c.cm2).action_approve_writeoff()
    assert b.state == "retired" and b.writeoff_approved_by_id == c.cm2
    p03.as_user(c.cm)
    assert p03.action(model="fix.itsm.asset", ids=[a.id], method="action_approve_writeoff").get(
        "success"
    )
    assert a.state == "retired"


def test_a12f_m66_10_certificate_must_be_a_real_reference(c):
    a = asset(c)
    assert "certificate" in refused(c.env, lambda: a.with_user(c.agent).action_retire())
    assert "not a certificate reference" in refused(
        c.env, lambda: a.with_user(c.agent).action_retire(wipe_certificate="x")
    )
    assert a.writeoff_state == "none"
    assert refused(c.env, lambda: a.with_user(c.agent).write({"wipe_certificate": "FORGED-1"}))


def test_a12f_m66_10_linked_m06_document_is_stamped(c):
    a = asset(c)
    att = c.env["ir.attachment"].create(
        {"name": "wc", "datas": b"ZGVzdHJveA==", "mimetype": "text/plain"}
    )
    doc = c.env["fix.document"].create(
        {
            "name": "Wipe certificate WIPE-777",
            "attachment_id": att.id,
            "document_type": "asset_document",
            "res_model": "fix.itsm.asset",
            "res_id": a.id,
        }
    )
    a.with_user(c.agent).action_retire(wipe_certificate="WIPE-777")
    assert a.wipe_document_id == doc


def test_a12f_m66_10_m06_document_can_be_made_mandatory(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_itsm.wipe_requires_m06_document", "1")
    a = asset(c)
    assert "M06" in refused(
        c.env, lambda: a.with_user(c.agent).action_retire(wipe_certificate="WIPE-1234")
    )


def test_a12f_m66_10_refused_write_off_leaves_the_asset(c):
    a = asset(c)
    a.with_user(c.agent).action_retire(wipe_certificate="WIPE-1234")
    assert refused(c.env, lambda: a.with_user(c.cm).action_reject_writeoff())
    a.with_user(c.cm).action_reject_writeoff(reason="Certificate unreadable")
    assert a.writeoff_state == "rejected" and a.state == "in_stock"
    a.with_user(c.agent).action_retire(wipe_certificate="WIPE-9999")
    assert a.writeoff_state == "requested"


def test_a12f_m66_10_retired_asset_stands_as_the_record(c, p03):
    a = retired(c, asset(c))
    assert refused(c.env, lambda: a.with_user(c.agent).write({"wipe_certificate": "OTHER-1"}))
    assert refused(c.env, lambda: a.with_user(c.agent).write({"assigned_to_id": c.plain_e.id}))
    assert refused(c.env, lambda: a.with_user(c.agent).write({"serial_no": "z"}))
    assert refused(c.env, lambda: a.with_user(c.agent).write({"state": "in_stock"}))
    assert refused(c.env, lambda: a.with_user(c.agent).action_allocate(assigned_to=c.plain_e.id))
    assert refused(c.env, lambda: a.with_user(c.agent).action_send_repair())
    assert "already retired" in refused(
        c.env, lambda: a.with_user(c.agent).action_retire(wipe_certificate="WIPE-2222")
    )


def test_a12f_m66_10_in_service_ci_blocks_retirement(c):
    a = asset(c)
    ci = (
        c.env["fix.itsm.ci"]
        .with_user(c.agent)
        .create({"name": "CI", "ci_key": "m66f-ci", "asset_id": a.id, "life_status": "in_service"})
    )
    assert "M66-13" in refused(
        c.env, lambda: a.with_user(c.agent).action_retire(wipe_certificate="WIPE-1234")
    )
    ci.with_user(c.agent).write({"life_status": "retired"})
    retired(c, a)
    assert a.state == "retired"
    assert refused(
        c.env,
        lambda: c.env["fix.itsm.ci"]
        .with_user(c.agent)
        .create({"name": "CI2", "ci_key": "m66f-ci2", "asset_id": a.id}),
    )


def test_a12f_bru_its_12_allocation_to_an_active_employee_with_acceptance(c, p03):
    ghost = c.env["hr.employee"].create({"name": "M66F Gone", "active": False})
    a = asset(c)
    assert refused(c.env, lambda: a.with_user(c.agent).action_allocate(assigned_to=ghost.id))
    assert refused(c.env, lambda: a.with_user(c.agent).write({"assigned_to_id": ghost.id}))
    # The screen's way: the form names the holder while it is in stock, then Allocate.
    p03.as_user(c.agent)
    out = p03.action(model="fix.itsm.asset", ids=[a.id], method="action_allocate")
    assert not out["success"] and "Name the employee" in out["error"]
    assert "error" not in p03.write(
        model="fix.itsm.asset", record_id=a.id, values={"assigned_to_id": c.plain_e.id}
    )
    out = p03.action(model="fix.itsm.asset", ids=[a.id], method="action_allocate")
    assert out.get("success"), out
    assert a.state == "in_service" and a.acceptance_state == "pending"
    assert a.sudo().activity_ids.filtered(lambda x: x.user_id == c.plain)
    p03.as_user(c.plain2)
    assert not p03.action(model="fix.itsm.asset", ids=[a.id], method="action_accept")["success"]
    p03.as_user(c.plain)
    out = p03.action(model="fix.itsm.asset", ids=[a.id], method="action_accept")
    assert out.get("success"), out
    assert a.acceptance_state == "accepted" and a.accepted_by_id == c.plain and a.accepted_on


def test_a12f_bru_its_12_paper_acceptance_for_a_holder_with_no_login(c, p03):
    holder = c.env["hr.employee"].create({"name": "M66F Paper"})
    a = allocated(c, holder)
    p03.as_user(c.agent)
    out = p03.action(model="fix.itsm.asset", ids=[a.id], method="action_record_acceptance")
    assert not out["success"]
    out = p03.action(
        model="fix.itsm.asset",
        ids=[a.id],
        method="action_record_acceptance",
        kwargs={"reference": "AF-1"},
    )
    assert out.get("success"), out
    assert a.acceptance_ref == "AF-1"


def test_a12f_n_m66_11_holder_moves_only_through_actions(c, p03):
    a = allocated(c)
    p03.as_user(c.agent)
    assert "error" in p03.write(
        model="fix.itsm.asset", record_id=a.id, values={"assigned_to_id": c.plain2_e.id}
    )
    assert "error" in p03.write(
        model="fix.itsm.asset", record_id=a.id, values={"assigned_to_id": False}
    )
    assert refused(c.env, lambda: a.with_user(c.agent).write({"assigned_to_id": False}))
    assert a.assigned_to_id == c.plain_e
    out = p03.action(model="fix.itsm.asset", ids=[a.id], method="action_return")
    assert out.get("success"), out
    assert a.state == "in_stock" and not a.assigned_to_id and a.acceptance_state == "none"
    assert refused(c.env, lambda: a.with_user(c.agent).action_return())


def test_a12f_m66_10_plain_user_works_no_asset(c):
    a = allocated(c)
    assert refused(c.env, lambda: a.with_user(c.plain).action_send_repair())
    assert refused(c.env, lambda: a.with_user(c.plain).action_return())
    assert refused(
        c.env, lambda: asset(c).with_user(c.plain).action_retire(wipe_certificate="WIPE-1")
    )


# ---- asset -> M21
def _exit(c, employee):
    Exit = c.env["fix.hr.exit"].sudo()
    vals = {"employee_id": employee.id, "last_working_day": c.today}
    for name, field in Exit._fields.items():
        if field.required and name not in vals and not field.default and not field.compute:
            if field.type == "selection":
                sel = (
                    field.selection if isinstance(field.selection, list) else field.selection(Exit)
                )
                vals[name] = sel[0][0]
            elif field.type == "date":
                vals[name] = c.today
            elif field.type == "char":
                vals[name] = "M66F"
    ex = Exit.create(vals)
    ex._guarded().write({"state": "notice"})
    return ex


def test_a12f_handoff_asset_blocks_exit_clearance_until_recovered(c):
    emp = c.env["hr.employee"].sudo().create({"name": "M66F Leaver"})
    a = allocated(c, emp)
    ex = _exit(c, emp)
    assert a.asset_tag in refused(c.env, lambda: ex._fix_tick("clearance_assets"))
    a.with_user(c.agent).action_return()
    ex._fix_tick("clearance_assets")
    assert ex.clearance_assets


def test_a12f_handoff_real_leaver_event_makes_the_asset_recovery_due(c):
    """Through the REAL M29 consumer: it clears the holder, and the asset must not
    read as free or as still in service."""
    emp = c.env["hr.employee"].sudo().create({"name": "M66F Leaver 2"})
    a = allocated(c, emp)
    ex = _exit(c, emp)
    emp.sudo().write({"active": False})  # M29 believes the event only once he has left
    c.env["fix.jml.event"].sudo().consume_employee_left(
        {
            "event_id": "m66f-leaver",
            "event_type": "employee.left",
            "aggregate_id": emp.id,
            "payload": {"employee_id": emp.id},
        }
    )
    a.invalidate_recordset()
    assert not a.assigned_to_id
    assert a.state == "recovery_due" and a.recovery_from_id == emp
    assert a.sudo().activity_ids, "nobody was told to recover it"
    # The block survives the holder being cleared.
    assert a.asset_tag in refused(c.env, lambda: ex._fix_tick("clearance_assets"))
    a.with_user(c.agent).action_recover()
    assert a.state == "in_stock" and not a.recovery_from_id
    ex._fix_tick("clearance_assets")


def test_a12f_handoff_write_off_also_lifts_the_block(c):
    emp = c.env["hr.employee"].sudo().create({"name": "M66F Leaver 3"})
    a = allocated(c, emp)
    ex = _exit(c, emp)
    a.sudo().write({"assigned_to_id": False})
    assert a.state == "recovery_due"
    assert refused(c.env, lambda: ex._fix_tick("clearance_assets"))
    retired(c, a)
    assert a.state == "retired" and not a.recovery_from_id
    ex._fix_tick("clearance_assets")


def test_a12f_handoff_a_late_allocation_blocks_action_clear(c):
    emp = c.env["hr.employee"].sudo().create({"name": "M66F Leaver 4"})
    ex = _exit(c, emp)
    ex._fix_tick("clearance_assets")
    a = allocated(c, emp)
    # M21 capture pass 2 (FR-HCM-036): HR's clearance waits for the leaver's
    # knowledge handover, accepted by the successor - arranged as M21's own
    # tests do, so this test reaches the asset rule it is about
    successor = c.env["hr.employee"].sudo().create({"name": "M66F Successor 4"})
    handover = c.env["fix.hr.exit.handover"].create(
        {"exit_id": ex.id, "successor_id": successor.id, "open_work": "none"}
    )
    handover.action_hand_over()
    handover.action_accept()
    for tick in ("clearance_it", "clearance_finance", "clearance_hr"):
        ex._fix_tick(tick)
    message = refused(c.env, lambda: ex.action_clear())
    assert message and a.asset_tag in message


# ---- asset -> M06, through the real publisher and relay
def test_a12f_n_m66_3_real_retirement_event_reaches_the_m06_document(c):
    a = asset(c)
    att = c.env["ir.attachment"].create(
        {"name": "wc", "datas": b"ZGVzdHJveA==", "mimetype": "text/plain"}
    )
    doc = c.env["fix.document"].create(
        {
            "name": "Warranty",
            "attachment_id": att.id,
            "document_type": "asset_document",
            "res_model": "fix.itsm.asset",
            "res_id": a.id,
        }
    )
    retired(c, a)
    c.env["fix.event.outbox"].sudo().cron_relay()
    consumer = (
        c.env["fix.event.consumer"].sudo().search([("method", "=", "consume_itsm_asset_retired")])
    )
    delivery = (
        c.env["fix.event.consumer.delivery"]
        .sudo()
        .search([("subscription_id", "=", consumer.id)], order="id desc", limit=1)
    )
    assert delivery.state == "done", delivery.last_error
    bodies = " ".join(str(m.body or "") for m in doc.sudo().message_ids)
    assert "destruction review" in bodies and a.asset_tag in bodies
    # Idempotent on the event id.
    event = delivery.event_id
    assert c.env["fix.document"].sudo().consume_itsm_asset_retired(event._relay_event_dict()) == 0


# ============================================================ M66-11 licences
def test_a12f_m66_11_seats_are_records_and_utilisation_is_measured(c, p03):
    x = licence(c, seats_owned=2)
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.licence",
        ids=[x.id],
        method="action_assign_seat",
        kwargs={"employee": c.plain_e.name},
    )
    assert out.get("success"), out
    assert x.seats_assigned == 1 and x.utilisation_pct == 50.0
    seat = x.seat_ids
    assert seat.employee_id == c.plain_e and seat.assigned_by_id == c.agent
    out = p03.action(model="fix.itsm.licence.seat", ids=[seat.id], method="action_revoke")
    assert out.get("success"), out
    assert x.seats_assigned == 0 and x.utilisation_pct == 0.0
    assert refused(c.env, lambda: x.with_user(c.agent).write({"seats_assigned": 9}))
    assert refused(c.env, lambda: licence(c, seats_assigned=15))
    p03.as_user(c.agent)
    assert "error" in p03.write(
        model="fix.itsm.licence", record_id=x.id, values={"seats_assigned": 9}
    )


def test_a12f_bru_its_16_no_seat_without_an_entitlement(c):
    x = licence(c, seats_owned=1)
    x.with_user(c.agent).action_assign_seat(employee=c.plain_e.id)
    assert "no free seat" in refused(
        c.env, lambda: x.with_user(c.agent).action_assign_seat(employee=c.plain2_e.id)
    )
    ghost = c.env["hr.employee"].create({"name": "M66F Ghost", "active": False})
    y = licence(c, seats_owned=5)
    assert refused(c.env, lambda: y.with_user(c.agent).action_assign_seat(employee=ghost.id))


def test_a12f_bru_its_17_overuse_is_an_exception_the_installer_cannot_close(c, p03):
    x = licence(c, seats_owned=1)
    x.with_user(c.agent).action_assign_seat(employee=c.plain_e.id)
    p03.as_user(c.agent)
    out = p03.action(
        model="fix.itsm.licence",
        ids=[x.id],
        method="action_record_overuse",
        kwargs={"employee": c.plain2_e.id},
    )
    assert out.get("success"), out
    assert x.compliance_state == "over" and x.seats_assigned == 2 and x.utilisation_pct == 200.0
    exc = x.exception_ids
    assert (
        len(exc) == 1
        and exc.state == "open"
        and exc.seats_over == 1
        and exc.installer_id == c.agent
    )
    assert exc.remediation_due > c.today
    # Still over: nobody closes it. Then the installer may not, a colleague may.
    p03.as_user(c.agent2)
    out = p03.action(
        model="fix.itsm.licence.exception",
        ids=[exc.id],
        method="action_close_exception",
        kwargs={"closure_note": "x"},
    )
    assert not out["success"] and "still over-allocated" in out["error"]
    x.seat_ids.filtered("over_entitlement").with_user(c.agent).action_revoke()
    assert x.compliance_state == "ok"
    assert "another person" in refused(
        c.env, lambda: exc.with_user(c.agent).action_close_exception(closure_note="done")
    )
    assert refused(c.env, lambda: exc.with_user(c.agent2).action_close_exception())
    exc.with_user(c.agent2).action_close_exception(closure_note="Removed the install")
    assert exc.state == "closed" and exc.closed_by_id == c.agent2


def test_a12f_m66_11_state_follows_the_clock_by_a_daily_cron(c):
    cron = c.env.ref("cd_itsm.ir_cron_itsm_licence_refresh")
    assert cron.active
    assert (cron.interval_number, cron.interval_type) == (1, "days")
    x = licence(c, renewal_on=c.today + timedelta(days=40))
    assert x.state == "active"
    c.env.flush_all()
    # The clock moves; only the cron can tell the stored state.
    c.env.cr.execute(
        "UPDATE fix_itsm_licence SET renewal_on = %s WHERE id = %s",
        (c.today - timedelta(days=1), x.id),
    )
    x.invalidate_recordset()
    assert x.state == "active", "setup: stored state did not stay stale"
    c.env["fix.itsm.licence"].sudo().cron_refresh_licences()
    assert x.state == "expired"


def test_a12f_m66_11_the_shipped_cron_action_flips_it_when_the_clock_moves(c):
    """R03's proof, without method_direct_trigger: that runs on a fresh cursor, which
    cannot see a licence created inside the test's transaction."""
    x = licence(c, renewal_on=c.today + timedelta(days=40))
    assert x.state == "active"
    c.env.flush_all()
    later = c.today + timedelta(days=60)
    with patch("odoo.fields.Date.context_today", lambda rec, timestamp=None: later):
        c.env.ref("cd_itsm.ir_cron_itsm_licence_refresh").sudo().ir_actions_server_id.run()
    x.invalidate_recordset()
    assert x.state == "expired"


def test_a12f_m66_11_state_is_not_forgeable(c):
    x = licence(c, renewal_on=c.today - timedelta(days=30))
    assert x.state == "expired"
    assert refused(c.env, lambda: x.with_user(c.agent).write({"state": "active"}))
    assert refused(c.env, lambda: x.with_user(c.plain).write({"seats_owned": 99}))
    assert refused(c.env, lambda: licence(c, seats_owned=-5))


def test_a12f_m66_11_typed_legacy_figure_is_shown_as_declared(c):
    """A pre-seat row: its figure is not measured, still counts, and can go over."""
    x = (
        c.env["fix.itsm.licence"]
        .sudo()
        .create({"name": "Legacy", "vendor": "V", "seats_owned": 10, "seats_assigned": 10})
    )
    assert x.seats_declared == 10 and x.seats_assigned == 0 and x.utilisation_pct == 100.0
    assert "no free seat" in refused(
        c.env, lambda: x.with_user(c.agent).action_assign_seat(employee=c.plain_e.id)
    )


# ============================================================ hand-offs, M66-13
def test_a12f_handoff_dead_letter_becomes_one_incident_through_the_real_relay(c):
    event = (
        c.env["fix.event.outbox"]
        .sudo()
        .create({"event_type": "m66f.test", "aggregate": "x", "aggregate_id": 1, "payload": "{}"})
    )
    sub = c.env["fix.event.consumer"].sudo().search([], limit=1)
    delivery = (
        c.env["fix.event.consumer.delivery"]
        .sudo()
        .create(
            {
                "subscription_id": sub.id,
                "event_id": event.id,
                "state": "dead",
                "attempts": 3,
                "last_error": "boom",
                "delivered_at": fields.Datetime.now() - timedelta(hours=3),
            }
        )
    )
    Tk = c.env["fix.itsm.ticket"].sudo()
    # A fresh dead letter is not yet an incident: the limit is an hour.
    young = (
        c.env["fix.event.consumer.delivery"]
        .sudo()
        .create(
            {
                "subscription_id": c.env["fix.event.consumer"].sudo().search([], limit=2)[-1].id,
                "event_id": event.id,
                "state": "dead",
                "attempts": 3,
                "last_error": "fresh",
                "delivered_at": fields.Datetime.now(),
            }
        )
    )
    created = Tk.cron_dead_letter_incidents()
    letter = c.env["fix.event.dlq"].sudo().search([("delivery_id", "=", delivery.id)])
    assert letter and "fix.event.dlq,%d" % letter.id in created.mapped("source_ref")
    fresh = c.env["fix.event.dlq"].sudo().search([("delivery_id", "=", young.id)])
    assert "fix.event.dlq,%d" % fresh.id not in created.mapped("source_ref")
    mine = Tk.search([("source_ref", "=", "fix.event.dlq,%d" % letter.id)])
    assert len(mine) == 1 and mine.ticket_type == "incident" and not mine.requester_id
    assert mine.priority == "high" and "boom" in mine.description
    # No second incident, by cron or by the relay's own unhealthy event.
    Tk.cron_dead_letter_incidents()
    assert Tk.search_count([("source_ref", "=", "fix.event.dlq,%d" % letter.id)]) == 1
    assert c.env.ref("cd_itsm.ir_cron_itsm_dead_letter_incidents").active
    consumer = c.env.ref("cd_itsm.consumer_itsm_relay_unhealthy")
    assert consumer.event_type == "outbox.relay_unhealthy"
    Tk.consume_relay_unhealthy({"event_id": "x", "payload": {}})
    assert Tk.search_count([("source_ref", "=", "fix.event.dlq,%d" % letter.id)]) == 1


def test_a12f_handoff_dead_webhook_becomes_one_incident_through_the_real_dispatcher(c, monkeypatch):
    """The webhook dispatcher's own dead letter, reached by failing three real attempts
    (M28), raises an incident like a relay dead letter does."""
    from odoo.addons.cd_itsm.models import fix_integration_dispatch as dispatch

    monkeypatch.setattr(dispatch, "_http_post", lambda url, body, headers, timeout: 503)
    monkeypatch.setenv("FIX_VAULT_WEBHOOKS_M66F_V1", "local-test-signing-value")
    monkeypatch.setenv("FIX_ENV", "local")
    Params = c.env["ir.config_parameter"].sudo()
    Params.set_param("fix.integration.webhook_allowlist", "localhost")
    Params.set_param("fix.integration.dispatch_enabled", "1")
    consumer = (
        c.env["fix.api.consumer"]
        .sudo()
        .create({"name": "M66F Consumer", "key_ref": "vault://keys/m66f/v1"})
    )
    topic = c.env["fix.event.topic"].sudo().create({"code": "m66f.hook", "name": "m66f.hook"})
    sub = (
        c.env["fix.event.subscription"]
        .sudo()
        .create(
            {
                "consumer_id": consumer.id,
                "topic_id": topic.id,
                "endpoint_url": "https://localhost:9443/in",
                "secret_ref": "vault://webhooks/m66f/v1",
            }
        )
    )
    c.env["fix.event.outbox"].sudo().emit("m66f.hook", "x", 1, {"a": 1})
    Delivery = c.env["fix.webhook.delivery"].sudo()
    Delivery.cron_dispatch_webhooks()
    row = Delivery.search([("subscription_id", "=", sub.id)])
    for _retry in range(2):
        row.write({"next_attempt_at": fields.Datetime.now() - timedelta(seconds=1)})
        Delivery.cron_dispatch_webhooks()
    assert row.state == "dead"
    letter = c.env["fix.event.dlq"].sudo().search([("webhook_delivery_id", "=", row.id)])
    assert letter.state == "pending" and not letter.delivery_id
    ref = "fix.event.dlq,%d" % letter.id
    Tk = c.env["fix.itsm.ticket"].sudo()
    Tk.cron_dead_letter_incidents()
    assert not Tk.search_count([("source_ref", "=", ref)]), "younger than the limit"
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_event_dlq SET created_at = created_at - interval '3 hours' WHERE id = %s",
        (letter.id,),
    )
    c.env.invalidate_all()
    assert ref in Tk.cron_dead_letter_incidents().mapped("source_ref")
    Tk.cron_dead_letter_incidents()
    assert Tk.search_count([("source_ref", "=", ref)]) == 1


def test_a12f_handoff_seeded_dlq_row_with_no_delivery_raises_no_incident(c):
    row = (
        c.env["fix.event.dlq"]
        .sudo()
        .create(
            {
                "topic_code": "seed.row",
                "payload": "{}",
                "reason": "seeded",
                "created_at": fields.Datetime.now() - timedelta(days=3),
            }
        )
    )
    created = c.env["fix.itsm.ticket"].sudo().cron_dead_letter_incidents()
    assert "fix.event.dlq,%d" % row.id not in created.mapped("source_ref")


def test_a12f_m66_13_real_relay_tells_a_person_about_a_new_ticket(c):
    t = ticket(c)
    c.env["fix.event.outbox"].sudo().cron_relay()
    assert "Handed to the service desk queue" in " ".join(
        str(m.body or "") for m in t.sudo().message_ids
    )
    owners = t.sudo().activity_ids.mapped("user_id")
    assert owners and owners[0].has_group(AGENT)


def test_a12f_m66_13_real_relay_asks_the_requester_to_confirm(c):
    t = working(c)
    t.with_user(c.agent).action_resolve(resolution="done")
    c.env["fix.event.outbox"].sudo().cron_relay()
    assert t.sudo().activity_ids.filtered(lambda a: a.user_id == c.plain)


def test_a12f_m66_13_no_claim_of_a_release_hand_off(c):
    ch = approved_change(c, implementer_id=c.agent2_e.id)
    ch.with_user(c.agent2).action_implement()
    Rel = c.env["fix.platform.release"].sudo()
    before = Rel.search_count([])
    c.env["fix.event.outbox"].sudo().cron_relay()
    body = " ".join(str(m.body or "") for m in ch.sudo().message_ids)
    assert "handed to the platform release register" not in body.lower()
    assert "Implemented event" in body
    assert Rel.search_count([]) == before, "a change does not invent a release"


def test_a12f_public_cron_bodies_refuse_a_plain_caller(c):
    for model, method in (
        ("fix.itsm.ticket", "cron_escalate_sla"),
        ("fix.itsm.ticket", "cron_ticket_housekeeping"),
        ("fix.itsm.ticket", "cron_dead_letter_incidents"),
        ("fix.itsm.change", "cron_chase_pir"),
        ("fix.itsm.problem", "cron_problem_verification"),
        ("fix.itsm.licence", "cron_refresh_licences"),
    ):
        recs = c.env[model].with_user(c.agent)
        assert refused(c.env, getattr(recs, method)), method


def test_a12f_every_new_cron_is_shipped(c):
    for xmlid, model in (
        ("cd_itsm.ir_cron_itsm_ticket_housekeeping", "fix.itsm.ticket"),
        ("cd_itsm.ir_cron_itsm_dead_letter_incidents", "fix.itsm.ticket"),
        ("cd_itsm.ir_cron_itsm_chase_pir", "fix.itsm.change"),
        ("cd_itsm.ir_cron_itsm_problem_verification", "fix.itsm.problem"),
        ("cd_itsm.ir_cron_itsm_licence_refresh", "fix.itsm.licence"),
    ):
        cron = c.env.ref(xmlid)
        assert cron.model_id.model == model and cron.active
        method = re.search(r"model\.(cron_[a-z_]+)\(\)", cron.code).group(1)
        assert callable(getattr(c.env[model], method))
