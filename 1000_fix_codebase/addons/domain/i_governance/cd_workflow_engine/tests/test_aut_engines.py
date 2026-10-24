# cd_workflow_engine tests — 60 Business Automations & Zero Engine Gaps (P06-M08-T04, R04-M05-T06, G3-e)
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]


class TestAutEnginesCoverage(unittest.TestCase):
    """T06: All 60 business automations mapped to concrete named engines with zero gaps."""

    def setUp(self):
        register_file = Path(__file__).resolve().parents[1] / "data" / "aut_register.yaml"
        self.data = yaml.safe_load(register_file.read_text(encoding="utf-8"))["automations"]

    def test_sixty_automations_count(self):
        self.assertEqual(len(self.data), 60)
        codes = [a["id"] for a in self.data]
        self.assertEqual(len(set(codes)), 60)
        self.assertEqual(codes[0], "AUT-001")
        self.assertEqual(codes[-1], "AUT-060")

    def test_zero_engine_gaps_in_register(self):
        """Every single automation must carry a concrete engine_ref."""
        placeholders = [
            "ir.actions.server (created at activation)",
            "dag: fix_< AUT id lowercase > (Airflow sync)",
            "route: services/* engine named in the action",
        ]
        gaps = []
        for a in self.data:
            ref = a.get("engine_ref")
            if not ref or ref in placeholders or "<" in str(ref) or ">" in str(ref):
                gaps.append((a["id"], ref))

        self.assertEqual(gaps, [], f"Found {len(gaps)} engine gaps: {gaps}")

    def test_engine_reference_prefixes_conformance(self):
        """Verify engine reference prefixes match engine classification."""
        for a in self.data:
            engine = a["engine"]
            ref = a["engine_ref"]
            if engine == "odoo_automated_action":
                self.assertTrue(
                    ref.startswith("ir.actions.server:") or ref.startswith("base.action_"),
                    f"{a['id']}: invalid odoo action ref: {ref}",
                )
            elif engine == "airflow":
                self.assertTrue(
                    ref.startswith("dag:"),
                    f"{a['id']}: invalid airflow dag ref: {ref}",
                )
            elif engine == "domain_service":
                self.assertTrue(
                    ref.startswith("service:"),
                    f"{a['id']}: invalid domain service ref: {ref}",
                )

    def test_trigger_and_action_completeness(self):
        """All automations must have rich non-empty trigger and action definitions."""
        for a in self.data:
            self.assertTrue(bool(a.get("trigger")), f"{a['id']} missing trigger")
            self.assertTrue(bool(a.get("action")), f"{a['id']} missing action")
            self.assertGreaterEqual(len(a["trigger"]), 5)
            self.assertGreaterEqual(len(a["action"]), 10)


if __name__ == "__main__":
    unittest.main()
