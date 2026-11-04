# fix_stream_registry — M48: IoT telemetry, alerting, PdM (P11-M03).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

# A07 P1 (2026-11-04) BRU-IOT-10 / FR-IOT-040: where a prediction's model is
# checked against the M26 registry. "use" (default): the prediction is
# recorded, but nothing APPLIES it - no prescriptive action is approved and no
# preventive work order is raised - unless its model is a published M26
# predictive-maintenance model. "create": a prediction naming an unpublished
# model is refused outright. M26 (cd_ml_services) depends on this module, so
# the registry is read at run time, never imported.
MODEL_CHECK_PARAM = "cd_stream_registry.prediction_model_check"


def _require_operator(env, what):
    if not (env.su or env.user.has_group("cd_stream_registry.group_iot_operator")):
        raise AccessError("%s requires the IoT Operator role." % what)


class FixIotDevice(models.Model):
    """M48: IoT device registry on M17's asset registry."""

    _name = "fix.iot.device"
    _description = "IoT Device"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe (2026-11-03): status and the last-reading stamp were
        # writable directly, so a device with no readings was shown online.
        # They change only through action_telemetry_received.
        return super()._fix_guarded_fields() | {"status", "last_telemetry"}

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    device_id = fields.Char(string="Device Identifier", required=True, index=True)
    device_type = fields.Selection(
        [
            ("sensor", "Sensor"),
            ("gateway", "Gateway"),
            ("tracker", "GPS Tracker"),
            ("meter", "Smart Meter"),
        ],
        required=True,
        default="sensor",
    )
    equipment_id = fields.Many2one(
        "fix.equipment",
        string="Equipment (M45)",
        ondelete="set null",
        help="The test equipment this IoT device monitors",
    )
    site_id = fields.Many2one("fix.site", string="Site (M47)", ondelete="set null")
    # A07 audit (2026-11-03) M48-1: nothing on the device, its equipment or its
    # site said whose data it collects, so a customer-owned device could not be
    # told from a facility sensor. A device naming a customer always needs a
    # telemetry consent before ingest (fix_iot_ops.CONSENT_SCOPE_PARAM).
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer (data subject)",
        ondelete="restrict",
        index=True,
        help="Set when the device is customer-owned or monitors a customer's asset.",
    )
    last_telemetry = fields.Datetime(readonly=True)
    status = fields.Selection(
        [("online", "Online"), ("degraded", "Degraded"), ("offline", "Offline")],
        default="online",
        required=True,
        tracking=True,
    )
    alert_ids = fields.One2many("fix.iot.alert", "device_id", string="Alerts")

    def action_telemetry_received(self, health):
        """Gateway hook: a device reported its health with a reading.

        A07 P1 (2026-11-04) M48-4: any internal user called this public method
        and marked a device with no readings `online`. Liveness is derived from
        received readings (ingest) and from the silence cron; only the platform
        (the superuser gateway service) reports it here."""
        if not self.env.su:
            raise AccessError(
                "Device health is set by the readings it sends, not by hand: ingest a "
                "reading through its stream instead."
            )
        return self._fix_telemetry_received(health)

    def _fix_telemetry_received(self, health, at=None):
        """Update on telemetry; unhealthy transitions raise alerts."""
        at = at or fields.Datetime.now()
        for rec in self.sudo():
            became_unhealthy = health != "online" and rec.status == "online"
            last = max(rec.last_telemetry, at) if rec.last_telemetry else at
            rec._guarded().write({"status": health, "last_telemetry": last})
            if became_unhealthy:
                rec._fix_raise_health_alert(health)

    def _fix_raise_health_alert(self, health, note=None):
        self.ensure_one()
        alert = (
            self.env["fix.iot.alert"]
            .sudo()
            .create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "device_id": self.id,
                    "severity": "major" if health == "offline" else "minor",
                    "message": f"{self.name} became {health}" + (f" ({note})" if note else ""),
                }
            )
        )
        # The aggregate is the ALERT (it was published with the
        # device's id under the fix.iot.alert aggregate).
        publish(
            self.env,
            "iot.alert_raised",
            "fix.iot.alert",
            alert.id,
            {"device": self.device_id, "health": health},
        )
        return alert

    def _fix_mark_offline(self):
        """The silence cron: every live stream of the device fell silent. The
        last-reading stamp is NOT moved (it is the last real reading)."""
        for rec in self.sudo():
            was_online = rec.status == "online"
            rec._guarded().write({"status": "offline"})
            if was_online:
                since = rec.last_telemetry
                rec._fix_raise_health_alert(
                    "offline", "no reading since %s" % since if since else "never reported"
                )


class FixIotTelemetry(models.Model):
    """M48: telemetry record (time-series; the volume model at 50k/min)."""

    _name = "fix.iot.telemetry"
    _description = "IoT Telemetry"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "timestamp desc"

    # A07 audit (2026-11-03) M48-1/M48-4: any internal user created readings
    # directly - skipping the consent check and the rule engine (a value of 99
    # against a threshold of 5 raised no alert) - and could rewrite a stored
    # reading. Readings now arrive only through fix.iot.stream.ingest(), which
    # holds the guard token; superuser code (seeds, gateways via sudo) is
    # trusted, as everywhere else.
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "company_id",
            "device_id",
            "timestamp",
            "metric",
            "value",
            "unit",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "Telemetry is recorded only through the stream's ingest, which checks the "
                "telemetry consent and evaluates the alert rules."
            )
        self._fix_check_duplicates(vals_list)
        return super().create(vals_list)

    def _fix_check_duplicates(self, vals_list):
        """A07 P1 (2026-11-04) M48-4 / FR-IOT-018: a reading carrying its own
        source timestamp is unique on device, signal and time, so a gateway
        replay after reconnection does not double a series. A reading the
        server stamps (no timestamp given) is a fresh message by definition."""
        seen = set()
        for vals in vals_list:
            if not vals.get("timestamp"):
                continue
            key = (
                vals.get("device_id"),
                vals.get("metric"),
                fields.Datetime.to_datetime(vals["timestamp"]),
            )
            if key in seen or self.sudo().search_count(
                [
                    ("device_id", "=", key[0]),
                    ("metric", "=", key[1]),
                    ("timestamp", "=", key[2]),
                ],
                limit=1,
            ):
                raise ValidationError(
                    "Duplicate reading refused: device %s already has a %s reading at %s "
                    "(FR-IOT-018)." % (key[0], key[1], key[2])
                )
            seen.add(key)

    @api.constrains("timestamp")
    def _check_timestamp_not_future(self):
        # A future-dated reading counted as "in the last 24 h" and inflated
        # the ingest-rate KPI (240 fake rows: 0.0 -> 10.0/h). No clock-skew
        # allowance is applied: the in-process ingest stamps the server clock.
        now = fields.Datetime.now()
        for rec in self:
            if rec.timestamp and rec.timestamp > now:
                raise ValidationError("A telemetry reading cannot be dated in the future.")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    device_id = fields.Many2one("fix.iot.device", required=True, ondelete="cascade", index=True)
    timestamp = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    metric = fields.Char(required=True, help="e.g. temperature, vibration, gps_lat")
    value = fields.Float(required=True)
    unit = fields.Char(help="e.g. C, mm/s, deg")


# What a resolved alert keeps unchanged for users.
_ALERT_TERMS = frozenset({"device_id", "severity", "message"})


class FixIotAlert(models.Model):
    """M48: IoT alerting with threshold configuration."""

    _name = "fix.iot.alert"
    _description = "IoT Alert"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    # A07 P0 recipe (2026-11-03) M48-3: an alert was resolved straight from
    # "new" with no acknowledgement and no resolution, or written to
    # "resolved" directly with resolved_on left empty. The lifecycle is now
    # new -> acked -> resolved, each step stamped by its action, and a
    # resolution note is required.
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "acked_on",
            "acked_by",
            "resolved_on",
            "resolved_by",
            "resolution_note",
            # A07 P1: what the evaluator recorded (FR-IOT-033 dedup).
            "rule_id",
            "stream_id",
            "trigger_value",
            "last_value",
            "occurrence_count",
            "last_occurrence_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(a.state == "resolved" for a in self):
            locked |= _ALERT_TERMS
        return locked

    def write(self, vals):
        # A resolved alert is closed history for users.
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda a: a.state == "resolved"):
                if [
                    n
                    for n in _ALERT_TERMS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]:
                    raise UserError("Alert %s is resolved and can no longer change." % rec.name)
        return super().write(vals)

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    device_id = fields.Many2one("fix.iot.device", required=True, ondelete="cascade", index=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major")], default="minor", required=True, tracking=True
    )
    message = fields.Char(required=True)
    acked_on = fields.Datetime(string="Acknowledged On", readonly=True)
    acked_by = fields.Many2one("res.users", string="Acknowledged By", readonly=True)
    resolved_on = fields.Datetime(string="Resolved On", readonly=True)
    resolved_by = fields.Many2one("res.users", string="Resolved By", readonly=True)
    resolution_note = fields.Text(string="Resolution", readonly=True)
    # A07 P1 (2026-11-04) FR-IOT-033 / spec fix.alert: which rule raised it, on
    # which stream, at what value; repeated breaches are counted on the open
    # alert instead of raising new ones.
    rule_id = fields.Many2one(
        "fix.iot.rule", string="Rule", readonly=True, ondelete="set null", index=True
    )
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", readonly=True, ondelete="set null"
    )
    trigger_value = fields.Float(string="Trigger Value", readonly=True)
    last_value = fields.Float(string="Latest Value", readonly=True)
    occurrence_count = fields.Integer(string="Occurrences", default=1, readonly=True)
    last_occurrence_on = fields.Datetime(string="Last Occurrence", readonly=True)
    state = fields.Selection(
        [("new", "New"), ("acked", "Acknowledged"), ("resolved", "Resolved")],
        default="new",
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.alert") or "IOT/New"
        return super().create(vals_list)

    def action_ack(self):
        # A07 P1 (2026-11-04): the alert queue is the IoT operator's (spec R13).
        _require_operator(self.env, "Acknowledging an alert")
        for rec in self:
            if rec.state != "new":
                raise UserError("Acknowledge a new alert")
            rec._guarded().write(
                {"state": "acked", "acked_on": fields.Datetime.now(), "acked_by": self.env.uid}
            )

    def action_resolve(self, resolution_note=None):
        _require_operator(self.env, "Resolving an alert")
        note = (resolution_note or "").strip()
        for rec in self:
            if rec.state == "resolved":
                raise UserError("Alert is already resolved")
            if rec.state != "acked":
                raise UserError("Acknowledge alert %s before resolving it." % rec.name)
            if not note:
                raise UserError("Record how alert %s was resolved." % rec.name)
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolved_on": fields.Datetime.now(),
                    "resolved_by": self.env.uid,
                    "resolution_note": note,
                }
            )


class FixPredictiveMaintenance(models.Model):
    """M48: predictive-maintenance model wired to M26's ML gateway.
    Predicted failures become preventive work orders through M02 dispatch."""

    _name = "fix.predictive.maintenance"
    _description = "Predictive Maintenance Prediction"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    # A07 P0 recipe (2026-11-03) M48-5: a plain user typed outcome=confirmed
    # on five predictions and the precision KPI went 0 -> 100%, and set
    # work_order_created with no work order. The outcome is now recorded only
    # by completing a prescriptive action (fix.iot.action.action_done), and the
    # flag only by action_create_preventive_wo.
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "outcome",
            "outcome_note",
            "outcome_recorded_by",
            "outcome_recorded_on",
            "outcome_action_id",
            "work_order_created",
        }

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade"
    )
    prediction = fields.Selection(
        [
            ("failure_predicted", "Failure Predicted"),
            ("healthy", "Healthy"),
            ("degrading", "Degrading"),
        ],
        required=True,
        default="healthy",
        tracking=True,
    )
    confidence = fields.Float(string="Confidence (0-1)")
    estimated_days_to_failure = fields.Integer(
        string="Days to Failure", help="The ML model's estimate; 0 = imminent"
    )
    model_name = fields.Char(
        string="Model",
        help="The code of the published M26 model (fix.ml.model) that produced this score",
    )
    # A07 P1 (2026-11-04) BRU-IOT-11: the feature window the score was computed
    # on, so the output can be reproduced.
    feature_window_from = fields.Datetime(string="Feature Window From")
    feature_window_to = fields.Datetime(string="Feature Window To")
    model_published = fields.Boolean(
        string="Model Published (M26)",
        compute="_compute_model_published",
        help="True when Model names a production predictive-maintenance model in the "
        "M26 registry. Only such predictions drive interventions (BRU-IOT-10).",
    )
    last_evaluated = fields.Datetime(string="Last Evaluated")
    outcome = fields.Selection(
        [
            ("pending", "Pending Verification"),
            ("confirmed", "Failure Confirmed"),
            ("false_alarm", "False Alarm"),
        ],
        required=True,
        default="pending",
    )
    outcome_note = fields.Text(string="Outcome Note", readonly=True, copy=False)
    outcome_recorded_by = fields.Many2one(
        "res.users", string="Outcome Recorded By", readonly=True, copy=False
    )
    outcome_recorded_on = fields.Datetime(string="Outcome Recorded On", readonly=True, copy=False)
    outcome_action_id = fields.Many2one(
        "fix.iot.action",
        string="Outcome From Action",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    work_order_created = fields.Boolean(default=False, readonly=True)
    action_ids = fields.One2many("fix.iot.action", "prediction_id", string="Prescriptive Actions")

    # M48-5: confidence 5.0 was shown as 500% and -30 days was accepted.
    @api.constrains("confidence", "estimated_days_to_failure")
    def _check_score_bounds(self):
        for rec in self:
            if not 0.0 <= (rec.confidence or 0.0) <= 1.0:
                raise ValidationError("Prediction confidence must be between 0 and 1.")
            if (rec.estimated_days_to_failure or 0) < 0:
                raise ValidationError("Days to failure cannot be negative.")

    @api.constrains("feature_window_from", "feature_window_to")
    def _check_feature_window(self):
        for rec in self:
            if (
                rec.feature_window_from
                and rec.feature_window_to
                and rec.feature_window_to < rec.feature_window_from
            ):
                raise ValidationError("The feature window cannot end before it starts.")

    @api.constrains("model_name")
    def _check_model_on_create(self):
        param = self.env["ir.config_parameter"].sudo().get_param(MODEL_CHECK_PARAM) or "use"
        if param == "create":
            for rec in self:
                rec._fix_assert_published_model("Recording prediction %s" % rec.name)

    def _fix_published_model(self):
        """The production M26 predictive-maintenance model this prediction
        names, or None (also None when M26 is not installed)."""
        self.ensure_one()
        if "fix.ml.model" not in self.env or not (self.model_name or "").strip():
            return None
        model = (
            self.env["fix.ml.model"]
            .sudo()
            .search(
                [
                    ("code", "=", self.model_name.strip()),
                    ("kind", "=", "predictive_maintenance"),
                    ("status", "=", "production"),
                ],
                limit=1,
            )
        )
        return model or None

    def _compute_model_published(self):
        for rec in self:
            rec.model_published = bool(rec._fix_published_model())

    def _fix_assert_published_model(self, what):
        for rec in self:
            if not rec._fix_published_model():
                raise UserError(
                    "%s refused: prediction %s names model '%s', which is not a published "
                    "(production) M26 predictive-maintenance model. An unpublished model is "
                    "never applied (BRU-IOT-10)." % (what, rec.name, rec.model_name or "")
                )

    def _fix_record_outcome(self, outcome, note, action):
        """Record what an intervention found (called by fix.iot.action's
        action_done, which has already checked its own state). As superuser:
        the outcome follows from the completed action whatever the completer's
        rights on the prediction; who recorded it is stamped explicitly."""
        uid = self.env.uid
        for rec in self.sudo():
            rec.write(
                {
                    "outcome": outcome,
                    "outcome_note": note,
                    "outcome_recorded_by": uid,
                    "outcome_recorded_on": fields.Datetime.now(),
                    "outcome_action_id": action.id,
                }
            )

    def action_create_preventive_wo(self):
        """Wire predicted failures into M02 dispatch as preventive work."""
        for rec in self:
            if rec.prediction != "failure_predicted":
                raise UserError("Only failure predictions create preventive work orders")
            if rec.work_order_created:
                raise UserError("Work order already created for this prediction")
            rec._fix_assert_published_model("Raising a preventive work order")
            rec._guarded().write({"work_order_created": True})
            publish(
                self.env,
                "predictive_maintenance.wo_created",
                "fix.predictive.maintenance",
                rec.id,
                {"equipment": rec.equipment_id.name, "days": rec.estimated_days_to_failure},
            )
