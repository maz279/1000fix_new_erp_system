# M57 capture audit (2026-11-17), live: the six records the sub-module pages
# now capture, attacked as freshly created NON-admin users through call_kw and
# the real M63 inbox. The superuser only builds the world.
import itertools
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError, ValidationError)
_SEQ = itertools.count(1)
PERIOD = "2031-07"
OFFICER = "cd_performance.group_performance_officer"
APPROVER = "cd_performance.group_incentive_approver"
CALIBRATOR = "cd_performance.group_performance_calibrator"
COMPENSATION = "cd_performance.group_compensation"
CFO = "cd_performance.group_scheme_cfo"
HR_MANAGER = "hr.group_hr_manager"


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M57 Cap User %d" % n,
                "login": "m57-cap-%d@test.local" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _employee(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "M57 Cap Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


def _rpc(env, user, model, method, ids, *args, **kw):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[model], method, [ids, *args], kw
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


@pytest.fixture
def w(odoo_env):
    env = odoo_env

    class W:
        pass

    x = W()
    x.env = env
    params = env["ir.config_parameter"].sudo()
    params.set_param("cd_performance.incentive_requires_attendance_lock", "0")
    params.set_param("cd_performance.incentive_dispute_days", "0")
    params.set_param("cd_performance.incentive_clawback_days", "0")
    x.officer = _user(env, OFFICER)
    x.officer2 = _user(env, OFFICER)
    x.approver = _user(env, APPROVER)
    x.hr = _user(env, HR_MANAGER)
    x.hr2 = _user(env, HR_MANAGER)
    x.calibrator = _user(env, CALIBRATOR)
    x.comp = _user(env, COMPENSATION)
    x.cfo = _user(env, CFO)
    x.plain = _user(env)
    x.tech_user = _user(env)
    x.peer_user = _user(env)
    x.mgr_user = _user(env)
    x.e_mgr = _employee(env, x.mgr_user)
    x.e_tech = _employee(env, x.tech_user, parent_id=x.e_mgr.id)
    x.e_peer = _employee(env, x.peer_user, parent_id=x.e_mgr.id)
    return x


# ====================================================== KPI definitions (FR-PIC-006)
def _kpi(w, user=None, **vals):
    base = {
        "name": "First-time fix",
        "code": "FTF%d" % next(_SEQ),
        "measure": "first_time_fix",
        "formula": "Orders completed without a rework or a second visit, over orders completed.",
        "target": 85.0,
        "threshold": 70.0,
        "date_from": "2031-01-01",
    }
    base.update(vals)
    return w.env["fix.kpi.definition"].with_user(user or w.officer).create(base)


def test_a_kpi_is_approved_by_an_hr_manager_who_did_not_prepare_it(w):
    kpi = _kpi(w)
    assert kpi.state == "draft" and kpi.version_no == 1
    assert kpi.kind == "quality" and kpi.direction == "higher" and kpi.unit == "pct"
    assert refused(w.env, lambda: _kpi(w, user=w.plain)), "a plain user defined a KPI"
    kpi.with_user(w.officer).action_submit()
    assert refused(w.env, lambda: kpi.with_user(w.officer2).action_approve()), "not an HR Manager"
    kpi.with_user(w.hr).action_approve()
    assert kpi.state == "approved" and kpi.approved_by_id == w.hr
    own = _kpi(w, user=w.hr)
    own.with_user(w.hr).action_submit()
    assert refused(w.env, lambda: own.with_user(w.hr).action_approve()), "approved own KPI"
    own.with_user(w.hr2).action_approve()


def test_kpi_state_and_stamps_cannot_be_forged_and_an_approved_one_is_frozen(w):
    kpi = _kpi(w)
    for vals in ({"state": "approved"}, {"approved_by_id": w.hr.id}, {"date_to": "2031-02-01"}):
        assert refused(
            w.env, lambda v=vals: _rpc(w.env, w.officer, kpi._name, "write", kpi.ids, v)
        ), vals
    assert refused(w.env, lambda: _kpi(w, state="approved"))
    kpi.with_user(w.officer).action_submit()
    kpi.with_user(w.hr).action_approve()
    assert refused(
        w.env, lambda: _rpc(w.env, w.officer, kpi._name, "write", kpi.ids, {"target": 95.0})
    )
    assert refused(w.env, lambda: kpi.with_user(w.officer).unlink())


def test_a_new_kpi_version_closes_the_old_one_and_never_backdates(w):
    today = fields.Date.today()
    old = _kpi(w, date_from=today - timedelta(days=400))
    old.with_user(w.officer).action_submit()
    old.with_user(w.hr).action_approve()
    past = _kpi(w, code=old.code, date_from=today - timedelta(days=10), target=90.0)
    assert past.version_no == 2
    past.with_user(w.officer).action_submit()
    err = refused(w.env, lambda: past.with_user(w.hr).action_approve())
    assert err and "BRU-PIC-02" in err
    start = today + timedelta(days=10)
    new = _kpi(w, code=old.code, date_from=start, target=90.0)
    new.with_user(w.officer).action_submit()
    new.with_user(w.hr).action_approve()
    assert old.date_to == start - timedelta(days=1)
    assert not new.date_to


def test_a_volume_kpi_needs_a_quality_kpi_beside_it(w):
    role = "workshop_technician"
    vol = _kpi(w, measure="jobs_completed", target=150, threshold=100, role_profile=role)
    assert vol.kind == "volume" and vol.unit == "count"
    vol.with_user(w.officer).action_submit()
    err = refused(w.env, lambda: vol.with_user(w.hr).action_approve())
    assert err and "BRU-PIC-04" in err
    q = _kpi(w, role_profile=role)
    q.with_user(w.officer).action_submit()
    q.with_user(w.hr).action_approve()
    vol.with_user(w.hr).action_approve()
    assert vol.state == "approved"


def test_kpi_figures_follow_the_direction(w):
    assert refused(w.env, lambda: _kpi(w, target=70.0, threshold=85.0))
    assert refused(w.env, lambda: _kpi(w, measure="rework_rate", target=5.0, threshold=2.0))
    assert refused(w.env, lambda: _kpi(w, target=150.0, threshold=70.0))


def test_the_scorecard_reads_the_kpis_in_force(w):
    kpi = _kpi(w, target=85.0, threshold=70.0)
    kpi.with_user(w.officer).action_submit()
    kpi.with_user(w.hr).action_approve()
    card = w.env["fix.performance.scorecard"].create({"employee_id": w.e_tech.id, "period": PERIOD})
    card.sudo()._guarded().write({"first_time_fix": 0.6})
    assert kpi.code in card.kpi_breaches
    assert "BELOW THRESHOLD" in card.kpi_attainment and "60.0%" in card.kpi_attainment
    card.sudo()._guarded().write({"first_time_fix": 0.9})
    assert not card.kpi_breaches and "meets target" in card.kpi_attainment


# ====================================================== review cycles (FR-PIC-016)
def _cycle(w, user=None, **vals):
    today = fields.Date.today()
    base = {
        "name": "Cycle %d" % next(_SEQ),
        "cycle_type": "half_yearly",
        "period": "2031-H1",
        "employee_ids": [(6, 0, [w.e_tech.id, w.e_peer.id, w.e_mgr.id])],
        "self_deadline": today + timedelta(days=5),
        "manager_deadline": today + timedelta(days=10),
        "calibration_deadline": today + timedelta(days=15),
    }
    base.update(vals)
    return w.env["fix.performance.review.cycle"].with_user(user or w.hr).create(base)


def test_hr_opens_a_cycle_which_raises_one_review_per_managed_employee(w):
    assert refused(w.env, lambda: _cycle(w, user=w.officer)), "a non-HR user set up a cycle"
    cyc = _cycle(w)
    assert refused(w.env, lambda: cyc.with_user(w.plain).action_open())
    cyc.with_user(w.hr).action_open()
    assert cyc.state == "open" and cyc.opened_by_id == w.hr
    reviews = cyc.review_ids
    assert set(reviews.mapped("employee_id").ids) == {w.e_tech.id, w.e_peer.id}
    assert all(r.reviewer_id == w.e_mgr for r in reviews)
    assert all(r.period == "2031-H1" for r in reviews)
    assert w.e_mgr.name in cyc.skipped_note  # no line manager
    assert refused(
        w.env, lambda: _rpc(w.env, w.hr, cyc._name, "write", cyc.ids, {"period": "2031-H2"})
    )
    assert refused(
        w.env,
        lambda: _rpc(w.env, w.hr, reviews._name, "write", reviews[:1].ids, {"cycle_id": False}),
    )
    err = refused(w.env, lambda: cyc.with_user(w.hr).action_close())
    assert err and "not closed" in err


def test_cycle_deadlines_run_in_order_and_period_is_well_formed(w):
    today = fields.Date.today()
    assert refused(w.env, lambda: _cycle(w, manager_deadline=today))
    assert refused(w.env, lambda: _cycle(w, period="H1 2031"))


def test_the_daily_job_chases_an_overdue_self_assessment(w):
    today = fields.Date.today()
    cyc = _cycle(
        w,
        self_deadline=today - timedelta(days=3),
        manager_deadline=today + timedelta(days=3),
        calibration_deadline=today + timedelta(days=6),
        employee_ids=[(6, 0, [w.e_tech.id])],
    )
    cyc.with_user(w.hr).action_open()
    assert cyc.overdue_count == 1
    w.env["fix.performance.review.cycle"]._cron_chase_overdue()
    review = cyc.review_ids
    users = review.activity_ids.mapped("user_id")
    assert w.tech_user in users and w.mgr_user in users  # the employee, then the next level
    w.env["fix.performance.review.cycle"]._cron_chase_overdue()
    assert len(review.activity_ids) == len(users), "the chase is not repeated daily per person"


# ====================================================== feedback (FR-PIC-020)
def _review(w, state="self_review"):
    rev = w.env["fix.performance.review"].create({"employee_id": w.e_tech.id, "period": PERIOD})
    rev.sudo()._guarded().write({"state": state})
    return rev


def _feedback(w, rev, respondent, user=None):
    return (
        w.env["fix.performance.feedback"]
        .with_user(user or w.hr)
        .create({"review_id": rev.id, "respondent_id": respondent.id, "relationship": "peer"})
    )


def test_only_the_respondent_answers_and_the_subject_never_reads_it(w):
    rev = _review(w)
    assert refused(w.env, lambda: _feedback(w, rev, w.e_peer, user=w.plain))
    fb = _feedback(w, rev, w.e_peer)
    assert fb.state == "requested" and fb.name.startswith("FBK/")
    assert w.peer_user in fb.activity_ids.mapped("user_id")
    for user in (w.tech_user, w.mgr_user, w.plain):
        assert refused(
            w.env,
            lambda u=user: _rpc(
                w.env, u, fb._name, "action_submit_feedback", fb.ids, feedback="5 great"
            ),
        ), user.name
    assert refused(
        w.env, lambda: _rpc(w.env, w.peer_user, fb._name, "write", fb.ids, {"rating": 5})
    )
    _rpc(
        w.env,
        w.peer_user,
        fb._name,
        "action_submit_feedback",
        fb.ids,
        feedback="4 fixes hard faults",
    )
    assert fb.state == "submitted" and fb.rating == 4 and "hard faults" in fb.strengths
    assert refused(
        w.env,
        lambda: _rpc(
            w.env, w.peer_user, fb._name, "action_submit_feedback", fb.ids, feedback="1 x"
        ),
    ), "an answer was changed"
    # the subject reads neither the answer nor who gave it; the line manager does
    assert not w.env["fix.performance.feedback"].with_user(w.tech_user).search([("id", "=", fb.id)])
    assert w.env["fix.performance.feedback"].with_user(w.mgr_user).search([("id", "=", fb.id)])
    assert rev.feedback_count == 1 and rev.feedback_avg == 4.0


def test_feedback_comes_from_someone_other_than_the_subject_or_manager(w):
    rev = _review(w)
    assert refused(w.env, lambda: _feedback(w, rev, w.e_tech))
    assert refused(w.env, lambda: _feedback(w, rev, w.e_mgr))
    assert refused(w.env, lambda: _feedback(w, _review(w, "calibrated"), w.e_peer))


def test_the_respondent_may_decline_with_a_reason(w):
    fb = _feedback(w, _review(w), w.e_peer)
    assert refused(
        w.env, lambda: _rpc(w.env, w.peer_user, fb._name, "action_decline", fb.ids, reason="")
    )
    _rpc(w.env, w.peer_user, fb._name, "action_decline", fb.ids, reason="never worked together")
    assert fb.state == "declined"


# ====================================================== calibration sessions (BRU-PIC-13)
def _calibrated_review(w, employee, rating):
    rev = w.env["fix.performance.review"].create({"employee_id": employee.id, "period": PERIOD})
    rev.sudo()._guarded().write({"state": "manager_review"})
    rev.with_user(w.mgr_user).action_record_manager_rating(rating)
    rev.with_user(w.mgr_user).action_request_calibration()
    return rev


def _session(w, user=None):
    return (
        w.env["fix.performance.calibration.session"]
        .with_user(user or w.calibrator)
        .create({"period": PERIOD, "scope": "Dhaka field teams"})
    )


def test_a_session_moves_a_rating_with_a_reason_and_records_the_distribution(w):
    a = _calibrated_review(w, w.e_tech, 5)
    b = _calibrated_review(w, w.e_peer, 3)
    _task_for(a, w.calibrator).with_user(w.calibrator).action_approve()
    assert refused(w.env, lambda: _session(w, user=w.plain))
    s = _session(w)
    assert s.name.startswith("CAL/")
    assert refused(
        w.env,
        lambda: w.env["fix.performance.calibration.line"]
        .with_user(w.calibrator)
        .create({"session_id": s.id, "review_id": a.id, "new_rating": 4, "reason": "x"}),
    ), "a rating changed before the session started"
    s.with_user(w.calibrator).action_start()
    assert "5 Outstanding: 1" in s.distribution_before and "3 Meets: 1" in s.distribution_before
    w.env["fix.performance.calibration.line"].with_user(w.calibrator).create(
        {"session_id": s.id, "review_id": a.id, "new_rating": 4, "reason": "lenient vs peers"}
    )
    err = refused(w.env, lambda: s.with_user(w.calibrator).action_conclude())
    assert err and "BRU-PIC-13" in err  # b still awaits calibration
    # while the session is open, no review of the period closes
    err = refused(w.env, lambda: a.with_user(w.hr).action_close())
    assert err and "calibration session" in err
    _task_for(b, w.calibrator).with_user(w.calibrator).action_approve()
    s.with_user(w.calibrator).action_conclude()
    assert s.state == "concluded" and a.calibrated_rating == 4
    assert s.line_ids.previous_rating == 5 and s.line_ids.applied
    assert "4 Exceeds: 1" in s.distribution_after
    a.with_user(w.hr).action_close()
    assert a.state == "closed"
    assert refused(
        w.env, lambda: _rpc(w.env, w.calibrator, s._name, "write", s.ids, {"minutes": "edit"})
    ), "a concluded session was edited"


def test_the_manager_of_a_moved_rating_does_not_conclude(w):
    mgr_cal = w.mgr_user
    mgr_cal.group_ids = [(4, w.env.ref(CALIBRATOR).id)]
    a = _calibrated_review(w, w.e_tech, 5)
    _task_for(a, w.calibrator).with_user(w.calibrator).action_approve()
    s = _session(w)
    s.with_user(w.calibrator).action_start()
    w.env["fix.performance.calibration.line"].with_user(w.calibrator).create(
        {"session_id": s.id, "review_id": a.id, "new_rating": 4, "reason": "peer comparison"}
    )
    err = refused(w.env, lambda: s.with_user(mgr_cal).action_conclude())
    assert err and "someone else" in err


def test_session_distribution_and_state_are_not_typed(w):
    s = _session(w)
    for vals in ({"state": "concluded"}, {"distribution_after": "all 5"}):
        assert refused(
            w.env, lambda v=vals: _rpc(w.env, w.calibrator, s._name, "write", s.ids, v)
        ), vals


# ====================================================== incentive adjustments (BRU-PIC-10/11)
def _scheme_world(w):
    scheme = w.env["fix.incentive.scheme"].create(
        {"name": "M57 cap scheme %d" % next(_SEQ), "code": "M57C%d" % next(_SEQ)}
    )
    w.env["fix.incentive.scheme.version"].create(
        {
            "scheme_id": scheme.id,
            "date_from": "2031-01-01",
            "band_base": 20000.0,
            "state": "approved",
        }
    )
    card = w.env["fix.performance.scorecard"].create(
        {
            "employee_id": w.e_tech.id,
            "period": PERIOD,
            "first_time_fix": 1.0,
            "sla_hit": 1.0,
            "csat": 1.0,
        }
    )
    card.action_publish()
    return scheme


def _adjustment(w, user=None, **vals):
    base = {
        "employee_id": w.e_tech.id,
        "period": PERIOD,
        "adjustment_type": "correction",
        "amount": 500.0,
        "reason": "Two closed jobs were missing from the order feed.",
    }
    base.update(vals)
    return w.env["fix.incentive.adjustment"].with_user(user or w.officer).create(base)


def test_an_adjustment_is_approved_from_the_inbox_and_becomes_a_visible_line(w):
    scheme = _scheme_world(w)
    adj = _adjustment(w)
    assert adj.name.startswith("IAD/") and adj.state == "draft"
    adj.with_user(w.officer).action_request_approval()
    assert not _task_for(adj, w.officer) and not _task_for(adj, w.tech_user)
    assert refused(w.env, lambda: adj.with_user(w.approver).action_approve())  # not from the inbox
    _task_for(adj, w.approver).with_user(w.approver).action_approve()
    assert adj.state == "approved" and adj.approved_by_id == w.approver
    assert w.tech_user in adj.activity_ids.mapped("user_id"), "the employee was not told"
    run = (
        w.env["fix.incentive.run"]
        .with_user(w.officer)
        .create({"period": PERIOD, "scheme_id": scheme.id})
    )
    run.with_user(w.officer).action_compute()
    line = run.line_ids.filtered(lambda r: r.line_type == "adjustment")
    assert line.amount == 500.0 and line.adjustment_id == adj
    assert "missing from the order feed" in line.eligibility_note
    assert adj.state == "applied" and adj.applied_run_id == run
    # the employee reads their adjustment line
    assert w.env["fix.incentive.line"].with_user(w.tech_user).search([("id", "=", line.id)])
    run.with_user(w.officer).action_reset_draft()
    assert adj.state == "approved" and not adj.applied_run_id


def test_adjustment_rules(w):
    _scheme_world(w)
    assert refused(w.env, lambda: _adjustment(w, user=w.plain))
    assert refused(w.env, lambda: _adjustment(w, amount=0.0))
    assert refused(w.env, lambda: _adjustment(w, reason=" "))
    err = refused(w.env, lambda: _adjustment(w, adjustment_type="fraud_reversal", amount=-300.0))
    assert err and "BRU-PIC-11" in err
    assert refused(
        w.env,
        lambda: _adjustment(w, adjustment_type="fraud_reversal", amount=300.0, evidence_ref="SO/1"),
    )
    officer_emp = _employee(w.env, w.officer2)
    assert refused(w.env, lambda: _adjustment(w, user=w.officer2, employee_id=officer_emp.id))
    adj = _adjustment(w)
    for vals in ({"state": "approved"}, {"approved_by_id": w.approver.id}):
        assert refused(
            w.env, lambda v=vals: _rpc(w.env, w.officer, adj._name, "write", adj.ids, v)
        ), vals
    assert refused(w.env, lambda: _adjustment(w, state="approved"))
    adj.with_user(w.officer).action_request_approval()
    assert refused(
        w.env, lambda: _rpc(w.env, w.officer, adj._name, "write", adj.ids, {"amount": 9000.0})
    ), "terms changed while in approval"
    assert refused(w.env, lambda: adj.with_user(w.officer).unlink())


def test_an_approved_period_is_locked_against_adjustment(w):
    scheme = _scheme_world(w)
    run = (
        w.env["fix.incentive.run"]
        .with_user(w.officer)
        .create({"period": PERIOD, "scheme_id": scheme.id})
    )
    run.with_user(w.officer).action_compute()
    run.with_user(w.officer).action_request_approval()
    _task_for(run, w.approver).with_user(w.approver).action_approve()
    err = refused(w.env, lambda: _adjustment(w))
    assert err and "T-06" in err


def test_adjustments_never_take_an_incentive_below_zero(w):
    scheme = _scheme_world(w)
    adj = _adjustment(
        w, adjustment_type="fraud_reversal", amount=-999999.0, evidence_ref="SO/9 audit"
    )
    adj.with_user(w.officer).action_request_approval()
    _task_for(adj, w.approver).with_user(w.approver).action_approve()
    run = (
        w.env["fix.incentive.run"]
        .with_user(w.officer)
        .create({"period": PERIOD, "scheme_id": scheme.id})
    )
    err = refused(w.env, lambda: run.with_user(w.officer).action_compute())
    assert err and "below zero" in err
    assert run.state == "draft" and adj.state == "approved"


# ====================================================== compensation cycles (BRU-PIC-17)
def _comp_world(w, basic=25000.0):
    grade = "M57G%d" % next(_SEQ)
    w.env["fix.compensation.band"].create(
        {
            "name": "M57 band",
            "grade": grade,
            "range_min": 20000,
            "range_mid": 30000,
            "range_max": 40000,
        }
    )
    pos = w.env["fix.org.position"].create({"name": "M57 Technician", "grade": grade})
    w.e_tech.position_id = pos
    contract = w.env["fix.employment.contract"].create(
        {
            "employee_id": w.e_tech.id,
            "contract_type": "permanent",
            "joining_date": fields.Date.today() - timedelta(days=400),
            "weekly_hours": 48,
            "basic_monthly": basic,
        }
    )
    contract.write({"state": "active"})
    rev = w.env["fix.performance.review"].create({"employee_id": w.e_tech.id, "period": PERIOD})
    rev.sudo()._guarded().write({"state": "closed", "calibrated_rating": 4})
    return rev


def _comp_cycle(w, budget):
    today = fields.Date.today()
    cyc = (
        w.env["fix.compensation.cycle"]
        .with_user(w.comp)
        .create(
            {
                "name": "FY31 review %d" % next(_SEQ),
                "date_from": today,
                "date_to": today + timedelta(days=90),
                "budget": budget,
                "guideline_pct": 10.0,
            }
        )
    )
    cyc.with_user(w.comp).action_open()
    return cyc


def _propose(w, rev, figure):
    out = rev.with_user(w.mgr_user).action_propose_compensation(
        proposal="%s a strong year" % figure
    )
    prop = w.env["fix.compensation.proposal"].browse(out["proposal_id"])
    prop.with_user(w.calibrator).action_calibration_review("aligned with peers")
    return prop


def test_a_cycle_is_set_up_and_opened_by_the_compensation_manager(w):
    assert refused(
        w.env,
        lambda: w.env["fix.compensation.cycle"]
        .with_user(w.hr)
        .create({"name": "x", "date_from": "2031-01-01", "date_to": "2031-03-31", "budget": 1000}),
    )
    cyc = _comp_cycle(w, 10000.0)
    assert cyc.state == "open" and cyc.opened_by_id == w.comp
    assert refused(
        w.env, lambda: _rpc(w.env, w.comp, cyc._name, "write", cyc.ids, {"budget": 99999.0})
    ), "an open cycle's budget changed"
    assert refused(w.env, lambda: _comp_cycle(w, 5000.0)), "two open cycles over the same dates"


def test_within_budget_the_compensation_manager_decides(w):
    rev = _comp_world(w)
    cyc = _comp_cycle(w, 10000.0)
    prop = _propose(w, rev, 30000)
    assert prop.cycle_id == cyc and not prop.over_budget
    assert cyc.pending_amount == 5000.0
    _task_for(prop, w.comp).with_user(w.comp).action_approve()
    assert prop.state == "approved"
    assert cyc.committed_amount == 5000.0 and cyc.remaining_amount == 5000.0
    err = refused(w.env, lambda: cyc.with_user(w.comp).action_close())
    assert not err and cyc.state == "closed"


def test_over_the_budget_only_the_cfo_decides(w):
    rev = _comp_world(w)
    _comp_cycle(w, 2000.0)
    prop = _propose(w, rev, 30000)
    assert prop.over_budget
    assert not _task_for(prop, w.comp), "an over-budget raise went to the Compensation Manager"
    task = _task_for(prop, w.cfo)
    assert task, "the CFO was not asked"
    task.with_user(w.cfo).action_approve()
    assert prop.state == "approved" and prop.approved_by_id == w.cfo


def test_cycle_stamps_and_spend_are_not_typed(w):
    cyc = _comp_cycle(w, 1000.0)
    assert refused(
        w.env, lambda: _rpc(w.env, w.comp, cyc._name, "write", cyc.ids, {"state": "draft"})
    )
    assert refused(w.env, lambda: cyc.with_user(w.comp).unlink())
