# P05 Vendor & Supplier API — the W4 contract endpoints (PP5).
#
# RFQ response (PO acknowledgement), delivery confirmation and invoice
# submission feeding cd_ap_ext's three-way match (G3-06: a blocked
# invoice is VISIBLE with its block reason, never warned about).
# Money is backend-computed BN-007 strings (AS-10); validation and the
# match engine stay server-side (AS-09). EA-05 scoping: a vendor sees
# only their own POs and invoices (security/ record rules).
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

import json


def _fmt_bdt(amount):
    """BN-007 South Asian grouping — the portal receives the string (AS-10)."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    whole = int(n)
    frac = f"{n - whole:.2f}"[1:]
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


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _vendor_domain(kwargs):
    """EA-05: vendors are scoped to their own rows; an internal user may
    pass vendor_id explicitly (procurement support view)."""
    vendor_id = kwargs.get("vendor_id")
    if vendor_id:
        return [("vendor_id", "=", int(vendor_id))]
    return []


class VendorApiController(http.Controller):
    """The P05 vendor & supplier portal API (W4 contract)."""

    # --- Purchase orders / RFQ -------------------------------------------

    @http.route("/vendor/purchase-orders", type="json", auth="user")
    def purchase_orders(self, **kwargs):
        """Combined endpoint: acknowledge when `po_id`+`action` are present,
        otherwise list (M16). RFQ response = acknowledging a `sent` PO."""
        if kwargs.get("po_id") and kwargs.get("action"):
            return self._act_on_po(**kwargs)
        domain = _vendor_domain(kwargs)
        state = kwargs.get("state")
        if state:
            domain.append(("state", "=", state))
        orders = request.env["fix.purchase.order"].search(
            domain, limit=100, order="id desc")
        result = [{
            "id": o.id,
            "ref": o.name,
            "state": o.state,
            "date_order": str(o.date_order or ""),
            "acknowledged_at": str(o.acknowledged_at or "") or None,
            "lines": [{
                "id": l.id,
                "product_id": l.product_id.id,
                "product": l.product_id.name or "",
                "ordered": l.qty_ordered,
                "received": l.qty_received,
                "unit_price_bdt": _fmt_bdt(l.unit_price),
            } for l in o.line_ids],
            "total_bdt": _fmt_bdt(o.amount_total),
        } for o in orders]
        return {"purchase_orders": result, "total": len(result)}

    def _act_on_po(self, **kwargs):
        action = kwargs.get("action")
        if action not in ("acknowledge", "deliver"):
            return _error("invalid_action",
                          "action must be acknowledge|deliver")
        order = request.env["fix.purchase.order"].browse(
            int(kwargs.get("po_id")))
        if not order.exists():
            return _error("no_po", "Purchase order not found")
        try:
            if action == "acknowledge":
                order.action_acknowledge()
            else:
                # delivery confirmation: {line_id: qty_received_this_delivery}
                receipts = kwargs.get("receipts") or {}
                if not receipts:
                    return _error("missing_receipts",
                                  "deliver needs receipts {line_id: qty}")
                order.action_record_receipt(
                    {int(k): float(v) for k, v in receipts.items()})
        except (UserError, ValidationError) as exc:
            return _error("po_rejected", str(exc))
        return {"purchase_order": {"id": order.id, "state": order.state}}

    # --- Invoices (3-way match) --------------------------------------------

    @http.route("/vendor/invoices", type="json", auth="user",
                readonly=False)
    def invoices(self, **kwargs):
        """Combined endpoint: submit when `invoice_ref` is present,
        otherwise list. Submission runs the three-way match (G3-06)."""
        if kwargs.get("invoice_ref"):
            return self._submit_invoice(**kwargs)
        domain = _vendor_domain(kwargs)
        invoices = request.env["fix.vendor.invoice"].search(
            domain, limit=100, order="id desc")
        result = [{
            "id": i.id,
            "invoice_ref": i.invoice_ref,
            "po_ref": i.requisition_id.name or "",
            "date": str(i.invoice_date or ""),
            "subtotal_bdt": _fmt_bdt(i.subtotal),
            "tds_bdt": _fmt_bdt(i.tds_amount),
            "payable_bdt": _fmt_bdt(i.total_payable),
            "match_state": i.match_state,
            # G3-06: the block reason ships WITH the blocked state —
            # visible, never warned about in the portal
            "match_detail": i.match_detail or "",
        } for i in invoices]
        return {"invoices": result, "total": len(result)}

    def _submit_invoice(self, **kwargs):
        """Invoice submission (M16-T03): the vendor's paper against a PO.
        The compute runs the match on save; the portal never judges."""
        vendor_id = kwargs.get("vendor_id") or (
            request.env["fix.purchase.order"].browse(
                int(kwargs.get("po_id", 0))).vendor_id.id
            if kwargs.get("po_id") else False)
        if not vendor_id:
            return _error("missing_vendor",
                          "vendor_id (or a po_id to derive it) is required")
        po_id = kwargs.get("po_id")
        if not po_id:
            return _error("missing_po",
                          "po_id is required (an invoice must land on a PO "
                          "for the three-way match)")
        lines = kwargs.get("lines") or []
        if not lines:
            return _error("missing_lines",
                          "lines [{product_id, description, quantity, "
                          "unit_price, tds_category?}] are required")
        Invoice = request.env["fix.vendor.invoice"]
        try:
            invoice = Invoice.create({
                "vendor_id": int(vendor_id),
                "invoice_ref": kwargs.get("invoice_ref"),
                "invoice_date": kwargs.get("invoice_date") or None,
                "requisition_id": int(po_id),
                "line_ids": [(0, 0, {
                    "product_id": int(l["product_id"]),
                    "description": l.get("description", ""),
                    "quantity": float(l.get("quantity", 1.0)),
                    "unit_price": float(l.get("unit_price", 0.0)),
                    "tds_category": l.get("tds_category", "service_general"),
                }) for l in lines],
            })
        except (UserError, ValidationError) as exc:
            return _error("invoice_rejected", str(exc))
        return {"invoice": {
            "id": invoice.id,
            "match_state": invoice.match_state,
            "match_detail": invoice.match_detail or "",
        }}
