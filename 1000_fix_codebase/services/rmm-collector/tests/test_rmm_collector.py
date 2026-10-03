"""rmm-collector tests — P08-M07-T04. Evaluation core, 100% of paths."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rmm_collector import (  # noqa: E402
    AlertDecision, OdooClient, Telemetry, evaluate, validate_target)


class TestEvaluation(unittest.TestCase):
    def test_offline_reports_major(self):
        d = evaluate([], Telemetry("A1", "offline"))
        self.assertEqual((d.severity, d.agent_id), ("major", "A1"))

    def test_degraded_reports_minor_with_flags(self):
        d = evaluate([], Telemetry("A2", "degraded", flags=["disk", "cpu"]))
        self.assertEqual(d.severity, "minor")
        self.assertIn("disk", d.message)

    def test_degraded_without_flags_names_it(self):
        d = evaluate([], Telemetry("A3", "degraded"))
        self.assertIn("unspecified", d.message)

    def test_healthy_never_alerts(self):
        self.assertIsNone(evaluate([], Telemetry("A4", "healthy")))

    def test_heartbeat_gap_alerts(self):
        history = [Telemetry("A5", "healthy", reported_at=1_000.0)]
        late = Telemetry("A5", "healthy", reported_at=1_000.0 + 61 * 3)
        d = evaluate(history, late)
        self.assertIsNotNone(d)
        self.assertEqual(d.severity, "major")
        self.assertIn("silent", d.message)

    def test_normal_cadence_no_alert(self):
        history = [Telemetry("A6", "healthy", reported_at=1_000.0)]
        on_time = Telemetry("A6", "healthy", reported_at=1_060.0)
        self.assertIsNone(evaluate(history, on_time))

    def test_first_report_healthy_no_gap_logic(self):
        # no history -> no gap computation possible
        self.assertIsNone(evaluate([], Telemetry("A7", "healthy")))


class TestBoundary(unittest.TestCase):
    def test_non_local_target_refused(self):
        with self.assertRaises(ValueError):
            validate_target("http://192.168.1.5:8069/x")
        with self.assertRaises(ValueError):
            validate_target("http://127.0.0.1:9999/x")

    def test_local_target_allowed(self):
        validate_target("http://127.0.0.1:8069/x")  # no raise
        validate_target("http://localhost:8069/y")


if __name__ == "__main__":
    unittest.main()
