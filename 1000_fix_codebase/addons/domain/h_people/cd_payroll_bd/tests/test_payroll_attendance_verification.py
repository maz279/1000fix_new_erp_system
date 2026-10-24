"""BRU-WFM-01 / BRU-PAY-01: payroll runs only on VERIFIED attendance - flagged
mobile clock-ins (M55 AUT-WFM-02) still pending approval block the run, and a
rejected clock-in is no worked time (live ORM, ``odoo_env``, rolled back)."""

from datetime import date, datetime

import pytest
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

PERIOD_START = date(2026, 1, 1)
PERIOD_END = date(2026, 1, 31)


def _clock(env, emp, day, hours, state):
    return env["fix.attendance.record"].create(
        {
            "employee_id": emp.id,
            "check_in": datetime(2026, 1, day, 8, 0),
            "check_out": datetime(2026, 1, day, 8 + hours, 0),
            "source": "mobile",
            "geofence_result": "outside",
            "approval_state": state,
            "approval_reason": "position outside the geofence",
        }
    )


@pytest.fixture
def run(odoo_env):
    env = odoo_env
    emp = env["hr.employee"].create({"name": "Payroll Flagged Tech"})
    env["fix.employment.contract"].create(
        {
            "employee_id": emp.id,
            "company_id": emp.company_id.id,
            "contract_type": "permanent",
            "joining_date": date(2020, 1, 1),
            "basic_monthly": 24000.0,
            "state": "active",
        }
    )
    lock = env["fix.attendance.lock"].create(
        {"name": "Jan 2026", "period_start": PERIOD_START, "period_end": PERIOD_END}
    )
    period = env["fix.payroll.period"].create(
        {"name": "2026-01", "period_start": PERIOD_START, "period_end": PERIOD_END}
    )
    return env, emp, lock, period


def test_payroll_refuses_a_period_with_pending_clock_ins_naming_them(run):
    env, emp, lock, period = run
    pending = _clock(env, emp, 20, 10, "pending")
    lock.state = "locked"  # a lock written around action_lock's own pending check (legacy data)
    with pytest.raises(UserError) as err, env.cr.savepoint():
        period.action_verify_attendance_locked()
    assert str(err.value) == (
        "Journey 13: 1 clock-in(s) of 2026-01 are still pending approval - payroll may not "
        f"calculate on unverified attendance: {pending.display_label}"
    )
    assert period.state == "draft"


def test_rejected_clock_ins_are_not_paid_overtime(run):
    env, emp, lock, period = run
    approved = _clock(env, emp, 10, 10, "pending")  # 2h overtime
    rejected = _clock(env, emp, 11, 12, "pending")  # would be 4h overtime
    approved.action_approve()
    rejected.action_reject(reason="Not on site")
    lock.action_lock()
    period.action_verify_attendance_locked()
    period.action_calculate()
    slip = period.payslip_ids.filtered(lambda s: s.employee_id == emp)
    # only the approved day: 10h - 8h standard = 2h overtime
    assert slip.ot_hours == 2.0
