"""employee.left -> Keycloak deprovisioning (M29, KPI-090) against a fake Keycloak server."""

from __future__ import annotations

import json

import pytest
from fake_keycloak import CLIENT_UUID, new_id
from identity_lifecycle import (
    CONSUMER_GROUP,
    EMPLOYEE_TOPIC,
    IdentityLifecycle,
    ProcessedLedger,
)
from keycloak_admin import KeycloakAdminClient, KeycloakConfig

from libs.py.fix_events import ConsumerBusState


def _deprovisioner(kc_env, buses, **kwargs) -> IdentityLifecycle:
    sleeps: list[float] = []
    dep = IdentityLifecycle(
        KeycloakAdminClient(KeycloakConfig.from_env(kc_env)),
        kwargs.pop("ledger", None),
        sleep=sleeps.append,
        bus=lambda: buses["bus"],
        migration=lambda: buses["migration"],
        **kwargs,
    )
    dep.sleeps = sleeps  # type: ignore[attr-defined]
    return dep


def _leave(buses, employee_id=17, code="EMP-0017", kc_id=None, **meta) -> str:
    """M21 publishing employee.left (as the outbox relay does) - returns its event_id."""
    payload = {
        "employee_id": employee_id,
        "employee_code": code,
        "keycloak_user_id": kc_id if kc_id is not None else False,
        "left_date": "2026-10-22",
    }
    meta.setdefault("correlation_id", "corr-leaver-1")
    res = buses["bus"].publish_dual("employee.left", "hr.employee", employee_id, payload, meta)
    return res["event_id"]


def _emitted(buses, event_type: str) -> list[dict]:
    topic = "fix.events." + event_type.split(".")[0]
    return [
        r.value
        for r in buses["kafka"].get_topic_records(topic)
        if r.value["event_type"] == event_type
    ]


# --------------------------------------------------------------------------- happy path


def test_leaver_is_disabled_logged_out_and_stripped_of_roles(keycloak, kc_env, buses):
    uid = keycloak.add_user(
        "rahim.uddin", "EMP-0017", realm_roles=("fix_technician", "fix_finance")
    )
    left_id = _leave(buses, kc_id=uid)

    [outcome] = _deprovisioner(kc_env, buses).drain()

    assert (outcome.status, outcome.keycloak_user_id, outcome.employee_id) == (
        "deprovisioned",
        uid,
        17,
    )
    assert keycloak.users[uid]["enabled"] is False
    assert keycloak.sessions[uid] == []
    assert keycloak.realm_roles[uid] == [] and keycloak.client_roles[uid] == []
    assert keycloak.calls_for("PUT") == [f"/admin/realms/1000fix-dev/users/{uid}"]
    assert keycloak.calls_for("POST", "/logout") == [
        f"/admin/realms/1000fix-dev/users/{uid}/logout"
    ]
    assert keycloak.calls_for("DELETE", f"/clients/{CLIENT_UUID}")

    [confirmation] = _emitted(buses, "identity.deprovisioned")
    payload = confirmation["payload"]
    assert payload["employee_id"] == 17 and payload["employee_code"] == "EMP-0017"
    assert payload["keycloak_user_id"] == uid and payload["username"] == "rahim.uddin"
    assert payload["enabled"] is False and payload["sessions_revoked"] is True
    assert payload["realm_roles_removed"] == ["fix_finance", "fix_technician"]
    assert payload["client_roles_removed"] == ["fix-odoo-local:odoo-user"]
    assert payload["left_event_id"] == left_id and payload["attempts"] == 1
    assert payload["deprovisioned_at"].endswith("Z")
    # AS-08 causal chain: same correlation, caused by the leaver event
    assert confirmation["correlation_id"] == "corr-leaver-1"
    assert confirmation["causation_id"] == left_id
    assert confirmation["aggregate"] == "hr.employee" and confirmation["aggregate_id"] == 17


def test_leaver_without_stored_id_is_found_by_employee_code_attribute(keycloak, kc_env, buses):
    other = keycloak.add_user("someone.else", "EMP-0099")
    uid = keycloak.add_user("karim", "EMP-0017")
    _leave(buses)
    [outcome] = _deprovisioner(kc_env, buses).drain()
    assert outcome.keycloak_user_id == uid
    assert keycloak.users[other]["enabled"] is True  # nobody else touched


def test_falls_back_to_a_username_equal_to_the_employee_code(keycloak, kc_env, buses):
    uid = keycloak.add_user("EMP-0017")  # no attribute; KC lower-cases usernames
    _leave(buses, code="EMP-0017")
    assert _deprovisioner(kc_env, buses).drain()[0].keycloak_user_id == uid


def test_stale_stored_id_falls_back_to_the_employee_code(keycloak, kc_env, buses):
    uid = keycloak.add_user("karim", "EMP-0017")
    _leave(buses, kc_id=new_id())  # 404 in Keycloak
    assert _deprovisioner(kc_env, buses).drain()[0].keycloak_user_id == uid


def test_a_crafted_user_id_never_reaches_a_url_path(keycloak, kc_env, buses):
    uid = keycloak.add_user("karim", "EMP-0017")
    _leave(buses, kc_id="../../clients")
    assert _deprovisioner(kc_env, buses).drain()[0].keycloak_user_id == uid
    assert not any("clients/../" in p or "/../" in p for _, p in keycloak.calls)


def test_user_without_roles_or_sessions_is_still_confirmed(keycloak, kc_env, buses):
    uid = keycloak.add_user("karim", "EMP-0017", realm_roles=(), client_roles=(), sessions=0)
    _leave(buses)
    [outcome] = _deprovisioner(kc_env, buses).drain()
    assert outcome.status == "deprovisioned"
    assert not keycloak.calls_for("DELETE")
    payload = _emitted(buses, "identity.deprovisioned")[0]["payload"]
    assert payload["realm_roles_removed"] == [] and payload["client_roles_removed"] == []
    assert keycloak.users[uid]["enabled"] is False


# --------------------------------------------------------------------------- failures


def test_unknown_user_emits_a_failure_and_touches_nothing(keycloak, kc_env, buses):
    keycloak.add_user("someone.else", "EMP-0099")
    left_id = _leave(buses, code="EMP-4040")
    [outcome] = _deprovisioner(kc_env, buses).drain()

    assert outcome.status == "failed" and outcome.reason.startswith("identity_not_found")
    assert not keycloak.calls_for("PUT") and not keycloak.calls_for("POST", "/logout")
    assert _emitted(buses, "identity.deprovisioned") == []
    [failure] = _emitted(buses, "identity.deprovision_failed")
    assert failure["payload"]["reason_code"] == "identity_not_found"
    assert failure["payload"]["employee_code"] == "EMP-4040"
    assert failure["payload"]["keycloak_user_id"] is None
    assert failure["payload"]["attempts"] == 1
    assert failure["causation_id"] == left_id


def test_ambiguous_match_is_never_guessed(keycloak, kc_env, buses):
    a = keycloak.add_user("karim1", "EMP-0017")
    b = keycloak.add_user("karim2", "EMP-0017")
    _leave(buses)
    [outcome] = _deprovisioner(kc_env, buses).drain()
    assert outcome.status == "failed" and "identity_ambiguous" in outcome.reason
    assert keycloak.users[a]["enabled"] and keycloak.users[b]["enabled"]


def test_leaver_without_id_or_code_is_a_failure(keycloak, kc_env, buses):
    _leave(buses, code="")
    [outcome] = _deprovisioner(kc_env, buses).drain()
    assert outcome.status == "failed" and "neither" in outcome.reason


def test_transient_outage_is_retried_with_backoff(keycloak, kc_env, buses):
    uid = keycloak.add_user("karim", "EMP-0017")
    keycloak.failures[("PUT", f"/users/{uid}")] = [503, 502]
    _leave(buses)
    dep = _deprovisioner(kc_env, buses)
    [outcome] = dep.drain()
    assert (outcome.status, outcome.attempts) == ("deprovisioned", 3)
    assert dep.sleeps == [0.5, 1.0]  # exponential backoff
    assert _emitted(buses, "identity.deprovisioned")[0]["payload"]["attempts"] == 3


def test_persistent_outage_reports_failure_and_a_redelivery_retries(keycloak, kc_env, buses):
    uid = keycloak.add_user("karim", "EMP-0017")
    keycloak.failures[("PUT", f"/users/{uid}")] = [503] * 4
    left = {
        "event_id": "evt-left-1",
        "event_type": "employee.left",
        "aggregate_id": 17,
        "payload": {"employee_id": 17, "employee_code": "EMP-0017", "keycloak_user_id": uid},
    }
    dep = _deprovisioner(kc_env, buses, backoff_cap=0.75)
    first = dep.handle(left)
    assert (first.status, first.attempts) == ("failed", 4)
    assert "idp_unavailable" in first.reason and "HTTP 503" in first.reason
    assert dep.sleeps == [0.5, 0.75, 0.75]  # capped
    [failure] = _emitted(buses, "identity.deprovision_failed")
    assert failure["payload"]["keycloak_user_id"] == uid
    assert keycloak.users[uid]["enabled"] is True

    # the IdP recovers: the SAME event re-delivered is worked again (not a final state)
    second = dep.handle(left)
    assert second.status == "deprovisioned"
    assert keycloak.users[uid]["enabled"] is False


def test_rejected_call_is_not_retried(keycloak, kc_env, buses):
    uid = keycloak.add_user("karim", "EMP-0017")
    keycloak.failures[("PUT", f"/users/{uid}")] = [403]
    _leave(buses)
    dep = _deprovisioner(kc_env, buses)
    [outcome] = dep.drain()
    assert (outcome.status, outcome.attempts) == ("failed", 1)
    assert "idp_rejected" in outcome.reason and dep.sleeps == []


def test_success_is_only_claimed_when_keycloak_confirms_the_disable(keycloak, kc_env, buses):
    keycloak.add_user("karim", "EMP-0017")
    keycloak.ignore_disable = True  # the IdP silently keeps the account enabled
    _leave(buses)
    [outcome] = _deprovisioner(kc_env, buses, max_attempts=2).drain()
    assert outcome.status == "failed" and "still enabled" in outcome.reason
    assert _emitted(buses, "identity.deprovisioned") == []


def test_success_is_only_claimed_when_no_session_survives(keycloak, kc_env, buses):
    keycloak.add_user("karim", "EMP-0017")
    keycloak.ignore_logout = True
    _leave(buses)
    [outcome] = _deprovisioner(kc_env, buses, max_attempts=1).drain()
    assert outcome.status == "failed" and "sessions survived" in outcome.reason


# --------------------------------------------------------------------------- idempotency


def test_redelivery_has_no_duplicate_side_effects(keycloak, kc_env, buses):
    uid = keycloak.add_user("karim", "EMP-0017")
    _leave(buses)
    dep = _deprovisioner(kc_env, buses)
    [record] = buses["redis"].get_messages("fix:events:employee")
    assert dep.handle(record["fields"]).status == "deprovisioned"
    calls = len(keycloak.calls)

    replay = dep.handle(record["fields"])  # the bus re-delivers the same event
    assert (replay.status, replay.keycloak_user_id) == ("duplicate", uid)
    assert len(keycloak.calls) == calls  # not a single extra Keycloak call
    assert len(_emitted(buses, "identity.deprovisioned")) == 1


def test_permanent_failure_is_not_repeated_on_redelivery(keycloak, kc_env, buses):
    _leave(buses, code="EMP-4040")
    dep = _deprovisioner(kc_env, buses)
    [record] = buses["redis"].get_messages("fix:events:employee")
    assert dep.handle(record["fields"]).status == "failed"
    assert dep.handle(record["fields"]).status == "duplicate"
    assert len(_emitted(buses, "identity.deprovision_failed")) == 1


def test_ledger_survives_a_restart(keycloak, kc_env, buses, tmp_path):
    keycloak.add_user("karim", "EMP-0017")
    _leave(buses)
    path = tmp_path / "state" / "ledger.json"
    [record] = buses["redis"].get_messages("fix:events:employee")
    assert (
        _deprovisioner(kc_env, buses, ledger=ProcessedLedger(path)).handle(record["fields"]).status
        == "deprovisioned"
    )
    restarted = _deprovisioner(kc_env, buses, ledger=ProcessedLedger(path))
    assert len(restarted.ledger) == 1
    assert restarted.handle(record["fields"]).status == "duplicate"
    assert json.loads(path.read_text(encoding="utf-8"))  # persisted, atomic replace


def test_event_without_event_id_dedups_on_its_payload(keycloak, kc_env, buses):
    keycloak.add_user("karim", "EMP-0017")
    dep = _deprovisioner(kc_env, buses)
    event = {
        "event_type": "employee.left",
        "payload": {"employee_id": 17, "employee_code": "EMP-0017"},
    }
    first = dep.handle(event)
    assert first.event_id.startswith("sha256:")
    assert dep.handle(dict(event)).status == "duplicate"
    assert _emitted(buses, "identity.deprovisioned")[0]["payload"]["left_event_id"] == ""


# --------------------------------------------------------------------------- consumption


def test_mover_events_change_nothing_in_keycloak(keycloak, kc_env, buses):
    """M29: business scope lives in Odoo record rules - a move is not an IdP change."""
    keycloak.add_user("karim", "EMP-0017")
    buses["bus"].publish_dual(
        "employee.moved", "hr.employee", 17, {"employee_code": "EMP-0017", "department": "QA"}
    )
    dep = _deprovisioner(kc_env, buses)
    [ignored] = dep.drain()
    assert ignored.status == "ignored" and keycloak.calls == []


@pytest.mark.parametrize(
    ("event", "reason"),
    [
        ({"event_type": "employee.left", "payload": "{broken"}, "malformed event"),
        (
            {"event_type": "employee.left", "payload": {"employee_code": "X"}},
            "without an employee id",
        ),
    ],
)
def test_malformed_leaver_events_are_skipped_not_fatal(kc_env, buses, keycloak, event, reason):
    outcome = _deprovisioner(kc_env, buses).handle(event)
    assert outcome.status == "ignored" and reason in outcome.reason
    assert keycloak.calls == []


@pytest.mark.parametrize("state", [ConsumerBusState.BUS_DUAL, ConsumerBusState.BUS_KAFKA])
def test_consumes_the_same_way_after_the_kafka_cutover(keycloak, kc_env, buses, state):
    uid = keycloak.add_user("karim", "EMP-0017")
    manager = buses["migration"]
    manager.register_group(CONSUMER_GROUP)
    manager.transition_group(CONSUMER_GROUP, state, "cut-over")
    _leave(buses)
    [outcome] = _deprovisioner(kc_env, buses).drain()
    assert (outcome.status, outcome.keycloak_user_id) == ("deprovisioned", uid)
    assert EMPLOYEE_TOPIC == "fix.events.employee"


def test_max_attempts_must_be_positive(kc_env):
    with pytest.raises(ValueError):
        IdentityLifecycle(KeycloakAdminClient(KeycloakConfig.from_env(kc_env)), max_attempts=0)


def test_from_env_builds_a_persistent_ledger(kc_env, tmp_path):
    env = dict(kc_env, IDENTITY_LIFECYCLE_LEDGER=str(tmp_path / "l.json"))
    dep = IdentityLifecycle.from_env(env)
    assert dep.ledger.path == tmp_path / "l.json"
    assert IdentityLifecycle.from_env(kc_env).ledger.path is None


def test_client_entries_without_roles_are_skipped(keycloak, kc_env, buses):
    keycloak.add_user("karim", "EMP-0017")
    keycloak.empty_client_mapping = True  # e.g. fix-portal-local listed with no mappings
    _leave(buses)
    [outcome] = _deprovisioner(kc_env, buses).drain()
    assert outcome.status == "deprovisioned"
    assert len(keycloak.calls_for("DELETE", "/role-mappings/clients/")) == 1
    payload = _emitted(buses, "identity.deprovisioned")[0]["payload"]
    assert payload["client_roles_removed"] == ["fix-odoo-local:odoo-user"]
