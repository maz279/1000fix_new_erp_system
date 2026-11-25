# Behavioural tests for the M21-core employee master: JML events through the
# outbox, the derived employment status and the M21 -> M29 role API.
import contextlib
import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import ValidationError


@contextlib.contextmanager
def _rejects(env, exc, match):
    """pytest.raises inside a savepoint: an expected failure never leaves a
    half-applied write in the shared test transaction."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


PAST = "2020-01-15"


def _events(env, event_type, employee):
    return env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", "hr.employee"),
            ("aggregate_id", "=", employee.id),
        ]
    )


def _payload(env, event_type, employee):
    events = _events(env, event_type, employee)
    assert len(events) == 1, f"expected one {event_type}, got {len(events)}"
    return json.loads(events.payload)


def _role(env, code, name=None):
    return env["fix.role"].create({"code": code, "name": name or code})


def _branch(env):
    company = env.company
    entity = env["fix.entity"].search([("company_id", "=", company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "EMPTEST", "legal_name": "Emp Test Ltd", "company_id": company.id})
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    return env["fix.branch"].create(
        {"code": "EB1", "name": "Emp Branch", "entity_id": entity.id, "operating_unit_id": ou.id}
    )


def _employee(env, **vals):
    return env["hr.employee"].create({"name": vals.pop("name", "Rahim Uddin"), **vals})


# --- joiner -------------------------------------------------------------------


def test_active_joiner_emits_employee_joined_with_full_payload(odoo_env):
    branch = _branch(odoo_env)
    role = _role(odoo_env, "R-T01")
    emp = _employee(
        odoo_env,
        employee_code="E-00042",
        branch_id=branch.id,
        primary_role_id=role.id,
        joined_date=PAST,
    )
    assert emp.employment_status == "active"
    assert _payload(odoo_env, "employee.joined", emp) == {
        "employee_id": emp.id,
        "employee_code": "E-00042",
        "branch_id": branch.id,
        "primary_role": "R-T01",
        "joined_date": PAST,
        "name": "Rahim Uddin",
        "work_email": None,
    }


def test_pre_start_joiner_emits_joined_with_null_references(odoo_env):
    emp = _employee(odoo_env)
    assert emp.employment_status == "joining"
    payload = _payload(odoo_env, "employee.joined", emp)
    assert payload["branch_id"] is None
    assert payload["primary_role"] is None
    assert payload["joined_date"] is None
    assert payload["work_email"] is None


def test_joiner_payload_carries_the_identity_attributes_m29_provisions(odoo_env):
    emp = _employee(odoo_env, name="Nusrat Jahan", work_email="nusrat@1000fix.local")
    payload = _payload(odoo_env, "employee.joined", emp)
    assert (payload["name"], payload["work_email"]) == ("Nusrat Jahan", "nusrat@1000fix.local")


def test_future_start_date_is_still_joining(odoo_env):
    future = fields.Date.today() + timedelta(days=10)
    emp = _employee(odoo_env, joined_date=future)
    assert emp.employment_status == "joining"
    assert _payload(odoo_env, "employee.joined", emp)["joined_date"] == str(future)


def test_employee_created_archived_emits_no_joiner(odoo_env):
    emp = _employee(odoo_env, active=False)
    assert emp.employment_status == "leaving"
    assert not _events(odoo_env, "employee.joined", emp)


# --- leaver -------------------------------------------------------------------


def test_archiving_an_active_employee_emits_employee_left(odoo_env):
    """Regression: the status compute had no dependencies, so whether the
    leaver event fired depended on a stale cache (fresh cache: never)."""
    emp = _employee(odoo_env, employee_code="E-7", joined_date=PAST)
    odoo_env.invalidate_all()  # a fresh request: nothing cached
    emp = odoo_env["hr.employee"].browse(emp.id)

    emp.write({"active": False})

    payload = _payload(odoo_env, "employee.left", emp)
    assert payload["employee_id"] == emp.id
    assert payload["employee_code"] == "E-7"
    assert payload["keycloak_user_id"] is False
    assert payload["left_date"] == str(fields.Date.today())
    assert emp.employment_status == "leaving"


def test_archiving_with_warm_cache_also_updates_status(odoo_env):
    emp = _employee(odoo_env, joined_date=PAST)
    assert emp.employment_status == "active"  # cached
    emp.write({"active": False, "left_date": fields.Date.today()})
    assert emp.employment_status == "left"
    assert len(_events(odoo_env, "employee.left", emp)) == 1


def test_archiving_a_pre_start_joiner_emits_no_leaver(odoo_env):
    emp = _employee(odoo_env)
    emp.write({"active": False})
    assert not _events(odoo_env, "employee.left", emp)


def test_reactivating_emits_no_leaver(odoo_env):
    emp = _employee(odoo_env, joined_date=PAST, active=False)
    emp.write({"active": True})
    assert emp.employment_status == "active"
    assert not _events(odoo_env, "employee.left", emp)


def test_action_mark_left_stamps_today_and_emits_leaver(odoo_env):
    emp = _employee(odoo_env, joined_date=PAST)
    emp.action_mark_left()
    assert emp.left_date == fields.Date.today()
    assert _payload(odoo_env, "employee.left", emp)["left_date"] == str(fields.Date.today())


# --- mover (role changes) -------------------------------------------------------


def test_primary_role_change_emits_role_changed(odoo_env):
    emp = _employee(odoo_env, joined_date=PAST)
    role = _role(odoo_env, "R-T02")
    emp.write({"primary_role_id": role.id})
    assert _payload(odoo_env, "employee.role_changed", emp) == {
        "employee_id": emp.id,
        "primary_role": "R-T02",
    }


def test_additional_role_change_emits_role_changed_without_primary(odoo_env):
    emp = _employee(odoo_env, joined_date=PAST)
    emp.write({"additional_role_ids": [(4, _role(odoo_env, "R-T03").id)]})
    assert _payload(odoo_env, "employee.role_changed", emp)["primary_role"] is None


def test_unrelated_write_emits_no_jml_event(odoo_env):
    emp = _employee(odoo_env, joined_date=PAST)
    emp.write({"name_bn": "রহিম উদ্দিন"})
    assert not _events(odoo_env, "employee.role_changed", emp)
    assert not _events(odoo_env, "employee.left", emp)


# --- M21 -> M29 sync API --------------------------------------------------------


def test_assign_role_unknown_code_raises(odoo_env):
    emp = _employee(odoo_env)
    with _rejects(odoo_env, ValueError, match="Role R-NOPE not found"):
        emp.assign_role("R-NOPE")


def test_assign_role_adds_additional_role_when_no_primary(odoo_env):
    emp = _employee(odoo_env)
    role = _role(odoo_env, "R-T04")
    emp.assign_role("R-T04")
    assert role in emp.additional_role_ids
    assert _events(odoo_env, "employee.role_changed", emp)


def test_assign_role_checks_sod_against_the_primary_role(odoo_env):
    primary = _role(odoo_env, "R-T05", "Cashier")
    conflicting = _role(odoo_env, "R-T06", "Cash Approver")
    compatible = _role(odoo_env, "R-T07", "Viewer")
    odoo_env["fix.sod.control"].create(
        {
            "code": "SOD-T1",
            "name": "Cash handling vs approval",
            "role_a_id": primary.id,
            "role_b_id": conflicting.id,
        }
    )
    emp = _employee(odoo_env, primary_role_id=primary.id)

    with _rejects(odoo_env, ValidationError, match="SoD control SOD-T1"):
        emp.assign_role("R-T06")
    assert conflicting not in emp.additional_role_ids

    emp.assign_role("R-T07")
    assert compatible in emp.additional_role_ids


def test_branch_carries_the_hr_grade_manager(odoo_env):
    branch = _branch(odoo_env)
    manager = _employee(odoo_env, name="Branch Boss")
    branch.employee_manager_id = manager
    assert branch.employee_manager_id == manager
