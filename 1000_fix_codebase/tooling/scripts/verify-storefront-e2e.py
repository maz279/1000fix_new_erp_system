"""E2E verification of the M38 Storefront API (catalogue -> cart -> checkout -> track -> return).

R01 re-audit 2026-10-22: carts and orders are bound to the caller and
``/storefront/returns`` is ``auth="user"`` + order ownership, so the lifecycle runs in an
AUTHENTICATED Odoo session of a customer test user - the order's owner. A second,
cookie-less session checks that a guest can neither track nor return that order.

Configuration comes from the environment only (credentials are never hard-coded):

  FIX_E2E_LOGIN, FIX_E2E_PASSWORD   test customer who places and returns the order (required)
  FIX_E2E_DB                         Odoo database (default: fix_dev)
  FIX_E2E_BASE_URL                   Odoo base URL (default: http://127.0.0.1:8069)
  FIX_E2E_STAFF_LOGIN, FIX_E2E_STAFF_PASSWORD
                                     optional internal test user standing in for the payment
                                     gateway: confirms the payment so the owner's return yields
                                     an RMA. Without it the order stays ``pending_payment`` and
                                     the owner's return must be refused (RETURN_NOT_ALLOWED).
"""

import json
import os
import urllib.request
from http.cookiejar import CookieJar

DEFAULT_BASE_URL = "http://127.0.0.1:8069"
DEFAULT_DB = "fix_dev"


class OdooSession:
    """A JSON-RPC client with its own cookie jar - one Odoo session per instance."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    def envelope(self, endpoint, params):
        """POST a JSON-RPC call; return the raw envelope (``result`` or ``error``)."""
        req_data = {"jsonrpc": "2.0", "method": "call", "params": params, "id": 1}
        req = urllib.request.Request(
            f"{self.base_url}{endpoint}",
            data=json.dumps(req_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with self._opener.open(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def call(self, endpoint, params):
        """The call's result; a JSON-RPC level error (auth, server fault) aborts the run."""
        envelope = self.envelope(endpoint, params)
        if "error" in envelope:
            err = envelope["error"]
            detail = (err.get("data") or {}).get("message") or err.get("message")
            raise SystemExit(f"FAIL {endpoint}: {detail}")
        return envelope.get("result")

    def authenticate(self, db, login, password):
        """Open an authenticated session (the session cookie stays in this jar)."""
        info = self.call(
            "/web/session/authenticate", {"db": db, "login": login, "password": password}
        )
        if not info or not info.get("uid"):
            raise SystemExit(f"FAIL: could not authenticate {login!r} on database {db!r}")
        return info


def _env(name, default=None, required=False):
    value = os.environ.get(name, "").strip() or default
    if required and not value:
        raise SystemExit(
            f"Set {name} (see the module docstring) - credentials are never hard-coded."
        )
    return value


def _ok(result, step):
    """Business refusals come back as a result ``{"error": {...}}``."""
    assert isinstance(result, dict), f"{step}: unexpected result {result!r}"
    assert "error" not in result, f"{step} refused: {result['error']}"
    return result


def _error_code(result):
    return ((result or {}).get("error") or {}).get("code")


def main():
    base_url = _env("FIX_E2E_BASE_URL", DEFAULT_BASE_URL)
    db = _env("FIX_E2E_DB", DEFAULT_DB)
    login = _env("FIX_E2E_LOGIN", required=True)
    password = _env("FIX_E2E_PASSWORD", required=True)
    staff_login = _env("FIX_E2E_STAFF_LOGIN")
    staff_password = _env("FIX_E2E_STAFF_PASSWORD")
    if bool(staff_login) != bool(staff_password):
        raise SystemExit("Set both FIX_E2E_STAFF_LOGIN and FIX_E2E_STAFF_PASSWORD, or neither.")

    print("Testing Complete M38 Storefront E2E Lifecycle (authenticated order owner)...")

    owner = OdooSession(base_url)
    who = owner.authenticate(db, login, password)
    print(f"0. Authenticated as {who.get('username') or login} (uid {who['uid']}) on {db}")

    # 1. Browse catalogue
    catalogue = _ok(owner.call("/storefront/catalogue", {"limit": 5}), "catalogue")
    products = catalogue.get("products", [])
    print(f"1. Catalogue loaded: {len(products)} products available.")
    assert len(products) > 0, "Expected at least 1 product in catalogue"
    test_prod = products[0]
    print(f"   Selected Product: {test_prod['name']} (BDT {test_prod['price_bdt']})")

    # 2. Add product to the owner's cart (resolved server-side from the session)
    cart = _ok(
        owner.call("/storefront/cart", {"product_id": test_prod["id"], "quantity": 2}), "cart"
    )
    cart_id = cart.get("cart_id")
    print(
        f"2. Cart #{cart.get('cart_name')} (ID: {cart_id}) Total: BDT {cart.get('total_bdt')} ({cart.get('items_count')} items)"
    )
    assert cart_id is not None, "Cart ID should not be None"
    assert cart.get("items_count") >= 1, "Cart should have items"

    # 3. Checkout with bKash payment rail
    checkout = _ok(
        owner.call(
            "/storefront/checkout",
            {
                "cart_id": cart_id,
                "shipping_address": "House 12, Road 5, Dhanmondi, Dhaka 1205",
                "shipping_method": "express_courier",
                "payment_rail": "bkash",
            },
        ),
        "checkout",
    )
    order_id = checkout.get("order_id")
    order_name = checkout.get("order_name")
    print(
        f"3. Order Placed #{order_name} (ID: {order_id}) State: {checkout.get('state')} Rail: {checkout.get('payment_rail')} Total: BDT {checkout.get('total_bdt')}"
    )
    assert order_id is not None, "Order ID should be created on checkout"

    # 4. Track Order as its owner
    track = _ok(owner.call("/storefront/orders/track", {"order_id": order_id}), "track")
    print(
        f"4. Order Tracking: #{track.get('order_name')} State: {track.get('state')} Delivery: {track.get('shipping_method')}"
    )
    assert track.get("order_name") == order_name, "Order name should match"

    # 4b. A cookie-less guest can neither see nor return the owner's order
    guest = OdooSession(base_url)
    guest_track = guest.call("/storefront/orders/track", {"order_id": order_id})
    assert (
        _error_code(guest_track) == "ORDER_NOT_FOUND"
    ), f"a guest must not track another customer's order, got {guest_track!r}"
    guest_return = guest.envelope("/storefront/returns", {"order_id": order_id})
    assert (
        "error" in guest_return
    ), f"an unauthenticated return must be refused (auth=user), got {guest_return!r}"
    print("4b. Guest without session: tracking -> ORDER_NOT_FOUND, return -> refused")

    # 5. Payment confirmation - the gateway's job, simulated by an internal user
    if staff_login:
        staff = OdooSession(base_url)
        staff.authenticate(db, staff_login, staff_password)
        staff.call(
            "/web/dataset/call_kw/fix.storefront.order/action_confirm_payment",
            {
                "model": "fix.storefront.order",
                "method": "action_confirm_payment",
                "args": [[order_id]],
                "kwargs": {"payment_ref": f"E2E-{order_name}"},
            },
        )
        paid = _ok(owner.call("/storefront/orders/track", {"order_id": order_id}), "track (paid)")
        assert paid.get("state") == "paid", f"Order should be paid, got {paid.get('state')}"
        print(f"5. Payment confirmed by {staff_login}: #{order_name} State: {paid.get('state')}")
    else:
        print("5. Payment confirmation skipped (FIX_E2E_STAFF_LOGIN not set) - order stays unpaid")

    # 6. Reverse Logistics Return RMA, requested by the owner; the server computes the refund
    ret = owner.call("/storefront/returns", {"order_id": order_id, "reason": "defective"})
    if staff_login:
        _ok(ret, "return")
        print(
            f"6. Return RMA Generated: #{ret.get('rma_number')} State: {ret.get('state')} Reason: {ret.get('reason')} Refund: BDT {ret.get('refund_bdt')}"
        )
        assert ret.get("rma_id") is not None, "RMA ID should be created"
    else:
        assert (
            _error_code(ret) == "RETURN_NOT_ALLOWED"
        ), f"a return on an unpaid order must be refused, got {ret!r}"
        print("6. Return on the unpaid order refused (RETURN_NOT_ALLOWED) as expected")

    print("\nALL STOREFRONT ENDPOINTS VERIFIED 100% WORKING!")


if __name__ == "__main__":
    main()
