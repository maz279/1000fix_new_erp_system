# A06 · M16 Procurement & Sourcing — surfaces, packs and KPIs over requisitions,
# RFQs/bids/awards, POs, PO goods receipts, blankets, expediting and inspection
# outcomes. The warehouse stock receipt and RTV screens read M15's documents
# (single-owner surfaces).
import datetime

# A06 workflow audit (2026-11-03) M16-9/M16-13: every transition the screens
# need is declared here; approval itself is decided in the M63 inbox (the
# requisition and PO approvals are routed), never by a button on the record.
SURFACES = {
    # A06 R5: the goods receipt against a PO line (M16-6); posting it feeds
    # the three-way match, so it is posted by its action only.
    "fix.purchase.receipt": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_post", "action_cancel"},
    },
    "fix.purchase.receipt.line": {"order": "id desc", "limit": 500, "actions": set()},
    "fix.requisition": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_submit",
            "action_request_approval",
            "action_recall_approval",
            "action_reset_draft",
            "action_cancel",
            "action_convert_to_po",
            "action_emergency_release",
            "action_emergency_close",
        },
    },
    "fix.purchase.order": {
        "order": "date_order desc, id desc",
        "limit": 300,
        "actions": {
            "action_submit_for_approval",
            "action_recall_approval",
            "action_record_requisition_exception",
            "action_send",
            "action_acknowledge_on_behalf",
            "action_create_change_order",
            "action_cancel",
            "action_close",
            "action_start_receipt",
            # an import purchase order raises its M44 import order
            "action_create_import_order",
        },
    },
    "fix.purchase.order.line": {"order": "order_id, id", "limit": 400, "actions": set()},
    # A local supplier's proforma and the advance against it (12 Nov 2026).
    # Read as the caller: the company / operating-unit rules apply.
    "fix.purchase.proforma": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_reject", "action_cancel"},
        "rules": True,
    },
    "fix.purchase.advance": {
        "order": "create_date desc, id desc",
        "limit": 300,
        # action_request_payment: an Accountant asks treasury to pay an approved
        # advance (cd_ap_ext fix_ap_supplier_advance)
        "actions": {
            "action_request",
            "action_approve",
            "action_reject",
            "action_cancel",
            "action_request_payment",
        },
        "rules": True,
    },
    "fix.procurement.rfq": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_open", "action_close"},
    },
    # M16-5: read as the caller, so the sealed-bid record rule applies; the sudo
    # list and form showed every vendor and price on an open RFQ to any employee.
    "fix.procurement.bid": {
        "order": "rfq_id, unit_price",
        "limit": 400,
        "actions": set(),
        "rules": True,
    },
    "fix.procurement.award": {
        "order": "decided_on desc, id desc",
        "limit": 200,
        "actions": {"action_decide", "action_cancel", "action_create_po"},
    },
    "fix.procurement.blanket": {
        "order": "valid_to desc, id desc",
        "limit": 200,
        "actions": {"action_activate", "action_revise", "action_cancel"},
    },
    "fix.procurement.expedite": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_chase", "action_resolve"},
    },
    "fix.procurement.inspection": {
        "order": "inspected_on desc, id desc",
        "limit": 300,
        "actions": {"action_confirm"},
    },
}

_OPEN_REQ = ("draft", "submitted", "approved")
_OPEN_PO = ("draft", "sent", "acknowledged", "partially_received")


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


def _company_domain(env, field="company_id"):
    return [(field, "in", env.companies.ids)]


def _orders(env):
    """The caller's purchase orders (their own rights, their companies)."""
    return env["fix.purchase.order"].search(_company_domain(env))


def _lines(env):
    return env["fix.purchase.order.line"].search(_company_domain(env, "order_id.company_id"))


def _category(product):
    return product.categ_id.name if product and product.categ_id else "Uncategorised"


def spend_by_category(env, date_from=None, date_to=None, **params):
    buckets = {}
    for line in _lines(env):
        order = line.order_id
        if order.state == "cancelled":
            continue
        key = (_category(line.product_id), order.vendor_id.name)
        row = buckets.setdefault(
            key,
            {
                "category": key[0],
                "vendor": key[1],
                "lines": 0,
                "amount": 0.0,
            },
        )
        row["lines"] += 1
        row["amount"] += line.line_total or 0.0
    rows = []
    for row in buckets.values():
        row["amount"] = round(row["amount"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["amount"])
    total = sum(r["amount"] for r in rows)
    for row in rows:
        row["share_pct"] = round((row["amount"] / total) * 100.0, 1) if total else 0.0
    return _pack(
        "Spend by Category & Vendor — PO lines, cancelled excluded",
        ["category", "vendor", "lines", "amount", "share_pct"],
        {
            "category": "Category",
            "vendor": "Vendor",
            "lines": "Lines",
            "amount": "Spend",
            "share_pct": "Share %",
        },
        rows,
        [
            "Spend is the PO line total (ordered quantity × unit price), not the "
            "invoice amount — the AP leg is M20/M52."
        ],
        totals={
            "category": "Total",
            "lines": sum(r["lines"] for r in rows),
            "amount": round(total, 2),
        },
        empty="No purchase order lines yet.",
    )


def match_exception(env, date_from=None, date_to=None, **params):
    rows = []
    for line in _lines(env):
        order = line.order_id
        if order.state in ("draft", "cancelled", "closed"):
            continue
        short = round((line.qty_ordered or 0.0) - (line.qty_received or 0.0), 3)
        if short <= 0:
            continue
        rows.append(
            {
                "po": order.name,
                "vendor": order.vendor_id.name,
                "product": line.product_id.display_name,
                "ordered": round(line.qty_ordered or 0.0, 3),
                "received": round(line.qty_received or 0.0, 3),
                "short": short,
                "value": round(short * (line.unit_price or 0.0), 2),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Match Exception Pareto — ordered vs received shortfalls",
        ["po", "vendor", "product", "ordered", "received", "short", "value", "state"],
        {
            "po": "PO",
            "vendor": "Vendor",
            "product": "Product",
            "ordered": "Ordered",
            "received": "Received",
            "short": "Short",
            "value": "Short Value",
            "state": "State",
        },
        rows,
        [
            "The invoice leg of the three-way match is M20/M52's; this workbench "
            "shows the ORDERED vs RECEIVED exception and its value."
        ],
        totals={
            "po": "Total",
            "short": round(sum(r["short"] for r in rows), 3),
            "value": round(sum(r["value"] for r in rows), 2),
        },
        empty="No ordered/received exceptions.",
    )


def otd_by_vendor(env, date_from=None, date_to=None, **params):
    buckets = {}
    for order in _orders(env):
        due = order.vendor_confirmed_date or order.promised_date
        if not order.received_on or not due:
            continue
        key = order.vendor_id.name
        row = buckets.setdefault(
            key,
            {
                "vendor": key,
                "pos": 0,
                "on_time": 0,
                "late": 0,
                "late_days": 0,
            },
        )
        row["pos"] += 1
        if order.received_on <= due:
            row["on_time"] += 1
        else:
            row["late"] += 1
            row["late_days"] += (order.received_on - due).days
    rows = []
    for row in buckets.values():
        row["otd_pct"] = round((row["on_time"] / row["pos"]) * 100.0, 1) if row["pos"] else 0.0
        rows.append(row)
    rows.sort(key=lambda r: r["otd_pct"])
    return _pack(
        "OTD by Vendor — received against the promised date",
        ["vendor", "pos", "on_time", "late", "late_days", "otd_pct"],
        {
            "vendor": "Vendor",
            "pos": "POs",
            "on_time": "On Time",
            "late": "Late",
            "late_days": "Late Days",
            "otd_pct": "OTD %",
        },
        rows,
        [
            "Only POs with both a due date (vendor-confirmed, else promised) and a "
            "received date count; a missing date is excluded rather than guessed. Both "
            "dates are stamped by their actions and cannot be edited."
        ],
        totals={
            "vendor": "Total",
            "pos": sum(r["pos"] for r in rows),
            "on_time": sum(r["on_time"] for r in rows),
            "late": sum(r["late"] for r in rows),
        },
        empty="No POs with promised and received dates yet.",
    )


def price_variance(env, date_from=None, date_to=None, **params):
    history = {}
    for line in _lines(env):
        order = line.order_id
        if order.state == "cancelled":
            continue
        key = (line.product_id.display_name, order.vendor_id.name)
        history.setdefault(key, []).append(
            (order.date_order or datetime.datetime.min, line.unit_price or 0.0)
        )
    rows = []
    for (product, vendor), entries in history.items():
        entries.sort(key=lambda e: e[0])
        if len(entries) < 2:
            continue
        previous = entries[-2][1]
        latest = entries[-1][1]
        variance = round(((latest - previous) / previous) * 100.0, 1) if previous else 0.0
        rows.append(
            {
                "product": product,
                "vendor": vendor,
                "previous_price": round(previous, 2),
                "latest_price": round(latest, 2),
                "variance_pct": variance,
                "alert": abs(variance) > 10.0,
            }
        )
    rows.sort(key=lambda r: -abs(r["variance_pct"]))
    return _pack(
        "Price Variance Alert — latest against previous PO price",
        ["product", "vendor", "previous_price", "latest_price", "variance_pct", "alert"],
        {
            "product": "Product",
            "vendor": "Vendor",
            "previous_price": "Previous",
            "latest_price": "Latest",
            "variance_pct": "Variance %",
            "alert": "Alert (>10%)",
        },
        rows,
        [
            "A product/vendor pair needs at least two PO lines; the alert threshold "
            "is an explicit 10% band."
        ],
        empty="No product/vendor pair has two recorded prices yet.",
    )


def maverick_spend(env, date_from=None, date_to=None, **params):
    orders = _orders(env)
    spend_orders = orders.filtered(lambda o: o.state != "cancelled")
    maverick = spend_orders.filtered(
        lambda o: not o.requisition_id or o.requisition_id.state != "converted"
    )
    total = sum(spend_orders.mapped("amount_total"))
    maverick_total = sum(maverick.mapped("amount_total"))
    rows = []
    for order in maverick:
        rows.append(
            {
                "po": order.name,
                "vendor": order.vendor_id.name,
                "amount": round(order.amount_total or 0.0, 2),
                "state": dict(order._fields["state"].selection).get(order.state),
                "date": str(order.date_order)[:10] if order.date_order else "—",
                "exception": "documented" if order.no_requisition_exception else "none",
            }
        )
    rows.sort(key=lambda r: -r["amount"])
    return _pack(
        "Maverick Spend — POs with no approved requisition behind them",
        ["po", "vendor", "amount", "state", "date", "exception"],
        {
            "po": "PO",
            "vendor": "Vendor",
            "amount": "Amount",
            "state": "State",
            "date": "Order Date",
            "exception": "Manager Exception",
        },
        rows,
        [
            "Maverick value %s of %s total PO spend (%.1f%%)."
            % (
                round(maverick_total, 2),
                round(total, 2),
                (maverick_total / total) * 100.0 if total else 0.0,
            )
        ],
        totals={"po": "Total", "amount": round(maverick_total, 2)},
        empty="Every PO traces to a requisition.",
    )


def po_cycle_time(env, date_from=None, date_to=None, **params):
    rows = []
    for order in _orders(env):
        days = "—"
        if order.date_order and order.received_on:
            days = (order.received_on - order.date_order.date()).days
        rows.append(
            {
                "po": order.name,
                "vendor": order.vendor_id.name,
                "ordered": str(order.date_order)[:10] if order.date_order else "—",
                "promised": str(order.promised_date) if order.promised_date else "—",
                "received": str(order.received_on) if order.received_on else "—",
                "cycle_days": days,
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: str(r["po"]), reverse=True)
    return _pack(
        "PO Cycle Time — order to receipt",
        ["po", "vendor", "ordered", "promised", "received", "cycle_days", "state"],
        {
            "po": "PO",
            "vendor": "Vendor",
            "ordered": "Ordered",
            "promised": "Promised",
            "received": "Received",
            "cycle_days": "Cycle (days)",
            "state": "State",
        },
        rows,
        ["Cycle days = received date − order date; an open PO shows '—'."],
        empty="No purchase orders yet.",
    )


def consolidation(env, date_from=None, date_to=None, **params):
    reqs = env["fix.requisition"].search(_company_domain(env))
    buckets = {}
    for req in reqs:
        key = (
            req.branch_id.name if req.branch_id else "No branch",
            dict(req._fields["urgency"].selection).get(req.urgency),
        )
        row = buckets.setdefault(
            key,
            {
                "branch": key[0],
                "urgency": key[1],
                "requests": 0,
                "amount": 0.0,
            },
        )
        row["requests"] += 1
        row["amount"] += req.estimate_amount or 0.0
    rows = []
    for row in buckets.values():
        row["amount"] = round(row["amount"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["amount"])
    return _pack(
        "Cross-Branch Consolidation — requisitions by branch and urgency",
        ["branch", "urgency", "requests", "amount"],
        {
            "branch": "Branch",
            "urgency": "Urgency",
            "requests": "Requisitions",
            "amount": "Estimated Amount",
        },
        rows,
        [
            "Consolidation view: the same branch/urgency bucket is one buying "
            "conversation. Amounts are the requisition estimates."
        ],
        totals={
            "branch": "Total",
            "requests": sum(r["requests"] for r in rows),
            "amount": round(sum(r["amount"] for r in rows), 2),
        },
        empty="No requisitions yet.",
    )


def price_history(env, date_from=None, date_to=None, **params):
    rows = []
    for line in _lines(env):
        order = line.order_id
        if order.state == "cancelled":
            continue
        rows.append(
            {
                "date": str(order.date_order)[:10] if order.date_order else "—",
                "po": order.name,
                "vendor": order.vendor_id.name,
                "product": line.product_id.display_name,
                "qty": round(line.qty_ordered or 0.0, 3),
                "unit_price": round(line.unit_price or 0.0, 2),
                "line_total": round(line.line_total or 0.0, 2),
            }
        )
    rows.sort(key=lambda r: (r["product"], r["date"]), reverse=False)
    return _pack(
        "Price History — every PO line by product",
        ["date", "po", "vendor", "product", "qty", "unit_price", "line_total"],
        {
            "date": "Date",
            "po": "PO",
            "vendor": "Vendor",
            "product": "Product",
            "qty": "Qty",
            "unit_price": "Unit Price",
            "line_total": "Line Total",
        },
        rows,
        ["Recorded PO prices only — no catalogue price is implied."],
        empty="No purchase order lines yet.",
    )


def _invoiced(env, order, product):
    """Quantity billed on live (not rejected) bills, under the caller's rights."""
    if "fix.vendor.invoice.line" not in env:
        return None
    lines = env["fix.vendor.invoice.line"].search(
        [
            ("invoice_id.requisition_id", "=", order.id),
            ("invoice_id.approval_state", "!=", "rejected"),
            ("product_id", "=", product.id),
        ]
    )
    return round(sum(lines.mapped("quantity")), 3)


def three_way(env, date_from=None, date_to=None, **params):
    rows = []
    for line in _lines(env):
        order = line.order_id
        if order.state in ("draft", "cancelled", "superseded"):
            continue
        invoiced = _invoiced(env, order, line.product_id)
        rows.append(
            {
                "po": order.name,
                "product": line.product_id.display_name,
                "ordered": round(line.qty_ordered or 0.0, 3),
                "received": round(line.qty_received or 0.0, 3),
                "accepted": round(line.qty_accepted or 0.0, 3),
                "invoice_qty": "—" if invoiced is None else invoiced,
                "variance": round((line.qty_accepted or 0.0) - (invoiced or 0.0), 3),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: str(r["po"]), reverse=True)
    return _pack(
        "3-Way Match Workbench — order, receipt and invoice",
        ["po", "product", "ordered", "received", "accepted", "invoice_qty", "variance", "state"],
        {
            "po": "PO",
            "product": "Product",
            "ordered": "Ordered",
            "received": "Received",
            "accepted": "Accepted",
            "invoice_qty": "Invoiced",
            "variance": "Accepted − Invoiced",
            "state": "State",
        },
        rows,
        [
            "Received and accepted come from POSTED goods receipts (accepted = passed "
            "inspection); invoiced is the quantity on live bills against the PO "
            "(fix.vendor.invoice.requisition_id). A negative variance is billed but not "
            "accepted: the three-way match blocks it."
        ],
        empty="No received purchase order lines yet.",
    )


def _po_value(line, qty):
    return qty * (line.approved_unit_price if line.approved_qty else line.unit_price or 0.0)


def gr_ir(env, date_from=None, date_to=None, **params):
    """Goods received against bills, by PO and valued per product, so that a line
    received and not billed never nets off against another billed and not received.
    Received is net of what inspection rejected: rejected goods go back to the vendor."""
    Bill = env.get("fix.vendor.invoice.line")
    rows = []
    for order in _orders(env):
        if order.state in ("draft", "cancelled", "superseded"):
            continue
        received = {}
        for line in order.line_ids:
            qty = sum(
                r.qty_received - r.qty_rejected
                for r in line.receipt_line_ids
                if r.state == "posted"
            )
            received[line.product_id.id] = received.get(line.product_id.id, 0.0) + _po_value(
                line, qty
            )
        invoiced = {}
        if Bill is not None:
            for bill in Bill.search(
                [
                    ("invoice_id.requisition_id", "=", order.id),
                    ("invoice_id.approval_state", "!=", "rejected"),
                ]
            ):
                value = (bill.quantity or 0.0) * (bill.unit_price or 0.0)
                invoiced[bill.product_id.id] = invoiced.get(bill.product_id.id, 0.0) + value
        not_invoiced = not_received = 0.0
        for product in set(received) | set(invoiced):
            gap = received.get(product, 0.0) - invoiced.get(product, 0.0)
            not_invoiced += max(gap, 0.0)
            not_received += max(-gap, 0.0)
        if not_invoiced < 0.005 and not_received < 0.005:
            continue
        rows.append(
            {
                "po": order.name,
                "vendor": order.vendor_id.name,
                "received_value": round(sum(received.values()), 2),
                "invoiced_value": round(sum(invoiced.values()), 2),
                "received_not_invoiced": round(not_invoiced, 2),
                "invoiced_not_received": round(not_received, 2),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: -(r["received_not_invoiced"] + r["invoiced_not_received"]))
    return _pack(
        "GR/IR Reconciliation — received not invoiced, invoiced not received",
        [
            "po",
            "vendor",
            "received_value",
            "invoiced_value",
            "received_not_invoiced",
            "invoiced_not_received",
            "state",
        ],
        {
            "po": "PO",
            "vendor": "Vendor",
            "received_value": "Received Value",
            "invoiced_value": "Invoiced Value",
            "received_not_invoiced": "Received, Not Invoiced",
            "invoiced_not_received": "Invoiced, Not Received",
            "state": "State",
        },
        rows,
        [
            "Received comes from POSTED goods receipts, net of quantity rejected at inspection, "
            "at the approved PO price; invoiced from bills on the PO that were not rejected. "
            "POs that agree are not listed."
        ],
        totals={
            "po": "Total",
            "received_not_invoiced": round(sum(r["received_not_invoiced"] for r in rows), 2),
            "invoiced_not_received": round(sum(r["invoiced_not_received"] for r in rows), 2),
        },
        empty="Every issued PO agrees: nothing received and not invoiced, or invoiced and not received.",
    )


def emergency_spend(env, date_from=None, date_to=None, **params):
    """BRU-PRO-12 / FR-PRO-036: an emergency purchase is counted."""
    reqs = env["fix.requisition"].search(
        [*_company_domain(env), ("emergency_state", "!=", False)],
        order="emergency_released_at desc",
    )
    spend = sum(_orders(env).filtered(lambda o: o.state != "cancelled").mapped("amount_total"))
    total = sum(reqs.mapped("estimate_amount"))
    rows = [
        {
            "requisition": req.description,
            "branch": req.branch_id.name if req.branch_id else "—",
            "amount": round(req.estimate_amount or 0.0, 2),
            "reason": req.emergency_reason or "",
            "released": str(req.emergency_released_at)[:16] if req.emergency_released_at else "—",
            "due": str(req.emergency_deadline)[:16] if req.emergency_deadline else "—",
            "path": dict(req._fields["emergency_state"].selection).get(req.emergency_state),
        }
        for req in reqs
    ]
    return _pack(
        "Emergency Purchases — post-hoc approval and share of spend",
        ["requisition", "branch", "amount", "reason", "released", "due", "path"],
        {
            "requisition": "Requisition",
            "branch": "Branch",
            "amount": "Amount",
            "reason": "Reason",
            "released": "Released",
            "due": "Post-Hoc Due",
            "path": "Status",
        },
        rows,
        [
            "Emergency value %s against %s total PO spend (%.1f%%); the module's target is under "
            "8%% of spend."
            % (round(total, 2), round(spend, 2), (total / spend) * 100.0 if spend else 0.0)
        ],
        totals={"requisition": "Total", "amount": round(total, 2)},
        empty="No emergency purchases.",
    )


REPORTS = {
    "spend_by_category": spend_by_category,
    "match_exception": match_exception,
    "otd_by_vendor": otd_by_vendor,
    "price_variance": price_variance,
    "maverick_spend": maverick_spend,
    "po_cycle_time": po_cycle_time,
    "consolidation": consolidation,
    "price_history": price_history,
    "three_way": three_way,
    "gr_ir": gr_ir,
    "emergency_spend": emergency_spend,
}


def kpis(env):
    reqs = env["fix.requisition"].search(_company_domain(env))
    rfqs = env["fix.procurement.rfq"].search(_company_domain(env))
    orders = _orders(env)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    spend_mtd = sum(
        order.amount_total or 0.0
        for order in orders
        if order.state != "cancelled"
        and order.date_order
        and order.date_order.date() >= month_start
    )
    received = orders.filtered(
        lambda o: o.received_on and (o.vendor_confirmed_date or o.promised_date)
    )
    on_time = received.filtered(
        lambda o: o.received_on <= (o.vendor_confirmed_date or o.promised_date)
    )
    exceptions = 0
    for line in _lines(env):
        order = line.order_id
        if order.state in ("draft", "cancelled", "closed"):
            continue
        if (line.qty_received or 0.0) < (line.qty_ordered or 0.0):
            exceptions += 1
    return {
        "open_requisitions": len(reqs.filtered(lambda r: r.state in _OPEN_REQ)),
        "rfq_open": len(rfqs.filtered(lambda r: r.state == "open")),
        "po_open": len(orders.filtered(lambda o: o.state in _OPEN_PO)),
        "match_exceptions": exceptions,
        "spend_mtd": round(spend_mtd, 2),
        "otd_pct": round((len(on_time) / len(received)) * 100.0, 1) if received else 0.0,
    }
