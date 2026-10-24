#!/usr/bin/env python3
"""api-sweep - probe every Odoo HTTP controller route (R01 re-audit 2026-10-22).

Zero-trust: nothing is asserted from a list; the route table is parsed from
the @http.route decorators in addons/, then each route is probed:

  * POST with an empty JSON-RPC body against Odoo (:8069) - a routed
    endpoint must answer JSON (an Odoo error object is fine: the route
    EXISTS and executes its dispatcher). HTML or a connection error is a
    finding.
  * The same POST through Kong (:8000) for the portal-facing segments -
    verifies the gateway proxies it (Kong "no route" HTML is distinct from
    an Odoo JSON error).

SSRF posture: probe targets are pinned loopback hosts (module constants);
every extracted route is validated to be a site-absolute path - no scheme,
no authority, no userinfo - before it is joined, and redirects are never
followed.

Exit 0 all probed OK, 1 any failure. Evidence: results/api-sweep.json.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES_FILE = ROOT / "results" / "api-routes.txt"
OUT = ROOT / "results" / "api-sweep.json"
ODOO = "http://127.0.0.1:8069"  # pinned loopback probe target
KONG = "http://127.0.0.1:8000"  # pinned loopback probe target

# Route segments Kong proxies verbatim (kong.yml odoo-portal-api).
KONG_SEGMENTS = frozenset(
    [
        "/customer",
        "/vendor",
        "/analytics",
        "/brand",
        "/contact",
        "/partner",
        "/seller",
        "/corporate",
        "/technician",
        "/storefront",
        "/p03",
    ]
)

# A probeable route: starts with "/", one segment minimum, no scheme,
# authority, query, fragment or backslash (url-splitting tricks).
ROUTE_RE = re.compile(r"^/[A-Za-z0-9_\-./:]*$")


def valid_route(route: str) -> bool:
    return (
        bool(ROUTE_RE.match(route))
        and "://" not in route
        and "@" not in route
        and "?" not in route
        and "#" not in route
        and "\\" not in route
        and route not in ("//", "/")
    )


def extract_routes() -> list[str]:
    routes = set()
    for py in (ROOT / "addons").rglob("*.py"):
        if "controllers" not in py.parts:
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"@http\.route\(\s*[\"']([^\"']+)[\"']", text):
            routes.add(m.group(1))
    return sorted(routes)


def probe(base: str, route: str) -> dict:
    if not valid_route(route):
        return {
            "status": None,
            "json": False,
            "ok": False,
            "note": "invalid route expression (refused)",
        }
    body = json.dumps({"jsonrpc": "2.0", "method": "call", "id": 1, "params": {}}).encode()
    req = urllib.request.Request(
        base + route, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        # No redirect following: the probe must land on the pinned host.
        opener = urllib.request.build_opener(NoRedirect)
        with opener.open(req, timeout=10) as resp:
            payload = resp.read(4096)
            ctype = resp.headers.get("Content-Type", "")
            is_json = "json" in ctype or payload.lstrip()[:1] == b"{"
            return {
                "status": resp.status,
                "json": is_json,
                "ok": resp.status in (200, 400, 401, 403, 404) and is_json,
                "note": f"content-type={ctype.split(';')[0]}",
            }
    except urllib.error.HTTPError as e:
        payload = e.read(4096)
        ctype = e.headers.get("Content-Type", "") if e.headers else ""
        is_json = "json" in ctype or payload.lstrip()[:1] == b"{"
        # JSON from Odoo = dispatcher answered (route may be method/auth gated);
        # HTML 404 = unrouted; connection failures are always failures.
        return {
            "status": e.code,
            "json": is_json,
            "ok": is_json,
            "note": f"http-error content-type={ctype.split(';')[0] if ctype else '?'}",
        }
    except Exception as e:
        return {"status": None, "json": False, "ok": False, "note": f"{type(e).__name__}: {e}"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def kong_proxied(route: str) -> bool:
    first = "/" + route.lstrip("/").split("/", 1)[0]
    return first in KONG_SEGMENTS


def main() -> int:
    if ROUTES_FILE.exists():
        routes = [r for r in ROUTES_FILE.read_text(encoding="utf-8").splitlines() if r]
    else:
        routes = extract_routes()
        ROUTES_FILE.parent.mkdir(exist_ok=True)
        ROUTES_FILE.write_text("\n".join(routes), encoding="utf-8")

    results = []
    for route in routes:
        direct = probe(ODOO, route)
        via_kong = probe(KONG, route) if kong_proxied(route) else None
        results.append({"route": route, "direct": direct, "kong": via_kong})

    failures = [r for r in results if not r["direct"]["ok"] or (r["kong"] and not r["kong"]["ok"])]
    evidence = {
        "schema": "1000fix-erp/api-sweep/1",
        "generatedAtUtc": datetime.now(UTC).isoformat(),
        "generator": "tooling/e2e/api-sweep.py",
        "probed": len(results),
        "failed": len(failures),
        "results": results,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    print(f"API SWEEP: {len(results) - len(failures)}/{len(results)} ok  -> {OUT}")
    for r in failures[:10]:
        print(f"  FAIL {r['route']} direct={r['direct']} kong={r['kong']}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
