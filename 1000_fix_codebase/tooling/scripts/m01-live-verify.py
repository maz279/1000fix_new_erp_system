#!/usr/bin/env python3
"""M01 live verification on real fix_dev data: the new workspace surfaces.

1. /p03/service/kpis — the module KPI payload
2. /p03/orders/list scopes (all/wip/holds/rework/rwty) — scope-correct rows
3. /p03/model/records for every whitelisted service model
4. /p03/model/report M01 reports (channel, sla, thresholds, types, wip)
5. /p03/model/action — advance one draft order (intake → diagnostic)
6. /p03/model/action — issue a repair warranty on a delivered order

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
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "id": rid[0],
        "params": {"service": service, "method": method, "args": list(args)},
    }
    resp = _post("/jsonrpc", payload)
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
    """Call a /p03 jsonrpc CONTROLLER endpoint (session-authenticated)."""
    rid[0] += 1
    resp = _post(
        path,
        {
            "jsonrpc": "2.0",
            "method": "call",
            "id": rid[0],
            "params": params or {},
        },
    )
    if "error" in resp:
        return {"error": resp["error"].get("data", {}).get("message") or resp["error"]}
    return resp.get("result")


def main():
    assert login(), "login failed"
    checks = []

    def ok(name, cond, detail=""):
        checks.append((name, bool(cond), detail))
        print(("  PASS " if cond else "  FAIL ") + name + (" :: " + str(detail) if detail else ""))

    # 1. KPIs
    print("[1] /p03/service/kpis")
    k = ep("/p03/service/kpis")
    ok("kpis payload", k and k.get("M01") is not None, str(k)[:160])
    k1 = (k or {}).get("M01", {})
    ok("open_orders number", isinstance(k1.get("open_orders"), int), k1.get("open_orders"))

    # 2. orders/list scopes
    print("[2] /p03/orders/list scopes")
    wip_states = {
        "intake",
        "diagnostic",
        "estimate_pending",
        "estimate_sent",
        "awaiting_approval",
        "approved",
        "in_repair",
        "qc_pending",
        "qc_failed",
    }
    r = ep("/p03/orders/list", {"scope": "wip", "limit": 50})
    rows = r.get("orders", [])
    ok("wip scope returns rows", len(rows) > 0, len(rows))
    ok(
        "wip scope wip-only",
        all(o["state"] in wip_states for o in rows),
        sorted({o["state"] for o in rows}),
    )
    ok("wip rows carry age_days", all("age_days" in o for o in rows))
    r = ep("/p03/orders/list", {"scope": "rwty", "limit": 50})
    ok(
        "rwty scope delivered/closed only",
        all(o["state"] in ("delivered", "closed") for o in r.get("orders", [])),
        len(r.get("orders", [])),
    )
    r = ep("/p03/orders/list", {"scope": "holds", "limit": 50})
    ok("holds scope answers (may be empty honestly)", "orders" in r, len(r.get("orders", [])))
    r = ep("/p03/orders/list", {"scope": "rework", "limit": 50})
    ok(
        "rework scope rework-flagged",
        all(o.get("is_rework") for o in r.get("orders", [])),
        len(r.get("orders", [])),
    )

    # 3. model records
    print("[3] /p03/model/records")
    for model, minrows in [
        ("fix.token.queue", 1),
        ("fix.sla.policy", 50),
        ("fix.diagnostic.node", 10),
        ("fix.estimate", 1),
        ("fix.qc.checklist", 1),
        ("fix.warranty", 50),
        ("fix.fault.code", 20),
        ("fix.walkin.intake", 1),
        ("fix.device.history", 1),
    ]:
        r = ep("/p03/model/records", {"model": model, "cols": [], "domain": []})
        ok(
            "records %s" % model,
            not r.get("error") and r.get("count", 0) >= minrows,
            r.get("count", r.get("error")),
        )

    # 4. reports
    print("[4] /p03/model/report M01")
    for report in [
        "channel_intake",
        "sla_compliance",
        "approval_thresholds",
        "type_matrix",
        "wip_ageing",
        "estimate_funnel",
        "rework_analysis",
        "tat_distribution",
        "uncollected_register",
    ]:
        r = ep("/p03/model/report", {"module": "M01", "report": report, "params": {}})
        ok(
            "report %s" % report,
            not r.get("error") and "rows" in r,
            len(r.get("rows", [])) if not r.get("error") else r.get("error"),
        )

    # 5. advance a draft order one step (intake -> diagnostic)
    print("[5] advance one draft order")
    drafts = call(
        "object",
        "execute_kw",
        DB,
        UID[0],
        PWD,
        "fix.service.order",
        "search_read",
        [[["state", "=", "intake"]], ["id", "name", "state"]],
        {"limit": 5},
    )
    if isinstance(drafts, list) and drafts:
        d = drafts[0]
        r = ep("/p03/order/advance_stage", {"order_id": d["id"], "next_state": "diagnostic"})
        ok(
            "advance %s -> diagnostic" % d["name"],
            r.get("success") and r.get("state") == "diagnostic",
            r.get("state") or r.get("error"),
        )
    else:
        ok("no intake orders to advance (skipped)", True)

    # 6. issue a repair warranty on a delivered order without one
    print("[6] issue repair warranty")
    delivered = call(
        "object",
        "execute_kw",
        DB,
        UID[0],
        PWD,
        "fix.service.order",
        "search_read",
        [
            [["state", "in", ["delivered", "closed"]], ("service_warranty_until", "=", False)],
            ["id", "name", "state"],
        ],
        {"limit": 1},
    )
    if isinstance(delivered, list) and delivered:
        o = delivered[0]
        r = ep(
            "/p03/model/action",
            {
                "model": "fix.service.order",
                "ids": [o["id"]],
                "method": "action_issue_repair_warranty",
            },
        )
        ok("warranty issued on %s" % o["name"], r.get("success"), r.get("error"))
        rec = call(
            "object",
            "execute_kw",
            DB,
            UID[0],
            PWD,
            "fix.service.order",
            "read",
            [[o["id"]], ["service_warranty_until"]],
        )
        ok(
            "warranty_until persisted",
            bool(rec and rec[0]["service_warranty_until"]),
            rec and rec[0]["service_warranty_until"],
        )
    else:
        ok("no eligible delivered orders (skipped)", True)

    failed = [c for c in checks if not c[1]]
    print("\n%d checks, %d failed" % (len(checks), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
