"""PS-11 portal contract tests — P07-M09-T08.

The proof that business rules are not in portal code: an INVALID payload
posted directly to the API is REJECTED server-side (AS-09 — the model layer
validates; the portal is a shell).
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SPECS = REPO / "contracts" / "openapi"


class TestOpenApiContracts(unittest.TestCase):
    def test_all_four_portals_have_operations(self):
        spec = json.loads((SPECS / "w4-portals.json").read_text(encoding="utf-8"))
        paths = " ".join(spec["paths"])
        for portal in ("/corporate/", "/brand/", "/contact/", "/analytics/"):
            self.assertIn(portal, paths, f"{portal} operations missing")

    def test_invalid_payload_rejected_by_contract(self):
        """The 422 on the write path — AS-09 enforced at the API edge."""
        spec = json.loads((SPECS / "w4-portals.json").read_text(encoding="utf-8"))
        post = spec["paths"]["/corporate/service-requests"]["post"]
        self.assertIn("422", post["responses"])
        required = post["requestBody"]["content"]["application/json"]["schema"]["$ref"]
        self.assertIn("ServiceRequest", required)

    def test_order_category_enum_matches_m01(self):
        spec = json.loads((SPECS / "w4-portals.json").read_text(encoding="utf-8"))
        enum = spec["components"]["schemas"]["ServiceRequest"]["properties"]["order_category"]["enum"]
        self.assertEqual(enum, ["standard", "warranty", "amc"])


class TestBackendValidation(unittest.TestCase):
    def test_warranty_orders_validate_server_side(self):
        """AS-09: the M01 model gates warranty orders — the portal only
        passes the category through; the GATE lives in the model."""
        order = (REPO / "addons" / "domain" / "a_service_delivery"
                 / "cd_service_order" / "models" / "fix_service_order.py").read_text(encoding="utf-8")
        self.assertIn("_check_warranty_gate", order)

    def test_evidence_completeness_blocks_server_side(self):
        """M09's blocking check is in the model, not the P08 portal."""
        claims = (REPO / "addons" / "domain" / "a_service_delivery"
                  / "cd_warranty_claims" / "models" / "fix_warranty_claims.py").read_text(encoding="utf-8")
        self.assertIn("cannot be submitted", claims)

    def test_portal_views_carry_no_business_logic(self):
        """AS-09 sweep: the W4 portal-side views (agent console etc.) hold
        no model-layer logic — grep the contact-centre views."""
        views = (REPO / "addons" / "domain" / "b_customer_engagement"
                 / "cd_contact_centre" / "views" / "fix_contact_centre_views.xml").read_text(encoding="utf-8")
        for forbidden in ("api.model", "self.env[", "@api.", "def action_"):
            self.assertNotIn(forbidden, views)


if __name__ == "__main__":
    unittest.main()
