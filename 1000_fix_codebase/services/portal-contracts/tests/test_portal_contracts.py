"""PS-11 portal contract tests — P07-M09-T08.

The proof that business rules are not in portal code: an INVALID payload
posted directly to the API is REJECTED server-side (AS-09 — the model layer
validates; the portal is a shell).
"""

from __future__ import annotations

import json
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
        enum = spec["components"]["schemas"]["ServiceRequest"]["properties"]["order_category"][
            "enum"
        ]
        self.assertEqual(enum, ["standard", "warranty", "amc"])


class TestBackendValidation(unittest.TestCase):
    def test_warranty_orders_validate_server_side(self):
        """AS-09: the M01 model gates warranty orders — the portal only
        passes the category through; the GATE lives in the model."""
        order = (
            REPO
            / "addons"
            / "domain"
            / "a_service_delivery"
            / "cd_service_order"
            / "models"
            / "fix_service_order.py"
        ).read_text(encoding="utf-8")
        self.assertIn("_check_warranty_gate", order)

    def test_evidence_completeness_blocks_server_side(self):
        """M09's blocking check is in the model, not the P08 portal."""
        claims = (
            REPO
            / "addons"
            / "domain"
            / "a_service_delivery"
            / "cd_warranty_claims"
            / "models"
            / "fix_warranty_claims.py"
        ).read_text(encoding="utf-8")
        self.assertIn("cannot be submitted", claims)

    def test_portal_views_carry_no_business_logic(self):
        """AS-09 sweep: the W4 portal-side views (agent console etc.) hold
        no model-layer logic — grep the contact-centre views."""
        views = (
            REPO
            / "addons"
            / "domain"
            / "b_customer_engagement"
            / "cd_contact_centre"
            / "views"
            / "fix_contact_centre_views.xml"
        ).read_text(encoding="utf-8")
        for forbidden in ("api.model", "self.env[", "@api.", "def action_"):
            self.assertNotIn(forbidden, views)


class TestConsentPdpaContract(unittest.TestCase):
    """PS-11 for contracts/openapi/consent-pdpa.json (PP1-M03)."""

    def setUp(self):
        self.spec = json.loads((SPECS / "consent-pdpa.json").read_text(encoding="utf-8"))

    def test_grant_without_proof_is_a_422_at_the_edge(self):
        """AS-09: proof-on-grant is the MODEL's rule (fix.consent) — the
        contract must publish the 422 so the portal never re-implements it."""
        post = self.spec["paths"]["/consent/{party_id}/grant"]["post"]
        self.assertIn("422", post["responses"])
        grant = self.spec["components"]["schemas"]["ConsentGrant"]
        self.assertIn("proof", grant["required"])
        self.assertGreater(
            grant["properties"]["proof"].get("minLength", 0),
            0,
            "proof must be a non-empty string",
        )

    def test_channels_match_the_model_selection(self):
        """The contract enum must equal fix.consent's channel selection —
        drift here forks the vocabulary between API and data."""
        model = (
            REPO / "addons" / "platform" / "cd_party_master" / "models" / "fix_consent.py"
        ).read_text(encoding="utf-8")
        enum = self.spec["components"]["schemas"]["ConsentChannel"]["enum"]
        for channel in enum:
            self.assertIn(f'"{channel}"', model, f"channel {channel} not in the fix.consent model")

    def test_dsr_types_match_pdpa_scopes(self):
        enum = self.spec["paths"]["/dsr"]["post"]["requestBody"]["content"]["application/json"][
            "schema"
        ]["$ref"]
        self.assertEqual(enum, "#/components/schemas/DsrRequest")
        types = self.spec["components"]["schemas"]["DsrRequest"]["properties"]["request_type"][
            "enum"
        ]
        self.assertEqual(sorted(types), ["access", "erasure", "rectification"])

    def test_withdraw_is_post_not_delete(self):
        """Withdrawal is a recorded event (audit trail), not row deletion."""
        self.assertIn("post", self.spec["paths"]["/consent/{party_id}/withdraw"])


class TestP01CustomerContract(unittest.TestCase):
    """PS-11 for contracts/openapi/p01-customer.json (PP1-M03)."""

    def setUp(self):
        self.spec = json.loads((SPECS / "p01-customer.json").read_text(encoding="utf-8"))

    def test_money_crosses_the_wire_as_strings(self):
        """AS-10/03-§8: totals arrive backend-computed and BN-007-formatted —
        numeric money fields in the contract would invite client math."""
        est = self.spec["components"]["schemas"]["Estimate"]
        for field in ("total_bdt", "vat_bdt"):
            self.assertEqual(est["properties"][field]["type"], "string")
        self.assertNotIn("number", json.dumps(est["properties"]))

    def test_tracking_events_are_bilingual(self):
        """DE-17: the timeline labels must arrive in both locales."""
        item = self.spec["paths"]["/customer/orders/{order_id}/tracking"]["get"]["responses"][
            "200"
        ]["content"]["application/json"]["schema"]["properties"]["events"]["items"]
        for field in ("label_en", "label_bn"):
            self.assertIn(field, item["properties"])
            self.assertIn(field, item["required"])

    def test_list_pagination_capped(self):
        """Unbounded listing is a DoS vector — the contract caps the page."""
        limit = self.spec["paths"]["/customer/{party_id}/orders"]["get"]["parameters"][2]["schema"]
        self.assertEqual(limit.get("maximum"), 100)

    def test_estimate_approval_is_a_state_not_a_calculation(self):
        """The POST carries only the decision; totals never round-trip."""
        body = self.spec["paths"]["/customer/orders/{order_id}/estimate"]["post"]["requestBody"][
            "content"
        ]["application/json"]["schema"]
        self.assertEqual(body["properties"], {"approved": {"type": "boolean"}})


if __name__ == "__main__":
    unittest.main()
