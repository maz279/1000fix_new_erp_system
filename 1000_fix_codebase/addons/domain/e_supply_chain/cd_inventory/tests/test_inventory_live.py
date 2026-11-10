# cd_inventory live-ORM tests — M15 spare parts, locations, consumption,
# valuation suspense (GV-005), reorder engine (M43 seam), graded stock.
#
# A06 remediation: the part's on-hand is the location ledger (it used to be
# typed into qty_available here), the issue takes the van's own bucket, the
# replenishment rule reads its own location, and an empty van audit is
# refused. The tests that asserted the old behaviour were rewritten to the
# ledger (see the comments on each).
import functools
import json
import logging
import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError, ValidationError

import libs.py.fix_events as fix_events

from .conftest import make_service_order

# per-run tag: unique keys (part number, location codes, serials) never
# collide with a concurrent run on fix_test
TAG = uuid.uuid4().hex[:6].upper()
PN = f"SM-A556-{TAG}"
BARCODE = f"880609{TAG}"
QR = f"QR-LCD-{TAG}"
HUB = f"MIR-{TAG}"
VAN = f"VAN07-{TAG}"


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


def _failing_publish(*_args, **_kwargs):
    raise RuntimeError("outbox unavailable")


class _Ctx(SimpleNamespace):
    @functools.cached_property
    def job(self):
        """A real service order: an issue is charged to a real job (A06 M15-10)."""
        return make_service_order(self.env, self.branch, TAG)

    @functools.cached_property
    def branch(self):
        """Created on first use, on its OWN company: fix.entity is UNIQUE per
        company, so an entity on the shared main company would serialise
        every concurrent test run behind one uncommitted row."""
        company = self.env["res.company"].create({"name": f"QA Inventory Co {TAG}"})
        entity = self.env["fix.entity"].create(
            {"code": f"E{TAG}", "legal_name": "Inventory Test Ltd", "company_id": company.id}
        )
        return self.env["fix.branch"].create(
            {
                "code": f"B{TAG}",
                "name": "Mirpur Hub",
                "entity_id": entity.id,
                "operating_unit_id": self.ou.id,
            }
        )


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    technician = env["hr.employee"].create({"name": "Jamal Technician"})
    hub = env["fix.stock.location"].create({"name": "Mirpur Hub Store", "code": HUB})
    van = env["fix.stock.location"].create(
        {
            "name": "Van 7",
            "code": VAN,
            "location_type": "van",
            "technician_id": technician.id,
            "van_plate": "DHAKA-METRO-GA-11-2233",
        }
    )
    part = env["fix.spare.part"].create(
        {
            "name": "Galaxy A55 Display Assembly",
            "part_number": PN,
            "barcode": BARCODE,
            "qr_code": QR,
            "unit_cost": 450.0,
        }
    )
    # the van holds 10 (the van class of the ledger); qty_available follows
    env["fix.stock.onhand"]._apply(part, van, "van", 10.0, 450.0)
    return _Ctx(env=env, ou=ou, technician=technician, hub=hub, van=van, part=part)


def _set_hub_stock(ctx, qty):
    """Put exactly `qty` of the part at the hub (the rule's location)."""
    Onhand = ctx.env["fix.stock.onhand"]
    row = Onhand._bucket(ctx.part, ctx.hub, "owned")
    current = row.qty if row else 0.0
    if qty != current:
        Onhand._apply(ctx.part, ctx.hub, "owned", qty - current, 450.0)


# --- spare part master -------------------------------------------------------------


def test_spare_part_defaults_and_related_fields(ctx):
    part = ctx.part
    assert (part.part_category, part.category, part.uom, part.state) == (
        "display",
        "display",
        "PCS",
        "active",
    )
    part.device_brand = "Samsung"
    assert part.brand == "Samsung"
    assert (part.min_qty, part.max_qty, part.warranty_months) == (5.0, 25.0, 6)


@pytest.mark.parametrize(("min_qty", "max_qty"), [(-1.0, 10.0), (0.0, -1.0)])
def test_spare_part_thresholds_cannot_be_negative(ctx, min_qty, max_qty):
    with pytest.raises(ValidationError, match="cannot be negative"), ctx.env.cr.savepoint():
        ctx.part.write({"min_qty": min_qty, "max_qty": max_qty})


def test_spare_part_max_below_min_is_refused(ctx):
    with (
        pytest.raises(ValidationError, match="cannot be less than minimum"),
        ctx.env.cr.savepoint(),
    ):
        ctx.part.write({"min_qty": 10.0, "max_qty": 9.0})


@pytest.mark.parametrize("code", [BARCODE, QR, PN, f"  {PN}  "])
def test_find_by_barcode_qr_or_part_number(ctx, code):
    assert ctx.env["fix.spare.part"].find_by_code(code) == ctx.part


@pytest.mark.parametrize("code", ["UNKNOWN-1", "", None])
def test_find_by_code_miss(ctx, code):
    assert not ctx.env["fix.spare.part"].find_by_code(code)


# --- stock locations / van stock -------------------------------------------------


def test_van_flags(ctx):
    assert (ctx.van.is_van_stock, ctx.van.is_van_location) == (True, True)
    assert (ctx.hub.is_van_stock, ctx.hub.is_van_location, ctx.hub.location_type) == (
        False,
        False,
        "branch",
    )


def test_van_requires_a_custodian(ctx):
    with (
        pytest.raises(ValidationError, match="must designate a custodian technician"),
        ctx.env.cr.savepoint(),
    ):
        ctx.env["fix.stock.location"].create(
            {"name": "Van 8", "code": f"VAN08-{TAG}", "location_type": "van"}
        )


def test_van_audit_reconciles_and_publishes(ctx):
    skus = [{"sku": "A", "discrepancy_qty": 0}, {"sku": "B", "discrepancy_qty": -1}, {"sku": "C"}]
    out = ctx.van.action_audit_van_stock(skus)
    # 3 audited, 1 discrepancy -> (3 - 1) / 3 = 66.7 %
    assert out == {
        "van_id": ctx.van.id,
        "audited_count": 3,
        "discrepancies": 1,
        "accuracy_pct": 66.7,
        "status": "reconciled",
    }
    # The model stamps fields.Date.context_today (user tz, Asia/Dhaka in the test
    # env); asserting date.today() of the UTC test process flipped this test to
    # "tomorrow" every evening after 18:00 UTC (the R01 Windows tzset note in
    # addons/conftest.py). Expect the date the same way the model computes it.
    from odoo import fields as odoo_fields

    assert (
        ctx.van.last_audit_date,
        ctx.van.audit_discrepancy_count,
    ) == (odoo_fields.Date.context_today(ctx.van), 1)
    assert _events(ctx.env, "van.reconciled", "fix.stock.location", ctx.van.id) == [
        {
            "van_id": ctx.van.id,
            "van_code": VAN,
            "technician_id": ctx.technician.id,
            "audited_qty": 3,
            "discrepancy_qty": 1,
            "accuracy_pct": 66.7,
            "audit_date": str(date.today()),
        }
    ]


def test_empty_van_audit_is_refused(ctx):
    """A06 M15-16: an audit with no lines used to report 100% accuracy."""
    with (
        pytest.raises(ValidationError, match="at least one audited line"),
        ctx.env.cr.savepoint(),
    ):
        ctx.van.action_audit_van_stock()


def test_audit_is_van_only(ctx):
    with (
        pytest.raises(ValidationError, match="only be performed on van stock locations"),
        ctx.env.cr.savepoint(),
    ):
        ctx.hub.action_audit_van_stock([])


def test_van_audit_survives_an_outbox_failure(ctx, monkeypatch, caplog):
    monkeypatch.setattr(fix_events, "publish", _failing_publish)
    with caplog.at_level(logging.ERROR):
        out = ctx.van.action_audit_van_stock([{"discrepancy_qty": 2}])
    assert out["accuracy_pct"] == 0.0
    assert "van.reconciled event publish failed" in caplog.text


# --- valuation suspense (GV-005) ---------------------------------------------------


def _suspense(ctx, **vals):
    return ctx.env["fix.inventory.valuation.suspense"].create({"product_id": ctx.part.id, **vals})


def test_suspense_defaults_and_derived_total(ctx):
    entry = _suspense(ctx, quantity=3.0, unit_cost=150.0)
    assert entry.total_valuation == 450.0  # 3 x 150, derived when not given
    assert entry.name.startswith("VAL-SUSP/")
    assert (entry.entry_type, entry.suspense_account_code, entry.status) == (
        "consumption",
        "110999",
        "pending_gl_cutover",
    )
    assert (entry.stub_reference, entry.stub_expiry_date) == (
        "STUB-M15-M19-001",
        date(2026, 11, 30),
    )


def test_suspense_explicit_total_and_partial_values_are_kept(ctx):
    assert (
        _suspense(ctx, quantity=3.0, unit_cost=150.0, total_valuation=400.0).total_valuation
        == 400.0
    )
    assert _suspense(ctx, quantity=3.0).total_valuation == 0.0  # no unit cost: nothing derived
    assert _suspense(ctx, name="VAL/MANUAL").name == "VAL/MANUAL"


def test_reconcile_to_gl(ctx):
    entry = _suspense(ctx, quantity=1.0, unit_cost=10.0)
    out = entry.action_reconcile_to_gl("JV/2026/0042")
    assert out == {"status": "reconciled", "entry": entry.name, "gl_voucher": "JV/2026/0042"}
    assert (entry.status, entry.gl_cutover_ref) == ("reconciled", "JV/2026/0042")
    assert entry.reconciled_at


@pytest.mark.parametrize("ref", ["", None])
def test_reconcile_needs_a_voucher(ctx, ref):
    entry = _suspense(ctx, quantity=1.0, unit_cost=10.0)
    with (
        pytest.raises(UserError, match="GL Voucher reference is mandatory"),
        ctx.env.cr.savepoint(),
    ):
        entry.action_reconcile_to_gl(ref)
    assert entry.status == "pending_gl_cutover"


# --- scan-to-consume ------------------------------------------------------------------


def _consumption(ctx, **vals):
    base = {
        "service_order_ref": ctx.job.name,
        "product_id": ctx.part.id,
        "location_id": ctx.van.id,
        "technician_id": ctx.technician.id,
        "quantity": 2.0,
        "scanned_code": BARCODE,
    }
    base.update(vals)
    return ctx.env["fix.stock.consumption"].create(base)


def test_consumption_numbering_and_cost(ctx):
    first, second = _consumption(ctx), _consumption(ctx, unit_cost=12.5, quantity=4.0)
    assert first.name.startswith("CNS/")
    assert first.name != second.name
    assert second.total_cost == 50.0  # 4 x 12.50
    assert _consumption(ctx, name="CNS/MANUAL").name == "CNS/MANUAL"


def test_scan_and_consume_deducts_values_and_publishes(ctx):
    # A06 M15-10: a work-order reference must name a real work order; this
    # issue is charged to its service order only
    rec = _consumption(ctx, serial_number="IMEI-1")
    out = rec.action_scan_and_consume()
    # 10 on hand - 2 consumed = 8; valuation 2 x 450 = 900.00
    assert ctx.part.qty_available == 8.0
    assert (rec.state, rec.unit_cost, rec.total_cost) == ("consumed", 450.0, 900.0)
    assert rec.consumed_at
    entry = ctx.env["fix.inventory.valuation.suspense"].search([("consumption_id", "=", rec.id)])
    assert (entry.quantity, entry.unit_cost, entry.total_valuation, entry.entry_type) == (
        2.0,
        450.0,
        900.0,
        "consumption",
    )
    assert out == {
        "status": "consumed",
        "consumption_ref": rec.name,
        "remaining_qty": 8.0,
        "valuation_entry": entry.name,
    }
    (event,) = _events(ctx.env, "stock.consumed", "fix.stock.consumption", rec.id)
    assert event == {
        "consumption_id": rec.id,
        "consumption_ref": rec.name,
        "service_order_ref": ctx.job.name,
        "work_order_ref": "",
        "part_id": ctx.part.id,
        "part_number": PN,
        "quantity": 2.0,
        "ownership_class": "van",
        "location_id": ctx.van.id,
        "location_code": VAN,
        "technician_id": ctx.technician.id,
        "serial_number": "IMEI-1",
        "scanned_code": BARCODE,
        "consumed_at": event["consumed_at"],
        "suspense_entry_id": entry.id,
    }


def test_consume_blank_refs_are_published_empty(ctx):
    rec = _consumption(ctx)
    rec.action_scan_and_consume()
    (event,) = _events(ctx.env, "stock.consumed", "fix.stock.consumption", rec.id)
    assert (event["work_order_ref"], event["serial_number"]) == ("", "")


def test_only_a_draft_scan_is_consumed(ctx):
    rec = _consumption(ctx)
    rec.action_scan_and_consume()
    with pytest.raises(UserError, match="Only draft scans"), ctx.env.cr.savepoint():
        rec.action_scan_and_consume()
    assert ctx.part.qty_available == 8.0  # deducted once


def test_consume_without_a_part_is_refused(ctx):
    draft = ctx.env["fix.stock.consumption"].new({"state": "draft", "quantity": 1.0})
    with pytest.raises(ValidationError, match="No valid spare part"), ctx.env.cr.savepoint():
        draft.action_scan_and_consume()


def test_serialized_part_needs_a_serial(ctx):
    ctx.part.is_serialized = True
    ctx.env["fix.stock.lot"].create(
        {"name": f"IMEI-{TAG}", "part_id": ctx.part.id, "location_id": ctx.van.id, "qty": 1.0}
    )
    rec = _consumption(ctx, quantity=1.0)
    with pytest.raises(ValidationError, match=f"{PN} is serialized"), ctx.env.cr.savepoint():
        rec.action_scan_and_consume()
    rec.serial_number = f"IMEI-{TAG}"  # a serial received at this van
    rec.action_scan_and_consume()
    assert rec.state == "consumed"


def test_insufficient_stock_is_refused(ctx):
    rec = _consumption(ctx, quantity=11.0)
    with (
        pytest.raises(
            UserError, match=f"Insufficient stock for {PN} at {VAN}: 10.0 available, 11.0"
        ),
        ctx.env.cr.savepoint(),
    ):
        rec.action_scan_and_consume()
    assert (rec.state, ctx.part.qty_available) == ("draft", 10.0)


def test_consume_survives_an_outbox_failure(ctx, monkeypatch, caplog):
    rec = _consumption(ctx)  # the job exists before the outbox goes down
    monkeypatch.setattr(fix_events, "publish", _failing_publish)
    with caplog.at_level(logging.ERROR):
        out = rec.action_scan_and_consume()
    assert (out["status"], ctx.part.qty_available) == ("consumed", 8.0)
    assert "stock.consumed event publish failed" in caplog.text


def test_return_restores_stock_and_reverses_valuation(ctx):
    rec = _consumption(ctx)
    rec.action_scan_and_consume()
    out = rec.action_return_part("wrong_diagnosis", "Board fault, not display")
    assert ctx.part.qty_available == 10.0
    assert (rec.state, rec.return_reason, rec.return_notes) == (
        "returned",
        "wrong_diagnosis",
        "Board fault, not display",
    )
    assert rec.returned_at
    reversal = ctx.env["fix.inventory.valuation.suspense"].search(
        [("consumption_id", "=", rec.id), ("entry_type", "=", "return")]
    )
    assert (reversal.quantity, reversal.total_valuation) == (-2.0, -900.0)
    assert out == {
        "status": "returned",
        "consumption_ref": rec.name,
        "restored_qty": 10.0,
        "quarantine": None,
    }
    (event,) = _events(ctx.env, "stock.returned", "fix.stock.consumption", rec.id)
    assert (event["return_reason"], event["quantity"], event["suspense_entry_id"]) == (
        "wrong_diagnosis",
        2.0,
        reversal.id,
    )


def test_only_consumed_parts_are_returned(ctx):
    with (
        pytest.raises(UserError, match="Only consumed parts can be returned"),
        ctx.env.cr.savepoint(),
    ):
        _consumption(ctx).action_return_part("excess_draw")


def test_return_survives_an_outbox_failure(ctx, monkeypatch, caplog):
    rec = _consumption(ctx)
    rec.action_scan_and_consume()
    monkeypatch.setattr(fix_events, "publish", _failing_publish)
    with caplog.at_level(logging.ERROR):
        out = rec.action_return_part("excess_draw")
    assert out["restored_qty"] == 10.0
    assert not rec.return_notes  # notes default to ""
    assert "stock.returned event publish failed" in caplog.text


# --- reorder engine + M43 seam ----------------------------------------------------------


def _rule(ctx, **vals):
    base = {"spare_part_id": ctx.part.id, "location_id": ctx.hub.id, "branch_id": ctx.branch.id}
    base.update(vals)
    return ctx.env["fix.reorder.rule"].create(base)


def test_rule_numbering_and_defaults(ctx):
    rule = _rule(ctx)
    assert rule.name.startswith("RDR/")
    assert (rule.min_qty, rule.max_qty, rule.safety_stock, rule.lead_time_days, rule.state) == (
        5.0,
        20.0,
        2.0,
        3,
        "active",
    )
    assert rule.m43_model_version == "m43_seam_v1.0"
    assert _rule(ctx, name="RDR/MANUAL").name == "RDR/MANUAL"


def test_rule_quantities_are_validated(ctx):
    assert ctx.branch  # created OUTSIDE the savepoints below (they roll back)
    with (
        pytest.raises(ValidationError, match="Minimum quantity cannot be negative"),
        ctx.env.cr.savepoint(),
    ):
        _rule(ctx, min_qty=-1.0)
    with (
        pytest.raises(ValidationError, match="must strictly exceed minimum"),
        ctx.env.cr.savepoint(),
    ):
        _rule(ctx, min_qty=20.0, max_qty=20.0)


def test_current_stock_and_suggestion(ctx):
    # the rule reads ITS location (the hub), not the company-wide aggregate
    _set_hub_stock(ctx, 3.0)
    rule = _rule(ctx)
    # 3 on hand <= min 5 -> order up to max: 20 - 3 = 17
    assert (rule.current_stock, rule.suggested_order_qty) == (3.0, 17.0)
    _set_hub_stock(ctx, 5.0)  # at the reorder point
    rule.invalidate_recordset(["current_stock", "suggested_order_qty"])
    assert rule.suggested_order_qty == 15.0
    _set_hub_stock(ctx, 10.0)  # above the reorder point
    rule.invalidate_recordset(["current_stock", "suggested_order_qty"])
    assert rule.suggested_order_qty == 0.0


def test_unsaved_rule_without_a_part_has_no_stock(ctx):
    draft = ctx.env["fix.reorder.rule"].new({"min_qty": 5.0, "max_qty": 20.0})
    assert (draft.current_stock, draft.suggested_order_qty) == (0.0, 20.0)


def test_dynamic_reorder_point_static_and_m43(ctx):
    rule = _rule(ctx)
    assert rule.compute_dynamic_reorder_point() == 7.0  # min 5 + safety 2
    rule.m43_ai_override = True
    assert rule.compute_dynamic_reorder_point() == 7.0  # no forecast yet: static
    rule.m43_predicted_demand = 14.0
    # 14 per week = 2/day x 3 days lead = 6 + safety 2 = 8.00
    assert rule.compute_dynamic_reorder_point() == 8.0
    rule.m43_ai_override = False
    assert rule.compute_dynamic_reorder_point() == 7.0  # forecast ignored when off


def test_trigger_reorder_alerts_and_publishes(ctx):
    _set_hub_stock(ctx, 3.0)
    rule = _rule(ctx)
    out = rule.action_trigger_reorder()
    assert out == {
        "status": "alert_triggered",
        "rule": rule.name,
        "part": PN,
        "order_qty": 17.0,
    }
    assert rule.state in ("alert", "ordered")  # "ordered" when a requisition was drafted
    assert rule.last_alert_date
    (event,) = _events(ctx.env, "reorder.triggered", "fix.reorder.rule", rule.id)
    assert event == {
        "rule_id": rule.id,
        "rule_code": rule.name,
        "spare_part_id": ctx.part.id,
        "part_number": PN,
        "part_name": "Galaxy A55 Display Assembly",
        "location_id": ctx.hub.id,
        "location_code": HUB,
        "branch_id": ctx.branch.id,
        "branch_name": ctx.branch.name,
        "current_stock": 3.0,
        "min_qty": 5.0,
        "suggested_order_qty": 17.0,
        "m43_dynamic_reorder_point": 7.0,
        "triggered_at": event["triggered_at"],
    }


def test_trigger_reorder_refused_above_the_reorder_point(ctx):
    """A06 M15-12: the manual trigger used to alert with stock above the
    minimum (and order "at least one" above the maximum)."""
    _set_hub_stock(ctx, 25.0)
    with pytest.raises(UserError, match="above the reorder point"), ctx.env.cr.savepoint():
        _rule(ctx).action_trigger_reorder()


def test_trigger_reorder_survives_an_outbox_failure(ctx, monkeypatch, caplog):
    monkeypatch.setattr(fix_events, "publish", _failing_publish)
    rule = _rule(ctx)
    with caplog.at_level(logging.ERROR):
        out = rule.action_trigger_reorder()
    assert out["status"] == "alert_triggered" and rule.state in ("alert", "ordered")
    assert "reorder.triggered event publish failed" in caplog.text


def test_replenishment_sweep(ctx):
    Rule = ctx.env["fix.reorder.rule"]
    Onhand = ctx.env["fix.stock.onhand"]
    baseline = Rule.search_count([("state", "in", ["active", "alert", "ordered"])])
    low_part = ctx.part.copy({"part_number": f"LOW-{TAG}"})
    ok_part = ctx.part.copy({"part_number": f"OK-{TAG}"})
    Onhand._apply(low_part, ctx.hub, "owned", 3.0, 450.0)
    Onhand._apply(ok_part, ctx.hub, "owned", 10.0, 450.0)
    Onhand._apply(ok_part, ctx.van, "van", 10.0, 450.0)
    low = _rule(ctx, spare_part_id=low_part.id)
    recovered = _rule(ctx, spare_part_id=ok_part.id, state="alert")
    steady = _rule(ctx, spare_part_id=ok_part.id, location_id=ctx.van.id)
    archived = _rule(ctx, spare_part_id=low_part.id, location_id=ctx.van.id, state="archived")
    out = Rule.check_replenishment_alerts()
    assert out["rules_checked"] == baseline + 3
    mine = [d for d in out["details"] if d["rule"] == low.name]
    assert mine == [
        {"status": "alert_triggered", "rule": low.name, "part": f"LOW-{TAG}", "order_qty": 17.0}
    ]
    assert low.state in ("alert", "ordered")
    assert (recovered.state, steady.state, archived.state) == (
        "active",  # stock back above min: the alert clears
        "active",
        "archived",  # archived rules are never swept
    )


# --- graded / refurbished stock -----------------------------------------------------------


@pytest.fixture
def graded(ctx):
    brand = ctx.env["fix.brand"].create({"name": f"QA Graded Brand {TAG}", "code": f"G{TAG}"})
    model = ctx.env["fix.device.model"].create({"name": "iPhone 13", "brand_id": brand.id})
    device = ctx.env["fix.device"].create(
        {"device_model_id": model.id, "serial_number": f"F2LXK0-{TAG}"}
    )
    grade = ctx.env["fix.refurb.grade"].search([("code", "=", "A")], limit=1)

    def make(**vals):
        base = {
            "device_id": device.id,
            "grade_id": grade.id,
            "acquisition_cost": 5000.0,
            "refurbishment_cost": 1200.0,
            "resale_price": 8000.0,
        }
        base.update(vals)
        return ctx.env["fix.graded.stock"].create(base)

    return SimpleNamespace(make=make, device=device, grade=grade)


def test_graded_stock_valuation_and_margin(ctx, graded):
    stock = graded.make()
    # valuation 5000 + 1200 = 6200; margin 8000 - 6200 = 1800
    assert (stock.inventory_valuation, stock.projected_margin) == (6200.0, 1800.0)
    stock.refurbishment_cost = 2000.0
    assert (stock.inventory_valuation, stock.projected_margin) == (7000.0, 1000.0)
    assert stock.state == "in_stock"


def test_graded_stock_tags_are_unique(ctx, graded):
    """Regression: every graded unit used to be tagged 'STK/GRD/New'."""
    first, second = graded.make(), graded.make()
    assert first.name.startswith("STK/GRD/")
    assert first.name != second.name
    assert graded.make(name="STK/GRD/MANUAL").name == "STK/GRD/MANUAL"


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("acquisition_cost", "Acquisition cost cannot be negative"),
        ("refurbishment_cost", "Refurbishment cost cannot be negative"),
        ("resale_price", "Resale price cannot be negative"),
    ],
)
def test_graded_stock_amounts_cannot_be_negative(ctx, graded, field, message):
    with pytest.raises(ValidationError, match=message), ctx.env.cr.savepoint():
        graded.make(**{field: -1.0})


def test_reserve_then_sell(ctx, graded):
    stock = graded.make()
    stock.action_reserve()
    assert stock.state == "reserved"
    with (
        pytest.raises(UserError, match="Only in-stock items can be reserved"),
        ctx.env.cr.savepoint(),
    ):
        stock.action_reserve()
    stock.action_sell()
    assert stock.state == "sold"
    assert _events(ctx.env, "graded_stock.sold", "fix.graded.stock", stock.id) == [
        {
            "device": graded.device.name,
            "grade": "A",
            "valuation": 6200.0,
            "resale_price": 8000.0,
            "margin": 1800.0,
        }
    ]
    with (
        pytest.raises(UserError, match="Only in-stock or reserved items can be sold"),
        ctx.env.cr.savepoint(),
    ):
        stock.action_sell()


def test_sell_straight_from_stock(ctx, graded):
    stock = graded.make()
    stock.action_sell()
    assert stock.state == "sold"


def _stock_user(env, login, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return env["res.users"].create(
        {"name": login, "login": "%s-%s" % (login, TAG), "group_ids": [(6, 0, ids)]}
    )


def test_a_clerk_cannot_type_a_graded_unit_sold(ctx, graded):
    """A04 integration (M38 gst_01 / p03_06): the state, and once the unit is
    committed the money, change only through the transitions."""
    clerk = _stock_user(ctx.env, "gst-clerk")
    stock = graded.make()
    with pytest.raises(UserError, match="cannot be set directly"), ctx.env.cr.savepoint():
        stock.with_user(clerk).write({"state": "sold", "resale_price": 1.0})
    with pytest.raises(UserError, match="cannot be set directly"), ctx.env.cr.savepoint():
        ctx.env["fix.graded.stock"].with_user(clerk).create(
            {"device_id": graded.device.id, "grade_id": graded.grade.id, "state": "sold"}
        )
    with pytest.raises(UserError, match="Inventory Controller"), ctx.env.cr.savepoint():
        stock.with_user(clerk).action_sell()
    stock.with_user(clerk).write({"resale_price": 8500.0})  # in stock: still priced freely
    controller = _stock_user(ctx.env, "gst-ctl", "cd_wms_structure.group_inventory_controller")
    stock.with_user(controller).action_reserve()
    with pytest.raises(UserError, match="cannot be set directly"), ctx.env.cr.savepoint():
        stock.with_user(controller).write({"resale_price": 1.0})
    stock.with_user(controller).action_release()
    assert (stock.state, stock.resale_price) == ("in_stock", 8500.0)
    stock.with_user(controller).action_sell()
    assert stock.state == "sold"
    assert _events(ctx.env, "graded_stock.sold", "fix.graded.stock", stock.id)


# --- MIG-03 legacy reference (migrations/load_inventory.py) ----------------------------

LEGACY_TABLES = {
    "fix.spare.part": "fix_spare_part",
    "fix.stock.location": "fix_stock_location",
    "fix.inventory.valuation.suspense": "fix_inventory_valuation_suspense",
}


def _legacy_record(ctx, model):
    if model == "fix.spare.part":
        return ctx.part
    if model == "fix.stock.location":
        return ctx.hub
    return _suspense(ctx, quantity=4.0, unit_cost=450.0, entry_type="initial_count")


@pytest.mark.parametrize("model", sorted(LEGACY_TABLES))
def test_legacy_reference_is_declared_on_the_loaded_models(ctx, model):
    """The loader no longer has to ALTER TABLE: the ORM owns the column."""
    field = ctx.env[model]._fields["legacy_reference"]
    assert (field.type, field.store, field.readonly, field.copy) == ("char", True, True, False)
    assert field.index
    table = LEGACY_TABLES[model]
    ctx.env.cr.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        (table, "legacy_reference"),
    )
    assert ctx.env.cr.fetchone() == (1,)
    ctx.env.cr.execute(
        "SELECT 1 FROM pg_indexes WHERE tablename = %s AND indexdef LIKE %s",
        (table, "%legacy_reference%"),
    )
    assert ctx.env.cr.fetchone() == (1,)


@pytest.mark.parametrize("model", sorted(LEGACY_TABLES))
def test_loader_written_reference_is_read_and_searchable(ctx, model):
    record = _legacy_record(ctx, model)
    ref = f"LEG:SRC38:{HUB}:{model}"
    ctx.env.flush_all()
    # exactly what the loader does: a raw UPDATE/INSERT of the column
    ctx.env.cr.execute(
        f"UPDATE {LEGACY_TABLES[model]} SET legacy_reference = %s WHERE id = %s",
        (ref, record.id),
    )
    record.invalidate_recordset(["legacy_reference"])
    assert record.legacy_reference == ref
    assert ctx.env[model].search([("legacy_reference", "=", ref)]) == record


def test_legacy_reference_is_permanent_and_never_copied(ctx):
    part = ctx.env["fix.spare.part"].create(
        {
            "name": "Legacy compressor",
            "part_number": f"LEG-CMP-{TAG}",
            "legacy_reference": f"LEG:SRC37:LEG-CMP-{TAG}",
        }
    )
    assert part.legacy_reference == f"LEG:SRC37:LEG-CMP-{TAG}"
    clone = part.copy({"part_number": f"LEG-CMP2-{TAG}"})
    assert clone.legacy_reference is False  # a copy is a NEW record, not a migrated one
    assert part.legacy_reference == f"LEG:SRC37:LEG-CMP-{TAG}"
