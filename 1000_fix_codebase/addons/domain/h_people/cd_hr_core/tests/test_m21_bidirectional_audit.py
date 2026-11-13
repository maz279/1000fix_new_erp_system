# ruff: noqa: F811 - the acceptance suite's fixtures are imported by name
# M21 bidirectional audit (13 Nov 2026): one test per defect the audit found,
# each run against the live ORM as the role that meets it in the workspace.
# The fixtures are the A09 M21 acceptance suite's (test_a09_m21_controls).
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_hr_core.tests.test_a09_m21_controls import (  # noqa: F401 - fixtures
    _approve,
    _cleared,
    _contract,
    _emp,
    _events,
    _exit,
    _rpc_write,
    _user,
    call,
    payroll_hook,
    residency,
    w,
)
from odoo.addons.cd_p03_portal.controllers.a09 import m21 as m21_surfaces
from odoo.exceptions import UserError, ValidationError


def _today(env):
    return fields.Date.context_today(env.user)


def _signed_active(c, emp, **vals):
    """An active contract, as activation leaves it (sudo: the sign-off path
    is the acceptance suite's)."""
    return _contract(c.env, emp, state="active", **vals)


# ============================================================ employee master
def test_saving_an_employee_of_an_over_filled_position_is_not_refused(w):
    """F6: the form echoes position_id; an unchanged one re-ran the seat
    constraint, so no employee of an over-filled position could be saved."""
    seat = w.env["fix.org.position"].create({"name": "M21 Audit Seat", "headcount": 1})
    a, b = _emp(w.env), _emp(w.env)
    a.write({"position_id": seat.id})
    # the over-filled state the fix_real import left behind (raw SQL)
    w.env.cr.execute("UPDATE hr_employee SET position_id = %s WHERE id = %s", (seat.id, b.id))
    b.invalidate_recordset()
    _rpc_write(w.env, w.hro, "hr.employee", b, {"position_id": seat.id, "job_title": "Renamed"})
    assert b.job_title == "Renamed"
    # a real new claim on the full seat is still refused (BRU-HCM-10)
    with pytest.raises(ValidationError, match="full"), w.env.cr.savepoint():
        _rpc_write(w.env, w.hro, "hr.employee", _emp(w.env), {"position_id": seat.id})


def test_an_unchanged_save_announces_no_move(w):
    """F7: every save posted department/position/band and published
    employee.moved, opening an IT access review each time."""
    dept = w.env["hr.department"].create({"name": "M21 Audit Dept"})
    emp = _emp(w.env, department_id=dept.id)
    before = len(_events(w.env, "employee.moved", emp.id))
    emp.write({"department_id": dept.id, "job_band": emp.job_band, "job_title": "Same"})
    assert len(_events(w.env, "employee.moved", emp.id)) == before
    other = w.env["hr.department"].create({"name": "M21 Audit Dept 2"})
    emp.write({"department_id": other.id})
    assert len(_events(w.env, "employee.moved", emp.id)) == before + 1


def test_workplace_category_is_stored(w):
    """The form offered a workplace category the server refused as read-only
    (it was hr's computed work_location_type): it is a stored field now."""
    emp = _emp(w.env)
    _rpc_write(w.env, w.hro, "hr.employee", emp, {"workplace_category": "field_mobile"})
    emp.invalidate_recordset()
    assert emp.workplace_category == "field_mobile"
    # hr's own computed field keeps its own selection
    assert "home" in dict(emp._fields["work_location_type"].selection)


def test_recorded_salary_account_changes_only_through_a_master_change(w):
    """F4: without an active contract the bank/MFS/identity gate was open, so
    an officer could overwrite any of the 504 imported employees' accounts."""
    emp = _emp(w.env)
    # first capture on the form is allowed
    _rpc_write(w.env, w.hro, "hr.employee", emp, {"mfs_provider": "bkash"})
    _rpc_write(w.env, w.hro, "hr.employee", emp, {"mfs_account_number": "01711000001"})
    with pytest.raises(UserError, match="Employee Master Change"):
        _rpc_write(w.env, w.hro, "hr.employee", emp, {"mfs_account_number": "01711000002"})
    assert emp.sudo().mfs_account_number == "01711000001"
    assert "mfs_account_number" in emp._fix_form_locked_fields()


def test_contract_activation_keeps_the_master_terms_in_step(w):
    """F2: Form 6 printed the master's wage fields, which nothing maintained."""
    emp = _emp(w.env)
    contract = _contract(
        w.env,
        emp,
        contract_type="probation",
        basic_monthly=18000.0,
        house_rent=9000.0,
        joining_date=_today(w.env) - timedelta(days=30),
        probation_end=_today(w.env) + timedelta(days=60),
    )
    contract._fix_activate()
    emp.invalidate_recordset()
    assert emp.sudo().basic_wage == 18000.0 and emp.sudo().wage == 27000.0
    assert emp.employment_type == "probationary"
    assert emp.joining_date == _today(w.env) - timedelta(days=30)
    doc = emp.with_user(w.hro).action_generate_form6_appointment()
    import base64

    text = base64.b64decode(doc.sudo().file_data).decode()
    assert "BDT 18,000.00" in text and "BDT 27,000.00" in text and "Probation" in text


def test_form6_refuses_an_employee_without_a_contract(w):
    with pytest.raises(UserError, match="no employment contract"):
        _emp(w.env).with_user(w.hro).action_generate_form6_appointment()


def test_generating_form7_does_not_endorse_the_service_book(w):
    """F3: the generated, unsigned draft stamped form7_endorsed_on and cleared
    the 15-day overdue flag; endorsement is the verified signed scan."""
    emp = _emp(w.env, form7_last_event_date=_today(w.env) - timedelta(days=30))
    assert emp.form7_update_overdue
    doc = emp.with_user(w.hro).action_generate_form7_service_book()
    emp.invalidate_recordset()
    assert emp.form7_update_overdue and not emp.form7_endorsed_on
    # the signed scan goes onto the generated entry, then a second person verifies
    doc.with_user(w.hro2).write({"file_data": b"c2lnbmVk", "file_name": "signed.pdf"})
    assert not doc.generated
    with pytest.raises(UserError, match="uploaded"):
        doc.with_user(w.hro2).action_verify()
    doc.with_user(w.hro3).action_verify()
    emp.invalidate_recordset()
    assert emp.form7_endorsed_on and not emp.form7_update_overdue


def test_a_new_file_needs_a_new_acknowledgement(w):
    emp = w.me  # w.plain's own employee record
    doc = w.env(user=w.hro.id)["fix.hr.document"].create(
        {"employee_id": emp.id, "doc_type": "nda", "file_data": b"YQ==", "file_name": "a.pdf"}
    )
    doc.with_user(w.plain).action_acknowledge()
    assert doc.acknowledged
    doc.with_user(w.hro).write({"file_data": b"Yg==", "file_name": "b.pdf"})
    assert not doc.acknowledged


# ============================================================ movement
def _move(c, emp, **vals):
    return c.env(user=c.hro.id)["fix.hr.transfer"].create(
        {
            "employee_id": emp.id,
            "movement_type": "promotion",
            "to_manager_id": c.dmgr_emp.id,
            **vals,
        }
    )


def test_gross_only_raise_is_refused(w):
    """T1: proposed_gross reached the master's wage; payroll pays the contract."""
    _signed_active(w, w.me, basic_monthly=30000.0, house_rent=15000.0)
    mv = _move(w, w.me, proposed_gross=80000.0)
    with pytest.raises(UserError, match="no component"):
        mv.with_user(w.mgr).action_recommend()
    mv2 = _move(w, w.me, proposed_gross=99000.0, proposed_basic=40000.0)
    mv.sudo().unlink()
    with pytest.raises(UserError, match="does not equal its components"):
        mv2.with_user(w.mgr).action_recommend()


def test_a_pay_change_needs_an_active_contract(w):
    mv = _move(w, w.me, proposed_basic=40000.0)
    with pytest.raises(UserError, match="no active employment contract"):
        mv.with_user(w.mgr).action_recommend()


def test_the_from_side_is_read_from_the_master_and_contract(w):
    """T7/T2: from_* and current pay were typed; the approval amount came from
    typed figures (equal figures routed a raise at amount 0)."""
    _signed_active(w, w.me, basic_monthly=30000.0, house_rent=15000.0)
    mv = _move(w, w.me, proposed_basic=40000.0, current_gross=999999.0)
    mv.with_user(w.mgr).action_recommend()
    assert mv.current_basic == 30000.0 and mv.current_gross == 45000.0
    assert mv._approval_amount() == 10000.0
    with pytest.raises(UserError):
        _rpc_write(w.env, w.hro, "fix.hr.transfer", mv, {"from_job_title": "Forged"})


def test_relocation_money_needs_finance(w):
    """T3: a transfer grant with no salary change skipped Finance at amount 0."""
    mv = _move(w, w.colleague, movement_type="transfer", transfer_grant=500000.0)
    mv.with_user(w.hro2).action_recommend()
    mv.with_user(w.dmgr).action_concur()
    mv.with_user(w.hro3).action_hr_audit()
    with pytest.raises(UserError, match="Finance clearance"):
        mv.with_user(w.hro3).action_request_approval()
    assert mv._approval_amount() == 500000.0


def test_destination_concurrence_is_never_skipped(w):
    """T4: recommend -> technical evaluation -> HR audit bypassed the receiving
    manager; concurred -> HR audit skipped a required technical evaluation."""
    mv = _move(w, w.colleague, movement_type="transfer", movement_category="technical_promotion")
    mv.with_user(w.hro2).action_recommend()
    with pytest.raises(UserError, match="concurred"):
        mv.with_user(w.hro3).action_tech_eval()
    mv.with_user(w.dmgr).action_concur()
    with pytest.raises(UserError, match="technical evaluation"):
        mv.with_user(w.hro3).action_hr_audit()


def test_one_open_movement_per_employee_and_no_backdating(w):
    first = _move(w, w.colleague, movement_type="transfer")
    first.with_user(w.hro2).action_recommend()
    second = _move(w, w.colleague, movement_type="transfer")
    with pytest.raises(UserError, match="already has an open movement"):
        second.with_user(w.hro2).action_recommend()
    old = _move(
        w, _emp(w.env), movement_type="transfer", effective_date=_today(w.env) - timedelta(days=10)
    )
    with pytest.raises(UserError, match="already past"):
        old.with_user(w.hro2).action_recommend()


def test_a_zero_seat_position_is_full_at_routing(w):
    """T12: routing treated 0 as unlimited, the apply's constraint as full."""
    seat = w.env["fix.org.position"].create({"name": "M21 Zero Seat", "headcount": 0})
    mv = _move(w, w.colleague, movement_type="transfer", to_position_id=seat.id)
    mv.with_user(w.hro2).action_recommend()
    mv.with_user(w.dmgr).action_concur()
    mv.with_user(w.hro3).action_hr_audit()
    with pytest.raises(UserError, match="full"):
        mv.with_user(w.hro3).action_request_approval()


# ============================================================ exit and settlement
def test_settled_before_the_last_working_day_ends_employment_on_that_day(w, payroll_hook):
    """E2: settling early terminated the contract and revoked access at once."""
    contract = _signed_active(w, w.colleague)
    lwd = _today(w.env) + timedelta(days=10)
    ex = _cleared(w, _exit(w, w.colleague, exit_type="contract_end", last_working_day=lwd))
    ex.with_user(w.hro2).action_compute_settlement()
    ex.with_user(w.hro2).action_request_approval()
    _approve(ex, w.fin)
    assert ex.state == "settled"
    assert contract.state == "active" and not w.colleague.left_date
    assert not _events(w.env, "employee.left", w.colleague.id)
    # on the day, the cron ends it
    w.env.cr.execute(
        "UPDATE fix_hr_exit SET last_working_day = %s WHERE id = %s", (_today(w.env), ex.id)
    )
    ex.invalidate_recordset()
    w.env["fix.hr.exit"]._cron_process_last_working_days()
    assert contract.state == "terminated" and w.colleague.left_date == _today(w.env)
    assert len(_events(w.env, "employee.left", w.colleague.id)) == 1


def test_a_hand_made_abandonment_exit_is_refused(w):
    """E14: it could never be confirmed and blocked the real s.27(3A) decision."""
    with pytest.raises(UserError, match="absence case"):
        _exit(w, w.colleague, exit_type="abandonment")
    ex = _exit(w, w.colleague)
    with pytest.raises(UserError, match="absence case"):
        ex.with_user(w.hro).write({"exit_type": "abandonment"})


def test_two_nominee_records_must_agree(w):
    """F5: the employee-form nominee was dropped once any dependant nominee existed."""
    emp = _emp(w.env, nominee_name="Spouse Person", nominee_pct=100.0)
    w.env["fix.hr.dependant"].create(
        {
            "employee_id": emp.id,
            "name": "Child Person",
            "relation": "child",
            "is_nominee": True,
            "nominee_pct": 100.0,
        }
    )
    ex = _exit(w, emp, exit_type="death")
    with pytest.raises(UserError, match="reconcile the nomination"):
        ex._fix_nominee_shares()


# ============================================================ disciplinary
def test_a_charge_is_never_backdated(w):
    """E6: a typed earlier charge date shortened the s.24 seven days."""
    case = w.env(user=w.hro.id)["fix.hr.disciplinary.case"].create(
        {
            "employee_id": w.colleague.id,
            "misconduct_category": w.env["fix.hr.disciplinary.case"]
            ._fields["misconduct_category"]
            ._description_selection(w.env)[0][0],
            "allegation": "Audit allegation",
            "charge_date": _today(w.env) - timedelta(days=8),
        }
    )
    case.with_user(w.hro2).action_charge()
    assert case.charge_date == _today(w.env)
    with pytest.raises(UserError, match="until"):
        case.with_user(w.hro2).action_hold_hearing()


# ============================================================ reports and KPIs
def test_headcount_excludes_leavers_and_movement_reconciles(w):
    env = w.env
    gone = _emp(env, left_date=_today(env) - timedelta(days=5))
    assert gone not in m21_surfaces._employees(env)
    pack = m21_surfaces.headcount_movement(env)
    for r in pack["rows"]:
        assert r["closing"] == (
            r["opening"] + r["joiners"] - r["leavers"] + r["transfers_in"] - r["transfers_out"]
        )


def test_attrition_honours_the_period(w):
    """The screen offers a period; the report always read year-to-date."""
    env = w.env
    ex = _exit(w, _emp(env), exit_type="contract_end", last_working_day=date(1999, 6, 30))
    ex.sudo()._guarded().write({"state": "notice"})
    in_1999 = m21_surfaces.attrition_analysis(env, date_from="1999-01-01", date_to="1999-12-31")
    in_1998 = m21_surfaces.attrition_analysis(env, date_from="1998-01-01", date_to="1998-12-31")
    assert in_1999["totals"]["exits"] == 1 and "1999-01-01" in in_1999["title"]
    assert in_1998["totals"]["exits"] == 0


def test_open_positions_sum_real_vacancies_and_over_establishment_shows(w):
    env = w.env
    full = env["fix.org.position"].create({"name": "M21 Over", "headcount": 1})
    env["fix.org.position"].create({"name": "M21 Empty", "headcount": 3})
    a, b = _emp(env), _emp(env)
    a.write({"position_id": full.id})
    env.cr.execute("UPDATE hr_employee SET position_id = %s WHERE id = %s", (full.id, b.id))
    b.invalidate_recordset()
    rows = {r["position"]: r for r in m21_surfaces.establishment_register(env)["rows"]}
    assert rows["M21 Over"]["over"] == 1 and rows["M21 Empty"]["vacant"] == 3
    before = m21_surfaces.kpis(env)["open_positions"]
    assert before >= 3  # the over-filled seat no longer cancels the empty ones


def test_probationary_employees_without_a_contract_are_shown(w):
    emp = _emp(w.env, employment_type="probationary")
    pack = m21_surfaces.probation_conversion(w.env)
    assert any(r["employee"] == emp.name and r["due_window"] == "Unknown" for r in pack["rows"])
