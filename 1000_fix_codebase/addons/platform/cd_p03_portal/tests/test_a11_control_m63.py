# A11 control suite — M63 Workflow & Approval Engine (cd_workflow_engine).
#
# The audit's executable probes, kept as the regression suite the report's P3
# asked for: a pytest PASS means the CONTROL HELD; a FAIL means a GAP crept
# back (the assertion message starts "GAP:" and names it). Everything runs
# inside the `odoo_env` fixture, which rolls the transaction back. Attacks
# run as NON-ADMIN users created in the transaction (base.group_user + an
# operating unit; DOFA tier / sales groups only where the step needs that
# role).
#
# Post-remediation note (E1-E4, G9): the rule book is DoA-administrator
# only, delegations are policy-checked, malformed conditions are refused at
# creation and dated rows version instead of editing in place. The six tests
# the remediation made stronger than the probe assumed (self-appointed
# delegates, plain-user matrix rows) now assert BOTH layers: the attack
# entry is refused, and the deeper control still holds for legitimate setup.
import os
import types
from datetime import date, datetime, timedelta

import pytest
import pytz
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
T1 = "cd_entity_config.group_dofa_tier_1"
T2 = "cd_entity_config.group_dofa_tier_2"
SALES = "sales_team.group_sale_salesman"
SALES_MGR = "sales_team.group_sale_manager"
SALES_ALL = (
    "sales_team.group_sale_salesman_all_leads"  # salesperson who sees all leads, NOT a manager
)
PWN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__a11_m63_pwn.txt")


class Ctx:
    pass


def _add_missing_columns(env):
    cr = env.cr
    cr.execute(
        "select table_name, column_name from information_schema.columns where table_schema='public'"
    )
    have = {}
    for t, col in cr.fetchall():
        have.setdefault(t, set()).add(col)
    added = []
    for _name, model in env.registry.items():
        if model._abstract or not model._auto or model._table not in have:
            continue
        for fname, f in model._fields.items():
            if f.store and f.column_type and fname not in have[model._table]:
                cr.execute(
                    'ALTER TABLE "%s" ADD COLUMN "%s" %s' % (model._table, fname, f.column_type[1])
                )
                have[model._table].add(fname)
                added.append("%s.%s" % (model._table, fname))
    return added


def _user(env, login, groups=(), employee=True):
    Users = env["res.users"].with_context(no_reset_password=True)
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    user = Users.create(
        {
            "name": login,
            "login": login,
            "group_ids": [(6, 0, gids)],
            "assigned_operating_unit_ids": [(6, 0, ou.ids)],
            "default_operating_unit_id": ou.id,
        }
    )
    if employee:
        env["hr.employee"].create({"name": login, "user_id": user.id})
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.added_columns = _add_missing_columns(env)
    x.ou = env["operating.unit"].search([], limit=1)
    x.clerk = _user(env, "a11m63_clerk")  # raises the record
    x.clerk2 = _user(env, "a11m63_clerk2")
    x.p = _user(env, "a11m63_plain")  # the attacker: base.group_user + OU only
    x.t1 = _user(env, "a11m63_t1", [T1])
    x.t1b = _user(env, "a11m63_t1b", [T1])
    x.t2 = _user(env, "a11m63_t2", [T2])
    x.customer = env["res.partner"].create({"name": "A11 M63 Customer", "phone": "01700006301"})
    x.accomplice = env["res.partner"].create({"name": "A11 M63 Accomplice", "phone": "01700006399"})
    return x


def complaint(c, user=None, amount=800.0, **kw):
    """A service-recovery concession: <=1,000 Tier 1, <=5,000 Tier 2, <=10,000 Tier 3, else T4."""
    vals = {
        "name": "A11M63-%s" % (user or c.clerk).login,
        "customer_id": c.customer.id,
        "operating_unit_id": c.ou.id,
        "description": "a11 m63 probe",
        "severity": "minor",
        "concession_amount": amount,
        "concession_type": "refund",
        "dofa_justification": "Repeat failure on the same repair.",
    }
    vals.update(kw)
    return c.env["fix.complaint"].with_user(user or c.clerk).create(vals)


def task_of(rec, user):
    return rec.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == user
    )


def assignees(rec):
    return rec.approval_request_id.task_ids.filtered(lambda t: t.state == "pending").mapped(
        "assigned_user_id"
    )


def overdue(req):
    req.task_ids.filtered(lambda t: t.state == "pending")._guarded().write(
        {"due_at": fields.Datetime.now() - timedelta(hours=2)}
    )


def run_cron(env):
    """The real ir.cron record's server action (not a direct method call)."""
    cron = env.ref("cd_workflow_engine.ir_cron_approval_escalate_overdue")
    cron.sudo().ir_actions_server_id.run()


def matrix_row(env, user=None, **kw):
    vals = {
        "name": "A11M63 rule",
        "decision_domain": "concession",
        "res_model": "fix.complaint",
        "approval_policy": "any",
        "sla_hours": 24,
        "max_escalations": 1,
        "final_action": "keep",
    }
    vals.update(kw)
    Model = env["fix.approval.matrix"]
    return (Model.with_user(user) if user else Model).create(vals)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    as_user(c.p)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw), as_user=as_user
        )
    finally:
        g.request, s.request = old_g, old_s


# =================================================================== tier resolution
def test_m63_01_s1_tier_stored_for_plain_creator(c):
    """A03 S1 (depends_context uid): a concession raised by a plain user must store its tier."""
    rec = complaint(c, amount=800)
    rec.flush_recordset()
    c.env.cr.execute("select dofa_tier_required from fix_complaint where id=%s", (rec.id,))
    stored = c.env.cr.fetchone()[0]
    assert stored == "tier_1", (
        "GAP: plain-user concession stored tier %r (expected tier_1)" % stored
    )


def test_m63_02_direct_press_refused_on_routed_model(c):
    """Decide from outside the inbox: a Tier-1 holder presses Approve on the record."""
    rec = complaint(c)
    with pytest.raises(UserError, match="inbox"):
        rec.with_user(c.t1).action_approve_concession()
    assert not rec.dofa_approved


def test_m63_03_no_approver_fails_closed(c):
    """A Tier-4 concession (BDT 20,000) when Tier 4 has no holders: refuse, never auto-approve."""
    rec = complaint(c, amount=20000)
    with pytest.raises(UserError, match="Appoint an approver"):
        rec.with_user(c.clerk).action_request_approval()
    with pytest.raises(REFUSED):
        rec._concession_denial()


# =================================================================== the inbox decision
def test_ref_m63_04_inbox_decision_runs_in_approver_env(c, monkeypatch):
    """Reference + A03 fourth-pass fix: the apply method runs as the approver, NOT env.su."""
    seen = {}
    cls = type(c.env["fix.complaint"])
    orig = cls.action_approve_concession

    def spy(self):
        seen.update(su=self.env.su, uid=self.env.uid, guard_open=self._fix_guard_open())
        return orig(self)

    monkeypatch.setattr(cls, "action_approve_concession", spy)
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    assert set(assignees(rec)) == {c.t1, c.t1b}, assignees(rec).mapped("login")
    task_of(rec, c.t1).with_user(c.t1).action_approve(comment="ok")
    assert seen == {"su": False, "uid": c.t1.id, "guard_open": False}, (
        "GAP: inbox apply ran with %r (sudo / open guard inside the decision)" % seen
    )
    assert rec.dofa_approved and rec.dofa_approved_by == c.t1 and rec.approval_state == "approved"
    events = rec.approval_request_id.history_ids.sorted("id").mapped("event")
    assert events == ["requested", "task_approved", "approved"], events


def test_m63_05_reject_runs_in_approver_env(c, monkeypatch):
    seen = {}
    cls = type(c.env["fix.complaint"])
    orig = cls._approval_on_rejected

    def spy(self, comment):
        seen.update(su=self.env.su, uid=self.env.uid)
        return orig(self, comment)

    monkeypatch.setattr(cls, "_approval_on_rejected", spy)
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    with pytest.raises(UserError, match="why"):
        task_of(rec, c.t1).with_user(c.t1).action_reject(comment="  ")
    task_of(rec, c.t1).with_user(c.t1).action_reject(comment="not upheld")
    assert seen == {"su": False, "uid": c.t1.id}, "GAP: reject hook ran with %r" % seen
    assert rec.approval_state == "rejected" and not rec.dofa_approved


def test_m63_06_requester_excluded_from_routing(c):
    """A Tier-1 holder who did not create the record requests it: they must not be routed it."""
    rec = complaint(c)
    rec.with_user(c.t1).action_request_approval()
    assert c.t1 not in assignees(rec), "GAP: requester routed their own request"
    assert c.clerk not in assignees(rec)


def test_m63_07_cannot_decide_someone_elses_task(c, p03):
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task = task_of(rec, c.t1)
    for user in (c.p, c.t1b, c.clerk):
        with pytest.raises(UserError, match="assignee"):
            task.with_user(user).action_approve()
    # P03 action path, as the plain user
    res = p03.action(model="fix.workflow.task", ids=[task.id], method="action_approve")
    assert not res.get("success"), "GAP: P03 action approved a task assigned to t1: %r" % res
    assert not rec.dofa_approved


def test_m63_08_cannot_approve_twice(c):
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    t1_task, t1b_task = task_of(rec, c.t1), task_of(rec, c.t1b)
    t1_task.with_user(c.t1).action_approve()
    for task, user in ((t1_task, c.t1), (t1b_task, c.t1b)):
        with pytest.raises(UserError):
            task.with_user(user).action_approve()
    assert len(rec.approval_request_id.history_ids.filtered(lambda h: h.event == "approved")) == 1


def test_m63_09_amount_change_voids_pending(c):
    """Void-on-change: the requester raises the amount while pending; the old task must die."""
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    req, task = rec.approval_request_id, task_of(rec, c.t1)
    rec.with_user(c.clerk).write({"concession_amount": 950})
    assert req.state == "voided" and rec.approval_state == "none", (req.state, rec.approval_state)
    with pytest.raises(UserError):
        task.with_user(c.t1).action_approve()
    assert not rec.dofa_approved


def test_m63_10_amount_change_by_system_voids_pending(c):
    """The same change made by superuser code (cron / service) while pending."""
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    req = rec.approval_request_id
    rec.sudo().write({"concession_amount": 990})
    assert req.state == "voided", "GAP: a system-side amount change left the request %s" % req.state


def test_m63_11_payee_change_after_approval_not_voided(c):
    """S4 for non-amount terms: after approval the clerk swaps the customer the refund goes to."""
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task_of(rec, c.t1).with_user(c.t1).action_approve()
    try:
        rec.with_user(c.clerk).write(
            {"customer_id": c.accomplice.id, "concession_type": "discount"}
        )
    except REFUSED:
        return
    assert not (rec.dofa_approved and rec.concession_approved), (
        "GAP: approval of a BDT 800 refund to %s still stands after the clerk re-pointed it to %s "
        "(type now %s): approval_state=%s dofa_approved=%s concession_approved=%s"
        % (
            c.customer.name,
            rec.customer_id.name,
            rec.concession_type,
            rec.approval_state,
            rec.dofa_approved,
            rec.concession_approved,
        )
    )


def test_m63_12_quorum_all_first_vote_already_approves(c):
    """Policy 'all' (unanimous) on the rule: after ONE of two votes the record must not be approved."""
    matrix_row(c.env, approval_policy="all")  # admin configuration (reference setup)
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    assert rec.approval_request_id.approval_policy == "all"
    task_of(rec, c.t1).with_user(c.t1).action_approve()
    req = rec.approval_request_id
    passed_gate = True
    try:
        rec._concession_denial()
    except REFUSED:
        passed_gate = False
    assert not rec.dofa_approved and not passed_gate, (
        "GAP: unanimous rule, 1 of 2 votes cast (request %s, approval_state %s) yet dofa_approved=%s, "
        "concession_approved=%s and the closure gate %s"
        % (
            req.state,
            rec.approval_state,
            rec.dofa_approved,
            rec.concession_approved,
            "PASSES" if passed_gate else "refuses",
        )
    )


def test_m63_13_quorum_all_later_reject_leaves_approval(c):
    matrix_row(c.env, approval_policy="all")
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task_of(rec, c.t1).with_user(c.t1).action_approve()
    task_of(rec, c.t1b).with_user(c.t1b).action_reject(comment="I do not agree")
    assert rec.approval_request_id.state == "rejected"
    assert not (rec.dofa_approved or rec.concession_approved), (
        "GAP: request REJECTED by the second approver, but the record keeps dofa_approved=%s, "
        "concession_approved=%s (approval_state=%s): the closure gate will pay it"
        % (rec.dofa_approved, rec.concession_approved, rec.approval_state)
    )


# =================================================================== escalation / SLA
def test_m63_14_escalation_routes_request_to_its_requester(c):
    """The requester (a Tier-2 manager, not the creator) asks for approval of a Tier-1 concession.
    Routing excludes them; the overdue escalation (cron, superuser env) must exclude them too."""
    rec = complaint(c)
    rec.with_user(c.t2).action_request_approval()
    req = rec.approval_request_id
    assert c.t2 not in assignees(rec)
    overdue(req)
    run_cron(c.env)  # 1st pass: reminder
    overdue(req)
    run_cron(c.env)  # 2nd pass: escalate to Tier 2
    own = task_of(rec, c.t2)
    if not own:
        return
    try:
        own.with_user(c.t2).action_approve()
    except REFUSED:
        return
    kpi = c.env["fix.approval.request"].approval_kpis()["approver_is_creator"]
    raise AssertionError(
        "GAP: escalation routed %s to its own requester %s, who approved it (dofa_approved_by=%s); "
        "the 'approver = creator' KPI still reads %s"
        % (req.name, c.t2.login, rec.dofa_approved_by.login, kpi)
    )


def test_m63_15_escalation_cron_is_real_and_escalates(c):
    """The escalation method has an active ir.cron and its server action escalates."""
    cron = c.env.ref("cd_workflow_engine.ir_cron_approval_escalate_overdue")
    assert cron.active and cron.model_id.model == "fix.approval.request"
    assert "cron_escalate_overdue" in (cron.code or cron.ir_actions_server_id.code)
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    req = rec.approval_request_id
    overdue(req)
    run_cron(c.env)
    assert req.reminded_at
    overdue(req)
    run_cron(c.env)
    assert req.escalation_level == 1 and task_of(rec, c.t2), "no escalation to Tier 2"
    assert {"reminded", "escalated"} <= set(req.history_ids.mapped("event"))


def test_m63_16_no_next_tier_keeps_pending_not_approved(c):
    """Escalation with nobody above: the request must stay undecided, never auto-approve."""
    rec = complaint(c, amount=4000)  # tier 2; nobody holds tier 3
    rec.with_user(c.clerk).action_request_approval()
    req = rec.approval_request_id
    for _ in range(3):
        overdue(req)
        run_cron(c.env)
    assert req.state == "pending" and not rec.dofa_approved and req.final_action_done
    assert "expired" in req.history_ids.mapped("event")


def _reference_due(start_utc, hours, windows, holidays, tz="Asia/Dhaka"):
    """Independent minute-stepping reference: working minutes in `windows`
    {weekday: (from_h, to_h)} local time, skipping `holidays` (dates)."""
    zone = pytz.timezone(tz)
    cur = pytz.utc.localize(start_utc).astimezone(zone).replace(tzinfo=None)
    need = int(round(hours * 60))
    while need > 0:
        w = windows.get(cur.weekday())
        if w and cur.date() not in holidays and w[0] * 60 <= cur.hour * 60 + cur.minute < w[1] * 60:
            need -= 1
        cur += timedelta(minutes=1)
    return zone.localize(cur).astimezone(pytz.utc).replace(tzinfo=None)


def _bd_calendar(env, holiday=None):
    cal = env["fix.working.calendar"].create({"name": "A11M63 Sun-Thu", "timezone": "Asia/Dhaka"})
    for wd in ("sun", "mon", "tue", "wed", "thu"):
        env["fix.working.calendar.line"].create(
            {"calendar_id": cal.id, "weekday": wd, "hour_from": 9.0, "hour_to": 17.0}
        )
    if holiday:
        env["fix.working.calendar.holiday"].create(
            {
                "calendar_id": cal.id,
                "name": "Probe holiday",
                "date_from": holiday,
                "date_to": holiday,
            }
        )
    return cal


BD_WINDOWS = {6: (9, 17), 0: (9, 17), 1: (9, 17), 2: (9, 17), 3: (9, 17)}  # Sun..Thu


def test_m63_17_business_hours_maths(c):
    """W2: Thursday 16:00 Dhaka + 8 working hours = Sunday 16:00 (Fri/Sat weekend);
    with Sunday a holiday = Monday 16:00; raised Thursday 17:30 = Sunday 09:00 + 8h = 17:00."""
    Req = c.env["fix.approval.request"]
    cal = _bd_calendar(c.env)
    cal_h = _bd_calendar(c.env, holiday=date(2026, 11, 8))
    thu_1600 = datetime(2026, 11, 5, 10, 0)  # UTC = 16:00 Dhaka (Thursday)
    thu_1730 = datetime(2026, 11, 5, 11, 30)
    cases = [
        (thu_1600, 8, cal, datetime(2026, 11, 8, 10, 0), set()),
        (thu_1600, 8, cal_h, datetime(2026, 11, 9, 10, 0), {date(2026, 11, 8)}),
        (thu_1730, 8, cal, datetime(2026, 11, 8, 11, 0), set()),
        (thu_1600, 24, cal, None, set()),
    ]
    bad = []
    for start, hrs, calendar, expected, hol in cases:
        got = Req._approval_add_business_hours(start, hrs, calendar)
        ref = _reference_due(start, hrs, BD_WINDOWS, hol)
        if (expected and got != expected) or got != ref:
            bad.append((str(start), hrs, calendar.name, str(got), str(expected or ref)))
    assert not bad, "GAP: business-hours SLA wrong: %r" % bad


def test_m63_18_business_hours_on_the_proper_path(c):
    """A rule with a working calendar and an 8 h SLA: the inbox task's due_at must be 8 working hours."""
    cal = _bd_calendar(c.env)
    matrix_row(c.env, sla_hours=8, calendar_id=cal.id)
    rec = complaint(c)
    before = fields.Datetime.now()
    rec.with_user(c.clerk).action_request_approval()
    due = task_of(rec, c.t1).due_at
    ref = _reference_due(before, 8, BD_WINDOWS, set())
    assert abs((due - ref).total_seconds()) <= 120, "GAP: task due %s, 8 working hours = %s" % (
        due,
        ref,
    )
    # The KPI 'pending over 72 h' and cycle_hours stay wall-clock (documented, not a pass/fail here).


# =================================================================== substitution / delegation
def _sub(env, absent, delegate, user=None, **kw):
    vals = {
        "absent_approver_id": absent.employee_ids[:1].id,
        "delegate_id": delegate.employee_ids[:1].id,
        "start_date": fields.Date.context_today(env["fix.approval.substitution"]),
        "end_date": fields.Date.context_today(env["fix.approval.substitution"]) + timedelta(days=5),
        "reason": "probe",
    }
    vals.update(kw)
    Model = env["fix.approval.substitution"]
    return (Model.with_user(user) if user else Model).create(vals)


def test_m63_19_plain_user_delegates_tier_authority_to_self(c):
    """A plain user (no tier) creates 'T1 is out of office, I am the delegate', activates it,
    then decides a colleague's concession on T1's authority."""
    try:
        sub = _sub(c.env, c.t1, c.p, user=c.p)
        sub.with_user(c.p).action_activate()
    except REFUSED:
        return
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task = task_of(rec, c.p)
    if not task:
        return
    try:
        task.with_user(c.p).action_approve()
    except REFUSED:
        return
    raise AssertionError(
        "GAP: plain user %s self-appointed as T1's delegate (%s, created+activated by himself) and "
        "approved %s: dofa_approved_by=%s on behalf of %s, T1 never consented"
        % (c.p.login, sub.name, rec.name, rec.dofa_approved_by.login, task.on_behalf_of_id.login)
    )


def test_m63_20_substitution_born_active_and_backdated(c):
    """State and dates are typed: born 'active' (no Activate step), back-dated to January."""
    try:
        sub = _sub(c.env, c.t2, c.p, user=c.p, state="active", start_date=date(2026, 1, 1))
    except REFUSED:
        return
    assert sub.state != "active", (
        "GAP: plain user created %s already 'active', back-dated to %s, delegating %s's Tier-2 "
        "authority to himself" % (sub.name, sub.start_date, c.t2.login)
    )


def test_m63_21_substitution_via_p03(c, p03):
    res = p03.write(
        model="fix.approval.substitution",
        values={
            "absent_approver_id": c.t1.employee_ids[:1].id,
            "delegate_id": c.p.employee_ids[:1].id,
            "start_date": str(date(2026, 1, 1)),
            "end_date": str(date(2027, 12, 31)),
            "state": "active",
        },
    )
    if res.get("error"):
        return
    sub = c.env["fix.approval.substitution"].browse(res["id"])
    assert sub.state != "active", (
        "GAP: /p03/model/write created %s as plain user, state=%s, delegating T1 to himself until %s"
        % (sub.name, sub.state, sub.end_date)
    )


def test_m63_22_expired_substitution_still_decides(c):
    """A legitimate delegation ends after routing; the delegate must lose the task.

    Post-E2: the delegate must himself hold the tier, so the legitimate
    delegation is t1 -> t1b (both Tier 1)."""
    sub = _sub(c.env, c.t1, c.t1b)
    sub.action_activate()
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task = task_of(rec, c.t1b)
    assert task and task.on_behalf_of_id == c.t1, "routing did not honour the delegation"
    sub.action_expire()
    with pytest.raises(REFUSED):
        task.with_user(c.t1b).action_approve()
    assert not rec.dofa_approved, (
        "GAP: substitution %s is %s (ended %s) yet its delegate %s approved %s on T1's authority"
        % (sub.name, sub.state, sub.end_date, c.t1b.login, rec.name)
    )


def test_m63_23_delegate_cannot_be_creator(c):
    """A delegation to the record's own creator must not let the creator decide.

    Post-E2 the delegate must hold the tier, so the creator here is the
    second Tier-1 holder."""
    sub = _sub(c.env, c.t1, c.t1b)
    sub.action_activate()
    rec = complaint(c, user=c.t1b)
    rec.with_user(c.t1b).action_request_approval()
    assert c.t1b not in assignees(rec), (
        "GAP: the record's own creator %s was routed his own record's approval via %s"
        % (c.t1b.login, sub.name)
    )


def test_m63_41_delegate_refused_when_absent_loses_tier(c):
    """Authority is re-read at decision: the absent approver loses Tier 1 after routing."""
    sub = _sub(c.env, c.t1, c.t1b)
    sub.action_activate()
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task = task_of(rec, c.t1b)
    assert task
    c.t1.write({"group_ids": [(3, c.env.ref(T1).id)]})
    with pytest.raises(UserError, match="DOFA authority"):
        task.with_user(c.t1b).action_approve()
    assert not rec.dofa_approved


# =================================================================== the matrix (rule book)
def test_m63_24_plain_user_edits_matrix(c, p03):
    """Who may change the DoA rule book? A plain user: create a row, archive a row, retune one."""
    admin_row = matrix_row(c.env, name="Admin rule")
    done = []
    for label, fn in (
        (
            "create",
            lambda: matrix_row(c.env, user=c.p, decision_domain="campaign_budget", res_model=False),
        ),
        (
            "write",
            lambda: admin_row.with_user(c.p).write(
                {"approval_policy": "any", "sla_hours": 1, "max_escalations": 0}
            ),
        ),
        ("archive", lambda: admin_row.with_user(c.p).write({"active": False})),
        (
            "p03-create",
            lambda: p03.write(
                model="fix.approval.matrix",
                values={
                    "decision_domain": "kyc",
                    "approval_policy": "any",
                    "sla_hours": 1,
                    "max_escalations": 0,
                    "final_action": "reject",
                },
            ),
        ),
    ):
        try:
            with c.env.cr.savepoint():
                out = fn()
            if not (isinstance(out, dict) and out.get("error")):
                done.append(label)
        except REFUSED:
            pass
    try:
        admin_row.with_user(c.p).unlink()
        done.append("unlink")
    except REFUSED:
        pass
    assert not done, "GAP: plain user changed the approval matrix: %s" % ", ".join(done)


def test_m63_25_plain_user_reroutes_dofa_approval_away_from_tier(c):
    """A plain user points the concession rule at an EMPTY group: every concession now has
    'no one can approve' - the real Tier-1 holders are removed from the chain."""
    try:
        matrix_row(
            c.env, user=c.p, approver_group_id=c.env.ref("cd_entity_config.group_dofa_tier_5").id
        )
    except REFUSED:
        return
    rec = complaint(c)
    try:
        rec.with_user(c.clerk).action_request_approval()
    except UserError as exc:
        raise AssertionError(
            "GAP: plain user's matrix row removed Tier 1 from the chain: %s" % exc
        ) from exc
    assert set(assignees(rec)) & {c.t1, c.t1b}, (
        "GAP: plain user's rule re-routed a Tier-1 concession to %s"
        % assignees(rec).mapped("login")
    )


def test_m63_26_matrix_group_reroute_dofa_decision_still_checks_tier(c):
    """A re-route to a group the attacker is in. Post-E1 there are two layers:
    the plain user cannot write the rule book at all, and even a rule the
    ADMINISTRATOR re-routes to the whole company only routes holders who
    actually hold the tier — a tier-less member never receives the stamp."""
    # Layer 1 (E1): the attack entry is closed.
    with pytest.raises(REFUSED):
        matrix_row(c.env, user=c.p, approver_group_id=c.env.ref("base.group_user").id)
    # Layer 2: an administrator's company-wide re-route stays competent.
    matrix_row(c.env, approver_group_id=c.env.ref("base.group_user").id)
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    holders = assignees(rec)
    assert holders, "re-route had no effect"
    tierless = holders.filtered(lambda u: not (u.has_group(T1) or u.has_group(T2)))
    assert not tierless, (
        "GAP: a whole-company re-route routed tier-less holders %s to decide a Tier-1 concession"
        % tierless.mapped("login")
    )
    assert c.p not in holders, "the tier-less attacker was routed anyway"
    assert not rec.dofa_approved


def test_m63_27_matrix_group_reroute_non_dofa_approval(c):
    """Non-DOFA routed approval (M07 contract verification): the apply method checks the group
    THE MATRIX names. A salesperson (All Leads, no manager group) re-points the rule to the All-Leads group and verifies a
    colleague's customer contract."""
    seller = _user(c.env, "a11m63_seller", [SALES])
    p = _user(c.env, "a11m63_sales_p", [SALES_ALL])
    _user(c.env, "a11m63_salesmgr", [SALES_MGR])
    lead = (
        c.env["crm.lead"]
        .with_user(seller)
        .create(
            {
                "name": "A11M63 deal",
                "type": "opportunity",
                "user_id": seller.id,
                "contract_ref": "PO-A11-1",
            }
        )
    )
    try:
        row = matrix_row(
            c.env,
            user=p,
            decision_domain="contract_verification",
            res_model="crm.lead",
            approver_group_id=c.env.ref(SALES_ALL).id,
        )
    except REFUSED as exc:
        print("STEP27 matrix create refused:", exc)
        return
    print(
        "STEP27 match:",
        c.env["fix.approval.matrix"]._match(lead).ids,
        "row",
        row.id,
        "simulate:",
        lead.approval_simulate(),
    )
    lead.with_user(seller).action_request_approval()
    routed = lead.approval_request_id.task_ids.mapped("assigned_user_id")
    print("STEP27 routed to:", routed.mapped("login"))
    task = lead.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == p)
    if not task:
        print("STEP27 attacker not routed")
        return
    try:
        task.with_user(p).action_approve()
    except REFUSED as exc:
        print("STEP27 decision refused:", exc)
        return
    assert not lead.contract_verified, (
        "GAP: salesperson %s (no manager group) edited the DoA matrix and verified %s's contract %s: "
        "contract_verified=%s rate_card_approved=%s by %s"
        % (
            p.login,
            seller.login,
            lead.contract_ref,
            lead.contract_verified,
            lead.rate_card_approved,
            lead.contract_verified_by.login,
        )
    )


def test_m63_28_matrix_final_action_auto_rejects_others(c):
    """A plain user's rule (SLA 1 h, no escalation, final action reject) kills a colleague's request."""
    try:
        matrix_row(c.env, user=c.p, sla_hours=1, max_escalations=0, final_action="reject")
    except REFUSED:
        return
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    req = rec.approval_request_id
    for _ in range(2):
        overdue(req)
        run_cron(c.env)
    assert req.state != "rejected", (
        "GAP: plain user's matrix row auto-rejected %s (state %s, record %s) after 1 h"
        % (req.name, req.state, rec.approval_state)
    )


def test_m63_29_matrix_condition_is_safe_eval(c):
    """The rule condition is code-shaped text: it must not execute Python.

    Post-E1 the row cannot even be created — safe_eval refuses `open` — but
    the no-execution property is what this control pins, for any creator."""
    if os.path.exists(PWN_FILE):
        os.remove(PWN_FILE)
    # The savepoint matters: a refused constraint leaves its INSERT in the
    # caller's transaction, and this suite catches the refusal.
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        matrix_row(c.env, condition="open(%r, 'w').write('pwned')" % PWN_FILE)
    executed = os.path.exists(PWN_FILE)
    if executed:
        os.remove(PWN_FILE)
    assert not executed, "GAP: matrix condition executed Python (file written)"


def test_m63_30_matrix_bad_condition_blocks_every_request(c):
    """Denial of service: a malformed condition must be refused at creation
    (post-G9 constraint), so it can never break anyone's request."""
    with pytest.raises(REFUSED, match="(?i)condition"), c.env.cr.savepoint():
        matrix_row(c.env, condition="[('x', '=', ")
    # And the request path still works.
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    assert (
        rec.approval_state == "pending"
    ), "GAP: a refused malformed condition still left the request path broken"


# =================================================================== evidence: request / history / task
def test_m63_31_request_cannot_be_forged(c, p03):
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    req = rec.approval_request_id
    with pytest.raises(AccessError):
        c.env["fix.approval.request"].with_user(c.p).create(
            {
                "res_model": "fix.complaint",
                "res_id": rec.id,
                "requested_by_id": c.p.id,
                "state": "approved",
            }
        )
    with pytest.raises(AccessError):
        req.with_user(c.clerk).write({"state": "approved"})
    res = p03.write(model="fix.approval.request", record_id=req.id, values={"state": "approved"})
    assert res.get("error"), "GAP: P03 wrote request state: %r" % res
    with pytest.raises(UserError):
        req.sudo().unlink()
    assert req.state == "pending"


def test_m63_32_history_is_append_only(c):
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task_of(rec, c.t1).with_user(c.t1).action_approve()
    hist = rec.approval_request_id.history_ids
    with pytest.raises(AccessError):
        c.env["fix.approval.history"].with_user(c.clerk).create(
            {
                "request_id": rec.approval_request_id.id,
                "res_model": "fix.complaint",
                "res_id": rec.id,
                "event": "approved",
                "user_id": c.t2.id,
            }
        )
    for who in (c.clerk.id, c.t1.id):
        with pytest.raises(REFUSED):
            hist[:1].with_user(who).write({"comment": "edited"})
    with pytest.raises(UserError):
        hist.sudo().write({"comment": "edited by sudo"})
    with pytest.raises(UserError):
        hist.sudo().unlink()


def test_m63_33_task_guarded_fields(c, p03):
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task = task_of(rec, c.t1)
    with pytest.raises(UserError):
        task.with_user(c.p).write({"assigned_user_id": c.p.id})
    with pytest.raises(UserError):
        task.with_user(c.t1).write({"state": "done", "decision": "approved"})
    with pytest.raises(UserError):
        c.env["fix.workflow.task"].with_user(c.p).create(
            {"res_model": "fix.complaint", "res_id": rec.id, "assigned_user_id": c.p.id}
        )
    res = p03.write(model="fix.workflow.task", record_id=task.id, values={"state": "done"})
    assert res.get("error"), "GAP: P03 wrote task state: %r" % res


def test_m63_34_task_unguarded_fields_writable_by_anyone(c):
    """A plain user re-labels someone else's pending approval task (task_type, name, instance)."""
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    task = task_of(rec, c.t1)
    try:
        task.with_user(c.p).write({"task_type": "review", "name": "nothing to see"})
    except REFUSED:
        return
    hidden = (
        not c.env["fix.workflow.task"]
        .with_user(c.t1)
        .search_count([("id", "=", task.id), ("task_type", "=", "approval")])
    )
    raise AssertionError(
        "GAP: plain user rewrote T1's pending approval task %d (task_type=%s, name=%r); hidden from the "
        "'Approval Chains' screen (domain task_type=approval): %s"
        % (task.id, task.task_type, task.name, hidden)
    )


def test_m63_35_recall_only_by_requester(c):
    rec = complaint(c)
    rec.with_user(c.clerk).action_request_approval()
    with pytest.raises(UserError):
        rec.with_user(c.p).action_recall_approval()
    rec.with_user(c.clerk).action_recall_approval()
    assert rec.approval_request_id.state == "recalled" and rec.approval_state == "none"


def test_m63_36_contract_ref_change_voids_verification_request(c):
    """Non-money void-on-change (M07): the PO reference is changed while verification is pending."""
    seller = _user(c.env, "a11m63_seller2", [SALES])
    mgr = _user(c.env, "a11m63_salesmgr2", [SALES_MGR])
    lead = (
        c.env["crm.lead"]
        .with_user(seller)
        .create(
            {
                "name": "A11M63 deal 2",
                "type": "opportunity",
                "user_id": seller.id,
                "contract_ref": "PO-A11-2",
            }
        )
    )
    lead.with_user(seller).action_request_approval()
    task = lead.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == mgr)
    assert task
    lead.with_user(seller).write({"contract_ref": "PO-A11-FAKE"})
    try:
        task.with_user(mgr).action_approve()
    except REFUSED:
        return
    raise AssertionError(
        "GAP: manager verified %s although the request was for PO-A11-2" % lead.contract_ref
    )


# =================================================================== business rules / automation / instances
def test_m63_37_business_rule_register_forgeable(c):
    """fix.business.rule: plain user plants a code-shaped rule and rewrites an admin rule's
    expression with a forged 'last changed by' and no new version."""
    admin_rule = c.env["fix.business.rule"].create(
        {
            "code": "BRU-A11-1",
            "name": "Discount cap",
            "expression": "discount <= 0.15",
            "rule_type": "gate",
        }
    )
    done = []
    try:
        with c.env.cr.savepoint():
            c.env["fix.business.rule"].with_user(c.p).create(
                {
                    "code": "BRU-A11-X",
                    "name": "x",
                    "rule_type": "gate",
                    "expression": "__import__('os').system('whoami')",
                }
            )
        done.append("create code-shaped rule")
    except REFUSED:
        pass
    try:
        with c.env.cr.savepoint():
            admin_rule.with_user(c.p).write(
                {"expression": "True", "last_changed_by": c.t2.id, "active": True}
            )
        done.append(
            "rewrite admin rule (version %d, last_changed_by=%s)"
            % (admin_rule.version, admin_rule.last_changed_by.login)
        )
    except REFUSED:
        pass
    assert not done, (
        "GAP: plain user: %s. (No code evaluates fix.business.rule.expression.)" % "; ".join(done)
    )


def test_m63_38_automation_register_forgeable(c):
    admin_aut = c.env["fix.automation"].create(
        {
            "code": "AUT-901",
            "trigger": "x",
            "action": "y",
            "engine": "airflow",
            "engine_ref": "dag: fix_aut_901",
        }
    )
    done = []
    try:
        with c.env.cr.savepoint():
            c.env["fix.automation"].with_user(c.p).create(
                {
                    "code": "AUT-999",
                    "trigger": "record.write",
                    "action": "run",
                    "engine": "odoo_automated_action",
                    "engine_ref": "base.action_server_x",
                }
            )
        done.append("create")
    except REFUSED:
        pass
    try:
        with c.env.cr.savepoint():
            admin_aut.with_user(c.p).write({"active": False, "engine_ref": "dag: none"})
        done.append("deactivate/re-point admin automation")
    except REFUSED:
        pass
    assert not done, "GAP: plain user: %s (nothing executes engine_ref)" % ", ".join(done)


def test_m63_39_workflow_instance_state_typed(c):
    """fix.workflow.instance feeds the 'automation rate' and 'STP share' KPIs: is its state typed?"""
    inst = c.env["fix.workflow.instance"].create({"res_model": "fix.complaint", "res_id": 1})
    try:
        inst.with_user(c.p).write({"state": "completed", "escalated": False})
        c.env["fix.workflow.instance"].with_user(c.p).create({"state": "completed"})
    except REFUSED:
        return
    raise AssertionError(
        "GAP: plain user wrote/created workflow instances as 'completed'; M63 'Automation rate' KPI "
        "is a count of typed states"
    )


# =================================================================== coverage (registry sweep)
def test_m63_40_coverage_sweep(c):
    """Which models inherit fix.approvable.mixin, which are routed, and by area (P03 surfaces)."""
    import importlib

    env = c.env
    area_of = {}
    for n in range(2, 13):
        try:
            mod = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a%02d" % n)
        except ImportError:
            continue
        for model in getattr(mod, "SURFACES", {}):
            area_of.setdefault(model, "A%02d" % n)
        for model in getattr(mod, "SURFACES", {}):
            area_of.setdefault(model, "A%02d" % n)
    rows, bespoke = [], []
    for name, model in sorted(env.registry.items()):
        if model._abstract or model._transient:
            continue
        if "approval_request_id" in model._fields and hasattr(model, "_approval_routed"):
            rows.append(
                (
                    area_of.get(name, "-"),
                    name,
                    model._module,
                    bool(model._approval_routed),
                    "dofa" if "dofa_approved" in model._fields else "group",
                    model._approval_apply_method,
                    model._approval_domain,
                )
            )
        elif name in area_of:
            flags = [
                f
                for f, fld in model._fields.items()
                if "approv" in f
                and fld.store
                and fld.type in ("boolean", "many2one", "selection", "datetime")
            ]
            if flags:
                bespoke.append((area_of[name], name, flags))
    for r in rows:
        print("APPROVABLE", *r)
    for b in bespoke:
        print("BESPOKE", b[0], b[1], ",".join(b[2]))
    by_area = {}
    for r in rows:
        a = by_area.setdefault(r[0], [0, 0])
        a[0] += 1
        a[1] += r[3]
    for a in sorted(by_area):
        print("AREA", a, "approvable=%d routed=%d" % tuple(by_area[a]))
    print(
        "TOTAL approvable=%d routed=%d bespoke_models=%d"
        % (len(rows), sum(r[3] for r in rows), len(bespoke))
    )
    # fix.risk.register (A10 P1-5, M60-7) routes by appetite inside its own method:
    # within appetite the Risk Owner signs; above it action_accept_residual raises
    # the M63 request. test_a10_p15_risk_control proves both paths.
    routed_by_condition = {"fix.risk.register"}
    unrouted = [r[1] for r in rows if not r[3] and r[1] not in routed_by_condition]
    assert not unrouted, (
        "GAP: %d of %d approvable models are NOT routed (their approve method runs directly, "
        "outside the inbox): %s" % (len(unrouted), len(rows), ", ".join(unrouted))
    )


# =================================================================== the real thresholds (cd_entity_config ladder)
def test_m63_42_plain_user_cannot_lower_dofa_ladder(c):
    """The tier is set by fix.dofa.threshold / fix.dofa.ladder (not the matrix 'threshold').
    A plain user tries to lower a band, add a band, and put a ladder in force."""
    thr = c.env["fix.dofa.threshold"].search([], limit=1)
    lad = c.env["fix.dofa.ladder"].search([("in_force", "=", False)], limit=1)
    assert thr and lad, "fixture: no ladder rows on the test DB"
    with pytest.raises(AccessError):
        thr.with_user(c.p).write({"upper_bound": 1.0})
    with pytest.raises(AccessError):
        c.env["fix.dofa.threshold"].with_user(c.p).create(
            {"ladder_id": lad.id, "upper_bound": 999999999.0, "tier": "tier_1"}
        )
    with pytest.raises(REFUSED):
        lad.with_user(c.p).action_put_in_force(reference="probe")
