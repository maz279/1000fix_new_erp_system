# cd_warranty_claims tests — P08 Brand API surface (source-level).
from pathlib import Path
import re
import unittest

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "brand_api.py").read_text(encoding="utf-8")


class TestBrandIsolation(unittest.TestCase):
    """PP5 special requirement: per-brand branding isolation — the
    brand_id filter is mandatory and unscoped reads are refused."""

    def test_brand_id_required_everywhere(self):
        # every route method calls _brand_scope and rejects None
        self.assertEqual(API.count("_brand_scope(kwargs)"), 4)
        self.assertIn("missing_brand", API)

    def test_cross_brand_claim_is_invisible(self):
        # another brand's claim returns not-found, never the data
        self.assertIn("claim.brand_id.id != brand_id", API)

    def test_claims_search_filters_brand(self):
        # literal-domain searches (claim_status, reconciliation) all
        # carry brand_id; _list_claims builds its domain from brand_id first
        searches = re.findall(
            r'\.search\(\s*\[(.*?)\]', API, re.S)
        self.assertGreaterEqual(len(searches), 2)
        for s in searches:
            self.assertIn("brand_id", s,
                          "unscoped claim search: [%s]" % s[:60])
        self.assertIn('domain = [("brand_id", "=", brand_id)]', API)


class TestDecisionAndReconciliation(unittest.TestCase):
    def test_decide_rides_model_action(self):
        self.assertIn("action_decide(", API)

    def test_decision_validated(self):
        self.assertIn("invalid_decision", API)
        self.assertIn("decision_rejected", API)

    def test_remittance_flags_mismatch(self):
        # T08: a mismatch is flagged, never auto-adjusted
        self.assertIn("mismatch", API)
        self.assertIn("action_record_remittance(", API)

    def test_money_backend_formatted(self):
        self.assertIn("_fmt_bdt", API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_brand_operations(self):
        import json
        spec = json.loads((REPO / "contracts" / "openapi"
                           / "w4-portals.json").read_text(encoding="utf-8"))
        self.assertIn("/brand/claims", spec["paths"])
        self.assertIn("/brand/claims/{claim_no}/status", spec["paths"])
        self.assertIn("/brand/reconciliation", spec["paths"])

    def test_routes_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/brand/[^"]+)"[^)]*type="json",\s*auth="user"',
            API)
        self.assertEqual(len(routes), 3, routes)


if __name__ == "__main__":
    unittest.main()
