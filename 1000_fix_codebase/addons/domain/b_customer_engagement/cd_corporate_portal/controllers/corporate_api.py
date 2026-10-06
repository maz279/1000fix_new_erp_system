# P04 Corporate API — the W4 contract endpoints (PP3).
#
# Serves the estate, consolidated invoices, and service requests the Next.js
# portal consumes. Data comes from the seeded/real Odoo models; every
# monetary value is backend-computed and BN-007-formatted (AS-10). The
# portal is a renderer, not a calculator (AS-09).
from odoo import http
from odoo.http import request

import json


def _fmt_bdt(amount):
    """Format a monetary value as a BN-007-style South Asian-grouped string.
    The portal never does this math — it receives the string (AS-10)."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    # South Asian grouping: 1,23,45,678.00
    whole = int(n)
    frac = f"{n - whole:.2f}"[1:]  # ".xx"
    s = str(whole)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        return ",".join(parts) + "," + last3 + frac
    return s + frac


class CorporateApiController(http.Controller):
    """The P04 corporate B2B portal API (W4 contract)."""

    @http.route("/corporate/estate", type="json", auth="user", readonly=True)
    def estate(self, **kwargs):
        """The corporate asset estate: devices grouped by brand/model with
        warranty status (M17 + M09 read)."""
        devices = request.env["fix.device"].search([], limit=100)
        result = []
        for d in devices:
            warranty = request.env["fix.warranty"].search(
                [("device_id", "=", d.id)], limit=1)
            result.append({
                "id": d.id,
                "brand": d.brand_id.name or "",
                "model": d.device_model_id.name or d.name or "",
                "identifier": (d.imei_1 or d.serial_number or "")[:6] + "…",
                "warranty_status": warranty.status if warranty else "pending",
                "warranty_end": str(warranty.end_date) if warranty and warranty.end_date else None,
            })
        return {"devices": result, "total": len(result)}

    @http.route("/corporate/invoices/consolidated", type="json",
                auth="user", readonly=True)
    def consolidated_invoices(self, **kwargs):
        """Consolidated B2B invoices: multi-job invoices (M20/M39 read).
        Totals are backend-computed strings — the portal displays them."""
        invoices = request.env["fix.ar.invoice"].search(
            [("state", "!=", "cancelled")], limit=50,
            order="invoice_date desc")
        result = []
        for inv in invoices:
            gross = inv.taxable_amount or 0
            vat = inv.vat_amount or 0
            result.append({
                "id": inv.id,
                "invoice_no": f"AR-{inv.id:05d}",
                "customer": inv.customer_id.name or "",
                "invoice_date": str(inv.invoice_date or ""),
                "state": inv.state,
                "gross_bdt": _fmt_bdt(gross),
                "vat_bdt": _fmt_bdt(vat),
                "net_bdt": _fmt_bdt(gross - vat),
            })
        return {"invoices": result, "total": len(result)}

    @http.route("/corporate/service-requests", type="json",
                auth="user", readonly=False)
    def service_requests(self, **kwargs):
        """Track and create service requests (M01 read/write).
        
        Combined endpoint: if `order_category` is provided → create;
        otherwise → list. (JSON-RPC routes are always POST; two routes
        at the same path conflict in Odoo's dispatcher.)
        """
        if kwargs.get("order_category"):
            return self._create_service_request(**kwargs)
        return self._list_service_requests(**kwargs)

    def _create_service_request(self, **kwargs):
        """Create a service request at scale (M01 write via the model —
        the portal passes through; validation is server-side, AS-09)."""
        category = kwargs.get("order_category", "standard")
        if category not in ("standard", "warranty", "amc"):
            return {"error": {"code": "invalid_category",
                              "message": "order_category must be standard|warranty|amc"}}
        customer_id = kwargs.get("customer_id")
        if not customer_id:
            return {"error": {"code": "missing_customer",
                              "message": "customer_id is required"}}
        device_id = kwargs.get("device_id")
        if not device_id:
            return {"error": {"code": "missing_device",
                              "message": "device_id is required (M17 — every order needs an identified device)"}}
        fault_description = kwargs.get("fault_description", "")
        if not fault_description:
            return {"error": {"code": "missing_fault",
                              "message": "fault_description is required"}}
        # branch_id is required by the model; the corporate portal uses the
        # first branch as the intake branch (multi-branch routing is M02)
        branch = request.env["fix.branch"].search([], limit=1)
        if not branch:
            return {"error": {"code": "no_branch",
                              "message": "No branch configured"}}
        try:
            order = request.env["fix.service.order"].create({
                "customer_id": customer_id,
                "device_id": device_id,
                "order_category": category,
                "fault_description": fault_description,
                "branch_id": branch.id,
            })
        except Exception as e:
            return {"error": {"code": "server_validation",
                              "message": str(e)}}
        return {"id": order.id, "state": order.state}

    def _list_service_requests(self, **kwargs):
        """Track service requests (M01 read)."""
        orders = request.env["fix.service.order"].search([], limit=50,
                                                         order="create_date desc")
        result = []
        for o in orders:
            result.append({
                "id": o.id,
                "name": o.name,
                "state": o.state,
                "customer": o.customer_id.name or "",
                "device": o.device_id.name if o.device_id else "",
                "opened_at": str(o.create_date or ""),
            })
        return {"orders": result, "total": len(result)}
