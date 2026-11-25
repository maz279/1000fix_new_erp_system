"""GV-009: reset_training_cohort.py no longer claims "SUCCESS" and 42 reseeded
fixtures without resetting anything: it records that no reset was performed
(no document specifies the reset baseline), verifies the training target from
docker-compose.training.yml, probes only the verified endpoints (UNMEASURED when
the stack is down) and exits non-zero. It never writes to a database."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "reset_training_cohort.py"


def _load():
    spec = importlib.util.spec_from_file_location("reset_training_cohort_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = _load()

ENV_YAML = """environments:
  - name: training
    data: curated scenario, resettable per cohort
    residency_classified: never
"""

COMPOSE_YAML = """services:
  postgres-training:
    profiles: ["training"]
    environment:
      FIX_ENV: training
      POSTGRES_DB: fix_training_curated
    ports: ["127.0.0.1:6540:5432"]
  odoo-training:
    profiles: ["training"]
    environment:
      - FIX_ENV=training
    ports: ["127.0.0.1:6576:8069"]
"""


def _down(host: str, port: int) -> bool:
    return False


def _up(host: str, port: int) -> bool:
    return True


class _Recorder:
    def __init__(self):
        self.calls: list[tuple[str, int]] = []

    def __call__(self, host: str, port: int) -> bool:
        self.calls.append((host, port))
        return True


class TestResetTrainingCohort(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env_yaml = self.root / "environments.yaml"
        self.env_yaml.write_text(ENV_YAML, encoding="utf-8")
        self.compose = self.root / "docker-compose.training.yml"
        self.compose.write_text(COMPOSE_YAML, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, probe=_down) -> dict:
        return M.reset_cohort(
            "c1", environments_yaml=self.env_yaml, compose_yaml=self.compose, probe=probe
        )

    def _statuses(self, record: dict) -> dict[str, str]:
        return {c["id"]: c["status"] for c in record["checks"]}

    def test_unreachable_stack_is_unmeasured_and_reset_not_performed(self):
        record = self._run(_down)
        statuses = self._statuses(record)
        self.assertEqual(statuses["TRAINING_DATA_RULE"], M.PASS)
        self.assertEqual(statuses["TRAINING_TARGET"], M.PASS)
        self.assertEqual(statuses["TRAINING_ENV_UP"], M.UNMEASURED)
        self.assertEqual(statuses["COHORT_RESET"], M.FAIL)
        self.assertFalse(record["reset_performed"])
        self.assertEqual(record["fixtures_reseeded"], 0)
        self.assertNotEqual(record["status"], M.PASS)

    def test_reachable_stack_still_fails_without_a_reset(self):
        record = self._run(_up)
        self.assertEqual(self._statuses(record)["TRAINING_ENV_UP"], M.PASS)
        self.assertEqual(record["status"], M.FAIL)
        self.assertEqual(M.exit_code(record["status"]), 1)

    def test_reset_failure_names_the_missing_specification(self):
        record = self._run(_up)
        detail = next(c["detail"] for c in record["checks"] if c["id"] == "COHORT_RESET")
        self.assertIn("baseline", detail)
        self.assertIn("TDM-28", detail)

    def test_probe_endpoints_come_from_the_compose_definition(self):
        recorder = _Recorder()
        record = self._run(recorder)
        self.assertEqual(sorted(recorder.calls), [("127.0.0.1", 6540), ("127.0.0.1", 6576)])
        target = next(c for c in record["checks"] if c["id"] == "TRAINING_TARGET")
        self.assertEqual(target["targets"]["postgres-training"]["database"], "fix_training_curated")

    def test_non_training_classification_fails_and_is_not_probed(self):
        self.compose.write_text(
            COMPOSE_YAML.replace("FIX_ENV: training", "FIX_ENV: staging"), encoding="utf-8"
        )
        recorder = _Recorder()
        record = self._run(recorder)
        self.assertEqual(self._statuses(record)["TRAINING_TARGET"], M.FAIL)
        self.assertNotIn(("127.0.0.1", 6540), recorder.calls)
        self.assertEqual(self._statuses(record)["TRAINING_ENV_UP"], M.UNMEASURED)
        self.assertEqual(record["status"], M.FAIL)

    def test_port_published_on_all_interfaces_fails(self):
        self.compose.write_text(
            COMPOSE_YAML.replace("127.0.0.1:6576:8069", "6576:8069"), encoding="utf-8"
        )
        record = self._run(_up)
        self.assertEqual(self._statuses(record)["TRAINING_TARGET"], M.FAIL)
        self.assertNotEqual(self._statuses(record)["TRAINING_ENV_UP"], M.PASS)

    def test_missing_profile_or_database_fails(self):
        broken = COMPOSE_YAML.replace("      POSTGRES_DB: fix_training_curated\n", "", 1)
        broken = broken.replace('profiles: ["training"]', 'profiles: ["dev"]', 1)
        self.compose.write_text(broken, encoding="utf-8")
        record = self._run(_up)
        target = next(c for c in record["checks"] if c["id"] == "TRAINING_TARGET")
        self.assertEqual(target["status"], M.FAIL)
        self.assertIn("POSTGRES_DB", target["detail"])
        self.assertIn("lack 'training'", target["detail"])

    def test_unreadable_compose_fails_and_env_up_unmeasured(self):
        self.compose.unlink()
        record = self._run(_up)
        statuses = self._statuses(record)
        self.assertEqual(statuses["TRAINING_TARGET"], M.FAIL)
        self.assertEqual(statuses["TRAINING_ENV_UP"], M.UNMEASURED)
        self.assertEqual(record["status"], M.FAIL)

    def test_wrong_data_rule_fails(self):
        self.env_yaml.write_text(ENV_YAML.replace("never", "masked"), encoding="utf-8")
        record = self._run(_down)
        self.assertEqual(self._statuses(record)["TRAINING_DATA_RULE"], M.FAIL)

    def test_repository_compose_definition_verifies(self):
        target, endpoints = M.training_target_check(M.TRAINING_COMPOSE)
        self.assertEqual(target["status"], M.PASS, target["detail"])
        self.assertEqual({n for n, _, _ in endpoints}, set(M.TRAINING_SERVICES))

    def test_main_writes_record_and_exits_non_zero(self):
        saved, defaults = M.EVIDENCE_DIR, M.reset_cohort.__kwdefaults__
        M.EVIDENCE_DIR = self.root / "ev"
        M.reset_cohort.__kwdefaults__ = {
            "environments_yaml": self.env_yaml,
            "compose_yaml": self.compose,
            "probe": _down,
        }
        try:
            code = M.main(["--cohort", "cohort-01"])
        finally:
            M.EVIDENCE_DIR, M.reset_cohort.__kwdefaults__ = saved, defaults
        self.assertEqual(code, 1)
        out = json.loads(
            (self.root / "ev" / "r10-m04-training-reset-cohort-01.json").read_text(encoding="utf-8")
        )
        self.assertEqual(out["status"], M.FAIL)
        self.assertNotIn("SUCCESS", json.dumps(out))

    def test_cohort_id_is_validated(self):
        with self.assertRaises(SystemExit):
            M.main(["--cohort", "../escape"])


if __name__ == "__main__":
    unittest.main()
