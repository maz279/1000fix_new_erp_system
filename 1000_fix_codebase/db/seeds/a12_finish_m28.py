# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""a12_finish_m28.py - bring live M28 rows into line with the finish-build controls.

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser), after -u cd_itsm. Idempotent.

What it does, and why it forges nothing:

1. Subscriptions: re-validates them against the allow-list, which ships empty. The 3
   live subscriptions on hooks.1000fix.internal fail, so they pause with a note saying
   why. Nobody decided those hosts are trusted (B-5), so none is listed here.
2. Log: rows written before the `measured` column carry measured=False, because only
   the platform's own path sets it. The log is append-only, so nothing is rewritten:
   the script counts them, and the reports leave them out and say so.
3. DLQ: rows with no delivery behind them are seed data. They close as discarded with
   that reason, including two that claim to have been replayed, which never happened.
   Real dead letters stay pending. The 3 on project.risk_escalated fail in
   fix_grc_handoffs.py (the M67 builder's): replay them after that fix lands.
4. Conflicts: raises rows from the offline ledger. A pending row that cannot be applied
   (off the sync allow-list, target gone, or empty values) closes with nothing applied.
5. Topics: registers a topic for each event type the outbox has actually carried
   (M28-8). Retention is 365 days, a long synthetic default, so seeding purges nothing
   recent. An operator shortens it per topic. No schema is attached.
6. Schemas: tests each published schema against recent real events. If any event would
   be refused, enforcement drops to "warn" so that a business write cannot start failing.
   That is listed for a person to resolve.

The allow-list stays empty and dispatch stays off. FIX_A12F_M28_COMMIT=1 commits;
otherwise the transaction rolls back and the output says what would have changed.
"""

import json
import os

from odoo import fields
from odoo.addons.cd_itsm.models.fix_integration_dispatch import (
    SCHEMA_ENFORCEMENT_KEY,
    _schema_violations,
)

SEEDED_TOPIC_RETENTION_DAYS = 365
SCHEMA_SAMPLE = 200
SEED_DLQ_REASON = "Seed row from before the mirror: no delivery behind it, nothing to replay"
result = {}

# 1. Subscriptions -----------------------------------------------------------------
Subscription = env["fix.event.subscription"].sudo()
paused_before = set(Subscription.search([("state", "=", "paused")]).ids)
result["subscriptions_paused"] = Subscription.cron_revalidate_subscriptions()
result["subscriptions_now_paused"] = [
    {"name": sub.name, "host": sub.endpoint_url, "why": sub.pause_reason}
    for sub in Subscription.search([("state", "=", "paused")])
    if sub.id not in paused_before
]

# 2. Log ---------------------------------------------------------------------------
Log = env["fix.integration.log"].sudo()
# Y05: a subscription still active with no go-live approval predates the route.
unapproved = Subscription.search(
    [("state", "in", ("active", "failing")), ("approval_state", "!=", "approved")]
)
unapproved._fix_pause_off_list("Predates go-live approval: use Request Go-Live to bring it back")
result["subscriptions_paused_no_go_live_approval"] = unapproved.mapped("name")

result["log_rows_not_measured"] = Log.search_count([("measured", "!=", True)])
result["log_rows_measured"] = Log.search_count([("measured", "=", True)])

# 3. DLQ ---------------------------------------------------------------------------
Dlq = env["fix.event.dlq"].sudo()
seeded = Dlq.search(
    [
        ("delivery_id", "=", False),
        ("webhook_delivery_id", "=", False),
        ("state", "in", ("pending", "replayed")),
    ]
)
result["dlq_seed_rows_closed"] = seeded.ids
for entry in seeded:
    entry._guarded().write(
        {
            "state": "discarded",
            "replayed_at": False,
            "replayed_by": False,
            "decision_reason": SEED_DLQ_REASON[:200],
        }
    )
result["dlq_real_rows_pending"] = [
    {"id": entry.id, "topic": entry.topic_code, "reason": entry.reason}
    for entry in Dlq.search([("state", "=", "pending")])
]

# 4. Conflicts ---------------------------------------------------------------------
Conflict = env["fix.sync.conflict"].sudo()
result["conflicts_raised_from_ledger"] = Conflict.cron_ingest_ledger_conflicts()
closed = []
for row in Conflict.search([("resolution", "=", "pending")]):
    gone = row.res_model not in env or not env[row.res_model].sudo().browse(row.res_id).exists()
    empty = not (row.local_value or row.remote_value)
    if row.policy_class == "denied" or gone or empty:
        why = "off the sync allow-list" if row.policy_class == "denied" else "target gone"
        why = "no collided values" if empty and not gone else why
        row.action_dismiss(note=f"Closed by the A12 finish seed: {why}")
        closed.append({"name": row.name, "target": row.res_model, "why": why})
result["conflicts_closed_nothing_applied"] = closed

# 5. Topics ------------------------------------------------------------------------
Topic = env["fix.event.topic"].sudo()
env.cr.execute("SELECT DISTINCT event_type, company_id FROM fix_event_outbox")
created = []
for event_type, company_id in env.cr.fetchall():
    if not Topic.search_count([("code", "=", event_type), ("company_id", "=", company_id)]):
        Topic.create(
            {
                "code": event_type,
                "name": event_type,
                "company_id": company_id,
                "retention_days": SEEDED_TOPIC_RETENTION_DAYS,
            }
        )
        created.append(event_type)
result["topics_registered_from_outbox"] = sorted(created)
env.cr.execute(
    "SELECT t.code FROM fix_event_topic t WHERE NOT EXISTS "
    "(SELECT 1 FROM fix_event_outbox e WHERE e.event_type = t.code)"
)
result["topics_with_no_events_for_review"] = sorted(row[0] for row in env.cr.fetchall())

# 6. Schemas -----------------------------------------------------------------------
Outbox = env["fix.event.outbox"].sudo()
breaking = []
for topic in Topic.search([("schema_id.state", "in", ("published", "deprecated"))]):
    contract = json.loads(topic.schema_id.schema_text or "{}")
    events = Outbox.search(
        [("event_type", "=", topic.code), ("company_id", "=", topic.company_id.id)],
        order="id desc",
        limit=SCHEMA_SAMPLE,
    )
    bad = [e for e in events if _schema_violations(contract, json.loads(e.payload or "{}"))]
    if bad:
        breaking.append({"topic": topic.code, "sampled": len(events), "would_refuse": len(bad)})
if breaking:
    env["ir.config_parameter"].sudo().set_param(SCHEMA_ENFORCEMENT_KEY, "warn")
result["schemas_breaking_live_events_for_review"] = breaking
result["schema_enforcement"] = (
    env["ir.config_parameter"].sudo().get_param(SCHEMA_ENFORCEMENT_KEY, "reject")
)

# State the screens will show ------------------------------------------------------
Connector = env["fix.connector"].sudo()
Connector.cron_probe_connectors()
result["credentials_alerted"] = env["fix.connector.credential"].sudo().cron_alert_expiring()
result["connectors"] = {
    "total": Connector.search_count([]),
    "ever_measured": Connector.search_count([("last_probe_at", "!=", False)]),
}
env.cr.execute(
    "SELECT code, version, company_id, count(*) FROM fix_event_schema "
    "GROUP BY 1, 2, 3 HAVING count(*) > 1"
)
result["schema_duplicates_for_review"] = env.cr.fetchall()
result["allowlist"] = sorted(Subscription._webhook_allowlist())
result["dispatch_enabled"] = (
    env["ir.config_parameter"].sudo().get_param("fix.integration.dispatch_enabled", "(unset: off)")
)
result["ran_at"] = fields.Datetime.now()
group = env.ref("cd_itsm.group_integration_admin")
result["integration_admins_for_review"] = group.all_user_ids.mapped("login")

print(json.dumps(result, indent=2, default=str))
if os.environ.get("FIX_A12F_M28_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back: nothing changed (set FIX_A12F_M28_COMMIT=1 to commit)")
