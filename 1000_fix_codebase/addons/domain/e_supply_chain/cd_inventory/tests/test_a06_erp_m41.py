# A06 Supply Chain ERP audit (20 Nov 2026) - stream M41, findings F01-F32 + X16.
# Live ORM, rolled back, NON-ADMIN roles. Each test is named after its finding
# and refuses only through the new rule (the older controls pass first).
import json
from datetime import timedelta
from pathlib import Path

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

from . import test_a06_m41_controls as base

wms = base.wms
REFUSED = (UserError, AccessError, ValidationError, IntegrityError)


def refused(w, fn, match=None):
    with pytest.raises(REFUSED, match=match), w.env.cr.savepoint():
        fn()
        w.env.flush_all()


def _approved_transfer(w, qty=4, to=None, part=None, lines=None):
    tr = (
        w.env["fix.stock.transfer"]
        .with_user(w.keeper)
        .create(
            {
                "from_location_id": w.central.id,
                "to_location_id": (to or w.hub).id,
                "operating_unit_id": w.ou.id,
                "line_ids": lines or [(0, 0, {"part_id": (part or w.wpart).id, "qty": qty})],
            }
        )
    )
    tr.with_user(w.keeper).action_submit()
    if tr.state == "submitted":
        tr.with_user(w.controller).action_approve()
    assert tr.state == "approved"
    return tr


def _demand(w, tr):
    return w.env["fix.wms.outbound.demand"].search([("transfer_id", "=", tr.id)])


def _build(w, demand, user=None):
    res = demand.with_user(user or w.operator).action_build_wave()
    return w.env["fix.wms.wave"].browse(res if isinstance(res, list) else [])


def _pick_all(w, wave):
    for line in wave.line_ids.filtered(lambda ln: ln.state == "pending"):
        line.with_user(w.operator).action_scan_pick(line.bin_id.name, line.part_id.part_number)


def _ship(w, wave):
    wave.with_user(w.supervisor).action_release()
    _pick_all(w, wave)
    base._pack_and_load(w, wave)
    wave.with_user(w.operator).action_ship()


def _receipt(w, qty, cls="owned", part=None):
    rec = w.env["fix.stock.receipt"].create(
        {
            "partner_id": w.supplier.id,
            "location_id": w.central.id,
            "ownership_class": cls,
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


def _shipments(w, ref):
    return w.suspense(ref, "shipment")


# ======================================================== F01 / X16 / F22 (O1)
def test_f01_a_wave_line_with_no_m15_document_never_ships(wms):
    w = wms
    wave = w.wave(qty=4)
    wave.with_user(w.supervisor).action_release()
    _pick_all(w, wave)
    base._pack_and_load(w, wave)
    refused(w, lambda: wave.with_user(w.operator).action_ship(), "M15 document")
    assert wave.state == "staged"
    assert w.qty(w.wpart, w.central, status="staged") == 4  # still the warehouse's
    assert not _shipments(w, wave.name)


def test_f01_manual_demand_leaves_as_an_m15_transfer(wms):
    w = wms
    demand = (
        w.env["fix.wms.outbound.demand"]
        .with_user(w.operator)
        .create(
            {
                "warehouse_id": w.wh.id,
                "source_type": "manual",
                "source_ref": "Branch call " + w.tag,
                "part_id": w.wpart.id,
                "qty": 3,
                "dest_location_id": w.hub.id,
            }
        )
    )
    assert not _build(w, demand)  # the transfer awaits its approval
    transfer = demand.transfer_id
    assert transfer and (transfer.from_location_id, transfer.to_location_id) == (w.central, w.hub)
    assert (transfer.state, transfer.requested_by_id) == ("submitted", w.operator)
    assert demand.state == "queued" and "approval" in demand.short_note
    refused(w, lambda: transfer.with_user(w.operator).action_approve())
    transfer.with_user(w.controller).action_approve()
    wave = _build(w, demand)
    _ship(w, wave)
    assert (demand.state, transfer.state) == ("shipped", "dispatched")
    assert w.qty(w.wpart, w.central, status="in_transit") == 3
    assert w.qty(w.wpart, w.central) == 97
    assert not _shipments(w, wave.name)


def test_f01_job_demand_leaves_as_an_m15_job_issue(wms):
    w = wms
    job = w.job()
    demand = (
        w.env["fix.wms.outbound.demand"]
        .with_user(w.operator)
        .create(
            {
                "warehouse_id": w.wh.id,
                "source_type": "job",
                "source_ref": job.name,
                "technician_id": w.tech1.id,
                "part_id": w.wpart.id,
                "qty": 2,
                "dest_location_id": w.hub.id,
                "priority": "urgent",
            }
        )
    )
    wave = _build(w, demand)
    issue = demand.consumption_id
    assert issue.state == "draft" and issue.service_order_ref == job.name
    _ship(w, wave)
    assert (demand.state, issue.state) == ("shipped", "consumed")
    assert w.qty(w.wpart, w.central) == 98
    assert w.qty(w.wpart, w.central, status="staged") == 0
    assert not _shipments(w, wave.name)


def test_f01_job_demand_needs_its_technician_and_rtv_demand_is_never_typed(wms):
    w = wms
    Demand = w.env["fix.wms.outbound.demand"].with_user(w.operator)
    vals = {
        "warehouse_id": w.wh.id,
        "source_ref": "X",
        "part_id": w.wpart.id,
        "qty": 1,
        "dest_location_id": w.hub.id,
    }
    refused(w, lambda: Demand.create(dict(vals, source_type="job")), "technician")
    refused(w, lambda: Demand.create(dict(vals, source_type="rtv")), "never typed")


def test_f01_f10_cross_dock_fulfils_its_demand_whole_through_the_transfer(wms):
    w = wms
    tr = _approved_transfer(w, qty=5)
    demand = _demand(w, tr)
    wave = _build(w, demand)
    rec = _receipt(w, 20)
    XD = w.env["fix.wms.crossdock"].with_user(w.operator)
    vals = {"receipt_line_id": rec.line_ids.id, "demand_id": demand.id, "stage_lane": "X1"}
    refused(w, lambda: XD.create(dict(vals, qty=4)), "whole")
    xd = XD.create(dict(vals, qty=5))
    xd.action_confirm(item_code=w.wpart.part_number)
    assert demand.state == "crossdocked" and not wave.line_ids
    assert w.qty(w.wpart, w.central, status="staged") == 5
    xd.action_dispatch(load_ref="VAN-7")
    assert (xd.state, demand.state, tr.state) == ("dispatched", "shipped", "dispatched")
    assert w.qty(w.wpart, w.central, status="staged") == 0
    assert w.qty(w.wpart, w.central, status="in_transit") == 5
    assert not _shipments(w, xd.name)


def test_f01_cross_dock_to_a_line_with_no_demand_is_refused(wms):
    w = wms
    wave = w.wave(qty=5)
    rec = _receipt(w, 5)
    refused(
        w,
        lambda: w.env["fix.wms.crossdock"]
        .with_user(w.operator)
        .create(
            {
                "receipt_line_id": rec.line_ids.id,
                "wave_line_id": wave.line_ids.id,
                "qty": 5,
                "stage_lane": "X1",
            }
        ),
        "no outbound demand",
    )


# ======================================================== F02
def test_f02_put_away_never_slots_more_than_m15_holds_outside_the_bins(wms):
    w = wms
    issue = w.issue(w.keeper, part=w.wpart, qty=85.0, location=w.central)
    issue.with_user(w.keeper).action_scan_and_consume()
    # 15 on hand, 10 in bin A: 5 outside the bins (the receipt line still "has" 90)
    pa = w.putaway(w.operator, qty=6, bin_rec=w.bin2)
    refused(w, lambda: base._complete(w, pa), "outside the bins")
    ok = w.putaway(w.operator, qty=5, bin_rec=w.bin2)
    base._complete(w, ok)
    assert w.env["fix.wms.slot"]._slot_for(w.wpart, w.bin2).qty == 5


def test_f02_stock_still_in_inspection_is_not_put_away(wms):
    w = wms
    rec = _receipt(w, 6)
    rec.sudo()._guarded().write({"inspection_held": True})
    pa = w.putaway(w.operator, qty=2, bin_rec=w.bin2, line=rec.line_ids)
    refused(w, lambda: base._complete(w, pa), "still in inspection")


# ======================================================== F03 / O6
def _consignment_bin(w):
    zone = w.env["fix.warehouse.zone"].create(
        {
            "warehouse_id": w.wh.id,
            "name": "Brand",
            "code": "CN",
            "zone_type": "storage",
            "ownership_class": "consignment",
        }
    )
    return w.env["fix.warehouse.bin"].create(
        {"zone_id": zone.id, "name": "C-01-" + w.tag, "ownership_class": "consignment"}
    )


def test_f03_consignment_stock_keeps_its_class_in_the_bins(wms):
    w = wms
    cbin = _consignment_bin(w)
    rec = _receipt(w, 6, cls="consignment")
    into_any = w.putaway(w.operator, qty=3, bin_rec=w.bin2, line=rec.line_ids)
    refused(w, lambda: base._complete(w, into_any), "BRU-WMS-03")
    pa = w.putaway(w.operator, qty=6, bin_rec=cbin, line=rec.line_ids)
    base._complete(w, pa)
    slot = w.env["fix.wms.slot"]._slot_for(w.wpart, cbin)
    assert slot.ownership_class == "consignment"
    wave = w.wave(qty=4, bin_rec=cbin)
    wave.with_user(w.supervisor).action_release()
    assert w.bucket(w.wpart, w.central, "consignment").reserved == 4
    assert w.bucket(w.wpart, w.central).reserved == 0
    _pick_all(w, wave)
    assert w.qty(w.wpart, w.central, "consignment", "staged") == 4
    assert w.qty(w.wpart, w.central, "owned", "staged") == 0


# ======================================================== F04
def test_f04_naming_the_line_after_the_bin_reruns_the_directive(wms):
    w = wms
    pa = (
        w.env["fix.wms.putaway"]
        .with_user(w.operator)
        .create({"part_id": w.wpart.id, "qty": 2, "to_bin_id": w.hbin.id})
    )
    assert pa.override_state == "none" and not pa.directed_bin_id
    pa.with_user(w.operator).write({"receipt_line_id": w.grn_line.id})
    assert pa.directed_bin_id and pa.to_bin_id == pa.directed_bin_id


def test_f04_completion_refuses_a_bin_off_the_directive_without_approval(wms):
    w = wms
    pa = (
        w.env["fix.wms.putaway"]
        .with_user(w.operator)
        .create({"part_id": w.wpart.id, "qty": 2, "receipt_line_id": w.grn_line.id})
    )
    other = w.bin2 if pa.directed_bin_id != w.bin2 else w.bin
    pa.sudo()._guarded().write({"to_bin_id": other.id, "override_state": "none"})
    refused(w, lambda: base._complete(w, pa), "no approved override")


# ======================================================== F05 / O3
def test_f05_only_a_supervisor_arms_automatic_release(wms):
    w = wms
    Tpl = w.env["fix.wms.wave.template"]
    vals = {"name": "Run " + w.tag, "warehouse_id": w.wh.id, "cutoff": "15:00"}
    refused(
        w, lambda: Tpl.with_user(w.operator).create(dict(vals, release_rule="cutoff")), "Supervisor"
    )
    manual = Tpl.with_user(w.operator).create(dict(vals, name="Manual " + w.tag))
    assert manual.release_rule == "manual"
    refused(
        w, lambda: manual.with_user(w.operator).write({"release_rule": "immediate"}), "Supervisor"
    )
    armed = Tpl.with_user(w.supervisor).create(dict(vals, release_rule="cutoff"))
    assert armed.armed_by_id == w.supervisor
    refused(w, lambda: armed.with_user(w.operator).write({"cutoff": "09:00"}), "Supervisor")


def test_f05_an_unarmed_automatic_template_does_not_release(wms):
    w = wms
    tpl = (
        w.env["fix.wms.wave.template"]
        .sudo()
        .create({"name": "Legacy " + w.tag, "warehouse_id": w.wh.id, "release_rule": "immediate"})
    )
    tpl.sudo().write({"armed_by_id": w.operator.id})  # a legacy row armed by an operator
    tr = _approved_transfer(w, qty=2)
    demand = _demand(w, tr)
    demand.sudo().write({"template_id": tpl.id})
    tpl._fix_release_queue(quiet=True)
    assert demand.state == "queued" and "Supervisor" in tpl.last_release_error


# ======================================================== F06
def test_f06_the_ledger_ties_are_the_supervisors_and_frozen_with_stock(wms):
    w = wms
    refused(w, lambda: w.bin2.with_user(w.operator).write({"ownership_class": "warranty"}), "F06")
    refused(w, lambda: w.izone.with_user(w.operator).write({"zone_type": "bulk"}), "F06")
    refused(w, lambda: w.wh.with_user(w.operator).write({"stock_location_id": w.hub.id}), "F06")
    # the supervisor may, but not while the bin holds stock
    refused(
        w, lambda: w.bin.with_user(w.supervisor).write({"ownership_class": "warranty"}), "frozen"
    )
    refused(
        w, lambda: w.wh.with_user(w.supervisor).write({"stock_location_id": w.hub.id}), "frozen"
    )
    w.bin2.with_user(w.supervisor).write({"storage_class": "hazardous"})
    other = w.env["fix.warehouse"].create(
        {"name": "Other " + w.tag, "code": "O" + w.tag[:5], "operating_unit_id": w.ou.id}
    )
    refused(w, lambda: other.write({"stock_location_id": w.central.id}))


# ======================================================== F07 / O2
def test_f07_opening_slot_load_is_the_supervisors_capped_and_off_ledger(wms):
    w = wms
    Load = w.env["fix.wms.slot.load"]
    vals = {
        "warehouse_id": w.wh.id,
        "bin_id": w.bin2.id,
        "part_id": w.wpart.id,
        "reason": "Cutover count " + w.tag,
    }
    refused(w, lambda: Load.with_user(w.operator).create(dict(vals, qty=5)), "Supervisor")
    too_much = Load.with_user(w.supervisor).create(dict(vals, qty=91))
    refused(w, lambda: too_much.with_user(w.supervisor).action_load(), "outside the bins")
    load = Load.with_user(w.supervisor).create(dict(vals, qty=60))
    before = w.qty(w.wpart, w.central)
    events = w.env["fix.inventory.valuation.suspense"].sudo().search_count([])
    load.with_user(w.supervisor).action_load()
    assert load.state == "loaded"
    assert w.env["fix.wms.slot"]._slot_for(w.wpart, w.bin2).qty == 60
    assert w.qty(w.wpart, w.central) == before  # no ledger effect
    assert w.env["fix.inventory.valuation.suspense"].sudo().search_count([]) == events


def test_f07_stock_arriving_by_m15_transfer_is_put_away(wms):
    w = wms
    w.stock(w.wpart, w.hub, 6.0, 50.0)
    tr = (
        w.env["fix.stock.transfer"]
        .with_user(w.keeper)
        .create(
            {
                "from_location_id": w.hub.id,
                "to_location_id": w.central.id,
                "operating_unit_id": w.ou.id,
                "line_ids": [(0, 0, {"part_id": w.wpart.id, "qty": 6})],
            }
        )
    )
    tr.with_user(w.keeper).action_submit()
    if tr.state == "submitted":
        tr.with_user(w.controller).action_approve()
    tr.with_user(w.keeper).action_dispatch()
    tr.with_user(w.keeper2).action_receive()
    pa = w.putaway(
        w.operator,
        qty=6,
        bin_rec=w.bin2,
        line=w.env["fix.stock.receipt.line"],
        transfer_line_id=tr.line_ids.id,
    )
    base._complete(w, pa)
    assert w.env["fix.wms.slot"]._slot_for(w.wpart, w.bin2).qty == 6
    again = w.putaway(
        w.operator,
        qty=1,
        bin_rec=w.bin2,
        line=w.env["fix.stock.receipt.line"],
        transfer_line_id=tr.line_ids.id,
    )
    refused(w, lambda: base._complete(w, again), "remains to be put away")


def test_f07_a_floor_gain_of_stock_m15_already_holds_is_slotted_not_booked(wms):
    w = wms
    w.bin.sudo().write({"capacity_qty": 100})
    count = base._floor(w, 12)
    count.with_user(w.operator).action_post()  # recount
    count.with_user(w.operator).write({"reason_code": "misplaced"})
    count.with_user(w.operator).action_post()
    m15 = count.stock_count_id
    assert m15.state == "to_approve"
    m15.with_user(w.controller).action_approve()
    assert count.state == "posted"
    assert w.slot.qty == 12
    assert w.qty(w.wpart, w.central) == 100  # the 2 were already M15's


# ======================================================== F08
def test_f08_the_expectation_is_taken_when_the_count_is_entered(wms):
    w = wms
    count = (
        w.env["fix.wms.floor.count"]
        .with_user(w.operator)
        .create({"bin_id": w.bin.id, "part_id": w.wpart.id})
    )
    wave = w.wave(qty=4)
    wave.with_user(w.supervisor).action_release()
    _pick_all(w, wave)
    assert w.slot.qty == 6
    count.with_user(w.operator).write({"counted_qty": 6})
    count.with_user(w.operator).action_post()
    assert count.state == "posted" and count.sudo().variance == 0


def test_f08_a_slot_under_count_does_not_move(wms):
    w = wms
    count = base._floor(w, 8)
    count.with_user(w.operator).action_post()
    assert count.state == "recount"
    wave = w.wave(qty=2)
    refused(w, lambda: wave.with_user(w.supervisor).action_release(), "being counted")


# ======================================================== F09
def test_f09_an_m15_count_loss_never_takes_slotted_stock(wms):
    w = wms
    count = w.count(w.keeper, 5.0, part=w.wpart, location=w.central)
    count.with_user(w.keeper).action_submit()
    count.with_user(w.keeper).write({"reason_code": "other", "reason_note": "lost"})
    count.line_ids.with_user(w.keeper).action_set_recount(5.0)
    count.with_user(w.keeper).action_submit()
    refused(w, lambda: count.with_user(w.controller).action_approve(), "in warehouse bins")
    assert w.qty(w.wpart, w.central) == 100 and w.slot.qty == 10


# ======================================================== F11
def test_f11_a_document_line_is_not_cancelled_alone_and_waves_whole(wms):
    w = wms
    other = w.env["fix.spare.part"].create({"name": "Other", "part_number": "A6O-" + w.tag})
    rec = _receipt(w, 5, part=other)
    base._complete(w, w.putaway(w.operator, qty=5, part=other, bin_rec=w.bin2, line=rec.line_ids))
    tr = _approved_transfer(
        w,
        lines=[(0, 0, {"part_id": w.wpart.id, "qty": 2}), (0, 0, {"part_id": other.id, "qty": 3})],
    )
    demands = _demand(w, tr)
    assert len(demands) == 2
    refused(w, lambda: demands[0].with_user(w.operator).action_cancel(), "cancel")
    wave = _build(w, demands[0])  # one chosen: the whole transfer is waved
    assert set(demands.mapped("state")) == {"waved"} and demands.mapped("wave_id") == wave
    _ship(w, wave)
    assert tr.state == "dispatched"


# ======================================================== F12
def test_f12_a_short_pick_raises_a_real_count_that_freezes_the_bin(wms):
    w = wms
    wave = w.wave(qty=4)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    line.with_user(w.operator).action_scan_short_pick(
        bin_code=w.bin.name, item_code=w.wpart.part_number, found_qty=1
    )
    count = w.env["fix.wms.floor.count"].search(
        [("bin_id", "=", w.bin.id), ("count_type", "=", "count_back")]
    )
    task = w.env["fix.wms.task"].search([("floor_count_id", "=", count.id)])
    assert count.state == "draft" and task.task_type == "count"
    second = w.wave(qty=1)
    refused(w, lambda: second.with_user(w.supervisor).action_release(), "being counted")


# ======================================================== F13
def test_f13_the_counter_never_reads_the_expectation(wms):
    w = wms
    count = base._floor(w, 7)
    count.with_user(w.operator).action_post()
    with pytest.raises(AccessError):
        count.with_user(w.operator).read(["expected_qty"])
    with pytest.raises(AccessError):
        count.with_user(w.operator).read(["variance"])
    assert count.with_user(w.supervisor).read(["expected_qty"])[0]["expected_qty"] == 10


# ======================================================== F14 / F15
def test_f14_pick_accuracy_counts_against_the_request(wms):
    from odoo.addons.cd_p03_portal.controllers.a06 import m41

    w = wms
    wave = w.wave(qty=4)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    line.with_user(w.operator).action_scan_short_pick(
        bin_code=w.bin.name, item_code=w.wpart.part_number, found_qty=3
    )
    wave.with_user(w.operator).action_accept_short()
    assert (line.qty, line.requested_qty, line.state) == (3, 4, "picked")
    env = w.env(user=w.supervisor.id)
    pack = m41.pick_accuracy(env)
    row = next(r for r in pack["rows"] if r["wave"] == wave.name)
    assert (row["requested"], row["picked"], row["exact"]) == (4, 3, "no")
    rate = m41.short_pick_rate(env)
    assert sum(r["short"] for r in rate["rows"]) >= 1


def test_f14_reports_honour_the_dhaka_date_range(wms):
    from odoo.addons.cd_p03_portal.controllers.a06 import m41

    w = wms
    pa = w.putaway(w.operator, qty=1, bin_rec=w.bin2)
    if pa.override_state == "none":  # bin2 was the directive's own choice
        pa = w.putaway(w.operator, qty=1, bin_rec=w.hbin)
    assert pa.override_state == "approved"
    env = w.env(user=w.supervisor.id)
    today = str((pa.create_date + timedelta(hours=6)).date())
    assert [r for r in m41.override_report(env, today, today)["rows"] if r["putaway"] == pa.name]
    old = "2001-01-01"
    assert not m41.override_report(env, old, old)["rows"]
    for name, fn in m41.REPORTS.items():
        pack = fn(env, date_from=old, date_to=old)
        assert "rows" in pack, name


def test_f15_slot_vs_ledger_reconciliation_flags_slots_above_m15(wms):
    from odoo.addons.cd_p03_portal.controllers.a06 import m41

    w = wms
    env = w.env(user=w.supervisor.id)
    row = next(r for r in m41.slot_ledger_recon(env)["rows"] if r["part"] == w.wpart.part_number)
    assert (row["on_hand"], row["slotted"], row["status"]) == (100, 10, "ok")
    # M15 loses stock behind the bins' back: the slot now exceeds the ledger
    w.env["fix.stock.onhand"]._apply(w.wpart, w.central, "owned", -95.0)
    row = next(r for r in m41.slot_ledger_recon(env)["rows"] if r["part"] == w.wpart.part_number)
    assert row["status"] == "SLOTS EXCEED LEDGER"


# ======================================================== F16 / O7
def _device(w, operative=None):
    return w.env["fix.wms.device"].create(
        {
            "warehouse_id": w.wh.id,
            "device_code": "RF-" + w.tag + str(bool(operative)),
            "operative_id": operative.id if operative else False,
        }
    )


def test_f16_an_rf_device_is_issued_to_a_named_operative(wms):
    w = wms
    loose = _device(w)
    Device = w.env["fix.wms.device"].with_user(w.operator)
    refused(w, lambda: Device._rf_resolve(loose.device_code), "not issued")
    mine = _device(w, w.op_emp)
    device, employee = Device._rf_resolve(mine.device_code)
    assert employee == w.op_emp


def test_f16_floor_work_needs_a_profile_at_the_warehouse(wms):
    w = wms
    stranger = w.user("stranger", "cd_wms_structure.group_warehouse_operator")
    w.env["hr.employee"].create({"name": "Stranger " + w.tag, "user_id": stranger.id})
    pa = w.putaway(w.operator, qty=2, bin_rec=w.bin2)
    refused(w, lambda: base._complete(w, pa, user=stranger), "operative profile")
    task = w.env["fix.wms.task"].create(
        {"task_type": "count", "part_id": w.wpart.id, "bin_id": w.bin.id}
    )
    refused(w, lambda: task.with_user(stranger).action_claim(), "operative profile")
    task.with_user(w.operator).action_claim()
    assert task.assignee_id == w.op_emp


def test_f16_templates_and_stations_belong_to_their_company(wms):
    w = wms
    other_co = w.env["res.company"].create({"name": "M41 Other " + w.tag})
    tpl = w.env["fix.wms.wave.template"].create(
        {"name": "Theirs " + w.tag, "company_id": other_co.id}
    )
    station = w.env["fix.wms.packing.station"].create(
        {"name": "Theirs " + w.tag, "company_id": other_co.id}
    )
    Tpl = w.env["fix.wms.wave.template"].with_user(w.operator)
    assert not Tpl.search([("id", "=", tpl.id)])
    assert (
        not w.env["fix.wms.packing.station"].with_user(w.operator).search([("id", "=", station.id)])
    )


# ======================================================== F17
def test_f17_a_substitution_request_cannot_carry_its_own_decision(wms):
    from . import test_m41_capture_pass2b_live as p2b

    w = wms
    sub, _wave, line = p2b._substitute_setup(w)
    p2b._alternate(w, w.wpart, sub)
    req = (
        w.env["fix.wms.substitution"]
        .with_user(w.operator)
        .create(
            {
                "wave_line_id": line.id,
                "substitute_part_id": sub.id,
                "bin_id": w.bin2.id,
                "state": "approved",
                "requested_by_id": w.supervisor.id,
                "decided_by_id": w.supervisor.id,
            }
        )
    )
    assert (req.state, req.requested_by_id, req.decided_by_id.id) == (
        "requested",
        w.operator,
        False,
    )
    refused(
        w,
        lambda: w.env["fix.wms.substitution"]
        .with_user(w.operator)
        .create({"wave_line_id": line.id, "substitute_part_id": sub.id, "bin_id": w.qbin.id}),
        "nothing is picked",
    )


# ======================================================== F18
def test_f18_a_handling_unit_is_stored_only_where_its_contents_are_slotted(wms):
    w = wms
    rec = _receipt(w, 4)
    hu = (
        w.env["fix.wms.handling.unit"]
        .with_user(w.operator)
        .create(
            {
                "warehouse_id": w.wh.id,
                "receipt_id": rec.id,
                "line_ids": [(0, 0, {"part_id": w.wpart.id, "qty": 4})],
            }
        )
    )
    hu.with_user(w.operator).action_close()
    refused(
        w,
        lambda: hu.with_user(w.operator).action_store(bin_code=w.bin2.name),
        "Put the contents away",
    )
    base._complete(w, w.putaway(w.operator, qty=4, bin_rec=w.bin2, line=rec.line_ids))
    hu.with_user(w.operator).action_store(bin_code=w.bin2.name)
    assert hu.state == "stored"


# ======================================================== F19
def test_f19_an_operative_cannot_clear_the_equipment_a_task_needs(wms):
    w = wms
    task = w.env["fix.wms.task"].create(
        {
            "task_type": "move",
            "part_id": w.wpart.id,
            "bin_id": w.bin.id,
            "equipment_required": "forklift",
        }
    )
    refused(w, lambda: task.with_user(w.operator).write({"equipment_required": False}), "equipment")
    refused(w, lambda: task.with_user(w.operator).action_claim(), "BRU-WMS-18")
    task.with_user(w.supervisor).write({"equipment_required": False})


# ======================================================== F20 / F24 / O5
def test_f24_operatives_report_a_bin_the_supervisor_blocks(wms):
    w = wms
    refused(w, lambda: w.bin2.with_user(w.operator).action_block(reason="x"), "report")
    w.bin2.with_user(w.operator).action_report_block(reason="Shelf cracked")
    assert not w.bin2.blocked and w.bin2.block_report_reason == "Shelf cracked"
    w.bin2.with_user(w.supervisor).action_block(reason="Shelf cracked")
    assert w.bin2.blocked and not w.bin2.block_report_reason


def test_f20_put_away_exceptions_cannot_walk_the_directive(wms):
    w = wms
    pa = (
        w.env["fix.wms.putaway"]
        .with_user(w.operator)
        .create({"part_id": w.wpart.id, "qty": 1, "receipt_line_id": w.grn_line.id})
    )
    first = pa.to_bin_id
    assert first
    pa.with_user(w.operator).action_report_exception(cause="blocked_bin", note="looks bent")
    assert not first.blocked and first.block_report_reason == "looks bent"
    second = pa.to_bin_id
    assert second and second != first
    pa.with_user(w.operator).action_report_exception(cause="full_bin")
    refused(
        w,
        lambda: pa.with_user(w.operator).action_report_exception(cause="full_bin"),
        "Supervisor",
    )
    assert w.env["fix.wms.floor.count"].search_count(
        [("bin_id", "=", second.id), ("count_type", "=", "count_back")]
    )
    pa.with_user(w.supervisor).action_report_exception(cause="full_bin")


# ======================================================== F25
def test_f25_a_warehouse_with_no_bins_queues_no_demand(inv):
    env = inv.env
    env["fix.warehouse"].create(
        {
            "name": "Empty WMS " + inv.tag,
            "code": "E" + inv.tag[:5],
            "operating_unit_id": inv.ou.id,
            "stock_location_id": inv.central.id,
            "wms_enabled": True,
        }
    )
    tr = inv.transfer(inv.keeper, qty=1.0)
    tr.with_user(inv.keeper).action_submit()
    tr.with_user(inv.controller).action_approve()
    assert not env["fix.wms.outbound.demand"].search([("transfer_id", "=", tr.id)])
    tr.with_user(inv.keeper).action_dispatch()


# ======================================================== F27
def test_f27_productivity_counts_only_work_that_moved_something(wms):
    w = wms
    typed = w.env["fix.wms.task"].create(
        {
            "task_type": "count",
            "part_id": w.wpart.id,
            "bin_id": w.bin.id,
            "assignee_id": w.op_emp.id,
            "qty": 50,
        }
    )
    typed.sudo()._guarded().write(
        {"state": "done", "done_at": typed.create_date, "done_by_id": w.operator.id}
    )
    wave = w.wave(qty=2)
    wave.with_user(w.supervisor).action_release()
    task = w.env["fix.wms.task"].search([("wave_line_id", "=", wave.line_ids.id)])
    task.with_user(w.operator).action_claim()
    task.with_user(w.operator).action_done(scan="%s %s" % (w.bin.name, w.wpart.part_number))
    day = (task.done_at + timedelta(hours=6)).date()
    run = (
        w.env["fix.wms.productivity.run"]
        .with_user(w.supervisor)
        .create({"warehouse_id": w.wh.id, "date_from": day, "date_to": day})
    )
    run.with_user(w.supervisor).action_compute()
    assert sum(run.line_ids.mapped("tasks_completed")) == 1
    assert sum(run.line_ids.mapped("units")) == 2


# ======================================================== F28
def test_f28_a_failed_auto_release_is_kept_on_the_template(wms):
    w = wms
    tpl = (
        w.env["fix.wms.wave.template"]
        .with_user(w.supervisor)
        .create(
            {
                "name": "Fail " + w.tag,
                "warehouse_id": w.wh.id,
                "release_rule": "cutoff",
                "cutoff": "00:01",
            }
        )
    )
    tr = _approved_transfer(w, qty=2)
    demand = _demand(w, tr)
    demand.sudo().write({"template_id": tpl.id})
    w.bin.with_user(w.supervisor).action_block(reason="Audit")
    tpl._fix_release_queue(quiet=True)
    assert demand.state == "queued"
    assert tpl.last_release_error or demand.short_note


# ======================================================== F29
def test_f29_a_refused_rf_confirmation_is_not_replayed_forever(wms):
    w = wms
    device = _device(w, w.op_emp)
    Device = w.env["fix.wms.device"].with_user(w.operator)
    dev, _emp = Device._rf_resolve(device.device_code)
    task = w.env["fix.wms.task"].create(
        {"task_type": "count", "part_id": w.wpart.id, "bin_id": w.bin.id}
    )
    first = dev._rf_run("K-" + w.tag, "confirm", task.id, {"scans": []})
    assert not first["ok"]
    dev._rf_run("C-" + w.tag, "claim", task.id, {})
    again = dev._rf_run("K-" + w.tag, "confirm", task.id, {"scans": []})
    assert again["replayed"] is False
    journal = w.env["fix.wms.rf.journal"].sudo().search([("key", "=", "K-" + w.tag)])
    assert len(journal) == 1


# ======================================================== F30
def test_f30_cancelling_work_is_the_supervisors(wms):
    w = wms
    task = w.env["fix.wms.task"].create(
        {"task_type": "count", "part_id": w.wpart.id, "bin_id": w.bin.id}
    )
    refused(w, lambda: task.with_user(w.operator).action_cancel(), "Supervisor")
    task.with_user(w.supervisor).action_cancel()
    pa = w.putaway(w.operator, qty=1, bin_rec=w.bin2)
    refused(w, lambda: pa.with_user(w.operator).action_cancel(reason="x"), "Supervisor")
    pa.with_user(w.supervisor).action_cancel(reason="Wrong part")
    assert pa.state == "cancelled"


# ======================================================== F31
def test_f31_an_approved_override_never_stores_stock_in_a_staging_bin(wms):
    w = wms
    szone = w.env["fix.warehouse.zone"].create(
        {"warehouse_id": w.wh.id, "name": "Staging", "code": "ST", "zone_type": "staging"}
    )
    sbin = w.env["fix.warehouse.bin"].create({"zone_id": szone.id, "name": "S-01-" + w.tag})
    pa = w.putaway(w.operator, qty=1, bin_rec=sbin)
    assert pa.override_state == "approved"
    refused(w, lambda: base._complete(w, pa), "not stored there")


# ======================================================== F23 / F26 / F32
def test_f23_a_carton_holds_a_fractional_content(wms):
    carton = wms.env["fix.wms.carton"].create({"contents_qty": 2.5, "weight_kg": 1.0})
    assert carton.contents_qty == 2.5


def test_f26_the_spec_events_are_published(wms):
    w = wms
    wave = w.wave(qty=2)
    wave.with_user(w.supervisor).action_release()
    _pick_all(w, wave)
    assert w.events("wh.wave_released", "fix.wms.wave", wave.id) == 1
    assert w.events("wh.pick_confirmed", "fix.wms.wave.line", wave.line_ids.id) == 1
    base._pack_and_load(w, wave)
    assert w.events("wh.packed", "fix.wms.wave", wave.id) == 1
    dock = w.env["fix.wms.dock"].create({"dock_no": "D9-" + w.tag, "dock_type": "inbound"})
    dock.action_check_in()
    assert w.events("wh.inbound_arrived", "fix.wms.dock", dock.id) == 1


def test_f32_no_cost_on_the_m41_surface(wms):
    from odoo.addons.cd_p03_portal.controllers.a06 import m15, m41

    assert "fix.inventory.valuation.suspense" not in m41.SURFACES
    # The item master (with its standard-cost action) is served by M15's
    # controller on purpose; M41's surface carries no part master and no cost.
    assert "fix.spare.part" not in m41.SURFACES
    assert not any(
        "action_set_standard_cost" in s.get("actions", {}) for s in m41.SURFACES.values()
    )
    assert "action_set_standard_cost" in m15.SURFACES["fix.spare.part"]["actions"]
    # the warehouse floor cannot set a cost through the screens ...
    res = wms.p03(wms.operator).action(
        model="fix.spare.part",
        ids=wms.wpart.ids,
        method="action_set_standard_cost",
        kwargs={"cost": 1.0},
    )
    assert not res.get("success")
    assert wms.wpart.unit_cost != 1.0
    # ... an Inventory Controller sets it on M15's item master
    res = wms.p03(wms.controller).action(
        model="fix.spare.part",
        ids=wms.wpart.ids,
        method="action_set_standard_cost",
        kwargs={"cost": 1.0},
    )
    assert res.get("success"), res
    js = Path(m41.__file__).resolve().parents[2] / "static" / "src" / "a06" / "m41.js"
    text = js.read_text(encoding="utf-8")
    assert "action_set_standard_cost" not in text and "valuation.suspense" not in text


def test_f26_the_new_event_schemas_are_registered():
    root = Path(__file__).resolve().parents[5] / "contracts" / "events"
    registry = json.loads((root / "master-event-registry.json").read_text(encoding="utf-8"))
    text = json.dumps(registry)
    for event in ("wh.wave_released", "wh.pick_confirmed", "wh.packed", "wh.count_submitted"):
        assert event in text, event
