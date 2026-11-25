# The two M49 capture gaps left by the 2026-11-17 audit, exercised on the live
# ORM as NON-ADMIN finance users and through the P03 endpoints the new forms
# post to (models/fix_asset_gaps.py):
#
#   page 3  fix.asset.component   FR-FXA-014: components of an asset brought
#                                 into service through the M19 seam
#   page 8  fix.asset.insurance   capability 20, BRU-FXA-25, AUT-FXA-20 and
#                                 the write-off claim link (FR-FXA-034)
from __future__ import annotations

from datetime import date

import pytest
from odoo.addons.cd_fixed_asset_ext.tests.test_a08_m49_controls import (
    _SEQ,
    _disposal,
    _post,
    _refused,
    balance,
    c,  # noqa: F401 - the fixture
    dep_run,
    p03,  # noqa: F401 - the fixture
    seam_asset,
)

pytestmark = [pytest.mark.financial]


def _draft_seam_asset(c, gross=100000.0, cat=None, purchase=date(2026, 1, 15)):  # noqa: F811
    """A registered asset whose M19 seam carries its cost, not yet in service."""
    cat = cat or c.cat
    move = _post(
        c,
        [(cat.asset_account_id, gross, 0.0, "acquisition"), (c.a["payable"], 0.0, gross, "AP")],
        when=purchase,
    )
    line = move.line_ids.filtered(lambda ln: ln.account_id == cat.asset_account_id)
    seam = c.cenv["fix.fixed.asset.seam"].create(
        {
            "operating_unit_id": c.ou.id,
            "name": "SEAM-G-%s" % next(_SEQ),
            "move_line_id": line.id,
            "amount": gross,
        }
    )
    return c.as_(c.acc1)["fix.fixed.asset"].create(
        {
            "name": "Branch fit-out",
            "category_id": cat.id,
            "gross": gross,
            "salvage": 0.0,
            "life_months": cat.useful_life_months,
            "purchase_date": purchase,
            "seam_id": seam.id,
            "operating_unit_id": c.ou.id,
        }
    )


def _electrical_category(c):  # noqa: F811
    """A category booking to its own asset account (a reclassification)."""
    account = c.cenv["account.account"].create(
        {
            "code": "A849E%s" % next(_SEQ),
            "name": "A08M49 Electrical installations",
            "account_type": "asset_fixed",
            "company_ids": [(6, 0, c.co.ids)],
        }
    )
    cat = c.cat.copy(
        {
            "code": "EL%s" % next(_SEQ),
            "name": "Electricals %s" % next(_SEQ),
            "asset_account_id": account.id,
            "useful_life_months": 60,
        }
    )
    return cat, account


# ------------------------------------------------------------------ page 3
def test_seam_asset_goes_into_service_as_its_components(c, p03):  # noqa: F811
    parent = _draft_seam_asset(c, gross=100000.0)
    elec, elec_account = _electrical_category(c)
    out = p03.write(
        c.acc1,
        model="fix.asset.component",
        values={
            "parent_asset_id": parent.id,
            "name": "Structure",
            "share_percent": 60.0,
            "life_months": 120,
        },
    )
    assert out.get("id") and "error" not in out, out
    C = c.as_(c.acc1)["fix.asset.component"]
    structure = C.browse(out["id"])
    _refused(C.create, {"parent_asset_id": parent.id, "name": "Wiring", "share_percent": 50.0})
    wiring = C.create(
        {
            "parent_asset_id": parent.id,
            "name": "Wiring",
            "share_percent": 40.0,
            "category_id": elec.id,
            "salvage_percent": 5.0,
        }
    )
    assert wiring.life_months == 60  # the component category's default life
    assert parent.asset_component_share_total == 100.0

    parent.with_user(c.acc1).action_activate()
    sibling = c.env["fix.fixed.asset"].search([("component_of_id", "=", parent.id)])
    assert len(sibling) == 1
    assert parent.state == "active" and sibling.state == "active"
    assert parent.gross == 60000.0 and parent.life_months == 120
    assert parent.name == "Branch fit-out - Structure"
    assert sibling.gross == 40000.0 and sibling.life_months == 60
    assert sibling.category_id == elec and sibling.salvage == 2000.0
    assert structure.asset_id == parent and wiring.asset_id == sibling
    assert parent.seam_id.consumed
    # the electrical share is reclassified to its own asset account
    assert wiring.reclass_move_id.state == "posted" and not structure.reclass_move_id
    assert balance(c, c.a["asset"]) == 60000.0 and balance(c, elec_account) == 40000.0
    # each depreciates over its own life
    dep_run(c, parent | sibling, 1)
    by_asset = {
        ln.asset_id: ln.amount
        for ln in (parent | sibling).depreciation_line_ids.filtered(lambda ln: ln.book == "book")
    }
    assert by_asset[parent] == 500.0 and by_asset[sibling] == 633.33
    # in service: the components are fixed
    _refused(wiring.with_user(c.acc1).write, {"share_percent": 10.0})
    _refused(wiring.with_user(c.acc1).unlink)
    _refused(C.create, {"parent_asset_id": parent.id, "name": "Late", "share_percent": 1.0})


def test_seam_components_must_total_100_and_required_componentisation(c):  # noqa: F811
    parent = _draft_seam_asset(c, gross=50000.0)
    half = c.as_(c.acc1)["fix.asset.component"].create(
        {"parent_asset_id": parent.id, "name": "Shell", "share_percent": 50.0}
    )
    _refused(parent.with_user(c.acc1).action_activate, match="100%")
    assert parent.state == "draft" and not parent.seam_id.consumed
    half.with_user(c.acc1).unlink()  # not in service: a wrong line is removed
    c.cat.with_user(c.mgr).write({"componentisation_required": True})
    _refused(parent.with_user(c.acc1).action_activate, match="components")
    assert parent.state == "draft" and not parent.seam_id.consumed
    # an asset already in service is not split
    c.cat.with_user(c.mgr).write({"componentisation_required": False})
    live = seam_asset(c, gross=30000.0)
    _refused(
        c.as_(c.acc1)["fix.asset.component"].create,
        {"parent_asset_id": live.id, "name": "Motor", "share_percent": 30.0},
        match="in service",
    )


# ------------------------------------------------------------------ page 8
def _insurer(c):  # noqa: F811
    return c.env["res.partner"].create({"name": "A08M49 insurer %s" % next(_SEQ)})


def test_insurance_cover_review_and_gap_report(c, p03):  # noqa: F811
    a1 = seam_asset(c, gross=120000.0)
    a2 = seam_asset(c, gross=80000.0, cat=c.cat_it, life=36)
    insurer = _insurer(c)
    out = p03.write(
        c.acc1,
        model="fix.asset.insurance",
        values={
            "name": "POL-ALL-1",
            "insurer_id": insurer.id,
            "cover_type": "all_risk",
            "scope": "assets",
            "asset_ids": [a1.id, a2.id],
            "sum_insured": 150000.0,
            "period_from": "2026-01-01",
            "period_to": "2026-12-31",
        },
    )
    assert out.get("id") and "error" not in out, out
    pol = c.as_(c.acc1)["fix.asset.insurance"].browse(out["id"])
    assert pol.reference.startswith("INS/") and pol.covered_count == 2
    assert pol.register_value == 200000.0 and pol.coverage_gap == 50000.0
    assert pol.coverage_gap_percent == 25.0 and pol.coverage_status == "under"
    # sums insured are not for billing or plain users (spec section 13)
    for outsider in (c.bill, c.plain):
        _refused(c.as_(outsider)["fix.asset.insurance"].search, [])
    # a typed state is refused; the accountant does not put it in force, nor
    # the manager who recorded it
    p03.write(c.acc1, model="fix.asset.insurance", record_id=pol.id, values={"state": "active"})
    pol.invalidate_recordset()
    assert pol.state == "draft"
    _refused(pol.with_user(c.acc1).action_activate, match="accounting manager")
    own = c.as_(c.mgr)["fix.asset.insurance"].create(
        {
            "name": "POL-OWN",
            "insurer_id": insurer.id,
            "asset_ids": [(6, 0, a1.ids)],
            "sum_insured": 1000.0,
            "period_from": date(2026, 1, 1),
            "period_to": date(2026, 12, 31),
        }
    )
    _refused(own.with_user(c.mgr).action_activate, match="segregation")
    p03.action(c.mgr, model="fix.asset.insurance", ids=[pol.id], method="action_activate")
    assert pol.state == "active" and pol.approved_by_id == c.mgr
    assert "POL-ALL-1" in a1.insured_under and "POL-OWN" not in a1.insured_under
    # in force: the cover is fixed
    _refused(pol.with_user(c.acc1).write, {"sum_insured": 999999.0})
    # a gap beyond the tolerance needs the note, then reaches the CFO
    _refused(pol.with_user(c.acc1).action_record_review, match="review note")
    pol.with_user(c.acc1).write({"review_note": "Values grew after the IT refresh; uplift asked"})
    pol.with_user(c.acc1).action_record_review()
    assert pol.reviewed_by_id == c.acc1 and pol.reviewed_register_value == 200000.0
    assert pol.reviewed_gap == 50000.0 and pol.gap_reported
    todo = pol.sudo().activity_ids.filtered(lambda a: "coverage gap" in (a.summary or ""))
    assert c.mgr in todo.mapped("user_id") and c.mgr2 in todo.mapped("user_id")
    _refused(pol.with_user(c.acc1).action_expire, match="in force until")

    # the renewal at the right value replaces it; its review is clean
    renewal = c.as_(c.acc1)["fix.asset.insurance"].create(
        {
            "name": "POL-ALL-2",
            "insurer_id": insurer.id,
            "asset_ids": [(6, 0, (a1 | a2).ids)],
            "sum_insured": 198000.0,
            "period_from": date(2026, 6, 1),
            "period_to": date(2027, 5, 31),
            "replaces_id": pol.id,
        }
    )
    renewal.with_user(c.mgr2).action_activate()
    assert pol.state == "replaced" and renewal.state == "active"
    assert renewal.coverage_status == "ok"
    renewal.with_user(c.acc1).action_record_review()
    assert not renewal.gap_reported and renewal.last_reviewed_on


def test_write_off_claims_under_a_policy_that_covers_the_asset(c):  # noqa: F811
    covered = seam_asset(c, gross=60000.0)
    other = seam_asset(c, gross=40000.0, cat=c.cat_it, life=36)
    insurer = _insurer(c)
    Pol = c.as_(c.acc1)["fix.asset.insurance"]
    by_class = Pol.create(
        {
            "name": "POL-TOOLS",
            "insurer_id": insurer.id,
            "scope": "category",
            "category_ids": [(6, 0, c.cat.ids)],
            "operating_unit_id": c.ou.id,
            "sum_insured": 60000.0,
            "period_from": date(2026, 1, 1),
            "period_to": date(2026, 12, 31),
        }
    )
    lapsed = Pol.create(
        {
            "name": "POL-2025",
            "insurer_id": insurer.id,
            "asset_ids": [(6, 0, covered.ids)],
            "sum_insured": 60000.0,
            "period_from": date(2025, 1, 1),
            "period_to": date(2025, 12, 31),
        }
    )
    (by_class | lapsed).with_user(c.mgr).action_activate()
    assert by_class.covered_count == 1 and by_class.coverage_status == "ok"
    write_off = {
        "kind": "write_off",
        "proceeds": 0.0,
        "partner_id": False,
        "incident_ref": "GD-2026-114",
        "reason": "Stolen from the branch store",
    }
    claim = _disposal(c, covered, insurance_id=by_class.id, **write_off)
    assert claim.insurance_id == by_class
    _refused(_disposal, c, other, insurance_id=by_class.id, match="does not cover", **write_off)
    _refused(_disposal, c, covered, insurance_id=lapsed.id, match="outside", **write_off)
