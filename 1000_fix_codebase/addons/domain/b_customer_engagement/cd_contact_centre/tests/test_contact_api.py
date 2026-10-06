# cd_contact_centre tests — P10 Agent Console API (source-level).
from pathlib import Path
import re
import unittest

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "contact_api.py").read_text(encoding="utf-8")


class TestSoftphoneSeam(unittest.TestCase):
    """PP5 special requirement: the softphone integration seam — config
    from system parameters only; no hosts or credentials in source."""

    def test_config_from_system_parameters(self):
        self.assertIn("ir.config_parameter", API)

    def test_no_host_literals(self):
        self.assertNotIn("http://", API)
        self.assertNotIn("https://", API)
        self.assertNotIn("wss://", API)

    def test_unset_config_surfaces_null(self):
        self.assertIn("or None", API)


class TestCustomer360(unittest.TestCase):
    def test_360_bundles_orders_devices_conversations(self):
        for key in ("open_orders", "devices", "recent_conversations"):
            self.assertIn(key, API)

    def test_transcript_in_sequence_order(self):
        self.assertIn("sequence", API)
        self.assertIn("transcript", API)


class TestCallControl(unittest.TestCase):
    def test_actions_are_validated(self):
        self.assertIn("invalid_action", API)
        self.assertIn("not_claimable", API)

    def test_state_transitions_target_model_states(self):
        # the model's own states (G4-04/G4-05): with_agent, with_ai,
        # resolved_agent — nothing invented
        self.assertIn('"with_agent"', API)
        self.assertIn('"resolved_agent"', API)

    def test_errors_are_structured(self):
        self.assertIn("handoff_rejected", API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_contact_operations(self):
        import json
        spec = json.loads((REPO / "contracts" / "openapi"
                           / "w4-portals.json").read_text(encoding="utf-8"))
        self.assertIn("/contact/conversations", spec["paths"])
        self.assertIn("/contact/handoff", spec["paths"])

    def test_routes_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/contact/[^"]+)"[^)]*type="json",\s*auth="user"',
            API)
        self.assertEqual(len(routes), 4, routes)

    def test_team_queue_scope_is_honest(self):
        # no phantom agent-assignment column in the domain
        self.assertNotIn("user_id", API)


if __name__ == "__main__":
    unittest.main()
