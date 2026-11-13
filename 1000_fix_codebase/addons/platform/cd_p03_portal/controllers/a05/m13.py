# A05 · M13 Rental & Equipment-as-a-Service — surfaces, computed packs and
# KPIs over fix.rental.reservation/damage (existing) and the fleet, kit,
# deposit, condition and turnaround models. Every figure is a live search;
# depreciation is modelled under IAS 16 on fix.rental.asset, Rental P&L reports
# collected revenue, damage cost, and asset lifecycle contribution.
import datetime

# A05 audit (M13-18, E3/E5/E11): every workflow action has a button; the
# routed approvals are requested from the workspace (action_request_approval /
# action_recall_approval) and decided in the approver's M63 inbox, never by
# pressing Approve here. `writable` is attached from writable.py. The sets
# are literals: the FF-48 wiring check reads them statically.

SURFACES = {
    "fix.rental.asset": {
        "order": "name",
        "limit": 300,
        "actions": {
            "action_retire",
            "action_ready",
            "action_send_to_maintenance",
            "action_request_approval",
            "action_recall_approval",
        },
    },
    "fix.rental.kit": {"order": "name", "limit": 200, "actions": set()},
    "fix.rental.reservation": {
        "order": "date_from desc, id desc",
        "limit": 300,
        "actions": {
            "action_reserve",
            "action_deliver",
            "action_activate",
            "action_return",
            "action_assess_damage",
            "action_close",
            "action_cancel",
            "action_generate_delivery_consignment",
            "action_generate_return_consignment",
            "action_send_agreement",
            "action_sign_agreement",
            "action_reset_agreement",
            "action_issue_rental_invoice",
            "action_report_fault",
        },
    },
    "fix.rental.damage": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_waive",
            "action_request_charge_approval",
            "action_recall_charge_approval",
            "action_raise_dispute",
            "action_request_approval",
            "action_recall_approval",
        },
    },
    "fix.rental.deposit": {
        "order": "date desc, id desc",
        "limit": 300,
        "actions": {"action_repost_gl"},
    },
    "fix.rental.condition": {"order": "reported_on desc, id desc", "limit": 300, "actions": set()},
    "fix.rental.turnaround": {
        "order": "returned_on desc, id desc",
        "limit": 300,
        "actions": {"action_ready", "action_retire"},
    },
}

_OPEN_STATES = ("reserved", "delivered", "active")
_RENTED_STATES = ("reserved", "delivered", "active", "returned", "damage_assess", "closed")


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


def _today():
    return datetime.date.today()


def _window(date_from, date_to, days=30):
    end = _parse(date_to) or _today()
    start = _parse(date_from) or (end - datetime.timedelta(days=days - 1))
    return start, end


def _parse(value):
    if not value:
        return None
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _scope(env):
    """The caller's companies (A05 E2 / M13-19): a report or KPI never
    reads another company's rentals. Read as superuser inside that domain so
    a fleet figure is the company's, not only the caller's operating unit."""
    return [("company_id", "in", env.companies.ids)]


def _assets(env):
    return env["fix.rental.asset"].sudo().search(_scope(env))


def _reservations(env):
    return env["fix.rental.reservation"].sudo().search(_scope(env))


def _ledger(env):
    return env["fix.rental.deposit"].sudo().search(_scope(env))


def _held(moves):
    """Deposit still held per the GL: posted collections less deductions,
    forfeits and refunds (a refused or pending collection holds nothing)."""
    collected = sum(m.amount for m in moves if m.kind == "collect" and m.gl_state == "posted")
    out = sum(m.amount for m in moves if m.kind in ("refund", "deduction", "forfeit"))
    return collected - out


def _overlap_days(res, start, end):
    lo = max(res.date_from, start)
    hi = min(res.date_to, end)
    return max((hi - lo).days + 1, 0)


def utilisation_by_category(env, date_from=None, date_to=None, **params):
    start, end = _window(date_from, date_to)
    assets = _assets(env)
    reservations = _reservations(env).filtered(
        lambda r: r.state in _RENTED_STATES and r.date_from and r.date_to
    )
    rows = []
    for key, label in assets._fields["category"].selection:
        cat_assets = assets.filtered(lambda a, k=key: a.category == k)
        cat_res = reservations.filtered(
            lambda r, k=key: r.rental_asset_id and r.rental_asset_id.category == k
        )
        rented = sum(_overlap_days(r, start, end) for r in cat_res)
        capacity = len(cat_assets) * ((end - start).days + 1)
        rows.append(
            {
                "category": label,
                "assets": len(cat_assets),
                "rentals": len(cat_res),
                "rented_days": rented,
                "utilization_pct": round((rented / capacity) * 100.0, 1) if capacity else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["utilization_pct"])
    return _pack(
        "Utilisation by Category — %s to %s" % (start, end),
        ["category", "assets", "rentals", "rented_days", "utilization_pct"],
        {
            "category": "Category",
            "assets": "Assets",
            "rentals": "Rentals",
            "rented_days": "Rented Days",
            "utilization_pct": "Utilisation %",
        },
        rows,
        [
            "Utilisation = rented asset-days ÷ (fleet assets × days in the window). "
            "Only reservations assigned to a fleet asset count."
        ],
        totals={
            "category": "Total",
            "assets": sum(r["assets"] for r in rows),
            "rentals": sum(r["rentals"] for r in rows),
            "rented_days": sum(r["rented_days"] for r in rows),
        },
        empty="No fleet assets recorded yet.",
    )


def damage_loss_rate(env, date_from=None, date_to=None, **params):
    start, end = _window(date_from, date_to, days=90)
    reservations = _reservations(env).filtered(
        lambda r: r.state in _RENTED_STATES and r.date_from and start <= r.date_from <= end
    )
    rows = []
    for res in reservations:
        rows.append(
            {
                "rental": res.name,
                "customer": res.customer_id.name,
                "asset": res.rental_asset_id.name if res.rental_asset_id else "—",
                "rental_charge": round(res.rental_charge or 0.0, 2),
                "damage_cost": round(res.damage_total or 0.0, 2),
                "late_fee": round(res.late_fee or 0.0, 2),
                "rate_pct": round(((res.damage_total or 0.0) / res.rental_charge) * 100.0, 1)
                if res.rental_charge
                else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["damage_cost"])
    damage = sum(r["damage_cost"] for r in rows)
    charge = sum(r["rental_charge"] for r in rows)
    return _pack(
        "Damage & Loss Rate — rentals starting %s to %s" % (start, end),
        ["rental", "customer", "asset", "rental_charge", "damage_cost", "late_fee", "rate_pct"],
        {
            "rental": "Rental",
            "customer": "Customer",
            "asset": "Asset",
            "rental_charge": "Rental Charge",
            "damage_cost": "Damage Cost",
            "late_fee": "Late Fee",
            "rate_pct": "Damage % of Charge",
        },
        rows,
        ["Damage rate = recorded damage cost ÷ rental charge for the same rental."],
        totals={
            "rental": "Total",
            "rental_charge": round(charge, 2),
            "damage_cost": round(damage, 2),
            "rate_pct": round((damage / charge) * 100.0, 1) if charge else 0.0,
        },
        empty="No rentals started in this window.",
    )


def rental_pl(env, date_from=None, date_to=None, **params):
    start, end = _window(date_from, date_to, days=90)
    reservations = _reservations(env).filtered(
        lambda r: r.state in _RENTED_STATES and r.date_from and start <= r.date_from <= end
    )
    by_sku = {}
    for res in reservations:
        # reservations without a SKU link are ONE declared bucket — never one
        # row per reservation (a rental id is not a SKU)
        key = res.rental_sku_id.name if res.rental_sku_id else "Unassigned SKU"
        row = by_sku.setdefault(
            key,
            {
                "sku": key,
                "rentals": 0,
                "charge": 0.0,
                "late": 0.0,
                "damage_cost": 0.0,
                "recovered": 0.0,
                "refunded": 0.0,
            },
        )
        row["rentals"] += 1
        row["charge"] += res.rental_charge or 0.0
        row["late"] += res.late_fee or 0.0
        row["damage_cost"] += res.damage_total or 0.0
        row["recovered"] += sum(res.damage_ids.mapped("recovered_amount"))
        row["refunded"] += res.deposit_refunded or 0.0
    rows = []
    for row in by_sku.values():
        for key in ("charge", "late", "damage_cost", "recovered", "refunded"):
            row[key] = round(row[key], 2)
        # collected revenue net of what actually went back to customers
        row["net_revenue"] = round(row["charge"] + row["late"] - row["damage_cost"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["net_revenue"])
    return _pack(
        "Rental P&L — by rental SKU, rentals starting %s to %s" % (start, end),
        ["sku", "rentals", "charge", "late", "damage_cost", "recovered", "refunded", "net_revenue"],
        {
            "sku": "Rental SKU",
            "rentals": "Rentals",
            "charge": "Rental Charge",
            "late": "Late Fees",
            "damage_cost": "Damage Cost",
            "recovered": "Recovered",
            "refunded": "Deposit Refunded",
            "net_revenue": "Net (charge+late−damage)",
        },
        rows,
        [
            "Net = rental charge + late fees − recorded damage cost. Asset "
            "depreciation is tracked on fix.rental.asset under IAS 16 straight-line depreciation."
        ],
        totals={
            "sku": "Total",
            "rentals": sum(r["rentals"] for r in rows),
            "charge": round(sum(r["charge"] for r in rows), 2),
            "late": round(sum(r["late"] for r in rows), 2),
            "damage_cost": round(sum(r["damage_cost"] for r in rows), 2),
            "recovered": round(sum(r["recovered"] for r in rows), 2),
            "refunded": round(sum(r["refunded"] for r in rows), 2),
            "net_revenue": round(sum(r["net_revenue"] for r in rows), 2),
        },
        empty="No rentals started in this window.",
    )


def late_return(env, date_from=None, date_to=None, **params):
    start, end = _window(date_from, date_to, days=180)
    reservations = _reservations(env).filtered(
        lambda r: r.actual_return_date and r.date_to and r.actual_return_date > r.date_to
    )
    rows = []
    for res in reservations:
        if not (start <= res.actual_return_date <= end):
            continue
        days_late = (res.actual_return_date - res.date_to).days
        rows.append(
            {
                "rental": res.name,
                "customer": res.customer_id.name,
                "asset": res.rental_asset_id.name if res.rental_asset_id else "—",
                "due": str(res.date_to),
                "returned": str(res.actual_return_date),
                "days_late": days_late,
                "late_fee": round(res.late_fee or 0.0, 2),
            }
        )
    rows.sort(key=lambda r: -r["days_late"])
    return _pack(
        "Late Return Analysis — returns %s to %s" % (start, end),
        ["rental", "customer", "asset", "due", "returned", "days_late", "late_fee"],
        {
            "rental": "Rental",
            "customer": "Customer",
            "asset": "Asset",
            "due": "Due",
            "returned": "Returned",
            "days_late": "Days Late",
            "late_fee": "Late Fee",
        },
        rows,
        [
            "Late = actual return date after the promised date; the fee is the "
            "recorded 1.5× overdue charge."
        ],
        totals={
            "rental": "Total",
            "days_late": sum(r["days_late"] for r in rows),
            "late_fee": round(sum(r["late_fee"] for r in rows), 2),
        },
        empty="No late returns recorded in this window.",
    )


def deposit_reconciliation(env, date_from=None, date_to=None, **params):
    reservations = _reservations(env).filtered(
        lambda r: (r.deposit_collected or 0.0) > 0 or r.deposit_refunded
    )
    ledger = _ledger(env)
    rows = []
    for res in reservations:
        moves = ledger.filtered(lambda m, rid=res.id: m.reservation_id.id == rid)
        collected = sum(m.amount for m in moves if m.kind == "collect" and m.gl_state == "posted")
        unposted = sum(m.amount for m in moves if m.kind == "collect" and m.gl_state != "posted")
        refunded = sum(m.amount for m in moves if m.kind == "refund")
        deducted = sum(m.amount for m in moves if m.kind in ("deduction", "forfeit"))
        rows.append(
            {
                "rental": res.name,
                "customer": res.customer_id.name,
                "state": res.state,
                "collected": round(collected, 2),
                "refunded": round(refunded, 2),
                "deducted": round(deducted, 2),
                "outstanding": round(collected - refunded - deducted, 2),
                "unposted": round(unposted, 2),
                "ledger_rows": len(moves),
            }
        )
    rows.sort(key=lambda r: -r["outstanding"])
    return _pack(
        "Deposit Reconciliation — per rental",
        [
            "rental",
            "customer",
            "state",
            "collected",
            "refunded",
            "deducted",
            "outstanding",
            "unposted",
            "ledger_rows",
        ],
        {
            "rental": "Rental",
            "customer": "Customer",
            "state": "State",
            "collected": "Collected",
            "refunded": "Refunded",
            "deducted": "Deducted",
            "outstanding": "Outstanding",
            "unposted": "Not in GL",
            "ledger_rows": "Ledger Rows",
        },
        rows,
        [
            "Outstanding = GL-posted collections − refunded − deducted, from the "
            "deposit ledger — the reservation's own fields are not trusted for this. "
            "'Not in GL' is collected money whose posting was refused or is pending: "
            "repost it."
        ],
        totals={
            "rental": "Total",
            "collected": round(sum(r["collected"] for r in rows), 2),
            "refunded": round(sum(r["refunded"] for r in rows), 2),
            "deducted": round(sum(r["deducted"] for r in rows), 2),
            "outstanding": round(sum(r["outstanding"] for r in rows), 2),
            "unposted": round(sum(r["unposted"] for r in rows), 2),
        },
        empty="No deposits collected yet.",
    )


def availability(env, date_from=None, date_to=None, **params):
    today = _today()
    assets = _assets(env)
    reservations = _reservations(env).filtered(lambda r: r.state in _OPEN_STATES)
    rows = []
    for asset in assets:
        current = reservations.filtered(
            lambda r, aid=asset.id: r.rental_asset_id.id == aid and r.date_to >= today
        ).sorted("date_from")
        booking = current[:1]
        rows.append(
            {
                "asset": asset.name,
                "category": dict(asset._fields["category"].selection).get(asset.category),
                "status": dict(asset._fields["status"].selection).get(asset.status),
                "grade": asset.condition_grade.upper() if asset.condition_grade else "—",
                "battery_health_pct": asset.battery_health_pct,
                "next_from": str(booking.date_from) if booking else "—",
                "next_to": str(booking.date_to) if booking else "—",
                "next_customer": booking.customer_id.name if booking else "—",
            }
        )
    rows.sort(key=lambda r: (r["status"] != "Available", r["asset"]))
    return _pack(
        "Real-Time Availability — fleet status today",
        [
            "asset",
            "category",
            "status",
            "grade",
            "battery_health_pct",
            "next_from",
            "next_to",
            "next_customer",
        ],
        {
            "asset": "Asset",
            "category": "Category",
            "status": "Status",
            "grade": "Grade",
            "battery_health_pct": "Battery %",
            "next_from": "Booked From",
            "next_to": "Booked To",
            "next_customer": "Customer",
        },
        rows,
        [
            "Status is the asset's own state (available/reserved/on rent/maintenance/"
            "retired); the booking columns are the first open reservation still running."
        ],
        empty="No fleet assets recorded yet.",
    )


def fleet_health(env, date_from=None, date_to=None, **params):
    today = _today()
    assets = _assets(env)
    reservations = _reservations(env).filtered(lambda r: r.state in _RENTED_STATES)
    damage = env["fix.rental.damage"].sudo().search(_scope(env))
    rows = []
    for asset in assets:
        asset_res = reservations.filtered(lambda r, aid=asset.id: r.rental_asset_id.id == aid)
        asset_damage = damage.filtered(lambda d, ids=asset_res.ids: d.reservation_id.id in ids)
        age_months = 0
        if asset.acquisition_date:
            age_months = max(
                (today.year - asset.acquisition_date.year) * 12
                + (today.month - asset.acquisition_date.month),
                0,
            )
        reasons = []
        if asset.status == "retired":
            reasons.append("retired")
        if (asset.battery_health_pct or 100) < 60:
            reasons.append("battery <60%")
        if asset.condition_grade == "d":
            reasons.append("grade D")
        if age_months >= 48:
            reasons.append("age ≥48m")
        rows.append(
            {
                "asset": asset.name,
                "category": dict(asset._fields["category"].selection).get(asset.category),
                "status": dict(asset._fields["status"].selection).get(asset.status),
                "age_months": age_months,
                "battery_health_pct": asset.battery_health_pct,
                "rentals": len(asset_res),
                "damage_cost": round(sum(asset_damage.mapped("cost")), 2),
                "recommendation": "Retire" if reasons else "Keep",
                "reason": ", ".join(reasons) or "within thresholds",
            }
        )
    rows.sort(key=lambda r: (r["recommendation"] != "Retire", -r["age_months"]))
    return _pack(
        "Fleet Health & Retirement — measured thresholds",
        [
            "asset",
            "category",
            "status",
            "age_months",
            "battery_health_pct",
            "rentals",
            "damage_cost",
            "recommendation",
            "reason",
        ],
        {
            "asset": "Asset",
            "category": "Category",
            "status": "Status",
            "age_months": "Age (months)",
            "battery_health_pct": "Battery %",
            "rentals": "Rentals",
            "damage_cost": "Damage Cost",
            "recommendation": "Recommendation",
            "reason": "Trigger",
        },
        rows,
        [
            "Retirement triggers are explicit: retired status, battery below 60%, "
            "grade D or age 48+ months. Nothing is scored by a model."
        ],
        empty="No fleet assets recorded yet.",
    )


REPORTS = {
    "utilization_by_category": utilisation_by_category,
    "damage_loss_rate": damage_loss_rate,
    "rental_pl": rental_pl,
    "late_return": late_return,
    "deposit_reconciliation": deposit_reconciliation,
    "availability": availability,
    "fleet_health": fleet_health,
}


def kpis(env):
    assets = _assets(env)
    reservations = _reservations(env)
    ledger = _ledger(env)
    today = _today()
    start = today - datetime.timedelta(days=29)
    rented = reservations.filtered(
        lambda r: r.state in _RENTED_STATES and r.rental_asset_id and r.date_from and r.date_to
    )
    rented_days = sum(_overlap_days(r, start, today) for r in rented)
    capacity = len(assets) * 30
    # M13-14: deposits held are what the GL holds, not every typed row
    outstanding = _held(ledger)
    damage_open = (
        env["fix.rental.damage"].sudo().search_count([*_scope(env), ("settled", "=", False)])
    )
    return {
        "fleet_size": len(assets),
        "available_now": len(assets.filtered(lambda a: a.status == "available")),
        "active_rentals": len(reservations.filtered(lambda r: r.state == "active")),
        "deposits_held": round(outstanding, 2),
        "damage_recovery_open": damage_open,
        "utilization_30d": round((rented_days / capacity) * 100.0, 1) if capacity else 0.0,
    }
