# cd_settlement_ext tests — the seller settlement statement surface (PP5).
import unittest
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "settlement_api.py").read_text(encoding="utf-8")


class TestSettlementStatement(unittest.TestCase):
    def test_statement_scopes_to_seller_party(self):
        self.assertIn("seller_partner_id", API)

    def test_session_party_default(self):
        self.assertIn("request.env.user.partner_id", API)

    def test_lines_carry_the_payout_state(self):
        self.assertIn('"state"', API)

    def test_net_total_backend_computed(self):
        self.assertIn("net_total_bdt", API)
        self.assertIn("_fmt_bdt", API)

    def test_route_json_auth_readonly(self):
        import re

        routes = re.findall(
            r'@http\.route\("(/seller/settlements)"[^)]*type="jsonrpc",\s*'
            r'auth="user",\s*readonly=True',
            API,
        )
        self.assertEqual(len(routes), 1, routes)


if __name__ == "__main__":
    unittest.main()
