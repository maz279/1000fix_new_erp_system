# A06 ERP audit (20 Nov 2026) - M15 builder stream. One test (or a few) per
# finding id, run as NON-ADMIN users holding the real role; each asserts the
# refusal the new rule makes and that the legitimate path still works. The
# mutation check for each rule re-introduces the defect and expects this file
# to go red (see the stream's report).
import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from .conftest import BRANCH, make_service_order
from .test_a06_m15_handoffs import po_world  # noqa: F401 (fixture)

REFUSED = (UserError, AccessError, ValidationError)


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _set_state(env, record, state, field="state"):
    """Trusted set-up: put a job in a state its own module's suite covers."""
    env.flush_all()
    env.cr.execute(
        "UPDATE %s SET %s = %%s WHERE id = %%s" % (record._table, field), [state, record.id]
    )
    record.invalidate_recordset([field])


def _warranty_job(inv, tag="W"):
    so = make_service_order(inv.env, inv.branch(), inv.tag + tag)
    _set_state(inv.env, so, "warranty", "order_category")
    _set_state(inv.env, so, "in_repair")
    return so


def _po(inv, qty=5.0, price=200.0):
    env = inv.env
    vendor = env["res.partner"].create({"name": "A06E Vendor " + inv.tag, "is_company": True})
    product = env["product.product"].create({"name": "A06E Display " + inv.tag})
    inv.part.product_id = product
    order = env["fix.purchase.order"].create(
        {
            "operating_unit_id": inv.ou.id,
            "vendor_id": vendor.id,
            "line_ids": [
                (0, 0, {"product_id": product.id, "qty_ordered": qty, "unit_price": price})
            ],
        }
    )
    order.write({"state": "sent"})
    return order, vendor


def _reserve(inv, qty, location=None, job=None, user=None):
    res = (
        inv.env["fix.stock.reservation"]
        .with_user(user or inv.keeper)
        .create(
            {
                "part_id": inv.part.id,
                "location_id": (location or inv.central).id,
                "qty": qty,
                "service_order_ref": (job or inv.job()).name,
            }
        )
    )
    res.with_user(user or inv.keeper).action_reserve()
    return res


# ============================================================ A01 (P0)
def test_a01_a_manual_receipt_naming_a_po_is_refused(inv):
    order, vendor = _po(inv)
    rec = inv.receipt(
        inv.keeper, purchase_order_id=order.id, partner_id=vendor.id, direct_reason=False
    )
    refused(inv, lambda: rec.with_user(inv.keeper).action_inspect(), "M16 goods receipt")
    # not even an Inventory Controller, nor trusted code without a hand-off
    refused(inv, lambda: rec.sudo().action_inspect(), "M16 goods receipt")
    assert inv.qty(inv.part, inv.hub) == 0.0
    # a direct receipt without a PO, with its reason, still works
    direct = inv.receipt(inv.keeper)
    direct.with_user(inv.keeper).action_inspect()
    direct.with_user(inv.controller).action_post()
    assert inv.qty(inv.part, inv.hub) == 5.0


# ============================================================ A12
def test_a12_a_line_rejected_whole_is_recorded_into_quarantine(inv):
    rec = inv.receipt(inv.keeper, rec=2.0, acc=0.0)
    rec.with_user(inv.keeper).action_inspect()
    rec.with_user(inv.controller).action_post()
    assert inv.qty(inv.part, inv.hub) == 0.0
    assert inv.qty(inv.part, inv.hub, status="quarantine") == 2.0
    assert rec.line_ids.quarantine_id.qty == 2.0


def test_a12_who_inspected_a_receipt_does_not_post_it(inv):
    rec = inv.receipt(inv.keeper)
    rec.with_user(inv.controller).action_inspect()
    refused(inv, lambda: rec.with_user(inv.controller).action_post(), "Segregation")
    rec.with_user(inv.controller2).action_post()
    assert rec.state == "posted"


# ============================================================ A13
def test_a13_po_goods_are_never_received_as_consignment(inv):
    order, vendor = _po(inv)
    with pytest.raises(ValidationError, match="owned stock"), inv.env.cr.savepoint():
        inv.env["fix.stock.receipt"].sudo().create(
            {
                "partner_id": vendor.id,
                "location_id": inv.hub.id,
                "purchase_order_id": order.id,
                "ownership_class": "consignment",
                "source_model": "fix.purchase.receipt",
                "source_res_id": 1,
            }
        )
        inv.env.flush_all()


# ============================================================ A04 / A05 counts
def test_a04_an_open_count_freezes_the_part_it_counts(inv):
    count = inv.count(inv.keeper, 10.0)
    issue = inv.issue(inv.keeper)
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "being counted")
    # another part at the same location still moves
    other = inv.env["fix.spare.part"].create({"name": "Free", "part_number": "A6X-" + inv.tag})
    inv.stock(other, inv.central, 2.0, 50.0)
    inv.issue(inv.keeper, part=other, scanned_code=other.part_number).with_user(
        inv.keeper
    ).action_scan_and_consume()
    count.with_user(inv.keeper).action_submit()
    assert count.state == "posted"
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert inv.qty(inv.part, inv.central) == 9.0


def test_a04_a_full_count_locks_the_location(inv):
    other = inv.env["fix.spare.part"].create({"name": "Other", "part_number": "A6Y-" + inv.tag})
    inv.stock(other, inv.central, 2.0, 50.0)
    count = (
        inv.env["fix.stock.count"]
        .with_user(inv.keeper)
        .create(
            {
                "location_id": inv.central.id,
                "count_type": "full",
                "operating_unit_id": inv.ou.id,
                "line_ids": [(0, 0, {"part_id": inv.part.id, "counted_qty": 10.0})],
            }
        )
    )
    issue = inv.issue(inv.keeper, part=other, scanned_code=other.part_number)
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "full count")
    # an abandoned count is cancelled by its counter, which lifts the lock
    refused(inv, lambda: count.with_user(inv.keeper2).action_cancel(), "Only who raised")
    count.with_user(inv.keeper).action_cancel()
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert inv.qty(other, inv.central) == 1.0


def _count_to_post(inv, counted):
    count = inv.count(inv.keeper, counted)
    count.with_user(inv.keeper).action_submit()
    count.line_ids.with_user(inv.keeper).write({"recount_qty": counted})
    count.with_user(inv.keeper).write({"reason_code": "loss"})
    count.with_user(inv.keeper).action_submit()
    count.with_user(inv.controller).action_approve()
    return count


def test_a05_a_count_loss_takes_free_stock_before_a_reservation(inv):
    _set_state(inv.env, inv.job(), "in_repair")
    res = _reserve(inv, 3.0)
    count = _count_to_post(inv, 8.0)  # loss of 2, free stock 7
    assert count.state == "posted"
    assert res.state == "active" and inv.bucket(inv.part, inv.central).reserved == 3.0
    assert inv.qty(inv.part, inv.central) == 8.0


def test_a05_a_larger_loss_releases_the_reservation_on_the_record(inv):
    _set_state(inv.env, inv.job(), "in_repair")
    res = _reserve(inv, 9.0)
    count = _count_to_post(inv, 2.0)  # loss of 8, free stock 1
    assert count.state == "posted"
    assert res.state == "released" and count.name in res.release_reason
    assert res in count.released_reservation_ids
    bucket = inv.bucket(inv.part, inv.central)
    assert (bucket.qty, bucket.reserved) == (2.0, 0.0)


def test_a05_reserved_stock_no_reservation_explains_is_never_taken(inv):
    inv.env["fix.stock.onhand"]._fix_reserve(inv.part, inv.central, "owned", 9.0, "WAVE/1")
    count = inv.count(inv.keeper, 2.0)
    count.with_user(inv.keeper).action_submit()
    count.line_ids.with_user(inv.keeper).write({"recount_qty": 2.0})
    count.with_user(inv.keeper).write({"reason_code": "loss"})
    count.with_user(inv.keeper).action_submit()
    refused(inv, lambda: count.with_user(inv.controller).action_approve(), "warehouse picks")
    assert inv.qty(inv.part, inv.central) == 10.0


def test_a05_a_reservation_whose_stock_already_left_is_still_released(inv):
    _set_state(inv.env, inv.job(), "in_repair")
    res = _reserve(inv, 3.0)
    bucket = inv.bucket(inv.part, inv.central)
    inv.env.cr.execute("UPDATE fix_stock_onhand SET reserved = 0 WHERE id = %s", [bucket.id])
    inv.env.invalidate_all()
    res.with_user(inv.keeper).action_release("done")
    assert res.state == "released" and "still held" in res.release_reason


def test_a05_one_bad_reservation_never_stops_the_expiry_sweep(inv, monkeypatch):
    _set_state(inv.env, inv.job(), "in_repair")
    first, second = _reserve(inv, 1.0), _reserve(inv, 1.0)
    past = fields.Datetime.now().replace(year=2020)
    (first | second).sudo()._guarded().write({"expires_at": past})
    Model = type(inv.env["fix.stock.reservation"])
    original = Model._release_open

    def broken(self, state, reason, displaced_by=None):
        if self == first:
            raise UserError("simulated failure")
        return original(self, state, reason, displaced_by)

    monkeypatch.setattr(Model, "_release_open", broken)
    done = inv.env["fix.stock.reservation"]._cron_expire()
    assert done >= 1 and second.state == "expired" and first.state == "active"


# ============================================================ A09
def test_a09_no_return_from_a_delivered_job(inv):
    _set_state(inv.env, inv.job(), "in_repair")
    issue = inv.issue(inv.keeper)
    issue.with_user(inv.keeper).action_scan_and_consume()
    _set_state(inv.env, inv.job(), "delivered")
    refused(
        inv,
        lambda: issue.with_user(inv.keeper).action_return_part(reason="excess_draw"),
        "finished job",
    )
    assert issue.state == "consumed"


def test_a09_a_job_being_cancelled_returns_its_parts_into_the_stores_hands(inv):
    _set_state(inv.env, inv.job(), "in_repair")
    issue = inv.issue(inv.keeper)
    issue.with_user(inv.keeper).action_scan_and_consume()
    _set_state(inv.env, inv.job(), "cancelled")
    refused(
        inv,
        lambda: issue.with_user(inv.clerk).action_return_part(reason="excess_draw"),
        "storekeeper",
    )
    issue.with_user(inv.keeper).action_return_part(reason="excess_draw")
    assert issue.state == "returned" and inv.qty(inv.part, inv.central) == 10.0


# ============================================================ A10
def test_a10_quarantine_is_released_by_qm_or_controller_only(inv):
    q = inv.quarantine(inv.keeper, qty=2.0)
    refused(inv, lambda: q.with_user(inv.keeper).action_release(), "Quality Manager")
    q.with_user(inv.controller).action_release()
    assert q.state == "released" and inv.qty(inv.part, inv.central) == 10.0


# ============================================================ A11
def _van_world(inv):
    other = inv.env["fix.spare.part"].create(
        {"name": "Van Cable", "part_number": "A6VC-" + inv.tag}
    )
    inv.stock(inv.part, inv.van, 5.0, 500.0, cls="van")
    inv.stock(other, inv.van, 3.0, 100.0, cls="van")
    return other


def test_a11_a_van_is_counted_part_by_part_and_the_approval_corrects_the_ledger(inv):
    other = _van_world(inv)
    inv.env["ir.config_parameter"].sudo().set_param("cd_inventory.van_variance_tolerance_pct", "1")
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.writeoff_approval_threshold", "5000"
    )
    recon = (
        inv.env["fix.stock.van.recon"]
        .with_user(inv.techuser)
        .create(
            {
                "location_id": inv.van.id,
                "line_ids": [
                    (0, 0, {"part_id": inv.part.id, "counted_qty": 6.0}),
                    (0, 0, {"part_id": other.id, "counted_qty": 2.0}),
                ],
            }
        )
    )
    recon.with_user(inv.techuser).action_confirm()
    assert recon.state == "discrepancy"
    lines = {ln.part_id: ln.sudo() for ln in recon.line_ids}
    assert (lines[inv.part].variance, lines[other].variance) == (1.0, -1.0)
    # the total pieces agree (8 = 8): only the per-part count finds it
    assert recon.sudo().variance == 0.0
    assert recon.sudo().variance_value == 400.0
    refused(inv, lambda: recon.with_user(inv.techuser).action_resolve("ok"))
    recon.with_user(inv.controller).action_resolve("Cable found missing, surplus display")
    assert recon.state == "resolved" and recon.ledger_corrected
    assert inv.qty(inv.part, inv.van, "van") == 6.0
    assert inv.qty(other, inv.van, "van") == 2.0
    assert inv.suspense(recon.name, "adjustment")


def test_a11_a_total_count_of_a_stocked_van_is_refused(inv):
    _van_world(inv)
    recon = (
        inv.env["fix.stock.van.recon"]
        .with_user(inv.techuser)
        .create({"location_id": inv.van.id, "counted_qty": 8.0})
    )
    refused(inv, lambda: recon.with_user(inv.techuser).action_confirm(), "Count each part")


def test_a11_a_variance_above_the_writeoff_limit_is_not_the_branchs(inv):
    _van_world(inv)
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.writeoff_approval_threshold", "1000"
    )
    recon = (
        inv.env["fix.stock.van.recon"]
        .with_user(inv.techuser)
        .create(
            {
                "location_id": inv.van.id,
                "line_ids": [(0, 0, {"part_id": inv.part.id, "counted_qty": 1.0})],
            }
        )
    )
    recon.with_user(inv.techuser).action_confirm()
    branch = inv.user("branchappr", BRANCH)
    refused(inv, lambda: recon.with_user(branch).action_resolve("lost"), "write-off threshold")
    recon.with_user(inv.controller).action_resolve("lost on the road")
    assert inv.qty(inv.part, inv.van, "van") == 1.0


# ============================================================ A14 / A15 / A16
def test_a14_consignment_moves_and_returns_as_consignment(inv):
    inv.stock(inv.part, inv.central, 4.0, 0.0, cls="consignment")
    transfer = (
        inv.env["fix.stock.transfer"]
        .with_user(inv.keeper)
        .create(
            {
                "from_location_id": inv.central.id,
                "to_location_id": inv.hub.id,
                "ownership_class": "consignment",
                "line_ids": [(0, 0, {"part_id": inv.part.id, "qty": 2.0})],
            }
        )
    )
    transfer.with_user(inv.keeper).action_submit()
    if transfer.state == "submitted":
        transfer.with_user(inv.controller).action_approve()
    transfer.with_user(inv.keeper).action_dispatch()
    transfer.with_user(inv.keeper2).action_receive()
    assert inv.qty(inv.part, inv.hub, "consignment") == 2.0
    assert inv.qty(inv.part, inv.hub) == 0.0
    rtv = inv.rtv(inv.keeper, qty=1.0, ownership_class="consignment")
    rtv.with_user(inv.keeper).action_submit()
    rtv.with_user(inv.controller).action_approve()
    rtv.with_user(inv.keeper).write({"rtv_ref": "RMA-1"})
    rtv.with_user(inv.keeper).action_ship()
    assert inv.qty(inv.part, inv.central, "consignment") == 1.0
    assert inv.qty(inv.part, inv.central) == 10.0


def test_a15_customer_property_and_own_stock_are_not_reclassed(inv):
    Change = inv.env["fix.stock.class.change"].with_user(inv.keeper)
    for frm, to in (("customer", "owned"), ("owned", "consignment"), ("owned", "van")):
        rec = Change.create(
            {
                "part_id": inv.part.id,
                "location_id": inv.central.id,
                "from_class": frm,
                "to_class": to,
                "qty": 1.0,
                "reason": "test",
            }
        )
        refused(inv, lambda r=rec: r.action_submit(), "does not change")
    inv.stock(inv.part, inv.central, 2.0, 300.0, cls="consignment")
    ok = Change.create(
        {
            "part_id": inv.part.id,
            "location_id": inv.central.id,
            "from_class": "consignment",
            "to_class": "owned",
            "qty": 1.0,
            "reason": "bought from the consignor",
        }
    )
    ok.action_submit()
    ok.with_user(inv.controller).action_approve()
    assert ok.state == "done"


def test_x20_a_transfer_never_crosses_companies(inv):
    other = inv.env["res.company"].create({"name": "A06E Other Co " + inv.tag})
    foreign = inv.env["fix.stock.location"].create(
        {"name": "Foreign", "code": "A6F-" + inv.tag, "company_id": other.id}
    )
    with pytest.raises(ValidationError, match="between companies"), inv.env.cr.savepoint():
        inv.env["fix.stock.transfer"].create(
            {
                "from_location_id": inv.central.id,
                "to_location_id": foreign.id,
                "line_ids": [(0, 0, {"part_id": inv.part.id, "qty": 1.0})],
            }
        )
        inv.env.flush_all()


def test_a16_an_inter_ou_transfer_moves_its_value_between_ous(inv):
    ou2 = inv.env["operating.unit"].create(
        {
            "name": "A06E OU2 " + inv.tag,
            "code": "E2" + inv.tag[:4],
            "partner_id": inv.env.company.partner_id.id,
            "company_id": inv.env.company.id,
        }
    )
    far = inv.env["fix.stock.location"].create(
        {"name": "Far", "code": "A6FAR-" + inv.tag, "operating_unit_id": ou2.id}
    )
    transfer = inv.env["fix.stock.transfer"].create(
        {
            "from_location_id": inv.central.id,
            "to_location_id": far.id,
            "line_ids": [(0, 0, {"part_id": inv.part.id, "qty": 2.0})],
        }
    )
    transfer.action_submit()
    if transfer.state == "submitted":
        transfer.action_approve()
    transfer.action_dispatch()
    transfer.action_receive()
    rows = inv.suspense(transfer.name, "transfer")
    assert sorted(rows.mapped("total_valuation")) == [-1000.0, 1000.0]
    assert set(rows.mapped("operating_unit_id")) == {inv.ou, ou2}
    # inside one OU nothing is booked
    same = inv.transfer(inv.keeper, qty=1.0)
    same.with_user(inv.keeper).action_submit()
    if same.state == "submitted":
        same.with_user(inv.controller).action_approve()
    same.with_user(inv.keeper).action_dispatch()
    same.with_user(inv.keeper2).action_receive()
    assert not inv.suspense(same.name, "transfer")


# ============================================================ A20 movement ledger
def test_a20_every_movement_is_on_the_immutable_ledger(inv):
    _set_state(inv.env, inv.job(), "in_repair")
    issue = inv.issue(inv.keeper)
    issue.with_user(inv.keeper).action_scan_and_consume()
    log = inv.env["fix.stock.move.log"].sudo().search([("reference", "=", issue.name)])
    assert log and log.qty == -1.0 and log.balance_qty == 9.0 and log.unit_cost == 500.0
    assert log.res_model == "fix.stock.consumption" and log.res_id == issue.id
    refused(inv, lambda: log.write({"qty": 5.0}), "final")
    refused(inv, lambda: log.unlink(), "final")
    refused(
        inv,
        lambda: inv.env["fix.stock.move.log"]
        .sudo()
        .create({"part_id": inv.part.id, "location_id": inv.central.id}),
        "written by stock movements",
    )


# ============================================================ A28 / D3 issue gates
def test_a28_a_direct_issue_needs_a_job_in_repair(inv):
    issue = inv.issue(inv.keeper)  # the fixture's job is a draft order
    _set_state(inv.env, inv.job(), "draft")
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "only while")
    _set_state(inv.env, inv.job(), "in_repair")
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert issue.state == "consumed"


def test_d3_a_warranty_job_draws_only_from_a_warranty_store(inv):
    job = _warranty_job(inv)
    issue = inv.issue(inv.keeper, service_order_ref=job.name)
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "warranty store")
    wstore = inv.env["fix.stock.location"].create(
        {
            "name": "Warranty",
            "code": "A6W-" + inv.tag,
            "stock_type": "warranty",
            "operating_unit_id": inv.ou.id,
        }
    )
    inv.stock(inv.part, wstore, 2.0, 500.0)
    ok = inv.issue(inv.keeper, service_order_ref=job.name, location=wstore)
    ok.with_user(inv.keeper).action_scan_and_consume()
    assert ok.state == "consumed"
    # and a paid job never draws from it
    _set_state(inv.env, inv.job(), "in_repair")
    paid = inv.issue(inv.keeper, location=wstore)
    refused(inv, lambda: paid.with_user(inv.keeper).action_scan_and_consume(), "warranty store")


def test_a30_the_governed_brand_decides_a_consignment_issue(inv):
    brand = inv.env["fix.brand"].create({"name": "GovBrand " + inv.tag, "code": "GB" + inv.tag})
    job = _warranty_job(inv)
    job.device_id.device_model_id.sudo().write({"brand_id": brand.id})
    inv.part.write({"device_brand": "Some Legacy Text", "brand_id": brand.id})
    wstore = inv.env["fix.stock.location"].create(
        {
            "name": "Warranty",
            "code": "A6W2-" + inv.tag,
            "stock_type": "warranty",
            "operating_unit_id": inv.ou.id,
        }
    )
    inv.stock(inv.part, wstore, 2.0, 0.0, cls="consignment")
    issue = inv.issue(
        inv.keeper, service_order_ref=job.name, location=wstore, issue_class="consignment"
    )
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert issue.state == "consumed"


# ============================================================ X19 / D4
def test_x19_uncosted_stock_is_issued_only_on_a_controllers_approval(inv):
    _set_state(inv.env, inv.job(), "in_repair")
    free = inv.env["fix.spare.part"].create({"name": "Uncosted", "part_number": "A6Z-" + inv.tag})
    inv.stock(free, inv.central, 3.0, 0.0)
    issue = inv.issue(inv.keeper, part=free, scanned_code=free.part_number)
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "no cost")
    refused(inv, lambda: issue.with_user(inv.keeper).action_approve_zero_cost(), "Inventory")
    issue.with_user(inv.controller).action_approve_zero_cost("priced next week")
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert issue.state == "consumed"


def test_x19_an_uncosted_count_variance_is_approved_even_within_tolerance(inv):
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.count_variance_tolerance_pct", "50"
    )
    free = inv.env["fix.spare.part"].create({"name": "Uncosted", "part_number": "A6Q-" + inv.tag})
    inv.stock(free, inv.central, 10.0, 0.0)
    count = inv.count(inv.keeper, 9.0, part=free)
    count.with_user(inv.keeper).action_submit()
    assert count.state == "recount", "a 10% variance inside a 50% tolerance still needs approval"


# ============================================================ A34 / A36
def test_a34_cancel_and_credit_need_their_role(inv):
    transfer = inv.transfer(inv.keeper)
    refused(inv, lambda: transfer.with_user(inv.keeper2).action_cancel(), "Only who raised")
    transfer.with_user(inv.keeper).action_cancel()
    rtv = inv.rtv(inv.keeper, qty=1.0)
    rtv.with_user(inv.keeper).action_submit()
    rtv.with_user(inv.controller).action_approve()
    rtv.with_user(inv.keeper).write({"rtv_ref": "RMA-2"})
    rtv.with_user(inv.keeper).action_ship()
    refused(inv, lambda: rtv.with_user(inv.keeper).action_mark_credited("CN-1"), "credit")
    rtv.with_user(inv.controller).action_mark_credited("CN-1")
    assert rtv.state == "credited"


def test_a36_a_storekeeper_cannot_name_a_vans_custodian_on_create(inv):
    refused(
        inv,
        lambda: inv.env["fix.stock.location"]
        .with_user(inv.keeper)
        .create(
            {
                "name": "My van",
                "code": "A6MV-" + inv.tag,
                "location_type": "van",
                "technician_id": inv.tech1.id,
                "operating_unit_id": inv.ou.id,
            }
        ),
        "custodian",
    )


# ============================================================ D7 / A25 / M43-02/03
def _rule(inv, location, **kw):
    vals = {
        "spare_part_id": inv.part.id,
        "location_id": location.id,
        "branch_id": inv.branch().id,
        "operating_unit_id": inv.ou.id,
        "min_qty": 5.0,
        "max_qty": 8.0,
        "requester_id": inv.tech2.id,
    }
    vals.update(kw)
    return inv.env["fix.reorder.rule"].create(vals)


def test_d7_a_van_below_its_minimum_gets_a_transfer_not_a_requisition(inv):
    inv.van.sudo().write({"supply_location_id": inv.central.id})
    rule = _rule(inv, inv.van)
    out = inv.env["fix.reorder.rule"].check_replenishment_alerts()
    assert out["alerts_triggered"] >= 1
    assert rule.state == "ordered" and rule.transfer_id and not rule.requisition_id
    line = rule.transfer_id.line_ids
    assert (rule.transfer_id.from_location_id, line.qty) == (inv.central, 8.0)
    # the transfer is on its way to the van: the position counts it
    rule._compute_position()
    assert rule.in_transit_qty == 8.0 and rule.position_qty == 8.0


def test_d7_a_store_with_no_warehouse_to_draw_from_fails_closed(inv):
    rule = _rule(inv, inv.hub)
    inv.central.sudo().write({"location_type": "branch"})  # no central store any more
    rule.action_trigger_reorder()
    assert rule.state == "alert" and not rule.transfer_id and not rule.requisition_id
    assert "Replenished From" in rule.message_ids[:1].body


def test_d7_a_warehouse_buys_and_nets_what_is_on_order(inv):
    product = inv.env["product.product"].create({"name": "A06E Buy " + inv.tag})
    inv.part.product_id = product
    rule = _rule(inv, inv.central, min_qty=12.0, max_qty=20.0)
    rule.action_trigger_reorder()
    assert rule.state == "ordered" and rule.requisition_id and not rule.transfer_id
    assert rule.requisition_id.qty == 10.0
    # the open requisition is on order: a second rule for the same part and
    # branch at the warehouse sees the position, not just the shelf
    rule._compute_position()
    assert rule.on_order_qty == 10.0 and rule.position_qty == 20.0
    # A25: a rejected requisition frees the rule
    _set_state(inv.env, rule.requisition_id, "rejected")
    inv.env["fix.reorder.rule"].check_replenishment_alerts()
    assert rule.state == "ordered" and rule.requisition_id.state != "rejected"


# ============================================================ X21
def test_x21_buckets_carry_their_locations_ou(inv):
    ou2 = inv.env["operating.unit"].create(
        {
            "name": "A06E OU3 " + inv.tag,
            "code": "E3" + inv.tag[:4],
            "partner_id": inv.env.company.partner_id.id,
            "company_id": inv.env.company.id,
        }
    )
    bucket = inv.bucket(inv.part, inv.central)
    inv.env.cr.execute(
        "UPDATE fix_stock_onhand SET operating_unit_id = %s WHERE id = %s", [ou2.id, bucket.id]
    )
    inv.env.invalidate_all()
    result = inv.env["fix.stock.onhand"]._fix_repair_ou_stamps(dry_run=True)
    assert result["buckets"] >= 1
    inv.env["fix.stock.onhand"]._fix_repair_ou_stamps()
    assert inv.bucket(inv.part, inv.central).operating_unit_id == inv.ou
    assert inv.env["fix.stock.onhand"]._fix_repair_ou_stamps(dry_run=True)["buckets"] == 0


# ============================================================ X33 / deployment
def test_x33_the_van_variance_consumer_is_wired_and_tells_the_branch(inv):
    consumer = inv.env.ref("cd_inventory.consumer_van_variance_notify")
    assert consumer.event_type == "stock.van_variance_detected"
    Model = inv.env[consumer.model]
    assert hasattr(Model, consumer.method)
    manager = inv.user("vanmgr")
    inv.van.sudo().write({"branch_id": inv.branch().id})
    inv.branch().manager_id = manager
    _van_world(inv)
    recon = inv.env["fix.stock.van.recon"].create({"location_id": inv.van.id, "counted_qty": 0.0})
    recon.action_confirm()
    assert recon.state == "discrepancy"
    event = {"aggregate_id": recon.id, "payload": {"variance": -8.0}}
    assert getattr(Model, consumer.method)(event) == 1
    assert getattr(Model, consumer.method)(event) == 0  # once per recon
    msg = inv.van.message_ids.filtered(lambda m: recon.name in (m.body or ""))
    assert manager.partner_id in msg.partner_ids


def test_deployment_ledger_and_rules_are_installed(inv):
    env = inv.env
    assert (
        env["ir.model.access"].sudo().search_count([("model_id.model", "=", "fix.stock.move.log")])
    )
    assert env["ir.rule"].sudo().search_count([("model_id.model", "=", "fix.stock.move.log")])
    assert env.ref("cd_inventory.ir_cron_replenishment_sweep").active
    sel = dict(env["fix.inventory.valuation.suspense"]._fields["entry_type"].selection)
    assert "transfer" in sel


# ============================================================ X25 (with A07)
def test_x25_a_capital_purchase_never_becomes_m15_stock(po_world):  # noqa: F811
    """A PO that spends an approved capex request is capitalised (CWIP /
    fixed assets); its goods receipt posts nothing into the M15 ledger."""
    from .test_a06_m15_handoffs import _no_inspection, _receive

    w = po_world
    if "capex_request_id" not in w.po._fields:
        pytest.skip("cd_fixed_asset_ext is not installed")
    _no_inspection(w)
    capex = (
        w.env["fix.capex.request"]
        .sudo()
        .create({"title": "A06E bench " + w.tag, "amount": 1000.0, "justification": "test"})
    )
    # trusted set-up: the capex approval is M49's suite
    w.env.flush_all()
    w.env.cr.execute("UPDATE fix_capex_request SET state = 'approved' WHERE id = %s", [capex.id])
    capex.invalidate_recordset(["state"])
    w.po.sudo().write({"capex_request_id": capex.id})
    grn = _receive(w, {w.prod: 3})
    assert not grn.stock_receipt_ids
    assert w.qty(w.part, w.central) == 10.0
