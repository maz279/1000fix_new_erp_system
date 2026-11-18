# Behavioural tests for the P03 Service Order API (cd_p03_portal) on the live
# ORM: the module-level `request` is patched with a minimal stand-in exposing
# the rolled-back `odoo_env`, and the route methods are called directly.
import itertools
import json
from datetime import datetime, time, timedelta
from types import SimpleNamespace
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_service_order_api as api
from odoo.exceptions import AccessError

_SEQ = itertools.count(1)
DHAKA = ZoneInfo("Asia/Dhaka")


class FakeRequest:
    def __init__(self, env):
        self.env = env


class EnvView:
    """The real environment with some models reported as NOT installed."""

    def __init__(self, env, hidden):
        self._env = env
        self._hidden = set(hidden)

    def __contains__(self, model):
        return model not in self._hidden and model in self._env

    def __getitem__(self, model):
        return self._env[model]

    def __getattr__(self, name):
        return getattr(self._env, name)


def _controller(env):
    patcher = mock.patch.object(api, "request", FakeRequest(env))
    patcher.start()
    return patcher, api.P03ServiceOrderApiController()


@pytest.fixture
def ctrl(odoo_env):
    patcher, controller = _controller(odoo_env)
    yield controller
    patcher.stop()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    company = env.company
    entity = env["fix.entity"].search([("company_id", "=", company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "P03W", "legal_name": "P03 World Ltd", "company_id": company.id})
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)

    def branch(code, name, **vals):
        return env["fix.branch"].create(
            {"code": code, "name": name, "entity_id": entity.id, "operating_unit_id": ou.id, **vals}
        )

    w = SimpleNamespace(env=env)
    w.khulna = branch("KHL", "Khulna Hub", phone="041-555")
    w.gulshan = branch("GUL", "Gulshan Centre")
    w.partner = env["res.partner"].create({"name": "Nusrat Jahan", "phone": "01710000001"})
    w.brand = env["fix.brand"].create({"name": "Probeworks", "code": "PRBW"})
    w.model = env["fix.device.model"].create(
        {"brand_id": w.brand.id, "name": "PW-15", "device_type": "laptop"}
    )
    w.device = _device(w, "SN-P03-0001")
    w.tech = env["hr.employee"].create(
        {"name": "Probe Technician Alam", "job_title": "Field Technician"}
    )
    return w


def _device(w, serial=None):
    return w.env["fix.device"].create(
        {
            "serial_number": serial or f"SN-P03-AUTO-{next(_SEQ):04d}",
            "device_model_id": w.model.id,
            "owner_id": w.partner.id,
        }
    )


def _order(w, state="intake", branch=None, device=None, **vals):
    return w.env["fix.service.order"].create(
        {
            "customer_id": w.partner.id,
            "branch_id": (branch or w.khulna).id,
            "device_id": (device or _device(w)).id,
            "fault_description": vals.pop("fault_description", "No power"),
            "state": state,
            **vals,
        }
    )


def _estimate(w, order, lines, state="draft", version=1, **vals):
    return w.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "version": version,
            "state": state,
            "line_ids": [
                (0, 0, {"description": d, "line_type": t, "quantity": 1, "unit_price": p})
                for d, t, p in lines
            ],
            **vals,
        }
    )


def _set_dates(env, model, rec, **dates):
    env.flush_all()
    table = env[model]._table
    for column, value in dates.items():
        env.cr.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", [value, rec.id])
    env.invalidate_all()


def _local_midnight_utc(day):
    return (
        datetime.combine(day, time.min, tzinfo=DHAKA)
        .astimezone(ZoneInfo("UTC"))
        .replace(tzinfo=None)
    )


def _messages(order):
    return order.message_ids.mapped("body")


# --- /p03/stats ----------------------------------------------------------------------------


def test_stats_aggregates_live_orders_estimates_qc_and_worklist(ctrl, world):
    env = world.env
    QC = env["fix.qc.checklist"]
    qc_passed_before = QC.search_count([("state", "=", "passed")])
    qc_total_before = QC.search_count([])
    before = ctrl.stats()

    past = fields.Datetime.now() - timedelta(hours=2)
    _order(world, "intake", sla_resolution_deadline=past)  # intake: never "at risk"
    at_risk = _order(world, "diagnostic", sla_resolution_deadline=past)
    _order(world, "diagnostic", sla_resolution_deadline=fields.Datetime.now() + timedelta(days=1))
    _order(world, "delivered")
    _order(world, "awaiting_approval", service_type="onsite")
    _order(world, "closed")
    est = _estimate(
        world,
        at_risk,
        [("Screen", "part", 4000.0), ("Fitting", "labour", 1000.0)],
        state="approved",
        approved_at=fields.Datetime.now(),
    )
    QC.create({"order_id": at_risk.id, "state": "passed"})
    QC.create({"order_id": at_risk.id, "state": "failed"})
    env["fix.work.order"].create({"order_id": at_risk.id})  # pending, no technician
    activity = env["mail.activity"].create(
        {
            "res_model_id": env["ir.model"]._get_id("fix.service.order"),
            "res_id": at_risk.id,
            "user_id": env.uid,
            "summary": "Approve the estimate",
            "activity_type_id": env.ref("mail.mail_activity_data_todo").id,
        }
    )

    after = ctrl.stats()

    def delta(key):
        return after[key] - before[key]

    assert delta("open_orders") == 4  # intake + 2 diagnostic + awaiting_approval
    assert delta("intake_today") == 6
    assert delta("delivered_today") == 1
    assert delta("sla_at_risk") == 1
    assert after["worklist"]["sla_at_risk"] == after["sla_at_risk"]
    assert after["by_state"]["diagnostic"] - before["by_state"]["diagnostic"] == 2
    assert after["by_state"]["closed"] - before["by_state"]["closed"] == 1
    assert set(after["by_state"]) == {
        s for s, _l in env["fix.service.order"]._fields["state"].selection
    }
    assert after["channel_mix"]["walk_in"] - before["channel_mix"]["walk_in"] == 5
    assert after["channel_mix"]["onsite"] - before["channel_mix"]["onsite"] == 1
    assert after["revenue_mtd"] - before["revenue_mtd"] == pytest.approx(est.grand_total)
    assert est.grand_total == pytest.approx(5750.0)  # 5,000 + 15% VAT
    assert after["first_time_fix"] == round(
        100.0 * (qc_passed_before + 1) / (qc_total_before + 2), 1
    )
    assert after["worklist"]["unassigned_wos"] - before["worklist"]["unassigned_wos"] == 1
    assert after["worklist"]["awaiting_approval"] - before["worklist"]["awaiting_approval"] == 1

    trend = after["trend"]
    assert len(trend["labels"]) == len(trend["values"]) == 12
    assert trend["labels"][-1] == fields.Date.context_today(env.user).strftime("%b")
    assert trend["values"][-1] - before["trend"]["values"][-1] == 6

    mine = [a for a in after["my_activities"] if a["res_id"] == at_risk.id]
    assert mine == [
        {
            "res_model": "fix.service.order",
            "res_id": at_risk.id,
            "res_name": activity.res_name,
            "summary": "Approve the estimate",
            "deadline": activity.date_deadline,
        }
    ]
    assert {"Khulna Hub", "Gulshan Centre"} <= set(after["branches"])
    assert "Probe Technician Alam" in after["technicians"]
    assert after["company"] == {
        "name": env.company.name,
        "vat": env.company.vat or "",
        "phone": env.company.phone or "",
    }


def test_stats_activity_without_summary_falls_back_to_activity_type(ctrl, world):
    env = world.env
    order = _order(world)
    todo = env.ref("mail.mail_activity_data_todo")
    env["mail.activity"].create(
        {
            "res_model_id": env["ir.model"]._get_id("fix.service.order"),
            "res_id": order.id,
            "user_id": env.uid,
            "activity_type_id": todo.id,
        }
    )
    [row] = [a for a in ctrl.stats()["my_activities"] if a["res_id"] == order.id]
    assert row["summary"] == todo.name
    assert row["res_name"] == order.name


def test_stats_today_window_starts_at_dhaka_midnight(ctrl, world):
    """Regression: 'today' compared the Dhaka date against UTC timestamps, so
    an order taken at 00:30 Dhaka time (18:30 UTC the day before) was never
    counted as today's intake."""
    env = world.env
    today = fields.Date.context_today(env.user)
    midnight = _local_midnight_utc(today)
    before = ctrl.stats()["intake_today"]

    just_after = _order(world)
    just_before = _order(world)
    _set_dates(env, "fix.service.order", just_after, create_date=midnight + timedelta(minutes=30))
    _set_dates(env, "fix.service.order", just_before, create_date=midnight - timedelta(minutes=30))

    assert ctrl.stats()["intake_today"] - before == 1


def test_stats_technicians_fall_back_to_all_staff_without_technician_titles(ctrl, odoo_env):
    if odoo_env["hr.employee"].search_count([("job_title", "ilike", "technician")]):
        pytest.skip("the shared database already carries technician-titled staff")
    odoo_env["hr.employee"].create({"name": "Plain Clerk Rina"})
    assert "Plain Clerk Rina" in ctrl.stats()["technicians"]


def test_stats_first_time_fix_is_null_without_qc_records(ctrl, odoo_env):
    odoo_env["fix.qc.checklist"].search([]).unlink()
    assert ctrl.stats()["first_time_fix"] is None


# --- /p03/orders/list --------------------------------------------------------------------------


def test_list_orders_filters_and_attaches_latest_estimate(ctrl, world):
    khulna_order = _order(world, "intake")
    gulshan_order = _order(world, "diagnostic", branch=world.gulshan)
    _estimate(world, khulna_order, [("Old quote", "part", 100.0)], version=1)
    latest = _estimate(world, khulna_order, [("New quote", "part", 200.0)], version=2, state="sent")

    by_branch = ctrl.list_orders(branch="Khulna", limit=500)["orders"]
    ids = {o["id"] for o in by_branch}
    assert khulna_order.id in ids and gulshan_order.id not in ids
    row = next(o for o in by_branch if o["id"] == khulna_order.id)
    assert row["grand_total"] == pytest.approx(latest.grand_total)
    assert row["vat_amount"] == pytest.approx(latest.vat_amount)
    assert row["estimate_state"] == "sent"

    by_status = ctrl.list_orders(status="Diagnostic", branch="All", limit=500)["orders"]
    assert gulshan_order.id in {o["id"] for o in by_status}
    assert all(o["state"] == "diagnostic" for o in by_status)
    unestimated = next(o for o in by_status if o["id"] == gulshan_order.id)
    assert unestimated["grand_total"] is None and unestimated["estimate_state"] is None

    by_serial = ctrl.list_orders(search=gulshan_order.device_id.serial_number, status="Any")
    assert [o["id"] for o in by_serial["orders"]] == [gulshan_order.id]
    by_customer = ctrl.list_orders(search="Nusrat", limit=500)["orders"]
    assert {khulna_order.id, gulshan_order.id} <= {o["id"] for o in by_customer}


def test_estimate_totals_of_no_orders_is_empty(odoo_env):
    assert api._estimate_totals([], odoo_env) == {}


# --- /p03/order/get ------------------------------------------------------------------------------


def test_get_order_unknown_returns_error(ctrl, world):
    assert ctrl.get_order(order_id=999_999_999) == {"success": False, "error": "Order not found"}


def test_get_order_returns_full_live_detail(ctrl, world):
    env = world.env
    order = _order(
        world,
        "diagnostic",
        technician_id=world.tech.id,
        sla_resolution_deadline=datetime(2030, 1, 2, 3, 4, 5),
    )
    _estimate(world, order, [("Battery", "part", 900.0)], version=1)
    _estimate(world, order, [("Board", "part", 1500.0), ("Bench", "labour", 500.0)], version=2)
    env["fix.work.order"].create({"order_id": order.id})
    order.message_post(body="Customer called for an update")
    env["ir.attachment"].create(
        {
            "name": "intake-photo.pdf",
            "res_model": "fix.service.order",
            "res_id": order.id,
            "raw": b"x" * 4096,
            "mimetype": "application/pdf",
        }
    )

    result = ctrl.get_order(order_id=order.id)

    assert result["success"] is True
    detail = result["order"]
    assert detail["name"] == order.name
    assert detail["customer_name"] == "Nusrat Jahan"
    assert detail["customer_phone"] == "01710000001"
    assert detail["serial_number"] == order.device_id.serial_number
    assert detail["device_name"] == order.device_id.display_name
    assert detail["branch_name"] == "Khulna Hub"
    assert detail["technician"] == "Probe Technician Alam"
    assert detail["sla_resolution_deadline"] == "2030-01-02 03:04:05"
    assert detail["grand_total"] == pytest.approx(2300.0)  # v2: 2,000 + 15% VAT
    assert sorted(line["description"] for line in result["estimate_lines"]) == ["Bench", "Board"]
    assert len(result["work_orders"]) == 1
    assert any("Customer called" in m["body"] for m in result["audit_trail"])
    assert [a["title"] for a in result["attachments"]] == ["intake-photo.pdf"]
    assert result["attachments"][0]["type"] == "PDF"
    assert result["attachments"][0]["size_kb"] == 4
    assert result["company"]["name"] == env.company.name


def test_get_order_by_name_without_estimate_or_technician(ctrl, world):
    order = _order(world, "intake")
    result = ctrl.get_order(order_name=order.name)
    assert result["order"]["id"] == order.id
    assert result["order"]["technician"] == ""
    # A02 audit B3: a default SLA policy ships, so every order carries a clock.
    assert result["order"]["sla_resolution_deadline"] is not None
    assert result["order"]["grand_total"] is None
    assert result["estimate_lines"] == []


# --- /p03/order/create ----------------------------------------------------------------------------

INTAKE = {
    "customer_name": "Farhana Akter",
    "customer_phone": "01810000002",
    "fault_description": "Cracked screen",
    "branch_name": "Gulshan",
    "brand": "Probeworks",
    "model": "PW-15",
    "serial": "SN-NEW-0001",
    "priority": "HIGH",
    "service_type": "walk_in",
    "entitlement": "corporate_amc",
}


@pytest.mark.parametrize("missing", ["customer_name", "customer_phone", "fault_description"])
def test_create_order_requires_core_intake_fields(ctrl, world, missing):
    payload = {**INTAKE, missing: "   "}
    result = ctrl.create_order(**payload)
    assert result["success"] is False
    assert "required (AS-09)" in result["error"]


def test_create_order_registers_party_device_and_order(ctrl, world):
    env = world.env
    result = ctrl.create_order(**INTAKE, idempotency_key="idem-p03-1")

    assert result["success"] is True
    order = env["fix.service.order"].browse(result["order_id"])
    assert order.state == "intake"
    assert order.priority == "high"
    assert order.order_category == "amc"
    assert order.branch_id == world.gulshan
    assert order.customer_id.name == "Farhana Akter"
    assert order.customer_id.phone == "01810000002"
    assert order.device_id.serial_number == "SN-NEW-0001"
    assert order.device_id.device_model_id == world.model
    assert order.device_id.owner_id == order.customer_id
    assert result["device"] == order.device_id.display_name
    assert result["branch"] == "Gulshan Centre"


def test_create_order_with_same_idempotency_key_replays(ctrl, world):
    first = ctrl.create_order(**INTAKE, idempotency_key="idem-p03-2")
    replay = ctrl.create_order(**INTAKE, idempotency_key="  idem-p03-2  ")
    assert replay["idempotent_replay"] is True
    assert replay["order_id"] == first["order_id"]
    assert replay["state"] == "intake"
    assert (
        world.env["fix.service.order"].search_count([("idempotency_key", "=", "idem-p03-2")]) == 1
    )


def test_create_order_reuses_existing_party_and_device(ctrl, world):
    env = world.env
    partners_before = env["res.partner"].search_count([])
    result = ctrl.create_order(
        **{**INTAKE, "customer_phone": "01710000001", "serial": "SN-P03-0001", "entitlement": ""}
    )
    order = env["fix.service.order"].browse(result["order_id"])
    assert order.customer_id == world.partner
    assert order.device_id == world.device
    assert order.order_category == "standard"
    assert env["res.partner"].search_count([]) == partners_before


def test_create_order_registers_a_new_brand_and_model(ctrl, world):
    env = world.env
    result = ctrl.create_order(
        **{
            **INTAKE,
            "brand": "Zentrix",
            "model": "ZX Fold",
            "serial": "SN-ZX-1",
            "entitlement": "mystery-plan",
        }
    )
    device = env["fix.service.order"].browse(result["order_id"]).device_id
    assert device.brand_id.name == "Zentrix" and device.brand_id.code == "ZENT"
    assert device.device_model_id.name == "ZX Fold"
    assert device.device_model_id.device_type == "laptop"
    assert env["fix.service.order"].browse(result["order_id"]).order_category == "standard"


def test_create_order_defaults_branch_brand_and_model_when_unspecified(ctrl, world):
    env = world.env
    result = ctrl.create_order(
        **{**INTAKE, "branch_name": "", "brand": "", "model": "", "serial": "SN-DEF-1"}
    )
    assert result["success"] is True
    order = env["fix.service.order"].browse(result["order_id"])
    assert order.branch_id == env["fix.branch"].search([], limit=1)
    assert order.device_id.brand_id == env["fix.brand"].search([], limit=1)


def test_create_order_unknown_branch_is_refused(ctrl, world):
    result = ctrl.create_order(**{**INTAKE, "branch_name": "Atlantis"})
    assert result == {"success": False, "error": "No branch matches the selection."}


def test_create_order_with_an_empty_brand_master_is_refused(ctrl, world):
    world.env["fix.brand"].search([]).write({"active": False})
    result = ctrl.create_order(**{**INTAKE, "brand": ""})
    assert result["success"] is False
    assert "brand master is empty" in result["error"]


def test_create_order_without_serial_never_borrows_another_device(ctrl, world):
    """Regression: with no serial the API attached the FIRST device in the
    registry (another customer's) to the new order."""
    env = world.env
    orders_before = env["fix.service.order"].search_count([])
    result = ctrl.create_order(**{**INTAKE, "serial": ""})
    assert result == {
        "success": False,
        "error": "Serial number is required to register a device.",
    }
    assert env["fix.service.order"].search_count([]) == orders_before


def test_create_order_failure_rolls_back_everything_it_registered(ctrl, world):
    """A warranty order for a device without an active warranty is refused by
    the BRU-SRM-02 gate; the party/brand/device rows created on the way are
    rolled back with it."""
    env = world.env
    payload = {
        **INTAKE,
        "customer_phone": "01910000009",
        "brand": "Ghostbrand",
        "serial": "SN-GHOST-1",
        "entitlement": "warranty",
    }
    result = ctrl.create_order(**payload)
    assert result["success"] is False
    assert "BRU-SRM-02" in result["error"]
    assert not env["res.partner"].search([("phone", "=", "01910000009")])
    assert not env["fix.brand"].search([("name", "=", "Ghostbrand")])
    assert not env["fix.device"].search([("serial_number", "=", "SN-GHOST-1")])


# --- /p03/order/advance_stage ------------------------------------------------------------------------


def test_advance_stage_unknown_order(ctrl, world):
    assert ctrl.advance_stage(order_id=999_999_999, next_state="diagnostic")["success"] is False


def test_advance_stage_requires_a_target(ctrl, world):
    result = ctrl.advance_stage(order_id=_order(world).id)
    assert result == {"success": False, "error": "next_state (or target_state) is required"}


def test_advance_stage_maps_workspace_aliases_along_valid_transitions(ctrl, world):
    order = _order(world, "intake")
    assert ctrl.advance_stage(order_id=order.id, next_state="Diagnosing") == {
        "success": True,
        "state": "diagnostic",
    }
    assert ctrl.advance_stage(order_id=order.id, target_state="estimate")["state"] == (
        "estimate_pending"
    )
    assert order.state == "estimate_pending"


def test_advance_stage_to_current_state_is_a_no_op(ctrl, world):
    order = _order(world, "in_repair")
    assert ctrl.advance_stage(order_id=order.id, next_state="in_progress") == {
        "success": True,
        "state": "in_repair",
        "no_op": True,
    }


def test_advance_stage_refuses_invalid_hops_with_the_legal_options(ctrl, world):
    order = _order(world, "intake")
    result = ctrl.advance_stage(order_id=order.id, next_state="ready")
    assert result["success"] is False
    assert result["error"] == "Invalid transition intake → ready. Valid: cancelled, diagnostic."
    assert order.state == "intake"
    closed = _order(world, "closed")
    assert "(terminal)" in ctrl.advance_stage(order_id=closed.id, next_state="intake")["error"]


def test_advance_stage_to_ready_is_held_by_the_qc_gate(ctrl, world):
    """Regression: advance_stage wrote state='ready' directly, bypassing the
    BRU-SRM-04 QC hard gate."""
    order = _order(world, "qc_pending")
    result = ctrl.advance_stage(order_id=order.id, next_state="ready")
    assert result["success"] is False
    assert "BRU-SRM-04" in result["error"]
    assert order.state == "qc_pending"
    world.env["fix.qc.checklist"].create({"order_id": order.id, "state": "passed"})
    assert ctrl.advance_stage(order_id=order.id, next_state="ready") == {
        "success": True,
        "state": "ready",
    }


# --- authorization guard ------------------------------------------------------------------------------


def _portal_user(env):
    return env["res.users"].create(
        {
            "name": "P03 API Portal Probe",
            "login": "p03.api.portal@example.test",
            "group_ids": [(6, 0, [env.ref("base.group_portal").id])],
        }
    )


@pytest.mark.parametrize(
    "route, kwargs",
    [
        ("stats", {}),
        ("list_orders", {}),
        ("get_order", {"order_id": 1}),
        ("create_order", {}),
        ("advance_stage", {"order_id": 1, "next_state": "diagnostic"}),
        ("assign_dispatch", {"order_id": 1}),
        ("reserve_inventory", {"order_id": 1}),
        ("dispatch_map_data", {}),
        ("consoles_data", {}),
        ("notify_collection", {"order_id": 1}),
    ],
)
def test_every_route_refuses_portal_sessions(odoo_env, route, kwargs):
    """auth="user" admits portal users; every /p03/* route is internal-only."""
    portal_env = odoo_env(user=_portal_user(odoo_env))
    patcher, controller = _controller(portal_env)
    try:
        with pytest.raises(AccessError):
            getattr(controller, route)(**kwargs)
    finally:
        patcher.stop()


def test_sudo_reads_are_fenced_to_the_users_companies(world):
    """map_data / consoles_data read with sudo(); another company's orders and
    branches must not leak into them."""
    env = world.env
    other = env["res.company"].create({"name": "P03 Foreign Co"})
    _order(world, "intake")
    foreign_entity = env["fix.entity"].create(
        {"code": "P03F", "legal_name": "P03 Foreign Ltd", "company_id": other.id}
    )
    foreign_ou = env["operating.unit"].create(
        {
            "name": "P03 Foreign OU",
            "code": "P03FOU",
            "company_id": other.id,
            "partner_id": other.partner_id.id,
        }
    )
    foreign_branch = env["fix.branch"].create(
        {
            "code": "FRN",
            "name": "Foreign Branch",
            "entity_id": foreign_entity.id,
            "operating_unit_id": foreign_ou.id,
        }
    )
    staff = env["res.users"].create(
        {
            "name": "P03 Staff Probe",
            "login": "p03.staff.probe@example.test",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            "company_id": env.company.id,
            "company_ids": [(6, 0, [env.company.id])],
        }
    )
    staff_env = env(user=staff)
    assert other not in staff_env.user.company_ids
    patcher, controller = _controller(staff_env)
    try:
        data = controller.dispatch_map_data()
    finally:
        patcher.stop()
    assert foreign_branch.id not in {b["id"] for b in data["branches"]}
    assert world.khulna.id in {b["id"] for b in data["branches"]}


# --- /p03/dispatch/assign ------------------------------------------------------------------------------


def _rostered(w, employee):
    shift = w.env["fix.shift.template"].create({"name": "Day", "start_hour": 9, "end_hour": 18})
    w.env["fix.roster.slot"].create(
        {
            "employee_id": employee.id,
            # the M55 availability check reads the context date (Asia/Dhaka)
            "date": fields.Date.context_today(w.env["fix.roster.slot"]),
            "shift_id": shift.id,
        }
    )


def _certified(w, employee):
    competency = w.env["fix.competency"].create(
        {
            "code": f"CMP-{next(_SEQ)}",
            "name": "Laptop repair",
            "device_type": "laptop",
            "required_for_dispatch": True,
        }
    )
    w.env["fix.certification"].create(
        {"employee_id": employee.id, "competency_id": competency.id, "status": "active"}
    )


def test_dispatch_unknown_order(ctrl, world):
    assert ctrl.assign_dispatch(order_id=999_999_999)["error"] == "Order not found"


def test_dispatch_unknown_technician(ctrl, world):
    result = ctrl.assign_dispatch(order_id=_order(world).id, technician="Nobody Matches Zz")
    assert result == {"success": False, "error": "No technician matches 'Nobody Matches Zz' in HR."}


def test_dispatch_creates_and_assigns_the_work_order(ctrl, world):
    _rostered(world, world.tech)
    _certified(world, world.tech)
    order = _order(world, "approved")

    result = ctrl.assign_dispatch(order_id=order.id, technician="Technician Alam", van_route="R-7")

    assert result["success"] is True
    assert order.technician_id == world.tech
    work_order = order.work_order_ids
    assert len(work_order) == 1
    assert (work_order.technician_id, work_order.state) == (world.tech, "assigned")
    assert result["work_order"] == work_order.name
    assert any("Probe Technician Alam" in b and "R-7" in b for b in _messages(order))


def test_dispatch_reuses_the_existing_work_order(ctrl, world):
    _rostered(world, world.tech)
    # A09 C4: the technician holds the certification; a waiver is a routed
    # record now (M22-F3), not a flag set on the work order
    _certified(world, world.tech)
    order = _order(world, "approved")
    existing = world.env["fix.work.order"].create({"order_id": order.id})
    result = ctrl.assign_dispatch(order_id=order.id, technician="Probe Technician")
    assert result["success"] is True
    assert order.work_order_ids == existing
    assert existing.state == "assigned"
    note = next(b for b in _messages(order) if "Dispatch" in b)
    assert " — " not in note  # no route/notes supplied


def test_dispatch_refusal_by_the_roster_gate_changes_nothing(ctrl, world):
    """Regression: a gate refusal used to leave the ORDER pointing at the
    refused technician (the order write was not rolled back)."""
    # certified, so the M22 gate (checked first, fail-closed) lets it through
    # and the M55 roster gate is the one that refuses: not on today's roster
    _certified(world, world.tech)
    order = _order(world, "approved")
    result = ctrl.assign_dispatch(order_id=order.id, technician="Probe Technician Alam")
    assert result["success"] is False
    assert result["refused_by_gate"] is True
    assert "M55 availability" in result["error"]
    assert not order.technician_id
    assert not order.work_order_ids


def test_dispatch_failure_outside_the_gates_is_not_flagged_as_gate(ctrl, world):
    order = _order(world, "approved")
    WorkOrder = type(world.env["fix.work.order"])
    with mock.patch.object(WorkOrder, "create", side_effect=RuntimeError("database unavailable")):
        result = ctrl.assign_dispatch(order_id=order.id, technician="Probe Technician Alam")
    # an unexpected failure is logged; the client gets a generic message,
    # never the exception text (information-disclosure fix)
    assert result == {
        "success": False,
        "error": api._GENERIC_ERROR,
        "refused_by_gate": False,
    }
    assert not order.technician_id


def test_dispatch_without_a_name_takes_the_first_employee(ctrl, world):
    first = world.env["hr.employee"].search([], limit=1)
    _rostered(world, first)
    _certified(world, first)
    order = _order(world, "approved")
    world.env["fix.work.order"].create({"order_id": order.id})
    result = ctrl.assign_dispatch(order_id=order.id)
    assert result["success"] is True
    assert result["technician"] == first.name


# --- /p03/inventory/reserve ------------------------------------------------------------------------------


def _product(env, code="PRT-SCR-15", cost=2450.5):
    return env["product.product"].create(
        {"name": "PW-15 Screen Assembly", "default_code": code, "standard_price": cost}
    )


def test_reserve_unknown_order(ctrl, world):
    assert ctrl.reserve_inventory(order_id=999_999_999)["error"] == "Order not found"


def test_reserve_unknown_sku(ctrl, world):
    result = ctrl.reserve_inventory(order_id=_order(world).id, part_sku="NO-SUCH-SKU-ZZ")
    assert result["success"] is False
    assert "No product matches SKU 'NO-SUCH-SKU-ZZ'" in result["error"]


def test_reserve_consumes_the_part_at_real_cost(ctrl, world):
    product = _product(world.env)
    order = _order(world, "in_repair")

    result = ctrl.reserve_inventory(order_id=order.id, part_sku="PRT-SCR-15", qty=2)

    assert result["success"] is True
    assert result["unit_cost"] == pytest.approx(2450.5)
    part = order.work_order_ids.parts_consumed_ids
    assert (part.product_id, part.quantity) == (product, 2.0)
    assert result["work_order"] == order.work_order_ids.name
    assert any("reserved 2×" in b and "2,450.50" in b for b in _messages(order))


def test_reserve_on_existing_work_order_by_name_and_default_qty(ctrl, world):
    _product(world.env, code="PRT-BAT-1", cost=0.0)
    order = _order(world, "in_repair")
    work_order = world.env["fix.work.order"].create({"order_id": order.id})
    result = ctrl.reserve_inventory(order_id=order.id, part_sku="Screen Assembly", qty=None)
    assert result["success"] is True
    assert work_order.parts_consumed_ids.quantity == 1.0
    assert result["unit_cost"] == 0.0


def test_reserve_without_sku_takes_the_first_product(ctrl, world):
    _product(world.env)
    order = _order(world, "in_repair")
    first = world.env["product.product"].search([], limit=1)
    result = ctrl.reserve_inventory(order_id=order.id)
    assert result["success"] is True, result
    assert result["part"] == first.display_name


def test_reserve_failure_leaves_no_half_created_work_order(ctrl, world):
    _product(world.env)
    order = _order(world, "in_repair")
    result = ctrl.reserve_inventory(order_id=order.id, part_sku="PRT-SCR-15", qty="two")
    assert result == {"success": False, "error": "Quantity must be a number."}
    assert not order.work_order_ids
    result = ctrl.reserve_inventory(order_id=order.id, part_sku="PRT-SCR-15", qty=-1)
    assert result == {"success": False, "error": "Quantity must be positive."}
    WorkOrder = type(world.env["fix.work.order"])
    with mock.patch.object(WorkOrder, "create", side_effect=RuntimeError("pg detail leak")):
        result = ctrl.reserve_inventory(order_id=order.id, part_sku="PRT-SCR-15")
    assert result == {"success": False, "error": api._GENERIC_ERROR}
    assert not order.work_order_ids


# --- /p03/dispatch/map_data --------------------------------------------------------------------------------


def _attendance(env, employee, lat=None, lng=None, check_out=None):
    vals = {
        "employee_id": employee.id,
        "check_in": fields.Datetime.now() - timedelta(hours=3),
        "source": "manual",
    }
    if lat is not None:
        vals.update(geo_lat=lat, geo_long=lng)
    if check_out:
        vals["check_out"] = check_out
    return env["fix.attendance.record"].create(vals)


def test_map_data_anchors_branches_and_counts_open_orders(ctrl, world):
    plaza = world.env["fix.branch"].create(
        {
            "code": "PLZ",
            "name": "Probe Plaza",
            "entity_id": world.khulna.entity_id.id,
            "operating_unit_id": world.khulna.operating_unit_id.id,
        }
    )
    _order(world, "intake")
    _order(world, "delivered")

    data = ctrl.dispatch_map_data()

    assert data["success"] is True
    branches = {b["id"]: b for b in data["branches"]}
    khulna, gulshan, other = (
        branches[world.khulna.id],
        branches[world.gulshan.id],
        branches[plaza.id],
    )
    assert khulna["open_orders"] == 1  # delivered is not open
    assert khulna["phone"] == "041-555" and gulshan["phone"] == ""
    # city-anchored approximations (+/- the deterministic 2x0.008 jitter)
    assert abs(khulna["lat"] - 22.8456) <= 0.0161 and abs(khulna["lng"] - 89.5403) <= 0.0161
    assert abs(gulshan["lat"] - 23.7925) <= 0.0161
    assert abs(other["lat"] - 23.8103) <= 0.0161 and abs(other["lng"] - 90.4125) <= 0.0161


def test_map_data_technicians_use_real_attendance_gps_only(ctrl, world):
    env = world.env
    on_duty = world.tech
    off_duty = env["hr.employee"].create(
        {"name": "Probe Technician Bina", "job_title": "Technician"}
    )
    absent = env["hr.employee"].create(
        {"name": "Probe Technician Chandu", "job_title": "Technician"}
    )
    _attendance(env, on_duty, lat=22.81234, lng=89.56789)
    _attendance(env, off_duty, check_out=fields.Datetime.now() - timedelta(hours=1))
    env["fix.work.order"].create(
        {
            "order_id": _order(world).id,
            "technician_id": on_duty.id,
            "state": "in_progress",
            "certification_waiver": True,
        }
    )

    techs = {t["id"]: t for t in ctrl.dispatch_map_data()["technicians"]}

    assert techs[on_duty.id]["on_duty"] is True
    assert (techs[on_duty.id]["lat"], techs[on_duty.id]["lng"]) == (22.8123, 89.5679)
    assert techs[on_duty.id]["active_wos"] == 1
    assert techs[on_duty.id]["job_title"] == "Field Technician"
    assert techs[off_duty.id]["on_duty"] is False
    assert techs[off_duty.id]["lat"] is None
    assert techs[absent.id]["on_duty"] is False and techs[absent.id]["lng"] is None


def test_map_data_falls_back_to_hr_attendance(world):
    env = world.env
    env["hr.attendance"].create(
        {"employee_id": world.tech.id, "check_in": fields.Datetime.now() - timedelta(hours=1)}
    )
    patcher, ctrl = _controller(EnvView(env, {"fix.attendance.record"}))
    try:
        techs = {t["id"]: t for t in ctrl.dispatch_map_data()["technicians"]}
    finally:
        patcher.stop()
    assert techs[world.tech.id]["on_duty"] is True
    assert techs[world.tech.id]["lat"] is None  # hr.attendance carries no geo_lat


def test_map_data_without_any_attendance_model(world):
    _attendance(world.env, world.tech, lat=22.8, lng=89.5)
    patcher, ctrl = _controller(EnvView(world.env, {"fix.attendance.record", "hr.attendance"}))
    try:
        techs = {t["id"]: t for t in ctrl.dispatch_map_data()["technicians"]}
    finally:
        patcher.stop()
    assert techs[world.tech.id]["on_duty"] is False
    assert techs[world.tech.id]["lat"] is None


def test_map_data_places_active_orders_near_their_branch(ctrl, world):
    order = _order(
        world, "in_repair", priority="urgent", sla_resolution_deadline=datetime(2030, 5, 6, 7, 8, 9)
    )
    _order(world, "ready")  # not an active dispatch state

    data = ctrl.dispatch_map_data()

    rows = {o["id"]: o for o in data["orders"]}
    row = rows[order.id]
    khulna = next(b for b in data["branches"] if b["id"] == world.khulna.id)
    assert abs(row["lat"] - khulna["lat"]) <= 0.0051
    assert row["branch"] == "Khulna Hub"
    assert row["customer"] == "Nusrat Jahan"
    assert row["priority"] == "urgent"
    assert row["deadline"] == "2030-05-06 07:08:09"
    assert all(
        o["state"] in {"intake", "diagnostic", "in_repair", "approved"} for o in rows.values()
    )


def _zone(env):
    return env["fix.zone"].create({"name": "Map Zone", "code": f"MZ{next(_SEQ)}"})


def test_map_data_geofence_absent_is_null(ctrl, world):
    world.env["fix.geofence"].search([]).write({"active": False})
    assert ctrl.dispatch_map_data()["geofence"] is None


def test_map_data_serves_a_real_circle_geofence(ctrl, world):
    env = world.env
    env["fix.geofence"].search([]).write({"active": False})
    env["fix.geofence"].create(
        {
            "name": "Dhaka North",
            "zone_id": _zone(env).id,
            "geofence_type": "circle",
            "geometry_json": json.dumps({"lat": 23.87, "lng": 90.39, "radius_m": 1500}),
        }
    )
    assert ctrl.dispatch_map_data()["geofence"] == {
        "name": "Dhaka North",
        "center": {"lat": 23.87, "lng": 90.39},
        "radius_m": 1500,
    }


def test_map_data_ignores_polygon_and_corrupt_geofences(ctrl, world):
    env = world.env
    env["fix.geofence"].search([]).write({"active": False})
    polygon = env["fix.geofence"].create(
        {
            "name": "Poly",
            "zone_id": _zone(env).id,
            "geofence_type": "polygon",
            "geometry_json": json.dumps({"points": [[23.7, 90.4], [23.8, 90.5], [23.9, 90.6]]}),
        }
    )
    assert ctrl.dispatch_map_data()["geofence"] is None

    polygon.active = False
    circle = env["fix.geofence"].create(
        {
            "name": "Legacy",
            "zone_id": _zone(env).id,
            "geofence_type": "circle",
            "geometry_json": json.dumps({"lat": 1, "lng": 2, "radius_m": 3}),
        }
    )
    # a legacy row corrupted outside the ORM (the constraint would refuse it)
    _set_dates(env, "fix.geofence", circle, geometry_json="{corrupt")
    assert ctrl.dispatch_map_data()["geofence"] is None


# --- /p03/consoles/data -------------------------------------------------------------------------------------


def test_consoles_data_branch_and_workshop_views(ctrl, world):
    env = world.env
    now = fields.Datetime.now()
    before_all = ctrl.consoles_data()
    walkin = _order(world, "intake")
    _order(world, "intake", service_type="onsite")  # not a walk-in
    aged_30h = _order(world, "diagnostic")
    aged_50h = _order(world, "in_repair")
    _set_dates(env, "fix.service.order", aged_30h, create_date=now - timedelta(hours=30))
    _set_dates(env, "fix.service.order", aged_50h, create_date=now - timedelta(hours=50))
    ready = _order(world, "ready")
    hold = _order(world, "awaiting_approval", fault_description="Board swap")
    qc = _order(world, "qc_pending", technician_id=world.tech.id)
    _order(world, "intake", order_category="rework")
    other_branch = _order(world, "intake", branch=world.gulshan)
    est = _estimate(world, ready, [("Part", "part", 1000.0)], state="approved", approved_at=now)
    bench = env["fix.work.order"].create(
        {
            "order_id": aged_50h.id,
            "technician_id": world.tech.id,
            "state": "in_progress",
            "certification_waiver": True,
            "start_time": now - timedelta(hours=2),
            "end_time": now,
        }
    )

    data = ctrl.consoles_data(branch_id=str(world.khulna.id))

    assert data["success"] is True
    branch = data["branch_console"]
    queue_ids = [w["id"] for w in branch["walkin_queue"]]
    assert walkin.id in queue_ids and other_branch.id not in queue_ids
    row = next(w for w in branch["walkin_queue"] if w["id"] == walkin.id)
    assert row["customer"] == "Nusrat Jahan" and row["priority"] == "normal"
    ageing = branch["wip_ageing"]
    assert ageing["between_24_48h"] == 1 and ageing["over_48h"] == 1
    assert ageing["under_24h"] >= 3  # the fresh intake / onsite / rework orders
    assert [r["id"] for r in branch["ready_collection"]] == [ready.id]
    cash = branch["cash_register"]
    assert cash["cash_collected_bdt"] - before_all["branch_console"]["cash_register"][
        "cash_collected_bdt"
    ] == pytest.approx(est.grand_total)
    assert cash["vat_collected_bdt"] >= est.vat_amount

    shop = data["workshop_console"]
    bench_row = next(b for b in shop["bench_board"] if b["id"] == bench.id)
    assert bench_row["technician"] == "Probe Technician Alam"
    assert bench_row["order_name"] == aged_50h.name
    assert bench_row["duration_hours"] == 2.0
    assert bench_row["bench_num"].startswith("Bench ")
    hold_row = next(h for h in shop["stuck_holds"] if h["id"] == hold.id)
    assert hold_row["reason"] == "Awaiting Customer Estimate Approval"
    qc_row = next(q for q in shop["qc_queue"] if q["id"] == qc.id)
    assert qc_row["technician"] == "Probe Technician Alam"
    assert shop["rework_count"] - before_all["workshop_console"]["rework_count"] >= 1


def test_consoles_data_without_branch_covers_all_branches(ctrl, world):
    gulshan_walkin = _order(world, "draft", branch=world.gulshan)
    qc = _order(world, "qc_pending")
    data = ctrl.consoles_data()
    assert gulshan_walkin.id in [w["id"] for w in data["branch_console"]["walkin_queue"]]
    assert (
        next(q for q in data["workshop_console"]["qc_queue"] if q["id"] == qc.id)["technician"]
        == "Bench Tech"
    )


def test_consoles_cash_register_counts_from_dhaka_midnight(ctrl, world):
    """Regression companion of the stats fix: an estimate approved at 00:30
    Dhaka time belongs to today's register, one at 23:30 yesterday does not."""
    env = world.env
    midnight = _local_midnight_utc(fields.Date.context_today(env.user))
    before = ctrl.consoles_data()["branch_console"]["cash_register"]["invoices_count"]
    order = _order(world, "approved")
    _estimate(
        world,
        order,
        [("P", "part", 10.0)],
        state="approved",
        approved_at=midnight + timedelta(minutes=30),
    )
    _estimate(
        world,
        order,
        [("P", "part", 10.0)],
        state="approved",
        version=2,
        approved_at=midnight - timedelta(minutes=30),
    )
    after = ctrl.consoles_data()["branch_console"]["cash_register"]["invoices_count"]
    assert after - before == 1


# --- /p03/notify/collection --------------------------------------------------------------------------------


def test_notify_collection_unknown_order(ctrl, world):
    assert ctrl.notify_collection(order_id=999_999_999) == {
        "success": False,
        "error": "Order not found",
    }


def test_notify_collection_logs_on_the_chatter_without_claiming_a_send(ctrl, world):
    order = _order(world, "ready")
    assert ctrl.notify_collection(order_id=order.id) == {"success": True, "order": order.name}
    note = next(b for b in _messages(order) if "Collection notification" in b)
    assert "logged by the branch console" in note
