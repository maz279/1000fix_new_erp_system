# fix_iot_ops — M48: streams, protocol adapters, threshold rules, downsampling,
# prescriptive actions and telemetry consent. Devices, telemetry rows, alerts and
# predictions live in fix_stream_registry.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixIotStream(models.Model):
    _name = "fix.iot.stream"
    _description = "IoT Stream Binding"
    _order = "device_id, metric"

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.iot.device", string="Device", required=True, ondelete="cascade", index=True
    )
    equipment_id = fields.Many2one(related="device_id.equipment_id", string="Equipment", store=True)
    site_id = fields.Many2one(related="device_id.site_id", string="Site", store=True)
    adapter_id = fields.Many2one("fix.iot.adapter", string="Protocol Adapter", ondelete="set null")
    metric = fields.Char(required=True, help="e.g. temperature, vibration, battery_pct")
    unit = fields.Char()
    sample_interval_sec = fields.Integer(string="Sample Interval (s)", default=60, required=True)
    retention_days = fields.Integer(string="Raw Retention (days)", default=90, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("suspended", "Suspended")],
        required=True,
        default="draft",
    )
    last_seen = fields.Datetime(related="device_id.last_telemetry", string="Last Seen")
    telemetry_ids = fields.One2many("fix.iot.telemetry", "device_id", string="Telemetry")
    rule_ids = fields.One2many("fix.iot.rule", "stream_id", string="Alert Rules")

    _interval_positive = models.Constraint(
        "CHECK (sample_interval_sec > 0)", "The sample interval must be positive"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.stream") or "STRM/New"
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            if rec.state == "active":
                raise UserError("Stream is already active")
            rec.state = "active"

    def action_suspend(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Suspend an active stream")
            rec.state = "suspended"

    def ingest(self, value):
        """Record one reading and evaluate the stream's active threshold rules."""
        self.ensure_one()
        if self.state != "active":
            raise UserError("Ingest requires an active stream")
        telemetry = self.env["fix.iot.telemetry"].create(
            {
                "device_id": self.device_id.id,
                "timestamp": fields.Datetime.now(),
                "metric": self.metric,
                "value": value,
                "unit": self.unit,
            }
        )
        # last_seen reads live from the device; action_telemetry_received
        # stamps it.
        self.device_id.action_telemetry_received("online")
        raised = self.env["fix.iot.alert"]
        for rule in self.rule_ids.filtered(lambda r: r.state == "active"):
            if rule.matches(value):
                raised |= self.env["fix.iot.alert"].create(
                    {
                        "device_id": self.device_id.id,
                        "severity": rule.severity,
                        "message": "%s %s %s: reading %s %s"
                        % (
                            self.metric,
                            dict(rule._fields["operator"].selection).get(rule.operator),
                            rule.threshold,
                            value,
                            self.unit or "",
                        ),
                    }
                )
        return telemetry, raised


class FixIotAdapter(models.Model):
    _name = "fix.iot.adapter"
    _description = "IoT Protocol Adapter"
    _order = "name"

    name = fields.Char(required=True, default="New")
    protocol = fields.Selection(
        [
            ("mqtt", "MQTT"),
            ("http", "HTTPS Webhook"),
            ("modbus", "Modbus TCP"),
            ("opcua", "OPC-UA"),
            ("lorawan", "LoRaWAN"),
        ],
        required=True,
        default="mqtt",
    )
    endpoint = fields.Char(help="Broker or collector URL recorded for configuration")
    auth_mode = fields.Selection(
        [("none", "None"), ("token", "Bearer Token"), ("certificate", "Mutual TLS")],
        required=True,
        default="token",
    )
    state = fields.Selection(
        [("enabled", "Enabled"), ("disabled", "Disabled")], required=True, default="enabled"
    )
    stream_ids = fields.One2many("fix.iot.stream", "adapter_id", string="Streams")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.adapter") or "IADP/New"
        return super().create(vals_list)

    def action_enable(self):
        for rec in self:
            rec.state = "enabled"

    def action_disable(self):
        for rec in self:
            rec.state = "disabled"


class FixIotRule(models.Model):
    _name = "fix.iot.rule"
    _description = "IoT Threshold Alert Rule"
    _order = "stream_id, name"

    name = fields.Char(required=True, default="New")
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", required=True, ondelete="cascade", index=True
    )
    operator = fields.Selection(
        [("gt", ">"), ("gte", ">="), ("lt", "<"), ("lte", "<=")],
        required=True,
        default="gt",
    )
    threshold = fields.Float(required=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major")], required=True, default="minor"
    )
    duration_min = fields.Integer(string="For (minutes)", default=0)
    cooldown_min = fields.Integer(string="Cooldown (minutes)", default=15)
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")], required=True, default="active"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.rule") or "IRUL/New"
        return super().create(vals_list)

    def matches(self, value):
        self.ensure_one()
        if self.operator == "gt":
            return value > self.threshold
        if self.operator == "gte":
            return value >= self.threshold
        if self.operator == "lt":
            return value < self.threshold
        return value <= self.threshold

    def action_pause(self):
        for rec in self:
            rec.state = "paused"

    def action_activate(self):
        for rec in self:
            rec.state = "active"


class FixIotDownsample(models.Model):
    _name = "fix.iot.downsample"
    _description = "IoT Downsampling Policy"
    _order = "stream_id"

    name = fields.Char(required=True, default="New")
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", required=True, ondelete="cascade", index=True
    )
    raw_interval_sec = fields.Integer(string="Raw Interval (s)", required=True, default=60)
    target_interval_sec = fields.Integer(string="Target Interval (s)", required=True, default=300)
    aggregation = fields.Selection(
        [("avg", "Average"), ("min", "Minimum"), ("max", "Maximum"), ("last", "Last Value")],
        required=True,
        default="avg",
    )
    retention_days = fields.Integer(string="Compressed Retention (days)", default=730)
    compression_pct = fields.Float(string="Compression %", default=80.0)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")], required=True, default="draft"
    )

    _target_ge_raw = models.Constraint(
        "CHECK (target_interval_sec >= raw_interval_sec)",
        "The target interval cannot be shorter than the raw interval",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.iot.downsample") or "IDSP/New"
                )
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            rec.state = "active"


class FixIotPrescriptiveAction(models.Model):
    _name = "fix.iot.action"
    _description = "Prescriptive Maintenance Action"
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    prediction_id = fields.Many2one(
        "fix.predictive.maintenance",
        string="Prediction",
        required=True,
        ondelete="cascade",
        index=True,
    )
    equipment_id = fields.Many2one(
        related="prediction_id.equipment_id", string="Equipment", store=True
    )
    action_type = fields.Selection(
        [
            ("inspect", "Inspect"),
            ("replace", "Replace"),
            ("calibrate", "Calibrate"),
            ("dispatch", "Dispatch Technician"),
            ("reduce_load", "Reduce Load"),
        ],
        required=True,
        default="inspect",
    )
    priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    technician_id = fields.Many2one("hr.employee", string="Technician")
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("approved", "Approved"),
            ("dispatched", "Dispatched"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="proposed",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.action") or "IACT/New"
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Approve a proposed action")
            rec.state = "approved"

    def action_dispatch(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Dispatch an approved action")
            rec.state = "dispatched"

    def action_done(self):
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Complete a dispatched action")
            rec.state = "done"


class FixIotConsent(models.Model):
    _name = "fix.iot.consent"
    _description = "IoT Telemetry Consent"
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    subject_type = fields.Selection(
        [("device", "Device"), ("site", "Site"), ("customer", "Customer")],
        required=True,
        default="device",
    )
    device_id = fields.Many2one("fix.iot.device", string="Device", ondelete="set null")
    site_id = fields.Many2one("fix.site", string="Site", ondelete="set null")
    partner_id = fields.Many2one("res.partner", string="Customer")
    purpose = fields.Selection(
        [
            ("service", "Service Delivery"),
            ("analytics", "Analytics"),
            ("safety", "Safety Monitoring"),
        ],
        required=True,
        default="service",
    )
    granted_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("revoked", "Revoked")], required=True, default="active"
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.consent") or "ICNS/New"
        return super().create(vals_list)

    def action_revoke(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Revoke an active consent")
            rec.state = "revoked"
