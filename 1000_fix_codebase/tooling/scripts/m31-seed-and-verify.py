#!/usr/bin/env python3
"""M31 seed + live verification on real fix_dev data.

Seed (real, derived):
  1. load the workshop/bench master data from the module's noupdate demo
     XML (never loaded — install-time noupdate files skip on upgrade)
  2. add the admin user to the workshop manager group (screens need it)
  3. bridge ~30 walk-in service orders into workshop jobs (the new bridge)
  4. auto-assign benches (the new engine), attach certified technicians
  5. walk jobs through lifecycles: L1 to ready/delivered via QC;
     one L2 through burn-in; one deliberate QC fail (NCR + rework loop)
  6. add real part lines with lot serials (genealogy)

Verify every M31 endpoint against DB truth.

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
    return call(
        "object",
        "execute_kw",
        DB,
        UID[0],
        PWD,
        model,
        method,
        args or [],
        kwargs or {},
    )


# the workshop/bench master rows from data/fix_workshop_data.xml (noupdate —
# skipped on upgrade, so they are created here if absent)
FACILITIES = [
    ("WS-TEJGAON-01", "Tejgaon Central Workshop", "central", "Dhaka"),
    ("WS-DHANMONDI-01", "Dhanmondi Regional Workshop", "regional", "Dhaka"),
    ("WS-CTG-01", "Chattogram Express Workshop", "express", "Chattogram"),
]
BENCHES = [
    ("BENCH-TEJ-L1-01", "Tejgaon Bench L1", "WS-TEJGAON-01", "l1", 2),
    ("BENCH-TEJ-L2-01", "Tejgaon Bench L2", "WS-TEJGAON-01", "l2", 1),
    ("BENCH-TEJ-L3-01", "Tejgaon Bench L3 (ESD)", "WS-TEJGAON-01", "l3", 1),
    ("BENCH-DHN-L1-01", "Dhanmondi Bench L1", "WS-DHANMONDI-01", "l1", 2),
]


def main():
    assert login(), "login failed"
    checks = []

    def ok(name, cond, detail=""):
        checks.append((name, bool(cond)))
        print(
            ("  PASS " if cond else "  FAIL ") + name + ((" :: " + str(detail)) if detail else "")
        )

    # ---------- master data ----------
    print("[seed] grant admin the workshop manager group FIRST (ACLs)")
    ws_grp = kw("res.groups", "search", [[["full_name", "ilike", "Depot Manager"]]])
    target = (ws_grp or [None])[0] if isinstance(ws_grp, list) and ws_grp else None
    if target:
        members = kw("res.groups", "read", [[target], ["user_ids"]])
        user_ids = members[0].get("user_ids", []) if isinstance(members, list) and members else []
        if UID[0] not in user_ids:
            kw("res.users", "write", [[UID[0]], {"groups_id": [(4, target)]}])
            print("  admin added to workshop group %s" % target)
            # group changes need a fresh session for live ACL checks
            COOKIE[0] = None
            assert login(), "re-login after group grant failed"

    print("[seed] workshop + bench master (from the module's noupdate data)")
    ou = kw("operating.unit", "search", [[]], {"limit": 1})
    branch_dhaka = kw("fix.branch", "search", [[["city", "ilike", "Dhaka"]]], {"limit": 1})
    branch_ctg = kw("fix.branch", "search", [[["city", "ilike", "Chattogram"]]], {"limit": 1})
    dhaka_branch_id = branch_dhaka[0] if isinstance(branch_dhaka, list) and branch_dhaka else False
    ctg_branch_id = branch_ctg[0] if isinstance(branch_ctg, list) and branch_ctg else False
    ws_ids = {}
    for code, name, wtype, city in FACILITIES:
        existing = kw("fix.workshop", "search", [[["code", "=", code]]])
        if existing:
            ws_ids[code] = existing[0]
            continue
        branch_id = dhaka_branch_id if city == "Dhaka" else ctg_branch_id
        vals = {
            "code": code,
            "name": name,
            "name_bn": name,
            "workshop_type": wtype,
            "city": city,
            "operating_unit_id": ou[0],
        }
        if branch_id:
            vals["branch_id"] = branch_id
        new_id = kw("fix.workshop", "create", [vals])
        ws_ids[code] = new_id
        print("  workshop %s created" % code)
    for code, name, ws_code, level, cap in BENCHES:
        existing = kw("fix.workshop.bench", "search", [[["code", "=", code]]])
        if existing:
            continue
        kw(
            "fix.workshop.bench",
            "create",
            [
                {
                    "code": code,
                    "name": name,
                    "name_bn": name,
                    "workshop_id": ws_ids[ws_code],
                    "repair_level": level,
                    "max_concurrent_jobs": cap,
                    "is_esd_safe": level == "l3",
                    "operating_unit_id": ou[0],
                }
            ],
        )
        print("  bench %s created" % code)

    # ---------- jobs ----------
    print("[seed] bridge walk-in orders -> workshop jobs")
    orders = kw(
        "fix.service.order",
        "search_read",
        [
            [["service_type", "=", "walk_in"], ["state", "not in", ["closed", "cancelled"]]],
            ["id", "name", "priority"],
        ],
        {"limit": 30, "order": "id asc"},
    )
    bridged = refused = 0
    for so in orders:
        res = ep(
            "/p03/model/action",
            {
                "model": "fix.service.order",
                "ids": [so["id"]],
                "method": "action_create_workshop_job",
            },
        )
        if res.get("success"):
            bridged += 1
        else:
            refused += 1
    print("  bridged %d, refused %d" % (bridged, refused))

    print("[seed] intake + diagnose + auto-bench + technician")
    drafts = kw("fix.workshop.job", "search", [[["state", "=", "draft"]]])
    if drafts:
        ep(
            "/p03/model/action",
            {"model": "fix.workshop.job", "ids": drafts[:30], "method": "action_intake"},
        )
    diag = kw("fix.workshop.job", "search", [[["state", "=", "intake"]]])
    if diag:
        ep(
            "/p03/model/action",
            {"model": "fix.workshop.job", "ids": diag[:30], "method": "action_diagnostic"},
        )
    # certified technicians (from the M22 gate holders)
    certs = kw("fix.certification", "search_read", [[], ["employee_id"]], {"limit": 6})
    tech_ids = list(
        dict.fromkeys(
            c["employee_id"][0] for c in certs if isinstance(c, dict) and c.get("employee_id")
        )
    )
    print("  certified technicians available: %d" % len(tech_ids))
    benchable = kw("fix.workshop.job", "search", [[["state", "=", "diagnostic"]]], {"limit": 8})
    assigned = 0
    for i, job_id in enumerate(benchable):
        if tech_ids:
            kw(
                "fix.workshop.job",
                "write",
                [[job_id], {"technician_id": tech_ids[i % len(tech_ids)]}],
            )
        res = ep(
            "/p03/model/action",
            {"model": "fix.workshop.job", "ids": [job_id], "method": "action_auto_assign_bench"},
        )
        if res.get("success"):
            assigned += 1
    print("  benched %d jobs" % assigned)

    print("[seed] walk lifecycles (L1 to delivered, one L2 burn-in, one QC fail)")

    # fresh rows each pass — states move under us
    def _diagnostic_benched(limit):
        return kw(
            "fix.workshop.job",
            "search_read",
            [
                [["bench_id", "!=", False], ["state", "=", "diagnostic"]],
                ["id", "repair_level"],
            ],
            {"limit": limit},
        )

    benched = _diagnostic_benched(8)
    delivered = burnin = failed = 0
    for i, job in enumerate(benched):
        jid = job["id"]
        ep(
            "/p03/model/action",
            {"model": "fix.workshop.job", "ids": [jid], "method": "action_start_repair"},
        )
        if i == 3:
            # deliberate QC fail -> NCR + rework loop
            ep(
                "/p03/model/action",
                {
                    "model": "fix.workshop.job",
                    "ids": [jid],
                    "method": "action_transition",
                    "kwargs": {"new_state": "qc_pending"},
                },
            )
            res = ep(
                "/p03/model/action",
                {
                    "model": "fix.workshop.job",
                    "ids": [jid],
                    "method": "action_fail_qc",
                    "kwargs": {"reason": "Seed: retest after flux cleanup"},
                },
            )
            if res.get("success"):
                failed += 1
            continue
        if i == 1:
            # L2 burn-in path
            kw("fix.workshop.job", "write", [[jid], {"repair_level": "l2"}])
            ep(
                "/p03/model/action",
                {"model": "fix.workshop.job", "ids": [jid], "method": "action_start_burn_in"},
            )
            r = ep(
                "/p03/model/action",
                {"model": "fix.workshop.job", "ids": [jid], "method": "action_pass_burn_in"},
            )
            if r.get("success"):
                burnin += 1
        else:
            # L1: submit to QC directly (the statusbar's own path)
            ep(
                "/p03/model/action",
                {
                    "model": "fix.workshop.job",
                    "ids": [jid],
                    "method": "action_transition",
                    "kwargs": {"new_state": "qc_pending"},
                },
            )
        res = ep(
            "/p03/model/action",
            {
                "model": "fix.workshop.job",
                "ids": [jid],
                "method": "action_pass_qc",
                "kwargs": {"notes": "Seed: QC pass"},
            },
        )
        if res.get("success"):
            ep(
                "/p03/model/action",
                {"model": "fix.workshop.job", "ids": [jid], "method": "action_deliver"},
            )
            delivered += 1
    print("  delivered %d, burn-in passed %d, QC-failed %d" % (delivered, burnin, failed))

    print("[seed] part lines with genealogy")
    job_rows = kw(
        "fix.workshop.job", "search_read", [[], ["id", "name"]], {"limit": 6, "order": "id desc"}
    )
    products = kw(
        "product.product",
        "search_read",
        [[], ["id", "default_code", "standard_price"]],
        {"limit": 3},
    )
    for i, job in enumerate(job_rows):
        if not products:
            break
        p = products[i % len(products)]
        kw(
            "fix.workshop.part.line",
            "create",
            [
                {
                    "job_id": job["id"],
                    "product_id": p["id"],
                    "quantity": 1,
                    "unit_cost": p["standard_price"],
                    "lot_serial_number": "LOT-%s-%04d" % (job["name"].split("/")[-1], i + 1),
                }
            ],
        )
    print("  %d part lines" % len(job_rows))

    # ---------- verify ----------
    print("[verify]")
    counts = {
        m: kw(m, "search_count", [[]])
        for m in (
            "fix.workshop",
            "fix.workshop.bench",
            "fix.workshop.job",
            "fix.workshop.part.line",
        )
    }
    ok("workshops exist", counts["fix.workshop"] >= 3, counts["fix.workshop"])
    ok("benches exist", counts["fix.workshop.bench"] >= 4, counts["fix.workshop.bench"])
    ok("jobs exist", counts["fix.workshop.job"] > 0, counts["fix.workshop.job"])
    ok("part lines exist", counts["fix.workshop.part.line"] > 0, counts["fix.workshop.part.line"])

    k = ep("/p03/workshop/kpis", {})
    ok("kpis payload", k and k.get("M31") is not None, str(k)[:150])

    for model in (
        "fix.workshop.job",
        "fix.workshop.bench",
        "fix.workshop",
        "fix.workshop.part.line",
        "fix.workshop.evidence",
    ):
        r = ep("/p03/model/records", {"model": model, "cols": [], "domain": []})
        ok("records %s" % model, not r.get("error"), r.get("count", r.get("error")))

    for report in (
        "bench_utilisation",
        "cycle_time",
        "rework_loops",
        "cost_per_repair",
        "parts_genealogy",
        "burn_in",
    ):
        r = ep("/p03/model/report", {"module": "M31", "report": report, "params": {}})
        ok("report %s" % report, not r.get("error") and "rows" in r, len(r.get("rows", [])))

    failed_checks = [c for c in checks if not c[1]]
    print("\n%d checks, %d failed" % (len(checks), len(failed_checks)))
    return 1 if failed_checks else 0


if __name__ == "__main__":
    raise SystemExit(main())
