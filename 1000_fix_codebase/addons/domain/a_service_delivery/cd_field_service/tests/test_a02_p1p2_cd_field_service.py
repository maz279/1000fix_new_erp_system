"""A02 workflow audit, P1/P2 for M02 Field Service & Dispatch.

B2 (field.order.completed reaches M01; literal publish calls), the acceptance
timeout, parts linked to the field order, and the geofence arrival from the
technician app (with unreadable fences failing closed). Users and the world
come from the P0 fixture (test_a02_p0_m02.py); every user is NON-ADMIN and
`odoo_env` rolls everything back.
"""

import json
import pathlib
from datetime import timedelta

from odoo import fields

from . import test_a02_p0_m02 as p0

w = p0.w
refused, give_evidence, _fence = p0.refused, p0.give_evidence, p0._fence
_sync, _cmd = p0._sync, p0._cmd


def _product(w, code="A02-FS-PART"):
    return w.env["product.product"].create(
        {"name": "Field relay %s" % code, "default_code": code, "standard_price": 350.0}
    )


def _payloads(env, rec, event_type):
    rows = (
        env["fix.event.outbox"]
        .sudo()
        .search([("aggregate_id", "=", rec.id), ("event_type", "=", event_type)])
    )
    out = []
    for row in rows:
        data = json.loads(row.payload or "{}")
        out.append(data.get("payload", data) if isinstance(data, dict) else data)
    return out


# ------------------------------------------------ B2: the hand-back event
def test_completion_publishes_the_m01_hand_back(w):
    rec = w.fo("in_progress", w.ea)
    give_evidence(rec)
    rec.with_user(w.ua).action_complete()
    payloads = _payloads(w.env, rec, "field.order.completed")
    assert len(payloads) == 1
    assert (payloads[0]["service_order_id"], payloads[0]["field_order_id"]) == (w.order.id, rec.id)


def test_field_events_are_literal_publish_calls():
    """FF-48 reads publish("<type>", ...) literally: no private wrapper."""
    src = (pathlib.Path(p0.__file__).parents[1] / "models" / "fix_field_order.py").read_text(
        encoding="utf-8"
    )
    assert "def _emit_field_event" not in src and "._emit_field_event(" not in src
    for event in ("field.order.dispatched", "field.order.completed", "field.order.declined"):
        assert '"%s",' % event in src


# ------------------------------------------------ acceptance timeout (M02-4)
def test_the_acceptance_timeout_is_off_by_default_and_returns_to_dispatch(w):
    env = w.env
    stale = w.fo("dispatched", w.ea)
    stale.write({"dispatched_at": fields.Datetime.now() - timedelta(minutes=90)})
    fresh = w.fo("dispatched", w.eb)
    fresh.write({"dispatched_at": fields.Datetime.now() - timedelta(minutes=5)})
    accepted = w.fo("accepted", w.ea)
    accepted.write({"dispatched_at": fields.Datetime.now() - timedelta(minutes=90)})
    Order = env["fix.field.order"]
    assert Order._cron_return_unaccepted() == 0 and stale.state == "dispatched"
    env["ir.config_parameter"].sudo().set_param("cd_field_service.acceptance_timeout_minutes", "30")
    assert Order._cron_return_unaccepted() >= 1
    assert (stale.state, stale.technician_id, stale.dispatched_at) == (
        "pending_dispatch",
        env["hr.employee"],
        False,
    )
    assert stale.activity_ids  # a to-do for a dispatcher
    assert fresh.state == "dispatched" and accepted.state == "accepted"
    # the dispatcher re-dispatches it, as from any pending order
    stale.with_user(w.ud).action_dispatch(technician_id=w.eb.id)
    assert stale.state == "dispatched" and stale.technician_id == w.eb


def test_a_garbled_timeout_switch_stays_off(w):
    w.env["ir.config_parameter"].sudo().set_param(
        "cd_field_service.acceptance_timeout_minutes", "soon"
    )
    rec = w.fo("dispatched", w.ea)
    rec.write({"dispatched_at": fields.Datetime.now() - timedelta(days=2)})
    assert w.env["fix.field.order"]._cron_return_unaccepted() == 0
    assert rec.state == "dispatched"


# ------------------------------------------------ parts on the field order
def test_offline_consume_part_writes_to_the_field_order(w, monkeypatch):
    rec = w.fo("in_progress", w.ea)
    prod = _product(w)
    res = _sync(
        w,
        w.ua,
        [
            _cmd(
                "fs-p-1",
                rec,
                "consume_part",
                {"field_order_id": rec.id, "barcode": prod.default_code, "quantity": 2},
            )
        ],  # fmt: skip
        monkeypatch,
    )
    ack = res["acknowledged"]["fs-p-1"]
    line = w.env["fix.field.order.part"].browse(ack["part_line_id"])
    assert (line.field_order_id, line.state, line.quantity) == (rec, "consumed", 2.0)
    assert rec.parts_total == 700.0
    # technician B cannot record parts on A's order; nobody records off site
    other = _sync(w, w.ub, [_cmd("fs-p-2", rec, "consume_part", {"product_id": prod.id})], monkeypatch)  # fmt: skip
    assert "fs-p-2" in other["rejected"]
    travelling = w.fo("en_route", w.ea)
    early = _sync(w, w.ua, [_cmd("fs-p-3", travelling, "consume_part", {"product_id": prod.id})], monkeypatch)  # fmt: skip
    assert "fs-p-3" in early["rejected"] and not travelling.part_line_ids


def test_a_picked_part_must_be_fitted_or_returned_before_completion(w):
    rec = w.fo("in_progress", w.ea)
    give_evidence(rec)
    Part = w.env["fix.field.order.part"].with_user(w.ua)
    picked = Part.create({"field_order_id": rec.id, "product_id": _product(w).id})
    err = refused(w.env, lambda: rec.with_user(w.ua).action_complete())
    assert "neither fitted nor returned" in err and rec.state == "in_progress"
    # technician B cannot fit A's part; the line's state is not typed
    assert "assigned" in refused(w.env, lambda: picked.with_user(w.ub).action_consume())
    assert p0.GUARD in refused(w.env, lambda: picked.write({"state": "returned"}))
    assert "Say why" in refused(w.env, lambda: picked.action_return(""))
    picked.action_return("Wrong revision; customer unit is rev B")
    rec.with_user(w.ua).action_complete()
    assert rec.state == "completed"


def test_a_fitted_part_is_frozen(w):
    rec = w.fo("in_progress", w.ea)
    part = (
        w.env["fix.field.order.part"]
        .with_user(w.ua)
        .create({"field_order_id": rec.id, "product_id": _product(w).id})
    )
    part.action_consume()
    assert (part.state, part.consumed_by_id) == ("consumed", w.ua)
    assert "record of what" in refused(w.env, lambda: part.write({"quantity": 5.0}))
    assert "cannot be deleted" in refused(w.env, lambda: part.unlink())
    assert "already consumed" in refused(w.env, lambda: part.action_consume())


# ------------------------------------------------ geofence arrival from the app
def test_offline_arrival_needs_a_position_inside_the_fence(w, monkeypatch):
    rec = w.fo("en_route", w.ea, geofence_id=_fence(w).id)
    none = _sync(w, w.ua, [_cmd("fs-a-1", rec, "arrive", {})], monkeypatch)
    assert "position" in none["rejected"]["fs-a-1"] and rec.state == "en_route"
    out = _sync(w, w.ua, [_cmd("fs-a-2", rec, "arrive", {"lat": 23.9, "lng": 90.4})], monkeypatch)
    assert "outside the geofence" in out["rejected"]["fs-a-2"] and rec.state == "en_route"
    mock = _sync(
        w,
        w.ua,
        [_cmd("fs-a-3", rec, "arrive", {"lat": 23.8, "lng": 90.4, "is_mock_location": True})],
        monkeypatch,  # fmt: skip
    )
    assert "fs-a-3" in mock["rejected"] and rec.state == "en_route"
    other = _sync(w, w.ub, [_cmd("fs-a-4", rec, "arrive", {"lat": 23.8, "lng": 90.4})], monkeypatch)  # fmt: skip
    assert "fs-a-4" in other["rejected"]
    ok = _sync(w, w.ua, [_cmd("fs-a-5", rec, "arrive", {"position": "23.8004, 90.4"})], monkeypatch)
    assert ok["acknowledged"]["fs-a-5"]["state"] == "arrived"
    assert (rec.state, rec.arrival_latitude) == ("arrived", 23.8004)
    again = _sync(w, w.ua, [_cmd("fs-a-6", rec, "arrive", {"lat": 23.8, "lng": 90.4})], monkeypatch)
    assert "fs-a-6" in again["conflicts"]


def test_an_unreadable_fence_fails_closed_until_waived(w):
    fence = _fence(w)
    w.env.flush_all()
    w.env.cr.execute(
        "UPDATE fix_geofence SET geometry_json = %s WHERE id = %s", ("{broken", fence.id)
    )
    w.env.invalidate_all()
    rec = w.fo("en_route", w.ea, geofence_id=fence.id)
    err = refused(
        w.env, lambda: rec.with_user(w.ua).action_arrive(current_lat=23.8, current_lon=90.4)
    )
    assert "outside the geofence" in err and rec.state == "en_route"
    rec.with_user(w.ud).action_waive_geofence("Fence geometry is being redrawn")
    rec.with_user(w.ua).action_arrive(current_lat=23.8, current_lon=90.4)
    assert rec.state == "arrived"
