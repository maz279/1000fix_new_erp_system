# P04 Corporate API — the W4 contract endpoints (PP3).
#
# Serves the estate, consolidated invoices, and service requests the Next.js
# portal consumes. Data comes from the seeded/real Odoo models; every
# monetary value is backend-computed and BN-007-formatted (AS-10). The
# portal is a renderer, not a calculator (AS-09).

from odoo import http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request


def _fmt_bdt(amount):
    """BN-007 South Asian grouping (``1,23,45,678.00``) - the portal receives the
    string (AS-10). (The former int()/fraction split rounded 1.999 down to
    "1.00" and turned -1234.5 into "-1,2340.50".)"""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    whole_str, frac_str = f"{abs(n):.2f}".split(".")
    if len(whole_str) > 3:
        rest = whole_str[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        groups.insert(0, rest)  # 1-2 leading digits: len(whole_str) > 3 leaves rest non-empty
        whole_str = ",".join(groups) + "," + whole_str[-3:]
    sign = "-" if n < 0 else ""
    return f"{sign}{whole_str}.{frac_str}"


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _is_staff():
    user = request.env.user
    return bool(user) and user._is_internal()


def _corporate_partner():
    """The tenant this request acts for: the signed-in user's COMMERCIAL
    partner. Client-supplied customer ids are never trusted for a portal
    session (the UI used to fall back to partner id 1)."""
    return request.env.user.commercial_partner_id


def _tenant_env():
    """Internal staff read under their own access rights (record rules apply);
    a corporate portal session reads with sudo() but EVERY query below is
    fenced to its own commercial partner (``_tenant_domain``)."""
    return request.env if _is_staff() else request.env(su=True)


def _tenant_domain(field):
    """Staff: no extra fence (ACL + record rules apply). Portal: only rows of
    the user's own commercial partner and its contacts."""
    if _is_staff():
        return []
    return [(field, "child_of", _corporate_partner().id)]


class CorporateApiController(http.Controller):
    """The P04 corporate B2B portal API (W4 contract)."""

    @http.route("/corporate/estate", type="jsonrpc", auth="user", readonly=True)
    def estate(self, **kwargs):
        """The corporate asset estate: devices grouped by brand/model with
        warranty status (M17 + M09 read)."""
        env = _tenant_env()
        devices = env["fix.device"].search(_tenant_domain("owner_id"), limit=100)
        result = []
        for d in devices:
            warranty = env["fix.warranty"].search([("device_id", "=", d.id)], limit=1)
            result.append(
                {
                    "id": d.id,
                    "brand": d.brand_id.name or "",
                    "model": d.device_model_id.name or d.name or "",
                    "identifier": (d.imei_1 or d.serial_number or "")[:6] + "…",
                    "warranty_status": warranty.status if warranty else "pending",
                    "warranty_end": str(warranty.end_date)
                    if warranty and warranty.end_date
                    else None,
                }
            )
        return {"devices": result, "total": len(result)}

    @http.route("/corporate/invoices/consolidated", type="jsonrpc", auth="user", readonly=True)
    def consolidated_invoices(self, **kwargs):
        """Consolidated B2B invoices: multi-job invoices (M20/M39 read).
        Totals are backend-computed strings — the portal displays them."""
        invoices = _tenant_env()["fix.ar.invoice"].search(
            [*_tenant_domain("customer_id"), ("state", "!=", "cancelled")],
            limit=50,
            order="invoice_date desc",
        )
        result = []
        for inv in invoices:
            # gross = taxable value + VAT; net payable = the invoice's own total
            # after the loyalty offset (the former "net" was taxable MINUS VAT)
            result.append(
                {
                    "id": inv.id,
                    "invoice_no": f"AR-{inv.id:05d}",
                    "customer": inv.customer_id.name or "",
                    "invoice_date": str(inv.invoice_date or ""),
                    "state": inv.state,
                    "gross_bdt": _fmt_bdt(inv.taxable_amount + inv.vat_amount),
                    "vat_bdt": _fmt_bdt(inv.vat_amount),
                    "net_bdt": _fmt_bdt(inv.total_payable),
                }
            )
        return {"invoices": result, "total": len(result)}

    @http.route("/corporate/service-requests", type="jsonrpc", auth="user", readonly=False)
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
        """Create a service request at scale (M01 write; validation is
        server-side, AS-09). The device must belong to the customer (M17).

        The customer is DERIVED from the session: a corporate portal user
        always books for its own commercial partner (any ``customer_id`` sent
        by the client is ignored) and the order is written with sudo() only
        after that ownership check. Internal staff (support desk) may name
        the customer and write under their own access rights."""
        category = kwargs.get("order_category", "standard")
        if category not in ("standard", "warranty", "amc"):
            return _error("invalid_category", "order_category must be standard|warranty|amc")
        staff = _is_staff()
        if staff and not kwargs.get("customer_id"):
            return _error("missing_customer", "customer_id is required")
        if not kwargs.get("device_id"):
            return _error(
                "missing_device",
                "device_id is required (M17 — every order needs an identified device)",
            )
        fault_description = kwargs.get("fault_description", "")
        if not fault_description:
            return _error("missing_fault", "fault_description is required")
        env = _tenant_env()
        if staff:
            customer = env["res.partner"].search(
                [("id", "=", _to_int(kwargs["customer_id"]) or 0)], limit=1
            )
        else:
            customer = _corporate_partner().with_env(env)
        device = env["fix.device"].search([("id", "=", _to_int(kwargs["device_id"]) or 0)], limit=1)
        owned = bool(
            customer
            and device
            and device.owner_id.commercial_partner_id == customer.commercial_partner_id
        )
        if not staff and not owned:
            # one answer for "absent" and "another tenant's": no id oracle
            return _error("not_found", "device_id does not exist in your estate")
        if not customer or not device:
            return _error("not_found", "customer_id / device_id does not exist")
        if not owned:
            return _error("not_owner", "The device is not registered to this customer")
        # branch_id is required by the model; the corporate portal uses the
        # first branch of the REQUESTER'S ALLOWED COMPANIES as the intake
        # branch (multi-branch routing is M02). Company-scoped explicitly:
        # the AS-03 fix.branch record rule (R01 re-audit 2026-10-22) enforces
        # the same isolation at the ORM - an unscoped search silently
        # returned nothing (or, pre-rule, another company's branch).
        branch = env["fix.branch"].search(
            [("company_id", "in", request.env.companies.ids)], limit=1
        )
        if not branch:
            return _error("no_branch", "No branch configured")
        try:
            # the model's gates raise after the INSERT: a refused order leaves nothing
            with request.env.cr.savepoint():
                order = env["fix.service.order"].create(
                    {
                        "customer_id": customer.id,
                        "device_id": device.id,
                        "order_category": category,
                        "fault_description": fault_description,
                        "branch_id": branch.id,
                    }
                )
        except (UserError, ValidationError, AccessError) as e:
            return _error("server_validation", str(e))
        return {"id": order.id, "state": order.state}

    def _list_service_requests(self, **kwargs):
        """Track service requests (M01 read)."""
        orders = _tenant_env()["fix.service.order"].search(
            _tenant_domain("customer_id"), limit=50, order="create_date desc"
        )
        result = []
        for o in orders:
            result.append(
                {
                    "id": o.id,
                    "name": o.name,
                    "state": o.state,
                    "customer": o.customer_id.name or "",
                    "device": o.device_id.name if o.device_id else "",
                    "opened_at": str(o.create_date or ""),
                }
            )
        return {"orders": result, "total": len(result)}
