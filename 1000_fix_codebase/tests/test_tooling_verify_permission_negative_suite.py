"""GV-009: verify-permission-negative-suite.py measures every check - an
unreachable database is UNMEASURED (never PASS), a missing role or a red suite
is FAIL, and the overall verdict / exit code are derived from the checks."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify-permission-negative-suite.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_permission_negative_suite_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()

ROLES = "\n".join(mod.EXPECTED_ROLES)
TIERS = "\n".join(mod.EXPECTED_TIERS)
SODS = "\n".join(mod.EXPECTED_SOD_CONTROLS)


def fake_db(roles=ROLES, tiers=TIERS, sods=SODS, t5="t|t"):
    def query(sql: str) -> str:
        if "fix_role" in sql:
            return roles
        if "requires_step_up" in sql:
            return t5
        if "fix_isolation_tier" in sql:
            return tiers
        if "fix_sod_control" in sql:
            return sods
        raise AssertionError(sql)

    return query


def green_suite(target: str) -> dict:
    return {"status": mod.PASS, "target": target, "tests_run": 3, "tests_passed": 3}


class TestPermissionSuiteVerdicts(unittest.TestCase):
    def test_all_measured_green_is_pass(self):
        ev = mod.build_evidence(query_fn=fake_db(), pytest_fn=green_suite)
        self.assertEqual(ev["overall_verdict"], "PASS")
        self.assertEqual(mod.exit_code_for(ev["overall_verdict"]), 0)

    def test_unreachable_database_is_unmeasured_not_pass(self):
        def down(_sql):
            raise mod.InfraUnavailable("docker/psql not runnable: no daemon")

        ev = mod.build_evidence(query_fn=down, pytest_fn=green_suite)
        for key in ("roles", "isolation_tiers", "sod_controls", "t5_invariants"):
            self.assertEqual(ev["results"][key]["status"], "UNMEASURED", key)
        self.assertEqual(ev["overall_verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(ev["overall_verdict"]), 2)

    def test_missing_role_fails(self):
        roles = "\n".join(mod.EXPECTED_ROLES[:-1])
        ev = mod.build_evidence(query_fn=fake_db(roles=roles), pytest_fn=green_suite)
        self.assertEqual(ev["results"]["roles"]["status"], "FAIL")
        self.assertEqual(ev["results"]["roles"]["missing"], ["R-53"])
        self.assertEqual(ev["results"]["roles"]["actual_count"], 52)
        self.assertEqual(ev["overall_verdict"], "FAIL")
        self.assertEqual(mod.exit_code_for(ev["overall_verdict"]), 1)

    def test_t5_flag_off_or_missing_row_fails(self):
        self.assertEqual(mod.check_t5_invariants(fake_db(t5="t|f"))["status"], "FAIL")
        self.assertEqual(mod.check_t5_invariants(fake_db(t5=""))["status"], "FAIL")

    def test_red_suite_fails_overall(self):
        def red(target):
            return {"status": mod.FAIL, "target": target, "tests_run": 3, "tests_passed": 2}

        ev = mod.build_evidence(query_fn=fake_db(), pytest_fn=red)
        self.assertEqual(ev["overall_verdict"], "FAIL")

    def test_all_skipped_suite_is_unmeasured(self):
        with tempfile.TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "test_skipped_only.py"
            test_file.write_text(
                textwrap.dedent(
                    """
                    import pytest

                    @pytest.mark.skip(reason="no runtime")
                    def test_nothing():
                        pass
                    """
                ),
                encoding="utf-8",
            )
            res = mod.run_pytest(str(test_file))
        self.assertEqual(res["status"], "UNMEASURED", res)
        self.assertEqual(res["tests_skipped"], 1)

    def test_main_writes_derived_verdict_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "evidence.json"
            orig_file, orig_build = mod.EVIDENCE_FILE, mod.build_evidence
            mod.EVIDENCE_FILE = out
            mod.build_evidence = lambda: orig_build(
                query_fn=fake_db(sods="SOD-01"), pytest_fn=green_suite
            )
            try:
                code = mod.main()
            finally:
                mod.EVIDENCE_FILE, mod.build_evidence = orig_file, orig_build
            data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(code, 1)
        self.assertEqual(data["overall_verdict"], "FAIL")
        self.assertEqual(data["results"]["sod_controls"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
