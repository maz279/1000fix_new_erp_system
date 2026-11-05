# A04 · M38 E-Commerce Storefront — surfaces, report packs and KPIs over the
# real fix.storefront.cart (88) / .cart.line / fix.storefront.order (1) and the
# new RMA and slot models. Payment mix and delivery come from the storefront
# order's own fields; refund GMV by grade is a declared gap (no grade link).
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

# A04 workflow audit (2026-11-04) C3/D2: every M38 surface declared
# `actions: set()`, so the workspace could only edit the state. The lifecycle
# now runs from these actions; the server checks the role, the state, the
# proof (gateway or M20 receipt, consignment POD, M20 credit note) and the
# segregation of duties for each. The refund itself is approved from the M63
# inbox (Request Refund Approval), never by pressing Approve here.
_REFUND_ACTIONS = {
    "action_approve",
    "action_receive_and_inspect",
    "action_request_approval",
    "action_recall_approval",
    "action_reject",
    "action_record_credit_note",
}

SURFACES = {
    "fix.storefront.cart": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.storefront.order": {
        "order": "order_date desc, id desc",
        "limit": 300,
        "actions": {
            "action_confirm_payment",
            "action_dispatch",
            "action_deliver",
            "action_cancel",
        },
    },
    "fix.storefront.rma": {
        "order": "requested_on desc, id desc",
        "limit": 300,
        "actions": set(_REFUND_ACTIONS),
    },
    "fix.storefront.slot": {
        "order": "slot_date, start_hour",
        "limit": 300,
        "actions": {"action_close", "action_reopen"},
    },
    # fix.graded.stock is mastered by M15 (cd_inventory); its lifecycle and
    # guard are M15's. The storefront reserves and sells it from the order.
    "fix.graded.stock": {
        "order": "id desc",
        "limit": 300,
        "actions": set(),
    },
    # fix.promotion is owned by M11 (a04) — read through the merged registry.
    "fix.storefront.return": {
        "order": "id desc",
        "limit": 400,
        "actions": set(_REFUND_ACTIONS),
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
        "empty": empty or "No data in this basis yet.",
    }


def _orders(env):
    return env["fix.storefront.order"].sudo().search([])


def _carts(env):
    return env["fix.storefront.cart"].sudo().search([])


def funnel_conversion(env, date_from=None, date_to=None, **params):
    carts = _carts(env)
    orders = _orders(env)
    states = ["open", "checkout", "ordered"]
    rows = []
    for state in states:
        mine = carts.filtered(lambda c, s=state: c.state == s)
        rows.append(
            {"stage": state, "carts": len(mine), "value": round(sum(mine.mapped("total")), 2)}
        )
    converted = len(orders)
    total = len(carts)
    return _pack(
        "Funnel & Conversion",
        ["stage", "carts", "value"],
        {"stage": "Funnel Stage", "carts": "Carts", "value": "Cart Value"},
        rows,
        [
            "Storefront orders: %d. Cart→order conversion: %d of %d carts (%.1f%%)."
            % (converted, converted, total, converted / total * 100.0 if total else 0.0)
        ],
        totals={"stage": "Total", "carts": total, "value": round(sum(carts.mapped("total")), 2)}
        if rows
        else None,
        empty="No carts yet.",
    )


def merchandising(env, date_from=None, date_to=None, **params):
    orders = _orders(env)
    by_rail = {}
    for order in orders:
        key = order.payment_rail or "unspecified"
        row = by_rail.setdefault(key, {"rail": key, "orders": 0, "value": 0.0})
        row["orders"] += 1
        row["value"] += order.total_amount or 0.0
    rows = []
    for row in by_rail.values():
        row["value"] = round(row["value"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Merchandising — orders by payment rail",
        ["rail", "orders", "value"],
        {"rail": "Payment Rail", "orders": "Orders", "value": "GMV"},
        rows,
        ["Order volume/value by the storefront's recorded payment rail."],
        totals={
            "rail": "Total",
            "orders": len(orders),
            "value": round(sum(orders.mapped("total_amount")), 2),
        }
        if rows
        else None,
        empty="No storefront orders yet.",
    )


def stock_availability(env, date_from=None, date_to=None, **params):
    stock = env["fix.graded.stock"].sudo().search([])
    rows = []
    for item in stock:
        rows.append(
            {
                "device": item.device_id.display_name or "—",
                "grade": item.grade_id.name or "—",
                "cost": round(item.acquisition_cost or 0.0, 2),
                "state": item.state,
            }
        )
    return _pack(
        "Compatibility & Refurb Stock",
        ["device", "grade", "cost", "state"],
        {"device": "Device", "grade": "Refurb Grade", "cost": "Acquisition Cost", "state": "State"},
        rows,
        [
            "Only graded refurb stock is listed: grade, acquisition cost and state. "
            "A compatibility matrix against new devices is not modelled (declared gap)."
        ],
        empty="No graded refurb stock yet.",
    )


def checkout_conversion(env, date_from=None, date_to=None, **params):
    carts = _carts(env)
    open_carts = carts.filtered(lambda c: c.state == "open")
    checkout = carts.filtered(lambda c: c.state == "checkout")
    ordered = carts.filtered(lambda c: c.state == "ordered")
    rows = [
        {"metric": "Carts open", "value": len(open_carts), "basis": "state=open"},
        {"metric": "In checkout", "value": len(checkout), "basis": "state=checkout"},
        {"metric": "Ordered", "value": len(ordered), "basis": "state=ordered"},
        {
            "metric": "Open cart value",
            "value": round(sum(open_carts.mapped("total")), 2),
            "basis": "total of open carts",
        },
        {
            "metric": "Checkout abandonment",
            "value": round(len(open_carts) / len(carts) * 100.0, 1) if carts else 0.0,
            "basis": "% carts still open",
        },
    ]
    return _pack(
        "Checkout Conversion",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "The checkout funnel is the cart state machine — no session analytics "
            "model exists beyond it."
        ],
    )


def delivery_performance(env, date_from=None, date_to=None, **params):
    slots = env["fix.storefront.slot"].sudo().search([])
    orders = _orders(env)
    rows = []
    for slot in slots:
        rows.append(
            {
                "slot": slot.name,
                "type": slot.slot_type,
                "date": str(slot.slot_date),
                "window": "%02d:00–%02d:00" % (slot.start_hour, slot.end_hour),
                "booked": slot.booked,
                "capacity": slot.capacity,
                "fill_pct": round(slot.booked / slot.capacity * 100.0, 1) if slot.capacity else 0.0,
                "state": slot.state,
            }
        )
    by_shipping = {}
    for order in orders:
        key = order.shipping_method or "unspecified"
        by_shipping[key] = by_shipping.get(key, 0) + 1
    notes = [
        "Slots are the booked capacity window per day.",
        "Orders by shipping method: %s."
        % (", ".join("%s=%d" % kv for kv in sorted(by_shipping.items())) or "none"),
    ]
    return _pack(
        "Delivery Performance",
        ["slot", "type", "date", "window", "booked", "capacity", "fill_pct", "state"],
        {
            "slot": "Slot",
            "type": "Type",
            "date": "Date",
            "window": "Window",
            "booked": "Booked",
            "capacity": "Capacity",
            "fill_pct": "Fill %",
            "state": "State",
        },
        rows,
        notes,
        empty="No delivery or storefront slots configured yet.",
    )


def rma_report(env, date_from=None, date_to=None, **params):
    rmas = env["fix.storefront.rma"].sudo().search([])
    rows = []
    for rma in rmas:
        rows.append(
            {
                "rma": rma.name,
                "customer": rma.customer_id.name or "—",
                "reason": rma.reason,
                "amount": round(rma.refund_amount or 0.0, 2),
                "state": rma.state,
            }
        )
    refunded = sum(r["amount"] for r in rows if r["state"] == "refunded")
    return _pack(
        "RMA & Returns Report",
        ["rma", "customer", "reason", "amount", "state"],
        {
            "rma": "RMA",
            "customer": "Customer",
            "reason": "Reason",
            "amount": "Refund Amount",
            "state": "State",
        },
        rows,
        ["Refunded value: %s. Reasons are the recorded RMA codes." % round(refunded, 2)],
        totals={"rma": "Total", "amount": round(sum(r["amount"] for r in rows), 2)}
        if rows
        else None,
        empty="No RMA requests yet.",
    )


def abandonment_recovery(env, date_from=None, date_to=None, **params):
    carts = _carts(env)
    today = datetime.date.today()
    open_carts = carts.filtered(lambda c: c.state in ("open", "checkout"))
    rows = []
    for cart in open_carts:
        age = (today - cart.create_date.date()).days if cart.create_date else 0
        rows.append(
            {
                "cart": cart.name or "cart-%s" % cart.id,
                "customer": cart.customer_id.name or "—",
                "state": cart.state,
                "value": round(cart.total or 0.0, 2),
                "age_days": age,
                "recovered": "✓" if cart.order_id else "✗",
            }
        )
    rows.sort(key=lambda r: -r["age_days"])
    recovered = len([r for r in rows if r["recovered"] == "✓"])
    return _pack(
        "Abandonment Recovery Rate",
        ["cart", "customer", "state", "value", "age_days", "recovered"],
        {
            "cart": "Cart",
            "customer": "Customer",
            "state": "State",
            "value": "Value",
            "age_days": "Age (days)",
            "recovered": "Recovered",
        },
        rows[:200],
        [
            "Recovery = a cart that produced an order. Recovery rate: %d of %d open "
            "carts (%.1f%%). No recovery-campaign model exists (declared gap)."
            % (recovered, len(rows), recovered / len(rows) * 100.0 if rows else 0.0)
        ],
        empty="No open carts — nothing to recover.",
    )


def payment_method_mix(env, date_from=None, date_to=None, **params):
    orders = _orders(env)
    by_rail = {}
    for order in orders:
        key = order.payment_rail or "unspecified"
        row = by_rail.setdefault(key, {"rail": key, "orders": 0, "value": 0.0})
        row["orders"] += 1
        row["value"] += order.total_amount or 0.0
    total = sum(r["value"] for r in by_rail.values())
    rows = []
    for row in by_rail.values():
        row["value"] = round(row["value"], 2)
        row["share_pct"] = round(row["value"] / total * 100.0, 1) if total else 0.0
        rows.append(row)
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Payment Method Mix",
        ["rail", "orders", "value", "share_pct"],
        {"rail": "Payment Rail", "orders": "Orders", "value": "GMV", "share_pct": "Share %"},
        rows,
        ["Mix is measured from the storefront order's recorded payment rail."],
        totals={
            "rail": "Total",
            "orders": len(orders),
            "value": round(total, 2),
            "share_pct": 100.0,
        }
        if rows
        else None,
        empty="No storefront orders yet.",
    )


def _refurb_lines(env, since=None):
    """Order lines that sold a graded refurb item, on orders not cancelled.
    A04 audit (2026-11-04) P2: order lines now carry the graded stock they
    sold, so refurb GMV is measured instead of declared a gap."""
    lines = (
        env["fix.storefront.order.line"]
        .sudo()
        .search([("graded_stock_id", "!=", False), ("order_id.state", "!=", "cancelled")])
    )
    if since:
        lines = lines.filtered(
            lambda ln: ln.order_id.order_date and ln.order_id.order_date.date() >= since
        )
    return lines


def refurb_gmv(env, date_from=None, date_to=None, **params):
    rows = {}
    for line in _refurb_lines(env):
        grade = line.graded_stock_id.grade_id.display_name or "Ungraded"
        row = rows.setdefault(grade, {"grade": grade, "orders": set(), "gmv": 0.0})
        row["orders"].add(line.order_id.id)
        row["gmv"] += line.subtotal or 0.0
    out = [
        {"grade": r["grade"], "orders": len(r["orders"]), "gmv": round(r["gmv"], 2)}
        for r in sorted(rows.values(), key=lambda r: r["grade"])
    ]
    return _pack(
        "Refurb GMV by Grade",
        ["grade", "orders", "gmv"],
        {"grade": "Refurb Grade", "orders": "Orders", "gmv": "GMV"},
        out,
        [
            "Order lines that sold a graded refurb item (M15 graded stock), on orders "
            "not cancelled, valued at the line subtotal."
        ],
        totals={
            "grade": "Total",
            "orders": sum(r["orders"] for r in out),
            "gmv": round(sum(r["gmv"] for r in out), 2),
        }
        if out
        else None,
        empty="No graded refurb item has been sold through the storefront yet.",
    )


REPORTS = {
    "funnel_conversion": funnel_conversion,
    "merchandising": merchandising,
    "stock_availability": stock_availability,
    "checkout_conversion": checkout_conversion,
    "delivery_performance": delivery_performance,
    "rma_report": rma_report,
    "abandonment_recovery": abandonment_recovery,
    "payment_method_mix": payment_method_mix,
    "refurb_gmv": refurb_gmv,
}


def kpis(env):
    carts = _carts(env)
    orders = _orders(env)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    open_carts = carts.filtered(lambda c: c.state in ("open", "checkout"))
    ordered = len(orders)
    total = len(carts)
    orders_mtd = len(orders.filtered(lambda o: o.order_date and o.order_date.date() >= month_start))
    bkash = len(orders.filtered(lambda o: o.payment_rail == "bkash"))
    rmas = env["fix.storefront.rma"].sudo().search([])
    return {
        "orders_mtd": orders_mtd,
        "conversion": round(ordered / total * 100.0, 1) if total else None,
        "cart_abandon": round(len(open_carts) / total * 100.0, 1) if total else None,
        "bkash_share": round(bkash / ordered * 100.0, 1) if ordered else None,
        "refurb_gmv_mtd": round(sum(_refurb_lines(env, since=month_start).mapped("subtotal")), 2),
        "rma_rate": round(len(rmas) / ordered * 100.0, 1) if ordered else None,
        # measured extras
        "carts_open": len(open_carts),
        "orders": ordered,
        "gmv": round(sum(orders.mapped("total_amount")), 2),
        "abandoned_value": round(sum(open_carts.mapped("total")), 2),
        "rma_open": len(
            rmas.filtered(
                lambda r: r.state in ("requested", "approved", "received", "refund_approved")
            )
        ),
    }


class P03StorefrontApi(http.Controller):
    @http.route("/p03/storefront/kpis", type="jsonrpc", auth="user", readonly=True)
    def storefront_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M38": kpis(request.env)}
