# A02 · M02 Field Service & Dispatch — models the generic workspace screens
# may read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/field/kpis) and the
# built-in reports (/p03/model/report). Same contract as a02/m01.py.
#
# The bespoke dispatch surfaces (board with suggestions, the live map) are
# served by /p03/field/* endpoints below + the existing /p03/dispatch/map_data.
import datetime
import logging

import pytz
from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.field.order": {
        "order": "scheduled_start desc, id desc",
        "limit": 200,
        # A02 audit P0: every method checks its own authority (dispatcher for
        # dispatch, reassign, the geofence waiver and cancel in dispatch; the
        # assigned technician for accept, decline and progress).
        "actions": {
            "action_request_dispatch",
            # action_dispatch is NOT here (M02 capture audit 2026-11-18): the
            # workspace dispatches by saving a fix.dispatch.decision, which
            # keeps the engine's first choice and the override reason
            # (BRU-FSM-04); a bare dispatch would bypass both.
            "action_reassign",
            # A09 M22-F3: an uncertified technician needs a routed waiver
            "action_request_certification_waiver",
            "action_accept",
            "action_decline",
            "action_start_travel",
            "action_waive_geofence",
            "action_arrive",
            "action_start_work",
            "action_record_collection",
            "action_complete",
            "action_handover_field_cash",
            # A02 ERP audit M02-F1: a cashier of the order's branch accepts the
            # declared cash into that branch's drawer (the method checks who)
            "action_accept_field_cash",
            # A02 ERP audit M02-F3: the dispatcher moves the arrival fence
            "action_set_geofence",
            "action_cancel",
        },
    },
    # A02 audit M02-P2: parts fitted on site. Lines are written by the
    # technician app (consume_part) and frozen once fitted, so the workspace
    # reads them and calls nothing.
    "fix.field.order.part": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
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
    "fix.work.order": {
        "order": "id desc",
        "limit": 200,
        # action_assign: the dispatcher-only way to name a slot's technician
        # (it checks the dispatcher group itself and sets the slot Assigned)
        "actions": {"action_assign", "action_request_certification_waiver"},
    },
    "fix.geofence": {
        "order": "id",
        "limit": 100,
        "actions": set(),
    },
    "fix.offline.idempotency.ledger": {
        # Offline Sync Monitor (registry screen M02-offline): the P02 app's
        # command journal — replay status and conflicts, read-only.
        "order": "client_created_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    # M02 capture audit (2026-11-18): the six capture registers. Each model
    # checks who may write it; the workspace saves them through their forms.
    "fix.dispatch.decision": {"order": "decided_at desc, id desc", "limit": 200, "actions": set()},
    "fix.technician.device": {
        "order": "state, enrolled_at desc, id desc",
        "limit": 200,
        "actions": {"action_revoke"},
    },
    "fix.offline.conflict.review": {
        "order": "reviewed_at desc, id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.tracking.pause": {
        "order": "started_at desc, id desc",
        "limit": 200,
        "actions": {"action_end"},
    },
    "fix.field.visit.exception": {
        "order": "recorded_at desc, id desc",
        "limit": 200,
        # A02 ERP audit pass 2 M02-12 (D21): a dispatcher waives the fee
        "actions": {"action_waive_fee"},
    },
    "fix.field.cash.recon": {
        "order": "recon_date desc, id desc",
        "limit": 200,
        "actions": {"action_submit", "action_confirm"},
    },
    # fix.workshop.evidence (Field Evidence Hub) is already surfaced by the
    # M31 workshop module in this same area's SURFACES — declaring it twice
    # raises "declared by two modules", so M02's screen reads that surface.
}

_ACTIVE_FIELD_STATES = ("dispatched", "accepted", "en_route", "arrived", "in_progress")
_OPEN_FIELD_STATES = (*_ACTIVE_FIELD_STATES, "draft", "pending_dispatch", "declined")


def _field(env):
    return env["fix.field.order"].sudo().with_context(lang="en_US")


LOCAL_TZ = "Asia/Dhaka"


def _dhaka_day_bounds(env, day=None):
    """(day, start, end): the Dhaka business day as naive-UTC datetimes, the
    frame the ORM stores. ``day`` defaults to today in Dhaka."""
    tz = pytz.timezone(env.context.get("tz") or env.user.tz or LOCAL_TZ)
    if day is None:
        day = datetime.datetime.now(pytz.utc).astimezone(tz).date()
    start = tz.localize(datetime.datetime.combine(day, datetime.time.min)).astimezone(pytz.utc)
    end = start + datetime.timedelta(days=1)
    return day, start.replace(tzinfo=None), end.replace(tzinfo=None)


def kpis(env):
    """The M02 module-tile KPI row — measured off the real field tables.

    A02 ERP audit M02-F21: the completed set was the first 500 rows in the
    model's default order (priority, schedule), not the last week's; the
    unassigned count included drafts nobody had submitted; an order with no
    scheduled start counted as a late arrival; and "now" was the server's
    local clock compared with UTC stamps."""
    FieldOrder = _field(env)
    company_domain = [("company_id", "in", env.companies.ids)]
    now = fields.Datetime.now()
    week_ago = now - datetime.timedelta(days=7)

    # Jobs / Tech / Day: completed field jobs per active technician, last 7 days
    recent = FieldOrder.search(
        [
            *company_domain,
            ("state", "=", "completed"),
            ("technician_id", "!=", False),
            ("completed_at", ">=", week_ago),
        ]
    )
    active_techs = len(
        set(
            FieldOrder.search(
                [
                    *company_domain,
                    ("state", "in", _ACTIVE_FIELD_STATES),
                    ("technician_id", "!=", False),
                ]
            ).technician_id.ids
        )
        | set(recent.technician_id.ids)
    )
    jobs_tech_day = round(len(recent) / max(active_techs, 1) / 7.0, 1) if recent else 0.0

    # on time = arrived at or before the scheduled start; only an order that
    # HAD a scheduled start can be on time or late
    measured = [
        *company_domain,
        ("state", "not in", ("draft", "cancelled")),
        ("arrived_at", "!=", False),
        ("scheduled_start", "!=", False),
    ]
    arrived = FieldOrder.search_count(measured)
    on_time = FieldOrder.search_count([*measured, ("on_time_arrival", "=", True)])

    # travel share over the last week's completed jobs: travel vs (travel +
    # on-site), on-site from started_work_at to completed_at
    travel_total = onsite = 0.0
    for fo in recent:
        if fo.actual_travel_minutes > 0:
            travel_total += fo.actual_travel_minutes
        if fo.started_work_at and fo.completed_at:
            onsite += max(0.0, (fo.completed_at - fo.started_work_at).total_seconds() / 60.0)
    travel_share = (
        round(100.0 * travel_total / (travel_total + onsite), 1)
        if (travel_total + onsite)
        else None
    )

    # waiting for a dispatcher for more than 15 minutes: submitted (or
    # returned) to the queue, never a draft nobody has submitted
    cutoff = now - datetime.timedelta(minutes=15)
    aged_15m = FieldOrder.search_count(
        [
            *company_domain,
            ("state", "in", ("pending_dispatch", "declined")),
            "|",
            ("dispatch_requested_at", "<", cutoff),
            "&",
            ("dispatch_requested_at", "=", False),
            ("write_date", "<", cutoff),
        ]
    )

    Ledger = env["fix.offline.idempotency.ledger"].sudo()
    applied = Ledger.search_count([*company_domain, ("status", "=", "applied")])
    total_ledger = Ledger.search_count(company_domain)

    dispatched_orders = FieldOrder.search_count(
        [*company_domain, ("state", "in", (*_ACTIVE_FIELD_STATES, "completed"))]
    )
    # Nothing measured is None (the tile says "no activity"). These four used
    # to fall back to 84.5 / 91.5 / 32.7 / 100.0, shown as "Live from Odoo" on
    # fix_real with no field order at all (M02 capture audit, 2026-11-12).
    # KPI-013 "automatic assignment rate": automatic dispatches / dispatches.
    # Every dispatch is a dispatcher's choice from the suggestion engine (no
    # automatic dispatch exists, FR-FSM-002), so the rate is 0 % once there
    # are dispatches. It was assigned / dispatched, which is 100 % by
    # construction (a dispatched order always has a technician).
    auto_assignment = 0.0 if dispatched_orders else None

    return {
        "jobs_tech_day": jobs_tech_day,
        "auto_assignment": auto_assignment,
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
            [
                ("company_id", "in", env.companies.ids),
                ("technician_id", "=", tech.id),
                ("state", "not in", ("draft", "cancelled")),
            ]
        )
        travel = max(0.0, sum(orders.mapped("actual_travel_minutes")))
        onsite = 0.0
        for fo in orders:
            if fo.started_work_at and fo.completed_at and fo.state == "completed":
                diff = (fo.completed_at - fo.started_work_at).total_seconds() / 60.0
                if diff > 0:
                    onsite += diff
        total_time = travel + onsite
        util_pct = round(100.0 * onsite / total_time, 1) if total_time > 0 else None
        rows.append(
            {
                "technician": tech.name,
                "jobs": len(orders),
                "completed": sum(1 for fo in orders if fo.state == "completed"),
                "travel_min": round(travel),
                "onsite_min": round(onsite),
                "utilization_pct": util_pct if util_pct is not None else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["jobs"])
    return {
        "title": "Technician Utilization & Travel Time",
        "cols": ["technician", "jobs", "completed", "travel_min", "onsite_min", "utilization_pct"],
        "labels": {
            "technician": "Technician",
            "jobs": "Assigned Jobs",
            "completed": "Completed Jobs",
            "travel_min": "Travel Time (min)",
            "onsite_min": "On-Site Work (min)",
            "utilization_pct": "On-Site Utilization %",
        },
        "rows": rows,
        "notes": [
            "Travel time runs from leaving for the job to arriving on site; on-site time "
            "from starting work to completing it, both from the technician's verified journey."
        ],
    }


def _geofence_delay_report(env, date_from=None, date_to=None, **params):
    """Geofence Breach & Delay Log, from the arrivals themselves.

    A02 ERP audit pass 2 X5-18: the log read a 'geofence.breach.detected'
    event nothing ever publishes, filled the gaps with made-up territory,
    technician and '+20 min' text, and listed every company's declines. It
    now lists the field orders of the viewer's companies (and the period)
    whose arrival was NOT proven by a fence: checked in under a dispatcher's
    waiver, recorded outside the order's fence, or with no fence at all, and
    how late the arrival was against the appointment window."""
    from odoo.addons.cd_field_service.models.fix_field_order import _point_in_fence

    FieldOrder = _field(env)
    orders = FieldOrder.search(
        [
            ("company_id", "in", env.companies.ids),
            ("arrived_at", "!=", False),
            *_period_domain(env, "arrived_at", date_from, date_to),
        ],
        order="arrived_at desc, id desc",
    )
    rows = []
    for fo in orders:
        fences = fo._fix_arrival_fences()
        has_pos = bool(fo.arrival_latitude or fo.arrival_longitude)
        inside = has_pos and any(
            _point_in_fence(f, fo.arrival_latitude, fo.arrival_longitude) for f in fences
        )
        if fo.geofence_waived_by:
            kind = "Arrival under dispatcher waiver"
            detail = "Waived by %s: %s" % (fo.geofence_waived_by.name, fo.geofence_waive_reason)
        elif fences and not inside:
            kind = "Arrival outside the geofence"
            detail = "Checked in at %.5f, %.5f" % (fo.arrival_latitude, fo.arrival_longitude)
        elif not fences:
            kind = "Arrival with no geofence"
            detail = (
                "Checked in at %.5f, %.5f" % (fo.arrival_latitude, fo.arrival_longitude)
                if has_pos
                else "No position recorded"
            )
        else:
            continue
        due = fo.scheduled_end or fo.scheduled_start
        late = round((fo.arrived_at - due).total_seconds() / 60.0) if due else None
        rows.append(
            {
                "event_type": kind,
                "ref": fo.name,
                "territory": fo.zone_id.name or "",
                "technician": fo.technician_id.name or "",
                "detail": detail,
                "delay": ("+%d min" % late) if late and late > 0 else ("on time" if due else ""),
                "at": str(fo.arrived_at)[:16],
            }
        )
    return {
        "title": "Geofence Breach & Delay Log",
        "cols": ["event_type", "ref", "territory", "technician", "detail", "delay", "at"],
        "labels": {
            "event_type": "Arrival",
            "ref": "Field Order",
            "territory": "Zone",
            "technician": "Technician",
            "detail": "Detail",
            "delay": "Late Against Window",
            "at": "Arrived At (UTC)",
        },
        "rows": rows,
        "notes": [
            "Arrivals a geofence did not prove: under a dispatcher's waiver, outside the "
            "order's fence, or where no fence was drawn. Lateness is against the end of the "
            "appointment window."
        ],
        "empty": "Every arrival in the period was inside its geofence.",
    }


def _dispatch_performance_report(env, **params):
    """Dispatch Performance by Zone: what the dispatch desk actually achieved per
    zone, measured from the field order's own timestamps — dispatched, accepted,
    mean acceptance time, on-time arrival, actual travel minutes and declines.
    A zone with no dispatched job shows no mean, never a zero."""
    FieldOrder = _field(env)
    zones = env["fix.zone"].sudo().search([])
    rows = []
    for zone in zones:
        mine = FieldOrder.search(
            [("company_id", "in", env.companies.ids), ("zone_id", "=", zone.id)]
        )
        dispatched = mine.filtered(lambda o: o.dispatched_at)
        accepted = [o for o in dispatched if o.accepted_at]
        waits = [
            (o.accepted_at - o.dispatched_at).total_seconds() / 60.0
            for o in accepted
            if o.accepted_at and o.dispatched_at
        ]
        completed = mine.filtered(lambda o: o.state == "completed")
        on_time = len(completed.filtered(lambda o: o.on_time_arrival))
        travels = [o.actual_travel_minutes for o in mine if o.actual_travel_minutes]
        rows.append(
            {
                "zone": zone.name,
                "jobs": len(mine),
                "dispatched": len(dispatched),
                "accepted": len(accepted),
                "avg_accept_min": round(sum(waits) / len(waits), 1) if waits else None,
                "completed": len(completed),
                "on_time_pct": round(100.0 * on_time / len(completed), 1) if completed else None,
                "avg_travel_min": round(sum(travels) / len(travels), 1) if travels else None,
                "declines": len(mine.filtered(lambda o: o.decline_reason)),
            }
        )
    rows.sort(key=lambda r: -r["jobs"])
    total_jobs = sum(r["jobs"] for r in rows)
    return {
        "title": "Dispatch Performance by Zone - %d job(s) across %d zone(s)"
        % (total_jobs, len(rows)),
        "cols": [
            "zone",
            "jobs",
            "dispatched",
            "accepted",
            "avg_accept_min",
            "completed",
            "on_time_pct",
            "avg_travel_min",
            "declines",
        ],
        "labels": {
            "zone": "Zone",
            "jobs": "Jobs",
            "dispatched": "Dispatched",
            "accepted": "Accepted",
            "avg_accept_min": "Mean accept (min)",
            "completed": "Completed",
            "on_time_pct": "On-time %",
            "avg_travel_min": "Mean travel (min)",
            "declines": "Declines",
        },
        "rows": rows,
        "notes": [
            "Acceptance time is the time from dispatch until the technician accepted the "
            "job. On-time % covers completed jobs only; a zone with no completed job shows "
            "no percentage rather than 100%."
        ],
        "empty": "No field orders in any zone yet.",
    }


def _zone_workload_report(env, **params):
    """Territory Workload Balance: open field orders per dispatch zone."""
    FieldOrder = _field(env)
    zones = env["fix.zone"].sudo().search([])
    rows = []
    for zone in zones:
        open_jobs = FieldOrder.search_count(
            [
                ("company_id", "in", env.companies.ids),
                ("zone_id", "=", zone.id),
                ("state", "in", _OPEN_FIELD_STATES),
            ]
        )
        unassigned = FieldOrder.search_count(
            [
                ("company_id", "in", env.companies.ids),
                ("zone_id", "=", zone.id),
                ("state", "in", ("draft", "pending_dispatch", "declined")),
            ]
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


def _period_domain(env, field, date_from=None, date_to=None):
    """``field`` within the Dhaka days date_from..date_to (both optional)."""
    domain = []
    if date_from:
        day = fields.Date.to_date(date_from)
        domain.append((field, ">=", _dhaka_day_bounds(env, day)[1]))
    if date_to:
        day = fields.Date.to_date(date_to)
        domain.append((field, "<", _dhaka_day_bounds(env, day)[2]))
    return domain


_PAY_STATUS = {
    "pending_handover": "Cash still with the technician",
    "pending_acceptance": "Cash declared, awaiting the branch cashier",
    "pending_settlement": "Settlement not recorded on the service order",
}


def _field_pay_status(fo):
    """The reconciliation status of one field order's own collection."""
    if fo.onsite_payment_state == "settled":
        order = fo.order_id
        if order and order.settlement_verified:
            return "Reconciled (verified by %s)" % (order.settlement_verified_by.name or "-")
        return "Recorded on the service order, not yet verified"
    if fo.onsite_payment_state in _PAY_STATUS:
        return _PAY_STATUS[fo.onsite_payment_state]
    if fo.onsite_payment_method == "corporate_credit":
        return "Billed on corporate credit"
    return "No on-site collection"


def _field_pay_report(env, date_from=None, date_to=None, **params):
    """On-Site Payment Reconciliation, from each completed field order's OWN
    collection: what was collected, how, its TrxID or drawer, and where the
    money stands.

    A02 ERP audit M02-F14: the report took the customer's last five AR
    receipts of ANY order and called the field order "Reconciled" when they
    added up to its estimate, so a customer's earlier payments reconciled a
    job whose cash never left the technician."""
    FieldOrder = _field(env)
    completed = FieldOrder.search(
        [
            ("company_id", "in", env.companies.ids),
            ("state", "=", "completed"),
            *_period_domain(env, "completed_at", date_from, date_to),
        ],
        order="completed_at desc, id desc",
        limit=500,
    )
    methods = dict(FieldOrder._fields["onsite_payment_method"].selection)
    rows = []
    for fo in completed:
        order = fo.order_id
        if fo.onsite_payment_method == "cash":
            reference = (
                "Cash shift #%s" % fo.cash_shift_id.id if fo.cash_shift_id else "COD/%s" % fo.name
            )
        else:
            reference = fo.onsite_payment_trx_id or "-"
        rows.append(
            {
                "field_order": fo.name,
                "service_order": order.name if order else "-",
                "customer": order.customer_id.name if order and order.customer_id else "-",
                "amount": round(fo.onsite_collection_amount or 0.0, 2),
                "method": methods.get(fo.onsite_payment_method, fo.onsite_payment_method or "-"),
                "receipt": reference,
                "status": _field_pay_status(fo),
                "completed_at": str(fo.completed_at or "")[:16],
            }
        )
    open_cash = round(
        sum(
            r["amount"]
            for r, fo in zip(rows, completed, strict=True)
            if fo.onsite_payment_state in ("pending_handover", "pending_acceptance")
        ),
        2,
    )
    return {
        "title": "On-Site Payment Reconciliation - BDT %.2f of field cash not yet in a drawer"
        % open_cash,
        "cols": [
            "field_order",
            "service_order",
            "customer",
            "amount",
            "method",
            "receipt",
            "status",
            "completed_at",
        ],
        "labels": {
            "field_order": "Field Order",
            "service_order": "Service Order",
            "customer": "Customer",
            "amount": "Collected On Site (BDT)",
            "method": "Channel",
            "receipt": "TrxID / Drawer",
            "status": "Reconciliation",
            "completed_at": "Completed At",
        },
        "rows": rows,
        "notes": [
            "Each row is the field order's own collection. Cash is reconciled when a cashier "
            "of the service order's branch has accepted it into that branch's drawer and the "
            "service order's settlement is verified; an MFS collection when its TrxID is "
            "verified on the service order.",
        ],
        "empty": "No completed field orders in scope.",
    }


def _travel_time_report(env, **params):
    """Travel-Time Analysis: per technician, measured travel minutes against
    on-site minutes from the real dispatch timestamps (no estimates)."""
    FieldOrder = _field(env)
    techs = FieldOrder.search(
        [("company_id", "in", env.companies.ids), ("technician_id", "!=", False)]
    ).mapped("technician_id")
    rows = []
    for tech in techs:
        jobs = FieldOrder.search(
            [
                ("company_id", "in", env.companies.ids),
                ("technician_id", "=", tech.id),
                ("state", "=", "completed"),
            ]
        )
        if not jobs:
            continue
        travel = sum(jobs.mapped("actual_travel_minutes") or [0.0])
        onsite = 0.0
        for fo in jobs:
            if fo.started_work_at and fo.completed_at:
                onsite += max(0.0, (fo.completed_at - fo.started_work_at).total_seconds() / 60.0)
        total = travel + onsite
        rows.append(
            {
                "technician": tech.name,
                "jobs": len(jobs),
                "travel_min": round(travel, 1),
                "onsite_min": round(onsite, 1),
                "travel_share": round(100.0 * travel / total, 1) if total else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["travel_min"])
    return {
        "title": "Travel-Time Analysis",
        "cols": ["technician", "jobs", "travel_min", "onsite_min", "travel_share"],
        "labels": {
            "technician": "Technician",
            "jobs": "Completed Jobs",
            "travel_min": "Travel (min)",
            "onsite_min": "On-site (min)",
            "travel_share": "Travel Share %",
        },
        "rows": rows,
        "notes": [
            "Travel minutes are the actual travel time recorded on each dispatch; on-site "
            "minutes run from the start of work to completion. Nothing is estimated."
        ],
        "empty": "No completed field jobs yet.",
    }


def _jobs_per_technician_report(env, **params):
    """Jobs per Technician — completed vs open field jobs per technician."""
    FieldOrder = _field(env)
    techs = FieldOrder.search(
        [("company_id", "in", env.companies.ids), ("technician_id", "!=", False)]
    ).mapped("technician_id")
    rows = []
    for tech in techs:
        base = [("company_id", "in", env.companies.ids), ("technician_id", "=", tech.id)]
        done = FieldOrder.search_count([*base, ("state", "=", "completed")])
        open_jobs = FieldOrder.search_count([*base, ("state", "in", _OPEN_FIELD_STATES)])
        if not (done or open_jobs):
            continue
        on_time = FieldOrder.search_count([*base, ("on_time_arrival", "=", True)])
        rows.append(
            {
                "technician": tech.name,
                "open": open_jobs,
                "completed": done,
                "total": open_jobs + done,
                "on_time": on_time,
            }
        )
    rows.sort(key=lambda r: -r["total"])
    return {
        "title": "Jobs per Technician",
        "cols": ["technician", "open", "completed", "total", "on_time"],
        "labels": {
            "technician": "Technician",
            "open": "Open Jobs",
            "completed": "Completed",
            "total": "Total",
            "on_time": "On-Time Arrivals",
        },
        "rows": rows,
        "notes": [
            "Live counts of field jobs; a job is on time when the technician arrived within "
            "the promised window."
        ],
        "empty": "No technician-assigned field jobs.",
    }


def _field_exceptions_report(env, date_from=None, date_to=None, **params):
    """Field Exception Summary — declined dispatches, failed visits (by type,
    zone and technician, with the wasted-visit fee) and cancellations.

    A02 ERP audit pass 2 M02-12: failed visits (the customer absent, no
    access, cannot complete) were not in the report at all."""
    FieldOrder = _field(env)
    company = [("company_id", "in", env.companies.ids)]
    Decline = env["fix.field.decline.log"].sudo()
    declining = {}
    for log in Decline.search([*company, *_period_domain(env, "create_date", date_from, date_to)]):
        reason = dict(log._fields["reason"].selection).get(log.reason, log.reason or "other")
        declining[reason] = declining.get(reason, 0) + 1
    rows = [
        {"exception": "Declined dispatch: %s" % reason, "zone": "", "technician": "", "count": n}
        for reason, n in sorted(declining.items(), key=lambda kv: -kv[1])
    ]
    Visit = env["fix.field.visit.exception"].sudo()
    labels = dict(Visit._fields["exception_type"].selection)
    failed = {}
    for v in Visit.search([*company, *_period_domain(env, "recorded_at", date_from, date_to)]):
        key = (
            labels.get(v.exception_type, v.exception_type),
            v.zone_id.name or "",
            v.technician_id.name or "",
        )
        row = failed.setdefault(key, {"count": 0, "fee": 0.0, "waived": 0.0})
        row["count"] += 1
        if v.fee_waived_by_id:
            row["waived"] += v.wasted_fee_bdt
        else:
            row["fee"] += v.wasted_fee_bdt
    for (kind, zone, tech), v in sorted(failed.items(), key=lambda kv: -kv[1]["count"]):
        rows.append(
            {
                "exception": "Failed visit: %s" % kind,
                "zone": zone,
                "technician": tech,
                "count": v["count"],
                "fee": round(v["fee"], 2) or None,
                "waived": round(v["waived"], 2) or None,
            }
        )
    cancelled = FieldOrder.search_count(
        [
            *company,
            ("state", "=", "cancelled"),
            *_period_domain(env, "write_date", date_from, date_to),
        ]
    )
    rows.append(
        {"exception": "Cancelled field orders", "zone": "", "technician": "", "count": cancelled}
    )
    return {
        "title": "Field Exception Summary",
        "cols": ["exception", "zone", "technician", "count", "fee", "waived"],
        "labels": {
            "exception": "Exception",
            "zone": "Zone",
            "technician": "Technician",
            "count": "Occurrences",
            "fee": "Wasted-Visit Fee (BDT)",
            "waived": "Fee Waived (BDT)",
        },
        "rows": rows,
        "notes": [
            "Declines are the jobs technicians turned down, with their recorded reason; failed "
            "visits are grouped by what happened, zone and technician, with the wasted-visit "
            "fee charged or waived (D21); cancellations are field jobs that were cancelled."
        ],
        "empty": "No field exceptions recorded.",
    }


def _van_stock_report(env, **params):
    """Van Stock Variance — the technician's van count against what the ledger
    expected (fix.stock.van.recon: expected vs counted, variance computed by the
    model), with the parts consumed on that van's field jobs beside it.

    A report called *Variance* must show a variance: the recon record supplies
    it. Where no count has been taken yet the pack says so instead of presenting
    consumption as if it were a variance."""
    Recon = env["fix.stock.van.recon"].sudo()
    # A02 ERP audit M02-F14: the parts used on VAN jobs are the field order's
    # own fitted lines (fix.field.order.part), counted against the van they
    # were issued from. It read the bench's fix.work.order.part, which never
    # leaves a van.
    Part = env["fix.field.order.part"].sudo()
    company = [("company_id", "in", env.companies.ids)]
    cons = {}
    for line in Part.search([*company, ("state", "=", "consumed")]):
        van = line.van_location_id or line.field_order_id.van_location_id
        key = van.id if van else 0
        row = cons.setdefault(key, {"qty": 0.0, "value": 0.0})
        row["qty"] += line.quantity or 0.0
        row["value"] += line.subtotal or 0.0
    rows = []
    for rec in Recon.search(company, order="recon_date desc, id desc", limit=300):
        used = cons.get(rec.location_id.id, {"qty": 0.0, "value": 0.0})
        rows.append(
            {
                "recon": rec.name,
                "date": str(rec.recon_date or ""),
                "technician": rec.technician_id.name if rec.technician_id else "Unassigned",
                "expected": round(rec.expected_qty or 0.0, 2),
                "counted": round(rec.counted_qty or 0.0, 2),
                "variance": round(rec.variance or 0.0, 2),
                "consumed_qty": round(used["qty"], 2),
                "consumed_value": round(used["value"], 2),
                "state": dict(rec._fields["state"].selection).get(rec.state, rec.state),
            }
        )
    if not rows:
        return {
            "title": "Van Stock Variance - no van count recorded",
            "cols": ["recon", "date", "technician", "expected", "counted", "variance"],
            "labels": {
                "recon": "Count",
                "date": "Date",
                "technician": "Technician",
                "expected": "Expected",
                "counted": "Counted",
                "variance": "Variance",
            },
            "rows": [],
            "notes": [
                "No van stock count has been taken yet. Parts used alone are not a "
                "variance, so none is shown until a count is taken."
            ],
            "empty": "No van stock count recorded.",
        }
    total_var = round(sum(r["variance"] for r in rows), 2)
    return {
        "title": "Van Stock Variance - %d count(s), net variance %s" % (len(rows), total_var),
        "cols": [
            "recon",
            "date",
            "technician",
            "expected",
            "counted",
            "variance",
            "consumed_qty",
            "consumed_value",
            "state",
        ],
        "labels": {
            "recon": "Count",
            "date": "Date",
            "technician": "Technician",
            "expected": "Expected (pcs)",
            "counted": "Counted (pcs)",
            "variance": "Variance (pcs)",
            "consumed_qty": "Consumed Qty",
            "consumed_value": "Consumed Value (BDT)",
            "state": "State",
        },
        "rows": rows,
        "totals": {"recon": "Net", "variance": total_var},
        "notes": [
            "Variance is the counted quantity less the expected quantity on each van count. "
            "Parts used are the parts fitted on field jobs from the same van (the field "
            "order's own part lines); they show use, not loss."
        ],
        "empty": "No van stock count recorded.",
    }


def _crews_report(env, **params):
    """Crews & Multi-Tech Jobs: service orders that carry more than one work-order
    technician (the only crew evidence the data model holds). One row per service
    order, with the distinct technicians and their work orders."""
    WO = (
        env["fix.work.order"]
        .sudo()
        .search([("company_id", "in", env.companies.ids), ("technician_id", "!=", False)])
    )
    grouped = {}
    for wo in WO:
        order = wo.order_id
        if not order:
            continue
        entry = grouped.setdefault(
            order.id,
            {
                "service_order": order.name,
                "customer": order.customer_id.name if order.customer_id else "-",
                "work_orders": 0,
                "technicians": {},
            },
        )
        entry["work_orders"] += 1
        entry["technicians"][wo.technician_id.id] = wo.technician_id.name
    rows = []
    for _oid, e in grouped.items():
        if len(e["technicians"]) < 2:
            continue
        rows.append(
            {
                "service_order": e["service_order"],
                "customer": e["customer"],
                "technicians": len(e["technicians"]),
                "crew": ", ".join(sorted(e["technicians"].values())),
                "work_orders": e["work_orders"],
            }
        )
    rows.sort(key=lambda r: -r["technicians"])
    return {
        "title": "Crews & Multi-Tech Jobs - %d service order(s) with 2+ technicians" % len(rows),
        "cols": ["service_order", "customer", "technicians", "crew", "work_orders"],
        "labels": {
            "service_order": "Service Order",
            "customer": "Customer",
            "technicians": "Technicians",
            "crew": "Crew",
            "work_orders": "Work Orders",
        },
        "rows": rows,
        "notes": [
            "A crew is measured, not declared: a service order counts as a multi-tech "
            "job when it carries work orders for two or more distinct technicians. "
            "Single-technician orders are not listed."
        ],
        "empty": "No service order currently carries more than one technician.",
    }


def _day_queue_report(env, **_params):
    """Day / Job Queue Preview — today's field orders by technician, in
    scheduled order (the P02 app's day view, server-side)."""
    FieldOrder = _field(env)
    # A02 ERP audit M02-F21: the server's date and naive midnights, not the
    # Dhaka day (a 05:00 Dhaka visit fell on the previous UTC day)
    today, start, end = _dhaka_day_bounds(env)
    tz = pytz.timezone(env.context.get("tz") or env.user.tz or LOCAL_TZ)
    orders = FieldOrder.search(
        [
            ("company_id", "in", env.companies.ids),
            ("scheduled_start", ">=", start),
            ("scheduled_start", "<", end),
        ],
        order="technician_id, scheduled_start, id",
    )
    rows = [
        {
            "scheduled": pytz.utc.localize(o.scheduled_start).astimezone(tz).strftime("%H:%M"),
            "technician": o.technician_id.name or "Unassigned",
            "field_order": o.name,
            "service_order": o.order_id.name if o.order_id else "—",
            "zone": o.zone_id.name or "—",
            "priority": o.priority,
            "state": o.state,
        }
        for o in orders
    ]
    return {
        "title": "Day / Job Queue — %s" % today,
        "cols": [
            "scheduled",
            "technician",
            "field_order",
            "service_order",
            "zone",
            "priority",
            "state",
        ],
        "labels": {
            "scheduled": "Time",
            "technician": "Technician",
            "field_order": "Field Order",
            "service_order": "Service Order",
            "zone": "Zone",
            "priority": "Priority",
            "state": "State",
        },
        "rows": rows,
        "notes": [
            "Today's scheduled field orders in time order — the same queue the P02 "
            "technician app renders offline."
        ],
        "empty": "No field jobs scheduled today.",
    }


def _cash_recon_report(env, date_from=None, date_to=None, **_params):
    """Daily Cash Reconciliation — per TECHNICIAN (FR-FSM-056, BRU-FSM-07).

    A02 ERP audit pass 2 M02-11: the screen listed the branch cash shifts,
    so no technician's field cash was ever reconciled on it. It now lists
    each technician's reconciled days (fix.field.cash.recon) and, for every
    technician who still holds field cash, a row of what is outstanding and
    whether it is past the hand-in deadline (D20)."""
    company = [("company_id", "in", env.companies.ids)]
    Recon = env["fix.field.cash.recon"].sudo()
    rows = []
    for r in Recon.search(
        [*company, *_period_domain(env, "create_date", date_from, date_to)],
        order="recon_date desc, id desc",
    ):
        rows.append(
            {
                "date": str(r.recon_date or ""),
                "technician": r.employee_id.name or "",
                "state": r.state,
                "collected": round(r.cash_collected or 0.0, 2),
                "handed_over": round(r.cash_handed_over or 0.0, 2),
                "outstanding": round(r.cash_outstanding or 0.0, 2),
                "counted": round(r.counted_amount or 0.0, 2),
                "variance": round(r.variance or 0.0, 2),
                "overdue": "",
                "confirmed_by": r.confirmed_by_id.name or "",
            }
        )
    FieldOrder = _field(env)
    held = FieldOrder.search(
        [
            *company,
            ("onsite_payment_method", "=", "cash"),
            ("onsite_collection_amount", ">", 0),
            ("cash_handed_over_at", "=", False),
            ("state", "in", ("completed", "cancelled")),
        ]
    )
    cutoff = FieldOrder._fix_cash_handin_cutoff()
    by_tech = {}
    for fo in held:
        entry = by_tech.setdefault(fo.technician_id, {"amount": 0.0, "overdue": 0.0})
        entry["amount"] += fo.onsite_collection_amount
        if fo.onsite_collected_at and fo.onsite_collected_at < cutoff:
            entry["overdue"] += fo.onsite_collection_amount
    for tech, v in sorted(by_tech.items(), key=lambda kv: -kv[1]["amount"]):
        rows.append(
            {
                "date": "now",
                "technician": tech.name or "",
                "state": "held",
                "collected": None,
                "handed_over": None,
                "outstanding": round(v["amount"], 2),
                "counted": None,
                "variance": None,
                "overdue": round(v["overdue"], 2) or "",
                "confirmed_by": "",
            }
        )
    return {
        "title": "Daily Cash Reconciliation",
        "cols": [
            "date",
            "technician",
            "state",
            "collected",
            "handed_over",
            "outstanding",
            "counted",
            "variance",
            "overdue",
            "confirmed_by",
        ],
        "labels": {
            "date": "Day",
            "technician": "Technician",
            "state": "Status",
            "collected": "Cash Collected",
            "handed_over": "Handed To A Branch",
            "outstanding": "Still Held",
            "counted": "Counted",
            "variance": "Variance",
            "overdue": "Past Hand-In Deadline",
            "confirmed_by": "Confirmed By",
        },
        "rows": rows,
        "notes": [
            "Each technician's reconciled days, then what every technician still holds now. "
            "Cash not handed to a branch cashier by the end of the next business day blocks "
            "new dispatch (D20); a confirmed shortage is recovered like a rider COD shortage."
        ],
        "empty": "No field cash recorded.",
    }


def _safety_events_report(env, kind="lone_worker", **_params):
    """Field Safety: lone-worker sessions (M59 fix.hse.loneworker) or panic
    alerts (the technician app's panic_sos commands in the offline journal),
    counted by state.

    It used to report a fixed zero and say no safety store existed, after M59
    had built one (bidirectional audit 2026-11-13).
    """
    FieldOrder = _field(env)
    company_domain = [("company_id", "in", env.companies.ids)]
    in_field = FieldOrder.search_count([*company_domain, ("state", "in", _ACTIVE_FIELD_STATES)])
    rows = []
    if kind == "lone_worker":
        title = "Lone-Worker Check-Ins"
        if "fix.hse.loneworker" in env:
            Session = env["fix.hse.loneworker"].sudo()
            labels = dict(Session._fields["state"].selection)
            for state, label in labels.items():
                rows.append(
                    {
                        "event": "Sessions: %s" % label,
                        "count": Session.search_count([*company_domain, ("state", "=", state)]),
                    }
                )
        note = (
            "Lone-worker sessions are opened on the Lone-Worker Check-In screen (M59). A "
            "session past its expected end escalates to the emergency contact and HSE."
        )
    else:
        title = "Panic Alerts"
        Ledger = env["fix.offline.idempotency.ledger"].sudo()
        rows.append(
            {
                "event": "Panic alerts received",
                "count": Ledger.search_count([*company_domain, ("operation", "=", "panic_sos")]),
            }
        )
        note = (
            "A panic alert is sent from the technician app. It escalates the technician's "
            "open lone-worker session and gives every dispatcher and HSE Officer a to-do."
        )
    rows.append({"event": "Technicians in the field now", "count": in_field})
    return {
        "title": title,
        "cols": ["event", "count"],
        "labels": {"event": "Event", "count": "Count"},
        "rows": rows,
        "notes": [note],
        "empty": "No safety events recorded.",
    }


def _ftfr_by_skill_report(env, date_from=None, date_to=None, **params):
    """First-Time Fix Rate by Skill, from real completions only.

    A02 ERP audit pass 2 M02-10: a skill with no jobs showed a fabricated
    92.5 % from invented counts (4 jobs and 3.7 fixes per technician). A first-
    time fix is a field job completed on its first visit (no failed visit on
    it) whose service order did not come back as a rework within its
    warranty. Grouped by the technician's job title; skills with no
    completed job in the period are not listed."""
    FieldOrder = _field(env)
    done = FieldOrder.search(
        [
            ("company_id", "in", env.companies.ids),
            ("state", "=", "completed"),
            ("technician_id", "!=", False),
            *_period_domain(env, "completed_at", date_from, date_to),
        ]
    )
    reworked = set()
    if done:
        Order = env["fix.service.order"].sudo()
        if "rework_of_id" in Order._fields:
            reworked = set(
                Order.search([("rework_of_id", "in", done.order_id.ids)]).rework_of_id.ids
            )
    by_skill = {}
    for fo in done:
        tech = fo.technician_id
        skill = tech.job_title or tech.job_id.name or "(no job title)"
        row = by_skill.setdefault(skill, {"techs": set(), "jobs": 0, "first": 0})
        row["techs"].add(tech.id)
        row["jobs"] += 1
        if not fo.visit_exception_ids and fo.order_id.id not in reworked:
            row["first"] += 1
    rows = []
    for skill, v in by_skill.items():
        pct = round(100.0 * v["first"] / v["jobs"], 1)
        rows.append(
            {
                "skill": skill,
                "tech_count": len(v["techs"]),
                "total_jobs": v["jobs"],
                "first_time_fixes": v["first"],
                "ftfr_pct": pct,
                "sla_target": "85.0%",
                "status": "Compliant" if pct >= 85.0 else "Action Required",
            }
        )
    rows.sort(key=lambda r: -r["ftfr_pct"])
    return {
        "title": "First-Time Fix Rate by Skill",
        "cols": [
            "skill",
            "tech_count",
            "total_jobs",
            "first_time_fixes",
            "ftfr_pct",
            "sla_target",
            "status",
        ],
        "labels": {
            "skill": "Skill (Job Title)",
            "tech_count": "Technicians",
            "total_jobs": "Completed Field Jobs",
            "first_time_fixes": "First-Time Fixes",
            "ftfr_pct": "FTFR %",
            "sla_target": "SLA Benchmark",
            "status": "SLA Status",
        },
        "rows": rows,
        "notes": [
            "A first-time fix is a completed field job with no failed visit whose service "
            "order did not come back as a rework. Only completed jobs count."
        ],
        "empty": "No completed field job in the period.",
    }


REPORTS = {
    "crews": _crews_report,
    # registry report -> function (v2 forensic audit: all six registry reports
    # plus the four original surfaces are served from measured reads)
    "dispatch_by_zone": _dispatch_performance_report,  # Dispatch Performance by Zone
    "dispatch_performance": _dispatch_performance_report,
    "travel_time": _travel_time_report,  # Travel-Time Analysis
    "jobs_per_technician": _jobs_per_technician_report,  # Jobs per Technician
    "field_exceptions": _field_exceptions_report,  # Field Exception Summary
    "van_stock": _van_stock_report,  # Van Stock Variance
    "field_payments": _field_pay_report,  # On-Site Payment Reconciliation
    # supporting surfaces / secondary screens
    "technician_utilization": _utilization_report,
    "ftfr_by_skill": _ftfr_by_skill_report,
    "geofence_delays": _geofence_delay_report,
    "zone_workload": _zone_workload_report,
    "day_queue": _day_queue_report,
    "cash_recon": _cash_recon_report,
    "lone_worker": lambda env, **kw: _safety_events_report(env, kind="lone_worker", **kw),
    "panic_alerts": lambda env, **kw: _safety_events_report(env, kind="panic", **kw),
}


class P03M02Controller(http.Controller):
    """Bespoke M02 dispatch endpoints: the suggestion engine behind the
    dispatch modal and the module KPI row."""

    @http.route("/p03/field/kpis", type="jsonrpc", auth="user", readonly=True)
    def field_kpis(self, **kw):
        _require_internal(request.env)
        try:
            # the viewer's employee: the dispatch board offers a job's next
            # step (accept, travel, arrive, work, complete) only to the
            # technician it is dispatched to - the server refuses anyone else
            return {"M02": kpis(request.env), "me_employee_id": request.env.user.employee_id.id}
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
