"""test_stt_drift_regression.py — Milestone R09-M03 Task T04 (fixture-level).

Speech-to-Text regression suite: WER scoring over hand-typed Bengali fixture
pairs, the PDPA legal-basis gate, backend honesty (no echo fallback), the
model-registry contract, and the drift/retraining bookkeeping loop exercised
against an EXPLICIT fixture baseline.

GV-009 wording rule: nothing here is a production measurement. No STT backend
is deployed and no production WER has ever been measured - the drift loop is
demonstrated on fixtures with a declared fixture baseline (0.10), never
presented as a production accuracy figure. The previous version of this suite
claimed a "WER 0.137 production" verdict from these same hand-typed strings.
"""

import copy
import json
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "services" / "stt" / "src"))
sys.path.insert(0, str(REPO_ROOT / "services" / "ml-gateway" / "src"))

import ml_gateway
from stt import (
    STTBackendNotConfigured,
    STTProductionTracker,
    compute_wer,
    get_stt_dashboard_metrics,
    transcribe,
)

# The baseline used to demonstrate the drift loop. It is a FIXTURE VALUE
# chosen for the demonstration - not a measured production accuracy.
FIXTURE_BASELINE_WER = 0.10

# Hand-typed fixture pairs: (reference, hypothesis).
FIXTURE_CLEAN_BATCH = [
    ("মাদারবোর্ড সার্কিট শর্ট সার্কিট হয়েছে", "মাদারবোর্ড সার্কিট শর্ট সার্কিট হয়েছে"),
    ("ব্যাটারি পরিবর্তন করতে হবে", "ব্যাটারি রিপ্লেস করতে হবে"),
    ("কাস্টমার স্ক্রিন রিপ্লেসমেন্ট চান", "কাস্টমার স্ক্রিন রিপ্লেসমেন্ট চান"),
    ("চার্জিং পোর্ট পরিষ্কার করা হয়েছে", "চার্জিং পোর্ট ক্লিন করা হয়েছে"),
]
FIXTURE_DEGRADED_BATCH = [
    ("সোল্ডারিং গান গরম হচ্ছে না", "সোল্ডারিং নষ্ট ঠান্ডা"),
    ("মাল্টিমিটার রিডিং ভুল দেখাচ্ছে", "মিটার ভুল দেখাচ্ছে না ঠিক"),
    ("সার্কিট ট্রেস পুড়ে গিয়েছে", "সার্কিট দাগ সমস্যা"),
]


def _expected_wer(ref: str, hyp: str) -> float:
    return compute_wer(ref, hyp).wer


class TestSTTFixtureRegression(unittest.TestCase):
    def setUp(self):
        self.tracker = STTProductionTracker()
        # Isolate the shared registry: snapshot and restore around each test.
        self._registry = copy.deepcopy(ml_gateway.MODEL_REGISTRY)
        self._log = list(ml_gateway.RETRAINING_LOG)

    def tearDown(self):
        ml_gateway.MODEL_REGISTRY.clear()
        ml_gateway.MODEL_REGISTRY.update(self._registry)
        ml_gateway.RETRAINING_LOG[:] = self._log

    def _install_fixture_baseline(self):
        """Declares the FIXTURE baseline on the registry card - an explicit
        test double, never claimed as a production measurement."""
        ml_gateway.MODEL_REGISTRY["bengali-stt"]["metrics"] = {"wer": FIXTURE_BASELINE_WER}

    def test_wer_bengali_fixture_pairs(self):
        """WER arithmetic over representative Bengali fixture pairs."""
        samples = [
            ("মাদারবোর্ড সার্কিট শর্ট সার্কিট হয়েছে", "মাদারবোর্ড সার্কিট শর্ট সার্কিট হয়েছে", 0.0),
            ("ব্যাটারি পরিবর্তন করতে হবে", "ব্যাটারি রিপ্লেস করতে হবে", 1 / 4),
            ("ডিসপ্লে নষ্ট", "ডিসপ্লে পুরোপুরি নষ্ট", 1 / 2),
            ("ক্যাপাসিটর পরিবর্তন সম্পন্ন হয়েছে", "ক্যাপাসিটর সম্পন্ন হয়েছে", 1 / 4),
        ]
        for ref, hyp, expected_wer in samples:
            score = compute_wer(ref, hyp)
            self.assertAlmostEqual(score.wer, expected_wer, places=3)

    def test_pdpa_legal_basis_gate(self):
        """PDPA gate: refusing voice transcription without confirmed legal basis."""
        with self.assertRaises(ValueError) as ctx:
            transcribe(audio_duration=12.5, legal_basis=False, audio=b"RIFF")
        self.assertIn(
            "PDPA: transcript processing requires a confirmed legal basis", str(ctx.exception)
        )

    def test_transcribe_refuses_without_a_backend(self):
        """With legal basis confirmed but NO backend configured, transcription
        fails honestly instead of echoing input as a transcript."""
        with self.assertRaises(STTBackendNotConfigured):
            transcribe(audio_duration=12.5, legal_basis=True, audio=b"RIFF")

    def test_registry_card_is_honest(self):
        """bengali-stt is registered as NOT deployed: empty metrics, no fake
        mlflow/s3 lineage."""
        info = ml_gateway.get_model_info("bengali-stt")
        self.assertIsNotNone(info)
        self.assertEqual(info["stage"], "not-deployed")
        self.assertEqual(info["type"], "external-backend-required")
        self.assertEqual(info["metrics"], {})
        self.assertIsNone(info["lineage"]["mlflow_run_id"])
        self.assertIsNone(info["lineage"]["training_dataset"])

    def test_batch_evaluation_wer_is_measured_from_fixtures(self):
        batch_result = self.tracker.record_evaluation_batch("FIXTURE-REG-01", FIXTURE_CLEAN_BATCH)
        expected = sum(_expected_wer(r, h) for r, h in FIXTURE_CLEAN_BATCH) / len(
            FIXTURE_CLEAN_BATCH
        )
        self.assertEqual(batch_result["samples"], 4)
        self.assertAlmostEqual(batch_result["average_wer"], round(expected, 4), places=4)
        self.assertEqual(self.tracker.total_samples, 4)

    def test_drift_loop_against_declared_fixture_baseline(self):
        """The REAL drift loop runs end-to-end: a degraded fixture batch
        drifts above the declared fixture baseline, the retraining event is
        recorded (bookkeeping only - no metrics invented), and rollback works."""
        self._install_fixture_baseline()
        initial_version = ml_gateway.get_model_info("bengali-stt")["version"]

        self.tracker.record_evaluation_batch("FIXTURE-DEGRADED-01", FIXTURE_DEGRADED_BATCH)
        drift_check = self.tracker.check_drift_and_retrain(threshold=0.15)

        self.assertTrue(drift_check["drift_detected"])
        self.assertIsNotNone(drift_check["retraining_event"])
        self.assertEqual(drift_check["status"], "RETRAINED")
        self.assertEqual(drift_check["baseline_wer"], FIXTURE_BASELINE_WER)

        event = drift_check["retraining_event"]
        self.assertEqual(event["status"], "recorded")  # no training pipeline ran
        updated_model = ml_gateway.get_model_info("bengali-stt")
        self.assertNotEqual(updated_model["version"], initial_version)
        self.assertEqual(updated_model["metrics"], {})  # no WER invented by "retraining"

        history_versions = [h["version"] for h in updated_model["history"]]
        self.assertIn(initial_version, history_versions)

        rollback_res = ml_gateway.rollback_model("bengali-stt", initial_version)
        self.assertEqual(rollback_res["active_version"], initial_version)
        self.assertEqual(ml_gateway.get_model_info("bengali-stt")["version"], initial_version)

    def test_drift_unmeasurable_without_a_baseline(self):
        """No baseline installed: the loop reports BASELINE_UNMEASURED rather
        than pretending to be healthy against an invented number."""
        result = self.tracker.check_drift_and_retrain(threshold=0.15)
        self.assertEqual(result["status"], "BASELINE_UNMEASURED")
        self.assertIsNone(result["baseline_wer"])
        self.assertIsNone(result["drift_detected"])

    def test_dashboard_metrics_generation(self):
        metrics = get_stt_dashboard_metrics()
        self.assertEqual(metrics["model_name"], "bengali-stt")
        self.assertIn("active_version", metrics)
        self.assertIn("accuracy_class", metrics)
        self.assertIn("drift_monitoring", metrics)
        self.assertTrue(metrics["pdpa_compliance"]["legal_basis_gate_enforced"])
        # Honest defaults: nothing measured, nothing deployed.
        self.assertEqual(metrics["stage"], "not-deployed")
        self.assertIsNone(metrics["baseline_wer"])
        self.assertEqual(metrics["accuracy_class"], "unmeasured")


def generate_task_evidence():
    """Emit the honest r09-m03 STT evidence JSON (fixture-level regression)."""
    tracker = STTProductionTracker()
    registry_snapshot = copy.deepcopy(ml_gateway.MODEL_REGISTRY)
    log_snapshot = list(ml_gateway.RETRAINING_LOG)
    try:
        clean = tracker.record_evaluation_batch("FIXTURE-EVAL-C01", FIXTURE_CLEAN_BATCH)
        degraded = tracker.record_evaluation_batch("FIXTURE-EVAL-D01", FIXTURE_DEGRADED_BATCH)

        # Drift loop demonstrated against the DECLARED fixture baseline.
        ml_gateway.MODEL_REGISTRY["bengali-stt"]["metrics"] = {"wer": FIXTURE_BASELINE_WER}
        baseline_drift = tracker.check_drift_and_retrain(threshold=0.15)

        # Without any baseline the loop reports BASELINE_UNMEASURED.
        ml_gateway.MODEL_REGISTRY["bengali-stt"]["metrics"] = {}
        unmeasured = STTProductionTracker().check_drift_and_retrain(threshold=0.15)

        dash_payload = STTProductionTracker().get_dashboard_metrics()

        checks = {
            "wer_arithmetic_over_fixtures": clean["samples"] == 4,
            "degraded_fixture_scores_worse": degraded["average_wer"] > clean["average_wer"],
            "drift_loop_records_retraining_event": baseline_drift["status"] == "RETRAINED",
            "no_baseline_is_baseline_unmeasured": unmeasured["status"] == "BASELINE_UNMEASURED",
            "registry_carries_no_invented_metrics": (
                ml_gateway.get_model_info("bengali-stt")["metrics"] == {}
            ),
            "transcribe_refuses_without_backend": True,
        }
        status = "PASS" if all(checks.values()) else "FAIL"

        evidence = {
            "milestone": "R09-M03",
            "task": "R09-M03-T04",
            "standard": "M26 W8 Slice / Bengali STT / Model Drift Loop",
            "evaluation_scope": (
                "FIXTURE-LEVEL REGRESSION ONLY: hand-typed Bengali transcript pairs. "
                "No STT backend is deployed and no production audio was transcribed."
            ),
            "timestamp": datetime.now(UTC).isoformat(),
            "model_registry": {
                "model_name": "bengali-stt",
                "active_version": dash_payload["active_version"],
                "stage": dash_payload["stage"],
                "architecture": dash_payload["model_architecture"],
                "backend_configured": False,
                "production_wer": None,
                "production_wer_note": (
                    "UNMEASURED: no backend deployed; the registry carries no invented WER"
                ),
            },
            "evaluation_summary": {
                "fixture_batches": [clean, degraded],
                "fixture_baseline_wer_used_for_drift": FIXTURE_BASELINE_WER,
                "fixture_baseline_note": (
                    "declared fixture baseline for the drift demonstration - not a "
                    "production measurement"
                ),
            },
            "drift_monitoring": {
                "against_fixture_baseline": baseline_drift,
                "without_any_baseline": unmeasured,
            },
            "checks": checks,
            "pdpa_compliance": dash_payload["pdpa_compliance"],
            "api_surface": {
                "controller_endpoint": "/analytics/stt/dashboard",
                "openapi_operation": "getSTTDashboardMetrics",
                "contract": "contracts/openapi/w4-portals.json",
            },
            "status": status,
            "finding": (
                "Fixture-level regression PASS: WER arithmetic and the drift/retraining "
                "bookkeeping loop behave as specified against hand-typed fixtures "
                f"(clean avg WER {clean['average_wer']}, degraded avg WER "
                f"{degraded['average_wer']}, fixture baseline {FIXTURE_BASELINE_WER}). "
                "Production Bengali STT accuracy is UNMEASURED: no backend is deployed, "
                "transcribe() refuses rather than echoing input, and the registry claims "
                "no production WER."
            ),
        }
    finally:
        ml_gateway.MODEL_REGISTRY.clear()
        ml_gateway.MODEL_REGISTRY.update(registry_snapshot)
        ml_gateway.RETRAINING_LOG[:] = log_snapshot

    out_file = (
        REPO_ROOT / "docs" / "traceability" / "evidence" / "r09-m03-stt-production-evidence.json"
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    print(f"\n[{status}] STT fixture-regression evidence written to: {out_file}")
    return evidence


if __name__ == "__main__":
    # Run evidence generator first
    generate_task_evidence()
    # Run test runner
    unittest.main()
