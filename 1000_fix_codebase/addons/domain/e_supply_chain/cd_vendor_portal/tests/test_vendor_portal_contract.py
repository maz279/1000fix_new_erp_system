# cd_vendor_portal — P05 vendor portal contract (source-level, 2026-11-24).
#
# The portal reuses the W4 /vendor/* routes and adds three read routes for
# the dashboard/profile. These checks pin the fields and the scoping rules.
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
PORTAL = (MODULE / "controllers" / "portal_api.py").read_text(encoding="utf-8")
BASE = (MODULE / "controllers" / "vendor_api.py").read_text(encoding="utf-8")


class TestPortalSurface(unittest.TestCase):
    def test_portal_routes_are_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/vendor/portal/[^"]+)"[^)]*type="jsonrpc",\s*auth="user"',
            PORTAL,
        )
        self.assertEqual(len(routes), 3, routes)
        self.assertEqual(len(set(routes)), 3, routes)

    def test_base_contract_routes_unchanged(self):
        routes = re.findall(
            r'@http\.route\("(/vendor/[^"]+)"[^)]*type="jsonrpc",\s*auth="user"', BASE
        )
        self.assertEqual(len(routes), 2, routes)
        self.assertNotIn("/vendor/portal/", BASE)


class TestVendorScoping(unittest.TestCase):
    def test_profile_is_fenced_to_the_session_commercial_partner(self):
        self.assertIn("_vendor_partner()", PORTAL)
        self.assertIn('("partner_id", "=", partner.id)', PORTAL)
        self.assertIn('("partner_id", "child_of", partner.id)', PORTAL)

    def test_staff_have_no_vendor_profile(self):
        self.assertIn("_is_staff()", PORTAL)
        self.assertIn("no_supplier_profile", PORTAL)

    def test_reads_are_sudo_after_scoping(self):
        self.assertIn('request.env(su=True)["fix.supplier"]', PORTAL)


class TestProfileContract(unittest.TestCase):
    def test_standing_and_contact_fields(self):
        for key in (
            "supplier_code",
            "status",
            "segment",
            "category",
            "payment_block",
            "classification",
            "risk_tier",
            "latest_score",
            "contacts",
            "masked",
        ):
            self.assertIn(key, PORTAL)

    def test_bank_number_is_masked(self):
        self.assertIn("def _mask_account", PORTAL)
        self.assertIn("number[-4:]", PORTAL)


class TestDocumentsContract(unittest.TestCase):
    def test_expiry_is_computed_from_the_valid_to_date(self):
        self.assertIn("days_to_expiry", PORTAL)
        self.assertIn("doc.valid_to - today", PORTAL)
        self.assertIn("is_valid", PORTAL)


class TestSummaryContract(unittest.TestCase):
    def test_summary_exposes_po_invoice_and_compliance_buckets(self):
        for key in (
            "awaiting_ack",
            "oldest_open_days",
            "open_value_bdt",
            "by_state",
            "by_match",
            "by_approval",
            "by_payment",
            "blocked",
            "expiring_30_days",
            "expired",
            "score",
        ):
            self.assertIn(key, PORTAL)

    def test_receipts_remain_warehouse_only(self):
        # the portal must never let a vendor self-certify delivery
        self.assertIn("Deliveries are recorded by the receiving warehouse", BASE)


class TestInvoiceEnrichment(unittest.TestCase):
    def test_invoice_list_carries_approval_payment_and_due(self):
        for key in ('"approval_state"', '"payment_state"', '"due_date"'):
            self.assertIn(key, BASE)

    def test_po_list_carries_confirmed_delivery(self):
        self.assertIn('"vendor_confirmed_date"', BASE)
        self.assertIn('"received_on"', BASE)


class TestNoHostLiterals(unittest.TestCase):
    def test_no_urls_in_source(self):
        for token in ("http://", "https://", "wss://"):
            self.assertNotIn(token, PORTAL)


if __name__ == "__main__":
    unittest.main()
