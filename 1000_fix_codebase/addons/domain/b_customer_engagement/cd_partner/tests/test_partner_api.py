# cd_partner tests — P12 Partner & Referral API (source-level).
from pathlib import Path
import re
import unittest

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "partner_api.py").read_text(encoding="utf-8")


class TestPartnerScoping(unittest.TestCase):
    def test_profile_lookup_scopes_to_partner(self):
        self.assertIn("request.env.user.partner_id", API)

    def test_referrals_search_filters_profile(self):
        searches = re.findall(r'\.search\(\s*\[(.*?)\]', API, re.S)
        self.assertGreaterEqual(len(searches), 2)
        for s in searches:
            self.assertIn("partner_id", s,
                          "unscoped partner search: [%s]" % s[:60])

    def test_missing_profile_is_structured(self):
        self.assertIn("no_partner_profile", API)


class TestReferralFlow(unittest.TestCase):
    def test_submission_requires_referred_party(self):
        self.assertIn("missing_referred", API)

    def test_submission_via_model_create(self):
        self.assertIn('"fix.referral"', API)

    def test_commission_statement_from_referral_ledger(self):
        self.assertIn("commissions", API)
        self.assertIn("earned_total_bdt", API)

    def test_money_backend_formatted(self):
        self.assertIn("_fmt_bdt", API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_partner_operations(self):
        import json
        spec = json.loads((REPO / "contracts" / "openapi"
                           / "w4-portals.json").read_text(encoding="utf-8"))
        for path in ("/partner/profile", "/partner/referrals",
                     "/partner/commissions"):
            self.assertIn(path, spec["paths"])

    def test_routes_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/partner/[^"]+)"[^)]*type="json",\s*auth="user"',
            API)
        self.assertEqual(len(routes), 3, routes)


if __name__ == "__main__":
    unittest.main()
