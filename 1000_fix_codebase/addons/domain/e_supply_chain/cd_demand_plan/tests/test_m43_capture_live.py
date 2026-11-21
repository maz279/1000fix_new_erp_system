"""M43 capture audit (2026-11-16): the records each sub-module page now
captures, driven live through the ORM and the P03 endpoints as the real roles.
Every test runs the proper path and then attacks the control. Fixtures in
conftest.py; the transaction is rolled back."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (UserError, ValidationError, AccessError, IntegrityError)
CFO = "cd_entity_config.group_dofa_tier_4"


def _refused(env, fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        fn(*args, **kw)
        env.flush_all()


def _history(m43, *qtys):
    """Consumption in the months before this one, oldest first."""
    for i, qty in enumerate(qtys):
        if qty:
            m43.consume(qty, m43.month(i - len(qtys)))


def _period(m43, delta):
    d = m43.month(delta)
    return "%04d-%02d" % (d.year, d.month)


def _adjustment(m43, user=None, **kw):
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "location_id": m43.loc.id,
        "period": _period(m43, -1),
        "adjustment_type": "outlier_exclude",
        "reason": "One-off 200-unit project order",
    }
    vals.update(kw)
    return m43.env["fix.demand.adjustment"].with_user(user or m43.planner).create(vals)


def _forecast(m43, **kw):
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "location_id": m43.loc.id,
        "period": m43.period,
        "window_months": 3,
    }
    vals.update(kw)
    return m43.env["fix.demand.forecast"].with_user(m43.planner).create(vals)


# ============================================================ page 1 overlay
def test_page1_an_applied_outlier_is_an_overlay_the_forecast_uses(m43):
    _history(m43, 6, 6, 200)  # a project spike last month
    adj = _adjustment(m43, adjustment_type="outlier_replace", adjusted_qty=6)
    adj.with_user(m43.planner).action_apply()
    assert adj.state == "applied" and adj.original_qty == pytest.approx(200)
    assert adj.applied_by_id == m43.planner

    fc = _forecast(m43)
    fc.with_user(m43.planner).action_compute_forecast()
    assert fc.statistical_qty == pytest.approx(6.0)
    assert "%s: 6*" % _period(m43, -1) in fc.history_detail
    # the M15 source is untouched
    consumed = m43.env["fix.stock.consumption"].search(
        [("product_id", "=", m43.part.id), ("quantity", "=", 200)]
    )
    assert consumed and consumed.state == "consumed"


def test_page1_exclude_and_reclassify_drop_the_month(m43):
    _history(m43, 6, 6, 120)
    adj = _adjustment(m43, adjustment_type="reclassify", demand_stream="project")
    adj.with_user(m43.planner).action_apply()
    assert adj.adjusted_qty == 0.0
    fc = _forecast(m43)
    fc.with_user(m43.planner).action_compute_forecast()
    assert fc.statistical_qty == pytest.approx(4.0)


def test_page1_treatment_rules(m43):
    _history(m43, 6, 6, 6)
    _refused(m43.env, _adjustment, m43, reason=" ", match="reason")
    _refused(m43.env, _adjustment, m43, adjustment_type="reclassify", match="stream")
    up = _adjustment(m43, adjustment_type="outlier_replace", adjusted_qty=10)
    _refused(m43.env, up.with_user(m43.planner).action_apply, match="lowers")
    low = _adjustment(m43, adjustment_type="censored", adjusted_qty=3, period=_period(m43, -2))
    _refused(m43.env, low.with_user(m43.planner).action_apply, match="raises")
    none = _adjustment(m43, period=_period(m43, -6))
    _refused(m43.env, none.with_user(m43.planner).action_apply, match="no M15 consumption")


def test_page1_one_applied_per_month_revoke_and_forgery(m43):
    _history(m43, 6, 6, 50)
    first = _adjustment(m43)
    first.with_user(m43.planner).action_apply()
    second = _adjustment(m43, adjustment_type="outlier_replace", adjusted_qty=6)
    _refused(m43.env, second.with_user(m43.planner).action_apply, match="revoke it first")
    _refused(m43.env, first.with_user(m43.planner).write, {"adjusted_qty": 99})
    _refused(m43.env, first.with_user(m43.planner).action_revoke, match="why")
    first.with_user(m43.planner).action_revoke(reason="Was a real demand")
    assert first.state == "revoked"
    second.with_user(m43.planner).action_apply()
    forged = _adjustment(m43, period=_period(m43, -2))
    _refused(m43.env, forged.with_user(m43.planner).write, {"state": "applied"})
    _refused(m43.env, forged.with_user(m43.clerk).action_apply, match="Planner")


# ============================================================ page 3 drivers
def test_page3_an_active_driver_shows_on_the_forecast_and_an_override_cites_it(m43):
    drv = (
        m43.env["fix.demand.driver"]
        .with_user(m43.planner)
        .create(
            {
                "driver_type": "campaign",
                "source_ref": "M09 campaign WC-1",
                "product_id": m43.prod.id,
                "period_from": m43.period,
                "period_to": m43.period,
                "expected_impact_pct": 40,
                "basis": "Recall of 300 units",
            }
        )
    )
    fc = _forecast(m43)
    assert fc.driver_impact_pct == 0.0
    drv.with_user(m43.planner).action_activate()
    fc.invalidate_recordset()
    assert fc.driver_impact_pct == pytest.approx(40.0) and drv.name in fc.driver_note
    _refused(m43.env, fc.with_user(m43.planner).write, {"override_driver_id": drv.id})
    fc.with_user(m43.planner).write(
        {
            "has_override": True,
            "override_qty": 14,
            "override_rationale": "Campaign",
            "override_driver_id": drv.id,
        }
    )
    fc.with_user(m43.approver).action_approve()
    _refused(m43.env, fc.with_user(m43.planner).write, {"override_driver_id": False})


def test_page3_driver_rules(m43):
    base = {
        "driver_type": "seasonality",
        "product_id": m43.prod.id,
        "period_from": "2026-12",
        "period_to": "2026-11",
        "expected_impact_pct": 10,
        "basis": "Eid",
    }
    Driver = m43.env["fix.demand.driver"].with_user(m43.planner)
    _refused(m43.env, Driver.create, base, match="ends on or after")
    _refused(m43.env, Driver.create, dict(base, period_to="2027-01", expected_impact_pct=0))


# ============================================================ page 5 targets
def _target(m43, user=None, **kw):
    vals = {"abc_class": "b", "target_pct": "98", "rationale": "B-class at branch"}
    vals.update(kw)
    return m43.env["fix.demand.service.target"].with_user(user or m43.planner).create(vals)


def test_page5_a_policy_below_its_segment_target_is_not_activated(m43):
    m43.segment(abc="b")
    tgt = _target(m43)
    _refused(m43.env, tgt.with_user(m43.planner).action_activate, match="Approver")
    tgt.with_user(m43.approver).action_activate()
    assert tgt.state == "active" and tgt.approved_by_id == m43.approver

    pol = m43.policy(2.0, 1.0, 10, service="95", state="draft")
    assert "98%" in pol.segment_target
    _refused(m43.env, pol.with_user(m43.approver).action_activate, match="target")
    pol.sudo()._guarded().write({"service_level_pct": "98"})
    pol.with_user(m43.planner).action_activate()
    assert pol.state == "active"


def test_page5_targets_supersede_and_keep_two_persons(m43):
    first = _target(m43)
    first.with_user(m43.approver).action_activate()
    second = _target(m43, target_pct="99")
    second.with_user(m43.approver2).action_activate()
    first.invalidate_recordset()
    assert first.state == "superseded" and second.state == "active"
    both = m43.user(
        "both5",
        ["cd_demand_plan.group_fix_demand_planner", "cd_demand_plan.group_fix_demand_approver"],
    )
    own = _target(m43, user=both, abc_class="a")
    _refused(m43.env, own.with_user(both).action_activate, match="segregation")


# ============================================================ page 6 lead time
def test_page6_measures_actual_receipts_beside_the_quoted_figure(m43):
    m43.part.sudo().write({"product_id": m43.prod.id})
    env = m43.env
    lt = (
        env["fix.demand.lead.time"]
        .with_user(m43.planner)
        .create({"product_id": m43.prod.id, "vendor_id": m43.vendor.id, "quoted_days": 14})
    )
    _refused(env, lt.with_user(m43.planner).action_measure, match="no posted receipt")
    assert lt.state == "quoted"
    today = fields.Date.today()
    order = env["fix.import.order"].create(
        {
            "name": "M43-LT-%s" % m43.tag,
            "operating_unit_id": m43.ou.id,
            "supplier_id": m43.vendor.id,
            "line_ids": [(0, 0, {"part_id": m43.part.id, "quantity": 5, "unit_price": 1})],
        }
    )
    env.cr.execute(
        "UPDATE fix_import_order SET create_date = %s, received_on = %s WHERE id = %s",
        (today - timedelta(days=30), today, order.id),
    )
    order.invalidate_recordset()
    lt.with_user(m43.planner).action_measure()
    assert lt.state == "measured" and lt.sample_count == 1
    assert lt.mean_days == pytest.approx(30) and lt.p95_days == pytest.approx(30)
    assert lt.supply_source == "import" and lt.variance_days == pytest.approx(16)
    _refused(env, lt.with_user(m43.planner).write, {"mean_days": 5})
    # a new supplier is a new key: the measurement belongs to the old one
    other = env["res.partner"].create({"name": "M43 Other %s" % m43.tag})
    lt.with_user(m43.planner).write({"vendor_id": other.id})
    assert lt.state == "quoted" and lt.sample_count == 0
    _refused(
        env,
        env["fix.demand.lead.time"].with_user(m43.planner).create,
        {"product_id": m43.prod.id, "vendor_id": other.id, "quoted_days": 3},
    )


# ============================================================ page 7 NPI / EOL
def test_page7_new_part_recommendation(m43):
    Npi = m43.env["fix.demand.npi"].with_user(m43.planner)
    vals = {
        "product_id": m43.prod.id,
        "part_id": m43.part.id,
        "recommended_initial_qty": 4,
        "rationale": "Launch of model X",
    }
    bare = Npi.create(vals)
    _refused(m43.env, bare.with_user(m43.approver).action_approve, match="nothing it is based on")
    npi = Npi.create(dict(vals, installed_base_ref="M17: 1,200 units sold"))
    _refused(m43.env, npi.with_user(m43.planner).action_approve, match="Approver")
    npi.with_user(m43.approver).action_approve()
    assert npi.state == "approved" and npi.approved_by_id == m43.approver
    _history(m43, 6, 6, 6)
    late = Npi.create(dict(vals, installed_base_ref="x"))
    _refused(m43.env, late.with_user(m43.approver).action_approve, match="already has M15 history")


def _eol(m43, qty, user=None):
    return (
        m43.env["fix.demand.eol"]
        .with_user(user or m43.planner)
        .create(
            {
                "part_id": m43.part.id,
                "run_down_start": date.today(),
                "projected_remaining_demand": qty,
                "last_time_buy_qty": qty,
                "rationale": "OEM ends supply",
            }
        )
    )


def test_page7_last_time_buy_needs_the_cfo_above_the_threshold(m43):
    m43.part.sudo().write({"unit_cost": 1000.0})
    small = _eol(m43, 10)  # 10,000 BDT
    small.with_user(m43.approver).action_approve()
    assert small.state == "approved" and not small.needs_cfo

    big = _eol(m43, 1000)  # 1,000,000 BDT
    assert big.needs_cfo and big.last_time_buy_value == pytest.approx(1_000_000)
    big.with_user(m43.approver).action_approve()
    assert big.state == "cfo"
    _refused(m43.env, big.with_user(m43.approver2).action_approve_cfo, match="CFO|Tier|role")
    cfo_and_approver = m43.user("cfoappr", [CFO])
    m43.approver.sudo().write({"group_ids": [(4, m43.env.ref(CFO).id)]})
    _refused(m43.env, big.with_user(m43.approver).action_approve_cfo, match="segregation")
    big.with_user(cfo_and_approver).action_approve_cfo()
    assert big.state == "approved" and big.cfo_approved_by_id == cfo_and_approver


def test_page7_last_time_buy_rules(m43):
    m43.part.sudo().write({"unit_cost": 0.0})
    plan = _eol(m43, 5)
    _refused(m43.env, plan.with_user(m43.approver).action_approve, match="standard cost")
    _refused(m43.env, plan.with_user(m43.approver).action_reject, match="why")
    plan.with_user(m43.approver).action_reject(reason="Successor ready")
    assert plan.state == "rejected"
    _refused(m43.env, plan.with_user(m43.planner).write, {"last_time_buy_qty": 9})


# ============================================================ page 8 network / van par
def _network(m43, user=None, **kw):
    vals = {
        "part_id": m43.part.id,
        "central_stock": True,
        "van_stock": False,
        "rationale": "Low density: central and one branch",
        "location_ids": [(6, 0, [m43.loc2.id])],
    }
    vals.update(kw)
    return m43.env["fix.demand.network.policy"].with_user(user or m43.planner).create(vals)


def test_page8_network_policy_refuses_a_policy_where_the_part_is_not_held(m43):
    net = _network(m43)
    _refused(m43.env, net.with_user(m43.planner).action_approve, match="Approver")
    net.with_user(m43.approver).action_approve()
    m43.segment(abc="c")
    # a branch store the policy does not list (m43.loc is a central store,
    # which this policy holds)
    pol = m43.policy(2.0, 1.0, 10, state="draft", loc=m43.location("N"))
    _refused(m43.env, pol.with_user(m43.planner).action_activate, match="does not hold")
    ok = m43.policy(2.0, 1.0, 10, state="draft", loc=m43.loc2)
    ok.with_user(m43.planner).action_activate()
    assert ok.state == "active"
    van = m43.location("V", van=True)
    _refused(m43.env, _network, m43, location_ids=[(6, 0, [van.id])], match="branch")


def _van_par(m43, van, user=None, **kw):
    vals = {"van_location_id": van.id, "part_id": m43.part.id, "replenish_days": 7}
    vals.update(kw)
    return m43.env["fix.demand.van.par"].with_user(user or m43.planner).create(vals)


def test_page8_van_par_is_computed_approved_and_published_to_m15(m43):
    van = m43.location("V", van=True)
    today = date.today()
    for back in range(1, 31):
        m43.consume(1, today - timedelta(days=back), loc=van)
    par = _van_par(m43, van)
    assert par.technician_id == m43.tech
    _refused(m43.env, par.with_user(m43.approver).action_approve, match="compute it first")
    par.with_user(m43.planner).action_compute()
    assert par.suggested_min > 0 and par.suggested_max > par.suggested_min
    assert (par.min_qty, par.max_qty) == (par.suggested_min, par.suggested_max)
    _refused(m43.env, par.with_user(m43.planner).write, {"suggested_min": 1})
    _refused(m43.env, par.with_user(m43.planner).action_approve, match="Approver")
    par.with_user(m43.approver).action_approve()
    assert par.state == "applied" and par.published_rule_id
    rule = par.published_rule_id.sudo()
    assert rule.location_id == van and rule.min_qty == pytest.approx(par.min_qty)
    assert rule.max_qty == pytest.approx(par.max_qty)


def test_page8_van_par_deviation_network_and_two_persons(m43):
    van = m43.location("W", van=True)
    m43.consume(3, date.today() - timedelta(days=2), loc=van)
    par = _van_par(m43, van)
    par.with_user(m43.planner).action_compute()
    par.with_user(m43.planner).write({"max_qty": par.suggested_max + 5})
    _refused(m43.env, par.with_user(m43.approver).action_approve, match="record why")
    par.with_user(m43.planner).write({"deviation_reason": "First-time-fix campaign"})
    _network(m43).with_user(m43.approver).action_approve()  # van_stock False
    _refused(m43.env, par.with_user(m43.approver).action_approve, match="does not hold")
    _refused(m43.env, _van_par, m43, m43.loc, match="van stock location")
    both = m43.user(
        "both8",
        ["cd_demand_plan.group_fix_demand_planner", "cd_demand_plan.group_fix_demand_approver"],
    )
    own = _van_par(m43, van, user=both)
    own.with_user(both).action_compute()
    _refused(m43.env, own.with_user(both).action_approve, match="segregation")


# ============================================================ the P03 endpoints
def test_the_workspace_form_creates_each_record_and_cannot_type_a_stamp(m43, p03):
    p03.as_user(m43.planner)
    out = p03.write(
        model="fix.demand.adjustment",
        record_id=None,
        values={
            "product_id": m43.prod.id,
            "part_id": m43.part.id,
            "period": _period(m43, -1),
            "adjustment_type": "outlier_exclude",
            "reason": "Project order",
            "original_qty": 999,
        },
    )
    assert "error" not in out, out
    adj = m43.env["fix.demand.adjustment"].search([("reason", "=", "Project order")])
    assert adj and adj.original_qty == 0.0, "a measured figure is never typed"
    out = p03.write(model="fix.demand.adjustment", record_id=adj.id, values={"state": "applied"})
    adj.invalidate_recordset()
    assert adj.state == "draft"
    out = p03.write(
        model="fix.demand.lead.time",
        record_id=None,
        values={"product_id": m43.prod.id, "vendor_id": m43.vendor.id, "quoted_days": 9},
    )
    assert "error" not in out, out
    a = p03.action(model="fix.demand.lead.time", ids=[out.get("id") or 0], method="action_measure")
    assert "error" in a  # no receipts: refused with the reason, nothing written
    p03.as_user(m43.clerk)
    c = p03.action(model="fix.demand.adjustment", ids=[adj.id], method="action_apply")
    assert "error" in c
