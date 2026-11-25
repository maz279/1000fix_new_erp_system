"""A06 final pass, M43: provisional demand, sourcing, the plan's later states,
the rebalance benefit gate, the paused reorder rule, publication of the classes,
company scope, import lead times and the reports. Each test attacks the control
as a non-admin with the real role and runs the proper path. Live ORM inside the
rolled-back odoo_env; fixtures in conftest.py."""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.a06 import m43 as ctl
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (UserError, ValidationError, AccessError, IntegrityError)


def _refused(env, fn, *args, match=None):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        fn(*args)
        env.flush_all()


def _draft_policy(m43, user=None, **kw):
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "location_id": m43.loc.id,
        "lead_time_days": 10,
        "review_period_days": 30,
    }
    vals.update(kw)
    return m43.env["fix.demand.policy"].with_user(user or m43.planner).create(vals)


def _with_history(m43):
    """Enough of the last window months carry M15 consumption."""
    for delta in (-1, -2, -3):
        m43.consume(6, m43.month(delta))


def _released(m43, **kw):
    plan = m43.ready_plan(**kw)
    plan.with_user(m43.approver).action_approve()
    plan.with_user(m43.planner).action_generate_pr()
    return plan


def _approve_requisition(req):
    req.sudo()._guarded().write({"state": "approved"})


def _converted(m43, plan):
    req = plan.sudo().pr_requisition_id
    _approve_requisition(req)
    req.sudo()._guarded().write(
        {
            "state": "converted",
            "purchase_order_id": m43.env["fix.purchase.order"]
            .create({"vendor_id": m43.vendor.id, "operating_unit_id": m43.ou.id, "state": "sent"})
            .id,
        }
    )
    return req.purchase_order_id


# ================================================================ B13 provisional demand
def test_b13_no_history_part_runs_on_an_approved_provisional_demand(m43):
    """The proper path: nothing in M15, a manual demand with a reason, an
    approver who did not enter it, policy active, plan approved."""
    pol = _draft_policy(m43, provisional_daily_demand=2.0, provisional_reason="New model launch")
    assert pol.provisional_state == "entered"
    _refused(m43.env, pol.with_user(m43.approver).action_activate, match="no demand statistics")

    pol.with_user(m43.approver).action_approve_provisional()
    assert pol.provisional_state == "approved"
    assert pol.provisional_approved_by_id == m43.approver
    assert pol.avg_daily_demand == pytest.approx(2.0)
    assert pol.reorder_point == pytest.approx(20.0) and pol.target_level == pytest.approx(80.0)
    assert not pol.history_computed_on, "it must not read as if it came from history"

    pol.with_user(m43.approver).action_activate()
    assert pol.state == "active" and pol.published_rule_id.min_qty == pytest.approx(20.0)

    m43.forecast(10)
    plan = m43.plan()
    plan.with_user(m43.approver).action_approve()
    assert plan.state == "approved" and plan.recommended_order > 0


def test_b13_role_and_two_person_rule(m43):
    pol = _draft_policy(m43, provisional_daily_demand=2.0, provisional_reason="New model")
    _refused(m43.env, pol.with_user(m43.planner).action_approve_provisional, match="Approver")
    _refused(m43.env, pol.with_user(m43.clerk).action_approve_provisional, match="Approver")
    assert pol.provisional_state == "entered"
    both = m43.user(
        "both",
        ["cd_demand_plan.group_fix_demand_planner", "cd_demand_plan.group_fix_demand_approver"],
    )
    own = _draft_policy(
        m43,
        user=both,
        provisional_daily_demand=2.0,
        provisional_reason="Mine",
        location_id=m43.loc2.id,
    )
    _refused(m43.env, own.with_user(both).action_approve_provisional, match="segregation")


def test_b13_needs_a_reason_and_no_real_history(m43):
    pol = _draft_policy(m43, provisional_daily_demand=2.0)
    _refused(m43.env, pol.with_user(m43.approver).action_approve_provisional, match="state why")
    pol.with_user(m43.planner).write({"provisional_reason": "New model"})
    _with_history(m43)
    _refused(
        m43.env, pol.with_user(m43.approver).action_approve_provisional, match="real M15 history"
    )


def test_b13_cannot_be_forged_or_kept_after_a_change(m43):
    pol = _draft_policy(m43, provisional_daily_demand=2.0, provisional_reason="New model")
    _refused(m43.env, pol.with_user(m43.planner).write, {"provisional_state": "approved"})
    _refused(m43.env, pol.with_user(m43.planner).write, {"avg_daily_demand": 50.0})
    pol.with_user(m43.approver).action_approve_provisional()
    # the approved figure retyped: back to awaiting approval, the figure gone
    pol.with_user(m43.planner).write({"provisional_daily_demand": 99.0})
    assert pol.provisional_state == "entered" and not pol.provisional_approved_by_id
    assert pol.avg_daily_demand == 0.0
    _refused(m43.env, pol.with_user(m43.approver).action_activate, match="no demand statistics")


def test_b13_refresh_keeps_it_with_no_history_and_expires_it_with_history(m43):
    pol = _draft_policy(m43, provisional_daily_demand=2.0, provisional_reason="New model")
    pol.with_user(m43.approver).action_approve_provisional()
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.provisional_state == "approved" and pol.avg_daily_demand == pytest.approx(2.0)
    _with_history(m43)
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.provisional_state == "expired" and pol.history_computed_on
    assert pol.avg_daily_demand != pytest.approx(2.0)


def test_b13_active_policy_expires_when_history_arrives_and_plan_is_refused(m43):
    pol = _draft_policy(m43, provisional_daily_demand=2.0, provisional_reason="New model")
    pol.with_user(m43.approver).action_approve_provisional()
    pol.with_user(m43.approver).action_activate()
    m43.forecast(10)
    plan = m43.plan()
    _with_history(m43)
    # refused at once, before the daily job has run
    _refused(m43.env, plan.with_user(m43.approver).action_approve, match="real M15 history")
    assert m43.env["fix.demand.policy"]._cron_expire_provisional() >= 1
    assert pol.provisional_state == "expired" and pol.state == "active"
    _refused(m43.env, plan.with_user(m43.approver).action_approve, match="real M15 history")
    # the way out: a new version from history
    pol.with_user(m43.planner).action_revise()
    new = m43.env["fix.demand.policy"].search([("previous_id", "=", pol.id)])
    assert new.provisional_state == "none"
    new.with_user(m43.planner).action_refresh_from_history()
    new.with_user(m43.approver).action_activate()
    plan.invalidate_recordset()
    plan.with_user(m43.approver).action_approve()
    assert plan.state == "approved"


def test_b13_cron_shipped(m43):
    cron = m43.env.ref("cd_demand_plan.ir_cron_demand_provisional_expire")
    assert cron.active and "_cron_expire_provisional" in cron.code


# ================================================================ B14 supplier
def test_b14_no_supplier_refuses_release(m43):
    plan = m43.ready_plan()
    plan.with_user(m43.planner).write({"vendor_id": False})
    plan.with_user(m43.approver).action_approve()
    _refused(m43.env, plan.with_user(m43.planner).action_generate_pr, match="no supplier")
    assert plan.state == "approved" and not plan.pr_requisition_id


def test_b14_inactive_supplier_refuses_release(m43):
    plan = m43.ready_plan()
    plan.with_user(m43.approver).action_approve()
    m43.supplier.sudo()._guarded().write({"status": "suspended"})
    _refused(m43.env, plan.with_user(m43.planner).action_generate_pr, match="not an active")
    assert plan.state == "approved"


def test_b14_supplier_unknown_to_m42_refuses_release(m43):
    stranger = m43.env["res.partner"].create({"name": "M43 Stranger %s" % m43.tag})
    plan = m43.ready_plan()
    plan.with_user(m43.planner).write({"vendor_id": stranger.id})
    plan.with_user(m43.approver).action_approve()
    _refused(m43.env, plan.with_user(m43.planner).action_generate_pr, match="not an active")


def test_b14_last_po_supplier_is_used_when_the_plan_names_none(m43):
    plan = m43.ready_plan()
    plan.with_user(m43.planner).write({"vendor_id": False})
    m43.env["fix.purchase.order"].create(
        {
            "vendor_id": m43.vendor.id,
            "operating_unit_id": m43.ou.id,
            "line_ids": [(0, 0, {"product_id": m43.prod.id, "qty_ordered": 1, "unit_price": 900})],
        }
    )
    plan.with_user(m43.approver).action_approve()
    plan.with_user(m43.planner).action_generate_pr()
    assert plan.sudo().pr_requisition_id.vendor_id == m43.vendor


# ================================================================ B15 later states
def test_b15_conversion_moves_the_plan_and_links_the_po(m43):
    plan = _released(m43)
    order = _converted(m43, plan)
    assert plan.state == "converted" and plan.purchase_order_id == order


def test_b15_full_receipt_closes_the_plan_with_the_actual_lead_time(m43):
    plan = _released(m43)
    order = _converted(m43, plan)
    plan.sudo()._guarded().write({"approved_on": fields.Datetime.now() - timedelta(days=12)})
    order.sudo()._guarded().write(
        {"state": "received", "received_on": fields.Date.context_today(order)}
    )
    assert plan.state == "closed"
    assert plan.actual_lead_time_days in (12, 11, 13)
    _refused(m43.env, plan.with_user(m43.planner).write, {"name": "changed", "part_id": False})


def test_b15_partial_receipt_keeps_it_converted(m43):
    plan = _released(m43)
    order = _converted(m43, plan)
    order.sudo()._guarded().write({"state": "partially_received"})
    assert plan.state == "converted"


def test_b15_rejected_requisition_reopens_and_reissues(m43):
    plan = _released(m43)
    req = plan.sudo().pr_requisition_id
    # refused while M16 is still deciding it
    _refused(m43.env, plan.with_user(m43.planner).action_reopen, "x", match="only when M16")
    req._guarded().write({"state": "rejected"})
    assert plan.pr_state == "rejected"
    _refused(m43.env, plan.with_user(m43.clerk).action_reopen, "x", match="Planner")
    _refused(m43.env, plan.with_user(m43.planner).action_reopen, match="why")
    plan.with_user(m43.planner).action_reopen("Supplier failed the price check")
    assert plan.state == "draft" and not plan.pr_requisition_id and not plan.approved_by_id
    assert plan.approved_order_qty == 0.0
    assert req.reissued_from_plan_id == plan and not req.demand_plan_id
    # the reopener prepared it now, so another approves it
    plan.with_user(m43.approver).action_approve()
    plan.with_user(m43.planner).action_generate_pr()
    assert plan.state == "released" and plan.pr_requisition_id != req


def test_b15_cancelled_po_reopens_a_converted_plan(m43):
    plan = _released(m43)
    order = _converted(m43, plan)
    _refused(m43.env, plan.with_user(m43.planner).action_reopen, "x", match="only when M16")
    order.sudo()._guarded().write({"state": "cancelled"})
    plan.with_user(m43.planner).action_reopen("PO cancelled by the supplier")
    assert plan.state == "draft" and not plan.purchase_order_id


def test_b15_released_plan_still_makes_one_requisition(m43):
    plan = _released(m43)
    _refused(m43.env, plan.with_user(m43.planner).action_generate_pr, match="already has")
    _refused(m43.env, plan.with_user(m43.planner).write, {"state": "draft"})
    _refused(
        m43.env,
        plan.with_user(m43.planner).write,
        {"purchase_order_id": False, "actual_lead_time_days": 1},
    )


# ================================================================ B16 benefit
def _proposal(m43, **kw):
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "source_location_id": m43.loc.id,
        "target_location_id": m43.loc2.id,
        "qty": 5,
        "transfer_cost": 200.0,
    }
    vals.update(kw)
    return m43.env["fix.demand.rebalance"].with_user(m43.planner).create(vals)


def test_b16_benefit_must_exceed_transfer_cost(m43):
    m43.stock(50, loc=m43.loc)
    for benefit in (0.0, 100.0, 200.0):
        prop = _proposal(m43, benefit_value=benefit, benefit_basis="Avoided buy")
        _refused(m43.env, prop.with_user(m43.approver).action_approve, match="BRU-DPL-13")
        assert prop.state == "proposed" and not prop.transfer_id


def test_b16_needs_a_basis_and_the_proper_path_makes_the_transfer(m43):
    m43.stock(50, loc=m43.loc)
    prop = _proposal(m43, benefit_value=500.0)
    assert prop.net_benefit == pytest.approx(300.0)
    _refused(m43.env, prop.with_user(m43.approver).action_approve, match="based on")
    prop.with_user(m43.planner).write({"benefit_basis": "Avoided emergency buy of 5 units"})
    prop.with_user(m43.approver).action_approve()
    assert prop.state == "approved" and prop.transfer_id
    _refused(m43.env, prop.with_user(m43.planner).write, {"benefit_value": 1.0})


# ================================================================ B17 paused
def test_b17_pause_suspends_the_published_rule_and_resume_restores_it(m43):
    pol = _draft_policy(m43, provisional_daily_demand=2.0, provisional_reason="New model")
    pol.with_user(m43.approver).action_approve_provisional()
    pol.with_user(m43.approver).action_activate()
    rule = pol.published_rule_id
    assert rule.state == "active"

    pol.with_user(m43.planner).action_pause()
    assert pol.state == "paused" and rule.state == "archived"
    # the sweep does not alert a suspended rule, though stock is at zero
    m43.env["fix.reorder.rule"].check_replenishment_alerts()
    assert rule.state == "archived"

    pol.with_user(m43.approver).action_resume()
    assert pol.state == "active" and rule.state == "active"
    assert rule.min_qty == pytest.approx(pol.reorder_point)
    m43.env["fix.reorder.rule"].check_replenishment_alerts()
    assert rule.state in ("alert", "ordered"), "live again"


def test_b17_clerk_cannot_pause(m43):
    pol = m43.policy(2, 0, 10)
    _refused(m43.env, pol.with_user(m43.clerk).action_pause)
    assert pol.state == "active"


# ================================================================ B18 publication and scope
def test_b18_classification_publishes_to_the_part(m43):
    m43.consume(6, m43.month(-1))
    m43.consume(6, m43.month(-2))
    seg = (
        m43.env["fix.demand.segment"]
        .with_user(m43.planner)
        .create({"product_id": m43.prod.id, "part_id": m43.part.id})
    )
    assert seg.company_id == m43.company
    seg.with_user(m43.planner).action_classify()
    part = m43.part
    assert part.demand_abc_class == seg.abc_class and part.demand_xyz_class == seg.xyz_class
    assert part.demand_classified_on == seg.classified_on
    seg.with_user(m43.approver).write({"criticality": "critical"})
    assert part.demand_criticality == "critical"
    assert part.criticality == "medium", "the part's own criticality stays M15's master"
    _refused(m43.env, part.with_user(m43.clerk).write, {"demand_abc_class": "a"})


def test_b18_packs_are_scoped_to_the_callers_company(m43):
    other = m43.env["res.company"].create({"name": "M43 Other Co %s" % m43.tag})
    product = m43.env["product.product"].create({"name": "M43 Foreign %s" % m43.tag})
    m43.env["fix.demand.segment"].create(
        {"product_id": product.id, "company_id": other.id, "classified_on": fields.Date.today()}
    )
    m43.segment()
    env = m43.env(user=m43.planner.id)
    rows = ctl.new_part_intro(env)["rows"]
    assert product.display_name not in [r["product"] for r in rows]
    assert m43.prod.display_name in [r["product"] for r in rows]
    assert (
        m43.env["fix.demand.segment"]
        .with_user(m43.planner)
        .search_count([("product_id", "=", product.id)])
        == 0
    ), "the record rule hides it too"
    review = (
        m43.env["fix.demand.review"]
        .with_user(m43.planner)
        .create({"period": m43.period, "due_on": fields.Date.today()})
    )
    assert review.company_id == m43.company
    foreign = m43.env["fix.demand.review"].create(
        {"period": m43.period, "due_on": fields.Date.today(), "company_id": other.id}
    )
    assert not m43.env["fix.demand.review"].with_user(m43.planner).search([("id", "=", foreign.id)])


# ================================================================ B19 lead times
def test_b19_an_import_with_no_po_gives_a_lead_time_sample(m43):
    from odoo.addons.cd_demand_plan.models.fix_demand_common import observed_lead_times

    m43.part.sudo().write({"product_id": m43.prod.id})
    env = m43.env
    today = fields.Date.today()
    order = env["fix.import.order"].create(
        {
            "name": "M43-IMP-%s" % m43.tag,
            "operating_unit_id": m43.ou.id,
            "line_ids": [(0, 0, {"part_id": m43.part.id, "quantity": 5, "unit_price": 1})],
        }
    )
    assert observed_lead_times(env, m43.company, m43.prod, today - timedelta(days=60)) == []
    env.cr.execute(
        "UPDATE fix_import_order SET create_date = %s, received_on = %s WHERE id = %s",
        (today - timedelta(days=21), today, order.id),
    )
    order.invalidate_recordset()
    assert observed_lead_times(env, m43.company, m43.prod, today - timedelta(days=60)) == [21]
    # a policy reads it as observed, and the sample cannot be typed
    pol = _draft_policy(m43, lead_time_window_days=60)
    pol.with_user(m43.planner).action_refresh_from_history()
    assert pol.lead_time_samples == 1 and pol.lead_time_days == 21
    assert pol.lead_time_source == "observed"


def test_b19_a_po_linked_import_is_not_counted_twice(m43):
    from odoo.addons.cd_demand_plan.models.fix_demand_common import observed_lead_times

    m43.part.sudo().write({"product_id": m43.prod.id})
    env = m43.env
    today = fields.Date.today()
    order = env["fix.import.order"].create(
        {
            "name": "M43-IMP2-%s" % m43.tag,
            "operating_unit_id": m43.ou.id,
            "line_ids": [(0, 0, {"part_id": m43.part.id, "quantity": 5, "unit_price": 1})],
        }
    )
    po = env["fix.purchase.order"].create(
        {
            "vendor_id": m43.vendor.id,
            "operating_unit_id": m43.ou.id,
            "line_ids": [(0, 0, {"product_id": m43.prod.id, "qty_ordered": 5, "unit_price": 1})],
        }
    )
    po._guarded().write({"state": "sent"})
    grn = env["fix.purchase.receipt"].create(
        {
            "purchase_order_id": po.id,
            "line_ids": [(0, 0, {"po_line_id": po.line_ids.id, "qty_received": 5})],
        }
    )
    env.cr.execute(
        "UPDATE fix_import_order SET received_on = %s, m16_receipt_id = %s WHERE id = %s",
        (today, grn.id, order.id),
    )
    order.invalidate_recordset()
    assert observed_lead_times(env, m43.company, m43.prod, today - timedelta(days=60)) == []


# ================================================================ B20 reports
def test_b20_empty_messages_say_what_feeds_them(m43):
    env = m43.env(user=m43.clerk.id)
    for report, needle in (
        (ctl.stockout_causes, "active policy"),
        (ctl.excess_obsolescence, "active policy"),
        (ctl.van_par, "van location"),
        (ctl.accuracy_bias, "M15 spare part"),
    ):
        assert needle in report(env)["empty"], report.__name__


def test_b20_stockout_reads_a_plan_and_an_uncovered_policy(m43):
    plan = m43.ready_plan(forecast=10, stock=5, avg=2, std=0, lead=10)
    uncovered = m43.policy(2, 0, 10, loc=m43.loc2)
    rows = ctl.stockout_causes(m43.env(user=m43.planner.id))["rows"]
    assert plan.name in [r["plan"] for r in rows]
    bare = [r for r in rows if r["plan"] == "— (no plan)"]
    assert any(r["reorder_point"] == pytest.approx(uncovered.reorder_point) for r in bare)


def test_b20_excess_reads_an_uncovered_policy(m43):
    pol = m43.policy(1, 0, 5, review=5)
    m43.stock(500)
    rows = ctl.excess_obsolescence(m43.env(user=m43.planner.id))["rows"]
    row = next(
        r for r in rows if r["plan"] == "— (no plan)" and r["target_level"] == pol.target_level
    )
    assert row["excess"] == pytest.approx(500 - pol.target_level)


def test_b20_van_par_and_accuracy_fill_with_their_data(m43):
    van = m43.location("V", van=True)
    pol = m43.policy(2, 0, 10, loc=van)
    m43.stock(5, loc=van)
    row = next(
        r for r in ctl.van_par(m43.env(user=m43.planner.id))["rows"] if r["van"] == van.display_name
    )
    assert row["van_par"] == pytest.approx(pol.target_level) and row["top_up_qty"] > 0
    fc = m43.forecast(10, period=m43.last_period)
    m43.consume(8, m43.month(-1))
    rows = ctl.accuracy_bias(m43.env(user=m43.planner.id))["rows"]
    row = next(
        r for r in rows if r["period"] == fc.period and r["product"] == m43.prod.display_name
    )
    assert row["actual"] == pytest.approx(8.0)


# ================================================================ method labels
def test_method_options_not_built_are_labelled_and_never_set(m43):
    labels = dict(m43.env["fix.demand.forecast"]._fields["method"].selection)
    assert "not built" in labels["exponential"] and "not built" in labels["seasonal"]
    fc = (
        m43.env["fix.demand.forecast"]
        .with_user(m43.planner)
        .create(
            {
                "product_id": m43.prod.id,
                "part_id": m43.part.id,
                "period": m43.period,
                "location_id": m43.loc.id,
            }
        )
    )
    _refused(m43.env, fc.with_user(m43.planner).write, {"method": "seasonal"})
    assert fc.method == "manual"
