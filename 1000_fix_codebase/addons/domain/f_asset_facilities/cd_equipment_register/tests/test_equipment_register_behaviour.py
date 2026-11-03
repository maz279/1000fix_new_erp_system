"""cd_equipment_register behaviour (live ORM, rolled back): test equipment
calibration tracking and the ISO 9001 7.1.5 usability gate."""

from __future__ import annotations

import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

TODAY = fields.Date.today()


def _events(env, event_type, res_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", "fix.calibration"),
            ("aggregate_id", "=", res_id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


def _equipment(env, code="EQ-MM-01", name="Fluke 117 Multimeter"):
    return env["fix.equipment"].create({"code": code, "name": name, "category": "multimeter"})


def _calibrate(env, equipment, calibrated_on, next_due, result="pass"):
    return env["fix.calibration"].create(
        {
            "equipment_id": equipment.id,
            "calibrated_on": calibrated_on,
            "next_due": next_due,
            "result": result,
            "standard_ref": "BSTI-REF-001",
        }
    )


def test_uncalibrated_equipment_has_no_dates_and_is_not_usable(odoo_env):
    """A07 audit M45-1: 'no due date' was treated as fit. No calibration means
    no certificate, so the instrument is unfit."""
    eq = _equipment(odoo_env)
    assert eq.last_calibration is False
    assert eq.next_calibration is False
    assert eq.calibration_overdue is False
    assert eq.calibration_state == "never"
    with pytest.raises(UserError, match="never been calibrated"):
        eq.action_assert_usable()


def test_the_latest_calibration_decides(odoo_env):
    """A07 audit M45-1: fitness was the max next_due of PASSING rows, so a
    later FAIL changed nothing. The latest calibration now rules."""
    eq = _equipment(odoo_env)
    _calibrate(odoo_env, eq, TODAY - timedelta(days=400), TODAY - timedelta(days=35))
    _calibrate(odoo_env, eq, TODAY - timedelta(days=30), TODAY + timedelta(days=335))
    assert eq.next_calibration == TODAY + timedelta(days=335)
    assert eq.action_assert_usable() is True
    # a later FAILED calibration withdraws the earlier pass and never gives a due date
    _calibrate(odoo_env, eq, TODAY - timedelta(days=1), TODAY + timedelta(days=900), "fail")
    assert eq.last_calibration == TODAY - timedelta(days=1)
    assert eq.next_calibration is False
    assert eq.calibration_state == "failed"
    with pytest.raises(UserError, match="failed its latest calibration"):
        eq.action_assert_usable()
    # re-calibrated and passed: fit again
    _calibrate(odoo_env, eq, TODAY, TODAY + timedelta(days=365))
    assert (eq.calibration_state, eq.next_calibration) == ("current", TODAY + timedelta(days=365))
    assert eq.action_assert_usable() is True


def test_overdue_calibration_blocks_use(odoo_env):
    eq = _equipment(odoo_env)
    _calibrate(odoo_env, eq, TODAY - timedelta(days=400), TODAY - timedelta(days=1))
    assert eq.calibration_overdue is True
    assert eq.calibration_state == "overdue"
    with pytest.raises(UserError, match="Calibration overdue on Fluke 117 Multimeter"):
        eq.action_assert_usable()


def test_usability_gate_checks_every_instrument(odoo_env):
    """Regression: the gate returned after the FIRST record, so an overdue
    instrument later in the recordset passed the ISO 9001 7.1.5 check."""
    fine = _equipment(odoo_env, "EQ-A", "Calibrated Scope")
    overdue = _equipment(odoo_env, "EQ-B", "Overdue Programmer")
    _calibrate(odoo_env, fine, TODAY, TODAY + timedelta(days=365))
    _calibrate(odoo_env, overdue, TODAY - timedelta(days=400), TODAY - timedelta(days=5))
    pair = (fine | overdue).sorted("code")
    assert pair[0] == fine
    with pytest.raises(UserError, match="Overdue Programmer"):
        pair.action_assert_usable()


def test_empty_recordset_is_trivially_usable(odoo_env):
    assert odoo_env["fix.equipment"].action_assert_usable() is True


def test_failing_a_calibration_withdraws_its_dates(odoo_env):
    """Regression: `result` was missing from the compute dependencies, so a
    calibration re-classified as failed kept certifying the instrument."""
    eq = _equipment(odoo_env)
    cal = _calibrate(odoo_env, eq, TODAY - timedelta(days=10), TODAY + timedelta(days=355))
    assert eq.next_calibration == TODAY + timedelta(days=355)
    cal.write({"result": "fail"})
    assert eq.next_calibration is False
    assert eq.last_calibration == TODAY - timedelta(days=10)  # the event still happened
    assert eq.calibration_state == "failed"


def test_calibration_publishes_recorded_event(odoo_env):
    eq = _equipment(odoo_env, code="EQ-PUB")
    due = TODAY + timedelta(days=180)
    cal = _calibrate(odoo_env, eq, TODAY, due)
    assert _events(odoo_env, "equipment.calibration.recorded", cal.id) == [
        {"equipment": "EQ-PUB", "result": "pass", "next_due": str(due)}
    ]
    assert _events(odoo_env, "equipment.calibration.overdue", cal.id) == []


def test_recording_an_already_lapsed_calibration_publishes_overdue(odoo_env):
    eq = _equipment(odoo_env, code="EQ-LATE")
    cal = _calibrate(odoo_env, eq, TODAY - timedelta(days=370), TODAY - timedelta(days=5))
    assert _events(odoo_env, "equipment.calibration.overdue", cal.id) == [{"equipment": "EQ-LATE"}]


def test_next_due_cannot_precede_calibration(odoo_env):
    eq = _equipment(odoo_env)
    with (
        pytest.raises(UserError, match="Next-due precedes the calibration date"),
        odoo_env.cr.savepoint(),
    ):
        _calibrate(odoo_env, eq, TODAY, TODAY - timedelta(days=1))
