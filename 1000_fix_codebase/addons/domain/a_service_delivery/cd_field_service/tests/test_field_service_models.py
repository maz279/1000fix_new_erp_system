"""Behavioural tests for the cd_field_service models on the live ORM
(``odoo_env``: fix_test, rolled back after every test)."""

import json
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.addons.cd_competency.tests.certify import certify_for_dispatch, licence_for_driving
from odoo.exceptions import UserError
from psycopg2 import IntegrityError


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def fs(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "FSMENT", "legal_name": "FS Model Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "FS Branch", "code": "FSMB", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "FsModelBrand", "code": "FSMBR"})
    device_model = env["fix.device.model"].create({"name": "FsFridge", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "FS Customer"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-FSM-1"}
    )
    so = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Not cooling",
            "service_type": "onsite",
        }
    )
    zone = env["fix.zone"].create({"name": "FS Zone", "code": "FSMZ"})
    tech = env["hr.employee"].create({"name": "FS Tech"})
    tech2 = env["hr.employee"].create({"name": "FS Tech Two"})
    # A09 C4: dispatch needs a device-scoped certification
    for technician in (tech, tech2):
        certify_for_dispatch(env, technician)
        licence_for_driving(env, technician)  # dispatch by van checks it
    return SimpleNamespace(env=env, ou=ou, so=so, zone=zone, tech=tech, tech2=tech2)


PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="
)


def _give_completion_evidence(fo):
    """A02 audit M02-2: completion needs the customer's signature, a post-work
    photo and a work summary (the order must be in progress)."""
    import base64

    Att = fo.env["ir.attachment"]
    for media in ("signature", "photo"):
        att = Att.create(
            {
                "name": "%s.png" % media,
                "raw": base64.b64decode(PNG_B64),
                "mimetype": "image/png",
                "res_model": "fix.field.order",
                "res_id": fo.id,
            }
        )
        fo._fix_attach_field_evidence(att, media, signer="Test Customer")
    fo.work_summary = "Replaced the faulty part and tested."


def _order(fs, **vals):
    return fs.env["fix.field.order"].create(
        {"order_id": fs.so.id, "zone_id": fs.zone.id, "operating_unit_id": fs.ou.id, **vals}
    )


def _events(env, aggregate, rec_id):
    return env["fix.event.outbox"].search(
        [("aggregate", "=", aggregate), ("aggregate_id", "=", rec_id)], order="id asc"
    )


def _fence(fs, geometry, kind="circle"):
    return fs.env["fix.geofence"].create(
        {
            "name": "FS fence",
            "geofence_type": kind,
            "zone_id": fs.zone.id,
            "geometry_json": json.dumps(geometry),
        }
    )


# --- fix.field.order --------------------------------------------------------------


def test_order_reference_comes_from_the_sequence(fs):
    order = _order(fs)
    year = fields.Date.today().year
    assert order.name.startswith(f"FO/{year}/")
    assert order.name_bn == order.name
    named = _order(fs, name="FO-MANUAL-1", name_bn="এফও-১")
    assert (named.name, named.name_bn) == ("FO-MANUAL-1", "এফও-১")


def test_lifecycle_emits_dispatch_accept_events(fs):
    """Regression: events went through ``env.get("fix.event.outbox")`` - an empty,
    falsy recordset - so no field-order event was ever emitted."""
    env = fs.env
    van = env["fix.stock.location"].create(
        {"name": "FS Van", "code": "FSVAN1", "location_type": "van", "technician_id": fs.tech.id}
    )
    order = _order(fs, scheduled_start=fields.Datetime.to_datetime("2026-10-23 09:30:00"))
    order.action_request_dispatch()
    assert order.state == "pending_dispatch"
    order.action_dispatch(technician_id=fs.tech.id)
    assert (order.state, order.technician_id, order.van_location_id) == ("dispatched", fs.tech, van)
    order.action_accept()
    order.action_start_travel()
    # A02 ERP audit M02-F3: the arrival is tested against the zone's fence
    _fence(fs, {"lat": 23.8, "lng": 90.4, "radius_m": 500})
    order.action_arrive(current_lat=23.8, current_lon=90.4)
    order.action_start_work()
    _give_completion_evidence(order)
    order.action_complete()
    assert order.state == "completed"
    # A02 audit B2: completion now also publishes the M01 hand-back
    # A02 ERP review: starting travel tells the customer (AUT-FSM-04)
    dispatched, accepted, en_route, completed = _events(env, "fix.field.order", order.id)
    assert (
        dispatched.event_type,
        accepted.event_type,
        en_route.event_type,
        completed.event_type,
    ) == (
        "field.order.dispatched",
        "field.order.accepted",
        "field.order.en_route",
        "field.order.completed",
    )
    assert json.loads(dispatched.payload) == {
        "field_order_id": order.id,
        "order_ref": order.name,
        "service_order_ref": fs.so.name,
        "technician_id": fs.tech.id,
        "technician_name": "FS Tech",
        "zone_id": fs.zone.id,
        "scheduled_start": "2026-10-23T09:30:00",
    }
    assert json.loads(accepted.payload)["technician_id"] == fs.tech.id


def test_transition_guards(fs):
    env = fs.env
    order = _order(fs)
    with _refused(env, UserError, "A technician must be assigned"):
        order.action_dispatch()
    for action, message in (
        (order.action_accept, "Only dispatched orders can be accepted"),
        (order.action_decline, "Only dispatched orders can be declined"),
        (order.action_start_travel, "must accept the order before starting travel"),
        (order.action_arrive, "must be en route"),
        (order.action_start_work, "must arrive on site"),
        (order.action_complete, "Only in-progress orders"),
    ):
        with _refused(env, UserError, message):
            action()
    order.action_dispatch(technician_id=fs.tech.id)  # no van: van_location_id stays empty
    assert not order.van_location_id
    with _refused(env, UserError, "Only draft field orders"):
        order.action_request_dispatch()
    order.action_accept()
    with _refused(env, UserError, "Cannot dispatch order in state 'accepted'"):
        order.action_dispatch()


def test_decline_logs_the_technician_and_frees_the_order(fs):
    env = fs.env
    order = _order(fs)
    order.action_dispatch(technician_id=fs.tech.id)
    order.action_decline(reason="distance", notes="Outside my area")
    assert (order.state, order.technician_id, order.decline_reason) == (
        "declined",
        fs.tech.browse(),
        "distance",
    )
    log = env["fix.field.decline.log"].search([("field_order_id", "=", order.id)])
    assert (log.technician_id, log.reason, log.notes) == (fs.tech, "distance", "Outside my area")
    assert log.name.startswith("DEC/") and log.name_bn == log.name
    event = _events(env, "fix.field.order", order.id)[-1]
    assert event.event_type == "field.order.declined"
    assert json.loads(event.payload)["declined_technician_id"] == fs.tech.id
    # a declined order is re-dispatched to someone else
    order.action_dispatch(technician_id=fs.tech2.id)
    assert (order.state, order.technician_id) == ("dispatched", fs.tech2)


def test_decline_without_a_technician_is_refused_cleanly(fs):
    """Regression: the decline log's NOT NULL technician made the decline crash
    after the order had already been written."""
    order = _order(fs, state="dispatched")
    with _refused(fs.env, UserError, "dispatched to a technician"):
        order.action_decline()
    assert order.state == "dispatched"
    assert not fs.env["fix.field.decline.log"].search([("field_order_id", "=", order.id)])


def test_arrival_outside_the_geofence_is_refused(fs):
    """A02 audit M02-8: an arrival outside the fence, or with no position on a
    geofenced order, is refused (it was accepted with only an event)."""
    env = fs.env
    fence = _fence(fs, {"lat": 23.8, "lng": 90.4, "radius_m": 500})
    inside, outside, unchecked = (
        _order(fs, geofence_id=fence.id, state="en_route") for _ in range(3)
    )
    inside.action_arrive(current_lat=23.8001, current_lon=90.4)
    with _refused(env, UserError, "outside the geofence"):
        outside.action_arrive(current_lat=23.9, current_lon=90.4)
    with _refused(env, UserError, "needs your current position"):
        unchecked.action_arrive(current_lat=23.9)  # no longitude
    assert (inside.state, outside.state, unchecked.state) == ("arrived", "en_route", "en_route")
    assert (inside.arrival_latitude, inside.arrival_longitude) == (23.8001, 90.4)
    assert not _events(env, "fix.field.order", inside.id)


def test_geofence_checks_circle_polygon_and_degenerate_geometry(fs):
    env = fs.env
    order = _order(fs)
    assert order._check_geofence_arrival(1.0, 1.0) is True  # no geofence: nothing to check
    square = _fence(
        fs, {"points": [[23.79, 90.40], [23.80, 90.40], [23.80, 90.41], [23.79, 90.41]]}, "polygon"
    )
    order.geofence_id = square
    assert order._check_geofence_arrival(23.795, 90.405) is True
    assert order._check_geofence_arrival(23.785, 90.405) is False
    env.flush_all()
    for raw in ("{broken", json.dumps({"points": [[23.79, 90.40], [23.8, 90.4]]})):
        # rows predating the geometry constraint (written around the ORM)
        env.cr.execute("UPDATE fix_geofence SET geometry_json = %s WHERE id = %s", (raw, square.id))
        env.invalidate_all()
        # A02 audit M02-8 (P2): unreadable geometry fails closed
        assert order._check_geofence_arrival(0.0, 0.0) is False


def test_cancel_records_the_reason_but_never_a_completed_order(fs):
    order = _order(fs, notes="Gate code 1234")
    order.action_cancel(reason="Customer not home")
    assert (order.state, order.notes) == (
        "cancelled",
        "Gate code 1234\nCancellation: Customer not home",
    )
    quiet = _order(fs)
    with _refused(fs.env, UserError, "reason for the cancellation"):
        quiet.action_cancel()  # A02 audit M02-9: a reason is required
    assert quiet.state == "draft"
    done = _order(fs, state="completed")
    with _refused(fs.env, UserError, "Completed orders cannot be cancelled"):
        done.action_cancel()


def test_haversine_distance():
    from odoo.addons.cd_field_service.models.fix_field_order import FixFieldOrder

    # 0.1 degree of latitude = 6,371,000 m x 0.1 x pi / 180 = 11,119.49 m
    assert round(FixFieldOrder._haversine_distance(23.8, 90.4, 23.9, 90.4), 2) == 11119.49


# --- fix.field.route ------------------------------------------------------------------


def test_route_optimisation_and_lifecycle(fs):
    env = fs.env
    route_model = env["fix.field.route"]
    # A02 ERP audit M02-F11: the route starts from its own depot (Tejgaon here)
    route = route_model.create(
        {
            "technician_id": fs.tech.id,
            "operating_unit_id": fs.ou.id,
            "depot_latitude": 23.7776,
            "depot_longitude": 90.3959,
        }
    )
    assert route.name.startswith("RO/") and route.name_bn == route.name
    assert (route.order_count, route.improvement_pct) == (0, 0.0)
    with _refused(env, UserError, "at least 2 field orders"):
        route.action_optimize_route()
    route.field_order_ids = _order(fs) | _order(fs) | _order(fs)
    with _refused(env, UserError, "lack GPS coordinates"):
        route.action_optimize_route()
    # Honest optimiser (R01 re-audit): real coordinates, haversine/OSRM matrix,
    # nearest-neighbour + 2-opt. Improvement is measured, never a constant.
    coords = [(23.760, 90.390), (23.860, 90.400), (23.760, 90.400), (23.850, 90.380)]
    route.field_order_ids = env["fix.field.order"].browse(
        [_order(fs, latitude=la, longitude=lo).id for la, lo in coords]
    )
    route.action_optimize_route()
    assert route.order_count == 4
    assert route.route_state == "optimized"
    assert route.total_distance_km > 0
    assert route.baseline_duration_hours >= route.total_duration_hours
    assert route.improvement_pct > 0, "2-opt must beat the crossing baseline layout"
    assert "engine:" in route.message_ids[0].body
    with _refused(env, UserError, "Only in-progress routes"):
        route.action_complete_route()
    route.action_start_route()
    with _refused(env, UserError, "drafted or optimized before starting"):
        route.action_start_route()
    route.action_complete_route()
    assert route.route_state == "completed"
    named = route_model.create(
        {
            "technician_id": fs.tech.id,
            "operating_unit_id": fs.ou.id,
            "name": "RO-X",
            "name_bn": "আরও",
        }
    )
    assert (named.name, named.name_bn) == ("RO-X", "আরও")


def test_decline_log_keeps_an_explicit_reference(fs):
    order = _order(fs)
    log = fs.env["fix.field.decline.log"].create(
        {
            "field_order_id": order.id,
            "technician_id": fs.tech.id,
            "operating_unit_id": fs.ou.id,
            "reason": "capacity",
            "name": "DEC-MANUAL",
            "name_bn": "ডিইসি",
        }
    )
    assert (log.name, log.name_bn) == ("DEC-MANUAL", "ডিইসি")


# --- fix.offline.idempotency.ledger ----------------------------------------------------


def test_ledger_cached_results(fs):
    ledger = fs.env["fix.offline.idempotency.ledger"]
    assert ledger.get_cached_result("fsm-none") is None
    ledger.record_execution(
        "fsm-1",
        fs.tech.id,
        "DEV-1",
        "fix.field.order",
        None,
        "start_order",
        "h",
        "applied",
        {"a": 1},
    )
    cached = ledger.get_cached_result("fsm-1")
    assert (cached["status"], cached["response"], cached["idempotent_replay"]) == (
        "applied",
        {"a": 1},
        True,
    )
    assert ledger.search([("command_id", "=", "fsm-1")]).record_id == 0
    raw = ledger.create(
        {"command_id": "fsm-2", "model": "m", "operation": "op", "response_payload": "not json"}
    )
    assert ledger.get_cached_result("fsm-2")["response"] == {"raw": "not json"}
    raw.response_payload = False
    assert ledger.get_cached_result("fsm-2")["response"] == {}


def test_ledger_command_id_is_unique_in_the_database(fs):
    """Regression: the legacy ``_sql_constraints`` list is ignored by Odoo 19, so
    the DI-05 uniqueness was never created."""
    ledger = fs.env["fix.offline.idempotency.ledger"]
    ledger.create({"command_id": "fsm-dup", "model": "m", "operation": "op"})
    with _refused(fs.env, IntegrityError, "fix_offline_idempotency_ledger_command_id_uniq"):
        ledger.create({"command_id": "fsm-dup", "model": "m", "operation": "op"})


# --- fix.technician.location ------------------------------------------------------------


def test_location_pings_are_throttled_per_nfr_056(fs):
    env = fs.env
    loc = env["fix.technician.location"]
    assert loc.record_ping(99999999, 23.8, 90.4) is False
    first = loc.record_ping(fs.tech.id, 23.75, 90.38, speed=12.5, battery=80)
    assert first.name.startswith("LOC/") and first.name_bn == first.name
    assert (first.is_throttled, first.operating_unit_id, first.company_id) == (
        False,
        fs.ou,
        env.company,
    )
    event = _events(env, "fix.technician.location", first.id)
    assert event.event_type == "technician.location.ping"  # regression: was never emitted
    payload = json.loads(event.payload)
    assert (payload["technician_id"], payload["speed_kmh"], payload["battery_pct"]) == (
        fs.tech.id,
        12.5,
        80,
    )
    # 5 s later, ~7 m away: throttled, no event
    near = loc.record_ping(fs.tech.id, 23.75005, 90.38005)
    assert near.is_throttled is True
    assert not _events(env, "fix.technician.location", near.id)
    # far away: not throttled even inside 30 s
    far = loc.record_ping(fs.tech.id, 23.80, 90.38)
    assert far.is_throttled is False
    # more than 30 s later at the same spot: not throttled
    env["fix.technician.location"].browse(far.id).timestamp = fields.Datetime.now() - timedelta(
        seconds=31
    )
    assert loc.record_ping(fs.tech.id, 23.80, 90.38).is_throttled is False


def test_location_ping_uses_the_technicians_operating_unit(fs):
    env = fs.env
    own_ou = env["operating.unit"].create(
        {"name": "FS OU Two", "code": "FSOU2", "partner_id": env.company.partner_id.id}
    )
    fs.tech.operating_unit_id = own_ou
    ping = env["fix.technician.location"].record_ping(fs.tech.id, 23.75, 90.38)
    assert ping.operating_unit_id == own_ou


def test_location_reference_can_be_given(fs):
    ping = fs.env["fix.technician.location"].create(
        {
            "technician_id": fs.tech.id,
            "operating_unit_id": fs.ou.id,
            "latitude": 1.0,
            "longitude": 2.0,
            "name": "LOC-X",
            "name_bn": "লোক",
        }
    )
    assert (ping.name, ping.name_bn) == ("LOC-X", "লোক")
