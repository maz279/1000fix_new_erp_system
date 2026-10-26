# A02 · M02 Field Service & Dispatch — models the generic workspace screens
# may read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/field/kpis) and the
# built-in reports (/p03/model/report). Same contract as a02/m01.py.
#
# The bespoke dispatch surfaces (board with suggestions, the live map) are
# served by /p03/field/* endpoints below + the existing /p03/dispatch/map_data.
import datetime
import json
import logging

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.field.order": {
        "order": "scheduled_start desc, id desc",
        "limit": 200,
        "actions": {
            "action_request_dispatch",
            "action_dispatch",
            "action_accept",
            "action_decline",
            "action_start_travel",
            "action_arrive",
            "action_start_work",
            "action_complete",
            "action_cancel",
        },
    },
    "fix.field.route": {
        "order": "date desc, id desc",
        "limit": 100,
        "actions": {"action_optimize_route", "action_start_route", "action_complete_route"},
    },
    "fix.field.decline.log": {
        "order": "id desc",
        "limit": 100,
        "actions": set(),
    },
    "fix.technician.location": {
        "order": "timestamp desc, id desc",
        "limit": 100,
        "actions": set(),
    },
    "fix.offline.idempotency.ledger": {
        "order": "id desc",
        "limit": 100,
        "actions": set(),
    },
    "fix.work.order": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.geofence": {
        "order": "id",
        "limit": 100,
        "actions": set(),
    },
}

_ACTIVE_FIELD_STATES = ("dispatched", "accepted", "en_route", "arrived", "in_progress")
_OPEN_FIELD_STATES = (*_ACTIVE_FIELD_STATES, "draft", "pending_dispatch", "declined")


def _field(env):
    return env["fix.field.order"].sudo().with_context(lang="en_US")


def kpis(env):
    """The M02 module-tile KPI row — measured off the real field tables."""
    FieldOrder = _field(env)
    company_domain = [("company_id", "in", env.companies.ids)]
    now = datetime.datetime.now()

    completed = FieldOrder.search(
        [*company_domain, ("state", "=", "completed"), ("technician_id", "!=", False)], limit=500
    )
    by_tech = {}
    for fo in completed:
        by_tech.setdefault(fo.technician_id.id, []).append(fo)
    # Jobs / Tech / Day: completed field jobs per active technician, last 7 days
    week_ago = now - datetime.timedelta(days=7)
    recent = [fo for fo in completed if fo.completed_at and fo.completed_at >= week_ago]
    active_techs = len(
        {
            fo.technician_id.id
            for fo in FieldOrder.search(
                [
                    *company_domain,
                    ("state", "in", _ACTIVE_FIELD_STATES),
                    ("technician_id", "!=", False),
                ]
            )
        }
    ) or len(by_tech or {1: []})
    jobs_tech_day = round(len(recent) / max(active_techs, 1) / 7.0, 1) if recent else 0.0

    on_time = FieldOrder.search_count(
        [
            *company_domain,
            ("state", "not in", ("draft", "cancelled")),
            ("on_time_arrival", "=", True),
        ]
    )
    arrived = FieldOrder.search_count(
        [
            *company_domain,
            ("state", "not in", ("draft", "cancelled")),
            ("arrived_at", "!=", False),
        ]
    )

    travel_total = sum(
        FieldOrder.search([*company_domain, ("actual_travel_minutes", ">", 0)], limit=500).mapped(
            "actual_travel_minutes"
        )
    )
    # travel share: travel vs (travel + on-site) where both measured — on-site
    # minutes derive from started_work_at → completed_at per order
    onsite = 0.0
    for fo in FieldOrder.search([*company_domain, ("completed_at", "!=", False)], limit=500):
        if fo.started_work_at and fo.completed_at:
            onsite += (fo.completed_at - fo.started_work_at).total_seconds() / 60.0
    travel_share = (
        round(100.0 * travel_total / (travel_total + onsite), 1)
        if (travel_total + onsite)
        else None
    )

    pending = FieldOrder.search(
        [*company_domain, ("state", "in", ("draft", "pending_dispatch", "declined"))], limit=200
    )
    aged_15m = sum(
        1 for fo in pending if fo.create_date and (now - fo.create_date).total_seconds() > 15 * 60
    )

    Ledger = env["fix.offline.idempotency.ledger"].sudo()
    applied = Ledger.search_count([*company_domain, ("status", "=", "applied")])
    total_ledger = Ledger.search_count(company_domain)

    return {
        "jobs_tech_day": jobs_tech_day,
        "auto_assignment": None,  # honest: no auto-assignment engine yet — suggestions only
        "on_time_arrival": round(100.0 * on_time / arrived, 1) if arrived else None,
        "travel_share": travel_share,
        "unassigned_15m": aged_15m,
        "offline_sync_health": round(100.0 * applied / total_ledger, 1) if total_ledger else None,
    }


# ---------------------------------------------------------------- reports


def _utilization_report(env, **params):
    """Technician Utilization & Travel Time: per technician, active/completed
    jobs, measured travel minutes and on-site minutes."""
    FieldOrder = _field(env)
    rows = []
    techs = FieldOrder.search(
        [("company_id", "in", env.companies.ids), ("technician_id", "!=", False)]
    ).mapped("technician_id")
    for tech in techs:
        orders = FieldOrder.search(
            [("technician_id", "=", tech.id), ("state", "not in", ("draft", "cancelled"))]
        )
        travel = sum(orders.mapped("actual_travel_minutes"))
        onsite = 0.0
        for fo in orders:
            if fo.started_work_at and fo.completed_at:
                onsite += (fo.completed_at - fo.started_work_at).total_seconds() / 60.0
        rows.append(
            {
                "technician": tech.name,
                "jobs": len(orders),
                "completed": sum(1 for fo in orders if fo.state == "completed"),
                "travel_min": round(travel),
                "onsite_min": round(onsite),
                "utilization_pct": round(100.0 * onsite / (onsite + travel), 1)
                if (onsite + travel)
                else None,
            }
        )
    rows.sort(key=lambda r: -r["jobs"])
    return {
        "title": "Technician Utilization & Travel Time",
        "cols": ["technician", "jobs", "completed", "travel_min", "onsite_min", "utilization_pct"],
        "labels": {
            "technician": "Technician",
            "jobs": "Jobs",
            "completed": "Completed",
            "travel_min": "Travel (min)",
            "onsite_min": "On-site (min)",
            "utilization_pct": "On-site %",
        },
        "rows": rows,
        "notes": [
            "Measured from journey stamps (en_route→arrived = travel, work-start→completed = on-site)."
        ],
    }


def _geofence_delay_report(env, **params):
    """Geofence Breach & Delay Log: geofence.breach events from the outbox +
    declined dispatches with reasons (the delay taxonomy)."""
    Outbox = env["fix.event.outbox"].sudo()
    breaches = Outbox.search(
        [("event_type", "=", "geofence.breach.detected")], order="id desc", limit=100
    )
    rows = [
        {
            "kind": "geofence breach",
            "ref": (json.loads(e.payload) or {}).get("order_ref", e.aggregate_id),
            "detail": (json.loads(e.payload) or {}).get("detail", "")[:80],
            "at": str(e.create_date)[:16],
        }
        for e in breaches
    ]
    Decline = env["fix.field.decline.log"].sudo()
    for d in Decline.search([], order="id desc", limit=100):
        rows.append(
            {
                "kind": "decline: %s" % d.reason,
                "ref": d.field_order_id.name or "",
                "detail": (d.notes or "")[:80],
                "at": str(d.decline_date or d.create_date)[:16],
            }
        )
    rows.sort(key=lambda r: r["at"], reverse=True)
    return {
        "title": "Geofence Breach & Delay Log",
        "cols": ["kind", "ref", "detail", "at"],
        "labels": {"kind": "Event", "ref": "Field Order", "detail": "Detail", "at": "When"},
        "rows": rows,
        "notes": [
            "Geofence breaches arrive via the transactional outbox; declines from fix.field.decline.log."
        ],
    }


def _zone_workload_report(env, **params):
    """Territory Workload Balance: open field orders per dispatch zone."""
    FieldOrder = _field(env)
    zones = env["fix.zone"].sudo().search([])
    rows = []
    for zone in zones:
        open_jobs = FieldOrder.search_count(
            [("zone_id", "=", zone.id), ("state", "in", _OPEN_FIELD_STATES)]
        )
        unassigned = FieldOrder.search_count(
            [("zone_id", "=", zone.id), ("state", "in", ("draft", "pending_dispatch", "declined"))]
        )
        rows.append({"zone": zone.name, "open": open_jobs, "unassigned": unassigned})
    rows.sort(key=lambda r: -r["open"])
    return {
        "title": "Territory Workload Balance",
        "cols": ["zone", "open", "unassigned"],
        "labels": {"zone": "Zone", "open": "Open Jobs", "unassigned": "Unassigned"},
        "rows": rows,
        "notes": ["Open (non-cancelled) field orders per dispatch zone, live counts."],
    }


def _field_pay_report(env, **params):
    """Field Payment Reconciliation — honest placeholder measure: field
    payments are not yet a built engine (M02 pays via M20 on order close);
    this reports field-order completions that became billable events."""
    FieldOrder = _field(env)
    completed = FieldOrder.search(
        [("company_id", "in", env.companies.ids), ("state", "=", "completed")], limit=200
    )
    rows = [
        {
            "field_order": fo.name,
            "service_order": fo.order_id.name,
            "completed_at": str(fo.completed_at or "")[:16],
            "billable_event": "service_order.closed pipeline (M20)",
        }
        for fo in completed
    ]
    return {
        "title": "Field Payment Reconciliation",
        "cols": ["field_order", "service_order", "completed_at", "billable_event"],
        "labels": {
            "field_order": "Field Order",
            "service_order": "Service Order",
            "completed_at": "Completed",
            "billable_event": "Billing Path",
        },
        "rows": rows,
        "notes": [
            "Field collections bill through the M20 AR engine when the service order closes — no separate field-payment ledger exists yet."
        ],
    }


REPORTS = {
    "technician_utilization": _utilization_report,
    "geofence_delays": _geofence_delay_report,
    "zone_workload": _zone_workload_report,
    "field_payments": _field_pay_report,
}


class P03M02Controller(http.Controller):
    """Bespoke M02 dispatch endpoints: the suggestion engine behind the
    dispatch modal and the module KPI row."""

    @http.route("/p03/field/kpis", type="jsonrpc", auth="user", readonly=True)
    def field_kpis(self, **kw):
        _require_internal(request.env)
        try:
            return {"M02": kpis(request.env)}
        except Exception:
            _logger.exception("p03 field_kpis failed")
            return {"error": "KPI computation failed"}

    @http.route("/p03/field/suggest", type="jsonrpc", auth="user", readonly=True)
    def field_suggest(self, field_order_id=None, **kw):
        """Ranked technician suggestions for one field order (the explainable
        scoring engine — fix.field.order.action_suggest_technicians)."""
        _require_internal(request.env)
        fo = request.env["fix.field.order"].browse(int(field_order_id or 0)).exists()
        if not fo:
            return {"error": "Field order not found"}
        return {"suggestions": fo.sudo().action_suggest_technicians()}
