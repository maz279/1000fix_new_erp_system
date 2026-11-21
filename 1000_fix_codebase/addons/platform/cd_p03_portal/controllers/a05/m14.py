# A05 · M14 Trade-In, Refurbishment & Resale — surfaces, packs and KPIs over
# the existing trade-in/refurbishment engine and the new valuation,
# provenance, grading, QA, harvest and warranty models. Graded stock is read
# through M38's surface (single owner); resale listings are M12's, so this
# module reports the trade-in resale record, never a duplicated listing model.
#
# A05 ERP audit (20 Nov 2026, XC-06/11/12/13/14/18/23/25/27, M14-18/24/25):
# every pack honours the period in Dhaka days on its own date (sale, grading,
# listing, harvest, valuation), reads only what the caller's company and
# operating-unit rules allow, measures a sale as the stock unit SOLD (not the
# seller paid), gross margin on the resale price, stock value on units held
# and ageing on units in stock; the markdown ladder is configuration shown in
# force with an NRV test; the funnel and the zero-target gate compliance
# report are added.
import datetime

from .m13 import (
    CONTROL_COLS,
    CONTROL_LABELS,
    _pack,
    control_row,
    dhaka_today,
    fenced,
    in_window,
    param_float,
    pct,
    period_note,
    to_dhaka_date,
    tracked_dates,
    utc_bounds,
    window,
)

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
            # A05 ERP (S2): listing price 4-eyes (D6), counter sale, parts-only
            # close and the recycle route (M14-09/13/15)
            "action_request_listing_price",
            "action_approve_listing_price",
            "action_counter_sell",
            "action_close_parts_only",
            "action_route_to_recycle",
        },
    },
    # M14-20: the step buttons the screen showed were not whitelisted.
    "fix.refurbishment": {
        "order": "tradein_id, id",
        "limit": 300,
        "actions": {
            "action_start",
            "action_request_parts",
            "action_complete_repair",
            "action_approve_cost",
        },
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
        "actions": {
            "action_clear",
            "action_flag",
            "action_run_neir_check",
            "action_record_neir_result",
        },
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
        "actions": {"action_open_intakes", "action_close", "action_allocate_lot_price"},
    },
    # A05 ERP (S2, M14-25 / BRU-TRF-18): an NRV markdown of a refurbished unit,
    # approved four-eyes by a pricing manager; approval reprices and posts the
    # write-down
    "fix.refurb.markdown": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request", "action_approve", "action_reject"},
        "pickers": {"tradein_id": [("state", "in", ("graded", "resale_ready"))]},
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
_WIPED_ONWARD = ("wiped", "refurbished", "graded", "resale_ready", "closed")
_GRADE_LABELS = {
    "a": "A — Like New",
    "b": "B — Good",
    "c": "C — Fair",
    "d": "D — Poor",
    "e": "E — Parts Only",
}
_GRADE_ORDER = list(_GRADE_LABELS.values())


def _grade_label(code):
    return _GRADE_LABELS.get(code, "—")


def _scoped(env, model, domain=None):
    """A05 ERP audit XC-23: the caller's own read (company AND operating-unit
    record rules) inside the caller's companies - never a superuser search."""
    found = fenced(env, model, domain)
    return found if found is not None else env["res.partner"].browse()


def _requests(env, domain=None):
    return _scoped(env, "fix.tradein.request", domain)


def _stock_by_request(env, requests):
    """{request id: graded stock unit} for the requests' resale units."""
    out = {r.id: r.graded_stock_id for r in requests if r.graded_stock_id}
    if "fix.graded.stock" in env:
        missing = [r.id for r in requests if r.id not in out]
        if missing:
            for unit in env["fix.graded.stock"].sudo().search([("tradein_id", "in", missing)]):
                out.setdefault(unit.tradein_id, unit)
    return out


def _sold(env, requests, start, end):
    """[(request, stock unit, sold day)] for units SOLD in the period: the
    graded stock unit's tracked move to 'sold' (A05 ERP audit M14-24: a paid
    seller is not a sale)."""
    stock = _stock_by_request(env, requests)
    units = (
        env["fix.graded.stock"]
        .sudo()
        .browse([u.id for u in stock.values()])
        .filtered(lambda u: u.state == "sold")
        if "fix.graded.stock" in env
        else []
    )
    if not units:
        return []
    sold_on = tracked_dates(env, units, "sold")
    by_unit = {u.id: rid for rid, u in stock.items()}
    reqs = {r.id: r for r in requests}
    out = []
    for unit in units:
        day = sold_on.get(unit.id) or to_dhaka_date(unit.write_date)
        if day and start <= day <= end:
            out.append((reqs[by_unit[unit.id]], unit, day))
    return out


def _price(req, unit):
    """The resale price of the unit: an ex-VAT price where the trade-in
    stream records one, else the listing price on the stock unit, else the
    request's resale value."""
    for record, name in ((unit, "resale_price_ex_vat"), (req, "resale_value_ex_vat")):
        if record and name in record._fields and record[name]:
            return record[name]
    if unit and unit.resale_price:
        return unit.resale_price
    return req.resale_value or 0.0


def _cost(req, unit):
    if unit and unit.inventory_valuation:
        return unit.inventory_valuation
    return req.inventory_valuation or 0.0


_PRICE_NOTE = (
    "Resale price = the unit's ex-VAT resale price where recorded, else its "
    "listing price (VAT-inclusive where VAT applies, D2)."
)


def tradein_margin(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    by_model = {}
    for req, unit, _day in _sold(env, _requests(env), start, end):
        key = req.device_model_id.name if req.device_model_id else "Unassigned model"
        row = by_model.setdefault(
            key,
            {
                "model": key,
                "units": 0,
                "acquisition": 0.0,
                "refurb": 0.0,
                "inventory": 0.0,
                "resale": 0.0,
                "margin": 0.0,
            },
        )
        cost = _cost(req, unit)
        price = _price(req, unit)
        row["units"] += 1
        row["acquisition"] += (unit.acquisition_cost if unit else 0.0) or req.payout_amount or 0.0
        row["refurb"] += req.refurbishment_cost or 0.0
        row["inventory"] += cost
        row["resale"] += price
        row["margin"] += price - cost
    rows = []
    for row in by_model.values():
        for key in ("acquisition", "refurb", "inventory", "resale", "margin"):
            row[key] = round(row[key], 2)
        row["margin_pct"] = pct(row["margin"], row["resale"])
        rows.append(row)
    rows.sort(key=lambda r: -r["margin"])
    resale = sum(r["resale"] for r in rows)
    margin = sum(r["margin"] for r in rows)
    return _pack(
        "Trade-In Margin by Model — units sold %s to %s" % (start, end),
        ["model", "units", "acquisition", "refurb", "inventory", "resale", "margin", "margin_pct"],
        {
            "model": "Device Model",
            "units": "Units Sold",
            "acquisition": "Acquisition Cost",
            "refurb": "Refurb Cost",
            "inventory": "Inventory Cost",
            "resale": "Resale Price",
            "margin": "Margin",
            "margin_pct": "Gross Margin %",
        },
        rows,
        [
            "Gross margin % = (resale price − inventory cost) ÷ resale price (spec "
            "target > 22%), on units whose stock unit was SOLD in the period.",
            _PRICE_NOTE,
            period_note(start, end, "sale date (stock unit moved to sold)"),
        ],
        totals={
            "model": "Total",
            "units": sum(r["units"] for r in rows),
            "acquisition": round(sum(r["acquisition"] for r in rows), 2),
            "refurb": round(sum(r["refurb"] for r in rows), 2),
            "inventory": round(sum(r["inventory"] for r in rows), 2),
            "resale": round(resale, 2),
            "margin": round(margin, 2),
            "margin_pct": pct(margin, resale),
        },
        empty="No refurbished unit sold in this window.",
    )


def _graded_in(env, requests, start, end):
    """{request id: Dhaka day of its latest grading in the period}."""
    if "fix.tradein.grade" not in env:
        return {}
    grades = (
        env["fix.tradein.grade"]
        .sudo()
        .search(
            [
                ("tradein_id", "in", requests.ids),
                ("graded_on", ">=", start),
                ("graded_on", "<=", end),
            ]
        )
    )
    out = {}
    for grade in grades:
        rid = grade.tradein_id.id
        out[rid] = max(out.get(rid, grade.graded_on), grade.graded_on)
    return out


def refurb_cost_grade(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    requests = _requests(env)
    graded = _graded_in(env, requests, start, end)
    by_grade = {}
    for rec in requests.filtered(lambda r: r.id in graded and r.grade):
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
    rows = []
    for row in by_grade.values():
        for key in ("parts", "labour", "total"):
            row[key] = round(row[key], 2)
        row["avg"] = round(row["total"] / row["units"], 2) if row["units"] else 0.0
        rows.append(row)
    rows.sort(key=lambda r: _GRADE_ORDER.index(r["grade"]) if r["grade"] in _GRADE_ORDER else 99)
    return _pack(
        "Refurb Cost per Grade — graded %s to %s" % (start, end),
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
        [
            "Costs are the recorded refurbishment parts + labour on each unit graded "
            "in the period.",
            period_note(start, end, "grading date"),
        ],
        totals={
            "grade": "Total",
            "units": sum(r["units"] for r in rows),
            "parts": round(sum(r["parts"] for r in rows), 2),
            "labour": round(sum(r["labour"] for r in rows), 2),
            "total": round(sum(r["total"] for r in rows), 2),
        },
        empty="No unit graded in this window.",
    )


def _markdown_policy(env):
    """XC-25 / M14-25: the markdown ladder is configuration, shown as in force."""
    return [
        (
            param_float(env, "cd_tradein.markdown_after_days_1", 90.0),
            param_float(env, "cd_tradein.markdown_pct_1", 10.0),
        ),
        (
            param_float(env, "cd_tradein.markdown_after_days_2", 180.0),
            param_float(env, "cd_tradein.markdown_pct_2", 20.0),
        ),
    ]


def _in_stock_since(env, units):
    tracked = tracked_dates(env, units, "in_stock")
    return {u.id: tracked.get(u.id) or to_dhaka_date(u.create_date) for u in units}


def ageing_markdown(env, date_from=None, date_to=None, **params):
    """Stock ageing at the period end (A05 ERP audit XC-14: units IN STOCK
    only - a sold or scrapped unit does not age) with the markdown ladder and
    a net-realisable-value test (FR-TRF-029)."""
    start, end = window(env, date_from, date_to, days=365)
    ladder = sorted(_markdown_policy(env), reverse=True)
    stock = _scoped(env, "fix.graded.stock", [("state", "=", "in_stock")])
    since = _in_stock_since(env, stock)
    rows = []
    for rec in stock:
        entered = since.get(rec.id)
        if not entered or entered > end or (date_from and entered < start):
            continue
        age = (end - entered).days
        markdown, reason = 0.0, "within policy"
        for days, md_pct in ladder:
            if age > days:
                markdown, reason = md_pct, "over %g days in stock" % days
                break
        cost = rec.inventory_valuation or 0.0
        nrv = (rec.resale_price or 0.0) * (1.0 - markdown / 100.0)
        rows.append(
            {
                "stock": rec.name,
                "grade": rec.grade_id.name if rec.grade_id else "—",
                "tradein": rec.tradein_ref or "—",
                "in_stock_since": str(entered),
                "age_days": age,
                "inventory": round(cost, 2),
                "resale": round(rec.resale_price or 0.0, 2),
                "suggested_markdown_pct": markdown,
                "nrv": round(nrv, 2),
                "nrv_test": "BELOW COST — write down" if nrv < cost else "OK",
                "action": reason,
            }
        )
    rows.sort(key=lambda r: -r["age_days"])
    over_90 = len([r for r in rows if r["age_days"] > 90])
    ladder_text = "; ".join(
        "after %g days %g%%" % (days, md_pct) for days, md_pct in sorted(ladder)
    )
    return _pack(
        "Ageing & Markdown — units in stock at %s" % end,
        [
            "stock",
            "grade",
            "tradein",
            "in_stock_since",
            "age_days",
            "inventory",
            "resale",
            "suggested_markdown_pct",
            "nrv",
            "nrv_test",
            "action",
        ],
        {
            "stock": "Stock Unit",
            "grade": "Grade",
            "tradein": "Trade-In",
            "in_stock_since": "In Stock Since",
            "age_days": "Days Held",
            "inventory": "Inventory Cost",
            "resale": "Listing Price",
            "suggested_markdown_pct": "Markdown %",
            "nrv": "NRV after Markdown",
            "nrv_test": "NRV Test",
            "action": "Policy",
        },
        rows,
        [
            "Only units in stock (available) age; sold, reserved and scrapped units do "
            "not. Days held run from the day the unit went into stock to the period end.",
            "Markdown ladder in force (cd_tradein.markdown_after_days_1/markdown_pct_1, "
            "cd_tradein.markdown_after_days_2/markdown_pct_2): %s - an owner decision "
            "(XC-25), configurable." % ladder_text,
            "NRV test: listing price after the markdown against inventory cost; below "
            "cost needs an approved write-down (BRU-TRF-18).",
            "Stock ageing beyond 90 days: %d of %d units (%.1f%%; spec target < 12%%)."
            % (over_90, len(rows), pct(over_90, len(rows))),
        ],
        totals={
            "stock": "Total",
            "inventory": round(sum(r["inventory"] for r in rows), 2),
            "resale": round(sum(r["resale"] for r in rows), 2),
            "nrv": round(sum(r["nrv"] for r in rows), 2),
        },
        empty="No graded stock units in stock.",
    )


def resale_channel(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    requests = _requests(env)
    labels = dict(env["fix.tradein.request"]._fields["resale_channel"].selection)
    by_channel = {}

    def row(key):
        return by_channel.setdefault(
            key or "none",
            {"channel": labels.get(key or "none", key), "listed": 0, "sold": 0, "value": 0.0},
        )

    for rec in requests:
        if rec.resale_listed_on and start <= rec.resale_listed_on <= end:
            row(rec.resale_channel)["listed"] += 1
    for req, unit, _day in _sold(env, requests, start, end):
        target = row(req.resale_channel)
        target["sold"] += 1
        target["value"] += _price(req, unit)
    rows = []
    for vals in by_channel.values():
        vals["value"] = round(vals["value"], 2)
        vals["avg"] = round(vals["value"] / vals["sold"], 2) if vals["sold"] else 0.0
        rows.append(vals)
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Resale Channel Performance — %s to %s" % (start, end),
        ["channel", "listed", "sold", "value", "avg"],
        {
            "channel": "Channel",
            "listed": "Listed in Period",
            "sold": "Sold in Period",
            "value": "Sales Value",
            "avg": "Average Price",
        },
        rows,
        [
            "Listed = trade-ins listed in the period; Sold = stock units sold in the "
            "period (not seller payouts). " + _PRICE_NOTE,
            period_note(start, end, "listing date and sale date"),
        ],
        totals={
            "channel": "Total",
            "listed": sum(r["listed"] for r in rows),
            "sold": sum(r["sold"] for r in rows),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="Nothing listed or sold in this window.",
    )


def harvest_yield(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    requests = _requests(env)
    harvests = (
        env["fix.tradein.harvest"]
        .sudo()
        .search(
            [
                ("tradein_id", "in", requests.ids),
                ("harvested_on", ">=", start),
                ("harvested_on", "<=", end),
            ]
        )
        if "fix.tradein.harvest" in env
        else []
    )
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
        acquired = sum(
            r.inventory_valuation or r.offered_value or 0.0
            for r in requests.browse(list(row["tradeins"]))
        )
        row["tradeins"] = len(row["tradeins"])
        row["value"] = round(row["value"], 2)
        row["yield_pct"] = pct(row["value"], acquired)
        rows.append(row)
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Harvest Yield — harvested %s to %s" % (start, end),
        ["component", "lines", "quantity", "tradeins", "value", "yield_pct"],
        {
            "component": "Component",
            "lines": "Lines",
            "quantity": "Quantity",
            "tradeins": "Trade-Ins",
            "value": "Recovered Value",
            "yield_pct": "Yield % of Unit Cost",
        },
        rows,
        [
            "Yield = recovered component value ÷ the source units' inventory cost (the "
            "offer where no cost is recorded).",
            period_note(start, end, "harvest date"),
        ],
        totals={
            "component": "Total",
            "lines": sum(r["lines"] for r in rows),
            "quantity": sum(r["quantity"] for r in rows),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No harvest lines in this window.",
    )


def resale_pipeline(env, date_from=None, date_to=None, **params):
    """Units graded or resale-ready (not sold) that entered the pipeline in
    the period (listing date, else grading date)."""
    start, end = window(env, date_from, date_to, days=365)
    requests = _requests(env).filtered(lambda r: r.state in ("graded", "resale_ready"))
    graded = _graded_in(env, requests, datetime.date(2000, 1, 1), end)
    stock = _stock_by_request(env, requests)
    rows = []
    for rec in requests:
        unit = stock.get(rec.id)
        if unit and unit.state == "sold":
            continue
        entered = rec.resale_listed_on or graded.get(rec.id) or to_dhaka_date(rec.create_date)
        if not entered or not (start <= entered <= end):
            continue
        rows.append(
            {
                "tradein": rec.name,
                "model": rec.device_model_id.name if rec.device_model_id else "—",
                "grade": _grade_label(rec.grade),
                "battery_health_pct": rec.battery_health_pct,
                "resale_value": round(_price(rec, unit), 2),
                "channel": dict(rec._fields["resale_channel"].selection).get(rec.resale_channel),
                "listed_on": str(rec.resale_listed_on) if rec.resale_listed_on else "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -r["resale_value"])
    return _pack(
        "Resale Pipeline — unsold units entering %s to %s" % (start, end),
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
            "resale_value": "Resale Price",
            "channel": "Channel",
            "listed_on": "Listed On",
            "state": "State",
        },
        rows,
        [
            "Graded and resale-ready units not yet sold. Live marketplace listings are "
            "M12/M38's; this grid is the trade-in's own resale record.",
            period_note(start, end, "listing date (else grading date)"),
        ],
        empty="No unsold unit entered the pipeline in this window.",
    )


def unit_economics(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    rows = []
    for req, unit, day in _sold(env, _requests(env), start, end):
        cost = _cost(req, unit)
        price = _price(req, unit)
        execution = req.payout_execution_id
        paid = req.net_payout if execution and execution.state == "executed" else 0.0
        rows.append(
            {
                "tradein": req.name,
                "model": req.device_model_id.name if req.device_model_id else "—",
                "grade": _grade_label(req.grade),
                "sold_on": str(day),
                "acquisition": round((unit.acquisition_cost if unit else 0.0) or 0.0, 2),
                "refurb": round(req.refurbishment_cost or 0.0, 2),
                "inventory": round(cost, 2),
                "resale": round(price, 2),
                "payout": round(paid or 0.0, 2),
                "margin": round(price - cost, 2),
                "margin_pct": pct(price - cost, price),
            }
        )
    rows.sort(key=lambda r: -r["margin"])
    totals = {"tradein": "Total"}
    for key in ("acquisition", "refurb", "inventory", "resale", "payout", "margin"):
        totals[key] = round(sum(r[key] for r in rows), 2)
    totals["margin_pct"] = pct(totals["margin"], totals["resale"])
    return _pack(
        "Unit Economics — units sold %s to %s" % (start, end),
        [
            "tradein",
            "model",
            "grade",
            "sold_on",
            "acquisition",
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
            "sold_on": "Sold On",
            "acquisition": "Acquisition Cost",
            "refurb": "Refurb Cost",
            "inventory": "Inventory Cost",
            "resale": "Resale Price",
            "payout": "Seller Payout Executed",
            "margin": "Margin",
            "margin_pct": "Gross Margin %",
        },
        rows,
        [
            "Gross margin % = margin ÷ resale price. Seller payout is the net payout "
            "once the M50 payment EXECUTED (a queued payout is not paid).",
            _PRICE_NOTE,
            period_note(start, end, "sale date"),
        ],
        totals=totals,
        empty="No refurbished unit sold in this window.",
    )


def valuation_queue(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    valuations = _scoped(
        env, "fix.tradein.valuation", [("valuated_on", ">=", start), ("valuated_on", "<=", end)]
    )
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
        "Valuation Queue — valuations %s to %s" % (start, end),
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
            "A manual override needs a stated reason before it can be applied.",
            period_note(start, end, "valuation date"),
        ],
        empty="No valuations in this window.",
    )


_FUNNEL = (
    ("draft", "Requests"),
    ("offered", "Offer Sent"),
    ("accepted", "Accepted"),
    ("collected", "Collected"),
    ("wiped", "Data Wiped"),
    ("graded", "Graded"),
    ("resale_ready", "Resale Ready"),
    ("closed", "Closed"),
)


def tradein_funnel(env, date_from=None, date_to=None, **params):
    """Spec §14 Trade-in funnel: requests opened in the period and the stage
    each reached (a rejected request counts at the stages it passed)."""
    start, end = window(env, date_from, date_to, days=90)
    lo, hi = utc_bounds(start, end)
    requests = _requests(env, [("create_date", ">=", lo), ("create_date", "<", hi)])
    order = [s for s, _l in env["fix.tradein.request"]._fields["state"].selection]
    reached = {}
    for state, _label in _FUNNEL[1:]:
        reached[state] = set(tracked_dates(env, requests, state))
    rows = []
    previous = None
    for state, label in _FUNNEL:
        if state == "draft":
            count = len(requests)
        else:
            idx = order.index(state)
            count = len(
                requests.filtered(
                    lambda r, s=state, i=idx: r.id in reached[s]
                    or (r.state != "rejected" and r.state in order and order.index(r.state) >= i)
                )
            )
        rows.append(
            {
                "stage": label,
                "requests": count,
                "conversion_pct": pct(count, previous) if previous is not None else 100.0,
                "of_requests_pct": pct(count, len(requests)),
            }
        )
        previous = count
    offered = rows[1]["requests"]
    accepted = rows[2]["requests"]
    revised = len(
        requests.filtered(lambda r: r.revision_state and r.revision_state not in ("none", False))
    )
    rejected = len(requests.filtered(lambda r: r.state == "rejected"))
    return _pack(
        "Trade-In Funnel — requests opened %s to %s" % (start, end),
        ["stage", "requests", "conversion_pct", "of_requests_pct"],
        {
            "stage": "Stage",
            "requests": "Requests Reaching It",
            "conversion_pct": "From Previous Stage %",
            "of_requests_pct": "Of All Requests %",
        },
        rows,
        [
            "Offer acceptance rate = %.1f%% (%d accepted of %d offered; spec target > 55%%). "
            "Offers revised at intake: %d (%.1f%% of accepted; target < 12%%). Rejected: %d."
            % (
                pct(accepted, offered),
                accepted,
                offered,
                revised,
                pct(revised, accepted),
                rejected,
            ),
            period_note(start, end, "request creation date"),
        ],
        empty="No trade-in requests opened in this window.",
    )


def _disclosure_measurable(env):
    return "buyer_disclosure_html" in env["fix.tradein.request"]._fields


def gate_compliance(env, date_from=None, date_to=None, **params):
    """Spec §15 M14 zero-target controls (gate compliance report)."""
    start, end = window(env, date_from, date_to, days=90)
    lo, hi = utc_bounds(start, end)
    requests = _requests(env)
    # 1. units processed (wiped onward / harvested) without a VERIFIED certificate
    processed = requests.filtered(
        lambda r: r.state in _WIPED_ONWARD and in_window(r.write_date, start, end)
    )
    no_cert = [
        r.name
        for r in processed
        if not r.wipe_certificate_id
        or (
            "sanitization_status" in r.wipe_certificate_id._fields
            and r.wipe_certificate_id.sanitization_status != "verified"
        )
    ]
    # 2. handsets purchased (accepted in the period) without a cleared IMEI check
    accepted = requests.filtered(lambda r: r.accepted_at and lo <= r.accepted_at < hi)
    no_imei = [
        r.name
        for r in accepted
        if not r.provenance_ids.filtered(lambda p: p.state == "cleared" and p.imei)
    ]
    # 3. units listed without a disclosure report (BRU-TRF-15)
    listed = requests.filtered(
        lambda r: (r.resale_listed_on and start <= r.resale_listed_on <= end)
        or (r.state == "resale_ready" and in_window(r.write_date, start, end))
    )
    measurable = _disclosure_measurable(env)
    no_disclosure = (
        [r.name for r in listed if not (r.buyer_disclosure_html or "").strip()]
        if measurable
        else []
    )
    # 4. stock units sold whose source unit has no verified certificate
    sold_no_cert = [
        unit.name
        for req, unit, _d in _sold(env, requests, start, end)
        if not req.wipe_certificate_id
    ]
    rows = [
        control_row("Units processed without a destruction / wipe certificate", no_cert),
        control_row("Handsets purchased without IMEI verification", no_imei),
        control_row(
            "Units listed without a disclosure report",
            no_disclosure,
            measurable=measurable,
            note="buyer_disclosure_html not installed yet (stream S2, I4)",
        ),
        control_row("Units sold without a wipe certificate", sold_no_cert),
    ]
    return _pack(
        "M14 Gate Compliance (Zero-Target Controls) — %s to %s" % (start, end),
        CONTROL_COLS,
        CONTROL_LABELS,
        rows,
        [
            "Spec §15: three M14 targets are zero - a single unit processed without a "
            "certificate is a reportable incident, not a missed target.",
            period_note(start, end, "processing, acceptance, listing and sale dates"),
        ],
        empty="No control data.",
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
    # A05 ERP audit XC-18: spec §14/§15 reports with no pack
    "tradein_funnel": tradein_funnel,
    "gate_compliance": gate_compliance,
}


def kpis(env):
    today = dhaka_today(env)
    year_start = today - datetime.timedelta(days=364)
    requests = _requests(env)
    pending_payout = requests.filtered(lambda r: r.payout_approval_state == "pending")
    resale_ready = requests.filtered(lambda r: r.state == "resale_ready")
    stock = _scoped(env, "fix.graded.stock")
    stock_by_req = _stock_by_request(env, requests)
    open_states = ("draft", "offered", "accepted", "collected", "wiped", "refurbished", "graded")
    # XC-14: stock value = units in stock or reserved; never sold or scrapped
    held = stock.filtered(lambda u: u.state in ("in_stock", "reserved"))
    in_stock = stock.filtered(lambda u: u.state == "in_stock")
    since = _in_stock_since(env, in_stock)
    aged = [u for u in in_stock if since.get(u.id) and (today - since[u.id]).days > 90]
    # XC-27: the pipeline is units not yet sold
    pipeline = requests.filtered(
        lambda r: r.state in ("graded", "resale_ready")
        and not (stock_by_req.get(r.id) and stock_by_req[r.id].state == "sold")
    )
    sold_12m = _sold(env, requests, year_start, today)
    revenue = sum(_price(req, unit) for req, unit, _d in sold_12m)
    margin = sum(_price(req, unit) - _cost(req, unit) for req, unit, _d in sold_12m)
    # KPI-077 yield: intake units (collected in 12 months) that became sellable
    collected = set(tracked_dates(env, requests, "collected"))
    intake = requests.filtered(
        lambda r: r.id in collected or (r.state in _WIPED_ONWARD and r.state != "rejected")
    ).filtered(lambda r: in_window(r.create_date, year_start, today))
    sellable = intake.filtered(lambda r: r.state in _RESALE_STATES and r.grade and r.grade != "e")
    # acceptance: of requests offered in 90 days
    recent = requests.filtered(
        lambda r: in_window(r.create_date, today - datetime.timedelta(days=89), today)
    )
    offered = set(tracked_dates(env, recent, "offered"))
    accepted_ids = set(tracked_dates(env, recent, "accepted"))
    offered_n = len([r for r in recent if r.id in offered or r.state not in ("draft", "rejected")])
    accepted_n = len(
        [
            r
            for r in recent
            if r.id in accepted_ids or r.state in ("accepted", "collected", *_WIPED_ONWARD)
        ]
    )
    # cycle time: purchase (accepted) to listed, units listed in 90 days
    listed = requests.filtered(
        lambda r: r.resale_listed_on
        and r.accepted_at
        and r.resale_listed_on >= today - datetime.timedelta(days=89)
    )
    cycle = [(r.resale_listed_on - to_dhaka_date(r.accepted_at)).days for r in listed]
    returns = (
        _scoped(env, "fix.refurb.return", [("return_date", ">=", year_start)])
        if "fix.refurb.return" in env
        else []
    )
    grades = (
        _scoped(env, "fix.tradein.grade", [("graded_on", ">=", year_start)])
        if "fix.tradein.grade" in env
        else []
    )
    overridden = [g for g in grades if "is_override" in g._fields and g.is_override]
    controls = gate_compliance(env, str(today - datetime.timedelta(days=89)), str(today))
    breaches = sum(r["actual"] for r in controls["rows"] if isinstance(r["actual"], int))
    return {
        "open_tradeins": len(requests.filtered(lambda r: r.state in open_states)),
        "pending_payouts": len(pending_payout),
        "refurb_open": len(_scoped(env, "fix.refurbishment", [("state", "=", "pending")])),
        "resale_ready": len(resale_ready),
        "graded_stock_value": round(sum(held.mapped("inventory_valuation")), 2),
        "margin_pipeline": round(
            sum(
                _price(r, stock_by_req.get(r.id)) - _cost(r, stock_by_req.get(r.id))
                for r in pipeline
            ),
            2,
        ),
        "refurb_yield_pct": pct(len(sellable), len(intake)) if intake else None,
        "units_sold_12m": len(sold_12m),
        "gross_margin_pct_12m": pct(margin, revenue) if revenue else None,
        "offer_acceptance_pct": pct(accepted_n, offered_n) if offered_n else None,
        "cycle_time_days": round(sum(cycle) / len(cycle), 1) if cycle else None,
        "return_rate_pct": pct(len(returns), len(sold_12m)) if sold_12m else None,
        "stock_over_90d_pct": pct(len(aged), len(in_stock)) if in_stock else None,
        "grade_override_pct": pct(len(overridden), len(grades)) if grades else None,
        "zero_target_breaches_90d": breaches,
    }
