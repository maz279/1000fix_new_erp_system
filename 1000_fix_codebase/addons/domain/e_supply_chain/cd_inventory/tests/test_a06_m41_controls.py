# A06 remediation - M41 Warehouse Management: one test per gap probe of
# working/A06_evidence/probes/m41/probe_m41.py (named after the probe id),
# run as NON-ADMIN Warehouse Operators / Inventory Controllers, plus the
# proper path (R1): the warehouse moves the M15 ledger, never a label.
from datetime import datetime

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (UserError, AccessError, ValidationError, IntegrityError)
GUARD = "changes only through its workflow"


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _complete(w, putaway, user=None):
    """The operative confirms a put-away by scanning the bin and the item."""
    return putaway.with_user(user or w.operator).action_complete(
        bin_code=putaway.to_bin_id.name, item_code=putaway.part_id.part_number
    )


@pytest.fixture
def wms(inv):
    env = inv.env
    w = inv
    w.wh = env["fix.warehouse"].create(
        {
            "name": "A06 WH " + inv.tag,
            "code": inv.tag[:6],
            "operating_unit_id": inv.ou.id,
            "stock_location_id": inv.central.id,
            "wms_enabled": True,
        }
    )
    Zone = env["fix.warehouse.zone"]
    w.zone = Zone.create(
        {"warehouse_id": w.wh.id, "name": "Pick", "code": "PK", "zone_type": "storage"}
    )
    w.qzone = Zone.create(
        {"warehouse_id": w.wh.id, "name": "Quarantine", "code": "QT", "zone_type": "quarantine"}
    )
    w.izone = Zone.create(
        {"warehouse_id": w.wh.id, "name": "Inspection", "code": "QC", "zone_type": "inspection"}
    )
    # A06 ERP audit O7 / F16: floor work is an operative's of THIS warehouse
    w.profile = env["fix.wms.operative"].create(
        {"employee_id": w.op_emp.id, "warehouse_id": w.wh.id}
    )
    Bin = env["fix.warehouse.bin"]
    w.bin = Bin.create({"zone_id": w.zone.id, "name": "A-01-" + inv.tag, "capacity_qty": 10})
    w.bin2 = Bin.create({"zone_id": w.zone.id, "name": "A-02-" + inv.tag, "capacity_qty": 100})
    w.hbin = Bin.create(
        {
            "zone_id": w.zone.id,
            "name": "H-01-" + inv.tag,
            "capacity_qty": 10,
            "storage_class": "hazardous",
        }
    )
    w.qbin = Bin.create({"zone_id": w.qzone.id, "name": "Q-01-" + inv.tag, "capacity_qty": 10})
    w.ibin = Bin.create({"zone_id": w.izone.id, "name": "I-01-" + inv.tag, "capacity_qty": 10})
    w.wpart = env["fix.spare.part"].create(
        {"name": "A06 WMS part", "part_number": "A6M-" + inv.tag, "unit_cost": 50.0}
    )
    w.part0 = env["fix.spare.part"].create({"name": "A06 zero", "part_number": "A60-" + inv.tag})
    # 100 received at the warehouse's M15 location (central)
    rec = env["fix.stock.receipt"].create(
        {
            "partner_id": inv.supplier.id,
            "location_id": inv.central.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": w.wpart.id,
                        "qty_received": 100,
                        "qty_accepted": 100,
                        "unit_cost": 50,
                    },
                )
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    w.grn_line = rec.line_ids
    # 10 put away into bin A by an operator
    pa = w.putaway(w.operator, qty=10, bin_rec=w.bin)
    _complete(w, pa)
    w.slot = env["fix.wms.slot"]._slot_for(w.wpart, w.bin)
    return w


def _pack_and_load(w, wave, user=None):
    user = user or w.operator
    picked = int(sum(wave.line_ids.mapped("picked_qty")))
    carton = (
        w.env["fix.wms.carton"]
        .with_user(user)
        .create({"wave_id": wave.id, "contents_qty": picked, "weight_kg": 1.5})
    )
    carton.with_user(user).action_seal()
    wave.with_user(user).action_packed()
    stage = w.env["fix.wms.stage"].with_user(user).create({"wave_id": wave.id, "lane": "L1"})
    wave.with_user(user).action_stage()
    stage.with_user(user).write({"load_ref": "TRUCK-DHK-11"})
    stage.with_user(user).action_load(carton_scans=carton.name)
    return carton, stage


def _doc_wave(w, qty=4):
    """A06 ERP audit F01 / O1: a wave ships only stock an M15 document moves.
    An approved transfer central -> hub queues its demand; the wave is built
    from it (the transfer is dispatched by the wave's shipment)."""
    tr = (
        w.env["fix.stock.transfer"]
        .with_user(w.keeper)
        .create(
            {
                "from_location_id": w.central.id,
                "to_location_id": w.hub.id,
                "operating_unit_id": w.ou.id,
                "line_ids": [(0, 0, {"part_id": w.wpart.id, "qty": qty})],
            }
        )
    )
    tr.with_user(w.keeper).action_submit()
    if tr.state == "submitted":
        tr.with_user(w.controller).action_approve()
    demand = w.env["fix.wms.outbound.demand"].search([("transfer_id", "=", tr.id)])
    return w.env["fix.wms.wave"].browse(demand.with_user(w.operator).action_build_wave())


def _ship(w, wave, user=None):
    user = user or w.operator
    wave.with_user(w.supervisor).action_release()
    for line in wave.line_ids:
        line.with_user(user).action_scan_pick(line.bin_id.name, line.part_id.part_number)
    carton, stage = _pack_and_load(w, wave, user)
    wave.with_user(user).action_ship()
    return carton, stage


# ===================================================== reference run
def test_m41_00_reference_full_wave_moves_m15(wms):
    w = wms
    assert w.slot.qty == 10 and w.qty(w.wpart, w.central) == 100
    wave = _doc_wave(w, qty=4)
    carton, stage = _ship(w, wave)
    assert (wave.state, wave.line_ids.state, carton.state, stage.state) == (
        "shipped",
        "handed",
        "dispatched",
        "dispatched",
    )
    assert w.slot.qty == 6
    assert w.qty(w.wpart, w.central) == 96  # the transfer took the shipped units
    assert w.qty(w.wpart, w.central, status="in_transit") == 4  # BRU-INV-16
    assert w.qty(w.wpart, w.central, status="staged") == 0
    assert w.wpart.qty_reserved == 0
    assert w.events("wh.shipped", "fix.wms.wave", wave.id) == 1
    assert wave.demand_ids.transfer_id.state == "dispatched"
    # F01: M41 books no write-off of its own (it was a "shipment" suspense row)
    assert not w.suspense(wave.name, "shipment")


# ===================================================== put-away and bin rules
def test_m41_01_putaway_over_capacity_refused(wms):
    pa = wms.putaway(wms.operator, qty=50)
    refused(wms, lambda: _complete(wms, pa), "holds at most")
    assert wms.slot.qty == 10


def test_m41_02_quarantine_zone_not_filled_or_picked(wms):
    pa = wms.putaway(wms.operator, qty=5, bin_rec=wms.qbin)
    refused(wms, lambda: _complete(wms, pa), "not reservable")
    wms.env["fix.wms.slot"].create({"part_id": wms.wpart.id, "bin_id": wms.qbin.id, "qty": 5})
    wave = wms.wave(qty=5, bin_rec=wms.qbin)
    refused(wms, lambda: wave.with_user(wms.supervisor).action_release(), "not reservable")


def test_m41_03_inspection_zone_not_picked(wms):
    wms.env["fix.wms.slot"].create({"part_id": wms.wpart.id, "bin_id": wms.ibin.id, "qty": 3})
    wave = wms.wave(qty=3, bin_rec=wms.ibin)
    refused(wms, lambda: wave.with_user(wms.supervisor).action_release(), "inspection")
    assert wave.state == "draft"


def test_m41_04_blocked_slot_not_filled(wms):
    wms.slot.with_user(wms.supervisor).action_block("racking damaged")
    pa = wms.putaway(wms.operator, qty=2)
    refused(wms, lambda: _complete(wms, pa), "blocked")
    assert wms.slot.qty == 10


def test_m41_05_blocked_slot_not_picked_and_unblock_by_another_controller(wms):
    wms.slot.with_user(wms.controller).action_block("cycle count")
    wave = wms.wave(qty=4)
    refused(wms, lambda: wave.with_user(wms.supervisor).action_release(), "blocked")
    refused(wms, lambda: wms.slot.with_user(wms.operator).action_unblock())
    refused(wms, lambda: wms.slot.with_user(wms.controller).action_unblock(), "Segregation")
    wms.slot.with_user(wms.controller2).action_unblock("counted, fine")
    wave.with_user(wms.supervisor).action_release()
    assert wave.state == "released"


def test_m41_06_putaway_only_of_received_stock(wms):
    pa = wms.putaway(
        wms.operator,
        qty=500,
        part=wms.part0,
        bin_rec=wms.bin2,
        line=wms.env["fix.stock.receipt.line"],
    )
    refused(wms, lambda: _complete(wms, pa), "POSTED goods-receipt")
    assert not wms.env["fix.wms.slot"]._slot_for(wms.part0, wms.bin2)


def test_m41_07_putaway_never_exceeds_what_was_received(wms):
    first = wms.putaway(wms.operator, qty=90, bin_rec=wms.bin2)
    _complete(wms, first)  # 10 + 90 = the 100 received
    second = wms.putaway(wms.operator, qty=1, bin_rec=wms.bin2)
    refused(wms, lambda: _complete(wms, second), "remains to be put away")
    slots = wms.env["fix.wms.slot"].search([("part_id", "=", wms.wpart.id)])
    assert sum(slots.mapped("qty")) == wms.qty(wms.wpart, wms.central) == 100


def test_m41_08_slot_qty_not_writable(wms):
    refused(wms, lambda: wms.slot.with_user(wms.operator).write({"qty": 999}), GUARD)
    refused(
        wms,
        lambda: (
            wms.env["fix.wms.slot"]
            .with_user(wms.operator)
            .create({"part_id": wms.wpart.id, "bin_id": wms.bin2.id, "qty": 990})
        ),
        GUARD,
    )
    assert wms.slot.qty == 10


def test_m41_09_slot_qty_not_writable_via_p03(wms):
    res = wms.p03(wms.operator).write(
        model="fix.wms.slot", record_id=wms.slot.id, values={"qty": 777}
    )
    assert "error" in res and wms.slot.qty == 10


def test_m41_10_serial_and_hazard_rules(wms):
    env = wms.env
    battery = env["fix.spare.part"].create(
        {
            "name": "Li-ion",
            "part_number": "A6L-" + wms.tag,
            "part_category": "battery",
            "is_serialized": True,
        }
    )
    assert battery.storage_class == "hazardous"
    rec = env["fix.stock.receipt"].create(
        {
            "partner_id": wms.supplier.id,
            "location_id": wms.central.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": battery.id,
                        "qty_received": 1,
                        "qty_accepted": 1,
                        "unit_cost": 900,
                        "line_no": "BAT-" + wms.tag,
                    },
                )
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    line = rec.line_ids
    no_serial = wms.putaway(wms.operator, qty=1, part=battery, bin_rec=wms.hbin, line=line)
    refused(wms, lambda: _complete(wms, no_serial), "serial")
    plain_bin = wms.putaway(
        wms.operator, qty=1, part=battery, bin_rec=wms.bin2, line=line, lot_id=line.lot_id.id
    )
    refused(wms, lambda: _complete(wms, plain_bin), "hazardous")
    ok = wms.putaway(
        wms.operator, qty=1, part=battery, bin_rec=wms.hbin, line=line, lot_id=line.lot_id.id
    )
    _complete(wms, ok)
    assert env["fix.wms.slot"]._slot_for(battery, wms.hbin).qty == 1


def test_m41_11_putaway_reaches_the_event_log(wms):
    pa = wms.putaway(wms.operator, qty=3, bin_rec=wms.bin2)
    _complete(wms, pa)
    assert wms.events("wh.putaway_completed", "fix.wms.putaway", pa.id) == 1
    assert pa.done_by_id == wms.operator


# ===================================================== dock
def _dock(wms, **kw):
    vals = {
        "dock_no": "D1-" + wms.tag,
        "slot_start": datetime(2026, 11, 5, 9),
        "slot_end": datetime(2026, 11, 5, 10),
    }
    vals.update(kw)
    return wms.env["fix.wms.dock"].with_user(wms.operator).create(vals)


def test_m41_12_dock_state_not_writable(wms):
    dock = _dock(wms)
    refused(wms, lambda: dock.with_user(wms.operator).write({"state": "completed"}), GUARD)


def test_m41_13_dock_not_double_booked(wms):
    _dock(wms, slot_end=datetime(2026, 11, 5, 11))
    refused(
        wms,
        lambda: _dock(
            wms, slot_start=datetime(2026, 11, 5, 10), slot_end=datetime(2026, 11, 5, 12)
        ),
        "already booked",
    )
    _dock(wms, slot_start=datetime(2026, 11, 5, 11), slot_end=datetime(2026, 11, 5, 12))


def test_m41_14_inbound_dock_completes_with_its_receipt(wms):
    dock = _dock(wms)
    dock.with_user(wms.operator).action_check_in()
    refused(wms, lambda: dock.with_user(wms.operator).action_complete(), "goods receipt")
    dock.with_user(wms.operator).write({"receipt_id": wms.grn_line.receipt_id.id})
    dock.with_user(wms.operator).action_complete()
    assert dock.state == "completed"


# ===================================================== release / allocation
def test_m41_15_release_allocates_in_m15(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    assert wms.wpart.qty_reserved == 4
    assert wms.bucket(wms.wpart, wms.central).reserved == 4
    assert (wms.slot.reserved_qty, wave.line_ids.reserved_qty) == (4, 4)


def test_m41_16_release_refused_without_stock(wms):
    wave = wms.wave(qty=50, part=wms.part0, bin_rec=wms.bin2)
    refused(wms, lambda: wave.with_user(wms.supervisor).action_release(), "holds no")
    assert wave.state == "draft"


def test_m41_17_pick_bounded_by_the_bin(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    # the bin physically holds less than was allocated (found at the pick face)
    wms.slot._guarded().sudo().write({"qty": 2, "reserved_qty": 2})
    wave.line_ids._guarded().sudo().write({"reserved_qty": 2})
    wms.env["fix.stock.onhand"]._fix_unreserve(wms.wpart, wms.central, "owned", 2, "test")
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    line = wave.line_ids
    assert (line.picked_qty, line.state, wms.slot.qty) == (2, "short", 0)
    assert wms.qty(wms.wpart, wms.central, status="staged") == 2
    assert wms.wpart.qty_reserved == 0


def test_m41_18_pick_all_is_idempotent(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    assert (wave.line_ids.picked_qty, wms.slot.qty) == (4, 6)
    assert wms.qty(wms.wpart, wms.central, status="staged") == 4


def test_m41_19_over_allocation_refused(wms):
    first, second = wms.wave(qty=8), wms.wave(qty=8)
    first.with_user(wms.supervisor).action_release()
    refused(wms, lambda: second.with_user(wms.supervisor).action_release(), "over-allocation")
    assert second.state == "draft"


def test_m41_20_picked_qty_bounded(wms):
    wave = wms.wave(qty=4)
    refused(wms, lambda: wave.line_ids.with_user(wms.operator).write({"picked_qty": 9}), GUARD)
    with pytest.raises(IntegrityError), wms.env.cr.savepoint():
        wave.line_ids.sudo().write({"picked_qty": 9})
        wave.line_ids.flush_recordset()


def test_m41_21_pick_evidence_not_typed(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    refused(
        wms,
        lambda: wave.line_ids.with_user(wms.operator).write({"picked_qty": 4, "state": "picked"}),
        "final|workflow",
    )
    refused(wms, lambda: wave.with_user(wms.operator).action_packed(), "Pack a picked wave")


def test_m41_22_ship_decrements_m15(wms):
    wave = _doc_wave(wms, qty=4)
    _ship(wms, wave)
    assert wms.qty(wms.wpart, wms.central) == 96 and wms.wpart.qty_reserved == 0


def test_m41_23_short_pick_raises_count_back(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    wms.slot._guarded().sudo().write({"qty": 1, "reserved_qty": 1})
    wave.line_ids._guarded().sudo().write({"reserved_qty": 1})
    wms.env["fix.stock.onhand"]._fix_unreserve(wms.wpart, wms.central, "owned", 3, "test")
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    tasks = wms.env["fix.wms.task"].search(
        [("task_type", "=", "count"), ("bin_id", "=", wms.bin.id)]
    )
    assert tasks and "Count-back" in tasks[0].ref
    # the short line is closed at what was picked, then the wave packs
    wave.with_user(wms.operator).action_accept_short()
    assert (wave.line_ids.qty, wave.line_ids.state) == (1, "picked")


def test_m41_24_zero_crossing_raises_count(wms):
    wave = wms.wave(qty=10)
    wave.with_user(wms.supervisor).action_release()
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    assert wms.slot.qty == 0
    tasks = wms.env["fix.wms.task"].search(
        [("task_type", "=", "count"), ("bin_id", "=", wms.bin.id)]
    )
    assert tasks and "Zero-crossing" in tasks[0].ref


def test_m41_25_wave_state_not_writable(wms):
    wave = wms.env["fix.wms.wave"].with_user(wms.operator).create({})
    refused(wms, lambda: wave.with_user(wms.operator).write({"state": "shipped"}), GUARD)


def test_m41_26_wave_state_not_writable_via_p03(wms):
    wave = wms.env["fix.wms.wave"].with_user(wms.operator).create({})
    assert "error" in wms.p03(wms.operator).write(
        model="fix.wms.wave", record_id=wave.id, values={"state": "shipped"}
    )
    assert wave.state == "draft"


def test_m41_27_wave_cannot_be_born_shipped(wms):
    refused(
        wms,
        lambda: wms.env["fix.wms.wave"].with_user(wms.operator).create({"state": "shipped"}),
        GUARD,
    )
    refused(
        wms,
        lambda: (
            wms.env["fix.wms.wave"]
            .with_user(wms.operator)
            .create(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "part_id": wms.wpart.id,
                                "bin_id": wms.bin.id,
                                "qty": 5,
                                "picked_qty": 5,
                                "state": "picked",
                            },
                        )
                    ]
                }
            )
        ),
        GUARD,
    )


def test_m41_28_pack_needs_sealed_cartons(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    refused(wms, lambda: wave.with_user(wms.operator).action_packed(), "sealed cartons")


def test_m41_29_ship_needs_a_loaded_stage(wms):
    wave = _doc_wave(wms, qty=4)
    wave.with_user(wms.supervisor).action_release()
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    carton = (
        wms.env["fix.wms.carton"]
        .with_user(wms.operator)
        .create({"wave_id": wave.id, "contents_qty": 4, "weight_kg": 1})
    )
    carton.with_user(wms.operator).action_seal()
    wave.with_user(wms.operator).action_packed()
    refused(wms, lambda: wave.with_user(wms.operator).action_stage(), "staging record")
    stage = (
        wms.env["fix.wms.stage"].with_user(wms.operator).create({"wave_id": wave.id, "lane": "L2"})
    )
    wave.with_user(wms.operator).action_stage()
    refused(wms, lambda: wave.with_user(wms.operator).action_ship(), "LOADED")
    refused(wms, lambda: stage.with_user(wms.operator).action_load(), "load / vehicle")
    stage.with_user(wms.operator).write({"load_ref": "TRUCK-1"})
    stage.with_user(wms.operator).action_load(carton_scans=carton.name)
    stage.with_user(wms.operator).action_dispatch()  # dispatching the load ships the wave
    assert (wave.state, stage.state) == ("shipped", "dispatched")


def test_m41_30_ship_publishes_wh_shipped(wms):
    wave = _doc_wave(wms, qty=4)
    _ship(wms, wave)
    event = (
        wms.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "wh.shipped"), ("aggregate_id", "=", wave.id)])
    )
    assert len(event) == 1 and "TRUCK-DHK-11" in event.payload


def test_m41_31_shipped_lines_final(wms):
    wave = _doc_wave(wms, qty=4)
    _ship(wms, wave)
    refused(
        wms,
        lambda: wave.line_ids.with_user(wms.operator).write({"qty": 400, "part_id": wms.part0.id}),
        "final",
    )
    assert wave.line_ids.qty == 4


def test_m41_32_no_line_added_after_release(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    refused(
        wms,
        lambda: (
            wms.env["fix.wms.wave.line"]
            .with_user(wms.operator)
            .create({"wave_id": wave.id, "part_id": wms.wpart.id, "bin_id": wms.bin.id, "qty": 6})
        ),
        "final",
    )


def test_m41_33_picked_line_not_deleted(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    refused(wms, lambda: wave.line_ids.with_user(wms.operator).unlink(), "final")
    assert wave.line_ids


def test_m41_34_empty_carton_not_sealed(wms):
    carton = wms.env["fix.wms.carton"].with_user(wms.operator).create({})
    refused(wms, lambda: carton.with_user(wms.operator).action_seal(), "wave")


def test_m41_35_carton_reconciles_to_picks(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    wave.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    carton = (
        wms.env["fix.wms.carton"]
        .with_user(wms.operator)
        .create({"wave_id": wave.id, "contents_qty": 500, "weight_kg": 0.1})
    )
    refused(wms, lambda: carton.with_user(wms.operator).action_seal(), "reconcile")


def test_m41_36_carton_state_not_writable(wms):
    carton = wms.env["fix.wms.carton"].with_user(wms.operator).create({})
    refused(wms, lambda: carton.with_user(wms.operator).write({"state": "dispatched"}), GUARD)


def test_m41_37_stage_only_for_a_staged_wave(wms):
    wave = wms.wave(qty=4)  # draft
    stage = (
        wms.env["fix.wms.stage"]
        .with_user(wms.operator)
        .create({"wave_id": wave.id, "lane": "L1", "load_ref": "T"})
    )
    refused(wms, lambda: stage.with_user(wms.operator).action_load(), "staged wave")
    refused(wms, lambda: stage.with_user(wms.operator).action_dispatch(), "loaded")


# ===================================================== tasks
def test_m41_38_unassigned_task_not_done(wms):
    task = wms.env["fix.wms.task"].with_user(wms.operator).create({"task_type": "pick"})
    refused(wms, lambda: task.with_user(wms.operator).action_done(), "assigned task")


def test_m41_39_pick_task_moves_the_stock(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    task = (
        wms.env["fix.wms.task"]
        .with_user(wms.operator)
        .create(
            {"task_type": "pick", "wave_line_id": wave.line_ids.id, "assignee_id": wms.op_emp.id}
        )
    )
    task.with_user(wms.operator).action_assign()
    # BRU-WMS-05: the RF pick needs the bin and the item scanned
    refused(wms, lambda: task.with_user(wms.operator).action_done(), "Scanned bin")
    refused(
        wms,
        lambda: task.with_user(wms.operator).action_done(scan="%s WRONG-ITEM" % wms.bin.name),
        "Scanned item",
    )
    task.with_user(wms.operator).action_done(scan="%s %s" % (wms.bin.name, wms.wpart.part_number))
    assert wms.slot.qty == 6 and wave.line_ids.state == "picked"
    assert (wave.line_ids.scanned_bin, wave.line_ids.scanned_item) == (
        wms.bin.name,
        wms.wpart.part_number,
    )
    assert wms.qty(wms.wpart, wms.central, status="staged") == 4
    free = (
        wms.env["fix.wms.task"]
        .with_user(wms.operator)
        .create(
            {
                "task_type": "pick",
                "part_id": wms.wpart.id,
                "bin_id": wms.bin.id,
                "qty": 4,
                "assignee_id": wms.op_emp.id,
            }
        )
    )
    free.with_user(wms.operator).action_assign()
    refused(wms, lambda: free.with_user(wms.operator).action_done(), "wave line")


def test_m41_40_done_task_not_reopened(wms):
    task = (
        wms.env["fix.wms.task"]
        .with_user(wms.operator)
        .create({"task_type": "replenish", "assignee_id": wms.op_emp.id})
    )
    task.with_user(wms.operator).action_assign()
    task.with_user(wms.operator).action_done()
    refused(wms, lambda: task.with_user(wms.operator).action_assign(), "open task")
    assert task.state == "done"


def test_m41_41_only_the_assignee_completes(wms):
    task = (
        wms.env["fix.wms.task"]
        .with_user(wms.operator)
        .create({"task_type": "replenish", "assignee_id": wms.op_emp.id})
    )
    task.with_user(wms.operator).action_assign()
    refused(wms, lambda: task.with_user(wms.operator2).action_done(), "only that operative")
    task.with_user(wms.operator).action_done()
    assert task.done_by_id == wms.operator


def test_m41_42_task_state_not_writable(wms):
    task = (
        wms.env["fix.wms.task"].with_user(wms.operator).create({"task_type": "pick", "qty": 1000})
    )
    refused(
        wms,
        lambda: task.with_user(wms.operator).write(
            {"state": "done", "done_at": "2026-11-03 08:00:00"}
        ),
        GUARD,
    )


def test_m41_43_task_state_not_writable_via_p03(wms):
    task = wms.env["fix.wms.task"].with_user(wms.operator).create({"task_type": "pick"})
    res = wms.p03(wms.operator).write(
        model="fix.wms.task", record_id=task.id, values={"state": "done"}
    )
    assert "error" in res and task.state == "open"


# ===================================================== floor counts
def _floor(wms, counted, user=None):
    return (
        wms.env["fix.wms.floor.count"]
        .with_user(user or wms.operator)
        .create({"bin_id": wms.bin.id, "part_id": wms.wpart.id, "counted_qty": counted})
    )


def test_m41_44_floor_variance_goes_to_m15_for_approval(wms):
    fc = _floor(wms, 7)
    fc.with_user(wms.operator).action_post()
    assert fc.sudo().expected_qty == 10  # F13: the supervisor's to read, not the counter's
    assert fc.state == "recount"
    refused(wms, lambda: fc.with_user(wms.operator).action_post(), "reason")
    fc.with_user(wms.operator).write({"reason_code": "loss"})
    fc.with_user(wms.operator).action_post()
    count = fc.stock_count_id
    assert fc.state == "submitted" and count.state == "to_approve"
    assert wms.qty(wms.wpart, wms.central) == 100 and wms.slot.qty == 10
    refused(wms, lambda: count.with_user(wms.operator).action_approve())
    count.with_user(wms.controller).action_approve()
    assert count.state == "posted" and fc.state == "posted"
    assert wms.qty(wms.wpart, wms.central) == 97 and wms.slot.qty == 7


def test_m41_44b_floor_counter_cannot_approve_the_m15_count(wms):
    fc = _floor(wms, 9, user=wms.controller)
    fc.with_user(wms.controller).action_post()
    fc.with_user(wms.controller).write({"reason_code": "damage"})
    fc.with_user(wms.controller).action_post()
    refused(
        wms, lambda: fc.stock_count_id.with_user(wms.controller).action_approve(), "Segregation"
    )


def test_m41_45_floor_expected_not_typed(wms):
    fc = (
        wms.env["fix.wms.floor.count"]
        .with_user(wms.operator)
        .create(
            {"bin_id": wms.bin.id, "part_id": wms.wpart.id, "expected_qty": 7, "counted_qty": 7}
        )
    )
    fc.with_user(wms.operator).action_post()
    assert (fc.sudo().expected_qty, fc.sudo().variance) == (10, -3)
    # F13: the counter can neither read nor type it
    refused(wms, lambda: fc.with_user(wms.operator).write({"expected_qty": 7}))


def test_m41_46_submitted_floor_count_final(wms):
    fc = _floor(wms, 10)
    fc.with_user(wms.operator).action_post()
    assert fc.state == "posted"
    refused(wms, lambda: fc.with_user(wms.operator).write({"counted_qty": 7}), "final")


def test_m41_47_floor_state_not_writable_via_p03(wms):
    fc = _floor(wms, 7)
    res = wms.p03(wms.operator).write(
        model="fix.wms.floor.count", record_id=fc.id, values={"state": "posted"}
    )
    assert "error" in res and fc.state == "draft"


# ===================================================== M15 records on the M41 surface
def test_m41_48_m41_surface_does_not_write_m15_on_hand(wms):
    res = wms.p03(wms.operator).write(
        model="fix.spare.part",
        record_id=wms.wpart.id,
        values={"qty_available": 5000, "qty_reserved": 0},
    )
    assert "error" in res
    res = wms.p03(wms.keeper).write(
        model="fix.spare.part", record_id=wms.wpart.id, values={"qty_available": 5000}
    )
    assert "error" in res and wms.wpart.qty_available == 100


def test_m41_49_suspense_not_reconciled_via_p03(wms):
    entry = wms.suspense(wms.grn_line.receipt_id.name, "receipt")
    res = wms.p03(wms.keeper).write(
        model="fix.inventory.valuation.suspense",
        record_id=entry.id,
        values={"status": "reconciled", "total_valuation": 0},
    )
    assert "error" in res and entry.status == "pending_gl_cutover"


def test_m41_50_action_path_keeps_transition_order(wms):
    wave = wms.wave(qty=4)
    out = wms.p03(wms.operator).action(model="fix.wms.wave", ids=[wave.id], method="action_ship")
    assert out.get("success") is False and wave.state == "draft"


def test_m41_51_every_surface_has_a_whitelist(wms):
    from odoo.addons.cd_p03_portal.controllers import form_fields
    from odoo.addons.cd_p03_portal.controllers.a06 import m41

    offered = form_fields.editable_by_model()
    for model, conf in m41.SURFACES.items():
        assert conf.get("writable") is not None, model
        guarded_fn = getattr(wms.env[model].browse(), "_fix_guarded_fields", None)
        if guarded_fn:
            assert not guarded_fn() & offered.get(model, set()), model


def test_m41_52_m41_models_guarded_and_role_bound(wms):
    for model in (
        "fix.wms.slot",
        "fix.wms.dock",
        "fix.wms.putaway",
        "fix.wms.wave",
        "fix.wms.wave.line",
        "fix.wms.carton",
        "fix.wms.stage",
        "fix.wms.task",
        "fix.wms.floor.count",
    ):
        assert wms.env[model].browse()._fix_guarded_fields(), model
        assert not wms.env[model].with_user(wms.clerk).has_access("create"), model
        assert wms.env[model].with_user(wms.operator).has_access("create"), model
    for model in ("fix.warehouse", "fix.warehouse.zone", "fix.warehouse.bin"):
        assert not wms.env[model].with_user(wms.clerk).has_access("write"), model


# ===================================================== KPI truth
def test_m41_53_labour_kpi_counts_executed_tasks_only(wms):
    from odoo.addons.cd_p03_portal.controllers.a06 import m41

    forged = wms.env["fix.wms.task"].create(
        {"task_type": "pick", "qty": 1000, "assignee_id": wms.op_emp.id}
    )
    forged.write({"state": "done", "done_at": "2026-11-03 08:00:00"})  # su: no operative recorded
    rows = m41.labour_productivity(wms.env(user=wms.operator.id))["rows"]
    assert not [r for r in rows if r["assignee"] == wms.op_emp.name]
    # A06 ERP audit F27: only work that moved something counts: a real move
    move = (
        wms.env["fix.wms.move"]
        .with_user(wms.operator)
        .create(
            {
                "part_id": wms.wpart.id,
                "from_bin_id": wms.bin.id,
                "to_bin_id": wms.bin2.id,
                "qty": 3,
                "reason_code": "wrong_bin",
                "assignee_id": wms.op_emp.id,
            }
        )
    )
    task = move.task_id
    task.with_user(wms.operator).action_assign()
    task.with_user(wms.operator).action_done(
        scan="%s %s %s" % (wms.bin.name, wms.bin2.name, wms.wpart.part_number)
    )
    rows = m41.labour_productivity(wms.env(user=wms.operator.id))["rows"]
    assert next(r for r in rows if r["assignee"] == wms.op_emp.name)["qty"] == 3


def test_m41_54_pick_accuracy_from_executed_picks_only(wms):
    from odoo.addons.cd_p03_portal.controllers.a06 import m41

    typed = wms.wave(qty=50, bin_rec=wms.bin2)
    typed.line_ids.sudo().write(
        {"picked_qty": 50, "state": "picked"}
    )  # su, never picked by the wave
    picked = wms.wave(qty=4)
    picked.with_user(wms.supervisor).action_release()
    picked.with_user(wms.supervisor).action_pick_all(reason="Scanner down")
    rows = m41.pick_accuracy(wms.env(user=wms.operator.id))["rows"]
    assert not [r for r in rows if r["wave"] == typed.name]
    assert next(r for r in rows if r["wave"] == picked.name)["accuracy_pct"] == 100.0


def test_m41_55_dock_default_window_is_valid(wms):
    dock = wms.env["fix.wms.dock"].with_user(wms.operator).create({"dock_no": "D9-" + wms.tag})
    dock.flush_recordset()
    assert dock.slot_end > dock.slot_start


def test_m41_04b_bin_ownership_class_enforced_at_putaway(wms):
    wms.bin2.write({"ownership_class": "consignment"})
    pa = wms.putaway(wms.operator, qty=2, bin_rec=wms.bin2)
    refused(wms, lambda: _complete(wms, pa), "BRU-WMS-03")
    wms.bin2.write({"ownership_class": "owned"})
    _complete(wms, pa)
    assert wms.env["fix.wms.slot"]._slot_for(wms.wpart, wms.bin2).qty == 2


def test_m41_21b_scan_pick_evidence(wms):
    wave = wms.wave(qty=4)
    wave.with_user(wms.supervisor).action_release()
    line = wave.line_ids
    refused(
        wms,
        lambda: line.with_user(wms.operator).action_scan_pick("OTHER-BIN", wms.wpart.part_number),
        "Scanned bin",
    )
    line.with_user(wms.operator).action_scan_pick(wms.bin.name, wms.wpart.part_number)
    assert (line.state, line.picked_qty, line.picked_by_id) == ("picked", 4, wms.operator)
    refused(
        wms, lambda: line.with_user(wms.operator).write({"scanned_bin": "forged"}), "final|workflow"
    )
