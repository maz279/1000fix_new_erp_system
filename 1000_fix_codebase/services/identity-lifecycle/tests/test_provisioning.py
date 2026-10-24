"""employee.joined -> Keycloak provisioning (M29 FR-SEC-027 / AUT-SEC-01) against a fake IdP."""

from __future__ import annotations

import pytest
from identity_lifecycle import IdentityLifecycle, split_name
from keycloak_admin import KeycloakAdminClient, KeycloakConfig


def _worker(kc_env, buses, **kwargs) -> IdentityLifecycle:
    sleeps: list[float] = []
    worker = IdentityLifecycle(
        KeycloakAdminClient(KeycloakConfig.from_env(kc_env)),
        sleep=sleeps.append,
        bus=lambda: buses["bus"],
        migration=lambda: buses["migration"],
        **kwargs,
    )
    worker.sleeps = sleeps  # type: ignore[attr-defined]
    return worker


def _join(buses, employee_id=21, code="EMP-0021", role="R-07", **extra) -> str:
    """cd_employee_core's employee.joined (the employee master) - returns its event_id."""
    payload = {
        "employee_id": employee_id,
        "employee_code": code,
        "branch_id": 3,
        "primary_role": role,
        "joined_date": "2026-10-22",
        "name": "Nusrat Jahan Chowdhury",
        "work_email": "nusrat.jahan@1000fix.local",
        **extra,
    }
    meta = {"correlation_id": "corr-joiner-1"}
    return buses["bus"].publish_dual("employee.joined", "hr.employee", employee_id, payload, meta)[
        "event_id"
    ]


def _emitted(buses, event_type):
    return [
        r.value
        for r in buses["kafka"].get_topic_records("fix.events.identity")
        if r.value["event_type"] == event_type
    ]


# --------------------------------------------------------------------------- new joiner


def test_new_joiner_gets_an_account_without_any_password(keycloak, kc_env, buses):
    joined_id = _join(buses)
    [outcome] = _worker(kc_env, buses).drain()

    assert outcome.status == "provisioned"
    [rep] = keycloak.created
    assert rep == {
        "username": "emp-0021",
        "enabled": True,
        "attributes": {"employee_code": ["EMP-0021"]},
        "requiredActions": ["UPDATE_PASSWORD"],
        "firstName": "Nusrat",
        "lastName": "Jahan Chowdhury",
        "email": "nusrat.jahan@1000fix.local",
        "emailVerified": False,
    }
    assert "credentials" not in rep  # never a default password
    uid = outcome.keycloak_user_id
    assert [r["name"] for r in keycloak.realm_roles[uid]] == ["R-07"]

    [event] = _emitted(buses, "identity.provisioned")
    payload = event["payload"]
    assert payload["employee_id"] == 21 and payload["employee_code"] == "EMP-0021"
    assert payload["keycloak_user_id"] == uid and payload["username"] == "emp-0021"
    assert payload["created"] is True and payload["enabled"] is True
    assert payload["realm_roles_assigned"] == ["R-07"]
    assert payload["required_actions"] == ["UPDATE_PASSWORD"]
    assert payload["joined_event_id"] == joined_id and payload["provisioned_at"].endswith("Z")
    assert (event["correlation_id"], event["causation_id"]) == ("corr-joiner-1", joined_id)


def test_joiner_without_name_email_or_role_gets_a_bare_account(keycloak, kc_env, buses):
    _join(buses, role=None, name=None, work_email=False)
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "provisioned"
    [rep] = keycloak.created
    assert set(rep) == {"username", "enabled", "attributes", "requiredActions"}
    assert not keycloak.calls_for("GET", "/roles/")
    assert _emitted(buses, "identity.provisioned")[0]["payload"]["realm_roles_assigned"] == []


def test_single_name_becomes_the_first_name():
    assert split_name("Rahim") == ("Rahim", "")
    assert split_name("  Rahim   Uddin  Ahmed ") == ("Rahim", "Uddin Ahmed")
    assert split_name(None) == ("", "") and split_name(False) == ("", "")


# --------------------------------------------------------------------------- reuse, never duplicate


def test_an_existing_account_for_the_employee_code_is_reused(keycloak, kc_env, buses):
    uid = keycloak.add_user("emp-0021", "EMP-0021", realm_roles=())
    _join(buses)
    [outcome] = _worker(kc_env, buses).drain()
    assert (outcome.status, outcome.keycloak_user_id) == ("provisioned", uid)
    assert keycloak.created == [] and keycloak.updates == []  # already this employee's
    assert len(keycloak.users) == 1
    assert _emitted(buses, "identity.provisioned")[0]["payload"]["created"] is False


def test_an_unattributed_account_with_the_username_is_adopted_keeping_its_profile(
    keycloak, kc_env, buses
):
    uid = keycloak.add_user("EMP-0021")  # pre-existing, no employee_code attribute
    _join(buses)
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.keycloak_user_id == uid and keycloak.created == []
    [(updated, rep)] = keycloak.updates
    assert updated == uid
    assert rep["attributes"] == {"employee_code": ["EMP-0021"]}
    # the full representation is sent: nothing else on the account is wiped
    assert (rep["firstName"], rep["email"]) == ("Existing", "emp-0021@local.invalid")


def test_a_rehire_reenables_the_old_account_and_forces_a_new_password(keycloak, kc_env, buses):
    uid = keycloak.add_user("emp-0021", "EMP-0021", enabled=False, realm_roles=())
    _join(buses)
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "provisioned"
    assert keycloak.users[uid]["enabled"] is True
    assert keycloak.users[uid]["requiredActions"] == ["UPDATE_PASSWORD"]
    assert keycloak.created == []


def test_a_second_joiner_event_for_the_same_employee_never_duplicates(keycloak, kc_env, buses):
    _join(buses)
    worker = _worker(kc_env, buses)
    worker.drain()
    _join(buses)  # e.g. re-emitted by a data fix - a NEW event id
    [second] = worker.drain()
    assert second.status == "provisioned"
    assert len(keycloak.created) == 1 and len(keycloak.users) == 1
    assert [e["payload"]["created"] for e in _emitted(buses, "identity.provisioned")] == [
        True,
        False,
    ]


def test_redelivery_of_the_same_event_has_no_side_effects(keycloak, kc_env, buses):
    _join(buses)
    worker = _worker(kc_env, buses)
    [record] = buses["redis"].get_messages("fix:events:employee")
    assert worker.handle(record["fields"]).status == "provisioned"
    calls = len(keycloak.calls)
    replay = worker.handle(record["fields"])
    assert replay.status == "duplicate" and replay.keycloak_user_id
    assert len(keycloak.calls) == calls
    assert len(_emitted(buses, "identity.provisioned")) == 1


# --------------------------------------------------------------------------- failures


def test_username_owned_by_another_employee_is_a_conflict(keycloak, kc_env, buses):
    other = keycloak.add_user("emp-0021", "EMP-9999")
    _join(buses)
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "failed" and outcome.reason.startswith("username_conflict")
    assert keycloak.created == [] and keycloak.updates == []
    [failure] = _emitted(buses, "identity.provision_failed")
    assert failure["payload"]["keycloak_user_id"] == other
    assert failure["payload"]["reason_code"] == "username_conflict"


def test_two_accounts_for_one_employee_code_are_never_guessed_between(keycloak, kc_env, buses):
    keycloak.add_user("a", "EMP-0021")
    keycloak.add_user("b", "EMP-0021")
    _join(buses)
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "failed" and "identity_ambiguous" in outcome.reason
    assert keycloak.created == []


def test_joiner_without_an_employee_code_cannot_be_keyed(keycloak, kc_env, buses):
    _join(buses, code="")
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "failed" and "no_employee_code" in outcome.reason
    assert keycloak.calls == []


def test_a_primary_role_missing_from_the_realm_is_reported_with_the_account(
    keycloak, kc_env, buses
):
    _join(buses, role="R-99")
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "failed" and "role_not_in_realm" in outcome.reason
    [failure] = _emitted(buses, "identity.provision_failed")
    # the account exists: its id travels so M21 can still key the leaver on it
    assert failure["payload"]["keycloak_user_id"] == outcome.keycloak_user_id
    assert outcome.keycloak_user_id in keycloak.users


def test_a_realm_that_drops_the_attribute_is_detected(keycloak, kc_env, buses):
    keycloak.drop_undeclared_attributes = True  # no user-profile declaration
    _join(buses)
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "failed" and "attribute_not_persisted" in outcome.reason
    assert _emitted(buses, "identity.provisioned") == []


def test_a_role_mapping_the_idp_does_not_keep_is_not_claimed(keycloak, kc_env, buses):
    keycloak.ignore_role_add = True
    _join(buses)
    [outcome] = _worker(kc_env, buses, max_attempts=2).drain()
    assert outcome.status == "failed" and "role mapping is missing" in outcome.reason
    assert len(keycloak.created) == 1  # the retry reused the account it had created


def test_an_account_that_does_not_appear_after_creation_is_retried(
    keycloak, kc_env, buses, monkeypatch
):
    worker = _worker(kc_env, buses, max_attempts=2)
    monkeypatch.setattr(worker.client, "create_user", lambda rep: None)  # IdP swallows it
    _join(buses)
    [outcome] = worker.drain()
    assert outcome.status == "failed" and "not findable" in outcome.reason
    assert worker.sleeps == [0.5]


def test_an_account_the_idp_reports_disabled_is_not_claimed(keycloak, kc_env, buses, monkeypatch):
    worker = _worker(kc_env, buses, max_attempts=1)
    real_get = worker.client.get_user
    monkeypatch.setattr(worker.client, "get_user", lambda uid: {**real_get(uid), "enabled": False})
    _join(buses)
    [outcome] = worker.drain()
    assert outcome.status == "failed" and "not enabled" in outcome.reason


def test_create_conflict_from_a_race_is_a_rejection(keycloak, kc_env, buses):
    keycloak.failures[("POST", "/admin/realms/1000fix-dev/users")] = [409]
    _join(buses)
    [outcome] = _worker(kc_env, buses).drain()
    assert outcome.status == "failed" and "idp_rejected" in outcome.reason
    assert outcome.attempts == 1


def test_transient_outage_on_create_is_retried(keycloak, kc_env, buses):
    keycloak.failures[("POST", "/admin/realms/1000fix-dev/users")] = [503]
    _join(buses)
    worker = _worker(kc_env, buses)
    [outcome] = worker.drain()
    assert (outcome.status, outcome.attempts) == ("provisioned", 2)
    assert worker.sleeps == [0.5]


@pytest.mark.parametrize(
    ("aggregate", "payload"),
    [
        # cd_talent's onboarding completion: the aggregate id is the PLAN, not an employee
        (
            "fix.onboarding.plan",
            {"onboarding_id": 5, "candidate_name": "X", "joined_date": "2026-10-22"},
        ),
        ("hr.employee", {"employee_code": "EMP-1"}),
    ],
)
def test_joiner_events_without_an_employee_are_ignored(keycloak, kc_env, buses, aggregate, payload):
    buses["bus"].publish_dual("employee.joined", aggregate, 5, payload)
    [outcome] = _worker(kc_env, buses).drain()
    if aggregate == "hr.employee":
        assert outcome.status == "provisioned"  # the employee-master aggregate id is the employee
        assert outcome.employee_id == 5
    else:
        assert outcome.status == "ignored" and "without an employee id" in outcome.reason
        assert keycloak.calls == []
