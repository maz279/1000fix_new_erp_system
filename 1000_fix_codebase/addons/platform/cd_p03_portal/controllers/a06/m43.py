# A06 · M43 Demand Planning & Replenishment — surfaces, packs and KPIs over the
# demand plans, forecasts, segmentation, policy versions, reviews, rebalancing
# and what-if scenarios.
#
# A06 audit (2026-11-03): every pack and KPI read with sudo().search([]) over
# every company, MAPE came from typed actuals and the rebalance KPI summed a
# flat "10% savings". Now: everything reads as the CALLER, filtered to the
# caller's allowed companies; forecast actuals and MAPE are M15 consumption
# (closed months only); plan figures are the computed position; rebalancing
# reports the stock value moved and the transfer cost, and claims no savings.
# Every workflow transition the screens offer is declared below; the models
# enforce the roles and the segregation of duties.

SURFACES = {
    "fix.demand.plan": {
        "order": "period_start desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_generate_pr", "action_reopen"},
    },
    "fix.demand.forecast": {
        "order": "period desc, id desc",
        "limit": 300,
        "actions": {
            "action_compute_forecast",
            "action_approve",
            "action_reset_draft",
            "action_publish",
        },
    },
    "fix.demand.segment": {"order": "product_id", "limit": 300, "actions": {"action_classify"}},
    "fix.demand.policy": {
        "order": "product_id, version desc",
        "limit": 300,
        "actions": {
            "action_refresh_from_history",
            "action_approve_provisional",
            "action_activate",
            "action_revise",
            "action_pause",
            "action_resume",
        },
    },
    "fix.demand.review": {
        "order": "period desc, id desc",
        "limit": 200,
        "actions": {"action_complete"},
    },
    "fix.demand.rebalance": {
        "order": "proposed_on desc, id desc",
        "limit": 200,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.demand.scenario": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_run"},
    },
    # capture audit 2026-11-16: the spec §10.1 records each page captures
    "fix.demand.adjustment": {
        "order": "period desc, id desc",
        "limit": 300,
        "actions": {"action_apply", "action_revoke"},
    },
    "fix.demand.driver": {
        "order": "period_from desc, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_retire"},
    },
    "fix.demand.service.target": {
        "order": "abc_class, effective_from desc, id desc",
        "limit": 200,
        "actions": {"action_activate"},
    },
    "fix.demand.lead.time": {
        "order": "product_id, vendor_id",
        "limit": 300,
        "actions": {"action_measure"},
    },
    "fix.demand.npi": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.demand.eol": {
        "order": "run_down_start desc, id desc",
        "limit": 200,
        "actions": {"action_approve", "action_approve_cfo", "action_reject"},
    },
    "fix.demand.van.par": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_compute", "action_approve", "action_reject"},
    },
    "fix.demand.network.policy": {
        "order": "part_id, id desc",
        "limit": 300,
        "actions": {"action_approve"},
    },
}


def _dhaka_today():
    from odoo.addons.cd_demand_plan.models.fix_demand_common import dhaka_today

    return dhaka_today()


def _in_range(period, date_from=None, date_to=None):
    """A06 ERP audit: the packs honour the date range (by forecast month)."""
    if date_from and period < str(date_from)[:7]:
        return False
    return not (date_to and period > str(date_to)[:7])


def accuracy_measures(forecasts):
    """M43-12: WAPE (sum |error| / sum actual: the months weighed by volume,
    and a zero-actual month counts), bias (sum (forecast - actual) / sum
    actual: positive = over-forecast) and the tracking signal (cumulative
    error / mean absolute deviation; beyond +/-4 the forecast is biased)."""
    actual = sum(f.actual_qty for f in forecasts)
    errors = [f.forecast_qty - f.actual_qty for f in forecasts]
    abs_sum = sum(abs(e) for e in errors)
    mad = abs_sum / len(errors) if errors else 0.0
    return {
        "wape_pct": round(abs_sum / actual * 100.0, 1) if actual else None,
        "bias_pct": round(sum(errors) / actual * 100.0, 1) if actual else None,
        "tracking_signal": round(sum(errors) / mad, 2) if mad else 0.0,
        "periods": len(errors),
    }


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty,
    }


def _company_domain(env):
    return [("company_id", "in", env.companies.ids)]


def _sel(rec, name):
    return dict(rec._fields[name].selection).get(rec[name])


def _forecasts(env):
    return env["fix.demand.forecast"].search(_company_domain(env))


def _measured(env):
    """Forecasts that can be measured: approved/published, tied to an M15
    part, for a month that has ended."""
    return _forecasts(env).filtered(
        lambda f: f.part_id and f.state in ("approved", "published") and f.period_closed
    )


def _policies(env, domain=None):
    return env["fix.demand.policy"].search(_company_domain(env) + (domain or []))


def _plans(env):
    return env["fix.demand.plan"].search(_company_domain(env))


def history_assembly(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _forecasts(env):
        rows.append(
            {
                "product": rec.product_id.display_name,
                "part": rec.part_id.display_name or "—",
                "period": rec.period,
                "window": rec.window_months,
                "history": rec.history_detail or "—",
                "statistical": round(rec.statistical_qty, 3),
                "forecast": round(rec.forecast_qty, 3),
                "actual": round(rec.actual_qty, 3),
                "method": _sel(rec, "method"),
                "source": _sel(rec, "source"),
                "state": _sel(rec, "state"),
            }
        )
    rows.sort(key=lambda r: (r["product"], r["period"]))
    return _pack(
        "History Assembly — M15 consumption behind each forecast",
        [
            "product",
            "part",
            "period",
            "window",
            "history",
            "statistical",
            "forecast",
            "actual",
            "method",
            "source",
            "state",
        ],
        {
            "product": "Product",
            "part": "M15 Part",
            "period": "Period",
            "window": "Window (months)",
            "history": "History Used",
            "statistical": "Statistical",
            "forecast": "Forecast",
            "actual": "Actual (M15)",
            "method": "Method",
            "source": "Source",
            "state": "State",
        },
        rows,
        [
            "The statistical forecast is the moving average of the M15 consumption of the "
            "window months before the period; a planner override keeps its rationale and is "
            "labelled Manual. The actual is the M15 consumption of the period."
        ],
        empty="No forecast periods recorded yet.",
    )


def accuracy_bias(env, date_from=None, date_to=None, **params):
    measured = _measured(env).filtered(lambda f: _in_range(f.period, date_from, date_to))
    rows = []
    by_product = {}
    for rec in measured:
        by_product.setdefault(rec.product_id, rec.browse())
        by_product[rec.product_id] |= rec
    for product, recs in by_product.items():
        m = accuracy_measures(recs)
        for rec in recs:
            rows.append(
                {
                    "product": product.display_name,
                    "period": rec.period,
                    "forecast": round(rec.forecast_qty, 3),
                    "actual": round(rec.actual_qty, 3),
                    "bias": round(rec.variance, 3),
                    "abs_error_pct": rec.abs_error_pct,
                    "tracking_signal": m["tracking_signal"],
                }
            )
    rows.sort(key=lambda r: (r["product"], r["period"]))
    total = accuracy_measures(measured)
    flagged = sorted(
        p.display_name
        for p, recs in by_product.items()
        if abs(accuracy_measures(recs)["tracking_signal"]) > 4
    )
    return _pack(
        "Accuracy & Bias (WAPE) — forecast against M15 consumption",
        ["product", "period", "forecast", "actual", "bias", "abs_error_pct", "tracking_signal"],
        {
            "product": "Product",
            "period": "Period",
            "forecast": "Forecast",
            "actual": "Actual (M15)",
            "bias": "Error (actual−forecast)",
            "abs_error_pct": "Abs Error % of Actual",
            "tracking_signal": "Tracking Signal (product)",
        },
        rows,
        [
            "WAPE %s, bias %s across %d closed month(s) (M43-12: weighted by actual volume; a "
            "month with no consumption has no percent error of its own but its error counts in "
            "the WAPE). Actuals are M15 consumption and cannot be typed."
            % (
                "%.1f%%" % total["wape_pct"] if total["wape_pct"] is not None else "n/a",
                "%+.1f%%" % total["bias_pct"] if total["bias_pct"] is not None else "n/a",
                total["periods"],
            ),
            "Tracking signal beyond ±4 (biased forecast): %s." % (", ".join(flagged) or "none"),
        ],
        empty="Nothing to measure yet. This reads approved or published forecasts that name an "
        "M15 spare part, for a month that has ended; a forecast without a part has no actuals.",
    )


def lead_time(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _policies(env):
        rows.append(
            {
                "policy": "%s v%d" % (rec.name, rec.version),
                "product": rec.product_id.display_name,
                "location": rec.location_id.display_name or "—",
                "avg_daily": round(rec.avg_daily_demand, 2),
                "stddev": round(rec.demand_stddev, 2),
                "lead_time_days": rec.lead_time_days,
                "lead_time_source": _sel(rec, "lead_time_source") or "—",
                "observed_lead_time": round(rec.observed_lead_time_days, 1),
                "service_level_pct": rec.service_level_pct,
                "safety_stock": round(rec.safety_stock, 2),
                "reorder_point": round(rec.reorder_point, 2),
                "target_level": round(rec.target_level, 2),
                "state": _sel(rec, "state"),
            }
        )
    rows.sort(key=lambda r: -r["reorder_point"])
    return _pack(
        "Lead-Time Modelling — safety stock, ROP and target per policy version",
        [
            "policy",
            "product",
            "location",
            "avg_daily",
            "stddev",
            "lead_time_days",
            "lead_time_source",
            "observed_lead_time",
            "service_level_pct",
            "safety_stock",
            "reorder_point",
            "target_level",
            "state",
        ],
        {
            "policy": "Policy",
            "product": "Product",
            "location": "Location",
            "avg_daily": "Avg Daily",
            "stddev": "Std Dev",
            "lead_time_days": "Lead Time",
            "lead_time_source": "Lead-Time Source",
            "observed_lead_time": "Observed (M16)",
            "service_level_pct": "Service %",
            "safety_stock": "Safety Stock",
            "reorder_point": "Reorder Point",
            "target_level": "Target",
            "state": "State",
        },
        rows,
        [
            "Average daily demand and its deviation come from M15 consumption; the lead time is "
            "the observed M16 PO-sent-to-receipt time unless overridden with a rationale "
            "(typed when there is no receipt history). Safety stock = "
            "z × σ × √lead time; ROP = avg daily × lead time + safety stock; target = ROP + "
            "avg daily × review period."
        ],
        empty="No demand policies yet.",
    )


def van_par(env, date_from=None, date_to=None, **params):
    from odoo.addons.cd_demand_plan.models.fix_demand_common import on_hand

    rows = []
    for rec in _policies(env, [("state", "=", "active")]):
        loc = rec.location_id
        if not loc or not (loc.is_van_location or loc.is_van_stock):
            continue
        stock = on_hand(env, rec.company_id, rec.part_id, loc) if rec.part_id else 0.0
        rows.append(
            {
                "product": rec.product_id.display_name,
                "van": loc.display_name,
                "reorder_point": round(rec.reorder_point, 2),
                "safety_stock": round(rec.safety_stock, 2),
                "van_par": round(rec.target_level, 2),
                "on_van": round(stock, 2),
                "top_up_qty": round(max(rec.target_level - stock, 0.0), 2),
            }
        )
    rows.sort(key=lambda r: -r["van_par"])
    return _pack(
        "Van-Stock Par Calculation — the van policy's target level",
        ["product", "van", "reorder_point", "safety_stock", "van_par", "on_van", "top_up_qty"],
        {
            "product": "Product",
            "van": "Van",
            "reorder_point": "ROP",
            "safety_stock": "Safety Stock",
            "van_par": "Van Par",
            "on_van": "On Van (M15)",
            "top_up_qty": "Top-up",
        },
        rows,
        [
            "Van par is the target level of the van location's active policy (from its M15 "
            "demand and variability); the top-up is par less the owned stock on the van."
        ],
        empty="No van to size yet. This reads active policies whose stock location is a van "
        "location (M15 location type Van); activate a policy for a van to see its par.",
    )


def accuracy_by_class(env, date_from=None, date_to=None, **params):
    segments = env["fix.demand.segment"].search(_company_domain(env))
    forecasts = _measured(env).filtered(lambda f: _in_range(f.period, date_from, date_to))
    buckets = {}
    for segment in segments:
        key = segment.abc_class.upper() if segment.classified_on else "Unclassified"
        recs = forecasts.filtered(lambda f, p=segment.product_id: f.product_id.id == p.id)
        row = buckets.setdefault(
            key, {"abc": key, "products": 0, "periods": 0, "recs": forecasts.browse()}
        )
        row["products"] += 1
        row["periods"] += len(recs)
        row["recs"] |= recs
    rows = []
    for row in buckets.values():
        m = accuracy_measures(row.pop("recs"))
        row["mape_pct"] = m["wape_pct"] if m["wape_pct"] is not None else 0.0
        row["bias_pct"] = m["bias_pct"] if m["bias_pct"] is not None else 0.0
        rows.append(row)
    rows.sort(key=lambda r: r["abc"])
    return _pack(
        "Forecast Accuracy by Class — WAPE and bias per ABC class",
        ["abc", "products", "periods", "mape_pct", "bias_pct"],
        {
            "abc": "ABC Class",
            "products": "Products",
            "periods": "Periods",
            "mape_pct": "WAPE %",
            "bias_pct": "Bias %",
        },
        rows,
        [
            "Classes are computed from M15 consumption value; only approved forecasts of "
            "closed months enter the WAPE (weighted absolute error over actual volume)."
        ],
        empty="No segmentation/actuals yet.",
    )


def _unplanned_policies(env, plans):
    """Active policies no plan covers: their stock is still a planning exposure,
    and a report fed by plans alone would hide it."""
    planned = {(p.part_id.id, p.location_id.id) for p in plans}
    return _policies(env, [("state", "=", "active")]).filtered(
        lambda r: r.part_id and r.location_id and (r.part_id.id, r.location_id.id) not in planned
    )


def stockout_causes(env, date_from=None, date_to=None, **params):
    from odoo.addons.cd_demand_plan.models.fix_demand_common import on_hand, on_order

    rows = []
    plans = _plans(env)
    for policy in _unplanned_policies(env, plans):
        stock = on_hand(env, policy.company_id, policy.part_id, policy.location_id)
        incoming = on_order(env, policy.company_id, policy.product_id)
        projected = round(stock + incoming, 3)
        if projected > policy.reorder_point:
            continue
        rows.append(
            {
                "plan": "— (no plan)",
                "product": policy.product_id.display_name,
                "forecast": 0.0,
                "stock": round(stock, 2),
                "on_order": round(incoming, 2),
                "projected": round(projected, 2),
                "reorder_point": round(policy.reorder_point, 2),
                "recommended": 0.0,
                "cause": (
                    "stock below safety stock"
                    if stock <= policy.safety_stock
                    else "at or below ROP, no plan"
                ),
                "state": _sel(policy, "state"),
            }
        )
    for plan in plans:
        if not plan.policy_id or plan.projected_stock > plan.reorder_point:
            continue
        cause = (
            "stock below safety stock"
            if plan.current_stock <= plan.safety_stock
            else "projected below ROP"
        )
        rows.append(
            {
                "plan": plan.name,
                "product": plan.product_id.display_name,
                "forecast": round(plan.forecast_quantity, 2),
                "stock": round(plan.current_stock, 2),
                "on_order": round(plan.on_order_qty, 2),
                "projected": round(plan.projected_stock, 2),
                "reorder_point": round(plan.reorder_point, 2),
                "recommended": round(plan.recommended_order, 2),
                "cause": cause,
                "state": _sel(plan, "state"),
            }
        )
    rows.sort(key=lambda r: r["projected"])
    return _pack(
        "Stockout Risk — plans projected at or below the reorder point",
        [
            "plan",
            "product",
            "forecast",
            "stock",
            "on_order",
            "projected",
            "reorder_point",
            "recommended",
            "cause",
            "state",
        ],
        {
            "plan": "Plan",
            "product": "Product",
            "forecast": "Forecast",
            "stock": "Stock (M15)",
            "on_order": "On Order",
            "projected": "Projected",
            "reorder_point": "ROP",
            "recommended": "Recommended",
            "cause": "Cause",
            "state": "State",
        },
        rows,
        [
            "Projected = M15 owned stock + open M16 orders − approved forecast demand of the "
            "plan period. An active policy no plan covers is read at stock + open orders."
        ],
        empty="No stockout exposure. This reads plans that name an M15 part and location with an "
        "active policy, and active policies no plan covers; a row appears when the projected "
        "stock is at or below the reorder point.",
    )


def excess_obsolescence(env, date_from=None, date_to=None, **params):
    from odoo.addons.cd_demand_plan.models.fix_demand_common import on_hand

    rows = []
    plans = _plans(env)
    for policy in _unplanned_policies(env, plans):
        stock = on_hand(env, policy.company_id, policy.part_id, policy.location_id)
        if stock <= policy.target_level:
            continue
        rows.append(
            {
                "plan": "— (no plan)",
                "product": policy.product_id.display_name,
                "stock": round(stock, 2),
                "forecast": 0.0,
                "target_level": round(policy.target_level, 2),
                "excess": round(stock - policy.target_level, 2),
                "state": _sel(policy, "state"),
            }
        )
    for plan in plans:
        if not plan.policy_id or plan.current_stock <= plan.target_level:
            continue
        rows.append(
            {
                "plan": plan.name,
                "product": plan.product_id.display_name,
                "stock": round(plan.current_stock, 2),
                "forecast": round(plan.forecast_quantity, 2),
                "target_level": round(plan.target_level, 2),
                "excess": round(plan.current_stock - plan.target_level, 2),
                "state": _sel(plan, "state"),
            }
        )
    rows.sort(key=lambda r: -r["excess"])
    return _pack(
        "Excess & Obsolescence Exposure — stock above the target level",
        ["plan", "product", "stock", "forecast", "target_level", "excess", "state"],
        {
            "plan": "Plan",
            "product": "Product",
            "stock": "Stock (M15)",
            "forecast": "Forecast",
            "target_level": "Target",
            "excess": "Excess",
            "state": "State",
        },
        rows,
        [
            "Excess = M15 owned stock − the policy's target level. Ageing by lot remains "
            "M15's report; this is the planning exposure. An active policy no plan covers is "
            "included."
        ],
        empty="No excess. This reads plans that name an M15 part and location with an active "
        "policy, and active policies no plan covers; a row appears when M15 owned stock is above "
        "the policy's target level.",
    )


def rebalancing_value(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in env["fix.demand.rebalance"].search(_company_domain(env)):
        rows.append(
            {
                "proposal": rec.name,
                "product": rec.product_id.display_name,
                "from": rec.source_location_id.display_name or rec.source_branch or "—",
                "to": rec.target_location_id.display_name or rec.target_branch or "—",
                "qty": round(rec.qty, 3),
                "stock_value": round(rec.stock_value, 2),
                "transfer_cost": round(rec.transfer_cost, 2),
                "benefit": round(rec.benefit_value, 2),
                "net_benefit": round(rec.net_benefit, 2),
                "transfer": rec.transfer_id.name or "—",
                "state": _sel(rec, "state"),
            }
        )
    rows.sort(key=lambda r: -r["stock_value"])
    approved = [r for r in rows if r["state"] == "Approved"]
    return _pack(
        "Rebalancing — stock value moved and transfer cost",
        [
            "proposal",
            "product",
            "from",
            "to",
            "qty",
            "stock_value",
            "transfer_cost",
            "benefit",
            "net_benefit",
            "transfer",
            "state",
        ],
        {
            "proposal": "Proposal",
            "product": "Product",
            "from": "From",
            "to": "To",
            "qty": "Qty",
            "stock_value": "Stock Value",
            "transfer_cost": "Transfer Cost",
            "benefit": "Est. Benefit",
            "net_benefit": "Net Benefit",
            "transfer": "M15 Transfer",
            "state": "State",
        },
        rows,
        [
            "Approved proposals move BDT %.2f of stock at an estimated transfer cost of BDT "
            "%.2f. A proposal is approved only where its estimated benefit exceeds the transfer "
            "cost (BRU-DPL-13); the benefit is the proposer's estimate, not a measured saving."
            % (
                sum(r["stock_value"] for r in approved),
                sum(r["transfer_cost"] for r in approved),
            )
        ],
        totals={
            "proposal": "Total",
            "stock_value": round(sum(r["stock_value"] for r in rows), 2),
            "transfer_cost": round(sum(r["transfer_cost"] for r in rows), 2),
        },
        empty="No rebalancing proposals yet.",
    )


def new_part_intro(env, date_from=None, date_to=None, **params):
    segments = env["fix.demand.segment"].search(_company_domain(env))
    forecasts = _forecasts(env)
    rows = []
    for segment in segments:
        product_forecasts = forecasts.filtered(
            lambda f, p=segment.product_id: f.product_id.id == p.id
        )
        computed = product_forecasts.filtered(lambda f: f.source == "history")
        rows.append(
            {
                "product": segment.product_id.display_name,
                "segment": (
                    "%s/%s" % (segment.abc_class.upper(), segment.xyz_class.upper())
                    if segment.classified_on
                    else "unclassified"
                ),
                "criticality": _sel(segment, "criticality"),
                "history_forecasts": len(computed),
                "manual_forecasts": len(product_forecasts) - len(computed),
                "status": (
                    "established" if computed else "new / insufficient M15 history (manual only)"
                ),
            }
        )
    rows.sort(key=lambda r: (r["history_forecasts"], r["product"]))
    return _pack(
        "New-Part Introduction — history depth per product",
        [
            "product",
            "segment",
            "criticality",
            "history_forecasts",
            "manual_forecasts",
            "status",
        ],
        {
            "product": "Product",
            "segment": "Segment",
            "criticality": "Criticality",
            "history_forecasts": "History Forecasts",
            "manual_forecasts": "Manual Forecasts",
            "status": "Status",
        },
        rows,
        [
            "A product whose forecasts are all manual has no M15 history the moving average "
            "could use; it is labelled new rather than forecast as if established."
        ],
        empty="No segmentation rows yet.",
    )


REPORTS = {
    "history_assembly": history_assembly,
    "accuracy_bias": accuracy_bias,
    "lead_time": lead_time,
    "van_par": van_par,
    "accuracy_by_class": accuracy_by_class,
    "stockout_causes": stockout_causes,
    "excess_obsolescence": excess_obsolescence,
    "rebalancing_value": rebalancing_value,
    "new_part_intro": new_part_intro,
}


def kpis(env):
    forecasts = _forecasts(env)
    measured = _measured(env)
    active = _policies(env, [("state", "=", "active")])
    plans = _plans(env)
    rebalances = env["fix.demand.rebalance"].search(
        [*_company_domain(env), ("state", "=", "approved")]
    )
    wape = accuracy_measures(measured)["wape_pct"]
    return {
        "forecasts_pending": len(forecasts.filtered(lambda f: f.state == "draft")),
        # M43-12: the headline error is the WAPE (key kept for the screen)
        "mape_pct": wape if wape is not None else 0.0,
        "policies_active": len(active),
        "planned_orders": len(plans.filtered(lambda p: p.state == "approved")),
        "rebalance_value_moved": round(sum(rebalances.mapped("stock_value")), 2),
        # M43-13: the ACHIEVED fill rate, not the average of the targets
        "service_level_avg": achieved_fill_rate(env, active)["fill_rate_pct"],
    }


def achieved_fill_rate(env, policies, days=90):
    """M43-13: the share of demand for policy-managed parts that M15 served
    from stock over the last `days` Dhaka days: consumed / (consumed +
    backordered + censored unmet demand recorded by the planner)."""
    from datetime import timedelta

    from odoo.addons.cd_demand_plan.models.fix_demand_common import _dt, period_of

    if not policies:
        return {"fill_rate_pct": 0.0, "served": 0.0, "unserved": 0.0}
    today = _dhaka_today()
    start = _dt(today - timedelta(days=days))
    parts = policies.mapped("part_id")
    companies = policies.mapped("company_id")
    served = sum(
        env["fix.stock.consumption"]
        .sudo()
        .search(
            [
                ("company_id", "in", companies.ids),
                ("product_id", "in", parts.ids),
                ("state", "=", "consumed"),
                ("consumed_at", ">=", start),
            ]
        )
        .mapped("quantity")
    )
    unserved = 0.0
    if "fix.stock.backorder" in env:
        unserved += sum(
            env["fix.stock.backorder"]
            .sudo()
            .search(
                [
                    ("company_id", "in", companies.ids),
                    ("part_id", "in", parts.ids),
                    ("state", "!=", "cancelled"),
                    ("create_date", ">=", start),
                ]
            )
            .mapped("qty")
        )
    first = period_of(today - timedelta(days=days))
    for adj in (
        env["fix.demand.adjustment"]
        .sudo()
        .search(
            [
                ("company_id", "in", companies.ids),
                ("part_id", "in", parts.ids),
                ("adjustment_type", "=", "censored"),
                ("state", "=", "applied"),
                ("period", ">=", first),
            ]
        )
    ):
        unserved += max((adj.adjusted_qty or 0.0) - (adj.original_qty or 0.0), 0.0)
    demand = served + unserved
    return {
        "fill_rate_pct": round(served / demand * 100.0, 1) if demand else 0.0,
        "served": round(served, 3),
        "unserved": round(unserved, 3),
    }
