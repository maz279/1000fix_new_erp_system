"""ml-gateway tests — P09-M06 (CD-M26-01)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ml_gateway
from ml_gateway import (
    DispatchFeatures,
    detect_drift,
    forecast_demand,
    get_model_info,
    get_model_lineage,
    rank_technicians,
    rollback_model,
    score_dispatch,
    trigger_retraining,
)


class _RegistryIsolation(unittest.TestCase):
    """Snapshots the shared registry around every test in this module."""

    @classmethod
    def setUpClass(cls):
        cls._registry = json.dumps(ml_gateway.MODEL_REGISTRY, default=str)
        cls._log = list(ml_gateway.RETRAINING_LOG)

    @classmethod
    def tearDownClass(cls):
        import copy

        restored = json.loads(cls._registry)
        ml_gateway.MODEL_REGISTRY.clear()
        ml_gateway.MODEL_REGISTRY.update(restored)
        # rebuild the history lists as independent objects
        for card in ml_gateway.MODEL_REGISTRY.values():
            card["history"] = copy.deepcopy(card.get("history", []))
        ml_gateway.RETRAINING_LOG[:] = cls._log


class TestDispatchScoring(_RegistryIsolation):
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


class TestRanking(_RegistryIsolation):
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


class TestDemandForecast(_RegistryIsolation):
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


class TestModelOps(_RegistryIsolation):
    def test_model_registry_has_both_models(self):
        self.assertIsNotNone(get_model_info("dispatch-scoring"))
        self.assertIsNotNone(get_model_info("demand-forecast"))

    def test_registry_carries_no_invented_metrics_or_lineage(self):
        """GV-009: no trained backend exists, so every card must carry EMPTY
        metrics and None lineage - never fabricated accuracies, mlflow run ids
        or s3 datasets."""
        for name in ("dispatch-scoring", "demand-forecast", "bengali-stt"):
            info = get_model_info(name)
            self.assertEqual(info["metrics"], {}, name)
            self.assertIsNone(info["lineage"]["mlflow_run_id"], name)
            self.assertIsNone(info["lineage"]["training_dataset"], name)
            self.assertNotIn("s3://", json.dumps(info), name)
            self.assertIn(info["stage"], ("heuristic", "not-deployed"), name)
        self.assertEqual(get_model_info("dispatch-scoring")["model_backend"], "heuristic-v1")

    def test_scores_are_labelled_heuristic(self):
        result = score_dispatch(DispatchFeatures("T1"))
        self.assertEqual(result.model_backend, "heuristic-v1")

    def test_drift_detection(self):
        self.assertTrue(detect_drift("m", actual=100, predicted=120))
        self.assertFalse(detect_drift("m", actual=100, predicted=110))

    def test_retraining_trigger_records_event_without_inventing_metrics(self):
        event = trigger_retraining(
            "dispatch-scoring", "Drift exceeded 15% threshold on FTF accuracy"
        )
        self.assertEqual(event["model_name"], "dispatch-scoring")
        self.assertEqual(event["from_version"], "1.0.0")
        self.assertEqual(event["to_version"], "1.1.0")
        # Bookkeeping only - no training pipeline ran, so nothing "completed"
        # and no post-retraining accuracy is fabricated.
        self.assertEqual(event["status"], "recorded")

        info = get_model_info("dispatch-scoring")
        self.assertEqual(info["version"], "1.1.0")
        self.assertEqual(info["stage"], "retrain-requested")
        self.assertEqual(info["metrics"], {})

    def test_model_lineage(self):
        lineage_info = get_model_lineage("demand-forecast")
        self.assertEqual(lineage_info["model_name"], "demand-forecast")
        self.assertIn("training_dataset", lineage_info["lineage"])
        self.assertIn("feature_pipeline", lineage_info["lineage"])
        # UNMEASURED metrics: present but empty, never invented.
        self.assertEqual(lineage_info["metrics"], {})

    def test_model_rollback(self):
        # Trigger retraining so 1.0.0 is placed into history, then rollback to 1.0.0
        trigger_retraining("dispatch-scoring", "Drift test")
        res = rollback_model("dispatch-scoring", "1.0.0")
        self.assertEqual(res["active_version"], "1.0.0")
        self.assertEqual(res["status"], "rolled_back")

        info = get_model_info("dispatch-scoring")
        self.assertEqual(info["version"], "1.0.0")
        self.assertEqual(info["stage"], "heuristic")  # prior stage restored


if __name__ == "__main__":
    unittest.main()
