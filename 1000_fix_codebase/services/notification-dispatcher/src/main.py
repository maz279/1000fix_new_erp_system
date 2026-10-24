"""HTTP surface for the notification dispatcher.

Endpoints:
  GET  /health        liveness — registry loaded, rule table built
  GET  /kpis          the four KPI families (P04-M05-T10)
  GET  /dlq           dead-letter queue (never-silent-drop evidence)
  GET  /fallbacks     the IP-09 P0 fallback register (P04-M05-T09)
  POST /consume/once  drain one event from the outbox via libs/py/fix_events
                      (FF-28) — the long-running drain loop uses the same call

The long-running deployment does not serve HTTP on the send path: events flow
fix_events.consume(handler=dispatcher.handle). HTTP exists for operations.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libs" / "py"))

from src.delivery import FALLBACK_REGISTER
from src.dispatcher import Dispatcher, load_registry

# Bind address: loopback unless the deployment says otherwise. The container
# image sets FIX_NOTIFICATION_DISPATCHER_HOST=0.0.0.0 (in-container bind; the
# published/cluster port is the only way in - compose publishes on loopback,
# production reaches it only through Kong/NetworkPolicy).
HOST = os.environ.get("FIX_NOTIFICATION_DISPATCHER_HOST", "").strip() or "127.0.0.1"
PORT = int(os.environ.get("FIX_NOTIFICATION_DISPATCHER_PORT", "8110"))


def build_dispatcher() -> Dispatcher:
    return Dispatcher(registry=load_registry(), active_wave=os.environ.get("FIX_ACTIVE_WAVE", "W1"))


class Handler(BaseHTTPRequestHandler):
    dispatcher: Dispatcher  # injected by serve()

    def _json(self, code: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        # NFR-092 / PE-08: correlation-id + traceparent on every response.
        for header, value in getattr(self, "_trace_headers", {}).items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(payload)
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
                "notification-dispatcher",
                self.path,
                dict(self.headers.items()),
            )
            self._trace_headers = headers
        except ImportError:
            self._trace_headers = {}

    def do_GET(self) -> None:
        self._observe()
        if self.path == "/health":
            self._json(
                200,
                {
                    "status": "UP",
                    "module": "M27",
                    "cd": "CD-M27-nn",
                    "wave": self.dispatcher.router.active_wave,
                    "consent_classes": sorted(self.dispatcher.rules),
                    "events": len(self.dispatcher.router.matrix),  # event rows only
                    "dry_run_default": True,
                },
            )
        elif self.path == "/kpis":
            self._json(200, self.dispatcher.kpi_snapshot())
        elif self.path == "/dlq":
            records = self.dispatcher.tracker.dead_letters
            self._json(
                200,
                {
                    "count": len(records),
                    "records": [
                        {"id": r.id, "event": r.event, "party_id": r.party_id, "state": r.state}
                        for r in records
                    ],
                },
            )
        elif self.path == "/fallbacks":
            self._json(200, FALLBACK_REGISTER)
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        self._observe()
        if self.path != "/consume/once":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0:
            # A negative length would read "until EOF" — on a live socket that
            # blocks this single-threaded server.
            self._json(400, {"error": "invalid content-length"})
            return
        try:
            event = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:  # JSONDecodeError and UnicodeDecodeError alike
            self._json(400, {"error": "invalid json"})
            return
        if not isinstance(event, dict):
            self._json(400, {"error": "event must be a JSON object"})
            return
        decisions = self.dispatcher.handle(event)
        self._json(200, {"decisions": decisions, "kpis": self.dispatcher.kpi_snapshot()})

    def log_message(self, fmt: str, *args) -> None:
        print(f"notification-dispatcher: {fmt % args}")


def serve() -> None:
    dispatcher = build_dispatcher()
    Handler.dispatcher = dispatcher
    server = HTTPServer((HOST, PORT), Handler)
    print(f"notification-dispatcher: listening on {HOST}:{PORT} (dry-run default; M27 / CD-M27-nn)")
    server.serve_forever()


if __name__ == "__main__":
    serve()
