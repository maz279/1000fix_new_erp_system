# A09 M22 acceptance suite (A09 workflow audit M22-F1..F11; report C4, C5,
# C6; build brief B1-B6): learning, competency and certification, attacked as
# freshly created NON-admin users. The superuser only builds the world.
import itertools
import json
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a09
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError, ValidationError)
_SEQ = itertools.count(1)
TRAINING = "cd_competency.group_training"
VERIFIER = "cd_competency.group_certification_verifier"
OVERRIDE = "cd_competency.group_dispatch_override"
DISPATCHER = "cd_field_service.group_fix_field_service_manager"


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
                "name": "A09 M22 User %d" % n,
                "login": "a09-m22-%d@test.local" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _employee(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "A09 M22 Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


def _rpc(env, user, model, method, rec, *args):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[model], method, [[rec.id], *args], {}
    )


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        return str(exc)
    return None


def _task_for(rec, user):
    return (
        rec.env["fix.workflow.task"]
        .sudo()
        .search(
            [
                ("request_id", "=", rec.sudo().approval_request_id.id),
                ("state", "=", "pending"),
                ("assigned_user_id", "=", user.id),
            ],
            limit=1,
        )
    )


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def c(odoo_env):
    env = odoo_env

    class C:
        pass

    x = C()
    x.env = env
    # the certification models (status, lapse cron, eligibility window) keep
    # the UTC clock, so x.today does too; only the roster slots (M55) sit on
    # the context date — see _rostered below.
    x.today = fields.Date.today()
    x.plain = _user(env)
    x.trn = _user(env, TRAINING)
    x.trn2 = _user(env, TRAINING)
    x.verifier = _user(env, VERIFIER)
    x.override = _user(env, OVERRIDE)
    x.disp = _user(env, DISPATCHER)
    x.assessor_user = _user(env)
    x.e_assessor = _employee(env, x.assessor_user)
    x.e_plain = _employee(env, x.plain)
    x.e_trn = _employee(env, x.trn)
    x.e_col = _employee(env)
    x.e_uncert = _employee(env)
    Comp = env["fix.competency"]
    x.c_smp = Comp.create(
        {"code": "A9SMP", "name": "A09 Smartphone", "device_type": "smartphone", "pass_mark": 70}
    )
    x.c_lap = Comp.create(
        {"code": "A9LAP", "name": "A09 Laptop", "device_type": "laptop", "pass_mark": 70}
    )
    x.course = env["fix.training.course"].create(
        {"code": "A9TRC", "name": "A09 Laptop L2 course", "competency_id": x.c_lap.id}
    )
    # the service-order world (the A09 probe's pattern)
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "A9M22", "legal_name": "A09 M22 entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "A09M22 Branch",
            "code": "A9M22",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    x.zone = env["fix.zone"].create({"name": "A09M22 Zone", "code": "A9Z22"})
    branch.write({"zone_id": x.zone.id})
    brand = env["fix.brand"].create({"name": "A09M22Brand", "code": "A9M22B"})
    cust = env["res.partner"].create({"name": "A09 M22 Customer", "phone": "01711022999"})
    x.ou = ou

    def order(device_type):
        model = env["fix.device.model"].create(
            {"name": "A09M22 %s" % device_type, "brand_id": brand.id, "device_type": device_type}
        )
        dev = env["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": cust.id,
                "serial_number": "SN-A9M22-%s" % device_type,
            }
        )
        return env["fix.service.order"].create(
            {
                "device_id": dev.id,
                "customer_id": cust.id,
                "branch_id": branch.id,
                "fault_description": "a09 m22",
                "service_type": "onsite",
            }
        )

    x.so_laptop = order("laptop")
    x.so_ac = order("appliance_ac")
    return x


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


def _assessment(c, employee, comp=None, score=85.0, assessor=None, user=None):
    # recorded by a second trainer, so it is never the assessee's own record
    return (
        c.env["fix.competency.assessment"]
        .with_user(user or c.trn2)
        .create(
            {
                "employee_id": employee.id,
                "competency_id": (comp or c.c_lap).id,
                "assessor_id": (assessor or c.e_assessor).id,
                "score": score,
                "level": "l3",
            }
        )
    )


def _draft_cert(c, employee, comp=None, user=None, **vals):
    comp = comp or c.c_lap
    base = {
        "employee_id": employee.id,
        "competency_id": comp.id,
        "issued_on": c.today - timedelta(days=1),
        "expires_on": c.today + timedelta(days=700),
        "evidence_ref": "DOC/A9/%d" % next(_SEQ),
        "assessment_id": _assessment(c, employee, comp).id,
    }
    base.update(vals)
    return c.env["fix.certification"].with_user(user or c.trn).create(base)


def _granted(c, employee, comp=None):
    cert = _draft_cert(c, employee, comp)
    cert.with_user(c.trn).action_request_grant()
    _task_for(cert, c.verifier).with_user(c.verifier).action_approve()
    return cert


def _eligible(c, employee, device_type="laptop"):
    return c.env["fix.certification"].dispatch_eligibility(employee, device_type=device_type)[0]


# ============================================================ grant (M22-F4)
def test_a_draft_certificate_never_makes_anyone_eligible(c):
    """M22-11/12: a Training Manager's direct create is a draft."""
    cert = _draft_cert(c, c.e_col)
    assert cert.state == "draft"
    assert not _eligible(c, c.e_col)


def test_state_cannot_be_forged(c):
    cert = _draft_cert(c, c.e_col)
    assert refused(c.env, lambda: _rpc(c.env, c.trn, cert._name, "write", cert, {"state": "valid"}))
    assert refused(
        c.env,
        lambda: (
            c.env["fix.certification"]
            .with_user(c.trn)
            .create({"employee_id": c.e_col.id, "competency_id": c.c_lap.id, "state": "valid"})
        ),
    )


@pytest.mark.parametrize(
    "vals,needle",
    [
        ({"assessment_id": False}, "assessment"),
        ({"expires_on": False}, "expiry"),
        ({"evidence_ref": False}, "evidence"),
    ],
)
def test_grant_needs_assessment_expiry_and_evidence(c, vals, needle):
    cert = _draft_cert(c, c.e_col, **vals)
    assert needle in refused(c.env, lambda: cert.with_user(c.trn).action_request_grant()).lower()


def test_grant_needs_a_passed_independent_assessment(c):
    failed = _assessment(c, c.e_col, score=40)
    assert not failed.passed
    cert = _draft_cert(c, c.e_col, assessment_id=failed.id)
    assert "did not pass" in refused(c.env, lambda: cert.with_user(c.trn).action_request_grant())


def test_routed_grant_by_a_verifier(c):
    cert = _draft_cert(c, c.e_col)
    assert refused(c.env, lambda: cert.with_user(c.trn).action_approve_grant())
    cert.with_user(c.trn).action_request_grant()
    assert not _task_for(cert, c.trn) and not _task_for(cert, c.trn2)
    assert refused(c.env, lambda: cert.with_user(c.verifier).action_approve_grant())
    _task_for(cert, c.verifier).with_user(c.verifier).action_approve()
    assert cert.state == "valid" and cert.verified_by_id == c.verifier
    assert _eligible(c, c.e_col)
    assert _events(c.env, "certification.granted", cert.id)


def test_nobody_certifies_themself(c):
    """M22-11/14: the Training Manager self-certification; a verifier is the subject."""
    own = _draft_cert(c, c.e_trn)
    assert "themself" in refused(c.env, lambda: own.with_user(c.trn).action_request_grant())
    e_ver = _employee(c.env, c.verifier)
    theirs = _draft_cert(c, e_ver)
    theirs.with_user(c.trn).action_request_grant()
    assert not _task_for(theirs, c.verifier)


def test_no_duplicate_valid_certificate(c):
    _granted(c, c.e_col)
    twin = _draft_cert(c, c.e_col)
    assert "already holds" in refused(c.env, lambda: twin.with_user(c.trn).action_request_grant())


def test_granted_certificate_is_never_re_dated(c):
    """M22-17: a lapsed certificate revived by typing +5 years."""
    cert = _granted(c, c.e_col)
    for vals in (
        {"expires_on": c.today + timedelta(days=1800)},
        {"evidence_ref": "forged"},
        {"employee_id": c.e_uncert.id},
    ):
        assert refused(c.env, lambda v=vals: _rpc(c.env, c.trn, cert._name, "write", cert, v))
    lapsed = c.env["fix.certification"].create(
        {
            "employee_id": c.e_uncert.id,
            "competency_id": c.c_lap.id,
            "issued_on": c.today - timedelta(days=800),
            "expires_on": c.today - timedelta(days=10),
        }
    )
    lapsed._fix_lapse_expired()
    assert lapsed.state == "lapsed"
    assert refused(
        c.env,
        lambda: _rpc(
            c.env,
            c.trn,
            lapsed._name,
            "write",
            lapsed,
            {"expires_on": c.today + timedelta(days=1800)},
        ),
    )


def test_renewal_is_a_new_granted_certificate(c):
    old = _granted(c, c.e_col)
    out = old.with_user(c.trn).action_renew()
    new = c.env["fix.certification"].browse(out["renewal_ids"])
    assert new.state == "draft" and new.renewal_of_id == old
    new.with_user(c.trn).write(
        {
            "expires_on": c.today + timedelta(days=1400),
            "evidence_ref": "DOC/A9/RENEW",
            "assessment_id": _assessment(c, c.e_col).id,
        }
    )
    new.with_user(c.trn).action_request_grant()
    _task_for(new, c.verifier).with_user(c.verifier).action_approve()
    assert new.state == "valid" and old.state == "superseded"


# ============================================================ suspend (M22-F8)
def test_suspension_blocks_dispatch_at_once(c):
    cert = _granted(c, c.e_col)
    assert refused(c.env, lambda: cert.with_user(c.trn).action_suspend(reason=""))
    cert.with_user(c.trn).action_suspend(reason="quality incident A09")
    assert cert.state == "suspended" and not _eligible(c, c.e_col)
    suspender_verifier = _user(c.env, VERIFIER, TRAINING)
    cert2 = _granted(c, c.e_uncert)
    cert2.with_user(suspender_verifier).action_suspend(reason="investigation")
    assert refused(
        c.env, lambda: cert2.with_user(suspender_verifier).action_reinstate(reason="cleared")
    )
    assert refused(c.env, lambda: cert.with_user(c.trn).action_reinstate(reason="cleared"))
    cert.with_user(c.verifier).action_reinstate(reason="cleared by QA")
    assert cert.state == "valid" and _eligible(c, c.e_col)


def test_revocation_is_final(c):
    cert = _granted(c, c.e_col)
    cert.with_user(c.trn).action_revoke(reason="fraudulent certificate")
    assert cert.state == "revoked" and not _eligible(c, c.e_col)
    assert refused(c.env, lambda: cert.with_user(c.verifier).action_reinstate(reason="x"))


# ============================================================ expiry (M22-F5, C5)
def test_expiry_cron_exists_and_is_active(odoo_env):
    cron = odoo_env.ref("cd_competency.ir_cron_certification_expiry")
    assert cron.active and cron.model_id.model == "fix.certification"
    assert "_cron_certification_expiry" in cron.code


def test_cron_lapses_and_alerts_once(c):
    Cert = c.env["fix.certification"]
    expired = Cert.create(
        {
            "employee_id": c.e_col.id,
            "competency_id": c.c_lap.id,
            "issued_on": c.today - timedelta(days=400),
            "expires_on": c.today - timedelta(days=1),
        }
    )
    mgr_user = _user(c.env)
    c.e_uncert.parent_id = _employee(c.env, mgr_user)
    soon = Cert.create(
        {
            "employee_id": c.e_uncert.id,
            "competency_id": c.c_lap.id,
            "issued_on": c.today - timedelta(days=300),
            "expires_on": c.today + timedelta(days=5),
        }
    )
    Cert._cron_certification_expiry()
    Cert._cron_certification_expiry()  # idempotent
    assert expired.state == "lapsed"
    assert len(_events(c.env, "certification.expired", expired.id)) == 1
    assert soon.state == "valid" and soon.expiry_alerted_on == c.today
    assert len(_events(c.env, "certification.expiring", soon.id)) == 1
    assert soon.activity_ids.filtered(lambda a: a.user_id == mgr_user)


def test_status_and_heatmap_follow_the_calendar(c):
    """M22-09: a certificate 3 days past expiry still read 'expiring'."""
    rec = _granted(c, c.e_col)
    rec.flush_recordset()
    c.env.cr.execute(
        "UPDATE fix_certification SET expires_on=%s WHERE id=%s",
        (c.today - timedelta(days=3), rec.id),
    )
    rec.invalidate_recordset()
    heat = a09.m22.skill_gap_heatmap(c.env)
    row = next(r for r in heat["rows"] if r["code"] == "A9LAP")
    assert rec.status == "expired" and row["certified"] == 0
    assert not _eligible(c, c.e_col)


# ============================================================ training (M22-F4/F9/F10)
def _enrol(c, employee):
    return (
        c.env["fix.training.enrollment"]
        .with_user(c.trn)
        .create({"course_id": c.course.id, "employee_id": employee.id})
    )


def test_pass_needs_a_passed_assessment_and_drafts_the_certificate(c):
    enr = _enrol(c, c.e_col)
    assert "assess" in refused(c.env, lambda: enr.with_user(c.trn).action_pass())
    _assessment(c, c.e_col)
    enr.with_user(c.trn).action_pass()
    assert enr.state == "passed" and enr.certification_id.state == "draft"
    assert not _eligible(c, c.e_col), "a training pass made the technician dispatch-eligible"
    assert refused(c.env, lambda: enr.with_user(c.trn).action_pass())
    certs = c.env["fix.certification"].search(
        [("employee_id", "=", c.e_col.id), ("competency_id", "=", c.c_lap.id)]
    )
    assert len(certs) == 1


def test_failed_enrolment_is_final(c):
    enr = _enrol(c, c.e_col)
    enr.with_user(c.trn).action_fail()
    _assessment(c, c.e_col)
    assert refused(c.env, lambda: enr.with_user(c.trn).action_pass())
    assert refused(c.env, lambda: _rpc(c.env, c.trn, enr._name, "write", enr, {"state": "passed"}))


def test_trainer_cannot_pass_own_enrolment(c):
    enr = _enrol(c, c.e_trn)
    _assessment(c, c.e_trn)
    assert refused(c.env, lambda: enr.with_user(c.trn).action_pass())


def test_enroll_techs_from_the_workspace(c, call):
    """M22-27: the button sent ids, the method wanted a recordset."""
    out = call(
        c.env(user=c.trn.id),
        "model_action",
        model="fix.training.course",
        ids=[c.course.id],
        method="action_enroll",
        kwargs={"employees": "%d, %d" % (c.e_col.id, c.e_uncert.id)},
    )
    assert out.get("success"), out
    assert out["result"]["enrolled"] == 2
    plain_out = call(
        c.env(user=c.plain.id),
        "model_action",
        model="fix.training.course",
        ids=[c.course.id],
        method="action_enroll",
        kwargs={"employees": str(c.e_plain.id)},
    )
    assert not plain_out.get("success")


def test_training_effectiveness_counts_passed(c, call):
    enr = _enrol(c, c.e_col)
    _assessment(c, c.e_col)
    enr.with_user(c.trn).action_pass()
    out = call(c.env(user=c.trn.id), "model_report", module="M22", report="training_effectiveness")
    row = next(r for r in out["rows"] if r["code"] == "A9TRC")
    assert row["completed"] == 1 and row["completion_pct"] == 100.0


# ============================================================ assessments / OJT (M22-F7)
def test_assessor_is_never_the_assessee(c):
    assert refused(c.env, lambda: _assessment(c, c.e_col, assessor=c.e_col))
    assert refused(c.env, lambda: _assessment(c, c.e_trn, user=c.trn))  # by the assessee


def test_passed_follows_the_score_and_cannot_be_ticked(c):
    low = _assessment(c, c.e_col, score=5)
    assert not low.passed
    assert refused(
        c.env,
        lambda: (
            c.env["fix.competency.assessment"]
            .with_user(c.trn)
            .create(
                {
                    "employee_id": c.e_col.id,
                    "competency_id": c.c_lap.id,
                    "assessor_id": c.e_assessor.id,
                    "score": 5,
                    "passed": True,
                }
            )
        ),
    )
    assert refused(c.env, lambda: _rpc(c.env, c.trn, low._name, "write", low, {"score": 95}))
    assert _assessment(c, c.e_col, score=70).passed
    unmarked = c.env["fix.competency"].create({"code": "A9NOPM", "name": "No pass mark"})
    assert not _assessment(c, c.e_col, comp=unmarked, score=100).passed


def test_attempt_limit(c):
    c.c_lap.attempt_limit = 2
    _assessment(c, c.e_col, score=10)
    _assessment(c, c.e_col, score=20)
    assert "attempts" in refused(c.env, lambda: _assessment(c, c.e_col, score=90))


def test_plain_employee_reads_only_own_assessments(c):
    own = _assessment(c, c.e_plain)
    other = _assessment(c, c.e_col)
    seen = c.env(user=c.plain.id)["fix.competency.assessment"].search([])
    assert own in seen and other not in seen


def test_ojt_signed_off_by_the_mentor_only(c):
    mentor_user = _user(c.env)
    mentor = _employee(c.env, mentor_user)
    assert refused(
        c.env,
        lambda: (
            c.env["fix.ojt.record"]
            .with_user(c.trn)
            .create({"employee_id": c.e_trn.id, "mentor_id": c.e_trn.id, "hours": 400})
        ),
    )
    assert refused(
        c.env,
        lambda: (
            c.env["fix.ojt.record"]
            .with_user(c.trn)
            .create(
                {
                    "employee_id": c.e_col.id,
                    "mentor_id": mentor.id,
                    "hours": 40,
                    "outcome": "competent",
                }
            )
        ),
    )
    ojt = (
        c.env["fix.ojt.record"]
        .with_user(c.trn)
        .create({"employee_id": c.e_plain.id, "mentor_id": mentor.id, "hours": 40})
    )
    assert refused(c.env, lambda: ojt.with_user(c.plain).action_sign_off("competent"))
    assert refused(c.env, lambda: ojt.with_user(c.trn).action_sign_off("competent"))
    ojt.with_user(mentor_user).action_sign_off("competent")
    assert ojt.outcome == "competent" and ojt.signed_off_by_id == mentor_user
    assert refused(c.env, lambda: _rpc(c.env, c.trn, ojt._name, "write", ojt, {"hours": 900}))


# ============================================================ ISO evidence (M22-F6)
def _evidence(c, **vals):
    return (
        c.env["fix.audit.evidence"]
        .with_user(c.trn)
        .create({"evidence_type": "iso_9001", "standard_ref": "7.2", **vals})
    )


def test_evidence_needs_a_file_and_a_different_acceptor(c):
    ev = _evidence(c)
    assert "file" in refused(c.env, lambda: ev.with_user(c.trn).action_submit())
    ev.with_user(c.trn).write({"evidence_file": "YTA5", "evidence_filename": "a09.pdf"})
    ev.with_user(c.trn).action_submit()
    assert refused(c.env, lambda: ev.with_user(c.trn).action_accept())  # not a verifier
    both = _user(c.env, TRAINING, VERIFIER)
    ev2 = (
        c.env["fix.audit.evidence"]
        .with_user(both)
        .create({"evidence_type": "iso_9001", "evidence_file": "YTA5"})
    )
    ev2.with_user(both).action_submit()
    assert refused(c.env, lambda: ev2.with_user(both).action_accept())  # own submission
    ev.with_user(c.verifier).action_accept()
    assert ev.state == "accepted" and ev.accepted_by_id == c.verifier
    assert refused(c.env, lambda: _rpc(c.env, c.trn, ev._name, "write", ev, {"reference": "x"}))


def test_evidence_state_not_writable_via_workspace(c, call):
    ev = _evidence(c)
    call(
        c.env(user=c.trn.id),
        "model_write",
        model="fix.audit.evidence",
        record_id=ev.id,
        values={"state": "accepted"},
    )
    assert ev.state == "draft"
    assert refused(c.env, lambda: _rpc(c.env, c.trn, ev._name, "write", ev, {"state": "accepted"}))


# ============================================================ work order gate (M22-F2/F3)
def test_work_order_gate_fails_closed_for_an_uncovered_device(c):
    """M22-03: a smartphone-only technician on an air-conditioner job."""
    _granted(c, c.e_col, c.c_smp)
    # A02 M01-P2: only a dispatcher assigns; the M22 gate fires inside that
    # assignment, so the driver is the dispatcher, not a plain user.
    err = refused(
        c.env,
        lambda: (
            c.env["fix.work.order"]
            .with_user(c.disp)
            .create({"order_id": c.so_ac.id, "technician_id": c.e_col.id})
        ),
    )
    assert err and "fail-closed" in err


def test_work_order_waiver_cannot_be_ticked(c):
    """M22-04: a plain user ticked certification_waiver and assigned anyone."""
    assert refused(
        c.env,
        lambda: (
            c.env["fix.work.order"]
            .with_user(c.plain)
            .create(
                {
                    "order_id": c.so_laptop.id,
                    "technician_id": c.e_uncert.id,
                    "certification_waiver": True,
                }
            )
        ),
    )
    wo = c.env["fix.work.order"].create({"order_id": c.so_laptop.id})
    assert refused(
        c.env, lambda: _rpc(c.env, c.plain, wo._name, "write", wo, {"certification_waiver": True})
    )


def _rostered(c, *employees):
    shift = c.env["fix.shift.template"].create(
        {"name": "A09 M22 day", "start_hour": 9, "end_hour": 18}
    )
    for emp in employees:
        c.env["fix.roster.slot"].create(
            {
                "employee_id": emp.id,
                # the M55 availability check reads the context date
                "date": fields.Date.context_today(c.env["fix.roster.slot"]),
                "shift_id": shift.id,
            }
        )


def test_an_approved_waiver_covers_one_technician_on_one_job(c):
    other = _employee(c.env)
    _rostered(c, c.e_uncert, other)
    wo = c.env["fix.work.order"].create({"order_id": c.so_laptop.id})
    Waiver = c.env["fix.certification.waiver"]
    # RAP X-02: a plain user cannot create the record itself...
    assert refused(
        c.env,
        lambda: Waiver.with_user(c.plain).create(
            {
                "employee_id": c.e_uncert.id,
                "res_model": "fix.work.order",
                "res_id": wo.id,
                "reason": "no certified technician within 50 km today",
            }
        ),
    )
    # ...they ask from the job, with a reason, never for themself
    WO = wo.with_user(c.plain)
    assert refused(c.env, lambda: WO.action_request_certification_waiver(c.e_uncert.id, "x"))
    assert refused(
        c.env,
        lambda: WO.action_request_certification_waiver(
            c.e_plain.id, "no certified tech within 50 km"
        ),
    )
    out = WO.action_request_certification_waiver(
        waiver="%d no certified technician within 50 km today" % c.e_uncert.id
    )
    waiver = Waiver.browse(out["waiver_id"])
    assert waiver.requester_id == c.plain and waiver.approval_state == "pending"
    assert refused(c.env, lambda: waiver.with_user(c.override).action_approve())
    assert not _task_for(waiver, c.plain)
    _task_for(waiver, c.override).with_user(c.override).action_approve()
    assert waiver.state == "approved" and wo.certification_waiver_id == waiver
    # A02 M01-P2: the waived technician is assigned by the dispatcher; the
    # approved waiver is what lets the M22 gate let them through.
    wo.with_user(c.disp).write({"technician_id": c.e_uncert.id})
    assert wo.technician_id == c.e_uncert
    # another technician is not covered: the waiver drops and the gate holds
    assert refused(c.env, lambda: wo.with_user(c.disp).write({"technician_id": other.id}))


def test_the_requester_never_approves_their_waiver(c):
    both = _user(c.env, OVERRIDE)
    wo = c.env["fix.work.order"].create({"order_id": c.so_laptop.id})
    out = wo.with_user(both).action_request_certification_waiver(
        c.e_uncert.id, "no certified technician within 50 km today"
    )
    waiver = c.env["fix.certification.waiver"].browse(out["waiver_id"])
    assert not _task_for(waiver, both) and _task_for(waiver, c.override)


def test_certified_technician_is_assigned(c):
    _granted(c, c.e_col)
    # A02 M01-P2: assignment is a dispatcher act; the certified technician
    # passes the M22 gate that runs inside it.
    wo = (
        c.env["fix.work.order"]
        .with_user(c.disp)
        .create({"order_id": c.so_laptop.id, "technician_id": c.e_col.id})
    )
    assert wo.technician_id == c.e_col


# ============================================================ field order gate (M22-F1, C4)
def _field_order(c, so=None):
    return c.env["fix.field.order"].create(
        {"order_id": (so or c.so_laptop).id, "zone_id": c.zone.id, "operating_unit_id": c.ou.id}
    )


def test_field_dispatch_refuses_an_uncertified_technician(c):
    fo = _field_order(c)
    err = refused(c.env, lambda: fo.with_user(c.disp).action_dispatch(technician_id=c.e_uncert.id))
    assert err and "M22 eligibility" in err
    assert fo.state != "dispatched" and not fo.technician_id


def test_field_dispatch_fails_closed_for_an_uncovered_device(c):
    _granted(c, c.e_col, c.c_smp)
    fo = _field_order(c, c.so_ac)
    assert "fail-closed" in refused(
        c.env, lambda: fo.with_user(c.disp).action_dispatch(technician_id=c.e_col.id)
    )


def test_field_dispatch_and_reassign_need_certification(c):
    _granted(c, c.e_col)
    fo = _field_order(c)
    fo.with_user(c.disp).action_dispatch(technician_id=c.e_col.id)
    assert fo.state == "dispatched" and fo.technician_id == c.e_col
    err = refused(
        c.env,
        lambda: fo.with_user(c.disp).action_reassign(
            reassignment="%d customer asked for another" % c.e_uncert.id
        ),
    )
    assert err and "M22 eligibility" in err
    assert fo.technician_id == c.e_col


def test_field_dispatch_with_an_approved_waiver(c):
    fo = _field_order(c)
    assert refused(c.env, lambda: fo.with_user(c.disp).action_dispatch(technician_id=c.e_uncert.id))
    assert refused(
        c.env,
        lambda: fo.with_user(c.plain).action_request_certification_waiver(
            c.e_uncert.id, "flood: no certified technician can reach the site"
        ),
    )
    out = fo.with_user(c.disp).action_request_certification_waiver(
        waiver="%d flood: no certified technician can reach the site" % c.e_uncert.id
    )
    waiver = c.env["fix.certification.waiver"].browse(out["waiver_id"])
    assert not _task_for(waiver, c.disp)
    assert refused(c.env, lambda: fo.with_user(c.disp).action_dispatch(technician_id=c.e_uncert.id))
    _task_for(waiver, c.override).with_user(c.override).action_approve()
    fo.with_user(c.disp).action_dispatch(technician_id=c.e_uncert.id)
    assert fo.technician_id == c.e_uncert


# ============================================================ workspace / deployment
def test_competency_scope_names_real_device_types(c):
    """M22-F2: fix_dev's 'home_appliance' matched no device."""
    assert refused(
        c.env,
        lambda: c.env["fix.competency"].create(
            {"code": "A9APP", "name": "A09 Appliance", "device_type": "home_appliance"}
        ),
    )


def test_workspace_actions(odoo_env):
    cert_actions = a09.SURFACES["fix.certification"]["actions"]
    assert {
        "action_grant",
        "action_suspend",
        "action_reinstate",
        "action_revoke",
        "action_renew",
    } <= cert_actions
    assert "action_approve_grant" not in cert_actions
    assert {"action_pass", "action_fail"} <= a09.SURFACES["fix.training.enrollment"]["actions"]
    assert {"action_sign_off"} <= a09.SURFACES["fix.ojt.record"]["actions"]
    assert {"action_reject"} <= a09.SURFACES["fix.audit.evidence"]["actions"]


def test_groups_and_access_rows(odoo_env):
    admin_root = odoo_env.ref("base.user_admin") | odoo_env.ref("base.user_root")
    for xmlid in (VERIFIER, OVERRIDE):
        assert odoo_env.ref(xmlid).user_ids <= admin_root
    plain_rows = (
        odoo_env["ir.model.access"]
        .sudo()
        .search(
            [
                ("model_id.model", "=", "fix.certification.waiver"),
                ("group_id", "=", odoo_env.ref("base.group_user").id),
            ]
        )
    )
    assert plain_rows and not any(
        plain_rows.mapped("perm_write") + plain_rows.mapped("perm_create")
    )
    Access = odoo_env["ir.model.access"].sudo()
    for model, group in (
        ("fix.certification", VERIFIER),
        ("fix.audit.evidence", VERIFIER),
        ("fix.certification.waiver", OVERRIDE),
        ("fix.certification.waiver", TRAINING),
    ):
        assert Access.search_count(
            [("model_id.model", "=", model), ("group_id", "=", odoo_env.ref(group).id)]
        ), (model, group)


# ============================================================ the gate through the workspace
def test_workspace_write_cannot_assign_an_uncertified_work_order_technician(c, call):
    _rostered(c, c.e_uncert)
    wo = c.env["fix.work.order"].create({"order_id": c.so_laptop.id})
    # A02 M01-P2: the workspace write comes from a dispatcher; M22 is the
    # control under test and it must refuse the uncertified technician.
    out = call(
        c.env(user=c.disp.id),
        "model_write",
        model="fix.work.order",
        record_id=wo.id,
        values={"technician_id": c.e_uncert.id},
    )
    assert "error" in out and "M22 eligibility" in out["error"], out
    assert not wo.technician_id


def test_workspace_write_cannot_assign_a_field_order_technician(c, call):
    fo = _field_order(c)
    out = call(
        c.env(user=c.disp.id),
        "model_write",
        model="fix.field.order",
        record_id=fo.id,
        values={"technician_id": c.e_uncert.id},
    )
    assert not fo.technician_id, out


def test_workspace_dispatch_action_refuses_an_uncertified_technician(c, call):
    fo = _field_order(c)
    # the workspace dispatches by saving a fix.dispatch.decision (M02 capture
    # audit 18 Nov); the decision runs action_dispatch and so the M22 gate
    out = call(
        c.env(user=c.disp.id),
        "model_write",
        model="fix.dispatch.decision",
        values={
            "field_order_id": fo.id,
            "technician_id": c.e_uncert.id,
            "override_reason": "other",
            "override_notes": "M22 control test",
        },
    )
    assert "M22 eligibility" in out.get("error", ""), out
    assert not fo.env["fix.dispatch.decision"].sudo().search([("field_order_id", "=", fo.id)])
    assert not fo.technician_id


def test_a_user_cannot_create_a_field_order_already_assigned(c):
    assert refused(
        c.env,
        lambda: (
            c.env["fix.field.order"]
            .with_user(c.disp)
            .create(
                {
                    "order_id": c.so_laptop.id,
                    "zone_id": c.zone.id,
                    "operating_unit_id": c.ou.id,
                    "technician_id": c.e_uncert.id,
                }
            )
        ),
    )
