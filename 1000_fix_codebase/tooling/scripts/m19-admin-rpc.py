#!/usr/bin/env python3
"""One-off admin RPC helper for the M19 GL verification (local dev only).

Credentials come from the environment — nothing is embedded here."""

import http.client
import json
import os
import sys

HOST = "localhost"  # literal loopback host — the local dev Odoo
PORT = 8069
DB = "fix_dev"
ADMIN = os.environ.get("ODOO_ADMIN", "admin")


def call(service, method, *args, uid=None, pwd=None):
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": {
                "service": service,
                "method": method,
                "args": [DB, uid or ADMIN, pwd or ADMIN, *args],
            },
        }
    )
    conn = http.client.HTTPConnection(HOST, PORT, timeout=60)
    conn.request(
        "POST",
        "/jsonrpc",
        body=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    body = json.loads(conn.getresponse().read().decode("utf-8"))
    conn.close()
    return body.get("result", body)


if __name__ == "__main__":
    uid = call("common", "login")
    new_pwd = os.environ.get("CHECKER_PWD")
    if not new_pwd:
        sys.exit("CHECKER_PWD env var required (no credentials in source)")
    call("object", "execute_kw", "res.users", "write", [[1355], {"password": new_pwd}], uid=uid)
    print("checker password set")
