# M41 capture pass 2, part 2 (2026-11-20) - the items the owner chose to build:
# the demand feed with the wave dispatching its document, auto-release at the
# cut-off, the scan log, substitute pick, slotting proposals and the RF
# journal. Live ORM, NON-ADMIN roles; each test runs the proper path and the
# control the spec names.
import uuid

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


def _slot(w, bin_rec, part=None):
    return w.env["fix.wms.slot"]._slot_for(part or w.wpart, bin_rec)


def _approved_transfer(w, qty=4, to=None):
    tr = w.transfer(w.keeper, qty=qty, part=w.wpart, to=to or w.hub)
    tr.with_user(w.keeper).action_submit()
    if tr.state == "submitted":
        tr.with_user(w.controller).action_approve()
    assert tr.state == "approved"
    return tr


def _demand(w, tr):
    return w.env["fix.wms.outbound.demand"].search([("transfer_id", "=", tr.id)])


def _pick_all(w, wave):
    for line in wave.line_ids.filtered(lambda ln: ln.state == "pending"):
        line.with_user(w.operator).action_scan_pick(line.bin_id.name, line.part_id.part_number)


# ======================================================== 1. demand feed + hand-off
def test_an_approved_transfer_queues_and_its_wave_dispatches_it(wms):
    w = wms
    tr = _approved_transfer(w)
    demand = _demand(w, tr)
    assert (demand.state, demand.source_type, demand.qty, demand.dest_location_id) == (
        "queued",
        "transfer",
        4,
        w.hub,
    )
    wave = w.env["fix.wms.wave"].browse(demand.with_user(w.operator).action_build_wave())
    refused(w, lambda: tr.with_user(w.keeper).action_dispatch(), "being picked by wave")
    unrestricted = w.qty(w.wpart, w.central)
    wave.with_user(w.supervisor).action_release()
    _pick_all(w, wave)
    base._pack_and_load(w, wave)
    wave.with_user(w.operator).action_ship()
    assert wave.state == "shipped" and wave.line_ids.state == "handed"
    assert demand.state == "shipped"
    assert (tr.state, tr.dispatched_by_id) == ("dispatched", w.operator)
    # BRU-INV-16: the sender keeps it in transit, it did not leave the ledger twice
    assert w.qty(w.wpart, w.central, status="in_transit") == 4
    assert w.qty(w.wpart, w.central, status="staged") == 0
    assert w.qty(w.wpart, w.central) == unrestricted - 4
    tr.with_user(w.keeper2).action_receive()
    assert w.qty(w.wpart, w.hub) == 4


def test_a_queued_transfer_dispatched_directly_leaves_the_queue(wms):
    w = wms
    tr = _approved_transfer(w)
    demand = _demand(w, tr)
    # unslotted stock at the warehouse location may still go straight out
    tr.with_user(w.keeper).action_dispatch()
    assert tr.state == "dispatched" and demand.state == "cancelled"


def test_van_replenishment_and_cancel_follow_the_transfer(wms):
    w = wms
    tr = _approved_transfer(w, to=w.van)
    demand = _demand(w, tr)
    assert demand.source_type == "van"
    wave = w.env["fix.wms.wave"].browse(demand.with_user(w.operator).action_build_wave())
    refused(w, lambda: tr.with_user(w.keeper).action_cancel(), "cancel the wave first")
    wave.with_user(w.supervisor).action_cancel(reason="re-plan")
    assert (demand.state, demand.wave_id) == ("queued", w.env["fix.wms.wave"])
    tr.with_user(w.keeper).action_cancel()
    assert demand.state == "cancelled"


def test_a_short_transfer_wave_does_not_ship(wms):
    w = wms
    tr = _approved_transfer(w, qty=4)
    demand = _demand(w, tr)
    wave = w.env["fix.wms.wave"].browse(demand.with_user(w.operator).action_build_wave())
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    line.with_user(w.operator).action_scan_short_pick(
        bin_code=line.bin_id.name, item_code=w.wpart.part_number, found_qty=2
    )
    wave.with_user(w.operator).action_accept_short()
    base._pack_and_load(w, wave)
    refused(w, lambda: wave.with_user(w.operator).action_ship(), "ships whole")
    assert tr.state == "approved"


def test_an_rtv_out_of_the_warehouse_is_picked_and_shipped_by_its_wave(wms):
    w = wms
    rtv = w.rtv(w.keeper, qty=3, part_id=w.wpart.id, rtv_ref="RMA-" + w.tag)
    rtv.with_user(w.controller).action_approve()
    demand = w.env["fix.wms.outbound.demand"].search([("rtv_id", "=", rtv.id)])
    assert (demand.source_type, demand.dest_location_id.id) == ("rtv", False)
    wave = w.env["fix.wms.wave"].browse(demand.with_user(w.operator).action_build_wave())
    refused(w, lambda: rtv.with_user(w.keeper).action_ship(), "being picked by wave")
    before = w.qty(w.wpart, w.central)
    wave.with_user(w.supervisor).action_release()
    _pick_all(w, wave)
    base._pack_and_load(w, wave)
    wave.with_user(w.operator).action_ship()
    assert rtv.state == "shipped" and demand.state == "shipped"
    assert w.qty(w.wpart, w.central, status="staged") == 0
    assert w.qty(w.wpart, w.central) == before - 3


# ======================================================== auto-release
def test_a_cutoff_template_releases_its_queue_and_leaves_short_demand_waiting(wms):
    w = wms
    tpl = (
        w.env["fix.wms.wave.template"]
        .with_user(w.operator)
        .create(
            {
                "name": "Branch run " + w.tag,
                "warehouse_id": w.wh.id,
                "purpose": "branch_run",
                "release_rule": "cutoff",
                "cutoff": "00:00",
            }
        )
    )
    Demand = w.env["fix.wms.outbound.demand"].with_user(w.keeper)
    vals = {"warehouse_id": w.wh.id, "part_id": w.wpart.id, "dest_location_id": w.hub.id}
    ok = Demand.create(dict(vals, source_ref="TRF/A-" + w.tag, qty=3))
    big = Demand.create(dict(vals, source_ref="TRF/B-" + w.tag, qty=500))
    assert ok.template_id == tpl and big.template_id == tpl  # assigned by purpose
    w.env["fix.wms.wave.template"].sudo()._cron_auto_release()
    assert ok.state == "waved" and ok.wave_id.state == "released"
    assert big.state == "queued" and "only" in big.short_note
    assert tpl.last_released_at
    # released once per cut-off: later demand waits for the next one
    late = Demand.create(dict(vals, source_ref="TRF/C-" + w.tag, qty=1))
    w.env["fix.wms.wave.template"].sudo()._cron_auto_release()
    assert late.state == "queued"


def test_an_immediate_template_releases_on_arrival(wms):
    w = wms
    w.env["fix.wms.wave.template"].with_user(w.operator).create(
        {
            "name": "Van now " + w.tag,
            "warehouse_id": w.wh.id,
            "purpose": "van",
            "release_rule": "immediate",
        }
    )
    tr = _approved_transfer(w, qty=2, to=w.van)
    demand = _demand(w, tr)
    assert demand.state == "waved" and demand.wave_id.state == "released"


# ======================================================== 2. scan log
def _committed_events(w, marker):
    """Refused scans are written in their own transaction: read them from one."""
    with w.env.registry.cursor() as cr:
        cr.execute(
            "SELECT accepted, rule, user_ref FROM fix_wms_scan_event WHERE scans LIKE %s",
            ("%" + marker + "%",),
        )
        return cr.fetchall()


def test_every_scan_is_logged_and_a_refused_one_survives_the_refusal(wms):
    w = wms
    marker = "WRONG-" + uuid.uuid4().hex[:8]
    pa = (
        w.env["fix.wms.putaway"]
        .with_user(w.operator)
        .create({"part_id": w.wpart.id, "qty": 2, "receipt_line_id": w.grn_line.id})
    )
    refused(
        w,
        lambda: pa.with_user(w.operator).action_complete(bin_code=marker, item_code="x"),
        "Scanned bin",
    )
    rows = _committed_events(w, marker)
    assert rows == [(False, "BRU-WMS-05", w.operator.id)]
    pa.with_user(w.operator).action_complete(
        bin_code=pa.to_bin_id.name, item_code=w.wpart.part_number
    )
    ok = w.env["fix.wms.scan.event"].search(
        [("res_model", "=", "fix.wms.putaway"), ("res_id", "=", pa.id), ("accepted", "=", True)]
    )
    assert ok and ok.user_ref == w.operator.id
    refused(w, lambda: ok.with_user(w.supervisor).write({"accepted": False}), "append-only")
    refused(
        w,
        lambda: w.env["fix.wms.scan.event"].with_user(w.operator).create({"accepted": True}),
    )


def test_an_ownership_class_breach_is_counted_as_attempted_violation(wms):
    w = wms
    cbin = w.env["fix.warehouse.bin"].create(
        {"zone_id": w.zone.id, "name": "C-09-" + w.tag, "ownership_class": "consignment"}
    )
    marker = cbin.name
    pa = w.putaway(w.operator, qty=1, bin_rec=cbin)  # an approved override into it
    refused(
        w,
        lambda: pa.with_user(w.operator).action_complete(
            bin_code=cbin.name, item_code=w.wpart.part_number
        ),
        "BRU-WMS-03",
    )
    assert (False, "BRU-WMS-03", w.operator.id) in _committed_events(w, marker)
    # the report counts refused scans by rule and operative
    from odoo.addons.cd_p03_portal.controllers.a06 import m41 as ctl

    w.env["fix.wms.scan.event"].sudo().create(
        {
            "accepted": False,
            "rule": "BRU-WMS-03",
            "user_name": "R " + w.tag,
            "message": "x",
            "company_id": w.env.company.id,
        }
    )
    pack = ctl.scan_violations(w.env)
    row = next(r for r in pack["rows"] if r["operative"] == "R " + w.tag)
    assert row["rule"] == "BRU-WMS-03" and row["attempts"] >= 1


# ======================================================== 3. substitute pick
def _alternate(w, part, sub, direction="one_way"):
    Item = w.env["fix.catalogue.item"].sudo()
    items = []
    for p in (part, sub):
        product = w.env["product.product"].create({"name": "M41S " + p.part_number})
        p.sudo().write({"product_id": product.id})
        tmpl = product.product_tmpl_id
        item = Item.search([("product_tmpl_id", "=", tmpl.id)], limit=1) or Item.create(
            {"product_tmpl_id": tmpl.id, "item_type": "part"}
        )
        items.append(item)
    return (
        w.env["fix.part.crossref"]
        .sudo()
        .create(
            {
                "part_item_id": items[0].id,
                "alt_item_id": items[1].id,
                "relation_type": "approved_alternate",
                "direction": direction,
            }
        )
    )


def _substitute_setup(w):
    sub = w.env["fix.spare.part"].create({"name": "M41 alt", "part_number": "M41ALT-" + w.tag})
    rec = w.env["fix.stock.receipt"].create(
        {
            "partner_id": w.supplier.id,
            "location_id": w.central.id,
            "line_ids": [
                (0, 0, {"part_id": sub.id, "qty_received": 5, "qty_accepted": 5, "unit_cost": 9})
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    w.putaway(w.operator, qty=5, bin_rec=w.bin2, part=sub, line=rec.line_ids).with_user(
        w.operator
    ).action_complete(bin_code=w.bin2.name, item_code=sub.part_number)
    wave = w.wave(qty=8)
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    line.with_user(w.operator).action_scan_short_pick(
        bin_code=w.bin.name, item_code=w.wpart.part_number, found_qty=3
    )
    assert line.state == "short"  # no other bin of the part: nothing to re-source
    return sub, wave, line


def test_a_short_line_takes_an_approved_alternate_on_a_supervisors_approval(wms):
    w = wms
    sub, wave, line = _substitute_setup(w)
    Sub = w.env["fix.wms.substitution"].with_user(w.operator)
    vals = {"wave_line_id": line.id, "substitute_part_id": sub.id, "bin_id": w.bin2.id}
    refused(w, lambda: Sub.create(vals), "no approved alternate")
    xref = _alternate(w, w.wpart, sub)
    req = Sub.create(vals)
    assert (req.qty, req.crossref_id, req.state) == (5, xref, "requested")
    refused(w, lambda: req.with_user(w.operator).action_approve(), "Supervisor")
    req.with_user(w.supervisor).action_approve()
    new = req.new_line_id
    assert (new.part_id, new.qty, new.state, new.substitute_of_id) == (sub, 5, "pending", line)
    assert (line.state, line.qty) == ("picked", 3)
    assert _slot(w, w.bin2, sub).reserved_qty == 5
    new.with_user(w.operator).action_scan_pick(w.bin2.name, sub.part_number)
    assert new.state == "picked"


def test_a_one_way_alternate_does_not_replace_backwards_and_nobody_approves_their_own(wms):
    w = wms
    sub, _wave, line = _substitute_setup(w)
    _alternate(w, sub, w.wpart)  # sub may be replaced BY wpart, not the reverse
    Sub = w.env["fix.wms.substitution"]
    vals = {"wave_line_id": line.id, "substitute_part_id": sub.id, "bin_id": w.bin2.id}
    refused(w, lambda: Sub.with_user(w.operator).create(vals), "no approved alternate")
    w.env["fix.part.crossref"].sudo().search(
        [("alt_item_id.product_tmpl_id", "=", w.wpart.product_id.product_tmpl_id.id)]
    ).write({"direction": "two_way"})
    req = Sub.with_user(w.supervisor).create(vals)
    refused(w, lambda: req.with_user(w.supervisor).action_approve(), "another supervisor")


def test_a_transfer_line_is_never_substituted(wms):
    w = wms
    tr = _approved_transfer(w, qty=4)
    demand = _demand(w, tr)
    wave = w.env["fix.wms.wave"].browse(demand.with_user(w.operator).action_build_wave())
    wave.with_user(w.supervisor).action_release()
    line = wave.line_ids
    line.with_user(w.operator).action_scan_short_pick(
        bin_code=line.bin_id.name, item_code=w.wpart.part_number, found_qty=1
    )
    assert line.state == "short"
    refused(
        w,
        lambda: w.env["fix.wms.substitution"]
        .with_user(w.operator)
        .create({"wave_line_id": line.id, "substitute_part_id": w.part0.id, "bin_id": w.bin2.id}),
        "not substituted",
    )


# ======================================================== 4. slotting proposals
def test_a_fast_mover_outside_a_pick_face_gets_a_reslot_proposal(wms):
    w = wms
    Param = w.env["ir.config_parameter"].sudo()
    Param.set_param("cd_inventory.wms_fast_picks_90d", "1")
    Param.set_param("cd_inventory.wms_medium_picks_90d", "1")
    face = w.env["fix.warehouse.bin"].create(
        {"zone_id": w.zone.id, "name": "PF-01-" + w.tag, "capacity_qty": 100, "is_pick_face": True}
    )
    wave = w.wave(qty=1)
    wave.with_user(w.supervisor).action_release()
    _pick_all(w, wave)
    refused(w, lambda: w.wh.with_user(w.operator).action_propose_slotting(), "Supervisor")
    w.wh.with_user(w.supervisor).action_propose_slotting()
    assert _slot(w, w.bin).velocity == "fast"
    prop = w.env["fix.wms.slot.proposal"].search([("from_bin_id", "=", w.bin.id)])
    assert (prop.kind, prop.to_bin_id, prop.qty, prop.state) == ("reslot", face, 9, "proposed")
    w.wh.with_user(w.supervisor).action_propose_slotting()  # never proposed twice
    assert w.env["fix.wms.slot.proposal"].search_count([("from_bin_id", "=", w.bin.id)]) == 1
    refused(w, lambda: prop.with_user(w.operator).action_accept(), "Supervisor")
    refused(
        w,
        lambda: w.env["fix.wms.slot.proposal"]
        .with_user(w.supervisor)
        .create(
            {
                "warehouse_id": w.wh.id,
                "kind": "reslot",
                "part_id": w.wpart.id,
                "from_bin_id": w.bin.id,
                "to_bin_id": face.id,
                "qty": 1,
            }
        ),
        "nightly",
    )
    prop.with_user(w.supervisor).action_accept()
    assert prop.state == "accepted" and prop.move_id.move_type == "reslot"
    assert prop.move_id.state == "open" and prop.move_id.task_id


def test_a_part_split_across_bins_gets_a_consolidation_proposal(wms):
    w = wms
    w.env["ir.config_parameter"].sudo().set_param("cd_inventory.wms_fast_picks_90d", "1000")
    w.putaway(w.operator, qty=20, bin_rec=w.bin2).with_user(w.operator).action_complete(
        bin_code=w.bin2.name, item_code=w.wpart.part_number
    )
    w.env["fix.wms.slot.proposal"].sudo()._cron_propose()
    prop = w.env["fix.wms.slot.proposal"].search(
        [("from_bin_id", "=", w.bin.id), ("kind", "=", "consolidate")]
    )
    assert (prop.to_bin_id, prop.qty) == (w.bin2, 10)
    prop.with_user(w.supervisor).action_reject()
    assert prop.state == "rejected" and not prop.move_id


# ======================================================== 5. RF API logic + journal
def _device(w, code=None, operative=None):
    return (
        w.env["fix.wms.device"]
        .with_user(w.supervisor)
        .create(
            {
                "warehouse_id": w.wh.id,
                "device_code": code or "RF-" + uuid.uuid4().hex[:6],
                "operative_id": (operative or w.op_emp).id,
            }
        )
    )


def test_the_rf_api_runs_each_confirmation_once(wms):
    w = wms
    dev = _device(w)
    wave = w.wave(qty=2)
    wave.with_user(w.supervisor).action_release()
    Device = w.env["fix.wms.device"].with_user(w.operator)
    device, employee = Device._rf_resolve(dev.device_code)
    dev.invalidate_recordset()
    assert employee == w.op_emp and device.env.uid == w.operator.id and dev.last_seen_at
    tasks = device._rf_next(employee)
    task = w.env["fix.wms.task"].browse(tasks[0]["id"])
    assert task.wave_line_id == wave.line_ids and "cost" not in str(tasks[0]).lower()
    assert device._rf_run("k1", "claim", task.id, {})["ok"]
    assert task.state == "assigned" and task.assignee_id == w.op_emp
    scans = {"scans": [w.bin.name, w.wpart.part_number]}
    first = device._rf_run("k2", "confirm", task.id, scans)
    assert first["ok"] and not first["replayed"] and task.state == "done"
    # it ran as the operative, not as superuser: the scan is logged under the device
    assert not device.env.su
    logged = w.env["fix.wms.scan.event"].search(
        [("device_code", "=", dev.device_code), ("accepted", "=", True)]
    )
    assert logged and logged[0].user_ref == w.operator.id and logged[0].idempotency_key == "k2"
    again = device._rf_run("k2", "confirm", task.id, scans)  # the same key, replayed
    assert again["ok"] and again["replayed"]
    assert wave.line_ids.picked_qty == 2  # picked once
    bad = device._rf_run("k3", "confirm", task.id, scans)
    assert not bad["ok"] and "assigned" in bad["error"]
    refused(w, lambda: device._rf_run("", "claim", task.id, {}), "idempotency key")
    journal = w.env["fix.wms.rf.journal"].sudo().search([("device_id", "=", dev.id)])
    assert sorted(journal.mapped("key")) == ["k1", "k2", "k3"]
    refused(w, lambda: journal.with_user(w.supervisor).write({"ok": True}), "append-only")


def test_a_deactivated_or_borrowed_device_is_refused(wms):
    w = wms
    Device = w.env["fix.wms.device"].with_user(w.operator)
    other = _device(w, operative=w.tech2)
    refused(w, lambda: Device._rf_resolve(other.device_code), "issued to")
    dev = _device(w)
    dev.with_user(w.supervisor).action_deactivate(reason="lost on the floor")
    refused(w, lambda: Device._rf_resolve(dev.device_code), "deactivated")
    refused(w, lambda: Device._rf_resolve("NOPE-" + w.tag), "Unknown")
