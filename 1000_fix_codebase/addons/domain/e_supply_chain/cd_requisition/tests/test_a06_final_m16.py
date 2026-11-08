# A06 final pass, M16 controls: the PO goods receipt a user can actually reach,
# the receiving tolerance, the vendor's own delivery date (M16-11), cost centre
# and required-by at intake, and the emergency path with its post-hoc window
# (BRU-PRO-12). Each attack runs as a non-admin user with the real role; each
# control also has its proper path. Rolled back.
import types
from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
GB = "cd_requisition.group_fix_procurement_buyer"
GR = "cd_requisition.group_fix_procurement_receiver"
T = {n: "cd_entity_config.group_dofa_tier_%d" % n for n in range(1, 6)}
SOON = date.today() + timedelta(days=14)
PARAM_TOL = "cd_requisition.receipt_over_tolerance_pct"
PARAM_MAX = "cd_requisition.emergency_max_amount"


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.requester = _user(env, "a06f16_requester")
    x.buyer = _user(env, "a06f16_buyer", [GB])
    x.receiver = _user(env, "a06f16_receiver", [GR])
    x.t2 = _user(env, "a06f16_t2", [T[2]])
    x.cfo = _user(env, "a06f16_cfo", [T[4]])
    x.emp = env["hr.employee"].create({"name": "A06F16 Requester", "user_id": x.requester.id})
    categ = env["product.category"].create({"name": "A06F16 Parts"})
    x.prod = env["product.product"].create({"name": "A06F16 Compressor", "categ_id": categ.id})
    x.prod2 = env["product.product"].create({"name": "A06F16 Fan", "categ_id": categ.id})
    x.vendor = env["res.partner"].create({"name": "A06F16 Vendor", "is_company": True})
    sup = env["fix.supplier"].create(
        {"name": x.vendor.name, "partner_id": x.vendor.id, "status": "active"}
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {
                "supplier_id": sup.id,
                "doc_type": doc_type,
                "state": "valid",
                "valid_to": date.today() + timedelta(days=365),
            }
        )
    return x


def _req(c, amount=20000.0, **kw):
    vals = {
        "operating_unit_id": c.ou.id,
        "requested_by": c.emp.id,
        "description": "A06F16 requisition",
        "justification": "Compressors for AMC visits",
        "estimate_amount": amount,
        "product_id": c.prod.id,
        "qty": 2,
        "vendor_id": c.vendor.id,
        "cost_centre": "CC-SVC-01",
        "required_by": SOON,
    }
    vals.update(kw)
    return c.env["fix.requisition"].with_user(c.requester).create(vals)


def _decide(c, record, approver):
    task = record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "no inbox task for %s" % approver.login
    task.with_user(approver).action_approve(comment="ok")


def _sent_po(c, lines=None):
    """Two-line PO by default, approved and sent."""
    po = (
        c.env["fix.purchase.order"]
        .with_user(c.buyer)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.vendor.id,
                "line_ids": [
                    (0, 0, {"product_id": p.id, "qty_ordered": q, "unit_price": 100.0})
                    for p, q in (lines or [(c.prod, 10), (c.prod2, 4)])
                ],
            }
        )
    )
    po.sudo().action_record_requisition_exception(reason="A06F16 test PO with no requisition")
    po.with_user(c.buyer).action_submit_for_approval(justification="A06F16 stock-out")
    _decide(c, po, c.t2)
    po.with_user(c.buyer).action_send()
    assert po.state == "sent"
    return po


# ------------------------------------------------- A1: the receipt a user reaches
def test_a1_start_receipt_holds_only_the_open_lines_of_that_po(c):
    po = _sent_po(c)
    other = _sent_po(c, [(c.prod2, 3)])
    out = po.with_user(c.receiver).action_start_receipt()
    receipt = po.receipt_ids
    assert receipt.name in out["note"] and receipt.state == "draft"
    assert receipt.line_ids.mapped("po_line_id") == po.line_ids
    assert other.line_ids not in receipt.line_ids.mapped("po_line_id")
    assert sorted(receipt.line_ids.mapped("qty_received")) == [4.0, 10.0]
    # pressed again it does not raise a second draft
    po.with_user(c.receiver).action_start_receipt()
    assert len(po.receipt_ids) == 1
    assert receipt.name in po.receipt_refs


def test_a1_a_part_received_line_offers_only_what_is_still_due(c):
    po = _sent_po(c)
    first = po.line_ids.filtered(lambda ln: ln.product_id == c.prod)
    po.with_user(c.receiver).action_record_receipt({first.id: 6})
    assert po.state == "partially_received"
    po.with_user(c.receiver).action_start_receipt()
    draft = po.receipt_ids.filtered(lambda r: r.state == "draft")
    due = {ln.po_line_id.product_id: ln.qty_received for ln in draft.line_ids}
    assert due == {c.prod: 4.0, c.prod2: 4.0}


def test_a1_start_receipt_needs_a_receiver_and_a_receivable_po(c):
    po = _sent_po(c)
    with pytest.raises(UserError, match="Receiver"):
        po.with_user(c.buyer).action_start_receipt()
    with pytest.raises(UserError, match="Receiver"):
        po.with_user(c.requester).action_start_receipt()
    draft = (
        c.env["fix.purchase.order"]
        .with_user(c.buyer)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.vendor.id,
                "line_ids": [(0, 0, {"product_id": c.prod.id, "qty_ordered": 1, "unit_price": 5})],
            }
        )
    )
    with pytest.raises(UserError, match="sent or acknowledged"):
        draft.with_user(c.receiver).action_start_receipt()


def test_a1_the_buyer_holding_the_receiver_role_still_cannot_post(c):
    po = _sent_po(c)
    c.buyer.write({"group_ids": [(4, c.env.ref(GR).id)]})
    po.with_user(c.buyer).action_start_receipt()
    with pytest.raises(UserError, match="SOD-02"):
        po.receipt_ids.with_user(c.buyer).action_post()
    assert po.state == "sent"
    po.receipt_ids.with_user(c.receiver).action_post()
    assert po.state == "received"


def test_a1_repointing_a_draft_receipt_reloads_the_lines_of_the_new_po(c):
    po, other = _sent_po(c), _sent_po(c, [(c.prod2, 3)])
    receipt = (
        c.env["fix.purchase.receipt"].with_user(c.receiver).create({"purchase_order_id": po.id})
    )
    receipt.with_user(c.receiver).write({"purchase_order_id": other.id})
    assert receipt.line_ids.mapped("po_line_id") == other.line_ids


def test_a1_a_receipt_cannot_receive_another_pos_line(c):
    po, other = _sent_po(c), _sent_po(c, [(c.prod2, 3)])
    receipt = (
        c.env["fix.purchase.receipt"].with_user(c.receiver).create({"purchase_order_id": po.id})
    )
    with pytest.raises(UserError, match="own PO"):
        c.env["fix.purchase.receipt.line"].with_user(c.receiver).create(
            {"receipt_id": receipt.id, "po_line_id": other.line_ids.id, "qty_received": 1}
        )


def test_a1_receipt_line_acceptance_cannot_be_typed(c):
    po = _sent_po(c)
    po.with_user(c.receiver).action_start_receipt()
    line = po.receipt_ids.line_ids[:1]
    with pytest.raises(UserError, match="changes only through its workflow"):
        line.with_user(c.receiver).write({"qty_accepted": 10})


# ------------------------------------------------- A4: display names
def test_a4_pickers_read_a_name_not_model_and_id(c):
    req = _req(c)
    assert req.display_name == "A06F16 requisition"
    po = _sent_po(c)
    po.with_user(c.receiver).action_start_receipt()
    rline = po.receipt_ids.line_ids[:1]
    for name in (rline.display_name, rline.po_line_id.display_name):
        assert "," not in name.split("·")[0] and rline.product_id.name in name
    assert po.receipt_ids.name in rline.display_name
    Line = c.env["fix.purchase.receipt.line"]
    found = [i for i, _label in Line.name_search(name=po.receipt_ids.name, limit=10)]
    assert set(po.receipt_ids.line_ids.ids) <= set(found)


# ------------------------------------------------- A7: receiving tolerance
def test_a7_over_receipt_is_refused_by_default(c):
    po = _sent_po(c, [(c.prod, 10)])
    with pytest.raises(UserError, match="outside"):
        po.with_user(c.receiver).action_record_receipt({po.line_ids.id: 10.5})
    assert po.line_ids.qty_received == 0


def test_a7_tolerance_allows_up_to_the_configured_percentage_and_no_more(c):
    c.env["ir.config_parameter"].sudo().set_param(PARAM_TOL, "10")
    po = _sent_po(c, [(c.prod, 10)])
    with pytest.raises(UserError, match="outside"):
        po.with_user(c.receiver).action_record_receipt({po.line_ids.id: 11.5})
    po.with_user(c.receiver).action_record_receipt({po.line_ids.id: 11})
    assert po.line_ids.qty_received == 11 and po.state == "received"


def test_a7_a_bad_tolerance_value_falls_back_to_no_tolerance(c):
    c.env["ir.config_parameter"].sudo().set_param(PARAM_TOL, "plenty")
    po = _sent_po(c, [(c.prod, 10)])
    with pytest.raises(UserError, match="outside"):
        po.with_user(c.receiver).action_record_receipt({po.line_ids.id: 10.5})


# ------------------------------------------------- B6: the vendor's date
def test_b6_acknowledgement_needs_the_confirmed_date(c):
    po = _sent_po(c)
    with pytest.raises(UserError, match="delivery date"):
        po.with_user(c.buyer).action_acknowledge_on_behalf(evidence="vendor e-mail ref 991")
    assert po.state == "sent" and not po.vendor_confirmed_date


def test_b6_the_buyers_promised_date_is_no_longer_taken_for_the_vendors(c):
    po = (
        c.env["fix.purchase.order"]
        .with_user(c.buyer)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.vendor.id,
                "promised_date": SOON,
                "line_ids": [(0, 0, {"product_id": c.prod.id, "qty_ordered": 1, "unit_price": 9})],
            }
        )
    )
    po.sudo().action_record_requisition_exception(reason="A06F16 test PO with no requisition")
    po.with_user(c.buyer).action_submit_for_approval(justification="A06F16 stock-out")
    _decide(c, po, c.t2)
    po.with_user(c.buyer).action_send()
    with pytest.raises(UserError, match="delivery date"):
        po.with_user(c.buyer).action_acknowledge_on_behalf(evidence="vendor e-mail ref 991")
    later = SOON + timedelta(days=5)
    po.with_user(c.buyer).action_acknowledge_on_behalf(
        evidence="vendor e-mail ref 991", confirmed_date=str(later)
    )
    assert po.vendor_confirmed_date == later and po.promised_date == SOON


def test_b6_a_date_that_is_not_one_or_is_before_sending_is_refused(c):
    po = _sent_po(c)
    with pytest.raises(UserError, match="not a date"):
        po.with_user(c.buyer).action_acknowledge_on_behalf(
            evidence="vendor e-mail ref 991", confirmed_date="next week"
        )
    with pytest.raises(UserError, match="before PO"):
        po.with_user(c.buyer).action_acknowledge_on_behalf(
            evidence="vendor e-mail ref 991", confirmed_date="2020-01-01"
        )
    assert po.state == "sent"


# ------------------------------------------------- B11: cost centre, required-by
def test_b11_submit_needs_cost_centre_and_required_by(c):
    req = _req(c, cost_centre=False, required_by=False)
    with pytest.raises(UserError, match="cost centre and the required-by"):
        req.with_user(c.requester).action_submit()
    req.with_user(c.requester).write({"cost_centre": "CC-SVC-01"})
    with pytest.raises(UserError, match="required-by"):
        req.with_user(c.requester).action_submit()
    assert req.state == "draft"
    req.with_user(c.requester).write({"required_by": SOON})
    req.with_user(c.requester).action_submit()
    assert req.state == "submitted" and req.approval_state == "pending"


def test_b11_an_old_draft_with_neither_is_still_readable_and_editable(c):
    """No stored row breaks: the rule is at submission, not on the record."""
    req = _req(c, cost_centre=False, required_by=False)
    req.with_user(c.requester).write({"description": "A06F16 reworded"})
    assert req.description == "A06F16 reworded"


# ------------------------------------------------- B12: the emergency path
def _release(c, amount=20000.0, **kw):
    req = _req(c, amount, urgency="emergency", **kw)
    req.with_user(c.requester).action_emergency_release(reason="Job 4471 stopped, no compressor")
    return req


def test_b12_emergency_goes_ahead_and_approval_stays_owed(c):
    req = _release(c)
    assert (req.state, req.emergency_state, req.approval_state) == (
        "submitted",
        "pending",
        "pending",
    )
    assert req.emergency_deadline > fields.Datetime.now()
    assert c.t2 in req.approval_request_id.task_ids.mapped("assigned_user_id")
    req.with_user(c.buyer).action_convert_to_po()
    po = req.purchase_order_id
    assert req.state == "converted"
    po.with_user(c.buyer).action_send()  # no PO approval: the release covers it
    assert po.state == "sent"
    _decide(c, req, c.t2)
    assert req.emergency_state == "approved" and req.state == "converted"
    assert req.dofa_approved_by == c.t2


def test_b12_a_normal_requisition_cannot_convert_before_approval(c):
    req = _req(c)
    req.with_user(c.requester).action_submit()
    with pytest.raises(UserError, match="Convert an approved"):
        req.with_user(c.buyer).action_convert_to_po()


def test_b12_release_is_refused_outside_its_bounds(c):
    normal = _req(c)
    with pytest.raises(UserError, match="not marked Emergency"):
        normal.with_user(c.requester).action_emergency_release(reason="Job 4471 stopped today")
    urgent = _req(c, urgency="emergency")
    with pytest.raises(UserError, match="what job stopped"):
        urgent.with_user(c.requester).action_emergency_release(reason="asap")
    big = _req(c, 50001.0, urgency="emergency")
    with pytest.raises(UserError, match="limited to"):
        big.with_user(c.requester).action_emergency_release(reason="Job 4471 stopped today")
    c.env["ir.config_parameter"].sudo().set_param(PARAM_MAX, "1000")
    with pytest.raises(UserError, match="limited to"):
        urgent.with_user(c.requester).action_emergency_release(reason="Job 4471 stopped today")
    assert urgent.state == "draft" and not urgent.emergency_state


def test_b12_no_named_approver_means_no_release(c):
    for tier in (2, 3, 4, 5):
        c.env.ref(T[tier]).sudo().write({"user_ids": [(5, 0, 0)]})
    req = _req(c, urgency="emergency")
    with pytest.raises(UserError, match="No one can approve"), c.env.cr.savepoint():
        req.with_user(c.requester).action_emergency_release(reason="Job 4471 stopped today")
    req.invalidate_recordset()
    assert req.state == "draft" and not req.emergency_state


def test_b12_the_po_cannot_outgrow_the_release(c):
    req = _release(c)
    req.with_user(c.buyer).action_convert_to_po()
    po = req.purchase_order_id
    po.line_ids.with_user(c.buyer).write({"unit_price": po.line_ids.unit_price * 2})
    with pytest.raises(UserError, match="not been approved"):
        po.with_user(c.buyer).action_send()


def test_b12_a_released_requisition_cannot_be_repriced(c):
    req = _release(c)
    with pytest.raises(UserError, match="can no longer change"):
        req.with_user(c.requester).write({"estimate_amount": 49000})


def test_b12_emergency_fields_cannot_be_typed(c):
    req = _req(c, urgency="emergency")
    with pytest.raises(UserError, match="changes only through its workflow"):
        req.with_user(c.requester).write({"emergency_state": "approved"})


def test_b12_overdue_escalates_and_blocks_the_requester_until_the_cfo_closes_it(c):
    req = _release(c)
    Model = c.env["fix.requisition"]
    assert req not in Model._cron_emergency_posthoc()  # in time: nothing happens
    req.sudo()._guarded().write({"emergency_deadline": fields.Datetime.now() - timedelta(hours=1)})
    assert req in Model._cron_emergency_posthoc()
    assert req.emergency_state == "overdue" and req.emergency_escalated_at
    todo = req.sudo().activity_ids.filtered(lambda a: a.user_id == c.cfo)
    assert todo and req.display_name in todo[0].summary
    assert req not in Model._cron_emergency_posthoc()  # once
    with pytest.raises(UserError, match="Convert an approved"):
        req.with_user(c.buyer).action_convert_to_po()  # the window closed
    second = _req(c, 1000.0, urgency="emergency", description="A06F16 second")
    with pytest.raises(UserError, match="BRU-PRO-12"):
        second.with_user(c.requester).action_emergency_release(reason="Job 4472 stopped too")
    with pytest.raises(UserError, match="CFO"):
        req.with_user(c.requester).action_emergency_close(reason="Dealt with by purchasing")
    req.with_user(c.cfo).action_emergency_close(reason="Reviewed with procurement, no loss")
    assert req.emergency_state == "closed"
    second.with_user(c.requester).action_emergency_release(reason="Job 4472 stopped too")
    assert second.emergency_state == "pending"


def test_b12_late_approval_lifts_the_block(c):
    req = _release(c)
    req.sudo()._guarded().write({"emergency_deadline": fields.Datetime.now() - timedelta(hours=1)})
    c.env["fix.requisition"]._cron_emergency_posthoc()
    _decide(c, req, c.t2)
    assert req.emergency_state == "approved"
    second = _req(c, 1000.0, urgency="emergency", description="A06F16 second")
    second.with_user(c.requester).action_emergency_release(reason="Job 4472 stopped too")
    assert second.emergency_state == "pending"


def test_b12_post_hoc_rejection_blocks_too(c):
    req = _release(c)
    req.with_user(c.buyer).action_convert_to_po()
    task = req.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == c.t2)
    task.with_user(c.t2).action_reject(comment="No job 4471 on the board")
    assert req.emergency_state == "rejected" and req.state == "converted"
    second = _req(c, 1000.0, urgency="emergency", description="A06F16 second")
    with pytest.raises(UserError, match="BRU-PRO-12"):
        second.with_user(c.requester).action_emergency_release(reason="Job 4472 stopped too")


def test_b12_a_blocked_person_cannot_name_a_colleague_as_requester(c):
    req = _release(c)
    req.sudo()._guarded().write({"emergency_deadline": fields.Datetime.now() - timedelta(hours=1)})
    c.env["fix.requisition"]._cron_emergency_posthoc()
    colleague = c.env["hr.employee"].create({"name": "A06F16 Colleague"})
    other = _req(c, 1000.0, urgency="emergency", requested_by=colleague.id, product_id=c.prod2.id)
    with pytest.raises(UserError, match="BRU-PRO-12"):
        other.with_user(c.requester).action_emergency_release(reason="Job 4473 stopped as well")
    assert other.state == "draft" and not other.emergency_state


def test_b12_releases_cannot_be_split_under_the_ceiling(c):
    _release(c, 30000.0)
    second = _req(c, 30000.0, urgency="emergency", description="A06F16 second")
    with pytest.raises(UserError, match="related requisitions"):
        second.with_user(c.requester).action_emergency_release(reason="Job 4471 stopped still")
    assert second.state == "draft" and not second.emergency_state
    # the same two under the ceiling together go ahead, and the approval sees the total
    third = _req(c, 15000.0, urgency="emergency", description="A06F16 third")
    third.with_user(c.requester).action_emergency_release(reason="Job 4471 stopped still")
    assert third.split_prior_amount == 30000.0
    assert third._dofa_amount() == 45000.0


def test_b12_the_requester_never_decides_the_post_hoc_approval(c):
    c.requester.write({"group_ids": [(4, c.env.ref(T[2]).id)]})
    req = _release(c)
    assert c.requester not in req.approval_request_id.task_ids.mapped("assigned_user_id")
