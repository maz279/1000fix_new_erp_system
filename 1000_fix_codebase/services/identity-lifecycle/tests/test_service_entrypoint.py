"""identity-lifecycle entrypoint: DE-11 guard, fail-closed start, worker and ops HTTP."""

from __future__ import annotations

import http.client
import json
import os
import threading
import time
from collections import deque

import identity_lifecycle_service as svc
import pytest
from identity_lifecycle import Outcome

ENDPOINT_VARS = (
    "PGHOST",
    "DB_HOST",
    "DATABASE_URL",
    "S3_ENDPOINT",
    "SMTP_HOST",
    "REDIS_URL",
    "RESIDENCY_BASE",
    "KEYCLOAK_URL",
    "OTEL_EXPORTER_OTLP_ENDPOINT",
)


@pytest.fixture
def service_env(monkeypatch, kc_env):
    for var in ENDPOINT_VARS:
        monkeypatch.delenv(var, raising=False)
    for var in ("KEYCLOAK_ADMIN_CLIENT_SECRET", "IDENTITY_LIFECYCLE_LEDGER", svc.TOKEN_ENV):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("FIX_ENV", "local")
    for key, value in kc_env.items():
        monkeypatch.setenv(key, value)
    return monkeypatch


def _leave(buses, employee_id=5, code="EMP-0005"):
    buses["bus"].publish_dual(
        "employee.left",
        "hr.employee",
        employee_id,
        {"employee_id": employee_id, "employee_code": code, "keycloak_user_id": False},
    )


# --------------------------------------------------------------------------- environment guard


def test_local_with_loopback_keycloak_may_start(service_env):
    svc.check_environment()


def test_local_pointing_at_a_remote_keycloak_refuses_to_start(service_env, capsys):
    service_env.setenv("KEYCLOAK_URL", "https://auth.1000fix.com")
    with pytest.raises(SystemExit) as exc:
        svc.check_environment()
    assert exc.value.code == 42
    assert "KEYCLOAK_URL points at 'auth.1000fix.com'" in capsys.readouterr().err


def test_staging_and_production_may_start_and_other_environments_may_not(capsys):
    for name in ("staging", "prod", "production"):
        svc.check_environment({"FIX_ENV": name})
    for name in ("", "dev", "sandbox"):
        with pytest.raises(SystemExit) as exc:
            svc.check_environment({"FIX_ENV": name})
        assert exc.value.code == 42
    assert "FIX_ENV='sandbox'" in capsys.readouterr().err


def test_production_without_a_token_keeps_mutation_endpoints_closed():
    assert svc.ops_token_policy({"FIX_ENV": "production"}) == (None, False)


# --------------------------------------------------------------------------- main


def test_once_drains_and_reports(service_env, keycloak, buses, capsys):
    uid = keycloak.add_user("rina", "EMP-0005")
    _leave(buses)
    assert svc.main(["--once"]) == 0
    [outcome] = json.loads(capsys.readouterr().out)["outcomes"]
    assert (outcome["status"], outcome["keycloak_user_id"]) == ("deprovisioned", uid)
    assert keycloak.users[uid]["enabled"] is False


def test_once_exits_non_zero_when_a_leaver_could_not_be_deprovisioned(
    service_env, keycloak, buses, capsys
):
    _leave(buses, code="EMP-4040")
    assert svc.main(["--once"]) == 1
    assert json.loads(capsys.readouterr().out)["outcomes"][0]["status"] == "failed"


def test_missing_credentials_fail_closed_before_consuming(service_env, keycloak, buses, capsys):
    service_env.delenv("KEYCLOAK_ADMIN_PASSWORD")
    _leave(buses)
    assert svc.main(["--once"]) == svc.EX_CONFIG
    assert "refuses to start" in capsys.readouterr().err
    assert keycloak.calls == []
    # the leaver event is still unconsumed - nothing was acknowledged
    assert buses["migration"]._groups.get("identity-lifecycle") is None


def test_default_mode_serves(service_env, monkeypatch):
    served = []
    monkeypatch.setattr(svc, "serve", served.append)
    assert svc.main([]) == 0
    assert len(served) == 1 and served[0].client.config.realm == "1000fix-dev"


# --------------------------------------------------------------------------- worker


class _Stopper:
    def __init__(self, stop: threading.Event, result=None, error: Exception | None = None):
        self.stop, self.result, self.error, self.calls = stop, result or [], error, 0

    def drain(self):
        self.calls += 1
        self.stop.set()
        if self.error:
            raise self.error
        return self.result


def test_worker_records_outcomes_and_survives_a_failed_poll(capsys):
    stop = threading.Event()
    recent: deque = deque()
    ok = _Stopper(stop, [Outcome("deprovisioned", "e1"), Outcome("ignored", "e2")])
    svc.run_worker(ok, recent, stop, 0)
    assert [o["event_id"] for o in recent] == ["e1"]  # ignored events are not ops noise

    stop.clear()
    svc.run_worker(_Stopper(stop, error=RuntimeError("bus down")), recent, stop, 0)
    assert "drain failed: bus down" in capsys.readouterr().err


# --------------------------------------------------------------------------- ops HTTP


def _start_service(env_overrides=None):
    created = []

    class FastServer(svc.HTTPServer):
        def serve_forever(self, poll_interval=0.02):
            super().serve_forever(poll_interval)

    def factory(address, handler):
        server = FastServer(address, handler)
        created.append(server)
        return server

    from identity_lifecycle import IdentityLifecycle

    env = {**os.environ, **(env_overrides or {})}
    dep = IdentityLifecycle.from_env()
    thread = threading.Thread(target=svc.serve, args=(dep, factory, env), daemon=True)
    thread.start()
    deadline = time.monotonic() + 5
    while not created and time.monotonic() < deadline:
        time.sleep(0.01)
    return created[0], thread


@pytest.fixture
def running_service(service_env, keycloak, buses):
    service_env.setenv("IDENTITY_LIFECYCLE_PORT", "0")
    service_env.setenv("IDENTITY_LIFECYCLE_POLL_SECONDS", "0.05")
    created = []

    class FastServer(svc.HTTPServer):
        def serve_forever(self, poll_interval=0.02):
            super().serve_forever(poll_interval)

    def factory(address, handler):
        server = FastServer(address, handler)
        created.append(server)
        return server

    from identity_lifecycle import IdentityLifecycle

    dep = IdentityLifecycle.from_env()
    thread = threading.Thread(target=svc.serve, args=(dep, factory), daemon=True)
    thread.start()
    deadline = time.monotonic() + 5
    while not created and time.monotonic() < deadline:
        time.sleep(0.01)
    server = created[0]
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        thread.join(5)


def _request(port, method, path, body: bytes | None = None, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request(method, path, body=body, headers=headers or {})
    resp = conn.getresponse()
    data = json.loads(resp.read() or b"{}")
    conn.close()
    return resp.status, data


def test_worker_drains_the_bus_while_serving(running_service, keycloak, buses):
    uid = keycloak.add_user("rina", "EMP-0005")
    _leave(buses)
    deadline = time.monotonic() + 5
    outcomes = []
    while not outcomes and time.monotonic() < deadline:
        outcomes = _request(running_service, "GET", "/outcomes")[1]["outcomes"]
        time.sleep(0.02)
    assert outcomes[0]["keycloak_user_id"] == uid
    status, health = _request(running_service, "GET", "/health")
    assert status == 200
    assert health == {
        "status": "ok",
        "consumer_group": "identity-lifecycle",
        "keycloak_realm": "1000fix-dev",
        "processed_events": 1,
    }


def test_consume_once_and_drain_endpoints(running_service, keycloak, buses):
    uid = keycloak.add_user("rina", "EMP-0005")
    event = {
        "event_id": "evt-ops-1",
        "event_type": "employee.left",
        "payload": {"employee_id": 5, "employee_code": "EMP-0005", "keycloak_user_id": uid},
    }
    status, body = _request(running_service, "POST", "/consume/once", json.dumps(event).encode())
    assert status == 200 and body["outcome"]["status"] == "deprovisioned"
    status, body = _request(running_service, "POST", "/consume/once", json.dumps(event).encode())
    assert body["outcome"]["status"] == "duplicate"
    status, body = _request(running_service, "POST", "/drain")
    assert status == 200 and body == {"outcomes": []}


@pytest.mark.parametrize(
    ("method", "path", "body", "headers", "expected"),
    [
        ("GET", "/nope", None, None, (404, "not found")),
        ("POST", "/nope", b"{}", None, (404, "not found")),
        ("POST", "/consume/once", b"{oops", None, (400, "invalid json")),
        ("POST", "/consume/once", b"[1]", None, (400, "event must be a JSON object")),
        (
            "POST",
            "/consume/once",
            b"{}",
            {"Content-Length": "abc"},
            (400, "invalid content-length"),
        ),
        ("POST", "/consume/once", b"{}", {"Content-Length": "-1"}, (400, "invalid content-length")),
        (
            "POST",
            "/consume/once",
            b"{}",
            {"Content-Length": str(svc.MAX_BODY_BYTES + 1)},
            (400, "invalid content-length"),
        ),
    ],
)
def test_ops_endpoints_reject_bad_requests(running_service, method, path, body, headers, expected):
    status, data = _request(running_service, method, path, body, headers)
    assert (status, data["error"]) == expected


def test_an_empty_consume_body_is_an_ignored_event(running_service):
    status, data = _request(running_service, "POST", "/consume/once", b"", {"Content-Length": "0"})
    assert status == 200
    assert data["outcome"]["status"] == "ignored"
    assert "malformed event" in data["outcome"]["reason"]
    assert _request(running_service, "GET", "/outcomes")[1] == {"outcomes": []}


def test_entrypoint_bootstraps_its_import_path(monkeypatch):
    """In the container nothing pre-populates sys.path: the entrypoint adds src + root."""
    import importlib.util
    import sys
    from pathlib import Path

    path = Path(svc.__file__)
    src, root = str(path.parent), str(path.parents[3])
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p not in (src, root)])
    spec = importlib.util.spec_from_file_location("identity_lifecycle_entry_copy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert sys.path[:2] == [root, src]
    assert path.parents[3] == module.REPO_ROOT


# --------------------------------------------------------------------------- ops authorization


TOKEN = "s3cret-ops-token-for-tests"
PROTECTED = [("GET", "/outcomes"), ("POST", "/drain"), ("POST", "/consume/once")]


@pytest.fixture
def tokened_service(service_env, keycloak, buses):
    service_env.setenv("IDENTITY_LIFECYCLE_PORT", "0")
    service_env.setenv("IDENTITY_LIFECYCLE_POLL_SECONDS", "60")
    server, thread = _start_service({svc.TOKEN_ENV: TOKEN})
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        thread.join(5)


@pytest.mark.parametrize(("method", "path"), PROTECTED)
@pytest.mark.parametrize("supplied", [None, "", "wrong", TOKEN + "x"])
def test_ops_endpoints_refuse_a_missing_or_wrong_token(tokened_service, method, path, supplied):
    """Regression: /drain and /consume/once were unauthenticated and could
    disable or provision Keycloak users."""
    headers = {} if supplied is None else {svc.TOKEN_HEADER: supplied}
    status, data = _request(tokened_service, method, path, b"{}", headers)
    assert (status, data) == (401, {"error": "unauthorized"})


def test_ops_endpoints_accept_the_shared_token(tokened_service, keycloak):
    uid = keycloak.add_user("rina", "EMP-0005")
    event = {
        "event_id": "evt-tok-1",
        "event_type": "employee.left",
        "payload": {"employee_id": 5, "employee_code": "EMP-0005", "keycloak_user_id": uid},
    }
    headers = {svc.TOKEN_HEADER: TOKEN}
    status, body = _request(
        tokened_service, "POST", "/consume/once", json.dumps(event).encode(), headers
    )
    assert status == 200 and body["outcome"]["status"] == "deprovisioned"
    assert _request(tokened_service, "POST", "/drain", None, headers)[0] == 200
    assert _request(tokened_service, "GET", "/outcomes", None, headers)[0] == 200
    # liveness stays open for probes
    assert _request(tokened_service, "GET", "/health")[0] == 200


def test_ops_endpoints_are_disabled_without_a_token_outside_local(
    service_env, keycloak, buses, capsys
):
    service_env.setenv("IDENTITY_LIFECYCLE_PORT", "0")
    service_env.setenv("IDENTITY_LIFECYCLE_POLL_SECONDS", "60")
    server, thread = _start_service({"FIX_ENV": "staging"})
    try:
        port = server.server_address[1]
        for method, path in PROTECTED:
            status, data = _request(port, method, path, b"{}")
            assert status == 503 and svc.TOKEN_ENV in data["error"]
        assert _request(port, "GET", "/health")[0] == 200
    finally:
        server.shutdown()
        thread.join(5)
    assert "ops endpoints DISABLED" in capsys.readouterr().err


def test_ops_token_policy():
    assert svc.ops_token_policy({"FIX_ENV": "local"}) == (None, True)
    assert svc.ops_token_policy({"FIX_ENV": "staging"}) == (None, False)
    assert svc.ops_token_policy({"FIX_ENV": "staging", svc.TOKEN_ENV: " t "}) == ("t", False)
    assert svc.ops_token_policy({"FIX_ENV": "local", svc.TOKEN_ENV: "t"}) == ("t", False)
