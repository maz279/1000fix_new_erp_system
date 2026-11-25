# P05 vendor portal read API — the supplier's own standing and desk view.
#
# The W4 contract in vendor_api.py stays the transactional surface (POs,
# invoices). This controller adds what the portal's dashboard and profile
# need and the contract does not expose: the supplier master standing, its
# compliance documents with expiry, the latest approved qualification score
# and a summary of open POs / invoices / blockers.
#
# Scoping is the same rule as vendor_api: the session's COMMERCIAL partner
# owns the supplier row; nothing is taken from the browser. Reads use sudo
# only after that scoping because the vendor-portal group has no ACL on the
# supplier master (it is an internal master record).

from datetime import timedelta

from odoo import fields, http
from odoo.http import request

from .vendor_api import _fmt_bdt, _is_staff, _vendor_partner


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _dt(value):
    return str(value or "")


def _vendor_supplier():
    """The supplier row for the signed-in vendor, or an empty recordset.

    Staff sessions have no vendor partner and get the structured refusal;
    this is a vendor portal, not the procurement back office.
    """
    if _is_staff():
        return None
    partner = _vendor_partner()
    if not partner:
        return None
    Supplier = request.env(su=True)["fix.supplier"]
    return Supplier.search(
        [
            "|",
            ("partner_id", "=", partner.id),
            ("partner_id", "child_of", partner.id),
        ],
        limit=1,
    )


def _mask_account(account):
    number = (account.acc_number or "").replace(" ", "")
    if not number:
        return ""
    return "•••• " + number[-4:] if len(number) > 4 else "••••"


class VendorPortalApiController(http.Controller):
    """Session-authenticated supplier standing and desk routes (:3007)."""

    @http.route("/vendor/portal/profile", type="jsonrpc", auth="user", readonly=True)
    def portal_profile(self, **kwargs):
        supplier = _vendor_supplier()
        if supplier is None:
            return _error(
                "no_supplier_profile",
                "No supplier profile is linked to this account — onboarding is handled by 1000 FiX procurement.",
            )
        if not supplier:
            return _error(
                "no_supplier_profile",
                "No supplier profile is linked to this account — onboarding is handled by 1000 FiX procurement.",
            )
        latest = request.env(su=True)["fix.supplier.qualification"].search(
            [("supplier_id", "=", supplier.id), ("state", "=", "approved")],
            limit=1,
            order="approved_on desc, id desc",
        )
        bank = supplier.bank_account_id
        return {
            "supplier": {
                "id": supplier.id,
                "name": supplier.name,
                "code": supplier.supplier_code or "",
                "status": supplier.status,
                "segment": supplier.segment,
                "category": supplier.category or "",
                "residency": supplier.residency,
                "classification": supplier.classification or "",
                "risk_tier": supplier.risk_tier or "",
                "onboarded_on": _dt(supplier.onboarded_on),
                "payment_block": bool(supplier.payment_block),
                "buyer": supplier.buyer_id.name or "",
                "bank": {
                    "masked": _mask_account(bank) if bank else "",
                    "bank": bank.bank_id.name if bank else "",
                },
                "contacts": [
                    {
                        "name": c.name,
                        "role": c.role,
                        "phone": c.phone or "",
                        "email": c.email or "",
                    }
                    for c in supplier.contact_ids.filtered("active")
                ],
                "latest_score": {
                    "score": latest.score,
                    "approved_on": _dt(latest.approved_on),
                    "stage": latest.stage,
                }
                if latest
                else None,
            }
        }

    @http.route("/vendor/portal/documents", type="jsonrpc", auth="user", readonly=True)
    def portal_documents(self, **kwargs):
        supplier = _vendor_supplier()
        if not supplier:
            return _error("no_supplier_profile", "No supplier profile is linked to this account")
        today = fields.Date.context_today(request.env.user)
        docs = request.env(su=True)["fix.supplier.document"].search(
            [("supplier_id", "=", supplier.id)], order="valid_to asc, id desc"
        )
        rows = []
        for doc in docs:
            days = (doc.valid_to - today).days if doc.valid_to else None
            rows.append(
                {
                    "id": doc.id,
                    "name": doc.name,
                    "doc_type": doc.doc_type,
                    "number": doc.number or "",
                    "valid_from": _dt(doc.valid_from),
                    "valid_to": _dt(doc.valid_to),
                    "state": doc.state,
                    "is_valid": bool(doc.is_valid),
                    "days_to_expiry": days,
                }
            )
        return {"documents": rows, "total": len(rows)}

    @http.route("/vendor/portal/summary", type="jsonrpc", auth="user", readonly=True)
    def portal_summary(self, **kwargs):
        supplier = _vendor_supplier()
        if not supplier:
            return _error("no_supplier_profile", "No supplier profile is linked to this account")
        env = request.env(su=True)
        partner = _vendor_partner()
        PO = env["fix.purchase.order"]
        Invoice = env["fix.vendor.invoice"]

        pos = PO.search([("vendor_id", "child_of", partner.id), ("state", "!=", "draft")])
        open_states = ("sent", "acknowledged", "partially_received")
        open_pos = pos.filtered(lambda p: p.state in open_states)
        awaiting = pos.filtered(lambda p: p.state == "sent")
        now = fields.Datetime.now()
        oldest = 0
        for po in open_pos:
            if po.date_order:
                oldest = max(oldest, int((now - po.date_order).total_seconds() // 86400))
        open_value = sum(p.amount_total for p in open_pos)

        invoices = Invoice.search([("vendor_id", "child_of", partner.id)])
        by_match, by_approval, by_payment = {}, {}, {}
        blocked = 0
        submitted = 0.0
        for inv in invoices:
            by_match[inv.match_state] = by_match.get(inv.match_state, 0) + 1
            by_approval[inv.approval_state] = by_approval.get(inv.approval_state, 0) + 1
            by_payment[inv.payment_state] = by_payment.get(inv.payment_state, 0) + 1
            if inv.match_state == "blocked":
                blocked += 1
            submitted += inv.total_payable_bdt or 0.0

        docs = env["fix.supplier.document"].search([("supplier_id", "=", supplier.id)])
        today = fields.Date.context_today(request.env.user)
        soon = today + timedelta(days=30)
        expiring = docs.filtered(
            lambda d: d.valid_to and today <= d.valid_to <= soon and d.state != "expired"
        )
        expired = docs.filtered(lambda d: d.valid_to and d.valid_to < today)
        latest = env["fix.supplier.qualification"].search(
            [("supplier_id", "=", supplier.id), ("state", "=", "approved")],
            limit=1,
            order="approved_on desc, id desc",
        )
        return {
            "supplier": {
                "id": supplier.id,
                "name": supplier.name,
                "status": supplier.status,
                "payment_block": bool(supplier.payment_block),
            },
            "purchase_orders": {
                "open": len(open_pos),
                "awaiting_ack": len(awaiting),
                "oldest_open_days": oldest,
                "open_value_bdt": _fmt_bdt(open_value),
                "by_state": {
                    state: len(pos.filtered(lambda p, s=state: p.state == s))
                    for state in (
                        "sent",
                        "acknowledged",
                        "partially_received",
                        "received",
                        "closed",
                    )
                },
            },
            "invoices": {
                "total": len(invoices),
                "blocked": blocked,
                "submitted_payable_bdt": _fmt_bdt(submitted),
                "by_match": by_match,
                "by_approval": by_approval,
                "by_payment": by_payment,
            },
            "compliance": {
                "documents": len(docs),
                "expiring_30_days": len(expiring),
                "expired": len(expired),
            },
            "score": latest.score if latest else None,
            "generated_at": str(now),
        }
