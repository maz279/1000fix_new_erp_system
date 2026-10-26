#!/usr/bin/env python3
"""M04 seed + live verification on real fix_dev data.

Seed (real, derived):
  1. issue tokens at real branches (the queue)
  2. walk tokens through call → serving → complete (waiting times recorded)
  3. one no-show + recall
  4. counter sales on products (cash into a real shift's takings)
  5. a full shift lifecycle: open → close → confirm → reconcile (balanced
     and a variance case)
  6. one walk-in intake through handover_pending → completed (order created
     + token linked)

Verify every M04 endpoint against DB truth.

Local verification only: literal loopback host via http.client."""

import http.client
import json
import os

HOST = "localhost"
PORT = 8069
DB = "fix_dev"
USER = "admin"
PWD = os.environ.get("ODOO_RPC_PWD", "admin")  # local dev default; env overrides

rid = [0]
UID = [None]
COOKIE = [None]


def _post(path, payload):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=90)
    headers = {"Content-Type": "application/json"}
    if COOKIE[0]:
        headers["Cookie"] = COOKIE[0]
    conn.request("POST", path, json.dumps(payload), headers)
    resp = conn.getresponse()
    if not COOKIE[0] and resp.getheader("Set-Cookie"):
        COOKIE[0] = resp.getheader("Set-Cookie").split(";")[0]
    body = resp.read()
    conn.close()
    return json.loads(body)


def call(service, method, *args):
    rid[0] += 1
    resp = _post(
        "/jsonrpc",
        {
            "jsonrpc": "2.0",
            "method": "call",
            "id": rid[0],
            "params": {"service": service, "method": method, "args": list(args)},
        },
    )
    if "error" in resp:
        return {"error": resp["error"].get("data", {}).get("message") or resp["error"]}
    return resp.get("result")


def login():
    rid[0] += 1
    resp = _post(
        "/web/session/authenticate",
        {
            "jsonrpc": "2.0",
            "method": "call",
            "id": rid[0],
            "params": {"db": DB, "login": USER, "password": PWD},
        },
    )
    UID[0] = (resp.get("result") or {}).get("uid")
    return UID[0] is not None


def ep(path, params=None):
    rid[0] += 1
    resp = _post(
        path,
        {"jsonrpc": "2.0", "method": "call", "id": rid[0], "params": params or {}},
    )
    if "error" in resp:
        return {"error": resp["error"].get("data", {}).get("message") or resp["error"]}
    return resp.get("result")


def kw(model, method, args=None, kwargs=None):
    return call("object", "execute_kw", DB, UID[0], PWD, model, method, args or [], kwargs or {})


def main():
    assert login(), "login failed"
    checks = []

    def ok(name, cond, detail=""):
        checks.append((name, bool(cond)))
        print(
            ("  PASS " if cond else "  FAIL ") + name + ((" :: " + str(detail)) if detail else "")
        )

    branches = kw("fix.branch", "search", [[["active", "=", True]]], {"limit": 3})
    customers = kw("res.partner", "search", [[]], {"limit": 6, "order": "id desc"})
    ou = kw("operating.unit", "search", [[]], {"limit": 1})[0]
    branch_ou = {b: ou for b in branches}  # OU attached per branch below
    rows = kw("fix.branch", "search_read", [[["id", "in", branches]], ["id", "operating_unit_id"]])
    for row in rows:
        branch_ou[row["id"]] = row["operating_unit_id"][0] if row["operating_unit_id"] else ou

    # ---------- seed ----------
    print("[seed] issue tokens at real branches")
    issued = 0
    token_ids = []
    for i in range(8):
        vals = {
            "branch_id": branches[i % len(branches)],
            "operating_unit_id": branch_ou[branches[i % len(branches)]],
            "customer_id": customers[i % len(customers)],
            "service_type": ["drop_off", "pick_up", "enquiry", "payment"][i % 4],
            "counter_number": (i % 3) + 1,
        }
        tid = kw("fix.token.queue", "create", [vals])
        if isinstance(tid, int):
            issued += 1
            token_ids.append(tid)
    print("  issued %d tokens" % issued)

    print("[seed] walk queue lifecycles")
    completed = noshow = 0
    for i, tid in enumerate(token_ids):
        if i == 5:
            ep(
                "/p03/model/action",
                {"model": "fix.token.queue", "ids": [tid], "method": "action_call"},
            )
            ep(
                "/p03/model/action",
                {"model": "fix.token.queue", "ids": [tid], "method": "action_no_show"},
            )
            r3 = ep(
                "/p03/model/action",
                {"model": "fix.token.queue", "ids": [tid], "method": "action_call"},
            )
            if r3.get("success"):
                noshow += 1
            continue
        ep("/p03/model/action", {"model": "fix.token.queue", "ids": [tid], "method": "action_call"})
        ep(
            "/p03/model/action",
            {"model": "fix.token.queue", "ids": [tid], "method": "action_serving"},
        )
        r = ep(
            "/p03/model/action",
            {"model": "fix.token.queue", "ids": [tid], "method": "action_complete"},
        )
        if r.get("success"):
            completed += 1
    print("  completed %d, no-show+recalled %d" % (completed, noshow))

    print("[seed] shift lifecycle (open → close → confirm → reconcile)")
    operators = kw("hr.employee", "search", [[["active", "=", True]]], {"limit": 2})
    from datetime import date as d

    shift_ids = []
    for j, variance_case in enumerate([False, True]):
        b = branches[j % len(branches)]
        vals = {
            "branch_id": b,
            "operating_unit_id": branch_ou[b],
            "operator_id": operators[j % len(operators)],
            "shift_date": str(d.today()),
            "shift_type": "morning",
            "opening_float": 2000.0,
        }
        sid = kw("fix.cash.shift", "create", [vals])
        ep(
            "/p03/model/action",
            {"model": "fix.cash.shift", "ids": [sid], "method": "action_close_shift"},
        )
        counted = 2000.0 if not variance_case else 1985.0
        kw("fix.cash.shift", "write", [[sid], {"closing_counted": counted, "cash_payments": 0.0}])
        ep(
            "/p03/model/action",
            {"model": "fix.cash.shift", "ids": [sid], "method": "action_confirm_closed"},
        )
        r = ep(
            "/p03/model/action",
            {"model": "fix.cash.shift", "ids": [sid], "method": "action_reconcile"},
        )
        shift_ids.append(sid)
    states = kw("fix.cash.shift", "read", [shift_ids, ["state", "variance"]])
    print("  shifts: %s" % [(s["state"], s["variance"]) for s in states])

    print("[seed] counter sales")
    products = kw("product.product", "search_read", [[], ["id", "list_price"]], {"limit": 3})
    sales_made = 0
    for i, p in enumerate(products[:3]):
        vals = {
            "shift_id": shift_ids[0],
            "branch_id": branches[0],
            "operating_unit_id": branch_ou[branches[0]],
            "product_id": p["id"],
            "quantity": 1 + i,
            "unit_price": p["list_price"] or 300.0,
            "payment_method": "cash" if i % 2 == 0 else "bkash",
        }
        cs = kw("fix.counter.sale", "create", [vals])
        r = ep(
            "/p03/model/action",
            {"model": "fix.counter.sale", "ids": [cs], "method": "action_confirm"},
        )
        if r.get("success"):
            sales_made += 1
    print("  confirmed %d counter sales" % sales_made)

    print("[seed] walk-in intake through handover_pending")
    brand_device = kw("fix.device", "search", [[["active", "=", True]]], {"limit": 1})
    wi_vals = {
        "branch_id": branches[0],
        "operating_unit_id": branch_ou[branches[0]],
        "customer_id": customers[0],
        "fault_description": "Seed: screen flicker",
    }
    if brand_device:
        wi_vals["device_id"] = brand_device[0]
    wi = kw("fix.walkin.intake", "create", [wi_vals])
    tk = kw(
        "fix.token.queue",
        "create",
        [
            {
                "branch_id": branches[0],
                "operating_unit_id": branch_ou[branches[0]],
                "customer_id": customers[0],
            }
        ],
    )
    kw("fix.walkin.intake", "write", [[wi], {"token_id": tk}])
    ep(
        "/p03/model/action",
        {"model": "fix.walkin.intake", "ids": [wi], "method": "action_submit_for_handover"},
    )
    r = ep(
        "/p03/model/action",
        {"model": "fix.walkin.intake", "ids": [wi], "method": "action_complete_handover"},
    )
    wi_row = kw("fix.walkin.intake", "read", [[wi], ["state", "service_order_id"]])[0]
    tk_row = kw("fix.token.queue", "read", [[tk], ["service_order_id"]])[0]
    print(
        "  intake %s; order=%s; token linked=%s"
        % (wi_row["state"], bool(wi_row["service_order_id"]), bool(tk_row["service_order_id"]))
    )

    # ---------- verify ----------
    print("[verify]")
    k = ep("/p03/branch/kpis", {})
    ok("kpis payload", k and k.get("M04") is not None, str(k)[:170])

    for model in ("fix.token.queue", "fix.walkin.intake", "fix.cash.shift", "fix.counter.sale"):
        r = ep("/p03/model/records", {"model": model, "cols": [], "domain": []})
        ok("records %s" % model, not r.get("error"), r.get("count", r.get("error")))

    for report in (
        "daily_cash",
        "wait_distribution",
        "uncollected_ageing",
        "sales_category",
        "variance_register",
        "branch_league",
    ):
        r = ep("/p03/model/report", {"module": "M04", "report": report, "params": {}})
        ok(
            "report %s" % report,
            not r.get("error") and "rows" in r,
            len(r.get("rows", [])) if not r.get("error") else r.get("error"),
        )

    ok("tokens completed", completed >= 6, completed)
    ok("shift variance case recorded", any(s["variance"] for s in states), states)
    ok(
        "intake completed + order + token link",
        wi_row["state"] == "completed"
        and wi_row["service_order_id"]
        and tk_row["service_order_id"],
    )

    failed = [c for c in checks if not c[1]]
    print("\n%d checks, %d failed" % (len(checks), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
