# cd_workflow_engine tests — M63 (P06-M08-T03/T04).
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT))

ENGINES = {"odoo_cron", "odoo_method", "event_consumer", "manual"}


class TestAutRegister(unittest.TestCase):
    """T04: all 60 automations, each with the mechanism that executes it."""

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
        for automation in self.data:
            self.assertIn(
                automation["engine"], ENGINES, "%s carries no named engine" % automation["id"]
            )

    def test_time_driven_automations_are_scheduled_actions(self):
        """A time-driven automation is executed by an ir.cron (or handed to a
        person); nothing in this estate runs Airflow DAGs (A4-F01). AUT-036
        is a method: nothing schedules a count plan when a cycle falls due."""
        by_id = {a["id"]: a for a in self.data}
        for aut in ("AUT-009", "AUT-012", "AUT-015", "AUT-023"):
            self.assertEqual(by_id[aut]["engine"], "odoo_cron", aut)
        self.assertEqual(by_id["AUT-036"]["engine"], "odoo_method")
        self.assertEqual(by_id["AUT-036"]["implementation"], "partial")

    def test_every_reference_is_a_concrete_target(self):
        """No placeholder text survives: a reference is an xmlid, a model
        method or an event type — all resolvable at runtime."""
        for automation in self.data:
            ref = automation["engine_ref"]
            self.assertNotIn("created at activation", ref, automation["id"])
            self.assertNotIn("<", ref, automation["id"])
            if automation["engine"] != "manual":
                self.assertTrue(
                    ref.split(":", 1)[0] in ("cron", "method", "consumer", automation["engine"]),
                    automation["id"],
                )
                self.assertGreater(len(ref.split(":", 1)[-1]), 3, automation["id"])

    def test_model_declared(self):
        source = (
            Path(__file__).resolve().parents[1] / "models" / "fix_workflow_engine.py"
        ).read_text(encoding="utf-8")
        self.assertIn('_name = "fix.automation"', source)
        self.assertIn('_name = "fix.approval.matrix"', source)

    def test_model_declares_a_runtime_resolver_and_gap_reporting(self):
        """G3 evidence: references are RESOLVED at runtime, never string-matched."""
        source = (
            Path(__file__).resolve().parents[1] / "models" / "fix_workflow_engine.py"
        ).read_text(encoding="utf-8")
        self.assertIn("action_report_engine_gap", source)
        self.assertIn("_binding_resolver", source)
        self.assertIn('"fix.event.consumer"', source)  # the consumer register it reads
        # the retired values stay out of the engine SELECTION (they survive
        # only in RETIRED_ENGINES, which the migration reads)
        start = source.index("ENGINES = [")
        selection = source[start : source.index("]", start)]
        for retired in ("odoo_automated_action", "airflow", "domain_service"):
            self.assertNotIn(retired, selection)
        for engine in ("odoo_cron", "odoo_method", "event_consumer", "manual"):
            self.assertIn('("%s",' % engine, selection)


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
