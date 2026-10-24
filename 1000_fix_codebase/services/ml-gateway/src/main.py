"""ml-gateway HTTP server (CD-M26-01) — stdlib http.server, like the sibling
services (see services/notification-dispatcher/src/main.py).

Endpoints:
- GET  /health          — honest liveness: up, with the model backend label.
- POST /v1/dispatch     — rank technicians via the LABELLED heuristic scorer.
- POST /v1/forecast     — demand forecast via the labelled smoothing baseline.
- GET  /v1/models/<name>— registry card (no invented metrics; empty = unmeasured).

Every inference response carries ``model_backend: heuristic-v1`` and the
weights in use, so no consumer can mistake the heuristic for a trained model.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ml_gateway
from ml_gateway import (
    MODEL_BACKEND_LABEL,
    WEIGHTS,
    DispatchFeatures,
    forecast_demand,
    get_model_info,
    rank_technicians,
)

HOST = os.environ.get("ML_GATEWAY_HOST", "0.0.0.0")  # noqa: S104 - in-container bind; published on loopback only (DE-04)
PORT = int(os.environ.get("ML_GATEWAY_PORT", "8090"))

KNOWN_FIELDS = set(DispatchFeatures.__dataclass_fields__)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        # NFR-092 / PE-08: correlation-id + traceparent on every response
        # (R01 re-audit 2026-10-23) - spans started in _observe.
        for header, value in getattr(self, "_trace_headers", {}).items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(body)
        if hasattr(self, "_observe"):
            from libs.py.fix_telemetry import end_http

            end_http(status)

    def _observe(self) -> None:
        """Start the request span + collect response trace headers."""
        try:
            from libs.py.fix_telemetry import observe_http

            _, headers = observe_http(
                "ml-gateway",
                self.path,
                dict(self.headers.items()),
            )
            self._trace_headers = headers
        except ImportError:
            self._trace_headers = {}

    def _read_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return None

    def do_GET(self) -> None:
        self._observe()
        if self.path == "/health":
            self._send(
                200,
                {
                    "status": "healthy",
                    "service": "ml-gateway",
                    "model_backend": MODEL_BACKEND_LABEL,
                    "trained_model_deployed": False,  # honest: heuristic only
                    "models": sorted(ml_gateway.MODEL_REGISTRY),
                },
            )
            return

        if self.path.startswith("/v1/models/"):
            name = self.path[len("/v1/models/") :].strip("/")
            info = get_model_info(name)
            if info is None:
                self._send(404, {"error": f"unknown model: {name}"})
            else:
                self._send(200, info)
            return

        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        self._observe()
        if self.path == "/v1/dispatch":
            body = self._read_json()
            if body is None:
                self._send(400, {"error": "invalid JSON body"})
                return
            candidates = body.get("candidates")
            if not isinstance(candidates, list) or not candidates:
                self._send(400, {"error": "body must contain a non-empty 'candidates' list"})
                return

            features: list[DispatchFeatures] = []
            for i, c in enumerate(candidates):
                if not isinstance(c, dict):
                    self._send(400, {"error": f"candidates[{i}] must be an object"})
                    return
                unknown = set(c) - KNOWN_FIELDS
                if unknown:
                    self._send(
                        400, {"error": f"candidates[{i}] has unknown fields: {sorted(unknown)}"}
                    )
                    return
                try:
                    features.append(DispatchFeatures(**c))
                except TypeError as exc:
                    self._send(400, {"error": f"candidates[{i}]: {exc}"})
                    return

            ranked = rank_technicians(features)
            self._send(
                200,
                {
                    "model_backend": MODEL_BACKEND_LABEL,
                    "weights": WEIGHTS,
                    "ranking": [
                        {
                            "technician_id": s.technician_id,
                            "score": s.score,
                            "factors": s.factors,
                        }
                        for s in ranked
                    ],
                },
            )
            return

        if self.path == "/v1/forecast":
            body = self._read_json()
            if body is None:
                self._send(400, {"error": "invalid JSON body"})
                return
            history = body.get("history")
            periods = body.get("periods_ahead", 3)
            if (
                not isinstance(history, list)
                or not history
                or not all(isinstance(h, list | tuple) and len(h) == 2 for h in history)
            ):
                self._send(
                    400,
                    {"error": "body must contain a non-empty 'history' of [period, value] pairs"},
                )
                return
            try:
                periods = int(periods)
            except (TypeError, ValueError):
                self._send(400, {"error": "periods_ahead must be an integer"})
                return

            forecasts = forecast_demand([(str(p), float(v)) for p, v in history], periods)
            self._send(
                200,
                {
                    "model_backend": MODEL_BACKEND_LABEL,
                    "forecast": [
                        {
                            "period": f.period,
                            "forecast_quantity": f.forecast_quantity,
                            "confidence": f.confidence,
                        }
                        for f in forecasts
                    ],
                },
            )
            return

        self._send(404, {"error": "not found"})

    def log_message(self, fmt: str, *args: object) -> None:  # concise logs
        print(f"[ml-gateway] {self.address_string()} {fmt % args}", flush=True)


def main() -> int:
    server = HTTPServer((HOST, PORT), Handler)
    print(
        f"[ml-gateway] listening on {HOST}:{PORT} "
        f"(model_backend={MODEL_BACKEND_LABEL}, trained_model_deployed=False)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
