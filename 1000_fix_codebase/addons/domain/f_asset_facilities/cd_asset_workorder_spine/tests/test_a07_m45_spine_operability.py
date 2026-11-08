# A07 M45: a calibration work order is completed by a calibration that certifies the
# instrument. A failed one must not close it. Live ORM, rolled back; the source
# fixtures and helpers are the spine suite's own.
from __future__ import annotations

from datetime import timedelta

from .test_a07_p1_spine import (
    _calibration,
    _deliver,
    _demands,
    _equipment,
    _refused,
    _run_wo,
    c,  # noqa: F401 - the fixture
)


def _calibration_wo(c, code):  # noqa: F811
    e = _equipment(c, code)
    _calibration(c, e, c.today - timedelta(days=340), c.today + timedelta(days=20))
    c.env["fix.equipment"].cron_calibration_status()
    _deliver(c, "equipment.calibration_due", e)
    wo = _demands(c, e).work_order_id
    assert wo.spine_origin == "m45_calibration"
    _run_wo(c, wo, notes="Sent to the lab")
    return e, wo


def test_a_failed_calibration_does_not_complete_the_work_order(c):  # noqa: F811
    e, wo = _calibration_wo(c, "A7SPO-EQ1")
    failed = c.env["fix.calibration"].create(
        {
            "equipment_id": e.id,
            "calibrated_on": c.today,
            "next_due": c.today + timedelta(days=1),
            "standard_ref": "STD-A7",
            "result": "fail",
        }
    )
    assert failed.result == "fail"
    _refused(c.env, wo.with_user(c.fm2).action_verify, match="a passing one")
    assert wo.state != "verified" and not wo.spine_calibration_id
    # the re-calibration that passes does
    good = _calibration(c, e, c.today, c.today + timedelta(days=365))
    wo.with_user(c.fm2).action_verify()
    assert wo.state == "verified" and wo.spine_calibration_id == good


def test_a_rejected_calibration_does_not_complete_it_either(c):  # noqa: F811
    e, wo = _calibration_wo(c, "A7SPO-EQ2")
    rejected = _calibration(c, e, c.today, c.today + timedelta(days=365))
    rejected.sudo()._guarded().write({"decision_state": "rejected"})
    _refused(c.env, wo.with_user(c.fm2).action_verify, match="a passing one")
    assert wo.state != "verified"
