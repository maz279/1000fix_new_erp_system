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

from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _require_internal, _user_error

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.service.order": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_intake",
            "action_start_diagnostic",
            "action_request_estimate",
            "action_send_estimate",
            "action_await_approval",
            "action_approve",
            "action_start_repair",
            "action_submit_qc",
            "action_ready",
            "action_deliver",
            "action_mark_settled",
            "action_close",
            "action_cancel",
            "action_resume_order",
            "action_issue_repair_warranty",
            # A02 workflow audit P0 (M01-1/10/12/15, FR-SRM-080): the workflow
            # actions that replaced direct writes of guarded fields
            "action_verify_settlement",
            "action_send_delivery_otp",
            "action_verify_delivery_otp",
            # M04 build (BRU-FRD-05, cd_front_desk): a third-party collector's ID
            "action_verify_collector_id",
            # A02 audit B1: goodwill and zero-charge rework are REQUESTED here
            # and decided from the approver's M63 inbox (the approve methods
            # refuse a direct press, so they are not offered).
            "action_request_goodwill",
            "action_request_rework_approval",
            # A02 audit M01-P2 / B3: comeback within the repair warranty, and
            # the supervisor's deferred hold
            "action_reopen_comeback",
            "action_defer_order",
            "action_change_category",
            "action_override_priority",
            "action_fail_qc",
            "action_mark_unrepairable",
            # A02 ERP audit M01-F8: the customer's unlock code, with consent
            "action_record_passcode",
            # M02 bridge (defined in cd_field_service's extension): hand an
            # on-site order to the dispatch pipeline
            "action_create_field_order",
            # M31 bridge (defined in cd_workshop's extension): hand a bench
            # job order to the workshop pipeline
            "action_create_workshop_job",
            # M03 bridge (defined in cd_consignment's extension): hand a
            # pick&drop order to logistics
            "action_create_consignment",
            # FR-SRM-029: finance's retry of a declined repair's fee invoice
            # (cd_billing_engine; finance managers only)
            "action_invoice_diagnostic_fee",
            # A02 pass 2: supervisor corrections of what is fixed after intake
            # (M01-02/07/15), the refused-repair invoice (D6, cd_billing_engine)
            # and the cashier's confirmation of a rider's COD remittance (D1)
            "action_correct_customer_device",
            "action_correct_lci",
            "action_transfer_branch",
            "action_bill_refused_repair",
            "action_confirm_cod_remitted",
        },
    },
    "fix.estimate": {
        "order": "id desc",
        "limit": 200,
        "actions": {
            # commercial document standard (17 Nov 2026): estimate -> proforma,
            # and its A4 / 80 mm receipt print
            "action_create_proforma",
            "action_fix_print",
            "action_fix_print_receipt",
            "action_send",
            "action_approve",
            # A02 audit B1: the BRU-SRM-08 manager key is requested here and
            # given from the branch manager's M63 inbox.
            "action_request_manager_key",
            "action_dofa_approve",
            # R7: a seller may also route the discount through the M63 inbox.
            "action_request_approval",
            "action_recall_approval",
            "action_reject",
            "action_revise",
            # A02 audit M01-9: the customer's approval is a verified code or
            # a recorded signed estimate, never typed text
            "action_send_customer_otp",
            "action_verify_customer_otp",
            "action_record_signed_approval",
            # A04 audit M36-2 (eq_08): the M36 quotation lifecycle on the
            # estimate; quotation_state is no longer writable.
            "action_quote",
            "action_negotiate",
            "action_accept",
            "action_decline",
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
        "actions": {
            "action_call",
            "action_serving",
            "action_complete",
            "action_evaluate_wait_sla",
            # M04 queue extensions (defined in cd_front_desk's ext file)
            "action_no_show",
            "action_cancel",
            # A02 ERP audit M04-F12: call the next waiting token by priority lane
            "action_call_next",
        },
    },
    "fix.walkin.intake": {
        "order": "id desc",
        "limit": 100,
        "actions": {
            "action_complete_handover",
            # M04 custody-parking step (cd_front_desk ext)
            "action_submit_for_handover",
        },
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
        # verified_by/verified_at shipped readonly with nothing to set them,
        # and 'pending' had no exit (A04 audit, 2026-11-01).
        # A02 audit B1: verification is requested here and decided from the
        # Warranty Officer's M63 inbox.
        "actions": {"action_request_approval", "action_recall_approval", "action_void"},
        # A07 operability M17-8: read as the caller; the row follows its device.
        "rules": True,
        # A07 operability M17: proof is a card or receipt, not any document.
        "pickers": {
            "proof_document_id": [
                ("document_type", "in", ["warranty_card", "invoice", "asset_document"]),
                "|",
                ("res_model", "=", False),
                ("res_model", "in", ["fix.warranty", "fix.device"]),
            ],
        },
    },
    "fix.device.history": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
        "rules": True,
    },
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.sla.item": {
        "order": "policy_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.sla.kpi.instance": {
        "order": "started_at desc, id desc",
        "limit": 300,
        "actions": {"cancel", "pause", "resume", "succeed"},
    },
    # M01 capture audit (2026-11-17): the escalation matrix (FR-SRM-049).
    # Rules are kept by Service Supervisors (ACL); the raised escalations are
    # written by the SLA cron and move only by Acknowledge.
    "fix.escalation.rule": {
        "order": "policy_id, threshold_pct, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.escalation.event": {
        "order": "fired_at desc, id desc",
        "limit": 300,
        "actions": {"action_acknowledge"},
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
# A02 ERP audit M01-F15: resolved = reached Ready (the resolution promise is
# "intake to ready"); Ready, delivered and closed orders are resolved.
_RESOLVED_STATES = ["ready", "delivered", "closed"]
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


# A02 pass 2 (M01-16): the rework rate and the TAT measure the last 30 days
_KPI_WINDOW_DAYS = 30


def _sla_at_risk(env, company_domain):
    """Open orders whose resolution clock is past its WARNING point (the
    policy's warn_at, 80% of the target by default) and still running: at
    risk before it breaches. A02 pass 2 (M01-16): 'at risk' counted orders
    already PAST the deadline - those are breached, not at risk."""
    Instance = env.get("fix.sla.kpi.instance")
    if Instance is None or "warn_at" not in Instance._fields:
        return 0
    order_ids = _orders(env).search([*company_domain, ("state", "in", _OPEN_STATES)]).ids
    if not order_ids:
        return 0
    now = fields.Datetime.now()
    rows = Instance.sudo()._read_group(
        [
            ("res_model", "=", "fix.service.order"),
            ("res_id", "in", order_ids),
            ("kpi_code", "=", "resolution"),
            ("state", "=", "in_progress"),
            ("warn_at", "!=", False),
            ("warn_at", "<=", now),
        ],
        ["res_id"],
        ["__count"],
    )
    return len(rows)


def kpis(env):
    """The M01 module-tile KPI row — same measures the Role Center computes
    (single source: the real fix.service.order/estimate tables).

    A02 pass 2 (M01-16 / X5-17): every measure reads the whole population
    (counts and grouped reads, no limit= cap: TAT read the newest 500
    orders); the rework rate is reworks among the period's DELIVERIES (it
    divided open reworks by open orders); conversion is per ORDER (an order
    revised three times counted three estimates); at-risk reads the SLA
    clock's warning point."""
    Order = _orders(env)
    company_domain = [("company_id", "in", env.companies.ids)]
    now = fields.Datetime.now()
    since = now - datetime.timedelta(days=_KPI_WINDOW_DAYS)

    open_orders = Order.search_count([*company_domain, ("state", "in", _OPEN_STATES)])
    at_risk = _sla_at_risk(env, company_domain)

    # TAT: orders resolved (Ready) within 24h of intake (IT target), over the
    # window. A02 ERP audit M01-F15: measured intake -> Ready.
    resolved_domain = [
        *company_domain,
        ("state", "in", _RESOLVED_STATES),
        ("sla_resolution_at", ">=", since),
        ("intake_completed_at", "!=", False),
    ]
    tat_total = 0
    tat_24 = 0
    for row in Order.search_read(resolved_domain, ["intake_completed_at", "sla_resolution_at"]):
        tat_total += 1
        if (row["sla_resolution_at"] - row["intake_completed_at"]).total_seconds() <= 24 * 3600:
            tat_24 += 1

    # Estimate conversion per order: orders whose estimate the customer
    # decided, and of them the orders with an approved one
    Estimate = env["fix.estimate"].sudo()
    decided_orders = {
        order.id
        for (order,) in Estimate._read_group(
            [
                *company_domain,
                ("order_id", "!=", False),
                ("state", "in", ("approved", "superseded", "rejected", "expired")),
            ],
            ["order_id"],
        )
    }
    approved_orders = {
        order.id
        for (order,) in Estimate._read_group(
            [
                *company_domain,
                ("order_id", "!=", False),
                ("state", "in", ("approved", "superseded")),
            ],
            ["order_id"],
        )
    }
    decided = len(decided_orders)
    approved = len(approved_orders & decided_orders)

    delivered_domain = [
        *company_domain,
        ("state", "in", ("delivered", "closed")),
        ("delivered_at", ">=", since),
    ]
    deliveries = Order.search_count(delivered_domain)
    rework_delivered = Order.search_count([*delivered_domain, ("is_rework", "=", True)])
    delivered_not_closed = Order.search_count([*company_domain, ("state", "=", "delivered")])

    # intake speed: average intake duration in minutes from walk-in intake records
    avg_minutes = None
    Walkin = env.get("fix.walkin.intake")
    if Walkin is not None:
        timed = Walkin.sudo().search([*company_domain, ("intake_duration_seconds", ">", 0)])
        if timed:
            durations = timed.mapped("intake_duration_seconds")
            avg_minutes = round(sum(durations) / (len(durations) * 60.0), 1)

    return {
        "open_orders": open_orders,
        "sla_at_risk": at_risk,
        "tat_under_24h": round(100.0 * tat_24 / tat_total, 1) if tat_total else None,
        "estimate_conversion": round(100.0 * approved / decided, 1) if decided else None,
        "intake_minutes": avg_minutes,
        "rework_rate": round(100.0 * rework_delivered / deliveries, 1) if deliveries else None,
        "delivered_not_closed": delivered_not_closed,
    }


# ---------------------------------------------------------------- reports


def _fmt_day(value):
    return str(value)[:10] if value else ""


def channel_intake_report(env, date_from=None, date_to=None, channel=None, group_by=None, **params):
    """Daily Intake by Channel: real orders grouped by service_type and day.

    Professional-report filters (UX-001): channel scope + day/week/month
    granularity, declared in the payload so the workspace renders them —
    exports carry the same filter values (the export is the screen).
    """
    domain = [("company_id", "in", env.companies.ids)]
    if date_from:
        domain.append(("create_date", ">=", date_from))
    if date_to:
        domain.append(("create_date", "<=", date_to + " 23:59:59"))
    # D10 (M01 audit 2026-11-06): rows, filter options and exports show the
    # selection LABELS — and the pill value rides back as a label, so map it
    # to the key before it reaches the domain.
    service_labels = dict(_orders(env)._fields["service_type"].selection)
    label_to_key = {label: key for key, label in service_labels.items()}
    if channel and channel != "All":
        domain.append(("service_type", "=", label_to_key.get(channel, channel)))

    granularity = group_by if group_by in ("day", "week", "month") else "day"
    rows = []
    grouped = _orders(env)._read_group(
        [*domain, ("service_type", "!=", False)],
        ["service_type", "create_date:%s" % granularity],
        ["__count"],
    )
    for service_type, bucket, count in grouped:
        rows.append(
            {
                "day": bucket if isinstance(bucket, str) else _fmt_day(bucket),
                "service_type": service_labels.get(service_type, service_type),
                "orders": count,
            }
        )
    rows.sort(key=lambda r: (r["day"], r["service_type"]))
    channels = sorted({r["service_type"] for r in rows})
    return {
        "title": "Daily Intake by Channel",
        "cols": ["day", "service_type", "orders"],
        "labels": {
            "day": {"day": "Day", "week": "Week", "month": "Month"}[granularity],
            "service_type": "Channel",
            "orders": "Orders",
        },
        "rows": rows,
        "totals": {"service_type": "Total", "orders": sum(r["orders"] for r in rows)},
        "filters": [
            {"key": "channel", "label": "Channel", "options": ["All", *channels]},
            {"key": "group_by", "label": "Group by", "options": ["day", "week", "month"]},
        ],
        "notes": [
            "Service orders received in the period, counted by intake channel and by %s."
            % granularity
        ],
    }


def wip_ageing_report(env, **params):
    """WIP Ageing by Branch: open WIP orders bucketed by HOURS since intake.

    A02 pass 2 (M01-16): the age was the difference of two UTC calendar days
    (server date.today() and create_date.date()), so an order taken in at
    23:00 was a day old an hour later and the < 24h bucket meant "today in
    UTC". It is the elapsed time since intake now (the same in any zone)."""
    now = fields.Datetime.now()
    domain = [
        ("company_id", "in", env.companies.ids),
        ("state", "in", _WIP_STATES),
    ]
    buckets = {"under_24h": 0, "24_48h": 0, "over_48h": 0}
    by_branch = {}
    for order in _orders(env).search(domain):
        started = order.intake_completed_at or order.create_date or now
        hours = (now - started).total_seconds() / 3600.0
        key = "under_24h" if hours < 24 else ("24_48h" if hours < 48 else "over_48h")
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
        "notes": [
            "Orders still in work (from intake up to a failed quality check), grouped by the "
            "hours since the device was taken in."
        ],
    }


def _dhaka_day_start_utc(day):
    """00:00 of a Dhaka business day as the naive-UTC datetime the ORM stores."""
    import pytz

    tz = pytz.timezone("Asia/Dhaka")
    start = tz.localize(datetime.datetime.combine(fields.Date.to_date(day), datetime.time.min))
    return start.astimezone(pytz.utc).replace(tzinfo=None)


def _period(domain, field, date_from=None, date_to=None):
    """``field`` within the Dhaka days date_from..date_to. The bounds were UTC
    days, so an order resolved between 00:00 and 06:00 Dhaka counted on the
    previous day (A02 ERP review, 20 Nov 2026; M02-M31 already used Dhaka)."""
    if date_from:
        domain.append((field, ">=", _dhaka_day_start_utc(date_from)))
    if date_to:
        end = _dhaka_day_start_utc(date_to) + datetime.timedelta(days=1)
        domain.append((field, "<", end))
    return domain


def sla_compliance_report(env, date_from=None, date_to=None, **params):
    """SLA Compliance: orders resolved (Ready) before their deadline, first
    responses (diagnosis or assignment) before theirs; open orders already
    past the deadline. Measured off the real SLA clock fields.

    A02 ERP audit M01-F15: resolution was read at DELIVERY (and only on
    delivered / closed orders) while the clock it was compared with stops at
    Ready, so the customer's collection delay counted as late repair; the
    response was never reported."""
    Order = _orders(env)
    company_domain = [("company_id", "in", env.companies.ids)]
    resolved_domain = _period(
        [*company_domain, ("state", "in", _RESOLVED_STATES), ("sla_resolution_at", "!=", False)],
        "sla_resolution_at",
        date_from,
        date_to,
    )
    closed = Order.search(resolved_domain, limit=1000)
    met = late = 0
    for order in closed:
        if order.sla_resolution_deadline and order.sla_resolution_at:
            if order.sla_resolution_at <= order.sla_resolution_deadline:
                met += 1
            else:
                late += 1
    responded = Order.search(
        _period(
            [
                *company_domain,
                ("sla_response_at", "!=", False),
                ("sla_response_deadline", "!=", False),
            ],
            "sla_response_at",
            date_from,
            date_to,
        ),
        limit=1000,
    )
    resp_met = sum(1 for o in responded if o.sla_response_at <= o.sla_response_deadline)
    resp_late = len(responded) - resp_met
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
            {"measure": "First response on time", "value": resp_met},
            {"measure": "First response late", "value": resp_late},
        ],
        "notes": [
            "On time means the order was resolved (ready for collection) before its SLA "
            "deadline. The deadline moves later by the time an order spends on hold or "
            "waiting for the customer's decision.",
            "The first response is the start of diagnosis or the technician's assignment, "
            "whichever came first.",
        ],
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
        "notes": [
            "Estimates sent to customers in the period and what became of them. Conversion is "
            "approved estimates as a share of estimates sent."
        ],
    }


def rework_analysis_report(env, **params):
    """Rework & Repeat-Fault Analysis: rework-flagged orders by state and
    device model (BRU-SRM-06 same-device-within-30-days detection)."""
    Order = _orders(env)
    domain = [("company_id", "in", env.companies.ids), ("is_rework", "=", True)]
    rework = Order.search(domain)  # X5-17: the whole population, no cap
    by_state = {}
    by_model = {}
    for order in rework:
        by_state[order.state] = by_state.get(order.state, 0) + 1
        model = order.device_id.device_model_id.name or "—"
        by_model[model] = by_model.get(model, 0) + 1
    # D10 (M01 audit 2026-11-06): state rows carry the selection label, not
    # the raw key (qc_failed → "QC Rework").
    state_labels = dict(Order._fields["state"].selection)
    rows = [
        {"dimension": "state: %s" % state_labels.get(state, state), "orders": count}
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
        "notes": [
            "A rework is a device returned with the same fault within 30 days of an earlier "
            "repair (business rule BRU-SRM-06)."
        ],
    }


def tat_distribution_report(env, date_from=None, date_to=None, **params):
    """Order Cycle-Time (TAT) distribution: hours from intake to resolution
    (Ready) for resolved orders (A02 ERP audit M01-F15: it read start of
    repair to delivery, on closed orders only)."""
    Order = _orders(env)
    closed = Order.search(
        _period(
            [
                ("company_id", "in", env.companies.ids),
                ("state", "in", _RESOLVED_STATES),
                ("sla_resolution_at", "!=", False),
            ],
            "sla_resolution_at",
            date_from,
            date_to,
        ),
        limit=1000,
    )
    buckets = {"< 4h": 0, "4–24h": 0, "24–72h": 0, "> 72h": 0}
    for order in closed:
        if not (order.intake_completed_at and order.sla_resolution_at):
            continue
        hours = (order.sla_resolution_at - order.intake_completed_at).total_seconds() / 3600.0
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
        "labels": {"bucket": "Turnaround", "orders": "Resolved Orders"},
        "rows": [{"bucket": k, "orders": v} for k, v in buckets.items()],
        "notes": [
            "Turnaround time is measured from intake to the moment the device was ready for "
            "collection."
        ],
    }


def uncollected_register_report(env, **params):
    """Uncollected Device Register: repaired devices Ready and not collected,
    oldest first, aged from the moment they became Ready.

    A02 ERP audit M01-F22: the register listed DELIVERED orders (collected:
    not in our custody) and aged every row from its last write, so any edit
    made an old device look new."""
    Order = _orders(env)
    domain = [
        ("company_id", "in", env.companies.ids),
        ("state", "=", "ready"),
    ]
    now = fields.Datetime.now()
    rows = []
    for order in Order.search(domain, order="ready_at asc, id asc", limit=300):
        since = order.ready_at or order.write_date
        rows.append(
            {
                "order": order.name,
                "customer": order.customer_id.name or "—",
                "device": order.device_id.name or order.device_serial or "—",
                "state": order.state,
                "ready_since": _fmt_day(since),
                "days_uncollected": (now - since).days if since else None,
            }
        )
    return {
        "title": "Uncollected Device Register",
        "cols": ["order", "customer", "device", "state", "ready_since", "days_uncollected"],
        "labels": {
            "order": "Order",
            "customer": "Customer",
            "device": "Device",
            "state": "State",
            "ready_since": "Ready Since",
            "days_uncollected": "Days Uncollected",
        },
        "rows": rows,
        "notes": [
            "Devices that are repaired and ready, but have not been collected by the customer."
        ],
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
        "notes": [
            "Every combination of intake channel and order category in the current order book."
        ],
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
        "notes": [
            "These are the approval limits the system applies to every estimate today; "
            "changing them requires the configured approval."
        ],
    }


# The aggregates cd_service_order publishes under (its publish() call sites).
_M01_EVENT_AGGREGATES = ("fix.service.order", "fix.estimate", "fix.sla.kpi.instance")


def domain_events_report(env, **params):
    """Domain Events Published: what M01 has written to the transactional
    outbox, per event type. The sub-module "API & Domain Event Broadcasting"
    had no screen of its own and showed the device-history list. Counts and
    the latest timestamp only - a payload is never read here."""
    Outbox = env["fix.event.outbox"].sudo()
    domain = [
        ("company_id", "in", env.companies.ids),
        ("aggregate", "in", list(_M01_EVENT_AGGREGATES)),
    ]
    by_type = {}
    for event_type, aggregate, status, count, last in Outbox._read_group(
        domain, ["event_type", "aggregate", "status"], ["__count", "create_date:max"]
    ):
        row = by_type.setdefault(
            (event_type, aggregate),
            {
                "event_type": event_type,
                "aggregate": aggregate,
                "total": 0,
                "published": 0,
                "pending": 0,
                "failed": 0,
                "last": None,
            },
        )
        row["total"] += count
        if status in ("published", "pending", "failed"):
            row[status] += count
        if last and (row["last"] is None or last > row["last"]):
            row["last"] = last
    rows = [by_type[key] for key in sorted(by_type)]
    for row in rows:
        # shown in the reader's own time zone, as the lists show a datetime
        row["last"] = (
            fields.Datetime.context_timestamp(env.user, row["last"]).strftime("%Y-%m-%d %H:%M")
            if row["last"]
            else None
        )
    return {
        "title": "Domain Events Published (Outbox)",
        "cols": ["event_type", "aggregate", "total", "published", "pending", "failed", "last"],
        "labels": {
            "event_type": "Event",
            "aggregate": "Record",
            "total": "Events",
            "published": "Published to the Bus",
            "pending": "Waiting in the Outbox",
            "failed": "Failed",
            "last": "Latest Event",
        },
        "rows": rows,
        "notes": [
            "Each change to an order, an estimate or an SLA clock is recorded as an event "
            "and then delivered to the systems that subscribe to it.",
            "A growing number of waiting or failed events means delivery has stopped and "
            "should be reported to IT support.",
        ],
    }


REPORTS = {
    "domain_events": domain_events_report,
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
