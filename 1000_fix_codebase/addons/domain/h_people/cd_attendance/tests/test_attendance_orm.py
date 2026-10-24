# cd_attendance live-ORM tests — P08-M02 / R06-M02 (CD-M55-01).
#
# Working-time figures are hand-computed against BLA 2006: 8h standard day
# (s.100), 10h daily ceiling (s.102/108), 11h minimum rest (s.101/105).
import json
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest import mock

import psycopg2
import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


def _record(env, emp, check_in, check_out=None):
    vals = {"employee_id": emp.id, "check_in": check_in, "source": "manual"}
    if check_out:
        vals["check_out"] = check_out
    return env["fix.attendance.record"].create(vals)


def _lock(env, start=date(2026, 1, 1), end=date(2026, 1, 31), name="Jan 2026"):
    lock = env["fix.attendance.lock"].create(
        {"name": name, "period_start": start, "period_end": end}
    )
    lock.action_lock()
    return lock


@pytest.fixture
def emp(odoo_env):
    return odoo_env["hr.employee"].create({"name": "Selim Reza"})


# --- shift templates and the roster -------------------------------------------


def test_shift_hours_must_be_within_the_day(odoo_env):
    shift = odoo_env["fix.shift.template"].create(
        {"name": "Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    assert (shift.start_hour, shift.end_hour) == (9.0, 17.0)
    for start, end in ((25.0, 5.0), (9.0, 24.0), (-1.0, 8.0)):
        with pytest.raises(ValidationError, match="within 0-24"), odoo_env.cr.savepoint():
            odoo_env["fix.shift.template"].create(
                {"name": "Bad", "start_hour": start, "end_hour": end}
            )


def test_roster_slot_label(odoo_env, emp):
    shift = odoo_env["fix.shift.template"].create(
        {"name": "Day", "start_hour": 9.0, "end_hour": 17.0}
    )
    slot = odoo_env["fix.roster.slot"].create(
        {"employee_id": emp.id, "date": date(2026, 3, 1), "shift_id": shift.id}
    )
    assert slot.display_label == "Selim Reza @ 2026-03-01"
    assert odoo_env["fix.roster.slot"].new({}).display_label == " @ "


# --- worked hours, overtime and statutory compliance ------------------------------


def test_hours_and_overtime(odoo_env, emp):
    standard = _record(odoo_env, emp, datetime(2026, 3, 1, 9, 0), datetime(2026, 3, 1, 17, 0))
    assert (standard.worked_hours, standard.overtime_hours) == (8.0, 0.0)
    assert standard.compliance_status == "compliant"
    assert standard.statutory_notes == "Standard shift compliant per BLA 2006"
    # 08:00 -> 18:30 = 10.5h worked, 2.5h beyond the 8h day: above the 10h ceiling
    long_day = _record(odoo_env, emp, datetime(2026, 3, 3, 8, 0), datetime(2026, 3, 3, 18, 30))
    assert (long_day.worked_hours, long_day.overtime_hours) == (10.5, 2.5)
    assert long_day.compliance_status == "daily_limit_exceeded"
    assert long_day.statutory_notes == (
        "BLA 2006 s.102/108 breach: 10.50h worked exceeds 10.0h daily limit"
    )
    open_shift = _record(odoo_env, emp, datetime(2026, 3, 5, 9, 0))
    assert (open_shift.worked_hours, open_shift.overtime_hours) == (0.0, 0.0)
    assert open_shift.display_label == "Selim Reza @ 2026-03-05 09:00:00"


def test_rest_interval_between_shifts(odoo_env, emp):
    _record(odoo_env, emp, datetime(2026, 3, 1, 9, 0), datetime(2026, 3, 1, 17, 0))
    # back at 01:30 next day: 8.5h rest < 11h
    short_rest = _record(odoo_env, emp, datetime(2026, 3, 2, 1, 30), datetime(2026, 3, 2, 7, 30))
    assert short_rest.compliance_status == "rest_interval_violation"
    assert short_rest.statutory_notes == (
        "BLA 2006 s.101/105 breach: 8.50h rest between shifts is under statutory 11.0h"
    )
    # 07:30 -> 19:00 the same day = 11.5h rest: compliant
    rested = _record(odoo_env, emp, datetime(2026, 3, 2, 19, 0), datetime(2026, 3, 2, 23, 0))
    assert rested.compliance_status == "compliant"
    # starting exactly when the previous shift ended is zero rest, not a breach
    back_to_back = _record(odoo_env, emp, datetime(2026, 3, 2, 23, 0), datetime(2026, 3, 3, 1, 0))
    assert back_to_back.compliance_status == "compliant"


def test_compliance_on_an_unsaved_form(odoo_env, emp):
    """The form shows the verdict before saving (onchange / new record)."""
    Record = odoo_env["fix.attendance.record"]
    blank = Record.new({})
    assert (blank.compliance_status, blank.worked_hours) == ("compliant", 0.0)
    _record(odoo_env, emp, datetime(2026, 3, 1, 9, 0), datetime(2026, 3, 1, 22, 0))
    # 22:00 -> 06:00 = 8h rest
    draft = Record.new({"employee_id": emp.id, "check_in": datetime(2026, 3, 2, 6, 0)})
    assert draft.compliance_status == "rest_interval_violation"
    assert draft.statutory_notes.startswith("BLA 2006 s.101/105 breach: 8.00h rest")


# --- the attendance lock (journey 13 gate 1) ---------------------------------------


def test_lock_only_past_periods_and_unlock(odoo_env):
    today = fields.Date.today()
    current = odoo_env["fix.attendance.lock"].create(
        {"name": "Now", "period_start": today - timedelta(days=5), "period_end": today}
    )
    with (
        pytest.raises(UserError, match="Only a fully PAST period may be locked"),
        odoo_env.cr.savepoint(),
    ):
        current.action_lock()
    assert current.state == "draft"
    lock = _lock(odoo_env)
    assert lock.state == "locked"
    assert _events(odoo_env, "attendance.locked", lock.id) == [{"period": "Jan 2026"}]
    lock.action_unlock()
    assert lock.state == "unlocked"
    assert _events(odoo_env, "attendance.unlocked", lock.id) == [{"period": "Jan 2026"}]


def test_locked_period_records_are_immutable(odoo_env, emp):
    inside = _record(odoo_env, emp, datetime(2026, 1, 10, 9, 0), datetime(2026, 1, 10, 17, 0))
    outside = _record(odoo_env, emp, datetime(2026, 2, 10, 9, 0), datetime(2026, 2, 10, 17, 0))
    _lock(odoo_env)
    with (
        pytest.raises(UserError, match="Cannot create attendance record in locked period Jan"),
        odoo_env.cr.savepoint(),
    ):
        _record(odoo_env, emp, datetime(2026, 1, 11, 9, 0))
    with (
        pytest.raises(UserError, match="is locked in period Jan 2026 - unlock before editing"),
        odoo_env.cr.savepoint(),
    ):
        inside.write({"check_out": datetime(2026, 1, 10, 18, 0)})
    with (
        pytest.raises(UserError, match="Cannot delete attendance record in locked period Jan"),
        odoo_env.cr.savepoint(),
    ):
        inside.unlink()
    # chatter / activity bookkeeping is not an attendance edit
    inside.write({"activity_ids": []})
    assert inside.check_out == datetime(2026, 1, 10, 17, 0)
    # records outside every locked period stay editable and deletable
    outside.write({"check_out": datetime(2026, 2, 10, 18, 0)})
    assert outside.worked_hours == 9.0
    outside.unlink()
    assert not outside.exists()


def test_create_without_check_in_is_rejected_by_the_database(odoo_env, emp):
    with (
        pytest.raises(psycopg2.errors.NotNullViolation),
        odoo_env.cr.savepoint(),
        mock.patch("odoo.sql_db._logger"),
    ):
        odoo_env["fix.attendance.record"].create({"employee_id": emp.id})


def test_checkout(odoo_env, emp):
    now = fields.Datetime.now()
    rec = _record(odoo_env, emp, now - timedelta(hours=9))
    with mock.patch.object(fields.Datetime, "now", return_value=now):
        rec.action_checkout()
    assert rec.check_out == now
    assert (rec.worked_hours, rec.overtime_hours) == (9.0, 1.0)
    assert _events(odoo_env, "attendance.checked_out", rec.id) == [
        {"employee": "Selim Reza", "hours": 9.0, "compliance": "compliant"}
    ]
    with pytest.raises(UserError, match="Already checked out"), odoo_env.cr.savepoint():
        rec.action_checkout()


# --- INT-041 biometric devices ------------------------------------------------------


@pytest.fixture
def device(odoo_env):
    return odoo_env["fix.biometric.device"].create(
        {"device_id": "ZK-DHK-001", "name": "Mirpur gate"}
    )


def test_device_identifier_is_unique(odoo_env, device):
    assert (device.model_type, device.status, device.active) == ("INT-041", "online", True)
    with (
        pytest.raises(psycopg2.errors.UniqueViolation),
        odoo_env.cr.savepoint(),
        mock.patch("odoo.sql_db._logger"),
    ):
        odoo_env["fix.biometric.device"].create({"device_id": "ZK-DHK-001", "name": "Clone"})


def test_punch_rejects_unknown_employee(device):
    with (
        pytest.raises(UserError, match="Invalid employee reference for biometric ingest: 999999"),
        device.env.cr.savepoint(),
    ):
        device.action_ingest_punch(999999, datetime(2026, 3, 1, 9, 0))


def test_check_in_and_check_out_punches(odoo_env, device, emp):
    check_in = device.action_ingest_punch(emp.id, "2026-03-01 09:00:00")
    assert (check_in.employee_id, check_in.check_in) == (emp, datetime(2026, 3, 1, 9, 0))
    assert (check_in.source, check_in.device_ref) == ("biometric", "ZK-DHK-001")
    assert check_in.company_id == device.company_id
    assert device.last_sync_at
    # the check-out closes the open record (employee passed as a record)
    closed = device.action_ingest_punch(emp, datetime(2026, 3, 1, 17, 30), punch_type="check_out")
    assert closed == check_in
    assert (closed.check_out, closed.worked_hours, closed.overtime_hours) == (
        datetime(2026, 3, 1, 17, 30),
        8.5,
        0.5,
    )
    # a check-out with no open record is kept as a zero-length punch
    orphan = device.action_ingest_punch(emp, datetime(2026, 3, 2, 18, 0), punch_type="check_out")
    assert orphan != check_in
    assert orphan.check_in == orphan.check_out == datetime(2026, 3, 2, 18, 0)
    assert orphan.worked_hours == 0.0


def test_punch_into_locked_period_is_rejected(odoo_env, device, emp):
    _lock(odoo_env)
    with (
        pytest.raises(UserError, match="Attendance period Jan 2026 is locked"),
        odoo_env.cr.savepoint(),
    ):
        device.action_ingest_punch(emp.id, datetime(2026, 1, 15, 9, 0))


class _FakeResidencyClient:
    def __init__(self):
        self.store = {}

    def put(self, key, value):
        self.store[key] = value
        return {"value_kind": "biometric"}


def test_biometric_template_is_routed_to_z4_never_stored_regionally(odoo_env, device):
    user = odoo_env["res.users"].create({"name": "Selim Login", "login": "selim.att.t"})
    with_user = odoo_env["hr.employee"].create({"name": "Selim Reza", "user_id": user.id})
    z4 = _FakeResidencyClient()
    with mock.patch("libs.py.fix_residency.get_client", return_value=z4):
        device.action_ingest_punch(
            with_user.id, datetime(2026, 3, 1, 9, 0), biometric_template="TEMPLATE-BYTES-01"
        )
    doc = odoo_env["fix.identity.document"].search([("partner_id", "=", user.partner_id.id)])
    assert doc.document_type == "biometric"
    assert doc.company_id == device.company_id
    assert doc.residency_ref
    # the template went to Z4 under the pointer; the regional row holds no value
    assert z4.store == {f"party identity:{doc.residency_ref}": "TEMPLATE-BYTES-01"}
    odoo_env.flush_all()
    odoo_env.cr.execute("SELECT document_number FROM fix_identity_document WHERE id = %s", [doc.id])
    assert odoo_env.cr.fetchone()[0] is None


def test_biometric_template_without_any_party_is_not_stored(odoo_env, device, emp):
    z4 = _FakeResidencyClient()
    before = odoo_env["fix.identity.document"].search_count([])
    with mock.patch("libs.py.fix_residency.get_client", return_value=z4):
        rec = device.action_ingest_punch(
            emp.id, datetime(2026, 3, 1, 9, 0), biometric_template="TEMPLATE-BYTES-02"
        )
    assert rec.check_in == datetime(2026, 3, 1, 9, 0)
    assert odoo_env["fix.identity.document"].search_count([]) == before
    assert z4.store == {}


# --- M02 -> M55: roster-based availability on the assignment path ------------------


@pytest.fixture
def wo_ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    entity = env["fix.entity"].create(
        {"code": "ATTT", "legal_name": "Attendance Test Ltd", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"code": "AT1", "name": "Uttara", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "Att Brand", "code": "ATTB"})
    model = env["fix.device.model"].create(
        {"name": "Note 13", "brand_id": brand.id, "device_type": "smartphone"}
    )
    device = env["fix.device"].create({"device_model_id": model.id, "branch_id": branch.id})
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": env["res.partner"].create({"name": "Customer"}).id,
            "branch_id": branch.id,
            "fault_description": "No power",
        }
    )
    tech = env["hr.employee"].create({"name": "Tech Rafiq"})
    shift = env["fix.shift.template"].create({"name": "Day", "start_hour": 9.0, "end_hour": 18.0})

    def work_order(**vals):
        # certification is M22's gate (cd_competency); waived here to isolate M55
        return env["fix.work.order"].create(
            {"order_id": order.id, "certification_waiver": True, **vals}
        )

    return SimpleNamespace(env=env, tech=tech, shift=shift, work_order=work_order)


def _slot(ctx, on_leave=False):
    return ctx.env["fix.roster.slot"].create(
        {
            "employee_id": ctx.tech.id,
            "date": fields.Date.today(),
            "shift_id": ctx.shift.id,
            "on_leave": on_leave,
        }
    )


def test_assignment_without_roster_slot_is_blocked(wo_ctx):
    wo = wo_ctx.work_order()
    with (
        pytest.raises(UserError, match="Tech Rafiq has no roster slot for"),
        wo_ctx.env.cr.savepoint(),
    ):
        wo.write({"technician_id": wo_ctx.tech.id})


def test_assignment_of_technician_on_leave_is_blocked(wo_ctx):
    _slot(wo_ctx, on_leave=True)
    wo = wo_ctx.work_order()
    with (
        pytest.raises(UserError, match="Tech Rafiq is on approved leave"),
        wo_ctx.env.cr.savepoint(),
    ):
        wo.write({"technician_id": wo_ctx.tech.id})


def test_rostered_technician_is_assignable(wo_ctx):
    _slot(wo_ctx)
    wo = wo_ctx.work_order()
    wo.write({"technician_id": wo_ctx.tech.id})
    assert wo.technician_id == wo_ctx.tech
    # writes that do not assign a technician run no roster check
    wo.write({"notes": "customer called"})
    assert wo.notes == "customer called"


def test_unassigned_work_order_is_trivially_available(wo_ctx):
    assert wo_ctx.work_order().action_check_technician_availability() is True


def test_every_work_order_of_a_batch_is_checked(wo_ctx):
    """Regression: the loop returned after the first record."""
    _slot(wo_ctx)
    unassigned = wo_ctx.work_order()
    assigned = wo_ctx.work_order()
    assigned.write({"technician_id": wo_ctx.tech.id})
    wo_ctx.env["fix.roster.slot"].search([("employee_id", "=", wo_ctx.tech.id)]).unlink()
    with pytest.raises(UserError, match="Tech Rafiq has no roster slot"), wo_ctx.env.cr.savepoint():
        (unassigned | assigned).action_check_technician_availability()
