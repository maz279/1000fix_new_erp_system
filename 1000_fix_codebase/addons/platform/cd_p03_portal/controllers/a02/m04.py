# A02 · M04 Branch & Front-Desk — models the generic workspace screens may
# read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/branch/kpis) and the
# built-in reports (/p03/model/report). Same contract as a02/m01..m03.
import datetime
import logging

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    # NOTE: fix.token.queue and fix.walkin.intake are OWNED by m01.py's
    # SURFACES (declared there for the M01 hotline/intake screens). The
    # a02 merge refuses duplicates, so the M04 queue/intake actions live on
    # the m01 entries — this file declares only the M04-native models.
    "fix.cash.shift": {
        "order": "id desc",
        "limit": 100,
        # A02 audit M04-2/-11: the blind count and the manager's variance
        # approval are workspace buttons; the methods check role and SoD.
        "actions": {
            "action_close_shift",
            "action_submit_blind_count",
            "action_confirm_closed",
            "action_approve_variance",
            "action_reconcile",
        },
    },
    "fix.counter.sale": {
        "order": "id desc",
        "limit": 200,
        # A02 audit M04-5: a refund is requested with a reason and approved by
        # someone who did not sell; a price below list is approved first.
        "actions": {
            "action_confirm",
            "action_approve_price_override",
            "action_request_refund",
            "action_approve_refund",
        },
    },
}

# tokens actually served vs issued today
_QUEUE_DONE = ("completed", "cancelled", "no_show")


def kpis(env):
    """The M04 module-tile KPI row (registry-canonical metrics)."""
    Token = env["fix.token.queue"].sudo()
    Shift = env["fix.cash.shift"].sudo()
    Sale = env["fix.counter.sale"].sudo()
    Order = env["fix.service.order"].sudo()
    domain = [("company_id", "in", env.companies.ids)]
    today = datetime.date.today()

    tokens_today = Token.search_count(
        [*domain, ("issued_at", ">=", today.strftime("%Y-%m-%d 00:00:00"))]
    )

    served = Token.search(
        [*domain, ("state", "=", "completed"), ("served_at", "!=", False)], limit=200
    )
    waits_min = [
        (t.served_at - t.called_at).total_seconds() / 60.0
        for t in served
        if t.called_at and t.served_at
    ]
    avg_wait = round(sum(waits_min) / len(waits_min), 1) if waits_min else None

    uncollected = Order.search_count(
        [
            *domain,
            ("state", "in", ("ready", "delivered")),
            ("write_date", "<=", (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")),
        ]
    )

    shifts_today = Shift.search([*domain, ("shift_date", "=", today)], limit=50)
    variances = [
        s.variance for s in shifts_today if s.state in ("reconciled", "discrepancy") and s.variance
    ]
    cash_variance = round(sum(variances), 2) if variances else 0.0

    shifts_open = Shift.search_count([*domain, ("state", "in", ("open", "counting", "closed"))])

    month_start = today.replace(day=1)
    sales_mtd = Sale.search_count([*domain, ("sale_date", ">=", month_start.strftime("%Y-%m-%d"))])

    return {
        "tokens_today": tokens_today,
        "avg_wait_min": avg_wait,
        "uncollected_7d": uncollected,
        "cash_variance_today": cash_variance,
        "shifts_open": shifts_open,
        "counter_sales_mtd": sales_mtd,
    }


# ---------------------------------------------------------------- reports


def _daily_cash_report(env, **params):
    Shift = env["fix.cash.shift"].sudo()
    rows = []
    shifts = Shift.search(
        [("state", "in", ("reconciled", "discrepancy"))], order="shift_date desc", limit=100
    )
    for s in shifts:
        rows.append(
            {
                "date": str(s.shift_date),
                "branch": s.branch_id.name or "—",
                "operator": s.operator_id.name or "—",
                "opening": s.opening_float,
                "counted": s.closing_counted,
                "variance": s.variance,
                "state": s.state,
            }
        )
    return {
        "title": "Branch Daily Cash Summary",
        "cols": ["date", "branch", "operator", "opening", "counted", "variance", "state"],
        "labels": {
            "date": "Date",
            "branch": "Branch",
            "operator": "Operator",
            "opening": "Opening Float",
            "counted": "Counted",
            "variance": "Variance",
            "state": "State",
        },
        "rows": rows,
        "notes": ["Closed/reconciled shifts with their counted drawers and variances, live."],
    }


def _wait_distribution_report(env, **params):
    Token = env["fix.token.queue"].sudo()
    served = Token.search([("state", "=", "completed"), ("served_at", "!=", False)], limit=300)
    buckets = {"< 5 min": 0, "5–15 min": 0, "15–30 min": 0, "> 30 min": 0}
    for t in served:
        if not (t.called_at and t.served_at):
            continue
        m = (t.served_at - t.called_at).total_seconds() / 60.0
        if m < 5:
            buckets["< 5 min"] += 1
        elif m <= 15:
            buckets["5–15 min"] += 1
        elif m <= 30:
            buckets["15–30 min"] += 1
        else:
            buckets["> 30 min"] += 1
    return {
        "title": "Token Wait-Time Distribution",
        "cols": ["bucket", "tokens"],
        "labels": {"bucket": "Wait", "tokens": "Tokens"},
        "rows": [{"bucket": k, "tokens": v} for k, v in buckets.items()],
        "notes": ["Call → serve duration on completed tokens."],
    }


def _uncollected_ageing_report(env, **params):
    Order = env["fix.service.order"].sudo()
    today = datetime.date.today()
    rows = []
    for o in Order.search(
        [("state", "in", ("ready", "delivered"))], order="write_date asc", limit=200
    ):
        since = o.write_date.date() if o.write_date else today
        rows.append(
            {
                "order": o.name,
                "customer": o.customer_id.name or "—",
                "branch": o.branch_id.name or "—",
                "state": o.state,
                "days": (today - since).days,
            }
        )
    rows.sort(key=lambda r: -r["days"])
    return {
        "title": "Uncollected Device Ageing",
        "cols": ["order", "customer", "branch", "state", "days"],
        "labels": {
            "order": "Order",
            "customer": "Customer",
            "branch": "Branch",
            "state": "State",
            "days": "Days Waiting",
        },
        "rows": rows,
        "notes": ["Repaired devices at branch awaiting collection, oldest first."],
    }


def _sales_category_report(env, **params):
    Sale = env["fix.counter.sale"].sudo()
    rows = []
    sales = Sale.search([], limit=300)
    by_product = {}
    for s in sales:
        key = s.product_id.display_name or "—"
        by_product.setdefault(key, {"count": 0, "total": 0.0})
        by_product[key]["count"] += 1
        by_product[key]["total"] += s.total
    for product, agg in sorted(by_product.items(), key=lambda kv: -kv[1]["total"]):
        rows.append({"product": product, "count": agg["count"], "total": agg["total"]})
    return {
        "title": "Counter Sales by Category",
        "cols": ["product", "count", "total"],
        "labels": {"product": "Product", "count": "Sales", "total": "Total (BDT)"},
        "rows": rows,
        "notes": ["Counter sales grouped by product, live."],
    }


def _variance_register_report(env, **params):
    Shift = env["fix.cash.shift"].sudo()
    rows = [
        {
            "date": str(s.shift_date),
            "branch": s.branch_id.name or "—",
            "variance": s.variance,
            "state": s.state,
            "notes": (s.reconciliation_notes or "")[:60],
        }
        for s in Shift.search([("variance", "!=", 0.0)], order="shift_date desc", limit=100)
    ]
    return {
        "title": "Shift Variance Register",
        "cols": ["date", "branch", "variance", "state", "notes"],
        "labels": {
            "date": "Date",
            "branch": "Branch",
            "variance": "Variance",
            "state": "State",
            "notes": "Notes",
        },
        "rows": rows,
        "notes": ["Every non-zero variance, live — the discrepancy trail."],
    }


def _branch_league_report(env, **params):
    env_all = env
    Order = env_all["fix.service.order"].sudo()
    rows = []
    branches = env_all["fix.branch"].sudo().search([])
    for b in branches:
        open_n = Order.search_count(
            [("branch_id", "=", b.id), ("state", "not in", ("closed", "cancelled"))]
        )
        ready_n = Order.search_count([("branch_id", "=", b.id), ("state", "=", "ready")])
        if open_n or ready_n:
            rows.append({"branch": b.name, "open_orders": open_n, "ready": ready_n})
    rows.sort(key=lambda r: -r["open_orders"])
    return {
        "title": "Branch Comparison League",
        "cols": ["branch", "open_orders", "ready"],
        "labels": {
            "branch": "Branch",
            "open_orders": "Open Orders",
            "ready": "Ready for Collection",
        },
        "rows": rows[:30],
        "notes": ["Branch workload comparison from the live order book."],
    }


REPORTS = {
    "daily_cash": _daily_cash_report,
    "wait_distribution": _wait_distribution_report,
    "uncollected_ageing": _uncollected_ageing_report,
    "sales_category": _sales_category_report,
    "variance_register": _variance_register_report,
    "branch_league": _branch_league_report,
}


class P03M04Controller(http.Controller):
    @http.route("/p03/branch/kpis", type="jsonrpc", auth="user", readonly=True)
    def branch_kpis(self, **kw):
        _require_internal(request.env)
        try:
            return {"M04": kpis(request.env)}
        except Exception:
            _logger.exception("p03 branch_kpis failed")
            return {"error": "KPI computation failed"}
