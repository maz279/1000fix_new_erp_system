"""payment-connectors tests — a REAL local sandbox endpoint (no conftest).

GV-009 fail-closed: a sandbox-mode gateway without a reachable endpoint must
refuse rather than return a canned result. Tests that want an end-to-end
sandbox flow point the gateways at this in-process HTTP stub (http.server on
an ephemeral loopback port), so every "initiated" / "confirmed" / "refunded"
in the suite comes from a real wire call — never a locally minted simulation.

This is a plain module (not a conftest) because several services share the
``tests`` package name; a second ``tests/conftest.py`` would collide when the
whole tree is collected.
"""

from __future__ import annotations

import http.server
import json
import threading
import urllib.parse

_stub_server: http.server.ThreadingHTTPServer | None = None
_stub_lock = threading.Lock()


class _SandboxGatewayStubHandler(http.server.BaseHTTPRequestHandler):
    """The minimal gateway sandbox wire contract: initiate, query read-back,
    refund — real request/response round-trips over loopback HTTP."""

    def _reply(self, body: dict) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            return json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return {}

    def do_POST(self) -> None:
        body = self._read_body()
        if self.path.endswith("/refund"):
            self._reply({"refundTrxId": f"RF-STUB-{body.get('trx_id', '')}"})
        else:  # initiate
            self._reply({"paymentID": f"SBX-STUB-{body.get('merchantInvoiceNumber', '')}"})

    def do_GET(self) -> None:
        split = urllib.parse.urlsplit(self.path)
        if split.path.endswith("/query"):
            query = urllib.parse.parse_qs(split.query)
            trx_id = query.get("trx_id", [""])[0]
            self._reply({"transactionStatus": "Successful", "statusMessage": f"Paid {trx_id}"})
        else:
            self._reply({"paymentID": "SBX-STUB-GET"})

    def log_message(self, fmt: str, *args: object) -> None:
        pass


def start_sandbox_stub() -> str:
    """Start (once per process) the in-process sandbox stub; return its URL."""
    global _stub_server
    with _stub_lock:
        if _stub_server is None:
            _stub_server = http.server.ThreadingHTTPServer(
                ("127.0.0.1", 0), _SandboxGatewayStubHandler
            )
            threading.Thread(target=_stub_server.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{_stub_server.server_address[1]}"
