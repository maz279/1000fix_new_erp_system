# P10 / M38: Storefront API Controller (CD-M38-02 / R08-M03).
# Serves M37 catalogue browsing, cart management, checkout with R04 payment rails,
# order tracking, and reverse logistics returns.
#
# Access model (R01 re-audit 2026-10-22):
# - catalogue: public.
# - cart / checkout: public, but a cart is never addressable by a caller-chosen id.
#   An authenticated customer gets their own partner's open cart; a guest gets ONLY
#   the cart whose id is stored in their own ``request.session``.
# - order tracking: the order owner (commercial partner match), internal staff with
#   read access, or the guest session that placed the order. Anything else is
#   answered exactly like a non-existent order.
# - returns: ``auth="user"`` + order ownership; the refund amount is computed
#   (capped) by the server.
#
# - payment callback (A04 audit M38-2): the gateway's server-to-server notice.
#   Public, but honoured only with a valid HMAC-SHA256 signature made with the
#   rail's shared secret (ir.config_parameter ``cd_storefront.gateway_secret.<rail>``).
#   With no secret configured the callback is refused: a payment is never
#   confirmed on an unsigned or unverifiable message.
import hashlib
import hmac
import json
import logging
import math

from odoo import SUPERUSER_ID, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

from libs.py.fix_api_edge import api_edge

_logger = logging.getLogger(__name__)

GATEWAY_SECRET_PARAM = "cd_storefront.gateway_secret.%s"  # noqa: S105 - a parameter key, not a secret
# Rocket and Upay since 13 Nov 2026 (quote-to-cash): each has its own secret
GATEWAY_RAILS = ("bkash", "nagad", "rocket", "upay", "sslcommerz")


def gateway_signature(secret, order_name, trx_id, amount):
    """The signature a gateway callback must carry: HMAC-SHA256 (hex) of
    ``<order>|<trx_id>|<amount with 2 decimals>`` under the rail's secret."""
    try:
        amount_txt = "%.2f" % float(amount)
    except (TypeError, ValueError):
        amount_txt = str(amount)
    message = "%s|%s|%s" % (order_name, trx_id, amount_txt)
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


SESSION_CART_KEY = "storefront_cart_id"
SESSION_ORDERS_KEY = "storefront_order_ids"
GUEST_PARTNER_NAME = "Guest Storefront Customer"
RETURNABLE_STATES = ("paid", "dispatched", "delivered")
CATALOGUE_MAX_LIMIT = 200


def _su_env():
    """Return superuser environment to avoid portal user ACL AccessErrors on models."""
    return request.env(user=SUPERUSER_ID, su=True)


def _fmt_bdt(amount):
    """Format a monetary value as a BN-007-style South Asian-grouped string (AS-10)."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    is_neg = n < 0
    formatted_float = f"{abs(n):.2f}"
    whole_str, frac_str = formatted_float.split(".")
    if len(whole_str) > 3:
        last3 = whole_str[-3:]
        rest = whole_str[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        groups.insert(0, rest)  # 1-2 leading digits: len(whole_str) > 3 leaves rest non-empty
        grouped = ",".join(groups) + "," + last3
    else:
        grouped = whole_str
    sign = "-" if is_neg else ""
    return f"{sign}{grouped}.{frac_str}"


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _selection_keys(env, model, field):
    """The allowed values of a static selection field, as a list: membership is
    tested by equality, so an unhashable JSON value is "unknown", not a TypeError."""
    return [key for key, _label in env[model]._fields[field].selection]


def _caller_user():
    """The authenticated (non-public) user of this request, or ``None`` for a guest."""
    user = request.env.user
    if not user or user._is_public():
        return None
    return user


def _guest_partner(env):
    """The shared partner that owns guest carts (guest carts are session-bound)."""
    partner = env["res.partner"].search([("name", "=", GUEST_PARTNER_NAME)], limit=1)
    if not partner:
        partner = env["res.partner"].create(
            {
                "name": GUEST_PARTNER_NAME,
                "email": "guest@storefront.1000fix.com",
            }
        )
    return partner


def normalise_bd_mobile(value):
    """'01XXXXXXXXX' for a Bangladesh mobile number given in any common form
    (+880 / 880 prefix, spaces, dashes), else ''."""
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if digits.startswith("880"):
        digits = digits[2:]
    if len(digits) == 11 and digits.startswith("01") and digits[2] in "3456789":
        return digits
    return ""


def guest_customer_for_phone(env, phone):
    """A04 ERP audit M38-F12: the customer of a guest order is the partner of
    its mobile number (one per number, found again on the next order), never
    one partner shared by every guest. Empty when the number is not a
    Bangladesh mobile number."""
    mobile = normalise_bd_mobile(phone)
    if not mobile:
        return env["res.partner"]
    ref = "sf-guest:%s" % mobile
    Partner = env["res.partner"].sudo()
    partner = Partner.search([("ref", "=", ref)], limit=1)
    if not partner:
        partner = Partner.create(
            {"name": "Storefront customer %s" % mobile, "phone": mobile, "ref": ref}
        )
    return partner


def _scoped_customer(kwargs):
    """Resolve customer partner ID for current request.
    Anti-IDOR: only internal staff may act for another customer (``customer_id`` /
    ``partner_id``); portal users are bound to their own partner, guests to the
    shared guest partner (their cart itself is bound to the session)."""
    user = _caller_user()
    if user is None:
        return _guest_partner(_su_env()).id
    if user._is_internal():
        partner_id = _to_int(kwargs.get("customer_id") or kwargs.get("partner_id"))
        if partner_id:
            return partner_id
    return user.partner_id.id


def _caller_cart(env, kwargs):
    """The caller's open cart, or an empty recordset.

    Guests only ever reach the cart id stored in their own ``request.session``.
    """
    cart_model = env["fix.storefront.cart"]
    customer_id = _scoped_customer(kwargs)
    if _caller_user() is None:
        cart = cart_model.browse(_to_int(request.session.get(SESSION_CART_KEY)) or 0).exists()
        if cart and cart.state == "open" and cart.customer_id.id == customer_id:
            return cart
        return cart_model
    return cart_model.search(
        [("customer_id", "=", customer_id), ("state", "=", "open")], limit=1, order="id desc"
    )


def _owns_order(order, user):
    """True when ``order`` belongs to ``user``'s commercial entity."""
    return order.customer_id.commercial_partner_id.id == user.partner_id.commercial_partner_id.id


def _can_view_order(order):
    user = _caller_user()
    if user is None:
        return order.id in (request.session.get(SESSION_ORDERS_KEY) or [])
    if _owns_order(order, user):
        return True
    return user._is_internal() and order.with_user(user).has_access("read")


def _error(code, message):
    return {"error": {"code": code, "message": message}}


def _cart_payload(cart):
    lines = []
    for line in cart.line_ids:
        lines.append(
            {
                "id": line.id,
                "product_id": line.product_id.id,
                "product_name": line.product_id.name,
                "quantity": line.quantity,
                "unit_price": float(line.unit_price),
                "unit_price_bdt": _fmt_bdt(line.unit_price),
                "subtotal": float(line.subtotal),
                "subtotal_bdt": _fmt_bdt(line.subtotal),
            }
        )
    return {
        "cart_id": cart.id or None,
        "cart_name": cart.name or None,
        "state": cart.state or "open",
        "total": float(cart.total or 0.0),
        "total_bdt": _fmt_bdt(cart.total or 0.0),
        "items_count": len(lines),
        "lines": lines,
    }


class StorefrontApiController(http.Controller):
    """M38 Storefront Customer API endpoints."""

    @http.route("/storefront/catalogue", type="jsonrpc", auth="public", readonly=True)
    @api_edge("/storefront/catalogue")
    def catalogue(self, category=None, search=None, limit=50, **kwargs):
        """Browse M37 catalogue products (parts, accessories, refurbished devices)."""
        env = _su_env()
        domain = [("sale_ok", "=", True)]
        if search:
            domain.append(("name", "ilike", search))

        limit = min(max(_to_int(limit) or 50, 1), CATALOGUE_MAX_LIMIT)
        # A04 ERP audit M38-F1: only items with a released M11 storefront
        # price are listed, at that price (VAT included); list_price is never
        # shown. A page is scanned in batches until it is full.
        Line = env["fix.storefront.cart.line"]
        partner = env["res.partner"].browse(_scoped_customer(kwargs))
        items, offset, batch = [], 0, max(limit * 2, 50)
        while len(items) < limit:
            products = env["product.template"].search(domain, limit=batch, offset=offset)
            if not products:
                break
            offset += batch
            for p in products:
                try:
                    info = Line._sf_m11_price(p, partner=partner)
                except UserError:
                    continue  # no released price: not sold online
                items.append(
                    {
                        "id": p.id,
                        "name": p.name,
                        "code": p.default_code or "",
                        "type": p.type,
                        "price": float(info["incl"]),
                        "price_bdt": _fmt_bdt(info["incl"]),
                        "price_excl_vat": float(info["excl"]),
                        "category": p.categ_id.name if p.categ_id else "General",
                    }
                )
                if len(items) >= limit:
                    break
        return {"products": items, "count": len(items)}

    @http.route("/storefront/cart", type="jsonrpc", auth="public")
    @api_edge("/storefront/cart")
    def get_or_update_cart(self, product_id=None, quantity=1, **kwargs):
        """Get the caller's active cart or add/update item lines.

        The cart is resolved from the caller (partner, or the guest's session) —
        a cart id is never accepted from the request."""
        env = _su_env()
        cart = _caller_cart(env, kwargs)

        if product_id:
            product = env["product.template"].browse(_to_int(product_id) or 0).exists()
            if not product or not product.sale_ok:
                return _error("PRODUCT_NOT_FOUND", "Product not found")
            try:
                qty = float(quantity or 1)
            except (TypeError, ValueError):
                qty = float("nan")
            if not math.isfinite(qty) or qty <= 0:
                return _error("INVALID_QUANTITY", "quantity must be a positive number")
            if abs(qty - round(qty)) > 1e-9:
                # A04 ERP audit M38-F4: whole units only
                return _error("INVALID_QUANTITY", "quantity must be a whole number of units")

            if not cart:
                cart = env["fix.storefront.cart"].create(
                    {
                        "customer_id": _scoped_customer(kwargs),
                        "state": "open",
                    }
                )
                if _caller_user() is None:
                    request.session[SESSION_CART_KEY] = cart.id
            # check if line already in cart
            existing_line = cart.line_ids.filtered(lambda line: line.product_id.id == product.id)
            try:
                with env.cr.savepoint():
                    if existing_line:
                        existing_line.write({"quantity": existing_line.quantity + qty})
                    else:
                        # A04 audit: the M37 lifecycle / M11 price and floor
                        # check; the price is the server's (M38-F1)
                        env["fix.storefront.cart.line"].create(
                            {"cart_id": cart.id, "product_id": product.id, "quantity": qty}
                        )
            except (UserError, ValidationError) as exc:
                return _error("PRODUCT_NOT_SELLABLE", str(exc))

        return _cart_payload(cart)

    @http.route("/storefront/checkout", type="jsonrpc", auth="public")
    @api_edge("/storefront/checkout")
    def checkout(
        self,
        cart_id=None,
        shipping_address=None,
        shipping_method="standard_delivery",
        payment_rail="bkash",
        **kwargs,
    ):
        """Checkout the caller's cart and place the storefront customer order.

        ``cart_id`` is optional and, when given, must be the caller's own open cart."""
        env = _su_env()
        cart = _caller_cart(env, kwargs)
        if cart_id not in (None, "", False) and (not cart or cart.id != _to_int(cart_id)):
            return _error("CART_NOT_FOUND", "Cart does not exist")

        if not cart:
            return _error("CART_NOT_FOUND", "Cart does not exist")

        if not cart.line_ids:
            return _error("CART_EMPTY", "Cannot checkout an empty cart")

        shipping_method = shipping_method or "standard_delivery"
        payment_rail = payment_rail or "bkash"
        if shipping_method not in _selection_keys(env, "fix.storefront.order", "shipping_method"):
            return _error("INVALID_SHIPPING_METHOD", f"Unknown shipping method '{shipping_method}'")
        if payment_rail not in _selection_keys(env, "fix.storefront.order", "payment_rail"):
            return _error("INVALID_PAYMENT_RAIL", f"Unknown payment rail '{payment_rail}'")

        guest_customer = None
        if _caller_user() is None:
            # A04 ERP audit M38-F12: every guest order was booked to ONE
            # shared partner. A guest order now belongs to the customer of
            # its mobile number; with no OTP verification on the storefront
            # yet, cash on delivery (money collected against an unverified
            # identity) is offered to signed-in customers only.
            if payment_rail == "cod":
                return _error(
                    "COD_NOT_ALLOWED",
                    "Cash on delivery needs a signed-in customer; please pay online or sign in.",
                )
            guest_customer = guest_customer_for_phone(env, kwargs.get("phone"))
            if not guest_customer:
                return _error(
                    "PHONE_REQUIRED",
                    "A guest order needs the customer's mobile number (01XXXXXXXXX).",
                )

        try:
            # all-or-nothing: a failed placement must not strand the cart in
            # "checkout" (the caller could never reach it again)
            with env.cr.savepoint():
                if guest_customer:
                    cart.write({"customer_id": guest_customer.id})
                cart.action_checkout()
                order = cart.action_place_order(
                    shipping_address=shipping_address,
                    shipping_method=shipping_method,
                    payment_rail=payment_rail,
                )
        except Exception:
            _logger.exception("Checkout failed")  # details stay server-side
            return _error(
                "CHECKOUT_FAILED", "Checkout could not be completed; the cart is unchanged"
            )

        if _caller_user() is None:
            # the guest session may track the order it placed (and nothing else)
            request.session[SESSION_CART_KEY] = None
            placed = list(request.session.get(SESSION_ORDERS_KEY) or [])
            request.session[SESSION_ORDERS_KEY] = [*placed, order.id]

        return {
            "order_id": order.id,
            "order_name": order.name,
            "total_amount": float(order.total_amount),
            "total_bdt": _fmt_bdt(order.total_amount),
            "payment_rail": order.payment_rail,
            "shipping_method": order.shipping_method,
            "shipping_address": order.shipping_address,
            "state": order.state,
        }

    @http.route("/storefront/orders/track", type="jsonrpc", auth="public", readonly=True)
    @api_edge("/storefront/orders/track")
    def track_order(self, order_name=None, order_id=None, **kwargs):
        """Track customer storefront order and reverse logistics consignment.

        Only the order's owner (same commercial partner as the authenticated user),
        internal staff with read access to the order, or the guest session that
        placed it may track an order. Every other lookup — including a sequential
        ``order_id`` or a guessed ``order_name`` — gets the same ``ORDER_NOT_FOUND``
        answer as a non-existent order, so references cannot be enumerated."""
        env = _su_env()
        order = env["fix.storefront.order"]
        if order_id:
            order = order.browse(_to_int(order_id) or 0).exists()
        elif order_name:
            order = order.search([("name", "=", order_name)], limit=1)

        if not order or not _can_view_order(order):
            return _error("ORDER_NOT_FOUND", "Storefront order not found")

        lines = []
        for line in order.line_ids:
            lines.append(
                {
                    "product_id": line.product_id.id,
                    "product_name": line.product_id.name,
                    "quantity": line.quantity,
                    "unit_price_bdt": _fmt_bdt(line.unit_price),
                    "subtotal_bdt": _fmt_bdt(line.subtotal),
                }
            )

        return {
            "order_id": order.id,
            "order_name": order.name,
            "order_date": str(order.order_date),
            "state": order.state,
            "total_bdt": _fmt_bdt(order.total_amount),
            "payment_rail": order.payment_rail,
            "payment_ref": order.payment_ref or "",
            "payment_date": str(order.payment_date or ""),
            "shipping_method": order.shipping_method,
            "shipping_address": order.shipping_address,
            "carrier_consignment": order.carrier_consignment_id.name
            if order.carrier_consignment_id
            else None,
            "lines": lines,
        }

    @http.route("/storefront/returns", type="jsonrpc", auth="user")
    def create_return(self, order_id=None, reason="defective", refund_amount=None, **kwargs):
        """Create a storefront return RMA with reverse logistics integration.

        Requires an authenticated customer who owns the order (commercial partner
        match) and a paid/dispatched/delivered order. The refund is computed by the
        server: the order line total minus refunds already requested on the order; a
        caller-supplied ``refund_amount`` may only lower it."""
        env = _su_env()
        user = request.env.user
        order = env["fix.storefront.order"].browse(_to_int(order_id) or 0).exists()
        if not order or not _owns_order(order, user):
            return _error("ORDER_NOT_FOUND", "Storefront order not found")

        if order.state not in RETURNABLE_STATES:
            return _error(
                "RETURN_NOT_ALLOWED",
                f"Only {'/'.join(RETURNABLE_STATES)} orders can be returned (order is {order.state})",
            )

        return_model = env["fix.storefront.return"]
        reason = reason or "defective"
        if reason not in _selection_keys(env, "fix.storefront.return", "reason"):
            return _error("INVALID_REASON", f"Unknown return reason '{reason}'")

        currency = order.currency_id
        already_requested = sum(
            return_model.search([("order_id", "=", order.id), ("state", "!=", "rejected")]).mapped(
                "refund_amount"
            )
        )
        refundable = currency.round(sum(order.line_ids.mapped("subtotal")) - already_requested)
        if currency.compare_amounts(refundable, 0.0) <= 0:
            return _error("RETURN_NOT_ALLOWED", "The order has no refundable amount left")

        refund_amt = refundable
        if refund_amount not in (None, "", False):
            try:
                requested = float(refund_amount)
            except (TypeError, ValueError):
                requested = float("nan")
            if not math.isfinite(requested) or requested <= 0:
                return _error("INVALID_REFUND_AMOUNT", "refund_amount must be a positive number")
            if currency.compare_amounts(requested, refundable) > 0:
                return _error(
                    "REFUND_EXCEEDS_ORDER",
                    f"refund_amount exceeds the refundable amount {_fmt_bdt(refundable)}",
                )
            refund_amt = currency.round(requested)

        try:
            # A04 audit M38-9: the model refuses a return outside the return
            # window (and re-checks the cap); say so instead of a server error.
            with env.cr.savepoint():
                ret = return_model.create(
                    {
                        "order_id": order.id,
                        "cart_id": order.cart_id.id if order.cart_id else False,
                        "customer_id": order.customer_id.id,
                        "currency_id": currency.id,
                        "reason": reason,
                        "refund_amount": refund_amt,
                        "state": "requested",
                    }
                )
        except (UserError, ValidationError) as exc:
            return _error("RETURN_NOT_ALLOWED", str(exc))

        return {
            "rma_id": ret.id,
            "rma_number": ret.name,
            "order_name": order.name,
            "state": ret.state,
            "reason": ret.reason,
            "refund_bdt": _fmt_bdt(ret.refund_amount),
        }

    @http.route(
        "/storefront/payment/callback/<string:rail>",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    @api_edge("/storefront/payment/callback/<string:rail>", http_route=True)
    def payment_callback(self, rail, **kwargs):
        """The gateway's server-to-server payment notice (bKash / Nagad /
        SSLCOMMERZ IPN). See handle_gateway_callback."""
        payload = {k: v for k, v in kwargs.items() if k != "rail"}
        if not payload:
            try:
                payload = json.loads(request.httprequest.get_data() or b"{}") or {}
            except ValueError:
                payload = {}
        body, status = handle_gateway_callback(_su_env(), rail, payload)
        return request.make_json_response(body, status=status)


def handle_gateway_callback(env, rail, payload):
    """Confirm a storefront payment from a signed gateway notice.

    Returns ``(body, http_status)``. A04 audit M38-2: the only way a payment
    is confirmed without an M20 receipt. The notice must name the order, the
    gateway's transaction id and the amount captured, signed with the rail's
    shared secret; the order is confirmed only when the rail is its own and
    the amount is its total, and a transaction id pays one order."""
    if rail not in GATEWAY_RAILS:
        return {"error": "UNKNOWN_RAIL"}, 404
    if not isinstance(payload, dict):
        return {"error": "BAD_REQUEST"}, 400
    secret = env["ir.config_parameter"].sudo().get_param(GATEWAY_SECRET_PARAM % rail)
    if not secret:
        _logger.warning("Storefront %s callback refused: no gateway secret configured", rail)
        return {"error": "GATEWAY_NOT_CONFIGURED"}, 503
    order_name = str(payload.get("order") or "").strip()
    trx_id = str(payload.get("trx_id") or "").strip()
    amount = payload.get("amount")
    signature = str(payload.get("signature") or "")
    if not (order_name and trx_id and amount not in (None, "")):
        return {"error": "BAD_REQUEST"}, 400
    expected = gateway_signature(secret, order_name, trx_id, amount)
    if not hmac.compare_digest(expected, signature):
        _logger.warning("Storefront %s callback for %s: bad signature", rail, order_name)
        return {"error": "BAD_SIGNATURE"}, 403
    try:
        with env.cr.savepoint():
            order = env["fix.storefront.order"]._sf_gateway_confirm(
                rail, order_name, trx_id, amount
            )
    except (UserError, ValidationError) as exc:
        return {"error": "PAYMENT_REFUSED", "message": str(exc)}, 409
    return {"status": order.state, "order": order.name}, 200
