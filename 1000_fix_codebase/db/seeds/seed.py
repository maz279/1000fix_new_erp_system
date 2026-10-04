#!/usr/bin/env python3
"""seed.py - deterministic synthetic data (P02-M06-T08/T09/T10, DE-12/16/17).

SYNTHETIC DATA ONLY - a developer workstation never holds production data,
masked or otherwise (DE-12). Bengali-first (DE-17: an interface that has only
ever been seen with English data hides its layout defects until UAT).
State-complete (DE-16): service orders are spread across EVERY state of the
declared machine - including on-hold-path states nobody tests otherwise.

Volumes follow db/seeds/MANIFEST.md (BE-001 section 6.5):
    5 branches | ~25 users | 200 customers | 500 devices |
    300 service orders (all 14 states) | 400 products | 60 SLAs

Runs against the LOCAL dev Odoo only (bind allowlisted, same boundary rule
as test-smoke). Deterministic for a given --seed value. Refuses to run over
an already-seeded database (exit 2) - re-seed with -Target reset.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import urllib.request
from urllib.parse import urlparse

BIND = "http://127.0.0.1:8069"
ALLOWED = {("http", "127.0.0.1", 8069), ("http", "localhost", 8069)}
DB = "fix_dev"
ADMIN = ("admin", "admin")

BRANCHES = [  # (code, bn, en) - the five cities of BE-001 6.5
    ("DHK", "ঢাকা", "Dhaka"), ("CTG", "চট্টগ্রাম", "Chattogram"),
    ("SYL", "সিলেট", "Sylhet"), ("KHL", "খুলনা", "Khulna"),
    ("RAJ", "রাজশাহী", "Rajshahi"),
]
GIVEN = ["রাহাত", "তানিয়া", "সাব্বির", "নুসরাত", "ইমরান", "মেহেদী", "ফারিয়া",
         "আরিফ", "সাদিয়া", "হাসিব", "জান্নাত", "রুবেল", "শারমিন", "নাজমুল",
         "তাসনিম", "শাকিল", "মৌসুমী", "রিফাত", "অনন্যা", "সাজ্জাদ"]
FAMILY = ["হোসেন", "আহমেদ", "রহমান", "চৌধুরী", "ইসলাম", "করিম", "মাহমুদ",
          "সুলতানা", "বেগম", "তালুকদার", "হক", "মির্জা", "সরকার", "দাস"]
FAULTS = ["ডিসপ্লে ভাঙা", "ব্যাটারি নষ্ট", "চার্জিং সমস্যা", "ওয়াটার ড্যামেজ",
          "সফটওয়্যার হ্যাং", "স্পিকার নষ্ট", "ক্যামেরা ঝাপসা", "কীপ্যাড কাজ করছে না"]
BRANDS = [("SAMS", "Samsung"), ("APPL", "Apple"), ("XIAO", "Xiaomi"),
          ("REAL", "Realme"), ("OPPO", "Oppo"), ("VIVO", "Vivo"), ("HUA", "Huawei")]
MODELS = ["Galaxy A55", "iPhone 14", "Redmi Note 13", "Narzo 70", "Reno 11",
          "V30e", "Nova 12", "Galaxy S24", "iPhone 13", "Redmi 13C"]

# Legal order states in walk order (DP-01 VALID_TRANSITIONS); index = depth
PATH = ["intake", "diagnostic", "estimate_pending", "estimate_sent",
        "awaiting_approval", "approved", "in_repair", "qc_pending"]
ALL_TARGETS = ["draft", *PATH, "qc_failed", "ready", "delivered", "closed", "cancelled"]

WS_GROUPS = ["Workspace: Service Intake (Front Desk)", "Workspace: Service Orders",
             "Workspace: Party Master", "Workspace: Device Registry",
             "Workspace: Catalogue", "Workspace: Administration"]


def validate_target(url: str) -> None:
    p = urlparse(url)
    if (p.scheme, p.hostname, p.port or 80) not in ALLOWED:
        raise ValueError(f"seed: refusing non-local endpoint {url!r}")


class Client:
    def __init__(self) -> None:
        self.cookie = ""

    def _post(self, path: str, payload: dict) -> dict:
        validate_target(BIND + path)
        req = urllib.request.Request(
            BIND + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     **({"Cookie": self.cookie} if self.cookie else {})})
        with urllib.request.urlopen(req, timeout=300) as resp:
            sc = resp.headers.get("Set-Cookie", "")
            if sc:
                self.cookie = sc.split(";")[0]
            return json.loads(resp.read())

    def login(self, db: str, login: str, password: str) -> None:
        r = self._post("/web/session/authenticate", {"params": {
            "db": db, "login": login, "password": password}})
        if "error" in r:
            raise SystemExit(f"seed: admin login failed: {r['error']['data']['message']}")

    def call(self, model: str, method: str, *args, **kw):
        r = self._post("/web/dataset/call_kw", {"params": {
            "model": model, "method": method, "args": list(args), "kwargs": kw}})
        if "error" in r:
            msg = r["error"]["data"].get("message", str(r["error"]["data"]))
            raise RuntimeError(f"{model}.{method}: {msg}")
        return r.get("result")

    def first(self, model: str, domain: list):
        ids = self.call(model, "search", domain, limit=1)
        return ids[0] if ids else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="1000fix", help="fixed random seed (DE-12)")
    ap.add_argument("--force", action="store_true",
                    help="seed even if orders already exist (appends)")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    c = Client()
    try:
        c.login(DB, *ADMIN)
    except Exception as e:
        print(f"seed: NOT-AVAILABLE - no Odoo on {BIND} ({e})")
        print("  remedy: tasks.ps1 -Target up, then -Target run")
        return 4

    if c.call("fix.service.order", "search_count", []) and not args.force:
        print("seed: REFUSED - fix.service.order already has rows (DE-12: never mix).")
        print("  re-seed from scratch: tasks.ps1 -Target reset (drops the volume), or --force to append.")
        return 2

    def purge_seed_rows() -> None:
        """--force reruns must be DETERMINISTIC: wipe this seed's own rows
        (children before parents) so a crashed half-seed never skews volumes."""
        for model, domain in (
                ("fix.service.order", [("fault_description", "in", FAULTS)]),
                ("fix.device", [("serial_number", "like", "SEED-D%")]),
                ("fix.catalogue.item", [("product_tmpl_id.name", "like", "মেরামত সেবা%")]),
                ("product.template", [("name", "like", "মেরামত সেবা%")]),
                ("fix.device.model", [("name", "like", "SmokeModel%")]),
                ("fix.sla.policy", [("code", "like", "SEEDSLA%")]),
                ("res.partner", [("email", "like", "seed.customer%@example.local")]),
                ("res.users", [("login", "like", "seed.user%@1000fix.local")]),
                ("fix.branch", [("code", "in", [b[0] for b in BRANCHES])]),
                ("fix.brand", [("code", "in", [b[0] for b in BRANDS])]),
        ):
            ids = c.call(model, "search", domain)
            if ids:
                try:
                    c.call(model, "unlink", ids)
                except RuntimeError as e:
                    print(f"seed: purge skipped {model}: {e}")

    if args.force:
        purge_seed_rows()

    company = c.first("res.company", [])
    ou = c.first("operating.unit", [])
    bd = c.first("res.country", [("code", "=", "BD")])
    entity = c.first("fix.entity", [("company_id", "=", company)])
    if not entity:
        entity = c.call("fix.entity", "create", {
            "code": "SEED", "legal_name": "1000FiX Services Ltd (Seed)",
            "company_id": company, "country_id": bd})

    # 5 branches (config rows: perm_unlink=0 by design - reuse by code) -----
    branch_ids = []
    for code, bn, en in BRANCHES:
        existing = c.first("fix.branch", [("code", "=", code),
                                          ("entity_id", "=", entity)])
        branch_ids.append(existing or c.call("fix.branch", "create", {
            "code": code, "name": f"{bn} শাখা ({en})", "entity_id": entity,
            "operating_unit_id": ou}))
    print("seed: 5 branches ready")

    # ~25 users across the workspace groups (reuse by login) -----------------
    group_ids = [g for g in (c.first("res.groups", [("name", "=", n)])
                             for n in WS_GROUPS) if g]
    new_users = []
    for i in range(25):
        login = f"seed.user{i + 1:02d}@1000fix.local"
        if c.first("res.users", [("login", "=", login)]):
            continue
        given, family = rng.choice(GIVEN), rng.choice(FAMILY)
        new_users.append({"name": f"{given} {family}", "login": login,
                          "email": login, "password": login,
                          "group_ids": [group_ids[i % len(group_ids)]] if group_ids else []})
    if new_users:
        c.call("res.users", "create", new_users)
    print(f"seed: 25 users across {len(group_ids)} workspace groups (created {len(new_users)})")

    # 200 customers (Bengali-first) ------------------------------------------
    c.call("res.partner", "create", [
        {"name": f"{rng.choice(GIVEN)} {rng.choice(FAMILY)}",
         "phone": f"01{rng.randint(3, 9)}{rng.randint(10000000, 99999999)}",
         "email": f"seed.customer{i + 1:03d}@example.local"}
        for i in range(200)])
    customers = c.call("res.partner", "search",
                       [("email", "like", "seed.customer%")], limit=200)
    print(f"seed: {len(customers)} customers")

    # 400 products: brands -> models -> products+catalogue items (reuse by key)
    brand_ids = []
    for code, name in BRANDS:
        brand_ids.append(c.first("fix.brand", [("code", "=", code)]) or
                         c.call("fix.brand", "create", {"code": code, "name": name}))
    have_models = c.call("fix.device.model", "search",
                         [("name", "like", "%"), ("company_id", "=", company)],
                         limit=40)
    if len(have_models) >= 40:
        model_ids = have_models[:40]
    else:
        model_ids = c.call("fix.device.model", "create", [
            {"name": rng.choice(MODELS) + f" {i}", "brand_id": rng.choice(brand_ids),
             "company_id": company} for i in range(40 - len(have_models))]) + have_models
    tmpl_ids = c.call("product.template", "create", [
        {"name": f"মেরামত সেবা {rng.choice(FAULTS)} {i}",
         "list_price": round(rng.uniform(300, 8000), 2),
         "type": "service"} for i in range(400)])
    c.call("fix.catalogue.item", "create", [
        {"product_tmpl_id": t, "company_id": company} for t in tmpl_ids])
    print(f"seed: 400 products + catalogue items")

    # 500 devices across models and warranty states (serial is unique: reuse) --
    existing_devices = c.call("fix.device", "search",
                              [("serial_number", "like", "SEED-D%")], limit=500)
    need = 500 - len(existing_devices)
    device_ids = existing_devices + (c.call("fix.device", "create", [
        {"serial_number": f"SEED-D{i:05d}",
         "device_model_id": rng.choice(model_ids), "company_id": company,
         "owner_id": rng.choice(customers),
         "warranty_status": rng.choice(
             ["in_warranty", "out_of_warranty", "extended", "unknown"])}
        for i in range(need)]) if need > 0 else [])
    print(f"seed: {len(device_ids)} devices")

    # 60 SLA policies (reuse by unique code) ----------------------------------
    sla_vals = []
    for i in range(60):
        code = f"SEEDSLA{i + 1:03d}"[:16]
        if c.first("fix.sla.policy", [("code", "=", code)]):
            continue
        pri = rng.choice(["normal", "high", "urgent", "emergency"])
        sla_vals.append({
            "code": code,
            "name": f"SLA {pri} {BRANCHES[i % 5][2]}",
            "service_type": rng.choice(["walk_in", "collection", "onsite", "mail_in"]),
            "priority": pri, "company_id": company,
            "response_hours": rng.choice([4, 8, 12, 24]),
            "resolution_hours": rng.choice([24, 48, 72, 120])})
    c.call("fix.sla.policy", "create", sla_vals)
    print("seed: 60 SLA policies")

    # 300 service orders, state-complete (DE-16). Idempotent over crashed
    # partial runs: existing seed orders (fault text is the marker) are kept,
    # pinned to whatever state they already reached; fresh orders are created
    # only for the states still short of their quota.
    per_state = {t: 300 // len(ALL_TARGETS) for t in ALL_TARGETS}
    existing = c.call("fix.service.order", "search_read",
                      [("fault_description", "in", FAULTS)], ["state"])
    orders: list[dict] = []
    order_ids: list[int] = [r["id"] for r in existing]
    taken: dict[str, int] = {}
    for r in existing:  # an order already AT a state satisfies that quota
        taken[r["state"]] = taken.get(r["state"], 0) + 1
    i = 0
    for target in ALL_TARGETS:
        for _ in range(per_state[target] - taken.get(target, 0)):
            orders.append({"target": target, "vals": {
                "customer_id": rng.choice(customers),
                "device_id": device_ids[i % len(device_ids)],
                "branch_id": branch_ids[i % len(branch_ids)],
                "fault_description": rng.choice(FAULTS)}})
            i += 1
    if orders:
        order_ids += c.call("fix.service.order", "create", [o["vals"] for o in orders])
    targets_all = ([r["state"] for r in existing] +
                   [o["target"] for o in orders])

    # Advance every order from its CURRENT state to its target along the
    # LEGAL path (BFS over DP-01's VALID_TRANSITIONS) - batched per hop, so
    # a crashed partial run is resumed, never invalidated. OFFLINE map is
    # mirrored from the model (single authority): draft->intake->...->
    # qc_pending->{ready,qc_failed}; ready->delivered->closed.
    SUCC = {
        "draft": ["intake"], "intake": ["diagnostic", "cancelled"],
        "diagnostic": ["estimate_pending", "cancelled"],
        "estimate_pending": ["estimate_sent", "cancelled"],
        "estimate_sent": ["awaiting_approval", "cancelled"],
        "awaiting_approval": ["approved", "cancelled"],
        "approved": ["in_repair", "cancelled"], "in_repair": ["qc_pending", "cancelled"],
        "qc_pending": ["ready", "qc_failed"], "qc_failed": ["in_repair"],
        "ready": ["delivered"], "delivered": ["closed"],
        "closed": [], "cancelled": [],
    }

    def path_to(src: str, dst: str) -> list[str]:
        # BFS shortest legal path src->dst (excluding src)
        if src == dst:
            return []
        seen, queue = {src}, [(src, [])]
        while queue:
            cur, p = queue.pop(0)
            for nxt in SUCC.get(cur, ()):
                if nxt == dst:
                    return p + [nxt]
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, p + [nxt]))
        raise RuntimeError(f"no legal path {src} -> {dst}")

    # zip(order_ids, targets_all): id -> its assigned target state
    for target in ALL_TARGETS:
        ids = [oid for oid, t in zip(order_ids, targets_all) if t == target]
        if not ids:
            continue
        states = {rec["id"]: rec["state"] for rec in c.call(
            "fix.service.order", "read", ids, ["state"])}
        # group orders with the same current state; batch each hop
        by_state: dict[str, list[int]] = {}
        for oid in ids:
            by_state.setdefault(states[oid], []).append(oid)
        for cur, group in by_state.items():
            for nxt in path_to(cur, target):
                c.call("fix.service.order", "write", group, {"state": nxt})

    counts = {}
    for t in ALL_TARGETS:
        counts[t] = c.call("fix.service.order", "search_count",
                           [("state", "=", t)])
    print(f"seed: 300 service orders, state-complete: {counts}")
    outbox = c.call("fix.event.outbox", "search_count", [])
    print(f"seed: outbox carries {outbox} events (AS-08) - dispatcher drain is a separate step")

    # --- Phase 8 estate: employment contracts, roster, attendance, payroll,
    # certifications, NCRs, MSP contracts (P08 seed extension).
    # IDEMPOTENT: every block searches before creating (a --force rerun
    # must be deterministic, never duplicating — the Phase 1-7 pattern).
    import datetime as _dt

    hr_employees = c.call("hr.employee", "search", [], limit=30)
    if not hr_employees:
        print("seed: no hr.employees found — skip Phase 8 estate (bootstrap W1 master first)")
    else:
        # 25 employment contracts (search-before-create per employee+date)
        contracts = []
        for i, emp in enumerate(hr_employees[:25]):
            joining = str(_dt.date(2015 + (i % 10), (i % 12) + 1, (i % 28) + 1))
            existing = c.first("fix.employment.contract", [
                ("employee_id", "=", emp), ("joining_date", "=", joining)])
            if existing:
                continue
            contracts.append({
                "employee_id": emp,
                "contract_type": rng.choice(["permanent", "probation", "fixed_term"]),
                "joining_date": joining,
                "basic_monthly": rng.choice([15000, 20000, 25000, 30000, 40000, 50000, 60000]),
                "weekly_hours": 48,
                "state": "active",
            })
        if contracts:
            c.call("fix.employment.contract", "create", contracts)
        print(f"seed: {len(contracts)} employment contracts created (idempotent)")

        # Leave types (statutory catalogue)
        leave_types = []
        for code, name, days, enc in [
            ("annual", "Annual Leave", 20, True),
            ("sick", "Sick Leave", 14, False),
            ("festival", "Festival Leave", 11, False),
            ("maternity", "Maternity Leave", 112, False),
        ]:
            existing = c.first("fix.leave.type", [("code", "=", code)])
            if not existing:
                leave_types.append({"code": code, "name": name,
                                    "name_bn": name, "entitlement_days": days,
                                    "encashable": enc,
                                    "maternity": code == "maternity"})
        if leave_types:
            c.call("fix.leave.type", "create", leave_types)
        print("seed: statutory leave types (annual/sick/festival/maternity)")

        # 30 leave requests (idempotent: per employee+type+date_from)
        lt_ids = c.call("fix.leave.type", "search", [], limit=4)
        created_leave = 0
        for i in range(30):
            emp = hr_employees[i % len(hr_employees)]
            lt = lt_ids[i % len(lt_ids)]
            df = str(_dt.date(2026, 11, (i % 28) + 1))
            existing = c.first("fix.leave.request", [
                ("employee_id", "=", emp), ("leave_type_id", "=", lt),
                ("date_from", "=", df)])
            if existing:
                continue
            c.call("fix.leave.request", "create", {
                "employee_id": emp,
                "leave_type_id": lt,
                "date_from": df,
                "date_to": str(_dt.date(2026, 11, (i % 28) + 1 + (i % 3))),
                "state": rng.choice(["draft", "submitted", "approved"]),
            })
            created_leave += 1
        print(f"seed: {created_leave} leave requests created (idempotent)")

        # 5 shift templates + 200 roster slots (the roster that closes M02->M55)
        shifts = []
        for name, start, end in [("Morning", 9.0, 17.0), ("Day", 10.0, 18.0),
                                  ("Evening", 14.0, 22.0), ("Night", 22.0, 6.0),
                                  ("Split", 9.0, 13.0)]:
            existing = c.first("fix.shift.template", [("name", "=", name)])
            if not existing:
                shifts.append({"name": name, "start_hour": start, "end_hour": end})
        if shifts:
            c.call("fix.shift.template", "create", shifts)
        shift_ids = c.call("fix.shift.template", "search", [], limit=5)
        roster = []
        for day_offset in range(5):
            d = _dt.date(2026, 10, 5 + day_offset)  # Mon-Fri of a working week
            for emp in hr_employees[:40]:
                # idempotent: per employee+date
                existing = c.first("fix.roster.slot", [
                    ("employee_id", "=", emp), ("date", "=", str(d))])
                if existing:
                    continue
                roster.append({
                    "employee_id": emp,
                    "date": str(d),
                    "shift_id": shift_ids[day_offset % len(shift_ids)],
                    "on_leave": rng.random() < 0.05,
                })
        if roster:
            c.call("fix.roster.slot", "create", roster)
        print(f"seed: {len(roster)} roster slots created (idempotent)")

        # 100 attendance records
        created_att = 0
        for i in range(100):
            emp = hr_employees[i % len(hr_employees)]
            check_in = _dt.datetime(2026, 10, 5, 9, 0) + _dt.timedelta(hours=i % 8)
            ci_str = check_in.strftime("%Y-%m-%d %H:%M:%S")
            if c.first("fix.attendance.record", [
                    ("employee_id", "=", emp), ("check_in", "=", ci_str)]):
                continue
            c.call("fix.attendance.record", "create", {
                "employee_id": emp,
                "check_in": ci_str,
                "check_out": (check_in + _dt.timedelta(hours=8 + (i % 3))).strftime("%Y-%m-%d %H:%M:%S"),
                "source": rng.choice(["biometric", "mobile", "manual"]),
                "device_ref": f"SEED-DEV-{i:03d}",
            })
            created_att += 1
        print(f"seed: {created_att} attendance records created (idempotent)")

        # One attendance lock for September 2026 (the payroll gate)
        lock = c.first("fix.attendance.lock", [("name", "=", "2026-09")])
        if not lock:
            lock = c.call("fix.attendance.lock", "create", {
                "name": "2026-09",
                "period_start": "2026-09-01",
                "period_end": "2026-09-30",
            })
        print("seed: attendance lock for 2026-09 (the payroll cycle's gate)")

        # Competencies + certifications (the dispatch eligibility engine)
        comps = []
        for code, name, dev in [
            ("SMP", "Smartphone Repair", "smartphone"),
            ("LAP", "Laptop Repair", "laptop"),
            ("APP", "Home Appliance Repair", "home_appliance"),
            ("NET", "Network Diagnostics", None),
        ]:
            existing = c.first("fix.competency", [("code", "=", code)])
            if not existing:
                comps.append({"code": code, "name": name,
                              "name_bn": name, "device_type": dev})
        if comps:
            c.call("fix.competency", "create", comps)
        comp_ids = c.call("fix.competency", "search", [], limit=4)
        certs = []
        for i, emp in enumerate(hr_employees[:30]):
            comp = comp_ids[i % len(comp_ids)]
            existing = c.first("fix.certification", [
                ("employee_id", "=", emp), ("competency_id", "=", comp),
                ("issued_on", "=", str(_dt.date(2025, 1, 15)))])
            if existing:
                continue
            certs.append({
                "employee_id": emp,
                "competency_id": comp,
                "issued_on": str(_dt.date(2025, 1, 15)),
                "expires_on": str(_dt.date(2027, 1, 15)),
            })
        if certs:
            c.call("fix.certification", "create", certs)
        print(f"seed: {len(certs)} certifications created (idempotent)")

        # One payroll period + payslips for September (Journey 13 exercised)
        period = c.first("fix.payroll.period", [("name", "=", "2026-09")])
        if not period:
            period = c.call("fix.payroll.period", "create", {
                "name": "2026-09",
                "period_start": "2026-09-01",
                "period_end": "2026-09-30",
                "state": "attendance_locked",
            })
            created_slips = 0
            for emp in hr_employees[:25]:
                if c.first("fix.payslip", [("period_id", "=", period),
                                           ("employee_id", "=", emp)]):
                    continue
                c.call("fix.payslip", "create", {
                    "period_id": period,
                    "employee_id": emp,
                    "basic": rng.choice([15000, 20000, 30000, 50000]),
                    "ot_hours": rng.choice([0, 5, 10, 20]),
                    "incentive": rng.choice([0, 500, 1500, 3000]),
                    "pf_employee_pct": 10.0,
                    "pf_employer_pct": 10.0,
                })
                created_slips += 1
            if created_slips:
                c.call("fix.payroll.period", "write", [period],
                       {"state": "calculated"})
        print(f"seed: payroll period + payslips (idempotent)")

        # 20 NCRs (idempotent: deterministic description per index)
        ncrs = []
        NCR_CAUSES = ['process deviation', 'equipment fault',
                      'documentation gap', 'training gap']
        for i in range(20):
            desc = f"Seed NCR {i+1}: {NCR_CAUSES[i % len(NCR_CAUSES)]}"
            existing = c.first("fix.ncr", [("description", "=", desc)])
            if existing:
                continue
            ncrs.append({
                "source": rng.choice(["service_order", "qc", "complaint", "audit"]),
                "severity": rng.choice(["minor", "major", "critical"]),
                "description": desc,
                "state": rng.choice(["new", "root_cause", "capa_open", "closed"]),
            })
        if ncrs:
            c.call("fix.ncr", "create", ncrs)
        print(f"seed: {len(ncrs)} NCRs created (idempotent)")

        # MSP: create a base contract first if none, then MSP + assets
        contract = c.first("fix.contract", [("name", "=", "Seed MSP Base Contract")])
        if not contract:
            customers = c.call("res.partner", "search",
                               [("email", "like", "seed.customer%")], limit=1)
            ous = c.call("operating.unit", "search", [], limit=1)
            if customers and ous:
                try:
                    contract = c.call("fix.contract", "create", {
                        "name": "Seed MSP Base Contract",
                        "customer_id": customers[0],
                        "operating_unit_id": ous[0],
                        "family": "amc",
                        "date_start": "2026-01-01",
                        "date_end": "2027-12-31",
                        "annual_value": 120000.0,
                        "state": "active",
                    })
                except RuntimeError as e:
                    print(f"seed: fix.contract creation failed: {e}")
        msp_contract = c.first("fix.msp.contract", [("name", "=", "Seed MSP")])
        if not msp_contract and contract:
            msp_contract = c.call("fix.msp.contract", "create", {
                "name": "Seed MSP",
                "contract_id": contract,
                "monitoring_scope": "endpoints",
                "per_device_monthly": 500.0,
            })
        if msp_contract:
            for i in range(10):
                agent = f"SEED-AGENT-{i:03d}"
                if c.first("fix.monitored.asset", [("agent_id", "=", agent)]):
                    continue
                c.call("fix.monitored.asset", "create", {
                    "msp_contract_id": msp_contract,
                    "agent_id": agent,
                    "hostname": f"seed-workstation-{i:03d}",
                    "health": rng.choice(["healthy", "degraded", "offline"]),
                })
            print("seed: 1 MSP contract + 10 monitored assets (idempotent)")
        else:
            print("seed: no fix.contract could be created — skip MSP")

        # --- Phase 9 estate: rental, trade-in, data cases, demand plans,
        # budgets, HSE, knowledge, ITSM, risk, talent (idempotent) --------
        devices = c.call("fix.device", "search", [], limit=10)
        if devices:
            for i in range(5):
                rname = f"SEED-RENT-{i+1:03d}"
                if not c.first("fix.rental.reservation", [("name", "=", rname)]):
                    c.call("fix.rental.reservation", "create", {
                        "name": rname,
                        "customer_id": customers[0] if customers else 1,
                        "device_id": devices[i % len(devices)],
                        "date_from": "2026-10-01",
                        "date_to": "2026-10-15",
                        "daily_rate": rng.choice([500, 800, 1200]),
                        "deposit_collected": rng.choice([2000, 5000]),
                        "state": "active",
                    })
            print("seed: rental reservations (idempotent)")

            for i in range(5):
                tname = f"SEED-TRD-{i+1:03d}"
                if not c.first("fix.tradein.request", [("name", "=", tname)]):
                    c.call("fix.tradein.request", "create", {
                        "name": tname,
                        "customer_id": customers[1] if len(customers) > 1 else 1,
                        "device_id": devices[i % len(devices)],
                        "offered_value": rng.choice([3000, 8000, 15000]),
                        "state": rng.choice(["offered", "accepted", "wiped"]),
                    })
            print("seed: trade-in requests (idempotent)")

        for i in range(3):
            dname = f"SEED-DRC-{i+1:03d}"
            if not c.first("fix.data.recovery.case", [("name", "=", dname)]):
                c.call("fix.data.recovery.case", "create", {
                    "name": dname,
                    "customer_id": customers[2] if len(customers) > 2 else 1,
                    "media_type": rng.choice(["hdd", "ssd", "phone"]),
                    "residency_zone": "z4",
                    "state": "custody",
                })
        print("seed: data recovery cases (idempotent)")

        products = c.call("product.template", "search", [], limit=10)
        for i in range(5):
            pname = f"SEED-DEMAND-{i+1:03d}"
            if not c.first("fix.demand.plan", [("name", "=", pname)]):
                c.call("fix.demand.plan", "create", {
                    "name": pname,
                    "period_start": "2026-11-01",
                    "period_end": "2026-11-30",
                    "product_id": products[i] if products else 1,
                    "forecast_quantity": rng.randint(20, 100),
                    "current_stock": rng.randint(5, 50),
                    "reorder_point": 10,
                })
        print("seed: demand plans (idempotent)")

        for i in range(3):
            bname = f"SEED-BUDGET-FY2027-{i+1}"
            if not c.first("fix.budget", [("name", "=", bname)]):
                c.call("fix.budget", "create", {
                    "name": bname,
                    "fiscal_year": "2027",
                    "planned_amount": rng.choice([500000, 1000000, 2000000]),
                })
        print("seed: budgets (idempotent)")

        for i in range(5):
            hname = f"SEED-HSE-{i+1:03d}"
            if not c.first("fix.hse.incident", [("name", "=", hname)]):
                c.call("fix.hse.incident", "create", {
                    "name": hname,
                    "incident_type": rng.choice(["injury", "near_miss", "fire"]),
                    "severity": rng.choice(["low", "medium", "high"]),
                    "description": f"Seed HSE incident {i+1}",
                })
        print("seed: HSE incidents (idempotent)")

        for i in range(5):
            kname = f"Seed KB Article {i+1}"
            if not c.first("fix.knowledge.article", [("name", "=", kname)]):
                c.call("fix.knowledge.article", "create", {
                    "name": kname,
                    "category": rng.choice(["troubleshooting", "repair_procedure",
                                            "device_guide"]),
                    "content": f"<p>Seed knowledge article {i+1}</p>",
                    "state": "published",
                })
        print("seed: knowledge articles (idempotent)")

        for i in range(5):
            iname = f"SEED-ITSM-{i+1:03d}"
            if not c.first("fix.itsm.ticket", [("name", "=", iname)]):
                c.call("fix.itsm.ticket", "create", {
                    "name": iname,
                    "title": f"Seed ITSM ticket {i+1}",
                    "requester_id": hr_employees[i] if hr_employees else 1,
                    "category": rng.choice(["hardware", "software", "network"]),
                    "priority": rng.choice(["low", "medium", "high"]),
                    "description": f"Seed ITSM issue {i+1}",
                })
        print("seed: ITSM tickets (idempotent)")

        for i in range(5):
            rname = f"SEED-RISK-{i+1:03d}"
            if not c.first("fix.risk.register", [("name", "=", rname)]):
                c.call("fix.risk.register", "create", {
                    "name": rname,
                    "category": rng.choice(["operational", "financial", "cyber"]),
                    "likelihood": str(rng.randint(1, 5)),
                    "impact": str(rng.randint(1, 5)),
                })
        print("seed: risk register entries (idempotent)")

        # --- Phase 10 estate: marketplace, settlement, storefront, partner,
        # pricing, facility, projects (idempotent) -----------------------
        seed_customers = c.call("res.partner", "search",
                                 [("email", "like", "seed.customer%")], limit=10)
        if seed_customers:
            # 5 marketplace sellers (party-role on M33)
            for i in range(5):
                sname = f"Seed Seller {i+1}"
                if not c.first("fix.marketplace.seller", [("name", "=", sname)]):
                    c.call("fix.marketplace.seller", "create", {
                        "name": sname,
                        "partner_id": seed_customers[i],
                        "kyc_status": rng.choice(["pending", "verified"]),
                        "rating": round(rng.uniform(3.0, 5.0), 1),
                    })
            print("seed: marketplace sellers (idempotent)")

            # 5 marketplace orders (journey 7 states)
            sellers = c.call("fix.marketplace.seller", "search", [], limit=5)
            for i in range(5):
                oname = f"SEED-MKT-{i+1:03d}"
                if not c.first("fix.marketplace.order", [("name", "=", oname)]):
                    c.call("fix.marketplace.order", "create", {
                        "name": oname,
                        "customer_id": seed_customers[i],
                        "description": f"Seed marketplace order {i+1}",
                        "budget": rng.choice([2000, 5000, 10000]),
                        "state": rng.choice(["open", "quoted", "commissioned"]),
                    })
                    # Add a quote for each order
                    orders = c.call("fix.marketplace.order", "search",
                                     [("name", "=", oname)])
                    if orders and sellers:
                        c.call("fix.seller.quote", "create", {
                            "marketplace_order_id": orders[0],
                            "seller_id": sellers[i % len(sellers)],
                            "quoted_price": rng.choice([1500, 3000, 8000]),
                            "eta_days": rng.randint(1, 7),
                        })
            print("seed: marketplace orders + quotes (idempotent)")

            # 5 commission ledger entries
            for i in range(5):
                cname = f"SEED-COM-{i+1:03d}"
                if not c.first("fix.commission.ledger", [("name", "=", cname)]):
                    c.call("fix.commission.ledger", "create", {
                        "name": cname,
                        "seller_partner_id": seed_customers[i],
                        "gross_amount": rng.choice([2000, 5000, 10000]),
                        "commission_rate": 0.10,
                        "tds_amount": rng.choice([20, 50, 100]),
                        "state": "earned",
                    })
            print("seed: commission ledger entries (idempotent)")

            # 3 storefront carts
            for i in range(3):
                cart_name = f"SEED-CART-{i+1:03d}"
                if not c.first("fix.storefront.cart", [("name", "=", cart_name)]):
                    products = c.call("product.template", "search", [], limit=5)
                    cart = c.call("fix.storefront.cart", "create", {
                        "name": cart_name,
                        "customer_id": seed_customers[i],
                    })
                    if products:
                        c.call("fix.storefront.cart.line", "create", {
                            "cart_id": cart,
                            "product_id": products[i],
                            "quantity": rng.randint(1, 3),
                            "unit_price": rng.choice([500, 1000, 2000]),
                        })
            print("seed: storefront carts (idempotent)")

            # 3 partners (referral type)
            for i in range(3):
                pname = f"Seed Partner {i+1}"
                if not c.first("fix.partner", [("name", "=", pname)]):
                    c.call("fix.partner", "create", {
                        "name": pname,
                        "partner_id": seed_customers[i],
                        "partner_type": rng.choice(["referral", "reseller", "franchise"]),
                        "commission_rate": 0.05,
                    })
            print("seed: channel partners (idempotent)")

        # Dynamic pricing rules
        for name, adj in [("Demand Surge +15%", 15.0), ("Off-Peak -10%", -10.0),
                           ("Clearance -25%", -25.0)]:
            if not c.first("fix.dynamic.price.rule", [("name", "=", name)]):
                c.call("fix.dynamic.price.rule", "create", {
                    "name": name,
                    "rule_type": "demand_surge" if adj > 0 else "off_peak",
                    "adjustment_pct": adj,
                    "min_adjustment": min(adj, 0) - 5,
                    "max_adjustment": max(adj, 0) + 5,
                })
        print("seed: dynamic pricing rules (idempotent)")

        # 3 sites (facility)
        branches = c.call("fix.branch", "search", [], limit=3)
        for i, site_type in enumerate(["branch", "warehouse", "office"]):
            sname = f"Seed Site {site_type.title()} {i+1}"
            if not c.first("fix.site", [("name", "=", sname)]):
                c.call("fix.site", "create", {
                    "name": sname,
                    "site_type": site_type,
                    "branch_id": branches[i] if i < len(branches) else False,
                    "monthly_rent": rng.choice([30000, 80000, 150000]),
                })
        print("seed: facility sites (idempotent)")

        # 3 projects (PPM)
        for i in range(3):
            proj_name = f"Seed Project {i+1}"
            if not c.first("fix.project", [("name", "=", proj_name)]):
                c.call("fix.project", "create", {
                    "name": proj_name,
                    "project_type": rng.choice(["internal", "client", "infrastructure"]),
                    "budget": rng.choice([100000, 500000, 1000000]),
                    "state": "active",
                })
        print("seed: projects (idempotent)")

    print("seed: done (deterministic for --seed " + args.seed + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
