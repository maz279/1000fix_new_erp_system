# M22 capture audit (2026-11-13): the training session and its attendance
# (FR-LMS-020 scheduling, FR-LMS-021 enrolment with capacity, FR-LMS-023
# attendance, FR-LMS-029 external training). Before, the "Schedule &
# Attendance" screen captured an enrolment with no session, no date, no
# trainer and no attendance.
#
# Attacked as freshly created NON-admin users (the round-1 fixtures).
# ruff: noqa: F811
from datetime import datetime, timedelta

from odoo.addons.cd_competency.tests.test_a09_m22_controls import (  # noqa: F401 (fixtures)
    _assessment,
    _employee,
    _events,
    _rpc,
    c,
    call,
    refused,
)


def _session(c, user=None, **vals):
    start = datetime.now().replace(microsecond=0) + timedelta(days=3)
    base = {
        "course_id": c.course.id,
        "delivery_mode": "classroom",
        "trainer_id": c.e_assessor.id,
        "venue": "Mirpur training room",
        "date_start": start,
        "date_end": start + timedelta(hours=6),
        "capacity": 2,
    }
    base.update(vals)
    return c.env["fix.training.session"].with_user(user or c.trn).create(base)


def _enrol(c, session, employee):
    return (
        c.env["fix.training.enrollment"]
        .with_user(c.trn)
        .create(
            {
                "course_id": session.course_id.id,
                "session_id": session.id,
                "employee_id": employee.id,
            }
        )
    )


def test_a_training_manager_schedules_a_session_and_a_plain_user_cannot(c):
    sess = _session(c)
    assert sess.name.startswith("TRS/") and sess.state == "planned"
    assert refused(c.env, lambda: _session(c, user=c.plain))


def test_the_window_and_the_external_provider_are_checked(c):
    start = datetime.now().replace(microsecond=0)
    assert "ends after" in refused(c.env, lambda: _session(c, date_start=start, date_end=start))
    err = refused(c.env, lambda: _session(c, delivery_mode="external", trainer_id=False))
    assert err and "provider" in err
    ext = _session(c, delivery_mode="external", trainer_id=False, external_trainer="OEM academy")
    assert ext.delivery_mode == "external"


def test_scheduling_needs_trainer_and_venue_and_publishes_the_window(c):
    sess = _session(c, venue=False)
    assert "venue" in refused(c.env, lambda: sess.with_user(c.trn).action_schedule())
    sess.with_user(c.trn).write({"venue": "Mirpur training room"})
    _enrol(c, sess, c.e_col)
    sess.with_user(c.trn).action_schedule()
    assert sess.state == "scheduled"
    event = _events(c.env, "training.session.scheduled", sess.id)
    assert event and event[-1]["employee_ids"] == [
        c.e_col.id
    ], "the schedule was not published for the roster (FR-LMS-022)"


def test_the_state_is_never_typed(c):
    sess = _session(c)
    assert refused(c.env, lambda: _rpc(c.env, c.trn, sess._name, "write", sess, {"state": "done"}))


def test_capacity_and_course_are_enforced(c):
    sess = _session(c, capacity=1)
    _enrol(c, sess, c.e_col)
    assert "full" in refused(c.env, lambda: _enrol(c, sess, c.e_uncert))
    other = c.env["fix.training.course"].create({"code": "A9OTH", "name": "Other course"})
    err = refused(
        c.env,
        lambda: c.env["fix.training.enrollment"]
        .with_user(c.trn)
        .create({"course_id": other.id, "session_id": sess.id, "employee_id": c.e_uncert.id}),
    )
    assert err and "delivers" in err


def test_attendance_is_recorded_by_a_trainer_on_a_scheduled_session(c):
    sess = _session(c)
    enr = _enrol(c, sess, c.e_col)
    assert enr.attendance == "pending"
    # not yet scheduled
    assert refused(c.env, lambda: enr.with_user(c.trn).action_mark_attended())
    sess.with_user(c.trn).action_schedule()
    # never typed, never by a plain user
    assert refused(
        c.env, lambda: _rpc(c.env, c.trn, enr._name, "write", enr, {"attendance": "attended"})
    )
    assert refused(c.env, lambda: enr.with_user(c.plain).action_mark_attended())
    enr.with_user(c.trn).action_mark_attended()
    assert enr.attendance == "attended" and enr.attendance_by_id == c.trn


def test_nobody_records_their_own_attendance(c):
    sess = _session(c)
    enr = _enrol(c, sess, c.e_trn)
    sess.with_user(c.trn).action_schedule()
    assert "own attendance" in refused(c.env, lambda: enr.with_user(c.trn).action_mark_attended())


def test_an_absent_trainee_is_not_passed(c):
    sess = _session(c)
    enr = _enrol(c, sess, c.e_col)
    sess.with_user(c.trn).action_schedule()
    enr.with_user(c.trn).action_mark_absent()
    _assessment(c, c.e_col)
    assert "absent" in refused(c.env, lambda: enr.with_user(c.trn).action_pass())


def test_an_attended_trainee_passes_as_before(c):
    sess = _session(c)
    enr = _enrol(c, sess, c.e_col)
    sess.with_user(c.trn).action_schedule()
    enr.with_user(c.trn).action_mark_attended()
    _assessment(c, c.e_col)
    enr.with_user(c.trn).action_pass()
    assert enr.state == "passed" and enr.certification_id.state == "draft"


def test_a_session_closes_only_once_every_attendance_is_recorded(c):
    sess = _session(c)
    a = _enrol(c, sess, c.e_col)
    b = _enrol(c, sess, c.e_uncert)
    sess.with_user(c.trn).action_schedule()
    a.with_user(c.trn).action_mark_attended()
    assert "attendance" in refused(c.env, lambda: sess.with_user(c.trn).action_mark_held())
    b.with_user(c.trn).action_mark_absent()
    sess.with_user(c.trn).action_mark_held()
    assert sess.state == "done" and sess.seats_taken == 2 and sess.attended_count == 1
    # a held session is final and takes nobody new
    assert refused(c.env, lambda: sess.with_user(c.trn).write({"venue": "elsewhere"}))
    assert refused(c.env, lambda: _enrol(c, sess, _employee(c.env)))


def test_a_session_with_attendance_is_not_cancelled(c):
    sess = _session(c)
    enr = _enrol(c, sess, c.e_col)
    sess.with_user(c.trn).action_schedule()
    enr.with_user(c.trn).action_mark_attended()
    assert refused(c.env, lambda: sess.with_user(c.trn).action_cancel())
    empty = _session(c)
    empty.with_user(c.trn).action_cancel()
    assert empty.state == "cancelled"


def test_an_enrolment_without_a_session_still_works(c):
    """The session is optional: the existing enrol-and-pass path is unchanged."""
    enr = (
        c.env["fix.training.enrollment"]
        .with_user(c.trn)
        .create({"course_id": c.course.id, "employee_id": c.e_col.id})
    )
    _assessment(c, c.e_col)
    enr.with_user(c.trn).action_pass()
    assert enr.state == "passed"


def test_the_workspace_serves_the_session_and_attendance(odoo_env):
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import SURFACES

    assert {"action_schedule", "action_mark_held", "action_cancel"} <= SURFACES[
        "fix.training.session"
    ]["actions"]
    assert {"action_mark_attended", "action_mark_absent"} <= SURFACES["fix.training.enrollment"][
        "actions"
    ]


def test_a_plain_user_reads_but_does_not_write_sessions(c):
    sess = _session(c)
    assert sess.with_user(c.plain).read(["name"])
    assert refused(c.env, lambda: sess.with_user(c.plain).write({"venue": "x"}))
