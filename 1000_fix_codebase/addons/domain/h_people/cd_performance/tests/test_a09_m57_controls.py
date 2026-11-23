# A09 M57 acceptance suite (A09 workflow audit M57-F1..F13; build brief I4,
# I7, B1-B6, C1): performance, incentives and compensation, attacked as
# freshly created NON-admin users.
#
# Writes go through call_kw with the client-controlled `tracking_disable` key
# (the P0 suites' pattern); workspace paths go through the real /p03
# controller with `request` patched. The superuser only builds the world.
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
PERIOD = "2031-03"
OFFICER = "cd_performance.group_performance_officer"
APPROVER = "cd_performance.group_incentive_approver"
CALIBRATOR = "cd_performance.group_performance_calibrator"
COMPENSATION = "cd_performance.group_compensation"


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
                "name": "A09 M57 User %d" % n,
                "login": "a09-m57-%d@test.local" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _employee(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "A09 M57 Employee %d" % n, "user_id": user.id if user else False, **vals}
    )


def _rpc(env, user, model, method, rec, *args):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[model],
        method,
        [[rec.id], *args],
        {},
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
def w(odoo_env):
    env = odoo_env

    class W:
        pass

    x = W()
    x.env = env
    env["ir.config_parameter"].sudo().set_param(
        "cd_performance.incentive_requires_attendance_lock", "0"
    )
    x.plain = _user(env)
    x.officer = _user(env, OFFICER)
    x.approver = _user(env, APPROVER)
    x.hrm = _user(env, "hr.group_hr_manager")
    x.hro = _user(env, "cd_hr_core.group_hr_officer")
    x.calibrator = _user(env, CALIBRATOR)
    x.mgr_user = _user(env)
    x.e_mgr = _employee(env, x.mgr_user)
    x.e_plain = _employee(env, x.plain, parent_id=x.e_mgr.id)
    x.e_officer = _employee(env, x.officer)
    x.e_hrm = _employee(env, x.hrm)
    x.e_col = _employee(env, parent_id=x.e_mgr.id)
    x.t1 = _employee(env)
    x.t2 = _employee(env)
    Card = env["fix.performance.scorecard"]
    # superuser-built facts (trusted seed path): published scorecards
    x.card1 = Card.create(
        {"employee_id": x.t1.id, "period": PERIOD, "first_time_fix": 1, "sla_hit": 1, "csat": 1}
    )
    x.card2 = Card.create(
        {
            "employee_id": x.t2.id,
            "period": PERIOD,
            "first_time_fix": 0.8,
            "sla_hit": 0.8,
            "csat": 0.8,
        }
    )
    (x.card1 | x.card2).action_publish()
    # BRU-PIC-01/02: a run computes only under an approved scheme version.
    # The superuser stands in for the HR Director and CFO here; the routed
    # two-signature flow is proven in test_a09_m57_round2.py.
    x.scheme = env["fix.incentive.scheme"].create(
        {"name": "A09 M57 scheme %d" % next(_SEQ), "code": "A9S%d" % next(_SEQ)}
    )
    x.version = env["fix.incentive.scheme.version"].create(
        {
            "scheme_id": x.scheme.id,
            "date_from": "2031-01-01",
            "band_base": 20000.0,
            "state": "approved",
        }
    )
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


def _run(w, user=None, **kw):
    vals = {"period": PERIOD, "scheme_id": w.scheme.id, **kw}
    return w.env["fix.incentive.run"].with_user(user or w.officer).create(vals)


def _computed_run(w):
    run = _run(w)
    run.with_user(w.officer).action_compute()
    return run


def _approved_run(w):
    run = _computed_run(w)
    run.with_user(w.officer).action_request_approval()
    task = _task_for(run, w.approver)
    assert task, "the approver got no task"
    task.with_user(w.approver).action_approve()
    return run


# ============================================================ roles (M57-F5)
def test_roles_exist_and_hold_only_root_and_admin(odoo_env):
    admin_root = odoo_env.ref("base.user_admin") | odoo_env.ref("base.user_root")
    for xmlid in (OFFICER, APPROVER, CALIBRATOR, COMPENSATION):
        group = odoo_env.ref(xmlid)
        assert odoo_env.ref("base.group_user") in group.implied_ids
        assert group.user_ids <= admin_root, (xmlid, group.user_ids.mapped("login"))


def test_incentive_officer_runs_the_engine_without_settings_admin(w):
    """M57-10/11: the engine needed base.group_system; the officer runs it."""
    assert not w.officer.has_group("base.group_system")
    run = _computed_run(w)
    assert run.state == "computed" and len(run.line_ids) == 2


def test_hr_manager_alone_cannot_create_or_compute_a_run(w):
    assert refused(w.env, lambda: _run(w, w.hrm))
    run = _run(w)
    assert refused(w.env, lambda: run.with_user(w.hrm).action_compute())


def test_plain_employee_cannot_read_runs_or_band_base(w, call):
    w.version.sudo().band_base = 77777.0
    _computed_run(w)
    assert not w.env(user=w.plain.id)["fix.incentive.run"].has_access("read")
    out = call(w.env(user=w.hrm.id), "model_report", module="M57", report="incentive_payout")
    assert all(r.get("band_base") != 77777.0 for r in out.get("rows", [])), out


# ============================================================ scorecards (M57-F2)
@pytest.mark.parametrize("field", ["first_time_fix", "sla_hit", "csat", "rework_rate"])
def test_scorecard_kpis_are_never_typed(w, field):
    card = w.env["fix.performance.scorecard"].create({"employee_id": w.e_col.id, "period": PERIOD})
    assert refused(w.env, lambda: _rpc(w.env, w.officer, card._name, "write", card, {field: 1.0}))
    assert card[field] == 0.0


def test_officer_cannot_create_a_typed_scorecard(w):
    assert refused(
        w.env,
        lambda: (
            w.env["fix.performance.scorecard"]
            .with_user(w.officer)
            .create({"employee_id": w.e_col.id, "period": PERIOD, "first_time_fix": 1, "csat": 1})
        ),
    )


def _orders_world(env, technician):
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "A9M57", "legal_name": "A09 M57 entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "A09M57 Branch",
            "code": "A9M57",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "A09M57Brand", "code": "A9M57B"})
    cust = env["res.partner"].create({"name": "A09 M57 Customer", "phone": "01711057999"})
    model = env["fix.device.model"].create(
        {"name": "A09M57 phone", "brand_id": brand.id, "device_type": "smartphone"}
    )
    orders = env["fix.service.order"]
    for i in range(4):
        dev = env["fix.device"].create(
            {"device_model_id": model.id, "owner_id": cust.id, "serial_number": "SN-A9M57-%d" % i}
        )
        orders |= env["fix.service.order"].create(
            {
                "device_id": dev.id,
                "customer_id": cust.id,
                "branch_id": branch.id,
                "fault_description": "a09 m57 facts",
                "service_type": "walk_in",
            }
        )
    orders.flush_recordset()
    done = fields.Datetime.to_datetime("2031-03-10 10:00:00")
    deadline = fields.Datetime.to_datetime("2031-03-11 10:00:00")
    late = fields.Datetime.to_datetime("2031-03-12 10:00:00")
    for i, so in enumerate(orders):
        # the superuser builds the facts the way the M01 flow leaves them
        env.cr.execute(
            "UPDATE fix_service_order SET state='delivered', technician_id=%s, delivered_at=%s, "
            "sla_resolution_deadline=%s, sla_resolution_at=%s, company_id=%s WHERE id=%s",
            (technician.id, done, deadline, late if i == 3 else done, env.company.id, so.id),
        )
    env.cr.execute(
        "UPDATE fix_service_order SET rework_of_id=%s, is_rework=true WHERE id=%s",
        (orders[0].id, orders[1].id),
    )
    orders.invalidate_recordset()
    return orders


def test_scorecard_is_computed_from_service_order_facts(w):
    _orders_world(w.env, w.e_col)
    card = (
        w.env["fix.performance.scorecard"]
        .with_user(w.officer)
        .create({"employee_id": w.e_col.id, "period": PERIOD})
    )
    card.with_user(w.officer).action_compute_from_orders()
    # 4 delivered orders; order 0 was reworked (by order 1, inside 30 days);
    # order 3 missed its SLA deadline.
    assert card.facts_orders == 4
    assert card.rework_rate == 0.25 and card.rework_30d_rate == 0.25
    # M57-F5: the rework ORDER is not a first-time fix either — it leaves both
    # sides of the ratio (2 of 3 non-rework orders), not 3 of 4
    assert card.first_time_fix == 0.6667
    assert card.sla_hit == 0.75
    assert card.computed_by_id == w.officer
    card.with_user(w.officer).action_publish()
    assert card.state == "published"
    assert refused(w.env, lambda: card.with_user(w.officer).action_compute_from_orders())


def test_no_facts_scores_zero_not_perfect(w):
    card = (
        w.env["fix.performance.scorecard"]
        .with_user(w.officer)
        .create({"employee_id": w.e_col.id, "period": PERIOD})
    )
    card.with_user(w.officer).action_compute_from_orders()
    assert card.facts_orders == 0 and card.score == 0.0


def test_nobody_computes_or_publishes_their_own_scorecard(w):
    card = w.env["fix.performance.scorecard"].create(
        {"employee_id": w.e_officer.id, "period": PERIOD}
    )
    assert refused(w.env, lambda: card.with_user(w.officer).action_compute_from_orders())
    assert refused(w.env, lambda: card.with_user(w.officer).action_publish())


def test_typed_draft_scorecard_cannot_be_published(w):
    card = (
        w.env["fix.performance.scorecard"]
        .with_user(w.officer)
        .create({"employee_id": w.e_col.id, "period": PERIOD})
    )
    assert "Compute the scorecard" in refused(
        w.env, lambda: card.with_user(w.officer).action_publish()
    )


# ============================================================ incentive run (I4, M57-F1/F6)
def test_compute_uses_published_scorecards_only(w):
    w.env["fix.performance.scorecard"].create(
        {"employee_id": w.e_col.id, "period": PERIOD, "first_time_fix": 1, "sla_hit": 1, "csat": 1}
    )  # a draft card: not paid
    run = _computed_run(w)
    assert run.line_ids.mapped("employee_id") == w.t1 | w.t2
    amounts = {line.employee_id: line.amount for line in run.line_ids}
    assert amounts == {w.t1: 3000.0, w.t2: 1600.0}


def test_compute_requires_the_attendance_lock_when_ruled(w):
    """BRU-PIC-07 (M57-12): no calculation before the M55 period lock."""
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_performance.incentive_requires_attendance_lock", "1"
    )
    run = _run(w)
    assert "BRU-PIC-07" in refused(w.env, lambda: run.with_user(w.officer).action_compute())
    lock = w.env["fix.attendance.lock"].create(
        {"name": "A09 M57 lock", "period_start": "2031-03-01", "period_end": "2031-03-31"}
    )
    w.env.cr.execute("UPDATE fix_attendance_lock SET state='locked' WHERE id=%s", (lock.id,))
    lock.invalidate_recordset()
    run.with_user(w.officer).action_compute()
    assert run.state == "computed"


def test_run_state_cannot_be_written(w):
    run = _run(w)
    for target in ("computed", "approved"):
        assert refused(
            w.env, lambda t=target: _rpc(w.env, w.officer, run._name, "write", run, {"state": t})
        )
    assert run.state == "draft"


def test_the_preparer_never_approves(w):
    run = _computed_run(w)
    assert refused(w.env, lambda: run.with_user(w.officer).action_approve())
    run.with_user(w.officer).action_request_approval()
    assert not _task_for(run, w.officer)
    assert run.approval_state == "pending"
    # a direct call by the real approver, outside the inbox, is refused too
    assert refused(w.env, lambda: run.with_user(w.approver).action_approve())


def test_routed_approval_freezes_the_run_and_pays_nothing_itself(w):
    run = _approved_run(w)
    assert run.state == "approved" and run.approval_state == "approved"
    assert run.approved_by_id == w.approver and run.approved_total == 4600.0
    line = run.line_ids.filtered(lambda r: r.employee_id == w.t2)
    assert _events(w.env, "incentive.approved", line.id)[0]["amount"] == 1600.0
    for user in (w.officer, w.approver):
        assert refused(
            w.env, lambda u=user: _rpc(w.env, u, line._name, "write", line, {"amount": 250000})
        )
    assert refused(
        w.env, lambda: _rpc(w.env, w.officer, run._name, "write", run, {"band_base": 99999})
    )
    assert refused(w.env, lambda: run.with_user(w.officer).action_reset_draft())
    assert line.amount == 1600.0


def test_computed_line_amount_cannot_be_tampered(w):
    """M57-14/21: 1,600 -> 250,000 before approval, by ORM or the workspace."""
    run = _computed_run(w)
    line = run.line_ids.filtered(lambda r: r.employee_id == w.t2)
    assert refused(
        w.env, lambda: _rpc(w.env, w.officer, line._name, "write", line, {"amount": 250000})
    )
    assert line.amount == 1600.0


def test_workspace_cannot_write_a_line_amount(w, call):
    run = _computed_run(w)
    line = run.line_ids[:1]
    before = line.amount
    out = call(
        w.env(user=w.officer.id),
        "model_write",
        model="fix.incentive.line",
        record_id=line.id,
        values={"amount": 123456},
    )
    assert "error" in out or line.amount == before
    assert line.amount == before


def test_no_hand_made_lines(w):
    """M57-17: a 500,000 line for oneself on an approved run."""
    run = _approved_run(w)
    for user in (w.officer, w.approver):
        assert refused(
            w.env,
            lambda u=user: (
                w.env["fix.incentive.line"]
                .with_user(u)
                .create(
                    {
                        "run_id": run.id,
                        "scorecard_id": w.card1.id,
                        "employee_id": w.e_officer.id,
                        "amount": 500000,
                    }
                )
            ),
        )


def test_one_run_per_period_and_company(w):
    """M57-18: a second run for the period cannot exist."""
    _computed_run(w)
    try:
        with w.env.cr.savepoint():
            _run(w)
            w.env.flush_all()
    except Exception as exc:  # the UNIQUE constraint (IntegrityError / ValidationError)
        assert "period" in str(exc).lower() or "unique" in str(exc).lower()
    else:
        pytest.fail("a second incentive run for the same period was created")


def test_someone_with_a_line_never_approves_the_run(w):
    conflicted = _user(w.env, APPROVER)
    emp = _employee(w.env, conflicted)
    card = w.env["fix.performance.scorecard"].create(
        {"employee_id": emp.id, "period": PERIOD, "first_time_fix": 1, "sla_hit": 1, "csat": 1}
    )
    card.action_publish()
    run = _computed_run(w)
    assert emp in run.line_ids.mapped("employee_id")
    run.with_user(w.officer).action_request_approval()
    assert not _task_for(run, conflicted)
    assert _task_for(run, w.approver)


def test_rejection_keeps_the_run_unapproved(w):
    run = _computed_run(w)
    run.with_user(w.officer).action_request_approval()
    _task_for(run, w.approver).with_user(w.approver).action_reject("base too high")
    assert run.state == "computed" and run.approval_state == "rejected"
    run.with_user(w.officer).action_reset_draft()
    assert run.state == "draft" and not run.line_ids


# ============================================================ I4 hand-off to payroll
def _payslips(w):
    period = w.env["fix.payroll.period"].create(
        {"name": PERIOD, "period_start": "2031-03-01", "period_end": "2031-03-31"}
    )
    slips = w.env["fix.payslip"]
    for emp in (w.t1, w.t2):
        slips |= (
            w.env["fix.payslip"]
            ._guarded()
            .create({"period_id": period.id, "employee_id": emp.id, "basic": 20000})
        )
    return slips


def test_m57_never_writes_the_payslip(w):
    slips = _payslips(w)
    _approved_run(w)
    assert all(s.incentive == 0 for s in slips)


def test_attach_payslip_only_for_an_approved_line_of_that_employee(w):
    slips = _payslips(w)
    s1 = slips.filtered(lambda s: s.employee_id == w.t1)
    s2 = slips - s1
    run = _computed_run(w)
    l1 = run.line_ids.filtered(lambda r: r.employee_id == w.t1)
    assert refused(w.env, lambda: l1._fix_attach_payslip(s1)), "attached a computed line"
    run.with_user(w.officer).action_request_approval()
    _task_for(run, w.approver).with_user(w.approver).action_approve()
    assert refused(w.env, lambda: l1._fix_attach_payslip(s2)), "attached to another employee"
    l1._fix_attach_payslip(s1)
    assert l1.applied_to_payslip and l1.payslip_ref_id == s1.id
    l1._fix_attach_payslip(s1)  # idempotent
    other = (
        w.env["fix.payslip"]
        ._guarded()
        .create({"period_id": s1.period_id.id, "employee_id": w.t1.id, "basic": 1})
    )
    assert "already paid" in refused(w.env, lambda: l1._fix_attach_payslip(other))


def test_attach_fields_are_not_writable(w):
    run = _approved_run(w)
    line = run.line_ids[:1]
    assert refused(
        w.env,
        lambda: _rpc(w.env, w.officer, line._name, "write", line, {"applied_to_payslip": True}),
    )


# ============================================================ review cycle (M57-F4)
def _review(w, employee=None, **vals):
    return w.env["fix.performance.review"].create(
        {"employee_id": (employee or w.e_plain).id, "period": PERIOD, **vals}
    )


def test_reviewer_defaults_to_and_must_be_the_line_manager(w):
    rev = _review(w)
    assert rev.reviewer_id == w.e_mgr
    assert refused(
        w.env, lambda: _rpc(w.env, w.hrm, rev._name, "write", rev, {"reviewer_id": w.e_col.id})
    )
    own = _review(w, w.e_hrm)
    assert refused(
        w.env, lambda: _rpc(w.env, w.hrm, own._name, "write", own, {"reviewer_id": w.e_hrm.id})
    )


def test_employee_records_own_self_rating_only(w):
    rev = _review(w)
    col = _review(w, w.e_col)
    rev.with_user(w.plain).action_record_self_rating(4)
    assert rev.self_rating == 4
    # no write access at all: RAP X-02 keeps base.group_user read-only
    assert refused(w.env, lambda: _rpc(w.env, w.plain, rev._name, "write", rev, {"self_rating": 5}))
    assert refused(w.env, lambda: col.with_user(w.plain).action_record_self_rating(5))
    assert refused(w.env, lambda: rev.with_user(w.plain).action_record_manager_rating(5))


def test_line_manager_rates_their_report_and_nobody_else_does(w):
    rev = _review(w)
    rev.with_user(w.mgr_user).action_record_manager_rating(3)
    assert rev.manager_rating == 3
    assert refused(
        w.env, lambda: _rpc(w.env, w.hrm, rev._name, "write", rev, {"manager_rating": 5})
    )


def test_ratings_stay_on_the_scale(w):
    rev = _review(w)
    assert refused(w.env, lambda: rev.with_user(w.mgr_user).action_record_manager_rating(42))


def test_the_full_cycle_with_calibration_by_someone_else(w):
    rev = _review(w)
    rev.with_user(w.hrm).action_start()
    rev.with_user(w.plain).action_record_self_rating(4)
    rev.with_user(w.plain).action_submit_self_assessment()
    rev.with_user(w.mgr_user).action_record_manager_rating(3)
    rev.with_user(w.mgr_user).action_manager_review()
    assert rev.approval_state == "pending"
    # the manager cannot calibrate the rating they gave, nor anyone directly
    assert not _task_for(rev, w.mgr_user)
    assert refused(w.env, lambda: rev.with_user(w.calibrator).action_calibrate())
    assert refused(w.env, lambda: rev.with_user(w.mgr_user).action_record_manager_rating(5))
    _task_for(rev, w.calibrator).with_user(w.calibrator).action_approve()
    assert rev.state == "calibrated" and rev.calibrated_rating == 3
    assert rev.calibrated_by_id == w.calibrator
    rev.with_user(w.hrm).action_close()
    assert rev.state == "closed"
    # a closed review never reopens (M57-30)
    assert refused(w.env, lambda: rev.with_user(w.mgr_user).action_record_manager_rating(1))
    assert refused(w.env, lambda: rev.with_user(w.mgr_user).action_manager_review())


def test_review_state_and_calibration_are_not_writable(w, call):
    rev = _review(w, w.e_col)
    for vals in ({"state": "closed"}, {"calibrated_rating": 5}):
        assert refused(w.env, lambda v=vals: _rpc(w.env, w.hrm, rev._name, "write", rev, v))
    out = call(
        w.env(user=w.hrm.id),
        "model_write",
        model="fix.performance.review",
        record_id=rev.id,
        values={"state": "closed", "calibrated_rating": 5},
    )
    assert rev.state == "draft" and rev.calibrated_rating == 0, out


def test_subject_of_a_review_never_calibrates_it(w):
    calib_emp_user = _user(w.env, CALIBRATOR)
    subject = _employee(w.env, calib_emp_user, parent_id=w.e_mgr.id)
    rev = _review(w, subject)
    rev.with_user(w.hrm).action_start()
    rev.sudo()._guarded().write({"state": "manager_review"})
    rev.with_user(w.mgr_user).action_record_manager_rating(4)
    rev.with_user(w.mgr_user).action_manager_review()
    assert not _task_for(rev, calib_emp_user)


# ============================================================ goals (M57-F11)
def _goal(w, weight=50.0, **vals):
    return (
        w.env["fix.performance.goal"]
        .with_user(w.hrm)
        .create(
            {
                "name": "A09 M57 goal",
                "employee_id": w.e_plain.id,
                "period": PERIOD,
                "weight": weight,
                **vals,
            }
        )
    )


def test_goal_weights_cannot_exceed_100(w):
    _goal(w, 60)
    assert refused(w.env, lambda: _goal(w, 50))


def test_goal_activation_needs_both_agreements_and_100_percent(w):
    g1 = _goal(w, 60)
    g2 = _goal(w, 40)
    assert "agree" in refused(w.env, lambda: g1.with_user(w.hrm).action_activate())
    assert refused(w.env, lambda: g1.with_user(w.hrm).action_agree())  # HR is neither party
    g1.with_user(w.plain).action_agree()
    g1.with_user(w.mgr_user).action_agree()
    assert g1.employee_agreed_by_id == w.plain and g1.manager_agreed_by_id == w.mgr_user
    g1.with_user(w.hrm).action_activate()
    assert g1.state == "active"
    g2.sudo().unlink()
    g3 = _goal(w, 30)
    g3.with_user(w.plain).action_agree()
    g3.with_user(w.mgr_user).action_agree()
    assert "100" in refused(w.env, lambda: g3.with_user(w.hrm).action_activate())


def test_closed_goal_is_final(w):
    g = _goal(w, 100, target_value=100, actual_value=50)
    g.with_user(w.plain).action_agree()
    g.with_user(w.mgr_user).action_agree()
    g.with_user(w.hrm).action_activate()
    g.with_user(w.mgr_user).action_close()
    assert g.state == "missed"
    assert refused(w.env, lambda: _rpc(w.env, w.hrm, g._name, "write", g, {"actual_value": 500}))
    assert refused(w.env, lambda: g.with_user(w.hrm).action_activate())
    assert refused(w.env, lambda: _rpc(w.env, w.hrm, g._name, "write", g, {"state": "achieved"}))


# ============================================================ PIP (M57-F7)
def _pip(w, **vals):
    return (
        w.env["fix.performance.pip"]
        .with_user(w.hrm)
        .create(
            {
                "employee_id": w.e_col.id,
                "end_date": fields.Date.today() + timedelta(days=30),
                "reason": "A09 M57 gaps",
                **vals,
            }
        )
    )


def test_draft_pip_never_closes(w):
    p = _pip(w, outcome="exit")
    assert refused(w.env, lambda: p.with_user(w.hrm).action_close())


def test_exit_outcome_only_after_the_plan_ran(w):
    p = _pip(w)
    p.with_user(w.hrm).action_start()
    p.with_user(w.hrm).write({"outcome": "exit"})
    assert "end date" in refused(w.env, lambda: p.with_user(w.hrm).action_close())


def test_closed_pip_never_restarts_or_changes(w):
    p = _pip(w)
    p.with_user(w.hrm).action_start()
    p.with_user(w.hrm).write({"outcome": "improved"})
    p.with_user(w.hrm).action_close()
    assert refused(w.env, lambda: p.with_user(w.hrm).action_start())
    assert refused(w.env, lambda: _rpc(w.env, w.hrm, p._name, "write", p, {"outcome": "exit"}))
    assert refused(w.env, lambda: _rpc(w.env, w.hrm, p._name, "write", p, {"state": "active"}))


def test_pip_mentor_is_not_the_employee(w):
    assert refused(w.env, lambda: _pip(w, mentor_id=w.e_col.id))


# ============================================================ recognition (M57-F8)
def test_hr_cannot_award_themself(w):
    """M57-39: an HR Manager awarded himself BDT 1,000,000."""
    Rec = w.env["fix.performance.recognition"].with_user(w.hrm)
    for prize in (0, 1000000):
        assert refused(
            w.env, lambda p=prize: Rec.create({"employee_id": w.e_hrm.id, "prize_amount": p})
        )
    # nor through a recognition someone else drafted for them
    seeded = w.env["fix.performance.recognition"].create(
        {"employee_id": w.e_hrm.id, "prize_amount": 9000}
    )
    assert refused(w.env, lambda: seeded.with_user(w.hrm).action_request_approval())
    seeded.write({"prize_amount": 0})
    assert refused(w.env, lambda: seeded.with_user(w.hrm).action_award())


def test_a_prize_is_approved_by_the_approver_not_the_awarder(w):
    rec = (
        w.env["fix.performance.recognition"]
        .with_user(w.hrm)
        .create(
            {"employee_id": w.e_col.id, "prize_amount": 5000, "citation": "A09 M57 FTF champion"}
        )
    )
    assert "Request Approval" in refused(w.env, lambda: rec.with_user(w.hrm).action_award())
    assert refused(w.env, lambda: _rpc(w.env, w.hrm, rec._name, "write", rec, {"state": "awarded"}))
    rec.with_user(w.hrm).action_request_approval()
    assert not _task_for(rec, w.hrm)
    _task_for(rec, w.approver).with_user(w.approver).action_approve()
    assert rec.state == "awarded" and rec.approved_prize == 5000
    payload = _events(w.env, "recognition.awarded", rec.id)[0]
    assert payload["employee_id"] == w.e_col.id and payload["amount"] == 5000
    assert refused(
        w.env, lambda: _rpc(w.env, w.hrm, rec._name, "write", rec, {"prize_amount": 500000})
    )


def test_a_non_monetary_award_needs_no_approval(w):
    rec = w.env["fix.performance.recognition"].with_user(w.hrm).create({"employee_id": w.e_col.id})
    rec.with_user(w.hrm).action_award()
    assert rec.state == "awarded" and rec.awarded_by_id == w.hrm


# ============================================================ I7 bands (M57-F9)
def _band(w, grade="A9G", lo=20000, mid=25000, hi=30000):
    return w.env["fix.compensation.band"].create(
        {
            "name": "A09 M57 band %s" % grade,
            "grade": grade,
            "range_min": lo,
            "range_mid": mid,
            "range_max": hi,
        }
    )


def _contract_vals(emp, basic):
    return {
        "employee_id": emp.id,
        "contract_type": "permanent",
        "joining_date": fields.Date.today(),
        "weekly_hours": 48,
        "basic_monthly": basic,
    }


def test_contract_outside_the_band_is_refused(w):
    """M57-40: a 500,000 contract for a grade whose band max is 30,000."""
    _band(w)
    pos = w.env["fix.org.position"].create({"name": "A09 M57 Technician", "grade": "A9G"})
    w.e_col.position_id = pos
    Contract = w.env["fix.employment.contract"].with_user(w.hro)
    # a DRAFT may carry any salary (M58's hire drafts one from the offer, I6);
    # payroll pays no draft. The band binds when the contract leaves draft.
    high = Contract.create(_contract_vals(w.e_col, 500000))
    assert "outside" in refused(w.env, lambda: high.sudo().write({"state": "active"}))
    assert high.state == "draft"
    ok = Contract.create(_contract_vals(w.e_col, 25000))
    ok.sudo().write({"state": "active"})
    # an active contract's terms are frozen (M21, BRU-HCM-03): a raise is a
    # new version, which is band-checked when it is activated like any other
    assert "never edited" in refused(w.env, lambda: ok.write({"basic_monthly": 45000}))
    assert ok.basic_monthly == 25000


def test_no_configured_band_means_no_band_check(w):
    pos = w.env["fix.org.position"].create({"name": "A09 M57 Unbanded", "grade": "A9-NONE"})
    w.e_col.position_id = pos
    contract = (
        w.env["fix.employment.contract"].with_user(w.hro).create(_contract_vals(w.e_col, 500000))
    )
    contract.sudo().write({"state": "active"})
    assert contract.state == "active"


def test_band_ranges_are_for_the_compensation_manager_only(w):
    band = _band(w)
    for user in (w.hrm, w.hro, w.officer):
        assert refused(
            w.env,
            lambda u=user: (
                w.env(user=u.id)["fix.compensation.band"].browse(band.id).read(["range_max"])
            ),
        )
    comp = _user(w.env, COMPENSATION)
    assert w.env(user=comp.id)["fix.compensation.band"].browse(band.id).range_max == 30000


# ============================================================ succession (M57-F13)
def test_incumbent_is_not_their_own_successor(w):
    assert refused(
        w.env,
        lambda: (
            w.env["fix.succession.plan"]
            .with_user(w.hrm)
            .create(
                {"position_name": "A09 key", "incumbent_id": w.e_col.id, "successor_id": w.e_col.id}
            )
        ),
    )


# ============================================================ workspace (M57-F10)
def test_incentive_accuracy_counts_approved_runs(w):
    _approved_run(w)
    assert a09.m57.kpis(w.env)["incentive_accuracy"] == 100.0


def test_workspace_offers_the_new_actions_and_not_apply(odoo_env):
    surfaces = a09.SURFACES
    assert "action_apply" not in surfaces["fix.incentive.run"]["actions"]
    assert {"action_compute", "action_request_approval", "action_reset_draft"} <= surfaces[
        "fix.incentive.run"
    ]["actions"]
    assert "action_calibrate" not in surfaces["fix.performance.review"]["actions"]
    assert {"action_agree"} <= surfaces["fix.performance.goal"]["actions"]
    assert {"action_compute_from_orders"} <= surfaces["fix.performance.scorecard"]["actions"]
    assert {"action_request_approval"} <= surfaces["fix.performance.recognition"]["actions"]


def test_workspace_routes_an_incentive_approval_request(w, call):
    run = _computed_run(w)
    out = call(
        w.env(user=w.officer.id),
        "model_action",
        model="fix.incentive.run",
        ids=[run.id],
        method="action_request_approval",
    )
    assert out.get("success"), out
    assert run.approval_state == "pending"


# ============================================================ deployment
def test_access_rows_exist(odoo_env):
    Access = odoo_env["ir.model.access"].sudo()
    for model, group in (
        ("fix.incentive.run", OFFICER),
        ("fix.incentive.run", APPROVER),
        ("fix.incentive.line", OFFICER),
        ("fix.performance.scorecard", OFFICER),
        ("fix.performance.recognition", APPROVER),
        ("fix.performance.review", CALIBRATOR),
        ("fix.compensation.band", COMPENSATION),
    ):
        assert Access.search_count(
            [("model_id.model", "=", model), ("group_id", "=", odoo_env.ref(group).id)]
        ), (model, group)
    band_system = Access.search_count(
        [
            ("model_id.model", "=", "fix.compensation.band"),
            ("group_id", "=", odoo_env.ref("base.group_system").id),
        ]
    )
    assert not band_system, "compensation bands still need Settings-admin"


def test_attach_survives_a_recalculation_that_deleted_the_slip(w):
    """M56's recalculation deletes and recreates slips: a line whose slip is
    gone re-attaches to the new one (a dangling payslip_ref_id never blocks)."""
    slips = _payslips(w)
    s1 = slips.filtered(lambda s: s.employee_id == w.t1)
    run = _approved_run(w)
    line = run.line_ids.filtered(lambda r: r.employee_id == w.t1)
    line._fix_attach_payslip(s1)
    period = s1.period_id
    s1.sudo().unlink()
    fresh = (
        w.env["fix.payslip"]
        ._guarded()
        .create({"period_id": period.id, "employee_id": w.t1.id, "basic": 20000})
    )
    line._fix_attach_payslip(fresh)
    assert line.payslip_ref_id == fresh.id and line.applied_to_payslip
