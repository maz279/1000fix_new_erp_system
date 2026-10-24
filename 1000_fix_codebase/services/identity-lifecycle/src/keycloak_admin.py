"""keycloak_admin.py — minimal Keycloak Admin REST client for M29's identity lifecycle.

Stdlib only (the L5 service discipline). Credentials come from the environment and
nowhere else; a missing setting is a configuration error and the service does not
start (fail closed). The admin bearer token never leaves the configured Keycloak:
redirects are refused and no proxy is used.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

#: Keycloak user ids are UUIDs; anything else from an event is never put in a URL path.
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")
#: Statuses worth retrying: the IdP is down, overloaded or rate-limiting us.
_TRANSIENT_STATUSES = {408, 425, 429, 500, 502, 503, 504}


class KeycloakConfigError(Exception):
    """Required Keycloak settings are missing: the service refuses to run."""


class KeycloakError(Exception):
    """A Keycloak Admin API call failed; ``transient`` failures are worth retrying."""

    def __init__(self, message: str, *, status: int | None = None, transient: bool = False):
        super().__init__(message)
        self.status = status
        self.transient = transient


@dataclass(frozen=True)
class KeycloakConfig:
    base_url: str
    realm: str
    admin_realm: str
    client_id: str
    client_secret: str | None
    username: str | None
    password: str | None
    timeout: float = 10.0

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> KeycloakConfig:
        """Admin credentials: a service-account client (preferred) or an admin user."""
        env = os.environ if env is None else env

        def get(name: str) -> str:
            return (env.get(name) or "").strip()

        missing = [n for n in ("KEYCLOAK_URL", "KEYCLOAK_REALM") if not get(n)]
        secret = get("KEYCLOAK_ADMIN_CLIENT_SECRET")
        username, password = get("KEYCLOAK_ADMIN_USER"), get("KEYCLOAK_ADMIN_PASSWORD")
        if not secret and not (username and password):
            missing.append(
                "KEYCLOAK_ADMIN_CLIENT_SECRET (service account) or "
                "KEYCLOAK_ADMIN_USER + KEYCLOAK_ADMIN_PASSWORD"
            )
        if missing:
            raise KeycloakConfigError(
                "identity-lifecycle refuses to start - missing Keycloak settings: "
                + ", ".join(missing)
            )
        base_url = get("KEYCLOAK_URL").rstrip("/")
        if urllib.parse.urlsplit(base_url).scheme not in ("http", "https"):
            raise KeycloakConfigError(f"KEYCLOAK_URL must be an http(s) URL, got {base_url!r}")
        try:
            timeout = float(get("KEYCLOAK_TIMEOUT_SECONDS") or 10.0)
        except ValueError as exc:
            raise KeycloakConfigError(f"KEYCLOAK_TIMEOUT_SECONDS is not a number: {exc}") from exc
        if timeout <= 0:
            raise KeycloakConfigError("KEYCLOAK_TIMEOUT_SECONDS must be positive")
        return cls(
            base_url=base_url,
            realm=get("KEYCLOAK_REALM"),
            admin_realm=get("KEYCLOAK_ADMIN_REALM") or "master",
            client_id=get("KEYCLOAK_ADMIN_CLIENT_ID") or "admin-cli",
            client_secret=secret or None,
            username=None if secret else username,
            password=None if secret else password,
            timeout=timeout,
        )


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise KeycloakError(f"redirect to {newurl!r} refused (admin token stays on the IdP)")


def build_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)


def is_user_id(value: Any) -> bool:
    return isinstance(value, str) and bool(_UUID_RE.match(value))


class KeycloakAdminClient:
    """The handful of Admin REST calls a leaver deprovisioning needs."""

    def __init__(
        self,
        config: KeycloakConfig,
        opener: urllib.request.OpenerDirector | None = None,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.config = config
        self._opener = opener or build_opener()
        self._clock = clock
        self._token: str | None = None
        self._token_expires_at = 0.0

    # ------------------------------------------------------------------ transport

    def _send(self, request: urllib.request.Request, what: str) -> tuple[int, Any]:
        try:
            with self._opener.open(request, timeout=self.config.timeout) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as exc:
            status = exc.code
            raise KeycloakError(
                f"{what}: HTTP {status}", status=status, transient=status in _TRANSIENT_STATUSES
            ) from exc
        except KeycloakError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise KeycloakError(f"{what}: Keycloak unreachable ({exc})", transient=True) from exc
        except ValueError as exc:  # a 2xx whose body is not JSON
            raise KeycloakError(f"{what}: unexpected response body ({exc})") from exc

    def _access_token(self) -> str:
        if self._token and self._clock() < self._token_expires_at:
            return self._token
        cfg = self.config
        form = {"client_id": cfg.client_id}
        if cfg.client_secret:
            form.update(grant_type="client_credentials", client_secret=cfg.client_secret)
        else:
            form.update(grant_type="password", username=cfg.username, password=cfg.password)
        url = (
            f"{cfg.base_url}/realms/{urllib.parse.quote(cfg.admin_realm, safe='')}"
            "/protocol/openid-connect/token"
        )
        request = urllib.request.Request(  # noqa: S310 - http(s) scheme validated in from_env
            url,
            data=urllib.parse.urlencode(form).encode("ascii"),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        _, body = self._send(request, "admin token")
        if not isinstance(body, dict) or not body.get("access_token"):
            raise KeycloakError("admin token: no access_token in the response")
        self._token = str(body["access_token"])
        # refresh 30 s early so a long deprovisioning never runs on an expiring token
        self._token_expires_at = self._clock() + max(float(body.get("expires_in", 60)) - 30, 0)
        return self._token

    def _call(
        self,
        method: str,
        path: str,
        body: Any = None,
        query: Mapping[str, str] | None = None,
    ) -> tuple[int, Any]:
        realm = urllib.parse.quote(self.config.realm, safe="")
        url = f"{self.config.base_url}/admin/realms/{realm}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(  # noqa: S310 - http(s) scheme validated in from_env
            url,
            data=None if body is None else json.dumps(body).encode("utf-8"),
            method=method,
            headers={
                "Authorization": f"Bearer {self._access_token()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        return self._send(request, f"{method} {path}")

    @staticmethod
    def _user_path(user_id: str, suffix: str = "") -> str:
        if not is_user_id(user_id):
            raise KeycloakError(f"refusing a malformed Keycloak user id {user_id!r}")
        return f"/users/{user_id}{suffix}"

    # ------------------------------------------------------------------ users

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        try:
            _, body = self._call("GET", self._user_path(user_id))
        except KeycloakError as exc:
            if exc.status == 404:
                return None
            raise
        return body

    def find_users_by_attribute(self, name: str, value: str) -> list[dict[str, Any]]:
        """Users whose attribute ``name`` holds exactly ``value`` (server search + exact check)."""
        _, body = self._call(
            "GET", "/users", query={"q": f"{name}:{value}", "exact": "true", "max": "5"}
        )
        return [u for u in (body or []) if value in ((u.get("attributes") or {}).get(name) or [])]

    def find_users_by_username(self, username: str) -> list[dict[str, Any]]:
        _, body = self._call(
            "GET", "/users", query={"username": username, "exact": "true", "max": "5"}
        )
        return [u for u in (body or []) if u.get("username") == username.lower()]

    def create_user(self, representation: dict[str, Any]) -> None:
        """POST /users (201, no body): callers resolve the new id by their lookup key."""
        self._call("POST", "/users", body=representation)

    def update_user(self, user_id: str, changes: dict[str, Any]) -> None:
        self._call("PUT", self._user_path(user_id), body=changes)

    def disable_user(self, user_id: str) -> None:
        self.update_user(user_id, {"enabled": False})

    def get_realm_role(self, name: str) -> dict[str, Any] | None:
        try:
            _, body = self._call("GET", f"/roles/{urllib.parse.quote(name, safe='')}")
        except KeycloakError as exc:
            if exc.status == 404:
                return None
            raise
        return body

    def add_realm_roles(self, user_id: str, roles: list[dict[str, Any]]) -> None:
        self._call("POST", self._user_path(user_id, "/role-mappings/realm"), body=roles)

    def logout_user(self, user_id: str) -> None:
        self._call("POST", self._user_path(user_id, "/logout"))

    def user_sessions(self, user_id: str) -> list[dict[str, Any]]:
        _, body = self._call("GET", self._user_path(user_id, "/sessions"))
        return list(body or [])

    def role_mappings(self, user_id: str) -> dict[str, Any]:
        _, body = self._call("GET", self._user_path(user_id, "/role-mappings"))
        return body or {}

    def remove_realm_roles(self, user_id: str, roles: list[dict[str, Any]]) -> None:
        self._call("DELETE", self._user_path(user_id, "/role-mappings/realm"), body=roles)

    def remove_client_roles(
        self, user_id: str, client_uuid: str, roles: list[dict[str, Any]]
    ) -> None:
        if not is_user_id(client_uuid):
            raise KeycloakError(f"refusing a malformed client id {client_uuid!r}")
        self._call(
            "DELETE",
            self._user_path(user_id, f"/role-mappings/clients/{client_uuid}"),
            body=roles,
        )
