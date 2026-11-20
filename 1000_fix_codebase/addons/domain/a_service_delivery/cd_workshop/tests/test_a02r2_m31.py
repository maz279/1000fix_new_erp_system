"""A02 ERP audit pass 2 (20 Nov 2026) - M31 Workshop & Depot Repair,
findings M31-01..M31-09 and M31-12 (the reports and job card are tested in
cd_p03_portal).

Every control runs as a non-admin workshop user of the A02 P0 fixture
(``m31``); the superuser is used for setup only. ``odoo_env`` rolls back.
"""

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError

from . import test_a02_p0_m31 as a02
from ._m45_decided import calibrations_decided  # noqa: F401 - autouse fixture
from .test_a02_p1p2_cd_workshop import _events

m31 = a02.m31
refused, _to_repair, _approved_estimate, _line, _qc_ready, _evidence, _as, _user = (
    a02.refused,
    a02._to_repair,
    a02._approved_estimate,
    a02._line,
    a02._qc_ready,
    a02._evidence,
    a02._as,
    a02._user,
)
GUARD = a02.GUARD


def _in_repair(m, amount=30000.0, **vals):
    so = m.order()
    _approved_estimate(m, so, amount)
    return _to_repair(m, m.job(so=so, **vals))


def _clock(m, job, minutes, user=None):
    user = user or m.tech
    log = m.env["fix.workshop.time.log"].with_user(user).create({"job_id": job.id})
    log.sudo()._guarded().write({"started_at": fields.Datetime.now() - timedelta(minutes=minutes)})
    log.with_user(user).action_stop()
    return log


def _waived(m, job):
    """Test setup only: the M22 certification waiver a supervisor grants from
    his inbox (its routing is tested in the P0 suite)."""
    job.sudo()._guarded().write(
        {"certification_waiver": True, "certification_waiver_technician_id": m.tech_emp.id}
    )
    return job


def _ready(m, job):
    _qc_ready(m, job)
    _as(m, m.qc, job).action_pass_qc("ok")
    assert job.sudo().state == "ready"
    return job


# ============================================================ M31-01
def test_m31_01_level_and_technician_are_fixed_waiting_for_parts(m31):
    job = _in_repair(m31)
    job.action_wait_parts()
    with refused(m31.env, UserError, "fixed once the job is under way"):
        job.write({"repair_level": "l2"})
    with refused(m31.env, UserError, "fixed once the job is under way"):
        job.write({"technician_id": m31.tech2_emp.id})
    # the bench cannot hand it over itself; a supervisor can, with the note
    with refused(m31.env, UserError, "under way"):
        job.action_allocate_bench(bench_id=m31.l1.id, technician_id=m31.tech2_emp.id, note="x")
    with refused(m31.env, UserError, "note"):
        _as(m31, m31.supv, job).action_allocate_bench(
            bench_id=m31.l1.id, technician_id=m31.tech2_emp.id
        )
    _as(m31, m31.supv, job).action_allocate_bench(
        bench_id=m31.l1.id, technician_id=m31.tech2_emp.id, note="tech off sick"
    )
    assert job.sudo().technician_id == m31.tech2_emp


def test_m31_01_a_supervisor_revises_the_level_and_it_never_drops(m31):
    job = _in_repair(m31)
    job.action_wait_parts()
    with refused(m31.env, UserError, "role"):
        job.action_revise_level("l2", "needs soldering")
    with refused(m31.env, UserError, "why"):
        _as(m31, m31.supv, job).action_revise_level("l2", "")
    # the L1 bench cannot take an L2 job: the revision checks the bench fit
    with refused(m31.env, UserError, "L1 only"):
        _as(m31, m31.supv, job).action_revise_level("l2", "needs soldering")
    _as(m31, m31.supv, job).action_allocate_bench(bench_id=m31.l2.id, note="to the L2 bench")
    _waived(m31, job)
    _as(m31, m31.supv, job).action_revise_level("l2", "needs soldering")
    assert job.sudo().repair_level == "l2"
    events = _events(m31.env, job, "workshop.job.level_revised")
    assert events and events[-1]["new_level"] == "l2"
    # the repair started as L1 and went up: it never comes back down
    with refused(m31.env, UserError, "does not drop"):
        _as(m31, m31.supv, job).action_revise_level("l1", "cheaper")
    assert job.sudo().repair_level == "l2"


def test_m31_01_qc_independence_covers_everyone_who_booked_time(m31):
    env = m31.env
    hybrid, _emp = _user(
        env,
        "qctech",
        [
            env.ref("cd_workshop.group_fix_workshop_qc_inspector"),
            env.ref("cd_workshop.group_fix_workshop_user"),
        ],
    )
    job = _in_repair(m31)
    _clock(m31, job, 20, user=hybrid)
    a02._protocol_passed(m31, job)
    job.action_submit_qc()
    _evidence(m31, job, "post_repair_photo", "test_log")
    with refused(env, ValidationError, "BRU-SRM-18"):
        _as(m31, hybrid, job).action_pass_qc("my own work")
    _as(m31, m31.qc, job).action_pass_qc("independent")
    assert job.sudo().state == "ready"


# ============================================================ M31-02
def test_m31_02_the_bench_releases_and_m01_delivery_closes_the_job(m31):
    so = m31.order()
    est = _approved_estimate(m31, so, 3000.0)
    job = _ready(m31, m31.job(so=so))
    # the bench no longer hands the device to the customer
    with refused(m31.env, UserError, "front desk"):
        job.action_deliver()
    job.action_release()
    assert (job.sudo().state, so.state) == ("released", "ready")
    assert job.released_by_id == m31.tech and job.released_at
    payloads = _events(m31.env, job, "workshop.job.delivered")
    assert len(payloads) == 1 and payloads[0]["service_order_id"] == so.id
    # M01 hands the device over; its delivered event closes the job
    a02._handover_ready(m31, so)
    so.sudo().write(
        {"payment_settlement_state": "settled", "amount_settled_bdt": est.grand_total,
         "settlement_verified": True}
    )  # fmt: skip
    so.sudo().action_deliver()
    res = (
        m31.env["fix.workshop.job"]
        .sudo()
        .consume_service_order_delivered({"payload": {"order_id": so.id}})
    )
    assert res["closed"] == [job.id] and job.sudo().state == "delivered"
    # idempotent
    assert (
        not m31.env["fix.workshop.job"]
        .sudo()
        .consume_service_order_delivered({"payload": {"order_id": so.id}})["closed"]
    )
    # relay only
    with refused(m31.env, UserError, "relay"):
        m31.env["fix.workshop.job"].with_user(m31.tech).consume_service_order_delivered(
            {"payload": {"order_id": so.id}}
        )


def test_m31_02_the_consumer_is_registered(m31):
    consumer = m31.env.ref("cd_workshop.consumer_service_order_delivered_workshop_job")
    assert (consumer.event_type, consumer.method) == (
        "service_order.delivered",
        "consume_service_order_delivered",
    )


# ============================================================ M31-03
def test_m31_03_a_job_names_its_order_and_keeps_it(m31):
    Job = m31.env["fix.workshop.job"].with_user(m31.tech)
    with refused(m31.env, UserError, "service order"):
        Job.create(
            {
                "workshop_id": m31.workshop.id,
                "fault_description": "no origin",
                "bookin_condition": "ok",
                "bookin_no_accessories": True,
            }
        )
    job = m31.job()
    with refused(m31.env, UserError, "never cleared"):
        job.write({"order_id": False})
    with refused(m31.env, UserError, "never cleared"):
        job.write({"order_id": m31.order().id})
    # a job raised by system code with no origin is not booked in
    orphan = m31.env["fix.workshop.job"].create(
        {
            "workshop_id": m31.workshop.id,
            "fault_description": "orphan",
            "bookin_condition": "ok",
            "bookin_no_accessories": True,
        }
    )
    with refused(m31.env, UserError, "names no service order"):
        orphan.with_user(m31.tech).action_intake()
    # an M45 work order is an origin
    mreq = m31.env["maintenance.request"].create({"name": "A02R2 calibration rig repair"})
    internal = Job.create(
        {
            "workshop_id": m31.workshop.id,
            "fault_description": "rig",
            "maintenance_request_id": mreq.id,
            "bookin_condition": "ok",
            "bookin_no_accessories": True,
        }
    )
    internal.action_intake()
    assert internal.state == "intake"


# ============================================================ M31-04
def test_m31_04_qc_is_judged_on_the_jobs_protocol(m31):
    job = _in_repair(m31)
    job.action_submit_qc()
    _evidence(m31, job, "post_repair_photo", "test_log")
    with refused(m31.env, UserError, "no test protocol"):
        _as(m31, m31.qc, job).action_pass_qc("looks fine")
    proto = m31.env["fix.workshop.test.protocol"].create(
        {
            "code": "R2-P-%d" % job.id,
            "name": "Two steps",
            "step_ids": [
                (0, 0, {"name": "Boot", "has_limits": False}),
                (0, 0, {"name": "Charge", "has_limits": False}),
            ],
        }
    )
    job.sudo().write({"protocol_id": proto.id})
    m31.env["fix.workshop.test.result"].with_user(m31.tech).create(
        {"job_id": job.id, "step_id": proto.step_ids[0].id, "observed_pass": True}
    )
    with refused(m31.env, UserError, "no result for"):
        _as(m31, m31.qc, job).action_pass_qc("one step")
    # the protocol is fixed once the job is in QC
    with refused(m31.env, UserError, "protocol is fixed"):
        job.write({"protocol_id": False})


def test_m31_04_the_protocol_sets_the_burn_in_even_on_l1(m31):
    job = _in_repair(m31)
    proto = a02._protocol_passed(m31, job, burn_in_minutes=30)
    with refused(m31.env, UserError, "burn-in"):
        job.action_submit_qc()
    job.action_start_burn_in()
    job.sudo()._guarded().write(
        {"burn_in_started_at": fields.Datetime.now() - timedelta(minutes=10)}
    )
    with refused(m31.env, UserError, "30 minutes"):
        job.action_pass_burn_in()
    job.sudo()._guarded().write(
        {"burn_in_started_at": fields.Datetime.now() - timedelta(minutes=31)}
    )
    job.action_pass_burn_in()
    assert job.sudo().state == "qc_pending"
    _evidence(m31, job, "post_repair_photo", "test_log", "burn_in_log")
    # the only result predates the end of the burn-in
    old = job.sudo().test_result_ids
    m31.env.cr.execute(
        "UPDATE fix_workshop_test_result SET tested_at=%s WHERE id IN %s",
        (job.burn_in_completed_at - timedelta(minutes=5), tuple(old.ids)),
    )
    old.invalidate_recordset(["tested_at"])
    with refused(m31.env, UserError, "before the burn-in ended"):
        _as(m31, m31.qc, job).action_pass_qc("x")
    m31.env["fix.workshop.test.result"].with_user(m31.tech).create(
        {"job_id": job.id, "step_id": proto.step_ids.id, "observed_pass": True}
    )
    _as(m31, m31.qc, job).action_pass_qc("re-tested after burn-in")
    assert job.sudo().state == "ready"


# ============================================================ M31-05
def test_m31_05_esd_is_todays_dhaka_check_and_l3_needs_a_certified_workshop(m31):
    from odoo.addons.cd_workshop.models.fix_workshop_bench import dhaka_today

    so = m31.order()
    _approved_estimate(m31, so)
    job = _waived(m31, m31.job(level="l2", so=so))
    job.action_intake()
    job.action_diagnostic()
    job.write({"bench_id": m31.l2.id})
    m31.l2.sudo()._guarded().write({"esd_last_verified_date": dhaka_today() - timedelta(days=1)})
    with refused(m31.env, UserError, "today's"):
        job.action_start_repair()
    m31.l2.with_user(m31.tech).action_log_daily_esd(5.0, 50.0)
    assert m31.l2.esd_last_verified_date == dhaka_today()
    job.action_start_repair()
    assert job.sudo().state == "in_repair"
    # L3 work only in an ESD-certified workshop (bench fit and the gate)
    m31.workshop.sudo().write({"is_esd_certified": False})
    l3 = m31.env["fix.workshop.bench"].create(
        {
            "workshop_id": m31.workshop.id,
            "code": "B-R2-L3-%d" % job.id,
            "name": "L3",
            "name_bn": "এল৩",
            "repair_level": "l3",
            "max_concurrent_jobs": 5,
        }
    )
    job3 = m31.job(level="l3")
    assert "ESD-certified" in (job3._m31_bench_fit_error(l3, m31.workshop, "l3") or "")
    m31.workshop.sudo().write({"is_esd_certified": True})
    assert not job3._m31_bench_fit_error(l3, m31.workshop, "l3")


# ============================================================ M31-06
def test_m31_06_the_rate_is_kept_on_the_segment(m31):
    m31.workshop.labour_rate_per_hour = 600.0
    job = _in_repair(m31)
    log = _clock(m31, job, 30)
    assert log.rate_per_hour == 600.0
    job.invalidate_recordset()
    before = job.labour_cost
    m31.workshop.labour_rate_per_hour = 1200.0
    job.invalidate_recordset()
    assert abs(job.labour_cost - before) < 0.01
    with refused(m31.env, UserError, GUARD):
        log.with_user(m31.tech).write({"rate_per_hour": 1.0})


def test_m31_06_clocks_stop_with_the_job_and_a_supervisor_corrects(m31):
    job = _in_repair(m31)
    running = m31.env["fix.workshop.time.log"].with_user(m31.tech).create({"job_id": job.id})
    a02._protocol_passed(m31, job)
    job.action_submit_qc()
    assert not running.running and running.ended_at
    with refused(m31.env, UserError, "no clock starts"):
        m31.env["fix.workshop.time.log"].with_user(m31.tech2).create({"job_id": job.id})
    start = running.started_at - timedelta(minutes=50)
    with refused(m31.env, UserError, "supervisor"):
        running.with_user(m31.tech).action_correct(started_at=start, reason="forgot")
    with refused(m31.env, UserError, "why"):
        running.with_user(m31.supv).action_correct(started_at=start)
    running.with_user(m31.supv).action_correct(started_at=start, reason="clock started late")
    assert running.started_at == start and running.corrected_by_id == m31.supv
    assert "clock started late" in running.correction_note


# ============================================================ M31-07
def test_m31_07_the_cost_gate_is_the_price_without_vat(m31):
    m31.workshop.labour_rate_per_hour = 0.0
    so = m31.order()
    est = _approved_estimate(m31, so, 1000.0)
    est.invalidate_recordset()
    assert est.grand_total > 1000.0  # VAT on top
    job = _to_repair(m31, m31.job(so=so))
    assert abs(job.estimate_ceiling - 1000.0) < 0.01
    job.with_user(m31.supv).action_record_labour(amount=1100)
    a02._protocol_passed(m31, job)
    with refused(m31.env, UserError, "BRU-WSR-11"):
        job.action_submit_qc()


def test_m31_07_variance_is_against_the_estimated_cost(m31):
    m31.workshop.labour_rate_per_hour = 600.0
    so = m31.order()
    est = m31.env["fix.estimate"].create(
        {
            "order_id": so.id,
            "line_ids": [
                (0, 0, {"description": "Screen", "product_id": m31.product.id,
                        "quantity": 1.0, "unit_price": 2000.0}),
                (0, 0, {"description": "Labour", "line_type": "labour",
                        "quantity": 1.0, "unit_price": 800.0}),
            ],
        }
    )  # fmt: skip
    m31.env.cr.execute("UPDATE fix_estimate SET state='approved' WHERE id=%s", (est.id,))
    est.invalidate_recordset(["state"])
    job = _to_repair(m31, m31.job(so=so))
    # the part at its standard cost + 1 labour hour at the workshop's 600
    assert abs(job.estimated_cost - (m31.product.standard_price + 600.0)) < 0.01


# ============================================================ M31-08
def test_m31_08_a_supervisor_cancels_with_a_reason_and_parts_unwind(m31):
    job = _in_repair(m31)
    reserved = _line(m31, job)
    reserved.action_reserve()
    with refused(m31.env, UserError, "role"):
        job.action_cancel(reason="customer changed mind")
    with refused(m31.env, UserError, "why"):
        _as(m31, m31.supv, job).action_cancel()
    _as(m31, m31.supv, job).action_cancel(reason="customer withdrew the device")
    assert job.sudo().state == "cancelled"
    assert reserved.reservation_state == "released"
    assert job.sudo().cancel_reason == "customer withdrew the device"
    assert job.sudo().cancelled_by_id == m31.supv
    events = _events(m31.env, job, "workshop.job.cancelled")
    assert events and events[0]["service_order_id"] == job.sudo().order_id.id


def test_m31_08_m15_issues_go_back_before_the_job_cancels(m31):
    from .test_a06_m15_workshop_issue import _bucket_qty, _m15

    part, store = _m15(m31, qty=5.0, cost=400.0)
    job = _in_repair(m31)
    line = _line(m31, job, qty=2.0, cost=400.0)
    line.action_consume_part()
    assert _bucket_qty(m31, part, store) == 3.0
    _as(m31, m31.supv, job).action_cancel(reason="wrong device booked")
    assert _bucket_qty(m31, part, store) == 5.0
    assert line.m15_consumption_id.state != "consumed"


# ============================================================ M31-09
def _ber_ready(m):
    so = m.order(state="diagnostic")
    job = m.job(so=so)
    job.action_intake()
    job.action_diagnostic()
    return so, job


def test_m31_09_a_ber_compares_cost_with_value_and_needs_a_photo(m31):
    _so, job = _ber_ready(m31)
    _evidence(m31, job, "diagnostic_report")
    with refused(m31.env, UserError, "give both"):
        job.action_propose_ber("dead board")
    with refused(m31.env, UserError, "economic to repair"):
        job.action_propose_ber("dead board", estimated_repair_cost=3000, device_value=8000)
    with refused(m31.env, UserError, "photo"):
        job.action_propose_ber("dead board", estimated_repair_cost=9000, device_value=8000)
    _evidence(m31, job, "pre_repair_photo")
    job.action_propose_ber("dead board", estimated_repair_cost=9000, device_value=8000)
    assert (job.ber_estimated_repair_cost, job.ber_device_value) == (9000.0, 8000.0)


def test_m31_09_a_zero_write_off_is_still_approved(m31):
    _so, job = _ber_ready(m31)
    _evidence(m31, job, "pre_repair_photo")
    job.action_propose_ber("water damage", estimated_repair_cost=9000, device_value=5000)
    job.invalidate_recordset()
    assert job._dofa_current_tier() == "tier_1" and job.dofa_writeoff_tier == "tier_1"
    job.sudo().write({"dofa_justification": "Water damage across the board"})
    approver, _emp = _user(m31.env, "tier1", [m31.env.ref("cd_entity_config.group_dofa_tier_1")])
    _as(m31, m31.tech2, job).action_confirm_ber()
    job.invalidate_recordset()
    # two technicians no longer close it: it waits for the approval
    assert (job.state, job.approval_state) == ("diagnostic", "pending")
    assert approver


# ============================================================ M31-12
def test_m31_12_only_the_receiving_workshops_supervisor_confirms(m31):
    env = m31.env
    job = m31.job()
    dst = env["fix.workshop"].create(
        {"code": "WS-R2-%d" % job.id, "name": "R2 Depot", "name_bn": "ডিপো"}
    )
    t = (
        env["fix.workshop.transfer"]
        .with_user(m31.tech)
        .create({"job_id": job.id, "to_workshop_id": dst.id, "reason": "BGA"})
    )
    with refused(env, UserError, "receiving workshop"):
        t.with_user(m31.supv).action_confirm()
    dst.sudo().write({"supervisor_user_ids": [(4, m31.supv.id)]})
    t.with_user(m31.supv).action_confirm()
    assert t.state == "in_transit"


# ============================================================ M31-10 / M31-11 (P03)
def test_m31_10_the_job_card_prints_fitted_parts_and_the_internal_roll_up(m31):
    job = _in_repair(m31)
    fitted = _line(m31, job, qty=1.0, cost=500.0)
    fitted.action_consume_part()
    _line(m31, job, qty=3.0, cost=500.0)  # drafted, never fitted
    report = m31.env["report.cd_p03_portal.report_a02_workshop_job"]
    payload = report._payload(job.sudo())
    parts = next(t for t in payload["tables"] if t["title"] == "Parts fitted")
    assert len(parts["rows"]) == 1
    titles = [b["title"] for b in payload["blocks"]]
    assert "Burn-in & rework" in titles and "Internal cost roll-up (BDT)" in titles
    customer = report.with_context(customer_copy=True)._payload(job.sudo())
    assert "Internal cost roll-up (BDT)" not in [b["title"] for b in customer["blocks"]]


def test_m31_11_the_rework_report_counts_every_loop(m31):
    from odoo.addons.cd_p03_portal.controllers.a02 import m31 as surface

    job = _qc_ready(m31, m31.job())
    _as(m31, m31.qc, job).action_fail_qc("fan noise")
    job.action_start_repair()
    a02._protocol_passed(m31, job)
    job.action_submit_qc()
    a02._passed_checklist(m31, job.order_id)
    _as(m31, m31.qc, job).action_fail_qc("fan noise again")
    report = surface._rework_loop_report(m31.env)
    loops = sum(r["loops"] for r in report["rows"])
    assert loops >= 2
    assert "loops per 100 QC'd jobs" in report["notes"][0]
    assert "action_release" in surface.SURFACES["fix.workshop.job"]["actions"]
    assert "action_deliver" not in surface.SURFACES["fix.workshop.job"]["actions"]
