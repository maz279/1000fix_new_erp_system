# M49 capture audit 2026-11-17 — the records the sub-module pages had no
# capture for, exercised on the live ORM as NON-ADMIN finance users (the
# accountant raises, a different accounting manager decides), and through the
# P03 workspace endpoints the new forms post to.
#
#   page 1  fix.capital.project             FR-FXA-006/007, BRU-FXA-24
#   page 3  fix.cwip.component              FR-FXA-014/016
#   page 4  fix.asset.depreciation.change   FR-FXA-023/024, BRU-FXA-10
#   page 5  fix.asset.impairment.assessment FR-FXA-032, BRU-FXA-26
#   page 7  fix.asset.verification.variance FR-FXA-030, BRU-FXA-15/16
from __future__ import annotations

from datetime import date

import pytest
from odoo.addons.cd_fixed_asset_ext.tests.test_a08_m49_controls import (
    _confirm_tax_rate,
    _refused,
    approved_capex,
    balance,
    budget,
    c,  # noqa: F401 - the fixture
    cwip_with_cost,
    dep_run,
    p03,  # noqa: F401 - the fixture
    request,
    seam_asset,
)

pytestmark = [pytest.mark.financial]


def _set_param(c, key, value):  # noqa: F811
    c.env["ir.config_parameter"].sudo().set_param("cd_fixed_asset_ext.%s" % key, value)


# ------------------------------------------------------------------ page 1
def test_capital_project_budget_completion_and_review(c, p03):  # noqa: F811
    _set_param(c, "capital_project_review_threshold", "250000")
    out = p03.write(
        c.mgr,
        model="fix.capital.project",
        values={
            "name": "Sylhet branch opening",
            "kind": "branch_opening",
            "owner_id": c.mgr.id,
            "total_budget": 300000.0,
            "operating_unit_id": c.ou.id,
        },
    )
    assert out.get("id") and "error" not in out, out
    pj = c.env["fix.capital.project"].search([("name", "=", "Sylhet branch opening")])
    assert pj.reference.startswith("CPJ/") and pj.review_required
    # the owner and raiser does not approve it; a typed state is refused
    _refused(pj.with_user(c.mgr).action_approve, match="segregation")
    p03.write(c.mgr, model="fix.capital.project", record_id=pj.id, values={"state": "active"})
    pj.invalidate_recordset()
    assert pj.state == "draft"
    pj.with_user(c.mgr2).action_approve()
    assert pj.state == "active" and pj.approved_by_id == c.mgr2
    # approved: the budget is fixed
    _refused(pj.with_user(c.mgr).write, {"total_budget": 900000.0})

    b = budget(c, amount=2000000.0, by=c.mgr, approve_by=c.mgr2)
    r1 = request(c, b, amount=200000.0, project_id=pj.id)
    r1.with_user(c.acc1).action_submit()
    r2 = request(c, b, amount=150000.0, project_id=pj.id)
    _refused(r2.with_user(c.acc1).action_submit, match="over its budget")
    assert r2.state == "draft"

    # completion waits for the requests in approval, then the review is due
    _refused(pj.with_user(c.acc1).action_complete, match="awaiting approval")
    r1.with_user(c.mgr2).action_reject()
    pj.with_user(c.acc1).action_complete()
    assert pj.state == "completed" and pj.review_due_date
    assert (pj.review_due_date - pj.actual_completion).days == 180
    # the review needs its content and is never the owner's
    _refused(pj.with_user(c.acc1).action_record_review, match="realised benefit")
    pj.with_user(c.acc1).write(
        {"benefit_assessment": "Branch opened two weeks late", "review_conclusion": "partial"}
    )
    _refused(pj.with_user(c.mgr).action_record_review, match="owner")
    pj.with_user(c.acc1).action_record_review()
    assert pj.state == "reviewed" and pj.reviewed_by_id == c.acc1
    assert pj.review_variance == -300000.0  # nothing approved was spent


# ------------------------------------------------------------------ page 3
def test_cwip_components_capitalise_as_separate_assets(c, p03):  # noqa: F811
    _b, r = approved_capex(c, 120000.0)
    cw = cwip_with_cost(c, r, 120000.0)
    out = p03.write(
        c.acc1,
        model="fix.cwip.component",
        values={"cwip_id": cw.id, "name": "Building", "share_percent": 70.0, "life_months": 120},
    )
    assert out.get("id") and "error" not in out, out
    C = c.as_(c.acc1)["fix.cwip.component"]
    _refused(C.create, {"cwip_id": cw.id, "name": "Fit-out", "share_percent": 40.0})
    fit = C.create(
        {"cwip_id": cw.id, "name": "Fit-out", "share_percent": 30.0, "category_id": c.cat_it.id}
    )
    assert fit.life_months == 36  # the component category's default life
    assets = cw.with_user(c.acc1).action_capitalise()
    assert len(assets) == 2
    by_life = {a.life_months: a for a in assets}
    assert by_life[120].gross == 84000.0 and by_life[36].gross == 36000.0
    assert by_life[36].category_id == c.cat_it and by_life[36].cwip_component_id == fit
    assert all(a.state == "active" for a in assets) and fit.asset_id == by_life[36]
    assert balance(c, c.a["asset"]) == 120000.0 and balance(c, c.a["cwip"]) == 0.0
    # capitalised: the components are fixed
    _refused(fit.with_user(c.acc1).write, {"share_percent": 10.0})
    _refused(fit.with_user(c.acc1).unlink)


def test_shares_not_100_and_required_componentisation_refused(c):  # noqa: F811
    _b, r = approved_capex(c, 90000.0)
    cw = cwip_with_cost(c, r, 90000.0)
    comp = c.as_(c.acc1)["fix.cwip.component"].create(
        {"cwip_id": cw.id, "name": "Shell", "share_percent": 60.0}
    )
    _refused(cw.with_user(c.acc1).action_capitalise, match="100%")
    comp.with_user(c.acc1).unlink()  # open project: a wrong line is removed
    c.cat.with_user(c.mgr).write({"componentisation_required": True})
    _refused(cw.with_user(c.acc1).action_capitalise, match="components")
    assert cw.state == "open"


# ------------------------------------------------------------------ page 4
def _change(c, a, by=None, **vals):  # noqa: F811
    return c.as_(by or c.acc1)["fix.asset.depreciation.change"].create(
        dict({"asset_id": a.id, "reason": "Engineering review of the bench"}, **vals)
    )


def test_life_change_is_approved_by_another_and_prospective(c, p03):  # noqa: F811
    a = seam_asset(c, gross=120000.0, purchase=date(2026, 1, 15), life=12)
    dep_run(c, a, 1)
    dep_run(c, a, 2)
    assert a.book_months_done == 2
    # a life that does not exceed the months already charged is refused
    early = _change(c, a, new_life_months=2)
    _refused(early.with_user(c.acc1).action_submit, match="prospectively")
    out = p03.write(
        c.acc1,
        model="fix.asset.depreciation.change",
        values={"asset_id": a.id, "kind": "life", "new_life_months": 22, "reason": "Re-rated"},
    )
    assert out.get("id") and "error" not in out, out
    ch = c.env["fix.asset.depreciation.change"].search([("asset_id", "=", a.id)], limit=1)
    assert ch.new_salvage == a.salvage  # untouched residual carried over
    ch.with_user(c.acc1).action_submit()
    _refused(ch.with_user(c.acc2).action_approve, match="manager")
    # a manager who raised a change does not approve it
    own = _change(c, a, by=c.mgr, new_life_months=30)
    own.with_user(c.mgr).action_submit()
    _refused(own.with_user(c.mgr).action_approve, match="segregation")
    p03.action(c.mgr, model="fix.asset.depreciation.change", ids=[ch.id], method="action_approve")
    ch.invalidate_recordset()
    assert ch.state == "approved" and ch.approved_by_id == c.mgr
    assert ch.applied_from == date(2026, 3, 1) and ch.previous_life_months == 12
    assert a.life_months == 22
    run = dep_run(c, a, 3)
    # (120,000 - 20,000 charged) over the 20 months left
    assert run.line_ids.amount == 5000.0
    posted = a.depreciation_line_ids.filtered(lambda ln: ln.period_start < date(2026, 3, 1))
    assert sorted(posted.mapped("amount")) == [10000.0, 10000.0]
    # a submitted change is frozen
    _refused(own.with_user(c.mgr).write, {"new_life_months": 40})


def test_suspension_stops_the_book_charge_not_the_tax_book(c):  # noqa: F811
    a = seam_asset(c, gross=120000.0, purchase=date(2026, 1, 15), life=12)
    dep_run(c, a, 1)
    s = _change(c, a, kind="suspend", reason="Bench idle: branch closed for refit")
    s.with_user(c.acc1).action_submit()
    s.with_user(c.mgr).action_approve()
    assert a.depreciation_suspended
    run = dep_run(c, a, 2, post=False)
    assert not run.line_ids
    _refused(a.with_user(c.acc1).action_accrue_month, match="suspended")
    _confirm_tax_rate(c, "ITA3-PLANT")
    tax = dep_run(c, a, 2, book="tax", post=False)
    assert tax.line_ids.amount > 0  # the tax book is independent (BRU-FXA-12)
    # a second suspension is refused; reinstate resumes the remaining life
    _refused(_change(c, a, kind="suspend").with_user(c.acc1).action_submit, match="already")
    back = _change(c, a, kind="reinstate", reason="Branch reopened")
    back.with_user(c.acc1).action_submit()
    back.with_user(c.mgr2).action_approve()
    assert not a.depreciation_suspended
    run = dep_run(c, a, 2, post=False)
    assert run.line_ids.amount == 10000.0  # 110,000 over the 11 months left


# ------------------------------------------------------------------ page 5
def _assessment(c, a, by=None, **vals):  # noqa: F811
    return c.as_(by or c.acc1)["fix.asset.impairment.assessment"].create(
        dict({"scope": "asset", "asset_id": a.id, "assessment_date": date(2026, 6, 30)}, **vals)
    )


def test_impairment_assessment_recorded_with_or_without_a_loss(c, p03):  # noqa: F811
    a = seam_asset(c, gross=120000.0, purchase=date(2026, 1, 15), life=12)
    dep_run(c, a, 1)
    assert a.book_nbv == 110000.0
    # an indicator means a test: "no indicator" with one ticked is refused
    _refused(_assessment, c, a, ind_idle=True)
    out = p03.write(
        c.acc1,
        model="fix.asset.impairment.assessment",
        values={
            "scope": "asset",
            "asset_id": a.id,
            "assessment_date": "2026-06-30",
            "trigger": "annual",
            "conclusion": "no_indicator",
        },
    )
    assert out.get("id") and "error" not in out, out
    none = c.env["fix.asset.impairment.assessment"].search([("asset_id", "=", a.id)], limit=1)
    assert none.operating_unit_id == c.ou  # the asset's branch
    _refused(none.with_user(c.acc1).action_confirm, match="manager")
    none.with_user(c.mgr).action_confirm()
    assert none.state == "confirmed" and none.carrying_amount == 110000.0
    assert not none.revaluation_id
    # a tested conclusion must agree with the carrying amount
    wrong = _assessment(
        c,
        a,
        ind_damage=True,
        indicator_note="Water damage in the store room",
        conclusion="no_impairment",
        recoverable_amount=90000.0,
        basis="Valuer quote",
    )
    _refused(wrong.with_user(c.mgr).action_confirm, match="below the carrying")
    loss = _assessment(
        c,
        a,
        ind_damage=True,
        indicator_note="Water damage in the store room",
        conclusion="impaired",
        recoverable_amount=80000.0,
        basis="Valuer quote, FVLCD",
    )
    own = _assessment(c, a, by=c.mgr)
    _refused(own.with_user(c.mgr).action_confirm, match="segregation")
    loss.with_user(c.mgr).action_confirm()
    rv = loss.revaluation_id
    assert loss.impairment_loss == 30000.0
    assert rv.kind == "impairment" and rv.new_value == 80000.0 and rv.state == "draft"
    _refused(loss.with_user(c.acc1).write, {"recoverable_amount": 1.0})


# ------------------------------------------------------------------ page 7
def _counted(c):  # noqa: F811
    """A campaign counted by c.mgr at branch ou: asset 1 found at ou2
    (misplaced), asset 2 never scanned (missing)."""
    a1 = seam_asset(c, gross=50000.0, name="Bench A")
    a2 = seam_asset(c, gross=60000.0, name="Bench B")
    camp = c.as_(c.acc1)["fix.asset.verification.campaign"].create(
        {
            "name": "FY27 count",
            "date": date(2026, 11, 1),
            "operating_unit_id": c.ou.id,
            "responsible_id": c.mgr.id,
        }
    )
    camp.with_user(c.acc1).action_start()
    camp.with_user(c.acc1).action_record_scan(tag=a1.code, branch=c.ou2.code)
    camp.with_user(c.acc1).action_close()
    lines = {ln.asset_id: ln for ln in camp.line_ids}
    assert lines[a1].result == "misplaced" and lines[a2].result == "missing"
    return a1, a2, lines[a1], lines[a2]


def test_variance_write_off_is_decided_by_neither_counter_nor_proposer(c, p03):  # noqa: F811
    _a1, a2, _l1, missing = _counted(c)
    out = p03.write(
        c.acc1,
        model="fix.asset.verification.variance",
        values={
            "line_id": missing.id,
            "explanation": "Not in the store; the guard log shows it left on 12 Oct",
            "proposed_action": "write_off",
        },
    )
    assert out.get("id") and "error" not in out, out
    v = c.env["fix.asset.verification.variance"].search([("line_id", "=", missing.id)])
    assert v.variance_type == "missing" and v.asset_id == a2
    assert "FY27 count" in missing.display_name
    _refused(v.with_user(c.acc1).action_propose, match="incident")
    v.with_user(c.acc1).write({"incident_ref": "GD-1123/26"})
    v.with_user(c.acc1).action_propose()
    # one investigation per result
    _refused(
        c.as_(c.acc2)["fix.asset.verification.variance"].create,
        {"line_id": missing.id, "explanation": "x", "proposed_action": "explained"},
    )
    _refused(v.with_user(c.mgr).action_approve, match="counter")
    v.with_user(c.mgr2).action_approve()
    d = v.disposal_id
    assert v.state == "approved" and d.kind == "write_off" and d.state == "draft"
    assert d.incident_ref == "GD-1123/26" and d.asset_id == a2


def test_variance_transfer_and_located_corrections(c):  # noqa: F811
    a1, _a2, misplaced, missing = _counted(c)
    V = c.as_(c.acc1)["fix.asset.verification.variance"]
    wrong = V.create({"line_id": misplaced.id, "explanation": "x", "proposed_action": "write_off"})
    _refused(wrong.with_user(c.acc1).action_propose, match="corrected by")
    wrong.with_user(c.acc1).write({"proposed_action": "transfer", "explanation": "Moved in July"})
    wrong.with_user(c.acc1).action_propose()
    wrong.with_user(c.mgr2).action_approve()
    t = wrong.transfer_id
    assert t.asset_id == a1 and t.operating_unit_id == c.ou2 and t.state == "draft"
    # located: the result is corrected by the approver, never the counter
    found = V.create(
        {"line_id": missing.id, "explanation": "In the van", "proposed_action": "located"}
    )
    found.with_user(c.acc1).action_propose()
    # the proposer does not approve
    mine = c.as_(c.mgr2)["fix.asset.verification.variance"]
    _refused(found.with_user(c.acc1).action_approve, match="manager")
    found.with_user(c.mgr2).action_approve()
    assert missing.result == "found" and missing.corrected_by_id == c.mgr2
    # a found result is not a variance
    _refused(mine.create, {"line_id": missing.id, "explanation": "x"})
    # a manager who proposed is not the approver of his own proposal
    _a, _b, _m, other = _counted(c)
    own = mine.create({"line_id": other.id, "explanation": "Sold", "proposed_action": "explained"})
    own.with_user(c.mgr2).action_propose()
    _refused(own.with_user(c.mgr2).action_approve, match="segregation")
