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
    compute_customer_statement,
    compute_leakage,
)
from odoo.exceptions import UserError
from odoo.http import request

from .p03_service_order_api import _require_internal, _user_error


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
        "due_date": str(inv.invoice_date + timedelta(days=inv._payment_terms_days()))
        if inv.invoice_date
        else "",
        "terms_days": inv._payment_terms_days(),
        "days_past_due": max(
            (datetime.date.today() - inv.invoice_date).days - inv._payment_terms_days(), 0
        )
        if inv.invoice_date
        else 0,
    }


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
            "lines": [
                {
                    "description": line.description or "",
                    "taxable": line.taxable_amount,
                    "vat": line.vat_amount,
                    "total": line.line_total,
                }
                for line in inv.line_ids
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
        rows = env["fix.dunning"].search([], order="create_date desc", limit=200)
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
        live_rows = [
            dict({"customer": name}, **{k: round(v, 2) for k, v in amounts.items()})
            for name, amounts in sorted(buckets.items())
        ]
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
        seen, partners = set(), []
        for p in list(invoiced) + list(receipted) + list(ranked):
            if p.id not in seen:
                seen.add(p.id)
                partners.append({"id": p.id, "name": p.name})
        return {"rows": partners}

    # =====================================================================
    # WRITE PATHS — every one savepointed (a refusal leaves nothing behind)
    # =====================================================================

    @http.route("/p03/ar/invoice/create", type="jsonrpc", auth="user")
    def ar_invoice_create(self, customer_id=None, invoice_date=None, lines=None, reason=None, **kw):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                invoice = env["fix.ar.invoice"].create_manual_invoice(
                    {
                        "customer_id": int(customer_id),
                        "operating_unit_id": env["operating.unit"]
                        .search([("company_id", "=", env.company.id)], limit=1)
                        .id,
                        "invoice_date": datetime.date.fromisoformat(str(invoice_date)[:10])
                        if invoice_date
                        else datetime.date.today(),
                    },
                    [
                        {
                            "description": line.get("description") or "Service",
                            "taxable_amount": round(float(line.get("taxable") or 0.0), 2),
                            "vat_amount": round(float(line.get("vat") or 0.0), 2),
                            "line_total": round(
                                float(line.get("taxable") or 0.0) + float(line.get("vat") or 0.0), 2
                            ),
                        }
                        for line in (lines or [])
                    ],
                    reason_code=reason or "",
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
    def ar_invoice_writeoff(self, invoice_id=None, reason=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                invoice = request.env["fix.ar.invoice"].browse(int(invoice_id))
                invoice.action_write_off(reason or "")
                return {"success": True, "state": invoice.state}
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
        **kw,
    ):
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                receipt = env["fix.ar.receipt"].create(
                    {
                        "customer_id": int(customer_id),
                        "amount": round(float(amount or 0.0), 2),
                        "method": method or "cash",
                        "reference": reference or "",
                        "nid_captured": nid or "",
                        "receipt_date": datetime.date.fromisoformat(str(receipt_date)[:10])
                        if receipt_date
                        else datetime.date.today(),
                    }
                )
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
                if note.state == "pending_approval":
                    note.action_approve()  # only a manager reaches here with ACL rights
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
    def ar_dunning_suppress(self, dunning_id=None, reason=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                row = request.env["fix.dunning"].browse(int(dunning_id))
                row.action_suppress(reason or "strategic")
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
    def ar_dispute_resolve(self, dispute_id=None, note=None, **kw):
        _require_internal(request.env)
        try:
            with request.env.cr.savepoint():
                dispute = request.env["fix.ar.dispute"].browse(int(dispute_id))
                dispute.action_resolve(note or "")
                return {"success": True, "state": dispute.state}
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
