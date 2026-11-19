"""M31 capture pass 2 (19 Nov 2026): each page captures the spec's own records.

After the 13/14 Nov passes every page had a relevant button, but read against
the specification (FR-WSR-001..053, BRU-WSR-01..14, §10.1 owned entities)
most of what a workshop records still had no capture: device location,
ESD checks, hand-over, shift close, escalation, teardown, instrument use,
consumables, burn-in station runs, internal rework, workshop transfer, the
work clock and the cost build-up. BRU-WSR-08/12/14 were not enforced.

Captures are saved through the real controller as non-admin workshop users
(``ui``); model rules are exercised as those users. ``odoo_env`` rolls back.
"""

from __future__ import annotations

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError

from . import test_a02_p0_m31 as a02
from .test_m31_relevant_capture import _allocate, _fragment_subs
from .test_m31_submodule_capture import m31, screens, ui  # noqa: F401 - fixtures

refused = a02.refused


def _ok(res):
    assert "error" not in res and res.get("success", True), res
    return res


def _err(res):
    assert ("error" in res) or (res.get("success") is False), res
    return res.get("error") or ""


def _intake(m31, **vals):  # noqa: F811
    job = m31.job(**vals)
    job.action_intake()
    return job


def _location(m31, kind="incoming_buffer", code=None, workshop=None):  # noqa: F811
    return m31.env["fix.workshop.location"].create(
        {
            "workshop_id": (workshop or m31.workshop).id,
            "code": code or "LOC-%s" % kind,
            "name": kind,
            "kind": kind,
        }
    )


def _act(ui, user, model, rec, method, **kwargs):  # noqa: F811
    return ui.action(user, model=model, ids=[rec.id], method=method, kwargs=kwargs or None)


# --- the pages offer the spec's captures ---------------------------------------

EXPECTED_FORMS = {
    "1": {"Move Device to Location"},
    "2": {"Workshop Location", "Burn-In Station", "ESD Bench Check"},
    "3": {"Shift Close", "Move Device to Location"},
    "4": {"Escalation"},
    "5": {"Teardown Record", "Instrument Use", "Knowledge Capture"},
    "6": {"Consumable Usage"},
    "7": {"Burn-In Run"},
    "8": {"Workshop Transfer"},
    "9": {"Work Clock"},
}


def test_every_page_offers_its_spec_records(screens):  # noqa: F811
    data = _fragment_subs()
    subs = {s[0]: s[3] for s in data["sub"]}
    for no, forms in EXPECTED_FORMS.items():
        assert forms <= set(subs[no]["forms"]), (no, subs[no]["forms"])
        for form in forms:
            target = data["chips"]["M31:%s" % form]
            assert target == "M61-form-capture" or target in screens, form
        for sid in subs[no]["screens"]:
            assert sid in screens, sid
    # page 8's button is the transfer itself, not a re-route
    assert subs["8"]["create"] == "M31-form-transfer"


def test_every_list_shows_fields_of_its_model(screens, odoo_env):  # noqa: F811
    bad = []
    for sid, cfg in screens.items():
        if cfg.get("kind") != "model_list":
            continue
        model = odoo_env[cfg["model"]]._fields
        bad += ["%s.%s" % (sid, c) for c in cfg["cols"] if c not in model]
    assert not bad, bad


# --- 1/3: device location (FR-WSR-005/053) -----------------------------------------


def test_a_booked_in_device_is_placed_and_its_trail_is_fixed(m31, ui):  # noqa: F811
    buffer = _location(m31)
    job = _intake(m31)
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.custody.move",
            values={"job_id": job.id, "location_id": buffer.id},
        )
    )
    job.invalidate_recordset()
    assert job.current_location_id == buffer
    move = m31.env["fix.workshop.custody.move"].browse(res["id"])
    assert move.moved_by_id == m31.tech and move.moved_at
    # a location of another workshop is refused, and so is a draft job
    other = m31.env["fix.workshop"].create({"code": "WS-P2-O", "name": "Other", "name_bn": "অ"})
    foreign = _location(m31, workshop=other, code="LOC-F")
    assert "belongs to" in _err(
        ui.write(
            m31.tech,
            model="fix.workshop.custody.move",
            values={"job_id": job.id, "location_id": foreign.id},
        )
    )
    draft = m31.job()
    assert "not booked in" in _err(
        ui.write(
            m31.tech,
            model="fix.workshop.custody.move",
            values={"job_id": draft.id, "location_id": buffer.id},
        )
    )
    with refused(m31.env, match="never deleted"):
        move.with_user(m31.tech).unlink()


# --- 2: ESD check (FR-WSR-050) ---------------------------------------------------------


def test_an_esd_check_feeds_the_bench_interlock(m31, ui):  # noqa: F811
    bench = m31.l2
    _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.esd.check",
            values={"bench_id": bench.id, "wrist_strap_mohm": 12.0, "worksurface_mohm": 200.0},
        )
    )
    bench.invalidate_recordset()
    assert bench.is_esd_safe and bench.esd_last_verified_date == fields.Date.today()
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.esd.check",
            values={"bench_id": bench.id, "wrist_strap_mohm": 60.0, "worksurface_mohm": 200.0},
        )
    )
    bench.invalidate_recordset()
    failed = m31.env["fix.workshop.esd.check"].browse(res["id"])
    assert not failed.passed and not bench.is_esd_safe


# --- 3: hand-over (FR-WSR-015) and shift close (BRU-WSR-13) ---------------------------


def test_a_hand_over_needs_its_note_and_is_recorded(m31, ui):  # noqa: F811
    job = _intake(m31)
    _ok(_allocate(ui, m31.tech, job, m31.l1))
    assert "hand-over" in _err(_allocate(ui, m31.tech, job, m31.l2))
    _ok(_allocate(ui, m31.tech, job, m31.l2, note="L1 bench needed for the express queue"))
    rows = m31.env["fix.workshop.bench.handover"].search([("job_id", "=", job.id)])
    assert len(rows) == 2  # the first allocation and the hand-over
    last = rows.sorted("id")[-1]
    assert (last.from_bench_id, last.to_bench_id) == (m31.l1, m31.l2)
    assert "express queue" in last.note


def test_the_shift_does_not_close_with_a_high_value_device_outside_the_store(m31, ui):  # noqa: F811
    job = _intake(m31, high_value_device=True)
    secure = _location(m31, kind="secure_store", code="SAFE")
    held = (
        m31.env["fix.workshop.job"]
        .sudo()
        .search_count(
            [
                ("workshop_id", "=", m31.workshop.id),
                (
                    "state",
                    "in",
                    (
                        "intake",
                        "diagnostic",
                        "waiting_parts",
                        "in_repair",
                        "burn_in",
                        "qc_pending",
                        "qc_failed",
                        "ready",
                    ),
                ),
            ]
        )
    )
    res = _ok(
        ui.write(
            m31.supv,
            model="fix.workshop.shift.close",
            values={"workshop_id": m31.workshop.id, "counted_wip": held},
        )
    )
    close = m31.env["fix.workshop.shift.close"].browse(res["id"])
    # a technician does not close a shift
    assert "supervisor" in _err(
        _act(ui, m31.tech, "fix.workshop.shift.close", close, "action_close")
    )
    assert "BRU-WSR-13" in _err(
        _act(ui, m31.supv, "fix.workshop.shift.close", close, "action_close")
    )
    m31.env["fix.workshop.custody.move"].with_user(m31.tech).create(
        {"job_id": job.id, "location_id": secure.id}
    )
    _ok(_act(ui, m31.supv, "fix.workshop.shift.close", close, "action_close"))
    close.invalidate_recordset()
    assert (
        close.state == "closed"
        and close.high_value_count == 1
        and job.name in close.high_value_summary
    )


def test_a_count_that_does_not_reconcile_needs_its_exception(m31, ui):  # noqa: F811
    _intake(m31)
    close = (
        m31.env["fix.workshop.shift.close"]
        .with_user(m31.supv)
        .create({"workshop_id": m31.workshop.id, "counted_wip": 999})
    )
    assert "does not reconcile" in _err(
        _act(ui, m31.supv, "fix.workshop.shift.close", close, "action_close")
    )
    close.write({"exception_note": "Recounted: count sheet error"})
    _ok(_act(ui, m31.supv, "fix.workshop.shift.close", close, "action_close"))


# --- 4: escalation (FR-WSR-029) ---------------------------------------------------------


def test_an_escalation_is_decided_by_another_supervisor(m31, ui):  # noqa: F811
    job = _intake(m31)
    assert "above the job" in _err(
        ui.write(
            m31.tech,
            model="fix.workshop.escalation",
            values={
                "job_id": job.id,
                "escalation_type": "higher_level",
                "to_level": "l1",
                "reason": "x",
            },
        )
    )
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.escalation",
            values={
                "job_id": job.id,
                "escalation_type": "higher_level",
                "to_level": "l3",
                "reason": "Board short beyond L1",
            },
        )
    )
    esc = m31.env["fix.workshop.escalation"].browse(res["id"])
    assert "State: intake" in esc.context_snapshot
    assert "supervisor" in _err(_act(ui, m31.tech, "fix.workshop.escalation", esc, "action_accept"))
    _ok(_act(ui, m31.supv, "fix.workshop.escalation", esc, "action_accept", note="agreed"))
    job.invalidate_recordset()
    esc.invalidate_recordset()
    assert job.repair_level == "l3" and esc.state == "accepted" and esc.decided_by_id == m31.supv


def test_a_supervisor_does_not_decide_his_own_escalation(m31, ui):  # noqa: F811
    job = _intake(m31)
    esc = (
        m31.env["fix.workshop.escalation"]
        .with_user(m31.supv)
        .create(
            {
                "job_id": job.id,
                "escalation_type": "higher_level",
                "to_level": "l2",
                "reason": "needs the hot-air station",
            }
        )
    )
    assert "does not decide" in _err(
        _act(ui, m31.supv, "fix.workshop.escalation", esc, "action_accept")
    )


# --- 5: teardown and instrument use (FR-WSR-019/025/040, BRU-WSR-09) --------------------


def test_a_teardown_step_is_recorded_and_kept(m31, ui):  # noqa: F811
    job = _intake(m31)
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.teardown",
            values={"job_id": job.id, "component": "Back cover", "condition": "corroded"},
        )
    )
    step = m31.env["fix.workshop.teardown"].browse(res["id"])
    assert step.recorded_by_id == m31.tech
    with refused(m31.env, match="never deleted"):
        step.with_user(m31.tech).unlink()


def test_an_out_of_calibration_instrument_is_flagged_and_reaches_m45(m31, ui):  # noqa: F811
    job = _intake(m31)
    meter = m31.env["fix.equipment"].create(
        {"code": "P2-DMM", "name": "Bench DMM"}
    )  # never calibrated
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.instrument.use",
            values={
                "job_id": job.id,
                "equipment_id": meter.id,
                "purpose": "rail check",
                "used_from": fields.Datetime.to_string(
                    fields.Datetime.now() - timedelta(minutes=5)
                ),
            },
        )
    )
    use = m31.env["fix.workshop.instrument.use"].browse(res["id"])
    job.invalidate_recordset()
    assert not use.calibration_valid and use.calibration_problem
    assert job.calibration_review
    assert use.usage_id.equipment_id == meter and use.usage_id.source_model == use._name
    # the evidence is fixed: only the end time and purpose are filled in later
    with refused(m31.env, match="evidence"):
        use.with_user(m31.tech).write({"equipment_id": meter.id + 0, "job_id": job.id})


# --- 6: consumables (FR-WSR-024) and part sources (BRU-WSR-08/12) ------------------------


def test_a_consumable_is_costed_at_standard_cost(m31, ui):  # noqa: F811
    job = _intake(m31)
    flux = m31.env["product.product"].create({"name": "Flux P2", "standard_price": 40.0})
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.consumable.usage",
            values={"job_id": job.id, "product_id": flux.id, "quantity": 2.5},
        )
    )
    line = m31.env["fix.workshop.consumable.usage"].browse(res["id"])
    assert line.unit_cost == 40.0 and line.subtotal == 100.0
    job.sudo().write({"state": "cancelled"})
    assert "closed" in _err(
        ui.write(
            m31.tech,
            model="fix.workshop.consumable.usage",
            values={"job_id": job.id, "product_id": flux.id, "quantity": 1},
        )
    )


def test_warranty_stock_and_harvested_parts_follow_the_order_category(m31):  # noqa: F811
    Line = m31.env["fix.workshop.part.line"].with_user(m31.tech)
    paid = m31.job()
    with refused(m31.env, ValidationError, match="BRU-WSR-08"):
        Line.create(
            {
                "job_id": paid.id,
                "product_id": m31.product.id,
                "quantity": 1,
                "source_origin": "oem_consignment",
            }
        )
    warranty_so = m31.order()
    # test setup only: M01's warranty-cover gate is not under test here
    m31.env.cr.execute(
        "UPDATE fix_service_order SET order_category='warranty' WHERE id=%s", (warranty_so.id,)
    )
    warranty_so.invalidate_recordset(["order_category"])
    warranty = m31.job(so=warranty_so)
    with refused(m31.env, ValidationError, match="BRU-WSR-12"):
        Line.create(
            {
                "job_id": warranty.id,
                "product_id": m31.product.id,
                "quantity": 1,
                "source_origin": "donor_board_harvest",
                "donor_board_serial": "DB-1",
            }
        )
    # the legitimate paths still work
    Line.create(
        {
            "job_id": warranty.id,
            "product_id": m31.product.id,
            "quantity": 1,
            "source_origin": "oem_consignment",
        }
    )
    Line.create(
        {
            "job_id": paid.id,
            "product_id": m31.product.id,
            "quantity": 1,
            "source_origin": "donor_board_harvest",
            "donor_board_serial": "DB-2",
        }
    )


# --- 7: burn-in at a station (FR-WSR-033/034, BRU-WSR-07) -------------------------------


def test_burn_in_runs_at_a_station_for_its_full_duration(m31, ui):  # noqa: F811
    station = m31.env["fix.workshop.burnin.station"].create(
        {"workshop_id": m31.workshop.id, "code": "BI-1", "name": "Rack 1", "capacity": 1}
    )
    job = a02._l2_in_repair(m31)
    # a workshop with a station runs burn-in there, not from the bare button
    with refused(m31.env, match="stations"):
        job.with_user(m31.tech).action_start_burn_in()
    # never shorter than the protocol minimum (240 for L2)
    assert "BRU-WSR-07" in _err(
        ui.write(
            m31.tech,
            model="fix.workshop.burnin.session",
            values={"job_id": job.id, "station_id": station.id, "required_minutes": 30},
        )
    )
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.burnin.session",
            values={"job_id": job.id, "station_id": station.id},
        )
    )
    run = m31.env["fix.workshop.burnin.session"].browse(res["id"])
    job.invalidate_recordset()
    assert job.state == "burn_in" and run.required_minutes == 240.0
    # the station is full
    other = a02._l2_in_repair(m31)
    assert "full" in _err(
        ui.write(
            m31.tech,
            model="fix.workshop.burnin.session",
            values={"job_id": other.id, "station_id": station.id},
        )
    )
    # extended, never shortened
    _ok(_act(ui, m31.tech, "fix.workshop.burnin.session", run, "action_extend", minutes="60"))
    run.invalidate_recordset()
    assert run.required_minutes == 300.0
    with refused(m31.env, match="workflow"):
        run.with_user(m31.tech).write({"required_minutes": 10})
    # 250 minutes in: past the policy minimum, short of this run's 300
    job.sudo()._guarded().write(
        {"burn_in_started_at": fields.Datetime.now() - timedelta(minutes=250)}
    )
    with refused(m31.env, match="BRU-WSR-07"):
        job.with_user(m31.tech).action_pass_burn_in()
    job.with_user(m31.tech).action_fail_burn_in(reason="thermal shutdown at 70C")
    run.invalidate_recordset()
    assert run.outcome == "failed" and run.completed_at
    loop = m31.env["fix.workshop.rework"].search([("job_id", "=", job.id)])
    assert loop.failed_at_state == "burn_in" and loop.iteration == 1


# --- 8: internal rework (BRU-WSR-10) and transfers (BRU-WSR-14) ---------------------------


def test_a_failed_qc_writes_a_rework_record_nobody_can_hide(m31):  # noqa: F811
    job = a02._qc_ready(m31, m31.job())
    job.with_user(m31.qc).action_fail_qc(reason="Charging port loose")
    loop = m31.env["fix.workshop.rework"].search([("job_id", "=", job.id)])
    assert loop.failed_at_state == "qc" and loop.attributed_to_id == m31.tech_emp
    with refused(m31.env, match="BRU-WSR-10"):
        loop.with_user(m31.supv).write({"reason": "nothing"})
    with refused(m31.env, match="BRU-WSR-10"):
        loop.with_user(m31.supv).unlink()


def test_a_booked_in_job_moves_workshop_only_by_a_confirmed_transfer(m31, ui):  # noqa: F811
    env = m31.env
    other = env["fix.workshop"].create(
        {"code": "WS-P2-T", "name": "Specialist Depot", "name_bn": "ডি"}
    )
    job = _intake(m31)
    _ok(_allocate(ui, m31.tech, job, m31.l1))
    # the routing form can no longer move it
    assert "BRU-WSR-14" in _err(
        ui.write(
            m31.tech, model="fix.workshop.job", record_id=job.id, values={"workshop_id": other.id}
        )
    )
    res = _ok(
        ui.write(
            m31.tech,
            model="fix.workshop.transfer",
            values={"job_id": job.id, "to_workshop_id": other.id, "reason": "BGA reballing"},
        )
    )
    transfer = env["fix.workshop.transfer"].browse(res["id"])
    assert transfer.from_workshop_id == m31.workshop
    # a technician does not confirm for the receiving workshop
    assert "BRU-WSR-14" in _err(
        _act(ui, m31.tech, "fix.workshop.transfer", transfer, "action_confirm")
    )
    _ok(_act(ui, m31.supv, "fix.workshop.transfer", transfer, "action_confirm"))
    job.invalidate_recordset()
    transfer.invalidate_recordset()
    assert job.workshop_id == other and not job.bench_id
    assert transfer.state == "in_transit"
    assert transfer.consignment_id.consignment_type == "branch_transfer"
    assert transfer.consignment_id.service_order_id == job.order_id
    _ok(_act(ui, m31.tech, "fix.workshop.transfer", transfer, "action_receive"))


def test_the_requester_does_not_confirm_his_own_transfer(m31, ui):  # noqa: F811
    other = m31.env["fix.workshop"].create({"code": "WS-P2-U", "name": "Depot U", "name_bn": "ডি"})
    job = _intake(m31)
    transfer = (
        m31.env["fix.workshop.transfer"]
        .with_user(m31.supv)
        .create({"job_id": job.id, "to_workshop_id": other.id, "reason": "capacity"})
    )
    assert "does not confirm" in _err(
        _act(ui, m31.supv, "fix.workshop.transfer", transfer, "action_confirm")
    )


# --- 9: work clock (FR-WSR-026) and the cost build-up (FR-WSR-043/044) -------------------


def test_the_clock_books_time_and_the_cost_sheet_builds_from_it(m31, ui):  # noqa: F811
    job = _intake(m31)
    m31.workshop.write(
        {"labour_rate_per_hour": 600.0, "equipment_rate_per_hour": 0.0, "overhead_pct": 10.0}
    )
    res = _ok(
        ui.write(
            m31.tech, model="fix.workshop.time.log", values={"job_id": job.id, "activity": "active"}
        )
    )
    log = m31.env["fix.workshop.time.log"].browse(res["id"])
    assert log.technician_id == m31.tech_emp and log.running
    # one clock per technician
    other = _intake(m31)
    assert "clock is running" in _err(
        ui.write(
            m31.tech,
            model="fix.workshop.time.log",
            values={"job_id": other.id, "activity": "active"},
        )
    )
    # 30 minutes later
    log.sudo()._guarded().write({"started_at": fields.Datetime.now() - timedelta(minutes=30)})
    _ok(_act(ui, m31.tech, "fix.workshop.time.log", log, "action_stop"))
    job.invalidate_recordset()
    assert round(job.logged_active_minutes) == 30 and round(job.actual_logged_minutes) == 30
    with refused(m31.env, match="not edited"):
        log.with_user(m31.tech).write({"note": "rewrite"})

    flux = m31.env["product.product"].create({"name": "Flux C", "standard_price": 50.0})
    m31.env["fix.workshop.consumable.usage"].with_user(m31.tech).create(
        {"job_id": job.id, "product_id": flux.id, "quantity": 2}
    )
    _ok(_act(ui, m31.tech, "fix.workshop.job", job, "action_build_cost_sheet"))
    job.invalidate_recordset()
    amounts = {line.cost_type: line.amount for line in job.cost_line_ids}
    assert set(amounts) == {"labour", "parts", "consumables", "equipment", "overhead"}
    assert round(amounts["labour"]) == 300 and amounts["consumables"] == 100.0
    assert round(amounts["overhead"], 2) == round(
        (amounts["labour"] + 100.0 + amounts["parts"]) * 0.10, 2
    )
    assert round(job.full_cost, 2) == round(sum(amounts.values()), 2)
    with refused(m31.env, match="derived"):
        job.cost_line_ids[0].with_user(m31.tech).write({"amount": 1})


def test_a_user_without_the_workshop_role_captures_nothing(m31, ui):  # noqa: F811
    job = _intake(m31)
    for model, vals in (
        ("fix.workshop.teardown", {"job_id": job.id, "component": "x", "condition": "good"}),
        ("fix.workshop.time.log", {"job_id": job.id, "activity": "active"}),
    ):
        _err(ui.write(m31.plain, model=model, values=vals))


def test_closed_jobs_take_no_new_record(m31):  # noqa: F811
    job = m31.job()
    job.sudo().write({"state": "delivered"})
    with refused(m31.env, UserError, match="closed"):
        m31.env["fix.workshop.teardown"].with_user(m31.tech).create(
            {"job_id": job.id, "component": "x", "condition": "good"}
        )
