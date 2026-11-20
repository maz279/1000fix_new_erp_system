"""A02 ERP audit (19 Nov 2026) - M31 Workshop & Depot Repair, findings
M31-F12..F19 and the M31 side of F20/F21.

Run as the non-admin workshop users of the A02 P0 fixture (``m31``); the
superuser is used for setup only. ``odoo_env`` rolls back after every test.
"""

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError

from . import test_a02_p0_m31 as a02
from ._m45_decided import calibrations_decided  # noqa: F401 - autouse fixture
from .test_a06_m15_workshop_issue import _m15
from .test_a07_p0_m45_qc import _meter

m31 = a02.m31
refused, _to_repair, _approved_estimate, _line, _qc_ready = (
    a02.refused,
    a02._to_repair,
    a02._approved_estimate,
    a02._line,
    a02._qc_ready,
)
GUARD = a02.GUARD
CAP = "cd_workshop.zero_charge_parts_cap_bdt"


def _in_repair(m, amount=30000.0, **vals):
    so = m.order()
    _approved_estimate(m, so, amount)
    return _to_repair(m, m.job(so=so, **vals))


# ============================================================ F12 fitted parts only
def test_f12_only_fitted_parts_cost_the_job(m31):
    job = _in_repair(m31)
    fitted = _line(m31, job, qty=1.0, cost=500.0)
    _line(m31, job, qty=4.0, cost=500.0)  # drafted, never fitted
    reserved = _line(m31, job, qty=2.0, cost=500.0)
    reserved.action_reserve()
    fitted.action_consume_part()
    job.invalidate_recordset()
    assert job.parts_total == 500.0
    assert job.total_repair_cost == 500.0 + job.labour_cost
    job.action_build_cost_sheet()
    parts = job.cost_line_ids.filtered(lambda c: c.cost_type == "parts")
    assert parts.amount == 500.0


# ============================================================ F13 unit cost
def test_f13_the_unit_cost_is_not_typed(m31):
    job = _in_repair(m31)
    Line = m31.env["fix.workshop.part.line"].with_user(m31.tech)
    with refused(m31.env, UserError, GUARD):
        Line.create({"job_id": job.id, "product_id": m31.product.id, "unit_cost": 1.0})
    # the backend onchange echoes the standard cost: accepted
    line = Line.create({"job_id": job.id, "product_id": m31.product.id, "unit_cost": 500.0})
    assert line.unit_cost == 500.0
    with refused(m31.env, UserError, GUARD):
        line.write({"unit_cost": 1.0})
    # a part swapped on an open line takes the new part's standard cost
    dear = m31.env["product.product"].create({"name": "F13 dear part", "standard_price": 900.0})
    line.write({"product_id": dear.id})
    assert line.unit_cost == 900.0


def test_f13_the_ceiling_is_judged_at_the_m15_issue_cost(m31):
    _m15(m31, qty=5.0, cost=650.0)  # M15 average cost 650, standard cost 500
    job = _in_repair(m31, amount=560.0)  # 500 fits under it, 650 does not
    line = _line(m31, job)
    assert line.unit_cost == 500.0
    # at 500 the part fits the 600 approved; at the 650 it is issued at, not
    with refused(m31.env, UserError, "BRU-WSR-11"):
        line.action_consume_part()
    assert line.reservation_state == "draft"
    # the estimate is revised and re-approved: the latest approved version governs
    _approved_estimate(m31, job.order_id, 5000.0)
    line.action_consume_part()
    assert line.unit_cost == 650.0 and line.m15_consumption_id
    job.invalidate_recordset()
    assert job.parts_total == 650.0


# ============================================================ F14 labour
def _clock(m, job, minutes):
    log = m.env["fix.workshop.time.log"].with_user(m.tech).create({"job_id": job.id})
    log.sudo()._guarded().write({"started_at": fields.Datetime.now() - timedelta(minutes=minutes)})
    log.with_user(m.tech).action_stop()
    return log


def test_f14_labour_is_the_clock_at_the_rate_and_not_typed(m31):
    m31.workshop.labour_rate_per_hour = 600.0
    job = _in_repair(m31)
    with refused(m31.env, UserError, GUARD):
        job.with_user(m31.tech).write({"labour_total": 1.0})
    _clock(m31, job, 30)
    job.invalidate_recordset()
    assert abs(job.labour_cost - 300.0) < 1.0
    assert abs(job.total_repair_cost - job.labour_cost) < 0.01
    # with a rate the clock is the record: no figure is recorded
    with refused(m31.env, UserError, "book the time"):
        job.with_user(m31.supv).action_record_labour(amount=10)


def test_f14_the_figure_is_a_supervisors_where_no_rate_is_set(m31):
    m31.workshop.labour_rate_per_hour = 0.0
    job = _in_repair(m31)
    with refused(m31.env, UserError, "role"):
        job.with_user(m31.tech).action_record_labour(amount=10)
    job.with_user(m31.supv).action_record_labour(amount=1200)
    assert job.labour_total == 1200.0 and job.labour_cost == 1200.0


def test_f14_clocked_labour_and_consumables_hit_the_cost_gate(m31):
    m31.workshop.labour_rate_per_hour = 600.0
    job = _in_repair(m31, amount=500.0)
    _clock(m31, job, 30)  # ~300
    flux = m31.env["product.product"].create({"name": "F14 flux", "standard_price": 200.0})
    m31.env["fix.workshop.consumable.usage"].with_user(m31.tech).create(
        {"job_id": job.id, "product_id": flux.id, "quantity": 2.0}
    )
    job.invalidate_recordset()
    assert job.total_repair_cost > 690.0
    # parts 0 + labour ~300 + consumables 400 > 500 approved: no QC
    with refused(m31.env, UserError, "BRU-WSR-11"):
        job.action_submit_qc()
    assert job.state == "in_repair"


# ============================================================ F15/F16 tests and QC
def _step(m, lower=3.0, upper=4.5):
    proto = m.env["fix.workshop.test.protocol"].create(
        {"code": "F15-%d" % m.workshop.id, "name": "F15 rail check"}
    )
    return m.env["fix.workshop.test.step"].create(
        {
            "protocol_id": proto.id,
            "name": "VBAT",
            "has_limits": True,
            "lower_limit": lower,
            "upper_limit": upper,
        }
    )


def _result(m, job, step, value, **vals):
    return (
        m.env["fix.workshop.test.result"]
        .with_user(m.tech)
        .create({"job_id": job.id, "step_id": step.id, "measured_value": value, **vals})
    )


def test_f15_qc_does_not_pass_a_failed_test_and_results_are_kept(m31):
    job = m31.job()
    _qc_ready(m31, job)
    step = _step(m31)
    bad = _result(m31, job, step, 5.2)
    assert not bad.passed and job.test_failed_count == 1
    with refused(m31.env, UserError, "1 test\\(s\\) failed"):
        job.with_user(m31.qc).action_pass_qc(notes="looks fine")
    # the failed reading is evidence: not rewritten, not deleted
    with refused(m31.env, UserError, "not edited"):
        bad.with_user(m31.tech).write({"measured_value": 4.0})
    with refused(m31.env, UserError, "never deleted"):
        bad.with_user(m31.supv).unlink()
    # a re-test is a new result; the latest result of the test is what counts
    _result(m31, job, step, 4.0)
    job.invalidate_recordset()
    assert job.test_failed_count == 0 and len(job.test_result_ids) == 2
    job.with_user(m31.qc).action_pass_qc(notes="re-tested in limits")
    assert job.state == "ready"


def test_f16_a_measurement_needs_a_fit_instrument(m31):
    job = _in_repair(m31)
    step = _step(m31)
    never = _meter(m31, "F16-NEVER", result=None)
    with refused(m31.env, UserError, "never been calibrated"):
        _result(m31, job, step, 4.0, equipment_id=never.id)
    good = _meter(m31, "F16-OK")
    res = _result(m31, job, step, 4.0, equipment_id=good.id)
    assert res.passed and res.equipment_id == good


# ============================================================ F17 transfer
def _transfer(m, job):
    dst = m.env["fix.workshop"].create(
        {"code": "WS-F17-%d" % job.id, "name": "F17 Depot", "name_bn": "ডিপো"}
    )
    # A02 pass 2 M31-12: the supervisor confirms for HIS workshop
    dst.sudo().write({"supervisor_user_ids": [(4, m.supv.id)]})
    t = (
        m.env["fix.workshop.transfer"]
        .with_user(m.tech)
        .create({"job_id": job.id, "to_workshop_id": dst.id, "reason": "BGA reballing"})
    )
    t.with_user(m.supv).action_confirm()
    return t, dst


def test_f17_a_transfer_is_received_only_on_its_delivered_consignment(m31):
    job = m31.job()
    job.action_intake()
    src = job.workshop_id
    t, dst = _transfer(m31, job)
    cons = t.consignment_id.sudo()
    assert t.state == "in_transit" and cons.state == "draft" and job.workshop_id == dst
    with refused(m31.env, UserError, "is delivered"):
        t.with_user(m31.supv).action_receive()
    # the move is withdrawn before dispatch: the job is back, the leg is gone
    with refused(m31.env, UserError, "did not arrive"):
        t.with_user(m31.supv).action_cancel()
    t.with_user(m31.supv).action_cancel(note="specialist bench down")
    assert t.state == "cancelled" and not cons.exists()
    assert job.workshop_id == src


def test_f17_a_consignment_on_the_road_blocks_the_close_and_delivery_receives(m31):
    job = m31.job()
    job.action_intake()
    t, dst = _transfer(m31, job)
    cons = t.consignment_id.sudo()
    cons.write({"state": "in_transit"})  # setup: the leg is on the road
    with refused(m31.env, UserError, "on its way"):
        t.with_user(m31.supv).action_cancel(note="lost?")
    cons.write({"state": "delivered"})  # setup: delivered at the receiving hub
    t.with_user(m31.supv).action_receive()
    assert t.state == "received" and job.workshop_id == dst


def test_f17_a_transfer_leg_respects_one_live_leg(m31):
    job = m31.job()
    job.action_intake()
    m31.env["fix.consignment"].create(
        {
            "consignment_type": "delivery",
            "scheduled_date": fields.Datetime.now(),
            "service_order_id": job.order_id.id,
            "operating_unit_id": m31.env["operating.unit"].search([], limit=1).id,
            "declared_value_bdt": 100.0,
        }
    )
    dst = m31.env["fix.workshop"].create({"code": "WS-F17B", "name": "F17B", "name_bn": "ডি"})
    dst.sudo().write({"supervisor_user_ids": [(4, m31.supv.id)]})
    t = (
        m31.env["fix.workshop.transfer"]
        .with_user(m31.tech)
        .create({"job_id": job.id, "to_workshop_id": dst.id, "reason": "L3 board"})
    )
    with refused(m31.env, UserError, "one leg at a time"):
        t.with_user(m31.supv).action_confirm()
    assert t.state == "requested"


# ============================================================ F18 bench capacity
def test_f18_a_job_that_failed_qc_keeps_its_bench(m31):
    bench = m31.env["fix.workshop.bench"].create(
        {
            "workshop_id": m31.workshop.id,
            "code": "B-F18-%d" % m31.workshop.id,
            "name": "F18",
            "name_bn": "এফ",
            "max_concurrent_jobs": 1,
        }
    )
    first = m31.job()
    _to_repair(m31, first, bench=bench)
    first.action_submit_qc()
    first.with_user(m31.qc).action_fail_qc(reason="charging port loose")
    assert first.state == "qc_failed" and first.bench_id == bench
    second = m31.job()
    second.action_intake()
    with refused(m31.env, UserError, "is full"):
        second.action_allocate_bench(bench_id=bench.id)
    # the rework goes back on its own bench
    first.action_start_repair()
    assert first.state == "in_repair" and first.bench_id == bench


# ============================================================ F19 burn-in edge
def test_f19_burn_in_does_not_fail_into_qc_failed(m31):
    job = m31.job(level="l2")
    m31.env.cr.execute("UPDATE fix_workshop_job SET state='burn_in' WHERE id=%s", (job.id,))
    job.invalidate_recordset(["state"])
    with refused(m31.env, UserError, "Invalid job state transition"):
        job._validate_transition("qc_failed")
    job._validate_transition("in_repair")


# ============================================================ F20/F21 KPIs and reports
def _closed(m, state="delivered", **vals):
    job = m.job()
    m.env.cr.execute("UPDATE fix_workshop_job SET state=%s WHERE id=%s", (state, job.id))
    job.invalidate_recordset(["state"])
    if vals:
        job.sudo()._guarded().write(vals)
    return job


def test_f20_first_pass_yield_counts_burn_in_failures(m31):
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as p03

    elsewhere = m31.env["res.company"].create({"name": "A02 F20 M31 Elsewhere"})
    m31.env.cr.execute(
        "UPDATE fix_workshop_job SET company_id = %s WHERE state = 'delivered'", (elsewhere.id,)
    )
    m31.env.invalidate_all()
    clean = _closed(m31)
    burnt = _closed(m31)
    m31.env["fix.workshop.rework"].sudo().create(
        {"job_id": burnt.id, "iteration": 1, "failed_at_state": "burn_in", "reason": "crash"}
    )
    assert clean.state == "delivered"
    assert p03.kpis(m31.env)["first_pass_yield"] == 50.0


def test_f20_the_burn_in_report_counts_failed_runs(m31):
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as p03

    started = fields.Datetime.now() - timedelta(hours=6)
    m31.env.cr.execute("UPDATE fix_workshop_job SET burn_in_started_at = NULL")
    m31.env.invalidate_all()
    _closed(m31, "qc_pending", burn_in_started_at=started, burn_in_passed=True)
    _closed(m31, "burn_in", burn_in_started_at=started)  # still running
    failed = _closed(m31, "in_repair", burn_in_started_at=started)
    for i in (1, 2):
        m31.env["fix.workshop.rework"].sudo().create(
            {"job_id": failed.id, "iteration": i, "failed_at_state": "burn_in"}
        )
    rows = {r["measure"]: r["value"] for r in p03.REPORTS["burn_in"](m31.env)["rows"]}
    assert rows["Jobs burn-in tested"] == 3
    assert rows["Still running"] == 1
    assert rows["Failed runs (back to the bench)"] == 2
    assert rows["Pass rate % (passed / passed + failed runs)"] == round(100.0 / 3, 1)


def test_f21_reports_stay_in_the_callers_companies(m31):
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as p03

    job = _closed(
        m31, completed_at=fields.Datetime.now(), is_rework=True, rework_reason="F21 probe"
    )
    line = m31.env["fix.workshop.part.line"].create(
        {"job_id": job.id, "product_id": m31.product.id, "lot_serial_number": "F21-SER"}
    )
    other = m31.env["res.company"].create({"name": "A02 F21 M31 Other"})
    theirs = m31.env(context=dict(m31.env.context, allowed_company_ids=[other.id]))

    def text(env, report):
        return " ".join(str(v) for r in p03.REPORTS[report](env)["rows"] for v in r.values())

    assert "F21 probe" in text(m31.env, "rework_loops")
    assert "F21 probe" not in text(theirs, "rework_loops")
    assert line.lot_serial_number in text(m31.env, "parts_genealogy")
    assert line.lot_serial_number not in text(theirs, "parts_genealogy")
    assert m31.workshop.name in text(m31.env, "bench_utilisation")
    assert m31.workshop.name not in text(theirs, "bench_utilisation")
    cycle = {r["level"]: r["delivered"] for r in p03.REPORTS["cycle_time"](theirs)["rows"]}
    assert cycle["L1"] == 0
    assert p03.kpis(theirs)["parts_fitment"] is None
