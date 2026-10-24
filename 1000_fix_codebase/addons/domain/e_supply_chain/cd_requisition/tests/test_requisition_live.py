# cd_requisition live-ORM tests — M16 PO / receipt (three-way match inputs).
import json
import uuid
from datetime import date, datetime
from types import SimpleNamespace

import pytest
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
    assert (first.state, first.currency_id) == ("draft", ctx.env.ref("base.BDT"))


def test_explicit_po_reference_is_kept(ctx):
    assert _po(ctx, name="PO/LEGACY/7").name == "PO/LEGACY/7"


def test_send_publishes_po_issued(ctx):
    po = _po(ctx)
    po.action_send()
    assert po.state == "sent"
    assert _events(ctx.env, "po.issued", "fix.purchase.order", po.id) == [
        {"po_ref": po.name, "vendor_id": ctx.vendor.id, "amount_total": 1360.0, "currency": "BDT"}
    ]


def test_only_a_sent_po_is_acknowledged(ctx):
    with (
        pytest.raises(UserError, match="Only a sent PO can be acknowledged"),
        ctx.env.cr.savepoint(),
    ):
        _po(ctx).action_acknowledge()


def test_acknowledge_with_the_vendors_timestamp(ctx):
    po = _po(ctx)
    po.action_send()
    po.action_acknowledge(acknowledged_at=datetime(2026, 3, 2, 10, 30))
    assert (po.state, po.acknowledged_at) == ("acknowledged", datetime(2026, 3, 2, 10, 30))
    assert _events(ctx.env, "po.acknowledged", "fix.purchase.order", po.id) == [
        {"po_ref": po.name, "vendor_id": ctx.vendor.id}
    ]


def test_acknowledge_defaults_to_now(ctx):
    po = _po(ctx)
    po.action_send()
    po.action_acknowledge()
    assert po.acknowledged_at


def test_partial_then_full_receipt(ctx):
    po = _po(ctx)
    compressor_line, capacitor_line = po.line_ids
    po.action_record_receipt({compressor_line.id: 1.0})
    assert po.state == "partially_received"
    assert (compressor_line.qty_received, capacitor_line.qty_received) == (1.0, 0.0)
    po.action_record_receipt({compressor_line.id: 1.0, capacitor_line.id: 3.0})
    assert po.state == "received"
    events = _events(ctx.env, "goods.received", "fix.purchase.order.line", compressor_line.id)
    assert events == [
        {"po_ref": po.name, "product_id": ctx.compressor.id, "qty_received": 1.0},
        {"po_ref": po.name, "product_id": ctx.compressor.id, "qty_received": 1.0},
    ]
    assert _events(ctx.env, "goods.received", "fix.purchase.order.line", capacitor_line.id) == [
        {"po_ref": po.name, "product_id": ctx.capacitor.id, "qty_received": 3.0}
    ]


def test_receipt_of_nothing_keeps_the_state(ctx):
    po = _po(ctx)
    po.action_send()
    po.action_record_receipt({po.line_ids[0].id: 0.0})  # zero: no movement
    assert po.state == "sent"
    assert _events(ctx.env, "goods.received", "fix.purchase.order.line", po.line_ids[0].id) == []


def test_over_receipt_is_refused(ctx):
    po = _po(ctx)
    with (
        pytest.raises(UserError, match=r"Received 3.00 outside 0..2.00 for Compressor 1.5T"),
        ctx.env.cr.savepoint(),
    ):
        po.action_record_receipt({po.line_ids[0].id: 3.0})


def test_line_quantities_are_validated(ctx):
    po = _po(ctx, lines=[])
    Line = ctx.env["fix.purchase.order.line"]
    base = {"order_id": po.id, "product_id": ctx.compressor.id, "unit_price": 10.0}
    with (
        pytest.raises(UserError, match="Ordered quantity must be positive"),
        ctx.env.cr.savepoint(),
    ):
        Line.create({**base, "qty_ordered": 0.0})
    with (
        pytest.raises(UserError, match=r"Received -1.00 outside 0..1.00 for \?"),
        ctx.env.cr.savepoint(),
    ):
        Line.create({**base, "qty_received": -1.0})


# --- requisition approval authority -----------------------------------------------


@pytest.fixture
def requisition_ctx(ctx):
    env = ctx.env
    employee = env["hr.employee"].create({"name": "Karim Store Keeper"})
    clerk = env["res.users"].create(
        {
            "name": "Stores Clerk",
            "login": f"req-stores-clerk-{uuid.uuid4().hex[:8]}",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )

    def make(amount):
        return env["fix.requisition"].create(
            {
                "operating_unit_id": ctx.ou.id,
                "requested_by": employee.id,
                "description": "Compressors for Q3 AMC visits",
                "estimate_amount": amount,
            }
        )

    return SimpleNamespace(env=env, make=make, clerk=clerk)


def test_requisition_within_authority_is_approved_by_anyone(requisition_ctx):
    req = requisition_ctx.make(25000.0)  # at the threshold, not above
    assert (req.state, req.urgency) == ("draft", "normal")
    req.with_user(requisition_ctx.clerk).action_approve()
    assert req.state == "approved"


def test_large_requisition_needs_cfo_level(requisition_ctx):
    req = requisition_ctx.make(25000.01)
    with (
        pytest.raises(UserError, match="above BDT 25000 require CFO-level approval"),
        requisition_ctx.env.cr.savepoint(),
    ):
        req.with_user(requisition_ctx.clerk).action_approve()
    assert req.state == "draft"
    req.action_approve()  # superuser: base.group_system
    assert req.state == "approved"
