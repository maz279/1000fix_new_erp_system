# cd_contact_centre — P10 agent-console portal API (source-level).
#
# The portal controller is deliberately separate from the W4 contact_api.py
# contract, so the base contract's route count and bearer-free shape stay
# untouched. These checks pin the staff boundary and the wrap-up delegation.
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
PORTAL = (MODULE / "controllers" / "portal_api.py").read_text(encoding="utf-8")
BASE = (MODULE / "controllers" / "contact_api.py").read_text(encoding="utf-8")


class TestPortalSurface(unittest.TestCase):
    def test_every_portal_route_is_session_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/contact/portal/[^"]+)"[^)]*type="jsonrpc",\s*auth="user"',
            PORTAL,
        )
        self.assertEqual(len(routes), 6, routes)
        self.assertEqual(len(set(routes)), 6, routes)

    def test_base_contract_keeps_its_six_routes(self):
        routes = re.findall(
            r'@http\.route\("(/contact/[^"]+)"[^)]*type="jsonrpc",\s*auth="user"', BASE
        )
        self.assertEqual(len(routes), 6, routes)
        self.assertNotIn("/contact/portal/", BASE)


class TestStaffBoundary(unittest.TestCase):
    def test_staff_guard_checks_internal_user(self):
        self.assertIn("def _staff_only()", PORTAL)
        self.assertIn("_is_internal()", PORTAL)
        self.assertIn('_error("staff_only"', PORTAL)

    def test_every_route_forwards_the_staff_guard(self):
        self.assertEqual(PORTAL.count("denied = _staff_only()"), 6)


class TestWritePaths(unittest.TestCase):
    def test_wrapup_delegates_to_the_model_gate(self):
        # the model owns disposition + notes + FCR + recording-digest rules
        self.assertIn("action_wrap_up(", PORTAL)
        self.assertNotIn('"state": "resolved_agent"', PORTAL)
        self.assertIn("wrapup_notes", PORTAL)
        self.assertIn("len(notes) < 20", PORTAL)

    def test_reply_records_an_agent_turn(self):
        self.assertIn('speaker="agent"', PORTAL)
        self.assertIn("intake_message(", PORTAL)

    def test_reply_refuses_unclaimed_or_foreign_conversations(self):
        self.assertIn('conv.state != "with_agent"', PORTAL)
        self.assertIn("not_your_conversation", PORTAL)
        self.assertIn("_is_supervisor()", PORTAL)

    def test_queue_exposes_sla_and_routing_context(self):
        for key in ("sla_breached", "waiting_minutes", "priority", "entitlement"):
            self.assertIn(key, PORTAL)

    def test_dispositions_are_active_only(self):
        self.assertIn('"fix.cc.disposition"', PORTAL)
        self.assertIn('[("active", "=", True)]', PORTAL)


class TestNoHostLiterals(unittest.TestCase):
    def test_no_urls_or_credentials_in_source(self):
        for token in ("http://", "https://", "wss://"):
            self.assertNotIn(token, PORTAL)
        self.assertNotIn("password", PORTAL.lower())


if __name__ == "__main__":
    unittest.main()
