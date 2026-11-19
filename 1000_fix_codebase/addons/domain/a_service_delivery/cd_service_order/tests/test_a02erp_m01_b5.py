# A02 ERP audit (2026-11-19), builder stream B5: M01 Service Request & Order
# Management findings M01-F2..F23 (money settlement is the lead's).
#
# Each control is exercised through the ORM as NON-ADMIN users (the shared M01
# fixture `w` of test_a02_p0_m01) or through the technician API with the real
# controller (`world` of test_technician_api_behaviour). Rolled back per test.
# ruff: noqa: F811 - the fixtures are imported so pytest registers them here.
import base64
from datetime import date, datetime, timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_p03_portal.controllers.a02 import m01 as p03_m01
from odoo.addons.cd_service_order.models import fix_service_order as so_mod
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import (  # noqa: F401 (fixture)
    GUARD,
    _user,
    approved,
    attempt,
    device,
    estimate,
    handover_evidence,
    order,
    so_request,
    to_estimating,
    to_ready,
    w,
)
from odoo.addons.cd_service_order.tests.test_a02_p1p2_cd_service_order import supervisor
from odoo.addons.cd_service_order.tests.test_technician_api_behaviour import (  # noqa: F401
    TechnicianApiController,
    _as,
    _so_to,
    world,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError

# the smallest valid PNG: the BER proposal checks the attachment is an image
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


def _qc(w, o, passed):
    return (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create(
            {"order_id": o.id, "item_ids": [Command.create({"name": "power", "passed": passed})]}
        )
    )


def _tech(w, login):
    user = _user(w.env, login)
    w.env["hr.employee"].create({"name": user.name, "user_id": user.id})
    return user


def _clocks(w, o, kpi):
    return w.env["fix.sla.kpi.instance"].for_record(o, kpi_code=kpi)


def _delivered_warranty_order(w, dev, **kw):
    """A zero-charge (warranty) order taken to Delivered."""
    w.env["ir.config_parameter"].set_param(so_mod.WARRANTY_VERIFIED_PARAM, "0")
    o = to_ready(w, order(w, dev=dev, order_category="warranty", **kw))
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered"
    return o


# ===================================================================== M01-F2
def test_f2_waiver_covers_only_the_amount_it_was_approved_for(w):
    o = to_estimating(order(w))
    # granted while nothing was priced: it covers BDT 0 (an e-waste intake)
    o.with_user(w.clerk).action_request_goodwill("nothing to charge yet")
    approve_via_inbox(so_request(w, "goodwill", o), w.approver, requester=w.clerk)
    assert o._fix_zero_charge_basis().startswith("goodwill")
    est = estimate(w, o, 1000)
    est.action_send()
    # the BDT 1,150 price that appeared later is NOT waived (it was, any amount)
    assert o._fix_amount_due() == 1150.0 and o._fix_zero_charge_basis() == ""
    # asked again on the price, and approved: the waiver covers it
    o.with_user(w.clerk).action_request_goodwill("loyal customer")
    approve_via_inbox(so_request(w, "goodwill", o), w.approver, requester=w.clerk)
    assert o.goodwill_cost_attribution_bdt == 1150.0
    assert o._fix_zero_charge_basis().startswith("goodwill")
    # a revision to a higher price voids the waiver: it covered BDT 1,150 only
    v2 = w.env["fix.estimate"].browse(est.with_user(w.clerk).action_revise()["res_id"])
    line = {"line_type": "labour", "description": "board", "quantity": 1, "unit_price": 20000}
    v2.with_user(w.clerk).write({"line_ids": [Command.create(line)]})
    v2.with_user(w.clerk).action_send()
    assert o._fix_amount_due() > 1150.0
    assert o._fix_zero_charge_basis() == ""
    # the rework confirmation is pinned the same way
    o.sudo()._guarded().write(
        {
            "is_goodwill": False,
            "is_rework": True,
            "rework_approved_by": w.approver.id,
            "rework_approved_amount_bdt": 1150.0,
        }
    )
    assert o._fix_zero_charge_basis() == ""
    o.sudo()._guarded().write({"rework_approved_amount_bdt": o._fix_amount_due()})
    assert o._fix_zero_charge_basis().startswith("rework confirmed")


# ===================================================================== M01-F3
def test_f3_version_and_order_link_are_guarded(w):
    o = to_estimating(order(w))
    assert GUARD in attempt(w, lambda: estimate(w, o, 500, version=4))
    est = estimate(w, o, 1000)
    assert GUARD in attempt(w, lambda: est.with_user(w.clerk).write({"version": 7}))
    est.action_send()
    other = to_estimating(order(w))
    assert "cannot be moved" in attempt(
        w, lambda: est.with_user(w.clerk).write({"order_id": other.id})
    )
    assert est.order_id == o


def test_f3_an_order_keeps_exactly_one_approved_version(w):
    o = to_estimating(order(w))
    v1 = estimate(w, o, 1000)
    v1.action_send()
    v2 = w.env["fix.estimate"].browse(v1.with_user(w.clerk).action_revise()["res_id"])
    assert v2.version == 2
    v2.with_user(w.clerk).action_send()
    # the older version is no longer the price on the table
    assert "superseded by version 2" in attempt(w, lambda: v1.with_user(w.clerk2).action_approve())
    v2.with_user(w.clerk2).action_approve()
    assert (v1.state, v2.state, o.state) == ("superseded", "approved", "approved")
    # a revision of the approved price, approved, retires the earlier approval
    v3 = w.env["fix.estimate"].browse(v2.with_user(w.clerk).action_revise()["res_id"])
    v3.with_user(w.clerk).action_send()
    v3.with_user(w.clerk2).action_approve()
    assert o.estimate_ids.filtered(lambda e: e.state == "approved") == v3
    assert (v2.state, o._fix_governing_estimate()) == ("superseded", v3)
    assert GUARD in attempt(w, lambda: v2.with_user(w.clerk).write({"state": "approved"}))


# ===================================================================== M01-F4
def test_f4_a_failed_inspection_does_not_block_the_next_qc_round(w):
    o = order(w)
    approved(w, o)
    o.action_start_repair()
    o.action_submit_qc()
    failed = _qc(w, o, False)
    failed.with_user(w.inspector).action_complete()
    assert (failed.state, o.state, failed.qc_round) == ("failed", "qc_failed", 1)
    o.action_start_repair()
    o.action_submit_qc()
    assert o.qc_round == 2
    assert "BRU-SRM-04" in attempt(w, lambda: o.action_ready())  # nothing inspected this round
    passed = _qc(w, o, True)
    passed.with_user(w.inspector).action_complete()
    o.action_ready()
    assert (o.state, passed.qc_round) == ("ready", 2)


def test_f4_an_inspection_started_after_a_pass_holds_ready(w):
    o = order(w)
    approved(w, o)
    o.action_start_repair()
    o.action_submit_qc()
    _qc(w, o, True).with_user(w.inspector).action_complete()
    _qc(w, o, True)  # a second inspection is under way
    assert "pending" in attempt(w, lambda: o.action_ready())


# ===================================================================== M01-F7
def test_f7_business_hours_are_dhaka_local_hours(w):
    env = w.env
    days = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
    cal = env["fix.working.calendar"].create(
        {
            "name": "B5 Dhaka 9-18",
            "line_ids": [
                Command.create({"weekday": d, "hour_from": 9.0, "hour_to": 18.0}) for d in days
            ],
        }
    )
    Inst = env["fix.sla.kpi.instance"]
    # 03:00 UTC is 09:00 in Dhaka: the branch has just opened
    assert Inst.add_business_hours(datetime(2026, 11, 22, 3, 0), 1.0, cal) == datetime(
        2026, 11, 22, 4, 0
    )
    # 17:00 Dhaka + 2 business hours = 10:00 Dhaka next day (04:00 UTC)
    assert Inst.add_business_hours(datetime(2026, 11, 22, 11, 0), 2.0, cal) == datetime(
        2026, 11, 23, 4, 0
    )
    # 08:00-11:00 Dhaka spans two working hours (09:00-11:00)
    assert Inst.business_minutes_between(
        datetime(2026, 11, 22, 2, 0), datetime(2026, 11, 22, 5, 0), cal
    ) == pytest.approx(120.0)
    # a holiday is a Dhaka DATE: 23 Nov closed moves the hour to 24 Nov
    env["fix.working.calendar.holiday"].create(
        {
            "calendar_id": cal.id,
            "name": "B5 closure",
            "date_from": date(2026, 11, 23),
            "date_to": date(2026, 11, 23),
        }
    )
    assert Inst.add_business_hours(datetime(2026, 11, 22, 11, 0), 2.0, cal) == datetime(
        2026, 11, 24, 4, 0
    )


# ===================================================================== M01-F8
def test_f8_passcode_needs_consent_is_masked_and_purged(w):
    o = order(w)
    assert "consent" in attempt(
        w, lambda: o.with_user(w.clerk).action_record_passcode("1234", "no")
    )
    o.with_user(w.clerk).action_record_passcode("1234", "yes")
    assert o.with_user(w.clerk).passcode_on_file
    assert o.passcode_consent_by == w.clerk and o.passcode_consent_at
    with pytest.raises(AccessError):
        o.with_user(w.clerk).read(["passcode_value"])
    assert o.with_user(w.inspector).passcode_value == "1234"
    assert GUARD in attempt(w, lambda: o.with_user(w.clerk).write({"passcode_value": "9999"}))
    o.action_intake()
    o.with_user(w.clerk).action_cancel(reason_code="duplicate")
    assert not o.sudo().passcode_value and o.passcode_purged_at
    assert not o.with_user(w.clerk).passcode_on_file


# ===================================================================== M01-F9
def test_f9_ber_needs_photo_evidence_and_a_second_technician(w):
    t1, t2 = _tech(w, "ber_one"), _tech(w, "ber_two")
    o = order(w)
    o.action_intake()
    o.action_start_diagnostic()
    assert "photographic" in attempt(
        w, lambda: o.with_user(t1).action_mark_unrepairable("board burnt")
    )
    # the other door: Cancel with reason 'unrepairable'
    assert "BRU-SRM-12" in attempt(
        w, lambda: o.with_user(w.clerk).action_cancel(reason_code="unrepairable")
    )
    photo = w.env["ir.attachment"].create({"name": "ber.png", "datas": base64.b64encode(PNG)})
    o.with_user(w.clerk).write({"ber_photo_attachment_id": photo.id})
    o.with_user(t1).action_mark_unrepairable("board burnt")
    assert (o.state, o.ber_proposed_by) == ("diagnostic", t1)
    assert "proposed by you" in attempt(w, lambda: o.with_user(t1).action_mark_unrepairable("x"))
    assert "frozen" in attempt(
        w, lambda: o.with_user(w.clerk).write({"ber_photo_attachment_id": False})
    )
    o.with_user(t2).action_mark_unrepairable("agreed, corrosion under the PMIC")
    assert (o.state, o.cancel_reason_code, o.ber_confirmed_by) == ("cancelled", "unrepairable", t2)


# ===================================================================== M01-F11 / F12 / F23
def test_f11_parts_issue_only_to_an_approved_order_and_cancel_ends_the_work(world):
    env, ctrl = world.env, TechnicianApiController()
    with _as(env, world.tech_user):
        refused = ctrl.van_stock_consume(work_order_id=world.wo.id, product_id=world.part.id)
    assert refused["error"]["code"] == "order_not_approved"
    with pytest.raises(UserError, match="Parts are issued"):
        env["fix.work.order.part"].with_user(world.other_user).create(
            {"work_order_id": world.wo.id, "product_id": world.part.id, "quantity": 1}
        )
    _so_to(world.so, "approved")
    with _as(env, world.tech_user):
        assert ctrl.van_stock_consume(work_order_id=world.wo.id, product_id=world.part.id)[
            "consumed"
        ]
        assert ctrl.technician_queue()["total"] == 1
    world.so.action_cancel(reason_code="customer_declined")
    assert world.wo.state == "cancelled"
    with _as(env, world.tech_user):
        assert ctrl.technician_queue()["total"] == 0
        again = ctrl.van_stock_consume(work_order_id=world.wo.id, product_id=world.part.id)
        status = ctrl.job_status(work_order_id=world.wo.id, action="start")
    assert again["error"]["code"] == "order_not_approved"
    assert status["error"]["code"] == "order_not_live"


def test_f12_qc_waits_for_every_work_order_and_f23_records_the_technician(world):
    env, ctrl = world.env, TechnicianApiController()
    second = env["fix.work.order"].create(
        {
            "order_id": world.so.id,
            "technician_id": world.other.id,
            "certification_waiver": True,
            "sequence": 2,
        }
    )
    _so_to(world.so, "approved")
    with _as(env, world.tech_user):
        ctrl.job_status(work_order_id=world.wo.id, action="start")
        first = ctrl.job_status(work_order_id=world.wo.id, action="complete")
    assert first["work_order"]["service_order_state"] == "in_repair"
    with _as(env, world.other_user):
        last = ctrl.job_status(work_order_id=second.id, action="complete")
    assert last["work_order"]["service_order_state"] == "qc_pending"
    assert world.so.repair_completed_by == world.other_user


def test_f23_the_workshop_bench_technician_cannot_inspect(w):
    if "workshop_job_ids" not in w.env["fix.service.order"]._fields:
        pytest.skip("cd_workshop is not installed")
    bench = _tech(w, "bench_tech")
    bench.write({"group_ids": [Command.link(w.env.ref(so_mod.GROUP_QC_INSPECTOR).id)]})
    o = order(w)
    approved(w, o)
    n = o.id
    workshop = w.env["fix.workshop"].create(
        {"code": "WS-B5-%d" % n, "name": "B5 Depot", "name_bn": "ডিপো"}
    )
    w.env["fix.workshop.job"].create(
        {
            "workshop_id": workshop.id,
            "fault_description": "B5 bench job",
            "repair_level": "l1",
            "order_id": o.id,
            "technician_id": bench.employee_id.id,
            "bookin_condition": "B5: scratches",
            "bookin_no_accessories": True,
        }
    )
    o.action_start_repair()
    o.action_submit_qc()
    qc = _qc(w, o, True)
    assert "Segregation of duties" in attempt(w, lambda: qc.with_user(bench).action_complete())


# ===================================================================== M01-F14
def test_f14_customer_damage_voids_warranty_zero_charge(w):
    params = w.env["ir.config_parameter"]
    params.set_param(so_mod.WARRANTY_VERIFIED_PARAM, "0")
    params.set_param(so_mod.WARRANTY_EXCLUDES_DAMAGE_PARAM, "1")
    o = order(w, dev=device(w, warranty="active"), order_category="warranty")
    assert o._fix_zero_charge_basis() == "warranty cover"
    o.with_user(w.clerk).write({"lci_tripped": True})
    assert o._fix_zero_charge_basis() == ""
    params.set_param(so_mod.WARRANTY_EXCLUDES_DAMAGE_PARAM, "0")
    assert o._fix_zero_charge_basis() == "warranty cover"
    params.set_param(so_mod.WARRANTY_EXCLUDES_DAMAGE_PARAM, "1")
    o.with_user(w.clerk).write({"lci_tripped": False})
    w.env["fix.fault.code"].create(
        {"code": "B5-LIQ-01", "name": "Liquid ingress", "category": "physical"}
    )
    w.env["fix.service.order.fault"].create(
        {"order_id": o.id, "fault_code": "B5-LIQ-01", "description": "Water in the port"}
    )
    assert o._fix_zero_charge_basis() == ""


# ===================================================================== M01-F15 / F16 / F17 / F20
def test_f15_f20_response_at_first_diagnosis_resolution_at_ready(w):
    o = order(w)
    o.action_intake()
    response = _clocks(w, o, so_mod.RESPONSE_KPI)
    assert response and o.sla_response_deadline == response.target_at
    o.action_start_diagnostic()
    assert o.sla_response_at
    response.invalidate_recordset()
    assert response.state == "succeeded"
    approved(w, o)
    o.action_start_repair()
    o.action_submit_qc()
    _qc(w, o, True).with_user(w.inspector).action_complete()
    o.action_ready()
    assert o.sla_resolution_at and o.sla_resolution_at == o.ready_at
    rows = {r["measure"]: r["value"] for r in p03_m01.sla_compliance_report(w.env)["rows"]}
    assert "First response on time" in rows and rows["Resolved on time"] >= 1


def test_f20_assignment_is_the_response(w):
    o = order(w)
    o.action_intake()
    tech = w.env["hr.employee"].create({"name": "B5 assigned"})
    response = _clocks(w, o, so_mod.RESPONSE_KPI)
    assert response.state == "in_progress"
    o.sudo().write({"technician_id": tech.id})
    assert o.sla_response_at
    response.invalidate_recordset()
    assert response.state == "succeeded" and not _clocks(w, o, so_mod.RESPONSE_KPI)


def test_f16_a_late_finish_is_recorded_as_a_breach(w):
    o = order(w)
    o.action_intake()
    clock = _clocks(w, o, "resolution")
    clock.sudo().write({"target_at": fields.Datetime.now() - timedelta(hours=1)})
    clock.sudo().succeed()
    assert clock.state == "breached" and clock.succeeded_at


def test_f17_a_service_order_clock_follows_the_order(w):
    sup = supervisor(w)
    o = order(w)
    o.action_intake()
    clock = _clocks(w, o, "resolution")
    assert "follows the order" in attempt(w, lambda: clock.with_user(sup).pause("lunch"))
    o.with_user(sup).action_defer_order("customer_travel")
    clock.invalidate_recordset()
    assert clock.state == "paused" and o.sla_clock_paused


# ===================================================================== M01-F18
def test_f18_a_hold_ends_on_its_date_and_on_parts_arrival(w):
    sup = supervisor(w)
    today = so_mod._dhaka_date()
    due, later, parts = order(w), order(w), order(w)
    for o in (due, later, parts):
        o.action_intake()
    due.with_user(sup).action_defer_order("customer_travel", resume_date=today - timedelta(days=1))
    later.with_user(sup).action_defer_order(
        "customer_travel", resume_date=today + timedelta(days=5)
    )
    parts.with_user(sup).action_defer_order("parts_backorder")
    w.env["fix.service.order"]._cron_resume_deferred()
    assert not due.is_deferred_block and not due.sla_clock_paused
    assert later.is_deferred_block and parts.is_deferred_block
    assert w.env.ref("cd_service_order.ir_cron_resume_deferred_orders").active
    Order = w.env["fix.service.order"].sudo()
    other = Order.consume_stock_reserved({"payload": {"service_order_ref": later.name}})
    assert not other["resumed"] and later.is_deferred_block  # not held for parts
    res = Order.consume_stock_reserved(
        {"payload": {"service_order_ref": parts.name, "part_number": "SCR-1", "quantity": 1}}
    )
    assert res["resumed"] and not parts.is_deferred_block and not parts.sla_clock_paused
    consumer = w.env.ref("cd_service_order.consumer_stock_reserved_service_order")
    assert (consumer.event_type, consumer.method) == ("stock.reserved", "consume_stock_reserved")


# ===================================================================== M01-F19
def test_f19_priority_override_is_a_supervisors_and_moves_the_sla(w):
    sup = supervisor(w)
    Policy = w.env["fix.sla.policy"].sudo()
    o = order(w)
    o.action_intake()
    urgent = o._fix_match_sla_policy("urgent") or Policy.create(
        {
            "code": "B5-URG",
            "name": "B5 urgent walk-in",
            "service_type": "walk_in",
            "priority": "urgent",
            "response_hours": 1.0,
            "resolution_hours": 4.0,
        }
    )
    assert "Supervisor" in attempt(
        w, lambda: o.with_user(w.clerk).action_override_priority("urgent", "VIP")
    )
    o.with_user(sup).action_override_priority("urgent", "VIP escalation")
    clock = _clocks(w, o, "resolution")
    assert (o.priority, o.sla_policy_id, clock.policy_id) == ("urgent", urgent, urgent)
    assert o.sla_resolution_deadline == clock.target_at and clock.supersedes_id


def test_f19_loyalty_priority_tier_gets_priority_one(w):
    env = w.env
    if env.get("fix.loyalty.account") is None:
        pytest.skip("cd_loyalty is not installed")
    env["ir.config_parameter"].set_param(so_mod.LOYALTY_PRIORITY_PARAM, "urgent")
    program = env["fix.loyalty.program"].create({"name": "B5 Privilege", "code": "B5PRV"})
    tier = env["fix.loyalty.tier"].create(
        {"program_id": program.id, "name": "Gold", "code": "B5GOLD", "priority_diagnostic": True}
    )
    env["fix.loyalty.account"].create(
        {"partner_id": w.customer.id, "program_id": program.id, "tier_id": tier.id}
    )
    assert order(w).priority == "urgent"
    env["ir.config_parameter"].set_param(so_mod.LOYALTY_PRIORITY_PARAM, "off")
    assert order(w).priority == "normal"


# ===================================================================== M01-F21
def test_f21_warranty_is_issued_at_handover_and_rework_counts_from_it(w):
    dev = device(w, warranty="active")
    fault = [Command.create({"fault_code": "DSP-01", "description": "No display"})]
    first = _delivered_warranty_order(w, dev, fault_line_ids=fault)
    days = first.service_warranty_days or 30
    assert first.service_warranty_until == so_mod._dhaka_date(first.delivered_at) + timedelta(
        days=days
    )
    assert first.with_user(w.clerk).action_reopen_comeback("no display again")
    # an earlier order still OPEN is not the repair the customer came back from
    open_dev = device(w)
    order(w, dev=open_dev, fault_line_ids=fault)
    assert not order(w, dev=open_dev, fault_line_ids=fault).is_rework
    # the window runs from the handover, not from the original order's creation
    w.env.cr.execute(
        "UPDATE fix_service_order SET create_date = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(days=60), first.id),
    )
    first.invalidate_recordset()
    again = order(w, dev=dev, fault_line_ids=fault)
    assert again.is_rework and again.rework_of_id == first


# ===================================================================== M01-F22
def test_f22_uncollected_register_lists_ready_devices_aged_from_ready(w):
    ready = to_ready(w, order(w))
    ready.sudo()._guarded().write({"ready_at": fields.Datetime.now() - timedelta(days=9)})
    report = p03_m01.uncollected_register_report(w.env)
    rows = {r["order"]: r for r in report["rows"]}
    assert rows[ready.name]["days_uncollected"] == 9
    assert {r["state"] for r in report["rows"]} == {"ready"}
