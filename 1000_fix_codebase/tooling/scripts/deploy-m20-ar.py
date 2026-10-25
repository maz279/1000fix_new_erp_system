#!/usr/bin/env python3
"""Deploy the M20 AR rebuild to fix_dev: upgrade the touched modules in
dependency-safe order (cd_gl_ext posting-log selection first, then
cd_billing_engine — the engine — the bridge, then cd_p03_portal).

Run AFTER the Odoo process on :8069 has been restarted (no dev-mode Python
reload: a stale process serves the old model registry and the upgrade of
cd_billing_engine fails with 'Invalid model name fix.billable.event').

Local deploy tool only: talks to the local Odoo dev instance on the literal
loopback host via http.client (no dynamic URL construction)."""

import http.client
import json
import os

HOST = "localhost"  # literal loopback host — the local dev Odoo
PORT = 8069
DB = "fix_dev"
USER = "admin"
PWD = os.environ.get("ODOO_RPC_PWD", "admin")  # local dev default; env overrides

_req_id = [0]
_UID = [None]


def call(service, method, *args):
    _req_id[0] += 1
    uid = _UID[0] if service == "object" else USER
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "call",
            "id": _req_id[0],
            "params": {
                "service": service,
                "method": method,
                "args": [DB, uid, PWD, *args],
            },
        }
    )
    conn = http.client.HTTPConnection(HOST, PORT, timeout=600)
    try:
        conn.request(
            "POST",
            "/jsonrpc",
            body=payload.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        resp = conn.getresponse()
        body = json.loads(resp.read().decode("utf-8"))
    finally:
        conn.close()
    if "error" in body:
        raise RuntimeError(json.dumps(body["error"])[:600])
    return body["result"]


def main():
    uid = call("common", "login")
    _UID[0] = uid
    print("login uid:", uid)

    modules = [
        "cd_gl_ext",
        "cd_billing_engine",
        "cd_finance_nav",
        "cd_p03_portal",
    ]
    for mod in modules:
        recs = call(
            "object",
            "execute_kw",
            "ir.module.module",
            "search_read",
            [[("name", "=", mod)]],
            {"fields": ["name", "state", "latest_version"]},
        )
        if not recs:
            print(f"{mod}: NOT FOUND")
            continue
        rec = recs[0]
        print(f"{mod}: {rec['state']} @ {rec['latest_version']}")
        if rec["state"] in ("installed", "to upgrade"):
            call(
                "object",
                "execute_kw",
                "ir.module.module",
                "button_immediate_upgrade",
                [[rec["id"]]],
                {},
            )
            print(f"{mod}: upgraded")

    # 2) verify the new models registered and the AR chart resolves
    for model in (
        "fix.billable.event",
        "fix.ar.receipt",
        "fix.ar.allocation",
        "fix.credit.profile",
        "fix.ar.dispute",
        "fix.ar.aging.snapshot",
        "fix.ar.payment.link",
    ):
        fields = call("object", "execute_kw", model, "fields_get", [[]], {"attributes": ["string"]})
        print(f"{model}: OK ({len(fields)} fields)")

    companies = call(
        "object", "execute_kw", "res.company", "search_read", [[]], {"fields": ["name"]}
    )
    print("companies:", [c["name"] for c in companies])

    print("deploy-m20-ar: DONE")


if __name__ == "__main__":
    main()
