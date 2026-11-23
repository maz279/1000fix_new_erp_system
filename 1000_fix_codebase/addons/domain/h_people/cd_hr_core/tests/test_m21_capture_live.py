# cd_hr_core: M21 capture audit (2026-11-17), the records the sub-module
# pages now capture, on a real database. Every capture and decision runs as a
# NON-ADMIN user: HR Officers (hro, hro2) and a plain internal user. Arrangement
# that is not under test is done as superuser and says so. Everything rolls
# back (odoo_env).
import itertools
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_hr_core.tests.residency_memory import install
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09 import m21 as m21_surfaces
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (AccessError, UserError, ValidationError)
_SEQ = itertools.count(1)
SCAN = "c2lnbmVkIGNvcHk="  # base64 "signed copy"


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M21CAP User %d" % n,
                "login": "a09-m21cap-%d@test.local" % n,
                "tz": "UTC",
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _emp(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "M21CAP Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


@pytest.fixture(autouse=True)
def residency(monkeypatch):
    return install(monkeypatch)


@pytest.fixture
def w(odoo_env):
    class W:
        pass

    c = W()
    env = c.env = odoo_env
    c.today = fields.Date.context_today(env.user)
    c.plain = _user(env)
    c.hro = _user(env, "cd_hr_core.group_hr_officer")
    c.hro2 = _user(env, "cd_hr_core.group_hr_officer")
    c.leaver_user = _user(env)
    c.emp = _emp(env)
    c.leaver = _emp(env, c.leaver_user)
    # arrangement (superuser): a published employment notice and a retired one
    Notice = env["fix.transparency.notice"].sudo()
    tag = next(_SEQ)
    c.notice = Notice.create(
        {"version": "emp-%d.1" % tag, "purpose_set": "employment", "text_en": "N", "text_bn": "N"}
    )
    c.retired = Notice.create(
        {"version": "emp-%d.0" % tag, "purpose_set": "employment", "text_en": "O", "text_bn": "O"}
    )
    c.retired.write({"retired_at": fields.Datetime.now()})
    return c


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


# ------------------------------------------------------- page 3: org structure
def test_hr_captures_departments_and_job_profiles_through_the_workspace(w, call):
    env = w.env(user=w.hro.id)
    tag = next(_SEQ)
    out = call(
        env,
        "model_write",
        model="hr.department",
        values={"name": "M21CAP Dept %d" % tag, "fix_code": "D%d" % tag, "name_bn": "বিভাগ"},
    )
    assert out.get("id"), out
    dept = w.env["hr.department"].browse(out["id"])
    assert dept.fix_code == "D%d" % tag
    out = call(
        env,
        "model_write",
        model="hr.job",
        values={
            "name": "M21CAP Job %d" % tag,
            "fix_code": "J%d" % tag,
            "fix_job_family": "field_service",
            "fix_job_band": "band_3",
            "department_id": dept.id,
        },
    )
    assert out.get("id"), out
    job = w.env["hr.job"].browse(out["id"])
    assert (job.fix_job_family, job.fix_job_band, job.department_id) == (
        "field_service",
        "band_3",
        dept,
    )
    # a code is used once per company
    with pytest.raises(IntegrityError), w.env.cr.savepoint():
        w.env["hr.job"].with_user(w.hro).create({"name": "Twin", "fix_code": "J%d" % tag})
    # a plain internal user reads the structure but does not make it
    with pytest.raises(AccessError):
        w.env["hr.department"].with_user(w.plain).create({"name": "Not mine"})
    for model in ("hr.department", "hr.job"):
        rows = call(env, "model_records", model=model, cols=["name", "fix_code", "name_bn"])
        assert not rows.get("error"), rows


def test_a_frozen_position_has_no_vacancy(w, call):
    hr = w.env(user=w.hro.id)
    job = hr["hr.job"].create({"name": "M21CAP Frozen Job %d" % next(_SEQ)})
    pos = hr["fix.org.position"].create(
        {"name": "M21CAP Seat %d" % next(_SEQ), "headcount": 3, "job_id": job.id}
    )
    before = m21_surfaces.kpis(hr)["open_positions"]
    pos.write({"frozen": True})
    after = m21_surfaces.kpis(hr)["open_positions"]
    assert before - after == 3
    pack = call(hr, "model_report", module="M21", report="establishment_register")
    row = next(r for r in pack["rows"] if r["position"] == pos.name)
    assert (row["vacant"], row["frozen"]) == (0, 3)


# ------------------------------------------- page 7: privacy notice (BRU-HCM-12)
def _ack(w, user, **kw):
    vals = {
        "employee_id": w.emp.id,
        "notice_id": w.notice.id,
        "method": "signed_paper",
        "evidence_file": SCAN,
    }
    vals.update(kw)
    return w.env["fix.hr.notice.ack"].with_user(user).create(vals)


def test_an_acknowledgement_is_recorded_against_the_notice_in_force(w):
    ack = _ack(w, w.hro)
    assert ack.recorded_by_id == w.hro and ack.state == "acknowledged"
    assert ack.purposes == "employment"
    assert w.emp in w.emp.fix_privacy_notice_acknowledged()
    with pytest.raises(UserError):
        _ack(w, w.hro, employee_id=w.leaver.id, notice_id=w.retired.id)  # not in force
    with pytest.raises(UserError):
        _ack(w, w.hro, employee_id=w.leaver.id, evidence_file=False)  # signed copy needed
    _ack(w, w.hro, employee_id=w.leaver.id, method="self_service", evidence_file=False)
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        _ack(w, w.hro2)  # already acknowledged
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        _ack(w, w.hro, employee_id=w.leaver.id, acknowledged_on=w.today + timedelta(days=2))


def test_an_acknowledgement_is_evidence_never_edited_or_deleted(w):
    ack = _ack(w, w.hro)
    for vals in (
        {"notice_id": w.retired.id},
        {"acknowledged_on": w.today - timedelta(days=9)},
        {"employee_id": w.leaver.id},
        {"state": "withdrawn"},
        {"recorded_by_id": w.hro2.id},
    ):
        with pytest.raises(UserError):
            ack.with_user(w.hro2).write(vals)
    with pytest.raises(UserError):
        ack.with_user(w.hro2).unlink()


def test_a_withdrawal_is_stamped_by_hr_with_what_was_withdrawn(w, call):
    ack = _ack(w, w.hro)
    with pytest.raises(UserError):
        ack.with_user(w.hro2).action_withdraw(reason="  ")
    with pytest.raises(REFUSED):
        ack.with_user(w.plain).action_withdraw(reason="photo use")
    out = call(
        w.env(user=w.hro2.id),
        "model_action",
        model="fix.hr.notice.ack",
        ids=[ack.id],
        method="action_withdraw",
        kwargs={"reason": "Use of photograph on the website"},
    )
    assert out.get("success"), out
    assert (ack.state, ack.withdrawn_by_id) == ("withdrawn", w.hro2)
    assert w.emp not in w.emp.fix_privacy_notice_acknowledged()
    # a new acknowledgement of the same version is possible after a withdrawal
    assert _ack(w, w.hro).state == "acknowledged"


def test_acknowledgements_are_hr_only_and_counted_in_the_kpi(w):
    with pytest.raises(AccessError):
        w.env["fix.hr.notice.ack"].with_user(w.plain).search([])
    hr = w.env(user=w.hro.id)
    before = m21_surfaces.kpis(hr)["privacy_notice_pending"]
    _ack(w, w.hro)
    assert m21_surfaces.kpis(hr)["privacy_notice_pending"] == before - 1
    # a caller who cannot read acknowledgements gets the other KPIs, not this one
    assert "privacy_notice_pending" not in m21_surfaces.kpis(w.env(user=w.plain.id))


def test_employee_rights_requests_list_on_the_m21_page(w, call):
    partner = w.emp.work_contact_id
    assert partner, "an employee is a party through their work contact"
    req = (
        w.env["fix.rights.request"]
        .with_user(w.hro)
        .create({"partner_id": partner.id, "request_type": "rectification"})
    )
    # the M21 list's own scope (the screen's domain)
    out = call(
        w.env(user=w.hro.id),
        "model_records",
        model="fix.rights.request",
        cols=["partner_id", "request_type", "state"],
        domain=[["partner_id.employee_ids", "!=", False]],
    )
    assert not out.get("error"), out
    assert req.id in [r["id"] for r in out["rows"]]


# ----------------------------------------------- page 8: exit interview
def _exit(w, emp, **kw):
    vals = {"employee_id": emp.id, "exit_type": "resignation", "last_working_day": w.today}
    vals.update(kw)
    return w.env["fix.hr.exit"].with_user(w.hro).create(vals)


def test_an_exit_has_one_interview_by_someone_other_than_the_leaver(w):
    ex = _exit(w, w.leaver)
    Interview = w.env["fix.hr.exit.interview"].with_user(w.hro)
    # (a constraint refuses after the INSERT: each refusal in its own savepoint)
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        Interview.create(
            {"exit_id": ex.id, "primary_reason": "compensation", "interviewer_id": w.leaver_user.id}
        )
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        Interview.create(
            {"exit_id": ex.id, "primary_reason": "compensation", "secondary_reason": "compensation"}
        )
    iv = Interview.create({"exit_id": ex.id, "primary_reason": "compensation"})
    assert iv.employee_id == w.leaver and iv.interviewer_id == w.hro
    with pytest.raises(IntegrityError), w.env.cr.savepoint():
        Interview.create({"exit_id": ex.id, "primary_reason": "manager"})
    cancelled = _exit(w, w.emp)
    cancelled.with_user(w.hro2).action_cancel()  # not its creator (SoD)
    with pytest.raises(ValidationError), w.env.cr.savepoint():
        Interview.create({"exit_id": cancelled.id, "primary_reason": "other"})
    with pytest.raises(AccessError):
        w.env["fix.hr.exit.interview"].with_user(w.plain).search([])


def test_recording_locks_the_answers_and_feeds_attrition_by_reason(w, call):
    # the report judges the period on the CALLER's business day (the HR users
    # here carry tz=UTC): date the leaver the day before the fixture's day so
    # the last working day has unambiguously passed for the caller too
    ex = _exit(w, w.leaver, last_working_day=w.today - timedelta(days=1))
    iv = (
        w.env["fix.hr.exit.interview"]
        .with_user(w.hro)
        .create({"exit_id": ex.id, "primary_reason": "career_growth", "rating_pay": "2"})
    )
    with pytest.raises(UserError):
        iv.with_user(w.plain).action_record()
    out = call(
        w.env(user=w.hro2.id),
        "model_action",
        model="fix.hr.exit.interview",
        ids=[iv.id],
        method="action_record",
    )
    assert out.get("success"), out
    assert iv.state == "recorded" and iv.recorded_on
    with pytest.raises(UserError):
        iv.with_user(w.hro).write({"primary_reason": "compensation"})
    # arrangement (superuser): the exit is confirmed so it counts as a leaver
    ex.sudo().write({"state": "notice"})
    pack = call(w.env(user=w.hro.id), "model_report", module="M21", report="attrition_analysis")
    note = next(n for n in pack["notes"] if "Main reason for leaving" in n)
    assert "Career Growth" in note, note
    # a caller who cannot read interviews gets the rate without the reasons
    pack = call(w.env(user=w.plain.id), "model_report", module="M21", report="attrition_analysis")
    assert not pack.get("error") and not any("Main reason" in n for n in pack["notes"])
