# cd_requisition live-ORM tests — M16 PO / receipt (three-way match inputs).
#
# A06 audit (2026-11-03): these tests sent unapproved POs to unregistered
# vendors, acknowledged them as staff, received goods on draft POs and approved
# requisitions as the IT administrator - each of which is now refused. They
# run as the system here, so the business gates (an approved requisition or a
# documented exception, an active supplier, a PO approval) are seeded the way
# the approval engine leaves them; the role and segregation checks are in
# test_a06_m16_controls.py.
import json
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.addons.cd_requisition.tests.p2p_fixtures import qualify_categories
from odoo.exceptions import UserError


def _events(env, event_type, aggregate, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", aggregate_id),
        ],
        order="id",
    )
    return [json.loads(row.payload) for row in rows]


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor = env["res.partner"].create({"name": "Gazi Spares Ltd."})
    supplier = env["fix.supplier"].create(
        {"name": vendor.name, "partner_id": vendor.id, "status": "active"}
    )
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].create(
            {"supplier_id": supplier.id, "doc_type": doc_type, "state": "valid"}
        )
    qualify_categories(env, supplier)  # A06 P08: categories approved by a qualification
    compressor, capacitor = env["product.product"].create(
        [{"name": "Compressor 1.5T"}, {"name": "Run Capacitor 35uF"}]
    )
    return SimpleNamespace(
        env=env, ou=ou, vendor=vendor, compressor=compressor, capacitor=capacitor
    )


def _po(ctx, lines=None, **vals):
    lines = (
        lines if lines is not None else [(ctx.compressor, 2.0, 500.0), (ctx.capacitor, 3.0, 120.0)]
    )
    return ctx.env["fix.purchase.order"].create(
        {
            "operating_unit_id": ctx.ou.id,
            "vendor_id": ctx.vendor.id,
            "line_ids": [
                (
                    0,
                    0,
                    {"product_id": p.id, "qty_ordered": q, "unit_price": u, "description": p.name},
                )
                for p, q, u in lines
            ],
            **vals,
        }
    )


def _approved(po):
    """The state the M63 engine leaves an approved PO in."""
    po.action_record_requisition_exception(reason="test PO without requisition")
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po.amount_total,
        }
    )
    return po


def _sent(ctx, **vals):
    po = _approved(_po(ctx, **vals))
    po.action_send()
    return po


# --- purchase order -------------------------------------------------------------


def test_po_numbering_and_totals(ctx):
    """Regression: without the fix.purchase.order sequence every PO of a day
    shared the reference 'PO/<today>'."""
    first, second = _po(ctx), _po(ctx, lines=[])
    prefix = f"PO/{date.today().year}/"
    assert first.name.startswith(prefix)
    assert second.name.startswith(prefix)
    assert first.name != second.name
    # 2 x 500 + 3 x 120 = 1360.00
    assert first.amount_total == 1360.0
    assert first.line_ids.mapped("line_total") == [1000.0, 360.0]
    assert second.amount_total == 0.0
    # A06 D5: the company's currency (BDT on the estate)
    assert (first.state, first.currency_id) == ("draft", ctx.env.company.currency_id)


def test_explicit_po_reference_is_kept(ctx):
    assert _po(ctx, name="PO/LEGACY/7").name == "PO/LEGACY/7"


def test_send_publishes_po_issued(ctx):
    po = _sent(ctx)
    assert po.state == "sent" and po.sent_at
    assert _events(ctx.env, "po.issued", "fix.purchase.order", po.id) == [
        {
            "po_ref": po.name,
            "vendor_id": ctx.vendor.id,
            "amount_total": 1360.0,
            "currency": ctx.env.company.currency_id.name,
            "fx_rate": 1.0,  # A06 P29: the rate the order went out at
        }
    ]
    assert po.line_ids.mapped("approved_unit_price") == [500.0, 120.0]


def test_unapproved_po_is_not_sent(ctx):
    po = _po(ctx)
    po.action_record_requisition_exception(reason="test PO without requisition")
    with pytest.raises(UserError, match="not been approved"), ctx.env.cr.savepoint():
        po.action_send()
    assert po.state == "draft"


def test_only_a_sent_po_is_acknowledged(ctx):
    with (
        pytest.raises(UserError, match="Only a sent PO can be acknowledged"),
        ctx.env.cr.savepoint(),
    ):
        _po(ctx).action_acknowledge_on_behalf(evidence="vendor e-mail 2026-03-02")


def test_staff_acknowledgement_is_on_behalf_with_evidence(ctx):
    po = _sent(ctx)
    with pytest.raises(UserError, match="P05 portal"), ctx.env.cr.savepoint():
        po.action_acknowledge()
    po.action_acknowledge_on_behalf(
        evidence="vendor e-mail 2026-03-02", confirmed_date=str(date.today() + timedelta(days=9))
    )
    assert (po.state, po.ack_channel, po.vendor_confirmed_date) == (
        "acknowledged",
        "buyer_on_behalf",
        date.today() + timedelta(days=9),
    )
    assert po.acknowledged_at
    assert _events(ctx.env, "po.acknowledged", "fix.purchase.order", po.id) == [
        {
            "po_ref": po.name,
            "vendor_id": ctx.vendor.id,
            "channel": "buyer_on_behalf",
            "confirmed_date": str(date.today() + timedelta(days=9)),
        }
    ]


def test_partial_then_full_receipt(ctx):
    po = _sent(ctx)
    compressor_line, capacitor_line = po.line_ids
    po.action_record_receipt({compressor_line.id: 1.0})
    assert po.state == "partially_received"
    assert (compressor_line.qty_received, capacitor_line.qty_received) == (1.0, 0.0)
    po.action_record_receipt({compressor_line.id: 1.0, capacitor_line.id: 3.0})
    assert po.state == "received" and po.received_on == fields.Date.context_today(po)
    assert len(po.receipt_ids) == 2 and set(po.receipt_ids.mapped("state")) == {"posted"}
    events = _events(ctx.env, "goods.received", "fix.purchase.order.line", compressor_line.id)
    assert [e["qty_received"] for e in events] == [1.0, 1.0]
    assert {e["vendor_id"] for e in events} == {ctx.vendor.id}
    assert {e["po_id"] for e in events} == {po.id}
    cap = _events(ctx.env, "goods.received", "fix.purchase.order.line", capacitor_line.id)
    assert [(e["product_id"], e["qty_received"]) for e in cap] == [(ctx.capacitor.id, 3.0)]


def test_receipt_of_nothing_is_refused(ctx):
    po = _sent(ctx)
    with pytest.raises(UserError, match="Nothing to receive"), ctx.env.cr.savepoint():
        po.action_record_receipt({po.line_ids[0].id: 0.0})
    assert po.state == "sent"
    assert _events(ctx.env, "goods.received", "fix.purchase.order.line", po.line_ids[0].id) == []


def test_over_receipt_is_refused(ctx):
    po = _sent(ctx)
    with (
        pytest.raises(UserError, match=r"Received 3.00 outside 0..2.00 for Compressor 1.5T"),
        ctx.env.cr.savepoint(),
    ):
        po.action_record_receipt({po.line_ids[0].id: 3.0})


def test_receipt_only_on_a_sent_po(ctx):
    with pytest.raises(UserError, match="sent or acknowledged"), ctx.env.cr.savepoint():
        _po(ctx).action_record_receipt({1: 1.0})


def test_line_quantities_are_validated(ctx):
    po = _po(ctx, lines=[])
    Line = ctx.env["fix.purchase.order.line"]
    base = {"order_id": po.id, "product_id": ctx.compressor.id, "unit_price": 10.0}
    with (
        pytest.raises(UserError, match="Ordered quantity must be positive"),
        ctx.env.cr.savepoint(),
    ):
        Line.create({**base, "qty_ordered": 0.0})
    line = Line.create({**base, "qty_ordered": 1.0})
    assert line.qty_received == 0.0  # only posted receipts move it


# --- requisition approval authority -----------------------------------------------


@pytest.fixture
def requisition_ctx(ctx):
    env = ctx.env
    employee = env["hr.employee"].create({"name": "Karim Store Keeper"})
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Stores Clerk",
                "login": "req-stores-clerk-a06",
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
                "assigned_operating_unit_ids": [(6, 0, ctx.ou.ids)],
                "default_operating_unit_id": ctx.ou.id,
            }
        )
    )

    def make(amount):
        return env["fix.requisition"].create(
            {
                "operating_unit_id": ctx.ou.id,
                "requested_by": employee.id,
                "description": "Compressors for Q3 AMC visits",
                "estimate_amount": amount,
                "cost_centre": "CC-AMC",
                "required_by": date.today() + timedelta(days=30),
            }
        )

    return SimpleNamespace(env=env, make=make, clerk=clerk)


def test_no_requisition_is_approved_by_pressing_approve(requisition_ctx):
    """The 25,000 'anyone may approve' band is gone: every requisition with a
    value is approved from the M63 inbox by a DOFA tier holder."""
    req = requisition_ctx.make(25000.0)
    assert (req.state, req.urgency) == ("draft", "normal")
    with pytest.raises(UserError), requisition_ctx.env.cr.savepoint():
        req.with_user(requisition_ctx.clerk).action_approve()
    assert req.state == "draft"


def test_large_requisition_is_not_the_it_administrators(requisition_ctx):
    req = requisition_ctx.make(25000.01)
    req.with_user(requisition_ctx.clerk).action_submit()
    assert req.state == "submitted"
    with pytest.raises(UserError), requisition_ctx.env.cr.savepoint():
        req.with_user(requisition_ctx.env.ref("base.user_admin")).action_approve()
    assert req.state == "submitted" and not req.dofa_approved
