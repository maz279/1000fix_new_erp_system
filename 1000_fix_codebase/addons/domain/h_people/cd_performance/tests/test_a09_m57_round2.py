# A09 round 2, M57 acceptance suite: incentive schemes and versions
# (BRU-PIC-01/02), proration and eligibility (FR-PIC-028/032), the dispute
# window (BRU-PIC-12), clawbacks (BRU-PIC-11), compensation proposals
# (BRU-PIC-17) and the line manager's calibration request and recall.
#
# Attacked as freshly created NON-admin users through call_kw and the real
# /p03 controller; the superuser only builds the world.
import itertools
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
PERIOD = "2031-05"
PREV = "2031-04"
OFFICER = "cd_performance.group_performance_officer"
APPROVER = "cd_performance.group_incentive_approver"
CALIBRATOR = "cd_performance.group_performance_calibrator"
COMPENSATION = "cd_performance.group_compensation"
HRD = "cd_performance.group_scheme_hr_director"
CFO = "cd_performance.group_scheme_cfo"
DISPUTE_DAYS = "cd_performance.incentive_dispute_days"
CLAWBACK_DAYS = "cd_performance.incentive_clawback_days"
LOCK = "cd_performance.incentive_requires_attendance_lock"


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
                "name": "A09 M57r2 User %d" % n,
                "login": "a09-m57r2-%d@test.local" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _employee(env, user=None, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create(
        {"name": "A09 M57r2 Employee %d" % n, "user_id": user.id if user else False, **vals}
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


@pytest.fixture
def r(odoo_env):
    env = odoo_env

    class R:
        pass

    x = R()
    x.env = env
    params = env["ir.config_parameter"].sudo()
    params.set_param(LOCK, "0")
    params.set_param(DISPUTE_DAYS, "0")
    params.set_param(CLAWBACK_DAYS, "0")
    x.officer = _user(env, OFFICER)
    x.officer2 = _user(env, OFFICER)
    x.approver = _user(env, APPROVER)
    x.hrd = _user(env, HRD)
    x.cfo = _user(env, CFO)
    x.calibrator = _user(env, CALIBRATOR)
    x.comp = _user(env, COMPENSATION)
    x.plain = _user(env)
    x.tech_user = _user(env)
    x.mgr_user = _user(env)
    x.e_mgr = _employee(env, x.mgr_user)
    x.e_tech = _employee(env, x.tech_user, parent_id=x.e_mgr.id)
    x.e_plain = _employee(env, x.plain)
    x.scheme = env["fix.incentive.scheme"].create(
        {"name": "A09 r2 scheme %d" % next(_SEQ), "code": "R2S%d" % next(_SEQ)}
    )
    return x


def _version(x, state="approved", **vals):
    base = {
        "scheme_id": x.scheme.id,
        "date_from": "2031-01-01",
        "band_base": 20000.0,
        "state": state,
    }
    base.update(vals)
    return x.env["fix.incentive.scheme.version"].create(base)


def _card(x, employee, period=PERIOD, kpi=1.0):
    card = x.env["fix.performance.scorecard"].create(
        {
            "employee_id": employee.id,
            "period": period,
            "first_time_fix": kpi,
            "sla_hit": kpi,
            "csat": kpi,
        }
    )
    card.action_publish()
    return card


def _run(x, period=PERIOD):
    return (
        x.env["fix.incentive.run"]
        .with_user(x.officer)
        .create({"period": period, "scheme_id": x.scheme.id})
    )


def _line(run, employee):
    return run.line_ids.filtered(lambda r: r.employee_id == employee and r.line_type == "incentive")


def _approve_run(x, run):
    run.with_user(x.officer).action_request_approval()
    _task_for(run, x.approver).with_user(x.approver).action_approve()
    assert run.state == "approved"


# ====================================================== scheme versions (BRU-PIC-01/02)
def test_seeded_version_one_is_the_coded_figures_unsourced_and_draft(odoo_env):
    v1 = odoo_env.ref("cd_performance.scheme_technician_v1")
    assert v1.state == "draft", "an unsourced version must not be in force"
    assert (v1.cut_top, v1.cut_mid, v1.cut_low) == (0.90, 0.75, 0.60)
    assert (v1.rate_top, v1.rate_mid, v1.rate_low) == (15.0, 8.0, 4.0)
    assert "unsourced" in v1.basis.lower()
    assert v1.min_service_days == 0 and v1.long_leave_days == 0


def test_a_version_is_approved_by_the_hr_director_then_the_cfo(r):
    v = (
        r.env["fix.incentive.scheme.version"]
        .with_user(r.officer)
        .create({"scheme_id": r.scheme.id, "date_from": "2031-01-01", "band_base": 20000.0})
    )
    assert v.state == "draft" and v.version_no >= 1
    v.with_user(r.officer).action_request_approval()
    assert v.state == "hr_review" and v.approval_state == "pending"
    assert not _task_for(v, r.cfo), "the CFO signed before the HR Director"
    assert refused(r.env, lambda: v.with_user(r.hrd).action_approve())  # not from the inbox
    _task_for(v, r.hrd).with_user(r.hrd).action_approve()
    assert v.state == "cfo_review" and v.hr_director_id == r.hrd
    assert v.approval_state == "pending"
    assert not _task_for(v, r.hrd)
    _task_for(v, r.cfo).with_user(r.cfo).action_approve()
    assert v.state == "approved" and v.approval_state == "approved"
    assert v.cfo_id == r.cfo and v.hr_director_id == r.hrd


def test_one_person_holding_both_signatures_signs_only_once(r):
    both = _user(r.env, HRD, CFO)
    v = _version(r, state="draft")
    v.with_user(r.officer).action_request_approval()
    _task_for(v, both).with_user(both).action_approve()
    assert v.state == "cfo_review"
    assert not _task_for(v, both), "the HR Director was routed the CFO step too"
    assert _task_for(v, r.cfo)


def test_the_requester_never_signs_a_version(r):
    officer_hrd = _user(r.env, OFFICER, HRD)
    v = _version(r, state="draft")
    v.with_user(officer_hrd).action_request_approval()
    assert not _task_for(v, officer_hrd) and _task_for(v, r.hrd)


def test_version_state_and_signatures_cannot_be_forged(r):
    Version = r.env["fix.incentive.scheme.version"].with_user(r.officer)
    assert refused(
        r.env,
        lambda: Version.create(
            {"scheme_id": r.scheme.id, "date_from": "2031-01-01", "state": "approved"}
        ),
    )
    v = _version(r, state="draft")
    for vals in ({"state": "approved"}, {"cfo_id": r.cfo.id}, {"hr_director_id": r.hrd.id}):
        assert refused(r.env, lambda vv=vals: _rpc(r.env, r.officer, v._name, "write", v, vv))
    assert v.state == "draft"


def test_an_approved_version_is_frozen(r):
    v = _version(r)
    for vals in ({"rate_top": 25.0}, {"band_base": 99999.0}, {"date_from": "2030-01-01"}):
        assert refused(r.env, lambda vv=vals: _rpc(r.env, r.officer, v._name, "write", v, vv))
    assert v.rate_top == 15.0


def test_bands_must_descend_and_rates_stay_percentages(r):
    assert refused(r.env, lambda: _version(r, state="draft", cut_mid=0.95))
    assert refused(r.env, lambda: _version(r, state="draft", rate_top=150.0))


def test_no_run_computes_without_an_approved_version(r):
    _version(r, state="draft")
    _card(r, r.e_tech)
    run = _run(r)
    err = refused(r.env, lambda: run.with_user(r.officer).action_compute())
    assert err and "BRU-PIC-01" in err
    assert run.state == "draft"


def test_the_run_uses_and_pins_the_version_in_force(r):
    v1 = _version(r, rate_top=10.0)
    _card(r, r.e_tech)
    run = _run(r)
    run.with_user(r.officer).action_compute()
    assert run.scheme_version_id == v1
    assert _line(run, r.e_tech).amount == 2000.0  # 20,000 x the version's 10 %
    assert run.sudo().band_base == 20000.0
    # a later version does not reach a computed run
    _version(r, date_from="2031-05-15", rate_top=30.0, band_base=50000.0)
    assert run.scheme_version_id == v1 and _line(run, r.e_tech).amount == 2000.0
    assert refused(
        r.env,
        lambda: _rpc(r.env, r.officer, run._name, "write", run, {"scheme_version_id": False}),
    )


def test_a_version_effective_after_the_period_is_not_in_force(r):
    _version(r, date_from="2031-06-01")
    _card(r, r.e_tech)
    run = _run(r)
    assert "BRU-PIC-01" in refused(r.env, lambda: run.with_user(r.officer).action_compute())


# ====================================================== the attendance lock (BRU-PIC-07)
def test_the_attendance_lock_is_seeded_enforced(odoo_env):
    param = odoo_env.ref("cd_performance.param_incentive_requires_attendance_lock")
    assert param.key == LOCK and param.value == "1"
    assert odoo_env["fix.incentive.run"]._fix_attendance_lock_required()


def test_the_seeded_lock_setting_refuses_an_unlocked_period(r):
    r.env["ir.config_parameter"].sudo().set_param(LOCK, "1")
    _version(r)
    _card(r, r.e_tech)
    run = _run(r)
    assert "BRU-PIC-07" in refused(r.env, lambda: run.with_user(r.officer).action_compute())


# ====================================================== proration (FR-PIC-028/032)
def _leave(x, employee, date_from, date_to):
    ltype = x.env["fix.leave.type"].create(
        {"code": "A9R2L%d" % next(_SEQ), "name": "A09 r2 leave", "entitlement_days": 60}
    )
    return x.env["fix.leave.request"].create(
        {
            "employee_id": employee.id,
            "leave_type_id": ltype.id,
            "date_from": date_from,
            "date_to": date_to,
            "state": "approved",
        }
    )


def test_joiner_and_leaver_are_prorated_by_days(r):
    _version(r)
    joiner = _employee(r.env, joining_date="2031-05-11")
    leaver = _employee(r.env, joining_date="2020-01-01", left_date="2031-05-10")
    full = _employee(r.env, joining_date="2020-01-01")
    for emp in (joiner, leaver, full):
        _card(r, emp)
    run = _run(r)
    run.with_user(r.officer).action_compute()
    # 3,000 for a full May (31 days) at the top band
    assert _line(run, full).amount == 3000.0
    assert _line(run, joiner).eligible_days == 21
    assert _line(run, joiner).amount == round(3000.0 * round(21 / 31, 4), 2)
    assert _line(run, leaver).eligible_days == 10
    assert _line(run, leaver).amount == round(3000.0 * round(10 / 31, 4), 2)
    assert "joined" in _line(run, joiner).eligibility_note


def test_long_leave_is_prorated_when_the_scheme_rules_it(r):
    _version(r, long_leave_days=5)
    emp = _employee(r.env, joining_date="2020-01-01")
    short = _employee(r.env, joining_date="2020-01-01")
    _leave(r, emp, "2031-05-01", "2031-05-10")  # 10 days: long leave
    _leave(r, short, "2031-05-01", "2031-05-02")  # 2 days: not long leave
    _card(r, emp)
    _card(r, short)
    run = _run(r)
    run.with_user(r.officer).action_compute()
    assert _line(run, emp).eligible_days == 21
    assert _line(run, short).eligible_days == 31 and _line(run, short).amount == 3000.0


def test_minimum_service_comes_from_the_scheme(r):
    _version(r, min_service_days=90)
    new = _employee(r.env, joining_date="2031-04-20")
    unknown = _employee(r.env)
    old = _employee(r.env, joining_date="2020-01-01")
    for emp in (new, unknown, old):
        _card(r, emp)
    run = _run(r)
    run.with_user(r.officer).action_compute()
    assert not _line(run, new).eligible and _line(run, new).amount == 0.0
    assert "service" in _line(run, new).eligibility_note
    assert not _line(run, unknown).eligible, "no joining date must not pass a ruled minimum"
    assert _line(run, old).eligible and _line(run, old).amount == 3000.0


def test_proration_fields_are_not_writable(r):
    _version(r)
    _card(r, r.e_tech)
    run = _run(r)
    run.with_user(r.officer).action_compute()
    line = _line(run, r.e_tech)
    for vals in ({"proration_factor": 2.0}, {"eligible": False}, {"line_type": "clawback"}):
        assert refused(r.env, lambda vv=vals: _rpc(r.env, r.officer, line._name, "write", line, vv))


# ====================================================== disputes (BRU-PIC-12)
def _computed(r, days=5):
    r.env["ir.config_parameter"].sudo().set_param(DISPUTE_DAYS, str(days))
    _version(r)
    _card(r, r.e_tech)
    _card(r, r.e_plain, kpi=0.8)
    run = _run(r)
    run.with_user(r.officer).action_compute()
    return run


def test_no_window_means_no_dispute(r):
    run = _computed(r, days=0)
    assert not run.dispute_deadline
    line = _line(run, r.e_tech)
    assert "No dispute window" in refused(
        r.env, lambda: line.with_user(r.tech_user).action_raise_dispute("wrong")
    )


def test_the_employee_disputes_their_own_line_inside_the_window(r):
    run = _computed(r)
    # the deadline is stamped on the context date (env tz Asia/Dhaka)
    assert run.dispute_deadline == fields.Date.context_today(run) + timedelta(days=5)
    line = _line(run, r.e_tech)
    other = _line(run, r.e_plain)
    assert refused(r.env, lambda: other.with_user(r.tech_user).action_raise_dispute("not mine"))
    assert refused(r.env, lambda: line.with_user(r.plain).action_raise_dispute("not mine"))
    assert refused(r.env, lambda: line.with_user(r.tech_user).action_raise_dispute(""))
    out = line.with_user(r.tech_user).action_raise_dispute("two jobs missing from my card")
    dispute = r.env["fix.incentive.dispute"].browse(out["dispute_ids"])
    assert dispute.state == "open" and dispute.raised_by_id == r.tech_user
    # nobody types a dispute or its answer
    assert refused(
        r.env,
        lambda: (
            r.env["fix.incentive.dispute"]
            .with_user(r.officer)
            .create({"run_id": run.id, "employee_id": r.e_tech.id, "reason": "x"})
        ),
    )
    assert refused(
        r.env,
        lambda: _rpc(r.env, r.officer, dispute._name, "write", dispute, {"state": "rejected"}),
    )


def test_an_open_dispute_blocks_the_approval(r):
    run = _computed(r)
    line = _line(run, r.e_tech)
    # the request waits for the window
    assert "BRU-PIC-12" in refused(
        r.env, lambda: run.with_user(r.officer).action_request_approval()
    )
    line.with_user(r.tech_user).action_raise_dispute("two jobs missing")
    run.sudo()._guarded().write({"dispute_deadline": fields.Date.today() - timedelta(days=1)})
    err = refused(r.env, lambda: run.with_user(r.officer).action_request_approval())
    assert err and "unsettled dispute" in err
    dispute = line.dispute_ids
    assert refused(r.env, lambda: dispute.with_user(r.tech_user).action_reject("no"))
    dispute.with_user(r.officer).action_reject("the two jobs closed in June")
    assert dispute.state == "rejected" and dispute.resolved_by_id == r.officer
    _approve_run(r, run)


def test_a_dispute_after_the_window_or_the_approval_is_refused(r):
    run = _computed(r)
    line = _line(run, r.e_tech)
    run.sudo()._guarded().write({"dispute_deadline": fields.Date.today() - timedelta(days=1)})
    assert "closed" in refused(
        r.env, lambda: line.with_user(r.tech_user).action_raise_dispute("late")
    )
    _approve_run(r, run)
    assert refused(r.env, lambda: line.with_user(r.tech_user).action_raise_dispute("after"))


def test_an_upheld_dispute_needs_the_run_recomputed(r):
    run = _computed(r)
    line = _line(run, r.e_tech)
    line.with_user(r.tech_user).action_raise_dispute("two jobs missing")
    line.dispute_ids.with_user(r.officer).action_uphold("confirmed: recompute")
    run.sudo()._guarded().write({"dispute_deadline": fields.Date.today() - timedelta(days=1)})
    assert "recompute" in refused(r.env, lambda: run.with_user(r.officer).action_request_approval())
    run.with_user(r.officer).action_reset_draft()
    run.with_user(r.officer).action_compute()
    run.sudo()._guarded().write({"dispute_deadline": fields.Date.today() - timedelta(days=1)})
    _approve_run(r, run)


# ====================================================== clawback (BRU-PIC-11)
def _orders(x, technician, done):
    """Four delivered orders of `technician` completed at `done`."""
    env = x.env
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "A9R2E%d" % n, "legal_name": "A09 r2 entity %d" % n, "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "A09r2 Branch %d" % n,
            "code": "A9R2B%d" % n,
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "A09r2Brand%d" % n, "code": "A9R2D%d" % n})
    cust = env["res.partner"].create({"name": "A09 r2 Customer", "phone": "0171105%04d" % n})
    model = env["fix.device.model"].create(
        {"name": "A09r2 phone %d" % n, "brand_id": brand.id, "device_type": "smartphone"}
    )
    orders = env["fix.service.order"]
    for i in range(4):
        dev = env["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": cust.id,
                "serial_number": "SN-R2-%d-%d" % (n, i),
            }
        )
        orders |= env["fix.service.order"].create(
            {
                "device_id": dev.id,
                "customer_id": cust.id,
                "branch_id": branch.id,
                "fault_description": "a09 r2 clawback",
                "service_type": "walk_in",
            }
        )
    orders.flush_recordset()
    # delivered inside their SLA: first-time fix and SLA 1.0 -> score 0.765,
    # the 8 % band (1,600 on a 20,000 base)
    env.cr.execute(
        "UPDATE fix_service_order SET state='delivered', technician_id=%s, delivered_at=%s, "
        "sla_resolution_deadline=%s, sla_resolution_at=%s, company_id=%s WHERE id IN %s",
        (
            technician.id,
            done,
            done + timedelta(days=1),
            done,
            env.company.id,
            tuple(orders.ids),
        ),
    )
    orders.invalidate_recordset()
    return orders, (branch, dev, cust)


def _computed_card(x, employee, period):
    card = (
        x.env["fix.performance.scorecard"]
        .with_user(x.officer)
        .create({"employee_id": employee.id, "period": period})
    )
    card.with_user(x.officer).action_compute_from_orders()
    card.with_user(x.officer).action_publish()
    return card


def _rework(x, original, when, world):
    branch, dev, cust = world
    rework = x.env["fix.service.order"].create(
        {
            "device_id": dev.id,
            "customer_id": cust.id,
            "branch_id": branch.id,
            "fault_description": "came back",
            "service_type": "walk_in",
        }
    )
    rework.flush_recordset()
    x.env.cr.execute(
        "UPDATE fix_service_order SET rework_of_id=%s, is_rework=true, create_date=%s WHERE id=%s",
        (original.id, when, rework.id),
    )
    rework.invalidate_recordset()
    return rework


def _clawback_world(r, days):
    r.env["ir.config_parameter"].sudo().set_param(CLAWBACK_DAYS, str(days))
    _version(r)
    done = fields.Datetime.to_datetime("2031-04-10 10:00:00")
    orders, world = _orders(r, r.e_tech, done)
    card = _computed_card(r, r.e_tech, PREV)
    r.env.cr.execute(
        "UPDATE fix_performance_scorecard SET computed_at=%s WHERE id=%s",
        (fields.Datetime.to_datetime("2031-04-30 18:00:00"), card.id),
    )
    card.invalidate_recordset()
    april = _run(r, PREV)
    april.with_user(r.officer).action_compute()
    _approve_run(r, april)
    return orders, world, april


def test_a_rework_inside_the_window_is_clawed_back_from_the_next_run(r):
    orders, world, april = _clawback_world(r, days=30)
    paid = _line(april, r.e_tech).amount
    assert paid > 0
    _rework(r, orders[2], fields.Datetime.to_datetime("2031-05-05 09:00:00"), world)
    _card(r, r.e_tech)  # May: top band, 3,000
    may = _run(r)
    may.with_user(r.officer).action_compute()
    cb = (
        r.env["fix.incentive.clawback"]
        .sudo()
        .search([("source_line_id", "=", _line(april, r.e_tech).id)])
    )
    assert len(cb) == 1 and cb.service_order_id == orders[2] and cb.trigger == "rework"
    assert cb.amount == round(paid / 4, 2)
    recovery = may.line_ids.filtered(lambda line: line.line_type == "clawback")
    assert recovery.amount == -cb.amount and recovery.clawback_id == cb
    assert cb.state == "recovered"
    # recomputing does not claw the same order back twice
    may.with_user(r.officer).action_reset_draft()
    assert cb.state == "open"
    may.with_user(r.officer).action_compute()
    assert (
        r.env["fix.incentive.clawback"]
        .sudo()
        .search_count([("source_line_id", "=", _line(april, r.e_tech).id)])
        == 1
    )
    assert len(may.line_ids.filtered(lambda line: line.line_type == "clawback")) == 1


def test_a_rework_after_the_window_or_with_no_window_is_not_clawed_back(r):
    orders, world, _april = _clawback_world(r, days=10)
    _rework(r, orders[1], fields.Datetime.to_datetime("2031-05-05 09:00:00"), world)  # day 25
    _card(r, r.e_tech)
    may = _run(r)
    may.with_user(r.officer).action_compute()
    assert not may.line_ids.filtered(lambda line: line.line_type == "clawback")
    assert not r.env["fix.incentive.clawback"].sudo().search([("employee_id", "=", r.e_tech.id)])


def test_a_clawback_never_exceeds_what_the_run_pays(r):
    orders, world, _april = _clawback_world(r, days=30)
    for order in orders:
        _rework(r, order, fields.Datetime.to_datetime("2031-05-05 09:00:00"), world)
    _card(r, r.e_tech, kpi=0.65)  # May: 4 % band, 800 < the 1,600 to claw back
    may = _run(r)
    may.with_user(r.officer).action_compute()
    earned = _line(may, r.e_tech).amount
    recovered = -sum(
        may.line_ids.filtered(lambda line: line.line_type == "clawback").mapped("amount")
    )
    assert round(recovered, 2) == round(earned, 2)
    assert (
        sum(may.line_ids.filtered(lambda line: line.employee_id == r.e_tech).mapped("amount")) == 0
    )
    open_cb = (
        r.env["fix.incentive.clawback"]
        .sudo()
        .search([("employee_id", "=", r.e_tech.id), ("state", "=", "open")])
    )
    assert open_cb, "the rest must stay open for the next run"


def test_clawbacks_are_not_typed(r):
    orders, _world, april = _clawback_world(r, days=30)
    assert refused(
        r.env,
        lambda: (
            r.env["fix.incentive.clawback"]
            .with_user(r.officer)
            .create(
                {
                    "employee_id": r.e_tech.id,
                    "source_line_id": _line(april, r.e_tech).id,
                    "service_order_id": orders[0].id,
                    "trigger": "rework",
                    "amount": 1,
                }
            )
        ),
    )


# ====================================================== calibration request / recall
def _review_in_manager_review(r):
    rev = r.env["fix.performance.review"].create({"employee_id": r.e_tech.id, "period": PERIOD})
    rev.sudo()._guarded().write({"state": "manager_review"})
    rev.with_user(r.mgr_user).action_record_manager_rating(4)
    return rev


def test_the_line_manager_requests_calibration_in_their_own_name(r):
    rev = _review_in_manager_review(r)
    colleague = _user(r.env)
    assert refused(r.env, lambda: rev.with_user(colleague).action_request_calibration())
    assert refused(r.env, lambda: rev.with_user(r.calibrator).action_request_calibration())
    rev.with_user(r.mgr_user).action_request_calibration()
    req = rev.sudo().approval_request_id
    assert rev.approval_state == "pending" and req.requested_by_id == r.mgr_user
    assert rev.manager_rated_by_id == r.mgr_user
    assert not _task_for(rev, r.mgr_user) and _task_for(rev, r.calibrator)
    # still no write access for a line manager (RAP X-02)
    assert refused(
        r.env, lambda: _rpc(r.env, r.mgr_user, rev._name, "write", rev, {"approval_state": "none"})
    )


def test_the_line_manager_recalls_calibration_and_re_rates(r):
    rev = _review_in_manager_review(r)
    rev.with_user(r.mgr_user).action_request_calibration()
    assert refused(r.env, lambda: rev.with_user(r.calibrator).action_recall_calibration())
    assert refused(r.env, lambda: rev.with_user(r.plain).action_recall_calibration())
    rev.with_user(r.mgr_user).action_recall_calibration()
    assert rev.approval_state == "none"
    assert rev.sudo().approval_request_id.state == "recalled"
    rev.with_user(r.mgr_user).action_record_manager_rating(3)
    rev.with_user(r.mgr_user).action_request_calibration()
    _task_for(rev, r.calibrator).with_user(r.calibrator).action_approve()
    assert rev.state == "calibrated" and rev.calibrated_rating == 3


def test_workspace_recall_through_the_action_endpoint(r, call):
    rev = _review_in_manager_review(r)
    out = call(
        r.env(user=r.mgr_user.id),
        "model_action",
        model="fix.performance.review",
        ids=[rev.id],
        method="action_request_calibration",
    )
    assert out.get("success"), out
    out = call(
        r.env(user=r.mgr_user.id),
        "model_action",
        model="fix.performance.review",
        ids=[rev.id],
        method="action_recall_calibration",
    )
    assert out.get("success"), out
    assert rev.approval_state == "none"


# ====================================================== compensation proposals (BRU-PIC-17)
def _comp_world(r, basic=25000.0):
    r.env["fix.compensation.band"].create(
        {
            "name": "A09 r2 band",
            "grade": "A9R2G",
            "range_min": 20000,
            "range_mid": 30000,
            "range_max": 40000,
        }
    )
    pos = r.env["fix.org.position"].create({"name": "A09 r2 Technician", "grade": "A9R2G"})
    r.e_tech.position_id = pos
    contract = r.env["fix.employment.contract"].create(
        {
            "employee_id": r.e_tech.id,
            "contract_type": "permanent",
            "joining_date": fields.Date.today() - timedelta(days=400),
            "weekly_hours": 48,
            "basic_monthly": basic,
        }
    )
    contract.write({"state": "active"})
    rev = r.env["fix.performance.review"].create({"employee_id": r.e_tech.id, "period": PERIOD})
    rev.sudo()._guarded().write({"state": "closed", "calibrated_rating": 4})
    return contract, rev


def test_only_the_line_manager_proposes_from_a_closed_review(r):
    contract, rev = _comp_world(r)
    for user in (r.plain, r.calibrator, r.comp, r.tech_user):
        assert refused(
            r.env,
            lambda u=user: rev.with_user(u).action_propose_compensation(proposal="32000 good year"),
        )
    assert refused(
        r.env,
        lambda: (
            r.env["fix.compensation.proposal"]
            .with_user(r.comp)
            .create(
                {
                    "employee_id": r.e_tech.id,
                    "contract_id": contract.id,
                    "effective_date": fields.Date.today(),
                    "justification": "typed",
                }
            )
        ),
    )
    out = rev.with_user(r.mgr_user).action_propose_compensation(proposal="32000 a strong year")
    prop = r.env["fix.compensation.proposal"].browse(out["proposal_id"])
    assert prop.state == "submitted" and prop.proposed_by_id == r.mgr_user
    assert prop.sudo().proposed_basic == 32000.0 and prop.sudo().current_basic == 25000.0
    # one open proposal per employee
    assert refused(
        r.env, lambda: rev.with_user(r.mgr_user).action_propose_compensation(proposal="33000 again")
    )


def test_a_proposal_outside_the_band_is_refused(r):
    _contract, rev = _comp_world(r)
    err = refused(
        r.env, lambda: rev.with_user(r.mgr_user).action_propose_compensation(proposal="90000 x")
    )
    assert err and "outside" in err


def test_calibration_then_the_compensation_manager_applies_a_new_version(r):
    contract, rev = _comp_world(r)
    prop = r.env["fix.compensation.proposal"].browse(
        rev.with_user(r.mgr_user).action_propose_compensation(proposal="32000 a strong year")[
            "proposal_id"
        ]
    )
    assert refused(r.env, lambda: prop.with_user(r.mgr_user).action_calibration_review("ok"))
    assert refused(r.env, lambda: prop.with_user(r.comp).action_approve())
    prop.with_user(r.calibrator).action_calibration_review("31000 aligned with peers")
    assert prop.state == "calibrated" and prop.approval_state == "pending"
    assert prop.sudo().proposed_basic == 31000.0
    for user in (r.mgr_user, r.calibrator):
        assert not _task_for(prop, user)
    assert refused(r.env, lambda: prop.with_user(r.comp).action_approve())  # not from the inbox
    _task_for(prop, r.comp).with_user(r.comp).action_approve()
    assert prop.state == "approved" and prop.approved_by_id == r.comp
    version = prop.new_contract_id
    assert version.state == "draft" and version.previous_contract_id == contract
    assert version.basic_monthly == 31000.0
    assert contract.state == "active" and contract.basic_monthly == 25000.0


def test_the_pinned_figure_is_not_typed_and_a_changed_contract_voids_it(r):
    contract, rev = _comp_world(r)
    prop = r.env["fix.compensation.proposal"].browse(
        rev.with_user(r.mgr_user).action_propose_compensation(proposal="32000 a strong year")[
            "proposal_id"
        ]
    )
    for user in (r.comp, r.calibrator):
        assert refused(
            r.env,
            lambda u=user: _rpc(r.env, u, prop._name, "write", prop, {"proposed_basic": 39000}),
        )
    prop.with_user(r.calibrator).action_calibration_review("confirmed")
    contract.sudo().write({"basic_monthly": 26000.0})  # changed behind the proposal
    err = refused(r.env, lambda: _task_for(prop, r.comp).with_user(r.comp).action_approve())
    assert err and "changed" in err


def test_the_proposer_withdraws_and_nobody_else_does(r):
    _contract, rev = _comp_world(r)
    prop = r.env["fix.compensation.proposal"].browse(
        rev.with_user(r.mgr_user).action_propose_compensation(proposal="32000 a strong year")[
            "proposal_id"
        ]
    )
    assert refused(r.env, lambda: prop.with_user(r.calibrator).action_withdraw())
    prop.with_user(r.mgr_user).action_withdraw()
    assert prop.state == "withdrawn"


# ====================================================== deployment
def test_round2_groups_hold_only_root_and_admin(odoo_env):
    admin_root = odoo_env.ref("base.user_admin") | odoo_env.ref("base.user_root")
    for xmlid in (HRD, CFO):
        group = odoo_env.ref(xmlid)
        assert odoo_env.ref("base.group_user") in group.implied_ids
        assert group.user_ids <= admin_root, xmlid


def test_round2_settings_are_seeded_off(odoo_env):
    get = odoo_env["ir.config_parameter"].sudo().get_param
    assert get(DISPUTE_DAYS) == "0" and get(CLAWBACK_DAYS) == "0"


def test_round2_access_rows_exist_and_none_lets_a_plain_user_write(odoo_env):
    Access = odoo_env["ir.model.access"].sudo()
    for model, group in (
        ("fix.incentive.scheme.version", OFFICER),
        ("fix.incentive.scheme.version", HRD),
        ("fix.incentive.scheme.version", CFO),
        ("fix.incentive.dispute", OFFICER),
        ("fix.compensation.proposal", CALIBRATOR),
        ("fix.compensation.proposal", COMPENSATION),
    ):
        assert Access.search_count(
            [("model_id.model", "=", model), ("group_id", "=", odoo_env.ref(group).id)]
        ), (model, group)
    plain = Access.search(
        [
            ("group_id", "=", odoo_env.ref("base.group_user").id),
            (
                "model_id.model",
                "in",
                [
                    "fix.incentive.scheme",
                    "fix.incentive.scheme.version",
                    "fix.incentive.dispute",
                    "fix.incentive.clawback",
                    "fix.compensation.proposal",
                ],
            ),
        ]
    )
    assert not any(plain.mapped("perm_write") + plain.mapped("perm_create"))


def test_round2_workspace_surfaces_and_actions(odoo_env):
    s = a09.SURFACES
    assert {
        "action_request_calibration",
        "action_recall_calibration",
        "action_propose_compensation",
    } <= s["fix.performance.review"]["actions"]
    assert {"action_raise_dispute"} <= s["fix.incentive.line"]["actions"]
    assert {"action_request_approval", "action_recall_approval"} <= s[
        "fix.incentive.scheme.version"
    ]["actions"]
    assert "action_approve" not in s["fix.incentive.scheme.version"]["actions"]
    assert {"action_uphold", "action_reject"} <= s["fix.incentive.dispute"]["actions"]
    assert {"action_calibration_review", "action_withdraw"} <= s["fix.compensation.proposal"][
        "actions"
    ]
    assert "action_approve" not in s["fix.compensation.proposal"]["actions"]
    for model in ("fix.incentive.scheme", "fix.incentive.clawback"):
        assert model in s
    # nothing a decision sets is offered as editable
    assert not s["fix.compensation.proposal"]["writable"]
    assert not s["fix.incentive.dispute"]["writable"]
    assert "state" not in s["fix.incentive.scheme.version"]["writable"]
