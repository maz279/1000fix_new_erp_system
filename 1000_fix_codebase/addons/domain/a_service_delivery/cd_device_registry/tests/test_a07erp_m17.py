"""A07 ERP audit (2026-11-20), M17 stream S1: every finding M17-01..M17-31,
owner decisions D12/D13 and LEAD-02, attacked on the live ORM (``odoo_env``,
rolled back) as the NON-ADMIN user who would really try it, each refusal paired
with the proper path working. Event consumers are handed the event the way the
relay hands it (superuser, savepoint), never by a source-text assertion.
"""

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_device_registry.tests.test_a07_p1_controls import (  # noqa: F401
    AGENT,
    BM,
    OFFICER,
    QM,
    _user,
    c,
    dev,
    doc,
    events,
    refused,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import UserError

HOLD = "fix.service.order.device.hold"
POP_APPROVER = "cd_device_registry.group_device_population_approver"
M09_CLERK = "cd_warranty_claims.group_warranty_claims_clerk"
M09_OFFICER = "cd_warranty_claims.group_warranty_claims_officer"
TAG = "A7ERP"


@pytest.fixture
def w(c):  # noqa: F811
    env = c.env
    x = types.SimpleNamespace(env=env)
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": TAG, "legal_name": "A07 ERP entity", "company_id": env.company.id})
    x.branch = env["fix.branch"].create(
        {
            "name": "%s Branch" % TAG,
            "code": TAG,
            "entity_id": entity.id,
            "operating_unit_id": c.ou.id,
        }
    )
    x.approver = _user(env, "a7erp_ops1", c.ou, [POP_APPROVER])
    x.approver2 = _user(env, "a7erp_ops2", c.ou, [POP_APPROVER])

    def order(device, **kw):
        vals = {
            "device_id": device.id,
            "customer_id": device.owner_id.id or c.owner.id,
            "branch_id": x.branch.id,
            "fault_description": "%s fault" % TAG,
            "operating_unit_id": c.ou.id,
        }
        vals.update(kw)
        return env["fix.service.order"].create(vals)

    x.order = order
    return x


def _event(record, event_type, payload=None):
    return {
        "event_id": "%s-%s-%s" % (TAG, event_type, record.id),
        "event_type": event_type,
        "aggregate": record._name,
        "aggregate_id": record.id,
        "payload": payload or {},
    }


def _active_warranty(c, device, wtype="manufacturer", days=200):  # noqa: F811
    today = device._dhaka_today()
    cover = c.env["fix.warranty"].create(
        {
            "device_id": device.id,
            "warranty_type": wtype,
            "start_date": today - timedelta(days=10),
            "end_date": today + timedelta(days=days),
        }
    )
    cover._guarded().write({"status": "active", "verified_at": fields.Datetime.now()})
    return cover


def _confirmed_grade(c, device):  # noqa: F811
    grade = c.env["fix.device.condition"].with_user(c.clerk).create({"device_id": device.id})
    grade.with_user(c.clerk2).action_confirm()
    return grade


def _to_population(c, device, population):  # noqa: F811
    c.env["fix.device.population.change"].sudo()._guarded().create(
        {"device_id": device.id, "to_population": population, "reason_code": "correction"}
    )


# ------------------------------------------------------------------ M17-01
def test_m17_01_an_order_opened_after_the_flag_is_held_at_once(c, w):  # noqa: F811
    d = dev(c)
    d.with_user(c.clerk).action_mark_lost(reason="Owner reported loss at hotline")
    o = w.order(d)
    hold = c.env[HOLD].search([("order_id", "=", o.id)])
    assert hold.state == "open" and hold.flag == "lost"
    assert o.device_flag_hold and o.activity_ids
    with pytest.raises(UserError, match="lost"), c.env.cr.savepoint():
        o._assert_device_not_held()
    # a device moved onto an existing order is held too
    clean = dev(c)
    o2 = w.order(clean)
    assert not o2.device_flag_hold
    o2.write({"device_id": d.id})
    assert c.env[HOLD].search_count([("order_id", "=", o2.id)]) == 1 and o2.device_flag_hold


# ------------------------------------------------------- D12(b) / M17-22
def test_d12_stolen_needs_a_police_reference(c):  # noqa: F811
    d = dev(c)
    assert refused(c.env, lambda: d.with_user(c.clerk).action_mark_lost("taken", "stolen"))
    d.with_user(c.clerk).action_mark_lost("Snatched at Farmgate", "stolen", "GD-1234")
    assert d.state == "lost" and d.lost_flag_type == "stolen" and d.lost_police_ref == "GD-1234"


def test_d12_a_disputed_ownership_blocks_hand_over_until_a_bm_clears_it(c, w):  # noqa: F811
    d = dev(c)
    o = w.order(d)
    d.with_user(c.clerk).action_flag_disputed(reason="Ex-spouse claims the phone")
    assert d.ownership_disputed and o.device_flag_hold
    flagged = events(c, "device.flagged", d.id).sorted("id")[-1:]
    assert flagged
    c.env[HOLD].sudo().consume_device_flagged(flagged._relay_event_dict())
    hold = c.env[HOLD].search([("order_id", "=", o.id), ("flag", "=", "disputed")])
    assert hold.state == "open"
    with pytest.raises(UserError, match="disputed"), c.env.cr.savepoint():
        o._assert_device_not_held()
    evidence = doc(c, "fix.device", d.id)
    assert refused(
        c.env,
        lambda: d.with_user(c.agent).action_transfer_ownership(
            c.buyer.id, "sale", reason="sold", evidence_document_id=evidence.id
        ),
    )
    assert refused(c.env, lambda: d.with_user(c.clerk).action_clear_dispute("settled"))
    bm = _user(c.env, "a7erp_bm_d", c.ou, [BM])
    assert refused(c.env, lambda: d.with_user(c.clerk2).action_clear_dispute("settled"))
    d.with_user(bm).action_clear_dispute(reason="Court order shows the owner")
    cleared = events(c, "device.flag_cleared", d.id).sorted("id")[-1:]
    c.env[HOLD].sudo().consume_device_flag_cleared(cleared._relay_event_dict())
    assert hold.state == "cleared" and not o.device_flag_hold


# ------------------------------------------------------------------ M17-02
def test_m17_02_a_transferred_release_goes_to_the_new_owner_with_evidence(c):  # noqa: F811
    d = dev(c)
    grade = _confirmed_grade(c, d)
    Custody = c.env["fix.device.custody"].with_user(c.clerk)

    def release(party, **kw):
        vals = {
            "device_id": d.id,
            "event": "transferred",
            "to_party_id": party.id,
            "condition_id": grade.id,
            "evidence_document_id": doc(c, doc_type="custody_photo").id,
            "accessories_reconciled": True,
        }
        vals.update(kw)
        return Custody.create(vals)

    assert refused(c.env, lambda: release(c.stranger))
    assert refused(c.env, lambda: release(c.owner, condition_id=False))
    assert refused(c.env, lambda: release(c.owner, evidence_document_id=False))
    evidence = doc(c, "fix.device", d.id)
    d.with_user(c.agent).action_transfer_ownership(
        c.buyer.id, "sale", reason="Sold privately", evidence_document_id=evidence.id
    )
    event = release(c.buyer)
    assert event.to_party_id == c.buyer and d.custody_state == "with_owner"


# ------------------------------------------------------- M17-03 / M17-19
def test_m17_03_a_lost_duplicate_is_never_merged_away(c):  # noqa: F811
    clean, stolen = dev(c), dev(c)
    stolen.with_user(c.clerk).action_mark_lost(reason="Stolen, reported by owner")
    cand = (
        c.env["fix.device.identity"]
        .with_user(c.clerk)
        .create(
            {
                "primary_device_id": clean.id,
                "duplicate_device_id": stolen.id,
                "match_reason": "same",
            }
        )
    )
    assert refused(c.env, lambda: cand.with_user(c.clerk).action_request_approval("same unit"))
    assert stolen.active


def test_m17_19_the_creator_of_a_device_does_not_approve_its_merge(c):  # noqa: F811
    primary = dev(c)
    provisional = dev(c, user=c.qm)
    cand = (
        c.env["fix.device.identity"]
        .with_user(c.clerk)
        .create(
            {
                "primary_device_id": primary.id,
                "duplicate_device_id": provisional.id,
                "match_reason": "same box",
            }
        )
    )
    with pytest.raises(UserError), c.env.cr.savepoint():
        approve_via_inbox(cand, c.qm, requester=c.clerk2, justification="same unit")
    assert cand.state == "candidate"


# ------------------------------------------------------- M17-04 / M17-23
def test_m17_04_trade_in_moves_owner_and_population_and_ends_portal_control(c):  # noqa: F811
    d = dev(c)
    tradein = (
        c.env["fix.tradein.request"].sudo().create({"customer_id": c.owner.id, "device_id": d.id})
    )
    Device = c.env["fix.device"].sudo()
    Device.consume_tradein_collected(_event(tradein, "tradein.collected"))
    assert d.population == "trade_in_intake" and d.custody_state == "in_refurb"
    # the seller can no longer give it away in the portal
    assert refused(
        c.env,
        lambda: d.sudo().action_transfer_ownership(
            c.stranger.id, reason="portal", channel="customer_portal"
        ),
    )
    Device.consume_tradein_paid(_event(tradein, "tradein.paid"))
    assert d.owner_id == tradein.company_id.partner_id
    # redelivery changes nothing
    rows = c.env["fix.device.ownership"].search_count([("device_id", "=", d.id)])
    Device.consume_tradein_paid(_event(tradein, "tradein.paid"))
    assert c.env["fix.device.ownership"].search_count([("device_id", "=", d.id)]) == rows


def test_m17_04_recycling_certificate_scraps_the_device(c):  # noqa: F811
    d = dev(c)
    cover = _active_warranty(c, d)
    item = (
        c.env["fix.ewaste.collection"].sudo().create({"customer_id": c.owner.id, "device_id": d.id})
    )
    Device = c.env["fix.device"].sudo()
    Device.consume_ewaste_collected(_event(item, "ewaste.collected"))
    assert d.population == "ewaste_pending"
    Device.consume_ewaste_certificate_issued(
        _event(item, "ewaste.certificate_issued", {"certificate": "M18-CERT-1"})
    )
    assert d.state == "scrapped" and d.custody_state == "disposed"
    assert cover.status == "voided" and not d.is_under_warranty()
    assert events(c, "device.end_of_life", d.id)


def test_m17_23_portal_transfers_go_only_to_an_individual_customer(c):  # noqa: F811
    d = dev(c)
    company = c.env["res.partner"].create({"name": "%s Ltd" % TAG, "is_company": True})
    assert refused(
        c.env,
        lambda: d.sudo().action_transfer_ownership(
            company.id, reason="x", channel="customer_portal"
        ),
    )
    assert refused(
        c.env,
        lambda: d.sudo().action_transfer_ownership(
            c.env.company.partner_id.id, reason="x", channel="customer_portal"
        ),
    )
    d.sudo().action_transfer_ownership(c.buyer.id, reason="gift", channel="customer_portal")
    assert d.owner_id == c.buyer


# ------------------------------------------------------------------ M17-06
def test_m17_06_no_service_order_invoice_on_a_provisional_identity(c, w):  # noqa: F811
    d = dev(c, serial_number=False, register_provisional=True, provisional_reason="Label gone")
    o = w.order(d)
    with pytest.raises(UserError, match="provisional"), c.env.cr.savepoint():
        c.env["fix.ar.invoice"].create({"source_model": "fix.service.order", "source_id": o.id})


# ------------------------------------------------------------------ M17-07
def test_m17_07_a_loaner_comes_from_company_stock_only(c, w):  # noqa: F811
    d, customer_phone, pool_phone = dev(c), dev(c), dev(c)
    o = w.order(d)
    assert refused(c.env, lambda: o.write({"loan_device_id": customer_phone.id}))
    _to_population(c, pool_phone, "rental_pool")
    o.write({"loan_device_id": pool_phone.id})
    pool_phone.with_user(c.clerk).action_mark_lost(reason="Lost by courier")
    o2 = w.order(dev(c))
    assert refused(c.env, lambda: o2.write({"loan_device_id": pool_phone.id}))


# ------------------------------------------------------------------ M17-08
def test_m17_08_warranty_changes_publish_warranty_updated(c):  # noqa: F811
    d = dev(c)
    before = len(events(c, "device.warranty_updated", d.id))
    today = d._dhaka_today()
    cover = (
        c.env["fix.warranty"]
        .with_user(c.clerk)
        .create({"device_id": d.id, "start_date": today, "end_date": today + timedelta(days=30)})
    )
    assert len(events(c, "device.warranty_updated", d.id)) == before + 1
    # a term corrected while pending is a change M09 must hear of
    cover.with_user(c.clerk).write({"end_date": today + timedelta(days=60)})
    assert len(events(c, "device.warranty_updated", d.id)) == before + 2
    cover.with_user(c.clerk).write({"end_date": today + timedelta(days=60)})  # an echo
    assert len(events(c, "device.warranty_updated", d.id)) == before + 2


# ------------------------------------------------------- M17-09 / M17-10
def test_m17_09_scrap_closes_cover_and_plans_and_no_order_opens(c, w):  # noqa: F811
    d = dev(c, eol_customer_instruction="recycle")
    cover = _active_warranty(c, d)
    plan = c.env["fix.device.pm"].create({"device_id": d.id, "next_due": d._dhaka_today()})
    lost = dev(c)
    _active_warranty(c, lost)
    lost.with_user(c.clerk).action_mark_lost(reason="lost")
    assert not lost.is_under_warranty()
    d.sudo()._guarded().write({"state": "scrapped"})  # the state, then the closure
    d._a07_close_for_end_of_life("scrapped in test", route="scrapped")
    assert not d.is_under_warranty() and cover.status == "voided" and plan.state == "paused"
    assert events(c, "device.end_of_life", d.id)
    assert refused(c.env, lambda: w.order(d))


def test_m17_10_an_approved_disposal_publishes_and_blocks_hand_on(c):  # noqa: F811
    d = dev(c)
    bm = _user(c.env, "a7erp_bm_eol", c.ou, [BM])
    decision = (
        c.env["fix.device.eol.decision"]
        .with_user(c.clerk)
        .create(
            {
                "device_id": d.id,
                "route": "dispose",
                "basis": "Board dead",
                "customer_instruction": "recycle",
            }
        )
    )
    decision.with_user(c.clerk).action_request()
    decision.with_user(bm).action_approve()
    assert d.population == "ewaste_pending" and events(c, "device.end_of_life", d.id)
    evidence = doc(c, "fix.device", d.id)
    assert refused(
        c.env,
        lambda: d.with_user(c.agent).action_transfer_ownership(
            c.stranger.id, "sale", reason="sell", evidence_document_id=evidence.id
        ),
    )


# ------------------------------------------------------------------ M17-11
def test_m17_11_purchase_date_is_corrected_only_by_an_officer_with_proof(c):  # noqa: F811
    d = dev(c, purchase_date="2024-01-10")
    assert refused(c.env, lambda: d.with_user(c.clerk).write({"purchase_date": "2026-10-01"}))
    assert refused(
        c.env, lambda: d.with_user(c.clerk).action_correct_purchase_date("2024-02-01", "typo")
    )
    assert refused(
        c.env, lambda: d.with_user(c.officer).action_correct_purchase_date("2024-02-01", "typo")
    )
    proof = doc(c, "fix.device", d.id, doc_type="invoice")
    d.with_user(c.officer).action_correct_purchase_date(
        "2024-02-01", "Receipt shows 1 Feb", evidence_document_id=proof.id
    )
    assert str(d.purchase_date) == "2024-02-01"


# ------------------------------------------------------- M17-12 / M17-13
def test_m17_13_a_shared_identifier_quarantines_both_until_qm_resolves(c):  # noqa: F811
    a, b = dev(c), dev(c)
    _active_warranty(c, a)
    a.with_user(c.clerk).action_add_identifier("brand_service_tag", "TAG-777")
    b.with_user(c.clerk).action_add_identifier("brand_service_tag", " tag-777 ")
    assert a.identifier_quarantined and b.identifier_quarantined
    assert not a.is_under_warranty() and events(c, "device.identifier_conflict", b.id)
    evidence = doc(c, "fix.device", a.id)
    assert refused(
        c.env,
        lambda: a.with_user(c.agent).action_transfer_ownership(
            c.buyer.id, "sale", reason="sell", evidence_document_id=evidence.id
        ),
    )
    issues = c.env["fix.device.quality.issue"].search(
        [("device_id", "in", (a | b).ids), ("issue_type", "=", "conflict")]
    )
    # M17-12: the clerk cannot assign himself, nor resolve a conflict once assigned
    assert refused(
        c.env, lambda: issues[0].with_user(c.clerk).write({"assigned_to_id": c.clerk.id})
    )
    bm = _user(c.env, "a7erp_bm_q", c.ou, [BM])
    issues[0].with_user(bm).action_assign(c.clerk.login)
    assert refused(c.env, lambda: issues[0].with_user(c.clerk).action_resolve("mine"))
    for issue in issues:
        issue.with_user(c.qm).action_resolve("Tag belongs to the first device")
    assert not a.identifier_quarantined and not b.identifier_quarantined


# ------------------------------------------------------------------ M17-14
def test_m17_14_custody_state_follows_the_order_and_dormancy(c, w):  # noqa: F811
    d = dev(c)
    o = w.order(d)
    o._guarded().write({"state": "intake"})
    assert d.custody_state == "under_service" and d.custody_branch_id == w.branch
    idle = dev(c)
    idle.sudo()._guarded().write({"last_activity_at": fields.Datetime.now() - timedelta(days=900)})
    c.env["fix.device"].cron_dormancy_sweep()
    assert idle.dormant and not d.dormant


# ------------------------------------------------------- M17-15 / M17-16
def test_m17_15_history_rows_are_idempotent_per_event(c):  # noqa: F811
    d = dev(c)
    d.add_history("repair", "Workshop job J1: a -> b", event_ref="evt-1")
    d.add_history("repair", "Workshop job J1: a -> b", event_ref="evt-1")
    assert c.env["fix.device.history"].search_count([("event_ref", "=", "evt-1")]) == 1


def test_m17_16_repeat_fault_counts_distinct_orders_in_the_window(c, w):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers.a07 import m17 as pack

    once, twice = dev(c), dev(c)
    first = w.order(once)
    for state in ("intake", "diagnostic"):
        first._guarded().write({"state": state})
    w.order(twice)
    w.order(twice)
    rows = pack.repeat_fault(c.env)["rows"]
    names = {r["device"] for r in rows}
    assert twice.name in names and once.name not in names


# ------------------------------------------------------------------ M17-17
def test_m17_17_a_population_change_waits_for_an_operations_director(c, w):  # noqa: F811
    d = dev(c)
    change = (
        c.env["fix.device.population.change"]
        .with_user(c.agent)
        .create(
            {"device_id": d.id, "to_population": "rental_pool", "reason_code": "rental_onboarding"}
        )
    )
    assert change.state == "requested" and d.population == "customer_owned"
    assert refused(c.env, lambda: change.with_user(c.agent).action_approve())
    change.with_user(w.approver).action_approve()
    assert d.population == "rental_pool" and events(c, "device.population_changed", d.id)
    own = (
        c.env["fix.device.population.change"]
        .with_user(w.approver)
        .create(
            {"device_id": d.id, "to_population": "refurbishment_stock", "reason_code": "correction"}
        )
    )
    assert refused(c.env, lambda: own.with_user(w.approver).action_approve())
    own.with_user(w.approver2).action_reject("not now")
    assert d.population == "rental_pool"


# ------------------------------------------------------- M17-18 / D12(a)
def test_d12_a_transfer_lapses_1000fix_cover_and_leaves_company_stock(c):  # noqa: F811
    d = dev(c)
    _to_population(c, d, "rental_pool")
    oem = _active_warranty(c, d, "manufacturer")
    ext = _active_warranty(c, d, "extended")
    evidence = doc(c, "fix.device", d.id)
    d.with_user(c.agent).action_transfer_ownership(
        c.buyer.id, "sale", reason="Sold pool unit", evidence_document_id=evidence.id
    )
    assert oem.status == "active" and ext.status == "voided"
    assert d.population == "customer_owned"


def test_d12_the_m09_four_eyes_transfer_carries_the_extended_cover(c):  # noqa: F811
    d = dev(c)
    ext = _active_warranty(c, d, "extended")
    clerk = _user(c.env, "a7erp_m09_clerk", c.ou, [M09_CLERK])
    officer = _user(c.env, "a7erp_m09_off", c.ou, [M09_OFFICER])
    transfer = (
        c.env["fix.warranty.transfer"]
        .with_user(clerk)
        .create(
            {
                "name": "%s-WT" % TAG,
                "warranty_id": ext.id,
                "from_partner_id": c.owner.id,
                "to_partner_id": c.buyer.id,
                "effective_date": d._dhaka_today(),
                "evidence_document_id": doc(c, "fix.device", d.id).id,
            }
        )
    )
    transfer.with_user(officer).action_approve()
    transfer.sudo().action_effect()
    assert d.owner_id == c.buyer and ext.status == "active"


# ------------------------------------------------------- M17-20 / M17-21
def test_m17_20_a_warranty_with_proof_is_not_moved_to_another_device(c):  # noqa: F811
    a, b = dev(c), dev(c)
    today = a._dhaka_today()
    cover = (
        c.env["fix.warranty"]
        .with_user(c.clerk)
        .create({"device_id": a.id, "start_date": today, "end_date": today + timedelta(days=90)})
    )
    cover.with_user(c.clerk).write(
        {"proof_document_id": doc(c, "fix.warranty", cover.id, doc_type="warranty_card").id}
    )
    assert refused(c.env, lambda: cover.with_user(c.clerk).write({"device_id": b.id}))


def test_m17_21_verification_records_the_derivation_basis(c):  # noqa: F811
    d = dev(c)
    today = d._dhaka_today()
    cover = (
        c.env["fix.warranty"]
        .with_user(c.clerk)
        .create({"device_id": d.id, "start_date": today, "end_date": today + timedelta(days=90)})
    )
    cover.with_user(c.clerk).write(
        {"proof_document_id": doc(c, "fix.warranty", cover.id, doc_type="warranty_card").id}
    )
    approve_via_inbox(cover, c.officer, requester=c.clerk, justification="card")
    assert cover.status == "active" and cover.derivation_basis == "purchase_evidence"


# ------------------------------------------------- M17-24 / M17-28
def test_m17_24_28_entitlements_in_priority_and_extended_status(c):  # noqa: F811
    d = dev(c)
    ext = _active_warranty(c, d, "extended")
    assert d.warranty_status == "extended"
    oem = _active_warranty(c, d, "manufacturer")
    d.invalidate_recordset(["warranty_status"])
    assert d.warranty_status == "in_warranty"
    found = d.resolve_entitlements()
    assert [f["id"] for f in found] == [ext.id, oem.id]
    d.with_user(c.clerk).action_mark_lost(reason="lost")
    assert d.resolve_entitlements() == []


# ------------------------------------------------- M17-29 / M17-30 / M17-31
def test_m17_29_30_channel_and_effective_date(c):  # noqa: F811
    d = dev(c)
    evidence = doc(c, "fix.device", d.id)
    assert refused(
        c.env,
        lambda: d.with_user(c.agent).action_transfer_ownership(
            c.buyer.id,
            "sale",
            reason="x",
            evidence_document_id=evidence.id,
            channel="customer_portal",
        ),
    )
    future = d._dhaka_today() + timedelta(days=3)
    assert refused(
        c.env,
        lambda: d.with_user(c.agent).action_transfer_ownership(
            c.buyer.id, "sale", reason="x", evidence_document_id=evidence.id, effective_date=future
        ),
    )
    past = d._dhaka_today() - timedelta(days=5)
    d.with_user(c.agent).action_transfer_ownership(
        c.buyer.id,
        "sale",
        reason="Sold last week",
        evidence_document_id=evidence.id,
        effective_date=past,
    )
    row = c.env["fix.device.ownership"].search([("device_id", "=", d.id)], limit=1)
    assert row.transfer_date == past and row.channel == "back_office"


def test_m17_30_an_escalated_issue_reaches_a_manager_as_an_activity(c, w):  # noqa: F811
    d = dev(c, branch_id=w.branch.id)
    bm = _user(c.env, "a7erp_bm_esc", c.ou, [BM])
    w.branch.manager_id = bm
    issue = (
        c.env["fix.device.quality.issue"]
        .sudo()
        .create({"device_id": d.id, "issue_type": "incomplete", "description": "No owner phone"})
    )
    issue._guarded().write({"raised_at": fields.Datetime.now() - timedelta(days=60)})
    c.env["fix.device.quality.issue"].cron_steward_sweep()
    assert issue.escalated and issue.activity_ids.filtered(lambda a: a.user_id == bm)


def test_m17_31_expiry_runs_on_the_dhaka_day(c):  # noqa: F811
    d = dev(c)
    dhaka = d._dhaka_today()
    cover = c.env["fix.warranty"].create(
        {
            "device_id": d.id,
            "start_date": dhaka - timedelta(days=30),
            "end_date": dhaka - timedelta(days=1),
        }
    )
    cover._guarded().write({"status": "active"})
    # a cron user far west of Dhaka still expires cover that ended yesterday in Dhaka
    c.env["fix.warranty"].with_context(tz="Pacific/Honolulu")._cron_expire_warranties()
    assert cover.status == "expired"


# ------------------------------------------------------------------ LEAD-02
def test_lead_02_a_part_issued_to_the_job_is_installed_in_the_device(c, w):  # noqa: F811
    d = dev(c)
    o = w.order(d)
    env = c.env
    part = env["fix.spare.part"].create(
        {"name": "%s Screen" % TAG, "part_number": "%s-SCR" % TAG, "part_category": "display"}
    )
    loc = env["fix.stock.location"].create(
        {"name": "%s Hub" % TAG, "code": "A7ERPHUB", "location_type": "branch"}
    )
    lot = env["fix.stock.lot"].create(
        {
            "name": "%s-LOT-1" % TAG,
            "part_id": part.id,
            "location_id": loc.id,
            "warranty_until": d._dhaka_today() + timedelta(days=180),
        }
    )
    tech = env["hr.employee"].create({"name": "%s Tech" % TAG})
    cons = (
        env["fix.stock.consumption"]
        .sudo()
        .create(
            {
                "service_order_ref": o.name,
                "product_id": part.id,
                "location_id": loc.id,
                "technician_id": tech.id,
                "scanned_code": "%s-SCR" % TAG,
                "state": "consumed",
                "consumed_at": fields.Datetime.now(),
                "lot_id": lot.id,
                "job_model": "fix.service.order",
                "job_res_id": o.id,
                "ownership_class": "owned",
            }
        )
    )
    Component = env["fix.device.component"].sudo()
    Component.consume_stock_consumed(_event(cons, "stock.consumed"))
    Component.consume_stock_consumed(_event(cons, "stock.consumed"))
    fitted = Component.search([("stock_consumption_id", "=", cons.id)])
    assert len(fitted) == 1 and fitted.device_id == d
    assert fitted.lot_model == "fix.stock.lot" and fitted.lot_id == lot.id
    assert fitted.serial_no == lot.name and fitted.technician_id == tech
    assert fitted.warranty_until == lot.warranty_until and fitted.ownership_class == "company_stock"
    assert fitted.service_order_model == "fix.service.order" and fitted.service_order_id == o.id
    cons._guarded().write({"state": "returned"})
    Component.consume_stock_returned(_event(cons, "stock.returned"))
    assert fitted.state == "removed"


# ------------------------------------------------------------------ M17-05
def test_m17_05_resale_cover_is_active_from_the_sale(c):  # noqa: F811
    env = c.env
    d = dev(c)
    grade = env["fix.refurb.grade"].sudo().search([], limit=1)
    if not grade:
        pytest.skip("no refurbishment grade on this database")
    tradein = (
        env["fix.tradein.request"].sudo().create({"customer_id": c.owner.id, "device_id": d.id})
    )
    _to_population(c, d, "refurbishment_stock")
    stock = (
        env["fix.graded.stock"]
        .sudo()
        .create(
            {
                "device_id": d.id,
                "grade_id": grade.id,
                "tradein_id": tradein.id,
                "acquisition_cost": 1000.0,
                "resale_price": 5000.0,
            }
        )
    )
    stock._guarded().write({"state": "sold"})
    event = _event(stock, "graded_stock.sold")
    # M14 issues its cover first (relay order), born pending
    env["fix.tradein.request"].sudo().consume_graded_stock_sold(event)
    cover = d.warranty_id.filtered(lambda w: w.warranty_type == "extended")
    assert cover.status == "pending"
    env["fix.warranty"].sudo().consume_graded_stock_sold(event)
    assert cover.status == "active" and cover.derivation_basis == "contract"
    assert d.is_under_warranty()
    # no buyer on record: the worklist says so
    assert env["fix.device.quality.issue"].search_count(
        [("device_id", "=", d.id), ("issue_type", "=", "incomplete")]
    )
