# A06 build - the cross-builder contracts B1 provides on the M15 ledger, and
# the S0 valuation-suspense integrity check. Other builders (M43 demand
# planning, M44 landed cost, M16 receipts) code against these signatures.
import pytest
from odoo.exceptions import AccessError, UserError

REFUSED = (UserError, AccessError)


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


# ------------------------------------------------------------- _apply (WAC)
def test_apply_values_receipts_at_weighted_average(inv):
    Onhand = inv.env["fix.stock.onhand"]
    row = Onhand._apply(inv.part, inv.central, "owned", 10.0, 100.0)
    assert (row.qty, row.unit_cost) == (20.0, 300.0)
    row = Onhand._apply(inv.part, inv.central, "owned", 5.0)  # no cost given: cost kept
    assert (row.qty, row.unit_cost) == (25.0, 300.0)
    row = Onhand._apply(inv.part, inv.central, "owned", -5.0)  # outflow at average
    assert (row.qty, row.unit_cost) == (20.0, 300.0)
    assert inv.part.qty_available == 20.0 and inv.part.average_cost == 300.0
    assert not Onhand._apply(inv.part, inv.hub, "owned", -1.0, must_exist=False)
    refused(inv, lambda: Onhand._apply(inv.part, inv.hub, "owned", -1.0), "No unrestricted")


# ------------------------------------------------------- reserve / unreserve
def test_fix_reserve_refuses_more_than_available(inv):
    Onhand = inv.env["fix.stock.onhand"]
    row = Onhand._fix_reserve(inv.part, inv.central, "owned", 6.0, "WAVE/1")
    assert (row.reserved, row.available_qty) == (6.0, 4.0)
    refused(
        inv, lambda: Onhand._fix_reserve(inv.part, inv.central, "owned", 5.0, "WAVE/2"), "only 4"
    )
    refused(inv, lambda: Onhand._fix_reserve(inv.part, inv.hub, "owned", 1.0, "WAVE/3"), "only 0")
    Onhand._fix_unreserve(inv.part, inv.central, "owned", 2.0, "WAVE/1")
    assert inv.bucket(inv.part, inv.central).reserved == 4.0
    refused(
        inv, lambda: Onhand._fix_unreserve(inv.part, inv.central, "owned", 5.0, "WAVE/1"), "only 4"
    )
    # reserved stock is not issued to another job
    rec = inv.issue(inv.keeper, qty=7.0)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "Insufficient")


def test_fix_reserve_takes_unrestricted_stock_only(inv):
    inv.quarantine(inv.keeper, qty=8.0)
    Onhand = inv.env["fix.stock.onhand"]
    refused(inv, lambda: Onhand._fix_reserve(inv.part, inv.central, "owned", 3.0, "X"), "only 2")


# ----------------------------------------------------------------- revalue
def test_fix_revalue_moves_value_not_quantity(inv):
    Onhand = inv.env["fix.stock.onhand"]
    row = Onhand._fix_revalue(inv.part, inv.central, "owned", 1000.0, "LC/2026/1")
    assert (row.qty, row.unit_cost) == (10.0, 600.0)
    assert inv.part.average_cost == 600.0
    entry = inv.suspense("LC/2026/1", "revaluation")
    assert entry.total_valuation == 1000.0
    row = Onhand._fix_revalue(inv.part, inv.central, "owned", -2000.0, "LC/2026/2")
    assert row.unit_cost == 400.0
    refused(
        inv, lambda: Onhand._fix_revalue(inv.part, inv.central, "owned", -10000.0, "X"), "negative"
    )
    refused(inv, lambda: Onhand._fix_revalue(inv.part, inv.hub, "owned", 50.0, "X"), "no quantity")
    # an issue after the landed-cost revaluation leaves at the new average
    rec = inv.issue(inv.keeper)
    rec.with_user(inv.keeper).action_scan_and_consume()
    assert rec.unit_cost == 400.0


def test_fix_revalue_of_held_stock_books_nothing(inv):
    inv.stock(inv.part, inv.hub, 4.0, 100.0, cls="consignment")
    inv.env["fix.stock.onhand"]._fix_revalue(inv.part, inv.hub, "consignment", 40.0, "LC/HELD")
    assert inv.bucket(inv.part, inv.hub, "consignment").unit_cost == 110.0
    assert not inv.suspense("LC/HELD")


# ---------------------------------------------------- publish from a plan
def test_publish_from_plan_creates_then_updates_with_provenance(inv):
    inv.hub.branch_id = inv.branch()
    Rule = inv.env["fix.reorder.rule"].with_user(inv.keeper)
    rule = Rule._fix_publish_from_plan(inv.part, inv.hub, 4.0, 16.0, "DPLAN/2026/7")
    assert (rule.min_qty, rule.max_qty, rule.state) == (4.0, 16.0, "active")
    assert (rule.published_by_id, rule.plan_source_ref, rule.branch_id) == (
        inv.keeper,
        "DPLAN/2026/7",
        inv.branch(),
    )
    again = Rule._fix_publish_from_plan(inv.part, inv.hub, 6.0, 30.0, "DPLAN/2026/8")
    assert again == rule and (rule.min_qty, rule.max_qty, rule.plan_source_ref) == (
        6.0,
        30.0,
        "DPLAN/2026/8",
    )
    refused(
        inv,
        lambda: Rule._fix_publish_from_plan(inv.part, inv.hub, 10.0, 10.0, "BAD"),
        "must exceed",
    )
    # the provenance is evidence: a user cannot retype it
    refused(
        inv, lambda: rule.with_user(inv.keeper).write({"plan_source_ref": "forged"}), "workflow"
    )


def test_publish_from_plan_finds_the_branch_of_the_operating_unit(inv):
    branch = inv.branch()
    rule = inv.env["fix.reorder.rule"]._fix_publish_from_plan(
        inv.part, inv.central, 1.0, 5.0, "DPLAN/OU"
    )
    assert rule.branch_id.operating_unit_id == branch.operating_unit_id


# --------------------------------------------- S0: valuation suspense integrity
def _baseline(inv, part, qty, cost, name):
    return inv.env["fix.inventory.valuation.suspense"].create(
        {
            "product_id": part.id,
            "quantity": qty,
            "unit_cost": cost,
            "entry_type": "initial_count",
            "name": name,
        }
    )


def test_s0_duplicate_baseline_is_reported_and_left_untouched(inv):
    Suspense = inv.env["fix.inventory.valuation.suspense"]
    before = Suspense.get_baseline_integrity()["companies"][0]
    first = _baseline(inv, inv.part, 10.0, 500.0, "VAL-INIT-A6-" + inv.tag)
    twin = _baseline(inv, inv.part, 10.0, 500.0, "VAL-INIT-A6-" + inv.tag)  # loaded twice
    _baseline(inv, inv.spart, 2.0, 8000.0, "VAL-INIT-A6S-" + inv.tag)
    after = Suspense.get_baseline_integrity()["companies"][0]
    assert after["duplicate_groups"] == before["duplicate_groups"] + 1
    assert after["duplicate_extra_rows"] == before["duplicate_extra_rows"] + 1
    assert after["duplicate_excess_value"] == pytest.approx(
        before["duplicate_excess_value"] + 5000.0
    )
    assert after["baseline_total"] == pytest.approx(before["baseline_total"] + 5000.0 * 2 + 16000.0)
    assert after["baseline_duplicated"] is True
    # read-only: nothing deleted, nothing reconciled
    assert (first.exists(), twin.exists()) == (first, twin)
    assert {first.status, twin.status} == {"pending_gl_cutover"}


def test_s0_integrity_compares_with_on_hand(inv):
    Suspense = inv.env["fix.inventory.valuation.suspense"]
    company = inv.env.company
    report = Suspense.get_baseline_integrity([company.id])["companies"][0]
    onhand = sum(
        b.qty * b.unit_cost
        for b in inv.env["fix.stock.onhand"].search(
            [
                ("company_id", "=", company.id),
                ("ownership_class", "in", ("owned", "van", "bench", "warranty")),
            ]
        )
    )
    assert report["onhand_value"] == pytest.approx(round(onhand, 2))
    assert report["gap_vs_onhand"] == pytest.approx(
        report["implied_stock_value"] - report["onhand_value"]
    )


def test_s0_integrity_report_pack_reads_as_the_caller(inv):
    from odoo.addons.cd_p03_portal.controllers.a06 import m15

    _baseline(inv, inv.part, 1.0, 500.0, "VAL-DUP-" + inv.tag)
    _baseline(inv, inv.part, 1.0, 500.0, "VAL-DUP-" + inv.tag)
    pack = m15.suspense_integrity(inv.env(user=inv.keeper.id))
    assert pack["rows"] and pack["rows"][0]["status"] == "Baseline loaded more than once"
    assert "suspense_integrity" in m15.REPORTS


def test_s0_suspense_reconciled_only_by_the_cutover(inv):
    entry = _baseline(inv, inv.part, 1.0, 500.0, "VAL-R-" + inv.tag)
    # trusted code (the M19 cutover runs it after proving the journal) may
    entry.action_reconcile_to_gl("JV/2026/0001")
    assert entry.status == "reconciled"
    other = _baseline(inv, inv.part, 1.0, 500.0, "VAL-R2-" + inv.tag)
    refused(
        inv,
        lambda: other.with_user(inv.controller).action_reconcile_to_gl("JV/2026/0001"),
        "cutover",
    )
    refused(inv, lambda: entry.with_user(inv.controller).write({"status": "pending_gl_cutover"}))
    assert other.status == "pending_gl_cutover"


def test_publish_from_plan_records_the_predicted_demand(inv):
    inv.hub.branch_id = inv.branch()
    Rule = inv.env["fix.reorder.rule"]
    rule = Rule._fix_publish_from_plan(
        inv.part, inv.hub, 4.0, 16.0, "DPLAN/PD", predicted_demand=21.0
    )
    assert rule.m43_predicted_demand == 21.0
    Rule._fix_publish_from_plan(inv.part, inv.hub, 4.0, 16.0, "DPLAN/PD2")  # old callers
    assert rule.m43_predicted_demand == 21.0 and rule.plan_source_ref == "DPLAN/PD2"
