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
            # A02 pass 2 (M04-03): a float other than the last close's cash
            "action_approve_opening_float",
            # A02 pass 2 (X5-20): a variance the GL still owes
            "action_retry_variance_posting",
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
            # A02 pass 2 (X5-20): a sale / refund the books still owe
            "action_retry_posting",
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
        # A02 pass 2 (M04-01 / X5-20): a cash-out the GL still owes
        "actions": {"action_approve", "action_post", "action_cancel", "action_retry_posting"},
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


def _branch_fence(env, model):
    """A02 pass 2 (M04-06): the tile shows the reader's branches. A reader
    restricted to some operating units sees theirs; the fence is the record's
    operating unit (or its branch's)."""
    units = getattr(env.user, "operating_unit_ids", None)
    if not units:
        return []
    has_ou, has_branch = "operating_unit_id" in model._fields, "branch_id" in model._fields
    if has_ou and has_branch:
        # A02 pass 2 review: the record's own unit, else its branch's (an order
        # with no unit of its own, at a branch of the reader's, was dropped)
        return [
            "|",
            ("operating_unit_id", "in", units.ids),
            "&",
            ("operating_unit_id", "=", False),
            ("branch_id.operating_unit_id", "in", units.ids),
        ]
    if has_ou:
        return [("operating_unit_id", "in", units.ids)]
    if has_branch:
        return [("branch_id.operating_unit_id", "in", units.ids)]
    return []


_WIP_EXCLUDED = ("ready", "delivered", "closed", "cancelled")


def kpis(env):
    """The M04 module-tile KPI row (registry-canonical metrics), fenced to the
    reader's companies and branches (A02 pass 2, M04-06) and dated in the
    Bangladesh business day. No figure is measured over a capped subset
    (X5-17: the average wait read the last 500 tokens of every branch ever)."""
    Token = env["fix.token.queue"].sudo()
    Shift = env["fix.cash.shift"].sudo()
    Sale = env["fix.counter.sale"].sudo()
    Order = env["fix.service.order"].sudo()
    Intake = env["fix.walkin.intake"].sudo()
    base = [("company_id", "in", env.companies.ids)]
    today = _today(env)
    day_start = _utc_start(env, today)
    day_end = _utc_start(env, today + datetime.timedelta(days=1))
    today_dt = [(">=", day_start), ("<", day_end)]

    def fenced(model):
        return [*base, *_branch_fence(env, model)]

    domain = fenced(Token)
    tokens_today = Token.search_count(
        [*domain, ("issued_at", ">=", day_start), ("issued_at", "<", day_end)]
    )

    # the wait is issue -> call, over every token called today (no cap)
    served = Token.search(
        [
            *domain,
            ("called_at", "!=", False),
            ("issued_at", "!=", False),
            ("called_at", ">=", day_start),
            ("called_at", "<", day_end),
        ]
    )
    waits_min = [w for w in (_wait_minutes(t) for t in served) if w is not None]
    avg_wait = round(sum(waits_min) / len(waits_min), 1) if waits_min else None

    # today's branch work: intakes handed over today, the repair work in
    # progress, the devices ready for collection, and today's takings
    intakes_today = Intake.search_count(
        [
            *fenced(Intake),
            ("state", "=", "completed"),
            *[("handover_complete", op, value) for op, value in today_dt],
        ]
    )
    order_domain = fenced(Order)
    wip = Order.search_count([*order_domain, ("state", "not in", _WIP_EXCLUDED)])
    ready = Order.search_count([*order_domain, ("state", "=", "ready")])
    sale_domain = fenced(Sale)
    sales_today = Sale.search(
        [*sale_domain, ("state", "=", "confirmed"), *[("sale_date", op, v) for op, v in today_dt]]
    )
    revenue_today = sum(sales_today.mapped("total"))
    if "fix.ar.receipt" in env and "source_order_id" in env["fix.ar.receipt"]._fields:
        Receipt = env["fix.ar.receipt"].sudo()
        receipts = Receipt.search(
            [
                *fenced(Receipt),
                ("state", "=", "confirmed"),
                ("source_order_id", "!=", False),
                ("receipt_date", "=", today),
            ]
        )
        revenue_today += sum(receipts.mapped("amount"))
    revenue_today = round(revenue_today, 2)
    domain = fenced(Order)

    # ready (not delivered) for more than 7 days since it became ready
    cutoff = _utc_start(env, today - datetime.timedelta(days=UNCOLLECTED_DAYS))
    uncollected = Order.search_count(
        [*domain, ("state", "=", "ready"), ("ready_at", "!=", False), ("ready_at", "<", cutoff)]
    )

    shift_domain = fenced(Shift)
    counted_today = Shift.search([*shift_domain, *_COUNTED, ("shift_date", "=", today)])
    shortage = round(sum(s.variance for s in counted_today if s.variance < 0), 2)
    overage = round(sum(s.variance for s in counted_today if s.variance > 0), 2)

    shifts_open = Shift.search_count([*shift_domain, ("state", "in", ("open", "counting"))])

    month_start = _utc_start(env, today.replace(day=1))
    sales_domain = [*sale_domain, ("state", "=", "confirmed"), ("sale_date", ">=", month_start)]
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
        # A02 pass 2 (M04-06): the branch's day
        "intakes_today": intakes_today,
        "orders_wip": wip,
        "orders_ready": ready,
        "takings_today_bdt": revenue_today,
        "books_pending": _books_pending_count(env),
    }


# ---------------------------------------------------------------- reports


_CASH_OUT_TYPES = ("safe_drop", "petty_expense", "staff_advance", "field_shortage")


def _drawer_breakdown(movements):
    """A shift's drawer movements by source (the ledger's own references)."""
    out = {"sales": 0.0, "settlements": 0.0, "field": 0.0, "refunds": 0.0, "cash_outs": 0.0}
    for mv in movements:
        if mv.state != "posted":
            continue
        ref = mv.reference or ""
        if mv.movement_type == "receipt":
            key = "sales" if ref.startswith("Counter sale") else "settlements"
        elif mv.movement_type == "field_cash":
            key = "field"
        elif mv.movement_type == "refund":
            key = "refunds"
        elif mv.movement_type in _CASH_OUT_TYPES:
            key = "cash_outs"
        else:
            continue
        out[key] += mv.amount
    return {k: round(v, 2) for k, v in out.items()}


def _non_cash_takings(env, branch, day):
    """What the branch took on ``day`` other than drawer cash: counter sales
    by wallet / card, service-order settlements and diagnostic fees by wallet /
    card (M20 receipts), and cash on delivery collected by riders."""
    Sale = env["fix.counter.sale"].sudo()
    total = sum(
        Sale.search(
            [
                ("branch_id", "=", branch.id),
                ("state", "in", ("confirmed", "refunded")),
                ("payment_method", "!=", "cash"),
                ("sale_date", ">=", _utc_start(env, day)),
                ("sale_date", "<", _utc_start(env, day + datetime.timedelta(days=1))),
            ]
        ).mapped("total")
    )
    if "fix.ar.receipt" in env and "source_order_id" in env["fix.ar.receipt"]._fields:
        total += sum(
            env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("branch_id", "=", branch.id),
                    ("state", "=", "confirmed"),
                    ("source_order_id", "!=", False),
                    ("method", "!=", "cash"),
                    ("receipt_date", "=", day),
                ]
            )
            .mapped("amount")
        )
    return round(total, 2)


def _daily_cash_report(env, **params):
    """X5-24 (A02 pass 2): every shift of the period with its drawer broken
    down by source (sales, service-order settlements and fees, field cash,
    refunds, cash-outs), and per branch day the takings that never touched a
    drawer (wallet / card / COD). No cap: the period decides."""
    Shift = env["fix.cash.shift"].sudo()
    Movement = env["fix.cash.movement"].sudo()
    rows = []
    shifts = Shift.search(
        [*_company(env), *_period_date("shift_date", params)],
        order="shift_date desc, branch_id, id desc",
    )
    states = dict(Shift._fields["state"].selection)
    movements = Movement.search([("shift_id", "in", shifts.ids)])
    by_shift = {}
    for mv in movements:
        by_shift.setdefault(mv.shift_id.id, []).append(mv)
    seen_days = []
    for s in shifts:
        parts = _drawer_breakdown(by_shift.get(s.id, []))
        counted = s.blind_count_submitted or s.state in ("closed", "reconciled", "discrepancy")
        rows.append(
            {
                "date": str(s.shift_date),
                "branch": s.branch_id.name or "—",
                "operator": s.operator_id.name or "—",
                "opening": s.opening_float,
                "sales": parts["sales"],
                "settlements": parts["settlements"],
                "field": parts["field"],
                "refunds": parts["refunds"],
                "cash_outs": parts["cash_outs"],
                "expected": s.expected_closing,
                "counted": s.closing_counted if counted else None,
                "variance": s.variance if counted else None,
                "non_cash": None,
                "state": states.get(s.state, s.state),
            }
        )
        key = (s.branch_id.id, s.shift_date)
        if s.branch_id and key not in seen_days:
            seen_days.append(key)
    for branch_id, day in seen_days:
        branch = env["fix.branch"].sudo().browse(branch_id)
        rows.append(
            {
                "date": str(day),
                "branch": branch.name or "—",
                "operator": "Non-cash takings (branch day)",
                "opening": None,
                "sales": None,
                "settlements": None,
                "field": None,
                "refunds": None,
                "cash_outs": None,
                "expected": None,
                "counted": None,
                "variance": None,
                "non_cash": _non_cash_takings(env, branch, day),
                "state": "—",
            }
        )
    return {
        "title": "Branch Daily Cash Summary",
        "cols": [
            "date",
            "branch",
            "operator",
            "opening",
            "sales",
            "settlements",
            "field",
            "refunds",
            "cash_outs",
            "expected",
            "counted",
            "variance",
            "non_cash",
            "state",
        ],
        "labels": {
            "date": "Date",
            "branch": "Branch",
            "operator": "Operator",
            "opening": "Opening Float",
            "sales": "Counter Sales (cash)",
            "settlements": "Order Settlements & Fees (cash)",
            "field": "Field Cash Handed In",
            "refunds": "Refunds Paid",
            "cash_outs": "Cash-Outs (expense / advance / safe)",
            "expected": "Expected",
            "counted": "Counted",
            "variance": "Variance",
            "non_cash": "Non-Cash Takings (wallet / card / COD)",
            "state": "State",
        },
        "rows": rows,
        "notes": [
            "Every shift of the period: opening float + counter sales + order settlements and "
            "diagnostic fees + field cash - refunds - cash-outs = expected; counted and the "
            "variance once the count is in.",
            "One line per branch day adds what was taken without touching a drawer: counter "
            "sales by wallet or card, service-order payments and fees by wallet, card or cash "
            "on delivery (their M20 receipts).",
            _period_note(params),
        ],
    }


# ---------------------------------------------------------------- books pending (X5-20)


def _books_pending_rows(env):
    """Everything the front desk took that the books still owe, with why."""
    rows = []
    Sale = env["fix.counter.sale"].sudo()
    if "posting_state" in Sale._fields:
        for sale in Sale.search(
            [*_company(env), ("posting_state", "in", ("pending", "reversal_pending"))],
            order="id",
        ):
            rows.append(
                {
                    "kind": "Counter sale",
                    "record": sale.name,
                    "model": "fix.counter.sale",
                    "id": sale.id,
                    "branch": sale.branch_id.name or "—",
                    "amount": sale.total,
                    "state": dict(Sale._fields["posting_state"].selection).get(
                        sale.posting_state, sale.posting_state
                    ),
                    "note": (sale.posting_note or "")[:200],
                    "retry": "action_retry_posting",
                }
            )
    Shift = env["fix.cash.shift"].sudo()
    if "variance_posting_state" in Shift._fields:
        for shift in Shift.search(
            [
                *_company(env),
                "|",
                ("variance_posting_state", "=", "pending"),
                ("float_posting_state", "=", "pending"),
            ],
            order="id",
        ):
            if shift.variance_posting_state == "pending":
                rows.append(
                    {
                        "kind": "Shift variance",
                        "record": "Shift #%s %s" % (shift.id, shift.shift_date),
                        "model": "fix.cash.shift",
                        "id": shift.id,
                        "branch": shift.branch_id.name or "—",
                        "amount": shift.variance,
                        "state": "Pending Posting",
                        "note": (shift.variance_posting_note or "")[:200],
                        "retry": "action_retry_variance_posting",
                    }
                )
            if shift.float_posting_state == "pending":
                rows.append(
                    {
                        "kind": "Opening float difference",
                        "record": "Shift #%s %s" % (shift.id, shift.shift_date),
                        "model": "fix.cash.shift",
                        "id": shift.id,
                        "branch": shift.branch_id.name or "—",
                        "amount": shift.float_variance,
                        "state": "Pending Posting",
                        "note": (shift.float_posting_note or "")[:200],
                        "retry": "action_retry_variance_posting",
                    }
                )
    Movement = env["fix.cash.movement"].sudo()
    if "posting_state" in Movement._fields:
        for mv in Movement.search([*_company(env), ("posting_state", "=", "pending")], order="id"):
            rows.append(
                {
                    "kind": "Drawer cash-out",
                    "record": mv.name,
                    "model": "fix.cash.movement",
                    "id": mv.id,
                    "branch": mv.branch_id.name or "—",
                    "amount": mv.amount,
                    "state": "Pending Posting",
                    "note": (mv.posting_note or "")[:200],
                    "retry": "action_retry_posting",
                }
            )
    return rows


def _books_pending_count(env):
    return len(_books_pending_rows(env))


def _books_pending_report(env, **params):
    rows = _books_pending_rows(env)
    return {
        "title": "Front-Desk Money Not Yet in the Books",
        "cols": ["kind", "record", "branch", "amount", "state", "note"],
        "labels": {
            "kind": "What",
            "record": "Record",
            "branch": "Branch",
            "amount": "Amount (BDT)",
            "state": "Books",
            "note": "Why It Has Not Posted",
        },
        "rows": rows,
        "notes": [
            "Counter sales and refunds, drawer variances, opening-float differences and "
            "drawer cash-outs whose GL / VAT / stock posting is pending. Fix the cause named "
            "(usually an account parameter), then Retry Posting on the record or wait for "
            "the hourly job. Nothing posts twice.",
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
    # A02 pass 2 (X5-20): money taken that the books still owe
    "books_pending": _books_pending_report,
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
