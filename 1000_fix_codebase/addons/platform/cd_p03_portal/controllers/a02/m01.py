# A02 · M01 Service Requests & Orders — models the generic workspace screens
# may read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/service/kpis) and the
# built-in reports (/p03/model/report). Each SURFACES entry:
# model -> {"order", "limit", "actions"}. Reads also need the caller's own
# read access on the model; actions run in a savepoint with the caller's
# context (SoD/permissions apply).
#
# The bespoke order surfaces (list scopes, board, intake console) are served
# by p03_service_order_api.py (/p03/orders/list with scope=, /p03/stats).
import datetime
import logging

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal, _user_error

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.service.order": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_start_diagnostic",
            "action_send_estimate",
            "action_approve",
            "action_start_repair",
            "action_submit_qc",
            "action_ready",
            "action_deliver",
            "action_close",
            "action_cancel",
            "action_resume_order",
            "action_issue_repair_warranty",
            # M02 bridge (defined in cd_field_service's extension): hand an
            # on-site order to the dispatch pipeline
            "action_create_field_order",
            # M31 bridge (defined in cd_workshop's extension): hand a bench
            # job order to the workshop pipeline
            "action_create_workshop_job",
        },
    },
    "fix.estimate": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            "action_send",
            "action_approve",
            "action_manager_approve",
            "action_reject",
            "action_revise",
        },
    },
    "fix.qc.checklist": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_complete"},
    },
    "fix.token.queue": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_call", "action_serving", "action_complete"},
    },
    "fix.walkin.intake": {
        "order": "id desc",
        "limit": 100,
        "actions": {"action_complete_handover"},
    },
    "fix.sla.policy": {
        "order": "code",
        "limit": 200,
        "actions": set(),
    },
    "fix.diagnostic.node": {
        "order": "id",
        "limit": 300,
        "actions": set(),
    },
    "fix.fault.code": {
        "order": "category, code",
        "limit": 200,
        "actions": set(),
    },
    "fix.warranty": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.device.history": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
}

# open orders = the AS-06 states where the job is still live work
_OPEN_STATES = [
    "draft",
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
    "qc_failed",
]
_WIP_STATES = [
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
    "qc_failed",
]


def _orders(env):
    return env["fix.service.order"].sudo().with_context(lang="en_US")


def kpis(env):
    """The M01 module-tile KPI row — same measures the Role Center computes
    (single source: the real fix.service.order/estimate tables)."""
    Order = _orders(env)
    company_domain = [("company_id", "in", env.companies.ids)]

    open_orders = Order.search_count([*company_domain, ("state", "in", _OPEN_STATES)])
    at_risk = Order.search_count(
        [
            *company_domain,
            ("state", "in", _OPEN_STATES),
            ("sla_clock_paused", "=", False),
            ("sla_resolution_deadline", "!=", False),
            ("sla_resolution_deadline", "<", datetime.datetime.now()),
        ]
    )

    # TAT: closed orders resolved within 24h of response start (IT target)
    closed = Order.search([*company_domain, ("state", "=", "closed")], limit=500)
    tat_total = 0
    tat_24 = 0
    for order in closed:
        started = order.sla_response_at
        resolved = order.sla_resolution_at
        if started and resolved:
            tat_total += 1
            if (resolved - started).total_seconds() <= 24 * 3600:
                tat_24 += 1

    # Estimate conversion: approved / (approved + rejected + expired)
    Estimate = env["fix.estimate"].sudo()
    decided = Estimate.search_count(
        [*company_domain, ("state", "in", ("approved", "rejected", "expired"))]
    )
    approved = Estimate.search_count([*company_domain, ("state", "=", "approved")])

    rework_open = Order.search_count(
        [*company_domain, ("state", "in", _OPEN_STATES), ("is_rework", "=", True)]
    )

    # intake speed: the walk-in intake model carries no timer yet — honest null
    return {
        "open_orders": open_orders,
        "sla_at_risk": at_risk,
        "tat_under_24h": round(100.0 * tat_24 / tat_total, 1) if tat_total else None,
        "estimate_conversion": round(100.0 * approved / decided, 1) if decided else None,
        "intake_minutes": None,
        "rework_rate": round(100.0 * rework_open / open_orders, 1) if open_orders else None,
    }


# ---------------------------------------------------------------- reports


def _fmt_day(value):
    return str(value)[:10] if value else ""


def channel_intake_report(env, date_from=None, date_to=None, **params):
    """Daily Intake by Channel: real orders grouped by service_type, day."""
    domain = [("company_id", "in", env.companies.ids)]
    if date_from:
        domain.append(("create_date", ">=", date_from))
    if date_to:
        domain.append(("create_date", "<=", date_to + " 23:59:59"))
    rows = []
    grouped = _orders(env)._read_group(
        [*domain, ("service_type", "!=", False)],
        ["service_type", "create_date:day"],
        ["__count"],
    )
    for service_type, day, count in grouped:
        rows.append(
            {
                "day": day if isinstance(day, str) else _fmt_day(day),
                "service_type": service_type,
                "orders": count,
            }
        )
    rows.sort(key=lambda r: (r["day"], r["service_type"]))
    return {
        "title": "Daily Intake by Channel",
        "cols": ["day", "service_type", "orders"],
        "labels": {"day": "Day", "service_type": "Channel", "orders": "Orders"},
        "rows": rows,
        "notes": ["Live reads of fix.service.order, grouped by intake channel and day."],
    }


def wip_ageing_report(env, **params):
    """WIP Ageing by Branch: open WIP orders bucketed by days since intake."""
    today = datetime.date.today()
    domain = [
        ("company_id", "in", env.companies.ids),
        ("state", "in", _WIP_STATES),
    ]
    buckets = {"under_24h": 0, "24_48h": 0, "over_48h": 0}
    by_branch = {}
    for order in _orders(env).search(domain):
        created = order.create_date.date() if order.create_date else today
        age = (today - created).days
        key = "under_24h" if age < 1 else ("24_48h" if age < 2 else "over_48h")
        buckets[key] += 1
        name = order.branch_id.name or "—"
        by_branch.setdefault(name, {"under_24h": 0, "24_48h": 0, "over_48h": 0})[key] += 1
    rows = [
        {
            "branch": branch,
            "under_24h": counts["under_24h"],
            "24_48h": counts["24_48h"],
            "over_48h": counts["over_48h"],
            "total": sum(counts.values()),
        }
        for branch, counts in sorted(by_branch.items())
    ]
    return {
        "title": "WIP Ageing by Branch",
        "cols": ["branch", "under_24h", "24_48h", "over_48h", "total"],
        "labels": {
            "branch": "Branch",
            "under_24h": "< 24h",
            "24_48h": "24–48h",
            "over_48h": "> 48h",
            "total": "Total WIP",
        },
        "rows": rows,
        "notes": ["Open WIP orders (intake → QC failed) bucketed by days since intake."],
    }


def sla_compliance_report(env, **params):
    """SLA Compliance: closed orders resolved before their deadline; open
    orders already past it. Measured off the real SLA clock fields."""
    Order = _orders(env)
    company_domain = [("company_id", "in", env.companies.ids)]
    closed = Order.search([*company_domain, ("state", "in", ("closed", "delivered"))], limit=1000)
    met = late = 0
    for order in closed:
        if order.sla_resolution_deadline and order.sla_resolution_at:
            if order.sla_resolution_at <= order.sla_resolution_deadline:
                met += 1
            else:
                late += 1
    open_late = Order.search_count(
        [
            *company_domain,
            ("state", "in", _OPEN_STATES),
            ("sla_clock_paused", "=", False),
            ("sla_resolution_deadline", "!=", False),
            ("sla_resolution_deadline", "<", datetime.datetime.now()),
        ]
    )
    paused = Order.search_count(
        [*company_domain, ("state", "in", _OPEN_STATES), ("sla_clock_paused", "=", True)]
    )
    decided = met + late
    return {
        "title": "SLA Compliance & Escalations",
        "cols": ["measure", "value"],
        "labels": {"measure": "Measure", "value": "Orders"},
        "rows": [
            {"measure": "Resolved on time", "value": met},
            {"measure": "Resolved late", "value": late},
            {
                "measure": "Compliance %",
                "value": round(100.0 * met / decided, 1) if decided else None,
            },
            {"measure": "Open & past deadline (at risk)", "value": open_late},
            {"measure": "Clocks paused (holds)", "value": paused},
        ],
        "notes": ["Deadline = sla_resolution_deadline; resolution stamp = sla_resolution_at."],
    }


def estimate_funnel_report(env, **params):
    """Estimate Conversion Funnel: sent → approved/rejected/expired."""
    Estimate = env["fix.estimate"].sudo()
    company_domain = [("company_id", "in", env.companies.ids)]
    sent = Estimate.search_count([*company_domain, ("state", "!=", "draft")])
    approved = Estimate.search_count([*company_domain, ("state", "=", "approved")])
    rejected = Estimate.search_count([*company_domain, ("state", "=", "rejected")])
    expired = Estimate.search_count([*company_domain, ("state", "=", "expired")])
    return {
        "title": "Estimate Conversion Funnel",
        "cols": ["stage", "value"],
        "labels": {"stage": "Stage", "value": "Estimates"},
        "rows": [
            {"stage": "Sent to customer", "value": sent},
            {"stage": "Approved", "value": approved},
            {"stage": "Rejected", "value": rejected},
            {"stage": "Expired", "value": expired},
            {"stage": "Conversion %", "value": round(100.0 * approved / sent, 1) if sent else None},
        ],
        "notes": ["Live fix.estimate states — the approval loop's real funnel."],
    }


def rework_analysis_report(env, **params):
    """Rework & Repeat-Fault Analysis: rework-flagged orders by state and
    device model (BRU-SRM-06 same-device-within-30-days detection)."""
    Order = _orders(env)
    domain = [("company_id", "in", env.companies.ids), ("is_rework", "=", True)]
    rework = Order.search(domain, limit=500)
    by_state = {}
    by_model = {}
    for order in rework:
        by_state[order.state] = by_state.get(order.state, 0) + 1
        model = order.device_id.device_model_id.name or "—"
        by_model[model] = by_model.get(model, 0) + 1
    rows = [
        {"dimension": "state: %s" % state, "orders": count}
        for state, count in sorted(by_state.items())
    ] + [
        {"dimension": "model: %s" % model, "orders": count}
        for model, count in sorted(by_model.items(), key=lambda kv: -kv[1])
    ]
    return {
        "title": "Rework & Repeat-Fault Analysis",
        "cols": ["dimension", "orders"],
        "labels": {"dimension": "Dimension", "orders": "Rework Orders"},
        "rows": rows,
        "notes": ["is_rework flags same-device orders within 30 days (BRU-SRM-06)."],
    }


def tat_distribution_report(env, **params):
    """Order Cycle-Time (TAT) distribution: hours between response start and
    resolution for closed orders."""
    Order = _orders(env)
    closed = Order.search(
        [("company_id", "in", env.companies.ids), ("state", "=", "closed")], limit=1000
    )
    buckets = {"< 4h": 0, "4–24h": 0, "24–72h": 0, "> 72h": 0}
    for order in closed:
        if not (order.sla_response_at and order.sla_resolution_at):
            continue
        hours = (order.sla_resolution_at - order.sla_response_at).total_seconds() / 3600.0
        if hours < 4:
            buckets["< 4h"] += 1
        elif hours <= 24:
            buckets["4–24h"] += 1
        elif hours <= 72:
            buckets["24–72h"] += 1
        else:
            buckets["> 72h"] += 1
    return {
        "title": "Order Cycle-Time (TAT) Distribution",
        "cols": ["bucket", "orders"],
        "labels": {"bucket": "Turnaround", "orders": "Closed Orders"},
        "rows": [{"bucket": k, "orders": v} for k, v in buckets.items()],
        "notes": ["TAT = first in_repair stamp → resolution stamp, closed orders."],
    }


def uncollected_register_report(env, **params):
    """Uncollected Device Register: repaired orders waiting on the customer
    (ready for collection or delivered but not closed) — devices in our
    custody that are not yet collected."""
    Order = _orders(env)
    domain = [
        ("company_id", "in", env.companies.ids),
        ("state", "in", ("ready", "delivered")),
    ]
    rows = []
    for order in Order.search(domain, order="write_date desc", limit=300):
        rows.append(
            {
                "order": order.name,
                "customer": order.customer_id.name or "—",
                "device": order.device_id.name or order.device_serial or "—",
                "state": order.state,
                "ready_since": _fmt_day(order.write_date),
            }
        )
    return {
        "title": "Uncollected Device Register",
        "cols": ["order", "customer", "device", "state", "ready_since"],
        "labels": {
            "order": "Order",
            "customer": "Customer",
            "device": "Device",
            "state": "State",
            "ready_since": "Since",
        },
        "rows": rows,
        "notes": ["Devices repaired but not collected (ready / delivered, not closed)."],
    }


def type_matrix_report(env, **params):
    """Order Types: real order counts by service_type × order_category — the
    live streams, not a hard-coded 12."""
    grouped = _orders(env)._read_group(
        [("company_id", "in", env.companies.ids)],
        ["service_type", "order_category"],
        ["__count"],
    )
    rows = [
        {"service_type": service_type or "—", "order_category": category or "—", "orders": count}
        for service_type, category, count in grouped
    ]
    rows.sort(key=lambda r: -r["orders"])
    return {
        "title": "Order Types — Live Streams",
        "cols": ["service_type", "order_category", "orders"],
        "labels": {
            "service_type": "Channel / Type",
            "order_category": "Category",
            "orders": "Orders",
        },
        "rows": rows,
        "notes": ["Every combination in the live order book (service_type × order_category)."],
    }


def approval_thresholds_report(env, **params):
    """Approval Thresholds: the live BRU-SRM-07/08 values actually enforced by
    fix.estimate (config-param overridable, defaults BDT 5,000 / 25,000)."""
    Estimate = env["fix.estimate"]
    return {
        "title": "Estimate Approval Thresholds",
        "cols": ["gate", "threshold_bdt", "source"],
        "labels": {"gate": "Approval Gate", "threshold_bdt": "Threshold (BDT)", "source": "Source"},
        "rows": [
            {
                "gate": "BRU-SRM-07 — documented customer approval",
                "threshold_bdt": Estimate._threshold_customer(),
                "source": "cd_service_order.estimate_threshold_customer (default 5,000)",
            },
            {
                "gate": "BRU-SRM-08 — + branch manager approval",
                "threshold_bdt": Estimate._threshold_dual(),
                "source": "cd_service_order.estimate_threshold_dual (default 25,000)",
            },
        ],
        "notes": ["These are the values action_approve enforces right now."],
    }


REPORTS = {
    "channel_intake": channel_intake_report,
    "wip_ageing": wip_ageing_report,
    "sla_compliance": sla_compliance_report,
    "estimate_funnel": estimate_funnel_report,
    "rework_analysis": rework_analysis_report,
    "tat_distribution": tat_distribution_report,
    "uncollected_register": uncollected_register_report,
    "type_matrix": type_matrix_report,
    "approval_thresholds": approval_thresholds_report,
}


class P03M01Controller(http.Controller):
    """The M01 module KPI row — served here so the A02 fragment owns its
    whole surface (same shape as /p03/finance/kpis for A08)."""

    @http.route("/p03/service/kpis", type="jsonrpc", auth="user", readonly=True)
    def service_kpis(self, **kw):
        _require_internal(request.env)
        try:
            # keyed by module — the same shape /p03/finance/kpis returns, so
            # the workspace's kpi loader reads res[mid] identically
            return {"M01": kpis(request.env)}
        except Exception:
            _logger.exception("p03 service_kpis failed")
            return {"error": _user_error("KPI computation failed")}
