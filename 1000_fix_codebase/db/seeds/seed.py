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
    print("seed: done (deterministic for --seed " + args.seed + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
