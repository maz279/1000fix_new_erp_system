# cd_warranty_claims tests — P08 Brand API surface (source-level).
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "brand_api.py").read_text(encoding="utf-8")


class TestBrandIsolation(unittest.TestCase):
    """PP5 special requirement: per-brand isolation - the brand is resolved from
    the authenticated user and every claim search carries it (behaviour:
    test_brand_api_behaviour.py)."""

    def test_brand_resolved_from_the_authenticated_user_everywhere(self):
        # one definition + the four endpoints
        self.assertEqual(API.count("resolve_brand(kwargs)"), 5)
        self.assertIn("def resolve_brand(kwargs)", API)
        self.assertIn('("api_user_ids", "in", user.id)', API)

    def test_claims_search_filters_brand(self):
        # every claim search domain carries the resolved brand
        searches = re.findall(r'\["fix\.warranty\.claim"\]\.search\(\s*\[(.*?)\]', API, re.S)
        self.assertGreaterEqual(len(searches), 4)
        for s in searches:
            self.assertIn("brand", s, "unscoped search: [%s]" % s[:60])
        self.assertIn('domain = [("brand_id", "=", brand.id)]', API)


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
        self.assertIn("variance_bdt", API)

    def test_webhook_endpoint_implemented(self):
        # T05: inbound status webhook acknowledging claim events
        self.assertIn('@http.route("/brand/claims/webhook"', API)
        self.assertIn("event_type", API)
        self.assertIn("claim.action_decide", API)

    def test_money_backend_formatted(self):
        self.assertIn("_fmt_bdt", API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_brand_operations(self):
        import json

        spec = json.loads(
            (REPO / "contracts" / "openapi" / "w4-portals.json").read_text(encoding="utf-8")
        )
        self.assertIn("/brand/claims", spec["paths"])
        self.assertIn("/brand/claims/{claim_no}/status", spec["paths"])
        self.assertIn("/brand/claims/webhook", spec["paths"])
        self.assertIn("/brand/reconciliation", spec["paths"])

    def test_routes_jsonrpc_auth_bearer(self):
        routes = re.findall(
            r'@http\.route\("(/brand/[^"]+)"[^)]*type="jsonrpc",\s*auth="bearer"', API
        )
        self.assertEqual(len(routes), 4, routes)


if __name__ == "__main__":
    unittest.main()
