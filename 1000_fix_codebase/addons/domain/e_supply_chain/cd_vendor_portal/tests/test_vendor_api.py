# cd_vendor_portal tests — P05 PP5 API surface.
#
# A06 audit (2026-11-03): this file asserted source text of vendor_api.py
# (assertIn on the module text: "action_acknowledge()" present, "received <"
# absent...). Those properties are behaviour and are tested as behaviour in
# test_vendor_api_live.py (match state and detail shipped with a submission,
# structured error codes, the PO's unit on the invoice, the invoice-date
# default, delivery refused to a vendor) and test_a06_m42_controls.py /
# cd_requisition's test_a06_m16_controls.py (acknowledgement, double billing,
# withholding category). What remains here is the published contract: the
# OpenAPI paths, the routes' type and auth, and the module dependencies.
import json
from pathlib import Path

from odoo.addons.cd_vendor_portal.controllers.vendor_api import VendorApiController
from odoo.modules.module import get_manifest

REPO = Path(__file__).resolve().parents[5]


def test_openapi_has_vendor_operations():
    spec = json.loads(
        (REPO / "contracts" / "openapi" / "w4-portals.json").read_text(encoding="utf-8")
    )
    for path in ("/vendor/purchase-orders", "/vendor/invoices"):
        assert path in spec["paths"]


def test_routes_json_auth_user():
    for method, path in (
        (VendorApiController.purchase_orders, "/vendor/purchase-orders"),
        (VendorApiController.invoices, "/vendor/invoices"),
    ):
        routing = method.original_routing
        assert routing["routes"] == [path]
        assert (routing["type"], routing["auth"]) == ("jsonrpc", "user")


def test_module_depends_on_requisition_and_ap(odoo_env):
    depends = get_manifest("cd_vendor_portal")["depends"]
    assert {"cd_requisition", "cd_ap_ext", "cd_rbac_ext"} <= set(depends)
