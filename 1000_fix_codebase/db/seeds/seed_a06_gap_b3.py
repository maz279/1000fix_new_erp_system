"""seed_a06_gap_b3.py - synthetic seed rows for the A06 final pass, M43 and M44.

Why this exists. The A06 final pass added screens and controls to M43 Demand
Planning and M44 Import, and on a copy of fix_dev these screens opened empty:
the LC amendment, LC payment, tariff, restriction, permit, C&F agent,
insurance and advance lists, the four M43 reports (accuracy, van par,
stockout, excess), and the live plans, policies and forecasts named no M15
part or location, so nothing could compute. As the A03 build taught
(seed_a03_gap.py), a screen on "No records yet" makes the build look
unchanged. This file closes that, under the seed manifest rules:

  * synthetic only (DE-12), Bengali-first (DE-17), fixed values;
  * state-complete where the model has a lifecycle (DE-16);
  * idempotent: every row carries a `SEED-A06-` marker and every block looks
    for it first, so a second run creates nothing;
  * no outbound anything (DE-11).

Every row goes through the PRODUCTION path: created, then moved by its
`action_*` as the real role, with the approver never the requester. The LC is
approved through the M63 inbox. Nothing writes a state or a stamp.

Not statutory. Tariff rows, restriction rows and the LC facility say in their
own text that they are synthetic test data: no rate, restriction or bank
sanction here is real.

Not configured here. The LC payment block needs the GL account for LC
payments (`cd_import_order.account_code.lc_clearing`). This file never sets
an account mapping; without it, that block reports FAIL and says why.

    PYTHONPATH=. .venv/Scripts/python.exe vendor/odoo/odoo-bin shell \
        -c infra/odoo-conf/local.resolved.conf -d <db> --no-http \
        < db/seeds/seed_a06_gap_b3.py

Each block runs in its own savepoint and reports, so one refusal from a
business rule is visible without hiding what the other blocks did.
"""

import time
from contextlib import contextmanager
from datetime import timedelta

MARK = "SEED-A06-"
RESULTS = []
SYNTHETIC = "Synthetic test data, not a statutory rate."
# a one-page PDF, enough to stand for an attached document
PDF = (
    "JVBERi0xLjQKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAw"
    "IG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8"
    "PC9UeXBlL1BhZ2UvUGFyZW50IDIgMCBSL01lZGlhQm94WzAgMCAyMDAgMjAwXT4+CmVuZG9iagp0"
    "cmFpbGVyCjw8L1Jvb3QgMSAwIFI+PgolJUVPRgo="
)


def seed(env):
    from odoo import fields
    from odoo.addons.cd_import_order.models.fix_import_common import param

    today = fields.Date.context_today(env["res.users"])
    usd = env.ref("base.USD")
    bdt = env.ref("base.BDT")
    company = env.company

    @contextmanager
    def block(name):
        started = time.monotonic()
        print(f"seed_a06_gap_b3: >> {name}", flush=True)
        try:
            with env.cr.savepoint():
                yield
            RESULTS.append(("ok", name, "%.1fs" % (time.monotonic() - started)))
        except Exception as exc:
            first = (str(exc).strip().splitlines() or [""])[0]
            RESULTS.append(("FAIL", name, f"{type(exc).__name__}: {first[:240]}"))

    def user(login):
        found = env["res.users"].search([("login", "=", login)], limit=1)
        if not found:
            raise RuntimeError(f"{login} is missing: run db/seeds/appoint_approvers.py first")
        return found

    def synthetic_user(role, name, groups):
        """A clearly synthetic holder for a role nobody holds (DE-12)."""
        login = f"seed.a06.{role}@1000fix.test"
        found = env["res.users"].search([("login", "=", login)], limit=1)
        if found:
            return found
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create({"name": name, "login": login, "group_ids": [(6, 0, ids)]})
        )

    def ensure(model, domain, vals, as_user=None):
        rec = env[model].search(domain, limit=1)
        if rec:
            return rec
        Model = env[model].with_user(as_user) if as_user else env[model]
        return Model.create(vals)

    admin = env.ref("base.user_admin")  # Import Officer and Demand Planner (seed)
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    location = {
        code: env["fix.stock.location"].search([("code", "=", code)], limit=1)
        for code in ("CENTRAL-WH", "DHAN-HUB", "MOT-HUB", "UTT-HUB", "VAN-DHAN-01")
    }
    supplier = env["fix.supplier"].search([("status", "=", "active")], order="id", limit=1)

    def part(code, name_bn, name_en, cost):
        """A synthetic spare part with the product it is bought as (M44-10)."""
        number = MARK + code
        found = env["fix.spare.part"].search([("part_number", "=", number)], limit=1)
        if found:
            return found
        tmpl = env["product.template"].create(
            {"name": f"{name_bn} ({name_en}) {number}", "standard_price": cost}
        )
        return env["fix.spare.part"].create(
            {
                "name": f"{name_bn} ({name_en})",
                "part_number": number,
                "product_id": tmpl.product_variant_id.id,
                "unit_cost": cost,
            }
        )

    def stock_in(prt, loc, qty, ref):
        """M15 goods receipt, inspected and posted: the stock the reports read."""
        if env["fix.stock.receipt"].search_count([("inspection_notes", "=", MARK + ref)]):
            return
        receipt = env["fix.stock.receipt"].create(
            {
                "partner_id": supplier.partner_id.id,
                "location_id": loc.id,
                "operating_unit_id": loc.operating_unit_id.id or ou.id,
                "inspection_notes": MARK + ref,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "part_id": prt.id,
                            "qty_received": qty,
                            "qty_accepted": qty,
                            "unit_cost": prt.unit_cost,
                        },
                    )
                ],
            }
        )
        if receipt.state == "draft":
            receipt.action_inspect()
        receipt.action_post()

    # ================================================================== M44
    officer = admin
    officer2 = synthetic_user(
        "import.officer",
        "সাকিব রহমান (Synthetic Import Officer 2)",
        ["cd_import_order.group_fix_import_officer"],
    )
    approver = user("seed.import.approver@1000fix.local")
    finance = user("seed.fin.accountant1@1000fix.local")
    treasury = user("seed.fin.admin@1000fix.local")
    imp = {}

    with block("M44 masters: parts and synthetic tariff rows"):
        imp["p1"] = part("IMP-P1", "এলসিডি প্যানেল", "LCD panel", 70500.0)
        imp["p2"] = part("IMP-P2", "লিথিয়াম ব্যাটারি", "Lithium battery", 23500.0)
        imp["p3"] = part("IMP-P3", "ওয়্যারলেস মডিউল", "Wireless module", 11750.0)
        Tariff = env["fix.import.tariff"]
        rows = (
            ("9901.10.00", "p1", 10, 3, 0),
            ("9901.20.00", "p2", 5, 0, 0),
            ("9901.30.00", "p3", 10, 3, 20),
        )
        for code, _key, cd, rd, sd in rows:
            row = Tariff.search([("sro_ref", "=", MARK + "TARIFF-" + code)], limit=1)
            if not row:
                row = Tariff.with_user(officer).create(
                    {
                        "hs_code": code,
                        "description": f"সিন্থেটিক শুল্ক হার — {SYNTHETIC}",
                        "sro_ref": MARK + "TARIFF-" + code,
                        "date_from": today - timedelta(days=60),
                        "cd_pct": cd,
                        "rd_pct": rd,
                        "sd_pct": sd,
                        "vat_pct": 15,
                        "at_pct": 5,
                        "ait_pct": 5,
                    }
                )
            if row.state == "draft":
                row.with_user(approver).action_activate()
        # a draft row awaiting its approver, and a row retired by its approver
        draft = Tariff.search([("sro_ref", "=", MARK + "TARIFF-DRAFT")], limit=1)
        if not draft:
            Tariff.with_user(officer).create(
                {
                    "hs_code": "9901.40.00",
                    "description": f"সিন্থেটিক খসড়া — {SYNTHETIC}",
                    "sro_ref": MARK + "TARIFF-DRAFT",
                    "date_from": today,
                    "cd_pct": 25,
                    "vat_pct": 15,
                }
            )
        retired = Tariff.search([("sro_ref", "=", MARK + "TARIFF-RETIRED")], limit=1)
        if not retired:
            retired = Tariff.with_user(officer).create(
                {
                    "hs_code": "9901.50.00",
                    "description": f"সিন্থেটিক অবসরপ্রাপ্ত — {SYNTHETIC}",
                    "sro_ref": MARK + "TARIFF-RETIRED",
                    "date_from": today - timedelta(days=120),
                    "cd_pct": 15,
                    "vat_pct": 15,
                }
            )
        if retired.state == "draft":
            retired.with_user(approver).action_activate()
        if retired.state == "active":
            retired.with_user(approver).action_retire(str(today - timedelta(days=1)))

    with block("M44 HS rulings for the seed parts"):
        for key, code in (("p1", "9901.10.00"), ("p2", "9901.20.00"), ("p3", "9901.30.00")):
            product = imp[key].product_id
            hs = env["fix.import.hs"].search([("product_id", "=", product.id)], limit=1)
            if not hs:
                hs = (
                    env["fix.import.hs"]
                    .with_user(officer)
                    .create(
                        {
                            "product_id": product.id,
                            "hs_code": code,
                            "description": "সিন্থেটিক শ্রেণিবিন্যাস (synthetic classification)",
                            "ruling_ref": MARK + "RUL-" + code,
                        }
                    )
                )
            if hs.state == "draft":
                hs.with_user(approver).action_rule()
            imp["hs_" + key] = hs

    with block("M44 restrictions (synthetic register)"):
        Restriction = env["fix.import.restriction"]
        restricted = Restriction.search([("legal_ref", "=", MARK + "RESTRICTED")], limit=1)
        if not restricted:
            restricted = Restriction.with_user(officer).create(
                {
                    "name": "সিন্থেটিক নিয়ন্ত্রিত পণ্য — ওয়্যারলেস মডিউল (synthetic, not statutory)",
                    "product_id": imp["p3"].product_id.id,
                    "restriction_type": "restricted",
                    "permit_type": "Synthetic radio-equipment NOC (test data)",
                    "issuing_authority": "Synthetic authority (test data)",
                    "legal_ref": MARK + "RESTRICTED",
                    "date_from": today - timedelta(days=30),
                }
            )
        if restricted.state == "draft":
            restricted.with_user(approver).action_activate()
        imp["restriction"] = restricted
        prohibited = Restriction.search([("legal_ref", "=", MARK + "PROHIBITED")], limit=1)
        if not prohibited:
            Restriction.with_user(officer).create(
                {
                    "name": "সিন্থেটিক নিষিদ্ধ শ্রেণি (synthetic prohibited prefix, draft)",
                    "hs_code_pattern": "9902",
                    "restriction_type": "prohibited",
                    "legal_ref": MARK + "PROHIBITED",
                    "date_from": today,
                }
            )
        old = Restriction.search([("legal_ref", "=", MARK + "RETIRED")], limit=1)
        if not old:
            old = Restriction.with_user(officer).create(
                {
                    "name": "সিন্থেটিক পুরোনো নিয়ন্ত্রণ (synthetic, retired)",
                    "hs_code_pattern": "9903",
                    "restriction_type": "restricted",
                    "permit_type": "Synthetic permit (test data)",
                    "legal_ref": MARK + "RETIRED",
                    "date_from": today - timedelta(days=200),
                }
            )
        if old.state == "draft":
            old.with_user(approver).action_activate()
        if old.state == "active":
            old.with_user(approver).action_retire()

    with block("M44 C&F agents"):
        Agent = env["fix.import.cnf.agent"]
        for code, name, end in (
            ("CNF-1", "চট্টগ্রাম ক্লিয়ারিং এজেন্সি (Chattogram Clearing, synthetic)", "approved"),
            ("CNF-2", "বেনাপোল ফরওয়ার্ডার্স (Benapole Forwarders, synthetic)", "blocked"),
            ("CNF-3", "ঢাকা কাস্টমস হাউস এজেন্ট (Dhaka Custom House Agent, synthetic)", "draft"),
        ):
            agent = Agent.search([("licence_no", "=", MARK + code)], limit=1)
            if not agent:
                agent = Agent.with_user(officer).create(
                    {
                        "name": name,
                        "supplier_id": supplier.id,
                        "licence_no": MARK + code,
                        "licence_expiry": today + timedelta(days=365),
                    }
                )
            if end != "draft" and agent.state == "draft":
                agent.with_user(approver).action_approve()
            if end == "blocked" and agent.state == "approved":
                agent.with_user(approver).action_block("Licence renewal under review (seed)")
            imp.setdefault("agent", agent)

    with block("M44 synthetic LC facility (M50)"):
        Facility = env["fix.bank.facility"]
        facility = Facility.search([("name", "=", MARK + "LC-FACILITY")], limit=1)
        if not facility:
            liability = env["account.account"].search(
                [("account_type", "=", "liability_current"), ("company_ids", "in", company.id)],
                order="code",
                limit=1,
            )
            lender = ensure(
                "res.partner",
                [("ref", "=", MARK + "AD-BANK")],
                {"name": "সিন্থেটিক এডি ব্যাংক (Synthetic AD Bank)", "ref": MARK + "AD-BANK"},
            )
            facility = Facility.with_user(treasury).create(
                {
                    "name": MARK + "LC-FACILITY",
                    "company_id": company.id,
                    "lender_id": lender.id,
                    "facility_type": "lc",
                    "currency_id": bdt.id,
                    "limit_amount": 50_000_000.0,
                    "liability_account_id": liability.id,
                    "expiry_date": today + timedelta(days=365),
                }
            )
        if facility.state == "draft":
            facility.with_user(treasury).action_activate()
        imp["facility"] = facility

    def import_order(name, lines, fob):
        found = env["fix.import.order"].search([("name", "=", name)], limit=1)
        if found:
            return found
        return (
            env["fix.import.order"]
            .with_user(officer)
            .create(
                {
                    "name": name,
                    "supplier_id": supplier.partner_id.id,
                    "operating_unit_id": ou.id,
                    "currency_id": usd.id,
                    "fob_value": fob,
                    "freight_cost": round(fob * 0.05, 2),
                    "insurance_cost": round(fob * 0.01, 2),
                    "fx_rate": 117.5,
                    "fx_rate_source": "সিন্থেটিক হার (synthetic rate, seed)",
                    "fx_rate_date": today,
                    "incoterm": "fob",
                    "location_id": location["CENTRAL-WH"].id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "part_id": imp[key].id,
                                "hs_id": imp["hs_" + key].id,
                                "quantity": qty,
                                "unit_price": price,
                            },
                        )
                        for key, qty, price in lines
                    ],
                }
            )
        )

    def cover(order, sum_insured):
        ins = env["fix.import.insurance"].search(
            [("policy_no", "=", MARK + "MC-" + order.name)], limit=1
        )
        if not ins:
            insurer = ensure(
                "res.partner",
                [("ref", "=", MARK + "INSURER")],
                {"name": "সিন্থেটিক বীমা কোম্পানি (Synthetic Insurer)", "ref": MARK + "INSURER"},
            )
            ins = (
                env["fix.import.insurance"]
                .with_user(officer)
                .create(
                    {
                        "order_id": order.id,
                        "insurer_id": insurer.id,
                        "policy_no": MARK + "MC-" + order.name,
                        "currency_id": usd.id,
                        "sum_insured": sum_insured,
                        "premium": round(sum_insured * 0.01, 2),
                        "cover_from": today - timedelta(days=1),
                        "cover_to": today + timedelta(days=120),
                    }
                )
            )
        if ins.state == "draft":
            ins.with_user(approver).action_verify()
        return ins

    with block("M44 LC-route order, cargo cover and proforma"):
        order = import_order(MARK + "IMP-LC", (("p1", 10, 600.0), ("p2", 20, 200.0)), 10000.0)
        imp["order_lc"] = order
        cover(order, 11000.0)  # 110% of FOB covers the CIF
        pf = env["fix.import.proforma"].search([("proforma_no", "=", MARK + "PI-LC")], limit=1)
        if not pf:
            pf = (
                env["fix.import.proforma"]
                .with_user(officer)
                .create(
                    {
                        "order_id": order.id,
                        "proforma_no": MARK + "PI-LC",
                        "currency_id": usd.id,
                        "amount": 10000.0,
                    }
                )
            )
        if pf.state == "received":
            pf.with_user(approver).action_approve()

    with block("M44 LC opened through the M63 inbox, and its LCA"):
        order = imp["order_lc"]
        letter = env["fix.import.lc"].search([("lc_no", "=", MARK + "LC-001")], limit=1)
        if not letter:
            letter = (
                env["fix.import.lc"]
                .with_user(officer)
                .create(
                    {
                        "order_id": order.id,
                        "lc_no": MARK + "LC-001",
                        "bank": "সিন্থেটিক এডি ব্যাংক (Synthetic AD Bank)",
                        "facility_id": imp["facility"].id,
                        "currency_id": bdt.id,
                        "amount": 1_175_000.0,
                        "expiry": today + timedelta(days=150),
                        "margin_pct": 10,
                    }
                )
            )
        lca = env["fix.import.lca"].search([("lca_no", "=", MARK + "LCA-001")], limit=1)
        if not lca:
            lca = (
                env["fix.import.lca"]
                .with_user(officer)
                .create(
                    {
                        "lc_id": letter.id,
                        "lca_no": MARK + "LCA-001",
                        "bank": "সিন্থেটিক এডি ব্যাংক (Synthetic AD Bank)",
                        "currency_id": bdt.id,
                        "amount": letter.amount,
                    }
                )
            )
        if lca.state == "applied":
            lca.with_user(approver).action_approve()
        if letter.state == "draft":
            letter.with_user(officer).action_apply()
        if letter.state == "applied" and letter.approval_state != "approved":
            if letter.approval_state != "pending":
                letter.with_user(officer).action_request_approval(
                    justification="LCD panels and batteries for the Q4 repair plan (seed)"
                )
            task = letter.approval_request_id.task_ids.filtered(
                lambda t: t.state == "pending" and t.assigned_user_id == approver
            )
            if not task:
                raise RuntimeError(f"the LC approval was not routed to {approver.login}")
            task.with_user(approver).action_approve(comment="Approved (seed)")
        if letter.state == "applied":
            letter.with_user(officer).action_open()
        imp["lc"] = letter

    with block("M44 LC amendments (one applied, one draft)"):
        letter = imp["lc"]
        Amend = env["fix.import.lc.amendment"]
        applied = Amend.search(
            [
                ("lc_id", "=", letter.id),
                ("reason", "=", MARK + "extend shipment window (expiry only)"),
            ],
            limit=1,
        )
        if not applied:
            applied = Amend.with_user(officer).create(
                {
                    "lc_id": letter.id,
                    # expiry only: a blank new amount means the amount is unchanged
                    "new_expiry": letter.expiry + timedelta(days=30),
                    "reason": MARK + "extend shipment window (expiry only)",
                }
            )
        if applied.state == "draft" and applied.approval_state != "approved":
            if applied.approval_state != "pending":
                applied.with_user(officer).action_request_approval(
                    justification="Supplier asked for 30 more days (seed)"
                )
            task = applied.approval_request_id.task_ids.filtered(
                lambda t: t.state == "pending" and t.assigned_user_id == approver
            )
            if not task:
                raise RuntimeError(f"the amendment was not routed to {approver.login}")
            task.with_user(approver).action_approve(comment="Approved (seed)")
        if applied.state == "draft":
            applied.with_user(officer).action_apply_amendment()
        if not Amend.search_count(
            [
                ("lc_id", "=", letter.id),
                ("reason", "=", MARK + "extend for partial shipment (expiry only)"),
            ]
        ):
            Amend.with_user(officer).create(
                {
                    "lc_id": letter.id,
                    "new_expiry": letter.expiry + timedelta(days=15),
                    "reason": MARK + "extend for partial shipment (expiry only)",
                }
            )

    with block("M44 LC payment"):
        if not param(env, "cd_import_order.account_code.lc_clearing"):
            raise RuntimeError(
                "skipped: cd_import_order.account_code.lc_clearing is not set, and this seed "
                "never sets an account mapping"
            )
        letter = imp["lc"]
        Pay = env["fix.import.lc.payment"]
        if not Pay.search_count([("reference", "=", MARK + "TT-001")]):
            Pay.with_user(finance).create(
                {"lc_id": letter.id, "amount": 350_000.0, "reference": MARK + "TT-001"}
            )

    with block("M44 shipping documents with files (B/L verified)"):
        order = imp["order_lc"]
        Doc = env["fix.import.shipdoc"]
        for doc_type, end, with_file in (
            ("bl", "verified", True),
            ("invoice", "received", True),
            ("coo", "received", False),
            ("packing", "pending", False),
        ):
            ref = MARK + doc_type.upper() + "-001"
            doc = Doc.search([("ref", "=", ref)], limit=1)
            if not doc:
                vals = {"order_id": order.id, "doc_type": doc_type, "ref": ref}
                if with_file:
                    vals.update(document=PDF, document_name=f"{ref.lower()}.pdf")
                doc = Doc.with_user(officer).create(vals)
            if end != "pending" and doc.state == "pending":
                doc.with_user(officer).action_receive()
            if end == "verified" and doc.state == "received":
                doc.with_user(officer2).action_verify()

    with block("M44 advance-route order, permit and advances"):
        order = import_order(MARK + "IMP-ADV", (("p3", 40, 100.0),), 4000.0)
        cover(order, 4400.0)
        permit = env["fix.import.permit"].search([("permit_no", "=", MARK + "NOC-001")], limit=1)
        if not permit:
            permit = (
                env["fix.import.permit"]
                .with_user(officer)
                .create(
                    {
                        "order_id": order.id,
                        "restriction_id": imp["restriction"].id,
                        "permit_no": MARK + "NOC-001",
                        "issuer": "Synthetic authority (test data)",
                        "issued_on": today - timedelta(days=5),
                        "valid_to": today + timedelta(days=180),
                        "document": PDF,
                        "document_name": "seed-a06-noc-001.pdf",
                    }
                )
            )
        if permit.state == "draft":
            permit.with_user(approver).action_verify()
        Advance = env["fix.import.advance"]
        for ref, amount, end in (
            ("APG-001", 400.0, "approved"),
            ("APG-002", 300.0, "requested"),
            ("APG-003", 250.0, "rejected"),
            ("APG-004", 200.0, "draft"),
        ):
            adv = Advance.search([("guarantee_ref", "=", MARK + ref)], limit=1)
            if not adv:
                adv = Advance.with_user(officer).create(
                    {
                        "order_id": order.id,
                        "currency_id": usd.id,
                        "amount": amount,
                        "bank": "সিন্থেটিক এডি ব্যাংক (Synthetic AD Bank)",
                        "guarantee_ref": MARK + ref,
                        "purpose": "সরবরাহকারীর অগ্রিম (supplier advance, seed)",
                    }
                )
            if end != "draft" and adv.state == "draft":
                adv.with_user(officer).action_request()
            if end == "approved" and adv.state == "requested":
                adv.with_user(approver).action_approve("Supplier requires 10% on order (seed)")
            if end == "rejected" and adv.state == "requested":
                adv.with_user(approver).action_reject("No guarantee on file (seed)")

    # ================================================================== M43
    planner = admin
    dapprover = user("seed.demand.approver@1000fix.local")
    dem = {}

    with block("M43 parts with their products"):
        dem["d1"] = part("DEM-D1", "মাদারবোর্ড", "Motherboard", 9500.0)
        dem["d2"] = part("DEM-D2", "চার্জিং পোর্ট", "Charging port", 450.0)
        dem["d3"] = part("DEM-D3", "স্ক্রিন প্রটেক্টর", "Screen guard", 250.0)
        dem["d4"] = part("DEM-D4", "কম্প্রেসর", "Compressor", 12000.0)

    with block("M43 stock through M15 receipts"):
        stock_in(dem["d1"], location["DHAN-HUB"], 5, "RCV-D1")
        stock_in(dem["d2"], location["MOT-HUB"], 500, "RCV-D2")
        stock_in(dem["d3"], location["VAN-DHAN-01"], 4, "RCV-D3")
        stock_in(dem["d4"], location["UTT-HUB"], 3, "RCV-D4")

    def policy(key, loc_code, daily, lead, review, reason):
        prt = dem[key]
        loc = location[loc_code]
        Policy = env["fix.demand.policy"]
        pol = Policy.search(
            [("part_id", "=", prt.id), ("location_id", "=", loc.id), ("previous_id", "=", False)],
            limit=1,
        )
        if not pol:
            pol = Policy.with_user(planner).create(
                {
                    "product_id": prt.product_id.id,
                    "part_id": prt.id,
                    "location_id": loc.id,
                    "lead_time_days": lead,
                    "review_period_days": review,
                    "service_level_pct": "95",
                    "provisional_daily_demand": daily,
                    "provisional_reason": MARK + reason,
                }
            )
        if pol.state == "draft" and pol.provisional_state == "entered":
            pol.with_user(dapprover).action_approve_provisional()
        if pol.state == "draft":
            pol.with_user(dapprover).action_activate()
        dem["pol_" + key] = pol
        return pol

    with block("M43 policies on provisional demand (no history yet)"):
        policy("d1", "DHAN-HUB", 2.0, 10, 30, "new model, no M15 history")
        policy("d2", "MOT-HUB", 1.0, 5, 5, "slow mover, no M15 history")
        policy("d3", "VAN-DHAN-01", 0.5, 7, 14, "van kit item, no M15 history")
        policy("d4", "UTT-HUB", 3.0, 10, 30, "seasonal compressor, no M15 history")
        # a draft revision awaiting its approver
        d2 = dem["pol_d2"]
        if d2.state == "active" and not env["fix.demand.policy"].search_count(
            [("previous_id", "=", d2.id)]
        ):
            d2.with_user(planner).action_revise()

    def forecast(key, loc_code, period, qty, end):
        prt = dem[key]
        Forecast = env["fix.demand.forecast"]
        fc = Forecast.search(
            [
                ("part_id", "=", prt.id),
                ("location_id", "=", location[loc_code].id),
                ("period", "=", period),
            ],
            limit=1,
        )
        if not fc:
            fc = Forecast.with_user(planner).create(
                {
                    "product_id": prt.product_id.id,
                    "part_id": prt.id,
                    "location_id": location[loc_code].id,
                    "period": period,
                    "has_override": True,
                    "override_qty": qty,
                    "override_rationale": MARK + "planner estimate, no M15 history",
                }
            )
        if end in ("approved", "published") and fc.state == "draft":
            fc.with_user(dapprover).action_approve()
        if end == "published" and fc.state == "approved":
            fc.with_user(planner).action_publish()
        return fc

    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    period = f"{this_month.year:04d}-{this_month.month:02d}"
    last_period = f"{last_month.year:04d}-{last_month.month:02d}"

    with block("M43 forecasts with a part and location"):
        forecast("d4", "UTT-HUB", period, 90.0, "published")
        forecast("d1", "DHAN-HUB", period, 60.0, "approved")
        forecast("d1", "DHAN-HUB", last_period, 55.0, "published")  # a closed month: accuracy
        forecast("d2", "MOT-HUB", period, 30.0, "draft")

    def plan(name, key, loc_code):
        prt = dem[key]
        found = env["fix.demand.plan"].search([("name", "=", name)], limit=1)
        if found:
            return found
        nxt = (this_month + timedelta(days=32)).replace(day=1)
        return (
            env["fix.demand.plan"]
            .with_user(planner)
            .create(
                {
                    "name": name,
                    "period_start": this_month,
                    "period_end": nxt - timedelta(days=1),
                    "product_id": prt.product_id.product_tmpl_id.id,
                    "part_id": prt.id,
                    "location_id": location[loc_code].id,
                    "operating_unit_id": location[loc_code].operating_unit_id.id or ou.id,
                    "vendor_id": supplier.partner_id.id,
                }
            )
        )

    with block("M43 plans: released to M16, approved"):
        released = plan(MARK + "PLAN-D4", "d4", "UTT-HUB")
        if released.state == "draft":
            released.with_user(dapprover).action_approve()
        if released.state == "approved":
            released.with_user(planner).action_generate_pr()
        approved = plan(MARK + "PLAN-D1", "d1", "DHAN-HUB")
        if approved.state == "draft":
            approved.with_user(dapprover).action_approve()


def report(env):
    counts = []
    for model in (
        "fix.import.tariff",
        "fix.import.restriction",
        "fix.import.cnf.agent",
        "fix.import.insurance",
        "fix.import.permit",
        "fix.import.lc.amendment",
        "fix.import.lc.payment",
        "fix.import.advance",
        "fix.import.shipdoc",
        "fix.demand.policy",
        "fix.demand.forecast",
        "fix.demand.plan",
    ):
        counts.append(f"  {model:<26} {env[model].sudo().search_count([])}")
    print("seed_a06_gap_b3: blocks")
    for status, name, detail in RESULTS:
        print("  [{}] {}{}".format(status, name, (" - " + detail) if detail else ""))
    print("seed_a06_gap_b3: row counts after seeding")
    print("\n".join(counts))


try:
    env  # noqa: B018 - provided by `odoo-bin shell`
except NameError:
    raise SystemExit(
        "seed_a06_gap_b3: run inside `odoo-bin shell` (see the module docstring)"
    ) from None
seed(env)  # noqa: F821 - `env` comes from odoo-bin shell
env.cr.commit()  # noqa: F821
report(env)  # noqa: F821
