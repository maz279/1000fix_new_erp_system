# P05 Vendor & Supplier API — the W4 contract endpoints (PP5).
#
# RFQ response (PO acknowledgement), delivery confirmation and invoice
# submission feeding cd_ap_ext's three-way match (G3-06: a blocked
# invoice is VISIBLE with its block reason, never warned about).
# Money is backend-computed BN-007 strings (AS-10); validation and the
# match engine stay server-side (AS-09). EA-05 scoping: a vendor sees
# only their own POs and invoices - the controller fences every query to the
# session's commercial partner (``_vendor_domain``) and the record rules in
# views/fix_vendor_portal_views.xml enforce the same at the ORM. Vendors may
# acknowledge POs and submit invoices; goods RECEIPTS are recorded by
# internal warehouse users only.

from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


def _fmt_bdt(amount):
    """BN-007 South Asian grouping — the portal receives the string (AS-10)."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    # Round ONCE, then split: formatting the whole and fractional parts
    # separately lost the rounding carry (999.996 -> "999.00") and mangled
    # negatives (-1234.5 -> "-1,2340.50").
    rounded = round(n, 2)
    sign = "-" if rounded < 0 else ""
    whole, frac = f"{abs(rounded):.2f}".split(".")
    if len(whole) > 3:
        rest, last3 = whole[:-3], whole[-3:]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        # rest is never empty here: it starts with >= 1 digit and the loop
        # stops at 1-2 digits, so it always leads the grouping
        whole = ",".join([rest, *parts, last3])
    return f"{sign}{whole}.{frac}"


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _is_staff():
    user = request.env.user
    return bool(user) and user._is_internal()


def _vendor_partner():
    """The vendor a portal session acts for: its COMMERCIAL partner."""
    return request.env.user.commercial_partner_id


def _vendor_domain(kwargs):
    """EA-05: a vendor (portal) session is fenced to ITS OWN commercial
    partner - any client-supplied vendor_id is ignored. Internal staff may
    pass vendor_id explicitly (procurement support view) and otherwise see
    what their own access rights allow."""
    if not _is_staff():
        return [("vendor_id", "child_of", _vendor_partner().id)]
    try:
        vendor_id = int(kwargs.get("vendor_id") or 0)
    except (TypeError, ValueError):
        vendor_id = 0
    if vendor_id:
        return [("vendor_id", "=", vendor_id)]
    return []


def _vendor_env():
    """Staff read/write under their own rights. A vendor session reads and
    writes with sudo() - but ONLY rows matched by ``_vendor_domain`` (every
    record is re-checked against it before an action)."""
    return request.env if _is_staff() else request.env(su=True)


def _own_po(po_id, kwargs):
    """The PO ``po_id`` if the caller may act on it, else an empty recordset
    (absent and foreign POs are indistinguishable to a vendor)."""
    try:
        po_id = int(po_id or 0)
    except (TypeError, ValueError):
        return _vendor_env()["fix.purchase.order"]
    domain = [("id", "=", po_id)]
    if not _is_staff():
        domain += _vendor_domain(kwargs)
    return _vendor_env()["fix.purchase.order"].search(domain, limit=1)


class VendorApiController(http.Controller):
    """The P05 vendor & supplier portal API (W4 contract)."""

    # --- Purchase orders / RFQ -------------------------------------------

    @http.route("/vendor/purchase-orders", type="jsonrpc", auth="user")
    def purchase_orders(self, **kwargs):
        """Combined endpoint: acknowledge when `po_id`+`action` are present,
        otherwise list (M16). RFQ response = acknowledging a `sent` PO."""
        if kwargs.get("po_id") and kwargs.get("action"):
            return self._act_on_po(**kwargs)
        domain = _vendor_domain(kwargs)
        state = kwargs.get("state")
        if state:
            domain.append(("state", "=", state))
        orders = _vendor_env()["fix.purchase.order"].search(domain, limit=100, order="id desc")
        result = [
            {
                "id": o.id,
                "ref": o.name,
                "state": o.state,
                "date_order": str(o.date_order or ""),
                "acknowledged_at": str(o.acknowledged_at or "") or None,
                "lines": [
                    {
                        "id": line.id,
                        "product_id": line.product_id.id,
                        "product": line.product_id.name or "",
                        "ordered": line.qty_ordered,
                        "received": line.qty_received,
                        "unit_price_bdt": _fmt_bdt(line.unit_price),
                    }
                    for line in o.line_ids
                ],
                "total_bdt": _fmt_bdt(o.amount_total),
            }
            for o in orders
        ]
        return {"purchase_orders": result, "total": len(result)}

    def _act_on_po(self, **kwargs):
        action = kwargs.get("action")
        if action not in ("acknowledge", "deliver"):
            return _error("invalid_action", "action must be acknowledge|deliver")
        order = _own_po(kwargs.get("po_id"), kwargs)
        if not order:
            return _error("no_po", "Purchase order not found")
        if action == "deliver" and not _is_staff():
            # receipts are recorded by internal warehouse users against the
            # physical goods-in - a vendor cannot self-certify its delivery
            # (it would feed the three-way match its own receipt quantities)
            return _error(
                "forbidden", "Deliveries are recorded by the receiving warehouse, not the vendor"
            )
        try:
            if action == "acknowledge":
                order.action_acknowledge()
            else:
                # delivery confirmation: {line_id: qty_received_this_delivery}
                receipts = kwargs.get("receipts") or {}
                if not receipts:
                    return _error("missing_receipts", "deliver needs receipts {line_id: qty}")
                order.action_record_receipt({int(k): float(v) for k, v in receipts.items()})
        except (UserError, ValidationError) as exc:
            return _error("po_rejected", str(exc))
        return {"purchase_order": {"id": order.id, "state": order.state}}

    # --- Invoices (3-way match) --------------------------------------------

    @http.route("/vendor/invoices", type="jsonrpc", auth="user", readonly=False)
    def invoices(self, **kwargs):
        """Combined endpoint: submit when `invoice_ref` is present,
        otherwise list. Submission runs the three-way match (G3-06)."""
        if kwargs.get("invoice_ref"):
            return self._submit_invoice(**kwargs)
        domain = _vendor_domain(kwargs)
        invoices = _vendor_env()["fix.vendor.invoice"].search(domain, limit=100, order="id desc")
        result = [
            {
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
            }
            for i in invoices
        ]
        return {"invoices": result, "total": len(result)}

    def _submit_invoice(self, **kwargs):
        """Invoice submission (M16-T03): the vendor's paper against a PO.
        The compute runs the match on save; the portal never judges."""
        po_id = kwargs.get("po_id")
        po = _own_po(po_id, kwargs)
        if po_id and not po:
            # a stale/foreign PO id is a structured error, not a MissingError
            # escaping as an HTTP 500 (same contract as _act_on_po)
            return _error("no_po", "Purchase order not found")
        # a vendor invoices as itself (the PO's vendor); only staff may name
        # another vendor id
        vendor_id = (kwargs.get("vendor_id") if _is_staff() else None) or po.vendor_id.id
        if not vendor_id:
            return _error("missing_vendor", "vendor_id (or a po_id to derive it) is required")
        if not po:
            return _error(
                "missing_po",
                "po_id is required (an invoice must land on a PO for the three-way match)",
            )
        lines = kwargs.get("lines") or []
        if not lines:
            return _error(
                "missing_lines",
                "lines [{product_id, description, quantity, "
                "unit_price, tds_category?}] are required",
            )
        Invoice = _vendor_env()["fix.vendor.invoice"]
        vals = {
            "vendor_id": int(vendor_id),
            "invoice_ref": kwargs.get("invoice_ref"),
            "requisition_id": po.id,
            # the model requires an operating unit; the portal rides the
            # PO's own OU (an invoice lands in the unit that ordered). The PO's
            # operating_unit_id is required (NOT NULL), so it is always set.
            "operating_unit_id": po.operating_unit_id.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": int(line["product_id"]),
                        "description": line.get("description", ""),
                        "quantity": float(line.get("quantity", 1.0)),
                        "unit_price": float(line.get("unit_price", 0.0)),
                        "tds_category": line.get("tds_category", "service_general"),
                    },
                )
                for line in lines
            ],
        }
        # an explicit None would OVERRIDE the model default (invoice_date
        # defaults to today) — only pass what the caller actually sent
        if kwargs.get("invoice_date"):
            vals["invoice_date"] = kwargs["invoice_date"]
        try:
            invoice = Invoice.create(vals)
        except (UserError, ValidationError) as exc:
            return _error("invoice_rejected", str(exc))
        return {
            "invoice": {
                "id": invoice.id,
                "match_state": invoice.match_state,
                "match_detail": invoice.match_detail or "",
            }
        }
