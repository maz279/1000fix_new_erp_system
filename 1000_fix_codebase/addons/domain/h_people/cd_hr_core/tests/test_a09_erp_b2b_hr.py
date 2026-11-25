# A09 ERP builder stream B2b — the HR lifecycle fixes: M21-F25 (the s.31
# service certificate clocked from the worker's application, re-issuable on a
# later application), M21-F13 (a running s.24 suspension derived on the
# employee master), X-F2 (exit clearance refuses while the leaver holds open
# work) and the M21-F20 readiness notes (the unrated settings named).
import itertools
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_competency.tests.certify import (
    certify_for_dispatch,
    licence_for_driving,
)
from odoo.exceptions import AccessError, UserError

REFUSED = (AccessError, UserError)
_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "B2b HR User %d" % n,
                "login": "a09-b2b-hr-%d@test.local" % n,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    c = itertools.count(1)
    w = type(
        "W",
        (),
        {
            "env": env,
            "plain": _user(env),
            "hro": _user(env, "cd_hr_core.group_hr_officer"),
            "hro2": _user(env, "cd_hr_core.group_hr_officer"),
            "it": _user(env, "cd_hr_core.group_clearance_it"),
            "fin": _user(env, "cd_hr_core.group_hr_finance"),
            "assets": _user(env, "cd_hr_core.group_clearance_assets"),
            "today": fields.Date.context_today(env.user),
        },
    )()

    def _emp(**vals):
        n = next(c)
        return env["hr.employee"].create({"name": "B2b HR Employee %d" % n, **vals})

    def _contract(emp, **vals):
        base = {
            "employee_id": emp.id,
            "company_id": env.company.id,
            "contract_type": "permanent",
            "joining_date": date(2020, 1, 1),
            "basic_monthly": 30000.0,
        }
        base.update(vals)
        return env["fix.employment.contract"].create(base)

    def _exit(emp, **vals):
        return env(user=w.hro.id)["fix.hr.exit"].create(
            {"employee_id": emp.id, "exit_type": "contract_end", **vals}
        )

    def _cleared(ex):
        ex.with_user(w.hro2).action_confirm_notice()
        ex.with_user(w.it).action_clear_it()
        ex.with_user(w.fin).action_clear_finance()
        handover = env["fix.hr.exit.handover"].create(
            {"exit_id": ex.id, "successor_id": _emp().id, "open_work": "none"}
        )
        handover.action_hand_over()
        handover.action_accept()
        ex.with_user(w.hro2).action_clear_hr()
        ex.with_user(w.assets).action_clear_assets()
        ex.with_user(w.hro2).action_clear()
        return ex

    w._emp, w._contract, w._exit, w._cleared = _emp, _contract, _exit, _cleared
    return w


# ---- M21-F25: the s.31 service certificate on application ---------------------


@pytest.fixture
def sun_thu(w):
    """A Sun-Thu calendar: the r.31 clock's working days (weekend Fri-Sat)."""
    return w.env["resource.calendar"].create(
        {
            "name": "B2b r31 Sun-Thu",
            "company_id": w.env.company.id,
            "attendance_ids": [
                (0, 0, {"name": d, "dayofweek": str(dw), "hour_from": 8.0, "hour_to": 16.0})
                for d, dw in (
                    ("Sunday", 6),
                    ("Monday", 0),
                    ("Tuesday", 1),
                    ("Wednesday", 2),
                    ("Thursday", 3),
                )
            ],
        }
    )


def test_certificate_clock_runs_from_the_application(w, sun_thu):
    emp = w._emp(resource_calendar_id=sun_thu.id)
    ex = w._exit(emp, last_working_day=w.today - timedelta(days=1))
    w._cleared(ex)
    draft_ex = w._exit(w._emp(), last_working_day=w.today + timedelta(days=5))
    with pytest.raises(UserError, match="confirmed exit"), w.env.cr.savepoint():
        draft_ex.with_user(w.hro2).action_record_service_certificate_application()
    ex.with_user(w.hro2).action_record_service_certificate_application("2026-11-01")
    w.env.invalidate_all()
    assert ex.service_certificate_applied_on == date(2026, 11, 1)
    # 15 working days after Sun 1 Nov 2026, Fri/Sat off, no company leaves:
    # 2-5, 8-12, 15-19, 22 Nov -> due Sunday 22 November 2026 (BLR r.31)
    assert ex.service_certificate_due_date == date(2026, 11, 22)


def test_certificate_reissue_follows_a_later_application(w):
    emp = w._emp()
    ex = w._exit(emp, last_working_day=w.today - timedelta(days=1))
    w._cleared(ex)
    # an early application, then the convenience issue (no new application)
    ex.with_user(w.hro2).action_record_service_certificate_application(
        fields.Date.to_string(w.today - timedelta(days=10))
    )
    ex.with_user(w.hro2).action_issue_service_certificate()
    first = ex.service_certificate_id
    assert first and first.doc_type == "service_certificate"
    # the OLD application does not re-open the issue
    with pytest.raises(UserError, match="already has"), w.env.cr.savepoint():
        ex.with_user(w.hro).action_issue_service_certificate()
    # a later application does (BLR r.31: issue within 15 days of THE application)
    ex.with_user(w.hro2).action_record_service_certificate_application()
    ex.with_user(w.hro2).action_issue_service_certificate()
    second = ex.service_certificate_id
    assert second.id != first.id, "a later application re-opens the issue (r.31)"
    assert second.issued_on == w.today


def test_certificate_application_is_hr_only_and_never_future(w):
    emp = w._emp()
    ex = w._exit(emp, last_working_day=w.today - timedelta(days=1))
    ex.with_user(w.hro2).action_confirm_notice()
    with pytest.raises(REFUSED), w.env.cr.savepoint():
        ex.with_user(w.plain).action_record_service_certificate_application()
    with pytest.raises(UserError, match="future"), w.env.cr.savepoint():
        ex.with_user(w.hro2).action_record_service_certificate_application(
            fields.Date.to_string(w.today + timedelta(days=1))
        )
    ex.with_user(w.hro2).action_record_service_certificate_application()
    assert ex.service_certificate_applied_on == w.today


# ---- M21-F13: a running suspension derived on the employee master ------------


def test_suspension_is_derived_on_the_employee_master(w):
    # the master's Date of Joining (the field the M21 form captures) is in the
    # past, and an ACTIVE contract backs it: the master reads "active"
    emp = w._emp(joining_date=w.today - timedelta(days=400))
    # an ACTIVE contract is what makes the master pay-ready; the suspension is
    # derived on top of the master status
    w._contract(emp, state="active")
    w.env.invalidate_all()
    assert emp.employment_status == "active"
    case = w.env["fix.hr.disciplinary.case"].create(
        {
            "company_id": w.env.company.id,
            "employee_id": emp.id,
            "allegation": "B2b: test allegation for the suspension derivation",
            "misconduct_category": "other",
        }
    )
    case.with_user(w.hro).action_charge()
    # M21-F20: the unrated subsistence setting blocks the suspension, naming it
    w.env.company.write({"fix_hr_suspension_subsistence_pct": 0.0})
    with pytest.raises(UserError, match="fix_hr_suspension_subsistence_pct"):
        case.with_user(w.hro).action_suspend(days=10)
    w.env.company.write({"fix_hr_suspension_subsistence_pct": 40.0})
    case.with_user(w.hro).action_suspend(days=10)
    w.env.invalidate_all()
    assert emp.fix_suspension_active, "searchable flag for attendance/dispatch"
    assert emp.fix_suspension_case_id == case
    assert emp.employment_status == "suspended", "M21-F13: visible on the master"
    assert emp in w.env["hr.employee"].search([("fix_suspension_active", "=", True)])
    case.with_user(w.hro).action_end_suspension()
    w.env.invalidate_all()
    assert not emp.fix_suspension_active
    assert emp.employment_status == "active"


# ---- X-F2: a leaver does not clear while holding work -------------------------


@pytest.fixture
def work(w):
    """An open work order held by a technician (M02), through the real
    service-order chain."""
    env = w.env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "B2BXF2", "legal_name": "B2b X-F2 Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "B2b X-F2 Branch",
            "code": "B2BXF2",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "B2bBrand", "code": "B2BXB"})
    model = env["fix.device.model"].create({"name": "B2b Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "B2b Customer", "phone": "01711000999"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-B2B-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No display",
        }
    )
    return order


def test_clearance_refuses_while_a_work_order_is_open(w, work):
    tech = w._emp()
    w._contract(tech)
    # FR-LMS-039: a technician holds the job only with a dispatch-gating cert
    certify_for_dispatch(w.env, tech)
    wo = w.env["fix.work.order"].create(
        {"order_id": work.id, "technician_id": tech.id, "state": "assigned"}
    )
    ex = w._exit(tech, last_working_day=w.today - timedelta(days=1))
    ex.with_user(w.hro2).action_confirm_notice()
    with pytest.raises(UserError, match=wo.name), w.env.cr.savepoint():
        ex.with_user(w.assets).action_clear_assets()
    # the direct check names what is still open
    with pytest.raises(UserError, match="open work order"), w.env.cr.savepoint():
        ex._fix_refuse_open_work()
    # once the work order closes, the refusal goes
    wo.write({"state": "completed"})
    ex.with_user(w.assets).action_clear_assets()
    ex.with_user(w.it).action_clear_it()
    ex.with_user(w.fin).action_clear_finance()
    handover = w.env["fix.hr.exit.handover"].create(
        {"exit_id": ex.id, "successor_id": w._emp().id, "open_work": "none"}
    )
    handover.action_hand_over()
    handover.action_accept()
    ex.with_user(w.hro2).action_clear_hr()
    ex.with_user(w.hro2).action_clear()
    assert ex.state == "cleared"


def test_clearance_refuses_while_a_vehicle_stays_booked(w):
    env = w.env
    tech = w._emp()
    w._contract(tech)
    # BRU-HSE-07: a vehicle-based booking needs the technician's licence on file
    licence_for_driving(env, tech)
    brand = env["fleet.vehicle.model.brand"].create({"name": "B2b Vans"})
    model = env["fleet.vehicle.model"].create(
        {"name": "B2b Van M", "brand_id": brand.id, "vehicle_type": "car"}
    )
    van = env["fleet.vehicle"].create({"model_id": model.id, "license_plate": "B2B-1200"})
    # M46's dispatch gate (BRU-FLT-xx) refuses a van whose document register
    # holds no valid fitness/insurance/tax: record them, as the fleet flow does
    for doc_type, valid_days in (("fitness", 30), ("insurance", 60), ("tax", 90)):
        env["fix.vehicle.document"].create(
            {
                "vehicle_id": van.id,
                "doc_type": doc_type,
                "valid_to": w.today + timedelta(days=valid_days),
            }
        )
    booking = env["fix.vehicle.assignment"].create(
        {"vehicle_id": van.id, "date": w.today + timedelta(days=1), "technician_id": tech.id}
    )
    ex = w._exit(tech, last_working_day=w.today - timedelta(days=1))
    ex.with_user(w.hro2).action_confirm_notice()
    with pytest.raises(UserError, match=booking.name), w.env.cr.savepoint():
        ex.with_user(w.assets).action_clear_assets()
    booking.action_release("leaver cleared the vehicle")
    ex.with_user(w.assets).action_clear_assets()


def test_action_clear_also_rechecks_open_work(w, work):
    # work assigned AFTER the assets tick still blocks the final clear
    tech = w._emp()
    w._contract(tech)
    certify_for_dispatch(w.env, tech)  # FR-LMS-039 dispatch gate
    ex = w._exit(tech, last_working_day=w.today - timedelta(days=1))
    ex.with_user(w.hro2).action_confirm_notice()
    ex.with_user(w.assets).action_clear_assets()
    ex.with_user(w.it).action_clear_it()
    ex.with_user(w.fin).action_clear_finance()
    handover = w.env["fix.hr.exit.handover"].create(
        {"exit_id": ex.id, "successor_id": w._emp().id, "open_work": "none"}
    )
    handover.action_hand_over()
    handover.action_accept()
    ex.with_user(w.hro2).action_clear_hr()
    wo = w.env["fix.work.order"].create(
        {"order_id": work.id, "technician_id": tech.id, "state": "pending"}
    )
    with pytest.raises(UserError, match=wo.name), w.env.cr.savepoint():
        ex.with_user(w.hro2).action_clear()
    wo.write({"state": "cancelled"})
    ex.with_user(w.hro2).action_clear()
    assert ex.state == "cleared"
