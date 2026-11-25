#!/usr/bin/env python3
"""M03 seed + live verification on real fix_dev data.

Seed (real, derived — nothing synthetic):
  1. bridge pick&drop service orders into consignments (the new bridge)
  2. confirm + start transit (first custody link auto-stamped)
  3. ride the custody chain: hub scans, out-for-delivery
  4. POD-OTP deliveries on several consignments (one wrong-OTP refusal kept)
  5. one deliberately BROKEN chain (backwards scan) — the G3-05 gate evidence
  6. one reported-lost consignment
  7. riders assigned across the fleet

Verify every M03 endpoint against DB truth.

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


def scan(cons_id, step, **vals):
    v = {"consignment_id": cons_id, "step": step}
    v.update(vals)
    return kw("fix.custody.scan", "create", [v])


def main():
    assert login(), "login failed"
    checks = []

    def ok(name, cond, detail=""):
        checks.append((name, bool(cond)))
        print(
            ("  PASS " if cond else "  FAIL ") + name + ((" :: " + str(detail)) if detail else "")
        )

    # ---------- seed ----------
    print("[seed] bridge pick&drop orders -> consignments")
    orders = kw(
        "fix.service.order",
        "search_read",
        [
            [
                ["service_type", "in", ["collection", "onsite"]],
                ["state", "not in", ["closed", "cancelled"]],
            ],
            ["id"],
        ],
        {"limit": 24, "order": "id asc"},
    )
    bridged = refused = 0
    for so in orders:
        res = ep(
            "/p03/model/action",
            {
                "model": "fix.service.order",
                "ids": [so["id"]],
                "method": "action_create_consignment",
            },
        )
        if res.get("success"):
            bridged += 1
        else:
            refused += 1
    print("  bridged %d, refused %d" % (bridged, refused))

    riders = kw("hr.employee", "search", [[["active", "=", True]]], {"limit": 3})
    drafts = kw("fix.consignment", "search", [[["state", "=", "draft"]]], {"limit": 24})
    for i, cid in enumerate(drafts):
        if riders:
            kw("fix.consignment", "write", [[cid], {"rider_id": riders[i % len(riders)]}])
        ep(
            "/p03/model/action",
            {"model": "fix.consignment", "ids": [cid], "method": "action_confirm"},
        )
    print("  confirmed %d with riders" % len(drafts))

    confirmed = kw("fix.consignment", "search", [[["state", "=", "confirmed"]]], {"limit": 24})
    transit = 0
    for cid in confirmed:
        res = ep(
            "/p03/model/action",
            {"model": "fix.consignment", "ids": [cid], "method": "action_start_transit"},
        )
        if res.get("success"):
            transit += 1
    print("  in transit %d (first custody link auto-stamped)" % transit)

    in_transit = kw("fix.consignment", "search", [[["state", "=", "in_transit"]]], {"limit": 24})
    delivered = refused_otp = broken = lost = returned = 0
    for i, cid in enumerate(in_transit):
        # ride the chain: hub scan then out for delivery
        scan(cid, "hub_scan")
        scan(cid, "out_for_delivery")
        if i == 0:
            # one wrong-OTP refusal — evidence the gate refuses
            kw("fix.consignment", "write", [[cid], {"pod_otp": "111222"}])
            r = ep(
                "/p03/model/action",
                {
                    "model": "fix.consignment",
                    "ids": [cid],
                    "method": "action_verify_pod",
                    "kwargs": {"otp": "999999"},
                },
            )
            if r.get("error"):
                refused_otp += 1
        if i < 8:
            # POD-OTP deliveries
            ep(
                "/p03/model/action",
                {"model": "fix.consignment", "ids": [cid], "method": "action_generate_otp"},
            )
            otp = kw("fix.consignment", "read", [[cid], ["pod_otp"]])[0]["pod_otp"]
            r = ep(
                "/p03/model/action",
                {
                    "model": "fix.consignment",
                    "ids": [cid],
                    "method": "action_verify_pod",
                    "kwargs": {"otp": otp},
                },
            )
            if r.get("success"):
                delivered += 1
        elif i == 8:
            # deliberately BROKEN chain: backwards scan after delivery leg
            scan(cid, "hub_scan")  # backwards from out_for_delivery
            broken += 1
        elif i == 9:
            ep(
                "/p03/model/action",
                {"model": "fix.consignment", "ids": [cid], "method": "action_report_lost"},
            )
            lost += 1
        elif i == 10:
            scan(cid, "returned", exception_reason="customer absent")
            ep(
                "/p03/model/action",
                {"model": "fix.consignment", "ids": [cid], "method": "action_return"},
            )
            returned += 1
    print(
        "  POD-OTP delivered %d, wrong-OTP refused %d, broken %d, lost %d, returned %d"
        % (delivered, refused_otp, broken, lost, returned)
    )

    # ---------- verify ----------
    print("[verify]")
    counts = {
        "consignment": kw("fix.consignment", "search_count", [[]]),
        "scans": kw("fix.custody.scan", "search_count", [[]]),
    }
    ok("consignments exist", counts["consignment"] > 0, counts["consignment"])
    ok("custody scans exist", counts["scans"] > 0, counts["scans"])

    k = ep("/p03/logistics/kpis", {})
    ok("kpis payload", k and k.get("M03") is not None, str(k)[:160])

    for model in ("fix.consignment", "fix.custody.scan"):
        r = ep("/p03/model/records", {"model": model, "cols": [], "domain": []})
        ok("records %s" % model, not r.get("error"), r.get("count", r.get("error")))

    for report in (
        "cycle_time",
        "custody_exceptions",
        "courier_performance",
        "cod_settlement",
        "reverse_volume",
        "damage_claims",
    ):
        r = ep("/p03/model/report", {"module": "M03", "report": report, "params": {}})
        ok(
            "report %s" % report,
            not r.get("error") and "rows" in r,
            len(r.get("rows", [])) if not r.get("error") else r.get("error"),
        )

    broken_rows = kw("fix.consignment", "search_count", [[["chain_broken", "=", True]]])
    ok("broken chain recorded (G3-05 evidence)", broken_rows >= 1, broken_rows)
    delivered_n = kw("fix.consignment", "search_count", [[["state", "=", "delivered"]]])
    ok("POD-OTP delivered consignments", delivered_n >= 8, delivered_n)

    failed = [c for c in checks if not c[1]]
    print("\n%d checks, %d failed" % (len(checks), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
