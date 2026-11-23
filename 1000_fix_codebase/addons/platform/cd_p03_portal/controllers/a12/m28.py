# A12 · M28 Integration, API & Events — surfaces, packs and KPIs over the API
# catalogue, consumers/quotas, event topics/schemas/subscriptions/DLQ, the
# connector framework, connector credentials, sync conflicts and the measured
# integration log.
#
# M28-13 (A12 finish build): the packs read with sudo, so any employee got all
# five reports (webhook URLs included) and the KPIs, across companies. They now
# read as the caller. Reporting on a surface takes the read ACL on it, and a pack
# reads another module's delivery table only after that check.
#
# M28-5: only rows the platform wrote carry measured=True. Seeded rows stay in the
# log, and a report leaves them out and says how many it left out.
import datetime

SURFACES = {
    "fix.api.endpoint": {
        "order": "version desc, code",
        "limit": 300,
        "actions": {
            "action_request_public",
            "action_recall_approval",
            "action_publish_endpoint",
            "action_deprecate",
            "action_sunset",
        },
    },
    "fix.api.consumer": {
        "order": "name",
        "limit": 200,
        "actions": {
            "action_request_registration",
            "action_recall_approval",
            "action_issue_key",
            "action_rotate_key",
        },
    },
    "fix.api.quota": {
        "order": "consumer_id, endpoint_id",
        "limit": 300,
        "actions": {"action_request_increase", "action_recall_approval"},
    },
    "fix.event.topic": {
        "order": "code",
        "limit": 200,
        "actions": {"action_pause", "action_resume"},
    },
    "fix.event.schema": {
        "order": "code, version desc",
        "limit": 200,
        "actions": {
            "action_publish",
            "action_deprecate",
            "action_request_breaking_exception",
            "action_recall_approval",
        },
    },
    "fix.event.subscription": {
        "order": "topic_id, consumer_id",
        "limit": 300,
        "actions": {
            "action_request_go_live",
            "action_recall_approval",
            "action_pause",
            "action_resume",
            "action_rotate_secret",
        },
    },
    "fix.event.dlq": {
        "order": "created_at desc, id desc",
        "limit": 300,
        "actions": {"action_replay", "action_discard", "action_recall_approval"},
    },
    "fix.webhook.delivery": {"order": "id desc", "limit": 300, "actions": set()},
    "fix.integration.allowed.host": {
        "order": "state, host",
        "limit": 200,
        "actions": {"action_remove"},
    },
    "fix.integration.reconciliation.run": {
        "order": "run_at desc, id desc",
        "limit": 300,
        "actions": {"action_resolve"},
    },
    "fix.integration.reconciliation.suppression": {
        "order": "valid_until desc, id desc",
        "limit": 100,
        "actions": {"action_request_suppression", "action_recall_approval", "action_end"},
    },
    "fix.connector": {
        "order": "connector_type, name",
        "limit": 300,
        "actions": {
            "action_request_go_live",
            "action_recall_approval",
            "action_probe",
            "action_mark_degraded",
            "action_mark_down",
            "action_mark_live",
            "action_disable",
        },
    },
    "fix.connector.credential": {"order": "name", "limit": 200, "actions": {"action_rotate"}},
    "fix.sync.conflict": {
        "order": "detected_at desc, id desc",
        "limit": 300,
        "actions": {
            "action_local_wins",
            "action_remote_wins",
            "action_merged",
            "action_dismiss",
            # the Offline Sync page's "Decide a Sync Conflict" (capture audit 2026-11-14)
            "action_resolve_decision",
        },
    },
    "fix.integration.log": {"order": "created_at desc, id desc", "limit": 500, "actions": set()},
    # capture pass 2 (2026-11-19): the spec records the pages could not capture
    "fix.api.credential": {
        "order": "consumer_id, environment, id desc",
        "limit": 300,
        "actions": {"action_rotate", "action_revoke"},
    },
    "fix.event.consumer": {"order": "event_type, model, method", "limit": 300, "actions": set()},
    "fix.event.consumer.replay": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_request_replay", "action_recall_approval"},
    },
    "fix.webhook.inbound.source": {
        "order": "code",
        "limit": 200,
        "actions": {"action_request_go_live", "action_recall_approval", "action_pause"},
    },
    "fix.webhook.inbound.event": {
        "order": "received_at desc, id desc",
        "limit": 500,
        "actions": set(),
    },
    "fix.integration.fallback": {"order": "connector_id, id", "limit": 300, "actions": set()},
    "fix.integration.fallback.test": {
        "order": "tested_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.integration.batch.run": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_verify", "action_reject"},
    },
}

# A12 R4 (finding M28-11): what /p03/model/write may set on each M28 surface —
# exactly the fields a workspace form offers as editable. The workflow fields
# (state / resolution / replayed_at / health) are NOT here: they change only
# through the whitelisted actions, which re-check the Integration Admin group
# and audit the privileged ones (replay, discard, rotate, resolve).
# Read-only screens carry an empty tuple:
#   - fix.event.dlq, fix.webhook.delivery: engine-raised; replay/discard only;
#   - fix.sync.conflict: raised by the offline sync engine. Its target was
#     writable here, which is how a resolution reached ir.config_parameter
#     (N-M28-1);
#   - fix.integration.log: system-written only (P1-6), no group may write it.
# key_ref and secret_ref are set at registration; the models lock them on an
# existing record, so after that they change only through a rotate action.
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
    "fix.api.consumer": ("name", "partner_id", "key_ref", "active"),
    "fix.api.quota": ("consumer_id", "endpoint_id", "requests_per_min", "daily_quota"),
    "fix.event.topic": ("code", "name", "schema_id", "retention_days"),
    "fix.event.schema": ("code", "version", "schema_text"),
    "fix.event.subscription": ("consumer_id", "topic_id", "endpoint_url", "secret_ref"),
    "fix.event.dlq": (),
    "fix.webhook.delivery": (),
    "fix.integration.allowed.host": ("host", "reason"),
    "fix.integration.reconciliation.run": (),
    "fix.integration.reconciliation.suppression": ("check_code", "reason", "valid_until"),
    "fix.connector": (
        "name",
        "connector_type",
        "endpoint",
        "credential_id",
        "fallback_connector_id",
        # capture pass 2: the integration register (FR-IPF-055, BRU-IPF-13)
        "int_code",
        "pattern",
        "priority",
        "owner_id",
    ),
    "fix.connector.credential": ("name", "auth_type", "secret_ref", "expires_on", "active"),
    "fix.sync.conflict": (),
    "fix.integration.log": (),
    # capture pass 2 (2026-11-19). Issued/revoked/replayed/verified stamps, the
    # client id, the receipt log and the in-process subscriptions are never typed.
    "fix.api.credential": ("consumer_id", "environment", "secret_ref", "expires_on"),
    "fix.event.consumer": (),
    "fix.event.consumer.replay": ("consumer_id", "replay_from", "replay_to", "reason"),
    "fix.webhook.inbound.source": (
        "name",
        "code",
        "connector_id",
        "owning_module",
        "route_key",
        "secret_ref",
        "replay_window_seconds",
    ),
    "fix.webhook.inbound.event": (),
    "fix.integration.fallback": (
        "connector_id",
        "fallback_type",
        "fallback_connector_id",
        "procedure",
        "user_message",
        "user_message_bn",
    ),
    "fix.integration.fallback.test": (
        "fallback_id",
        "tested_at",
        "result",
        "engage_seconds",
        "evidence",
    ),
    "fix.integration.batch.run": (
        "connector_id",
        "direction",
        "purpose",
        "reference",
        "file",
        "file_name",
        "declared_records",
        "declared_total",
    ),
}

NOT_MEASURED_NOTE = "%d seed row(s) in the log are not measured traffic and are left out."
NO_TRAFFIC = "No measured traffic yet."


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


def _measured(env, kind):
    """The caller's measured rows of `kind`, and how many seed rows were left out."""
    Log = env["fix.integration.log"]
    Log.check_access("read")
    rows = Log.search([("kind", "=", kind), ("measured", "=", True)])
    return rows, Log.search_count([("kind", "=", kind), ("measured", "!=", True)])


def _seed_notes(unmeasured):
    return [NOT_MEASURED_NOTE % unmeasured] if unmeasured else []


def _dispatch_note(env):
    params = env["ir.config_parameter"].sudo()
    enabled = (params.get_param("fix.integration.dispatch_enabled") or "").strip().lower()
    if enabled in ("1", "true", "yes", "on"):
        return (
            "Dispatch is on (fix.integration.dispatch_enabled). In a local environment "
            "only a local host is reached (DE-11)."
        )
    return (
        "Dispatch is off (fix.integration.dispatch_enabled): no webhook leaves this "
        "system, and each delivery records 'not sent: dispatch disabled'."
    )


def api_usage(env, date_from=None, date_to=None, **params):
    """API usage by consumer: request counts, throttles, failures, p95."""
    logs, unmeasured = _measured(env, "api")
    groups = {}
    for log in logs:
        key = log.consumer_id.name if log.consumer_id else "No registered consumer"
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
        p95 = lat[min(int(len(lat) * 0.95), len(lat) - 1)] if lat else None
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
            "Measured at the API edge on the routes it is wired to. p95 is computed over the "
            "recorded request latencies; a consumer with no latency records shows an honest dash.",
            *_seed_notes(unmeasured),
        ],
        totals={
            "consumer": "Total",
            "requests": sum(r["requests"] for r in rows),
            "success": sum(r["success"] for r in rows),
            "throttled": sum(r["throttled"] for r in rows),
            "failed": sum(r["failed"] for r in rows),
        },
        empty=NO_TRAFFIC,
    )


def _delivery_counts(env):
    """{event type: {delivered, failed, dead}} from the relay's own delivery table:
    each row is a real in-process delivery. The webhook side is its own report."""
    env["fix.integration.log"].check_access("read")
    grouped = (
        env["fix.event.consumer.delivery"]
        .sudo()
        ._read_group(
            [("event_id.company_id", "in", env.companies.ids)],
            ["event_type", "state"],
            ["__count"],
        )
    )
    counts = {}
    for event_type, state, count in grouped:
        row = counts.setdefault(event_type or "unknown", {"delivered": 0, "failed": 0, "dead": 0})
        row["delivered" if state == "done" else state] += count
    return counts


def event_delivery_slo(env, date_from=None, date_to=None, **params):
    """Event delivery SLO: delivered vs failed by event type."""
    counts = _delivery_counts(env)
    rows = []
    for key, v in sorted(counts.items()):
        total = v["delivered"] + v["failed"] + v["dead"]
        rows.append(
            {
                "topic": key,
                "delivered": v["delivered"],
                "failed": v["failed"],
                "dead": v["dead"],
                "slo": round(v["delivered"] / total * 100.0, 2) if total else None,
            }
        )
    return _pack(
        "Event Delivery SLO",
        ["topic", "delivered", "failed", "dead", "slo"],
        {
            "topic": "Event Type",
            "delivered": "Delivered",
            "failed": "Failed (retrying)",
            "dead": "Dead-Lettered",
            "slo": "Delivery %",
        },
        rows,
        [
            "Counted from the relay's real delivery records (fix.event.consumer.delivery), "
            "for the event types that have an in-process consumer. Webhook attempts are on "
            "the Webhook Success Rate report."
        ],
        totals={
            "topic": "Total",
            "delivered": sum(r["delivered"] for r in rows),
            "failed": sum(r["failed"] for r in rows),
            "dead": sum(r["dead"] for r in rows),
        },
        empty=NO_TRAFFIC,
    )


def connector_latency(env, date_from=None, date_to=None, **params):
    """Connector latency and health from the connector register."""
    connectors = env["fix.connector"].search([])
    rows = []
    for c in connectors:
        measured = bool(c.last_probe_at)
        rows.append(
            {
                "connector": c.name,
                "type": dict(c._fields["connector_type"].selection).get(c.connector_type),
                "latency_ms": c.last_latency_ms if measured else None,
                "last_success": str(c.last_success_at or "—")[:19] if measured else "—",
                "evidence": "Measured" if measured else (c.last_probe_note or "Not measured"),
                "fallback": c.fallback_connector_id.name or "—",
                "state": dict(c._fields["state"].selection).get(c.state, c.state),
            }
        )
    rows.sort(key=lambda r: -(r["latency_ms"] or 0))
    slow = len([r for r in rows if (r["latency_ms"] or 0) > 1000])
    unmeasured = len([c for c in connectors if not c.last_probe_at])
    notes = ["Latency is the last value measured from connector traffic or an active probe."]
    if unmeasured:
        notes.append(
            "%d connector(s) have never been measured: their state is what was registered, "
            "not an observation. Traffic does not flow through this register yet, and the "
            "active probe needs dispatch to be on." % unmeasured
        )
    return _pack(
        "Connector Latency — %d connector(s) above 1s" % slow,
        ["connector", "type", "latency_ms", "last_success", "evidence", "fallback", "state"],
        {
            "connector": "Connector",
            "type": "Type",
            "latency_ms": "Last Latency (ms)",
            "last_success": "Last Success",
            "evidence": "Evidence",
            "fallback": "Fallback",
            "state": "State",
        },
        rows,
        notes,
        empty="No connectors configured.",
    )


def dlq_analysis(env, date_from=None, date_to=None, **params):
    """DLQ analysis: entries by topic and reason."""
    dlqs = env["fix.event.dlq"].search([])
    origins = dict(dlqs._fields["origin"].selection)
    groups = {}
    for entry in dlqs:
        key = (entry.topic_code, entry.reason, origins.get(entry.origin))
        g = groups.setdefault(key, {"count": 0, "pending": 0, "replayed": 0, "discarded": 0})
        g["count"] += 1
        if entry.state == "pending":
            g["pending"] += 1
        elif entry.state == "replayed":
            g["replayed"] += 1
        elif entry.state == "discarded":
            g["discarded"] += 1
    rows = [{"topic": t, "reason": r, "origin": o, **v} for (t, r, o), v in sorted(groups.items())]
    return _pack(
        "DLQ Analysis",
        ["topic", "reason", "origin", "count", "pending", "replayed", "discarded"],
        {
            "topic": "Topic",
            "reason": "Reason",
            "origin": "Origin",
            "count": "Entries",
            "pending": "Pending",
            "replayed": "Replayed",
            "discarded": "Discarded",
        },
        rows,
        [
            "Every dead-letter entry keeps its payload and reason; replay is per entry and "
            "needs a stated reason. An entry with no delivery behind it is seed data: it "
            "cannot be replayed."
        ],
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
    logs, unmeasured = _measured(env, "webhook")
    subs = env["fix.event.subscription"].search([("topic_id.company_id", "in", env.companies.ids)])
    rows = []
    for sub in subs:
        # M28-12: match attempts on the SUBSCRIPTION, not the consumer - a
        # consumer can hold several subscriptions, and the old consumer_id
        # match only looked right when the two ids happened to coincide.
        sub_logs = logs.filtered(lambda ln, s=sub.id: ln.subscription_id.id == s)
        sent = sub_logs.filtered(lambda ln: ln.status in ("success", "failed"))
        ok = len(sent.filtered(lambda ln: ln.status == "success"))
        rows.append(
            {
                "subscription": sub.name,
                "topic": sub.topic_id.code if sub.topic_id else "—",
                "url": sub.endpoint_url[:60],
                "attempts": len(sent),
                "success": ok,
                "not_sent": len(sub_logs) - len(sent),
                "rate": round(ok / len(sent) * 100.0, 1) if sent else None,
                "state": dict(sub._fields["state"].selection).get(sub.state, sub.state),
            }
        )
    rows.sort(key=lambda r: -(r["rate"] if r["rate"] is not None else -1))
    return _pack(
        "Webhook Success Rate",
        ["subscription", "topic", "url", "attempts", "success", "not_sent", "rate", "state"],
        {
            "subscription": "Subscription",
            "topic": "Topic",
            "url": "Endpoint URL",
            "attempts": "Attempts",
            "success": "Success",
            "not_sent": "Not Sent",
            "rate": "Success %",
            "state": "State",
        },
        rows,
        [
            _dispatch_note(env),
            "Success % is over attempts that left the system; 'not sent' is not an attempt. A "
            "subscription with no attempts shows a dash rather than a fabricated rate. Attempts "
            "are matched to the subscription by the log's subscription link (M28-12).",
            *_seed_notes(unmeasured),
        ],
        totals={
            "subscription": "Total",
            "attempts": sum(r["attempts"] for r in rows),
            "success": sum(r["success"] for r in rows),
            "not_sent": sum(r["not_sent"] for r in rows),
        },
        empty="No event subscriptions configured.",
    )


def offline_sync(env, date_from=None, date_to=None, **params):
    """N-M28-9: the protocol's own numbers, from the idempotency ledger."""
    env["fix.sync.conflict"].check_access("read")
    if "fix.offline.idempotency.ledger" not in env:
        return _pack(
            "Offline Sync Protocol",
            [],
            {},
            [],
            ["The field service module is not installed here."],
            empty=NO_TRAFFIC,
        )
    grouped = (
        env["fix.offline.idempotency.ledger"]
        .sudo()
        ._read_group(
            [("company_id", "in", env.companies.ids)],
            ["operation", "status"],
            ["__count"],
        )
    )
    table = {}
    for operation, status, count in grouped:
        row = table.setdefault(
            operation, {"applied": 0, "conflict_applied": 0, "rejected": 0, "operation": operation}
        )
        row[status] += count
    rows = [
        {**row, "total": row["applied"] + row["conflict_applied"] + row["rejected"]}
        for _name, row in sorted(table.items())
    ]
    pending = env["fix.sync.conflict"].search_count([("resolution", "=", "pending")])
    return _pack(
        "Offline Sync Protocol",
        ["operation", "total", "applied", "conflict_applied", "rejected"],
        {
            "operation": "Operation",
            "total": "Commands",
            "applied": "Applied",
            "conflict_applied": "Applied Over a Server Change",
            "rejected": "Rejected",
        },
        rows,
        [
            "Upload-first sync: each command runs once (idempotency ledger) and in its own "
            "savepoint. The server is authoritative for assignment, pricing, stock and state; "
            "the device for notes, evidence and timestamps (BRU-IPF-17).",
            "%d conflict(s) wait for a decision on Conflict Resolution." % pending,
        ],
        totals={
            "operation": "Total",
            "total": sum(r["total"] for r in rows),
            "applied": sum(r["applied"] for r in rows),
            "conflict_applied": sum(r["conflict_applied"] for r in rows),
            "rejected": sum(r["rejected"] for r in rows),
        },
        empty="No offline commands recorded.",
    )


REPORTS = {
    "api_usage": api_usage,
    "event_delivery_slo": event_delivery_slo,
    "connector_latency": connector_latency,
    "dlq_analysis": dlq_analysis,
    "webhook_success": webhook_success,
    "offline_sync": offline_sync,
}


def kpis(env):
    # One endpoint serves every module's KPIs, so a user with no read ACL here gets
    # no M28 tiles and no refusal: the other modules' tiles still load.
    if not env["fix.integration.log"].has_access("read"):
        return {}
    logs, _unmeasured = _measured(env, "api")
    counts = _delivery_counts(env)
    delivered = sum(c["delivered"] for c in counts.values())
    delivery_total = sum(c["delivered"] + c["failed"] + c["dead"] for c in counts.values())
    dlq = env["fix.event.dlq"].search([("state", "=", "pending")])
    connectors = env["fix.connector"].search([])
    today = datetime.date.today()
    conflicts = env["fix.sync.conflict"].search_count(
        [("detected_at", ">=", str(today) + " 00:00:00")]
    )
    lat = sorted([ln.latency_ms for ln in logs if ln.latency_ms])
    p95 = lat[min(int(len(lat) * 0.95), len(lat) - 1)] if lat else None
    live = len(connectors.filtered(lambda c: c.state == "live"))
    # M28: the bus backlog tiles. event_delivery is the SLO of DISPATCHED
    # deliveries; these two say whether anything is still WAITING — the pair
    # that was invisible while 19k events sat pending on the live estate.
    health = env["fix.event.outbox"].relay_health() if hasattr(
        env["fix.event.outbox"], "relay_health"
    ) else {}
    return {
        "api_p95": p95,
        "uptime": None,
        "event_delivery": round(delivered / delivery_total * 100.0, 1) if delivery_total else None,
        "dlq_depth": len(dlq),
        "bus_pending": health.get("bus_pending", 0),
        "oldest_bus_pending_hours": health.get("oldest_bus_pending_hours", 0.0),
        "connectors_live": live,
        "sync_conflicts_today": conflicts,
        "connectors_total": len(connectors),
    }
