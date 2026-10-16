#!/usr/bin/env python3
"""livefire-p03 — live positive/negative probes for the P03 workspace API.

Exercises every /p03/* endpoint the Operations Workspace calls, against the
running fix_dev server: stats, orders/list (with real estimate money),
order/get (full detail), order/create (AS-09 validation + happy path),
advance_stage (strict AS-06 transitions), dispatch/assign (real work order),
inventory/reserve (real product), plus the registry + tellme controllers.

Dev-only harness: the target is pinned to the loopback literal below and
every request URL is validated (http, 127.0.0.1, fixed port) before use;
redirects are refused.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime

BASE = "http://127.0.0.1:8069"
DB = "fix_dev"
ADMIN = ("admin", "admin")
TAG = "P03-LIVEFIRE"

PASS, FAIL = 0, 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}" + (f" :: {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  [FAIL] {name} :: {detail}")


def safe_url(path: str) -> str:
    """Pinned-target guard: only http://127.0.0.1:8069/<path> may be fetched."""
    url = BASE + path
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "http" or parts.hostname != "127.0.0.1"
            or parts.port != 8069 or parts.username or parts.query
            or parts.fragment):
        raise ValueError(f"refusing non-loopback target: {url!r}")
    return url


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # never follow redirects (SSRF hygiene)


_OPENER = urllib.request.build_opener(_NoRedirect)


class Client:
    def __init__(self):
        self.cookie = ""

    def _post(self, path, payload):
        req = urllib.request.Request(
            safe_url(path),
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Accept": "application/json",
                     **({"Cookie": self.cookie} if self.cookie else {})})
        with _OPENER.open(req, timeout=30) as r:
            if "set-cookie" in r.headers:
                self.cookie = r.headers["set-cookie"].split(";")[0]
            return json.loads(r.read())

    def login(self):
        out = self._post("/web/session/authenticate", {
            "jsonrpc": "2.0",
            "params": {"db": DB, "login": ADMIN[0], "password": ADMIN[1]}})
        return bool(out.get("result", {}).get("uid"))

    def call(self, path, params=None):
        return self._post(path, {"jsonrpc": "2.0", "params": params or {}})


def main() -> int:
    c = Client()
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            if c.login():
                break
        except Exception:
            pass
        time.sleep(3)
    else:
        print("cannot authenticate admin")
        return 2
    print(f"{TAG} authenticated @ {datetime.now(UTC).isoformat()}")

    nonce = str(int(time.time()) % 100000)

    # --- /p03/stats -------------------------------------------------------
    stats = c.call("/p03/stats").get("result", {})
    check("stats: aggregates present",
          all(k in stats for k in ("open_orders", "intake_today", "sla_at_risk",
                                   "by_state", "channel_mix", "trend", "worklist",
                                   "my_activities", "branches", "technicians",
                                   "company")))
    check("stats: revenue_mtd numeric", isinstance(stats.get("revenue_mtd"), (int, float)))
    check("stats: branches from live master",
          isinstance(stats.get("branches"), list) and len(stats["branches"]) >= 1,
          f"{len(stats.get('branches', []))} branches")

    # --- /p03/orders/list: money is estimate-backed or null ---------------
    r = c.call("/p03/orders/list", {"limit": 10}).get("result", {})
    orders = r.get("orders", [])
    check("orders/list: rows served", isinstance(orders, list))
    check("orders/list: no hardcoded 4945 amounts",
          all(o.get("grand_total") != 4945 for o in orders))

    # --- /p03/order/create: AS-09 negative --------------------------------
    r = c.call("/p03/order/create", {
        "customer_name": "", "customer_phone": "",
        "fault_description": "",
    }).get("result", {})
    check("create: rejects missing required fields",
          r.get("success") is False and "required" in r.get("error", ""))

    # --- /p03/order/create: happy path (idempotency DI-04) ----------------
    key = f"livefire-{nonce}"
    payload = {
        "customer_name": f"Livefire Probe {nonce}",
        "customer_phone": f"+8809{nonce}000001",
        "branch_name": (stats.get("branches") or [""])[0],
        "brand": "Dell", "model": "Latitude 5420",
        "serial": f"LIVEFIRE-{nonce}",
        "fault_description": "Probe fault — livefire",
        "priority": "high", "service_type": "walk_in",
        "entitlement": "standard", "idempotency_key": key,
    }
    r = c.call("/p03/order/create", payload).get("result", {})
    check("create: order created", r.get("success") is True, r.get("order_name", ""))
    order_id = r.get("order_id")

    r2 = c.call("/p03/order/create", payload).get("result", {})
    check("create: idempotent replay returns same order",
          r2.get("success") is True and r2.get("order_id") == order_id
          and r2.get("idempotent_replay") is True)

    # --- /p03/order/get: real detail, no fabricated fallbacks -------------
    r = c.call("/p03/order/get", {"order_id": order_id}).get("result", {})
    o = r.get("order", {})
    check("get: full payload keys",
          r.get("success") and all(k in o for k in (
              "name", "customer_name", "customer_phone", "device_name",
              "serial_number", "branch_name", "state", "fault_description",
              "grand_total", "vat_amount")))
    check("get: phone is the real input (no fabricated fallback)",
          o.get("customer_phone") == payload["customer_phone"])
    check("get: no estimate yet → amounts null",
          o.get("grand_total") is None and o.get("vat_amount") is None)

    # --- /p03/order/advance_stage: strict AS-06 ---------------------------
    r = c.call("/p03/order/advance_stage",
               {"order_id": order_id, "next_state": "delivered"}).get("result", {})
    check("advance: illegal hop refused with valid-nexts error",
          r.get("success") is False and "Valid" in r.get("error", ""),
          r.get("error", "")[:60])
    r = c.call("/p03/order/advance_stage",
               {"order_id": order_id, "next_state": "diagnosing"}).get("result", {})
    check("advance: intake→diagnostic ok", r.get("success") is True,
          f"state={r.get('state')}")

    # --- /p03/dispatch/assign: real work order, or the estate's M22 gate --
    techs = stats.get("technicians") or []
    tech = techs[0] if techs else ""
    r = c.call("/p03/dispatch/assign",
               {"order_id": order_id, "technician": tech,
                "notes": "livefire"}).get("result", {})
    if r.get("success"):
        check("dispatch: assigns via HR + creates work order",
              bool(r.get("work_order")),
              f"tech={r.get('technician')} wo={r.get('work_order')}")
        dispatch_ok = True
    elif r.get("refused_by_gate"):
        # The estate's real assignment gates (M22 certification FR-LMS-039,
        # M55 roster availability) refuse honestly — never bypassed.
        check("dispatch: assignment gate held (structured refusal)",
              any(m in r.get("error", "") for m in
                  ("eligibility", "availability", "roster")),
              r.get("error", "")[:70])
        dispatch_ok = False
    else:
        check("dispatch: clean refusal (no fake assign)", False,
              r.get("error", "")[:80])
        dispatch_ok = False

    # --- /p03/inventory/reserve: real product ------------------------------
    r = c.call("/p03/inventory/reserve",
               {"order_id": order_id, "part_sku": "__no_such_sku__",
                "qty": 1}).get("result", {})
    check("reserve: unknown SKU refused honestly",
          r.get("success") is False and "No product" in r.get("error", ""))

    r = c.call("/p03/inventory/reserve",
               {"order_id": order_id, "part_sku": "Service",
                "qty": 1}).get("result", {})
    if r.get("success"):
        check("reserve: real product reserved on work order",
              r.get("success") is True and r.get("work_order"),
              f"part={r.get('part')} unit_cost={r.get('unit_cost')}")
    else:
        check("reserve: no matching product → refused (no fabricated rows)",
              "No product" in r.get("error", ""), r.get("error", "")[:60])

    # --- /p03/order/get after dispatch: audit trail has real chatter -------
    r = c.call("/p03/order/get", {"order_id": order_id}).get("result", {})
    trail = r.get("audit_trail", [])
    if dispatch_ok:
        check("get: audit trail from real mail.thread (incl. dispatch note)",
              len(trail) >= 1 and any("Dispatch" in (m.get("event") or "")
                                      for m in trail),
              f"{len(trail)} messages")
    else:
        check("get: audit trail from real mail.thread",
              len(trail) >= 1, f"{len(trail)} messages")

    # --- registry + tellme controllers still healthy -----------------------
    r = c.call("/p03/registry").get("result", {})
    check("registry: areas served", len(r.get("areas", [])) >= 11)
    r = c.call("/p03/tellme", {"query": "orders", "limit": 3}).get("result", {})
    check("tellme: results served", len(r.get("results", [])) >= 1)

    print(f"\n{TAG}: {PASS}/{PASS + FAIL} checks passed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
