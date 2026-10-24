"""GV-009: run_r11_m03_security_review.py measures its 24 vectors - an
unreachable Odoo is UNMEASURED (never PASS), a scanned defect is FAIL with a
derived finding count, and rotation / custody / SIEM claims that need
production or a human are UNMEASURED, so the verdict cannot be PASS."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "run_r11_m03_security_review.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_r11_m03_security_review_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()

CLEAN_COMPOSE = textwrap.dedent(
    """
    services:
      postgres:
        image: postgres@sha256:aaaa
        ports: ["127.0.0.1:5433:5432"]
    """
)
LEAKY_COMPOSE = textwrap.dedent(
    """
    services:
      postgres:
        image: postgres:17
        ports:
          - "0.0.0.0:5432:5432"
    """
)
DIRTY_PY = textwrap.dedent(
    """
    import subprocess


    def run(cr, name):
        cr.execute(f"SELECT * FROM {name}")
        subprocess.run(name, shell=True)
    """
)
REVIEWED_PY = textwrap.dedent(
    """
    def count(cr, table):
        cr.execute(f'SELECT count(*) FROM "{table}"')  # noqa: S608 - table is a repo constant
    """
)


def _tree(root: Path, compose: str, py: str) -> None:
    (root / "infra" / "compose").mkdir(parents=True)
    (root / "infra" / "compose" / "docker-compose.yml").write_text(compose, encoding="utf-8")
    ctl = root / "addons" / "cd_x" / "controllers"
    ctl.mkdir(parents=True)
    (ctl / "main.py").write_text(py, encoding="utf-8")
    (root / "FORKS.yaml").write_text("forks: []\n", encoding="utf-8")


def unreachable(method, path, jsonrpc=False):
    return {"reachable": False, "status": None, "location": "", "body": "", "error": "refused"}


def green_fitness(name):
    return "PASS", f"{name} exit 0: OK"


def green_pytest(target):
    return "PASS", f"pytest {target}: 1 passed"


def vendor_ok():
    return 0, "check-vendor-clean: OK"


def _by_code(result):
    return {v["code"]: v for v in result["vectors"]}


class TestPentestDelta(unittest.TestCase):
    def run_delta(self, compose, py, http=unreachable):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, compose, py)
            return mod.run_post_cutover_pentest_delta(
                root=root,
                http=http,
                fitness=green_fitness,
                pytest_fn=green_pytest,
                vendor_clean=vendor_ok,
            )

    def test_unreachable_target_is_unmeasured_never_pass(self):
        res = self.run_delta(CLEAN_COMPOSE, "x = 1\n")
        vec = _by_code(res)
        self.assertEqual(res["total_vectors"], 24)
        self.assertEqual(vec["A01-01"]["status"], "UNMEASURED")
        self.assertEqual(vec["A05-01"]["status"], "UNMEASURED")
        self.assertEqual(res["failed"], 0)
        self.assertEqual(res["status"], "INCOMPLETE")

    def test_scanned_defects_fail_with_derived_findings(self):
        res = self.run_delta(LEAKY_COMPOSE, DIRTY_PY)
        vec = _by_code(res)
        for code in ("A03-01", "A03-02", "A05-03", "A08-02"):
            self.assertEqual(vec[code]["status"], "FAIL", code)
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(res["critical_findings"], 2)  # A03-01 + A03-02
        self.assertEqual(res["high_findings"], 1)  # A05-03
        self.assertEqual(res["medium_findings"], 1)  # A08-02

    def test_reviewed_s608_interpolation_is_not_a_finding(self):
        vec = _by_code(self.run_delta(CLEAN_COMPOSE, REVIEWED_PY))
        self.assertEqual(vec["A03-01"]["status"], "PASS")
        self.assertIn("1 more carry a reviewed", vec["A03-01"]["details"])

    def test_private_key_in_source_fails(self):
        key = "-----BEGIN " + "RSA PRIVATE KEY-----\nMIIB\n"
        vec = _by_code(self.run_delta(CLEAN_COMPOSE, f"KEY = '''{key}'''\n"))
        self.assertEqual(vec["A02-01"]["status"], "FAIL")

    def test_served_route_and_traceback_fail(self):
        def leaky(method, path, jsonrpc=False):
            if jsonrpc:
                body = json.dumps(
                    {"error": {"data": {"debug": "Traceback (most recent call last):"}}}
                )
                return {"reachable": True, "status": 200, "location": "", "body": body}
            if path == "/my":
                return {"reachable": True, "status": 200, "location": "", "body": "<html>data"}
            return {"reachable": True, "status": 404, "location": "", "body": "not found"}

        vec = _by_code(self.run_delta(CLEAN_COMPOSE, "x = 1\n", http=leaky))
        self.assertEqual(vec["A01-01"]["status"], "FAIL")
        self.assertIn("GET /my", vec["A01-01"]["details"])
        self.assertEqual(vec["A05-01"]["status"], "FAIL")

    def test_redirect_to_login_is_a_rejection(self):
        res = {"reachable": True, "status": 303, "location": "/web/login?redirect=/my", "body": ""}
        self.assertTrue(mod._probe_rejected(res, jsonrpc=False))
        self.assertIsNone(mod._probe_rejected({"reachable": True, "status": 404}, jsonrpc=False))


class TestOtherSections(unittest.TestCase):
    def test_ep06_measured_and_env_restored(self):
        before = os.environ.get("FIX_ENV")
        res = mod.execute_vault_secret_checks()
        self.assertEqual(os.environ.get("FIX_ENV"), before)
        self.assertEqual(res["checks"]["ep06_prod_enforcement"]["status"], "PASS")
        self.assertEqual(res["checks"]["production_secret_rotation"]["status"], "UNMEASURED")
        self.assertEqual(res["status"], "INCOMPLETE")

    def test_wazuh_is_unmeasured_whether_or_not_ports_answer(self):
        self.assertEqual(
            mod.verify_wazuh_osquery_alerting(lambda h, p: False)["status"], "UNMEASURED"
        )
        self.assertEqual(
            mod.verify_wazuh_osquery_alerting(lambda h, p: True)["status"], "UNMEASURED"
        )

    def test_report_verdict_is_derived_and_markdown_unsigned(self):
        pentest = {
            "status": "PASS",
            "passed": 24,
            "failed": 0,
            "unmeasured": 0,
            "total_vectors": 24,
        }
        pentest.update(critical_findings=0, high_findings=0, medium_findings=0, vectors=[])
        secrets = {"status": "PASS", "checks": {}}
        custody = mod.verify_key_custody_transfer()
        wazuh = mod.verify_wazuh_osquery_alerting(lambda h, p: False)
        rep = mod.build_report(pentest, secrets, custody, wazuh)
        self.assertEqual(rep["verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(rep["verdict"]), 2)
        md = mod.render_markdown(rep)
        self.assertIn("**`INCOMPLETE`**", md)
        self.assertNotIn("CISSP", md)


if __name__ == "__main__":
    unittest.main()
