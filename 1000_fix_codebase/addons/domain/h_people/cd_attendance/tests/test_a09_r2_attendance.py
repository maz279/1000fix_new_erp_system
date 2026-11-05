# A09 round 2, M55 attendance (package r2e): the items round 1 left open.
#
#   1. the biometric webhook /hooks/v1/biometric/<device> (M55-8)
#   2. roster publication and change control (BRU-WFM-12)
#   3. versioned, effective-dated working-time rules (T-07/T-08)
#   4. the s.101, s.105, s.102-average and short-rest checks, label or block
#   5. forward adjustments to payroll (FR-WFM-052, interface I8)
#   6. the on-call allowance approval (interface I9)
#   8. biometric consent (BRU-WFM-08)
#   9. festival holidays in the calendar
#  10. night-work consent withdrawal re-checks the roster (BLA s.109)
#  11. the employee.left relay consumer (AUT-WFM-16)
#
# Every attack runs as a freshly created NON-admin user and is refused; the
# proper path is then run by the right role. Direct writes go through call_kw
# with the client-controlled `tracking_disable` key; the webhook is called
# through its real controller with `request` replaced by a stand-in.
import itertools
import json
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields, http
from odoo.addons.cd_attendance.controllers import biometric_webhook as hook
from odoo.addons.cd_p03_portal.controllers.a09 import m55
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REC = "fix.attendance.record"
GUARDED = "changes only through its workflow"
JAN_S, JAN_E = date(2026, 1, 1), date(2026, 1, 31)
SECRET = "a9-r2e-device-secret-0123456789abcdefXYZ"
_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 R2E User %d" % n,
                "login": "a09-r2e-%d@test.local" % n,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


def dt(day, hour, minute=0):
    return datetime(day.year, day.month, day.day, hour, minute)


def rpc(c, user, model, method, ids, *args, **kw):
    env = c.env(user=user.id, context={"tracking_disable": True})
    return call_kw(env[model], method, [ids, *args], kw)


@pytest.fixture
def x(odoo_env):
    env = odoo_env
    # the business date (env tz Asia/Dhaka): M55 availability and the night-
    # consent recheck both decide on the context date, so the file does too —
    # a UTC `today` runs a day behind after 18:00 UTC.
    c = SimpleNamespace(env=env, today=fields.Date.context_today(env["fix.roster.slot"]))
    c.emp_u, c.col_u, c.fem_u = (_user(env) for _ in range(3))
    # W4 (apply-as-approver): the routed line manager decides regularisations
    # in their own environment, so they hold the attendance role (write on
    # fix.attendance.regularisation) like the officers below.
    c.mgr_u = _user(env, "hr_attendance.group_hr_attendance_user")
    c.off_u = _user(env, "hr_attendance.group_hr_attendance_user")
    c.sup_u = _user(env, "cd_attendance.group_attendance_supervisor")
    c.sup2_u = _user(env, "cd_attendance.group_attendance_supervisor")
    c.lockmgr_u = _user(env, "cd_attendance.group_attendance_lock_manager")
    c.hrm_u = _user(env, "hr.group_hr_manager")
    c.hrm2_u = _user(env, "hr.group_hr_manager")
    c.hro_u = _user(env, "cd_hr_core.group_hr_officer")
    c.pay_u = _user(env, "cd_payroll_bd.group_payroll_officer")
    E = env["hr.employee"]
    c.e_mgr = E.create({"name": "R2E Line Manager", "user_id": c.mgr_u.id})
    c.e_emp = E.create(
        {
            "name": "R2E Employee",
            "user_id": c.emp_u.id,
            "parent_id": c.e_mgr.id,
            "sex": "male",
            "employee_code": "R2E-0001",
        }
    )
    c.e_col = E.create({"name": "R2E Colleague", "user_id": c.col_u.id, "parent_id": c.e_mgr.id})
    c.e_fem = E.create(
        {"name": "R2E Night Tech", "user_id": c.fem_u.id, "sex": "female", "parent_id": c.e_mgr.id}
    )
    c.day_shift = env["fix.shift.template"].create(
        {"name": "R2E Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    c.night_shift = env["fix.shift.template"].create(
        {"name": "R2E Night", "start_hour": 22.0, "end_hour": 6.0}
    )
    c.dev = env["fix.biometric.device"].create({"device_id": "R2E-DEV-1", "name": "Gate"})
    c.dev.action_rotate_credential(credential=SECRET)
    return c


def consent(c, emp, user=None):
    """HR prepares the consent record; the employee gives it (BRU-WFM-08)."""
    user = user or emp.user_id
    rec = c.env["fix.biometric.consent"].with_user(c.hro_u).create({"employee_id": emp.id})
    rec.with_user(user).action_give()
    return rec


def clean(c, day, h_in, h_out, emp=None, m_out=0):
    """setup: a clean device punch (superuser = the device integration)."""
    return c.env[REC].create(
        {
            "employee_id": (emp or c.e_emp).id,
            "check_in": dt(day, h_in),
            "check_out": dt(day, h_out, m_out),
            "source": "biometric",
        }
    )


def tasks(c, rec):
    return (
        c.env["fix.workflow.task"]
        .sudo()
        .search([("res_model", "=", rec._name), ("res_id", "=", rec.id), ("state", "=", "pending")])
    )


def assignees(c, rec):
    return tasks(c, rec).mapped("assigned_user_id")


# ======================================================================= 1. webhook
def call_hook(c, device, body, credential=SECRET, header="Authorization"):
    """POST through the real controller; `request` is a stand-in whose
    make_json_response builds a real odoo.http.Response."""
    headers = {}
    if credential is not None:
        headers[header] = ("Bearer %s" % credential) if header == "Authorization" else credential
    raw = body if isinstance(body, bytes) else json.dumps(body).encode()

    def make_json_response(data, status=200):
        return http.Response(json.dumps(data), status=status, mimetype="application/json")

    fake = SimpleNamespace(
        env=c.env,
        httprequest=SimpleNamespace(headers=headers, get_data=lambda: raw),
        make_json_response=make_json_response,
    )
    with mock.patch.object(hook, "request", fake):
        resp = hook.BiometricWebhook().biometric_punches(device)
    return SimpleNamespace(status=resp.status_code, data=json.loads(resp.get_data()))


def punch(event, hour, kind="check_in", code="R2E-0001", day=date(2026, 3, 2)):
    return {
        "event_id": event,
        "employee_code": code,
        "time": "%sT%02d:00:00+06:00" % (day, hour),
        "type": kind,
    }


def test_webhook_route_is_device_authenticated_post():
    routing = hook.BiometricWebhook.biometric_punches.original_routing
    assert routing["routes"] == ["/hooks/v1/biometric/<string:device>"]
    assert (routing["auth"], routing["type"], routing["methods"], routing["csrf"]) == (
        "none",
        "http",
        ["POST"],
        False,
    )


def test_webhook_refuses_wrong_credential_unknown_device_and_wrong_company(x):
    consent(x, x.e_emp)
    body = {"punches": [punch("e1", 9)]}
    for device, cred in (
        ("R2E-DEV-1", "wrong-" + SECRET),
        ("R2E-DEV-1", None),
        ("NO-SUCH", SECRET),
    ):
        res = call_hook(x, device, body, credential=cred)
        assert (res.status, res.data["error"]) == (401, "unauthorized"), (device, cred)
    res = call_hook(x, "R2E-DEV-1", {**body, "company_id": x.env.company.id + 999})
    assert (res.status, res.data["error"]) == (403, "wrong_company")
    res = call_hook(x, "R2E-DEV-1", b"not json")
    assert (res.status, res.data["error"]) == (400, "bad_payload")
    assert not x.env[REC].search([("employee_id", "=", x.e_emp.id)])
    # an inactive or offline terminal is refused even with its credential
    x.dev.status = "offline"
    assert call_hook(x, "R2E-DEV-1", body).status == 403
    x.dev.write({"status": "online", "active": False})
    assert call_hook(x, "R2E-DEV-1", body).status == 403
    x.dev.active = True
    # the X-Device-Credential header works too
    res = call_hook(x, "R2E-DEV-1", body, header="X-Device-Credential")
    assert (res.status, res.data["ingested"]) == (200, 1)


def test_webhook_ingests_once_and_answers_replays_from_the_log(x):
    consent(x, x.e_emp)
    body = {"punches": [punch("e10", 9), punch("e11", 18, "check_out")]}
    res = call_hook(x, "R2E-DEV-1", body)
    assert (res.status, res.data["ingested"], res.data["refused"]) == (200, 2, 0), res.data
    rec = x.env[REC].search([("employee_id", "=", x.e_emp.id)])
    # +06:00 is converted to UTC
    assert (rec.check_in, rec.check_out, rec.source, rec.device_id) == (
        datetime(2026, 3, 2, 3, 0),
        datetime(2026, 3, 2, 12, 0),
        "biometric",
        x.dev,
    )
    replay = call_hook(x, "R2E-DEV-1", body)
    assert (replay.data["duplicates"], replay.data["ingested"]) == (2, 0)
    assert {r["record_id"] for r in replay.data["results"]} == {rec.id}
    # the same punch under a new event id is still one record (ingest de-duplication)
    again = call_hook(x, "R2E-DEV-1", {"punches": [punch("e12", 9)]})
    assert again.data["ingested"] == 1 and again.data["results"][0]["record_id"] == rec.id
    assert len(x.env[REC].search([("employee_id", "=", x.e_emp.id)])) == 1
    events = x.env["fix.biometric.punch.event"].search([("device_id", "=", x.dev.id)])
    assert set(events.mapped("state")) == {"ingested"} and len(events) == 3


def test_webhook_refuses_another_companys_employee_and_unconsented_punches(x):
    co_b = x.env["res.company"].create({"name": "R2E Co B"})
    x.env["hr.employee"].create(
        {"name": "R2E Co-B Worker", "company_id": co_b.id, "employee_code": "R2E-B-1"}
    )
    res = call_hook(x, "R2E-DEV-1", {"punches": [punch("b1", 9, code="R2E-B-1")]})
    assert res.data["refused"] == 1 and "belongs to" in res.data["results"][0]["error"]
    # no consent: refused, and the same event is accepted once consent is recorded
    res = call_hook(x, "R2E-DEV-1", {"punches": [punch("c1", 9)]})
    assert res.data["refused"] == 1 and "consent" in res.data["results"][0]["error"]
    consent(x, x.e_emp)
    res = call_hook(x, "R2E-DEV-1", {"punches": [punch("c1", 9)]})
    assert res.data["ingested"] == 1
    # a punch into a locked period is refused
    x.env["fix.attendance.lock"].create(
        {"name": "R2E Jan", "period_start": JAN_S, "period_end": JAN_E}
    ).action_lock()
    res = call_hook(x, "R2E-DEV-1", {"punches": [punch("l1", 9, day=date(2026, 1, 12))]})
    assert res.data["refused"] == 1 and "locked" in res.data["results"][0]["error"]


def test_credential_is_hashed_and_rotated_by_a_supervisor_only(x):
    for user in (x.emp_u, x.off_u, x.hro_u):
        with pytest.raises(AccessError), x.env.cr.savepoint():
            x.dev.with_user(user).action_rotate_credential(credential="z" * 40)
    with pytest.raises(UserError, match=GUARDED):
        rpc(x, x.sup_u, "fix.biometric.device", "write", [x.dev.id], {"credential_prefix": "xx"})
    stored = x.dev.sudo().credential_hash
    assert stored and stored != SECRET and SECRET not in stored
    with pytest.raises(UserError, match="at least 32"), x.env.cr.savepoint():
        x.dev.with_user(x.sup_u).action_rotate_credential(credential="short")
    new = "r2e-rotated-credential-ABCDEFGHIJKLMNOP"
    x.dev.with_user(x.sup_u).action_rotate_credential(credential=new)
    assert x.dev.credential_rotated_by_id == x.sup_u
    assert call_hook(x, "R2E-DEV-1", {"punches": []}).status == 401  # the old one is dead
    assert call_hook(x, "R2E-DEV-1", {"punches": []}, credential=new).status == 200
    # generated when none is given, and returned once
    out = x.dev.with_user(x.sup_u).action_rotate_credential()
    assert len(out["credential"]) >= 32
    assert call_hook(x, "R2E-DEV-1", {"punches": []}, credential=out["credential"]).status == 200


# ======================================================================= 8. biometric consent
def test_consent_is_the_employees_and_can_be_withdrawn(x):
    Consent = x.env["fix.biometric.consent"]
    # RAP X-02: a plain user writes nothing on the model; HR prepares the record
    with pytest.raises(AccessError), x.env.cr.savepoint():
        Consent.with_user(x.emp_u).create({"employee_id": x.e_emp.id})
    rec = Consent.with_user(x.hro_u).create({"employee_id": x.e_emp.id})
    with pytest.raises(UserError), x.env.cr.savepoint():  # guard, then ACL
        rpc(x, x.emp_u, "fix.biometric.consent", "write", [rec.id], {"state": "given"})
    with pytest.raises(AccessError), x.env.cr.savepoint():
        rpc(x, x.emp_u, "fix.biometric.consent", "write", [rec.id], {"notice_version": "v9"})
    with pytest.raises(UserError, match=GUARDED), x.env.cr.savepoint():
        rpc(x, x.hro_u, "fix.biometric.consent", "write", [rec.id], {"state": "given"})
    # the supervisor who runs the devices does not consent for the employee
    with pytest.raises(AccessError), x.env.cr.savepoint():
        rec.with_user(x.sup_u).action_give()
    # HR records it only from a signed consent
    other = Consent.with_user(x.hro_u).create({"employee_id": x.e_col.id})
    with pytest.raises(UserError, match="signed consent"), x.env.cr.savepoint():
        other.with_user(x.hro_u).action_give()
    rec.with_user(x.emp_u).action_give()
    assert (rec.state, rec.given_by_id) == ("given", x.emp_u)
    with pytest.raises(ValidationError, match="already has"), x.env.cr.savepoint():
        consent(x, x.e_emp)
    x.dev.action_ingest_punch(x.e_emp.id, dt(date(2026, 3, 4), 9))
    rec.with_user(x.emp_u).action_withdraw()
    with pytest.raises(UserError, match="no recorded consent"), x.env.cr.savepoint():
        x.dev.action_ingest_punch(x.e_emp.id, dt(date(2026, 3, 5), 9))
    # the colleague cannot read it
    assert not Consent.with_user(x.col_u).search([("id", "=", rec.id)])


# ======================================================================= 2. roster publication
def slot(c, day, emp=None, shift=None, user=None):
    return (
        c.env["fix.roster.slot"]
        .with_user(user or c.sup_u)
        .create(
            {"employee_id": (emp or c.e_emp).id, "date": day, "shift_id": (shift or c.day_shift).id}
        )
    )


def publish(c, d_from, d_to, planner=None, approver=None):
    pub = (
        c.env["fix.roster.publication"]
        .with_user(planner or c.sup_u)
        .create({"date_from": d_from, "date_to": d_to})
    )
    pub.action_submit()
    pub.with_user(approver or c.sup2_u).action_inbox_approve()
    return pub


def test_roster_is_published_by_someone_other_than_the_planner(x):
    d = x.today + timedelta(days=5)
    s1 = slot(x, d)
    assert s1.state == "draft"
    # the employee does not see a draft slot
    assert not x.env["fix.roster.slot"].with_user(x.emp_u).search([("id", "=", s1.id)])
    with pytest.raises(UserError, match=GUARDED):
        rpc(x, x.sup_u, "fix.roster.slot", "write", [s1.id], {"state": "published"})
    with pytest.raises(AccessError), x.env.cr.savepoint():
        x.env["fix.roster.publication"].with_user(x.emp_u).create({"date_from": d, "date_to": d})
    pub = x.env["fix.roster.publication"].with_user(x.sup_u).create({"date_from": d, "date_to": d})
    with pytest.raises(AccessError), x.env.cr.savepoint():
        pub.with_user(x.emp_u).action_submit()
    pub.action_submit()
    who = assignees(x, pub)
    assert x.sup2_u in who and x.sup_u not in who and x.emp_u not in who
    with pytest.raises(UserError, match=GUARDED):
        rpc(x, x.sup_u, "fix.roster.publication", "write", [pub.id], {"state": "published"})
    with pytest.raises(UserError, match="not awaiting your decision"), x.env.cr.savepoint():
        pub.with_user(x.sup_u).action_inbox_approve()
    with pytest.raises(UserError), x.env.cr.savepoint():
        pub.with_user(x.sup2_u).action_approve()  # direct, not from the task
    # a slot inside a publication awaiting approval is not edited
    with pytest.raises(UserError, match="awaiting publication"), x.env.cr.savepoint():
        rpc(x, x.sup_u, "fix.roster.slot", "write", [s1.id], {"shift_id": x.night_shift.id})
    pub.with_user(x.sup2_u).action_inbox_approve()
    assert (pub.state, pub.decided_by_id, s1.state) == ("published", x.sup2_u, "published")
    assert x.env["fix.roster.slot"].with_user(x.emp_u).search([("id", "=", s1.id)]) == s1


def test_a_rostered_supervisor_never_publishes_his_own_roster(x):
    e_sup2 = x.env["hr.employee"].create({"name": "R2E Supervisor Two", "user_id": x.sup2_u.id})
    d = x.today + timedelta(days=6)
    slot(x, d, emp=e_sup2)
    pub = x.env["fix.roster.publication"].with_user(x.sup_u).create({"date_from": d, "date_to": d})
    pub.action_submit()
    assert x.sup2_u not in assignees(x, pub)


def test_a_published_slot_changes_only_through_a_routed_change_request(x):
    d = x.today + timedelta(days=7)
    s1 = slot(x, d)
    publish(x, d, d)
    with pytest.raises(UserError, match="change request"):
        rpc(x, x.sup_u, "fix.roster.slot", "write", [s1.id], {"shift_id": x.night_shift.id})
    with pytest.raises(UserError, match="change request"), x.env.cr.savepoint():
        s1.with_user(x.sup_u).unlink()
    CR = x.env["fix.roster.change.request"]
    # RAP X-02: a plain user raises no change request directly
    with pytest.raises(AccessError), x.env.cr.savepoint():
        CR.with_user(x.emp_u).create(
            {"slot_id": s1.id, "new_date": d + timedelta(days=1), "reason": "x"}
        )
    # a colleague cannot ask about someone else's slot
    with pytest.raises(AccessError), x.env.cr.savepoint():
        s1.with_user(x.col_u).action_ask_change(reason="swap me in")
    out = s1.with_user(x.emp_u).action_ask_change(reason="family event on that day")
    req = CR.browse(out["change_request_ids"])
    assert (req.state, req.old_employee_id, req.create_uid) == ("draft", x.e_emp, x.emp_u)
    assert CR.with_user(x.emp_u).search([("id", "=", req.id)]) == req  # he sees his own
    with pytest.raises(AccessError), x.env.cr.savepoint():
        rpc(x, x.emp_u, "fix.roster.change.request", "write", [req.id], {"new_date": str(d)})
    with pytest.raises(UserError, match=GUARDED), x.env.cr.savepoint():
        rpc(x, x.sup_u, "fix.roster.change.request", "write", [req.id], {"state": "approved"})
    # the supervisor completes it and submits; another supervisor decides
    later = str(d + timedelta(days=1))
    rpc(x, x.sup_u, "fix.roster.change.request", "write", [req.id], {"new_date": later})
    req.with_user(x.sup_u).action_submit()
    who = assignees(x, req)
    assert x.emp_u not in who and x.sup_u not in who and x.sup2_u in who
    with pytest.raises(UserError, match="not awaiting your decision"), x.env.cr.savepoint():
        req.with_user(x.emp_u).action_inbox_approve()
    with pytest.raises(UserError, match="State why"), x.env.cr.savepoint():
        req.with_user(x.sup_u).action_reject()
    req.with_user(x.sup2_u).action_inbox_approve()
    assert (req.state, s1.date, s1.state) == ("approved", d + timedelta(days=1), "published")
    rem = CR.with_user(x.sup_u).create(
        {"slot_id": s1.id, "kind": "remove", "reason": "branch closed"}
    )
    rem.action_submit()
    assert x.sup_u not in assignees(x, rem)
    rem.with_user(x.sup2_u).action_inbox_approve()
    assert not s1.exists()


def test_dispatch_published_only_is_a_company_switch(x):
    t = x.today
    slot(x, t)
    wo = x.env["fix.work.order"].new({"technician_id": x.e_emp.id})
    with mock.patch("odoo.addons.cd_attendance.models.fix_attendance.publish"):
        assert wo.action_check_technician_availability() is True  # today's behaviour
    x.env.company.fix_roster_dispatch_published_only = True
    with pytest.raises(UserError, match="no roster slot"):
        wo.action_check_technician_availability()


def test_publication_notice_is_a_setting(x):
    x.env.company.fix_roster_notice_days = 14
    d = x.today + timedelta(days=3)
    slot(x, d)
    pub = x.env["fix.roster.publication"].with_user(x.sup_u).create({"date_from": d, "date_to": d})
    with pytest.raises(UserError, match="14 days ahead"), x.env.cr.savepoint():
        pub.action_submit()


# ======================================================================= roster notices (M27)
def _notices(c, key=None):
    dom = [("key", "=", key)] if key else []
    return c.env["fix.roster.notice"].search(dom)


def _deliveries(c, emp, prefix):
    return (
        c.env["fix.notif.delivery"]
        .sudo()
        .search([("dedup_key", "=like", "m55-roster:%s%%:%d" % (prefix, emp.id))])
    )


def test_a_published_roster_is_sent_to_each_employee_once(x):
    d = x.today + timedelta(days=12)
    x.e_emp.mobile_phone = "01712345678"
    x.e_col.write({"mobile_phone": False, "work_email": False})
    x.e_col.work_contact_id.write({"phone": False, "email": False})
    a = slot(x, d)
    b = slot(x, d + timedelta(days=1))
    c = slot(x, d, emp=x.e_col)
    pub = publish(x, d, d + timedelta(days=1))
    key = "publication:%d" % pub.id
    notices = _notices(x, key)
    assert len(notices) == 2  # one per rostered employee, not per slot
    mine = notices.filtered(lambda n: n.employee_id == x.e_emp)
    sent = _deliveries(x, x.e_emp, key)
    assert (mine.route, mine.channel, len(sent)) == ("m27", "sms", 1)
    assert (sent.channel, sent.to_address, sent.state) == ("sms", "01712345678", "queued")
    assert (
        sent.lawful_basis == "contract"
        and str(d) in sent.body
        and str(d + timedelta(days=1)) in sent.body
    )
    assert mine.slot_ids == a | b
    # the colleague has no phone or e-mail: chatter, follower and an activity instead
    theirs = notices - mine
    assert (theirs.route, theirs.slot_ids) == ("chatter", c)
    assert "no mobile number or e-mail" in theirs.fallback_reason
    assert x.e_col.work_contact_id in c.message_partner_ids
    assert c.activity_ids.user_id == x.col_u
    # a replay sends nothing twice
    pub._fix_notify_published()
    assert len(_notices(x, key)) == 2 and len(_deliveries(x, x.e_emp, key)) == 1
    assert len(c.activity_ids) == 1
    # notices are the workflow's
    with pytest.raises(AccessError), x.env.cr.savepoint():
        x.env["fix.roster.notice"].with_user(x.sup_u).create(
            {
                "key": "k",
                "employee_id": x.e_emp.id,
                "company_id": x.env.company.id,
                "kind": "published",
                "route": "m27",
            }
        )


def test_an_approved_slot_change_is_sent_to_the_employee_once(x):
    d = x.today + timedelta(days=14)
    x.e_emp.mobile_phone = "01712345679"
    s1 = slot(x, d)
    publish(x, d, d)
    req = (
        x.env["fix.roster.change.request"]
        .with_user(x.sup_u)
        .create(
            {"slot_id": s1.id, "new_shift_id": x.night_shift.id, "reason": "cover for a colleague"}
        )
    )
    req.action_submit()
    assert not _notices(x, "change:%d" % req.id)  # nothing before the decision
    req.with_user(x.sup2_u).action_inbox_approve()
    key = "change:%d" % req.id
    note = _notices(x, key)
    assert (len(note), note.kind, note.route, note.employee_id) == (1, "changed", "m27", x.e_emp)
    sent = _deliveries(x, x.e_emp, key)
    assert len(sent) == 1 and "R2E Night" in sent.body
    req._fix_notify_changed()
    assert len(_notices(x, key)) == 1 and len(_deliveries(x, x.e_emp, key)) == 1


# ======================================================================= 10. night-consent withdrawal
def test_withdrawing_night_consent_rechecks_the_rostered_nights(x):
    # the recheck decides on the context date (Asia/Dhaka): align with it, or
    # an 18:00-24:00 UTC run makes the "today" slot tomorrow's in Dhaka
    t = fields.Date.context_today(x.env["fix.roster.slot"])
    Consent = x.env["fix.night.work.consent"]
    nc = Consent.with_user(x.fem_u).create(
        {
            "employee_id": x.e_fem.id,
            "date_from": t - timedelta(days=5),
            "date_to": t + timedelta(days=30),
        }
    )
    nc.with_user(x.fem_u).action_confirm()
    past = slot(x, t - timedelta(days=2), emp=x.e_fem, shift=x.night_shift)
    today_pub = slot(x, t, emp=x.e_fem, shift=x.night_shift)
    later_pub = slot(x, t + timedelta(days=2), emp=x.e_fem, shift=x.night_shift)
    publish(x, t - timedelta(days=2), t + timedelta(days=2))
    draft_night = slot(x, t + timedelta(days=9), emp=x.e_fem, shift=x.night_shift)
    day_slot = slot(x, t + timedelta(days=10), emp=x.e_fem)
    nc.with_user(x.fem_u).action_withdraw()
    assert not draft_night.exists()
    assert today_pub.night_consent_flag and later_pub.night_consent_flag
    assert not past.night_consent_flag and day_slot.exists() and not day_slot.night_consent_flag
    removal = later_pub.change_request_ids
    assert (removal.kind, removal.state) == ("remove", "submitted")
    assert x.fem_u not in assignees(x, removal)
    # dispatch never sends her on the night she withdrew
    wo = x.env["fix.work.order"].new({"technician_id": x.e_fem.id})
    with pytest.raises(UserError, match="withdrew her night-work consent"):
        wo.action_check_technician_availability()
    with pytest.raises(UserError, match=GUARDED):
        rpc(x, x.sup_u, "fix.roster.slot", "write", [today_pub.id], {"night_consent_flag": False})
    removal.with_user(x.sup_u).action_inbox_approve()
    assert not later_pub.exists()


# ======================================================================= 3/4. working-time rules
def rule(c, start, **figures):
    return c.env["fix.working.time.rule"].with_user(c.hrm_u).create({"date_from": start, **figures})


def test_version_one_holds_the_pre_audit_figures(x):
    v1 = x.env["fix.working.time.rule"].search(
        [("company_id", "=", x.env.company.id)], order="version"
    )[:1]
    assert v1.version == 1 and v1.date_from <= date(2000, 1, 1)
    assert (
        v1.weekly_limit_hours,
        v1.min_rest_hours,
        v1.daily_max_hours,
        v1.daily_ot_cap_hours,
    ) == (
        60.0,
        11.0,
        10.0,
        2.0,
    )
    assert (v1.rest_interval_after_hours, v1.spread_over_max_hours, v1.annual_avg_weekly_hours) == (
        0,
        0,
        0,
    )
    assert {
        v1.short_rest_mode,
        v1.rest_interval_mode,
        v1.spread_over_mode,
        v1.annual_average_mode,
    } == {"label"}
    assert x.env.company.fix_att_max_weekly_hours == 60.0
    rec = clean(x, date(2026, 3, 9), 9, 17)
    assert rec.wt_rule_id == v1


def test_rule_versions_are_effective_dated_and_never_edited_once_in_force(x):
    Rule = x.env["fix.working.time.rule"]
    with pytest.raises(AccessError), x.env.cr.savepoint():
        Rule.with_user(x.sup_u).create({"date_from": x.today + timedelta(days=30)})
    with pytest.raises(UserError, match="future day"), x.env.cr.savepoint():
        rule(x, x.today, weekly_limit_hours=48.0)
    v1 = Rule.search([("company_id", "=", x.env.company.id), ("version", "=", 1)])
    with pytest.raises(UserError, match="has taken effect"):
        rpc(x, x.hrm_u, "fix.working.time.rule", "write", [v1.id], {"weekly_limit_hours": 48.0})
    with pytest.raises(UserError, match=GUARDED):
        rpc(x, x.hrm_u, "fix.working.time.rule", "write", [v1.id], {"version": 9})
    start = x.today + timedelta(days=40)
    v2 = rule(x, start, daily_ot_cap_hours=1.0, weekly_limit_hours=48.0)
    assert v2.version == v1.version + 1 and v1.date_to == start - timedelta(days=1)
    # still in the future: the HR Manager may correct it
    rpc(x, x.hrm_u, "fix.working.time.rule", "write", [v2.id], {"weekly_limit_hours": 50.0})
    # valuation and checks read the version of the DAY
    before = clean(x, start - timedelta(days=1), 8, 22)
    after = clean(x, start + timedelta(days=1), 8, 22)
    assert (before.wt_rule_id, after.wt_rule_id) == (v1, v2)
    OT = x.env["fix.overtime.request"].with_user(x.emp_u)
    with pytest.raises(ValidationError, match="At most 1 h"), x.env.cr.savepoint():
        OT.create(
            {
                "employee_id": x.e_emp.id,
                "date": start + timedelta(days=1),
                "hours": 2,
                "reason": "x",
            }
        )
    assert OT.create(
        {"employee_id": x.e_emp.id, "date": start - timedelta(days=1), "hours": 2, "reason": "x"}
    )


def test_s101_rest_interval_label_then_block(x):
    d1 = x.today + timedelta(days=50)
    d2 = d1 + timedelta(days=14)
    rule(x, d1, rest_interval_after_hours=6.0, rest_interval_minutes=60.0)
    rule(
        x, d2, rest_interval_after_hours=6.0, rest_interval_minutes=60.0, rest_interval_mode="block"
    )
    flagged = clean(x, d1, 8, 15)  # 7 h without a break
    assert flagged.compliance_status == "rest_break_missing" and "s.101" in flagged.statutory_notes
    clean(x, d1 + timedelta(days=1), 8, 12)
    ok = clean(x, d1 + timedelta(days=1), 13, 17)  # a 1 h interval after 4 h
    assert ok.compliance_status == "compliant"
    with pytest.raises(ValidationError, match=r"s.101"), x.env.cr.savepoint():
        clean(x, d2, 8, 15)
    assert clean(x, d2, 8, 13).compliance_status == "compliant"


def test_s105_spread_over_label_then_block(x):
    d1 = x.today + timedelta(days=80)
    d2 = d1 + timedelta(days=14)
    rule(x, d1, spread_over_max_hours=10.0)
    rule(x, d2, spread_over_max_hours=10.0, spread_over_mode="block")
    clean(x, d1, 7, 11)
    late = clean(x, d1, 18, 20)  # 07:00 to 20:00 = 13 h spread
    assert late.compliance_status == "spread_over_exceeded"
    clean(x, d2, 7, 11)
    with pytest.raises(ValidationError, match=r"s.105"), x.env.cr.savepoint():
        clean(x, d2, 18, 20)
    # the employee's own manual entry is refused the same way
    with pytest.raises(ValidationError, match=r"s.105"), x.env.cr.savepoint():
        x.env[REC].with_user(x.emp_u).create(
            {
                "employee_id": x.e_emp.id,
                "check_in": dt(d2, 18),
                "check_out": dt(d2, 20),
                "manual_reason": "x",
            }
        )


def test_short_rest_between_shifts_label_then_block(x):
    d1 = x.today + timedelta(days=110)
    d2 = d1 + timedelta(days=14)
    rule(x, d2, short_rest_mode="block")
    clean(x, d1, 14, 23)
    short = clean(x, d1 + timedelta(days=1), 6, 12)  # 7 h rest < 11 h
    assert short.compliance_status == "rest_interval_violation"
    clean(x, d2, 14, 23)
    with pytest.raises(ValidationError, match="rest between shifts"), x.env.cr.savepoint():
        clean(x, d2 + timedelta(days=1), 6, 12)
    # editing an existing record into the breach is refused too
    ok = clean(x, d2 + timedelta(days=1), 12, 18)
    with pytest.raises(ValidationError, match="rest between shifts"), x.env.cr.savepoint():
        rpc(x, x.sup_u, REC, "write", [ok.id], {"check_in": dt(d2 + timedelta(days=1), 6)})


def test_s102_annual_average_label_then_block(x):
    # a deliberately tiny test figure (0.2 h a week = 10.4 h a year): the
    # mechanism, not a statutory number
    d1 = date(x.today.year + 2, 3, 2)
    d2 = date(x.today.year + 3, 3, 1)
    rule(x, d1, annual_avg_weekly_hours=0.2)
    rule(x, d2, annual_avg_weekly_hours=0.2, annual_average_mode="block")
    clean(x, d1, 9, 15)
    over = clean(x, d1 + timedelta(days=1), 9, 15)  # 12 h in the year
    assert over.compliance_status == "annual_average_exceeded"
    clean(x, d2, 9, 15)
    with pytest.raises(ValidationError, match=r"s.102"), x.env.cr.savepoint():
        clean(x, d2 + timedelta(days=1), 9, 15)


# ======================================================================= 6. on-call allowance (I9)
def oncall(c, emp=None, allowance=1500.0, day=date(2026, 3, 1), user=None):
    return (
        c.env["fix.hr.oncall"]
        .with_user(user or c.sup_u)
        .create(
            {
                "employee_id": (emp or c.e_emp).id,
                "date_from": dt(day, 18),
                "date_to": dt(day + timedelta(days=1), 8),
                "allowance": allowance,
            }
        )
    )


def test_on_call_allowance_is_approved_by_someone_else_and_pinned(x):
    oc = oncall(x)
    with pytest.raises(UserError, match=GUARDED):
        rpc(x, x.sup_u, "fix.hr.oncall", "write", [oc.id], {"approved_allowance": 1500.0})
    oc.with_user(x.sup_u).action_submit_allowance()
    who = assignees(x, oc)
    assert who == x.mgr_u  # the line manager; never the person on call or the recorder
    for user in (x.emp_u, x.sup_u):
        with pytest.raises(UserError, match="not awaiting your decision"), x.env.cr.savepoint():
            oc.with_user(user).action_inbox_approve()
    # a change of the amount while pending voids the request
    rpc(x, x.sup_u, "fix.hr.oncall", "write", [oc.id], {"allowance": 1800.0})
    assert oc.approval_state == "none"
    oc.with_user(x.sup_u).action_submit_allowance()
    oc.with_user(x.mgr_u).action_inbox_approve()
    assert (oc.approval_state, oc.approved_allowance, oc.allowance_approved_by_id) == (
        "approved",
        1800.0,
        x.mgr_u,
    )
    with pytest.raises(UserError, match="what was approved"):
        rpc(x, x.sup_u, "fix.hr.oncall", "write", [oc.id], {"allowance": 9000.0})


def test_on_call_recorded_by_the_line_manager_goes_to_the_officers(x):
    mgr_sup = _user(x.env, "cd_attendance.group_attendance_supervisor")
    x.e_mgr.user_id = mgr_sup
    oc = oncall(x, user=mgr_sup)
    oc.with_user(mgr_sup).action_submit_allowance()
    who = assignees(x, oc)
    assert mgr_sup not in who and x.off_u in who


def test_an_allowance_approved_after_payroll_froze_is_carried_forward(x):
    P = x.env["fix.payroll.period"].create(
        {"name": "R2E-2026-03", "period_start": date(2026, 3, 1), "period_end": date(2026, 3, 31)}
    )
    P.write({"state": "approved"})  # setup: the March run is already approved
    oc = oncall(x, allowance=1200.0)
    oc.action_start()
    oc.action_complete()
    oc.with_user(x.sup_u).action_submit_allowance()
    oc.with_user(x.mgr_u).action_inbox_approve()
    adj = x.env["fix.attendance.adjustment"].search([("oncall_id", "=", oc.id)])
    assert (adj.kind, adj.quantity, adj.amount, adj.state, adj.period_month) == (
        "oncall_allowance",
        1.0,
        1200.0,
        "approved",
        "2026-03",
    )
    assert adj.approved_by_id == x.mgr_u


# ======================================================================= 5. forward adjustments (I8)
@pytest.fixture
def paid_jan(x):
    """January worked, locked, paid by payroll (state set as setup), then re-opened."""
    env = x.env
    env["fix.employment.contract"].create(
        {
            "employee_id": x.e_emp.id,
            "company_id": env.company.id,
            "contract_type": "permanent",
            "joining_date": date(2020, 1, 1),
            "basic_monthly": 20800.0,
            "state": "active",
        }
    )
    recs = {d: clean(x, date(2026, 1, d), 8, 22) for d in (5, 6)}  # 6 h recorded each
    req = env["fix.overtime.request"].create(
        {"employee_id": x.e_emp.id, "date": date(2026, 1, 6), "hours": 2, "reason": "rush"}
    )
    req.write({"state": "submitted"})
    req.action_approve()
    lk = env["fix.attendance.lock"].create(
        {"name": "R2E Jan", "period_start": JAN_S, "period_end": JAN_E}
    )
    lk.action_lock()
    P = env["fix.payroll.period"].create(
        {"name": "R2E-PAY-01", "period_start": JAN_S, "period_end": JAN_E}
    )
    P.action_verify_attendance_locked()
    with pytest.raises(UserError, match="has not paid it yet"), env.cr.savepoint():
        lk.with_user(x.lockmgr_u).action_unlock(reason="too early")
    P.write({"state": "paid"})  # setup: payroll paid January
    lk.with_user(x.lockmgr_u).action_unlock(reason="Uttara terminal uploaded late")
    return SimpleNamespace(lock=lk, period=P, recs=recs)


def adjustments(c, kind=None):
    dom = [("employee_id", "=", c.e_emp.id), ("state", "!=", "cancelled")]
    if kind:
        dom.append(("kind", "=", kind))
    return c.env["fix.attendance.adjustment"].search(dom)


def test_reopening_a_paid_month_records_what_was_paid(x, paid_jan):
    lk = paid_jan.lock
    assert (lk.state, lk.payroll_paid, lk.baseline_taken) == ("unlocked", True, True)
    base = x.env["fix.attendance.paid.baseline"].search(
        [("lock_id", "=", lk.id), ("employee_id", "=", x.e_emp.id)]
    )
    assert {(b.date.day, b.overtime_hours, b.worked) for b in base} == {
        (5, 0.0, True),
        (6, 2.0, True),
    }
    assert not adjustments(x)


def test_a_change_after_payment_becomes_a_routed_forward_adjustment(x, paid_jan):
    jan6 = paid_jan.recs[6]
    # the employee shortens his own Jan 6 record: it goes back to pending (pays nothing)
    rpc(x, x.emp_u, REC, "write", [jan6.id], {"check_out": dt(date(2026, 1, 6), 20)})
    ot = adjustments(x, "overtime_hours")
    absent = adjustments(x, "absence_days")
    assert (ot.date, ot.period_month, ot.quantity, ot.amount, ot.state) == (
        date(2026, 1, 6),
        "2026-01",
        -2.0,
        -400.0,
        "draft",
    )
    assert (absent.quantity, absent.amount) == (1.0, 0.0)
    assert ot.approval_state == "pending" and ot.raised_by_id == x.emp_u
    who = assignees(x, ot)
    assert x.emp_u not in who and x.hrm_u in who and x.hrm2_u in who
    # nobody types an adjustment or its state
    with pytest.raises(AccessError), x.env.cr.savepoint():
        x.env["fix.attendance.adjustment"].with_user(x.hrm_u).create(
            {
                "employee_id": x.e_emp.id,
                "company_id": x.env.company.id,
                "date": JAN_S,
                "kind": "overtime_hours",
            }
        )
    with pytest.raises((AccessError, UserError)), x.env.cr.savepoint():
        rpc(
            x,
            x.hrm_u,
            "fix.attendance.adjustment",
            "write",
            [ot.id],
            {"state": "approved", "quantity": 9},
        )
    # the line manager approves the regularisation: the day is back to what was paid
    jan6.action_request_regularisation()
    jan6.with_user(x.mgr_u).action_approve()
    assert not adjustments(x)
    # a retrospective overtime approval on Jan 5 is owed: +2 h at the s.108 rate
    req = (
        x.env["fix.overtime.request"]
        .with_user(x.emp_u)
        .create(
            {
                "employee_id": x.e_emp.id,
                "date": date(2026, 1, 5),
                "hours": 2,
                "reason": "Server migration kept us late",
            }
        )
    )
    req.action_submit()
    req.with_user(x.hrm_u).action_inbox_approve()
    owed = adjustments(x, "overtime_hours")
    assert (owed.date, owed.quantity, owed.amount) == (date(2026, 1, 5), 2.0, 400.0)
    assert x.hrm_u not in assignees(x, owed)  # he approved the overtime: he raised the change
    owed.with_user(x.hrm2_u).action_inbox_approve()
    assert (owed.state, owed.approved_by_id) == ("approved", x.hrm2_u)
    # re-locked: the period is flagged as carrying differences
    paid_jan.lock.with_user(x.sup_u).action_lock()
    assert paid_jan.lock.retro_flag


def test_payroll_consumes_only_an_approved_adjustment_once_into_a_later_slip(x, paid_jan):
    jan6 = paid_jan.recs[6]
    rpc(x, x.emp_u, REC, "write", [jan6.id], {"check_out": dt(date(2026, 1, 6), 20)})
    adj = adjustments(x, "overtime_hours")
    Slip = x.env["fix.payslip"]
    feb = x.env["fix.payroll.period"].create(
        {"name": "R2E-PAY-02", "period_start": date(2026, 2, 1), "period_end": date(2026, 2, 28)}
    )
    slip_feb = Slip.create(
        {
            "period_id": feb.id,
            "employee_id": x.e_emp.id,
            "company_id": x.env.company.id,
            "basic": 1.0,
        }
    )
    slip_jan = Slip.create(
        {
            "period_id": paid_jan.period.id,
            "employee_id": x.e_emp.id,
            "company_id": x.env.company.id,
            "basic": 1.0,
        }
    )
    slip_col = Slip.create(
        {
            "period_id": feb.id,
            "employee_id": x.e_col.id,
            "company_id": x.env.company.id,
            "basic": 1.0,
        }
    )
    with pytest.raises(AccessError), x.env.cr.savepoint():
        adj.with_user(x.emp_u)._fix_consume(slip_feb)
    with pytest.raises(UserError, match="only an approved"), x.env.cr.savepoint():
        adj.with_user(x.pay_u)._fix_consume(slip_feb)
    adj.with_user(x.hrm_u).action_inbox_approve()
    with pytest.raises(UserError, match="LATER payroll period"), x.env.cr.savepoint():
        adj.with_user(x.pay_u)._fix_consume(slip_jan)
    with pytest.raises(UserError, match="not to that payslip"), x.env.cr.savepoint():
        adj.with_user(x.pay_u)._fix_consume(slip_col)
    adj.with_user(x.pay_u)._fix_consume(slip_feb)
    assert (adj.state, adj.payslip_ref_id) == ("consumed", slip_feb.id)
    # the same slip again is a no-op; another slip that exists is refused
    adj.with_user(x.pay_u)._fix_consume(slip_feb)
    assert (adj.state, adj.payslip_ref_id) == ("consumed", slip_feb.id)
    mar = x.env["fix.payroll.period"].create(
        {"name": "R2E-PAY-03", "period_start": date(2026, 3, 1), "period_end": date(2026, 3, 31)}
    )
    slip_mar = Slip.create(
        {
            "period_id": mar.id,
            "employee_id": x.e_emp.id,
            "company_id": x.env.company.id,
            "basic": 1.0,
        }
    )
    with pytest.raises(UserError, match="already on payslip"), x.env.cr.savepoint():
        adj.with_user(x.pay_u)._fix_consume(slip_mar)
    # a later change never rewrites what was consumed: the remainder is a new draft
    rpc(x, x.emp_u, REC, "write", [jan6.id], {"check_out": dt(date(2026, 1, 6), 19)})
    assert adj.quantity == -2.0
    assert not adjustments(x, "overtime_hours").filtered(lambda a: a.state == "draft")


def test_an_adjustment_whose_slip_a_recalculation_deleted_is_consumed_again(x, paid_jan):
    """I8 (payroll builder's request): only a DIFFERENT payslip that still
    exists blocks a consume; the slip a recalculation replaced does not."""
    rpc(x, x.emp_u, REC, "write", [paid_jan.recs[6].id], {"check_out": dt(date(2026, 1, 6), 20)})
    adj = adjustments(x, "overtime_hours")
    adj.with_user(x.hrm_u).action_inbox_approve()
    Slip = x.env["fix.payslip"]
    feb = x.env["fix.payroll.period"].create(
        {"name": "R2E-PAY-02R", "period_start": date(2026, 2, 1), "period_end": date(2026, 2, 28)}
    )
    vals = {
        "period_id": feb.id,
        "employee_id": x.e_emp.id,
        "company_id": x.env.company.id,
        "basic": 1.0,
    }
    first = Slip.create(vals)
    adj.with_user(x.pay_u)._fix_consume(first)
    gone = first.id
    first.unlink()  # setup: payroll's recalculation deletes and rebuilds the slip
    replacement = Slip.create(vals)
    assert adj.payslip_ref_id == gone and not Slip.browse(gone).exists()
    adj.with_user(x.pay_u)._fix_consume(replacement)
    assert (adj.state, adj.payslip_ref_id) == ("consumed", replacement.id)
    # still refused for a non-payroll user, and never onto a slip of the corrected month
    with pytest.raises(AccessError), x.env.cr.savepoint():
        adj.with_user(x.emp_u)._fix_consume(replacement)
    replacement.unlink()
    jan_slip = Slip.create({**vals, "period_id": paid_jan.period.id})
    with pytest.raises(UserError, match="LATER payroll period"), x.env.cr.savepoint():
        adj.with_user(x.pay_u)._fix_consume(jan_slip)


def test_a_period_in_payroll_but_not_paid_stays_shut(x):
    clean(x, date(2026, 1, 12), 9, 17)
    lk = x.env["fix.attendance.lock"].create(
        {"name": "R2E Jan B", "period_start": JAN_S, "period_end": JAN_E}
    )
    lk.action_lock()
    P = x.env["fix.payroll.period"].create(
        {"name": "R2E-PAY-B", "period_start": JAN_S, "period_end": JAN_E}
    )
    P.action_verify_attendance_locked()
    for state in ("attendance_locked", "calculated", "approved"):
        P.write({"state": state})
        with pytest.raises(UserError, match="has not paid it yet"), x.env.cr.savepoint():
            lk.with_user(x.lockmgr_u).action_unlock(reason="fix")


# ======================================================================= 9. festival holidays
def test_festival_holidays_are_calendar_days_leave_skips(x):
    x.env["fix.hr.holiday"].with_user(x.sup_u).create(
        {"name": "R2E Eid-ul-Fitr", "date": date(2031, 3, 20), "holiday_type": "festival"}
    )
    casual = x.env["fix.leave.type"].search(
        [("code", "=", "casual"), ("company_id", "=", x.env.company.id)]
    )
    lv = (
        x.env["fix.leave.request"]
        .with_user(x.emp_u)
        .create(
            {
                "employee_id": x.e_emp.id,
                "leave_type_id": casual.id,
                "date_from": date(2031, 3, 19),
                "date_to": date(2031, 3, 21),
            }
        )
    )
    assert lv.days == 2
    work = clean(x, date(2031, 3, 20), 9, 17)
    assert work.holiday_hours == 8.0


# ======================================================================= 11. employee.left consumer
def test_employee_left_closes_the_leavers_future_roster(x):
    t = x.today
    keep = slot(x, t)
    after_draft = slot(x, t + timedelta(days=3))
    after_pub = slot(x, t + timedelta(days=4))
    publish(x, t + timedelta(days=4), t + timedelta(days=4))
    planned = oncall(x, day=t + timedelta(days=5))
    with pytest.raises(AccessError), x.env.cr.savepoint():
        x.env["hr.employee"].with_user(x.hrm_u).consume_employee_left_roster(
            {"payload": {"employee_id": x.e_emp.id}}
        )
    x.e_emp.left_date = t
    x.e_emp._emit_leaver()
    x.env["fix.event.outbox"].cron_relay()
    assert keep.exists() and not after_draft.exists() and not after_pub.exists()
    assert planned.state == "cancelled"
    # idempotent
    res = x.env["hr.employee"].consume_employee_left_roster(
        {"payload": {"employee_id": x.e_emp.id}}
    )
    assert res == {"slots_removed": 0, "oncall_cancelled": 0}


# ======================================================================= deployment
def test_deployment_crons_consumer_acl_rules_and_surfaces(x):
    env = x.env
    cron = env.ref("cd_attendance.cron_route_attendance_adjustments")
    assert cron.active and cron.model_id.model == "fix.attendance.adjustment"
    assert cron.code.strip() == "model.cron_route_adjustments()"
    assert env["fix.attendance.adjustment"].cron_route_adjustments() == 0
    sub = env.ref("cd_attendance.event_consumer_employee_left_roster")
    assert (sub.active, sub.event_type, sub.model, sub.method) == (
        True,
        "employee.left",
        "hr.employee",
        "consume_employee_left_roster",
    )
    Access = env["ir.model.access"]
    user = env.ref("base.group_user")
    for model, perms in (
        ("fix.working.time.rule", (True, False, False, False)),
        ("fix.biometric.consent", (True, False, False, False)),
        ("fix.roster.publication", (True, False, False, False)),
        ("fix.roster.change.request", (True, False, False, False)),
        ("fix.attendance.adjustment", (True, False, False, False)),
    ):
        row = Access.search([("model_id.model", "=", model), ("group_id", "=", user.id)])
        assert (row.perm_read, row.perm_write, row.perm_create, row.perm_unlink) == perms, model
    for model in ("fix.biometric.punch.event", "fix.attendance.paid.baseline", "fix.roster.notice"):
        assert not Access.search([("model_id.model", "=", model), ("group_id", "=", user.id)])
    for xmlid in (
        "cd_attendance.rule_roster_slot_published",
        "cd_attendance.rule_roster_change_request_own",
        "cd_attendance.rule_biometric_consent_own",
        "cd_attendance.rule_attendance_adjustment_own",
    ):
        assert not env.ref(xmlid).groups  # global rules
    for model, group in (
        ("fix.biometric.consent", "cd_hr_core.group_hr_officer"),
        ("fix.roster.change.request", "cd_attendance.group_attendance_supervisor"),
    ):
        row = Access.search([("model_id.model", "=", model), ("group_id", "=", env.ref(group).id)])
        perms = (row.perm_read, row.perm_write, row.perm_create, row.perm_unlink)
        assert perms == (True, True, True, False), model
    surf = m55.SURFACES
    assert surf["fix.biometric.device"]["actions"] == {"action_rotate_credential"}
    assert surf["fix.roster.slot"]["actions"] == {"action_ask_change"}
    assert (
        {"action_submit", "action_inbox_approve", "action_reject", "action_cancel"}
        == surf["fix.roster.publication"]["actions"]
        == surf["fix.roster.change.request"]["actions"]
    )
    assert {"action_submit_allowance", "action_inbox_approve", "action_reject_allowance"} <= surf[
        "fix.hr.oncall"
    ]["actions"]
    assert surf["fix.attendance.adjustment"]["actions"] == {"action_inbox_approve", "action_reject"}
    assert surf["fix.biometric.consent"]["actions"] == {"action_give", "action_withdraw"}
    assert "fix.working.time.rule" in surf and not surf["fix.working.time.rule"]["actions"]
    assert {"rosters_awaiting", "adjustments_open"} <= set(m55.kpis(env(user=x.sup_u.id)))
