# fix_integration — M28: API gateway catalogue, consumers/quotas, event bus
# (topics, schemas, subscriptions, DLQ, replay), the 47-connector framework,
# connector credentials and offline-sync conflict resolution. The
# transactional outbox lives in cd_event_outbox (fix.event.outbox).
#
# A12 remediation (2026-11-04, report X4 / P1-6 / R4, findings M28-1..M28-13):
# this module was a register anyone could rewrite. Now:
#   - every model inherits fix.guarded.mixin, so state / resolution /
#     replayed_at / health fields change only through a transition action;
#   - every mutating action re-checks cd_itsm.group_integration_admin in
#     code (X4: the ACL alone is not enough);
#   - webhook subscriptions take an https URL on an allow-listed host with a
#     mandatory vault:// signing secret (M28-1; allow-list default EMPTY —
#     refuse everything until the operator lists a host);
#   - fix.event.dlq mirrors the REAL dead letters of the relay
#     (fix.event.consumer.delivery, state='dead') via cron_sync_dead_letters,
#     and replay re-enqueues that delivery (privileged, audited, idempotent);
#   - a published schema is frozen: corrections ship as a new version
#     (BRU-IPF-06 / M28-8);
#   - fix.integration.log is system-written only (M28-5): no user create or
#     write; server code logs through _log_request;
#   - key rotation bumps the version inside the vault reference instead of
#     appending a "#rotated" suffix (M28-2 / E A05), and is audited.
import json
import re
from urllib.parse import urlsplit

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

INTEGRATION_ADMIN = "cd_itsm.group_integration_admin"
# Hosts a webhook endpoint_url may point at (comma or whitespace separated;
# an entry "*.corp.local" allows subdomains). Conservative default: EMPTY —
# every external AND localhost URL is refused until the operator lists it.
WEBHOOK_ALLOWLIST_KEY = "fix.integration.webhook_allowlist"
# Context flag that marks a create() of fix.integration.log as coming from
# server code (the ACL denies create to every group anyway; this is the
# second lock — P1-6).
LOG_SERVICE_KEY = "fix_integration_log_service"


def _require_integration_admin(env, what):
    """X4 code check: the caller must hold the Integration Admin group.

    The ACL already denies plain users; this re-check closes the gap for
    anyone who gains the model ACLs without the role, and states the rule in
    the action itself. Superuser service code (crons, seeds) is trusted.
    """
    if env.su:
        return
    if not env.user.has_group(INTEGRATION_ADMIN):
        raise AccessError(
            "Only an Integration Admin may %s. Ask the platform owner to "
            "appoint one (cd_itsm.group_integration_admin)." % what
        )


def _integration_audit(env, event, object_ref, detail):
    """P1-6: privileged integration actions land in the append-only security
    audit trail. B1 ships fix.security.audit.log_event(event, object_ref,
    detail); until it lands, write the row directly under the generic
    'privileged' event so the action is still on the record."""
    audit = env["fix.security.audit"].sudo()
    log_event = getattr(audit, "log_event", None)
    if callable(log_event):
        log_event(event=event, object_ref=object_ref, detail=detail)
    else:
        audit.create(
            {
                "event": "privileged",
                "object_ref": object_ref,
                "detail": "[%s] %s" % (event, detail),
            }
        )


def _webhook_host(url):
    try:
        return (urlsplit(url or "").hostname or "").lower()
    except ValueError:
        return ""


class FixApiEndpoint(models.Model):
    _name = "fix.api.endpoint"
    _inherit = ["fix.guarded.mixin"]
    _description = "API Catalogue Entry"
    _order = "version desc, code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version = fields.Char(required=True, default="v1")
    path = fields.Char(required=True)
    method = fields.Selection(
        [
            ("GET", "GET"),
            ("POST", "POST"),
            ("PUT", "PUT"),
            ("PATCH", "PATCH"),
            ("DELETE", "DELETE"),
        ],
        required=True,
        default="GET",
    )
    auth_type = fields.Selection(
        [
            ("none", "Public"),
            ("api_key", "API Key"),
            ("oauth2", "OAuth 2.0"),
            ("mtls", "Mutual TLS"),
        ],
        required=True,
        default="api_key",
    )
    description = fields.Char()
    active = fields.Boolean(default=True)

    _code_version_unique = models.Constraint(
        "UNIQUE (code, version, company_id)", "An endpoint code+version is unique per company"
    )


class FixApiConsumer(models.Model):
    _name = "fix.api.consumer"
    _inherit = ["fix.guarded.mixin"]
    _description = "API Consumer"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="Linked Partner")
    key_ref = fields.Char(
        string="Key Reference",
        help="Vault path or key alias - never the key itself (SEC-101). "
        "Changes only through the Rotate Key action, which bumps the version.",
    )
    quota_ids = fields.One2many("fix.api.quota", "consumer_id", string="Quotas")
    request_count = fields.Integer(compute="_compute_usage", string="Requests (30d)")
    active = fields.Boolean(default=True)

    @api.constrains("key_ref")
    def _check_key_ref_vault(self):
        for rec in self:
            if rec.key_ref and not rec.key_ref.startswith("vault://"):
                raise ValidationError(
                    "A key reference must be a vault:// path (SEC-101) - the key "
                    "value itself never lands in this model."
                )

    def _compute_usage(self):
        Log = self.env["fix.integration.log"].sudo()
        for rec in self:
            rec.request_count = Log.search_count(
                [
                    ("kind", "=", "api"),
                    ("consumer_id", "=", rec.id),
                    ("status", "=", "success"),
                ]
            )

    def action_rotate_key(self):
        """Real rotation (M28-2): bump the version inside the vault
        reference (vault://keys/consumer-x/v2 -> /v3). Nothing is
        deactivated, the previous version stays valid in the vault until it
        expires there. Privileged and audited."""
        _require_integration_admin(self.env, "rotate an API consumer key")
        for rec in self:
            current = rec.key_ref or ""
            match = re.match(r"^(vault://.+/v)(\d+)$", current)
            if match:
                new_ref = "%s%d" % (match.group(1), int(match.group(2)) + 1)
            elif current.startswith("vault://"):
                new_ref = current.rstrip("/") + "/v2"
            else:
                raise UserError(
                    "The key reference of %s must be a vault:// path before it can "
                    "rotate (it is %r)." % (rec.name, current or "empty")
                )
            rec.write({"key_ref": new_ref})
            _integration_audit(
                self.env,
                "integration.key_rotated",
                "fix.api.consumer,%d" % rec.id,
                "integration.key_rotated: %s key reference %s -> %s by %s"
                % (rec.name, current, new_ref, self.env.user.name),
            )
        return True


class FixApiQuota(models.Model):
    _name = "fix.api.quota"
    _inherit = ["fix.guarded.mixin"]
    _description = "Rate Limit / Quota"
    _order = "consumer_id, endpoint_id"

    consumer_id = fields.Many2one("fix.api.consumer", required=True, ondelete="cascade", index=True)
    endpoint_id = fields.Many2one("fix.api.endpoint", string="Endpoint", ondelete="cascade")
    requests_per_min = fields.Integer(string="Requests / minute", default=60, required=True)
    daily_quota = fields.Integer(string="Daily Quota", default=10000, required=True)
    state = fields.Selection(
        [("active", "Active"), ("throttled", "Throttled")], required=True, default="active"
    )

    _rpm_positive = models.Constraint(
        "CHECK (requests_per_min > 0 AND daily_quota > 0)", "Quota limits must be positive"
    )

    def _fix_guarded_fields(self):
        # 'throttled' is the gateway's verdict on live traffic: a measured
        # state, not a configuration field. An Integration Admin changes the
        # LIMITS (which take effect on the next request - no pause/resume
        # trick needed); only server code records a throttle.
        return {"state"}


class FixEventTopic(models.Model):
    _name = "fix.event.topic"
    _inherit = ["fix.guarded.mixin"]
    _description = "Event Topic"
    _order = "code"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    schema_id = fields.Many2one("fix.event.schema", string="Schema")
    retention_days = fields.Integer(default=30, required=True)
    subscription_ids = fields.One2many("fix.event.subscription", "topic_id", string="Subscriptions")
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")], required=True, default="active"
    )

    @api.constrains("retention_days")
    def _check_retention_positive(self):
        # M28-8 / E B05: retention -5 was accepted while nothing read it.
        for rec in self:
            if rec.retention_days < 1:
                raise ValidationError(
                    "Topic retention must be at least 1 day (BRU-IPF-22): events "
                    "may not be deleted before retention."
                )

    def _fix_guarded_fields(self):
        return {"state"}

    def action_pause(self):
        _require_integration_admin(self.env, "pause an event topic")
        self._guarded().write({"state": "paused"})
        return True

    def action_resume(self):
        _require_integration_admin(self.env, "resume an event topic")
        self._guarded().write({"state": "active"})
        return True


class FixEventSchema(models.Model):
    _name = "fix.event.schema"
    _inherit = ["fix.guarded.mixin"]
    _description = "Event Schema"
    _order = "code, version desc"

    code = fields.Char(required=True)
    version = fields.Integer(required=True, default=1)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    schema_text = fields.Text(required=True, help="JSON Schema payload contract for the topic.")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("deprecated", "Deprecated")],
        required=True,
        default="draft",
    )

    @api.constrains("schema_text")
    def _check_schema_json(self):
        # M28-8 / E B06: "not json {{{" was published. A published contract
        # must at least parse; the registry is the source of truth.
        for rec in self:
            try:
                data = json.loads(rec.schema_text or "")
            except ValueError as parse_err:
                raise ValidationError(
                    "Schema text must be valid JSON (a JSON Schema object) - %s v%s "
                    "does not parse." % (rec.code, rec.version)
                ) from parse_err
            if not isinstance(data, dict):
                raise ValidationError(
                    "Schema text must be a JSON object for %s v%s." % (rec.code, rec.version)
                )

    def _fix_guarded_fields(self):
        return {"state"}

    def _frozen_fields(self):
        """BRU-IPF-06: once published (or deprecated) the contract, code and
        version are immutable - a breaking change ships as a NEW version."""
        return {"code", "version", "schema_text"}

    def _fix_form_locked_fields(self):
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            if rec.state in ("published", "deprecated"):
                locked |= rec._frozen_fields()
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = self._frozen_fields() & set(vals)
            if frozen:
                for rec in self:
                    if rec.state not in ("published", "deprecated"):
                        continue
                    changed = sorted(
                        n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])
                    )
                    if changed:
                        raise UserError(
                            "Schema %s v%s is %s: %s cannot be edited in place. A "
                            "published contract is frozen (BRU-IPF-06) - ship the "
                            "correction as a NEW version record."
                            % (rec.code, rec.version, rec.state, ", ".join(changed))
                        )
        return super().write(vals)

    def action_publish(self):
        _require_integration_admin(self.env, "publish an event schema")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Publish a draft schema (this one is %s)." % rec.state)
        # The JSON contract is validated by _check_schema_json on save; the
        # publish transition re-parses so a draft written before the
        # constraint cannot slip through.
        self._check_schema_json()
        self._guarded().write({"state": "published"})
        return True


class FixEventSubscription(models.Model):
    _name = "fix.event.subscription"
    _inherit = ["fix.guarded.mixin"]
    _description = "Event Subscription (webhook)"
    _order = "topic_id, consumer_id"

    name = fields.Char(required=True, default="New")
    consumer_id = fields.Many2one("fix.api.consumer", required=True, index=True)
    topic_id = fields.Many2one("fix.event.topic", required=True, ondelete="cascade", index=True)
    endpoint_url = fields.Char(
        required=True, help="The consumer webhook URL the event is delivered to."
    )
    secret_ref = fields.Char(
        string="Signing Secret Reference", help="Vault alias of the HMAC secret."
    )
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused"), ("failing", "Failing")],
        required=True,
        default="active",
    )

    @api.model
    def _webhook_allowlist(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(WEBHOOK_ALLOWLIST_KEY, "") or ""
        return {h.strip().lower() for h in re.split(r"[,\s]+", raw) if h.strip()}

    @staticmethod
    def _host_allowed(host, allowlist):
        if not host:
            return False
        if host in allowlist:
            return True
        return any(entry.startswith("*.") and host.endswith(entry[1:]) for entry in allowlist)

    @api.constrains("endpoint_url", "secret_ref")
    def _check_webhook_endpoint(self):
        # M28-1 / E B01-B03: a webhook is where payloads leave the Company.
        # https only, host on the operator's allow-list (default: empty =
        # refuse everything, localhost included), HMAC secret referenced in
        # the vault - never inline.
        allowlist = self._webhook_allowlist()
        for rec in self:
            url = rec.endpoint_url or ""
            scheme = urlsplit(url).scheme.lower()
            if scheme != "https":
                raise ValidationError(
                    "Webhook endpoint_url must be https:// - %r is not accepted "
                    "(M28-1: payloads must not leave the Company in clear)." % url
                )
            host = _webhook_host(url)
            if not self._host_allowed(host, allowlist):
                raise ValidationError(
                    "Webhook host %r is not on the integration allow-list "
                    "(ir.config_parameter %s). The list ships EMPTY on purpose: "
                    "no external or localhost host receives Company payloads until "
                    "an Integration Admin lists it." % (host or "?", WEBHOOK_ALLOWLIST_KEY)
                )
            if not rec.secret_ref:
                raise ValidationError(
                    "A webhook subscription needs its signing secret reference: "
                    "deliveries are HMAC-signed, and the secret is held in the vault."
                )
            if not rec.secret_ref.startswith("vault://"):
                raise ValidationError(
                    "The signing secret reference must be a vault:// alias (SEC-101), "
                    "not the secret itself."
                )

    def _fix_guarded_fields(self):
        return {"state"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.event.subscription") or "SUB/New"
                )
        return super().create(vals_list)

    def action_pause(self):
        _require_integration_admin(self.env, "pause an event subscription")
        self._guarded().write({"state": "paused"})
        return True

    def action_resume(self):
        _require_integration_admin(self.env, "resume an event subscription")
        self._guarded().write({"state": "active"})
        return True


class FixEventDlq(models.Model):
    """The dead-letter register the DLQ screen shows.

    A12 P1-6 / M28-4: this table no longer pretends to be a second queue. It
    MIRRORS the real dead letters of the in-process relay
    (fix.event.consumer.delivery, state='dead') — cron_sync_dead_letters
    copies each one in exactly once — and Replay re-enqueues that delivery
    for the relay cron to retry. Entries with no linked delivery (rows
    seeded before the mirror existed) cannot be replayed: nothing could be
    re-delivered, and the action says so instead of pretending."""

    _name = "fix.event.dlq"
    _inherit = ["fix.guarded.mixin"]
    _description = "Dead-Letter Queue Entry"
    _order = "created_at desc, id desc"
    _rec_name = "display_label"

    display_label = fields.Char(compute="_compute_label")
    topic_code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    payload = fields.Text(required=True)
    reason = fields.Char(required=True)
    attempts = fields.Integer(default=3, required=True)
    created_at = fields.Datetime(required=True, default=fields.Datetime.now)
    delivery_id = fields.Many2one(
        "fix.event.consumer.delivery",
        string="Relay Delivery",
        index=True,
        ondelete="set null",
        help="The relay delivery this entry mirrors; replay re-enqueues THIS row.",
    )
    replayed_at = fields.Datetime()
    replayed_by = fields.Many2one("res.users", string="Replayed By")
    state = fields.Selection(
        [("pending", "Pending"), ("replayed", "Replayed"), ("discarded", "Discarded")],
        required=True,
        default="pending",
    )

    _delivery_once = models.Constraint(
        "UNIQUE (delivery_id)", "A dead relay delivery is mirrored into the DLQ once"
    )

    @api.depends("topic_code", "created_at")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (rec.topic_code, str(rec.created_at or "")[:19])

    def _fix_guarded_fields(self):
        # state, replayed_at and replayed_by change only through the
        # privileged replay/discard actions, never through a plain write —
        # so no row can be born 'replayed' or rewritten to 'discarded' (C03).
        return {"state", "replayed_at", "replayed_by"}

    @api.model
    def cron_sync_dead_letters(self):
        """ir.cron fix.event.dlq (15 min): mirror every relay delivery whose
        state is 'dead' into the DLQ register, once per delivery."""
        Delivery = self.env["fix.event.consumer.delivery"].sudo()
        dead = Delivery.search([("state", "=", "dead")])
        if not dead:
            return 0
        already = set(
            self.sudo().search([("delivery_id", "in", dead.ids)]).mapped("delivery_id").ids
        )
        vals_list = []
        for delivery in dead:
            if delivery.id in already:
                continue
            event = delivery.event_id
            vals_list.append(
                {
                    "topic_code": delivery.event_type or event.event_type,
                    "company_id": event.company_id.id or self.env.company.id,
                    "payload": event.payload or "{}",
                    "reason": (delivery.last_error or "consumer dead-lettered")[:500],
                    "attempts": delivery.attempts,
                    "created_at": delivery.delivered_at or fields.Datetime.now(),
                    "delivery_id": delivery.id,
                }
            )
        if vals_list:
            self.sudo().create(vals_list)
        # A replay that dead-letters AGAIN must resurface as pending: the
        # unique link stops a second row, so without this the screen would
        # keep showing 'replayed' while the delivery is dead once more
        # (BRU-IPF-14: a dead letter older than an hour is an incident).
        # A discarded entry stays discarded - that decision is final.
        for rec in self.sudo().search(
            [("delivery_id", "in", dead.ids), ("state", "=", "replayed")]
        ):
            delivered = rec.delivery_id.delivered_at
            if rec.replayed_at and delivered and delivered > rec.replayed_at:
                rec.sudo().write({"state": "pending", "replayed_at": False, "replayed_by": False})
        return len(vals_list)

    def action_replay(self):
        """Privileged, audited, idempotent replay (M28-6 / P1-6).

        Re-enqueues the mirrored relay delivery: the delivery goes back to
        'failed' (the relay retries those and skips done/dead) and the outbox
        event is marked unrelayed, so the relay cron performs a real
        redelivery. A row already replayed is refused; a row with no linked
        delivery cannot be replayed at all (nothing would be re-delivered)."""
        _require_integration_admin(self.env, "replay a dead-letter entry")
        for rec in self:
            if rec.state != "pending":
                raise UserError(
                    "This dead-letter entry was already %s at %s - replay it once."
                    % (rec.state, str(rec.replayed_at or "")[:19])
                )
            delivery = rec.delivery_id
            if not delivery:
                raise UserError(
                    "This entry has no relay delivery behind it (a seeded row from "
                    "before the mirror): there is nothing to re-deliver."
                )
            if delivery.state != "dead":
                raise UserError(
                    "The linked relay delivery is no longer dead (state=%s) - it has "
                    "already been retried." % delivery.state
                )
            # The relay retries 'failed' deliveries and skips done/dead, so a
            # replay = fresh attempt budget + the event back in the relay's
            # queue. Both writes are server-side service writes.
            delivery.sudo().write(
                {
                    "state": "failed",
                    "attempts": 0,
                    "last_error": False,
                    "delivered_at": fields.Datetime.now(),
                }
            )
            delivery.event_id.sudo().write({"relayed_at": False})
            rec._guarded().write(
                {
                    "state": "replayed",
                    "replayed_at": fields.Datetime.now(),
                    "replayed_by": self.env.user.id,
                }
            )
            _integration_audit(
                self.env,
                "integration.dlq_replayed",
                "fix.event.dlq,%d" % rec.id,
                "integration.dlq_replayed: %s (delivery %d, event %s) re-enqueued by %s"
                % (
                    rec.topic_code,
                    delivery.id,
                    delivery.event_id.event_id,
                    self.env.user.name,
                ),
            )
        return True

    def action_discard(self):
        _require_integration_admin(self.env, "discard a dead-letter entry")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Discard a pending DLQ entry")
        self._guarded().write({"state": "discarded"})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.dlq_discarded",
                "fix.event.dlq,%d" % rec.id,
                "integration.dlq_discarded: %s discarded by %s"
                % (rec.topic_code, self.env.user.name),
            )
        return True


class FixConnector(models.Model):
    _name = "fix.connector"
    _inherit = ["fix.guarded.mixin"]
    _description = "External Connector"
    _order = "connector_type, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    connector_type = fields.Selection(
        [
            ("payment", "Payment"),
            ("logistics", "Logistics"),
            ("government", "Government / NBR"),
            ("messaging", "Messaging"),
            ("cloud", "Cloud / Storage"),
            ("crm", "CRM"),
            ("bi", "Analytics"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    endpoint = fields.Char()
    credential_id = fields.Many2one("fix.connector.credential", string="Credential")
    last_latency_ms = fields.Integer(string="Last Latency (ms)")
    last_success_at = fields.Datetime()
    state = fields.Selection(
        [("live", "Live"), ("degraded", "Degraded"), ("down", "Down"), ("disabled", "Disabled")],
        required=True,
        default="live",
    )

    def _fix_guarded_fields(self):
        # M28-9: health is MEASURED (probe / circuit breaker writes it as
        # server code), never typed by a user. The mark actions below are the
        # operator's manual override of last resort - privileged.
        return {"state", "last_latency_ms", "last_success_at"}

    def action_mark_degraded(self):
        _require_integration_admin(self.env, "mark a connector degraded")
        self._guarded().write({"state": "degraded"})
        return True

    def action_mark_live(self):
        _require_integration_admin(self.env, "mark a connector live")
        self._guarded().write({"state": "live"})
        return True


class FixConnectorCredential(models.Model):
    _name = "fix.connector.credential"
    _inherit = ["fix.guarded.mixin"]
    _description = "Connector Credential Reference"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    auth_type = fields.Selection(
        [
            ("api_key", "API Key"),
            ("oauth2", "OAuth 2.0"),
            ("basic", "Basic"),
            ("mtls", "Mutual TLS"),
        ],
        required=True,
        default="api_key",
    )
    secret_ref = fields.Char(
        string="Vault Reference",
        required=True,
        help="Vault path or alias. The secret VALUE never lands in this model (SEC-101).",
    )
    expires_on = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains("secret_ref")
    def _check_secret_ref_vault(self):
        # M28-10 / E D07: a raw key-shaped string was stored in clear.
        for rec in self:
            if rec.secret_ref and not rec.secret_ref.startswith("vault://"):
                raise ValidationError(
                    "A credential must reference the secret manager (vault://...) - "
                    "key material must never be entered here."
                )


class FixSyncConflict(models.Model):
    _name = "fix.sync.conflict"
    _inherit = ["fix.guarded.mixin"]
    _description = "Offline Sync Conflict"
    _order = "detected_at desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_ref = fields.Char(string="Device / Client", required=True, index=True)
    res_model = fields.Char(string="Record Model", required=True)
    res_id = fields.Integer(string="Record ID", required=True)
    field_name = fields.Char(required=True)
    local_value = fields.Char()
    remote_value = fields.Char()
    detected_at = fields.Datetime(required=True, default=fields.Datetime.now)
    resolution = fields.Selection(
        [
            ("pending", "Pending"),
            ("local_wins", "Local Wins"),
            ("remote_wins", "Remote Wins"),
            ("merged", "Manually Merged"),
        ],
        required=True,
        default="pending",
    )

    def _fix_guarded_fields(self):
        # M28-7 / E E04: a resolved conflict is immutable - resolution and
        # the collided values change only through the resolve actions.
        return {"resolution", "local_value", "remote_value"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.sync.conflict") or "SYC/New"
                )
        return super().create(vals_list)

    def _resolve(self, resolution):
        _require_integration_admin(self.env, "resolve an offline sync conflict")
        for rec in self:
            if rec.resolution != "pending":
                raise UserError("Resolve a pending conflict (this one is %s)" % rec.resolution)
        self._guarded().write({"resolution": resolution})
        for rec in self:
            _integration_audit(
                self.env,
                "integration.sync_conflict_resolved",
                "fix.sync.conflict,%d" % rec.id,
                "integration.sync_conflict_resolved: %s %s on %s.%s by %s"
                % (
                    rec.name,
                    resolution,
                    rec.res_model,
                    rec.field_name,
                    self.env.user.name,
                ),
            )
        return True

    def action_local_wins(self):
        return self._resolve("local_wins")

    def action_remote_wins(self):
        return self._resolve("remote_wins")

    def action_merged(self):
        return self._resolve("merged")


class FixIntegrationLog(models.Model):
    """The measured traffic log: API requests, event deliveries and webhook
    attempts — the data the five reports compute from.

    A12 P1-6 / M28-5: system-written only. No group holds create or write on
    this model, and the model itself refuses a user-driven create/write as a
    second lock: measured figures must not be typeable (50 forged 'success'
    rows lifted the SLO to 100%). Server code logs through _log_request."""

    _name = "fix.integration.log"
    _description = "Integration Log Entry"
    _order = "created_at desc, id desc"

    kind = fields.Selection(
        [("api", "API Request"), ("delivery", "Event Delivery"), ("webhook", "Webhook Attempt")],
        required=True,
        index=True,
    )
    consumer_id = fields.Many2one("fix.api.consumer", string="Consumer", index=True)
    endpoint_id = fields.Many2one("fix.api.endpoint", string="Endpoint", index=True)
    topic_code = fields.Char(index=True)
    subscription_id = fields.Many2one(
        "fix.event.subscription",
        string="Subscription",
        index=True,
        help="The webhook attempt's subscription — the success-rate report "
        "matches on THIS, not on the consumer (M28-12).",
    )
    status = fields.Selection(
        [("success", "Success"), ("throttled", "Throttled"), ("failed", "Failed")],
        required=True,
        default="success",
        index=True,
    )
    latency_ms = fields.Integer()
    status_code = fields.Integer()
    created_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        # P1-6: only server code logs. A caller that reaches this far with a
        # plain environment (no service key, no superuser) is forging the
        # register — refuse.
        if not (self.env.su or self.env.context.get(LOG_SERVICE_KEY)):
            raise AccessError(
                "The integration log is written by the platform (measured "
                "requests, deliveries and webhook attempts only) — it cannot be "
                "created by hand."
            )
        return super().create(vals_list)

    def write(self, vals):
        raise AccessError(
            "The integration log is append-only: a measured request cannot be "
            "edited afterwards (flip a failure to success and the SLO lies)."
        )

    def unlink(self):
        raise AccessError("The integration log is append-only: entries cannot be deleted.")

    @api.private
    @api.model
    def _log_request(
        self,
        kind,
        status="success",
        consumer=None,
        endpoint=None,
        topic_code=None,
        subscription=None,
        latency_ms=None,
        status_code=None,
        created_at=None,
    ):
        """The one path server code logs a request/delivery/webhook attempt
        through (P1-6). @api.private: never callable over RPC."""
        vals = {
            "kind": kind,
            "status": status,
            "latency_ms": latency_ms,
            "status_code": status_code,
            "created_at": created_at or fields.Datetime.now(),
        }
        if consumer:
            vals["consumer_id"] = consumer if isinstance(consumer, int) else consumer.id
        if endpoint:
            vals["endpoint_id"] = endpoint if isinstance(endpoint, int) else endpoint.id
        if subscription:
            vals["subscription_id"] = (
                subscription if isinstance(subscription, int) else subscription.id
            )
        if topic_code:
            vals["topic_code"] = topic_code
        return self.sudo().with_context(**{LOG_SERVICE_KEY: True}).create(vals)
