"""A fake Keycloak Admin REST server (loopback, ephemeral port) for the service tests.

The fake implements exactly the Admin API surface the deprovisioner uses, keeps real
state (users, sessions, role mappings), enforces bearer tokens, records every call,
and can be scripted to fail - so the client is exercised over a real HTTP socket
without any network beyond 127.0.0.1.
"""

from __future__ import annotations

import json
import sys
import threading
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

SRC = Path(__file__).resolve().parents[1] / "src"
ROOT = Path(__file__).resolve().parents[3]
for _p in (str(SRC), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


REALM = "1000fix-dev"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "test-only-admin-password"
CLIENT_UUID = "6f1c2c0e-3b7a-4d7e-9a51-2f4c8b0d1e22"


def new_id() -> str:
    return str(uuid.uuid4())


class FakeKeycloak:
    """In-memory Keycloak realm behind a ThreadingHTTPServer."""

    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}
        self.sessions: dict[str, list[dict[str, Any]]] = {}
        self.realm_roles: dict[str, list[dict[str, Any]]] = {}
        self.client_roles: dict[str, list[dict[str, Any]]] = {}
        self.calls: list[tuple[str, str]] = []
        self.created: list[dict[str, Any]] = []  # POST /users representations
        self.updates: list[tuple[str, dict[str, Any]]] = []  # PUT /users/{id} bodies
        self.tokens: set[str] = set()
        self.token_requests = 0
        # scripted failures: (METHOD, path-substring) -> list of statuses to return first
        self.failures: dict[tuple[str, str], list[int]] = {}
        self.ignore_disable = False
        self.ignore_logout = False
        self.redirect_token_to: str | None = None
        self.token_response: dict[str, Any] | None = None  # override the token body
        self.garbage_paths: set[str] = set()  # 200 with a non-JSON body
        self.empty_client_mapping = False  # a client entry whose mappings are empty
        # Keycloak 26 without a user-profile declaration silently drops custom attributes
        self.drop_undeclared_attributes = False
        self.realm_role_catalogue = {"R-01", "R-07", "R-12", "fix_technician"}
        self.ignore_role_add = False
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self._thread = threading.Thread(
            target=self.server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True
        )
        self._thread.start()

    # ------------------------------------------------------------------ state helpers

    def add_user(
        self,
        username: str,
        employee_code: str | None = None,
        *,
        realm_roles: tuple[str, ...] = ("fix_technician",),
        client_roles: tuple[str, ...] = ("odoo-user",),
        sessions: int = 2,
        user_id: str | None = None,
        enabled: bool = True,
    ) -> str:
        uid = user_id or new_id()
        attributes = {"employee_code": [employee_code]} if employee_code else {}
        self.users[uid] = {
            "id": uid,
            "username": username.lower(),
            "enabled": enabled,
            "firstName": "Existing",
            "email": f"{username.lower()}@local.invalid",
            "attributes": attributes,
        }
        self.sessions[uid] = [{"id": new_id(), "username": username} for _ in range(sessions)]
        self.realm_roles[uid] = [{"id": new_id(), "name": r} for r in realm_roles]
        self.client_roles[uid] = [{"id": new_id(), "name": r} for r in client_roles]
        return uid

    def calls_for(self, method: str, fragment: str = "") -> list[str]:
        return [p for m, p in self.calls if m == method and fragment in p]

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    # ------------------------------------------------------------------ HTTP

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:  # silence
                return

            def _send(self, code: int, body: Any = None, headers: dict[str, str] | None = None):
                data = b"" if body is None else json.dumps(body).encode("utf-8")
                self.send_response(code)
                for k, v in (headers or {}).items():
                    self.send_header(k, v)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _body(self) -> Any:
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length) if length else b""
                return raw

            def _dispatch(self, method: str) -> None:
                parsed = urllib.parse.urlsplit(self.path)
                path, query = parsed.path, urllib.parse.parse_qs(parsed.query)
                raw = self._body()
                fake.calls.append((method, self.path))
                if any(fragment in self.path for fragment in fake.garbage_paths):
                    data = b"<html>maintenance</html>"
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                for (m, fragment), statuses in fake.failures.items():
                    if m == method and fragment in self.path and statuses:
                        self._send(statuses.pop(0), {"error": "scripted"})
                        return
                if path == "/realms/master/protocol/openid-connect/token" and method == "POST":
                    self._token(urllib.parse.parse_qs(raw.decode("ascii")))
                    return
                prefix = f"/admin/realms/{REALM}"
                if not path.startswith(prefix):
                    self._send(404, {"error": "unknown realm"})
                    return
                auth = self.headers.get("Authorization", "")
                if not auth.startswith("Bearer ") or auth[7:] not in fake.tokens:
                    self._send(401, {"error": "unauthorized"})
                    return
                self._admin(method, path[len(prefix) :], query, raw)

            def _token(self, form: dict[str, list[str]]) -> None:
                fake.token_requests += 1
                if fake.redirect_token_to:
                    self._send(302, None, {"Location": fake.redirect_token_to})
                    return
                grant = form.get("grant_type", [""])[0]
                ok = (
                    grant == "password"
                    and form.get("username") == [ADMIN_USER]
                    and form.get("password") == [ADMIN_PASSWORD]
                ) or (
                    grant == "client_credentials"
                    and form.get("client_secret") == ["test-only-service-account-secret"]
                )
                if not ok:
                    self._send(401, {"error": "invalid_grant"})
                    return
                token = f"tok-{new_id()}"
                fake.tokens.add(token)
                body = {"access_token": token, "expires_in": 300}
                self._send(200, fake.token_response if fake.token_response is not None else body)

            def _admin(self, method: str, path: str, query: dict, raw: bytes) -> None:
                parts = [p for p in path.split("/") if p]
                if parts == ["users"] and method == "POST":
                    rep = json.loads(raw)
                    if any(u["username"] == rep["username"].lower() for u in fake.users.values()):
                        self._send(409, {"errorMessage": "User exists with same username"})
                        return
                    uid = new_id()
                    attributes = (
                        {} if fake.drop_undeclared_attributes else rep.get("attributes", {})
                    )
                    fake.users[uid] = {
                        **{k: v for k, v in rep.items() if k != "attributes"},
                        "id": uid,
                        "username": rep["username"].lower(),
                        "attributes": attributes,
                    }
                    fake.created.append(rep)
                    fake.sessions[uid], fake.realm_roles[uid], fake.client_roles[uid] = [], [], []
                    self._send(201, None, {"Location": f"{fake.base_url}/users/{uid}"})
                    return
                if parts[:1] == ["roles"] and method == "GET":
                    name = urllib.parse.unquote(parts[1])
                    if name not in fake.realm_role_catalogue:
                        self._send(404, {"error": "Could not find role"})
                    else:
                        self._send(200, {"id": f"role-{name}", "name": name})
                    return
                if parts == ["users"] and method == "GET":
                    if "q" in query:
                        name, _, value = query["q"][0].partition(":")
                        found = [
                            u
                            for u in fake.users.values()
                            if value in (u["attributes"].get(name) or [])
                        ]
                    else:
                        wanted = query.get("username", [""])[0].lower()
                        found = [u for u in fake.users.values() if u["username"] == wanted]
                    self._send(200, found)
                    return
                if len(parts) < 2 or parts[0] != "users" or parts[1] not in fake.users:
                    self._send(404, {"error": "User not found"})
                    return
                uid, rest = parts[1], parts[2:]
                if not rest and method == "GET":
                    self._send(200, fake.users[uid])
                elif not rest and method == "PUT":
                    changes = json.loads(raw)
                    fake.updates.append((uid, changes))
                    if fake.drop_undeclared_attributes:
                        changes.pop("attributes", None)
                    if not (fake.ignore_disable and changes.get("enabled") is False):
                        fake.users[uid].update(changes)
                    self._send(204)
                elif rest == ["logout"] and method == "POST":
                    if not fake.ignore_logout:
                        fake.sessions[uid] = []
                    self._send(204)
                elif rest == ["sessions"] and method == "GET":
                    self._send(200, fake.sessions[uid])
                elif rest == ["role-mappings"] and method == "GET":
                    clients = (
                        {
                            "fix-odoo-local": {
                                "id": CLIENT_UUID,
                                "client": "fix-odoo-local",
                                "mappings": fake.client_roles[uid],
                            }
                        }
                        if fake.client_roles[uid]
                        else {}
                    )
                    if fake.empty_client_mapping:
                        clients["fix-portal-local"] = {
                            "id": CLIENT_UUID,
                            "client": "fix-portal-local",
                            "mappings": [],
                        }
                    body = {"clientMappings": clients} if clients else {}
                    if fake.realm_roles[uid]:
                        body["realmMappings"] = fake.realm_roles[uid]
                    self._send(200, body)
                elif rest == ["role-mappings", "realm"] and method == "POST":
                    if not fake.ignore_role_add:
                        have = {r["name"] for r in fake.realm_roles[uid]}
                        fake.realm_roles[uid] += [
                            r for r in json.loads(raw) if r["name"] not in have
                        ]
                    self._send(204)
                elif rest == ["role-mappings", "realm"] and method == "DELETE":
                    names = {r["name"] for r in json.loads(raw)}
                    fake.realm_roles[uid] = [
                        r for r in fake.realm_roles[uid] if r["name"] not in names
                    ]
                    self._send(204)
                elif rest[:2] == ["role-mappings", "clients"] and method == "DELETE":
                    assert rest[2] == CLIENT_UUID
                    names = {r["name"] for r in json.loads(raw)}
                    fake.client_roles[uid] = [
                        r for r in fake.client_roles[uid] if r["name"] not in names
                    ]
                    self._send(204)
                else:
                    self._send(405, {"error": "unsupported"})

            def do_GET(self) -> None:
                self._dispatch("GET")

            def do_POST(self) -> None:
                self._dispatch("POST")

            def do_PUT(self) -> None:
                self._dispatch("PUT")

            def do_DELETE(self) -> None:
                self._dispatch("DELETE")

        return Handler
