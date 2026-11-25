"""GV-009: tooling/scripts/verify_pdm_closed_loop.py measures each closed-loop stage or
reports it UNMEASURED - the loop is never 'verified' while stages are unobserved, and a
broken M02 ranking is a FAIL (no hard-coded status PASS / closed_loop_verified True)."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_pdm_closed_loop.py"

PUBLISHER_SRC = """
class FixPredictiveMaintenance:
    _name = "fix.predictive.maintenance"

    def action_create_preventive_wo(self):
        publish(self.env, "predictive_maintenance.wo_created", "x", 1, {})
"""


def _load():
    spec = importlib.util.spec_from_file_location("verify_pdm_closed_loop_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fake_gateway(real, *, broken_ranking=False, with_pdm=False):
    fake = types.ModuleType("fake_ml_gateway_ut")
    fake.DispatchFeatures = real.DispatchFeatures

    def rank_technicians(features):
        ranked = real.rank_technicians(features)
        return list(reversed(ranked)) if broken_ranking else ranked

    rank_technicians.__module__ = fake.__name__
    fake.rank_technicians = rank_technicians
    if with_pdm:

        def predict_failure(*_args, **_kwargs):
            return None

        predict_failure.__module__ = fake.__name__
        fake.predict_failure = predict_failure
    return fake


class VerifyPdmClosedLoopTest(unittest.TestCase):
    def setUp(self):
        self.m = _load()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.m.EVIDENCE_PATH = self.root / "evidence" / "pdm.json"
        self.real_gateway = self.m.ml_gateway
        self.assertIsNotNone(self.real_gateway, "services/ml-gateway must import")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self) -> dict:
        res = self.m.PredictiveMaintenanceClosedLoopVerifier().run()
        on_disk = json.loads(self.m.EVIDENCE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["verdict"], res["verdict"])
        return res

    def _stage(self, res: dict, prefix: str) -> dict:
        return next(s for s in res["stages"] if s["stage"].startswith(prefix))

    def test_local_run_is_never_pass(self):
        res = self._run()
        self.assertNotEqual(res["verdict"], "PASS")
        self.assertFalse(res["closed_loop_verified"])
        for prefix in ("1_", "5_", "6_"):
            self.assertEqual(self._stage(res, prefix)["status"], "UNMEASURED")
        self.assertEqual(self._stage(res, "4_")["status"], "PASS")
        self.assertNotEqual(self.m.EXIT_CODES[res["verdict"]], 0)

    def test_broken_dispatch_ranking_fails(self):
        self.m.ml_gateway = _fake_gateway(self.real_gateway, broken_ranking=True)
        res = self._run()
        self.assertEqual(self._stage(res, "4_")["status"], "FAIL")
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["status"], "FAIL")

    def test_missing_gateway_fails_prediction_and_dispatch(self):
        self.m.ml_gateway = None
        res = self._run()
        self.assertEqual(self._stage(res, "2_")["status"], "FAIL")
        self.assertEqual(self._stage(res, "4_")["status"], "FAIL")
        self.assertEqual(res["verdict"], "FAIL")

    def test_all_wiring_present_is_incomplete_not_pass(self):
        publisher = self.root / "addons" / "pdm_model.py"
        publisher.parent.mkdir(parents=True)
        publisher.write_text(PUBLISHER_SRC, encoding="utf-8")
        consumer = self.root / "services" / "wo" / "consumer.py"
        consumer.parent.mkdir(parents=True)
        consumer.write_text('EVENT = "predictive_maintenance.wo_created"\n', encoding="utf-8")
        self.m.PDM_MODEL_FILE = publisher
        self.m.CONSUMER_SCAN_ROOTS = [self.root / "addons", self.root / "services"]
        self.m.REPO_ROOT = self.root
        self.m.ml_gateway = _fake_gateway(self.real_gateway, with_pdm=True)
        res = self._run()
        self.assertEqual(self._stage(res, "2_")["status"], "UNMEASURED")
        self.assertEqual(self._stage(res, "3_")["status"], "UNMEASURED")
        self.assertEqual(self._stage(res, "4_")["status"], "PASS")
        self.assertEqual(res["verdict"], "INCOMPLETE")
        self.assertFalse(res["closed_loop_verified"])

    def test_missing_consumer_fails_work_order_stage(self):
        publisher = self.root / "addons" / "pdm_model.py"
        publisher.parent.mkdir(parents=True)
        publisher.write_text(PUBLISHER_SRC, encoding="utf-8")
        self.m.PDM_MODEL_FILE = publisher
        self.m.CONSUMER_SCAN_ROOTS = [self.root / "addons"]
        self.m.REPO_ROOT = self.root
        res = self._run()
        stage = self._stage(res, "3_")
        self.assertEqual(stage["status"], "FAIL")
        self.assertEqual(stage["consumers"], [])


if __name__ == "__main__":
    unittest.main()
