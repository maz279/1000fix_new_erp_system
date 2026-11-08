"""seed_a06_gap_b2.py - synthetic M16 Procurement and M42 Supplier rows, A06 final pass.

Why this exists. The A06 final pass added PO Goods Receipts (M16-po-receipts),
supplier bank-detail changes (M42-bank), the GR/IR and emergency-purchase
reports, and made the procure-to-pay path reachable end to end. On a copy of
fix_dev those screens opened on "No records yet" (and Price Variance had no
product bought twice), so the build looked unchanged. This file gives them rows
that tell one story: two suppliers onboarded through M42, then requisitions
taken through approval, PO, receipt, inspection and bill to a closed PO, with
others left at each stage on the way.

Rules, as seed_a03_gap.py:
  * synthetic only, Bengali-first names, fixed values (no random);
  * every row is made by the PRODUCTION path as the role the workflow needs:
    requester, buyer, receiver, supplier stewards and approver, DOFA approvers
    deciding from the M63 inbox, AP clerk. Approver is never the requester. No
    state, approval stamp or guarded field is ever written;
  * idempotent: every block looks for its own `SEED-A06-` marker first, so a
    second run creates nothing;
  * no outbound anything, and no config parameter or account mapping is set.

Roles. Buyer, Receiver and Supplier Steward are held only by admin on fix_dev,
and segregation of duties refuses one person playing them all, so synthetic
holders are created (login seed.a06.<role>@1000fix.test, like
appoint_approvers.py). The DOFA approvers, the Supplier Approver and the AP
clerk are the existing seed users.

    PYTHONPATH=. .venv/Scripts/python.exe vendor/odoo/odoo-bin shell \
        -c infra/odoo-conf/local.resolved.conf -d <db> --no-http \
        < db/seeds/seed_a06_gap_b2.py

Each block runs in its own savepoint and reports, so one refusal from a
business rule is visible without hiding what the other blocks did.
"""

import base64
import time
from contextlib import contextmanager
from datetime import timedelta

MARK = "SEED-A06-"
RESULTS = []
PDF = base64.b64encode(b"%PDF-1.4\n% SEED-A06 synthetic test document, not a real record\n")


def seed(env):
    from odoo import fields

    now = fields.Datetime.now()
    today = fields.Date.context_today(env["res.users"])
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], order="id", limit=1)

    @contextmanager
    def block(name):
        started = time.monotonic()
        print(f"seed_a06_gap_b2: >> {name}", flush=True)
        try:
            with env.cr.savepoint():
                yield
            RESULTS.append(("ok", name, f"{time.monotonic() - started:.1f}s"))
        except _Skip as exc:
            RESULTS.append(("ok", name, f"already seeded, nothing created: {exc}"))
        except Exception as exc:
            first = (str(exc).strip().splitlines() or [""])[0]
            RESULTS.append(("FAIL", name, f"{type(exc).__name__}: {first[:220]}"))

    # ---------------------------------------------------------------- people
    def user(login, name, groups):
        Users = env["res.users"].with_context(no_reset_password=True)
        found = Users.search([("login", "=", login)], limit=1)
        ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
        if found:
            return found
        return Users.create(
            {
                "name": name,
                "login": login,
                "email": login,
                "group_ids": [(6, 0, ids)],
                "company_id": env.company.id,
                "company_ids": [(6, 0, env.company.ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )

    def employee(u, name):
        Emp = env["hr.employee"]
        return Emp.search([("user_id", "=", u.id)], limit=1) or Emp.create(
            {"name": name, "user_id": u.id, "company_id": env.company.id}
        )

    def existing(login):
        u = env["res.users"].search([("login", "=", login)], limit=1)
        if not u:
            raise RuntimeError(f"seed user {login} is missing: run appoint_approvers.py first")
        return u

    with block("roles: synthetic requesters, buyer, receiver, supplier stewards"):
        requester = user("seed.a06.requester@1000fix.test", "তানভীর আহমেদ (SEED-A06 Requester)", [])
        requester2 = user(
            "seed.a06.requester2@1000fix.test", "শারমিন সুলতানা (SEED-A06 Field Requester)", []
        )
        buyer = user(
            "seed.a06.buyer@1000fix.test",
            "রাকিব হাসান (SEED-A06 Buyer)",
            ["cd_requisition.group_fix_procurement_buyer"],
        )
        receiver = user(
            "seed.a06.receiver@1000fix.test",
            "মোস্তফা কামাল (SEED-A06 Receiver)",
            ["cd_requisition.group_fix_procurement_receiver"],
        )
        steward = user(
            "seed.a06.steward@1000fix.test",
            "সাদিয়া রহমান (SEED-A06 Supplier Steward)",
            ["cd_vendor_portal.group_fix_supplier_steward"],
        )
        steward2 = user(
            "seed.a06.steward2@1000fix.test",
            "ইমরান খান (SEED-A06 Supplier Steward)",
            ["cd_vendor_portal.group_fix_supplier_steward"],
        )
        employee(requester, "তানভীর আহমেদ (SEED-A06)")
        employee(requester2, "শারমিন সুলতানা (SEED-A06)")

    requester = env["res.users"].search([("login", "=", "seed.a06.requester@1000fix.test")])
    requester2 = env["res.users"].search([("login", "=", "seed.a06.requester2@1000fix.test")])
    buyer = env["res.users"].search([("login", "=", "seed.a06.buyer@1000fix.test")])
    receiver = env["res.users"].search([("login", "=", "seed.a06.receiver@1000fix.test")])
    steward = env["res.users"].search([("login", "=", "seed.a06.steward@1000fix.test")])
    steward2 = env["res.users"].search([("login", "=", "seed.a06.steward2@1000fix.test")])
    sup_approver = existing("seed.supplier.approver@1000fix.local")
    ap = existing("seed.fin.accountant1@1000fix.local")
    emp = env["hr.employee"].search([("user_id", "=", requester.id)], limit=1)
    emp2 = env["hr.employee"].search([("user_id", "=", requester2.id)], limit=1)

    # ---------------------------------------------------------------- catalogue
    with block("catalogue: category and three purchased products"):
        categ = env["product.category"].search(
            [("name", "=", "কম্প্রেসর ও কুলিং যন্ত্রাংশ (SEED-A06)")], limit=1
        ) or env["product.category"].create({"name": "কম্প্রেসর ও কুলিং যন্ত্রাংশ (SEED-A06)"})
        for code, name in (
            ("P1", "এসি কম্প্রেসর ১.৫ টন"),
            ("P2", "রেফ্রিজারেন্ট গ্যাস R410A সিলিন্ডার"),
            ("P3", "আউটডোর ফ্যান মোটর"),
        ):
            full = f"{name} ({MARK}{code})"
            if not env["product.product"].search([("name", "=", full)], limit=1):
                env["product.product"].create(
                    {"name": full, "categ_id": categ.id, "default_code": MARK + code}
                )

    def product(code):
        return env["product.product"].search([("default_code", "=", MARK + code)], limit=1)

    # ---------------------------------------------------------------- M42
    def onboard(code, name, segment):
        """Register, document, screen, qualify and activate, each step by its role."""
        Supplier = env["fix.supplier"]
        found = Supplier.search([("name", "=", f"{name} ({MARK}{code})")], limit=1)
        if found:
            return found, False
        partner = env["res.partner"].create(
            {"name": f"{name} ({MARK}{code})", "is_company": True, "ref": MARK + code}
        )
        sup = Supplier.with_user(steward).create(
            {"name": partner.name, "partner_id": partner.id, "segment": segment}
        )
        docs = env["fix.supplier.document"]
        for doc_type in ("trade_licence", "tin", "vat"):
            docs |= (
                env["fix.supplier.document"]
                .with_user(steward)
                .create(
                    {
                        "supplier_id": sup.id,
                        "doc_type": doc_type,
                        "number": f"{MARK}{code}-{doc_type.upper()}",
                        "valid_from": today - timedelta(days=30),
                        "valid_to": today + timedelta(days=365),
                        "file": PDF,
                        "file_filename": f"{MARK}{code}-{doc_type}.pdf",
                    }
                )
            )
        docs.with_user(steward2).action_verify()  # a second steward verifies
        for screening_type in ("sanctions", "coi", "abac"):
            screening = (
                env["fix.supplier.screening"]
                .with_user(steward)
                .create(
                    {
                        "supplier_id": sup.id,
                        "screening_type": screening_type,
                        "result": "clear",
                        "reference": f"{MARK}{code}-SCR-{screening_type.upper()}",
                    }
                )
            )
            screening.with_user(steward).action_clear()
        qual = (
            env["fix.supplier.qualification"]
            .with_user(steward)
            .create(
                {
                    "supplier_id": sup.id,
                    "score": 84,
                    "notes": MARK + "synthetic qualification, not a real assessment",
                }
            )
        )
        qual.with_user(steward).action_start()
        qual.with_user(sup_approver).action_approve()  # the scorer never approves
        gate = (
            env["fix.supplier.activation"]
            .with_user(steward)
            .create({"supplier_id": sup.id, "qualification_id": qual.id})
        )
        gate.with_user(sup_approver).action_activate()  # the preparer never activates
        return sup, True

    with block("M42 suppliers: two onboarded through documents, screening, qualification, gate"):
        sup1, _new = onboard("SUP1", "ঢাকা কুলিং সলিউশনস লিমিটেড", "preferred")
        sup2, _new = onboard("SUP2", "চট্টগ্রাম রেফ্রিজারেশন সাপ্লাই", "transactional")
        expect(sup1.status == "active" and sup2.status == "active", (sup1.status, sup2.status))

    sup1 = env["fix.supplier"].search([("name", "like", MARK + "SUP1")], limit=1)
    sup2 = env["fix.supplier"].search([("name", "like", MARK + "SUP2")], limit=1)

    with block("M42-bank: bank-detail changes (rejected, confirmed, awaiting confirmation)"):
        Change = env["fix.supplier.bank.change"]
        if Change.search([("verification_ref", "like", MARK)], limit=1):
            raise _Skip("bank-detail changes")
        bank = env["res.bank"].search([("name", "=", "সিড টেস্ট ব্যাংক (SEED-A06)")], limit=1) or env[
            "res.bank"
        ].create({"name": "সিড টেস্ট ব্যাংক (SEED-A06)"})

        def propose(sup, number, ref):
            change = Change.with_user(steward).create(
                {
                    "supplier_id": sup.id,
                    "acc_number": number,
                    "bank_id": bank.id,
                    "routing_number": "999000001",
                    "acc_holder_name": sup.name,
                    "verification_ref": f"{MARK}{ref} call-back on the number held on file (synthetic)",
                    "evidence_ref": f"{MARK}{ref}-EVIDENCE",
                }
            )
            change.with_user(steward).action_propose()
            return change

        first = propose(sup1, "9990000000000101", "BANK1")
        first.with_user(steward2).action_reject(
            reason="Call-back could not reach the number on file"
        )
        second = propose(sup1, "9990000000000102", "BANK2")
        second.with_user(steward2).action_confirm()  # a second person confirms
        propose(sup2, "9990000000000201", "BANK3")  # left proposed: payments stay blocked

    # ---------------------------------------------------------------- M16
    def decide(record):
        """The pending inbox task, decided by the approver it was routed to."""
        task = record.sudo().approval_request_id.task_ids.filtered(lambda t: t.state == "pending")[
            :1
        ]
        if not task:
            raise RuntimeError(f"{record.display_name} has no pending approval task")
        task.with_user(task.assigned_user_id).action_approve(comment=MARK + "approved")
        return task.assigned_user_id

    def requisition(key, who, emp_rec, prod, qty, unit, vendor, urgency="normal", days_ago=0):
        Req = env["fix.requisition"]
        desc = "{} ({}{})".format(prod.name.split(" (")[0], MARK, key)
        found = Req.search([("description", "=", desc)], limit=1)
        if found:
            return found, False
        req = Req.with_user(who).create(
            {
                "description": desc,
                "justification": f"{MARK}{key}: synthetic demand for the seed walk",
                "requested_by": emp_rec.id,
                "operating_unit_id": ou.id,
                "product_id": prod.id,
                "qty": qty,
                "estimate_amount": qty * unit,
                "vendor_id": vendor.partner_id.id,
                "cost_centre": "CC-SEED-A06",
                "required_by": today + timedelta(days=21 - days_ago),
                "urgency": urgency,
            }
        )
        return req, True

    def to_po(req, days_ago, approve=True):
        """Approved requisition -> PO, dated back, approval requested and decided."""
        req.with_user(buyer).action_convert_to_po()
        po = req.purchase_order_id
        po.with_user(buyer).write(
            {
                "date_order": now - timedelta(days=days_ago),
                "promised_date": today + timedelta(days=10 - days_ago),
            }
        )
        po.with_user(buyer).action_submit_for_approval(
            justification=f"{req.description}: synthetic purchase for the seed walk"
        )
        if approve:
            decide(po)
        return po

    def acknowledge(po, days):
        po.with_user(buyer).action_acknowledge_on_behalf(
            evidence=f"{MARK} vendor e-mail confirmation (synthetic)",
            confirmed_date=str(today + timedelta(days=days)),
        )

    def receive(po, qty_by_line=None, post=True):
        po.with_user(receiver).action_start_receipt()
        receipt = po.sudo().receipt_ids.filtered(lambda r: r.state == "draft")[:1]
        receipt.with_user(receiver).write({"delivery_note_ref": f"{MARK}CHALLAN-{po.id}"})
        for line, qty in (qty_by_line or {}).items():
            receipt.line_ids.filtered(lambda rl, pl=line: rl.po_line_id == pl).with_user(
                receiver
            ).write({"qty_received": qty})
        if post:
            receipt.with_user(receiver).action_post()
        return receipt

    def inspect(receipt, accepted):
        rline = receipt.line_ids[:1]
        insp = (
            env["fix.procurement.inspection"]
            .with_user(receiver)
            .create(
                {
                    "receipt_line_id": rline.id,
                    "qty_accepted": accepted,
                    "notes": MARK + "synthetic inspection",
                }
            )
        )
        insp.with_user(receiver).action_confirm()
        return insp

    def bill(po, ref, qty, unit):
        return (
            env["fix.vendor.invoice"]
            .with_user(ap)
            .create(
                {
                    "vendor_id": po.vendor_id.id,
                    "invoice_ref": MARK + ref,
                    "bill_type": "po",
                    "requisition_id": po.id,
                    "operating_unit_id": ou.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": po.line_ids[:1].product_id.id,
                                "description": po.line_ids[:1].product_id.name,
                                "quantity": qty,
                                "unit_price": unit,
                                "tds_category": "supply_of_goods",
                            },
                        )
                    ],
                }
            )
        )

    with block(
        "walk W1: requisition to closed PO (approved, sent, acknowledged, received, inspected, billed, closed)"
    ):
        req, new = requisition("W1", requester, emp, product("P1"), 2, 18000.0, sup1, days_ago=12)
        if not new:
            raise _Skip("W1")
        req.with_user(requester).action_submit()
        decide(req)
        po = to_po(req, days_ago=12)
        po.with_user(buyer).action_send()
        acknowledge(po, days=2)  # on time: a confirmed date before sending is refused (M16-11)
        receipt = receive(po)
        inspect(receipt, accepted=2)
        matched = bill(po, "BILL-W1", 2, 18000.0)
        expect(matched.match_state == "matched", matched.match_detail)
        po.with_user(buyer).action_close()
        expect(po.state == "closed", po.state)

    with block(
        "walk W2: partly received, inspected; the rest on a draft receipt (GR/IR received, not invoiced)"
    ):
        req, new = requisition("W2", requester, emp, product("P1"), 2, 18500.0, sup1, days_ago=6)
        if not new:
            raise _Skip("W2")
        req.with_user(requester).action_submit()
        decide(req)
        po = to_po(req, days_ago=6)
        po.with_user(buyer).action_send()
        acknowledge(po, days=3)
        line = po.line_ids[:1]
        first = receive(po, {line: 1})
        inspect(first, accepted=1)
        receive(po, post=False)  # the second delivery keyed, not yet posted
        expect(po.state == "partially_received", po.state)

    with block(
        "walk W3: sent, awaiting the vendor; billed ahead of receipt (GR/IR invoiced, not received)"
    ):
        req, new = requisition("W3", requester, emp, product("P2"), 5, 4000.0, sup1, days_ago=3)
        if not new:
            raise _Skip("W3")
        req.with_user(requester).action_submit()
        decide(req)
        po = to_po(req, days_ago=3)
        po.with_user(buyer).action_send()
        early = bill(po, "BILL-W3-EARLY", 5, 4000.0)
        expect(early.match_state == "blocked", early.match_state)

    with block("walk W4: price 20% up on the previous PO, PO approval pending in the M63 inbox"):
        req, new = requisition("W4", requester, emp, product("P2"), 5, 4800.0, sup1, days_ago=1)
        if not new:
            raise _Skip("W4")
        req.with_user(requester).action_submit()
        decide(req)
        po = to_po(req, days_ago=1, approve=False)
        expect(po.approval_state == "pending", po.approval_state)

    with block("requisitions: one draft, one awaiting approval in the inbox"):
        draft, new = requisition("R5", requester, emp, product("P3"), 3, 6500.0, sup2)
        if not new:
            raise _Skip("R5/R6")
        pending, _new = requisition("R6", requester, emp, product("P3"), 4, 6500.0, sup2)
        pending.with_user(requester).action_submit()
        expect(pending.approval_state == "pending", pending.approval_state)

    with block(
        "emergency purchases: one released and sent pending post-hoc approval, one approved post-hoc"
    ):
        e1, new = requisition(
            "E1", requester2, emp2, product("P3"), 1, 9500.0, sup2, urgency="emergency"
        )
        if not new:
            raise _Skip("E1/E2")
        e1.with_user(requester2).action_emergency_release(
            reason="Job card SEED-A06-JOB-1: shop AC down, fan motor failed (synthetic)"
        )
        e1.with_user(buyer).action_convert_to_po()
        e1.purchase_order_id.with_user(buyer).action_send()  # the release covers it
        e2, _new = requisition(
            "E2", requester2, emp2, product("P2"), 2, 6000.0, sup2, urgency="emergency"
        )
        e2.with_user(requester2).action_emergency_release(
            reason="Job card SEED-A06-JOB-2: chiller out of gas at a client site (synthetic)"
        )
        decide(e2)  # the named approver signs off after the fact
        expect(
            (e1.emergency_state, e2.emergency_state) == ("pending", "approved"),
            (e1.emergency_state, e2.emergency_state),
        )


def expect(condition, detail):
    """The seed's own check of where a walk ended: raises, so the block FAILs."""
    if not condition:
        raise RuntimeError(f"unexpected outcome: {detail}")


class _Skip(Exception):
    """A block whose rows exist already: reported as ok, nothing created."""


def report(env):
    print("seed_a06_gap_b2: blocks")
    for status, name, detail in RESULTS:
        print("  [{}] {}{}".format(status, name, (" - " + detail) if detail else ""))
    print(f"seed_a06_gap_b2: seeded rows (marker {MARK})")
    for model, field in (
        ("fix.supplier", "name"),
        ("fix.supplier.bank.change", "verification_ref"),
        ("fix.requisition", "description"),
        ("fix.vendor.invoice", "invoice_ref"),
    ):
        print(f"  {model:<28} {env[model].sudo().search_count([(field, 'like', MARK)])}")
    for model in ("fix.purchase.receipt", "fix.purchase.order", "fix.procurement.inspection"):
        print(f"  {model:<28} {env[model].sudo().search_count([])} (all rows)")


try:
    env  # noqa: B018 - provided by `odoo-bin shell`
except NameError:
    raise SystemExit(
        "seed_a06_gap_b2: run inside `odoo-bin shell` (see the module docstring)"
    ) from None
seed(env)  # noqa: F821 - `env` comes from odoo-bin shell
env.cr.commit()  # noqa: F821
report(env)  # noqa: F821
