# A09 round 2, M22 acceptance suite: the certification and training event
# consumers, the start-of-work gate, the statutory / safety certification
# class (BRU-LMS-07), the training budget (BRU-LMS-10), the attempt-limit
# escalation (BRU-LMS-09) and the repair tier on work orders.
#
# Attacked as freshly created NON-admin users; events travel through the real
# relay (fix.event.outbox.cron_relay -> fix.event.consumer rows).
#
# The `c` and `call` fixtures are the round-1 suite's (imported), so every
# test function's `c` parameter "redefines" the imported name.
# ruff: noqa: F811
from datetime import timedelta

from odoo import fields
from odoo.addons.cd_competency.tests.test_a09_m22_controls import (  # noqa: F401 (fixtures)
    DISPATCHER,
    TRAINING,
    _assessment,
    _employee,
    _enrol,
    _events,
    _field_order,
    _granted,
    _rostered,
    _rpc,
    _task_for,
    _user,
    c,
    call,
    refused,
)
from odoo.addons.cd_p03_portal.controllers import a09

BUDGET = "cd_competency.group_training_budget_approver"
HSE = "cd_hse.group_hse_officer"


def _relay(env):
    env.flush_all()
    env["fix.event.outbox"].sudo().cron_relay()
    env.flush_all()


def _activities(rec, user=None):
    dom = [("res_model", "=", rec._name), ("res_id", "=", rec.id)]
    if user:
        dom.append(("user_id", "=", user.id))
    return rec.env["mail.activity"].sudo().search(dom)


def _tech(c):
    # a field technician (Field Service / Technician) progresses their own order
    user = _user(c.env, "cd_field_service.group_fix_field_service_user")
    return user, _employee(c.env, user)


# ====================================================== consumers (deployment)
def test_the_consumers_are_registered(odoo_env):
    for xmlid, event_type, method in (
        ("consumer_certification_expired", "certification.expired", "consume_certification_lost"),
        (
            "consumer_certification_suspended",
            "certification.suspended",
            "consume_certification_lost",
        ),
        ("consumer_certification_revoked", "certification.revoked", "consume_certification_lost"),
        ("consumer_training_passed", "training.passed", "consume_training_passed"),
    ):
        sub = odoo_env.ref("cd_competency.%s" % xmlid)
        assert sub.active and sub.event_type == event_type and sub.method == method
        assert callable(getattr(odoo_env[sub.model], sub.method))


# ====================================================== certification lost -> jobs
def test_a_suspension_flags_the_not_started_work_order_and_stops_its_start(c):
    disp = _user(c.env, DISPATCHER)
    _rostered(c, c.e_col)
    _granted(c, c.e_col)
    # A02 M01-P2: a dispatcher assigns the technician (create-with-technician
    # is a dispatcher act); state moves only through a transition, so the job
    # sits at 'pending' until work starts.
    wo = (
        c.env["fix.work.order"]
        .with_user(c.disp)
        .create({"order_id": c.so_laptop.id, "technician_id": c.e_col.id})
    )
    cert = c.env["fix.certification"].search(
        [("employee_id", "=", c.e_col.id), ("state", "=", "valid")]
    )
    cert.with_user(c.trn).action_suspend("quality incident under investigation")
    _relay(c.env)
    acts = _activities(wo)
    assert len(acts) == 1 and "certification suspended" in acts.summary.lower()
    assert acts.user_id in (disp | c.env.ref(DISPATCHER).all_user_ids)
    assert wo.state == "pending" and wo.technician_id == c.e_col, "the consumer moved the job"
    # the start itself is a privileged transition; M22 still gates it: the
    # suspended technician's job cannot start.
    err = refused(c.env, lambda: wo.sudo().write({"state": "in_progress"}))
    assert err and "cannot start" in err
    # a redelivery does not raise a second to-do
    c.env["fix.certification"].consume_certification_lost(
        {"aggregate_id": cert.id, "event_type": "certification.suspended"}
    )
    assert len(_activities(wo)) == 1


def test_a_started_or_still_covered_job_is_not_flagged(c):
    _rostered(c, c.e_col)
    _granted(c, c.e_col)
    started = c.env["fix.work.order"].create(
        {"order_id": c.so_laptop.id, "technician_id": c.e_col.id}
    )
    started.write({"state": "in_progress"})
    _granted(c, c.e_col, c.c_smp)  # a second certification, for another device
    cert = c.env["fix.certification"].search(
        [("employee_id", "=", c.e_col.id), ("competency_id", "=", c.c_smp.id)]
    )
    cert.with_user(c.trn).action_revoke("wrong device family")
    _relay(c.env)
    assert not _activities(started)


def test_an_expiry_flags_a_dispatched_field_order_and_stops_its_start(c):
    tech_user, tech = _tech(c)
    _granted(c, tech)
    fo = _field_order(c)
    fo.with_user(c.disp).action_dispatch(technician_id=tech.id)
    cert = c.env["fix.certification"].search(
        [("employee_id", "=", tech.id), ("state", "=", "valid")]
    )
    c.env.cr.execute(
        "UPDATE fix_certification SET expires_on=%s WHERE id=%s",
        (fields.Date.today() - timedelta(days=1), cert.id),
    )
    cert.invalidate_recordset()
    c.env["fix.certification"]._cron_certification_expiry()
    assert cert.state == "lapsed"
    _relay(c.env)
    acts = _activities(fo)
    assert len(acts) == 1 and "expired" in acts.summary
    assert fo.state == "dispatched" and fo.technician_id == tech
    fo.sudo()._guarded().write({"state": "arrived"})
    err = refused(c.env, lambda: fo.with_user(tech_user).action_start_work())
    assert err and "M22 eligibility" in err
    assert fo.state == "arrived"


def test_a_certified_technician_starts_field_work(c):
    tech_user, tech = _tech(c)
    _granted(c, tech)
    fo = _field_order(c)
    fo.with_user(c.disp).action_dispatch(technician_id=tech.id)
    fo.sudo()._guarded().write({"state": "arrived"})
    fo.with_user(tech_user).action_start_work()
    assert fo.state == "in_progress"


# ====================================================== safety class (BRU-LMS-07)
def test_a_lapsed_safety_certification_is_escalated_to_hse(c):
    hse = _user(c.env, HSE)
    c.c_lap.certification_class = "safety"
    cert = _granted(c, c.e_col)
    c.env.cr.execute(
        "UPDATE fix_certification SET expires_on=%s WHERE id=%s",
        (fields.Date.today() - timedelta(days=1), cert.id),
    )
    cert.invalidate_recordset()
    c.env["fix.certification"]._cron_certification_expiry()
    assert cert.state == "lapsed"
    assert _activities(cert, hse), "no HSE Officer was told"
    events = _events(c.env, "certification.safety_lapsed", cert.id)
    assert events and events[0]["employee_id"] == c.e_col.id
    # the cron is idempotent: a second sweep raises nothing new
    c.env["fix.certification"]._cron_certification_expiry()
    assert len(_events(c.env, "certification.safety_lapsed", cert.id)) == 1


def test_an_operational_lapse_is_not_an_hse_escalation(c):
    cert = _granted(c, c.e_col)
    c.env.cr.execute(
        "UPDATE fix_certification SET expires_on=%s WHERE id=%s",
        (fields.Date.today() - timedelta(days=1), cert.id),
    )
    cert.invalidate_recordset()
    c.env["fix.certification"]._cron_certification_expiry()
    assert cert.state == "lapsed"
    assert not _events(c.env, "certification.safety_lapsed", cert.id)


def test_the_class_is_set_by_the_training_manager_only(c):
    assert refused(
        c.env,
        lambda: _rpc(
            c.env, c.plain, "fix.competency", "write", c.c_lap, {"certification_class": "standard"}
        ),
    )


# ====================================================== training.passed (consumer)
def test_a_passed_training_records_its_competence_evidence(c):
    enr = _enrol(c, c.e_col)
    _assessment(c, c.e_col)
    enr.with_user(c.trn).action_pass()
    _relay(c.env)
    ev = enr.evidence_id
    assert ev and ev.employee_id == c.e_col and ev.evidence_type == "skills_audit"
    assert ev.state == "draft", "the consumer must not accept its own evidence"
    assert enr.evidence_recorded_at
    c.env["fix.training.enrollment"].consume_training_passed({"aggregate_id": enr.id})
    assert c.env["fix.audit.evidence"].search_count([("employee_id", "=", c.e_col.id)]) == 1
    assert refused(
        c.env, lambda: _rpc(c.env, c.trn, enr._name, "write", enr, {"evidence_id": False})
    )


# ====================================================== training budget (BRU-LMS-10)
def _budgeted(c, amount=2500.0, cost=1000.0):
    approver = _user(c.env, BUDGET)
    c.course.cost_per_seat = cost
    budget = (
        c.env["fix.training.budget"]
        .with_user(approver)
        .create({"year": fields.Date.today().year, "amount": amount})
    )
    return approver, budget


def test_no_budget_means_no_budget_check(c):
    c.course.cost_per_seat = 1000000.0
    enr = _enrol(c, c.e_col)
    assert enr.cost == 1000000.0 and enr.budget_year == fields.Date.today().year


def test_an_enrolment_past_the_budget_needs_a_routed_approval(c):
    approver, budget = _budgeted(c)
    a, b, d, e = (_employee(c.env) for _i in range(4))
    _enrol(c, a)
    _enrol(c, b)
    assert budget.consumed == 2000.0 and budget.remaining == 500.0
    err = refused(c.env, lambda: _enrol(c, d))
    assert err and "BRU-LMS-10" in err
    req = (
        c.env["fix.training.budget.exception"]
        .with_user(c.trn)
        .create(
            {
                "course_id": c.course.id,
                "seats": 1,
                "employee_ids": [(6, 0, [d.id])],
                "reason": "brand audit next month needs a third certified technician",
            }
        )
    )
    assert req.amount == 1000.0
    assert refused(c.env, lambda: req.with_user(approver).action_approve())
    req.with_user(c.trn).action_request_approval()
    assert req.state == "pending" and not _task_for(req, c.trn)
    _task_for(req, approver).with_user(approver).action_approve()
    assert req.state == "approved" and req.approved_by_id == approver
    assert refused(c.env, lambda: _enrol(c, e)), "the approval named another technician"
    enr = _enrol(c, d)
    assert enr.budget_exception_id == req
    # the one seat is used
    req.sudo().employee_ids = False
    assert refused(c.env, lambda: _enrol(c, e))


def test_the_requester_never_approves_their_over_budget_request(c):
    both = _user(c.env, TRAINING, BUDGET)
    approver, _budget = _budgeted(c)
    req = (
        c.env["fix.training.budget.exception"]
        .with_user(both)
        .create({"course_id": c.course.id, "seats": 2, "reason": "two extra seats"})
    )
    req.with_user(both).action_request_approval()
    assert not _task_for(req, both) and _task_for(req, approver)


def test_cost_and_budget_fields_are_not_typed(c):
    _budgeted(c)
    assert refused(
        c.env,
        lambda: (
            c.env["fix.training.enrollment"]
            .with_user(c.trn)
            .create({"course_id": c.course.id, "employee_id": c.e_col.id, "cost": 5.0})
        ),
    )
    enr = _enrol(c, c.e_col)
    assert refused(c.env, lambda: _rpc(c.env, c.trn, enr._name, "write", enr, {"cost": 0.0}))
    assert refused(
        c.env,
        lambda: (
            c.env["fix.training.budget"]
            .with_user(c.trn)
            .create({"year": fields.Date.today().year + 1, "amount": 99999999.0})
        ),
    )


def test_a_decided_over_budget_request_keeps_its_terms(c):
    _approver, _budget = _budgeted(c)
    req = (
        c.env["fix.training.budget.exception"]
        .with_user(c.trn)
        .create({"course_id": c.course.id, "seats": 1, "reason": "one extra seat"})
    )
    req.with_user(c.trn).action_request_approval()
    assert refused(c.env, lambda: _rpc(c.env, c.trn, req._name, "write", req, {"seats": 50}))
    assert refused(
        c.env, lambda: _rpc(c.env, c.trn, req._name, "write", req, {"state": "approved"})
    )


# ====================================================== attempt limit (BRU-LMS-09)
def test_reaching_the_attempt_limit_escalates_to_a_training_manager(c):
    c.c_lap.attempt_limit = 2
    first = _assessment(c, c.e_col, score=10)
    assert not first.attempt_escalated
    second = _assessment(c, c.e_col, score=20)  # recorded by trn2
    assert second.attempt_escalated
    acts = _activities(second)
    assert acts and c.trn in acts.mapped("user_id"), "the training manager got no task"
    assert c.trn2 not in acts.mapped("user_id"), "the recorder was asked to decide"
    assert "escalated" in refused(c.env, lambda: _assessment(c, c.e_col, score=90))
    # the recorder and the technician do not grant the retake
    assert refused(c.env, lambda: second.with_user(c.trn2).action_grant_retake("again"))
    assert refused(c.env, lambda: second.with_user(c.plain).action_grant_retake("again"))
    assert refused(c.env, lambda: second.with_user(c.trn).action_grant_retake(""))
    assert refused(
        c.env,
        lambda: _rpc(c.env, c.trn, second._name, "write", second, {"attempt_escalated": False}),
    )
    second.with_user(c.trn).action_grant_retake("retrained on BGA rework")
    assert second.retake_granted_by_id == c.trn and not _activities(second)
    assert _assessment(c, c.e_col, score=90).passed


# ====================================================== repair tier on work orders
def test_the_work_order_tier_is_passed_to_the_eligibility_check(c):
    _rostered(c, c.e_col)
    c.c_lap.repair_tier = "l2"
    _granted(c, c.e_col)
    wo = c.env["fix.work.order"].create({"order_id": c.so_laptop.id, "repair_tier": "l3"})
    # A02 M01-P2: the assignment write comes from the dispatcher; the tier
    # gate (M22) is the control under test.
    err = refused(
        c.env, lambda: _rpc(c.env, c.disp, wo._name, "write", wo, {"technician_id": c.e_col.id})
    )
    assert err and "tier" in err.lower()
    low = c.env["fix.work.order"].create({"order_id": c.so_laptop.id, "repair_tier": "l2"})
    low.with_user(c.disp).write({"technician_id": c.e_col.id})
    assert low.technician_id == c.e_col
    # raising the tier of an assigned job re-checks it
    assert refused(
        c.env, lambda: _rpc(c.env, c.plain, low._name, "write", low, {"repair_tier": "l4"})
    )
    assert low.repair_tier == "l2"


# ====================================================== deployment / workspace
def test_round2_groups_access_and_surfaces(odoo_env):
    admin_root = odoo_env.ref("base.user_admin") | odoo_env.ref("base.user_root")
    assert odoo_env.ref(BUDGET).user_ids <= admin_root
    Access = odoo_env["ir.model.access"].sudo()
    for model, group in (
        ("fix.training.budget", BUDGET),
        ("fix.training.budget.exception", BUDGET),
        ("fix.training.budget.exception", TRAINING),
    ):
        assert Access.search_count(
            [("model_id.model", "=", model), ("group_id", "=", odoo_env.ref(group).id)]
        ), (model, group)
    plain = Access.search(
        [
            ("group_id", "=", odoo_env.ref("base.group_user").id),
            ("model_id.model", "in", ["fix.training.budget", "fix.training.budget.exception"]),
        ]
    )
    assert not plain
    s = a09.SURFACES
    assert {"action_grant_retake"} <= s["fix.competency.assessment"]["actions"]
    assert {"action_request_approval", "action_cancel"} <= s["fix.training.budget.exception"][
        "actions"
    ]
    assert "action_approve" not in s["fix.training.budget.exception"]["actions"]
    assert "state" not in s["fix.training.budget.exception"]["writable"]
    assert "cost" not in s["fix.training.enrollment"]["writable"]


# ====================================================== vehicle work (FR-HSE-019)
# cd_hse provides hr.employee._fix_driving_licence(date) -> (fix.driver, reason);
# cd_competency does not depend on it, so the tests stand it in.
def _licence(valid=True, reason="the driving licence of X expired on 2026-01-01"):
    def check(day):
        return (object() if valid else False), ("" if valid else reason)

    return check


def _patch_licence(monkeypatch, check):
    from odoo.addons.cd_competency.models import fix_competency

    monkeypatch.setattr(fix_competency, "licence_checker", lambda employee: check)


def test_vehicle_work_needs_a_valid_driving_licence(c, monkeypatch):
    _granted(c, c.e_col)
    Cert = c.env["fix.certification"]
    _patch_licence(monkeypatch, _licence(True))
    assert Cert.dispatch_eligibility(c.e_col, device_type="laptop", requires_vehicle=True)[0]
    _patch_licence(monkeypatch, _licence(False))
    ok, reason = Cert.dispatch_eligibility(c.e_col, device_type="laptop", requires_vehicle=True)
    assert not ok and "FR-HSE-019" in reason and "expired" in reason
    # no vehicle: the licence is not asked for
    assert Cert.dispatch_eligibility(c.e_col, device_type="laptop")[0]


def test_vehicle_work_fails_closed_when_the_licence_cannot_be_checked(c, monkeypatch):
    _granted(c, c.e_col)
    Cert = c.env["fix.certification"]
    _patch_licence(monkeypatch, None)  # cd_hse not installed
    ok, reason = Cert.dispatch_eligibility(c.e_col, device_type="laptop", requires_vehicle=True)
    assert not ok and "fail-closed" in reason

    def broken(day):
        raise KeyError("fix.driver")

    _patch_licence(monkeypatch, broken)
    ok, reason = Cert.dispatch_eligibility(c.e_col, device_type="laptop", requires_vehicle=True)
    assert not ok and "fail-closed" in reason


def _van(c, technician):
    return c.env["fix.stock.location"].create(
        {
            "name": "A09 r2 van %s" % technician.id,
            "code": "VAN%s" % technician.id,
            "location_type": "van",
            "technician_id": technician.id,
        }
    )


def test_a_field_order_travelling_by_van_checks_the_licence(c, monkeypatch):
    _granted(c, c.e_col)
    van = _van(c, c.e_col)
    assert van.is_van_stock
    fo = _field_order(c)
    _patch_licence(monkeypatch, _licence(False))
    err = refused(c.env, lambda: fo.with_user(c.disp).action_dispatch(technician_id=c.e_col.id))
    assert err and "FR-HSE-019" in err
    assert fo.state != "dispatched"
    _patch_licence(monkeypatch, _licence(True))
    fo.with_user(c.disp).action_dispatch(technician_id=c.e_col.id)
    assert fo.state == "dispatched" and fo.van_location_id == van
    # a licence that lapses after the dispatch stops the work from starting
    _patch_licence(monkeypatch, _licence(False))
    fo.sudo()._guarded().write({"state": "arrived"})
    tech_user = _user(c.env, "cd_field_service.group_fix_field_service_user")
    c.e_col.user_id = tech_user
    assert "FR-HSE-019" in refused(c.env, lambda: fo.with_user(tech_user).action_start_work())


def test_a_field_order_without_a_vehicle_does_not_ask_for_a_licence(c, monkeypatch):
    _granted(c, c.e_col)
    fo = _field_order(c)
    _patch_licence(monkeypatch, _licence(False))
    fo.with_user(c.disp).action_dispatch(technician_id=c.e_col.id)
    assert fo.state == "dispatched" and not fo.van_location_id
