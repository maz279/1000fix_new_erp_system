# fix_integration_dispatch — M28: what makes the integration registers act
# (A12 finish build, decision B-7, findings M28-3, M28-8, N-M28-5).
#
#   - fix.webhook.delivery: the webhook dispatcher. A cron reads the outbox for
#     active subscriptions and POSTs a signed envelope (AP-004 §4.3-4.6: Standard
#     Webhooks headers, 3 attempts at 0 / 30 s / 5 min, then the DLQ; 5 consecutive
#     failures disable the endpoint). Every attempt writes a log row.
#     DE-11: real HTTP also needs fix.integration.dispatch_enabled (default off) and,
#     in a local environment, a local host. Otherwise the row says "not sent" and why.
#   - fix.integration.allowed.host: the allow-list screen. An Integration Admin edits
#     the one parameter through an audited action and gains no other access to
#     ir.config_parameter.
#   - fix.event.outbox / fix.event.consumer: a topic's published schema is checked at
#     emit, and a paused topic holds its events.
import base64
import hashlib
import hmac
import json
import logging
import os
import re
import time
from datetime import timedelta

import requests
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_integration import (
    DISPATCH_ENABLED_KEY,
    INTEGRATION_ADMIN,
    WEBHOOK_ALLOWLIST_KEY,
    _allowlist,
    _dispatch_refusal,
    _integration_audit,
    _notify_integration_admins,
    _param_int,
    _param_on,
    _require_integration_admin,
    _require_service,
    _required_text,
)

_logger = logging.getLogger(__name__)

# AP-004 §4.5: attempt 1 immediate, attempt 2 at ~30 s, attempt 3 at ~5 min.
WEBHOOK_MAX_ATTEMPTS = 3
WEBHOOK_BACKOFF_SECONDS = {1: 30, 2: 300}
WEBHOOK_TIMEOUT_SECONDS = 10
# A slow endpoint must not hold the cron: this many sends per run.
WEBHOOK_BATCH = 25
ENQUEUE_BATCH = 500
# BRU-IPF-18: five consecutive failures disable the endpoint.
AUTO_DISABLE_KEY = "fix.integration.webhook_disable_after"
AUTO_DISABLE_DEFAULT = 5
# "reject" (default): a payload breaking the topic's published schema is refused at
# emit. "warn": logged only, for rehearsing a new schema against live traffic.
SCHEMA_ENFORCEMENT_KEY = "fix.integration.schema_enforcement"
HOST_NOT_LISTED = "host not on the allow-list"
# Y04. Rows need this long to settle before a gap counts: the mirror crons run every
# 15 minutes. A suppression lasts at most this many days.
RECONCILIATION_SETTLE = timedelta(hours=1)
SUPPRESSION_MAX_DAYS_KEY = "fix.integration.suppression_max_days"
SUPPRESSION_MAX_DAYS_DEFAULT = 7
RECONCILIATION_SUPPRESSIBLE = [
    ("relay_lag", "Relay: events past the settling time"),
    ("dead_letters", "Relay dead letters missing from the DLQ"),
    ("webhook_dead", "Webhook dead letters missing from the DLQ"),
    ("sync_conflicts", "Offline conflicts missing from the register"),
]
RECONCILIATION_CHECKS = [
    *RECONCILIATION_SUPPRESSIBLE,
    ("external", "Portal and external systems"),
]
RECONCILIATION_NOT_RUN = (
    "Not reconciled: no portal or external system is connected, and no connector carries "
    "traffic through the register."
)
DISPATCH_DISABLED = "dispatch disabled"
# M28-D2: how long a not-sent webhook delivery may sit in limbo before the
# dispatcher parks it in the DLQ for a human (configurable, days).
NOT_SENT_GRACE_KEY = "cd_itsm.webhook_not_sent_grace_days"
NOT_SENT_GRACE_DAYS = 7

_HOST = re.compile(r"^(\*\.)?[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$")
_JSON_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}


def _http_post(url, body, headers, timeout):
    """The dispatcher's request. Tests replace this: no real network."""
    response = requests.post(
        url, data=body, headers=headers, timeout=timeout, allow_redirects=False
    )
    return response.status_code


def _vault_secret(ref):
    """The value behind a vault reference, or None. No secrets manager exists
    (B-8): values reach the process as FIX_VAULT_<PATH> environment variables,
    the way deployment secrets do. No value means nothing is signed or sent."""
    path = re.sub(r"[^A-Z0-9]+", "_", (ref or "")[len("vault://") :].upper()).strip("_")
    return os.environ.get("FIX_VAULT_%s" % path) or None


def _sign(secret, event_id, timestamp, body):
    """AP-004 §4.4: v1,base64(HMAC-SHA256(secret, "<id>.<timestamp>.<raw body>"))."""
    signed = ("%s.%s." % (event_id, timestamp)).encode() + body
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).digest()
    return "v1,%s" % base64.b64encode(digest).decode()


def _schema_violations(schema, value, path="$"):
    """The JSON Schema keywords a topic contract uses: type, required, properties,
    enum, items, additionalProperties=false. jsonschema is not a dependency here."""
    problems = []
    expected = schema.get("type")
    if expected:
        names = expected if isinstance(expected, list) else [expected]
        if not any(_type_matches(name, value) for name in names):
            return ["%s is not %s" % (path, "/".join(names))]
    if "enum" in schema and value not in schema["enum"]:
        problems.append("%s is not one of %s" % (path, schema["enum"]))
    if isinstance(value, dict):
        for name in schema.get("required") or []:
            if name not in value:
                problems.append("%s.%s is required" % (path, name))
        properties = schema.get("properties") or {}
        for name, sub in properties.items():
            if name in value and isinstance(sub, dict):
                problems += _schema_violations(sub, value[name], "%s.%s" % (path, name))
        if schema.get("additionalProperties") is False:
            for name in value:
                if name not in properties:
                    problems.append("%s.%s is not in the contract" % (path, name))
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for index, item in enumerate(value):
            problems += _schema_violations(schema["items"], item, "%s[%d]" % (path, index))
    return problems


def _type_matches(name, value):
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    python_type = _JSON_TYPES.get(name)
    return isinstance(value, python_type) if python_type else True


class FixIntegrationAllowedHost(models.Model):
    """One line of the outbound allow-list, with who listed it and why (N-M28-5)."""

    _name = "fix.integration.allowed.host"
    _inherit = ["fix.guarded.mixin"]
    _description = "Allowed Outbound Host"
    _order = "state, host"
    _rec_name = "host"

    host = fields.Char(required=True, help="A host name, or *.example.com for its subdomains.")
    reason = fields.Char(required=True, help="Why Company data may go to this host.")
    state = fields.Selection(
        [("listed", "Listed"), ("removed", "Removed")], required=True, default="listed"
    )
    listed_by_id = fields.Many2one("res.users", string="Listed By", readonly=True)
    listed_at = fields.Datetime(readonly=True)
    removed_by_id = fields.Many2one("res.users", string="Removed By", readonly=True)
    removed_at = fields.Datetime(readonly=True)
    removal_reason = fields.Char(readonly=True)

    def _fix_guarded_fields(self):
        return {
            "state",
            "listed_by_id",
            "listed_at",
            "removed_by_id",
            "removed_at",
            "removal_reason",
        }

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= {"host", "reason"}
        return locked

    @api.model
    def _fix_normal_host(self, raw):
        host = (raw or "").strip().lower()
        if not _HOST.match(host):
            raise ValidationError(
                "%r is not a host name. Give a host such as hooks.example.com or "
                "*.example.com: no scheme, port or path." % (raw or "")
            )
        if host.startswith("*.") and host.count(".") < 2:
            raise ValidationError("%r is too wide: it would allow a whole top-level domain." % host)
        return host

    @api.model_create_multi
    def create(self, vals_list):
        _require_integration_admin(self.env, "list an outbound host")
        Sudo = self.sudo()
        listed = _allowlist(self.env)
        for vals in vals_list:
            vals["host"] = self._fix_normal_host(vals.get("host"))
            vals["reason"] = _required_text(vals.get("reason"), "why this host may receive data")
            if Sudo.search_count([("host", "=", vals["host"]), ("state", "=", "listed")]):
                raise ValidationError("%s is already on the list." % vals["host"])
            vals.update(
                {
                    "state": "listed",
                    "listed_by_id": self.env.user.id,
                    "listed_at": fields.Datetime.now(),
                }
            )
            listed.add(vals["host"])
        records = super(FixIntegrationAllowedHost, Sudo).create(vals_list)
        Sudo._fix_store_hosts(listed)
        for rec in records:
            _integration_audit(
                self.env,
                "integration.allowlist_added",
                "fix.integration.allowed.host,%d" % rec.id,
                "integration.allowlist_added: %s by %s; why: %s"
                % (rec.host, self.env.user.name, rec.reason),
            )
        return records.with_env(self.env)

    def write(self, vals):
        # The form posts what it shows, so an unchanged echo passes. A listed host is
        # evidence of who allowed what: to change one, remove it and list another.
        if not self._fix_guard_open():
            for rec in self:
                for name in {"host", "reason"} & set(vals):
                    if rec._fix_guard_differs(name, vals[name], rec[name]):
                        raise UserError(
                            "A listed host is not edited: remove it and list the new one."
                        )
        return super().write(vals)

    def _fix_store_hosts(self, hosts):
        value = ",".join(sorted(hosts)) or False
        self.env["ir.config_parameter"].sudo().set_param(WEBHOOK_ALLOWLIST_KEY, value)

    def action_remove(self, reason=None):
        """Take a host off the list. Subscriptions on it pause at once."""
        _require_integration_admin(self.env, "remove an outbound host")
        why = _required_text(reason, "why this host is being removed")
        listed = _allowlist(self.env)
        for rec in self:
            if rec.state != "listed":
                raise UserError("%s is not on the list." % rec.host)
            listed.discard(rec.host)
        self.sudo()._fix_store_hosts(listed)
        self.sudo()._guarded().write(
            {
                "state": "removed",
                "removed_by_id": self.env.user.id,
                "removed_at": fields.Datetime.now(),
                "removal_reason": why[:200],
            }
        )
        for rec in self:
            _integration_audit(
                self.env,
                "integration.allowlist_removed",
                "fix.integration.allowed.host,%d" % rec.id,
                "integration.allowlist_removed: %s by %s; why: %s"
                % (rec.host, self.env.user.name, why),
            )
        self.env["fix.event.subscription"].sudo().cron_revalidate_subscriptions()
        return True

    def _fix_adopt_parameter_hosts(self):
        """The parameter stays the source of truth. A system administrator can set it
        directly, so the screen follows it instead of showing a list that is not in
        force. Server code only."""
        _require_service(self.env, "Allow-list reconciliation")
        hosts = _allowlist(self.env)
        rows = self.sudo().search([("state", "=", "listed")])
        for rec in rows.filtered(lambda r: r.host not in hosts):
            rec._guarded().write(
                {
                    "state": "removed",
                    "removed_at": fields.Datetime.now(),
                    "removal_reason": "Removed directly from the parameter",
                }
            )
        for host in sorted(hosts - set(rows.mapped("host"))):
            try:
                self.sudo().create(
                    {"host": host, "reason": "Listed directly in the parameter by a system admin"}
                )
            except ValidationError:
                _logger.warning("M28: the allow-list parameter holds an unusable entry: %s", host)


class FixWebhookDelivery(models.Model):
    """One event for one subscription: the attempts and how they ended."""

    _name = "fix.webhook.delivery"
    _description = "Webhook Delivery"
    _order = "id desc"

    subscription_id = fields.Many2one(
        "fix.event.subscription", required=True, index=True, ondelete="cascade"
    )
    event_id = fields.Many2one("fix.event.outbox", required=True, index=True, ondelete="cascade")
    event_type = fields.Char(related="event_id.event_type", store=True)
    company_id = fields.Many2one("res.company", required=True, index=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("retry", "Retry Scheduled"),
            ("sent", "Sent"),
            ("not_sent", "Not Sent"),
            ("dead", "Dead-Lettered"),
        ],
        required=True,
        default="pending",
        index=True,
    )
    attempts = fields.Integer(default=0, help="Real requests made. A refusal makes none.")
    next_attempt_at = fields.Datetime(index=True)
    last_outcome = fields.Char()
    last_status_code = fields.Integer()
    sent_at = fields.Datetime()

    _once = models.Constraint(
        "UNIQUE (subscription_id, event_id)", "An event is delivered to a subscription once"
    )

    @api.depends("event_type", "subscription_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s > %s" % (rec.event_type, rec.subscription_id.name)

    # ---- the cron -----------------------------------------------------------
    @api.model
    def cron_dispatch_webhooks(self):
        """ir.cron (1 minute): queue new events for each subscription, then work
        what is due. A separate cron from the relay, so a slow endpoint cannot delay
        an in-process hand-off."""
        _require_service(self.env, "The webhook dispatcher")
        self._fix_enqueue()
        due = self._fix_due()
        for row in due:
            row._fix_attempt()
        return len(due)

    def _fix_enqueue(self):
        """One row per new event per subscription, from the subscription's creation
        on (no surprise backfill) and in its own company only. A disabled endpoint's
        events go straight to the DLQ (AP-004 AD-03). An operator's pause holds them."""
        Subscription = self.env["fix.event.subscription"].sudo()
        subs = Subscription.search(
            [
                ("topic_id.state", "=", "active"),
                "|",
                ("state", "in", ("active", "failing")),
                ("auto_disabled", "=", True),
            ]
        )
        self.env.flush_all()
        created = self.browse()
        for sub in subs:
            topic = sub.topic_id
            self.env.cr.execute(
                """
                SELECT e.id FROM fix_event_outbox e
                 WHERE e.event_type = %s AND e.company_id = %s AND e.create_date >= %s
                   AND NOT EXISTS (SELECT 1 FROM fix_webhook_delivery d
                                    WHERE d.subscription_id = %s AND d.event_id = e.id)
                 ORDER BY e.id LIMIT %s
                """,
                (topic.code, topic.company_id.id, sub.create_date, sub.id, ENQUEUE_BATCH),
            )
            event_ids = [row[0] for row in self.env.cr.fetchall()]
            if not event_ids:
                continue
            rows = self.sudo().create(
                [
                    {
                        "subscription_id": sub.id,
                        "event_id": event_id,
                        "company_id": topic.company_id.id,
                    }
                    for event_id in event_ids
                ]
            )
            if sub.auto_disabled:
                for row in rows:
                    row.write(
                        {
                            "state": "dead",
                            "last_outcome": "endpoint disabled after repeated failures",
                        }
                    )
                    row._fix_dead_letter("Endpoint disabled: the event was not sent (AD-03)")
            else:
                created |= rows
        return created

    def _fix_due(self):
        now = fields.Datetime.now()
        if _param_on(self.env, DISPATCH_ENABLED_KEY):
            # Dispatch was off: what waited behind that gate goes out now. Rows
            # refused for any other reason stay as they are until someone replays.
            self.sudo().search(
                [
                    ("state", "=", "not_sent"),
                    ("last_outcome", "=", "not sent: %s" % DISPATCH_DISABLED),
                ]
            ).write({"state": "pending"})
        # M28-D2: a row parked because its signing secret was missing gets
        # another chance as soon as the vault holds the secret again — a
        # refusal that clears must not strand the payload forever.
        stuck_secret = self.sudo().search(
            [
                ("state", "=", "not_sent"),
                ("last_outcome", "like", "not sent: signing secret unavailable%"),
            ]
        )
        for row in stuck_secret:
            if _vault_secret(row.subscription_id.secret_ref):
                row.write({"state": "pending"})
        # And nothing waits in limbo indefinitely: a not-sent row older than
        # the grace window graduates to the DLQ, where the replay screen owns
        # it (AD-03 posture: a human decides, with the reason on the row).
        grace_days = _param_int(self.env, NOT_SENT_GRACE_KEY, NOT_SENT_GRACE_DAYS)
        horizon = now - timedelta(days=grace_days)
        stranded = self.sudo().search([("state", "=", "not_sent"), ("create_date", "<=", horizon)])
        for row in stranded:
            outcome = "not sent for over %d days: %s" % (
                grace_days,
                (row.last_outcome or "unknown").replace("not sent: ", ""),
            )
            row.write({"state": "dead", "last_outcome": outcome})
            row._fix_dead_letter("Webhook %s" % outcome)
        return self.sudo().search(
            [
                ("subscription_id.state", "in", ("active", "failing")),
                ("subscription_id.topic_id.state", "=", "active"),
                "|",
                ("state", "=", "pending"),
                "&",
                ("state", "=", "retry"),
                ("next_attempt_at", "<=", now),
            ],
            order="id",
            limit=WEBHOOK_BATCH,
        )

    # ---- one attempt --------------------------------------------------------
    def _fix_attempt(self):
        self.ensure_one()
        sub = self.subscription_id
        refusal = _dispatch_refusal(self.env, sub.endpoint_url)
        if refusal == HOST_NOT_LISTED:
            sub._fix_pause_off_list("Failed at send time: %s" % HOST_NOT_LISTED)
        if refusal:
            return self._fix_not_sent(refusal)
        secret = _vault_secret(sub.secret_ref)
        if not secret:
            return self._fix_not_sent("signing secret unavailable (%s)" % sub.secret_ref)
        return self._fix_send(secret)

    def _fix_not_sent(self, reason):
        """Nothing left the process: say so, and do not count it as a failure."""
        outcome = "not sent: %s" % reason
        self.write({"state": "not_sent", "last_outcome": outcome, "next_attempt_at": False})
        self._fix_log("not_sent", outcome=outcome)
        return False

    def _fix_log(self, status, outcome=None, latency_ms=None, status_code=None):
        self.env["fix.integration.log"].sudo()._log_request(
            "webhook",
            status=status,
            consumer=self.subscription_id.consumer_id,
            subscription=self.subscription_id,
            topic_code=self.event_type,
            latency_ms=latency_ms,
            status_code=status_code,
            outcome=outcome,
        )

    def _fix_send(self, secret):
        event = self.event_id
        sub = self.subscription_id
        body = json.dumps(
            event._relay_event_dict(), ensure_ascii=False, sort_keys=True, default=str
        ).encode("utf-8")
        timestamp = str(int(time.time()))
        metadata = json.loads(event.metadata_json) if event.metadata_json else {}
        headers = {
            "webhook-id": event.event_id,
            "webhook-timestamp": timestamp,
            "webhook-signature": _sign(secret, event.event_id, timestamp, body),
            "content-type": "application/json; charset=utf-8",
            "x-correlation-id": str(metadata.get("correlation_id") or ""),
            "user-agent": "1000FiX-Webhooks/1.0",
        }
        started = time.monotonic()
        try:
            code = _http_post(sub.endpoint_url, body, headers, WEBHOOK_TIMEOUT_SECONDS)
            outcome = "HTTP %d" % code
        except requests.RequestException as exc:
            code = 0
            outcome = "no response: %s" % type(exc).__name__
        latency = int((time.monotonic() - started) * 1000)
        ok = 200 <= code < 300
        self._fix_log(
            "success" if ok else "failed", outcome=outcome, latency_ms=latency, status_code=code
        )
        vals = {"attempts": self.attempts + 1, "last_outcome": outcome, "last_status_code": code}
        if ok:
            self.write({**vals, "state": "sent", "sent_at": fields.Datetime.now()})
            if sub.state == "failing" or sub.consecutive_failures:
                sub._guarded().write({"state": "active", "consecutive_failures": 0})
            return True
        attempts = vals["attempts"]
        if attempts >= WEBHOOK_MAX_ATTEMPTS:
            self.write({**vals, "state": "dead", "next_attempt_at": False})
            self._fix_dead_letter("Webhook failed %d attempts, last: %s" % (attempts, outcome))
        else:
            self.write(
                {
                    **vals,
                    "state": "retry",
                    "next_attempt_at": fields.Datetime.now()
                    + timedelta(seconds=WEBHOOK_BACKOFF_SECONDS[attempts]),
                }
            )
        self._fix_count_failure(sub)
        return False

    def _fix_count_failure(self, sub):
        failures = sub.consecutive_failures + 1
        limit = _param_int(self.env, AUTO_DISABLE_KEY, AUTO_DISABLE_DEFAULT)
        if failures < limit:
            sub._guarded().write({"state": "failing", "consecutive_failures": failures})
            return
        why = "%d consecutive delivery failures (BRU-IPF-18)" % failures
        sub._guarded().write(
            {
                "state": "paused",
                "consecutive_failures": failures,
                "auto_disabled": True,
                "pause_reason": why,
            }
        )
        told = _notify_integration_admins(
            sub,
            "Webhook %s disabled" % sub.name,
            "%s. Fix the endpoint, then resume it with a reason. Missed events are not "
            "replayed automatically." % why,
        )
        _integration_audit(
            self.env,
            "integration.webhook_disabled",
            "fix.event.subscription,%d" % sub.id,
            "integration.webhook_disabled: %s: %s; %d Integration Admin(s) told"
            % (sub.name, why, told),
        )

    def _fix_dead_letter(self, reason):
        """Into the real DLQ: a row an Integration Admin replays or discards."""
        Dlq = self.env["fix.event.dlq"].sudo()
        entry = Dlq.search([("webhook_delivery_id", "=", self.id)], limit=1)
        if entry:
            # Replayed and dead again: it resurfaces, as a relay delivery does.
            entry.write(
                {
                    "state": "pending",
                    "replayed_at": False,
                    "replayed_by": False,
                    "reason": reason[:500],
                    "attempts": self.attempts,
                }
            )
            return entry
        return Dlq.create(
            {
                "topic_code": self.event_type,
                "company_id": self.company_id.id,
                "payload": self.event_id.payload or "{}",
                "reason": reason[:500],
                "attempts": self.attempts,
                "webhook_delivery_id": self.id,
            }
        )

    def _fix_requeue(self):
        """Back in the queue with a fresh attempt budget (DLQ replay)."""
        self.sudo().write(
            {"state": "pending", "attempts": 0, "next_attempt_at": False, "last_outcome": False}
        )


class FixIntegrationReconciliationRun(models.Model):
    """One check of one night (BRU-IPF-19, FR-IPF-052): what was compared and what
    disagreed. Divergence raises an alert. A suppressed one is still recorded: it is
    held back from the alert, never absorbed."""

    _name = "fix.integration.reconciliation.run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Integration Reconciliation Run"
    _order = "run_at desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True)
    check_code = fields.Selection(RECONCILIATION_CHECKS, string="Check", required=True, index=True)
    run_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    records_compared = fields.Integer()
    divergences_found = fields.Integer()
    detail = fields.Char()
    state = fields.Selection(
        [
            ("clean", "Clean"),
            ("divergent", "Divergent"),
            ("suppressed", "Divergent, Alert Suppressed"),
            ("not_run", "Not Run"),
        ],
        required=True,
        default="clean",
        index=True,
    )
    alerted = fields.Boolean()
    suppression_id = fields.Many2one(
        "fix.integration.reconciliation.suppression", ondelete="set null"
    )
    resolved_at = fields.Datetime()
    resolved_by_id = fields.Many2one("res.users", string="Resolved By")
    resolution_note = fields.Char()

    def _fix_counts(self, check, company):
        """(records compared, divergences) for one check, or None when it cannot run."""
        cutoff = fields.Datetime.now() - RECONCILIATION_SETTLE
        Delivery = self.env["fix.event.consumer.delivery"].sudo()
        Dlq = self.env["fix.event.dlq"].sudo()
        if check == "relay_lag":
            Outbox = self.env["fix.event.outbox"].sudo()
            domain = [("relayed_at", "=", False), ("company_id", "=", company.id)]
            stale = Outbox.search_count([*domain, ("create_date", "<", cutoff)])
            return Outbox.search_count(domain), stale
        if check == "dead_letters":
            dead = Delivery.search(
                [("state", "=", "dead"), ("event_id.company_id", "=", company.id)]
            )
            mirrored = set(Dlq.search([("delivery_id", "in", dead.ids)]).delivery_id.ids)
            late = dead.filtered(
                lambda d: d.id not in mirrored and (d.delivered_at or cutoff) <= cutoff
            )
            return len(dead), len(late)
        if check == "webhook_dead":
            dead = (
                self.env["fix.webhook.delivery"]
                .sudo()
                .search([("state", "=", "dead"), ("company_id", "=", company.id)])
            )
            kept = set(
                Dlq.search([("webhook_delivery_id", "in", dead.ids)]).webhook_delivery_id.ids
            )
            return len(dead), len(dead.filtered(lambda d: d.id not in kept))
        if check == "sync_conflicts":
            if "fix.offline.idempotency.ledger" not in self.env:
                return None
            rows = (
                self.env["fix.offline.idempotency.ledger"]
                .sudo()
                .search(
                    [
                        ("status", "=", "conflict_applied"),
                        ("company_id", "=", company.id),
                        ("applied_at", "<", cutoff),
                    ]
                )
            )
            known = set(
                self.env["fix.sync.conflict"]
                .sudo()
                .search([("source_command_id", "in", rows.mapped("command_id"))])
                .mapped("source_command_id")
            )
            return len(rows), len(rows.filtered(lambda r: r.command_id not in known))
        return None

    @api.model
    def cron_reconcile(self):
        """AUT-IPF-17, nightly. No role can switch a check off (spec s13). What it can
        honestly compare today is internal: nothing external carries traffic through
        the connector register (N08), and the row for that says so."""
        _require_service(self.env, "Reconciliation")
        Suppression = self.env["fix.integration.reconciliation.suppression"].sudo()
        created = self.browse()
        for company in self.env["res.company"].sudo().search([]):
            for check, _label in RECONCILIATION_CHECKS:
                counts = self._fix_counts(check, company)
                vals = {"company_id": company.id, "check_code": check}
                if counts is None:
                    vals.update(state="not_run", detail=RECONCILIATION_NOT_RUN)
                    created |= self.sudo().create(vals)
                    continue
                compared, found = counts
                vals.update(records_compared=compared, divergences_found=found)
                suppression = Suppression._fix_in_force(check, company) if found else Suppression
                if not found:
                    vals["state"] = "clean"
                elif suppression:
                    vals.update(state="suppressed", suppression_id=suppression.id)
                else:
                    vals["state"] = "divergent"
                row = self.sudo().create(vals)
                created |= row
                if row.state == "divergent":
                    row._fix_alert()
        return len(created)

    def _fix_alert(self):
        self.ensure_one()
        label = dict(RECONCILIATION_CHECKS)[self.check_code]
        told = _notify_integration_admins(
            self,
            "Reconciliation divergence: %s" % label,
            "%d of %d disagree. Investigate it: divergence is never absorbed (BRU-IPF-19)."
            % (self.divergences_found, self.records_compared),
        )
        self.sudo().write({"alerted": True})
        _integration_audit(
            self.env,
            "integration.reconciliation_divergence",
            "fix.integration.reconciliation.run,%d" % self.id,
            "integration.reconciliation_divergence: %s found %d of %d; %d Integration Admin(s) told"
            % (self.check_code, self.divergences_found, self.records_compared, told),
        )

    def action_resolve(self, note=None):
        """Records the investigation. If it still disagrees, tomorrow's run says so."""
        _require_integration_admin(self.env, "resolve a reconciliation divergence")
        text = _required_text(note, "what was found and done")
        for rec in self:
            if rec.state not in ("divergent", "suppressed") or rec.resolved_at:
                raise UserError("Resolve an open divergence.")
        self.sudo().write(
            {
                "resolved_at": fields.Datetime.now(),
                "resolved_by_id": self.env.user.id,
                "resolution_note": text[:200],
            }
        )
        for rec in self:
            _integration_audit(
                self.env,
                "integration.reconciliation_resolved",
                "fix.integration.reconciliation.run,%d" % rec.id,
                "integration.reconciliation_resolved: %s by %s: %s"
                % (rec.check_code, self.env.user.name, text),
            )
        return True


class FixIntegrationReconciliationSuppression(models.Model):
    """Y04, spec s13: a time-boxed hold on one check's alert, in force only once a
    second person approves it. It stops the alert, not the check."""

    _name = "fix.integration.reconciliation.suppression"
    _inherit = ["fix.approvable.mixin"]
    _description = "Reconciliation Alert Suppression"
    _order = "valid_until desc, id desc"

    _approval_domain = "other"
    _approval_group = INTEGRATION_ADMIN
    _approval_apply_method = "_fix_apply_suppression"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    check_code = fields.Selection(RECONCILIATION_SUPPRESSIBLE, string="Check", required=True)
    reason = fields.Char(required=True)
    valid_until = fields.Datetime(required=True)
    in_force_from = fields.Datetime(readonly=True, copy=False)
    ended_at = fields.Datetime(readonly=True, copy=False)
    status = fields.Selection(
        [
            ("requested", "Not Approved"),
            ("in_force", "In Force"),
            ("ended", "Ended or Expired"),
        ],
        compute="_compute_status",
    )

    @api.depends("in_force_from", "ended_at", "valid_until")
    def _compute_status(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.ended_at or (rec.valid_until and rec.valid_until <= now):
                rec.status = "ended"
            elif rec.in_force_from:
                rec.status = "in_force"
            else:
                rec.status = "requested"

    @api.depends("check_code", "valid_until")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s until %s" % (rec.check_code, str(rec.valid_until or "")[:16])

    @api.constrains("valid_until")
    def _check_time_box(self):
        days = _param_int(self.env, SUPPRESSION_MAX_DAYS_KEY, SUPPRESSION_MAX_DAYS_DEFAULT)
        now = fields.Datetime.now()
        for rec in self:
            if rec.valid_until <= now or rec.valid_until > now + timedelta(days=days):
                raise ValidationError(
                    "A suppression is time-boxed: it must end within the next %d days." % days
                )

    def _fix_guarded_fields(self):
        return super()._fix_guarded_fields() | {"in_force_from", "ended_at"}

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            if rec.in_force_from or rec.ended_at:
                locked |= {"check_code", "reason", "valid_until", "company_id"}
        return locked

    def _approval_needed(self) -> bool:
        self.ensure_one()
        return not self.in_force_from and not self.ended_at

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"check_code", "reason", "valid_until"}

    def _approval_clear_stamp(self, reason):
        self.sudo()._guarded().write({"in_force_from": False})

    def write(self, vals):
        # Stretching a suppression in force would be a new decision by one person.
        if not self._fix_guard_open() and {"check_code", "reason", "valid_until"} & set(vals):
            for rec in self.filtered(lambda r: r.in_force_from or r.ended_at):
                for name in {"check_code", "reason", "valid_until"} & set(vals):
                    if rec._fix_guard_differs(name, vals[name], rec[name]):
                        raise UserError(
                            "This suppression was already decided: end it and request a new one."
                        )
        return super().write(vals)

    @api.model
    def _fix_in_force(self, check, company):
        return self.sudo().search(
            [
                ("check_code", "=", check),
                ("company_id", "=", company.id),
                ("in_force_from", "!=", False),
                ("ended_at", "=", False),
                ("valid_until", ">", fields.Datetime.now()),
            ],
            limit=1,
        )

    def action_request_suppression(self, justification=None):
        _require_integration_admin(self.env, "request a reconciliation suppression")
        text = _required_text(justification, "why this alert should be held back")
        for rec in self:
            rec._check_time_box()
            rec.action_request_approval(justification=text)
        return True

    def _fix_apply_suppression(self):
        self._approval_assert_routed()
        self._check_time_box()
        self._guarded().write({"in_force_from": fields.Datetime.now()})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.reconciliation_suppressed",
                "fix.integration.reconciliation.suppression,%d" % rec.id,
                "integration.reconciliation_suppressed: %s until %s approved by %s; why: %s"
                % (rec.check_code, rec.valid_until, self.env.user.name, rec.reason),
            )
        return True

    def action_end(self):
        """One person may end it early: that restores the alert."""
        _require_integration_admin(self.env, "end a reconciliation suppression")
        self._guarded().write({"ended_at": fields.Datetime.now()})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.reconciliation_suppression_ended",
                "fix.integration.reconciliation.suppression,%d" % rec.id,
                "integration.reconciliation_suppression_ended: %s by %s"
                % (rec.check_code, self.env.user.name),
            )
        return True


class FixEventOutbox(models.Model):
    _inherit = "fix.event.outbox"

    @api.private
    @api.model
    def emit(self, event_type, aggregate, aggregate_id, payload, metadata=None):
        """M28-8: a payload is checked against its topic's published schema. A topic
        with no published schema checks nothing."""
        topic = (
            self.env["fix.event.topic"]
            .sudo()
            .search(
                [
                    ("code", "=", event_type),
                    ("company_id", "=", self.env.company.id),
                    ("schema_id.state", "in", ("published", "deprecated")),
                ],
                limit=1,
            )
        )
        if topic:
            topic._fix_check_payload(json.loads(json.dumps(payload, default=str)))
        return super().emit(event_type, aggregate, aggregate_id, payload, metadata)


class FixEventTopicContract(models.Model):
    _inherit = "fix.event.topic"

    def _fix_check_payload(self, payload):
        self.ensure_one()
        schema = json.loads(self.schema_id.schema_text or "{}")
        problems = _schema_violations(schema, payload)
        if not problems:
            return
        text = "Event %s breaks schema %s: %s" % (
            self.code,
            self.schema_id.display_name,
            "; ".join(problems[:5]),
        )
        mode = self.env["ir.config_parameter"].sudo().get_param(SCHEMA_ENFORCEMENT_KEY, "reject")
        if mode == "warn":
            _logger.warning(text)
            return
        raise ValidationError(text)


class FixEventConsumerHold(models.Model):
    _inherit = "fix.event.consumer"

    def _fix_paused_codes(self):
        cache = self.env.cr.cache
        if "fix_paused_topic_codes" not in cache:
            topics = self.env["fix.event.topic"].sudo().search([("state", "=", "paused")])
            cache["fix_paused_topic_codes"] = set(topics.mapped("code"))
        return cache["fix_paused_topic_codes"]

    def _matches(self, event_type):
        """M28-3: pausing a topic did nothing. The relay now skips its events, and
        Resume puts back what was skipped since the pause."""
        return super()._matches(event_type) and event_type not in self._fix_paused_codes()
