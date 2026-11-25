#!/usr/bin/env python3
"""M05 seed + live verification on real fix_dev data.

Seed (real, derived): an MSP contract on a real M08 contract, monitored
assets on real devices, telemetry-driven alerts through the collector
path, the alert→ack→ticket→resolve journey, PDPA-gated remote sessions
and a monthly report.

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
    resp = _post(path, {"jsonrpc": "2.0", "method": "call", "id": rid[0], "params": params or {}})
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

    ou = kw("operating.unit", "search", [[]], {"limit": 1})[0]

    # ---------- seed ----------
    print("[seed] MSP contract on a real M08 contract + customer")
    customer = kw("res.partner", "search", [[]], {"limit": 1, "order": "id desc"})[0]
    contract = kw(
        "fix.contract",
        "create",
        [
            {
                "name": "Seed MSP Coverage FY27",
                "customer_id": customer,
                "family": "managed",
                "operating_unit_id": ou,
                "date_start": "2026-07-01",
                "date_end": "2027-06-30",
                "annual_value": 480000.0,
            }
        ],
    )
    msp = kw(
        "fix.msp.contract",
        "create",
        [
            {
                "name": "Seed MSP — Corporate IT",
                "contract_id": contract,
                "operating_unit_id": ou,
                "device_count": 6,
                "per_device_monthly": 1500.0,
            }
        ],
    )
    print("  msp contract #%s on contract #%s" % (msp, contract))

    print("[seed] monitored assets on real devices (branch-linked for ticketing)")
    import random

    run_tag = "%04d" % random.randint(0, 9999)
    devices = kw(
        "fix.device",
        "search_read",
        [[["active", "=", True], ["branch_id", "!=", False]], ["id", "branch_id"]],
        {"limit": 6, "order": "id desc"},
    )
    agent_ids = []
    for i, d in enumerate(devices):
        agent_code = "AGT-%s-%03d" % (run_tag, i + 1)
        asset = kw(
            "fix.monitored.asset",
            "create",
            [
                {
                    "msp_contract_id": msp,
                    "agent_id": agent_code,
                    "hostname": "ws-%s-%03d" % (run_tag, i + 1),
                    "device_id": d["id"],
                }
            ],
        )
        agent_ids.append((asset, agent_code))
    print("  %d assets (run %s — agent ids unique per run)" % (len(agent_ids), run_tag))

    print("[seed] telemetry → alerts (the collector path)")
    raised = 0
    for i, (_asset, agent) in enumerate(agent_ids[:3]):
        health = "offline" if i == 0 else "degraded"
        r = kw("fix.monitored.asset", "ingest_telemetry", [], {"agent_id": agent, "health": health})
        if r:
            raised += 1
    print("  %d alerts raised via ingest_telemetry" % raised)

    print("[seed] alert journey: ack → ticket → resolve (walked explicitly)")
    # telemetry alerts may land deduped/state-dependent; the journey is proven
    # by walking ONE alert end-to-end through the whitelisted actions
    fresh = kw(
        "fix.msp.alert",
        "create",
        [
            {
                "msp_contract_id": msp,
                "asset_id": agent_ids[0][0],
                "severity": "major",
                "message": "Seed: SMART failure on %s" % agent_ids[0][1],
            }
        ],
    )
    if not isinstance(fresh, int):
        print("  fresh create error:", str(fresh)[:200])
    ep(
        "/p03/model/action",
        {"model": "fix.msp.alert", "ids": [fresh], "method": "action_acknowledge"},
    )
    ticketed_n = 0
    resolved_n = 0
    r = ep(
        "/p03/model/action",
        {"model": "fix.msp.alert", "ids": [fresh], "method": "action_to_ticket"},
    )
    if not r.get("success"):
        print("  to_ticket error:", str(r)[:200], "| fresh id:", fresh)
    if r.get("success"):
        ticketed_n += 1
        rr = ep(
            "/p03/model/action",
            {
                "model": "fix.msp.alert",
                "ids": [fresh],
                "method": "action_resolve",
                "kwargs": {"note": "Seed: drive replaced"},
            },
        )
        if rr.get("success"):
            resolved_n += 1
    # a false-positive alert resolved without ticketing (the guard permits it)
    fp = kw(
        "fix.msp.alert",
        "create",
        [
            {
                "msp_contract_id": msp,
                "asset_id": agent_ids[1][0],
                "severity": "minor",
                "message": "Seed: flapping check",
            }
        ],
    )
    r2 = ep(
        "/p03/model/action",
        {
            "model": "fix.msp.alert",
            "ids": [fp],
            "method": "action_resolve",
            "kwargs": {"note": "Seed: false positive"},
        },
    )
    if r2.get("success"):
        resolved_n += 1
    print("  ticketed %d, resolved %d (incl. one no-ticket resolve)" % (ticketed_n, resolved_n))

    print("[seed] PDPA remote sessions")
    tech = kw("hr.employee", "search", [[["active", "=", True]]], {"limit": 1})[0]
    started = ended = 0
    for i, (asset, _agent) in enumerate(agent_ids[:2]):
        sess = kw(
            "fix.remote.session",
            "create",
            [
                {
                    "msp_contract_id": msp,
                    "asset_id": asset,
                    "technician_id": tech,
                    "tool": "rustdesk",
                    "consent_captured": True,
                }
            ],
        )
        r = ep(
            "/p03/model/action",
            {"model": "fix.remote.session", "ids": [sess], "method": "action_start"},
        )
        if r.get("success"):
            started += 1
        if i == 0:
            r2 = ep(
                "/p03/model/action",
                {"model": "fix.remote.session", "ids": [sess], "method": "action_end"},
            )
            if r2.get("success"):
                ended += 1
    print("  started %d, ended %d (one left running honestly)" % (started, ended))

    print("[seed] monthly report via the contract's own engine")
    ep(
        "/p03/model/action",
        {"model": "fix.msp.contract", "ids": [msp], "method": "action_generate_monthly_report"},
    )
    reports = kw("fix.msp.service.report", "search_count", [[["msp_contract_id", "=", msp]]])
    print("  %d report(s) generated" % reports)

    # ---------- verify ----------
    print("[verify]")
    k = ep("/p03/msp/kpis", {})
    ok("kpis payload", k and k.get("M05") is not None, str(k)[:170])

    for model in (
        "fix.msp.contract",
        "fix.monitored.asset",
        "fix.msp.alert",
        "fix.remote.session",
        "fix.msp.service.report",
    ):
        r = ep("/p03/model/records", {"model": model, "cols": [], "domain": []})
        ok("records %s" % model, not r.get("error"), r.get("count", r.get("error")))

    for report in (
        "sla_by_client",
        "remote_resolution",
        "patch_compliance",
        "alert_conversion",
        "backup_log",
        "sla_credit_register",
    ):
        r = ep("/p03/model/report", {"module": "M05", "report": report, "params": {}})
        ok(
            "report %s" % report,
            not r.get("error") and "rows" in r,
            len(r.get("rows", [])) if not r.get("error") else r.get("error"),
        )

    ok("resolved alerts recorded", resolved_n >= 2, "resolved=%d" % resolved_n)
    ok("tickets created (service orders)", ticketed_n >= 1, "ticketed=%d" % ticketed_n)

    failed = [c for c in checks if not c[1]]
    print("\n%d checks, %d failed" % (len(checks), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
