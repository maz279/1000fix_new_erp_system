"""A07 ERP audit (2026-11-20), M45 findings carried by the spine (stream S2):
M45-10 exit clearance against the register custodian, M45-13 / D7(c) the
QC-instrument gate scoped to measurement QC with a QM waiver, M45-11 / M45-23
the escalation ladders, M45-20 the impact on open warranty claims, M45-21 the
M06 erasure before a data-bearing item is disposed of. Live ORM, rolled back.
"""

from __future__ import annotations

import itertools
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workshop.tests import test_a02_p0_m31 as a02
from odoo.addons.cd_workshop.tests import test_a07_p0_m45_qc as p0
from odoo.addons.cd_workshop.tests._m45_decided import (  # noqa: F401 - autouse fixture
    calibrations_decided,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
ROLE_QM = "cd_equipment_register.group_quality_manager"
QC_PARAM = "cd_workshop.qc_requires_instrument"
_SEQ = itertools.count(1)

m31 = a02.m31
ready_job = p0.ready_job
_as = a02._as


def refused(env, fn, match=None):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        env.invalidate_all()
        if match and match not in str(exc):
            raise AssertionError("refused for another reason: %s" % exc) from exc
        return True
    return False


def _user(env, tag, groups=()):
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A7ERPS %s %d" % (tag, n),
                "login": "a7erps.%s.%d@a07.test" % (tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    user.employee_id = env["hr.employee"].create(
        {"name": "A7ERPS %s %d" % (tag, n), "user_id": user.id}
    )
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["res.users"].with_context(tz="Asia/Dhaka"))
    return x


# ============================================================ M45-10
def test_m45_10_exit_clearance_refuses_while_the_leaver_is_a_register_custodian(c):
    leaver = c.env["hr.employee"].create({"name": "A7ERPS leaver"})
    kit = c.env["fix.equipment"].create(
        {"code": "A7ERPS-KIT", "name": "Personal toolkit", "custodian_id": leaver.id}
    )
    ex = c.env["fix.hr.exit"].create(
        {
            "employee_id": leaver.id,
            "notice_date": c.today - timedelta(days=40),
            "last_working_day": c.today + timedelta(days=5),
            "clearance_it": True,
            "clearance_finance": True,
            "clearance_hr": True,
            "clearance_assets": True,
        }
    )
    ex.action_confirm_notice()
    assert refused(c.env, ex.action_clear, "A7ERPS-KIT")
    # a retired item holds nobody accountable
    kit._guarded().write({"operational_status": "retired", "retired_on": c.today})
    ex.action_clear()
    assert ex.state == "cleared"


# ============================================================ M45-13 / D7(c)
def _measurement_protocol(env, job):
    device = job.device_id or job.order_id.device_id
    model = device.device_model_id.sudo()
    if not model.device_type:
        selection = model._fields["device_type"]._description_selection(env)
        model.write({"device_type": selection[0][0]})
    protocol = env["fix.workshop.test.protocol"].create(
        {
            "code": "A7ERPS-PR-%d" % next(_SEQ),
            "name": "Charging rail check",
            "device_type": device.device_type,
            "step_ids": [
                (
                    0,
                    0,
                    {
                        "name": "5V rail",
                        "unit": "V",
                        "has_limits": True,
                        "lower_limit": 4.75,
                        "upper_limit": 5.25,
                    },
                )
            ],
        }
    )
    assert protocol.requires_measuring_instrument
    return protocol


def test_d7c_the_switch_binds_only_measurement_qc(m31, ready_job):
    m31.env["ir.config_parameter"].sudo().set_param(QC_PARAM, "1")
    # no measuring procedure for the job: QC passes without an instrument
    job = ready_job()
    _as(m31, m31.qc, job).action_pass_qc()
    assert job.state == "ready"
    # a procedure with a measured step: the inspector names an instrument
    job = ready_job()
    _measurement_protocol(m31.env, job)
    assert refused(m31.env, lambda: _as(m31, m31.qc, job).action_pass_qc(), "BRU-EAM-15")
    assert job.state == "qc_pending"


def test_d7c_a_quality_manager_waives_the_instrument_while_none_qualifies(
    m31, ready_job, monkeypatch
):
    m31.env["ir.config_parameter"].sudo().set_param(QC_PARAM, "1")
    job = ready_job()
    _measurement_protocol(m31.env, job)
    qm = _user(m31.env, "qm", [ROLE_QM])
    Job = type(m31.env["fix.workshop.job"])
    assert refused(
        m31.env, lambda: job.with_user(m31.qc).action_waive_qc_instrument("none"), "Quality Manager"
    )
    assert refused(m31.env, lambda: job.with_user(qm).action_waive_qc_instrument(""), "why")
    # a fit instrument exists: name it, do not waive
    p0._meter(m31, "A7ERPS-FIT")
    assert refused(m31.env, lambda: job.with_user(qm).action_waive_qc_instrument("none"), "name it")
    monkeypatch.setattr(Job, "_m45_qualifying_instruments", lambda self: m31.env["fix.equipment"])
    job.with_user(qm).action_waive_qc_instrument("No calibrated DMM registered at the depot yet")
    assert job.qc_instrument_waiver_by_id == qm and "DMM" in job.qc_instrument_waiver_reason
    assert refused(m31.env, lambda: job.with_user(qm).write({"qc_instrument_waiver_reason": "x"}))
    _as(m31, m31.qc, job).action_pass_qc()
    assert job.state == "ready"


# ============================================================ M45-23 / M45-11
def test_m45_23_custody_overdue_climbs_holder_branch_manager_quality_manager(c):
    holder = _user(c.env, "holder")
    manager = _user(c.env, "branch-manager")
    stranger = _user(c.env, "stranger")
    e = c.env["fix.equipment"].create({"code": "A7ERPS-LAD", "name": "Ladder meter"})
    issue = c.env["fix.equipment.issue"].create(
        {"equipment_id": e.id, "custodian_id": holder.employee_id.id}
    )
    Alert = c.env["fix.asset.alert"]

    def raise_level(level):
        Alert.consume_asset_alert(
            {
                "event_type": "equipment.custody_overdue",
                "aggregate": "fix.equipment.issue",
                "aggregate_id": issue.id,
                "payload": {
                    "escalation_level": level,
                    "holder_user_id": holder.id,
                    "branch_manager_id": manager.id,
                },
            }
        )
        return Alert.search(
            [
                ("event_type", "=", "equipment.custody_overdue"),
                ("res_id", "=", issue.id),
                ("state", "=", "open"),
            ]
        )

    first = raise_level(1)
    assert len(first) == 1 and first.addressee_ids == holder
    second = raise_level(2) - first
    assert second.addressee_ids == manager
    assert second.role_group_xmlid == "cd_facility.group_branch_operations_lead"
    third = raise_level(3) - first - second
    assert third.role_group_xmlid == ROLE_QM and not third.addressee_ids
    assert refused(c.env, lambda: second.with_user(stranger).action_acknowledge(), "role")
    second.with_user(manager).action_acknowledge()
    assert second.state == "acknowledged"
    # a repeat of a level counts on its own row
    raise_level(2)
    assert second.raise_count == 1


def test_m45_11_calibration_due_escalates_to_the_quality_manager(c):
    e = c.env["fix.equipment"].create({"code": "A7ERPS-DUE", "name": "Due meter"})
    event = {
        "event_type": "equipment.calibration_due",
        "aggregate": "fix.equipment",
        "aggregate_id": e.id,
        "payload": {
            "due_date": str(c.today + timedelta(days=10)),
            "horizon_days": 15,
            "escalate_to": "quality_manager",
        },
    }
    c.env["fix.maintenance.demand"].consume_equipment_calibration_due(event)
    alert = c.env["fix.asset.alert"].search(
        [("event_type", "=", "equipment.calibration_due"), ("res_id", "=", e.id)]
    )
    assert alert.role_group_xmlid == ROLE_QM


# ============================================================ M45-21
def test_m45_21_a_data_bearing_item_waits_for_its_m06_erasure(c):
    qm = _user(c.env, "qm-erase", [ROLE_QM])
    cat = (
        c.env["fix.equipment.category"]
        .with_user(qm)
        .create({"code": "A7ERPS-IT", "name": "Laptops", "classification": "it_asset"})
    )
    laptop = c.env["fix.equipment"].create(
        {"code": "A7ERPS-LT", "name": "Bench laptop", "category_id": cat.id, "serial_no": "LT-SN-1"}
    )
    laptop._guarded().write({"operational_status": "retired", "retired_on": c.today})
    retirement = (
        c.env["fix.equipment.retirement"]
        .with_user(qm)
        .create({"equipment_id": laptop.id, "basis": "obsolete", "justification": "end of life"})
    )
    assert retirement.state == "approved" and retirement.data_bearing
    request = retirement.wipe_request_id
    assert request and request.serial_number == "LT-SN-1" and request.state == "requested"
    retirement.with_user(qm).write(
        {
            "disposal_route": "ewaste",
            "disposal_ref": "EW-1",
            "erasure_certificate_ref": "typed-cert",
        }
    )
    # a typed reference no longer lets it leave
    assert refused(c.env, lambda: retirement.with_user(qm).action_dispose(), "certified")
    assert retirement.state == "approved"


# ============================================================ M45-20
def test_m45_20_an_impact_assessment_reaches_the_open_warranty_claims(m31):
    env = m31.env
    meter = p0._meter(m31, "A7ERPS-IMP")
    job = m31.job()
    order = job.order_id
    env["fix.equipment.usage"].m45_record_qc_use(
        meter, job.name, "pass", source=job, service_order_ref=order.name
    )
    claim = env["fix.warranty.claim"].create(
        {
            "operating_unit_id": env["operating.unit"].search([], limit=1).id,
            "service_order_id": order.id,
            "brand_id": order.device_id.brand_id.id,
            "claim_amount": 3000.0,
        }
    )
    today = fields.Date.context_today(env["fix.equipment"].with_context(tz="Asia/Dhaka"))
    fail = env["fix.calibration"].create(
        {
            "equipment_id": meter.id,
            "calibrated_on": today,
            "next_due": today + timedelta(days=1),
            "standard_ref": "STD",
            "result": "fail",
        }
    )
    impact = fail.impact_id
    env["fix.service.order.recheck"].consume_impact_assessment_raised(
        {"aggregate_id": impact.id, "payload": {}}
    )
    assert claim in impact.affected_claim_ids
    assert any(impact.name in (m.body or "") for m in claim.message_ids)
    # idempotent
    env["fix.service.order.recheck"].consume_impact_assessment_raised(
        {"aggregate_id": impact.id, "payload": {}}
    )
    assert len(impact.affected_claim_ids) == 1
