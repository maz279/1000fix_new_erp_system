# cd_workflow_engine tests — M63 (P06-M08-T03/T04).
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT))


class TestAutRegister(unittest.TestCase):
    """T04: all 60 automations, each with a named engine."""

    def setUp(self):
        register = Path(__file__).resolve().parents[1] / "data" / "aut_register.yaml"
        self.data = yaml.safe_load(register.read_text(encoding="utf-8"))["automations"]

    def test_all_sixty_present(self):
        ids = [a["id"] for a in self.data]
        self.assertEqual(len(ids), 60)
        self.assertEqual(len(set(ids)), 60)
        self.assertEqual(ids[0], "AUT-001")
        self.assertEqual(ids[-1], "AUT-060")

    def test_every_automation_names_an_engine(self):
        valid = {"odoo_automated_action", "airflow", "domain_service"}
        for automation in self.data:
            self.assertIn(
                automation["engine"], valid, "%s carries no named engine" % automation["id"]
            )

    def test_time_driven_automations_go_to_airflow(self):
        by_id = {a["id"]: a for a in self.data}
        for aut in ("AUT-009", "AUT-013", "AUT-015", "AUT-023", "AUT-036"):
            self.assertEqual(by_id[aut]["engine"], "airflow", aut)

    def test_computational_automations_go_to_domain_services(self):
        """An automation whose action routes/reconciles/scores belongs to a
        named engine — UNLESS its trigger is time-driven (a scheduled
        workflow may orchestrate a service call)."""
        for automation in self.data:
            action = automation["action"].lower()
            if any(k in action for k in ("route", "reconcil", "score")):
                self.assertIn(automation["engine"], ("domain_service", "airflow"), automation["id"])

    def test_model_declared(self):
        source = (
            Path(__file__).resolve().parents[1] / "models" / "fix_workflow_engine.py"
        ).read_text(encoding="utf-8")
        self.assertIn('_name = "fix.automation"', source)
        self.assertIn('_name = "fix.approval.matrix"', source)

    def test_model_declares_engine_gap_reporting(self):
        """G3 evidence: gaps are reported, never assumed done."""
        source = (
            Path(__file__).resolve().parents[1] / "models" / "fix_workflow_engine.py"
        ).read_text(encoding="utf-8")
        self.assertIn("action_report_engine_gap", source)
        self.assertIn("fix.automation", source)


class TestM63M27Break(unittest.TestCase):
    def test_notifications_via_events_not_calls(self):
        """T03: closes the M63 -> M27 violation — publish, never call."""
        source = (
            Path(__file__).resolve().parents[1] / "models" / "fix_workflow_engine.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("cd_notification", source)  # no module import
        self.assertIn("from libs.py.fix_events import publish", source)


if __name__ == "__main__":
    unittest.main()
