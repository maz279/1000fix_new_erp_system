"""Behavioural tests for the P02 technician API beyond the security contract
(test_api_security.py): geofenced attendance, job-status transitions, diagnostics,
van stock, the formatting helpers and /technician/sync idempotency (DI-05).

Live ORM (``odoo_env``: fix_test, rolled back per test); ``request`` is replaced by
a minimal stand-in, the controller code runs unmodified.
"""

import json
from collections.abc import Mapping
from contextlib import contextmanager
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import Command, http
from odoo.addons.cd_service_order.controllers import technician_api as tapi
from odoo.addons.cd_service_order.controllers.technician_api import TechnicianApiController
from odoo.exceptions import ValidationError


class _Request:
    def __init__(self, env):
        self.env = env
        self.session = http.Session(http.get_default_session(), "test-sid", new=True)
        self.httprequest = SimpleNamespace(headers={})


@contextmanager
def _as(env, user):
    fake = _Request(env(user=user.id))
    with patch.object(tapi, "request", fake):
        yield fake


@contextmanager
def _without_model(env, model_name):
    """Make ``env.get(model_name)`` return None, as on a database without the
    module defining it (the soft dependencies of this controller)."""
    env_class = type(env)

    def get(self, key, default=None):
        return default if key == model_name else Mapping.get(self, key, default)

    with patch.object(env_class, "get", get):
        yield


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "TABENT", "legal_name": "Tech API Entity", "company_id": env.company.id}
    )
    zone = env["fix.zone"].create({"name": "Tab Zone", "code": "TABZ"})
    branch = env["fix.branch"].create(
        {
            "name": "Tech Branch",
            "code": "TABB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
            "zone_id": zone.id,
        }
    )
    brand = env["fix.brand"].create({"name": "TabBrand", "code": "TABBR"})
    device_model = env["fix.device.model"].create({"name": "TabPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "Tab Customer", "phone": "01811000000"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-TAB-1"}
    )
    so = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Water damage",
            "priority": "high",
        }
    )
    users = env["res.users"].with_context(no_reset_password=True)
    tech_user = users.create({"name": "Tab Tech", "login": "tab.tech@api.test"})
    other_user = users.create({"name": "Tab Other", "login": "tab.other@api.test"})
    tech = env["hr.employee"].create(
        {"name": "Tab Tech", "user_id": tech_user.id, "branch_id": branch.id}
    )
    other = env["hr.employee"].create({"name": "Tab Other", "user_id": other_user.id})
    wo = env["fix.work.order"].create(
        {"order_id": so.id, "technician_id": tech.id, "certification_waiver": True, "sequence": 1}
    )
    part = env["product.product"].create(
        {
            "name": "Tab Screen",
            "default_code": "PART-TAB-1",
            "barcode": "BC-TAB-1",
            "list_price": 1250.5,
        }
    )
    fence = env["fix.geofence"].create(
        {
            "name": "Tab fence",
            "zone_id": zone.id,
            "geometry_json": json.dumps({"lat": 23.8, "lng": 90.4, "radius_m": 500}),
        }
    )
    return SimpleNamespace(
        env=env,
        branch=branch,
        fence=fence,
        so=so,
        device=device,
        customer=customer,
        tech_user=tech_user,
        other_user=other_user,
        tech=tech,
        other=other,
        wo=wo,
        part=part,
        zone=zone,
    )


def _geofence(world, geometry, kind="circle", zone=None):
    return world.env["fix.geofence"].create(
        {
            "name": f"Tab fence {kind}",
            "geofence_type": kind,
            "zone_id": (zone or world.zone).id,
            "geometry_json": json.dumps(geometry),
        }
    )


# the centre of the world's own fence, with a good (10 m) GPS fix
DHAKA = {"geo_lat": 23.8, "geo_long": 90.4, "accuracy_m": 10}


def _so_to(so, state):
    """Walk a draft service order along the declared transitions to ``state``."""
    chain = ["intake", "diagnostic", "estimate_pending", "estimate_sent"]
    chain += ["awaiting_approval", "approved", "in_repair", "qc_pending", "qc_failed"]
    for nxt in chain[: chain.index(state) + 1]:
        so.state = nxt


# --- helpers -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (0, "0.00"),
        (999.999, "1,000.00"),  # rounded to "1000.00" first, then grouped
        (1234567.891, "12,34,567.89"),
        (100000, "1,00,000.00"),
        (-1234.5, "-1,234.50"),
        ("12.5", "12.50"),
        ("abc", "0.00"),
        (None, "0.00"),
    ],
)
def test_fmt_bdt_south_asian_grouping(amount, expected):
    assert tapi._fmt_bdt(amount) == expected


def test_haversine_and_polygon_helpers():
    assert tapi._haversine_distance_m(23.8, 90.4, 23.8, 90.4) == 0.0
    # 0.1 degree of latitude = 6,371,000 m x 0.1 x pi / 180 = 11,119.49 m
    assert round(tapi._haversine_distance_m(23.8, 90.4, 23.9, 90.4), 2) == 11119.49
    square = [(23.79, 90.40), (23.80, 90.40), (23.80, 90.41), (23.79, 90.41)]
    assert tapi._point_in_polygon(23.795, 90.405, square) is True
    assert tapi._point_in_polygon(23.785, 90.405, square) is False
    assert tapi._point_in_polygon(23.795, 90.415, square) is False


def test_payload_digest_is_sorted_key_sha256():
    import hashlib

    expected = hashlib.sha256(b'{"a": 1, "b": "x"}').hexdigest()
    assert tapi.payload_digest({"b": "x", "a": 1}) == expected


# --- profile & attendance --------------------------------------------------------------


def test_me_reports_shift_and_own_zone_geofence(world):
    other_zone = world.env["fix.zone"].create({"name": "Other Zone", "code": "TABZ2"})
    _geofence(world, {"lat": 22.35, "lng": 91.85, "radius_m": 500}, zone=other_zone)
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        off = ctrl.technician_me()["technician"]
        ctrl.attendance_clock_in(**DHAKA)
        on = ctrl.technician_me()["technician"]
    assert (off["active_shift"], off["status"], off["last_clock_in"]) == (False, "off_duty", None)
    assert off["geofence"] == {
        "id": world.fence.id,
        "name": "Tab fence",
        "type": "circle",
        "geometry": {"lat": 23.8, "lng": 90.4, "radius_m": 500},
    }
    assert off["user_id"] == world.tech_user.id
    assert (on["active_shift"], on["status"]) == (True, "on_duty")
    assert on["last_clock_in"]


def test_me_without_a_zone_geofence(world):
    world.fence.active = False
    with _as(world.env, world.tech_user):
        me = TechnicianApiController().technician_me()["technician"]
    assert me["geofence"] is None
    assert (me["id"], me["name"]) == (world.tech.id, "Tab Tech")
    world.fence.active = True
    world.branch.zone_id = False  # no zone: no fence is "the technician's"
    with _as(world.env, world.tech_user):
        assert TechnicianApiController().technician_me()["technician"]["geofence"] is None


def _record(world, res):
    return world.env["fix.attendance.record"].browse(res["attendance_id"])


def test_clock_in_inside_the_own_zone_fence(world):
    with _as(world.env, world.tech_user):
        inside = TechnicianApiController().attendance_clock_in(
            geo_lat=23.8001, geo_long=90.4, accuracy_m=12.5, device_ref="PHONE-7"
        )
    # 0.0001 degree of latitude = 11.12 m from the centre, radius 500 m
    assert (inside["clock_in"], inside["in_geofence"], inside["distance_m"]) == (True, True, 11.1)
    assert (inside["geofence_result"], inside["approval_state"]) == ("inside", "not_required")
    assert inside["message"] == "Clock-in successful (within geofence)"
    att = _record(world, inside)
    assert (att.source, att.device_ref, att.geo_lat, att.accuracy_m) == (
        "mobile",
        "PHONE-7",
        23.8001,
        12.5,
    )
    assert (att.geofence_result, att.approval_state, att.approval_reason) == (
        "inside",
        "not_required",
        False,
    )


def test_clock_in_outside_the_own_zone_fence_is_recorded_for_approval(world):
    """M55 AUT-WFM-02: an out-of-geofence clock-in is recorded and FLAGGED for
    approval (it used to be recorded with a warning only)."""
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().attendance_clock_in(
            geo_lat=23.9, geo_long=90.4, accuracy_m=5
        )
    # 0.1 degree of latitude from the centre = 11,119.49 m
    reason = "position outside the geofence of zone TABZ (11119.5 m away)"
    assert res["message"] == f"Clock-in recorded - pending supervisor approval: {reason}"
    assert (
        res["in_geofence"],
        res["distance_m"],
        res["geofence_result"],
        res["approval_state"],
    ) == (
        False,
        11119.5,
        "outside",
        "pending",
    )
    att = _record(world, res)
    assert (att.geofence_result, att.approval_state, att.approval_reason) == (
        "outside",
        "pending",
        reason,
    )


def test_inside_another_zones_fence_is_flagged(world):
    """Regression: the FIRST active geofence of the whole estate was tested, so a
    technician standing in any zone's fence clocked in unflagged."""
    other_zone = world.env["fix.zone"].create({"name": "Ctg Zone", "code": "TABCTG"})
    _geofence(world, {"lat": 22.35, "lng": 91.85, "radius_m": 500}, zone=other_zone)
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().attendance_clock_in(
            geo_lat=22.35, geo_long=91.85, accuracy_m=5
        )
    assert (res["geofence_result"], res["approval_state"]) == ("outside", "pending")
    assert "zone TABZ" in res["message"]


def test_no_zone_or_no_fence_is_recorded_for_approval(world):
    ctrl = TechnicianApiController()
    world.fence.active = False
    with _as(world.env, world.tech_user):
        no_fence = ctrl.attendance_clock_in(**DHAKA)
        ctrl.attendance_clock_out()
    assert (no_fence["geofence_result"], no_fence["approval_state"], no_fence["distance_m"]) == (
        "no_geofence",
        "pending",
        None,
    )
    assert no_fence["message"].endswith(
        "pending supervisor approval: zone TABZ has no active geofence"
    )
    world.branch.zone_id = False
    with _as(world.env, world.tech_user):
        no_zone = ctrl.attendance_clock_in(**DHAKA)
    assert (no_zone["geofence_result"], no_zone["approval_state"]) == ("no_zone", "pending")
    assert _record(world, no_zone).approval_reason == "the technician's branch has no dispatch zone"


def test_low_or_unreported_accuracy_is_flagged(world):
    """M55 T-06: a low-accuracy fix is flagged, not silently accepted - an
    unreported accuracy is not an acceptable one."""
    ctrl = TechnicianApiController()
    results = []
    with _as(world.env, world.tech_user):
        for accuracy in (150, None, "junk", 100):
            params: dict[str, object] = {"geo_lat": 23.8, "geo_long": 90.4}
            if accuracy is not None:
                params["accuracy_m"] = accuracy
            results.append(ctrl.attendance_clock_in(**params))
            ctrl.attendance_clock_out()
    coarse, missing, junk, at_limit = results
    assert (coarse["geofence_result"], coarse["approval_state"], coarse["in_geofence"]) == (
        "low_accuracy",
        "pending",
        True,
    )
    assert _record(world, coarse).approval_reason == "GPS accuracy 150 m, the limit is 100 m"
    for res in (missing, junk):
        assert (
            _record(world, res).approval_reason == "GPS accuracy not reported, the limit is 100 m"
        )
    assert at_limit["approval_state"] == "not_required"  # 100 m is within the 100 m default


def test_the_accuracy_limit_is_a_configuration_parameter(world):
    params = world.env["ir.config_parameter"].sudo()
    assert tapi.max_clock_in_accuracy_m(world.env) == tapi.DEFAULT_MAX_ACCURACY_M == 100.0
    params.set_param(tapi.ACCURACY_PARAM, "20")
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        res = ctrl.attendance_clock_in(geo_lat=23.8, geo_long=90.4, accuracy_m=30)
    assert _record(world, res).approval_reason == "GPS accuracy 30 m, the limit is 20 m"
    params.set_param(tapi.ACCURACY_PARAM, "twenty")  # unreadable: the documented default
    assert tapi.max_clock_in_accuracy_m(world.env) == 100.0


def test_any_fence_of_the_own_zone_admits(world):
    """A zone can have several fences (branch, depot): inside any one of them is in."""
    _geofence(
        world,
        {"points": [[22.30, 91.80], [22.40, 91.80], [22.40, 91.90], [22.30, 91.90]]},
        kind="polygon",
    )
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        inside = ctrl.attendance_clock_in(geo_lat=22.35, geo_long=91.85, accuracy_m=8)  # polygon
        ctrl.attendance_clock_out()
        outside = ctrl.attendance_clock_in(geo_lat=22.50, geo_long=91.80, accuracy_m=8)
    assert (inside["in_geofence"], inside["distance_m"], inside["approval_state"]) == (
        True,
        0.0,
        "not_required",
    )
    # nearest: polygon vertex (22.40, 91.80), 0.1 degree of latitude = 11,119.49 m
    assert (outside["approval_state"], outside["distance_m"]) == ("pending", 11119.5)


def test_an_unreadable_fence_is_skipped_never_trusted(world):
    env = world.env
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_geofence SET geometry_json = %s WHERE id = %s", ("{not json", world.fence.id)
    )
    env.invalidate_all()
    ctrl = TechnicianApiController()
    with _as(env, world.tech_user):
        flagged = ctrl.attendance_clock_in(**DHAKA)
        ctrl.attendance_clock_out()
    assert (flagged["geofence_result"], flagged["distance_m"]) == ("outside", None)
    assert _record(world, flagged).approval_reason == "position outside the geofence of zone TABZ"
    _geofence(world, {"lat": 23.8, "lng": 90.4, "radius_m": 100})
    with _as(env, world.tech_user):
        assert ctrl.attendance_clock_in(**DHAKA)["approval_state"] == "not_required"


def test_clock_in_validates_coordinates_and_the_attendance_lock(world):
    """Coordinates are required: they used to default to the Dhaka centre."""
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        bad = ctrl.attendance_clock_in(geo_lat="north", geo_long=90.4)
        missing = ctrl.attendance_clock_in()
        half = ctrl.attendance_clock_in(geo_lat=23.8)
    for res in (bad, missing, half):
        assert res["error"] == {
            "code": "invalid_coordinates",
            "message": "geo_lat and geo_long are required and numeric",
        }  # nothing to evaluate: refused, not recorded
    world.env["fix.attendance.lock"].create(
        {
            "name": "TAB-LOCK",
            "period_start": date.today() - timedelta(days=1),
            "period_end": date.today() + timedelta(days=1),
            "state": "locked",
        }
    )
    with _as(world.env, world.tech_user):
        locked = ctrl.attendance_clock_in(**DHAKA)
    assert locked == {
        "error": {
            "code": "attendance_locked",
            "message": "Attendance period TAB-LOCK is locked — mobile clock-in rejected",
        }
    }
    assert not world.env["fix.attendance.record"].search([("employee_id", "=", world.tech.id)])


def test_clock_out_closes_the_open_shift(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        ctrl.attendance_clock_in(**DHAKA)
        again_in = ctrl.attendance_clock_in(**DHAKA)
        out = ctrl.attendance_clock_out()
        again = ctrl.attendance_clock_out()
    att = world.env["fix.attendance.record"].browse(out["attendance_id"])
    assert (again_in["already_clocked_in"], again_in["attendance_id"]) == (True, att.id)
    assert again_in["approval_state"] == "not_required"
    assert out["clock_out"] is True and att.check_out
    assert out["worked_hours"] == round(att.worked_hours, 2)
    assert again["error"]["code"] == "no_open_shift"


# --- job status ------------------------------------------------------------------------


def test_job_status_requires_work_order_and_action(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        assert ctrl.job_status(action="start")["error"]["code"] == "missing_params"
        assert ctrl.job_status(work_order_id=world.wo.id)["error"]["code"] == "missing_params"


def test_start_does_not_walk_an_unapproved_service_order_into_repair(world):
    # A02 audit M01-2: starting a job used to walk a draft order through the
    # estimate and the customer's approval; only an approved order is repaired.
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().job_status(work_order_id=world.wo.id, action="start")
    assert res["work_order"]["state"] == "in_progress"
    assert res["work_order"]["service_order_state"] == "draft"
    assert world.wo.start_time


@pytest.mark.parametrize("so_state", ["approved", "qc_failed"])
def test_start_moves_the_service_order_into_repair(world, so_state):
    _so_to(world.so, so_state)
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().job_status(work_order_id=world.wo.id, action="start")
    assert res["work_order"]["service_order_state"] == "in_repair"


@pytest.mark.parametrize("so_state", ["in_repair", "qc_pending", "awaiting_approval"])
def test_start_leaves_a_service_order_already_past_approval(world, so_state):
    _so_to(world.so, so_state)
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().job_status(work_order_id=world.wo.id, action="start")
    assert res["work_order"]["state"] == "in_progress"
    assert res["work_order"]["service_order_state"] == so_state


def test_a_refused_service_order_transition_does_not_fail_the_job_start(world):
    so_class = type(world.so)
    with (
        patch.object(so_class, "_validate_transition", side_effect=ValidationError("frozen")),
        _as(world.env, world.tech_user),
    ):
        res = TechnicianApiController().job_status(work_order_id=world.wo.id, action="start")
    assert res["work_order"]["state"] == "in_progress"
    assert world.so.state == "draft"


def test_restart_keeps_the_original_start_time(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        ctrl.job_status(work_order_id=world.wo.id, action="start")
        first = world.wo.start_time
        ctrl.job_status(work_order_id=world.wo.id, action="pause")
        assert world.wo.state == "in_progress"  # pause acknowledges, changes nothing
        ctrl.job_status(work_order_id=world.wo.id, action="start")
    assert world.wo.start_time == first


def test_complete_submits_an_in_repair_order_to_qc(world):
    ctrl = TechnicianApiController()
    _so_to(world.so, "approved")  # A02 M01-2: start repairs an APPROVED order only
    with _as(world.env, world.tech_user):
        ctrl.job_status(work_order_id=world.wo.id, action="start")
        res = ctrl.job_status(work_order_id=world.wo.id, action="complete")
    assert (res["work_order"]["state"], res["work_order"]["service_order_state"]) == (
        "completed",
        "qc_pending",
    )
    assert world.wo.end_time


def test_complete_outside_repair_leaves_the_order_and_tolerates_a_refusal(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        res = ctrl.job_status(work_order_id=world.wo.id, action="complete")
    assert (res["work_order"]["state"], res["work_order"]["service_order_state"]) == (
        "completed",
        "draft",
    )
    _so_to(world.so, "in_repair")
    with (
        patch.object(type(world.so), "_validate_transition", side_effect=ValidationError("no")),
        _as(world.env, world.tech_user),
    ):
        res = ctrl.job_status(work_order_id=world.wo.id, action="complete")
    assert res["work_order"]["service_order_state"] == "in_repair"


def test_fail_marks_the_work_order_failed(world):
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().job_status(work_order_id=world.wo.id, action="fail")
    assert res["work_order"]["state"] == "failed"
    assert world.wo.end_time


# --- diagnostics -------------------------------------------------------------------------


def _tree(world):
    return world.env["fix.diagnostic.node"].create(
        {
            "name": "Boots?",
            "code": "TAB-D1",
            "children_ids": [
                Command.create(
                    {
                        "name": "No - battery",
                        "code": "TAB-D1A",
                        "fault_code": "F-BAT",
                        "recommended_action": "Replace battery",
                    }
                )
            ],
        }
    )


def test_diagnostic_tree_lists_roots_with_children(world):
    root = _tree(world)
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().diagnostics_tree()
    mine = [t for t in res["trees"] if t["id"] == root.id]
    assert mine == [
        {
            "id": root.id,
            "code": "TAB-D1",
            "name": "Boots?",
            "is_terminal": False,
            "children": [
                {
                    "id": root.children_ids.id,
                    "code": "TAB-D1A",
                    "name": "No - battery",
                    "is_terminal": True,
                    "fault_code": "F-BAT",
                    "recommended_action": "Replace battery",
                }
            ],
        }
    ]
    assert res["total"] == len(res["trees"])


def test_diagnostics_submit_paths(world):
    root = _tree(world)
    leaf = root.children_ids
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        missing = ctrl.diagnostics_submit(work_order_id=world.wo.id)
        by_node = ctrl.diagnostics_submit(
            work_order_id=world.wo.id, node_id=leaf.id, fault_code="X"
        )
        assert world.wo.notes is False  # no notes: nothing appended
        root_node = ctrl.diagnostics_submit(
            work_order_id=world.wo.id, node_id=root.id, fault_code="F-MANUAL", notes="checked"
        )
        unknown = ctrl.diagnostics_submit(
            work_order_id=world.wo.id, node_id=99999999, fault_code="F-U"
        )
        junk = ctrl.diagnostics_submit(work_order_id=world.wo.id, node_id="abc", fault_code="F-J")
    assert missing["error"]["code"] == "missing_params"
    # a terminal node carries its own fault code (the client's is ignored)
    assert by_node["diagnosis"]["diagnostic_tree_id"] == leaf.id
    assert by_node["diagnosis"]["diagnosed_fault_code"] == "F-BAT"
    # a node without a fault code falls back to the submitted one
    assert root_node["diagnosis"]["diagnostic_tree_id"] == root.id
    assert root_node["diagnosis"]["diagnosed_fault_code"] == "F-MANUAL"
    assert root_node["diagnosis"]["notes"] == "[Diagnosis]: checked"
    # an unknown or malformed node id records the fault code only
    assert (
        unknown["diagnosis"]["diagnostic_tree_id"],
        unknown["diagnosis"]["diagnosed_fault_code"],
    ) == (
        root.id,
        "F-U",
    )
    assert junk["diagnosis"]["diagnosed_fault_code"] == "F-J"


# --- van stock -----------------------------------------------------------------------------


def test_van_stock_catalogue_formats_prices(world):
    with _as(world.env, world.tech_user):
        res = TechnicianApiController().van_stock()
    item = next(i for i in res["van_stock"] if i["id"] == world.part.id)
    assert item == {
        "id": world.part.id,
        "default_code": "PART-TAB-1",
        "barcode": "BC-TAB-1",
        "name": "Tab Screen",
        "list_price_bdt": "1,250.50",
        "stock_qty": 5,
    }
    assert res["van_locations"] == []
    assert res["total"] == len(res["van_stock"])


def test_van_stock_without_the_inventory_module(world):
    with _without_model(world.env, "fix.stock.location"), _as(world.env, world.tech_user):
        res = TechnicianApiController().van_stock()
    assert res["van_locations"] == []
    assert world.part.id in {i["id"] for i in res["van_stock"]}


def test_van_stock_consume_by_product_id(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        missing = ctrl.van_stock_consume(work_order_id=world.wo.id)
        junk = ctrl.van_stock_consume(work_order_id=world.wo.id, product_id="abc")
        gone = ctrl.van_stock_consume(work_order_id=world.wo.id, product_id=99999999)
        ok = ctrl.van_stock_consume(work_order_id=world.wo.id, product_id=world.part.id, quantity=3)
    assert missing["error"]["code"] == "missing_params"
    assert junk["error"] == {"code": "no_product", "message": "Part 'abc' not found in catalogue"}
    assert gone["error"]["code"] == "no_product"
    # 3 x 1,250.50 = 3,751.50
    assert ok["consumed"]["quantity"] == 3.0
    assert (ok["consumed"]["unit_cost_bdt"], ok["consumed"]["line_total_bdt"]) == (
        "1,250.50",
        "3,751.50",
    )
    line = world.env["fix.work.order.part"].browse(ok["consumed"]["part_line_id"])
    assert (line.product_id, line.quantity, line.currency_id.name) == (world.part, 3.0, "BDT")


def test_van_stock_consume_by_barcode(world):
    with _as(world.env, world.tech_user):
        ok = TechnicianApiController().van_stock_consume(
            work_order_id=world.wo.id, barcode_or_code="BC-TAB-1"
        )
    assert (ok["consumed"]["product_code"], ok["consumed"]["quantity"]) == ("PART-TAB-1", 1.0)


def test_queue_carries_service_order_context(world):
    with _as(world.env, world.tech_user):
        TechnicianApiController().van_stock_consume(
            work_order_id=world.wo.id, product_id=world.part.id
        )
        res = TechnicianApiController().technician_queue()
    (row,) = res["queue"]
    assert row["service_order"] == {
        "id": world.so.id,
        "ref": world.so.name,
        "state": "draft",
        "priority": "high",
        "fault_description": "Water damage",
        "customer_name": "Tab Customer",
        "customer_phone": "01811000000",
        "device": "TabBrand TabPhone",
        "branch": "Tech Branch",
        "sla_deadline": "",
    }
    assert row["parts_consumed"][0]["unit_cost_bdt"] == "1,250.50"
    assert (row["diagnostic_tree_id"], row["diagnostic_tree_name"]) == (None, "")
    assert (res["technician_name"], res["total"]) == ("Tab Tech", 1)


# --- /technician/sync: batch handling and DI-05 idempotency -----------------------------------


def _sync(ctrl, commands, **extra):
    return ctrl.technician_sync(
        commands=commands, batch_checksum=tapi.batch_digest(commands), **extra
    )


def _cmd(cmd_id, operation, **payload):
    return {"command_id": cmd_id, "operation": operation, "payload": payload}


def _ledger(world, cmd_id=None):
    domain = [("technician_id", "in", (world.tech.id, world.other.id))]
    if cmd_id:
        domain.append(("command_id", "=", cmd_id))
    return world.env["fix.offline.idempotency.ledger"].search(domain)


def _counts(world):
    return (
        world.env["fix.attendance.record"].search_count([("employee_id", "=", world.tech.id)]),
        len(world.wo.parts_consumed_ids),
    )


def test_sync_skips_entries_without_a_command_id(world):
    commands = ["junk", {"operation": "clock_in"}, {"command_id": "", "operation": "clock_in"}]
    with _as(world.env, world.tech_user):
        res = _sync(TechnicianApiController(), commands)["sync"]
    assert (res["acknowledged"], res["rejected"], res["ack_count"]) == ({}, {}, 0)
    assert _counts(world) == (0, 0)


def test_resubmitted_batch_is_acknowledged_without_re_executing(world):
    """DI-05: the client lost the response of a successful sync and uploads again."""
    batch = [
        _cmd("u-in", "clock_in", geo_lat=23.8, geo_long=90.4),
        _cmd(
            "u-part",
            "consume_part",
            work_order_id=world.wo.id,
            product_id=world.part.id,
            quantity=2,
        ),
        _cmd("u-job", "job_status", work_order_id=world.wo.id, action="start"),
    ]
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_user):
        first = _sync(ctrl, batch, device_id="PHONE-9")["sync"]
        after_first = _counts(world)
        second = _sync(ctrl, batch, device_id="PHONE-9")["sync"]
    assert set(first["acknowledged"]) == {"u-in", "u-part", "u-job"}
    assert (first["duplicates"], first["dup_count"]) == ([], 0)
    assert after_first == (1, 1)
    # the replay creates nothing: still one attendance record and one part line
    assert _counts(world) == (1, 1)
    assert set(second["acknowledged"]) == {"u-in", "u-part", "u-job"}
    assert (second["duplicates"], second["dup_count"], second["ack_count"]) == (
        ["u-in", "u-part", "u-job"],
        3,
        3,
    )
    for cmd_id, original in first["acknowledged"].items():
        assert second["acknowledged"][cmd_id] == dict(original, status="already_applied")
    assert second["checksum"] == first["checksum"]
    entries = _ledger(world)
    assert sorted(entries.mapped("command_id")) == ["u-in", "u-job", "u-part"]
    part_entry = _ledger(world, "u-part")
    assert (part_entry.model, part_entry.record_id, part_entry.operation) == (
        "fix.work.order",
        world.wo.id,
        "consume_part",
    )
    assert (part_entry.device_id, part_entry.status) == ("PHONE-9", "applied")
    assert part_entry.payload_hash == tapi.payload_digest(batch[1]["payload"])
    assert _ledger(world, "u-in").model == "fix.attendance.record"


def test_batch_mixing_new_and_applied_commands_runs_only_the_new_ones(world):
    ctrl = TechnicianApiController()
    applied = _cmd("m-part-1", "consume_part", work_order_id=world.wo.id, product_id=world.part.id)
    with _as(world.env, world.tech_user):
        _sync(ctrl, [applied])
        mixed = _sync(
            ctrl,
            [
                applied,
                _cmd(
                    "m-part-2",
                    "consume_part",
                    work_order_id=world.wo.id,
                    barcode_or_code="PART-TAB-1",
                ),
            ],
        )["sync"]
    assert mixed["duplicates"] == ["m-part-1"]
    assert set(mixed["acknowledged"]) == {"m-part-1", "m-part-2"}
    assert "status" not in mixed["acknowledged"]["m-part-2"]  # executed now
    assert len(world.wo.parts_consumed_ids) == 2  # one per distinct command


def test_replayed_rejection_and_foreign_command_ids(world):
    ctrl = TechnicianApiController()
    foreign_wo = _cmd("r-1", "job_status", work_order_id=999999999, action="start")
    with _as(world.env, world.tech_user):
        first = _sync(ctrl, [foreign_wo])["sync"]
        again = _sync(ctrl, [foreign_wo])["sync"]
    assert first["rejected"] == {"r-1": "Work order not found or not assigned to you"}
    assert again["rejected"] == first["rejected"]
    assert (_ledger(world, "r-1").status, again["duplicates"]) == ("rejected", [])
    # the other technician re-using tech's command id executes nothing
    stolen = _cmd("r-1", "clock_in")
    with _as(world.env, world.other_user):
        res = _sync(ctrl, [stolen])["sync"]
    assert res["rejected"] == {"r-1": "command_id already used by another technician"}
    assert not world.env["fix.attendance.record"].search([("employee_id", "=", world.other.id)])


def test_tampered_replay_is_still_refused_as_a_whole(world):
    ctrl = TechnicianApiController()
    applied = _cmd("t-1", "clock_in", **DHAKA)
    with _as(world.env, world.tech_user):
        _sync(ctrl, [applied])
        tampered = [
            applied,
            _cmd("t-2", "consume_part", work_order_id=world.wo.id, product_id=world.part.id),
        ]
        res = ctrl.technician_sync(commands=tampered, batch_checksum=tapi.batch_digest([applied]))
    assert res["error"]["code"] == "checksum_mismatch"
    assert not world.wo.parts_consumed_ids
    assert not _ledger(world, "t-2")


def test_a_failing_command_is_rolled_back_and_recorded_rejected(world):
    ctrl = TechnicianApiController()
    commands = [
        _cmd("f-boom", "job_status", work_order_id=world.wo.id, action="start"),
        _cmd("f-ok", "clock_in", **DHAKA),
    ]
    with (
        patch.object(TechnicianApiController, "job_status", side_effect=RuntimeError("boom")),
        _as(world.env, world.tech_user),
    ):
        res = _sync(ctrl, commands)["sync"]
    assert res["rejected"] == {"f-boom": "boom"}
    assert set(res["acknowledged"]) == {"f-ok"}
    entry = _ledger(world, "f-boom")
    assert (entry.status, entry.conflict_reason) == ("rejected", "boom")
    assert json.loads(entry.response_payload) == {"error": "boom"}


def test_a_ledger_that_cannot_record_rejects_the_command_without_effect(world):
    ledger_class = type(world.env["fix.offline.idempotency.ledger"])
    commands = [_cmd("l-1", "clock_in", **DHAKA)]
    with (
        patch.object(ledger_class, "record_execution", side_effect=RuntimeError("ledger down")),
        _as(world.env, world.tech_user),
    ):
        res = _sync(TechnicianApiController(), commands)["sync"]
    assert res["rejected"] == {"l-1": "ledger down"}
    assert _counts(world) == (0, 0)  # the clock-in rolled back with its savepoint


def test_sync_fails_closed_without_the_ledger(world):
    commands = [_cmd("n-1", "clock_in")]
    with _without_model(world.env, tapi.LEDGER_MODEL), _as(world.env, world.tech_user):
        res = _sync(TechnicianApiController(), commands)
    assert res["error"]["code"] == "ledger_unavailable"
    assert _counts(world) == (0, 0)
