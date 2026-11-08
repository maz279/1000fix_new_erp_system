"""A06 M43 controls: every gap probe of working/A06_evidence/probes/m43 re-run
as the attack it was, now refused (or now computing the right figure), plus
the proper paths: a planner forecasts from M15 history, an approver who did
not prepare a plan approves it, and the released requisition lands in M16 as
a draft submitted into M16's own approval.

Test names follow the probe ids (test_m43_NN_...)."""

from __future__ import annotations

import contextlib
from datetime import date, datetime, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

PLANNER = "cd_demand_plan.group_fix_demand_planner"
APPROVER = "cd_demand_plan.group_fix_demand_approver"

REFUSED = (UserError, ValidationError, AccessError, IntegrityError)


def _approve(m43, plan):
    plan.with_user(m43.approver).action_approve()
    return plan


def _release(m43, plan):
    _approve(m43, plan)
    plan.with_user(m43.planner).action_generate_pr()
    return plan.sudo().pr_requisition_id


# ===================================================================== roles
def test_m43_roles_shipped(m43):
    env = m43.env
    planner = env.ref(PLANNER)
    approver = env.ref(APPROVER)
    assert env.ref("base.user_admin") in planner.user_ids
    assert env.ref("base.user_admin") not in approver.user_ids, "approvers ship empty"
    assert env.ref("base.group_user") in planner.implied_ids
    for key in (
        "cd_demand_plan.forecast_window_months",
        "cd_demand_plan.forecast_min_history_months",
        "cd_demand_plan.policy_history_days",
        "cd_demand_plan.review_period_days",
    ):
        assert env["ir.config_parameter"].sudo().get_param(key), key


def test_m43_plain_user_reads_but_cannot_create(m43):
    m43.plan(user=m43.planner)
    assert m43.env["fix.demand.plan"].with_user(m43.clerk).search_count([]) >= 1
    with pytest.raises(AccessError), m43.env.cr.savepoint():
        m43.plan(user=m43.clerk)
    with pytest.raises(AccessError), m43.env.cr.savepoint():
        m43.env["fix.demand.forecast"].with_user(m43.clerk).create(
            {"product_id": m43.prod.id, "period": m43.period}
        )


# ===================================================================== reference / proper path
def test_m43_00_proper_path_plan_to_submitted_requisition(m43):
    """Planner prepares, a different approver approves, the planner releases:
    the requisition is a DRAFT submitted into M16, never born approved."""
    plan = m43.ready_plan(forecast=10, stock=5, avg=2, std=0, lead=10)
    assert plan.recommended_order == pytest.approx(85.0)
    req = _release(m43, plan)
    assert req, "the plan raised a requisition"
    assert plan.state == "released"
    assert req.state == "submitted", req.state  # M16's own approval decides it
    assert req.qty == pytest.approx(85.0)
    assert req.estimate_amount == pytest.approx(85_000.0)
    assert req.demand_plan_id == plan
    assert req.requested_by.user_id == m43.planner
    assert plan.approved_by_id == m43.approver


def test_m43_00b_m16_approval_then_applies(m43):
    """The released requisition is decided by M16, not by the planner who
    raised it nor by a plain clerk."""
    req = _release(m43, m43.ready_plan(forecast=10, stock=5, avg=2, std=0, lead=10))
    for user in (m43.clerk, m43.planner):
        with pytest.raises(REFUSED), m43.env.cr.savepoint():
            req.with_user(user).action_approve()
    req.invalidate_recordset()
    assert req.state not in ("approved", "converted")


# ===================================================================== plan figures computed
def test_m43_01_plan_forecast_from_forecast_cycle(m43):
    m43.policy(2, 0, 10)
    m43.forecast(40)
    plan = m43.plan()
    assert plan.forecast_quantity == pytest.approx(40.0)
    assert plan.forecast_months_covered == m43.period
    # a draft (unapproved) forecast does not count
    m43.forecast(999, period=m43.last_period, state="draft")
    assert plan.forecast_quantity == pytest.approx(40.0)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        m43.plan(forecast_quantity=1_000_000, name="typed")


def test_m43_01b_plan_without_forecast_for_every_month_not_approved(m43):
    m43.policy(2, 0, 10)
    m43.stock(1)
    plan = m43.plan()
    with pytest.raises(UserError, match="no approved forecast"), m43.env.cr.savepoint():
        plan.with_user(m43.approver).action_approve()


def test_m43_02_current_stock_from_m15_owned_onhand(m43):
    m43.stock(37)
    m43.stock(500, ownership="consignment")  # not ours to plan on
    m43.stock(11, loc=m43.loc2)  # another location
    plan = m43.plan()
    assert plan.current_stock == pytest.approx(37.0)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        plan.with_user(m43.planner).write({"current_stock": 0})


def test_m43_03_below_rop_orders_up_to_target(m43):
    """Finding E03: forecast 10, stock 5, ROP 20 recommended 0. Now: projected
    5 - 10 = -5 <= ROP 20 -> order up to target 80 (ROP 20 + 2/day x 30): 85."""
    plan = m43.ready_plan(forecast=10, stock=5, avg=2, std=0, lead=10, review=30)
    assert plan.reorder_point == pytest.approx(20.0)
    assert plan.target_level == pytest.approx(80.0)
    assert plan.projected_stock == pytest.approx(-5.0)
    assert plan.recommended_order == pytest.approx(85.0)
    assert plan.projected_stock + plan.recommended_order == pytest.approx(plan.target_level)


def test_m43_04_order_restores_target_not_zero(m43):
    """Finding E04: forecast 100, stock 0, ROP 50 recommended 100 (ending at 0).
    Now: ROP 50 (5/day x 10), target 200, projected -100 -> order 300."""
    plan = m43.ready_plan(forecast=100, stock=0, avg=5, std=0, lead=10, review=30)
    assert plan.reorder_point == pytest.approx(50.0)
    assert plan.recommended_order == pytest.approx(300.0)
    assert plan.recommended_order >= 150
    assert plan.projected_stock + plan.recommended_order == pytest.approx(200.0)


def test_m43_04b_above_rop_no_order_and_net_of_on_order(m43):
    plan = m43.ready_plan(forecast=10, stock=100, avg=2, std=0, lead=10)
    assert plan.projected_stock == pytest.approx(90.0)
    assert plan.recommended_order == 0.0
    # stock on order is netted: an open requisition of 30 for the product
    low = m43.plan(name="low", location_id=m43.loc2.id)
    m43.policy(2, 0, 10, loc=m43.loc2)
    m43.forecast(10, loc=m43.loc2, product_id=m43.prod.id, part_id=m43.part.id, period=m43.period)
    m43.env["fix.requisition"].create(
        {
            "description": "open M16 requisition",
            "product_id": m43.prod.id,
            "qty": 30,
            "estimate_amount": 30_000,
            "requested_by": m43.tech.id,
            "operating_unit_id": m43.ou.id,
        }
    )
    low.invalidate_recordset()
    assert low.on_order_qty == pytest.approx(30.0)
    # projected 0 + 30 - 10 = 20 <= ROP 20 -> up to target 80: 60
    assert low.recommended_order == pytest.approx(60.0)


def test_m43_05_recommended_order_not_writable(m43):
    plan = m43.ready_plan()
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        plan.with_user(m43.planner).write({"recommended_order": 99_999})
    assert plan.recommended_order == pytest.approx(85.0)


# ===================================================================== plan approval
def test_m43_06_plan_approval_role_and_sod(m43):
    plan = m43.ready_plan()
    for user in (m43.clerk, m43.planner, m43.planner2):
        with pytest.raises(REFUSED), m43.env.cr.savepoint():
            plan.with_user(user).action_approve()
    # an approver who prepared (changed) the plan cannot approve it either
    m43.env.ref(PLANNER).sudo().write({"user_ids": [(4, m43.approver2.id)]})
    plan.with_user(m43.approver2).write({"name": "renamed"})  # name is not an input
    plan.with_user(m43.approver2).write({"location_id": m43.loc2.id})
    plan.with_user(m43.approver2).write({"location_id": m43.loc.id})
    assert plan.prepared_by_id == m43.approver2
    with pytest.raises(UserError, match="segregation"), m43.env.cr.savepoint():
        plan.with_user(m43.approver2).action_approve()
    plan.with_user(m43.approver).action_approve()
    assert plan.state == "approved" and plan.approved_by_id == m43.approver


def test_m43_07_plan_state_forged_by_write(m43):
    plan = m43.ready_plan()
    for user in (m43.planner, m43.approver):
        with pytest.raises(REFUSED), m43.env.cr.savepoint():
            plan.with_user(user).write({"state": "approved"})
    ev = m43.env["fix.event.outbox"].search_count(
        [("event_type", "=", "demand_plan.approved"), ("aggregate_id", "=", plan.id)]
    )
    assert plan.state == "draft" and ev == 0


def test_m43_08_plan_state_forged_via_p03(m43, p03):
    plan = m43.ready_plan()
    p03.as_user(m43.planner)
    out = p03.write(model="fix.demand.plan", record_id=plan.id, values={"state": "approved"})
    plan.invalidate_recordset()
    assert "error" in out and plan.state == "draft"


def test_m43_09_refused_plan_cannot_be_forced(m43):
    plan = m43.ready_plan(forecast=5, stock=50)
    with pytest.raises(UserError, match="Nothing to replenish"), m43.env.cr.savepoint():
        plan.with_user(m43.approver).action_approve()
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        plan.with_user(m43.planner).write({"state": "approved", "forecast_quantity": 5000})
    with pytest.raises(UserError), m43.env.cr.savepoint():
        plan.with_user(m43.planner).action_generate_pr()
    assert not plan.sudo().pr_requisition_id


def test_m43_10_approval_pinned_and_voided_on_change(m43):
    plan = _approve(m43, m43.ready_plan())
    assert plan.approved_order_qty == pytest.approx(85.0)
    # live stock moves after approval: the approved quantity does not
    m43.env["fix.stock.onhand"].search(
        [("part_id", "=", m43.part.id), ("location_id", "=", m43.loc.id)]
    ).write({"qty": 0})
    plan.invalidate_recordset()
    assert plan.recommended_order == pytest.approx(90.0)
    assert plan.approved_order_qty == pytest.approx(85.0)
    # an input change by another planner voids the approval
    plan.with_user(m43.planner2).write({"location_id": m43.loc2.id})
    assert plan.state == "draft" and not plan.approved_by_id and plan.approved_order_qty == 0
    with pytest.raises(UserError, match="Approve the plan"), m43.env.cr.savepoint():
        plan.with_user(m43.planner2).action_generate_pr()
    # back to the reviewed location, re-approved, released at the pinned figure
    plan.with_user(m43.planner2).write({"location_id": m43.loc.id})
    plan.with_user(m43.approver).action_approve()
    plan.with_user(m43.planner).action_generate_pr()
    assert plan.sudo().pr_requisition_id.qty == pytest.approx(plan.approved_order_qty)
    with pytest.raises(UserError, match="released"), m43.env.cr.savepoint():
        plan.with_user(m43.planner).write({"period_start": m43.this_month - timedelta(days=1)})


# ===================================================================== hand-off to M16
def test_m43_11_m16_threshold_control_reference(m43):
    emp = m43.env["hr.employee"].search([("user_id", "=", m43.clerk.id)], limit=1)
    req = (
        m43.env["fix.requisition"]
        .with_user(m43.clerk)
        .create(
            {
                "description": "A06M43 direct requisition",
                "requested_by": emp.id,
                "operating_unit_id": m43.ou.id,
                "estimate_amount": 1_000_000,
            }
        )
    )
    with pytest.raises(REFUSED):
        req.with_user(m43.clerk).action_approve()


def test_m43_12_generated_requisition_is_not_born_approved(m43):
    plan = m43.ready_plan(forecast=1000, stock=10, avg=2, std=0, lead=10)
    req = _release(m43, plan)
    assert req.state not in ("approved", "converted"), req.state
    assert req.estimate_amount > 25_000


def test_m43_13_no_po_from_unapproved_requisition(m43):
    plan = m43.ready_plan(forecast=1000, stock=10, avg=2, std=0, lead=10)
    req = _release(m43, plan).with_user(m43.planner)
    vendor = m43.env["res.partner"].create({"name": "M43 Vendor"})
    with contextlib.suppress(REFUSED):
        req.write({"vendor_id": vendor.id})
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        req.action_convert_to_po()
    assert not req.sudo().purchase_order_id


def test_m43_14_p03_actions_need_the_roles(m43, p03):
    plan = m43.ready_plan(forecast=1000, stock=10, avg=2, std=0, lead=10)
    p03.as_user(m43.clerk)
    a = p03.action(model="fix.demand.plan", ids=[plan.id], method="action_approve")
    b = p03.action(model="fix.demand.plan", ids=[plan.id], method="action_generate_pr")
    assert not a["success"] and not b["success"]
    p03.as_user(m43.planner)
    assert not p03.action(model="fix.demand.plan", ids=[plan.id], method="action_approve")[
        "success"
    ]
    p03.as_user(m43.approver)
    assert p03.action(model="fix.demand.plan", ids=[plan.id], method="action_approve")["success"]
    p03.as_user(m43.planner)
    out = p03.action(model="fix.demand.plan", ids=[plan.id], method="action_generate_pr")
    assert out["success"], out
    req = plan.sudo().pr_requisition_id
    assert req and req.state not in ("approved", "converted")


def test_m43_15_requester_is_the_releasing_planner(m43):
    m43.env["hr.employee"].create({"name": "AAAA Unrelated Storekeeper"})
    req = _release(m43, m43.ready_plan())
    assert req.requested_by.user_id == m43.planner
    # a releaser with no employee record is refused, never attributed to someone else
    orphan = m43.user("orphan", [PLANNER], employee=False)
    other = m43.env["product.template"].create({"name": "M43 other", "standard_price": 10.0})
    plan = m43.plan(name="second", location_id=m43.loc2.id, product_id=other.id)
    m43.policy(2, 0, 10, loc=m43.loc2)
    m43.forecast(10, loc=m43.loc2)
    plan.with_user(m43.approver).action_approve()
    with pytest.raises(UserError, match="employee"), m43.env.cr.savepoint():
        plan.with_user(orphan).action_generate_pr()


def test_m43_16_zero_value_requisition_refused(m43):
    m43.tmpl.standard_price = 0.0
    plan = _approve(m43, m43.ready_plan())
    with pytest.raises(UserError, match="no purchase price"), m43.env.cr.savepoint():
        plan.with_user(m43.planner).action_generate_pr()
    assert not plan.sudo().pr_requisition_id


def test_m43_16b_unsourced_plan_refused(m43):
    plan = m43.ready_plan()
    plan.with_user(m43.planner).write({"part_id": False})
    with pytest.raises(UserError, match="spare part"), m43.env.cr.savepoint():
        plan.with_user(m43.approver).action_approve()


def test_m43_17_one_pr_per_plan(m43):
    plan = m43.ready_plan()
    _release(m43, plan)
    with pytest.raises(UserError, match="already has a requisition"):
        plan.with_user(m43.planner).action_generate_pr()


def test_m43_18_pr_link_cannot_be_rearmed(m43):
    plan = m43.ready_plan()
    req = _release(m43, plan)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        plan.with_user(m43.planner).write({"pr_requisition_id": False})
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        req.with_user(m43.planner).write({"demand_plan_id": False})
    # even a forged second requisition for the same plan is refused by the DB
    with pytest.raises(IntegrityError), m43.env.cr.savepoint():
        m43.env["fix.requisition"].create(
            {
                "description": "second",
                "requested_by": m43.tech.id,
                "operating_unit_id": m43.ou.id,
                "demand_plan_id": plan.id,
            }
        )
        m43.env.flush_all()
    n = m43.env["fix.requisition"].search_count([("demand_plan_id", "=", plan.id)])
    assert n == 1


def test_m43_19_generate_pr_requires_approved(m43):
    plan = m43.ready_plan()
    with pytest.raises(UserError, match="Approve the plan"):
        plan.with_user(m43.planner).action_generate_pr()


def test_m43_20_price_and_vendor_from_last_po(m43):
    """The requisition is priced from the last purchase-order price. BRU-DPL-11:
    the last PO's vendor used to be blanked when M42 did not list it and the
    release went on, unsourced; now the release is refused."""
    vendor = m43.env["res.partner"].create({"name": "M43 Last Vendor"})
    m43.env["fix.purchase.order"].create(
        {
            "operating_unit_id": m43.ou.id,
            "vendor_id": vendor.id,
            "line_ids": [(0, 0, {"product_id": m43.prod.id, "qty_ordered": 1, "unit_price": 1200})],
        }
    )
    plan = m43.ready_plan()
    plan.with_user(m43.planner).write({"vendor_id": False})
    _approve(m43, plan)
    with pytest.raises(UserError, match="not an active supplier"), m43.env.cr.savepoint():
        plan.with_user(m43.planner).action_generate_pr()
    assert plan.state == "approved" and not plan.pr_requisition_id
    m43.env["fix.supplier"].create(
        {"name": vendor.name, "partner_id": vendor.id, "status": "active"}
    )
    plan.with_user(m43.planner).action_generate_pr()
    req = plan.sudo().pr_requisition_id
    # the open PO line (1 unit) is on order: projected 5 + 1 - 10 = -4 -> 84
    assert req.qty == pytest.approx(84.0)
    assert req.estimate_amount == pytest.approx(84 * 1200.0)
    assert req.vendor_id == vendor


# ===================================================================== forecasts
def _history(m43, q1, q2, q3, loc=None):
    m43.consume(q1, m43.month(-3), loc=loc)
    m43.consume(q2, m43.month(-2), loc=loc)
    m43.consume(q3, m43.month(-1), loc=loc)


def _draft_forecast(m43, user=None, **kw):
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "location_id": m43.loc.id,
        "period": m43.period,
        "window_months": 3,
    }
    vals.update(kw)
    return m43.env["fix.demand.forecast"].with_user(user or m43.planner).create(vals)


def test_m43_22_forecast_computed_from_m15_history(m43):
    _history(m43, 10, 20, 30)
    m43.consume(500, m43.month(-1), loc=m43.loc2)  # other location: not this forecast's
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        _draft_forecast(m43, forecast_qty=999_999, method="moving_average", source="history")
    f = _draft_forecast(m43)
    assert f.method == "manual" and f.forecast_qty == 0
    f.with_user(m43.planner).action_compute_forecast()
    assert f.statistical_qty == pytest.approx(20.0)
    assert f.forecast_qty == pytest.approx(20.0)
    assert (f.method, f.source) == ("moving_average", "history")
    assert f.window_months == 3 and f.history_months_with_data == 3
    # a planner override keeps the statistical value beside it, labelled manual
    with pytest.raises(ValidationError), m43.env.cr.savepoint():
        f.with_user(m43.planner).write({"has_override": True, "override_qty": 25})
    f.with_user(m43.planner).write(
        {"has_override": True, "override_qty": 25, "override_rationale": "launch promo"}
    )
    assert f.forecast_qty == 25 and f.statistical_qty == pytest.approx(20.0)
    assert (f.method, f.source) == ("manual", "manual")


def test_m43_22b_no_statistical_forecast_without_history(m43):
    m43.consume(10, m43.month(-1))
    f = _draft_forecast(m43)
    with pytest.raises(UserError, match="not ready"), m43.env.cr.savepoint():
        f.with_user(m43.planner).action_compute_forecast()
    m43.env["ir.config_parameter"].sudo().set_param("cd_demand_plan.forecast_min_history_months", 1)
    f.with_user(m43.planner).action_compute_forecast()
    assert f.statistical_qty == pytest.approx(10 / 3, abs=1e-3)


def test_m43_22c_no_forecast_labelled_history_without_computation(m43):
    """Post-migration invariant (19.0.0.2.0): forecasts typed before the
    remediation were relabelled manual overrides; nothing is labelled
    moving-average / history unless it was computed from M15."""
    Forecast = m43.env["fix.demand.forecast"]
    assert not Forecast.search_count(
        [("computed_on", "=", False), "|", ("method", "!=", "manual"), ("source", "!=", "manual")]
    )
    typed = Forecast.search([("computed_on", "=", False), ("has_override", "=", True)])
    assert all(f.override_rationale for f in typed)


def test_m43_23_actual_from_m15_and_mape_not_suppressible(m43):
    from odoo.addons.cd_p03_portal.controllers.a06 import m43 as m43_api

    f = m43.forecast(100, period=m43.last_period)
    m43.consume(40, m43.month(-1, day=10))
    assert f.actual_qty == pytest.approx(40.0)
    assert f.period_closed
    assert f.abs_error_pct == pytest.approx(150.0)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        f.with_user(m43.planner).write({"actual_qty": 100})
    measured = m43_api._measured(m43.env(user=m43.clerk.id))
    assert f in measured
    rows = [
        r
        for r in m43_api.accuracy_bias(m43.env(user=m43.clerk.id))["rows"]
        if r["period"] == m43.last_period and r["product"] == m43.prod.display_name
    ]
    assert rows and rows[0]["abs_error_pct"] == pytest.approx(150.0)


def test_m43_24_forecast_approval_role_and_sod(m43):
    _history(m43, 10, 20, 30)
    f = _draft_forecast(m43)
    f.with_user(m43.planner).action_compute_forecast()
    for user in (m43.clerk, m43.planner, m43.planner2):
        with pytest.raises(REFUSED), m43.env.cr.savepoint():
            f.with_user(user).action_approve()
    f.with_user(m43.approver).action_approve()
    assert f.state == "approved" and f.approved_by_id == m43.approver
    f.with_user(m43.planner).action_publish()
    assert f.state == "published"


def test_m43_25_forecast_state_forged(m43):
    f = _draft_forecast(m43)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        f.with_user(m43.planner).write({"state": "published"})
    assert f.state == "draft"


def test_m43_26_forecast_state_forged_via_p03(m43, p03):
    f = _draft_forecast(m43)
    p03.as_user(m43.planner)
    out = p03.write(model="fix.demand.forecast", record_id=f.id, values={"state": "published"})
    f.invalidate_recordset()
    assert "error" in out and f.state == "draft"


def test_m43_27_published_forecast_frozen(m43):
    _history(m43, 10, 20, 30)
    f = _draft_forecast(m43)
    f.with_user(m43.planner).action_compute_forecast()
    f.with_user(m43.approver).action_approve()
    f.with_user(m43.planner).action_publish()
    for vals in (
        {"has_override": True, "override_qty": 5000, "override_rationale": "x"},
        {"period": m43.last_period},
        {"window_months": 1},
    ):
        with pytest.raises(REFUSED), m43.env.cr.savepoint():
            f.with_user(m43.planner2).write(vals)
    with pytest.raises(UserError), m43.env.cr.savepoint():
        f.with_user(m43.planner).action_reset_draft()
    assert f.forecast_qty == pytest.approx(20.0)


def test_m43_28_one_forecast_per_product_location_month(m43):
    _draft_forecast(m43)
    with pytest.raises(ValidationError), m43.env.cr.savepoint():
        _draft_forecast(m43, user=m43.planner2)


def test_m43_29_period_must_be_a_month(m43):
    with pytest.raises(ValidationError), m43.env.cr.savepoint():
        _draft_forecast(m43, period="banana")


# ===================================================================== policy
def test_m43_30_safety_stock_formula(m43):
    pol = m43.policy(4, 2, 9, state="draft")
    assert pol.safety_stock == pytest.approx(9.9)
    assert pol.reorder_point == pytest.approx(45.9)
    assert pol.target_level == pytest.approx(45.9 + 4 * 30)


def test_m43_31_policy_statistics_from_m15_history(m43):
    pol = (
        m43.env["fix.demand.policy"]
        .with_user(m43.planner)
        .create(
            {
                "product_id": m43.prod.id,
                "part_id": m43.part.id,
                "location_id": m43.loc.id,
                "history_days": 10,
                "lead_time_days": 9,
            }
        )
    )
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        pol.with_user(m43.planner).write({"demand_stddev": 0, "avg_daily_demand": 40})
    first = fields.Date.today() - timedelta(days=10)
    for i in range(0, 10, 2):  # 2 units on 5 of the 10 days
        m43.consume(2, datetime.combine(first + timedelta(days=i), datetime.min.time()))
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.avg_daily_demand == pytest.approx(1.0)
    assert pol.demand_stddev == pytest.approx((10 / 9) ** 0.5, abs=1e-3)
    assert pol.safety_stock == pytest.approx(round(1.65 * (10 / 9) ** 0.5 * 3, 2))


def test_m43_32_policy_computes_not_writable(m43):
    pol = m43.policy(4, 2, 9, state="draft")
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        pol.with_user(m43.planner).write({"safety_stock": 5000, "reorder_point": 9000})
    pol.invalidate_recordset()
    assert pol.safety_stock == pytest.approx(9.9)


def test_m43_33_policy_safety_stock_p03_refused(m43, p03):
    pol = m43.policy(4, 2, 9, state="draft")
    p03.as_user(m43.planner)
    out = p03.write(model="fix.demand.policy", record_id=pol.id, values={"safety_stock": 5000})
    pol.invalidate_recordset()
    assert "error" in out and pol.safety_stock == pytest.approx(9.9)


def test_m43_34_a_class_parameter_change_needs_approval_and_versions(m43, monkeypatch):
    published = []
    Rule = type(m43.env["fix.reorder.rule"])
    monkeypatch.setattr(
        Rule,
        "_fix_publish_from_plan",
        lambda self, *a, **k: published.append(a) or self.browse(),
        raising=False,
    )
    m43.segment(abc="a", criticality="critical")
    v1 = m43.policy(6, 2.2, 13, service="99")
    rop = v1.reorder_point
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        v1.with_user(m43.planner).write({"service_level_pct": "90", "lead_time_days": 1})
    v1.invalidate_recordset()
    assert v1.reorder_point == rop
    action = v1.with_user(m43.planner).action_revise()
    v2 = m43.env["fix.demand.policy"].browse(action["res_id"])
    assert v2.state == "draft" and v2.version == 2 and v2.previous_id == v1
    v2.with_user(m43.planner).write({"service_level_pct": "90", "lead_time_days": 1})
    v2.sudo().write(
        {"avg_daily_demand": 6, "demand_stddev": 2.2, "history_computed_on": datetime.now()}
    )
    assert v2.approval_required
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        v2.with_user(m43.planner).action_activate()
    m43.env.ref(PLANNER).sudo().write({"user_ids": [(4, m43.approver2.id)]})
    v2.with_user(m43.approver2).write({"review_period_days": 31})
    with pytest.raises(UserError, match="segregation"), m43.env.cr.savepoint():
        v2.with_user(m43.approver2).action_activate()
    v2.with_user(m43.approver).action_activate()
    assert (v1.state, v2.state) == ("superseded", "active")
    assert v1.reorder_point == rop, "the superseded version keeps its figures"
    assert v2.approved_by_id == m43.approver
    assert published and published[-1][2] == pytest.approx(v2.reorder_point)


def test_m43_34b_b_class_planner_activates_within_guard_rails(m43, monkeypatch):
    Rule = type(m43.env["fix.reorder.rule"])
    monkeypatch.setattr(
        Rule, "_fix_publish_from_plan", lambda self, *a, **k: self.browse(), raising=False
    )
    m43.segment(abc="b", criticality="medium")
    pol = m43.policy(4, 2, 9, state="draft")
    assert not pol.approval_required
    pol.with_user(m43.planner).action_activate()
    assert pol.state == "active"
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        m43.policy(1, 1, 5, state="draft").with_user(m43.clerk).action_activate()


def test_m43_35_one_active_policy_per_part_location(m43, monkeypatch):
    Rule = type(m43.env["fix.reorder.rule"])
    monkeypatch.setattr(
        Rule, "_fix_publish_from_plan", lambda self, *a, **k: self.browse(), raising=False
    )
    m43.segment()
    first = m43.policy(4, 1, 7, state="draft")
    second = m43.policy(40, 10, 7, state="draft")
    first.with_user(m43.planner).action_activate()
    with pytest.raises(UserError, match="revise"), m43.env.cr.savepoint():
        second.with_user(m43.planner).action_activate()
    with pytest.raises(ValidationError), m43.env.cr.savepoint():
        m43.policy(40, 10, 7, state="active")


def test_m43_36_activation_publishes_rop_to_m15_reorder_rule(m43):
    """B1 contract fix.reorder.rule._fix_publish_from_plan(part, location,
    min_qty, max_qty, source_ref). Fails until B1's method lands."""
    m43.segment()
    pol = m43.policy(4, 2, 9, state="draft")
    pol.with_user(m43.planner).action_activate()
    assert pol.published_on
    rule = m43.env["fix.reorder.rule"].search(
        [("spare_part_id", "=", m43.part.id), ("location_id", "=", m43.loc.id)]
    )
    assert len(rule) == 1
    assert rule.min_qty == pytest.approx(pol.reorder_point)
    assert rule.max_qty == pytest.approx(pol.target_level)


def test_m43_37_plan_rop_is_the_policy_rop(m43):
    m43.policy(4, 2, 9)
    plan = m43.plan()
    assert plan.reorder_point == pytest.approx(45.9)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        plan.with_user(m43.planner).write({"reorder_point": 0})


def test_m43_38_pause_and_resume_are_transitions(m43):
    m43.segment(abc="a")
    pol = m43.policy(4, 2, 9)
    pol.with_user(m43.planner).action_pause()
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        pol.with_user(m43.planner).write({"state": "active"})
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        pol.with_user(m43.planner).action_resume()
    pol.with_user(m43.approver).action_resume()
    assert pol.state == "active"
    with pytest.raises(UserError), m43.env.cr.savepoint():
        pol.with_user(m43.approver).action_resume()


# ===================================================================== rebalance
def _rebalance(m43, user=None, **kw):
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "source_location_id": m43.loc.id,
        "target_location_id": m43.loc2.id,
        "qty": 5,
        "transfer_cost": 300,
        "benefit_value": 500,
        "benefit_basis": "Avoided emergency buy",
    }
    vals.update(kw)
    return m43.env["fix.demand.rebalance"].with_user(user or m43.planner).create(vals)


def test_m43_39_rebalance_approval_role_and_sod(m43):
    m43.stock(50)
    r = _rebalance(m43)
    for user in (m43.clerk, m43.planner):
        with pytest.raises(REFUSED), m43.env.cr.savepoint():
            r.with_user(user).action_approve()
    m43.env.ref(PLANNER).sudo().write({"user_ids": [(4, m43.approver2.id)]})
    r.with_user(m43.approver2).write({"qty": 6})
    with pytest.raises(UserError, match="segregation"), m43.env.cr.savepoint():
        r.with_user(m43.approver2).action_approve()
    r.with_user(m43.approver).action_approve()
    assert r.state == "approved"


def test_m43_40_approved_rebalance_creates_draft_m15_transfer(m43):
    m43.stock(50)
    r = _rebalance(m43)
    r.with_user(m43.approver).action_approve()
    t = r.transfer_id
    assert t and t.state == "draft"
    assert (t.from_location_id, t.to_location_id) == (m43.loc, m43.loc2)
    assert t.line_ids.part_id == m43.part and t.line_ids.qty == pytest.approx(5.0)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        _rebalance(m43, target_location_id=m43.loc.id)
        m43.env.flush_all()
    big = _rebalance(m43, qty=500)
    with pytest.raises(UserError, match="available"), m43.env.cr.savepoint():
        big.with_user(m43.approver).action_approve()


def test_m43_41_no_flat_savings_claim(m43):
    r = _rebalance(m43, qty=3)
    assert "savings" not in r._fields
    assert r.stock_value == pytest.approx(3 * 1000.0)
    assert r.transfer_cost == pytest.approx(300.0)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        r.with_user(m43.planner).write({"stock_value": 1_000_000})


def test_m43_42_rebalance_decisions_are_final(m43):
    m43.stock(50)
    r = _rebalance(m43)
    r.with_user(m43.approver).action_approve()
    with pytest.raises(UserError), m43.env.cr.savepoint():
        r.with_user(m43.approver2).action_reject()
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        r.with_user(m43.planner).write({"qty": 9})
    assert r.state == "approved"


def test_m43_43_rebalance_state_forged_and_kpi(m43):
    from odoo.addons.cd_p03_portal.controllers.a06 import m43 as m43_api

    before = m43_api.kpis(m43.env(user=m43.clerk.id))["rebalance_value_moved"]
    r = _rebalance(m43, qty=100_000)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        r.with_user(m43.planner).write({"state": "approved"})
    after = m43_api.kpis(m43.env(user=m43.clerk.id))["rebalance_value_moved"]
    assert r.state == "proposed" and after == before


# ===================================================================== scenario / review
def test_m43_44_scenario_applies_lead_time_delta(m43):
    pol = m43.policy(4, 2, 9)
    s = (
        m43.env["fix.demand.scenario"]
        .with_user(m43.planner)
        .create({"policy_id": pol.id, "demand_adjust_pct": 0, "lead_time_delta_days": 30})
    )
    assert s.product_id == m43.prod
    assert s.base_reorder_point == pytest.approx(45.9)
    assert s.projected_lead_time == 39
    assert s.projected_safety_stock == pytest.approx(round(1.65 * 2 * 39**0.5, 2))
    assert s.projected_reorder_point == pytest.approx(round(4 * 39 + s.projected_safety_stock, 2))


def test_m43_45_scenario_base_rop_from_policy(m43):
    pol = m43.policy(4, 2, 9)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        m43.env["fix.demand.scenario"].with_user(m43.planner).create(
            {"product_id": m43.prod.id, "policy_id": pol.id, "base_reorder_point": 1}
        )
    s = m43.env["fix.demand.scenario"].with_user(m43.planner).create({"policy_id": pol.id})
    assert s.base_reorder_point == pytest.approx(45.9)


def test_m43_46_scenario_writes_no_parameters(m43):
    pol = m43.policy(4, 2, 9)
    n_plans = m43.env["fix.demand.plan"].search_count([])
    s = (
        m43.env["fix.demand.scenario"]
        .with_user(m43.planner)
        .create({"policy_id": pol.id, "demand_adjust_pct": 50})
    )
    s.with_user(m43.planner).action_run()
    assert s.state == "run"
    assert pol.reorder_point == pytest.approx(45.9)
    assert m43.env["fix.demand.plan"].search_count([]) == n_plans
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        s.with_user(m43.planner).write({"demand_adjust_pct": 0})


def test_m43_47_review_completed_by_its_owner_with_outcome(m43):
    Review = m43.env["fix.demand.review"].with_user(m43.planner)
    r = Review.create({"period": m43.period, "due_on": date.today()})
    with pytest.raises(UserError, match="owner"), m43.env.cr.savepoint():
        r.action_complete()
    owner = m43.env["hr.employee"].search([("user_id", "=", m43.planner2.id)], limit=1)
    r.write({"owner_id": owner.id})
    with pytest.raises(UserError, match="owner"), m43.env.cr.savepoint():
        r.with_user(m43.planner).action_complete()
    with pytest.raises(UserError, match="outcome"), m43.env.cr.savepoint():
        r.with_user(m43.planner2).action_complete()
    r.with_user(m43.planner2).write({"notes": "Agreed the Q4 consensus numbers"})
    r.with_user(m43.planner2).action_complete()
    assert r.state == "done" and r.completed_by_id == m43.planner2
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        r.with_user(m43.planner2).write({"state": "scheduled"})


# ===================================================================== KPI / report truth
def test_m43_48_van_par_is_the_van_policy_target(m43):
    from odoo.addons.cd_p03_portal.controllers.a06 import m43 as m43_api

    van = m43.location("V", van=True)
    pol = m43.policy(4, 2, 9, loc=van)
    m43.stock(10, loc=van)
    rows = [
        r
        for r in m43_api.van_par(m43.env(user=m43.clerk.id))["rows"]
        if r["van"] == van.display_name
    ]
    assert rows
    assert rows[0]["van_par"] == pytest.approx(pol.target_level)
    assert rows[0]["van_par"] != pytest.approx(round(45.9 * 1.2, 2))
    assert rows[0]["top_up_qty"] == pytest.approx(pol.target_level - 10)


def test_m43_49_p03_refuses_every_workflow_field(m43, p03):
    """Through /p03/model/write the guarded fields of every M43 model are refused."""
    m43.stock(50)
    pol = m43.policy(4, 2, 9, state="draft")
    records = {
        "fix.demand.plan": (m43.plan(), {"state": "approved", "approved_order_qty": 5}),
        "fix.demand.forecast": (_draft_forecast(m43), {"state": "approved", "statistical_qty": 7}),
        "fix.demand.policy": (pol, {"state": "active", "avg_daily_demand": 9}),
        "fix.demand.segment": (m43.segment(), {"abc_class": "a"}),
        "fix.demand.review": (
            m43.env["fix.demand.review"].create({"period": m43.period, "due_on": date.today()}),
            {"state": "done"},
        ),
        "fix.demand.rebalance": (_rebalance(m43), {"state": "approved", "stock_value": 1}),
        "fix.demand.scenario": (
            m43.env["fix.demand.scenario"].create({"policy_id": pol.id}),
            {"state": "run", "projected_reorder_point": 1},
        ),
    }
    p03.as_user(m43.planner)
    for model, (rec, attacks) in records.items():
        for field, value in attacks.items():
            before = rec[field]
            out = p03.write(model=model, record_id=rec.id, values={field: value})
            rec.invalidate_recordset()
            assert "error" in out, (model, field, out)
            assert rec[field] == before, (model, field)


def test_m43_50_every_model_guarded_and_actions_declared(m43):
    from odoo.addons.cd_p03_portal.controllers.a06 import m43 as m43_api

    for model, conf in m43_api.SURFACES.items():
        recs = m43.env[model]
        assert "state" in recs._fix_guarded_fields(), model
        for method in conf["actions"]:
            assert callable(getattr(recs, method, None)), (model, method)


def test_m43_51_segment_classified_from_m15_value(m43):
    other_tmpl = m43.env["product.template"].create({"name": "M43 cheap %s" % m43.tag})
    cheap_part = m43.env["fix.spare.part"].create(
        {"name": "M43 cheap", "part_number": "M43C-%s" % m43.tag, "unit_cost": 1.0}
    )
    seg = (
        m43.env["fix.demand.segment"]
        .with_user(m43.planner)
        .create({"product_id": m43.prod.id, "part_id": m43.part.id})
    )
    cheap = (
        m43.env["fix.demand.segment"]
        .with_user(m43.planner)
        .create({"product_id": other_tmpl.product_variant_id.id, "part_id": cheap_part.id})
    )
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        seg.with_user(m43.planner).write({"abc_class": "a", "xyz_class": "x"})
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        seg.with_user(m43.planner).write({"criticality": "low"})
    for delta in range(-12, 0):
        m43.consume(100, m43.month(delta))
    m43.consume(1, m43.month(-2), part=cheap_part)
    m43.env["fix.demand.segment"].with_user(m43.planner).action_classify()
    assert seg.classified_on and seg.abc_class == "a" and seg.xyz_class == "x"
    assert seg.consumption_value == pytest.approx(1200 * 1000.0)
    assert cheap.abc_class in ("b", "c") and cheap.xyz_class == "z"
    seg.with_user(m43.approver).write({"criticality": "critical"})
    assert seg.criticality == "critical"


def test_m43_kpis_read_as_the_caller(m43):
    from odoo.addons.cd_p03_portal.controllers.a06 import m43 as m43_api

    plan = _approve(m43, m43.ready_plan())
    k = m43_api.kpis(m43.env(user=m43.clerk.id))
    assert k["planned_orders"] >= 1
    assert plan.state == "approved"
    for name, fn in m43_api.REPORTS.items():
        pack = fn(m43.env(user=m43.clerk.id))
        assert "rows" in pack, name


# ===================================================================== follow-up: lead time, MOQ/pack, budget
def _received_po(m43, sent, received, qty=5):
    """A sent PO for the product with a posted goods receipt (superuser setup)."""
    vendor = m43.env["res.partner"].create({"name": "M43 LT Vendor"})
    po = m43.env["fix.purchase.order"].create(
        {
            "operating_unit_id": m43.ou.id,
            "vendor_id": vendor.id,
            "line_ids": [
                (0, 0, {"product_id": m43.prod.id, "qty_ordered": qty, "unit_price": 900})
            ],
        }
    )
    po.write({"state": "sent", "sent_at": datetime.combine(sent, datetime.min.time())})
    receipt = m43.env["fix.purchase.receipt"].create(
        {
            "purchase_order_id": po.id,
            "line_ids": [(0, 0, {"po_line_id": po.line_ids.id, "qty_received": qty})],
        }
    )
    receipt.write({"state": "posted", "received_on": received})
    return po


def _draft_policy(m43, **kw):
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "location_id": m43.loc.id,
        "lead_time_days": 9,
    }
    vals.update(kw)
    return m43.env["fix.demand.policy"].with_user(m43.planner).create(vals)


def test_m43_31b_lead_time_observed_from_m16_receipts(m43):
    today = fields.Date.today()
    _received_po(m43, today - timedelta(days=20), today - timedelta(days=10))  # 10 days
    _received_po(m43, today - timedelta(days=16), today - timedelta(days=3))  # 13 days
    _received_po(m43, today - timedelta(days=900), today - timedelta(days=880))  # outside window
    pol = _draft_policy(m43, lead_time_window_days=365)
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        pol.with_user(m43.planner).write({"observed_lead_time_days": 1})
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.lead_time_samples == 2
    assert pol.observed_lead_time_days == pytest.approx(11.5)
    assert pol.lead_time_days == 12 and pol.lead_time_source == "observed"
    # a planner override needs a recorded rationale
    with pytest.raises(ValidationError, match="rationale"), m43.env.cr.savepoint():
        pol.with_user(m43.planner).write({"lead_time_days": 5})
    pol.with_user(m43.planner).write(
        {"lead_time_days": 5, "lead_time_override_rationale": "Vendor moved to air freight"}
    )
    assert pol.lead_time_source == "override"
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.lead_time_days == 5, "a reasoned override survives a refresh"
    assert pol.observed_lead_time_days == pytest.approx(11.5)


def test_m43_31c_override_on_a_class_needs_an_approver(m43, monkeypatch):
    Rule = type(m43.env["fix.reorder.rule"])
    monkeypatch.setattr(
        Rule, "_fix_publish_from_plan", lambda self, *a, **k: self.browse(), raising=False
    )
    today = fields.Date.today()
    _received_po(m43, today - timedelta(days=20), today - timedelta(days=10))
    m43.segment(abc="a")
    pol = _draft_policy(m43)
    m43.consume(3, today - timedelta(days=2))
    pol.with_user(m43.planner).action_refresh_from_history()
    pol.with_user(m43.planner).write(
        {"lead_time_days": 4, "lead_time_override_rationale": "expedited lane"}
    )
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        pol.with_user(m43.planner).action_activate()
    pol.with_user(m43.approver).action_activate()
    assert pol.state == "active" and pol.lead_time_source == "override"


def test_m43_31d_no_receipt_history_keeps_typed_lead_time(m43):
    pol = _draft_policy(m43, lead_time_days=9)
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.lead_time_samples == 0
    assert pol.lead_time_days == 9 and pol.lead_time_source == "typed"


def test_m43_04c_moq_and_pack_size_applied(m43):
    m43.policy(2, 0, 10, moq_qty=100, pack_size=12)
    m43.forecast(10)
    m43.stock(5)
    plan = m43.plan()
    assert plan.raw_order_qty == pytest.approx(85.0)
    assert plan.recommended_order == pytest.approx(108.0)  # MOQ 100 -> 9 packs of 12
    other = m43.location("C")
    m43.policy(2, 0, 10, pack_size=20, loc=other)
    m43.forecast(10, loc=other)
    m43.stock(5, loc=other)
    plan2 = m43.plan(name="pack only", location_id=other.id)
    assert plan2.recommended_order == pytest.approx(100.0)  # 85 -> 5 packs of 20
    plan.with_user(m43.approver).action_approve()
    assert plan.approved_order_qty == pytest.approx(108.0)
    with pytest.raises(ValidationError), m43.env.cr.savepoint():
        m43.policy(2, 0, 10, state="draft", pack_size=-1, loc=other)


def _parts_budget(m43, planned):
    env = m43.env
    account = env["account.account"].search([("account_type", "=", "expense")], limit=1)
    today = fields.Date.today()
    version = env["fix.budget.version"].create(
        {
            "name": "M43 budget %s" % m43.tag,
            "fiscal_year": str(today.year),
            "date_from": today.replace(month=1, day=1),
            "date_to": today.replace(month=12, day=31),
            "parts_account_id": account.id,
        }
    )
    budget = env["fix.budget"].create(
        {"name": "M43 parts", "fiscal_year": str(today.year), "version_id": version.id}
    )
    env["fix.budget.line"].create(
        {
            "budget_id": budget.id,
            "account_id": account.id,
            "date_from": today.replace(month=1, day=1),
            "date_to": today.replace(month=12, day=31),
            "planned_amount": planned,
        }
    )
    version.write({"state": "approved"})
    return version


def test_m43_16c_budget_check(m43):
    if "fix.budget.line" not in m43.env:
        plan = m43.ready_plan()
        _release(m43, plan)
        assert plan.budget_check.startswith("No budget check")
        return
    m43.env["fix.budget.version"].search(
        [("company_id", "=", m43.company.id), ("state", "=", "approved")]
    ).write({"state": "superseded"})
    # no approved version -> released, with a clear note
    plan = m43.ready_plan()
    _release(m43, plan)
    assert plan.budget_check.startswith("No budget check")
    # an exhausted budget is refused when enforced, reported otherwise
    _parts_budget(m43, 1.0)
    other = m43.env["product.template"].create({"name": "M43 budget", "standard_price": 100.0})
    second = m43.plan(name="second", location_id=m43.loc2.id, product_id=other.id)
    m43.policy(2, 0, 10, loc=m43.loc2)
    m43.forecast(10, loc=m43.loc2)
    second.with_user(m43.approver).action_approve()
    m43.env["ir.config_parameter"].sudo().set_param("cd_demand_plan.enforce_budget", "1")
    with pytest.raises(UserError, match="Over budget"), m43.env.cr.savepoint():
        second.with_user(m43.planner).action_generate_pr()
    m43.env["ir.config_parameter"].sudo().set_param("cd_demand_plan.enforce_budget", "0")
    second.with_user(m43.planner).action_generate_pr()
    assert second.state == "released"
    assert second.budget_check.startswith("Over budget")
    with pytest.raises(REFUSED), m43.env.cr.savepoint():
        second.with_user(m43.planner).write({"budget_check": "fine"})


def test_m43_36b_predicted_demand_passed_when_m15_accepts_it(m43, monkeypatch):
    seen = {}
    Rule = type(m43.env["fix.reorder.rule"])

    def publish(self, part, location, min_qty, max_qty, source_ref, predicted_demand=None):
        seen["predicted"] = predicted_demand
        return self.browse()

    monkeypatch.setattr(Rule, "_fix_publish_from_plan", publish, raising=False)
    m43.segment()
    pol = m43.policy(4, 2, 9, state="draft")
    pol.with_user(m43.planner).action_activate()
    assert seen["predicted"] == pytest.approx(28.0)
