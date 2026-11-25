# fix_stream_registry — M48: IoT telemetry, alerting, PdM (P11-M03).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_iot_ops import (
    IOT_CONSENT,
    IngestRefused,
    _is_location_metric,
    _require_role,
)

# A07 P1 (2026-11-04) BRU-IOT-10 / FR-IOT-040: where a prediction's model is
# checked against the M26 registry. "use" (default): the prediction is
# recorded, but nothing APPLIES it - no prescriptive action is approved and no
# preventive work order is raised - unless its model is a published M26
# predictive-maintenance model. "create": a prediction naming an unpublished
# model is refused outright. M26 (cd_ml_services) depends on this module, so
# the registry is read at run time, never imported.
MODEL_CHECK_PARAM = "cd_stream_registry.prediction_model_check"
# A07 (2026-11-07): a preventive work order is requested only on a score at least
# this confident (a 5% "failure predicted" raised one). A value nobody can read as
# a number between 0 and 1 falls back to the default: it never opens the gate.
PREVENTIVE_MIN_CONFIDENCE_PARAM = "cd_stream_registry.preventive_min_confidence"
PREVENTIVE_MIN_CONFIDENCE_DEFAULT = 0.5
# A07 ERP audit (2026-11-20) M48-20 / T-07: a gateway clock a little fast is
# normal. A reading up to this far ahead of the server clock is accepted.
CLOCK_SKEW_SECONDS = 120
# M48-01: what a device is bound to decides whose data it collects, so whether a
# consent is needed. Extended by the spine (M17 device, M46 vehicle, M05 endpoint).
_DEVICE_BINDING = frozenset({"partner_id", "site_id", "equipment_id"})


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
        return super()._fix_guarded_fields() | {
            "status",
            "last_telemetry",
            "consent_ever_recorded",
            "binding_log",
        }

    # ---- what the device is bound to (A07 ERP audit 2026-11-20, M48-01/05) ----
    def _fix_binding_fields(self) -> set:
        return set(_DEVICE_BINDING)

    def _fix_company_asset(self):
        """The company asset the device monitors (a facility sensor), or False."""
        self.ensure_one()
        return self.equipment_id or self.site_id

    def _fix_bound_asset(self):
        """Any asset the device is bound to (BRU-IOT-02)."""
        self.ensure_one()
        return self._fix_company_asset()

    def _fix_customer_binding(self):
        """Why the device collects a customer's data, or "" (the spine adds the
        M17 customer device and the M05 endpoint)."""
        self.ensure_one()
        if self.partner_id:
            return "the device belongs to customer %s" % self.partner_id.display_name
        return ""

    def _fix_binding_locked(self):
        """Why the device's binding no longer changes by a plain edit, or ""."""
        self.ensure_one()
        if self.consent_ever_recorded:
            return "a telemetry consent has been recorded for it"
        if (
            self.env["fix.iot.stream"]
            .sudo()
            .search_count([("device_id", "=", self.id), ("state", "!=", "draft")], limit=1)
        ):
            return "it has streams that have left draft"
        return ""

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(d._fix_binding_locked() for d in self):
            locked |= self._fix_binding_fields()
        return locked

    def write(self, vals):
        # M48-01: the administrator cleared the device's customer (or moved its
        # site) and the consent exemption came back, undoing a revocation. Once
        # a consent is on record or a stream has left draft, the binding changes
        # only through action_change_binding, the Consent Officer's.
        if self and not self._fix_guard_open():
            touched = self._fix_binding_fields() & set(vals)
            for rec in self:
                changed = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                why = changed and rec._fix_binding_locked()
                if why:
                    raise UserError(
                        "Device %s: its %s can no longer be edited because %s. The Consent "
                        "Officer changes it with Change Binding, giving the reason."
                        % (
                            rec.name,
                            ", ".join(sorted(self._fields[n].string for n in changed)),
                            why,
                        )
                    )
        return super().write(vals)

    def action_change_binding(self, field=None, value=None, reason=None):
        """M48-01: the Consent Officer re-binds a monitored device (its customer,
        site, equipment...). `value` is the record id, or blank to clear it. Live
        streams the consent gate no longer lets through are suspended at once."""
        _require_role(self.env, IOT_CONSENT, "Changing what a monitored device is bound to")
        name = (field or "").strip()
        allowed = self._fix_binding_fields()
        if name not in allowed:
            raise UserError("Name the binding to change: %s." % ", ".join(sorted(allowed)))
        why = (reason or "").strip()
        if not why:
            raise UserError("Give the reason for changing the device's binding.")
        comodel = self.env[self._fields[name].comodel_name].sudo()
        target = comodel.browse()
        if value not in (None, False, "", 0, "0"):
            try:
                target = comodel.browse(int(value)).exists()
            except (TypeError, ValueError) as exc:
                raise UserError("Give the id of the record to bind, or leave it blank.") from exc
            if not target:
                raise UserError("No such %s." % self._fields[name].string)
        for rec in self:
            before = rec[name].display_name or "-"
            line = "%s: %s changed from %s to %s by %s (%s)" % (
                fields.Datetime.now(),
                self._fields[name].string,
                before,
                target.display_name or "-",
                self.env.user.name,
                why,
            )
            rec.sudo()._guarded().write(
                {
                    name: target.id or False,
                    "binding_log": "\n".join(filter(None, (rec.binding_log, line))),
                }
            )
            rec.sudo().message_post(body=line)
            live = (
                self.env["fix.iot.stream"]
                .sudo()
                .search([("device_id", "=", rec.id), ("state", "in", ("active", "silent"))])
            )
            for stream in live:
                try:
                    stream._fix_check_consent()
                except IngestRefused:
                    stream._fix_suspend("device %s re-bound: %s" % (rec.name, why))
        return True

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
    # M48-01: set once a counting consent (a verified grant or a withdrawal) has
    # covered the device; never cleared. A device that once needed a consent
    # keeps needing one, whatever its binding later says.
    consent_ever_recorded = fields.Boolean(
        string="Consent On Record", readonly=True, copy=False, index=True
    )
    binding_log = fields.Text(string="Binding Changes", readonly=True, copy=False)
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
            came_back = health == "online" and rec.status != "online"
            last = max(rec.last_telemetry, at) if rec.last_telemetry else at
            rec._guarded().write({"status": health, "last_telemetry": last})
            if became_unhealthy:
                rec._fix_raise_health_alert(health)
            if came_back:
                # A07 ERP audit (2026-11-20) M48-18: the "became offline" alert
                # stayed open for ever after the device reported again.
                rec._fix_close_health_alerts("device reporting again at %s" % at)

    def _fix_close_health_alerts(self, note):
        """Resolve the device-level (not rule) alerts of these devices."""
        now = fields.Datetime.now()
        uid = self.env.uid
        alerts = (
            self.env["fix.iot.alert"]
            .sudo()
            .search(
                [
                    ("device_id", "in", self.ids),
                    ("rule_id", "=", False),
                    ("stream_id", "=", False),
                    ("state", "!=", "resolved"),
                ]
            )
        )
        for alert in alerts:
            alert._guarded().write(
                {
                    "state": "resolved",
                    "acked_on": alert.acked_on or now,
                    "acked_by": alert.acked_by.id or uid,
                    "resolved_on": now,
                    "resolved_by": uid,
                    "resolution_note": "Closed automatically: %s." % note,
                }
            )
        return alerts

    def _fix_mark_degraded(self):
        """M48-18: some, not all, of the device's live streams fell silent."""
        for rec in self.sudo().filtered(lambda d: d.status == "online"):
            rec._guarded().write({"status": "degraded"})
            rec._fix_raise_health_alert("degraded", "a stream fell silent")

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
    """M48: telemetry record (time-series; the volume model at 50k/min).

    A07 ERP audit (2026-11-20) M48-14: a reading is not a document. It carried
    mail.thread and mail.activity.mixin (followers, chatter and activities per
    reading); it is a plain guarded row now."""

    _name = "fix.iot.telemetry"
    _description = "IoT Telemetry"
    _inherit = ["fix.guarded.mixin"]
    _order = "timestamp desc"

    # M48-20 / FR-IOT-018: the duplicate check below searched, then inserted, so
    # two concurrent replays of the same reading both landed. The index makes it
    # atomic for every reading that carries its source's own time stamp.
    _source_reading_once = models.UniqueIndex(
        "(device_id, metric, timestamp) WHERE source_stamped AND device_id IS NOT NULL",
        "Duplicate reading refused: the device already has this signal at this time.",
    )

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
            "anonymised",
            "source_stamped",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "Telemetry is recorded only through the stream's ingest, which checks the "
                "telemetry consent and evaluates the alert rules."
            )
        for vals in vals_list:
            if vals.get("timestamp"):
                vals["source_stamped"] = True
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
        # the ingest-rate KPI (240 fake rows: 0.0 -> 10.0/h). A07 ERP audit
        # (2026-11-20) M48-20: a gateway clock one second fast got HTTP 409 and
        # could drop the reading; up to CLOCK_SKEW_SECONDS ahead is accepted
        # (the KPIs count only readings dated up to now).
        limit = fields.Datetime.now() + timedelta(seconds=CLOCK_SKEW_SECONDS)
        for rec in self:
            if rec.timestamp and rec.timestamp > limit:
                raise ValidationError("A telemetry reading cannot be dated in the future.")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    # A07 (2026-11-07): a reading loses its device only when it is anonymised
    # after a withdrawn consent (the CHECK below); every other reading has one.
    device_id = fields.Many2one("fix.iot.device", ondelete="cascade", index=True)
    timestamp = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    metric = fields.Char(required=True, help="e.g. temperature, vibration, gps_lat")
    value = fields.Float(required=True)
    unit = fields.Char(help="e.g. C, mm/s, deg")
    anonymised = fields.Boolean(
        string="Anonymised",
        default=False,
        readonly=True,
        help="The link to the device was removed and the time rounded to the hour, after "
        "the consent covering it was withdrawn.",
    )
    source_stamped = fields.Boolean(
        string="Source Time Stamp",
        readonly=True,
        help="The reading carries its source's own time (deduplicated on device, signal "
        "and time); otherwise the server stamped it on arrival.",
    )
    # M48-23 / BRU-IOT-18: a location series is a person's whereabouts. It is
    # read only by the IoT roles (record rule rule_fix_iot_telemetry_location).
    is_location = fields.Boolean(
        string="Location Signal", compute="_compute_is_location", store=True, index=True
    )

    @api.depends("metric")
    def _compute_is_location(self):
        for rec in self:
            rec.is_location = _is_location_metric(rec.metric)

    _device_or_anonymised = models.Constraint(
        "CHECK (device_id IS NOT NULL OR anonymised)",
        "A reading names its device unless it has been anonymised.",
    )

    def _fix_anonymise(self):
        """Treat these readings under a withdrawn consent: nothing left ties them
        to the data subject. A location series IS the person's whereabouts, so
        no rounding makes it anonymous: it is deleted. Returns (anonymised,
        deleted)."""
        location = self.filtered(lambda r: _is_location_metric(r.metric)).sudo()
        deleted = len(location)
        location.unlink()
        rest = self.exists().sudo()
        for reading in rest:
            reading._guarded().write(
                {
                    "device_id": False,
                    "operating_unit_id": False,
                    "anonymised": True,
                    "timestamp": reading.timestamp.replace(minute=0, second=0, microsecond=0),
                }
            )
        return len(rest), deleted


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
            "escalation_level",
            "escalated_on",
            "routed_to_module",
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
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        default="minor",
        required=True,
        tracking=True,
    )
    message = fields.Char(required=True)
    # A07 ERP audit (2026-11-20) M48-10 / AUT-IOT-10: an unacknowledged alert
    # waited for ever. The escalation job raises the level once the severity's
    # acknowledgement SLA (a setting) has passed, and tells the owning role.
    escalation_level = fields.Integer(string="Escalation Level", readonly=True, default=0)
    escalated_on = fields.Datetime(string="Last Escalated", readonly=True)
    # M48-15: the module that owns the asset the alert is about.
    routed_to_module = fields.Char(string="Routed To", readonly=True)
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

    # A11 audit M26-P02: prediction/confidence/days/model_name are the
    # MODEL'S OUTPUT, and an output is recorded, never rewritten — a plain
    # user could flip healthy/0.95 to failure_predicted/0.2 after the fact
    # and raise a work order from a decision no engine made. Recording a NEW
    # prediction is the intake act, the IoT Operator's since A07 (2026-11-07);
    # an existing row's output half is locked here and shown read-only on the
    # P03 form. A re-assessment records a NEW prediction row — the same
    # decision-log rule the M26 inference runs follow. A score belongs to the
    # equipment it was computed for, so re-pointing it is the same forgery.
    _OUTPUT_FIELDS = {
        "equipment_id",
        "prediction",
        "confidence",
        "estimated_days_to_failure",
        "model_name",
        "feature_window_from",
        "feature_window_to",
        "last_evaluated",
    }

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
            "preventive_action_id",
            "score_source",
            "horizon_flagged",
        }

    def _fix_form_locked_fields(self) -> set:
        # The output half is locked ON THE FORM for every existing record (P03
        # reads this). An empty recordset is a new form: A07 (2026-11-07) locking
        # it too dropped the score on save, so every new prediction was stored
        # as "healthy" with a blank model.
        locked = super()._fix_form_locked_fields()
        return locked | self._OUTPUT_FIELDS if self else locked

    @api.model_create_multi
    def create(self, vals_list):
        person = not self.env.su
        if person:
            _require_operator(self.env, "Recording a prediction")
        now = fields.Datetime.now()
        engine = not person or bool(self.env.context.get("fix_m26_inference"))
        for vals in vals_list:
            vals.setdefault("last_evaluated", now)
            # A07 ERP audit (2026-11-20) M48-02: a score typed by a person is kept
            # (it may be useful) but it is a MANUAL score: it never drives work.
            # Only the M26 inference path (superuser engine code) records an
            # engine score.
            vals["score_source"] = "engine" if engine else "manual"
        records = super().create(vals_list)
        if person:
            # A person names a model of the M26 catalogue: a blank model is not one.
            for rec in records:
                if not rec._fix_catalog_model():
                    rec._fix_assert_published_model("Recording this prediction")
        return records

    def write(self, vals):
        # P02: the lock itself. Only the engine (superuser code or a guard
        # token) rewrites an output; anyone else records a new prediction.
        if self and not self._fix_guard_open():
            touched = self._OUTPUT_FIELDS & set(vals)
            if touched:
                changed = {
                    name
                    for rec in self
                    for name in touched
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    self._fix_guard_refuse(changed)
        return super().write(vals)

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    # A07 ERP audit (2026-11-20) M48-05: a prediction names ONE asset. M45
    # equipment here; the spine adds the M46 vehicle and the M17 customer device.
    equipment_id = fields.Many2one("fix.equipment", string="Equipment", ondelete="cascade")
    asset_label = fields.Char(string="Asset", compute="_compute_asset_label")
    # M48-02: who produced the score. Only an engine score of a governed M26
    # model version drives work (BRU-IOT-10/11).
    score_source = fields.Selection(
        [("engine", "M26 Inference (engine)"), ("manual", "Recorded by Hand")],
        string="Score Source",
        readonly=True,
        default="manual",
        copy=False,
    )
    # M48-03: the preventive work order is now a prescriptive action approved by
    # the Operations Director, not the operator's own click.
    preventive_action_id = fields.Many2one(
        "fix.iot.action",
        string="Preventive Request (Action)",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    # M48-10 / AUT-IOT-16: the horizon passed with no outcome; flagged once.
    horizon_flagged = fields.Boolean(string="Horizon Passed (flagged)", readonly=True, copy=False)
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
    # A07 (2026-11-07): set when the request is made, before any order exists,
    # so it says "requested". The demand and the order are on the spine; dismissing
    # the demand clears this, and the request can be made again.
    work_order_created = fields.Boolean(
        string="Preventive Work Order Requested", default=False, readonly=True
    )
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
                if not rec._fix_catalog_model():
                    rec._fix_assert_published_model("Recording prediction %s" % rec.name)

    @api.constrains("equipment_id")
    def _check_asset(self):
        for rec in self:
            if not rec._fix_prediction_asset():
                raise ValidationError(
                    "Prediction %s names no asset: name the equipment, vehicle or customer "
                    "device it was computed for." % rec.name
                )

    def _fix_prediction_asset(self):
        """The asset this prediction is about (the spine adds vehicle and device)."""
        self.ensure_one()
        return self.equipment_id

    def _compute_asset_label(self):
        for rec in self:
            asset = rec._fix_prediction_asset()
            rec.asset_label = asset.display_name if asset else False

    def _fix_publication_problem(self):
        """Why this prediction may not drive work, or "" (BRU-IOT-10). The M26
        bridge adds the governance of the model version that produced it."""
        self.ensure_one()
        if not self._fix_catalog_model():
            codes = self._fix_published_codes()
            return (
                "it names model '%s', which is not a published M26 predictive-maintenance "
                "model. %s"
                % (
                    self.model_name or "(none)",
                    "Name one of: %s." % ", ".join(codes)
                    if codes
                    else "No such model is published in M26 yet.",
                )
            )
        if self.score_source != "engine":
            return (
                "it is a score recorded by hand: only a score the M26 inference path "
                "produced from a governed model version drives work"
            )
        return ""

    def _fix_published_model(self):
        """The M26 model whose governed engine produced this score, or None."""
        self.ensure_one()
        if self._fix_publication_problem():
            return None
        return self._fix_catalog_model()

    def _fix_catalog_model(self):
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

    def _fix_published_codes(self):
        """The codes a prediction may name: production M26 predictive-maintenance
        models (none when M26 is not installed)."""
        if "fix.ml.model" not in self.env:
            return []
        return (
            self.env["fix.ml.model"]
            .sudo()
            .search([("kind", "=", "predictive_maintenance"), ("status", "=", "production")])
            .mapped("code")
        )

    def _fix_assert_published_model(self, what):
        for rec in self:
            problem = rec._fix_publication_problem()
            if problem:
                raise UserError("%s refused: prediction %s %s." % (what, rec.name, problem))

    def _fix_record_outcome(self, outcome, note, action):
        """Record what an intervention found (called by fix.iot.action's
        action_done, which has already checked its own state). As superuser:
        the outcome follows from the completed action whatever the completer's
        rights on the prediction; who recorded it is stamped explicitly."""
        uid = self.env.uid
        for rec in self.sudo():
            # A07 (2026-11-07): a second action on the prediction overwrote the
            # finding the first one recorded.
            if rec.outcome != "pending":
                raise UserError(
                    "Prediction %s already has its outcome, recorded by action %s: a "
                    "re-assessment records a new prediction."
                    % (rec.name, rec.outcome_action_id.name or "-")
                )
            rec.write(
                {
                    "outcome": outcome,
                    "outcome_note": note,
                    "outcome_recorded_by": uid,
                    "outcome_recorded_on": fields.Datetime.now(),
                    "outcome_action_id": action.id,
                }
            )

    def _fix_preventive_min_confidence(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(PREVENTIVE_MIN_CONFIDENCE_PARAM)
        try:
            value = float(raw) if raw not in (None, False, "") else None
        except (TypeError, ValueError):
            value = None
        if value is None or not 0.0 <= value <= 1.0:
            return PREVENTIVE_MIN_CONFIDENCE_DEFAULT
        return value

    def action_create_preventive_wo(self, justification=None, scheduled_on=None):
        """Request preventive work on a predicted failure.

        A07 ERP audit (2026-11-20) M48-03: the operator's click raised the work
        order with no approval and no segregation of duties. It now proposes a
        prescriptive action and requests its approval (the Operations Director,
        DOFA Tier 2 while nobody holds that role; never the requester). Only the
        approval publishes predictive_maintenance.wo_created, and the approval pins
        the scheduled date (decision D17(c)). Whoever recorded the score does not
        request work on it."""
        _require_operator(self.env, "Requesting a preventive work order")
        why = (justification or "").strip()
        if not self.env.su and not why:
            raise UserError(
                "Say why a preventive work order is needed: the approver decides on your reason."
            )
        minimum = self._fix_preventive_min_confidence()
        Action = self.env["fix.iot.action"]
        for rec in self:
            if rec.prediction != "failure_predicted":
                raise UserError("Only failure predictions create preventive work orders")
            if rec.work_order_created:
                raise UserError("A preventive work order was already requested for this prediction")
            rec._fix_assert_published_model("Raising a preventive work order")
            if (rec.confidence or 0.0) < minimum:
                raise UserError(
                    "Prediction %s has confidence %s, below the %s a preventive work order "
                    "needs (setting %s)."
                    % (rec.name, rec.confidence or 0.0, minimum, PREVENTIVE_MIN_CONFIDENCE_PARAM)
                )
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "You recorded prediction %s: someone else requests the work it calls for."
                    % rec.name
                )
            days = rec.estimated_days_to_failure or 0
            vals = {
                "prediction_id": rec.id,
                "action_type": "inspect",
                "priority": "high" if days <= 7 else ("medium" if days <= 30 else "low"),
                "preventive_request": True,
                "notes": "Preventive work order requested on prediction %s" % rec.name,
            }
            if scheduled_on:
                vals["scheduled_on"] = scheduled_on
            # preventive_request is guarded: only this method marks an action so
            action = Action.browse(Action._guarded().create(vals).id)
            rec._guarded().write({"work_order_created": True, "preventive_action_id": action.id})
            action.action_request_approval(
                justification=why or "Preventive work order on prediction %s" % rec.name
            )
        return True

    def _fix_release_preventive_request(self, why):
        """The preventive request is over without work (cancelled, dismissed)."""
        for rec in self.sudo().filtered("work_order_created"):
            rec._guarded().write({"work_order_created": False, "preventive_action_id": False})
            rec.message_post(
                body="The preventive work order request was withdrawn (%s). It can be "
                "requested again." % why
            )
