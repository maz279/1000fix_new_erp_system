# P04 Corporate API — the W4 contract endpoints (PP3).
#
# Serves the estate, consolidated invoices, and service requests the Next.js
# portal consumes. Data comes from the seeded/real Odoo models; every
# monetary value is backend-computed and BN-007-formatted (AS-10). The
# portal is a renderer, not a calculator (AS-09).

from datetime import date, timedelta

from odoo import fields, http
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
        warranty status (M17 + M09 read) and the site the asset lives at."""
        env = _tenant_env()
        devices = env["fix.device"].search(_tenant_domain("owner_id"), limit=200)
        result = []
        sites = {}
        for d in devices:
            warranties = d.warranty_id
            end = max((w.end_date for w in warranties if w.end_date), default=None)
            site = d.branch_id.name or ""
            if site:
                sites[site] = sites.get(site, 0) + 1
            identifier = d.imei_1 or d.serial_number or ""
            result.append(
                {
                    "id": d.id,
                    "brand": d.brand_id.name or "",
                    "model": d.device_model_id.name or d.name or "",
                    "identifier": (identifier[:6] + "…") if identifier else "",
                    "serial_number": d.serial_number or "",
                    "imei": d.imei_1 or "",
                    "asset_tag": d.asset_tag or "",
                    "site": site,
                    "state": d.state,
                    "custody_state": d.custody_state or "",
                    # the computed label is date-aware (in/extended/out/unknown)
                    "warranty_status": d.warranty_status or "unknown",
                    "warranty_end": str(end) if end else None,
                }
            )
        return {
            "devices": result,
            "total": len(result),
            "sites": [{"site": k, "count": v} for k, v in sorted(sites.items())],
        }

    @http.route("/corporate/invoices/consolidated", type="jsonrpc", auth="user", readonly=True)
    def consolidated_invoices(self, **kwargs):
        """Consolidated B2B invoices + the account statement view.

        Only customer-facing documents (issued / paid / credited) leave the
        back office — drafts, cancellations and write-offs are internal. Each
        row carries its due date, paid amount, balance, days overdue and aging
        bucket; totals are backend-computed strings (AS-09/AS-10)."""
        invoices = _tenant_env()["fix.ar.invoice"].search(
            [
                *_tenant_domain("customer_id"),
                ("state", "in", ("issued", "paid", "credited")),
            ],
            limit=100,
            order="invoice_date desc, id desc",
        )
        today = fields.Date.context_today(request.env.user)
        result = []
        outstanding = 0.0
        overdue = 0.0
        paid_total = 0.0
        overdue_count = 0
        buckets = {
            "current": [0, 0.0],
            "1-30": [0, 0.0],
            "31-60": [0, 0.0],
            "61-90": [0, 0.0],
            "90+": [0, 0.0],
        }
        for inv in invoices:
            total = inv.total_payable or 0.0
            paid = inv.amount_paid or 0.0
            balance = max(0.0, total - paid)
            due = inv.date_due or inv.invoice_date
            days_overdue = max(0, (today - due).days) if due and balance > 0 else 0
            if balance > 0:
                outstanding += balance
                if days_overdue:
                    overdue += balance
                    overdue_count += 1
            paid_total += min(paid, total)
            if balance <= 0 or days_overdue == 0:
                bucket = "current"
            elif days_overdue <= 30:
                bucket = "1-30"
            elif days_overdue <= 60:
                bucket = "31-60"
            elif days_overdue <= 90:
                bucket = "61-90"
            else:
                bucket = "90+"
            buckets[bucket][0] += 1
            buckets[bucket][1] += balance
            result.append(
                {
                    "id": inv.id,
                    "invoice_no": inv.name or "AR-%05d" % inv.id,
                    "customer": inv.customer_id.name or "",
                    "invoice_date": str(inv.invoice_date or ""),
                    "date_due": str(due or ""),
                    "state": inv.state,
                    "gross_bdt": _fmt_bdt((inv.taxable_amount or 0.0) + (inv.vat_amount or 0.0)),
                    "vat_bdt": _fmt_bdt(inv.vat_amount),
                    "net_bdt": _fmt_bdt(total),
                    "paid_bdt": _fmt_bdt(paid),
                    "balance_bdt": _fmt_bdt(balance),
                    "days_overdue": days_overdue,
                    "aging": bucket,
                }
            )
        return {
            "invoices": result,
            "total": len(result),
            "totals": {
                "outstanding_bdt": _fmt_bdt(outstanding),
                "overdue_bdt": _fmt_bdt(overdue),
                "paid_bdt": _fmt_bdt(paid_total),
                "count": len(result),
                "overdue_count": overdue_count,
            },
            "aging": [
                {"bucket": k, "count": v[0], "amount_bdt": _fmt_bdt(v[1])}
                for k, v in buckets.items()
            ],
        }

    @http.route("/corporate/contracts", type="jsonrpc", auth="user", readonly=True)
    def contracts(self, **kwargs):
        """Contracts and their SLA coverage for the signed-in corporate
        account (M08 read). Drafts and pre-signature states are internal; the
        customer sees active, expiring, expired, suspended and terminated."""
        contracts = _tenant_env()["fix.contract"].search(
            [
                *_tenant_domain("customer_id"),
                ("state", "in", ("active", "expiring", "expired", "suspended", "terminated")),
            ],
            limit=50,
            order="date_end desc, id desc",
        )
        today = fields.Date.context_today(request.env.user)
        result = []
        annual_total = 0.0
        expiring = 0
        active = 0
        for c in contracts:
            days = (c.date_end - today).days if c.date_end else None
            if c.state in ("active", "expiring"):
                active += 1
                annual_total += c.annual_value or 0.0
            if days is not None and 0 <= days <= 90:
                expiring += 1
            result.append(
                {
                    "id": c.id,
                    "code": c.code,
                    "name": c.name,
                    "family": c.family,
                    "date_start": str(c.date_start or ""),
                    "date_end": str(c.date_end or ""),
                    "state": c.state,
                    "annual_value_bdt": _fmt_bdt(c.annual_value),
                    "billing_frequency": c.billing_frequency,
                    "covered_count": len(c.covered_device_ids),
                    "days_to_expiry": days,
                    "slas": [
                        {
                            "code": s.code,
                            "name": s.name,
                            "response_hours": s.response_hours,
                            "resolution_hours": s.resolution_hours,
                        }
                        for s in c.sla_policy_ids
                    ],
                }
            )
        return {
            "contracts": result,
            "total": len(result),
            "summary": {
                "active": active,
                "expiring_90": expiring,
                "annual_value_bdt": _fmt_bdt(annual_total),
            },
        }

    @http.route("/corporate/tenders", type="jsonrpc", auth="user", readonly=True)
    def tenders(self, **kwargs):
        """Tenders where this account is the procuring client, plus the
        quotations 1000 FiX has issued to it (M36 read). Internal bid
        preparation (draft / no-bid) never leaves the back office."""
        env = _tenant_env()
        tenders = env["fix.tender"].search(
            [
                *_tenant_domain("client_id"),
                ("state", "in", ("submitted", "won", "lost")),
            ],
            limit=50,
            order="due_date desc, id desc",
        )
        quotations = env["fix.quotation"].search(
            [
                *_tenant_domain("customer_id"),
                ("state", "in", ("approved", "sent", "accepted", "declined", "expired")),
            ],
            limit=50,
            order="valid_until desc, id desc",
        )
        today = fields.Date.context_today(request.env.user)
        tender_rows = []
        for t in tenders:
            tender_rows.append(
                {
                    "id": t.id,
                    "reference": t.reference or "TND-%04d" % t.id,
                    "name": t.name,
                    "client_name": t.client_name or "",
                    "due_date": str(t.due_date or ""),
                    "state": t.state,
                    "tender_type": t.tender_type,
                    "estimated_value_bdt": _fmt_bdt(t.estimated_value),
                    "awarded_value_bdt": _fmt_bdt(t.awarded_value) if t.state == "won" else "",
                    "award_ref": t.award_ref or "",
                    "days_to_due": (t.due_date - today).days if t.due_date else None,
                }
            )
        quotation_rows = [
            {
                "id": q.id,
                "name": q.name,
                "quote_type": q.quote_type,
                "state": q.state,
                "version": q.version,
                "value_bdt": _fmt_bdt(q.value),
                "valid_until": str(q.valid_until or ""),
                "sent_at": str(q.sent_at or ""),
            }
            for q in quotations
        ]
        return {
            "tenders": tender_rows,
            "quotations": quotation_rows,
            "total": len(tender_rows) + len(quotation_rows),
        }

    @http.route("/corporate/profile", type="jsonrpc", auth="user", readonly=True)
    def profile(self, **kwargs):
        """The corporate account master data (own commercial partner only)."""
        partner = _corporate_partner()
        env = _tenant_env()
        partner = partner.with_env(env)
        manager = partner.user_id
        contacts = partner.child_ids.filtered(lambda p: p.active)
        users = partner.user_ids.filtered(lambda u: u.active)
        return {
            "company": {
                "id": partner.id,
                "name": partner.name or "",
                "bin": partner.vat or "",
                "company_registry": getattr(partner, "company_registry", False) or "",
                "phone": partner.phone or "",
                "email": partner.email or "",
                "street": " ".join(filter(None, [partner.street, partner.street2])),
                "city": partner.city or "",
                "zip": partner.zip or "",
                "country": partner.country_id.name or "",
                "payment_terms": partner.property_payment_term_id.name
                if "property_payment_term_id" in partner._fields
                else "",
            },
            "account_manager": {
                "name": manager.name or "",
                "email": manager.email or "",
                "phone": manager.phone or "",
            }
            if manager
            else None,
            "contacts": [
                {
                    "id": p.id,
                    "name": p.name or "",
                    "email": p.email or "",
                    "phone": p.phone or "",
                    "function": p.function or "",
                }
                for p in contacts
            ],
            "users": [{"id": u.id, "name": u.name, "login": u.login} for u in users],
        }

    @http.route("/corporate/reports/summary", type="jsonrpc", auth="user", readonly=True)
    def reports_summary(self, **kwargs):
        """Spend, service volume, estate distribution and AR aging for the
        account — every monetary value is a backend-computed BN-007 string."""
        env = _tenant_env()
        today = fields.Date.context_today(request.env.user)
        invoices = env["fix.ar.invoice"].search(
            [
                *_tenant_domain("customer_id"),
                ("state", "in", ("issued", "paid", "credited")),
            ],
            limit=500,
            order="invoice_date",
        )
        orders = env["fix.service.order"].search(_tenant_domain("customer_id"), limit=500)
        devices = env["fix.device"].search(_tenant_domain("owner_id"), limit=500)

        # Spend for the last six months, zero-filled.
        months = []
        cursor = date(today.year, today.month, 1)
        for _ in range(6):
            months.append(cursor)
            cursor = (cursor - timedelta(days=1)).replace(day=1)
        months.reverse()
        spend_map = {m.strftime("%Y-%m"): [0, 0.0] for m in months}
        for inv in invoices:
            if not inv.invoice_date:
                continue
            key = inv.invoice_date.strftime("%Y-%m")
            if key in spend_map:
                spend_map[key][0] += 1
                spend_map[key][1] += inv.total_payable or 0.0
        spend = []
        for month in months:
            key = month.strftime("%Y-%m")
            spend.append(
                {
                    "key": key,
                    "label": month.strftime("%b %Y"),
                    "count": spend_map[key][0],
                    "amount_bdt": _fmt_bdt(spend_map[key][1]),
                    # raw numeric for chart geometry only; the display value
                    # is the formatted string above (AS-09/AS-10)
                    "amount": round(spend_map[key][1], 2),
                }
            )

        state_counts = {}
        for o in orders:
            state_counts[o.state] = state_counts.get(o.state, 0) + 1
        orders_by_state = [
            {"state": k, "count": v} for k, v in sorted(state_counts.items(), key=lambda x: -x[1])
        ]

        site_counts = {}
        for d in devices:
            site = d.branch_id.name or "Unassigned"
            site_counts[site] = site_counts.get(site, 0) + 1
        estate_by_site = [
            {"site": k, "count": v} for k, v in sorted(site_counts.items(), key=lambda x: -x[1])
        ]

        # AR aging across outstanding balances.
        buckets = {
            "current": [0, 0.0],
            "1-30": [0, 0.0],
            "31-60": [0, 0.0],
            "61-90": [0, 0.0],
            "90+": [0, 0.0],
        }
        outstanding = 0.0
        for inv in invoices:
            balance = max(0.0, (inv.total_payable or 0.0) - (inv.amount_paid or 0.0))
            if balance <= 0:
                continue
            outstanding += balance
            due = inv.date_due or inv.invoice_date
            days = max(0, (today - due).days) if due else 0
            bucket = (
                "current"
                if days == 0
                else "1-30"
                if days <= 30
                else "31-60"
                if days <= 60
                else "61-90"
                if days <= 90
                else "90+"
            )
            buckets[bucket][0] += 1
            buckets[bucket][1] += balance

        active_contracts = env["fix.contract"].search_count(
            [*_tenant_domain("customer_id"), ("state", "in", ("active", "expiring"))]
        )
        open_orders = orders.filtered(lambda o: o.state not in ("delivered", "closed", "cancelled"))
        return {
            "spend": spend,
            "orders_by_state": orders_by_state,
            "estate_by_site": estate_by_site,
            "aging": [
                {
                    "bucket": k,
                    "count": v[0],
                    "amount_bdt": _fmt_bdt(v[1]),
                    "amount": round(v[1], 2),
                }
                for k, v in buckets.items()
            ],
            "totals": {
                "spend_bdt": _fmt_bdt(sum(v[1] for v in spend_map.values())),
                "outstanding_bdt": _fmt_bdt(outstanding),
                "assets": len(devices),
                "open_requests": len(open_orders),
                "active_contracts": active_contracts,
            },
        }

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
        """Create service requests at scale (M01 write; validation is
        server-side, AS-09). Accepts one ``device_id`` or a ``device_ids``
        list (B2B bulk intake); every device must belong to the customer's
        estate (M17) and the whole batch is atomic — one rejected device
        leaves no orders behind.

        The customer is DERIVED from the session: a corporate portal user
        always books for its own commercial partner (any ``customer_id`` sent
        by the client is ignored) and the orders are written with sudo() only
        after that ownership check. Internal staff (support desk) may name
        the customer and write under their own access rights."""
        category = kwargs.get("order_category", "standard")
        if category not in ("standard", "warranty", "amc"):
            return _error("invalid_category", "order_category must be standard|warranty|amc")
        staff = _is_staff()
        if staff and not kwargs.get("customer_id"):
            return _error("missing_customer", "customer_id is required")

        raw_ids = kwargs.get("device_ids")
        if isinstance(raw_ids, list | tuple):
            requested = [_to_int(v) for v in raw_ids]
        else:
            requested = [_to_int(kwargs.get("device_id"))]
        device_ids = list(dict.fromkeys(i for i in requested if i))
        if not device_ids:
            return _error(
                "missing_device",
                "device_id (or device_ids) is required (M17 — every order needs an identified device)",
            )
        if len(device_ids) > 50:
            return _error("too_many_devices", "A bulk request is limited to 50 devices")

        priority = kwargs.get("priority") or "normal"
        if priority not in ("normal", "high", "urgent"):
            return _error("invalid_priority", "priority must be normal|high|urgent")
        service_type = kwargs.get("service_type") or (
            "b2b_bulk" if len(device_ids) > 1 else "corporate"
        )
        if service_type not in ("corporate", "b2b_bulk", "web_portal"):
            return _error(
                "invalid_service_type", "service_type must be corporate|b2b_bulk|web_portal"
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
        if not customer:
            return _error("not_found", "customer_id does not exist")
        devices = env["fix.device"].search([("id", "in", device_ids)])
        if len(devices) != len(device_ids):
            # one answer for "absent" and "another tenant's": no id oracle
            return _error("not_found", "device_id does not exist in your estate")
        owned = all(
            d.owner_id.commercial_partner_id == customer.commercial_partner_id for d in devices
        )
        if not staff and not owned:
            return _error("not_found", "device_id does not exist in your estate")
        if not owned:
            return _error("not_owner", "A device is not registered to this customer")

        # branch_id is required by the model; prefer the device's own site,
        # then the requester's first allowed-company branch. Company-scoped
        # explicitly (AS-03 record rule).
        fallback_branch = env["fix.branch"].search(
            [("company_id", "in", request.env.companies.ids)], limit=1
        )
        if not fallback_branch and any(not d.branch_id for d in devices):
            return _error("no_branch", "No branch configured")

        created = []
        try:
            # the model's gates raise after the INSERT: a refused batch leaves nothing
            with request.env.cr.savepoint():
                for device in devices:
                    branch = device.branch_id or fallback_branch
                    order = env["fix.service.order"].create(
                        {
                            "customer_id": customer.id,
                            "device_id": device.id,
                            "order_category": category,
                            "fault_description": fault_description,
                            "branch_id": branch.id,
                            "priority": priority,
                            "service_type": service_type,
                        }
                    )
                    created.append(
                        {
                            "id": order.id,
                            "name": order.name,
                            "state": order.state,
                            "device_id": device.id,
                        }
                    )
        except (UserError, ValidationError, AccessError) as e:
            return _error("server_validation", str(e))
        return {
            "created": created,
            "total": len(created),
            # backward-compatible single-request fields
            "id": created[0]["id"],
            "name": created[0]["name"],
            "state": created[0]["state"],
        }

    def _list_service_requests(self, **kwargs):
        """Track service requests (M01 read)."""
        orders = _tenant_env()["fix.service.order"].search(
            _tenant_domain("customer_id"), limit=100, order="create_date desc"
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
                    "serial_number": o.device_id.serial_number if o.device_id else "",
                    "site": o.branch_id.name or "",
                    "priority": o.priority or "normal",
                    "service_type": o.service_type or "",
                    "technician": o.technician_id.name or "",
                    "response_deadline": str(o.sla_response_deadline or ""),
                    "resolution_deadline": str(o.sla_resolution_deadline or ""),
                    "opened_at": str(o.create_date or ""),
                }
            )
        return {"orders": result, "total": len(result)}
