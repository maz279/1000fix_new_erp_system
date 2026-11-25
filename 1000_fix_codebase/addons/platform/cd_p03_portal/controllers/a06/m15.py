# A06 · M15 Spare Parts & Inventory — surfaces, packs and KPIs over the part
# master, locations, issues and reorder rules plus the on-hand ledger and
# control documents. Valuation is quantity × the bucket's weighted-average
# cost; ABC uses on-hand value, XYZ uses movement recency.
#
# A06 audit (2026-11-03): every pack and KPI read sudo().search([]), so a
# clerk saw other companies' stock and the Stock Value KPI counted supplier
# consignment and customer property as 1000FiX inventory. Everything below
# reads as the CALLER (record rules apply), filtered to env.companies, and
# values only the owned classes (BRU-INV-02). Every workflow transition the
# screens need is declared in its surface's `actions`.
#
# A06 final pass B18 (spec section 13): cost and value are field-restricted.
# Technicians and store keepers see quantity, location and condition; a pack
# they read leaves the cost and value columns out. The value of what they may
# not see is still needed for ABC, so it is computed as sudo and not shown.
import datetime

COST_GROUP = "cd_wms_structure.group_stock_cost_viewer"
VAN_VARIANCE_GROUPS = (
    "cd_wms_structure.group_inventory_controller",
    "cd_wms_structure.group_inventory_approver_branch",
    "cd_wms_structure.group_inventory_approver_finance",
)

SURFACES = {
    # A06 ERP audit integration: the item master belongs to M15 (it was served
    # from M41's surface); setting the standard cost is an Inventory
    # Controller's action here, never on M41 (spec section 13: no cost in M41)
    "fix.spare.part": {
        "order": "id desc",
        "limit": 400,
        "actions": {
            "action_discontinue",
            "action_mark_obsolete",
            "action_reactivate",
            "action_set_standard_cost",
        },
    },
    # D1: the stock valuation ledger, one row per movement and its journal
    # entry - written by the movements, never typed in (read-only)
    "fix.inventory.valuation.suspense": {
        "order": "id desc",
        "limit": 400,
        "actions": set(),
    },
    "fix.stock.onhand": {"order": "part_id, location_id", "limit": 400, "actions": set()},
    "fix.stock.lot": {"order": "received_on desc, id desc", "limit": 400, "actions": set()},
    "fix.stock.consumption": {
        "order": "create_date desc, id desc",
        "limit": 300,
        # A06 ERP audit X19 / D4: an uncosted issue goes ahead on a controller's approval
        "actions": {"action_scan_and_consume", "action_return_part", "action_approve_zero_cost"},
    },
    "fix.stock.receipt": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_inspect", "action_post"},
    },
    "fix.stock.receipt.line": {"order": "receipt_id, id", "limit": 400, "actions": set()},
    "fix.stock.transfer": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_submit",
            "action_approve",
            "action_reject",
            "action_cancel",
            "action_dispatch",
            "action_receive",
            "action_resolve_discrepancy",
        },
    },
    "fix.stock.transfer.line": {"order": "transfer_id, id", "limit": 400, "actions": set()},
    "fix.stock.count": {
        "order": "create_date desc, id desc",
        "limit": 200,
        # A06 ERP audit A04: an abandoned count (it freezes its stock) is cancelled
        "actions": {"action_submit", "action_approve", "action_reject", "action_cancel"},
    },
    "fix.stock.count.line": {"order": "count_id, id", "limit": 400, "actions": set()},
    "fix.stock.van.recon": {
        "order": "recon_date desc, id desc",
        "limit": 300,
        "actions": {"action_confirm", "action_resolve"},
    },
    "fix.stock.quarantine": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_release",
            "action_scrap",
            "action_request_scrap",
            "action_approve_scrap",
            "action_reject_scrap",
        },
    },
    "fix.stock.rtv": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_submit",
            "action_approve",
            "action_cancel",
            "action_ship",
            "action_mark_credited",
        },
    },
    "fix.reorder.rule": {
        "order": "name",
        "limit": 300,
        "actions": {"action_trigger_reorder", "action_activate", "action_archive_rule"},
    },
    "fix.stock.class.change": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
    # capture pass 2 (2026-11-19): pages 3, 4, 5 and 7
    "fix.stock.reservation": {
        "order": "priority, expires_at, id",
        "limit": 300,
        "actions": {"action_reserve", "action_release"},
    },
    "fix.stock.backorder": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_raise_transfer",
            "action_raise_requisition",
            "action_fulfil",
            "action_cancel",
        },
    },
    "fix.stock.recall": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_execute", "action_cancel"},
    },
    "fix.consignment.reconciliation": {
        "order": "as_at desc, id desc",
        "limit": 200,
        "actions": {"action_compute", "action_submit", "action_acknowledge"},
    },
    "fix.consignment.reconciliation.line": {
        "order": "reconciliation_id, part_id",
        "limit": 400,
        "actions": set(),
    },
}

# The owned classes: consignment and customer property are held, never valued.
_VALUED = ("owned", "van", "bench", "warranty")

_OWNERSHIP_LABELS = {
    "owned": "Owned Stock",
    "consignment": "Supplier Consignment",
    "customer": "Customer Property",
    "van": "Van Stock",
    "bench": "Bench / WIP",
    "warranty": "Warranty Reserve",
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


def _mine(env, model, domain=None, **kw):
    """The caller's records of this model in the companies they work in."""
    records = env[model]
    company = [("company_id", "in", env.companies.ids)] if "company_id" in records._fields else []
    return records.search(company + list(domain or []), **kw)


def _onhand(env):
    return _mine(env, "fix.stock.onhand")


def _sees_cost(env):
    return env.su or env.user.has_group(COST_GROUP)


def _sees_van_variance(env):
    return env.su or any(env.user.has_group(g) for g in VAN_VARIANCE_GROUPS)


def _value(rows):
    """Value of these ledger rows. As sudo: callers show it only to a cost viewer."""
    return sum(
        (r.qty or 0.0) * (r.unit_cost or 0.0) for r in rows.sudo() if r.ownership_class in _VALUED
    )


def _without(pack, *hidden):
    """The pack without the columns this reader may not see."""
    pack["cols"] = [c for c in pack["cols"] if c not in hidden]
    pack["rows"] = [{k: v for k, v in row.items() if k not in hidden} for row in pack["rows"]]
    pack["labels"] = {k: v for k, v in pack["labels"].items() if k not in hidden}
    if pack.get("totals"):
        pack["totals"] = {k: v for k, v in pack["totals"].items() if k not in hidden}
    return pack


def _restricted(title):
    return _pack(
        title,
        [],
        {},
        [],
        ["Stock cost and value are visible to finance and inventory-manager roles only."],
        empty="Stock cost and value are visible to finance and inventory-manager roles only.",
    )


# ------------------------------------------------------------------ dates
# A06 ERP audit A22/A37/X32: every report honours the screen's period and the
# business day is Asia/Dhaka (a UTC "today" is yesterday until 06:00 Dhaka).
DHAKA = "Asia/Dhaka"


def _today(env):
    from odoo import fields

    return fields.Date.context_today(env["res.users"].with_context(tz=DHAKA))


def _date(value):
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


def _period(date_from, date_to):
    return _date(date_from), _date(date_to)


def _dhaka_date(env, stamp):
    """The Dhaka business date of a stored (naive UTC) datetime."""
    from odoo import fields

    if not stamp:
        return None
    return fields.Date.context_today(env["res.users"].with_context(tz=DHAKA), stamp)


def _date_domain(field, date_from, date_to):
    domain = []
    if date_from:
        domain.append((field, ">=", date_from))
    if date_to:
        domain.append((field, "<=", date_to))
    return domain


def _datetime_domain(field, date_from, date_to):
    """A Dhaka-day period on a UTC datetime field (Dhaka is UTC+6, no DST)."""
    six = datetime.timedelta(hours=6)
    domain = []
    if date_from:
        domain.append((field, ">=", datetime.datetime.combine(date_from, datetime.time()) - six))
    if date_to:
        end = datetime.datetime.combine(date_to + datetime.timedelta(days=1), datetime.time())
        domain.append((field, "<", end - six))
    return domain


def _period_note(date_from, date_to, field):
    if not date_from and not date_to:
        return "All dates (no period chosen)."
    return "Period %s to %s on the %s (Dhaka dates)." % (
        date_from or "the start",
        date_to or "today",
        field,
    )


def ownership_classes(env, date_from=None, date_to=None, **params):
    rows = []
    for key, label in _OWNERSHIP_LABELS.items():
        recs = _onhand(env).filtered(lambda r, k=key: r.ownership_class == k)
        rows.append(
            {
                "ownership": label,
                "lines": len(recs),
                "qty": round(sum(recs.mapped("qty")), 3),
                "value": round(_value(recs), 2),
            }
        )
    rows.sort(key=lambda r: -r["value"])
    pack = _pack(
        "6 Ownership Classes — on-hand quantity and value",
        ["ownership", "lines", "qty", "value"],
        {"ownership": "Ownership Class", "lines": "Lines", "qty": "Quantity", "value": "Value"},
        rows,
        [
            "Value = on-hand quantity × the bucket's average cost. Consignment and "
            "customer property are held, not owned: they carry no value (BRU-INV-02). "
            "A position now (the period does not apply)."
        ],
        totals={
            "ownership": "Total",
            "lines": sum(r["lines"] for r in rows),
            "qty": round(sum(r["qty"] for r in rows), 3),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No on-hand rows recorded yet.",
    )
    return pack if _sees_cost(env) else _without(pack, "value")


def availability(env, date_from=None, date_to=None, **params):
    """A06 ERP audit A24: the NETWORK position. A storekeeper's own record
    rules show only his operating unit, so the network search reads every
    location of the caller's companies as the system, and shows quantity only:
    no cost or value leaves this report (cost is field-restricted, B18)."""
    rows = []
    domain = [
        ("company_id", "in", env.companies.ids),
        ("stock_status", "=", "unrestricted"),
        ("available_qty", ">", 0),
    ]
    for rec in env["fix.stock.onhand"].sudo().search(domain):
        loc = rec.location_id
        rows.append(
            {
                "part": rec.part_id.part_number,
                "description": rec.part_id.name,
                "location": loc.code,
                "branch": loc.branch_id.name or (loc.operating_unit_id.name or "—"),
                "stock_type": dict(loc._fields["stock_type"].selection).get(loc.stock_type) or "—",
                "ownership": _OWNERSHIP_LABELS.get(rec.ownership_class, rec.ownership_class),
                "available": round(rec.available_qty, 3),
            }
        )
    rows.sort(key=lambda r: (r["part"], -r["available"]))
    return _pack(
        "Network Availability — available quantity at every location",
        ["part", "description", "location", "branch", "stock_type", "ownership", "available"],
        {
            "part": "Part Number",
            "description": "Description",
            "location": "Location",
            "branch": "Branch / OU",
            "stock_type": "Store Type",
            "ownership": "Ownership",
            "available": "Available",
        },
        rows,
        [
            "Available = unrestricted on-hand − reserved, per location and ownership class, "
            "across every operating unit of your companies (A24); quarantined, in-transit "
            "and staged stock is not available. Quantities only: cost is not shown here.",
            "Warranty stores serve warranty jobs only, other stores never do (D3).",
        ],
        totals={"part": "Total", "available": round(sum(r["available"] for r in rows), 3)},
        empty="No available stock recorded yet.",
    )


def genealogy(env, date_from=None, date_to=None, **params):
    df, dt = _period(date_from, date_to)
    consumptions = _mine(
        env,
        "fix.stock.consumption",
        _datetime_domain("consumed_at", df, dt),
        order="create_date desc",
        limit=300,
    )
    lots = _mine(env, "fix.stock.lot")
    rows = []
    for rec in consumptions:
        lot = (
            lots.filtered(lambda ln, serial=rec.serial_number: serial and ln.name == serial)[:1]
            if rec.serial_number
            else lots.browse()
        )
        rows.append(
            {
                "consumption": rec.name,
                "consumed_on": str(_dhaka_date(env, rec.consumed_at) or "—"),
                "part": rec.product_id.part_number,
                "qty": round(rec.quantity or 0.0, 3),
                "technician": rec.technician_id.name if rec.technician_id else "—",
                "service_order": rec.service_order_ref or "—",
                "serial": rec.serial_number or "—",
                "lot_status": dict(lot._fields["status"].selection).get(lot.status) if lot else "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    return _pack(
        "Consumption Genealogy — part → serial/lot → job",
        [
            "consumption",
            "consumed_on",
            "part",
            "qty",
            "technician",
            "service_order",
            "serial",
            "lot_status",
            "state",
        ],
        {
            "consumption": "Consumption",
            "consumed_on": "Issued On",
            "part": "Part",
            "qty": "Qty",
            "technician": "Technician",
            "service_order": "Service Order",
            "serial": "Serial",
            "lot_status": "Lot Status",
            "state": "State",
        },
        rows,
        [
            "A serial is matched to its lot record when one exists; an unmatched "
            "serial stays visible as '—' rather than being hidden.",
            _period_note(df, dt, "issue date"),
        ],
        empty="No part consumption recorded in the period.",
    )


def van_stock(env, date_from=None, date_to=None, **params):
    vans = _mine(env, "fix.stock.location", [("is_van_location", "=", True)])
    rows = []
    for rec in _onhand(env).filtered(lambda r: r.location_id.is_van_location):
        rows.append(
            {
                "van": rec.location_id.code,
                "technician": rec.location_id.technician_id.name
                if rec.location_id.technician_id
                else "—",
                "part": rec.part_id.part_number,
                "qty": round(rec.qty or 0.0, 3),
                "reserved": round(rec.reserved or 0.0, 3),
                "available": round(rec.available_qty or 0.0, 3),
            }
        )
    rows.sort(key=lambda r: (r["van"], r["part"]))
    return _pack(
        "Van Stock by Technician — %d van locations" % len(vans),
        ["van", "technician", "part", "qty", "reserved", "available"],
        {
            "van": "Van",
            "technician": "Technician",
            "part": "Part",
            "qty": "On Hand",
            "reserved": "Reserved",
            "available": "Available",
        },
        rows,
        [
            "Van stock is the `van` ownership class at a location flagged as a van; "
            "technician comes from the location's assigned technician. A position now."
        ],
        totals={
            "van": "Total",
            "qty": round(sum(r["qty"] for r in rows), 3),
            "available": round(sum(r["available"] for r in rows), 3),
        },
        empty="No van stock recorded yet.",
    )


def valuation_by_class(env, date_from=None, date_to=None, **params):
    if not _sees_cost(env):
        return _restricted("Stock Valuation by Class — quantity × weighted-average cost")
    rows = []
    for rec in _onhand(env).filtered(lambda r: r.ownership_class in _VALUED):
        rows.append(
            {
                "part": rec.part_id.part_number,
                "location": rec.location_id.code,
                "ownership": _OWNERSHIP_LABELS.get(rec.ownership_class, rec.ownership_class),
                "qty": round(rec.qty or 0.0, 3),
                "unit_cost": round(rec.unit_cost or 0.0, 2),
                "value": round((rec.qty or 0.0) * (rec.unit_cost or 0.0), 2),
                "method": dict(rec._fields["valuation_method"].selection).get(rec.valuation_method),
            }
        )
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Stock Valuation by Class — quantity × weighted-average cost",
        ["part", "location", "ownership", "qty", "unit_cost", "value", "method"],
        {
            "part": "Part",
            "location": "Location",
            "ownership": "Ownership",
            "qty": "Qty",
            "unit_cost": "Unit Cost",
            "value": "Value",
            "method": "Method",
        },
        rows,
        [
            "Weighted average cost (WAC) is the only method in operation: each bucket "
            "carries its average (receipts average in; issues, transfers and scrap leave "
            "at it). There are no FIFO cost layers. Consignment and customer property "
            "are excluded: they are not 1000FiX's inventory. A position now.",
            "%d line(s) hold quantity at no cost: their value is unknown (D4), not nil."
            % len([r for r in rows if r["qty"] > 0 and not r["unit_cost"]]),
        ],
        totals={
            "part": "Total",
            "qty": round(sum(r["qty"] for r in rows), 3),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No on-hand rows recorded yet.",
    )


def _age_buckets(env, rows, today):
    """A06 ERP audit A22/X30: the age of each bucket's quantity without lots.
    The movement ledger holds every receipt into the bucket: the quantity on
    hand is the most recent arrivals (first in, first out), so each unit is as
    old as the arrival it came with. A bucket with no movement on the ledger
    (taken on before it) is as old as its last movement date."""
    Log = env["fix.stock.move.log"].sudo()
    arrivals = {}
    if rows:
        for log in Log.search(
            [("part_id", "in", rows.mapped("part_id").ids), ("qty", ">", 0)],
            order="moved_at desc, id desc",
        ):
            key = (log.part_id.id, log.location_id.id, log.ownership_class, log.stock_status)
            arrivals.setdefault(key, []).append((log.move_date, log.qty))
    out = []
    for rec in rows:
        left = rec.qty or 0.0
        key = (rec.part_id.id, rec.location_id.id, rec.ownership_class, rec.stock_status)
        layers = []
        for when, qty in arrivals.get(key, []):
            if left <= 1e-6:
                break
            take = min(qty, left)
            layers.append((when, take))
            left -= take
        if left > 1e-6:
            layers.append((rec.last_move_date, left))
        for when, qty in layers:
            age = (today - when).days if when else None
            out.append((rec, when, age, qty))
    return out


def _age_band(age):
    if age is None:
        return "Unknown age", "Date the stock"
    if age > 365:
        return ">365 days", "Write-off review"
    if age > 180:
        return "181–365 days", "Markdown / return"
    if age > 90:
        return "91–180 days", "Move first"
    return "0–90 days", "Healthy"


def ageing(env, date_from=None, date_to=None, **params):
    """Ageing & dead stock from receipt and movement dates (A22/X30): it no
    longer reads serial lots only (fix_real has none)."""
    today = _date(date_to) or _today(env)
    rows = _onhand(env).filtered(
        lambda r: (r.qty or 0.0) > 0 and r.stock_status in ("unrestricted", "quarantine")
    )
    cost = _sees_cost(env)
    out = []
    for rec, when, age, qty in _age_buckets(env, rows, today):
        band, action = _age_band(age)
        row = {
            "part": rec.part_id.part_number,
            "location": rec.location_id.code,
            "ownership": _OWNERSHIP_LABELS.get(rec.ownership_class, rec.ownership_class),
            "since": str(when) if when else "—",
            "age_days": age if age is not None else "—",
            "qty": round(qty, 3),
            "bucket": band,
            "action": action,
        }
        if cost:
            unit = rec.sudo().unit_cost or 0.0
            row["value"] = round(qty * unit, 2) if rec.ownership_class in _VALUED else 0.0
        out.append(row)
    out.sort(key=lambda r: -(r["age_days"] if isinstance(r["age_days"], int) else 99999))
    cols = [
        "part",
        "location",
        "ownership",
        "since",
        "age_days",
        "qty",
        "value",
        "bucket",
        "action",
    ]
    labels = {
        "part": "Part",
        "location": "Location",
        "ownership": "Ownership",
        "since": "In Stock Since",
        "age_days": "Days Held",
        "qty": "Qty",
        "value": "Value",
        "bucket": "Age Band",
        "action": "Policy",
    }
    dead = sum(r.get("value", 0.0) for r in out if r["bucket"] == ">365 days")
    total = sum(r.get("value", 0.0) for r in out)
    pack = _pack(
        "Ageing & Dead Stock — quantity by days held",
        cols,
        labels,
        out,
        [
            "Age runs from the receipt the quantity came in with (the movement ledger, "
            "first in first out); stock taken on before the ledger ages from its last "
            "movement. Policy bands 90/180/365 days. As at %s (Dhaka)." % today,
            "Dead stock (>365 days): BDT %.2f of BDT %.2f (KPI-046)." % (dead, total)
            if cost
            else "Values are visible to finance and inventory-manager roles only.",
        ],
        totals={"part": "Total", "qty": round(sum(r["qty"] for r in out), 3)},
        empty="No stock on hand.",
    )
    return pack if cost else _without(pack, "value")


def abc_segmentation(env, date_from=None, date_to=None, **params):
    today = _today(env)
    rows = []
    for rec in _onhand(env).filtered(lambda r: r.ownership_class in _VALUED):
        value = (rec.qty or 0.0) * (rec.sudo().unit_cost or 0.0)
        last = rec.last_move_date
        if last and (today - last).days <= 30:
            movement = "X — fast"
        elif last and (today - last).days <= 90:
            movement = "Y — medium"
        else:
            movement = "Z — slow / no movement"
        rows.append(
            {
                "part": rec.part_id.part_number,
                "description": rec.part_id.name,
                "qty": round(rec.qty or 0.0, 3),
                "value": round(value, 2),
                "criticality": dict(rec.part_id._fields["criticality"].selection).get(
                    rec.part_id.criticality
                )
                if rec.part_id.criticality
                else "—",
                "movement": movement,
            }
        )
    total = sum(r["value"] for r in rows) or 1.0
    cumulative = 0.0
    for row in sorted(rows, key=lambda r: -r["value"]):
        cumulative += row["value"]
        row["cumulative_pct"] = round((cumulative / total) * 100.0, 1)
        # ABC follows the value Pareto (A ≤80%, B ≤95%), not fixed thresholds
        row["abc"] = (
            "A"
            if row["cumulative_pct"] <= 80.0
            else ("B" if row["cumulative_pct"] <= 95.0 else "C")
        )
    rows.sort(key=lambda r: -r["value"])
    pack = _pack(
        "ABC / XYZ / Criticality — value Pareto, movement recency, part criticality",
        ["part", "description", "qty", "value", "abc", "cumulative_pct", "movement", "criticality"],
        {
            "part": "Part",
            "description": "Description",
            "qty": "Qty",
            "value": "Value",
            "abc": "ABC (value)",
            "cumulative_pct": "Cumulative %",
            "movement": "XYZ (movement)",
            "criticality": "Criticality",
        },
        rows,
        [
            "ABC is the running value Pareto (A ≤80%, B ≤95%, C rest). XYZ uses days "
            "since last movement (X ≤30, Y ≤90, Z beyond, Dhaka dates). Criticality is "
            "the part master's."
        ],
        empty="No on-hand rows recorded yet.",
    )
    return pack if _sees_cost(env) else _without(pack, "value", "cumulative_pct")


def _count_tolerance(env):
    raw = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("cd_inventory.count_variance_tolerance_pct", 2.0)
    )
    try:
        return max(float(raw), 0.0)
    except (TypeError, ValueError):
        return 0.0


def _accurate(line, pct):
    expected = line.expected_qty or 0.0
    return abs(line.variance or 0.0) <= abs(expected) * pct / 100.0 + 1e-6


def accuracy_audit(env, date_from=None, date_to=None, **params):
    df, dt = _period(date_from, date_to)
    counts = _mine(env, "fix.stock.count", _date_domain("counted_on", df, dt))
    # blind counts: the expected quantity is revealed once a count is posted
    # (or to an Inventory Controller); open counts are listed without it
    lines = env["fix.stock.count.line"].search([("count_id", "in", counts.ids)])
    pct = _count_tolerance(env)
    rows = []
    for line in lines:
        visible = line.expected_visible
        rows.append(
            {
                "count": line.count_id.name,
                "location": line.count_id.location_id.code,
                "type": dict(line.count_id._fields["count_type"].selection).get(
                    line.count_id.count_type
                ),
                "part": line.part_id.part_number,
                "ownership": _OWNERSHIP_LABELS.get(line.ownership_class, "—"),
                "expected": round(line.expected_qty or 0.0, 3) if visible else "—",
                "counted": round(line.counted_qty or 0.0, 3),
                "variance": round(line.variance or 0.0, 3) if visible else "—",
                "state": dict(line.count_id._fields["state"].selection).get(line.count_id.state),
            }
        )
    rows.sort(key=lambda r: -abs(r["variance"]) if isinstance(r["variance"], float) else 0)
    # A06 ERP audit A22: accuracy over POSTED lines only - a blind line whose
    # expected quantity is hidden used to read as an exact match
    posted = lines.filtered(lambda ln: ln.count_id.state == "posted" and ln.expected_visible)
    accurate = len([ln for ln in posted if _accurate(ln, pct)])
    return _pack(
        "Inventory Accuracy Audit — count lines and variance",
        [
            "count",
            "location",
            "type",
            "part",
            "ownership",
            "expected",
            "counted",
            "variance",
            "state",
        ],
        {
            "count": "Count",
            "location": "Location",
            "type": "Type",
            "part": "Part",
            "ownership": "Class",
            "expected": "Expected",
            "counted": "Counted",
            "variance": "Variance",
            "state": "State",
        },
        rows,
        [
            "%d counts, %d lines; %d posted line(s), %d within the %.1f%% tolerance — "
            "accuracy %.1f%% (KPI-042, posted lines only: an open blind count's expected "
            "quantity is not shown and not scored)."
            % (
                len(counts),
                len(lines),
                len(posted),
                accurate,
                pct,
                (accurate / len(posted)) * 100.0 if posted else 0.0,
            ),
            _period_note(df, dt, "count date"),
        ],
        totals={
            "count": "Total",
            "counted": round(sum(r["counted"] for r in rows), 3),
        },
        empty="No stock counts recorded in the period.",
    )


def van_variance(env, date_from=None, date_to=None, **params):
    df, dt = _period(date_from, date_to)
    recons = _mine(env, "fix.stock.van.recon", _date_domain("recon_date", df, dt))
    cost = _sees_cost(env)
    rows = []
    for rec in recons:
        ledger = rec.sudo()
        row = {
            "recon": rec.name,
            "van": rec.location_id.code,
            "technician": rec.technician_id.name if rec.technician_id else "—",
            "date": str(rec.recon_date),
            "parts": len(rec.line_ids),
            "expected": round(ledger.expected_qty or 0.0, 3),
            "counted": round(rec.counted_qty or 0.0, 3),
            "variance": round(ledger.variance or 0.0, 3),
            "state": dict(rec._fields["state"].selection).get(rec.state),
        }
        if cost:
            row["variance_value"] = round(ledger.variance_value or 0.0, 2)
        rows.append(row)
    rows.sort(key=lambda r: -abs(r["variance"]))
    pack = _pack(
        "Van Stock Variance — daily reconciliation",
        [
            "recon",
            "van",
            "technician",
            "date",
            "parts",
            "expected",
            "counted",
            "variance",
            "variance_value",
            "state",
        ],
        {
            "recon": "Reconciliation",
            "van": "Van",
            "technician": "Technician",
            "date": "Date",
            "parts": "Parts Counted",
            "expected": "Expected",
            "counted": "Counted",
            "variance": "Variance",
            "variance_value": "Variance Value",
            "state": "State",
        },
        rows,
        [
            "Variance = counted − expected; each van is counted part by part and an "
            "approved discrepancy corrects the ledger at the van's average cost (A11).",
            _period_note(df, dt, "reconciliation date"),
        ],
        totals={
            "recon": "Total",
            "expected": round(sum(r["expected"] for r in rows), 3),
            "counted": round(sum(r["counted"] for r in rows), 3),
            "variance": round(sum(r["variance"] for r in rows), 3),
        },
        empty="No van reconciliations recorded in the period.",
    )
    if not cost:
        pack = _without(pack, "variance_value")
    # M15-8: the count is blind: the van's expected quantity is an approver's
    return pack if _sees_van_variance(env) else _without(pack, "expected", "variance")


def transfer_performance(env, date_from=None, date_to=None, **params):
    df, dt = _period(date_from, date_to)
    transfers = _mine(env, "fix.stock.transfer", _date_domain("requested_on", df, dt))
    rows = []
    for rec in transfers:
        days = "—"
        if rec.dispatched_on and rec.received_on:
            days = (rec.received_on - rec.dispatched_on).days
        rows.append(
            {
                "transfer": rec.name,
                "from": rec.from_location_id.code,
                "to": rec.to_location_id.code,
                "requested": str(rec.requested_on),
                "dispatched": str(rec.dispatched_on) if rec.dispatched_on else "—",
                "received": str(rec.received_on) if rec.received_on else "—",
                "transit_days": days,
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: str(r["transfer"]), reverse=True)
    short = len(transfers.filtered(lambda t: t.discrepancy_resolution or t.state == "discrepancy"))
    return _pack(
        "Transfer Performance — request to receipt",
        ["transfer", "from", "to", "requested", "dispatched", "received", "transit_days", "state"],
        {
            "transfer": "Transfer",
            "from": "From",
            "to": "To",
            "requested": "Requested",
            "dispatched": "Dispatched",
            "received": "Received",
            "transit_days": "Transit Days",
            "state": "State",
        },
        rows,
        [
            "Transit days = received − dispatched; open transfers show '—'. %d of %d "
            "arrived short (discrepancy rate %.1f%%)."
            % (short, len(transfers), (short / len(transfers) * 100.0) if transfers else 0.0),
            _period_note(df, dt, "request date"),
        ],
        empty="No transfers recorded in the period.",
    )


# ---------------------------------------------------- A22: spec registers
def adjustment_register(env, date_from=None, date_to=None, **params):
    """Adjustment and write-off register (spec section 14): every count
    adjustment, van correction and write-off with reason, requester, approver
    and value."""
    df, dt = _period(date_from, date_to)
    cost = _sees_cost(env)
    rows = []
    for rec in _mine(env, "fix.stock.count", [("state", "=", "posted")]):
        day = _dhaka_date(env, rec.posted_at)
        if (df and (not day or day < df)) or (dt and (not day or day > dt)):
            continue
        rows.append(
            {
                "document": rec.name,
                "kind": "Count adjustment",
                "date": str(day or "—"),
                "location": rec.location_id.code,
                "reason": dict(rec._fields["reason_code"].selection).get(rec.reason_code)
                or "Within tolerance",
                "requested_by": rec.counted_by_id.name or "—",
                "approved_by": rec.approved_by_id.name or "—",
                "value": round(rec.sudo().variance_value or 0.0, 2),
            }
        )
    for rec in _mine(env, "fix.stock.van.recon", [("ledger_corrected", "=", True)]):
        day = _date(rec.approved_at and _dhaka_date(env, rec.approved_at))
        if (df and (not day or day < df)) or (dt and (not day or day > dt)):
            continue
        rows.append(
            {
                "document": rec.name,
                "kind": "Van correction",
                "date": str(day or "—"),
                "location": rec.location_id.code,
                "reason": rec.approval_note or "—",
                "requested_by": rec.confirmed_by_id.name or "—",
                "approved_by": rec.approved_by_id.name or "—",
                "value": round(rec.sudo().variance_value or 0.0, 2),
            }
        )
    for rec in _mine(env, "fix.stock.quarantine", [("state", "=", "scrapped")]):
        day = _dhaka_date(env, rec.scrapped_at)
        if (df and (not day or day < df)) or (dt and (not day or day > dt)):
            continue
        rows.append(
            {
                "document": rec.name,
                "kind": "Write-off",
                "date": str(day or "—"),
                "location": rec.location_id.code,
                "reason": dict(rec._fields["reason"].selection).get(rec.reason),
                "requested_by": rec.requested_by_id.name or rec.create_uid.name or "—",
                "approved_by": rec.approved_by_id.name or "—",
                "value": -round(rec.sudo()._writeoff_value(), 2),
            }
        )
    rows.sort(key=lambda r: r["date"], reverse=True)
    pack = _pack(
        "Adjustment & Write-off Register",
        ["document", "kind", "date", "location", "reason", "requested_by", "approved_by", "value"],
        {
            "document": "Document",
            "kind": "Kind",
            "date": "Date",
            "location": "Location",
            "reason": "Reason",
            "requested_by": "Requested / Counted By",
            "approved_by": "Approved By",
            "value": "Value (BDT)",
        },
        rows,
        [
            "Gains are positive, losses and write-offs negative, at the average cost the "
            "stock moved at.",
            _period_note(df, dt, "posting date"),
        ],
        totals={"document": "Total", "value": round(sum(r["value"] for r in rows), 2)},
        empty="No adjustment or write-off in the period.",
    )
    return pack if cost else _without(pack, "value")


def quarantine_register(env, date_from=None, date_to=None, **params):
    """Quarantine and counterfeit register (spec section 14)."""
    df, dt = _period(date_from, date_to)
    rows = []
    for rec in _mine(env, "fix.stock.quarantine", _date_domain("quarantined_on", df, dt)):
        rows.append(
            {
                "quarantine": rec.name,
                "date": str(rec.quarantined_on),
                "part": rec.part_id.part_number,
                "location": rec.location_id.code,
                "qty": round(rec.qty or 0.0, 3),
                "reason": dict(rec._fields["reason"].selection).get(rec.reason),
                "source": rec.source_ref or "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: r["date"], reverse=True)
    return _pack(
        "Quarantine & Counterfeit Register",
        ["quarantine", "date", "part", "location", "qty", "reason", "source", "state"],
        {
            "quarantine": "Quarantine",
            "date": "Quarantined",
            "part": "Part",
            "location": "Location",
            "qty": "Qty",
            "reason": "Reason",
            "source": "Source (receipt / recall)",
            "state": "Disposition",
        },
        rows,
        [
            "Held stock by reason and its disposition (released by the Quality Manager or "
            "an Inventory Controller, scrapped, or returned to the vendor).",
            _period_note(df, dt, "quarantine date"),
        ],
        totals={"quarantine": "Total", "qty": round(sum(r["qty"] for r in rows), 3)},
        empty="Nothing quarantined in the period.",
    )


def rtv_register(env, date_from=None, date_to=None, **params):
    """RTV and credit recovery (spec section 14)."""
    df, dt = _period(date_from, date_to)
    cost = _sees_cost(env)
    today = _today(env)
    rows = []
    for rec in _mine(env, "fix.stock.rtv", _date_domain("requested_on", df, dt)):
        ledger = rec.sudo()
        rows.append(
            {
                "rtv": rec.name,
                "vendor": rec.partner_id.name,
                "part": rec.part_id.part_number,
                "qty": round(rec.qty or 0.0, 3),
                "requested": str(rec.requested_on),
                "value": round((rec.qty or 0.0) * (ledger.unit_cost or 0.0), 2),
                "credit": rec.credit_ref or "—",
                "age_days": (today - rec.requested_on).days
                if rec.state not in ("credited", "cancelled")
                else "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: r["requested"], reverse=True)
    raised = sum(r["value"] for r in rows if r["state"] != "Cancelled")
    credited = sum(r["value"] for r in rows if r["credit"] != "—")
    pack = _pack(
        "RTV & Credit Recovery",
        ["rtv", "vendor", "part", "qty", "requested", "value", "credit", "age_days", "state"],
        {
            "rtv": "RTV",
            "vendor": "Vendor",
            "part": "Part",
            "qty": "Qty",
            "requested": "Requested",
            "value": "Value (BDT)",
            "credit": "Credit Ref",
            "age_days": "Days Open",
            "state": "State",
        },
        rows,
        [
            "Credits recovered: BDT %.2f of BDT %.2f raised (%.1f%%)."
            % (credited, raised, (credited / raised * 100.0) if raised else 0.0)
            if cost
            else "Values are visible to finance and inventory-manager roles only.",
            _period_note(df, dt, "request date"),
        ],
        totals={"rtv": "Total", "qty": round(sum(r["qty"] for r in rows), 3)},
        empty="No return to vendor in the period.",
    )
    return pack if cost else _without(pack, "value")


def stockout_register(env, date_from=None, date_to=None, **params):
    """Stockout and unmet demand (spec section 14): the backorders raised when
    a part was not at hand, with the job that waited."""
    df, dt = _period(date_from, date_to)
    rows = []
    for rec in _mine(env, "fix.stock.backorder", _datetime_domain("create_date", df, dt)):
        rows.append(
            {
                "backorder": rec.name,
                "raised": str(_dhaka_date(env, rec.create_date) or "—"),
                "part": rec.part_id.part_number,
                "location": rec.location_id.code,
                "qty": round(rec.qty or 0.0, 3),
                "job": rec.service_order_ref or "Stock",
                "met_by": rec.transfer_id.name or rec.requisition_id.display_name or "—",
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: r["raised"], reverse=True)
    return _pack(
        "Stockout & Unmet Demand",
        ["backorder", "raised", "part", "location", "qty", "job", "met_by", "state"],
        {
            "backorder": "Backorder",
            "raised": "Raised",
            "part": "Part",
            "location": "Needed At",
            "qty": "Qty",
            "job": "Job Waiting",
            "met_by": "Met By",
            "state": "State",
        },
        rows,
        [
            "Each row is demand the requesting location could not meet when asked " "(FR-INV-025).",
            _period_note(df, dt, "date raised"),
        ],
        totals={"backorder": "Total", "qty": round(sum(r["qty"] for r in rows), 3)},
        empty="No stockout in the period.",
    )


def branch_position(env, date_from=None, date_to=None, **params):
    """Branch stock position (spec section 14): per reorder rule, on hand,
    reserved, available, on order, in transit and whether it is below its
    minimum. Rules carry the real minimum (no default min applies)."""
    rows = []
    for rule in _mine(env, "fix.reorder.rule", [("state", "!=", "archived")]):
        below = rule.position_qty <= (rule.min_qty or 0.0) + 1e-6
        rows.append(
            {
                "location": rule.location_id.code,
                "part": rule.spare_part_id.part_number,
                "available": round(rule.current_stock, 3),
                "on_order": round(rule.on_order_qty, 3),
                "in_transit": round(rule.in_transit_qty, 3),
                "min": round(rule.min_qty or 0.0, 3),
                "max": round(rule.max_qty or 0.0, 3),
                "status": "Below minimum" if below else "OK",
                "document": rule.transfer_id.name or rule.requisition_id.display_name or "—",
            }
        )
    rows.sort(key=lambda r: (r["status"] != "Below minimum", r["location"], r["part"]))
    return _pack(
        "Branch Stock Position — against each location's minimum",
        [
            "location",
            "part",
            "available",
            "on_order",
            "in_transit",
            "min",
            "max",
            "status",
            "document",
        ],
        {
            "location": "Location",
            "part": "Part",
            "available": "Available",
            "on_order": "On Order",
            "in_transit": "In Transit",
            "min": "Minimum",
            "max": "Maximum",
            "status": "Status",
            "document": "Replenishment",
        },
        rows,
        [
            "Position = available + on order + in transit (D7). Vans and branch stores "
            "are refilled by transfer, warehouses by purchase. A position now."
        ],
        empty="No reorder rule set.",
    )


def movers(env, date_from=None, date_to=None, **params):
    """Slow and fast movers (spec section 14): what left each part's stock in
    the period (issues, transfers out, write-offs, from the movement ledger)
    against what it holds now; turns are annualised."""
    df, dt = _period(date_from, date_to)
    today = _today(env)
    start = df or (today - datetime.timedelta(days=365))
    end = dt or today
    days = max((end - start).days + 1, 1)
    logs = (
        env["fix.stock.move.log"]
        .sudo()
        .search(
            [
                ("company_id", "in", env.companies.ids),
                ("move_date", ">=", start),
                ("move_date", "<=", end),
                ("qty", "<", 0),
                ("stock_status", "=", "unrestricted"),
                ("ownership_class", "in", _VALUED),
            ]
        )
    )
    out = {}
    for log in logs:
        out[log.part_id] = out.get(log.part_id, 0.0) + abs(log.qty)
    held = {}
    for rec in _onhand(env).filtered(lambda r: r.ownership_class in _VALUED):
        held[rec.part_id] = held.get(rec.part_id, 0.0) + (rec.qty or 0.0)
    rows = []
    for part in set(out) | set(held):
        moved = out.get(part, 0.0)
        stock = held.get(part, 0.0)
        turns = round((moved / stock) * (365.0 / days), 2) if stock > 1e-6 else None
        rows.append(
            {
                "part": part.part_number,
                "category": part.category_id.display_name or "—",
                "moved": round(moved, 3),
                "on_hand": round(stock, 3),
                "turns": turns if turns is not None else "—",
                "speed": "Fast"
                if (turns or 0) >= 6
                else ("Slow" if (turns or 0) < 1 else "Medium"),
            }
        )
    rows.sort(key=lambda r: -(r["turns"] if isinstance(r["turns"], float) else -1))
    return _pack(
        "Slow & Fast Movers — turns by part",
        ["part", "category", "moved", "on_hand", "turns", "speed"],
        {
            "part": "Part",
            "category": "Category",
            "moved": "Issued / Moved Out",
            "on_hand": "On Hand",
            "turns": "Turns / Year",
            "speed": "Speed",
        },
        rows,
        [
            "Turns = quantity that left unrestricted stock in the period ÷ on hand, "
            "annualised (KPI-045 target 6+). Read from the movement ledger: movements "
            "before it started are not counted.",
            _period_note(start, end, "movement date"),
        ],
        empty="No stock movement in the period.",
    )


def suspense_integrity(env, date_from=None, date_to=None, **params):
    """S0 (read-only): is the initial-count baseline loaded twice, and how
    does the pending M19 suspense compare with the on-hand value?"""
    if not _sees_cost(env):
        return _restricted("Valuation Suspense Integrity")
    data = env["fix.inventory.valuation.suspense"].get_baseline_integrity()
    rows = []
    for item in data["companies"]:
        rows.append(
            {
                "company": item["company"],
                "pending_entries": item["pending_entries"],
                "pending_total": item["pending_total"],
                "baseline_total": item["baseline_total"],
                "duplicate_rows": item["duplicate_extra_rows"],
                "duplicate_value": item["duplicate_excess_value"],
                "onhand_value": item["onhand_value"],
                "gap_vs_onhand": item["gap_vs_onhand"],
                "status": "Baseline loaded more than once"
                if item["baseline_duplicated"]
                else ("Gap to on-hand" if abs(item["gap_vs_onhand"]) > 0.01 else "Consistent"),
            }
        )
    return _pack(
        "Valuation Suspense Integrity — baseline duplicates and suspense vs on-hand",
        [
            "company",
            "pending_entries",
            "pending_total",
            "baseline_total",
            "duplicate_rows",
            "duplicate_value",
            "onhand_value",
            "gap_vs_onhand",
            "status",
        ],
        {
            "company": "Company",
            "pending_entries": "Pending Entries",
            "pending_total": "Pending Total",
            "baseline_total": "Baseline (initial count)",
            "duplicate_rows": "Duplicate Rows",
            "duplicate_value": "Duplicated Value",
            "onhand_value": "On-hand Value",
            "gap_vs_onhand": "Gap vs On-hand",
            "status": "Status",
        },
        rows,
        [
            "A duplicate is a pending initial-count row identical to another (part, "
            "reference, quantity, unit cost). This report changes nothing: removing "
            "duplicates before the 2026-11-30 M19 cutover is a Finance decision.",
            "Gap = baseline after de-duplication + every later movement − the on-hand "
            "value of the owned classes.",
        ],
        empty="No pending valuation suspense entries.",
    )


def stock_gl_tieout(env, date_from=None, date_to=None, **params):
    """D1 (A06 ERP audit): stock valuation subledger vs on-hand (qty x unit
    cost) vs the general ledger, per stock account and operating unit, as at
    date_to (default: today in Dhaka). Finance and cost viewers only."""
    if not _sees_cost(env):
        return _restricted("Stock to GL Tie-out")
    rows, notes = [], []
    for company in env.companies:
        data = env["fix.inventory.valuation.suspense"].get_stock_gl_tieout(
            company.id, date_to or None
        )
        for r in data["rows"]:
            ok = abs(r["gl_minus_subledger"]) < 0.005 and abs(r["subledger_minus_onhand"]) <= r.get(
                "rounding_allowance", 0.0
            )
            rows.append(
                {
                    "company": data["company"],
                    "account_code": r["account_code"],
                    "operating_unit": r["operating_unit"],
                    "subledger_value": r["subledger_value"],
                    "onhand_value": r["onhand_value"],
                    "gl_balance": r["gl_balance"],
                    "gl_minus_subledger": r["gl_minus_subledger"],
                    "subledger_minus_onhand": r["subledger_minus_onhand"],
                    "status": "Ties out" if ok else "Break",
                }
            )
        if not data.get("realtime_since"):
            notes.append(
                "%s has not taken its stock on to the GL yet (posting is real time "
                "from the take-on)." % data["company"]
            )
    notes += [
        "GL and subledger agree to the paisa; subledger and qty x unit cost may "
        "differ by the 4-decimal unit-cost rounding only.",
        "A break is investigated before the period is closed.",
    ]
    return _pack(
        "Stock to GL Tie-out — subledger, on-hand and general ledger by account and branch",
        [
            "company",
            "account_code",
            "operating_unit",
            "subledger_value",
            "onhand_value",
            "gl_balance",
            "gl_minus_subledger",
            "subledger_minus_onhand",
            "status",
        ],
        {
            "company": "Company",
            "account_code": "Stock Account",
            "operating_unit": "Operating Unit",
            "subledger_value": "Subledger",
            "onhand_value": "On-hand (qty x cost)",
            "gl_balance": "GL Balance",
            "gl_minus_subledger": "GL − Subledger",
            "subledger_minus_onhand": "Subledger − On-hand",
            "status": "Status",
        },
        rows,
        notes,
        empty="No stock account balance or stock on hand.",
    )


REPORTS = {
    "suspense_integrity": suspense_integrity,
    "stock_gl_tieout": stock_gl_tieout,
    "ownership_classes": ownership_classes,
    "availability": availability,
    "genealogy": genealogy,
    "van_stock": van_stock,
    "valuation_by_class": valuation_by_class,
    "ageing": ageing,
    # the key the screens used before X32 (kept so a saved link still opens)
    "ageeing": ageing,
    "abc_segmentation": abc_segmentation,
    "accuracy_audit": accuracy_audit,
    "van_variance": van_variance,
    "transfer_performance": transfer_performance,
    "adjustment_register": adjustment_register,
    "quarantine_register": quarantine_register,
    "rtv_register": rtv_register,
    "stockout_register": stockout_register,
    "branch_position": branch_position,
    "movers": movers,
}


def _pct(part, whole):
    return round(part / whole * 100.0, 1) if whole else None


def kpis(env):
    """Read as the caller, in the caller's companies; only owned stock is
    valued. Month to date in Dhaka (X32). KPI-042..047 per spec section 15."""
    onhand = _onhand(env)
    sees_cost = _sees_cost(env)
    value = _value(onhand) if sees_cost else None
    stocked_parts = len(onhand.filtered(lambda r: (r.qty or 0.0) > 0).mapped("part_id"))
    today = _today(env)
    month_start = today.replace(day=1)
    company = [("company_id", "in", env.companies.ids)]
    # A23: below the REAL minimum - a reorder rule's, on unrestricted available
    # stock at its own location (no part-master default min of 5 any more)
    rules = _mine(env, "fix.reorder.rule", [("state", "!=", "archived")])
    below = rules.filtered(lambda r: (r.current_stock or 0.0) <= (r.min_qty or 0.0) + 1e-6)
    stockout = rules.filtered(lambda r: (r.current_stock or 0.0) <= 1e-6)
    # a figure over confirmed recons only: a draft's variance would tell the
    # counter how far off his typed count is (M15-8)
    recons = _mine(
        env,
        "fix.stock.van.recon",
        [("recon_date", ">=", month_start), ("state", "!=", "draft")],
    )
    van_var = sum(abs(r.sudo().variance or 0.0) for r in recons)
    van_expected = sum(abs(r.sudo().expected_qty or 0.0) for r in recons)
    # KPI-042: posted count lines this month within tolerance
    pct = _count_tolerance(env)
    lines = (
        env["fix.stock.count.line"]
        .sudo()
        .search(
            [
                ("count_id.company_id", "in", env.companies.ids),
                ("count_id.state", "=", "posted"),
                ("count_id.counted_on", ">=", month_start),
            ]
        )
    )
    accurate = len([ln for ln in lines if _accurate(ln, pct)])
    # KPI-043 / 044: demand met at first request vs backorders this month
    start_dt = _datetime_domain("create_date", month_start, today)
    issues = env["fix.stock.consumption"].search_count(
        [*company, ("state", "in", ("consumed", "returned")), *start_dt]
    )
    backorders = _mine(env, "fix.stock.backorder", start_dt)
    jobs_waiting = {b.service_order_ref for b in backorders if b.service_order_ref}
    jobs = (
        set(_mine(env, "fix.stock.consumption", start_dt).mapped("service_order_ref"))
        | jobs_waiting
    )
    # KPI-045 / 046: turns (issue value, annualised) and dead stock share
    turns = dead_pct = None
    if sees_cost and value:
        year_ago = today - datetime.timedelta(days=365)
        issued = sum(
            -(log.value or 0.0)
            for log in env["fix.stock.move.log"]
            .sudo()
            .search(
                [
                    ("company_id", "in", env.companies.ids),
                    ("move_date", ">=", year_ago),
                    ("qty", "<", 0),
                    ("res_model", "=", "fix.stock.consumption"),
                ]
            )
        )
        turns = round(issued / value, 2)
        dead = sum(
            (r.qty or 0.0) * (r.sudo().unit_cost or 0.0)
            for r in onhand
            if r.ownership_class in _VALUED
            and (not r.last_move_date or (today - r.last_move_date).days > 365)
        )
        dead_pct = _pct(dead, value)
    return {
        "stock_value": round(value, 2) if value is not None else None,
        "stocked_skus": stocked_parts,
        "stockout_skus": len(stockout.mapped("spare_part_id")),
        "below_min_lines": len(below),
        "pending_counts": env["fix.stock.count"].search_count(
            [*company, ("state", "in", ("draft", "recount", "to_approve", "to_dofa"))]
        ),
        "open_transfers": env["fix.stock.transfer"].search_count(
            [*company, ("state", "in", ("draft", "submitted", "approved", "dispatched"))]
        ),
        "van_variance_pcs": round(van_var, 3),
        "kpi_042_accuracy_pct": _pct(accurate, len(lines)),
        "kpi_043_first_request_pct": _pct(issues, issues + len(backorders)),
        "kpi_044_stockout_delay_pct": _pct(len(jobs_waiting), len(jobs)),
        "kpi_045_turns": turns,
        "kpi_046_dead_stock_pct": dead_pct,
        "kpi_047_van_variance_pct": _pct(van_var, van_expected),
    }
