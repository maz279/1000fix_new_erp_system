# cd_workflow_engine tests — 60 Business Automations & verified engine bindings (P06-M08-T04, G3-e)
#
# 19.0.1.2.0 (A11 fix B1, A4-F01): the register used to claim three engines
# none of whose references resolved. These assertions pin the HONEST
# catalogue: the mechanism really executing each row, and the verdict on how
# much of the described behaviour it performs.
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]

ENGINES = {"odoo_cron", "odoo_method", "event_consumer", "manual"}
PREFIXES = {
    "odoo_cron": "cron:",
    "odoo_method": "method:",
    "event_consumer": "consumer:",
}


class TestAutEnginesCoverage(unittest.TestCase):
    """T06 (honest): all 60 automations mapped to the mechanism that executes them."""

    def setUp(self):
        register_file = Path(__file__).resolve().parents[1] / "data" / "aut_register.yaml"
        self.data = yaml.safe_load(register_file.read_text(encoding="utf-8"))["automations"]

    def test_sixty_automations_count(self):
        self.assertEqual(len(self.data), 60)
        codes = [a["id"] for a in self.data]
        self.assertEqual(len(set(codes)), 60)
        self.assertEqual(codes[0], "AUT-001")
        self.assertEqual(codes[-1], "AUT-060")

    def test_no_retired_engine_value_survives(self):
        """odoo_automated_action / airflow / domain_service resolved to nothing
        (0 of 60); a regression would reinstate the fiction."""
        engines = {a["engine"] for a in self.data}
        self.assertLessEqual(engines, ENGINES)
        self.assertEqual(engines, ENGINES)
        for retired in ("odoo_automated_action", "airflow", "domain_service"):
            self.assertNotIn(retired, engines)

    def test_every_reference_matches_its_engine(self):
        for a in self.data:
            ref = a.get("engine_ref") or ""
            engine = a["engine"]
            if engine == "manual":
                self.assertEqual(ref, "", "%s: manual rows carry no reference" % a["id"])
                continue
            prefix = PREFIXES[engine]
            self.assertTrue(
                ref.startswith(prefix),
                "%s: %s reference must start with %r, got %r" % (a["id"], engine, prefix, ref),
            )
            self.assertNotIn("<", ref)
            self.assertNotIn(">", ref)
            # a concrete target after the prefix
            self.assertGreater(len(ref), len(prefix), a["id"])

    def test_implementation_verdicts_are_complete_and_consistent(self):
        counts = {"full": 0, "partial": 0, "none": 0}
        for a in self.data:
            self.assertIn(a["implementation"], counts, a["id"])
            counts[a["implementation"]] += 1
            # engine 'manual' means nothing executes the row: it cannot claim
            # an implementation, and anything implemented must not be manual
            if a["implementation"] == "none":
                self.assertEqual(a["engine"], "manual", a["id"])
            else:
                self.assertNotEqual(a["engine"], "manual", a["id"])
            self.assertTrue(a.get("executor_note"), "%s has no executor note" % a["id"])
        # the honest verdict on the estate at issue (A4 §3: 25 FULL / 27
        # PARTIAL / 8 NONE claimed; re-verified against the code: 20/32/8)
        self.assertEqual(counts, {"full": 20, "partial": 32, "none": 8})

    def test_trigger_and_action_completeness(self):
        """All automations must have rich non-empty trigger and action definitions."""
        for a in self.data:
            self.assertTrue(bool(a.get("trigger")), f"{a['id']} missing trigger")
            self.assertTrue(bool(a.get("action")), f"{a['id']} missing action")
            self.assertGreaterEqual(len(a["trigger"]), 5)
            self.assertGreaterEqual(len(a["action"]), 10)


if __name__ == "__main__":
    unittest.main()
