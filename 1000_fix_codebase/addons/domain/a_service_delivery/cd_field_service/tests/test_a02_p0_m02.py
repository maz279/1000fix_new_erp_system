"""A02 audit P0, M02 Field Service & Dispatch: the probe gaps as controls.

The A02 workflow audit (2026-11-03, working/A02_evidence/probes/m02_m03/
probe_m02.py) found 19 gaps in cd_field_service: a technician wrote
state=completed with customer_otp_verified=True on a dispatched order,
self-dispatched through the workspace, accepted another technician's job,
cancelled an in-progress job with no reason, checked in 11 km outside the
geofence, cleared the mock-GPS block, moved a breached SLA deadline 30 days
out, completed with no evidence, and a typed TrxID marked the service order
settled.

Every control is tested both ways, as NON-ADMIN users created here: the
bypass is refused, and the legitimate path still works. ``odoo_env``
(addons/conftest.py) rolls back after every test.
"""

import base64
import json
import types
from datetime import timedelta
from unittest.mock import patch

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
GUARD = "changes only through its workflow"
PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="
)


# --------------------------------------------------------------------- world
@pytest.fixture
def w(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    co = env.company
    entity = env["fix.entity"].create(
        {"code": "P0M02", "legal_name": "A02 P0 M02 entity", "company_id": co.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "P0 M02 Branch",
            "code": "P0M02",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    zone = env["fix.zone"].create({"name": "P0 M02 Zone", "code": "P0MZ"})
    branch.write({"zone_id": zone.id})
    brand = env["fix.brand"].create({"name": "P0M02Brand", "code": "P0MB"})
    model = env["fix.device.model"].create({"name": "P0 Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "P0 M02 Customer", "phone": "01711000998"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-P0M02-1"}
    )

    def so(**kw):
        vals = {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "onsite P0",
            "service_type": "onsite",
        }
        vals.update(kw)
        return env["fix.service.order"].create(vals)

    order = so()
    g_tech = env.ref("cd_field_service.group_fix_field_service_user")
    g_disp = env.ref("cd_field_service.group_fix_field_service_manager")

    def mk(login, groups):
        user = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [(6, 0, [env.ref("base.group_user").id] + [g.id for g in groups])],
                    "company_id": co.id,
                    "company_ids": [(6, 0, [co.id])],
                    "operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )
        emp = env["hr.employee"].create({"name": login, "user_id": user.id})
        return user, emp

    ua, ea = mk("p0m02_tech_a", [g_tech])
    ub, eb = mk("p0m02_tech_b", [g_tech])
    ud, ed = mk("p0m02_dispatcher", [g_disp])

    def fo(state="draft", tech=None, **kw):
        rec = env["fix.field.order"].create(
            {
                "order_id": kw.pop("order_id", order.id),
                "zone_id": zone.id,
                "operating_unit_id": ou.id,
                **kw,
            }
        )
        # setup only: the superuser places the record in the state under test
        rec.write({"state": state, "technician_id": tech.id if tech else False})
        return rec

    return types.SimpleNamespace(
        env=env, ou=ou, co=co, zone=zone, branch=branch, order=order, so=so, fo=fo,
        ua=ua, ea=ea, ub=ub, eb=eb, ud=ud, ed=ed, g_disp=g_disp,
    )  # fmt: skip


def p03(w, user, monkeypatch):
    """In-process /p03/model/write and /p03/model/action as ``user``."""
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    monkeypatch.setattr(g, "request", types.SimpleNamespace(env=w.env(user=user.id)))
    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    ma = getattr(
        g.P03GenericApiController.model_action,
        "original_endpoint",
        g.P03GenericApiController.model_action,
    )
    return (lambda **kw: mw(ctl, **kw)), (lambda **kw: ma(ctl, **kw))  # fmt: skip


def refused(env, fn):
    """Run fn in a savepoint; the refusal text, or None when it went through."""
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return str(exc)
    return None


def walk_to_in_progress(rec, user):
    r = rec.with_user(user)
    r.action_accept()
    r.action_start_travel()
    r.action_arrive()
    r.action_start_work()


def _attachment(rec, name="evidence.png"):
    return (
        rec.env["ir.attachment"]
        .sudo()
        .create(
            {
                "name": name,
                "raw": base64.b64decode(PNG_B64),
                "mimetype": "image/png",
                "res_model": "fix.field.order",
                "res_id": rec.id,
            }
        )
    )


def give_evidence(rec, signature=True, photo=True, summary=True):
    """What the technician app's evidence channel links (superuser, as the
    bearer channel runs), and the technician's own work summary."""
    if signature:
        rec.sudo()._fix_attach_field_evidence(_attachment(rec, "sig.png"), "signature", "Karim")
    if photo:
        rec.sudo()._fix_attach_field_evidence(_attachment(rec, "after.png"), "photo")
    if summary:
        rec.sudo().work_summary = "Replaced the compressor relay; tested 30 minutes."


def _fence(w, lat=23.8, lng=90.4, radius=300, **kw):
    return w.env["fix.geofence"].create(
        {
            "name": "P0 fence",
            "geofence_type": "circle",
            "zone_id": w.zone.id,
            "geometry_json": json.dumps({"lat": lat, "lng": lng, "radius_m": radius}),
            **kw,
        }
    )


# ================================================== A1: guarded fields (M02-1)
def test_technician_cannot_write_state_or_stamps_but_the_actions_can(w):
    """M02-1/M02-10: state and the journey stamps change only through the actions."""
    rec = w.fo("dispatched", w.ea)
    stamp = fields.Datetime.now() - timedelta(hours=5)
    for vals in (
        {"state": "completed"},
        {"arrived_at": stamp},
        {"completed_at": stamp},
        {"customer_otp_verified": True},
        {"sla_deadline": fields.Datetime.now() + timedelta(days=30)},
        {"technician_id": w.eb.id},
        {"onsite_payment_trx_id": "FAKE-1"},
        {"is_mock_location": True},
    ):
        err = refused(w.env, lambda vals=vals: rec.with_user(w.ua).write(vals))
        assert err and GUARD in err, vals
    rec.invalidate_recordset()
    assert rec.state == "dispatched" and not rec.arrived_at
    # the legitimate path: the assigned technician's actions write the same fields
    walk_to_in_progress(rec, w.ua)
    assert rec.state == "in_progress" and rec.arrived_at and rec.started_work_at


def test_p03_write_cannot_forge_completion(w, monkeypatch):
    """M02-1 over /p03/model/write: state, OTP flag, TrxID."""
    rec = w.fo("dispatched", w.ea)
    mw, _ma = p03(w, w.ua, monkeypatch)
    res = mw(
        model="fix.field.order",
        record_id=rec.id,
        values={
            "state": "completed",
            "customer_otp_verified": True,
            "work_summary": "forged",
            "onsite_payment_trx_id": "FAKE-TRX-1",
        },
    )
    w.env.invalidate_all()
    assert res.get("error") and rec.state == "dispatched" and not rec.customer_otp_verified
    # what the form does offer (the work summary) still saves
    res = mw(model="fix.field.order", record_id=rec.id, values={"work_summary": "Gate code 1234"})
    w.env.invalidate_all()
    assert not res.get("error"), res
    assert rec.work_summary == "Gate code 1234"


def test_sla_deadline_cannot_be_moved_and_is_derived_at_create(w, monkeypatch):
    """M02-7: a technician moved a breached deadline 30 days out."""
    rec = w.fo("in_progress", w.ea)
    rec.sudo()._guarded().write({"sla_deadline": fields.Datetime.now() - timedelta(hours=2)})
    before = rec.sla_deadline
    mw, _ma = p03(w, w.ua, monkeypatch)
    new = fields.Datetime.to_string(fields.Datetime.now() + timedelta(days=30))
    res = mw(model="fix.field.order", record_id=rec.id, values={"sla_deadline": new})
    w.env.invalidate_all()
    assert res.get("error") and rec.sla_deadline == before
    # at create, an untrusted caller cannot type a deadline ...
    so = w.so(sla_resolution_deadline=fields.Datetime.now() + timedelta(hours=8))
    FO = w.env["fix.field.order"].with_user(w.ud)
    vals = {"order_id": so.id, "zone_id": w.zone.id, "operating_unit_id": w.ou.id}
    far = fields.Datetime.now() + timedelta(days=60)
    assert GUARD in refused(w.env, lambda: FO.create({**vals, "sla_deadline": far}))
    # ... the service order's own deadline is derived (and may be passed, as the bridge does)
    made = FO.create(dict(vals))
    passed = FO.create({**vals, "sla_deadline": so.sla_resolution_deadline})
    assert made.sla_deadline == so.sla_resolution_deadline == passed.sla_deadline


def test_m01_bridge_still_creates_the_field_order_as_a_plain_user(w):
    """The M01 hand-off passes the SLA deadline it derives; it still works for a
    non-admin user once the field is guarded."""
    so = w.so(sla_resolution_deadline=fields.Datetime.now() + timedelta(hours=6))
    fo = so.with_user(w.ud).action_create_field_order()
    assert fo.state == "draft" and fo.sla_deadline == so.sla_resolution_deadline


def test_reassignment_is_a_dispatcher_action_with_a_reason(w, monkeypatch):
    """M02-4: technician B took over A's in-progress job by editing technician_id."""
    rec = w.fo("in_progress", w.ea)
    mw, ma = p03(w, w.ub, monkeypatch)
    res = mw(model="fix.field.order", record_id=rec.id, values={"technician_id": w.eb.id})
    w.env.invalidate_all()
    assert res.get("error") and rec.technician_id == w.ea
    # a technician cannot reassign; a dispatcher cannot reassign a job already on site
    assert refused(w.env, lambda: rec.with_user(w.ub).action_reassign(w.eb.id, "mine now"))
    assert "can be reassigned" in refused(
        w.env, lambda: rec.with_user(w.ud).action_reassign(w.eb.id, "swap")
    )
    # the legitimate path: a dispatched job, by the dispatcher, with a reason
    job = w.fo("accepted", w.ea)
    assert "reason" in refused(w.env, lambda: job.with_user(w.ud).action_reassign(w.eb.id))
    _mw, ma = p03(w, w.ud, monkeypatch)
    res = ma(
        model="fix.field.order",
        ids=[job.id],
        method="action_reassign",
        kwargs={"reassignment": "%d A is off sick" % w.eb.id},
    )
    w.env.invalidate_all()
    assert res.get("success"), res
    assert (job.technician_id, job.state, job.accepted_at) == (w.eb, "dispatched", False)
    assert any("A is off sick" in (b or "") for b in job.message_ids.mapped("body"))


def test_decline_log_cannot_be_created_directly_and_never_flips_an_order(w, monkeypatch):
    """M02-4: creating a decline log through the P03 form declined an ACCEPTED order."""
    rec = w.fo("accepted", w.ea)
    mw, _ma = p03(w, w.ua, monkeypatch)
    res = mw(
        model="fix.field.decline.log",
        values={
            "field_order_id": rec.id,
            "technician_id": w.ea.id,
            "reason": "other",
            "notes": "x",
        },
    )
    w.env.invalidate_all()
    assert rec.state == "accepted" and not res.get("id")
    Log = w.env["fix.field.decline.log"]
    assert refused(
        w.env,
        lambda: Log.with_user(w.ud).create(
            {"field_order_id": rec.id, "technician_id": w.ea.id, "reason": "other"}
        ),
    )
    # even a trusted (superuser) log create leaves the order's state alone
    Log.create({"field_order_id": rec.id, "technician_id": w.ea.id, "reason": "capacity"})
    assert rec.state == "accepted"


def test_mock_location_flag_cannot_be_cleared_by_the_technician(w, monkeypatch):
    """M02-8: the technician cleared the mock-GPS hard block and checked in."""
    rec = w.fo("en_route", w.ea)
    rec.write({"is_mock_location": True})
    mw, ma = p03(w, w.ua, monkeypatch)
    res_w = mw(model="fix.field.order", record_id=rec.id, values={"is_mock_location": False})
    res_a = ma(model="fix.field.order", ids=[rec.id], method="action_arrive")
    w.env.invalidate_all()
    assert res_w.get("error") and not res_a.get("success")
    assert rec.state == "en_route" and rec.is_mock_location
    # without the flag the same technician checks in
    clean = w.fo("en_route", w.ea)
    clean.with_user(w.ua).action_arrive()
    assert clean.state == "arrived"


def test_route_state_moves_only_through_the_route_actions(w):
    route = w.env["fix.field.route"].create(
        {"technician_id": w.ea.id, "operating_unit_id": w.ou.id}
    )
    for vals in ({"route_state": "completed"}, {"total_distance_km": 3.0}):
        assert GUARD in refused(w.env, lambda vals=vals: route.with_user(w.ua).write(vals))
    route.with_user(w.ua).action_start_route()
    route.with_user(w.ua).action_complete_route()
    assert route.route_state == "completed"


# ===================================================== A3: dispatch authority
def test_only_a_dispatcher_dispatches(w, monkeypatch):
    """M02-4: a plain technician self-dispatched through P03."""
    rec = w.fo("pending_dispatch")
    _mw, ma = p03(w, w.ub, monkeypatch)
    res = ma(
        model="fix.field.order",
        ids=[rec.id],
        method="action_dispatch",
        kwargs={"technician_id": w.eb.id},
    )
    w.env.invalidate_all()
    assert not res.get("success") and rec.state == "pending_dispatch" and not rec.technician_id
    _mw, ma = p03(w, w.ud, monkeypatch)
    res = ma(
        model="fix.field.order",
        ids=[rec.id],
        method="action_dispatch",
        kwargs={"technician_id": w.eb.id},
    )
    w.env.invalidate_all()
    assert res.get("success"), res
    assert (rec.state, rec.technician_id) == ("dispatched", w.eb) and rec.dispatched_at


def test_only_the_assigned_technician_accepts_and_progresses(w):
    """M02-4: technician B accepted (and could then work) A's job."""
    rec = w.fo("dispatched", w.ea)
    assert refused(w.env, lambda: rec.with_user(w.ub).action_accept())
    assert refused(w.env, lambda: rec.with_user(w.ud).action_accept())  # not the dispatcher either
    rec.with_user(w.ua).action_accept()
    assert refused(w.env, lambda: rec.with_user(w.ub).action_start_travel())
    rec.with_user(w.ua).action_start_travel()
    assert rec.state == "en_route"


def test_decline_needs_the_assigned_technician_and_a_reason(w, monkeypatch):
    rec = w.fo("dispatched", w.ea)
    assert refused(w.env, lambda: rec.with_user(w.ub).action_decline(reason="distance"))
    assert "Say why" in refused(w.env, lambda: rec.with_user(w.ua).action_decline())
    _mw, ma = p03(w, w.ua, monkeypatch)
    res = ma(
        model="fix.field.order",
        ids=[rec.id],
        method="action_decline",
        kwargs={"reason": "Van broke down"},
    )
    w.env.invalidate_all()
    assert res.get("success"), res
    assert (rec.state, rec.technician_id, rec.decline_reason) == (
        "declined",
        w.ea.browse(),
        "other",
    )
    log = w.env["fix.field.decline.log"].search([("field_order_id", "=", rec.id)])
    assert (log.technician_id, log.notes) == (w.ea, "Van broke down")


def test_cancel_needs_a_reason_and_a_dispatcher_once_in_dispatch(w):
    """M02-9: a technician cancelled an in-progress job with no reason."""
    rec = w.fo("in_progress", w.ea)
    assert refused(w.env, lambda: rec.with_user(w.ua).action_cancel(reason="customer away"))
    assert "reason" in refused(w.env, lambda: rec.with_user(w.ud).action_cancel())
    rec.with_user(w.ud).action_cancel(reason="Customer cancelled by phone")
    assert (rec.state, rec.cancel_reason) == ("cancelled", "Customer cancelled by phone")
    # a draft (not yet in dispatch) is cancelled by its creator, still with a reason
    draft = w.fo("draft")
    draft.with_user(w.ua).action_cancel(reason="Raised in error")
    assert draft.state == "cancelled"


# ================================================ A5: completion evidence
def test_completion_needs_sign_off_photo_and_summary(w):
    """M02-2 / URD US-P3-013: completed with no OTP, signature, photo or notes."""
    rec = w.fo("dispatched", w.ea)
    walk_to_in_progress(rec, w.ua)
    err = refused(w.env, lambda: rec.with_user(w.ua).action_complete())
    assert "sign-off" in err and "post-work photo" in err and "work summary" in err
    give_evidence(rec, photo=False)
    assert "post-work photo" in refused(w.env, lambda: rec.with_user(w.ua).action_complete())
    give_evidence(rec, signature=False, summary=False)
    # only the assigned technician completes
    assert refused(w.env, lambda: rec.with_user(w.ub).action_complete())
    rec.with_user(w.ua).action_complete()
    assert rec.state == "completed" and rec.completed_at
    assert rec.customer_signature_sha256 and len(rec.customer_signature_sha256) == 64
    # a completed order keeps its evidence and summary
    assert refused(w.env, lambda: rec.with_user(w.ua).write({"work_summary": "rewritten"}))


def test_a_verified_otp_stands_in_for_the_signature(w):
    rec = w.fo("dispatched", w.ea)
    walk_to_in_progress(rec, w.ua)
    give_evidence(rec, signature=False)
    assert "sign-off" in refused(w.env, lambda: rec.with_user(w.ua).action_complete())
    rec.sudo().write({"customer_otp_verified": True})  # a trusted verification step
    rec.with_user(w.ua).action_complete()
    assert rec.state == "completed"


def test_evidence_profile_switch_fails_closed(w):
    ICP = w.env["ir.config_parameter"].sudo()
    rec = w.fo("dispatched", w.ea)
    walk_to_in_progress(rec, w.ua)
    give_evidence(rec, photo=False)
    ICP.set_param("cd_field_service.completion_evidence_profile", "anything-else")
    assert "post-work photo" in refused(w.env, lambda: rec.with_user(w.ua).action_complete())
    ICP.set_param("cd_field_service.completion_evidence_profile", "no_photo")
    rec.with_user(w.ua).action_complete()
    assert rec.state == "completed"


def test_a_photo_taken_before_work_is_not_post_work_evidence(w):
    rec = w.fo("arrived", w.ea)
    rec.sudo()._fix_attach_field_evidence(_attachment(rec), "photo")
    assert rec.pre_work_photo_attachment_id and not rec.post_work_photo_attachment_id
    foreign = w.fo("in_progress", w.eb)
    with pytest.raises(UserError, match="does not belong"):
        foreign.sudo()._fix_attach_field_evidence(_attachment(rec), "photo")


# --- the technician app channels (offline sync + evidence upload) ----------
def _sync(w, user, commands, monkeypatch):
    import odoo.addons.cd_field_service.controllers.offline_sync_api as osa
    import odoo.addons.cd_service_order.controllers.technician_api as tapi

    ns = types.SimpleNamespace(env=w.env(user=user.id))
    monkeypatch.setattr(osa, "request", ns)
    monkeypatch.setattr(tapi, "request", ns)
    ctl = osa.OfflineSyncApiController()
    fn = getattr(
        osa.OfflineSyncApiController.offline_sync,
        "original_endpoint",
        osa.OfflineSyncApiController.offline_sync,
    )
    res = fn(ctl, device_id="DEV-P0", commands=commands, batch_checksum=tapi.batch_digest(commands))
    w.env.invalidate_all()
    return res  # fmt: skip


def _cmd(cid, rec, op, payload=None):
    return {"command_id": cid, "model": "fix.field.order", "record_id": rec.id, "operation": op, "payload": payload or {}}  # fmt: skip


def test_offline_signature_stores_a_verifiable_artefact(w, monkeypatch):
    """M02-2: the op answered verified=True for a client token and stored nothing."""
    rec = w.fo("in_progress", w.ea)
    token = _sync(
        w,
        w.ua,
        [_cmd("p0-sig-1", rec, "customer_signature", {"signer_name": "x", "signature_token": "x"})],
        monkeypatch,
    )
    assert "p0-sig-1" in token["rejected"] and not rec.customer_signature_attachment_id
    good = _sync(w, w.ua, [_cmd("p0-sig-2", rec, "customer_signature", {"signer_name": "Karim", "signature_base64": PNG_B64})], monkeypatch)  # fmt: skip
    ack = good["acknowledged"]["p0-sig-2"]
    assert "verified" not in ack and ack["recorded"] is True
    att = rec.customer_signature_attachment_id
    assert att and att.res_id == rec.id and att.mimetype == "image/png"
    assert (
        rec.customer_signature_signer == "Karim" and ack["sha256"] == rec.customer_signature_sha256
    )
    # technician B cannot sign A's order
    other = _sync(
        w,
        w.ub,
        [_cmd("p0-sig-3", rec, "customer_signature", {"signature_base64": PNG_B64})],
        monkeypatch,
    )
    assert "p0-sig-3" in other["rejected"]


def test_offline_completion_with_evidence_is_idempotent(w, monkeypatch):
    """DI-05 replay still executes once, now with the evidence gate in front."""
    rec = w.fo("in_progress", w.ea)
    give_evidence(rec, summary=False)
    c = [_cmd("p0-cmd-1", rec, "complete_order", {"resolution_notes": "fixed the fan"})]
    r1 = _sync(w, w.ua, c, monkeypatch)
    r2 = _sync(w, w.ua, c, monkeypatch)
    n = (
        w.env["fix.offline.idempotency.ledger"]
        .sudo()
        .search_count([("command_id", "=", "p0-cmd-1")])
    )
    assert "p0-cmd-1" in r1["acknowledged"] and "p0-cmd-1" in r2["acknowledged"]
    assert n == 1 and rec.state == "completed" and rec.work_summary == "fixed the fan"
    bare = w.fo("in_progress", w.ea)
    r3 = _sync(w, w.ua, [_cmd("p0-cmd-2", bare, "complete_order")], monkeypatch)
    assert "p0-cmd-2" in r3["rejected"] and bare.state == "in_progress"


def test_evidence_upload_links_the_signature_and_photo(w, monkeypatch):
    import odoo.addons.cd_field_service.controllers.evidence_api as eapi
    import odoo.addons.cd_service_order.controllers.technician_api as tapi

    rec = w.fo("in_progress", w.ea)
    ns = types.SimpleNamespace(env=w.env(user=w.ua.id))
    monkeypatch.setattr(eapi, "request", ns)
    monkeypatch.setattr(tapi, "request", ns)
    ctl = eapi.OfflineEvidenceApiController()
    fn = getattr(eapi.OfflineEvidenceApiController.upload_chunk, "original_endpoint", eapi.OfflineEvidenceApiController.upload_chunk)  # fmt: skip
    for media in ("signature", "photo"):
        res = fn(
            ctl, media_uuid="p0-%s" % media, chunk_index=0, total_chunks=1, chunk_data=PNG_B64,
            media_type=media, model="fix.field.order", record_id=rec.id,
        )  # fmt: skip
        assert res.get("complete"), res
    w.env.invalidate_all()
    assert rec.customer_signature_attachment_id and rec.post_work_photo_attachment_id


# ================================================== A4: on-site money (M02-3)
def test_collection_fields_are_recorded_by_the_action_only(w):
    rec = w.fo("in_progress", w.ea)
    assert GUARD in refused(
        w.env, lambda: rec.with_user(w.ua).write({"onsite_collection_amount": 5000.0})
    )
    assert "Transaction ID" in refused(
        w.env, lambda: rec.with_user(w.ua).action_record_collection(payment="bkash 900")
    )
    assert refused(w.env, lambda: rec.with_user(w.ub).action_record_collection(payment="cash 900"))
    rec.with_user(w.ua).action_record_collection(payment="bkash 900 8N7A6B5C")
    assert (rec.onsite_payment_method, rec.onsite_collection_amount, rec.onsite_payment_trx_id) == (
        "bkash",
        900.0,
        "8N7A6B5C",
    )


def _complete_with(w, so, payment):
    rec = w.fo("dispatched", w.ea, order_id=so.id)
    walk_to_in_progress(rec, w.ua)
    rec.with_user(w.ua).action_record_collection(payment=payment)
    give_evidence(rec)
    rec.with_user(w.ua).action_complete()
    return rec


def test_completion_never_writes_the_service_order_settlement_itself(w):
    """M02-3: a typed TrxID marked the SERVICE ORDER settled for BDT 5,000."""
    so = w.so()
    SO = type(so)
    calls = []

    def stub(self, amount, ref, source=None):
        calls.append((self.id, amount, ref, source))

    with patch.object(SO, "_fix_record_settlement", new=stub, create=True):
        rec = _complete_with(w, so, "bkash 5000 TRX-REAL-1")
    assert calls == [(so.id, 5000.0, "TRX-REAL-1", "field_collection")]
    assert rec.onsite_payment_state == "settled"
    assert so.payment_settlement_state != "settled"  # the stub settled nothing itself


def test_a_refused_or_missing_settlement_leaves_the_collection_pending(w):
    so = w.so()

    def refuse(self, amount, ref, source=None):
        raise UserError("no gateway receipt for %s" % ref)

    with patch.object(type(so), "_fix_record_settlement", new=refuse, create=True):
        rec = _complete_with(w, so, "nagad 700 TRX-UNVERIFIED")
    assert (rec.state, rec.onsite_payment_state) == ("completed", "pending_settlement")
    assert so.payment_settlement_state != "settled"
    if not hasattr(so, "_fix_record_settlement"):
        so2 = w.so()
        rec2 = _complete_with(w, so2, "bkash 300 TRX-2")
        assert rec2.onsite_payment_state == "pending_settlement"
        assert so2.payment_settlement_state != "settled"


def test_the_m01_settlement_records_a_field_trxid_unverified(w):
    """With M01's real _fix_record_settlement: the typed TrxID is a claim, so
    the service order records it UNVERIFIED (its delivery gate stays shut)."""
    so = w.so()
    if not hasattr(so, "_fix_record_settlement"):
        pytest.skip("cd_service_order has no _fix_record_settlement yet")
    rec = _complete_with(w, so, "bkash 1200 TRX-INTEG-1")
    assert rec.onsite_payment_state == "settled"
    assert (so.settlement_source, so.invoice_ref, so.settlement_verified) == (
        "field_collection",
        "TRX-INTEG-1",
        False,
    )


def _open_shift(w):
    return (
        w.env["fix.cash.shift"]
        .sudo()
        .create(
            {
                "branch_id": w.branch.id,
                "operating_unit_id": w.ou.id,
                "operator_id": w.ed.id,
                "opening_float": 1000.0,
                "company_id": w.co.id,
            }
        )
    )


def test_field_cash_waits_for_its_hand_over_before_any_settlement(w):
    """M02-3: cash marked the SO settled while it was still in the technician's pocket."""
    so = w.so()
    calls = []

    def stub(self, amount, ref, source=None):
        calls.append((amount, ref, source))

    with patch.object(type(so), "_fix_record_settlement", new=stub, create=True):
        rec = _complete_with(w, so, "cash 3000")
        assert rec.onsite_payment_state == "pending_handover" and not calls
        assert so.payment_settlement_state != "settled"
        # a drawer already being counted takes no cash (M04's _post_field_cash)
        counted = _open_shift(w)
        counted._guarded().write({"state": "counting"})
        assert refused(w.env, lambda: rec.with_user(w.ua).action_handover_field_cash(counted.id))
        assert not counted.field_cash_deposited and rec.onsite_payment_state == "pending_handover"
        counted._guarded().write({"state": "closed"})  # one live shift per branch (M04)
        shift = _open_shift(w)
        before = shift.field_cash_deposited
        assert refused(w.env, lambda: rec.with_user(w.ub).action_handover_field_cash(shift.id))
        rec.with_user(w.ua).action_handover_field_cash(shift.id)
        assert shift.field_cash_deposited == before + 3000.0
        assert (rec.cash_shift_id, rec.onsite_payment_state) == (shift, "settled")
        assert calls == [(3000.0, "COD/%s" % rec.name, "field_collection")]
        # handed over once only
        assert refused(w.env, lambda: rec.with_user(w.ua).action_handover_field_cash(shift.id))
    assert shift.field_cash_deposited == before + 3000.0


# =================================================== geofence (M02-8)
def test_arrival_outside_the_fence_is_refused_inside_is_accepted(w):
    rec = w.fo("en_route", w.ea, geofence_id=_fence(w).id)
    err = refused(
        w.env, lambda: rec.with_user(w.ua).action_arrive(current_lat=23.9, current_lon=90.4)
    )
    assert "outside the geofence" in err and rec.state == "en_route"
    rec.with_user(w.ua).action_arrive(current_lat=23.8005, current_lon=90.4)
    assert rec.state == "arrived" and rec.arrival_latitude == 23.8005


def test_p03_arrival_needs_a_position_on_a_fenced_order(w, monkeypatch):
    rec = w.fo("en_route", w.ea, geofence_id=_fence(w).id)
    _mw, ma = p03(w, w.ua, monkeypatch)
    res = ma(model="fix.field.order", ids=[rec.id], method="action_arrive")
    w.env.invalidate_all()
    assert not res.get("success") and "position" in res.get("error", "") and rec.state == "en_route"
    res = ma(
        model="fix.field.order",
        ids=[rec.id],
        method="action_arrive",
        kwargs={"position": "23.8001, 90.4001"},
    )
    w.env.invalidate_all()
    assert res.get("success"), res
    assert rec.state == "arrived"


def test_the_zone_fence_applies_when_the_order_has_none(w):
    _fence(w)
    rec = w.fo("en_route", w.ea)
    assert "position" in refused(w.env, lambda: rec.with_user(w.ua).action_arrive())
    assert "outside" in refused(
        w.env, lambda: rec.with_user(w.ua).action_arrive(position="24.5, 91.0")
    )
    rec.with_user(w.ua).action_arrive(position="23.8, 90.4")
    assert rec.state == "arrived"


def test_a_dispatcher_waives_the_fence_with_a_reason(w):
    rec = w.fo("en_route", w.ea, geofence_id=_fence(w).id)
    assert refused(w.env, lambda: rec.with_user(w.ua).action_waive_geofence("I am here"))
    assert "reason" in refused(w.env, lambda: rec.with_user(w.ud).action_waive_geofence())
    rec.with_user(w.ud).action_waive_geofence("Customer moved to the next building")
    assert rec.geofence_waived_by == w.ud
    rec.with_user(w.ua).action_arrive(current_lat=23.9, current_lon=90.4)
    assert rec.state == "arrived"


# ========================================================= SLA watch (M02-7)
def test_sla_breaches_are_escalated_to_a_dispatcher_once(w):
    breached = w.fo("pending_dispatch")
    breached.write({"sla_deadline": fields.Datetime.now() - timedelta(hours=3)})
    on_time = w.fo("pending_dispatch")
    on_time.write({"sla_deadline": fields.Datetime.now() + timedelta(hours=3)})
    done = w.fo("completed", w.ea)
    done.write({"sla_deadline": fields.Datetime.now() - timedelta(hours=3)})
    FO = w.env["fix.field.order"]
    assert FO._cron_escalate_sla_breaches() >= 1
    dispatchers = w.g_disp.all_user_ids
    acts = breached.activity_ids
    assert len(acts) == 1 and acts.user_id in dispatchers and "SLA breached" in acts.summary
    assert breached.sla_escalated_at and not on_time.sla_escalated_at and not done.sla_escalated_at
    FO._cron_escalate_sla_breaches()
    assert len(breached.activity_ids) == 1  # once
    cron = w.env.ref("cd_field_service.ir_cron_field_order_sla_escalation")
    assert cron.active and "_cron_escalate_sla_breaches" in cron.code


def test_sla_escalation_waits_for_an_appointed_dispatcher(w):
    breached = w.fo("dispatched", w.ea)
    breached.write({"sla_deadline": fields.Datetime.now() - timedelta(hours=3)})
    w.g_disp.sudo().write({"user_ids": [(5, 0, 0)]})
    w.env["fix.field.order"]._cron_escalate_sla_breaches()
    assert not breached.sla_escalated_at and not breached.activity_ids


# =========================================================== the P03 surface
def test_the_surface_whitelists_the_new_actions_and_offers_no_guarded_field():
    from odoo.addons.cd_p03_portal.controllers import a02
    from odoo.addons.cd_p03_portal.controllers.a02.writable import WRITABLE

    actions = a02.SURFACES["fix.field.order"]["actions"]
    for m in ("action_decline", "action_cancel", "action_handover_field_cash", "action_reassign",
              "action_record_collection", "action_waive_geofence"):  # fmt: skip
        assert m in actions
    offered = set(WRITABLE["fix.field.order"])
    assert not offered & {
        "state",
        "technician_id",
        "sla_deadline",
        "is_mock_location",
        "customer_otp_verified",
    }
    assert set(WRITABLE["fix.field.decline.log"]) == {"notes"}
