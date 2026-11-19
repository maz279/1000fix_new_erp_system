"""A07 workflow audit, P0 for the M45 fitness gate at M31 QC (M45-1, M45-4).

The A07 probes 20-22 (working/A07_evidence/probes/m45/probe_m45.py) turned
into controls, on the real action_pass_qc path with no mock. The users and the
job set-up are the A02 M31 fixture (test_a02_p0_m31.py): `qc` is a Workshop
QC Inspector and `tech` the repairing technician, both NON-ADMIN.
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

from . import test_a02_p0_m31 as a02
from ._m45_decided import calibrations_decided  # noqa: F401 - autouse fixture

# the A02 M31 users and job factory, shared as a fixture
m31 = a02.m31
_as, _qc_ready, refused = a02._as, a02._qc_ready, a02.refused

PARAM = "cd_workshop.qc_requires_instrument"


def _meter(m, code, result="pass", on=None, due=None):
    today = fields.Date.today()
    meter = m.env["fix.equipment"].create({"code": code, "name": "QC meter %s" % code})
    if result:
        m.env["fix.calibration"].create(
            {
                "equipment_id": meter.id,
                "calibrated_on": on or today - timedelta(days=10),
                "next_due": due or today + timedelta(days=355),
                "standard_ref": "STD-A7-QC",
                "result": result,
            }
        )
    return meter


@pytest.fixture
def ready_job(m31):
    def _make(**vals):
        job = m31.job(**vals)
        _qc_ready(m31, job)
        return job

    return _make


def test_qc_refuses_unfit_instruments(m31, ready_job):
    """Probe 20: failed-after-pass, out-of-service, never calibrated, retired."""
    today = fields.Date.today()
    failed = _meter(m31, "A7QC-FAIL", on=today - timedelta(days=100))
    m31.env["fix.calibration"].create(
        {
            "equipment_id": failed.id,
            "calibrated_on": today,
            "next_due": today + timedelta(days=1),
            "standard_ref": "STD",
            "result": "fail",
        }
    )
    oos = _meter(m31, "A7QC-OOS")
    m31.env["fix.equipment.oos"].create({"equipment_id": oos.id, "reason": "fault"})
    never = _meter(m31, "A7QC-NEVER", result=None)
    retired = _meter(m31, "A7QC-RET")
    retired.operational_status = "retired"
    overdue = _meter(
        m31, "A7QC-LATE", on=today - timedelta(days=400), due=today - timedelta(days=1)
    )
    for meter, msg in (
        (failed, "failed its latest calibration"),
        (oos, "Out of Service"),
        (never, "never been calibrated"),
        (retired, "Retired"),
        (overdue, "Calibration overdue"),
    ):
        job = ready_job(equipment_id=meter.id)
        with refused(m31.env, UserError, msg):
            _as(m31, m31.qc, job).action_pass_qc()
        assert (job.state, job.qc_passed) == ("qc_pending", False), meter.code


def test_qc_passes_with_a_fit_instrument(m31, ready_job):
    meter = _meter(m31, "A7QC-OK")
    job = ready_job(equipment_id=meter.id)
    _as(m31, m31.qc, job).action_pass_qc("rails nominal")
    assert (job.state, job.qc_passed, job.equipment_id) == ("ready", True, meter)


def test_instrument_issued_to_the_technician_counts_as_on_the_bench(m31, ready_job):
    meter = _meter(m31, "A7QC-ISSUED")
    m31.env["fix.equipment.issue"].create(
        {"equipment_id": meter.id, "custodian_id": m31.tech_emp.id}
    )
    job = ready_job(equipment_id=meter.id)
    _as(m31, m31.qc, job).action_pass_qc()
    assert job.state == "ready"


def test_instrument_issued_to_someone_else_is_refused(m31, ready_job):
    meter = _meter(m31, "A7QC-ELSEWHERE")
    m31.env["fix.equipment.issue"].create(
        {"equipment_id": meter.id, "custodian_id": m31.tech2_emp.id}
    )
    job = ready_job(equipment_id=meter.id)
    with refused(m31.env, UserError, "only its holder"):
        _as(m31, m31.qc, job).action_pass_qc()


def test_qc_without_instrument_follows_the_business_switch(m31, ready_job):
    """Probe 21 / BRU-EAM-15. Off by default (live QC names no instrument
    today); once the business switches it on a QC pass must name one."""
    ICP = m31.env["ir.config_parameter"].sudo()
    ICP.set_param(PARAM, "0")
    job = ready_job()
    _as(m31, m31.qc, job).action_pass_qc()  # deploy-safe default
    assert job.state == "ready"

    ICP.set_param(PARAM, "1")
    job = ready_job()
    with refused(m31.env, UserError, "BRU-EAM-15"):
        _as(m31, m31.qc, job).action_pass_qc()
    assert job.state == "qc_pending"
    # a QC FAIL does not need an instrument: it opens the rework loop
    _as(m31, m31.qc, job).action_fail_qc("no power")
    assert job.state == "qc_failed"
    job = ready_job(equipment_id=_meter(m31, "A7QC-REQ").id)
    _as(m31, m31.qc, job).action_pass_qc()
    assert job.state == "ready"


def test_instrument_frozen_once_qc_passed(m31, ready_job):
    """Probe 22: the instrument is the measurement evidence of the QC pass."""
    a = _meter(m31, "A7QC-A")
    b = _meter(m31, "A7QC-B")
    job = ready_job(equipment_id=a.id)
    job.write({"equipment_id": b.id})  # before QC the bench may swap meters
    _as(m31, m31.qc, job).action_pass_qc()
    for user in (m31.tech, m31.qc, m31.supv):
        for value in (False, a.id):
            with refused(m31.env, UserError, "cannot be changed"):
                _as(m31, user, job).write({"equipment_id": value})
    assert job.equipment_id == b
