# M41 capture pass 2 (2026-11-19) - the spec records the pass-1 buttons could
# not hold, exercised on the live ORM as NON-ADMIN users holding the real roles.
# Each test runs the proper path and the control the spec names.
import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

from . import test_a06_m41_controls as base

wms = base.wms
REFUSED = (UserError, AccessError, ValidationError, IntegrityError)


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _slot(w, bin_rec, part=None):
    return w.env["fix.wms.slot"]._slot_for(part or w.wpart, bin_rec)


def _new_putaway(w, user, qty, **kw):
    vals = {"part_id": w.wpart.id, "qty": qty, "receipt_line_id": w.grn_line.id}
    vals.update(kw)
    return w.env["fix.wms.putaway"].with_user(user).create(vals)


def _complete(w, pa, user=None):
    pa.with_user(user or w.operator).action_complete(
        bin_code=pa.to_bin_id.name, item_code=w.wpart.part_number
    )


def _receipt(w, qty, part=None):
    rec = w.env["fix.stock.receipt"].create(
        {
            "partner_id": w.supplier.id,
            "location_id": w.central.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": (part or w.wpart).id,
                        "qty_received": qty,
                        "qty_accepted": qty,
                        "unit_cost": 50,
                    },
                )
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    return rec


# ======================================================== page 1 structure
def test_warehouse_execution_is_opt_in_and_a_supervisors_call(wms):
    w = wms
    Wh = w.env["fix.warehouse"]
    branch = Wh.create(
        {"name": "Branch " + w.tag, "code": "B" + w.tag[:5], "operating_unit_id": w.ou.id}
    )
    assert branch.wms_enabled is False  # FR-WMS-003: off unless switched on
    Zone = w.env["fix.warehouse.zone"]
    refused(
        w,
        lambda: Zone.create(
            {"warehouse_id": branch.id, "name": "Z", "code": "Z", "zone_type": "storage"}
        ),
        "does not run warehouse execution",
    )
    refused(w, lambda: branch.with_user(w.operator).write({"wms_enabled": True}), "Supervisor")
    branch.with_user(w.supervisor).write({"wms_enabled": True, "wave_cutoffs": "10:00, 15:30"})
    assert branch.wms_enabled
    refused(
        w, lambda: branch.with_user(w.supervisor).write({"wave_cutoffs": "25:00"}), "not a time"
    )
    # the live warehouse holds stock in a bin: execution cannot be turned off
    refused(
        w, lambda: w.wh.with_user(w.supervisor).write({"wms_enabled": False}), "still holds stock"
    )


def test_bin_coordinates_give_a_serpentine_walk(wms):
    w = wms
    Bin = w.env["fix.warehouse.bin"]

    def mk(aisle, bay):
        return Bin.with_user(w.operator).create(
            {
                "zone_id": w.zone.id,
                "name": "%s-%02d-%s" % (aisle, bay, w.tag),
                "aisle": aisle,
                "bay": bay,
            }
        )

    a1, a5, b1, b5 = mk("A", 1), mk("A", 5), mk("B", 1), mk("B", 5)
    # aisle A walked up, aisle B walked back down
    order = sorted([a1, a5, b1, b5], key=lambda b: b.pick_sequence)
    assert order == [a1, a5, b5, b1]
    refused(w, lambda: a1.write({"level": -1}), "cannot be negative")


def test_a_zone_reserved_for_a_class_takes_no_other_bin(wms):
    w = wms
    cz = w.env["fix.warehouse.zone"].create(
        {
            "warehouse_id": w.wh.id,
            "name": "Brand cage",
            "code": "BC",
            "zone_type": "secure",
            "ownership_class": "consignment",
        }
    )
    Bin = w.env["fix.warehouse.bin"]
    refused(w, lambda: Bin.create({"zone_id": cz.id, "name": "BC-1-" + w.tag}), "T-02")
    ok = Bin.create({"zone_id": cz.id, "name": "BC-2-" + w.tag, "ownership_class": "consignment"})
    assert ok.zone_id.ownership_class == "consignment"


def test_bin_weight_limit_holds(wms):
    w = wms
    product = w.env["product.product"].create({"name": "Heavy " + w.tag, "weight": 3.0})
    w.wpart.write({"product_id": product.id})
    w.bin2.write({"max_weight_kg": 10.0})
    pa = _new_putaway(w, w.operator, 4)
    assert pa.directed_bin_id != w.bin2  # 12 kg: rejected for weight
    assert any("weight" in r["why"] for r in json.loads(pa.rejected_bins))
    refused(
        w,
        lambda: w.env["fix.wms.slot"]
        ._slot_for(w.wpart, w.bin2, create=True)
        ._guarded()
        .write({"qty": 4}),
        "kg",
    )


def test_block_and_unblock_leave_a_history(wms):
    w = wms
    w.bin2.with_user(w.supervisor).action_block("rack bent")
    w.bin2.with_user(w.controller).action_unblock(note="rack replaced")
    log = w.env["fix.wms.bin.block.log"].search([("bin_id", "=", w.bin2.id)])
    assert sorted(log.mapped("event")) == ["block", "unblock"]
    assert set(log.mapped("user_id")) == {w.supervisor, w.controller}
    refused(w, lambda: log[:1].with_user(w.controller).write({"reason": "x"}), "append-only")
    refused(
        w,
        lambda: w.env["fix.wms.bin.block.log"]
        .with_user(w.operator)
        .create({"bin_id": w.bin2.id, "event": "block", "reason": "x", "user_id": w.operator.id}),
    )


# ======================================================== page 3 directed put-away
def test_the_system_directs_the_bin_and_says_why(wms):
    w = wms
    pa = _new_putaway(w, w.operator, 5)
    # bin A, the part's pick face, already holds its 10 (capacity 10): the
    # fixed bin is refused and the next empty bin of the pick zone is directed
    assert pa.to_bin_id == pa.directed_bin_id == w.bin2
    assert pa.strategy_used == "near_pick"
    rejected = json.loads(pa.rejected_bins)
    assert {"bin": w.bin.name, "strategy": "fixed", "why": "full (10.0 of 10.0)"} in rejected
    _complete(w, pa)
    assert _slot(w, w.bin2).qty == 5
    # bin 2 is now a pick face of the part with room: the fixed-bin strategy
    pa2 = _new_putaway(w, w.operator, 3)
    assert (pa2.directed_bin_id, pa2.strategy_used) == (w.bin2, "fixed")


def test_another_bin_is_an_override_a_second_supervisor_approves(wms):
    w = wms
    pa = _new_putaway(w, w.operator, 2)
    assert pa.directed_bin_id == w.bin2
    refused(w, lambda: pa.with_user(w.operator).write({"to_bin_id": w.hbin.id}), "override reason")
    pa.with_user(w.operator).write({"to_bin_id": w.hbin.id, "override_reason": "closer"})
    assert (pa.override_state, pa.override_by_id) == ("pending", w.operator)
    refused(w, lambda: _complete(w, pa), "approves the override")
    refused(w, lambda: pa.with_user(w.operator).action_approve_override(), "Supervisor")
    pa.with_user(w.supervisor).action_approve_override()
    assert (pa.override_state, pa.override_approved_by_id) == ("approved", w.supervisor)
    assert w.events("wh.directive_overridden", "fix.wms.putaway", pa.id)
    _complete(w, pa)
    assert _slot(w, w.hbin).qty == 2
    # nobody approves their own override (spec section 13)
    pa2 = _new_putaway(w, w.supervisor, 1)
    assert pa2.directed_bin_id != w.bin2
    pa2.with_user(w.supervisor).write({"to_bin_id": w.bin2.id, "override_reason": "other"})
    refused(w, lambda: pa2.with_user(w.supervisor).action_approve_override(), "another supervisor")


def test_override_state_is_never_typed(wms):
    w = wms
    pa = _new_putaway(w, w.operator, 1)
    refused(w, lambda: pa.with_user(w.operator).write({"override_state": "approved"}), "workflow")
    refused(w, lambda: pa.with_user(w.operator).write({"directed_bin_id": w.hbin.id}), "workflow")


def test_a_full_bin_exception_redirects_and_counts_back(wms):
    w = wms
    pa = _new_putaway(w, w.operator, 2)
    assert pa.to_bin_id == w.bin2
    pa.with_user(w.operator).action_report_exception(cause="full_bin", note="pallet in the way")
    exc = pa.exception_ids
    assert (exc.cause, exc.bin_id, exc.reported_by_id) == ("full_bin", w.bin2, w.operator)
    assert pa.to_bin_id not in (w.bin2, w.bin) and exc.redirected_bin_id == pa.to_bin_id
    count = w.env["fix.wms.task"].search([("bin_id", "=", w.bin2.id), ("task_type", "=", "count")])
    assert count, "FR-WMS-033: a put-away exception counts the bin back"
    pa.with_user(w.operator).action_report_exception(cause="damaged_item")
    assert len(pa.exception_ids) == 2 and pa.state == "pending"
    refused(w, lambda: pa.with_user(w.operator).action_report_exception(cause="lost"), "full bin")


# ======================================================== page 3 docks
def test_dock_doors_are_master_data_and_appointments_clock_the_unload(wms):
    w = wms
    Door = w.env["fix.wms.dock.door"]
    refused(
        w,
        lambda: Door.with_user(w.operator).create({"warehouse_id": w.wh.id, "code": "D1"}),
        "Supervisor",
    )
    d_in = Door.with_user(w.supervisor).create(
        {"warehouse_id": w.wh.id, "code": "D1", "direction": "inbound"}
    )
    d_out = Door.with_user(w.supervisor).create(
        {"warehouse_id": w.wh.id, "code": "D2", "direction": "outbound"}
    )
    Dock = w.env["fix.wms.dock"].with_user(w.operator)
    appt = Dock.create({"door_id": d_in.id, "dock_type": "inbound"})
    assert appt.dock_no == "D1"
    refused(w, lambda: Dock.create({"door_id": d_out.id, "dock_type": "inbound"}), "outbound only")
    appt.action_check_in()
    assert appt.arrived_at
    appt.action_start_unload()
    assert appt.unload_started_at
    refused(w, lambda: appt.action_start_unload(), "once")
    # one booking per door per window; the same door code elsewhere is another door
    refused(w, lambda: Dock.create({"door_id": d_in.id, "dock_type": "inbound"}), "already booked")
    other_wh = w.env["fix.warehouse"].create(
        {
            "name": "Other " + w.tag,
            "code": "D" + w.tag[:5],
            "operating_unit_id": w.ou.id,
            "wms_enabled": True,
        }
    )
    d_far = Door.with_user(w.supervisor).create(
        {"warehouse_id": other_wh.id, "code": "D1", "direction": "inbound"}
    )
    assert Dock.create({"door_id": d_far.id, "dock_type": "inbound"}).dock_no == "D1"


# ======================================================== page 3 handling units
def test_a_handling_unit_holds_what_its_receipt_accepted(wms):
    w = wms
    rec = _receipt(w, 6)
    HU = w.env["fix.wms.handling.unit"].with_user(w.operator)
    hu = HU.create(
        {
            "warehouse_id": w.wh.id,
            "receipt_id": rec.id,
            "line_ids": [(0, 0, {"part_id": w.wpart.id, "qty": 6})],
        }
    )
    assert hu.name.startswith("HU/") and hu.contents_qty == 6
    refused(
        w,
        lambda: HU.create(
            {
                "warehouse_id": w.wh.id,
                "receipt_id": rec.id,
                "line_ids": [(0, 0, {"part_id": w.wpart.id, "qty": 1})],
            }
        ),
        "accepted",
    )
    pallet = HU.create({"warehouse_id": w.wh.id, "hu_type": "pallet"})
    hu.write({"parent_id": pallet.id})
    assert pallet.contents_qty == 6
    outer = HU.create({"warehouse_id": w.wh.id})
    refused(w, lambda: pallet.write({"parent_id": outer.id}), "T-11")
    # a unit already inside the pallet cannot take a unit of its own (one level)
    refused(w, lambda: HU.create({"warehouse_id": w.wh.id, "parent_id": hu.id}), "one level")
    hu.action_close()
    refused(w, lambda: hu.line_ids.write({"qty": 2}), "final")
    pallet.action_close()
    refused(w, lambda: pallet.action_store(bin_code="NOPE"), "not a bin")
    # A06 ERP audit F18: the contents are put away into the bin first
    refused(w, lambda: pallet.action_store(bin_code=w.bin2.name), "Put the contents away")
    pa = _new_putaway(
        w,
        w.operator,
        6,
        receipt_line_id=rec.line_ids.id,
        to_bin_id=w.bin2.id,
        override_reason="other",
    )
    if pa.override_state == "pending":
        pa.with_user(w.supervisor).action_approve_override()
    _complete(w, pa)
    pallet.action_store(bin_code=w.bin2.name)
    assert (pallet.state, pallet.current_bin_id, hu.current_bin_id) == ("stored", w.bin2, w.bin2)
    refused(w, lambda: pallet.write({"state": "open"}), "workflow")


# ======================================================== page 3 cross-dock
def test_cross_dock_sends_received_stock_straight_to_waiting_demand(wms):
    w = wms
    rec = _receipt(w, 20)
    line = rec.line_ids
    # A06 ERP audit F01/F10: the waiting demand is an approved transfer's, in a
    # draft wave; the cross-dock fulfils it whole and the transfer ships it
    wave = base._doc_wave(w, qty=5)
    demand = wave.line_ids
    XD = w.env["fix.wms.crossdock"].with_user(w.operator)
    refused(
        w,
        lambda: XD.create(
            {"receipt_line_id": line.id, "wave_line_id": demand.id, "qty": 6, "stage_lane": "X1"}
        ),
        "asks for 5",
    )
    xd = XD.create(
        {"receipt_line_id": line.id, "wave_line_id": demand.id, "qty": 5, "stage_lane": "X1"}
    )
    staged = w.qty(w.wpart, w.central, status="staged")
    refused(w, lambda: xd.action_confirm(item_code="WRONG"), "Scanned item")
    xd.action_confirm(item_code=w.wpart.part_number)
    assert xd.state == "staged" and xd.demand_qty_before == 5
    assert w.qty(w.wpart, w.central, status="staged") == staged + 5
    assert not wave.line_ids  # the demand is fulfilled by the dock
    # what was cross-docked is no longer there to put away
    pa = _new_putaway(w, w.operator, 16, receipt_line_id=line.id)
    refused(w, lambda: _complete(w, pa), "remains to be put away")
    unrestricted = w.qty(w.wpart, w.central)
    xd.action_dispatch(load_ref="VAN-7")
    assert xd.state == "dispatched"
    assert w.qty(w.wpart, w.central, status="staged") == staged
    assert w.qty(w.wpart, w.central) == unrestricted
    assert w.qty(w.wpart, w.central, status="in_transit") == 5  # the transfer took it


def test_cross_dock_only_before_the_wave_is_released(wms):
    w = wms
    rec = _receipt(w, 5)
    wave = base._doc_wave(w, qty=2)
    wave.with_user(w.supervisor).action_release()
    refused(
        w,
        lambda: w.env["fix.wms.crossdock"]
        .with_user(w.operator)
        .create(
            {
                "receipt_line_id": rec.line_ids.id,
                "wave_line_id": wave.line_ids.id,
                "qty": 2,
                "stage_lane": "X1",
            }
        ),
        "BRU-WMS-15",
    )


# ======================================================== page 3 returns
def test_returns_wait_for_a_second_persons_disposition(wms):
    w = wms
    rz = w.env["fix.warehouse.zone"].create(
        {"warehouse_id": w.wh.id, "name": "Returns", "code": "RT", "zone_type": "returns"}
    )
    rbin = w.env["fix.warehouse.bin"].create({"zone_id": rz.id, "name": "R-01-" + w.tag})
    rec = _receipt(w, 2)
    Ret = w.env["fix.wms.return.receipt"].with_user(w.operator)
    vals = {
        "warehouse_id": w.wh.id,
        "source_type": "branch_return",
        "source_ref": "TRF/BR-12",
        "part_id": w.wpart.id,
        "qty": 2,
        "receipt_line_id": rec.line_ids.id,
    }
    refused(w, lambda: Ret.create(dict(vals, returns_bin_id=w.bin2.id)), "returns zone")
    ret = Ret.create(dict(vals, returns_bin_id=rbin.id))
    ret.write({"disposition": "restock"})
    refused(w, lambda: ret.action_dispose(), "Supervisor")
    ret_c = ret.with_user(w.controller)
    ret_c.action_dispose()
    assert (ret.state, ret.disposed_by_id) == ("disposed", w.controller)
    assert ret.putaway_id and ret.putaway_id.directed_bin_id
    refused(w, lambda: ret.write({"qty": 1}), "final")
    # the receiver never decides; a scrap names its M15 record
    ret2 = (
        w.env["fix.wms.return.receipt"]
        .with_user(w.controller)
        .create(dict(vals, returns_bin_id=rbin.id, disposition="scrap"))
    )
    refused(w, lambda: ret2.with_user(w.controller).action_dispose(), "another person")
    refused(w, lambda: ret2.with_user(w.supervisor).action_dispose(), "M15")


# ======================================================== page 4 demand and waves
def test_demand_queues_and_builds_a_draft_wave_from_free_bin_stock(wms):
    w = wms
    Demand = w.env["fix.wms.outbound.demand"].with_user(w.keeper)
    d1 = Demand.create(
        {
            "warehouse_id": w.wh.id,
            "source_type": "transfer",
            "source_ref": "TRF/0001",
            "part_id": w.wpart.id,
            "qty": 4,
            "dest_location_id": w.hub.id,
            "priority": "urgent",
        }
    )
    assert d1.state == "queued" and d1.name.startswith("OBD/")
    # A06 ERP audit F01 / O1: typed demand leaves through an M15 transfer raised
    # (in the builder's name) when the wave is built; it waits for its approval
    waiting = d1.with_user(w.operator).action_build_wave()
    assert isinstance(waiting, dict) and d1.state == "queued"
    assert d1.transfer_id.state == "submitted" and d1.transfer_id.requested_by_id == w.operator
    d1.transfer_id.with_user(w.controller).action_approve()
    wave_ids = d1.with_user(w.operator).action_build_wave()
    wave = w.env["fix.wms.wave"].browse(wave_ids)
    assert (d1.state, d1.wave_id) == ("waved", wave)
    line = wave.line_ids
    assert (line.bin_id, line.qty, line.dest_location_id, line.demand_id) == (w.bin, 4, w.hub, d1)
    assert wave.state == "draft" and wave.priority == "urgent"
    refused(w, lambda: d1.write({"qty": 9}), "final")
    big = Demand.create(
        {
            "warehouse_id": w.wh.id,
            "source_ref": "TRF/0002",
            "part_id": w.wpart.id,
            "qty": 50,
            "dest_location_id": w.hub.id,
        }
    )
    big.with_user(w.operator).action_build_wave()  # raises its transfer
    big.transfer_id.with_user(w.controller).action_approve()
    refused(w, lambda: big.with_user(w.operator).action_build_wave(), "free")
    # a template serves only its destinations
    tpl = w.env["fix.wms.wave.template"].create(
        {"name": "Van run " + w.tag, "purpose": "van", "dest_location_ids": [(6, 0, w.van.ids)]}
    )
    refused(w, lambda: big.write({"template_id": tpl.id}), "serves")


def test_release_walks_the_pick_path_and_cluster_is_a_strategy(wms):
    w = wms
    tpl = w.env["fix.wms.wave.template"].create(
        {"name": "Cluster " + w.tag, "strategy": "cluster", "release_rule": "manual"}
    )
    wave = (
        w.env["fix.wms.wave"]
        .with_user(w.operator)
        .create(
            {
                "template_id": tpl.id,
                "line_ids": [(0, 0, {"part_id": w.wpart.id, "bin_id": w.bin.id, "qty": 2})],
            }
        )
    )
    assert wave.strategy == "cluster"
    wave.with_user(w.supervisor).action_release()
    task = w.env["fix.wms.task"].search([("wave_line_id", "=", wave.line_ids.id)])
    assert wave.line_ids.pick_sequence == 1 and task.pick_sequence == 1


# ======================================================== page 5 short-pick re-source
def test_a_short_pick_is_resourced_from_another_bin(wms):
    w = wms
    _complete(w, _new_putaway(w, w.operator, 6))  # 6 into bin 2 (directed)
    wave = w.wave(qty=8)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    line.with_user(w.operator).action_scan_short_pick(
        bin_code=w.bin.name, item_code=w.wpart.part_number, found_qty=3
    )
    new = wave.line_ids - line
    assert (line.state, line.qty, line.picked_qty) == ("picked", 3, 3)
    assert (new.bin_id, new.qty, new.state, new.resourced_from_id) == (w.bin2, 5, "pending", line)
    assert _slot(w, w.bin2).reserved_qty == 5
    assert w.env["fix.wms.task"].search([("wave_line_id", "=", new.id), ("task_type", "=", "pick")])
    new.with_user(w.operator).action_scan_pick(w.bin2.name, w.wpart.part_number)
    assert new.state == "picked"


# ======================================================== page 9 counts and labour
def test_a_count_plan_counts_a_zone_blind(wms):
    w = wms
    Plan = w.env["fix.wms.count.plan"].with_user(w.operator)
    plan = Plan.create({"warehouse_id": w.wh.id, "scope": "zone", "zone_id": w.zone.id})
    plan.action_generate()
    count = plan.floor_count_ids
    assert count.bin_id == w.bin and count.plan_id == plan and count.state == "draft"
    # F08: the expectation is taken when the count is entered, not when raised
    assert not count.expected_taken_at
    assert w.env["fix.wms.task"].search([("floor_count_id", "=", count.id)])
    again = Plan.create({"warehouse_id": w.wh.id, "scope": "zone", "zone_id": w.zone.id})
    refused(w, lambda: again.action_generate(), "Nothing to count")
    refused(w, lambda: plan.action_close(), "still open")
    refused(
        w, lambda: Plan.create({"warehouse_id": w.wh.id, "scope": "velocity"}), "names its class"
    )
    refused(w, lambda: plan.write({"state": "closed"}), "final")


def test_time_standards_and_productivity_are_measured_not_typed(wms):
    w = wms
    Std = w.env["fix.wms.time.standard"]
    refused(
        w,
        lambda: Std.with_user(w.operator).create({"warehouse_id": w.wh.id, "task_type": "pick"}),
        "Supervisor",
    )
    Std.with_user(w.supervisor).create(
        {
            "warehouse_id": w.wh.id,
            "task_type": "pick",
            "seconds_per_task": 30,
            "seconds_per_unit": 5,
        }
    )
    wave = w.wave(qty=2)
    wave.with_user(w.supervisor).action_release()
    task = w.env["fix.wms.task"].search([("wave_line_id", "=", wave.line_ids.id)])
    assert task.time_standard_sec == 40
    task.with_user(w.operator).action_claim()
    assert task.claimed_at and task.assignee_id == w.op_emp
    task.with_user(w.operator).action_done(scan="%s %s" % (w.bin.name, w.wpart.part_number))
    Run = w.env["fix.wms.productivity.run"]
    today = fields.Date.today()
    run = Run.with_user(w.supervisor).create(
        {
            "warehouse_id": w.wh.id,
            "date_from": today - timedelta(days=1),
            "date_to": today + timedelta(days=1),
        }
    )
    refused(w, lambda: run.with_user(w.operator).action_compute(), "Supervisor")
    run.with_user(w.supervisor).action_compute()
    row = run.line_ids.filtered(lambda r: r.operative_id == w.op_emp and r.task_type == "pick")
    assert row.tasks_completed == 1 and row.units == 2 and row.standard_seconds == 40
    assert row.accuracy_pct == 100.0
    refused(w, lambda: row.with_user(w.supervisor).write({"units": 99}), "never typed")
