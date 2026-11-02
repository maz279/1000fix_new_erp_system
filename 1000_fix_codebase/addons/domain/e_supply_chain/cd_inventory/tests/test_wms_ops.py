"""fix_wms_ops behaviour (live ORM, rolled back): the M41 execution documents —
slotting, dock appointments, put-away, waves, cartons, staging, tasks and bin
floor counts. The models live in cd_inventory (module-cycle avoidance)."""

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
    warehouse = env["fix.warehouse"].create(
        {
            "name": f"Ops WH {TAG}",
            "code": TAG[:6],
            "operating_unit_id": env.ref("base.main_company").id,
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
    tech = env["hr.employee"].create({"name": f"WMS Operator {TAG}"})
    return {
        "env": env,
        "warehouse": warehouse,
        "zone": zone,
        "bin_a": bin_a,
        "bin_b": bin_b,
        "part": part,
        "tech": tech,
    }


def test_slot_unique_per_part_and_bin(ctx):
    env, part = ctx["env"], ctx["part"]
    slot = env["fix.wms.slot"].create({"part_id": part.id, "bin_id": ctx["bin_a"].id, "qty": 5})
    assert slot.zone_id == ctx["zone"]
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.wms.slot"].create({"part_id": part.id, "bin_id": ctx["bin_a"].id, "qty": 1})


def test_dock_appointment_window_and_flow(ctx):
    env = ctx["env"]
    start = datetime(2026, 10, 28, 9, 0)
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.wms.dock"].create({"dock_no": "D1", "slot_start": start, "slot_end": start})
    dock = env["fix.wms.dock"].create(
        {"dock_no": "D1", "slot_start": start, "slot_end": start + timedelta(hours=1)}
    )
    assert dock.name.startswith("DOCK/")
    dock.action_check_in()
    dock.action_complete()
    assert dock.state == "completed"
    with pytest.raises(UserError, match="checked-in"), env.cr.savepoint():
        dock.action_complete()


def test_putaway_creates_or_adds_slot(ctx):
    env, part = ctx["env"], ctx["part"]
    first = env["fix.wms.putaway"].create(
        {"part_id": part.id, "qty": 2, "to_bin_id": ctx["bin_a"].id}
    )
    assert first.name.startswith("PUTA/")
    first.action_complete()
    slot = env["fix.wms.slot"].search(
        [("part_id", "=", part.id), ("bin_id", "=", ctx["bin_a"].id)], limit=1
    )
    assert slot.qty == pytest.approx(2.0)
    second = env["fix.wms.putaway"].create(
        {"part_id": part.id, "qty": 3, "to_bin_id": ctx["bin_a"].id}
    )
    second.action_complete()
    assert slot.qty == pytest.approx(5.0)


def test_wave_lifecycle_and_pick_decrements_slot(ctx):
    env, part = ctx["env"], ctx["part"]
    env["fix.wms.slot"].create({"part_id": part.id, "bin_id": ctx["bin_a"].id, "qty": 6})
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
    wave.action_pick_all()
    wave.line_ids[0].state = "pending"
    with pytest.raises(UserError, match="Every line must be picked"), env.cr.savepoint():
        wave.action_packed()
    wave.line_ids[0].state = "picked"
    assert wave.line_ids.picked_qty == pytest.approx(2.0)
    slot = env["fix.wms.slot"].search(
        [("part_id", "=", part.id), ("bin_id", "=", ctx["bin_a"].id)], limit=1
    )
    assert slot.qty == pytest.approx(4.0)
    wave.action_packed()
    wave.action_stage()
    wave.action_ship()
    assert wave.state == "shipped"
    assert wave.shipped_at


def test_wave_release_needs_lines(ctx):
    env = ctx["env"]
    wave = env["fix.wms.wave"].create({"wave_date": date(2026, 10, 28)})
    with pytest.raises(UserError, match="at least one line"), env.cr.savepoint():
        wave.action_release()


def test_carton_seal_and_negative_weight(ctx):
    env = ctx["env"]
    carton = env["fix.wms.carton"].create({"carton_size": "m", "weight_kg": 1.0})
    assert carton.name.startswith("CART/")
    carton.action_seal()
    assert carton.state == "sealed"
    with pytest.raises(IntegrityError), env.cr.savepoint():
        carton.weight_kg = -1


def test_stage_must_advance_in_order(ctx):
    env = ctx["env"]
    stage = env["fix.wms.stage"].create({"lane": "L1"})
    assert stage.name.startswith("STAG/")
    with pytest.raises(UserError, match="loaded"), env.cr.savepoint():
        stage.action_dispatch()
    stage.action_load()
    stage.action_dispatch()
    assert stage.state == "dispatched"


def test_task_assign_requires_operator_and_done(ctx):
    env, part = ctx["env"], ctx["part"]
    task = env["fix.wms.task"].create({"task_type": "pick", "part_id": part.id, "qty": 1})
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
    count = env["fix.wms.floor.count"].create(
        {
            "bin_id": ctx["bin_a"].id,
            "part_id": part.id,
            "expected_qty": 5,
            "counted_qty": 4,
            "counted_on": date(2026, 10, 28),
        }
    )
    assert count.name.startswith("FLCT/")
    assert count.variance == pytest.approx(-1.0)
    count.action_post()
    assert count.state == "posted"
    with pytest.raises(UserError, match="draft"), env.cr.savepoint():
        count.action_post()


def test_pick_marks_short_when_bin_holds_less(ctx):
    env, part = ctx["env"], ctx["part"]
    env["fix.wms.slot"].create({"part_id": part.id, "bin_id": ctx["bin_a"].id, "qty": 1})
    wave = env["fix.wms.wave"].create(
        {
            "wave_date": date(2026, 10, 28),
            "line_ids": [(0, 0, {"part_id": part.id, "bin_id": ctx["bin_a"].id, "qty": 2})],
        }
    )
    wave.action_release()
    wave.action_pick_all()
    line = wave.line_ids
    assert line.picked_qty == pytest.approx(1.0)
    assert line.state == "short"
    with pytest.raises(UserError, match="Every line must be picked"), env.cr.savepoint():
        wave.action_packed()
