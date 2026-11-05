# A12 · M28 Integration, API & Events — surfaces, packs and KPIs over the API
# catalogue, consumers/quotas, event topics/schemas/subscriptions/DLQ, the
# connector framework, connector credentials, sync conflicts and the measured
# integration log.
import datetime

SURFACES = {
    "fix.api.endpoint": {"order": "version desc, code", "limit": 300, "actions": set()},
    "fix.api.consumer": {"order": "name", "limit": 200, "actions": {"action_rotate_key"}},
    "fix.api.quota": {"order": "consumer_id, endpoint_id", "limit": 300, "actions": set()},
    "fix.event.topic": {
        "order": "code",
        "limit": 200,
        "actions": {"action_pause", "action_resume"},
    },
    "fix.event.schema": {
        "order": "code, version desc",
        "limit": 200,
        "actions": {"action_publish"},
    },
    "fix.event.subscription": {
        "order": "topic_id, consumer_id",
        "limit": 300,
        "actions": {"action_pause", "action_resume"},
    },
    "fix.event.dlq": {
        "order": "created_at desc, id desc",
        "limit": 300,
        "actions": {"action_replay", "action_discard"},
    },
    "fix.connector": {
        "order": "connector_type, name",
        "limit": 300,
        "actions": {"action_mark_degraded", "action_mark_live"},
    },
    "fix.connector.credential": {"order": "name", "limit": 200, "actions": set()},
    "fix.sync.conflict": {
        "order": "detected_at desc, id desc",
        "limit": 300,
        "actions": {"action_local_wins", "action_remote_wins", "action_merged"},
    },
    "fix.integration.log": {"order": "created_at desc, id desc", "limit": 500, "actions": set()},
}

# A12 R4 (finding M28-11): what /p03/model/write may set on each M28 surface —
# exactly the fields a workspace form offers as editable. The workflow fields
# (state / resolution / replayed_at / health) are NOT here: they change only
# through the whitelisted actions, which re-check the Integration Admin group
# and audit the privileged ones (replay, discard, rotate, resolve).
# Read-only screens carry an empty tuple:
#   - fix.event.dlq: engine-raised — the cron mirrors the relay's dead
#     deliveries; replay/discard are the only operations;
#   - fix.integration.log: system-written only (P1-6), no group may write it.
WRITABLE = {
    "fix.api.endpoint": (
        "code",
        "name",
        "version",
        "path",
        "method",
        "auth_type",
        "description",
        "active",
    ),
    "fix.api.consumer": ("name", "partner_id", "active"),
    "fix.api.quota": ("consumer_id", "endpoint_id", "requests_per_min", "daily_quota"),
    "fix.event.topic": ("code", "name", "schema_id", "retention_days"),
    "fix.event.schema": ("code", "version", "schema_text"),
    "fix.event.subscription": ("consumer_id", "topic_id", "endpoint_url", "secret_ref"),
    "fix.event.dlq": (),
    "fix.connector": ("name", "connector_type", "endpoint", "credential_id"),
    "fix.connector.credential": ("name", "auth_type", "secret_ref", "expires_on", "active"),
    "fix.sync.conflict": ("device_ref", "res_model", "res_id", "field_name"),
    "fix.integration.log": (),
}


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


def api_usage(env, date_from=None, date_to=None, **params):
    """API usage by consumer: request counts, throttles, failures, p95."""
    logs = env["fix.integration.log"].sudo().search([("kind", "=", "api")])
    groups = {}
    for log in logs:
        key = log.consumer_id.name if log.consumer_id else "Anonymous"
        g = groups.setdefault(
            key, {"total": 0, "success": 0, "throttled": 0, "failed": 0, "latencies": []}
        )
        g["total"] += 1
        g[log.status] = g.get(log.status, 0) + 1
        if log.latency_ms:
            g["latencies"].append(log.latency_ms)
    rows = []
    for key, v in sorted(groups.items(), key=lambda kv: -kv[1]["total"]):
        lat = sorted(v["latencies"])
        p95 = lat[int(len(lat) * 0.95)] if lat else None
        rows.append(
            {
                "consumer": key,
                "requests": v["total"],
                "success": v["success"],
                "throttled": v["throttled"],
                "failed": v["failed"],
                "p95_ms": p95,
            }
        )
    return _pack(
        "API Usage by Consumer",
        ["consumer", "requests", "success", "throttled", "failed", "p95_ms"],
        {
            "consumer": "Consumer",
            "requests": "Requests",
            "success": "Success",
            "throttled": "Throttled",
            "failed": "Failed",
            "p95_ms": "p95 (ms)",
        },
        rows,
        [
            "p95 is computed over the recorded request latencies; a consumer with no latency "
            "records shows an honest dash."
        ],
        totals={
            "consumer": "Total",
            "requests": sum(r["requests"] for r in rows),
            "success": sum(r["success"] for r in rows),
            "throttled": sum(r["throttled"] for r in rows),
            "failed": sum(r["failed"] for r in rows),
        },
        empty="No API requests logged.",
    )


def event_delivery_slo(env, date_from=None, date_to=None, **params):
    """Event delivery SLO: delivered vs failed by topic."""
    logs = env["fix.integration.log"].sudo().search([("kind", "=", "delivery")])
    groups = {}
    for log in logs:
        key = log.topic_code or "unknown"
        g = groups.setdefault(key, {"delivered": 0, "failed": 0})
        if log.status == "success":
            g["delivered"] += 1
        elif log.status == "failed":
            g["failed"] += 1
    rows = []
    for key, v in sorted(groups.items()):
        total = v["delivered"] + v["failed"]
        rows.append(
            {
                "topic": key,
                "delivered": v["delivered"],
                "failed": v["failed"],
                "slo": round(v["delivered"] / total * 100.0, 2) if total else 0.0,
            }
        )
    return _pack(
        "Event Delivery SLO",
        ["topic", "delivered", "failed", "slo"],
        {"topic": "Topic", "delivered": "Delivered", "failed": "Failed", "slo": "Delivery %"},
        rows,
        [
            "Delivery % is successes over successes+failures per topic; throttled deliveries "
            "are excluded from the SLO denominator."
        ],
        totals={
            "topic": "Total",
            "delivered": sum(r["delivered"] for r in rows),
            "failed": sum(r["failed"] for r in rows),
        },
        empty="No event deliveries logged.",
    )


def connector_latency(env, date_from=None, date_to=None, **params):
    """Connector latency and health from the connector register."""
    connectors = env["fix.connector"].sudo().search([])
    rows = []
    for c in connectors:
        rows.append(
            {
                "connector": c.name,
                "type": dict(c._fields["connector_type"].selection).get(c.connector_type),
                "latency_ms": c.last_latency_ms or 0,
                "last_success": str(c.last_success_at or "—")[:19],
                "state": dict(c._fields["state"].selection).get(c.state, c.state),
            }
        )
    rows.sort(key=lambda r: -r["latency_ms"])
    slow = len([r for r in rows if r["latency_ms"] > 1000])
    return _pack(
        "Connector Latency — %d connector(s) above 1s" % slow,
        ["connector", "type", "latency_ms", "last_success", "state"],
        {
            "connector": "Connector",
            "type": "Type",
            "latency_ms": "Last Latency (ms)",
            "last_success": "Last Success",
            "state": "State",
        },
        rows,
        ["Latency is the last recorded probe value on the connector register."],
        empty="No connectors configured.",
    )


def dlq_analysis(env, date_from=None, date_to=None, **params):
    """DLQ analysis: entries by topic and reason."""
    dlqs = env["fix.event.dlq"].sudo().search([])
    groups = {}
    for entry in dlqs:
        key = (entry.topic_code, entry.reason)
        g = groups.setdefault(key, {"count": 0, "pending": 0, "replayed": 0, "discarded": 0})
        g["count"] += 1
        if entry.state == "pending":
            g["pending"] += 1
        elif entry.state == "replayed":
            g["replayed"] += 1
        elif entry.state == "discarded":
            g["discarded"] += 1
    rows = [{"topic": t, "reason": r, **v} for (t, r), v in sorted(groups.items())]
    return _pack(
        "DLQ Analysis",
        ["topic", "reason", "count", "pending", "replayed", "discarded"],
        {
            "topic": "Topic",
            "reason": "Reason",
            "count": "Entries",
            "pending": "Pending",
            "replayed": "Replayed",
            "discarded": "Discarded",
        },
        rows,
        ["Every dead-letter entry keeps its payload and reason; replay is per entry."],
        totals={
            "topic": "Total",
            "count": sum(r["count"] for r in rows),
            "pending": sum(r["pending"] for r in rows),
            "replayed": sum(r["replayed"] for r in rows),
            "discarded": sum(r["discarded"] for r in rows),
        },
        empty="No dead-letter entries.",
    )


def webhook_success(env, date_from=None, date_to=None, **params):
    """Webhook success rate by subscription."""
    subs = env["fix.event.subscription"].sudo().search([])
    logs = env["fix.integration.log"].sudo().search([("kind", "=", "webhook")])
    rows = []
    for sub in subs:
        # M28-12: match attempts on the SUBSCRIPTION, not the consumer - a
        # consumer can hold several subscriptions, and the old consumer_id
        # match only looked right when the two ids happened to coincide.
        sub_logs = logs.filtered(lambda ln, s=sub.id: ln.subscription_id.id == s)
        total = len(sub_logs)
        ok = len(sub_logs.filtered(lambda ln: ln.status == "success"))
        rows.append(
            {
                "subscription": sub.name,
                "topic": sub.topic_id.code if sub.topic_id else "—",
                "url": sub.endpoint_url[:60],
                "attempts": total,
                "success": ok,
                "rate": round(ok / total * 100.0, 1) if total else None,
                "state": dict(sub._fields["state"].selection).get(sub.state, sub.state),
            }
        )
    rows.sort(key=lambda r: -(r["rate"] if r["rate"] is not None else -1))
    return _pack(
        "Webhook Success Rate",
        ["subscription", "topic", "url", "attempts", "success", "rate", "state"],
        {
            "subscription": "Subscription",
            "topic": "Topic",
            "url": "Endpoint URL",
            "attempts": "Attempts",
            "success": "Success",
            "rate": "Success %",
            "state": "State",
        },
        rows,
        [
            "Success % is over recorded webhook attempts; a subscription with no traffic shows "
            "a dash rather than a fabricated rate. Attempts are matched to the subscription "
            "by the log's subscription link (M28-12)."
        ],
        totals={
            "subscription": "Total",
            "attempts": sum(r["attempts"] for r in rows),
            "success": sum(r["success"] for r in rows),
        },
        empty="No event subscriptions configured.",
    )


REPORTS = {
    "api_usage": api_usage,
    "event_delivery_slo": event_delivery_slo,
    "connector_latency": connector_latency,
    "dlq_analysis": dlq_analysis,
    "webhook_success": webhook_success,
}


def kpis(env):
    logs = env["fix.integration.log"].sudo().search([("kind", "=", "api")])
    deliveries = env["fix.integration.log"].sudo().search([("kind", "=", "delivery")])
    dlq = env["fix.event.dlq"].sudo().search([("state", "=", "pending")])
    connectors = env["fix.connector"].sudo().search([])
    today = datetime.date.today()
    conflicts = (
        env["fix.sync.conflict"]
        .sudo()
        .search(
            [
                ("detected_at", ">=", str(today) + " 00:00:00"),
            ]
        )
    )
    lat = sorted([ln.latency_ms for ln in logs if ln.latency_ms])
    p95 = lat[int(len(lat) * 0.95)] if lat else 0
    live = len(connectors.filtered(lambda c: c.state == "live"))
    delivered_ok = len(deliveries.filtered(lambda ln: ln.status == "success"))
    return {
        "api_p95": p95,
        "uptime": None,
        "event_delivery": round(delivered_ok / len(deliveries) * 100.0, 1) if deliveries else 0.0,
        "dlq_depth": len(dlq),
        "connectors_live": live,
        "sync_conflicts_today": len(conflicts),
        "connectors_total": len(connectors),
    }
