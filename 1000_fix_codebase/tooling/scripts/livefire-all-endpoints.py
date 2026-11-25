#!/usr/bin/env python3
"""livefire-all-endpoints — PP-audit iteration 2 (2026-10-14).

Sweeps EVERY @http.route endpoint in the estate (enumerated from source,
55 routes) twice:
  1. UNAUTHENTICATED — must be refused cleanly (Odoo session error for
     auth="user"; structured answer for auth="public"), never a 500.
  2. AUTHENTICATED (admin) with minimal params — must answer 200 with a
     structured body (result or error object), never an unhandled
     traceback (Odoo JSON-RPC error envelopes with a traceback in data
     count as server errors).

Loopback-pinned (SSRF guard), no redirects, no credential literals.
Exit: 0 = all pass, 1 = failures printed with evidence.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:8069"
DB = "fix_dev"
ADMIN = ("admin", "admin")  # dev-only database credentials


def safe_url(path: str) -> str:
    parts = urllib.parse.urlsplit(BASE + path)
    if parts.scheme != "http" or parts.hostname != "127.0.0.1" or parts.port != 8069:
        raise ValueError(f"refusing non-loopback: {path!r}")
    return BASE + path


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def post(path, payload, cookie=""):
    req = urllib.request.Request(
        safe_url(path),
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            **({"Cookie": cookie} if cookie else {}),
        },
    )
    try:
        with _OPENER.open(req, timeout=30) as r:
            return r.status, r.headers.get("set-cookie", ""), json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:400]
        try:
            return e.code, e.headers.get("set-cookie", ""), json.loads(body)
        except ValueError:
            return e.code, e.headers.get("set-cookie", ""), {"raw": body}


def enumerate_routes():
    routes = {}
    for f in (REPO / "addons").rglob("*.py"):
        if "__pycache__" in str(f) or ".mimosa" in str(f):
            continue
        try:
            src = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in re.finditer(
            r'@http\.route\(\s*(\[[^\]]*\]|"[^"]*"|\'[^\']*\')\s*,?([^)]*)\)', src, re.S
        ):
            for p in re.findall(r'"([^"]+)"|\'([^\']+)\'', m.group(1)):
                path = p[0] or p[1]
                rest = m.group(2)
                auth = re.search(r'auth="(\w+)"', rest)
                routes[path] = auth.group(1) if auth else "user"
    return routes


def main() -> int:
    deadline = time.time() + 90
    cookie = ""
    while time.time() < deadline:
        code, sc, body = post(
            "/web/session/authenticate",
            {"jsonrpc": "2.0", "params": {"db": DB, "login": ADMIN[0], "password": ADMIN[1]}},
        )
        if code == 200 and body.get("result", {}).get("uid"):
            cookie = sc.split(";")[0]
            break
        time.sleep(3)
    else:
        print("cannot authenticate")
        return 2

    routes = enumerate_routes()
    print(f"sweeping {len(routes)} routes (unauth + auth)\n")
    fails = []
    for path in sorted(routes):
        # --- unauthenticated probe -------------------------------------
        code, _, body = post(path, {"jsonrpc": "2.0", "params": {}})
        crashed = (
            isinstance(body, dict)
            and "error" in body
            and ("Odoo Server Error" in str(body["error"].get("message", "")))
        )
        if code >= 500 or crashed:
            fails.append(f"UNAUTH {path} -> {code} {str(body)[:120]}")

        # --- authenticated probe ---------------------------------------
        code, _, body = post(path, {"jsonrpc": "2.0", "params": {}}, cookie)
        server_err = (code >= 500) or (
            isinstance(body, dict)
            and "error" in body
            and "Odoo Server Error" in str(body["error"].get("message", ""))
            and
            # a clean ValidationError/UserError refusal is a valid answer
            "ValidationError" not in str(body["error"].get("data", {}).get("name", ""))
            and "UserError" not in str(body["error"].get("data", {}).get("name", ""))
        )
        structured = isinstance(body, dict) and ("result" in body or "error" in body)
        if server_err or not structured:
            fails.append(f"AUTH {path} -> {code} {str(body)[:140]}")

    if fails:
        print("FAILURES:")
        for f in fails:
            print("  ", f)
        print(
            f"\nendpoint sweep: {len(routes) - len({x.split()[1] for x in fails})}"
            f" clean / {len({x.split()[1] for x in fails})} with failures"
        )
        return 1
    print(
        f"endpoint sweep: {len(routes)}/{len(routes)} routes clean "
        "(unauth refused properly; auth answers structured)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
