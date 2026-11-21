# A06 final pass, M16 screens. Procure-to-pay used to stop at goods receipt: the
# receipt that feeds the PO lines had no screen and an empty write whitelist, so
# inspection had no line to pick, every PO bill stayed blocked, and the PO never
# closed. test_walk_* runs the whole path through /p03/model/write and
# /p03/model/action as distinct role users, with only the inputs and buttons the
# fragments offer. Also here: sealed bids on the workspace (M16-5), the pickers, the
# GR/IR report, and the sweep that every button collects what its method needs.
import ast
import base64
import inspect
import itertools
import re
from datetime import timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a06, form_fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

GB = "cd_requisition.group_fix_procurement_buyer"
GR = "cd_requisition.group_fix_procurement_receiver"
GS = "cd_vendor_portal.group_fix_supplier_steward"
GSA = "cd_vendor_portal.group_fix_supplier_approver"
T2 = "cd_entity_config.group_dofa_tier_2"
AP = "account.group_account_user"
A06_JS = Path(a06.__file__).resolve().parents[2] / "static" / "src" / "a06"
_SEQ = itertools.count(1)
PDF = base64.b64encode(b"%PDF-1.4 a06 walk document").decode()


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def p03(odoo_env):
    """Call a route as a user, the way the workspace does."""
    active = []

    def call(user, route, **kw):
        patcher = mock.patch.object(api, "request", FakeRequest(odoo_env(user=user.id)))
        patcher.start()
        active.append(patcher)
        try:
            return getattr(api.P03GenericApiController(), route)(**kw)
        finally:
            patcher.stop()
            active.remove(patcher)

    yield call


def _user(env, tag, *groups):
    n = next(_SEQ)
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A06 Final %s %d" % (tag, n),
                "login": "a06.final.m16.%s.%d@a06.test" % (tag, n),
                "group_ids": [(6, 0, ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def write_ok(p03, user, model, values, record_id=False, lines=None):
    out = p03(user, "model_write", model=model, record_id=record_id, values=values, lines=lines)
    assert "error" not in out, out
    return out["id"]


def press(p03, user, model, rec_id, method, **kwargs):
    out = p03(user, "model_action", model=model, ids=[rec_id], method=method, kwargs=kwargs)
    assert out["success"], "%s.%s as %s: %s" % (model, method, user.login, out.get("error"))
    return out["result"]


def refused(p03, user, model, rec_id, method, match, **kwargs):
    out = p03(user, "model_action", model=model, ids=[rec_id], method=method, kwargs=kwargs)
    assert not out["success"], "%s.%s was allowed for %s" % (model, method, user.login)
    assert re.search(match, out["error"]), out["error"]


def inbox(env, p03, user, record):
    """The M63 inbox screen's domain, as the approver: is_mine and pending."""
    rows = p03(
        user,
        "model_records",
        model="fix.workflow.task",
        cols=["name", "res_model", "res_id", "state"],
        domain=[["is_mine", "=", True], ["state", "=", "pending"]],
    )
    assert "error" not in rows, rows
    mine = [
        r["id"] for r in rows["rows"] if r["res_model"] == record._name and r["res_id"] == record.id
    ]
    assert mine, "nothing for %s in the inbox of %s" % (record.display_name, user.login)
    return mine[0]


def form_choices(p03, user, model, field, domain=None, record_id=False):
    out = p03(
        user,
        "model_form",
        model=model,
        fields=[{"name": field, "domain": domain or []}],
        record_id=record_id,
    )
    assert "error" not in out, out
    return {c["id"]: c["label"] for c in out["fields"][0]["choices"]}


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    w = type("World", (), {})()
    w.env = env
    w.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    w.requester = _user(env, "requester")
    w.emp = env["hr.employee"].create({"name": "A06 Final Requester", "user_id": w.requester.id})
    w.buyer = _user(env, "buyer", GB)
    w.approver = _user(env, "t2", T2)
    w.receiver = _user(env, "receiver", GR)
    # A06 ERP audit P21: whoever received goods does not record their inspection
    w.inspector = _user(env, "inspector", GR)
    w.ap = _user(env, "ap", AP)
    w.steward = _user(env, "steward", GS)
    w.steward2 = _user(env, "steward2", GS)
    w.supplier_approver = _user(env, "supapprover", GSA)
    w.plain = _user(env, "plain")
    # A06 ERP audit P08: a purchased product has a category the supplier is
    # qualified for (the PO category gate)
    categ = env["product.category"].create({"name": "A06 Final Compressors"})
    w.product = env["product.product"].create(
        {"name": "A06 Final Compressor", "categ_id": categ.id}
    )
    w.vendor = env["res.partner"].create({"name": "A06 Final Vendor", "is_company": True})
    return w


def onboard(w, p03, partner):
    """M42, through its screens: documents, screening, qualification, activation."""
    steward, second, approver = w.steward, w.steward2, w.supplier_approver
    sid = write_ok(
        p03,
        steward,
        "fix.supplier",
        {"name": partner.name, "partner_id": partner.id, "segment": "transactional"},
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        doc = write_ok(
            p03,
            steward,
            "fix.supplier.document",
            {
                "supplier_id": sid,
                "doc_type": doc_type,
                "number": "%s-%d" % (doc_type, sid),
                "file": PDF,
                "file_filename": "%s.pdf" % doc_type,
                "valid_to": str(fields.Date.today() + timedelta(days=365)),
            },
        )
        press(p03, second, "fix.supplier.document", doc, "action_verify")
    for key in ("sanctions", "coi", "abac"):
        rec = write_ok(
            p03,
            steward,
            "fix.supplier.screening",
            {"supplier_id": sid, "screening_type": key, "result": "clear"},
        )
        # A06 ERP audit P20: whoever recorded a screening does not clear it
        press(p03, second, "fix.supplier.screening", rec, "action_clear")
    # A06 ERP audit P08: the categories a supplier may supply are approved on
    # its qualification (the PO category gate is on)
    qual = write_ok(
        p03,
        steward,
        "fix.supplier.qualification",
        {
            "supplier_id": sid,
            "score": 82,
            "category_ids": [(6, 0, [w.product.categ_id.id])],
        },
    )
    press(p03, steward, "fix.supplier.qualification", qual, "action_start")
    press(p03, approver, "fix.supplier.qualification", qual, "action_approve")
    gate = write_ok(
        p03, steward, "fix.supplier.activation", {"supplier_id": sid, "qualification_id": qual}
    )
    press(p03, approver, "fix.supplier.activation", gate, "action_activate")
    supplier = w.env["fix.supplier"].browse(sid)
    assert supplier.status == "active"
    return supplier


def raise_and_send_po(w, p03, qty=10, price=2000.0):
    """Requisition -> M63 inbox -> PO -> M63 inbox -> send. Returns the PO."""
    env = w.env
    req_id = write_ok(
        p03,
        w.requester,
        "fix.requisition",
        {
            "description": "A06 final walk compressors",
            "justification": "Stock-out on compressors for AMC visits",
            "product_id": w.product.id,
            "qty": qty,
            "vendor_id": w.vendor.id,
            "estimate_amount": qty * price,
            "cost_centre": "CC-SVC-01",
            "required_by": str(fields.Date.today() + timedelta(days=20)),
            "urgency": "normal",
            "requested_by": w.emp.id,
            "operating_unit_id": w.ou.id,
        },
    )
    req = env["fix.requisition"].browse(req_id)
    press(p03, w.requester, "fix.requisition", req_id, "action_submit")
    assert (req.state, req.approval_state) == ("submitted", "pending")
    refused(p03, w.buyer, "fix.requisition", req_id, "action_convert_to_po", "approved")
    task = inbox(env, p03, w.approver, req)
    press(p03, w.approver, "fix.workflow.task", task, "action_approve")
    assert req.state == "approved"
    press(p03, w.buyer, "fix.requisition", req_id, "action_convert_to_po")
    po = req.purchase_order_id
    assert po.state == "draft" and po.requisition_id == req
    refused(p03, w.buyer, "fix.purchase.order", po.id, "action_send", "not been approved")
    press(
        p03,
        w.buyer,
        "fix.purchase.order",
        po.id,
        "action_submit_for_approval",
        justification="Stock-out on compressors",
    )
    task = inbox(env, p03, w.approver, po)
    press(p03, w.approver, "fix.workflow.task", task, "action_approve")
    press(p03, w.buyer, "fix.purchase.order", po.id, "action_send")
    assert po.state == "sent"
    return po


def bill_values(w, po, ref):
    return {
        "invoice_ref": ref,
        "vendor_id": po.vendor_id.id,
        "bill_type": "po",
        "requisition_id": po.id,
        "invoice_date": str(fields.Date.today()),
        "payment_channel": "bank",
        "operating_unit_id": w.ou.id,
    }


def bill_lines(w, qty, price):
    row = {
        "product_id": w.product.id,
        "description": "Compressor",
        "quantity": qty,
        "unit_price": price,
        "tds_category": "supply_of_goods",
    }
    return {"field": "line_ids", "rows": [{"values": row}], "removed": []}


# ---------------------------------------------------------------- A1: the walk
def test_the_m63_inbox_lists_the_approvers_tasks_and_nobody_elses(world, p03):
    """The inbox domain was inverted (Odoo 19 hands a boolean search `in {True}`):
    an approver saw every task but their own, so the walk stopped at step two."""
    w = world
    second = _user(w.env, "t2b", T2)
    onboard(w, p03, w.vendor)
    req = (
        w.env["fix.requisition"]
        .with_user(w.requester)
        .create(
            {
                "description": "A06 final inbox requisition",
                "estimate_amount": 1000,
                "cost_centre": "CC-SVC-01",
                "required_by": str(fields.Date.today()),
                "requested_by": w.emp.id,
                "operating_unit_id": w.ou.id,
            }
        )
    )
    press(p03, w.requester, "fix.requisition", req.id, "action_submit")
    tasks = req.approval_request_id.task_ids
    assert {w.approver, second} <= set(tasks.mapped("assigned_user_id"))
    Task = w.env["fix.workflow.task"]
    for holder in (w.approver, second):
        mine = tasks.filtered(lambda t, u=holder: t.assigned_user_id == u)
        assert inbox(w.env, p03, holder, req) == mine.id
        as_holder = Task.with_user(holder)
        assert mine in as_holder.search([("is_mine", "=", True)])
        assert mine not in as_holder.search([("is_mine", "=", False)])
        assert mine not in as_holder.search([("is_mine", "!=", True)])
        assert (tasks - mine) <= as_holder.search([("is_mine", "=", False)])
    rows = p03(
        w.plain,
        "model_records",
        model="fix.workflow.task",
        cols=["res_model", "res_id"],
        domain=[["is_mine", "=", True], ["state", "=", "pending"]],
    )
    assert not [r for r in rows.get("rows", []) if r["res_id"] == req.id]


def test_walk_requisition_to_closed_po_through_the_screens_only(world, p03):
    w, env = world, world.env
    onboard(w, p03, w.vendor)
    po = raise_and_send_po(w, p03)

    # acknowledge: the button's two prompts
    refused(
        p03,
        w.buyer,
        "fix.purchase.order",
        po.id,
        "action_acknowledge_on_behalf",
        "delivery date",
        evidence="Vendor e-mail 2026-11-07 ref 88",
    )
    promised = fields.Date.today() + timedelta(days=15)
    press(
        p03,
        w.buyer,
        "fix.purchase.order",
        po.id,
        "action_acknowledge_on_behalf",
        evidence="Vendor e-mail 2026-11-07 ref 88",
        confirmed_date=str(promised),
    )
    assert po.state == "acknowledged" and po.vendor_confirmed_date == promised

    # the receiver starts the receipt from the PO; the buyer cannot
    refused(p03, w.buyer, "fix.purchase.order", po.id, "action_start_receipt", "Receiver")
    result = press(p03, w.receiver, "fix.purchase.order", po.id, "action_start_receipt")
    receipt = po.receipt_ids
    assert receipt.name in result["note"] and receipt.state == "draft"
    assert receipt.name in po.receipt_refs

    # the form shows the PO's open lines; a short delivery of 6 is keyed in the grid
    form = p03(
        w.receiver,
        "model_form",
        model="fix.purchase.receipt",
        fields=[{"name": "purchase_order_id"}, {"name": "delivery_note_ref"}],
        record_id=receipt.id,
        lines={
            "field": "line_ids",
            "fields": [
                {"name": "po_line_id", "readonly": True},
                {"name": "qty_received", "required": True},
                {"name": "inspection_state", "readonly": True},
                {"name": "qty_accepted", "readonly": True},
            ],
        },
    )
    assert "error" not in form, form
    rows = form["lines"]["rows"]
    assert [r["po_line_id"]["id"] for r in rows] == po.line_ids.ids
    assert "A06 Final Compressor" in rows[0]["po_line_id"]["label"]
    # the save posts every column the grid shows, the read-only ones included
    keyed = {k: v for k, v in rows[0].items() if k != "id"}
    keyed["qty_received"] = 6
    write_ok(
        p03,
        w.receiver,
        "fix.purchase.receipt",
        {
            "purchase_order_id": {"id": po.id, "label": po.name},
            "delivery_note_ref": "CHALLAN-771",
            "vendor_id": {"id": po.vendor_id.id, "label": po.vendor_id.name},
        },
        record_id=receipt.id,
        lines={
            "field": "line_ids",
            "rows": [{"id": rows[0]["id"], "values": keyed}],
            "removed": [],
        },
    )
    press(p03, w.receiver, "fix.purchase.receipt", receipt.id, "action_post")
    assert po.state == "partially_received" and po.line_ids.qty_received == 6
    refused(p03, w.buyer, "fix.purchase.order", po.id, "action_close", "Manager", reason="short")

    # a bill before inspection is blocked: nothing is accepted yet
    bill_id = write_ok(
        p03,
        w.ap,
        "fix.vendor.invoice",
        bill_values(w, po, "A06F-WALK-1"),
        lines=bill_lines(w, 6, 2000.0),
    )
    bill = env["fix.vendor.invoice"].browse(bill_id)
    assert bill.match_state == "blocked" and "awaiting inspection" in bill.match_detail
    refused(p03, w.ap, "fix.vendor.invoice", bill_id, "action_request_payment", "G3-06")

    # inspection picks the line from a picker that offers it by name
    domain = [["state", "=", "posted"], ["inspection_state", "=", "pending"]]
    choices = form_choices(
        p03, w.inspector, "fix.procurement.inspection", "receipt_line_id", domain
    )
    rline = receipt.line_ids
    assert receipt.name in choices[rline.id]
    insp = write_ok(
        p03,
        w.inspector,
        "fix.procurement.inspection",
        {"receipt_line_id": rline.id, "qty_accepted": 6},
    )
    press(p03, w.inspector, "fix.procurement.inspection", insp, "action_confirm")
    assert rline.inspection_state == "passed"
    assert not form_choices(
        p03, w.inspector, "fix.procurement.inspection", "receipt_line_id", domain
    ).get(rline.id)

    # the bill now matches, on nothing but the receipt it was blocked for
    bill.invalidate_recordset()
    assert bill.match_state == "matched", bill.match_detail

    # the rest arrives, is inspected and billed; the PO closes
    second = write_ok(p03, w.receiver, "fix.purchase.receipt", {"purchase_order_id": po.id})
    second_receipt = env["fix.purchase.receipt"].browse(second)
    assert second_receipt.line_ids.qty_received == 4  # only what is still due
    press(p03, w.receiver, "fix.purchase.receipt", second, "action_post")
    assert po.state == "received" and po.received_on
    insp = write_ok(
        p03,
        w.inspector,
        "fix.procurement.inspection",
        {"receipt_line_id": second_receipt.line_ids.id, "qty_accepted": 4},
    )
    press(p03, w.inspector, "fix.procurement.inspection", insp, "action_confirm")
    rest = write_ok(
        p03,
        w.ap,
        "fix.vendor.invoice",
        bill_values(w, po, "A06F-WALK-2"),
        lines=bill_lines(w, 4, 2000.0),
    )
    assert env["fix.vendor.invoice"].browse(rest).match_state == "matched"
    press(p03, w.buyer, "fix.purchase.order", po.id, "action_close")
    assert po.state == "closed"

    # the bills post (their last approval; the matrix is covered by A08):
    # GR/IR counts posted bills only (A06 X26)
    _post_bill(w, "A06F-WALK-1")
    _post_bill(w, "A06F-WALK-2")
    # the three-way workbench and GR/IR agree there is nothing left open
    report = p03(w.buyer, "model_report", module="M16", report="three_way")
    row = next(r for r in report["rows"] if r["po"] == po.name)
    assert (row["ordered"], row["received"], row["accepted"], row["invoice_qty"]) == (
        10,
        10,
        10,
        10,
    )
    grir = p03(w.buyer, "model_report", module="M16", report="gr_ir")
    assert not [r for r in grir["rows"] if r["po"] == po.name]


def test_walk_rejection_keeps_the_bill_blocked(world, p03):
    w, env = world, world.env
    onboard(w, p03, w.vendor)
    po = raise_and_send_po(w, p03)
    press(p03, w.receiver, "fix.purchase.order", po.id, "action_start_receipt")
    press(p03, w.receiver, "fix.purchase.receipt", po.receipt_ids.id, "action_post")
    bill_id = write_ok(
        p03,
        w.ap,
        "fix.vendor.invoice",
        bill_values(w, po, "A06F-WALK-3"),
        lines=bill_lines(w, 10, 2000.0),
    )
    insp = write_ok(
        p03,
        w.inspector,
        "fix.procurement.inspection",
        {"receipt_line_id": po.receipt_ids.line_ids.id, "qty_accepted": 7},
    )
    press(p03, w.inspector, "fix.procurement.inspection", insp, "action_confirm")
    bill = env["fix.vendor.invoice"].browse(bill_id)
    bill.invalidate_recordset()
    assert bill.match_state == "blocked" and "rejected at inspection" in bill.match_detail


def test_walk_only_a_receiver_writes_a_receipt_and_never_its_state(world, p03):
    w = world
    onboard(w, p03, w.vendor)
    po = raise_and_send_po(w, p03)
    out = p03(
        w.buyer,
        "model_write",
        model="fix.purchase.receipt",
        record_id=False,
        values={"purchase_order_id": po.id},
    )
    assert "error" in out
    rid = write_ok(p03, w.receiver, "fix.purchase.receipt", {"purchase_order_id": po.id})
    out = p03(
        w.receiver,
        "model_write",
        model="fix.purchase.receipt",
        record_id=rid,
        values={"state": "posted"},
    )
    assert "error" in out
    assert w.env["fix.purchase.receipt"].browse(rid).state == "draft"
    refused(p03, w.buyer, "fix.purchase.receipt", rid, "action_post", "Receiver")


def test_walk_a_posted_receipt_is_final_on_the_screen(world, p03):
    w = world
    onboard(w, p03, w.vendor)
    po = raise_and_send_po(w, p03)
    rid = write_ok(p03, w.receiver, "fix.purchase.receipt", {"purchase_order_id": po.id})
    press(p03, w.receiver, "fix.purchase.receipt", rid, "action_post")
    line = po.receipt_ids.line_ids
    out = p03(
        w.receiver,
        "model_write",
        model="fix.purchase.receipt",
        record_id=rid,
        values={},
        lines={"field": "line_ids", "rows": [{"id": line.id, "values": {"qty_received": 1}}]},
    )
    assert "error" in out
    assert line.qty_received == 10
    refused(p03, w.receiver, "fix.purchase.receipt", rid, "action_cancel", "draft")


# ---------------------------------------------------------------- A3: sealed bids
@pytest.fixture
def rfq(world):
    w = world
    w.buyer2 = _user(w.env, "buyer2", GB)
    sup_partner = w.env["res.partner"].create({"name": "A06 Final Bidder", "is_company": True})
    rec = (
        w.env["fix.procurement.rfq"]
        .with_user(w.buyer)
        .create(
            {
                "description": "A06 final RFQ",
                "product_id": w.product.id,
                "qty": 5,
                "invited_vendor_ids": [(6, 0, sup_partner.ids)],
                "response_deadline": "2099-01-01",
            }
        )
    )
    rec.with_user(w.buyer).action_open()
    bid = (
        w.env["fix.procurement.bid"]
        .with_user(w.buyer)
        .create({"rfq_id": rec.id, "vendor_id": sup_partner.id, "unit_price": 777.0})
    )
    return rec, bid


def _bids(p03, user, rec):
    out = p03(
        user,
        "model_records",
        model="fix.procurement.bid",
        cols=["rfq_id", "vendor_id", "unit_price", "state"],
        domain=[["rfq_id", "=", rec.id]],
    )
    assert "error" not in out, out
    return out["rows"]


def _bid_form(p03, user, bid):
    return p03(
        user,
        "model_form",
        model="fix.procurement.bid",
        fields=[{"name": "vendor_id"}, {"name": "unit_price"}],
        record_id=bid.id,
    )


def test_a3_an_open_rfqs_bids_are_hidden_from_a_plain_user_and_another_buyer(world, rfq, p03):
    rec, bid = rfq
    for user in (world.plain, world.buyer2):
        assert _bids(p03, user, rec) == []
        form = _bid_form(p03, user, bid)
        assert "error" in form and not form.get("record")


def test_a3_the_buyer_who_recorded_a_bid_sees_only_that_bid_while_open(world, rfq, p03):
    rec, bid = rfq
    assert [r["id"] for r in _bids(p03, world.buyer, rec)] == [bid.id]
    other = world.env["res.partner"].create({"name": "A06 Final Bidder 2", "is_company": True})
    rec.write({"invited_vendor_ids": [(4, other.id)]})  # FR-PRO-011: only invitees bid
    theirs = (
        world.env["fix.procurement.bid"]
        .with_user(world.buyer2)
        .create({"rfq_id": rec.id, "vendor_id": other.id, "unit_price": 700.0})
    )
    assert [r["id"] for r in _bids(p03, world.buyer, rec)] == [bid.id]
    assert [r["id"] for r in _bids(p03, world.buyer2, rec)] == [theirs.id]
    assert "error" in _bid_form(p03, world.buyer, theirs)


def test_a3_after_close_the_comparison_is_open_to_all(world, rfq, p03):
    rec, bid = rfq
    rec.with_user(world.buyer).action_close()
    for user in (world.plain, world.buyer, world.buyer2):
        rows = _bids(p03, user, rec)
        assert [r["id"] for r in rows] == [bid.id] and rows[0]["unit_price"] == 777.0
        assert _bid_form(p03, user, bid)["record"]["unit_price"] == 777.0


def test_a3_pickers_and_reports_show_no_price_or_vendor_while_open(world, rfq, p03):
    rec, bid = rfq
    choices = form_choices(p03, world.plain, "fix.procurement.award", "bid_id")
    assert "777" not in str(choices.get(bid.id, "")) and "Bidder" not in str(
        choices.get(bid.id, "")
    )
    for report in a06.m16.REPORTS:
        out = p03(world.plain, "model_report", module="M16", report=report)
        text = str(out)
        assert "777" not in text and "A06 Final Bidder" not in text, report
    assert "bid" not in str(p03(world.plain, "model_report", module="M16", report="three_way"))


# ---------------------------------------------------------------- A4/A5: pickers
def _offered(p03, user, model, field, domain, q):
    """Ids the picker offers for `q`: the inline list when the domain is small,
    the server search the picker switches to above PICKER_LIMIT (a database
    holding the real supplier register is always above it)."""
    inline = form_choices(p03, user, model, field, domain)
    if inline:
        return set(inline)
    out = p03(user, "model_choices", model=model, field=field, q=q, domain=domain)
    return {c["id"] for c in out["choices"]}


def test_a5_vendor_pickers_offer_active_suppliers_only(world, p03):
    w = world
    active = onboard(w, p03, w.vendor)
    prospect = w.env["res.partner"].create({"name": "A06 Final Prospect", "is_company": True})
    w.env["fix.supplier"].create({"name": prospect.name, "partner_id": prospect.id})
    stranger = w.env["res.partner"].create({"name": "A06 Final Stranger", "is_company": True})
    domain = [["fix_supplier_status", "=", "active"]]
    offered = _offered(p03, w.buyer, "fix.purchase.order", "vendor_id", domain, "A06 Final")
    assert active.partner_id.id in offered
    assert prospect.id not in offered and stranger.id not in offered
    # the server search honours the same domain
    out = p03(
        w.buyer,
        "model_choices",
        model="fix.purchase.order",
        field="vendor_id",
        q="A06 Final",
        domain=domain,
    )
    assert [c["id"] for c in out["choices"]] == [active.partner_id.id]
    registered = [["fix_supplier_status", "!=", False]]
    offered = _offered(p03, w.buyer, "fix.procurement.bid", "vendor_id", registered, "A06 Final")
    assert prospect.id in offered and stranger.id not in offered


def test_a4_the_requisition_picker_reads_a_name(world, p03):
    w = world
    req = (
        w.env["fix.requisition"]
        .with_user(w.requester)
        .create(
            {
                "description": "A06 final named requisition",
                "requested_by": w.emp.id,
                "operating_unit_id": w.ou.id,
            }
        )
    )
    choices = form_choices(p03, w.buyer, "fix.procurement.rfq", "requisition_id")
    assert choices[req.id] == "A06 final named requisition"


# ---------------------------------------------------------------- A7: GR/IR
def _post_bill(w, ref):
    """The bill's last approval posts it (the approval matrix is covered by
    the A08 suites): GR/IR counts posted bills only."""
    bill = w.env["fix.vendor.invoice"].search([("invoice_ref", "=", ref)])
    bill.sudo()._guarded().write({"approval_state": "approved"})
    bill.sudo()._post_approved_bill()
    return bill


def _grir(p03, user, po):
    report = p03(user, "model_report", module="M16", report="gr_ir")
    assert "error" not in report, report
    return [r for r in report["rows"] if r["po"] == po.name]


def test_a7_grir_lists_both_directions_by_po_from_posted_receipts_and_bills(world, p03):
    w = world
    onboard(w, p03, w.vendor)
    po = raise_and_send_po(w, p03, qty=10, price=2000.0)
    assert not _grir(p03, w.buyer, po)  # nothing received, nothing billed

    # a draft receipt counts for nothing
    rid = write_ok(p03, w.receiver, "fix.purchase.receipt", {"purchase_order_id": po.id})
    assert not _grir(p03, w.buyer, po)

    # received, not invoiced (held for inspection, still owed)
    press(p03, w.receiver, "fix.purchase.receipt", rid, "action_post")
    row = _grir(p03, w.buyer, po)[0]
    assert (row["received_not_invoiced"], row["invoiced_not_received"]) == (20000.0, 0.0)

    # rejected goods are not owed a bill: 4 of 10 accepted
    insp = write_ok(
        p03,
        w.inspector,
        "fix.procurement.inspection",
        {"receipt_line_id": po.receipt_ids.line_ids.id, "qty_accepted": 4},
    )
    press(p03, w.inspector, "fix.procurement.inspection", insp, "action_confirm")
    row = _grir(p03, w.buyer, po)[0]
    assert (row["received_value"], row["received_not_invoiced"]) == (8000.0, 8000.0)

    # a draft bill has cleared nothing (A06 X26: the posted basis that ties to
    # the GRNI account); once posted, 4 accepted and 4 billed leave nothing
    write_ok(
        p03,
        w.ap,
        "fix.vendor.invoice",
        bill_values(w, po, "A06F-GRIR-1"),
        lines=bill_lines(w, 4, 2000.0),
    )
    row = _grir(p03, w.buyer, po)[0]
    assert (row["received_not_invoiced"], row["invoiced_value"]) == (8000.0, 0.0)
    _post_bill(w, "A06F-GRIR-1")
    assert not _grir(p03, w.buyer, po)


def test_a7_grir_a_bill_for_goods_not_received_never_posts_as_invoiced(world, p03):
    """A06 X26 / three-way match: a bill for goods not yet received is
    blocked, cannot post, and so is not 'invoiced' on the GR/IR basis; after
    the goods arrive and the bill posts, nothing is open either way."""
    w = world
    onboard(w, p03, w.vendor)
    po = raise_and_send_po(w, p03, qty=2, price=1000.0)
    write_ok(
        p03,
        w.ap,
        "fix.vendor.invoice",
        bill_values(w, po, "A06F-GRIR-2"),
        lines=bill_lines(w, 2, 1000.0),
    )
    bill = w.env["fix.vendor.invoice"].search([("invoice_ref", "=", "A06F-GRIR-2")])
    assert bill.match_state != "matched"
    assert not _grir(p03, w.buyer, po)
    press(p03, w.receiver, "fix.purchase.order", po.id, "action_start_receipt")
    press(p03, w.receiver, "fix.purchase.receipt", po.receipt_ids.id, "action_post")
    row = _grir(p03, w.buyer, po)[0]
    assert (row["received_not_invoiced"], row["invoiced_not_received"]) == (2000.0, 0.0)


def test_b12_emergency_report_counts_a_release(world, p03):
    w = world
    onboard(w, p03, w.vendor)
    rid = write_ok(
        p03,
        w.requester,
        "fix.requisition",
        {
            "description": "A06 final emergency compressor",
            "product_id": w.product.id,
            "qty": 1,
            "vendor_id": w.vendor.id,
            "estimate_amount": 9000,
            "cost_centre": "CC-SVC-01",
            "required_by": str(fields.Date.today()),
            "urgency": "emergency",
            "requested_by": w.emp.id,
            "operating_unit_id": w.ou.id,
        },
    )
    press(
        p03,
        w.requester,
        "fix.requisition",
        rid,
        "action_emergency_release",
        reason="Job 4471 stopped, no compressor in the branch",
    )
    out = p03(w.buyer, "model_report", module="M16", report="emergency_spend")
    row = next(r for r in out["rows"] if r["requisition"] == "A06 final emergency compressor")
    assert row["amount"] == 9000.0 and "Awaiting" in row["path"]


# ---------------------------------------------------------------- A6: the sweep
def _screens(module):
    """{screen id: body} of a fragment's SCREENS, as form_fields reads them."""
    text = (A06_JS / ("%s.js" % module)).read_text(encoding="utf-8")
    text = text[text.index("export const SCREENS") : text.index("export const REPORT_ROUTES")]
    found = [(m.start(), m.group(1)) for m in form_fields.SCREEN.finditer(text)]
    return {
        sid: text[pos : found[i + 1][0] if i + 1 < len(found) else len(text)]
        for i, (pos, sid) in enumerate(found)
    }


def _buttons(body):
    block = re.search(r"\bactions:\s*\[(.*?)\n?\s*\]\s*(,\s*\n\s*note:.*)?\}", body, re.S)
    if not block:
        return []
    out = []
    for piece in re.split(r"(?=\{\s*m:\s*')", block.group(1)):
        method = re.match(r"\{\s*m:\s*'([a-z_0-9]+)'", piece)
        if method:
            out.append((method.group(1), set(re.findall(r"kwarg:\s*'([a-z_]+)'", piece))))
    return out


MUST_BE_ASKED = {"reason", "evidence", "confirmed_date", "note", "comment", "credit_ref"}


@pytest.mark.parametrize("module", ["m16", "m42"])
def test_a6_every_button_is_served_and_collects_what_its_method_needs(odoo_env, module):
    seen = 0
    for sid, body in _screens(module).items():
        if "kind: 'model_list'" not in body:
            continue
        model = form_fields.MODEL.search(body).group(1)
        for method, asked in _buttons(body):
            if method.startswith("__"):
                continue  # opens a form on the client ("Raise Call-Off PO"); no server method
            seen += 1
            assert method in api.SURFACES[model]["actions"], "%s: %s not served" % (sid, method)
            fn = getattr(odoo_env[model], method)
            params = inspect.signature(fn).parameters
            for name, param in params.items():
                required = param.default is inspect.Parameter.empty and param.kind in (
                    param.POSITIONAL_OR_KEYWORD,
                    param.KEYWORD_ONLY,
                )
                if required or name in MUST_BE_ASKED:
                    assert name in asked, "%s: %s needs %s, no prompt collects it" % (
                        sid,
                        method,
                        name,
                    )
            assert asked <= set(params), "%s: %s prompts for %s" % (sid, method, asked)
    assert seen > 15


@pytest.mark.parametrize("module", ["m16", "m42"])
def test_a6_list_columns_exist_and_status_labels_cover_every_value(odoo_env, module):
    for sid, body in _screens(module).items():
        match = form_fields.MODEL.search(body)
        if not match or match.group(1) not in odoo_env:
            continue
        model = odoo_env[match.group(1)]
        cols = re.search(r"\bcols:\s*\[([^\]]*)\]", body)
        if cols and "kind: 'model_list'" in body:
            for col in re.findall(r"'([a-z_0-9]+)'", cols.group(1)):
                assert col in model._fields, "%s: no column %s on %s" % (sid, col, model._name)
        status = re.search(r"status:\s*\{\s*field:\s*'(\w+)',\s*labels:\s*\{(.*?)\}", body, re.S)
        if status:
            labels = set(re.findall(r"(\w+):\s*['\"]", status.group(2)))
            values = {
                k for k, _v in model._fields[status.group(1)]._description_selection(odoo_env)
            }
            assert values <= labels, "%s: status misses %s" % (sid, values - labels)


def test_a1_the_screens_reach_the_right_documents():
    body = _screens("m16")
    assert form_fields.MODEL.search(body["M16-po-receipts"]).group(1) == "fix.purchase.receipt"
    assert form_fields.MODEL.search(body["M16-grn"]).group(1) == "fix.stock.receipt"
    text = (A06_JS / "m16.js").read_text(encoding="utf-8")
    grn = re.search(r"id: 'M16-grn', en: '([^']+)'", text).group(1)
    receipts = re.search(r"id: 'M16-po-receipts', en: '([^']+)', bn: '([^']+)'", text)
    assert grn != receipts.group(1) and "M15" in grn and receipts.group(2)
    assert api.SURFACES["fix.purchase.order"]["actions"] >= {"action_start_receipt"}
    assert "line_ids" in api.SURFACES["fix.purchase.receipt"]["writable"]
    assert api.SURFACES["fix.procurement.bid"].get("rules") is True


def _declared_picker_domains(module):
    """Every (comodel-owning model, field, domain) the fragment's forms declare."""
    out = []
    for sid, body in _screens(module).items():
        if "kind: 'model_form'" not in body:
            continue
        header, _lines = form_fields._cut_block(body, "lines")
        model = form_fields.MODEL.search(header).group(1)
        for match in re.finditer(r"name:\s*'(\w+)'[^\n]*?domain:\s*(\[\[.*?\]\])\s*\}", header):
            literal = match.group(2).replace("false", "False").replace("true", "True")
            out.append((sid, model, match.group(1), ast.literal_eval(literal)))
    return out


@pytest.mark.parametrize("module", ["m16", "m42"])
def test_a5_picker_domains_run_and_use_only_what_a_filter_may_test(odoo_env, module):
    """The engine runs a picker's filter under sudo, so it may only test workflow
    values (e248461d): selection, boolean or relation fields, none groups-restricted.
    A groups-restricted field here refused the whole form, not one picker."""
    declared = _declared_picker_domains(module)
    if module == "m16":
        assert len(declared) > 8
    allowed_types = {"selection", "boolean", "many2one", "many2many", "one2many"}
    for sid, model, field, domain in declared:
        comodel = odoo_env[model]._fields[field].comodel_name
        for path, operator, _value in domain:
            assert operator in ("=", "!=", "in", "not in"), (sid, field, operator)
            current = odoo_env[comodel]
            target = None
            for part in path.split("."):
                target = current._fields[part]
                assert not target.groups, (sid, field, part)
                if target.relational:
                    current = odoo_env[target.comodel_name]
            assert target.type in allowed_types, (sid, field, path, target.type)
        odoo_env[comodel].sudo().search_read(domain, ["display_name"], limit=1)


def test_a5_the_supplier_status_filter_reads_for_anyone_and_searches_both_ways(world, p03):
    w = world
    active = onboard(w, p03, w.vendor)
    Partner = w.env["res.partner"]
    prospect = Partner.create({"name": "A06 Final Status Prospect", "is_company": True})
    w.env["fix.supplier"].create({"name": prospect.name, "partner_id": prospect.id})
    none = Partner.create({"name": "A06 Final Status None", "is_company": True})
    assert active.partner_id.fix_supplier_status == "active"
    assert prospect.fix_supplier_status == "prospect" and not none.fix_supplier_status
    in_active = Partner.search([("fix_supplier_status", "=", "active")])
    registered = Partner.search([("fix_supplier_status", "!=", False)])
    assert active.partner_id in in_active and prospect not in in_active
    assert {active.partner_id, prospect} <= set(registered) and none not in registered
    # a portal vendor has no access to fix.supplier, and reading a partner must not fail
    group = w.env.ref("cd_vendor_portal.group_fix_vendor_portal")
    portal = (
        w.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A06 Final Portal",
                "login": "a06.final.portal@vendor.test",
                "partner_id": w.vendor.id,
                "group_ids": [(6, 0, [group.id])],
            }
        )
    )
    mine = w.vendor.with_user(portal)
    assert mine.read(["fix_supplier_status"])[0]["fix_supplier_status"] == "active"
    assert not w.env["fix.supplier"].with_user(portal).has_access("read")
