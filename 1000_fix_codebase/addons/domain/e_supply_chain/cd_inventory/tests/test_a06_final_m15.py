# A06 final pass - M15 model controls. Each test attacks the control as a
# NON-ADMIN user holding the real role and asserts the refusal, and shows the
# proper path still works. Item numbers are the final-pass brief's (B1..B19).
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from .conftest import BRANCH, FIN, SK, TECH, make_service_order

REFUSED = (UserError, AccessError, ValidationError)


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _dispatched(inv, qty=5.0, part=None, **line):
    transfer = inv.transfer(inv.keeper, qty=qty, part=part)
    if line:
        transfer.line_ids.with_user(inv.keeper).write(line)
    transfer.with_user(inv.keeper).action_submit()
    transfer.with_user(inv.controller).action_approve()
    transfer.with_user(inv.keeper).action_dispatch()
    return transfer


# ======================================================== B1 serials follow stock
def test_b1_transfer_refuses_a_serialized_line_without_its_serial(inv):
    transfer = inv.transfer(inv.keeper, qty=1.0, part=inv.spart)
    refused(inv, lambda: transfer.with_user(inv.keeper).action_submit(), "serialized")


def test_b1_transfer_moves_the_serial_with_the_stock(inv):
    transfer = _dispatched(inv, qty=1.0, part=inv.spart, lot_id=inv.lot1.id)
    inv.env.invalidate_all()
    assert (inv.lot1.status, inv.lot1.location_id) == ("in_transit", inv.central)
    # on the road: the sender's, but nobody issues it
    issue = inv.issue(
        inv.keeper,
        part=inv.spart,
        serial=inv.lot1.name,
        scanned_code=inv.spart.part_number,
    )
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "not in stock")
    transfer.with_user(inv.keeper2).action_receive()
    inv.env.invalidate_all()
    assert (inv.lot1.status, inv.lot1.location_id) == ("in_stock", inv.hub)
    # issued at its new home, not at the old one
    issue2 = inv.issue(
        inv.keeper,
        part=inv.spart,
        location=inv.hub,
        serial=inv.lot1.name,
        scanned_code=inv.spart.part_number,
    )
    issue2.with_user(inv.keeper).action_scan_and_consume()
    assert inv.lot1.status == "issued"


def test_b1_a_serial_cannot_travel_twice(inv):
    _dispatched(inv, qty=1.0, part=inv.spart, lot_id=inv.lot1.id)
    second = inv.transfer(inv.keeper, qty=1.0, part=inv.spart)
    second.line_ids.with_user(inv.keeper).write({"lot_id": inv.lot1.id})
    refused(inv, lambda: second.with_user(inv.keeper).action_submit(), "cannot move")


def test_b1_rtv_from_unrestricted_closes_the_serial(inv):
    rtv = inv.rtv(inv.keeper, qty=1.0, part_id=inv.spart.id, rtv_ref="RMA-1")
    refused(inv, lambda: rtv.with_user(inv.keeper).action_submit(), "serialized")
    rtv.with_user(inv.keeper).write({"lot_id": inv.lot1.id})
    rtv.with_user(inv.keeper).action_submit()
    rtv.with_user(inv.controller).action_approve()
    rtv.with_user(inv.keeper).action_ship()
    inv.env.invalidate_all()
    assert (inv.lot1.status, inv.lot1.qty) == ("returned", 0.0)


# ======================================================== B3 direct and PO receipts
def _po(inv, qty=5.0, price=200.0):
    env = inv.env
    vendor = env["res.partner"].create({"name": "A06F Vendor " + inv.tag, "is_company": True})
    product = env["product.product"].create({"name": "A06F Display " + inv.tag})
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
    order.write({"state": "sent"})  # trusted setup: approved and sent
    return order, vendor


def test_b3_direct_receipt_needs_a_recorded_reason(inv):
    rec = inv.receipt(inv.keeper, direct_reason=False)
    refused(inv, lambda: rec.with_user(inv.keeper).action_inspect(), "no purchase order")
    rec.with_user(inv.keeper).write({"direct_reason": "Brand free-of-charge replacement"})
    rec.with_user(inv.keeper).action_inspect()
    assert rec.state == "inspected"


def test_b3_only_a_controller_posts_a_direct_receipt(inv):
    rec = inv.receipt(inv.keeper)
    rec.with_user(inv.keeper).action_inspect()
    refused(inv, lambda: rec.with_user(inv.keeper).action_post(), "only an Inventory Controller")
    assert inv.qty(inv.part, inv.hub) == 0.0
    rec.with_user(inv.controller).action_post()
    assert inv.qty(inv.part, inv.hub) == 5.0


def test_b3_a_user_cannot_claim_a_system_handoff_to_skip_the_rule(inv):
    rec = inv.receipt(inv.keeper)
    refused(
        inv,
        lambda: rec.with_user(inv.keeper).write({"source_model": "fix.import.order"}),
        "changes only through its workflow",
    )


def test_b3_po_receipt_cannot_exceed_the_open_quantity(inv):
    order, vendor = _po(inv, qty=5.0)
    rec = inv.receipt(
        inv.keeper,
        rec=6.0,
        acc=6.0,
        purchase_order_id=order.id,
        partner_id=vendor.id,
        direct_reason=False,
    )
    refused(inv, lambda: rec.with_user(inv.keeper).action_inspect(), "open")
    first = inv.receipt(
        inv.keeper,
        rec=3.0,
        acc=3.0,
        purchase_order_id=order.id,
        partner_id=vendor.id,
        direct_reason=False,
    )
    first.with_user(inv.keeper).action_inspect()
    first.with_user(inv.keeper).action_post()  # a storekeeper posts a PO receipt
    second = inv.receipt(
        inv.keeper,
        rec=3.0,
        acc=3.0,
        purchase_order_id=order.id,
        partner_id=vendor.id,
        direct_reason=False,
    )
    refused(inv, lambda: second.with_user(inv.keeper).action_inspect(), "open")
    assert inv.qty(inv.part, inv.hub) == 3.0


def test_b3_po_receipt_takes_the_po_price_not_a_typed_cost(inv):
    order, vendor = _po(inv, qty=5.0, price=200.0)
    rec = inv.receipt(
        inv.controller,
        cost=999.0,
        purchase_order_id=order.id,
        partner_id=vendor.id,
        direct_reason=False,
    )
    rec.with_user(inv.controller).action_inspect()
    rec.with_user(inv.controller).action_post()
    assert inv.bucket(inv.part, inv.hub).unit_cost == 200.0
    assert rec.line_ids.sudo().unit_cost == 200.0


def test_b3_po_receipt_refuses_a_part_the_order_does_not_buy(inv):
    order, vendor = _po(inv)
    rec = inv.receipt(
        inv.keeper,
        part=inv.spart,
        rec=1.0,
        acc=1.0,
        serial="A6F-SN",
        purchase_order_id=order.id,
        partner_id=vendor.id,
        direct_reason=False,
    )
    refused(inv, lambda: rec.with_user(inv.keeper).action_inspect(), "does not order")


def test_b3_draft_po_cannot_be_received_against(inv):
    order, vendor = _po(inv)
    order.write({"state": "draft"})
    rec = inv.receipt(
        inv.keeper, purchase_order_id=order.id, partner_id=vendor.id, direct_reason=False
    )
    refused(inv, lambda: rec.with_user(inv.keeper).action_inspect(), "issued order")


# ======================================================== B4 issue class rules
def _warranty_job(inv, brand_name):
    env = inv.env
    so = make_service_order(env, inv.branch(), inv.tag + "W")
    # trusted set-up: M01's own warranty gate is its suite's (it needs a warranty record)
    env.cr.execute(
        "UPDATE fix_service_order SET order_category = 'warranty' WHERE id = %s", [so.id]
    )
    so.invalidate_recordset(["order_category"])
    so.device_id.device_model_id.brand_id.sudo().write({"name": brand_name})
    return so


def test_b4_consignment_refused_on_a_paid_job(inv):
    inv.stock(inv.part, inv.central, 3.0, 300.0, cls="consignment")
    issue = inv.issue(inv.keeper, issue_class="consignment")
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "BRU-INV-01")
    assert inv.qty(inv.part, inv.central, "consignment") == 3.0


def test_b4_consignment_refused_for_another_brands_warranty_job(inv):
    inv.part.write({"device_brand": "Samsung"})
    inv.stock(inv.part, inv.central, 3.0, 300.0, cls="consignment")
    job = _warranty_job(inv, "Walton " + inv.tag)
    issue = inv.issue(inv.keeper, issue_class="consignment", service_order_ref=job.name)
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "BRU-INV-01")


def test_b4_consignment_goes_on_its_brands_warranty_job_unvalued(inv):
    brand = "Samsung " + inv.tag
    inv.part.write({"device_brand": brand})
    inv.stock(inv.part, inv.central, 3.0, 300.0, cls="consignment")
    job = _warranty_job(inv, brand)
    issue = inv.issue(inv.keeper, issue_class="consignment", service_order_ref=job.name)
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert inv.qty(inv.part, inv.central, "consignment") == 2.0
    assert issue.ownership_class == "consignment"
    assert (
        not issue.env["fix.inventory.valuation.suspense"]
        .sudo()
        .search([("consumption_id", "=", issue.id)])
    ), "BRU-INV-02: consignment is never valued"


def _customer_stock(inv, customer, qty=2.0):
    rec = inv.env["fix.stock.receipt"].create(
        {
            "partner_id": customer.id,
            "location_id": inv.central.id,
            "ownership_class": "customer",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": inv.part.id,
                        "qty_received": qty,
                        "qty_accepted": qty,
                        "unit_cost": 0.0,
                    },
                )
            ],
        }
    )
    rec.action_inspect()
    rec.action_post()
    return rec


def test_b4_customer_stock_goes_only_on_that_customers_job(inv):
    job = inv.job()
    _customer_stock(inv, job.customer_id, qty=2.0)
    stranger = make_service_order(inv.env, inv.branch(), inv.tag + "X")
    other = inv.issue(inv.keeper, issue_class="customer", service_order_ref=stranger.name)
    refused(inv, lambda: other.with_user(inv.keeper).action_scan_and_consume(), "BRU-INV-04")
    own = inv.issue(inv.keeper, issue_class="customer", qty=2.0)
    own.with_user(inv.keeper).action_scan_and_consume()
    assert own.job_customer_id == job.customer_id.commercial_partner_id
    assert inv.qty(inv.part, inv.central, "customer") == 0.0
    # what the customer brought is used up: even with stock of another customer
    # at the location, this job takes no more
    _customer_stock(inv, stranger.customer_id, qty=1.0)
    more = inv.issue(inv.keeper, issue_class="customer", qty=1.0)
    refused(inv, lambda: more.with_user(inv.keeper).action_scan_and_consume(), "BRU-INV-04")


def test_b4_harvested_serial_never_goes_on_warranty_work(inv):
    env = inv.env
    harvest = env["fix.stock.receipt"].create(
        {
            "partner_id": inv.supplier.id,
            "location_id": inv.central.id,
            "source_model": "fix.tradein.harvest",
            "source_res_id": 1,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "part_id": inv.spart.id,
                        "qty_received": 1,
                        "qty_accepted": 1,
                        "unit_cost": 10.0,
                        "line_no": "HARV-" + inv.tag,
                    },
                )
            ],
        }
    )
    harvest.action_inspect()
    harvest.action_post()
    job = _warranty_job(inv, "AnyBrand " + inv.tag)
    issue = inv.issue(
        inv.keeper,
        part=inv.spart,
        serial="HARV-" + inv.tag,
        scanned_code=inv.spart.part_number,
        service_order_ref=job.name,
    )
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "BRU-INV-03")


# ======================================================== B5 technician and approver roles
@pytest.fixture
def tech(inv):
    """A real R10-R12 technician: the van technician group and nothing else."""
    user = inv.user("vantech", TECH)
    emp = inv.env["hr.employee"].create({"name": "A06F Van Tech " + inv.tag, "user_id": user.id})
    van = inv.env["fix.stock.location"].create(
        {
            "name": "A06F Own Van",
            "code": "A6O-" + inv.tag,
            "location_type": "van",
            "technician_id": emp.id,
            "operating_unit_id": inv.ou.id,
        }
    )
    inv.stock(inv.part, van, 4.0, 500.0, cls="van")
    return type("T", (), {"user": user, "emp": emp, "van": van})


def test_b5_technician_issues_from_his_own_van(inv, tech):
    issue = inv.issue(tech.user, location=tech.van, tech=tech.emp)
    issue.with_user(tech.user).action_scan_and_consume()
    assert inv.qty(inv.part, tech.van, "van") == 3.0
    assert issue.state == "consumed"
    issue.with_user(tech.user).action_return_part(reason="excess_draw")
    assert inv.qty(inv.part, tech.van, "van") == 4.0


def test_b5_technician_cannot_write_on_another_van_or_the_store(inv, tech):
    inv.job()  # outside the savepoints below, which would roll it back
    inv.stock(inv.part, inv.van, 2.0, 500.0, cls="van")
    refused(inv, lambda: inv.issue(tech.user, location=inv.van, tech=inv.tech1))
    refused(inv, lambda: inv.issue(tech.user, location=inv.central, tech=tech.emp))
    # a storekeeper's rights are unchanged by the rule
    inv.issue(inv.keeper)


def test_b5_technician_reconciles_only_his_own_van(inv, tech):
    Recon = inv.env["fix.stock.van.recon"]
    refused(inv, lambda: Recon.with_user(tech.user).create({"location_id": inv.van.id}))
    recon = Recon.with_user(tech.user).create({"location_id": tech.van.id, "counted_qty": 4.0})
    recon.with_user(tech.user).action_confirm()
    assert recon.state == "confirmed"


def test_b5_plain_employee_still_cannot_issue(inv):
    refused(inv, lambda: inv.issue(inv.clerk))


def test_b5_branch_approver_decides_transfers_but_not_rtvs(inv):
    approver = inv.user("branchmgr", BRANCH)
    transfer = inv.transfer(inv.keeper)
    transfer.with_user(inv.keeper).action_submit()
    transfer.with_user(approver).action_approve()
    assert (transfer.state, transfer.approved_by_id) == ("approved", approver)
    rtv = inv.rtv(inv.keeper, rtv_ref="RMA-2")
    rtv.with_user(inv.keeper).action_submit()
    refused(inv, lambda: rtv.with_user(approver).action_approve(), "Inventory Controller")


def test_b5_finance_approver_decides_writeoffs_but_not_transfers(inv):
    approver = inv.user("finmgr", FIN)
    scrap = inv.quarantine(inv.keeper, qty=1.0)
    scrap.with_user(inv.keeper).action_request_scrap()
    scrap.with_user(approver).action_approve_scrap(note="seen")
    assert scrap.state == "scrapped"
    transfer = inv.transfer(inv.keeper)
    transfer.with_user(inv.keeper).action_submit()
    refused(inv, lambda: transfer.with_user(approver).action_approve(), "Inventory Controller")


def test_b5_approver_is_still_refused_on_his_own_document(inv):
    approver = inv.user("finkeeper", FIN, SK)
    scrap = inv.quarantine(approver, qty=1.0)
    scrap.with_user(approver).action_request_scrap()
    refused(inv, lambda: scrap.with_user(approver).action_approve_scrap(), "Segregation of duties")


def test_b5_roles_are_mapped(inv):
    env = inv.env
    for role in ("role_r10", "role_r11", "role_r12"):
        assert env.ref(TECH) in env.ref("cd_rbac_ext." + role).group_ids
    assert env.ref(BRANCH) in env.ref("cd_rbac_ext.role_r06").group_ids
    assert env.ref(FIN) in env.ref("cd_rbac_ext.role_r26").group_ids


# ======================================================== B6 custody is the acting user
def test_b6_a_storekeeper_cannot_type_the_custodian_and_draw_from_the_van(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    issue = inv.issue(inv.keeper, location=inv.van, tech=inv.tech1)
    refused(
        inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "only that technician"
    )
    assert inv.qty(inv.part, inv.van, "van") == 3.0


def test_b6_the_custodian_and_a_controller_can(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    issue = inv.issue(inv.keeper, location=inv.van, tech=inv.tech1)
    issue.with_user(inv.techuser).action_scan_and_consume()
    second = inv.issue(inv.keeper, location=inv.van, tech=inv.tech1)
    second.with_user(inv.controller).action_scan_and_consume()
    assert inv.qty(inv.part, inv.van, "van") == 1.0


# ======================================================== B10 blind recon, technician hold
def test_b10_the_counter_cannot_read_expected_or_variance(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    recon = (
        inv.env["fix.stock.van.recon"]
        .with_user(inv.techuser)
        .create({"location_id": inv.van.id, "counted_qty": 3.0})
    )
    with pytest.raises(AccessError):
        recon.with_user(inv.techuser).expected_qty
    with pytest.raises(AccessError):
        recon.with_user(inv.techuser).variance
    with pytest.raises(AccessError):
        recon.with_user(inv.techuser).read(["expected_qty"])
    # an approver reads both
    assert recon.with_user(inv.controller).expected_qty == 3.0
    recon.with_user(inv.techuser).action_confirm()
    assert recon.state == "confirmed"


def test_b10_a_variance_holds_the_technician_not_only_the_van(inv):
    inv.stock(inv.part, inv.van, 3.0, 500.0, cls="van")
    recon = (
        inv.env["fix.stock.van.recon"]
        .with_user(inv.techuser)
        .create({"location_id": inv.van.id, "counted_qty": 1.0})
    )
    recon.with_user(inv.techuser).action_confirm()
    assert recon.state == "discrepancy"
    # the same technician, drawing from the central store, is held too
    elsewhere = inv.issue(inv.keeper, location=inv.central, tech=inv.tech1)
    refused(inv, lambda: elsewhere.with_user(inv.keeper).action_scan_and_consume(), "discrepancy")
    assert inv.qty(inv.part, inv.central) == 10.0
    # another technician at the store is not
    inv.issue(inv.keeper, location=inv.central, tech=inv.tech2).with_user(
        inv.keeper
    ).action_scan_and_consume()
    recon.with_user(inv.controller).action_resolve(note="Recounted: two in the wrong tray")
    elsewhere.with_user(inv.keeper).action_scan_and_consume()
    assert elsewhere.state == "consumed"


# ======================================================== B14 the scan is compared
def test_b14_the_scan_must_read_the_part(inv):
    issue = inv.issue(inv.keeper, scanned_code="SOME-OTHER-PART")
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "Scanned code")
    assert inv.qty(inv.part, inv.central) == 10.0


@pytest.mark.parametrize("field", ["barcode", "qr_code", "part_number"])
def test_b14_barcode_qr_or_part_number_is_accepted(inv, field):
    code = "%s-%s" % (field, inv.tag)
    if field == "part_number":
        code = inv.part.part_number
    else:
        inv.part.write({field: code})
    issue = inv.issue(inv.keeper, scanned_code=code)
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert issue.state == "consumed"


def test_b14_a_serialized_part_may_be_scanned_by_its_serial(inv):
    issue = inv.issue(inv.keeper, part=inv.spart, serial=inv.lot1.name, scanned_code=inv.lot2.name)
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "Scanned code")
    good = inv.issue(inv.keeper, part=inv.spart, serial=inv.lot1.name, scanned_code=inv.lot1.name)
    good.with_user(inv.keeper).action_scan_and_consume()
    assert good.state == "consumed"


# ======================================================== B15 short receipts
def test_b15_receive_moves_what_arrived_and_opens_a_discrepancy(inv):
    transfer = _dispatched(inv, qty=5.0)
    transfer.line_ids.with_user(inv.keeper2).write({"received_qty": 3.0})
    transfer.with_user(inv.keeper2).action_receive()
    assert transfer.state == "discrepancy"
    assert inv.qty(inv.part, inv.hub) == 3.0
    assert inv.qty(inv.part, inv.central, status="in_transit") == 2.0, "still the sender's"
    assert transfer.line_ids.discrepancy_qty == 2.0
    assert inv.events("stock.transfer_received", "fix.stock.transfer", transfer.id) == 1


def test_b15_nothing_arrived_is_a_real_answer(inv):
    transfer = _dispatched(inv, qty=5.0)
    transfer.line_ids.with_user(inv.keeper2).write({"received_qty": 0.0})
    transfer.with_user(inv.keeper2).action_receive()
    assert transfer.state == "discrepancy"
    assert inv.qty(inv.part, inv.hub) == 0.0
    assert inv.qty(inv.part, inv.central, status="in_transit") == 5.0


def test_b15_full_receipt_needs_no_typing(inv):
    transfer = _dispatched(inv, qty=5.0)
    transfer.with_user(inv.keeper2).action_receive()
    assert transfer.state == "received"
    assert inv.qty(inv.part, inv.hub) == 5.0
    assert inv.qty(inv.part, inv.central, status="in_transit") == 0.0


def test_b15_the_received_quantity_is_bounded_and_not_the_dispatchers(inv):
    transfer = _dispatched(inv, qty=5.0)
    line = transfer.line_ids
    refused(inv, lambda: line.with_user(inv.keeper2).write({"received_qty": 9.0}), "between")
    refused(inv, lambda: line.with_user(inv.keeper).write({"received_qty": 1.0}), "Segregation")
    # the rest of a dispatched line stays final
    refused(inv, lambda: line.with_user(inv.keeper2).write({"qty": 1.0}), "final")
    refused(
        inv,
        lambda: transfer.with_user(inv.keeper2).write(
            {"line_ids": [(1, line.id, {"qty": 1.0, "received_qty": 1.0})]}
        ),
        "final",
    )


def test_b15_received_quantity_cannot_be_set_before_arrival(inv):
    transfer = inv.transfer(inv.keeper, qty=5.0)
    refused(
        inv,
        lambda: transfer.line_ids.with_user(inv.keeper).write({"received_qty": 1.0}),
        "recorded when",
    )


def _short(inv):
    transfer = _dispatched(inv, qty=5.0)
    transfer.line_ids.with_user(inv.keeper2).write({"received_qty": 3.0})
    transfer.with_user(inv.keeper2).action_receive()
    return transfer


def test_b15_the_receiver_and_dispatcher_cannot_close_it(inv):
    transfer = _short(inv)
    receiver = inv.user("recvctl", "cd_wms_structure.group_inventory_controller")
    # keeper2 received, and is not an approver anyway
    refused(
        inv,
        lambda: transfer.with_user(inv.keeper2).action_resolve_discrepancy("found", "x"),
        "Inventory Controller",
    )
    transfer.sudo()._guarded().write({"received_by_id": receiver.id})
    refused(
        inv,
        lambda: transfer.with_user(receiver).action_resolve_discrepancy("found", "x"),
        "Segregation",
    )


def test_b15_resolution_and_note_are_required(inv):
    transfer = _short(inv)
    refused(
        inv,
        lambda: transfer.with_user(inv.controller).action_resolve_discrepancy("lost", "x"),
        "resolution",
    )
    refused(
        inv,
        lambda: transfer.with_user(inv.controller).action_resolve_discrepancy("found", " "),
        "Record",
    )


def test_b15_found_goes_on_to_the_destination(inv):
    transfer = _short(inv)
    transfer.with_user(inv.controller).action_resolve_discrepancy("found", "On the next van")
    assert (transfer.state, transfer.discrepancy_resolution) == ("received", "found")
    assert inv.qty(inv.part, inv.hub) == 5.0
    assert inv.qty(inv.part, inv.central, status="in_transit") == 0.0


def test_b15_returned_goes_back_to_the_sender(inv):
    transfer = _short(inv)
    transfer.with_user(inv.controller).action_resolve_discrepancy("returned", "Back on the truck")
    assert inv.qty(inv.part, inv.hub) == 3.0
    assert inv.qty(inv.part, inv.central) == 7.0  # 10 - 5 + 2


def test_b15_quarantine_opens_the_normal_writeoff_path(inv):
    transfer = _short(inv)
    transfer.with_user(inv.controller).action_resolve_discrepancy(
        "quarantine", "Crushed in transit"
    )
    assert inv.qty(inv.part, inv.central, status="quarantine") == 2.0
    scrap = inv.env["fix.stock.quarantine"].search([("source_ref", "=", transfer.name)])
    assert scrap.qty == 2.0 and scrap.state == "quarantined"


def test_b15_short_serial_stays_in_transit_until_resolved(inv):
    transfer = _dispatched(inv, qty=1.0, part=inv.spart, lot_id=inv.lot1.id)
    transfer.line_ids.with_user(inv.keeper2).write({"received_qty": 0.0})
    transfer.with_user(inv.keeper2).action_receive()
    inv.env.invalidate_all()
    assert inv.lot1.status == "in_transit"
    transfer.with_user(inv.controller).action_resolve_discrepancy("found", "Found it")
    inv.env.invalidate_all()
    assert (inv.lot1.status, inv.lot1.location_id) == ("in_stock", inv.hub)


# ======================================================== B16 discontinued / obsolete
def test_b16_discontinued_is_run_down_but_not_bought(inv):
    product = inv.env["product.product"].create({"name": "A06F Retiring " + inv.tag})
    inv.part.product_id = product
    inv.part.with_user(inv.controller).action_discontinue()
    # run-down: still issued (BRU-CAT-10)
    issue = inv.issue(inv.keeper)
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert issue.state == "consumed"
    # no new purchase
    vendor = inv.env["res.partner"].create({"name": "A06F V2 " + inv.tag})
    refused(
        inv,
        lambda: inv.env["fix.purchase.order"].create(
            {
                "operating_unit_id": inv.ou.id,
                "vendor_id": vendor.id,
                "line_ids": [(0, 0, {"product_id": product.id, "qty_ordered": 1, "unit_price": 1})],
            }
        ),
        "no longer purchased",
    )
    # no new stock with no order behind it
    rec = inv.receipt(inv.keeper)
    refused(inv, lambda: rec.with_user(inv.keeper).action_inspect(), "no longer purchased")
    # no reorder
    rule = inv.env["fix.reorder.rule"].create(
        {
            "spare_part_id": inv.part.id,
            "location_id": inv.hub.id,
            "branch_id": inv.branch().id,
            "operating_unit_id": inv.ou.id,
        }
    )
    refused(inv, lambda: rule.action_trigger_reorder(), "not reordered")
    rule.check_replenishment_alerts()
    assert rule.state == "active"


def test_b16_obsolete_is_not_issued(inv):
    inv.part.with_user(inv.controller).action_mark_obsolete()
    issue = inv.issue(inv.keeper)
    refused(inv, lambda: issue.with_user(inv.keeper).action_scan_and_consume(), "obsolete")


# ======================================================== B17 reorder requisition
def test_b17_the_requisition_can_be_converted(inv):
    product = inv.env["product.product"].create({"name": "A06F Reordered " + inv.tag})
    inv.part.product_id = product
    rule = inv.env["fix.reorder.rule"].create(
        {
            "spare_part_id": inv.part.id,
            "location_id": inv.hub.id,
            "branch_id": inv.branch().id,
            "operating_unit_id": inv.ou.id,
            "requester_id": inv.tech1.id,
            "max_qty": 20.0,
        }
    )
    rule.action_trigger_reorder()
    requisition = rule.requisition_id
    assert requisition, "the sweep drafts a requisition"
    assert requisition.product_id == product
    assert requisition.qty == 20.0


# ======================================================== B18 cost is restricted
def test_b18_a_storekeeper_cannot_read_or_write_cost(inv):
    row = inv.bucket(inv.part, inv.central)
    for record, field in (
        (row, "unit_cost"),
        (inv.part, "unit_cost"),
        (inv.part, "average_cost"),
    ):
        with pytest.raises(AccessError):
            record.with_user(inv.keeper)[field]
    with pytest.raises(AccessError):
        row.with_user(inv.keeper).read(["unit_cost"])
    with pytest.raises(AccessError), inv.env.cr.savepoint():
        inv.env["fix.spare.part"].with_user(inv.keeper).create(
            {"name": "c", "part_number": "A6C-" + inv.tag, "unit_cost": 1.0}
        )


def test_b18_the_ledger_still_values_what_a_storekeeper_moves(inv):
    issue = inv.issue(inv.keeper)
    issue.with_user(inv.keeper).action_scan_and_consume()
    assert issue.sudo().unit_cost == 500.0
    with pytest.raises(AccessError):
        issue.with_user(inv.keeper).unit_cost
    transfer = inv.transfer(inv.keeper)
    transfer.with_user(inv.keeper).action_submit()
    with pytest.raises(AccessError):
        transfer.with_user(inv.keeper).transfer_value
    scrap = inv.quarantine(inv.keeper)
    assert scrap.sudo().unit_cost == 500.0
    assert inv.bucket(inv.part, inv.central, status="quarantine").unit_cost == 500.0


def test_b18_controller_and_finance_read_cost(inv):
    row = inv.bucket(inv.part, inv.central)
    finance = inv.user("fincost", FIN)
    assert row.with_user(inv.controller).unit_cost == 500.0
    assert row.with_user(finance).unit_cost == 500.0
    assert inv.part.with_user(finance).average_cost == 500.0


def test_b18_reports_leave_cost_out_for_a_storekeeper(inv):
    from odoo.addons.cd_p03_portal.controllers.a06 import m15

    keeper_env = inv.env(user=inv.keeper.id)
    boss_env = inv.env(user=inv.controller.id)
    assert m15.kpis(keeper_env)["stock_value"] is None
    assert m15.kpis(boss_env)["stock_value"] > 0
    pack = m15.availability(keeper_env)
    assert "unit_cost" not in pack["cols"] and all("unit_cost" not in r for r in pack["rows"])
    assert "unit_cost" in m15.availability(boss_env)["cols"]
    assert "value" not in m15.ownership_classes(keeper_env)["cols"]
    assert m15.valuation_by_class(keeper_env)["rows"] == []
    assert m15.valuation_by_class(boss_env)["rows"]
    assert "value" not in m15.abc_segmentation(keeper_env)["cols"]


# ======================================================== B19 honest valuation
def test_b19_fifo_is_refused(inv):
    row = inv.bucket(inv.part, inv.central)
    refused(inv, lambda: row.sudo().write({"valuation_method": "fifo"}), "FIFO")
    assert row.valuation_method == "wac"


def test_b19_the_report_says_what_runs(inv):
    from odoo.addons.cd_p03_portal.controllers.a06 import m15

    pack = m15.valuation_by_class(inv.env(user=inv.controller.id))
    assert {r["method"] for r in pack["rows"]} == {"WAC (Weighted Average)"}
    assert any("WAC" in note for note in pack["notes"])


def test_migration_makes_stored_rows_honest(inv):
    """Rows already stored at the upgrade: a bucket labelled FIFO, and a line in
    transit whose received_qty 0 would now read as "nothing arrived"."""
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "migrations" / "19.0.1.2.0" / "post-migrate.py"
    spec = importlib.util.spec_from_file_location("a06_final_post_migrate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    row = inv.bucket(inv.part, inv.central)
    transfer = _dispatched(inv, qty=5.0)
    line = transfer.line_ids
    inv.env.flush_all()
    inv.env.cr.execute(
        "UPDATE fix_stock_onhand SET valuation_method = 'fifo' WHERE id = %s", [row.id]
    )
    inv.env.cr.execute(
        "UPDATE fix_stock_transfer_line SET received_qty = 0 WHERE id = %s", [line.id]
    )
    inv.env.invalidate_all()
    assert line.received_qty == 0.0 and row.valuation_method == "fifo"
    module.migrate(inv.env.cr, "19.0.1.1.0")
    inv.env.invalidate_all()
    assert row.valuation_method == "wac"
    assert line.received_qty == 5.0
    transfer.with_user(inv.keeper2).action_receive()
    assert transfer.state == "received" and inv.qty(inv.part, inv.hub) == 5.0


# ======================================================== A5 the count approver's view
def test_a5_the_approver_sees_variance_and_value_the_counter_does_not(inv):
    count = inv.count(inv.keeper, 7.0)
    count.with_user(inv.keeper).action_submit()
    count.line_ids.with_user(inv.keeper).write({"recount_qty": 7.0})
    count.with_user(inv.keeper).write({"reason_code": "loss"})
    count.with_user(inv.keeper).action_submit()
    assert count.state == "to_approve"
    boss = count.with_user(inv.controller)
    assert boss.line_ids.expected_qty == 10.0 and boss.line_ids.variance == -3.0
    assert boss.variance_value == -1500.0 and boss.adjustment_value == 1500.0
    mine = count.with_user(inv.keeper)
    assert mine.line_ids.expected_qty == 0.0 and mine.line_ids.variance == 0.0
    with pytest.raises(AccessError):
        mine.variance_value
    # the sudo read the workspace form makes must not unblind it either
    assert count.with_user(inv.keeper).sudo().line_ids.expected_qty == 0.0
