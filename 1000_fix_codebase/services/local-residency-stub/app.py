"""Local residency service stub - P02-M05-T09 / DE-14 / FF-09.

SYNTHETIC VALUES ONLY. This stub is *structurally incapable* of connecting to
a real resident store: it opens no outbound connection of any kind, and the
values it returns are deterministic fakes derived from the input key. FF-09
is satisfied locally by the impossibility of a real value existing, not by a
check.

The real client contract lives in libs/py/fix_residency (the ONLY client of
the production residency service, CD-M29-nn). This stub speaks that contract.
"""
import hashlib
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

SYNTHETIC_BANNER = "SYNTHETIC-LOCAL-ONLY"


def synthetic_value(key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{SYNTHETIC_BANNER}-{digest}"


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, body: dict) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "UP", "mode": "synthetic-only"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path == "/assert-local":
            # DE-11 companion: the stub refuses anything but FIX_ENV=local.
            self._json(200, {"fix_env": "local", "ok": True})
            return
        if self.path in ("/put", "/get", "/erase"):
            length = int(self.headers.get("Content-Length", "0"))
            try:
                req = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._json(400, {"error": "invalid json"})
                return
            key = str(req.get("key", ""))
            if not key:
                self._json(400, {"error": "key required"})
                return
            if self.path == "/put":
                self._json(200, {"stored": True, "value_kind": "synthetic", "key": key})
            elif self.path == "/get":
                self._json(200, {"key": key, "value": synthetic_value(key), "kind": "synthetic"})
            else:  # erase
                self._json(200, {"erased": True, "key": key, "tombstone": synthetic_value("tombstone:" + key)})
            return
        self._json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003 - stdlib signature
        print(f"residency-stub: {fmt % args}")


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8100), Handler)
    print("residency-stub: listening on 127.0.0.1:8100 (SYNTHETIC VALUES ONLY)")
    server.serve_forever()
