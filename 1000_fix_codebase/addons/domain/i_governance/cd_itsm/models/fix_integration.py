# fix_integration — M28: API gateway catalogue, consumers/quotas, event bus
# (topics, schemas, subscriptions, DLQ, replay), the 47-connector framework,
# connector credentials and offline-sync conflict resolution. The
# transactional outbox lives in cd_event_outbox (fix.event.outbox).
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixApiEndpoint(models.Model):
    _name = "fix.api.endpoint"
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
    _description = "API Consumer"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="Linked Partner")
    key_ref = fields.Char(
        string="Key Reference",
        help="Vault path or key alias - never the key itself (SEC-101).",
    )
    quota_ids = fields.One2many("fix.api.quota", "consumer_id", string="Quotas")
    request_count = fields.Integer(compute="_compute_usage", string="Requests (30d)")
    active = fields.Boolean(default=True)

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
        for rec in self:
            # Only the reference rotates here; the secret lives in the vault.
            rec.key_ref = (rec.key_ref or "vault://api-keys/") + "#rotated"


class FixApiQuota(models.Model):
    _name = "fix.api.quota"
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


class FixEventTopic(models.Model):
    _name = "fix.event.topic"
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


class FixEventSchema(models.Model):
    _name = "fix.event.schema"
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

    def action_publish(self):
        for rec in self:
            rec.state = "published"


class FixEventSubscription(models.Model):
    _name = "fix.event.subscription"
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.event.subscription") or "SUB/New"
                )
        return super().create(vals_list)

    def action_pause(self):
        for rec in self:
            rec.state = "paused"

    def action_resume(self):
        for rec in self:
            rec.state = "active"


class FixEventDlq(models.Model):
    _name = "fix.event.dlq"
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
    replayed_at = fields.Datetime()
    state = fields.Selection(
        [("pending", "Pending"), ("replayed", "Replayed"), ("discarded", "Discarded")],
        required=True,
        default="pending",
    )

    @api.depends("topic_code", "created_at")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (rec.topic_code, str(rec.created_at or "")[:19])

    def action_replay(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Replay a pending DLQ entry")
            rec.write({"state": "replayed", "replayed_at": fields.Datetime.now()})

    def action_discard(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Discard a pending DLQ entry")
            rec.state = "discarded"


class FixConnector(models.Model):
    _name = "fix.connector"
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

    def action_mark_degraded(self):
        for rec in self:
            rec.state = "degraded"

    def action_mark_live(self):
        for rec in self:
            rec.state = "live"


class FixConnectorCredential(models.Model):
    _name = "fix.connector.credential"
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


class FixSyncConflict(models.Model):
    _name = "fix.sync.conflict"
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.sync.conflict") or "SYC/New"
                )
        return super().create(vals_list)

    def action_local_wins(self):
        for rec in self:
            if rec.resolution != "pending":
                raise UserError("Resolve a pending conflict")
            rec.resolution = "local_wins"

    def action_remote_wins(self):
        for rec in self:
            if rec.resolution != "pending":
                raise UserError("Resolve a pending conflict")
            rec.resolution = "remote_wins"

    def action_merged(self):
        for rec in self:
            if rec.resolution != "pending":
                raise UserError("Resolve a pending conflict")
            rec.resolution = "merged"


class FixIntegrationLog(models.Model):
    """The measured traffic log: API requests, event deliveries and webhook
    attempts — the data the five reports compute from."""

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
    status = fields.Selection(
        [("success", "Success"), ("throttled", "Throttled"), ("failed", "Failed")],
        required=True,
        default="success",
        index=True,
    )
    latency_ms = fields.Integer()
    status_code = fields.Integer()
    created_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
