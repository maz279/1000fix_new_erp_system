# A06 · M43 Demand Planning & Replenishment — surfaces, packs and KPIs over the
# existing demand plans plus forecasts, segmentation, safety-stock policy,
# reviews, rebalancing and what-if scenarios. MAPE uses forecast vs recorded
# actuals; stock-out causes read the recorded plan gaps.

SURFACES = {
    "fix.demand.plan": {
        "order": "period_start desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_generate_pr"},
    },
    "fix.demand.forecast": {
        "order": "period desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_publish"},
    },
    "fix.demand.segment": {"order": "product_id", "limit": 300, "actions": set()},
    "fix.demand.policy": {
        "order": "product_id",
        "limit": 300,
        "actions": {"action_pause"},
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


def _forecasts(env):
    return env["fix.demand.forecast"].sudo().search([])


def history_assembly(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _forecasts(env):
        rows.append(
            {
                "product": rec.product_id.display_name,
                "period": rec.period,
                "forecast": round(rec.forecast_qty, 3),
                "actual": round(rec.actual_qty, 3),
                "method": dict(rec._fields["method"].selection).get(rec.method),
                "source": dict(rec._fields["source"].selection).get(rec.source),
                "confidence_pct": rec.confidence_pct,
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: (r["product"], r["period"]))
    return _pack(
        "History Assembly — recorded forecast/actual periods",
        ["product", "period", "forecast", "actual", "method", "source", "confidence_pct", "state"],
        {
            "product": "Product",
            "period": "Period",
            "forecast": "Forecast",
            "actual": "Actual",
            "method": "Method",
            "source": "Source",
            "confidence_pct": "Confidence %",
            "state": "State",
        },
        rows,
        [
            "Only recorded periods appear; the actual quantity is entered/loaded, "
            "never inferred from forecast."
        ],
        empty="No forecast periods recorded yet.",
    )


def accuracy_bias(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _forecasts(env).filtered(lambda f: (f.actual_qty or 0.0) > 0):
        rows.append(
            {
                "product": rec.product_id.display_name,
                "period": rec.period,
                "forecast": round(rec.forecast_qty, 3),
                "actual": round(rec.actual_qty, 3),
                "bias": round(rec.variance, 3),
                "abs_error_pct": rec.abs_error_pct,
            }
        )
    rows.sort(key=lambda r: -r["abs_error_pct"])
    mape = round(sum(r["abs_error_pct"] for r in rows) / len(rows), 1) if rows else 0.0
    return _pack(
        "Accuracy & Bias (MAPE) — forecast against the recorded actual",
        ["product", "period", "forecast", "actual", "bias", "abs_error_pct"],
        {
            "product": "Product",
            "period": "Period",
            "forecast": "Forecast",
            "actual": "Actual",
            "bias": "Bias (actual−forecast)",
            "abs_error_pct": "Abs Error %",
        },
        rows,
        ["MAPE %.1f%% across %d period(s) with an actual." % (mape, len(rows))],
        empty="No period has a recorded actual yet.",
    )


def lead_time(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in env["fix.demand.policy"].sudo().search([]):
        rows.append(
            {
                "product": rec.product_id.display_name,
                "avg_daily": round(rec.avg_daily_demand, 2),
                "stddev": round(rec.demand_stddev, 2),
                "lead_time_days": rec.lead_time_days,
                "service_level_pct": rec.service_level_pct,
                "safety_stock": round(rec.safety_stock, 2),
                "reorder_point": round(rec.reorder_point, 2),
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -r["reorder_point"])
    return _pack(
        "Lead-Time Modelling — safety stock and ROP per product",
        [
            "product",
            "avg_daily",
            "stddev",
            "lead_time_days",
            "service_level_pct",
            "safety_stock",
            "reorder_point",
            "state",
        ],
        {
            "product": "Product",
            "avg_daily": "Avg Daily",
            "stddev": "Std Dev",
            "lead_time_days": "Lead Time",
            "service_level_pct": "Service %",
            "safety_stock": "Safety Stock",
            "reorder_point": "Reorder Point",
            "state": "State",
        },
        rows,
        [
            "Safety stock = z × σ × √lead time (z from the service level); ROP = "
            "avg daily × lead time + safety stock. Transparent formula, no model."
        ],
        empty="No demand policies yet.",
    )


def van_par(env, date_from=None, date_to=None, **params):
    policies = env["fix.demand.policy"].sudo().search([("state", "=", "active")])
    rows = []
    for rec in policies:
        par = round((rec.reorder_point or 0.0) * 1.2, 2)
        rows.append(
            {
                "product": rec.product_id.display_name,
                "reorder_point": round(rec.reorder_point, 2),
                "safety_stock": round(rec.safety_stock, 2),
                "van_par": par,
                "top_up_qty": round(max(par - rec.safety_stock, 0.0), 2),
            }
        )
    rows.sort(key=lambda r: -r["van_par"])
    return _pack(
        "Van-Stock Par Calculation — 1.2 × ROP as the van par",
        ["product", "reorder_point", "safety_stock", "van_par", "top_up_qty"],
        {
            "product": "Product",
            "reorder_point": "ROP",
            "safety_stock": "Safety Stock",
            "van_par": "Van Par",
            "top_up_qty": "Top-up per Visit",
        },
        rows,
        [
            "Van par = 1.2 × ROP (20% on-van buffer); the top-up is the par less the "
            "safety stock the van already carries."
        ],
        empty="No active demand policies yet.",
    )


def accuracy_by_class(env, date_from=None, date_to=None, **params):
    segments = env["fix.demand.segment"].sudo().search([])
    forecasts = _forecasts(env).filtered(lambda f: (f.actual_qty or 0.0) > 0)
    buckets = {}
    for segment in segments:
        key = segment.abc_class.upper()
        recs = forecasts.filtered(lambda f, p=segment.product_id: f.product_id.id == p.id)
        row = buckets.setdefault(
            key,
            {
                "abc": key,
                "products": 0,
                "periods": 0,
                "errors": [],
            },
        )
        row["products"] += 1
        row["periods"] += len(recs)
        row["errors"].extend(recs.mapped("abs_error_pct"))
    rows = []
    for row in buckets.values():
        errors = row.pop("errors")
        row["mape_pct"] = round(sum(errors) / len(errors), 1) if errors else 0.0
        rows.append(row)
    rows.sort(key=lambda r: r["abc"])
    return _pack(
        "Forecast Accuracy by Class — MAPE per ABC class",
        ["abc", "products", "periods", "mape_pct"],
        {"abc": "ABC Class", "products": "Products", "periods": "Periods", "mape_pct": "MAPE %"},
        rows,
        ["Classes come from the segmentation rows; only periods with an actual " "enter the MAPE."],
        empty="No segmentation/actuals yet.",
    )


def stockout_causes(env, date_from=None, date_to=None, **params):
    plans = env["fix.demand.plan"].sudo().search([])
    rows = []
    for plan in plans:
        gap = (plan.forecast_quantity or 0.0) - (plan.current_stock or 0.0)
        if gap <= 0:
            continue
        rows.append(
            {
                "plan": plan.name,
                "product": plan.product_id.display_name,
                "forecast": round(plan.forecast_quantity, 2),
                "stock": round(plan.current_stock, 2),
                "gap": round(gap, 2),
                "reorder_point": round(plan.reorder_point, 2),
                "recommended": round(plan.recommended_order, 2),
                "cause": "below ROP"
                if (plan.current_stock or 0.0) <= (plan.reorder_point or 0.0)
                else "forecast exceeds stock",
                "state": dict(plan._fields["state"].selection).get(plan.state),
            }
        )
    rows.sort(key=lambda r: -r["gap"])
    return _pack(
        "Stockout Root Causes — forecast gaps against stock",
        [
            "plan",
            "product",
            "forecast",
            "stock",
            "gap",
            "reorder_point",
            "recommended",
            "cause",
            "state",
        ],
        {
            "plan": "Plan",
            "product": "Product",
            "forecast": "Forecast",
            "stock": "Stock",
            "gap": "Gap",
            "reorder_point": "ROP",
            "recommended": "Recommended",
            "cause": "Cause",
            "state": "State",
        },
        rows,
        [
            "Cause is classified from the recorded position: below ROP, or a "
            "forecast that exceeds current stock while still above ROP."
        ],
        empty="No forecast gap in the recorded plans.",
    )


def excess_obsolescence(env, date_from=None, date_to=None, **params):
    plans = env["fix.demand.plan"].sudo().search([])
    rows = []
    for plan in plans:
        excess = (plan.current_stock or 0.0) - (plan.forecast_quantity or 0.0)
        if excess <= 0:
            continue
        rows.append(
            {
                "plan": plan.name,
                "product": plan.product_id.display_name,
                "stock": round(plan.current_stock, 2),
                "forecast": round(plan.forecast_quantity, 2),
                "excess": round(excess, 2),
                "reorder_point": round(plan.reorder_point, 2),
                "state": dict(plan._fields["state"].selection).get(plan.state),
            }
        )
    rows.sort(key=lambda r: -r["excess"])
    return _pack(
        "Excess & Obsolescence Exposure — stock above forecast",
        ["plan", "product", "stock", "forecast", "excess", "reorder_point", "state"],
        {
            "plan": "Plan",
            "product": "Product",
            "stock": "Stock",
            "forecast": "Forecast",
            "excess": "Excess",
            "reorder_point": "ROP",
            "state": "State",
        },
        rows,
        [
            "Excess = current stock − forecast. Ageing by lot remains M15's report; "
            "this is the planning exposure."
        ],
        empty="No plan carries excess stock.",
    )


def rebalancing_savings(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in env["fix.demand.rebalance"].sudo().search([]):
        rows.append(
            {
                "proposal": rec.name,
                "product": rec.product_id.display_name,
                "from": rec.source_branch,
                "to": rec.target_branch,
                "qty": round(rec.qty, 3),
                "unit_cost": round(rec.unit_cost, 2),
                "savings": round(rec.savings, 2),
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -r["savings"])
    approved = round(sum(r["savings"] for r in rows if r["state"] == "Approved"), 2)
    return _pack(
        "Rebalancing Savings — transfer vs buy (10% avoided-buy basis)",
        ["proposal", "product", "from", "to", "qty", "unit_cost", "savings", "state"],
        {
            "proposal": "Proposal",
            "product": "Product",
            "from": "From",
            "to": "To",
            "qty": "Qty",
            "unit_cost": "Unit Cost",
            "savings": "Savings",
            "state": "State",
        },
        rows,
        [
            "Savings = qty x unit cost x 10%% (the declared avoided-buy assumption); "
            "approved proposals total %s." % approved
        ],
        totals={"proposal": "Total", "savings": round(sum(r["savings"] for r in rows), 2)},
        empty="No rebalancing proposals yet.",
    )


def new_part_intro(env, date_from=None, date_to=None, **params):
    segments = env["fix.demand.segment"].sudo().search([])
    forecasts = _forecasts(env)
    rows = []
    for segment in segments:
        product_forecasts = forecasts.filtered(
            lambda f, p=segment.product_id: f.product_id.id == p.id
        )
        periods = len(product_forecasts)
        rows.append(
            {
                "product": segment.product_id.display_name,
                "segment": "%s/%s" % (segment.abc_class.upper(), segment.xyz_class.upper()),
                "criticality": dict(segment._fields["criticality"].selection).get(
                    segment.criticality
                ),
                "periods_of_data": periods,
                "first_forecast": min(product_forecasts.mapped("period")) if periods else "—",
                "status": "established" if periods >= 2 else "new / insufficient history",
            }
        )
    rows.sort(key=lambda r: (r["periods_of_data"], r["product"]))
    return _pack(
        "New-Part Introduction — history depth per product",
        ["product", "segment", "criticality", "periods_of_data", "first_forecast", "status"],
        {
            "product": "Product",
            "segment": "Segment",
            "criticality": "Criticality",
            "periods_of_data": "Periods",
            "first_forecast": "First Forecast",
            "status": "Status",
        },
        rows,
        [
            "A product with fewer than two recorded periods is labelled new / "
            "insufficient history rather than forecast as if established."
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
    "rebalancing_savings": rebalancing_savings,
    "new_part_intro": new_part_intro,
}


def kpis(env):
    forecasts = _forecasts(env)
    policies = env["fix.demand.policy"].sudo().search([])
    plans = env["fix.demand.plan"].sudo().search([])
    rebalances = env["fix.demand.rebalance"].sudo().search([])
    with_actuals = forecasts.filtered(lambda f: (f.actual_qty or 0.0) > 0)
    mape = (
        round(sum(with_actuals.mapped("abs_error_pct")) / len(with_actuals), 1)
        if with_actuals
        else 0.0
    )
    levels = [int(p.service_level_pct or 95) for p in policies]
    return {
        "forecasts_pending": len(forecasts.filtered(lambda f: f.state == "draft")),
        "mape_pct": mape,
        "policies_active": len(policies.filtered(lambda p: p.state == "active")),
        "planned_orders": len(
            plans.filtered(
                lambda p: p.state == "approved"
                and (p.recommended_order or 0.0) > 0
                and not p.pr_requisition_id
            )
        ),
        "rebalance_savings": round(
            sum(r.savings or 0.0 for r in rebalances if r.state == "approved"), 2
        ),
        "service_level_avg": round(sum(levels) / len(levels), 1) if levels else 0.0,
    }
