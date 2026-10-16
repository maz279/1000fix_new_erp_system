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

from src.dispatcher import Dispatcher, load_registry  # noqa: E402
from src.delivery import FALLBACK_REGISTER  # noqa: E402

HOST = "127.0.0.1"
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
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 - stdlib signature
        if self.path == "/health":
            self._json(200, {
                "status": "UP",
                "module": "M27",
                "cd": "CD-M27-nn",
                "wave": self.dispatcher.router.active_wave,
                "consent_classes": sorted(self.dispatcher.rules),
                "events": len(self.dispatcher.registry["event_matrix"]),
                "dry_run_default": True,
            })
        elif self.path == "/kpis":
            self._json(200, self.dispatcher.kpi_snapshot())
        elif self.path == "/dlq":
            records = self.dispatcher.tracker.dead_letters
            self._json(200, {"count": len(records), "records": [
                {"id": r.id, "event": r.event, "party_id": r.party_id, "state": r.state}
                for r in records
            ]})
        elif self.path == "/fallbacks":
            self._json(200, FALLBACK_REGISTER)
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib signature
        if self.path != "/consume/once":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            event = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        decisions = self.dispatcher.handle(event)
        self._json(200, {"decisions": decisions, "kpis": self.dispatcher.kpi_snapshot()})

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003, N802 - stdlib signature
        print(f"notification-dispatcher: {fmt % args}")


def serve() -> None:
    dispatcher = build_dispatcher()
    Handler.dispatcher = dispatcher
    server = HTTPServer((HOST, PORT), Handler)
    print(f"notification-dispatcher: listening on {HOST}:{PORT} (dry-run default; M27 / CD-M27-nn)")
    server.serve_forever()


if __name__ == "__main__":
    serve()
