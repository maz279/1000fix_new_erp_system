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
import datetime

from .writable import WRITABLE as _WRITABLE

SURFACES = {
    "fix.stock.onhand": {"order": "part_id, location_id", "limit": 400, "actions": set()},
    "fix.stock.lot": {"order": "received_on desc, id desc", "limit": 400, "actions": set()},
    "fix.stock.consumption": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_scan_and_consume", "action_return_part"},
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
        },
    },
    "fix.stock.transfer.line": {"order": "transfer_id, id", "limit": 400, "actions": set()},
    "fix.stock.count": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_post", "action_approve", "action_reject"},
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
}

# Surfaces whose write whitelist the lead generates from the forms
# (controllers/form_fields.py --a06). Served once writable.py lists them, so
# the package never imports a surface without a whitelist.
_PENDING_SURFACES = {
    "fix.stock.class.change": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
}
SURFACES.update({m: c for m, c in _PENDING_SURFACES.items() if m in _WRITABLE})

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


def _value(rows):
    return sum((r.qty or 0.0) * (r.unit_cost or 0.0) for r in rows if r.ownership_class in _VALUED)


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
    return _pack(
        "6 Ownership Classes — on-hand quantity and value",
        ["ownership", "lines", "qty", "value"],
        {"ownership": "Ownership Class", "lines": "Lines", "qty": "Quantity", "value": "Value"},
        rows,
        [
            "Value = on-hand quantity × the bucket's average cost. Consignment and "
            "customer property are held, not owned: they carry no value (BRU-INV-02)."
        ],
        totals={
            "ownership": "Total",
            "lines": sum(r["lines"] for r in rows),
            "qty": round(sum(r["qty"] for r in rows), 3),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No on-hand rows recorded yet.",
    )


def availability(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _onhand(env).filtered(
        lambda r: (r.available_qty or 0.0) > 0 and r.stock_status == "unrestricted"
    ):
        rows.append(
            {
                "part": rec.part_id.part_number,
                "description": rec.part_id.name,
                "location": rec.location_id.code,
                "ownership": _OWNERSHIP_LABELS.get(rec.ownership_class, rec.ownership_class),
                "available": round(rec.available_qty, 3),
                "unit_cost": round(rec.unit_cost or 0.0, 2),
            }
        )
    rows.sort(key=lambda r: (r["part"], -r["available"]))
    return _pack(
        "Network Availability — available quantity by location",
        ["part", "description", "location", "ownership", "available", "unit_cost"],
        {
            "part": "Part Number",
            "description": "Description",
            "location": "Location",
            "ownership": "Ownership",
            "available": "Available",
            "unit_cost": "Unit Cost",
        },
        rows,
        [
            "Available = unrestricted on-hand − reserved, per location and ownership "
            "class; quarantined, in-transit and staged stock is not available."
        ],
        totals={"part": "Total", "available": round(sum(r["available"] for r in rows), 3)},
        empty="No available stock recorded yet.",
    )


def genealogy(env, date_from=None, date_to=None, **params):
    consumptions = _mine(env, "fix.stock.consumption", order="create_date desc", limit=300)
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
            "serial stays visible as '—' rather than being hidden."
        ],
        empty="No part consumption recorded yet.",
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
            "technician comes from the location's assigned technician."
        ],
        totals={
            "van": "Total",
            "qty": round(sum(r["qty"] for r in rows), 3),
            "available": round(sum(r["available"] for r in rows), 3),
        },
        empty="No van stock recorded yet.",
    )


def valuation_by_class(env, date_from=None, date_to=None, **params):
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
            "Each bucket carries its weighted-average cost (receipts average in; issues, "
            "transfers and scrap leave at it). Consignment and customer property are "
            "excluded: they are not 1000FiX's inventory."
        ],
        totals={
            "part": "Total",
            "qty": round(sum(r["qty"] for r in rows), 3),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No on-hand rows recorded yet.",
    )


def ageeing(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    lots = _mine(env, "fix.stock.lot", [("status", "=", "in_stock")])
    rows = []
    for lot in lots:
        age = (today - lot.received_on).days if lot.received_on else 0
        if age > 365:
            bucket, action = ">365 days", "Write-off review"
        elif age > 180:
            bucket, action = "181–365 days", "Markdown / return"
        elif age > 90:
            bucket, action = "91–180 days", "Move first"
        else:
            bucket, action = "0–90 days", "Healthy"
        rows.append(
            {
                "lot": lot.name,
                "part": lot.part_id.part_number,
                "location": lot.location_id.code if lot.location_id else "—",
                "received_on": str(lot.received_on) if lot.received_on else "—",
                "age_days": age,
                "qty": round(lot.qty or 0.0, 3),
                "bucket": bucket,
                "action": action,
            }
        )
    rows.sort(key=lambda r: -r["age_days"])
    return _pack(
        "Ageing & Dead Stock — lots by days held",
        ["lot", "part", "location", "received_on", "age_days", "qty", "bucket", "action"],
        {
            "lot": "Serial / Lot",
            "part": "Part",
            "location": "Location",
            "received_on": "Received",
            "age_days": "Days Held",
            "qty": "Qty",
            "bucket": "Age Bucket",
            "action": "Policy",
        },
        rows,
        [
            "Age runs from the lot's received date; the policy buckets are explicit "
            "(90/180/365 days), not a scoring model."
        ],
        empty="No in-stock lots recorded yet.",
    )


def abc_segmentation(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _onhand(env).filtered(lambda r: r.ownership_class in _VALUED):
        value = (rec.qty or 0.0) * (rec.unit_cost or 0.0)
        last = rec.last_move_date
        if last and (datetime.date.today() - last).days <= 30:
            movement = "X — fast"
        elif last and (datetime.date.today() - last).days <= 90:
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
    return _pack(
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
            "since last movement (X ≤30, Y ≤90, Z beyond). Criticality is the part master's."
        ],
        empty="No on-hand rows recorded yet.",
    )


def accuracy_audit(env, date_from=None, date_to=None, **params):
    counts = _mine(env, "fix.stock.count")
    # blind counts: the expected quantity is revealed once a count is posted
    # (or to an Inventory Controller); open counts are listed without it
    lines = env["fix.stock.count.line"].search([("count_id", "in", counts.ids)])
    rows = []
    for line in lines:
        rows.append(
            {
                "count": line.count_id.name,
                "location": line.count_id.location_id.code,
                "type": dict(line.count_id._fields["count_type"].selection).get(
                    line.count_id.count_type
                ),
                "part": line.part_id.part_number,
                "expected": round(line.expected_qty or 0.0, 3),
                "counted": round(line.counted_qty or 0.0, 3),
                "variance": round(line.variance or 0.0, 3),
                "state": dict(line.count_id._fields["state"].selection).get(line.count_id.state),
            }
        )
    rows.sort(key=lambda r: -abs(r["variance"]))
    total_lines = len(lines)
    exact = len([r for r in rows if r["variance"] == 0])
    return _pack(
        "Inventory Accuracy Audit — count lines and variance",
        ["count", "location", "type", "part", "expected", "counted", "variance", "state"],
        {
            "count": "Count",
            "location": "Location",
            "type": "Type",
            "part": "Part",
            "expected": "Expected",
            "counted": "Counted",
            "variance": "Variance",
            "state": "State",
        },
        rows,
        [
            "%d counts, %d lines; %d line(s) exact — accuracy %.1f%% by exact-match lines."
            % (
                len(counts),
                total_lines,
                exact,
                (exact / total_lines) * 100.0 if total_lines else 0.0,
            )
        ],
        totals={
            "count": "Total",
            "expected": round(sum(r["expected"] for r in rows), 3),
            "counted": round(sum(r["counted"] for r in rows), 3),
            "variance": round(sum(r["variance"] for r in rows), 3),
        },
        empty="No stock counts recorded yet.",
    )


def van_variance(env, date_from=None, date_to=None, **params):
    recons = _mine(env, "fix.stock.van.recon")
    rows = []
    for rec in recons:
        rows.append(
            {
                "recon": rec.name,
                "van": rec.location_id.code,
                "technician": rec.technician_id.name if rec.technician_id else "—",
                "date": str(rec.recon_date),
                "expected": round(rec.expected_qty or 0.0, 3),
                "counted": round(rec.counted_qty or 0.0, 3),
                "variance": round(rec.variance or 0.0, 3),
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -abs(r["variance"]))
    return _pack(
        "Van Stock Variance — daily reconciliation",
        ["recon", "van", "technician", "date", "expected", "counted", "variance", "state"],
        {
            "recon": "Reconciliation",
            "van": "Van",
            "technician": "Technician",
            "date": "Date",
            "expected": "Expected",
            "counted": "Counted",
            "variance": "Variance",
            "state": "State",
        },
        rows,
        ["Variance = counted − expected, at the van's total-piece level."],
        totals={
            "recon": "Total",
            "expected": round(sum(r["expected"] for r in rows), 3),
            "counted": round(sum(r["counted"] for r in rows), 3),
            "variance": round(sum(r["variance"] for r in rows), 3),
        },
        empty="No van reconciliations recorded yet.",
    )


def transfer_performance(env, date_from=None, date_to=None, **params):
    transfers = _mine(env, "fix.stock.transfer")
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
        ["Transit days = received − dispatched; open transfers show '—'."],
        empty="No transfers recorded yet.",
    )


def suspense_integrity(env, date_from=None, date_to=None, **params):
    """S0 (read-only): is the initial-count baseline loaded twice, and how
    does the pending M19 suspense compare with the on-hand value?"""
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


REPORTS = {
    "suspense_integrity": suspense_integrity,
    "ownership_classes": ownership_classes,
    "availability": availability,
    "genealogy": genealogy,
    "van_stock": van_stock,
    "valuation_by_class": valuation_by_class,
    "ageeing": ageeing,
    "abc_segmentation": abc_segmentation,
    "accuracy_audit": accuracy_audit,
    "van_variance": van_variance,
    "transfer_performance": transfer_performance,
}


def kpis(env):
    """Read as the caller, in the caller's companies; only owned stock is valued."""
    onhand = _onhand(env)
    value = _value(onhand)
    stocked_parts = len(onhand.filtered(lambda r: (r.qty or 0.0) > 0).mapped("part_id"))
    parts = _mine(env, "fix.spare.part", [("state", "=", "active")])
    stockouts = len(parts.filtered(lambda p: (p.qty_available or 0.0) <= (p.min_qty or 0.0)))
    today = datetime.date.today()
    month_start = today.replace(day=1)
    van_var = sum(
        abs(r.variance or 0.0)
        for r in _mine(env, "fix.stock.van.recon", [("recon_date", ">=", month_start)])
    )
    company = [("company_id", "in", env.companies.ids)]
    return {
        "stock_value": round(value, 2),
        "stocked_skus": stocked_parts,
        "stockout_skus": stockouts,
        "pending_counts": env["fix.stock.count"].search_count(
            [*company, ("state", "in", ("draft", "recount", "to_approve"))]
        ),
        "open_transfers": env["fix.stock.transfer"].search_count(
            [*company, ("state", "in", ("draft", "submitted", "approved", "dispatched"))]
        ),
        "van_variance_pcs": round(van_var, 3),
    }
