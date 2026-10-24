# cd_vendor_portal tests — P05 PP5 API surface (source-level battery).
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "vendor_api.py").read_text(encoding="utf-8")
MANIFEST = (MODULE / "__manifest__.py").read_text(encoding="utf-8")


class TestThreeWayMatchSurface(unittest.TestCase):
    """G3-06: a blocked invoice is visible with its reason, never warned."""

    def test_match_detail_ships_with_state(self):
        self.assertIn("match_state", API)
        self.assertIn("match_detail", API)

    def test_match_engine_not_reimplemented(self):
        # the portal never judges: no match logic here, only the compute's output
        self.assertNotIn("received <", API)
        self.assertNotIn("price above PO", API)

    def test_submission_requires_po(self):
        self.assertIn("missing_po", API)
        self.assertIn("requisition_id", API)

    def test_money_backend_formatted(self):
        self.assertIn("_fmt_bdt", API)


class TestActionDelegation(unittest.TestCase):
    """Writes ride the owning model's action methods (AS-09)."""

    def test_acknowledge_rides_model_action(self):
        self.assertIn("action_acknowledge()", API)

    def test_delivery_rides_record_receipt(self):
        self.assertIn("action_record_receipt(", API)

    def test_errors_are_structured(self):
        for code in ("po_rejected", "invoice_rejected", "invalid_action"):
            self.assertIn(code, API)


class TestLivefireRegressions(unittest.TestCase):
    """Bugs found by the PP5 live-fire (tooling/scripts/livefire-pp5.py);
    locked here so they cannot return."""

    def test_invoice_create_sets_operating_unit(self):
        # fix.vendor.invoice.operating_unit_id is required with no default —
        # without this the portal could never submit an invoice. The PO's
        # own (required) unit is used; the live behaviour is asserted in
        # test_vendor_api_live.py.
        self.assertIn('"operating_unit_id": po.operating_unit_id.id', API)

    def test_invoice_date_none_never_overrides_default(self):
        # an explicit None in create() overrides the model default (today)
        self.assertNotIn('"invoice_date": kwargs.get("invoice_date") or None', API)
        self.assertIn('vals["invoice_date"] = kwargs["invoice_date"]', API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_vendor_operations(self):
        import json

        spec = json.loads(
            (REPO / "contracts" / "openapi" / "w4-portals.json").read_text(encoding="utf-8")
        )
        for path in ("/vendor/purchase-orders", "/vendor/invoices"):
            self.assertIn(path, spec["paths"])

    def test_routes_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("(/vendor/[^"]+)"[^)]*type="jsonrpc",\s*auth="user"', API
        )
        self.assertEqual(len(routes), 2, routes)

    def test_module_depends_on_requisition_and_ap(self):
        self.assertIn("cd_requisition", MANIFEST)
        self.assertIn("cd_ap_ext", MANIFEST)


if __name__ == "__main__":
    unittest.main()
