# cd_customer_portal tests — P01 PP5 API surface (source-level battery;
# the runtime contract is exercised by PS-11 against a live Odoo).
from pathlib import Path
import re
import unittest
import yaml

MODULE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
API = (MODULE / "controllers" / "customer_api.py").read_text(encoding="utf-8")
SECURITY = (MODULE / "security" / "fix_customer_portal_security.xml").read_text(
    encoding="utf-8")
ACL = (MODULE / "security" / "ir.model.access.csv").read_text(encoding="utf-8")


class TestEa05Scoping(unittest.TestCase):
    """The P01 API must scope every read/write to the session's partner."""

    def test_partner_scoping_helper(self):
        self.assertIn("request.env.user.partner_id.id", API)

    def test_every_top_level_search_filters_on_partner(self):
        # the four customer-facing domains each scope on the partner;
        # the device-history search is scoped through an already-owned
        # device_id (transitively partner-scoped)
        self.assertIn('("owner_id", "=", partner)', API)      # devices
        self.assertIn('("customer_id", "=", partner)', API)   # orders
        self.assertIn('("order_id", "in", orders.ids)', API)  # estimates
        self.assertIn('("partner_id", "=", partner)', API)    # consent
        self.assertIn('("device_id", "=", d.id)', API)        # history

    def test_record_rules_bind_customer_group(self):
        self.assertIn("rule_fix_device_customer_self", SECURITY)
        self.assertIn("user.partner_id.id", SECURITY)

    def test_portal_group_not_internal(self):
        self.assertIn("ref('base.group_portal')", SECURITY)
        self.assertNotIn("ref('base.group_user')", SECURITY)

    def test_consent_write_via_owning_model(self):
        # withdrawal rides action_withdraw (the auditable trail), not a raw write
        self.assertIn("action_withdraw()", API)

    def test_transfer_rides_model_action(self):
        self.assertIn("action_transfer_ownership(", API)


class TestAs09ServerSideValidation(unittest.TestCase):
    """AS-09: validation and money stay server-side."""

    def test_booking_rejections_are_structured(self):
        self.assertIn("booking_rejected", API)
        self.assertIn("missing_device", API)
        self.assertIn("not_owner", API)

    def test_estimate_gates_surfaced_not_warned(self):
        # BRU-SRM-07 proof requirement + the model's hard gates
        self.assertIn("missing_approval_ref", API)
        self.assertIn("estimate_rejected", API)
        self.assertIn("action_approve()", API)

    def test_consent_grant_requires_proof(self):
        self.assertIn("missing_proof", API)
        self.assertIn("invalid_channel", API)

    def test_money_is_backend_formatted(self):
        self.assertIn("_fmt_bdt", API)
        self.assertIn("grand_total_bdt", API)


class TestApiSurface(unittest.TestCase):
    def test_openapi_has_customer_operations(self):
        import json
        spec = json.loads((REPO / "contracts" / "openapi"
                           / "w4-portals.json").read_text(encoding="utf-8"))
        for path in ("/customer/devices", "/customer/bookings",
                     "/customer/tracking", "/customer/estimates",
                     "/customer/consent", "/customer/ownership/transfer"):
            self.assertIn(path, spec["paths"])

    def test_routes_are_json_auth_user(self):
        routes = re.findall(
            r'@http\.route\("([^"]+)"[^)]*type="json",\s*auth="user"',
            API)
        self.assertGreaterEqual(len(routes), 6, routes)

    def test_no_readonly_write_route(self):
        # combined list/create endpoints must be readonly=False
        for m in re.finditer(
                r'@http\.route\("(/customer/(?:bookings|estimates|consent))"'
                r'[^)]*readonly=True', API):
            self.fail("write route declared readonly: %s" % m.group(1))


class TestManifest(unittest.TestCase):
    def test_cd_id_is_register_member(self):
        manifest = (MODULE / "__manifest__.py").read_text(encoding="utf-8")
        cd_id = re.search(r'"x_cd_id":\s*"([^"]+)"', manifest).group(1)
        register = yaml.safe_load((REPO / "tooling" / "cd-register.yaml"
                                   ).read_text(encoding="utf-8"))
        ids = {item["id"] for item in register["items"]}
        self.assertIn(cd_id, ids)

    def test_acl_grants_portal_group_only(self):
        for line in ACL.strip().splitlines()[1:]:
            self.assertIn("group_fix_customer_portal", line,
                          "ACL row outside the portal group: %s" % line)


if __name__ == "__main__":
    unittest.main()
