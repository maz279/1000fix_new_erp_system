"""Behavioural security tests for the P02 technician API (R01 re-audit 2026-10-22).

Runs against the live ORM (``odoo_env``: database fix_test, rolled back per test)
with ``odoo.http.request`` replaced by a minimal stand-in exposing ``env`` /
``session`` / ``update_env`` — the controller code itself runs unmodified.
"""

import hashlib
import json
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import api, http
from odoo.addons.base.models import ir_http
from odoo.addons.cd_service_order.controllers import technician_api as tapi
from odoo.addons.cd_service_order.controllers.technician_api import TechnicianApiController
from werkzeug.exceptions import Unauthorized

TECH_ROUTES = (
    "technician_me",
    "technician_queue",
    "attendance_clock_in",
    "attendance_clock_out",
    "job_status",
    "diagnostics_tree",
    "diagnostics_submit",
    "van_stock",
    "van_stock_consume",
    "technician_sync",
)


class _Request:
    """The slice of ``odoo.http.request`` the controllers and ir.http use."""

    def __init__(self, env, headers=None):
        self.env = env
        self.session = http.Session(http.get_default_session(), "test-sid", new=True)
        self.httprequest = SimpleNamespace(headers=headers or {})

    def update_env(self, user=None, context=None, su=None):
        self.env = self.env(user=user, context=context, su=su)


@contextmanager
def _as(env, user):
    """Run controller code as ``user`` (a res.users record)."""
    fake = _Request(env(user=user.id))
    with patch.object(tapi, "request", fake):
        yield fake


def _signed_sync(ctrl, commands, **extra):
    """/technician/sync with the SP-03 digest of ``commands`` attached."""
    return ctrl.technician_sync(
        commands=commands, batch_checksum=tapi.batch_digest(commands), **extra
    )


def _anonymous(env):
    """An environment without any user, as for a request with no session/API key."""
    return api.Environment(env.cr, None, env.context)


def _set_write_date(env, record, when):
    env.flush_all()  # pending ORM writes would otherwise re-stamp write_date
    env.cr.execute(
        f'UPDATE "{record._table}" SET write_date = %s WHERE id = %s',
        (when, record.id),
    )
    env.invalidate_all()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "SECENT", "legal_name": "Security Test Entity", "company_id": env.company.id}
    )
    zone = env["fix.zone"].create({"name": "Sec Zone", "code": "SECZ"})
    env["fix.geofence"].create(
        {
            "name": "Sec fence",
            "zone_id": zone.id,
            "geometry_json": '{"lat": 23.8, "lng": 90.4, "radius_m": 500}',
        }
    )
    branch = env["fix.branch"].create(
        {
            "name": "Sec Branch",
            "code": "SECB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
            "zone_id": zone.id,
        }
    )
    brand = env["fix.brand"].create({"name": "SecBrand", "code": "SECBR"})
    device_model = env["fix.device.model"].create({"name": "SecPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "Sec Customer", "phone": "01711000000"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-SEC-1"}
    )
    so = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Screen flicker",
        }
    )
    users = env["res.users"].with_context(no_reset_password=True)
    tech_a_user = users.create({"name": "Tech A", "login": "tech.a@sec.test"})
    tech_b_user = users.create({"name": "Tech B", "login": "tech.b@sec.test"})
    clerk_user = users.create({"name": "Clerk", "login": "clerk@sec.test"})
    tech_a = env["hr.employee"].create(
        {"name": "Tech A", "user_id": tech_a_user.id, "branch_id": branch.id}
    )
    tech_b = env["hr.employee"].create(
        {"name": "Tech B", "user_id": tech_b_user.id, "branch_id": branch.id}
    )
    wo_vals = {"order_id": so.id, "certification_waiver": True}
    wo_a = env["fix.work.order"].create(dict(wo_vals, technician_id=tech_a.id, sequence=10))
    wo_a2 = env["fix.work.order"].create(dict(wo_vals, technician_id=tech_a.id, sequence=20))
    wo_b = env["fix.work.order"].create(dict(wo_vals, technician_id=tech_b.id, sequence=30))
    part = env["product.product"].create(
        {"name": "Sec Part", "default_code": "PART-SEC-1", "list_price": 250.0}
    )
    return SimpleNamespace(
        env=env,
        so=so,
        tech_a_user=tech_a_user,
        tech_b_user=tech_b_user,
        clerk_user=clerk_user,
        public_user=env.ref("base.public_user"),
        tech_a=tech_a,
        tech_b=tech_b,
        wo_a=wo_a,
        wo_a2=wo_a2,
        wo_b=wo_b,
        part=part,
    )


def _attendance(env, employee):
    return env["fix.attendance.record"].search([("employee_id", "=", employee.id)])


# --- route declaration ---------------------------------------------------------


@pytest.mark.parametrize("name", TECH_ROUTES)
def test_route_requires_bearer_auth_and_sends_no_cors(name):
    routing = getattr(TechnicianApiController, name).original_routing
    assert routing["auth"] == "bearer"
    assert "cors" not in routing


# --- framework-level authentication (auth="bearer") ----------------------------


def test_bearer_refuses_anonymous_invalid_key_and_bare_cookie_session(world):
    env = world.env
    for fake in (
        _Request(_anonymous(env)),  # anonymous internet caller
        _Request(_anonymous(env), {"Authorization": "Bearer not-a-real-key"}),
        _Request(env(user=world.tech_a_user.id)),  # cookie session, no Sec-Fetch headers
    ):
        with patch.object(ir_http, "request", fake), pytest.raises(Unauthorized):
            env["ir.http"]._auth_method_bearer()


def test_bearer_api_key_authenticates_the_key_owner_as_technician(world):
    env = world.env
    key = env["res.users.apikeys"].with_user(world.tech_a_user).sudo()._generate(None, "p02", None)
    fake = _Request(_anonymous(env), {"Authorization": f"Bearer {key}"})
    with patch.object(ir_http, "request", fake):
        env["ir.http"]._auth_method_bearer()
    assert fake.env.uid == world.tech_a_user.id
    with patch.object(tapi, "request", fake):
        me = TechnicianApiController().technician_me()
    assert me["technician"]["id"] == world.tech_a.id


# --- technician resolution -----------------------------------------------------


def test_public_user_is_refused_by_every_route_and_nothing_is_written(world):
    ctrl = TechnicianApiController()
    calls = {
        "technician_me": {},
        "technician_queue": {},
        "attendance_clock_in": {},
        "attendance_clock_out": {},
        "job_status": {"work_order_id": world.wo_a.id, "action": "start"},
        "diagnostics_tree": {},
        "diagnostics_submit": {"work_order_id": world.wo_a.id, "fault_code": "F1"},
        "van_stock": {},
        "van_stock_consume": {"work_order_id": world.wo_a.id, "product_id": world.part.id},
        "technician_sync": {"commands": []},
    }
    assert set(calls) == set(TECH_ROUTES)
    with _as(world.env, world.public_user):
        for name, kwargs in calls.items():
            res = getattr(ctrl, name)(**kwargs)
            assert res["error"]["code"] == "unauthenticated", name
    assert world.wo_a.state == "pending"
    assert not world.wo_a.diagnosed_fault_code
    assert not world.wo_a.parts_consumed_ids
    assert not world.env["fix.attendance.record"].search([])


def test_user_without_employee_gets_no_employee_and_no_fallback(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.clerk_user):
        assert ctrl.technician_me()["error"]["code"] == "no_employee"
        assert ctrl.attendance_clock_in()["error"]["code"] == "no_employee"
        res = ctrl.job_status(work_order_id=world.wo_a.id, action="start")
        assert res["error"]["code"] == "no_employee"
    assert not world.env["fix.attendance.record"].search([])
    assert world.wo_a.state == "pending"


@pytest.mark.parametrize("param", ["employee_id", "technician_id"])
def test_impersonation_parameter_is_refused(world, param):
    ctrl = TechnicianApiController()
    other = {param: world.tech_b.id}
    with _as(world.env, world.tech_a_user):
        assert ctrl.technician_me(**other)["error"]["code"] == "forbidden"
        assert ctrl.technician_queue(**other)["error"]["code"] == "forbidden"
        assert ctrl.attendance_clock_in(**other)["error"]["code"] == "forbidden"
        res = ctrl.job_status(work_order_id=world.wo_b.id, action="start", **other)
        assert res["error"]["code"] == "forbidden"
        assert ctrl.technician_me(**{param: "not-an-id"})["error"]["code"] == "forbidden"
        # naming yourself is harmless
        mine = ctrl.technician_me(**{param: world.tech_a.id})
        assert mine["technician"]["id"] == world.tech_a.id
    assert not _attendance(world.env, world.tech_b)
    assert world.wo_b.state == "pending"


# --- per-endpoint scoping --------------------------------------------------------


def test_queue_lists_only_own_work_orders(world):
    with _as(world.env, world.tech_a_user):
        res = TechnicianApiController().technician_queue()
    assert res["technician_id"] == world.tech_a.id
    assert {row["id"] for row in res["queue"]} == {world.wo_a.id, world.wo_a2.id}


def test_clock_in_and_out_act_on_the_authenticated_technician_only(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        res = ctrl.attendance_clock_in(geo_lat=23.8, geo_long=90.4)
        assert res["clock_in"] is True
        assert ctrl.attendance_clock_in(geo_lat=23.8, geo_long=90.4)["already_clocked_in"] is True
    with _as(world.env, world.tech_b_user):
        assert ctrl.attendance_clock_out()["error"]["code"] == "no_open_shift"
    with _as(world.env, world.tech_a_user):
        assert ctrl.attendance_clock_out()["clock_out"] is True
    assert len(_attendance(world.env, world.tech_a)) == 1
    assert not _attendance(world.env, world.tech_b)


def test_job_status_only_on_own_work_order(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        res = ctrl.job_status(work_order_id=world.wo_b.id, action="start")
        assert res["error"]["code"] == "no_work_order"
        res = ctrl.job_status(work_order_id="abc", action="start")
        assert res["error"]["code"] == "no_work_order"
        res = ctrl.job_status(work_order_id=world.wo_a.id, action="jump")
        assert res["error"]["code"] == "invalid_action"
        ok = ctrl.job_status(work_order_id=world.wo_a.id, action="start")
    assert world.wo_b.state == "pending"
    assert not world.wo_b.start_time
    assert ok["work_order"]["state"] == "in_progress"
    assert world.wo_a.state == "in_progress"


def test_diagnostics_submit_only_on_own_work_order(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        res = ctrl.diagnostics_submit(work_order_id=world.wo_b.id, fault_code="F-X")
        assert res["error"]["code"] == "no_work_order"
        ok = ctrl.diagnostics_submit(work_order_id=world.wo_a.id, fault_code="F-OK", notes="n")
    assert not world.wo_b.diagnosed_fault_code
    assert ok["diagnosis"]["diagnosed_fault_code"] == "F-OK"
    assert "[Diagnosis]: n" in world.wo_a.notes


def test_diagnostics_tree_requires_a_technician(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        assert ctrl.diagnostics_tree()["total"] >= 0
    with _as(world.env, world.clerk_user):
        assert ctrl.diagnostics_tree()["error"]["code"] == "no_employee"


def test_van_stock_shows_only_own_van_location(world):
    env = world.env
    loc = env["fix.stock.location"]
    van_a = loc.create(
        {"name": "Van A", "code": "VANA", "location_type": "van", "technician_id": world.tech_a.id}
    )
    loc.create(
        {"name": "Van B", "code": "VANB", "location_type": "van", "technician_id": world.tech_b.id}
    )
    with _as(env, world.tech_a_user):
        res = TechnicianApiController().van_stock()
    assert [v["id"] for v in res["van_locations"]] == [van_a.id]
    assert world.part.id in {item["id"] for item in res["van_stock"]}


def test_van_stock_consume_scoped_to_own_work_order_and_validated(world):
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        foreign = ctrl.van_stock_consume(work_order_id=world.wo_b.id, product_id=world.part.id)
        assert foreign["error"]["code"] == "no_work_order"
        for qty in (-3, 0, "nan", "lots"):
            res = ctrl.van_stock_consume(
                work_order_id=world.wo_a.id, product_id=world.part.id, quantity=qty
            )
            assert res["error"]["code"] == "invalid_quantity", qty
        missing = ctrl.van_stock_consume(work_order_id=world.wo_a.id, barcode_or_code="NOPE")
        assert missing["error"]["code"] == "no_product"
        ok = ctrl.van_stock_consume(
            work_order_id=world.wo_a.id, barcode_or_code="PART-SEC-1", quantity=2
        )
    assert not world.wo_b.parts_consumed_ids
    assert ok["consumed"]["quantity"] == 2.0
    assert world.wo_a.parts_consumed_ids.product_id == world.part


# --- /technician/sync ------------------------------------------------------------


def test_sync_replays_commands_only_as_the_authenticated_technician(world):
    commands = [
        {
            "command_id": "c-own",
            "operation": "job_status",
            "payload": {"work_order_id": world.wo_a.id, "action": "start"},
        },
        {
            "command_id": "c-foreign",
            "operation": "job_status",
            "payload": {"work_order_id": world.wo_b.id, "action": "start"},
        },
        {
            "command_id": "c-impersonate",
            "operation": "clock_in",
            "payload": {"employee_id": world.tech_b.id},
        },
        {"command_id": "c-bad", "operation": "self_destruct", "payload": {}},
        {"command_id": "c-bad-payload", "operation": "clock_in", "payload": ["x"]},
    ]
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        res = _signed_sync(ctrl, commands)["sync"]
        refused = ctrl.technician_sync(commands="nope")
    assert set(res["acknowledged"]) == {"c-own"}
    assert set(res["rejected"]) == {"c-foreign", "c-impersonate", "c-bad", "c-bad-payload"}
    assert world.wo_a.state == "in_progress"
    assert world.wo_b.state == "pending"
    assert not _attendance(world.env, world.tech_b)
    assert refused["error"]["code"] == "invalid_batch"


def _attendance_and_state(world):
    return (len(_attendance(world.env, world.tech_a)), world.wo_a.state, world.wo_a2.state)


def test_sync_without_batch_checksum_executes_nothing(world):
    """SP-03 on /technician/sync: an unsigned batch is refused as a whole."""
    commands = [
        {"command_id": "c1", "operation": "clock_in", "payload": {}},
        {
            "command_id": "c2",
            "operation": "job_status",
            "payload": {"work_order_id": world.wo_a.id, "action": "start"},
        },
    ]
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        missing = ctrl.technician_sync(commands=commands)
        empty = ctrl.technician_sync(commands=commands, batch_checksum="")
    assert missing == {
        "error": {
            "code": "checksum_missing",
            "message": "batch_checksum is required (SP-03); no command in the batch was executed",
        }
    }
    assert empty["error"]["code"] == "checksum_missing"
    assert _attendance_and_state(world) == (0, "pending", "pending")


def test_sync_with_tampered_batch_executes_nothing(world):
    """A digest signed over one batch does not authorise a different batch."""
    signed = [
        {
            "command_id": "c1",
            "operation": "job_status",
            "payload": {"work_order_id": world.wo_a.id, "action": "start"},
        }
    ]
    tampered = [
        dict(signed[0]),
        {
            "command_id": "c-smuggled",
            "operation": "job_status",
            "payload": {"work_order_id": world.wo_a2.id, "action": "complete"},
        },
    ]
    ctrl = TechnicianApiController()
    with _as(world.env, world.tech_a_user):
        res = ctrl.technician_sync(commands=tampered, batch_checksum=tapi.batch_digest(signed))
        wrong_type = ctrl.technician_sync(commands=signed, batch_checksum=12345)
    assert res["error"]["code"] == "checksum_mismatch"
    assert "no command in the batch was executed" in res["error"]["message"]
    assert wrong_type["error"]["code"] == "checksum_mismatch"
    assert _attendance_and_state(world) == (0, "pending", "pending")


def test_sync_with_valid_checksum_is_case_insensitive_and_executes(world):
    commands = [
        {
            "command_id": "c1",
            "operation": "job_status",
            "payload": {"work_order_id": world.wo_a.id, "action": "start"},
        }
    ]
    digest = " " + tapi.batch_digest(commands).upper() + " "
    with _as(world.env, world.tech_a_user):
        res = TechnicianApiController().technician_sync(commands=commands, batch_checksum=digest)
    assert set(res["sync"]["acknowledged"]) == {"c1"}
    assert world.wo_a.state == "in_progress"


def test_sync_last_token_filters_deltas(world):
    env = world.env
    now = env.cr.now()
    _set_write_date(env, world.wo_a, now - timedelta(hours=2))
    _set_write_date(env, world.wo_a2, now - timedelta(minutes=10))
    cut_token = tapi.encode_sync_token(now - timedelta(hours=1))
    ctrl = TechnicianApiController()
    with _as(env, world.tech_a_user):
        delta = _signed_sync(ctrl, [], last_token=cut_token)["sync"]
        full = _signed_sync(ctrl, [], last_token="TOKEN-garbage")["sync"]
        none = _signed_sync(ctrl, [])["sync"]
    assert [d["record_id"] for d in delta["deltas"]] == [world.wo_a2.id]
    assert delta["full_resync"] is False
    assert [d["record_id"] for d in full["deltas"]] == [world.wo_a.id, world.wo_a2.id]
    assert full["full_resync"] is True
    assert none["full_resync"] is True
    # the other technician's work order is never part of the download
    assert world.wo_b.id not in {d["record_id"] for d in full["deltas"]}
    cut, last_id = tapi.parse_sync_token(delta["token"])
    assert last_id == 0
    assert cut == now - tapi.SYNC_CURSOR_OVERLAP


def test_collect_deltas_pages_with_a_keyset_cursor(world):
    env = world.env
    now = env.cr.now()
    stamp = now - timedelta(minutes=5)
    for wo in (world.wo_a, world.wo_a2):
        _set_write_date(env, wo, stamp)  # same write_date: the id breaks the tie
    model = env["fix.work.order"]
    domain = [("technician_id", "=", world.tech_a.id)]

    def ident(rec):
        return rec.id

    first, token, has_more, full = tapi.collect_deltas(model, domain, None, ident, 1)
    assert (first, has_more, full) == ([world.wo_a.id], True, True)
    assert tapi.parse_sync_token(token) == (stamp, world.wo_a.id)
    second, token, has_more, full = tapi.collect_deltas(model, domain, token, ident, 1)
    assert (second, has_more, full) == ([world.wo_a2.id], True, False)
    third, _token, has_more, _full = tapi.collect_deltas(model, domain, token, ident, 1)
    assert (third, has_more) == ([], False)
    # a token from the future cannot hide changes: full resync
    future = tapi.encode_sync_token(now + timedelta(days=1))
    rows, _token, _more, full = tapi.collect_deltas(model, domain, future, ident)
    assert full is True
    assert len(rows) == 2


@pytest.mark.parametrize(
    "token",
    [
        None,
        "",
        42,
        "TOKEN-",
        "TOKEN-2026-13-40T00:00:00.000000",
        "TOKEN-2026-10-22T08:00:00.000000~x",
        "TOKEN-2026-10-22T08:00:00.000000~-1",
        "SOMETHING-2026-10-22T08:00:00.000000",
    ],
)
def test_malformed_sync_tokens_mean_full_resync(token):
    assert tapi.parse_sync_token(token) is None


def test_batch_digest_is_the_documented_canonical_sha256():
    commands = [{"payload": {"b": 2, "a": "জ"}, "command_id": "c1", "operation": "clock_in"}]
    canonical = '[{"command_id":"c1","operation":"clock_in","payload":{"a":"জ","b":2}}]'
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert tapi.batch_digest(commands) == expected
    reordered = json.loads(json.dumps(commands[0], sort_keys=True))
    assert tapi.batch_digest([reordered]) == expected
    assert tapi.verify_batch_checksum(commands, expected) is None
    assert tapi.verify_batch_checksum(commands, expected.upper()) is None
    assert tapi.verify_batch_checksum(commands, None)["error"]["code"] == "checksum_missing"
    mismatch = tapi.verify_batch_checksum(commands, "0" * 64)
    assert mismatch["error"]["code"] == "checksum_mismatch"
    assert tapi.verify_batch_checksum(commands, 123)["error"]["code"] == "checksum_mismatch"
