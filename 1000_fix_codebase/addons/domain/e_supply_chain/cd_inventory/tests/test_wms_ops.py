"""fix_wms_ops behaviour (live ORM, rolled back): the M41 execution documents —
slotting, dock appointments, put-away, waves, cartons, staging, tasks and bin
floor counts. The models live in cd_inventory (module-cycle avoidance).

A06 remediation (R1): the proper paths through the M15 ledger, run as
trusted code. The pre-remediation versions put stock away from nothing,
typed slot quantities and line states, packed without cartons and shipped
without a loaded stage: they asserted the defects the A06 audit reported."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    location = env["fix.stock.location"].create({"name": "WMS Central", "code": f"WMC-{TAG}"})
    warehouse = env["fix.warehouse"].create(
        {
            "name": f"Ops WH {TAG}",
            "code": TAG[:6],
            "operating_unit_id": ou.id,
            "stock_location_id": location.id,
        }
    )
    zone = env["fix.warehouse.zone"].create(
        {
            "warehouse_id": warehouse.id,
            "name": "Pick",
            "code": f"Z{TAG[:4]}",
            "zone_type": "storage",
        }
    )
    bin_a = env["fix.warehouse.bin"].create(
        {"zone_id": zone.id, "name": f"A-{TAG}", "capacity_qty": 10}
    )
    bin_b = env["fix.warehouse.bin"].create(
        {"zone_id": zone.id, "name": f"B-{TAG}", "capacity_qty": 10}
    )
    part = env["fix.spare.part"].create(
        {"name": "WMS Ops Part", "part_number": f"WMS-{TAG}", "unit_cost": 100.0}
    )
    supplier = env["res.partner"].create({"name": f"WMS Supplier {TAG}"})
    receipt = env["fix.stock.receipt"].create(
        {
            "partner_id": supplier.id,
            "location_id": location.id,
            "line_ids": [
                (
                    0,
                    0,
                    {"part_id": part.id, "qty_received": 12, "qty_accepted": 12, "unit_cost": 100},
                )
            ],
        }
    )
    receipt.action_inspect()
    receipt.action_post()
    tech = env["hr.employee"].create({"name": f"WMS Operator {TAG}"})
    return {
        "env": env,
        "location": location,
        "warehouse": warehouse,
        "zone": zone,
        "bin_a": bin_a,
        "bin_b": bin_b,
        "part": part,
        "line": receipt.line_ids,
        "tech": tech,
    }


def _putaway(ctx, qty, bin_rec):
    pa = ctx["env"]["fix.wms.putaway"].create(
        {
            "part_id": ctx["part"].id,
            "qty": qty,
            "to_bin_id": bin_rec.id,
            "receipt_line_id": ctx["line"].id,
        }
    )
    pa.action_complete()
    return pa


def _slot(ctx, bin_rec):
    return ctx["env"]["fix.wms.slot"]._slot_for(ctx["part"], bin_rec)


def test_slot_unique_per_part_and_bin(ctx):
    env, part = ctx["env"], ctx["part"]
    slot = env["fix.wms.slot"].create({"part_id": part.id, "bin_id": ctx["bin_a"].id})
    assert slot.zone_id == ctx["zone"] and slot.qty == 0
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.wms.slot"].create({"part_id": part.id, "bin_id": ctx["bin_a"].id})
        env.flush_all()


def test_dock_appointment_window_and_flow(ctx):
    env = ctx["env"]
    start = datetime(2026, 10, 28, 9, 0)
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.wms.dock"].create({"dock_no": "D1", "slot_start": start, "slot_end": start})
        env.flush_all()
    dock = env["fix.wms.dock"].create(
        {
            "dock_no": f"D1-{TAG}",
            "slot_start": start,
            "slot_end": start + timedelta(hours=1),
            "receipt_id": ctx["line"].receipt_id.id,
        }
    )
    assert dock.name.startswith("DOCK/")
    dock.action_check_in()
    dock.action_complete()
    assert dock.state == "completed"
    with pytest.raises(UserError, match="checked-in"), env.cr.savepoint():
        dock.action_complete()


def test_putaway_creates_or_adds_slot(ctx):
    first = _putaway(ctx, 2, ctx["bin_a"])
    assert first.name.startswith("PUTA/")
    assert _slot(ctx, ctx["bin_a"]).qty == pytest.approx(2.0)
    _putaway(ctx, 3, ctx["bin_a"])
    assert _slot(ctx, ctx["bin_a"]).qty == pytest.approx(5.0)


def test_wave_lifecycle_moves_the_ledger(ctx):
    env, part = ctx["env"], ctx["part"]
    _putaway(ctx, 6, ctx["bin_a"])
    wave = env["fix.wms.wave"].create(
        {
            "wave_date": date(2026, 10, 28),
            "line_ids": [(0, 0, {"part_id": part.id, "bin_id": ctx["bin_a"].id, "qty": 2})],
        }
    )
    assert wave.name.startswith("WAVE/")
    with pytest.raises(UserError, match="Pack a picked wave"), env.cr.savepoint():
        wave.action_packed()
    wave.action_release()
    assert part.qty_reserved == pytest.approx(2.0)
    wave.action_pick_all()
    assert wave.line_ids.picked_qty == pytest.approx(2.0)
    assert _slot(ctx, ctx["bin_a"]).qty == pytest.approx(4.0)
    carton = env["fix.wms.carton"].create({"wave_id": wave.id, "contents_qty": 2, "weight_kg": 1.0})
    carton.action_seal()
    wave.action_packed()
    stage = env["fix.wms.stage"].create({"wave_id": wave.id, "lane": "L1", "load_ref": "VAN-1"})
    wave.action_stage()
    stage.action_load()
    wave.action_ship()
    assert wave.state == "shipped"
    assert wave.shipped_at
    assert part.qty_available == pytest.approx(10.0)  # 12 received - 2 shipped


def test_wave_release_needs_lines(ctx):
    env = ctx["env"]
    wave = env["fix.wms.wave"].create({"wave_date": date(2026, 10, 28)})
    with pytest.raises(UserError, match="at least one line"), env.cr.savepoint():
        wave.action_release()


def test_carton_seal_needs_a_picking_wave_and_weight_cannot_be_negative(ctx):
    env = ctx["env"]
    carton = env["fix.wms.carton"].create({"carton_size": "m", "weight_kg": 1.0})
    assert carton.name.startswith("CART/")
    with pytest.raises(UserError, match="wave"), env.cr.savepoint():
        carton.action_seal()
    with pytest.raises(IntegrityError), env.cr.savepoint():
        carton.weight_kg = -1
        carton.flush_recordset()


def test_stage_must_advance_in_order(ctx):
    env = ctx["env"]
    stage = env["fix.wms.stage"].create({"lane": "L1"})
    assert stage.name.startswith("STAG/")
    with pytest.raises(UserError, match="loaded"), env.cr.savepoint():
        stage.action_dispatch()
    with pytest.raises(UserError, match="staged wave"), env.cr.savepoint():
        stage.action_load()


def test_task_assign_requires_operator_and_done(ctx):
    env = ctx["env"]
    task = env["fix.wms.task"].create(
        {"task_type": "replenish", "part_id": ctx["part"].id, "qty": 1}
    )
    assert task.name.startswith("TASK/")
    with pytest.raises(UserError, match="operator"), env.cr.savepoint():
        task.action_assign()
    task.assignee_id = ctx["tech"].id
    task.action_assign()
    task.action_done()
    assert task.state == "done"
    assert task.done_at


def test_floor_count_variance_and_post(ctx):
    env, part = ctx["env"], ctx["part"]
    _putaway(ctx, 5, ctx["bin_a"])
    count = env["fix.wms.floor.count"].create(
        {
            "bin_id": ctx["bin_a"].id,
            "part_id": part.id,
            "counted_qty": 5,
            "counted_on": date(2026, 10, 28),
        }
    )
    assert count.name.startswith("FLCT/")
    assert (count.expected_qty, count.variance) == (5.0, 0.0)
    count.action_post()
    assert count.state == "posted"
    with pytest.raises(UserError, match="draft"), env.cr.savepoint():
        count.action_post()


def test_pick_marks_short_when_bin_holds_less(ctx):
    env, part = ctx["env"], ctx["part"]
    _putaway(ctx, 2, ctx["bin_a"])
    wave = env["fix.wms.wave"].create(
        {
            "wave_date": date(2026, 10, 28),
            "line_ids": [(0, 0, {"part_id": part.id, "bin_id": ctx["bin_a"].id, "qty": 2})],
        }
    )
    wave.action_release()
    # the pick face holds one less than the system thought
    slot = _slot(ctx, ctx["bin_a"])
    slot.write({"qty": 1, "reserved_qty": 1})
    wave.line_ids.write({"reserved_qty": 1})
    env["fix.stock.onhand"]._fix_unreserve(part, ctx["location"], "owned", 1, "test")
    wave.action_pick_all()
    line = wave.line_ids
    assert line.picked_qty == pytest.approx(1.0)
    assert line.state == "short"
    with pytest.raises(UserError, match="Every line must be picked"), env.cr.savepoint():
        wave.action_packed()
