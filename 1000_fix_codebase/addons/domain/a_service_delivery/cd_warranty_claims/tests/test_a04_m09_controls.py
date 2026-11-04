"""A04 C2-C13 (2026-11-04): the M09 controls, exercised as NON-ADMIN users.

Each test is one control from working/A04_Workflow_and_Approval_Report.md §6
(M09-1..-14), driven through the ORM as the role that would attempt it.
Replaces the October grep-only suites (test_warranty_claims.py,
test_brand_api.py) and the mock re-implementations
(test_aut018_timing_proof.py, test_warranty_approval_rate.py), which asserted
source strings or a local copy of the rules instead of the model."""

import base64
import json
from datetime import timedelta

from odoo import Command, fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, assigned
from odoo.exceptions import AccessError, UserError, ValidationError

from .conftest import KEYS

REFUSED = (UserError, AccessError, ValidationError)
CLAIM = "fix.warranty.claim"
OFFICER_XMLID = "cd_warranty_claims.group_warranty_claims_officer"


def _as(rec, user):
    return rec.with_user(user)


def _submitted(wc, amount=12500.0, by=None, **vals):
    """A claim raised by the intake, packed, and submitted by a clerk."""
    claim = wc.full_pack(wc.claim(amount=amount, **vals))
    _as(claim, by or wc.clerk).action_submit()
    return claim


def _event(env, claim, event_type):
    row = env["fix.event.outbox"].search(
        [("aggregate_id", "=", claim.id), ("event_type", "=", event_type)],
        order="id desc",
        limit=1,
    )
    return json.loads(row.payload) if row else None


# ---------------------------------------------------------------- roles (C2/§7.1)


def test_plain_users_read_claims_and_the_roles_do_the_work(wc):
    claim = wc.claim()
    assert _as(claim, wc.plain).claim_no == claim.claim_no  # read is kept
    with wc.refused(AccessError):
        _as(claim, wc.plain).write({"warranty_product_id": False, "brand_id": wc.other_brand.id})
    with wc.refused(AccessError):
        _as(wc.env[CLAIM], wc.plain).create(
            {
                "operating_unit_id": wc.ou.id,
                "service_order_id": wc.closed_order().id,
                "brand_id": wc.brand.id,
            }
        )
    wc.full_pack(claim)
    with wc.refused(AccessError, "Warranty Claims Clerk"):
        _as(claim, wc.plain).action_submit()
    # the groups ship with a privilege and the admin as a member
    for xmlid in (
        "cd_warranty_claims.group_warranty_claims_clerk",
        "cd_warranty_claims.group_warranty_claims_officer",
    ):
        group = wc.env.ref(xmlid)
        assert group.privilege_id and wc.env.ref("base.user_admin") in group.user_ids


# ---------------------------------------------------------------- origin and amount (M09-5, C6)


def test_a_clerk_claims_only_a_closed_warranty_job_for_its_approved_estimate(wc):
    Claim = _as(wc.env[CLAIM], wc.clerk)
    base = {"operating_unit_id": wc.ou.id, "brand_id": wc.brand.id}
    with wc.refused(ValidationError, "closed warranty job"):
        Claim.create({**base, "service_order_id": wc.order.id})  # a draft job
    paid = wc.closed_order(category="standard")
    with wc.refused(ValidationError, "double recovery"):
        Claim.create({**base, "service_order_id": paid.id})
    no_estimate = wc.closed_order(total=0.0)
    with wc.refused(ValidationError, "no approved estimate"):
        Claim.create({**base, "service_order_id": no_estimate.id})
    job = wc.closed_order(2000.0)
    with wc.refused(ValidationError, "not a typed figure"):
        Claim.create({**base, "service_order_id": job.id, "claim_amount": 99000.0})
    claim = Claim.create({**base, "service_order_id": job.id})
    assert claim.claim_amount == 2300.0  # the approved estimate, VAT inclusive
    # the amount is fixed when the claim is raised
    with wc.refused(UserError, "approved estimate"):
        _as(claim, wc.clerk).write({"claim_amount": 500000.0})
    assert _as(claim, wc.clerk).action_refresh_amount() is True
    assert claim.claim_amount == 2300.0


def test_a_user_cannot_drive_the_aut018_intake(wc):
    """consume_order_completed is RPC-reachable; it is a system service."""
    job = wc.closed_order()
    with wc.refused(AccessError, "system service"):
        _as(wc.env[CLAIM], wc.clerk).consume_order_completed({"aggregate_id": job.id})
    assert not wc.env[CLAIM].search([("service_order_id", "=", job.id)])


# ---------------------------------------------------------------- guard and freeze (M09-1, C2)


def test_state_decision_and_money_fields_are_not_writable(wc):
    claim = wc.full_pack(wc.claim())
    for vals in (
        {"state": "approved"},
        {"approved_amount": 1.0},
        {"remittance_amount": 12500.0},
        {"decided_by_id": wc.officer.id},
        {"rejection_reason": "x"},
    ):
        with wc.refused(UserError, "cannot be set directly"):
            _as(claim, wc.clerk).write(vals)
    _as(claim, wc.clerk).action_submit()
    # submitted: the brand, product and pack are what the brand received
    with wc.refused(UserError, "submitted to the brand"):
        _as(claim, wc.clerk).write({"brand_id": wc.other_brand.id})
    with wc.refused(UserError, "locked"):
        _as(claim.evidence_ids[:1], wc.clerk).unlink()
    with wc.refused(UserError, "locked"):
        _as(wc.env["fix.warranty.evidence"], wc.clerk).create(
            {"claim_id": claim.id, "requirement_key": "diagnostic"}
        )


def test_the_p03_form_locks_what_the_server_refuses(wc):
    claim = wc.claim()
    locked = claim._fix_form_locked_fields()
    assert {"state", "claim_amount", "approved_amount", "remittance_amount"} <= locked
    claim.write({"state": "approved"})
    assert {"brand_id", "warranty_product_id", "currency_id"} <= claim._fix_form_locked_fields()


# ---------------------------------------------------------------- evidence (M09-6)


def test_one_document_for_every_item_is_refused(wc):
    claim = wc.claim()
    one = wc.document("anything")
    claim.evidence_ids = [
        Command.create({"requirement_key": key, "document_id": one.id}) for key in KEYS
    ]
    assert claim.evidence_complete  # every key has a hashed document...
    with wc.refused(UserError, "same document"):
        _as(claim, wc.clerk).action_submit()  # ...but it is one document


def test_the_same_file_uploaded_twice_is_refused(wc):
    claim = wc.claim()
    rows = []
    for key in KEYS:
        payload = b"same-photo" if key in ("photo_before", "photo_after") else key.encode()
        rows.append(
            Command.create(
                {
                    "requirement_key": key,
                    "document_id": wc.document(key).id,
                    "file_data": base64.b64encode(payload),
                    "file_name": key + ".jpg",
                }
            )
        )
    claim.evidence_ids = rows
    with wc.refused(UserError, r"same file \(SHA-256\)"):
        _as(claim, wc.clerk).action_submit()


# ---------------------------------------------------------------- product rules (M09-7)


def test_waiting_period_and_aggregate_limit_are_enforced(wc):
    Product = wc.env["fix.warranty.product"]
    waiting = Product.create({"name": "Fresh plan", "waiting_days": 365})
    claim = wc.full_pack(wc.claim(warranty_product_id=waiting.id))
    with wc.refused(UserError, "waiting period"):
        _as(claim, wc.clerk).action_submit()

    capped = Product.create({"name": "Capped plan", "claim_limit": 15000.0})
    first = _submitted(wc, amount=10000.0, warranty_product_id=capped.id)
    first.action_decide(approved=True)  # brand path: 10,000 settled under the cap
    second = wc.full_pack(wc.claim(amount=6000.0, warranty_product_id=capped.id))
    with wc.refused(UserError, "aggregate claim limit"):
        _as(second, wc.clerk).action_submit()
    third = _submitted(wc, amount=5000.0, warranty_product_id=capped.id)
    assert third.state == "submitted"  # 10,000 + 5,000 fits


# ---------------------------------------------------------------- the decision (M09-2/-3, C4/C9)


def test_the_decision_is_keyed_by_a_clerk_and_recorded_by_an_officer(wc):
    env = wc.env
    claim = _submitted(wc)
    # nobody decides directly: the brand path is the superuser's only
    for user in (wc.clerk, wc.officer):
        with wc.refused(UserError, "Propose Decision"):
            _as(claim, user).action_decide(approved=True)
        with wc.refused(UserError, "approver's inbox"):
            _as(claim, user).action_apply_decision()
    with wc.refused(AccessError):
        _as(claim, wc.plain).action_propose_approve()
    _as(claim, wc.clerk2).action_propose_approve(oem_reference="OEM-77")
    assert (claim.approval_state, claim.proposed_decision) == ("pending", "approve")
    routed = assigned(claim)
    assert wc.officer in routed and not routed & (wc.clerk | wc.clerk2)
    # the keyed decision is pinned: re-keying while pending is refused
    with wc.refused(UserError, "awaiting the officer"):
        _as(claim, wc.clerk2).action_propose_reject(reason="x")
    approve_via_inbox(claim, wc.officer)
    assert (claim.state, claim.approved_amount, claim.decided_by_id) == (
        "approved",
        12500.0,
        wc.officer,
    )
    assert claim.approval_state == "approved" and claim.decision_source == "officer"
    (row,) = claim.decision_ids
    assert (row.decision, row.requested_amount, row.approved_amount, row.oem_reference) == (
        "approve",
        12500.0,
        12500.0,
        "OEM-77",
    )
    assert (row.proposed_by_id, row.decided_by_id) == (wc.clerk2, wc.officer)
    payload = _event(env, claim, "warranty_claim.decided")
    assert (payload["decision"], payload["approved_amount"], payload["source"]) == (
        "approve",
        12500.0,
        "officer",
    )
    # an approved claim is frozen: the amount stays what was approved
    with wc.refused(UserError, "frozen|approved estimate"):
        _as(claim, wc.clerk).write({"claim_amount": 990000.0})
    with wc.refused(UserError):
        row.with_user(wc.officer).write({"approved_amount": 1.0})


def test_whoever_submitted_or_keyed_a_claim_never_records_its_decision(wc):
    # an officer can do clerk work, but then not decide the same claim
    officer3 = wc.user("wcl_officer_three", OFFICER_XMLID)
    claim = _submitted(wc, by=wc.officer)
    _as(claim, wc.officer2).action_propose_reject(reason="Liquid ingress")
    routed = assigned(claim)
    assert officer3 in routed and not routed & (wc.officer | wc.officer2)
    approve_via_inbox(claim, officer3)
    assert (claim.state, claim.rejection_reason, claim.decided_by_id) == (
        "rejected",
        "Liquid ingress",
        officer3,
    )


def test_a_partial_decision_and_its_remittance(wc):
    env = wc.env
    claim = _submitted(wc)
    with wc.refused(UserError, "less than the requested"):
        _as(claim, wc.clerk).action_propose_partial(approved_amount=12500.0)
    _as(claim, wc.clerk).action_propose_partial(approved_amount=5000.0, reason="Labour capped")
    approve_via_inbox(claim, wc.officer)
    assert (claim.state, claim.claim_amount, claim.approved_amount) == (
        "partially_approved",
        12500.0,
        5000.0,
    )
    # the remittance is recorded by an officer against the bank, never by a clerk
    with wc.refused(AccessError, "Claim Decision Officer"):
        _as(claim, wc.clerk).action_record_remittance(5000.0, "BANK-9")
    _as(claim, wc.officer).action_record_remittance(5000.0, "BANK-9")
    assert (claim.state, claim.remittance_mismatch, claim.remitted_by_id) == (
        "remitted",
        False,
        wc.officer,
    )
    assert _event(env, claim, "warranty_claim.remitted")["settled"] is True
    _as(claim, wc.officer).action_close()
    assert claim.state == "closed"


def test_an_officer_can_send_a_keyed_decision_back(wc):
    claim = _submitted(wc)
    _as(claim, wc.clerk).action_propose_approve()
    task = claim.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == wc.officer)
    task.with_user(wc.officer).action_reject(comment="OEM letter says partial")
    assert claim.state == "submitted" and not claim.proposed_decision
    assert claim.approval_state == "rejected"
    _as(claim, wc.clerk).action_propose_partial(approved_amount=4000.0, reason="per letter")
    assert claim.approval_state == "pending"


def test_no_caller_switch_for_the_serial_check(wc):
    device = wc.device
    device.sudo()._guarded().write({"serial_number": False})
    claim = _submitted(wc)
    with wc.refused(UserError, "provenance"):
        claim.with_context(skip_serial_validation=True).action_decide(approved=True)
    _as(claim, wc.clerk).action_propose_approve()
    with wc.refused(UserError, "provenance"):
        approve_via_inbox(claim, wc.officer)


# ---------------------------------------------------------------- appeal (M09-8)


def test_an_appeal_is_decided_by_an_independent_officer_and_reopens_the_claim(wc):
    claim = _submitted(wc)
    _as(claim, wc.clerk).action_propose_reject(reason="Out of warranty")
    approve_via_inbox(claim, wc.officer)
    Appeal = _as(wc.env["fix.claim.appeal"], wc.clerk)
    with wc.refused(UserError, "cannot be set directly"):
        Appeal.create({"name": "A0", "claim_id": claim.id, "reason": "x", "decision": "upheld"})
    appeal = Appeal.create({"name": "A1", "claim_id": claim.id, "reason": "Proof attached"})
    with wc.refused(ValidationError, "open appeal"):
        Appeal.create({"name": "A2", "claim_id": claim.id, "reason": "again"})
    with wc.refused(UserError, "cannot be set directly"):
        appeal.write({"decision": "upheld"})
    with wc.refused(AccessError, "Claim Decision Officer"):
        _as(appeal, wc.clerk2).action_uphold(note="looks fine")
    with wc.refused(UserError, "Segregation of duties"):
        _as(appeal, wc.officer).action_uphold(note="I decided it")
    _as(appeal, wc.officer2).action_uphold(note="Purchase proof is valid")
    assert (appeal.decision, appeal.decided_by_id) == ("upheld", wc.officer2)
    assert bool(appeal.decided_at)
    assert (claim.state, claim.approval_state, claim.approved_amount) == ("submitted", "none", 0.0)
    assert len(claim.decision_ids) == 1  # the first decision stays on record
    with wc.refused(UserError, "final"):
        _as(appeal, wc.clerk).write({"reason": "edited"})
    # the re-submitted claim is decided again, through the inbox
    _as(claim, wc.clerk).action_propose_approve()
    approve_via_inbox(claim, wc.officer2)
    assert claim.state == "approved" and len(claim.decision_ids) == 2


def test_an_unrejected_claim_cannot_be_appealed(wc):
    claim = wc.claim()
    with wc.refused(ValidationError, "rejected or partly approved"):
        _as(wc.env["fix.claim.appeal"], wc.clerk).create(
            {"name": "A", "claim_id": claim.id, "reason": "x"}
        )


# ---------------------------------------------------------------- transfer (M09-9)


def test_a_warranty_transfer_is_approved_by_someone_else_and_moves_the_device(wc):
    env = wc.env
    stranger = env["res.partner"].create({"name": "Second Owner"})
    Transfer = _as(env["fix.warranty.transfer"], wc.officer)
    base = {"name": "TR-1", "warranty_id": wc.warranty.id, "effective_date": wc.today}
    with wc.refused(ValidationError, "current owner"):
        Transfer.create({**base, "from_partner_id": stranger.id, "to_partner_id": stranger.id})
    with wc.refused(UserError, "cannot be set directly"):
        Transfer.create(
            {
                **base,
                "from_partner_id": wc.customer.id,
                "to_partner_id": stranger.id,
                "state": "effective",
            }
        )
    tr = Transfer.create({**base, "from_partner_id": wc.customer.id, "to_partner_id": stranger.id})
    with wc.refused(UserError, "Segregation of duties"):
        tr.action_approve()
    _as(tr, wc.officer2).action_approve()
    assert (tr.state, tr.approved_by_id) == ("approved", wc.officer2)
    with wc.refused(UserError, "draft"):
        tr.write({"to_partner_id": wc.customer.id})
    with wc.refused(UserError, "evidence"):
        _as(tr, wc.officer2).action_effect()
    _as(tr, wc.officer).action_void()
    evidence = env["fix.document"].attach(
        name="sale-receipt.pdf",
        datas=base64.b64encode(b"receipt"),
        document_type="other",
        res_model="fix.device",
        res_id=wc.device.id,
    )
    tr2 = Transfer.create(
        {
            **base,
            "name": "TR-2",
            "from_partner_id": wc.customer.id,
            "to_partner_id": stranger.id,
            "evidence_document_id": evidence.id,
        }
    )
    _as(tr2, wc.officer2).action_approve()
    _as(tr2, wc.officer2).action_effect()
    assert tr2.state == "effective" and wc.device.owner_id == stranger
    assert tr.state == "void"


# ---------------------------------------------------------------- recall (M09-10)


def test_a_recall_has_a_lifecycle_and_bounded_coverage(wc):
    Recall = _as(wc.env["fix.warranty.recall"], wc.clerk)
    with wc.refused(ValidationError, "cannot exceed"):
        Recall.create({"name": "RC", "affected_units": 100, "covered_units": 500})
    with wc.refused(UserError, "cannot be set directly"):
        Recall.create({"name": "RC", "affected_units": 100, "state": "completed"})
    rc = Recall.create({"name": "RC", "brand_id": wc.brand.id, "affected_units": 100})
    rc.action_launch()
    assert rc.state == "active" and rc.launched_on == fields.Date.context_today(rc)
    rc.write({"covered_units": 60})
    with wc.refused(AccessError, "Claim Decision Officer"):
        rc.action_complete()
    _as(rc, wc.officer).action_complete()
    assert rc.state == "completed"
    with wc.refused(UserError, "closed for edits"):
        rc.write({"covered_units": 70})


# ---------------------------------------------------------------- cron (C10) and workspace


def test_the_overdue_cron_exists_and_escalates_each_claim_once(wc):
    cron = wc.env.ref("cd_warranty_claims.ir_cron_warranty_claim_overdue")
    assert cron.active and "cron_claim_overdue_escalation" in cron.code
    assert cron.model_id.model == CLAIM
    late = wc.claim()
    late.submission_deadline = fields.Datetime.now() - timedelta(hours=1)
    Claim = wc.env[CLAIM]
    assert Claim.cron_claim_overdue_escalation() >= 1
    assert late.overdue_escalated_at
    assert late.activity_ids or late.message_ids.filtered(lambda m: "overdue" in (m.body or ""))
    stamped = late.overdue_escalated_at
    Claim.cron_claim_overdue_escalation()
    assert late.overdue_escalated_at == stamped  # idempotent


def test_the_workspace_runs_the_claim_lifecycle(wc):
    import types

    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    claim = wc.full_pack(wc.claim())
    ctl = g.P03GenericApiController()
    action = g.P03GenericApiController.model_action.original_endpoint
    write = g.P03GenericApiController.model_write.original_endpoint
    saved = getattr(g, "request", None)
    g.request = types.SimpleNamespace(env=wc.env(user=wc.clerk.id))
    try:
        res = write(ctl, model=CLAIM, record_id=claim.id, values={"state": "approved"})
        assert res.get("error") and claim.state == "draft"
        res = action(ctl, model=CLAIM, ids=[claim.id], method="action_submit")
        assert res["success"], res
        res = action(ctl, model=CLAIM, ids=[claim.id], method="action_decide")
        assert not res["success"]  # not a workspace action
        res = action(
            ctl,
            model=CLAIM,
            ids=[claim.id],
            method="action_propose_reject",
            kwargs={"reason": "Bench test passed"},
        )
        assert res["success"], res
    finally:
        g.request = saved
    assert claim.state == "submitted" and claim.approval_state == "pending"
