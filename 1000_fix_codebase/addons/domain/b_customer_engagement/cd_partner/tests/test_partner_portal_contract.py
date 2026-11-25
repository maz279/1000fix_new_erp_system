# cd_partner — P12 partner portal contract (source-level, 2026-11-24).
#
# The portal reuses the W4 /partner/* routes. These checks pin the fields the
# external portal relies on and the scoping/consent rules it must not weaken.
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
API = (MODULE / "controllers" / "partner_api.py").read_text(encoding="utf-8")


class TestPortalProfile(unittest.TestCase):
    def test_profile_exposes_standing_and_contact(self):
        for key in ("kyc_verified", "email", "phone", "commission_rate", "territory"):
            self.assertIn(key, API)

    def test_partner_binding_is_session_first(self):
        self.assertIn("request.env.user.partner_id", API)
        self.assertIn('search([("partner_id", "=", partner.id)]', API)

    def test_staff_override_is_the_only_profile_id_path(self):
        self.assertIn('user.has_group("base.group_user")', API)
        self.assertIn("profile.sudo().partner_id != user.partner_id", API)


class TestLeadContract(unittest.TestCase):
    def test_lead_rows_carry_state_reason_and_protection(self):
        for key in (
            "service_interest",
            "attribution_expires_on",
            "converted_at",
            "loss_reason",
            "referral",
            "commission_bdt",
        ):
            self.assertIn(key, API)

    def test_submission_requires_consent_and_refuses_party_ids(self):
        self.assertIn('"missing_consent"', API)
        self.assertIn('"referred_party_not_accepted"', API)
        self.assertIn('"missing_phone"', API)

    def test_lead_is_created_with_consent(self):
        self.assertIn('"consent_given": True', API)
        self.assertIn('"consent_method": method', API)


class TestCommissionContract(unittest.TestCase):
    def test_statement_uses_the_customer_name_the_partner_typed(self):
        self.assertIn("typed.get(r.id)", API)
        self.assertIn("lead.customer_name", API)

    def test_customer_master_read_is_guarded(self):
        # a portal partner must not inherit access to the party master
        self.assertIn("except AccessError", API)
        self.assertIn("r.referred_partner_id.name", API)

    def test_statement_line_fields(self):
        for key in ("referred_on", "base_amount_bdt", "commission_rate", "commission_bdt", "state"):
            self.assertIn(key, API)


class TestApiSurface(unittest.TestCase):
    def test_routes_are_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/partner/[^"]+)"[^)]*type="jsonrpc",\s*auth="user"', API
        )
        self.assertEqual(len(routes), 3, routes)

    def test_no_host_literals(self):
        for token in ("http://", "https://", "wss://"):
            self.assertNotIn(token, API)


if __name__ == "__main__":
    unittest.main()
