# P07 Marketplace Seller API — the W4 contract endpoints (PP5).
#
# Seller onboarding state (KYC), the open jobs board with the seller's
# quotes, quote submission, and the scorecard. Settlement statements are
# served by cd_settlement_ext (/seller/settlements) where the commission
# ledger lives — one surface per owning module (FL-03).
# Money is backend-computed BN-007 strings (AS-10).
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


def _seller(kwargs):
    """The seller this request acts for. EA-05: the seller surface is
    scoped by seller_id; portal-user binding rides the session partner."""
    seller_id = kwargs.get("seller_id")
    if seller_id:
        seller = request.env["fix.marketplace.seller"].browse(
            int(seller_id))
        return seller if seller.exists() else None
    partner = request.env.user.partner_id
    return request.env["fix.marketplace.seller"].search(
        [("partner_id", "=", partner.id)], limit=1) or None


class SellerApiController(http.Controller):
    """The P07 marketplace seller API (W4 contract)."""

    @http.route("/seller/dashboard", type="json", auth="user", readonly=True)
    def dashboard(self, **kwargs):
        """Onboarding state + headline numbers (the seller's home)."""
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller",
                          "No seller profile for this account — complete "
                          "onboarding first (M12 KYC)")
        return {"seller": {
            "id": seller.id,
            "name": seller.name,
            "kyc_status": seller.kyc_status,
            "kyc_ref": seller.kyc_ref or "",
            "rating": seller.rating,
            "total_jobs": seller.total_jobs,
        }}

    @http.route("/seller/orders", type="json", auth="user", readonly=True)
    def orders(self, **kwargs):
        """The open jobs board + this seller's quotes on each (M12).
        A quote already submitted is VISIBLE as `my_quote` — the seller
        sees their own standing, not the other quotes (EA-05)."""
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        board = request.env["fix.marketplace.order"].search(
            [("state", "=", "open")], limit=100, order="id desc")
        result = []
        for o in board:
            mine = o.quote_ids.filtered(
                lambda q: q.seller_id.id == seller.id)
            result.append({
                "id": o.id,
                "name": o.name,
                "description": o.description,
                "budget_bdt": _fmt_bdt(o.budget),
                "state": o.state,
                "my_quote": ({
                    "id": mine[0].id,
                    "price_bdt": _fmt_bdt(mine[0].quoted_price),
                    "eta_days": mine[0].eta_days,
                    "state": mine[0].state,
                } if mine else None),
            })
        return {"orders": result, "total": len(result)}

    @http.route("/seller/quotes", type="json", auth="user", readonly=False)
    def quotes(self, **kwargs):
        """Combined endpoint: submit when `order_id` is present, otherwise
        list the seller's quotes. Submission validates server-side (AS-09)."""
        if kwargs.get("order_id"):
            return self._submit_quote(**kwargs)
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        quotes = request.env["fix.seller.quote"].search(
            [("seller_id", "=", seller.id)], limit=100, order="id desc")
        result = [{
            "id": q.id,
            "order_name": q.marketplace_order_id.name,
            "price_bdt": _fmt_bdt(q.quoted_price),
            "eta_days": q.eta_days,
            "state": q.state,
        } for q in quotes]
        return {"quotes": result, "total": len(result)}

    def _submit_quote(self, **kwargs):
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        if seller.kyc_status != "verified":
            # G-series: the gate is stated, not warned about in the portal
            return _error("kyc_not_verified",
                          "Only a KYC-verified seller can quote (M12)")
        quoted_price = kwargs.get("quoted_price")
        if quoted_price is None or float(quoted_price) <= 0:
            return _error("invalid_price",
                          "quoted_price must be a positive amount")
        order = request.env["fix.marketplace.order"].browse(
            int(kwargs.get("order_id")))
        if not order.exists() or order.state != "open":
            return _error("order_not_open",
                          "Quotes are only accepted on open jobs")
        try:
            quote = request.env["fix.seller.quote"].create({
                "marketplace_order_id": order.id,
                "seller_id": seller.id,
                "quoted_price": float(quoted_price),
                "eta_days": int(kwargs.get("eta_days", 3)),
                "notes": kwargs.get("notes", ""),
            })
        except (UserError, ValidationError) as exc:
            return _error("quote_rejected", str(exc))
        return {"quote": {"id": quote.id, "state": quote.state}}

    @http.route("/seller/scorecard", type="json", auth="user",
                readonly=True)
    def scorecard(self, **kwargs):
        """The seller's scorecard history (M12 performance)."""
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        scores = request.env["fix.seller.score"].search(
            [("seller_id", "=", seller.id)], limit=24, order="period desc")
        result = [{
            "period": s.period,
            "acceptance_rate": s.acceptance_rate,
            "on_time_rate": s.on_time_rate,
            "review_rating": s.review_rating,
            "dispute_rate": s.dispute_rate,
            "composite": s.composite,
        } for s in scores]
        return {"scorecard": result, "total": len(result)}
