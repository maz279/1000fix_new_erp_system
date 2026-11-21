# A05 · M13 Rental & Equipment-as-a-Service — surfaces, computed packs and
# KPIs over fix.rental.reservation/damage (existing) and the fleet, kit,
# deposit, condition and turnaround models. Every figure is a live search.
#
# A05 ERP audit (20 Nov 2026, XC-06/11/16/17/18/23/25/27, M13-23/27): every
# pack honours the period in Dhaka days, reads only what the caller's company
# and operating-unit rules allow, measures utilisation from hand-over to
# actual return over the days a unit was in the fleet, builds the Rental P&L
# by category from the invoices issued (recovered damage added; depreciation
# and loss subtracted), shows policy figures as the parameters in force, and
# adds the spec §14/§15 reports (overdue, damage recovery, turnaround, swap
# SLA, loss register, zero-target controls). The shared period/fence helpers
# below are imported by m14 and m18.
import datetime

import pytz
from odoo import fields

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
        },
    },
    # A05 ERP (S1, BRU-RNT-15): a unit retires only through an approved
    # retirement request (joint CSH + CFO, M06 wipe gate, route resale|recycle)
    "fix.rental.retirement": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval", "action_retire"},
        "pickers": {"asset_id": [("status", "in", ("available", "maintenance"))]},
    },
    # A05 ERP (S1, BRU-RNT-07): a deposit below the computed floor needs a
    # routed Finance Manager approval with a reason
    "fix.rental.deposit.reduction": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval"},
        "pickers": {"reservation_id": [("state", "=", "draft")]},
    },
    # A05 ERP (S1, FR-RNT-037): the cumulative billing ledger, read-only
    "fix.rental.billing": {"order": "id desc", "limit": 300, "actions": set()},
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
            # A05 ERP (S1): the M53 lease-term assessment of a long rental
            "action_record_lease_assessment",
        },
        # capture pass 2: allocation offers available units, the waiver
        # election published plans
        "pickers": {
            "rental_asset_id": [("status", "=", "available")],
            "waiver_plan_id": [("state", "=", "published")],
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
    # M13 capture pass 2 (2026-11-19): the records the spec names that had no
    # model. Pickers offer only what the server accepts: an available unit to
    # move, allocate or swap in; a condition report still at its stage; a
    # published waiver plan.
    "fix.rental.redeployment": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_dispatch", "action_receive", "action_cancel"},
        "pickers": {"rental_asset_id": [("status", "=", "available")]},
    },
    "fix.rental.pm.plan": {"order": "rental_sku_id, category, id", "limit": 200, "actions": set()},
    "fix.rental.exposure": {"order": "partner_id", "limit": 300, "actions": set()},
    # A05 ERP audit XC-02: an exposure override is decided in the approver's
    # M63 inbox (routed, tiered on the excess), never by a button here.
    "fix.rental.exposure.override": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval"},
        "pickers": {"reservation_id": [("state", "=", "draft")]},
    },
    "fix.rental.extension": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_apply", "action_reject"},
        "pickers": {"reservation_id": [("state", "in", ("delivered", "active"))]},
    },
    "fix.rental.waiver.plan": {
        "order": "state, name",
        "limit": 100,
        "actions": {"action_publish", "action_retire"},
    },
    "fix.rental.condition.photo": {
        "order": "condition_id, sequence, id",
        "limit": 500,
        "actions": set(),
        "pickers": {
            "condition_id": [
                "|",
                "&",
                ("report_type", "=", "pre_delivery"),
                ("reservation_id.state", "in", ("draft", "reserved")),
                "&",
                ("report_type", "=", "post_return"),
                ("reservation_id.state", "in", ("returned", "damage_assess")),
            ]
        },
    },
    "fix.rental.loss": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_escalate",
            "action_recover",
            "action_request_writeoff",
            "action_write_off",
            "action_recall_approval",
        },
        "pickers": {"reservation_id": [("state", "in", ("delivered", "active"))]},
    },
    "fix.rental.swap": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_execute", "action_cancel"},
        "pickers": {
            "reservation_id": [("state", "in", ("delivered", "active"))],
            "in_asset_id": [("status", "=", "available")],
        },
    },
}

_OPEN_STATES = ("reserved", "delivered", "active")
_RENTED_STATES = ("reserved", "delivered", "active", "returned", "damage_assess", "closed")
# A05 ERP audit XC-16: a unit is on rent from hand-over (delivered) to its
# actual return; a reservation that never left the shelf earns no rent-day.
_OUT_STATES = ("delivered", "active", "returned", "damage_assess", "closed")
DHAKA = "Asia/Dhaka"


# ---------------------------------------------------------------------------
# Shared A05 report helpers (m14 / m18 import them from here)
# ---------------------------------------------------------------------------
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


def dhaka_today(env):
    """A05 ERP audit XC-11: the business day is Dhaka's. Odoo forces the
    process to UTC, so datetime.date.today() is yesterday until 06:00."""
    return fields.Date.context_today(env["res.users"].with_context(tz=DHAKA))


def to_dhaka_date(stamp):
    """The Dhaka calendar day of a naive-UTC datetime (or a date as is)."""
    if not stamp:
        return None
    if isinstance(stamp, datetime.datetime):
        return pytz.utc.localize(stamp).astimezone(pytz.timezone(DHAKA)).date()
    return stamp


def _parse(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def window(env, date_from=None, date_to=None, days=30):
    """The report period in Dhaka days: (start, end), both inclusive. With no
    end the period ends today (Dhaka); with no start it covers `days` days."""
    end = _parse(date_to) or dhaka_today(env)
    start = _parse(date_from) or (end - datetime.timedelta(days=days - 1))
    if start > end:
        start, end = end, start
    return start, end


# kept for callers of the old private name
_window = window


def utc_bounds(start, end):
    """Naive-UTC [start 00:00 Dhaka, end+1 00:00 Dhaka) for datetime fields."""
    tz = pytz.timezone(DHAKA)
    lo = tz.localize(datetime.datetime.combine(start, datetime.time.min))
    hi = tz.localize(datetime.datetime.combine(end + datetime.timedelta(days=1), datetime.time.min))
    return (
        lo.astimezone(pytz.utc).replace(tzinfo=None),
        hi.astimezone(pytz.utc).replace(tzinfo=None),
    )


def in_window(day, start, end):
    day = to_dhaka_date(day)
    return bool(day) and start <= day <= end


def fenced(env, model, domain=None, order=None):
    """A05 ERP audit XC-23: the records the CALLER may read - the user's own
    search, so the company AND operating-unit record rules apply - inside the
    caller's companies. The result is returned as superuser only so related
    figures (a unit's category, a ledger's posting) can be read without a
    second access check per row; the set itself is the user's."""
    if model not in env:
        return None
    Model = env[model]
    base = [("company_id", "in", env.companies.ids)] if "company_id" in Model._fields else []
    ids = Model.search([*base, *(domain or [])], order=order).ids
    return Model.sudo().browse(ids)


def tracked_dates(env, records, value, field="state"):
    """{record id: Dhaka day the tracked selection `field` FIRST became
    `value`}, from the record's own tracking history (mail.tracking.value).
    A record with no tracked change is absent: the caller falls back."""
    if not records:
        return {}
    spec = records._fields.get(field)
    if spec is None or spec.type != "selection":
        return {}
    labels = {
        str(label) for key, label in (spec._description_selection(env) or []) if key == value
    } | {str(value)}
    env.cr.execute(
        """
        SELECT msg.res_id, MIN(msg.date)
          FROM mail_tracking_value val
          JOIN mail_message msg ON msg.id = val.mail_message_id
          JOIN ir_model_fields fld ON fld.id = val.field_id
         WHERE msg.model = %s
           AND msg.res_id = ANY(%s)
           AND fld.model = %s
           AND fld.name = %s
           AND val.new_value_char = ANY(%s)
         GROUP BY msg.res_id
        """,
        (records._name, list(records.ids), records._name, field, list(labels)),
    )
    return {res_id: to_dhaka_date(stamp) for res_id, stamp in env.cr.fetchall()}


def param(env, key, default=None):
    """An ir.config_parameter value, or `default` when unset/blank."""
    value = env["ir.config_parameter"].sudo().get_param(key)
    return default if value in (None, False, "") else value


def param_float(env, key, default=None):
    value = param(env, key, None)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def pct(part, whole, digits=1):
    return round((part / whole) * 100.0, digits) if whole else 0.0


def period_note(start, end, basis):
    return "Period %s to %s (Dhaka days), by %s." % (start, end, basis)


def control_row(control, refs, target=0, measurable=True, note=""):
    """One zero-target control (spec §15: a partial score is a control failure)."""
    count = len(refs)
    status = ("PASS" if count <= target else "BREACH") if measurable else "NOT MEASURED"
    return {
        "control": control,
        "target": target,
        "actual": count if measurable else "—",
        "status": status,
        "examples": ", ".join(str(r) for r in list(refs)[:8]) or ("—" if measurable else note),
    }


CONTROL_COLS = ["control", "target", "actual", "status", "examples"]
CONTROL_LABELS = {
    "control": "Control (spec §15 zero target)",
    "target": "Target",
    "actual": "Actual",
    "status": "Status",
    "examples": "Records",
}


# ---------------------------------------------------------------------------
# M13 reads
# ---------------------------------------------------------------------------
def _scope(env):
    return [("company_id", "in", env.companies.ids)]


def _assets(env):
    return fenced(env, "fix.rental.asset")


def _reservations(env, domain=None):
    return fenced(env, "fix.rental.reservation", domain)


def _ledger(env, reservations=None):
    """The deposit ledger of the reservations the caller may read (the
    ledger carries only a company rule: the reservation is the OU fence)."""
    reservations = _reservations(env) if reservations is None else reservations
    return (
        env["fix.rental.deposit"]
        .sudo()
        .search([("reservation_id", "in", reservations.ids)], order="date, id")
    )


def _held(moves):
    """Deposit still held per the GL: posted collections less POSTED
    deductions, forfeits and refunds. A queued refund (M50 has not confirmed
    the bank transfer) is still held by the ledger - A05 ERP audit XC-27."""
    collected = sum(m.amount for m in moves if m.kind == "collect" and m.gl_state == "posted")
    out = sum(
        m.amount
        for m in moves
        if m.kind in ("refund", "deduction", "forfeit") and m.gl_state == "posted"
    )
    return collected - out


def _overlap_days(lo, hi, start, end):
    if not (lo and hi):
        return 0
    lo = max(lo, start)
    hi = min(hi, end)
    return max((hi - lo).days + 1, 0)


def _delivered_on(env, reservations):
    """{reservation id: Dhaka day of hand-over}: the tracked move to
    'delivered', else the booked start (a legacy row with no history)."""
    tracked = tracked_dates(env, reservations, "delivered")
    return {r.id: tracked.get(r.id) or r.date_from for r in reservations}


def _rent_spans(env, reservations, today):
    """{reservation: (out_from, out_to)} for units that actually left: from
    hand-over to the actual return (still out: today)."""
    out = reservations.filtered(lambda r: r.state in _OUT_STATES and r.rental_asset_id)
    delivered = _delivered_on(env, out)
    spans = {}
    for res in out:
        lo = delivered.get(res.id)
        hi = res.actual_return_date or (today if res.state in ("delivered", "active") else None)
        if lo and hi and hi >= lo:
            spans[res] = (lo, hi)
    return spans


def _loss_dates(env, assets):
    """{asset id: Dhaka day the unit left the company's control} for open or
    written-off losses (a recovered unit came back)."""
    if "fix.rental.loss" not in env:
        return {}
    losses = (
        env["fix.rental.loss"]
        .sudo()
        .search([("rental_asset_id", "in", assets.ids), ("state", "in", ("open", "written_off"))])
    )
    out = {}
    for loss in losses:
        day = to_dhaka_date(loss.reported_at) or loss.written_off_on
        if day:
            aid = loss.rental_asset_id.id
            out[aid] = min(out.get(aid, day), day)
    return out


def _available_days(asset, start, end, lost_from=None):
    """Days in [start, end] the unit was in the fleet: acquired, not yet
    retired, not lost. A retired unit with no retirement day is excluded."""
    if asset.status == "retired" and not asset.retired_on:
        return 0
    lo = max(start, asset.acquisition_date or start)
    hi = end
    if asset.retired_on:
        hi = min(hi, asset.retired_on - datetime.timedelta(days=1))
    if lost_from:
        hi = min(hi, lost_from - datetime.timedelta(days=1))
    return max((hi - lo).days + 1, 0)


def _category_label(env, key):
    return dict(env["fix.rental.asset"]._fields["category"].selection).get(key, key or "Other")


def _net_taxable(invoice):
    """Ex-VAT value of an issued invoice, less what a credit note took back."""
    taxable = invoice.taxable_amount or 0.0
    total = invoice.total_payable or 0.0
    credited = invoice.credited_amount or 0.0
    if credited and total:
        taxable *= max(1.0 - credited / total, 0.0)
    return taxable


_RECOVERY_SOURCES = ("fix.rental.damage", "fix.rental.loss")


def _rental_invoices(env, reservations, start, end):
    """[(reservation, invoice, kind)] for the M20 invoices issued in the
    period for these rentals: kind 'rental' (rental charge, extensions, late
    fees, waiver fees - D1 rental income) or 'recovery' (damage, loss,
    charges above the deposit - D1 recovery income). Read from the invoices
    themselves, never the reservation's contracted charge (XC-17)."""
    if "fix.ar.invoice" not in env or not reservations:
        return []
    Invoice = env["fix.ar.invoice"].sudo()
    by_id = {r.id: r for r in reservations}
    excess = {r.excess_invoice_id.id: r for r in reservations if r.excess_invoice_id}
    domain = [
        ("company_id", "in", env.companies.ids),
        ("state", "not in", ("draft", "cancelled")),
        ("invoice_date", ">=", start),
        ("invoice_date", "<=", end),
    ]
    found = Invoice.search(
        [*domain, "|", ("source_model", "=like", "fix.rental.%"), ("id", "in", list(excess))]
    )
    out = []
    for inv in found:
        res, kind = None, "rental"
        if inv.id in excess:
            res, kind = excess[inv.id], "recovery"
        elif inv.source_model == "fix.rental.reservation":
            res = by_id.get(inv.source_id)
        elif inv.source_model in env:
            source = env[inv.source_model].sudo().browse(inv.source_id).exists()
            holder = (
                source.reservation_id if source and "reservation_id" in source._fields else None
            )
            res = by_id.get(holder.id) if holder else None
            if inv.source_model in _RECOVERY_SOURCES:
                kind = "recovery"
        if res:
            out.append((res, inv, kind))
    return out


def _depreciation(asset, start, end, lost_from=None):
    days = _available_days(asset, start, end, lost_from)
    return (asset.daily_depreciation or 0.0) * days


# ---------------------------------------------------------------------------
# M13 packs
# ---------------------------------------------------------------------------
def utilisation_by_category(env, date_from=None, date_to=None, **params):
    """KPI-075 time utilisation (days on rent ÷ days available, hand-over to
    actual return; retired and lost units are not capacity) and financial
    utilisation (annualised invoiced rental revenue ÷ acquisition cost)."""
    start, end = window(env, date_from, date_to)
    today = dhaka_today(env)
    assets = _assets(env)
    reservations = _reservations(env)
    spans = _rent_spans(env, reservations, today)
    lost = _loss_dates(env, assets)
    invoices = _rental_invoices(env, reservations, start, end)
    period_days = (end - start).days + 1
    rows = []
    for key, label in assets._fields["category"].selection:
        cat_assets = assets.filtered(lambda a, k=key: a.category == k)
        available = {a.id: _available_days(a, start, end, lost.get(a.id)) for a in cat_assets}
        in_fleet = cat_assets.filtered(lambda a, av=available: av[a.id] > 0)
        rented = 0
        rentals = 0
        for res, (lo, hi) in spans.items():
            asset = res.rental_asset_id
            if asset.category != key or not available.get(asset.id):
                continue
            days = _overlap_days(lo, hi, start, end)
            if days:
                rentals += 1
                rented += min(days, available[asset.id])
        capacity = sum(available.values())
        revenue = sum(
            _net_taxable(inv)
            for res, inv, kind in invoices
            if kind == "rental" and res.rental_asset_id.category == key
        )
        cost = sum(in_fleet.mapped("purchase_cost"))
        annualised = revenue * 365.0 / period_days if period_days else 0.0
        if not (cat_assets or rentals):
            continue
        rows.append(
            {
                "category": label,
                "assets": len(in_fleet),
                "rentals": rentals,
                "available_days": capacity,
                "rented_days": rented,
                "utilization_pct": pct(rented, capacity),
                "revenue": round(revenue, 2),
                "acquisition_cost": round(cost, 2),
                "financial_util_pct": pct(annualised, cost),
            }
        )
    rows.sort(key=lambda r: -r["utilization_pct"])
    capacity = sum(r["available_days"] for r in rows)
    rented = sum(r["rented_days"] for r in rows)
    revenue = sum(r["revenue"] for r in rows)
    cost = sum(r["acquisition_cost"] for r in rows)
    return _pack(
        "Utilisation by Category — %s to %s" % (start, end),
        [
            "category",
            "assets",
            "rentals",
            "available_days",
            "rented_days",
            "utilization_pct",
            "revenue",
            "acquisition_cost",
            "financial_util_pct",
        ],
        {
            "category": "Category",
            "assets": "Units in Fleet",
            "rentals": "Rentals",
            "available_days": "Days Available",
            "rented_days": "Days on Rent",
            "utilization_pct": "Time Utilisation %",
            "revenue": "Rental Revenue (ex-VAT)",
            "acquisition_cost": "Acquisition Cost",
            "financial_util_pct": "Financial Utilisation % (annualised)",
        },
        rows,
        [
            "KPI-075 time utilisation = days on rent ÷ days available. A unit is on "
            "rent from hand-over (delivered) to its actual return; a reservation that "
            "was never handed over earns nothing. Days available exclude days before "
            "acquisition, after retirement and after a loss was reported.",
            "Financial utilisation = invoiced rental revenue (ex-VAT, issued M20 "
            "invoices in the period) annualised ÷ acquisition cost of the units in the "
            "fleet (spec FR-RNT-006).",
            period_note(start, end, "rent-day overlap and invoice date"),
        ],
        totals={
            "category": "Total",
            "assets": sum(r["assets"] for r in rows),
            "rentals": sum(r["rentals"] for r in rows),
            "available_days": capacity,
            "rented_days": rented,
            "utilization_pct": pct(rented, capacity),
            "revenue": round(revenue, 2),
            "acquisition_cost": round(cost, 2),
            "financial_util_pct": pct(revenue * 365.0 / ((end - start).days + 1), cost),
        },
        empty="No fleet assets recorded yet.",
    )


def damage_loss_rate(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=90)
    reservations = _reservations(env).filtered(
        lambda r: r.state in _RENTED_STATES and r.date_from and start <= r.date_from <= end
    )
    rows = []
    for res in reservations:
        assessed = res.damage_total or 0.0
        recovered = sum(res.damage_ids.mapped("recovered_amount"))
        rows.append(
            {
                "rental": res.name,
                "customer": res.customer_id.name,
                "asset": res.rental_asset_id.name if res.rental_asset_id else "—",
                "rental_charge": round(res.rental_charge or 0.0, 2),
                "damage_cost": round(assessed, 2),
                "recovered": round(recovered, 2),
                "late_fee": round(res.late_fee or 0.0, 2),
                "rate_pct": pct(assessed, res.rental_charge or 0.0),
                "recovery_pct": pct(recovered, assessed),
            }
        )
    rows.sort(key=lambda r: -r["damage_cost"])
    damage = sum(r["damage_cost"] for r in rows)
    charge = sum(r["rental_charge"] for r in rows)
    recovered = sum(r["recovered"] for r in rows)
    return _pack(
        "Damage & Loss Rate — rentals starting %s to %s" % (start, end),
        [
            "rental",
            "customer",
            "asset",
            "rental_charge",
            "damage_cost",
            "recovered",
            "late_fee",
            "rate_pct",
            "recovery_pct",
        ],
        {
            "rental": "Rental",
            "customer": "Customer",
            "asset": "Asset",
            "rental_charge": "Rental Charge",
            "damage_cost": "Damage Assessed",
            "recovered": "Recovered",
            "late_fee": "Late Fee",
            "rate_pct": "Damage % of Charge",
            "recovery_pct": "Recovery % (KPI-076)",
        },
        rows,
        [
            "Damage rate = assessed damage cost ÷ rental charge for the same rental. "
            "KPI-076 damage recovery rate = recovered ÷ assessed (recovered = deposit "
            "deductions linked to the damage line).",
            period_note(start, end, "rental start date"),
        ],
        totals={
            "rental": "Total",
            "rental_charge": round(charge, 2),
            "damage_cost": round(damage, 2),
            "recovered": round(recovered, 2),
            "rate_pct": pct(damage, charge),
            "recovery_pct": pct(recovered, damage),
        },
        empty="No rentals started in this window.",
    )


def rental_pl(env, date_from=None, date_to=None, **params):
    """Spec §14 Rental P&L by category (XC-17 / M13-23): revenue from the
    invoices issued, recovered damage added, damage cost, depreciation and
    loss subtracted."""
    start, end = window(env, date_from, date_to, days=90)
    assets = _assets(env)
    reservations = _reservations(env)
    lost = _loss_dates(env, assets)
    rows = {}

    def row(key):
        return rows.setdefault(
            key or "other",
            {
                "category": _category_label(env, key or "other"),
                "revenue": 0.0,
                "recovered": 0.0,
                "damage": 0.0,
                "depreciation": 0.0,
                "loss": 0.0,
            },
        )

    for res, inv, kind in _rental_invoices(env, reservations, start, end):
        target = row(res.rental_asset_id.category or "other")
        target["revenue" if kind == "rental" else "recovered"] += _net_taxable(inv)
    # deposit deductions and forfeits are recovery income (D1 400111) when posted
    for move in _ledger(env, reservations):
        if (
            move.kind in ("deduction", "forfeit")
            and move.gl_state == "posted"
            and start <= move.date <= end
        ):
            row(move.reservation_id.rental_asset_id.category)["recovered"] += move.amount
    damages = env["fix.rental.damage"].sudo().search([("reservation_id", "in", reservations.ids)])
    for dmg in damages:
        if dmg.incident_date and start <= dmg.incident_date <= end:
            row(dmg.reservation_id.rental_asset_id.category)["damage"] += dmg.cost or 0.0
    for asset in assets:
        dep = _depreciation(asset, start, end, lost.get(asset.id))
        if dep:
            row(asset.category)["depreciation"] += dep
    if "fix.rental.loss" in env:
        for loss in (
            env["fix.rental.loss"]
            .sudo()
            .search([("reservation_id", "in", reservations.ids), ("state", "=", "written_off")])
        ):
            if loss.written_off_on and start <= loss.written_off_on <= end:
                row(loss.rental_asset_id.category)["loss"] += loss.valuation or 0.0
    out = []
    for vals in rows.values():
        for key in ("revenue", "recovered", "damage", "depreciation", "loss"):
            vals[key] = round(vals[key], 2)
        vals["gross_margin"] = round(
            vals["revenue"]
            + vals["recovered"]
            - vals["damage"]
            - vals["depreciation"]
            - vals["loss"],
            2,
        )
        vals["margin_pct"] = pct(vals["gross_margin"], vals["revenue"])
        out.append(vals)
    out.sort(key=lambda r: -r["gross_margin"])
    totals = {"category": "Total"}
    for key in ("revenue", "recovered", "damage", "depreciation", "loss", "gross_margin"):
        totals[key] = round(sum(r[key] for r in out), 2)
    totals["margin_pct"] = pct(totals["gross_margin"], totals["revenue"])
    return _pack(
        "Rental P&L by Category — %s to %s" % (start, end),
        [
            "category",
            "revenue",
            "recovered",
            "damage",
            "depreciation",
            "loss",
            "gross_margin",
            "margin_pct",
        ],
        {
            "category": "Category",
            "revenue": "Rental Revenue (invoiced, ex-VAT)",
            "recovered": "Damage / Loss Recovered",
            "damage": "Damage Cost (direct)",
            "depreciation": "Depreciation",
            "loss": "Asset Loss Written Off",
            "gross_margin": "Gross Margin",
            "margin_pct": "Margin %",
        },
        out,
        [
            "Revenue = rental, extension, late-fee and waiver charges on M20 invoices "
            "issued in the period (ex-VAT, net of credit notes) - not the contracted "
            "charge of an unbilled reservation.",
            "Recovered = posted deposit deductions/forfeits + damage, loss and "
            "above-deposit invoices issued in the period. Damage cost = assessed "
            "repair cost of incidents in the period.",
            "Depreciation = each unit's straight-line daily depreciation x its days in "
            "the fleet in the period (retired / lost units stop). Loss = the recorded "
            "valuation of units written off in the period.",
            "Gross margin = revenue + recovered - damage - depreciation - loss; "
            "margin % on revenue.",
            period_note(start, end, "invoice, ledger, incident and write-off date"),
        ],
        totals=totals,
        empty="No rental revenue or cost in this window.",
    )


def late_return(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=180)
    reservations = _reservations(env).filtered(
        lambda r: r.actual_return_date
        and r.date_to
        and r.actual_return_date > r.date_to
        and start <= r.actual_return_date <= end
    )
    rows = []
    for res in reservations:
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
    multiplier = param(env, "cd_rental_asset.late_fee_multiplier", "1.5 (default)")
    grace = param(env, "cd_rental_asset.late_fee_grace_days", "0 (default)")
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
            "Late = actual return date after the promised date. The fee is the one "
            "recorded on the rental, at the configured policy: "
            "cd_rental_asset.late_fee_multiplier = %s x the daily rate per late day, "
            "after cd_rental_asset.late_fee_grace_days = %s grace day(s)." % (multiplier, grace),
            period_note(start, end, "actual return date"),
        ],
        totals={
            "rental": "Total",
            "days_late": sum(r["days_late"] for r in rows),
            "late_fee": round(sum(r["late_fee"] for r in rows), 2),
        },
        empty="No late returns recorded in this window.",
    )


def deposit_reconciliation(env, date_from=None, date_to=None, **params):
    """The deposit position AT the period end (ledger rows dated on or before
    it) with the period's own movements, per rental (M13-27)."""
    start, end = window(env, date_from, date_to, days=30)
    reservations = _reservations(env)
    ledger = _ledger(env, reservations).filtered(lambda m: m.date and m.date <= end)
    by_res = {}
    for move in ledger:
        by_res.setdefault(move.reservation_id.id, []).append(move)
    rows = []
    for res in reservations:
        moves = by_res.get(res.id) or []
        if not moves:
            continue
        posted = [m for m in moves if m.gl_state == "posted"]
        collected = sum(m.amount for m in posted if m.kind == "collect")
        refunded = sum(m.amount for m in posted if m.kind == "refund")
        deducted = sum(m.amount for m in posted if m.kind in ("deduction", "forfeit"))
        unposted = sum(m.amount for m in moves if m.kind == "collect" and m.gl_state != "posted")
        queued = sum(m.amount for m in moves if m.kind == "refund" and m.gl_state != "posted")
        moved = [m for m in moves if start <= m.date <= end]
        outstanding = collected - refunded - deducted
        if not moved and not outstanding and not unposted and not queued:
            continue
        rows.append(
            {
                "rental": res.name,
                "customer": res.customer_id.name,
                "state": res.state,
                "collected": round(collected, 2),
                "refunded": round(refunded, 2),
                "deducted": round(deducted, 2),
                "outstanding": round(outstanding, 2),
                "refund_queued": round(queued, 2),
                "unposted": round(unposted, 2),
                "period_rows": len(moved),
            }
        )
    rows.sort(key=lambda r: -r["outstanding"])
    keys = ("collected", "refunded", "deducted", "outstanding", "refund_queued", "unposted")
    totals = {"rental": "Total"}
    for key in keys:
        totals[key] = round(sum(r[key] for r in rows), 2)
    return _pack(
        "Deposit Reconciliation — position at %s, movements %s to %s" % (end, start, end),
        [
            "rental",
            "customer",
            "state",
            "collected",
            "refunded",
            "deducted",
            "outstanding",
            "refund_queued",
            "unposted",
            "period_rows",
        ],
        {
            "rental": "Rental",
            "customer": "Customer",
            "state": "State",
            "collected": "Collected (GL)",
            "refunded": "Refunded (GL)",
            "deducted": "Deducted (GL)",
            "outstanding": "Held at Period End",
            "refund_queued": "Refund Queued (M50)",
            "unposted": "Collected, Not in GL",
            "period_rows": "Movements in Period",
        },
        rows,
        [
            "Held = GL-posted collections − GL-posted refunds, deductions and "
            "forfeits dated on or before the period end, from the deposit ledger. A "
            "refund queued at M50 is still held until the bank confirms it left. "
            "'Collected, Not in GL' is money whose posting was refused or is pending: "
            "repost it.",
            period_note(start, end, "ledger date"),
        ],
        totals=totals,
        empty="No deposit movements in this window.",
    )


def availability(env, date_from=None, date_to=None, **params):
    today = dhaka_today(env)
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
        "Real-Time Availability — fleet status on %s" % today,
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
            "retired); the booking columns are the first open reservation still running "
            "on or after today (Dhaka). A real-time board: the period does not apply."
        ],
        empty="No fleet assets recorded yet.",
    )


def _retirement_policy(env):
    """XC-25: the retirement triggers are parameters, never figures in code.
    The first three keep the triggers the fleet has used; the spec's own
    triggers (repair cost against written-down value, utilisation floor) are
    off until the owner sets them (spec AUT-RNT-15, owner question Q-08)."""
    return {
        "battery": param_float(env, "cd_rental_asset.retire_battery_below_pct", 60.0),
        "grade": str(param(env, "cd_rental_asset.retire_grade", "d")).lower(),
        "age": param_float(env, "cd_rental_asset.retire_age_months", 48.0),
        "repair_wdv": param_float(env, "cd_rental_asset.retire_repair_cost_wdv_pct", None),
        "util_floor": param_float(env, "cd_rental_asset.retire_utilisation_floor_pct", None),
    }


def fleet_health(env, date_from=None, date_to=None, **params):
    start, end = window(env, date_from, date_to, days=180)
    policy = _retirement_policy(env)
    assets = _assets(env)
    reservations = _reservations(env).filtered(lambda r: r.state in _RENTED_STATES)
    spans = _rent_spans(env, reservations, dhaka_today(env))
    lost = _loss_dates(env, assets)
    damage = env["fix.rental.damage"].sudo().search([("reservation_id", "in", reservations.ids)])
    rows = []
    for asset in assets:
        asset_res = reservations.filtered(lambda r, aid=asset.id: r.rental_asset_id.id == aid)
        asset_damage = damage.filtered(
            lambda d, ids=asset_res.ids: d.reservation_id.id in ids
            and (not d.incident_date or d.incident_date <= end)
        )
        age_months = 0
        if asset.acquisition_date:
            age_months = max(
                (end.year - asset.acquisition_date.year) * 12
                + (end.month - asset.acquisition_date.month),
                0,
            )
        available = _available_days(asset, start, end, lost.get(asset.id))
        rented = sum(
            min(_overlap_days(lo, hi, start, end), available)
            for res, (lo, hi) in spans.items()
            if res.rental_asset_id.id == asset.id
        )
        util = pct(rented, available)
        wdv = asset.net_book_value or 0.0
        repair = (asset.total_repair_cost or 0.0) + sum(asset_damage.mapped("cost"))
        reasons = []
        if asset.status == "retired":
            reasons.append("retired")
        if (asset.battery_health_pct or 100) < policy["battery"]:
            reasons.append("battery <%g%%" % policy["battery"])
        if asset.condition_grade and asset.condition_grade == policy["grade"]:
            reasons.append("grade %s" % policy["grade"].upper())
        if age_months >= policy["age"]:
            reasons.append("age ≥%gm" % policy["age"])
        if policy["repair_wdv"] is not None and wdv and pct(repair, wdv) >= policy["repair_wdv"]:
            reasons.append("repair ≥%g%% of WDV" % policy["repair_wdv"])
        if policy["util_floor"] is not None and available and util < policy["util_floor"]:
            reasons.append("utilisation <%g%%" % policy["util_floor"])
        rows.append(
            {
                "asset": asset.name,
                "category": dict(asset._fields["category"].selection).get(asset.category),
                "status": dict(asset._fields["status"].selection).get(asset.status),
                "age_months": age_months,
                "battery_health_pct": asset.battery_health_pct,
                "rentals": len(asset_res),
                "utilization_pct": util,
                "repair_cost": round(repair, 2),
                "wdv": round(wdv, 2),
                "recommendation": "Retire" if reasons else "Keep",
                "reason": ", ".join(reasons) or "within thresholds",
            }
        )
    rows.sort(key=lambda r: (r["recommendation"] != "Retire", -r["age_months"]))

    def shown(value, unit=""):
        return ("%g%s" % (value, unit)) if value is not None else "not set (owner decision Q-08)"

    return _pack(
        "Fleet Health & Retirement — %s to %s" % (start, end),
        [
            "asset",
            "category",
            "status",
            "age_months",
            "battery_health_pct",
            "rentals",
            "utilization_pct",
            "repair_cost",
            "wdv",
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
            "utilization_pct": "Utilisation % (period)",
            "repair_cost": "Repair + Damage Cost",
            "wdv": "Written-Down Value",
            "recommendation": "Recommendation",
            "reason": "Trigger",
        },
        rows,
        [
            "Retirement triggers are configuration (ir.config_parameter), shown here as "
            "in force: cd_rental_asset.retire_battery_below_pct = %s; "
            "cd_rental_asset.retire_grade = %s; cd_rental_asset.retire_age_months = %s; "
            "cd_rental_asset.retire_repair_cost_wdv_pct = %s; "
            "cd_rental_asset.retire_utilisation_floor_pct = %s."
            % (
                shown(policy["battery"], "%"),
                policy["grade"].upper(),
                shown(policy["age"]),
                shown(policy["repair_wdv"], "%"),
                shown(policy["util_floor"], "%"),
            ),
            period_note(start, end, "rent-day overlap (utilisation) and age at period end"),
        ],
        empty="No fleet assets recorded yet.",
    )


_AGE_BANDS = ((1, 3, "1–3 days"), (4, 7, "4–7 days"), (8, 14, "8–14 days"), (15, 30, "15–30 days"))


def _age_band(days):
    for lo, hi, label in _AGE_BANDS:
        if lo <= days <= hi:
            return label
    return "over 30 days"


def overdue_recovery(env, date_from=None, date_to=None, **params):
    """Spec §14 Overdue and recovery report: units past due at the period end
    by age band, the charge accrued and the escalation stage."""
    start, end = window(env, date_from, date_to, days=30)
    as_at = min(end, dhaka_today(env))
    reservations = _reservations(env).filtered(
        lambda r: r.date_to
        and r.date_to < as_at
        and (
            r.state in ("delivered", "active")
            or (r.actual_return_date and r.actual_return_date > as_at)
        )
    )
    losses = {}
    if "fix.rental.loss" in env:
        for loss in (
            env["fix.rental.loss"].sudo().search([("reservation_id", "in", reservations.ids)])
        ):
            losses[loss.reservation_id.id] = loss
    stages = dict(env["fix.rental.loss"]._fields["escalation_stage"].selection) if losses else {}
    rows = []
    for res in reservations:
        days = (as_at - res.date_to).days
        try:
            accrued = res._late_fee_on(as_at)
        except Exception:  # a policy read never breaks the report
            accrued = res.late_fee or 0.0
        loss = losses.get(res.id)
        rows.append(
            {
                "rental": res.name,
                "customer": res.customer_id.name,
                "asset": res.rental_asset_id.name if res.rental_asset_id else "—",
                "due": str(res.date_to),
                "days_overdue": days,
                "age_band": _age_band(days),
                "accrued_late_fee": round(accrued or 0.0, 2),
                "deposit_held": round(_held(res.deposit_ids), 2),
                "escalation": stages.get(loss.escalation_stage, "—") if loss else "Reminder",
            }
        )
    rows.sort(key=lambda r: -r["days_overdue"])
    return _pack(
        "Overdue & Recovery — units past due at %s" % as_at,
        [
            "rental",
            "customer",
            "asset",
            "due",
            "days_overdue",
            "age_band",
            "accrued_late_fee",
            "deposit_held",
            "escalation",
        ],
        {
            "rental": "Rental",
            "customer": "Customer",
            "asset": "Asset",
            "due": "Due Back",
            "days_overdue": "Days Overdue",
            "age_band": "Age Band",
            "accrued_late_fee": "Late Fee Accrued",
            "deposit_held": "Deposit Held (GL)",
            "escalation": "Escalation Stage",
        },
        rows,
        [
            "Units still out (delivered/active) past their return date at the period end "
            "(or today, whichever is earlier). The late fee accrued is the rental's own "
            "policy calculation at that date; escalation is the loss record's stage.",
            period_note(start, end, "position at period end"),
        ],
        totals={
            "rental": "Total",
            "accrued_late_fee": round(sum(r["accrued_late_fee"] for r in rows), 2),
            "deposit_held": round(sum(r["deposit_held"] for r in rows), 2),
        },
        empty="No unit is overdue.",
    )


def damage_recovery(env, date_from=None, date_to=None, **params):
    """Spec §14 Damage and recovery report (KPI-076 by damage category)."""
    start, end = window(env, date_from, date_to, days=90)
    reservations = _reservations(env)
    damages = (
        env["fix.rental.damage"]
        .sudo()
        .search([("reservation_id", "in", reservations.ids)])
        .filtered(lambda d: d.incident_date and start <= d.incident_date <= end)
    )
    labels = dict(env["fix.rental.damage"]._fields["category"].selection)
    rows = {}
    for dmg in damages:
        row = rows.setdefault(
            dmg.category,
            {
                "category": labels.get(dmg.category, dmg.category),
                "incidents": 0,
                "assessed": 0.0,
                "recovered": 0.0,
                "waived": 0.0,
                "disputed": 0,
                "waiver_cover": 0,
            },
        )
        row["incidents"] += 1
        row["assessed"] += dmg.cost or 0.0
        row["recovered"] += dmg.recovered_amount or 0.0
        row["waived"] += dmg.waived_amount or 0.0
        row["disputed"] += 1 if dmg.disputed else 0
        if "waiver_plan_id" in dmg.reservation_id._fields and dmg.reservation_id.waiver_plan_id:
            row["waiver_cover"] += 1
    out = []
    for row in rows.values():
        for key in ("assessed", "recovered", "waived"):
            row[key] = round(row[key], 2)
        row["recovery_pct"] = pct(row["recovered"], row["assessed"])
        out.append(row)
    out.sort(key=lambda r: -r["assessed"])
    assessed = sum(r["assessed"] for r in out)
    recovered = sum(r["recovered"] for r in out)
    return _pack(
        "Damage & Recovery — incidents %s to %s" % (start, end),
        [
            "category",
            "incidents",
            "assessed",
            "recovered",
            "waived",
            "recovery_pct",
            "disputed",
            "waiver_cover",
        ],
        {
            "category": "Damage Category",
            "incidents": "Incidents",
            "assessed": "Assessed",
            "recovered": "Recovered",
            "waived": "Waived (DOFA)",
            "recovery_pct": "Recovery % (KPI-076)",
            "disputed": "Disputed",
            "waiver_cover": "Under a Waiver Plan",
        },
        out,
        [
            "KPI-076 damage recovery rate = recovered ÷ assessed (target > 85%). "
            "Recovered = deposit deductions linked to the damage line.",
            period_note(start, end, "incident date"),
        ],
        totals={
            "category": "Total",
            "incidents": sum(r["incidents"] for r in out),
            "assessed": round(assessed, 2),
            "recovered": round(recovered, 2),
            "waived": round(sum(r["waived"] for r in out), 2),
            "recovery_pct": pct(recovered, assessed),
            "disputed": sum(r["disputed"] for r in out),
        },
        empty="No damage recorded in this window.",
    )


def _turnaround_hours(turn):
    if not (turn.returned_on and turn.ready_timestamp):
        return None
    tz = pytz.timezone(DHAKA)
    returned = tz.localize(datetime.datetime.combine(turn.returned_on, datetime.time.min))
    ready = pytz.utc.localize(turn.ready_timestamp)
    return max((ready - returned).total_seconds() / 3600.0, 0.0)


def turnaround_performance(env, date_from=None, date_to=None, **params):
    """Spec §14 Turnaround performance: return to available, by category."""
    start, end = window(env, date_from, date_to, days=30)
    assets = _assets(env)
    turns = (
        env["fix.rental.turnaround"]
        .sudo()
        .search(
            [
                ("rental_asset_id", "in", assets.ids),
                ("returned_on", ">=", start),
                ("returned_on", "<=", end),
            ]
        )
    )
    rows = {}
    for turn in turns:
        key = turn.rental_asset_id.category
        row = rows.setdefault(
            key,
            {
                "category": _category_label(env, key),
                "returns": 0,
                "ready": 0,
                "hours": [],
                "open": 0,
            },
        )
        row["returns"] += 1
        hours = _turnaround_hours(turn)
        if hours is not None:
            row["ready"] += 1
            row["hours"].append(hours)
        elif turn.state not in ("ready", "retired"):
            row["open"] += 1
    out = []
    for row in rows.values():
        hours = row.pop("hours")
        row["avg_hours"] = round(sum(hours) / len(hours), 1) if hours else 0.0
        row["max_hours"] = round(max(hours), 1) if hours else 0.0
        out.append(row)
    out.sort(key=lambda r: -r["avg_hours"])
    return _pack(
        "Turnaround Performance — returns %s to %s" % (start, end),
        ["category", "returns", "ready", "open", "avg_hours", "max_hours"],
        {
            "category": "Category",
            "returns": "Returns",
            "ready": "Back Available",
            "open": "Still in Turnaround",
            "avg_hours": "Average Hours to Available",
            "max_hours": "Longest (hours)",
        },
        out,
        [
            "Hours from the return day (00:00 Dhaka) to the turnaround's ready "
            "timestamp. Spec target < 24 h (W7+).",
            period_note(start, end, "return date"),
        ],
        totals={
            "category": "Total",
            "returns": sum(r["returns"] for r in out),
            "ready": sum(r["ready"] for r in out),
            "open": sum(r["open"] for r in out),
        },
        empty="No returns in this window.",
    )


def swap_sla(env, date_from=None, date_to=None, **params):
    """Spec §14 Swap SLA performance."""
    start, end = window(env, date_from, date_to, days=90)
    lo, hi = utc_bounds(start, end)
    reservations = _reservations(env)
    swaps = (
        env["fix.rental.swap"]
        .sudo()
        .search(
            [
                ("reservation_id", "in", reservations.ids),
                ("reported_at", ">=", lo),
                ("reported_at", "<", hi),
            ]
        )
    )
    rows = []
    for swap in swaps:
        rows.append(
            {
                "swap": swap.name,
                "rental": swap.reservation_id.name,
                "reported": str(to_dhaka_date(swap.reported_at) or ""),
                "sla_hours": swap.sla_hours,
                "state": dict(swap._fields["state"].selection).get(swap.state),
                "sla_met": "Yes" if swap.sla_met else ("—" if swap.state == "open" else "No"),
            }
        )
    executed = swaps.filtered(lambda s: s.state == "executed")
    met = executed.filtered("sla_met")
    sla = param(env, "cd_rental_asset.swap_sla_hours", "24 (default)")
    return _pack(
        "Swap SLA Performance — reported %s to %s" % (start, end),
        ["swap", "rental", "reported", "sla_hours", "state", "sla_met"],
        {
            "swap": "Swap",
            "rental": "Rental",
            "reported": "Reported",
            "sla_hours": "SLA (hours)",
            "state": "State",
            "sla_met": "SLA Met",
        },
        rows,
        [
            "Swap SLA met rate = %.1f%% (%d of %d executed swaps; spec target > 95%%). "
            "SLA from cd_rental_asset.swap_sla_hours = %s."
            % (pct(len(met), len(executed)), len(met), len(executed), sla),
            period_note(start, end, "fault reported time"),
        ],
        empty="No swaps in this window.",
    )


def loss_register(env, date_from=None, date_to=None, **params):
    """Spec §14 Loss and claims register."""
    start, end = window(env, date_from, date_to, days=365)
    lo, hi = utc_bounds(start, end)
    if "fix.rental.loss" not in env:
        return _pack(
            "Loss & Claims Register", [], {}, [], [], empty="Loss records are not installed."
        )
    reservations = _reservations(env)
    losses = (
        env["fix.rental.loss"]
        .sudo()
        .search(
            [
                ("reservation_id", "in", reservations.ids),
                ("reported_at", ">=", lo),
                ("reported_at", "<", hi),
            ]
        )
    )
    Loss = env["fix.rental.loss"]
    kinds = dict(Loss._fields["kind"].selection)
    states = dict(Loss._fields["state"].selection)
    claims = dict(Loss._fields["claim_decision"].selection)
    rows = []
    for loss in losses:
        rows.append(
            {
                "loss": loss.name,
                "rental": loss.reservation_id.name,
                "asset": loss.rental_asset_id.name or "—",
                "kind": kinds.get(loss.kind),
                "reported": str(to_dhaka_date(loss.reported_at) or ""),
                "valuation": round(loss.valuation or 0.0, 2),
                "claim": claims.get(loss.claim_decision, "—"),
                "forfeited": round(loss.forfeited_amount or 0.0, 2),
                "invoiced": round(loss.invoiced_amount or 0.0, 2),
                "state": states.get(loss.state),
                "written_off": str(loss.written_off_on or "—"),
            }
        )
    keys = ("valuation", "forfeited", "invoiced")
    totals = {"loss": "Total"}
    for key in keys:
        totals[key] = round(sum(r[key] for r in rows), 2)
    return _pack(
        "Loss & Claims Register — reported %s to %s" % (start, end),
        [
            "loss",
            "rental",
            "asset",
            "kind",
            "reported",
            "valuation",
            "claim",
            "forfeited",
            "invoiced",
            "state",
            "written_off",
        ],
        {
            "loss": "Loss",
            "rental": "Rental",
            "asset": "Asset",
            "kind": "Kind",
            "reported": "Reported",
            "valuation": "Valuation",
            "claim": "Insurance Claim",
            "forfeited": "Deposit Forfeited",
            "invoiced": "Invoiced",
            "state": "State",
            "written_off": "Written Off",
        },
        rows,
        [
            "Every non-return, loss and theft with its valuation, claim decision, "
            "recoveries and write-off.",
            period_note(start, end, "reported time"),
        ],
        totals=totals,
        empty="No losses reported in this window.",
    )


def zero_target_controls(env, date_from=None, date_to=None, **params):
    """Spec §15: five M13 targets are zero - a partial score is a control
    failure. Each control lists the records that breach it in the period."""
    start, end = window(env, date_from, date_to, days=90)
    reservations = _reservations(env)
    delivered = _delivered_on(env, reservations.filtered(lambda r: r.state in _OUT_STATES))
    minimum = int(param_float(env, "cd_rental_asset.condition_photo_minimum", 1) or 0)

    def complete(res, stage):
        reports = res.condition_ids.filtered(lambda c: c.report_type == stage)
        if not reports:
            return False
        if minimum and "photo_ids" in reports._fields:
            return any(len(c.photo_ids) >= minimum for c in reports)
        return True

    no_pre = [
        r.name
        for r in reservations
        if r.id in delivered and start <= delivered[r.id] <= end and not complete(r, "pre_delivery")
    ]
    no_post = [
        r.name
        for r in reservations
        if r.state == "closed"
        and r.actual_return_date
        and start <= r.actual_return_date <= end
        and not complete(r, "post_return")
    ]
    booked = reservations.filtered(
        lambda r: r.state in ("reserved", "delivered", "active")
        and r.rental_asset_id
        and r.date_from
        and r.date_to
        and r.date_from <= end
        and r.date_to >= start
    )
    double = set()
    by_asset = {}
    for res in booked:
        by_asset.setdefault(res.rental_asset_id.id, []).append(res)
    for group in by_asset.values():
        group.sort(key=lambda r: r.date_from)
        for i, first in enumerate(group):
            for second in group[i + 1 :]:
                if second.date_from <= first.date_to:
                    double.add("%s/%s" % (first.name, second.name))
    data_bearing = set(
        str(
            param(
                env,
                "cd_rental_asset.data_bearing_categories",
                "camera,laptop,projector,audio,medical,network,other",
            )
        ).split(",")
    )
    assets = _assets(env)
    turns = (
        env["fix.rental.turnaround"]
        .sudo()
        .search([("rental_asset_id", "in", assets.ids), ("state", "=", "ready")])
    )
    no_wipe = [
        t.name
        for t in turns
        if t.rental_asset_id.category in data_bearing
        and in_window(t.ready_timestamp or t.available_on, start, end)
        and not t.data_wipe_certificate_id
    ]
    unbilled = [
        r.name
        for r in reservations
        if r.state == "closed"
        and r.actual_return_date
        and start <= r.actual_return_date <= end
        and (r.rental_charge or 0.0) > 0
        and not r.mushak_6_3_id
    ]
    rows = [
        control_row("Dispatches without a complete condition report", no_pre),
        control_row("Returns closed without an inbound condition report", no_post),
        control_row("Double-booked units", sorted(double)),
        control_row(
            "Units re-entering the pool without an M06 certificate (data-bearing)", no_wipe
        ),
        control_row("Rentals closed with the rental charge never invoiced (M13-04)", unbilled),
    ]
    return _pack(
        "M13 Zero-Target Controls — %s to %s" % (start, end),
        CONTROL_COLS,
        CONTROL_LABELS,
        rows,
        [
            "Spec §15: condition evidence, double booking and the destruction gate are "
            "controls, not performance measures - any count above zero is a breach.",
            "A complete condition report has at least cd_rental_asset.condition_photo_minimum "
            "= %d photograph(s)." % minimum,
            period_note(start, end, "hand-over, return, ready and booking dates"),
        ],
        empty="No control data.",
    )


REPORTS = {
    "utilization_by_category": utilisation_by_category,
    "damage_loss_rate": damage_loss_rate,
    "rental_pl": rental_pl,
    "late_return": late_return,
    "deposit_reconciliation": deposit_reconciliation,
    "availability": availability,
    "fleet_health": fleet_health,
    # A05 ERP audit XC-18: the spec §14 reports that had no pack
    "overdue_recovery": overdue_recovery,
    "damage_recovery": damage_recovery,
    "turnaround_performance": turnaround_performance,
    "swap_sla": swap_sla,
    "loss_register": loss_register,
    "zero_target_controls": zero_target_controls,
}


def kpis(env):
    today = dhaka_today(env)
    assets = _assets(env)
    reservations = _reservations(env)
    ledger = _ledger(env, reservations)
    start = today - datetime.timedelta(days=29)
    year_start = today - datetime.timedelta(days=364)
    lost = _loss_dates(env, assets)
    spans = _rent_spans(env, reservations, today)
    available = {a.id: _available_days(a, start, today, lost.get(a.id)) for a in assets}
    rented = sum(
        min(_overlap_days(lo, hi, start, today), available.get(res.rental_asset_id.id, 0))
        for res, (lo, hi) in spans.items()
    )
    capacity = sum(available.values())
    # financial utilisation: 12 months' invoiced rental revenue ÷ fleet cost
    revenue_12m = sum(
        _net_taxable(inv)
        for _res, inv, kind in _rental_invoices(env, reservations, year_start, today)
        if kind == "rental"
    )
    in_fleet = assets.filtered(lambda a: _available_days(a, today, today, lost.get(a.id)))
    fleet_cost = sum(in_fleet.mapped("purchase_cost"))
    damages = env["fix.rental.damage"].sudo().search([("reservation_id", "in", reservations.ids)])
    dmg_year = damages.filtered(lambda d: d.incident_date and d.incident_date >= year_start)
    assessed = sum(dmg_year.mapped("cost"))
    recovered = sum(dmg_year.mapped("recovered_amount"))
    grace = int(param_float(env, "cd_rental_asset.late_fee_grace_days", 0) or 0)
    returned = reservations.filtered(
        lambda r: r.actual_return_date
        and r.date_to
        and r.actual_return_date >= today - datetime.timedelta(days=89)
    )
    on_time = returned.filtered(
        lambda r: r.actual_return_date <= r.date_to + datetime.timedelta(days=grace)
    )
    losses_12m = [aid for aid, day in lost.items() if day and day >= year_start]
    avg_fleet = sum(_available_days(a, year_start, today, lost.get(a.id)) for a in assets) / 365.0
    turns = (
        env["fix.rental.turnaround"]
        .sudo()
        .search([("rental_asset_id", "in", assets.ids), ("returned_on", ">=", start)])
    )
    hours = [h for h in (_turnaround_hours(t) for t in turns) if h is not None]
    swaps = (
        env["fix.rental.swap"]
        .sudo()
        .search([("reservation_id", "in", reservations.ids), ("state", "=", "executed")])
        .filtered(
            lambda s: s.executed_at
            and to_dhaka_date(s.executed_at) >= today - datetime.timedelta(days=89)
        )
    )
    release_days = param_float(env, "cd_rental_asset.deposit_release_days", None)
    released_pct = None
    if release_days is not None:
        refunds = ledger.filtered(
            lambda m: m.kind == "refund" and m.date >= today - datetime.timedelta(days=89)
        )
        timely = refunds.filtered(
            lambda m: m.reservation_id.actual_return_date
            and (m.date - m.reservation_id.actual_return_date).days <= release_days
        )
        released_pct = pct(len(timely), len(refunds)) if refunds else None
    controls = zero_target_controls(env, str(today - datetime.timedelta(days=89)), str(today))
    breaches = sum(r["actual"] for r in controls["rows"] if isinstance(r["actual"], int))
    damage_open = len(damages.filtered(lambda d: not d.settled))
    return {
        "fleet_size": len(in_fleet),
        "available_now": len(assets.filtered(lambda a: a.status == "available")),
        "active_rentals": len(reservations.filtered(lambda r: r.state == "active")),
        # M13-14 / XC-27: deposits held are what the GL holds
        "deposits_held": round(_held(ledger), 2),
        "damage_recovery_open": damage_open,
        # KPI-075, hand-over to actual return over days available (XC-16)
        "utilization_30d": pct(rented, capacity),
        "financial_utilization_12m": pct(revenue_12m, fleet_cost),
        "damage_recovery_rate": pct(recovered, assessed) if assessed else None,
        "on_time_return_rate": pct(len(on_time), len(returned)) if returned else None,
        "loss_rate_12m": pct(len(losses_12m), avg_fleet, 2) if avg_fleet else None,
        "turnaround_avg_hours": round(sum(hours) / len(hours), 1) if hours else None,
        "swap_sla_met_pct": pct(len(swaps.filtered("sla_met")), len(swaps)) if swaps else None,
        "deposits_released_in_window_pct": released_pct,
        "zero_target_breaches_90d": breaches,
    }
