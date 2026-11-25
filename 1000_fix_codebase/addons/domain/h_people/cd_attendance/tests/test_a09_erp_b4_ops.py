# A09 ERP audit fix program, builder B4 — M55 ops-side tests.
#
#   M55-F7  AUT-WFM-04 device health cron (stale terminal -> supervisors'
#           to-do + event, idempotent) and AUT-WFM-06 exception ageing before
#           the payroll cut-off (company setting, default 0 = off)
#   M55-F9 (part) end-of-day detection: missing punch-out, late arrival and
#           early departure against the rostered shift flag the record and
#           route like the capture flags; a zero-punch rostered day (AWOL) is
#           NOT flagged (DEFERRED)
#   M55-F16 fix.work.order keeps M02's operating_unit_id after the duplicate
#           re-declaration was dropped
#   M55-F17 the batch s.117 ledger equals the authoritative per-employee one
import json
from datetime import date, datetime, timedelta

import pytest
from odoo import fields

REC = "fix.attendance.record"


def _dhaka_today(env):
    """The caller's business day (context_today needs a RECORD, not an env:
    an Environment has no .env, which is what the first draft tripped on)."""
    return fields.Date.context_today(env.user.with_context(tz=env.user.tz or "Asia/Dhaka"))


@pytest.fixture
def emp(odoo_env):
    return odoo_env["hr.employee"].create({"name": "B4 Ops"})


def _record(env, emp, check_in, check_out=None):
    vals = {"employee_id": emp.id, "check_in": check_in, "source": "manual"}
    if check_out:
        vals["check_out"] = check_out
    return env[REC].create(vals)


def _events(env, event_type, model, res_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


# --- M55-F7: device health -------------------------------------------------------------


@pytest.fixture
def device(odoo_env):
    return odoo_env["fix.biometric.device"].create(
        {"device_id": "B4-INT041-1", "name": "B4 Uttara Terminal"}
    )


def test_a_stale_terminal_alerts_the_supervisors_once(odoo_env, device):
    device.last_sync_at = fields.Datetime.now() - timedelta(hours=3)
    Device = odoo_env["fix.biometric.device"]
    flagged = Device.cron_check_device_health()
    assert flagged == 1
    activities = odoo_env["mail.activity"].search(
        [("res_model", "=", "fix.biometric.device"), ("res_id", "=", device.id)]
    )
    assert activities, "the stale terminal raises a to-do"
    assert "not syncing" in activities[0].summary
    # the event is published for the record
    assert (
        _events(odoo_env, "attendance.device.stale", "fix.biometric.device", device.id)[0]["device"]
        == "B4-INT041-1"
    )
    # a terminal that synced now is healthy
    device.last_sync_at = fields.Datetime.now()
    assert Device.cron_check_device_health() == 0
    # idempotent: re-flagging does not stack a second to-do per user
    device.last_sync_at = fields.Datetime.now() - timedelta(hours=3)
    before = odoo_env["mail.activity"].search_count(
        [("res_model", "=", "fix.biometric.device"), ("res_id", "=", device.id)]
    )
    Device.cron_check_device_health()
    after = odoo_env["mail.activity"].search_count(
        [("res_model", "=", "fix.biometric.device"), ("res_id", "=", device.id)]
    )
    assert before == after


def test_the_stale_interval_is_configured(odoo_env, device):
    odoo_env["ir.config_parameter"].sudo().set_param("fix.attendance.device_stale_hours", "0.05")
    device.last_sync_at = fields.Datetime.now() - timedelta(minutes=5)
    assert odoo_env["fix.biometric.device"].cron_check_device_health() == 1


# --- M55-F7: exception ageing before the payroll cut-off --------------------------------


def test_pending_exceptions_escalate_inside_the_window_only(odoo_env, emp):
    env = odoo_env
    today = _dhaka_today(env)
    pending = _record(env, emp, datetime(2026, 3, 10, 3, 0), datetime(2026, 3, 10, 13, 0))
    pending._guarded().write({"approval_state": "pending"})
    # the mechanism default is OFF (the window figure is the business's)
    assert "fix_attendance_exception_escalate_days" in env.company._fields
    assert env.company.fix_attendance_exception_escalate_days == 0
    assert env[REC].cron_escalate_pending_exceptions() == 0
    # N = 3 and the next payroll period starts in 2 days: inside the window
    env.company.write({"fix_attendance_exception_escalate_days": 3})
    period = env["fix.payroll.period"].create(
        {
            "name": "B4 Dec",
            "period_start": today + timedelta(days=2),
            "period_end": today + timedelta(days=30),
        }
    )
    assert env[REC].cron_escalate_pending_exceptions() == 1
    summary = "Attendance exception pending before payroll %s" % period.name
    assert env["mail.activity"].search(
        [("res_model", "=", REC), ("res_id", "=", pending.id), ("summary", "=", summary)]
    ), "the pending record escalates to the supervisors"
    assert _events(env, "attendance.exception.escalated", REC, pending.id)
    # idempotent: a second run escalates nothing new
    assert env[REC].cron_escalate_pending_exceptions() == 0
    # a cut-off outside the window escalates nothing
    env.company.write({"fix_attendance_exception_escalate_days": 1})
    env["mail.activity"].search([("summary", "=", summary)]).unlink()
    assert env[REC].cron_escalate_pending_exceptions() == 0


# --- M55-F9 (part): end-of-day exception detection ---------------------------------------


def test_yesterdays_roster_day_exceptions_are_detected(odoo_env, emp):
    env = odoo_env
    yesterday = _dhaka_today(env) - timedelta(days=1)
    shift = env["fix.shift.template"].create(
        {"name": "B4 Day 9-17", "start_hour": 9.0, "end_hour": 17.0}
    )
    # the fixture's opener/closer/ghost slots (the opener is only the roster)
    env["fix.roster.slot"].create({"employee_id": emp.id, "date": yesterday, "shift_id": shift.id})
    closer = env["hr.employee"].create({"name": "B4 Ops Closer"})
    env["fix.roster.slot"].create(
        {"employee_id": closer.id, "date": yesterday, "shift_id": shift.id}
    )
    ghost = env["hr.employee"].create({"name": "B4 Ops Ghost"})
    env["fix.roster.slot"].create(
        {"employee_id": ghost.id, "date": yesterday, "shift_id": shift.id}
    )
    # Dhaka wall clock 10:30-15:30 (04:30-09:30 UTC): late AND early on one day
    late_early = _record(
        env,
        emp,
        datetime(yesterday.year, yesterday.month, yesterday.day, 4, 30),
        datetime(yesterday.year, yesterday.month, yesterday.day, 9, 30),
    )
    # an open shift: checked in, never out
    open_shift = _record(
        env, closer, datetime(yesterday.year, yesterday.month, yesterday.day, 3, 0)
    )
    detected = env[REC]._fix_detect_day_exceptions(yesterday)
    assert detected == 2
    late_early.invalidate_recordset()
    open_shift.invalidate_recordset()
    assert late_early.approval_state == "pending"
    assert "Late arrival" in late_early.approval_reason
    assert "Early departure" in late_early.approval_reason
    assert open_shift.approval_state == "pending"
    assert "Missing punch-out" in open_shift.approval_reason
    # the AWOL case (rostered, zero punches) is DEFERRED, not flagged
    assert not env[REC].search([("employee_id", "=", ghost.id)])
    # idempotent: already-flagged records are not re-flagged
    assert env[REC]._fix_detect_day_exceptions(yesterday) == 0


def test_a_punctual_roster_day_is_not_flagged(odoo_env, emp):
    env = odoo_env
    yesterday = _dhaka_today(env) - timedelta(days=1)
    shift = env["fix.shift.template"].create(
        {"name": "B4 Day 9-17b", "start_hour": 9.0, "end_hour": 17.0}
    )
    env["fix.roster.slot"].create({"employee_id": emp.id, "date": yesterday, "shift_id": shift.id})
    _record(
        env,
        emp,
        datetime(yesterday.year, yesterday.month, yesterday.day, 3, 0),  # 09:00 Dhaka
        datetime(yesterday.year, yesterday.month, yesterday.day, 11, 0),  # 17:00 Dhaka
    )
    assert env[REC]._fix_detect_day_exceptions(yesterday) == 0
    assert env[REC].cron_detect_attendance_exceptions() == 0  # nothing new yesterday


# --- M55-F16: no duplicate field, M02's stands --------------------------------------------


def test_work_order_keeps_m02s_operating_unit(odoo_env):
    WO = odoo_env["fix.work.order"]
    assert "operating_unit_id" in WO._fields
    assert WO._fields["operating_unit_id"].type == "many2one"


# --- M55-F17: the batch s.117 ledger --------------------------------------------------------


def test_batch_ledger_equals_the_authoritative_single_ledger(odoo_env):
    env = odoo_env
    annual = env.ref("cd_hr_core.leave_type_annual")
    emps = env["hr.employee"].create(
        [
            {"name": "B4 Ledger One", "joining_date": date(2024, 6, 1)},
            {"name": "B4 Ledger Two", "joining_date": date(2023, 1, 15)},
            {"name": "B4 Ledger No Service"},  # no joining date: no ledger
        ]
    )
    Leave = env["fix.leave.request"]
    Leave.create(
        {
            "employee_id": emps[0].id,
            "leave_type_id": annual.id,
            "date_from": date(2026, 2, 2),
            "date_to": date(2026, 2, 6),
        }
    ).write({"state": "approved"})
    Leave.create(
        {
            "employee_id": emps[1].id,
            "leave_type_id": annual.id,
            "date_from": date(2026, 3, 2),
            "date_to": date(2026, 3, 8),
        }
    ).write({"state": "rejected"})  # refused leave lifts the carry-forward cap
    as_of = date(2026, 11, 23)
    batch = emps._fix_unused_annual_leave_days_batch(as_of)
    for emp in emps:
        assert batch[emp.id] == emp._fix_unused_annual_leave_days(as_of), emp.name
    assert batch[emps[0].id] > 0  # a joiner with an approved week: earned less taken
    assert batch[emps[2].id] == 0.0  # no service start: no annual leave


# --- deployment wiring ------------------------------------------------------------------------


def test_deployment_b4_crons_and_settings(odoo_env):
    env = odoo_env
    device_cron = env.ref("cd_attendance.cron_check_device_health")
    assert device_cron.active and device_cron.model_id.model == "fix.biometric.device"
    assert device_cron.code.strip() == "model.cron_check_device_health()"
    detect = env.ref("cd_attendance.cron_detect_attendance_exceptions")
    assert detect.active and detect.model_id.model == REC
    assert detect.code.strip() == "model.cron_detect_attendance_exceptions()"
    escalate = env.ref("cd_attendance.cron_escalate_pending_exceptions")
    assert escalate.active and escalate.model_id.model == REC
    assert escalate.code.strip() == "model.cron_escalate_pending_exceptions()"
    # the methods exist and run clean on an empty estate
    assert env["fix.biometric.device"].cron_check_device_health() == 0
    assert env[REC].cron_detect_attendance_exceptions() == 0
    assert env[REC].cron_escalate_pending_exceptions() == 0
    # the escalation window is a company setting, default off
    assert "fix_attendance_exception_escalate_days" in env["res.company"]._fields
