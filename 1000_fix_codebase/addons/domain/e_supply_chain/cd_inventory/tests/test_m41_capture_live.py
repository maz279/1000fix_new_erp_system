# M41 capture audit (2026-11-14) - the records the new page captures create,
# exercised on the live ORM as NON-ADMIN users holding the real roles. Each
# test shows the proper path works and the control the spec names refuses.
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

from . import test_a06_m41_controls as base

wms = base.wms

REFUSED = (UserError, AccessError, ValidationError, IntegrityError)


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _slot(w, bin_rec):
    return w.env["fix.wms.slot"]._slot_for(w.wpart, bin_rec)


def _move(w, user, qty=4, to_bin=None, **kw):
    vals = {
        "move_type": "move",
        "part_id": w.wpart.id,
        "from_bin_id": w.bin.id,
        "to_bin_id": (to_bin or w.bin2).id,
        "qty": qty,
        "reason_code": "wrong_bin",
    }
    vals.update(kw)
    return w.env["fix.wms.move"].with_user(user).create(vals)


def _confirm(w, move, user):
    move.with_user(user).action_confirm(
        from_code=move.from_bin_id.name,
        to_code=move.to_bin_id.name,
        item_code=move.part_id.part_number,
    )


def _location_total(w):
    on_hand = w.env["fix.stock.onhand"]._bucket(w.wpart, w.central, "owned")
    return on_hand.qty if on_hand else 0.0


# ======================================================== page 7 internal move
def test_a_move_shifts_the_bin_slots_and_never_the_ledger(wms):
    w = wms
    total = _location_total(w)
    move = _move(w, w.operator)
    assert move.state == "open" and move.task_id.task_type == "move"
    assert move.task_id.move_id == move and move.name.startswith("MOVE/")
    _confirm(w, move, w.operator)
    assert (move.state, move.done_by_id) == ("done", w.operator)
    assert (move.scanned_from, move.scanned_to) == (w.bin.name, w.bin2.name)
    assert _slot(w, w.bin).qty == 6 and _slot(w, w.bin2).qty == 4
    assert move.task_id.state == "done"
    assert _location_total(w) == total  # BRU-WMS-01: M15 is untouched


def test_a_move_needs_both_bin_scans_and_the_item(wms):
    w = wms
    move = _move(w, w.operator)
    refused(w, lambda: move.with_user(w.operator).action_confirm(), "Scanned bin")
    refused(
        w,
        lambda: move.with_user(w.operator).action_confirm(w.bin.name, w.bin.name, "x"),
        "Scanned bin",
    )
    refused(
        w,
        lambda: move.with_user(w.operator).action_confirm(w.bin.name, w.bin2.name, "NOPE"),
        "Scanned item",
    )
    assert move.state == "open" and _slot(w, w.bin).qty == 10


def test_a_move_takes_only_free_stock(wms):
    w = wms
    move = _move(w, w.operator, qty=11)
    refused(w, lambda: _confirm(w, move, w.operator), "free")
    wave = w.wave(qty=8)
    wave.with_user(w.supervisor).action_release()
    move2 = _move(w, w.operator, qty=3)
    refused(w, lambda: _confirm(w, move2, w.operator), "allocated")


def test_a_move_obeys_the_put_away_rules(wms):
    w = wms
    # quarantine is reached through M15, not a bin move
    refused(w, lambda: _confirm(w, _move(w, w.operator, to_bin=w.qbin), w.operator), "quarantine")
    # ownership class (BRU-WMS-03): an unrestricted bin's stock cannot enter a consignment bin
    cbin = w.env["fix.warehouse.bin"].create(
        {"zone_id": w.zone.id, "name": "C-01-" + w.tag, "ownership_class": "consignment"}
    )
    refused(w, lambda: _confirm(w, _move(w, w.operator, to_bin=cbin), w.operator), "BRU-WMS-03")
    # capacity (BRU-WMS-09): bin A holds 10
    w.env["fix.wms.slot"]._slot_for(w.wpart, w.bin2, create=True)
    small = w.env["fix.warehouse.bin"].create(
        {"zone_id": w.zone.id, "name": "S-01-" + w.tag, "capacity_qty": 2}
    )
    refused(
        w,
        lambda: _confirm(w, _move(w, w.operator, qty=3, to_bin=small), w.operator),
        "holds at most",
    )
    # blocked target (BRU-WMS-12)
    w.bin2.with_user(w.operator).action_block("rack damaged")
    refused(w, lambda: _confirm(w, _move(w, w.operator), w.operator), "blocked")
    assert _slot(w, w.bin).qty == 10


def test_a_move_between_warehouses_is_refused(wms):
    w = wms
    other_wh = w.env["fix.warehouse"].create(
        {
            "name": "Other " + w.tag,
            "code": "O" + w.tag[:5],
            "operating_unit_id": w.ou.id,
            "wms_enabled": True,
        }
    )
    zone = w.env["fix.warehouse.zone"].create(
        {"warehouse_id": other_wh.id, "name": "Z", "code": "Z1", "zone_type": "storage"}
    )
    far = w.env["fix.warehouse.bin"].create({"zone_id": zone.id, "name": "F-01-" + w.tag})
    refused(w, lambda: _move(w, w.operator, to_bin=far), "different warehouses")


def test_a_done_move_is_final_and_a_plain_user_cannot_create_one(wms):
    w = wms
    move = _move(w, w.operator)
    _confirm(w, move, w.operator)
    refused(w, lambda: move.with_user(w.operator).write({"qty": 1}), "final")
    refused(w, lambda: move.with_user(w.operator).write({"state": "open"}))
    refused(w, lambda: _move(w, w.clerk), None)


def test_the_assigned_task_confirms_the_move(wms):
    w = wms
    move = _move(w, w.operator, assignee_id=w.op_emp.id)
    task = move.task_id
    task.with_user(w.operator).action_assign()
    task.with_user(w.operator).action_done(
        scan="%s %s %s" % (w.bin.name, w.bin2.name, w.wpart.part_number)
    )
    assert (task.state, move.state) == ("done", "done")
    assert _slot(w, w.bin2).qty == 4


# ======================================================== page 2/7 pick-face replenishment
def _bulk(w, qty=20):
    bulk = w.env["fix.warehouse.bin"].create(
        {"zone_id": w.zone.id, "name": "B-01-" + w.tag, "capacity_qty": 100}
    )
    pa = w.putaway(w.operator, qty=qty, bin_rec=bulk)
    pa.with_user(w.operator).action_complete(bin_code=bulk.name, item_code=w.wpart.part_number)
    slot = _slot(w, bulk)
    slot.write({"slot_type": "bulk"})
    return bulk, slot


def test_a_pick_face_below_minimum_raises_the_bulk_move(wms):
    w = wms
    bulk, _bs = _bulk(w)
    w.slot.with_user(w.operator).write({"min_qty": 12, "max_qty": 15})
    w.slot.with_user(w.operator).action_raise_replenishment()
    move = w.env["fix.wms.move"].search([("to_bin_id", "=", w.bin.id), ("state", "=", "open")])
    assert (move.move_type, move.from_bin_id, move.qty, move.trigger_qty) == (
        "replenish",
        bulk,
        5.0,
        10.0,
    )
    assert move.task_id.task_type == "replenish"
    # one open replenishment per pick face
    refused(w, lambda: w.slot.with_user(w.operator).action_raise_replenishment(), "already open")


def test_replenishment_refuses_without_minimum_or_source(wms):
    w = wms
    refused(w, lambda: w.slot.with_user(w.operator).action_raise_replenishment(), "minimum")
    w.slot.with_user(w.operator).write({"min_qty": 12})
    refused(w, lambda: w.slot.with_user(w.operator).action_raise_replenishment(), "No bulk")
    refused(w, lambda: w.slot.with_user(w.operator).write({"min_qty": 5, "max_qty": 2}), "minimum")


def test_a_pick_that_crosses_the_minimum_replenishes_itself(wms):
    w = wms
    bulk, _bs = _bulk(w)
    w.slot.write({"min_qty": 8})
    wave = w.wave(qty=4)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    line.with_user(w.operator).action_scan_pick(bin_code=w.bin.name, item_code=w.wpart.part_number)
    move = w.env["fix.wms.move"].search([("to_bin_id", "=", w.bin.id), ("state", "=", "open")])
    assert move and move.from_bin_id == bulk and move.qty == 2.0  # back up to the minimum


# ======================================================== page 5 short pick
def test_a_short_pick_picks_what_was_found_and_counts_the_bin_back(wms):
    w = wms
    wave = w.wave(qty=6)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    refused(
        w,
        lambda: line.with_user(w.operator).action_scan_short_pick(
            bin_code=w.bin.name, item_code=w.wpart.part_number, found_qty=6
        ),
        "not short",
    )
    refused(
        w,
        lambda: line.with_user(w.operator).action_scan_short_pick(bin_code=w.bin.name),
        "quantity",
    )
    line.with_user(w.operator).action_scan_short_pick(
        bin_code=w.bin.name, item_code=w.wpart.part_number, found_qty=2
    )
    assert (line.state, line.picked_qty, line.scanned_bin) == ("short", 2.0, w.bin.name)
    assert _slot(w, w.bin).qty == 8  # the count-back settles the rest, never the device
    back = w.env["fix.wms.task"].search(
        [("bin_id", "=", w.bin.id), ("task_type", "=", "count"), ("ref", "like", "Count-back")]
    )
    assert back


def test_an_empty_bin_short_pick_needs_no_item_scan(wms):
    w = wms
    wave = w.wave(qty=3)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    refused(
        w,
        lambda: line.with_user(w.operator).action_scan_short_pick(bin_code="X", found_qty=0),
        "Scanned bin",
    )
    line.with_user(w.operator).action_scan_short_pick(bin_code=w.bin.name, found_qty=0)
    assert (line.state, line.picked_qty) == ("short", 0.0)
    assert _slot(w, w.bin).qty == 10


# ======================================================== page 8 claim, devices
def test_an_operative_claims_a_free_task_once(wms):
    w = wms
    task = w.env["fix.wms.task"].with_user(w.operator).create({"task_type": "replenish"})
    task.with_user(w.operator).action_claim()
    assert (task.state, task.assignee_id) == ("assigned", w.op_emp)
    w.env["hr.employee"].create({"name": "Op2 " + w.tag, "user_id": w.operator2.id})
    refused(w, lambda: task.with_user(w.operator2).action_claim(), "only an open task")
    refused(w, lambda: task.with_user(w.clerk).action_claim(), "employee record")


def test_equipment_bound_tasks_go_only_to_holders(wms):
    w = wms
    task = (
        w.env["fix.wms.task"]
        .with_user(w.operator)
        .create({"task_type": "replenish", "bin_id": w.bin.id, "equipment_required": "ladder"})
    )
    refused(w, lambda: task.with_user(w.operator).action_claim(), "BRU-WMS-18")
    ladder = (
        w.env["fix.wms.equipment"]
        .with_user(w.supervisor)
        .create(
            {
                "warehouse_id": w.wh.id,
                "code": "LAD-1",
                "name": "Step ladder",
                "equipment_type": "ladder",
            }
        )
    )
    w.env["fix.wms.operative"].with_user(w.supervisor).create(
        {"employee_id": w.op_emp.id, "warehouse_id": w.wh.id, "equipment_ids": [(6, 0, ladder.ids)]}
    )
    task.with_user(w.operator).action_claim()
    assert task.state == "assigned"


def test_profiles_equipment_and_devices_are_the_supervisors(wms):
    w = wms
    refused(
        w,
        lambda: (
            w.env["fix.wms.equipment"]
            .with_user(w.operator)
            .create(
                {
                    "warehouse_id": w.wh.id,
                    "code": "T1",
                    "name": "Trolley",
                    "equipment_type": "trolley",
                }
            )
        ),
    )
    refused(
        w,
        lambda: (
            w.env["fix.wms.operative"]
            .with_user(w.operator)
            .create({"employee_id": w.op_emp.id, "warehouse_id": w.wh.id})
        ),
    )
    refused(
        w,
        lambda: (
            w.env["fix.wms.device"]
            .with_user(w.operator)
            .create({"warehouse_id": w.wh.id, "device_code": "RF-X-" + w.tag})
        ),
    )
    other = w.env["fix.warehouse.zone"].create(
        {
            "warehouse_id": w.env["fix.warehouse"]
            .create(
                {
                    "name": "W2 " + w.tag,
                    "code": "Q" + w.tag[:5],
                    "operating_unit_id": w.ou.id,
                    "wms_enabled": True,
                }
            )
            .id,
            "name": "Z",
            "code": "Z9",
            "zone_type": "storage",
        }
    )
    refused(
        w,
        lambda: (
            w.env["fix.wms.operative"]
            .with_user(w.supervisor)
            .create(
                {
                    "employee_id": w.op_emp.id,
                    "warehouse_id": w.wh.id,
                    "zone_ids": [(6, 0, other.ids)],
                }
            )
        ),
        "must belong",
    )


def test_a_lost_device_is_deactivated_and_another_admin_reactivates(wms):
    w = wms
    dev = (
        w.env["fix.wms.device"]
        .with_user(w.supervisor)
        .create(
            {"warehouse_id": w.wh.id, "device_code": "RF-" + w.tag, "operative_id": w.op_emp.id}
        )
    )
    assert dev.state == "active" and dev.enrolled_by_id == w.supervisor and dev.enrolled_at
    refused(w, lambda: dev.with_user(w.supervisor).write({"state": "deactivated"}))
    refused(w, lambda: dev.with_user(w.supervisor).action_deactivate(), "reason")
    refused(w, lambda: dev.with_user(w.operator).action_deactivate(reason="lost"))
    dev.with_user(w.supervisor).action_deactivate(reason="Lost on the dock")
    assert (dev.state, dev.deactivated_by_id) == ("deactivated", w.supervisor)
    refused(w, lambda: dev.with_user(w.supervisor).action_reactivate(), "another administrator")
    dev.with_user(w.controller).action_reactivate()
    assert dev.state == "active"
    refused(
        w,
        lambda: (
            w.env["fix.wms.device"]
            .with_user(w.supervisor)
            .create({"warehouse_id": w.wh.id, "device_code": "RF-" + w.tag})
        ),
    )
