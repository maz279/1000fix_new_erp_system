#!/usr/bin/env python3
"""Deploy the M19 GL rebuild to fix_dev: upgrade the touched modules in
dependency-safe order (cd_gl_ext engine first, the menu-edited g_finance
modules, the cd_finance_nav bridge, then cd_p03_portal), then run the chart
unification (action_link_odoo_accounts) for every company with a loaded
statutory chart.

Local deploy tool only: it talks to the local Odoo dev instance on the
literal loopback host below via http.client (no dynamic URL construction)."""

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

    # 1) upgrade modules in order
    modules = [
        "cd_gl_ext",
        "cd_subscription",
        "cd_ap_ext",
        "cd_billing_engine",
        "cd_cash_position",
        "cd_fixed_asset_ext",
        "cd_tax_engine_bd",
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

    # 2) chart unification for every company with a loaded statutory chart
    loaders = call(
        "object",
        "execute_kw",
        "fix.chart.loader",
        "search_read",
        [[]],
        {"fields": ["id", "company_id", "state"]},
    )
    print("loaders:", loaders)
    for loader in loaders:
        result = call(
            "object",
            "execute_kw",
            "fix.chart.loader",
            "action_link_odoo_accounts",
            [[loader["id"]]],
            {},
        )
        print(f"chart link for {loader['company_id'][1]}:", result)

    # 3) verify: mapped accounts + new models present
    mapped = call(
        "object",
        "execute_kw",
        "fix.chart.account",
        "search_count",
        [[("odoo_account_id", "!=", False)]],
    )
    print("mapped statutory accounts:", mapped)
    for model in ("fix.journal.template", "fix.allocation.rule", "fix.journal.posting.log"):
        count = call("object", "execute_kw", model, "search_count", [[]])
        print(f"{model}: {count} records (model live)")


if __name__ == "__main__":
    main()
