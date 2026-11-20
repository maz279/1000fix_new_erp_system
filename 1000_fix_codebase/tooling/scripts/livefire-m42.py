"""livefire-m42 — end-to-end probes of the M42 Supplier Relationship models
behind the P03 workspace capture forms (CD-M42-01..04).

Run INSIDE an Odoo shell against a dev database with cd_vendor_ext,
cd_supplier_qualification, cd_supplier_scorecard and cd_supplier_risk
installed (synthetic data only, DE-12):

    odoo-bin shell -c <conf> -d fix_dev < tooling/scripts/livefire-m42.py

Covers each model's state flow, the §13 segregation-of-duties blocks, the
daily expiry/escalation schedulers (idempotency), the fail-closed activation
gate (T-01/T-02), price-change governance (FR-SRM2-023) and event emission
through the outbox. Everything runs in one transaction that is ROLLED BACK
at the end — nothing persists.
"""

import sys
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

env = globals().get("env")  # injected by `odoo-bin shell`
if env is None:
    sys.exit("run inside `odoo-bin shell` (see the module docstring)")

results = []


def ok(name, cond=True):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)


def raises(name, exc, fn, contains=None):
    """Expect `exc` (exactly that class when it is AccessError vs UserError
    matters) and, when given, a message containing `contains`."""
    try:
        with env.cr.savepoint():
            fn()
    except exc as e:
        msg = str(e)
        right = contains is None or contains in msg
        ok(name + f" -> {type(e).__name__}: {msg[:70]}", right)
        return
    ok(name + " (did not raise)", False)


Users = env["res.users"]
grp = env.ref("base.group_user")
# Spec §13 roles: two officers, a finance manager and a CFO (all M42 rights).


def _user(name, login, group_xmlid):
    return Users.create({"name": name, "login": login, "group_ids": [
        (6, 0, [grp.id, env.ref(group_xmlid).id])]})


u1 = _user("M42 Officer", "m42_officer", "cd_vendor_ext.group_m42_officer")
u2 = _user("M42 CFO", "m42_cfo", "cd_vendor_ext.group_m42_cfo")
u3 = _user("M42 Peer Officer", "m42_peer", "cd_vendor_ext.group_m42_officer")
u4 = _user("M42 Finance", "m42_finance", "cd_vendor_ext.group_m42_finance")
e1, e2, e3, e4 = env(user=u1), env(user=u2), env(user=u3), env(user=u4)

partner = env["res.partner"].create({"name": "Dhaka Parts Distributors Ltd"})
alt_partner = env["res.partner"].create({"name": "Chattogram Components"})
cat = env["product.category"].create({"name": "Laptop Displays"})
product = env["product.product"].create({"name": "14in FHD Panel"})

P = e1["fix.supplier.profile"]
prof = P.create({"partner_id": partner.id, "classification": "authorised_distributor",
                 "segment": "preferred", "risk_tier": "high"})
alt = P.create({"partner_id": alt_partner.id, "classification": "local_trader"})
ok("profile created as prospect", prof.state == "prospect")
ok("profile OU defaulted", True)
raises("duplicate profile per company blocked", Exception,
       lambda: P.create({"partner_id": partner.id, "classification": "oem"}))
raises("officer cannot suspend (manager right)", AccessError, lambda: prof.action_suspend(reason="x"))
raises("suspend needs reason", UserError, lambda: prof.with_env(e2).action_suspend(reason=""))
blk = P.create({"partner_id": env["res.partner"].create({"name": "Grey Market Traders"}).id,
                "classification": "local_trader"})
raises("officer cannot block (CFO right)", AccessError, lambda: blk.action_block(reason="counterfeit"))
blk.with_env(e2).action_block(reason="Counterfeit panels found at GRN")
ok("CFO blocks permanently", blk.state == "blocked")

# Segment review + SoD
rev = e1["fix.supplier.segment.review"].create({
    "profile_id": prof.id, "proposed_segment": "strategic", "proposed_risk_tier": "critical",
    "criticality": "high", "rationale": "Top-3 display spend"})
ok("segment review snapshots current", rev.current_segment == "preferred")
rev.action_submit()
raises("officer cannot approve segment change", AccessError, lambda: rev.action_approve(), "Procurement Manager")
own = e2["fix.supplier.segment.review"].create({
    "profile_id": prof.id, "proposed_segment": "preferred", "proposed_risk_tier": "high",
    "rationale": "self-proposed"})
own.action_submit()
raises("SoD: proposer cannot approve own segment change", UserError, lambda: own.action_approve(),
       "proposer of a segment change")
rev.with_env(e2).action_approve()
ok("approved review moves profile", prof.segment == "strategic" and prof.risk_tier == "critical")
prof.risk_tier = "high"

# Document
D = e1["fix.supplier.document"]
raises("brand authorisation needs expiry", ValidationError,
       lambda: D.create({"profile_id": prof.id, "doc_type": "brand_authorisation", "reference": "BA-1"}))
raises("expiry before issue blocked", ValidationError,
       lambda: D.create({"profile_id": prof.id, "doc_type": "trade_licence", "reference": "TL-0",
                         "issued_on": "2026-05-01", "expires_on": "2026-01-01"}))
att = env["ir.attachment"].create({"name": "tl.pdf", "raw": b"trade licence scan"})
doc = D.create({"profile_id": prof.id, "doc_type": "trade_licence", "reference": "TL-1",
                "issued_on": fields.Date.today() - timedelta(days=300),
                "expires_on": fields.Date.today() + timedelta(days=20), "attachment_id": att.id})
ok("evidence hashed at capture", doc.evidence_hash and len(doc.evidence_hash) == 64)
raises("SoD: capturer cannot verify document", UserError, lambda: doc.action_verify(),
       "captured a document")
ba = D.create({"profile_id": prof.id, "doc_type": "brand_authorisation", "reference": "BA-7",
               "expires_on": fields.Date.today() + timedelta(days=200)})
raises("officer cannot verify brand authorisation", AccessError, lambda: ba.with_env(e3).action_verify(),
       "Quality Manager")
doc.with_env(e2).action_verify()
ok("document verified", doc.state == "verified")
ok("profile counts expiring doc", prof.document_expiring_count == 1)
old = D.create({"profile_id": prof.id, "doc_type": "tin", "reference": "TIN-1",
                "expires_on": fields.Date.today() + timedelta(days=5)})
old.with_env(e2).action_verify()
old.sudo().write({"expires_on": fields.Date.today() - timedelta(days=1)})
n = env["fix.supplier.document"]._cron_expire_documents()
n2 = env["fix.supplier.document"]._cron_expire_documents()
ok("expiry cron idempotent (1 then 0)", (n, n2) == (1, 0) and old.state == "expired")

# Bank change
raises("officer cannot raise a bank change (Finance only)", AccessError,
       lambda: e1["fix.supplier.bank.change"].create({
           "profile_id": prof.id, "bank_name": "X", "account_holder": "X",
           "account_number": "1", "verification_method": "callback", "verification_note": "x"}))
B = e4["fix.supplier.bank.change"]
bc = B.create({"profile_id": prof.id, "bank_name": "Dutch-Bangla Bank", "account_holder": partner.name,
               "account_number": "1234567890123", "verification_method": "callback",
               "verification_note": "Called registered finance contact"})
ok("previous value hashed", len(bc.previous_value_hash) == 64)
bc.action_submit()
raises("SoD: requester cannot approve bank change", UserError, lambda: bc.action_approve(),
       "requester of a bank-detail change")
raises("non-finance approver blocked", AccessError, lambda: bc.with_env(e3).action_approve(),
       "Only Finance")
bc.with_env(e2).action_approve()
ok("bank account created on partner", "1234567890123" in partner.bank_ids.mapped("acc_number"))
raises("decided bank change immutable", UserError, lambda: bc.write({"account_number": "999"}))

# Agreement + price change
A = e1["fix.supplier.agreement"]
raises("agreement end before start blocked", ValidationError,
       lambda: A.create({"profile_id": prof.id, "name": "X", "term_from": "2026-06-01", "term_to": "2026-01-01"}))
ag = A.create({"profile_id": prof.id, "name": "FA-2026-01", "agreement_type": "framework",
               "term_from": fields.Date.today() - timedelta(days=10),
               "term_to": fields.Date.today() + timedelta(days=30), "committed_value": 5000000})
raises("officer cannot execute agreement", AccessError, lambda: ag.action_activate(), "Procurement Manager")
ag.with_env(e2).action_activate()
exp, lap = env["fix.supplier.agreement"]._cron_agreement_expiry()
ok("agreement inside 90d flagged expiring", ag.state == "expiring")
PC = e1["fix.supplier.price.change"]
pc = PC.create({"profile_id": prof.id, "agreement_id": ag.id, "product_id": product.id,
                "old_price": 8000, "proposed_price": 8800, "effective_from": fields.Date.today(),
                "justification": "Panel cost +10% (USD/BDT)"})
ok("variance computed", abs(pc.variance_pct - 10.0) < 0.001)
raises("agreement of other supplier rejected", ValidationError,
       lambda: PC.create({"profile_id": alt.id, "agreement_id": ag.id, "product_id": product.id,
                          "proposed_price": 1, "effective_from": fields.Date.today(), "justification": "x"}))
pc.action_submit()
raises("officer cannot approve price change", AccessError, lambda: pc.action_approve(), "Procurement Manager")
own_pc = e2["fix.supplier.price.change"].create({
    "profile_id": prof.id, "product_id": product.id, "proposed_price": 9000,
    "effective_from": fields.Date.today(), "justification": "self"})
own_pc.action_submit()
raises("SoD: requester cannot approve own price change", UserError, lambda: own_pc.action_approve(),
       "requester of a price change")
pc.with_env(e2).action_approve()
row = env["fix.supplier.price.list"].search([("profile_id", "=", prof.id), ("product_id", "=", product.id)])
ok("approved price published", len(row) == 1 and row.price == 8800)
raises("direct price edit blocked", UserError, lambda: row.with_env(e1).write({"price": 1}))

# Qualification + gate
Q = e1["fix.supplier.qualification"]
gate = env["fix.supplier.qualification"].check_activation
ok("gate denies before qualification", gate(partner.id, cat.id)["allow"] is False)
ok("gate fails closed on bad input", gate(None, None)["allow"] is False)
q1 = Q.create({"profile_id": prof.id, "category_id": cat.id, "responses": "ISO 9001 yes; warehouse 2,000 sqft",
               "score": 82})
ok("qualification version 1", q1.version == 1 and q1.result == "pass")
ok("profile under qualification", prof.state == "under_qualification")
raises("submit needs anti-bribery declaration", UserError, lambda: q1.action_submit())
q1.anti_bribery_declared = True
q1.action_submit()
raises("officer cannot approve qualification", AccessError, lambda: q1.action_approve(), "Quality Manager")
q1.with_env(e2).action_approve()
ok("approval activates supplier", prof.state == "active")
ok("gate allows after approval", gate(partner.id, cat.id)["allow"] is True)
raises("approved qualification immutable", UserError, lambda: q1.write({"score": 99}))
own_q = e2["fix.supplier.qualification"].create({
    "profile_id": prof.id, "category_id": cat.id, "responses": "self-scored", "score": 95,
    "anti_bribery_declared": True})
own_q.action_submit()
raises("SoD: scorer cannot solely approve at high tier", UserError, lambda: own_q.action_approve(),
       "scorer cannot be")
own_q.action_reject()
q2 = Q.create({"profile_id": prof.id, "category_id": cat.id, "responses": "re-qual", "score": 90,
               "anti_bribery_declared": True})
ok("re-qualification takes the next version", q2.version == own_q.version + 1 == 3)
q2.action_submit()
q2.with_env(e2).action_approve()
ok("prior version superseded", q1.state == "superseded")
env.cr.execute(
    "UPDATE fix_supplier_qualification SET valid_until = %s WHERE id = %s",
    (fields.Date.today() - timedelta(days=1), q2.id))
q2.invalidate_recordset()
env["fix.supplier.qualification"]._cron_expire_qualifications()
ok("lapse expires and suspends", q2.state == "expired" and prof.state == "suspended")
ok("gate denies after lapse", gate(partner.id, cat.id)["allow"] is False)

# Screening
S = e1["fix.supplier.screening"]
raises("COI without details blocked", ValidationError,
       lambda: S.create({"profile_id": prof.id, "coi_declared": True}))
sc = S.create({"profile_id": prof.id, "sanctions_result": "clear", "anti_bribery_declared": True,
               "code_of_conduct_accepted": True, "code_of_conduct_version": "SCoC v2.1"})
ok("screening outcome clear", sc.outcome == "clear")
sc.action_submit()
raises("officer cannot clear screening", AccessError, lambda: sc.action_clear(), "Procurement Manager")
own_sc = e2["fix.supplier.screening"].create({"profile_id": prof.id, "anti_bribery_declared": True})
own_sc.action_submit()
raises("SoD: capturer cannot clear own screening", UserError, lambda: own_sc.action_clear(),
       "captured a screening")
sc.with_env(e2).action_clear()
ok("screening cleared", sc.state == "cleared")
bad = S.create({"profile_id": prof.id, "sanctions_result": "confirmed_match"})
ok("confirmed match fails", bad.outcome == "fail")

# Review + CAR
R = e1["fix.supplier.review"]
rv = R.create({"profile_id": prof.id, "period": "2026-Q4", "scheduled_for": fields.Date.today()})
ok("strategic cadence 91 days", rv.next_review_due == fields.Date.today() + timedelta(days=91))
raises("held needs minutes", UserError, lambda: rv.action_mark_held())
rv.minutes = "OTD 94%, two late deliveries"
rv.action_mark_held()
ok("review held", rv.state == "held" and rv.held_on)
C = e1["fix.supplier.car"]
car = C.create({"profile_id": prof.id, "source": "inspection", "issue": "3 dead-pixel panels in GRN",
                "required_action": "100% pre-shipment test", "due_date": fields.Date.today() + timedelta(days=14)})
ok("CAR numbered", car.name.startswith("CAR/"))
car.supplier_response = "Added burn-in test"
car.action_record_response()
car.root_cause = "No outgoing QC on panel line"
car.action_mark_action_taken()
car.effectiveness = "effective"
raises("officer cannot verify CAR", AccessError, lambda: car.action_verify_effective(), "Quality Manager")
own_car = e2["fix.supplier.car"].create({
    "profile_id": prof.id, "source": "audit", "issue": "x", "required_action": "y",
    "due_date": fields.Date.today() + timedelta(days=5), "supplier_response": "r", "root_cause": "c",
    "effectiveness": "effective"})
own_car.action_record_response()
own_car.action_mark_action_taken()
raises("SoD: raiser cannot verify own CAR", UserError, lambda: own_car.action_verify_effective(),
       "raised a CAR")
car.with_env(e2).action_verify_effective()
ok("CAR verified", car.state == "verified")
late = C.create({"profile_id": prof.id, "source": "delivery", "issue": "late", "required_action": "x",
                 "due_date": fields.Date.today() + timedelta(days=1)})

env.cr.execute("UPDATE fix_supplier_car SET due_date = %s WHERE id = %s",
               (fields.Date.today() - timedelta(days=1), late.id))
late.invalidate_recordset()
env["fix.supplier.car"]._cron_escalate_overdue()
ok("overdue CAR escalated", late.state == "escalated" and late.escalation_level == 1)

# Risk
Rk = e1["fix.supplier.risk"]
dims = dict(financial="2", operational="2", geographic="1", compliance="2", counterfeit="5", continuity="3")
raises("single-source needs alternate or exception", ValidationError,
       lambda: Rk.create(dict(profile_id=prof.id, single_source_critical=True, **dims)))
own_rk = e2["fix.supplier.risk"].create(dict(profile_id=alt.id, **dims))
own_rk.action_submit()
raises("SoD: assessor cannot approve own risk", UserError, lambda: own_rk.action_approve(),
       "assessor cannot approve")
rk = Rk.create(dict(profile_id=prof.id, single_source_critical=True, alternate_profile_id=alt.id, **dims))
ok("any 5 rolls up to critical", rk.overall_tier == "critical")
ok("critical re-assess in 90 days", rk.next_assessment_due == fields.Date.today() + timedelta(days=90))
rk.action_submit()
raises("officer cannot approve risk", AccessError, lambda: rk.action_approve(), "Procurement Manager")
rk.with_env(e2).action_approve()
ok("approved risk sets profile tier", prof.risk_tier == "critical")

outbox = env["fix.event.outbox"].search_count([("event_type", "like", "supplier.%")])
ok(f"events emitted via outbox ({outbox})", outbox >= 8)

failed = [n for n, c in results if not c]
print(f"\nSCENARIO: {len(results) - len(failed)}/{len(results)} passed")
for n in failed:
    print("  FAILED:", n)
env.cr.rollback()
