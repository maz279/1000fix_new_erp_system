# M22 capture audit, pass 2 (2026-11-19), on the live ORM: the records the
# spec names on each sub-module page that nothing could capture before.
#
#   page 1  role requirement per competency + gap analysis (FR-LMS-002/005)
#   page 2/4 training need (FR-LMS-031, BRU-LMS-13, lifecycle 8.2)
#   page 4  training plan (FR-LMS-032), feedback (FR-LMS-036),
#           withdrawal / substitution (FR-LMS-021)
#   page 5  mentoring and its interactions (FR-LMS-028)
#   page 6  effectiveness evaluation (FR-LMS-035, BRU-LMS-15)
#
# Attacked as freshly created NON-admin users (the round-1 fixtures).
# ruff: noqa: F811
from datetime import datetime, timedelta

from odoo import fields
from odoo.addons.cd_competency.tests.test_a09_m22_controls import (  # noqa: F401 (fixtures)
    _assessment,
    _employee,
    _rpc,
    _user,
    c,
    call,
    refused,
)

BUDGET_APPROVER = "cd_competency.group_training_budget_approver"


def _need(c, employee=None, user=None, **vals):
    base = {
        "employee_id": (employee or c.e_col).id,
        "competency_id": c.c_lap.id,
        "course_id": c.course.id,
        "description": "Cannot diagnose laptop boards unassisted",
    }
    base.update(vals)
    return c.env["fix.training.need"].with_user(user or c.trn).create(base)


def _plan(c, **vals):
    base = {"name": "FY Plan Mirpur", "period": "annual", "year": fields.Date.today().year}
    base.update(vals)
    return c.env["fix.training.plan"].with_user(c.trn).create(base)


def _session(c, **vals):
    start = datetime.now().replace(microsecond=0) + timedelta(days=2)
    base = {
        "course_id": c.course.id,
        "delivery_mode": "classroom",
        "trainer_id": c.e_assessor.id,
        "venue": "Mirpur lab",
        "date_start": start,
        "date_end": start + timedelta(hours=4),
        "capacity": 1,
    }
    base.update(vals)
    return c.env["fix.training.session"].with_user(c.trn).create(base)


def _enrol(c, employee, session=None):
    vals = {"course_id": c.course.id, "employee_id": employee.id}
    if session:
        vals["session_id"] = session.id
    return c.env["fix.training.enrollment"].with_user(c.trn).create(vals)


# ---------------------------------------------------------------- page 1 / 2
def test_role_requirement_and_gap_analysis_raise_needs_once(c, call):
    seat = c.env["fix.org.position"].create({"name": "M22 Laptop Tech", "headcount": 5})
    c.e_col.position_id = seat
    c.e_uncert.position_id = seat
    path = (
        c.env["fix.learning.path"]
        .with_user(c.trn)
        .create(
            {
                "name": "M22 Laptop path",
                "target_role": "Laptop Technician",
                "position_ids": [(6, 0, seat.ids)],
                "requirement_ids": [(0, 0, {"competency_id": c.c_lap.id, "min_level": "l3"})],
            }
        )
    )
    # a plain user does not set a role requirement
    assert refused(
        c.env,
        lambda: c.env["fix.role.competency"]
        .with_user(c.plain)
        .create({"path_id": path.id, "competency_id": c.c_smp.id}),
    )
    _assessment(c, c.e_col)  # an independent L3 pass: e_col meets it
    # an independent L2 pass is still below the L3 the role requires
    c.env["fix.competency.assessment"].with_user(c.trn2).create(
        {
            "employee_id": c.e_uncert.id,
            "competency_id": c.c_lap.id,
            "assessor_id": c.e_assessor.id,
            "score": 90.0,
            "level": "l2",
        }
    )
    gaps = path.with_user(c.trn)._fix_gap_rows()
    assert [(g["employee"], g["held"], g["gap"]) for g in gaps] == [(c.e_uncert, "l2", 1)], gaps
    out = path.with_user(c.trn).action_raise_gap_needs()
    assert out["raised"] == 1
    need = c.env["fix.training.need"].browse(out["need_ids"])
    assert need.employee_id == c.e_uncert and need.source == "competency_gap"
    assert need.course_id == c.course and need.priority == "high"
    assert path.with_user(c.trn).action_raise_gap_needs()["raised"] == 0, "raised twice"
    rep = call(c.env(user=c.trn.id), "model_report", module="M22", report="role_gap_analysis")
    assert [r["employee"] for r in rep["rows"]] == [c.e_uncert.name]
    assert rep["rows"][0]["need"] == "Open"
    assert refused(c.env, lambda: path.with_user(c.plain).action_raise_gap_needs())


# ---------------------------------------------------------------- needs
def test_a_need_is_raised_by_training_and_safety_is_mandatory(c):
    assert refused(c.env, lambda: _need(c, user=c.plain))
    need = _need(c, source="safety", priority="low")
    assert need.name.startswith("TNR/") and need.priority == "mandatory"
    need.with_user(c.trn).write({"priority": "low"})
    assert need.priority == "mandatory", "AUT-LMS-07: a safety need stays mandatory"
    assert refused(
        c.env, lambda: _rpc(c.env, c.trn, need._name, "write", need, {"state": "closed"})
    )


def test_a_need_is_s2(c):
    mgr = _user(c.env)
    c.e_col.parent_id = _employee(c.env, mgr)
    need = _need(c)
    other = _user(c.env)
    assert need.with_user(mgr).search_count([("id", "=", need.id)]) == 1
    assert need.with_user(other).search_count([("id", "=", need.id)]) == 0


def test_need_closes_on_a_pass_and_reopens_on_a_fail(c):
    need = _need(c)
    need.with_user(c.trn).action_enrol()
    assert need.state == "enrolled" and need.enrollment_id.course_id == c.course
    _assessment(c, c.e_col)
    need.enrollment_id.with_user(c.trn).action_pass()
    assert need.state == "closed" and need.closed_on
    need2 = _need(c, employee=c.e_uncert)
    need2.with_user(c.trn).action_enrol()
    enr = need2.enrollment_id
    enr.with_user(c.trn).action_fail()
    assert need2.state == "identified" and not need2.enrollment_id


# ---------------------------------------------------------------- plan
def test_plan_needs_costed_needs_inside_budget_and_an_independent_approver(c):
    approver = _user(c.env, BUDGET_APPROVER)
    c.course.cost_per_seat = 5000
    plan = _plan(c, budget=6000)
    n1 = _need(c, plan_id=plan.id)
    assert n1.state == "planned"
    # a planned need waits for the plan's approval before enrolment
    assert "not approved" in (refused(c.env, lambda: n1.with_user(c.trn).action_enrol()) or "")
    _need(c, employee=c.e_uncert, plan_id=plan.id)
    assert "budget" in (refused(c.env, lambda: plan.with_user(c.trn).action_submit()) or "")
    plan.with_user(c.trn).write({"budget": 10000})
    plan.with_user(c.trn).action_submit()
    assert plan.state == "submitted" and plan.planned_cost == 10000
    # frozen once submitted; the submitter never decides; a trainer is no approver
    assert refused(c.env, lambda: plan.with_user(c.trn).write({"budget": 1}))
    assert refused(c.env, lambda: plan.with_user(c.trn2).action_approve())
    both = _user(c.env, "cd_competency.group_training", BUDGET_APPROVER)
    plan_b = _plan(c, name="Self plan")
    _need(c, employee=c.e_plain, plan_id=plan_b.id, user=both)
    plan_b.with_user(both).action_submit()
    assert "submitted" in (refused(c.env, lambda: plan_b.with_user(both).action_approve()) or "")
    # a need does not join a submitted plan
    assert refused(c.env, lambda: _need(c, employee=c.e_trn, plan_id=plan.id))
    plan.with_user(approver).action_approve()
    assert plan.state == "approved" and plan.approved_by_id == approver
    n1.with_user(c.trn).action_enrol()
    assert n1.state == "enrolled"


def test_cancelling_a_plan_releases_its_needs(c):
    plan = _plan(c)
    need = _need(c, plan_id=plan.id)
    plan.with_user(c.trn).action_cancel()
    assert plan.state == "cancelled" and need.state == "identified" and not need.plan_id


# ---------------------------------------------------------------- enrolment
def test_withdrawal_frees_the_seat_and_its_cost_and_substitution_takes_it(c):
    c.course.cost_per_seat = 1200
    sess = _session(c, capacity=1)
    first = _enrol(c, c.e_col, sess)
    assert first.cost == 1200
    assert "full" in (refused(c.env, lambda: _enrol(c, c.e_uncert, sess)) or "")
    assert refused(c.env, lambda: first.with_user(c.plain).action_withdraw(reason="ill"))
    assert refused(c.env, lambda: first.with_user(c.trn).action_withdraw(reason=" "))
    out = first.with_user(c.trn).action_substitute(employee=str(c.e_uncert.id))
    sub = c.env["fix.training.enrollment"].browse(out["enrollment_id"])
    assert first.state == "withdrawn" and first.cost == 0.0
    assert sub.employee_id == c.e_uncert and sub.session_id == sess
    assert sub.substitute_of_id == first and sess.seats_taken == 1
    # the session closes without the withdrawn trainee's attendance
    sess.with_user(c.trn).action_schedule()
    sub.with_user(c.trn).action_mark_attended()
    sess.with_user(c.trn).action_mark_held()
    assert sess.state == "done"
    assert refused(c.env, lambda: sub.with_user(c.trn).action_withdraw(reason="late"))


def test_feedback_is_the_trainees_own_after_attending(c):
    trainee_user = _user(c.env)
    trainee = _employee(c.env, trainee_user)
    sess = _session(c, capacity=3)
    enr = _enrol(c, trainee, sess)
    vals = {
        "enrollment_id": enr.id,
        "rating_content": "4",
        "rating_trainer": "5",
        "rating_applicability": "4",
    }
    Feedback = c.env["fix.training.feedback"]
    assert "attended" in (
        refused(c.env, lambda: Feedback.with_user(trainee_user).create(vals)) or ""
    )
    sess.with_user(c.trn).action_schedule()
    enr.with_user(c.trn).action_mark_attended()
    assert refused(c.env, lambda: Feedback.with_user(c.plain).create(vals))
    assert refused(
        c.env, lambda: Feedback.with_user(c.trn).create(vals)
    ), "a manager does not speak for a trainee who has an account"
    fb = Feedback.with_user(trainee_user).create(vals)
    assert fb.trainer_id == c.e_assessor and fb.recorded_by_id == trainee_user
    assert refused(c.env, lambda: fb.with_user(trainee_user).write({"rating_trainer": "1"}))
    assert refused(
        c.env, lambda: Feedback.with_user(trainee_user).create(vals)
    ), "one per enrolment"
    assert Feedback.with_user(c.plain).search_count([("id", "=", fb.id)]) == 0, "S2"


# ---------------------------------------------------------------- mentoring
def test_mentoring_pairing_interactions_and_closure(c):
    mentor_user = c.assessor_user
    mentee_user = c.plain
    Mentoring = c.env["fix.mentoring"]
    vals = {
        "mentee_id": c.e_plain.id,
        "mentor_id": c.e_assessor.id,
        "objectives": "Independent L2 laptop diagnosis in 8 weeks",
    }
    assert refused(c.env, lambda: Mentoring.with_user(mentor_user).create(vals))
    assert refused(
        c.env, lambda: Mentoring.with_user(c.trn).create(dict(vals, mentor_id=c.e_plain.id))
    )
    men = Mentoring.with_user(c.trn).create(vals)
    assert men.name.startswith("MEN/")
    assert refused(c.env, lambda: Mentoring.with_user(c.trn).create(vals)), "duplicate pair"
    Log = c.env["fix.mentoring.interaction"]
    log = {"mentoring_id": men.id, "topics": "Board-level fault tree", "duration_hours": 1.5}
    assert "active" in (refused(c.env, lambda: Log.with_user(mentor_user).create(log)) or "")
    men.with_user(c.trn).action_start()
    assert refused(c.env, lambda: men.with_user(c.trn).write({"mentor_id": c.e_col.id}))
    assert refused(c.env, lambda: Log.with_user(mentee_user).create(log)), "mentee logs"
    assert refused(
        c.env,
        lambda: Log.with_user(c.trn2).create(
            dict(log, date=fields.Date.today() + timedelta(days=2))
        ),
    )
    assert refused(
        c.env, lambda: men.with_user(mentor_user).action_close(outcome="achieved")
    ), "closed with no interaction"
    entry = Log.with_user(mentor_user).create(log)
    assert entry.recorded_by_id == mentor_user and men.interaction_count == 1
    assert refused(
        c.env, lambda: entry.with_user(c.trn).write({"topics": "x"})
    ), "only the recorder corrects it"
    assert refused(c.env, lambda: men.with_user(mentee_user).action_close(outcome="achieved"))
    men.with_user(mentor_user).action_close(outcome="achieved")
    assert men.state == "closed" and men.outcome == "achieved"
    assert refused(c.env, lambda: Log.with_user(mentor_user).create(log)), "closed is final"
    other = _user(c.env)
    assert Mentoring.with_user(other).search_count([("id", "=", men.id)]) == 0, "S2"
    assert Mentoring.with_user(mentee_user).search_count([("id", "=", men.id)]) == 1


def test_a_training_manager_who_is_the_mentee_neither_logs_nor_closes(c):
    """The mentee bar holds even when the mentee holds the Training Manager role."""
    men = (
        c.env["fix.mentoring"]
        .with_user(c.trn2)
        .create(
            {
                "mentee_id": c.e_trn.id,
                "mentor_id": c.e_assessor.id,
                "objectives": "Trainer certification for the workshop lead",
            }
        )
    )
    men.with_user(c.trn2).action_start()
    log = {"mentoring_id": men.id, "topics": "Teaching BGA rework"}
    Log = c.env["fix.mentoring.interaction"]
    assert "mentee" in (refused(c.env, lambda: Log.with_user(c.trn).create(log)) or "")
    Log.with_user(c.trn2).create(log)
    err = refused(c.env, lambda: men.with_user(c.trn).action_close(outcome="achieved"))
    assert err and "mentee" in err


# ---------------------------------------------------------------- effectiveness
def test_effectiveness_needs_a_held_session_after_value_conclusion_and_no_trainer(c, call):
    sess = _session(c, capacity=3)
    Eval = c.env["fix.training.effectiveness"]
    vals = {
        "session_id": sess.id,
        "target_measure": "First-time-fix rate, laptop jobs",
        "measure_unit": "%",
        "baseline_value": 71.0,
        "baseline_period": "Aug-Oct",
    }
    assert "held" in (refused(c.env, lambda: Eval.with_user(c.trn).create(vals)) or "")
    enr = _enrol(c, c.e_col, sess)
    sess.with_user(c.trn).action_schedule()
    enr.with_user(c.trn).action_mark_attended()
    sess.with_user(c.trn).action_mark_held()
    assert refused(c.env, lambda: Eval.with_user(c.plain).create(vals))
    ev = Eval.with_user(c.trn).create(vals)
    assert ev.course_id == c.course and ev.name.startswith("TEV/")
    assert "after" in (refused(c.env, lambda: ev.with_user(c.trn).action_evaluate()) or "")
    ev.with_user(c.trn).write({"after_value": 80.0, "after_period": "Jan-Mar"})
    assert ev.result == "improved" and ev.change == 9.0
    assert "conclusion" in (refused(c.env, lambda: ev.with_user(c.trn).action_evaluate()) or "")
    ev.with_user(c.trn).write({"conclusion": "Gain held across both branches"})
    # the trainer does not grade their own session
    trainer = c.env["res.users"].browse(c.assessor_user.id)
    trainer.group_ids = [(4, c.env.ref("cd_competency.group_training").id)]
    assert "trainer" in (refused(c.env, lambda: ev.with_user(trainer).action_evaluate()) or "")
    ev.with_user(c.trn).action_evaluate()
    assert ev.state == "evaluated" and ev.evaluated_by_id == c.trn
    assert refused(c.env, lambda: ev.with_user(c.trn).write({"after_value": 99.0}))
    rep = call(c.env(user=c.trn.id), "model_report", module="M22", report="training_effectiveness")
    row = next(r for r in rep["rows"] if r["code"] == c.course.code)
    assert row["evaluated"] == 1 and row["improved"] == 1
    lower = Eval.with_user(c.trn).create(
        dict(vals, better_when="lower", after_value=80.0, after_period="Q1")
    )
    assert lower.result == "worse"


def test_workspace_writes_cannot_type_workflow_fields(c, call):
    need = _need(c)
    out = call(
        c.env(user=c.trn.id),
        "model_write",
        model="fix.training.need",
        record_id=need.id,
        values={"state": "closed"},
    )
    assert out.get("error"), out
    assert need.state == "identified"
