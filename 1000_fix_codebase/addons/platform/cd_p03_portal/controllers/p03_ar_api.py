# P03 AR API — the read/write endpoints behind the M20 in-workspace screens.
#
# Every screen of M20 (invoices, the Mushak invoice record, billable events,
# consolidated bills, brand claims, receipts, payment links, matching &
# allocation, credit control, dunning, disputes, ageing, leakage and customer
# statements) is fed from here — live reads of the real cd_billing_engine
# models. Write paths call the SAME model methods the Odoo forms use, so the
# NID rule, FR-ARB-025, the credit-note authority ladder, the write-off
# authority matrix and the ageing-snapshot immutability apply identically.
#
# Every write endpoint wraps its work in a savepoint: a refused action
# (UserError) must leave nothing behind (the M19 leaked-draft lesson).
# Internal-user only (NVR-22). Nothing is fabricated — absent data comes
# back as None/[] and the workspace keeps its honest placeholder.
import datetime
from datetime import timedelta

from odoo import http
from odoo.addons.cd_billing_engine.models.fix_ar_engine import (
    age_slot,
    compute_customer_statement,
    compute_leakage,
    takeon_ar_opening,
    takeon_label,
)
from odoo.exceptions import UserError
from odoo.http import request

from .p03_service_order_api import _require_internal, _user_error


def aging_live_rows(env):
    """Open receivables by customer and age bucket as of today: issued
    invoices with a balance, plus each customer's legacy take-on still open
    on the AR control (the Aging screen and its report pack share this)."""
    # live current view (as of today) for the grid before any capture
    today = datetime.date.today()
    buckets = {}
    invoices = (
        env["fix.ar.invoice"]
        .search([("state", "=", "issued")])
        .filtered(lambda i: i.amount_residual > 0.005)
    )
    for inv in invoices:
        days_past = (today - inv.invoice_date).days - inv._payment_terms_days()
        slot = (
            "current"
            if days_past <= 0
            else "d1_30"
            if days_past <= 30
            else "d31_60"
            if days_past <= 60
            else "d61_90"
            if days_past <= 90
            else "d90_plus"
        )
        per = buckets.setdefault(
            inv.customer_id.name,
            {"current": 0.0, "d1_30": 0.0, "d31_60": 0.0, "d61_90": 0.0, "d90_plus": 0.0},
        )
        per[slot] += inv.amount_residual
    # each customer's legacy take-on still open on the AR control: its own
    # line, aged from the take-on date (finance roles: GL lines)
    if env["account.move.line"].has_access("read"):
        Partner = env["res.partner"].sudo()
        for company in env.companies:
            for partner_id, opening in takeon_ar_opening(env, company, as_of=today).items():
                if abs(opening["residual"]) <= 0.005:
                    continue
                name = Partner.browse(partner_id).name if partner_id else "(no customer)"
                per = buckets.setdefault(
                    "%s · %s" % (name, takeon_label(opening["date"])),
                    {
                        "current": 0.0,
                        "d1_30": 0.0,
                        "d31_60": 0.0,
                        "d61_90": 0.0,
                        "d90_plus": 0.0,
                    },
                )
                per[age_slot((today - opening["date"]).days)] += opening["residual"]
    live_rows = [
        dict({"customer": name}, **{k: round(v, 2) for k, v in amounts.items()})
        for name, amounts in sorted(buckets.items())
    ]
    return live_rows


def _invoice_row(inv):
    return {
        "id": inv.id,
        "name": inv.name if inv.name != "New" else "",
        "customer": inv.customer_id.name,
        "customer_id": inv.customer_id.id,
        "date": str(inv.invoice_date),
        "taxable": inv.taxable_amount,
        "vat": inv.vat_amount,
        "total": inv.total_payable,
        "paid": inv.amount_paid,
        "credited": inv.credited_amount,
        "residual": inv.amount_residual,
        "state": inv.state,
        "mushak": inv.mushak_id.mushak_no or "",
        "source": "%s/%s" % (inv.source_model, inv.source_id),
        "auto": inv.source_model != "manual",
        "gl_move": inv.posted_move_id.name or "",
        "gl_note": inv.gl_note or "",
        "gl_posted": bool(inv.posted_move_id),
        "paid_date": str(inv.paid_date) if inv.paid_date else "",
        "category": inv.customer_category or "",
        "category_label": inv._fix_category_label() if hasattr(inv, "_fix_category_label") else "",
        "due_date": str(_due(inv)) if inv.invoice_date else "",
        "terms_days": (_due(inv) - inv.invoice_date).days if inv.invoice_date else 0,
        "days_past_due": max((datetime.date.today() - _due(inv)).days, 0)
        if inv.invoice_date
        else 0,
    }


def _due(inv):
    """The invoice's due date: on the day for walk-in and cash customers
    (commercial document standard), else by the customer's payment terms."""
    if "date_due" in inv._fields and inv.date_due:
        return inv.date_due
    return inv.invoice_date + timedelta(days=inv._payment_terms_days())


def _invoice_header(inv):
    """The document header and footer the invoice record tab shows."""
    party = inv._fix_doc_party() if hasattr(inv, "_fix_doc_party") else {}
    return {
        "bill_to": party,
        "po_ref": inv.customer_po_ref or "",
        "po_date": str(inv.customer_po_date) if inv.customer_po_date else "",
        "salesperson": inv.salesperson_id.name or "",
        "service_item": inv.service_item or "",
        "challan": inv.challan_ref or "",
        "delivery_address": inv.delivery_address or "",
        "vehicle": inv.vehicle_no or "",
        "remarks": inv.remarks or "",
        "reason": inv.manual_reason or "",
        "date_due": str(inv.date_due) if inv.date_due else "",
        "items": inv.item_count,
        "quantity": inv.total_quantity,
        "gross": inv.gross_total,
        "discount": inv.discount_total,
        "words": inv.amount_in_words_en if "amount_in_words_en" in inv._fields else "",
        "print_url": "/report/pdf/cd_doc_suite.report_invoice/%s" % inv.id,
    }


def _float(value):
    try:
        return round(float(value or 0.0), 6)
    except (TypeError, ValueError):
        return 0.0


def _editor_line(line):
    """An editor line -> fix.ar.invoice.line values (the commercial line
    standard). The old editor sent {description, taxable, vat}: kept."""
    if "unit_price" not in line and "taxable" in line:
        return {
            "description": line.get("description") or "Service",
            "taxable_amount": round(_float(line.get("taxable")), 2),
            "vat_amount": round(_float(line.get("vat")), 2),
            "line_total": round(_float(line.get("taxable")) + _float(line.get("vat")), 2),
        }
    vals = {
        "line_type": line.get("line_type") or "service",
        "description": (line.get("description") or "").strip(),
        "quantity": _float(line.get("quantity")),
        "unit_price": _float(line.get("unit_price")),
        "discount_pct": _float(line.get("discount_pct")),
    }
    if line.get("product_id"):
        vals["product_id"] = int(line["product_id"])
    if line.get("uom_id"):
        vals["uom_id"] = int(line["uom_id"])
    if (line.get("serial") or "").strip():
        vals["serial_ref"] = line["serial"].strip()
    return vals


def _editor_line_is_blank(line):
    if "unit_price" not in line:
        return _float(line.get("taxable")) <= 0
    return not line.get("product_id") and _float(line.get("unit_price")) <= 0


# Header fields the invoice editor may set (the document header standard).
EDITOR_HEADER = (
    "customer_category",
    "bill_to_name",
    "bill_to_phone",
    "bill_to_address",
    "customer_bin",
    "customer_po_ref",
    "service_item",
    "challan_ref",
    "delivery_address",
    "vehicle_no",
    "remarks",
)


# The controlled lists the single-value prompts offer (M20-10, M20-11).
DUNNING_SUPPRESSIONS = ("dispute", "payment_plan", "strategic")
DISPUTE_OUTCOME_CODES = (
    "upheld_credit",
    "partially_upheld",
    "rejected",
    "withdrawn",
    "payment_plan",
)


def _split_prompt(value, parts):
    """A prompt's text split on "|" into exactly `parts` stripped values; the
    missing ones are None. The last value keeps any further "|"."""
    pieces = [p.strip() for p in str(value or "").split("|", parts - 1)]
    pieces += [None] * (parts - len(pieces))
    return [p or None for p in pieces]


class P03ArApiController(http.Controller):
    """M20 in-workspace screen data."""

    # ------------------------------------------------------------- invoices

    @http.route("/p03/ar/invoices", type="jsonrpc", auth="user", readonly=True)
    def ar_invoices(self, state=None, customer_id=None, source=None, **kw):
        _require_internal(request.env)
        env = request.env
        domain = []
        if state:
            domain.append(("state", "=", state))
        if customer_id:
            domain.append(("customer_id", "=", int(customer_id)))
        if source:
            domain.append(("source_model", "=", source))
        invoices = env["fix.ar.invoice"].search(
            domain, order="invoice_date desc, id desc", limit=200
        )
        return {"rows": [_invoice_row(i) for i in invoices]}

    @http.route("/p03/ar/invoice", type="jsonrpc", auth="user", readonly=True)
    def ar_invoice(self, invoice_id=None, **kw):
        _require_internal(request.env)
        inv = request.env["fix.ar.invoice"].browse(int(invoice_id))
        if not inv.exists():
            return {"invoice": None}
        return {
            "invoice": _invoice_row(inv),
            "header": _invoice_header(inv),
            "lines": [
                {
                    "sl": index,
                    "line_type": line.line_type or "",
                    "type_label": dict(line._fields["line_type"].selection).get(line.line_type, ""),
                    "code": line.item_code or "",
                    "description": line.description or "",
                    "serial": line.serial_ref or "",
                    "quantity": line.quantity,
                    "uom": line.uom_id.name or "",
                    "unit_price": line.unit_price,
                    "discount": line.discount_amount,
                    "taxable": line.taxable_amount,
                    "vat_rate": line.vat_rate,
                    "vat": line.vat_amount,
                    "total": line.line_total,
                }
                for index, line in enumerate(inv.line_ids.sorted(lambda r: (r.sequence, r.id)), 1)
            ],
            "allocations": [
                {
                    "receipt": a.receipt_id.name,
                    "amount": a.amount,
                    "date": str(a.allocated_at.date()) if a.allocated_at else "",
                }
                for a in inv.allocation_ids
            ],
            "credit_notes": [
                {"amount": n.amount, "reason": n.reason_code, "state": n.state}
                for n in inv.credit_note_ids
            ],
            "disputes": [
                {"amount": d.amount_disputed, "reason": d.reason, "state": d.state}
                for d in inv.env["fix.ar.dispute"].search([("invoice_id", "=", inv.id)])
            ],
            "mushak": {
                "no": inv.mushak_id.mushak_no or "",
                "posted": inv.mushak_id.posted,
                "supplier_bin": inv.mushak_id.supplier_bin or "",
                "customer_bin": inv.mushak_id.customer_bin or "",
            }
            if inv.mushak_id
            else None,
        }

    # ------------------------------------------------------- billable events

    @http.route("/p03/ar/events", type="jsonrpc", auth="user", readonly=True)
    def ar_events(self, state=None, **kw):
        _require_internal(request.env)
        env = request.env
        domain = []
        if state:
            domain.append(("state", "=", state))
        rows = env["fix.billable.event"].search(domain, order="first_seen_at desc", limit=200)
        counts = {}
        for row in env["fix.billable.event"].search([]):
            counts[row.state] = counts.get(row.state, 0) + 1
        return {
            "rows": [
                {
                    "id": r.id,
                    "event": r.event_id[:13] + "…",
                    "age_days": r.age_days,
                    "source": "%s/%s" % (r.source_model, r.source_id),
                    "customer": r.customer_id.name or "",
                    "state": r.state,
                    "attempts": r.attempts,
                    "error": (r.last_error or "")[:160],
                    "invoice": r.invoice_id.name or "",
                }
                for r in rows
            ],
            "counts": counts,
            "stranded_outbox": env["fix.event.outbox"]
            .sudo()
            .search_count([("event_type", "=", "service_order.closed")]),
        }

    # ---------------------------------------------------------- consolidated

    @http.route("/p03/ar/consolidated", type="jsonrpc", auth="user", readonly=True)
    def ar_consolidated(self, **kw):
        _require_internal(request.env)
        bills = request.env["fix.ar.consolidated.bill"].search([], limit=100)
        return {
            "rows": [
                {
                    "id": b.id,
                    "ref": b.bill_ref,
                    "customer": b.customer_id.name,
                    "period": "%s → %s" % (b.period_start, b.period_end),
                    "invoices": len(b.invoice_ids),
                    "total": b.total_payable,
                    "state": b.state,
                }
                for b in bills
            ]
        }

    # -------------------------------------------------------------- receipts

    @http.route("/p03/ar/receipts", type="jsonrpc", auth="user", readonly=True)
    def ar_receipts(self, state=None, **kw):
        _require_internal(request.env)
        env = request.env
        domain = []
        if state:
            domain.append(("state", "=", state))
        rows = env["fix.ar.receipt"].search(domain, order="receipt_date desc, id desc", limit=200)
        return {
            "rows": [
                {
                    "id": r.id,
                    "name": r.name,
                    "customer": r.customer_id.name,
                    "customer_id": r.customer_id.id,
                    "date": str(r.receipt_date),
                    "method": r.method or "",
                    "payment_method": r.payment_method_id.name or "",
                    "reference": r.reference or "",
                    "amount": r.amount,
                    "allocated": r.allocated_amount,
                    "unapplied": r.unapplied_amount,
                    "state": r.state,
                    "gl_posted": bool(r.posted_move_id),
                    "gl_note": r.gl_note or "",
                    "nid": r.nid_captured or "",
                }
                for r in rows
            ],
            "methods": [m[0] for m in env["fix.ar.receipt"]._fields["method"].selection],
            # the one customer payment-method list (quote-to-cash P1): what the
            # capture form offers; each sets the tender the receipt books as
            "payment_methods": [
                {"id": pm.id, "name": pm.name, "receipt_method": pm.receipt_method}
                for pm in env["fix.payment.method"].search([("receipt_method", "!=", False)])
            ],
            "branches": [
                {"id": b.id, "name": b.name}
                for b in env["fix.branch"].search([("active", "=", True)], order="name", limit=300)
            ],
        }

    @http.route("/p03/ar/open-items", type="jsonrpc", auth="user", readonly=True)
    def ar_open_items(self, customer_id=None, **kw):
        """Open issued invoices with residual — the allocation console's
        right-hand side."""
        _require_internal(request.env)
        env = request.env
        domain = [("state", "=", "issued")]
        if customer_id:
            domain.append(("customer_id", "=", int(customer_id)))
        invoices = (
            env["fix.ar.invoice"]
            .search(domain, order="invoice_date asc")
            .filtered(lambda i: i.amount_residual > 0.005)
        )
        return {"rows": [_invoice_row(i) for i in invoices]}

    @http.route("/p03/ar/match", type="jsonrpc", auth="user", readonly=True)
    def ar_match(self, **kw):
        _require_internal(request.env)
        proposals = request.env["fix.ar.receipt"].action_auto_match()
        unmatched = (
            request.env["fix.ar.receipt"]
            .search([("state", "=", "confirmed")])
            .filtered(lambda r: r.unapplied_amount > 0.005)
        )
        unapplied_wo_proposal = [
            {"receipt": r.name, "customer": r.customer_id.name, "amount": r.unapplied_amount}
            for r in unmatched
            if r.id not in {p["receipt_id"] for p in proposals}
        ]
        return {"proposals": proposals, "exceptions": unapplied_wo_proposal}

    # -------------------------------------------------------- credit control

    @http.route("/p03/ar/credit-notes", type="jsonrpc", auth="user", readonly=True)
    def ar_credit_notes(self, **kw):
        _require_internal(request.env)
        notes = request.env["fix.credit.note"].search([], limit=200)
        return {
            "rows": [
                {
                    "id": n.id,
                    "invoice": n.invoice_id.name or "AR/%s" % n.invoice_id.id,
                    "invoice_id": n.invoice_id.id,
                    "customer": n.invoice_id.customer_id.name,
                    "amount": n.amount,
                    "reason": n.reason_code,
                    "state": n.state,
                    "issued_at": str(n.issued_at.date()) if n.issued_at else "",
                    "gl_posted": bool(n.posted_move_id),
                }
                for n in notes
            ]
        }

    @http.route("/p03/ar/credit-profiles", type="jsonrpc", auth="user", readonly=True)
    def ar_credit_profiles(self, **kw):
        _require_internal(request.env)
        env = request.env
        profiles = env["fix.credit.profile"].search([])
        return {
            "rows": [
                {
                    "id": p.id,
                    "customer": p.customer_id.name,
                    "customer_id": p.customer_id.id,
                    "limit": p.credit_limit,
                    "exposure": p.exposure,
                    "over_limit": p.over_limit,
                    "terms": p.payment_terms_days,
                    "hold": p.credit_hold,
                    "hold_reason": p.hold_reason or "",
                }
                for p in profiles
            ],
            "customers_without_profile": env["res.partner"].search_count(
                [("customer_rank", ">", 0)]
            )
            - len(profiles),
        }

    # --------------------------------------------------------------- dunning

    @http.route("/p03/ar/dunning", type="jsonrpc", auth="user", readonly=True)
    def ar_dunning(self, **kw):
        _require_internal(request.env)
        env = request.env
        # The worklist is the ACTIVE ladder: a dunning row whose invoice is
        # settled/credited is history (the effectiveness report keeps it),
        # not something a collector should chase with a ৳0 balance.
        rows = env["fix.dunning"].search(
            [("invoice_id.state", "=", "issued")], order="create_date desc", limit=200
        )
        return {
            "rows": [
                {
                    "id": r.id,
                    "invoice": r.invoice_id.name or "AR/%s" % r.invoice_id.id,
                    "invoice_id": r.invoice_id.id,
                    "customer": r.invoice_id.customer_id.name,
                    "overdue": r.overdue_amount,
                    "days": r.days_overdue,
                    "bucket": r.bucket or "",
                    "step": r.step,
                    "step_date": str(r.step_date) if r.step_date else "",
                    "suppressed": r.suppressed,
                    "suppression": r.suppression_reason or "",
                }
                for r in rows
            ],
            "disputes": [
                {
                    "id": d.id,
                    "invoice": d.invoice_id.name or "",
                    "amount": d.amount_disputed,
                    "reason": d.reason,
                    "state": d.state,
                }
                for d in env["fix.ar.dispute"].search([], limit=100)
            ],
        }

    # ----------------------------------------------------------------- ageing

    @http.route("/p03/ar/aging", type="jsonrpc", auth="user", readonly=True)
    def ar_aging(self, **kw):
        _require_internal(request.env)
        env = request.env
        snapshots = env["fix.ar.aging.snapshot"].search([], order="as_of_date desc", limit=10)
        live_rows = aging_live_rows(env)
        return {
            "live": live_rows,
            "history": [
                {
                    "id": s.id,
                    "as_of": str(s.as_of_date),
                    "state": s.state,
                    "total": s.total_open,
                    "captured_at": str(s.captured_at) if s.captured_at else "",
                }
                for s in snapshots
            ],
        }

    @http.route("/p03/ar/aging/snapshot", type="jsonrpc", auth="user", readonly=True)
    def ar_aging_snapshot(self, snapshot_id=None, **kw):
        _require_internal(request.env)
        snap = request.env["fix.ar.aging.snapshot"].browse(int(snapshot_id))
        if not snap.exists():
            return {"snapshot": None, "rows": []}
        return {
            "snapshot": {"as_of": str(snap.as_of_date), "total": snap.total_open},
            "rows": [
                {
                    "customer": line.customer_id.name,
                    "current": line.current,
                    "d1_30": line.d1_30,
                    "d31_60": line.d31_60,
                    "d61_90": line.d61_90,
                    "d90_plus": line.d90_plus,
                }
                for line in snap.line_ids
            ],
        }

    # -------------------------------------------------------- leakage/links

    @http.route("/p03/ar/leakage", type="jsonrpc", auth="user", readonly=True)
    def ar_leakage(self, **kw):
        _require_internal(request.env)
        return compute_leakage(request.env)

    @http.route("/p03/ar/payment-links", type="jsonrpc", auth="user", readonly=True)
    def ar_payment_links(self, **kw):
        _require_internal(request.env)
        links = request.env["fix.ar.payment.link"].search([], limit=100)
        return {
            "rows": [
                {
                    "id": lk.id,
                    "invoice": lk.invoice_id.name or "",
                    "amount": lk.amount,
                    "token": lk.token[:12] + "…",
                    "state": lk.state,
                    "expires": str(lk.expires_at) if lk.expires_at else "",
                    "gateway": lk.gateway_note or "",
                }
                for lk in links
            ]
        }

    # ------------------------------------------------------------ statements

    @http.route("/p03/ar/statement", type="jsonrpc", auth="user", readonly=True)
    def ar_statement(self, customer_id=None, date_from=None, date_to=None, **kw):
        _require_internal(request.env)
        env = request.env
        if not customer_id:
            return {"statement": None}
        date_from = (
            datetime.date.fromisoformat(str(date_from)[:10])
            if date_from
            else datetime.date.today().replace(day=1)
        )
        date_to = (
            datetime.date.fromisoformat(str(date_to)[:10]) if date_to else datetime.date.today()
        )
        stmt = compute_customer_statement(env, int(customer_id), date_from, date_to)
        stmt["customer"] = env["res.partner"].browse(int(customer_id)).name
        return {"statement": stmt}

    @http.route("/p03/ar/customers", type="jsonrpc", auth="user", readonly=True)
    def ar_customers(self, **kw):
        _require_internal(request.env)
        env = request.env
        # customers that matter for AR: those with invoices/receipts/profiles
        invoiced = env["fix.ar.invoice"].search([]).mapped("customer_id")
        receipted = env["fix.ar.receipt"].search([]).mapped("customer_id")
        ranked = env["res.partner"].search([("customer_rank", ">", 0)], limit=50)
        # a customer whose whole balance was taken on from the legacy system
        # has no invoice or receipt yet: list them too (their statement opens
        # on the take-on balance)
        taken_on = env["res.partner"]
        if env["account.move.line"].has_access("read"):
            ids = set()
            for company in env.companies:
                ids |= {k for k, v in takeon_ar_opening(env, company).items() if k and v["lines"]}
            taken_on = env["res.partner"].browse(sorted(ids)).exists()
        seen, partners = set(), []
        for p in list(invoiced) + list(receipted) + list(ranked) + list(taken_on):
            if p.id not in seen:
                seen.add(p.id)
                partners.append({"id": p.id, "name": p.name})
        return {"rows": partners}

    # =====================================================================
    # WRITE PATHS — every one savepointed (a refusal leaves nothing behind)
    # =====================================================================

    @http.route("/p03/ar/invoice/create", type="jsonrpc", auth="user")
    def ar_invoice_create(
        self,
        customer_id=None,
        invoice_date=None,
        lines=None,
        reason=None,
        header=None,
        overall_discount=0.0,
        **kw,
    ):
        _require_internal(request.env)
        env = request.env
        header = header or {}
        try:
            with env.cr.savepoint():
                vals = {
                    "customer_id": int(customer_id),
                    "operating_unit_id": (
                        getattr(env.user, "default_operating_unit_id", False)
                        or env["operating.unit"].search(
                            [("company_id", "=", env.company.id)], limit=1
                        )
                    ).id,
                    "invoice_date": datetime.date.fromisoformat(str(invoice_date)[:10])
                    if invoice_date
                    else datetime.date.today(),
                }
                for key in EDITOR_HEADER:
                    value = header.get(key)
                    if isinstance(value, str):
                        value = value.strip()
                    if value:
                        vals[key] = value
                if header.get("customer_po_date"):
                    vals["customer_po_date"] = datetime.date.fromisoformat(
                        str(header["customer_po_date"])[:10]
                    )
                if header.get("payment_method_id"):
                    vals["payment_method_id"] = int(header["payment_method_id"])
                invoice = env["fix.ar.invoice"].create_manual_invoice(
                    vals,
                    [
                        _editor_line(line)
                        for line in (lines or [])
                        if not _editor_line_is_blank(line)
                    ],
                    reason_code=reason or "",
                    overall_discount=_float(overall_discount),
                )
                return {"success": True, "invoice_id": invoice.id, "state": invoice.state}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/invoice/issue", type="jsonrpc", auth="user")
    def ar_invoice_issue(self, invoice_id=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                invoice = request.env["fix.ar.invoice"].browse(int(invoice_id))
                invoice.action_issue()
                return {"success": True, "state": invoice.state, "name": invoice.name}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/invoice/cancel", type="jsonrpc", auth="user")
    def ar_invoice_cancel(self, invoice_id=None, reason=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                invoice = request.env["fix.ar.invoice"].browse(int(invoice_id))
                invoice.action_cancel(reason or "")
                return {"success": True, "state": invoice.state}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/invoice/writeoff", type="jsonrpc", auth="user")
    def ar_invoice_writeoff(self, invoice_id=None, reason=None, recovery_history=None, **kw):
        """The single prompt carries "reason | recovery history" (BRU-ARB-12);
        the M20 Write-offs screen has the two fields separately."""
        _require_internal(request.env)
        reason, recovery = _split_prompt(reason, 2)
        recovery_history = recovery_history or recovery
        try:
            with request.env.cr.savepoint():
                invoice = request.env["fix.ar.invoice"].browse(int(invoice_id))
                requests = invoice.action_write_off(
                    reason or "", recovery_history=recovery_history or ""
                )
                return {
                    "success": True,
                    "state": invoice.state,
                    "request": requests[:1].name,
                    "request_state": requests[:1].state,
                }
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/event/generate", type="jsonrpc", auth="user")
    def ar_event_generate(self, event_id=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                row = request.env["fix.billable.event"].browse(int(event_id))
                row.action_generate_invoice()
                return {
                    "success": True,
                    "state": row.state,
                    "invoice": row.invoice_id.name or "",
                    "error": (row.last_error or "")[:200],
                }
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/event/process-all", type="jsonrpc", auth="user")
    def ar_event_process_all(self, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                result = request.env["fix.billable.event"].action_process_all_due()
                return {"success": True, **result}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/receipt/create", type="jsonrpc", auth="user")
    def ar_receipt_create(
        self,
        customer_id=None,
        amount=None,
        method=None,
        reference=None,
        receipt_date=None,
        nid=None,
        branch_id=None,
        payment_method_id=None,
        **kw,
    ):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                vals = {
                    "customer_id": int(customer_id),
                    "amount": round(float(amount or 0.0), 2),
                    "reference": reference or "",
                    "nid_captured": nid or "",
                    "receipt_date": datetime.date.fromisoformat(str(receipt_date)[:10])
                    if receipt_date
                    else datetime.date.today(),
                }
                if branch_id:
                    vals["branch_id"] = int(branch_id)
                if payment_method_id:
                    # the payment method sets the tender; a tender sent with
                    # it must agree (the receipt refuses a mismatch)
                    vals["payment_method_id"] = int(payment_method_id)
                    if method:
                        vals["method"] = method
                else:
                    vals["method"] = method or "cash"
                receipt = env["fix.ar.receipt"].create(vals)
                return {"success": True, "receipt_id": receipt.id, "name": receipt.name}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/receipt/confirm", type="jsonrpc", auth="user")
    def ar_receipt_confirm(self, receipt_id=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                receipt = request.env["fix.ar.receipt"].browse(int(receipt_id))
                receipt.action_confirm()
                return {
                    "success": True,
                    "state": receipt.state,
                    "gl_posted": bool(receipt.posted_move_id),
                    "gl_note": receipt.gl_note or "",
                }
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/receipt/reverse", type="jsonrpc", auth="user")
    def ar_receipt_reverse(self, receipt_id=None, reason=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                receipt = request.env["fix.ar.receipt"].browse(int(receipt_id))
                receipt.action_reverse(reason or "")
                return {"success": True, "state": receipt.state}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/allocation/create", type="jsonrpc", auth="user")
    def ar_allocation_create(self, receipt_id=None, invoice_id=None, amount=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                allocation = request.env["fix.ar.allocation"].create(
                    {
                        "receipt_id": int(receipt_id),
                        "invoice_id": int(invoice_id),
                        "amount": round(float(amount or 0.0), 2),
                    }
                )
                invoice = allocation.invoice_id
                return {
                    "success": True,
                    "invoice_state": invoice.state,
                    "residual": invoice.amount_residual,
                }
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/credit-note/create", type="jsonrpc", auth="user")
    def ar_credit_note_create(self, invoice_id=None, amount=None, reason=None, **kw):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                invoice = env["fix.ar.invoice"].browse(int(invoice_id))
                note = env["fix.credit.note"].create(
                    {
                        "operating_unit_id": invoice.operating_unit_id.id,
                        "invoice_id": invoice.id,
                        "amount": round(float(amount or 0.0), 2),
                        "reason_code": reason or "goodwill",
                    }
                )
                note.action_submit()
                return {"success": True, "note_id": note.id, "state": note.state}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/credit-note/issue", type="jsonrpc", auth="user")
    def ar_credit_note_issue(self, note_id=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                note = request.env["fix.credit.note"].browse(int(note_id))
                # A08 S3 (M20-1/7): a credit note is approved by someone other
                # than its raiser, through its own approval (a second
                # Accountant within the band, the M63 inbox above it). Issuing
                # never approves on the caller's behalf.
                if note.state == "pending_approval":
                    return {
                        "success": False,
                        "error": "Credit note %s is awaiting approval by someone other than "
                        "its raiser; it can be issued once approved." % note.display_name,
                    }
                note.action_issue()
                return {
                    "success": True,
                    "state": note.state,
                    "invoice_state": note.invoice_id.state,
                    "residual": note.invoice_id.amount_residual,
                }
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/credit-profile/save", type="jsonrpc", auth="user")
    def ar_credit_profile_save(
        self,
        customer_id=None,
        credit_limit=None,
        terms_days=None,
        hold=None,
        hold_reason=None,
        **kw,
    ):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                profile = env["fix.credit.profile"].search(
                    [("customer_id", "=", int(customer_id)), ("company_id", "=", env.company.id)],
                    limit=1,
                )
                vals = {
                    "credit_limit": round(float(credit_limit or 0.0), 2),
                    "payment_terms_days": int(terms_days or 30),
                }
                if profile:
                    profile.write(vals)
                    if hold is not None and bool(hold) != profile.credit_hold:
                        # the model's own hold workflow (A08 M20): reason,
                        # who/when stamp and the chatter trail
                        profile.action_toggle_hold(reason=hold_reason or None)
                else:
                    vals.update(
                        {
                            "customer_id": int(customer_id),
                            "credit_hold": bool(hold),
                            "hold_reason": hold_reason or "",
                        }
                    )
                    profile = env["fix.credit.profile"].create(vals)
                return {"success": True, "id": profile.id}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/dunning/run", type="jsonrpc", auth="user")
    def ar_dunning_run(self, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                result = request.env["fix.dunning"].action_run_dunning()
                return {"success": True, **result}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/dunning/suppress", type="jsonrpc", auth="user")
    def ar_dunning_suppress(self, dunning_id=None, reason=None, until=None, note=None, **kw):
        """A code from the controlled list, never a default: the single prompt
        carries "code | until YYYY-MM-DD | note"; until and note are optional."""
        _require_internal(request.env)
        code, typed_until, typed_note = _split_prompt(reason, 3)
        code = (code or "").lower().replace(" ", "_").replace("-", "_")
        if code not in DUNNING_SUPPRESSIONS:
            return {
                "success": False,
                "error": "Start with a suppression code: %s, then optionally "
                "| until YYYY-MM-DD | note." % ", ".join(DUNNING_SUPPRESSIONS),
            }
        try:
            with request.env.cr.savepoint():
                row = request.env["fix.dunning"].browse(int(dunning_id))
                row.action_suppress(code, until=until or typed_until, note=note or typed_note)
                return {
                    "success": True,
                    "suppressed": row.suppressed,
                    "until": str(row.suppressed_until or ""),
                }
        except ValueError:
            return {"success": False, "error": "The until date is written YYYY-MM-DD."}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/dunning/lift", type="jsonrpc", auth="user")
    def ar_dunning_lift(self, dunning_id=None, note=None, **kw):
        """End a suppression early (logged)."""
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                row = request.env["fix.dunning"].browse(int(dunning_id))
                row.action_lift_suppression(note=note or "")
                return {"success": True, "suppressed": row.suppressed}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/dispute/create", type="jsonrpc", auth="user")
    def ar_dispute_create(self, invoice_id=None, amount=None, reason=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                dispute = request.env["fix.ar.dispute"].create(
                    {
                        "invoice_id": int(invoice_id),
                        "amount_disputed": round(float(amount or 0.0), 2),
                        "reason": reason or "",
                    }
                )
                return {"success": True, "dispute_id": dispute.id, "state": dispute.state}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/dispute/resolve", type="jsonrpc", auth="user")
    def ar_dispute_resolve(self, dispute_id=None, note=None, outcome_code=None, **kw):
        """BRU-ARB-17: a dispute closes with an outcome code and a note. The
        single prompt carries "code | note"; the route always sent no code, so
        the Resolve button could only fail."""
        _require_internal(request.env)
        if not outcome_code:
            first, rest = _split_prompt(note, 2)
            code = (first or "").lower().replace(" ", "_").replace("-", "_")
            if code in DISPUTE_OUTCOME_CODES:
                outcome_code, note = code, rest
            else:
                return {
                    "success": False,
                    "error": "Start with an outcome code: %s, then | the resolution note."
                    % ", ".join(DISPUTE_OUTCOME_CODES),
                }
        try:
            with request.env.cr.savepoint():
                dispute = request.env["fix.ar.dispute"].browse(int(dispute_id))
                dispute.action_resolve(note or "", outcome_code=outcome_code)
                return {
                    "success": True,
                    "state": dispute.state,
                    "outcome_code": dispute.outcome_code,
                }
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/aging/capture", type="jsonrpc", auth="user")
    def ar_aging_capture(self, as_of=None, **kw):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                snap = env["fix.ar.aging.snapshot"].create(
                    {
                        "as_of_date": datetime.date.fromisoformat(str(as_of)[:10])
                        if as_of
                        else datetime.date.today()
                    }
                )
                snap.action_capture()
                return {"success": True, "id": snap.id, "total": snap.total_open}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/payment-link/create", type="jsonrpc", auth="user")
    def ar_payment_link_create(self, invoice_id=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                link = request.env["fix.ar.payment.link"].create({"invoice_id": int(invoice_id)})
                return {"success": True, "token": link.token}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/consolidated/generate", type="jsonrpc", auth="user")
    def ar_consolidated_generate(
        self, customer_id=None, period_start=None, period_end=None, ref=None, **kw
    ):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                bill = env["fix.ar.consolidated.bill"].create(
                    {
                        "customer_id": int(customer_id),
                        "bill_ref": ref or "CB/%s" % datetime.date.today().strftime("%Y%m"),
                        "period_start": datetime.date.fromisoformat(str(period_start)[:10]),
                        "period_end": datetime.date.fromisoformat(str(period_end)[:10]),
                    }
                )
                bill.action_generate()
                return {
                    "success": True,
                    "id": bill.id,
                    "invoices": len(bill.invoice_ids),
                    "total": bill.total_payable,
                }
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/ar/consolidated/send", type="jsonrpc", auth="user")
    def ar_consolidated_send(self, bill_id=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                bill = request.env["fix.ar.consolidated.bill"].browse(int(bill_id))
                bill.action_send()
                return {"success": True, "state": bill.state}
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}
