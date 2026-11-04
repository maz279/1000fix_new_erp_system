# A06 remediation - M15 Spare Parts & Inventory: one test per gap probe of
# working/A06_evidence/probes/m15/probe_m15.py (named after the probe id),
# run as NON-ADMIN users, plus the proper paths showing the legitimate role
# can still do the job. A PASS means the control now holds.
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from .conftest import IC, SK

REFUSED = (UserError, AccessError, ValidationError)
GUARD = "changes only through its workflow"


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _posted_receipt(inv, user=None, **kw):
    user = user or inv.keeper
    rec = inv.receipt(user, **kw)
    rec.with_user(user).action_inspect()
    rec.with_user(user).action_post()
    return rec


def _count_to_approval(inv, counted, user=None, reason="loss", **kw):
    """Counter counts, is asked to recount, recounts the same, gives a reason."""
    user = user or inv.keeper
    count = inv.count(user, counted, **kw)
    count.with_user(user).action_submit()
    assert count.state == "recount"
    count.line_ids.with_user(user).write({"recount_qty": counted})
    count.with_user(user).write({"reason_code": reason})
    count.with_user(user).action_submit()
    assert count.state == "to_approve"
    return count


# =================================================================== part master
def test_m15_01_part_aggregate_qty_not_writable(inv):
    refused(inv, lambda: inv.part.with_user(inv.clerk).write({"qty_available": 9999.0}))
    refused(inv, lambda: inv.part.with_user(inv.keeper).write({"qty_available": 9999.0}), GUARD)
    # the aggregate IS the ledger
    assert inv.part.qty_available == 10.0
    inv.stock(inv.part, inv.hub, 3.0, 500.0)
    assert inv.part.qty_available == 13.0


def test_m15_02_standard_cost_changes_only_by_controller(inv):
    refused(inv, lambda: inv.part.with_user(inv.keeper).write({"unit_cost": 1.0}))
    refused(inv, lambda: inv.part.with_user(inv.keeper).action_set_standard_cost(1.0))
    inv.part.with_user(inv.controller).action_set_standard_cost(450.0)
    assert inv.part.unit_cost == 450.0
    # an issue is valued at the ledger's average cost, not the standard cost
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    assert rec.unit_cost == 500.0


def test_m15_03_part_cannot_be_born_with_stock(inv):
    refused(
        inv,
        lambda: (
            inv.env["fix.spare.part"]
            .with_user(inv.keeper)
            .create({"name": "ghost", "part_number": "A6G-" + inv.tag, "qty_available": 1000.0})
        ),
        GUARD,
    )
    part = (
        inv.env["fix.spare.part"]
        .with_user(inv.keeper)
        .create({"name": "fresh", "part_number": "A6F-" + inv.tag, "unit_cost": 100.0})
    )
    assert part.qty_available == 0.0


def test_m15_04_obsolete_part_not_issued(inv):
    refused(inv, lambda: inv.part.with_user(inv.keeper).action_mark_obsolete())
    inv.part.with_user(inv.controller).action_mark_obsolete()
    rec = inv.issue(inv.keeper)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "obsolete")
    assert inv.qty(inv.part, inv.central) == 10.0


# =================================================================== on-hand ledger
def test_m15_05_onhand_bucket_not_creatable(inv):
    for user in (inv.clerk, inv.keeper, inv.controller):
        refused(
            inv,
            lambda u=user: (
                inv.env["fix.stock.onhand"]
                .with_user(u)
                .create({"part_id": inv.part.id, "location_id": inv.hub.id, "qty": 500.0})
            ),
        )
    assert inv.qty(inv.part, inv.hub) == 0.0


def test_m15_06_onhand_bucket_not_creatable_via_p03(inv):
    res = inv.p03(inv.keeper).write(
        model="fix.stock.onhand",
        values={"part_id": inv.part.id, "location_id": inv.hub.id, "qty": 500, "unit_cost": 500},
    )
    assert "error" in res
    assert inv.qty(inv.part, inv.hub) == 0.0


def test_m15_07_onhand_qty_not_adjustable_via_p03(inv):
    bucket = inv.bucket(inv.part, inv.central)
    res = inv.p03(inv.keeper).write(
        model="fix.stock.onhand", record_id=bucket.id, values={"qty": 100}
    )
    assert "error" in res
    assert inv.qty(inv.part, inv.central) == 10.0


def test_m15_08_onhand_cost_not_revalued_via_p03(inv):
    bucket = inv.bucket(inv.part, inv.central)
    res = inv.p03(inv.controller).write(
        model="fix.stock.onhand", record_id=bucket.id, values={"unit_cost": 5}
    )
    assert "error" in res
    assert inv.bucket(inv.part, inv.central).unit_cost == 500.0


def test_m15_09_ownership_class_changes_only_by_approved_document(inv):
    consignment = inv.stock(inv.part, inv.hub, 5.0, 300.0, cls="consignment")
    res = inv.p03(inv.keeper).write(
        model="fix.stock.onhand", record_id=consignment.id, values={"ownership_class": "owned"}
    )
    assert "error" in res
    refused(inv, lambda: consignment.with_user(inv.keeper).write({"ownership_class": "owned"}))
    # proper path: a class change, approved by a controller who did not request it
    change = (
        inv.env["fix.stock.class.change"]
        .with_user(inv.keeper)
        .create(
            {
                "part_id": inv.part.id,
                "location_id": inv.hub.id,
                "from_class": "consignment",
                "to_class": "owned",
                "qty": 2.0,
                "reason": "bought out of consignment",
            }
        )
    )
    change.with_user(inv.keeper).action_submit()
    refused(inv, lambda: change.with_user(inv.keeper).action_approve())
    change.with_user(inv.controller).action_approve()
    assert change.state == "done" and change.approved_by_id == inv.controller
    assert inv.qty(inv.part, inv.hub, "consignment") == 3.0
    owned = inv.bucket(inv.part, inv.hub)
    assert (owned.qty, owned.unit_cost) == (2.0, 300.0)
    entry = inv.suspense(change.name, "class_change")
    assert entry.total_valuation == 600.0


def test_m15_09b_class_change_requester_cannot_approve(inv):
    inv.stock(inv.part, inv.hub, 5.0, 300.0, cls="consignment")
    change = (
        inv.env["fix.stock.class.change"]
        .with_user(inv.controller)
        .create(
            {
                "part_id": inv.part.id,
                "location_id": inv.hub.id,
                "from_class": "consignment",
                "to_class": "owned",
                "qty": 1.0,
                "reason": "x",
            }
        )
    )
    change.with_user(inv.controller).action_submit()
    refused(inv, lambda: change.with_user(inv.controller).action_approve(), "Segregation")
    change.with_user(inv.controller2).action_approve()
    assert change.state == "done"


def test_m15_10_negative_onhand_refused(inv):
    bucket = inv.bucket(inv.part, inv.central)
    refused(inv, lambda: bucket.with_user(inv.keeper).write({"qty": -1.0}))
    refused(inv, lambda: inv.stock(inv.part, inv.central, -11.0, None), "insufficient")


def test_m15_11_reserved_above_onhand_refused(inv):
    bucket = inv.bucket(inv.part, inv.central)
    refused(inv, lambda: bucket.with_user(inv.keeper).write({"reserved": 11.0}))
    Onhand = inv.env["fix.stock.onhand"]
    refused(inv, lambda: Onhand._fix_reserve(inv.part, inv.central, "owned", 11.0, "X"), "only 10")


# =================================================================== goods receipt
def test_m15_12_draft_receipt_cannot_post(inv):
    rec = inv.receipt(inv.keeper)
    refused(inv, lambda: rec.with_user(inv.keeper).action_post(), "inspected")


def test_m15_13_inspection_needs_accepted_qty(inv):
    rec = inv.receipt(inv.keeper, acc=0.0)
    refused(inv, lambda: rec.with_user(inv.keeper).action_inspect(), "accepted quantity")


def test_m15_14_inspection_not_skipped_by_state_write(inv):
    rec = inv.receipt(inv.keeper)
    refused(inv, lambda: rec.with_user(inv.keeper).write({"state": "inspected"}), GUARD)
    refused(inv, lambda: rec.with_user(inv.keeper).action_post())
    assert inv.qty(inv.part, inv.hub) == 0.0


def test_m15_15_inspection_not_skipped_via_p03(inv):
    rec = inv.receipt(inv.keeper)
    api = inv.p03(inv.keeper)
    assert "error" in api.write(
        model="fix.stock.receipt", record_id=rec.id, values={"state": "inspected"}
    )
    assert (
        api.action(model="fix.stock.receipt", ids=[rec.id], method="action_post")["success"]
        is False
    )
    assert inv.qty(inv.part, inv.hub) == 0.0


def test_m15_16_posted_receipt_line_frozen(inv):
    rec = _posted_receipt(inv, rec=50.0, acc=5.0)
    refused(inv, lambda: rec.line_ids.with_user(inv.keeper).write({"qty_accepted": 50.0}), "final")
    refused(
        inv,
        lambda: rec.with_user(inv.keeper).write(
            {"line_ids": [(0, 0, {"part_id": inv.part.id, "qty_received": 9, "qty_accepted": 9})]}
        ),
        "final",
    )
    assert rec.line_ids.qty_accepted == 5.0


def test_m15_17_receipt_links_its_source_and_is_postable_by_code(inv):
    fields = inv.env["fix.stock.receipt"]._fields
    assert fields["purchase_order_id"].comodel_name == "fix.purchase.order"
    assert {"source_model", "source_res_id", "source_ref"} <= set(fields)
    # contract: a receipt created by code (M16 PO / M44 import) posts as before
    rec = inv.env["fix.stock.receipt"].create(
        {
            "partner_id": inv.supplier.id,
            "location_id": inv.hub.id,
            "source_model": "fix.import.order",
            "source_res_id": 42,
            "source_ref": "IMP/TEST",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": inv.part.id,
                        "qty_received": 4,
                        "qty_accepted": 4,
                        "unit_cost": 250,
                    },
                )
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    assert rec.state == "posted"
    assert inv.qty(inv.part, inv.hub) == 4.0
    assert inv.events("stock.received", "fix.stock.receipt", rec.id) == 1


def test_m15_18_receipt_values_at_weighted_average(inv):
    _posted_receipt(inv, location=inv.central, rec=10.0, acc=10.0, cost=100.0)
    bucket = inv.bucket(inv.part, inv.central)
    assert (bucket.qty, bucket.unit_cost) == (20.0, 300.0)
    assert inv.part.average_cost == 300.0


def test_m15_19_serial_received_once(inv):
    rec = inv.receipt(
        inv.keeper,
        part=inv.spart,
        location=inv.central,
        rec=1,
        acc=1,
        cost=8000,
        serial=inv.lot1.name,
    )
    rec.with_user(inv.keeper).action_inspect()
    refused(inv, lambda: rec.with_user(inv.keeper).action_post(), "already been received")
    assert inv.lot1.qty == 1.0
    # one serial = one unit: a two-unit line for one serial is refused
    two = inv.receipt(
        inv.keeper,
        part=inv.spart,
        location=inv.central,
        rec=2,
        acc=2,
        cost=8000,
        serial="NEW-" + inv.tag,
    )
    two.with_user(inv.keeper).action_inspect()
    refused(inv, lambda: two.with_user(inv.keeper).action_post(), "one serial")
    # proper path: a new serial, one unit
    ok = _posted_receipt(
        inv, part=inv.spart, location=inv.central, rec=1, acc=1, cost=8000, serial="SN3-" + inv.tag
    )
    lot = inv.env["fix.stock.lot"]._fix_find(inv.spart, "SN3-" + inv.tag)
    assert ok.state == "posted" and (lot.qty, lot.status) == (1.0, "in_stock")


def test_m15_20_receipt_books_its_ownership_class(inv):
    rec = _posted_receipt(inv, ownership_class="consignment", cost=400.0)
    assert inv.qty(inv.part, inv.hub, "consignment") == 5.0
    assert inv.qty(inv.part, inv.hub, "owned") == 0.0
    # held stock is never valued (BRU-INV-02)
    assert not inv.suspense(rec.name, "receipt")


# =================================================================== issue to job
def test_ref_m15_21_issue_proper_path(inv):
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    entry = inv.suspense(entry_type="consumption").filtered(lambda e: e.consumption_id == rec)
    assert (inv.part.qty_available, inv.qty(inv.part, inv.central), entry.total_valuation) == (
        9.0,
        9.0,
        500.0,
    )
    assert inv.events("stock.consumed", "fix.stock.consumption", rec.id) == 1


def test_m15_22_issue_needs_stock_at_that_location(inv):
    rec = inv.issue(inv.keeper, location=inv.hub)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "Insufficient")
    assert inv.part.qty_available == 10.0


def test_m15_23_van_issue_reduces_van_stock(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    rec = inv.issue(inv.techuser, location=inv.van)
    rec.with_user(inv.techuser).action_scan_and_consume()
    assert inv.qty(inv.part, inv.van, "van") == 2.0
    assert inv.qty(inv.part, inv.central) == 10.0
    assert rec.ownership_class == "van"


def test_m15_24_serialized_needs_serial(inv):
    rec = inv.issue(inv.keeper, part=inv.spart)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "serialized")


def test_m15_25_serial_issued_once(inv):
    first = inv.issue(inv.keeper, part=inv.spart, serial=inv.lot1.name)
    first.with_user(inv.keeper).action_scan_and_consume()
    second = inv.issue(inv.keeper, part=inv.spart, serial=inv.lot1.name)
    refused(
        inv,
        lambda: second.with_user(inv.keeper).action_scan_and_consume(),
        "cannot be issued again",
    )
    assert inv.qty(inv.spart, inv.central) == 1.0


def test_m15_26_unknown_serial_not_issued(inv):
    rec = inv.issue(inv.keeper, part=inv.spart, serial="NEVER-RECEIVED-999")
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "never received")


def test_m15_27_issue_moves_the_lot(inv):
    rec = inv.issue(inv.keeper, part=inv.spart, serial=inv.lot1.name)
    rec.with_user(inv.keeper).action_scan_and_consume()
    assert (inv.lot1.status, inv.lot1.qty) == ("issued", 0.0)
    assert rec.lot_id == inv.lot1


def test_m15_29_forged_consumed_cannot_create_stock_on_return(inv):
    rec = inv.issue(inv.keeper, qty=5.0)
    refused(inv, lambda: rec.with_user(inv.keeper).write({"state": "consumed"}), GUARD)
    refused(
        inv, lambda: rec.with_user(inv.keeper).action_return_part("excess_draw"), "Only consumed"
    )
    assert inv.qty(inv.part, inv.central) == 10.0


def test_m15_30_consumed_state_not_forged_via_p03(inv):
    rec = inv.issue(inv.keeper)
    res = inv.p03(inv.keeper).write(
        model="fix.stock.consumption", record_id=rec.id, values={"state": "consumed"}
    )
    assert "error" in res and rec.state == "draft"


def test_m15_31_issued_record_is_final(inv):
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    refused(inv, lambda: rec.with_user(inv.keeper).write({"unit_cost": 1.0}), GUARD)
    refused(inv, lambda: rec.with_user(inv.keeper).write({"quantity": 0.01}), "final")
    assert (rec.unit_cost, rec.quantity) == (500.0, 1.0)


def test_m15_32_return_at_issue_cost(inv):
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    # stock received later at another cost moves the average, not the return
    _posted_receipt(inv, location=inv.central, rec=9.0, acc=9.0, cost=900.0)
    rec.with_user(inv.keeper).action_return_part("excess_draw")
    rows = inv.suspense(entry_type=False).filtered(lambda e: e.consumption_id == rec)
    assert abs(sum(rows.mapped("total_valuation"))) < 0.01


def test_m15_33_defective_return_goes_to_quarantine(inv):
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    out = rec.with_user(inv.keeper).action_return_part("defective_new", "DOA out of box")
    assert inv.qty(inv.part, inv.central) == 9.0
    assert inv.qty(inv.part, inv.central, status="quarantine") == 1.0
    quarantine = inv.env["fix.stock.quarantine"].search([("name", "=", out["quarantine"])])
    assert quarantine.state == "quarantined" and quarantine.qty == 1.0


def test_m15_34_quarantined_stock_not_issued(inv):
    inv.quarantine(inv.keeper, qty=10.0, reason="suspect")
    rec = inv.issue(inv.keeper, qty=10.0)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "Insufficient")


def test_m15_35_van_issue_only_for_its_custodian(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    rec = inv.issue(inv.keeper, location=inv.van, tech=inv.tech2)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "custody")


def test_m15_36_van_discrepancy_holds_the_next_issue(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    recon = (
        inv.env["fix.stock.van.recon"]
        .with_user(inv.techuser)
        .create({"location_id": inv.van.id, "counted_qty": 1})
    )
    recon.with_user(inv.techuser).action_confirm()
    assert recon.state == "discrepancy"
    rec = inv.issue(inv.techuser, location=inv.van)
    refused(inv, lambda: rec.with_user(inv.techuser).action_scan_and_consume(), "discrepancy")
    refused(inv, lambda: recon.with_user(inv.techuser).action_resolve("found it"))
    recon.with_user(inv.controller).action_resolve("two units used on SO-1, count booked")
    rec.with_user(inv.techuser).action_scan_and_consume()
    assert inv.qty(inv.part, inv.van, "van") == 2.0


def test_m15_37_fractional_pieces_refused(inv):
    rec = inv.issue(inv.keeper, qty=0.25)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "whole pieces")


def test_m15_38_negative_issue_refused(inv):
    rec = inv.issue(inv.keeper, qty=-5.0)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "positive")
    assert inv.qty(inv.part, inv.central) == 10.0


def test_m15_39_inactive_location_moves_nothing(inv):
    refused(inv, lambda: inv.central.with_user(inv.keeper).write({"state": "inactive"}), GUARD)
    inv.central.with_user(inv.keeper).action_set_inactive()
    rec = inv.issue(inv.keeper)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "not active")


def test_m15_40_other_operating_unit_store_refused(inv):
    try:
        with inv.env.cr.savepoint():
            ou2 = inv.env["operating.unit"].create(
                {
                    "name": "A06 OU2 " + inv.tag,
                    "code": "O2" + inv.tag[:4],
                    "partner_id": inv.env.company.partner_id.id,
                }
            )
    except Exception as exc:
        pytest.skip("could not create a second operating unit: %s" % exc)
    loc2 = inv.env["fix.stock.location"].create(
        {"name": "OU2 store", "code": "A6X-" + inv.tag, "operating_unit_id": ou2.id}
    )
    inv.stock(inv.part, loc2, 3.0, 500.0)
    rec = inv.issue(inv.keeper, location=loc2)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume())
    assert inv.qty(inv.part, loc2) == 3.0


# =================================================================== transfers
def test_m15_41_empty_transfer_cannot_move(inv):
    trf = (
        inv.env["fix.stock.transfer"]
        .with_user(inv.keeper)
        .create({"from_location_id": inv.central.id, "to_location_id": inv.hub.id})
    )
    refused(inv, lambda: trf.with_user(inv.keeper).action_submit(), "at least one line")
    refused(inv, lambda: trf.with_user(inv.keeper).action_dispatch())


def _approved_transfer(inv, qty=5.0):
    trf = inv.transfer(inv.keeper, qty=qty)
    trf.with_user(inv.keeper).action_submit()
    trf.with_user(inv.controller).action_approve()
    return trf


def test_m15_42_dispatched_stock_is_in_transit(inv):
    trf = _approved_transfer(inv, qty=10.0)
    trf.with_user(inv.keeper).action_dispatch()
    assert inv.qty(inv.part, inv.central) == 0.0
    assert inv.qty(inv.part, inv.central, status="in_transit") == 10.0
    rec = inv.issue(inv.keeper, qty=10.0)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "Insufficient")
    trf.with_user(inv.keeper2).action_receive()
    assert (trf.state, inv.qty(inv.part, inv.hub)) == ("received", 10.0)
    assert inv.qty(inv.part, inv.central, status="in_transit") == 0.0


def test_m15_43_transfer_needs_approval_and_separate_receiver(inv):
    trf = inv.transfer(inv.keeper)
    refused(inv, lambda: trf.with_user(inv.keeper).action_dispatch(), "approved")
    trf.with_user(inv.keeper).action_submit()
    refused(inv, lambda: trf.with_user(inv.keeper).action_approve())  # not a controller
    trf.with_user(inv.controller).action_approve()
    trf.with_user(inv.keeper).action_dispatch()
    refused(inv, lambda: trf.with_user(inv.keeper).action_receive(), "Segregation")
    trf.with_user(inv.keeper2).action_receive()
    assert (trf.requested_by_id, trf.approved_by_id, trf.dispatched_by_id, trf.received_by_id) == (
        inv.keeper,
        inv.controller,
        inv.keeper,
        inv.keeper2,
    )


def test_m15_43b_requesting_controller_cannot_approve(inv):
    trf = inv.transfer(inv.controller)
    trf.with_user(inv.controller).action_submit()
    refused(inv, lambda: trf.with_user(inv.controller).action_approve(), "Segregation")
    trf.with_user(inv.controller2).action_approve()
    assert trf.state == "approved"


def test_m15_44_received_state_not_forged_via_p03(inv):
    trf = inv.transfer(inv.keeper)
    assert "error" in inv.p03(inv.keeper).write(
        model="fix.stock.transfer", record_id=trf.id, values={"state": "received"}
    )
    assert trf.state == "draft" and inv.qty(inv.part, inv.hub) == 0.0


def test_m15_45_lines_frozen_after_submission(inv):
    trf = _approved_transfer(inv, qty=1.0)
    trf.with_user(inv.keeper).action_dispatch()
    refused(inv, lambda: trf.line_ids.with_user(inv.keeper).write({"qty": 10.0}), "final")
    trf.with_user(inv.keeper2).action_receive()
    assert inv.qty(inv.part, inv.hub) == 1.0


def test_m15_46_transfer_carries_the_source_cost(inv):
    cheap = inv.env["fix.spare.part"].create(
        {"name": "cheap", "part_number": "A6K-" + inv.tag, "unit_cost": 500.0}
    )
    inv.stock(cheap, inv.central, 10.0, 100.0)
    trf = inv.transfer(inv.keeper, qty=5.0, part=cheap)
    trf.with_user(inv.keeper).action_submit()
    trf.with_user(inv.controller).action_approve()
    trf.with_user(inv.keeper).action_dispatch()
    trf.with_user(inv.keeper2).action_receive()
    assert inv.bucket(cheap, inv.hub).unit_cost == 100.0


# =================================================================== blind counts
def test_ref_m15_47_count_proper_path_within_tolerance(inv):
    count = inv.count(inv.keeper, 10.0)
    count.with_user(inv.keeper).action_submit()
    assert count.state == "posted" and inv.qty(inv.part, inv.central) == 10.0
    # a configured tolerance lets a small variance post without approval
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.count_variance_tolerance_pct", "25"
    )
    small = inv.count(inv.keeper, 8.0)
    small.with_user(inv.keeper).action_submit()
    assert small.state == "posted" and inv.qty(inv.part, inv.central) == 8.0
    assert inv.suspense(small.name, "adjustment").total_valuation == -1000.0


def test_m15_48_expected_is_the_systems_and_blind(inv):
    count = inv.count(inv.keeper, 10.0, expected_qty=2.0)  # a typed expected is ignored
    line = count.line_ids
    assert line.with_user(inv.keeper).expected_qty == 0.0  # hidden from the counter
    assert line.with_user(inv.controller).expected_qty == 10.0  # the ledger's
    refused(
        inv, lambda: inv.env["fix.stock.count.snapshot"].with_user(inv.keeper).search([]).read()
    )
    count.with_user(inv.keeper).action_submit()
    assert count.state == "posted" and inv.qty(inv.part, inv.central) == 10.0


def test_m15_49_counter_cannot_approve_his_count(inv):
    count = _count_to_approval(inv, 9.0, user=inv.controller)
    refused(inv, lambda: count.with_user(inv.controller).action_approve(), "Segregation")
    count.with_user(inv.controller2).action_approve()
    assert count.state == "posted" and inv.qty(inv.part, inv.central) == 9.0


def test_m15_50_write_down_needs_recount_reason_and_approval(inv):
    big = inv.env["fix.spare.part"].create(
        {"name": "big", "part_number": "A6B-" + inv.tag, "unit_cost": 50000.0}
    )
    inv.stock(big, inv.central, 10.0, 50000.0)
    count = inv.count(inv.keeper, 0.0, part=big)
    count.with_user(inv.keeper).action_submit()
    assert count.state == "recount" and inv.qty(big, inv.central) == 10.0
    count.line_ids.with_user(inv.keeper).write({"recount_qty": 0.0})
    refused(inv, lambda: count.with_user(inv.keeper).action_submit(), "reason")
    count.with_user(inv.keeper).write({"reason_code": "loss"})
    count.with_user(inv.keeper).action_submit()
    assert count.state == "to_approve" and inv.qty(big, inv.central) == 10.0
    refused(inv, lambda: count.with_user(inv.keeper2).action_approve())  # not a controller
    count.with_user(inv.controller).action_approve()
    assert count.state == "posted" and inv.qty(big, inv.central) == 0.0
    assert inv.suspense(count.name, "adjustment").total_valuation == -500000.0
    assert inv.events("stock.adjusted", "fix.stock.count", count.id) == 1


def test_m15_51_posted_state_not_forged_via_p03(inv):
    count = inv.count(inv.keeper, 3.0)
    assert "error" in inv.p03(inv.keeper).write(
        model="fix.stock.count", record_id=count.id, values={"state": "posted"}
    )
    assert count.state == "draft"


def test_m15_52_posted_count_lines_final(inv):
    count = inv.count(inv.keeper, 10.0)
    count.with_user(inv.keeper).action_submit()
    refused(inv, lambda: count.line_ids.with_user(inv.keeper).write({"counted_qty": 7.0}), "final")
    refused(inv, lambda: count.line_ids.with_user(inv.keeper).unlink(), "final")
    assert len(count.line_ids) == 1


def test_m15_52b_recount_only_in_recount(inv):
    count = inv.count(inv.keeper, 7.0)
    refused(inv, lambda: count.line_ids.with_user(inv.keeper).write({"recount_qty": 10.0}))
    count.with_user(inv.keeper).action_submit()
    refused(inv, lambda: count.line_ids.with_user(inv.keeper).write({"counted_qty": 10.0}))
    count.line_ids.with_user(inv.keeper).write({"recount_qty": 10.0})
    count.with_user(inv.keeper).action_submit()  # the recount matches: posts, no change
    assert count.state == "posted" and inv.qty(inv.part, inv.central) == 10.0


# =================================================================== van reconciliation
def _van_recon(inv, counted, user=None):
    return (
        inv.env["fix.stock.van.recon"]
        .with_user(user or inv.techuser)
        .create({"location_id": inv.van.id, "counted_qty": counted})
    )


def test_m15_53_discrepancy_not_reconfirmed_away(inv):
    inv.stock(inv.part, inv.van, 20.0, 500.0, cls="van")
    recon = _van_recon(inv, 5)
    recon.with_user(inv.techuser).action_confirm()
    refused(inv, lambda: recon.with_user(inv.techuser).write({"counted_qty": 20}), "final")
    refused(inv, lambda: recon.with_user(inv.techuser).action_confirm(), "already been confirmed")
    assert recon.state == "discrepancy"


def test_m15_54_recon_state_not_forged_via_p03(inv):
    recon = _van_recon(inv, 5, user=inv.keeper)
    assert "error" in inv.p03(inv.keeper).write(
        model="fix.stock.van.recon", record_id=recon.id, values={"state": "confirmed"}
    )
    assert recon.state == "draft"


def test_m15_55_van_expected_is_the_ledger(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    recon = (
        inv.env["fix.stock.van.recon"]
        .with_user(inv.techuser)
        .create({"location_id": inv.van.id, "expected_qty": 0, "counted_qty": 0})
    )
    assert recon.expected_qty == 3.0
    recon.with_user(inv.techuser).action_confirm()
    assert recon.state == "discrepancy" and recon.variance == -3.0
    ok = _van_recon(inv, 3)
    ok.with_user(inv.techuser).action_confirm()
    assert ok.state == "confirmed"


def test_m15_56_van_variance_is_published(inv):
    inv.stock(inv.part, inv.van, 10.0, 500.0, cls="van")
    recon = _van_recon(inv, 4)
    recon.with_user(inv.techuser).action_confirm()
    assert inv.events("stock.van_variance_detected", "fix.stock.van.recon", recon.id) == 1


def test_m15_57_recon_only_for_a_van_and_its_custodian(inv):
    refused(
        inv,
        lambda: (
            inv.env["fix.stock.van.recon"]
            .with_user(inv.keeper)
            .create({"location_id": inv.central.id, "counted_qty": 1})
        ),
        "van location",
    )
    refused(
        inv,
        lambda: (
            inv.env["fix.stock.van.recon"]
            .with_user(inv.keeper)
            .create({"location_id": inv.van.id, "technician_id": inv.tech2.id, "counted_qty": 1})
        ),
        "custody",
    )


def test_m15_57b_technician_cannot_resolve_his_van(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    tech_controller = inv.user("techctl", IC)
    inv.tech1.user_id = tech_controller
    recon = _van_recon(inv, 1, user=inv.keeper)
    recon.with_user(inv.keeper).action_confirm()
    refused(inv, lambda: recon.with_user(tech_controller).action_resolve("mine"), "Segregation")


# =================================================================== quarantine / scrap
def test_m15_58_quarantine_segregates_stock(inv):
    inv.quarantine(inv.keeper, qty=4.0, reason="defective")
    bucket = inv.bucket(inv.part, inv.central)
    assert (bucket.qty, bucket.available_qty) == (6.0, 6.0)
    assert inv.qty(inv.part, inv.central, status="quarantine") == 4.0
    assert inv.part.qty_available == 10.0  # still on hand, no longer available


def test_m15_59_write_off_needs_controller_not_quarantiner(inv):
    big = inv.env["fix.spare.part"].create(
        {"name": "big", "part_number": "A6B-" + inv.tag, "unit_cost": 50000.0}
    )
    inv.stock(big, inv.central, 10.0, 50000.0)
    q = inv.quarantine(inv.keeper, qty=10.0, part=big)
    refused(inv, lambda: q.with_user(inv.keeper).action_scrap(), "approval threshold")
    q.with_user(inv.keeper).action_request_scrap()
    refused(inv, lambda: q.with_user(inv.keeper).action_approve_scrap())
    assert inv.qty(big, inv.central, status="quarantine") == 10.0
    q.with_user(inv.controller).action_approve_scrap()
    assert q.state == "scrapped" and q.approved_by_id == inv.controller
    assert inv.qty(big, inv.central, status="quarantine") == 0.0
    assert big.qty_available == 0.0


def test_m15_59b_controller_who_quarantined_cannot_approve(inv):
    q = inv.quarantine(inv.controller, qty=1.0)
    q.with_user(inv.controller).action_request_scrap()
    refused(inv, lambda: q.with_user(inv.controller).action_approve_scrap(), "Segregation")


def test_m15_59c_small_write_off_within_threshold(inv):
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.writeoff_approval_threshold", "1000"
    )
    q = inv.quarantine(inv.keeper, qty=1.0)
    q.with_user(inv.keeper).action_scrap()
    assert q.state == "scrapped" and inv.part.qty_available == 9.0


def test_m15_60_scrapped_state_not_forged_via_p03(inv):
    q = inv.quarantine(inv.keeper, qty=3.0)
    assert "error" in inv.p03(inv.keeper).write(
        model="fix.stock.quarantine", record_id=q.id, values={"state": "scrapped"}
    )
    assert q.state == "quarantined"


def test_m15_61_partial_scrap_keeps_the_rest_of_the_lot(inv):
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.writeoff_approval_threshold", "1000"
    )
    lot = inv.env["fix.stock.lot"].create(
        {
            "name": "A6LOT-" + inv.tag,
            "part_id": inv.part.id,
            "location_id": inv.central.id,
            "qty": 5.0,
        }
    )
    q = inv.quarantine(inv.keeper, qty=1.0, lot_id=lot.id)
    q.with_user(inv.keeper).action_scrap()
    assert (lot.qty, lot.status) == (4.0, "in_stock")


def test_m15_62_scrap_publishes_write_off_and_values_it(inv):
    q = inv.quarantine(inv.keeper, qty=2.0)
    q.with_user(inv.keeper).action_request_scrap()
    q.with_user(inv.controller).action_approve_scrap()
    assert inv.events("stock.written_off", "fix.stock.quarantine", q.id) == 1
    assert inv.suspense(q.name, "write_off").total_valuation == -1000.0


def test_m15_63_scrapped_cannot_be_released(inv):
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.writeoff_approval_threshold", "1000"
    )
    q = inv.quarantine(inv.keeper, qty=1.0)
    q.with_user(inv.keeper).action_scrap()
    refused(inv, lambda: q.with_user(inv.keeper).action_release(), "quarantined")


def test_m15_63b_release_returns_stock(inv):
    q = inv.quarantine(inv.keeper, qty=3.0)
    q.with_user(inv.keeper).action_release()
    assert inv.qty(inv.part, inv.central) == 10.0 and q.state == "released"


# =================================================================== RTV
def test_m15_64_rtv_not_self_approved(inv):
    own = inv.rtv(inv.controller)
    refused(inv, lambda: own.with_user(inv.controller).action_approve(), "Segregation")
    plain = inv.rtv(inv.keeper)
    refused(inv, lambda: plain.with_user(inv.keeper).action_approve())
    plain.with_user(inv.controller).action_approve()
    assert plain.state == "approved" and plain.approved_by_id == inv.controller


def test_m15_65_approved_not_forged_via_p03(inv):
    r = inv.rtv(inv.keeper)
    assert "error" in inv.p03(inv.keeper).write(
        model="fix.stock.rtv", record_id=r.id, values={"state": "approved"}
    )
    assert r.state == "draft"


def test_m15_66_rtv_ships_with_rma(inv):
    r = inv.rtv(inv.keeper)
    r.with_user(inv.controller).action_approve()
    refused(inv, lambda: r.with_user(inv.keeper).action_ship(), "RMA")
    r.with_user(inv.keeper).write({"rtv_ref": "RMA-77"})
    r.with_user(inv.keeper).action_ship()
    assert r.state == "shipped" and inv.qty(inv.part, inv.central) == 8.0


def test_m15_67_rtv_closes_on_credit(inv):
    r = inv.rtv(inv.keeper, rtv_ref="RMA-1")
    r.with_user(inv.controller).action_approve()
    r.with_user(inv.keeper).action_ship()
    refused(inv, lambda: r.with_user(inv.keeper).action_mark_credited(""), "credit")
    r.with_user(inv.keeper).action_mark_credited("CN-2026-0042")
    assert (r.state, r.credit_ref) == ("credited", "CN-2026-0042")


def test_m15_68_draft_rtv_cannot_ship(inv):
    r = inv.rtv(inv.keeper, rtv_ref="RMA-2")
    refused(inv, lambda: r.with_user(inv.keeper).action_ship(), "approved")


def test_m15_89_rtv_pinned_after_approval(inv):
    r = inv.rtv(inv.keeper, qty=1.0, rtv_ref="RMA-3")
    r.with_user(inv.controller).action_approve()
    other = inv.env["res.partner"].create({"name": "accomplice"})
    refused(inv, lambda: r.with_user(inv.keeper).write({"qty": 9.0}), "pinned")
    refused(inv, lambda: r.with_user(inv.keeper).write({"partner_id": other.id}), "pinned")
    r.with_user(inv.keeper).action_ship()
    assert inv.qty(inv.part, inv.central) == 9.0


def test_m15_89b_rtv_of_quarantined_stock(inv):
    q = inv.quarantine(inv.keeper, qty=2.0, reason="defective")
    r = inv.rtv(inv.keeper, qty=2.0, quarantine_id=q.id, rtv_ref="RMA-4")
    r.with_user(inv.keeper).action_submit()
    r.with_user(inv.controller).action_approve()
    r.with_user(inv.keeper).action_ship()
    assert q.state == "returned"
    assert inv.qty(inv.part, inv.central, status="quarantine") == 0.0
    assert inv.qty(inv.part, inv.central) == 8.0


# =================================================================== valuation
def test_m15_69_every_valued_movement_books_suspense(inv):
    receipt = _posted_receipt(inv)
    count = _count_to_approval(inv, 9.0)
    count.with_user(inv.controller).action_approve()
    q = inv.quarantine(inv.keeper, qty=1.0)
    q.with_user(inv.keeper).action_request_scrap()
    q.with_user(inv.controller).action_approve_scrap()
    r = inv.rtv(inv.keeper, qty=1.0, rtv_ref="RMA-5")
    r.with_user(inv.controller).action_approve()
    r.with_user(inv.keeper).action_ship()
    assert inv.suspense(receipt.name, "receipt").total_valuation == 2500.0
    assert inv.suspense(count.name, "adjustment").total_valuation == -500.0
    assert inv.suspense(q.name, "write_off").total_valuation == -500.0
    assert inv.suspense(r.name, "rtv").total_valuation == -500.0


def test_m15_70_issue_valued_at_bucket_cost(inv):
    cheap = inv.env["fix.spare.part"].create(
        {"name": "c", "part_number": "A6Q-" + inv.tag, "unit_cost": 500.0}
    )
    inv.stock(cheap, inv.central, 5.0, 100.0)
    rec = inv.issue(inv.keeper, part=cheap)
    rec.with_user(inv.keeper).action_scan_and_consume()
    assert (
        inv.suspense(entry_type="consumption")
        .filtered(lambda e: e.consumption_id == rec)
        .total_valuation
        == 100.0
    )


def test_m15_71_kpi_excludes_held_stock(inv):
    from odoo.addons.cd_p03_portal.controllers.a06 import m15

    base = m15.kpis(inv.env(user=inv.keeper.id))["stock_value"]
    inv.stock(inv.part, inv.hub, 100.0, 500.0, cls="consignment")
    inv.stock(inv.part, inv.hub, 10.0, 500.0, cls="customer")
    assert m15.kpis(inv.env(user=inv.keeper.id))["stock_value"] == base
    inv.stock(inv.part, inv.hub, 1.0, 500.0)
    assert m15.kpis(inv.env(user=inv.keeper.id))["stock_value"] == pytest.approx(base + 500.0)


def test_m15_72_kpi_stays_in_the_callers_companies(inv):
    from odoo.addons.cd_p03_portal.controllers.a06 import m15

    co2 = inv.env["res.company"].create({"name": "A06 Other Co " + inv.tag})
    loc2 = inv.env["fix.stock.location"].create(
        {"name": "other", "code": "A6Y-" + inv.tag, "company_id": co2.id}
    )
    p2 = inv.env["fix.spare.part"].create(
        {"name": "other", "part_number": "A6Z-" + inv.tag, "company_id": co2.id}
    )
    base = m15.kpis(inv.env(user=inv.keeper.id))["stock_value"]
    inv.stock(p2, loc2, 1000.0, 1000.0)
    assert m15.kpis(inv.env(user=inv.keeper.id))["stock_value"] == base
    rows = m15.valuation_by_class(inv.env(user=inv.keeper.id))["rows"]
    assert not [r for r in rows if r["location"] == loc2.code]


def test_m15_73_suspense_ledger_is_system_only(inv):
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    entry = inv.suspense(entry_type="consumption").filtered(lambda e: e.consumption_id == rec)
    Suspense = inv.env["fix.inventory.valuation.suspense"]
    for user in (inv.clerk, inv.keeper, inv.controller):
        refused(
            inv,
            lambda u=user: entry.with_user(u).write(
                {"status": "reconciled", "total_valuation": 0.0}
            ),
        )
        refused(
            inv,
            lambda u=user: Suspense.with_user(u).create(
                {
                    "product_id": inv.part.id,
                    "quantity": 1000,
                    "unit_cost": 500,
                    "entry_type": "initial_count",
                }
            ),
        )
        refused(inv, lambda u=user: entry.with_user(u).unlink())
        # a typed voucher reconciles nothing outside the M19 cutover
        refused(
            inv, lambda u=user: entry.with_user(u).action_reconcile_to_gl("JV/TYPED"), "cutover"
        )
    assert (entry.status, entry.total_valuation) == ("pending_gl_cutover", 500.0)


# =================================================================== replenishment
def _rule(inv, location=None, mn=5.0, mx=20.0, **kw):
    vals = {
        "spare_part_id": inv.part.id,
        "location_id": (location or inv.central).id,
        "branch_id": inv.branch().id,
        "min_qty": mn,
        "max_qty": mx,
        "operating_unit_id": inv.ou.id,
    }
    vals.update(kw)
    return inv.env["fix.reorder.rule"].with_user(inv.keeper).create(vals)


def test_m15_74_manual_trigger_only_at_reorder_point(inv):
    rule = _rule(inv)  # central holds 10 > min 5
    refused(
        inv, lambda: rule.with_user(inv.keeper).action_trigger_reorder(), "above the reorder point"
    )
    assert rule.state == "active"


def test_m15_75_rule_reads_its_own_location(inv):
    rule = _rule(inv, location=inv.hub)  # hub holds 0 while central holds 10
    assert rule.current_stock == 0.0
    inv.env["fix.reorder.rule"].with_user(inv.keeper).check_replenishment_alerts()
    assert rule.state in ("alert", "ordered")


def test_m15_76_replenishment_sweep_is_scheduled(inv):
    cron = inv.env.ref("cd_inventory.ir_cron_replenishment_sweep")
    assert cron.active and "check_replenishment_alerts" in cron.code
    assert cron.model_id.model == "fix.reorder.rule"


def test_m15_77_one_alert_per_shortage(inv):
    rule = _rule(inv, location=inv.hub)
    Rule = inv.env["fix.reorder.rule"]
    for _sweep in range(3):
        Rule.check_replenishment_alerts()
    assert inv.events("reorder.triggered", "fix.reorder.rule", rule.id) == 1
    # recovery clears the alert; a new shortage alerts again
    inv.stock(inv.part, inv.hub, 6.0, 500.0)
    Rule.check_replenishment_alerts()
    assert rule.state == "active"


def test_m15_78_alert_drafts_a_requisition(inv):
    rule = _rule(inv, location=inv.hub, requester_id=inv.tech1.id)
    rule.with_user(inv.keeper).action_trigger_reorder()
    assert rule.state == "ordered" and rule.requisition_id
    assert rule.requisition_id.state == "draft"
    assert rule.requisition_id.requested_by == inv.tech1


def test_m15_79_alert_not_silenced(inv):
    rule = _rule(inv, location=inv.hub)
    rule.with_user(inv.keeper).action_trigger_reorder()
    assert "error" in inv.p03(inv.keeper).write(
        model="fix.reorder.rule", record_id=rule.id, values={"state": "archived"}
    )
    refused(inv, lambda: rule.with_user(inv.keeper).action_archive_rule(), "alerting")
    assert rule.state in ("alert", "ordered")


def test_m15_80_max_must_exceed_min(inv):
    refused(inv, lambda: _rule(inv, mn=10.0, mx=10.0), "strictly exceed")


def test_m15_81_van_needs_custodian(inv):
    refused(
        inv,
        lambda: (
            inv.env["fix.stock.location"]
            .with_user(inv.keeper)
            .create({"name": "x", "code": "A6W-" + inv.tag, "location_type": "van"})
        ),
        "custodian",
    )


# =================================================================== surfaces / guards / roles
M15_MODELS = [
    "fix.spare.part",
    "fix.stock.location",
    "fix.stock.onhand",
    "fix.stock.lot",
    "fix.stock.consumption",
    "fix.stock.receipt",
    "fix.stock.receipt.line",
    "fix.stock.transfer",
    "fix.stock.transfer.line",
    "fix.stock.count",
    "fix.stock.count.line",
    "fix.stock.van.recon",
    "fix.stock.quarantine",
    "fix.stock.rtv",
    "fix.reorder.rule",
    "fix.inventory.valuation.suspense",
    "fix.stock.class.change",
]


def test_m15_82_every_surface_has_a_whitelist_and_forms_offer_no_workflow_field(inv):
    from odoo.addons.cd_p03_portal.controllers import form_fields
    from odoo.addons.cd_p03_portal.controllers.a06 import m15

    offered_by_forms = form_fields.editable_by_model()
    for model, conf in m15.SURFACES.items():
        assert conf.get("writable") is not None, model
    for model in M15_MODELS:
        guarded = inv.env[model].browse()._fix_guarded_fields()
        offered = guarded & offered_by_forms.get(model, set())
        assert not offered, (model, sorted(offered))


def test_m15_83_models_guarded_and_roles_exist(inv):
    for model in M15_MODELS:
        assert inv.env[model].browse()._fix_guarded_fields(), model
        clerk = inv.env[model].with_user(inv.clerk)
        assert clerk.has_access("read"), model
        assert not clerk.has_access("write") and not clerk.has_access("create"), model
    for model in ("fix.stock.consumption", "fix.stock.receipt", "fix.stock.count"):
        assert inv.env[model].with_user(inv.keeper).has_access("create")
    # the approver group ships empty: who approves is a business appointment
    controller = inv.env.ref(IC)
    assert not (controller.user_ids - inv.env["res.users"].search([("login", "like", "a06inv.%")]))
    assert inv.env.ref("base.user_admin") in inv.env.ref(SK).user_ids


def test_m15_84_posted_receipt_line_not_deletable(inv):
    rec = _posted_receipt(inv)
    refused(inv, lambda: rec.line_ids.with_user(inv.keeper).unlink(), "final")
    assert len(rec.line_ids) == 1


def test_m15_85_lot_status_not_writable(inv):
    inv.lot1.sudo().with_context().write({"status": "quarantined"})
    res = inv.p03(inv.keeper).write(
        model="fix.stock.lot", record_id=inv.lot1.id, values={"status": "in_stock", "qty": 50}
    )
    assert "error" in res
    assert (inv.lot1.status, inv.lot1.qty) == ("quarantined", 1.0)
    refused(inv, lambda: inv.lot1.with_user(inv.keeper).write({"qty": 50}), GUARD)
    refused(inv, lambda: inv.lot1.write({"qty": 2.0}), "one unit")
    inv.lot1.with_user(inv.keeper).write({"warranty_until": "2027-10-01"})


def test_m15_86_return_reachable_from_the_workspace(inv):
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    res = inv.p03(inv.keeper).action(
        model="fix.stock.consumption",
        ids=[rec.id],
        method="action_return_part",
        kwargs={"reason": "excess_draw"},
    )
    assert res["success"], res
    assert rec.state == "returned" and inv.qty(inv.part, inv.central) == 10.0


def test_m15_87_rejected_quantity_goes_to_quarantine(inv):
    rec = _posted_receipt(inv, rec=5.0, acc=3.0)
    line = rec.line_ids
    assert inv.qty(inv.part, inv.hub) == 3.0
    assert inv.qty(inv.part, inv.hub, status="quarantine") == 2.0
    assert line.quarantine_id.qty == 2.0 and line.quarantine_id.state == "quarantined"
    assert inv.part.qty_available == 15.0


def test_m15_88_reserved_stock_not_issued_to_another_job(inv):
    inv.env["fix.stock.onhand"]._fix_reserve(inv.part, inv.central, "owned", 10.0, "SO-RESERVED")
    rec = inv.issue(inv.keeper, qty=10.0)  # another job than the reservation
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "Insufficient")
    assert inv.qty(inv.part, inv.central) == 10.0
