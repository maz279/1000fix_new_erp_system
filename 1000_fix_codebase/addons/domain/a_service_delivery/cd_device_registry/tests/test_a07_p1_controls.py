"""A07 P1/P2 (M17): the spec's roles, the scheduled jobs, record scope and the
lifecycle depth (identifier history, provisional identity, merge lineage,
NEIR status, release evidence, genealogy), attacked as NON-ADMIN users on the
live ORM (``odoo_env``: fix_test, rolled back). Each attack runs as a user
WITH the role they would really hold, and without it where the role is the
control; each refusal is paired with the proper path working.

A07 audit 2026-11-03/04: M17-1 (transfer with no proof), M17-2 (re-identify,
NEIR), M17-3 (merge lineage), M17-4 (custody), M17-5 (warranty expiry),
M17-6 (scope), M17-7 (history forged), M17-8 (lifecycle), M17-9 (identifiers),
M17-11 (genealogy), M17-12 (PM), M17-14 (estates), M17-17 (roles), D9 (crons).
"""

import json
import re
import types
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

TAG = "A7P1"
AGENT = "cd_device_registry.group_device_registry_user"
BM = "cd_device_registry.group_device_branch_manager"
QM = "cd_device_registry.group_device_quality_manager"
OFFICER = "cd_device_registry.group_warranty_officer"
REFUSED = (UserError, ValidationError, AccessError, IntegrityError)
IMEI_A, IMEI_B, IMEI_BAD = "356938035643809", "490154203237518", "356938035643808"


def _user(env, login, ou, groups=()):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED:
        return True
    return False


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, seq=iter(range(1, 999)))
    x.ou = env["operating.unit"].search([], limit=1)
    x.ou2 = env["operating.unit"].search([("id", "!=", x.ou.id)], limit=1) or env[
        "operating.unit"
    ].create(
        {
            "name": f"{TAG} OU2",
            "code": TAG,
            "partner_id": env.company.partner_id.id,
            "company_id": env.company.id,
        }
    )
    brand = env["fix.brand"].create({"name": f"{TAG} Brand", "code": TAG})
    x.model = env["fix.device.model"].create({"name": f"{TAG} Phone", "brand_id": brand.id})
    x.clerk = _user(env, f"{TAG.lower()}_clerk", x.ou)
    x.clerk2 = _user(env, f"{TAG.lower()}_clerk2", x.ou)
    x.clerk_b = _user(env, f"{TAG.lower()}_clerk_b", x.ou2)
    x.agent = _user(env, f"{TAG.lower()}_agent", x.ou, [AGENT])
    x.bm = _user(env, f"{TAG.lower()}_bm", x.ou, [BM])
    x.bm2 = _user(env, f"{TAG.lower()}_bm2", x.ou, [BM])
    x.qm = _user(env, f"{TAG.lower()}_qm", x.ou, [QM])
    x.officer = _user(env, f"{TAG.lower()}_officer", x.ou, [OFFICER])
    x.owner = env["res.partner"].create({"name": f"{TAG} Owner"})
    x.buyer = env["res.partner"].create({"name": f"{TAG} Buyer"})
    x.stranger = env["res.partner"].create({"name": f"{TAG} Stranger"})
    x.today = fields.Date.context_today(env["fix.device"])
    return x


def dev(c, user=None, **kw):
    vals = {
        "device_model_id": c.model.id,
        "serial_number": "%s-SN-%03d" % (TAG, next(c.seq)),
        "owner_id": c.owner.id,
    }
    vals.update(kw)
    Device = c.env["fix.device"].with_user(user) if user else c.env["fix.device"]
    return Device.create(vals)


def doc(c, res_model=False, res_id=0, doc_type="contract"):
    att = c.env["ir.attachment"].create({"name": "evidence.pdf", "raw": b"%PDF-1.4 a7p1"})
    return c.env["fix.document"].create(
        {
            "name": "Evidence",
            "attachment_id": att.id,
            "document_type": doc_type,
            "res_model": res_model,
            "res_id": res_id,
        }
    )


def events(c, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id:
        domain.append(("aggregate_id", "=", aggregate_id))
    return c.env["fix.event.outbox"].sudo().search(domain)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()

    def ep(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    try:
        yield types.SimpleNamespace(
            as_user=as_user,
            write=lambda **kw: ep("model_write")(ctl, **kw),
            action=lambda **kw: ep("model_action")(ctl, **kw),
            g=g,
        )
    finally:
        g.request, s.request = old_g, old_s


# ============================================================ roles (P1)
def test_spec_roles_exist_with_the_manager_implying_the_agent(c):
    agent, bm, qm = (c.env.ref(x) for x in (AGENT, BM, QM))
    assert c.env.ref("base.group_user") in agent.implied_ids
    assert agent in bm.implied_ids and agent in qm.implied_ids
    admin = c.env.ref("base.user_admin")
    assert all(admin in g.all_user_ids for g in (agent, bm, qm))
    assert c.bm.has_group(AGENT) and not c.clerk.has_group(AGENT)
    # configuration goes to the manager: a plain user may not edit the matrix
    Matrix = c.env["fix.device.part.compatibility"]
    vals = {"model_id": c.model.id, "part_number": f"{TAG}-P", "part_name": "Panel"}
    assert refused(c.env, lambda: Matrix.with_user(c.clerk).create(vals))
    assert Matrix.with_user(c.bm).create(vals).part_number == f"{TAG}-P"


# ============================================================ crons (P1)
@pytest.mark.parametrize(
    "xmlid, model, method",
    [
        # one warranty job: the A02 record, which also runs the A07 notices
        ("cd_device_registry.ir_cron_warranty_expiry", "fix.warranty", "_cron_expire_warranties"),
        ("cd_device_registry.ir_cron_device_pm_due", "fix.device.pm", "cron_pm_due"),
    ],
)
def test_cron_records_exist_are_active_and_call_the_method(c, xmlid, model, method):
    cron = c.env.ref(xmlid)
    assert cron.active and cron.model_id.model == model
    assert cron.code.strip() == "model.%s()" % method
    assert callable(getattr(c.env[model], method))


def test_warranty_cron_expires_ended_cover_and_announces_expiry_once(c):
    d = dev(c)
    W = c.env["fix.warranty"]
    ended = W.create(
        {
            "device_id": d.id,
            "start_date": c.today - timedelta(days=400),
            "end_date": c.today - timedelta(days=1),
            "status": "active",
        }
    )
    ending = W.create(
        {
            "device_id": d.id,
            "start_date": c.today - timedelta(days=10),
            "end_date": c.today + timedelta(days=5),
            "status": "active",
        }
    )
    W._cron_expire_warranties()
    assert ended.status == "expired" and ending.status == "active"
    assert ending.expiry_notified_on == fields.Date.context_today(W.with_context(tz="Asia/Dhaka"))
    expired_ev = events(c, "device.warranty_expired", d.id)
    expiring_ev = events(c, "device.warranty_expiring", d.id)
    assert len(expired_ev) == 1 and len(expiring_ev) == 1
    assert json.loads(expired_ev.payload)["warranty_id"] == ended.id
    # idempotent: a second run the same day changes and publishes nothing
    assert W._cron_expire_warranties() == 0
    assert len(events(c, "device.warranty_expired", d.id)) == 1
    assert len(events(c, "device.warranty_expiring", d.id)) == 1
    # the stamp is the cron's: a user cannot reset it to be told again
    assert refused(c.env, lambda: ending.with_user(c.clerk).write({"expiry_notified_on": False}))


def test_pm_cron_announces_a_due_plan_once_per_due_date(c):
    d = dev(c)
    Pm = c.env["fix.device.pm"]
    due = Pm.create({"device_id": d.id, "next_due": c.today - timedelta(days=3)})
    later = Pm.create({"device_id": d.id, "next_due": c.today + timedelta(days=40)})
    assert Pm.cron_pm_due() >= 1
    ev = events(c, "device.maintenance_due", d.id)
    assert len(ev) == 1 and json.loads(ev.payload)["plan_id"] == due.id
    assert due.due_notified_for == due.next_due and not later.due_notified_for
    Pm.cron_pm_due()
    assert len(events(c, "device.maintenance_due", d.id)) == 1
    assert refused(c.env, lambda: due.with_user(c.clerk).write({"due_notified_for": False}))


# ============================================================ ownership transfer
def test_transfer_needs_the_agent_role_a_reason_and_evidence(c):
    d = dev(c)
    with pytest.raises(AccessError, match="Device Registry Agent"), c.env.cr.savepoint():
        d.with_user(c.clerk).action_transfer_ownership(c.buyer.id, reason="sold")
    as_agent = d.with_user(c.agent)
    with pytest.raises(UserError, match="reason"), c.env.cr.savepoint():
        as_agent.action_transfer_ownership(c.buyer.id, evidence_document_id=doc(c).id)
    with pytest.raises(UserError, match="evidence"), c.env.cr.savepoint():
        as_agent.action_transfer_ownership(c.buyer.id, reason="sold")
    # evidence filed against another record is not this transfer's evidence
    foreign = doc(c, "res.partner", c.stranger.id)
    with pytest.raises(UserError, match="another record"), c.env.cr.savepoint():
        as_agent.action_transfer_ownership(
            c.buyer.id, reason="sold", evidence_document_id=foreign.id
        )
    assert d.owner_id == c.owner and not c.env["fix.device.ownership"].search(
        [("device_id", "=", d.id)]
    )
    proof = doc(c)
    as_agent.action_transfer_ownership(
        c.buyer.id,
        transfer_type="sale",
        reason="sold at the counter",
        evidence_document_id=proof.id,
    )
    row = c.env["fix.device.ownership"].search([("device_id", "=", d.id)])
    assert (d.owner_id, row.to_partner_id, row.reason) == (c.buyer, c.buyer, "sold at the counter")
    assert (row.evidence_document_id, row.recorded_by_id, row.channel) == (
        proof,
        c.agent,
        "back_office",
    )
    assert (proof.res_model, proof.res_id) == ("fix.device", d.id)
    payload = json.loads(events(c, "device.ownership_transferred", d.id).payload)
    assert payload["from_owner_id"] == c.owner.id and payload["evidence_document_id"] == proof.id


def test_p03_transfer_reads_the_transfer_staged_on_the_asset(c, p03):
    assert "action_transfer_ownership" in p03.g.SURFACES["fix.device"]["actions"]
    d = dev(c)
    proof = doc(c)
    d.with_user(c.agent).write(
        {
            "transfer_to_partner_id": c.buyer.id,
            "transfer_type_pending": "gift",
            "transfer_reason": "gift to a sibling",
            "transfer_evidence_document_id": proof.id,
        }
    )
    p03.as_user(c.clerk)
    out = p03.action(model="fix.device", ids=[d.id], method="action_transfer_ownership")
    assert not out["success"] and d.owner_id == c.owner
    p03.as_user(c.agent)
    out = p03.action(model="fix.device", ids=[d.id], method="action_transfer_ownership")
    assert out["success"], out
    row = c.env["fix.device.ownership"].search([("device_id", "=", d.id)])
    assert (d.owner_id, row.transfer_type, row.reason) == (c.buyer, "gift", "gift to a sibling")
    assert not (d.transfer_to_partner_id or d.transfer_reason or d.transfer_evidence_document_id)


def test_a_technician_does_not_re_own_a_device_in_his_custody(c):
    d = dev(c)
    emp = c.env["hr.employee"].create({"name": f"{TAG} Tech", "user_id": c.agent.id})
    c.env["fix.device.custody"].create(
        {
            "device_id": d.id,
            "event": "returned",
            "custodian_id": emp.id,
            "from_party_id": c.owner.id,
        }
    )
    with pytest.raises(UserError, match="your custody"), c.env.cr.savepoint():
        d.with_user(c.agent).action_transfer_ownership(
            c.buyer.id, reason="sold", evidence_document_id=doc(c).id
        )
    d.with_user(c.bm).action_transfer_ownership(
        c.buyer.id, reason="sold", evidence_document_id=doc(c).id
    )
    assert d.owner_id == c.buyer


def test_neir_deregistration_on_transfer_is_a_switch_and_blocked_imeis_stop_hand_over(c):
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_device_registry.neir_deregistration_on_transfer", "1"
    )
    d = dev(c, imei_1=IMEI_A)
    imei_row = d.identifier_ids.filtered(lambda i: i.identifier_type == "imei_1")
    assert imei_row.neir_status == "not_checked" and d.neir_status == "not_checked"
    d.with_user(c.agent).action_transfer_ownership(
        c.buyer.id, reason="sold", evidence_document_id=doc(c).id
    )
    assert imei_row.neir_status == "deregistration_pending"
    payload = json.loads(events(c, "device.neir_deregistration_required", d.id).payload)
    assert payload["imeis"] == [IMEI_A] and payload["to_owner_id"] == c.buyer.id
    # a NEIR result is recorded by a Branch Manager with its reference
    with pytest.raises(AccessError), c.env.cr.savepoint():
        imei_row.with_user(c.clerk).action_neir_blocked("BTRC-1")
    with pytest.raises(UserError, match="reference"), c.env.cr.savepoint():
        imei_row.with_user(c.bm).action_neir_blocked("  ")
    imei_row.with_user(c.bm).action_neir_blocked("BTRC-STOLEN-77")
    d.invalidate_recordset(["neir_status"])
    assert d.neir_status == "blocked" and imei_row.neir_checked_by_id == c.bm
    with pytest.raises(UserError, match="NEIR"), c.env.cr.savepoint():
        d.with_user(c.agent).action_transfer_ownership(
            c.owner.id, reason="back", evidence_document_id=doc(c).id
        )
    with pytest.raises(UserError, match="NEIR"), c.env.cr.savepoint():
        c.env["fix.device.custody"].with_user(c.clerk).create(
            {"device_id": d.id, "event": "transferred", "to_party_id": c.stranger.id}
        )
    # the row itself is a registry record: not typed, not deleted
    assert refused(c.env, lambda: imei_row.with_user(c.bm).write({"neir_status": "registered"}))
    assert refused(c.env, lambda: imei_row.with_user(c.bm).unlink())


# ============================================================ identifiers
def test_identifier_variants_and_cross_imei_collisions_are_refused(c):
    dev(c, serial_number=f"{TAG}-DUPE", imei_1=IMEI_A)
    for serial in (f"{TAG.lower()}-dupe", f"  {TAG}-DUPE "):
        assert refused(c.env, lambda s=serial: dev(c, user=c.clerk, serial_number=s)), serial
    assert refused(c.env, lambda: dev(c, user=c.clerk, imei_2=IMEI_A))
    assert refused(c.env, lambda: dev(c, user=c.clerk, imei_2="NOT-AN-IMEI"))
    assert refused(c.env, lambda: dev(c, user=c.clerk, imei_1=IMEI_B, imei_2=IMEI_B))
    padded = dev(c, user=c.clerk, serial_number=f"  {TAG}-PAD  ")
    assert padded.serial_number == f"{TAG}-PAD"


def test_a_bad_check_digit_warns_without_blocking(c):
    bad = dev(c, user=c.clerk, imei_1=IMEI_BAD)
    good = dev(c, user=c.clerk, imei_1=IMEI_B)
    assert "IMEI 1 fails the IMEI check digit" in bad.identifier_warning
    assert not good.identifier_warning
    assert refused(c.env, lambda: good.with_user(c.clerk).write({"identifier_warning": "x"}))


def test_identifier_history_keeps_every_value_with_source_and_correction(c):
    d = dev(c, user=c.clerk, imei_1=IMEI_A)
    rows = d.identifier_ids
    assert set(rows.mapped("identifier_type")) == {"serial_number", "imei_1"}
    assert set(rows.mapped("source")) == {"registration"} and rows.captured_by_id == c.clerk
    d.with_user(c.clerk).write({"imei_2": IMEI_B})
    d.invalidate_recordset(["identifier_ids"])
    cap = d.identifier_ids.filtered(lambda i: i.identifier_type == "imei_2")
    assert (cap.value, cap.source) == (IMEI_B, "capture")
    with pytest.raises(AccessError), c.env.cr.savepoint():
        d.with_user(c.bm).action_correct_identifier("imei_1", "490154203237526", "board swap")
    d.with_user(c.qm).action_correct_identifier("imei_1", "490154203237526", "board swap J-9")
    d.invalidate_recordset(["identifier_ids"])
    old = d.identifier_ids.filtered(lambda i: i.value == IMEI_A)
    new = d.identifier_ids.filtered(lambda i: i.value == "490154203237526")
    assert not old.is_current and old.supersede_reason == "board swap J-9"
    assert old.superseded_by_id == c.qm and new.is_current and new.source == "correction"
    assert events(c, "device.identifier_corrected", d.id)
    # plain users read the history, never write it
    Identifier = c.env["fix.device.identifier"].with_user(c.clerk)
    assert Identifier.search([("device_id", "=", d.id)])
    assert refused(
        c.env,
        lambda: Identifier.create(
            {
                "device_id": d.id,
                "identifier_type": "imei_1",
                "value": IMEI_A,
                "source": "capture",
                "captured_at": fields.Datetime.now(),
            }
        ),
    )
    assert refused(c.env, lambda: old.with_user(c.clerk).write({"is_current": True}))


# ============================================================ provisional
def test_a_provisional_identity_gets_no_cover_no_transfer_until_confirmed(c):
    d = dev(c, user=c.clerk, serial_number=False, state="provisional")
    assert d.state == "provisional"
    assert events(c, "device.provisional_raised", d.id)
    w = c.env["fix.warranty"].create(
        {
            "device_id": d.id,
            "start_date": c.today - timedelta(days=5),
            "end_date": c.today + timedelta(days=300),
            "status": "active",
        }
    )
    assert not d.is_under_warranty()
    pending = (
        c.env["fix.warranty"]
        .with_user(c.clerk)
        .create(
            {
                "device_id": d.id,
                "start_date": c.today,
                "end_date": c.today + timedelta(days=30),
                "proof_document_id": doc(c, "fix.device", d.id, "warranty_card").id,
            }
        )
    )
    # verification is a routed approval (A02 B1): the request itself is refused
    with pytest.raises(UserError, match="provisional"), c.env.cr.savepoint():
        pending.with_user(c.clerk).action_request_approval(justification="card on file")
    with pytest.raises(UserError, match="Provisional"), c.env.cr.savepoint():
        d.with_user(c.agent).action_transfer_ownership(
            c.buyer.id, reason="sold", evidence_document_id=doc(c).id
        )
    with pytest.raises(UserError, match="BRU-AST-03"), c.env.cr.savepoint():
        d.assert_identity_resolved("be invoiced")
    with pytest.raises(AccessError), c.env.cr.savepoint():
        d.with_user(c.clerk).action_confirm_identity()
    with pytest.raises(UserError, match="Capture"), c.env.cr.savepoint():
        d.with_user(c.agent).action_confirm_identity()
    d.with_user(c.clerk).write({"imei_1": IMEI_A})
    d.with_user(c.agent).action_confirm_identity()
    assert (d.state, d.identity_confirmed_by_id) == ("registered", c.agent)
    assert d.is_under_warranty() and w.status == "active"


# ============================================================ lost / custody
def test_a_lost_custody_event_flags_the_device_and_a_branch_manager_clears_it(c):
    d = dev(c)
    c.env["fix.device.custody"].with_user(c.clerk).create(
        {"device_id": d.id, "event": "lost", "notes": "snatched at Farmgate"}
    )
    assert (d.state, d.lost_flagged_by_id) == ("lost", c.clerk)
    assert json.loads(events(c, "device.flagged", d.id).payload)["source"] == "custody"
    with pytest.raises(AccessError, match="Branch Manager"), c.env.cr.savepoint():
        d.with_user(c.clerk2).action_clear_lost("found")
    d.with_user(c.bm).action_clear_lost("recovered by police, GD 44")
    # a Branch Manager who flagged it himself does not clear it either
    d.with_user(c.bm2).action_mark_lost("second report")
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        d.with_user(c.bm2).action_clear_lost("found")
    d.with_user(c.bm).action_clear_lost("withdrawn")
    assert d.state == "registered" and events(c, "device.flag_cleared", d.id)


def test_release_needs_owner_condition_photo_and_accessories(c):
    d = dev(c)
    Custody = c.env["fix.device.custody"].with_user(c.clerk)
    base = {"device_id": d.id, "event": "issued"}
    # to a stranger: refused whatever evidence
    assert refused(c.env, lambda: Custody.create(dict(base, to_party_id=c.stranger.id)))
    with pytest.raises(UserError, match="BRU-AST-08"), c.env.cr.savepoint():
        Custody.create(dict(base, to_party_id=c.owner.id))
    grade = c.env["fix.device.condition"].with_user(c.clerk).create({"device_id": d.id})
    other_grade = c.env["fix.device.condition"].create({"device_id": dev(c).id})
    other_grade.action_confirm()
    grade.with_user(c.clerk2).action_confirm()
    photo = doc(c, doc_type="custody_photo")
    full = dict(
        base,
        to_party_id=c.owner.id,
        condition_id=grade.id,
        evidence_document_id=photo.id,
        accessories_reconciled=True,
        signature_ref="SIG-1",
    )
    for drop in ("evidence_document_id", "accessories_reconciled"):
        vals = dict(full)
        vals.pop(drop)
        assert refused(c.env, lambda v=vals: Custody.create(v)), drop
    assert refused(c.env, lambda: Custody.create(dict(full, condition_id=other_grade.id)))
    ev = Custody.create(full)
    assert (photo.res_model, photo.res_id) == ("fix.device.custody", ev.id)
    payload = json.loads(events(c, "device.custody_recorded", d.id)[:1].payload)
    assert payload["condition_grade"] == grade.grade
    # a lost device is released to no one
    d.with_user(c.clerk).action_mark_lost("reported stolen")
    assert refused(c.env, lambda: Custody.create(full))


# ============================================================ service history
def test_history_is_projected_never_typed(c):
    d = dev(c)
    H = c.env["fix.device.history"].with_user(c.clerk)
    vals = {
        "device_id": d.id,
        "event_type": "repair",
        "description": "forged",
        "date": fields.Datetime.now() - timedelta(days=30),
    }
    with pytest.raises(UserError, match="projected"), c.env.cr.savepoint():
        H.create(vals)
    d.with_user(c.clerk).add_history("repair", "real repair on the bench")
    assert c.env["fix.device.history"].search_count([("device_id", "=", d.id)]) == 1


# ============================================================ merge lineage
def _merge(c, p, d):
    r = (
        c.env["fix.device.identity"]
        .with_user(c.clerk)
        .create({"primary_device_id": p.id, "duplicate_device_id": d.id, "match_reason": "label"})
    )
    approve_via_inbox(r, c.qm, requester=c.clerk)
    return r


def test_merge_repoints_history_and_keeps_a_reversible_lineage(c):
    p, d = dev(c), dev(c)
    d.add_history("repair", "on the duplicate")
    w = c.env["fix.warranty"].create(
        {"device_id": d.id, "start_date": c.today, "end_date": c.today + timedelta(days=365)}
    )
    k = c.env["fix.device.component"].create({"device_id": d.id, "part_name": "Battery"})
    r = _merge(c, p, d)
    assert r.state == "merged" and not d.active and r.resolved_by_id == c.qm
    H = c.env["fix.device.history"]
    assert not H.search_count([("device_id", "=", d.id)])
    assert H.search_count([("device_id", "=", p.id)]) == 1
    assert (w.device_id, k.device_id) == (p, p)
    lineage = r.merge_id
    assert (lineage.survivor_id, lineage.merged_id, lineage.approved_by_id) == (p, d, c.qm)
    refmap = json.loads(lineage.reference_map)
    assert w.id in refmap["fix.warranty"]["device_id"] and lineage.rows_repointed >= 3
    assert json.loads(events(c, "device.merged", p.id).payload)["merged_id"] == d.id
    # the lineage is a permanent record; reversal is the Quality Manager's
    assert refused(c.env, lambda: lineage.with_user(c.clerk).write({"state": "reversed"}))
    with pytest.raises(AccessError), c.env.cr.savepoint():
        lineage.with_user(c.bm).action_reverse("wrong pair")
    with pytest.raises(UserError, match="reason"), c.env.cr.savepoint():
        lineage.with_user(c.qm).action_reverse(" ")
    lineage.with_user(c.qm).action_reverse("two different phones after all")
    assert d.active and (w.device_id, k.device_id) == (d, d)
    assert H.search_count([("device_id", "=", d.id)]) == 1
    assert (r.state, lineage.state, lineage.reversed_by_id) == ("reversed", "reversed", c.qm)
    assert events(c, "device.merge_reversed", p.id)
    with pytest.raises(UserError, match="already"), c.env.cr.savepoint():
        lineage.with_user(c.qm).action_reverse("again")


def test_merge_reversal_closes_with_its_window(c):
    p, d = dev(c), dev(c)
    lineage = _merge(c, p, d).merge_id
    lineage.sudo()._guarded().write({"reversible_until": c.today - timedelta(days=1)})
    with pytest.raises(UserError, match="window"), c.env.cr.savepoint():
        lineage.with_user(c.qm).action_reverse("too late")
    assert not d.active


# ============================================================ warranty
def test_warranty_dates_and_proof_binding(c):
    d = dev(c)
    W = c.env["fix.warranty"].with_user(c.clerk)
    with pytest.raises(ValidationError, match="before it starts"), c.env.cr.savepoint():
        W.create({"device_id": d.id, "start_date": c.today, "end_date": c.today - timedelta(1)})
    foreign = doc(c, "res.partner", c.stranger.id, "other")
    w = W.create(
        {
            "device_id": d.id,
            "start_date": c.today,
            "end_date": c.today + timedelta(days=365),
            "proof_document_id": foreign.id,
        }
    )
    # verification is a routed approval (A02 B1): the request itself is refused
    with pytest.raises(UserError, match="another record"), c.env.cr.savepoint():
        w.with_user(c.clerk).action_request_approval(justification="receipt on file")
    unfiled = doc(c, doc_type="warranty_card")
    w.write({"proof_document_id": unfiled.id})
    approve_via_inbox(w, c.officer, requester=c.clerk, justification="card on file")
    assert w.status == "active" and (unfiled.res_model, unfiled.res_id) == ("fix.warranty", w.id)


# ============================================================ genealogy
def test_genealogy_fields_compatibility_and_disposition(c):
    d = dev(c)
    c.env["fix.device.part.compatibility"].create(
        {
            "model_id": c.model.id,
            "part_number": f"{TAG}-BAD",
            "part_name": "Bad panel",
            "category": "display",
            "compatibility_type": "incompatible",
        }
    )
    Comp = c.env["fix.device.component"].with_user(c.clerk)
    for vals in ({"part_number": f" {TAG.lower()}-bad "}, {"source_ref": f"{TAG}-BAD"}):
        assert refused(
            c.env, lambda v=vals: Comp.create(dict({"device_id": d.id, "part_name": "Panel"}, **v))
        ), vals
    assert refused(
        c.env,
        lambda: Comp.create(
            {"device_id": d.id, "part_name": "Panel", "warranty_until": c.today - timedelta(1)}
        ),
    )
    assert refused(
        c.env,
        lambda: Comp.create({"device_id": d.id, "part_name": "Panel", "service_order_id": 10**9}),
    )
    emp = c.env["hr.employee"].create({"name": f"{TAG} Fitter"})
    k = Comp.create(
        {
            "device_id": d.id,
            "part_name": "Panel",
            "part_number": f"{TAG}-OK",
            "technician_id": emp.id,
            "warranty_until": c.today + timedelta(days=90),
            "ownership_class": "company_stock",
        }
    )
    assert json.loads(events(c, "device.genealogy_recorded", d.id).payload)["component_id"] == k.id
    assert refused(c.env, lambda: k.write({"disposition": "harvested"}))
    k.action_remove()
    k.action_record_disposition("returned_to_customer")
    assert (k.state, k.disposition) == ("removed", "returned_to_customer")
    with pytest.raises(UserError, match="no disposition"), c.env.cr.savepoint():
        k.action_record_disposition("scrapped")


# ============================================================ PM
def test_plan_type_and_interval_agree(c):
    d = dev(c)
    Pm = c.env["fix.device.pm"].with_user(c.clerk)
    with pytest.raises(ValidationError, match="every 3 months"), c.env.cr.savepoint():
        Pm.create(
            {
                "device_id": d.id,
                "plan_type": "quarterly",
                "interval_months": 12,
                "next_due": c.today,
            }
        )
    q = Pm.create({"device_id": d.id, "plan_type": "quarterly", "next_due": c.today})
    b = Pm.create({"device_id": d.id, "interval_months": 6, "next_due": c.today})
    x = Pm.create({"device_id": d.id, "interval_months": 5, "next_due": c.today})
    assert (q.interval_months, b.plan_type, x.plan_type) == (3, "biannual", "custom")
    assert refused(c.env, lambda: q.write({"interval_months": 12, "plan_type": "quarterly"}))


# ============================================================ lifecycle / EOL
def test_lifecycle_stage_is_a_branch_manager_decision_with_customer_instruction(c):
    d = dev(c)
    assert refused(c.env, lambda: d.with_user(c.clerk).write({"lifecycle_stage": "obsolete"}))
    assert refused(c.env, lambda: d.with_user(c.clerk).write({"end_of_support_date": c.today}))
    with pytest.raises(AccessError), c.env.cr.savepoint():
        d.with_user(c.clerk).action_set_vintage("parts scarce")
    with pytest.raises(UserError, match="basis"), c.env.cr.savepoint():
        d.with_user(c.bm).action_set_vintage("")
    d.with_user(c.bm).action_set_vintage("OEM parts on allocation only")
    assert (d.lifecycle_stage, d.lifecycle_decided_by_id) == ("vintage", c.bm)
    with pytest.raises(UserError, match="instruction"), c.env.cr.savepoint():
        d.with_user(c.bm).action_set_obsolete("BER")
    d.with_user(c.clerk).write({"eol_customer_instruction": "recycle"})
    d.with_user(c.bm).action_set_obsolete("beyond economic repair, customer signed form")
    assert d.lifecycle_stage == "obsolete" and d.end_of_support_date
    payload = json.loads(events(c, "device.lifecycle_changed", d.id).sorted("id")[-1].payload)
    assert payload["to_stage"] == "obsolete" and payload["customer_instruction"] == "recycle"
    with pytest.raises(UserError, match="final"), c.env.cr.savepoint():
        d.with_user(c.bm2).action_set_vintage("undo")


# ============================================================ estates
def test_an_estate_holds_only_the_clients_own_devices(c):
    corp = c.env["res.partner"].create({"name": f"{TAG} Corp", "is_company": True})
    staff = c.env["res.partner"].create({"name": f"{TAG} Corp Staff", "parent_id": corp.id})
    est = c.env["fix.device.estate"].with_user(c.clerk).create({"name": "HQ", "client_id": corp.id})
    personal = dev(c)
    with pytest.raises(ValidationError, match="cannot sit in the estate"), c.env.cr.savepoint():
        personal.with_user(c.clerk).write({"estate_id": est.id})
    issued = dev(c, owner_id=staff.id)
    issued.with_user(c.clerk).write({"estate_id": est.id})
    assert issued.estate_id == est
    # the device leaves the estate with an owner outside the client
    issued.with_user(c.agent).action_transfer_ownership(
        c.buyer.id, reason="sold to staff member", evidence_document_id=doc(c).id
    )
    assert not issued.estate_id


# ============================================================ scope
def test_devices_and_satellite_rows_follow_the_operating_unit(c):
    m17 = pytest.importorskip("odoo.addons.cd_p03_portal.controllers.a07.m17")
    env_b = c.env(user=c.clerk_b.id)
    k0 = m17.kpis(env_b)["devices_active"]
    d = dev(c, user=c.clerk, imei_1=IMEI_A)
    assert d.operating_unit_id == c.ou
    d.add_history("repair", "bench")
    d.sudo().action_transfer_ownership(c.buyer.id)
    c.env["fix.device.custody"].create({"device_id": d.id, "event": "returned"})
    for model in (
        "fix.device",
        "fix.device.ownership",
        "fix.device.custody",
        "fix.device.history",
        "fix.device.identifier",
    ):
        field = "id" if model == "fix.device" else "device_id"
        assert not c.env[model].with_user(c.clerk_b).search([(field, "=", d.id)]), model
        assert c.env[model].with_user(c.clerk).search([(field, "=", d.id)]), model
    assert not [r for r in m17.asset_360(env_b)["rows"] if r["device"] == d.name]
    assert m17.kpis(env_b)["devices_active"] == k0
    assert [r for r in m17.asset_360(c.env(user=c.clerk.id))["rows"] if r["device"] == d.name]


def test_customer_endpoint_support_view_needs_the_agent_role(c):
    import odoo.addons.cd_customer_portal.controllers.customer_api as capi

    dev(c, user=c.clerk, imei_1=IMEI_A)  # lands in the clerk's unit (OU1)
    c.clerk_b.group_ids = [(4, c.env.ref(AGENT).id)]
    ctl = capi.CustomerApiController()
    endpoint = capi.CustomerApiController.devices
    endpoint = getattr(endpoint, "original_endpoint", endpoint)
    old = getattr(capi, "request", None)
    try:
        capi.request = types.SimpleNamespace(env=c.env(user=c.clerk.id))
        out = endpoint(ctl, partner_id=c.owner.id)
        assert out["error"]["code"] == "not_permitted" and "devices" not in out
        capi.request = types.SimpleNamespace(env=c.env(user=c.agent.id))
        out = endpoint(ctl, partner_id=c.owner.id)
        assert [x["imei_1"] for x in out["devices"]] == [IMEI_A]
        capi.request = types.SimpleNamespace(env=c.env(user=c.clerk_b.id))
        out = endpoint(ctl, partner_id=c.owner.id)
        assert out["devices"] == []  # an agent of another unit sees none of them
    finally:
        capi.request = old


# ============================================================ P03 wiring
_JS = Path(__file__).resolve().parents[4] / "platform/cd_p03_portal/static/src/a07/m17.js"


def test_p03_m17_columns_and_form_fields_exist(c):
    """Unknown columns drop silently in the workspace: every list column and
    form field the M17 screens declare is a real field of its model."""
    text = _JS.read_text(encoding="utf-8")
    checked = 0
    for block in re.split(r"\n  '(?=M17-)", text):
        model = re.search(r"model: '([\w.]+)'", block)
        if not model or model.group(1) not in c.env:
            continue
        Model = c.env[model.group(1)]
        cols = re.search(r"cols: \[([^\]]*)\]", block)
        names = re.findall(r"'(\w+)'", cols.group(1)) if cols else []
        names += re.findall(r"\{ name: '(\w+)'", block)
        missing = [n for n in names if n not in Model._fields]
        assert not missing, (model.group(1), missing)
        checked += len(names)
    assert checked > 100


def test_p03_new_surfaces_are_registered_with_their_actions(c, p03):
    S = p03.g.SURFACES
    assert {"action_neir_blocked", "action_neir_registered"} <= S["fix.device.identifier"][
        "actions"
    ]
    assert S["fix.device.merge"]["actions"] == {"action_reverse"}
    assert S["fix.device.identifier"]["writable"] == frozenset()
    assert {"action_confirm_identity", "action_set_obsolete"} <= S["fix.device"]["actions"]
