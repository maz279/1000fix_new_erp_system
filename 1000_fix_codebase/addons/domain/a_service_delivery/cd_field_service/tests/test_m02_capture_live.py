"""M02 capture audit (2026-11-18): the six records the sub-module pages now
capture, exercised on fix_test as the NON-ADMIN users who capture them.

Pages 1, 6, 7, 8, 9 and 11 had nothing a person could record: the spec's
dispatch override reason (BRU-FSM-04), device enrolment (T-11), conflict
review (AUT-FSM-06), tracking pause (BRU-FSM-05), failed visit with site
evidence (BRU-FSM-09) and the technician's daily cash reconciliation
(BRU-FSM-07) had no record. Each rule is tested both ways: the bypass is
refused and the legitimate path works. ``odoo_env`` rolls back per test.
"""

# ruff: noqa: F811 - `w` is the shared fixture, taken as an argument by every test
from datetime import timedelta

from odoo import fields

from .test_a02_p0_m02 import PNG_B64, p03, refused, w  # noqa: F401 - shared world
from .test_field_dispatch_ext import _shift

SITE = (23.8103, 90.4125)  # the order's site: Dhaka


def _events(env, event_type, aggregate_id):
    return (
        env["fix.event.outbox"]
        .sudo()
        .search_count([("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)])
    )


def _ranked_world(w):
    """ea ranks first (rostered today, certified); eb second (certified, not
    rostered) - the suggestion engine's own scoring."""
    fo = w.fo("pending_dispatch", latitude=SITE[0], longitude=SITE[1])
    w.env["fix.roster.slot"].create(
        {"employee_id": w.ea.id, "date": fo._fix_day(), "shift_id": _shift(w.env).id}
    )
    w.env["fix.work.order"].create({"order_id": w.order.id, "technician_id": w.eb.id})
    ranked = fo.sudo().action_suggest_technicians(limit=20)
    names = [r["employee_id"] for r in ranked]
    assert names.index(w.ea.id) == 0 and w.eb.id in names, ranked
    assert ranked[0]["score"] > next(r for r in ranked if r["employee_id"] == w.eb.id)["score"]
    return fo


def _decide(w, user, fo, tech, **kw):
    return (
        w.env["fix.dispatch.decision"]
        .with_user(user)
        .create({"field_order_id": fo.id, "technician_id": tech.id, **kw})
    )


# ------------------------------------------------- page 1: dispatch decision
def test_sending_the_recommended_technician_needs_no_reason(w):
    fo = _ranked_world(w)
    d = _decide(w, w.ud, fo, w.ea)
    assert fo.state == "dispatched" and fo.technician_id == w.ea
    assert not d.is_override and d.recommended_technician_id == w.ea and d.selected_rank == 1
    assert "rostered today" in d.explanation
    assert not _events(w.env, "assignment.overridden", d.id)


def test_overriding_the_recommendation_needs_a_reason(w):
    fo = _ranked_world(w)
    msg = refused(w.env, lambda: _decide(w, w.ud, fo, w.eb))
    assert msg and "BRU-FSM-04" in msg
    assert fo.state == "pending_dispatch" and not fo.technician_id
    msg = refused(w.env, lambda: _decide(w, w.ud, fo, w.eb, override_reason="other"))
    assert msg and "say why" in msg
    d = _decide(w, w.ud, fo, w.eb, override_reason="customer_preference", override_notes="asked")
    assert fo.state == "dispatched" and fo.technician_id == w.eb
    assert d.is_override and d.recommended_technician_id == w.ea and d.selected_rank > 1
    assert _events(w.env, "assignment.overridden", d.id) == 1


def test_a_technician_cannot_dispatch_and_a_decision_is_never_edited(w):
    fo = _ranked_world(w)
    assert refused(w.env, lambda: _decide(w, w.ua, fo, w.ea))
    assert fo.state == "pending_dispatch"
    d = _decide(w, w.ud, fo, w.ea)
    assert refused(w.env, lambda: d.with_user(w.ud).write({"override_notes": "later"}))
    assert refused(w.env, lambda: _decide(w, w.ud, fo, w.eb, override_reason="workload_balance"))


def test_the_workspace_dispatches_only_through_a_decision(w, monkeypatch):
    fo = _ranked_world(w)
    write, action = p03(w, w.ud, monkeypatch)
    res = action(model="fix.field.order", ids=[fo.id], method="action_dispatch",
                 kwargs={"technician_id": w.eb.id})  # fmt: skip
    assert not res.get("success") and fo.state == "pending_dispatch"
    res = write(model="fix.dispatch.decision", record_id=False,
                values={"field_order_id": fo.id, "technician_id": w.eb.id})  # fmt: skip
    assert "BRU-FSM-04" in (res.get("error") or "")
    res = write(model="fix.dispatch.decision", record_id=False,
                values={"field_order_id": fo.id, "technician_id": w.eb.id,
                        "override_reason": "parts_on_van"})  # fmt: skip
    assert res.get("id"), res
    assert fo.state == "dispatched" and fo.technician_id == w.eb


# ----------------------------------------------- page 6: device enrolment
def _enrol(w, user, emp, uid="DEV-M02-A"):
    return (
        w.env["fix.technician.device"]
        .with_user(user)
        .create({"employee_id": emp.id, "device_uid": uid, "platform": "android"})
    )


def test_a_dispatcher_enrols_and_revokes_a_device(w):
    Dev = w.env["fix.technician.device"]
    assert refused(w.env, lambda: _enrol(w, w.ua, w.ea))  # a technician enrols nothing
    dev = _enrol(w, w.ud, w.ea)
    assert dev.state == "enrolled" and dev.company_id
    assert refused(w.env, lambda: _enrol(w, w.ud, w.eb))  # one live enrolment per device
    assert Dev._fix_sync_refusal("DEV-M02-A", w.ea) is None
    assert "another technician" in Dev._fix_sync_refusal("DEV-M02-A", w.eb)
    assert Dev._fix_sync_refusal("DEV-NEVER-SEEN", w.ea) is None
    assert refused(w.env, lambda: dev.with_user(w.ua).action_revoke(revoke="lost"))
    assert refused(w.env, lambda: dev.with_user(w.ud).action_revoke(revoke="dropped it"))
    assert refused(w.env, lambda: dev.with_user(w.ud).write({"employee_id": w.eb.id}))
    dev.with_user(w.ud).action_revoke(revoke="stolen on the bus")
    assert dev.state == "revoked" and dev.revoke_notes == "on the bus"
    assert "revoked" in Dev._fix_sync_refusal("DEV-M02-A", w.ea)
    assert _events(w.env, "technician_device.revoked", dev.id) == 1


def test_a_revoked_device_cannot_sync(w, monkeypatch):
    from odoo.addons.cd_field_service.controllers import offline_sync_api as api

    dev = _enrol(w, w.ud, w.ea, "DEV-M02-SYNC")
    dev.with_user(w.ud).action_revoke(revoke="lost")
    cls = api.OfflineSyncApiController
    # unwrap @route and @api_edge to the method body
    fn = cls.offline_sync
    while hasattr(fn, "original_endpoint") or hasattr(fn, "__wrapped__"):
        fn = getattr(fn, "original_endpoint", None) or fn.__wrapped__
    monkeypatch.setattr(api, "resolve_technician", lambda kw: (w.ea, None))
    monkeypatch.setattr(api, "verify_batch_checksum", lambda c, s: None)
    monkeypatch.setattr(api, "_su_env", lambda: w.env)
    res = fn(cls(), device_id="DEV-M02-SYNC", commands=[])
    assert res.get("error", {}).get("code") == "device_refused", res
    # the same phone enrolled again syncs
    _enrol(w, w.ud, w.ea, "DEV-M02-SYNC")
    res = fn(cls(), device_id="DEV-M02-SYNC", commands=[])
    assert res.get("status") == "success", res


# --------------------------------------------- page 7: conflict review
def _ledger(w, tech, status="conflict_applied"):
    return w.env["fix.offline.idempotency.ledger"].create(
        {"command_id": "cmd-m02-%s-%s" % (tech.id, status), "technician_id": tech.id,
         "model": "fix.field.order", "operation": "complete_order", "status": status, "conflict_reason": "stale state"}
    )  # fmt: skip


def test_a_conflict_is_reviewed_once_by_someone_else(w):
    Review = w.env["fix.offline.conflict.review"]
    entry = _ledger(w, w.ea)
    assert entry.review_state == "pending"
    vals = {"ledger_id": entry.id, "decision": "server_kept", "notes": "told the technician"}
    assert refused(w.env, lambda: Review.with_user(w.ua).create(vals))
    clean = _ledger(w, w.ea, "applied")
    assert refused(w.env, lambda: Review.with_user(w.ud).create({**vals, "ledger_id": clean.id}))
    assert refused(w.env, lambda: Review.with_user(w.ud).create({**vals, "notes": " "}))
    own = _ledger(w, w.ed)  # the dispatcher's own command
    assert refused(w.env, lambda: Review.with_user(w.ud).create({**vals, "ledger_id": own.id}))
    rev = Review.with_user(w.ud).create(vals)
    entry.invalidate_recordset()
    assert rev.technician_id == w.ea and entry.review_state == "reviewed"
    assert refused(w.env, lambda: Review.with_user(w.ud).create(vals))
    assert refused(w.env, lambda: rev.with_user(w.ud).write({"decision": "escalated"}))


# ------------------------------------------------- page 8: tracking pause
def test_no_position_is_kept_during_a_pause(w):
    Loc = w.env["fix.technician.location"]
    Pause = w.env["fix.tracking.pause"]
    now = fields.Datetime.now()
    assert refused(
        w.env,
        lambda: Pause.with_user(w.ua).create(
            {"employee_id": w.eb.id, "reason": "break", "planned_end": now + timedelta(hours=1)}
        ),
    )
    assert refused(w.env, lambda: Pause.with_user(w.ua).create(
        {"employee_id": w.ea.id, "reason": "break", "started_at": now - timedelta(hours=2),
         "planned_end": now + timedelta(hours=1)}))  # fmt: skip
    assert refused(
        w.env,
        lambda: Pause.with_user(w.ua).create(
            {"employee_id": w.ea.id, "reason": "off_duty", "planned_end": now + timedelta(hours=20)}
        ),
    )
    pause = Pause.with_user(w.ua).create(
        {"employee_id": w.ea.id, "reason": "meal", "planned_end": now + timedelta(hours=1)}
    )
    assert pause.state == "active"
    assert refused(
        w.env,
        lambda: Pause.with_user(w.ud).create(
            {"employee_id": w.ea.id, "reason": "break", "planned_end": now + timedelta(minutes=30)}
        ),
    )
    assert Loc.record_ping(w.ea.id, *SITE) is False
    assert not Loc.search_count([("technician_id", "=", w.ea.id)])
    assert Loc.record_ping(w.eb.id, *SITE)  # someone else's tracking is untouched
    assert refused(w.env, lambda: pause.with_user(w.ub).action_end())
    pause.with_user(w.ua).action_end()
    pause.invalidate_recordset()
    assert pause.state == "ended" and Loc.record_ping(w.ea.id, *SITE)


def test_a_dispatcher_can_pause_a_technician(w):
    pause = w.env["fix.tracking.pause"].with_user(w.ud).create(
        {"employee_id": w.ea.id, "reason": "off_duty",
         "planned_end": fields.Datetime.now() + timedelta(hours=10)}
    )  # fmt: skip
    assert pause.state == "active" and pause.company_id


# --------------------------------------------------- page 9: failed visit
def _failed(w, user, fo, **kw):
    vals = {"field_order_id": fo.id, "exception_type": "customer_absent",
            "reason": "nobody answered for 15 minutes", "follow_up": "revisit",
            "evidence_photo": PNG_B64, "evidence_photo_name": "door.png",
            "latitude": SITE[0] + 0.001, "longitude": SITE[1]}  # fmt: skip
    vals.update(kw)
    return w.env["fix.field.visit.exception"].with_user(user).create(vals)


def test_a_failed_visit_needs_the_assigned_technician_and_site_evidence(w):
    fo = w.fo("en_route", tech=w.ea, latitude=SITE[0], longitude=SITE[1])
    assert refused(w.env, lambda: _failed(w, w.ub, fo))  # not their job
    assert refused(w.env, lambda: _failed(w, w.ud, fo))  # nobody files it for them
    assert "photo" in refused(w.env, lambda: _failed(w, w.ua, fo, evidence_photo=False))
    far = refused(w.env, lambda: _failed(w, w.ua, fo, latitude=SITE[0] + 0.05))
    assert far and "BRU-FSM-09" in far
    assert refused(w.env, lambda: _failed(w, w.ua, fo, latitude=0.0, longitude=0.0))
    assert fo.state == "en_route"
    rec = _failed(w, w.ua, fo)
    assert fo.state == "pending_dispatch" and not fo.technician_id and not fo.en_route_at
    assert rec.technician_id == w.ea and 50 < rec.distance_from_site_m < 200
    assert fo.failed_visit_count == 1
    assert _events(w.env, "visit.failed", rec.id) == 1
    assert refused(w.env, lambda: rec.with_user(w.ua).write({"follow_up": "workshop_transfer"}))


def test_only_a_visit_under_way_can_fail(w):
    assert refused(w.env, lambda: _failed(w, w.ua, w.fo("dispatched", tech=w.ea)))
    paid = w.fo("arrived", tech=w.ea, latitude=SITE[0], longitude=SITE[1])
    paid.write({"onsite_collection_amount": 900, "onsite_payment_method": "cash"})
    assert refused(w.env, lambda: _failed(w, w.ua, paid))


# ----------------------------------------------- page 11: field cash day
def _cash_job(w, tech, amount, handed=False):
    rec = w.fo("completed", tech=tech)
    vals = {"onsite_collection_amount": amount, "onsite_payment_method": "cash",
            "completed_at": fields.Datetime.now()}  # fmt: skip
    if handed:
        vals["cash_handed_over_at"] = fields.Datetime.now()
        shift = w.env["fix.cash.shift"].create(
            {"branch_id": w.branch.id, "operating_unit_id": w.ou.id, "company_id": w.co.id,
             "shift_type": "morning", "operator_id": w.ed.id, "opening_float": 0.0}
        )  # fmt: skip
        vals["cash_shift_id"] = shift.id
    rec.write(vals)  # setup only: the superuser places the job as completed
    return rec


def test_a_technicians_cash_day_is_measured_counted_and_confirmed_by_another(w):
    from odoo.addons.cd_field_service.models.fix_field_capture import _local_today

    _cash_job(w, w.ea, 900)
    _cash_job(w, w.ea, 600, handed=True)
    _cash_job(w, w.eb, 5000)  # another technician's cash is not counted
    Recon = w.env["fix.field.cash.recon"]
    assert refused(w.env, lambda: Recon.with_user(w.ua).create({"employee_id": w.eb.id}))
    rec = Recon.with_user(w.ua).create({"employee_id": w.ea.id, "counted_amount": 800})
    assert rec.recon_date == _local_today(w.env(user=w.ua.id))
    assert (rec.order_count, rec.cash_collected, rec.cash_handed_over, rec.cash_outstanding) == (
        2, 1500, 600, 900,
    )  # fmt: skip
    assert refused(w.env, lambda: rec.with_user(w.ua).write({"cash_outstanding": 800}))
    msg = refused(w.env, lambda: rec.with_user(w.ua).action_submit())
    assert msg and "BRU-FSM-07" in msg
    rec.with_user(w.ua).write({"variance_reason": "paid the van fuel, receipt attached"})
    rec.with_user(w.ua).action_submit()
    assert rec.state == "submitted" and rec.variance == -100
    assert refused(w.env, lambda: rec.with_user(w.ua).write({"counted_amount": 900}))
    assert refused(w.env, lambda: rec.with_user(w.ua).action_confirm())
    assert refused(w.env, lambda: rec.with_user(w.ub).action_confirm())  # not a dispatcher
    rec.with_user(w.ud).action_confirm()
    assert rec.state == "confirmed" and rec.confirmed_by_id == w.ud
    assert refused(w.env, lambda: Recon.with_user(w.ua).create({"employee_id": w.ea.id}))


def test_a_future_day_is_not_reconciled(w):
    from odoo.addons.cd_field_service.models.fix_field_capture import _local_today

    day = _local_today(w.env) + timedelta(days=1)
    assert refused(
        w.env,
        lambda: w.env["fix.field.cash.recon"]
        .with_user(w.ua)
        .create({"employee_id": w.ea.id, "recon_date": day}),
    )


def test_the_submitter_does_not_confirm(w):
    _cash_job(w, w.ea, 300)
    rec = (
        w.env["fix.field.cash.recon"]
        .with_user(w.ud)
        .create({"employee_id": w.ea.id, "counted_amount": 300})
    )
    rec.with_user(w.ud).action_submit()
    assert rec.variance == 0
    assert refused(w.env, lambda: rec.with_user(w.ud).action_confirm())
    assert rec.state == "submitted"
