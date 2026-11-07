# A06 final pass - M41 model controls. Each test attacks the control as a
# NON-ADMIN user holding the real role and asserts the refusal, and shows the
# proper path still works. Item numbers are the final-pass brief's (B1..B19).
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

from . import test_a06_m41_controls as base

wms = base.wms
_pack_and_load = base._pack_and_load

REFUSED = (UserError, AccessError, ValidationError, IntegrityError)


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _released(w, qty=4, **kw):
    wave = w.wave(qty=qty, **kw)
    wave.with_user(w.supervisor).action_release()
    return wave


def _pick(w, line, user=None):
    line.with_user(user or w.operator).action_scan_pick(
        bin_code=line.bin_id.name, item_code=line.part_id.part_number
    )


def _serial_slot(w):
    """One serialized unit, received at the warehouse's location and binned."""
    env = w.env
    name = "WMS-SN-" + w.tag
    rec = env["fix.stock.receipt"].create(
        {
            "partner_id": w.supplier.id,
            "location_id": w.central.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": w.spart.id,
                        "qty_received": 1,
                        "qty_accepted": 1,
                        "unit_cost": 8000,
                        "line_no": name,
                    },
                )
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    lot = env["fix.stock.lot"]._fix_find(w.spart, name)
    pa = env["fix.wms.putaway"].create(
        {
            "part_id": w.spart.id,
            "qty": 1,
            "to_bin_id": w.bin2.id,
            "receipt_line_id": rec.line_ids.id,
            "lot_id": lot.id,
        }
    )
    pa.action_complete()
    return lot


# ======================================================== B7 scans, supervisor exception
def test_b7_put_away_needs_the_bin_and_item_scan(wms):
    w = wms
    pa = w.putaway(w.operator, qty=5, bin_rec=w.bin2)
    refused(w, lambda: pa.with_user(w.operator).action_complete(), "Scanned bin")
    refused(
        w,
        lambda: pa.with_user(w.operator).action_complete(
            bin_code=w.bin.name, item_code=w.wpart.part_number
        ),
        "Scanned bin",
    )
    refused(
        w,
        lambda: pa.with_user(w.operator).action_complete(bin_code=w.bin2.name, item_code="NOPE"),
        "Scanned item",
    )
    assert pa.state == "pending"
    pa.with_user(w.operator).action_complete(bin_code=w.bin2.name, item_code=w.wpart.part_number)
    assert pa.state == "done"
    assert (pa.scanned_bin, pa.scanned_item) == (w.bin2.name, w.wpart.part_number)


def test_b7_pick_all_is_a_supervisor_exception_with_a_reason(wms):
    w = wms
    wave = _released(w)
    refused(
        w, lambda: wave.with_user(w.operator).action_pick_all(reason="scanner down"), "Supervisor"
    )
    refused(w, lambda: wave.with_user(w.supervisor).action_pick_all(), "reason")
    wave.with_user(w.supervisor).action_pick_all(reason="Scanner down in aisle 3")
    assert wave.line_ids.state == "picked"
    assert (wave.pick_all_reason, wave.pick_all_by_id) == ("Scanner down in aisle 3", w.supervisor)


def test_b7_pick_all_refuses_a_serialized_line(wms):
    w = wms
    _serial_slot(w)
    wave = w.wave(qty=1, part=w.spart, bin_rec=w.bin2)
    wave.with_user(w.supervisor).action_release()
    refused(w, lambda: wave.with_user(w.supervisor).action_pick_all(reason="x"), "serialized")


def test_b7_release_raises_one_pick_task_per_line(wms):
    w = wms
    wave = _released(w)
    tasks = w.env["fix.wms.task"].search([("wave_line_id", "=", wave.line_ids.id)])
    assert len(tasks) == 1
    assert (tasks.task_type, tasks.state, tasks.part_id, tasks.bin_id, tasks.qty) == (
        "pick",
        "open",
        w.wpart,
        w.bin,
        4.0,
    )


def test_b7_scan_pick_closes_the_lines_task(wms):
    w = wms
    wave = _released(w)
    line = wave.line_ids
    _pick(w, line)
    task = w.env["fix.wms.task"].search([("wave_line_id", "=", line.id)])
    assert (task.state, task.done_by_id, task.qty) == ("done", w.operator, 4.0)
    assert (line.state, line.picked_qty, line.scanned_bin) == ("picked", 4.0, w.bin.name)


def test_b7_the_assignee_completes_the_pick_through_the_task(wms):
    w = wms
    wave = _released(w)
    task = w.env["fix.wms.task"].search([("wave_line_id", "=", wave.line_ids.id)])
    task.with_user(w.operator).write({"assignee_id": w.op_emp.id})
    task.with_user(w.operator).action_assign()
    task.with_user(w.operator).action_done(scan="%s %s" % (w.bin.name, w.wpart.part_number))
    assert task.state == "done" and wave.line_ids.state == "picked"


# ======================================================== B8 one operative, supervisor grant
def test_b8_release_needs_the_supervisor(wms):
    w = wms
    wave = w.wave(qty=4)
    refused(w, lambda: wave.with_user(w.operator).action_release(), "Supervisor")
    assert wave.state == "draft"
    wave.with_user(w.supervisor).action_release()
    assert wave.state == "released"


def test_b8_an_inventory_controller_holds_the_supervisor_grant(wms):
    w = wms
    wave = w.wave(qty=4)
    wave.with_user(w.controller).action_release()
    assert wave.state == "released"


def test_b8_an_operator_cannot_take_a_task_from_its_assignee(wms):
    w = wms
    other = w.env["hr.employee"].create({"name": "Other Op " + w.tag, "user_id": w.operator2.id})
    task = (
        w.env["fix.wms.task"]
        .with_user(w.operator)
        .create({"task_type": "replenish", "assignee_id": w.op_emp.id})
    )
    task.with_user(w.operator).action_assign()
    refused(w, lambda: task.with_user(w.operator2).write({"assignee_id": other.id}), "Supervisor")
    refused(w, lambda: task.with_user(w.operator2).action_done(), "assigned to")
    task.with_user(w.supervisor).write({"assignee_id": other.id})
    task.with_user(w.operator2).action_done()
    assert task.state == "done"


def test_b8_an_operator_may_claim_a_free_task_but_not_hand_one_out(wms):
    w = wms
    other = w.env["hr.employee"].create({"name": "Other Op2 " + w.tag})
    free = w.env["fix.wms.task"].with_user(w.operator).create({"task_type": "replenish"})
    refused(w, lambda: free.with_user(w.operator).write({"assignee_id": other.id}), "Supervisor")
    free.with_user(w.operator).write({"assignee_id": w.op_emp.id})
    assert free.assignee_id == w.op_emp


def test_b8_another_operator_cannot_scan_pick_an_assigned_line(wms):
    w = wms
    wave = _released(w)
    task = w.env["fix.wms.task"].search([("wave_line_id", "=", wave.line_ids.id)])
    task.with_user(w.operator).write({"assignee_id": w.op_emp.id})
    task.with_user(w.operator).action_assign()
    refused(w, lambda: _pick(w, wave.line_ids, user=w.operator2), "assigned to")
    assert wave.line_ids.state == "pending"


def test_b8_put_away_reassignment_is_the_supervisors(wms):
    w = wms
    other = w.env["hr.employee"].create({"name": "Other Op3 " + w.tag, "user_id": w.operator2.id})
    pa = w.putaway(w.operator, qty=5, bin_rec=w.bin2, assignee_id=w.op_emp.id)
    refused(w, lambda: pa.with_user(w.operator2).write({"assignee_id": other.id}), "Supervisor")
    pa.with_user(w.supervisor).write({"assignee_id": other.id})
    assert pa.assignee_id == other


# ======================================================== B9 M15 movements respect bins
def test_b9_an_issue_cannot_take_stock_out_of_the_bins(wms):
    w = wms
    # 100 at the location, 10 of them in bin A: 90 are free
    issue = w.issue(w.keeper, part=w.wpart, qty=91.0, location=w.central)
    refused(w, lambda: issue.with_user(w.keeper).action_scan_and_consume(), "in warehouse bins")
    assert w.qty(w.wpart, w.central) == 100.0
    ok = w.issue(w.keeper, part=w.wpart, qty=90.0, location=w.central)
    ok.with_user(w.keeper).action_scan_and_consume()
    assert w.qty(w.wpart, w.central) == 10.0
    assert w.slot.qty == 10.0


def test_b9_a_transfer_cannot_take_stock_out_of_the_bins(wms):
    w = wms
    transfer = w.transfer(w.keeper, qty=95.0, part=w.wpart)
    transfer.with_user(w.keeper).action_submit()
    transfer.with_user(w.controller).action_approve()
    refused(w, lambda: transfer.with_user(w.keeper).action_dispatch(), "in warehouse bins")


def test_b9_a_quarantine_cannot_take_stock_out_of_the_bins(wms):
    w = wms
    refused(w, lambda: w.quarantine(w.keeper, qty=95.0, part=w.wpart), "in warehouse bins")
    w.quarantine(w.keeper, qty=90.0, part=w.wpart)
    assert w.qty(w.wpart, w.central, status="quarantine") == 90.0


def test_b9_a_location_with_no_warehouse_is_unaffected(inv):
    issue = inv.issue(inv.keeper, qty=10.0)
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert inv.qty(inv.part, inv.central) == 0.0


# ======================================================== B11 the block closes the bin
def test_b11_another_part_cannot_enter_a_blocked_bin(wms):
    w = wms
    w.slot.with_user(w.operator).action_block(reason="Racking damaged")
    other = w.env["fix.spare.part"].create(
        {"name": "A06 Other", "part_number": "A6Z-" + w.tag, "unit_cost": 1.0}
    )
    rec = w.env["fix.stock.receipt"].create(
        {
            "partner_id": w.supplier.id,
            "location_id": w.central.id,
            "line_ids": [
                (0, 0, {"part_id": other.id, "qty_received": 2, "qty_accepted": 2, "unit_cost": 1})
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    pa = w.putaway(w.operator, qty=2, part=other, line=rec.line_ids)
    refused(
        w,
        lambda: pa.with_user(w.operator).action_complete(
            bin_code=w.bin.name, item_code=other.part_number
        ),
        "blocked",
    )


def test_b11_an_empty_bin_can_be_blocked_from_the_bin_row(wms):
    w = wms
    w.bin2.with_user(w.operator).action_block(reason="Cleaning")
    assert w.bin2.blocked and w.bin2.block_reason == "Cleaning"
    refused(
        w,
        lambda: w.putaway(w.operator, qty=1, bin_rec=w.bin2)
        .with_user(w.operator)
        .action_complete(bin_code=w.bin2.name, item_code=w.wpart.part_number),
        "blocked",
    )
    refused(
        w, lambda: w.bin2.with_user(w.operator).action_unblock(note="ok"), "Inventory Controller"
    )
    w.bin2.with_user(w.controller).action_unblock(note="Clean again")
    assert not w.bin2.blocked


def test_b11_block_is_guarded_and_the_blocker_cannot_unblock(wms):
    w = wms
    refused(w, lambda: w.bin2.with_user(w.operator).write({"blocked": True}), "changes only")
    w.bin2.with_user(w.controller).action_block(reason="Audit hold")
    refused(w, lambda: w.bin2.with_user(w.controller).action_unblock(note="x"), "Segregation")
    w.bin2.with_user(w.controller2).action_unblock(note="Audit done")
    assert not w.bin2.blocked


def test_b11_unblocking_a_slot_opens_every_slot_of_the_bin(wms):
    w = wms
    w.slot.with_user(w.operator).action_block(reason="Racking damaged")
    assert w.bin.blocked and w.slot.state == "blocked"
    w.slot.with_user(w.controller).action_unblock(note="Repaired")
    assert not w.bin.blocked and w.slot.state == "active"


# ======================================================== B12 wave cancel
def test_b12_cancel_needs_the_supervisor_and_a_reason(wms):
    w = wms
    wave = _released(w)
    refused(w, lambda: wave.with_user(w.operator).action_cancel(reason="x"), "Supervisor")
    refused(w, lambda: wave.with_user(w.supervisor).action_cancel(), "Record why")
    assert wave.state == "released"


def test_b12_cancel_releases_the_reservations(wms):
    w = wms
    wave = _released(w, qty=4)
    assert w.bucket(w.wpart, w.central).reserved == 4.0 and w.slot.reserved_qty == 4.0
    wave.with_user(w.supervisor).action_cancel(reason="Order withdrawn")
    assert wave.state == "cancelled" and wave.cancel_reason == "Order withdrawn"
    assert w.bucket(w.wpart, w.central).reserved == 0.0 and w.slot.reserved_qty == 0.0
    assert wave.line_ids.state == "cancelled"
    task = w.env["fix.wms.task"].search([("wave_line_id", "=", wave.line_ids.id)])
    assert task.state == "cancelled"
    # another wave can now have that stock
    _released(w, qty=10)


def test_b12_cancel_puts_picked_stock_back(wms):
    w = wms
    wave = _released(w, qty=4)
    _pick(w, wave.line_ids)
    assert w.slot.qty == 6.0 and w.qty(w.wpart, w.central, status="staged") == 4.0
    carton = (
        w.env["fix.wms.carton"]
        .with_user(w.operator)
        .create({"wave_id": wave.id, "contents_qty": 4, "weight_kg": 1.0})
    )
    carton.with_user(w.operator).action_seal()
    wave.with_user(w.supervisor).action_cancel(reason="Order withdrawn")
    assert w.slot.qty == 10.0
    assert w.qty(w.wpart, w.central, status="staged") == 0.0
    assert w.qty(w.wpart, w.central) == 100.0
    assert carton.state == "open"


def test_b12_a_loaded_or_shipped_wave_cannot_be_cancelled(wms):
    w = wms
    wave = _released(w, qty=4)
    _pick(w, wave.line_ids)
    _carton, stage = _pack_and_load(w, wave)
    assert stage.state == "loaded"
    refused(w, lambda: wave.with_user(w.supervisor).action_cancel(reason="x"), "loaded")
    wave.with_user(w.operator).action_ship()
    refused(w, lambda: wave.with_user(w.supervisor).action_cancel(reason="x"), "already")


# ======================================================== B13 manifest and events
def _staged(w, wave):
    carton = (
        w.env["fix.wms.carton"]
        .with_user(w.operator)
        .create(
            {
                "wave_id": wave.id,
                "contents_qty": int(sum(wave.line_ids.mapped("picked_qty"))),
                "weight_kg": 1.0,
            }
        )
    )
    carton.with_user(w.operator).action_seal()
    wave.with_user(w.operator).action_packed()
    stage = (
        w.env["fix.wms.stage"]
        .with_user(w.operator)
        .create({"wave_id": wave.id, "lane": "L1", "load_ref": "TRUCK-9"})
    )
    wave.with_user(w.operator).action_stage()
    return carton, stage


def test_b13_loading_needs_the_scanned_manifest(wms):
    w = wms
    wave = _released(w)
    _pick(w, wave.line_ids)
    carton, stage = _staged(w, wave)
    refused(w, lambda: stage.with_user(w.operator).action_load(), "manifest")
    refused(
        w, lambda: stage.with_user(w.operator).action_load(carton_scans="CART/WRONG"), "manifest"
    )
    refused(
        w,
        lambda: stage.with_user(w.operator).action_load(carton_scans=carton.name + " CART/EXTRA"),
        "manifest",
    )
    assert stage.state == "staging"
    stage.with_user(w.operator).action_load(carton_scans=carton.name)
    assert stage.state == "loaded" and stage.manifest_verified and carton.load_scanned


def test_b13_ship_refuses_a_load_with_no_verified_manifest(wms):
    w = wms
    wave = _released(w)
    _pick(w, wave.line_ids)
    _carton, stage = _staged(w, wave)
    # an old stage already loaded when the manifest arrived
    stage.sudo()._guarded().write({"state": "loaded"})
    refused(w, lambda: wave.with_user(w.operator).action_ship(), "manifest")
    refused(
        w, lambda: stage.with_user(w.operator).write({"manifest_verified": True}), "changes only"
    )
    # it verifies by loading again
    stage.with_user(w.operator).action_load(carton_scans=_carton.name)
    wave.with_user(w.operator).action_ship()
    assert wave.state == "shipped"
    assert w.events("wh.shipped", "fix.wms.wave", wave.id) == 1


def test_b13_short_pick_publishes(wms):
    w = wms
    wave = w.wave(qty=4)
    wave.with_user(w.supervisor).action_release()
    # the bin was found short by an approved count
    w.slot.sudo()._guarded().write({"qty": 3.0, "reserved_qty": 3.0})
    _pick(w, wave.line_ids)
    line = wave.line_ids
    assert line.state == "short"
    assert w.events("wh.short_pick", "fix.wms.wave.line", line.id) == 1


def test_b13_transfer_received_publishes(inv):
    transfer = inv.transfer(inv.keeper, qty=2.0)
    transfer.with_user(inv.keeper).action_submit()
    transfer.with_user(inv.controller).action_approve()
    transfer.with_user(inv.keeper).action_dispatch()
    transfer.with_user(inv.keeper2).action_receive()
    assert inv.events("stock.transfer_received", "fix.stock.transfer", transfer.id) == 1


# ======================================================== B1 serials through the wave
def test_b1_scan_pick_needs_the_serial_and_ship_closes_it(wms):
    w = wms
    lot = _serial_slot(w)
    wave = w.wave(qty=1, part=w.spart, bin_rec=w.bin2)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    scan = {"bin_code": w.bin2.name, "item_code": w.spart.part_number}
    refused(w, lambda: line.with_user(w.operator).action_scan_pick(**scan), "serial")
    refused(
        w,
        lambda: line.with_user(w.operator).action_scan_pick(serial="NEVER-RECEIVED", **scan),
        "never received",
    )
    line.with_user(w.operator).action_scan_pick(serial=lot.name, **scan)
    w.env.invalidate_all()
    assert (lot.status, line.lot_id) == ("staged", lot)
    # staged: nobody issues it
    issue = w.issue(
        w.keeper,
        part=w.spart,
        serial=lot.name,
        scanned_code=w.spart.part_number,
        location=w.central,
    )
    refused(w, lambda: issue.with_user(w.keeper).action_scan_and_consume(), "not in stock")
    _pack_and_load(w, wave)
    wave.with_user(w.operator).action_ship()
    w.env.invalidate_all()
    assert (lot.status, lot.qty) == ("shipped", 0.0)


def test_b1_cancelled_wave_puts_the_serial_back(wms):
    w = wms
    lot = _serial_slot(w)
    wave = w.wave(qty=1, part=w.spart, bin_rec=w.bin2)
    wave.with_user(w.supervisor).action_release()
    wave.line_ids.with_user(w.operator).action_scan_pick(
        bin_code=w.bin2.name, item_code=w.spart.part_number, serial=lot.name
    )
    wave.with_user(w.supervisor).action_cancel(reason="Withdrawn")
    w.env.invalidate_all()
    assert lot.status == "in_stock"


def test_a3_wave_and_receipt_lines_have_a_real_name(wms):
    w = wms
    wave = w.wave(qty=4)
    assert wave.name in wave.line_ids.display_name
    assert w.wpart.part_number in wave.line_ids.display_name
    assert w.grn_line.receipt_id.name in w.grn_line.display_name
