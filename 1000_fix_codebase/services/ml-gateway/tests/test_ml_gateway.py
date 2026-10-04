"""ml-gateway tests — P09-M06 (CD-M26-01)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ml_gateway import (  # noqa: E402
    DispatchFeatures, detect_drift, forecast_demand, get_model_info,
    rank_technicians, score_dispatch)


class TestDispatchScoring(unittest.TestCase):
    def test_certified_beats_uncertified(self):
        cert = score_dispatch(DispatchFeatures("T1", certification_active=True))
        uncert = score_dispatch(DispatchFeatures("T2", certification_active=False))
        self.assertGreater(cert.score, uncert.score)

    def test_high_ftf_scores_higher(self):
        good = score_dispatch(DispatchFeatures("T1", historical_ftf=0.9))
        bad = score_dispatch(DispatchFeatures("T2", historical_ftf=0.3))
        self.assertGreater(good.score, bad.score)

    def test_workload_penalises(self):
        idle = score_dispatch(DispatchFeatures("T1", workload_today=0))
        busy = score_dispatch(DispatchFeatures("T1", workload_today=5))
        self.assertGreater(idle.score, busy.score)

    def test_score_is_explainable(self):
        result = score_dispatch(DispatchFeatures("T1"))
        self.assertIn("certification", result.factors)
        self.assertIn("first_time_fix", result.factors)


class TestRanking(unittest.TestCase):
    def test_ranking_orders_by_score(self):
        techs = [
            DispatchFeatures("A", historical_ftf=0.3),
            DispatchFeatures("B", historical_ftf=0.9),
            DispatchFeatures("C", historical_ftf=0.6),
        ]
        ranked = rank_technicians(techs)
        self.assertEqual(ranked[0].technician_id, "B")
        self.assertEqual(ranked[-1].technician_id, "A")

    def test_uncertified_always_last(self):
        techs = [
            DispatchFeatures("certified", certification_active=True, historical_ftf=0.1),
            DispatchFeatures("uncertified", certification_active=False, historical_ftf=1.0),
        ]
        ranked = rank_technicians(techs)
        self.assertEqual(ranked[-1].technician_id, "uncertified")


class TestDemandForecast(unittest.TestCase):
    def test_forecast_produces_periods(self):
        history = [("2026-01", 100), ("2026-02", 110), ("2026-03", 105)]
        forecasts = forecast_demand(history, periods_ahead=3)
        self.assertEqual(len(forecasts), 3)
        self.assertEqual(forecasts[0].period, "t+1")

    def test_confidence_degrades(self):
        history = [("2026-01", 100)]
        forecasts = forecast_demand(history, periods_ahead=3)
        self.assertGreater(forecasts[0].confidence, forecasts[2].confidence)

    def test_empty_history_returns_empty(self):
        self.assertEqual(forecast_demand([]), [])


class TestModelOps(unittest.TestCase):
    def test_model_registry_has_both_models(self):
        self.assertIsNotNone(get_model_info("dispatch-scoring"))
        self.assertIsNotNone(get_model_info("demand-forecast"))

    def test_drift_detection(self):
        self.assertTrue(detect_drift("m", actual=100, predicted=120))
        self.assertFalse(detect_drift("m", actual=100, predicted=110))


if __name__ == "__main__":
    unittest.main()
