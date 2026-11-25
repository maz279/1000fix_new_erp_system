#!/usr/bin/env python3
"""test-smoke - P02-M10-T06: one path end to end, under three minutes.

The kernel is present, so this is the REAL smoke (it was a wired-off
placeholder until the Phase-7 bring-up): against the RUNNING local Odoo
(BIND, validated below) it drives

    create customer (Bengali-first, DE-17)
      -> create device (catalogue chain: brand -> model)
      -> create service order
      -> transition the state machine (draft -> diagnostic -> estimate_sent
         -> approved -> in_repair)
      -> ASSERT the transactional outbox emitted every declared event (AS-08)
      -> ASSERT a portal login (no ACL on fix.*) is DENIED the order (the
         negative-permission check; internal ACLs grant base.group_user)

Exit codes: 0 pass, 1 assertion/runtime failure, 4 server not reachable
(never a silent green - run `tasks.ps1 -Target run` first).
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import urllib.request
from urllib.parse import urlparse

# The ONLY endpoint this smoke may talk to: the local dev Odoo. The bind is
# validated (scheme, host, port) before any request - a test client must be
# as explicit about its target boundary as a production client.
BIND = "http://127.0.0.1:8069"
ALLOWED = {("http", "127.0.0.1", 8069), ("http", "localhost", 8069)}
# FIX_SMOKE_DB lets CI (stage 5, integration) drive the clean `fix_test`
# build instead of a dev database a runner never has. Only local synthetic
# databases are accepted - the same boundary rule as BIND.
DB = os.environ.get("FIX_SMOKE_DB", "fix_dev")
if DB != "fix_dev" and not DB.startswith("fix_test"):
    sys.exit(f"test-smoke: REFUSED - FIX_SMOKE_DB={DB!r} is not fix_dev or fix_test*")
ADMIN = ("admin", "admin")

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((label, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))
    return ok


def validate_target(url: str) -> None:
    """Allowlist the request boundary: exact scheme+host+port, nothing else."""
    p = urlparse(url)
    if (p.scheme, p.hostname, p.port or 80) not in ALLOWED:
        raise ValueError(f"test-smoke: refusing non-local endpoint {url!r}")


class RpcError(RuntimeError):
    pass


class Client:
    """Minimal Odoo JSON-RPC client (stdlib only) with session cookies."""

    def __init__(self, base: str = BIND):
        self.base = base
        self.cookie = ""

    def _post(self, path: str, payload: dict) -> dict:
        validate_target(self.base + path)
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Cookie": self.cookie} if self.cookie else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:  # no redirects followed
            sc = resp.headers.get("Set-Cookie", "")
            if sc:
                self.cookie = sc.split(";")[0]
            return json.loads(resp.read())

    def login(self, db: str, login: str, password: str) -> dict:
        r = self._post(
            "/web/session/authenticate",
            {"params": {"db": db, "login": login, "password": password}},
        )
        if "error" in r:
            raise RpcError(r["error"]["data"]["message"])
        return r.get("result", {})

    def call(self, model: str, method: str, *args, **kw) -> object:
        r = self._post(
            "/web/dataset/call_kw",
            {"params": {"model": model, "method": method, "args": list(args), "kwargs": kw}},
        )
        if "error" in r:
            raise RpcError(
                r["error"]["data"].get("name", "rpc error")
                + ": "
                + r["error"]["data"].get("message", "")
            )
        return r.get("result")


def reachable() -> bool:
    validate_target(BIND + "/web/login")
    try:
        with urllib.request.urlopen(BIND + "/web/login", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def main() -> int:
    if not reachable():
        print("test-smoke: NOT-AVAILABLE - no Odoo on " + BIND)
        print("  remedy: powershell -File tooling/scripts/tasks.ps1 -Target up, then -Target run")
        return 4
    tag = f"SMOKE{secrets.randbelow(90000) + 10000}"
    print(f"test-smoke: end-to-end path (tag {tag})")

    admin = Client()
    try:
        admin.login(DB, *ADMIN)
    except Exception as e:
        print(f"  [FAIL] admin login: {e}")
        return 1

    # --- fixtures (idempotent by tag) --------------------------------------
    def first(model: str, domain: list) -> int:
        ids = admin.call(model, "search", domain, limit=1)
        if not ids:
            raise RpcError(f"no {model} row for {domain}")
        return ids[0]

    company_id = first("res.company", [])
    ou_id = first("operating.unit", [])
    bd = first("res.country", [("code", "=", "BD")])

    # one fix.entity per res.company (company_unique) - reuse or create
    existing = admin.call("fix.entity", "search", [("company_id", "=", company_id)], limit=1)
    if existing:
        entity_id = existing[0]
    else:
        entity_id = admin.call(
            "fix.entity",
            "create",
            {
                "code": tag,
                "legal_name": f"Smoke Entity {tag}",
                "company_id": company_id,
                "country_id": bd,
            },
        )
    branch_id = admin.call(
        "fix.branch",
        "create",
        {
            "code": tag[:10],
            "name": f"স্মোক ব্রাঞ্চ {tag}",
            "entity_id": entity_id,
            "operating_unit_id": ou_id,
        },
    )
    check("entity + branch ready (Bengali branch name, DE-17)", bool(branch_id))

    partner_id = admin.call(
        "res.partner", "create", {"name": f"স্মোক গ্রাহক {tag}", "phone": "01700000000"}
    )
    check("customer created (Bengali-first)", bool(partner_id))

    brand_id = admin.call("fix.brand", "create", {"name": f"SmokeBrand {tag}", "code": tag[:4]})
    model_id = admin.call(
        "fix.device.model",
        "create",
        {"name": f"SmokeModel {tag}", "brand_id": brand_id, "company_id": company_id},
    )
    device_id = admin.call(
        "fix.device",
        "create",
        {
            "serial_number": f"SMK-{tag}",
            "device_model_id": model_id,
            "company_id": company_id,
            "owner_id": partner_id,
        },
    )
    check("device created via catalogue chain (brand -> model -> device)", bool(device_id))

    order_id = admin.call(
        "fix.service.order",
        "create",
        {
            "customer_id": partner_id,
            "device_id": device_id,
            "branch_id": branch_id,
            "fault_description": "স্মোক পরীক্ষা: ডিসপ্লে ভাঙা (smoke: broken display)",
        },
    )
    check("service order created in draft", bool(order_id))

    # --- state machine (AS-06: the declared transitions are the authority;
    # write() enforces DP-01's VALID_TRANSITIONS, so the smoke drives the
    # legal path draft->intake->diagnostic->estimate_sent->awaiting_approval
    # ->approved->in_repair) -----------------------------------------------
    for state in (
        "intake",
        "diagnostic",
        "estimate_pending",
        "estimate_sent",
        "awaiting_approval",
        "approved",
        "in_repair",
    ):
        admin.call("fix.service.order", "write", [order_id], {"state": state})
        got_state = admin.call("fix.service.order", "read", [order_id], ["state"])[0]["state"]
        check(f"transition -> {state}", got_state == state, f"state={got_state}")

    # An ILLEGAL transition must be rejected (the state machine has teeth)
    rejected = False
    try:
        admin.call("fix.service.order", "write", [order_id], {"state": "draft"})
    except RpcError as e:
        rejected = "Invalid state transition" in str(e)
    check("illegal transition in_repair -> draft rejected", rejected)

    # --- transactional outbox (AS-08) ---------------------------------------
    events = admin.call(
        "fix.event.outbox",
        "search_read",
        [("aggregate", "=", "fix.service.order"), ("aggregate_id", "=", order_id)],
        ["event_type"],
    )
    got = sorted(e["event_type"] for e in events)
    expected = sorted(
        [
            "service_order.created",
            "service_order.intake",
            "service_order.diagnostic",
            "service_order.estimate_pending",
            "service_order.estimate_sent",
            "service_order.awaiting_approval",
            "service_order.approved",
            "service_order.in_repair",
        ]
    )
    check("outbox emitted every declared event", got == expected, f"got={got}")

    # --- negative permission: a portal login has NO ACL on fix.* -----------
    portal_login = f"portal-{tag}@smoke.local"
    admin.call(
        "res.users",
        "create",
        {
            "name": f"Smoke Portal {tag}",
            "login": portal_login,
            "email": portal_login,
            "password": portal_login,
            "group_ids": [first("res.groups", [("name", "=", "Portal User (P03)")])],
        },
    )
    portal = Client()
    try:
        portal.login(DB, portal_login, portal_login)
    except Exception:
        portal_ok = False
    else:
        portal_ok = True
    denied = False
    if portal_ok:
        try:
            portal.call("fix.service.order", "search", [], limit=1)
        except RpcError as e:
            denied = "AccessError" in str(e)
    check(
        "portal login denied service orders (no ACL)",
        denied,
        "AccessError raised" if denied else "NO denial - ACL gap!",
    )

    # --- seed idempotency (PP6 E4): a second seed run must REFUSE -----
    # seed.py refuses exit 2 over an already-seeded database — the TEST
    # data class enters exactly once; re-seeding is an explicit reset
    # (03-DATA-STRATEGY §1/E4)
    import subprocess
    from pathlib import Path

    seed = Path(__file__).resolve().parents[2] / "db" / "seeds" / "seed.py"
    r = subprocess.run(
        [sys.executable, str(seed), "--seed", "1000fix"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    check(
        "seed double-run refused (idempotency guard)",
        r.returncode == 2,
        f"exit={r.returncode} {r.stdout.strip()[:80]}",
    )

    failures = [r for r in RESULTS if not r[1]]
    print(f"test-smoke: {len(RESULTS) - len(failures)}/{len(RESULTS)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
