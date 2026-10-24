"""GV-009: drill_build_once_promote.py no longer hashes a string into a "digest"
or reports probes it never sent: unconfigured probes, digests and the rollback
rehearsal are UNMEASURED, failed probes are FAIL, and GP-12 is never discharged
on an unmeasured drill."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "drill_build_once_promote.py"


def _load():
    spec = importlib.util.spec_from_file_location("drill_build_once_promote_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()


class TestGp12Drill(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.evidence = Path(self.tmp.name)
        self.saved = M.http_status

    def tearDown(self):
        M.http_status = self.saved
        self.tmp.cleanup()

    def test_unconfigured_infra_is_unmeasured_not_discharged(self):
        ev = M.run_build_once_promote_drill(self.evidence, environ={})
        self.assertEqual(ev["status"], "INCOMPLETE")
        self.assertFalse(ev["gp_12_discharged"])
        self.assertEqual(M.exit_code(ev["status"]), 2)
        self.assertIsNone(ev["immutable_digest"])
        self.assertTrue(all(p["status"] == "UNMEASURED" for p in ev["promotion_ladder"]))
        self.assertTrue(all(p["probes_sent"] == 0 for p in ev["promotion_ladder"]))
        self.assertEqual(ev["rollback_rehearsal"]["status"], "UNMEASURED")
        written = json.loads((self.evidence / M.EVIDENCE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(written["status"], "INCOMPLETE")

    def test_failing_probe_fails_the_drill(self):
        M.http_status = lambda url: 503
        environ = {"GP12_HEALTHZ_URL_DEV": "http://example.invalid/healthz"}
        ev = M.run_build_once_promote_drill(self.evidence, environ=environ)
        dev = next(p for p in ev["promotion_ladder"] if p["environment"] == "dev")
        self.assertEqual(dev["status"], "FAIL")
        self.assertEqual(dev["probes_passed"], 0)
        self.assertEqual(ev["status"], "FAIL")
        self.assertEqual(M.exit_code(ev["status"]), 1)

    def test_healthy_probes_alone_do_not_discharge_gp12(self):
        M.http_status = lambda url: 200
        environ = {f"GP12_HEALTHZ_URL_{e.upper()}": f"http://h/{e}" for e in M.ENVIRONMENTS}
        ev = M.run_build_once_promote_drill(self.evidence, environ=environ)
        self.assertTrue(all(p["status"] == "PASS" for p in ev["promotion_ladder"]))
        self.assertEqual(ev["status"], "INCOMPLETE")
        self.assertFalse(ev["gp_12_discharged"])

    def test_silent_endpoint_is_unmeasured(self):
        M.http_status = lambda url: None
        ev = M.run_build_once_promote_drill(
            self.evidence, environ={"GP12_HEALTHZ_URL_SIT": "http://h/sit"}
        )
        sit = next(p for p in ev["promotion_ladder"] if p["environment"] == "sit")
        self.assertEqual(sit["status"], "UNMEASURED")


if __name__ == "__main__":
    unittest.main()
