#!/usr/bin/env python3
"""livefire-pp5 — PP5 deep-audit live probe (all 25 controller routes).

Exercises every PP5 portal API against the running local Odoo (fix_dev):
positive cases on real model writes through the routes, and the
negative cases the source tests only assert structurally (missing
brand_id, KYC gate, proof gate, cross-scope reads...). Records are
prefixed PP5-LIVEFIRE so the run is identifiable in the dev DB.

Usage: python tooling/scripts/livefire-pp5.py
Exit: 0 all checks pass / 1 failures.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from urllib.parse import urlparse

BASE = "http://127.0.0.1:8069"
# The ONLY endpoint this probe may talk to: the local dev Odoo. The bind
# is validated (scheme, host, port) before any request - a test client
# must be as explicit about its target boundary as a production client.
ALLOWED = {("http", "127.0.0.1", 8069), ("http", "localhost", 8069)}
DB = "fix_dev"
ADMIN = ("admin", "admin")
# Run nonce: every run creates its own records (serial numbers are unique)
TAG = "PP5-LIVEFIRE-%d" % int(time.time())

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((label, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))
    return ok


def validate_target(url: str) -> None:
    """Allowlist the request boundary: exact scheme+host+port, nothing else."""
    p = urlparse(url)
    if (p.scheme, p.hostname, p.port or 80) not in ALLOWED:
        raise ValueError(f"livefire-pp5: refusing non-local endpoint {url!r}")


class Client:
    """Minimal Odoo JSON-RPC client with session cookies + dev-reload patience."""

    def __init__(self, base: str = BASE):
        self.base = base
        self.cookie = ""

    def _post(self, path: str, payload: dict, timeout: int = 300) -> dict:
        validate_target(self.base + path)
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Cookie": self.cookie} if self.cookie else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:  # no redirects followed
            sc = r.headers.get("Set-Cookie", "")
            if sc:
                self.cookie = sc.split(";")[0]
            return json.loads(r.read())

    def login(self, login: str = ADMIN[0], password: str = ADMIN[1]) -> bool:
        for _ in range(6):
            try:
                out = self._post(
                    "/web/session/authenticate",
                    {"jsonrpc": "2.0", "params": {"db": DB, "login": login, "password": password}},
                )
                if "result" in out:
                    return True
            except Exception:
                pass
            time.sleep(4)  # server mid-reload (--dev=all)
        return False

    def call(self, model: str, method: str, args, kwargs=None, **extra):
        merged = {**(kwargs or {}), **extra}
        if isinstance(args, list) and not args:
            args = [[]]  # search(domain) with the empty domain
        out = self._post(
            "/web/dataset/call_kw",
            {
                "jsonrpc": "2.0",
                "params": {"model": model, "method": method, "args": args, "kwargs": merged},
            },
        )
        if "error" in out:
            msg = out["error"]["data"].get("message", "?")
            if "Session expired" in msg:
                self.cookie = ""
                if self.login():
                    return self.call(model, method, args, kwargs, **extra)
            raise RuntimeError(msg[:300])
        return out.get("result")

    def route(self, path: str, params: dict):
        """Call an http.route type=json endpoint. Returns (ok, payload);
        a transport/500 error is normalised into the same error shape."""
        try:
            out = self._post(path, {"jsonrpc": "2.0", "params": params})
        except urllib.error.HTTPError as e:
            return False, {
                "error": {
                    "code": "http_%d" % e.code,
                    "message": e.read()[:120].decode(errors="replace"),
                }
            }
        if "error" in out:
            return False, {
                "error": {
                    "code": "server_error",
                    "message": out["error"]["data"].get("message", "?"),
                }
            }
        return True, out.get("result")


def err_code(payload) -> str:
    return (payload or {}).get("error", {}).get("code", "")


def main() -> int:
    c = Client()
    assert c.login(), "cannot authenticate admin"

    # ---------- shared setup: an owner partner + device for P01 ----------
    partner = c.call(
        "res.partner", "create", [{"name": f"{TAG} owner", "email": f"{TAG}@livefire.local"}]
    )
    models = c.call("fix.device.model", "search", [], limit=1)
    branches = c.call("fix.branch", "search", [], limit=1)
    if models:
        model = models[0]
    else:
        brands = c.call("fix.brand", "search", [], limit=1)
        brand = brands[0] if brands else c.call("fix.brand", "create", [{"name": f"{TAG} brand"}])
        model = c.call("fix.device.model", "create", [{"name": f"{TAG} model", "brand_id": brand}])
    device = c.call(
        "fix.device",
        "create",
        [
            {
                "name": f"{TAG} device",
                "device_model_id": model,
                "owner_id": c.call("res.users", "read", [[2], ["partner_id"]])[0]["partner_id"][0],
                "branch_id": branches[0] if branches else False,
                "serial_number": f"{TAG}-SN-001",
            }
        ],
    )

    # ================= P01 Customer =================
    ok, r = c.route("/customer/devices", {})
    check("P01 devices list", ok and "devices" in r, str(r)[:80])
    ok, r = c.route("/customer/bookings", {})
    check("P01 bookings list", ok and "bookings" in r, str(r)[:80])
    ok, r = c.route(
        "/customer/bookings", {"device_id": device, "fault_description": f"{TAG} screen flicker"}
    )
    check("P01 booking create (model write)", ok and r.get("booking", {}).get("ref"), str(r)[:100])
    order_id = r.get("booking", {}).get("id")
    ok, r = c.route("/customer/tracking", {"order_id": order_id})
    check(
        "P01 tracking (state + SLA shape)",
        ok and "tracking" in r and "eta_resolution" in r["tracking"],
        str(r)[:100],
    )
    foreign = c.call("fix.device", "search", [[("serial_number", "!=", f"{TAG}-SN-001")]], limit=1)
    if foreign:
        ok, r = c.route("/customer/bookings", {"device_id": foreign[0], "fault_description": "x"})
        check(
            "P01 booking on a foreign device rejected",
            ok and err_code(r) == "not_owner",
            err_code(r),
        )
    ok, r = c.route("/customer/estimates", {})
    check("P01 estimates list", ok and "estimates" in r, str(r)[:80])
    est_order = c.call("fix.service.order", "search", [[("customer_id", "!=", 2)]], limit=1)
    if est_order:
        est = c.call("fix.estimate", "search", [[("order_id", "=", est_order)]], limit=1)
        if est:
            ok, r = c.route("/customer/estimates", {"estimate_id": est[0], "action": "approve"})
            check(
                "P01 approving someone else's estimate refused",
                ok and err_code(r) in ("not_your_estimate", "no_estimate"),
                err_code(r),
            )
    ok, r = c.route("/customer/consent", {})
    check("P01 consent dashboard", ok and "consents" in r, str(r)[:80])
    ok, r = c.route("/customer/consent", {"action": "grant", "channel": "sms"})
    check("P01 grant without proof refused", ok and err_code(r) == "missing_proof", err_code(r))
    ok, r = c.route(
        "/customer/consent", {"action": "grant", "channel": "sms", "proof": f"{TAG}-OTP-1"}
    )
    check(
        "P01 grant with proof", ok and r.get("consent", {}).get("state") == "granted", str(r)[:80]
    )
    ok, r = c.route("/customer/consent", {"action": "withdraw", "channel": "sms"})
    check(
        "P01 withdraw keeps the trail",
        ok and r.get("consent", {}).get("state") == "withdrawn",
        str(r)[:80],
    )
    other = c.call("res.partner", "create", [{"name": f"{TAG} transferee"}])
    ok, r = c.route("/customer/ownership/transfer", {"device_id": device, "to_partner_id": other})
    check("P01 ownership transfer (T05)", ok and r.get("transferred"), str(r)[:80])
    ok, r = c.route("/customer/ownership/transfer", {"device_id": device, "to_partner_id": partner})
    check("P01 re-transfer by former owner refused", ok and err_code(r) == "not_owner", err_code(r))

    # ================= P05 Vendor =================
    ok, r = c.route("/vendor/purchase-orders", {})
    check("P05 PO list", ok and "purchase_orders" in r, str(r)[:80])
    vendor = c.call("res.partner", "create", [{"name": f"{TAG} vendor"}])
    products = c.call("product.product", "search", [], limit=1)
    if products and branches:
        product = products[0]
        ous = c.call("operating.unit", "search", [], limit=1)
        po = c.call(
            "fix.purchase.order",
            "create",
            [
                {
                    "vendor_id": vendor,
                    "branch_id": branches[0],
                    "operating_unit_id": ous[0] if ous else False,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product,
                                "description": f"{TAG} part",
                                "qty_ordered": 5,
                                "unit_price": 100.0,
                            },
                        )
                    ],
                }
            ],
        )
        c.call("fix.purchase.order", "action_send", [po])
        lines = c.call("fix.purchase.order.line", "search", [[("order_id", "=", po)]], limit=1)
        ok, r = c.route("/vendor/purchase-orders", {"po_id": po, "action": "acknowledge"})
        check(
            "P05 PO acknowledge (RFQ response)",
            ok and r.get("purchase_order", {}).get("state") == "acknowledged",
            str(r)[:80],
        )
        ok, r = c.route(
            "/vendor/purchase-orders", {"po_id": po, "action": "deliver", "receipts": {lines[0]: 5}}
        )
        check(
            "P05 delivery confirm",
            ok and r.get("purchase_order", {}).get("state") == "received",
            str(r)[:80],
        )
        ok, r = c.route("/vendor/invoices", {})
        check(
            "P05 invoice list (match state ships)",
            ok and "match_state" in json.dumps(r)[:400],
            str(r)[:80],
        )
        ok, r = c.route("/vendor/invoices", {"invoice_ref": f"{TAG}-INV-1", "vendor_id": vendor})
        check("P05 invoice without PO refused", ok and err_code(r) == "missing_po", err_code(r))
        ok, r = c.route(
            "/vendor/invoices",
            {
                "invoice_ref": f"{TAG}-INV-1",
                "po_id": po,
                "lines": [
                    {
                        "product_id": product,
                        "description": f"{TAG} part",
                        "quantity": 5,
                        "unit_price": 100.0,
                    }
                ],
            },
        )
        check(
            "P05 invoice submit -> 3-way match runs",
            ok and r.get("invoice", {}).get("match_state") == "matched",
            str(r)[:120],
        )
        ok, r = c.route(
            "/vendor/invoices",
            {
                "invoice_ref": f"{TAG}-INV-2",
                "po_id": po,
                "lines": [
                    {
                        "product_id": product,
                        "description": "overcharge",
                        "quantity": 5,
                        "unit_price": 999.0,
                    }
                ],
            },
        )
        check(
            "P05 overprice invoice BLOCKED with reason",
            ok
            and r.get("invoice", {}).get("match_state") == "blocked"
            and "price above PO" in (r.get("invoice", {}).get("match_detail") or ""),
            str(r.get("invoice", {}))[:120],
        )

    # ================= P06 Analytics =================
    ok, r = c.route("/analytics/dashboards", {})
    check("P06 dashboard registry (5)", ok and len(r.get("dashboards", [])) == 5, str(r)[:80])
    ok, r = c.route("/analytics/kpis", {"dashboard": "executive"})
    check(
        "P06 executive KPIs (read_group)",
        ok and "orders_by_state" in r.get("kpis", {}),
        str(r)[:100],
    )
    ok, r = c.route("/analytics/kpis", {"dashboard": "warranty"})
    check(
        "P06 warranty KPIs include claims",
        ok and "claims_by_state" in r.get("kpis", {}),
        str(r)[:100],
    )
    ok, r = c.route("/analytics/kpis", {"dashboard": "bogus"})
    check("P06 invalid dashboard rejected", ok and err_code(r) == "invalid_dashboard", err_code(r))

    # ================= P07 Seller =================
    ok, r = c.route("/seller/dashboard", {})
    check(
        "P07 dashboard without profile -> structured",
        ok and err_code(r) == "no_seller",
        err_code(r),
    )
    seller = c.call(
        "fix.marketplace.seller", "create", [{"name": f"{TAG} seller", "partner_id": partner}]
    )
    mo = c.call(
        "fix.marketplace.order",
        "create",
        [
            {
                "name": f"{TAG} job",
                "description": f"{TAG} broken screen",
                "customer_id": partner,
                "budget": 5000.0,
            }
        ],
    )
    ok, r = c.route("/seller/orders", {"seller_id": seller})
    check(
        "P07 jobs board lists open order",
        ok and any(o["id"] == mo for o in r.get("orders", [])),
        str(r)[:80],
    )
    ok, r = c.route("/seller/quotes", {"seller_id": seller, "order_id": mo, "quoted_price": 4500})
    check(
        "P07 quote BLOCKED before KYC (gate stated)",
        ok and err_code(r) == "kyc_not_verified",
        err_code(r),
    )
    c.call("fix.marketplace.seller", "action_verify_kyc", [seller])
    ok, r = c.route("/seller/quotes", {"seller_id": seller, "order_id": mo, "quoted_price": 4500})
    check("P07 quote after KYC", ok and r.get("quote", {}).get("id"), str(r)[:80])
    ok, r = c.route("/seller/scorecard", {"seller_id": seller})
    check("P07 scorecard list", ok and "scorecard" in r, str(r)[:60])
    ok, r = c.route("/seller/settlements", {"partner_id": partner})
    check("P07 settlements (ledger module route)", ok and "settlements" in r, str(r)[:80])

    # ================= P08 Brand =================
    ok, r = c.route("/brand/claims", {})
    check("P08 unscoped claims REFUSED", ok and err_code(r) == "missing_brand", err_code(r))
    brand = c.call("fix.brand", "search", [], limit=1)
    if brand:
        brand = brand[0]
        ok, r = c.route("/brand/claims", {"brand_id": brand})
        check("P08 claims list (brand-scoped)", ok and "claims" in r, str(r)[:60])
        ok, r = c.route("/brand/claims/status", {"brand_id": brand, "claim_no": "NO-SUCH-CLAIM"})
        check(
            "P08 unknown claim is not-found (isolation)",
            ok and err_code(r) == "no_claim",
            err_code(r),
        )
        ok, r = c.route(
            "/brand/claims", {"brand_id": brand, "claim_id": 999999, "decision": "approve"}
        )
        check(
            "P08 foreign/nonexistent claim decision refused",
            ok and err_code(r) == "no_claim",
            err_code(r),
        )
        ok, r = c.route("/brand/reconciliation", {"brand_id": brand})
        check("P08 reconciliation view", ok and "reconciliation" in r, str(r)[:60])

    # ================= P10 Contact =================
    ous = c.call("operating.unit", "search", [], limit=1)
    conv = c.call(
        "fix.conversation",
        "create",
        [
            {
                "channel": "voice",
                "contact_identity": f"{TAG}-16743",
                "state": "with_ai",
                "operating_unit_id": ous[0] if ous else False,
            }
        ],
    )
    c.call(
        "fix.conversation.turn",
        "create",
        [
            {
                "conversation_id": conv,
                "speaker": "customer",
                "text": "আমার ফোনের স্ক্রিন ভেঙে গেছে",
                "lang": "bn",
            }
        ],
    )
    ok, r = c.route("/contact/conversations", {})
    check(
        "P10 unified queue lists the call",
        ok and any(x["id"] == conv for x in r.get("conversations", [])),
        str(r)[:80],
    )
    ok, r = c.route("/contact/conversations/detail", {"conversation_id": conv})
    d = r.get("conversation", {}) if ok else {}
    check(
        "P10 detail: transcript + 360 bundle",
        ok and len(d.get("transcript", [])) == 1 and "customer_360" in d,
        str(r)[:100],
    )
    ok, r = c.route("/contact/handoff", {"conversation_id": conv, "action": "claim"})
    check(
        "P10 claim -> with_agent",
        ok and r.get("conversation", {}).get("state") == "with_agent",
        str(r)[:80],
    )
    ok, r = c.route("/contact/handoff", {"conversation_id": conv, "action": "claim"})
    check("P10 double-claim refused", ok and err_code(r) == "not_claimable", err_code(r))
    ok, r = c.route("/contact/handoff", {"conversation_id": conv, "action": "end"})
    check(
        "P10 end -> resolved_agent",
        ok and r.get("conversation", {}).get("state") == "resolved_agent",
        str(r)[:80],
    )
    ok, r = c.route("/contact/softphone", {})
    check(
        "P10 softphone seam (nulls, no hosts)",
        ok and all(v is None for v in r.get("softphone", {}).values()),
        str(r)[:80],
    )

    # ================= P12 Partner =================
    ok, r = c.route("/partner/profile", {})
    check(
        "P12 profile without profile -> structured",
        ok and err_code(r) == "no_partner_profile",
        err_code(r),
    )
    prof = c.call("fix.partner", "create", [{"name": f"{TAG} partner", "partner_id": partner}])
    referred = c.call("res.partner", "create", [{"name": f"{TAG} referred"}])
    ok, r = c.route("/partner/referrals", {"partner_profile_id": prof})
    check("P12 referrals list", ok and "referrals" in r, str(r)[:60])
    ok, r = c.route(
        "/partner/referrals", {"partner_profile_id": prof, "referred_name": f"{TAG} referral"}
    )
    check(
        "P12 referral without referred party refused",
        ok and err_code(r) == "missing_referred",
        err_code(r),
    )
    ok, r = c.route(
        "/partner/referrals",
        {
            "partner_profile_id": prof,
            "referred_partner_id": referred,
            "referred_name": f"{TAG} referral",
        },
    )
    check("P12 referral submit", ok and r.get("referral", {}).get("id"), str(r)[:80])
    ok, r = c.route("/partner/commissions", {"partner_profile_id": prof})
    check(
        "P12 commission statement",
        ok and "earned_total_bdt" in r.get("commissions", {}),
        str(r)[:80],
    )

    failures = [x for x in RESULTS if not x[1]]
    print(f"\nlivefire-pp5: {len(RESULTS) - len(failures)}/{len(RESULTS)} checks passed")
    for label, _, detail in failures:
        print(f"  FAILED: {label} - {detail}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
