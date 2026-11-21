# A06 · M16 Procurement & Sourcing — surfaces, packs and KPIs over requisitions,
# RFQs/bids/awards, POs, PO goods receipts, blankets, expediting and inspection
# outcomes. The warehouse stock receipt and RTV screens read M15's documents
# (single-owner surfaces).
import datetime

from odoo.exceptions import UserError

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
            # the commercial document standard PDF (18 Nov 2026)
            "action_fix_print",
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
        # FR-PRO-011 (19 Nov 2026): an RFQ invites its suppliers before it opens
        "actions": {"action_open", "action_close", "action_invite_approved_sources"},
    },
    # FR-PRO-009 (19 Nov 2026): the suppliers approved to supply each part
    "fix.procurement.approved.source": {
        "order": "product_id, priority, agreed_price, id",
        "limit": 300,
        "actions": {"action_approve", "action_withdraw"},
    },
    # FR-PRO-037 / BRU-PRO-19 (19 Nov 2026): a service or non-stock line is
    # confirmed by its requester, which posts the receipt the match reads
    "fix.purchase.service.entry": {
        "order": "service_date desc, id desc",
        "limit": 300,
        "actions": {"action_confirm", "action_cancel"},
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
    # A06 P11: post-receipt price amendment, versioned and re-approved
    "fix.purchase.price.amendment": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_submit", "action_approve", "action_reject"},
    },
    "fix.procurement.inspection": {
        "order": "inspected_on desc, id desc",
        "limit": 300,
        "actions": {"action_confirm"},
    },
}

_OPEN_REQ = ("draft", "submitted", "approved")
_OPEN_PO = ("draft", "sent", "acknowledged", "partially_received")


_ISSUED = ("sent", "acknowledged", "partially_received", "received", "closed")
_DHAKA = datetime.timezone(datetime.timedelta(hours=6))
# A06 P33: the price alert band is configuration (it was a hard-coded 10 %)
PARAM_PRICE_ALERT = "cd_requisition.price_alert_pct"


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


# ---- A06 P25 / X31: one basis for every spend figure -----------------------
def _day(value):
    """A date, or the Asia/Dhaka business day of a UTC datetime."""
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=datetime.UTC).astimezone(_DHAKA).date()
    return value


def _today():
    return datetime.datetime.now(_DHAKA).date()


def _bounds(date_from, date_to):
    def parse(v):
        if not v:
            return None
        if isinstance(v, datetime.date):
            return v
        try:
            return datetime.date.fromisoformat(str(v)[:10])
        except ValueError:
            return None

    return parse(date_from), parse(date_to)


def _within(day, date_from, date_to):
    start, end = _bounds(date_from, date_to)
    if (start or end) and not day:
        return False
    return not ((start and day < start) or (end and day > end))


def _issued(order):
    """Spend is what was ISSUED to a supplier: drafts, cancellations and the
    original of a change order (superseded) are not spend."""
    return order.state in _ISSUED


def _bdt(order, amount):
    """`amount` of `order` in BDT at the order's stamped rate (P29)."""
    if not amount:
        return 0.0
    try:
        rate = order._fix_rate_bdt()
    except UserError:  # a report shows what it can; no rate = not converted
        return 0.0
    return round(amount * rate, 2)


def _price_alert_pct(env):
    raw = env["ir.config_parameter"].sudo().get_param(PARAM_PRICE_ALERT)
    try:
        return float(raw) if raw not in (None, False, "") else 10.0
    except (TypeError, ValueError):
        return 10.0


def spend_by_category(env, date_from=None, date_to=None, **params):
    buckets = {}
    for line in _lines(env):
        order = line.order_id
        if not _issued(order) or not _within(_day(order.date_order), date_from, date_to):
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
        row["amount"] += _bdt(order, line.line_total)
    rows = []
    for row in buckets.values():
        row["amount"] = round(row["amount"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["amount"])
    total = sum(r["amount"] for r in rows)
    for row in rows:
        row["share_pct"] = round((row["amount"] / total) * 100.0, 1) if total else 0.0
    return _pack(
        "Spend by Category & Vendor — issued POs, in BDT",
        ["category", "vendor", "lines", "amount", "share_pct"],
        {
            "category": "Category",
            "vendor": "Vendor",
            "lines": "Lines",
            "amount": "Spend (BDT)",
            "share_pct": "Share %",
        },
        rows,
        [
            "Spend is the line total of ISSUED orders (sent onwards; drafts, cancellations and "
            "orders superseded by a change order are excluded), converted to BDT at each "
            "order's stamped rate, by order date (Dhaka) within the period. The AP leg is M52."
        ],
        totals={
            "category": "Total",
            "lines": sum(r["lines"] for r in rows),
            "amount": round(total, 2),
        },
        empty="No issued purchase order lines in the period.",
    )


def _blocked_bills(env, date_from=None, date_to=None):
    """(bills on POs in the period, the blocked ones) — KPI-049's basis."""
    if "fix.vendor.invoice" not in env:
        return None, None
    bills = env["fix.vendor.invoice"].search(
        [*_company_domain(env), ("bill_type", "=", "po"), ("approval_state", "!=", "rejected")]
    )
    bills = bills.filtered(lambda b: _within(b.invoice_date, date_from, date_to))
    return bills, bills.filtered(lambda b: b.match_state in ("blocked", "unmatched"))


def match_exception(env, date_from=None, date_to=None, **params):
    """A06 P26 / KPI-049: a match exception is a vendor bill the three-way
    match blocks, not an order line still awaiting delivery."""
    bills, blocked = _blocked_bills(env, date_from, date_to)
    rows = []
    for bill in blocked or []:
        rows.append(
            {
                "bill": bill.invoice_ref,
                "po": bill.requisition_id.name or "—",
                "vendor": bill.vendor_id.name,
                "detail": bill.match_detail or "",
                "value": round(bill.gross_amount_bdt or 0.0, 2),
                "date": str(bill.invoice_date or ""),
                "state": dict(bill._fields["approval_state"].selection).get(bill.approval_state),
            }
        )
    rows.sort(key=lambda r: -r["value"])
    rate = (len(blocked) / len(bills) * 100.0) if bills else 0.0
    return _pack(
        "Match Exceptions — vendor bills the three-way match blocks",
        ["bill", "po", "vendor", "detail", "value", "date", "state"],
        {
            "bill": "Bill",
            "po": "PO",
            "vendor": "Vendor",
            "detail": "Why",
            "value": "Gross (BDT)",
            "date": "Bill Date",
            "state": "Approval",
        },
        rows,
        [
            "KPI-049 three-way match exception rate: %d of %d PO bills (%.1f%%), target < 5%%."
            % (len(blocked or []), len(bills or []), rate)
        ],
        totals={"bill": "Total", "value": round(sum(r["value"] for r in rows), 2)},
        empty="No vendor bill is blocked by the three-way match.",
    )


def otd_by_vendor(env, date_from=None, date_to=None, **params):
    buckets = {}
    for order in _orders(env):
        due = order._a06_otd_due_date()  # P16: never a buyer-typed vendor date
        if not order.received_on or not due:
            continue
        if not _within(order.received_on, date_from, date_to):
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
            "Orders fully received within the period. The due date is the date the vendor "
            "confirmed in the portal, else the promised date: a date a buyer recorded on the "
            "vendor's behalf does not move the yardstick."
        ],
        totals={
            "vendor": "Total",
            "pos": sum(r["pos"] for r in rows),
            "on_time": sum(r["on_time"] for r in rows),
            "late": sum(r["late"] for r in rows),
        },
        empty="No POs with promised and received dates in the period.",
    )


def price_variance(env, date_from=None, date_to=None, **params):
    band = _price_alert_pct(env)
    history = {}
    for line in _lines(env):
        order = line.order_id
        if not _issued(order) or not (line.qty_ordered or 0.0):
            continue
        day = _day(order.date_order)
        _start, end = _bounds(date_from, date_to)
        if end and day and day > end:
            continue
        key = (line.product_id.display_name, order.vendor_id.name)
        unit_bdt = _bdt(order, line.unit_price)
        history.setdefault(key, []).append(
            (order.date_order or datetime.datetime.min, unit_bdt, day)
        )
    rows = []
    for (product, vendor), entries in history.items():
        entries.sort(key=lambda e: e[0])
        if len(entries) < 2 or not _within(entries[-1][2], date_from, None):
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
                "alert": abs(variance) > band,
            }
        )
    rows.sort(key=lambda r: -abs(r["variance_pct"]))
    return _pack(
        "Price Variance Alert — latest against previous PO price (BDT)",
        ["product", "vendor", "previous_price", "latest_price", "variance_pct", "alert"],
        {
            "product": "Product",
            "vendor": "Vendor",
            "previous_price": "Previous (BDT)",
            "latest_price": "Latest (BDT)",
            "variance_pct": "Variance %",
            "alert": "Alert (>%g%%)" % band,
        },
        rows,
        [
            "Issued orders only, unit prices in BDT at each order's stamped rate; the latest "
            "price falls in the period. The alert band is system parameter %s (default 10%%)."
            % PARAM_PRICE_ALERT
        ],
        empty="No product/vendor pair has two issued prices yet.",
    )


def maverick_spend(env, date_from=None, date_to=None, **params):
    orders = _orders(env).filtered(
        lambda o: _issued(o) and _within(_day(o.date_order), date_from, date_to)
    )
    maverick = orders.filtered(
        lambda o: not o._fix_all_requisitions() or o.requisition_id.state != "converted"
    )
    total = sum(_bdt(o, o.amount_total) for o in orders)
    maverick_total = sum(_bdt(o, o.amount_total) for o in maverick)
    rows = []
    for order in maverick:
        rows.append(
            {
                "po": order.name,
                "vendor": order.vendor_id.name,
                "amount": _bdt(order, order.amount_total),
                "state": dict(order._fields["state"].selection).get(order.state),
                "date": str(_day(order.date_order) or "—"),
                "exception": "documented" if order.no_requisition_exception else "none",
            }
        )
    rows.sort(key=lambda r: -r["amount"])
    return _pack(
        "Maverick Spend — issued POs with no approved requisition behind them",
        ["po", "vendor", "amount", "state", "date", "exception"],
        {
            "po": "PO",
            "vendor": "Vendor",
            "amount": "Amount (BDT)",
            "state": "State",
            "date": "Order Date",
            "exception": "Manager Exception",
        },
        rows,
        [
            "Maverick value BDT %s of BDT %s issued PO spend in the period (%.1f%%)."
            % (
                round(maverick_total, 2),
                round(total, 2),
                (maverick_total / total) * 100.0 if total else 0.0,
            )
        ],
        totals={"po": "Total", "amount": round(maverick_total, 2)},
        empty="Every issued PO traces to a requisition.",
    )


def po_cycle_time(env, date_from=None, date_to=None, **params):
    """A06 P26: the spec's PO cycle time is approved requisition -> placed
    (sent) order, in hours, against the < 24 h target."""
    rows = []
    for order in _orders(env):
        if not order.sent_at or not _within(_day(order.sent_at), date_from, date_to):
            continue
        req = order.requisition_id
        approved_at = req.dofa_approved_at if req else None
        hours = "—"
        if approved_at:
            hours = round((order.sent_at - approved_at).total_seconds() / 3600.0, 1)
        rows.append(
            {
                "po": order.name,
                "vendor": order.vendor_id.name,
                "requisition": req.display_name if req else "—",
                "approved": str(approved_at)[:16] if approved_at else "—",
                "sent": str(order.sent_at)[:16],
                "cycle_hours": hours,
                "on_target": "yes" if hours != "—" and hours <= 24 else "no",
            }
        )
    rows.sort(key=lambda r: str(r["po"]), reverse=True)
    timed = [r["cycle_hours"] for r in rows if r["cycle_hours"] != "—"]
    return _pack(
        "PO Cycle Time — approved requisition to placed order",
        ["po", "vendor", "requisition", "approved", "sent", "cycle_hours", "on_target"],
        {
            "po": "PO",
            "vendor": "Vendor",
            "requisition": "Requisition",
            "approved": "Requisition Approved (UTC)",
            "sent": "PO Sent (UTC)",
            "cycle_hours": "Cycle (hours)",
            "on_target": "< 24 h",
        },
        rows,
        [
            "Orders sent in the period. %d timed, %d within the 24-hour target. An order with "
            "no approved requisition (a documented exception) is not timed."
            % (len(timed), len([h for h in timed if h <= 24]))
        ],
        empty="No purchase orders sent in the period.",
    )


def consolidation(env, date_from=None, date_to=None, **params):
    """FR-PRO-006: the same part asked for by several branches is one sourcing
    event. Approved requisitions not yet converted, by part: those of two or
    more branches are the candidates, and one already out to tender says on
    which RFQ (13 Nov 2026: this grouped every requisition by branch and
    urgency, which is the opposite of consolidating across branches)."""
    reqs = env["fix.requisition"].search(
        [*_company_domain(env), ("state", "=", "approved"), ("purchase_order_id", "=", False)]
    )
    rfqs = (
        env["fix.procurement.rfq"]
        .sudo()
        .search(
            [
                ("state", "in", ("draft", "open", "closed")),
                "|",
                ("requisition_ids", "in", reqs.ids),
                ("requisition_id", "in", reqs.ids),
            ]
        )
    )
    tender = {}
    for rfq in rfqs:
        for req in rfq.requisition_id | rfq.requisition_ids:
            tender[req.id] = rfq.name
    buckets = {}
    for req in reqs:
        key = req.product_id.id or 0
        row = buckets.setdefault(
            key,
            {
                "product": req.product_id.display_name or "No product (free text)",
                "branches": set(),
                "requests": 0,
                "qty": 0.0,
                "amount": 0.0,
                "required_by": None,
                "rfqs": set(),
            },
        )
        row["branches"].add(req.branch_id.name or "No branch")
        row["requests"] += 1
        row["qty"] += req.qty or 0.0
        row["amount"] += req.estimate_amount or 0.0
        if req.required_by and (not row["required_by"] or req.required_by < row["required_by"]):
            row["required_by"] = req.required_by
        if req.id in tender:
            row["rfqs"].add(tender[req.id])
    rows = []
    for row in buckets.values():
        count = len(row["branches"])
        rows.append(
            {
                "product": row["product"],
                "branches": ", ".join(sorted(row["branches"])),
                "branch_count": count,
                "requests": row["requests"],
                "qty": round(row["qty"], 3),
                "amount": round(row["amount"], 2),
                "required_by": (row["required_by"] and str(row["required_by"])) or "",
                "status": (
                    "Out to tender: " + ", ".join(sorted(row["rfqs"]))
                    if row["rfqs"]
                    else ("Consolidate" if count > 1 else "Single branch")
                ),
            }
        )
    rows.sort(key=lambda r: (-r["branch_count"], -r["amount"]))
    return _pack(
        "Cross-Branch Consolidation — approved requisitions by part",
        [
            "product",
            "branches",
            "branch_count",
            "requests",
            "qty",
            "amount",
            "required_by",
            "status",
        ],
        {
            "product": "Part",
            "branches": "Requesting Branches",
            "branch_count": "Branches",
            "requests": "Requisitions",
            "qty": "Total Quantity",
            "amount": "Estimated Amount",
            "required_by": "Earliest Required By",
            "status": "Sourcing",
        },
        rows,
        [
            "Only approved requisitions that are not yet on a purchase order are counted.",
            "A part asked for by two or more branches can be bought in one event: use "
            "Consolidate Requisitions into an RFQ on this page. The award then raises one "
            "purchase order with a line for each branch.",
        ],
        totals={
            "product": "Total",
            "requests": sum(r["requests"] for r in rows),
            "amount": round(sum(r["amount"] for r in rows), 2),
        },
        empty="No approved requisition is waiting to be bought.",
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


def gr_ir(env, date_from=None, date_to=None, **params):
    """A06 X26 / P13: goods received not invoiced AS AT the period end, on the
    one basis the AP GRNI accrual uses and the GRNI account holds: accepted
    receipts at their receipt value in BDT, less returns and less what posted
    bills billed (net of their return credit notes)."""
    as_of = _bounds(None, date_to)[1] or _today()
    if "fix.ap.grni.accrual" not in env:
        return _pack(
            "GR/IR Reconciliation",
            [],
            {},
            [],
            ["The AP sub-ledger (cd_ap_ext) is not installed: there is no GRNI basis."],
            empty="No GRNI basis.",
        )
    from odoo.addons.cd_ap_ext.models.fix_ap_grni import grir_po_summary_as_of, grni_rows_as_of

    allowed = set(env.companies.ids)
    buckets = {}
    for r in grni_rows_as_of(env, as_of):
        pol = r["po_line"]
        company = pol.order_id.company_id if pol else None
        if company and company.id not in allowed:
            continue
        key = r["order_ref"]
        row = buckets.setdefault(
            key,
            {
                "po": key,
                "vendor": r["vendor"].name or "",
                "received_qty": 0.0,
                "invoiced_qty": 0.0,
                "open_qty": 0.0,
                "received_not_invoiced": 0.0,
                "received_value": 0.0,
                "invoiced_value": 0.0,
                "invoiced_not_received": 0.0,
                "oldest_days": None,
            },
        )
        row["received_qty"] += r["received"]
        row["invoiced_qty"] += r["invoiced"]
        row["open_qty"] += r["open_qty"]
        row["received_not_invoiced"] += r["accrual"]
        if r["age_days"] is not None:
            row["oldest_days"] = max(row["oldest_days"] or 0, r["age_days"])
    # the other direction on the same posted basis: billed ahead of receipt
    for po, vals in grir_po_summary_as_of(env, as_of).items():
        if po.company_id.id not in allowed:
            continue
        row = buckets.setdefault(
            po.name,
            {
                "po": po.name,
                "vendor": vals["vendor"].name or "",
                "received_qty": 0.0,
                "invoiced_qty": 0.0,
                "open_qty": 0.0,
                "received_not_invoiced": 0.0,
                "received_value": 0.0,
                "invoiced_value": 0.0,
                "invoiced_not_received": 0.0,
                "oldest_days": None,
            },
        )
        for k in ("received_value", "invoiced_value", "invoiced_not_received"):
            row[k] = vals[k]
    rows = []
    for row in buckets.values():
        for k in ("received_qty", "invoiced_qty", "open_qty"):
            row[k] = round(row[k], 3)
        for k in (
            "received_not_invoiced",
            "received_value",
            "invoiced_value",
            "invoiced_not_received",
        ):
            row[k] = round(row[k], 2)
        if not row["received_not_invoiced"] and not row["invoiced_not_received"]:
            continue  # received and billed alike: nothing to reconcile
        row["oldest_days"] = "" if row["oldest_days"] is None else row["oldest_days"]
        rows.append(row)
    rows.sort(key=lambda r: -(r["received_not_invoiced"] + r["invoiced_not_received"]))
    return _pack(
        "GR/IR Reconciliation — received not invoiced as at %s (BDT)" % as_of,
        [
            "po",
            "vendor",
            "received_qty",
            "invoiced_qty",
            "open_qty",
            "received_value",
            "invoiced_value",
            "received_not_invoiced",
            "invoiced_not_received",
            "oldest_days",
        ],
        {
            "po": "PO / Import",
            "vendor": "Vendor",
            "received_qty": "Accepted",
            "invoiced_qty": "Billed / Returned",
            "open_qty": "Open Qty",
            "received_value": "Received Value (BDT)",
            "invoiced_value": "Invoiced Value (BDT)",
            "received_not_invoiced": "Received, Not Invoiced (BDT)",
            "invoiced_not_received": "Invoiced, Not Received (BDT)",
            "oldest_days": "Oldest (days)",
        },
        rows,
        [
            "As at the period end: accepted quantity of receipts posted by then (inspection "
            "rejections excluded), less returns shipped by then and quantity billed on bills "
            "posted by then net of return credit notes, at the receipt value in BDT (the M15 "
            "receipt cost, else the approved price at the order's stamped rate). The same basis "
            "as the AP GRNI accrual; the total ties to the GRNI account (100503).",
            "Invoiced, not received: per product, what posted bills billed beyond the accepted "
            "quantity, at the bill's BDT price (a product received never nets another billed).",
        ],
        totals={
            "po": "Total",
            "received_not_invoiced": round(sum(r["received_not_invoiced"] for r in rows), 2),
            "invoiced_not_received": round(sum(r["invoiced_not_received"] for r in rows), 2),
        },
        empty="Nothing received and not invoiced, or invoiced and not received, at the period end.",
    )


def emergency_spend(env, date_from=None, date_to=None, **params):
    """BRU-PRO-12 / FR-PRO-036: an emergency purchase is counted."""
    reqs = env["fix.requisition"].search(
        [*_company_domain(env), ("emergency_state", "!=", False)],
        order="emergency_released_at desc",
    )
    reqs = reqs.filtered(lambda r: _within(_day(r.emergency_released_at), date_from, date_to))
    spend = sum(
        _bdt(o, o.amount_total)
        for o in _orders(env)
        if _issued(o) and _within(_day(o.date_order), date_from, date_to)
    )

    def req_bdt(req):
        try:
            return req._dofa_amount() - (req.split_prior_amount or 0.0)
        except UserError:  # no rate: not converted
            return 0.0

    total = sum(req_bdt(r) for r in reqs)
    rows = [
        {
            "requisition": req.description,
            "branch": req.branch_id.name if req.branch_id else "—",
            "amount": round(req_bdt(req), 2),
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
            "amount": "Amount (BDT)",
            "reason": "Reason",
            "released": "Released",
            "due": "Post-Hoc Due",
            "path": "Status",
        },
        rows,
        [
            "Emergency value BDT %s against BDT %s issued PO spend in the period (%.1f%%); the "
            "module's target is under 8%% of spend."
            % (round(total, 2), round(spend, 2), (total / spend) * 100.0 if spend else 0.0)
        ],
        totals={"requisition": "Total", "amount": round(total, 2)},
        empty="No emergency purchases in the period.",
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
    today = _today()
    month_start = today.replace(day=1)
    # A06 X31: issued orders only, in BDT, by the Dhaka order day
    spend_mtd = sum(
        _bdt(order, order.amount_total)
        for order in orders
        if _issued(order) and (_day(order.date_order) or today) >= month_start
    )
    received = orders.filtered(lambda o: o.received_on and o._a06_otd_due_date())
    on_time = received.filtered(lambda o: o.received_on <= o._a06_otd_due_date())
    # A06 P26: KPI-049 counts bills the match blocks, not undelivered order lines
    _bills, blocked = _blocked_bills(env)
    return {
        "open_requisitions": len(reqs.filtered(lambda r: r.state in _OPEN_REQ)),
        "rfq_open": len(rfqs.filtered(lambda r: r.state == "open")),
        "po_open": len(orders.filtered(lambda o: o.state in _OPEN_PO)),
        "match_exceptions": len(blocked or []),
        "spend_mtd": round(spend_mtd, 2),
        "otd_pct": round((len(on_time) / len(received)) * 100.0, 1) if received else 0.0,
    }
