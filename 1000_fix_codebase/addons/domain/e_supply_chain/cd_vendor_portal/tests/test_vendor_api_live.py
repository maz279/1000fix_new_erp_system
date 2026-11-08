# cd_vendor_portal live tests — the P05 vendor API controller, driven
# directly with a fake `request` bound to the rolled-back `odoo_env`.
#
# A06 audit (2026-11-03): these tests sent unapproved POs to vendors with no
# supplier record, acknowledged them as staff with no evidence and recorded
# deliveries on draft POs - all now refused. The fixture seeds what the
# workflows leave (active suppliers, an approved and sent PO, a posted and
# inspected receipt); the attacks are in test_a06_m42_controls.py and
# cd_requisition's test_a06_m16_controls.py.
from datetime import date
from types import SimpleNamespace

import pytest
from odoo.addons.cd_vendor_portal.controllers import vendor_api
from odoo.exceptions import ValidationError

# --- BN-007 money formatting -----------------------------------------------------


@pytest.mark.parametrize(
    ("amount", "text"),
    [
        (None, "0.00"),
        ("not a number", "0.00"),
        (0, "0.00"),
        (999.5, "999.50"),
        ("1234.5", "1,234.50"),
        (123456, "1,23,456.00"),
        (12345678.9, "1,23,45,678.90"),
        (1234567890.12, "1,23,45,67,890.12"),
        # regressions: the rounding carry was lost and negatives mangled
        (999.996, "1,000.00"),
        (-1234.5, "-1,234.50"),
        (-1234567, "-12,34,567.00"),
        (-0.001, "0.00"),
    ],
)
def test_fmt_bdt(amount, text):
    assert vendor_api._fmt_bdt(amount) == text


def test_error_shape_and_vendor_scope(odoo_env, monkeypatch):
    assert vendor_api._error("x", "y") == {"error": {"code": "x", "message": "y"}}
    monkeypatch.setattr(vendor_api, "request", SimpleNamespace(env=odoo_env))
    # internal staff: the explicit procurement filter, or their own rights
    assert vendor_api._vendor_domain({"vendor_id": "42"}) == [("vendor_id", "=", 42)]
    assert vendor_api._vendor_domain({"vendor_id": "x"}) == []
    assert vendor_api._vendor_domain({}) == []


# --- fixtures ----------------------------------------------------------------------


@pytest.fixture
def api(odoo_env, monkeypatch):
    monkeypatch.setattr(vendor_api, "request", SimpleNamespace(env=odoo_env))
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    vendor, other_vendor = env["res.partner"].create(
        [{"name": "Gazi Spares Ltd."}, {"name": "Rangs Parts Ltd."}]
    )
    compressor, capacitor, fan = env["product.product"].create(
        [{"name": "Compressor 1.5T"}, {"name": "Run Capacitor 35uF"}, {"name": "Fan Motor"}]
    )
    for partner in (vendor, other_vendor):
        sup = env["fix.supplier"].create(
            {"name": partner.name, "partner_id": partner.id, "status": "active"}
        )
        for doc_type in ("trade_licence", "tin", "vat"):
            env["fix.supplier.document"].create(
                {"supplier_id": sup.id, "doc_type": doc_type, "state": "valid"}
            )

    def po(vendor_rec=vendor, lines=((compressor, 2.0, 12500.0), (capacitor, 3.0, 120.0))):
        return env["fix.purchase.order"].create(
            {
                "operating_unit_id": ou.id,
                "vendor_id": vendor_rec.id,
                "line_ids": [
                    (0, 0, {"product_id": p.id, "qty_ordered": q, "unit_price": u})
                    for p, q, u in lines
                ],
            }
        )

    def send(order):
        """Approved and sent, as the M63 engine and the buyer leave it."""
        order.action_record_requisition_exception(reason="vendor API test PO")
        order._guarded().write(
            {
                "approval_state": "approved",
                "dofa_approved": True,
                "dofa_approved_tier": order._dofa_current_tier(),
                "dofa_approved_amount": order.amount_total,
            }
        )
        order.action_send()
        return order

    return SimpleNamespace(
        send=send,
        ctl=vendor_api.VendorApiController(),
        env=env,
        ou=ou,
        vendor=vendor,
        other_vendor=other_vendor,
        compressor=compressor,
        capacitor=capacitor,
        fan=fan,
        po=po,
    )


# --- /vendor/purchase-orders ----------------------------------------------------------


def test_list_scopes_to_the_vendor_and_formats_money(api):
    mine = api.po()
    api.po(vendor_rec=api.other_vendor)
    out = api.ctl.purchase_orders(vendor_id=api.vendor.id)
    assert out["total"] == 1
    (row,) = out["purchase_orders"]
    assert (row["id"], row["ref"], row["state"], row["acknowledged_at"]) == (
        mine.id,
        mine.name,
        "draft",
        None,
    )
    assert row["date_order"] == str(mine.date_order)
    # 2 x 12,500 + 3 x 120 = 25,360.00
    assert row["total_bdt"] == "25,360.00"
    assert row["lines"] == [
        {
            "id": mine.line_ids[0].id,
            "product_id": api.compressor.id,
            "product": "Compressor 1.5T",
            "ordered": 2.0,
            "received": 0.0,
            "unit_price_bdt": "12,500.00",
        },
        {
            "id": mine.line_ids[1].id,
            "product_id": api.capacitor.id,
            "product": "Run Capacitor 35uF",
            "ordered": 3.0,
            "received": 0.0,
            "unit_price_bdt": "120.00",
        },
    ]


def test_list_filters_by_state(api):
    sent = api.send(api.po())
    api.po()  # stays draft
    sent.action_acknowledge_on_behalf(
        evidence="vendor e-mail 2026-11-03", confirmed_date="2099-01-01"
    )
    out = api.ctl.purchase_orders(vendor_id=api.vendor.id, state="acknowledged")
    assert [row["id"] for row in out["purchase_orders"]] == [sent.id]
    assert out["purchase_orders"][0]["acknowledged_at"] == str(sent.acknowledged_at)


def test_list_without_vendor_is_the_procurement_view(api):
    ids = (api.po() | api.po(vendor_rec=api.other_vendor)).ids
    listed = [row["id"] for row in api.ctl.purchase_orders()["purchase_orders"]]
    assert set(ids) <= set(listed)


def test_an_action_without_a_po_lists_instead(api):
    out = api.ctl.purchase_orders(action="acknowledge", vendor_id=api.vendor.id)
    assert "purchase_orders" in out


def test_invalid_action(api):
    out = api.ctl.purchase_orders(po_id=api.po().id, action="cancel")
    assert out == {
        "error": {"code": "invalid_action", "message": "action must be acknowledge|deliver"}
    }


def test_unknown_po(api):
    out = api.ctl.purchase_orders(po_id=987654321, action="acknowledge")
    assert out["error"]["code"] == "no_po"


def test_staff_acknowledge_needs_the_vendors_evidence(api):
    order = api.send(api.po())
    out = api.ctl.purchase_orders(po_id=str(order.id), action="acknowledge")
    assert out["error"]["code"] == "po_rejected" and order.state == "sent"
    out = api.ctl.purchase_orders(
        po_id=str(order.id),
        action="acknowledge",
        evidence="vendor letter GS/118",
        delivery_date="2099-01-01",
    )
    assert out == {"purchase_order": {"id": order.id, "state": "acknowledged"}}
    assert order.ack_channel == "buyer_on_behalf" and order.ack_evidence == "vendor letter GS/118"


def test_acknowledging_a_draft_is_rejected_with_the_reason(api):
    out = api.ctl.purchase_orders(
        po_id=api.po().id, action="acknowledge", evidence="vendor letter GS/119"
    )
    assert out == {
        "error": {"code": "po_rejected", "message": "Only a sent PO can be acknowledged"}
    }


def test_delivery_needs_receipts(api):
    for receipts in (None, {}):
        out = api.ctl.purchase_orders(po_id=api.po().id, action="deliver", receipts=receipts)
        assert out["error"]["code"] == "missing_receipts"


def test_delivery_confirmation_records_receipts(api):
    order = api.send(api.po())
    compressor_line, capacitor_line = order.line_ids
    out = api.ctl.purchase_orders(
        po_id=order.id, action="deliver", receipts={str(compressor_line.id): "1"}
    )
    assert out == {"purchase_order": {"id": order.id, "state": "partially_received"}}
    out = api.ctl.purchase_orders(
        po_id=order.id,
        action="deliver",
        receipts={str(compressor_line.id): 1, str(capacitor_line.id): 3.0},
    )
    assert out["purchase_order"]["state"] == "received"
    assert (compressor_line.qty_received, capacitor_line.qty_received) == (2.0, 3.0)


def test_delivery_on_a_draft_po_is_rejected(api):
    order = api.po()
    out = api.ctl.purchase_orders(
        po_id=order.id, action="deliver", receipts={order.line_ids[0].id: 1}
    )
    assert out["error"]["code"] == "po_rejected"
    assert "sent or acknowledged" in out["error"]["message"]


def test_over_delivery_is_rejected(api):
    order = api.send(api.po())
    out = api.ctl.purchase_orders(
        po_id=order.id, action="deliver", receipts={order.line_ids[0].id: 5}
    )
    assert out["error"]["code"] == "po_rejected"
    assert "Received 5.00 outside 0..2.00" in out["error"]["message"]


# --- /vendor/invoices -------------------------------------------------------------


def _received_po(api):
    order = api.send(api.po())
    order.action_record_receipt({line.id: line.qty_ordered for line in order.line_ids})
    for line in order.receipt_ids.line_ids:
        inspection = api.env["fix.procurement.inspection"].create(
            {"receipt_line_id": line.id, "qty_accepted": line.qty_received}
        )
        inspection.action_confirm()
    return order


def _line(product, qty, price, **extra):
    return {
        "product_id": product.id,
        "description": product.name,
        "quantity": qty,
        "unit_price": price,
        **extra,
    }


def test_submission_derives_vendor_and_unit_from_the_po_and_matches(api):
    order = _received_po(api)
    out = api.ctl.invoices(
        invoice_ref="GS/INV/2026/0101",
        po_id=order.id,
        lines=[_line(api.compressor, 2, 12500.0)],
    )
    invoice = api.env["fix.vendor.invoice"].browse(out["invoice"]["id"])
    assert out["invoice"] == {
        "id": invoice.id,
        "match_state": "matched",
        "match_detail": "PO / receipt / invoice reconciled",
    }
    assert (invoice.vendor_id, invoice.operating_unit_id, invoice.requisition_id) == (
        api.vendor,
        order.operating_unit_id,
        order,
    )
    assert invoice.invoice_date == date.today()  # model default, never overridden by None
    assert invoice.line_ids.tds_category == "service_general"


def test_submission_blocks_unreceived_goods_visibly(api):
    order = api.po()  # nothing received yet
    out = api.ctl.invoices(
        invoice_ref="GS/INV/2026/0102",
        po_id=order.id,
        vendor_id=api.vendor.id,
        invoice_date="2026-03-05",
        lines=[
            _line(api.compressor, 2, 12500.0),
            _line(api.fan, 1, 900.0, tds_category="supply_of_goods"),
        ],
    )
    assert out["invoice"]["match_state"] == "blocked"
    assert out["invoice"]["match_detail"] == (
        "Compressor 1.5T: received 0.00 < invoiced 2.00\nFan Motor: not on the PO"
    )
    invoice = api.env["fix.vendor.invoice"].browse(out["invoice"]["id"])
    assert invoice.invoice_date == date(2026, 3, 5)


def test_submission_without_vendor_or_po(api):
    out = api.ctl.invoices(invoice_ref="X-1", lines=[_line(api.fan, 1, 1.0)])
    assert out["error"]["code"] == "missing_vendor"


def test_submission_needs_a_po(api):
    out = api.ctl.invoices(invoice_ref="X-2", vendor_id=api.vendor.id)
    assert out["error"]["code"] == "missing_po"


def test_submission_against_an_unknown_po(api):
    """Regression: a stale PO id raised MissingError (HTTP 500) instead of a
    structured error."""
    out = api.ctl.invoices(invoice_ref="X-3", po_id=987654321, lines=[_line(api.fan, 1, 1.0)])
    assert out == {"error": {"code": "no_po", "message": "Purchase order not found"}}


def test_submission_needs_lines(api):
    out = api.ctl.invoices(invoice_ref="X-4", po_id=api.po().id, lines=[])
    assert out["error"]["code"] == "missing_lines"


def test_submission_defaults_line_values(api):
    order = api.po()
    out = api.ctl.invoices(
        invoice_ref="X-5", po_id=order.id, lines=[{"product_id": api.fan.id, "description": "Fan"}]
    )
    line = api.env["fix.vendor.invoice"].browse(out["invoice"]["id"]).line_ids
    assert (line.quantity, line.unit_price) == (1.0, 0.0)


def test_a_rejected_submission_is_reported(api, monkeypatch):
    Invoice = type(api.env["fix.vendor.invoice"])

    def refuse(self, vals_list):
        raise ValidationError("Vendor invoice ref already used")

    monkeypatch.setattr(Invoice, "create", refuse)
    out = api.ctl.invoices(invoice_ref="X-6", po_id=api.po().id, lines=[_line(api.fan, 1, 1.0)])
    assert out == {
        "error": {"code": "invoice_rejected", "message": "Vendor invoice ref already used"}
    }


def test_invoice_list_shows_block_reasons(api):
    order = api.po()
    api.ctl.invoices(
        invoice_ref="GS/INV/2026/0200",
        po_id=order.id,
        lines=[_line(api.compressor, 1, 13000.0)],
    )
    api.ctl.invoices(
        invoice_ref="RP/INV/1",
        po_id=api.po(vendor_rec=api.other_vendor).id,
        lines=[_line(api.fan, 1, 1.0)],
    )
    out = api.ctl.invoices(vendor_id=api.vendor.id)
    assert out["total"] == 1
    (row,) = out["invoices"]
    assert (row["invoice_ref"], row["po_ref"], row["date"]) == (
        "GS/INV/2026/0200",
        order.name,
        str(date.today()),
    )
    assert row["match_state"] == "blocked"
    assert row["match_detail"] == (
        "Compressor 1.5T: received 0.00 < invoiced 1.00\nCompressor 1.5T: price above PO"
    )
    assert row["subtotal_bdt"] == "13,000.00"
    invoice = api.env["fix.vendor.invoice"].browse(row["id"])
    assert row["tds_bdt"] == vendor_api._fmt_bdt(invoice.tds_amount)
    assert row["payable_bdt"] == vendor_api._fmt_bdt(invoice.total_payable)


def test_invoice_list_handles_unlinked_invoices(api):
    invoice = api.env["fix.vendor.invoice"].create(
        {"vendor_id": api.vendor.id, "invoice_ref": "MANUAL-1", "operating_unit_id": api.ou.id}
    )
    (row,) = api.ctl.invoices(vendor_id=api.vendor.id)["invoices"]
    assert (row["id"], row["po_ref"], row["match_state"]) == (invoice.id, "", "unmatched")
    assert row["match_detail"] == "No purchase order linked"


# --- vendor (portal) sessions: EA-05 fence + no self-recorded receipts -------------


def _vendor_user(api, partner, login):
    group = api.env.ref("cd_vendor_portal.group_fix_vendor_portal")
    return (
        api.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": partner.name,
                "login": login,
                "partner_id": partner.id,
                "group_ids": [(6, 0, [group.id])],
            }
        )
    )


def _as_vendor(api, monkeypatch, user):
    monkeypatch.setattr(vendor_api, "request", SimpleNamespace(env=api.env(user=user.id)))


def test_a_vendor_sees_only_its_own_pos_and_invoices(api, monkeypatch):
    """Regression: _vendor_domain returned [] for a vendor session - every
    vendor listed every PO and invoice; a client vendor_id is now ignored."""
    mine, theirs = api.send(api.po()), api.po(vendor_rec=api.other_vendor)
    draft = api.po()
    Invoice = api.env["fix.vendor.invoice"]
    my_inv = Invoice.create(
        {"vendor_id": api.vendor.id, "invoice_ref": "V-OWN", "operating_unit_id": api.ou.id}
    )
    their_inv = Invoice.create(
        {"vendor_id": api.other_vendor.id, "invoice_ref": "V-FOR", "operating_unit_id": api.ou.id}
    )
    _as_vendor(api, monkeypatch, _vendor_user(api, api.vendor, "gazi@vendor.test"))
    pos = {
        r["id"] for r in api.ctl.purchase_orders(vendor_id=api.other_vendor.id)["purchase_orders"]
    }
    assert mine.id in pos and theirs.id not in pos
    assert draft.id not in pos  # an unapproved draft is not shown to the vendor
    invs = {r["id"] for r in api.ctl.invoices(vendor_id=api.other_vendor.id)["invoices"]}
    assert my_inv.id in invs and their_inv.id not in invs
    # a foreign PO is "not found" for every action
    api.send(theirs)
    assert api.ctl.purchase_orders(po_id=theirs.id, action="acknowledge")["error"]["code"] == (
        "no_po"
    )
    assert theirs.state == "sent"


def test_a_vendor_acknowledges_its_po_but_cannot_record_receipts(api, monkeypatch):
    order = api.send(api.po())
    _as_vendor(api, monkeypatch, _vendor_user(api, api.vendor, "gazi2@vendor.test"))
    out = api.ctl.purchase_orders(po_id=order.id, action="acknowledge", delivery_date="2099-01-01")
    assert out == {"purchase_order": {"id": order.id, "state": "acknowledged"}}
    assert order.ack_channel == "portal" and str(order.vendor_confirmed_date) == "2099-01-01"
    out = api.ctl.purchase_orders(
        po_id=order.id, action="deliver", receipts={order.line_ids[0].id: 1}
    )
    assert out["error"]["code"] == "forbidden"
    assert order.line_ids[0].qty_received == 0.0


def test_vendor_portal_acl_is_read_only_and_rule_scoped(api):
    user = _vendor_user(api, api.vendor, "gazi3@vendor.test")
    mine, theirs = api.po(), api.po(vendor_rec=api.other_vendor)
    PO = api.env["fix.purchase.order"].with_user(user)
    assert PO.search([("id", "in", (mine | theirs).ids)]).ids == [mine.id]
    for model in ("fix.purchase.order", "fix.vendor.invoice"):
        assert not api.env[model].with_user(user).has_access("write")
        assert not api.env[model].with_user(user).has_access("create")
