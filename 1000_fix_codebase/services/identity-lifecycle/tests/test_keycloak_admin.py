"""Keycloak Admin client: fail-closed configuration, token handling, transport safety."""

from __future__ import annotations

import socket

import pytest
from fake_keycloak import ADMIN_PASSWORD, ADMIN_USER, REALM, new_id
from keycloak_admin import (
    KeycloakAdminClient,
    KeycloakConfig,
    KeycloakConfigError,
    KeycloakError,
    is_user_id,
)

# --------------------------------------------------------------------------- configuration


def test_missing_settings_fail_closed_with_every_gap_named():
    with pytest.raises(KeycloakConfigError) as exc:
        KeycloakConfig.from_env({})
    message = str(exc.value)
    assert "refuses to start" in message
    assert "KEYCLOAK_URL" in message and "KEYCLOAK_REALM" in message
    assert "KEYCLOAK_ADMIN_CLIENT_SECRET" in message


def test_a_user_without_password_is_not_a_credential():
    with pytest.raises(KeycloakConfigError, match="KEYCLOAK_ADMIN_PASSWORD"):
        KeycloakConfig.from_env(
            {"KEYCLOAK_URL": "http://kc", "KEYCLOAK_REALM": "r", "KEYCLOAK_ADMIN_USER": "admin"}
        )


def test_password_grant_defaults():
    cfg = KeycloakConfig.from_env(
        {
            "KEYCLOAK_URL": "http://keycloak:8080/",
            "KEYCLOAK_REALM": REALM,
            "KEYCLOAK_ADMIN_USER": " admin ",
            "KEYCLOAK_ADMIN_PASSWORD": "pw",
        }
    )
    assert (cfg.base_url, cfg.admin_realm, cfg.client_id) == (
        "http://keycloak:8080",
        "master",
        "admin-cli",
    )
    assert (cfg.username, cfg.password, cfg.client_secret, cfg.timeout) == (
        "admin",
        "pw",
        None,
        10.0,
    )


def test_service_account_takes_precedence_over_a_user():
    cfg = KeycloakConfig.from_env(
        {
            "KEYCLOAK_URL": "https://kc",
            "KEYCLOAK_REALM": REALM,
            "KEYCLOAK_ADMIN_CLIENT_ID": "identity-lifecycle",
            "KEYCLOAK_ADMIN_CLIENT_SECRET": "s",
            "KEYCLOAK_ADMIN_USER": "admin",
            "KEYCLOAK_ADMIN_PASSWORD": "pw",
            "KEYCLOAK_ADMIN_REALM": REALM,
        }
    )
    assert (cfg.client_id, cfg.client_secret, cfg.username, cfg.password) == (
        "identity-lifecycle",
        "s",
        None,
        None,
    )
    assert cfg.admin_realm == REALM


@pytest.mark.parametrize(
    ("overrides", "match"),
    [
        ({"KEYCLOAK_URL": "ftp://kc"}, "http\\(s\\) URL"),
        ({"KEYCLOAK_URL": "kc:8080"}, "http\\(s\\) URL"),
        ({"KEYCLOAK_TIMEOUT_SECONDS": "soon"}, "not a number"),
        ({"KEYCLOAK_TIMEOUT_SECONDS": "0"}, "must be positive"),
    ],
)
def test_invalid_settings_fail_closed(overrides, match):
    env = {
        "KEYCLOAK_URL": "http://kc",
        "KEYCLOAK_REALM": REALM,
        "KEYCLOAK_ADMIN_USER": "a",
        "KEYCLOAK_ADMIN_PASSWORD": "b",
        **overrides,
    }
    with pytest.raises(KeycloakConfigError, match=match):
        KeycloakConfig.from_env(env)


# --------------------------------------------------------------------------- tokens


def _client(keycloak, **env_overrides) -> KeycloakAdminClient:
    env = {
        "KEYCLOAK_URL": keycloak.base_url,
        "KEYCLOAK_REALM": REALM,
        "KEYCLOAK_ADMIN_USER": ADMIN_USER,
        "KEYCLOAK_ADMIN_PASSWORD": ADMIN_PASSWORD,
        **env_overrides,
    }
    return KeycloakAdminClient(KeycloakConfig.from_env(env))


def test_token_is_cached_until_shortly_before_expiry(keycloak):
    uid = keycloak.add_user("karim", "EMP-1")
    now = [1000.0]
    client = KeycloakAdminClient(_client(keycloak).config, clock=lambda: now[0])
    client.get_user(uid)
    client.user_sessions(uid)
    assert keycloak.token_requests == 1
    now[0] += 300 - 30  # expires_in 300, refreshed 30 s early
    client.get_user(uid)
    assert keycloak.token_requests == 2


def test_service_account_uses_client_credentials(keycloak):
    uid = keycloak.add_user("karim", "EMP-1")
    client = _client(keycloak, KEYCLOAK_ADMIN_CLIENT_SECRET="test-only-service-account-secret")
    assert client.get_user(uid)["username"] == "karim"


def test_wrong_admin_credentials_are_rejected_not_retried(keycloak):
    client = _client(keycloak, KEYCLOAK_ADMIN_PASSWORD="wrong")
    with pytest.raises(KeycloakError) as exc:
        client.get_user(new_id())
    assert (exc.value.status, exc.value.transient) == (401, False)


def test_token_response_without_a_token_is_an_error(keycloak):
    keycloak.token_response = {"token_type": "bearer"}
    with pytest.raises(KeycloakError, match="no access_token"):
        _client(keycloak).get_user(new_id())


def test_redirects_are_refused_so_the_token_never_leaves_the_idp(keycloak):
    keycloak.redirect_token_to = "http://evil.example/collect"
    with pytest.raises(KeycloakError, match=r"redirect to 'http://evil.example/collect' refused"):
        _client(keycloak).get_user(new_id())


# --------------------------------------------------------------------------- transport


def test_unreachable_keycloak_is_transient():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    client = KeycloakAdminClient(
        KeycloakConfig.from_env(
            {
                "KEYCLOAK_URL": f"http://127.0.0.1:{port}",
                "KEYCLOAK_REALM": REALM,
                "KEYCLOAK_ADMIN_USER": "a",
                "KEYCLOAK_ADMIN_PASSWORD": "b",
                "KEYCLOAK_TIMEOUT_SECONDS": "2",
            }
        )
    )
    with pytest.raises(KeycloakError, match="unreachable") as exc:
        client.get_user(new_id())
    assert exc.value.transient is True


@pytest.mark.parametrize(
    ("status", "transient"), [(503, True), (429, True), (500, True), (409, False)]
)
def test_http_errors_carry_status_and_retry_class(keycloak, status, transient):
    uid = keycloak.add_user("karim", "EMP-1")
    keycloak.failures[("GET", f"/users/{uid}/sessions")] = [status]
    with pytest.raises(KeycloakError) as exc:
        _client(keycloak).user_sessions(uid)
    assert (exc.value.status, exc.value.transient) == (status, transient)


def test_get_user_maps_404_to_none_but_reraises_other_errors(keycloak):
    client = _client(keycloak)
    assert client.get_user(new_id()) is None
    uid = keycloak.add_user("karim", "EMP-1")
    keycloak.failures[("GET", f"/users/{uid}")] = [500]
    with pytest.raises(KeycloakError):
        client.get_user(uid)


def test_a_non_json_success_body_is_an_error(keycloak):
    uid = keycloak.add_user("karim", "EMP-1")
    keycloak.garbage_paths.add("/sessions")
    with pytest.raises(KeycloakError, match="unexpected response body"):
        _client(keycloak).user_sessions(uid)


def test_lookup_helpers_return_exact_matches_only(keycloak):
    uid = keycloak.add_user("EMP-7", "EMP-7")
    keycloak.add_user("emp-77", "EMP-77")
    client = _client(keycloak)
    assert [u["id"] for u in client.find_users_by_attribute("employee_code", "EMP-7")] == [uid]
    assert [u["id"] for u in client.find_users_by_username("EMP-7")] == [uid]
    assert client.find_users_by_attribute("employee_code", "EMP-404") == []
    assert client.role_mappings(uid)["realmMappings"][0]["name"] == "fix_technician"


def test_ids_from_events_are_validated_before_any_url_is_built(keycloak):
    client = _client(keycloak)
    for bad in ("../../clients", "", "x" * 36, None, 42):
        assert is_user_id(bad) is False
    with pytest.raises(KeycloakError, match="malformed Keycloak user id"):
        client.disable_user("../realm-settings")
    with pytest.raises(KeycloakError, match="malformed client id"):
        client.remove_client_roles(new_id(), "../../roles", [])
    assert keycloak.calls == []  # nothing was sent


def test_realm_role_lookup_maps_404_to_none_but_reraises_other_errors(keycloak):
    client = _client(keycloak)
    assert client.get_realm_role("R-07")["name"] == "R-07"
    assert client.get_realm_role("R-404") is None
    keycloak.failures[("GET", "/roles/R-07")] = [500]
    with pytest.raises(KeycloakError) as exc:
        client.get_realm_role("R-07")
    assert exc.value.transient is True
