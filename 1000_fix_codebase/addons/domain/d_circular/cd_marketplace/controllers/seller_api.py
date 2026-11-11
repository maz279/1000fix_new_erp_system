# P07 Marketplace Seller API — the W4 contract endpoints (PP5).
#
# Seller onboarding state (KYC), the open jobs board with the seller's
# quotes, quote submission, and the scorecard. Settlement statements are
# served by cd_settlement_ext (/seller/settlements) where the commission
# ledger lives — one surface per owning module (FL-03).
# Money is backend-computed BN-007 strings (AS-10).

import math
from decimal import ROUND_HALF_UP, Decimal

from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

# Jobs a seller may still quote on: an order stays biddable after its first
# quote ("quoted") until a quote is selected — competing quotes are the point.
QUOTABLE_STATES = ("open", "quoted")


def _fmt_bdt(amount):
    """BN-007 South Asian grouping (12,34,567.89) — the portal receives the
    string (AS-10). The amount is rounded half-up to paisa BEFORE it is
    split, so 999.999 carries into 1,000.00, and a negative amount keeps its
    sign in front of the grouping. Non-numeric and non-finite input is 0.00."""
    try:
        exact = Decimal(repr(float(amount)))
        cents = int(exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)
    except (TypeError, ValueError, ArithmeticError):  # None/"abc"; NaN; inf / out of range
        return "0.00"
    sign = "-" if cents < 0 else ""
    whole, paisa = divmod(abs(cents), 100)
    digits = str(whole)
    head, groups = digits[:-3], [digits[-3:]]
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    return f"{sign}{','.join(groups)}.{paisa:02d}"


def _to_int(value):
    """A request id parameter as an int, or None when it is not one."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _seller(kwargs):
    """The seller this request acts for. EA-05: the seller surface is
    scoped by seller_id; portal-user binding rides the session partner.
    Anti-IDOR: Portal users cannot override their own partner_id."""
    user = request.env.user
    seller_id = kwargs.get("seller_id")
    if seller_id:
        seller_id = _to_int(seller_id)
        if seller_id is None:
            return None
        seller = request.env["fix.marketplace.seller"].browse(seller_id)
        if not seller.exists():
            return None
        # Defense-in-depth: portal users MUST match their session partner
        if not user.has_group("base.group_user") and seller.partner_id.id != user.partner_id.id:
            return None
        return seller
    partner = request.env.user.partner_id
    return (
        request.env["fix.marketplace.seller"].search([("partner_id", "=", partner.id)], limit=1)
        or None
    )


class SellerApiController(http.Controller):
    """The P07 marketplace seller API (W4 contract)."""

    @http.route("/seller/dashboard", type="jsonrpc", auth="user", readonly=True)
    def dashboard(self, **kwargs):
        """Onboarding state + headline numbers (the seller's home)."""
        seller = _seller(kwargs)
        if not seller:
            return _error(
                "no_seller",
                "No seller profile for this account — complete " "onboarding first (M12 KYC)",
            )
        return {
            "seller": {
                "id": seller.id,
                "name": seller.name,
                "kyc_status": seller.kyc_status,
                "kyc_ref": seller.kyc_doc_z4_ref or "",
                "rating": seller.rating,
                "total_jobs": seller.total_jobs,
            }
        }

    @http.route("/seller/orders", type="jsonrpc", auth="user", readonly=True)
    def orders(self, **kwargs):
        """The open jobs board + this seller's quotes on each (M12).
        A quote already submitted is VISIBLE as `my_quote` — the seller
        sees their own standing, not the other quotes (EA-05). Jobs that
        already received a quote stay on the board until one is selected."""
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        board = request.env["fix.marketplace.order"].search(
            [("state", "in", QUOTABLE_STATES)], limit=100, order="id desc"
        )
        result = []
        for o in board:
            mine = o.quote_ids.filtered(lambda q: q.seller_id.id == seller.id)
            result.append(
                {
                    "id": o.id,
                    "name": o.name,
                    "description": o.description,
                    "budget_bdt": _fmt_bdt(o.budget),
                    "state": o.state,
                    "my_quote": (
                        {
                            "id": mine[0].id,
                            "price_bdt": _fmt_bdt(mine[0].quoted_price),
                            "eta_days": mine[0].eta_days,
                            "state": mine[0].state,
                        }
                        if mine
                        else None
                    ),
                }
            )
        return {"orders": result, "total": len(result)}

    @http.route("/seller/quotes", type="jsonrpc", auth="user", readonly=False)
    def quotes(self, **kwargs):
        """Combined endpoint: submit when `order_id` is present, otherwise
        list the seller's quotes. Submission validates server-side (AS-09)."""
        if kwargs.get("order_id"):
            return self._submit_quote(**kwargs)
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        quotes = request.env["fix.seller.quote"].search(
            [("seller_id", "=", seller.id)], limit=100, order="id desc"
        )
        result = [
            {
                "id": q.id,
                "order_name": q.marketplace_order_id.name,
                "price_bdt": _fmt_bdt(q.quoted_price),
                "eta_days": q.eta_days,
                "state": q.state,
            }
            for q in quotes
        ]
        return {"quotes": result, "total": len(result)}

    def _submit_quote(self, **kwargs):
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        if seller.kyc_status != "verified":
            # G-series: the gate is stated, not warned about in the portal
            return _error("kyc_not_verified", "Only a KYC-verified seller can quote (M12)")
        try:
            quoted_price = float(kwargs.get("quoted_price"))
        except (TypeError, ValueError):
            quoted_price = math.nan
        if not (math.isfinite(quoted_price) and quoted_price > 0):
            return _error("invalid_price", "quoted_price must be a positive amount")
        eta_days = _to_int(kwargs.get("eta_days", 3))
        if eta_days is None:
            return _error("invalid_eta", "eta_days must be a whole number of days")
        order_id = _to_int(kwargs.get("order_id"))
        order = request.env["fix.marketplace.order"].browse(order_id or [])
        if not order.exists() or order.state not in QUOTABLE_STATES:
            return _error("order_not_open", "Quotes are only accepted on open jobs")
        try:
            quote = request.env["fix.seller.quote"].create(
                {
                    "marketplace_order_id": order.id,
                    "seller_id": seller.id,
                    "quoted_price": quoted_price,
                    "eta_days": eta_days,
                    "notes": kwargs.get("notes", ""),
                }
            )
        except (UserError, ValidationError) as exc:
            return _error("quote_rejected", str(exc))
        return {"quote": {"id": quote.id, "state": quote.state}}

    @http.route("/seller/scorecard", type="jsonrpc", auth="user", readonly=True)
    def scorecard(self, **kwargs):
        """The seller's scorecard history (M12 performance)."""
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        scores = request.env["fix.seller.score"].search(
            [("seller_id", "=", seller.id)], limit=24, order="period desc"
        )
        result = [
            {
                "period": s.period,
                "acceptance_rate": s.acceptance_rate,
                "on_time_rate": s.on_time_rate,
                "review_rating": s.review_rating,
                "dispute_rate": s.dispute_rate,
                "composite": s.composite,
            }
            for s in scores
        ]
        return {"scorecard": result, "total": len(result)}

    @http.route("/seller/disputes", type="jsonrpc", auth="user", readonly=True)
    def disputes(self, **kwargs):
        """The seller's disputes history and active SLA timers (M12 / BRU-BIL-03)."""
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        disputes = request.env["fix.marketplace.dispute"].search(
            [("seller_id", "=", seller.id)], limit=50, order="id desc"
        )
        result = [
            {
                "id": d.name,
                "order_ref": d.order_id.name if d.order_id else "",
                "dispute_reason": d.dispute_reason,
                "disputed_amount_bdt": _fmt_bdt(d.disputed_amount),
                "state": d.state,
                "sla_breached": d.sla_breached,
                "description": d.description,
            }
            for d in disputes
        ]
        return {"disputes": result, "total": len(result)}

    @http.route("/seller/stock", type="jsonrpc", auth="user", readonly=False)
    def stock(self, **kwargs):
        """The seller's stock positions (M12-stock). With `listing_id` and
        `sku` it reports one position (on hand, reserved) first; the server
        stamps who reported it and when. Only the seller's own listings take
        stock (the P07 record rule decides, not this endpoint)."""
        seller = _seller(kwargs)
        if not seller:
            return _error("no_seller", "No seller profile for this account")
        Stock = request.env["fix.seller.stock"]
        if kwargs.get("listing_id") and kwargs.get("sku"):
            listing_id = _to_int(kwargs.get("listing_id"))
            listing = request.env["fix.marketplace.listing"].sudo().browse(listing_id or [])
            if not listing.exists() or listing.seller_id != seller:
                return _error("not_your_listing", "Stock is reported only on your own listings")
            try:
                on_hand = float(kwargs.get("qty_on_hand", 0))
                reserved = float(kwargs.get("qty_reserved", 0))
            except (TypeError, ValueError):
                return _error("invalid_quantity", "Quantities must be numbers")
            if not (math.isfinite(on_hand) and math.isfinite(reserved)):
                return _error("invalid_quantity", "Quantities must be numbers")
            try:
                Stock.report_position(listing.id, kwargs.get("sku"), on_hand, reserved)
            except (UserError, ValidationError) as exc:
                return _error("stock_rejected", str(exc))
        positions = Stock.search([("seller_id", "=", seller.id)], limit=500)
        result = [
            {
                "id": p.id,
                "listing": p.listing_id.sudo().name,
                "sku": p.sku,
                "qty_on_hand": p.qty_on_hand,
                "qty_reserved": p.qty_reserved,
                "qty_available": p.qty_available,
                "last_updated": str(p.last_updated or ""),
                "source": p.source,
            }
            for p in positions
        ]
        return {"stock": result, "total": len(result)}
