"""A04 C2-C13 (2026-11-04): the M12 controls, exercised as NON-ADMIN users.

Each test is one control from working/A04_Workflow_and_Approval_Report.md §6
(M12-1..-14), driven through the ORM as the role that would attempt it.
Replaces the October source-inspection suites (test_marketplace.py,
test_seller_api.py), which asserted that strings existed in the source."""

import json
import types
from contextlib import contextmanager
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

from .b4_helpers import customer_receipt, seller_scheme

REFUSED = (UserError, AccessError, ValidationError)
SELLER, ORDER, QUOTE = "fix.marketplace.seller", "fix.marketplace.order", "fix.seller.quote"
DISPUTE, LISTING = "fix.marketplace.dispute", "fix.marketplace.listing"
CHARGEBACK, SCORE = "fix.marketplace.chargeback", "fix.seller.score"
OPERATOR = "cd_marketplace.group_marketplace_operator"
COMPLIANCE = "cd_marketplace.group_marketplace_compliance"
ARBITRATOR = "cd_marketplace.group_marketplace_arbitrator"
CFO = "cd_entity_config.group_dofa_tier_4"


def _job_evidence(order):
    """BRU-MKP-02 (M12 capture audit, 19 Nov 2026): a marketplace job
    completes only with the owned-job evidence. Recorded as the trusted
    superuser, as a seller's app or an operator would."""
    import base64

    png = base64.b64encode(b"\x89PNG evidence")
    Evidence = order.env["fix.marketplace.job.evidence"].sudo()
    for kind, vals in (
        ("before_photo", {"evidence_file": png, "evidence_filename": "before.png"}),
        ("after_photo", {"evidence_file": png, "evidence_filename": "after.png"}),
        ("qc_checklist", {"qc_passed": True, "note": "All QC checks passed"}),
        ("parts_declaration", {"provenance": "none"}),
    ):
        Evidence.create({"order_id": order.id, "artefact_type": kind, **vals})


@contextmanager
def _refused(env, exc=REFUSED, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def mk(odoo_env):
    env = odoo_env
    params = env["ir.config_parameter"].sudo()
    params.set_param("cd_marketplace.platform_commission_rate", False)
    params.set_param("cd_marketplace.platform_commission_rate", "0.10")
    users = env["res.users"].with_context(no_reset_password=True)

    def user(login, *groups):
        return users.create(
            {
                "name": login.replace("_", " ").title(),
                "login": login,
                "group_ids": [Command.set([env.ref(g).id for g in groups])],
            }
        )

    ns = types.SimpleNamespace(env=env)
    ns.plain = user("mk_plain", "base.group_user")
    ns.operator = user("mk_operator", "base.group_user", OPERATOR)
    ns.operator2 = user("mk_operator_two", "base.group_user", OPERATOR)
    ns.compliance = user("mk_compliance", "base.group_user", COMPLIANCE)
    ns.compliance2 = user("mk_compliance_two", "base.group_user", COMPLIANCE)
    ns.arbitrator = user("mk_arbitrator", "base.group_user", ARBITRATOR)
    ns.cfo = user("mk_cfo", "base.group_user", CFO)
    ns.seller_user = user("mk_seller", "cd_marketplace.group_fix_marketplace_seller")
    ns.customer = env["res.partner"].create({"name": "MK Customer"})

    def seller(name="MK Shop", ready=True, partner=None, **vals):
        rec = env[SELLER].create(
            {
                "name": name,
                "partner_id": (partner or env["res.partner"].create({"name": name})).id,
                **vals,
            }
        )
        if ready:  # seed-style, as the trusted superuser
            rec.write({"kyc_status": "verified", "cfo_approved": True})
        return rec

    def order(user=None, **vals):
        vals.setdefault("customer_id", ns.customer.id)
        vals.setdefault("description", "Cracked screen")
        vals.setdefault("customer_consent", True)  # BRU-MKP-07
        vals.setdefault("consent_method", "signed")
        return env[ORDER].with_user(user or ns.operator).create(vals)

    def awarded(seller_rec=None, price=8000.0, **vals):
        o = order(**vals)
        q = env[QUOTE].create(
            {
                "marketplace_order_id": o.id,
                "seller_id": (seller_rec or seller()).id,
                "quoted_price": price,
            }
        )
        q.with_user(ns.operator).action_select()
        return o, q

    def reviewed(seller_rec=None, price=8000.0):
        o, q = awarded(seller_rec, price)
        as_op = o.with_user(ns.operator)
        as_op.action_start_job()
        _job_evidence(o)
        as_op.action_complete()
        as_op.action_review(rating=5)
        customer_receipt(env, o)  # A04 ERP M12-F1: the customer paid (M20)
        return o

    seller_scheme(env)  # A04 ERP M12-F4: Finance configured the scheme

    ns.user, ns.seller, ns.order, ns.awarded, ns.reviewed = user, seller, order, awarded, reviewed
    ns.refused = lambda exc=REFUSED, match=None: _refused(env, exc, match)
    return ns


def _event(env, event_type, res_id):
    row = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)], order="id desc", limit=1
    )
    return json.loads(row.payload) if row else None


# ---------------------------------------------------------------- roles (§7.1)


def test_plain_users_read_the_marketplace_and_the_roles_do_the_work(mk):
    s = mk.seller()
    assert s.with_user(mk.plain).name == "MK Shop"
    with mk.refused(AccessError):
        mk.order(user=mk.plain)
    with mk.refused(AccessError):
        s.with_user(mk.plain).write({"name": "Renamed"})
    for xmlid in (OPERATOR, COMPLIANCE, ARBITRATOR):
        group = mk.env.ref(xmlid)
        assert group.privilege_id and mk.env.ref("base.user_admin") in group.user_ids


# ---------------------------------------------------------------- KYC and CFO (M12-1/-2)


def test_kyc_is_a_compliance_decision_and_cfo_approval_a_routed_one(mk):
    env = mk.env
    s = mk.seller(ready=False, partner=mk.seller_user.partner_id, seller_type="individual")
    mk.env["ir.attachment"].create(
        {"name": "kyc.pdf", "datas": "UERG", "res_model": SELLER, "res_id": s.id}
    )  # A04 ERP M12-F8
    s.with_user(mk.operator).action_submit_kyc(nid_number="1990123456789")
    assert s.kyc_status == "in_review"
    with mk.refused(AccessError, "Compliance Reviewer"):
        s.with_user(mk.operator).action_verify_kyc()
    s.with_user(mk.compliance).action_verify_kyc()
    # verifying KYC no longer grants CFO approval to the same person
    assert (s.kyc_status, s.compliance_reviewer_id, s.cfo_approved) == (
        "verified",
        mk.compliance,
        False,
    )
    # nobody approves directly; the request goes to DOFA Tier 4 holders
    for u in (mk.operator, mk.cfo, mk.compliance):
        with mk.refused(UserError, "approver's inbox"):
            s.with_user(u).action_cfo_approve()
    # the KYC reviewer may hold Tier 4 too: he is still not asked
    mk.compliance.write({"group_ids": [Command.link(env.ref(CFO).id)]})
    s.with_user(mk.operator).action_request_approval(justification="Strong references")
    routed = assigned(s)
    assert mk.cfo in routed and mk.compliance not in routed and mk.operator not in routed
    approve_via_inbox(s, mk.cfo)
    assert (s.cfo_approved, s.cfo_approved_by) == (True, mk.cfo)
    assert _event(env, "seller.cfo_approved", s.id) == {
        "seller": s.name,
        "approver": mk.cfo.name,
    }
    # identity is frozen once verified
    with mk.refused(UserError, "KYC-verified"):
        s.with_user(mk.operator).write({"nid_number": "000"})


def test_cfo_approval_needs_kyc_first(mk):
    s = mk.seller(ready=False)
    with mk.refused(UserError, "Nothing to approve"):
        s.with_user(mk.operator).action_request_approval()
    with mk.refused(UserError, "not KYC-verified"):
        s.action_cfo_approve()  # not even the superuser skips KYC


def test_approval_fields_are_guarded(mk):
    s = mk.seller(ready=False)
    for vals in (
        {"kyc_status": "verified"},
        {"cfo_approved": True},
        {"tier": "platinum"},
        {"payout_hold": False, "rating": 5.0},
    ):
        with mk.refused(UserError, "cannot be set directly"):
            s.with_user(mk.operator).write(vals)
    with mk.refused(AccessError):
        s.with_user(mk.seller_user).write({"name": "x"})


def test_rejecting_kyc_withdraws_cfo_approval(mk):
    s = mk.seller()
    with mk.refused(UserError, "reason"):
        s.with_user(mk.compliance).action_reject_kyc(reason="")
    s.with_user(mk.compliance).action_reject_kyc(reason="Licence forged")
    assert (s.kyc_status, s.cfo_approved) == ("rejected", False)


# ---------------------------------------------------------------- listings (M12-10)


def test_a_listing_goes_live_only_on_an_independent_compliance_approval(mk):
    env = mk.env
    Listing = env[LISTING].with_user(mk.operator)
    with mk.refused(UserError, "cannot be set directly"):
        Listing.create({"name": "Screens", "seller_id": mk.seller().id, "state": "active"})
    rejected = mk.seller(name="Rejected Shop")
    rejected.write({"kyc_status": "rejected"})
    bad = Listing.create({"name": "Cheap screens", "seller_id": rejected.id, "list_price": 100})
    with mk.refused(UserError, "not KYC-verified"):
        bad.action_submit()
    ln = Listing.create({"name": "Screen repair", "seller_id": mk.seller().id, "list_price": 900})
    assert ln.company_id == env.company
    ln.action_submit()
    assert (ln.state, ln.approval_state) == ("submitted", "pending")
    assert mk.operator not in assigned(ln) and mk.compliance in assigned(ln)
    with mk.refused(UserError, "approver's inbox"):
        ln.with_user(mk.compliance).action_approve()
    approve_via_inbox(ln, mk.compliance)
    assert (ln.state, ln.approved_by_id) == ("active", mk.compliance)
    with mk.refused(UserError, "withdraw it to draft"):
        ln.write({"list_price": 1.0})
    ln.action_withdraw()
    ln.write({"list_price": 950})
    assert ln.state == "draft"


# ---------------------------------------------------------------- order money (M12-5/-7/-8)


def test_price_and_tier_rate_are_pinned_at_award(mk):
    env = mk.env
    env["ir.config_parameter"].sudo().set_param("cd_marketplace.commission_rate.gold", "0.12")
    gold = mk.seller(name="Gold Shop")
    gold.sudo()._guarded().write({"tier": "gold"})
    o, q = mk.awarded(gold, price=8000.0)
    assert (o.awarded_price, o.commission_rate, q.state) == (8000.0, 0.12, "selected")
    for vals in ({"commission_rate": 0.0001}, {"state": "completed"}, {"awarded_price": 1.0}):
        with mk.refused(UserError, "cannot be set directly"):
            o.with_user(mk.operator).write(vals)
    with mk.refused(UserError, "not edited once submitted"):
        q.with_user(mk.operator).write({"quoted_price": 48000.0})
    with mk.refused(UserError, "the order is"):
        o.with_user(mk.operator).write({"budget": 1.0})
    as_op = o.with_user(mk.operator)
    as_op.action_start_job()
    _job_evidence(o)
    as_op.action_complete()
    as_op.action_review(rating=4)
    customer_receipt(env, o)  # A04 ERP M12-F1: the customer paid (M20)
    as_op.action_earn_commission()
    assert o.commission_amount == pytest.approx(960.0)
    payload = _event(env, "commission.earned", o.id)
    assert (payload["order_id"], payload["rate"], payload["seller_tier"], payload["gross"]) == (
        o.id,
        0.12,
        "gold",
        8000.0,
    )


def test_a_seller_without_the_category_is_not_awarded(mk):
    cat = mk.env["product.category"].create({"name": "MK Microsoldering"})
    o = mk.order(category_id=cat.id)
    q = mk.env[QUOTE].create(
        {"marketplace_order_id": o.id, "seller_id": mk.seller().id, "quoted_price": 900}
    )
    with mk.refused(UserError, "BRU-ECM-07"):
        q.with_user(mk.operator).action_select()


def test_the_payout_waits_for_escrow_disputes_and_the_seller_hold(mk):
    env = mk.env
    s = mk.seller()
    o = mk.reviewed(s)
    as_op = o.with_user(mk.operator)
    as_op.action_earn_commission()
    with mk.refused(AccessError):
        o.with_user(mk.plain).action_paid()
    with mk.refused(UserError, "Escrow Hold"):
        as_op.with_context(skip_escrow_check=True).action_paid()  # no caller switch
    # a dispute on ANOTHER order of the seller holds every payout (BRU-BIL-03)
    other, _q = mk.awarded(s)
    env[DISPUTE].with_user(mk.operator).create(
        {
            "order_id": other.id,
            "seller_id": s.id,
            "customer_id": mk.customer.id,
            "description": "never repaired",
        }
    )
    assert s.payout_hold
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_marketplace_order SET delivery_confirmed_at = %s WHERE id = %s",
        [fields.Datetime.now() - timedelta(days=8), o.id],
    )
    o.invalidate_recordset()
    o._compute_payout_escrow()
    with mk.refused(UserError, "payout hold"):
        as_op.action_paid()
    s.sudo()._guarded().write({"payout_hold": False})
    # A04 ERP audit M12-F2: every guard met, and still not by hand - the
    # order is paid out by the M53 payout run's bank-confirmed discharge
    with mk.refused(UserError, "payout run"):
        as_op.action_paid()
    assert o.state == "commissioned"


# ---------------------------------------------------------------- disputes (M12-3/-4)


def test_a_dispute_is_ruled_once_by_an_independent_arbitrator(mk):
    env = mk.env
    s = mk.seller(partner=mk.seller_user.partner_id)
    o, _q = mk.awarded(s)
    Dispute = env[DISPUTE].with_user(mk.operator)
    with mk.refused(ValidationError, "awarded"):
        Dispute.create(
            {
                "order_id": o.id,
                "seller_id": mk.seller(name="Other").id,
                "customer_id": mk.customer.id,
                "description": "x",
            }
        )
    d = Dispute.create(
        {
            "order_id": o.id,
            "seller_id": s.id,
            "customer_id": mk.customer.id,
            "description": "screen flickers",
            "disputed_amount": 3000.0,
        }
    )
    assert s.payout_hold and d.sla_deadline
    with mk.refused(UserError, "cannot be set directly"):
        d.write({"state": "resolved", "resolution_type": "payout_seller"})
    with mk.refused():
        d.with_user(mk.seller_user).action_resolve(resolution_type="payout_seller")
    d.action_investigate()
    with mk.refused(UserError, "Propose the ruling"):
        d.action_arbitrate()
    d.write(
        {
            "proposed_resolution": "split_settlement",
            "proposed_refund_amount": 9000.0,
            "resolution_notes": "Partial fault",
        }
    )
    with mk.refused(UserError, "between 0 and the disputed amount"):
        d.action_arbitrate()
    d.write({"proposed_refund_amount": 1500.0})
    d.action_arbitrate()
    assert (d.state, d.approval_state) == ("arbitration", "pending")
    assert mk.arbitrator in assigned(d) and mk.operator not in assigned(d)
    with mk.refused(UserError, "the ruling is with the arbitrator"):
        d.write({"proposed_refund_amount": 1.0})
    with mk.refused(UserError, "approver's inbox"):
        d.with_user(mk.arbitrator).action_resolve()
    approve_via_inbox(d, mk.arbitrator)
    assert (d.state, d.resolution_type, d.refund_amount, d.resolved_by) == (
        "resolved",
        "split_settlement",
        1500.0,
        mk.arbitrator,
    )
    assert not s.payout_hold
    payload = _event(env, "marketplace.dispute_resolved", d.id)
    assert (payload["refund_amount"], payload["seller_id"], payload["order_id"]) == (
        1500.0,
        s.id,
        o.id,
    )
    with mk.refused(UserError, "final"):
        d.sudo().action_resolve(resolution_type="payout_seller")  # not even the superuser
    with mk.refused(UserError, "resolved dispute is final"):
        d.with_user(mk.operator).write({"description": "edited"})


def test_an_arbitrator_can_send_a_ruling_back(mk):
    s = mk.seller()
    o, _q = mk.awarded(s)
    d = (
        mk.env[DISPUTE]
        .with_user(mk.operator)
        .create(
            {
                "order_id": o.id,
                "seller_id": s.id,
                "customer_id": mk.customer.id,
                "description": "late",
                "disputed_amount": 1000.0,
            }
        )
    )
    d.action_investigate()
    d.write({"proposed_resolution": "refund_customer", "resolution_notes": "No show"})
    d.action_arbitrate()
    assert d.proposed_refund_amount == 1000.0
    inbox_task(d, mk.arbitrator).with_user(mk.arbitrator).action_reject(comment="Get the logs")
    assert (d.state, d.approval_state) == ("investigating", "rejected")
    assert s.payout_hold


def test_the_dispute_sla_cron_escalates_each_dispute_once(mk):
    env = mk.env
    cron = env.ref("cd_marketplace.ir_cron_marketplace_dispute_sla")
    assert cron.active and "cron_dispute_sla_escalation" in cron.code
    assert cron.model_id.model == DISPUTE
    s = mk.seller()
    o, _q = mk.awarded(s)
    d = (
        env[DISPUTE]
        .with_user(mk.operator)
        .create(
            {
                "order_id": o.id,
                "seller_id": s.id,
                "customer_id": mk.customer.id,
                "description": "slow",
            }
        )
    )
    d.sudo()._guarded().write({"sla_deadline": fields.Datetime.now() - timedelta(hours=1)})
    assert env[DISPUTE].cron_dispute_sla_escalation() >= 1
    assert (d.state, s.tier, bool(d.escalated_at)) == ("escalated", "at_risk", True)
    stamped = d.escalated_at
    env[DISPUTE].cron_dispute_sla_escalation()
    assert d.escalated_at == stamped


# ---------------------------------------------------------------- chargebacks (P2)


def test_a_chargeback_holds_the_payout_and_a_lost_one_is_recovered(mk):
    env = mk.env
    s = mk.seller()
    o, _q = mk.awarded(s, price=5000.0)
    Chargeback = env[CHARGEBACK].with_user(mk.operator)
    with mk.refused(ValidationError, "exceeds"):
        Chargeback.create({"order_id": o.id, "amount": 9000.0, "gateway_ref": "BK-1"})
    cb = Chargeback.create({"order_id": o.id, "amount": 2000.0, "gateway_ref": "BK-1"})
    assert (cb.seller_id, s.payout_hold, cb.name.startswith("CB/")) == (s, True, True)
    with mk.refused(UserError, "cannot be set directly"):
        cb.write({"state": "won"})
    with mk.refused(UserError):
        cb.action_mark_lost(note="x")  # not contested yet
    cb.action_submit_evidence(note="Job card and customer sign-off")
    cb.action_mark_lost(note="Gateway case closed: customer")
    assert (cb.state, s.payout_hold) == ("lost", False)
    payload = _event(env, "marketplace.chargeback_lost", cb.id)
    assert (payload["amount"], payload["seller_id"], payload["outcome"]) == (2000.0, s.id, "lost")
    with mk.refused(UserError, "keeps the order"):
        cb.write({"amount": 1.0})


# ---------------------------------------------------------------- scores (C5)


def test_seller_kpis_are_measured_never_typed(mk):
    s = mk.seller()
    score = mk.env[SCORE].create({"seller_id": s.id, "period": "2026-11"})
    with mk.refused(UserError, "cannot be set directly"):
        score.with_user(mk.operator).write({"acceptance_rate": 1.0, "metrics_measured": True})
    score.with_user(mk.operator).action_publish()
    assert (score.metrics_measured, s.tier) == (False, "unrated")


# ---------------------------------------------------------------- workspace


def test_the_workspace_runs_the_marketplace_lifecycles(mk):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    s = mk.seller(ready=False, trade_license_no="TL-77", tin_number="123456789012")
    mk.env["ir.attachment"].create(
        {"name": "kyc.pdf", "datas": "UERG", "res_model": SELLER, "res_id": s.id}
    )  # A04 ERP M12-F8
    s.with_user(mk.operator).action_submit_kyc()
    ctl = g.P03GenericApiController()
    action = g.P03GenericApiController.model_action.original_endpoint
    write = g.P03GenericApiController.model_write.original_endpoint
    saved = getattr(g, "request", None)
    g.request = types.SimpleNamespace(env=mk.env(user=mk.compliance.id))
    try:
        res = write(ctl, model=SELLER, record_id=s.id, values={"cfo_approved": True})
        assert res.get("error") and not s.cfo_approved
        res = action(ctl, model=SELLER, ids=[s.id], method="action_verify_kyc")
        assert res["success"], res
        res = action(ctl, model=SELLER, ids=[s.id], method="action_cfo_approve")
        assert not res["success"]  # decided from the inbox, not the screen
    finally:
        g.request = saved
    assert (s.kyc_status, s.cfo_approved) == ("verified", False)
