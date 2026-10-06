# cd_marketplace tests — P07 Seller API surface (source-level).
from pathlib import Path
import re
import unittest

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "seller_api.py").read_text(encoding="utf-8")


class TestSellerScoping(unittest.TestCase):
    def test_seller_lookup_scopes_to_partner(self):
        self.assertIn("request.env.user.partner_id", API)

    def test_only_own_quotes_visible(self):
        self.assertIn("seller_id.id == seller.id", API)

    def test_missing_seller_is_structured(self):
        self.assertIn("no_seller", API)


class TestKycGate(unittest.TestCase):
    """M12: only a KYC-verified seller quotes — stated, not warned."""

    def test_kyc_gate_before_quote(self):
        self.assertIn("kyc_not_verified", API)
        self.assertIn("kyc_status", API)


class TestActionDelegation(unittest.TestCase):
    def test_quote_create_via_model(self):
        self.assertIn('"fix.seller.quote"', API)

    def test_price_validation_server_side(self):
        self.assertIn("invalid_price", API)
        self.assertIn("order_not_open", API)

    def test_money_backend_formatted(self):
        self.assertIn("_fmt_bdt", API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_seller_operations(self):
        import json
        spec = json.loads((REPO / "contracts" / "openapi"
                           / "w4-portals.json").read_text(encoding="utf-8"))
        for path in ("/seller/dashboard", "/seller/orders", "/seller/quotes",
                     "/seller/scorecard"):
            self.assertIn(path, spec["paths"])

    def test_routes_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/seller/[^"]+)"[^)]*type="json",\s*auth="user"',
            API)
        self.assertEqual(len(routes), 4, routes)

    def test_settlements_not_duplicated_here(self):
        # FL-03: settlement statements live with the ledger (cd_settlement_ext)
        # — this module registers no route for them (the docstring pointer
        # is the only mention)
        routes = re.findall(r'@http\.route\("(/seller/[^"]+)"', API)
        self.assertNotIn("/seller/settlements", routes)


if __name__ == "__main__":
    unittest.main()
