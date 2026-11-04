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
import os
import random
import subprocess
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

BIND = "http://127.0.0.1:8069"
ALLOWED = {("http", "127.0.0.1", 8069), ("http", "localhost", 8069)}
DB = "fix_dev"
ADMIN = ("admin", "admin")

BRANCHES = [  # (code, bn, en) - the five cities of BE-001 6.5
    ("DHK", "ঢাকা", "Dhaka"),
    ("CTG", "চট্টগ্রাম", "Chattogram"),
    ("SYL", "সিলেট", "Sylhet"),
    ("KHL", "খুলনা", "Khulna"),
    ("RAJ", "রাজশাহী", "Rajshahi"),
]
GIVEN = [
    "রাহাত",
    "তানিয়া",
    "সাব্বির",
    "নুসরাত",
    "ইমরান",
    "মেহেদী",
    "ফারিয়া",
    "আরিফ",
    "সাদিয়া",
    "হাসিব",
    "জান্নাত",
    "রুবেল",
    "শারমিন",
    "নাজমুল",
    "তাসনিম",
    "শাকিল",
    "মৌসুমী",
    "রিফাত",
    "অনন্যা",
    "সাজ্জাদ",
]
FAMILY = [
    "হোসেন",
    "আহমেদ",
    "রহমান",
    "চৌধুরী",
    "ইসলাম",
    "করিম",
    "মাহমুদ",
    "সুলতানা",
    "বেগম",
    "তালুকদার",
    "হক",
    "মির্জা",
    "সরকার",
    "দাস",
]
FAULTS = [
    "ডিসপ্লে ভাঙা",
    "ব্যাটারি নষ্ট",
    "চার্জিং সমস্যা",
    "ওয়াটার ড্যামেজ",
    "সফটওয়্যার হ্যাং",
    "স্পিকার নষ্ট",
    "ক্যামেরা ঝাপসা",
    "কীপ্যাড কাজ করছে না",
]
BRANDS = [
    ("SAMS", "Samsung"),
    ("APPL", "Apple"),
    ("XIAO", "Xiaomi"),
    ("REAL", "Realme"),
    ("OPPO", "Oppo"),
    ("VIVO", "Vivo"),
    ("HUA", "Huawei"),
]
MODELS = [
    "Galaxy A55",
    "iPhone 14",
    "Redmi Note 13",
    "Narzo 70",
    "Reno 11",
    "V30e",
    "Nova 12",
    "Galaxy S24",
    "iPhone 13",
    "Redmi 13C",
]

# Legal order states in walk order (DP-01 VALID_TRANSITIONS); index = depth
PATH = [
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
]
ALL_TARGETS = ["draft", *PATH, "qc_failed", "ready", "delivered", "closed", "cancelled"]

WS_GROUPS = [
    "Workspace: Service Intake (Front Desk)",
    "Workspace: Service Orders",
    "Workspace: Party Master",
    "Workspace: Device Registry",
    "Workspace: Catalogue",
    "Workspace: Administration",
]


def validate_target(url: str) -> None:
    p = urlparse(url)
    if (p.scheme, p.hostname, p.port or 80) not in ALLOWED:
        raise ValueError(f"seed: refusing non-local endpoint {url!r}")


class Client:
    def __init__(self) -> None:
        self.cookie = ""

    def _post(self, path: str, payload: dict) -> dict:
        validate_target(BIND + path)
        req = urllib.request.Request(  # noqa: S310 - URL pinned by validate_target() above
            BIND + path,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Cookie": self.cookie} if self.cookie else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=300) as resp:  # noqa: S310 - URL pinned by validate_target() above
            sc = resp.headers.get("Set-Cookie", "")
            if sc:
                self.cookie = sc.split(";")[0]
            return json.loads(resp.read())

    def login(self, db: str, login: str, password: str) -> None:
        r = self._post(
            "/web/session/authenticate",
            {"params": {"db": db, "login": login, "password": password}},
        )
        if "error" in r:
            raise SystemExit(f"seed: admin login failed: {r['error']['data']['message']}")

    def call(self, model: str, method: str, *args, **kw):
        r = self._post(
            "/web/dataset/call_kw",
            {"params": {"model": model, "method": method, "args": list(args), "kwargs": kw}},
        )
        if "error" in r:
            msg = r["error"]["data"].get("message", str(r["error"]["data"]))
            raise RuntimeError(f"{model}.{method}: {msg}")
        return r.get("result")

    def first(self, model: str, domain: list):
        ids = self.call(model, "search", domain, limit=1)
        return ids[0] if ids else None


QC_LOGIN = "seed.qc@1000fix.local"
ROOT = Path(__file__).resolve().parents[2]
ODOO_CONF = "infra/odoo-conf/local.resolved.conf"


def xmlid(c: Client, module: str, name: str) -> int:
    rows = c.call(
        "ir.model.data", "search_read", [("module", "=", module), ("name", "=", name)], ["res_id"]
    )
    if not rows:
        raise RuntimeError(f"seed: {module}.{name} is not installed")
    return rows[0]["res_id"]


def qc_inspector_client(c: Client, db: str) -> Client:
    """A seed QC inspector, logged in. SOD-07: the admin walking the orders
    completes their repairs, so it may not inspect them."""
    if not c.first("res.users", [("login", "=", QC_LOGIN)]):
        groups = [
            xmlid(c, "base", "group_user"),
            xmlid(c, "cd_service_order", "group_so_qc_inspector"),
        ]
        c.call(
            "res.users",
            "create",
            {
                "name": "সিড কিউসি পরিদর্শক (Seed QC Inspector)",
                "login": QC_LOGIN,
                "email": QC_LOGIN,
                "password": QC_LOGIN,
                "group_ids": [(6, 0, groups)],
            },
        )
    qc = Client()
    qc.login(db, QC_LOGIN, QC_LOGIN)
    return qc


def seed_estimate(order_id: int, rng: random.Random) -> dict:
    """A priced estimate under the BDT 5,000 customer-approval threshold."""
    return {
        "order_id": order_id,
        "line_ids": [
            (0, 0, {"line_type": "diagnostic", "description": "ডায়াগনস্টিক", "unit_price": 300}),
            (0, 0, {"line_type": "labour", "description": "মেরামত শ্রম", "unit_price": 800}),
            (
                0,
                0,
                {
                    "line_type": "part",
                    "description": "যন্ত্রাংশ",
                    "unit_price": rng.choice([600, 900, 1500]),
                },
            ),
        ],
    }


def seed_checklist(order_id: int, passed: bool) -> dict:
    items = ["পাওয়ার অন", "ডিসপ্লে", "চার্জিং", "স্পিকার ও মাইক"]
    return {
        "order_id": order_id,
        "item_ids": [
            (0, 0, {"name": name, "passed": passed or i > 0}) for i, name in enumerate(items)
        ],
    }


# Run inside `odoo-bin shell` as the superuser acting for admin. The handover
# code goes to the customer's phone, so the seed captures it from a stubbed
# SMS sender (as the tests do) and reads it back; everything else is the
# real settle / verify / deliver / close path.
HANDOVER_SHELL = r"""
import base64, json
from odoo.addons.cd_service_order.models import fix_otp_util

plan = json.loads(%(plan)r)
sent = {}
fix_otp_util.dispatch_otp = lambda phone, code, ttl, language="bn": sent.update({phone: code})
env = env(user=env.ref("base.user_admin").id, su=True)
SO = env["fix.service.order"]
for target, ids in plan.items():
    for order in SO.browse(ids):
        if order.state == "ready":
            due = order._fix_amount_due()
            if due > 0 and order.payment_settlement_state == "unpaid":
                order.action_mark_settled(amount_bdt=due, reference="SEED-PAY-%%d" %% order.id)
            order.action_send_delivery_otp()
            order.action_verify_delivery_otp(otp=sent[fix_otp_util.bd_mobile(order.customer_id)])
            report = env["ir.attachment"].create({
                "name": "%%s-service-report.pdf" %% order.name,
                "datas": base64.b64encode(b"%%PDF-1.4 synthetic seed report"),
                "res_model": SO._name,
                "res_id": order.id,
            })
            order.write({"recipient_name": order.customer_id.name,
                         "service_report_attachment_id": report.id})
            order.action_deliver()
        if target == "closed" and order.state == "delivered":
            order.action_close()
env.cr.commit()
print("seed-handover:", {t: len(i) for t, i in plan.items()})
"""


def run_in_shell(db: str, script: str, marker: str) -> None:
    """Run ``script`` in `odoo-bin shell` on ``db`` and print its ``marker`` line."""
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONUTF8": "1"}
    out = subprocess.run(  # noqa: S603 - fixed argv, local odoo-bin only
        [sys.executable, "vendor/odoo/odoo-bin", "shell", "-c", ODOO_CONF, "-d", db, "--no-http"],
        input=script,
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=env,
        check=False,
    )
    if marker not in out.stdout:
        raise RuntimeError(f"seed: {marker} shell failed:\n{out.stderr[-3000:]}")
    print(next(line for line in out.stdout.splitlines() if marker in line))


def handover_in_shell(db: str, plan: dict[str, list[int]]) -> None:
    run_in_shell(db, HANDOVER_SHELL % {"plan": json.dumps(plan)}, "seed-handover:")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="1000fix", help="fixed random seed (DE-12)")
    ap.add_argument(
        "--force", action="store_true", help="seed even if orders already exist (appends)"
    )
    ap.add_argument("--db", default=DB, help="database on the local Odoo (default fix_dev)")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    c = Client()
    try:
        c.login(args.db, *ADMIN)
    except Exception as e:
        print(f"seed: NOT-AVAILABLE - no Odoo on {BIND} ({e})")
        print("  remedy: tasks.ps1 -Target up, then -Target run")
        return 4

    if c.call("fix.service.order", "search_count", []) and not args.force:
        print("seed: REFUSED - fix.service.order already has rows (DE-12: never mix).")
        print(
            "  re-seed from scratch: tasks.ps1 -Target reset (drops the volume), or --force to append."
        )
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
        entity = c.call(
            "fix.entity",
            "create",
            {
                "code": "SEED",
                "legal_name": "1000FiX Services Ltd (Seed)",
                "company_id": company,
                "country_id": bd,
            },
        )

    # 5 branches (config rows: perm_unlink=0 by design - reuse by code) -----
    branch_ids = []
    for code, bn, en in BRANCHES:
        existing = c.first("fix.branch", [("code", "=", code), ("entity_id", "=", entity)])
        branch_ids.append(
            existing
            or c.call(
                "fix.branch",
                "create",
                {
                    "code": code,
                    "name": f"{bn} শাখা ({en})",
                    "entity_id": entity,
                    "operating_unit_id": ou,
                },
            )
        )
    print("seed: 5 branches ready")

    # ~25 users across the workspace groups (reuse by login) -----------------
    group_ids = [g for g in (c.first("res.groups", [("name", "=", n)]) for n in WS_GROUPS) if g]
    new_users = []
    for i in range(25):
        login = f"seed.user{i + 1:02d}@1000fix.local"
        if c.first("res.users", [("login", "=", login)]):
            continue
        given, family = rng.choice(GIVEN), rng.choice(FAMILY)
        new_users.append(
            {
                "name": f"{given} {family}",
                "login": login,
                "email": login,
                "password": login,
                "group_ids": [group_ids[i % len(group_ids)]] if group_ids else [],
            }
        )
    if new_users:
        c.call("res.users", "create", new_users)
    print(f"seed: 25 users across {len(group_ids)} workspace groups (created {len(new_users)})")

    # 200 customers (Bengali-first) ------------------------------------------
    c.call(
        "res.partner",
        "create",
        [
            {
                "name": f"{rng.choice(GIVEN)} {rng.choice(FAMILY)}",
                "phone": f"01{rng.randint(3, 9)}{rng.randint(10000000, 99999999)}",
                "email": f"seed.customer{i + 1:03d}@example.local",
            }
            for i in range(200)
        ],
    )
    customers = c.call("res.partner", "search", [("email", "like", "seed.customer%")], limit=200)
    print(f"seed: {len(customers)} customers")

    # 400 products: brands -> models -> products+catalogue items (reuse by key)
    brand_ids = []
    for code, name in BRANDS:
        brand_ids.append(
            # the brand master ships as module data (BRD-001 ...): reuse by name too
            c.first("fix.brand", ["|", ("code", "=", code), ("name", "=ilike", name)])
            or c.call("fix.brand", "create", {"code": code, "name": name})
        )
    have_models = c.call(
        "fix.device.model",
        "search",
        [("name", "like", "%"), ("company_id", "=", company)],
        limit=40,
    )
    if len(have_models) >= 40:
        model_ids = have_models[:40]
    else:
        model_ids = (
            c.call(
                "fix.device.model",
                "create",
                [
                    {
                        "name": rng.choice(MODELS) + f" {i}",
                        "brand_id": rng.choice(brand_ids),
                        "company_id": company,
                    }
                    for i in range(40 - len(have_models))
                ],
            )
            + have_models
        )
    tmpl_ids = c.call(
        "product.template",
        "create",
        [
            {
                "name": f"মেরামত সেবা {rng.choice(FAULTS)} {i}",
                "list_price": round(rng.uniform(300, 8000), 2),
                "type": "service",
            }
            for i in range(400)
        ],
    )
    c.call(
        "fix.catalogue.item",
        "create",
        [{"product_tmpl_id": t, "company_id": company} for t in tmpl_ids],
    )
    print("seed: 400 products + catalogue items")

    # 500 devices across models and warranty states (serial is unique: reuse) --
    existing_devices = c.call(
        "fix.device", "search", [("serial_number", "like", "SEED-D%")], limit=500
    )
    need = 500 - len(existing_devices)
    device_ids = existing_devices + (
        c.call(
            "fix.device",
            "create",
            [
                {
                    "serial_number": f"SEED-D{i:05d}",
                    "device_model_id": rng.choice(model_ids),
                    "company_id": company,
                    "owner_id": rng.choice(customers),
                    "warranty_status": rng.choice(
                        ["in_warranty", "out_of_warranty", "extended", "unknown"]
                    ),
                }
                for i in range(need)
            ],
        )
        if need > 0
        else []
    )
    print(f"seed: {len(device_ids)} devices")

    # 60 SLA policies (reuse by unique code) ----------------------------------
    sla_vals = []
    for i in range(60):
        code = f"SEEDSLA{i + 1:03d}"[:16]
        if c.first("fix.sla.policy", [("code", "=", code)]):
            continue
        pri = rng.choice(["normal", "high", "urgent", "emergency"])
        sla_vals.append(
            {
                "code": code,
                "name": f"SLA {pri} {BRANCHES[i % 5][2]}",
                "service_type": rng.choice(["walk_in", "collection", "onsite", "mail_in"]),
                "priority": pri,
                "company_id": company,
                "response_hours": rng.choice([4, 8, 12, 24]),
                "resolution_hours": rng.choice([24, 48, 72, 120]),
            }
        )
    c.call("fix.sla.policy", "create", sla_vals)
    print("seed: 60 SLA policies")

    # 300 service orders, state-complete (DE-16). Idempotent over crashed
    # partial runs: existing seed orders (fault text is the marker) are kept,
    # pinned to whatever state they already reached; fresh orders are created
    # only for the states still short of their quota.
    per_state = {t: 300 // len(ALL_TARGETS) for t in ALL_TARGETS}
    existing = c.call(
        "fix.service.order", "search_read", [("fault_description", "in", FAULTS)], ["state"]
    )
    orders: list[dict] = []
    order_ids: list[int] = [r["id"] for r in existing]
    taken: dict[str, int] = {}
    for r in existing:  # an order already AT a state satisfies that quota
        taken[r["state"]] = taken.get(r["state"], 0) + 1
    i = 0
    for target in ALL_TARGETS:
        for _ in range(per_state[target] - taken.get(target, 0)):
            orders.append(
                {
                    "target": target,
                    "vals": {
                        "customer_id": rng.choice(customers),
                        "device_id": device_ids[i % len(device_ids)],
                        "branch_id": branch_ids[i % len(branch_ids)],
                        "fault_description": rng.choice(FAULTS),
                    },
                }
            )
            i += 1
    if orders:
        order_ids += c.call("fix.service.order", "create", [o["vals"] for o in orders])
    targets_all = [r["state"] for r in existing] + [o["target"] for o in orders]

    # Advance every order from its CURRENT state to its target along the
    # LEGAL path (BFS over DP-01's VALID_TRANSITIONS) - batched per hop, so
    # a crashed partial run is resumed, never invalidated. OFFLINE map is
    # mirrored from the model (single authority): draft->intake->...->
    # qc_pending->{ready,qc_failed}; ready->delivered->closed.
    SUCC = {
        "draft": ["intake"],
        "intake": ["diagnostic", "cancelled"],
        "diagnostic": ["estimate_pending", "cancelled"],
        "estimate_pending": ["estimate_sent", "cancelled"],
        "estimate_sent": ["awaiting_approval", "cancelled"],
        "awaiting_approval": ["approved", "cancelled"],
        "approved": ["in_repair", "cancelled"],
        "in_repair": ["qc_pending", "cancelled"],
        "qc_pending": ["ready", "qc_failed"],
        "qc_failed": ["in_repair"],
        "ready": ["delivered"],
        "delivered": ["closed"],
        "closed": [],
        "cancelled": [],
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
                    return [*p, nxt]
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, [*p, nxt]))
        raise RuntimeError(f"no legal path {src} -> {dst}")

    # A02 P0 (M01): state changes only through the action that owns it, so
    # each hop brings the evidence its gate asks for - a priced estimate
    # sent and approved, a QC checklist completed by an independent
    # inspector (SOD-07: not the person who completed the repair).
    # Ready -> Delivered -> Closed needs the customer's handover code, which
    # by design never comes back over RPC: those hops run in a superuser
    # odoo shell instead (handover_in_shell).
    qc = qc_inspector_client(c, args.db)
    handover: dict[str, list[int]] = {"delivered": [], "closed": []}

    def hop(group: list[int], nxt: str) -> None:
        if nxt == "estimate_sent":
            orders_ = c.call("fix.service.order", "read", group, ["estimate_ids"])
            fresh = [o["id"] for o in orders_ if not o["estimate_ids"]]
            if fresh:
                c.call("fix.estimate", "create", [seed_estimate(oid, rng) for oid in fresh])
            c.call("fix.service.order", "action_send_estimate", group)
        elif nxt == "approved":
            sent = c.call(
                "fix.estimate", "search", [("order_id", "in", group), ("state", "=", "sent")]
            )
            c.call("fix.estimate", "action_approve", sent)
        elif nxt in ("ready", "qc_failed"):
            passed = nxt == "ready"
            checklists = c.call(
                "fix.qc.checklist", "create", [seed_checklist(oid, passed) for oid in group]
            )
            qc.call("fix.qc.checklist", "action_complete", checklists)  # a fail sends it back
            if passed:
                c.call("fix.service.order", "action_ready", group)
        elif nxt == "cancelled":
            c.call("fix.service.order", "action_cancel", group, reason_code="customer_declined")
        else:
            c.call("fix.service.order", "action_transition", group, nxt)

    # zip(order_ids, targets_all): id -> its assigned target state
    for target in ALL_TARGETS:
        ids = [oid for oid, t in zip(order_ids, targets_all, strict=False) if t == target]
        if not ids:
            continue
        states = {
            rec["id"]: rec["state"] for rec in c.call("fix.service.order", "read", ids, ["state"])
        }
        # group orders with the same current state; batch each hop
        by_state: dict[str, list[int]] = {}
        for oid in ids:
            by_state.setdefault(states[oid], []).append(oid)
        for cur, group in by_state.items():
            for nxt in path_to(cur, target):
                if nxt in handover:  # the rest of the walk is the handover
                    handover[target] += group
                    break
                hop(group, nxt)
    if handover["delivered"] or handover["closed"]:
        handover_in_shell(args.db, handover)

    counts = {}
    for t in ALL_TARGETS:
        counts[t] = c.call("fix.service.order", "search_count", [("state", "=", t)])
    print(f"seed: 300 service orders, state-complete: {counts}")
    outbox = c.call("fix.event.outbox", "search_count", [])
    print(f"seed: outbox carries {outbox} events (AS-08) - dispatcher drain is a separate step")

    # The M63 approval groups: with nobody appointed every routed request is
    # refused with "No one can approve" (db/seeds/appoint_approvers.py). Done
    # here because the anchors below decide as the appointed approvers.
    appoint = (Path(__file__).parent / "appoint_approvers.py").read_text(encoding="utf-8")
    run_in_shell(args.db, appoint, "appoint-approvers:")

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
            existing = c.first(
                "fix.employment.contract",
                [("employee_id", "=", emp), ("joining_date", "=", joining)],
            )
            if existing:
                continue
            basic = rng.choice([15000, 20000, 25000, 30000, 40000, 50000, 60000])
            contracts.append(
                {
                    "employee_id": emp,
                    "contract_type": rng.choice(["permanent", "probation", "fixed_term"]),
                    "joining_date": joining,
                    "basic_monthly": basic,
                    # Bangladesh pay structure: house rent 50% of basic, medical
                    # 10%, fixed conveyance, and a technical allowance for the
                    # repair grades. Without these the payslip allowance seam
                    # and the Para 27 exemption are never exercised.
                    "house_rent": round(basic * 0.50, 2),
                    "medical_allowance": round(basic * 0.10, 2),
                    "conveyance_allowance": 2500.0,
                    "technical_allowance": 2000.0 if i % 2 == 0 else 0.0,
                    "weekly_hours": 48,
                    "state": "active",
                }
            )
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
                leave_types.append(
                    {
                        "code": code,
                        "name": name,
                        "name_bn": name,
                        "entitlement_days": days,
                        "encashable": enc,
                        "maternity": code == "maternity",
                    }
                )
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
            existing = c.first(
                "fix.leave.request",
                [("employee_id", "=", emp), ("leave_type_id", "=", lt), ("date_from", "=", df)],
            )
            if existing:
                continue
            c.call(
                "fix.leave.request",
                "create",
                {
                    "employee_id": emp,
                    "leave_type_id": lt,
                    "date_from": df,
                    "date_to": str(_dt.date(2026, 11, (i % 28) + 1 + (i % 3))),
                    "state": rng.choice(["draft", "submitted", "approved"]),
                },
            )
            created_leave += 1
        print(f"seed: {created_leave} leave requests created (idempotent)")

        # 5 shift templates + 200 roster slots (the roster that closes M02->M55)
        shifts = []
        for name, start, end in [
            ("Morning", 9.0, 17.0),
            ("Day", 10.0, 18.0),
            ("Evening", 14.0, 22.0),
            ("Night", 22.0, 6.0),
            ("Split", 9.0, 13.0),
        ]:
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
                existing = c.first(
                    "fix.roster.slot", [("employee_id", "=", emp), ("date", "=", str(d))]
                )
                if existing:
                    continue
                roster.append(
                    {
                        "employee_id": emp,
                        "date": str(d),
                        "shift_id": shift_ids[day_offset % len(shift_ids)],
                        "on_leave": rng.random() < 0.05,
                    }
                )
        if roster:
            c.call("fix.roster.slot", "create", roster)
        print(f"seed: {len(roster)} roster slots created (idempotent)")

        # 100 attendance records
        created_att = 0
        for i in range(100):
            emp = hr_employees[i % len(hr_employees)]
            check_in = _dt.datetime(2026, 10, 5, 9, 0) + _dt.timedelta(hours=i % 8)
            ci_str = check_in.strftime("%Y-%m-%d %H:%M:%S")
            if c.first(
                "fix.attendance.record", [("employee_id", "=", emp), ("check_in", "=", ci_str)]
            ):
                continue
            c.call(
                "fix.attendance.record",
                "create",
                {
                    "employee_id": emp,
                    "check_in": ci_str,
                    "check_out": (check_in + _dt.timedelta(hours=8 + (i % 3))).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "source": rng.choice(["biometric", "mobile", "manual"]),
                    "device_ref": f"SEED-DEV-{i:03d}",
                },
            )
            created_att += 1
        print(f"seed: {created_att} attendance records created (idempotent)")

        # One attendance lock for September 2026 (the payroll gate)
        lock = c.first("fix.attendance.lock", [("name", "=", "2026-09")])
        if not lock:
            lock = c.call(
                "fix.attendance.lock",
                "create",
                {
                    "name": "2026-09",
                    "period_start": "2026-09-01",
                    "period_end": "2026-09-30",
                },
            )
        print("seed: attendance lock for 2026-09 (the payroll cycle's gate)")

        # Device taxonomy (RAP-M22-01). The model shipped but was never
        # populated: with 0 categories and no branded competency the
        # brand-scoped dispatch gate can never fire, however correct its code.
        cat_by = {}
        for code, name, tier in [
            ("LAPTOP", "Laptop & Notebook", "l2"),
            ("PHONE", "Smartphone & Tablet", "l3"),
            ("APPLIANCE", "Home Appliance", "l2"),
            ("NETWORK", "Network & Infrastructure", "l2"),
        ]:
            cid = c.first("fix.device.category", [("code", "=", code)])
            if not cid:
                cid = c.call(
                    "fix.device.category",
                    "create",
                    {"code": code, "name": name, "repair_tier_floor": tier},
                )
            cat_by[code] = cid

        def _brand(nm):
            return c.first("fix.brand", [("name", "ilike", nm)]) or c.first("fix.brand", [])

        # Competencies + certifications (the dispatch eligibility engine).
        # Each gating competency carries a brand, a device category and the
        # minimum repair tier, so (brand, category, tier) is actually gated.
        comps = []
        SCOPE = {
            "SMP": ("Smartphone Repair", "smartphone", "Apple", "PHONE", "l3"),
            "LAP": ("Laptop Repair", "laptop", "Dell", "LAPTOP", "l2"),
            "APP": ("Home Appliance Repair", "home_appliance", "Samsung", "APPLIANCE", "l2"),
            "NET": ("Network Diagnostics", None, "Cisco", "NETWORK", "l2"),
        }
        for code, (name, dev, bname, ccode, tier) in SCOPE.items():
            existing = c.first("fix.competency", [("code", "=", code)])
            vals = {
                "code": code,
                "name": name,
                "name_bn": name,
                "device_type": dev,
                "brand_id": _brand(bname),
                "device_category_id": cat_by[ccode],
                "repair_tier": tier,
            }
            if existing:
                c.call(
                    "fix.competency",
                    "write",
                    [existing],
                    {
                        k: v
                        for k, v in vals.items()
                        if k in ("brand_id", "device_category_id", "repair_tier")
                    },
                )
            else:
                comps.append(vals)
        if comps:
            c.call("fix.competency", "create", comps)
        comp_ids = c.call("fix.competency", "search", [], limit=4)
        certs = []
        for i, emp in enumerate(hr_employees[:30]):
            comp = comp_ids[i % len(comp_ids)]
            existing = c.first(
                "fix.certification",
                [
                    ("employee_id", "=", emp),
                    ("competency_id", "=", comp),
                    ("issued_on", "=", str(_dt.date(2025, 1, 15))),
                ],
            )
            if existing:
                continue
            comp_rec = c.call(
                "fix.competency",
                "read",
                [comp],
                ["brand_id", "device_category_id", "repair_tier"],
            )[0]
            certs.append(
                {
                    "employee_id": emp,
                    "competency_id": comp,
                    "issued_on": str(_dt.date(2025, 1, 15)),
                    "expires_on": str(_dt.date(2027, 1, 15)),
                    # scope the certificate to its competency so the gate has
                    # something to match and nobody loses existing eligibility
                    "brand_id": (comp_rec.get("brand_id") or [False])[0],
                    "device_category_id": (comp_rec.get("device_category_id") or [False])[0],
                    "repair_tier": comp_rec.get("repair_tier") or False,
                }
            )
        if certs:
            c.call("fix.certification", "create", certs)
        print(f"seed: {len(certs)} certifications created (idempotent)")

        # One payroll period + payslips for September (Journey 13 exercised)
        period = c.first("fix.payroll.period", [("name", "=", "2026-09")])
        if not period:
            period = c.call(
                "fix.payroll.period",
                "create",
                {
                    "name": "2026-09",
                    "period_start": "2026-09-01",
                    "period_end": "2026-09-30",
                    "state": "attendance_locked",
                },
            )
            created_slips = 0
            for emp in hr_employees[:25]:
                if c.first("fix.payslip", [("period_id", "=", period), ("employee_id", "=", emp)]):
                    continue
                c.call(
                    "fix.payslip",
                    "create",
                    {
                        "period_id": period,
                        "employee_id": emp,
                        "basic": rng.choice([15000, 20000, 30000, 50000]),
                        "ot_hours": rng.choice([0, 5, 10, 20]),
                        "incentive": rng.choice([0, 500, 1500, 3000]),
                        "pf_employee_pct": 10.0,
                        "pf_employer_pct": 10.0,
                    },
                )
                created_slips += 1
            if created_slips:
                c.call("fix.payroll.period", "write", [period], {"state": "calculated"})
        print("seed: payroll period + payslips (idempotent)")

        # 20 NCRs (idempotent: deterministic description per index)
        ncrs = []
        NCR_CAUSES = ["process deviation", "equipment fault", "documentation gap", "training gap"]
        for i in range(20):
            desc = f"Seed NCR {i+1}: {NCR_CAUSES[i % len(NCR_CAUSES)]}"
            existing = c.first("fix.ncr", [("description", "=", desc)])
            if existing:
                continue
            ncrs.append(
                {
                    "source": rng.choice(["service_order", "qc", "complaint", "audit"]),
                    "severity": rng.choice(["minor", "major", "critical"]),
                    "description": desc,
                    "state": rng.choice(["new", "root_cause", "capa_open", "closed"]),
                }
            )
        if ncrs:
            c.call("fix.ncr", "create", ncrs)
        print(f"seed: {len(ncrs)} NCRs created (idempotent)")

        # MSP: create a base contract first if none, then MSP + assets
        contract = c.first("fix.contract", [("name", "=", "Seed MSP Base Contract")])
        if not contract:
            customers = c.call(
                "res.partner", "search", [("email", "like", "seed.customer%")], limit=1
            )
            ous = c.call("operating.unit", "search", [], limit=1)
            if customers and ous:
                try:
                    contract = c.call(
                        "fix.contract",
                        "create",
                        {
                            "name": "Seed MSP Base Contract",
                            "customer_id": customers[0],
                            "operating_unit_id": ous[0],
                            "family": "amc",
                            "date_start": "2026-01-01",
                            "date_end": "2027-12-31",
                            "annual_value": 120000.0,
                            # A04 build (M08-14): activation is the DOFA ->
                            # Legal -> signed-envelope -> stamp-duty ladder;
                            # a seed cannot honestly supply the customer's
                            # signature, so the contract stays a draft.
                        },
                    )
                except RuntimeError as e:
                    print(f"seed: fix.contract creation failed: {e}")
        msp_contract = c.first("fix.msp.contract", [("name", "=", "Seed MSP")])
        if not msp_contract and contract:
            msp_contract = c.call(
                "fix.msp.contract",
                "create",
                {
                    "name": "Seed MSP",
                    "contract_id": contract,
                    "monitoring_scope": "endpoints",
                    "per_device_monthly": 500.0,
                },
            )
        if msp_contract:
            for i in range(10):
                agent = f"SEED-AGENT-{i:03d}"
                if c.first("fix.monitored.asset", [("agent_id", "=", agent)]):
                    continue
                c.call(
                    "fix.monitored.asset",
                    "create",
                    {
                        "msp_contract_id": msp_contract,
                        "agent_id": agent,
                        "hostname": f"seed-workstation-{i:03d}",
                        "health": rng.choice(["healthy", "degraded", "offline"]),
                    },
                )
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
                    c.call(
                        "fix.rental.reservation",
                        "create",
                        {
                            "name": rname,
                            "customer_id": customers[0] if customers else 1,
                            "device_id": devices[i % len(devices)],
                            "date_from": "2026-10-01",
                            "date_to": "2026-10-15",
                            "daily_rate": rng.choice([500, 800, 1200]),
                            "deposit_collected": rng.choice([2000, 5000]),
                            "state": "active",
                        },
                    )
            print("seed: rental reservations (idempotent)")

            for i in range(5):
                tname = f"SEED-TRD-{i+1:03d}"
                if not c.first("fix.tradein.request", [("name", "=", tname)]):
                    c.call(
                        "fix.tradein.request",
                        "create",
                        {
                            "name": tname,
                            "customer_id": customers[1] if len(customers) > 1 else 1,
                            "device_id": devices[i % len(devices)],
                            "offered_value": rng.choice([3000, 8000, 15000]),
                            "state": rng.choice(["offered", "accepted", "wiped"]),
                        },
                    )
            print("seed: trade-in requests (idempotent)")

        for i in range(3):
            dname = f"SEED-DRC-{i+1:03d}"
            if not c.first("fix.data.recovery.case", [("name", "=", dname)]):
                # A02 P2 (M06-2, M06-9): custody and the Z4 route are taken by
                # their actions, which write the custody ledger
                case = c.call(
                    "fix.data.recovery.case",
                    "create",
                    {
                        "name": dname,
                        "customer_id": customers[2] if len(customers) > 2 else 1,
                        "media_type": rng.choice(["hdd", "ssd", "phone"]),
                    },
                )
                c.call("fix.data.recovery.case", "action_take_custody", [case], "Seed intake")
                c.call("fix.data.recovery.case", "action_route_to_z4", [case])
        print("seed: data recovery cases (idempotent)")

        # A06 S8/R6: forecast, stock and reorder point are computed from the
        # part's M15 consumption and on-hand ledger, so a seed names the part
        # and the location and lets the plan compute the figures.
        products = c.call("product.template", "search", [], limit=10)
        parts = c.call("fix.spare.part", "search", [], limit=10)
        locations = c.call("fix.stock.location", "search", [], limit=1)
        for i in range(5 if parts and locations else 0):
            pname = f"SEED-DEMAND-{i+1:03d}"
            if not c.first("fix.demand.plan", [("name", "=", pname)]):
                c.call(
                    "fix.demand.plan",
                    "create",
                    {
                        "name": pname,
                        "period_start": "2026-11-01",
                        "period_end": "2026-11-30",
                        "product_id": products[i % len(products)] if products else False,
                        "part_id": parts[i % len(parts)],
                        "location_id": locations[0],
                    },
                )
        print("seed: demand plans (idempotent)")

        for i in range(3):
            bname = f"SEED-BUDGET-FY2027-{i+1}"
            if not c.first("fix.budget", [("name", "=", bname)]):
                c.call(
                    "fix.budget",
                    "create",
                    {
                        "name": bname,
                        "fiscal_year": "2027",
                        "planned_amount": rng.choice([500000, 1000000, 2000000]),
                    },
                )
        print("seed: budgets (idempotent)")

        for i in range(5):
            hname = f"SEED-HSE-{i+1:03d}"
            if not c.first("fix.hse.incident", [("name", "=", hname)]):
                c.call(
                    "fix.hse.incident",
                    "create",
                    {
                        "name": hname,
                        "incident_type": rng.choice(["injury", "near_miss", "fire"]),
                        "severity": rng.choice(["low", "medium", "high"]),
                        "description": f"Seed HSE incident {i+1}",
                        # a high-severity injury names the injured worker or the reporter
                        "employee_id": hr_employees[i % len(hr_employees)]
                        if hr_employees
                        else False,
                    },
                )
        print("seed: HSE incidents (idempotent)")

        for i in range(5):
            kname = f"Seed KB Article {i+1}"
            if not c.first("fix.knowledge.article", [("name", "=", kname)]):
                c.call(
                    "fix.knowledge.article",
                    "create",
                    {
                        "name": kname,
                        "category": rng.choice(
                            ["troubleshooting", "repair_procedure", "device_guide"]
                        ),
                        "content": f"<p>Seed knowledge article {i+1}</p>",
                        "state": "published",
                    },
                )
        print("seed: knowledge articles (idempotent)")

        for i in range(5):
            iname = f"SEED-ITSM-{i+1:03d}"
            if not c.first("fix.itsm.ticket", [("name", "=", iname)]):
                c.call(
                    "fix.itsm.ticket",
                    "create",
                    {
                        "name": iname,
                        "title": f"Seed ITSM ticket {i+1}",
                        "requester_id": hr_employees[i % len(hr_employees)] if hr_employees else 1,
                        "category": rng.choice(["hardware", "software", "network"]),
                        "priority": rng.choice(["low", "medium", "high"]),
                        "description": f"Seed ITSM issue {i+1}",
                    },
                )
        print("seed: ITSM tickets (idempotent)")

        for i in range(5):
            rname = f"SEED-RISK-{i+1:03d}"
            if not c.first("fix.risk.register", [("name", "=", rname)]):
                c.call(
                    "fix.risk.register",
                    "create",
                    {
                        "name": rname,
                        "category": rng.choice(["operational", "financial", "cyber"]),
                        "likelihood": str(rng.randint(1, 5)),
                        "impact": str(rng.randint(1, 5)),
                    },
                )
        print("seed: risk register entries (idempotent)")

        # --- Phase 10 estate: marketplace, settlement, storefront, partner,
        # pricing, facility, projects (idempotent) -----------------------
        seed_customers = c.call(
            "res.partner", "search", [("email", "like", "seed.customer%")], limit=10
        )
        if seed_customers:
            # 5 marketplace sellers (party-role on M33)
            for i in range(5):
                sname = f"Seed Seller {i+1}"
                if not c.first("fix.marketplace.seller", [("name", "=", sname)]):
                    seller = c.call(
                        "fix.marketplace.seller",
                        "create",
                        {
                            "name": sname,
                            "partner_id": seed_customers[i],
                            "rating": round(rng.uniform(3.0, 5.0), 1),
                        },
                    )
                    # BRU-ECM-01: only a CFO-approved, KYC-verified seller quotes;
                    # the sign-offs are the actions, not a typed status
                    if rng.random() < 0.6:
                        c.call("fix.marketplace.seller", "action_cfo_approve", [seller])
                        c.call("fix.marketplace.seller", "action_verify_kyc", [seller])
            print("seed: marketplace sellers (idempotent)")

            # 5 marketplace orders (journey 7 states)
            sellers = c.call(
                "fix.marketplace.seller",
                "search",
                [("kyc_status", "=", "verified"), ("cfo_approved", "=", True)],
                limit=5,
            )
            for i in range(5):
                oname = f"SEED-MKT-{i+1:03d}"
                if not c.first("fix.marketplace.order", [("name", "=", oname)]):
                    c.call(
                        "fix.marketplace.order",
                        "create",
                        {
                            "name": oname,
                            "customer_id": seed_customers[i],
                            "description": f"Seed marketplace order {i+1}",
                            "budget": rng.choice([2000, 5000, 10000]),
                            # A04 build (M14): the order state is readonly and
                            # moves only through select_quote / start_job /
                            # complete, which need seller quotes a fresh seed
                            # has not yet accepted; it is born open.
                        },
                    )
                    # Add a quote for each order
                    orders = c.call("fix.marketplace.order", "search", [("name", "=", oname)])
                    if orders and sellers:
                        c.call(
                            "fix.seller.quote",
                            "create",
                            {
                                "marketplace_order_id": orders[0],
                                "seller_id": sellers[i % len(sellers)],
                                "quoted_price": rng.choice([1500, 3000, 8000]),
                                "eta_days": rng.randint(1, 7),
                            },
                        )
            print("seed: marketplace orders + quotes (idempotent)")

            # 5 commission ledger entries
            for i in range(5):
                cname = f"SEED-COM-{i+1:03d}"
                if not c.first("fix.commission.ledger", [("name", "=", cname)]):
                    c.call(
                        "fix.commission.ledger",
                        "create",
                        {
                            "name": cname,
                            "seller_partner_id": seed_customers[i],
                            "gross_amount": rng.choice([2000, 5000, 10000]),
                            "commission_rate": 0.10,
                            "tds_amount": rng.choice([20, 50, 100]),
                            # A04 build: "earned" is set by the marketplace
                            # order's action_earn_commission once a completed
                            # job is reviewed; it is not a typed status.
                        },
                    )
            print("seed: commission ledger entries (idempotent)")

            # 3 storefront carts
            for i in range(3):
                cart_name = f"SEED-CART-{i+1:03d}"
                if not c.first("fix.storefront.cart", [("name", "=", cart_name)]):
                    products = c.call("product.template", "search", [], limit=5)
                    cart = c.call(
                        "fix.storefront.cart",
                        "create",
                        {
                            "name": cart_name,
                            "customer_id": seed_customers[i],
                        },
                    )
                    if products:
                        c.call(
                            "fix.storefront.cart.line",
                            "create",
                            {
                                "cart_id": cart,
                                "product_id": products[i],
                                "quantity": rng.randint(1, 3),
                                "unit_price": rng.choice([500, 1000, 2000]),
                            },
                        )
            print("seed: storefront carts (idempotent)")

            # 3 partners (referral type)
            for i in range(3):
                pname = f"Seed Partner {i+1}"
                if not c.first("fix.partner", [("name", "=", pname)]):
                    c.call(
                        "fix.partner",
                        "create",
                        {
                            "name": pname,
                            "partner_id": seed_customers[i],
                            "partner_type": rng.choice(["referral", "reseller", "franchise"]),
                            "commission_rate": 0.05,
                        },
                    )
            print("seed: channel partners (idempotent)")

        # Dynamic pricing rules
        for name, adj in [
            ("Demand Surge +15%", 15.0),
            ("Off-Peak -10%", -10.0),
            ("Clearance -25%", -25.0),
        ]:
            if not c.first("fix.dynamic.price.rule", [("name", "=", name)]):
                c.call(
                    "fix.dynamic.price.rule",
                    "create",
                    {
                        "name": name,
                        "rule_type": "demand_surge" if adj > 0 else "off_peak",
                        "adjustment_pct": adj,
                        "min_adjustment": min(adj, 0) - 5,
                        "max_adjustment": max(adj, 0) + 5,
                    },
                )
        print("seed: dynamic pricing rules (idempotent)")

        # 3 sites (facility)
        branches = c.call("fix.branch", "search", [], limit=3)
        for i, site_type in enumerate(["branch", "warehouse", "office"]):
            sname = f"Seed Site {site_type.title()} {i+1}"
            if not c.first("fix.site", [("name", "=", sname)]):
                c.call(
                    "fix.site",
                    "create",
                    {
                        "name": sname,
                        "site_type": site_type,
                        "branch_id": branches[i] if i < len(branches) else False,
                        "monthly_rent": rng.choice([30000, 80000, 150000]),
                    },
                )
        print("seed: facility sites (idempotent)")

        # 3 projects (PPM)
        for i in range(3):
            proj_name = f"Seed Project {i+1}"
            if not c.first("fix.project", [("name", "=", proj_name)]):
                c.call(
                    "fix.project",
                    "create",
                    {
                        "name": proj_name,
                        "project_type": rng.choice(["internal", "client", "infrastructure"]),
                        "budget": rng.choice([100000, 500000, 1000000]),
                        "state": "active",
                    },
                )
        print("seed: projects (idempotent)")

        # --- Phase 11 estate: data governance, IoT, e-waste (idempotent) ---
        # 5 data entities (the catalogue)
        for name, etype, cls in [
            ("Service Orders Table", "table", "internal"),
            ("Customer API Resource", "api", "confidential"),
            ("Order Events Stream", "event", "internal"),
            ("SLA Attainment KPI", "report", "internal"),
            ("Identity Documents", "document", "residency_classified"),
        ]:
            if not c.first("fix.data.entity", [("name", "=", name)]):
                c.call(
                    "fix.data.entity",
                    "create",
                    {
                        "name": name,
                        "entity_type": etype,
                        "classification": cls,
                        "retention_policy": "7 years (statutory)",
                    },
                )
        print("seed: data catalogue entities (idempotent)")

        # 3 lineage chains
        entities = c.call("fix.data.entity", "search", [], limit=5)
        if len(entities) >= 3:
            for i in range(3):
                lname = f"Seed Lineage {i+1}"
                if not c.first("fix.data.lineage", [("name", "=", lname)]):
                    c.call(
                        "fix.data.lineage",
                        "create",
                        {
                            "name": lname,
                            "source_entity_id": entities[i],
                            "target_entity_id": entities[i + 1]
                            if i + 1 < len(entities)
                            else entities[0],
                            "transformation": f"dbt model seed_lineage_{i+1}",
                            "lineage_order": i + 1,
                        },
                    )
            print("seed: data lineage chains (idempotent)")

        # 3 DQ rules
        for name, rtype in [
            ("Orders Complete", "completeness"),
            ("Customer Unique", "uniqueness"),
            ("Events Fresh", "timeliness"),
        ]:
            if not c.first("fix.data.quality.rule", [("name", "=", name)]):
                c.call(
                    "fix.data.quality.rule",
                    "create",
                    {
                        "name": name,
                        "entity_id": entities[0] if entities else 1,
                        "rule_type": rtype,
                        "threshold": 95.0,
                    },
                )
        print("seed: data quality rules (idempotent)")

        # 5 test-equipment records (M45; IoT + PdM need these to attach to)
        for i in range(5):
            ecode = f"SEED-EQ-{i+1:03d}"
            if not c.first("fix.equipment", [("code", "=", ecode)]):
                c.call(
                    "fix.equipment",
                    "create",
                    {
                        "code": ecode,
                        "name": f"Seed Equipment {i+1}",
                        "category": rng.choice(["multimeter", "thermal camera", "otp programmer"]),
                    },
                )
        equipment = c.call("fix.equipment", "search", [("code", "like", "SEED-EQ-")], limit=5)
        print("seed: test equipment (idempotent)")

        # 5 IoT devices
        for i in range(5):
            dname = f"Seed IoT Device {i+1}"
            if not c.first("fix.iot.device", [("name", "=", dname)]):
                c.call(
                    "fix.iot.device",
                    "create",
                    {
                        "name": dname,
                        "device_id": f"SEED-IOT-{i+1:03d}",
                        "device_type": rng.choice(["sensor", "gateway", "tracker"]),
                        "equipment_id": equipment[i] if i < len(equipment) else False,
                        "status": "online",
                    },
                )
        print("seed: IoT devices (idempotent)")

        # 20 telemetry readings, 4 per device. A07 P0 (M48-1): readings arrive only
        # through the stream's ingest, which checks the telemetry consent, so each
        # device gets a temperature stream, and a synthetic seed consent where one
        # is required (trackers, unbound devices). Idempotent by count.
        iot_devices = c.call("fix.iot.device", "search", [], limit=5)
        for dev in iot_devices:
            d = c.call("fix.iot.device", "read", [dev], ["device_type", "equipment_id", "site_id"])[
                0
            ]
            needs_consent = d["device_type"] == "tracker" or not (d["equipment_id"] or d["site_id"])
            if needs_consent and not c.first(
                "fix.iot.consent", [("device_id", "=", dev), ("state", "=", "active")]
            ):
                c.call(
                    "fix.iot.consent",
                    "create",
                    {
                        "subject_type": "device",
                        "device_id": dev,
                        "purpose": "service",
                        "granted_on": "2026-01-01",
                        "notes": "Synthetic seed consent (DE-12): test data only",
                    },
                )
            stream = c.first(
                "fix.iot.stream", [("device_id", "=", dev), ("metric", "=", "temperature")]
            )
            if not stream:
                stream = c.call(
                    "fix.iot.stream",
                    "create",
                    {"device_id": dev, "metric": "temperature", "unit": "C"},
                )
            if not (d["equipment_id"] or d["site_id"]):
                # A07 P1 (M48 FR-IOT-004): a stream bound to no company asset is
                # not activated; it waits in draft until someone binds the device.
                continue
            if c.call("fix.iot.stream", "read", [stream], ["state"])[0]["state"] != "active":
                c.call("fix.iot.stream", "action_activate", [stream])
            have = c.call(
                "fix.iot.telemetry",
                "search_count",
                [("device_id", "=", dev), ("metric", "=", "temperature")],
            )
            for _ in range(max(0, 4 - have)):
                c.call("fix.iot.stream", "ingest", [stream], round(rng.uniform(20, 45), 2))
        print("seed: IoT telemetry records (idempotent)")

        # 3 IoT alerts (name is sequence-generated; guard on message)
        for i, sev in enumerate(["minor", "major", "minor"]):
            msg = f"Seed alert {i+1}: temperature above threshold"
            if not c.first("fix.iot.alert", [("message", "=", msg)]):
                c.call(
                    "fix.iot.alert",
                    "create",
                    {
                        "device_id": iot_devices[i % len(iot_devices)] if iot_devices else 1,
                        "severity": sev,
                        "message": msg,
                    },
                )
        print("seed: IoT alerts (idempotent)")

        # 2 predictive-maintenance predictions
        for i, (pred, days) in enumerate([("failure_predicted", 7), ("healthy", 0)]):
            pname = f"Seed PdM Prediction {i+1}"
            if equipment and not c.first("fix.predictive.maintenance", [("name", "=", pname)]):
                c.call(
                    "fix.predictive.maintenance",
                    "create",
                    {
                        "name": pname,
                        "equipment_id": equipment[i % len(equipment)],
                        "prediction": pred,
                        "confidence": round(rng.uniform(0.75, 0.98), 2),
                        "estimated_days_to_failure": days,
                    },
                )
        print("seed: predictive maintenance predictions (idempotent)")

        # 5 e-waste collections (name is sequence-generated; count-guard)
        ew_count = c.call("fix.ewaste.collection", "search_count", [])
        for i in range(max(0, 5 - ew_count)):
            c.call(
                "fix.ewaste.collection",
                "create",
                {
                    "customer_id": seed_customers[i % len(seed_customers)] if seed_customers else 1,
                    "material_type": rng.choice(["phone", "laptop", "battery"]),
                    "weight_kg": round(rng.uniform(0.2, 3.0), 2),
                    "state": rng.choice(["collected", "triaged", "recycled"]),
                },
            )
        print("seed: e-waste collections (idempotent)")

        # 3 ESG metrics
        for name, mtype, val in [
            ("CO2 Saved Oct", "co2_saved", 150.5),
            ("E-Waste Oct", "ewaste_collected", 45.2),
            ("Refurbished Oct", "devices_refurbished", 12),
        ]:
            if not c.first("fix.esg.metric", [("name", "=", name)]):
                c.call(
                    "fix.esg.metric",
                    "create",
                    {
                        "name": name,
                        "metric_type": mtype,
                        "period": "2026-10",
                        "value": val,
                    },
                )
        print("seed: ESG metrics (idempotent)")

        # --- Anchor backfill (P02-P11): every model with zero rows gets
        # seed data (DE-16: a state seed cannot reach is a state nobody
        # tests). Detail lines remain byproducts of their parents. ---
        def ensure(model, key_domain, vals):
            if not c.first(model, key_domain):
                c.call(model, "create", vals)

        def cycle(ids: list, n: int) -> list:
            # a small database has fewer rows than the anchors index
            return [ids[i % len(ids)] for i in range(n)]

        emp = cycle(c.call("hr.employee", "search", [], limit=5) or [1], 5)
        brn = c.call("fix.branch", "search", [], limit=5) or [1]
        ord_ids = c.call("fix.service.order", "search", [], limit=5) or [1]
        dev_ids = c.call("fix.device", "search", [], limit=5) or [1]
        brd = c.call("fix.brand", "search", [], limit=3) or [1]
        ste = c.call("fix.site", "search", [], limit=3) or [1]
        prj = c.call("fix.project", "search", [], limit=3) or [1]
        veh = c.call("fleet.vehicle", "search", [], limit=3)
        if not veh:
            # A07 P1 (M46): a fresh database has no vehicles, and the old `or [1]`
            # pointed every vehicle row below at a record that does not exist.
            vbrand = c.first("fleet.vehicle.model.brand", [("name", "=", "Seed Van Brand")])
            vbrand = vbrand or c.call(
                "fleet.vehicle.model.brand", "create", {"name": "Seed Van Brand"}
            )
            vmodel = c.first("fleet.vehicle.model", [("name", "=", "Seed Van")])
            vmodel = vmodel or c.call(
                "fleet.vehicle.model", "create", {"name": "Seed Van", "brand_id": vbrand}
            )
            veh = [
                c.call(
                    "fleet.vehicle",
                    "create",
                    {"model_id": vmodel, "license_plate": f"SEED-VAN-{i + 1}"},
                )
                for i in range(2)
            ]
        ncr = c.call("fix.ncr", "search", [], limit=3) or [1]
        ctr = c.call("fix.contract", "search", [], limit=1) or [1]
        mspc = c.call("fix.msp.contract", "search", [], limit=1) or [1]
        mon = c.call("fix.monitored.asset", "search", [], limit=3) or [1]
        rres = c.call("fix.rental.reservation", "search", [], limit=3) or [1]
        # only an approved seller is scored or quotes (BRU-ECM-01); none may exist
        slr = c.call(
            "fix.marketplace.seller",
            "search",
            [("kyc_status", "=", "verified"), ("cfo_approved", "=", True)],
            limit=3,
        )
        slr = cycle(slr, 3) if slr else []
        mvl = c.call("account.move.line", "search", [], limit=3)  # none on a fresh database
        ou = c.call("operating.unit", "search", [], limit=1) or [1]
        cust = seed_customers or [1]

        # Masters
        for i in range(3):
            ensure(
                "fix.org.position",
                [("name", "=", f"Seed Position {i+1}")],
                {"name": f"Seed Position {i+1}"},
            )
            ensure(
                "fix.training.course",
                [("code", "=", f"SEED-CRS-{i+1:02d}")],
                {"code": f"SEED-CRS-{i+1:02d}", "name": f"প্রশিক্ষণ কোর্স {i+1}"},
            )
            ensure(
                "fix.compensation.band",
                [("grade", "=", f"S{i+1}")],
                {"grade": f"S{i+1}", "name": f"Seed Band S{i+1}"},
            )
            ensure(
                "fix.cost.allocation",
                [("name", "=", f"Seed Allocation {i+1}")],
                {"name": f"Seed Allocation {i+1}"},
            )
            ensure(
                "fix.price.explanation",
                [("name", "=", f"Seed Explanation {i+1}")],
                {"name": f"Seed Explanation {i+1}"},
            )
            ensure(
                "fix.vat.treatment",
                [("code", "=", f"SEED-VT-{i+1}")],
                {
                    "code": f"SEED-VT-{i+1}",
                    "name": f"Seed Treatment {i+1}",
                    "treatment_type": ["standard_15", "zero_rated", "exempt"][i],
                    "rate": [15.0, 0.0, 0.0][i],
                },
            )
        for i, intent in enumerate(["reset_request", "battery_issue", "warranty_query"]):
            ensure(
                "fix.assistant.intent",
                [("code", "=", f"SEED-INT-{i+1}")],
                {
                    "code": f"SEED-INT-{i+1}",
                    "name": intent,
                    "name_bn": f"অভিপ্রায় {i+1}",
                    "sample_bn": "আমার ফোনের ব্যাটারি সমস্যা হচ্ছে",
                },
            )
        for i in range(2):
            ensure(
                "fix.approval.matrix",
                [
                    ("decision_domain", "=", ["discount", "write_off"][i]),
                    ("approver_role", "=", "seed_role"),
                ],
                {
                    "approver_role": "seed_role",
                    "decision_domain": ["discount", "write_off"][i],
                    "threshold": 5000 * (i + 1),
                },
            )
            ensure(
                "fix.automation",
                [("code", "=", f"AUT-9{i+1}")],
                {
                    "code": f"AUT-9{i+1}",
                    "trigger": "record_created",
                    "engine": ["odoo_automated_action", "domain_service"][i],
                    "failure_policy": "manual_fallback",
                    "action": "notify owner",
                },
            )
        for i in range(3):
            ensure(
                "fix.control",
                [("name", "=", f"Seed Control {i+1}")],
                {
                    "name": f"Seed Control {i+1}",
                    "control_type": ["preventive", "detective", "corrective"][i],
                    "frequency": ["daily", "weekly", "monthly"][i],
                    "state": "active",
                },
            )
        print("seed: anchor masters (idempotent)")

        # Warehouse structure (M56)
        for i in range(2):
            ensure(
                "fix.warehouse",
                [("code", "=", f"SEED-WH-{i+1}")],
                {
                    "code": f"SEED-WH-{i+1}",
                    "name": f"Seed Warehouse {i+1}",
                    "operating_unit_id": ou[0],
                },
            )
        wh = c.call("fix.warehouse", "search", [("code", "like", "SEED-WH-")], limit=2) or [1]
        for i, zt in enumerate(["receiving", "storage", "dispatch"]):
            ensure(
                "fix.warehouse.zone",
                [("code", "=", f"SEED-ZN-{i+1}")],
                {
                    "code": f"SEED-ZN-{i+1}",
                    "name": f"Seed Zone {i+1}",
                    "warehouse_id": wh[i % len(wh)],
                    "zone_type": zt,
                },
            )
        zn = c.call("fix.warehouse.zone", "search", [("code", "like", "SEED-ZN-")], limit=3) or [1]
        for i in range(3):
            ensure(
                "fix.warehouse.bin",
                [("name", "=", f"SEED-BIN-{i+1}")],
                {"name": f"SEED-BIN-{i+1}", "zone_id": zn[i % len(zn)]},
            )
        print("seed: warehouse structure (idempotent)")

        # Service-delivery chain (estimates -> discount approvals, work
        # orders, QC, front desk, warranty)
        # A02 P0 (M01-4): an estimate's state moves only by send / approve. The
        # order walk seeded sent and approved estimates; a draft is prepared on
        # an order still in diagnosis.
        diag = c.call(
            "fix.service.order",
            "search",
            [("state", "=", "diagnostic"), ("estimate_ids", "=", False)],
            limit=1,
        )
        if diag and not c.first("fix.estimate", [("state", "=", "draft")]):
            c.call("fix.estimate", "create", seed_estimate(diag[0], rng))
        est = c.call("fix.estimate", "search", [], limit=3) or [1]
        for i in range(2):
            ensure(
                "fix.discount.approval",
                [("quotation_id", "=", est[i])],
                {
                    "quotation_id": est[i],
                    "discount_pct": 5.0 * (i + 1),
                    "justification": "Seed margin-approved discount",
                    "operating_unit_id": ou[0],
                    # 5% is within the agent's authority (approved on create);
                    # 10% waits in a DOFA Tier 2 inbox (A03 audit R7)
                },
            )
        # A02 audit M01-P2: a work order is assigned only by a dispatcher
        # (action_assign), and M55 only to a technician rostered today (the
        # server's UTC date); in progress / completed come from the technician
        # app. The order walk seeded passed and failed QC; these checklists are
        # pending.
        rostered = [
            s["employee_id"][0]
            for s in c.call(
                "fix.roster.slot",
                "search_read",
                [("date", "=", datetime.now(UTC).date().isoformat()), ("on_leave", "=", False)],
                ["employee_id"],
                limit=2,
            )
        ]
        for i in range(3):
            ensure("fix.work.order", [("order_id", "=", ord_ids[i])], {"order_id": ord_ids[i]})
            if i and len(rostered) >= i:
                wo = c.first(
                    "fix.work.order", [("order_id", "=", ord_ids[i]), ("state", "=", "pending")]
                )
                if wo:
                    c.call("fix.work.order", "action_assign", [wo], rostered[i - 1])
            ensure("fix.qc.checklist", [("order_id", "=", ord_ids[i])], {"order_id": ord_ids[i]})
        for i in range(2):
            # A02 audit M04: a token moves by call / serve / complete
            if not c.first(
                "fix.token.queue", [("branch_id", "=", brn[i]), ("service_type", "=", "drop_off")]
            ):
                tok = c.call(
                    "fix.token.queue",
                    "create",
                    {"branch_id": brn[i], "service_type": "drop_off", "operating_unit_id": ou[0]},
                )
                if i:
                    for step in ("action_call", "action_serving", "action_complete"):
                        c.call("fix.token.queue", step, [tok])
            ensure(
                "fix.walkin.intake",
                [("branch_id", "=", brn[i]), ("customer_id", "=", cust[i])],
                {
                    "branch_id": brn[i],
                    "customer_id": cust[i],
                    "device_id": dev_ids[i],  # BRU-FRD-12: an intake starts with the device
                    "fault_description": "স্ক্রিন ভাঙা (seed)",
                    "operating_unit_id": ou[0],
                },
            )
            # A02 audit M04-2/-6/-11: a shift closes on the cashier's blind
            # denomination count and is reconciled by a Branch Manager who did
            # not handle the cash (BRU-FRD-11)
            shift_key = [
                ("branch_id", "=", brn[i]),
                ("shift_date", "=", "2026-10-01"),
                ("shift_type", "=", "morning"),
            ]
            if not c.first("fix.cash.shift", shift_key):
                shift = c.call(
                    "fix.cash.shift",
                    "create",
                    {
                        "branch_id": brn[i],
                        "operator_id": emp[i],
                        "shift_date": "2026-10-01",
                        "shift_type": "morning",
                        "opening_float": 5000.0,
                        "operating_unit_id": ou[0],
                    },
                )
                if i:
                    c.call("fix.cash.shift", "write", [shift], {"denom_1000_count": 5})
                    c.call("fix.cash.shift", "action_submit_blind_count", [shift])
                    c.call("fix.cash.shift", "action_confirm_closed", [shift])
                    manager = Client()
                    manager.login(args.db, *(["seed.branch.manager@1000fix.local"] * 2))
                    manager.call("fix.cash.shift", "action_reconcile", [shift])
        for i in range(3):
            ensure(
                "fix.warranty.product",
                [("name", "=", f"Seed Warranty Product {i+1}")],
                {
                    "name": f"Seed Warranty Product {i+1}",
                    "product_type": ["extension", "protection", "extension"][i],
                    "duration_months": [6, 12, 24][i],
                },
            )
        for i in range(5):
            ensure(
                "fix.warranty",
                [("device_id", "=", dev_ids[i]), ("warranty_type", "=", "manufacturer")],
                {
                    "device_id": dev_ids[i],
                    "warranty_type": "manufacturer",
                    "start_date": "2025-10-01",
                    # A07 P1 (M17): status is not typed; the daily warranty expiry
                    # job moves cover past its end date to expired.
                    "end_date": ["2027-10-01", "2026-10-01"][i % 2],
                },
            )
        for i in range(3):
            ensure(
                "fix.warranty.claim",
                [("claim_no", "=", f"SEED-WC-{i+1:03d}")],
                {
                    "claim_no": f"SEED-WC-{i+1:03d}",
                    "brand_id": brd[i],
                    "service_order_id": ord_ids[i],
                    "claim_amount": round(rng.uniform(500, 5000), 2),
                    # A04 build (M09-5 / C6): a claim is raised from a CLOSED
                    # warranty job for its approved estimate, and its state
                    # moves only through submit / propose / decide; the seed
                    # leaves the ladder to the workshop.
                    "operating_unit_id": ou[0],
                },
            )
        print("seed: service-delivery anchors (idempotent)")

        # CX + commercial
        # A03 audit: a campaign runs only through action_launch (social needs no
        # consent list or BTRC window) and ends through action_complete; a call
        # resolves only with a disposition and substantive wrap-up notes
        # (REQ-27.1). Abandoned calls come from the telephony hang-up endpoint,
        # so the second call stays in the queue.
        disposition = c.first("fix.cc.disposition", [("code", "=", "SEED-RES")]) or c.call(
            "fix.cc.disposition",
            "create",
            {"code": "SEED-RES", "name": "Seed: resolved at first contact"},
        )
        for i in range(2):
            cname = f"Seed Campaign {i+1}"
            if not c.first("fix.campaign", [("name", "=", cname)]):
                camp = c.call(
                    "fix.campaign",
                    "create",
                    {
                        "name": cname,
                        "channel": "social",
                        "start_date": "2026-10-01",
                        "end_date": "2026-12-31",
                    },
                )
                c.call("fix.campaign", "action_launch", [camp])
                if i:
                    c.call("fix.campaign", "action_complete", [camp])
            started = f"2026-10-0{i+1} 09:00:00"
            if not c.first(
                "fix.conversation", [("channel", "=", "voice"), ("started_at", "=", started)]
            ):
                conv = c.call(
                    "fix.conversation",
                    "create",
                    {
                        "channel": "voice",
                        "started_at": started,
                        "disposition_id": disposition,
                        "wrapup_notes": "গ্রাহকের প্রশ্নের উত্তর দেওয়া হয়েছে; seed call resolved.",
                        "operating_unit_id": ou[0],
                    },
                )
                if not i:
                    c.call("fix.conversation", "action_resolve", [conv])
        for i in range(3):
            ensure(
                "fix.survey",
                [("service_order_id", "=", ord_ids[i])],
                {
                    "service_order_id": ord_ids[i],
                    "state": ["sent", "responded", "expired"][i],
                    "rating": [False, "4", False][i],
                    "operating_unit_id": ou[0],
                },
            )
            # A03 audit M34: a complaint is assessed, then investigated; it
            # closes only with a root cause and the customer's acceptance, which
            # a seed cannot honestly supply, so the third stops investigating.
            cmp_name = f"SEED-CMP-{i+1:03d}"
            if not c.first("fix.complaint", [("name", "=", cmp_name)]):
                cmp_id = c.call(
                    "fix.complaint",
                    "create",
                    {
                        "name": cmp_name,
                        "customer_id": cust[i],
                        "category": ["service_quality", "delay", "billing"][i],
                        "severity": ["minor", "major", "critical"][i],
                        "description": "Seed complaint description",
                        "operating_unit_id": ou[0],
                    },
                )
                if i:
                    c.call("fix.complaint", "action_assess", [cmp_id])
                if i == 2:
                    c.call("fix.complaint", "action_investigate", [cmp_id])
        for i, lt in enumerate(["labour", "part", "transport"]):
            ensure(
                "fix.rate.card",
                [("product_code", "=", f"SEED-RC-{i+1}"), ("line_type", "=", lt)],
                {"product_code": f"SEED-RC-{i+1}", "line_type": lt, "unit_price": 250.0 * (i + 1)},
            )
        for i in range(3):
            ensure(
                "fix.subscription",
                [("name", "=", f"Seed Subscription {i+1}")],
                {
                    "name": f"Seed Subscription {i+1}",
                    "customer_id": cust[i],
                    "plan": ["basic", "standard", "premium"][i],
                    "billing_cycle": "monthly",
                    "recurring_amount": [499.0, 999.0, 1999.0][i],
                    "start_date": "2026-07-01",
                    "next_invoice_date": "2026-11-01",
                    # A04 build (M39): subscriptions are born per the model
                    # default; past_due arrives from the dunning job and
                    # trial from the plan's terms, never from a typed status.
                    "operating_unit_id": ou[0],
                },
            )
        fxp = c.call("fix.partner", "search", [], limit=3) or [1]
        for i in range(2):
            ensure(
                "fix.storefront.return",
                [("name", "=", f"SEED-RET-{i+1:03d}")],
                {
                    "name": f"SEED-RET-{i+1:03d}",
                    "customer_id": cust[i],
                    "reason": ["defective", "changed_mind"][i],
                    # A04 build: a refund is executed through the payment
                    # rails once the return is approved; the seed stops at
                    # the requested return.
                    "operating_unit_id": ou[0],
                },
            )
            ensure(
                "fix.referral",
                [("name", "=", f"Seed Referral {i+1}")],
                {
                    "name": f"Seed Referral {i+1}",
                    "partner_id": fxp[i % len(fxp)],
                    # A04 build (M40): conversion records the converted
                    # customer and payout basis through action_convert;
                    # a referral is born submitted and stays there.
                },
            )
        print("seed: CX + commercial anchors (idempotent)")

        # Supply chain + circular. A06 P0 (S2/S3): requisition, purchase-order
        # and import states move only through their approval and receipt
        # actions, which need appointed approvers and real receipts, so the
        # seed creates the documents as drafts and leaves the workflow to them.
        for i in range(2):
            ensure(
                "fix.requisition",
                [("description", "=", f"Seed requisition {i+1}")],
                {
                    "description": f"Seed requisition {i+1}",
                    "requested_by": emp[i],
                    "urgency": ["normal", "urgent"][i],
                    "operating_unit_id": ou[0],
                },
            )
            ensure(
                "fix.purchase.order",
                [("vendor_id", "=", cust[i]), ("date_order", "=", "2026-10-01 10:00:00")],
                {
                    "vendor_id": cust[i],
                    "date_order": "2026-10-01 10:00:00",
                    "operating_unit_id": ou[0],
                },
            )
            ensure(
                "fix.import.order",
                [("name", "=", f"SEED-IMP-{i+1:03d}")],
                {"name": f"SEED-IMP-{i+1:03d}"},
            )
            # A02 M03: a consignment is confirmed by its action; delivery needs
            # it in transit with a verified proof of delivery, so none is seeded
            cons_key = [
                ("consignment_type", "=", "pickup"),
                ("scheduled_date", "=", f"2026-10-0{i+2} 08:00:00"),
            ]
            if not c.first("fix.consignment", cons_key):
                cons = c.call(
                    "fix.consignment",
                    "create",
                    {
                        "consignment_type": "pickup",
                        "scheduled_date": f"2026-10-0{i+2} 08:00:00",
                        "operating_unit_id": ou[0],
                    },
                )
                if i:
                    c.call("fix.consignment", "action_confirm", [cons])
            ensure(
                "fix.refurbishment",
                [("name", "=", f"SEED-RFB-{i+1:03d}")],
                {
                    "name": f"SEED-RFB-{i+1:03d}",
                    "step": ["repair", "testing"][i],
                    "state": "pending",
                },
            )
            ensure(
                "fix.rental.damage",
                [("reservation_id", "=", rres[i]), ("category", "=", "cosmetic")],
                {
                    "reservation_id": rres[i],
                    "category": "cosmetic",
                    "cost": round(rng.uniform(200, 1500), 2),
                    "description": "Seed cosmetic damage",
                },
            )
        for i in range(2):
            ensure(
                "fix.data.wipe.certificate",
                [("method", "=", "nist_800_88"), ("name", "=", f"Seed Wipe Cert {i+1}")],
                {"name": f"Seed Wipe Cert {i+1}", "method": "nist_800_88", "device_id": dev_ids[i]},
            )
        # A07 P0 (M17-1): ownership history is written only by a transfer, which
        # moves the owner and records the row together. Rows created directly
        # had contradicted the device's owner (fix_dev devices 552-554).
        for i in range(3):
            if c.first("fix.device.ownership", [("device_id", "=", dev_ids[i])]):
                continue
            d = c.call("fix.device", "read", [dev_ids[i]], ["owner_id", "state"])[0]
            if d["state"] in ("lost", "scrapped") or (
                d["owner_id"] and d["owner_id"][0] == cust[i]
            ):
                continue
            # A07 P1 (M17-1): a transfer needs a reason and the hand-over evidence the
            # new owner accepted, filed against this device (synthetic seed paper).
            att = c.call(
                "ir.attachment",
                "create",
                {
                    "name": f"seed-transfer-{dev_ids[i]}.pdf",
                    "datas": "U0VFRCBUUkFOU0ZFUiBFVklERU5DRQ==",  # "SEED TRANSFER EVIDENCE"
                    "mimetype": "application/pdf",
                },
            )
            evidence = c.call(
                "fix.document",
                "create",
                {
                    "name": f"Seed hand-over {dev_ids[i]} (synthetic test data)",
                    "document_type": "asset_document",
                    "attachment_id": att,
                    "res_model": "fix.device",
                    "res_id": dev_ids[i],
                },
            )
            c.call(
                "fix.device",
                "action_transfer_ownership",
                [dev_ids[i]],
                cust[i],
                "sale",
                None,
                "Synthetic seed sale (test data only)",
                evidence,
            )
        print("seed: supply-chain + circular anchors (idempotent)")

        # Assets + facilities
        for i in range(3):
            ensure(
                "fix.fixed.asset",
                [("name", "=", f"Seed Asset {i+1}")],
                {
                    "name": f"Seed Asset {i+1}",
                    "category": ["it_equipment", "test_gear", "vehicle"][i],
                    "gross": round(rng.uniform(50000, 500000), 2),
                    "life_months": [36, 60, 84][i],
                    "purchase_date": "2025-01-15",
                    "state": ["draft", "active", "disposed"][i],
                },
            )
            ensure(
                "fix.cwip.entry",
                [("name", "=", f"Seed CWIP {i+1}")],
                {
                    "name": f"Seed CWIP {i+1}",
                    "amount": round(rng.uniform(10000, 100000), 2),
                    "state": ["open", "open", "capitalised"][i],
                },
            )
            ensure(
                "fix.calibration",
                [("equipment_id", "=", equipment[i]), ("standard_ref", "=", "SEED-ISO-17025")],
                {
                    "equipment_id": equipment[i],
                    "calibrated_on": "2026-09-01",
                    "next_due": "2027-03-01",
                    "result": ["pass", "pass", "fail"][i],
                    "standard_ref": "SEED-ISO-17025",
                    # A07 P0 (M45-2): a pass is evidence only with its certificate
                    # and the person who performed it (synthetic seed values).
                    "certificate_ref": f"SEED-CAL-CERT-{i+1:03d}",
                    "performed_by": "Seed Calibration Lab",
                },
            )
        # BRTA compliance first: a vehicle is only dispatchable with valid
        # fitness + insurance (cd_vehicle_ext enforces this on assignment).
        # A07 P1 (M46-10): the header expiry dates are derived from the document
        # register and cannot be typed, so the seed records only the documents.
        for vid in veh:
            # A07 P0 (M46-2): the gate decides from the document register, not the
            # header dates, so each seed van carries its mandatory documents. A07
            # P1 (M46-23): a document counts only with its scan (synthetic here).
            for doc_type, valid_to in (
                ("fitness", "2027-06-30"),
                ("insurance", "2027-03-31"),
                ("tax", "2027-06-30"),
                # B3 (decided 4 Nov 2026): the route permit is a mandatory document
                ("route_permit", "2027-06-30"),
            ):
                ensure(
                    "fix.vehicle.document",
                    [
                        ("vehicle_id", "=", vid),
                        ("doc_type", "=", doc_type),
                        ("valid_to", ">=", "2026-12-31"),
                    ],
                    {
                        "vehicle_id": vid,
                        "doc_type": doc_type,
                        "number": f"SEED-{doc_type.upper()}-{vid}",
                        "valid_from": "2026-01-01",
                        "valid_to": valid_to,
                        "evidence_file": "U0VFRCBWRUhJQ0xFIERPQ1VNRU5UIFNDQU4=",  # synthetic
                    },
                )
        for i in range(2):
            ensure(
                "fix.vehicle.assignment",
                [("vehicle_id", "=", veh[i]), ("date", "=", "2026-10-01")],
                {"vehicle_id": veh[i], "date": "2026-10-01"},
            )
            # A07 P0 (M47-1): a work order's state moves only through its actions,
            # so the seed creates a draft and walks it (no cost: no approval).
            if not c.first("fix.facility.work.order", [("name", "=", f"SEED-FAC-{i+1:03d}")]):
                wo = c.call(
                    "fix.facility.work.order",
                    "create",
                    {
                        "name": f"SEED-FAC-{i+1:03d}",
                        "site_id": ste[i],
                        "work_type": ["maintenance", "inspection"][i],
                        "description": "Seed facility work",
                    },
                )
                c.call("fix.facility.work.order", "action_schedule", [wo])
                if i == 1:
                    c.call("fix.facility.work.order", "action_start", [wo])
                    c.call(
                        "fix.facility.work.order",
                        "action_complete",
                        [wo],
                        "Seed inspection done; no defects",
                    )
            ensure(
                "fix.safety.inspection",
                [("name", "=", f"SEED-HSE-{i+1:03d}")],
                {
                    "name": f"SEED-HSE-{i+1:03d}",
                    "branch_id": brn[i],
                    "inspected_on": "2026-09-20",
                    "state": ["done", "follow_up"][i],
                },
            )
        print("seed: asset + facility anchors (idempotent)")

        # Finance (AR -> credit note/dunning; AP -> withholding; VAT/TDS)
        for i in range(3):
            ensure(
                "fix.ar.invoice",
                [("source_model", "=", "fix.service.order"), ("source_id", "=", ord_ids[i])],
                {
                    "customer_id": cust[i],
                    "invoice_date": "2026-09-30",
                    "source_model": "fix.service.order",
                    "source_id": ord_ids[i],
                    "state": ["issued", "paid", "credited"][i],
                    "operating_unit_id": ou[0],
                },
            )
        ar = c.call("fix.ar.invoice", "search", [], limit=3) or [1]
        ensure(
            "fix.credit.note",
            [("invoice_id", "=", ar[0]), ("reason_code", "=", "goodwill")],
            {
                "invoice_id": ar[0],
                "amount": 500.0,
                "reason_code": "goodwill",
                "state": "issued",
                "operating_unit_id": ou[0],
            },
        )
        ensure(
            "fix.dunning",
            [("invoice_id", "=", ar[0]), ("step", "=", "reminder")],
            {"invoice_id": ar[0], "step": "reminder"},
        )
        for i in range(3):
            ensure(
                "fix.vendor.invoice",
                [("invoice_ref", "=", f"SEED-VI-{i+1:03d}")],
                {
                    "vendor_id": cust[i],
                    "invoice_date": "2026-09-25",
                    "invoice_ref": f"SEED-VI-{i+1:03d}",
                    "match_state": ["unmatched", "matched", "blocked"][i],
                    "operating_unit_id": ou[0],
                },
            )
        vi = c.call("fix.vendor.invoice", "search", [], limit=3) or [1]
        ensure(
            "fix.withholding.certificate",
            [("vendor_invoice_id", "=", vi[0])],
            {
                "vendor_invoice_id": vi[0],
                "withheld_amount": 250.0,
                "supplier_name": "Seed Vendor 1",
            },
        )
        for i in range(3):
            ensure(
                "fix.mushak.register",
                [("mushak_no", "=", f"SEED-MUSH-{i+1:03d}")],
                {
                    "mushak_no": f"SEED-MUSH-{i+1:03d}",
                    "invoice_ref": f"SEED-INV-{i+1:03d}",
                    "customer_name": f"Seed Customer {i+1}",
                    "supplier_name": "1000FiX Ltd",
                    "supplier_bin": "0000000000000",
                    "invoice_date": "2026-09-30",
                    "taxable_amount": [10000.0, 20000.0, 5000.0][i],
                    "vat_amount": [1500.0, 3000.0, 0.0][i],
                    "total_payable": [11500.0, 23000.0, 5000.0][i],
                    "operating_unit_id": ou[0],
                },
            )
        ensure(
            "fix.vat.return",
            [("period", "=", "2026-09")],
            {"period": "2026-09", "state": "prepared"},
        )
        ensure(
            "fix.tds.return",
            # the label is the fiscal-year start and quarter (Oct-Dec 2026 = 2026-Q2)
            [("quarter", "=", "2026-Q2")],
            {"quarter": "2026-Q2"},
        )
        for i in range(2):
            ensure(
                "fix.payment.execution",
                [
                    ("source_model", "=", "fix.vendor.invoice"),
                    ("source_id", "=", vi[i]),
                    ("method", "=", "bank_transfer"),
                ],
                {
                    "method": "bank_transfer",
                    "payee": f"Seed Vendor {i+1}",
                    "source_model": "fix.vendor.invoice",
                    "source_id": vi[i],
                    "amount": round(rng.uniform(5000, 50000), 2),
                    "state": ["pending", "executed"][i],
                    "operating_unit_id": ou[0],
                },
            )
        ensure(
            "fix.cash.position",
            [("as_of", "=", "2026-09-30 18:00:00")],
            {"as_of": "2026-09-30 18:00:00"},
        )
        ensure(
            "fix.period.close",
            [("period_end", "=", "2026-09-30")],
            {"period_end": "2026-09-30", "state": "ready_to_close"},
        )
        for i in range(min(2, len(mvl))):
            ensure(
                "fix.journal.dimension",
                [("move_line_id", "=", mvl[i])],
                {"move_line_id": mvl[i], "operating_unit_id": ou[0]},
            )
            ensure(
                "fix.fixed.asset.seam",
                [("move_line_id", "=", mvl[i]), ("name", "=", f"Seed Seam {i+1}")],
                {
                    "move_line_id": mvl[i],
                    "name": f"Seed Seam {i+1}",
                    "amount": round(rng.uniform(1000, 9000), 2),
                    "operating_unit_id": ou[0],
                },
            )
        ensure(
            "fix.payout.run",
            [("name", "=", "Seed Payout 2026-09")],
            {"name": "Seed Payout 2026-09", "period": "2026-09", "state": "approved"},
        )
        print("seed: finance anchors (idempotent)")

        # People (talent, training, performance, payroll-out)
        for i in range(3):
            ensure(
                "fix.job.requisition",
                [("name", "=", f"Seed Requisition {i+1}")],
                {
                    "name": f"Seed Requisition {i+1}",
                    "openings": i + 1,
                    "state": ["open", "hired", "closed"][i],
                },
            )
            ensure(
                "fix.candidate",
                [("name", "=", f"Seed Candidate {i+1}")],
                {"name": f"Seed Candidate {i+1}", "state": ["applied", "interview", "hired"][i]},
            )
            crs = c.call("fix.training.course", "search", [], limit=3) or [1]
            ensure(
                "fix.training.enrollment",
                [("course_id", "=", crs[i]), ("employee_id", "=", emp[i])],
                {
                    "course_id": crs[i],
                    "employee_id": emp[i],
                    "state": ["enrolled", "passed", "failed"][i],
                },
            )
            ensure(
                "fix.performance.scorecard",
                [("employee_id", "=", emp[i]), ("period", "=", "2026-H1")],
                {"employee_id": emp[i], "period": "2026-H1"},
            )
        # Scorecards with real components for the incentive period, spread so
        # every band (>=0.90 / >=0.75 / >=0.60 / below) is represented and the
        # top band can be shown to pay (RAP-M57-01 / RAP-M57-09).
        _bands = [
            (1.00, 1.00, 1.00, 0.00, 1.00),  # score 1.0000 -> 15% band
            (0.85, 0.80, 0.80, 0.02, 0.80),  # score 0.8170 -> 8% band
            (0.70, 0.65, 0.65, 0.04, 0.60),  # score 0.6565 -> 4% band
            (0.40, 0.40, 0.40, 0.10, 0.20),  # score 0.3550 -> below bands, 0%
        ]
        for i, (ftf, sla, csat, rew, salv) in enumerate(_bands):
            if i >= len(emp):
                break
            ensure(
                "fix.performance.scorecard",
                [("employee_id", "=", emp[i]), ("period", "=", "2026-09")],
                {
                    "employee_id": emp[i],
                    "period": "2026-09",
                    "first_time_fix": ftf,
                    "sla_hit": sla,
                    "csat": csat,
                    "rework_rate": rew,
                    "salvage_target": 100000.0,
                    "salvage_value": round(100000.0 * salv, 2),
                },
            )
        ensure(
            "fix.incentive.run",
            [("period", "=", "2026-09")],
            {"period": "2026-09", "band_base": 100000.0},
        )
        _run = c.first("fix.incentive.run", [("period", "=", "2026-09")])
        if _run and not c.first("fix.incentive.line", [("run_id", "=", _run)]):
            # compute for real: the run was previously stamped "computed" with
            # no lines behind it, so the payout bands were never demonstrable
            c.call("fix.incentive.run", "action_compute", [_run])

        # WPPF year-end allocation (BLA 2006 Ch. XV) — absent from the estate,
        # so the 80:10:10 split screen had nothing to show.
        if not c.first("fix.wppf.allocation", [("fiscal_year", "=", "2025-2026")]):
            _wppf = c.call(
                "fix.wppf.allocation",
                "create",
                {
                    "name": "WPPF 2025-2026",
                    "fiscal_year": "2025-2026",
                    "net_profit": 10000000.0,
                    "eligible_workers_count": 100,
                    "fiscal_year_end_date": "2026-06-30",
                },
            )
            c.call("fix.wppf.allocation", "action_calculate", [_wppf])
        for i in range(2):
            ensure(
                "fix.expense.claim",
                [
                    ("employee_id", "=", emp[i]),
                    ("expense_date", "=", "2026-09-28"),
                    ("description", "=", f"Seed expense {i+1}"),
                ],
                {
                    "employee_id": emp[i],
                    "expense_date": "2026-09-28",
                    "amount": round(rng.uniform(500, 3000), 2),
                    "description": f"Seed expense {i+1}",
                    "state": ["submitted", "approved"][i],
                    "operating_unit_id": ou[0],
                },
            )
        # NB: fix.beftn.batch is deliberately NOT seeded — batches are
        # outputs of the payroll approval flow (ACL: read-only to users),
        # same policy as detail lines.
        print("seed: people anchors (idempotent)")

        # MSP + governance + partner-channel
        for i in range(2):
            ensure(
                "fix.msp.alert",
                [
                    ("msp_contract_id", "=", mspc[0]),
                    ("asset_id", "=", mon[i]),
                    ("message", "=", "Seed RMM alert: disk usage 92%"),
                ],
                {
                    "msp_contract_id": mspc[0],
                    "asset_id": mon[i],
                    "message": "Seed RMM alert: disk usage 92%",
                    "severity": ["minor", "major"][i],
                },
            )
            if i:
                alert = c.first(
                    "fix.msp.alert",
                    [("asset_id", "=", mon[i]), ("message", "=", "Seed RMM alert: disk usage 92%")],
                )
                if (
                    alert
                    and c.call("fix.msp.alert", "read", [alert], ["state"])[0]["state"] == "new"
                ):
                    c.call("fix.msp.alert", "action_acknowledge", [alert])
            # A02 M05: consent and the start are captured by the session's
            # actions from the client's own answer; seeded sessions await it
            ensure(
                "fix.remote.session",
                [("asset_id", "=", mon[i]), ("technician_id", "=", emp[i])],
                {
                    "msp_contract_id": mspc[0],
                    "asset_id": mon[i],
                    "technician_id": emp[i],
                    "tool": "rustdesk",
                },
            )
        ensure(
            "fix.msp.service.report",
            [("msp_contract_id", "=", mspc[0]), ("period_label", "=", "2026-09")],
            {"msp_contract_id": mspc[0], "period_label": "2026-09"},
        )
        for i in range(2):
            ensure(
                "fix.capa",
                [("ncr_id", "=", ncr[i])],
                {
                    "ncr_id": ncr[i],
                    "owner_id": emp[i],
                    "corrective_action": "Seed corrective action",
                    "severity": ["minor", "major"][i],
                    "state": ["open", "verified"][i],
                },
            )
            ensure(
                "fix.internal.audit",
                [("branch_id", "=", brn[i]), ("scheduled_on", "=", "2026-10-10")],
                {
                    "branch_id": brn[i],
                    "auditor_id": emp[i],
                    "scheduled_on": "2026-10-10",
                    "scope": "Seed audit scope",
                    "state": ["planned", "reported"][i],
                },
            )
            ensure(
                "fix.supplier.scorecard",
                [("vendor_id", "=", cust[i]), ("period", "=", "2026-Q3")],
                {"vendor_id": cust[i], "period": "2026-Q3", "operating_unit_id": ou[0]},
            )
            if slr:
                ensure(
                    "fix.seller.score",
                    [("seller_id", "=", slr[i]), ("period", "=", "2026-09")],
                    {"seller_id": slr[i], "period": "2026-09"},
                )
            ensure(
                "fix.contract.entitlement",
                [
                    ("contract_id", "=", ctr[0]),
                    ("entitlement_type", "=", ["visits", "incidents"][i]),
                ],
                {
                    "contract_id": ctr[0],
                    "entitlement_type": ["visits", "incidents"][i],
                    "quantity_included": 10.0 * (i + 1),
                },
            )
            ensure(
                "fix.contract.pm.visit",
                [("contract_id", "=", ctr[0]), ("scheduled_date", "=", f"2026-10-0{i+5}")],
                {
                    "contract_id": ctr[0],
                    "device_id": dev_ids[i],
                    "scheduled_date": f"2026-10-0{i+5}",
                    "state": ["scheduled", "completed"][i],
                },
            )
        for i in range(3):
            ensure(
                "fix.project.milestone",
                [("project_id", "=", prj[i % len(prj)]), ("name", "=", f"Seed Milestone {i+1}")],
                {
                    "project_id": prj[i % len(prj)],
                    "name": f"Seed Milestone {i+1}",
                    "state": ["pending", "done", "pending"][i],
                },
            )
        print("seed: MSP + governance anchors (idempotent)")

        # --- Config masters (platform P02-P06): RBAC, calendars, MDM,
        # documents, party model. Without these the modules that consume
        # them have nothing to govern.
        # NB: fix.isolation.tier (T0-T5) and fix.refurb.grade (A-E) are
        # fixed taxonomy -> shipped as noupdate module data (cd_rbac_ext,
        # cd_catalogue), not seeded. fix.country.pack/.line, fix.bd.address,
        # fix.feature.flag and fix.retention.class are pipeline/admin
        # managed by design (AF-09 MD-005; ACL denies user creates).
        # RBAC: roles + SoD controls
        for i in range(3):
            ensure(
                "fix.role",
                [("code", "=", f"R-9{i+1}")],
                {
                    "name": ["Seed Technician", "Seed Auditor", "Seed Branch Manager"][i],
                    "code": f"R-9{i+1}",
                },
            )
        rol = c.call("fix.role", "search", [], limit=3) or [1]
        ensure(
            "fix.sod.control",
            [("code", "=", "SEED-SOD-1")],
            {
                "name": "Seed SoD: quote vs approve",
                "code": "SEED-SOD-1",
                "role_a_id": rol[0],
                "role_b_id": rol[1],
                "conflict_action": "warn",
            },
        )
        # Working calendar (Asia/Dhaka) + a moon-dependent holiday
        ensure(
            "fix.working.calendar",
            [("name", "=", "Seed BD Calendar")],
            {"name": "Seed BD Calendar", "timezone": "Asia/Dhaka"},
        )
        wcal = c.first("fix.working.calendar", [("name", "=", "Seed BD Calendar")])
        if wcal:
            ensure(
                "fix.working.calendar.holiday",
                [("calendar_id", "=", wcal), ("name", "=", "Seed Eid Holiday")],
                {
                    "calendar_id": wcal,
                    "name": "Seed Eid Holiday",
                    "name_bn": "সিড ঈদ ছুটি",
                    "date_from": "2027-03-20",
                    "date_to": "2027-03-22",
                },
            )
        # MDM: match rules, golden rules, a change request
        ensure(
            "fix.mdm.match.rule",
            [("model_name", "=", "res.partner"), ("field_name", "=", "phone")],
            {
                "model_name": "res.partner",
                "field_name": "phone",
                "match_type": "exact",
                "weight": 0.6,
            },
        )
        ensure(
            "fix.mdm.match.rule",
            [("model_name", "=", "res.partner"), ("field_name", "=", "name")],
            {
                "model_name": "res.partner",
                "field_name": "name",
                "match_type": "phonetic",
                "weight": 0.4,
            },
        )
        ensure(
            "fix.mdm.golden.rule",
            [("model_name", "=", "res.partner"), ("field_name", "=", "phone")],
            {"model_name": "res.partner", "field_name": "phone", "strategy": "most_verified"},
        )
        ensure(
            "fix.mdm.change.request",
            [("title", "=", "Seed MDR: merge duplicates")],
            {
                "title": "Seed MDR: merge duplicates",
                "model_name": "res.partner",
                "record_id": cust[0],
                "priority": "normal",
                "state": "submitted",
            },
        )
        # Field rules + dedup rules (need ir.model ids)
        so_model = c.first("ir.model", [("model", "=", "fix.service.order")])
        if so_model:
            phone_field = c.first(
                "ir.model.fields", [("model_id", "=", so_model), ("name", "=", "customer_id")]
            )
            ensure(
                "fix.dedup.rule",
                [("name", "=", "Seed dedup: partner phone")],
                {
                    "name": "Seed dedup: partner phone",
                    "model_id": c.first("ir.model", [("model", "=", "res.partner")]),
                    "scope": "fuzzy",
                    "action": "flag",
                    "match_fields": "phone,name",
                },
            )
            if phone_field:
                ensure(
                    "fix.field.rule",
                    [("model_id", "=", so_model), ("field_id", "=", phone_field)],
                    {"model_id": so_model, "field_id": phone_field, "permission": "read"},
                )
        # Country/BD geography + retention: pipeline-managed (see note
        # above) — deliberately not seeded.
        # Notification config + consents
        for i, cc in enumerate(["transactional", "marketing"]):
            ensure(
                "fix.notification.config",
                [("consent_class", "=", cc), ("channel", "=", "sms")],
                {
                    "consent_class": cc,
                    "channel": "sms",
                    "send_window": "08:00-21:00",
                    "sms_route": ["masking", "non-masking"][i],
                },
            )
        notice = c.first("fix.transparency.notice", []) or c.call(
            "fix.transparency.notice",
            "create",
            {
                "version": "0.1-seed",
                "text_en": "Synthetic seed transparency notice (DE-12).",
                "text_bn": "সিড স্বচ্ছতা বিজ্ঞপ্তি (পরীক্ষামূলক)।",
            },
        )
        for i in range(2):
            ensure(
                "fix.consent",
                [("partner_id", "=", cust[i]), ("channel", "=", "sms"), ("state", "=", "granted")],
                {
                    "partner_id": cust[i],
                    "channel": "sms",
                    "state": "granted",
                    "source": "web",
                    "proof": f"SEED-CONSENT-{i + 1}",
                    "notice_version_id": notice,
                },
            )
        # Identity documents (synthetic checksum-valid style per DE-12)
        for i in range(2):
            ensure(
                "fix.identity.document",
                [("partner_id", "=", cust[i]), ("document_type", "=", "nid_17")],
                {
                    "partner_id": cust[i],
                    "document_type": "nid_17",
                    # verified only by a data steward's routed decision (A02 B1)
                },
            )
        # Party model: roles + hierarchy
        for i, rt in enumerate(["customer", "seller"]):
            ensure(
                "fix.party.role",
                [("partner_id", "=", cust[i]), ("role_type", "=", rt)],
                {"partner_id": cust[i], "role_type": rt, "role_status": "active"},
            )
        ensure(
            "fix.party.hierarchy",
            [
                ("parent_id", "=", cust[0]),
                ("child_id", "=", cust[1]),
                ("relation_type", "=", "corporate"),
            ],
            {"parent_id": cust[0], "child_id": cust[1], "relation_type": "corporate"},
        )
        # Documents + e-signature. NB: documents carry their OWN
        # attachments — never a random ir.attachment: Odoo stores its
        # generated asset bundles there, and an ondelete-restrict
        # reference blocks asset regeneration (found the hard way).
        if not c.first("ir.attachment", [("name", "=", "seed-document.pdf")]):
            c.call(
                "ir.attachment",
                "create",
                {
                    "name": "seed-document.pdf",
                    "datas": "U0VFRCBET0NVTUVOVA==",  # "SEED DOCUMENT"
                    "mimetype": "application/pdf",
                },
            )
        att = [c.first("ir.attachment", [("name", "=", "seed-document.pdf")])] * 2
        for i in range(2):
            ensure(
                "fix.document",
                [("name", "=", f"Seed Document {i+1}")],
                {
                    "name": f"Seed Document {i+1}",
                    "document_type": ["service_report", "evidence_pack"][i],
                    "isolation_tier": ["T1", "T3"][i],
                    "state": "active",
                    "attachment_id": att[i],
                },
            )
        doc = c.call("fix.document", "search", [], limit=2) or [1]
        ensure(
            "fix.document.template",
            [("code", "=", "SEED-TPL-1")],
            {
                "code": "SEED-TPL-1",
                "name": "Seed service report template",
                "name_bn": "সিড সার্ভিস রিপোর্ট টেমপ্লেট",
                "document_type": "service_report",
            },
        )
        ensure(
            "fix.esignature.envelope",
            [("name", "=", "Seed Envelope 1")],
            {
                "name": "Seed Envelope 1",
                "document_id": doc[0],
                "state": "sent",
                "operating_unit_id": ou[0],
            },
        )
        env = c.first("fix.esignature.envelope", [("name", "=", "Seed Envelope 1")])
        if env:
            ensure(
                "fix.esignature.signer",
                [("envelope_id", "=", env)],
                {"envelope_id": env, "partner_id": cust[0]},
            )
        # Circular catalogs: rental SKUs (refurb grades A-E are module data)
        cat = c.call("fix.catalogue.item", "search", [], limit=3) or [1]
        ensure(
            "fix.rental.sku",
            [("catalogue_item_id", "=", cat[0])],
            {"catalogue_item_id": cat[0], "daily_rate": 150.0},
        )
        # Service kits + components
        ensure(
            "fix.service.kit",
            [("name", "=", "Seed Screen Replacement Kit")],
            {
                "name": "Seed Screen Replacement Kit",
                "catalogue_item_id": cat[1 % len(cat)],
                # a kit must have at least one component when it is created
                "component_ids": [
                    (
                        0,
                        0,
                        {"component_type": "part", "quantity": 1.0, "notes": "স্ক্রিন প্যানেল"},
                    )
                ],
            },
        )
        kit = c.first("fix.service.kit", [("name", "=", "Seed Screen Replacement Kit")])
        if kit:
            ensure(
                "fix.service.kit.component",
                [("kit_id", "=", kit), ("component_type", "=", "part")],
                {"kit_id": kit, "component_type": "part", "quantity": 1.0},
            )
        # Zones + geofences (MSP)
        ensure(
            "fix.zone",
            [("code", "=", "SEED-ZONE-1")],
            {"name": "Seed Service Zone", "code": "SEED-ZONE-1"},
        )
        zn1 = c.first("fix.zone", [("code", "=", "SEED-ZONE-1")])
        if zn1:
            ensure(
                "fix.geofence",
                [("name", "=", "Seed Dhaka Circle")],
                {
                    "name": "Seed Dhaka Circle",
                    "zone_id": zn1,
                    "geofence_type": "circle",
                    "geometry_json": '{"lat":23.8,"lng":90.4,"radius_m":15000}',
                },
            )
        # Finance stragglers: bank statement lines + seller quotes
        for i in range(3):
            ensure(
                "fix.bank.statement.line",
                [("date", "=", "2026-09-28"), ("amount", "=", 1000.0 * (i + 1))],
                {
                    "date": "2026-09-28",
                    "amount": 1000.0 * (i + 1),
                    "match_state": ["unmatched", "auto", "manual"][i],
                },
            )
        mo = c.call("fix.marketplace.order", "search", [], limit=2)
        for i in range(min(2, len(mo)) if slr else 0):
            ensure(
                "fix.seller.quote",
                [("marketplace_order_id", "=", mo[i]), ("seller_id", "=", slr[i])],
                {
                    "marketplace_order_id": mo[i],
                    "seller_id": slr[i],
                    "eta_days": 2 + i,
                    "quoted_price": round(rng.uniform(800, 3000), 2),
                    # selection is the order's action (action_select_quote)
                },
            )
        print("seed: config masters (idempotent)")

    print("seed: done (deterministic for --seed " + args.seed + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
