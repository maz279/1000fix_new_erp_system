# cd_hr_core live-ORM tests — P08-M01 / R06-M01 (CD-M21-01).
#
# Statutory figures: BLA s.4(8) (probation 6 months clerical, 3 others),
# BLA 2006 s.102 (48h week, a company setting), s.115 (10 casual days per
# calendar year), s.116 (14 sick days).
import base64
import json
from datetime import date, datetime, timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def emp(odoo_env):
    return odoo_env["hr.employee"].create({"name": "Farhana Islam", "employee_code": "E-0042"})


def _contract(env, emp, **vals):
    base = {
        "employee_id": emp.id,
        "contract_type": "permanent",
        "joining_date": date(2024, 7, 1),
        "basic_monthly": 35000.0,
    }
    base.update(vals)
    return env["fix.employment.contract"].create(base)


# --- hr.employee extension -------------------------------------------------------


def test_contract_count(odoo_env, emp):
    assert emp.contract_count == 0
    _contract(odoo_env, emp)
    _contract(odoo_env, emp, contract_type="fixed_term")
    emp.invalidate_recordset(["contract_count"])
    assert emp.contract_count == 2


def test_leaver_event_starts_kpi_090_clock_and_requests_deprovisioning(odoo_env, emp):
    assert (emp.keycloak_deprovision_status, emp.left_at) == ("active", False)
    now = datetime(2026, 10, 20, 9, 0)
    with mock.patch.object(fields.Datetime, "now", return_value=now):
        emp.action_mark_left()  # cd_employee_core: emits employee.left (M29 consumes it)
    assert [e["employee_id"] for e in _events(odoo_env, "employee.left", emp.id)] == [emp.id]
    assert emp.left_at == now
    # requested, NOT done: only a confirmation may set "deprovisioned"
    assert emp.keycloak_deprovision_status == "pending"
    assert not emp.keycloak_deprovisioned_at
    assert _events(odoo_env, "employee.keycloak.deprovisioned", emp.id) == []
    # archiving an active employee is the other leaver path
    other = odoo_env["hr.employee"].create(
        {"name": "Archived Leaver", "joined_date": date(2024, 1, 1)}
    )
    other.write({"active": False})
    assert other.keycloak_deprovision_status == "pending"
    assert other.left_at


@pytest.fixture
def hr_manager(odoo_env):
    return odoo_env["res.users"].create(
        {
            "name": "HR Manager Nila",
            "login": "hr.manager.kpi090.t",
            "group_ids": [(4, odoo_env.ref("hr.group_hr_manager").id)],
        }
    )


def test_manager_confirms_deprovisioning_and_sla_is_measured(odoo_env, emp, hr_manager):
    left = datetime(2026, 10, 20, 9, 0)
    with mock.patch.object(fields.Datetime, "now", return_value=left):
        emp.action_mark_left()
    confirmed = left + timedelta(minutes=45)
    with mock.patch.object(fields.Datetime, "now", return_value=confirmed):
        emp.with_user(hr_manager).action_confirm_keycloak_deprovisioned()
    assert emp.keycloak_deprovision_status == "deprovisioned"
    assert emp.keycloak_deprovisioned_at == confirmed
    assert emp.keycloak_deprovision_confirmed_by == hr_manager
    assert emp.keycloak_deprovision_hours == 0.75  # 45 min <= the 1 h target
    assert _events(odoo_env, "employee.keycloak.deprovisioned", emp.id) == [
        {
            "employee_code": "E-0042",
            "left_at": "2026-10-20 09:00:00",
            "deprovisioned_at": "2026-10-20 09:45:00",
            "hours": 0.75,
            "within_sla": True,
            "confirmed_by": "HR Manager Nila",
            "confirmation": "manual",
            "kpi": "KPI-090",
        }
    ]
    with (
        pytest.raises(UserError, match="has no Keycloak deprovisioning to confirm"),
        odoo_env.cr.savepoint(),
    ):
        emp.action_confirm_keycloak_deprovisioned()  # already confirmed


def test_late_confirmation_breaches_the_one_hour_target(odoo_env, hr_manager):
    late = odoo_env["hr.employee"].create({"name": "Late Leaver", "employee_code": ""})
    left = datetime(2026, 10, 20, 9, 0)
    with mock.patch.object(fields.Datetime, "now", return_value=left):
        late.action_mark_left()
    late.keycloak_deprovision_status = "failed"  # e.g. a removal attempt that failed
    with mock.patch.object(fields.Datetime, "now", return_value=left + timedelta(hours=3)):
        late.with_user(hr_manager).action_confirm_keycloak_deprovisioned()
    payload = _events(odoo_env, "employee.keycloak.deprovisioned", late.id)[0]
    assert (payload["hours"], payload["within_sla"]) == (3.0, False)
    # a create mints the employee code (M58-F1): the event carries it
    assert late.employee_code and payload["employee_code"] == late.employee_code


def test_confirmation_is_an_hr_manager_control(odoo_env, emp):
    emp.action_mark_left()
    clerk = odoo_env["res.users"].create({"name": "Clerk", "login": "clerk.kpi090.t"})
    with (
        pytest.raises(AccessError, match="Only an HR manager may confirm"),
        odoo_env.cr.savepoint(),
    ):
        emp.with_user(clerk).action_confirm_keycloak_deprovisioned()
    assert emp.keycloak_deprovision_status == "pending"


def test_nothing_to_confirm_for_a_current_employee(odoo_env, emp):
    with (
        pytest.raises(UserError, match=r"no Keycloak deprovisioning to confirm \(status: active\)"),
        odoo_env.cr.savepoint(),
    ):
        emp.action_confirm_keycloak_deprovisioned()


def test_kpi_090_counts_unconfirmed_leavers_24h_after_the_leaver_event(odoo_env):
    Employee = odoo_env["hr.employee"]
    baseline = Employee.measure_kpi_090_orphaned_accounts()
    now = fields.Datetime.now()

    def leaver(name, hours_ago, **vals):
        employee = Employee.create({"name": name, **vals})
        employee.action_mark_left()
        employee.write({"left_at": now - timedelta(hours=hours_ago)})
        return employee

    leaver("Left 2 days ago, pending", 48)
    still_active_record = leaver("Left 30 h ago, record kept active", 30)
    leaver("Left 25 h ago, removal failed", 25)
    confirmed = leaver("Left 2 days ago, confirmed", 48)
    confirmed.action_confirm_keycloak_deprovisioned()
    leaver("Left 2 h ago", 2)  # still inside the 24 h window
    # an employee HIRED long ago who never left is not a leaver at all
    Employee.create({"name": "Long-serving, archived without leaver event", "active": False})
    assert still_active_record.active
    assert Employee.measure_kpi_090_orphaned_accounts() == baseline + 3


def test_mover_events(odoo_env, emp):
    dept = odoo_env["hr.department"].create({"name": "Field Service"})
    # A09 ERP audit X-F15: a department on its own is context, not an access
    # move — it announces nothing
    emp.write({"department_id": dept.id})
    assert _events(odoo_env, "employee.moved", emp.id) == []
    location = odoo_env["hr.work.location"].create(
        {"name": "Uttara Hub", "address_id": odoo_env.company.partner_id.id}
    )
    emp.write({"work_location_id": location.id})  # regression: was `work_location`
    job = odoo_env["hr.job"].create({"name": "Senior Technician"})
    emp.write({"job_id": job.id})
    moves = _events(odoo_env, "employee.moved", emp.id)
    assert [m["employee_code"] for m in moves] == ["E-0042", "E-0042"]
    emp.write({"private_email": "farhana@example.com"})  # not a move
    assert len(_events(odoo_env, "employee.moved", emp.id)) == 2
    blank = odoo_env["hr.employee"].create({"name": "No Dept"})
    blank.write({"job_id": job.id})
    moved = _events(odoo_env, "employee.moved", blank.id)
    # a create mints the employee code (M58-F1): the event names it
    assert blank.employee_code
    assert len(moved) == 1 and moved[0]["employee_code"] == blank.employee_code


# --- organisation structure --------------------------------------------------------


def test_reporting_line_loop_is_refused(odoo_env):
    Position = odoo_env["fix.org.position"]
    ceo = Position.create({"name": "CEO"})
    coo = Position.create({"name": "COO", "parent_id": ceo.id})
    manager = Position.create({"name": "Service Manager", "parent_id": coo.id})
    assert manager.parent_id.parent_id == ceo
    with (
        pytest.raises(ValidationError, match="Reporting line loop at CEO"),
        odoo_env.cr.savepoint(),
    ):
        ceo.write({"parent_id": manager.id})


# --- employment contracts -------------------------------------------------------------


def test_contract_reference(odoo_env, emp):
    assert _contract(odoo_env, emp).name == "CNT/E-0042/PERMANENT/2024"
    # a create in the estate mints the employee code (M58-F1); the reference
    # names the CODE, never a changeable name
    minted = odoo_env["hr.employee"].create({"name": "Rubel"})
    assert minted.employee_code
    assert _contract(odoo_env, minted, contract_type="probation").name == (
        "CNT/%s/PROBATION/2024" % minted.employee_code
    )
    draft = odoo_env["fix.employment.contract"].new({"contract_type": "part_time"})
    assert draft.name == "CNT/EMP/PART_TIME/%d" % fields.Date.today().year


def test_statutory_limits_are_constraints_on_every_path(odoo_env, emp):
    """A09 M21-8: the limits used to run only inside action_activate, so a
    contract created (or written) past them was saved. Now no path saves it.

    Honest rewrite of the old test: it activated a draft directly, which is
    no longer possible without Legal Counsel's routed sign-off
    (test_a09_m21_controls.py proves that path as non-admin users)."""
    # BLA s.4(8): 6 months for a clerical worker (the default class)
    ok = _contract(odoo_env, emp, contract_type="probation", probation_end=date(2025, 1, 1))
    assert ok.state == "draft"
    for vals, message in (
        ({"probation_end": date(2025, 1, 2)}, "Probation exceeds the 6-month statutory cap"),
        (
            {"probation_end": date(2024, 10, 2), "probation_class": "other"},
            "Probation exceeds the 3-month statutory cap",
        ),
        ({"weekly_hours": 49.0}, "weekly hours may not exceed 48"),
        ({"basic_monthly": 0.0}, "Basic salary must be positive"),
        ({"state": "active", "contract_type": "probation"}, "needs its probation end date"),
    ):
        with pytest.raises(ValidationError, match=message), odoo_env.cr.savepoint():
            _contract(odoo_env, emp, **vals)
    with pytest.raises(ValidationError, match="weekly hours"), odoo_env.cr.savepoint():
        ok.write({"weekly_hours": 72.0})


def test_activation_requires_the_legal_signoff(odoo_env, emp):
    draft = _contract(odoo_env, emp)
    with pytest.raises(UserError, match="needs Legal Counsel's sign-off"), odoo_env.cr.savepoint():
        draft.action_activate()
    assert draft.state == "draft"


def test_terminate_is_not_a_one_click_leaver(odoo_env, emp):
    """A09 M21-7 / r2 D1: action_terminate ended the contract and fired
    employee.left with no exit, grounds or notice. An employment now ends only
    through its exit's settlement (I3), proved in test_a09_m21_controls.py."""
    contract = _contract(odoo_env, emp, state="active")
    with pytest.raises(UserError, match="ends through its Exit"), odoo_env.cr.savepoint():
        contract.action_terminate()
    assert contract.state == "active"
    assert _events(odoo_env, "employee.left", emp.id) == []
    assert (emp.keycloak_deprovision_status, emp.left_at) == ("active", False)


def test_one_active_contract_per_employee(odoo_env, emp):
    _contract(odoo_env, emp, state="active")
    with (
        pytest.raises(ValidationError, match="already has an active contract"),
        odoo_env.cr.savepoint(),
    ):
        _contract(odoo_env, emp, joining_date=date(2025, 1, 1), state="active")


def test_contract_document_generation(odoo_env, emp):
    template = odoo_env["fix.document.template"].search([("document_type", "=", "contract")])[-1]
    chosen = _contract(odoo_env, emp, template_id=template.id)
    doc = chosen.action_generate_contract_document()
    assert chosen.document_id == doc
    assert doc.template_id == template
    assert (doc.document_type, doc.isolation_tier) == ("contract", "T1")
    assert (doc.res_model, doc.res_id) == ("fix.employment.contract", chosen.id)
    assert doc.name == "Contract - Farhana Islam (permanent)"
    assert doc.name_bn == "নিয়োগ চুক্তি - Farhana Islam"
    attachment = doc.attachment_id
    assert attachment.name == "Employment_Contract_CNT_E-0042_PERMANENT_2024.txt"
    text = base64.b64decode(attachment.datas).decode()
    assert "Contract Ref: CNT/E-0042/PERMANENT/2024\n" in text
    assert "Employee: Farhana Islam (Code: E-0042)\n" in text
    assert "Statutory Weekly Hours: 48.0 (s.102 cap)\n" in text
    assert "Basic Monthly Salary: BDT 35,000.00\n" in text
    assert _events(odoo_env, "employment.contract.generated", chosen.id) == [
        {
            "contract": "CNT/E-0042/PERMANENT/2024",
            "document_id": doc.id,
        }
    ]


def test_contract_documents_for_every_contract_of_a_batch(odoo_env, emp):
    """Regression: the loop returned after the first contract."""
    other = odoo_env["hr.employee"].create({"name": "Rubel"})
    pair = _contract(odoo_env, emp) | _contract(odoo_env, other)
    docs = pair.action_generate_contract_document()
    assert len(docs) == 2
    assert all(c.document_id for c in pair)
    # no template chosen: the Form 6 contract template is picked
    assert set(docs.mapped("template_id.document_type")) == {"contract"}
    no_code = base64.b64decode(pair[1].document_id.attachment_id.datas).decode()
    # a create mints the code (M58-F1), so the letter prints it
    assert "Employee: Rubel (Code: %s)\n" % other.employee_code in no_code


def test_document_generation_refuses_invalid_contract(odoo_env, emp):
    with (
        pytest.raises(ValidationError, match="Basic salary must be positive"),
        odoo_env.cr.savepoint(),
    ):
        _contract(odoo_env, emp, basic_monthly=0.0).action_generate_contract_document()


# Statutory leave is proved behaviourally, as non-admin users, in
# test_a09_leave_controls.py (A09 M55); the superuser-only leave tests that
# used to live here asserted a direct, unrouted approval as correct.
