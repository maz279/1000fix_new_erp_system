# A05 · M14 Trade-In, Refurbishment & Resale — surfaces, packs and KPIs over
# the existing trade-in/refurbishment engine and the new valuation,
# provenance, grading, QA, harvest and warranty models. Graded stock is read
# through M38's surface (single owner); resale listings are M12's, so this
# module reports the trade-in resale record, never a duplicated listing model.
import datetime

from ..p03_service_order_api import _require_internal  # noqa: F401

SURFACES = {
    # A05 audit M14-3 / E11: the payout is requested here and decided from the
    # approver's M63 inbox; action_approve_payout, action_reject_payout and
    # action_dofa_approve are never pressed on the record (they refuse).
    "fix.tradein.request": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_send_offer",
            "action_accept",
            "action_reject",
            "action_accept_revision",
            "action_collect",
            "action_wipe",
            "action_refurbish",
            "action_grade",
            "action_resale_ready",
            "action_verify_psr",
            "action_request_payout_approval",
            "action_request_approval",
            "action_recall_approval",
            "action_pay",
        },
    },
    # M14-20: the step buttons the screen showed were not whitelisted.
    "fix.refurbishment": {
        "order": "tradein_id, id",
        "limit": 300,
        "actions": {"action_start", "action_request_parts", "action_complete_repair"},
    },
    "fix.tradein.valuation": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_apply_to_tradein",
            "action_request_override_approval",
            "action_approve_override",
            "action_reject_override",
        },
    },
    "fix.tradein.price.grid": {
        "order": "device_model_id, valid_from desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_retire"},
    },
    "fix.tradein.provenance": {
        "order": "checked_on desc, id desc",
        "limit": 300,
        "actions": {"action_clear", "action_flag", "action_run_neir_check"},
    },
    "fix.tradein.grade": {"order": "graded_on desc, id desc", "limit": 300, "actions": set()},
    "fix.refurb.qa": {
        "order": "checked_on desc, id desc",
        "limit": 300,
        "actions": {"action_submit_result"},
    },
    "fix.tradein.harvest": {
        "order": "harvested_on desc, id desc",
        "limit": 300,
        "actions": {"action_harvest", "action_scrap"},
    },
    "fix.tradein.warranty": {
        "order": "start_date desc, id desc",
        "limit": 300,
        "actions": {"action_void"},
    },
    # M14 capture audit (2026-11-13): the corporate bulk buy-back lot
    # (FR-TRF-009). Its declared assets are written as the form's child grid;
    # each asset's trade-in is opened by action_open_intakes, never typed.
    "fix.bulk.buyback": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_open_intakes", "action_close"},
    },
    # M14 capture pass 2 (2026-11-19): physical intake verification
    # (FR-TRF-005), the refurbished return (FR-TRF-026) and the parts-only
    # routing with its write-off approval (FR-TRF-020). The QA protocol rows
    # (fix.refurb.qa.test) are written as the QA form's child grid.
    "fix.tradein.intake.check": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_confirm"},
    },
    "fix.refurb.return": {
        "order": "return_date desc, id desc",
        "limit": 300,
        "actions": {"action_receive", "action_decide"},
    },
    "fix.refurb.writeoff": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request", "action_approve", "action_reject"},
    },
}

_RESALE_STATES = ("graded", "resale_ready", "closed")


def _today():
    return datetime.date.today()


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


def _scoped(env, model):
    """The user's companies only (A05 audit E2 / M18-11: KPIs and packs read
    every company's rows through an unscoped superuser search)."""
    return env[model].sudo().search([("company_id", "in", env.companies.ids)])


def _requests(env):
    return _scoped(env, "fix.tradein.request")


def _grade_label(code):
    return {
        "a": "A — Like New",
        "b": "B — Good",
        "c": "C — Fair",
        "d": "D — Poor",
        "e": "E — Parts Only",
    }.get(code, "—")


def tradein_margin(env, date_from=None, date_to=None, **params):
    rows = []
    by_model = {}
    for rec in _requests(env).filtered(lambda r: r.state in _RESALE_STATES):
        key = rec.device_model_id.name if rec.device_model_id else "Unassigned model"
        row = by_model.setdefault(
            key,
            {
                "model": key,
                "units": 0,
                "offered": 0.0,
                "refurb": 0.0,
                "inventory": 0.0,
                "resale": 0.0,
                "margin": 0.0,
            },
        )
        row["units"] += 1
        row["offered"] += rec.offered_value or 0.0
        row["refurb"] += rec.refurbishment_cost or 0.0
        row["inventory"] += rec.inventory_valuation or 0.0
        row["resale"] += rec.resale_value or 0.0
        row["margin"] += (rec.resale_value or 0.0) - (rec.inventory_valuation or 0.0)
    for row in by_model.values():
        for key in ("offered", "refurb", "inventory", "resale", "margin"):
            row[key] = round(row[key], 2)
        row["margin_pct"] = (
            round((row["margin"] / row["inventory"]) * 100.0, 1) if row["inventory"] else 0.0
        )
        rows.append(row)
    rows.sort(key=lambda r: -r["margin"])
    return _pack(
        "Trade-In Margin by Model — graded, resale-ready and closed units",
        ["model", "units", "offered", "refurb", "inventory", "resale", "margin", "margin_pct"],
        {
            "model": "Device Model",
            "units": "Units",
            "offered": "Offered",
            "refurb": "Refurb Cost",
            "inventory": "Inventory Cost",
            "resale": "Resale Value",
            "margin": "Margin",
            "margin_pct": "Margin %",
        },
        rows,
        [
            "Margin = resale value − inventory cost (acquisition at the graded payout "
            "value, else the offer, + refurbishment). "
            "Only units that reached grading count."
        ],
        totals={
            "model": "Total",
            "units": sum(r["units"] for r in rows),
            "offered": round(sum(r["offered"] for r in rows), 2),
            "refurb": round(sum(r["refurb"] for r in rows), 2),
            "inventory": round(sum(r["inventory"] for r in rows), 2),
            "resale": round(sum(r["resale"] for r in rows), 2),
            "margin": round(sum(r["margin"] for r in rows), 2),
        },
        empty="No unit has reached grading yet.",
    )


def refurb_cost_grade(env, date_from=None, date_to=None, **params):
    rows = []
    by_grade = {}
    for rec in _requests(env).filtered(lambda r: r.state in _RESALE_STATES and r.grade):
        row = by_grade.setdefault(
            rec.grade,
            {
                "grade": _grade_label(rec.grade),
                "units": 0,
                "parts": 0.0,
                "labour": 0.0,
                "total": 0.0,
            },
        )
        row["units"] += 1
        row["parts"] += rec.parts_cost or 0.0
        row["labour"] += rec.labour_cost or 0.0
        row["total"] += rec.refurbishment_cost or 0.0
    for row in by_grade.values():
        for key in ("parts", "labour", "total"):
            row[key] = round(row[key], 2)
        row["avg"] = round(row["total"] / row["units"], 2) if row["units"] else 0.0
        rows.append(row)
    order = {
        label: i
        for i, label in enumerate(
            ["A — Like New", "B — Good", "C — Fair", "D — Poor", "E — Parts Only"]
        )
    }
    rows.sort(key=lambda r: order.get(r["grade"], 99))
    return _pack(
        "Refurb Cost per Grade",
        ["grade", "units", "parts", "labour", "total", "avg"],
        {
            "grade": "Grade",
            "units": "Units",
            "parts": "Parts",
            "labour": "Labour",
            "total": "Total Cost",
            "avg": "Average per Unit",
        },
        rows,
        ["Costs are the recorded refurbishment parts + labour on each unit."],
        totals={
            "grade": "Total",
            "units": sum(r["units"] for r in rows),
            "parts": round(sum(r["parts"] for r in rows), 2),
            "labour": round(sum(r["labour"] for r in rows), 2),
            "total": round(sum(r["total"] for r in rows), 2),
        },
        empty="No graded units yet.",
    )


def ageing_markdown(env, date_from=None, date_to=None, **params):
    today = _today()
    stock = _scoped(env, "fix.graded.stock")
    rows = []
    for rec in stock:
        age = (today - rec.create_date.date()).days if rec.create_date else 0
        if age > 180:
            markdown, reason = 20.0, "over 180 days in stock"
        elif age > 90:
            markdown, reason = 10.0, "over 90 days in stock"
        else:
            markdown, reason = 0.0, "within policy"
        rows.append(
            {
                "stock": rec.name,
                "grade": rec.grade_id.name if rec.grade_id else "—",
                "tradein": rec.tradein_ref or "—",
                "age_days": age,
                "inventory": round(rec.inventory_valuation or 0.0, 2),
                "resale": round(rec.resale_price or 0.0, 2),
                "margin": round(rec.projected_margin or 0.0, 2),
                "suggested_markdown_pct": markdown,
                "action": reason,
            }
        )
    rows.sort(key=lambda r: -r["age_days"])
    return _pack(
        "Ageing & Markdown — graded stock by days held",
        [
            "stock",
            "grade",
            "tradein",
            "age_days",
            "inventory",
            "resale",
            "margin",
            "suggested_markdown_pct",
            "action",
        ],
        {
            "stock": "Stock Unit",
            "grade": "Grade",
            "tradein": "Trade-In",
            "age_days": "Days Held",
            "inventory": "Inventory Cost",
            "resale": "Resale Price",
            "margin": "Projected Margin",
            "suggested_markdown_pct": "Markdown %",
            "action": "Policy",
        },
        rows,
        [
            "Markdown policy: 10% after 90 days, 20% after 180 days in stock — "
            "explicit thresholds, no model."
        ],
        empty="No graded stock units held.",
    )


def resale_channel(env, date_from=None, date_to=None, **params):
    rows = []
    by_channel = {}
    labels = dict(env["fix.tradein.request"]._fields["resale_channel"].selection)
    for rec in _requests(env).filtered(lambda r: r.state in _RESALE_STATES):
        key = rec.resale_channel or "none"
        row = by_channel.setdefault(
            key,
            {
                "channel": labels.get(key, key),
                "units": 0,
                "listed": 0,
                "value": 0.0,
                "sold": 0,
            },
        )
        row["units"] += 1
        if rec.resale_listed_on:
            row["listed"] += 1
        row["value"] += rec.resale_value or 0.0
        if rec.state == "closed":
            row["sold"] += 1
    for row in by_channel.values():
        row["value"] = round(row["value"], 2)
        row["avg"] = round(row["value"] / row["units"], 2) if row["units"] else 0.0
        rows.append(row)
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Resale Channel Performance",
        ["channel", "units", "listed", "sold", "value", "avg"],
        {
            "channel": "Channel",
            "units": "Units",
            "listed": "Listed",
            "sold": "Sold",
            "value": "Resale Value",
            "avg": "Average Price",
        },
        rows,
        [
            "Marketplace/store listing execution lives in M12/M38; this reads the "
            "trade-in's recorded resale channel and price."
        ],
        totals={
            "channel": "Total",
            "units": sum(r["units"] for r in rows),
            "listed": sum(r["listed"] for r in rows),
            "sold": sum(r["sold"] for r in rows),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No graded units yet.",
    )


def harvest_yield(env, date_from=None, date_to=None, **params):
    harvests = _scoped(env, "fix.tradein.harvest")
    by_component = {}
    for rec in harvests:
        row = by_component.setdefault(
            rec.component,
            {
                "component": dict(rec._fields["component"].selection).get(rec.component),
                "lines": 0,
                "quantity": 0,
                "value": 0.0,
                "tradeins": set(),
            },
        )
        row["lines"] += 1
        row["quantity"] += rec.quantity or 0
        row["value"] += rec.total_value or 0.0
        row["tradeins"].add(rec.tradein_id.id)
    rows = []
    for row in by_component.values():
        offered = sum(
            r.offered_value or 0.0
            for r in _requests(env).filtered(lambda r, ids=row["tradeins"]: r.id in ids)
        )
        row["tradeins"] = len(row["tradeins"])
        row["value"] = round(row["value"], 2)
        row["yield_pct"] = round((row["value"] / offered) * 100.0, 1) if offered else 0.0
        rows.append(row)
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Harvest Yield — recovered component value",
        ["component", "lines", "quantity", "tradeins", "value", "yield_pct"],
        {
            "component": "Component",
            "lines": "Lines",
            "quantity": "Quantity",
            "tradeins": "Trade-Ins",
            "value": "Recovered Value",
            "yield_pct": "Yield % of Offer",
        },
        rows,
        [
            "Yield = recovered component value ÷ the offer paid for the source "
            "trade-ins. Harvest lines that are still pending are included."
        ],
        totals={
            "component": "Total",
            "lines": sum(r["lines"] for r in rows),
            "quantity": sum(r["quantity"] for r in rows),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No harvest lines recorded yet.",
    )


def resale_pipeline(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _requests(env).filtered(lambda r: r.state in _RESALE_STATES):
        rows.append(
            {
                "tradein": rec.name,
                "model": rec.device_model_id.name if rec.device_model_id else "—",
                "grade": _grade_label(rec.grade),
                "battery_health_pct": rec.battery_health_pct,
                "resale_value": round(rec.resale_value or 0.0, 2),
                "channel": dict(rec._fields["resale_channel"].selection).get(rec.resale_channel),
                "listed_on": str(rec.resale_listed_on) if rec.resale_listed_on else "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -r["resale_value"])
    return _pack(
        "Resale Listings — the trade-in resale record",
        [
            "tradein",
            "model",
            "grade",
            "battery_health_pct",
            "resale_value",
            "channel",
            "listed_on",
            "state",
        ],
        {
            "tradein": "Trade-In",
            "model": "Model",
            "grade": "Grade",
            "battery_health_pct": "Battery %",
            "resale_value": "Resale Value",
            "channel": "Channel",
            "listed_on": "Listed On",
            "state": "State",
        },
        rows,
        [
            "Live marketplace listings are created in M12/M38; this grid is the "
            "trade-in's own resale record (price, channel, listing date)."
        ],
        empty="No unit is at or past grading yet.",
    )


def unit_economics(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _requests(env).filtered(lambda r: r.state in _RESALE_STATES):
        margin = (rec.resale_value or 0.0) - (rec.inventory_valuation or 0.0)
        rows.append(
            {
                "tradein": rec.name,
                "model": rec.device_model_id.name if rec.device_model_id else "—",
                "grade": _grade_label(rec.grade),
                "offered": round(rec.offered_value or 0.0, 2),
                "refurb": round(rec.refurbishment_cost or 0.0, 2),
                "inventory": round(rec.inventory_valuation or 0.0, 2),
                "resale": round(rec.resale_value or 0.0, 2),
                "payout": round(rec.payout_amount or 0.0, 2),
                "margin": round(margin, 2),
                "margin_pct": round((margin / rec.inventory_valuation) * 100.0, 1)
                if rec.inventory_valuation
                else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["margin"])
    return _pack(
        "Unit Economics — per refurbished unit",
        [
            "tradein",
            "model",
            "grade",
            "offered",
            "refurb",
            "inventory",
            "resale",
            "payout",
            "margin",
            "margin_pct",
        ],
        {
            "tradein": "Trade-In",
            "model": "Model",
            "grade": "Grade",
            "offered": "Offered",
            "refurb": "Refurb Cost",
            "inventory": "Inventory Cost",
            "resale": "Resale",
            "payout": "Payout Paid",
            "margin": "Margin",
            "margin_pct": "Margin %",
        },
        rows,
        [
            "Margin = resale − inventory cost. Payout Paid is the treasury payout "
            "recorded on the request (0 until M50 executes)."
        ],
        totals={
            "tradein": "Total",
            "offered": round(sum(r["offered"] for r in rows), 2),
            "refurb": round(sum(r["refurb"] for r in rows), 2),
            "inventory": round(sum(r["inventory"] for r in rows), 2),
            "resale": round(sum(r["resale"] for r in rows), 2),
            "payout": round(sum(r["payout"] for r in rows), 2),
            "margin": round(sum(r["margin"] for r in rows), 2),
        },
        empty="No unit has reached grading yet.",
    )


def valuation_queue(env, date_from=None, date_to=None, **params):
    valuations = _scoped(env, "fix.tradein.valuation")
    rows = []
    for rec in valuations:
        rows.append(
            {
                "valuation": rec.name,
                "tradein": rec.tradein_id.name,
                "model": rec.device_model_id.name if rec.device_model_id else "—",
                "market_ref": round(rec.market_ref_price or 0.0, 2),
                "computed": round(rec.computed_offer or 0.0, 2),
                "final": round(rec.final_offer or 0.0, 2),
                "method": dict(rec._fields["method"].selection).get(rec.method),
                "state": dict(rec._fields["state"].selection).get(rec.state),
                "valuated_on": str(rec.valuated_on),
            }
        )
    rows.sort(key=lambda r: r["valuated_on"], reverse=True)
    return _pack(
        "Valuation Queue — offers computed and applied",
        [
            "valuation",
            "tradein",
            "model",
            "market_ref",
            "computed",
            "final",
            "method",
            "state",
            "valuated_on",
        ],
        {
            "valuation": "Valuation",
            "tradein": "Trade-In",
            "model": "Model",
            "market_ref": "Market Ref",
            "computed": "Computed Offer",
            "final": "Final Offer",
            "method": "Method",
            "state": "State",
            "valuated_on": "Valuated",
        },
        rows,
        [
            "Computed = market reference × age factor × condition factor. "
            "A manual override needs a stated reason before it can be applied."
        ],
        empty="No valuations recorded yet.",
    )


REPORTS = {
    "tradein_margin": tradein_margin,
    "refurb_cost_grade": refurb_cost_grade,
    "ageing_markdown": ageing_markdown,
    "resale_channel": resale_channel,
    "harvest_yield": harvest_yield,
    "resale_pipeline": resale_pipeline,
    "unit_economics": unit_economics,
    "valuation_queue": valuation_queue,
}


def kpis(env):
    requests = _requests(env)
    pending_payout = requests.filtered(lambda r: r.payout_approval_state == "pending")
    resale_ready = requests.filtered(lambda r: r.state == "resale_ready")
    graded = requests.filtered(lambda r: r.state in _RESALE_STATES)
    stock = _scoped(env, "fix.graded.stock")
    open_states = ("draft", "offered", "accepted", "collected", "wiped", "refurbished", "graded")
    return {
        "open_tradeins": len(requests.filtered(lambda r: r.state in open_states)),
        "pending_payouts": len(pending_payout),
        "refurb_open": env["fix.refurbishment"]
        .sudo()
        .search_count([("state", "=", "pending"), ("company_id", "in", env.companies.ids)]),
        "resale_ready": len(resale_ready),
        "graded_stock_value": round(sum(stock.mapped("inventory_valuation")), 2),
        "margin_pipeline": round(
            sum((r.resale_value or 0.0) - (r.inventory_valuation or 0.0) for r in graded), 2
        ),
    }
