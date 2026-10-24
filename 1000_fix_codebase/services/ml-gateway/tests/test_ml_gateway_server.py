"""ml-gateway HTTP server tests (src/main.py) - stdlib http.server.

The server runs in-process on an ephemeral port; requests go through
http.client against a real socket (no network beyond loopback).
"""

from __future__ import annotations

import http.client
import json
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import main as ml_server


class _Server:
    def __init__(self) -> None:
        self.server = ml_server.HTTPServer(("127.0.0.1", 0), ml_server.Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            payload = json.dumps(body).encode() if body is not None else None
            headers = {"Content-Type": "application/json"} if payload else {}
            conn.request(method, path, body=payload, headers=headers)
            resp = conn.getresponse()
            return resp.status, json.loads(resp.read().decode())
        finally:
            conn.close()


class TestMlGatewayServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = _Server()
        cls.srv.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.stop()

    def test_health_is_honest(self):
        status, payload = self.srv.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "healthy")
        self.assertEqual(payload["model_backend"], "heuristic-v1")
        # Honest: no trained model is deployed.
        self.assertFalse(payload["trained_model_deployed"])

    def test_dispatch_ranks_and_labels_the_heuristic(self):
        status, payload = self.srv.request(
            "POST",
            "/v1/dispatch",
            {
                "candidates": [
                    {"technician_id": "T1", "historical_ftf": 0.9},
                    {"technician_id": "T2", "historical_ftf": 0.4},
                ]
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["model_backend"], "heuristic-v1")
        self.assertIn("weights", payload)  # the heuristic's weights are exposed
        self.assertEqual(payload["ranking"][0]["technician_id"], "T1")
        self.assertEqual(payload["ranking"][1]["technician_id"], "T2")
        self.assertIn("certification", payload["ranking"][0]["factors"])
        # No invented accuracy metrics ride along.
        self.assertNotIn("accuracy", json.dumps(payload))
        self.assertNotIn("mlflow", json.dumps(payload))

    def test_dispatch_rejects_bad_payloads(self):
        for body in ({}, {"candidates": []}, {"candidates": [{"technician_id": "T", "bogus": 1}]}):
            status, payload = self.srv.request("POST", "/v1/dispatch", body)
            self.assertEqual(status, 400, body)
            self.assertIn("error", payload)

    def test_forecast_endpoint(self):
        status, payload = self.srv.request(
            "POST",
            "/v1/forecast",
            {"history": [["2026-01", 100], ["2026-02", 110]], "periods_ahead": 2},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["model_backend"], "heuristic-v1")
        self.assertEqual(len(payload["forecast"]), 2)
        self.assertEqual(payload["forecast"][0]["period"], "t+1")

    def test_model_card_exposes_unmeasured_metrics(self):
        status, payload = self.srv.request("GET", "/v1/models/bengali-stt")
        self.assertEqual(status, 200)
        self.assertEqual(payload["metrics"], {})
        self.assertIsNone(payload["lineage"]["mlflow_run_id"])

        status, _ = self.srv.request("GET", "/v1/models/ghost")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
