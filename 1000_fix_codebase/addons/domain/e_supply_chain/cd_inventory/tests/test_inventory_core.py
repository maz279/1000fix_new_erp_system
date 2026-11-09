# cd_inventory tests — M15 Spare Parts & Inventory core behaviour (CD-M15-01).
#
# A06 audit M15-17: this file used to "certify" the module by grepping its
# source for "stock.consumed", "110999" and "van.reconciled". Those were
# not tests of behaviour; they are replaced by executed checks of the same
# promises: the consumption books 110999 and publishes stock.consumed, the
# return reverses it, the van audit publishes van.reconciled, and the ledger
# (not a typed number) is what the part reports.
import json

import pytest
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


def _event(env, event_type, aggregate, aggregate_id):
    rows = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", event_type),
                ("aggregate", "=", aggregate),
                ("aggregate_id", "=", aggregate_id),
            ]
        )
    )
    return [json.loads(r.payload) for r in rows]


def test_location_code_unique_per_company(inv):
    with pytest.raises(IntegrityError), inv.env.cr.savepoint():
        inv.env["fix.stock.location"].create({"name": "dup", "code": inv.central.code})
        inv.env.flush_all()


def test_van_location_flags_and_custodian(inv):
    assert (inv.van.is_van_location, inv.van.is_van_stock, inv.van.technician_id) == (
        True,
        True,
        inv.tech1,
    )
    assert not inv.hub.is_van_location


def test_van_audit_publishes_van_reconciled(inv):
    out = inv.van.action_audit_van_stock(
        [{"sku": "A", "discrepancy_qty": 0}, {"sku": "B", "discrepancy_qty": 1}]
    )
    assert (out["audited_count"], out["discrepancies"], out["accuracy_pct"]) == (2, 1, 50.0)
    (event,) = _event(inv.env, "van.reconciled", "fix.stock.location", inv.van.id)
    assert event["discrepancy_qty"] == 1 and inv.van.audit_discrepancy_count == 1


def test_empty_van_audit_is_refused(inv):
    """M15-16: an audit with no lines used to report 100% accuracy."""
    with pytest.raises(ValidationError, match="at least one audited line"), inv.env.cr.savepoint():
        inv.van.action_audit_van_stock([])


def test_part_reports_the_ledger(inv):
    assert inv.part.qty_available == 10.0 and inv.part.average_cost == 500.0
    inv.stock(inv.part, inv.hub, 5.0, 200.0)
    assert inv.part.qty_available == 15.0
    assert inv.part.average_cost == pytest.approx((10 * 500 + 5 * 200) / 15, abs=1e-3)
    inv.stock(inv.part, inv.hub, 5.0, 100.0, cls="consignment")
    assert inv.part.qty_available == 20.0  # on hand...
    assert inv.part.average_cost == pytest.approx(
        (10 * 500 + 5 * 200) / 15, abs=1e-3
    )  # ...not valued


def test_consumption_books_110999_and_publishes(inv):
    rec = inv.issue(inv.keeper, qty=2.0)
    rec.with_user(inv.keeper).action_scan_and_consume()
    entry = (
        inv.env["fix.inventory.valuation.suspense"].sudo().search([("consumption_id", "=", rec.id)])
    )
    assert (entry.suspense_account_code, entry.entry_type, entry.total_valuation) == (
        "110999",
        "consumption",
        1000.0,
    )
    assert entry.stub_reference == "STUB-M15-M19-001"
    (event,) = _event(inv.env, "stock.consumed", "fix.stock.consumption", rec.id)
    assert (event["quantity"], event["suspense_entry_id"]) == (2.0, entry.id)


def test_return_reverses_and_publishes(inv):
    rec = inv.issue(inv.keeper, qty=2.0)
    rec.with_user(inv.keeper).action_scan_and_consume()
    rec.with_user(inv.keeper).action_return_part("wrong_diagnosis")
    rows = (
        inv.env["fix.inventory.valuation.suspense"].sudo().search([("consumption_id", "=", rec.id)])
    )
    assert sorted(rows.mapped("total_valuation")) == [-1000.0, 1000.0]
    assert _event(inv.env, "stock.returned", "fix.stock.consumption", rec.id)
    assert inv.qty(inv.part, inv.central) == 10.0


def test_return_needs_a_known_reason(inv):
    from odoo.exceptions import UserError

    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    with pytest.raises(UserError, match="return reason"), inv.env.cr.savepoint():
        rec.with_user(inv.keeper).action_return_part("because")


def test_stock_type_dimension_on_typed_locations(inv):
    """E1 (warehouse-with-location report 2026-11-09): the legacy estate's six
    stock classes are a location dimension of their own — a structural hub
    carries none, a typed child under it carries exactly one, and the legacy
    'Returnable Damage' class is representable."""
    assert inv.hub.stock_type is False, "a structural hub carries no stock class"
    child = inv.env["fix.stock.location"].create(
        {
            "name": "A06 Warranty Bay",
            "code": "A6W-" + inv.tag,
            "location_type": "branch",
            "stock_type": "warranty",
            "parent_id": inv.hub.id,
            "operating_unit_id": inv.ou.id,
        }
    )
    assert child.stock_type == "warranty"
    selection = dict(
        child.fields_get(["stock_type"], attributes=["selection"])["stock_type"]["selection"]
    )
    assert selection["returnable_damage"] == "Returnable Damage"
    assert selection["non_warranty"] == "Non-Warranty"
