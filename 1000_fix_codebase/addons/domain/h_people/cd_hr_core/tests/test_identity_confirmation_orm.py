# cd_hr_core live-ORM tests - M29 -> M21 IdP deprovisioning confirmation (KPI-090).
#
# employee.left is consumed by services/identity-lifecycle, which removes the
# Keycloak access and reports identity.deprovisioned / identity.deprovision_failed;
# cd_hr_core applies that outcome ("confirmation": "idp"). The manual HR-manager
# confirmation remains the fallback control.
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo import fields

from libs.py.fix_events import ConsumerGroupMigrationManager, DualWriteEventBus, InMemoryBus
from libs.py.fix_events import dual_write as dual_write_mod
from libs.py.fix_events import kafka_bus as kafka_bus_mod
from libs.py.fix_events import migration as migration_mod
from libs.py.fix_events.dual_write import MockRedisStreamStore

LEFT = datetime(2026, 10, 20, 9, 0)
KC_USER = "0d7e1f9a-5c3b-4a8e-9f21-6b4d2c8e1a07"


def _outbox(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [(json.loads(r.payload), json.loads(r.metadata_json or "{}")) for r in rows]


@pytest.fixture
def leaver(odoo_env):
    emp = odoo_env["hr.employee"].create({"name": "Sabbir Hossain", "employee_code": "E-0777"})
    with mock.patch.object(fields.Datetime, "now", return_value=LEFT):
        emp.action_mark_left()
    assert emp.keycloak_deprovision_status == "pending"
    return emp


@pytest.fixture
def buses(monkeypatch):
    kafka, redis = InMemoryBus(), MockRedisStreamStore()
    monkeypatch.setattr(kafka_bus_mod, "_global_kafka_client", kafka)
    monkeypatch.setattr(dual_write_mod, "_global_redis_store", redis)
    bus = DualWriteEventBus()
    monkeypatch.setattr(dual_write_mod, "_global_dual_bus", bus)
    manager = ConsumerGroupMigrationManager(kafka_client=kafka, redis_store=redis)
    monkeypatch.setattr(migration_mod, "_global_migration_mgr", manager)
    return {"bus": bus, "kafka": kafka, "redis": redis, "migration": manager}


def _deprovisioned(emp, at="2026-10-20T09:20:00Z", event_id="evt-idp-1", **payload):
    body = {
        "employee_id": emp.id,
        "employee_code": "E-0777",
        "keycloak_user_id": KC_USER,
        "username": "sabbir",
        "deprovisioned_at": at,
        "enabled": False,
        "sessions_revoked": True,
        "realm_roles_removed": ["fix_technician"],
        "client_roles_removed": [],
        "attempts": 1,
        "left_event_id": "evt-left-1",
        **payload,
    }
    return {
        "event_id": event_id,
        "event_type": "identity.deprovisioned",
        "correlation_id": "corr-leaver",
        "causation_id": "evt-left-1",
        "aggregate": "hr.employee",
        "aggregate_id": emp.id,
        "payload": body,
    }


def _failed(emp, reason_code="identity_not_found", reason="no Keycloak account for E-0777"):
    return {
        "event_id": "evt-idp-fail",
        "event_type": "identity.deprovision_failed",
        "aggregate_id": emp.id,
        "payload": {
            "employee_id": emp.id,
            "employee_code": "E-0777",
            "keycloak_user_id": None,
            "reason_code": reason_code,
            "reason": reason,
            "failed_at": "2026-10-20T09:05:00Z",
            "attempts": 1,
            "left_event_id": "evt-left-1",
        },
    }


# --- applying the IdP outcome ----------------------------------------------------


def test_idp_confirmation_marks_the_leaver_deprovisioned(odoo_env, leaver):
    Employee = odoo_env["hr.employee"]
    assert Employee.consume_identity_lifecycle_event(_deprovisioned(leaver)) == leaver
    assert leaver.keycloak_deprovision_status == "deprovisioned"
    assert leaver.keycloak_deprovisioned_at == datetime(2026, 10, 20, 9, 20)
    assert leaver.keycloak_deprovision_hours == 0.33  # 20 min, well inside 1 h
    assert not leaver.keycloak_deprovision_confirmed_by  # nobody clicked: the IdP confirmed
    assert leaver.keycloak_user_id == KC_USER
    [(payload, meta)] = _outbox(odoo_env, "employee.keycloak.deprovisioned", leaver.id)
    assert payload == {
        "employee_code": "E-0777",
        "left_at": "2026-10-20 09:00:00",
        "deprovisioned_at": "2026-10-20 09:20:00",
        "hours": 0.33,
        "within_sla": True,
        "confirmed_by": "identity-lifecycle (Keycloak)",
        "confirmation": "idp",
        "kpi": "KPI-090",
    }
    assert (meta["correlation_id"], meta["causation_id"]) == ("corr-leaver", "evt-idp-1")
    assert odoo_env["hr.employee"].measure_kpi_090_orphaned_accounts() >= 0


def test_redis_shaped_event_and_offset_timestamps_are_understood(odoo_env, leaver):
    event = _deprovisioned(leaver, at="2026-10-20T15:30:00+06:00")  # Asia/Dhaka offset
    raw = {
        **{k: v for k, v in event.items() if k != "payload"},
        "aggregate_id": str(leaver.id),
        "payload": json.dumps(event["payload"]),
    }
    odoo_env["hr.employee"].consume_identity_lifecycle_event(raw)
    assert leaver.keycloak_deprovisioned_at == datetime(2026, 10, 20, 9, 30)  # stored as UTC


def test_late_idp_confirmation_is_recorded_as_a_breach(odoo_env, leaver):
    odoo_env["hr.employee"].consume_identity_lifecycle_event(
        _deprovisioned(leaver, at="2026-10-20T12:00:00Z")
    )
    assert leaver.keycloak_deprovision_hours == 3.0
    [(payload, _meta)] = _outbox(odoo_env, "employee.keycloak.deprovisioned", leaver.id)
    assert payload["within_sla"] is False


def test_redelivery_and_late_failures_never_undo_a_confirmed_removal(odoo_env, leaver):
    Employee = odoo_env["hr.employee"]
    Employee.consume_identity_lifecycle_event(_deprovisioned(leaver))
    assert not Employee.consume_identity_lifecycle_event(_deprovisioned(leaver))
    assert not Employee.consume_identity_lifecycle_event(_failed(leaver))
    assert leaver.keycloak_deprovision_status == "deprovisioned"
    assert len(_outbox(odoo_env, "employee.keycloak.deprovisioned", leaver.id)) == 1


def test_idp_failure_marks_failed_and_the_manual_fallback_still_works(odoo_env, leaver):
    Employee = odoo_env["hr.employee"]
    assert Employee.consume_identity_lifecycle_event(_failed(leaver)) == leaver
    assert leaver.keycloak_deprovision_status == "failed"
    assert "identity_not_found" in leaver.message_ids[0].body
    assert _outbox(odoo_env, "employee.keycloak.deprovisioned", leaver.id) == []
    # fallback control: an HR manager verifies and confirms by hand
    leaver.action_confirm_keycloak_deprovisioned()
    assert leaver.keycloak_deprovision_status == "deprovisioned"
    [(payload, _meta)] = _outbox(odoo_env, "employee.keycloak.deprovisioned", leaver.id)
    assert payload["confirmation"] == "manual"


def test_idp_success_after_a_reported_failure_is_applied(odoo_env, leaver):
    Employee = odoo_env["hr.employee"]
    Employee.consume_identity_lifecycle_event(_failed(leaver, "idp_unavailable", "HTTP 503"))
    Employee.consume_identity_lifecycle_event(_deprovisioned(leaver))  # retried later, OK
    assert leaver.keycloak_deprovision_status == "deprovisioned"


def test_events_that_do_not_apply_are_ignored(odoo_env, leaver):
    Employee = odoo_env["hr.employee"]
    current = Employee.create({"name": "Still Here", "employee_code": "E-0001"})
    assert not Employee.consume_identity_lifecycle_event(_deprovisioned(current))
    assert current.keycloak_deprovision_status == "active"  # no leaver event, no clock
    ghost = _deprovisioned(leaver)
    ghost["payload"]["employee_id"] = 0
    ghost["aggregate_id"] = None
    assert not Employee.consume_identity_lifecycle_event(ghost)
    other = dict(_deprovisioned(leaver), event_type="identity.suspended")
    assert not Employee.consume_identity_lifecycle_event(other)
    assert leaver.keycloak_deprovision_status == "pending"


# --- consumption through fix_events -------------------------------------------------


def test_drain_applies_outcomes_from_the_bus_once(odoo_env, leaver, buses):
    event = _deprovisioned(leaver)
    buses["bus"].publish_dual(
        "identity.deprovisioned",
        "hr.employee",
        leaver.id,
        event["payload"],
        {"correlation_id": "corr-leaver", "causation_id": "evt-left-1"},
    )
    Employee = odoo_env["hr.employee"]
    assert Employee.drain_identity_lifecycle_events() == leaver
    assert leaver.keycloak_deprovision_status == "deprovisioned"
    assert not Employee.drain_identity_lifecycle_events()  # cursor advanced: nothing new


def test_cron_data_schedules_the_drain(odoo_env):
    from odoo.tools.convert import convert_file

    convert_file(
        odoo_env,
        "cd_hr_core",
        "data/identity_lifecycle_cron.xml",
        {},
        mode="init",
        noupdate=False,
        kind="data",
    )
    cron = odoo_env.ref("cd_hr_core.ir_cron_drain_identity_lifecycle_events")
    assert cron.model_id.model == "hr.employee"
    assert cron.code.strip() == "model.drain_identity_lifecycle_events()"
    assert (cron.interval_number, cron.interval_type, cron.active) == (5, "minutes", True)


# --- joiner: the provisioned Keycloak id is stored -------------------------------------


def _provisioned(emp, kc_id=KC_USER, event_type="identity.provisioned", **payload):
    return {
        "event_id": "evt-prov-1",
        "event_type": event_type,
        "aggregate": "hr.employee",
        "aggregate_id": emp.id,
        "payload": {
            "employee_id": emp.id,
            "employee_code": "E-0777",
            "keycloak_user_id": kc_id,
            **payload,
        },
    }


def test_provisioned_identity_id_is_stored_once(odoo_env):
    Employee = odoo_env["hr.employee"]
    emp = Employee.create({"name": "New Joiner", "employee_code": "E-0777"})
    assert not emp.keycloak_user_id
    assert Employee.consume_identity_lifecycle_event(_provisioned(emp)) == emp
    assert emp.keycloak_user_id == KC_USER
    assert not Employee.consume_identity_lifecycle_event(_provisioned(emp))  # redelivery


def test_a_different_id_never_replaces_the_recorded_one(odoo_env):
    Employee = odoo_env["hr.employee"]
    emp = Employee.create({"name": "New Joiner", "employee_code": "E-0777"})
    Employee.consume_identity_lifecycle_event(_provisioned(emp))
    other = "9a8b7c6d-1111-4222-8333-444455556666"
    assert not Employee.consume_identity_lifecycle_event(_provisioned(emp, kc_id=other))
    assert emp.keycloak_user_id == KC_USER
    assert "duplicate identity" in emp.message_ids[0].body


def test_a_failed_provisioning_keeps_the_created_account_id_and_the_reason(odoo_env):
    Employee = odoo_env["hr.employee"]
    emp = Employee.create({"name": "New Joiner", "employee_code": "E-0777"})
    failed = _provisioned(
        emp,
        event_type="identity.provision_failed",
        reason_code="role_not_in_realm",
        reason="realm role R-99 does not exist",
    )
    assert Employee.consume_identity_lifecycle_event(failed) == emp
    assert emp.keycloak_user_id == KC_USER  # the leaver can still be matched by id
    assert "role_not_in_realm" in emp.message_ids[0].body
    no_account = _provisioned(
        emp, kc_id=None, event_type="identity.provision_failed", reason_code="idp_rejected"
    )
    assert Employee.consume_identity_lifecycle_event(no_account) == emp
    assert emp.keycloak_user_id == KC_USER and "idp_rejected" in emp.message_ids[0].body


def test_provisioning_outcome_for_an_unknown_employee_is_ignored(odoo_env):
    ghost = {"event_type": "identity.provisioned", "payload": {"employee_id": 0}}
    assert not odoo_env["hr.employee"].consume_identity_lifecycle_event(ghost)


# --- end to end: Odoo joiner -> M29 -> Keycloak -> Odoo -> leaver by id -----------


def _relay(env, bus, event_type, employee):
    """The outbox relay: one outbox row onto the bus, its ids intact."""
    row = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", employee.id)],
        order="id desc",
        limit=1,
    )
    meta = json.loads(row.metadata_json)
    bus.publish_dual(
        row.event_type,
        row.aggregate,
        row.aggregate_id,
        json.loads(row.payload),
        {"event_id": row.event_id, "correlation_id": meta["correlation_id"]},
    )
    return json.loads(row.payload)


def test_end_to_end_joiner_then_leaver_by_the_stored_id(odoo_env, buses):
    service = Path(__file__).resolve().parents[5] / "services" / "identity-lifecycle"
    for p in (str(service / "src"), str(service / "tests")):
        if p not in sys.path:
            sys.path.insert(0, p)
    from fake_keycloak import ADMIN_PASSWORD, ADMIN_USER, REALM, FakeKeycloak
    from identity_lifecycle import IdentityLifecycle
    from keycloak_admin import KeycloakAdminClient, KeycloakConfig

    keycloak = FakeKeycloak()
    try:
        config = KeycloakConfig.from_env(
            {
                "KEYCLOAK_URL": keycloak.base_url,
                "KEYCLOAK_REALM": REALM,
                "KEYCLOAK_ADMIN_USER": ADMIN_USER,
                "KEYCLOAK_ADMIN_PASSWORD": ADMIN_PASSWORD,
            }
        )
        clock = [datetime(2026, 10, 20, 9, 12, tzinfo=UTC)]
        worker = IdentityLifecycle(KeycloakAdminClient(config), now=lambda: clock[0])
        Employee = odoo_env["hr.employee"]

        # joiner: the employee master announces the hire, M29 creates the identity
        emp = Employee.create(
            {
                "name": "Sabbir Hossain",
                "employee_code": "E-0777",
                "work_email": "sabbir@1000fix.local",
            }
        )
        _relay(odoo_env, buses["bus"], "employee.joined", emp)
        [joined] = worker.drain()
        assert joined.status == "provisioned"
        uid = joined.keycloak_user_id
        assert keycloak.users[uid]["attributes"] == {"employee_code": ["E-0777"]}
        assert keycloak.users[uid]["requiredActions"] == ["UPDATE_PASSWORD"]
        assert Employee.drain_identity_lifecycle_events() == emp
        assert emp.keycloak_user_id == uid

        # leaver: the stored id travels in employee.left and is the lookup path
        with mock.patch.object(fields.Datetime, "now", return_value=LEFT):
            emp.action_mark_left()
        left_payload = _relay(odoo_env, buses["bus"], "employee.left", emp)
        assert left_payload["keycloak_user_id"] == uid
        keycloak.calls.clear()
        [left] = worker.drain()
        assert (left.status, left.keycloak_user_id) == ("deprovisioned", uid)
        first_admin_call = next(c for c in keycloak.calls if "/admin/" in c[1])
        assert first_admin_call == ("GET", f"/admin/realms/{REALM}/users/{uid}")  # by id
        assert not any("q=employee_code" in path for _, path in keycloak.calls)
        assert keycloak.users[uid]["enabled"] is False

        assert Employee.drain_identity_lifecycle_events() == emp
        assert emp.keycloak_deprovision_status == "deprovisioned"
        assert emp.keycloak_deprovision_hours == 0.2  # 12 minutes: KPI-090 met
        [(payload, _meta)] = _outbox(odoo_env, "employee.keycloak.deprovisioned", emp.id)
        assert payload["confirmation"] == "idp" and payload["within_sla"] is True
        assert emp.left_at + timedelta(hours=1) > emp.keycloak_deprovisioned_at
    finally:
        keycloak.close()
