"""A07 P1 (2026-11-04), M45 at M31 QC: every inspection made with a test
instrument writes its usage row (probe 16, FR-EAM-045), stamped with the
calibration at use, so the retrospective impact assessment sees QC work; and
the instrument stays pinned after QC for every caller, the superuser included
(probe 22). Real action_pass_qc / action_fail_qc paths, NON-ADMIN inspector
(the A02 M31 fixture).
"""

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError

from . import test_a02_p0_m31 as a02
from . import test_a07_p0_m45_qc as p0
from ._m45_decided import calibrations_decided  # noqa: F401 - autouse fixture

m31 = a02.m31
_as, refused = a02._as, a02.refused
# the P0 meter factory and ready-job fixture, shared
_meter, ready_job = p0._meter, p0.ready_job


def test_qc_pass_and_fail_write_usage_rows_with_the_calibration_at_use(m31, ready_job):
    meter = _meter(m31, "A7P1-QC-USE")
    passed = ready_job(equipment_id=meter.id)
    _as(m31, m31.qc, passed).action_pass_qc("rails nominal")
    failed = ready_job(equipment_id=meter.id)
    _as(m31, m31.qc, failed).action_fail_qc("ripple out of spec")
    rows = m31.env["fix.equipment.usage"].search([("equipment_id", "=", meter.id)])
    got = {(r.job_ref, r.qc_result, r.source_model, r.source_res_id) for r in rows}
    assert got == {
        (passed.name, "pass", "fix.workshop.job", passed.id),
        (failed.name, "fail", "fix.workshop.job", failed.id),
    }
    latest = meter._m45_latest_calibration()
    assert set(rows.mapped("calibration_id")) == {latest}
    assert set(rows.mapped("fitness_state_at_use")) == {"current"}
    assert set(rows.mapped("used_by_id")) == {m31.qc}
    # a row written for a workshop job is that job's evidence
    row = rows[:1].with_user(m31.qc)
    with refused(m31.env, UserError, "cannot be set directly"):
        row.write({"qc_result": "na"})


def test_a_later_fail_lists_the_qc_uses_in_its_impact_assessment(m31, ready_job):
    today = fields.Date.context_today(m31.env["fix.equipment"])  # the business day
    meter = _meter(m31, "A7P1-QC-IMP", on=today - timedelta(days=60))
    job = ready_job(equipment_id=meter.id)
    _as(m31, m31.qc, job).action_pass_qc()
    fail = m31.env["fix.calibration"].create(
        {
            "equipment_id": meter.id,
            "calibrated_on": today,
            "next_due": today + timedelta(days=1),
            "standard_ref": "STD",
            "result": "fail",
        }
    )
    assert job.name in fail.impact_id.usage_ids.mapped("job_ref")


def test_the_qc_instrument_is_pinned_for_the_superuser_too(m31, ready_job):
    meter = _meter(m31, "A7P1-QC-PIN")
    job = ready_job(equipment_id=meter.id)
    _as(m31, m31.qc, job).action_pass_qc()
    with refused(m31.env, UserError, "measurement evidence"):
        job.sudo().write({"equipment_id": False})
    assert job.equipment_id == meter
