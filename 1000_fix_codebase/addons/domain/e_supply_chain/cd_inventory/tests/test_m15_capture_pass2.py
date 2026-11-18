# M15 capture pass 2 (2026-11-19): the records four sub-module pages could
# not capture, exercised on the live ORM as NON-ADMIN users holding the real
# roles. Each control the spec names has its proper path and its refusal.
#
#   page 4 fix.stock.reservation   FR-INV-019..021, 027; BRU-INV-17..19
#   page 5 fix.stock.backorder     FR-INV-025, AUT-INV-02 (+ issue from a hold)
#   page 7 fix.stock.recall        FR-INV-040, AUT-INV-14
#   page 3 fix.consignment.*       FR-INV-012, 014, AUT-INV-07
import datetime

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

from .conftest import BRANCH, SK, make_service_order

REFUSED = (UserError, AccessError, ValidationError, IntegrityError)


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


_N = iter(range(1, 10_000))


def _job(inv, category="standard", sla=False):
    """A real service order of the given kind (as trusted set-up)."""
    order = make_service_order(inv.env, inv.branch(), "%s%d" % (inv.tag, next(_N)))
    if "sla_policy_id" in order._fields:
        order.sudo().write({"sla_policy_id": sla or False})
    inv.env.flush_all()
    # trusted set-up, as test_a06_final_m15._warranty_job: M01's warranty gate
    # (a warranty record on the device) is M01's suite's to test
    inv.env.cr.execute(
        "UPDATE fix_service_order SET order_category = %s WHERE id = %s", [category, order.id]
    )
    order.invalidate_recordset()
    return order


def _reserve(inv, user, qty=1.0, job=None, location=None, part=None, **kw):
    vals = {
        "part_id": (part or inv.part).id,
        "location_id": (location or inv.central).id,
        "qty": qty,
        "service_order_ref": job.name if job else False,
    }
    vals.update(kw)
    rec = inv.env["fix.stock.reservation"].with_user(user).create(vals)
    return rec


def _held(inv, user, qty=1.0, job=None, **kw):
    rec = _reserve(inv, user, qty, job, **kw)
    rec.with_user(user).action_reserve()
    return rec


# =================================================================== page 4
def test_a_reservation_holds_stock_for_its_job_and_the_issue_draws_it(inv):
    job = _job(inv)
    rsv = _held(inv, inv.keeper, 2.0, job)
    assert (rsv.state, rsv.booked_class, rsv.priority) == ("active", "owned", "2_paid")
    assert rsv.name.startswith("RSV/") and rsv.expires_at > fields.Datetime.now()
    assert inv.bucket(inv.part, inv.central).reserved == 2.0
    assert inv.events("stock.reserved", "fix.stock.reservation", rsv.id) == 1
    issue = inv.issue(inv.keeper, qty=2.0, service_order_ref=job.name, reservation_id=rsv.id)
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert (rsv.state, rsv.qty_consumed, rsv.qty_open) == ("consumed", 2.0, 0.0)
    row = inv.bucket(inv.part, inv.central)
    assert (row.qty, row.reserved) == (8.0, 0.0)


def test_held_stock_is_not_issued_to_another_job(inv):
    rsv = _held(inv, inv.keeper, 10.0, _job(inv))
    plain = inv.issue(inv.keeper, service_order_ref=_job(inv).name)
    refused(inv, lambda: plain.with_user(inv.keeper).action_scan_and_consume(), "Insufficient")
    other = inv.issue(inv.keeper, service_order_ref=_job(inv).name, reservation_id=rsv.id)
    refused(inv, lambda: other.with_user(inv.keeper).action_scan_and_consume(), "held for job")
    assert inv.bucket(inv.part, inv.central).reserved == 10.0


def test_warranty_work_takes_stock_from_lower_priority_holds(inv):
    """BRU-INV-17 computed: SLA/warranty > paid > internal."""
    internal = _held(inv, inv.keeper, 10.0)
    assert internal.priority == "3_internal"
    warranty = _held(inv, inv.keeper2, 4.0, _job(inv, "warranty"))
    assert warranty.priority == "1_sla" and warranty.state == "active"
    assert (internal.state, internal.displaced_by_id) == ("overridden", warranty)
    assert "BRU-INV-17" in internal.release_reason
    assert inv.bucket(inv.part, inv.central).reserved == 4.0
    # and never the other way round, nor between equals: only an override does that
    refused(inv, lambda: _held(inv, inv.keeper, 7.0), "lower-priority")
    refused(inv, lambda: _held(inv, inv.keeper, 7.0, _job(inv, "warranty")), "lower-priority")
    assert warranty.state == "active"


def test_an_sla_bound_paid_job_ranks_with_warranty(inv):
    policy = inv.env["fix.sla.policy"].search([], limit=1)
    if not policy:
        pytest.skip("no SLA policy in this database")
    assert _held(inv, inv.keeper, 1.0, _job(inv, "standard", policy.id)).priority == "1_sla"


def test_emergency_override_needs_the_role_and_a_reason(inv):
    first = _held(inv, inv.keeper, 10.0, _job(inv))
    job2 = _job(inv)
    by_keeper = _reserve(
        inv,
        inv.keeper2,
        1.0,
        job2,
        displaces_id=first.id,
        override_reason="Customer flying out tonight",
    )
    refused(inv, lambda: by_keeper.with_user(inv.keeper2).action_reserve(), "Branch Manager")
    manager = inv.user("bm", SK, BRANCH)
    short = _reserve(inv, manager, 1.0, job2, displaces_id=first.id, override_reason="urgent")
    refused(inv, lambda: short.with_user(manager).action_reserve(), "why")
    ok = _reserve(
        inv,
        manager,
        1.0,
        job2,
        displaces_id=first.id,
        override_reason="Customer flying out tonight",
    )
    ok.with_user(manager).action_reserve()
    assert (ok.state, ok.override_by_id) == ("active", manager)
    assert (first.state, first.displaced_by_id) == ("overridden", ok)
    assert "Emergency override" in first.release_reason
    assert first.message_ids.filtered(lambda m: "overridden" in (m.body or ""))
    assert inv.bucket(inv.part, inv.central).reserved == 1.0


def test_an_unissued_reservation_expires_back_to_stock(inv):
    rsv = _held(inv, inv.keeper, 3.0, _job(inv))
    rsv.sudo()._guarded().write({"expires_at": fields.Datetime.now() - datetime.timedelta(hours=1)})
    inv.env.flush_all()
    assert inv.env["fix.stock.reservation"]._cron_expire() >= 1
    assert rsv.state == "expired" and inv.bucket(inv.part, inv.central).reserved == 0.0
    assert inv.events("stock.reservation_released", "fix.stock.reservation", rsv.id) == 1


def test_release_is_the_requesters_or_a_controllers(inv):
    rsv = _held(inv, inv.keeper, 2.0, _job(inv))
    refused(inv, lambda: rsv.with_user(inv.keeper2).action_release(), "Only")
    rsv.with_user(inv.keeper).action_release("job cancelled")
    assert rsv.state == "released" and inv.bucket(inv.part, inv.central).reserved == 0.0


def test_a_reservation_obeys_the_class_and_status_rules(inv):
    inv.stock(inv.part, inv.central, 4.0, 400.0, cls="consignment")
    paid = _reserve(inv, inv.keeper, 1.0, _job(inv), reserve_class="consignment")
    refused(inv, lambda: paid.with_user(inv.keeper).action_reserve(), "BRU-INV-01")
    quarantine = inv.env["fix.stock.location"].create(
        {
            "name": "A06 QRN",
            "code": "A6Q-" + inv.tag,
            "location_type": "quarantine",
            "operating_unit_id": inv.ou.id,
        }
    )
    held = _reserve(inv, inv.keeper, 1.0, location=quarantine)
    refused(inv, lambda: held.with_user(inv.keeper).action_reserve(), "BRU-INV-08")
    unknown = _reserve(inv, inv.keeper, 1.0, service_order_ref="NO-SUCH-JOB")
    refused(inv, lambda: unknown.with_user(inv.keeper).action_reserve(), "matches no")


def test_a_held_reservation_is_fixed_and_its_state_is_guarded(inv):
    rsv = _held(inv, inv.keeper, 2.0, _job(inv))
    refused(inv, lambda: rsv.with_user(inv.keeper).write({"qty": 5.0}), "fixed")
    refused(inv, lambda: rsv.with_user(inv.keeper).write({"state": "released"}))
    refused(inv, lambda: _reserve(inv, inv.keeper, 1.0, state="active"))
    refused(
        inv,
        lambda: inv.env["fix.stock.reservation"]
        .with_user(inv.clerk)
        .create({"part_id": inv.part.id, "location_id": inv.central.id, "qty": 1.0}),
    )


# =================================================================== page 5
def _backorder(inv, user, qty=2.0, location=None, job=None, **kw):
    vals = {
        "part_id": inv.part.id,
        "location_id": (location or inv.hub).id,
        "qty": qty,
        "service_order_ref": job.name if job else False,
    }
    vals.update(kw)
    return inv.env["fix.stock.backorder"].with_user(user).create(vals)


def test_no_backorder_for_stock_at_hand(inv):
    refused(inv, lambda: _backorder(inv, inv.keeper, location=inv.central), "reserve it instead")


def test_a_backorder_pulls_from_the_network_then_holds_it_for_the_job(inv):
    job = _job(inv)
    bko = _backorder(inv, inv.keeper, 2.0, job=job)
    assert bko.state == "open" and bko.name.startswith("BKO/")
    assert (bko.source_location_id, bko.source_available) == (inv.central, 10.0)
    assert inv.events("stock.stockout", "fix.stock.backorder", bko.id) == 1
    refused(
        inv,
        lambda: bko.with_user(inv.keeper).action_raise_requisition(),
        "transfer, not a purchase",
    )
    refused(inv, lambda: bko.with_user(inv.keeper).action_fulfil(), "stays open")
    bko.with_user(inv.keeper).action_raise_transfer()
    t = bko.transfer_id
    assert bko.state == "transfer"
    assert (t.from_location_id, t.to_location_id, t.line_ids.qty) == (inv.central, inv.hub, 2.0)
    inv.stock(inv.part, inv.hub, 2.0, 500.0)  # the transfer has arrived
    bko.with_user(inv.keeper).action_fulfil()
    rsv = bko.reservation_id
    assert bko.state == "fulfilled"
    assert (rsv.state, rsv.service_order_ref, rsv.qty) == ("active", job.name, 2.0)
    refused(inv, lambda: bko.with_user(inv.keeper).write({"qty": 9.0}), "fixed")


def test_a_backorder_buys_only_what_nobody_holds(inv):
    inv.env["hr.employee"].create({"name": "A06 Keeper %s" % inv.tag, "user_id": inv.keeper.id})
    nowhere = inv.env["fix.spare.part"].create(
        {"name": "A06 Rare", "part_number": "A6R-" + inv.tag}
    )
    bko = _backorder(inv, inv.keeper, 1.0, part_id=nowhere.id)
    assert not bko.source_location_id
    refused(inv, lambda: bko.with_user(inv.keeper).action_raise_transfer(), "requisition instead")
    bko.with_user(inv.keeper).action_raise_requisition()
    assert bko.state == "requisition" and bko.requisition_id
    assert bko.name in bko.requisition_id.description
    refused(inv, lambda: bko.with_user(inv.keeper).action_cancel(""), "reason")
    bko.with_user(inv.keeper).action_cancel("customer cancelled the repair")
    assert bko.state == "cancelled"


# =================================================================== page 7
def test_a_recall_quarantines_every_unit_everywhere_and_lists_the_jobs(inv):
    inv.stock(inv.part, inv.hub, 3.0, 500.0)
    inv.stock(inv.part, inv.van, 2.0, 500.0, cls="van")
    issue = inv.issue(inv.keeper)
    issue.with_user(inv.keeper).action_scan_and_consume()
    held = _held(inv, inv.keeper, 1.0, _job(inv), location=inv.hub)
    rcl = (
        inv.env["fix.stock.recall"]
        .with_user(inv.keeper)
        .create({"part_id": inv.part.id, "reason": "recall", "reference": "BRAND-BULLETIN-7"})
    )
    refused(inv, lambda: rcl.with_user(inv.keeper).action_execute(), "Inventory Controller")
    rcl.with_user(inv.controller).action_execute()
    assert (rcl.state, rcl.qty_quarantined, rcl.qty_not_reached) == ("executed", 14.0, 0.0)
    assert held.state == "released" and "Recalled" in held.release_reason
    for loc, cls, qty in (
        (inv.central, "owned", 9.0),
        (inv.hub, "owned", 3.0),
        (inv.van, "van", 2.0),
    ):
        assert inv.qty(inv.part, loc, cls) == 0.0
        assert inv.qty(inv.part, loc, cls, "quarantine") == qty
    assert set(rcl.quarantine_ids.mapped("reason")) == {"defective"}
    assert issue in rcl.affected_consumption_ids
    assert inv.events("stock.quarantined", "fix.stock.recall", rcl.id) == 1
    refused(
        inv, lambda: rcl.with_user(inv.controller).write({"reason": "defect"}), "executed recall"
    )


def test_a_serial_recall_takes_only_the_named_serials(inv):
    rcl = (
        inv.env["fix.stock.recall"]
        .with_user(inv.keeper)
        .create(
            {
                "part_id": inv.spart.id,
                "scope": "serials",
                "lot_ids": [(6, 0, inv.lot1.ids)],
                "reason": "counterfeit",
            }
        )
    )
    rcl.with_user(inv.controller).action_execute()
    assert (inv.lot1.status, inv.lot2.status) == ("quarantined", "in_stock")
    assert rcl.quarantine_ids.reason == "suspect" and rcl.qty_quarantined == 1.0
    assert inv.qty(inv.spart, inv.central) == 1.0


def test_a_recall_names_its_serials(inv):
    refused(
        inv,
        lambda: inv.env["fix.stock.recall"]
        .with_user(inv.keeper)
        .create({"part_id": inv.spart.id, "scope": "serials", "reason": "defect"}),
        "Name the serials",
    )
    refused(
        inv,
        lambda: inv.env["fix.stock.recall"]
        .with_user(inv.keeper)
        .create(
            {
                "part_id": inv.part.id,
                "scope": "serials",
                "lot_ids": [(6, 0, inv.lot1.ids)],
                "reason": "defect",
            }
        ),
        "not serials of",
    )


# =================================================================== page 3
def _consignment_world(inv):
    job = _job(inv, "warranty")
    brand = job.device_id.sudo().brand_id  # what the issue's BRU-INV-01 check reads
    part = inv.env["fix.spare.part"].create(
        {
            "name": "A06 Brand Panel",
            "part_number": "A6B-" + inv.tag,
            "unit_cost": 400.0,
            "device_brand": brand.name,
            "brand_id": brand.id,
        }
    )
    rec = inv.receipt(inv.keeper, part=part, location=inv.central, ownership_class="consignment")
    rec.with_user(inv.keeper).action_inspect()
    rec.with_user(inv.controller).action_post()
    issue = inv.issue(inv.keeper, part=part, issue_class="consignment", service_order_ref=job.name)
    issue.with_user(inv.keeper).action_scan_and_consume()
    return brand, part


def _statement(inv, brand, user=None):
    return (
        inv.env["fix.consignment.reconciliation"]
        .with_user(user or inv.keeper)
        .create(
            {
                "brand_id": brand.id,
                "period_start": fields.Date.context_today(inv.env.user).replace(day=1),
            }
        )
    )


def test_the_brand_statement_reconciles_the_ledger_to_the_brand(inv):
    brand, part = _consignment_world(inv)
    csr = _statement(inv, brand)
    refused(inv, lambda: csr.with_user(inv.keeper).action_submit(), "Compute")
    csr.with_user(inv.keeper).action_compute()
    line = csr.line_ids.filtered(lambda line: line.part_id == part)
    assert (
        line.opening_qty,
        line.received_qty,
        line.consumed_qty,
        line.other_qty,
        line.closing_qty,
    ) == (0.0, 5.0, 1.0, 0.0, 4.0)
    assert csr.state == "computed" and csr.prepared_by_id == inv.keeper
    csr.with_user(inv.keeper).action_submit()
    line.with_user(inv.keeper).write({"brand_qty": 3.0})
    assert csr.variance_qty == -1.0
    refused(inv, lambda: csr.with_user(inv.keeper).action_acknowledge(), "Inventory Controller")
    refused(inv, lambda: csr.with_user(inv.controller).action_acknowledge(), "statement reference")
    csr.with_user(inv.controller).write(
        {
            "statement_ref": "BR-STMT-11",
            "brand_acknowledged_by": "Brand ops",
            "brand_acknowledged_on": fields.Date.today(),
        }
    )
    refused(inv, lambda: csr.with_user(inv.controller).action_acknowledge(), "explain the variance")
    csr.with_user(inv.controller).write(
        {"variance_note": "One panel damaged in brand transit, claim raised"}
    )
    csr.with_user(inv.controller).action_acknowledge()
    assert (csr.state, csr.recorded_by_id) == ("acknowledged", inv.controller)
    assert inv.events("stock.consignment_reconciled", "fix.consignment.reconciliation", csr.id) == 1
    refused(inv, lambda: line.with_user(inv.keeper).write({"brand_qty": 4.0}))
    refused(inv, lambda: csr.with_user(inv.controller).write({"statement_ref": "edited"}), "final")
    # the next statement carries this one's closing and cannot overlap it
    nxt = _statement(inv, brand)
    refused(inv, lambda: nxt.with_user(inv.keeper).action_compute(), "already covers")


def test_the_preparer_does_not_record_the_brands_acknowledgement(inv):
    brand, _part = _consignment_world(inv)
    csr = _statement(inv, brand, inv.controller)
    csr.with_user(inv.controller).action_compute()
    csr.with_user(inv.controller).action_submit()
    csr.with_user(inv.controller).write(
        {
            "statement_ref": "BR-1",
            "brand_acknowledged_by": "Brand",
            "brand_acknowledged_on": fields.Date.today(),
        }
    )
    refused(inv, lambda: csr.with_user(inv.controller).action_acknowledge(), "second person")
    csr.with_user(inv.controller2).action_acknowledge()
    assert csr.state == "acknowledged"


def test_statement_figures_come_from_the_ledger_only(inv):
    brand, part = _consignment_world(inv)
    csr = _statement(inv, brand)
    csr.with_user(inv.keeper).action_compute()
    refused(inv, lambda: csr.line_ids.with_user(inv.keeper).write({"closing_qty": 99.0}))
    refused(inv, lambda: csr.with_user(inv.keeper).write({"state": "acknowledged"}))
    refused(
        inv,
        lambda: csr.with_user(inv.keeper).write(
            {
                "brand_id": inv.env["fix.brand"]
                .create({"name": "Other %s" % inv.tag, "code": "OB%s" % inv.tag})
                .id
            }
        ),
        "Recompute",
    )
