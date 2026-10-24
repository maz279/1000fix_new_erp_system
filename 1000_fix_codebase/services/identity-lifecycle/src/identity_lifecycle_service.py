"""identity-lifecycle service — M29 joiner/leaver worker (FR-SEC-027, KPI-090).

A worker thread drains ``employee.joined`` / ``employee.left`` from the bus through libs/py/fix_events
(FF-28) every IDENTITY_LIFECYCLE_POLL_SECONDS; HTTP exists for operations only:

  GET  /health        liveness - Keycloak configured, consumer group, ledger size
  GET  /outcomes      the most recent provisioning / deprovisioning outcomes   [token]
  POST /consume/once  handle one event body (operations / replay)              [token]
  POST /drain         drain the bus now                                        [token]

Authorization: the [token] endpoints disable / provision Keycloak users, so
they require the shared secret IDENTITY_LIFECYCLE_TOKEN in the
``X-Identity-Lifecycle-Token`` header (constant-time compare). Without a
configured token they are open ONLY in FIX_ENV=local (loopback dev); in any
other environment they answer 503 - the bus worker keeps running.

Usage:  python -m identity_lifecycle_service [--once]
"""

from __future__ import annotations

import hmac
import json
import os
import sys
import threading
from collections import deque
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

SRC_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("FIX_REPO_ROOT") or SRC_DIR.parents[2])
for _path in (str(SRC_DIR), str(REPO_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from identity_lifecycle import (  # noqa: E402
    CONSUMER_GROUP,
    IdentityLifecycle,
    Outcome,
    outcome_dict,
)
from keycloak_admin import KeycloakConfigError  # noqa: E402

from libs.py.fix_env_guard import assert_local  # noqa: E402

EX_CONFIG = 78  # sysexits.h: configuration error - the service refuses to run
MAX_BODY_BYTES = 64 * 1024
TOKEN_ENV = "IDENTITY_LIFECYCLE_TOKEN"  # noqa: S105 - env var NAME, not a secret
TOKEN_HEADER = "X-Identity-Lifecycle-Token"  # noqa: S105 - header name
PROTECTED_PATHS = frozenset({"/outcomes", "/consume/once", "/drain"})


def ops_token_policy(env: dict[str, str] | None = None) -> tuple[str | None, bool]:
    """(token, open_without_token) for the protected ops endpoints.

    A configured token is always required. Without one the endpoints are open
    only in the synthetic local environment; elsewhere they are disabled."""
    env = dict(os.environ) if env is None else env
    token = (env.get(TOKEN_ENV) or "").strip() or None
    return token, token is None and env.get("FIX_ENV") == "local"


RUNNABLE_ENVS = ("staging", "prod", "production")


def check_environment(env: dict[str, str] | None = None) -> None:
    """DE-11: local must never reach a non-local endpoint. Staging and
    production run too; outside local the mutation endpoints stay closed
    (503) unless IDENTITY_LIFECYCLE_TOKEN is set (ops_token_policy)."""
    env = dict(os.environ) if env is None else env
    fix_env = env.get("FIX_ENV", "")
    if fix_env == "local":
        assert_local()
    elif fix_env not in RUNNABLE_ENVS:
        print(f"identity-lifecycle: refusing to start: FIX_ENV={fix_env!r}", file=sys.stderr)
        raise SystemExit(42)


class Handler(BaseHTTPRequestHandler):
    lifecycle: IdentityLifecycle
    recent: deque[dict[str, Any]]
    token: str | None = None
    open_without_token: bool = False

    def _authorized(self) -> bool:
        """Gate for PROTECTED_PATHS; answers 401/503 itself when refused."""
        if self.path not in PROTECTED_PATHS:
            return True
        if self.token is None:
            if self.open_without_token:
                return True
            self._json(503, {"error": f"ops endpoints disabled: {TOKEN_ENV} is not configured"})
            return False
        supplied = self.headers.get(TOKEN_HEADER) or ""
        if hmac.compare_digest(supplied.encode("utf-8"), self.token.encode("utf-8")):
            return True
        self._json(401, {"error": "unauthorized"})
        return False

    def _json(self, code: int, body: dict[str, Any]) -> None:
        data = json.dumps(body, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        # NFR-092 / PE-08: correlation-id + traceparent on every response.
        for header, value in getattr(self, "_trace_headers", {}).items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(data)
        if hasattr(self, "_observe"):
            try:
                from libs.py.fix_telemetry import end_http

                end_http(code)
            except ImportError:
                pass

    def _observe(self) -> None:
        try:
            from libs.py.fix_telemetry import observe_http

            _, headers = observe_http(
                "identity-lifecycle",
                self.path,
                dict(self.headers.items()),
            )
            self._trace_headers = headers
        except ImportError:
            self._trace_headers = {}

    def do_GET(self) -> None:
        self._observe()
        if not self._authorized():
            return
        if self.path == "/health":
            self._json(
                200,
                {
                    "status": "ok",
                    "consumer_group": CONSUMER_GROUP,
                    "keycloak_realm": self.lifecycle.client.config.realm,
                    "processed_events": len(self.lifecycle.ledger),
                },
            )
        elif self.path == "/outcomes":
            self._json(200, {"outcomes": list(self.recent)})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        self._observe()
        if not self._authorized():
            return
        if self.path == "/drain":
            outcomes = record(self.recent, self.lifecycle.drain())
            self._json(200, {"outcomes": outcomes})
            return
        if self.path != "/consume/once":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY_BYTES:
            self._json(400, {"error": "invalid content-length"})
            return
        try:
            event = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            self._json(400, {"error": "invalid json"})
            return
        if not isinstance(event, dict):
            self._json(400, {"error": "event must be a JSON object"})
            return
        outcome = self.lifecycle.handle(event)
        record(self.recent, [outcome])  # ignored events are answered, not kept
        self._json(200, {"outcome": outcome_dict(outcome)})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"identity-lifecycle: {fmt % args}")


def record(recent: deque[dict[str, Any]], outcomes: list[Outcome]) -> list[dict[str, Any]]:
    rendered = [outcome_dict(o) for o in outcomes if o.status != "ignored"]
    recent.extend(rendered)
    return rendered


def run_worker(
    lifecycle: IdentityLifecycle,
    recent: deque[dict[str, Any]],
    stop: threading.Event,
    interval: float,
) -> None:
    """Drain until stopped; a failed drain is logged and retried on the next tick."""
    while not stop.is_set():
        try:
            record(recent, lifecycle.drain())
        except Exception as exc:  # the worker must outlive one bad poll
            print(f"identity-lifecycle: drain failed: {exc}", file=sys.stderr)
        stop.wait(interval)


def serve(
    lifecycle: IdentityLifecycle,
    server_factory: Callable[..., HTTPServer] = HTTPServer,
    env: dict[str, str] | None = None,
) -> None:
    env = dict(os.environ) if env is None else env
    host = env.get("IDENTITY_LIFECYCLE_HOST") or "127.0.0.1"
    port = int(env.get("IDENTITY_LIFECYCLE_PORT") or "8120")
    interval = float(env.get("IDENTITY_LIFECYCLE_POLL_SECONDS") or "15")
    recent: deque[dict[str, Any]] = deque(maxlen=200)
    Handler.lifecycle = lifecycle
    Handler.recent = recent
    Handler.token, Handler.open_without_token = ops_token_policy(env)
    if Handler.token is None:
        state = "OPEN (FIX_ENV=local)" if Handler.open_without_token else "DISABLED"
        print(
            f"identity-lifecycle: {TOKEN_ENV} not set - ops endpoints {state}",
            file=sys.stderr,
        )
    stop = threading.Event()
    worker = threading.Thread(
        target=run_worker, args=(lifecycle, recent, stop, interval), daemon=True
    )
    worker.start()
    server = server_factory((host, port), Handler)
    print(f"identity-lifecycle: listening on {host}:{port}, draining every {interval}s")
    try:
        server.serve_forever()
    finally:
        stop.set()
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    check_environment()
    try:
        lifecycle = IdentityLifecycle.from_env()
    except KeycloakConfigError as exc:
        print(str(exc), file=sys.stderr)
        return EX_CONFIG
    if "--once" in args:
        outcomes = [outcome_dict(o) for o in lifecycle.drain()]
        print(json.dumps({"outcomes": outcomes}, default=str))
        return 1 if any(o["status"] == "failed" for o in outcomes) else 0
    serve(lifecycle)
    return 0


if __name__ == "__main__":
    sys.exit(main())
