# A02 · M04 Branch & Front-Desk — models the generic workspace screens may
# read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/branch/kpis) and the
# built-in reports (/p03/model/report). Same contract as a02/m01..m03.
import datetime
import logging

import pytz
from odoo import fields, http
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
        # A02 audit M04-2/-11: the blind count is a workspace button; the
        # methods check role and SoD. A02 audit B1: the variance is approved
        # from the M63 inbox, so the workspace requests (or recalls) it.
        "actions": {
            "action_close_shift",
            "action_submit_blind_count",
            "action_confirm_closed",
            "action_request_approval",
            "action_recall_approval",
            "action_reconcile",
        },
    },
    "fix.counter.sale": {
        "order": "id desc",
        "limit": 200,
        # A02 audit M04-5: a refund is requested with a reason and approved by
        # someone who did not sell; a price below list is approved first.
        # A02 audit B1: both approvals are decided in the M63 inbox; the
        # refund request routes itself, the price approval is requested.
        "actions": {
            "action_confirm",
            "action_request_approval",
            "action_recall_approval",
            "action_request_refund",
            # BRU-FRD-10: a protection plan / membership's terms (A02 ERP audit)
            "action_accept_terms",
            # A02 ERP audit X-17: the customer's receipt, A4 and 80 mm
            "action_print_receipt",
            "action_print_receipt_80",
        },
    },
    # Quote-to-cash (13 Nov 2026): a customer's several items, one payment.
    # Confirming raises one counter sale per item through the sale's own
    # confirm (cd_front_desk_finance fix.counter.basket).
    "fix.counter.basket": {"order": "id desc", "limit": 200, "actions": {"action_confirm"}},
    # M04 sub-module audit (13 Nov 2026): the opening / closing checklist
    # (FR-FRD-020/024) is recorded, not derived from the cash shifts.
    "fix.branch.checklist": {
        "order": "checklist_date desc, id desc",
        "limit": 100,
        "actions": {"action_complete"},
    },
    # M04 build (13 Nov 2026): counters and priority rules (FR-FRD-007/027,
    # BRU-FRD-07), storage locations (FR-FRD-011), the drawer movement ledger
    # (FR-FRD-015, BRU-FRD-09) and branch announcements (FR-FRD-031).
    # A02 ERP audit M04-F12: a counter calls its next customer by priority lane
    "fix.queue.counter": {
        "order": "branch_id, number",
        "limit": 300,
        "actions": {"action_call_next"},
    },
    "fix.queue.priority.rule": {"order": "sequence, id", "limit": 200, "actions": set()},
    "fix.storage.location": {"order": "branch_id, code", "limit": 500, "actions": set()},
    "fix.cash.movement": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_approve", "action_post", "action_cancel"},
    },
    "fix.branch.announcement": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_publish", "action_withdraw", "action_acknowledge"},
    },
    # M04 capture audit (18 Nov 2026): the shift handover the incoming team
    # acknowledges (FR-FRD-022) and the NID + consent behind a high-value
    # cash receipt (FR-FRD-019, cd_front_desk_finance). A check is evidence:
    # it has no action and is never edited.
    "fix.shift.handover": {"order": "id desc", "limit": 200, "actions": {"action_acknowledge"}},
    "fix.cash.id.check": {"order": "id desc", "limit": 200, "actions": set()},
}

# ---------------------------------------------------------------- frame
#
# A02 ERP audit M04-F17 / X-13 / X-14: every figure below was a sudo read with
# no company fence, the packs ignored the screen's period, "today" was the
# server's date against UTC stamps, the shift variance netted shortages
# against overages, the average wait measured call -> serve (the time at the
# counter, not the wait), "uncollected" counted delivered orders and aged them
# from their last write, open shifts counted closed ones, and counter sales
# counted drafts and refunds.

LOCAL_TZ = "Asia/Dhaka"
# a ready device not collected after this many days is "uncollected"
UNCOLLECTED_DAYS = 7
# what a counted drawer's variance is: a count exists
_COUNTED = [("blind_count_submitted", "=", True)]


def _tz(env):
    return pytz.timezone(env.context.get("tz") or env.user.tz or LOCAL_TZ)


def _today(env):
    """The reader's business day (Asia/Dhaka when no zone is set)."""
    return datetime.datetime.now(pytz.utc).astimezone(_tz(env)).date()


def _utc_start(env, day):
    """Naive-UTC instant of local midnight starting ``day``."""
    local = _tz(env).localize(datetime.datetime.combine(day, datetime.time.min))
    return local.astimezone(pytz.utc).replace(tzinfo=None)


def _local_day(env, stamp):
    if not stamp:
        return None
    return pytz.utc.localize(stamp).astimezone(_tz(env)).date()


def _as_date(value):
    if not value:
        return None
    try:
        return fields.Date.to_date(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _company(env, model=None):
    """The company fence of a sudo read (the reader's allowed companies)."""
    if model is not None and "company_id" not in model._fields:
        return []
    return [("company_id", "in", env.companies.ids)]


def _period_datetime(env, field, params):
    """The screen's date_from / date_to (reader's calendar days) on a
    datetime field, as UTC bounds."""
    start, end = _as_date(params.get("date_from")), _as_date(params.get("date_to"))
    domain = []
    if start:
        domain.append((field, ">=", _utc_start(env, start)))
    if end:
        domain.append((field, "<", _utc_start(env, end + datetime.timedelta(days=1))))
    return domain


def _period_date(field, params):
    start, end = _as_date(params.get("date_from")), _as_date(params.get("date_to"))
    domain = []
    if start:
        domain.append((field, ">=", start))
    if end:
        domain.append((field, "<=", end))
    return domain


def _period_note(params):
    start, end = params.get("date_from"), params.get("date_to")
    if start or end:
        return "Period: %s to %s." % (start or "start", end or "today")
    return "All periods."


def _wait_minutes(token):
    """The customer's wait: issued -> called (FR-FRD-005, G1-02)."""
    if not (token.issued_at and token.called_at):
        return None
    return max((token.called_at - token.issued_at).total_seconds(), 0.0) / 60.0


def kpis(env):
    """The M04 module-tile KPI row (registry-canonical metrics), fenced to the
    reader's companies and dated in the Bangladesh business day."""
    Token = env["fix.token.queue"].sudo()
    Shift = env["fix.cash.shift"].sudo()
    Sale = env["fix.counter.sale"].sudo()
    Order = env["fix.service.order"].sudo()
    domain = [("company_id", "in", env.companies.ids)]
    today = _today(env)
    day_start = _utc_start(env, today)
    day_end = _utc_start(env, today + datetime.timedelta(days=1))

    tokens_today = Token.search_count(
        [*domain, ("issued_at", ">=", day_start), ("issued_at", "<", day_end)]
    )

    # the wait is issue -> call; the population is the served tokens
    served = Token.search(
        [
            *domain,
            ("state", "=", "completed"),
            ("served_at", "!=", False),
            ("called_at", "!=", False),
        ],
        order="called_at desc",
        limit=500,
    )
    waits_min = [w for w in (_wait_minutes(t) for t in served) if w is not None]
    avg_wait = round(sum(waits_min) / len(waits_min), 1) if waits_min else None

    # ready (not delivered) for more than 7 days since it became ready
    cutoff = _utc_start(env, today - datetime.timedelta(days=UNCOLLECTED_DAYS))
    uncollected = Order.search_count(
        [*domain, ("state", "=", "ready"), ("ready_at", "!=", False), ("ready_at", "<", cutoff)]
    )

    counted_today = Shift.search([*domain, *_COUNTED, ("shift_date", "=", today)])
    shortage = round(sum(s.variance for s in counted_today if s.variance < 0), 2)
    overage = round(sum(s.variance for s in counted_today if s.variance > 0), 2)

    shifts_open = Shift.search_count([*domain, ("state", "in", ("open", "counting"))])

    month_start = _utc_start(env, today.replace(day=1))
    sales_domain = [*domain, ("state", "=", "confirmed"), ("sale_date", ">=", month_start)]
    sales_mtd = Sale.search_count(sales_domain)
    sales_mtd_bdt = round(sum(Sale.search(sales_domain).mapped("total")), 2)

    return {
        "tokens_today": tokens_today,
        "avg_wait_min": avg_wait,
        "uncollected_7d": uncollected,
        # gross: a shortage is never netted against another drawer's overage
        "cash_variance_today": round(abs(shortage) + overage, 2),
        "cash_shortage_today": shortage,
        "cash_overage_today": overage,
        "shifts_open": shifts_open,
        "counter_sales_mtd": sales_mtd,
        "counter_sales_mtd_bdt": sales_mtd_bdt,
    }


# ---------------------------------------------------------------- reports


def _daily_cash_report(env, **params):
    Shift = env["fix.cash.shift"].sudo()
    rows = []
    shifts = Shift.search(
        [
            *_company(env),
            ("state", "in", ("closed", "reconciled", "discrepancy")),
            *_period_date("shift_date", params),
        ],
        order="shift_date desc, id desc",
        limit=500,
    )
    for s in shifts:
        rows.append(
            {
                "date": str(s.shift_date),
                "branch": s.branch_id.name or "—",
                "operator": s.operator_id.name or "—",
                "opening": s.opening_float,
                "expected": s.expected_closing,
                "counted": s.closing_counted,
                "variance": s.variance,
                "state": s.state,
            }
        )
    return {
        "title": "Branch Daily Cash Summary",
        "cols": [
            "date",
            "branch",
            "operator",
            "opening",
            "expected",
            "counted",
            "variance",
            "state",
        ],
        "labels": {
            "date": "Date",
            "branch": "Branch",
            "operator": "Operator",
            "opening": "Opening Float",
            "expected": "Expected",
            "counted": "Counted",
            "variance": "Variance",
            "state": "State",
        },
        "rows": rows,
        "notes": [
            "Closed and reconciled shifts with their counted drawers and variances.",
            _period_note(params),
        ],
    }


def _wait_distribution_report(env, **params):
    Token = env["fix.token.queue"].sudo()
    called = Token.search(
        [
            *_company(env),
            ("called_at", "!=", False),
            *_period_datetime(env, "issued_at", params),
        ],
        order="issued_at desc",
        limit=5000,
    )
    buckets = {"< 5 min": 0, "5–15 min": 0, "15–30 min": 0, "> 30 min": 0}
    for t in called:
        m = _wait_minutes(t)
        if m is None:
            continue
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
        "notes": [
            "The customer's wait: token issued -> token called, on every called token.",
            _period_note(params),
        ],
    }


def _uncollected_ageing_report(env, **params):
    Order = env["fix.service.order"].sudo()
    today = _today(env)
    rows = []
    for o in Order.search(
        [*_company(env), ("state", "=", "ready"), *_period_datetime(env, "ready_at", params)],
        order="ready_at asc, id asc",
        limit=1000,
    ):
        since = _local_day(env, o.ready_at)
        rows.append(
            {
                "order": o.name,
                "customer": o.customer_id.name or "—",
                "branch": o.branch_id.name or "—",
                "ready_since": str(since) if since else "—",
                "days": (today - since).days if since else None,
            }
        )
    rows.sort(key=lambda r: -(r["days"] if r["days"] is not None else -1))
    return {
        "title": "Uncollected Device Ageing",
        "cols": ["order", "customer", "branch", "ready_since", "days"],
        "labels": {
            "order": "Order",
            "customer": "Customer",
            "branch": "Branch",
            "ready_since": "Ready Since",
            "days": "Days Waiting",
        },
        "rows": rows,
        "notes": [
            "Repaired devices ready at the branch and not yet collected, aged from the day "
            "they became ready; oldest first.",
            _period_note(params),
        ],
    }


def _sales_category_report(env, **params):
    Sale = env["fix.counter.sale"].sudo()
    sales = Sale.search(
        [
            *_company(env),
            ("state", "=", "confirmed"),
            *_period_datetime(env, "sale_date", params),
        ]
    )
    by_category = {}
    for s in sales:
        key = s.product_id.categ_id.display_name or "Uncategorised"
        agg = by_category.setdefault(key, {"count": 0, "quantity": 0.0, "total": 0.0})
        agg["count"] += 1
        agg["quantity"] += s.quantity
        agg["total"] += s.total
    rows = [
        {
            "category": category,
            "count": agg["count"],
            "quantity": agg["quantity"],
            "total": round(agg["total"], 2),
        }
        for category, agg in sorted(by_category.items(), key=lambda kv: -kv[1]["total"])
    ]
    return {
        "title": "Counter Sales by Category",
        "cols": ["category", "count", "quantity", "total"],
        "labels": {
            "category": "Product Category",
            "count": "Sales",
            "quantity": "Quantity",
            "total": "Total (BDT)",
        },
        "rows": rows,
        "notes": [
            "Confirmed counter sales (drafts and refunded sales excluded), by product category.",
            _period_note(params),
        ],
    }


def _variance_register_report(env, **params):
    Shift = env["fix.cash.shift"].sudo()
    rows = [
        {
            "date": str(s.shift_date),
            "branch": s.branch_id.name or "—",
            "shortage": s.variance if s.variance < 0 else 0.0,
            "overage": s.variance if s.variance > 0 else 0.0,
            "approved_by": s.supervisor_variance_approved_by.name or "—",
            "state": s.state,
            "notes": (s.reconciliation_notes or "")[:60],
        }
        for s in Shift.search(
            [
                *_company(env),
                *_COUNTED,
                ("variance", "!=", 0.0),
                *_period_date("shift_date", params),
            ],
            order="shift_date desc, id desc",
            limit=1000,
        )
    ]
    return {
        "title": "Shift Variance Register",
        "cols": ["date", "branch", "shortage", "overage", "approved_by", "state", "notes"],
        "labels": {
            "date": "Date",
            "branch": "Branch",
            "shortage": "Shortage",
            "overage": "Overage",
            "approved_by": "Approved By",
            "state": "State",
            "notes": "Notes",
        },
        "rows": rows,
        "notes": [
            "Every counted drawer that did not balance, shortages and overages apart.",
            _period_note(params),
        ],
    }


def _branch_league_report(env, **params):
    Order = env["fix.service.order"].sudo()
    base = [*_company(env), *_period_datetime(env, "create_date", params)]

    def counts(extra):
        return {
            branch.id: count
            for branch, count in Order._read_group(
                [*base, *extra], groupby=["branch_id"], aggregates=["__count"]
            )
            if branch
        }

    open_n = counts([("state", "not in", ("closed", "cancelled", "delivered"))])
    ready_n = counts([("state", "=", "ready")])
    branches = env["fix.branch"].sudo().browse(sorted(set(open_n) | set(ready_n)))
    rows = [
        {
            "branch": b.name or "—",
            "open_orders": open_n.get(b.id, 0),
            "ready": ready_n.get(b.id, 0),
        }
        for b in branches
    ]
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
        "notes": ["Branch workload comparison from the live order book.", _period_note(params)],
    }


def _shift_checklists_report(env, **params):
    """Open/Close Checklists: the branch day's open/close procedure per cash
    shift — float staged, blind count submitted, counted, variance approved
    (M04 sweep audit 2026-11-06: the screen previously duplicated the branch
    league; this is its own register, per the module's freg sub 8)."""
    Shift = env["fix.cash.shift"].sudo()
    type_labels = dict(Shift._fields["shift_type"].selection)
    state_labels = dict(Shift._fields["state"].selection)
    rows = []
    for s in Shift.search(
        [*_company(env), *_period_date("shift_date", params)],
        order="shift_date desc, id desc",
        limit=500,
    ):
        needs = s.blind_count_submitted and abs(s.variance) > s._fd_tolerance()
        rows.append(
            {
                "shift": "%s · %s"
                % (
                    s.shift_date,
                    type_labels.get(s.shift_type, s.shift_type or "—"),
                ),
                "branch": s.branch_id.name or "—",
                "operator": s.operator_id.name or "—",
                "state": state_labels.get(s.state, s.state),
                "float_staged": "Yes" if s.opening_float else "—",
                "blind_count": "Yes" if s.blind_count_submitted else "No",
                "counted": "Yes" if s.counted_at else "—",
                "variance": s.variance if s.variance else None,
                "variance_approved": "Yes"
                if s.supervisor_variance_approved_by
                else ("Pending" if needs else "Not required"),
            }
        )
    return {
        "title": "Open/Close Checklists",
        "cols": [
            "shift",
            "branch",
            "operator",
            "state",
            "float_staged",
            "blind_count",
            "counted",
            "variance",
            "variance_approved",
        ],
        "labels": {
            "shift": "Shift",
            "branch": "Branch",
            "operator": "Operator",
            "state": "State",
            "float_staged": "Opening Float Staged",
            "blind_count": "Blind Count",
            "counted": "Counted",
            "variance": "Variance (৳)",
            "variance_approved": "Variance Approval",
        },
        "rows": rows,
        "notes": [
            "The open procedure is the staged float; the close procedure is the "
            "blind count, the counted till and the variance sign-off. A variance "
            "beyond tolerance without an approver is a pending checklist item.",
            _period_note(params),
        ],
    }


REPORTS = {
    "daily_cash": _daily_cash_report,
    "wait_distribution": _wait_distribution_report,
    "uncollected_ageing": _uncollected_ageing_report,
    "sales_category": _sales_category_report,
    "variance_register": _variance_register_report,
    "branch_league": _branch_league_report,
    # M04 sweep audit 2026-11-06: the checklist screen gets its own pack.
    "shift_checklists": _shift_checklists_report,
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
